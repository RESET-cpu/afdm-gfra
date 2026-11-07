"""Explicit plan/inspect/run/summarize entry; no inference during preparation."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

from experiment.studies.provenance import execution_identity
from workspace import ROOT
from fileio import read_json, sha256, write_json

CONFIG = ROOT / 'src/configs/experiments/convergence.json'
METHODS = ['STMP', 'GP-MP', 'Off-grid SBL (7)', 'Off-grid SBL (13)', 'Off-grid SBL (25)']


def checked(path, digest):
    if sha256(path) != digest:
        raise ValueError('Changed frozen asset: ' + str(path))


def case_name(method, scene):
    key = method.replace(' ', '_').replace('(', '').replace(')', '')
    return f'{key}_scene{scene:04d}'


def check_input(case):
    ready = Path(case['ready'])
    checked(ready, case['ready_sha256'])
    for name, digest in case['files'].items():
        checked(ready.parent / name, digest)


def prepare(output, config_path=CONFIG):
    if output.exists():
        raise FileExistsError('Use a fresh plan directory; existing attempts are preserved')
    config = read_json(config_path)
    if (config['methods'] != METHODS or config['early_stopping']
            or config['phase_mode'] != 'known' or config['noise_mode'] != 'estimated'
            or config['runtime']['tf32'] or config['runtime']['workers'] != 1
            or config['scene_count'] < 1 or config['iterations'] < 1):
        raise ValueError('Unsupported convergence protocol')
    white = ROOT / config['white_source']
    sbl = ROOT / config['sbl_source']
    source_plans = [read_json(white / 'PLAN.json'), read_json(sbl / 'PLAN.json')]
    manifest = read_json(white / 'INPUTS.json')
    other = {(r['scene'], r['index']): r for r in read_json(sbl / 'INPUTS.json')}
    scenes = list(range(config['first_scene'], config['first_scene'] + config['scene_count']))
    inputs = [r for r in manifest if r['scene'] in scenes and r['snr_db'] == config['snr_db']]
    if sorted(r['scene'] for r in inputs) != scenes:
        raise ValueError('Require exactly one existing input per declared scene at the selected SNR')
    inputs.sort(key=lambda r: r['scene'])
    for case in inputs:
        paired = other[(case['scene'], case['index'])]
        if any(case[key] != paired[key] for key in ('files', 'ready_sha256', 'snr_db')):
            raise ValueError('White and SBL source manifests are not paired')
        check_input(case)
    stmp = read_json(ROOT / config['stmp_source'])['configurations']['STMP']
    gp = read_json(ROOT / config['gp_configuration'])
    if gp != source_plans[0]['receiver_configuration']:
        raise ValueError('GP-MP must use the current matched white-trained binding')
    configurations = {'STMP': stmp, 'GP-MP': gp, 'Off-grid SBL (7)': 'src/configs/final/offgrid_sbl.json'}
    for budget in (13, 25):
        configurations[f'Off-grid SBL ({budget})'] = source_plans[1]['configurations'][str(budget)]
    budget13 = read_json(ROOT / configurations['Off-grid SBL (13)'])
    assets = {}
    for source in source_plans:
        for name, digest in source['assets'].items():
            path = (ROOT / name).resolve()
            checked(path, digest)
            assets[str(path)] = digest
    # Include STMP's exact weights/settings and every inherited STMP source.
    for key, value in stmp.items():
        if isinstance(value, str) and key + '_sha256' in stmp:
            path = ROOT / value
            checked(path, stmp[key + '_sha256'])
            assets[str(path.resolve())] = stmp[key + '_sha256']
    paths = [config_path, ROOT / config['stmp_source'], ROOT / config['gp_configuration'],
             white / 'PLAN.json', sbl / 'PLAN.json', white / 'INPUTS.json', sbl / 'INPUTS.json']
    paths += list(Path(__file__).parent.glob('*.py')) + list((ROOT / 'src/receiver/stmp').rglob('*.py'))
    for path in paths:
        assets[str(path.resolve())] = sha256(path)
    plan = dict(config, scene_ids=scenes, inputs=inputs, configurations=configurations, assets=assets,
                activity_readout=budget13['activity_readout'], activity_policy=budget13['activity_policy'],
                planned_inferences=len(scenes) * len(METHODS), created_at=datetime.now().astimezone().isoformat(),
                stopping_policy='Run all actual iterations; keep native stopping diagnostics; no padding',
                scoring='Sum per-user squared errors / sum active signal energy, then convert to dB; pooled AER',
                truth_used_in_inference=False,
                observer_note='Truth is used only by the passive trajectory scorer; never by receiver updates',
                timing_note='Timing includes scoring and extra SBL posterior reconstruction; not a runtime benchmark')
    output.mkdir(parents=True)
    write_json(output / 'PLAN.json', plan)
    write_json(output / 'PLAN_HASH.json', dict(sha256=sha256(output / 'PLAN.json')))
    write_json(output / 'STATUS.json', dict(stage='PREPARED', completed=0, total=plan['planned_inferences'],
                                          inference_started=False))
    return plan


def verify(output, *, inputs=True):
    checked(output / 'PLAN.json', read_json(output / 'PLAN_HASH.json')['sha256'])
    plan = read_json(output / 'PLAN.json')
    for path, digest in plan['assets'].items():
        checked(path, digest)
    if inputs:
        for case in plan['inputs']:
            check_input(case)
    return plan


def worker(output, method, scene):
    plan = verify(output, inputs=False)
    execution = execution_identity()
    if method not in plan['methods'] or scene not in plan['scene_ids']:
        raise ValueError('Case outside frozen plan')
    case = next(r for r in plan['inputs'] if r['scene'] == scene)
    check_input(case)
    dest = output / 'cases' / case_name(method, scene)
    dest.mkdir(parents=True, exist_ok=False)
    write_json(dest / 'START.json', dict(method=method, scene=scene, pid=os.getpid(), started_unix=time.time(), execution=execution))
    collector = None
    try:
        import numpy as np
        import torch
        from threadpoolctl import threadpool_limits
        from channel.observation import ReceiverInput
        from .adapters import infer_mp, infer_sbl
        from .metrics import Collector

        torch.set_num_threads(plan['runtime']['threads'])
        torch.set_num_interop_threads(1)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
        folder = Path(case['ready']).parent
        with np.load(folder / 'public.npz', allow_pickle=False) as data:
            inputs = ReceiverInput(data['y'], data['a'], 1., float(data['rho']))
        with np.load(folder / 'truth.npz', allow_pickle=False) as data:
            collector = Collector(data, plan['iterations'])
        started = time.perf_counter()
        with threadpool_limits(limits=plan['runtime']['threads']):
            infer = infer_mp if method in ('STMP', 'GP-MP') else infer_sbl
            arrays, record = infer(method, plan, inputs, collector)
        if not all(np.isfinite(v).all() for v in arrays.values()):
            raise FloatingPointError('Nonfinite final prediction')
        collector.verify_final(arrays)
        if record['iterations'] != plan['iterations']:
            raise ValueError('Native solver did not execute the full iteration budget')
        diagnostics = [r['iteration'] for r in collector.rows if r['native_would_stop']]
        record.update(stopping_reason='FIXED_ITERATIONS', converged=bool(diagnostics and diagnostics[-1] == plan['iterations']),
                      native_first_stop_iteration=diagnostics[0] if diagnostics else None,
                      early_stopping_enabled=False, truth_used_in_inference=False,
                      phase_mode=plan['phase_mode'], noise_mode=plan['noise_mode'], tf32=False,
                      total_seconds_including_observers=time.perf_counter() - started)
        np.savez_compressed(dest / 'FINAL.npz', **arrays)
        np.savez_compressed(dest / 'TRACE.npz', **collector.arrays())
        write_json(dest / 'TRACE.json', collector.rows)
        write_json(dest / 'RECORD.json', record)
        names = ('FINAL.npz', 'TRACE.npz', 'TRACE.json', 'RECORD.json')
        write_json(dest / 'RESULT.json', dict(status='COMPLETE', method=method, scene=scene,
            iterations=plan['iterations'], input_hashes=case['files'],
            plan_sha256=sha256(output / 'PLAN.json'), files={n: sha256(dest / n) for n in names}))
    except BaseException:
        if collector is not None:
            import numpy as np
            np.savez_compressed(dest / 'PARTIAL_TRACE.npz', **collector.arrays())
        write_json(dest / 'FAILURE.json', dict(status='FAILED', traceback=traceback.format_exc(), automatic_retry=False))
        raise


def load_case(output, plan, method, scene):
    import numpy as np
    dest = output / 'cases' / case_name(method, scene)
    result = read_json(dest / 'RESULT.json')
    case = next(r for r in plan['inputs'] if r['scene'] == scene)
    if (result['status'] != 'COMPLETE' or result['method'] != method or result['scene'] != scene
            or result['iterations'] != plan['iterations'] or result['input_hashes'] != case['files']
            or result['plan_sha256'] != sha256(output / 'PLAN.json')):
        raise ValueError('Case does not match the paired frozen plan')
    for name, digest in result['files'].items():
        checked(dest / name, digest)
    with np.load(dest / 'TRACE.npz', allow_pickle=False) as data:
        return {key: data[key] for key in data.files}


def summarize(output):
    import numpy as np
    from .metrics import aggregate
    plan = verify(output)
    curves, paired = {}, {}
    for method in plan['methods']:
        traces = {s: load_case(output, plan, method, s) for s in plan['scene_ids']}
        for scene, trace in traces.items():
            if scene in paired:
                np.testing.assert_array_equal(trace['truth_activity'], paired[scene][0])
                np.testing.assert_equal(trace['signal_energy'], paired[scene][1])
            else:
                paired[scene] = (trace['truth_activity'], trace['signal_energy'])
        data = aggregate(traces, plan['scene_ids'], plan['iterations'])
        curves[method] = {k: v.tolist() if isinstance(v, np.ndarray) else v for k, v in data.items()}
    write_json(output / 'SUMMARY.json', dict(status='COMPLETE', scenes=plan['scene_count'],
        iterations=plan['iterations'], snr_db=plan['snr_db'], phase_mode=plan['phase_mode'],
        noise_mode=plan['noise_mode'], plan_sha256=sha256(output / 'PLAN.json'), curves=curves))
    return curves


def coordinate(output):
    plan = verify(output)
    lock = output / 'RUNNING.lock'
    with lock.open('x') as handle:
        handle.write(str(os.getpid()))
    process, completed = None, 0
    try:
        for scene in plan['scene_ids']:
            for method in plan['methods']:
                name = case_name(method, scene)
                dest = output / 'cases' / name
                if dest.exists():
                    # Complete cases can resume; a partial/failed attempt is never overwritten.
                    load_case(output, plan, method, scene)
                    completed += 1
                    continue
                logs = output / 'logs'
                logs.mkdir(exist_ok=True)
                command = [sys.executable, '-X', 'utf8', '-B', str(ROOT / 'run_experiments.py'),
                           'convergence', 'worker', '--output', str(output), '--method', method, '--scene', str(scene)]
                env = dict(os.environ, PYTHONPATH=str(ROOT / 'src'), OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                           OPENBLAS_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1')
                if method.startswith('Off-grid'):
                    env['CUDA_VISIBLE_DEVICES'] = ''
                with (logs / (name + '.out')).open('x') as stdout, (logs / (name + '.err')).open('x') as stderr:
                    process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=stdout, stderr=stderr,
                                               creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                    write_json(output / 'STATUS.json', dict(stage='RUNNING', completed=completed,
                        total=plan['planned_inferences'], active=name, worker_pid=process.pid, pid=os.getpid()))
                    code = process.wait()
                if code:
                    raise RuntimeError(f'{name} failed with exit code {code}; no automatic retry')
                load_case(output, plan, method, scene)
                completed += 1
                print(json.dumps(dict(completed=completed, total=plan['planned_inferences'], last=name)), flush=True)
        summarize(output)
        write_json(output / 'STATUS.json', dict(stage='COMPLETE', completed=completed, total=plan['planned_inferences']))
    except BaseException:
        if process is not None and process.poll() is None:
            process.terminate()
            process.wait()
        write_json(output / 'STATUS.json', dict(stage='STOPPED', completed=completed, total=plan['planned_inferences'],
            traceback=traceback.format_exc(), automatic_retry=False))
        raise
    finally:
        lock.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description='50 paired scenes, 300 actual iterations; explicit execution only')
    parser.add_argument('command', choices=['plan', 'inspect', 'run', 'summarize', 'worker'])
    parser.add_argument('--config', type=Path, default=CONFIG)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--method', choices=METHODS)
    parser.add_argument('--scene', type=int)
    args = parser.parse_args(argv)
    output = (args.output or ROOT / read_json(args.config)['output']).resolve()
    if args.command == 'plan':
        plan = prepare(output, args.config)
    elif args.command == 'inspect':
        plan = verify(output)
    elif args.command == 'run':
        return coordinate(output)
    elif args.command == 'summarize':
        summarize(output)
        return
    else:
        if args.method is None or args.scene is None:
            parser.error('worker requires --method and --scene')
        return worker(output, args.method, args.scene)
    print(json.dumps(dict(status='PREPARED' if args.command == 'plan' else 'VERIFIED',
                         scenes=len(plan['scene_ids']), iterations=plan['iterations'],
                         inferences=plan['planned_inferences'], methods=plan['methods'], inference_started=False)))


if __name__ == '__main__':
    main()
