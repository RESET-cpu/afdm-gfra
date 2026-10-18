"""Six old cases: recurrent TSVD with two direct row probes, no feature projection."""
import json
from pathlib import Path
import sys,time,warnings
from collections import Counter
import numpy as np
import torch
from threadpoolctl import threadpool_limits
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from afdm_jadcedd.algorithm.registry import build_receiver
from afdm_jadcedd.algorithm.baselines.ldamp_joint.core import solve_projected
from afdm_jadcedd.system.observation import load_input
from afdm_jadcedd.utils import sha256,write_json
from structure import StructuredDenoiser
from develop import metrics


def main():
    torch.set_num_threads(1)
    out=ROOT/'results/ldamp_structure_20261015/development_direct';out.mkdir(exist_ok=False)
    base=build_receiver('ldamp',device='mps');denoise=StructuredDenoiser(base.denoise)
    controls=dict(iterations=10,row_probes=2,measurement_batch=4,seed=202610150401)
    paths=[Path(__file__),Path(__file__).with_name('structure.py'),ROOT/'src/afdm_jadcedd/algorithm/baselines/ldamp_joint/core.py',ROOT/'src/afdm_jadcedd/algorithm/baselines/ldamp_joint/projected_trace.py']
    write_json(out/'PLAN.json',dict(independent_validation=False,scenes=[0,1],snr_db=[-4,0,6],controls=controls,base_signature=base.signature,sources={str(p.relative_to(ROOT)):sha256(p) for p in paths}))
    rows=[];started=time.time()
    for scene in range(2):
        for snr in [-4,0,6]:
            source=ROOT/f'results/ldamp_diagnosis_20261014/receiver_pilot/calibration/scene{scene:03d}/snr{snr:+03d}'
            row=dict(scene=scene,snr_db=snr,method='recurrent_rank_one_direct2',input_sha256=sha256(source/'input.npz'))
            try:
                with warnings.catch_warnings(record=True) as caught,threadpool_limits(1):
                    warnings.simplefilter('always',RuntimeWarning)
                    result=solve_projected(load_input(source/'input.npz'),denoise,**controls)
                with np.load(source/'truth.npz') as saved:truth={k:saved[k] for k in saved.files}
                target=out/f'scene{scene:03d}_snr{snr:+03d}.npz';np.savez_compressed(target,estimate=result['estimate'],activity_score=result['energy'])
                row.update(status='COMPLETE',**metrics(result['estimate'],truth),seconds=result['seconds'],warnings=dict(Counter(str(w.message) for w in caught)),output_sha256=sha256(target),trace=result['trace'],score=result['energy'].tolist())
            except Exception as exc:row.update(status='FAILED',error=repr(exc))
            rows.append(row);write_json(out/'ROWS.json',rows);write_json(out/'STATUS.json',dict(status='RUNNING',completed=len(rows),expected=6,seconds=time.time()-started))
            print(json.dumps({k:v for k,v in row.items() if k not in ['active','score','trace']}),flush=True)
    write_json(out/'STATUS.json',dict(status='COMPLETE' if all(r['status']=='COMPLETE' for r in rows) else 'FAILED',completed=len(rows),seconds=time.time()-started))


if __name__=='__main__':main()
