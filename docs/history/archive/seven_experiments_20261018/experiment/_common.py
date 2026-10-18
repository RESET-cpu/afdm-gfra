"""Shared generation, native receiver calls and scoring for the four experiments."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import os
import sys
import time
import traceback
import warnings

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT)]
import numpy as np
from afdm_jadcedd.algorithm import phase_estimation_optimized as phase
from afdm_jadcedd.algorithm.baselines.baseline_noise import EstimatedNoiseBaselineReceiver
from afdm_jadcedd.algorithm.proposed_noise_candidate import EstimatedNoiseProposedReceiver
from afdm_jadcedd.algorithm.unknown_phase_model import UnknownPhaseInput
from afdm_jadcedd.experiment.unknown_phase import generate_case
from afdm_jadcedd.experiment.evaluation.metrics import score_arrays
from afdm_jadcedd.system.observation import array_sha256, ReceiverInput
from afdm_jadcedd.system.phase import phase_operator

METHODS = ['proposed', 'offgrid_sbl', 'gnn', 'gamp', 'somp']
CONFIGS = dict(proposed='configs/proposed.json', offgrid_sbl='configs/offgrid_baselines.json',
               gnn='configs/baselines.json', gamp='configs/baselines.json', somp='configs/baselines.json')
LABELS = dict(proposed='Proposed', offgrid_sbl='Off-grid SBL', gnn='GNN-ASPL', gamp='GAMP-SBL', somp='SOMP')


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f'.{os.getpid()}.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    temp.replace(path)


def save_arrays(path, arrays):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f'.{os.getpid()}.tmp')
    with temp.open('wb') as f:
        np.savez_compressed(f, **arrays)
    temp.replace(path)


def condition(spec, value):
    parameters = {key: spec[key] for key in ('snr_db', 'frames', 'users', 'activity_probability')}
    parameters[spec['variable']] = value
    return parameters


def observation(seed, parameters, scale):
    """Use the completed 500-scene protocol's zero-dB draw and paired noise."""
    kwargs = {k: parameters[k] for k in ('frames', 'users', 'activity_probability')}
    public, truth, metadata = generate_case(seed, 0., scale, **kwargs)
    clean = np.einsum('qkn,kmrn->qmr', phase_operator(public['pilot'], truth['phase_slopes']),
                      truth['channel'], optimize=False)
    power = float(np.mean(abs(clean)**2))
    epsilon = (public['observation'] - clean) / np.sqrt(public['noise_variance'])
    variance = power * 10**(-parameters['snr_db'] / 10)
    # Only observation, pilot and prior go to the estimated-noise receiver.
    inputs = UnknownPhaseInput(clean + np.sqrt(variance)*epsilon, public['pilot'], 1., public['activity_prior'])
    metadata = dict(metadata, snr_db=parameters['snr_db'], noise_mode='estimated',
                    generated_noise_variance=variance)
    return inputs, truth, metadata


def validate(spec):
    if spec['scenes'] < 1 or not spec['values'] or len(set(spec['values'])) != len(spec['values']):
        raise ValueError('Positive scene count and distinct conditions required')
    for value in spec['values']:
        p = condition(spec, value)
        if not np.isfinite(list(p.values())).all() or not 0 < p['activity_probability'] < 1:
            raise ValueError('Finite parameters and activity probability in (0, 1) required')
        if int(p['users']) != p['users'] or p['users'] < 2 or int(p['frames']) != p['frames'] or not 1 <= p['frames'] <= 32:
            raise ValueError('At least two users and 1–32 integer pilot frames required')


def identities():
    files = [ROOT / 'MAINLINE.json']
    for directory, pattern in [('src', '*.py'), ('configs', '*.json'), ('experiment', '*.py'),
                               ('models/proposed', '*'), ('models/gnn', '*')]:
        files.extend(p for p in (ROOT / directory).rglob(pattern) if p.is_file())
    return {str(p.relative_to(ROOT)): sha(p) for p in files}


def verify_sources(plan):
    for name, expected in plan['source_and_weight_sha256'].items():
        if sha(ROOT / name) != expected:
            raise ValueError('Experiment source or weight changed: ' + name)


def aggregate(spec, records):
    rows = []
    for index, value in enumerate(spec['values']):
        for method in spec['methods']:
            group = [r for r in records if r['condition'] == index and r['method'] == method]
            complete = [r for r in group if r['status'] == 'COMPLETE']
            row = dict(method=method, value=value, planned=spec['scenes'], completed=len(complete),
                       failed=sum(r['status'] == 'FAILED' for r in group), missing=spec['scenes']-len(group))
            row['status'] = 'COMPLETE' if len(complete) == spec['scenes'] else 'INCOMPLETE'
            if row['status'] == 'COMPLETE':
                sums = {key: sum(r['metrics'][key] for r in complete) for key in
                        ('active', 'inactive', 'misses', 'false_alarms', 'full_error', 'signal_energy')}
                users = sums['active'] + sums['inactive']
                ratio = sums['full_error']/sums['signal_energy']
                row.update(sums, aer=(sums['misses']+sums['false_alarms'])/users,
                           nmse_db=float(10*np.log10(ratio)) if ratio else None,
                           exact_zero_error=ratio == 0, average_active_users=sums['active']/len(complete),
                           receiver_seconds_median=float(np.median([r['receiver_seconds'] for r in complete])))
            rows.append(row)
    return rows


def summarize(out, spec):
    records = []
    for scene in range(spec['scenes']):
        for index in range(len(spec['values'])):
            folder = out / f'scene{scene:03d}' / f'condition{index:02d}'
            for method in spec['methods']:
                path = folder / f'{method}.json'
                if not path.exists():
                    continue
                row = read(path)
                if (row['scene'], row['condition'], row['method']) != (scene, index, method):
                    raise ValueError('Result identity differs: ' + str(path))
                if row['status'] == 'COMPLETE' and sha(folder / f'{method}.npz') != row['compact_sha256']:
                    raise ValueError('Result content differs: ' + str(path))
                records.append(row)
    rows = aggregate(spec, records)
    status = 'COMPLETE' if all(r['status'] == 'COMPLETE' for r in rows) else 'INCOMPLETE'
    save(out / 'SUMMARY.json', dict(status=status, rows=rows, phase_mode='estimated', noise_mode='estimated',
         statistics='Pooled counts and channel energies; point estimates only, no significance claims.',
         timing='Sequential conditional receivers; shared phase estimation recorded separately.'))
    with (out / 'STATISTICS.csv').open('w', newline='') as f:
        fields = list(dict.fromkeys(k for row in rows for k in row))
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)
    if status == 'COMPLETE':
        plot(out, spec, rows)
    print(json.dumps(dict(status=status, output=str(out), completed=sum(r['completed'] for r in rows))))
    return 0 if status == 'COMPLETE' else 1


def plot(out, spec, rows):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout='constrained')
    zero_aer, zero_error = [], []
    for method in spec['methods']:
        group = sorted([r for r in rows if r['method'] == method], key=lambda r: r['value'])
        x = [r['value'] for r in group]
        axes[0].plot(x, [r['aer'] if r['aer'] else np.nan for r in group], marker='o', label=LABELS[method])
        axes[1].plot(x, [r['nmse_db'] for r in group], marker='o', label=LABELS[method])
        zeros = [str(r['value']) for r in group if r['aer'] == 0]
        exact = [str(r['value']) for r in group if r['exact_zero_error']]
        if zeros:
            zero_aer.append(f'{LABELS[method]}: AER = 0 at ' + ', '.join(zeros))
        if exact:
            zero_error.append(f'{LABELS[method]}: NMSE = −∞ dB at ' + ', '.join(exact))
    axes[0].set_yscale('log')
    if not any(r['aer'] > 0 for r in rows):
        axes[0].set_ylim(1e-5, 1)
    axes[0].set_ylabel('Activity error rate')
    axes[1].set_ylabel('Full-channel NMSE (dB)')
    for ax in axes:
        ax.set_xlabel(spec['xlabel']); ax.grid(alpha=.25); ax.legend(fontsize=8)
        ax.set_xticks(sorted(spec['values']))
    for ax, notes in zip(axes, (zero_aer, zero_error)):
        if notes:
            ax.text(.03, .03, '\n'.join(notes), transform=ax.transAxes, fontsize=7,
                    va='bottom', bbox=dict(facecolor='white', alpha=.9, edgecolor='none'))
    noun = 'scene' if spec['scenes'] == 1 else 'scenes'
    fig.suptitle(f'{spec["scenes"]} {noun} per condition; estimated phase and noise')
    for suffix in ('png', 'pdf'):
        fig.savefig(out / f'comparison.{suffix}', dpi=180)
    plt.close(fig)


def run(out, plan):
    import torch
    from threadpoolctl import threadpool_limits
    verify_sources(plan)
    spec = plan['experiment']
    torch.set_num_threads(1)
    controls = phase.Controls(**read(ROOT / 'configs/proposed_frontend.json')['phase_estimation'])
    with threadpool_limits(1):
        solvers = {m: (EstimatedNoiseProposedReceiver(read(ROOT / CONFIGS[m]), device=spec['device']) if m == 'proposed'
                       else EstimatedNoiseBaselineReceiver(m, config=ROOT / CONFIGS[m], device=spec['device']))
                   for m in spec['methods']}
        for scene in range(spec['scenes']):
            for index, value in enumerate(spec['values']):
                folder = out / f'scene{scene:03d}' / f'condition{index:02d}'
                pending = []
                for method in spec['methods']:
                    path = folder / f'{method}.json'
                    if not path.exists():
                        pending.append(method); continue
                    row = read(path)
                    if row['status'] != 'COMPLETE' or sha(folder / f'{method}.npz') != row['compact_sha256']:
                        raise ValueError('Preserved failure or changed result requires inspection: ' + str(path))
                if not pending:
                    continue
                inputs, truth, metadata = observation(spec['seed']+scene, condition(spec, value), spec['scale'])
                input_hash = {k: array_sha256(v) for k, v in inputs.arguments().items()}
                ready = folder / 'INPUT.json'
                if ready.exists() and read(ready)['arrays'] != input_hash:
                    raise ValueError('Regenerated observation differs: ' + str(folder))
                save(ready, dict(arrays=input_hash, generation=metadata))
                save_arrays(folder / 'truth.npz', truth)
                with warnings.catch_warnings(record=True) as notices:
                    warnings.simplefilter('always', RuntimeWarning)
                    values, phase_record = phase.estimate(inputs, controls)
                save(folder / 'PHASE_WARNINGS.json', [str(w.message) for w in notices])
                save(folder / 'PHASE.json', phase_record)
                conditional = inputs.at_estimated_phase(values['phase_slopes'])
                conditional = ReceiverInput(conditional.observation, conditional.operator, 1., conditional.activity_prior)
                for method in pending:
                    target = folder / f'{method}.json'
                    base = dict(scene=scene, condition=index, method=method, input_array_sha256=input_hash,
                                phase_mode='estimated', noise_mode='estimated', truth_used_in_inference=False)
                    try:
                        with warnings.catch_warnings(record=True) as notices:
                            warnings.simplefilter('always', RuntimeWarning)
                            arrays, record = solvers[method].infer(conditional)
                        if record.get('status', 'COMPLETE') != 'COMPLETE' or not all(np.isfinite(v).all() for v in arrays.values()):
                            raise FloatingPointError('Incomplete or nonfinite receiver output')
                        metrics = score_arrays(arrays, truth)
                        compact = {k: v for k, v in arrays.items() if np.asarray(v).ndim <= 1}
                        compact.update(per_user_error=np.asarray(metrics['per_user_error']), truth_activity=truth['activity'])
                        save_arrays(folder / f'{method}.npz', compact)
                        if scene == 0:
                            save_arrays(folder / f'{method}.prediction.npz', arrays)
                        save(folder / f'{method}.record.json', record)
                        save(target, dict(base, status='COMPLETE', metrics=metrics, receiver_seconds=record['seconds'],
                             phase_seconds=phase_record['seconds'], compact_sha256=sha(folder / f'{method}.npz'),
                             output_array_sha256={k: array_sha256(v) for k, v in arrays.items()},
                             warnings=[str(w.message) for w in notices]))
                    except Exception:
                        save(target, dict(base, status='FAILED', traceback=traceback.format_exc()))
                        raise
                    print(f'{scene + 1}/{spec["scenes"]} {spec["variable"]}={value} {method}', flush=True)
    verify_sources(plan)
    return summarize(out, spec)


def main(defaults, argv=None):
    parser = argparse.ArgumentParser(description=defaults['description'])
    parser.add_argument('command', choices=('plan', 'run', 'summarize', 'saved'))
    parser.add_argument('--output', type=Path, help='Fresh results directory; required except for saved')
    parser.add_argument('--scenes', type=int, default=defaults['scenes'])
    parser.add_argument('--seed', type=int, default=defaults['seed'])
    parser.add_argument('--values', type=float, nargs='+', default=defaults['values'])
    parser.add_argument('--methods', nargs='+', choices=METHODS, default=METHODS)
    parser.add_argument('--device', choices=('cpu', 'mps', 'auto'), default='cpu')
    args = parser.parse_args(argv)
    if args.command == 'saved':
        if defaults['variable'] != 'snr_db':
            parser.error('This experiment has no completed mainline result yet')
        print((ROOT / 'results/baseline_comparison_500_20261018/REPORT.md').read_text())
        return 0
    if args.output is None:
        parser.error('--output is required')
    out = args.output.resolve()
    if args.command == 'plan':
        if out.exists() and any(out.iterdir()):
            raise FileExistsError('Plan requires a fresh empty directory: ' + str(out))
        spec = dict(defaults, scenes=args.scenes, seed=args.seed, values=args.values,
                    methods=list(dict.fromkeys(args.methods)), device=args.device,
                    scale=read(ROOT / 'configs/proposed.json')['scale'])
        if spec['variable'] in ('users', 'frames'):
            if any(int(v) != v for v in spec['values']):
                raise ValueError('Integer dimension values required')
            spec['values'] = [int(v) for v in spec['values']]
        validate(spec)
        save(out / 'PLAN.json', dict(experiment=spec, source_and_weight_sha256=identities(), created_unix=time.time(),
             pairing='Same public observation for all methods within each condition; same seed index across conditions.',
             information='Estimated phase and noise; frozen receiver weights and decision rules.',
             expected_runs=spec['scenes']*len(spec['values'])*len(spec['methods'])))
        print(json.dumps(dict(status='PLANNED', output=str(out))))
        return 0
    plan = read(out / 'PLAN.json')
    if plan['experiment']['variable'] != defaults['variable']:
        raise ValueError('Use the experiment entry matching this plan')
    # Run and summarize use the saved plan; CLI settings only apply to plan.
    return run(out, plan) if args.command == 'run' else summarize(out, plan['experiment'])
