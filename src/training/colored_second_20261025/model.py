"""Learn the second-score contraction needed for a scalar variance message.

Real coordinates: u = tr(Sigma S2 Sigma) / tr(Sigma), S2 = Hessian log p(r|C).
The conditional variance per complex coordinate is nu*(1+u), nu=tr(Sigma)/N.
Only this contraction is supervised; individual Hessian entries are not identified.
See paper/docs/C_STMP_DERIVATION_20261024.md, section 8.
"""
from copy import deepcopy

import torch
from torch import nn

from networks.score import DirectCaiConfig, DirectCaiNetwork


def noise_power(spectral):
    # Each antenna/input eigenvalue repeats on the output axis and real/imag axes.
    return 2 * spectral.variance_eigenvalues.flatten(1).mean(1)


def conditional_error(mean, clean):
    """One realization of error power per COMPLEX coordinate, not true covariance."""
    return 2 * (mean.detach() - clean).square().flatten(1).mean(1)


def trace_loss(normalized_trace, mean, clean, spectral):
    """Cai trace matching with Sigma on both sides; square after the trace.

    With finite frozen mean, the population optimum reads out conditional risk.
    In the vI case this equals direct_second_loss with u=(v/2)*mean(S2).
    """
    target = conditional_error(mean, clean) / noise_power(spectral) - 1
    return (normalized_trace - target).square().mean()


def variance_from_trace(normalized_trace, spectral):
    """Raw variance readout; do not hide negative predictions by clipping."""
    return noise_power(spectral) * (1 + normalized_trace)


class ColoredSecondScore(nn.Module):
    """Independent original second RefineNet, C conditioner and scaled input.

    The trunk's map is pooled to one dimensionless weighted Hessian trace.
    Its pixels are latent outputs, not claims of separately learned diagonals.
    No first-network parameters or features are shared.
    """
    def __init__(self, base, reference_real_variance=.5):
        super().__init__()
        if not isinstance(base, DirectCaiNetwork) or base.order != 2:
            raise ValueError('Original independent second-order initializer required')
        self.config = base.config
        self.reference_real_variance = float(reference_real_variance)
        if self.reference_real_variance <= 0:
            raise ValueError('Positive reference real variance required')
        self.backbone = deepcopy(base.network)
        old = self.backbone.condition[0]
        size = 1 + 2*(self.config.antennas**2 + self.config.side**2)
        new = nn.Linear(size, old.out_features, device=old.weight.device, dtype=old.weight.dtype)
        with torch.no_grad():
            new.weight.zero_()
            new.weight[:, :1].copy_(old.weight)
            new.bias.copy_(old.bias)
        self.backbone.condition[0] = new

    def forward(self, observation, covariance, spectral):
        batch = len(observation)
        expected = (batch, 2, self.config.antennas, self.config.side, self.config.side)
        if tuple(observation.shape) != expected:
            raise ValueError('Expected real-packed channel query')
        scaled = spectral.apply(observation,
            (self.reference_real_variance + spectral.variance_eigenvalues).rsqrt())
        condition = self.backbone.condition(covariance.condition())
        output = self.backbone.trunk(scaled.reshape(batch, 2*self.config.antennas,
                                                    self.config.side, self.config.side), condition)
        return output.flatten(1).mean(1)


def load_checkpoint(path, device='cpu', *, first_sha256=None):
    blob = torch.load(path, map_location='cpu', weights_only=False)
    if (blob.get('schema') != 'colored-second-score-trace-v1' or blob.get('order') != 2
            or blob.get('output') != 'normalized_covariance_weighted_hessian_trace'):
        raise ValueError('Expected independent colored second-score trace checkpoint')
    if first_sha256 is not None and blob['first_sha256'] != first_sha256:
        raise ValueError('Second score was trained for a different frozen first')
    model = ColoredSecondScore(DirectCaiNetwork(DirectCaiConfig(**blob['config']), order=2),
                              blob['reference_real_variance'])
    model.load_state_dict(blob['state_dict'], strict=True)
    return model.to(device).eval(), blob
