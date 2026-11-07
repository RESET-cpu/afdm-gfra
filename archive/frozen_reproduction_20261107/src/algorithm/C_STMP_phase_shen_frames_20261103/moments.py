"""Exact projected moments for arbitrary per-frame unit phases.

The reference frame q=0 is fixed by the phase solver, not by this E step.

The observation covariance is C[Q,Q] tensored with identity across output
coordinates and antennas.  Computing C directly preserves all cross-user
conditional covariances without allocating the larger (Q*R) square matrix.
The Gaussian message is an approximation to the physical channel posterior;
the computations below are exact only for that declared message model.
"""
import time

import numpy as np
from scipy.linalg import cho_factor, cho_solve, solve_triangular


def _model(observation, pilot, mean, variance, noise, phase):
    started = time.perf_counter()
    y, p, x = (np.asarray(value, dtype=np.complex128)
               for value in (observation, pilot, mean))
    phase = np.asarray(phase, dtype=np.complex128)
    if y.ndim != 3 or p.ndim != 3 or x.ndim != 4:
        raise ValueError('Expected observation[Q,M,R], pilot[Q,K,N], mean[K,M,R,N]')
    q, k, n = p.shape
    if not all(p.shape) or not all(y.shape):
        raise ValueError('Nonempty observation and pilot dimensions required')
    m, rows = y.shape[1:]
    if y.shape[0] != q or x.shape != (k, m, rows, n) or phase.shape != (q, k):
        raise ValueError('Incompatible observation, pilot, mean, or phase dimensions')
    variance, noise = float(variance), float(noise)
    if (not all(np.isfinite(value).all() for value in (y, p, x, phase))
            or not np.isfinite(variance) or variance <= 0
            or not np.isfinite(noise) or noise <= 0):
        raise ValueError('Finite arrays and positive complex variances required')
    if not np.allclose(abs(phase), 1., rtol=0., atol=1e-10):
        raise ValueError('Unit-modulus phases required')
    # d=(antenna, output coordinate) in both arrays; no transpose is needed.
    y = y.reshape(q, m*rows)
    base = np.einsum('qkn,skn->kqs', p, p.conj(), optimize=True)
    projected = np.einsum('qkn,kmrn->kqmr', p, x, optimize=True).reshape(k, q, m*rows)
    phase = phase.T
    rotated = base*phase[:, :, None]*phase[:, None, :].conj()
    covariance = noise*np.eye(q)+variance*rotated.sum(axis=0)
    covariance_error = float(np.max(abs(covariance-covariance.conj().T)))
    covariance = (covariance+covariance.conj().T)/2
    residual = y-np.sum(phase[:, :, None]*projected, axis=0)
    details = dict(shape=dict(frames=q, users=k, inputs=n, antennas=m, outputs=rows),
                   covariance_shape=[q, q], full_covariance_order=q*rows,
                   covariance_hermitian_error=covariance_error,
                   setup_seconds=time.perf_counter()-started)
    return y, base, projected, phase, covariance, residual, variance, details


def conditional_projected_moments(observation, pilot, mean, variance, noise, phase):
    """Return unphased contribution means and per-coordinate covariances.

    projected[k,q,d] = E[z_k[q,d] | Y], where z_k=P_k x_k.
    covariance[q,k,l] = E[(z_k[q,d]-mu_k) conj(z_l[q,d]-mu_l) | Y].
    The covariance is identical for each d; multiplying it by D belongs in
    the expected quadratic, not in this covariance itself.
    """
    started = time.perf_counter()
    y, base, projected, phase, covariance, residual, variance, details = _model(
        observation, pilot, mean, variance, noise, phase)
    factor = cho_factor(covariance, lower=True, check_finite=False)
    solved = cho_solve(factor, residual, check_finite=False)
    cross = variance*base*phase[:, None, :].conj()
    projected = projected+cross@solved
    lower = np.tril(factor[0])
    whitened = np.empty_like(cross)
    for user in range(len(base)):
        whitened[user] = solve_triangular(
            lower, cross[user].conj().T, lower=True, check_finite=False).conj().T
    posterior = -np.einsum('kqt,lqt->qkl', whitened, whitened.conj(), optimize=True)
    users = np.arange(len(base))
    posterior[:, users, users] += variance*np.diagonal(base, axis1=1, axis2=2).T
    error = float(np.max(abs(posterior-posterior.conj().transpose(0, 2, 1))))
    posterior = (posterior+posterior.conj().transpose(0, 2, 1))/2
    details.update(projected_covariance_hermitian_error=error,
                   projected_covariance_min_diagonal=float(
                       np.diagonal(posterior, axis1=1, axis2=2).real.min()),
                   projected_mean_norm=float(np.linalg.norm(projected)),
                   elapsed_seconds=time.perf_counter()-started,
                   moment_scope='Exact conditional moments of fixed isotropic Gaussian message',
                   cross_user_covariance_retained=True)
    return projected, posterior, details


def conditional_quadratic(observation, pilot, mean, variance, noise, phase):
    """Return G[q,k,l]=sum_d E[conj(z_k) z_l] and b[q,k]."""
    started = time.perf_counter()
    projected, covariance, details = conditional_projected_moments(
        observation, pilot, mean, variance, noise, phase)
    q, d = projected.shape[1:]
    y = np.asarray(observation, dtype=np.complex128).reshape(q, d)
    gram = np.einsum('kqd,lqd->qkl', projected.conj(), projected, optimize=True)
    gram += d*covariance.conj()
    error = float(np.max(abs(gram-gram.conj().transpose(0, 2, 1))))
    gram = (gram+gram.conj().transpose(0, 2, 1))/2
    matched = np.einsum('kqd,qd->qk', projected.conj(), y, optimize=True)
    details.update(quadratic_hermitian_error=error, elapsed_seconds=time.perf_counter()-started)
    return gram, matched, details


def marginal_value(observation, pilot, mean, variance, noise, phase):
    """Negative Gaussian log likelihood per independent column, up to a constant.

    Returns logdet(C) + tr(residual^H C^-1 residual)/(M*R).
    The legacy QR-dimensional objective equals R times this value.
    """
    y, _, _, _, covariance, residual, _, _ = _model(
        observation, pilot, mean, variance, noise, phase)
    factor = cho_factor(covariance, lower=True, check_finite=False)
    whitened = solve_triangular(np.tril(factor[0]), residual, lower=True, check_finite=False)
    return float(2*np.log(np.diag(factor[0]).real).sum()+np.vdot(whitened, whitened).real/y.shape[1])
