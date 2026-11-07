"""Paired activity-evidence ablation with frozen channel networks and MP controls."""
from pathlib import Path
import argparse
import csv
import json
import time

import numpy as np
from _common import run, summarize, validate
from _support import ROOT
from _support.storage import read, save, sha, identities, verify_sources
from _support.settings import DEFAULTS, CONFIGS, PHASE_CONFIG, HISTORICAL_SNR, solver, proposed_bundles
from _support.density_ratio import GaussianSiteReceiver


# Include the full seven-SNR historical panel in this dedicated ablation.
EXPERIMENT = dict(
    DEFAULTS, description=__doc__, variable='snr_db', xlabel='SNR (dB)',
    values=[-4, -2, 0, 2, 4, 6, 8], seed=202610172000001,
    methods=['proposed', 'gaussian_site'], experiment_kind='density_ratio_ablation',
    bootstrap_replicates=10000, bootstrap_seed=2026101801,
)


def receiver_factory(method, spec):
    if method == 'proposed':
        return solver(method, spec)
    if method == 'gaussian_site':
        return GaussianSiteReceiver(spec['proposed_bundles']['proposed']['configuration'],
                                    device=spec['device'])
    raise ValueError('This ablation compares exactly the two activity-evidence choices')


def paired_statistics(out, spec):
    """Bootstrap entire paired scenes, retaining all users and the SNR pairing."""
    rows = []
    n = spec['scenes']
    for index, snr in enumerate(spec['values']):
        pairs = []
        for scene in range(n):
            folder = out / f'scene{scene:03d}' / f'condition{index:02d}'
            a, b = [read(folder / f'{method}.json') for method in spec['methods']]
            if a['status'] != 'COMPLETE' or b['status'] != 'COMPLETE':
                raise ValueError('Paired analysis requires every planned result')
            if a['input_array_sha256'] != b['input_array_sha256']:
                raise ValueError('Paired receivers used different observations')
            ma, mb = a['metrics'], b['metrics']
            for key in ('active', 'inactive', 'signal_energy'):
                if ma[key] != mb[key]:
                    raise ValueError('Paired scoring truth differs: ' + key)
            pairs.append([ma['misses']+ma['false_alarms'], mb['misses']+mb['false_alarms'],
                          ma['full_error'], mb['full_error'], ma['active']+ma['inactive'],
                          ma['misses'], mb['misses'], ma['false_alarms'], mb['false_alarms'],
                          ma['active'], ma['inactive']])
        data = np.asarray(pairs, dtype=float)

        def differences(totals):
            return np.stack(((totals[..., 0]-totals[..., 1])/totals[..., 4],
                             10*np.log10(totals[..., 2]/totals[..., 3])), axis=-1)

        total = data.sum(axis=0)
        delta_aer = (total[0]-total[1])/total[4]
        delta_nmse = float(10*np.log10(total[2]/total[3])) if np.all(total[2:4] > 0) else None
        row = dict(snr_db=snr, paired_scenes=n,
                   delta_aer=float(delta_aer), delta_nmse_db=delta_nmse,
                   exact_zero_channel_error=bool(np.any(total[2:4] == 0)),
                   learned_misses=int(total[5]), gaussian_misses=int(total[6]),
                   learned_false_alarms=int(total[7]), gaussian_false_alarms=int(total[8]),
                   active=int(total[9]), inactive=int(total[10]))
        if n >= 2 and np.all(data[:, 2:4] > 0):
            # Reset seed per SNR so the same scene resamples are used across SNRs.
            rng = np.random.default_rng(spec['bootstrap_seed'])
            boot = []
            remaining = spec['bootstrap_replicates']
            while remaining:
                batch = min(remaining, 200)
                chosen = rng.integers(0, n, size=(batch, n))
                boot.append(differences(data[chosen].sum(axis=1)))
                remaining -= batch
            low, high = np.quantile(np.concatenate(boot), [.025, .975], axis=0)
            row.update(delta_aer_ci95_low=float(low[0]), delta_aer_ci95_high=float(high[0]),
                       delta_nmse_db_ci95_low=float(low[1]), delta_nmse_db_ci95_high=float(high[1]))
        rows.append(row)
    save(out / 'PAIRED_STATISTICS.json', dict(
        rows=rows, difference='Learned density ratio minus Gaussian-site evidence; negative favors learned.',
        interval='Pointwise 95% paired scene bootstrap percentile intervals; not simultaneous intervals.',
        bootstrap_replicates=spec['bootstrap_replicates'], bootstrap_seed=spec['bootstrap_seed'],
        small_sample_note='Intervals omitted for fewer than two scenes or exact zero channel errors.'))
    with (out / 'PAIRED_STATISTICS.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        writer.writeheader(); writer.writerows(rows)
    return rows


def finish(out, spec):
    paired_statistics(out, spec)
    summary = read(out / 'SUMMARY.json')
    summary['statistics'] = 'Pooled counts and energies; paired scene intervals in PAIRED_STATISTICS.json.'
    save(out / 'SUMMARY.json', summary)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('plan', 'run', 'summarize'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--scenes', type=int, default=EXPERIMENT['scenes'])
    parser.add_argument('--seed', type=int, default=EXPERIMENT['seed'])
    parser.add_argument('--values', type=float, nargs='+', default=EXPERIMENT['values'])
    parser.add_argument('--device', choices=('auto', 'cpu', 'mps'), default='auto')
    parser.add_argument('--fresh', action='store_true', help='Run both arms on newly generated inputs; do not reuse historical results')
    args = parser.parse_args(argv)
    out = args.output.resolve()
    if args.command == 'plan':
        if out.exists() and any(out.iterdir()):
            raise FileExistsError('Plan requires a fresh empty directory')
        import torch
        device = ('mps' if torch.backends.mps.is_available() else 'cpu') if args.device == 'auto' else args.device
        if device == 'mps' and not torch.backends.mps.is_available():
            raise ValueError('MPS is unavailable; use CPU')
        bundles, hashes = proposed_bundles()
        bundles['proposed']['label'] = 'Proposed (learned density ratio)'
        bundles['gaussian_site'] = dict(label='Gaussian-site activity evidence')
        spec = dict(EXPERIMENT, scenes=args.scenes, seed=args.seed, values=args.values,
                    device=device, scale=bundles['proposed']['configuration']['scale'],
                    proposed_bundles=bundles, phase_config=PHASE_CONFIG,
                    receiver_configs={'proposed': CONFIGS['proposed']},
                    reuse_require_same_device=True)
        if not args.fresh:
            spec['reuse_plan'] = HISTORICAL_SNR
            hashes[HISTORICAL_SNR] = sha(ROOT / HISTORICAL_SNR)
        validate(spec)
        save(out / 'PLAN.json', dict(
            experiment=spec, source_and_weight_sha256=identities() | hashes,
            created_unix=time.time(), expected_runs=2*spec['scenes']*len(spec['values']),
            intervention='Only replace learned activity evidence with normalized Gaussian-site evidence in every MP iteration.',
            controls='Same score weights, phase/noise estimators, initialization, damping, variance bounds, stopping rules and decision threshold.',
            pairing='Same scene, observation, estimated phase, and compute backend for both arms.',
            reuse='Reuse verified Proposed results only on the same backend; otherwise recompute. Gaussian-site results are always new.',
            analysis='AER, misses, false alarms, full-channel NMSE and paired scene bootstrap intervals.'))
        print(json.dumps(dict(status='PLANNED', output=str(out), expected_runs=2*spec['scenes']*len(spec['values']))))
        return 0
    plan = read(out / 'PLAN.json')
    if plan['experiment'].get('experiment_kind') != 'density_ratio_ablation':
        raise ValueError('Use this entry only for a density-ratio ablation plan')
    verify_sources(plan)
    if args.command == 'run':
        code = run(out, plan, receiver_factory=receiver_factory)
    else:
        code = summarize(out, plan['experiment'])
    if code == 0:
        finish(out, plan['experiment'])
    return code


if __name__ == '__main__':
    from _suite_entry import dispatch
    raise SystemExit(dispatch(__file__))
