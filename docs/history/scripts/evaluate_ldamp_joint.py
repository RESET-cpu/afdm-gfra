"""Calibrate on reused development scenes or evaluate frozen models on new scenes.

Calibration uses eight already observed physical scenes at -4, 0 and 6 dB.
Evaluation uses disjoint physical scene seeds at all six registered SNRs.
Every failed case is retained. No model or threshold is selected on evaluation.
"""
import argparse
import hashlib
from copy import deepcopy
from collections import Counter
import json
import platform
from pathlib import Path
import sys
import time
import warnings
import numpy as np
import torch
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from afdm_jadcedd.algorithm.registry import build_receiver, DEFAULT_CONFIGS
from afdm_jadcedd.algorithm.baselines.ldamp_joint.receiver import load_configuration, signature
from afdm_jadcedd.experiment.generate import generate_case
from afdm_jadcedd.system.observation import ReceiverInput, load_input
from afdm_jadcedd.utils import sha256, write_json
from validate_ldamp import fit_threshold, quality_by_snr


def score(arrays, truth):
    active = truth['activity'].astype(bool)
    target = truth['channel'] * active[:, None, None, None]
    errors = np.sum(abs(arrays['estimate'] - target)**2, axis=(1, 2, 3))
    result = dict(full_error=float(errors.sum()), active_error=float(errors[active].sum()),
        inactive_error=float(errors[~active].sum()), signal_energy=float(np.sum(abs(target)**2)),
        score=(arrays['activity_score'] if 'activity_score' in arrays else arrays['probabilities']).tolist(),
        active=active.tolist(), users=len(active))
    if 'activity_decision' in arrays:
        decision = arrays['activity_decision'].astype(bool)
        masked = arrays['estimate'] * decision[:, None, None, None]
        result.update(misses=int(np.sum(active & ~decision)), false_alarms=int(np.sum(~active & decision)),
            estimated_activity_masked_error=float(np.sum(abs(masked-target)**2)))
    return result


def receiver_identity(receiver):
    if hasattr(receiver, 'signature'):
        return receiver.signature
    # Proposed exposes its configuration and checkpoint identities but no
    # signature property. Bind its public configuration and source package here.
    sources = {str(p.relative_to(ROOT)): sha256(p)
               for p in (ROOT/'src/afdm_jadcedd').rglob('*.py')}
    payload = dict(configuration=receiver.configuration, sources=sources)
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def warning_summary(caught):
    counts = Counter((str(w.message), w.filename, w.lineno, w.category.__name__) for w in caught)
    return dict(count=len(caught), occurrences=[dict(message=key[0], filename=key[1],
        line=key[2], category=key[3], count=count) for key, count in counts.items()])


def summarize(rows, seed=202610150301):
    """Paired physical-scene bootstrap; users and SNRs are not independent units."""
    reports = []
    methods = sorted({r['method'] for r in rows})
    for snr in sorted({r['snr_db'] for r in rows}):
        selected = [r for r in rows if r['snr_db'] == snr]
        scenes = sorted({r['scene'] for r in selected})
        if any(r['status'] != 'COMPLETE' for r in selected):
            reports.append(dict(snr_db=snr, status='FAILED', reason='At least one retained failed case'))
            continue
        rng = np.random.default_rng(seed)
        indices = rng.integers(len(scenes), size=(5000, len(scenes)))
        boot = {}
        for method in methods:
            values = sorted([r for r in selected if r['method'] == method], key=lambda r: r['scene'])
            if len(values) != len(scenes):
                raise ValueError('Incomplete paired panel')
            errors = np.array([r['full_error'] for r in values])
            powers = np.array([r['signal_energy'] for r in values])
            boot[method] = 10*np.log10(errors[indices].sum(axis=1)/powers[indices].sum(axis=1))
            report = dict(snr_db=snr, method=method, scenes=len(scenes), status='COMPLETE',
                nmse_db=float(10*np.log10(errors.sum()/powers.sum())),
                nmse_db_scene_bootstrap_95=np.quantile(boot[method], [.025, .975]).tolist(),
                mean_seconds=float(np.mean([r['seconds'] for r in values])))
            if all('misses' in r for r in values):
                misses = np.array([r['misses'] for r in values]); false = np.array([r['false_alarms'] for r in values])
                users = np.array([r['users'] for r in values]); positives = np.array([sum(r['active']) for r in values])
                aer = (misses + false)[indices].sum(axis=1)/users[indices].sum(axis=1)
                report.update(misses=int(misses.sum()), false_alarms=int(false.sum()),
                    active_users=int(positives.sum()), inactive_users=int((users-positives).sum()),
                    aer=float((misses+false).sum()/users.sum()),
                    aer_scene_bootstrap_95=np.quantile(aer, [.025, .975]).tolist())
            if all('estimated_activity_masked_error' in r for r in values):
                masked_errors = np.array([r['estimated_activity_masked_error'] for r in values])
                report['estimated_activity_masked_nmse_db'] = float(10*np.log10(masked_errors.sum()/powers.sum()))
            reports.append(report)
        if 'joint' in boot and 'original' in boot:
            difference = boot['joint'] - boot['original']
            reports.append(dict(snr_db=snr, contrast='joint_minus_original_nmse_db',
                paired_scene_bootstrap_95=np.quantile(difference, [.025, .975]).tolist()))
    return reports


def cached_development(source, config):
    """Reuse only an exact input and inference-identity match; never score-based selection."""
    folder = ROOT / 'results/ldamp_complete_20261015/public_development_v2'
    source_hash = sha256(source / 'input.npz')
    expected = signature(config)
    for record_path in sorted(folder.glob('seed*_scene*_snr*.json')):
        record = json.loads(record_path.read_text())
        if record.get('input_sha256') == source_hash and record.get('inference_sha256') == expected:
            path = record_path.with_suffix('.npz')
            if record['output_sha256'] != sha256(path):
                raise ValueError('Cached development output identity mismatch')
            with np.load(path) as saved:
                arrays = {k: saved[k] for k in saved.files}
            return arrays, record, str(path.relative_to(ROOT))
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['calibrate', 'evaluate'], required=True)
    parser.add_argument('--config', type=Path, default=ROOT/'configs/ldamp_joint.json')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--scenes', type=int, default=10)
    parser.add_argument('--seed-base', type=int, default=2026101503100000)
    parser.add_argument('--methods', nargs='+', choices=['joint', 'original', 'proposed', 'somp', 'gamp', 'gnn', 'offgrid_sbl'],
                        default=['joint', 'original'])
    parser.add_argument('--device', choices=['cpu', 'mps'], default='mps')
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Fresh evaluation directory required')
    torch.set_num_threads(1)
    config = load_configuration(args.config)
    calibrating = args.stage == 'calibrate'
    if calibrating:
        config['readout'] = None
        methods = ['joint']; scenes = 8; snrs = [-4, 0, 6]
    else:
        if not config.get('readout'):
            raise ValueError('Freeze activity readout before independent evaluation')
        methods = args.methods; scenes = args.scenes; snrs = [-4, -2, 0, 2, 4, 6]
        if scenes < 1:
            raise ValueError('Positive scene count required')
        seeds = set(range(args.seed_base, args.seed_base+scenes))
        for split in ['train', 'validation']:
            if seeds & set(np.load(ROOT/f'data/proposed/{split}_identities.npy')[:, 0]):
                raise ValueError('Evaluation overlaps denoiser data')
        # Reserved ranges of previously generated receiver studies. The exact
        # new seed range is also written before generation for an external audit.
        if seeds & set(range(2026101452100000, 2026101452100008)):
            raise ValueError('Evaluation overlaps current development scenes')
    args.output.mkdir(parents=True)
    candidate_path = args.output / 'candidate.json'
    write_json(candidate_path, config)
    configs = {'joint': candidate_path}
    configs.update({m: DEFAULT_CONFIGS['ldamp' if m == 'original' else m] for m in methods if m != 'joint'})
    for method in methods:
        if method != 'joint':
            snapshot = args.output/f'configuration_{method}.json'
            write_json(snapshot, json.loads(configs[method].read_text()))
            configs[method] = snapshot
    source_hashes = {}
    for path in (ROOT/'src/afdm_jadcedd').rglob('*.py'):
        relative = path.relative_to(ROOT)
        target = args.output/'sources'/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
        source_hashes[str(relative)] = sha256(target)
    for path in [Path(__file__).resolve(), ROOT/'scripts/validate_ldamp.py']:
        target = args.output/'sources'/path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
        source_hashes[str(path.relative_to(ROOT))] = sha256(target)
    receivers = {m: build_receiver('ldamp' if m in ('joint', 'original') else m,
                 config=configs[m], device=args.device) for m in methods}
    identities = {m: receiver_identity(r) for m, r in receivers.items()}
    plan = dict(stage=args.stage, configuration=config, configurations={m: json.loads(p.read_text()) for m, p in configs.items()},
        inference_sha256=identities, methods=methods, scenes=scenes, snr_db=snrs,
        seed_base=None if calibrating else args.seed_base, script_sha256=sha256(Path(__file__)),
        independent_validation=not calibrating, threshold_rule='Minimum calibration AER; largest threshold on ties',
        source_sha256=source_hashes,
        environment=dict(python=sys.version, platform=platform.platform(), numpy=np.__version__,
            torch=torch.__version__, requested_device=args.device, torch_threads=torch.get_num_threads(),
            blas_thread_limit_during_inference=1, timing='Per-case inference only; model loading and data generation excluded'),
        interpretation='Physical scene is the sampling unit; all methods and SNRs share each scene; 5000 paired scene bootstrap replicates',
        primary_metric='Full raw channel estimate including inactive-user error',
        secondary_metric='Zero estimates only where each method itself declares inactivity; same operation for every method; no true activity mask',
        scope='Reused development scenes' if calibrating else 'Frozen model evaluation, no selection or retuning')
    write_json(args.output/'PLAN.json', plan)
    rows = []; started = time.time()
    for scene in range(scenes):
        for snr in snrs:
            folder = args.output/f'scene{scene:03d}'/f'snr{snr:+03d}'
            folder.mkdir(parents=True)
            try:
                if calibrating:
                    source = ROOT/f'results/ldamp_diagnosis_20261014/receiver_pilot/calibration/scene{scene:03d}/snr{snr:+03d}'
                    inputs = load_input(source/'input.npz')
                    with np.load(source/'truth.npz') as saved:
                        truth = {k: saved[k] for k in saved.files}
                    write_json(folder/'SOURCE.json', dict(path=str(source.relative_to(ROOT)),
                        input_sha256=sha256(source/'input.npz'), truth_sha256=sha256(source/'truth.npz')))
                else:
                    with warnings.catch_warnings(record=True) as caught:
                        warnings.simplefilter('always', RuntimeWarning)
                        public, truth, metadata = generate_case(args.seed_base+scene, snr,
                            json.loads((ROOT/config['bundle_path']).read_text())['scale'],
                            users=40, frames=16, activity_probability=.1, require_active_user=True, grid_mode='off_grid')
                    inputs = ReceiverInput(**{key: public[key] for key in ReceiverInput.__dataclass_fields__})
                    write_json(folder/'generation.json', metadata)
                    write_json(folder/'generation_warnings.json', warning_summary(caught))
                np.savez_compressed(folder/'input.npz', **inputs.arguments())
                np.savez_compressed(folder/'truth.npz', channel=truth['channel'], activity=truth['activity'])
            except Exception as exc:
                for method in methods:
                    rows.append(dict(scene=scene, snr_db=snr, method=method, status='FAILED', phase='GENERATION', error=repr(exc)))
                write_json(args.output/'ROWS.json', rows)
                continue
            for method, receiver in receivers.items():
                row = dict(scene=scene, snr_db=snr, method=method)
                try:
                    reused = cached_development(source, config) if calibrating else None
                    with warnings.catch_warnings(record=True) as caught, threadpool_limits(1):
                        warnings.simplefilter('always', RuntimeWarning)
                        if reused is None:
                            arrays, record = receiver.infer(inputs)
                        else:
                            arrays, record, reused_path = reused
                            record = deepcopy(record); record['reused_from'] = reused_path
                    if not all(np.isfinite(value).all() for value in arrays.values()):
                        raise FloatingPointError('Nonfinite public receiver output')
                    target = folder/f'{method}.npz'
                    np.savez_compressed(target, **arrays)
                    record.update(input_sha256=sha256(folder/'input.npz'), output_sha256=sha256(target))
                    write_json(target.with_suffix('.json'), record)
                    write_json(folder/f'{method}.warnings.json', warning_summary(caught))
                    row.update(status='COMPLETE', **score(arrays, truth), seconds=record['seconds'],
                        warning_count=len(caught), inference_sha256=identities[method])
                except Exception as exc:
                    row.update(status='FAILED', phase='INFERENCE', error=repr(exc))
                rows.append(row)
                write_json(args.output/'ROWS.json', rows)
                write_json(args.output/'STATUS.json', dict(status='RUNNING', completed=len(rows),
                    expected=scenes*len(snrs)*len(methods), seconds=time.time()-started))
                print(json.dumps({k: v for k, v in row.items() if k not in ('score', 'active')}), flush=True)
    if any(r['status'] != 'COMPLETE' for r in rows):
        write_json(args.output/'STATUS.json', dict(status='FAILED', completed=len(rows), failures=sum(r['status'] != 'COMPLETE' for r in rows)))
        return 1
    # Reconstruct receivers to catch source, model or readout changes during a run.
    for method in methods:
        fresh = build_receiver('ldamp' if method in ('joint', 'original') else method,
                               config=configs[method], device='cpu')
        if receiver_identity(fresh) != identities[method]:
            raise ValueError('Inference identity changed during evaluation')
        del fresh
    if calibrating:
        scores = np.concatenate([r['score'] for r in rows]); labels = np.concatenate([r['active'] for r in rows])
        threshold, errors = fit_threshold(scores, labels)
        path = args.output/'READOUT.json'
        write_json(path, dict(inference_sha256=identities['joint'], threshold=threshold,
            calibration_errors=errors, calibration_users=len(labels), scenes=scenes, snr_db=snrs,
            scope='Already observed development scenes; not independent validation',
            statistic='channel_frobenius_energy', true_snr_used=False, objective=plan['threshold_rule']))
        config['readout'] = dict(path=str(path.resolve().relative_to(ROOT)), sha256=sha256(path))
        config['validation_status'] = 'CALIBRATED_AWAITING_INDEPENDENT_VALIDATION'
        write_json(args.output/'receiver.json', config)
        for row in rows:
            active = np.array(row['active'], bool); score_values = np.array(row['score'])
            decision = (score_values >= threshold) & (score_values > 0)
            row.update(misses=int(np.sum(active & ~decision)), false_alarms=int(np.sum(~active & decision)))
            folder = args.output/f"scene{row['scene']:03d}"/f"snr{row['snr_db']:+03d}"
            with np.load(folder/'joint.npz') as saved, np.load(folder/'truth.npz') as truth:
                target = truth['channel']*active[:, None, None, None]
                masked = saved['estimate']*decision[:, None, None, None]
                row['estimated_activity_masked_error'] = float(np.sum(abs(masked-target)**2))
        write_json(args.output/'ROWS.json', rows)
    quality = None
    joint_rows = [row for row in rows if row['method'] == 'joint']
    if joint_rows:
        threshold = json.loads((ROOT/config['readout']['path']).read_text())['threshold']
        quality = quality_by_snr(joint_rows, threshold)
        write_json(args.output/'MINIMUM_UTILITY.json', quality)
    write_json(args.output/'SUMMARY.json', dict(results=summarize(rows), independent_validation=not calibrating,
        minimum_utility=quality, default_configuration_installed=False))
    write_json(args.output/'STATUS.json', dict(status='COMPLETE', seconds=time.time()-started,
        completed=len(rows), minimum_utility_passed=None if quality is None else quality['status'] == 'PASS',
        default_configuration_installed=False))
    return 1 if quality is not None and quality['status'] != 'PASS' else 0


if __name__ == '__main__':
    raise SystemExit(main())
