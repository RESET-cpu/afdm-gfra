"""Independent dense Gaussian algebra and physical phase regression checks."""
from types import SimpleNamespace

import numpy as np
import pytest

from algorithm.STMP import phase_slopes, phase_slopes_iterations
from algorithm.proposed.phase_math import observed_covariances, stationary_maximum
from algorithm.proposed.phase_update import objective
from algorithm.STMP.records import SpatialConfig
from system.receiver.unknown_phase import UnknownPhaseInput
from algorithm.STMP.iterations import moment_damp
from algorithm.STMP.linear import SpatialLinear
from system.phase import phase_operator


def normal(rng, shape):
    return (rng.normal(size=shape) + 1j * rng.normal(size=shape)) / np.sqrt(2)


def fixture(seed=9, q=4):
    rng = np.random.default_rng(seed)
    k, rows, n, m = 3, 2, 2, 3
    pilot = normal(rng, (q, k, n))
    blocks = []
    for user in range(k):
        b = np.zeros((q * rows, rows * n), complex)
        for frame in range(q):
            for row in range(rows):
                b[frame * rows + row, row * n:(row + 1) * n] = pilot[frame, user]
        blocks.append(b)
    beta = rng.uniform(-np.pi, np.pi, k)
    frames = np.repeat(np.arange(q), rows)
    means = normal(rng, (k, rows * n, m))
    y = normal(rng, (q * rows, m))
    projected = np.array([b @ mu for b, mu in zip(blocks, means)])
    projected *= np.exp(1j * beta[:, None] * frames)[:, :, None]
    gram = observed_covariances(pilot, np.eye(rows * n))
    return (gram, projected, y, .6, frames, beta, .25), blocks, means, rows


@pytest.mark.parametrize('seed', [9, 38, 102])
def test_projected_quadratic_matches_dense_joint_gaussian(seed):
    args, blocks, means, rows = fixture(seed)
    gram, projected, y, noise, frames, beta, gamma = args
    q, k, m = int(frames.max()) + 1, len(beta), y.shape[1]
    a = np.concatenate([np.exp(1j * beta[u] * frames)[:, None] * b
                        for u, b in enumerate(blocks)], axis=1)
    mu = np.concatenate(means)
    covariance = noise * np.eye(len(y)) + gamma * a @ a.conj().T
    posterior = mu + gamma * a.conj().T @ np.linalg.solve(covariance, y - a @ mu)
    sigma = gamma * np.eye(len(mu)) - gamma**2 * a.conj().T @ np.linalg.solve(covariance, a)
    g, linear, projected_mean = phase_slopes.conditional_quadratic(*args)
    dimension = means.shape[1]
    expected_g, expected_b = np.zeros_like(g), np.zeros_like(linear)
    for frame in range(q):
        sl = slice(frame * rows, (frame + 1) * rows)
        z = [b[sl] @ posterior[u * dimension:(u + 1) * dimension]
             for u, b in enumerate(blocks)]
        for u in range(k):
            expected_b[frame, u] = np.vdot(z[u], y[sl])
            for v in range(k):
                cross = sigma[v * dimension:(v + 1) * dimension,
                              u * dimension:(u + 1) * dimension]
                expected_g[frame, u, v] = np.vdot(z[u], z[v]) + m * np.trace(
                    blocks[v][sl] @ cross @ blocks[u][sl].conj().T)
    np.testing.assert_allclose(g, expected_g, rtol=2e-12, atol=2e-12)
    np.testing.assert_allclose(linear, expected_b, rtol=2e-12, atol=2e-12)
    for u, b in enumerate(blocks):
        np.testing.assert_allclose(projected_mean[u], b @ posterior[u * dimension:(u + 1) * dimension],
            rtol=2e-12, atol=2e-12)


@pytest.mark.parametrize('q', [1, 4, 8, 16])
def test_real_coordinate_stationary_solution_dominates_dense_grid(q):
    rng = np.random.default_rng(q)
    for _ in range(8):
        u = normal(rng, q)
        c = u / 2
        c[0] = u[0].real
        beta, value, _ = stationary_maximum(c, .23)
        direct = float(np.real(np.exp(-1j * np.arange(q) * beta) @ u))
        np.testing.assert_allclose(value, direct, atol=2e-12, rtol=2e-12)
        grid = np.linspace(-np.pi, np.pi, 8193)
        reference = np.real(np.exp(-1j * grid[:, None] * np.arange(q)) @ u)
        assert value >= reference.max() - 2e-11


@pytest.mark.parametrize('seed', list(range(10)))
def test_update_keeps_zero_intercept_and_reduces_direct_marginal_likelihood(seed):
    args, blocks, means, _ = fixture(seed, q=5)
    gram, projected, y, noise, frames, beta, gamma = args
    new_beta, angle, record = phase_slopes.update(*args)
    np.testing.assert_array_equal(angle, np.zeros(len(beta)))
    assert record['after'] <= record['before'] + 1e-10
    assert np.all(np.diff(record['conditional_quadratic']['objectives']) <= 1e-9)
    a = np.concatenate([np.exp(1j * new_beta[u] * frames)[:, None] * b
                        for u, b in enumerate(blocks)], axis=1)
    residual = y - a @ np.concatenate(means)
    covariance = noise * np.eye(len(y)) + gamma * a @ a.conj().T
    sign, logdet = np.linalg.slogdet(covariance)
    assert np.isclose(sign, 1)
    direct = logdet + np.vdot(residual, np.linalg.solve(covariance, residual)).real / y.shape[1]
    np.testing.assert_allclose(record['after'], direct, rtol=2e-12, atol=2e-12)
    np.testing.assert_array_equal(np.exp(1j * 0 * new_beta), np.ones(len(beta)))


def test_operator_change_retains_physical_query_and_feedback(monkeypatch):
    rng = np.random.default_rng(12)
    inputs = UnknownPhaseInput(normal(rng, (4, 2, 2)), normal(rng, (4, 3, 2)), .3, .4)
    calls, observed = [], []
    class Gaussian:
        site_mean = None
        message_fresh = True
        last = {}
        def __call__(self, r, v):
            calls.append((r.copy(), v.copy()))
            scalar = np.trace(v).real / 2
            mean = r / (1 + scalar)
            self.site_mean = np.zeros_like(r)
            return SimpleNamespace(mean=mean, conditional_mean=mean, activity=np.full(3, .8),
                spatial_covariance=np.tile(np.eye(2) * scalar / (1 + scalar), (3, 1, 1)))
    def update(*args):
        return args[-2] + .04, np.zeros(3), {'conditional_quadratic': {'users': []}}
    monkeypatch.setattr(phase_slopes_iterations, 'update_phase', update)
    controls = SpatialConfig(iterations=4, min_iterations=4, damping=.2, covariance_mode='isotropic')
    configuration = dict(constant_phase='contained_in_channel', periodic_update=dict(start=2, interval=2),
        minimum_iterations_after_last_update=1, stopping=dict(allow_original_stopping=True,
            comparison='completed_phase_update_cycles', require_raw_site_residual=False,
            consecutive_cycles=2, relative_tolerance=.005, activity_tolerance=.001, require_stable_decisions=10))
    def observe(row, state, r, v, prior, prior_cov, out, out_v, posterior):
        observed.append((r.copy(), v.copy(), out.copy(), out_v.copy()))
    result, beta, steps = phase_slopes_iterations.infer(inputs, Gaussian(), scale=.27,
        initial_variance=.4, controls=controls, initial_slopes=np.zeros(3),
        phase_configuration=configuration, observer=observe)
    r, v, feedback, feedback_v = observed[1]
    linear = SpatialLinear(phase_operator(inputs.pilot, np.full(3, .04)), 2, .3 / .27**2)
    _, _, new_r, new_v = linear.update(inputs.observation / .27, feedback, feedback_v)
    expected_r, expected_v = moment_damp(r, v, new_r, new_v, .2)
    np.testing.assert_array_equal(calls[2][0], expected_r)
    np.testing.assert_array_equal(calls[2][1], expected_v)
    assert len(steps) == 1 and steps[0]['rotated_cached_means'] == []
    assert len(result.trace) == 4
