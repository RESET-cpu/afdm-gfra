"""The accepted first-order backbone, initialized before loading fixed weights."""
from networks.score import DirectCaiConfig
from networks.score import DirectCaiNetwork
from receiver.du.configuration import CONFIG


def make_score():
    settings = CONFIG['backbone']
    if settings['kind'] != 'direct_cai':
        raise ValueError('The final model requires its selected direct_cai backbone')
    return DirectCaiNetwork(DirectCaiConfig(**settings['config']), order=1)
