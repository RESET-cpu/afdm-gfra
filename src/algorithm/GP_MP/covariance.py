"""Covariance representation used by the frozen checkpoint architecture.

The adopted network is trained with identity factors. The representation and
operation order are retained so checkpoint keys and FP32 arithmetic stay fixed.
"""
from dataclasses import dataclass
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
