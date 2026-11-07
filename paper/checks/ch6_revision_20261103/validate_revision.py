"""Read-only manuscript/data validation; never runs an experiment or training."""
from pathlib import Path
import collections
import csv
import difflib
import hashlib
import json
import math
import re
import sys

RUN = Path(__file__).resolve().parent
PAPER = RUN.parents[1]
ROOT = PAPER.parents[1]
sys.path.append(str(Path.home() / '.cache/codex-pymupdf'))
import pymupdf as fitz

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

sources = {}
def read(relative):
    path = ROOT / relative
    sources[relative] = digest(path)
    return json.loads(path.read_text(encoding='utf-8-sig'))

paths = {
    'denoising': 'result/channel_denoising/figures/narrow_paper_20261026/PLOT_DATA.json',
    'convergence': 'result/snr_comparison/figures/convergence_current_paper_20261026/PLOT_DATA.json',
    'snr': 'result/snr_comparison/figures/phase_selected_main_500_20261102/PLOT_DATA.json',
    'users': 'result/user_count/figures/redraw_beta01_500_20261028/PLOT_DATA.json',
    'activity': 'result/activity_probability/figures/stmp_c_stmp_500_20261026/PLOT_DATA.json',
    'pilots': 'result/pilot_frames/figures/full_grid_final_20261026/PLOT_DATA.json',
    'cross': 'result/cross_channel/figures/full_500_paper_20261028/PLOT_DATA.json',
}
data = {key: read(path) for key, path in paths.items()}
evidence = read('result/snr_comparison/data/c_stmp_ablation_1000_20261028/phase_only_20261029/GAUSSIAN_RETAINED_SUMMARY.json')
phase_completion = read('result/snr_comparison/data/c_stmp_phase_selected_500_20261030/COMPLETION.json')
phase_validation = read('result/snr_comparison/figures/phase_selected_main_500_20261102/VALIDATION.json')
assert phase_completion['status'] == 'PASS'
assert phase_validation['status'] == 'PASS_DATA_AND_RENDER'
assert phase_completion['iteration_caps_by_variant']['selected_phase'] == 1

tex = (PAPER / 'sections/06_simulation_results.tex').read_text(encoding='utf-8')
checks = []
def row(group, method, **parameters):
    matches = [r for r in data[group]['rows'] if r['method'] == method
               and all(r.get(k, r.get('parameters', {}).get(k)) == v for k, v in parameters.items())]
    assert len(matches) == 1, (group, method, parameters, len(matches))
    return matches[0]

def number(label, value, printed, places=2, token=None):
    assert f'{value:.{places}f}' == printed, (label, value, printed)
    assert (token or printed) in tex, (label, token or printed)
    checks.append(dict(claim=label, value=value, displayed=printed))

def nm(group, method, **parameters):
    return row(group, method, **parameters)['nmse_db']

def gain(group, reference, **parameters):
    return nm(group, reference, **parameters) - nm(group, 'C_STMP', **parameters)

# Verify values in the manuscript against saved figure coordinates.
number('denoising colored at 0', nm('denoising','pretrained_colored_first',snr_db=0), '-17.98')
number('denoising Gaussian at 0', nm('denoising','gaussian',snr_db=0), '-2.98')
for snr, printed in [(-20,'1.74'),(-10,'2.11'),(0,'0.06')]:
    number(f'colored training gain at {snr}', nm('denoising','proposed',snr_db=snr)
           - nm('denoising','pretrained_colored_first',snr_db=snr), printed)
high_gains=[nm('denoising','pretrained_colored_first',snr_db=s)
            -nm('denoising','proposed',snr_db=s) for s in (10,20,30)]
number('white training high-SNR minimum gain',min(high_gains),'1.00')
number('white training high-SNR maximum gain',max(high_gains),'1.37')
assert all(-11.2 < nm('denoising',m,snr_db=30) < -10.7 for m in ('somp','gnn','gamp','offgrid_sbl'))
number('learned evidence AER percent',100*evidence['paired_known']['aer'],'0.134',3)
number('Gaussian evidence AER percent',100*evidence['paired']['gaussian_evidence']['aer'],'36.95')
assert evidence['paired_physical_scenes']==354 and evidence['paired_conditions']==2124
ablation=tex.split('\\subsection{Effect of Density Ratio Estimation}')[1].split('\\subsection{JADCE Performance}')[0]
assert not re.search(r'NMSE|false alarm|missed detection|nonconverged|724',ablation,re.I)
assert ablation.count('\\begin{table}')==1 and '\\begin{figure}' not in ablation
for method, iteration, value in [('C_STMP',2,'14.60'),('STMP',2,'25.51'),
    ('C_STMP',30,'-13.78'),('STMP',30,'-9.08'),('C_STMP',60,'-13.85'),('STMP',85,'-11.79')]:
    number(f'convergence {method} iteration {iteration}',nm('convergence',method,iteration=iteration),value)
assert len(data['snr']['rows'])==42
assert all(r['scenes']==500 for r in data['snr']['rows'])
for r in data['snr']['rows']:
    assert math.isclose(r['nmse_db'],10*math.log10(r['full_error']/r['signal_energy']),abs_tol=1e-10)
    assert math.isclose(r['aer'],(r['misses']+r['false_alarms'])/(r['active']+r['inactive']),abs_tol=1e-12)
for method,value in [('C_STMP','-12.98'),('STMP','-11.42'),('offgrid_sbl','-8.51'),('C_STMP_phase_selected','-12.73')]:
    number(f'SNR 0 {method}',nm('snr',method,snr_db=0),value)
for method,snr,value in [('STMP',-4,'1.86'),('STMP',6,'0.39'),('offgrid_sbl',-4,'4.09'),('offgrid_sbl',6,'5.98')]:
    number(f'SNR gain over {method} at {snr}',gain('snr',method,snr_db=snr),value)
a0=row('snr','C_STMP',snr_db=0)['aer']; b0=row('snr','STMP',snr_db=0)['aer']
number('AER relative reduction at 0',100*(1-a0/b0),'43',0,token='43\\%')
for method,snr,value,token in [('C_STMP',0,.00105,'1.05\\times10^{-3}'),('STMP',0,.00185,'1.85\\times10^{-3}'),
    ('C_STMP',-4,.00415,'4.15\\times10^{-3}'),('offgrid_sbl',-4,.0036,'3.60\\times10^{-3}'),
    ('C_STMP_phase_selected',0,.00125,'1.25\\times10^{-3}'),('C_STMP',6,.00015,'1.5\\times10^{-4}'),
    ('C_STMP_phase_selected',6,.00045,'4.5\\times10^{-4}')]:
    assert math.isclose(row('snr',method,snr_db=snr)['aer'],value,abs_tol=1e-12) and token in tex
    checks.append(dict(claim=f'AER {method} at {snr}',value=value,displayed=token))
losses=[nm('snr','C_STMP_phase_selected',snr_db=s)-nm('snr','C_STMP',snr_db=s) for s in (-4,-2,0,2,4,6)]
number('minimum phase NMSE loss',min(losses),'0.26');number('maximum phase NMSE loss',max(losses),'0.31')
assert all(nm('snr','C_STMP_phase_selected',snr_db=s)<nm('snr','STMP',snr_db=s) for s in (-4,-2,0,2,4,6))
for method,k,value in [('C_STMP',20,'-14.73'),('C_STMP',100,'-8.84'),('STMP',20,'-13.58'),('STMP',100,'-5.61')]:
    number(f'users {k} {method}',nm('users',method,users=k),value)
for method,k,value in [('STMP',20,'1.14'),('STMP',100,'3.23'),('offgrid_sbl',20,'5.05'),('offgrid_sbl',100,'2.53')]:
    number(f'users gain over {method} at {k}',gain('users',method,users=k),value)
for method,limit in [('C_STMP',80),('STMP',40)]:
    assert max(r['users'] for r in data['users']['rows'] if r['method']==method and r['nmse_db']<=-10)==limit
for p,value in [(.05,'-14.78'),(.25,'-9.26')]:
    number(f'activity {p}',nm('activity','C_STMP',activity_probability=p),value)
for method,p,value in [('STMP',.05,'1.07'),('STMP',.25,'2.25'),('offgrid_sbl',.25,'2.15')]:
    number(f'activity gain {method} {p}',gain('activity',method,activity_probability=p),value)
for q,value in [(16,'1.57'),(48,'0.51')]:
    number(f'pilot gain at {q}',gain('pilots','STMP',frames=q),value)
for method,q in [('C_STMP',24),('STMP',32)]:
    assert min(r['frames'] for r in data['pilots']['rows'] if r['method']==method and r['nmse_db']<=-14)==q
    assert row('pilots',method,frames=48)['aer']==.0001
number('Q8 STMP NMSE',nm('pilots','STMP',frames=8),'34.70')
number('Q8 proposed NMSE',nm('pilots','C_STMP',frames=8),'-8.87')
assert row('pilots','STMP',frames=8)['aer']==.8101 and '0.8101' in tex
assert row('pilots','C_STMP',frames=8)['aer']==.0077 and '0.0077' in tex
cross_gains=[gain('cross','STMP',channel_model=c,snr_db=0) for c in 'DABC']
number('cross minimum gain at 0',min(cross_gains),'1.02');number('cross maximum gain at 0',max(cross_gains),'1.60')
for c,value in [('A','0.39'),('B','0.58')]:
    number(f'STMP advantage on {c} at 6',-gain('cross','STMP',channel_model=c,snr_db=6),value)
assert abs(gain('cross','STMP',channel_model='B',snr_db=4))<.01
for r in data['cross']['rows']:
    if r['method'] in ('somp','gnn','gamp','offgrid_sbl'):
        assert r['nmse_db']>nm('cross','C_STMP',channel_model=r['channel_model'],snr_db=r['snr_db'])

# Actual 500-scene stopping statistics, without another inference pass.
csv_path=ROOT/'result/snr_comparison/data/c_stmp_variance_em_1000_snr_m4_p6_20261025/per_scene.csv'
sources[str(csv_path.relative_to(ROOT))]=digest(csv_path)
with csv_path.open(newline='') as f:
    records=[r for r in csv.DictReader(f) if int(r['scene'])<500]
assert collections.Counter(r['method'] for r in records)=={'C_STMP':3000,'STMP':3000}
assert all(r['stopping_reason']=='CONVERGED' for r in records)

before=json.loads((RUN/'BEFORE_HASHES.json').read_text())
allowed={'sections/05_overall_algorithm.tex','sections/06_simulation_results.tex',
         'sections/appendix_parameter_estimation.tex','sections/appendix_evaluation_protocol.tex',
         'figures/snr_comparison.pdf','docs/TERMINOLOGY.md','README.md','figures/README.md','main.pdf'}
protected=[];concurrent=[]
for relative,old_hash in before.items():
    normalized=relative.replace('\\','/')
    if normalized not in allowed:
        if normalized in ('sections/02_system_model.tex','sections/03_bayesian_receiver_design.tex'):
            old=(RUN/'before'/relative).read_text(encoding='utf-8')
            new=(PAPER/relative).read_text(encoding='utf-8')
            expected=old.replace('\\begin{figure*}[!t]','\\begin{figure}[!t]').replace('\\end{figure*}','\\end{figure}')
            expected=expected.replace('width=0.78\\textwidth','width=\\linewidth')
            assert new==expected,('unexpected concurrent source edit',relative)
            concurrent.append({'file':normalized,'change':'Externally updated method-figure placement; preserved.',
                'before_sha256':old_hash,'current_sha256':digest(PAPER/relative)})
        else:
            assert digest(PAPER/relative)==old_hash,relative
            protected.append(normalized)
new_figure=ROOT/'result/snr_comparison/figures/phase_selected_main_500_20261102/snr_comparison.pdf'
assert digest(PAPER/'figures/snr_comparison.pdf')==digest(new_figure)
sources[str(new_figure.relative_to(ROOT))]=digest(new_figure)
equations=[];changes=[]
math_pattern=r'\\begin\{(equation\*?|align\*?|gather\*?)\}[\s\S]*?\\end\{\1\}'
for relative in sorted(allowed-{'main.pdf','figures/snr_comparison.pdf'}):
    old=(RUN/'before'/relative).read_text(encoding='utf-8');new=(PAPER/relative).read_text(encoding='utf-8')
    changes.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='before/'+relative,tofile=relative))
    if relative.endswith('.tex'):
        a=[m.group() for m in re.finditer(math_pattern,old)];b=[m.group() for m in re.finditer(math_pattern,new)]
        assert a==b,relative
        equations.append(dict(file=relative,count=len(a),unchanged=True))
old5=(RUN/'before/sections/05_overall_algorithm.tex').read_text()
new5=(PAPER/'sections/05_overall_algorithm.tex').read_text()
algorithm=r'\\begin\{figure\}\[!t\][\s\S]*?\\end\{figure\}'
assert re.search(algorithm,old5).group()==re.search(algorithm,new5).group()
assert re.findall(r'\\subsection\{([^}]+)',tex)==['Simulation Settings','Channel Denoising Performance',
    'Effect of Density Ratio Estimation','JADCE Performance','Comparison Across Channel Profiles']
assert tex.count('\\includegraphics')==7
log=(PAPER/'main.log').read_text(encoding='utf-8')
assert not re.search(r'undefined references|Citation .+ undefined|Reference .+ undefined|multiply defined|Overfull',log,re.I)
doc=fitz.open(PAPER/'main.pdf');aux=(PAPER/'main.aux').read_text()
labels={}
for label in ['sec:simulations','tab:activity-evidence','fig:cstmp-denoising','fig:cstmp-convergence','fig:cstmp-snr',
    'fig:cstmp-users','fig:cstmp-activity','fig:cstmp-pilots','fig:cstmp-cross']:
    m=re.search(r'\\newlabel\{'+re.escape(label)+r'\}\{\{([^}]+)\}\{([^}]+)\}',aux)
    assert m,label
    labels[label]={'number':m[1],'page':int(m[2])}
for page in doc:
    assert page.rect.width==612 and page.rect.height==792
    assert len(page.get_text().strip())>100
(RUN/'CHANGES.diff').write_text(''.join(changes),encoding='utf-8')
result={'status':'PASS','numeric_checks':checks,'source_hashes':sources,'protected_files_unchanged':protected,
        'concurrent_method_layout_changes_preserved':concurrent,
        'equations':equations,'algorithm_1_unchanged':True,'only_snr_figure_replaced':True,
        'activity_ablation_reports_only_aer':True,'all_snr_curves_500_scenes':True,
        'known_phase_outputs_converged':{'C_STMP':3000,'STMP':3000},'undefined_references':False,'overfull_boxes':False,
        'labels':labels,'pages':len(doc),'pdf_sha256':digest(PAPER/'main.pdf'),
        'new_inferences':0,'training_runs':0,'visual_inspection':'See REVISION_NOTES.md; not certified by this script.'}
(RUN/'VALIDATION.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:result[k] for k in ('status','pages','labels','new_inferences','training_runs')},indent=2))
print('Numerical statements checked:',len(checks))
