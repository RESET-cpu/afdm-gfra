"""From-scratch joint-user conditional denoising and density-ratio training.

The loss is active conditional EDM-weighted MSE plus balanced binary cross
entropy. It is not a mixed-prior DSM loss. At the unrestricted population
optimum the heads identify F and the likelihood ratio separately, and pF is
the mixed-prior posterior mean. Finite heads need not satisfy F=T grad(ell).
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import platform
import shutil
import time
import traceback

import numpy as np
import torch
from torch.nn import functional as functional

from afdm_jadcedd.algorithm.baselines.ldamp.representation import Representation, beam_transform
from afdm_jadcedd.algorithm.joint_amp.network import JointScoreNetwork, load_checkpoint
from afdm_jadcedd.project import ROOT
from afdm_jadcedd.utils import sha256, write_json


def utc():
    return datetime.now(timezone.utc).isoformat()


def cpu_state(value):
    if torch.is_tensor(value):
        return value.detach().cpu().clone()
    if isinstance(value, dict):
        return {key: cpu_state(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return type(value)(cpu_state(item) for item in value)
    return value


def transform_channels(bank, indices, scale, representation):
    transformed = representation.forward(beam_transform(np.asarray(bank[indices]) / scale))
    return np.stack((transformed.real, transformed.imag), axis=1).astype(np.float32)


def prepare_bank(bank, path, scale):
    """Derived cache only; immutable physical banks remain unchanged."""
    result = np.lib.format.open_memmap(path, mode='w+', dtype=np.float32,
                                     shape=(len(bank), 2, 16, 16, 16))
    representation = Representation()
    for start in range(0, len(bank), 256):
        stop = min(start + 256, len(bank))
        result[start:stop] = transform_channels(bank, np.arange(start, stop), scale, representation)
    result.flush()
    return np.load(path, mmap_mode='r')


def noise_variance(rng, count, *, mode='training', bounds=(.001, 100.)):
    """50% common, 25% independent, 25% one-decade spread; fixed before validation."""
    lower, upper = np.log(bounds)
    if mode == 'independent':
        value = rng.uniform(lower, upper, (count, 16))
    else:
        center = rng.uniform(lower, upper, (count, 1))
        value = np.repeat(center, 16, axis=1)
        if mode == 'spread':
            value += rng.uniform(-math.log(10) / 2, math.log(10) / 2, value.shape)
        elif mode == 'training':
            choice = rng.random(count)
            independent = (choice >= .5) & (choice < .75)
            spread = choice >= .75
            value[independent] = rng.uniform(lower, upper, (independent.sum(), 16))
            value[spread] += rng.uniform(-math.log(10) / 2, math.log(10) / 2, (spread.sum(), 16))
        elif mode != 'common':
            raise ValueError('Unknown variance sampling mode')
    return np.exp(np.clip(value, math.log(.001), math.log(100))).astype(np.float32)


def make_batch(bank, rng, recipe):
    count = recipe['active_batch_size']
    indices = rng.integers(len(bank), size=count)
    active = np.array(bank[indices], copy=True)
    if recipe['phase_augmentation']:
        phase = rng.uniform(-np.pi, np.pi, (count, 1, 1, 1))
        real, imag = active[:, 0].copy(), active[:, 1].copy()
        active[:, 0] = real * np.cos(phase) - imag * np.sin(phase)
        active[:, 1] = real * np.sin(phase) + imag * np.cos(phase)
    clean = np.concatenate((active, np.zeros_like(active)))
    # Exactly matched V per class prevents class information in the conditioning.
    variance = noise_variance(rng, count)
    variance = np.concatenate((variance, variance))
    noise = rng.standard_normal(clean.shape, dtype=np.float32)
    noisy = clean + noise * np.sqrt(variance[:, None, :, None, None] / 2)
    labels = np.concatenate((np.ones(count), np.zeros(count))).astype(np.float32)
    return tuple(torch.from_numpy(value) for value in (noisy, clean, variance, labels))


def objective(model, noisy, clean, variance, labels):
    components = model.components(noisy, variance, .5)
    active = labels > .5
    error = (components['conditional_mean'][active] - clean[active]).square().mean(dim=(1, 3, 4))
    denoising = (error * model.loss_weight(variance[active])).mean()
    classification = functional.binary_cross_entropy_with_logits(components['log_likelihood_ratio'], labels)
    return denoising + classification, denoising, classification


def validation_strata():
    bounds = [.001, .01, .1, 1., 10., 100.]
    rows = [dict(mode=mode, bounds=[low, high], weight=weight)
            for mode, weight in [('common', .1), ('spread', .05)]
            for low, high in zip(bounds[:-1], bounds[1:])]
    rows.append(dict(mode='independent', bounds=[.001, 100.], weight=.25))
    return rows


@torch.inference_mode()
def validate(model, clean, recipe, device, *, seed=None):
    model.eval()
    rng = np.random.default_rng(recipe['validation_seed'] if seed is None else seed)
    rho = recipe['activity_probability']
    metrics = []
    for stratum in validation_strata():
        totals = dict(active_mse=0., inactive_mse=0., conditional_active_mse=0.,
            active_power=0., weighted_risk=0., balanced_bce=0., mixture_bce=0.,
            brier=0., miss=0., false_alarm=0., linear_mse=0., count=0)
        for start in range(0, len(clean), recipe['validation_batch_size']):
            target = np.asarray(clean[start:start + recipe['validation_batch_size']])
            count = len(target)
            variance = noise_variance(rng, count, mode=stratum['mode'], bounds=stratum['bounds'])
            noise = rng.standard_normal(target.shape, dtype=np.float32)
            noise *= np.sqrt(variance[:, None, :, None, None] / 2)
            inputs = np.concatenate((target + noise, noise))
            variances = np.concatenate((variance, variance))
            result = model.components(torch.from_numpy(inputs).to(device),
                torch.from_numpy(variances).to(device), rho)
            result = {key: value.cpu().numpy().astype(np.float64) for key, value in result.items()}
            target64 = target.astype(np.float64)
            ea = ((result['mean'][:count] - target64) ** 2).mean(axis=(1, 3, 4))
            ei = (result['mean'][count:] ** 2).mean(axis=(1, 3, 4))
            ef = ((result['conditional_mean'][:count] - target64) ** 2).mean(axis=(1, 3, 4))
            power = (target64 ** 2).mean(axis=(1, 3, 4))
            weight = 2 / variance.astype(np.float64) + 1 / model.sigma_data ** 2
            logratio = result['log_likelihood_ratio']
            logodds = logratio + math.log(rho / (1 - rho))
            probability = result['probability']
            linear_gain = rho * model.sigma_data ** 2 / (variance / 2 + rho * model.sigma_data ** 2)
            linear_a = (target64 + noise) * linear_gain[:, None, :, None, None]
            linear_i = noise * linear_gain[:, None, :, None, None]
            totals['active_mse'] += float(ea.mean(axis=1).sum())
            totals['inactive_mse'] += float(ei.mean(axis=1).sum())
            totals['conditional_active_mse'] += float(ef.mean(axis=1).sum())
            totals['active_power'] += float(power.mean(axis=1).sum())
            totals['weighted_risk'] += float(((rho * ea + (1 - rho) * ei) * weight).mean(axis=1).sum())
            totals['balanced_bce'] += float((np.logaddexp(0., -logratio[:count])
                                             + np.logaddexp(0., logratio[count:])).sum() / 2)
            totals['mixture_bce'] += float((rho * np.logaddexp(0., -logodds[:count])
                                           + (1 - rho) * np.logaddexp(0., logodds[count:])).sum())
            totals['brier'] += float((rho * (1 - probability[:count]) ** 2
                                     + (1 - rho) * probability[count:] ** 2).sum())
            totals['miss'] += int((probability[:count] < .5).sum())
            totals['false_alarm'] += int((probability[count:] >= .5).sum())
            totals['linear_mse'] += float((rho * ((linear_a - target64) ** 2).mean(axis=(1, 2, 3, 4))
                + (1 - rho) * (linear_i ** 2).mean(axis=(1, 2, 3, 4))).sum())
            totals['count'] += count
        count = totals.pop('count')
        row = {key: value / count for key, value in totals.items()}
        row['mixture_mse'] = rho * row['active_mse'] + (1 - rho) * row['inactive_mse']
        row['zero_mse'] = rho * row['active_power']
        row['nmse_db'] = float(10 * np.log10(row['mixture_mse'] / row['zero_mse']))
        row['active_nmse_db'] = float(10 * np.log10(row['active_mse'] / row['active_power']))
        row['conditional_active_nmse_db'] = float(10 * np.log10(row['conditional_active_mse'] / row['active_power']))
        row['linear_nmse_db'] = float(10 * np.log10(row['linear_mse'] / row['zero_mse']))
        row['aer'] = rho * row['miss'] + (1 - rho) * row['false_alarm']
        metrics.append(dict(**stratum, users=count, **row))
    summary = {key: float(sum(row['weight'] * row[key] for row in metrics))
               for key in ['weighted_risk', 'active_mse', 'inactive_mse', 'conditional_active_mse',
                           'mixture_mse', 'zero_mse', 'active_power', 'balanced_bce',
                           'mixture_bce', 'brier', 'miss', 'false_alarm', 'aer', 'linear_mse']}
    summary['nmse_db'] = float(10 * np.log10(summary['mixture_mse'] / summary['zero_mse']))
    summary['active_nmse_db'] = float(10 * np.log10(summary['active_mse'] / summary['active_power']))
    summary['linear_nmse_db'] = float(10 * np.log10(summary['linear_mse'] / summary['zero_mse']))
    return dict(summary=summary, strata=metrics, activity_probability=rho,
                pairs_per_stratum=len(clean), all_beams=True)


def save_checkpoint(path, model, recipe, step, validation, hashes, extra=None):
    payload = dict(schema='afdm-joint-score-checkpoint-v1', state_dict=cpu_state(model.state_dict()),
        network=model.configuration, recipe=recipe, step=step, validation=validation,
        source_sha256=hashes, created_utc=utc(), initialization='random; no existing learned weights loaded',
        score_convention='real score=(p F-r)/(complex_variance/2), per beam',
        training_objective='active conditional EDM-weighted MSE + equally weighted balanced BCE',
        limitations='Two finite heads are not constrained to satisfy F=T grad(log_likelihood_ratio)')
    if extra:
        payload.update(extra)
    temporary = Path(str(path) + '.tmp')
    torch.save(payload, temporary)
    temporary.replace(path)


def consistency_diagnostics(model, clean, device):
    """Descriptive consistency check, not a post-hoc checkpoint rejection rule."""
    records = []
    for value in [.001, .01, .1, 1., 10., 100.]:
        generator = torch.Generator().manual_seed(202610159023 + int(value * 1000))
        target = torch.from_numpy(np.array(clean[:4], copy=True))
        variance = torch.full((len(target), 16), value)
        noisy = (target + torch.randn(target.shape, generator=generator) * math.sqrt(value / 2)).to(device)
        noisy.requires_grad_(True)
        result = model.components(noisy, variance.to(device), .1)
        gradient, = torch.autograd.grad(result['log_likelihood_ratio'].sum(), noisy)
        mean = result['conditional_mean'].detach()
        discrepancy = mean - value / 2 * gradient
        records.append(dict(complex_variance=value,
            relative_norm=(discrepancy.flatten(1).norm(dim=1) / mean.flatten(1).norm(dim=1).clamp_min(1e-20)).cpu().tolist(),
            conditional_mean_norm=mean.flatten(1).norm(dim=1).cpu().tolist(),
            scaled_logratio_gradient_norm=(value / 2 * gradient).flatten(1).norm(dim=1).cpu().tolist()))
    return dict(identity='F=T grad_r ell at unrestricted consistent population optimum',
                criterion='descriptive; not used for model selection', samples=4, records=records)


def run(args):
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    start = time.time()
    write_json(output / 'PROCESS.json', dict(pid=os.getpid(), started_utc=utc(),
        timeout_seconds=args.timeout_seconds, command_args=vars(args) | {'output': str(args.output)},
        experiment_type='training', alive=True))
    try:
        return _run(args, output, start)
    except BaseException as error:
        write_json(output / 'STATUS.json', dict(status='FAILED', pid=os.getpid(), alive=False,
            error=repr(error), elapsed_seconds=time.time() - start, completed_utc=utc(),
            traceback=traceback.format_exc()))
        raise


def _run(args, output, start):
    torch.set_num_threads(1)
    torch.manual_seed(args.seed)
    rng = np.random.default_rng(args.seed)
    recipe = dict(schema='afdm-joint-score-training-v1', scale=None, noise_support=[.001, 100.],
        activity_probability=.1, train_path='data/proposed/train_channel.npy',
        validation_path='data/proposed/validation_channel.npy',
        train_identities='data/proposed/train_identities.npy',
        validation_identities='data/proposed/validation_identities.npy',
        prior_definition='data/proposed/prior_definition.json',
        seed=args.seed, validation_seed=args.validation_seed, active_batch_size=args.active_batch_size,
        inactive_batch_size=args.active_batch_size, validation_batch_size=32,
        phase_augmentation=True, variance_sampling={'common': .5, 'independent': .25, 'spread_one_decade': .25},
        variance_class_matching='Exactly the same per-user V values for balanced active/inactive classes',
        noise_class_matching='Independent train noise; paired validation noise',
        loss='active-only EDM-weighted MSE plus balanced BCE; both terms coefficient one',
        loss_scope='Not a mixed DSM objective; two ideal heads imply the mixed posterior mean pF',
        conditional_DSM_weight='For each real coordinate tau=v/2: lambda_score=tau^2/c_out^2',
        rho_scope='Only public-prior correction at inference; not a classifier training condition',
        representation='fixed beam DFT then invertible time-lag DFT', input_shape=[2, 16, 16, 16],
        maximum_steps=args.steps, minimum_steps=args.minimum_steps, patience=args.patience,
        validation_interval=args.validation_interval, validation_users=args.validation_users,
        final_validation_users=args.final_validation_users, learning_rate=args.learning_rate,
        validation_strata=validation_strata(),
        checkpoint_selection='Minimum fixed validation mixture EDM-weighted risk, rho=.1, declared stratum weights',
        plateau_criterion='No relative weighted-risk improvement >=0.2% for patience validation checks after minimum steps')
    prior = json.loads((ROOT / recipe['prior_definition']).read_text())
    recipe['scale'] = prior['global_complex_rms']
    q = prior['normalized_mean_element_power'] / 2
    network = dict(width=args.width, blocks=args.blocks, embedding=128, fourier_features=8,
                   sigma_data=math.sqrt(q), noise_min=.001, noise_max=100.)
    source_paths = [Path(__file__), Path(__file__).with_name('network.py'),
        ROOT / 'scripts/train_joint_amp.py', ROOT / 'src/afdm_jadcedd/algorithm/baselines/ldamp/representation.py',
        ROOT / 'experiments/joint_amp_20261015/training/METHOD.md',
        ROOT / 'experiments/joint_amp_20261015/training/smoke.py']
    hashes = {str(path.relative_to(ROOT)): sha256(path) for path in source_paths}
    (output / 'sources').mkdir()
    for path in source_paths:
        shutil.copy2(path, output / 'sources' / path.name)
    banks = {split: np.load(ROOT / recipe[split + '_path'], mmap_mode='r') for split in ['train', 'validation']}
    data_hashes = {split: sha256(ROOT / recipe[split + '_path']) for split in banks}
    if data_hashes != prior['sample_files_sha256']:
        raise ValueError('Physical bank hashes differ from the prior definition')
    identities = {split: np.load(ROOT / recipe[split + '_identities']) for split in banks}
    if len(np.intersect1d(identities['train'][:, 0], identities['validation'][:, 0])):
        raise ValueError('Physical scene identity overlap')
    for split in banks:
        if banks[split].shape[1:] != (16, 16, 16) or len(banks[split]) != len(identities[split]):
            raise ValueError('Unexpected physical bank shape or identity count')
    model = JointScoreNetwork(**network).to(args.device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=.5,
        patience=4, threshold=.002, min_lr=1e-5)
    indices = np.linspace(0, len(banks['validation']) - 1, args.validation_users, dtype=int)
    final_indices = np.linspace(0, len(banks['validation']) - 1, args.final_validation_users, dtype=int)
    representation = Representation()
    validation_clean = transform_channels(banks['validation'], indices, recipe['scale'], representation)
    final_clean = transform_channels(banks['validation'], final_indices, recipe['scale'], representation)
    write_json(output / 'PLAN.json', dict(recipe=recipe, network=network, source_sha256=hashes,
        data_sha256=data_hashes, identity_sha256={s: sha256(ROOT / recipe[s + '_identities']) for s in banks},
        train_physical_scenes=int(len(np.unique(identities['train'][:, 0]))),
        validation_physical_scenes=int(len(np.unique(identities['validation'][:, 0]))),
        physical_scene_overlap=0, selection_indices=indices.tolist(), final_indices=final_indices.tolist(),
        receiver_test_access=False, old_checkpoint_access=False, device=args.device,
        parameters=sum(p.numel() for p in model.parameters()), pid=os.getpid(), started_utc=utc()))
    write_json(output / 'ENVIRONMENT.json', dict(python=platform.python_version(), platform=platform.platform(),
        numpy=np.__version__, torch=str(torch.__version__), mps_available=torch.backends.mps.is_available()))
    write_json(output / 'STATUS.json', dict(status='PREPARING', pid=os.getpid(), alive=True, elapsed_seconds=time.time() - start))
    derived = prepare_bank(banks['train'], output / 'train_coefficients.npy', recipe['scale'])
    write_json(output / 'CACHE.json', dict(path='train_coefficients.npy', sha256=sha256(output / 'train_coefficients.npy'),
        source_sha256=data_hashes['train'], scale=recipe['scale'], shape=list(derived.shape), dtype=str(derived.dtype)))
    history, train_log = [], []
    best, best_step, stale = float('inf'), 0, 0
    running = np.zeros(3)
    train_start = time.time()
    for step in range(args.steps + 1):
        if time.time() - start > args.timeout_seconds:
            raise TimeoutError(f'Predeclared hard timeout {args.timeout_seconds}s reached')
        if step:
            model.train()
            noisy, clean, variance, labels = [item.to(args.device) for item in make_batch(derived, rng, recipe)]
            optimizer.zero_grad(set_to_none=True)
            total, denoising, classification = objective(model, noisy, clean, variance, labels)
            if not bool(torch.isfinite(total)):
                raise FloatingPointError(f'Nonfinite loss at step {step}')
            total.backward()
            norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 10.)
            if not bool(torch.isfinite(norm)):
                raise FloatingPointError(f'Nonfinite gradient at step {step}')
            optimizer.step()
            running += [float(item.detach().cpu()) for item in [total, denoising, classification]]
            if step % 100 == 0:
                train_log.append(dict(step=step, total=running[0] / 100, denoising=running[1] / 100,
                    bce=running[2] / 100, gradient_norm=float(norm.detach().cpu()),
                    elapsed_seconds=time.time() - start, steps_per_second=step / (time.time() - train_start)))
                running[:] = 0
                write_json(output / 'TRAINING.json', train_log)
                write_json(output / 'STATUS.json', dict(status='TRAINING', step=step, pid=os.getpid(), alive=True,
                    best_step=best_step, best_risk=best, elapsed_seconds=time.time() - start,
                    last_heartbeat_utc=utc(), estimated_training_seconds=args.steps * (time.time() - train_start) / step))
        if step % args.validation_interval == 0 or step == args.steps:
            validation = validate(model, validation_clean, recipe, args.device)
            risk = validation['summary']['weighted_risk']
            if not np.isfinite(risk):
                raise FloatingPointError('Nonfinite validation metric')
            substantial = risk < best * .998
            if risk < best:
                best, best_step = risk, step
                save_checkpoint(output / 'best.pt', model, recipe, step, validation, hashes)
            stale = 0 if substantial else stale + 1
            if step:
                scheduler.step(risk)
            extra = dict(optimizer=cpu_state(optimizer.state_dict()), scheduler=scheduler.state_dict(),
                numpy_rng=rng.bit_generator.state, torch_rng=torch.get_rng_state())
            save_checkpoint(output / 'last.pt', model, recipe, step, validation, hashes, extra)
            row = dict(step=step, validation=validation, elapsed_seconds=time.time() - start,
                learning_rate=optimizer.param_groups[0]['lr'], stale=stale, best_step=best_step)
            history.append(row)
            write_json(output / 'HISTORY.json', history)
            if step in [10000, 30000, 63000, args.steps]:
                shutil.copy2(output / 'best.pt', output / f'best_through_{step:05d}.pt')
                shutil.copy2(output / 'last.pt', output / f'step_{step:05d}.pt')
            print(json.dumps(dict(step=step, **validation['summary'], best_step=best_step, stale=stale,
                elapsed_seconds=round(time.time() - start, 2))), flush=True)
            if step >= args.minimum_steps and stale >= args.patience:
                break
    selected, payload = load_checkpoint(output / 'best.pt', args.device)
    final = validate(selected, final_clean, recipe, args.device, seed=args.validation_seed + 1)
    diagnostic = consistency_diagnostics(selected, final_clean, args.device)
    write_json(output / 'CONSISTENCY.json', diagnostic)
    write_json(output / 'VALIDATION.json', dict(validation=final, channel_indices=final_indices.tolist(),
        source='held-out physical validation bank', noise_seed=args.validation_seed + 1,
        selection_data_overlap='Bank is shared with model selection; no test claim'))
    manifest = dict(schema='afdm-joint-score-model-v1', checkpoint=str(output / 'best.pt'),
        checkpoint_sha256=sha256(output / 'best.pt'), network=network, recipe=recipe,
        scale=recipe['scale'], noise_support=recipe['noise_support'], best_step=best_step,
        completed_steps=step, final_validation=final, trained_from_scratch=True,
        source_sha256=hashes, data_sha256=data_hashes, receiver_validated=False)
    write_json(output / 'MODEL.json', manifest)
    write_json(output / 'STATUS.json', dict(status='COMPLETE', pid=os.getpid(), alive=False,
        completed_steps=step, best_step=best_step, best_risk=best, early_stopped=step < args.steps,
        validation_plateau_observed=stale >= args.patience, elapsed_seconds=time.time() - start,
        completed_utc=utc(), checkpoint_sha256=manifest['checkpoint_sha256']))
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--device', choices=['cpu', 'mps'], default='mps')
    parser.add_argument('--steps', type=int, default=63342)
    parser.add_argument('--minimum-steps', type=int, default=30000)
    parser.add_argument('--patience', type=int, default=10)
    parser.add_argument('--validation-interval', type=int, default=1000)
    parser.add_argument('--validation-users', type=int, default=96)
    parser.add_argument('--final-validation-users', type=int, default=512)
    parser.add_argument('--active-batch-size', type=int, default=64)
    parser.add_argument('--width', type=int, default=96)
    parser.add_argument('--blocks', type=int, default=4)
    parser.add_argument('--learning-rate', type=float, default=3e-4)
    parser.add_argument('--seed', type=int, default=202610159001)
    parser.add_argument('--validation-seed', type=int, default=202610159002)
    parser.add_argument('--timeout-seconds', type=int, default=14400)
    run(parser.parse_args())


if __name__ == '__main__':
    main()
