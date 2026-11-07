"""Final experiments with independent phase/noise modes and paired scene subsets."""
from pathlib import Path
from dataclasses import asdict
from contextlib import contextmanager
from datetime import datetime
from datetime import timezone
import argparse
import gc
import json
import os
import sys
import time
import traceback

import numpy as np

HERE = Path(__file__).resolve().parent
from workspace import ROOT
from workspace import CONFIGS
from workspace import source_files
from workspace import physical_source_files
from scenario.catalog import condition_key
from scenario.catalog import DEFAULT
from scenario.catalog import REGISTRY
from experiment.runtime import setup
from experiment.runtime import synchronize
from experiment.runtime import activate
from experiment.runtime import network_modules
from experiment.runtime import parameter_count
from experiment.runtime import backend
from experiment import experiments
from receiver import registry as algorithms
from experiment.observations import observation
from experiment.observations import estimated_phase
from experiment.storage import save_arrays
from experiment.storage import arrays
from fileio import read_json
from fileio import write_json
from fileio import sha256
from fileio import json_digest
from channel.observation import ReceiverInput
from channel.observation import array_sha256
from channel.phase import phase_operator
from channel.unknown_phase import UnknownPhaseInput
from receiver.frontend import phase_estimation as phase
from experiment.metrics import score_arrays
from scenario.profiles import generate_profile_case

NAMES = experiments.NAMES
PANEL_HASH = '025b7732b7396d32318acfe1c5f9baea21210ec81328ba075a8dfa4da852af2f'
DEFAULT_OUTPUT = ROOT / 'result/organized_default_20261107'
SMOKE_SEED = 202610219900001


def assets(binding, definitions, config_path, device):
    files = {CONFIGS / 'organized/models.json', REGISTRY / 'PLAN.json', REGISTRY / 'SCENES.csv',
             REGISTRY / 'SEED_SEPARATION.json', REGISTRY / 'PAIRING_CHECK.json'}
    files.update(source_files())
    files.update((ROOT / 'src/configs/final').glob('*.json'))
    files.add(ROOT / 'run_experiments.py')
    files.add(config_path)
    for spec in definitions.values():
        files.update(algorithms.source_files(spec, binding, device))
    return {str(p.resolve()): sha256(p) for p in sorted(files)}


def verify(plan):
    for name, expected in plan['assets'].items():
        if sha256(name) != expected:
            raise ValueError('Frozen evaluation asset changed: '+name)


def experiment_config(name, path=None):
    path = Path(path or CONFIGS / 'experiments' / (name+'.json')).resolve()
    config = read_json(path)
    if config.get('schema') != 'afdm-experiment-v1' or config.get('experiment') != name:
        raise ValueError('Wrong experiment configuration: '+str(path))
    if config['execution_status'] not in ('READY', 'DEFERRED_BY_USER'):
        raise ValueError('Unknown experiment execution status')
    return path, config


def selections(name, args, config=None):
    if config is None:
        _, config = experiment_config(name, getattr(args, 'config', None))
    return experiments.get(name).conditions(config, args)


def make_plan(name, args):
    if sha256(REGISTRY / 'PLAN.json') != PANEL_HASH:
        raise ValueError('The user-confirmed 2000-scene policy changed')
    out = args.output or DEFAULT_OUTPUT / name
    out = out.resolve()
    if out.exists() and any(out.iterdir()):
        raise FileExistsError('A new plan needs an empty directory: '+str(out))
    binding = algorithms.load_models()
    config_path, config = experiment_config(name, args.config)
    entry = experiments.get(name)
    definitions = algorithms.load_catalog(args.catalog)
    methods = list(args.methods if args.methods is not None else config['methods'])
    include_stmp = args.include_stmp or config.get('include_stmp', False)
    if include_stmp and entry.KIND == 'receiver' and 'STMP' not in methods:
        methods = list(methods)+['STMP']
    phase_mode = args.phase_mode or config.get('phase_mode', 'estimated')
    noise_mode = args.noise_mode or config.get('noise_mode', 'estimated')
    if phase_mode not in ('known', 'estimated') or noise_mode not in ('known', 'estimated'):
        raise ValueError('Phase and noise modes must be known or estimated')
    if entry.KIND == 'denoiser':
        if args.phase_mode is not None or args.noise_mode is not None:
            raise ValueError('Phase/noise selection applies to receivers; AWGN denoising already uses known variance')
        selected = algorithms.select(methods, definitions, entry.KIND)
        phase_mode, noise_mode = 'not_applicable', 'known'
    else:
        selected = algorithms.select(methods, definitions, entry.KIND,
                                     noise_mode=noise_mode, phase_mode=phase_mode)
    status = 'READY' if include_stmp else config['execution_status']
    if status == 'READY' and not include_stmp and any(s.get('requires_stmp_opt_in') for s in selected.values()):
        raise ValueError('STMP execution is deferred; opt in with include_stmp only when requested again')
    # Evaluation uses the same fixed 1000-scene prefix for every experiment.
    # The remaining registry scenes are reserved for separately planned calibration.
    formal_count = 1000
    if type(config['scenes']) is not int or not 1 <= config['scenes'] <= formal_count:
        raise ValueError('Configured scene count is outside the fixed registry subset')
    repeats = config['timing_repeats']
    if not isinstance(repeats, int) or repeats < 1:
        raise ValueError('timing_repeats must be a positive integer')
    count = args.scenes if args.scenes is not None else (1 if args.smoke else config['scenes'])
    if not 1 <= count <= formal_count:
        raise ValueError('Scene count is outside the fixed registry subset')
    conditions = selections(name, args, config)
    if not conditions or len({json_digest(c) for c in conditions}) != len(conditions):
        raise ValueError('Distinct nonempty conditions required')
    for c in conditions:
        if entry.KIND == 'denoiser':
            if not .001 <= c['variance'] <= 100:
                raise ValueError('AWGN variance outside declared support')
        else:
            if c['users'] != int(c['users']) or c['frames'] != int(c['frames']):
                raise ValueError('Integer user/pilot counts required')
            c.update(users=int(c['users']), frames=int(c['frames']))
            if not 2 <= c['users'] <= 100 or not 1 <= c['frames'] <= 48 or not 0 < c['activity_probability'] < 1:
                raise ValueError('Invalid experimental condition')
    panel = read_json(REGISTRY / 'PLAN.json')
    runtime_assets = assets(binding, selected, config_path, args.device)
    cache = (args.cache or (out.parent / ('shared_smoke' if args.smoke else 'shared'))).resolve()
    # Experiment selection is not part of input/cache identity. Two experiments
    # with the same physical condition can still reuse the very same input.
    runtime_assets_for_cache = {p: h for p, h in runtime_assets.items() if p != str(config_path)}
    input_paths = physical_source_files()
    input_paths += [HERE/p for p in ('observations.py','storage.py')]
    input_paths += [ROOT/'src/fileio.py', ROOT/binding['phase_configuration']]
    input_identity = json_digest(dict(sources={str(p): sha256(p) for p in input_paths},
                                 scale=binding['STMP']['scale'], panel=PANEL_HASH,
                                 phase_mode=phase_mode, noise_mode=noise_mode))
    plan = dict(schema='afdm-configured-experiments-v1', experiment=name, experiment_kind=entry.KIND,
        experiment_config=config, configuration_file=str(config_path), algorithm_specs=selected,
        reference_method=config['reference_method'] if config['reference_method'] in methods else methods[0],
        extra_comparisons=[pair for pair in config.get('extra_comparisons', []) if all(m in methods for m in pair)],
        scene_count=count, base_seed=SMOKE_SEED if args.smoke else panel['base_seed'],
        formal_panel_sha256=PANEL_HASH, scene_registry=str(REGISTRY / 'SCENES.csv'),
        mode='SMOKE_ONLY' if args.smoke else ('FORMAL_1000' if count == formal_count else 'FORMAL_SUBSET'),
        scene_selection='diagnostic_seeds' if args.smoke else 'fixed_registry_prefix',
        execution_status=status,
        include_stmp=include_stmp, timing_repeats=repeats,
        conditions=conditions, methods=methods, model_binding=binding, assets=runtime_assets,
        input_identity=input_identity, runtime_identity=json_digest(runtime_assets_for_cache), device=args.device, threads=4, tf32=False,
        cache=str(cache), phase_mode=phase_mode, noise_mode=noise_mode,
        bootstrap_replicates=10000, bootstrap_seed=2026102198,
        timing='One warmup per method/shape, CUDA synchronization. Internal phase initialization/updates are included in receiver time; external frontend time is added separately. Cached results keep original timing.',
        ablation_scope='Controlled learned-vs-Gaussian-site evidence on STMP.',
        denoising_scope='Configured first-network means on paired known-variance AWGN queries; colored-trained networks use C=vI. No receiver layer, second score or activity network is evaluated.',
        amendments=['User requested 1000 MC scenes for all future experiments, including runtime comparison; registry IDs 0..999.',
                    'User requested pretrained first-score denoising only.', 'User deferred STMP three-network execution and its activity-evidence ablation.'],
        material_passport=dict(origin_skill='academic-research-suite / experiment-agent', origin_mode='run',
            origin_date=datetime.now(timezone.utc).date().isoformat(), verification_status='PLANNED',
            version_label='configured_experiments_v1'))
    write_json(out / 'PLAN.json', plan)
    write_json(out / 'PLAN_HASH.json', dict(sha256=sha256(out / 'PLAN.json')))
    print(json.dumps(dict(status='PLANNED', output=str(out), scenes=count, conditions=len(conditions),
                         methods=methods, phase_mode=phase_mode, noise_mode=noise_mode)), flush=True)
    return out, plan


@contextmanager
def lock(cache):
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / 'RUNNING.lock'
    with path.open('x', encoding='utf-8') as stream:
        json.dump(dict(pid=os.getpid(), created_unix=time.time(), command=sys.argv), stream)
    try:
        yield
    finally:
        path.unlink()


def prepared_case(plan, scene, condition, *, method=None):
    seed = plan['base_seed']+scene
    phase_mode, noise_mode = plan['phase_mode'], plan['noise_mode']
    internal = method is not None and plan['algorithm_specs'][method].get('phase_input') == 'raw'
    phase_input = 'raw' if internal else 'operator'
    mode_key = f'phase_{"internal" if internal else phase_mode}_noise_{noise_mode}'
    folder = Path(plan['cache']) / 'inputs' / f'{seed}' / condition_key(condition) / mode_key
    identity = dict(seed=seed, condition=condition, runtime=plan['input_identity'],
                    phase_mode=phase_mode, noise_mode=noise_mode, phase_input=phase_input)
    marker = folder / 'READY.json'
    if marker.exists():
        receipt = read_json(marker)
        if receipt['identity'] != identity:
            raise ValueError('Shared input runtime or physical condition changed')
        for name, expected in receipt['files'].items():
            if sha256(folder / name) != expected:
                raise ValueError('Shared input bytes changed')
        public = arrays(folder / 'public.npz')
        value = (UnknownPhaseInput(public['y'], public['a'], float(public['noise_variance']), float(public['rho']))
                 if internal else ReceiverInput(public['y'], public['a'], float(public['noise_variance']), float(public['rho'])))
        return (value,
                arrays(folder / 'truth.npz'), receipt, folder)
    scale = plan['model_binding']['STMP']['scale']
    raw, truth, meta = observation(seed, condition, scale, generator=generate_profile_case)
    if internal:
        fitted = dict(phase_slopes=np.zeros(raw.pilot.shape[1]))
        phase_record = dict(phase_mode='estimated', source='receiver_internal', seconds=0.,
                            initialized=False, note='Zero placeholder is not an estimate; receiver starts from raw pilots')
        save_arrays(folder / 'phase.npz', fitted)
        write_json(folder / 'PHASE.json', phase_record)
    elif phase_mode == 'known':
        fitted = dict(phase_slopes=truth['phase_slopes'])
        phase_record = dict(phase_mode='known', source='simulator_truth', seconds=0., oracle_phase_supplied=True)
        save_arrays(folder / 'phase.npz', fitted)
        write_json(folder / 'PHASE.json', phase_record)
    else:
        controls = phase.Controls(**read_json(ROOT / plan['model_binding']['phase_configuration'])['phase_estimation'])
        fitted, phase_record = estimated_phase(raw, folder, controls)
    noise_variance = meta['generated_noise_variance'] if noise_mode == 'known' else 1.
    operator = raw.pilot if internal else phase_operator(raw.pilot, fitted['phase_slopes'])
    public = (UnknownPhaseInput(raw.observation, operator, noise_variance, raw.activity_prior) if internal
              else ReceiverInput(raw.observation, operator, noise_variance, raw.activity_prior))
    save_arrays(folder / 'public.npz', dict(y=public.observation, a=operator, rho=public.activity_prior,
                                         noise_variance=public.noise_variance))
    save_arrays(folder / 'raw.npz', dict(y=raw.observation, pilot=raw.pilot, rho=raw.activity_prior))
    save_arrays(folder / 'truth.npz', truth)
    receipt = dict(identity=identity, generation=dict(meta, noise_mode=noise_mode, phase_mode=phase_mode),
                   phase_seconds=phase_record['seconds'],
                   files={n:sha256(folder/n) for n in ['public.npz','raw.npz','truth.npz','phase.npz','PHASE.json']})
    write_json(marker, receipt)
    return public, truth, receipt, folder


def method_case(plan, scene, condition, method):
    """Select raw pilots or a shared phase operator from the algorithm catalog."""
    if plan['algorithm_specs'][method].get('phase_input') == 'raw':
        return prepared_case(plan, scene, condition, method=method)
    return prepared_case(plan, scene, condition)


def checked_result(path, identity):
    if not path.exists():
        return None
    row = read_json(path)
    if row['identity'] != identity or row['status'] != 'COMPLETE' or sha256(path.with_suffix('.npz')) != row['compact_sha256']:
        raise ValueError('Changed or failed saved result: '+str(path))
    return row


def receiver_result(plan, model, method, scene, cond, public, truth, case, warmed):
    import torch
    identity = dict(runtime=plan['runtime_identity'], input=case['files'], method=method,
                    algorithm=json_digest(plan['algorithm_specs'][method]),
                    phase_mode=plan['phase_mode'], noise_mode=plan['noise_mode'],
                    device=plan['device'], repeats=plan['timing_repeats'], seed=plan['base_seed']+scene)
    path = Path(plan['cache']) / 'predictions' / (json_digest(identity)+'.json')
    row = checked_result(path, identity)
    if row is not None:
        return row, path
    shape = public.pilot.shape if isinstance(public, UnknownPhaseInput) else public.operator.shape
    warm_key = (method, shape)
    if warm_key not in warmed:
        # The deterministic warmup is disjoint from the formal evaluation panel.
        # Its outputs never participate in any statistical summary.
        probe = dict(plan, base_seed=SMOKE_SEED+80000)
        warm_public, _, _, _ = method_case(probe, 0, cond, method)
        model.infer(warm_public)
        warmed.add(warm_key)
    synchronize(plan['device'])
    if plan['device'] == 'cuda':
        torch.cuda.reset_peak_memory_stats()
    timings=[]
    reference_output=None
    for _ in range(plan['timing_repeats']):
        synchronize(plan['device'])
        start = time.perf_counter()
        output, record = model.infer(public)
        synchronize(plan['device'])
        timings.append(time.perf_counter()-start)
        if reference_output is None:
            reference_output={k:np.array(output[k],copy=True) for k in ('estimate','activity_decision')}
        else:
            np.testing.assert_allclose(output['estimate'],reference_output['estimate'],rtol=2e-6,atol=2e-7)
            np.testing.assert_array_equal(output['activity_decision'],reference_output['activity_decision'])
    elapsed = float(np.median(timings))
    record = dict(record, phase_mode=plan['phase_mode'], noise_information=plan['noise_mode'],
                  supplied_noise_variance_used=plan['noise_mode'] == 'known',
                  oracle_phase_supplied=plan['phase_mode'] == 'known',
                  oracle_noise_supplied=plan['noise_mode'] == 'known',
                  noise_truth_used=plan['noise_mode'] == 'known',
                  truth_used_in_inference='known' in (plan['phase_mode'], plan['noise_mode']))
    if not all(np.isfinite(v).all() for v in output.values()):
        raise FloatingPointError('Nonfinite output; scene retained as failure')
    metrics = score_arrays(output, truth)
    # Rescore from a serialized full prediction before retaining compact sufficient statistics.
    path.parent.mkdir(parents=True, exist_ok=True)
    full = path.with_suffix('.prediction.npz')
    save_arrays(full, dict(estimate=output['estimate'], activity_decision=output['activity_decision']))
    rescored = score_arrays(arrays(full), truth)
    if metrics != rescored:
        raise ValueError('Prediction serialization/rescoring mismatch')
    prediction_hash = sha256(full)
    compact = {k:np.asarray(v) for k,v in output.items() if np.asarray(v).ndim <= 1}
    compact.update(per_user_error=np.asarray(metrics['per_user_error']), truth_activity=truth['activity'])
    save_arrays(path.with_suffix('.npz'), compact)
    row = dict(status='COMPLETE', identity=identity, metrics=metrics,
        phase_mode=plan['phase_mode'], noise_mode=plan['noise_mode'],
        receiver_seconds=elapsed, phase_seconds=case['phase_seconds'], end_to_end_seconds=elapsed+case['phase_seconds'],
        timing_repeats_seconds=timings, backend=backend(model, plan['device']),
        parameter_count=parameter_count(model),
        iterations=record['iterations'], stopping_reason=record['stopping_reason'],
        peak_allocated_mib=(torch.cuda.max_memory_allocated()/2**20 if backend(model,plan['device'])=='cuda' else 0.) if plan['device']=='cuda' else None,
        compact_sha256=sha256(path.with_suffix('.npz')), prediction_sha256=prediction_hash,
        full_prediction_retained=scene==0, rescoring='PASSED',
        timing_scope=('Synchronized receiver including internal phase initialization and nine updates'
                      if plan['algorithm_specs'][method].get('phase_input') == 'raw' else
                      'Synchronized conditional receiver; cached shared phase listed separately'),
        phase_method=record.get('phase_method', 'supplied_operator'),
        diagnostics=record.get('diagnostics', []), selected_epoch=record.get('selected_epoch'))
    write_json(path.with_suffix('.record.json'), record)
    write_json(path, row)
    if scene != 0:
        full.unlink()  # Only this newly written scratch full prediction; compact evidence is retained.
    return row, path


def run(out, plan):
    import torch
    from threadpoolctl import threadpool_limits
    verify(plan)
    if any(s['factory'].startswith('algorithm.') for s in plan['algorithm_specs'].values()):
        raise ValueError('Historical plan requires its frozen implementation; see archive/frozen_reproduction_20261107/README.md. Create a new plan to use current code.')
    if plan['execution_status'] == 'DEFERRED_BY_USER':
        print(json.dumps(dict(status='DEFERRED_BY_USER',reason='This experiment is deferred by its configuration.')))
        return 0
    if (out / 'COMPLETE.json').exists():
        for name, expected in read_json(out / 'COMPLETE.json')['files'].items():
            if sha256(out / name) != expected:
                raise ValueError('Completed report changed: '+name)
        print(json.dumps(dict(status='ALREADY_COMPLETE',experiment=plan['experiment'])),flush=True)
        return 0
    device = setup(plan['device'])
    if device != plan['device']:
        raise ValueError('Execution device must be resolved when making the plan')
    with lock(Path(plan['cache'])), threadpool_limits(4):
        models, warmed = {}, set()
        try:
            for scene in range(plan['scene_count']):
                for index, cond in enumerate(plan['conditions']):
                    folder = out / f'scene{scene:04d}' / f'condition{index:02d}'
                    if plan['experiment_kind']=='denoiser':
                        results = experiments.get(plan['experiment']).evaluate_case(plan, models, scene, cond)
                        for row,path in results:
                            write_json(folder/(row['identity']['method']+'.json'), dict(result=str(path), sha256=sha256(path)))
                    else:
                        for method in plan['methods']:
                            public, truth, case, _ = method_case(plan,scene,cond,method)
                            if method not in models:
                                models[method] = algorithms.build_algorithm(method, binding=plan['model_binding'],
                                    device=device, definitions=plan['algorithm_specs'])
                            activate(models,method,device)
                            row,path = receiver_result(plan,models[method],method,scene,cond,public,truth,case,warmed)
                            write_json(folder/(method+'.json'), dict(result=str(path), sha256=sha256(path)))
                    write_json(out/'STATUS.json',dict(stage='RUNNING',pid=os.getpid(),scene=scene+1,condition=index+1,
                         scenes=plan['scene_count'], conditions=len(plan['conditions']), updated_unix=time.time()))
                    print(json.dumps(dict(experiment=plan['experiment'],scene=scene+1,condition=index+1,
                                          total_conditions=len(plan['conditions']))),flush=True)
            del models
            gc.collect()
            if device=='cuda':torch.cuda.empty_cache()
            verify(plan)
            return summarize(out,plan)
        except BaseException:
            write_json(out/'failures'/f'{time.time_ns()}.json',dict(status='FAILED',traceback=traceback.format_exc(),pid=os.getpid()))
            write_json(out/'STATUS.json',dict(stage='FAILED',pid=os.getpid(),updated_unix=time.time()))
            raise


def summarize(out, plan):
    from experiment.reporting import finish
    return finish(out,plan)


def main(name=None, argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['plan','run','summarize','inspect'])
    if name is None:parser.add_argument('--experiment',choices=NAMES,required=True)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--config',type=Path,help='Experiment JSON; applies when creating a plan')
    parser.add_argument('--catalog',type=Path,help='Algorithm catalog JSON; applies when creating a plan')
    parser.add_argument('--cache',type=Path)
    parser.add_argument('--device',choices=['cuda','cpu','auto'],default='cuda')
    parser.add_argument('--smoke',action='store_true',help='Use separate diagnostic seeds, never the formal panel')
    parser.add_argument('--scenes',type=int,help='Use the first N paired registry scenes (diagnostic seeds with --smoke)')
    parser.add_argument('--phase-mode',choices=['known','estimated'],help='Use true phase or estimate phase; default: estimated')
    parser.add_argument('--noise-mode',choices=['known','estimated'],help='Supply true noise variance or estimate it; default: estimated')
    parser.add_argument('--values',type=float,nargs='+')
    parser.add_argument('--snr',type=float,nargs='+')
    parser.add_argument('--profiles',choices=['A','B','C','D'],nargs='+')
    parser.add_argument('--include-stmp',action='store_true',help='Opt in to the currently deferred STMP receiver')
    parser.add_argument('--methods',nargs='+',help='Override the configured method IDs when creating a plan')
    args=parser.parse_args(argv)
    name = name or args.experiment
    if args.command=='plan':
        if args.device=='auto':
            import torch
            args.device='cuda' if torch.cuda.is_available() else 'cpu'
        make_plan(name,args)
        return 0
    if any(value is not None for value in (args.config,args.catalog,args.methods,args.values,args.snr,args.profiles,args.scenes,args.phase_mode,args.noise_mode)) or args.include_stmp or args.smoke or args.cache:
        parser.error('Selection options apply to plan only; create a plan in a new output directory, then run it')
    out=(args.output or DEFAULT_OUTPUT/name).resolve()
    if read_json(out/'PLAN_HASH.json')['sha256'] != sha256(out/'PLAN.json'):
        raise ValueError('Saved plan changed')
    plan=read_json(out/'PLAN.json')
    if plan['experiment'] != name:raise ValueError('Wrong entrypoint for saved plan')
    if args.command=='inspect':
        verify(plan)
        print(json.dumps(dict(status=plan['execution_status'],mode=plan['mode'],scenes=plan['scene_count'],methods=plan['methods'],
                              phase_mode=plan['phase_mode'],noise_mode=plan['noise_mode'])))
        return 0
    return run(out,plan) if args.command=='run' else summarize(out,plan)


if __name__=='__main__':
    raise SystemExit(main())
