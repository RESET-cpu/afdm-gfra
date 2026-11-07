"""Verify the retry control flow and reuse unchanged converged development work."""
from pathlib import Path
import shutil
import time
import numpy as np
import repair_stability_retry as r
import validate_stability_candidate as validation


def wait_summary(path):
    deadline=time.monotonic()+1800
    while not path.exists():
        if (path.parent/'FAILURE.json').exists() or time.monotonic()>deadline:raise RuntimeError(str(path))
        time.sleep(2)
    return r.d.paired.read(path)


def identical(a,b):
    x,y=r.d.paired.arrays(a),r.d.paired.arrays(b)
    return set(x)==set(y) and all(np.array_equal(x[k],y[k]) for k in x)


if __name__=='__main__':
    r.prepare()
    first=r.OUT/'evaluations/development'/r.NAME/'scene000_users20'
    row=wait_summary(first/'SUMMARY.json')
    native=r.OLD/'evaluations/development/damping0.1_budget1200_fp32/scene000_users20'
    assert row['stopping_reason']=='CONVERGED'
    assert identical(first/'prediction.npz',native/'prediction.npz')
    assert r.d.paired.read(first/'record.json')['attempt_count']==1
    r.d.paired.save(r.OUT/'FIRST_ATTEMPT_CHECK.json',dict(passed=True,exact_native_prediction=True,
        first_attempt_iterations=row['iterations'],native_sha256=r.d.paired.sha(native/'prediction.npz')))
    for method in (r.NAME,'offgrid_sbl'):
        old_method='damping0.1_budget1200_fp32' if method==r.NAME else method
        for scene in range(4):
            for users in (20,40,60,80,100):
                old=r.OLD/'evaluations/development'/old_method/f'scene{scene:03d}_users{users}'
                new=r.OUT/'evaluations/development'/method/old.name
                if (new/'SUMMARY.json').exists():continue
                row=r.d.paired.read(old/'SUMMARY.json')
                if method==r.NAME:assert row['stopping_reason']=='CONVERGED'
                new.mkdir(parents=True,exist_ok=False);proof={}
                for name in ('record.json','TRACE.json','prediction.npz'):
                    shutil.copy2(old/name,new/name);proof[str(old/name)]=r.d.paired.sha(old/name)
                    assert r.d.paired.sha(new/name)==proof[str(old/name)]
                r.d.paired.save(new/'PLAN.json',dict(candidate=method,reused_from=proof,
                    original_plan=r.d.paired.read(old/'PLAN.json'),original_plan_sha256=r.d.paired.sha(old/'PLAN.json'),
                    selection='The first 0.1 attempt already converged; the retry rule therefore makes no further inference call.'))
                r.d.paired.save(new/'SUMMARY.json',dict(row,candidate=method,reused_from=proof,
                    reuse_reason='Unchanged first-attempt output; original native execution time retained. Not a controlled speed measurement.'))
    reverse=r.OUT/'evaluations/development/damping_retry_reverse_check_fp32/scene001_users100'
    wait_summary(reverse/'SUMMARY.json');record=r.d.paired.read(reverse/'record.json')
    checks=[]
    for i,damping in enumerate((.05,.1)):
        native=r.OLD/'evaluations/development'/f'damping{damping:g}_budget1200_fp32'/'scene001_users100'
        path=reverse/'attempts'/f'attempt{i}.npz'
        deadline=time.monotonic()+60
        while not path.exists():
            if time.monotonic()>deadline:raise TimeoutError(str(path))
            time.sleep(1)
        checks.append(dict(attempt=i,damping=damping,exact_native_prediction=identical(path,native/'prediction.npz'),
            native_prediction_sha256=r.d.paired.sha(native/'prediction.npz')))
    assert all(x['exact_native_prediction'] for x in checks)
    assert record['attempt_count']==2 and record['converged'] and record['iterations']==2079
    assert len(record['trace'])==2079
    assert record['retry_policy']['attempts'][0]['converged'] is False
    assert record['retry_policy']['attempts'][1]['converged'] is True
    r.d.paired.save(r.OUT/'RETRY_STATE_RESET_CHECK.json',dict(passed=True,checks=checks,total_iterations=2079,
        actual_order_for_integration_check=[.05,.1],final_policy_order=[.1,.05],
        scope='Original development scene only; this reversed-order check is not a final-policy performance case.'))
    gate=validation.evaluate('development',candidate=r.NAME)
    r.d.paired.save(r.OUT/'DEVELOPMENT_GATE.json',gate)
    print(gate['status'],gate['cases'],'state reset exact',flush=True)
