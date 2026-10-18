#!/usr/bin/env python3
"""CPU-only replay of preserved observations; frozen algorithms are imported intact."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
import warnings

# Set limits before importing numerical libraries, regardless of caller environment.
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
            'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
os.environ['MPLBACKEND'] = 'Agg'
ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'experiment')]
if os.name == 'nt':
    raise SystemExit('Use WSL2/Linux on Windows: frozen receiver signatures require POSIX paths. See README_9900X.md.')
import numpy as np
import torch
from threadpoolctl import threadpool_limits, threadpool_info
import _common as common
from _support import pairing
from afdm_jadcedd.algorithm.unknown_phase_model import UnknownPhaseInput
from afdm_jadcedd.system.observation import ReceiverInput, array_sha256

BASELINES = ['offgrid_sbl', 'gnn', 'gamp', 'somp']
CASE_INDEX = None
read, save, sha, arrays, save_arrays = common.read, common.save, common.sha, common.arrays, common.save_arrays


def rooted(base, name):
    path = (base / name).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError('Nonportable or escaping manifest path: ' + str(name))
    return path


def verify_manifest(path, base):
    manifest = read(path)
    if not manifest.get('files'):
        raise ValueError('Empty manifest: ' + str(path))
    for name, digest in manifest['files'].items():
        if sha(rooted(base, name)) != digest:
            raise ValueError('File differs from manifest: ' + name)
    return manifest


def verify_sources(job):
    global CASE_INDEX
    manifest = verify_manifest(ROOT / 'SOURCE_MANIFEST.json', ROOT)
    if 'inputs/INDEX.json' not in manifest['files']:
        raise ValueError('Input index is absent from the source manifest')
    CASE_INDEX = read(ROOT / 'inputs' / 'INDEX.json')['experiments']
    plan_path = ROOT / 'inputs' / job / 'PLAN.json'
    plan = read(plan_path)
    spec = plan['experiment']
    indexed = CASE_INDEX[job]
    expected_cases = {f'scene{s:03d}/condition{i:02d}' for s in range(spec['scenes'])
                      for i in range(len(spec['values']))}
    if (indexed['source_plan_sha256'] != sha(plan_path) or
            indexed['conditions'] != len(expected_cases) or set(indexed['cases']) != expected_cases):
        raise ValueError('Input index does not cover the complete original plan')
    if spec['methods'] != BASELINES or spec['device'] != 'cpu':
        raise ValueError('Expected frozen CPU plan with exactly the four baselines')
    if spec['variable'] != {'user_count': 'users', 'cross_channel': 'channel_model'}[job]:
        raise ValueError('Wrong experiment plan')
    # The old plan also references Proposed assets, which are not needed in this
    # CPU package. Never edit that plan or claim its complete asset set was tested.
    for name, digest in plan['source_and_weight_sha256'].items():
        if name.startswith('models/proposed/'):
            continue
        if manifest['files'].get(name) != digest:
            raise ValueError('Portable source differs from original plan: ' + name)
    if manifest['files'].get(plan_path.relative_to(ROOT).as_posix()) != sha(plan_path):
        raise ValueError('Original plan is absent from the source manifest')
    if manifest['files'].get('run_cpu.py') != sha(ROOT / 'run_cpu.py'):
        raise ValueError('Runner is absent from the source manifest')
    inherited_key = f'results/{job}/INHERITED_RESULTS.json'
    if (ROOT / inherited_key).exists() and inherited_key not in manifest['files']:
        raise ValueError('Inherited-result identity is absent from the source manifest')
    common.validate(spec)
    return plan


def load_case(job, spec, scene, index):
    folder = ROOT / 'inputs' / job / f'scene{scene:03d}' / f'condition{index:02d}'
    key = f'scene{scene:03d}/condition{index:02d}'
    if sha(folder / 'CASE.json') != CASE_INDEX[job]['cases'][key]:
        raise ValueError('Case manifest changed: ' + str(folder))
    record = read(folder / 'CASE.json')
    if record['seed'] != spec['seed'] + scene or record['parameters'] != common.condition(spec, spec['values'][index]):
        raise ValueError('Case identity differs: ' + str(folder))
    for name in ('public.npz', 'truth.npz'):
        if sha(folder / name) != record['files'][name]:
            raise ValueError('Saved input changed: ' + str(folder / name))
    public, truth = arrays(folder / 'public.npz'), arrays(folder / 'truth.npz')
    inputs = UnknownPhaseInput(**public)
    hashes = {k: array_sha256(v) for k, v in inputs.arguments().items()}
    if record['arrays'] != hashes:
        raise ValueError('Public input array hashes differ: ' + str(folder))
    if 'truth_arrays' in record and record['truth_arrays'] != {k: array_sha256(v) for k, v in truth.items()}:
        raise ValueError('Scoring truth array hashes differ: ' + str(folder))
    if float(inputs.noise_variance) != 1.:
        raise ValueError('Expected unused noise variance placeholder=1')
    return inputs, truth, record['generation'], hashes


def verify_existing(folder, inputs, truth, metadata, hashes, scene, index):
    if not folder.exists():
        return
    method_files = [folder / f'{m}.json' for m in BASELINES]
    if not any(p.exists() for p in method_files):
        return
    stored = pairing.verify(folder)
    if stored['generation'] != metadata:
        raise ValueError('Existing generation metadata differs: ' + str(folder))
    for name, expected in [('public.npz', inputs.arguments()), ('truth.npz', truth)]:
        actual = {k: array_sha256(v) for k, v in arrays(folder / name).items()}
        if actual != {k: array_sha256(v) for k, v in expected.items()}:
            raise ValueError('Existing pairing differs from preserved test input: ' + str(folder))
    if read(folder / 'INPUT.json')['arrays'] != hashes:
        raise ValueError('Existing input record differs')
    for path in method_files:
        if path.exists():
            record = read(path)
            if (record['scene'], record['condition'], record['method']) != (scene, index, path.stem):
                raise ValueError('Existing result identity differs: ' + str(path))
            if record['input_array_sha256'] != hashes or record['truth_used_in_inference'] is not False:
                raise ValueError('Existing result input identity differs: ' + str(path))
    common.pending_methods(folder, BASELINES)  # Reject changed outputs and preserved failures.


def verify_inherited(job, plan):
    out = ROOT / 'results' / job
    path = out / 'INHERITED_RESULTS.json'
    if not path.exists():
        if (out / 'scene000').exists() and not (out / 'RUN_PLAN.json').exists():
            raise ValueError('Preexisting results need INHERITED_RESULTS.json')
        return
    record = verify_manifest(path, out)
    if record['source_plan_sha256'] != sha(ROOT / 'inputs' / job / 'PLAN.json'):
        raise ValueError('Inherited result plan differs')
    for index in range(len(plan['experiment']['values'])):
        inputs, truth, metadata, hashes = load_case(job, plan['experiment'], 0, index)
        verify_existing(out / 'scene000' / f'condition{index:02d}', inputs, truth, metadata, hashes, 0, index)


def run_identity(job, plan, smoke, conditions):
    return dict(schema='portable-cpu-run-v1', experiment=job,
        original_plan_sha256=sha(ROOT / 'inputs' / job / 'PLAN.json'),
        source_manifest_sha256=sha(ROOT / 'SOURCE_MANIFEST.json'),
        runner_sha256=sha(ROOT / 'run_cpu.py'), methods=BASELINES,
        device='cpu', threads=1, mode='smoke' if smoke else 'formal',
        conditions=conditions if smoke else list(range(len(plan['experiment']['values']))),
        observation_source='Preserved public.npz; no regeneration',
        omitted_original_plan_assets='models/proposed/*; not required by these baselines')


def environment():
    import scipy, matplotlib
    return dict(python=sys.version, platform=platform.platform(), machine=platform.machine(),
        packages=dict(numpy=np.__version__, scipy=scipy.__version__, torch=torch.__version__,
                      matplotlib=matplotlib.__version__), device='cpu', threads=1,
        threadpools=threadpool_info(), recorded_unix=time.time())


def execute(job, plan, out, *, smoke=False, conditions=None, max_scenes=None):
    spec = dict(plan['experiment'], device='cpu')
    indices = conditions if conditions is not None else list(range(len(spec['values'])))
    nscenes = 1 if smoke else min(max_scenes or spec['scenes'], spec['scenes'])
    if smoke and out.exists():
        raise FileExistsError('Smoke requires a new output directory: ' + str(out))
    out.mkdir(parents=True, exist_ok=True)
    lock = out / 'RUNNING.lock'
    descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    os.write(descriptor, json.dumps(dict(pid=os.getpid(), host=platform.node(), started=time.time())).encode())
    os.close(descriptor)
    try:
        identity = run_identity(job, plan, smoke, indices)
        target = out / 'RUN_PLAN.json'
        if target.exists() and read(target) != identity:
            raise ValueError('Existing run belongs to another input/source/runner plan')
        save(target, identity)
        envfile = out / 'environments' / f'{time.time_ns()}_{os.getpid()}.json'
        controls = common.phase.Controls(**read(ROOT / spec['phase_config'])['phase_estimation'])
        torch.set_num_threads(1)
        torch.set_num_interop_threads(1)
        completed = 0
        with threadpool_limits(1):
            save(envfile, environment())
            solvers = {method: common.solver(method, spec) for method in BASELINES}
            for scene in range(nscenes):
                for index in indices:
                    inputs, truth, metadata, hashes = load_case(job, spec, scene, index)
                    folder = out / f'scene{scene:03d}' / f'condition{index:02d}'
                    verify_existing(folder, inputs, truth, metadata, hashes, scene, index)
                    if (folder / 'FRONTEND_FAILURE.json').exists():
                        raise ValueError('Preserved frontend failure requires inspection: ' + str(folder))
                    pending = common.pending_methods(folder, BASELINES)
                    if not pending:
                        continue
                    save(folder / 'INPUT.json', dict(arrays=hashes, generation=metadata))
                    try:
                        values, phase_record = common.estimated_phase(inputs, folder, controls)
                        conditional = inputs.at_estimated_phase(values['phase_slopes'])
                        conditional = ReceiverInput(conditional.observation, conditional.operator, 1., conditional.activity_prior)
                        pairing.preserve(folder, inputs, conditional, truth, metadata)
                    except Exception:
                        save(folder / 'FRONTEND_FAILURE.json', dict(status='FAILED', traceback=traceback.format_exc()))
                        raise
                    for method in pending:
                        base = dict(scene=scene, condition=index, method=method,
                            input_array_sha256=hashes, phase_mode='estimated', noise_mode='estimated',
                            truth_used_in_inference=False, execution_device='cpu',
                            environment=str(envfile.relative_to(out)))
                        target = folder / f'{method}.json'
                        try:
                            with warnings.catch_warnings(record=True) as notices:
                                warnings.simplefilter('always', RuntimeWarning)
                                prediction, record = solvers[method].infer(conditional)
                            if record.get('status', 'COMPLETE') != 'COMPLETE' or not all(np.isfinite(v).all() for v in prediction.values()):
                                raise FloatingPointError('Incomplete or nonfinite receiver output')
                            metrics = common.score_arrays(prediction, truth)
                            compact = {k:v for k,v in prediction.items() if np.asarray(v).ndim <= 1}
                            compact.update(per_user_error=np.asarray(metrics['per_user_error']), truth_activity=truth['activity'])
                            save_arrays(target.with_suffix('.npz'), compact)
                            if scene == 0:
                                save_arrays(folder / f'{method}.prediction.npz', prediction)
                            save(folder / f'{method}.record.json', record)
                            save(target, dict(base, status='COMPLETE', metrics=metrics,
                                receiver_seconds=record['seconds'], phase_seconds=phase_record['seconds'],
                                compact_sha256=sha(target.with_suffix('.npz')),
                                iterations=record['iterations'], stopping_reason=record['stopping_reason'],
                                output_array_sha256={k:array_sha256(v) for k,v in prediction.items()},
                                warnings=[str(w.message) for w in notices]))
                        except Exception:
                            save(target, dict(base, status='FAILED', traceback=traceback.format_exc()))
                            raise
                        completed += 1
                        print(f'{job} scene={scene:03d} condition={index:02d} {method} COMPLETE', flush=True)
        verify_sources(job)
        if smoke:
            save(out / 'SMOKE.json', dict(status='COMPLETE', newly_computed_results=completed,
                conditions=indices, scenes=1, timing='Smoke results are separate from formal results.'))
            print(json.dumps(dict(status='SMOKE_COMPLETE', newly_computed_results=completed, output=str(out))))
            return 0
        result = summarize(job, out, spec)
        return result if nscenes == spec['scenes'] else 0
    finally:
        lock.unlink(missing_ok=True)


def summarize(job, out, spec):
    plotter = None
    if job == 'cross_channel':
        from cross_channel import plot_profiles
        plotter = plot_profiles
    status = common.summarize(out, spec, plotter=plotter)
    summary = read(out / 'SUMMARY.json')
    inherited = 0
    if (out / 'INHERITED_RESULTS.json').exists():
        manifest = read(out / 'INHERITED_RESULTS.json')
        for name in manifest['files']:
            path = Path(name)
            if path.suffix == '.json' and path.stem in BASELINES:
                inherited += read(out / path)['status'] == 'COMPLETE'
    completed = sum(row['completed'] for row in summary['rows'])
    summary.update(inherited_completed_results=inherited,
        completed_by_portable_runner=completed-inherited,
        reuse_count_scope='reused_results/newly_computed_results retain the original historical-reuse convention; newly_computed_results includes inherited first-scene results. The two portable counters distinguish transfer reuse.')
    save(out / 'SUMMARY.json', summary)
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['check', 'smoke', 'run', 'summarize'])
    parser.add_argument('--experiment', choices=['user_count', 'cross_channel'], required=True)
    parser.add_argument('--conditions', nargs='+', type=int, help='Smoke only: original zero-based condition indices')
    parser.add_argument('--max-scenes', type=int, help='Run/check only: inspect or execute the first N scenes')
    parser.add_argument('--output', type=Path, help='Smoke only: new isolated output directory')
    args = parser.parse_args()
    if args.conditions is not None and args.command != 'smoke':
        parser.error('--conditions is smoke-only')
    if args.output is not None and args.command != 'smoke':
        parser.error('--output is smoke-only; formal output is fixed by experiment')
    if args.max_scenes is not None and (args.max_scenes < 1 or args.command not in ('run', 'check')):
        parser.error('--max-scenes must be positive and used with run/check')
    plan = verify_sources(args.experiment)
    spec = plan['experiment']
    if args.conditions is not None and (len(set(args.conditions)) != len(args.conditions) or
            any(i < 0 or i >= len(spec['values']) for i in args.conditions)):
        parser.error('Distinct condition indices in plan range required')
    verify_inherited(args.experiment, plan)
    if args.command == 'check':
        count = 0
        for scene in range(min(args.max_scenes or spec['scenes'], spec['scenes'])):
            for index in range(len(spec['values'])):
                load_case(args.experiment, spec, scene, index)
                count += 1
        print(json.dumps(dict(status='CHECK_PASSED', experiment=args.experiment, verified_cases=count)))
        return 0
    out = ROOT / 'results' / args.experiment
    if args.command == 'summarize':
        return summarize(args.experiment, out, spec)
    if args.command == 'smoke':
        out = (args.output or (ROOT / 'results' / f'smoke_{args.experiment}_{time.time_ns()}')).resolve()
    return execute(args.experiment, plan, out, smoke=args.command == 'smoke',
                   conditions=args.conditions, max_scenes=args.max_scenes)


if __name__ == '__main__':
    raise SystemExit(main())
