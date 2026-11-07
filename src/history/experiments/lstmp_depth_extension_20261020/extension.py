"""Grow a preserved receiver by one independently parameterized layer at a time.

Copied into a NEW frozen lstmp_candidate_20261019 package by the preparation
script. The message equations and networks remain those of the parent run.
The adaptation/joint schedule is a project budget, not a paper's epoch count.
"""
import copy
import json
import math
import time

import torch

from .common import CONFIG, OUT, check_budget, cpu_state, log_event, save_json, save_torch, sha, status
from .data import Cases, build_cases
from .execution import configure_execution
from .fixed_budget import epoch_order
from .optimization import clip_gradient_norm
from .receiver import Receiver, evaluate, loss


def append_trained_layer(model):
    """Independent storage, initialized from the preceding trained layer."""
    if not model.layers:
        raise ValueError('Expansion requires an existing trained receiver')
    model.layers.append(copy.deepcopy(model.layers[-1]))


def eligible_parameters(model):
    # Keep any architecture-defined non-trainable parameters frozen.
    return {name for name, parameter in model.named_parameters() if parameter.requires_grad}


def set_phase(model, eligible, adaptation):
    """In adaptation, also learn the formerly terminal feedback calibration.

    Its c[2] did not affect any old output. c[0:2] remain fixed until joint
    fine-tuning. A fresh optimizer is used at each new depth, as in the parent.
    """
    old_hook = getattr(model, '_adaptation_hook', None)
    if old_hook is not None:
        old_hook.remove()
        model._adaptation_hook = None
    newest = len(model.layers) - 1
    boundary = f'layers.{newest-1}.calibration'
    for name, parameter in model.named_parameters():
        trainable = name in eligible and (not adaptation or
            name.startswith(f'layers.{newest}.') or name == boundary)
        parameter.requires_grad_(trainable)
        parameter.grad = None
    if adaptation:
        parameter = model.layers[-2].calibration
        model._adaptation_hook = parameter.register_hook(lambda gradient: gradient * gradient.new_tensor([0., 0., 1.]))


def make_optimizer(model, eligible):
    settings = CONFIG['receiver']
    named = dict(model.named_parameters())
    # Names, not the current phase's requires_grad flags, determine stable
    # optimizer groups and enable exact checkpoint resume across phase changes.
    groups = [dict(params=[p for n, p in named.items() if n in eligible and token in n], lr=rate)
              for token, rate in (('.score.', settings['learning_rate']),
                                  ('.activity.', settings['activity_learning_rate']))]
    groups.append(dict(params=[layer.calibration for layer in model.layers],
                       lr=settings['calibration_learning_rate']))
    return torch.optim.Adam(groups, foreach=False)


def validate(model, cases, depth, epoch, started):
    def progress(rows):
        if len(rows) % 64 == 0 or len(rows) == len(cases):
            status('RECEIVER_VALIDATION', depth=depth, epoch=epoch,
                   scenes=len(rows), total=len(cases), elapsed_seconds=time.time()-started)
    return evaluate(model, cases, started=started, on_row=progress)


def train_receiver(pretrained, scale, device, started):
    settings, specification = CONFIG['receiver'], CONFIG['depth_extension']
    parent_depth = specification['parent_depth']
    for split in ('train', 'validation'):
        build_cases(split, scale, started)
    training, validation = Cases('train', scale, device), Cases('validation', scale, device)
    model = Receiver()
    for _ in range(parent_depth):
        model.add_layer(None)
    parent = OUT / specification['parent_checkpoint']
    if sha(parent) != specification['parent_checkpoint_sha256']:
        raise ValueError('Parent checkpoint changed')
    model.load_state_dict(torch.load(parent, map_location='cpu', weights_only=False)['state'])
    model.to(device)
    for depth in range(parent_depth+1, settings['maximum_depth']+1):
        check_budget(started)
        append_trained_layer(model)
        eligible = eligible_parameters(model)
        folder = OUT/'checkpoints'/f'depth_{depth}'
        folder.mkdir(parents=True, exist_ok=True)
        maximum_epochs = settings['epoch_schedule'][depth-1]
        receipt = folder/'COMPLETE.json'
        if receipt.exists():
            saved = json.loads(receipt.read_text())
            if (saved['status'] != 'COMPLETE' or saved['steps'] != len(training)*maximum_epochs
                    or saved['checkpoint_sha256'] != sha(folder/'best.pt')):
                raise ValueError('Completed stage binding changed')
            model.load_state_dict(torch.load(folder/'best.pt', map_location=device, weights_only=False)['state'])
            continue
        optimizer = make_optimizer(model, eligible)
        epoch, cursor, steps, best, selected_epoch = 1, 0, 0, math.inf, 0
        history, loss_sum, samples = [], 0., 0
        resume = folder/'last.pt'
        if resume.exists():
            saved = torch.load(resume, map_location='cpu', weights_only=False)
            if saved['depth'] != depth:
                raise ValueError('Wrong resume depth')
            model.load_state_dict(saved['state'])
            optimizer.load_state_dict(saved['optimizer'])
            epoch, cursor, steps, best, selected_epoch, history, loss_sum, samples = (
                saved[k] for k in ('epoch', 'cursor', 'steps', 'best', 'selected_epoch', 'history', 'loss_sum', 'samples'))
            del saved
        configure_execution(model, optimizer, CONFIG['execution'], device)

        def checkpoint():
            save_torch(resume, dict(state=cpu_state(model), optimizer=optimizer.state_dict(), depth=depth,
                epoch=epoch, cursor=cursor, steps=steps, best=best, selected_epoch=selected_epoch,
                history=history, loss_sum=loss_sum, samples=samples,
                phase='ADAPTATION' if epoch == 1 else 'JOINT', inherited_updates=specification['inherited_updates']))
            save_json(OUT/'ACTIVE_TIME.json', dict(consumed_seconds=time.time()-started))

        try:
            if not history:
                result = validate(model, validation, depth, 0, started)
                best = result['summary']['loss']
                save_json(folder/'validation_epoch_0.json', result)
                save_json(folder/'initial_validation.json', result)
                save_json(folder/'best_validation.json', result)
                save_torch(folder/'best.pt', dict(state=cpu_state(model), depth=depth, scale=scale, epoch=0))
                history = [dict(epoch=0, validation=result['summary'], selected=True, phase='INITIALIZATION')]
                save_json(folder/'history.json', history)
                checkpoint()
            while epoch <= maximum_epochs:
                adaptation = epoch == 1
                set_phase(model, eligible, adaptation)
                model.train()
                order = epoch_order(training.indices, depth, epoch)
                while cursor < len(order):
                    check_budget(started)
                    optimizer.zero_grad(set_to_none=True)
                    public, labels, info = training[int(order[cursor])]
                    outputs, diagnostics = model(public)
                    value = loss(outputs, labels)
                    if not bool(torch.isfinite(value)):
                        raise FloatingPointError(f'Nonfinite loss: {info}')
                    value.backward()
                    norm = clip_gradient_norm(model.parameters(), 1.)
                    optimizer.step()
                    steps += 1; cursor += 1; samples += 1; loss_sum += float(value.detach())
                    if steps % settings['checkpoint_steps'] == 0 or steps == 1:
                        checkpoint()
                    if steps % 8 == 0 or steps == 1:
                        status('PROGRESSIVE_RECEIVER_TRAINING', depth=depth, epoch=epoch,
                            phase='ADAPTATION' if adaptation else 'JOINT', scene=cursor, total=len(order),
                            steps=steps, max_epochs=maximum_epochs, loss=float(value.detach()),
                            gradient_norm=float(norm), diagnostics=diagnostics, selected_epoch=selected_epoch,
                            best_validation_loss=best, gpu_memory_allocated_bytes=torch.cuda.memory_allocated(),
                            elapsed_seconds=time.time()-started)
                result = validate(model, validation, depth, epoch, started)
                save_json(folder/f'validation_epoch_{epoch}.json', result)
                score = result['summary']['loss']; selected = score < best
                if selected:
                    best = score; selected_epoch = epoch
                    save_torch(folder/'best.pt', dict(state=cpu_state(model), depth=depth, scale=scale, epoch=epoch))
                    save_json(folder/'best_validation.json', result)
                row = dict(epoch=epoch, phase='ADAPTATION' if adaptation else 'JOINT',
                           train_loss=loss_sum/samples, validation=result['summary'], selected=selected)
                history.append(row); save_json(folder/'history.json', history)
                log_event(dict(stage='RECEIVER_VALIDATION', depth=depth, **row))
                epoch += 1; cursor = 0; loss_sum = 0.; samples = 0
                checkpoint()
            if selected_epoch == 0:
                raise RuntimeError(f'Depth {depth} did not improve initialization; further expansion was not started')
            save_json(receipt, dict(status='COMPLETE', selected_epoch=selected_epoch, steps=steps,
                reason='FIXED_BUDGET_COMPLETED', best_validation_loss=best,
                checkpoint_sha256=sha(folder/'best.pt')))
        except BaseException:
            checkpoint()
            raise
        set_phase(model, eligible, False)
        model.load_state_dict(torch.load(folder/'best.pt', map_location=device, weights_only=False)['state'])
        del optimizer
    return model
