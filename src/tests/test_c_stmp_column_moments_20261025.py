"""Complex derivative, synthetic likelihood and activity mixture checks."""
import numpy as np
from numpy.testing import assert_allclose
from algorithm.C_STMP_column_messages.moments import (
    corrupt_information, covariance_from_directions, mixture_moments,
)


def complex_normal(rng, shape):
    return (rng.normal(size=shape) + 1j*rng.normal(size=shape))/np.sqrt(2)


def test_synthetic_information_has_the_declared_colored_noise():
    rng = np.random.default_rng(2026102511)
    precision = np.array([[.9, .22j], [-.22j, .2]], complex)
    h = complex_normal(rng, (2, 65536))
    message = corrupt_information(h, precision, rng)
    error = message.information-precision@h
    assert np.linalg.norm(error@error.conj().T/error.shape[1]-precision)/np.linalg.norm(precision) < .025
    z, gain, noise = message.reference_coordinates()
    e = z-gain@h
    assert np.linalg.norm(e@e.conj().T/e.shape[1]-noise)/np.linalg.norm(noise) < .025


def test_information_derivative_matches_complex_and_nonproper_gaussian_covariance():
    # Deterministic probes with exact proper second moments over the repeated
    # coordinates isolate complex-factor/orientation correctness from MC noise.
    n, l = 4, 128
    probe = np.exp(2j*np.pi*np.arange(1, n+1)[:, None]*np.arange(l)/l)
    assert_allclose(probe@probe.conj().T/l, np.eye(n), atol=1e-14)
    assert_allclose(probe@probe.T/l, 0, atol=1e-14)
    rng = np.random.default_rng(2026102512)
    g = complex_normal(rng, (n, n))
    cov = g@g.conj().T/n + .1*np.eye(n)
    eta = complex_normal(rng, (n, l))
    estimate = covariance_from_directions(lambda x: cov@x, eta, probe[None])
    assert_allclose(estimate, cov, atol=1e-12, rtol=1e-12)
    # Real-valued h embedded in complex coordinates has nonzero pseudocovariance.
    real_cov = np.diag([.1, .2, .3, .4])
    estimate_real = covariance_from_directions(lambda x: 2*real_cov@x.real, eta, probe[None])
    assert_allclose(estimate_real, real_cov, atol=1e-12, rtol=1e-12)


def test_activity_mixture_covariance_matches_enumerated_moments():
    # Exact finite distribution with two equally likely active states.
    plus = np.array([[1+2j, 2], [.5j, -1j]])
    minus = np.array([[-1j, 1j], [2, 1]])
    mu = (plus+minus)/2
    deviations = [plus-mu, minus-mu]
    conditional = sum(d@d.conj().T for d in deviations)/(2*mu.shape[1])
    p = .23
    joint_mean, joint_cov = mixture_moments(p, mu, conditional)
    values = [np.zeros_like(mu), plus, minus]
    weights = [1-p, p/2, p/2]
    exact_mean = sum(w*x for w, x in zip(weights, values))
    exact_cov = sum(w*(x-exact_mean)@(x-exact_mean).conj().T
                    for w, x in zip(weights, values))/mu.shape[1]
    assert_allclose(joint_mean, exact_mean, atol=1e-14)
    assert_allclose(joint_cov, exact_cov, atol=1e-14)
