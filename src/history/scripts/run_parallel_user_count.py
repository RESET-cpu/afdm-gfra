"""Run independent user-count cases concurrently, then continue cross-channel."""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import ctypes
import msvcrt
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback
import warnings
import numpy as np
import torch
from threadpoolctl import threadpool_limits
import evaluate_saved_baseline_inputs as paired
from benchmark_receiver_execution import GraphForward

ROOT = paired.ROOT
OLD = ROOT/'results/new_models_paired_20261019_v2'
OUT = ROOT/'results/new_models_paired_20261019_cuda_graph'
read, save, sha = paired.read, paired.save, paired.sha


def prepare(workers):
    target = OUT/'user_count'
    if OUT.exists():
        raise ValueError('Fresh candidate directory required')
    plan = read(OLD/'user_count/PLAN.json')
    paired.verify_sources(plan)
    reports = [ROOT/'results/receiver_execution_20261019'/name/'REPORT.json'
               for name in ('graph_cross40_v2', 'graph_user20', 'graph_user100')]
    for path in reports:
        assert read(path)['exact'] and read(path)['iterations'] == 600
    index = read(Path(plan['input_package'])/'inputs/INDEX.json')['experiments']['user_count']['cases']
    reused = {}
    for row_path in sorted((OLD/'user_count').glob('scene*/condition*/proposed.json')):
        row = read(row_path)
        assert row['status'] == 'COMPLETE'
        assert sha(row_path.with_suffix('.npz')) == row['compact_sha256']
        _, _, hashes, _, _, _ = paired.load_case(plan, index, row['scene'], row['condition'])
        assert row['input_array_sha256'] == hashes
        relative = row_path.parent.relative_to(OLD/'user_count')
        reused[str(relative)] = {}
        for source in row_path.parent.iterdir():
            if source.suffix not in ('.json', '.npz'):
                continue
            destination = target/relative/source.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            assert sha(source) == sha(destination)
            reused[str(relative)][source.name] = sha(source)
    save(target/'REUSED_RESULTS.json', dict(source=str(OLD/'user_count'), cases=reused))
    new_files = [Path(__file__), ROOT/'scripts/benchmark_receiver_execution.py',
                 target/'REUSED_RESULTS.json', OLD/'user_count/PLAN.json', *reports]
    plan['source_and_weight_sha256'].update({str(p):sha(p) for p in new_files})
    plan.update(execution=dict(kind='CUDA graphs for unchanged first/second forward; independent case workers',
        workers=workers, numerical_validation='Exact equality of all output arrays on three full 600-iteration cases',
        precision='Original float32 networks and float64/complex128 CPU iteration',
        controls_changed=False, old_results_reused=len(reused)), created_unix=time.time())
    save(target/'PLAN.json', plan)
    save(target/'STATUS.json', dict(status='PREPARED', completed=len(reused), expected_runs=2500))
    print({'prepared':str(target), 'reused':len(reused), 'workers':workers}, flush=True)


def worker(number):
    target = OUT/'user_count'
    plan = read(target/'PLAN.json'); paired.verify_sources(plan)
    spec = plan['experiment']; workers = plan['execution']['workers']
    index = read(Path(plan['input_package'])/'inputs/INDEX.json')['experiments']['user_count']['cases']
    status = target/f'STATUS.worker{number}.json'
    assigned = list(range(number, plan['expected_runs'], workers))
    done = newly = 0
    started = time.time()
    torch.set_num_threads(1)
    model = paired.EstimatedNoiseProposedReceiver(spec['proposed_bundles']['proposed']['configuration'], device='cuda')
    model.base.model.first = GraphForward(model.base.model.first)
    model.base.model.second = GraphForward(model.base.model.second)
    with threadpool_limits(1):
        for flat in assigned:
            scene, condition = divmod(flat, len(spec['values']))
            folder = target/f'scene{scene:03d}/condition{condition:02d}'
            if not paired.pending_methods(folder, ['proposed']):
                done += 1
                continue
            state = dict(status='RUNNING', pid=os.getpid(), worker=number, completed=done,
                newly_completed=newly, assigned=len(assigned), scene=scene, condition=condition,
                started_unix=started, updated_unix=time.time())
            save(status, state)
            base = dict(scene=scene, condition=condition, method='proposed', phase_mode='estimated',
                        noise_mode='estimated', truth_used_in_inference=False)
            try:
                inputs, truth, hashes, proof, generation, phase = paired.load_case(plan, index, scene, condition)
                base['input_array_sha256'] = hashes
                save(folder/'INPUT.json', dict(arrays=hashes, generation=generation))
                save(folder/'PAIRING_SOURCE.json', dict(files=proof, operator_sha256=paired.array_sha256(inputs.operator),
                    public_input_sha256=hashes, no_regeneration=True))
                with warnings.catch_warnings(record=True) as notices:
                    warnings.simplefilter('always', RuntimeWarning)
                    prediction, record = model.infer(inputs)
                assert record['status'] == 'COMPLETE'
                if not all(np.isfinite(v).all() for v in prediction.values()):
                    raise FloatingPointError('Nonfinite output')
                metrics = paired.score_arrays(prediction, truth)
                compact = {k:v for k,v in prediction.items() if np.asarray(v).ndim <= 1}
                compact.update(per_user_error=np.asarray(metrics['per_user_error']), truth_activity=truth['activity'])
                paired.save_arrays(folder/'proposed.npz', compact)
                if scene == 0:
                    paired.save_arrays(folder/'proposed.prediction.npz', prediction)
                record['execution'] = plan['execution']
                save(folder/'proposed.record.json', record)
                save(folder/'proposed.json', dict(base, status='COMPLETE', metrics=metrics,
                    receiver_seconds=record['seconds'], phase_seconds=phase['seconds'],
                    compact_sha256=sha(folder/'proposed.npz'), iterations=record['iterations'],
                    stopping_reason=record['stopping_reason'],
                    output_array_sha256={k:paired.array_sha256(v) for k,v in prediction.items()},
                    warnings=[str(w.message) for w in notices]))
            except Exception:
                failure = traceback.format_exc()
                save(folder/'proposed.json', dict(base, status='FAILED', traceback=failure))
                save(status, dict(state, status='FAILED', traceback=failure, updated_unix=time.time()))
                raise
            done += 1; newly += 1
            save(status, dict(state, completed=done, newly_completed=newly, updated_unix=time.time()))
            print({'worker':number, 'completed':done, 'scene':scene, 'condition':condition,
                   'seconds':record['seconds'], 'time_unix':time.time()}, flush=True)
    paired.verify_sources(plan)
    save(status, dict(status='COMPLETE', completed=done, newly_completed=newly, assigned=len(assigned),
                     updated_unix=time.time()))


def supervise():
    with (OUT/'run.lock').open('a+b') as lock:
        lock.seek(0)
        if not lock.read(1):
            lock.write(b'0'); lock.flush()
        lock.seek(0); msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
        children, streams = [], []
        started = time.time()
        target = OUT/'user_count'; plan = read(target/'PLAN.json')
        paired.verify_sources(plan)
        (OUT/'logs').mkdir(exist_ok=True)
        try:
            for number in range(plan['execution']['workers']):
                log = (OUT/'logs'/f'user_count_worker{number}.log').open('a', encoding='utf-8')
                streams.append(log)
                command = [sys.executable, '-X', 'utf8', '-u', '-B', __file__, 'worker', '--worker', str(number)]
                children.append(subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NO_WINDOW))
            while True:
                codes = [p.poll() for p in children]
                states = [read(path) for path in sorted(target.glob('STATUS.worker*.json'))]
                if any(code not in (None, 0) for code in codes):
                    save(OUT/'STATUS.json', dict(status='FAILED', jobs=states, exit_codes=codes))
                    for child in children:
                        if child.poll() is None:
                            child.terminate()
                    return 1
                # Scan committed case results to include all reused cases during worker startup.
                completed = sum(1 for _ in target.glob('scene*/condition*/proposed.json'))
                state = dict(status='RUNNING', current_job='user_count', pid=os.getpid(),
                    worker_pids=[p.pid for p in children], workers=len(children), completed=completed,
                    newly_completed=sum(s.get('newly_completed', 0) for s in states),
                    expected_runs=2500, started_unix=started, updated_unix=time.time(),
                    cross_channel='QUEUED_UNTIL_USER_COUNT_COMPLETE')
                save(OUT/'STATUS.json', state); save(target/'STATUS.json', state)
                if all(code == 0 for code in codes):
                    break
                time.sleep(15)
            paired.verify_sources(plan)
            paired.summarize(target, plan['experiment'])
            if read(target/'SUMMARY.json')['status'] != 'COMPLETE':
                raise ValueError('User-count summary incomplete; cross-channel remains queued')
            save(target/'STATUS.json', dict(status='COMPLETE', completed=2500, updated_unix=time.time()))
            command = [sys.executable, '-X', 'utf8', '-u', '-B', 'scripts/evaluate_saved_baseline_inputs.py',
                       'run', '--output', str(OLD/'cross_channel')]
            with (OLD/'logs/cross_channel.log').open('a', encoding='utf-8') as log:
                child = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                         creationflags=subprocess.CREATE_NO_WINDOW)
                save(OUT/'STATUS.json', dict(status='RUNNING', current_job='cross_channel',
                    pid=os.getpid(), child_pid=child.pid, output=str(OLD/'cross_channel'), updated_unix=time.time()))
                code = child.wait()
            save(OUT/'STATUS.json', dict(status='COMPLETE' if code == 0 else 'FAILED', exit_code=code, updated_unix=time.time()))
            return code
        finally:
            for stream in streams:
                stream.close()
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'run', 'worker'))
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--worker', type=int)
    args = parser.parse_args()
    if args.action == 'prepare':
        prepare(args.workers)
    elif args.action == 'worker':
        worker(args.worker)
    else:
        raise SystemExit(supervise())
