"""Validate complex covariance orientation, power and identity reduction."""
import numpy as np
import torch
from evaluation.colored_noise_experiment_20261025 import factor_bases, colored_noise
from training.colored_score_20261024.noise import Covariance


def test_tensor_corruption_matches_dense_complex_covariance_root():
    rng = np.random.default_rng(71)
    eps = (rng.normal(size=(1, 3, 2, 3))+1j*rng.normal(size=(1, 3, 2, 3)))/np.sqrt(2)
    noise, ra, rc = colored_noise(eps, factor_bases(72, 1, size=3, rank=2), .5)
    dense = np.kron(np.kron(ra[0], np.eye(2)), rc[0])
    ev, u = np.linalg.eigh(dense)
    root = (u*np.sqrt(ev)) @ u.conj().T
    np.testing.assert_allclose(noise.reshape(-1), root @ eps.reshape(-1), rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(np.trace(dense).real, 18, atol=1e-12)
    cov = Covariance(torch.ones(1, dtype=torch.float64), torch.tensor(ra), torch.tensor(rc))
    np.testing.assert_allclose(cov.apply_complex(torch.tensor(eps), .5).numpy(), noise, rtol=1e-12, atol=1e-12)


def test_zero_strength_preserves_original_noise_exactly():
    eps = np.arange(18).reshape(1, 3, 2, 3).astype(complex)*(1+2j)
    noise, ra, rc = colored_noise(eps, factor_bases(73, 1, size=3, rank=2), 0.)
    np.testing.assert_array_equal(noise, eps)
    np.testing.assert_array_equal(ra[0], np.eye(3))
    np.testing.assert_array_equal(rc[0], np.eye(3))


def test_empirical_complex_covariance_and_pseudocovariance():
    # Each output slice is an independent realization; proper complex noise is essential.
    rng = np.random.default_rng(74)
    eps = (rng.normal(size=(1, 3, 20000, 3))+1j*rng.normal(size=(1, 3, 20000, 3)))/np.sqrt(2)
    noise, ra, rc = colored_noise(eps, factor_bases(75, 1, size=3, rank=2), .5)
    samples = noise[0].transpose(1, 0, 2).reshape(-1, 9)
    expected = np.kron(ra[0], rc[0])
    estimated = samples.T @ samples.conj()/len(samples)
    assert np.linalg.norm(estimated-expected)/np.linalg.norm(expected) < .03
    assert np.linalg.norm(samples.T @ samples/len(samples))/np.linalg.norm(expected) < .03
