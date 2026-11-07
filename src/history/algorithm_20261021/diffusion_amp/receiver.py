"""Standalone, public-input-only score D-AMP receiver and bound activity rule."""
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
from .denoiser import ScoreDenoiser

DEFAULT_CONFIG = ROOT/'configs/diffusion_amp.json'


def load_configuration(path=None):
    return json.loads(Path(path or DEFAULT_CONFIG).read_text())


def signature(configuration):
    c = configuration
    paths = [Path(__file__).with_name(name) for name in ('network.py', 'denoiser.py', 'core.py', 'receiver.py')]
    paths.append(ROOT/'src/afdm_jadcedd/algorithm/baselines/ldamp/representation.py')
    payload = {key: c[key] for key in ('schema', 'checkpoint_sha256', 'scale', 'solver', 'batch_size')}
    payload['sources'] = {str(p.relative_to(ROOT)): sha256(p) for p in paths}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


class DiffusionAMPReceiver:
    def __init__(self, configuration=None, *, device='auto'):
        self.configuration = c = deepcopy(configuration or load_configuration())
        if c['schema'] != 'afdm-diffusion-amp-v1':
            raise ValueError('Independent score D-AMP configuration required')
        checkpoint = ROOT/c['checkpoint_path']
        if sha256(checkpoint) != c['checkpoint_sha256']:
            raise ValueError('Score checkpoint identity mismatch')
        self.device = ('mps' if torch.backends.mps.is_available() else 'cpu') if device == 'auto' else device
        self.denoise = ScoreDenoiser(checkpoint, device=self.device, batch_size=c['batch_size'])
        if self.denoise.scale != c['scale']:
            raise ValueError('Physical training/inference scale mismatch')
        self.signature = signature(c)
        self.readout = None
        if c.get('readout'):
            binding = c['readout']
            path = ROOT/binding['path']
            if sha256(path) != binding['sha256']:
                raise ValueError('Activity readout identity mismatch')
            self.readout = json.loads(path.read_text())
            if self.readout['inference_sha256'] != self.signature:
                raise ValueError('Activity threshold belongs to another receiver')

    def infer(self, inputs, *, observer=None):
        if not isinstance(inputs, ReceiverInput) or inputs.observation.shape[1:] != (16, 16):
            raise ValueError('Public AFDM ReceiverInput required')
        start = time.monotonic()
        before = (self.denoise.calls, self.denoise.direction_evaluations, self.denoise.network_batches)
        self.denoise.noise_log = []
        beam_observer = None if observer is None else lambda row, h: observer(row, beam_transform(h, inverse=True))
        result = solve(replace(inputs, observation=beam_transform(inputs.observation)), self.denoise,
            scale=self.configuration['scale'], controls=Controls(**self.configuration['solver']), observer=beam_observer)
        estimate = beam_transform(result.pop('estimate'), inverse=True)
        energy = np.sum(abs(estimate)**2, axis=(1, 2, 3))
        arrays = {'estimate' if result['status'] == 'COMPLETE' else 'last_valid_estimate': estimate,
                  'channel_energy': energy, 'activity_score': energy}
        if result['status'] == 'COMPLETE' and self.readout is not None:
            arrays['activity_decision'] = (energy >= self.readout['threshold']) & (energy > 0)
        record = dict(method='diffusion_amp', **result, seconds=time.monotonic()-start,
            configuration=self.configuration, inference_sha256=self.signature, device=self.device,
            denoiser_calls=self.denoise.calls-before[0],
            directional_derivative_evaluations=self.denoise.direction_evaluations-before[1],
            network_batches=self.denoise.network_batches-before[2],
            training_activity_probability=self.denoise.activity_probability,
            public_activity_prior=float(inputs.activity_prior),
            activity_decision_available='activity_decision' in arrays,
            truth_used_in_inference=False, input_fields=list(ReceiverInput.__dataclass_fields__),
            statistical_scope='Per-beam marginal prior; scalar noise within a beam, not a claim of joint AWGN',
            derivative='Forward automatic differentiation, paired Wirtinger directions, block partial traces')
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
