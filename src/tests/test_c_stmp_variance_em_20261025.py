"""Complex variance and activity mixture checks for the independent candidate."""
import numpy as np
from algorithm.C_STMP_variance_em_20261025.iterations import expected_residual_power


def test_complex_gaussian_expected_residual():
    rng = np.random.default_rng(42)
    r = rng.normal(size=(3,2,4,5))+1j*rng.normal(size=(3,2,4,5))
    a, v = .7, 2.3
    mean = a/(a+v)*r
    tau = a*v/(a+v)
    cov = np.broadcast_to(tau*np.eye(2), (3,2,2))
    got, _, uncertainty = expected_residual_power(r, mean, cov)
    expected = (v/(a+v))**2*np.mean(abs(r)**2)+tau
    np.testing.assert_allclose(got, expected, rtol=2e-15)
    assert uncertainty == tau


def test_activity_mixture_expected_energy_matches_component_formula():
    rng = np.random.default_rng(43)
    r = rng.normal(size=(3,2,4,5))+1j*rng.normal(size=(3,2,4,5))
    mu = rng.normal(size=r.shape)+1j*rng.normal(size=r.shape)
    p = np.array([0., .3, 1.]); tau = np.array([.1,.2,.3])
    flat = mu.reshape(3,2,-1)
    gram = flat@flat.conj().swapaxes(-1,-2)/20
    cov = p[:,None,None]*tau[:,None,None]*np.eye(2)+(p*(1-p))[:,None,None]*gram
    got, _, _ = expected_residual_power(r, p[:,None,None,None]*mu, cov)
    expected = np.mean((1-p)*np.mean(abs(r)**2,axis=(1,2,3))+
        p*(np.mean(abs(r-mu)**2,axis=(1,2,3))+tau))
    np.testing.assert_allclose(got, expected, rtol=2e-15)
