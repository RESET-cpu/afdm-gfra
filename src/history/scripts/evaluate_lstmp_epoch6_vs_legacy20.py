"""Predeclared 20-scene comparison; execute only after five-layer training completes.

Uses the training run's frozen sources, separate public input/truth files, and
unchanged receiver settings. Preparation uses CPU only. No optimizer is created.
"""
import argparse
import csv
import gc
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import sys
import time
import traceback

import numpy as np

ROOT = Path(r'C:\Users\25911\Desktop\afdm-gfra')
RUN = Path(r'D:\afdm-gfra-cpu\runs\lstmp_refinenet_50000_epoch6_20261020')
OUT = ROOT / 'results/lstmp_epoch6_vs_legacy20_20261020'
CONFIG_NAME = 'reuse_50000_fast.json'
CONDITION = dict(users=40, frames=16, activity_probability=.1, snr_db=5.)
SEEDS = list(range(202610208700001, 202610208700021))
WARMUP_SEED = 202610208799999
METHODS = ('new_five_layer', 'legacy_50000_damping01')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    temp.replace(path)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(2**20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def modules(root, run):
    os.environ['AFDM_LSTMP_ROOT'] = str(root)
    os.environ['AFDM_LSTMP_CONFIG'] = str(run / 'source_code/experiments/lstmp_candidate_20261019' / CONFIG_NAME)
    sys.path.insert(0, str(run / 'source_code'))
    from experiments.lstmp_candidate_20261019 import common, data, receiver
    if Path(common.OUT).resolve() != run.resolve():
        raise RuntimeError('Wrong candidate module/configuration was imported')
    return common, data, receiver


def readiness(run):
    """A partial checkpoint, pause, or process exit is never training completion."""
    complete = run / 'COMPLETE.json'
    if not complete.exists():
        return False, 'WAITING_FOR_SUCCESSFUL_TRAINING_COMPLETION'
    if read(complete).get('status') != 'COMPLETE':
        raise ValueError('Invalid training completion record')
    if (run / 'RUNNING.lock').exists():
        return False, 'WAITING_FOR_TRAINING_PROCESS_RELEASE'
    for depth, epochs in enumerate((2, 2, 2, 2, 6), 1):
        folder = run / 'checkpoints' / f'depth_{depth}'
        receipt = read(folder / 'COMPLETE.json')
        if (receipt.get('status') != 'COMPLETE' or receipt['selected_epoch'] < 1 or
                receipt['steps'] != 4800 * epochs or
                receipt['checkpoint_sha256'] != sha(folder / 'best.pt')):
            raise ValueError(f'Incomplete budget or changed selected checkpoint: depth {depth}')
    if not all(read(complete)['protected_assets_preserved'].values()):
        raise ValueError('Training reports a changed protected asset')
    return True, 'READY'


def make_case(folder, seed, scale):
    from afdm_jadcedd.experiment.generate import generate_case
    from afdm_jadcedd.system.observation import ReceiverInput
    condition = dict(CONDITION)
    snr = condition.pop('snr_db')
    inputs, truth, metadata = generate_case(seed, snr, scale, **condition)
    public = ReceiverInput(**{k: inputs[k] for k in ReceiverInput.__dataclass_fields__})
    folder.mkdir(parents=True, exist_ok=False)
    np.savez_compressed(folder / 'input.npz', **public.arguments())
    np.savez_compressed(folder / 'truth.npz', channel=truth['channel'], activity=truth['activity'])
    write(folder / 'generation.json', metadata)
    return dict(seed=seed, input_sha256=sha(folder / 'input.npz'),
                truth_sha256=sha(folder / 'truth.npz'), generation_sha256=sha(folder / 'generation.json'))


def prepare(root, run, out):
    if out.exists():
        raise FileExistsError('Existing comparison is preserved: ' + str(out))
    common, _, _ = modules(root, run)
    import torch
    from threadpoolctl import threadpool_limits
    torch.set_num_threads(1)
    threadpool_limits(1)
    # Check disjointness against the full original scene pools, not just the subset.
    for split in ('train', 'validation', 'test'):
        cfg = common.CONFIG['receiver']
        base = cfg[f'{split}_seed']
        count = cfg.get('case_sources', {}).get(split, {}).get('pool_count', cfg[f'{split}_scenes'])
        if any(base <= seed < base + count for seed in SEEDS + [WARMUP_SEED]):
            raise ValueError('Evaluation seed overlaps a training/selection scene')
    prior_path=root/'runs/proposed_50000_cuda_20261018/data/prior_definition.json'
    prior=read(prior_path)
    for identity in prior['dataset_identities'].values():
        if set(identity['scene_seeds']).intersection(SEEDS+[WARMUP_SEED]):
            raise ValueError('Evaluation seed overlaps first-score pretraining')
    from experiments.lstmp_candidate_20261019.baseline_evaluation import binding
    old_config, old_binding = binding(dict(name=METHODS[1],
        configuration='runs/proposed_auxiliary_100_cuda_graph_20261019/n50000/receiver.json', damping=.1))
    scale = common.CONFIG['pretrained_score']['global_complex_rms']
    if old_config['scale'] != scale or old_config['decision_threshold'] != .5:
        raise ValueError('Comparison normalization or activity threshold mismatch')
    out.mkdir(parents=True)
    (out / 'source').mkdir()
    script = out / 'source' / Path(__file__).name
    shutil.copy2(__file__, script)
    cases = []
    for index, seed in enumerate(SEEDS):
        cases.append(dict(index=index, **make_case(out / 'cases' / f'{index:03d}', seed, scale)))
    warmup = make_case(out / 'warmup', WARMUP_SEED, scale)
    plan = dict(schema='paired-receiver-20-v1', created_unix=time.time(), root=str(root),
        training_run=str(run), training_manifest_sha256=sha(run / 'MANIFEST.json'),
        evaluator_sha256=sha(script), scene_count=20, condition=CONDITION, cases=cases, warmup=warmup,
        scale=scale, phase_mode='known', noise_mode='known',
        activity_sampling='Bernoulli p=0.1 conditioned on at least one active user, as in training; public prior is the conditional marginal',
        seeds_independent_of_training_and_selection=True,
        pretraining_prior_sha256=sha(prior_path),
        new_checkpoint='checkpoints/depth_5/best.pt',
        new_selection='Final depth-five validation-selected checkpoint, only after all 67200 updates finish, including the inherited 57600',
        old_binding=old_binding, device='cuda', cpu_threads=4, allow_tf32=True, activity_threshold=.5,
        timing='One untimed independent warmup per method; 20 sequential scenes. CPU-resident public arrays to CPU-resident predictions, synchronized CUDA. Includes method-specific preparation/SVD/copies and inference; excludes disk I/O, truth scoring, plot generation and model load. Model load reported separately.',
        execution='New then legacy, one resident model at a time, no concurrent training. Native float32 score networks; each frozen linear-module implementation retains its own precision.',
        metrics='AER=(misses+false alarms)/800 users. NMSE uses effective channels including inactive-user errors: pooled sum(error energy)/sum(truth energy), and mean of 20 per-scene linear ratios converted to dB. No hard mask on estimates.',
        overhead='Parameter count and bytes, state-dict tensor bytes, checkpoint file bytes, per-scene peak allocated/reserved CUDA memory, score/classifier calls, iteration counts and additional fine-tuning elapsed time. Historical pretraining cost not inferred.',
        limitations='20 independent scenes at one condition; known phase/noise control, not unknown-phase end-to-end or a full experiment sweep. Wall time measures the saved implementations, not hardware-independent complexity.',
        failures='Preserve all scenes and attempts. Do not retune thresholds, damping, weights, or iteration budget using these test labels. No summary marked complete if any scene fails.')
    previous = root / 'results/lstmp_vs_legacy20_repaired_20261019'
    old_plan = read(previous/'PLAN.json')
    old_seeds = {c['seed'] for c in old_plan['cases']} | {old_plan['warmup']['seed']}
    if old_seeds.intersection(SEEDS + [WARMUP_SEED]):
        raise ValueError('Fresh confirmation overlaps the revealed prior comparison')
    if plan['old_binding'] != old_plan['old_binding']:
        raise ValueError('Legacy receiver binding differs from the prior comparison')
    continuation = run/'protocol/EPOCH6_CONTINUATION.json'
    plan['epoch_extension'] = dict(record=str(continuation), record_sha256=sha(continuation),
        inherited_updates=57600, additional_updates=9600, total_updates=67200,
        epoch_schedule=[2,2,2,2,6], previous_comparison=str(previous),
        previous_plan_sha256=sha(previous/'PLAN.json'),
        previous_summary_sha256=sha(previous/'SUMMARY.json'),
        independent_fresh_confirmation=True)
    write(out / 'PLAN.json', plan)
    write(out / 'STATUS.json', dict(stage='WAITING_FOR_TRAINING', updated_unix=time.time()))
    return dict(output=str(out), scenes=len(cases), warmup_scenes=1, training_started=False, gpu_used=False)


def verify_plan(out, plan):
    root, run = Path(plan['root']), Path(plan['training_run'])
    if sha(__file__) != plan['evaluator_sha256'] or sha(run / 'MANIFEST.json') != plan['training_manifest_sha256']:
        raise ValueError('Evaluation source or training manifest changed')
    manifest = read(run / 'MANIFEST.json')
    for name, expected in manifest['snapshot_hashes'].items():
        if sha(name) != expected:
            raise ValueError('Frozen source changed: ' + name)
    for name, expected in manifest['protected_assets'].items():
        if sha(root / name) != expected:
            raise ValueError('Protected asset changed: ' + name)
    for folder, case in [(out / 'cases' / f'{c["index"]:03d}', c) for c in plan['cases']] + [(out / 'warmup', plan['warmup'])]:
        for filename, key in [('input.npz', 'input_sha256'), ('truth.npz', 'truth_sha256'), ('generation.json', 'generation_sha256')]:
            if sha(folder / filename) != case[key]:
                raise ValueError('Paired scene changed: ' + str(folder / filename))


def score_arrays(estimate, probabilities, truth, active, threshold=.5):
    estimate, truth = np.asarray(estimate, np.complex128), np.asarray(truth, np.complex128)
    p, active = np.asarray(probabilities, float), np.asarray(active, bool)
    if estimate.shape != truth.shape or p.shape != active.shape or len(p) != len(truth):
        raise ValueError('Prediction/truth dimensions differ')
    if (not np.isfinite(estimate).all() or not np.isfinite(p).all() or
            not np.isfinite(truth).all() or np.any((p < 0) | (p > 1))):
        raise FloatingPointError('Invalid prediction; scene cannot be discarded')
    decision = p >= threshold
    error = np.abs(estimate - truth)**2
    power = np.abs(truth)**2
    e, t = float(error.sum()), float(power.sum())
    misses, false = int((active & ~decision).sum()), int((~active & decision).sum())
    return dict(error_energy=e, truth_energy=t, nmse=e/t if t > 0 else None,
        active_error_energy=float(error[active].sum()), active_truth_energy=float(power[active].sum()),
        active=int(active.sum()), inactive=int((~active).sum()), misses=misses, false_alarms=false,
        aer=(misses+false)/len(active))


def model_size(networks):
    parameters = [p for model in networks for p in model.parameters()]
    tensors = [v for model in networks for v in model.state_dict().values()]
    return dict(parameters=sum(p.numel() for p in parameters),
        parameter_bytes=sum(p.numel()*p.element_size() for p in parameters),
        state_tensor_bytes=sum(v.numel()*v.element_size() for v in tensors))


class Adapter:
    def __init__(self, method, plan, common, data, receiver):
        import torch
        self.method, self.plan, self.data = method, plan, data
        self.scale = plan['scale']
        root, run = Path(plan['root']), Path(plan['training_run'])
        if method == METHODS[0]:
            self.model = receiver.Receiver()
            for _ in range(5):
                self.model.add_layer(None)
            self.model.load_state_dict(torch.load(run / plan['new_checkpoint'], map_location='cpu', weights_only=False)['state'])
            self.model.cuda().eval()
            self.model.use_checkpoint = False
            self.networks = [self.model]
            self.checkpoint_bytes = (run / plan['new_checkpoint']).stat().st_size
        else:
            from afdm_jadcedd.algorithm.proposed.receiver import Receiver
            cfg = plan['old_binding']['applied_configuration']
            self.model = Receiver(cfg, device='cuda')
            self.networks = [self.model.model.first, self.model.model.second, self.model.evidence.network]
            self.checkpoint_bytes = sum((root / cfg[k]).stat().st_size for k in ('first_checkpoint', 'second_checkpoint', 'evidence_checkpoint'))

    def prepare(self, public):
        if self.method == METHODS[0]:
            values = dict(y=public.observation, a=public.operator, noise=public.noise_variance, rho=public.activity_prior)
            return self.data.prepare_public(values, self.scale, 'cuda', phase_mode='known', noise_mode='known')[0]
        return public

    def infer(self, prepared):
        import torch
        if self.method == METHODS[0]:
            outputs, diagnostics = self.model(prepared)
            x, logits = outputs[-1]
            real = x.cpu().numpy()
            estimate = (real[:, 0].astype(np.float64) + 1j*real[:, 1].astype(np.float64))*self.scale
            p = torch.sigmoid(logits).cpu().numpy()
            users = len(p)
            calls = 5 * math.ceil(users / self.plan['new_microbatch'])
            record = dict(iterations=5, converged=None, stopping_reason='FIXED_FIVE_LAYERS',
                first_score_calls=calls, first_score_samples=5*users, second_score_calls=0,
                second_score_samples=0, classifier_calls=5, classifier_samples=5*users,
                diagnostics=diagnostics)
            return dict(estimate=estimate, probabilities=p), record
        return self.model.infer(prepared)


def timed_inference(adapter, public):
    import torch
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    start = time.perf_counter()
    with torch.no_grad():
        prepared = adapter.prepare(public)
        torch.cuda.synchronize()
        ready = time.perf_counter()
        arrays, record = adapter.infer(prepared)
        torch.cuda.synchronize()
        end = time.perf_counter()
    times = dict(preparation_seconds=ready-start, inference_seconds=end-ready, total_seconds=end-start,
        peak_allocated_bytes=torch.cuda.max_memory_allocated(), peak_reserved_bytes=torch.cuda.max_memory_reserved())
    return arrays, record, times


def summarize(rows):
    if not rows or any(r['status'] != 'COMPLETE' for r in rows):
        raise ValueError('All planned scenes must finish before aggregation')
    total = lambda key: sum(r[key] for r in rows)
    ratio = total('error_energy')/total('truth_energy')
    means = np.asarray([r['nmse'] for r in rows])
    seconds = np.asarray([r['total_seconds'] for r in rows])
    db = lambda x: 10*math.log10(x) if x > 0 else None
    return dict(scenes=len(rows), aer=(total('misses')+total('false_alarms'))/(total('active')+total('inactive')),
        misses=total('misses'), false_alarms=total('false_alarms'), active=total('active'), inactive=total('inactive'),
        pooled_nmse=ratio, pooled_nmse_db=db(ratio), mean_scene_nmse=float(means.mean()),
        mean_scene_nmse_db=db(float(means.mean())),
        mean_seconds=float(seconds.mean()), median_seconds=float(np.median(seconds)),
        std_seconds=float(seconds.std(ddof=1)) if len(rows)>1 else 0., p95_seconds=float(np.quantile(seconds,.95)),
        mean_preparation_seconds=total('preparation_seconds')/len(rows),
        mean_inference_seconds=total('inference_seconds')/len(rows),
        peak_allocated_bytes=max(r['peak_allocated_bytes'] for r in rows),
        peak_reserved_bytes=max(r['peak_reserved_bytes'] for r in rows),
        mean_iterations=total('iterations')/len(rows),
        converged_scenes=sum(r['converged'] is True for r in rows),
        iteration_limit_scenes=sum(r['stopping_reason']=='MAX_ITERATIONS' for r in rows),
        fixed_depth_scenes=sum(r['stopping_reason']=='FIXED_FIVE_LAYERS' for r in rows),
        mean_first_score_calls=total('first_score_calls')/len(rows),
        mean_second_score_calls=total('second_score_calls')/len(rows),
        mean_classifier_calls=total('classifier_calls')/len(rows))


def make_report(out, plan, identity):
    methods, paired = {}, {}
    for method in METHODS:
        folder = out / method
        rows = [read(folder / f'{i:03d}.json') for i in range(plan['scene_count'])]
        for row, case in zip(rows, plan['cases']):
            if (row['case_index'] != case['index'] or row['seed'] != case['seed'] or
                    row['input_sha256'] != case['input_sha256'] or
                    row['prediction_sha256'] != sha(folder / f'{case["index"]:03d}.npz')):
                raise ValueError('Completed prediction no longer matches its paired input')
        methods[method] = dict(**summarize(rows), **read(folder / 'OVERHEAD.json'))
        paired[method] = rows
    a, b = methods[METHODS[0]], methods[METHODS[1]]
    report = dict(status='COMPLETE', identity=identity, condition=plan['condition'],
        phase_mode=plan['phase_mode'], noise_mode=plan['noise_mode'], methods=methods,
        speedup_legacy_over_new=b['mean_seconds']/a['mean_seconds'],
        paired_new_minus_legacy=dict(aer=a['aer']-b['aer'],
            pooled_nmse_db=a['pooled_nmse_db']-b['pooled_nmse_db'],
            new_lower_nmse_scenes=sum(x['nmse']<y['nmse'] for x,y in zip(paired[METHODS[0]],paired[METHODS[1]])),
            new_lower_aer_scenes=sum(x['aer']<y['aer'] for x,y in zip(paired[METHODS[0]],paired[METHODS[1]]))),
        training_overhead=dict(additional_finetuning_seconds=read(Path(plan['training_run'])/'COMPLETE.json')['seconds'],
            scope='Resumable active-run elapsed time, including training, validation, checkpoints and run initialization; excludes user pauses. Not kernel-only GPU time.',
            historical_first_second_activity_training_seconds=None,
            historical_cost_note='Existing pretrained networks are reused; historical total training time is not reconstructed or assumed zero.',
            shared_first_score_pretraining='Both algorithms reuse the same 50000-sample first-score starting point; do not charge its historical cost twice.'),
        limitations=plan['limitations'])
    inherited = read(Path(plan['training_run'])/'protocol/EPOCH6_CONTINUATION.json')['inherited_training_seconds']
    report['training_overhead']['inherited_finetuning_seconds'] = inherited
    report['training_overhead']['current_continuation_seconds'] = report['training_overhead']['additional_finetuning_seconds'] - inherited
    report['training_overhead']['cumulative_time_limit_hours'] = 12
    report['training_overhead']['additional_finetuning_seconds_scope'] = 'Cumulative fine-tuning across the preserved parent and this continuation; current_continuation_seconds is this extension alone.'
    write(out / 'SUMMARY.json', report)
    with (out / 'summary.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['method', *a])
        writer.writeheader()
        writer.writerows(dict(method=name, **methods[name]) for name in METHODS)
    flat = [dict(method=method, **row) for method in METHODS for row in paired[method]]
    with (out / 'per_scene.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(flat[0]))
        writer.writeheader(); writer.writerows(flat)
    # Scientific figure, derived only from the saved paired rows.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.5), constrained_layout=True)
    labels = ['New: 5 layers', 'Legacy: damping 0.1']
    for ax, key, title, factor in zip(axes,
            ['aer','pooled_nmse_db','mean_seconds','peak_allocated_bytes'],
            ['AER (%)','Pooled NMSE (dB)','Mean time / scene (s)','Peak GPU allocation (GiB)'],
            [100,1,1,1/2**30]):
        values = [methods[m][key]*factor for m in METHODS]
        bars=ax.bar(labels, values, color=['#227C9D','#ED8B3A'])
        ax.bar_label(bars, fmt='%.3f', padding=4)
        ax.set_title(title, fontsize=10); ax.grid(axis='y', alpha=.2); ax.set_axisbelow(True)
        ax.margins(y=.25); ax.tick_params(axis='x', labelsize=8)
    fig.suptitle('20 paired independent scenes | K=40, Q=16, p=0.1, SNR=5 dB | Known phase/noise')
    fig.savefig(out/'comparison.png', dpi=180)
    fig.savefig(out/'comparison.pdf')
    plt.close(fig)
    write(out / 'COMPLETE.json', dict(status='COMPLETE', completed_unix=time.time(),
        plan_sha256=sha(out/'PLAN.json'), summary_sha256=sha(out/'SUMMARY.json'),
        scene_counts={m:len(paired[m]) for m in METHODS}, preserved_inputs_verified=True))
    return report


def run_comparison(out):
    plan = read(out / 'PLAN.json')
    root, run = Path(plan['root']), Path(plan['training_run'])
    ready, state = readiness(run)
    if not ready:
        return dict(stage=state, evaluation_started=False)
    verify_plan(out, plan)
    if (out/'COMPLETE.json').exists():
        return dict(stage='ALREADY_COMPLETE', output=str(out))
    descriptor = os.open(out/'RUNNING.lock', os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    os.write(descriptor, str(os.getpid()).encode()); os.close(descriptor)
    try:
        common, data, receiver = modules(root, run)
        import torch
        from threadpoolctl import threadpool_limits
        from afdm_jadcedd.system.observation import load_input
        torch.set_num_threads(plan['cpu_threads']); threadpool_limits(plan['cpu_threads'])
        torch.backends.cuda.matmul.allow_tf32 = plan['allow_tf32']
        torch.backends.cudnn.allow_tf32 = plan['allow_tf32']
        torch.backends.cudnn.benchmark = True
        plan = dict(plan, new_microbatch=common.CONFIG['receiver']['microbatch'])
        identity = dict(plan_sha256=sha(out/'PLAN.json'), selected_checkpoint_sha256=sha(run/plan['new_checkpoint']),
            training_complete_sha256=sha(run/'COMPLETE.json'), torch=torch.__version__, cuda=torch.version.cuda,
            cudnn=torch.backends.cudnn.version(), gpu=torch.cuda.get_device_name(), python=platform.python_version())
        if (out/'BINDING.json').exists() and read(out/'BINDING.json') != identity:
            raise ValueError('Evaluation checkpoint or environment changed on resume')
        write(out/'BINDING.json', identity)
        for method in METHODS:
            folder = out/method; folder.mkdir(exist_ok=True)
            if all((folder/f'{i:03d}.json').exists() for i in range(plan['scene_count'])):
                continue
            torch.cuda.empty_cache(); torch.cuda.synchronize()
            started=time.perf_counter()
            adapter=Adapter(method,plan,common,data,receiver)
            torch.cuda.synchronize()
            overhead=dict(model_size(adapter.networks), checkpoint_file_bytes=adapter.checkpoint_bytes,
                          model_load_seconds=time.perf_counter()-started)
            # Warmup output and labels never select a model, threshold, or setting.
            timed_inference(adapter,load_input(out/'warmup/input.npz'))
            torch.cuda.empty_cache()
            if not (folder/'OVERHEAD.json').exists(): write(folder/'OVERHEAD.json',overhead)
            for case in plan['cases']:
                index=case['index']; path=folder/f'{index:03d}.json'
                if path.exists():
                    prior=read(path)
                    if prior['case_index']!=index or prior['input_sha256']!=case['input_sha256'] or prior['status']!='COMPLETE':
                        raise ValueError('Invalid completed scene on resume')
                    continue
                write(out/'STATUS.json',dict(stage='EVALUATING',pid=os.getpid(),method=method,scene=index+1,total=20,updated_unix=time.time()))
                public=load_input(out/'cases'/f'{index:03d}'/'input.npz')
                arrays,record,times=timed_inference(adapter,public)
                with np.load(out/'cases'/f'{index:03d}'/'truth.npz',allow_pickle=False) as truth:
                    metrics=score_arrays(arrays['estimate'],arrays['probabilities'],truth['channel'],truth['activity'])
                np.savez_compressed(folder/f'{index:03d}.npz',estimate=arrays['estimate'],probabilities=arrays['probabilities'])
                write(folder/f'{index:03d}_trace.json',record)
                keys=('iterations','converged','stopping_reason','first_score_calls','second_score_calls','classifier_calls',
                      'first_score_samples','second_score_samples','classifier_samples')
                row=dict(status='COMPLETE',case_index=index,seed=case['seed'],input_sha256=case['input_sha256'],
                    prediction_sha256=sha(folder/f'{index:03d}.npz'),**metrics,**times,**{k:record[k] for k in keys})
                write(path,row)
                print(json.dumps(dict(method=method,scene=index+1,seconds=times['total_seconds'],aer=metrics['aer'],nmse=metrics['nmse'])),flush=True)
                del arrays,record,public
            del adapter
            gc.collect(); torch.cuda.empty_cache()
        verify_plan(out,plan)
        result=make_report(out,plan,identity)
        write(out/'STATUS.json',dict(stage='COMPLETE',updated_unix=time.time()))
        return dict(stage='COMPLETE',summary=str(out/'SUMMARY.json'),speedup=result['speedup_legacy_over_new'])
    except BaseException as error:
        write(out/f'FAILURE_{time.time_ns()}.json',dict(error=repr(error),traceback=traceback.format_exc(),updated_unix=time.time()))
        write(out/'STATUS.json',dict(stage='FAILED',error=repr(error),updated_unix=time.time()))
        raise
    finally:
        (out/'RUNNING.lock').unlink(missing_ok=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare',action='store_true')
    mode.add_argument('--run',action='store_true')
    mode.add_argument('--inspect',action='store_true')
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--training-run',type=Path,default=RUN)
    parser.add_argument('--output',type=Path,default=OUT)
    args=parser.parse_args()
    if args.prepare: result=prepare(args.root,args.training_run,args.output)
    elif args.run: result=run_comparison(args.output)
    else:
        plan=read(args.output/'PLAN.json')
        ready,state=readiness(Path(plan['training_run']))
        result=dict(ready=ready,stage=state,comparison_status=read(args.output/'STATUS.json'),scenes=plan['scene_count'])
    print(json.dumps(result,ensure_ascii=False,allow_nan=False),flush=True)


if __name__=='__main__':
    main()
