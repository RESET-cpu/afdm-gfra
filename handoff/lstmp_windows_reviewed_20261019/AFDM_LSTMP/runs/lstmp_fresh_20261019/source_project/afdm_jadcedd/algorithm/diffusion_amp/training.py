"""Fresh training of a continuous-noise score prior for residual D-AMP.

Only physical channel training/validation banks enter this routine. Receiver
queries, receiver-test truth, and existing learned checkpoints are not read.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import shutil
import sys
import time
import traceback

import numpy as np
import torch

from afdm_jadcedd.algorithm.baselines.ldamp.representation import Representation, beam_transform
from afdm_jadcedd.algorithm.diffusion_amp.network import BeamScoreDenoiser
from afdm_jadcedd.project import ROOT
from afdm_jadcedd.utils import sha256, write_json


def cpu_state(value):
    if torch.is_tensor(value):
        return value.detach().cpu().clone()
    if isinstance(value, dict):
        return {key: cpu_state(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return type(value)(cpu_state(item) for item in value)
    return value


def selected_beams(bank, indices, beams, scale, representation):
    """Exact fixed unitary transforms, then select one beam per channel."""
    channels = np.asarray(bank[indices]) / scale
    beam = beam_transform(channels)
    transformed = representation.forward(beam[np.arange(len(indices)), beams])
    return np.stack((transformed.real, transformed.imag), axis=1).astype(np.float32)


def make_batch(bank, rng, recipe, representation):
    """Balanced importance sampling with the true 0.1/0.9 mixture weights."""
    batch_size = recipe['batch_size']
    count = batch_size // 2
    indices = rng.integers(len(bank), size=count)
    beams = rng.integers(16, size=count)
    active = selected_beams(bank, indices, beams, recipe['scale'], representation)
    # Independent uniform global phases preserve this physical prior exactly.
    if recipe['phase_augmentation']:
        phase = rng.uniform(-np.pi, np.pi, count)
        z = (active[:, 0] + 1j * active[:, 1]) * np.exp(1j * phase[:, None, None])
        active = np.stack((z.real, z.imag), axis=1).astype(np.float32)
    clean = np.concatenate((active, np.zeros_like(active)), axis=0)
    low, high = recipe['noise_support']
    variance = np.exp(rng.uniform(np.log(low), np.log(high), batch_size)).astype(np.float32)
    noise = rng.standard_normal(clean.shape).astype(np.float32)
    noisy = clean + noise * np.sqrt(variance[:, None, None, None] / 2)
    probability = recipe['activity_probability']
    importance = np.concatenate((np.full(count, 2 * probability),
                                 np.full(count, 2 * (1 - probability)))).astype(np.float32)
    return tuple(torch.from_numpy(value) for value in (noisy, clean, variance, importance))


def validation_channels(bank, count, scale, representation):
    # All sixteen beams; select physical candidates evenly across bank rows.
    indices = np.linspace(0, len(bank) - 1, min(count, len(bank)), dtype=int)
    chunks = []
    for start in range(0, len(indices), 32):
        value = np.asarray(bank[indices[start:start + 32]]) / scale
        transformed = representation.forward(beam_transform(value))
        transformed = transformed.reshape(-1, 16, 16)
        chunks.append(np.stack((transformed.real, transformed.imag), axis=1).astype(np.float32))
    return np.concatenate(chunks), indices


@torch.inference_mode()
def validate(model, clean, recipe, device, *, seed=None):
    """Exact activity-mixture weighting; fixed held-out AWGN per interval."""
    model.eval()
    rng = np.random.default_rng(recipe['validation_seed'] if seed is None else seed)
    boundaries = [.001, .01, .1, 1., 10., 100.]
    metrics = []
    probability = recipe['activity_probability']
    batch_size = recipe['validation_batch_size']
    for low, high in zip(boundaries[:-1], boundaries[1:]):
        active_error = inactive_error = power = objective = coordinates = 0.
        for start in range(0, len(clean), batch_size):
            target = clean[start:start + batch_size]
            variance = np.exp(rng.uniform(np.log(low), np.log(high), len(target))).astype(np.float32)
            noise = rng.standard_normal(target.shape).astype(np.float32)
            noise *= np.sqrt(variance[:, None, None, None] / 2)
            # Paired noise lowers the comparison variance between mixture parts.
            inputs = np.concatenate((target + noise, noise), axis=0)
            variances = np.concatenate((variance, variance))
            prediction = model(torch.from_numpy(inputs).to(device),
                               torch.from_numpy(variances).to(device)).cpu().numpy()
            ea = np.square(prediction[:len(target)].astype(np.float64) - target).mean(axis=(1, 2, 3))
            ei = np.square(prediction[len(target):].astype(np.float64)).mean(axis=(1, 2, 3))
            p = np.square(target.astype(np.float64)).mean(axis=(1, 2, 3))
            weights = 2 / variance.astype(np.float64) + 1 / model.sigma_data ** 2
            active_error += float(ea.sum())
            inactive_error += float(ei.sum())
            power += float(p.sum())
            objective += float((weights * (probability * ea + (1 - probability) * ei)).sum())
            coordinates += len(target)
        weighted_error = probability * active_error + (1 - probability) * inactive_error
        metrics.append(dict(bounds=[low, high], mse_real=weighted_error / coordinates,
            objective=objective / coordinates, zero_mse_real=probability * power / coordinates,
            error_over_zero=weighted_error / (probability * power),
            nmse_db=float(10 * np.log10(weighted_error / (probability * power))),
            active_nmse_db=float(10 * np.log10(active_error / power)),
            inactive_mse_real=inactive_error / coordinates, beam_samples=int(coordinates)))
    return dict(objective=float(np.mean([row['objective'] for row in metrics])),
                mean_mse_real=float(np.mean([row['mse_real'] for row in metrics])),
                mean_error_over_zero=float(np.mean([row['error_over_zero'] for row in metrics])),
                intervals=metrics)


def save_checkpoint(path, model, recipe, step, validation, source_hashes, *, extra=None):
    payload = dict(schema='afdm-continuous-score-checkpoint-v1',
        model=cpu_state(model.state_dict()), network=model.configuration, recipe=recipe,
        step=step, validation=validation, source_sha256=source_hashes,
        initialization='Independent random initialization; no existing weights loaded',
        score_convention='Real score=(denoised_mean-query)/(complex_variance/2)',
        representation='fixed beam DFT and invertible time-lag DFT',
        diffusion_scope='Continuous variance-exploding Gaussian corruption prior; no reverse-time sampler in receiver')
    if extra:
        payload.update(extra)
    temporary = Path(str(path) + '.tmp')
    torch.save(payload, temporary)
    temporary.replace(path)


def run(args):
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    start = time.time()
    try:
        return _run(args, output, start)
    except BaseException as error:
        write_json(output / 'STATUS.json', dict(status='FAILED', elapsed_seconds=time.time() - start,
            error=repr(error), traceback=traceback.format_exc()))
        raise


def _run(args, output, start):
    torch.set_num_threads(1)
    recipe = dict(schema='afdm-continuous-score-training-v1',
        train_path='data/proposed/train_channel.npy', validation_path='data/proposed/validation_channel.npy',
        train_identities='data/proposed/train_identities.npy',
        validation_identities='data/proposed/validation_identities.npy',
        prior_definition='data/proposed/prior_definition.json',
        noise_support=[.001, 100.], activity_probability=.1,
        seed=args.seed, validation_seed=args.validation_seed, batch_size=args.batch_size,
        validation_batch_size=128, validation_users=args.validation_users,
        final_validation_users=args.final_validation_users, phase_augmentation=True,
        maximum_steps=args.steps, minimum_steps=args.minimum_steps,
        validation_interval=args.validation_interval, patience=args.patience,
        learning_rate=args.learning_rate, minimum_learning_rate=1e-5,
        loss='EDM-weighted clean MSE, importance-weighted to activity prior 0.1',
        score_equivalence='lambda_D ||D-x||^2 = lambda_D sigma^4 ||s_theta+(r-x)/sigma^2||^2, sigma^2=v/2',
        checkpoint_selection='Minimum fixed held-out EDM-weighted denoising objective across five log-noise intervals')
    prior = json.loads((ROOT / recipe['prior_definition']).read_text())
    recipe['scale'] = prior['global_complex_rms']
    sigma_data = float(np.sqrt(.1 * prior['normalized_mean_element_power'] / 2))
    network = dict(width=args.width, blocks=args.blocks, embedding=64, fourier_features=16,
                   sigma_data=sigma_data, noise_min=.001, noise_max=100.)
    source_paths = [Path(__file__), Path(__file__).with_name('network.py'),
                    ROOT / 'scripts/train_diffusion_amp.py',
                    ROOT / 'src/afdm_jadcedd/algorithm/baselines/ldamp/representation.py']
    hashes = {str(path.relative_to(ROOT)): sha256(path) for path in source_paths}
    (output / 'sources').mkdir()
    for path in source_paths:
        shutil.copy2(path, output / 'sources' / path.name)
    banks = {split: np.load(ROOT / recipe[split + '_path'], mmap_mode='r')
             for split in ('train', 'validation')}
    data_hashes = {split: sha256(ROOT / recipe[split + '_path']) for split in banks}
    if data_hashes != prior['sample_files_sha256']:
        raise ValueError('Physical bank SHA256 does not match prior definition')
    identities = {split: np.load(ROOT / recipe[split + '_identities']) for split in banks}
    overlap = np.intersect1d(identities['train'][:, 0], identities['validation'][:, 0])
    if len(overlap):
        raise ValueError('Training and validation physical scene identities overlap')
    for split in banks:
        if banks[split].shape[1:] != (16, 16, 16) or len(banks[split]) != len(identities[split]):
            raise ValueError('Expected complete complex 16-antenna channel bank and identities')
    if args.batch_size % 2:
        raise ValueError('Balanced importance sampling requires an even batch size')
    torch.manual_seed(args.seed)
    rng = np.random.default_rng(args.seed)
    model = BeamScoreDenoiser(**network).to(args.device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', patience=3, factor=.5, threshold=.002, min_lr=1e-5)
    representation = Representation()
    validation_clean, validation_indices = validation_channels(
        banks['validation'], args.validation_users, recipe['scale'], representation)
    write_json(output / 'PLAN.json', dict(recipe=recipe, network=network, device=args.device,
        parameters=sum(p.numel() for p in model.parameters()), source_sha256=hashes,
        data_sha256=data_hashes,
        identity_sha256={s: sha256(ROOT / recipe[s + '_identities']) for s in banks},
        train_physical_scenes=int(len(np.unique(identities['train'][:, 0]))),
        validation_physical_scenes=int(len(np.unique(identities['validation'][:, 0]))),
        physical_scene_overlap=0, validation_channel_indices=validation_indices.tolist(),
        initialization='Independent random initialization; no trained weights loaded',
        receiver_test_access=False, maximum_steps=args.steps))
    history, train_log = [], []
    best, best_step, stale = float('inf'), 0, 0
    running_loss = 0.
    validation = None
    for step in range(args.steps + 1):
        if step:
            model.train()
            noisy, clean, variance, importance = [value.to(args.device) for value in
                make_batch(banks['train'], rng, recipe, representation)]
            optimizer.zero_grad(set_to_none=True)
            prediction = model(noisy, variance)
            per_sample = (prediction - clean).square().mean(dim=(1, 2, 3))
            loss = (per_sample * model.loss_weight(variance) * importance).mean()
            if not bool(torch.isfinite(loss)):
                raise FloatingPointError(f'Nonfinite objective at step {step}')
            loss.backward()
            norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 10.)
            if not bool(torch.isfinite(norm)):
                raise FloatingPointError(f'Nonfinite gradient at step {step}')
            optimizer.step()
            running_loss += float(loss.detach().cpu())
            if step % 100 == 0:
                train_log.append(dict(step=step, objective=running_loss / 100,
                    gradient_norm=float(norm.detach().cpu()), elapsed_seconds=time.time() - start))
                running_loss = 0.
                write_json(output / 'TRAINING.json', train_log)
                write_json(output / 'STATUS.json', dict(status='TRAINING', step=step,
                    best_step=best_step, best_validation_objective=best, elapsed_seconds=time.time() - start))
        if step % args.validation_interval == 0 or step == args.steps:
            validation = validate(model, validation_clean, recipe, args.device)
            row = dict(step=step, validation=validation, elapsed_seconds=time.time() - start,
                       learning_rate=optimizer.param_groups[0]['lr'])
            history.append(row)
            improved = validation['objective'] < best
            substantial = validation['objective'] < best * .998
            if improved:
                best, best_step = validation['objective'], step
                save_checkpoint(output / 'best.pt', model, recipe, step, validation, hashes)
            stale = 0 if substantial else stale + 1
            if step:
                scheduler.step(validation['objective'])
            save_checkpoint(output / 'last.pt', model, recipe, step, validation, hashes,
                extra=dict(optimizer=cpu_state(optimizer.state_dict()), scheduler=scheduler.state_dict(),
                           numpy_rng=rng.bit_generator.state, torch_rng=torch.get_rng_state()))
            write_json(output / 'HISTORY.json', history)
            print(json.dumps(dict(step=step, objective=validation['objective'], best_step=best_step,
                interval_nmse_db=[round(item['nmse_db'], 4) for item in validation['intervals']],
                elapsed_seconds=round(time.time() - start, 2), stale=stale)), flush=True)
            if step >= args.minimum_steps and stale >= args.patience:
                break
    # Final report evaluates the selected checkpoint on a larger held-out set.
    payload = torch.load(output / 'best.pt', map_location='cpu', weights_only=True)
    model.load_state_dict(payload['model'])
    final_clean, final_indices = validation_channels(
        banks['validation'], args.final_validation_users, recipe['scale'], representation)
    final = validate(model, final_clean, recipe, args.device, seed=args.validation_seed + 1)
    write_json(output / 'VALIDATION.json', dict(validation=final,
        channel_indices=final_indices.tolist(), source='held-out physical validation bank',
        selection_data_overlap='Validation subset may overlap selection subset; no test claims',
        active_probability=.1, all_beams=True, noise_seed=args.validation_seed + 1))
    manifest = dict(schema='afdm-continuous-score-bank-v1', checkpoint=str(output / 'best.pt'),
        checkpoint_sha256=sha256(output / 'best.pt'), scale=recipe['scale'],
        noise_support=recipe['noise_support'], network=network,
        representation='beam_time_lag_dft', input_shape=[2, 16, 16],
        activity_probability=.1, score_convention='real, sigma^2=complex_variance/2',
        best_step=best_step, final_validation=final, trained_from_scratch=True,
        source_sha256=hashes, data_sha256=data_hashes)
    write_json(output / 'MODEL.json', manifest)
    write_json(output / 'STATUS.json', dict(status='COMPLETE', completed_steps=step,
        best_step=best_step, best_validation_objective=best, early_stopped=step < args.steps,
        validation_plateau_observed=stale >= args.patience,
        elapsed_seconds=time.time() - start, receiver_validated=False,
        checkpoint_sha256=manifest['checkpoint_sha256']))
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--device', choices=['cpu', 'mps'], default='mps')
    parser.add_argument('--steps', type=int, default=10000)
    parser.add_argument('--minimum-steps', type=int, default=5000)
    parser.add_argument('--patience', type=int, default=8)
    parser.add_argument('--validation-interval', type=int, default=500)
    parser.add_argument('--validation-users', type=int, default=96)
    parser.add_argument('--final-validation-users', type=int, default=512)
    parser.add_argument('--batch-size', type=int, default=64)
    parser.add_argument('--width', type=int, default=48)
    parser.add_argument('--blocks', type=int, default=4)
    parser.add_argument('--learning-rate', type=float, default=3e-4)
    parser.add_argument('--seed', type=int, default=202610157001)
    parser.add_argument('--validation-seed', type=int, default=202610157002)
    args = parser.parse_args()
    run(args)


if __name__ == '__main__':
    main()
