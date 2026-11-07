"""Joint-user denoising mean and activity density ratio in fixed coordinates.

For a fixed diagonal real noise covariance T, the mixture score is
T^{-1}(p F-r). F estimates E[x|r,a=1,T], while a classifier trained with equal
class weights estimates log p(r|a=1,T)/p(r|a=0,T). The receiver supplies its
public activity prior. There is no cross-user operation or batch statistic.
"""
from pathlib import Path
import math

import torch
from torch import nn
from torch.nn import functional as functional


class ConditionalResidualBlock(nn.Module):
    def __init__(self, width, embedding):
        super().__init__()
        self.conv1 = nn.Conv2d(width, width, 3, padding=1)
        self.conv2 = nn.Conv2d(width, width, 3, padding=1)
        self.affine = nn.Linear(embedding, 2 * width)
        nn.init.zeros_(self.affine.weight)
        nn.init.zeros_(self.affine.bias)

    def forward(self, value, embedding):
        hidden = self.conv1(functional.silu(value))
        scale, shift = self.affine(embedding).chunk(2, dim=1)
        hidden = hidden * (1 + scale[:, :, None, None]) + shift[:, :, None, None]
        hidden = self.conv2(functional.silu(hidden))
        return (value + hidden) / math.sqrt(2)


class JointScoreNetwork(nn.Module):
    """B x 2 x 16 x 16 x 16 real coordinates; B x 16 complex variances.

    The second and third axes are real/imaginary and beam, respectively. The
    two spatial axes are the invertible time-lag-DFT representation. The
    population scale and all fixed transforms are owned by the caller.
    Variance and activity prior are held fixed during Onsager differentiation.
    Neither probability nor the conditional mean is detached from the input.
    """
    def __init__(self, width=96, blocks=4, embedding=128, fourier_features=8,
                 sigma_data=math.sqrt(.5), noise_min=.001, noise_max=100.):
        super().__init__()
        self.configuration = dict(width=int(width), blocks=int(blocks),
            embedding=int(embedding), fourier_features=int(fourier_features),
            sigma_data=float(sigma_data), noise_min=float(noise_min), noise_max=float(noise_max))
        self.sigma_data = float(sigma_data)
        self.noise_min, self.noise_max = float(noise_min), float(noise_max)
        self.register_buffer('frequencies', torch.exp(torch.linspace(
            math.log(.5), math.log(16.), fourier_features // 2)))
        self.noise_embedding = nn.Sequential(
            nn.Linear(16 * (fourier_features + 1), embedding), nn.SiLU(),
            nn.Linear(embedding, embedding), nn.SiLU())
        self.input = nn.Conv2d(32, width, 3, padding=1)
        self.blocks = nn.ModuleList([ConditionalResidualBlock(width, embedding) for _ in range(blocks)])
        self.output = nn.Conv2d(width, 32, 3, padding=1)
        self.activity = nn.Sequential(nn.Linear(2 * width + 16 + embedding, embedding),
            nn.SiLU(), nn.Linear(embedding, 1))
        nn.init.zeros_(self.output.weight)
        nn.init.zeros_(self.output.bias)
        nn.init.zeros_(self.activity[-1].weight)
        nn.init.zeros_(self.activity[-1].bias)

    def _variance(self, noisy, variance):
        if noisy.ndim != 5 or noisy.shape[1:] != (2, 16, 16, 16):
            raise ValueError('Expected B x 2 x 16 x 16 x 16 coordinates')
        value = torch.as_tensor(variance, dtype=noisy.dtype, device=noisy.device)
        if value.ndim == 0:
            value = value.expand(noisy.shape[0], 16)
        elif value.shape == (16,):
            value = value[None].expand(noisy.shape[0], 16)
        if value.shape != (noisy.shape[0], 16):
            raise ValueError('Expected one complex variance per user and beam')
        return value

    def components(self, noisy, variance, activity_prior):
        variance = self._variance(noisy, variance)
        tau, q = variance / 2, self.sigma_data ** 2
        c_skip = q / (tau + q)
        c_out = torch.sqrt(tau * q / (tau + q))
        c_in = torch.rsqrt(tau + q)
        c_noise = torch.log(tau) / 8
        angles = c_noise[:, :, None] * self.frequencies[None, None]
        condition = torch.cat((c_noise[:, :, None], angles.sin(), angles.cos()), dim=2)
        embedding = self.noise_embedding(condition.flatten(1))
        standardized = noisy * c_in[:, None, :, None, None]
        hidden = self.input(standardized.flatten(1, 2))
        for block in self.blocks:
            hidden = block(hidden, embedding)
        features = functional.silu(hidden)
        residual = self.output(features).reshape_as(noisy)
        conditional_mean = (c_skip[:, None, :, None, None] * noisy
            + c_out[:, None, :, None, None] * residual)
        energy = standardized.square().mean(dim=(1, 3, 4))
        pooled = torch.cat((features.mean(dim=(2, 3)), features.square().mean(dim=(2, 3)),
                            energy, embedding), dim=1)
        log_likelihood_ratio = self.activity(pooled).squeeze(1)
        prior = torch.as_tensor(activity_prior, dtype=noisy.dtype, device=noisy.device)
        if prior.ndim == 0:
            prior = prior.expand(noisy.shape[0])
        if prior.shape != (noisy.shape[0],):
            raise ValueError('Expected scalar or one activity prior per user')
        probability = torch.sigmoid(torch.logit(prior) + log_likelihood_ratio)
        mean = probability[:, None, None, None, None] * conditional_mean
        return dict(conditional_mean=conditional_mean, log_likelihood_ratio=log_likelihood_ratio,
                    probability=probability, mean=mean)

    def forward(self, noisy, variance, activity_prior):
        return self.components(noisy, variance, activity_prior)['mean']

    def score(self, noisy, variance, activity_prior):
        variance = self._variance(noisy, variance)
        return (self(noisy, variance, activity_prior) - noisy) / (variance[:, None, :, None, None] / 2)

    def loss_weight(self, variance):
        """Active conditional clean-MSE weight 1/c_out^2, per beam."""
        return 2 / variance + 1 / self.sigma_data ** 2


def load_checkpoint(path, device='cpu'):
    """Return evaluation-mode model and complete checkpoint metadata."""
    payload = torch.load(Path(path), map_location='cpu', weights_only=True)
    if payload.get('schema') != 'afdm-joint-score-checkpoint-v1':
        raise ValueError('Unexpected joint score checkpoint schema')
    model = JointScoreNetwork(**payload['network'])
    model.load_state_dict(payload['state_dict'])
    return model.to(device).eval(), payload
