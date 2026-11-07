from pathlib import Path
import collections
import difflib
import hashlib
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path.home()/'.cache/codex-pymupdf'))
import pymupdf as fitz
from PIL import Image, ImageDraw

RUN = Path(__file__).resolve().parent
PAPER = RUN.parents[1]
ROOT = PAPER.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: p.read_text(encoding='utf-8')
save = lambda name, obj: (RUN/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
before = json.loads(read(RUN/'BEFORE_HASHES.json'))
changed = [p for p,h in before.items() if sha(PAPER/p) != h]
assert set(changed) == {'sections/06_simulation_results.tex','main.pdf','main_full.pdf'}, changed
old = read(RUN/'before/sections/06_simulation_results.tex')
new = read(PAPER/'sections/06_simulation_results.tex')
(RUN/'SOURCE_DIFF.txt').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='before/06_simulation_results.tex',tofile='after/06_simulation_results.tex')),encoding='utf-8')
def envs(s,e):
    return re.findall(r'\\begin\{'+re.escape(e)+r'\}.*?\\end\{'+re.escape(e)+r'\}',s,re.S)
assert envs(old,'equation') == envs(new,'equation')
assert all(x in envs(new,'table') for x in envs(old,'table'))
for e in ['figure','figure*']: assert envs(old,e) == envs(new,e)
assert set(re.findall(r'\\label\{([^}]+)\}',old)) <= set(re.findall(r'\\label\{([^}]+)\}',new))
assert new.count(r'\item \textbf{') == 8

paths = {
 'snr':'result/snr_comparison/figures/full_grid_final_20261026/PLOT_DATA.json',
 'denoising':'result/channel_denoising/figures/narrow_paper_20261026/PLOT_DATA.json',
 'pilot':'result/pilot_frames/figures/full_grid_final_20261026/PLOT_DATA.json',
 'users':'result/user_count/figures/redraw_beta01_500_20261028/PLOT_DATA.json',
 'activity':'result/activity_probability/figures/stmp_c_stmp_500_20261026/PLOT_DATA.json',
 'cross':'result/cross_channel/figures/full_500_paper_20261028/PLOT_DATA.json',
 'convergence':'result/snr_comparison/figures/convergence_current_paper_20261026/PLOT_DATA.json',
}
data = {k:json.loads(read(ROOT/p))['rows'] for k,p in paths.items()}
facts = {}
sparse = ['somp','gamp','gnn','offgrid_sbl']
lookup = {(r['method'],r['snr_db']):r for r in data['snr']}
snrs = sorted(set(r['snr_db'] for r in data['snr']))
facts['snr_gpmpc_lowest_nmse'] = all(lookup['C_STMP',s]['nmse_db'] < lookup[m,s]['nmse_db'] for s in snrs for m in sparse+['STMP'])
facts['snr_offgrid_lowest_of_sparse'] = all(lookup['offgrid_sbl',s]['nmse_db'] < lookup[m,s]['nmse_db'] for s in snrs for m in sparse if m!='offgrid_sbl')
gaps=[lookup['STMP',s]['nmse_db']-lookup['C_STMP',s]['nmse_db'] for s in snrs]
facts['snr_gpmp_gap_narrows'] = all(a>b for a,b in zip(gaps,gaps[1:]))
facts['snr_gaps_to_sparse_grow'] = all(lookup[m,b]['nmse_db']-lookup[n,b]['nmse_db'] > lookup[m,a]['nmse_db']-lookup[n,a]['nmse_db'] for a,b in zip(snrs,snrs[1:]) for m in sparse for n in ['C_STMP','STMP'])
facts['snr_aer_below_gpmp'] = all(lookup['C_STMP',s]['aer']<lookup['STMP',s]['aer'] for s in snrs)
facts['snr_aer_below_sparse_from_0db'] = all(lookup['C_STMP',s]['aer']<lookup[m,s]['aer'] for s in snrs if s>=0 for m in sparse)
lookup = {(r['method'],r['snr_db']):r for r in data['denoising']}
levels=sorted(set(r['snr_db'] for r in data['denoising']))
learned=['proposed','pretrained_colored_first']
facts['denoisers_below_ls_and_gaussian'] = all(lookup[m,s]['nmse_db']<lookup[n,s]['nmse_db'] for s in levels for m in learned for n in ['noisy','gaussian'])
facts['colored_denoiser_better_at_low_snr'] = all(lookup['pretrained_colored_first',s]['nmse_db']<lookup['proposed',s]['nmse_db'] for s in [-20.,-10.])
facts['white_denoiser_better_at_high_snr'] = all(lookup['proposed',s]['nmse_db']<lookup['pretrained_colored_first',s]['nmse_db'] for s in [10.,20.,30.])
facts['denoisers_above_genie'] = all(lookup[m,s]['nmse_db']>lookup['genie_bound',s]['nmse_db'] for s in levels for m in learned)
facts['denoiser_nmse_decreases'] = all(lookup[m,b]['nmse_db']<lookup[m,a]['nmse_db'] for a,b in zip(levels,levels[1:]) for m in learned)
for name,key in [('users','users'),('activity','activity_probability')]:
    lookup={(r['method'],r[key]):r for r in data[name]}
    levels=sorted(set(r[key] for r in data[name]))
    methods=sorted(set(r['method'] for r in data[name]))
    facts[name+'_gpmpc_lowest'] = all(lookup['C_STMP',s]['nmse_db']<lookup[m,s]['nmse_db'] for s in levels for m in methods if m!='C_STMP')
    facts[name+'_nmse_worsens'] = all(lookup[m,b]['nmse_db']>lookup[m,a]['nmse_db'] for a,b in zip(levels,levels[1:]) for m in methods)
    gaps=[lookup['STMP',s]['nmse_db']-lookup['C_STMP',s]['nmse_db'] for s in levels]
    facts[name+'_gap_to_gpmp_grows'] = all(a<b for a,b in zip(gaps,gaps[1:]))
first={m:min(r['frames'] for r in data['pilot'] if r['method']==m and r['nmse_db']<=-14) for m in ['C_STMP','STMP']}
facts['pilot_target_24_vs_32'] = first=={'C_STMP':24,'STMP':32}
last={m:max((r for r in data['convergence'] if r['method']==m),key=lambda r:r['parameters']['iteration']) for m in ['C_STMP','STMP']}
facts['convergence_stop_60_vs_85'] = [last[m]['parameters']['iteration'] for m in ['C_STMP','STMP']]==[60,85]
facts['convergence_gpmpc_lower_final_nmse'] = last['C_STMP']['nmse_db']<last['STMP']['nmse_db']
lookup={(r['method'],r['channel_model'],r['snr_db']):r for r in data['cross']}
conditions=sorted(set((r['channel_model'],r['snr_db']) for r in data['cross']))
facts['cross_below_sparse_all_profiles'] = all(lookup['C_STMP',c,s]['nmse_db']<lookup[m,c,s]['nmse_db'] for c,s in conditions for m in sparse)
facts['cross_gpmp_difference_smaller_than_sparse_gap'] = all(abs(lookup['C_STMP',c,s]['nmse_db']-lookup['STMP',c,s]['nmse_db']) < lookup[m,c,s]['nmse_db']-lookup['C_STMP',c,s]['nmse_db'] for c,s in conditions for m in sparse)
assert all(facts.values()), {k:v for k,v in facts.items() if not v}
save('RESULT_EVIDENCE.json',{'facts':facts,'sources':{k:{'path':p,'sha256':sha(ROOT/p)} for k,p in paths.items()},'scope':'Read-only verification of saved plot data; no experiments run. The user requested removal of the proposed SNR missed-detection/false-alarm breakdown; that breakdown is absent from the revised SNR paragraph.'})

previews=RUN/'previews';previews.mkdir(exist_ok=True)
pdfinfo={}
for name in ['main','main_full']:
    d=fitz.open(PAPER/f'{name}.pdf');previous=fitz.open(RUN/f'before/{name}.pdf')
    changed_pages=[]
    for i,p in enumerate(d):
        pix=p.get_pixmap(matrix=fitz.Matrix(1.5,1.5))
        differs=i>=len(previous) or pix.samples != previous[i].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).samples
        if differs: changed_pages.append(i+1)
        if i>=7 or differs:pix.save(previews/f'{name}_{i+1}.png')
    fig10=[(i+1,r.y0) for i,p in enumerate(d) for r in p.search_for('Fig. 10.')]
    conclusion=[(i+1,r.y0) for i,p in enumerate(d) for r in p.search_for('VII. CONCLUSION')]
    assert fig10 and conclusion and min(fig10)<min(conclusion),(fig10,conclusion)
    log=read(PAPER/f'{name}.log')
    assert not re.search(r'Overfull|undefined references|Citation .* undefined|Reference .* undefined',log,re.I)
    aux=read(PAPER/f'{name}.aux')
    entries=re.findall(r'\\bibcite\{([^}]+)\}',aux)
    assert len([x for x in entries if x!='IEEEcontrol'])==43
    pdfinfo[name]={'pages':len(d),'changed_pages':changed_pages,'figure_10_caption':fig10,'conclusion':conclusion,'sha256':sha(PAPER/f'{name}.pdf'),'references':43}
    thumbs=[]
    for i in range(8,len(d)+1):
        im=Image.open(previews/f'{name}_{i}.png');im.thumbnail((300,400));thumbs.append((i,im.copy()))
    sheet=Image.new('RGB',(1200,430*((len(thumbs)+3)//4)),'white');draw=ImageDraw.Draw(sheet)
    for j,(i,im) in enumerate(thumbs):
        x=j%4*300;y=j//4*430;draw.text((x+8,y+3),f'{name} p.{i}',fill='black');sheet.paste(im,(x,y+22))
    sheet.save(previews/f'{name}_contact.png')
save('VALIDATION.json',{'status':'PASS','changed_manuscript_files':changed,'protected_files_unchanged':len(before)-len(changed),'displayed_equations_unchanged':len(envs(old,'equation')),'existing_tables_unchanged':len(envs(old,'table')),'new_network_table':1,'figure_environments_unchanged':7,'bold_list_items':8,'numeric_claim_checks':len(facts),'pdfs':pdfinfo,'visual_review':'See VISUAL_QA.md for inspected final renders; automated checks do not replace visual inspection.'})
print(json.dumps({'status':'PASS','protected_files_unchanged':len(before)-len(changed),'numeric_claim_checks':len(facts),'pdfs':pdfinfo},ensure_ascii=False))
