"""Reuse the frozen first-score architecture, expanding only its conditioner."""
from copy import deepcopy

import torch
from torch import nn
from networks.score import DirectCaiNetwork


class ColoredScore(nn.Module):
    def __init__(self, base):
        super().__init__()
        if not isinstance(base, DirectCaiNetwork) or base.order != 1:
            raise ValueError('A continuous first-order DirectCaiNetwork is required')
        self.config = base.config
        self.backbone = deepcopy(base.network)
        old = self.backbone.condition[0]
        size = 1 + 2*(self.config.antennas**2 + self.config.side**2)
        new = nn.Linear(size, old.out_features, device=old.weight.device,
                        dtype=old.weight.dtype)
        with torch.no_grad():
            new.weight.zero_()
            new.weight[:, :1].copy_(old.weight)
            new.bias.copy_(old.bias)
        self.backbone.condition[0] = new

    def forward(self, observation, covariance):
        batch = len(observation)
        expected = (batch, 2, self.config.antennas, self.config.side, self.config.side)
        if tuple(observation.shape) != expected:
            raise ValueError('Expected real-packed [B,2,antenna,output,input] channel')
        condition = self.backbone.condition(covariance.condition())
        packed = observation.reshape(batch, 2*self.config.antennas,
                                     self.config.side, self.config.side)
        score = self.backbone.trunk(packed, condition).reshape(expected)
        return score / (covariance.variance[:, None, None, None, None]/2).sqrt()
