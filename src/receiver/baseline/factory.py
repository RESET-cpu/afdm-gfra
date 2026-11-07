"""Construct baseline receivers for an explicitly supplied noise variance."""

from receiver.baseline._base import EstimatedNoiseBaselineReceiver


def known_noise_baseline(method, *, config=None, device='cpu'):
    """Use the native solver without its noise-estimation frontend."""
    return EstimatedNoiseBaselineReceiver(method, config=config, device=device).base
