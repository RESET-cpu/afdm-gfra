"""Bounded paired evaluation of frozen weights; no training or parameter search."""
from pathlib import Path
from copy import deepcopy
import argparse
import os
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp
import numpy as np
import torch
from threadpoolctl import threadpool_limits
from project import ROOT
from utils import read_json, write_json, sha256
from evaluation.metrics import score_arrays
from system.observation import ReceiverInput

OUT = ROOT/'result/snr_comparison/data/c_stmp_reuse_20261025'
FIG = ROOT/'result/snr_comparison/figures/c_stmp_reuse_20261025'
PHOTO = ROOT/'result/snr_comparison/data/c_stmp_second_20261025_scene0200_snr0'
MODELS = {}


def verify(paths):
    for p, digest in paths.items():
        assert sha256(ROOT/p) == digest, p


def prepare():
    assert not (OUT/'PLAN.json').exists(), 'Existing plan must not be overwritten'
    paused = read_json(ROOT/'result/snr_comparison/data/c_stmp_column_50000_20261025/STATUS.json')
    assert paused['stage']=='STOPPED_BY_USER'
    old = read_json(ROOT/'result/snr_comparison/data/c_stmp_query_repair_20261025/PLAN.json')
    photo = read_json(PHOTO/'PLAN.json')
    cfg = read_json(ROOT/'src/configs/training/column_messages_20261025.json')
    candidate = deepcopy(cfg['receiver'])
    candidate.update(scale=cfg['scale'], first_checkpoint=old['configuration']['first_checkpoint'],
        first_sha256=old['configuration']['first_checkpoint_sha256'],
        activity_checkpoint=old['configuration']['evidence_checkpoint'],
        activity_sha256=old['configuration']['evidence_checkpoint_sha256'])
    # Only fields actually consumed by this independent matrix receiver.
    for unused in ('covariance_mode','activity_stopping_reference','activity_weight_residual_tolerance'):
        candidate['ep'].pop(unused, None)
    photo_candidate = deepcopy(candidate)
    photo_candidate.update(activity_checkpoint=photo['configurations']['derivative']['evidence_checkpoint'],
                           activity_sha256=photo['configurations']['derivative']['evidence_checkpoint_sha256'])
    configurations = dict(matrix_latest=candidate, matrix_photo=photo_candidate,
                          scalar_photo=photo['configurations']['derivative'], scalar_latest=old['configuration'])
    pin = photo['input']; ready=Path(pin['input'])
    assert sha256(ready)==pin['input_sha256']
    case = dict(scene=200,index=2,snr_db=0,ready=str(ready),ready_sha256=sha256(ready),
                files=read_json(ready)['files'],panel='photo')
    tasks = [dict(case=case,method=method,key='photo_'+method) for method in configurations]
    for c in old['development_cases']:
        c = dict(c,panel='errors')
        tasks.append(dict(case=c,method='matrix_latest',key=f'errors_scene{c["scene"]:04d}_condition{c["index"]:02d}'))
    protected = dict(old['protected'])
    protected.update({str(p.relative_to(ROOT)):sha256(p) for p in PHOTO.glob('*') if p.is_file()})
    protected.update({str(p.relative_to(ROOT)):sha256(p) for p in (ROOT/'src/training/column_messages_20261025').glob('*.py')})
    for p in (ROOT/'src/algorithm/C_STMP_column_20261025').glob('*.py'):
        protected[str(p.relative_to(ROOT))]=sha256(p)
    for method,c in configurations.items():
        for key in ('first_checkpoint','activity_checkpoint','evidence_checkpoint'):
            if key in c: protected[c[key]]=sha256(ROOT/c[key])
    pause_root = ROOT/'result/snr_comparison/data/c_stmp_column_50000_20261025'
    for name in ('STATUS.json','STOP.json','SPECIFICATION.json','first/last.pt','first/best.pt'):
        p=pause_root/name; protected[str(p.relative_to(ROOT))]=sha256(p)
    for task in tasks:
        c=task['case'];assert sha256(c['ready'])==c['ready_sha256']
        for name,digest in c['files'].items():assert sha256(Path(c['ready']).parent/name)==digest
    sources={str(p.relative_to(ROOT)):sha256(p) for p in Path(__file__).parent.glob('*.py')}
    sources['src/tests/test_c_stmp_reuse_20261025.py']=sha256(ROOT/'src/tests/test_c_stmp_reuse_20261025.py')
    plan=dict(configurations=configurations,tasks=tasks,protected=protected,source_sha256=sources,
        created_unix=time.time(),pause=paused,unit_tests='5 passed',workers=3,
        scope='Scene200 0dB: both already-trained classifiers, paired scalar/matrix. All 10 known error inputs: latest already-trained classifier, matrix vs saved scalar. No training, threshold fitting, full-SNR resume or weight replacement.',
        caveats=['First adapter preserves the trained denoiser function for identical r,C.',
                 'Activity matrix features preserve the old scalar limit but general-C calibration is not established.',
                 'Matrix receiver changes Gaussian messages and feedback; four derivative probes versus one in historical scalar receiver.',
                 'Known error inputs are retrospectively selected, not a population AER estimate.',
                 'Retain all failures and nonconvergence. Concurrent wall times are not compared with old timings.'])
    OUT.mkdir(parents=True,exist_ok=True)
    write_json(OUT/'PLAN.json',plan)
    write_json(ROOT/'src/configs/candidates/C_STMP_reuse_20261025.json',candidate)
    verify(protected)
    write_json(OUT/'STATUS.json',dict(status='PREPARED',planned=len(tasks),completed=0))
    print('Prepared',len(tasks),'paired runs; training remains stopped',flush=True)


def worker(task, configuration):
    from evaluation.receivers import setup
    from algorithm.C_STMP_reuse_20261025.receiver import Receiver
    from algorithm.C_STMP.receiver import Receiver as ScalarPhoto
    from algorithm.C_STMP_retrained.receiver import Receiver as ScalarLatest
    if not MODELS:
        setup('cuda');torch.set_num_threads(2)
    method=task['method'];key=task['key'];case=task['case']
    output=OUT/key
    assert not output.with_suffix('.json').exists(), 'Do not overwrite or automatically retry'
    try:
        with threadpool_limits(2):
            if method not in MODELS:
                klass = Receiver if method.startswith('matrix') else ScalarPhoto if method=='scalar_photo' else ScalarLatest
                MODELS[method]=klass(configuration,device='cuda')
            model=MODELS[method]
            ready=Path(case['ready']);assert sha256(ready)==case['ready_sha256']
            for name,digest in case['files'].items():assert sha256(ready.parent/name)==digest
            with np.load(ready.parent/'public.npz') as z:
                inputs=ReceiverInput(z['y'],z['a'],float(z['noise_variance']),float(z['rho']))
            # Truth is held only by the evaluation observer, never passed to infer.
            with np.load(ready.parent/'truth.npz') as z:truth=dict(z)
            active=truth['activity'].astype(bool);h=truth['channel'];signal=float(np.sum(abs(h)**2))
            trace=[];errors=[];probabilities=[]
            def observe(row,state,prob=None,*unused):
                if method.startswith('matrix'):
                    mean=state.reshape(len(state),16,16,16).transpose(0,2,3,1)
                    p=prob.copy()
                else:
                    mean=state.mean;p=state.activity.copy()
                err=np.sum(abs(mean*configuration['scale']-h)**2,axis=(1,2,3))
                d=p>=configuration['decision_threshold']
                metrics=dict(iteration=row['iteration'],nmse_db=float(10*np.log10(max(err.sum()/signal,1e-300))),
                    aer=float(np.mean(d!=active)),misses=int(np.sum(active & ~d)),false_alarms=int(np.sum(~active & d)))
                trace.append(metrics);errors.append(err);probabilities.append(p)
                if row['iteration']==1 or row['iteration']%25==0:
                    write_json(OUT/(key+'.progress.json'),dict(status='RUNNING',pid=os.getpid(),updated=time.time(),**metrics))
            arrays,record=model.infer(inputs,observer=observe)
            assert all(np.isfinite(a).all() for a in arrays.values())
            assert len(trace)==record['iterations']
            np.testing.assert_array_equal(probabilities[-1],arrays['probabilities'])
            np.savez_compressed(output.with_suffix('.npz'),**arrays,per_user_error=np.asarray(errors),
                probability_trace=np.asarray(probabilities),truth_activity=active,signal_energy=signal)
            write_json(OUT/(key+'.record.json'),record)
            with np.load(output.with_suffix('.npz')) as z:metrics=score_arrays(dict(z),truth)
            assert abs(metrics['nmse_db']-trace[-1]['nmse_db'])<1e-10
            assert metrics['misses']==trace[-1]['misses'] and metrics['false_alarms']==trace[-1]['false_alarms']
            replay=None
            if key=='photo_scalar_photo':
                old=read_json(PHOTO/'derivative.json')
                with np.load(PHOTO/'derivative.npz') as z:
                    assert len(trace)==len(old['trace'])
                    pdiff=float(np.max(abs(np.asarray(probabilities)-z['probability_trace'])))
                    ndiff=float(np.max(abs(np.asarray([r['nmse_db'] for r in trace])-np.asarray([r['nmse_db'] for r in old['trace']]))))
                    decisions_exact=bool(np.array_equal(np.asarray(probabilities)>=.5,z['probability_trace']>=.5))
                replay=dict(probability_max_difference=pdiff,nmse_db_max_difference=ndiff,decisions_exact=decisions_exact)
                assert pdiff<1e-5 and ndiff<1e-4 and decisions_exact,replay
            result=dict(status='COMPLETE',task=task,metrics=metrics,trace=trace,iterations=record['iterations'],
                stopping_reason=record['stopping_reason'],converged=record['stopping_reason']=='CONVERGED',
                output_sha256=sha256(output.with_suffix('.npz')),record_sha256=sha256(OUT/(key+'.record.json')),replay=replay,
                first_calls=record.get('first_calls',record.get('first_score_calls')))
            write_json(output.with_suffix('.json'),result)
            write_json(OUT/(key+'.progress.json'),dict(status='COMPLETE',**trace[-1]))
            return result
    except BaseException:
        failed=dict(status='FAILED',task=task,traceback=traceback.format_exc())
        write_json(OUT/(key+'.FAILED.json'),failed)
        return failed


def run():
    plan=read_json(OUT/'PLAN.json');verify(plan['protected']);verify(plan['source_sha256'])
    assert not (OUT/'RUN_STARTED.json').exists(), 'Inspect previous run; no automatic retry'
    write_json(OUT/'RUN_STARTED.json',dict(pid=os.getpid(),time=time.time(),plan_sha256=sha256(OUT/'PLAN.json')))
    completed=[]
    with ProcessPoolExecutor(max_workers=plan['workers'],mp_context=mp.get_context('spawn')) as pool:
        futures=[pool.submit(worker,t,plan['configurations'][t['method']]) for t in plan['tasks']]
        for future in as_completed(futures):
            result=future.result();completed.append(result)
            write_json(OUT/'STATUS.json',dict(status='RUNNING',pid=os.getpid(),completed=len(completed),planned=len(futures),
                failures=sum(r['status']!='COMPLETE' for r in completed),last=result['task']['key']))
            print(result['task']['key'],result['status'],result.get('metrics',{}).get('nmse_db'),result.get('iterations'),flush=True)
    verify(plan['protected']);verify(plan['source_sha256'])
    write_json(OUT/'INFERENCE_COMPLETE.json',dict(tasks=len(completed),failures=sum(r['status']!='COMPLETE' for r in completed),
        plan_sha256=sha256(OUT/'PLAN.json'),protected_assets=len(plan['protected'])))
    write_json(OUT/'STATUS.json',dict(status='INFERENCE_COMPLETE',completed=len(completed),planned=len(completed)))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['prepare','run']);args=parser.parse_args()
    try:
        prepare() if args.command=='prepare' else run()
    except BaseException:
        OUT.mkdir(parents=True,exist_ok=True)
        write_json(OUT/'FAILURE.json',dict(error=traceback.format_exc()))
        raise
