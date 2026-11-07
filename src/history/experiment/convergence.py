"""Paired full-channel NMSE versus each method's native iteration/layer count."""
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
import argparse
import csv
import sys
import textwrap
import traceback
import warnings

from _common import (ROOT, METHODS, CONFIGS, LABELS, read, save, sha, save_arrays,
                     identities, verify_sources, observation, phase, phase_operator,
                     solver as build_solver,
                     DEFAULTS, PHASE_CONFIG, bind_receivers, pending_methods, estimated_phase, validate as validate_scan)
import numpy as np
from afdm_jadcedd.system.dictionary import AFDMGrid
from afdm_jadcedd.system.observation import array_sha256
from afdm_jadcedd.algorithm.unknown_phase_model import UnknownPhaseInput
from afdm_jadcedd.algorithm.baselines import gamp_sbl_mmv, offgrid_noise
from afdm_jadcedd.algorithm.baselines.offgrid.atoms import reconstruct
from afdm_jadcedd.algorithm.baselines.offgrid.sbl import posterior

# Representative convergence experiment; not a replacement for the 500-scene panel.
EXPERIMENT = dict(DEFAULTS, scenes=20, seed=202610180400001, snr_db=[-4, 0, 4],
                  methods=METHODS,
                  pilots=['dft', 'hadamard'])
ITERATION_UNITS = dict(proposed='native iteration', offgrid_sbl='SBL iteration',
                       gamp='GAMP iteration', gnn='AMP unfolding layer', somp='selected atom')


def hadamard_pilot(users, frames, seed, input_size=16):
    """Partial real Hadamard; Sylvester or Paley(q=19) plus doubling.

    Paley construction: arXiv:2411.18897 §4.1 Theorem 1; doubling §4.2
    Theorem 3. Row/column permutations and column signs preserve HH^T.
    Default order 640 = 20 * 2**5, without padding or changing user count.
    """
    dimension = users*input_size
    if dimension > 0 and dimension & (dimension-1) == 0:
        matrix = np.ones((1, 1), dtype=np.int64)
    elif dimension % 20 == 0 and (dimension//20) & (dimension//20-1) == 0:
        q = 19
        residues = {x*x % q for x in range(q)}
        core = np.array([[1 if (i-j) % q in residues else -1 for j in range(q)] for i in range(q)])
        matrix = np.ones((20, 20), dtype=np.int64)
        matrix[1:, 0] = -1
        matrix[1:, 1:] = core
    else:
        raise ValueError('This experiment supports Hadamard orders 2**m or 20*2**m; use DFT-only for other dimensions')
    if not 0 < frames <= dimension:
        raise ValueError('Pilot frames must lie between 1 and K*N')
    while len(matrix) < dimension:
        matrix = np.block([[matrix, matrix], [matrix, -matrix]])
    rng = np.random.default_rng(seed)
    rows = rng.permutation(dimension)[:frames]
    columns = rng.permutation(dimension)
    signs = np.where(rng.random(dimension) < .5, -1., 1.)
    pilot = matrix[rows[:, None], columns]*signs/np.sqrt(input_size)
    np.testing.assert_allclose(pilot@pilot.T, users*np.eye(frames), atol=1e-12, rtol=1e-12)
    return pilot.reshape(frames, users, input_size).astype(complex)


def pilot_observation(seed, parameters, scale, pilot_type):
    original, truth, metadata = observation(seed, parameters, scale)
    if pilot_type == 'dft':
        return original, truth, dict(metadata, pilot_type='dft')
    if pilot_type != 'hadamard':
        raise ValueError('Expected dft or hadamard')
    pilot = hadamard_pilot(parameters['users'], parameters['frames'], seed+10**12)
    old_clean = np.einsum('qkn,kmrn->qmr', phase_operator(original.pilot, truth['phase_slopes']), truth['channel'], optimize=False)
    epsilon = (original.observation-old_clean)/np.sqrt(metadata['generated_noise_variance'])
    clean = np.einsum('qkn,kmrn->qmr', phase_operator(pilot, truth['phase_slopes']), truth['channel'], optimize=False)
    power = float(np.mean(abs(clean)**2))
    variance = power*10**(-parameters['snr_db']/10)
    result = UnknownPhaseInput(clean+np.sqrt(variance)*epsilon, pilot, 1., original.activity_prior)
    return result, truth, dict(metadata, pilot_type='hadamard', generated_noise_variance=variance,
        generator_version='convergence_hadamard_v1', base_generator_version=metadata['generator_version'],
        pilot_sha256=array_sha256(pilot), standardized_noise_sha256=array_sha256(epsilon),
        physical_clean_power=power, noise_variance=variance,
        pilot_scope='Same K,N,Q and unit per-user per-frame energy; partial real Hadamard; fixed native receivers',
        comparison_noise_policy='Same received SNR and paired standard noise; physical noise variances may differ')



def pilot_conditions(spec):
    for index, snr in enumerate(spec['snr_db']):
        yield index, snr, 'dft', spec['methods']
        if 'hadamard' in spec.get('pilots', ['dft']):
            yield index, snr, 'hadamard', ['proposed']


def condition_folder(out, scene, index, pilot):
    folder = out / f'scene{scene:03d}' / f'snr{index:02d}'
    return folder if pilot == 'dft' else folder / 'hadamard'


@contextmanager
def observe_trace(functions, callback):
    """Read completed native trace entries without replacing solver functions.

    Python tracing is limited to the exact selected code objects. The callback
    reads locals and calculates a channel for scoring; it never assigns locals,
    writes solver arrays, or returns a value to the inference routine.
    """
    if sys.gettrace() is not None:
        raise RuntimeError('Run this experiment outside another Python tracer/debugger')
    codes = {function.__code__ for function in functions}

    def dispatch(frame, event, arg):
        if event != 'call' or frame.f_code not in codes:
            return None
        seen = 0

        def local(current, event, arg):
            nonlocal seen
            trace = current.f_locals.get('trace', [])
            if event in ('line', 'return') and len(trace) > seen:
                if len(trace) != seen + 1:
                    raise RuntimeError('More than one native iteration was missed')
                seen = len(trace)
                callback(current.f_locals, seen)
            return local
        return local

    sys.settrace(dispatch)
    try:
        yield
    finally:
        sys.settrace(None)


def infer_curve(method, solver, inputs, truth):
    """Score read-only observations; retain the native stopping decision."""
    channel = truth['channel']
    signal = float(np.sum(abs(channel)**2))
    if signal <= 0:
        raise ValueError('Nonempty physical scene required')
    points = [dict(iteration=0, full_error=signal, signal_energy=signal)]
    last = np.zeros_like(channel)

    def capture(iteration, estimate):
        nonlocal last
        estimate = np.asarray(estimate)
        if estimate.shape != channel.shape or not np.isfinite(estimate).all():
            raise ValueError('Invalid intermediate physical channel')
        if iteration != len(points):
            raise ValueError('Native iteration numbers must be contiguous')
        last = estimate.copy()
        points.append(dict(iteration=int(iteration), full_error=float(np.sum(abs(last-channel)**2)),
                           signal_energy=signal))

    if method == 'proposed':
        scale = solver.base.configuration['scale']
        arrays, record = solver.infer(inputs, observer=lambda row, state, *unused:
                                     capture(row['iteration'], state.mean*scale))
    elif method == 'somp':
        arrays, record = solver.infer(inputs, observer=lambda row, get_channel:
                                     capture(row['iteration'], get_channel()))
    else:
        if method in ('gamp', 'gnn'):
            dictionary = solver.base.configuration['dictionary'] if method == 'gamp' else solver.base.native.dictionary
            grid = AFDMGrid.from_operator(inputs.operator, **dictionary)
        if method == 'gamp':
            functions = [gamp_sbl_mmv.solve_mmv]

            def snapshot(state, iteration):
                capture(iteration, grid.reconstruct(state['mean']*grid.norms[:, None]))
        elif method == 'gnn':
            model = solver.base.native.model
            functions = [model.forward]
            if hasattr(model, '_forward_real'):
                functions.append(model._forward_real)

            def snapshot(state, iteration):
                if 'z' in state:
                    coefficients = state['z'].detach().cpu().numpy()[0]
                else:
                    coefficients = (state['zr'].detach().cpu().numpy()[0]
                                    + 1j*state['zi'].detach().cpu().numpy()[0])
                capture(iteration, grid.reconstruct(coefficients*grid.norms[:, None]))
        elif method == 'offgrid_sbl':
            functions = [offgrid_noise.solve]

            def snapshot(state, iteration):
                # Apply the native final readout to this iteration's completed
                # hyperparameters. These new arrays never feed back to SBL.
                offsets = state['offsets']
                design = state['a0'] + state['derivatives'][0]*offsets[:, 0] + state['derivatives'][1]*offsets[:, 1]
                mean, _, _ = posterior(design, state['y'], state['variance'], state['noise'])
                estimate = reconstruct(inputs.operator.shape[1], inputs.observation.shape[1],
                    state['users'], state['centers']+offsets, mean/state['scales'][:, None])
                capture(iteration, estimate)
        else:
            raise ValueError(method)
        with observe_trace(functions, snapshot):
            arrays, record = solver.infer(inputs)
    if len(points)-1 != record['iterations']:
        raise ValueError('Observed iteration count differs from the native record')
    np.testing.assert_allclose(last, arrays['estimate'], rtol=1e-10, atol=1e-12,
                               err_msg='Last observed channel differs from native output')
    return arrays, record, points


def pooled_curve(records):
    """Hold each stopped scene's final estimate; never average only survivors."""
    last = max(record['iterations'] for record in records)
    rows = []
    for iteration in range(last+1):
        selected = [record['points'][min(iteration, record['iterations'])] for record in records]
        error = sum(point['full_error'] for point in selected)
        signal = sum(point['signal_energy'] for point in selected)
        rows.append(dict(iteration=iteration, full_error=error, signal_energy=signal,
             nmse_db=float(10*np.log10(error/signal)) if error else None,
             exact_zero_error=error == 0, scenes=len(records),
             stopped_scenes=sum(record['iterations'] < iteration for record in records)))
    return rows


def summarize(out, spec):
    groups, missing, failed = [], [], []
    for snr_index, snr, pilot, methods in pilot_conditions(spec):
        for method in methods:
            records = []
            for scene in range(spec['scenes']):
                path = condition_folder(out, scene, snr_index, pilot) / f'{method}.json'
                if not path.exists():
                    missing.append(str(path.relative_to(out))); continue
                record = read(path)
                if (record['scene'], record['snr_db'], record['method'], record.get('pilot_type', 'dft')) != (scene, snr, method, pilot):
                    raise ValueError('Record identity mismatch: ' + str(path))
                if record['status'] != 'COMPLETE':
                    failed.append(str(path.relative_to(out))); continue
                if sha(path.with_suffix('.npz')) != record['output_sha256']:
                    raise ValueError('Saved final output changed: ' + str(path))
                records.append(record)
            if len(records) == spec['scenes']:
                stops = [record['iterations'] for record in records]
                groups.append(dict(method=method, snr_db=snr, pilot_type=pilot, iteration_unit=ITERATION_UNITS[method],
                    native_stop_min=min(stops), native_stop_median=float(np.median(stops)), native_stop_max=max(stops),
                    stopping_reasons=dict(Counter(record['stopping_reason'] for record in records)),
                    curve=pooled_curve(records)))
    complete = not missing and not failed
    save(out / 'SUMMARY.json', dict(status='COMPLETE' if complete else 'INCOMPLETE', groups=groups,
        missing=missing, failed=failed, native_iterations_preserved=True,
        stopped_scene_policy='Hold final estimate after native stopping for fixed-cohort energy pooling.',
        interpretation='Native iteration/layer counts are not equal computation budgets; point estimates only.',
        timing='Observer reconstruction/scoring adds overhead; recorded runtimes are not speed benchmarks.'))
    if complete:
        with (out / 'CONVERGENCE.csv').open('w', newline='') as f:
            rows = [dict(method=g['method'], snr_db=g['snr_db'], pilot_type=g['pilot_type'], **point) for g in groups for point in g['curve']]
            writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
        plot(out, spec, groups)
        if 'hadamard' in spec.get('pilots', ['dft']):
            plot_pilots(out, spec, groups)
    print(f'{"COMPLETE" if complete else "INCOMPLETE"}: {out}')
    return 0 if complete else 1


def plot(out, spec, groups):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    for limit, name in [(None, 'convergence'), (100, 'convergence_first100')]:
        fig, axes = plt.subplots(1, len(spec['snr_db']), figsize=(5*len(spec['snr_db']), 4.5),
                                 squeeze=False, layout='constrained')
        for ax, snr in zip(axes[0], spec['snr_db']):
            for group in [g for g in groups if g['snr_db'] == snr and g['pilot_type'] == 'dft']:
                curve = [p for p in group['curve'] if limit is None or p['iteration'] <= limit]
                ax.plot([p['iteration'] for p in curve], [p['nmse_db'] for p in curve],
                        marker='o' if len(curve) == 1 else None, label=LABELS[group['method']])
                zeros = [str(p['iteration']) for p in curve if p['exact_zero_error']]
                if zeros:
                    ax.text(.03, .04+.05*spec['methods'].index(group['method']),
                            LABELS[group['method']]+': zero error (−∞ dB)', transform=ax.transAxes, fontsize=7)
            ax.set(title=f'SNR = {snr:g} dB', xlabel='Native iteration / unfolding layer', ylabel='Full-channel NMSE (dB)')
            ax.grid(alpha=.25); ax.legend(fontsize=8)
        noun = 'scene' if spec['scenes'] == 1 else 'scenes'
        width = 48 if len(spec['snr_db']) == 1 else 100
        title = f'{spec["scenes"]} paired {noun} per SNR; estimated phase and noise'
        note = 'Stopped scenes retain final estimates; iteration counts are not equal computation budgets'
        fig.suptitle(textwrap.fill(title, width) + '\n' + textwrap.fill(note, width), fontsize=9)
        for suffix in ('png', 'pdf'):
            fig.savefig(out / f'{name}.{suffix}', dpi=180, bbox_inches='tight')
        plt.close(fig)


def plot_pilots(out, spec, groups):
    """Same Proposed weights under two pilots; separate from method ranking."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, len(spec['snr_db']), figsize=(5*len(spec['snr_db']), 4.5),
                             squeeze=False, layout='constrained')
    for ax, snr in zip(axes[0], spec['snr_db']):
        for pilot, label in [('dft', 'Proposed / partial DFT'), ('hadamard', 'Proposed / partial Hadamard')]:
            group = next(g for g in groups if g['snr_db'] == snr and g['method'] == 'proposed' and g['pilot_type'] == pilot)
            curve = group['curve']
            ax.plot([p['iteration'] for p in curve], [p['nmse_db'] for p in curve], label=label)
            if any(p['exact_zero_error'] for p in curve):
                ax.text(.03, .04+.05*(pilot == 'hadamard'), label+': zero error (−∞ dB)', transform=ax.transAxes, fontsize=7)
        ax.set(title=f'SNR = {snr:g} dB', xlabel='Native iteration', ylabel='Full-channel NMSE (dB)')
        ax.grid(alpha=.25); ax.legend(fontsize=8)
    width = 48 if len(spec['snr_db']) == 1 else 100
    title = f'{spec["scenes"]} paired scenes; same weights, pilot dimensions and transmit energy'
    note = 'Estimated phase and noise; matched received SNR; native stopping retained'
    fig.suptitle(textwrap.fill(title, width)+'\n'+textwrap.fill(note, width), fontsize=9)
    for suffix in ('png', 'pdf'):
        fig.savefig(out / f'convergence_pilots.{suffix}', dpi=180, bbox_inches='tight')
    plt.close(fig)


def run(out, plan):
    import torch
    from threadpoolctl import threadpool_limits
    verify_sources(plan)
    spec = plan['experiment']
    torch.set_num_threads(1)
    with threadpool_limits(1):
        solvers = {m: build_solver(m, spec) for m in spec['methods']}
        controls = phase.Controls(**read(ROOT / spec.get('phase_config', PHASE_CONFIG))['phase_estimation'])
        for scene in range(spec['scenes']):
            for index, snr, pilot, methods in pilot_conditions(spec):
                folder = condition_folder(out, scene, index, pilot)
                pending = pending_methods(folder, methods, 'output_sha256')
                if not pending:
                    continue
                parameters = dict(snr_db=snr, users=spec['users'], frames=spec['frames'], activity_probability=spec['activity_probability'])
                inputs, truth, metadata = pilot_observation(spec['seed']+scene, parameters, spec['scale'], pilot)
                values, phase_record = estimated_phase(inputs, folder, controls)
                save(folder / 'GENERATION.json', metadata)
                save_arrays(folder / 'truth.npz', truth)
                conditional = inputs.at_estimated_phase(values['phase_slopes'])
                input_hash = {k: array_sha256(v) for k, v in inputs.arguments().items()}
                for method in pending:
                    target = folder / f'{method}.json'
                    base = dict(scene=scene, snr_db=snr, method=method, pilot_type=pilot, input_sha256=input_hash,
                                iteration_unit=ITERATION_UNITS[method], truth_used_only_for_scoring=True)
                    try:
                        with warnings.catch_warnings(record=True) as notices:
                            warnings.simplefilter('always', RuntimeWarning)
                            solver = solvers[method]
                            native = native_record = None
                            # First scene at every SNR checks the actual experiment dimensions.
                            if scene == 0:
                                native, native_record = solver.infer(conditional)
                            arrays, record, points = infer_curve(method, solver, conditional, truth)
                        if not all(np.isfinite(v).all() for v in arrays.values()) or record.get('status', 'COMPLETE') != 'COMPLETE':
                            raise FloatingPointError('Nonfinite or incomplete native receiver output')
                        equivalence = None
                        if native is not None:
                            if native.keys() != arrays.keys():
                                raise AssertionError('Observer changed output fields')
                            for key in native:
                                np.testing.assert_array_equal(arrays[key], native[key], err_msg=method+' '+key)
                            if any(record[k] != native_record[k] for k in ('iterations', 'stopping_reason')):
                                raise AssertionError('Observer changed native stopping')
                            equivalence = 'ALL_OUTPUT_ARRAYS_EXACT_AND_STOPPING_IDENTICAL'
                        save_arrays(target.with_suffix('.npz'), arrays)
                        save(folder / f'{method}.native.json', record)
                        save(target, dict(base, status='COMPLETE', iterations=record['iterations'],
                             stopping_reason=record['stopping_reason'], points=points,
                             output_sha256=sha(target.with_suffix('.npz')), observer_equivalence=equivalence,
                             last_point_matches_native_output=True, warnings=[str(w.message) for w in notices]))
                    except Exception:
                        save(target, dict(base, status='FAILED', traceback=traceback.format_exc())); raise
                    print(f'{scene+1}/{spec["scenes"]} SNR={snr:g} {pilot} {method}: {record["iterations"]} native updates', flush=True)
    verify_sources(plan)
    return summarize(out, spec)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('plan', 'run', 'summarize'))
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--scenes', type=int, default=EXPERIMENT['scenes'])
    parser.add_argument('--snr', type=float, nargs='+', default=EXPERIMENT['snr_db'])
    parser.add_argument('--seed', type=int, default=EXPERIMENT['seed'])
    parser.add_argument('--users', type=int, default=EXPERIMENT['users'])
    parser.add_argument('--frames', type=int, default=EXPERIMENT['frames'])
    parser.add_argument('--methods', nargs='+', choices=METHODS, default=METHODS)
    parser.add_argument('--pilots', nargs='+', choices=('dft', 'hadamard'),
                        help='Default: DFT for all methods plus Hadamard for Proposed; dft alone disables the added panel')
    args = parser.parse_args(argv)
    out = args.output.resolve()
    if args.command == 'plan':
        if out.exists() and any(out.iterdir()):
            raise FileExistsError('Plan requires a fresh empty output directory')
        if args.scenes < 1 or args.users < 2 or not 1 <= args.frames <= min(48, args.users*16) or not np.isfinite(args.snr).all() or len(set(args.snr)) != len(args.snr):
            parser.error('Positive scenes, users >= 2, 1–min(48, users*16) frames and distinct finite SNR values required')
        pilots = args.pilots or (EXPERIMENT['pilots'] if 'proposed' in args.methods else ['dft'])
        if 'dft' not in pilots or len(set(pilots)) != len(pilots) or ('hadamard' in pilots and 'proposed' not in args.methods):
            parser.error('Distinct pilots including dft required; Hadamard comparison requires proposed')
        if 'hadamard' in pilots:
            hadamard_pilot(args.users, args.frames, args.seed+10**12)
        spec = dict(EXPERIMENT, scenes=args.scenes, seed=args.seed, users=args.users, frames=args.frames,
                    snr_db=args.snr, methods=list(args.methods), pilots=pilots, scale=read(ROOT / CONFIGS['proposed'])['scale'])
        validate_scan(dict(spec, variable='snr_db', values=spec['snr_db'], snr_db=0.))
        bind_receivers(spec)
        save(out / 'PLAN.json', dict(experiment=spec, source_and_weight_sha256=identities(),
             pilot_comparison='Original DFT: all selected methods; same-weight Proposed: DFT vs real Hadamard. No retraining.',
             pairing='Same physical truth, K/N/Q, unit per-user frame energy, received SNR and paired standard noise.',
             expected_runs=spec['scenes']*len(spec['snr_db'])*(len(spec['methods'])+int('hadamard' in pilots)),
             expected_native_checks=len(spec['snr_db'])*(len(spec['methods'])+int('hadamard' in pilots)),
             stopping='Preserve native configuration, iterations and stopping; no truth-based decisions.',
             offgrid_readout='Apply the native final posterior/reconstruction to each completed hyperparameter update.',
             observation='Read-only Python trace for GAMP, SBL and GNN; existing observers for Proposed and SOMP.',
             phase_mode='estimated', noise_mode='estimated', observer_equivalence='Exact arrays and stopping on first scene at every SNR.'))
        print(f'PLANNED: {out}'); return 0
    plan = read(out / 'PLAN.json')
    if 'offgrid_readout' not in plan:
        raise ValueError('Expected a convergence experiment plan')
    return run(out, plan) if args.command == 'run' else summarize(out, plan['experiment'])


if __name__ == '__main__':
    raise SystemExit('Convergence experiments were retired by user request. Use experiment/runtime_comparison.py; historical curves are preserved.')
