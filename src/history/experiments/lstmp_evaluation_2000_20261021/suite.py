"""Current eight-experiment entrypoint, sharing the fixed 2000-scene registry."""
from pathlib import Path
from dataclasses import asdict
from contextlib import contextmanager
import argparse
import csv
import gc
import hashlib
import json
import os
import sys
import time
import traceback

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'experiment'))
from shared_scenes import condition_key, DEFAULT, SWEEPS, OUTPUT as REGISTRY
from receivers import build, setup, synchronize, LABELS, activate, network_modules, parameter_count
from _common import observation, estimated_phase
from _support.storage import save_arrays, arrays
from afdm_jadcedd.system.observation import ReceiverInput, array_sha256
from afdm_jadcedd.algorithm.unknown_phase_model import UnknownPhaseInput
from afdm_jadcedd.algorithm import phase_estimation_optimized as phase
from afdm_jadcedd.experiment.evaluation.metrics import score_arrays
from cross_channel import generate_profile_case
import channel_denoising as denoising

NAMES = list(SWEEPS) + ['runtime_comparison', 'channel_denoising', 'cross_channel', 'density_ratio_ablation']
PANEL_HASH = '025b7732b7396d32318acfe1c5f9baea21210ec81328ba075a8dfa4da852af2f'
DEFAULT_OUTPUT = ROOT / 'results/lstmp_v3_formal2000_20261021'
SMOKE_SEED = 202610219900001


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f'.{os.getpid()}.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    temp.replace(path)


def assets(binding):
    files = {HERE / 'models.json', REGISTRY / 'PLAN.json', REGISTRY / 'SCENES.csv',
             REGISTRY / 'SEED_SEPARATION.json', REGISTRY / 'PAIRING_CHECK.json'}
    for directory, pattern in [('src', '*.py'), ('configs', '*.json'), ('experiment', '*.py'),
                               ('models/gnn', '*')]:
        files.update(p for p in (ROOT / directory).rglob(pattern) if p.is_file())
    files.update(HERE.glob('*.py'))
    c = binding['legacy_configuration']
    for key in ('first_checkpoint', 'second_checkpoint', 'evidence_checkpoint', 'prior_definition'):
        p = ROOT / c[key]
        if sha(p) != c[key+'_sha256']:
            raise ValueError('Legacy asset changed: '+str(p))
        files.add(p)
    spec = binding['ten_layer']
    run = Path(spec['run'])
    complete = read(run / 'COMPLETE.json')
    if (complete['completed_updates'] != 142500 or complete['selected_sha256'] != spec['checkpoint_sha256']
            or (run / 'RUNNING.lock').exists() or sha(spec['checkpoint']) != spec['checkpoint_sha256']):
        raise ValueError('Completed ten-layer training and selected weights must agree')
    files.update((Path(spec['checkpoint']), run / 'COMPLETE.json', run / 'MANIFEST.json', Path(spec['config'])))
    for folder in ('source_code', 'source_project'):
        files.update((run / folder).rglob('*.py'))
    return {str(p.resolve()): sha(p) for p in sorted(files)}


def verify(plan):
    for name, expected in plan['assets'].items():
        if sha(name) != expected:
            raise ValueError('Frozen evaluation asset changed: '+name)


def selections(name, args):
    if name in SWEEPS:
        field, defaults = SWEEPS[name]
        values = args.values if args.values is not None else defaults
        return [dict(DEFAULT, **{field: v}) for v in values]
    if name == 'cross_channel':
        return [dict(DEFAULT, channel_model=p, snr_db=v) for p in (args.profiles or ['D', 'A', 'B', 'C'])
                for v in (args.snr if args.snr is not None else SWEEPS['snr_comparison'][1])]
    if name == 'runtime_comparison':
        return [dict(DEFAULT, snr_db=v) for v in (args.snr if args.snr is not None else [-4, 0, 4])]
    if name == 'density_ratio_ablation':
        return [dict(DEFAULT, snr_db=v) for v in (args.values if args.values is not None else [-4,-2,0,2,4,6,8])]
    return [dict(variance=v, users=40, candidates=4) for v in
            (args.values if args.values is not None else [.001, .01, .1, 1., 10., 100.])]


def make_plan(name, args):
    if sha(REGISTRY / 'PLAN.json') != PANEL_HASH:
        raise ValueError('The user-confirmed 2000-scene policy changed')
    out = args.output or DEFAULT_OUTPUT / name
    out = out.resolve()
    if out.exists() and any(out.iterdir()):
        raise FileExistsError('A new plan needs an empty directory: '+str(out))
    binding = read(HERE / 'models.json')
    methods = args.methods or binding['default_methods']
    if args.include_legacy and 'legacy' not in methods:
        methods = list(methods)+['legacy']
    if 'legacy' in methods and not args.include_legacy:
        raise ValueError('Legacy execution is deferred; explicitly opt in only when it is requested again')
    if name == 'density_ratio_ablation':
        methods = ['ten_layer', 'legacy', 'legacy_gaussian']
    if name == 'channel_denoising':
        methods = ['noisy', 'gaussian', 'genie_bound', 'pretrained_first']
    count = args.scenes if args.scenes is not None else (1 if args.smoke else (20 if name == 'runtime_comparison' else 2000))
    if not 1 <= count <= (20 if name == 'runtime_comparison' else 2000):
        raise ValueError('Scene count is outside the fixed registry subset')
    if not args.smoke and count != (20 if name == 'runtime_comparison' else 2000):
        raise ValueError('Reduced scene counts require --smoke and use separate seeds')
    conditions = selections(name, args)
    if not conditions or len({digest(c) for c in conditions}) != len(conditions):
        raise ValueError('Distinct nonempty conditions required')
    for c in conditions:
        if name == 'channel_denoising':
            if not .001 <= c['variance'] <= 100:
                raise ValueError('AWGN variance outside declared support')
        else:
            if c['users'] != int(c['users']) or c['frames'] != int(c['frames']):
                raise ValueError('Integer user/pilot counts required')
            c.update(users=int(c['users']), frames=int(c['frames']))
            if not 2 <= c['users'] <= 100 or not 1 <= c['frames'] <= 48 or not 0 < c['activity_probability'] < 1:
                raise ValueError('Invalid experimental condition')
    panel = read(REGISTRY / 'PLAN.json')
    runtime_assets = assets(binding)
    cache = (args.cache or (out.parent / ('shared_smoke' if args.smoke else 'shared'))).resolve()
    plan = dict(schema='afdm-eight-experiments-ten-layer-v1', experiment=name,
        scene_count=count, base_seed=SMOKE_SEED if args.smoke else panel['base_seed'],
        formal_panel_sha256=PANEL_HASH, scene_registry=str(REGISTRY / 'SCENES.csv'),
        mode='SMOKE_ONLY' if args.smoke else 'FORMAL_2000',
        execution_status='DEFERRED_BY_USER' if name=='density_ratio_ablation' and not args.include_legacy else 'READY',
        include_legacy=args.include_legacy, timing_repeats=3 if name=='runtime_comparison' else 1,
        conditions=conditions, methods=methods, model_binding=binding, assets=runtime_assets,
        runtime_identity=digest(runtime_assets), device=args.device, threads=4, tf32=False,
        cache=str(cache), phase_mode='estimated', noise_mode='estimated',
        bootstrap_replicates=10000, bootstrap_seed=2026102198,
        timing='One warmup per method/shape, CUDA synchronization; shared frontend time added separately. Cached results keep original timing.',
        ablation_scope='Controlled learned-vs-Gaussian-site evidence on legacy only; ten-layer is a full-receiver reference, not a matched ablation.',
        denoising_scope='Only the frozen pretrained first-score AWGN network; no receiver layer, second score or activity network is evaluated.',
        amendments=['User replaced convergence curves with runtime/accuracy comparison; original 20-scene representative prefix retained.',
                    'User requested pretrained first-score denoising only.', 'User deferred legacy three-network execution and its activity-evidence ablation.'],
        material_passport=dict(origin_skill='academic-research-suite / experiment-agent', origin_mode='run',
            origin_date='2026-10-21', verification_status='PLANNED', version_label='ten_layer_integration_v1'))
    save(out / 'PLAN.json', plan)
    save(out / 'PLAN_HASH.json', dict(sha256=sha(out / 'PLAN.json')))
    print(json.dumps(dict(status='PLANNED', output=str(out), scenes=count, conditions=len(conditions), methods=methods)), flush=True)
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


def prepared_case(plan, scene, condition):
    seed = plan['base_seed']+scene
    folder = Path(plan['cache']) / 'inputs' / f'{seed}' / condition_key(condition)
    identity = dict(seed=seed, condition=condition, runtime=plan['runtime_identity'])
    marker = folder / 'READY.json'
    if marker.exists():
        receipt = read(marker)
        if receipt['identity'] != identity:
            raise ValueError('Shared input runtime or physical condition changed')
        for name, expected in receipt['files'].items():
            if sha(folder / name) != expected:
                raise ValueError('Shared input bytes changed')
        public = arrays(folder / 'public.npz')
        return (ReceiverInput(public['y'], public['a'], 1., float(public['rho'])),
                arrays(folder / 'truth.npz'), receipt, folder)
    scale = plan['model_binding']['legacy_configuration']['scale']
    raw, truth, meta = observation(seed, condition, scale, generator=generate_profile_case)
    controls = phase.Controls(**read(ROOT / plan['model_binding']['phase_configuration'])['phase_estimation'])
    fitted, phase_record = estimated_phase(raw, folder, controls)
    public = raw.at_estimated_phase(fitted['phase_slopes'])
    save_arrays(folder / 'public.npz', dict(y=public.observation, a=public.operator, rho=public.activity_prior))
    save_arrays(folder / 'raw.npz', dict(y=raw.observation, pilot=raw.pilot, rho=raw.activity_prior))
    save_arrays(folder / 'truth.npz', truth)
    receipt = dict(identity=identity, generation=meta, phase_seconds=phase_record['seconds'],
                   files={n:sha(folder/n) for n in ['public.npz','raw.npz','truth.npz','phase.npz','PHASE.json']})
    save(marker, receipt)
    return ReceiverInput(public.observation, public.operator, 1., public.activity_prior), truth, receipt, folder


def checked_result(path, identity):
    if not path.exists():
        return None
    row = read(path)
    if row['identity'] != identity or row['status'] != 'COMPLETE' or sha(path.with_suffix('.npz')) != row['compact_sha256']:
        raise ValueError('Changed or failed saved result: '+str(path))
    return row


def receiver_result(plan, model, method, scene, cond, public, truth, case, warmed):
    import torch
    identity = dict(runtime=plan['runtime_identity'], input=case['files'], method=method,
                    device=plan['device'], repeats=plan['timing_repeats'], seed=plan['base_seed']+scene)
    path = Path(plan['cache']) / 'predictions' / (digest(identity)+'.json')
    row = checked_result(path, identity)
    if row is not None:
        return row, path
    warm_key = (method, public.operator.shape)
    if warm_key not in warmed:
        # The deterministic warmup is disjoint from the formal evaluation panel.
        # Its outputs never participate in any statistical summary.
        probe = dict(plan, base_seed=SMOKE_SEED+80000)
        warm_public, _, _, _ = prepared_case(probe, 0, cond)
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
    prediction_hash = sha(full)
    compact = {k:np.asarray(v) for k,v in output.items() if np.asarray(v).ndim <= 1}
    compact.update(per_user_error=np.asarray(metrics['per_user_error']), truth_activity=truth['activity'])
    save_arrays(path.with_suffix('.npz'), compact)
    row = dict(status='COMPLETE', identity=identity, metrics=metrics,
        receiver_seconds=elapsed, phase_seconds=case['phase_seconds'], end_to_end_seconds=elapsed+case['phase_seconds'],
        timing_repeats_seconds=timings, backend=plan['device'] if network_modules(model) else 'cpu',
        parameter_count=parameter_count(model),
        iterations=record['iterations'], stopping_reason=record['stopping_reason'],
        peak_allocated_mib=(torch.cuda.max_memory_allocated()/2**20 if network_modules(model) else 0.) if plan['device']=='cuda' else None,
        compact_sha256=sha(path.with_suffix('.npz')), prediction_sha256=prediction_hash,
        full_prediction_retained=scene==0, rescoring='PASSED',
        timing_scope='Synchronized conditional receiver, median of declared repeats; cached shared phase listed separately',
        diagnostics=record.get('diagnostics', []), selected_epoch=record.get('selected_epoch'))
    save(path.with_suffix('.record.json'), record)
    save(path, row)
    if scene != 0:
        full.unlink()  # Only this newly written scratch full prediction; compact evidence is retained.
    return row, path


def denoising_results(plan, models, scene, condition):
    import torch
    variance = condition['variance']
    scale = plan['model_binding']['legacy_configuration']['scale']
    seed = plan['base_seed']+scene
    physical, selected, priors = denoising.clean_channels(seed, 40, 4, genie_scale=scale)
    truth = physical/scale
    rng = np.random.default_rng(np.random.SeedSequence([seed,8240]))
    epsilon = (rng.normal(size=truth.shape)+1j*rng.normal(size=truth.shape))/np.sqrt(2)
    query = truth+np.sqrt(variance)*epsilon
    identity = dict(runtime=plan['runtime_identity'], seed=seed, variance=variance,
                    query_sha256=array_sha256(query), truth_sha256=array_sha256(truth), users=selected.tolist(), device=plan['device'])
    folder = Path(plan['cache']) / 'denoising' / digest(identity)
    saved = {m: checked_result(folder/(m+'.json'), dict(identity,method=m)) for m in plan['methods']}
    if all(row is not None for row in saved.values()):
        return [(row, folder/(m+'.json')) for m,row in saved.items()]
    if not models:
        c = plan['model_binding']['legacy_configuration']
        models['pretrained_first'] = denoising.FirstChannelMean(scale, ROOT/c['first_checkpoint'],device=plan['device'],batch_size=4)
    save_arrays(folder / 'query.npz', dict(query=query, truth=truth, users=selected))
    power = plan['model_binding']['legacy_configuration']['initialization']['normalized_training_second_moment']
    means = dict(noisy=query, gaussian=power/(power+variance)*query)
    means['genie_bound'], risk = denoising.genie_mmse(query, variance, priors)
    means['pretrained_first'] = models['pretrained_first'].infer(query,variance).mean
    results = []
    for method in plan['methods']:
        path = folder/(method+'.json')
        if saved[method] is not None:
            results.append((saved[method],path)); continue
        values = denoising.denoising_metrics(means[method], truth)
        if method == 'genie_bound':
            values.update(realized_error=values['error'], error=risk)
        save_arrays(path.with_suffix('.npz'), values)
        row = dict(identity=dict(identity,method=method), status='COMPLETE',
                   compact_sha256=sha(path.with_suffix('.npz')), error=float(values['error'].sum()),
                   energy=float(values['energy'].sum()), samples=4, truth_used=method=='genie_bound',
                   error_kind='analytic_conditional_mmse' if method=='genie_bound' else 'realized_squared_error')
        save(path, row)
        if scene == 0:
            save_arrays(folder/(method+'.prediction.npz'), dict(estimate=means[method]))
        results.append((row,path))
    return results


def run(out, plan):
    import torch
    from threadpoolctl import threadpool_limits
    verify(plan)
    if plan['execution_status'] == 'DEFERRED_BY_USER':
        print(json.dumps(dict(status='DEFERRED_BY_USER',reason='Legacy three-network execution is paused by user request.')))
        return 0
    if (out / 'COMPLETE.json').exists():
        for name, expected in read(out / 'COMPLETE.json')['files'].items():
            if sha(out / name) != expected:
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
                    if plan['experiment']=='channel_denoising':
                        results = denoising_results(plan, models, scene, cond)
                        for row,path in results:
                            save(folder/(row['identity']['method']+'.json'), dict(result=str(path), sha256=sha(path)))
                    else:
                        public, truth, case, _ = prepared_case(plan,scene,cond)
                        for method in plan['methods']:
                            if method not in models:
                                models[method] = build(method, plan['model_binding'],device)
                            activate(models,method,device)
                            row,path = receiver_result(plan,models[method],method,scene,cond,public,truth,case,warmed)
                            save(folder/(method+'.json'), dict(result=str(path), sha256=sha(path)))
                    save(out/'STATUS.json',dict(stage='RUNNING',pid=os.getpid(),scene=scene+1,condition=index+1,
                         scenes=plan['scene_count'], conditions=len(plan['conditions']), updated_unix=time.time()))
                    print(json.dumps(dict(experiment=plan['experiment'],scene=scene+1,condition=index+1,
                                          total_conditions=len(plan['conditions']))),flush=True)
            del models
            gc.collect()
            if device=='cuda':torch.cuda.empty_cache()
            verify(plan)
            return summarize(out,plan)
        except BaseException:
            save(out/'failures'/f'{time.time_ns()}.json',dict(status='FAILED',traceback=traceback.format_exc(),pid=os.getpid()))
            save(out/'STATUS.json',dict(stage='FAILED',pid=os.getpid(),updated_unix=time.time()))
            raise


def summarize(out, plan):
    from reporting import finish
    return finish(out,plan)


def main(name=None, argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['plan','run','summarize','inspect'])
    if name is None:parser.add_argument('--experiment',choices=NAMES,required=True)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--cache',type=Path)
    parser.add_argument('--device',choices=['cuda','cpu','auto'],default='cuda')
    parser.add_argument('--smoke',action='store_true',help='Use separate diagnostic seeds, never the formal panel')
    parser.add_argument('--scenes',type=int)
    parser.add_argument('--values',type=float,nargs='+')
    parser.add_argument('--snr',type=float,nargs='+')
    parser.add_argument('--profiles',choices=['A','B','C','D'],nargs='+')
    parser.add_argument('--include-legacy',action='store_true',help='Opt in to the currently deferred legacy receiver')
    parser.add_argument('--methods',choices=['ten_layer','legacy','offgrid_sbl','gnn','gamp','somp'],nargs='+')
    args=parser.parse_args(argv)
    name = name or args.experiment
    if args.command=='plan':
        if args.device=='auto':
            import torch
            args.device='cuda' if torch.cuda.is_available() else 'cpu'
        make_plan(name,args)
        return 0
    out=(args.output or DEFAULT_OUTPUT/name).resolve()
    if read(out/'PLAN_HASH.json')['sha256'] != sha(out/'PLAN.json'):
        raise ValueError('Saved plan changed')
    plan=read(out/'PLAN.json')
    if plan['experiment'] != name:raise ValueError('Wrong entrypoint for saved plan')
    if args.command=='inspect':
        verify(plan)
        print(json.dumps(dict(status='READY',mode=plan['mode'],scenes=plan['scene_count'],methods=plan['methods'])))
        return 0
    return run(out,plan) if args.command=='run' else summarize(out,plan)


if __name__=='__main__':
    raise SystemExit(main())
