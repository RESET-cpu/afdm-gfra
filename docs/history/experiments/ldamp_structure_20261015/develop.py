"""Compare unchanged L-DAMP, final TSVD, and recurrent TSVD on six old cases."""
import json
from pathlib import Path
import sys,time,warnings
from collections import Counter
import numpy as np
import torch
from threadpoolctl import threadpool_limits
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'experiments/ldamp_complete_20261015'))
from afdm_jadcedd.algorithm.registry import build_receiver
from afdm_jadcedd.system.observation import load_input
from afdm_jadcedd.utils import sha256,write_json
from receiver import solve
from structure import rank_one,StructuredDenoiser


def metrics(estimate,truth):
    active=truth['activity'].astype(bool);h=truth['channel']
    errors=np.sum(abs(estimate-h)**2,axis=(1,2,3))
    return dict(full_error=float(errors.sum()),active_error=float(errors[active].sum()),
        inactive_error=float(errors[~active].sum()),signal_energy=float(np.sum(abs(h)**2)),active=active.tolist())


def main():
    torch.set_num_threads(1)
    out=ROOT/'results/ldamp_structure_20261015/development';out.mkdir(exist_ok=False)
    original=build_receiver('ldamp',device='mps');candidate=StructuredDenoiser(original.denoise)
    controls=dict(iterations=10,probes=8,seed=202610150401,group_size=256)
    write_json(out/'PLAN.json',dict(independent_validation=False,scenes=[0,1],snr_db=[-4,0,6],
        controls=controls,original_signature=original.signature,sources={str(p.relative_to(ROOT)):sha256(p) for p in Path(__file__).parent.glob('*.py')},
        recurrence_source_sha256=sha256(ROOT/'experiments/ldamp_complete_20261015/receiver.py'),
        interpretation='Whole 256-feature partial trace for recurrent projection; original grouped trace only for unchanged independent-beam receiver. No truth in inference or projection.'))
    rows=[];started=time.time()
    for scene in range(2):
        for snr in [-4,0,6]:
            source=ROOT/f'results/ldamp_diagnosis_20261014/receiver_pilot/calibration/scene{scene:03d}/snr{snr:+03d}'
            inputs=load_input(source/'input.npz')
            with np.load(source/'truth.npz') as saved:truth={k:saved[k] for k in saved.files}
            cached=None
            for method in ['original','output_rank_one','recurrent_rank_one']:
                row=dict(scene=scene,snr_db=snr,method=method,input_sha256=sha256(source/'input.npz'))
                try:
                    with warnings.catch_warnings(record=True) as caught,threadpool_limits(1):
                        warnings.simplefilter('always',RuntimeWarning)
                        start=time.monotonic()
                        if method=='original':
                            arrays,record=original.infer(inputs);cached=(arrays,record)
                        elif method=='output_rank_one':
                            if cached is None:raise ValueError('Original inference failed')
                            arrays={k:v.copy() for k,v in cached[0].items()}
                            arrays['estimate']=rank_one(arrays['estimate'])
                            # Keep original activity score/decision for this first isolated control.
                            arrays['channel_energy']=np.sum(abs(arrays['estimate'])**2,axis=(1,2,3))
                            record=dict(seconds=cached[1]['seconds']+time.monotonic()-start)
                        else:
                            result=solve(inputs,candidate,**controls)
                            arrays=dict(estimate=result.pop('estimate'),activity_score=result.pop('energy'))
                            record=result
                        duration=record['seconds']
                    target=out/f'{method}_scene{scene:03d}_snr{snr:+03d}.npz';np.savez_compressed(target,**arrays)
                    row.update(status='COMPLETE',**metrics(arrays['estimate'],truth),seconds=duration,
                        score=arrays['activity_score'].tolist(),warnings=dict(Counter(str(w.message) for w in caught)),
                        output_sha256=sha256(target),trace=record.get('trace',[]))
                except Exception as exc:row.update(status='FAILED',error=repr(exc))
                rows.append(row);write_json(out/'ROWS.json',rows)
                write_json(out/'STATUS.json',dict(status='RUNNING',completed=len(rows),expected=18,seconds=time.time()-started))
                print(json.dumps({k:v for k,v in row.items() if k not in ['active','score','trace','warnings']}),flush=True)
    summary=[]
    for method in ['original','output_rank_one','recurrent_rank_one']:
        for snr in [-4,0,6]:
            v=[r for r in rows if r['method']==method and r['snr_db']==snr]
            if all(r['status']=='COMPLETE' for r in v):summary.append(dict(method=method,snr_db=snr,nmse_db=float(10*np.log10(sum(r['full_error'] for r in v)/sum(r['signal_energy'] for r in v)))))
    write_json(out/'SUMMARY.json',dict(results=summary,independent_validation=False))
    write_json(out/'STATUS.json',dict(status='COMPLETE' if all(r['status']=='COMPLETE' for r in rows) else 'FAILED',completed=len(rows),seconds=time.time()-started))


if __name__=='__main__':main()
