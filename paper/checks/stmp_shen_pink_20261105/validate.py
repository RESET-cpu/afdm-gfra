from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
PAPER=ROOT/'paper/C-STMP'
sys.path.insert(0,str(ROOT/'src/evaluation/plots'))
from manuscript.vector import fitz
from PIL import Image,ImageDraw
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
before=json.loads((OUT/'BEFORE_HASHES.json').read_text(encoding='utf-8'))
cfg='src/configs/plots/manuscript.json'
assert (ROOT/cfg).read_bytes()==(OUT/'before'/cfg).read_bytes().replace(b'#ff6699',b'#ff00ff')
for rel,digest in before.items():
    if rel.endswith(('.tex','.bib')) or rel in ['FINAL.json','MAINLINE.json'] or any(rel.endswith(n+'.pdf') for n in ['system_multiframe','factor_graph','learned_receiver']):
        assert sha(ROOT/rel)==digest,rel
report=json.loads((OUT/'PLOT_VALIDATION.json').read_text(encoding='utf-8'))
old=json.loads((PAPER/'checks/gp_mp_legends_20261105/PLOT_VALIDATION.json').read_text(encoding='utf-8'))
assert report['status']=='PASS' and report['sources']==old['sources']
render=OUT/'rendered';render.mkdir(exist_ok=True)
colors={}
for name,fig in report['figures'].items():
    assert fig['curves']==old['figures'][name]['curves'],name
    with fitz.open(PAPER/'figures'/(name+'.pdf')) as doc:
        colors[name]=sum(d.get('color')==(1.,0.,1.) for d in doc[0].get_drawings())
        assert colors[name]>0
        assert not any(d.get('color') and all(abs(a-b)<1e-5 for a,b in zip(d['color'],[1,.4,.6])) for d in doc[0].get_drawings())
        doc[0].get_pixmap(dpi=170).save(render/(name+'.png'))
pdfs={}
for stem in ['main','main_full']:
    log=(PAPER/(stem+'.log')).read_text(encoding='utf-8').lower()
    assert not any(s in log for s in ['undefined references','overfull \\hbox','overfull \\vbox'])
    changed=[]
    with fitz.open(PAPER/(stem+'.pdf')) as doc,fitz.open(OUT/'before/paper/C-STMP'/(stem+'.pdf')) as previous:
        assert len(doc)==len(previous)
        for i,(a,b) in enumerate(zip(doc,previous)):
            assert a.get_text()==b.get_text(),(stem,i)
            if a.get_pixmap(dpi=100).samples!=b.get_pixmap(dpi=100).samples:
                changed.append(i+1);a.get_pixmap(dpi=110).save(render/f'{stem}-{i+1}.png')
        assert changed==[10,11,12],changed
        pdfs[stem]={'pages':len(doc),'text_unchanged':True,'changed_rendered_pages':changed,'sha256':sha(PAPER/(stem+'.pdf'))}
files=[render/(n+'.png') for n in report['figures']]
contact=Image.new('RGB',(1100,2040),'#dedede');draw=ImageDraw.Draw(contact)
for i,p in enumerate(files):
    im=Image.open(p).convert('RGB');im.thumbnail((538,470))
    x=(i%2)*550+6;y=(i//2)*510+25
    contact.paste(im,(x,y));draw.text((x,y-19),p.stem,fill='black')
contact.save(render/'figures_contact.png')
contact=Image.new('RGB',(1530,690),'#dedede')
for i in range(3):
    im=Image.open(render/f'main-{10+i}.png').convert('RGB');im.thumbnail((500,670));contact.paste(im,(i*510+5,10))
contact.save(render/'pages_contact.png')
result={'status':'PASS','color':'#ff00ff','vector_strokes':colors,'configuration_changes':9,
        'unchanged_curve_points':sum(f['point_count'] for f in report['figures'].values()),
        'tex_bibliography_method_figures_and_model_binding_unchanged':True,'compiled_pdfs':pdfs}
(OUT/'VALIDATION.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
