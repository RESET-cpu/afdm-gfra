"""Proper complex separable noise in [antenna, output, input] C order.

Project derivation: see paper/docs/COLORED_SCORE_TRAINING_20261024.md.
No 4096 x 4096 covariance is materialized by the training path.
"""
from dataclasses import dataclass
import math

import numpy as np
import torch


def pack(z):
    return torch.stack((z.real, z.imag), dim=1)


def unpack(x):
    return torch.complex(x[:, 0], x[:, 1])


def hermitian_power(matrix, power):
    values, vectors = torch.linalg.eigh(matrix)
    if not bool(torch.all(torch.isfinite(values) & (values > 0))):
        raise ValueError('Positive definite covariance required; no eigenvalue clipping')
    return (vectors * values.pow(power).unsqueeze(-2)) @ vectors.mH


@dataclass
class Covariance:
    variance: torch.Tensor
    antenna: torch.Tensor
    column: torch.Tensor

    def to(self, device):
        return Covariance(*(x.to(device) for x in (self.variance, self.antenna, self.column)))

    def apply_complex(self, x, power=1.):
        """Apply C**power; right tensor factor is transposed, NOT adjointed."""
        if power == 1:
            a, c = self.antenna, self.column
        else:
            a, c = hermitian_power(self.antenna, power), hermitian_power(self.column, power)
        y = torch.einsum('baj,bjok,bik->baoi', a, x, c)
        return y * self.variance.pow(power)[:, None, None, None]

    def apply_real(self, x, power=1.):
        # Sigma = real_embedding(C)/2, and real_embedding respects powers.
        return pack(self.apply_complex(unpack(x), power)) * (2. ** -power)

    def condition(self):
        # Exact matrices: redundant Hermitian entries are inexpensive and avoid
        # a fixed eigenbasis or unidentified finite auxiliary-noise condition.
        parts = [self.variance.log()[:, None] / 5.]
        for matrix in (self.antenna, self.column):
            delta = matrix - torch.eye(matrix.shape[-1], device=matrix.device,
                                       dtype=matrix.dtype)
            parts.extend((delta.real.flatten(1), delta.imag.flatten(1)))
        return torch.cat(parts, dim=1)


def sample_covariance(rng, batch, antennas=16, columns=16, *, snr_db=(-20., 30.),
                      max_strength=.5, rank=4, dtype=torch.float32):
    """One conditional Gaussian family with independently drawn axis factors.

    Each factor is R=(1-alpha)I+alpha*m*GG^H/tr(GG^H),
    G~CN(0,I), alpha~Uniform[0,max_strength]. Parameters are declared
    design choices, not estimates of the current receiver's error law.
    max_strength=0 gives exact AWGN for validation; there is no class draw
    or point mass at identity in the default training distribution.
    """
    if not 0 <= max_strength < 1 or rank < 1:
        raise ValueError('Require 0 <= max_strength < 1 and rank >= 1')
    v = 10. ** (-rng.uniform(*snr_db, batch) / 10.)
    factors = []
    complex_dtype = torch.complex128 if dtype == torch.float64 else torch.complex64
    for m in (antennas, columns):
        g = (rng.standard_normal((batch, m, rank))
             + 1j*rng.standard_normal((batch, m, rank))) / math.sqrt(2.)
        gram = g @ g.conj().transpose(0, 2, 1)
        normalized = gram * (m / np.trace(gram, axis1=1, axis2=2).real)[:, None, None]
        alpha = rng.uniform(0., max_strength, batch)
        matrix = (1-alpha[:, None, None])*np.eye(m) + alpha[:, None, None]*normalized
        factors.append(torch.as_tensor(matrix, dtype=complex_dtype))
    return Covariance(torch.as_tensor(v, dtype=dtype), *factors)


def corrupt(clean, covariance, rng):
    """clean is real-packed; rng is independent of channel generation."""
    epsilon = torch.as_tensor(rng.standard_normal(tuple(clean.shape)),
                              dtype=clean.dtype, device=clean.device)
    return clean + covariance.apply_real(epsilon, .5)


def score_loss(score, noisy, clean, covariance):
    residual = (covariance.apply_real(score, .5)
                + covariance.apply_real(noisy-clean, -.5))
    return residual.square().mean()


def posterior_mean(noisy, score, covariance):
    return noisy + covariance.apply_real(score)
