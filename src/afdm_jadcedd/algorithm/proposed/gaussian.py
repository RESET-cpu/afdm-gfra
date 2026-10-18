"""Gaussian covariance and extrinsic message algebra."""

import numpy as np
from scipy.linalg import eigh


def hermitian(x):
    return (x + x.conj().T) / 2


def inverse(x):
    val, vec = eigh(hermitian(x), check_finite=True)
    if val.min() <= 0:
        raise FloatingPointError("positive Gaussian covariance required")
    return np.einsum("mi,i,ni->mn", vec, 1 / val, vec.conj(), optimize=False)


def spatial_apply(matrix, x):
    diagonal = np.diag(matrix)
    if np.count_nonzero(matrix - np.diag(diagonal)) == 0:
        return diagonal[None, :, None, None] * x
    rhs = np.moveaxis(x, 1, 0).reshape(len(matrix), -1)
    return np.moveaxis((matrix @ rhs).reshape(len(matrix), x.shape[0], *x.shape[2:]), 0, 1)


def gaussian_extrinsic(mean, posterior_cov, r, cavity_cov, floor=1e-6, ceiling=1 - 1e-6):
    v, u = eigh(hermitian(cavity_cov))
    root = np.einsum("mi,i,ni->mn", u, np.sqrt(v), u.conj(), optimize=False)
    invroot = np.einsum("mi,i,ni->mn", u, 1 / np.sqrt(v), u.conj(), optimize=False)
    whitened = np.einsum("ij,jk,kl->il", invroot, posterior_cov, invroot, optimize=False)
    fraction, basis = eigh(hermitian(whitened))
    used = np.clip(fraction, floor, ceiling)
    adjusted = ((root @ basis) * used) @ basis.conj().T @ root
    pt, pv = inverse(adjusted), inverse(cavity_cov)
    outgoing_cov = inverse(hermitian(pt - pv))
    outgoing_mean = spatial_apply(outgoing_cov, spatial_apply(pt, mean) - spatial_apply(pv, r))
    return outgoing_mean, outgoing_cov, fraction, used
