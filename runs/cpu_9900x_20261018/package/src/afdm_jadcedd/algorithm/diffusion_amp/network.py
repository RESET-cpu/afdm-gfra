"""Continuous-noise denoising score model for one complex AFDM beam.

The network is trained from scratch on the activity-masked channel prior. It
uses the denoiser preconditioning of Karras et al. (2022), Table 1. In the real
two-channel representation, complex AWGN variance v means sigma**2 = v/2.
The score is (D_theta(r, v) - r)/(v/2), so a weighted denoising MSE is exactly a
weighted denoising score-matching objective. This module is a diffusion prior;
calling its conditional mean once is not a reverse-diffusion sampler.
"""
from pathlib import Path
import math

import torch
from torch import nn


class ConditionalResidualBlock(nn.Module):
    """A sample-local residual block with continuous noise conditioning."""

    def __init__(self, width: int, embedding: int):
        super().__init__()
        self.conv1 = nn.Conv2d(width, width, 3, padding=1)
        self.conv2 = nn.Conv2d(width, width, 3, padding=1)
        self.affine = nn.Linear(embedding, 2 * width)
        nn.init.zeros_(self.affine.weight)
        nn.init.zeros_(self.affine.bias)

    def forward(self, value, embedding):
        hidden = self.conv1(torch.nn.functional.silu(value))
        scale, shift = self.affine(embedding).chunk(2, dim=1)
        hidden = hidden * (1 + scale[:, :, None, None]) + shift[:, :, None, None]
        hidden = self.conv2(torch.nn.functional.silu(hidden))
        return (value + hidden) / math.sqrt(2)


class BeamScoreDenoiser(nn.Module):
    """Map B x 2 x 16 x 16 observations and B complex variances to means.

    All inputs/outputs use the same frozen population-normalized beam and
    time-lag-DFT coordinates. The caller owns these fixed unitary transforms.
    There is no mixing between samples or between beams, and no batch
    statistics. Variances are fixed conditioning arguments when differentiating
    the denoiser for Onsager correction. The module does not silently clip v.
    """

    def __init__(self, width=48, blocks=4, embedding=64, fourier_features=16,
                 sigma_data=math.sqrt(.05), noise_min=.001, noise_max=100.):
        super().__init__()
        self.configuration = dict(width=width, blocks=blocks, embedding=embedding,
            fourier_features=fourier_features, sigma_data=float(sigma_data),
            noise_min=float(noise_min), noise_max=float(noise_max))
        self.sigma_data = float(sigma_data)
        self.noise_min, self.noise_max = float(noise_min), float(noise_max)
        self.register_buffer('frequencies', torch.exp(torch.linspace(
            math.log(.5), math.log(16.), fourier_features // 2)))
        self.noise_embedding = nn.Sequential(
            nn.Linear(fourier_features + 1, embedding), nn.SiLU(),
            nn.Linear(embedding, embedding), nn.SiLU())
        self.input = nn.Conv2d(2, width, 3, padding=1)
        self.blocks = nn.ModuleList([
            ConditionalResidualBlock(width, embedding) for _ in range(blocks)])
        self.output = nn.Conv2d(width, 2, 3, padding=1)
        # This is a prescribed initialization, not a loaded learned checkpoint.
        # The initial mean is the Gaussian linear-MMSE preconditioning term.
        nn.init.zeros_(self.output.weight)
        nn.init.zeros_(self.output.bias)

    def _variance(self, noisy, complex_variance):
        if noisy.ndim != 4 or noisy.shape[1:] != (2, 16, 16):
            raise ValueError('Expected B x 2 x 16 x 16 real coordinates')
        variance = torch.as_tensor(complex_variance, dtype=noisy.dtype,
                                   device=noisy.device)
        if variance.ndim == 0:
            variance = variance.expand(noisy.shape[0])
        if variance.shape != (noisy.shape[0],):
            raise ValueError('One complex variance per sample is required')
        return variance

    def forward(self, noisy, complex_variance):
        variance = self._variance(noisy, complex_variance)
        sigma2 = variance / 2
        data2 = self.sigma_data ** 2
        c_skip = data2 / (sigma2 + data2)
        c_out = torch.sqrt(sigma2 * data2 / (sigma2 + data2))
        c_in = torch.rsqrt(sigma2 + data2)
        c_noise = torch.log(sigma2) / 8  # log(sigma)/4, EDM Table 1.
        angles = c_noise[:, None] * self.frequencies[None, :]
        condition = torch.cat((c_noise[:, None], angles.sin(), angles.cos()), dim=1)
        embedding = self.noise_embedding(condition)
        hidden = self.input(c_in[:, None, None, None] * noisy)
        for block in self.blocks:
            hidden = block(hidden, embedding)
        residual = self.output(torch.nn.functional.silu(hidden))
        return (c_skip[:, None, None, None] * noisy
                + c_out[:, None, None, None] * residual)

    def score(self, noisy, complex_variance):
        variance = self._variance(noisy, complex_variance)
        return (self(noisy, variance) - noisy) / (variance[:, None, None, None] / 2)

    def loss_weight(self, complex_variance):
        """EDM weighting lambda(sigma) = 1/sigma**2 + 1/sigma_data**2."""
        return 2 / complex_variance + 1 / self.sigma_data ** 2


def load_checkpoint(path, *, device='cpu'):
    """Return (evaluation-mode model, metadata) without loading other weights."""
    payload = torch.load(Path(path), map_location='cpu', weights_only=True)
    if payload.get('schema') != 'afdm-continuous-score-checkpoint-v1':
        raise ValueError('Unexpected diffusion-AMP checkpoint schema')
    model = BeamScoreDenoiser(**payload['network'])
    model.load_state_dict(payload['model'])
    return model.to(device).eval(), payload
