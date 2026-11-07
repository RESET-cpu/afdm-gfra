"""Execution-only continuation; same v3 conditions, state, order and budget."""
import argparse
import gc
import json
import os
import random
import shutil
import time
import traceback
from pathlib import Path

import numpy as np
import psutil
import torch
from threadpoolctl import threadpool_limits
from experiments.lstmp_candidate_20261019.common import (
    CONFIG, CONFIG_PATH, ROOT, OUT, sha, save_json, save_torch, cpu_state,
    status, log_event, check_budget)
from .data import Cases
from experiments.lstmp_candidate_20261019.fixed_budget import epoch_order
from experiments.lstmp_candidate_20261019.execution import configure_execution
from experiments.lstmp_candidate_20261019.optimization import clip_gradient_norm
from .receiver import Receiver
from experiments.lstmp_training_v2_20261020.objectives import loss_components, assign_gradients, selected_epoch
from experiments.lstmp_training_v2_20261020.optimization import (eligible_parameters, set_phase, make_optimizer,
                           rng_state, restore_rng, gradient_diagnostics)
from experiments.lstmp_training_v2_20261020.evaluation import evaluate


def seed_depth(depth):
    seed = CONFIG['seed'] + depth * 100000
    random.seed(seed)
    np.random.seed(seed % 2**32)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def verify_binding():
    manifest = json.loads((OUT / 'MANIFEST.json').read_text(encoding='utf-8'))
    if manifest['configuration'] != CONFIG:
        raise ValueError('Frozen configuration changed')
    for key in ('snapshot_hashes', 'bound_assets'):
        for path, digest in manifest[key].items():
            if sha(path) != digest:
                raise ValueError(f'Frozen input changed: {path}')
    for path, digest in manifest['protected_assets'].items():
        if sha(ROOT / path) != digest:
            raise ValueError(f'Protected baseline changed: {path}')
    preflight = json.loads((OUT / 'protocol/PREFLIGHT.json').read_text(encoding='utf-8'))
    if preflight['status'] != 'PASSED' or preflight['manifest_sha256'] != sha(OUT / 'MANIFEST.json'):
        raise ValueError('Preflight does not cover this frozen implementation')
    if sha(preflight['report']) != preflight['report_sha256']:
        raise ValueError('Preflight report binding changed')
    return manifest


def acquire_lock(resume):
    path = OUT / 'RUNNING.lock'
    if path.exists():
        pid = int(path.read_text(encoding='utf-8'))
        try:
            process = psutil.Process(pid)
            live = process.is_running() and process.status() != psutil.STATUS_ZOMBIE
            matches = live and str(OUT).lower() in str(process.cwd()).lower()
            if matches:
                raise RuntimeError(f'This run is already active: PID {pid}')
        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            pass
        if not resume:
            raise RuntimeError('Existing lock requires explicit resume after inspection')
        path.unlink()
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(descriptor, str(os.getpid()).encode())
    os.close(descriptor)
    return path


def total_updates(depth, epoch, cursor):
    return (depth - 1) * 3 * CONFIG['receiver']['train_scenes'] + (
        epoch - 1) * CONFIG['receiver']['train_scenes'] + cursor


def empty_totals():
    return dict(channel=0., activity=0., total=0., gradient_norm=0.,
                clipped_steps=0, scene_seconds=0., score_forward_calls=0)


def save_resume(folder, model, optimizer, eligible, depth, epoch, cursor,
                order, totals, history, best_epoch, started):
    save_torch(folder / 'last.pt', dict(
        schema='lstmp-conditional-bce-v3-resume', manifest_sha256=sha(OUT / 'MANIFEST.json'),
        state=cpu_state(model), optimizer=optimizer.state_dict(), eligible=sorted(eligible),
        depth=depth, epoch=epoch, cursor=cursor, order=np.asarray(order),
        totals=totals, history=history, best_epoch=best_epoch, rng=rng_state(),
        phase='ADAPTATION' if epoch <= 1 else 'JOINT',
        completed_updates=total_updates(depth, epoch, cursor),
        elapsed_seconds=time.time() - started))
    save_json(OUT / 'ACTIVE_TIME.json', dict(consumed_seconds=time.time() - started))


def validation(model, cases, statistics, depth, epoch, started):
    def progress(count):
        status('VALIDATING', depth=depth, epoch=epoch, scenes=count, total=len(cases),
               completed_updates=((depth - 1) * 3 + epoch) * CONFIG['receiver']['train_scenes'],
               elapsed_seconds=time.time() - started)
    status('VALIDATING', depth=depth, epoch=epoch, scenes=0, total=len(cases))
    return evaluate(model, cases, statistics, started=started, on_progress=progress)


def record_epoch(folder, model, result, depth, epoch):
    save_json(folder / f'validation_epoch_{epoch}.json', result)
    save_torch(folder / f'epoch_{epoch}.pt', dict(
        schema='lstmp-conditional-bce-v3-weights', state=cpu_state(model),
        depth=depth, epoch=epoch, summary=result['summary'],
        manifest_sha256=sha(OUT / 'MANIFEST.json')))
    return dict(epoch=epoch, **result['summary'])


def train_receiver(device, started):
    statistics = json.loads((OUT / 'protocol/TRAINING_STATISTICS.json').read_text(encoding='utf-8'))
    prior = torch.load(OUT / 'initialization/first_50000.pt',
                       map_location='cpu', weights_only=False, mmap=True)
    scale = prior['scale']
    training, validation_cases = Cases('train', scale, device), Cases('validation', scale, device)
    settings = CONFIG['receiver']
    previous = None
    for depth in range(1, settings['maximum_depth'] + 1):
        folder = OUT / f'checkpoints/depth_{depth}'
        folder.mkdir(parents=True, exist_ok=True)
        complete = folder / 'COMPLETE.json'
        if complete.exists():
            receipt = json.loads(complete.read_text(encoding='utf-8'))
            previous = folder / 'best.pt'
            if receipt['updates'] != 3 * len(training) or sha(previous) != receipt['best_sha256']:
                raise ValueError(f'Completed depth {depth} binding changed')
            continue
        seed_depth(depth)
        model = Receiver()
        for _ in range(depth):
            model.add_layer(prior['state'])
        if previous is not None:
            old = torch.load(previous, map_location='cpu', weights_only=False, mmap=True)
            result = model.load_state_dict(old['state'], strict=False)
            expected = {n for n in model.state_dict() if n.startswith(f'layers.{depth-1}.')}
            if set(result.missing_keys) != expected or result.unexpected_keys:
                raise ValueError('Previous selected layers did not load exactly')
            del old
        eligible = eligible_parameters(model)
        model.to(device)
        optimizer = make_optimizer(model, settings, eligible,
                                   fused=CONFIG['execution']['adam_implementation'] == 'fused')
        configure_execution(model, optimizer, CONFIG['execution'], device)
        last = folder / 'last.pt'
        if last.exists():
            saved = torch.load(last, map_location='cpu', weights_only=False, mmap=True)
            current_binding = saved['manifest_sha256'] == sha(OUT / 'MANIFEST.json')
            origin = CONFIG['execution_continuation']
            inherited_binding = (
                saved['manifest_sha256'] == origin['source_manifest_sha256']
                and sha(last) == origin['source_checkpoint_sha256'])
            if not (current_binding or inherited_binding) or saved['depth'] != depth:
                raise ValueError('Resume checkpoint belongs to different run/depth')
            model.load_state_dict(saved['state'], strict=True)
            optimizer.load_state_dict(saved['optimizer'])
            configure_execution(model, optimizer, CONFIG['execution'], device)
            eligible = set(saved['eligible'])
            epoch, cursor = saved['epoch'], saved['cursor']
            order, totals = saved['order'], saved['totals']
            history, best_epoch = saved['history'], saved['best_epoch']
            restore_rng(saved['rng'])
            del saved
        else:
            epoch, cursor, totals = 1, 0, empty_totals()
            set_phase(model, optimizer, eligible, epoch)
            initial = validation(model, validation_cases, statistics, depth, 0, started)
            history = [record_epoch(folder, model, initial, depth, 0)]
            best_epoch = 0
            del initial
            order = epoch_order(training.indices, depth, epoch)
            save_resume(folder, model, optimizer, eligible, depth, epoch, cursor,
                        order, totals, history, best_epoch, started)
        while epoch <= 3:
            model.graphs_enabled = False
            model.clear_graphs()
            optimizer.zero_grad(set_to_none=True)
            gc.collect()
            if torch.device(device).type == 'cuda':
                torch.cuda.empty_cache()
            phase = set_phase(model, optimizer, eligible, epoch)
            if not np.array_equal(order, epoch_order(training.indices, depth, epoch)):
                raise ValueError('Resume scene order changed')
            model.train()
            diagnostic_path = folder / f'gradients_epoch_{epoch}.json'
            if not diagnostic_path.exists():
                # Same public training scene at all depths. Does not choose weights.
                diagnostic_position = min(range(len(training)), key=training.indices.__getitem__)
                public, labels, info = training[diagnostic_position]
                optimizer.zero_grad(set_to_none=True)
                outputs, _ = model(public)
                components = loss_components(outputs, labels, statistics)
                measured = gradient_diagnostics(model, components)
                save_json(diagnostic_path, dict(depth=depth, epoch=epoch, phase=phase, info=info,
                    before_clipping=True, gradients=measured,
                    zero_initial_head_may_block_bce_score_gradient=True))
                del outputs, components, public, labels
            model.graphs_enabled = True
            if torch.device(device).type == 'cuda':
                torch.cuda.reset_peak_memory_stats()
            try:
                while cursor < len(order):
                    check_budget(started)
                    position = int(order[cursor])
                    training.prefetch(order[cursor:cursor+4])
                    public, labels, info = training[position]
                    before = time.perf_counter()
                    calls_before = model.score_evaluations
                    optimizer.zero_grad(set_to_none=True)
                    collect = cursor == 0 or (cursor+1) % 32 == 0 or cursor+1 == len(order)
                    outputs, diagnostics = model(public, collect_diagnostics=collect)
                    components = loss_components(outputs, labels, statistics)
                    if not bool(torch.isfinite(components['total'])):
                        raise FloatingPointError(f'Nonfinite training loss at {info}; sample retained')
                    assign_gradients(model, components, bce_updates_score=True)
                    norm = float(clip_gradient_norm(model.parameters(), 1.))
                    optimizer.step()
                    for key in ('channel', 'activity', 'total'):
                        totals[key] += float(components[key].detach())
                    totals['gradient_norm'] += norm
                    totals['clipped_steps'] += int(norm > 1.)
                    totals['scene_seconds'] += time.perf_counter() - before
                    totals['score_forward_calls'] += model.score_evaluations - calls_before
                    cursor += 1
                    if cursor == 1 or cursor % settings['checkpoint_steps'] == 0 or cursor == len(order):
                        save_resume(folder, model, optimizer, eligible, depth, epoch, cursor,
                                    order, totals, history, best_epoch, started)
                    if cursor == 1 or cursor % 32 == 0 or cursor == len(order):
                        status('TRAINING', depth=depth, epoch=epoch, phase=phase, cursor=cursor,
                            scenes_per_epoch=len(training), completed_updates=total_updates(depth, epoch, cursor),
                            planned_updates=CONFIG['planned_updates'], loss=float(components['total'].detach()),
                            channel_loss=float(components['channel'].detach()),
                            activity_loss=float(components['activity'].detach()), gradient_norm=norm,
                            mean_epoch_loss=totals['total'] / cursor,
                            clip_fraction=totals['clipped_steps'] / cursor, scene=info,
                            epoch_score_forward_calls=totals['score_forward_calls'],
                            score_graph_replays=model.graph_replays,
                            score_graph_captures=model.graph_capture_count,
                            learning_rates={g['name']: g['lr'] for g in optimizer.param_groups},
                            last_layer_diagnostics=diagnostics[-1],
                            peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated() if torch.device(device).type == 'cuda' else 0,
                            elapsed_seconds=time.time() - started)
                    del outputs, components, public, labels
            except (InterruptedError, KeyboardInterrupt):
                save_resume(folder, model, optimizer, eligible, depth, epoch, cursor,
                            order, totals, history, best_epoch, started)
                raise
            optimizer.zero_grad(set_to_none=True)
            result = validation(model, validation_cases, statistics, depth, epoch, started)
            row = record_epoch(folder, model, result, depth, epoch)
            row.update(phase=phase, training_totals=totals)
            history.append(row)
            best_epoch = selected_epoch(history)
            save_json(folder / 'history.json', history)
            save_json(folder / 'BEST.json', dict(epoch=best_epoch,
                selection='minimum final-layer conditional-channel loss + BCE; earlier epoch wins ties',
                checkpoint=f'epoch_{best_epoch}.pt',
                selection_loss=history[best_epoch]['selection_loss']))
            log_event(dict(stage='EPOCH_COMPLETE', depth=depth, **row, selected_epoch=best_epoch))
            del result
            epoch += 1
            cursor, totals = 0, empty_totals()
            order = epoch_order(training.indices, depth, epoch)
            save_resume(folder, model, optimizer, eligible, depth, epoch, cursor,
                        order, totals, history, best_epoch, started)
        previous = folder / 'best.pt'
        shutil.copy2(folder / f'epoch_{best_epoch}.pt', previous)
        save_json(folder / 'COMPLETE.json', dict(depth=depth, selected_epoch=best_epoch,
            selected_initialization=best_epoch == 0, updates=3 * len(training),
            best_sha256=sha(previous), epoch_sha256={
                str(i): sha(folder / f'epoch_{i}.pt') for i in range(4)},
            selection_loss=history[best_epoch]['selection_loss'], history=history,
            aer_best_epoch=min(history, key=lambda r: (r['aer'], r['epoch']))['epoch'],
            nmse_best_epoch=min(history, key=lambda r: (r['pooled_nmse'], r['epoch']))['epoch']))
        status('DEPTH_COMPLETE', depth=depth, selected_epoch=best_epoch,
               completed_updates=depth * 3 * len(training), elapsed_seconds=time.time() - started)
        model.clear_graphs()
        del model, optimizer
        gc.collect()
        if torch.device(device).type == 'cuda':
            torch.cuda.empty_cache()
    training.close()
    validation_cases.close()
    return previous


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', action='store_true')
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--fresh', action='store_true')
    modes.add_argument('--resume', action='store_true')
    parser.add_argument('--device', default='cuda')
    args = parser.parse_args()
    if not args.train:
        parser.error('Training requires --train')
    if args.fresh and (OUT / 'checkpoints').exists():
        raise FileExistsError('Fresh training requires a run without checkpoints')
    if args.resume and not (OUT / 'checkpoints').exists():
        raise FileNotFoundError('No training checkpoint to resume')
    if (OUT / 'COMPLETE.json').exists():
        raise RuntimeError('Completed runs are immutable')
    manifest = verify_binding()
    lock = acquire_lock(args.resume)
    consumed = 0.
    usage = OUT / 'ACTIVE_TIME.json'
    if args.resume and usage.exists():
        consumed = json.loads(usage.read_text())['consumed_seconds']
    started = time.time() - consumed
    try:
        torch.set_num_threads(CONFIG['cpu_threads'])
        threadpool_limits(CONFIG['cpu_threads'])
        if torch.device(args.device).type == 'cuda':
            torch.backends.cuda.matmul.allow_tf32 = CONFIG['allow_tf32']
            torch.backends.cudnn.allow_tf32 = CONFIG['allow_tf32']
            torch.backends.cudnn.benchmark = True
        status('STARTING', protocol='v3 main A; nineteen conditions; ten layers', device=args.device,
               planned_updates=CONFIG['planned_updates'], resume=args.resume, config=str(CONFIG_PATH))
        best = train_receiver(args.device, started)
        preserved = {path: sha(ROOT / path) == digest for path, digest in manifest['protected_assets'].items()}
        if not all(preserved.values()):
            raise RuntimeError('A protected baseline asset changed')
        save_json(OUT / 'COMPLETE.json', dict(status='COMPLETE', protocol='v3 main A; nineteen conditions; ten layers',
            completed_updates=CONFIG['planned_updates'], selected_checkpoint=str(best), selected_sha256=sha(best),
            protected_assets_preserved=preserved, independent_test_performed=False,
            elapsed_seconds=time.time() - started))
        status('COMPLETE', completed_updates=CONFIG['planned_updates'], checkpoint=str(best))
    except (InterruptedError, KeyboardInterrupt) as error:
        status('PAUSED', reason=str(error) or 'Keyboard interrupt', elapsed_seconds=time.time() - started)
        raise
    except BaseException as error:
        save_json(OUT / f'FAILURE_{time.time_ns()}.json', dict(
            error=repr(error), traceback=traceback.format_exc(), elapsed_seconds=time.time() - started))
        status('FAILED', error=repr(error))
        raise
    finally:
        save_json(usage, dict(consumed_seconds=time.time() - started))
        lock.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
