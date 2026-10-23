"""Separate entry retaining the same complete frozen joint denoiser."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import time
import torch
from afdm_jadcedd.project import ROOT
from afdm_jadcedd.utils import sha256
from afdm_jadcedd.algorithm.score_amp.denoiser import FrozenJointDenoiser
from afdm_jadcedd.algorithm.score_amp.receiver import ScoreAMPReceiver
from .core import QueryDampedControls, solve

DEFAULT_CONFIG = ROOT/'configs/proposed_amp_query_damped.json'


def load_configuration(path=None):
    return json.loads(Path(path or DEFAULT_CONFIG).read_text())


class QueryDampedScoreAMPReceiver(ScoreAMPReceiver):
    def __init__(self, configuration=None, *, device='auto'):
        self.configuration = c = deepcopy(configuration or load_configuration())
        if c['schema'] != 'afdm-frozen-score-query-damped-matrix-amp-v1' or c['decision_threshold'] != .5:
            raise ValueError('Query-damped frozen-score matrix AMP configuration required')
        self.controls = QueryDampedControls(**c['solver'])
        self.device = ('mps' if torch.backends.mps.is_available() else 'cpu') if device == 'auto' else device
        self.denoiser = FrozenJointDenoiser(c['networks'], device=self.device, batch_size=c['batch_size'])
        paths = sorted(Path(__file__).parent.glob('*.py'))
        for name in ('score_amp', 'score_amp_damped'):
            paths += sorted((Path(__file__).parent.parent/name).glob('*.py'))
        paths += [ROOT/'src/afdm_jadcedd/algorithm/proposed'/name for name in ('network.py', 'activity.py')]
        paths += sorted((ROOT/'src/afdm_jadcedd/algorithm/proposed/cai_models').glob('*.py'))
        payload = dict(configuration=c, sources={str(p.relative_to(ROOT)):sha256(p) for p in paths})
        self.signature = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    def infer(self, inputs, *, observer=None):
        before = (self.denoiser.evaluations, self.denoiser.samples,
                  self.denoiser.first_batches, self.denoiser.activity_batches)
        started = time.monotonic()
        result = solve(inputs, self.denoiser, scale=self.denoiser.scale,
                       controls=self.controls, observer=observer)
        if self.device == 'mps':
            torch.mps.synchronize()
        arrays = {key:result.pop(key) for key in
                  ('estimate', 'denoised_estimate', 'probabilities', 'conditional_matrix')}
        arrays['activity_decision'] = arrays['probabilities'] >= self.configuration['decision_threshold']
        result.update(method='score_amp_query_damped', device=self.device, configuration=deepcopy(self.configuration),
            inference_sha256=self.signature, seconds=time.monotonic()-started,
            joint_denoiser_evaluations=self.denoiser.evaluations-before[0],
            first_score_samples=self.denoiser.samples-before[1],
            first_score_calls=self.denoiser.first_batches-before[2],
            classifier_calls=self.denoiser.activity_batches-before[3], second_score_calls=0,
            input_fields=['observation', 'operator', 'noise_variance', 'activity_prior'],
            truth_used_in_inference=False,
            variance_interface='Power of residuals mixed with the query history weights, including cross terms',
            statistical_status='Explicit AFDM adaptation; no AFDM state evolution or convergence guarantee')
        return arrays, result
