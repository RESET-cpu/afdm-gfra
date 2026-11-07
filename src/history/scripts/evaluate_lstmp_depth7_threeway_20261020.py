"""Frozen 20-scene comparison of trained depth seven, frozen depth five and legacy.

Preparation and auditing use CPU only. Inference starts only after all seven
training stages finish and uses the prior comparison's scoring/timing routines.
"""
import argparse
import ast
import csv
import gc
import importlib.util
import math
import os
from pathlib import Path
import platform
import shutil
import time
import traceback

import numpy as np

CORE_PATH = Path(__file__).with_name('paired_core.py')
if not CORE_PATH.exists():
    CORE_PATH = Path(__file__).with_name('evaluate_lstmp_epoch6_vs_legacy20.py')
_spec = importlib.util.spec_from_file_location('depth7_paired_core', CORE_PATH)
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)
read, write, sha = C.read, C.write, C.sha
ROOT = Path(r'C:\Users\25911\Desktop\afdm-gfra')
RUN = Path(r'D:\afdm-gfra-cpu\runs\lstmp_refinenet_depth7_20261020')
PARENT = RUN.parent/'lstmp_refinenet_50000_epoch6_20261020'
OUT = ROOT/'results/lstmp_depth7_threeway20_20261020'
METHODS = ('new_seven_layer', 'frozen_five_layer', 'legacy_50000_damping01')
DEPTHS = dict(new_seven_layer=7, frozen_five_layer=5)
SEEDS = list(range(202610209700001, 202610209700021))
WARMUP_SEED = 202610209799999
SCHEDULE = (2, 2, 2, 2, 6, 2, 2)


def readiness(run):
    if not (run/'COMPLETE.json').exists():
        return False, 'WAITING_FOR_SUCCESSFUL_TRAINING_COMPLETION'
    complete = read(run/'COMPLETE.json')
    if complete.get('status') != 'COMPLETE':
        raise ValueError('Training did not complete successfully')
    if (run/'RUNNING.lock').exists():
        return False, 'WAITING_FOR_TRAINING_PROCESS_RELEASE'
    for depth, epochs in enumerate(SCHEDULE, 1):
        folder = run/f'checkpoints/depth_{depth}'
        receipt = read(folder/'COMPLETE.json')
        if (receipt.get('status') != 'COMPLETE' or receipt['selected_epoch'] < 1 or
                receipt['steps'] != epochs*4800 or receipt['checkpoint_sha256'] != sha(folder/'best.pt')):
            raise ValueError(f'Incomplete budget or changed checkpoint: depth {depth}')
    if not all(complete['protected_assets_preserved'].values()):
        raise ValueError('A protected asset changed')
    return True, 'READY'


def check_five_forward(run, parent):
    """The extension alters the training loss, not the frozen five-layer forward."""
    a = run/'source_code/experiments/lstmp_candidate_20261019'
    b = parent/'source_code/experiments/lstmp_candidate_20261019'
    files = ('receiver.py', 'message_damping.py', 'data.py', 'backbone.py', 'reuse.py')
    for name in files:
        if sha(a/name) != sha(b/name):
            raise ValueError('Five-layer inference source differs: '+name)
    def functions(path):
        return {n.name: ast.dump(n) for n in ast.parse(path.read_text(encoding='utf-8')).body
                if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    fa, fb = functions(a/'receiver_base.py'), functions(b/'receiver_base.py')
    if set(fa) != set(fb) or any(fa[k] != fb[k] for k in fa if k != 'loss'):
        raise ValueError('Five-layer receiver numerical implementation changed')
    ca, cb = (read(x/'MANIFEST.json')['configuration'] for x in (run, parent))
    for key in ('backbone', 'pretrained_score', 'normalized_training_second_moment', 'complex_variance_support'):
        if ca[key] != cb[key]:
            raise ValueError('Five-layer network/scale differs: '+key)
    for key in ('microbatch', 'variance_calibration_order', 'variance_soft_floor_temperature_ratio',
                'maximum_feedback_variance_ratio', 'activity_threshold', 'phase_mode', 'noise_mode'):
        if ca['receiver'][key] != cb['receiver'][key]:
            raise ValueError('Five-layer inference control differs: '+key)
    return dict(same_forward=True, only_receiver_base_function_changed='loss',
                inference_does_not_call_loss=True, matching_source_files=list(files))


def prepare(root, run, out):
    if out.exists():
        raise FileExistsError(out)
    common, _, _ = C.modules(root, run)
    import torch
    from threadpoolctl import threadpool_limits
    torch.set_num_threads(1); threadpool_limits(1)
    parent = Path(common.CONFIG['depth_extension']['parent_run'])
    if not C.readiness(parent)[0]:
        raise ValueError('Frozen five-layer parent is incomplete')
    compatible = check_five_forward(run, parent)
    seeds = SEEDS+[WARMUP_SEED]
    for split in ('train', 'validation', 'test'):
        cfg = common.CONFIG['receiver']; base = cfg[f'{split}_seed']
        count = cfg.get('case_sources', {}).get(split, {}).get('pool_count', cfg[f'{split}_scenes'])
        if any(base <= seed < base+count for seed in seeds):
            raise ValueError('Comparison seed overlaps a training/selection pool')
    prior_path = root/'runs/proposed_50000_cuda_20261018/data/prior_definition.json'
    for identity in read(prior_path)['dataset_identities'].values():
        if set(identity['scene_seeds']).intersection(seeds):
            raise ValueError('Comparison seed overlaps pretraining')
    previous = root/'results/lstmp_epoch6_vs_legacy20_20261020'
    for folder in (previous, root/'results/lstmp_vs_legacy20_repaired_20261019'):
        p = read(folder/'PLAN.json')
        if ({c['seed'] for c in p['cases']} | {p['warmup']['seed']}).intersection(seeds):
            raise ValueError('Comparison overlaps revealed paired test scenes')
    from experiments.lstmp_candidate_20261019.baseline_evaluation import binding
    cfg, old = binding(dict(name=METHODS[-1],
        configuration='runs/proposed_auxiliary_100_cuda_graph_20261019/n50000/receiver.json', damping=.1))
    if old != read(previous/'PLAN.json')['old_binding']:
        raise ValueError('Legacy binding changed')
    scale = common.CONFIG['pretrained_score']['global_complex_rms']
    assert cfg['scale'] == scale and cfg['decision_threshold'] == .5
    out.mkdir(parents=True); (out/'source').mkdir()
    evaluator = out/'source'/Path(__file__).name
    shutil.copy2(__file__, evaluator)
    shutil.copy2(CORE_PATH, out/'source/paired_core.py')
    auditor = out/'source/verify_lstmp_depth7_threeway20_20261020.py'
    shutil.copy2(root/'scripts'/auditor.name, auditor)
    cases = [dict(index=i, **C.make_case(out/'cases'/f'{i:03d}', seed, scale)) for i, seed in enumerate(SEEDS)]
    warmup = C.make_case(out/'warmup', WARMUP_SEED, scale)
    plan = dict(schema='depth7-threeway-paired20-v1', created_unix=time.time(), root=str(root),
        training_run=str(run), training_manifest_sha256=sha(run/'MANIFEST.json'),
        evaluator_sha256=sha(evaluator), core_sha256=sha(out/'source/paired_core.py'),
        auditor_sha256=sha(auditor),
        methods=list(METHODS), depths=DEPTHS, scene_count=20, condition=C.CONDITION, cases=cases, warmup=warmup,
        scale=scale, phase_mode='known', noise_mode='known', device='cuda', cpu_threads=4, allow_tf32=True,
        activity_threshold=.5, new_microbatch=common.CONFIG['receiver']['microbatch'],
        new_checkpoint='checkpoints/depth_7/best.pt',
        new_selection='Validation-selected depth seven after 86400 cumulative updates; no test-based model selection',
        five_layer_binding=dict(run=str(parent), manifest_sha256=sha(parent/'MANIFEST.json'),
            checkpoint='checkpoints/depth_5/best.pt', checkpoint_sha256=sha(parent/'checkpoints/depth_5/best.pt'),
            complete_sha256=sha(parent/'COMPLETE.json'), source_compatibility=compatible),
        old_binding=old, seeds_independent_of_training_and_selection=True,
        pretraining_prior_sha256=sha(prior_path),
        training_schedule=list(SCHEDULE), additional_updates=19200, cumulative_updates=86400,
        timing=read(previous/'PLAN.json')['timing'],
        execution='Seven, frozen five, then legacy; one resident model at a time. No concurrent GPU training.',
        metrics='Pooled full-channel NMSE and scene-average NMSE; missed detections, false alarms, their conditional rates, AER and synchronized wall time. Inactive-user errors retained.',
        limitations='Twenty independent scenes at K40/Q16/p0.1/SNR5dB, known phase/noise. Frozen legacy may hit 600 iterations; finite-depth networks are not declared converged. Speed is not an equal-accuracy comparison.',
        failures='Keep all planned scenes and failed attempts. No threshold or weight changes on test labels.',
        next_depth_policy='Stop after depth seven and its comparison; depth nine is not authorized by this run.')
    write(out/'PLAN.json', plan)
    write(out/'STATUS.json', dict(stage='WAITING_FOR_TRAINING', updated_unix=time.time()))
    return dict(status='PREPARED', output=str(out), scenes=20, methods=METHODS, gpu_used=False)


def verify_plan(out, plan):
    root, run = Path(plan['root']), Path(plan['training_run'])
    for path, digest in ((Path(__file__), plan['evaluator_sha256']), (CORE_PATH, plan['core_sha256']),
                         (out/'source/verify_lstmp_depth7_threeway20_20261020.py', plan['auditor_sha256']),
                         (run/'MANIFEST.json', plan['training_manifest_sha256'])):
        if sha(path) != digest: raise ValueError('Frozen file changed: '+str(path))
    parent = Path(plan['five_layer_binding']['run']); five = plan['five_layer_binding']
    for path, digest in ((parent/'MANIFEST.json', five['manifest_sha256']),
                         (parent/five['checkpoint'], five['checkpoint_sha256']),
                         (parent/'COMPLETE.json', five['complete_sha256'])):
        if sha(path) != digest: raise ValueError('Five-layer binding changed: '+str(path))
    check_five_forward(run, parent)
    for source in (run, parent):
        manifest = read(source/'MANIFEST.json')
        for path, digest in manifest['snapshot_hashes'].items():
            if sha(path) != digest: raise ValueError('Frozen source changed: '+path)
        for path, digest in manifest['protected_assets'].items():
            if sha(root/path) != digest: raise ValueError('Protected asset changed: '+path)
    for folder, case in [(out/'cases'/f'{c["index"]:03d}', c) for c in plan['cases']]+[(out/'warmup', plan['warmup'])]:
        for name in ('input', 'truth', 'generation'):
            path = folder/(name+('.json' if name == 'generation' else '.npz'))
            if sha(path) != case[name+'_sha256']: raise ValueError('Paired input changed: '+str(path))


class Adapter:
    def __init__(self, method, plan, common, data, receiver):
        import torch
        self.method, self.plan, self.data, self.scale = method, plan, data, plan['scale']
        self.depth = DEPTHS.get(method)
        if self.depth is None:
            self.legacy = C.Adapter(C.METHODS[-1], plan, common, data, receiver)
            self.networks, self.checkpoint_bytes = self.legacy.networks, self.legacy.checkpoint_bytes
        else:
            if self.depth == 7:
                path = Path(plan['training_run'])/plan['new_checkpoint']
            else:
                five = plan['five_layer_binding']; path = Path(five['run'])/five['checkpoint']
            state = torch.load(path, map_location='cpu', weights_only=False)
            if state['depth'] != self.depth: raise ValueError('Wrong checkpoint depth')
            self.model = receiver.Receiver()
            for _ in range(self.depth): self.model.add_layer(None)
            self.model.load_state_dict(state['state']); del state
            self.model.cuda().eval(); self.model.use_checkpoint = False
            self.networks, self.checkpoint_bytes = [self.model], path.stat().st_size

    def prepare(self, public):
        if self.depth is None: return self.legacy.prepare(public)
        values = dict(y=public.observation, a=public.operator, noise=public.noise_variance, rho=public.activity_prior)
        return self.data.prepare_public(values, self.scale, 'cuda', phase_mode='known', noise_mode='known')[0]

    def infer(self, prepared):
        if self.depth is None: return self.legacy.infer(prepared)
        import torch
        outputs, diagnostics = self.model(prepared)
        x, logits = outputs[-1]; real = x.cpu().numpy()
        estimate = (real[:, 0].astype(np.float64)+1j*real[:, 1].astype(np.float64))*self.scale
        p = torch.sigmoid(logits).cpu().numpy(); users = len(p)
        record = dict(iterations=self.depth, converged=None, stopping_reason=f'FIXED_{self.depth}_LAYERS',
            first_score_calls=self.depth*math.ceil(users/self.plan['new_microbatch']), first_score_samples=self.depth*users,
            second_score_calls=0, second_score_samples=0, classifier_calls=self.depth, classifier_samples=self.depth*users,
            diagnostics=diagnostics)
        return dict(estimate=estimate, probabilities=p), record


def summarize(rows):
    result = C.summarize(rows)
    result['fixed_depth_scenes'] = sum(r['stopping_reason'].startswith('FIXED_') for r in rows)
    result['missed_detection_rate'] = result['misses']/result['active'] if result['active'] else None
    result['false_alarm_rate'] = result['false_alarms']/result['inactive'] if result['inactive'] else None
    return result


def make_report(out, plan, identity):
    paired, methods = {}, {}
    for method in METHODS:
        rows = [read(out/method/f'{c["index"]:03d}.json') for c in plan['cases']]
        for row, case in zip(rows, plan['cases']):
            if (row['status'] != 'COMPLETE' or row['seed'] != case['seed'] or row['case_index'] != case['index'] or
                row['input_sha256'] != case['input_sha256'] or row['prediction_sha256'] != sha(out/method/f'{case["index"]:03d}.npz')):
                raise ValueError('Paired prediction changed')
        paired[method] = rows
        methods[method] = dict(**summarize(rows), **read(out/method/'OVERHEAD.json'))
    comparisons = {}
    for other in METHODS[1:]:
        a, b = methods[METHODS[0]], methods[other]
        comparisons[other] = dict(seven_minus_other_nmse_db=a['pooled_nmse_db']-b['pooled_nmse_db'],
            seven_minus_other_aer=a['aer']-b['aer'], other_over_seven_seconds=b['mean_seconds']/a['mean_seconds'],
            seven_lower_nmse_scenes=sum(x['nmse'] < y['nmse'] for x, y in zip(paired[METHODS[0]], paired[other])))
    run = Path(plan['training_run']); total = read(run/'COMPLETE.json')['seconds']
    inherited = read(run/'protocol/DEPTH_EXTENSION.json')['inherited_training_seconds']
    report = dict(status='COMPLETE', identity=identity, condition=plan['condition'], phase_mode='known', noise_mode='known',
        methods=methods, paired_seven_comparisons=comparisons,
        training_overhead=dict(cumulative_finetuning_seconds=total, inherited_finetuning_seconds=inherited,
            depth_extension_seconds=total-inherited, historical_pretraining_seconds=None), limitations=plan['limitations'])
    write(out/'SUMMARY.json', report)
    for filename, rows in [('summary.csv', [dict(method=m, **methods[m]) for m in METHODS]),
                           ('per_scene.csv', [dict(method=m, **r) for m in METHODS for r in paired[m]])]:
        with (out/filename).open('w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.8), constrained_layout=True)
    labels = ['7 layers', 'Frozen 5', 'Legacy']
    for ax, key, title in zip(axes, ['pooled_nmse_db', 'misses', 'false_alarms', 'mean_seconds'],
                             ['Full-channel NMSE (dB)', 'Missed detections', 'False alarms', 'Mean time / scene (s)']):
        values = [methods[m][key] for m in METHODS]
        bars = ax.bar(labels, values, color=['#227C9D', '#65A879', '#ED8B3A'])
        ax.bar_label(bars, fmt='%.3f' if key in ('mean_seconds', 'pooled_nmse_db') else '%.0f', padding=4)
        if key == 'mean_seconds': ax.set_yscale('log')
        ax.set_title(title, fontsize=10); ax.margins(y=.3); ax.grid(axis='y', alpha=.2); ax.set_axisbelow(True)
    fig.suptitle('20 paired new scenes | K=40, Q=16, p=0.1, SNR=5 dB | Known phase/noise')
    fig.savefig(out/'comparison.png', dpi=180); fig.savefig(out/'comparison.pdf'); plt.close(fig)
    write(out/'COMPLETE.json', dict(status='COMPLETE', completed_unix=time.time(), plan_sha256=sha(out/'PLAN.json'),
        summary_sha256=sha(out/'SUMMARY.json'), scene_counts=dict.fromkeys(METHODS, plan['scene_count'])))
    return report


def run_comparison(out):
    plan = read(out/'PLAN.json'); root, run = Path(plan['root']), Path(plan['training_run'])
    ready, state = readiness(run)
    if not ready: return dict(stage=state, evaluation_started=False)
    verify_plan(out, plan)
    if (out/'COMPLETE.json').exists(): return dict(stage='ALREADY_COMPLETE')
    fd = os.open(out/'RUNNING.lock', os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    os.write(fd, str(os.getpid()).encode()); os.close(fd)
    try:
        common, data, receiver = C.modules(root, run)
        import torch
        from threadpoolctl import threadpool_limits
        from afdm_jadcedd.system.observation import load_input
        torch.set_num_threads(plan['cpu_threads']); threadpool_limits(plan['cpu_threads'])
        torch.backends.cuda.matmul.allow_tf32 = plan['allow_tf32']; torch.backends.cudnn.allow_tf32 = plan['allow_tf32']
        torch.backends.cudnn.benchmark = True
        identity = dict(plan_sha256=sha(out/'PLAN.json'), selected_seven_sha256=sha(run/plan['new_checkpoint']),
            frozen_five_sha256=plan['five_layer_binding']['checkpoint_sha256'],
            training_complete_sha256=sha(run/'COMPLETE.json'), torch=torch.__version__, cuda=torch.version.cuda,
            cudnn=torch.backends.cudnn.version(), gpu=torch.cuda.get_device_name(), python=platform.python_version())
        if (out/'BINDING.json').exists() and read(out/'BINDING.json') != identity:
            raise ValueError('Evaluation weights/environment changed on resume')
        write(out/'BINDING.json', identity)
        for method in METHODS:
            folder = out/method; folder.mkdir(exist_ok=True)
            if all((folder/f'{i:03d}.json').exists() for i in range(plan['scene_count'])): continue
            gc.collect(); torch.cuda.empty_cache(); torch.cuda.synchronize(); start = time.perf_counter()
            adapter = Adapter(method, plan, common, data, receiver); torch.cuda.synchronize()
            overhead = dict(C.model_size(adapter.networks), checkpoint_file_bytes=adapter.checkpoint_bytes,
                            model_load_seconds=time.perf_counter()-start)
            C.timed_inference(adapter, load_input(out/'warmup/input.npz')); torch.cuda.empty_cache()
            if not (folder/'OVERHEAD.json').exists(): write(folder/'OVERHEAD.json', overhead)
            for case in plan['cases']:
                i = case['index']; path = folder/f'{i:03d}.json'
                if path.exists():
                    row = read(path)
                    if row['status'] != 'COMPLETE' or row['input_sha256'] != case['input_sha256']:
                        raise ValueError('Invalid saved scene')
                    continue
                write(out/'STATUS.json', dict(stage='EVALUATING', pid=os.getpid(), method=method,
                    scene=i+1, total=plan['scene_count'], updated_unix=time.time()))
                public = load_input(out/'cases'/f'{i:03d}'/'input.npz')
                arrays, record, times = C.timed_inference(adapter, public)
                with np.load(out/'cases'/f'{i:03d}'/'truth.npz', allow_pickle=False) as truth:
                    metrics = C.score_arrays(arrays['estimate'], arrays['probabilities'], truth['channel'], truth['activity'])
                np.savez_compressed(folder/f'{i:03d}.npz', **arrays); write(folder/f'{i:03d}_trace.json', record)
                keys = ('iterations', 'converged', 'stopping_reason', 'first_score_calls', 'second_score_calls',
                        'classifier_calls', 'first_score_samples', 'second_score_samples', 'classifier_samples')
                write(path, dict(status='COMPLETE', case_index=i, seed=case['seed'], input_sha256=case['input_sha256'],
                    prediction_sha256=sha(folder/f'{i:03d}.npz'), **metrics, **times, **{k: record[k] for k in keys}))
                print(method, i+1, metrics['nmse'], times['total_seconds'], flush=True)
                del arrays, record, public
            del adapter; gc.collect(); torch.cuda.empty_cache()
        verify_plan(out, plan); make_report(out, plan, identity)
        write(out/'STATUS.json', dict(stage='COMPLETE', updated_unix=time.time()))
        return dict(stage='COMPLETE', summary=str(out/'SUMMARY.json'))
    except BaseException as error:
        write(out/f'FAILURE_{time.time_ns()}.json', dict(error=repr(error), traceback=traceback.format_exc()))
        write(out/'STATUS.json', dict(stage='FAILED', error=repr(error), updated_unix=time.time()))
        raise
    finally:
        (out/'RUNNING.lock').unlink(missing_ok=True)


def main():
    p = argparse.ArgumentParser(description=__doc__); modes = p.add_mutually_exclusive_group(required=True)
    modes.add_argument('--prepare', action='store_true'); modes.add_argument('--run', action='store_true')
    modes.add_argument('--inspect', action='store_true'); p.add_argument('--output', type=Path, default=OUT)
    args = p.parse_args()
    if args.prepare: result = prepare(ROOT, RUN, args.output)
    elif args.run: result = run_comparison(args.output)
    else:
        plan = read(args.output/'PLAN.json'); verify_plan(args.output, plan)
        ready, state = readiness(Path(plan['training_run']))
        result = dict(ready=ready, stage=state, comparison_status=read(args.output/'STATUS.json'))
    import json
    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == '__main__': main()
