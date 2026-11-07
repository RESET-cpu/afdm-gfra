"""Verify the authorized relocation of experimental process notes to Appendix C.
No inference, training, compilation, or full numerical-claim reanalysis is performed.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[3]
PAPER=ROOT/'paper/C-STMP'
checks=[]
def read(p): return p.read_text(encoding='utf-8')
def load(p): return json.loads(read(p))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def compact(s): return re.sub(r'\s+', ' ', s).strip()
def check(name, ok, **evidence): checks.append(dict(name=name, passed=bool(ok), **evidence))
baseline={v['path']:v for v in load(RUN/'baseline.json')}
allowed={'sections/06_simulation_results.tex','sections/appendix_evaluation_protocol.tex','main.pdf'}
protected=[x for x in baseline if x not in allowed]
for rel in protected:
    actual=sha(PAPER/rel)
    check('protected:'+rel,actual==baseline[rel]['sha256'],sha256=actual)
vi=read(PAPER/'sections/06_simulation_results.tex')
old=read(RUN/'before/sections/06_simulation_results.tex')
app=read(PAPER/'sections/appendix_evaluation_protocol.tex')
oldapp=read(RUN/'before/sections/appendix_evaluation_protocol.tex')
for rel in ['sections/06_simulation_results.tex','sections/appendix_evaluation_protocol.tex']:
    check('before_matches_baseline:'+rel,sha(RUN/'before'/rel)==baseline[rel]['sha256'])

# Explicitly allowed textual relocations. Equality afterward ensures that
# no scientific interpretation or comparison was changed elsewhere in VI.
replacements=[
(r'\subsubsection{Compared Receivers and Evaluation Protocol}',r'\subsubsection{Compared Receivers}'),
('use $500$ paired physical scenes per point. All finite outputs, including\n'
 'those reaching the iteration limit, enter the reported metrics.\n'
 'These are retrospective comparisons: baseline threshold development\n'
 'overlaps evaluation scenes, and the user-count study uses damping\n'
 'settings selected after preliminary evaluation. The selection procedure\n'
 'and convergence counts are detailed in Appendix~\\ref{app:evaluation-protocol}.',
 'use $500$ paired physical scenes per point.'),
('five active terminals.\nEach curve ends at its actual stopping iteration.}',
 'five active terminals.}'),
('reaches a lower error level earlier. Its native stopping point is the\n'
 'imposed minimum of $60$ iterations, compared with $85$ for STMP.',
 'reaches a lower error level earlier.'),
('The extreme $Q=8$ case also tests the stability of the configured\n'
 "iterations. STMP's large NMSE is accompanied by $462$ of $500$ runs\n"
 'reaching the iteration limit, compared with two for the proposed receiver.\n'
 'The pilot-saving comparison above uses $Q\\geq16$, where both receivers\n'
 'converge in all evaluated scenes.', ''),
('scenes. The retrospective damping adjustments are given in\n'
 'Appendix~\\ref{app:evaluation-protocol}.}', 'scenes.}'),
]
expected=old
for i,(a,b) in enumerate(replacements):
    count=expected.count(a)
    check('authorized_edit_source_match:'+str(i+1),count==1,count=count)
    expected=expected.replace(a,b)
check('vi_contains_only_authorized_changes',compact(expected)==compact(vi))

for name,pattern in [
 ('five_equations',r'\\begin\{equation\}.*?\\end\{equation\}'),
 ('parameter_table',r'\\begin\{table\}.*?\\end\{table\}'),
 ('seven_figure_commands',r'\\includegraphics(?:\[[^\]]*\])?\{[^}]+\}'),
 ('labels',r'\\label\{[^}]+\}'),
 ('citations',r'\\cite(?:\[[^\]]*\])?\{[^}]+\}'),
]:
    a,b=re.findall(pattern,old,re.S),re.findall(pattern,vi,re.S)
    check(name+'_unchanged',a==b,before_count=len(a),after_count=len(b))

insert=('In the single-scene example of Fig.~\\ref{fig:cstmp-convergence},\n'
        'GP-CCD-MP-DRE stops at the imposed minimum of $60$ iterations,\n'
        'compared with $85$ for STMP. Each displayed trajectory ends at\n'
        'its actual stopping iteration.\n\n')
check('appendix_adds_only_actual_convergence_records',app.count(insert)==1
      and compact(app.replace(insert,''))==compact(oldapp))
check('appendix_is_still_included',r'\input{sections/appendix_evaluation_protocol}' in read(PAPER/'main.tex'))
apptext=compact(app)
required={
 'development_overlap':'Development and baseline-threshold selection overlap the evaluation scenes',
 'snr_range_selection':'SNR range was narrowed after interim inspection',
 'diagnostic_reuse':'All $12$ diagnostic inputs are included',
 'selected_replacement':'only scene~372 was rerun',
 'replacement_in_report':'this selected replacement is used in the reported panel',
 'retrospective_selection':'retrospective parameter development, rather than independent validation',
 'finite_outputs':'All finite outputs enter the reported metrics',
 'q8_counts':'At $Q=8$, the corresponding counts are $462$ and two out of $500$',
 'q16_convergence':'all runs at the evaluated $Q\\geq16$ satisfy the stopping criterion',
 'native_minimum':'stops at the imposed minimum of $60$ iterations',
 'stmp_endpoint':'compared with $85$ for STMP',
 'actual_endpoints':'Each displayed trajectory ends at its actual stopping iteration',
}
for name,text in required.items(): check('appendix_retains:'+name,text in apptext)

# Check every included narrative chapter I-VI, not the main-file appendix input.
for p in sorted((PAPER/'sections').glob('0[1-6]_*.tex')):
    s=read(p)
    forbidden=[r'app:evaluation-protocol',r'Appendix\s*[~ ]?\s*C\b',
        r'appendix_evaluation_protocol',r'\bevaluation protocol\b',
        r'\bretrospective\b',r'baseline.threshold development',
        r'overlaps? (?:the )?evaluation scenes',r'scene~372',
        r'All finite outputs',r'after preliminary evaluation']
    matches=[x for x in forbidden if re.search(x,s,re.I)]
    check('no_process_notice_or_appendix_c_pointer:'+p.name,not matches,matches=matches)
check('q8_runtime_paragraph_absent',"The extreme $Q=8$ case" not in vi and '$462$ of $500$' not in vi)
check('convergence_stop_records_absent_from_vi','native stopping point' not in vi
      and 'actual stopping iteration' not in vi and 'compared with $85$ for STMP' not in vi)

# Existing dataset identities are rechecked; only relocated run-count and
# actual-endpoint facts are recalculated in this migration audit.
old_audit=load(PAPER/'checks/experiment_analysis_20261030/baseline.json')
data_paths=[p for p in old_audit if p.endswith('/PLOT_DATA.json')]
data_bindings={}
for rel in data_paths:
    h=sha(ROOT/rel)
    check('dataset_unchanged:'+rel,h==old_audit[rel]['sha256'],sha256=h)
    data_bindings[rel]=h
convergence=load(ROOT/'result/snr_comparison/figures/convergence_current_paper_20261026/PLOT_DATA.json')['rows']
for method,n in [('C_STMP',60),('STMP',85)]:
    actual=max(r.get('iteration',r.get('parameters',{}).get('iteration'))
               for r in convergence if r['method']==method)
    check('actual_trajectory_endpoint:'+method,actual==n,actual=actual)
pilots=load(ROOT/'result/pilot_frames/figures/full_grid_final_20261026/PLOT_DATA.json')['rows']
for method,n in [('C_STMP',2),('STMP',462)]:
    rows=[r for r in pilots if r['method']==method and r['frames']==8]
    actual=rows[0]['stopping_reasons'].get('MAX_ITERATIONS',0) if len(rows)==1 else None
    check('q8_iteration_limit_count:'+method,actual==n,actual=actual)
check('q16_and_above_all_converged',all(r['convergence_rate']==1 for r in pilots
      if r['method'] in ['C_STMP','STMP'] and r['frames']>=16))

report={
 'status':'PASS' if all(c['passed'] for c in checks) else 'FAIL',
 'generated_utc':datetime.now(timezone.utc).isoformat(),
 'scope':'Authorized VI prose/caption relocation to Appendix C; full preservation of preexisting Appendix C; no Appendix C pointers or specified process notices in chapters I-VI; hashes of protected manuscript files, figures and seven saved plot datasets; recomputation only of relocated trajectory endpoints and Q8 cap counts. Not a new experiment, training, full numerical reanalysis, compilation or visual review.',
 'checks_count':len(checks),'checks':checks,
 'source_sha256':{rel:sha(PAPER/rel) for rel in ['sections/06_simulation_results.tex','sections/appendix_evaluation_protocol.tex']},
 'baseline_sha256':sha(RUN/'baseline.json'),'data_sha256':data_bindings,
 'canonical_files_written':False,'training_started':False,'inference_started':False,
 'visual_review':'Performed separately; not asserted by this script.'}
(RUN/'MIGRATION_VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'checks':len(checks),'failures':[c['name'] for c in checks if not c['passed']]}))
raise SystemExit(0 if report['status']=='PASS' else 1)
