"""Explicit entry points for research receivers outside the selected comparison."""

ALGORITHMS = ('em',)


def build_receiver(algorithm, *, config=None, device='auto'):
    if algorithm not in ALGORITHMS:
        raise ValueError('Select one research algorithm: '+', '.join(ALGORITHMS))
    from .baselines.receiver import BaselineReceiver, load_configuration
    return BaselineReceiver(load_configuration(config), algorithm)
