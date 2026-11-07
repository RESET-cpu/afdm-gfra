"""Two-worker queue; both predecessor completion gates apply before CUDA use."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
import psutil
from .common import (ROOT, OUT, tag, checked, verify, require_ready, live_processes,
                     check_phase_record, validate_result)
from utils import read_json, write_json, sha256
from evaluation.white_matched_fp32_20261105.run import capacity


def status(stage, active, completed, **extra):
    value = dict(stage=stage, pid=os.getpid(), updated_unix=time.time(), planned=6000,
                 completed=completed, active_workers=len(active), workers=[r for _,r in active], **extra)
    for attempt in range(3):
        try:
            write_json(OUT/'STATUS.json', value)
            return
        except PermissionError:
            time.sleep(.05)
    print('Advisory status temporarily locked', flush=True)


def worker(position, preflight=False):
    require_ready()  # Before torch import, model loading, or device checks.
    plan = verify(full=False)
    import numpy as np
    import torch
    from threadpoolctl import threadpool_limits
    from evaluation.storage import arrays as load_arrays, save_arrays
    from evaluation.metrics import score_arrays
    from system.receiver.unknown_phase import UnknownPhaseInput
    from .receiver import Receiver
    torch.set_num_threads(plan['runtime']['threads_per_worker'])
    torch.set_num_interop_threads(1)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA is required; no device substitution')
    process = psutil.Process()
    process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    folder = (OUT/'preflight' if preflight else Path(plan['native_directory']))/tag(position)
    folder.mkdir(parents=True, exist_ok=False)
    began = time.time()
    try:
        case = read_json(OUT/'INPUTS.json')[position]
        source = Path(case['ready']).parent
        checked(case['ready'], case['ready_sha256'])
        for name, digest in case['files'].items():
            checked(source/name, digest)
        write_json(folder/'INPUT_MANIFEST.json', dict(case=case, plan_sha256=sha256(OUT/'PLAN.json')))
        write_json(folder/'START.json', dict(pid=os.getpid(), created_unix=process.create_time(),
                                            started_unix=began, position=position, preflight=preflight))
        raw = load_arrays(source/'raw.npz')
        inputs = UnknownPhaseInput(raw['y'], raw['pilot'], 1.0, float(raw['rho']))
        last = [0.]
        def publish(stage, **values):
            if time.monotonic()-last[0] >= 10:
                write_json(folder/'WORKER_STATUS.json', dict(stage=stage, pid=os.getpid(),
                           updated_unix=time.time(), elapsed_seconds=time.time()-began, **values))
                last[0] = time.monotonic()
        with threadpool_limits(limits=plan['runtime']['threads_per_worker']):
            receiver = Receiver(plan['configuration'], device='cuda', noise_mode='estimated')
            prediction, record = receiver.infer(inputs,
                observer=lambda row,*args: publish('CONDITIONAL_RECEIVER', iteration=row['iteration']),
                phase_observer=lambda row: publish('PHASE_FRONTEND', sweep=row['sweep']))
        check_phase_record(record, prediction, configuration=plan['receiver_configuration'], binding=plan['frontend_binding'])
        assert all(np.isfinite(v).all() for v in prediction.values())
        assert 1 <= record['iterations'] <= 600
        assert all(p.dtype == torch.float32 for model in (receiver.model.network, receiver.evidence.network)
                   for p in model.parameters())
        save_arrays(folder/'prediction.npz', prediction)
        write_json(folder/'record.json', record)
        # Truth is only parsed after prediction and inference record are saved.
        metrics = score_arrays(load_arrays(folder/'prediction.npz'), load_arrays(source/'truth.npz'))
        row = dict(status='COMPLETE', scene=case['scene'], index=case['index'], snr_db=case['snr_db'],
            metrics=metrics, iterations=record['iterations'], converged=record['converged'],
            stopping_reason=record['stopping_reason'], seconds=record['seconds'],
            frontend_seconds=record['phase_initialization']['seconds'], process_seconds=time.time()-began,
            preflight=preflight, input_files=case['files'], phase_mode='estimated', noise_mode='estimated',
            channel_activity_truth_used_in_inference=False, oracle_phase_supplied=False,
            plan_sha256=sha256(OUT/'PLAN.json'),
            files={str(folder/n):sha256(folder/n) for n in ('prediction.npz','record.json','INPUT_MANIFEST.json')},
            peak_working_set_bytes=getattr(process.memory_info(), 'peak_wset', process.memory_info().rss),
            peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved(),
            environment=dict(network_dtype='float32', python=sys.version, numpy=np.__version__,
                torch=torch.__version__, cuda=torch.version.cuda, gpu=torch.cuda.get_device_name(0),
                threads=plan['runtime']['threads_per_worker'], tf32=torch.backends.cuda.matmul.allow_tf32,
                cudnn_tf32=torch.backends.cudnn.allow_tf32, cudnn_benchmark=torch.backends.cudnn.benchmark))
        write_json(folder/'RESULT.json', row)
        if not preflight:
            write_json(OUT/'results'/(tag(position)+'.json'), dict(result=str(folder/'RESULT.json'),
                       sha256=sha256(folder/'RESULT.json')))
        print(dict(event='SAVED', position=position, preflight=preflight, iterations=record['iterations']), flush=True)
    except Exception:
        write_json(folder/'FAILURE.json', dict(status='FAILED', traceback=traceback.format_exc(), automatic_retry=False))
        raise


def launch_worker(position, preflight):
    label = ('preflight_' if preflight else '') + tag(position)
    env = dict(os.environ, PYTHONPATH=str(ROOT/'src'), OMP_NUM_THREADS='2', MKL_NUM_THREADS='2',
               OPENBLAS_NUM_THREADS='2', NUMEXPR_NUM_THREADS='2')
    env.pop('CUDA_VISIBLE_DEVICES', None)
    command = [str(ROOT/'.venv/Scripts/python.exe'), '-X', 'utf8', '-B', '-m',
               'evaluation.white_phase_frontend_20261106.run', 'worker', '--position', str(position)]
    if preflight:
        command.append('--preflight')
    stdout, stderr = OUT/'logs'/(label+'.out'), OUT/'logs'/(label+'.err')
    with stdout.open('xb') as out, stderr.open('xb') as err:
        proc = subprocess.Popen(command, cwd=ROOT, env=env, stdout=out, stderr=err,
                                creationflags=subprocess.CREATE_NO_WINDOW)
    receipt = dict(position=position, preflight=preflight, pid=proc.pid,
        created_unix=psutil.Process(proc.pid).create_time(), started_unix=time.time(), command=command,
        stdout=str(stdout), stderr=str(stderr))
    write_json(OUT/'launches'/(label+'.json'), receipt)
    return proc, receipt


def coordinate(resume=False):
    gates = require_ready()
    plan = verify()
    if (OUT/'STOP.json').exists() or (OUT/'FAILURE.json').exists():
        raise RuntimeError('Stop/failure record exists; do not automatically retry')
    own = psutil.Process()
    ancestors = {p.pid for p in own.parents()} | {own.pid}
    others = [p for p in live_processes(('evaluation.white_phase_frontend_20261106.run',)) if p['pid'] not in ancestors]
    if others:
        raise RuntimeError('Existing estimated-phase execution: ' + str(others))
    if (OUT/'COMPLETION.json').exists():
        complete = read_json(OUT/'COMPLETION.json')
        assert complete['status'] == 'PASS'
        checked(OUT/'SUMMARY.json', complete['summary_sha256'])
        return
    if (OUT/'START.json').exists() and not resume:
        raise RuntimeError('Use --resume after inspecting the existing execution')
    lock = OUT/'RUNNING.lock'
    with lock.open('x', encoding='utf-8') as f:
        import json
        json.dump(dict(pid=own.pid, created_unix=own.create_time()), f)
    active, completed, failed = [], set(), []
    began = read_json(OUT/'START.json')['started_unix'] if resume else time.time()
    try:
        write_json(OUT/'DEPENDENCIES.json', gates)
        if not resume:
            write_json(OUT/'START.json', dict(pid=own.pid, created_unix=own.create_time(), started_unix=began,
                                             plan_sha256=sha256(OUT/'PLAN.json')))
        else:
            write_json(OUT/f'RESUME_{time.time_ns()}.json', dict(pid=own.pid, created_unix=own.create_time()))
        native = Path(plan['native_directory']); native.mkdir(exist_ok=True)
        for position in range(6000):
            folder = native/tag(position)
            pointer = OUT/'results'/(tag(position)+'.json')
            if pointer.exists():
                link = read_json(pointer)
                assert Path(link['result']) == folder/'RESULT.json'
                checked(link['result'], link['sha256'])
                validate_result(position, plan)
                completed.add(position)
            elif folder.exists():
                if not (folder/'RESULT.json').exists() or (folder/'FAILURE.json').exists():
                    raise RuntimeError('Incomplete input retained for inspection: ' + str(folder))
                validate_result(position, plan)
                write_json(pointer, dict(result=str(folder/'RESULT.json'), sha256=sha256(folder/'RESULT.json')))
                completed.add(position)
        preflight_position = plan['preflight_position']
        if not (OUT/'PREFLIGHT.json').exists():
            if not (OUT/'preflight'/tag(preflight_position)/'RESULT.json').exists():
                while not capacity(plan, []):
                    if (OUT/'STOP.json').exists():
                        status('PAUSED', [], len(completed), failed=0); return
                    if time.time()-began > plan['runtime']['total_timeout_seconds']:
                        raise TimeoutError('Total execution budget exceeded')
                    status('WAITING_FOR_MEMORY_PREFLIGHT', [], len(completed), failed=0); time.sleep(10)
                proc, receipt = launch_worker(preflight_position, True); active = [(proc, receipt)]
                while proc.poll() is None:
                    if time.time()-receipt['started_unix'] > plan['runtime']['input_timeout_seconds']:
                        raise TimeoutError('Preflight timed out; process retained')
                    status('PREFLIGHT', active, len(completed), failed=0); time.sleep(5)
                active = []
                if proc.returncode != 0:
                    raise RuntimeError('Preflight failed; no automatic retry')
            from .report import validate_preflight
            validate_preflight(plan)
        else:
            assert read_json(OUT/'PREFLIGHT.json')['status'] == 'PASS'
        pending = [i for i in range(6000) if i not in completed]
        cursor = 0
        while cursor < len(pending) or active:
            remaining = []
            for proc, receipt in active:
                code = proc.poll()
                if code is None:
                    if time.time()-receipt['started_unix'] > plan['runtime']['input_timeout_seconds']:
                        raise TimeoutError('Worker timed out; process retained')
                    remaining.append((proc, receipt))
                elif code:
                    failed.append(dict(receipt, exit_code=code))
                else:
                    link = read_json(OUT/'results'/(tag(receipt['position'])+'.json'))
                    checked(link['result'], link['sha256'])
                    assert read_json(link['result'])['status'] == 'COMPLETE'
                    completed.add(receipt['position'])
            active = remaining
            stopped = (OUT/'STOP.json').exists()
            if time.time()-began > plan['runtime']['total_timeout_seconds']:
                raise TimeoutError('Total execution budget exceeded; active processes retained')
            while (not failed and not stopped and cursor < len(pending) and
                   len(active) < plan['runtime']['max_workers'] and capacity(plan, active)):
                active.append(launch_worker(pending[cursor], False)); cursor += 1
            if (failed or stopped) and not active:
                if failed:
                    write_json(OUT/'FAILURE.json', dict(status='FAILED', failures=failed, automatic_retry=False))
                status('FAILED' if failed else 'PAUSED', [], len(completed), failed=len(failed)); return
            if cursor == len(pending) and not active:
                break
            status('DRAINING_FAILURE' if failed else 'DRAINING_STOP' if stopped else
                   'RUNNING' if active else 'WAITING_FOR_MEMORY', active, len(completed), failed=len(failed))
            time.sleep(5)
        status('VERIFYING', [], len(completed), failed=0)
        from .report import summarize
        summarize()
        status('COMPLETE', [], len(completed), failed=0)
    except Exception:
        write_json(OUT/'FAILURE.json', dict(status='FAILED', traceback=traceback.format_exc(),
                   active_workers=[r for _,r in active], automatic_retry=False))
        status('FAILED', active, len(completed), failed=max(1, len(failed)))
        raise
    finally:
        lock.unlink(missing_ok=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['coordinate', 'worker', 'inspect'])
    parser.add_argument('--position', type=int)
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    if args.command == 'inspect':
        from .common import dependencies
        print(dependencies())
    elif args.command == 'coordinate':
        coordinate(args.resume)
    else:
        if args.position is None:
            parser.error('--position is required for worker')
        worker(args.position, args.preflight)
