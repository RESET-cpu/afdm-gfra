"""Candidate: fixed-Gaussian-message EM with the physical exp(i*q*beta).

The channel includes constant phase. No separate constant rotation is fitted,
and no cached channel means change coordinates. See the candidate derivation
in result/candidates/stmp_phase_integration_20261023/DERIVATION.md.
"""
import numpy as np
from scipy.linalg import cho_factor
from scipy.linalg import cho_solve
from scipy.linalg import solve_triangular

from receiver.du.phase_math import quadratic_objective
from receiver.du.phase_math import stationary_maximum
from receiver.du.phase_update import objective


def conditional_quadratic(gram, projected, y, noise, frames, beta, gamma):
    """Exact projected moments under the fixed isotropic Gaussian message."""
    k, length, _ = gram.shape
    q = int(frames.max() + 1)
    rows, m = length // q, y.shape[1]
    phi = np.exp(1j * beta[:, None] * frames)
    covariance = noise * np.eye(length) + gamma * (
        gram * phi[:, :, None] * phi[:, None, :].conj()).sum(axis=0)
    factor = cho_factor(covariance, lower=True, check_finite=False)
    residual = y - projected.sum(axis=0)
    solved = cho_solve(factor, residual, check_finite=False)
    cross = gamma * gram * phi[:, None, :].conj()
    mean = projected * phi[:, :, None].conj() + cross @ solved
    lower = np.tril(factor[0])
    whitened = np.empty_like(cross)
    for user in range(k):
        whitened[user] = solve_triangular(
            lower, cross[user].conj().T, lower=True, check_finite=False).conj().T
    diagonal = np.diagonal(gram, axis1=1, axis2=2).real.reshape(k, q, rows).sum(axis=2)
    quadratic = np.empty((q, k, k), complex)
    linear = np.empty((q, k), complex)
    for frame in range(q):
        sl = slice(frame * rows, (frame + 1) * rows)
        means = mean[:, sl].reshape(k, rows * m)
        weights = whitened[:, sl].reshape(k, rows * length)
        covariance_trace = gamma * np.diag(diagonal[:, frame]) - weights.conj() @ weights.T
        quadratic[frame] = means.conj() @ means.T + m * covariance_trace
        quadratic[frame] = (quadratic[frame] + quadratic[frame].conj().T) / 2
        linear[frame] = means.conj() @ y[sl].reshape(-1)
    return quadratic, linear, mean


def update_slopes(beta, gram, b, max_sweeps=10, relative_tolerance=1e-7):
    """Lower the conditional quadratic with theta fixed to zero throughout.

    A coordinate maximizes Re sum_q u_q exp(-i*q*beta), not the magnitude
    of this sum. The latter implicitly introduces an additional constant phase.
    """
    q, k = b.shape
    frames = np.arange(q)
    beta = np.asarray(beta, float).copy()
    phase = np.exp(1j * frames[:, None] * beta)
    trace = [quadratic_objective(phase, gram, b)]
    off_diagonal = np.array(gram, copy=True)
    ix = np.arange(k)
    off_diagonal[:, ix, ix] = 0
    normalization = max(1., float(np.sum(abs(off_diagonal)) + 2 * np.sum(abs(b))))
    order = np.argsort(-np.diagonal(gram, axis1=1, axis2=2).real.sum(axis=0), kind='stable')
    gains, details = [], []
    converged = False
    for sweep in range(max_sweeps):
        for user in order:
            u = b[:, user] - np.einsum('ql,ql->q', gram[:, user], phase,
                optimize=True) + gram[:, user, user] * phase[:, user]
            before = float(np.vdot(phase[:, user], u).real)
            coefficients = u / 2
            coefficients[0] = u[0].real
            slope, value, count = stationary_maximum(coefficients, beta[user])
            if value >= before:
                beta[user] = slope
                phase[:, user] = np.exp(1j * frames * slope)
            details.append(dict(sweep=sweep, user=int(user), linear_term_before=before,
                linear_term_after=max(before, value), stationary_roots=count))
        trace.append(quadratic_objective(phase, gram, b))
        if trace[-1] > trace[-2] + 1e-9 * max(1., abs(trace[-2])):
            raise FloatingPointError('Physical-phase conditional quadratic increased')
        gains.append((trace[-2] - trace[-1]) / normalization)
        if sweep >= 1 and gains[-1] <= relative_tolerance:
            converged = True
            break
    beta = (beta + np.pi) % (2 * np.pi) - np.pi
    return beta, dict(sweeps=len(gains), maximum_sweeps=max_sweeps,
        relative_tolerance=relative_tolerance, normalization=normalization,
        normalized_gains=gains, converged=converged, objectives=trace, users=details,
        constant_phase_parameter=False,
        convergence_scope='Fixed conditional quadratic only; no global neural convergence claim')


def update(gram, projected, y, noise, frames, beta, gamma):
    quadratic, linear, mean = conditional_quadratic(
        gram, projected, y, noise, frames, beta, gamma)
    new_beta, m_step = update_slopes(beta, quadratic, linear)
    increment = np.angle(np.exp(1j * (new_beta - beta)))
    span = max(float(frames.max()), 1.)
    center = float(frames.max()) / 2
    args = gram, projected, y, noise, frames, beta, gamma
    before = objective(np.zeros(2 * len(beta)), *args)[0]
    # The reused objective uses centered frames: offset=center*increment is
    # necessary to represent exp(i*q*increment) with zero physical intercept.
    after, gradient = objective(np.r_[increment * span, center * increment], *args)
    if after > before + 1e-8 * max(1., abs(before)):
        raise FloatingPointError(f'Physical-phase fixed-message likelihood increased: {before}, {after}')
    slope_gradient = gradient[:len(beta)] + center / span * gradient[len(beta):]
    angle = np.zeros_like(beta)
    return new_beta, angle, dict(before=before, after=after, trial_value=after,
        accepted=True, trace=[before, after], iterations=m_step['sweeps'],
        success=m_step['converged'], message='Physical slope conditional quadratic update',
        gradient_max=float(np.max(abs(slope_gradient))),
        unwrapped_increment=increment.tolist(), centered_offset=(center * increment).tolist(),
        channel_rotation=angle.tolist(), covariance_scale=float(gamma),
        conditional_quadratic=m_step, posterior_mean_norm=float(np.linalg.norm(mean)),
        posterior_covariance='Full Gaussian cross-user projected covariance',
        constant_phase_parameter=False, first_frame_phase_fixed=True)
