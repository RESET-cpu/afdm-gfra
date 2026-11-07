"""Cai's NCSNv2/NCSN scores, with AFDM antennas packed as feature channels.

Backbone definitions for first- and second-order denoising score matching.
"""
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch
from torch import nn

from .cai_models.ncsn_channel_diffusion import NCSN



@dataclass(frozen=True)
class DirectCaiConfig:
    antennas: int = 16
    side: int = 16
    base_channels: int = 128
    snr_db_min: int = -10
    snr_db_max: int = 30
    noise_conditioning: str = 'continuous'
    input_transform: str = 'legacy_image'

    def __post_init__(self):
        if (type(self.snr_db_min) is not int or type(self.snr_db_max) is not int
                or self.snr_db_min >= self.snr_db_max):
            raise ValueError('integer SNR endpoints in increasing order required')
        if self.noise_conditioning != 'continuous':
            raise ValueError('unknown noise conditioning')
        if self.input_transform not in ('legacy_image', 'identity'):
            raise ValueError('unknown score input transform')


class ContinuousCaiBackbone(nn.Module):
    """Cai's conditional RefineNet with smooth log-variance conditioning.

    Every conditional normalization receives features from a shared noise MLP.
    There are no class embeddings, rounded labels or noise lookup in this path.
    Both orders use the conditional trunk; order one retains 1/sigma scaling.
    """
    def __init__(self, settings, *, order):
        super().__init__()
        self.order = order
        self.condition = nn.Sequential(nn.Linear(1, 64), nn.SiLU(), nn.Linear(64, 64), nn.SiLU())
        self.trunk = NCSN(settings)
        from .cai_models.normalization import ConditionalInstanceNorm2dPlus
        for module in self.trunk.modules():
            if isinstance(module, ConditionalInstanceNorm2dPlus):
                width = module.num_features
                projection = nn.Linear(64, width*(3 if module.bias else 2))
                nn.init.normal_(projection.weight, std=.02)
                with torch.no_grad():
                    projection.bias[:2*width].fill_(1.)
                    projection.bias[2*width:].zero_()
                module.embed = projection

    def forward(self, x, complex_variance):
        condition = self.condition(torch.log(complex_variance)[:, None]/5.)
        score = self.trunk(x, condition)
        if self.order == 1:
            score = score/torch.sqrt(complex_variance[:, None, None, None]/2)
        return score


class DirectCaiNetwork(nn.Module):
    def __init__(self, config=DirectCaiConfig(), *, order=1):
        super().__init__()
        if order not in (1, 2):
            raise ValueError('score order must be one or two')
        self.config, self.order = config, order
        settings = SimpleNamespace(
            data=SimpleNamespace(channels=2*config.antennas, image_size=config.side,
                                 logit_transform=False, rescaled=config.input_transform == 'identity'),
            model=SimpleNamespace(ngf=config.base_channels,
                num_classes=config.snr_db_max-config.snr_db_min+1,
                normalization='InstanceNorm++', nonlinearity='elu', spec_norm=False,
                snr_db_begin=config.snr_db_min, snr_db_end=config.snr_db_max, sigma_dist='geometric'),
            var_h_element=.5, device='cpu')
        settings.model.num_classes = 1
        self.network = ContinuousCaiBackbone(settings, order=order)

    def forward(self, observation, labels):
        expected = (len(observation), 2, self.config.antennas, self.config.side, self.config.side)
        if tuple(observation.shape) != expected or tuple(labels.shape) != (len(observation),):
            raise ValueError('direct Cai AFDM score shape mismatch')
        if self.config.noise_conditioning == 'continuous':
            if not labels.is_floating_point() or not bool(torch.all(torch.isfinite(labels) & (labels > 0))):
                raise ValueError('continuous scores require actual positive complex variances')
        packed = observation.reshape(len(observation), 2*self.config.antennas,
                                     self.config.side, self.config.side)
        return self.network(packed, labels).reshape(expected)


def load_direct_checkpoint(path, device='cpu'):
    checkpoint = torch.load(path, map_location='cpu', weights_only=False)
    if checkpoint.get('schema') == 'afdm-channel-unit-power-score-v1':
        from .channel_score import ChannelScoreConfig, ChannelScoreNetwork
        if checkpoint.get('normalization') != 'per_sample_power':
            raise ValueError('score schema and normalization disagree')
        model = ChannelScoreNetwork(ChannelScoreConfig(**checkpoint['config']), order=checkpoint['order'])
    elif checkpoint.get('schema') == 'afdm-cai-direct-score-v1':
        model = DirectCaiNetwork(DirectCaiConfig(**checkpoint['config']), order=checkpoint['order'])
    else:
        raise ValueError('expected direct Cai score checkpoint')
    model.load_state_dict(checkpoint['state_dict'])
    return model.to(device).eval(), checkpoint
