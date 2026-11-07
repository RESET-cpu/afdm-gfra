"""Bounded CUDA queue on saved known-phase inputs, one process per input."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

import psutil

from project import ROOT
from utils import read_json, write_json, sha256

OUT = ROOT / 'result/snr_comparison/data/white_preconditioned_matched_fp32_1000_snr_20261105'


def checked(path, digest):
    if sha256(path) != digest:
        raise ValueError('Changed asset: ' + str(path))


def verify():
    checked(OUT/'PLAN.json', read_json(OUT/'PLAN_HASH.json')['sha256'])
    plan = read_json(OUT/'PLAN.json')
    for path, digest in plan['assets'].items():
        checked(path, digest)
    return plan


def tag(position):
    return f'scene{position//6:04d}_condition{position%6:02d}'


def status(stage, active, completed, **extra):
    value = dict(stage=stage, pid=os.getpid(), updated_unix=time.time(), completed=completed,
                 planned=6000, active_workers=len(active), workers=[r for _,r in active], **extra)
    for attempt in range(3):
        try:
            write_json(OUT/'STATUS.json', value)
            return
        except PermissionError:
            if attempt == 2:
                print('Advisory status temporarily locked', flush=True)
            time.sleep(.05)


def worker(position, preflight=False):
    import numpy as np
    import torch
    from threadpoolctl import threadpool_limits
    from system.observation import ReceiverInput
    from evaluation.metrics import score_arrays
    from evaluation.storage import save_arrays, arrays as load_arrays
    from .receiver import Receiver
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
    destination = (OUT/'preflight' if preflight else Path(plan['native_directory'])) / tag(position)
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
                   started_unix=began,position=position,preflight=preflight))
        calls = 0
        def observe(row, *args):
            nonlocal calls
            calls += 1
            if calls == 1 or calls % 10 == 0:
                write_json(destination/'WORKER_STATUS.json', dict(stage='INFER',iterations=calls,
                           pid=os.getpid(),updated_unix=time.time(),elapsed_seconds=time.time()-began))
        with threadpool_limits(limits=plan['runtime']['threads_per_worker']):
            receiver = Receiver(plan['configuration'], device='cuda', noise_mode='estimated')
            arrays, record = receiver.infer(inputs, observer=observe)
        assert all(np.isfinite(v).all() for v in arrays.values())
        assert record['iterations'] <= 600 and not record['receiver_truth_used'] and not record['noise_truth_used']
        assert record['oracle_phase_supplied'] and record['configuration'] == plan['receiver_configuration']
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
        if preflight:
            reference = read_json(plan['precision_validation'])[0]
            expected = load_arrays(Path(reference['folder'])/'prediction.npz')
            np.testing.assert_allclose(arrays['estimate'], expected['estimate'], rtol=1e-10, atol=1e-12)
            np.testing.assert_array_equal(arrays['activity_decision'], expected['activity_decision'])
            assert record['iterations'] == reference['iterations']
        assert metrics == score_arrays(arrays, truth)
        result = dict(status='COMPLETE',scene=case['scene'],index=case['index'],snr_db=case['snr_db'],
                      metrics=metrics,iterations=record['iterations'],converged=record['converged'],
                      stopping_reason=record['stopping_reason'],seconds=record['seconds'],
                      process_seconds=time.time()-began,preflight=preflight,input_files=case['files'],
                      phase_mode='known',noise_mode='estimated',channel_activity_truth_used_in_inference=False,
                      oracle_phase_supplied=True,plan_sha256=sha256(OUT/'PLAN.json'),
                      files={str(destination/n):sha256(destination/n) for n in ('prediction.npz','record.json','INPUT_MANIFEST.json')},
                      peak_working_set_bytes=getattr(process.memory_info(),'peak_wset',process.memory_info().rss),
                      peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved(),
                      environment=dict(python=sys.version,numpy=np.__version__,torch=torch.__version__,
                                       cuda=torch.version.cuda,gpu=torch.cuda.get_device_name(0),
                                       threads=plan['runtime']['threads_per_worker'],
                                       tf32=torch.backends.cuda.matmul.allow_tf32,cudnn_tf32=torch.backends.cudnn.allow_tf32,
                                       cudnn_benchmark=torch.backends.cudnn.benchmark))
        write_json(destination/'RESULT.json', result)
        write_json(destination/'WORKER_STATUS.json',dict(stage='SAVED',iterations=record['iterations'],updated_unix=time.time()))
        if not preflight:
            write_json(OUT/'results'/(tag(position)+'.json'),dict(result=str(destination/'RESULT.json'),sha256=sha256(destination/'RESULT.json')))
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


def launch_worker(position, preflight, plan):
    label = ('preflight_' if preflight else '')+tag(position)
    logs = OUT/'logs'; logs.mkdir(exist_ok=True)
    env = dict(os.environ,PYTHONPATH=str(ROOT/'src'),OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2',
               OMP_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2')
    env.pop('CUDA_VISIBLE_DEVICES',None)
    command = [str(ROOT/'.venv/Scripts/python.exe'),'-X','utf8','-B','-m',
               'evaluation.white_matched_fp32_20261105.run','worker','--position',str(position)]
    if preflight: command.append('--preflight')
    stdout, stderr = logs/(label+'.out'), logs/(label+'.err')
    with stdout.open('xb') as out, stderr.open('xb') as err:
        proc = subprocess.Popen(command,cwd=ROOT,env=env,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
    receipt = dict(position=position,preflight=preflight,pid=proc.pid,created_unix=psutil.Process(proc.pid).create_time(),
                   command=command,started_unix=time.time(),stdout=str(stdout),stderr=str(stderr))
    write_json(OUT/'launches'/(label+'.json'),receipt)
    return proc, receipt


def coordinate():
    plan = verify()
    lock = OUT/'RUNNING.lock'
    with lock.open('x',encoding='utf-8') as f:
        import json
        json.dump(dict(pid=os.getpid(),created_unix=psutil.Process().create_time()),f)
    active, completed, failed = [], 0, []
    began = time.time()
    try:
        if (OUT/'START.json').exists():
            raise RuntimeError('Execution already exists; automatic resume/retry forbidden')
        write_json(OUT/'START.json',dict(pid=os.getpid(),started_unix=began,plan_sha256=sha256(OUT/'PLAN.json')))
        while not capacity(plan,[]):
            if (OUT/'STOP.json').exists():
                status('PAUSED',[],0,failed=0); return
            if time.time()-began > plan['runtime']['total_timeout_seconds']:
                raise TimeoutError('Queue exceeded total budget')
            status('WAITING_FOR_MEMORY_PREFLIGHT',[],0,failed=0)
            time.sleep(10)
        proc, receipt = launch_worker(plan['preflight_position'],True,plan)
        active = [(proc,receipt)]
        while proc.poll() is None:
            if time.time()-receipt['started_unix'] > plan['runtime']['input_timeout_seconds']:
                raise TimeoutError('Preflight timeout; process retained for inspection')
            status('PREFLIGHT',active,0,failed=0)
            time.sleep(5)
        active = []
        if proc.returncode != 0:
            raise RuntimeError('Full inference preflight failed; no automatic retry')
        row = read_json(OUT/'preflight'/tag(plan['preflight_position'])/'RESULT.json')
        assert row['status'] == 'COMPLETE'
        assert row['peak_working_set_bytes']/2**30 <= plan['runtime']['worker_peak_budget_gib']
        assert row['peak_cuda_reserved_bytes']/2**30 <= plan['runtime']['gpu_budget_gib_per_worker']
        write_json(OUT/'PREFLIGHT.json',dict(status='PASS',completed_unix=time.time(),position=plan['preflight_position'],
                   finite_full_inference=True,saved_arrays_rescored=True,receiver_controls_unchanged=True,
                   peak_ram_gib=row['peak_working_set_bytes']/2**30,peak_cuda_reserved_gib=row['peak_cuda_reserved_bytes']/2**30,
                   iterations=row['iterations'],result=str(OUT/'preflight'/tag(plan['preflight_position'])/'RESULT.json')))
        cursor = 0
        while cursor < 6000 or active:
            remaining = []
            for proc, receipt in active:
                code = proc.poll()
                if code is None:
                    if time.time()-receipt['started_unix'] > plan['runtime']['input_timeout_seconds']:
                        raise TimeoutError('Input timeout; active process retained for inspection')
                    remaining.append((proc,receipt)); continue
                if code == 0:
                    link = read_json(OUT/'results'/(tag(receipt['position'])+'.json'))
                    checked(link['result'],link['sha256'])
                    assert read_json(link['result'])['status'] == 'COMPLETE'
                    completed += 1
                else:
                    failed.append(dict(receipt,exit_code=code))
            active = remaining
            stopped = (OUT/'STOP.json').exists()
            if time.time()-began > plan['runtime']['total_timeout_seconds']:
                raise TimeoutError('Queue exceeded total budget; active processes retained')
            while not failed and not stopped and cursor < 6000 and len(active) < plan['runtime']['max_workers'] and capacity(plan,active):
                active.append(launch_worker(cursor,False,plan)); cursor += 1
            stage = 'DRAINING_FAILURE' if failed else 'DRAINING_STOP' if stopped else 'RUNNING' if active else 'WAITING_FOR_MEMORY'
            status(stage,active,completed,failed=len(failed),dispatched=cursor)
            if (failed or stopped) and not active:
                if failed: write_json(OUT/'FAILURE.json',dict(status='FAILED',failures=failed,automatic_retry=False))
                status('FAILED' if failed else 'PAUSED',[],completed,failed=len(failed)); return
            if cursor == 6000 and not active: break
            time.sleep(5)
        status('VERIFYING',[],completed,failed=0)
        from .report import summarize
        summarize()
        status('COMPLETE',[],completed,failed=0)
    except Exception:
        write_json(OUT/'FAILURE.json',dict(status='FAILED',traceback=traceback.format_exc(),active_workers=[r for _,r in active],automatic_retry=False))
        status('FAILED',active,completed,failed=max(1,len(failed)))
        raise
    finally:
        lock.unlink(missing_ok=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command',choices=['coordinate','worker'])
    parser.add_argument('--position',type=int)
    parser.add_argument('--preflight',action='store_true')
    args = parser.parse_args()
    if args.command == 'coordinate': coordinate()
    else: worker(args.position,args.preflight)
