"""Independent Gaussian ground truth and finite covariance checks for candidate."""
import numpy as np
from numpy.testing import assert_allclose
from scipy.linalg import block_diag

from algorithm.C_STMP_column_messages.messages import (
    ColumnLinear, GaussianMessage, extrinsic, gaussian_posterior,
)


def complex_normal(rng, shape):
    return (rng.normal(size=shape) + 1j*rng.normal(size=shape))/np.sqrt(2)


def problem(q=7, k=3, n=4, l=5):
    rng = np.random.default_rng(2026102509)
    a = complex_normal(rng, (q, k, n))/np.sqrt(q)
    p = complex_normal(rng, (k, n, l))
    g = complex_normal(rng, (k, n, n))
    v = g @ g.conj().transpose(0, 2, 1)/n + .3*np.eye(n)
    y = complex_normal(rng, (q, l))
    return a, p, v, y, .17


def test_gaussian_marginal_and_division_match_full_joint_posterior():
    a, p, v, y, noise = problem()
    q, k, n = a.shape
    full_a = a.reshape(q, k*n)
    full_v = block_diag(*v)
    prior_precision = np.linalg.inv(full_v)
    post_cov = np.linalg.inv(prior_precision + full_a.conj().T @ full_a/noise)
    post_mean = post_cov @ (prior_precision @ p.reshape(k*n, -1)
                            + full_a.conj().T @ y/noise)
    messages = ColumnLinear(a, noise).update(y, p, v)
    for j, message in enumerate(messages):
        mu, cov = gaussian_posterior(message, p[j], v[j])
        sl = slice(j*n, (j+1)*n)
        assert_allclose(mu, post_mean[sl], rtol=2e-12, atol=2e-12)
        assert_allclose(cov, post_cov[sl, sl], rtol=2e-12, atol=2e-12)
        back = extrinsic(mu, cov, message)
        # A Gaussian prior module must return exactly its own prior factor.
        assert_allclose(back.precision, np.linalg.inv(v[j]), rtol=2e-12, atol=2e-12)
        assert_allclose(back.information, np.linalg.solve(v[j], p[j]),
                        rtol=2e-12, atol=2e-12)


def test_unit_response_covariance_and_square_operator_special_case():
    a, p, v, y, noise = problem(q=4)
    messages = ColumnLinear(a, noise).update(y, p, v)
    for k, message in enumerate(messages):
        ak = a[:, k]
        s = noise*np.eye(4, dtype=complex)
        ym = y.copy()
        for j in range(len(p)):
            if j != k:
                s += a[:, j] @ v[j] @ a[:, j].conj().T
                ym -= a[:, j] @ p[j]
        r, c = message.moments()
        t = c @ ak.conj().T @ np.linalg.inv(s)
        assert_allclose(t @ ak, np.eye(4), atol=2e-12)
        assert_allclose(t @ s @ t.conj().T, c, rtol=2e-12, atol=2e-12)
        assert_allclose(r, np.linalg.solve(ak, ym), rtol=2e-12, atol=2e-12)
        z, gain, cov = message.reference_coordinates()
        assert_allclose(z, gain @ r, rtol=2e-12, atol=2e-12)
        assert_allclose(cov, gain @ c @ gain, rtol=2e-12, atol=2e-12)


def test_rank_deficient_likelihood_remains_usable_in_precision_form():
    a, p, v, y, noise = problem(q=2)
    for j, message in enumerate(ColumnLinear(a, noise).update(y, p, v)):
        z, gain, cov = message.reference_coordinates()
        assert np.linalg.matrix_rank(message.precision, tol=1e-10) == 2
        assert np.linalg.eigvalsh(gain).min() > -1e-12
        assert np.linalg.eigvalsh(cov).max() <= .25+1e-12
        mu, posterior = gaussian_posterior(message, p[j], v[j])
        assert np.isfinite(mu).all() and np.linalg.eigvalsh(posterior).min() > 0


def test_complex_covariance_uses_conjugation_not_transpose():
    # A non-real covariance catches orientation and real/complex factor mistakes.
    c = np.array([[1., .35j], [-.35j, .8]], complex)
    message = GaussianMessage(np.linalg.inv(c), np.zeros((2, 1), complex))
    _, gain, noise = message.reference_coordinates()
    rng = np.random.default_rng(2026102510)
    samples = gain @ np.linalg.cholesky(c) @ complex_normal(rng, (2, 65536))
    empirical = samples @ samples.conj().T/samples.shape[1]
    assert np.linalg.norm(empirical-noise)/np.linalg.norm(noise) < .025
