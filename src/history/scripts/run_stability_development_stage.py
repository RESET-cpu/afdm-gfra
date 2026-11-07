"""Run a declared candidate on all development cases with bounded concurrency."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import subprocess
import sys
import time
import repair_stability_development as d


def one(scene,users,candidate):
    out=d.OUT/'evaluations/development'/candidate/f'scene{scene:03d}_users{users}'
    if (out/'SUMMARY.json').exists():
        return d.paired.read(out/'SUMMARY.json')
    if (out/'PLAN.json').exists():
        deadline=time.monotonic()+1800
        while not (out/'SUMMARY.json').exists():
            if (out/'FAILURE.json').exists() or time.monotonic()>deadline:
                raise RuntimeError(f'Existing attempt did not complete: {out}')
            time.sleep(2)
        return d.paired.read(out/'SUMMARY.json')
    ready=d.OUT/'bank/development'/f'scene{scene:03d}_users{users}'/'READY.json'
    deadline=time.monotonic()+1800
    while not ready.exists():
        if time.monotonic()>deadline:
            raise TimeoutError(str(ready))
        time.sleep(2)
    log=d.OUT/'logs'/f'{candidate}_scene{scene:03d}_users{users}.log'
    log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('x') as handle:
        result=subprocess.run([sys.executable,'scripts/repair_stability_development.py',
            '--candidate',candidate,'--scene',str(scene),'--users',str(users)],
            cwd=d.ROOT,stdout=handle,stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f'{log}: return code {result.returncode}')
    return d.paired.read(out/'SUMMARY.json')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',required=True)
    parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args()
    rows=[]
    with ThreadPoolExecutor(args.workers) as pool:
        tasks=[pool.submit(one,scene,users,args.candidate) for scene in range(4) for users in (20,40,60,80,100)]
        for future in as_completed(tasks):
            r=future.result();rows.append(r)
            print(len(rows),'/20',r['scene'],r['users'],r['metrics']['nmse_db'],r['stopping_reason'],flush=True)
    d.paired.save(d.OUT/f'DEVELOPMENT_{args.candidate}.json',dict(status='COMPLETE',rows=rows))
