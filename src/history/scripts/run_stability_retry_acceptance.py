"""Freeze the convergence-based retry rule and use a new sealed scene bank."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import shutil
import subprocess
import sys
import time
import repair_stability_retry as r
import validate_stability_candidate as validation


def preserve():
    for path,digest in r.d.paired.read(r.OUT/'PRESERVATION.json').items():
        assert r.d.paired.sha(r.d.ROOT/path)==digest,path


def freeze():
    gate=validation.evaluate('development',candidate=r.NAME)
    assert gate['passed']
    for name in ('FIRST_ATTEMPT_CHECK.json','RETRY_STATE_RESET_CHECK.json','RETRY_CONTROL_FLOW_CHECK.json','SEED_ISOLATION_CHECK.json'):
        assert r.d.paired.read(r.OUT/name)['passed']
    old_gate=r.d.paired.read(r.OLD/'ACCEPTANCE_GATE.json')
    assert not old_gate['passed'] and old_gate['cases']==60
    preserve()
    path=r.OUT/'FROZEN_CANDIDATE.json'
    if path.exists():return
    sources=r.d.paired.identities()
    config=r.d.paired.read(r.OUT/'configs'/f'{r.NAME}.json')
    files=[r.OUT/'configs'/f'{r.NAME}.json',r.OUT/'PROTOCOL.json',r.d.ROOT/config['prior_definition']]
    files += [r.d.ROOT/config[k] for k in ('first_checkpoint','second_checkpoint','evidence_checkpoint')]
    files += [r.d.ROOT/'scripts'/name for name in ('repair_stability_development.py','benchmark_receiver_execution.py',
        'evaluate_saved_baseline_inputs.py','validate_stability_candidate.py','stability_damping_retry.py',
        'repair_stability_retry.py','check_stability_retry.py','run_stability_retry_acceptance.py')]
    for source in files:
        sources[str(source.resolve())]=r.d.paired.sha(source)
        if source.suffix=='.py':
            target=r.OUT/'frozen_source'/source.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
    r.d.paired.save(path,dict(candidate=r.NAME,configuration=config,created_unix=time.time(),
        execution=dict(cudnn_allow_tf32=False,matmul_allow_tf32=False,cuda_graph_first_second=True,
            damping_order=[.1,.05],iterations_per_attempt=1200,maximum_total_iterations=2400,
            selection='First native convergence; truth and NMSE are never selection inputs'),
        development_gate_sha256=r.d.paired.sha(r.OUT/'DEVELOPMENT_GATE.json'),
        previous_failed_acceptance_sha256=r.d.paired.sha(r.OLD/'ACCEPTANCE_GATE.json'),
        new_acceptance_seed_base=202610193000001,source_and_weight_sha256=sources))
    (r.OUT/'logs').mkdir(exist_ok=True)


def one(scene,users):
    for method in (r.NAME,'offgrid_sbl'):
        out=r.OUT/'evaluations/acceptance'/method/f'scene{scene:03d}_users{users}'
        if (out/'SUMMARY.json').exists():continue
        log=r.OUT/'logs'/f'acceptance_{method}_scene{scene:03d}_users{users}.log'
        with log.open('x') as handle:
            completed=subprocess.run([sys.executable,'scripts/repair_stability_retry.py','--split','acceptance',
                '--method',method,'--scene',str(scene),'--users',str(users)],cwd=r.d.ROOT,stdout=handle,stderr=subprocess.STDOUT)
        if completed.returncode:raise RuntimeError(f'{log}: {completed.returncode}')
    return r.d.paired.read(r.OUT/'evaluations/acceptance'/r.NAME/f'scene{scene:03d}_users{users}'/'SUMMARY.json')


if __name__=='__main__':
    r.prepare();deadline=time.monotonic()+3600
    while not (r.OUT/'DEVELOPMENT_GATE.json').exists():
        if time.monotonic()>deadline:raise TimeoutError('Development integration check did not finish')
        time.sleep(5)
    freeze();rows=[]
    r.d.paired.save(r.OUT/'STATUS.json',dict(status='ACCEPTANCE_RUNNING',completed=0,expected=60,formal_experiments='PAUSED'))
    with ThreadPoolExecutor(4) as pool:
        tasks=[pool.submit(one,s,k) for s in range(12) for k in (20,40,60,80,100)]
        for future in as_completed(tasks):
            row=future.result();rows.append(row)
            r.d.paired.save(r.OUT/'STATUS.json',dict(status='ACCEPTANCE_RUNNING',completed=len(rows),expected=60,
                formal_experiments='PAUSED',updated_unix=time.time()))
            print(len(rows),'/60',row['scene'],row['users'],row['metrics']['nmse_db'],row['stopping_reason'],flush=True)
    gate=validation.evaluate('acceptance',candidate=r.NAME);preserve()
    r.d.paired.save(r.OUT/'ACCEPTANCE_GATE.json',gate)
    r.d.paired.save(r.OUT/'STATUS.json',dict(status='ACCEPTANCE_PASSED' if gate['passed'] else 'ACCEPTANCE_FAILED',
        completed=60,expected=60,formal_experiments='PAUSED',updated_unix=time.time()))
    print('NEW ACCEPTANCE',gate['status'],flush=True)
