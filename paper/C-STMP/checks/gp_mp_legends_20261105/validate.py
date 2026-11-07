from pathlib import Path
import hashlib, json, re, sys
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
PAPER=ROOT/'paper/C-STMP'
sys.path.insert(0,str(ROOT/'src/evaluation/plots'))
from manuscript.vector import fitz
from PIL import Image, ImageDraw

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
before=json.loads((OUT/'BEFORE_HASHES.json').read_text(encoding='utf-8'))
config_rel='src/configs/plots/manuscript.json'
raw=(OUT/'before'/config_rel).read_bytes()
assert (ROOT/config_rel).read_bytes()==raw.replace(b'CGP-MP',b'GP-MP')
for rel in ['FINAL.json','MAINLINE.json','paper/C-STMP/figures/system_multiframe.pdf',
            'paper/C-STMP/figures/factor_graph.pdf','paper/C-STMP/figures/learned_receiver.pdf']:
    assert sha(ROOT/rel)==before[rel]
report=json.loads((OUT/'PLOT_VALIDATION.json').read_text(encoding='utf-8'))
assert report['status']=='PASS'
assert sum(x['point_count'] for x in report['figures'].values())==559
for rel,digest in report['sources'].items(): assert sha(ROOT/rel)==digest
preview=OUT/'rendered'; preview.mkdir(exist_ok=True)
images=[]
for name in report['figures']:
    with fitz.open(PAPER/'figures'/(name+'.pdf')) as doc:
        text=doc[0].get_text()
        assert 'CGP-MP' not in text and 'GP-MP' in text,name
        if name=='snr_comparison': assert 'GP-MP-EP' in text
        p=preview/(name+'.png'); doc[0].get_pixmap(dpi=170).save(p); images.append(p)
out=Image.new('RGB',(1100,4*510),'#e0e0e0'); draw=ImageDraw.Draw(out)
for i,p in enumerate(images):
    im=Image.open(p).convert('RGB'); im.thumbnail((538,470))
    x=(i%2)*550+6; y=(i//2)*510+25
    out.paste(im,(x,y)); draw.text((x,y-19),p.stem,fill='black')
out.save(preview/'figures_contact.png')
pdfs={}
for stem in ['main','main_full']:
    log=(PAPER/(stem+'.log')).read_text(encoding='utf-8')
    assert not any(s in log.lower() for s in ['undefined references','overfull \\hbox','overfull \\vbox'])
    with fitz.open(PAPER/(stem+'.pdf')) as doc:
        text='\n'.join(p.get_text() for p in doc)
        assert 'CGP-MP' not in text
        assert 'GP-MP-EP' in text
        pdfs[stem]={'pages':len(doc),'sha256':sha(PAPER/(stem+'.pdf'))}
        pages=range(6,len(doc)) if stem=='main' else range(12,len(doc))
        for i in pages: doc[i].get_pixmap(dpi=90).save(preview/f'{stem}-{i+1:02d}.png')
images=sorted(preview.glob('main-*.png'))+sorted(preview.glob('main_full-*.png'))
out=Image.new('RGB',(1360,((len(images)+3)//4)*460),'#e0e0e0'); draw=ImageDraw.Draw(out)
for i,p in enumerate(images):
    im=Image.open(p).convert('RGB'); im.thumbnail((328,430))
    x=(i%4)*340+6;y=(i//4)*460+22
    out.paste(im,(x,y));draw.text((x,y-18),p.stem,fill='black')
out.save(preview/'manuscript_contact.png')
result={'status':'PASS','configuration_change':'display labels only','points_preserved':559,
        'sources_unchanged':report['sources'],'compiled_pdfs':pdfs,
        'no_CGP_MP_in_pdfs':True,'method_figures_and_model_binding_unchanged':True}
(OUT/'VALIDATION.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='sources_unchanged'},indent=2))
