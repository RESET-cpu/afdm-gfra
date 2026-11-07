"""Constant phase absorption and physical-query history in the STMP candidate."""
from types import SimpleNamespace
import numpy as np
import pytest

from algorithm.STMP import phase_feedback_iterations, phase_refresh_iterations
from algorithm.STMP.iterations import moment_damp
from algorithm.STMP.linear import SpatialLinear
from algorithm.STMP.records import SpatialConfig
from algorithm.proposed.phase_math import observed_covariances
from algorithm.proposed.phase_update import update
from system.phase import phase_operator
from system.receiver.unknown_phase import UnknownPhaseInput


def normal(rng, shape):
    return (rng.normal(size=shape) + 1j * rng.normal(size=shape)) / np.sqrt(2)


def test_absorbed_feedback_phase_has_identical_marginal_likelihood():
    rng = np.random.default_rng(633)
    for _ in range(8):
        q, k, n, m = 5, 3, 2, 4
        pilot = normal(rng, (q, k, n))
        mu = normal(rng, (k, n, m))
        beta = rng.normal(size=k)
        frames = np.arange(q)
        y = normal(rng, (q, m))
        gram = observed_covariances(pilot, np.eye(n))
        projected = np.einsum('qkn,knm->kqm', pilot, mu)
        projected *= np.exp(1j * beta[:, None] * frames)[:, :, None]
        new_beta, angle, record = update(gram, projected, y, .3, frames, beta, .4)
        a = phase_operator(pilot, new_beta).reshape(q, k * n)
        rotated = (mu * np.exp(1j * angle)[:, None, None]).reshape(k * n, m)
        residual = y - a @ rotated
        covariance = .3 * np.eye(q) + .4 * a @ a.conj().T
        direct = np.linalg.slogdet(covariance)[1] + np.vdot(
            residual, np.linalg.solve(covariance, residual)).real / m
        np.testing.assert_allclose(direct, record['after'], rtol=2e-12, atol=2e-12)


@pytest.mark.parametrize('kernel,mode,refresh', [
    (phase_feedback_iterations, 'feedback_only', False),
    (phase_refresh_iterations, 'feedback_and_new_query', True),
])
def test_next_query_uses_declared_mean_covariance_pair(monkeypatch,kernel,mode,refresh):
    rng = np.random.default_rng(12)
    inputs = UnknownPhaseInput(normal(rng, (4, 2, 2)), normal(rng, (4, 3, 2)), .3, .4)
    calls, observed = [], []
    class Gaussian:
        site_mean = None
        message_fresh = True
        last = {}
        def __call__(self, r, v):
            calls.append((r.copy(), v.copy(), None if self.site_mean is None else self.site_mean.copy()))
            scalar = np.trace(v).real / 2
            mean = r / (1 + scalar)
            self.site_mean = np.ones_like(r) * (1 + .1j)
            return SimpleNamespace(mean=mean, conditional_mean=mean, activity=np.full(3, .8),
                spatial_covariance=np.tile(np.eye(2) * scalar / (1 + scalar), (3, 1, 1)))
    def changed(*args):
        return args[-2] + .04, np.array([.3, -.2, .5]), {'conditional_quadratic': {'users': []}}
    monkeypatch.setattr(kernel, 'update_phase', changed)
    controls = SpatialConfig(iterations=4, min_iterations=4, damping=.2, covariance_mode='isotropic')
    configuration = dict(state_update=mode, periodic_update=dict(start=2, interval=2),
        minimum_iterations_after_last_update=1, stopping=dict(allow_original_stopping=True,
            comparison='completed_phase_update_cycles', require_raw_site_residual=False,
            consecutive_cycles=2, relative_tolerance=.005, activity_tolerance=.001, require_stable_decisions=10))
    def observe(row, state, r, v, prior, prior_cov, out, out_v, posterior):
        observed.append((r.copy(), v.copy(), out.copy(), out_v.copy()))
    result, beta, steps = kernel.infer(inputs, Gaussian(), scale=.27,
        initial_variance=.4, controls=controls, initial_slopes=np.zeros(3),
        phase_configuration=configuration, observer=observe)
    r, v, feedback, feedback_v = observed[1]
    feedback = feedback * np.exp(1j * np.array([.3, -.2, .5]))[:, None, None, None]
    linear = SpatialLinear(phase_operator(inputs.pilot, np.full(3, .04)), 2, .3 / .27**2)
    _, _, new_r, new_v = linear.update(inputs.observation / .27, feedback, feedback_v)
    expected_r, expected_v = (new_r,new_v) if refresh else moment_damp(r, v, new_r, new_v, .2)
    np.testing.assert_array_equal(calls[2][0], expected_r)
    np.testing.assert_array_equal(calls[2][1], expected_v)
    np.testing.assert_array_equal(calls[2][2], np.ones_like(r) * (1 + .1j))
    assert len(steps) == 1 and steps[0]['rotated_cached_means'] == ['feedback']
    assert len(result.trace) == 4
