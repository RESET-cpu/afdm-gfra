"""Run five frozen baselines with an observation-only shared phase estimate."""
import argparse
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time
import traceback
import warnings

import numpy as np
import torch
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT/'src')); sys.path.insert(0, str(ROOT/'scripts'))
from experiments.unknown_phase_20261015 import model, estimate_phase
from afdm_jadcedd.algorithm.registry import build_receiver, DEFAULT_CONFIGS, verify_algorithms
from afdm_jadcedd.system.phase import wrap
from afdm_jadcedd.utils import sha256, write_json
from evaluate_ldamp_joint import score, warning_summary, summarize

METHODS = ['somp', 'gamp', 'gnn', 'offgrid_sbl', 'ldamp']
SNRS = [-4, -2, 0, 2, 4, 6]


def seed_audit(seeds):
    prior_path = ROOT/'results/ldamp_complete_20261015/COMPARISON_SEED_AUDIT.json'
    prior = json.loads(prior_path.read_text())
    assert prior['status'] == 'PASS_SEED_SEPARATION'
    for path, digest in prior['source_sha256'].items():
        assert sha256(ROOT/path) == digest, path
    checks = []
    for row in prior['checks']:
        passed = all(not row['minimum'] <= seed <= row['maximum'] for seed in seeds)
        checks.append(dict(source=row['source'], minimum=row['minimum'], maximum=row['maximum'], passed=passed))
        assert passed, row['source']
    old = json.loads((ROOT/'results/ldamp_structure_20261015/PLAN.json').read_text())
    for values in [prior['evaluation_seeds'], old['reserved_new_test_seeds'], old['allowed_development_seeds']]:
        assert not set(seeds) & set(values)
    return dict(status='PASS', seeds=seeds, checks=checks,
                prior_audit_sha256=sha256(prior_path), bound_sources=prior['source_sha256'],
                limitation='Disjoint from the verified training/development cohorts and preceding comparison panels; historical missing configuration references remain outside verification.')


def phase_metrics(phase, truth, frames):
    active = truth['activity'].astype(bool)
    delta = wrap(phase['phase_slopes']-truth['phase_slopes'])
    phasor = np.exp(1j*np.arange(frames)[:, None]*delta[None, active])-1
    return dict(active_users=int(active.sum()), active_phase_squared_error=float(np.sum(delta[active]**2)),
                active_phase_rmse_rad=float(np.sqrt(np.mean(delta[active]**2))),
                active_frame_phasor_squared_error=float(np.sum(abs(phasor)**2)),
                active_doppler_squared_error_hz2=float(np.sum((phase['doppler_hz'][active]-truth['doppler_hz'][active])**2)),
                active_phase_errors_rad=delta[active].tolist())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--scenes', type=int, default=10)
    parser.add_argument('--seed-base', type=int, default=2026101511100000)
    parser.add_argument('--device', choices=['cpu', 'mps'], default='mps')
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Fresh result directory required')
    if args.scenes < 1:
        raise ValueError('Positive scene count required')
    seeds = list(range(args.seed_base, args.seed_base+args.scenes))
    separation = seed_audit(seeds)
    torch.set_num_threads(1)
    with threadpool_limits(1):
        verification = verify_algorithms()
        paths = {method: DEFAULT_CONFIGS[method] for method in METHODS}
        paths['ldamp'] = ROOT/'configs/ldamp_output_tsvd.json'
        receivers = {method: build_receiver(method, config=paths[method], device=args.device) for method in METHODS}
    controls = estimate_phase.Controls()
    phase_signature = estimate_phase.signature(controls)
    identities = {}
    for method, receiver in receivers.items():
        payload = dict(base=receiver.signature, phase=phase_signature,
                       protocol='Estimate phase from Y/P, then run the frozen baseline')
        identities[method] = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    args.output.mkdir(parents=True)
    out = args.output
    sources = list((ROOT/'src/afdm_jadcedd').rglob('*.py'))
    sources += list(Path(__file__).parent.glob('*.py'))
    sources += [ROOT/'scripts/evaluate_ldamp_joint.py', ROOT/'tests/test_unknown_phase_estimator.py',
                ROOT/'tests/test_unknown_phase_model.py', ROOT/'tests/test_ldamp_output.py']
    hashes = {str(p.relative_to(ROOT)): sha256(p) for p in sources}
    for p in sources:
        target = out/'sources'/p.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(p.read_bytes())
    plan = dict(stage='evaluate', scenes=args.scenes, seed_base=args.seed_base, seeds=seeds, snr_db=SNRS,
                methods=METHODS, users=40, frames=16, array=[4,4], grid_mode='off_grid',
                activity_probability=.1, require_active_user=True, phase_controls=asdict(controls),
                phase_inference_sha256=phase_signature, inference_sha256=identities,
                baseline_inference_sha256={m:r.signature for m,r in receivers.items()},
                configurations={m:json.loads(p.read_text()) for m,p in paths.items()},
                configuration_sha256={str(p.relative_to(ROOT)):sha256(p) for p in set(paths.values())},
                sources=hashes, mainline_asset_verification=verification,
                receiver_input_fields=list(model.UnknownPhaseInput.__dataclass_fields__),
                truth_used_in_inference=False, shared_phase_estimator=True,
                procedure='Observation-only common phase estimation followed by each frozen conditional baseline',
                qualification='First unknown-phase evaluation of adapted two-stage receivers; not native paper reproductions',
                threshold_policy='Original known-phase calibrated thresholds transferred without retuning',
                primary_metric='Unmasked full-channel pooled error/energy, including inactive-user errors',
                timing='Each method charged full shared phase-estimation time plus its inference time; loading and generation excluded',
                uncertainty='5000 physical-scene bootstrap resamples; pointwise intervals; fixed weights and inference seeds',
                environment=dict(python=sys.version, numpy=np.__version__, torch=torch.__version__,
                                 platform=platform.platform(), device=args.device, torch_threads=1, blas_threads=1),
                pid=os.getpid(), started_unix=time.time(), hard_timeout_seconds=3600)
    write_json(out/'PLAN.json', plan); write_json(out/'SEED_AUDIT.json', separation)
    rows, phase_rows = [], []
    started = time.monotonic()

    def progress(stage, scene, snr, method=None):
        state = dict(status='RUNNING', stage=stage, scene=scene, snr_db=snr, method=method,
                     completed_rows=len(rows), expected_rows=args.scenes*len(SNRS)*len(METHODS),
                     completed_phase_conditions=len(phase_rows), pid=os.getpid(), seconds=time.monotonic()-started)
        write_json(out/'STATUS.json', state)
        print(json.dumps(state), flush=True)
        if state['seconds'] > plan['hard_timeout_seconds']:
            raise TimeoutError('Recorded one-hour experiment budget exceeded')

    for scene in range(args.scenes):
        for snr in SNRS:
            folder = out/f'scene{scene:03d}'/f'snr{snr:+03d}'; folder.mkdir(parents=True)
            progress('generate', scene, snr)
            try:
                with warnings.catch_warnings(record=True) as caught, threadpool_limits(1):
                    warnings.simplefilter('always', RuntimeWarning)
                    inputs, truth, metadata = model.generate_case(seeds[scene], snr, .2647966452702405)
                metadata['estimator_status'] = 'SHARED_PHASE_ESTIMATOR_IMPLEMENTED_UNDER_EVALUATION'
                np.savez_compressed(folder/'input.npz', **inputs.arguments())
                np.savez_compressed(folder/'truth.npz', **truth)
                write_json(folder/'generation.json', metadata)
                write_json(folder/'generation_warnings.json', warning_summary(caught))
                del truth
                progress('estimate_phase', scene, snr)
                with warnings.catch_warnings(record=True) as caught, threadpool_limits(1):
                    warnings.simplefilter('always', RuntimeWarning)
                    phase, phase_record = estimate_phase.estimate(inputs, controls,
                        observer=lambda row: progress('phase_sweep_'+str(row['sweep']), scene, snr))
                np.savez_compressed(folder/'phase.npz', **phase)
                phase_record.update(input_sha256=sha256(folder/'input.npz'), output_sha256=sha256(folder/'phase.npz'),
                                    warnings=warning_summary(caught))
                write_json(folder/'phase.json', phase_record)
                conditional = inputs.at_estimated_phase(phase['phase_slopes'])
                np.savez_compressed(folder/'estimated_operator_input.npz', **conditional.arguments())
            except Exception as exc:
                failure = dict(status='FAILED', scene=scene, snr_db=snr, error=repr(exc), traceback=traceback.format_exc())
                write_json(folder/'phase_failure.json', failure)
                rows.extend(dict(failure, method=m) for m in METHODS)
                write_json(out/'ROWS.json', rows)
                print(json.dumps(failure), flush=True)
                continue
            for method in METHODS:
                progress('baseline', scene, snr, method)
                try:
                    with warnings.catch_warnings(record=True) as caught, threadpool_limits(1):
                        warnings.simplefilter('always', RuntimeWarning)
                        arrays, record = receivers[method].infer(conditional)
                    if not all(np.isfinite(v).all() for v in arrays.values()):
                        raise FloatingPointError('Nonfinite baseline output')
                    target = folder/f'{method}.npz'; np.savez_compressed(target, **arrays)
                    record.update(baseline_seconds=record['seconds'], phase_seconds=phase_record['seconds'],
                                  seconds=record['seconds']+phase_record['seconds'],
                                  baseline_inference_sha256=record['inference_sha256'],
                                  inference_sha256=identities[method], phase_inference_sha256=phase_signature,
                                  public_unknown_phase_input_sha256=sha256(folder/'input.npz'),
                                  input_sha256=sha256(folder/'estimated_operator_input.npz'), output_sha256=sha256(target),
                                  phase_estimate_sha256=sha256(folder/'phase.npz'),
                                  operator_provenance='Estimated slopes from observation-only shared physical-path fit',
                                  validation_status='UNKNOWN_PHASE_TRANSFER_EVALUATION',
                                  activity_threshold_scope='Frozen known-phase rule, not recalibrated for phase errors',
                                  warnings=warning_summary(caught), truth_used_in_inference=False)
                    write_json(folder/f'{method}.json', record)
                    # Truth enters only after this method's inference has returned.
                    with np.load(folder/'truth.npz', allow_pickle=False) as saved:
                        truth = {key:saved[key] for key in saved.files}
                    row = dict(scene=scene, snr_db=snr, method=method, status='COMPLETE', **score(arrays, truth),
                               seconds=record['seconds'], baseline_seconds=record['baseline_seconds'],
                               phase_seconds=record['phase_seconds'], input_sha256=record['input_sha256'],
                               public_unknown_phase_input_sha256=record['public_unknown_phase_input_sha256'],
                               output_sha256=record['output_sha256'], inference_sha256=identities[method],
                               warning_count=len(caught))
                    del truth
                except Exception as exc:
                    row = dict(scene=scene, snr_db=snr, method=method, status='FAILED',
                               error=repr(exc), traceback=traceback.format_exc())
                    write_json(folder/f'{method}_failure.json', row)
                rows.append(row); write_json(out/'ROWS.json', rows)
            with np.load(folder/'truth.npz', allow_pickle=False) as saved:
                truth = {key:saved[key] for key in saved.files}
            phase_rows.append(dict(scene=scene, snr_db=snr, seconds=phase_record['seconds'],
                                   **phase_metrics(phase, truth, len(inputs.pilot))))
            del truth
            write_json(out/'PHASE_METRICS.json', phase_rows)
            progress('condition_complete', scene, snr)
    failures = [row for row in rows if row['status'] != 'COMPLETE']
    changed = [p for p,digest in hashes.items() if sha256(ROOT/p) != digest]
    if estimate_phase.signature(controls) != phase_signature:
        changed.append('phase signature')
    write_json(out/'SUMMARY.json', dict(results=summarize(rows), failures=failures,
                                      source_changes=changed, phase_metrics=phase_rows))
    write_json(out/'STATUS.json', dict(status='COMPLETE' if not failures and not changed else 'FAILED',
                completed_rows=len(rows), expected_rows=args.scenes*len(SNRS)*len(METHODS),
                phase_conditions=len(phase_rows), failures=len(failures), source_changes=changed,
                seconds=time.monotonic()-started, pid=os.getpid()))
    if failures or changed:
        raise SystemExit(1)
    print(json.dumps(dict(status='COMPLETE', rows=len(rows), seconds=time.monotonic()-started)), flush=True)


if __name__ == '__main__':
    main()
