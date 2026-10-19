"""Gaussian-site posterior used outside the learned query support."""

import numpy as np
from scipy.special import expit
from .records import SpatialMoments


def full_posterior(r, v, e, c, rho):
    """Normalized CN(e,c I) active site plus an inactive point mass at zero."""
    k, m, nr, nc = r.shape
    length = m * nr * nc
    tau = c * v / (c + v)
    mu = (c[:, None, None, None] * r + v * e) / (c + v)[:, None, None, None]
    ell = np.sum(abs(r) ** 2, axis=(1, 2, 3)) / v
    ell -= np.sum(abs(r - e) ** 2, axis=(1, 2, 3)) / (c + v) + length * np.log1p(c / v)
    p = expit(np.log(rho / (1 - rho)) + ell)
    flat = mu.reshape(k, m, -1)
    gram = np.einsum("kmd,knd->kmn", flat, flat.conj()) / (nr * nc)
    conditional_cov = tau[:, None, None] * np.eye(m)
    covariance = p[:, None, None] * conditional_cov + (p * (1 - p))[:, None, None] * gram
    kl = length * (tau / c - 1 + np.log(c / tau)) + np.sum(abs(mu - e) ** 2, axis=(1, 2, 3)) / c
    return SpatialMoments(
        p[:, None, None, None] * mu, mu, p, covariance, conditional_cov, ell, np.zeros(k), kl
    )
