"""Per-user input-column Gaussian messages.

This is exact algebra for independent Gaussian incoming messages, not a claim
that the finite nonlinear receiver errors are independent or Gaussian. See
paper/docs/C_STMP_COLUMN_MESSAGES_20261025.md. No frozen receiver imports this.
Arrays use [user, input column, independent coordinate] and [user, N, N].
"""
from dataclasses import dataclass

import numpy as np
from scipy.linalg import cho_factor, cho_solve


def hermitian(x):
    return (x + x.conj().swapaxes(-1, -2)) * .5


def solve_positive(a, b):
    return cho_solve(cho_factor(hermitian(a), lower=True, check_finite=True), b)


@dataclass
class GaussianMessage:
    """exp(-h^H precision h + 2 Re(h^H information)), per repeated coordinate.

An extrinsic factor need not be a normalizable Gaussian by itself. Its precision
is therefore not clipped here. A proper covariance requires positive precision.
"""
    precision: np.ndarray
    information: np.ndarray

    def moments(self):
        covariance = solve_positive(self.precision, np.eye(len(self.precision)))
        return covariance @ self.information, hermitian(covariance)

    def reference_coordinates(self):
        """Equivalent bounded coordinates Z=(I+Lambda)^-1 eta, J=Lambda/(I+Lambda).

        Under the Gaussian observation model, Z=J h+e, Cov(e)=J(I-J).
        This preserves the likelihood information, including when Lambda is
        singular, without constructing C=Lambda^-1. This is a parameterization,
        not an assertion that Z itself is h plus noise.
        """
        identity = np.eye(len(self.precision))
        system = identity + self.precision
        gain = hermitian(solve_positive(system, self.precision))
        z = solve_positive(system, self.information)
        noise = hermitian(gain @ (identity - gain))
        return z, gain, noise


def gaussian_posterior(message, prior_mean, prior_covariance):
    """Combine this likelihood with a proper Gaussian prior, without C^-1 inversion."""
    prior_precision = solve_positive(prior_covariance, np.eye(len(prior_covariance)))
    precision = hermitian(message.precision + prior_precision)
    covariance = solve_positive(precision, np.eye(len(precision)))
    mean = covariance @ (message.information + prior_precision @ prior_mean)
    return mean, hermitian(covariance)


def extrinsic(mean, covariance, incoming):
    """Gaussian moment approximation divided by the incoming factor; no clipping."""
    precision = solve_positive(covariance, np.eye(len(covariance)))
    return GaussianMessage(hermitian(precision - incoming.precision),
                           precision @ mean - incoming.information)


class ColumnLinear:
    """Integrate all other users under their independent Gaussian messages.

    Retain N x N input-column covariance for each user, shared across the other
    coordinates. A_k is [Q,N]; pilot is [Q,K,N]. Noise is proper complex white.
    """
    def __init__(self, pilot, noise_variance):
        p = np.asarray(pilot, dtype=np.complex128)
        if p.ndim != 3 or not all(p.shape) or not np.isfinite(p).all():
            raise ValueError('Expected finite pilot[Q,K,N]')
        if not np.isfinite(noise_variance) or noise_variance <= 0:
            raise ValueError('Positive finite noise variance required')
        self.a = p.transpose(1, 0, 2).copy()
        self.users, self.frames, self.columns = self.a.shape
        self.noise = float(noise_variance)

    def update(self, observation, mean, covariance):
        y, p, v = (np.asarray(x, dtype=np.complex128)
                   for x in (observation, mean, covariance))
        if (y.ndim != 2 or y.shape[0] != self.frames
                or p.shape != (self.users, self.columns, y.shape[1])
                or v.shape != (self.users, self.columns, self.columns)):
            raise ValueError('Expected y[Q,L], mean[K,N,L], covariance[K,N,N]')
        if not all(np.isfinite(x).all() for x in (y, p, v)):
            raise ValueError('Finite messages required')
        # Incoming messages must be proper. Do not silently repair their spectrum.
        for vk in v:
            cho_factor(hermitian(vk), lower=True)
        contributions = self.a @ v @ self.a.conj().transpose(0, 2, 1)
        predictions = self.a @ p
        residual = y - predictions.sum(axis=0)
        messages = []
        for k, ak in enumerate(self.a):
            # Sum the other users directly to avoid subtracting two large matrices.
            others = np.arange(self.users) != k
            s = self.noise*np.eye(self.frames) + contributions[others].sum(axis=0)
            factor = cho_factor(hermitian(s), lower=True)
            weighted_a = cho_solve(factor, ak)
            precision = hermitian(ak.conj().T @ weighted_a)
            information = weighted_a.conj().T @ (residual + predictions[k])
            messages.append(GaussianMessage(precision, information))
        return messages
