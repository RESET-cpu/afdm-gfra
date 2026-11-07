"""White-noise conditional-mean training with the adopted DSM objective."""
import argparse
from copy import deepcopy
from dataclasses import asdict
import json
import math
import os
from pathlib import Path
import platform
import signal
import time
import traceback

import numpy as np
import torch
from threadpoolctl import threadpool_limits

from workspace import ROOT, repository_path
from fileio import sha256, write_json
from networks.score import load_direct_checkpoint
from training.stmp.first import learning_rate
from training.scores.trainer import cpu_state
from training.scores.device import capture_device_rng, restore_device_rng
from receiver.gp_mp.model import PreconditionedMean as PreconditionedScore
from .data import assets
from .batches import (draw_arrays, raw_output, loss_from_raw, mean_from_raw,
                             loss_unchecked, BatchGraph)

DEFAULT = ROOT/'src/configs/training/gp_mp_first.json'


def source_files():
    paths = list((ROOT/'src/training/gp_mp').glob('*.py'))
    paths += list((ROOT/'src/receiver/gp_mp').glob('*.py'))
    paths += list((ROOT/'src/networks').rglob('*.py'))
    paths += [ROOT/'src/workspace.py', ROOT/'src/fileio.py', ROOT/'src/training/stmp/first.py']
    paths += list((ROOT/'src/training/scores').glob('*.py'))
    return sorted(set(paths))


def prepare(config, config_path):
    if config['schema'] != 'white-conditional-mean-training-v1':
        raise ValueError('Matched formal training recipe required')
    if config['noise'].get('max_strength', 0.0) != 0.0:
        raise ValueError('White-noise recipe required')
    out = repository_path(config['output']).resolve()
    allowed = (ROOT/'result/channel_denoising/data').resolve()
    if not out.is_relative_to(allowed) or out == allowed:
        raise ValueError('Use a dedicated channel_denoising candidate directory')
    original = repository_path(config['original_training'])
    assert sha256(original) == config['original_training_sha256']
    source = json.loads(original.read_text(encoding='utf-8'))
    fixed = ('seed', 'validation_seed', 'batch_size', 'microbatch_size', 'learning_rate',
             'minimum_learning_rate', 'ema_decay', 'gradient_clip', 'checkpoint_seconds',
             'maximum_epochs', 'minimum_epochs', 'validation_patience',
             'meaningful_relative_improvement', 'initial_checkpoint_sha256')
    for key in fixed:
        if config['first'][key] != source['first'][key]:
            raise ValueError('Matched setting differs: '+key)
    if (config['runtime']['execution_batch_size'] != config['first']['batch_size']
            or config['runtime']['precision'] != 'float32'):
        raise ValueError('Preserve the original float32 execution batch')
    expected_parameterization = dict(reference_real_variance=0.5, output='conditional_mean',
        objective='original_covariance_weighted_DSM')
    if config['parameterization'] != expected_parameterization:
        raise ValueError('Require the declared reference variance and unchanged DSM objective')
    binding, _, paths, _, _, records = assets(config)
    assert config['scale'] == binding['scale'] == source['scale']
    assert config['train_samples'] == source['bank']['train_samples'] == 50000
    assert config['validation_samples'] == source['bank']['validation_samples'] == 5000
    initial = repository_path(config['first']['initial_checkpoint'])
    assert sha256(initial) == config['first']['initial_checkpoint_sha256']
    data = {s:np.load(p, mmap_mode='r', allow_pickle=False) for s,p in paths.items()}
    for s in data:
        assert len(data[s]) == config[s+'_samples']
    spec = dict(schema=config['schema'], configuration=config,
        configuration_sha256=sha256(config_path), data_sha256=records,
        environment=dict(python=platform.python_version(), torch=str(torch.__version__),
            numpy=np.__version__, cuda=torch.version.cuda,
            gpu=torch.cuda.get_device_name() if torch.cuda.is_available() else None,
            matmul_precision=torch.get_float32_matmul_precision(),
            cudnn_allow_tf32=torch.backends.cudnn.allow_tf32,
            matmul_allow_tf32=torch.backends.cuda.matmul.allow_tf32),
        source_sha256={str(p.relative_to(ROOT)):sha256(p) for p in source_files()},
        prior_definition_sha256=binding['prior_definition_sha256'],
        original_specification='result/runs/proposed_50000_cuda_graph_20261018/model/first/specification.json',
        validation_scope='Same 5000 internal validation samples in 1250 scenes, not the separate 1000-scene performance experiment.',
        matched_settings=list(fixed), planned_optimizer_steps=math.ceil(50000/64)*200)
    out.mkdir(parents=True, exist_ok=True)
    path = out/'specification.json'
    if path.exists():
        if json.loads(path.read_text(encoding='utf-8')) != spec:
            raise ValueError('Existing matched-run specification differs')
    else:
        write_json(path, spec)
        # Exact source bytes retained for this long run, without changing imports.
        for p in source_files():
            dest = out/'source'/p.relative_to(ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(p.read_bytes())
        (out/'recipe.json').write_bytes(config_path.read_bytes())
    return out, data, sha256(path)


def batches(bank, chosen, rng, shape_rng, cfg):
    draw = cfg['first']['microbatch_size']
    parts = [draw_arrays(np.asarray(bank[chosen[i:i+draw]]), rng, shape_rng,
                         cfg['scale'], cfg['noise']) for i in range(0, len(chosen), draw)]
    return tuple(np.concatenate([p[j] for p in parts], axis=0) for j in range(len(parts[0])))


def tensors(arrays, device):
    return tuple(torch.as_tensor(x, device=device) for x in arrays)


def validation(model, bank, cfg, device):
    rng = np.random.default_rng(cfg['first']['validation_seed'])
    shape_rng = np.random.default_rng(cfg['validation_shape_seed'])
    draw = cfg['first']['microbatch_size']
    total = count = error = power = 0
    bands = {}
    model.eval()
    with torch.inference_mode():
        for start in range(0, len(bank), draw):
            arrays = draw_arrays(bank[start:start+draw], rng, shape_rng, cfg['scale'], cfg['noise'])
            ts = tensors(arrays, device)
            raw = raw_output(model, ts)
            loss = loss_from_raw(model, raw, ts)
            mean = mean_from_raw(model, raw, ts)
            e = (mean-ts[0]).square().flatten(1).sum(1).cpu().numpy().astype(float)
            s = ts[0].square().flatten(1).sum(1).cpu().numpy().astype(float)
            value = float(loss.cpu())
            if not np.isfinite(value) or not np.isfinite(e).all():
                raise FloatingPointError('Nonfinite fixed-noise validation')
            total += value*len(e); count += len(e); error += e.sum(); power += s.sum()
            groups = np.floor(-10*np.log10(arrays[2])/5)*5
            for label in np.unique(groups):
                mask = groups == label
                row = bands.setdefault(f'snr_{int(label)}_to_{int(label)+5}_db',
                                       dict(samples=0, error=0., signal=0.))
                row['samples'] += int(mask.sum())
                row['error'] += float(e[mask].sum()); row['signal'] += float(s[mask].sum())
    for row in bands.values():
        row['nmse_db'] = float(10*np.log10(row['error']/row['signal']))
    return dict(loss=total/count, samples=count, nmse_db=float(10*np.log10(error/power)),
                error=float(error), signal=float(power), bands=bands)


class Trainer:
    def __init__(self, out, cfg, specification_hash):
        self.out, self.cfg, self.specification_hash = out, cfg, specification_hash
        self.stop = False

    def status(self, state, **kwargs):
        row = dict(status=state, pid=os.getpid(), updated_unix=time.time(), **kwargs)
        write_json(self.out/'status.json', row)
        print(json.dumps(row), flush=True)

    def request_stop(self, *_):
        self.stop = True

    def save_weight(self, path, model, score, epoch):
        temp = path.with_suffix('.tmp')
        torch.save(dict(schema='colored-preconditioned-first-v1', order=1,
            config=asdict(model.config), architecture=asdict(model.config),
            global_complex_rms=self.cfg['scale'], normalization='population_rms',
            parameterization=self.cfg['parameterization'], output='conditional_mean',
            state_dict=cpu_state(model), metadata=dict(epoch=epoch, validation=score,
                specification_sha256=self.specification_hash,
                initialization_sha256=self.cfg['first']['initial_checkpoint_sha256'],
                noise=self.cfg['noise'], training_scope=self.cfg['scope'])), temp)
        temp.replace(path)

    def run(self, data):
        cfg, settings = self.cfg, self.cfg['first']
        device = cfg['runtime']['device']
        if (self.out/'complete.json').exists():
            complete = json.loads((self.out/'complete.json').read_text())
            assert complete['specification_sha256'] == self.specification_hash
            assert sha256(self.out/'first_best.pt') == complete['weight_sha256']
            self.status('COMPLETED', **{k:complete[k] for k in ('epochs','optimizer_steps','selected_epoch')})
            return
        torch.manual_seed(settings['seed'])
        rng = np.random.default_rng(settings['seed'])
        shape_rng = np.random.default_rng(cfg['shape_seed'])
        base, blob = load_direct_checkpoint(repository_path(settings['initial_checkpoint']), device)
        assert blob['order'] == 1 and blob['global_complex_rms'] == cfg['scale']
        assert list(cfg['noise']['snr_db']) == [blob['config']['snr_db_min'],blob['config']['snr_db_max']]
        model = PreconditionedScore(base, cfg['parameterization']['reference_real_variance']).to(device); del base
        ema = deepcopy(model).eval()
        optimizer = torch.optim.Adam(model.parameters(), lr=settings['learning_rate'])
        epoch, cursor, steps, best, selected_epoch = 1, 0, 0, math.inf, 0
        indices, history, loss_sum, seen = None, [], 0., 0
        last_saved = time.time()
        last = self.out/'last.pt'

        def checkpoint():
            nonlocal last_saved
            state = dict(schema='colored-preconditioned-first-resume-v1',
                specification_sha256=self.specification_hash, model=cpu_state(model), ema=cpu_state(ema),
                optimizer=optimizer.state_dict(), rng=rng.bit_generator.state,
                shape_rng=shape_rng.bit_generator.state, torch_rng=torch.get_rng_state(),
                **capture_device_rng(device), epoch=epoch, cursor=cursor, steps=steps,
                indices=indices, history=history, loss_sum=loss_sum, seen=seen,
                best=best, selected_epoch=selected_epoch)
            temp = last.with_suffix('.tmp'); torch.save(state, temp); temp.replace(last)
            last_saved = time.time()

        if last.exists():
            state = torch.load(last, map_location='cpu', weights_only=False)
            assert state['schema'] == 'colored-preconditioned-first-resume-v1'
            assert state['specification_sha256'] == self.specification_hash
            model.load_state_dict(state['model']); ema.load_state_dict(state['ema'])
            optimizer.load_state_dict(state['optimizer'])
            rng.bit_generator.state = state['rng']; shape_rng.bit_generator.state = state['shape_rng']
            torch.set_rng_state(state['torch_rng']); restore_device_rng(device, state)
            epoch, cursor, steps, indices = (state[k] for k in ('epoch','cursor','steps','indices'))
            history, loss_sum, seen, best, selected_epoch = (state[k] for k in
                ('history','loss_sum','seen','best','selected_epoch'))
            del state
            self.status('RESUMED', epoch=epoch, samples=cursor, optimizer_steps=steps)
        else:
            self.status('VALIDATING_INITIALIZATION', samples=len(data['validation']))
            baseline = validation(ema, data['validation'], cfg, device)
            best = baseline['loss']
            write_json(self.out/'baseline.json', baseline)
            self.save_weight(self.out/'first_best.pt', ema, baseline, 0)
            checkpoint()
            self.status('INITIALIZATION_VALIDATED', validation_loss=best, validation_nmse_db=baseline['nmse_db'])

        graph = BatchGraph(model, settings['batch_size']) if cfg['runtime']['cuda_graph'] else None
        while epoch <= settings['maximum_epochs']:
            start = time.time()
            rate = learning_rate(settings, epoch)
            for group in optimizer.param_groups:
                group['lr'] = rate
            model.train()
            if indices is None:
                indices = rng.permutation(len(data['train']))
            while cursor < len(indices):
                if self.stop or (self.out/'pause.request').exists():
                    checkpoint()
                    self.status('PAUSED', epoch=epoch, samples=cursor, optimizer_steps=steps, resumable=True)
                    return
                chosen = indices[cursor:cursor+settings['batch_size']]
                arrays = batches(data['train'], chosen, rng, shape_rng, cfg)
                optimizer.zero_grad(set_to_none=True)
                if graph:
                    loss_sum += graph.backward(arrays)
                else:
                    loss = loss_unchecked(model, tensors(arrays, device))
                    value = float(loss.detach().cpu())
                    if not np.isfinite(value):
                        raise FloatingPointError('Nonfinite training loss')
                    loss.backward(); loss_sum += value*len(chosen)
                torch.nn.utils.clip_grad_norm_(model.parameters(), settings['gradient_clip'], error_if_nonfinite=True)
                optimizer.step()
                with torch.no_grad():
                    torch._foreach_lerp_(list(ema.parameters()), list(model.parameters()), 1-settings['ema_decay'])
                cursor += len(chosen); seen += len(chosen); steps += 1
                if time.time()-last_saved >= settings['checkpoint_seconds']:
                    checkpoint()
                if steps % 50 == 0:
                    self.status('TRAINING', epoch=epoch, epochs=settings['maximum_epochs'],
                        samples=cursor, training_samples=len(indices), optimizer_steps=steps,
                        loss=loss_sum/seen, learning_rate=rate,
                        elapsed_epoch_seconds=time.time()-start)
            self.status('VALIDATING', epoch=epoch, optimizer_steps=steps)
            result = validation(ema, data['validation'], cfg, device)
            history.append(dict(epoch=epoch, train_loss=loss_sum/seen, validation=result,
                learning_rate=rate, seconds_this_invocation=time.time()-start))
            write_json(self.out/'history.json', history)
            if result['loss'] < best:
                best, selected_epoch = result['loss'], epoch
                self.save_weight(self.out/'first_best.pt', ema, result, epoch)
            self.status('EPOCH_COMPLETE', epoch=epoch, optimizer_steps=steps,
                validation_loss=result['loss'], validation_nmse_db=result['nmse_db'],
                best_validation_loss=best, selected_epoch=selected_epoch)
            epoch += 1; cursor, indices, loss_sum, seen = 0, None, 0., 0
            checkpoint()
        self.save_weight(self.out/'first_final.pt', ema, history[-1]['validation'], epoch-1)
        best_blob = torch.load(self.out/'first_best.pt', map_location='cpu', weights_only=False)
        record = dict(status='COMPLETED', epochs=len(history), optimizer_steps=steps,
            selected_epoch=selected_epoch, validation=best_blob['metadata']['validation'],
            stopping_reason='EXACT_200_EPOCH_BUDGET', optimization_converged_proven=False,
            specification_sha256=self.specification_hash, weight_sha256=sha256(self.out/'first_best.pt'),
            final_weight_sha256=sha256(self.out/'first_final.pt'), receiver_evaluation_completed=False)
        write_json(self.out/'complete.json', record)
        self.status('COMPLETED', epochs=len(history), optimizer_steps=steps, selected_epoch=selected_epoch)


def preflight(out, data, cfg, specification_hash):
    """One disposable optimizer step with the intended execution batch."""
    device = cfg['runtime']['device']
    torch.manual_seed(cfg['first']['seed'])
    base, _ = load_direct_checkpoint(repository_path(cfg['first']['initial_checkpoint']), device)
    model = PreconditionedScore(base, cfg['parameterization']['reference_real_variance']).to(device); del base
    arrays = batches(data['train'], np.arange(64), np.random.default_rng(cfg['first']['seed']),
                     np.random.default_rng(cfg['shape_seed']), cfg)
    if device == 'cuda':
        torch.cuda.reset_peak_memory_stats()
    optimizer = torch.optim.Adam(model.parameters(), lr=cfg['first']['learning_rate'])
    model.train()
    graph = BatchGraph(model, 64)
    before = graph.backward(arrays, use_graph=False)/64
    gradients = [p.grad.detach().clone() for p in model.parameters()]
    optimizer.zero_grad(set_to_none=True)
    captured = graph.backward(arrays)/64
    numerator = sum(float((p.grad-g).double().square().sum().cpu()) for p,g in zip(model.parameters(),gradients))
    denominator = sum(float(g.double().square().sum().cpu()) for g in gradients)
    difference = math.sqrt(numerator/max(denominator,1e-30))
    assert abs(before-captured) < 1e-5*max(1,abs(before)) and difference < 1e-4
    del gradients
    norm = torch.nn.utils.clip_grad_norm_(model.parameters(), cfg['first']['gradient_clip'], error_if_nonfinite=True)
    optimizer.step()
    # Replay after parameter update as well.
    optimizer.zero_grad(set_to_none=True)
    after = graph.backward(arrays)/64
    assert np.isfinite(after)
    result = dict(status='PASS', specification_sha256=specification_hash,
        device=device, execution_batch=64, effective_batch=64,
        initial_loss=before, captured_loss=captured, updated_loss=after,
        graph_gradient_relative_difference=difference, unclipped_gradient_norm=float(norm),
        max_allocated_bytes=torch.cuda.max_memory_allocated() if device == 'cuda' else None,
        max_reserved_bytes=torch.cuda.max_memory_reserved() if device == 'cuda' else None,
        training_steps_saved=0, note='Disposable check; formal run reloads original initializer and fresh optimizer/RNG')
    write_json(out/'PREFLIGHT.json', result)
    print(json.dumps(result), flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('command', choices=('prepare','preflight','train'))
    parser.add_argument('--config', type=Path, default=DEFAULT)
    args = parser.parse_args(argv)
    cfg = json.loads(args.config.read_text(encoding='utf-8'))
    torch.set_num_threads(cfg['runtime']['threads'])
    with threadpool_limits(limits=cfg['runtime']['threads']):
        out, data, specification_hash = prepare(cfg, args.config)
        if args.command == 'prepare':
            print(json.dumps(dict(status='PREPARED', output=str(out), epochs=200, optimizer_steps=156400)))
            return
        if args.command == 'preflight':
            preflight(out, data, cfg, specification_hash)
            return
        if not (out/'PREFLIGHT.json').exists():
            raise ValueError('Complete the intended-device preflight before training')
        checked = json.loads((out/'PREFLIGHT.json').read_text(encoding='utf-8'))
        if checked['status'] != 'PASS' or checked['specification_sha256'] != specification_hash:
            raise ValueError('Preflight must pass for this exact specification')
        trainer = Trainer(out, cfg, specification_hash)
        signal.signal(signal.SIGINT, trainer.request_stop)
        signal.signal(signal.SIGTERM, trainer.request_stop)
        try:
            trainer.run(data)
        except Exception:
            write_json(out/'FAILURE.json', dict(status='FAILED', traceback=traceback.format_exc(),
                pid=os.getpid(), updated_unix=time.time(), automatic_retry=False))
            trainer.status('FAILED', details='FAILURE.json; last complete checkpoint retained')
            raise


if __name__ == '__main__':
    main()
