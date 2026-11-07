"""Bounded independent inference, saved predictions, and explicit safe resumption."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
import psutil
from project import ROOT
from utils import read_json,write_json,sha256
from .common import OUT,METHODS,checked,verify,tag,check_new


def status(stage, active, completed, **extra):
    value=dict(stage=stage,pid=os.getpid(),updated_unix=time.time(),completed=completed,
               planned=6000,active_workers=len(active),workers=[r for _,r in active],**extra)
    for attempt in range(5):
        try:
            write_json(OUT/'STATUS.json',value);return
        except PermissionError:
            time.sleep(.1)
    print('Advisory status temporarily locked',flush=True)


def worker(position, method, preflight=False):
    import numpy as np
    import torch
    from threadpoolctl import threadpool_limits
    from system.observation import ReceiverInput
    from evaluation.metrics import score_arrays
    from evaluation.storage import save_arrays, arrays as load_arrays
    from .receivers import OriginalSTMP, WhiteGaussianGPMP
    plan = verify()
    torch.set_num_threads(plan['runtime']['threads_per_worker'])
    torch.set_num_interop_threads(1)
    # Match the historical colored evaluation's evaluation.receivers.setup.
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    if not torch.cuda.is_available():
        raise RuntimeError('Authorized CUDA evaluation requires the GPU')
    process = psutil.Process()
    process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    destination = (OUT/'preflight' if preflight else Path(plan['native_directory'])) / method / tag(position)
    destination.mkdir(parents=True, exist_ok=False)
    began = time.time()
    try:
        case = read_json(OUT/'INPUTS.json')[position]
        folder = Path(case['ready']).parent
        checked(case['ready'], case['ready_sha256'])
        for name, digest in case['files'].items():
            checked(folder/name, digest)
        write_json(destination/'INPUT_MANIFEST.json', dict(case=case, plan_sha256=sha256(OUT/'PLAN.json')))
        with np.load(folder/'public.npz', allow_pickle=False) as z:
            inputs = ReceiverInput(z['y'], z['a'], 1.0, float(z['rho']))
        write_json(destination/'START.json', dict(pid=os.getpid(),created_unix=process.create_time(),
                   started_unix=began,position=position,method=method,preflight=preflight))
        calls = 0
        def observe(row, *args):
            nonlocal calls
            calls += 1
            if calls == 1 or calls % 10 == 0:
                write_json(destination/'WORKER_STATUS.json', dict(stage='INFER',iterations=calls,
                           pid=os.getpid(),updated_unix=time.time(),elapsed_seconds=time.time()-began))
        with threadpool_limits(limits=plan['runtime']['threads_per_worker']):
            def forbidden(*args, **kwargs):
                raise AssertionError('Gaussian arm attempted to call a classifier')
            from algorithm.STMP.activity import FrozenEvidence
            FrozenEvidence.infer = forbidden
            FrozenEvidence.__init__ = forbidden
            receiver = (OriginalSTMP if method == 'STMP-Gaussian' else WhiteGaussianGPMP)(plan['configurations'][method], device='cuda')
            assert getattr(receiver, 'evidence', None) is None
            modules = [receiver.model.first, receiver.model.second] if method == 'STMP-Gaussian' else [receiver.model.network]
            assert all(p.dtype == torch.float32 for m in modules for p in m.parameters())
            arrays, record = receiver.infer(inputs, observer=observe)
        assert all(np.isfinite(v).all() for v in arrays.values())
        assert record['iterations'] <= 600 and not record['receiver_truth_used'] and not record['noise_truth_used']
        assert record['oracle_phase_supplied'] and not record['classifier_loaded'] and record['classifier_calls'] == 0
        assert arrays['estimate'].shape == (40,16,16,16) and arrays['probabilities'].shape == (40,)
        assert np.all((arrays['probabilities'] >= 0) & (arrays['probabilities'] <= 1))
        np.testing.assert_array_equal(arrays['activity_decision'], arrays['probabilities'] >= .5)
        assert not torch.backends.cuda.matmul.allow_tf32 and not torch.backends.cudnn.allow_tf32
        assert not torch.backends.cudnn.benchmark
        save_arrays(destination/'prediction.npz', arrays)
        write_json(destination/'record.json', record)
        # Evaluator-only truth access, after inference and prediction saving.
        truth = load_arrays(folder/'truth.npz')
        metrics = score_arrays(load_arrays(destination/'prediction.npz'), truth)
        assert metrics == score_arrays(arrays, truth)
        result = dict(status='COMPLETE',method=method,scene=case['scene'],index=case['index'],snr_db=case['snr_db'],
                      metrics=metrics,iterations=record['iterations'],converged=record['converged'],
                      stopping_reason=record['stopping_reason'],seconds=record['seconds'],
                      process_seconds=time.time()-began,preflight=preflight,input_files=case['files'],
                      phase_mode='known',noise_mode='estimated',channel_activity_truth_used_in_inference=False,
                      oracle_phase_supplied=True,plan_sha256=sha256(OUT/'PLAN.json'),
                      files={str(destination/n):sha256(destination/n) for n in ('prediction.npz','record.json','INPUT_MANIFEST.json')},
                      peak_working_set_bytes=getattr(process.memory_info(),'peak_wset',process.memory_info().rss),
                      peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved(),
                      environment=dict(network_dtype='float32',python=sys.version,numpy=np.__version__,torch=torch.__version__,
                                       cuda=torch.version.cuda,gpu=torch.cuda.get_device_name(0),
                                       threads=plan['runtime']['threads_per_worker'],
                                       tf32=torch.backends.cuda.matmul.allow_tf32,cudnn_tf32=torch.backends.cudnn.allow_tf32,
                                       cudnn_benchmark=torch.backends.cudnn.benchmark))
        write_json(destination/'RESULT.json', result)
        write_json(destination/'WORKER_STATUS.json',dict(stage='SAVED',iterations=record['iterations'],updated_unix=time.time()))
        if not preflight:
            write_json(OUT/'results'/(method+'_'+tag(position)+'.json'),dict(result=str(destination/'RESULT.json'),sha256=sha256(destination/'RESULT.json')))
        print(dict(event='SAVED',position=position,preflight=preflight,iterations=record['iterations']),flush=True)
    except Exception:
        write_json(destination/'FAILURE.json',dict(status='FAILED',traceback=traceback.format_exc(),automatic_retry=False))
        raise


def capacity(plan, active):
    rt = plan['runtime']
    available = psutil.virtual_memory().available/2**30
    reserve = 0.
    for proc, receipt in active:
        try:
            parent = psutil.Process(proc.pid)
            rss = sum(p.memory_info().rss for p in [parent]+parent.children(recursive=True))/2**30
            reserve += max(0.,rt['worker_peak_budget_gib']-rss)
        except psutil.NoSuchProcess:
            pass
    if available-reserve < rt['worker_peak_budget_gib']+rt['minimum_free_ram_gib']:
        return False
    gpu = subprocess.run(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],
                         capture_output=True,text=True,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    free_gpu = float(gpu.stdout.strip().splitlines()[0])/1024
    return free_gpu >= rt['gpu_budget_gib_per_worker']+rt['minimum_free_gpu_gib']


def launch_worker(position, method, preflight, plan):
    label = ('preflight_' if preflight else '')+method+'_'+tag(position)
    logs = OUT/'logs'; logs.mkdir(exist_ok=True)
    env = dict(os.environ,PYTHONPATH=str(ROOT/'src'),OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2',
               OMP_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2')
    env.pop('CUDA_VISIBLE_DEVICES',None)
    command = [str(ROOT/'.venv/Scripts/python.exe'),'-X','utf8','-B','-m',
               'evaluation.activity_evidence_500_20261105.run','worker','--position',str(position),'--method',method]
    if preflight: command.append('--preflight')
    stdout, stderr = logs/(label+'.out'), logs/(label+'.err')
    with stdout.open('xb') as out, stderr.open('xb') as err:
        proc = subprocess.Popen(command,cwd=ROOT,env=env,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
    receipt = dict(position=position,method=method,plan_sha256=sha256(OUT/'PLAN.json'),preflight=preflight,pid=proc.pid,created_unix=psutil.Process(proc.pid).create_time(),
                   command=command,started_unix=time.time(),stdout=str(stdout),stderr=str(stderr))
    write_json(OUT/'launches'/(label+'.json'),receipt)
    return proc, receipt


def coordinate(preflight_only=False):
    plan=verify()
    from .prepare import prerequisites
    prerequisites()
    # Process identity, rather than a PID alone, protects against PID reuse.
    for receipt_path in (OUT/'launches').glob('*.json'):
        receipt=read_json(receipt_path)
        try:
            p=psutil.Process(receipt['pid'])
            if abs(p.create_time()-receipt['created_unix']) < .1:
                raise RuntimeError('Existing inference worker is still alive: '+str(receipt_path))
        except psutil.NoSuchProcess:
            pass
    lock=OUT/'RUNNING.lock'
    if lock.exists():
        previous=read_json(lock)
        try:
            p=psutil.Process(previous['pid'])
            if abs(p.create_time()-previous['created_unix']) < .1:
                raise RuntimeError('Coordinator already alive')
        except psutil.NoSuchProcess:
            pass
        lock.rename(OUT/('RUNNING.stale.'+str(time.time_ns())+'.json'))
    with lock.open('x',encoding='utf-8') as f:
        import json
        json.dump(dict(pid=os.getpid(),created_unix=psutil.Process().create_time()),f)
    active=[];completed=0;failed=[];began=time.time()
    try:
        write_json(OUT/('COORDINATOR_'+str(time.time_ns())+'.json'),dict(pid=os.getpid(),
            created_unix=psutil.Process().create_time(),command=sys.argv,plan_sha256=sha256(OUT/'PLAN.json')))
        if (OUT/'STOP.json').exists():
            status('PAUSED',[],0);return
        preflight_rows=[]
        for method in METHODS:
            dest=OUT/'preflight'/method/tag(0)
            if dest.exists():
                row=check_new(method,0,plan,preflight=True)
            else:
                while not capacity(plan,[]):
                    status('WAITING_FOR_MEMORY_PREFLIGHT',[],0)
                    if time.time()-began>plan['runtime']['total_timeout_seconds']: raise TimeoutError('Memory wait')
                    if (OUT/'STOP.json').exists(): status('PAUSED',[],0);return
                    time.sleep(5)
                proc,receipt=launch_worker(0,method,True,plan);active=[(proc,receipt)]
                while proc.poll() is None:
                    status('PREFLIGHT',active,0)
                    if time.time()-receipt['started_unix']>plan['runtime']['input_timeout_seconds']:
                        raise TimeoutError('Preflight timeout; process preserved')
                    time.sleep(5)
                active=[]
                if proc.returncode: raise RuntimeError('Preflight failed: '+method)
                row=check_new(method,0,plan,preflight=True)
            assert row['peak_working_set_bytes']/2**30 <= plan['runtime']['worker_peak_budget_gib']
            assert row['peak_cuda_reserved_bytes']/2**30 <= plan['runtime']['gpu_budget_gib_per_worker']
            preflight_rows.append(row)
        write_json(OUT/'PREFLIGHT.json',dict(status='PASS',rows=preflight_rows,checked_unix=time.time(),
            classifier_calls=0,saved_arrays_rescored=True,actual_controls_preserved=True))
        if preflight_only:
            status('READY',[],0);return
        pending=[]
        # An existing incomplete destination is a failure to inspect, never silently overwritten.
        for position in range(3000):
            for method in METHODS:
                dest=Path(plan['native_directory'])/method/tag(position)
                if dest.exists():
                    check_new(method,position,plan);completed+=1
                else:
                    pending.append((position,method))
        cursor=0
        while cursor<len(pending) or active:
            remaining=[]
            for proc,receipt in active:
                code=proc.poll()
                if code is None:
                    if time.time()-receipt['started_unix']>plan['runtime']['input_timeout_seconds']:
                        raise TimeoutError('Input timeout; process preserved')
                    remaining.append((proc,receipt));continue
                if code==0:
                    check_new(receipt['method'],receipt['position'],plan);completed+=1
                else: failed.append(dict(receipt,exit_code=code))
            active=remaining
            stopped=(OUT/'STOP.json').exists()
            while not failed and not stopped and cursor<len(pending) and len(active)<plan['runtime']['max_workers'] and capacity(plan,active):
                position,method=pending[cursor]
                active.append(launch_worker(position,method,False,plan));cursor+=1
            status('DRAINING_FAILURE' if failed else 'DRAINING_STOP' if stopped else 'RUNNING' if active else 'WAITING_FOR_MEMORY',
                   active,completed,failed=len(failed))
            if (failed or stopped) and not active:
                if failed: write_json(OUT/'FAILURE.json',dict(status='FAILED',failures=failed,automatic_retry=False))
                status('FAILED' if failed else 'PAUSED',[],completed,failed=len(failed));return
            if time.time()-began>plan['runtime']['total_timeout_seconds']:
                raise TimeoutError('Queue timeout; processes preserved')
            if cursor==len(pending) and not active: break
            time.sleep(5)
        assert completed==6000
        status('VERIFYING',[],completed)
        from .report import summarize
        summarize()
        status('COMPLETE',[],completed)
    except Exception:
        write_json(OUT/'FAILURE.json',dict(status='FAILED',traceback=traceback.format_exc(),
            active_workers=[r for _,r in active],automatic_retry=False))
        status('FAILED',active,completed);raise
    finally:
        lock.unlink(missing_ok=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['coordinate','worker'])
    parser.add_argument('--position',type=int)
    parser.add_argument('--method',choices=METHODS)
    parser.add_argument('--preflight',action='store_true')
    parser.add_argument('--preflight-only',action='store_true')
    args=parser.parse_args()
    if args.command=='coordinate': coordinate(args.preflight_only)
    else:
        assert args.position is not None and 0<=args.position<3000 and args.method in METHODS
        worker(args.position,args.method,args.preflight)

