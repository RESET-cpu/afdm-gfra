"""Independent full-user score D-AMP receiver with a shared activity variable."""
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import time
import numpy as np
import torch

from afdm_jadcedd.project import ROOT
from afdm_jadcedd.system.observation import ReceiverInput, load_input
from afdm_jadcedd.algorithm.baselines.ldamp.representation import beam_transform
from afdm_jadcedd.utils import sha256, write_json
from .core import Controls, solve
from .denoiser import JointDenoiser

DEFAULT_CONFIG = ROOT/'configs/joint_amp.json'


def load_configuration(path=None):
    return json.loads(Path(path or DEFAULT_CONFIG).read_text())


def signature(configuration):
    paths = [Path(__file__).with_name(name) for name in ('network.py', 'denoiser.py', 'core.py', 'receiver.py')]
    paths += [ROOT/'src/afdm_jadcedd/algorithm/baselines/ldamp/representation.py',
              ROOT/'src/afdm_jadcedd/system/config.py',
              ROOT/'src/afdm_jadcedd/system/afdm/path_operator_multicycle_full.py']
    payload = {key: configuration[key] for key in
               ('schema', 'checkpoint_sha256', 'scale', 'solver', 'batch_size', 'decision_threshold')}
    payload['sources'] = {str(path.relative_to(ROOT)): sha256(path) for path in paths}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


class JointAMPReceiver:
    def __init__(self, configuration=None, *, device='auto'):
        self.configuration = c = deepcopy(configuration or load_configuration())
        if c['schema'] != 'afdm-joint-score-amp-v1':
            raise ValueError('Full-user score D-AMP configuration required')
        checkpoint = ROOT/c['checkpoint_path']
        if sha256(checkpoint) != c['checkpoint_sha256']:
            raise ValueError('Joint checkpoint identity mismatch')
        if not 0 < c['decision_threshold'] < 1:
            raise ValueError('A fixed probability decision threshold in (0,1) is required')
        self.device = ('mps' if torch.backends.mps.is_available() else 'cpu') if device == 'auto' else device
        self.denoise = JointDenoiser(checkpoint, device=self.device, batch_size=c['batch_size'])
        if self.denoise.scale != c['scale']:
            raise ValueError('Physical training/inference scale mismatch')
        self.signature = signature(c)

    def infer(self, inputs, *, observer=None):
        if not isinstance(inputs, ReceiverInput) or inputs.observation.shape[1:] != (16, 16):
            raise ValueError('Public AFDM ReceiverInput required')
        if not np.isfinite(inputs.activity_prior) or not 0 < inputs.activity_prior < 1:
            raise ValueError('Finite activity prior in (0,1) required')
        start = time.monotonic()
        before = (self.denoise.calls, self.denoise.direction_evaluations, self.denoise.network_batches)
        self.denoise.activity_prior = float(inputs.activity_prior)
        self.denoise.probabilities = None
        beam_observer = None if observer is None else lambda row, h: observer(row, beam_transform(h, inverse=True))
        result = solve(replace(inputs, observation=beam_transform(inputs.observation)), self.denoise,
            scale=self.configuration['scale'], controls=Controls(**self.configuration['solver']), observer=beam_observer)
        estimate = beam_transform(result.pop('estimate'), inverse=True)
        probability = result.pop('probabilities')
        arrays = {'estimate' if result['status'] == 'COMPLETE' else 'last_valid_estimate': estimate,
                  'channel_energy': np.sum(abs(estimate)**2, axis=(1, 2, 3))}
        if result['status'] == 'COMPLETE':
            arrays.update(probabilities=probability, activity_score=probability,
                          activity_decision=probability >= self.configuration['decision_threshold'])
        elif probability is not None:
            arrays['last_valid_probabilities'] = probability
        if self.device == 'mps':
            torch.mps.synchronize()
        record = dict(method='joint_amp', **result, seconds=time.monotonic()-start,
            configuration=self.configuration, inference_sha256=self.signature, device=self.device,
            denoiser_calls=self.denoise.calls-before[0],
            directional_derivative_evaluations=self.denoise.direction_evaluations-before[1],
            network_batches=self.denoise.network_batches-before[2],
            public_activity_prior=float(inputs.activity_prior), truth_used_in_inference=False,
            input_fields=list(ReceiverInput.__dataclass_fields__),
            activity_decision_available=result['status'] == 'COMPLETE',
            statistical_scope='Full-user conditional channel and shared activity; per-beam scalar Gaussian query approximation',
            derivative=('Actual pF map; paired real JVP; direct full ZB action using user-row directions'
                if self.configuration['solver'].get('correction_estimator', 'matrix') == 'user_row'
                else 'Actual pF map; paired real JVP; exact direct skip component plus full 256x256 remainder partial trace'),
            channel_output='Damped mean; no second probability multiplication or activity decision gating')
        return arrays, record

    def run(self, input_path, output_path, *, observer=None):
        out = Path(output_path)
        if out.suffix != '.npz' or out.exists() or out.with_suffix('.json').exists():
            raise ValueError('Fresh .npz output required')
        arrays, record = self.infer(load_input(input_path), observer=observer)
        out.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(out, **arrays)
        record.update(input_sha256=sha256(input_path), output_sha256=sha256(out))
        write_json(out.with_suffix('.json'), record)
        return record
