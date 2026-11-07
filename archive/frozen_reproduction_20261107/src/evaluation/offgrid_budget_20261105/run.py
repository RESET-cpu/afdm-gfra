"""Saved-input CPU batch; each inference runs in a fresh, bounded worker."""
import argparse
import csv
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

import psutil

from project import ROOT
from utils import read_json, sha256, write_json

OUT = ROOT / 'result/snr_comparison/data/offgrid_search_budgets_1000_cpu_20261105'
NATIVE = Path('E:/afdm-gfra-results/offgrid_search_budgets_1000_cpu_20261105')
SNRS = [-4, -2, 0, 2, 4, 6]


def checked(path, digest):
    if sha256(path) != digest:
        raise ValueError('SHA256 mismatch: ' + str(path))


def verify():
    plan = read_json(OUT / 'PLAN.json')
    checked(OUT / 'PLAN.json', read_json(OUT / 'PLAN_HASH.json')['sha256'])
    for path, digest in plan['assets'].items():
        checked(ROOT / path, digest)
    return plan


def input_case(position):
    import numpy as np
    from system.observation import ReceiverInput
    case = read_json(OUT / 'INPUTS.json')[position]
    folder = Path(case['ready']).parent
    checked(case['ready'], case['ready_sha256'])
    for name, digest in case['files'].items():
        checked(folder / name, digest)
    with np.load(folder / 'public.npz', allow_pickle=False) as z:
        inputs = ReceiverInput(z['y'], z['a'], 1.0, float(z['rho']))
    return case, folder, inputs


def task_tag(budget, position):
    return f'budget{budget}_scene{position // 6:04d}_condition{position % 6:02d}'


def worker(budget, position, preflight=False):
    import numpy as np
    from threadpoolctl import threadpool_limits
    from evaluation.offgrid_budget_20261105.receiver import Receiver
    from evaluation.metrics import score_arrays
    from evaluation.storage import save_arrays, arrays as load_arrays
    plan = verify()
    process = psutil.Process()
    process.cpu_affinity(plan['runtime']['cpu_affinity'])
    process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    tag = task_tag(budget, position)
    dest = (OUT / 'preflight' if preflight else NATIVE) / tag
    dest.mkdir(parents=True, exist_ok=False)
    started = time.time()
    try:
        case, folder, inputs = input_case(position)
        write_json(dest / 'START.json', dict(pid=os.getpid(), created_unix=process.create_time(),
                   case=case, budget=budget, started_unix=started, preflight=preflight))
        with threadpool_limits(limits=1):
            if budget == 7:
                from algorithm.baseline._base import EstimatedNoiseBaselineReceiver
                receiver = EstimatedNoiseBaselineReceiver('offgrid_sbl', device='cpu')
                arrays, record = receiver.infer(inputs)
                entry = read_json(ROOT / plan['baseline_selection'])
                spec = importlib.util.spec_from_file_location('adopted_baseline_readout', entry['readout_implementation'])
                readout = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(readout)
                snr = readout.estimated_snr(float(np.mean(abs(inputs.observation)**2)),
                                          float(arrays['noise_variance_estimate']))
                threshold, node = readout.threshold('offgrid_sbl', snr)
                arrays['native_activity_decision'] = arrays['activity_decision'].copy()
                arrays['activity_decision'] = readout.decide(arrays['activity_score'], arrays['channel_energy'], threshold)
                record.update(activity_threshold=float(threshold), public_estimated_snr_db=snr,
                              activity_policy_sha256=entry['policy_sha256'])
            else:
                receiver = Receiver(plan['configurations'][str(budget)])
                arrays, record = receiver.infer(inputs)
        if not all(np.isfinite(v).all() for v in arrays.values()):
            raise FloatingPointError('Nonfinite receiver output')
        assert record['iterations'] <= 120 and not record['noise_truth_used'] and not record['truth_used_in_inference']
        save_arrays(dest / 'prediction.npz', arrays)
        write_json(dest / 'record.json', record)
        # Channel/activity truth is opened only after inference and prediction saving.
        truth = load_arrays(folder / 'truth.npz')
        metrics = score_arrays(arrays, truth)
        rescored = score_arrays(load_arrays(dest / 'prediction.npz'), truth)
        assert metrics == rescored
        row = dict(status='COMPLETE', scene=case['scene'], index=case['index'], snr_db=case['snr_db'],
                   budget=budget, metrics=metrics, iterations=record['iterations'],
                   stopping_reason=record['stopping_reason'], seconds=time.time()-started,
                   inference_seconds=record['seconds'], preflight=preflight,
                   peak_working_set_bytes=getattr(process.memory_info(), 'peak_wset', process.memory_info().rss),
                   prediction=str(dest / 'prediction.npz'), prediction_sha256=sha256(dest / 'prediction.npz'),
                   record=str(dest / 'record.json'), record_sha256=sha256(dest / 'record.json'),
                   input_hashes=case['files'], plan_sha256=sha256(OUT / 'PLAN.json'),
                   truth_used_in_inference=False, phase_mode='known', noise_mode='estimated')
        if budget == 7:
            ref = read_json(OUT / 'REFERENCES.json')[position]
            checked(ref['result'], ref['sha256'])
            old = read_json(ref['result'])
            compact = Path(ref['result']).with_suffix('.npz')
            checked(compact, old['compact_sha256'])
            saved = load_arrays(compact)
            np.testing.assert_allclose(metrics['per_user_error'], saved['per_user_error'], rtol=1e-7, atol=1e-8)
            np.testing.assert_allclose(arrays['activity_score'], saved['activity_score'], rtol=1e-7, atol=1e-9)
            expected = readout.decide(saved['activity_score'], saved['channel_energy'], ref['threshold'])
            np.testing.assert_array_equal(arrays['activity_decision'], expected)
            assert record['iterations'] == old['iterations'] and record['stopping_reason'] == old['stopping_reason']
            row['baseline_reproduction'] = 'PASS'
            row['baseline_nmse_difference_db'] = metrics['nmse_db'] - old['metrics']['nmse_db']
        write_json(dest / 'RESULT.json', row)
        if not preflight:
            write_json(OUT / 'results' / (tag + '.json'), dict(result=str(dest / 'RESULT.json'), sha256=sha256(dest / 'RESULT.json')))
    except Exception:
        write_json(dest / 'FAILURE.json', dict(status='FAILED', budget=budget, position=position,
                   traceback=traceback.format_exc(), automatic_retry=False))
        raise


def launch_worker(budget, position, preflight, plan):
    tag = ('preflight_' if preflight else '') + task_tag(budget, position)
    logs = OUT / 'logs'; logs.mkdir(exist_ok=True)
    env = dict(os.environ, PYTHONPATH=str(ROOT / 'src'), CUDA_VISIBLE_DEVICES='',
               OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', OMP_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1')
    args = [str(ROOT / '.venv/Scripts/python.exe'), '-X', 'utf8', '-B', '-m',
            'evaluation.offgrid_budget_20261105.run', 'worker', '--budget', str(budget), '--position', str(position)]
    if preflight:
        args.append('--preflight')
    stdout = (logs / (tag + '.out')).open('xb'); stderr = (logs / (tag + '.err')).open('xb')
    try:
        proc = subprocess.Popen(args, cwd=ROOT, env=env, stdout=stdout, stderr=stderr,
                                creationflags=subprocess.CREATE_NO_WINDOW)
    finally:
        stdout.close(); stderr.close()
    receipt = dict(tag=tag, pid=proc.pid, command=args, started_unix=time.time(), budget=budget,
                   position=position, preflight=preflight, stdout=str(logs / (tag + '.out')),
                   stderr=str(logs / (tag + '.err')))
    write_json(OUT / 'launches' / (tag + '.json'), receipt)
    return proc, receipt


def status(stage, active, completed, **extra):
    value = dict(stage=stage, pid=os.getpid(), updated_unix=time.time(), completed=completed,
                 planned=12000, active_workers=len(active), workers=[r for _, r in active], **extra)
    # Advisory progress is separate from strict scientific result files.
    for attempt in range(3):
        try:
            write_json(OUT / 'STATUS.json', value)
            return
        except PermissionError:
            if attempt == 2:
                print('Advisory STATUS write temporarily locked', flush=True)
            time.sleep(.05)


def capacity(plan, active):
    rt = plan['runtime']; available = psutil.virtual_memory().available / 2**30
    # Account for memory that live workers may still allocate after their startup.
    reserve = 0.0
    for proc, receipt in active:
        try:
            processes = [psutil.Process(proc.pid)]
            processes += processes[0].children(recursive=True)
            rss = sum(p.memory_info().rss for p in processes) / 2**30
            reserve += max(0.0, rt['worker_peak_budget_gib'] - rss)
        except psutil.NoSuchProcess:
            pass
    return available - reserve >= rt['minimum_free_ram_gib'] + rt['worker_peak_budget_gib']


def coordinate():
    plan = verify()
    lock = OUT / 'RUNNING.lock'
    with lock.open('x', encoding='utf-8') as f:
        import json
        json.dump(dict(pid=os.getpid(), created_unix=psutil.Process().create_time()), f)
    if (OUT / 'START.json').exists():
        lock.unlink()
        raise RuntimeError('A prior execution exists; no automatic resume or retry')
    write_json(OUT / 'START.json', dict(started_unix=time.time(), pid=os.getpid(), plan_sha256=sha256(OUT / 'PLAN.json')))
    active = []; completed = 0; failed = []
    began = time.time()
    try:
        for budget in (7, 13, 25):
            while not capacity(plan, []):
                if (OUT / 'STOP.json').exists():
                    status('PAUSED', [], completed, failed=0)
                    return
                if time.time()-began > plan['runtime']['total_timeout_seconds']:
                    raise TimeoutError('CPU queue exceeded the total time budget')
                status('WAITING_FOR_MEMORY_PREFLIGHT', [], completed, failed=0, next_budget=budget)
                time.sleep(15)
            proc, receipt = launch_worker(budget, 0, True, plan)
            active = [(proc, receipt)]
            while proc.poll() is None:
                status('PREFLIGHT', active, completed, failed=0, budget=budget)
                if time.time()-receipt['started_unix'] > plan['runtime']['input_timeout_seconds']:
                    raise TimeoutError('Preflight exceeded timeout; process retained for inspection')
                time.sleep(5)
            active = []
            if proc.returncode != 0:
                raise RuntimeError(f'Preflight budget {budget} failed; no automatic retry')
            record = read_json(OUT / 'preflight' / task_tag(budget, 0) / 'RESULT.json')
            assert record['status'] == 'COMPLETE'
        write_json(OUT / 'PREFLIGHT.json', dict(status='PASS', budgets=[7,13,25],
                   original_budget_reproduced=True, truth_not_used_for_inference=True,
                   new_budgets_finite=True, thresholds_not_refitted=True, completed_unix=time.time()))
        tasks = [(budget, position) for position in range(6000) for budget in (13,25)]
        cursor = 0
        while cursor < len(tasks) or active:
            still = []
            for proc, receipt in active:
                rc = proc.poll()
                if rc is None:
                    if time.time()-receipt['started_unix'] > plan['runtime']['input_timeout_seconds']:
                        raise TimeoutError('Worker exceeded timeout; process retained for inspection')
                    still.append((proc, receipt)); continue
                if rc == 0:
                    pointer = OUT / 'results' / (task_tag(receipt['budget'], receipt['position']) + '.json')
                    link = read_json(pointer); checked(link['result'], link['sha256'])
                    result = read_json(link['result']); assert result['status'] == 'COMPLETE'
                    completed += 1
                else:
                    failed.append(dict(receipt, exit_code=rc))
            active = still
            stopped = (OUT / 'STOP.json').exists()
            if time.time()-began > plan['runtime']['total_timeout_seconds']:
                raise TimeoutError('Batch exceeded total budget; active processes retained')
            while not failed and not stopped and cursor < len(tasks) and len(active) < plan['runtime']['max_workers'] and capacity(plan, active):
                budget, position = tasks[cursor]
                active.append(launch_worker(budget, position, False, plan)); cursor += 1
            stage = 'DRAINING_FAILURE' if failed else 'DRAINING_STOP' if stopped else 'RUNNING' if active else 'WAITING_FOR_MEMORY'
            status(stage, active, completed, failed=len(failed), dispatched=cursor)
            if (failed or stopped) and not active:
                if failed:
                    write_json(OUT / 'FAILURE.json', dict(status='FAILED', failures=failed, automatic_retry=False))
                status('FAILED' if failed else 'PAUSED', [], completed, failed=len(failed))
                return
            if cursor == len(tasks) and not active:
                break
            time.sleep(5)
        status('VERIFYING', [], completed, failed=0)
        summarize(plan)
        status('COMPLETE', [], completed, failed=0)
    except Exception:
        write_json(OUT / 'FAILURE.json', dict(status='FAILED', traceback=traceback.format_exc(),
                   active_workers=[r for _,r in active], automatic_retry=False))
        status('FAILED', active, completed, failed=max(1,len(failed)))
        raise
    finally:
        lock.unlink(missing_ok=True)


def summarize(plan):
    import numpy as np
    from evaluation.metrics import score_arrays
    from evaluation.storage import arrays as load_arrays
    verify()
    cases = read_json(OUT / 'INPUTS.json'); refs = read_json(OUT / 'REFERENCES.json')
    entry = read_json(ROOT / plan['baseline_selection'])
    spec = importlib.util.spec_from_file_location('offgrid_report_readout', entry['readout_implementation'])
    readout = importlib.util.module_from_spec(spec); spec.loader.exec_module(readout)
    rows = []; hashes = {}
    for position, case in enumerate(cases):
        folder = Path(case['ready']).parent
        checked(folder / 'truth.npz', case['files']['truth.npz'])
        truth = load_arrays(folder / 'truth.npz')
        ref = refs[position]; assert (ref['scene'],ref['index']) == (case['scene'],case['index'])
        checked(ref['result'], ref['sha256']); old = read_json(ref['result'])
        compact = Path(ref['result']).with_suffix('.npz'); checked(compact,old['compact_sha256'])
        saved = load_arrays(compact); np.testing.assert_array_equal(saved['truth_activity'],truth['activity'])
        np.testing.assert_allclose(saved['per_user_error'].sum(),old['metrics']['full_error'],rtol=1e-12)
        decision = readout.decide(saved['activity_score'],saved['channel_energy'],ref['threshold'])
        active = truth['activity'].astype(bool)
        baseline = dict(old['metrics'],misses=int((active & ~decision).sum()),false_alarms=int((~active & decision).sum()))
        per_input = [(7,baseline,old['iterations'],old['stopping_reason'])]
        for budget in (13,25):
            link = read_json(OUT / 'results' / (task_tag(budget,position)+'.json'))
            checked(link['result'],link['sha256']); result = read_json(link['result'])
            for key in ('prediction','record'):
                checked(result[key],result[key+'_sha256']); hashes[result[key]]=result[key+'_sha256']
            metrics = score_arrays(load_arrays(result['prediction']),truth)
            assert metrics == result['metrics'] and result['input_hashes'] == case['files']
            per_input.append((budget,metrics,result['iterations'],result['stopping_reason']))
        for budget, metrics, iterations, reason in per_input:
            rows.append(dict(scene=case['scene'],index=case['index'],snr_db=case['snr_db'],budget=budget,
                **{k:metrics[k] for k in ['active','inactive','misses','false_alarms','full_error','signal_energy']},
                iterations=iterations,iteration_cap=reason=='MAX_ITERATIONS'))
    summary=[]
    for budget in (7,13,25):
        for index,snr in enumerate(SNRS):
            group=[r for r in rows if r['budget']==budget and r['index']==index]
            assert len(group)==1000 and {r['scene'] for r in group}==set(range(1000))
            sums={k:sum(r[k] for r in group) for k in ['active','inactive','misses','false_alarms','full_error','signal_energy']}
            summary.append(dict(budget=budget,snr_db=snr,scenes=1000,**sums,
                nmse_db=float(10*np.log10(sums['full_error']/sums['signal_energy'])),
                aer=(sums['misses']+sums['false_alarms'])/(sums['active']+sums['inactive']),
                mean_iterations=float(np.mean([r['iterations'] for r in group])),
                iteration_caps=sum(r['iteration_cap'] for r in group)))
    original=read_json(ROOT / plan['baseline_summary'])
    for actual in [r for r in summary if r['budget']==7]:
        expected=next(r for r in original['rows'] if r['method']=='offgrid_sbl' and r['snr_db']==actual['snr_db'])
        # Original summaries may use historical display names for AER fields;
        # NMSE alone is checked here, with full counts retained above.
        np.testing.assert_allclose(actual['nmse_db'],expected['nmse_db'],rtol=0,atol=1e-9)
        for key in ('misses','false_alarms','active','inactive'):
            assert actual[key] == expected[key]
    with (OUT / 'PAIRED_CASES.csv').open('x',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    write_json(OUT / 'SUMMARY.json',dict(status='COMPLETE',rows=summary,scenes=1000,
        new_inferences=12000,baseline_saved_results=6000,known_phases=True,estimated_noise=True,
        prior_development_exposure=True,grid_and_candidates_changed_together=True,
        activity_thresholds_transferred_without_refitting=True,
        finite_iteration_cap_outputs_retained=True,controlled_runtime_benchmark=False))
    write_json(OUT / 'OUTPUT_HASHES.json',hashes)
    write_json(OUT / 'COMPLETION.json',dict(status='PASS',new_inferences=12000,
        coverage='2 budgets x 1000 scenes x 6 SNRs',saved_arrays_rescored=True,
        summary_sha256=sha256(OUT/'SUMMARY.json'),output_hashes_sha256=sha256(OUT/'OUTPUT_HASHES.json'),
        completed_unix=time.time(),performance_acceptance=False))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['coordinate','worker','summarize'])
    parser.add_argument('--budget',type=int,choices=[7,13,25])
    parser.add_argument('--position',type=int)
    parser.add_argument('--preflight',action='store_true')
    args=parser.parse_args()
    if args.command=='coordinate': coordinate()
    elif args.command=='worker': worker(args.budget,args.position,args.preflight)
    else: summarize(verify())
