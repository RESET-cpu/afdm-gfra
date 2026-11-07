from pathlib import Path
import difflib
import hashlib
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0,str(Path.home()/'.cache/codex-pymupdf'))
import pymupdf as fitz
from PIL import Image, ImageDraw

RUN=Path(__file__).resolve().parent
PAPER=RUN.parents[1]
ROOT=PAPER.parents[1]
read=lambda p:p.read_text(encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=json.loads(read(RUN/'BEFORE_HASHES.json'))
changed=[p for p,h in before.items() if sha(PAPER/p)!=h]
assert set(changed)=={'main.pdf','main_full.pdf','sections/06_simulation_results.tex',
                      'figures/channel_denoising.pdf','figures/cross_channel.pdf'},changed
old=read(RUN/'before/sections/06_simulation_results.tex')
new=read(PAPER/'sections/06_simulation_results.tex')
envs=lambda s,e:re.findall(r'\\begin\{'+e+r'\}.*?\\end\{'+e+r'\}',s,re.S)
assert envs(old,'equation')==envs(new,'equation')
assert envs(old,'table')==envs(new,'table')
assert set(re.findall(r'\\label\{([^}]+)\}',old))==set(re.findall(r'\\label\{([^}]+)\}',new))
order=['denoising','convergence','snr','pilots','users','activity','cross']
assert re.findall(r'\\label\{fig:cstmp-([^}]+)\}',new)==order
text_order=['snr','pilots','users','activity','cross']
assert [new.index('Figure~\\ref{fig:cstmp-'+x+'}') for x in text_order]==sorted(new.index('Figure~\\ref{fig:cstmp-'+x+'}') for x in text_order)
assert 'profiles A, B, C, and D (from left' in new
(RUN/'SOURCE_DIFF.txt').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),
    fromfile='before/06_simulation_results.tex',tofile='after/06_simulation_results.tex')),encoding='utf-8')
snr=ROOT/'result/snr_comparison/figures/full_grid_final_20261026/PLOT_DATA.json'
rows=json.loads(read(snr))['rows']
values={r['method']:r['nmse_db'] for r in rows if r['snr_db']==0}
gain=values['STMP']-values['C_STMP']
assert round(gain,1)==1.6
figures=json.loads(read(RUN/'RENDER_VALIDATION.json'))
assert sum(f['point_count'] for f in figures['figures'])==198
for f in figures['figures']:
    for p,h in f['sources'].items():assert sha(ROOT/p)==h
    assert sha(PAPER/'figures'/(f['name']+'.pdf'))==f['pdf_sha256']
    d=fitz.open(PAPER/'figures'/(f['name']+'.pdf'))
    assert len(d)==1 and not d[0].get_images()
    if f['name']=='cross_channel':
        positions=[d[0].search_for('NTN-TDL-'+c)[0].x0 for c in 'ABCD']
        assert positions==sorted(positions)
    else:
        for label in ['Denoiser (colored)','Denoiser (AWGN)','Genie MMSE','Off-grid SBL','GNN-ASPL','GAMP-SBL','SOMP','LS','Gaussian prior']:
            assert label in d[0].get_text(),label
pdfs={}
for name in ['main','main_full']:
    doc=fitz.open(PAPER/(name+'.pdf'))
    prev=fitz.open(RUN/'before'/(name+'.pdf'))
    changed_pages=[]
    for i,page in enumerate(doc):
        pix=page.get_pixmap(matrix=fitz.Matrix(1.5,1.5))
        differs=i>=len(prev) or pix.samples!=prev[i].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).samples
        if differs:
            changed_pages.append(i+1)
            pix.save(RUN/'previews'/f'{name}_{i+1}.png')
    aux=read(PAPER/(name+'.aux'))
    numbers={x:int(re.search(r'\\newlabel\{fig:cstmp-'+x+r'\}\{\{(\d+)\}',aux)[1]) for x in order}
    assert list(numbers.values())==list(range(4,11)),numbers
    refs=re.findall(r'\\bibcite\{([^}]+)\}',aux)
    assert len([x for x in refs if x!='IEEEcontrol'])==43
    assert not re.search(r'Overfull|undefined references|Citation .* undefined|Reference .* undefined',read(PAPER/(name+'.log')),re.I)
    fig10=[(i+1,r.y0) for i,p in enumerate(doc) for r in p.search_for('Fig. 10.')]
    concl=[(i+1,r.y0) for i,p in enumerate(doc) for r in p.search_for('VII. CONCLUSION')]
    assert fig10 and concl and min(fig10)<min(concl),(fig10,concl)
    pdfs[name]=dict(pages=len(doc),changed_pages=changed_pages,figure_numbers=numbers,
        figure_10_caption=fig10,conclusion=concl,sha256=sha(PAPER/(name+'.pdf')))
    thumbs=[]
    for n in changed_pages:
        im=Image.open(RUN/'previews'/f'{name}_{n}.png');im.thumbnail((300,400));thumbs.append((n,im.copy()))
    contact=Image.new('RGB',(1200,430*((len(thumbs)+3)//4)),'white');draw=ImageDraw.Draw(contact)
    for j,(n,im) in enumerate(thumbs):
        x,y=j%4*300,j//4*430;draw.text((x+8,y+3),f'{name} p.{n}',fill='black');contact.paste(im,(x,y+22))
    contact.save(RUN/'previews'/f'{name}_contact.png')
result=dict(status='PASS',changed_manuscript_assets=changed,protected_assets_unchanged=len(before)-len(changed),
    numbered_equations_unchanged=len(envs(old,'equation')),tables_unchanged=len(envs(old,'table')),
    original_labels_preserved=True,curve_points_preserved=198,
    new_snr_comparison=dict(snr_db=0,gain_db=gain,reported_gain_db=1.6,source=snr.relative_to(ROOT).as_posix(),source_sha256=sha(snr)),
    figures=figures,pdfs=pdfs,visual_review='See VISUAL_QA.md',inference_started=False,training_started=False)
(RUN/'VALIDATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:result[k] for k in ['status','changed_manuscript_assets','protected_assets_unchanged','curve_points_preserved','pdfs']},ensure_ascii=False))
