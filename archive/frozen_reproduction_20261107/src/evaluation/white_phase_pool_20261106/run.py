"""Reuse loaded models; keep the frozen inference and saved-result protocol."""
import argparse
import gc
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
from unittest.mock import patch

import psutil
from evaluation.white_phase_adopted100_20261106 import gate as g
from evaluation.white_phase_frontend_20261106 import common
from evaluation.white_matched_fp32_20261105.run import capacity

ROOT, OUT = g.ROOT, g.OUT
REV = OUT / 'runtime_pool_20261106'
MODULE = 'evaluation.white_phase_pool_20261106.run'
TOKENS = (MODULE, 'evaluation.white_phase_adopted100_20261106.run',
          'evaluation.white_phase_frontend_20261106.run')


def verify():
    amendment = g.read_json(REV / 'AMENDMENT.json')
    g.checked(OUT / 'PLAN.json', amendment['original_plan_sha256'])
    g.checked(REV / 'REQUEST.json', amendment['request_sha256'])
    for file, digest in amendment['assets'].items():
        g.checked(file, digest)
    return g.verify(full=False)


def no_other_execution():
    own = psutil.Process()
    excluded = {own.pid} | {p.pid for p in own.parents()}
    others = [p for p in g.live_processes(TOKENS) if p['pid'] not in excluded]
    if others:
        raise RuntimeError('Existing estimated-phase process: ' + str(others))


def initialize(plan):
    import torch
    from evaluation.white_phase_frontend_20261106.receiver import Receiver
    torch.set_num_threads(plan['runtime']['threads_per_worker'])
    torch.set_num_interop_threads(1)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA required')
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    return Receiver(plan['configuration'], device='cuda', noise_mode='estimated')


def execute_case(receiver, plan, case, folder, *, validation=False, session=None):
    import numpy as np
    import torch
    from threadpoolctl import threadpool_limits
    from evaluation.storage import arrays, save_arrays
    from evaluation.metrics import score_arrays
    from system.receiver.unknown_phase import UnknownPhaseInput
    position = case['scene'] * 6 + case['index']
    pointer = OUT / 'results' / (g.tag(position) + '.json')
    if not validation and pointer.exists():
        raise RuntimeError('Refusing to rerun an existing result')
    folder.mkdir(parents=True, exist_ok=False)
    began = time.time()
    process = psutil.Process()
    try:
        source = Path(case['ready']).parent
        g.checked(case['ready'], case['ready_sha256'])
        for name, digest in case['files'].items():
            g.checked(source / name, digest)
        plan_hash = g.sha256(OUT / 'PLAN.json')
        g.write_json(folder / 'INPUT_MANIFEST.json', dict(case=case, plan_sha256=plan_hash))
        g.write_json(folder / 'START.json', dict(pid=process.pid, created_unix=process.create_time(),
            started_unix=began, position=position, preflight=validation, execution_session=session))
        raw = arrays(source / 'raw.npz')
        inputs = UnknownPhaseInput(raw['y'], raw['pilot'], 1.0, float(raw['rho']))
        # The frozen infer creates a new Denoiser/linear state and resets probes.
        # Reset diagnostic counters too, preserving the per-input record semantics.
        receiver.last_trace, receiver.denoiser = [], None
        receiver.model.samples = receiver.model.first_calls = receiver.model.second_calls = 0
        receiver.model.network_samples = 0
        receiver.model.last = {}
        last = [0.]

        def publish(stage, **values):
            if time.monotonic() - last[0] >= 10:
                g.write_json(folder / 'WORKER_STATUS.json', dict(stage=stage, pid=process.pid,
                    updated_unix=time.time(), elapsed_seconds=time.time()-began, **values))
                last[0] = time.monotonic()

        with threadpool_limits(limits=plan['runtime']['threads_per_worker']):
            prediction, record = receiver.infer(inputs,
                observer=lambda row, *args: publish('CONDITIONAL_RECEIVER', iteration=row['iteration']),
                phase_observer=lambda row: publish('PHASE_FRONTEND', sweep=row['sweep']))
        g.check_phase_record(record, prediction, configuration=plan['receiver_configuration'],
                             binding=plan['frontend_binding'])
        assert all(np.isfinite(v).all() for v in prediction.values())
        assert 1 <= record['iterations'] <= 600
        assert all(p.dtype == torch.float32 for m in (receiver.model.network, receiver.evidence.network)
                   for p in m.parameters())
        save_arrays(folder / 'prediction.npz', prediction)
        g.write_json(folder / 'record.json', record)
        # Truth remains inaccessible to inference and is opened only after saving.
        metrics = score_arrays(arrays(folder / 'prediction.npz'), arrays(source / 'truth.npz'))
        row = dict(status='COMPLETE', scene=case['scene'], index=case['index'], snr_db=case['snr_db'],
            metrics=metrics, iterations=record['iterations'], converged=record['converged'],
            stopping_reason=record['stopping_reason'], seconds=record['seconds'],
            frontend_seconds=record['phase_initialization']['seconds'], process_seconds=time.time()-began,
            preflight=validation, input_files=case['files'], phase_mode='estimated', noise_mode='estimated',
            channel_activity_truth_used_in_inference=False, oracle_phase_supplied=False,
            plan_sha256=plan_hash,
            files={str(folder/n):g.sha256(folder/n) for n in ('prediction.npz','record.json','INPUT_MANIFEST.json')},
            peak_working_set_bytes=getattr(process.memory_info(), 'peak_wset', process.memory_info().rss),
            peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved(),
            environment=dict(network_dtype='float32', python=sys.version, numpy=np.__version__,
                torch=torch.__version__, cuda=torch.version.cuda, gpu=torch.cuda.get_device_name(0),
                threads=plan['runtime']['threads_per_worker'], tf32=torch.backends.cuda.matmul.allow_tf32,
                cudnn_tf32=torch.backends.cudnn.allow_tf32, cudnn_benchmark=torch.backends.cudnn.benchmark),
            execution=dict(module=MODULE, persistent_models=True, session=session,
                           amendment_sha256=g.sha256(REV/'AMENDMENT.json')))
        g.write_json(folder/'RESULT.json', row)
        if not validation:
            g.write_json(pointer, dict(result=str(folder/'RESULT.json'), sha256=g.sha256(folder/'RESULT.json')))
        return row
    except Exception:
        g.write_json(folder/'FAILURE.json', dict(status='FAILED', traceback=traceback.format_exc(),
                                               automatic_retry=False))
        raise
    finally:
        receiver.last_trace, receiver.denoiser = [], None
        gc.collect()


def validate():
    g.require_ready()
    plan = verify()
    no_other_execution()
    if (OUT/'FAILURE.json').exists():
        raise RuntimeError('Unresolved batch failure')
    from evaluation.storage import arrays
    from evaluation.metrics import score_arrays
    from evaluation.white_matched_fp32_20261105.report import check_metrics
    from utils import state_sha
    import numpy as np
    cases = g.read_json(OUT/'INPUTS.json')
    existing = []
    for pointer in sorted((OUT/'results').glob('*.json')):
        link = g.read_json(pointer); g.checked(link['result'], link['sha256'])
        r = g.read_json(link['result']); existing.append(r)
    hardest = max(existing, key=lambda r:r['iterations'])
    hard_position = hardest['scene']*6+hardest['index']
    sequence = [0, hard_position, 5, 0]
    receiver = initialize(plan)
    models = [receiver.model.network, receiver.evidence.network]
    before = [state_sha(m) for m in models]
    reports = []
    try:
        for order, position in enumerate(sequence):
            target = REV/'validation'/f'{order:02d}_{g.tag(position)}'
            row = execute_case(receiver, plan, cases[position], target, validation=True, session='validation')
            old, _, reference = g.validate_result(position, plan)
            current = arrays(target/'prediction.npz')
            assert set(current) == set(reference)
            differences = {}
            for key in current:
                a, b = current[key], reference[key]
                assert a.shape == b.shape and a.dtype == b.dtype
                maximum = float(np.max(np.abs(a.astype(complex)-b.astype(complex))))
                differences[key] = maximum
                if key in ('activity_decision','phase','phase_slopes','initial_phase','initial_phase_slopes'):
                    np.testing.assert_array_equal(a,b)
                else:
                    # Same FP32 operators; a few ulps allowed, decisions/stopping exact.
                    np.testing.assert_allclose(a,b,rtol=2e-6,atol=2e-7)
            assert row['iterations']==old['iterations'] and row['stopping_reason']==old['stopping_reason']
            check_metrics(row['metrics'],score_arrays(current,arrays(Path(cases[position]['ready']).parent/'truth.npz')))
            assert row['metrics']['misses']==old['metrics']['misses']
            assert row['metrics']['false_alarms']==old['metrics']['false_alarms']
            reports.append(dict(position=position, iterations=row['iterations'], maximum_absolute_differences=differences,
                result=str(target/'RESULT.json'), result_sha256=g.sha256(target/'RESULT.json'),
                reference=str(Path(plan['native_directory'])/g.tag(position)/'RESULT.json'),
                reference_sha256=g.sha256(Path(plan['native_directory'])/g.tag(position)/'RESULT.json')))
        assert before == [state_sha(m) for m in models]
        g.write_json(REV/'VALIDATION.json',dict(status='PASS', completed_unix=time.time(),
            sequence=sequence, tests=reports, networks_unchanged=True, saved_arrays_rescored=True,
            decisions_and_iterations_identical=True, plan_sha256=g.sha256(OUT/'PLAN.json'),
            amendment_sha256=g.sha256(REV/'AMENDMENT.json'), counted_in_main_6000=False))
    except Exception:
        g.write_json(REV/'VALIDATION_FAILURE.json',dict(status='FAILED',traceback=traceback.format_exc(),tests=reports))
        raise


def worker(session, slot):
    g.require_ready()
    plan = verify()
    folder = REV/'sessions'/session/f'worker{slot}'
    process = psutil.Process()
    identity = dict(pid=process.pid,created_unix=process.create_time(),command=process.cmdline())
    try:
        receiver = initialize(plan)
        cases = g.read_json(OUT/'INPUTS.json')
        g.write_json(folder/'STATE.json',dict(stage='READY',updated_unix=time.time(),**identity))
        for line in sys.stdin:
            request = json.loads(line)
            if request['position'] is None:
                break
            position = request['position']
            began = time.time()
            g.write_json(folder/'STATE.json',dict(stage='BUSY',position=position,started_unix=began,
                updated_unix=began,**identity))
            row = execute_case(receiver, plan, cases[position], Path(plan['native_directory'])/g.tag(position),session=session)
            g.write_json(folder/'STATE.json',dict(stage='COMPLETE',position=position,started_unix=began,
                updated_unix=time.time(),iterations=row['iterations'],rss_gib=process.memory_info().rss/2**30,**identity))
        g.write_json(folder/'STATE.json',dict(stage='EXITED',updated_unix=time.time(),**identity))
    except Exception:
        g.write_json(folder/'STATE.json',dict(stage='FAILED',updated_unix=time.time(),traceback=traceback.format_exc(),**identity))
        raise


def scan_completed(plan, session_folder):
    cases = g.read_json(OUT/'INPUTS.json')
    original_read = common.read_json
    completed = set()
    hashes = {}
    def cached_read(path):
        return cases if Path(path)==OUT/'INPUTS.json' else original_read(path)
    with patch.object(common,'read_json',cached_read):
        for position in range(6000):
            folder = Path(plan['native_directory'])/g.tag(position)
            pointer = OUT/'results'/(g.tag(position)+'.json')
            if not folder.exists() and not pointer.exists():
                continue
            if not pointer.exists() or (folder/'FAILURE.json').exists():
                raise RuntimeError('Unfinished or unlinked output retained: '+str(folder))
            link = g.read_json(pointer)
            assert Path(link['result'])==folder/'RESULT.json'
            g.checked(link['result'],link['sha256'])
            g.validate_result(position,plan)
            completed.add(position);hashes[str(pointer)]=g.sha256(pointer)
            if len(completed)%100==0:
                g.write_json(session_folder/'RESUME_CHECK_PROGRESS.json',dict(checked=len(completed),updated_unix=time.time()))
    g.write_json(session_folder/'PRESERVED_RESULTS.json',hashes)
    g.write_json(session_folder/'RESUME_VALIDATION.json',dict(status='PASS',inputs=len(completed),
        saved_arrays_rescored=True,exact_pointer_and_native_pairing=True,
        preserved_results_sha256=g.sha256(session_folder/'PRESERVED_RESULTS.json')))
    return completed


def launch(session, slot):
    folder = REV/'sessions'/session/f'worker{slot}'
    folder.mkdir(parents=True,exist_ok=False)
    env = dict(os.environ,PYTHONPATH=str(ROOT/'src'),OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',
               OPENBLAS_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2')
    env.pop('CUDA_VISIBLE_DEVICES',None)
    command = [str(ROOT/'.venv/Scripts/python.exe'),'-X','utf8','-B','-m',MODULE,'worker','--session',session,'--slot',str(slot)]
    with (folder/'stdout.log').open('xb') as out, (folder/'stderr.log').open('xb') as err:
        proc = subprocess.Popen(command,cwd=ROOT,env=env,stdin=subprocess.PIPE,stdout=out,stderr=err,
                                creationflags=subprocess.CREATE_NO_WINDOW,text=True)
    receipt = dict(pid=proc.pid,created_unix=psutil.Process(proc.pid).create_time(),command=command,
        started_unix=time.time(),state_path=str(folder/'STATE.json'),stdout=str(folder/'stdout.log'),
        stderr=str(folder/'stderr.log'),slot=slot,position=None,closing=False)
    g.write_json(folder/'LAUNCH.json',receipt)
    return proc,receipt


def coordinate():
    dependencies = g.require_ready()
    plan = verify()
    g.verify(full=True)
    no_other_execution()
    for name in ('STOP.json','FAILURE.json','COMPLETION.json'):
        if (OUT/name).exists():
            raise RuntimeError('Inspect existing '+name+' before continuation')
    validation = g.read_json(REV/'VALIDATION.json')
    assert validation['status']=='PASS' and validation['amendment_sha256']==g.sha256(REV/'AMENDMENT.json')
    assert g.read_json(OUT/'PREFLIGHT.json')['status']=='PASS'
    amendment = g.read_json(REV/'AMENDMENT.json')
    runtime_plan = dict(plan,runtime=dict(plan['runtime'],**amendment['runtime_overrides']))
    session = str(time.time_ns())
    folder = REV/'sessions'/session;folder.mkdir(parents=True,exist_ok=False)
    own = psutil.Process()
    identity = dict(pid=own.pid,created_unix=own.create_time(),command=own.cmdline())
    lock = OUT/'RUNNING.lock'
    with lock.open('x',encoding='utf-8') as stream:
        json.dump(identity,stream)
    active,completed = [],set()
    original_start = g.read_json(OUT/'START.json')
    began = original_start['started_unix']
    g.write_json(folder/'PREVIOUS_START.json',original_start)
    g.write_json(folder/'START.json',dict(**identity,session=session,started_unix=time.time(),
        original_started_unix=began,amendment_sha256=g.sha256(REV/'AMENDMENT.json'),dependencies=dependencies))
    g.write_json(OUT/'START.json',dict(**identity,started_unix=began,resumed_unix=time.time(),
        session=session,execution_module=MODULE,plan_sha256=g.sha256(OUT/'PLAN.json')))
    last_status = 0.
    def status(stage,failed=0,force=False):
        nonlocal last_status
        if force or time.monotonic()-last_status>=2:
            workers=[]
            for proc,r in active:
                value=dict(r)
                state_path=Path(r['state_path'])
                if state_path.exists():value['worker_state']=g.read_json(state_path)
                workers.append(value)
            g.write_json(OUT/'STATUS.json',dict(stage=stage,**identity,updated_unix=time.time(),planned=6000,
                completed=len(completed),active_workers=len(active),workers=workers,failed=failed,
                execution_module=MODULE,session=session,max_workers=runtime_plan['runtime']['max_workers']))
            last_status=time.monotonic()
    try:
        status('VALIDATING_RESUME',force=True)
        completed=scan_completed(plan,folder)
        pending=[p for p in range(6000) if p not in completed]
        cursor=0;failures=[];next_slot=0
        while active or cursor<len(pending):
            stopping=(OUT/'STOP.json').exists() or bool(failures)
            survivors=[]
            for proc,r in active:
                state=g.read_json(r['state_path']) if Path(r['state_path']).exists() else {'stage':'LOADING'}
                code=proc.poll()
                if state['stage']=='FAILED' or (code is not None and (code!=0 or not r['closing'])):
                    failures.append(dict(receipt=r,exit_code=code,state=state));stopping=True
                    if code is None:survivors.append((proc,r))
                    continue
                if code is not None:
                    g.write_json(Path(r['state_path']).parent/'EXIT.json',dict(exit_code=code,checked_unix=time.time()))
                    continue
                if r['position'] is not None and state['stage']=='COMPLETE' and state['position']==r['position']:
                    pos=r['position'];link=g.read_json(OUT/'results'/(g.tag(pos)+'.json'))
                    g.checked(link['result'],link['sha256']);row=g.read_json(link['result'])
                    assert row['status']=='COMPLETE' and row['execution']['session']==session
                    completed.add(pos);r['position']=None
                if not r['closing'] and r['position'] is None and state['stage'] in ('READY','COMPLETE'):
                    if stopping or cursor==len(pending):
                        proc.stdin.write(json.dumps({'position':None})+'\n');proc.stdin.flush();r['closing']=True
                    else:
                        pos=pending[cursor];cursor+=1;r['position']=pos;r['started_unix']=time.time()
                        proc.stdin.write(json.dumps({'position':pos})+'\n');proc.stdin.flush()
                if not r['closing'] and time.time()-r['started_unix']>plan['runtime']['input_timeout_seconds']:
                    raise TimeoutError('Worker timeout; process retained for inspection')
                survivors.append((proc,r))
            active=survivors
            if not stopping and cursor<len(pending) and len(active)<runtime_plan['runtime']['max_workers']:
                # Start one at a time. Wait for its CUDA/model allocation before adding another.
                ready=all(Path(r['state_path']).exists() for _,r in active)
                if ready and capacity(runtime_plan,active):
                    active.append(launch(session,next_slot));next_slot+=1
            if time.time()-began>plan['runtime']['total_timeout_seconds']:
                raise TimeoutError('Original total execution budget exceeded')
            status('DRAINING_FAILURE' if failures else 'DRAINING_STOP' if stopping else
                   'RUNNING' if active else 'WAITING_FOR_MEMORY',len(failures))
            if stopping and not active:
                if failures:g.write_json(OUT/'FAILURE.json',dict(status='FAILED',failures=failures,automatic_retry=False))
                status('FAILED' if failures else 'PAUSED',len(failures),force=True);return
            time.sleep(.2)
        status('VERIFYING',force=True)
        verify()
        from evaluation.white_phase_frontend_20261106.report import summarize
        summarize()
        status('COMPLETE',force=True)
    except Exception:
        g.write_json(OUT/'FAILURE.json',dict(status='FAILED',traceback=traceback.format_exc(),
            active_workers=[r for _,r in active],automatic_retry=False))
        status('FAILED',1,force=True)
        raise
    finally:
        lock.unlink(missing_ok=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=('coordinate','worker','validate','inspect'))
    parser.add_argument('--session');parser.add_argument('--slot',type=int)
    args=parser.parse_args()
    if args.command=='coordinate':coordinate()
    elif args.command=='worker':worker(args.session,args.slot)
    elif args.command=='validate':validate()
    else:print(g.require_ready());print(verify()['planned'])
