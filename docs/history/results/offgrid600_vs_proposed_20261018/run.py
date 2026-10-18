"""Fixed independent development panel; no fitting or test-driven selection."""
from pathlib import Path
import sys
import time
import json
import gzip
import traceback
import warnings
from collections import Counter
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'experiment'))
import _common as c

METHODS = ['offgrid120', 'offgrid600', 'proposed']


def compressed(path, value):
    with gzip.open(path, 'wt') as f:
        json.dump(value, f, ensure_ascii=False, allow_nan=False)


def main():
    import torch
    from threadpoolctl import threadpool_limits
    plan_path = OUT/'PLAN.json'
    if not plan_path.exists():
        c.save(plan_path, dict(
            purpose='Independent development comparison, fixed before outcomes; no tuning',
            seed_base=202610182000001, scenes=10, snr_db=[-4,-2,0,2,4,6],
            users=40, frames=16, activity_probability=.1, methods=METHODS,
            scale=c.read(ROOT/'configs/proposed.json')['scale'], expected_inferences=180,
            configs=dict(offgrid120='configs/offgrid_baselines.json',
                         offgrid600='configs/experiments/offgrid_sbl_600.json', proposed='configs/proposed.json'),
            pairing='Same physical scene and standard noise across SNR; identical observation and estimated phase for three methods',
            thresholds='Frozen original thresholds; 600-iteration thresholds reused, not recalibrated',
            device='cpu', torch_threads=1, blas_threads=1, execution='Serial; method order cyclically rotated by condition',
            timing='Native conditional receiver times; phase time separate; descriptive CPU times, not a dedicated latency benchmark',
            hard_timeout_seconds=3600, bootstrap_replicates=10000, bootstrap_seed=182026,
            analysis='Pooled errors/energies; paired physical-scene percentile bootstrap; descriptive pointwise intervals, not simultaneous claims',
            source_and_weight_sha256=c.identities() | {str(Path(__file__).relative_to(ROOT)):c.sha(__file__)},
            historical_results='Preserved; no previous 500-scene result imported'))
    plan=c.read(plan_path); c.verify_sources(plan)
    start=time.monotonic()
    c.save(OUT/'RUN_STATE.json',dict(status='RUNNING',pid=__import__('os').getpid(),started_utc=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()))
    torch.set_num_threads(1)
    with threadpool_limits(1):
        receivers={
            name:c.EstimatedNoiseBaselineReceiver('offgrid_sbl',config=ROOT/plan['configs'][name],device='cpu')
            for name in METHODS[:2]}
        receivers['proposed']=c.EstimatedNoiseProposedReceiver(c.read(ROOT/plan['configs']['proposed']),device='cpu')
        controls=c.phase.Controls(**c.read(ROOT/'configs/proposed_frontend.json')['phase_estimation'])
        completed=0
        for scene in range(plan['scenes']):
            for index,snr in enumerate(plan['snr_db']):
                if time.monotonic()-start > plan['hard_timeout_seconds']:
                    raise TimeoutError('Predeclared one-hour development run limit exceeded; partial data retained')
                folder=OUT/f'scene{scene:03d}'/f'condition{index:02d}'
                targets=[folder/(m+'.json') for m in METHODS]
                if all(p.exists() for p in targets):
                    for p in targets:
                        r=c.read(p)
                        if r['status']!='COMPLETE' or c.sha(p.with_suffix('.npz'))!=r['compact_sha256']:
                            raise ValueError('Preserved failed or changed result: '+str(p))
                    completed+=3
                    continue
                with warnings.catch_warnings(record=True) as notices:
                    warnings.simplefilter('always',RuntimeWarning)
                    inputs,truth,metadata=c.observation(plan['seed_base']+scene,
                        dict(users=plan['users'],frames=plan['frames'],snr_db=snr,activity_probability=plan['activity_probability']),plan['scale'])
                    values,phase_record=c.phase.estimate(inputs,controls)
                conditional=inputs.at_estimated_phase(values['phase_slopes'])
                input_hash={k:c.array_sha256(v) for k,v in inputs.arguments().items()}
                identity=dict(arrays=input_hash,operator_sha256=c.array_sha256(conditional.operator),generation=metadata)
                if (folder/'INPUT.json').exists() and c.read(folder/'INPUT.json')!=identity:
                    raise ValueError('Regenerated input differs')
                c.save(folder/'INPUT.json',identity)
                c.save(folder/'PHASE.json',dict(record=phase_record,warning_counts=dict(Counter(str(w.message) for w in notices))))
                c.save_arrays(folder/'truth.npz',truth)
                c.save_arrays(folder/'phase.npz',values)
                offset=(scene*len(plan['snr_db'])+index)%3
                order=METHODS[offset:]+METHODS[:offset]
                native={}
                for method in order:
                    target=folder/(method+'.json')
                    if target.exists():
                        old=c.read(target)
                        if old['status']!='COMPLETE' or c.sha(target.with_suffix('.npz'))!=old['compact_sha256']:
                            raise ValueError('Preserved failed or changed result: '+str(target))
                        with gzip.open(folder/(method+'.native.json.gz'),'rt') as f:native[method]=json.load(f)
                        completed+=1
                        continue
                    try:
                        with warnings.catch_warnings(record=True) as notices:
                            warnings.simplefilter('always',RuntimeWarning)
                            arrays,record=receivers[method].infer(conditional)
                        if record.get('status')!='COMPLETE' or not all(np.isfinite(v).all() for v in arrays.values()):
                            raise FloatingPointError('Nonfinite/incomplete native result')
                        metrics=c.score_arrays(arrays,truth)
                        compact={k:v for k,v in arrays.items() if np.asarray(v).ndim<=1}
                        compact.update(per_user_error=np.asarray(metrics['per_user_error']),truth_activity=truth['activity'])
                        c.save_arrays(target.with_suffix('.npz'),compact)
                        if scene==0:c.save_arrays(folder/(method+'.prediction.npz'),arrays)
                        compressed(folder/(method+'.native.json.gz'),record)
                        row=dict(status='COMPLETE',scene=scene,seed=plan['seed_base']+scene,snr_db=snr,method=method,
                            metrics=metrics,iterations=record['iterations'],stopping_reason=record['stopping_reason'],
                            receiver_seconds=record['seconds'],phase_seconds=phase_record['seconds'],
                            input_sha256=input_hash,operator_sha256=identity['operator_sha256'],
                            compact_sha256=c.sha(target.with_suffix('.npz')),
                            native_sha256=c.sha(folder/(method+'.native.json.gz')),
                            warning_counts=dict(Counter(str(w.message) for w in notices)))
                        c.save(target,row); native[method]=record
                    except Exception:
                        c.save(target,dict(status='FAILED',scene=scene,snr_db=snr,method=method,traceback=traceback.format_exc()))
                        raise
                    completed+=1
                    print(f'{completed}/180 scene={scene} SNR={snr:+g} {method}: NMSE={metrics["nmse_db"]:.3f} dB errors={metrics["misses"]+metrics["false_alarms"]} iterations={record["iterations"]} {record["stopping_reason"]} seconds={record["seconds"]:.2f}',flush=True)
                n=native['offgrid120']['iterations']
                if native['offgrid120']['trace']!=native['offgrid600']['trace'][:n]:
                    raise AssertionError('Budget extension changed the shared native iteration prefix')
                c.save(folder/'PAIR_CHECK.json',dict(status='COMPLETE',offgrid_shared_updates_exact=n,identical_inputs_and_phase=True))
                c.save(OUT/'PROGRESS.json',dict(completed=completed,total=180,elapsed_seconds=time.monotonic()-start,last_scene=scene,last_snr=snr))
    c.verify_sources(plan)
    c.save(OUT/'RUN_STATE.json',dict(status='COMPLETE',completed=completed,seconds=time.monotonic()-start))
    print('COMPLETE',flush=True)


if __name__=='__main__':
    try:main()
    except Exception:
        c.save(OUT/'RUN_STATE.json',dict(status='FAILED',traceback=traceback.format_exc()))
        raise
