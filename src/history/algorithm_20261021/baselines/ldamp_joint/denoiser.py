"""Portable frozen model and complete real directional derivatives."""
import json
from pathlib import Path
import numpy as np
import torch
from afdm_jadcedd.algorithm.baselines.ldamp.representation import Representation
from afdm_jadcedd.utils import sha256
from .model import JointDnCNN, unpack
from .residual_model import FrozenBeamBank
from .residual_noise_model import NoiseScaledResidualDnCNN
from .range_model import MeanAndBeamSelectedDnCNN


def verify_bundle(path):
    path = Path(path)
    spec = json.loads(path.read_text())
    if (spec['schema'] != 'afdm-joint-dncnn-bundle-v1'
            or spec['selection_scope'] != 'mean_and_beam'
            or not np.isfinite(spec['scale']) or spec['scale'] <= 0
            or not np.isfinite(spec['boundary']) or spec['boundary'] <= 0):
        raise ValueError('Invalid joint-denoiser bundle')
    for key in ('base', 'low', 'high'):
        if sha256(path.parent / spec[key]['path']) != spec[key]['sha256']:
            raise ValueError(f'Joint-denoiser {key} identity mismatch')
    bank_path = path.parent / spec['base']['path']
    bank = json.loads(bank_path.read_text())
    if not bank['complete'] or bank['scale'] != spec['scale'] or bank['representation'] != 'beam_time_lag_dft':
        raise ValueError('Incompatible frozen base bank')
    for entry in bank['entries']:
        if sha256(bank_path.parent / entry['path']) != entry['sha256']:
            raise ValueError('Frozen base checkpoint identity mismatch')
    return spec


class JointDenoiser:
    def __init__(self, path, *, device='cpu', double=False):
        path = Path(path)
        self.spec = spec = verify_bundle(path)
        bank = FrozenBeamBank((path.parent / spec['base']['path']).parent)
        low = torch.load(path.parent / spec['low']['path'], map_location='cpu', weights_only=True)
        high = torch.load(path.parent / spec['high']['path'], map_location='cpu', weights_only=True)
        if low['scale'] != spec['scale'] or high['scale'] != spec['scale']:
            raise ValueError('Inconsistent population normalization')
        for key, value in bank.state_dict().items():
            if not torch.equal(low['model']['bank.' + key], value):
                raise ValueError('Residual checkpoint changed the frozen base bank')
        low_model = NoiseScaledResidualDnCNN(low['power'], bank, low['width'], low['depth'])
        high_model = JointDnCNN(high['power'], high['mode'], high['width'], high['depth'])
        low_model.load_state_dict(low['model'])
        high_model.load_state_dict(high['model'])
        self.device = device
        self.dtype = torch.float64 if double else torch.float32
        self.scale = spec['scale']
        self.model = MeanAndBeamSelectedDnCNN(low_model, high_model, spec['boundary']).to(
            device=device, dtype=self.dtype).eval()
        for parameter in self.model.parameters():
            parameter.requires_grad_(False)
        self.representation = Representation()
        self.log = []

    def _pack(self, value):
        return torch.as_tensor(np.concatenate([value.real, value.imag], axis=-3),
                               device=self.device, dtype=self.dtype)

    @torch.no_grad()
    def linearize(self, query, covariance):
        if query.shape[1:] != (16, 16, 16):
            raise ValueError('Full AFDM user channel required')
        variance = np.diag(covariance).real.reshape(16, 16).mean(axis=1)
        if np.any(variance <= 0) or not np.isfinite(variance).all():
            raise ValueError('Positive public residual variance required')
        value = self._pack(self.representation.forward(query))
        v = torch.as_tensor(np.broadcast_to(variance, (len(query), 16)).copy(),
                            device=self.device, dtype=self.dtype)
        output, derivative = self.model.linearize(value, v)

        def directions(delta):
            result = derivative(self._pack(self.representation.forward(delta))).cpu().numpy()
            return self.representation.inverse(unpack(result))

        self.log.append(dict(variance=variance.tolist(), mean_variance=float(variance.mean()),
                             high_beams=int(self.model.masks(v)[1][0, :16].sum()),
                             outside_training_mean_range=bool(variance.mean() < .001 or variance.mean() > 1000)))
        return self.representation.inverse(unpack(output.cpu().numpy())), directions
