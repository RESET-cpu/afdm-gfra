"""Explicit standalone commands; default plan never launches training.

Run from the repository root with PYTHONPATH=src and python -m
training.colored_score_20261024.run plan|smoke|train|evaluate ... .
"""
import argparse
from dataclasses import asdict
import json
from pathlib import Path

import numpy as np
import torch

from project import ROOT, repository_path
from utils import sha256, write_json
from networks.score import DirectCaiConfig, DirectCaiNetwork, load_direct_checkpoint
from .model import ColoredScore
from .noise import Covariance, sample_covariance, corrupt, pack, score_loss, posterior_mean

DEFAULT = ROOT/'src/configs/training/colored_score_20261024.json'
OUTPUT = ROOT/'result/channel_denoising/data/colored_score_single_family_20261024'


def assets(config):
    binding = json.loads(repository_path(config['base_config']).read_text(encoding='utf-8'))
    prior_path = repository_path(binding['prior_definition'])
    if sha256(prior_path) != binding['prior_definition_sha256']:
        raise ValueError('Frozen prior hash changed')
    prior = json.loads(prior_path.read_text(encoding='utf-8'))
    checkpoint = repository_path(binding['first_checkpoint'])
    if sha256(checkpoint) != binding['first_checkpoint_sha256']:
        raise ValueError('Frozen first-score hash changed')
    paths = {s: repository_path(prior['data_files'][s]) for s in ('train', 'validation')}
    ids = {s: repository_path(prior['dataset_identities'][s]['identities_path']) for s in paths}
    records = {}
    for s in paths:
        for p, expected in ((paths[s], prior['sample_files_sha256'][s]),
                            (ids[s], prior['dataset_identities'][s]['identities_sha256'])):
            actual = sha256(p)
            if actual != expected:
                raise ValueError('Dataset hash changed: '+str(p))
            records[str(p.relative_to(ROOT))] = actual
    identities = {s: np.load(ids[s], allow_pickle=False) for s in ids}
    if np.intersect1d(identities['train'][:, 0], identities['validation'][:, 0]).size:
        raise ValueError('Train/validation scenes overlap')
    _, rows = np.unique(identities['validation'][:, 0], return_index=True)
    rows = rows[:config['evaluation_scenes']]
    if len(rows) != 1000:
        raise ValueError('This candidate evaluation requires 1000 distinct scenes')
    return binding, checkpoint, paths, identities, rows, records


def clean_batch(bank, rows, scale, device):
    return pack(torch.as_tensor(np.array(bank[rows], copy=True), device=device))/scale


def white_cov(c):
    return Covariance(c.variance,
        torch.eye(c.antenna.shape[-1], device=c.antenna.device, dtype=c.antenna.dtype).expand_as(c.antenna),
        torch.eye(c.column.shape[-1], device=c.column.device, dtype=c.column.dtype).expand_as(c.column))


def save_model(path, model, config, arm, steps, base_hash):
    torch.save(dict(schema='colored-first-score-candidate-v2', architecture=asdict(model.config),
        state_dict={k: v.detach().cpu() for k, v in model.state_dict().items()},
        recipe=config, arm=arm, optimizer_steps=steps, base_sha256=base_hash), path)


def load_model(path, device):
    blob = torch.load(path, map_location='cpu', weights_only=False)
    if blob['schema'] != 'colored-first-score-candidate-v2':
        raise ValueError('Independent colored-score checkpoint required')
    model = ColoredScore(DirectCaiNetwork(DirectCaiConfig(**blob['architecture'])))
    model.load_state_dict(blob['state_dict'], strict=True)
    return model.to(device).eval(), blob


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('command', choices=('plan', 'smoke', 'train', 'evaluate'))
    parser.add_argument('--config', type=Path, default=DEFAULT)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--arm', choices=('colored', 'white'), default='colored')
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding='utf-8'))
    if config['schema'] != 'colored-first-score-candidate-v2':
        raise ValueError('Use the single-family v2 recipe; preserve original v1 records')
    output = args.output.resolve()
    allowed = (ROOT/'result/channel_denoising/data').resolve()
    if not output.is_relative_to(allowed) or output == allowed:
        raise ValueError('Use a dedicated candidate output under channel_denoising/data')
    output.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(2)
    torch.manual_seed(config['seed'])
    binding, checkpoint, paths, ids, rows, records = assets(config)
    base_hash = sha256(checkpoint)
    if args.command == 'plan':
        sources = {str(p.relative_to(ROOT)): sha256(p) for p in Path(__file__).parent.glob('*.py')}
        write_json(output/'PLAN.json', dict(status='PREPARED_NOT_TRAINED', recipe=config,
            base_checkpoint=str(checkpoint.relative_to(ROOT)), base_sha256=base_hash,
            source_hashes=sources, data_hashes=records,
            evaluation_scene_ids=list(range(1000)), validation_rows=rows.tolist(),
            validation_identities=ids['validation'][rows].tolist(),
            arms=['frozen_white', 'continued_white', 'colored'],
            evaluation_note=config['evaluation_scope']))
        print('Prepared plan: 50000 clean training channels reused; 1000 distinct development scenes.')
        return
    rng = np.random.default_rng(config['seed'])
    base, blob = load_direct_checkpoint(checkpoint, args.device)
    if blob['global_complex_rms'] != binding['scale'] or blob['order'] != 1:
        raise ValueError('Warm start scale/order mismatch')
    bank = np.load(paths['train'], mmap_mode='r', allow_pickle=False)
    if args.command == 'smoke':
        model = ColoredScore(base).to(args.device)
        clean = clean_batch(bank, [0], binding['scale'], args.device)
        c = sample_covariance(rng, 1, max_strength=0., snr_db=(0., 0.))
        c = c.to(args.device)
        noisy = corrupt(clean, c, rng)
        with torch.no_grad():
            old, new = base(noisy, c.variance), model(noisy, c)
        torch.testing.assert_close(old, new, atol=3e-5, rtol=3e-5)
        c = sample_covariance(rng, 1, snr_db=(0., 0.),
                                 max_strength=config['noise']['max_strength'], rank=config['noise']['rank'])
        c = c.to(args.device)
        noisy = corrupt(clean, c, rng)
        optimizer = torch.optim.Adam(model.parameters(), lr=config['learning_rate'])
        loss = score_loss(model(noisy, c), noisy, clean, c)
        loss.backward()
        gradient = model.backbone.condition[0].weight.grad[:, 1:]
        assert torch.isfinite(gradient).all() and gradient.norm() > 0
        assert all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters())
        optimizer.step()
        with torch.no_grad():
            after = score_loss(model(noisy, c), noisy, clean, c)
        assert torch.isfinite(after)
        write_json(output/'SMOKE.json', dict(status='PASS', device=args.device,
            base_sha256=base_hash, awgn_max_abs_difference=float((old-new).abs().max()),
            loss_before=float(loss.detach()), loss_after=float(after),
            covariance_condition_gradient_norm=float(gradient.norm()),
            optimizer_steps=1, checkpoint_saved=False,
            scope='One real training channel; pipeline check only, not a performance experiment'))
        print('PASS: frozen checkpoint AWGN equivalence and one colored-noise optimizer step.')
        return
    if args.command == 'train':
        destination = output/args.arm
        destination.mkdir(exist_ok=False)
        write_json(destination/'recipe.json', config)
        write_json(destination/'provenance.json', dict(base_sha256=base_hash, data_hashes=records,
            source_hashes={str(p.relative_to(ROOT)): sha256(p) for p in Path(__file__).parent.glob('*.py')}))
        model = ColoredScore(base).to(args.device).train()
        optimizer = torch.optim.Adam(model.parameters(), lr=config['learning_rate'])
        # Separate RNGs ensure the two arms receive identical channel row order.
        row_rng = np.random.default_rng(config['seed']+1)
        losses = []
        for step in range(config['pilot_steps']):
            batch_rows = row_rng.integers(0, len(bank), config['batch_size'])
            clean = clean_batch(bank, batch_rows, binding['scale'], args.device)
            c = sample_covariance(rng, len(clean), **config['noise'])
            c = c.to(args.device)
            if args.arm == 'white':
                c = white_cov(c)
            noisy = corrupt(clean, c, rng)
            optimizer.zero_grad(set_to_none=True)
            loss = score_loss(model(noisy, c), noisy, clean, c)
            if not bool(torch.isfinite(loss)):
                raise FloatingPointError('Nonfinite loss; all completed losses retained in training.jsonl')
            loss.backward()
            if not all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters()):
                raise FloatingPointError('Nonfinite gradient')
            optimizer.step()
            losses.append(float(loss.detach()))
            with (destination/'training.jsonl').open('a', encoding='utf-8') as stream:
                stream.write(json.dumps(dict(step=step+1, loss=losses[-1]))+'\n')
            if (step+1) % 100 == 0:
                print(json.dumps(dict(arm=args.arm, step=step+1, loss=losses[-1])), flush=True)
        save_model(destination/'last.pt', model, config, args.arm, len(losses), base_hash)
        write_json(destination/'COMPLETE.json', dict(status='COMPLETED_FIXED_BUDGET_PILOT',
            optimizer_steps=len(losses), checkpoint_sha256=sha256(destination/'last.pt'),
            mean_loss=float(np.mean(losses)), selection='Final step, no validation selection'))
        return
    models = {}
    for arm in ('white', 'colored'):
        models[arm], candidate = load_model(output/arm/'last.pt', args.device)
        if (candidate['recipe'] != config or candidate['optimizer_steps'] != config['pilot_steps']
                or candidate['base_sha256'] != base_hash or candidate['arm'] != arm):
            raise ValueError('Paired pilot recipe/budget/initialization differs')
    validation = np.load(paths['validation'], mmap_mode='r', allow_pickle=False)
    result_path = output/'DENOISING.npz'
    if result_path.exists():
        raise FileExistsError('Evaluation exists; preserve it and use a new candidate output')
    errors = np.empty((len(config['evaluation_snr_db']), 1000, 3), dtype=np.float64)
    input_errors = np.empty(errors.shape[:-1], dtype=np.float64)
    signal = np.empty(1000, dtype=np.float64)
    with torch.no_grad():
        for si, snr in enumerate(config['evaluation_snr_db']):
            # Fixed per-scene RNG makes observations invariant to microbatch size.
            for scene_id, row in enumerate(rows):
                gen = np.random.default_rng(np.random.SeedSequence(
                    [config['validation_seed'], si, scene_id]))
                clean = clean_batch(validation, [row], binding['scale'], args.device)
                c = sample_covariance(gen, 1, snr_db=(snr, snr),
                    max_strength=config['noise']['max_strength'], rank=config['noise']['rank'])
                c = c.to(args.device)
                noisy = corrupt(clean, c, gen)
                white = white_cov(c)
                estimates = [posterior_mean(noisy, base(noisy, c.variance), white),
                    posterior_mean(noisy, models['white'](noisy, white), white),
                    posterior_mean(noisy, models['colored'](noisy, c), c)]
                signal[scene_id] = float(clean.square().sum())
                input_errors[si, scene_id] = float((noisy-clean).square().sum())
                for j, estimate in enumerate(estimates):
                    errors[si, scene_id, j] = float((estimate-clean).square().sum())
            print(json.dumps(dict(snr_db=snr, scenes=1000)), flush=True)
    np.savez(result_path, errors=errors, input_errors=input_errors, signal=signal,
             scene_ids=np.arange(1000), identities=ids['validation'][rows])
    write_json(output/'DENOISING_SUMMARY.json', dict(status='ANALYZED',
        methods=['frozen_white', 'continued_white', 'colored'],
        noise_family=config['noise_family'], snr_db=config['evaluation_snr_db'],
        nmse_db=(10*np.log10(errors.sum(axis=1)/signal.sum())).tolist(),
        input_nmse_db=(10*np.log10(input_errors.sum(axis=1)/signal.sum())).tolist(),
        note=config['evaluation_scope'], inference_scope='Synthetic conditional noise; no activity detection claim'))


if __name__ == '__main__':
    main()
