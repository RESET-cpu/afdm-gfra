"""Execution-only options: preserve Adam moments, scene order and objectives."""
import torch


def configure_execution(model, optimizer, settings, device):
    model.use_checkpoint = settings.get('activation_checkpointing', True)
    selective = settings.get('selective_checkpoint', {})
    depth = len(getattr(model, 'layers', []))
    model.checkpoint_first_layers = (selective.get('first_layers', 0)
        if depth >= selective.get('minimum_depth', 1) else 0)
    model.checkpoint_min_users = selective.get('minimum_users', 0)
    mode = settings.get('adam_implementation', 'single')
    if mode not in ('single', 'fused'):
        raise ValueError('Unknown Adam execution implementation')
    fused = mode == 'fused'
    if fused and torch.device(device).type != 'cuda':
        raise ValueError('The measured fused Adam execution requires CUDA')
    # Loading an older checkpoint restores its old group flags. Apply execution
    # options afterward and migrate only the step counter required by fused Adam;
    # parameter values, first/second moments and all Adam hyperparameters persist.
    for group in optimizer.param_groups:
        group['foreach'] = False
        group['fused'] = fused
        for parameter in group['params']:
            state = optimizer.state.get(parameter)
            if state and 'step' in state:
                state['step'] = state['step'].to(parameter.device if fused else 'cpu')
