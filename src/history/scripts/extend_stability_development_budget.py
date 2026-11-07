"""Re-evaluate budget-limited development cases; reuse proven early stops."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import shutil
import time
import run_stability_development_stage as stage
import repair_stability_development as d

SOURCE='damping0.05_fp32'
TARGET='damping0.05_budget1200_fp32'


def one(scene,users):
    old=d.OUT/'evaluations/development'/SOURCE/f'scene{scene:03d}_users{users}'
    new=d.OUT/'evaluations/development'/TARGET/old.name
    limit=time.monotonic()+1800
    while not (old/'SUMMARY.json').exists():
        if (old/'FAILURE.json').exists() or time.monotonic()>limit:
            raise RuntimeError(str(old))
        time.sleep(2)
    summary=d.paired.read(old/'SUMMARY.json')
    if summary['stopping_reason']!='CONVERGED' or (new/'PLAN.json').exists():
        return stage.one(scene,users,TARGET)
    a=d.paired.read(d.OUT/'configs'/f'{SOURCE}.json')
    b=d.paired.read(d.OUT/'configs'/f'{TARGET}.json')
    old_budget=a['ep']['iterations'];a['ep']['iterations']=b['ep']['iterations']
    assert a==b and summary['iterations']<=old_budget<b['ep']['iterations']
    assert summary['prediction_sha256']==d.paired.sha(old/'prediction.npz')
    new.mkdir(parents=True,exist_ok=False)
    proof={}
    for name in ('record.json','TRACE.json','prediction.npz'):
        shutil.copy2(old/name,new/name)
        proof[str((old/name).resolve())]=d.paired.sha(old/name)
        assert d.paired.sha(new/name)==proof[str((old/name).resolve())]
    summary=dict(summary,candidate=TARGET,reused_from=proof,
        reuse_reason='Only the maximum budget changed, after the already reached unchanged stopping condition. Recorded inference configuration and timing remain the original values.')
    d.paired.save(new/'PLAN.json',dict(candidate=TARGET,configuration=b,original_plan=d.paired.read(old/'PLAN.json'),
        original_plan_sha256=d.paired.sha(old/'PLAN.json'),reused=True))
    d.paired.save(new/'SUMMARY.json',summary)
    return summary


if __name__=='__main__':
    rows=[]
    with ThreadPoolExecutor(3) as pool:
        tasks=[pool.submit(one,s,k) for s in range(4) for k in (20,40,60,80,100)]
        for future in as_completed(tasks):
            r=future.result();rows.append(r)
            print(len(rows),'/20',r['scene'],r['users'],r['metrics']['nmse_db'],r['stopping_reason'],flush=True)
    d.paired.save(d.OUT/f'DEVELOPMENT_{TARGET}.json',dict(status='COMPLETE',rows=rows))
