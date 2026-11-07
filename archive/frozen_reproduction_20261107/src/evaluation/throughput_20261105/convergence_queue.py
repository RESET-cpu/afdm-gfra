"""Independent CPU/GPU queues around the original fixed-300-iteration worker."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

import psutil

from project import ROOT
from utils import read_json, write_json, sha256
from evaluation.convergence_20261105.run import verify, case_name, load_case, summarize

OUT = ROOT / 'result/snr_comparison/data/convergence_50x300_20261105'
TUNE = OUT / 'throughput_20261105'
WHITE = ROOT / 'result/snr_comparison/data/white_preconditioned_matched_fp32_1000_snr_20261105'
STATE_CACHE = {}


def backend(method):
    return 'gpu' if method in ('STMP', 'GP-MP') else 'cpu'


def admission(available, outstanding_reserve, peak, floor):
    return available - outstanding_reserve >= peak + floor


def publish_status(path, value):
    """Status is advisory; a transient Windows reader must not stop inference."""
    for attempt in range(5):
        try:
            write_json(path, value)
            return True
        except PermissionError:
            time.sleep(.05 * (attempt + 1))
    print(json.dumps(dict(event='STATUS_WRITE_DELAYED', path=str(path))), flush=True)
    return False


def read_state(path, fallback=None):
    """Use the last complete advisory snapshot while Windows holds a file lock."""
    for attempt in range(5):
        try:
            value = read_json(path)
            STATE_CACHE[str(path)] = value
            return value
        except PermissionError:
            time.sleep(.02 * (attempt + 1))
    if str(path) in STATE_CACHE:
        return STATE_CACHE[str(path)]
    if fallback is not None:
        return fallback
    raise PermissionError('Runtime settings remained locked: ' + str(path))


def tree_rss(pid):
    try:
        parent = psutil.Process(pid)
        total = 0.
        for member in [parent] + parent.children(recursive=True):
            try:
                total += member.memory_info().rss / 2**30
            except psutil.NoSuchProcess:
                pass
        return total
    except psutil.NoSuchProcess:
        return 0.


def gpu_sample():
    result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.free,power.draw',
                             '--format=csv,noheader,nounits'], capture_output=True, text=True, check=True,
                            timeout=10, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    utilization, used, free, power = map(float, result.stdout.strip().split(','))
    return dict(gpu_utilization=utilization, gpu_used_gib=used/1024, gpu_free_gib=free/1024,
                gpu_power_watts=power, ram_available_gib=psutil.virtual_memory().available/2**30)


def capacity(kind, active, settings, sample):
    reserve = 0.
    for _, receipt in active:
        reserve += max(0., settings[receipt['backend'] + '_peak_ram_gib'] - tree_rss(receipt['pid']))
    # Reserve growth for the two independent, unchanged white-SNR worker slots.
    white = read_state(WHITE / 'STATUS.json', dict(stage='RUNNING', workers=[], completed=0))
    if white['stage'] in ('RUNNING', 'WAITING_FOR_MEMORY'):
        workers = white.get('workers', [])
        reserve += sum(max(0., settings['white_peak_ram_gib'] - tree_rss(row['pid'])) for row in workers)
        reserve += max(0, 2-len(workers)) * settings['white_peak_ram_gib']
    if not admission(sample['ram_available_gib'], reserve, settings[kind + '_peak_ram_gib'],
                     settings['minimum_free_ram_gib']):
        return False
    return kind != 'gpu' or sample['gpu_free_gib'] >= settings['minimum_free_gpu_gib']


def pending_cases(plan):
    jobs, complete = [], []
    for scene in plan['scene_ids']:
        for method in plan['methods']:
            dest = OUT / 'cases' / case_name(method, scene)
            if dest.exists():
                load_case(OUT, plan, method, scene)
                complete.append((method, scene))
            else:
                jobs.append(dict(method=method, scene=scene, backend=backend(method)))
    return jobs, complete


def launch(job, companions=()):
    name = case_name(job['method'], job['scene'])
    logs = OUT / 'logs'
    command = [sys.executable, '-X', 'utf8', '-B', str(ROOT/'run_experiments.py'), 'convergence',
               'worker', '--output', str(OUT), '--method', job['method'], '--scene', str(job['scene'])]
    grouped = [job, *companions]
    if companions:
        validation = read_json(TUNE/'paired_validation'/'VALIDATION.json')
        if (validation['status'] != 'PASS' or validation['adapter_sha256'] != sha256(
                ROOT/'src/evaluation/throughput_20261105/paired_gpu.py')):
            raise ValueError('Validated shared-runtime adapter required')
        specification = TUNE/'groups'/(name+'.json')
        if specification.exists():
            raise FileExistsError('GPU group already launched: '+name)
        write_json(specification, dict(output=str(OUT), jobs=grouped))
        command = [sys.executable, '-X', 'utf8', '-B', '-m',
                   'evaluation.throughput_20261105.paired_gpu', str(specification)]
    env = dict(os.environ, PYTHONPATH=str(ROOT/'src'), OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
               OPENBLAS_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1')
    flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    if job['backend'] == 'cpu':
        env['CUDA_VISIBLE_DEVICES'] = ''
        flags |= getattr(subprocess, 'BELOW_NORMAL_PRIORITY_CLASS', 0)
    else:
        env.pop('CUDA_VISIBLE_DEVICES', None)
    with (logs/(name+'.out')).open('xb') as stdout, (logs/(name+'.err')).open('xb') as stderr:
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=stdout, stderr=stderr, creationflags=flags)
    receipt = dict(job, jobs=grouped, pid=process.pid, created_unix=psutil.Process(process.pid).create_time(),
                   started_unix=time.time(), command=command)
    write_json(TUNE/'launches'/(name+'.json'), receipt)
    return process, receipt


def coordinate():
    plan = verify(OUT)
    with (OUT/'RUNNING.lock').open('x') as handle:
        handle.write(str(os.getpid()))
    active, failed = [], []
    started = time.time()
    try:
        jobs, complete = pending_cases(plan)
        initial_completed = len(complete)
        write_json(TUNE/'START.json', dict(pid=os.getpid(), created_unix=psutil.Process().create_time(),
            started_unix=started, completed=initial_completed, remaining=len(jobs),
            authorization='你尽量让我的5080火力全开', plan_sha256=sha256(OUT/'PLAN.json'),
            scheduler_sha256=sha256(__file__), inference_worker_unchanged=True,
            precision_unchanged=True, automatic_retry=False))
        last_sample = 0.
        while jobs or active:
            remaining = []
            for process, receipt in active:
                code = process.poll()
                if code is None:
                    remaining.append((process, receipt))
                    if time.time()-receipt['started_unix'] > 7200:
                        raise TimeoutError('Worker exceeded two hours; retained for diagnosis')
                elif code:
                    failed.append(dict(receipt, exit_code=code))
                else:
                    for job in receipt['jobs']:
                        load_case(OUT, plan, job['method'], job['scene'])
                        complete.append((job['method'], job['scene']))
                        print(json.dumps(dict(event='COMPLETE', method=job['method'], scene=job['scene'],
                              group_seconds=time.time()-receipt['started_unix'], completed=len(complete))), flush=True)
            active = remaining
            settings = read_state(TUNE/'RUNTIME.json')
            stopped = (TUNE/'STOP.json').exists()
            if time.time()-started > 1209600:
                raise TimeoutError('Total scheduling budget exceeded; active workers retained')
            if time.time()-last_sample >= 2:
                sample = gpu_sample()
                sample.update(time=time.time(), completed=len(complete), initial_completed=initial_completed,
                              active_gpu=sum(r['backend']=='gpu' for _, r in active),
                              active_gpu_cases=sum(len(r['jobs']) for _, r in active if r['backend']=='gpu'),
                              active_cpu=sum(r['backend']=='cpu' for _, r in active),
                              white_completed=read_state(WHITE/'STATUS.json', dict(completed=0))['completed'],
                              gpu_worker_limit=settings['gpu_workers'], cpu_worker_limit=settings['cpu_workers'])
                with (TUNE/'TELEMETRY.jsonl').open('a', encoding='utf-8') as handle:
                    handle.write(json.dumps(sample)+'\n')
                last_sample = time.time()
            for kind in ('gpu', 'cpu'):
                while not failed and not stopped and sum(r['backend']==kind for _, r in active) < settings[kind+'_workers']:
                    if kind == 'cpu' and any(j['backend']=='gpu' for j in jobs) and not any(
                            r['backend']=='gpu' for _, r in active):
                        break
                    job = next((j for j in jobs if j['backend']==kind), None)
                    if job is None:
                        break
                    live_sample = dict(sample, ram_available_gib=psutil.virtual_memory().available/2**30)
                    if not capacity(kind, active, settings, live_sample):
                        break
                    companions = ([j for j in jobs if j['backend']=='gpu' and j != job][
                                  :settings.get('gpu_tasks_per_process', 1)-1] if kind=='gpu' else [])
                    active.append(launch(job, companions))
                    jobs.remove(job)
                    for companion in companions:
                        jobs.remove(companion)
            stage = ('DRAINING_FAILURE' if failed else 'DRAINING_STOP' if stopped else
                     'RUNNING' if active else 'WAITING_FOR_MEMORY')
            publish_status(OUT/'STATUS.json', dict(stage=stage, pid=os.getpid(), updated_unix=time.time(),
                completed=len(complete), total=plan['planned_inferences'], active_workers=len(active),
                workers=[r for _, r in active], gpu_workers=sum(r['backend']=='gpu' for _, r in active),
                cpu_workers=sum(r['backend']=='cpu' for _, r in active), failed=len(failed),
                gpu_cases=sum(len(r['jobs']) for _, r in active if r['backend']=='gpu'),
                runtime_override=str(TUNE/'RUNTIME.json')))
            publish_status(OUT/'MONITOR.json', dict(updated_unix=time.time(), coordinator_alive=True,
                coordinator_pid=os.getpid(), completed=len(complete), total=plan['planned_inferences'],
                stage=stage, elapsed_seconds=time.time()-started, timeout_seconds=1209600))
            if (failed or stopped) and not active:
                if failed:
                    write_json(TUNE/'FAILURE.json', dict(failures=failed, automatic_retry=False))
                break
            time.sleep(.5)
        if not failed and not jobs:
            summarize(OUT)
        stage = 'FAILED' if failed else 'PAUSED' if jobs else 'COMPLETE'
        write_json(OUT/'STATUS.json', dict(stage=stage, completed=len(complete), total=plan['planned_inferences'],
                   active_workers=0, gpu_workers=0, cpu_workers=0, failed=len(failed)))
        write_json(TUNE/'EXIT.json', dict(stage=stage, finished_unix=time.time(), automatic_retry=False))
    except BaseException:
        write_json(TUNE/'FAILURE.json', dict(traceback=traceback.format_exc(),
                   active_workers=[r for _, r in active], automatic_retry=False))
        raise
    finally:
        (OUT/'RUNNING.lock').unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['run'])
    parser.parse_args()
    coordinate()
