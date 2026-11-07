"""Rank-one approximation of each antenna unfolding; no array angles required."""

import numpy as np


def rank_one_spatial_mean(mean):
    """Return u1 u1^H F for F shaped [users, antennas, rows, columns].

    The leading eigenvector of F F^H is its leading left singular vector.
    This equals truncated SVD in Frobenius norm and uses the estimate only.
    It is not generally the posterior mean of a rank-one channel prior.
    See docs/TERMINOLOGY.md, rank-r matrix approximation (Xu et al., §3, Eq. 7).
    """
    value = np.asarray(mean, complex)
    if value.ndim != 4 or not all(value.shape) or not np.isfinite(value).all():
        raise ValueError("finite [users, antennas, rows, columns] mean required")
    flat = value.reshape(value.shape[0], value.shape[1], -1)
    gram = np.einsum("kmd,knd->kmn", flat, flat.conj(), optimize=False)
    _, vectors = np.linalg.eigh(gram)
    direction = vectors[..., -1]
    coefficients = np.einsum("km,kmd->kd", direction.conj(), flat, optimize=False)
    projected = direction[..., None]*coefficients[:, None, :]
    return projected.reshape(value.shape)
