"""Train the L-DAMP DnCNN on the existing, disjoint physical channel banks.

Produces a checkpoint and a runnable, checkpoint-bound receiver configuration
inside a fresh output directory. Formal activity calibration and receiver
evaluation remain explicit later stages. --smoke never installs formal weights.
"""
from copy import deepcopy
import argparse
import json
import os
from pathlib import Path
import signal
import shutil
import sys
import time
import numpy as np
import torch

ROOT = next(parent for parent in Path(__file__).resolve().parents
            if (parent/'src/afdm_jadcedd').is_dir())
sys.path.insert(0, str(ROOT/'src'))
from afdm_jadcedd.algorithm.baselines.ldamp.network import DnCNN, pack
from afdm_jadcedd.utils import sha256, write_json


def initialize_noise_identity(model):
    """Initialize the residual-noise CNN to the identity in evaluation mode.

    For C real input channels, the first ReLU keeps [x_+, (-x)_+].
    Center-tap identity convolutions and identity BatchNorm transforms preserve
    these nonnegative features; the final convolution subtracts each pair.
    Thus the initial clean estimate x - noise(x) is zero. This is a project
    initialization choice, not an additional denoiser or an inference fallback.
    """
    convolutions = [layer for layer in model.modules() if isinstance(layer, torch.nn.Conv2d)]
    channels = convolutions[0].in_channels
    if any(layer.out_channels < 2*channels for layer in convolutions[:-1]):
        raise ValueError('Noise identity initialization requires at least twice the input channels')
    with torch.no_grad():
        for layer in convolutions:
            layer.weight.zero_()
            if layer.bias is not None:
                layer.bias.zero_()
        for index in range(channels):
            convolutions[0].weight[index, index, 1, 1] = 1
            convolutions[0].weight[index+channels, index, 1, 1] = -1
            convolutions[-1].weight[index, index, 1, 1] = 1
            convolutions[-1].weight[index, index+channels, 1, 1] = -1
        for layer in convolutions[1:-1]:
            for index in range(2*channels):
                layer.weight[index, index, 1, 1] = 1
        for layer in model.modules():
            if isinstance(layer, torch.nn.BatchNorm2d):
                mean, variance = 1/np.sqrt(2*np.pi), .5-1/(2*np.pi)
                layer.running_mean.fill_(mean)
                layer.running_var.fill_(variance)
                layer.weight.fill_(np.sqrt(variance+layer.eps))
                layer.bias.fill_(mean)


def completed_band(rows, recipe):
    best, stale = float('inf'), 0
    for row in rows:
        value = row['validation']['mse_real']
        best, stale = (value, 0) if value < best else (best, stale+1)
    return bool(rows) and (rows[-1]['epoch'] >= recipe['maximum_epochs'] or
        (rows[-1]['epoch'] >= recipe['minimum_epochs'] and stale >= recipe['validation_patience']))


def cpu_state(value):
    if torch.is_tensor(value):
        return value.detach().cpu().clone()
    if isinstance(value, dict):
        return {k:cpu_state(v) for k,v in value.items()}
    if isinstance(value, list):
        return [cpu_state(v) for v in value]
    if isinstance(value, tuple):
        return tuple(cpu_state(v) for v in value)
    return value


def save_training_state(path, model, optimizer, scheduler, rng, *, device, **progress):
    payload = dict(schema='ldamp-training-state-v2', model=cpu_state(model.state_dict()),
        optimizer=cpu_state(optimizer.state_dict()), scheduler=scheduler.state_dict(),
        numpy_rng=rng.bit_generator.state, torch_rng=torch.get_rng_state(), **progress)
    if device == 'mps':
        payload['mps_rng'] = torch.mps.get_rng_state()
    temporary = path.with_suffix('.tmp')
    torch.save(payload, temporary)
    temporary.replace(path)


def restore_training_state(payload, model, optimizer, scheduler, rng, *, device):
    model.load_state_dict(payload['model'])
    optimizer.load_state_dict(payload['optimizer'])
    scheduler.load_state_dict(payload['scheduler'])
    rng.bit_generator.state = payload['numpy_rng']
    torch.set_rng_state(payload['torch_rng'])
    if device == 'mps' and 'mps_rng' in payload:
        torch.mps.set_rng_state(payload['mps_rng'])


def make_batch(bank, indices, rng, recipe, scale):
    h = np.asarray(bank[indices])/scale
    active = rng.random(len(indices)) < recipe['activity_probability']
    clean = pack(h*active[:,None,None,None])
    lo, hi = recipe['noise_complex_variance']
    variance = np.exp(rng.uniform(np.log(lo), np.log(hi), len(indices)))
    noise = rng.standard_normal(clean.shape).astype(np.float32)*np.sqrt(variance[:,None,None,None]/2)
    input_scale = recipe.get('network_input_scale', 1.)
    return torch.from_numpy(((clean+noise)/input_scale).astype(np.float32)), torch.from_numpy(clean/input_scale), active


@torch.inference_mode()
def validate(model, bank, count, recipe, scale, device):
    model.eval()
    rng = np.random.default_rng(recipe['validation_seed'])
    error = power = active_error = inactive_error = active_power = 0.
    coordinates = active_count = 0
    for start in range(0, count, recipe['batch_size']):
        x, target, active = make_batch(bank, np.arange(start,min(count,start+recipe['batch_size'])), rng, recipe, scale)
        output = model(x.to(device)).cpu().numpy()
        truth = target.numpy()
        errors = np.sum((output-truth).astype(np.float64)**2, axis=(1,2,3))
        powers = np.sum(truth.astype(np.float64)**2, axis=(1,2,3))
        error += float(errors.sum()); power += float(powers.sum())
        active_error += float(errors[active].sum()); inactive_error += float(errors[~active].sum())
        active_power += float(powers[active].sum()); active_count += int(active.sum())
        coordinates += truth.size
    return dict(mse_real=error/coordinates, zero_estimator_mse=power/coordinates,
                network_input_scale=recipe.get('network_input_scale',1.),
                active_nmse_db=float(10*np.log10(max(active_error/max(active_power,1e-30),1e-30))),
                inactive_error=inactive_error, active_samples=active_count,
                full_error=error, signal_energy=power, samples=count)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT/'configs/training/ldamp.json')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--device', choices=['cpu','mps'], default='mps' if torch.backends.mps.is_available() else 'cpu')
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--resume-from', type=Path,
                        help='Continue saved training into a fresh output directory')
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Fresh training directory required; previous attempts are retained')
    recipe = json.loads(args.config.read_text())
    if recipe.get('schema') == 'ldamp-beam-dncnn-training-v2':
        from afdm_jadcedd.algorithm.baselines.ldamp.training import run
        return run(args)
    receiver = json.loads((ROOT/recipe['receiver_config']).read_text())
    torch.set_num_threads(1)
    torch.manual_seed(recipe['seed'])
    model = DnCNN(**receiver['network']).to(args.device)
    train = np.load(ROOT/recipe['train_path'], mmap_mode='r')
    val = np.load(ROOT/recipe['validation_path'], mmap_mode='r')
    train_ids = np.load(ROOT/recipe['train_identities'])
    val_ids = np.load(ROOT/recipe['validation_identities'])
    if set(train_ids[:,0]) & set(val_ids[:,0]):
        raise ValueError('Training and validation physical scenes overlap')
    if train.shape[1:] != (16,16,16) or val.shape[1:] != train.shape[1:]:
        raise ValueError('Full 16-antenna AFDM channel banks required')
    prior = json.loads((ROOT/recipe['prior_definition']).read_text())
    hashes = {s: sha256(ROOT/recipe[s+'_path']) for s in ('train','validation')}
    if hashes != prior['sample_files_sha256']:
        raise ValueError('Physical training bank hash mismatch')
    ntrain, nval = (64,64) if args.smoke else (len(train),len(val))
    epochs = 1 if args.smoke else recipe['maximum_epochs']
    sources = {str(p.relative_to(ROOT)):sha256(p) for p in
               [Path(__file__).resolve(), ROOT/'src/afdm_jadcedd/algorithm/baselines/ldamp/network.py']}
    args.output.mkdir(parents=True)
    write_json(args.output/'PLAN.json', dict(recipe=recipe, receiver=receiver, smoke=args.smoke,
        train_samples=ntrain, validation_samples=nval, device=args.device, bank_sha256=hashes,
        source_sha256=sources, parameters=sum(p.numel() for p in model.parameters()),
        validation_scope='Denoising validation only; no test or receiver-performance claims'))
    rng = np.random.default_rng(recipe['seed'])
    started, best, stale = time.time(), float('inf'), 0
    stopped = False
    def request_stop(*_):
        nonlocal stopped
        stopped = True
    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    parent = args.resume_from
    history = []
    if parent is not None:
        plan = json.loads((parent/'PLAN.json').read_text())
        if plan['recipe'] != recipe or plan['bank_sha256'] != hashes or plan['smoke'] != args.smoke:
            raise ValueError('Resume recipe, data banks and smoke status must match')
        for key in ('network','scale','noise_boundaries'):
            if plan['receiver'][key] != receiver[key]:
                raise ValueError('Resume representation changed: '+key)
        network_path = 'src/afdm_jadcedd/algorithm/baselines/ldamp/network.py'
        if plan['source_sha256'][network_path] != sources[network_path]:
            raise ValueError('Resume network implementation changed')
        history = json.loads((parent/'HISTORY.json').read_text()) if (parent/'HISTORY.json').exists() else []
        # The legacy checkpoint lacks shuffle/noise RNG state. Declare a new
        # stream and restart its incomplete epoch with retained model/Adam.
        rng = np.random.default_rng(recipe['seed']+1)
        torch.manual_seed(recipe['seed']+1)
        write_json(args.output/'HISTORY.json', history)
        write_json(args.output/'CONTINUATION.json', dict(parent=str(parent.resolve()),
            parent_plan_sha256=sha256(parent/'PLAN.json'),
            parent_history_sha256=sha256(parent/'HISTORY.json') if (parent/'HISTORY.json').exists() else None,
            inherited_complete_epochs=len(history), legacy_continuation_seed=recipe['seed']+1,
            legacy_scope='Retain model and Adam; reconstruct scheduler from history; restart incomplete epoch with a new shuffle/noise stream. Not exact legacy trajectory continuation.',
            v2_scope='Restore full model, optimizer, scheduler, RNG, sample order and partial-epoch loss state'))
    try:
        states, scales, validations = [], [], []
        boundaries = receiver['noise_boundaries']
        for band, (low, high) in enumerate(zip(boundaries[:-1], boundaries[1:])):
            band_recipe = deepcopy(recipe)
            band_recipe['noise_complex_variance'] = [low, high]
            input_scale = float(np.sqrt(1+np.sqrt(low*high)))
            band_recipe['network_input_scale'] = input_scale
            band_out = args.output/f'band{band:02d}'
            band_out.mkdir()
            previous = [r for r in history if r['noise_band'] == band]
            if parent is not None and completed_band(previous, recipe):
                shutil.copy2(parent/band_out.name/'denoiser.pt', band_out/'denoiser.pt')
                checkpoint = torch.load(band_out/'denoiser.pt', map_location='cpu', weights_only=True)
                states.append(checkpoint['model']); scales.append(input_scale)
                validations.append(checkpoint['validation'])
                write_json(band_out/'COMPLETE.json', dict(status='REUSED_COMPLETED_BAND',
                    parent=str(parent/band_out.name), checkpoint_sha256=sha256(band_out/'denoiser.pt')))
                continue
            model = DnCNN(**receiver['network']).to(args.device)
            if recipe.get('initialization') == 'noise_identity':
                initialize_noise_identity(model)
            optimizer = torch.optim.Adam(model.parameters(), lr=recipe['learning_rate'])
            scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, factor=.1,
                patience=recipe['lr_patience'], min_lr=recipe['minimum_learning_rate'])
            best, stale = float('inf'), 0
            pending = None
            start_epoch = 1
            if parent is not None and previous:
                source = parent/band_out.name
                shutil.copy2(source/'denoiser.pt', band_out/'denoiser.pt')
                for row in previous:
                    value = row['validation']['mse_real']
                    best, stale = (value,0) if value < best else (best,stale+1)
                    scheduler.step(value)
                state_path = source/'interrupted.pt' if (source/'interrupted.pt').exists() else source/'last.pt'
                payload = torch.load(state_path, map_location='cpu', weights_only=False)
                if payload.get('schema') == 'ldamp-training-state-v2':
                    restore_training_state(payload,model,optimizer,scheduler,rng,device=args.device)
                    start_epoch = payload['epoch']
                    if payload.get('order') is not None:
                        pending = payload
                else:
                    model.load_state_dict(payload['model']); optimizer.load_state_dict(payload['optimizer'])
                    start_epoch = payload['epoch']
                    write_json(band_out/'LEGACY_RESUME.json', dict(checkpoint_sha256=sha256(state_path),
                        restarted_epoch=start_epoch, inherited_partial_epoch_samples=payload['samples_in_epoch'],
                        retained_optimizer=True, exact_random_stream_restored=False))
            elif parent is not None and (parent/band_out.name/'interrupted.pt').exists():
                payload = torch.load(parent/band_out.name/'interrupted.pt',map_location='cpu',weights_only=False)
                if payload.get('schema') != 'ldamp-training-state-v2':
                    raise ValueError('First-epoch legacy checkpoint requires an explicit migration')
                restore_training_state(payload,model,optimizer,scheduler,rng,device=args.device)
                start_epoch=payload['epoch'];pending=payload
            for epoch in range(start_epoch,epochs+1):
                model.train()
                if pending is not None:
                    order, total, seen = pending['order'], pending['total_loss'], pending['samples_in_epoch']
                    pending = None
                else:
                    order = rng.permutation(ntrain)
                    total, seen = 0., 0
                last_report = 0.
                for offset in range(seen,ntrain,recipe['batch_size']):
                    indices = order[offset:offset+recipe['batch_size']]
                    x, target, _ = make_batch(train,indices,rng,band_recipe,receiver['scale'])
                    optimizer.zero_grad(set_to_none=True)
                    loss = (model(x.to(args.device))-target.to(args.device)).square().mean()
                    if not torch.isfinite(loss):
                        raise FloatingPointError('Nonfinite DnCNN training loss')
                    loss.backward()
                    optimizer.step()
                    total += float(loss.item())*len(indices); seen += len(indices)
                    if time.time()-last_report > 30:
                        write_json(args.output/'STATUS.json', dict(status='TRAINING', pid=os.getpid(), noise_band=band, epoch=epoch,
                            samples_in_epoch=seen, train_samples=ntrain, elapsed_seconds=time.time()-started))
                        last_report = time.time()
                    if stopped:
                        break
                if stopped:
                    save_training_state(band_out/'interrupted.pt',model,optimizer,scheduler,rng,device=args.device,
                        epoch=epoch,samples_in_epoch=seen,order=order,total_loss=total,
                        network=receiver['network'],scale=receiver['scale'],noise_band=band)
                    write_json(args.output/'STATUS.json',dict(status='INTERRUPTED',noise_band=band,epoch=epoch,samples_in_epoch=seen))
                    return 130
                metrics = validate(model,val,nval,band_recipe,receiver['scale'],args.device)
                row = dict(noise_band=band, epoch=epoch, training_mse=total/seen, validation=metrics,
                           learning_rate=optimizer.param_groups[0]['lr'], elapsed_seconds=time.time()-started)
                if not np.isfinite(metrics['mse_real']):
                    raise FloatingPointError('Nonfinite validation error')
                if metrics['mse_real'] < best:
                    best, stale = metrics['mse_real'], 0
                    torch.save(dict(model={k:v.detach().cpu() for k,v in model.state_dict().items()},
                        network=receiver['network'], scale=receiver['scale'], epoch=epoch,
                        validation=metrics, smoke=args.smoke, recipe=band_recipe, input_scale=input_scale),band_out/'denoiser.pt')
                else:
                    stale += 1
                scheduler.step(metrics['mse_real'])
                history.append(row)
                write_json(args.output/'HISTORY.json',history)
                save_training_state(band_out/'last.pt',model,optimizer,scheduler,rng,device=args.device,
                    epoch=epoch+1,samples_in_epoch=0,order=None,total_loss=0.,
                    network=receiver['network'],scale=receiver['scale'],noise_band=band)
                print(json.dumps(row),flush=True)
                if epoch >= recipe['minimum_epochs'] and stale >= recipe['validation_patience']:
                    break
            checkpoint = torch.load(band_out/'denoiser.pt', map_location='cpu', weights_only=True)
            states.append(checkpoint['model'])
            scales.append(input_scale)
            validations.append(checkpoint['validation'])
            write_json(band_out/'COMPLETE.json',dict(status='COMPLETE',completed_epoch=epoch,
                selected_epoch=checkpoint['epoch'],checkpoint_sha256=sha256(band_out/'denoiser.pt')))
        torch.save(dict(models=states, network=receiver['network'], scale=receiver['scale'],
            noise_boundaries=boundaries, input_scales=scales, validation=validations,
            smoke=args.smoke), args.output/'denoiser_bank.pt')
        if any(sha256(ROOT/p) != h for p,h in sources.items()):
            raise RuntimeError('Training source changed during execution; checkpoint retained for inspection')
        receiver.update(checkpoint_path=str((args.output/'denoiser_bank.pt').resolve()),
            checkpoint_sha256=sha256(args.output/'denoiser_bank.pt'), readout=None,
            receiver_validation_passed=False,
            validation_status='SMOKE_ONLY' if args.smoke else 'DENOISER_TRAINED_RECEIVER_UNVALIDATED')
        receiver.pop('comparison_report', None)
        receiver.pop('diagnosis_report', None)
        write_json(args.output/'receiver.json', receiver)
        write_json(args.output/'STATUS.json', dict(status='SMOKE_COMPLETE' if args.smoke else 'TRAINING_COMPLETE',
            epochs_across_bands=len(history), bands=len(states), elapsed_seconds=time.time()-started,
            next_stage='Independent receiver calibration and paired evaluation; no activity rule installed'))
        return 0
    except Exception as error:
        write_json(args.output/'STATUS.json',dict(status='FAILED',error=repr(error),elapsed_seconds=time.time()-started))
        raise


if __name__ == '__main__':
    raise SystemExit(main())
