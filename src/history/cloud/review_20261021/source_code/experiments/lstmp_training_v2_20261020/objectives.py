"""Equations T4, T5 and T8 in docs/LSTMP_TRAINING_PROTOCOL_20261020_V2.md."""
import torch
from torch.nn import functional as F


def layer_terms(output, labels, statistics):
    active = labels['active'].to(output['conditional'].dtype)
    mask = active.reshape(-1, *([1] * (labels['x'].ndim - 1)))
    channel = ((output['conditional'] - labels['x']).square() * mask).sum()
    activity = F.binary_cross_entropy_with_logits(
        output['logits'], labels['active'], reduction='sum')
    return (channel / statistics['mean_scene_energy'],
            activity / statistics['mean_users_per_scene'])


def loss_components(outputs, labels, statistics, earlier_weight=.2):
    terms = [layer_terms(output, labels, statistics) for output in outputs]
    weights = [earlier_weight] * (len(terms) - 1) + [1.]
    denominator = sum(weights)
    channel = sum(w * term[0] for w, term in zip(weights, terms)) / denominator
    activity = sum(w * term[1] for w, term in zip(weights, terms)) / denominator
    return dict(channel=channel, activity=activity, total=channel + activity,
                selection=terms[-1][0] + terms[-1][1])


def selected_epoch(history):
    return min(history, key=lambda row: (row['selection_loss'], row['epoch']))['epoch']


def assign_gradients(model, components, *, bce_updates_score=True):
    """T9 in the main arm; T10 is available only for the specified control.

    Do not detach conditional means: BCE also reaches earlier scores through
    messages, and later channel losses reach earlier activity heads.
    """
    if bce_updates_score:
        components['total'].backward()
        return
    named = [(n, p) for n, p in model.named_parameters() if p.requires_grad]
    parameters = [p for _, p in named]
    channel = torch.autograd.grad(components['channel'], parameters,
                                  retain_graph=True, allow_unused=True)
    activity = torch.autograd.grad(components['activity'], parameters, allow_unused=True)
    for (name, parameter), gh, ga in zip(named, channel, activity):
        if '.score.' in name:
            parameter.grad = gh
        elif gh is None:
            parameter.grad = ga
        elif ga is None:
            parameter.grad = gh
        else:
            parameter.grad = gh + ga
