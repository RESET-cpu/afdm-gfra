"""Freeze a development-passing candidate before opening independent acceptance."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import shutil
import subprocess
import sys
import time
import validate_stability_candidate as validation
import repair_stability_development as d


def preserve_check():
    for path,digest in d.paired.read(d.OUT/'PRESERVATION.json').items():
        if d.paired.sha(d.ROOT/path)!=digest:
            raise ValueError('Preserved asset changed: '+path)


def freeze():
    gate=validation.evaluate('development')
    d.paired.save(d.OUT/'DEVELOPMENT_GATE.json',gate)
    if not gate['passed']:
        return False
    assert d.paired.read(d.OUT/'PRECISION_AUDIT.json')['passed']
    preserve_check()
    path=d.OUT/'FROZEN_CANDIDATE.json'
    if path.exists():
        return True
    sources=d.paired.identities()
    config=d.paired.read(d.OUT/'configs'/f'{validation.TARGET}.json')
    paths=[d.OUT/'configs'/f'{validation.TARGET}.json',d.ROOT/config['prior_definition']]
    paths += [d.ROOT/config[k] for k in ('first_checkpoint','second_checkpoint','evidence_checkpoint')]
    paths += [d.ROOT/'scripts'/name for name in ('repair_stability_development.py',
        'benchmark_receiver_execution.py','evaluate_saved_baseline_inputs.py',
        'validate_stability_candidate.py','run_stability_acceptance.py')]
    for source in paths:
        sources[str(source.resolve())]=d.paired.sha(source)
        if source.suffix=='.py':
            target=d.OUT/'frozen_source'/source.name
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source,target)
    d.paired.save(path,dict(candidate=validation.TARGET,created_unix=time.time(),
        configuration=config,execution=dict(cudnn_allow_tf32=False,matmul_allow_tf32=False,
            cuda_graph_first_second=True,network_dtype='float32',iteration_dtype='complex128'),
        development_gate_sha256=d.paired.sha(d.OUT/'DEVELOPMENT_GATE.json'),
        precision_audit_sha256=d.paired.sha(d.OUT/'PRECISION_AUDIT.json'),
        source_and_weight_sha256=sources,acceptance_opened_after_this_freeze=True))
    return True


def one(scene,users):
    for candidate in (validation.TARGET,'offgrid_sbl'):
        out=d.OUT/'evaluations/acceptance'/candidate/f'scene{scene:03d}_users{users}'
        if (out/'SUMMARY.json').exists():
            continue
        log=d.OUT/'logs'/f'acceptance_{candidate}_scene{scene:03d}_users{users}.log'
        with log.open('x') as handle:
            result=subprocess.run([sys.executable,'scripts/repair_stability_development.py',
                '--split','acceptance','--candidate',candidate,'--scene',str(scene),'--users',str(users)],
                cwd=d.ROOT,stdout=handle,stderr=subprocess.STDOUT)
        if result.returncode:
            raise RuntimeError(f'{log}: return code {result.returncode}')
    return d.paired.read(d.OUT/'evaluations/acceptance'/validation.TARGET/f'scene{scene:03d}_users{users}'/'SUMMARY.json')


if __name__=='__main__':
    deadline=time.monotonic()+3600
    while not (d.OUT/f'DEVELOPMENT_{validation.TARGET}.json').exists():
        if time.monotonic()>deadline:raise TimeoutError('Development did not finish')
        time.sleep(5)
    if not freeze():
        d.paired.save(d.OUT/'STATUS.json',dict(status='DEVELOPMENT_FAILED',formal_experiments='PAUSED',acceptance_opened=False))
        print('DEVELOPMENT FAILED; ACCEPTANCE SEALED; FORMAL PAUSED',flush=True)
        raise SystemExit(0)
    rows=[]
    with ThreadPoolExecutor(4) as pool:
        futures=[pool.submit(one,s,k) for s in range(12) for k in (20,40,60,80,100)]
        for future in as_completed(futures):
            row=future.result();rows.append(row)
            d.paired.save(d.OUT/'STATUS.json',dict(status='ACCEPTANCE_RUNNING',completed=len(rows),expected=60,
                formal_experiments='PAUSED',updated_unix=time.time()))
            print(len(rows),'/60',row['scene'],row['users'],row['metrics']['nmse_db'],row['stopping_reason'],flush=True)
    gate=validation.evaluate('acceptance')
    preserve_check()
    d.paired.save(d.OUT/'ACCEPTANCE_GATE.json',gate)
    d.paired.save(d.OUT/'STATUS.json',dict(status='ACCEPTANCE_PASSED' if gate['passed'] else 'ACCEPTANCE_FAILED',
        completed=60,expected=60,formal_experiments='PAUSED',updated_unix=time.time()))
    print('ACCEPTANCE',gate['status'],flush=True)
