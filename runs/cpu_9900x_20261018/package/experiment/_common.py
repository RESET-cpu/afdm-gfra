"""Shared receiver experiment: observations, phase, paired inference and reporting."""
from pathlib import Path
import argparse
import csv
import json
import sys
import time
import traceback
import warnings
from dataclasses import asdict
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _support import ROOT
from _support.storage import read, save, sha, save_arrays, arrays, identities, verify_sources, pending_methods
from _support.pairing import preserve as preserve_pairing
from _support.settings import (METHODS, CONFIGS, LABELS, DEFAULTS, SNR_VALUES, PHASE_CONFIG, HISTORICAL_SNR,
                               proposed_bundles, method_label, solver, bind_receivers, validate_seed, validate_methods)
import numpy as np
from afdm_jadcedd.algorithm import phase_estimation_optimized as phase
from afdm_jadcedd.algorithm.baselines.baseline_noise import EstimatedNoiseBaselineReceiver
from afdm_jadcedd.algorithm.proposed_noise_candidate import EstimatedNoiseProposedReceiver
from afdm_jadcedd.algorithm.unknown_phase_model import UnknownPhaseInput
from afdm_jadcedd.experiment.unknown_phase import generate_case
from afdm_jadcedd.experiment.evaluation.metrics import score_arrays
from afdm_jadcedd.system.observation import array_sha256, ReceiverInput
from afdm_jadcedd.system.phase import phase_operator
from afdm_jadcedd.system.pilot import PartialDFTPilot

def condition(spec, value):
    parameters = {key: spec[key] for key in ('snr_db', 'frames', 'users', 'activity_probability')}
    if spec['variable'] == 'channel_model':
        model, snr = value.split('/')
        parameters.update(channel_model=model, snr_db=float(snr))
    else:
        parameters[spec['variable']] = value
    return parameters


def observation(seed, parameters, scale, *, generator=generate_case):
    """Use the completed 500-scene protocol's zero-dB draw and paired noise."""
    kwargs = {k: parameters[k] for k in ('frames', 'users', 'activity_probability')}
    frames = int(kwargs['frames'])
    if not 1 <= frames <= min(48, int(kwargs['users'])*16):
        raise ValueError('Pilot frames must be in [1, min(48, users*16)]')
    kwargs['frames'] = min(frames, 32)
    if 'channel_model' in parameters:
        public, truth, metadata = generator(seed, 0., scale, profile=parameters['channel_model'], **kwargs)
    else:
        public, truth, metadata = generator(seed, 0., scale, **kwargs)
    clean = np.einsum('qkn,kmrn->qmr', phase_operator(public['pilot'], truth['phase_slopes']),
                      truth['channel'], optimize=False)
    power = float(np.mean(abs(clean)**2))
    epsilon = (public['observation'] - clean) / np.sqrt(public['noise_variance'])
    pilot = public['pilot']
    if frames > 32:
        # Preserve the frozen generator and all <=32-frame numerical results.
        pilot = PartialDFTPilot(parameters['users'], frames, seed+10**12).dense().reshape(frames, parameters['users'], 16)
        np.testing.assert_array_equal(pilot[:32], public['pilot'])
        rng = np.random.default_rng(np.random.SeedSequence([seed, 2097]))
        shape = (16, *epsilon.shape[1:])
        extra = (rng.normal(size=shape)+1j*rng.normal(size=shape))/np.sqrt(2)
        epsilon = np.concatenate([epsilon, extra[:frames-32]])
        clean = np.einsum('qkn,kmrn->qmr', phase_operator(pilot, truth['phase_slopes']), truth['channel'], optimize=False)
        power = float(np.mean(abs(clean)**2))
        metadata = dict(metadata, frames=frames, parent_generator_version=metadata['generator_version'],
                        generator_version='unknown_phase_extended_frames_v1', frame_extension='paired_33_to_48_v1',
                        extension_noise_seed=[seed, 2097], pilot_sha256=array_sha256(pilot),
                        standardized_noise_sha256=array_sha256(epsilon), physical_clean_power=power)
    variance = power * 10**(-parameters['snr_db'] / 10)
    # Only observation, pilot and prior go to the estimated-noise receiver.
    inputs = UnknownPhaseInput(clean + np.sqrt(variance)*epsilon, pilot, 1., public['activity_prior'])
    metadata = dict(metadata, snr_db=parameters['snr_db'], noise_mode='estimated',
                    generated_noise_variance=variance)
    if frames > 32:
        metadata['noise_variance'] = variance
    return inputs, truth, metadata


def validate(spec):
    validate_seed(spec['seed'])
    validate_methods(spec['methods'])
    if spec['scenes'] < 1 or not spec['values'] or len(set(spec['values'])) != len(spec['values']):
        raise ValueError('Positive scene count and distinct conditions required')
    for value in spec['values']:
        p = condition(spec, value)
        if not np.isfinite([v for k, v in p.items() if k != 'channel_model']).all() or not 0 < p['activity_probability'] < 1:
            raise ValueError('Finite parameters and activity probability in (0, 1) required')
        if int(p['users']) != p['users'] or p['users'] < 2 or int(p['frames']) != p['frames'] or not 1 <= p['frames'] <= min(48, p['users']*16):
            raise ValueError('At least two users and 1–min(48, users*16) integer pilot frames required')


def estimated_phase(inputs, folder, controls, *, reused=None):
    """Reuse a verified local or historical phase estimate before computing it."""
    identity = dict(inputs={k: array_sha256(v) for k, v in inputs.arguments().items()}, controls=asdict(controls))
    cache = folder / 'PHASE_CACHE.json'
    if cache.exists():
        saved = read(cache)
        if saved['identity'] != identity or saved['phase_sha256'] != sha(folder / 'phase.npz'):
            raise ValueError('Saved phase input, configuration or arrays changed')
        return arrays(folder / 'phase.npz'), read(folder / 'PHASE.json')
    if reused is None:
        with warnings.catch_warnings(record=True) as notices:
            warnings.simplefilter('always', RuntimeWarning)
            values, record = phase.estimate(inputs, controls)
        notices = [str(w.message) for w in notices]
    else:
        values, record, notices = reused
    save_arrays(folder / 'phase.npz', values)
    save(folder / 'PHASE.json', record)
    save(folder / 'PHASE_WARNINGS.json', notices)
    save(cache, dict(identity=identity, phase_sha256=sha(folder / 'phase.npz'), reused=reused is not None))
    return values, record


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
                if all('iterations' in r and 'stopping_reason' in r for r in complete):
                    reasons = Counter(r['stopping_reason'] for r in complete)
                    row.update(mean_iterations=float(np.mean([r['iterations'] for r in complete])),
                               stopping_counts=dict(reasons))
                    if method == 'offgrid_sbl':
                        row.update(stopping_condition_met=reasons['HYPERPARAMETER_CHANGE'],
                                   maximum_iterations_reached=reasons['MAX_ITERATIONS'])
            rows.append(row)
    return rows


def summarize(out, spec, *, plotter=None):
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
                for source, digest in row.get('reused_from', {}).items():
                    if sha(ROOT / source) != digest:
                        raise ValueError('Reused result source changed: ' + source)
                records.append(row)
    rows = aggregate(spec, records)
    status = 'COMPLETE' if all(r['status'] == 'COMPLETE' for r in rows) else 'INCOMPLETE'
    save(out / 'SUMMARY.json', dict(status=status, rows=rows, phase_mode='estimated', noise_mode='estimated',
         training_sample_comparison=spec.get('training_sample_comparison', 'NOT_APPLICABLE'),
         reused_results=sum(bool(r.get('reused_from')) for r in records),
         newly_computed_results=sum(r['status'] == 'COMPLETE' and not r.get('reused_from') for r in records),
         statistics='Pooled counts and channel energies; point estimates only, no significance claims.',
         timing='Receiver times retain their original run context; reused and new times are not an isolated speed benchmark.'))
    with (out / 'STATISTICS.csv').open('w', newline='') as f:
        fields = list(dict.fromkeys(k for row in rows for k in row))
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)
    if status == 'COMPLETE':
        (plotter or plot)(out, spec, rows)
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
        label = method_label(spec, method)
        axes[0].plot(x, [r['aer'] if r['aer'] else np.nan for r in group], marker='o', label=label)
        axes[1].plot(x, [r['nmse_db'] for r in group], marker='o', label=label)
        zeros = [str(r['value']) for r in group if r['aer'] == 0]
        exact = [str(r['value']) for r in group if r['exact_zero_error']]
        if zeros:
            zero_aer.append(f'{label}: AER = 0 at ' + ', '.join(zeros))
        if exact:
            zero_error.append(f'{label}: NMSE = −∞ dB at ' + ', '.join(exact))
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


def run(out, plan, *, generator=generate_case, plotter=None, receiver_factory=solver):
    import torch
    from threadpoolctl import threadpool_limits
    from _support.reuse import HistoricalSNR
    verify_sources(plan)
    spec = plan['experiment']
    torch.set_num_threads(1)
    controls = phase.Controls(**read(ROOT / spec.get('phase_config', PHASE_CONFIG))['phase_estimation'])
    historical = HistoricalSNR(spec)
    with threadpool_limits(1):
        solvers = {m: receiver_factory(m, spec) for m in spec['methods']}
        for scene in range(spec['scenes']):
            for index, value in enumerate(spec['values']):
                folder = out / f'scene{scene:03d}' / f'condition{index:02d}'
                pending = pending_methods(folder, spec['methods'])
                if not pending:
                    continue
                parameters = condition(spec, value)
                reused_case = historical.case(spec['seed']+scene, parameters)
                if reused_case is None:
                    inputs, truth, metadata = observation(spec['seed']+scene, parameters, spec['scale'], generator=generator)
                else:
                    inputs, truth, metadata = [reused_case[k] for k in ('inputs', 'truth', 'metadata')]
                input_hash = {k: array_sha256(v) for k, v in inputs.arguments().items()}
                ready = folder / 'INPUT.json'
                if ready.exists() and read(ready)['arrays'] != input_hash:
                    raise ValueError('Regenerated observation differs: ' + str(folder))
                save(ready, dict(arrays=input_hash, generation=metadata))
                values, phase_record = estimated_phase(inputs, folder, controls,
                    reused=reused_case['phase'] if reused_case is not None else None)
                conditional = inputs.at_estimated_phase(values['phase_slopes'])
                conditional = ReceiverInput(conditional.observation, conditional.operator, 1., conditional.activity_prior)
                preserve_pairing(folder, inputs, conditional, truth, metadata)
                for method in pending:
                    target = folder / f'{method}.json'
                    base = dict(scene=scene, condition=index, method=method, input_array_sha256=input_hash,
                                phase_mode='estimated', noise_mode='estimated', truth_used_in_inference=False)
                    try:
                        reused = historical.result(reused_case, method, solvers[method])
                        if reused is not None:
                            save_arrays(target.with_suffix('.npz'), reused['compact'])
                            save(target, dict(base, status='COMPLETE', metrics=reused['metrics'],
                                receiver_seconds=reused['receiver_seconds'], phase_seconds=phase_record['seconds'],
                                compact_sha256=sha(target.with_suffix('.npz')), reused_from=reused['provenance'],
                                reused_execution_device=reused['execution_device'],
                                iterations=reused['iterations'], stopping_reason=reused['stopping_reason']))
                            print(f'{scene+1}/{spec["scenes"]} {spec["variable"]}={value} {method}: reused', flush=True)
                            continue
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
                             iterations=record['iterations'], stopping_reason=record['stopping_reason'],
                             output_array_sha256={k: array_sha256(v) for k, v in arrays.items()},
                             warnings=[str(w.message) for w in notices]))
                    except Exception:
                        save(target, dict(base, status='FAILED', traceback=traceback.format_exc()))
                        raise
                    print(f'{scene + 1}/{spec["scenes"]} {spec["variable"]}={value} {method}', flush=True)
    verify_sources(plan)
    return summarize(out, spec, plotter=plotter)


def main(defaults, argv=None):
    parser = argparse.ArgumentParser(description=defaults['description'])
    parser.add_argument('command', choices=('plan', 'run', 'summarize', 'saved'))
    parser.add_argument('--output', type=Path, help='Fresh results directory; required except for saved')
    parser.add_argument('--scenes', type=int, default=defaults['scenes'])
    parser.add_argument('--seed', type=int, default=defaults['seed'])
    parser.add_argument('--values', type=float, nargs='+', default=defaults['values'])
    parser.add_argument('--methods', nargs='+', choices=METHODS, default=METHODS)
    parser.add_argument('--device', choices=('cpu', 'mps', 'auto'), default=defaults.get('device', DEFAULTS['device']))
    parser.add_argument('--users', type=int, default=defaults.get('users', DEFAULTS['users']))
    parser.add_argument('--frames', type=int, default=defaults.get('frames', DEFAULTS['frames']))
    if defaults.get('training_sample_comparison'):
        parser.add_argument('--small-config', type=Path, help='Complete small-data receiver.json; only SNR and denoising support this comparison')
        parser.add_argument('--full-config', type=Path, help='Complete paired full-data receiver.json; default is the frozen mainline')
    if defaults.get('reuse_completed_snr'):
        parser.add_argument('--fresh', action='store_true', help='Disable reuse of the registered SNR results for this new plan')
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
                    methods=list(args.methods), device=args.device,
                    users=args.users, frames=args.frames,
                    scale=read(ROOT / CONFIGS['proposed'])['scale'])
        extra_hashes = {}
        if defaults.get('training_sample_comparison'):
            if (args.small_config or args.full_config) and 'proposed' not in spec['methods']:
                parser.error('Proposed configurations require proposed in --methods')
            bundles, extra_hashes = proposed_bundles(args.small_config, args.full_config)
            spec['proposed_bundles'] = bundles
            spec['scale'] = bundles['proposed']['configuration']['scale']
            spec['training_sample_comparison'] = 'CONFIGURED_BANK_SIZE_COMPARISON' if args.small_config else 'PENDING_SMALL_WEIGHTS'
            if args.small_config:
                spec['methods'].insert(spec['methods'].index('proposed')+1, 'proposed_small')
        if spec['variable'] in ('users', 'frames'):
            if any(int(v) != v for v in spec['values']):
                raise ValueError('Integer dimension values required')
            spec['values'] = [int(v) for v in spec['values']]
        validate(spec)
        bind_receivers(spec)
        if defaults.get('reuse_completed_snr') and not args.fresh:
            spec['reuse_plan'] = HISTORICAL_SNR
            spec['reuse_device_policy'] = 'Preserve original backend for reused results; requested device applies to new inference only'
        save(out / 'PLAN.json', dict(experiment=spec, source_and_weight_sha256=identities() | extra_hashes, created_unix=time.time(),
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
