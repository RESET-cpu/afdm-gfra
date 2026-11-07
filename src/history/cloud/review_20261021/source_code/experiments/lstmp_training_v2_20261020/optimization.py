"""Independent calibration states and a uniform adaptation/joint schedule."""
import random
import numpy as np
import torch


def eligible_parameters(model):
    return {name for name, p in model.named_parameters() if p.requires_grad}


def set_phase(model, optimizer, eligible, epoch):
    newest = len(model.layers) - 1
    adaptation = epoch <= 1
    for name, p in model.named_parameters():
        index = int(name.split('.')[1])
        allowed = (not adaptation or index == newest or
                   name == f'layers.{newest-1}.c_beta')
        allowed = allowed and name != f'layers.{newest}.c_beta' and name in eligible
        p.requires_grad_(allowed)
        if not allowed:
            p.grad = None
    multiplier = 1. if adaptation else .1
    for group in optimizer.param_groups:
        group['lr'] = group['adaptation_lr'] * multiplier
    return 'ADAPTATION' if adaptation else 'JOINT'


def make_optimizer(model, settings, eligible, *, fused=False):
    groups = []
    rates = dict(score=settings['learning_rate'],
                 activity=settings['activity_learning_rate'],
                 calibration=settings['calibration_learning_rate'])
    for kind, lr in rates.items():
        params = [p for name, p in model.named_parameters()
                  if name in eligible and parameter_kind(name) == kind]
        groups.append(dict(params=params, name=kind, lr=lr, adaptation_lr=lr))
    return torch.optim.Adam(groups, betas=(.9, .999), eps=1e-8,
                            weight_decay=0., foreach=False, fused=fused)


def parameter_kind(name):
    return 'score' if '.score.' in name else 'activity' if '.activity.' in name else 'calibration'


def rng_state():
    return dict(python=random.getstate(), numpy=np.random.get_state(),
                torch=torch.get_rng_state(),
                cuda=torch.cuda.get_rng_state_all() if torch.cuda.is_available() else [])


def restore_rng(state):
    random.setstate(state['python'])
    np.random.set_state(state['numpy'])
    torch.set_rng_state(state['torch'].cpu())
    if state['cuda']:
        torch.cuda.set_rng_state_all([s.cpu() for s in state['cuda']])


def gradient_diagnostics(model, components):
    """Measured before clipping on fixed training cases, never on validation."""
    named = [(name, p) for name, p in model.named_parameters() if p.requires_grad]
    report = {}
    for loss_name in ('channel', 'activity'):
        gradients = torch.autograd.grad(components[loss_name], [p for _, p in named],
                                       retain_graph=True, allow_unused=True)
        groups = {}
        for (name, _), gradient in zip(named, gradients):
            key = f"{name.split('.')[1]}:{parameter_kind(name)}"
            entry = groups.setdefault(key, dict(squared_norm=0., connected_tensors=0,
                                                nonzero_tensors=0))
            if gradient is not None:
                norm = float(torch.linalg.vector_norm(gradient.detach(), dtype=torch.float64))
                entry['squared_norm'] += norm * norm
                entry['connected_tensors'] += 1
                entry['nonzero_tensors'] += int(norm > 0)
        report[loss_name] = {key: dict(norm=value.pop('squared_norm') ** .5, **value)
                             for key, value in groups.items()}
        del gradients
    return report
