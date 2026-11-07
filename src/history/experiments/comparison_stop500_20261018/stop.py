import os,signal,time,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
R=ROOT/'results/baseline_comparison_600_20261017'
def save(name,d):
 p=R/name;t=p.with_suffix('.tmp');t.write_text(json.dumps(d));t.replace(p)
state=json.loads((R/'RUN.json').read_text());supervisor=json.loads((R/'CONTINUATION_STATUS.json').read_text())
parents=[supervisor['pid'],state['pid']]
for pid in parents:os.kill(pid,signal.SIGSTOP)
save('SCOPE_REVISION_500.json',dict(request='User requested stopping at 500 physical scenes',scenes=500,receiver_runs=17500,original_plan_preserved=True,pid=os.getpid(),status='WAITING_FOR_500',time=time.time()))
workers=dict(zip(state['roles'],state['children']))
while workers:
 for role,pid in list(workers.items()):
  methods=['offgrid_sbl','gnn','gamp','somp'] if role=='producer' else ['proposed']
  scenes=range(500) if role=='producer' else range(int(role[-1]),500,2)
  paths=[R/'scenes'/f'scene{i:03d}'/f'snr{s:+03d}'/(m+'.metrics.json') for i in scenes for s in range(-4,9,2) for m in methods]
  if all(p.exists() for p in paths):
   assert all(json.loads(p.read_text())['status']=='COMPLETE' for p in paths)
   os.kill(pid,signal.SIGTERM);del workers[role]
 if workers:time.sleep(1)
for pid in parents:
 os.kill(pid,signal.SIGKILL)
save('SCOPE_REVISION_500.json',dict(request='User requested stopping at 500 physical scenes',scenes=500,receiver_runs=17500,original_plan_preserved=True,status='COMPUTATION_STOPPED_AT_500',time=time.time()))
save('RUN.json',dict(status='USER_STOPPED_AFTER_500',receiver_runs=17500,original_target=600,finished_unix=time.time()))
save('CONTINUATION_STATUS.json',dict(status='USER_STOPPED_AFTER_500',stage='awaiting_500_report',physical_scenes=500,receiver_runs=17500,updated_unix=time.time()))
print('500 scenes complete; all experiment workers stopped',flush=True)
