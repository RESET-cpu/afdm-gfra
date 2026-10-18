"""Calibrate an activity threshold, then evaluate L-DAMP on disjoint new scenes.

Independent scene validation only; comparative evaluation is separate.
All numerical failures are retained and prevent promotion.
Neither truth nor a realized activity count is passed to the receiver.
"""
import argparse
import json
from pathlib import Path
import sys
import time
import warnings
import numpy as np
import torch
from threadpoolctl import threadpool_limits

ROOT=next(parent for parent in Path(__file__).resolve().parents
          if (parent/'src/afdm_jadcedd').is_dir())
sys.path.insert(0,str(ROOT/'src'))
from afdm_jadcedd.algorithm.baselines.ldamp.receiver import LDAMPReceiver, load_configuration, verify
from afdm_jadcedd.experiment.generate import generate_case
from afdm_jadcedd.system.observation import ReceiverInput
from afdm_jadcedd.utils import write_json,sha256

# Float32 residual cancellation can make an untrained zero estimate appear a
# few parts in 1e7 better than zero. This margin is numerical, not statistical.
ZERO_RELATIVE_MARGIN = 1e-4


def beats_zero(error, zero):
    return bool(np.isfinite([error, zero]).all() and
                zero > 0 and 0 <= error < zero*(1-ZERO_RELATIVE_MARGIN))


def audit_denoiser_validation(config):
    """Check selected weights against their saved, training-held-out zero baseline."""
    if config.get('schema') == 'afdm-ldamp-beam-v2':
        verify(config)
        path = ROOT/config['bank_path']
        bank = json.loads(path.read_text())
        rows = []
        for entry in bank['entries']:
            payload = torch.load(path.parent/entry['path'], map_location='cpu', weights_only=True)
            metric = payload.get('validation')
            if metric is None or metric != entry['validation']:
                raise ValueError('Validation metadata is not bound to the selected denoiser weights')
            if payload['recipe']['noise_complex_variance'] != entry['bounds']:
                raise ValueError('Validation interval differs from the selected bank')
            error, zero = float(metric['mse']), float(metric['zero_mse'])
            rows.append(dict(band=entry['index'], mse_real=error, zero_estimator_mse=zero,
                             passed=beats_zero(error, zero), checkpoint_sha256=entry['sha256']))
        return dict(status='PASS' if all(row['passed'] for row in rows) else 'FAILED', bands=rows,
                    relative_numerical_margin=ZERO_RELATIVE_MARGIN,
                    criterion='Each selected denoiser must beat zero on held-out denoising validation; this is not receiver validation')
    path = ROOT/config['checkpoint_path']
    bank = torch.load(path, map_location='cpu', weights_only=True)
    metrics = bank.get('validation')
    if metrics is None:
        metrics = []
        for band, state in enumerate(bank['models']):
            companion = path.parent/f'band{band:02d}'/'denoiser.pt'
            if not companion.is_file():
                return dict(status='UNAVAILABLE', reason='Selected denoiser validation metadata missing')
            saved = torch.load(companion, map_location='cpu', weights_only=True)
            if set(saved['model']) != set(state) or any(
                    not torch.equal(saved['model'][key], state[key]) for key in state):
                raise ValueError('Validation metadata is not bound to the selected denoiser weights')
            metrics.append(saved['validation'])
    if len(metrics) != len(bank['models']):
        raise ValueError('Incomplete selected-band validation metadata')
    rows = []
    for band, metric in enumerate(metrics):
        error, zero = float(metric['mse_real']), float(metric['zero_estimator_mse'])
        passed = beats_zero(error, zero)
        rows.append(dict(band=band, mse_real=error, zero_estimator_mse=zero, passed=passed))
    return dict(status='PASS' if all(row['passed'] for row in rows) else 'FAILED', bands=rows,
                relative_numerical_margin=ZERO_RELATIVE_MARGIN,
                criterion='Each selected denoiser must beat zero on its held-out training validation; numerical margin is not a statistical significance claim')


def receiver_quality(rows, errors):
    """Minimum utility checks; failures remain recorded, never relabeled or dropped."""
    labels = np.concatenate([row['active'] for row in rows]).astype(bool)
    constant_errors = min(int(labels.sum()), int((~labels).sum()))
    full_error = sum(row['full_error'] for row in rows)
    signal_energy = sum(row['signal_energy'] for row in rows)
    passed = beats_zero(full_error, signal_energy) and 0 <= errors < constant_errors
    return dict(status='PASS' if passed else 'FAILED', full_error=full_error,
                zero_estimator_error=signal_energy, activity_errors=int(errors),
                best_constant_activity_errors=constant_errors,
                criterion='Beat the zero channel estimate and the best constant activity decision')


def fit_threshold(scores, labels):
    candidates=np.unique(np.r_[0., scores, np.nextafter(scores,np.inf), np.nextafter(1.,np.inf)])
    errors=np.array([np.count_nonzero(((scores>=t)&(scores>0))!=labels) for t in candidates])
    # Fixed conservative tie convention; no evaluation labels are consulted.
    i=np.flatnonzero(errors==errors.min())[-1]
    return float(candidates[i]),int(errors[i])


def quality_by_snr(rows, threshold):
    checks = []
    for snr in sorted({row['snr_db'] for row in rows}):
        selected = [row for row in rows if row['snr_db'] == snr]
        scores = np.concatenate([row['score'] for row in selected])
        labels = np.concatenate([row['active'] for row in selected])
        errors = int(np.count_nonzero(((scores >= threshold) & (scores > 0)) != labels))
        checks.append(dict(snr_db=snr, **receiver_quality(selected, errors)))
    return dict(status='PASS' if all(row['status'] == 'PASS' for row in checks) else 'FAILED', results=checks)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--device',choices=['cpu','mps'],default='mps')
    parser.add_argument('--calibration-seed-base',type=int,default=2026101469100000)
    parser.add_argument('--evaluation-seed-base',type=int,default=2026101469200000)
    parser.add_argument('--calibration-scenes',type=int,default=8)
    parser.add_argument('--evaluation-scenes',type=int,default=16)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError('Fresh validation directory required')
    cfg=load_configuration(args.config)
    if cfg['validation_status']=='SMOKE_ONLY':raise ValueError('Smoke weights cannot enter receiver validation')
    cfg['readout']=None
    torch.set_num_threads(1)
    receiver=LDAMPReceiver(cfg,device=args.device)
    args.output.mkdir(parents=True)
    audit = audit_denoiser_validation(cfg)
    write_json(args.output/'DENOISER_VALIDATION.json', audit)
    if audit['status'] != 'PASS':
        write_json(args.output/'STATUS.json', dict(status='FAILED', phase='DENOISER_VALIDATION',
            reason=audit, default_configuration_installed=False))
        return 1
    snrs=[-4,-2,0,2,4,6]
    bases={'calibration':args.calibration_seed_base,'evaluation':args.evaluation_seed_base}
    counts={'calibration':args.calibration_scenes,'evaluation':args.evaluation_scenes}
    if min(counts.values()) < 1:raise ValueError('Positive scene counts required')
    scene_sets={split:set(range(base,base+counts[split])) for split,base in bases.items()}
    if scene_sets['calibration'] & scene_sets['evaluation']:
        raise ValueError('Calibration and evaluation scenes must be disjoint')
    for split in ('train','validation'):
        ids=set(np.load(ROOT/f'data/proposed/{split}_identities.npy')[:,0].tolist())
        if any(ids & scenes for scenes in scene_sets.values()):
            raise ValueError('Receiver scenes overlap denoiser training or validation')
    initial_signature=receiver.signature
    statistic='channel_frobenius_energy' if cfg.get('schema')=='afdm-ldamp-beam-v2' else 'channel_energy_over_max_user_energy'
    write_json(args.output/'PLAN.json',dict(snr_db=snrs,scenes_per_split=counts,seed_bases=bases,
        inference_sha256=receiver.signature,configuration=cfg,statistic=statistic,
        threshold_objective='minimum calibration AER; largest threshold on ties',
        validation_script_sha256=sha256(Path(__file__)),
        statistical_scope='Physical scenes are independent; SNR points reuse each scene. This is not a paired baseline comparison.'))
    rows=[]
    threshold=None
    for split,base in bases.items():
        count=counts[split]
        for scene in range(count):
            for snr in snrs:
                folder=args.output/split/f'scene{scene:03d}'/f'snr{snr:+03d}'
                folder.mkdir(parents=True)
                try:
                    with warnings.catch_warnings(record=True) as generation_warnings:
                        warnings.simplefilter('always',RuntimeWarning)
                        public,truth,metadata=generate_case(base+scene,snr,cfg['scale'],users=40,
                            frames=16,activity_probability=.1,require_active_user=True,grid_mode='off_grid')
                    if not np.isfinite(truth['channel']).all():raise FloatingPointError('Nonfinite generated truth')
                    inputs=ReceiverInput(**{k:public[k] for k in ReceiverInput.__dataclass_fields__})
                    np.savez_compressed(folder/'input.npz',**inputs.arguments())
                    np.savez_compressed(folder/'truth.npz',channel=truth['channel'],activity=truth['activity'])
                    write_json(folder/'generation.json',metadata)
                    write_json(folder/'generation_warnings.json',dict(count=len(generation_warnings),
                        messages=sorted(set(str(w.message) for w in generation_warnings)),public_and_truth_finite=True))
                    with threadpool_limits(1):arrays,record=receiver.infer(inputs)
                    if not all(np.isfinite(v).all() for v in arrays.values()):
                        raise FloatingPointError('Nonfinite receiver output')
                    np.savez_compressed(folder/'estimate.npz',**arrays)
                    record.update(input_sha256=sha256(folder/'input.npz'),output_sha256=sha256(folder/'estimate.npz'))
                    write_json(folder/'receiver.json',record)
                    active=np.asarray(truth['activity'],bool)
                    target=truth['channel']*active[:,None,None,None]
                    errors=np.sum(abs(arrays['estimate']-target)**2,axis=(1,2,3))
                    row=dict(split=split,scene=scene,snr_db=snr,status='COMPLETE',
                        score=arrays['activity_score'].tolist(),active=active.tolist(),
                        full_error=float(errors.sum()),active_error=float(errors[active].sum()),
                        signal_energy=float(np.sum(abs(target)**2)),seconds=record['seconds'],
                        outside_noise_support_calls=record['outside_noise_support_calls'])
                    if threshold is not None:
                        decision=arrays['activity_decision']
                        row.update(misses=int(np.sum(active&~decision)),false_alarms=int(np.sum(~active&decision)))
                except Exception as error:
                    row=dict(split=split,scene=scene,snr_db=snr,status='FAILED',error=repr(error))
                    write_json(folder/'FAILURE.json',row)
                rows.append(row)
                write_json(args.output/'ROWS.json',rows)
                write_json(args.output/'STATUS.json',dict(status=split.upper(),completed=len(rows),expected=6*sum(counts.values()),
                    failures=sum(r['status']=='FAILED' for r in rows),updated_unix=time.time()))
        selected=[r for r in rows if r['split']==split]
        if any(r['status']=='FAILED' for r in selected):
            write_json(args.output/'STATUS.json',dict(status='FAILED',phase=split,
                completed=len(rows),failures=sum(r['status']=='FAILED' for r in selected),
                note='No failed cases excluded; no activity rule or formal configuration promoted'))
            return 1
        if split=='calibration':
            scores=np.concatenate([r['score'] for r in selected])
            labels=np.concatenate([r['active'] for r in selected])
            threshold,errors=fit_threshold(scores,labels)
            policy=args.output/'READOUT.json'
            write_json(policy,dict(inference_sha256=receiver.signature,threshold=threshold,
                calibration_errors=errors,calibration_users=len(labels),seed_base=base,scenes=count,
                statistic=statistic,true_snr_used=False))
            quality = quality_by_snr(selected, threshold)
            write_json(args.output/'CALIBRATION_QUALITY.json', quality)
            if quality['status'] != 'PASS':
                write_json(args.output/'STATUS.json', dict(status='FAILED', phase='CALIBRATION_QUALITY',
                    reason=quality, threshold=threshold, default_configuration_installed=False))
                return 1
            cfg['readout']=dict(path=str(policy.resolve()),sha256=sha256(policy))
            receiver=LDAMPReceiver(cfg,device=args.device)
        else:
            quality = quality_by_snr(selected, threshold)
            write_json(args.output/'EVALUATION_QUALITY.json', quality)
            if quality['status'] != 'PASS':
                write_json(args.output/'STATUS.json', dict(status='FAILED', phase='EVALUATION_QUALITY',
                    reason=quality, default_configuration_installed=False))
                return 1
    summary=[]
    for snr in snrs:
        subset=[r for r in rows if r['split']=='evaluation' and r['snr_db']==snr]
        error=sum(r['full_error'] for r in subset);energy=sum(r['signal_energy'] for r in subset)
        summary.append(dict(snr_db=snr,scenes=len(subset),full_nmse_db=float(10*np.log10(max(error/energy,1e-30))),
            misses=sum(r['misses'] for r in subset),false_alarms=sum(r['false_alarms'] for r in subset),
            users=len(subset)*40,mean_seconds=float(np.mean([r['seconds'] for r in subset])),
            outside_noise_support_calls=sum(r['outside_noise_support_calls'] for r in subset)))
    if verify(cfg)['inference_sha256'] != initial_signature:
        write_json(args.output/'STATUS.json',dict(status='FAILED',phase='INFERENCE_IDENTITY'))
        raise ValueError('Inference sources or weights changed during validation')
    cfg['validation_status']='RECEIVER_PILOT_COMPLETE_NOT_COMPARATIVE'
    cfg['receiver_validation_passed']=True
    write_json(args.output/'receiver.json',cfg)
    write_json(args.output/'SUMMARY.json',dict(results=summary,threshold=threshold,
        inference_sha256=receiver.signature,minimum_utility_passed=True,comparative_validation_complete=False,
        scope=f'One training seed, {counts["evaluation"]} independent evaluation scenes; no comparative or convergence claim'))
    write_json(args.output/'STATUS.json',dict(status='COMPLETE',completed=len(rows),failures=0))
    return 0


if __name__=='__main__':raise SystemExit(main())
