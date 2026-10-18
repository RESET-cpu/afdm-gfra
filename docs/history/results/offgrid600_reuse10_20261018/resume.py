"""Ten supplemental SBL runs; reuse original inputs, phase and comparators."""
from pathlib import Path
import sys,json,gzip,time,warnings,os,traceback
from collections import Counter
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
SOURCE=ROOT/'results/baseline_comparison_600_20261017/scenes'
sys.path.insert(0,str(ROOT/'experiment'))
import _common as c

def read(path):
    if str(path).endswith('.gz'):
        with gzip.open(path,'rt') as f:return json.load(f)
    return c.read(path)

def arrays(path):
    with np.load(path,allow_pickle=False) as z:return dict(z)

def main():
    from threadpoolctl import threadpool_limits
    source_files=[]
    for scene in range(10):
        parent=SOURCE/f'scene{scene:03d}'; folder=parent/'snr+00'
        source_files += [parent/n for n in ('READY.json','pairing.npz','truth.npz')]
        source_files += [folder/n for n in ('READY.json','phase.npz')]
        source_files += [folder/(m+s) for m in ('proposed','offgrid_sbl') for s in ('.metrics.json','.compact.npz','.record.json.gz')]
    if not (OUT/'PLAN.json').exists():
        c.save(OUT/'PLAN.json',dict(scenes=list(range(10)),snr_db=0,users=40,frames=16,activity_probability=.1,
            new_inferences=10,new_method='offgrid_sbl_600',reused_methods=['proposed','offgrid_sbl_120'],
            reused_phase=True,selection='First ten existing physical scenes, fixed before supplemental results',
            source_directory=str(SOURCE.relative_to(ROOT)),config='configs/experiments/offgrid_sbl_600.json',
            threshold_status='Original thresholds reused without 600-iteration recalibration',
            timing='New receiver CPU times recorded; historical comparator times came from another run and are not an isolated speed benchmark',
            source_and_weight_sha256=c.identities() | {str(Path(__file__).relative_to(ROOT)):c.sha(__file__)},
            reused_file_sha256={str(p.relative_to(ROOT)):c.sha(p) for p in source_files}))
    plan=c.read(OUT/'PLAN.json');c.verify_sources(plan)
    assert c.sha(__file__)==c.read(OUT/'REPAIR.json')['resume_sha256']
    for p,h in plan['reused_file_sha256'].items():assert c.sha(ROOT/p)==h
    start=time.monotonic();c.save(OUT/'RUN_STATE.json',dict(status='RUNNING',pid=os.getpid()))
    receiver=c.EstimatedNoiseBaselineReceiver('offgrid_sbl',config=ROOT/plan['config'],device='cpu')
    with threadpool_limits(1):
        for scene in plan['scenes']:
            dest=OUT/f'scene{scene:03d}';dest.mkdir(exist_ok=True)
            if (dest/'result.json').exists():
                saved=c.read(dest/'result.json')
                assert saved['status']=='COMPLETE'
                assert c.sha(dest/'prediction.npz')==saved['prediction_sha256']
                continue
            parent=SOURCE/f'scene{scene:03d}';folder=parent/'snr+00'
            base=read(parent/'READY.json');ready=read(folder/'READY.json');pairing=arrays(parent/'pairing.npz')
            assert c.sha(parent/'pairing.npz')==base['pairing_sha256']
            assert c.sha(parent/'truth.npz')==base['truth_sha256']
            variance=base['power']
            inputs=c.UnknownPhaseInput(pairing['clean']+np.sqrt(variance)*pairing['standard_noise'],pairing['pilot'],variance,base['activity_prior'])
            assert {k:c.array_sha256(v) for k,v in inputs.arguments().items()}==ready['public_array_sha256']
            assert c.sha(folder/'phase.npz')==ready['phase_sha256']
            conditional=inputs.at_estimated_phase(arrays(folder/'phase.npz')['phase_slopes'])
            conditional=c.ReceiverInput(conditional.observation,conditional.operator,1.,conditional.activity_prior)
            with warnings.catch_warnings(record=True) as notices:
                warnings.simplefilter('always',RuntimeWarning)
                output,record=receiver.infer(conditional)
            assert record['status']=='COMPLETE' and all(np.isfinite(v).all() for v in output.values())
            # Save successful inference before postprocessing checks.
            c.save_arrays(dest/'prediction.npz',output)
            with gzip.open(dest/'native.json.gz','wt') as f:json.dump(record,f,allow_nan=False)
            truth=arrays(parent/'truth.npz');metrics=c.score_arrays(output,truth)
            reused={m:read(folder/(m+'.metrics.json')) for m in ('proposed','offgrid_sbl')}
            for m,row in reused.items():
                assert row['status']=='COMPLETE' and row['shared_phase_sha256']==ready['phase_sha256']
                assert c.sha(folder/(m+'.compact.npz'))==row['compact_sha256']
                np.testing.assert_allclose(row['metrics']['signal_energy'],metrics['signal_energy'],rtol=8*np.finfo(float).eps,atol=0)
            old_native=read(folder/'offgrid_sbl.record.json.gz');n=old_native['iterations']
            exact=old_native['trace']==record['trace'][:n]
            old=np.asarray([list(r.values()) for r in old_native['trace']],float)
            new=np.asarray([list(r.values()) for r in record['trace'][:n]],float)
            np.testing.assert_allclose(old,new,rtol=1e-12,atol=1e-12)
            c.save_arrays(dest/'prediction.npz',output)
            with gzip.open(dest/'native.json.gz','wt') as f:json.dump(record,f,allow_nan=False)
            c.save(dest/'result.json',dict(status='COMPLETE',scene=scene,seed=base['seed'],snr_db=0,
                metrics=metrics,iterations=record['iterations'],stopping_reason=record['stopping_reason'],
                receiver_seconds=record['seconds'],native_sha256=c.sha(dest/'native.json.gz'),prediction_sha256=c.sha(dest/'prediction.npz'),
                reused=reused,source_folder=str(folder.relative_to(ROOT)),shared_phase_sha256=ready['phase_sha256'],
                original_observation_hashes_exact=True,original_trace_prefix_exact=exact,
                original_trace_prefix_max_absolute_difference=float(np.max(abs(old-new))),
                warning_counts=dict(Counter(str(w.message) for w in notices))))
            print(f'{scene+1}/10: SBL120={reused["offgrid_sbl"]["metrics"]["nmse_db"]:.3f}, SBL600={metrics["nmse_db"]:.3f}, Proposed={reused["proposed"]["metrics"]["nmse_db"]:.3f} dB; iterations={record["iterations"]} {record["stopping_reason"]}',flush=True)
            c.save(OUT/'PROGRESS.json',dict(completed=scene+1,total=10,elapsed_seconds=time.monotonic()-start))
    c.verify_sources(plan)
    for p,h in plan['reused_file_sha256'].items():assert c.sha(ROOT/p)==h
    c.save(OUT/'RUN_STATE.json',dict(status='COMPLETE',new_inferences=10,reused_comparator_results=20,reused_phase_estimates=10,seconds=time.monotonic()-start))

if __name__=='__main__':
    try:main()
    except BaseException:
        c.save(OUT/'RUN_STATE.json',dict(status='FAILED',traceback=traceback.format_exc()));raise
