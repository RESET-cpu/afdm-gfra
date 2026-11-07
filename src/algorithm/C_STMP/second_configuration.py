"""Independent binding for the trained second-score variance candidate."""
from copy import deepcopy
from pathlib import Path
import torch

from project import ROOT
from utils import read_json, sha256
from .configuration import verify as verify_first


def verify(configuration):
    c = read_json(configuration) if isinstance(configuration, (str, Path)) else deepcopy(configuration)
    if (c.get('schema') != 'colored-stmp-second-candidate-v1'
            or c.get('variance_estimator') != {'kind': 'learned_second_score_trace'}):
        raise ValueError('Explicit learned second-score candidate required')
    common = deepcopy(c)
    common['schema'] = 'colored-stmp-candidate-v1'
    _, hashes = verify_first(common)
    digest = sha256(ROOT / c['second_checkpoint'])
    if digest != c['second_checkpoint_sha256']:
        raise ValueError('Candidate second checkpoint changed')
    second = torch.load(ROOT / c['second_checkpoint'], map_location='cpu', weights_only=False, mmap=True)
    first = torch.load(ROOT / c['first_checkpoint'], map_location='cpu', weights_only=False, mmap=True)
    if (second.get('schema') != 'colored-second-score-trace-v1'
            or second.get('order') != 2
            or second.get('output') != 'normalized_covariance_weighted_hessian_trace'
            or second.get('first_sha256') != hashes['first_checkpoint']
            or second.get('global_complex_rms') != c['scale']
            or second['metadata']['epoch'] != c['second_epoch']
            or second['config'] != first['config']):
        raise ValueError('Second score must match the frozen first and its coordinates')
    hashes['second_checkpoint'] = digest
    return c, hashes
