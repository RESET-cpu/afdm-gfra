"""Separable functions of the real covariance Sigma = real_embedding(C)/2."""
from dataclasses import dataclass
import math

import torch


@dataclass
class Spectral:
    """Complex axis eigenvectors and Sigma eigenvalues [batch, antenna, column].

    The untouched output axis is an identity factor. Build the eigensystem before
    CUDA graph capture; ``apply`` uses only the three supplied spectral tensors.
    """

    antenna_vectors: torch.Tensor
    column_vectors: torch.Tensor
    variance_eigenvalues: torch.Tensor

    @classmethod
    def from_covariance(cls, covariance):
        """Diagonalize positive axis factors outside the captured forward path."""
        antenna_values, antenna_vectors = torch.linalg.eigh(covariance.antenna)
        column_values, column_vectors = torch.linalg.eigh(covariance.column)
        for values in (antenna_values, column_values, covariance.variance):
            if not bool(torch.all(torch.isfinite(values) & (values > 0))):
                raise ValueError('Positive finite covariance required; no eigenvalue clipping')
        eigenvalues = (covariance.variance[:, None, None] / 2
                       * antenna_values[:, :, None] * column_values[:, None, :])
        return cls(antenna_vectors, column_vectors, eigenvalues)

    def to(self, device):
        return type(self)(*(tensor.to(device) for tensor in (
            self.antenna_vectors, self.column_vectors, self.variance_eigenvalues)))

    def apply(self, x, multiplier):
        """Apply a real spectral multiplier and restore [B,2,A,O,C] coordinates.

        Reconstruction uses Ua Z Uc^T on the two correlated axes, not Uc^H.
        There are no tensor-to-host reads or eigendecompositions on this path.
        """
        if x.ndim != 5 or x.shape[1] != 2:
            raise ValueError('Expected real-packed [B,2,antenna,output,input] channel')
        expected = (x.shape[0], x.shape[2], x.shape[4])
        if tuple(multiplier.shape) != expected or tuple(self.variance_eigenvalues.shape) != expected:
            raise ValueError('Spectral multipliers must have shape [B,antenna,input]')
        dtype = torch.promote_types(x.dtype, self.variance_eigenvalues.dtype)
        # Complex-half contractions are not supported on both CPU and CUDA.
        dtype = torch.float64 if dtype == torch.float64 else torch.float32
        z = torch.complex(x[:, 0].to(dtype), x[:, 1].to(dtype))
        ua = self.antenna_vectors.to(dtype=z.dtype)
        uc = self.column_vectors.to(dtype=z.dtype)
        modes = torch.einsum('bja,bjoc->baoc', ua.conj(), z)
        modes = torch.einsum('bck,baoc->baok', uc.conj(), modes)
        modes = modes * multiplier[:, :, None, :]
        restored = torch.einsum('baj,bjok->baok', ua, modes)
        restored = torch.einsum('bck,baok->baoc', uc, restored)
        return torch.stack((restored.real, restored.imag), dim=1)


def from_covariance(covariance):
    """Convenience constructor; call outside CUDA graph capture."""
    return Spectral.from_covariance(covariance)


def stable_residual(raw, clean, epsilon, spectral, reference_real_variance=.5):
    """Return Sigma^(-1/2)(D-clean) without subtracting nearly equal signals.

    Requires observation = clean + Sigma^(1/2) epsilon and the raw trunk output
    from that observation. The squared mean is exactly the weighted DSM loss.
    """
    variance = float(reference_real_variance)
    if not math.isfinite(variance) or variance <= 0:
        raise ValueError('Positive finite reference real variance required')
    eigenvalues = spectral.variance_eigenvalues
    denominator = variance + eigenvalues
    gain = variance / denominator
    return (spectral.apply(raw, gain.sqrt())
            - spectral.apply(clean, eigenvalues.sqrt() / denominator)
            + spectral.apply(epsilon, gain))
