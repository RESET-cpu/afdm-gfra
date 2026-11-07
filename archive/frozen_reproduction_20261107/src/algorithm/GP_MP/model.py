"""Frozen conditional-mean network with strict white-training provenance.

Historical serialized schema and parameterization strings remain exact; they do
not describe this checkpoint's training covariance. Nonzero covariance strength
is rejected before a model is constructed.
"""
from copy import deepcopy
import math
import torch
from torch import nn
from networks.score import DirectCaiConfig, DirectCaiNetwork
from .operators import stable_residual

class CovarianceConditionedNetwork(nn.Module):
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


class PreconditionedMean(CovarianceConditionedNetwork):
    """Preserve CovarianceConditionedNetwork initialization; ``forward`` returns a denoised mean.

    For tau^2 = reference_real_variance and Sigma = real_embedding(C)/2,
    D(r,C) = K r + O F(B r,C), where B=(tau^2 I+Sigma)^(-1/2),
    K=tau^2/(tau^2+Sigma), and O=tau*sqrt(Sigma/(tau^2+Sigma)).
    F is the unchanged trunk output, with no scalar score normalization.
    """

    def __init__(self, base, reference_real_variance=.5):
        variance = float(reference_real_variance)
        if not math.isfinite(variance) or variance <= 0:
            raise ValueError('Positive finite reference real variance required')
        super().__init__(base)
        self.reference_real_variance = variance

    def raw(self, observation, covariance, spectral):
        """Evaluate F once using precomputed spectral tensors; capture-safe."""
        batch = len(observation)
        expected = (batch, 2, self.config.antennas, self.config.side, self.config.side)
        if tuple(observation.shape) != expected:
            raise ValueError('Expected real-packed [B,2,antenna,output,input] channel')
        scale = (self.reference_real_variance + spectral.variance_eigenvalues).rsqrt()
        preconditioned = spectral.apply(observation, scale)
        condition = self.backbone.condition(covariance.condition())
        packed = preconditioned.reshape(batch, 2*self.config.antennas,
                                        self.config.side, self.config.side)
        return self.backbone.trunk(packed, condition).reshape(expected)

    def from_raw(self, raw, observation, spectral):
        """Recover D from an already evaluated raw output, without another CNN call."""
        eigenvalues = spectral.variance_eigenvalues
        variance = self.reference_real_variance
        denominator = variance + eigenvalues
        gain = variance / denominator
        output_scale = (variance * eigenvalues / denominator).sqrt()
        return (spectral.apply(observation, gain)
                + spectral.apply(raw, output_scale))

    def mean(self, observation, covariance, spectral):
        raw = self.raw(observation, covariance, spectral)
        return self.from_raw(raw, observation, spectral)

    def forward(self, observation, covariance, spectral):
        return self.mean(observation, covariance, spectral)

    def score(self, observation, covariance, spectral):
        """Return Sigma^(-1)(D-r), using an algebraically stable expression."""
        raw = self.raw(observation, covariance, spectral)
        eigenvalues = spectral.variance_eigenvalues
        variance = self.reference_real_variance
        denominator = variance + eigenvalues
        scale = math.sqrt(variance) / (eigenvalues * denominator).sqrt()
        return (spectral.apply(raw, scale)
                - spectral.apply(observation, denominator.reciprocal()))

    def stable_residual(self, raw, clean, epsilon, spectral):
        return stable_residual(raw, clean, epsilon, spectral,
                               self.reference_real_variance)


def load_checkpoint(path, device='cpu'):
    """Load only the registered conditional-mean preconditioning parameterization."""
    blob = torch.load(path, map_location='cpu', weights_only=False)
    if (not isinstance(blob, dict)
            or blob.get('schema') != 'colored-preconditioned-first-v1'
            or blob.get('output') != 'conditional_mean'):
        raise ValueError('Expected a colored-preconditioned-first-v1 conditional-mean checkpoint')
    if blob.get('metadata', {}).get('noise', {}).get('max_strength') != 0.0:
        raise ValueError('A white-noise-trained checkpoint with max_strength=0 is required')
    parameters = blob.get('parameterization', {})
    if (not isinstance(parameters, dict)
            or parameters.get('reference_real_variance') != .5
            or parameters.get('output') != 'conditional_mean'
            or parameters.get('objective') != 'original_covariance_weighted_DSM'):
        raise ValueError('Unsupported covariance preconditioning parameterization')
    base = DirectCaiNetwork(DirectCaiConfig(**blob['config']), order=1)
    model = PreconditionedMean(base, reference_real_variance=.5)
    model.load_state_dict(blob['state_dict'], strict=True)
    return model.to(device).eval(), blob
