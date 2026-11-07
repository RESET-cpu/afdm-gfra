"""Check plot values, protected assets, and the two compiled manuscripts."""
from pathlib import Path
import hashlib
import json
import re
import sys
from PIL import Image, ImageOps, ImageDraw

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src/evaluation/plots'))
from manuscript.vector import fitz

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

before=read(OUT/'BEFORE_HASHES.json')
config=read(ROOT/'src/configs/plots/manuscript.json')
old_config=read(OUT/'before/src/configs/plots/manuscript.json')
cfg=config['figures']['snr_comparison']
for name in old_config['figures']:
    if name!='snr_comparison': assert old_config['figures'][name]==config['figures'][name]
report=read(OUT/'PLOT_VALIDATION.json')
assert report['status']=='PASS'
plot=report['figures']['snr_comparison']
assert plot['point_count']==108 and plot['pdf_images']==0
old=read(ROOT/old_config['figures']['snr_comparison']['source'])
data=read(ROOT/cfg['source'])
assert data['rows'][:len(old['rows'])]==old['rows']
for curve in plot['curves']:
    rows=sorted([r for r in data['rows'] if r['method']==curve['method']],key=lambda r:r['snr_db'])
    assert curve['x']==[r['snr_db'] for r in rows]
    assert curve['y']==[r[curve['metric']] for r in rows]
    if curve['metric']=='aer':
        lo,hi=cfg['panel_config']['axes']['aer']['limits']
        assert all(lo<=v<=hi for v in curve['y'])

protected=[p for p in before if p in ('FINAL.json','MAINLINE.json') or
           (p.startswith('paper/C-STMP/figures/') and not Path(p).name.startswith('snr_comparison.'))]
for p in protected: assert sha(ROOT/p)==before[p],p
for suffix in ('pdf','png'):
    assert sha(ROOT/f'paper/C-STMP/figures/snr_comparison.{suffix}')==sha(OUT/f'rendered/snr_comparison.{suffix}')
pdfs={}; previews=[]
for name in ('main','main_full'):
    path=ROOT/f'paper/C-STMP/{name}.pdf'
    log=(ROOT/f'paper/C-STMP/{name}.log').read_text(encoding='utf-8',errors='replace')
    assert not re.search(r'Overfull|undefined references|undefined citations|Missing character|^!',log,re.I|re.M)
    with fitz.open(path) as doc,fitz.open(OUT/f'before/paper/C-STMP/{name}.pdf') as prior:
        texts=[p.get_text() for p in doc]
        figure_pages=[i+1 for i,t in enumerate(texts) if 'Off-grid SBL (25)' in t]
        assert len(figure_pages)==1
        assert all(label in texts[figure_pages[0]-1] for label in cfg['labels'].values())
        changes=[]
        for i,p in enumerate(doc):
            if i>=len(prior) or p.get_pixmap(dpi=72).samples!=prior[i].get_pixmap(dpi=72).samples:
                changes.append(i+1)
        pdfs[name]=dict(pages=len(doc),previous_pages=len(prior),figure_page=figure_pages[0],
            changed_pages=changes,sha256=sha(path),compile_errors=False,overfull_boxes=False,
            references=len(re.findall(r'\\bibitem', (ROOT/f'paper/C-STMP/{name}.bbl').read_text())))
        # Inspect all changed pages as thumbnails and the figure page at readable resolution.
        for page in changes:
            pix=doc[page-1].get_pixmap(dpi=60,alpha=False)
            im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
            im=ImageOps.expand(im,border=(2,22,2,2),fill='white')
            ImageDraw.Draw(im).text((8,4),f'{name} p.{page}',fill='black')
            previews.append(im)
        doc[figure_pages[0]-1].get_pixmap(dpi=150,alpha=False).save(OUT/f'{name}_snr_page.png')
cols=4; width=max(p.width for p in previews); height=max(p.height for p in previews)
sheet=Image.new('RGB',(cols*width,((len(previews)+cols-1)//cols)*height),'#dddddd')
for i,p in enumerate(previews): sheet.paste(p,((i%cols)*width,(i//cols)*height))
sheet.save(OUT/'changed_pages.png')
result=dict(status='PASS',original_curve_points_unchanged=84,new_curve_points=24,total_points=108,
    original_rows_preserved=True,all_plotted_values_verified=True,no_curves_outside_aer_axis=True,
    figure_vector_only=True,legend_font_pt=8,other_figure_configs_unchanged=True,
    protected_files_verified=len(protected),pdfs=pdfs,visual_review='PENDING',inference_started=False)
(OUT/'VALIDATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
