"""Independent finite-dimensional checks; no receiver or physical truth is loaded."""
import numpy as np
import pytest

from algorithm.C_STMP_phase_direct_20261103.moments import (
    conditional_projected_moments, conditional_quadratic, marginal_value)
from algorithm.proposed.phase_math import observed_covariances, quadratic_objective
from algorithm.proposed.phase_update import objective, update_rotations


def _case(seed=3, q=4, k=3, n=2, m=2, rows=3):
    rng = np.random.default_rng(seed)

    def normal(shape):
        return (rng.normal(size=shape)+1j*rng.normal(size=shape))/np.sqrt(2)

    return (normal((q, m, rows)), normal((q, k, n))/np.sqrt(n),
            normal((k, m, rows, n)), .37, .21, rng.uniform(-np.pi, np.pi, k))


def _direct_posterior(case):
    """Full KN-dimensional Gaussian conditioning, independent of projection kernel."""
    observation, pilot, mean, variance, noise, beta = case
    q, k, n = pilot.shape
    m, rows = observation.shape[1:]
    y = observation.reshape(q, -1)
    x = mean.transpose(0, 3, 1, 2).reshape(k*n, -1)
    phase = np.exp(1j*np.arange(q)[:, None]*beta)
    a = (pilot*phase[:, :, None]).reshape(q, k*n)
    precision = np.eye(k*n)/variance+a.conj().T@a/noise
    posterior_cov = np.linalg.solve(precision, np.eye(k*n))
    posterior_mean = np.linalg.solve(precision, x/variance+a.conj().T@y/noise)
    z = np.empty((k, q, m*rows), complex)
    for user in range(k):
        z[user] = pilot[:, user]@posterior_mean[user*n:(user+1)*n]
    covariance = np.empty((q, k, k), complex)
    for frame in range(q):
        b = np.zeros((k, k*n), complex)
        for user in range(k):
            b[user, user*n:(user+1)*n] = pilot[frame, user]
        covariance[frame] = b@posterior_cov@b.conj().T
    return z, covariance


def _legacy_projected_quadratic(case):
    """Recompute the legacy QR-dimensional projected moments by dense solves."""
    observation, pilot, mean, variance, noise, beta = case
    q, k, n = pilot.shape
    m, rows = observation.shape[1:]
    g = observed_covariances(pilot, np.eye(rows*n))
    y = observation.transpose(0, 2, 1).reshape(q*rows, m)
    frames = np.repeat(np.arange(q), rows)
    phase = np.exp(1j*beta[:, None]*frames)
    z0 = np.einsum('qkn,kmrn->kqrm', pilot, mean).reshape(k, q*rows, m)
    covariance = noise*np.eye(q*rows)+variance*np.sum(
        g*phase[:, :, None]*phase[:, None, :].conj(), axis=0)
    residual = y-np.sum(z0*phase[:, :, None], axis=0)
    inverse = np.linalg.solve(covariance, np.eye(q*rows))
    cross = variance*g*phase[:, None, :].conj()
    z = z0+cross@inverse@residual
    quadratic = np.empty((q, k, k), complex)
    linear = np.empty((q, k), complex)
    for frame in range(q):
        ix = slice(frame*rows, (frame+1)*rows)
        zq = z[:, ix].reshape(k, rows*m)
        quadratic[frame] = zq.conj()@zq.T
        linear[frame] = zq.conj()@y[ix].reshape(-1)
        for first in range(k):
            for second in range(k):
                block = -cross[first]@inverse@cross[second].conj().T
                if first == second:
                    block += variance*g[first]
                quadratic[frame, first, second] += m*np.trace(block[ix, ix]).conj()
    return quadratic, linear, g, y, frames, z0*phase[:, :, None]


@pytest.mark.parametrize('seed,q,k,n,m,rows', [(3, 4, 3, 2, 2, 3), (19, 3, 2, 5, 3, 2)])
def test_full_channel_and_legacy_projection_agree(seed, q, k, n, m, rows):
    case = _case(seed, q, k, n, m, rows)
    z, covariance, details = conditional_projected_moments(*case)
    reference_z, reference_covariance = _direct_posterior(case)
    np.testing.assert_allclose(z, reference_z, rtol=2e-12, atol=2e-12)
    np.testing.assert_allclose(covariance, reference_covariance, rtol=2e-12, atol=2e-12)
    gram, matched, details = conditional_quadratic(*case)
    old_gram, old_matched, g, y, frames, projected = _legacy_projected_quadratic(case)
    np.testing.assert_allclose(gram, old_gram, rtol=2e-12, atol=2e-12)
    np.testing.assert_allclose(matched, old_matched, rtol=2e-12, atol=2e-12)
    old_value = objective(np.zeros(2*k), g, projected, y, case[4], frames, case[5], case[3])[0]
    np.testing.assert_allclose(old_value, rows*marginal_value(*case), rtol=2e-12, atol=2e-12)
    assert details['covariance_shape'] == [q, q]
    assert details['full_covariance_order'] == q*rows
    assert details['projected_covariance_hermitian_error'] < 1e-12
    assert np.linalg.eigvalsh(covariance).min() > -1e-12
    assert np.linalg.eigvalsh(gram).min() > -1e-12


def test_physical_and_normalized_units_agree():
    case = _case()
    observation, pilot, mean, variance, noise, beta = case
    scale = 7.3
    scaled = (observation*scale, pilot, mean*scale, variance*scale**2, noise*scale**2, beta)
    gram, matched, _ = conditional_quadratic(*case)
    other_gram, other_matched, _ = conditional_quadratic(*scaled)
    np.testing.assert_allclose(other_gram, gram*scale**2, rtol=2e-12, atol=2e-12)
    np.testing.assert_allclose(other_matched, matched*scale**2, rtol=2e-12, atol=2e-12)
    np.testing.assert_allclose(marginal_value(*scaled)-marginal_value(*case),
                               len(pilot)*np.log(scale**2), rtol=2e-12, atol=2e-12)


def test_fixed_message_gem_descent_with_channel_rotation():
    case = _case(seed=73, q=5, k=3, n=4, rows=2)
    observation, pilot, mean, variance, noise, beta = case
    gram, matched, _ = conditional_quadratic(*case)
    next_beta, angle, _ = update_rotations(beta, gram, matched, max_sweeps=3)
    old_phase = np.exp(1j*np.arange(len(pilot))[:, None]*beta)
    next_phase = np.exp(1j*(np.arange(len(pilot))[:, None]*next_beta+angle))
    assert quadratic_objective(next_phase, gram, matched) <= quadratic_objective(old_phase, gram, matched)+1e-10
    next_mean = mean*np.exp(1j*angle)[:, None, None, None]
    assert marginal_value(observation, pilot, next_mean, variance, noise, next_beta) <= marginal_value(*case)+1e-10


def test_public_dimensions_and_variances_are_checked():
    case = list(_case())
    case[3] = 0
    with pytest.raises(ValueError, match='positive complex variances'):
        conditional_quadratic(*case)
    case = list(_case())
    case[2] = case[2][..., :-1]
    with pytest.raises(ValueError, match='Incompatible'):
        conditional_quadratic(*case)
