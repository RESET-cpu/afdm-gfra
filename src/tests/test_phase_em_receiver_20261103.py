"""Math/interface checks for the independent phase candidate; no trained model."""
from dataclasses import replace
from types import SimpleNamespace
import numpy as np
import pytest

from algorithm.C_STMP_phase_em_20261103 import iterations
from algorithm.C_STMP_phase_em_20261103.denoiser import GuardedDenoiser
from algorithm.STMP.denoiser import Denoiser
from algorithm.C_STMP_variance_em_20261025.iterations import run_spatial_score
from algorithm.STMP.records import SpatialConfig
from system.phase import phase_operator
from test_phase_direct_integration_20261103 import GaussianDenoiser, _input


def _controls(n=12):
    return SpatialConfig(iterations=n, min_iterations=n+1, damping=.4,
                         covariance_mode='isotropic')


def _policy(block=3):
    return dict(e_step_iterations=block, phase_tolerance=1e-4,
                m_step=dict(max_steps=3, gradient_tolerance=1e-7, armijo=1e-4, max_backtracks=12))


@pytest.mark.parametrize('enabled', [False, True])
@pytest.mark.parametrize('adapt', [False, True])
def test_unchanged_phase_is_bitwise_frozen_receiver(monkeypatch, enabled, adapt):
    raw, beta, cfg = _input(), np.array([.3, -.2, .1]), _controls()
    monkeypatch.setattr(iterations, 'update_phase',
                        lambda y, p, m, b, **kw: (b.copy(), dict(seconds=0.)))
    expected = run_spatial_score(raw.at_estimated_phase(beta), GaussianDenoiser(),
                                scale=.7, initial_variance=.4, config=cfg, adapt=adapt)
    actual, used, trials = iterations.infer(raw, GaussianDenoiser(), scale=.7,
        initial_variance=.4, controls=cfg, policy=_policy(), initial_slopes=beta,
        phase_enabled=enabled, adapt=adapt)
    for key in ('estimate', 'conditional_matrix', 'probabilities', 'spatial_covariance'):
        np.testing.assert_array_equal(getattr(actual, key), getattr(expected, key))
    np.testing.assert_array_equal(used, beta)
    assert actual.stopping_reason == expected.stopping_reason
    for a, b in zip(actual.trace, expected.trace):
        for key in ('em_variance_target', 'query_variance_ratio', 'residual_power',
                    'estimate_change', 'activity_change', 'input_covariance_change'):
            assert a[key] == b[key]
    assert len(trials) == (3 if enabled else 0)


def test_fixed_phase_stopping_matches_original():
    raw, beta = _input(), np.zeros(3)
    cfg = replace(_controls(100), min_iterations=5, convergence_tolerance=.1,
                  convergence_patience=2, activity_convergence_tolerance=.1,
                  decision_stability_window=2)
    expected = run_spatial_score(raw.at_estimated_phase(beta), GaussianDenoiser(),
                                scale=.7, initial_variance=.4, config=cfg)
    actual, _, _ = iterations.infer(raw, GaussianDenoiser(), scale=.7,
        initial_variance=.4, controls=cfg, policy=_policy(), phase_enabled=False)
    assert actual.stopping_reason == expected.stopping_reason == 'CONVERGED'
    assert len(actual.trace) == len(expected.trace)
    np.testing.assert_array_equal(actual.estimate, expected.estimate)


def test_joint_tolerance_returns_phase_actually_used_for_channel(monkeypatch):
    raw = _input()
    cfg = replace(_controls(100), min_iterations=5, convergence_tolerance=.1,
                  convergence_patience=2, activity_convergence_tolerance=.1,
                  decision_stability_window=2)
    monkeypatch.setattr(iterations, 'update_phase',
                        lambda y, p, m, b, **kw: (b+1e-9, dict(seconds=0.)))
    actual, beta, trials = iterations.infer(raw, GaussianDenoiser(), scale=.7,
        initial_variance=.4, controls=cfg, policy=_policy())
    assert actual.stopping_reason == 'CONVERGED'
    assert trials[-1]['e_step_converged'] and not trials[-1]['applied']
    np.testing.assert_array_equal(beta, np.asarray(actual.trace[-1]['phase_slopes_used']))
    assert not np.array_equal(beta, trials[-1]['proposed_slopes'])


def test_m_step_uses_joint_mean_and_every_applied_phase_has_following_full_block(monkeypatch):
    raw, seen, states, operators = _input(), [], [], []
    original = iterations.SpatialLinear
    class Linear(original):
        def __init__(self, operator, *args):
            super().__init__(operator, *args)
            self.operator = operator.copy()
        def update(self, *args):
            answer = super().update(*args)
            operators.append((self.operator, answer[2].copy(), answer[3].copy()))
            return answer
    monkeypatch.setattr(iterations, 'SpatialLinear', Linear)
    def update(y, pilot, mean, beta, **kw):
        np.testing.assert_array_equal(mean, states[-1]['mean'])
        seen.append(beta.copy())
        return beta+np.array([.01, -.02, .03]), dict(seconds=0.)
    monkeypatch.setattr(iterations, 'update_phase', update)
    def observe(row, state, query, covariance, prior, prior_cov, out, out_cov, post):
        states.append(dict(mean=state.mean.copy(), query=query.copy(), covariance=covariance.copy(),
                           prior=prior.copy(), prior_cov=prior_cov.copy(), out=out.copy(), out_cov=out_cov.copy()))
    result, beta, trials = iterations.infer(raw, GaussianDenoiser(), scale=.7,
        initial_variance=.4, controls=_controls(), policy=_policy(), observer=observe)
    assert [t['after_iteration'] for t in trials] == [3, 6, 9]
    assert all(t['applied'] and t['used_by_following_e_step'] for t in trials)
    np.testing.assert_array_equal(operators[-1][0], phase_operator(raw.pilot, beta))
    np.testing.assert_array_equal(result.estimate, states[-1]['mean']*.7)
    for i in (3, 6, 9):
        # No old-operator query enters query damping after a phase change.
        np.testing.assert_array_equal(states[i]['query'], operators[i][1])
        # Channel feedback and variance ratio stay as warm-start quantities.
        np.testing.assert_array_equal(states[i]['prior'], states[i-1]['out'])
        np.testing.assert_array_equal(states[i]['prior_cov'], states[i-1]['out_cov'])
        assert result.trace[i]['query_variance_ratio'] == result.trace[i-1]['next_query_variance_ratio']
        assert result.trace[i]['conditional_iteration'] == 1
        assert result.trace[i]['estimate_change'] is None


class Model:
    noise_support = (.001, 100.)
    def __init__(self, variances):
        self.variances, self.samples = list(variances), 0
    def infer(self, query, variance):
        self.samples += len(query)
        return SimpleNamespace(mean=.4*query+.1j,
                               variance=np.full(len(query), self.variances.pop(0)))


class Evidence:
    noise_support = Model.noise_support
    training_class_prior = .5
    def infer(self, query, variance, mean):
        np.testing.assert_array_equal(mean, .4*query+.1j)
        return np.zeros(len(query))


def _denoiser(cls, variances):
    return cls(Model(variances), Evidence(), activity_prior=.3, conditional_variance_floor=1e-4)


@pytest.mark.parametrize('bad', [-.53, 0.])
def test_nonpositive_trace_preserves_site_and_original_diagnostics(bad):
    d = _denoiser(GuardedDenoiser, [.2, bad])
    q = np.ones((3, 2, 2, 2), complex)
    d(q, np.eye(2))
    previous_mean, previous_var = d.site_mean.copy(), d.site_variance.copy()
    state = d(2*q, np.eye(2))
    np.testing.assert_array_equal(d.site_mean, previous_mean)
    np.testing.assert_array_equal(d.site_variance, previous_var)
    assert d.last['raw_pooled_variance'] == bad
    assert not d.last['site_accepted'] and not d.last['conditional_variance_floored']
    assert d.last['nonpositive_pooled_variance_rejected'] and not d.message_fresh
    assert d.last['conditional_variance_fraction'] is None
    np.testing.assert_array_equal(d.snapshot['raw_network_variance'], np.full(3, bad))
    np.testing.assert_allclose(state.activity, .3)
    assert np.min(np.linalg.eigvalsh(state.spatial_covariance)) > 0


@pytest.mark.parametrize('variance', [1e-5, .2, 1., 2.])
def test_positive_trace_preserves_frozen_denoiser(variance):
    q = np.ones((3, 2, 2, 2), complex)
    old, new = _denoiser(Denoiser, [variance]), _denoiser(GuardedDenoiser, [variance])
    a, b = old(q, np.eye(2)), new(q, np.eye(2))
    for field in ('mean', 'conditional_mean', 'activity', 'spatial_covariance'):
        np.testing.assert_array_equal(getattr(a, field), getattr(b, field))
    assert a is not b
    assert not new.last['nonpositive_pooled_variance_rejected']


def test_nan_moments_still_fail():
    d = _denoiser(GuardedDenoiser, [np.nan])
    with pytest.raises(FloatingPointError):
        d(np.ones((3, 2, 2, 2)), np.eye(2))


@pytest.mark.parametrize('users,variance', [(3, 1.), (40, 7.351634930334476)])
def test_first_negative_trace_retains_original_unit_site_initialization(users, variance):
    d = _denoiser(GuardedDenoiser, [-.53])
    state = d(np.ones((users, 2, 2, 2)), variance*np.eye(2))
    np.testing.assert_array_equal(d.site_mean, np.zeros((users, 2, 2, 2)))
    np.testing.assert_array_equal(d.site_variance, np.ones(users))
    np.testing.assert_array_equal(state.conditional_spatial_covariance,
        np.broadcast_to(variance/(1+variance)*np.eye(2), (users, 2, 2)))
