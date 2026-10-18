"""Independent active-channel AWGN denoising and conditional-MSE validation."""
from pathlib import Path
from dataclasses import replace
import argparse
import csv
import traceback
import warnings
import numpy as np

from _common import (ROOT, read, save, sha, save_arrays, identities, verify_sources,
                     proposed_bundles, method_label, DEFAULTS, pending_methods, validate_seed)
from afdm_jadcedd.system.scenario.geometry_consistent import draw_scene
from afdm_jadcedd.system.scenario.continuous import user_channel
from afdm_jadcedd.system.observation import array_sha256
from afdm_jadcedd.experiment.training.proposed.data import candidate_indices
from afdm_jadcedd.algorithm.proposed.moments import FullChannelMoments
from afdm_jadcedd.system import config as physical_config

EXPERIMENT = dict(description=__doc__, variable='denoising_variance', scenes=DEFAULTS['scenes'],
                  seed=202610180500001, users=DEFAULTS['users'], candidates=4,
                  values=[.001, .01, .1, 1., 10., 100.], device='cpu')


def first_score_bundles(full_config, small_config=None):
    """Bind completed first scores without loading second/activity networks."""
    import torch
    if full_config is None:
        raise ValueError('--first-only requires --full-config')
    bundles, hashes, architectures = {}, {}, {}
    paths = [('proposed', Path(full_config).resolve())]
    if small_config:
        paths.append(('proposed_small', Path(small_config).resolve()))
    for name, path in paths:
        config = read(path)
        if config.get('schema') != 'proposed-first-score-evaluation-v1':
            raise ValueError('Dedicated completed first-score configuration required')
        checkpoint, prior_path, record_path = [ROOT/config[k] for k in
                  ('first_checkpoint', 'prior_definition', 'completion_record')]
        for key, asset in [('first_checkpoint', checkpoint), ('prior_definition', prior_path),
                           ('completion_record', record_path)]:
            if sha(asset) != config[key+'_sha256']:
                raise ValueError('First-score evaluation asset changed: '+key)
        prior, record = read(prior_path), read(record_path)
        blob = torch.load(checkpoint, map_location='cpu', weights_only=False)
        specification = record_path.parent/'specification.json'
        if (record['status'] != 'COMPLETED' or record['optimizer_steps'] < 1 or
                record['weight_sha256'] != sha(checkpoint) or
                record['specification_sha256'] != sha(specification) or
                blob.get('order') != 1 or blob.get('normalization') != 'population_rms' or
                blob['metadata']['specification_sha256'] != sha(specification) or
                blob['metadata']['prior_definition_sha256'] != sha(prior_path) or
                config['scale'] != blob['global_complex_rms'] or prior['global_complex_rms'] != config['scale']):
            raise ValueError('Completed first score, prior and training identity must agree')
        count = prior['train_samples']
        config = dict(config, batch_size=8,
                      initialization=dict(normalized_training_second_moment=prior['normalized_mean_element_power']))
        bundles[name] = dict(configuration=config, train_samples=count,
                             label=f'Proposed (N_train={count:,})',
                             sample_scope='Distinct clean training channels; first-score evaluation only')
        architectures[name] = blob['config']
        hashes.update({str(p):sha(p) for p in (path, checkpoint, prior_path, record_path, specification)})
    if small_config:
        full, small = bundles['proposed'], bundles['proposed_small']
        if (small['train_samples'] >= full['train_samples'] or
                architectures['proposed'] != architectures['proposed_small'] or
                full['configuration']['scale'] != small['configuration']['scale']):
            raise ValueError('Nested sample sizes, identical architectures and common coordinates required')
        if full['configuration']['first_checkpoint_sha256'] == small['configuration']['first_checkpoint_sha256']:
            raise ValueError('Distinct trained first-score checkpoints required')
    return bundles, hashes


class FirstChannelMean:
    """Use the same first-score Tweedie mean as the complete receiver."""
    def __init__(self, scale, path, *, device, batch_size=8):
        from afdm_jadcedd.algorithm.proposed.network import load_direct_checkpoint
        self.first, blob = load_direct_checkpoint(path, device)
        if blob['order'] != 1 or blob.get('normalization') != 'population_rms':
            raise ValueError('Population-coordinate first score required')
        self.scale_ratio = scale/blob['global_complex_rms']
        self.noise_support = (.001/self.scale_ratio**2, 100./self.scale_ratio**2)
        self.device, self.batch_size = device, batch_size

    def infer(self, observation, variance):
        import torch
        from afdm_jadcedd.algorithm.proposed.moments import convert_moments, MatrixMomentEstimate
        query = np.asarray(observation, complex)
        variances = np.broadcast_to(np.asarray(variance, float), (len(query),))
        means = []
        with torch.inference_mode():
            for start in range(0, len(query), self.batch_size):
                block = query[start:start+self.batch_size]
                vb = variances[start:start+self.batch_size]
                packed = self.scale_ratio*np.stack((block.real, block.imag), axis=1)
                x = torch.tensor(packed, dtype=torch.float32, device=self.device)
                v = torch.tensor(vb*self.scale_ratio**2, dtype=torch.float32, device=self.device)
                score = self.first(x, v).cpu().numpy().astype(float)
                # The shared conversion's mean does not depend on the second score.
                mean = convert_moments(block, vb, score, np.zeros_like(score), self.scale_ratio).mean
                means.append(mean)
        return MatrixMomentEstimate(np.concatenate(means), None)


def clean_channels(seed, users, candidates, *, genie_scale=None):
    """Uniform candidate selection before activity masking, as in training."""
    scene, _ = draw_scene(seed, n_users=users)
    selected = candidate_indices(seed, users, candidates)
    channels = np.stack([user_channel(scene.paths_of(int(u))) for u in selected])
    if genie_scale is None:
        return channels, selected
    return channels, selected, [genie_prior(scene.paths_of(int(u)), genie_scale) for u in selected]


def genie_prior(paths, scale):
    """True path geometry/powers and LOS gain; diffuse gains remain unknown.

    Given this side information h = m + B g, g ~ CN(0,I). The frozen LOS
    gain has random phase and fixed amplitude, so geometry-only LMMSE is
    not an MMSE lower bound for this channel distribution.
    """
    los, columns = [], []
    for path in paths:
        kind = physical_config.NTN_TDL_D_FADING[path.path_id]
        if kind == 'los':
            los.append(path)
        elif kind == 'rayleigh':
            power = 10.**(physical_config.NTN_TDL_D_POWER_DB[path.path_id]/10)
            atom = user_channel([replace(path, gain=1., legacy_gain=1.)])/scale
            columns.append(np.sqrt(power)*atom.reshape(-1))
        else:
            raise ValueError('Genie bound requires conditionally Gaussian diffuse gains')
    mean = user_channel(los)/scale
    basis, singular, _ = np.linalg.svd(np.stack(columns, axis=1), full_matrices=False)
    return dict(mean=mean, basis=basis, eigenvalues=singular**2)


def genie_mmse(query, variance, priors):
    """Conditional posterior mean and analytic Bayes MSE, in training units."""
    means, risks = [], []
    for received, prior in zip(query, priors, strict=True):
        basis, eigenvalues, known = prior['basis'], prior['eigenvalues'], prior['mean']
        residual = (received-known).reshape(-1)
        update = basis@((eigenvalues/(eigenvalues+variance))*(basis.conj().T@residual))
        means.append(known+update.reshape(known.shape))
        risks.append(float(np.sum(variance*eigenvalues/(eigenvalues+variance))))
    return np.stack(means), np.asarray(risks)


def validate_test_seeds(spec, bundles):
    # Reject overlap with any declared source-training or validation scene set.
    start, end = spec['seed'], spec['seed']+spec['scenes']
    for bundle in bundles.values():
        prior = read(ROOT / bundle['configuration']['prior_definition'])
        for split, record in prior.get('dataset_identities', {}).items():
            if 'scene_seeds' in record:
                if any(start <= seed < end for seed in record['scene_seeds']):
                    raise ValueError('Test scenes overlap '+split+' scene seeds')
                continue
            base, count = record.get('seed_base'), record.get('scenes')
            if base is not None and count is not None and max(start, base) < min(end, base+count):
                raise ValueError('Test scenes overlap '+split+' scene seeds')


def denoising_metrics(mean, truth, predicted_variance=None):
    axes = tuple(range(1, truth.ndim))
    error = np.sum(abs(mean-truth)**2, axis=axes)
    energy = np.sum(abs(truth)**2, axis=axes)
    arrays = dict(error=error, energy=energy)
    if predicted_variance is not None:
        arrays['predicted_error'] = np.asarray(predicted_variance)*int(np.prod(truth.shape[1:]))
    if not all(np.isfinite(a).all() for a in arrays.values()):
        raise FloatingPointError('Nonfinite denoising output or error prediction')
    return arrays


def aggregate(spec, records):
    rows = []
    for index, variance in enumerate(spec['values']):
        for method in spec['methods']:
            group = [r for r in records if r['condition'] == index and r['method'] == method]
            complete = [r for r in group if r['status'] == 'COMPLETE']
            row = dict(method=method, variance=variance, planned=spec['scenes'], completed=len(complete),
                       failed=sum(r['status'] == 'FAILED' for r in group), missing=spec['scenes']-len(group),
                       status='COMPLETE' if len(complete) == spec['scenes'] else 'INCOMPLETE')
            if row['status'] == 'COMPLETE':
                error = sum(r['error'] for r in complete)
                energy = sum(r['energy'] for r in complete)
                count = sum(r['samples'] for r in complete)
                row.update(error=error, energy=energy, samples=count,
                           error_kind=complete[0].get('error_kind', 'realized_squared_error'),
                           nmse_db=float(10*np.log10(error/energy)) if error else None,
                           exact_zero_error=error == 0)
                if method == 'genie_bound':
                    row.update(realized_error=sum(r['realized_error'] for r in complete),
                               truth_used_in_denoiser=True,
                               side_information='True geometry, path powers and LOS complex gain')
                if 'predicted_error' in complete[0]:
                    prediction = sum(r['predicted_error'] for r in complete)
                    row.update(predicted_error=prediction,
                               predicted_to_observed_mse=prediction/error if error else None,
                               negative_variance_samples=sum(r['negative_variance_samples'] for r in complete))
            rows.append(row)
    return rows


def plot(out, spec, rows):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    first_only = spec.get('first_only', False)
    fig, axes = plt.subplots(1, 1 if first_only else 2,
                             figsize=(6.5, 4) if first_only else (11, 4), layout='constrained', squeeze=False)
    axes = axes[0]
    for method in spec['methods']:
        group = sorted([r for r in rows if r['method'] == method], key=lambda r:r['variance'])
        label = {'noisy':'Noisy channel', 'gaussian':'Gaussian prior (training power)',
                 'genie_bound':'Genie MMSE bound (geometry + LOS known)'}.get(method, method_label(spec, method))
        x = [r['variance'] for r in group]
        axes[0].plot(x, [r['nmse_db'] for r in group], 's--' if method == 'genie_bound' else 'o-', label=label)
        if not first_only and 'predicted_error' in group[0]:
            axes[1].plot(x, [r['predicted_to_observed_mse'] for r in group], 'o-', label=label)
    if not first_only:
        axes[1].axhline(1., color='black', linestyle=':', label='Matching average MSE')
        axes[1].set_ylabel('Raw predicted / observed MSE')
    axes[0].set_ylabel('Active-channel NMSE (dB)')
    for ax in axes:
        ax.set_xscale('log'); ax.set_xlabel('Complex AWGN variance in fixed training coordinates')
        ax.grid(alpha=.25); ax.legend(fontsize=8)
    fig.suptitle(f'{spec["scenes"]} independent scenes × {spec["candidates"]} candidate channels; known query noise')
    for suffix in ('png', 'pdf'):
        fig.savefig(out / f'denoising.{suffix}', dpi=180)
    plt.close(fig)


def summarize(out, spec):
    records = []
    for scene in range(spec['scenes']):
        for index in range(len(spec['values'])):
            for method in spec['methods']:
                path = out / f'scene{scene:03d}/condition{index:02d}/{method}.json'
                if not path.exists():
                    continue
                row = read(path)
                if (row['scene'], row['condition'], row['method']) != (scene, index, method):
                    raise ValueError('Denoising result identity differs')
                if row['status'] == 'COMPLETE' and sha(path.with_suffix('.npz')) != row['compact_sha256']:
                    raise ValueError('Denoising result changed: '+str(path))
                records.append(row)
    rows = aggregate(spec, records)
    status = 'COMPLETE' if all(r['status'] == 'COMPLETE' for r in rows) else 'INCOMPLETE'
    save(out / 'SUMMARY.json', dict(status=status, rows=rows,
         first_only=spec.get('first_only', False),
         uncertainty_calibration='PENDING_SECOND_SCORE' if spec.get('first_only') else 'INCLUDED',
         training_sample_comparison=spec['training_sample_comparison'],
         statistics='Pooled channel energies; multiple candidates share a physical scene; point estimates only.',
         scope='Active-channel AWGN queries, no activity classifier or receiver iteration; raw variance is not clipped.',
         bound='Genie conditional Gaussian MMSE: true geometry, path powers and LOS gain known. Analytic conditional MSE pooled over sampled geometry, divided by the same empirical channel energy. A population MSE bound, not a per-realization inequality.'))
    with (out / 'STATISTICS.csv').open('w', newline='') as f:
        fields = list(dict.fromkeys(k for r in rows for k in r))
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    if status == 'COMPLETE':
        plot(out, spec, rows)
    print(f'{status}: {out}')
    return 0 if status == 'COMPLETE' else 1


def run(out, plan):
    import torch
    from threadpoolctl import threadpool_limits
    verify_sources(plan)
    spec = plan['experiment']
    torch.set_num_threads(1)
    device = ('mps' if torch.backends.mps.is_available() else 'cpu') if spec['device'] == 'auto' else spec['device']
    models = {}
    for method, bundle in spec['proposed_bundles'].items():
        c = bundle['configuration']
        if spec.get('first_only'):
            models[method] = FirstChannelMean(spec['scale'], ROOT/c['first_checkpoint'],
                                             device=device, batch_size=c['batch_size'])
        else:
            models[method] = FullChannelMoments(spec['scale'], ROOT/c['first_checkpoint'], ROOT/c['second_checkpoint'],
                                               device=device, batch_size=c['batch_size'])
        lo, hi = models[method].noise_support
        if min(spec['values']) < lo or max(spec['values']) > hi:
            raise ValueError('Denoising variances must lie inside the trained query-noise support')
    power = spec['proposed_bundles']['proposed']['configuration']['initialization']['normalized_training_second_moment']
    with threadpool_limits(1):
        for scene in range(spec['scenes']):
            seed = spec['seed']+scene
            pending = {i: pending_methods(out / f'scene{scene:03d}/condition{i:02d}', spec['methods'])
                       for i in range(len(spec['values']))}
            if not any(pending.values()):
                continue
            physical, users, priors = clean_channels(seed, spec['users'], spec['candidates'], genie_scale=spec['scale'])
            truth = physical/spec['scale']
            rng = np.random.default_rng(np.random.SeedSequence([seed, 8240]))
            epsilon = (rng.normal(size=truth.shape)+1j*rng.normal(size=truth.shape))/np.sqrt(2)
            for index, variance in enumerate(spec['values']):
                if not pending[index]:
                    continue
                query = truth+np.sqrt(variance)*epsilon
                folder = out / f'scene{scene:03d}/condition{index:02d}'
                identity = dict(seed=seed, users=users.tolist(), variance=variance, scale=spec['scale'],
                                truth_sha256=array_sha256(truth), query_sha256=array_sha256(query),
                                standard_noise_sha256=array_sha256(epsilon))
                input_path = folder / 'INPUT.json'
                if input_path.exists() and read(input_path) != identity:
                    raise ValueError('Regenerated denoising input differs')
                save(input_path, identity)
                if scene == 0:
                    save_arrays(folder / 'query.npz', dict(truth=truth, query=query, users=users))
                for method in pending[index]:
                    target = folder / f'{method}.json'
                    base = dict(scene=scene, condition=index, method=method, samples=len(truth),
                                truth_used_in_denoiser=method == 'genie_bound', supplied_query_variance=variance,
                                error_kind='analytic_conditional_mmse' if method == 'genie_bound' else 'realized_squared_error')
                    try:
                        with warnings.catch_warnings(record=True) as notices:
                            warnings.simplefilter('always', RuntimeWarning)
                            predicted = None
                            if method == 'noisy':
                                mean = query
                            elif method == 'gaussian':
                                mean = power/(power+variance)*query
                            elif method == 'genie_bound':
                                mean, risk = genie_mmse(query, variance, priors)
                            else:
                                moments = models[method].infer(query, variance)
                                mean, predicted = moments.mean, moments.variance
                            arrays = denoising_metrics(mean, truth, predicted)
                            if method == 'genie_bound':
                                if not np.isfinite(risk).all() or (risk < 0).any():
                                    raise FloatingPointError('Invalid analytic genie MMSE')
                                arrays['realized_error'] = arrays['error']
                                arrays['error'] = risk
                        save_arrays(target.with_suffix('.npz'), arrays)
                        metrics = dict(error=float(arrays['error'].sum()), energy=float(arrays['energy'].sum()))
                        if method == 'genie_bound':
                            metrics.update(realized_error=float(arrays['realized_error'].sum()),
                                           side_information='True geometry, path powers and LOS complex gain')
                        if predicted is not None:
                            metrics.update(predicted_error=float(arrays['predicted_error'].sum()),
                                           negative_variance_samples=int(np.count_nonzero(predicted < 0)))
                        if scene == 0:
                            save_arrays(folder / f'{method}.prediction.npz', dict(mean=mean))
                        save(target, dict(base, **metrics, status='COMPLETE', compact_sha256=sha(target.with_suffix('.npz')),
                                          warnings=[str(w.message) for w in notices]))
                    except Exception:
                        save(target, dict(base, status='FAILED', traceback=traceback.format_exc())); raise
                    print(f'{scene+1}/{spec["scenes"]} variance={variance:g} {method}', flush=True)
    verify_sources(plan)
    return summarize(out, spec)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('plan', 'run', 'summarize'))
    parser.add_argument('--output', type=Path, required=True)
    for key in ('scenes', 'seed', 'users', 'candidates'):
        parser.add_argument('--'+key, type=int, default=EXPERIMENT[key])
    parser.add_argument('--values', type=float, nargs='+', default=EXPERIMENT['values'], help='Normalized complex noise variances')
    parser.add_argument('--small-config', type=Path, help='Complete small-data receiver.json')
    parser.add_argument('--full-config', type=Path, help='Paired full-data configuration; default is the frozen mainline')
    parser.add_argument('--first-only', action='store_true', help='Evaluate completed first scores before training auxiliary networks')
    parser.add_argument('--device', choices=('cpu', 'mps', 'auto'), default=EXPERIMENT['device'])
    args = parser.parse_args(argv)
    out = args.output.resolve()
    if args.command == 'plan':
        if out.exists() and any(out.iterdir()):
            raise FileExistsError('Plan requires a fresh output directory')
        spec = dict(EXPERIMENT, **{k:getattr(args, k) for k in
                                 ('scenes', 'seed', 'users', 'candidates', 'values', 'device')})
        if (spec['scenes'] < 1 or not 1 <= spec['candidates'] <= spec['users'] or
                len(set(spec['values'])) != len(spec['values']) or
                not np.isfinite(spec['values']).all() or min(spec['values']) < .001 or max(spec['values']) > 100):
            parser.error('Positive scenes/candidates and distinct noise variances in [0.001,100] required')
        validate_seed(spec['seed'])
        bundles, extra_hashes = (first_score_bundles(args.full_config, args.small_config) if args.first_only
                                else proposed_bundles(args.small_config, args.full_config))
        validate_test_seeds(spec, bundles)
        spec.update(proposed_bundles=bundles, scale=bundles['proposed']['configuration']['scale'],
                    first_only=args.first_only,
                    methods=['noisy', 'gaussian', *bundles, 'genie_bound'],
                    training_sample_comparison='CONFIGURED_BANK_SIZE_COMPARISON' if args.small_config else 'PENDING_SMALL_WEIGHTS')
        save(out / 'PLAN.json', dict(experiment=spec, source_and_weight_sha256=identities() | extra_hashes,
             pairing='Same independent clean channels and standard complex noise for all variants and noise levels.',
             information='Known AWGN query variance; no receiver pseudo-observations and no activity labels.',
             genie_information='Bound alone knows geometry, path powers and LOS complex gain; no unknown diffuse gain is supplied.',
             expected_queries=spec['scenes']*spec['candidates']*len(spec['values'])*len(bundles)))
        print(f'PLANNED: {out}'); return 0
    plan = read(out / 'PLAN.json')
    if plan['experiment']['variable'] != 'denoising_variance':
        raise ValueError('Expected an independent denoising plan')
    return run(out, plan) if args.command == 'run' else summarize(out, plan['experiment'])


if __name__ == '__main__':
    raise SystemExit(main())
