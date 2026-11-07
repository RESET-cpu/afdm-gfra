"""Small analytic-denoiser checks; no network, physical search, or truth data."""
from types import SimpleNamespace

import numpy as np

from algorithm.C_STMP_phase_direct_20261103 import iterations
from algorithm.C_STMP_phase_direct_20261103.initialization import column_moment
from algorithm.C_STMP_variance_em_20261025.iterations import run_spatial_score
from algorithm.STMP.records import SpatialConfig
from system.phase import phase_operator
from system.receiver.unknown_phase import UnknownPhaseInput


class GaussianDenoiser:
    def __init__(self):
        self.last = {}
        self.message_fresh = True

    def __call__(self, query, covariance):
        k, m = query.shape[:2]
        variance = np.trace(covariance).real/m
        mean = query/(1+variance)
        self.message_fresh = True
        return SimpleNamespace(mean=mean, conditional_mean=mean,
            activity=np.full(k, .8),
            spatial_covariance=np.broadcast_to(np.eye(m)*variance/(1+variance), (k,m,m)))


def _input():
    rng = np.random.default_rng(349)
    normal = lambda shape: rng.normal(size=shape)+1j*rng.normal(size=shape)
    return UnknownPhaseInput(normal((4,2,3)), normal((4,3,2)), .3, .4)


def _controls(iterations_count=8):
    return SpatialConfig(iterations=iterations_count, min_iterations=iterations_count+1,
                         damping=.4, covariance_mode='isotropic')


def _policy():
    return dict(start=1, interval=1, sweeps=1, fit_offset=False,
                phase_tolerance=.005, settle_iterations=2)


def _proposal(beta, *, change=0.):
    return beta+change, np.zeros_like(beta), dict(
        prediction_change=abs(change), covariance_change=abs(change), seconds=0.)


def test_small_phase_trials_preserve_base_receiver_and_variance_learning(monkeypatch):
    raw, beta, controls = _input(), np.array([.3, -.2, .1]), _controls()

    def small(observation, pilot, mean, variance, noise, current, **kwargs):
        return _proposal(current)

    monkeypatch.setattr(iterations, 'update', small)
    actual, slopes, steps, trials = iterations.infer(raw, GaussianDenoiser(), scale=.7,
        initial_variance=.4, controls=controls, policy=_policy(), initial_slopes=beta)
    expected = run_spatial_score(raw.at_estimated_phase(beta), GaussianDenoiser(), scale=.7,
        initial_variance=.4, config=controls)
    for field in ('estimate', 'conditional_matrix', 'probabilities', 'spatial_covariance'):
        np.testing.assert_array_equal(getattr(actual, field), getattr(expected, field))
    np.testing.assert_array_equal(slopes, beta)
    assert not steps and len(trials) == controls.iterations
    assert all(not trial['applied'] for trial in trials)
    for index in range(1, len(actual.trace)):
        assert actual.trace[index]['query_variance_ratio'] == actual.trace[index-1]['next_query_variance_ratio']


def test_early_updates_need_no_conditional_stability_and_return_current_operator(monkeypatch):
    raw, beta, controls = _input(), np.zeros(3), _controls(iterations_count=4)
    linear_type = iterations.SpatialLinear
    used_operators, states = [], []

    class RecordingLinear(linear_type):
        def __init__(self, operator, *args):
            super().__init__(operator, *args)
            self.operator = operator.copy()

        def update(self, *args):
            used_operators.append(self.operator.copy())
            return super().update(*args)

    class NeverFresh(GaussianDenoiser):
        def __call__(self, *args):
            state = super().__call__(*args)
            self.message_fresh = False
            return state

    def change(observation, pilot, mean, variance, noise, current, **kwargs):
        return _proposal(current, change=.1)

    def observe(row, state, *args):
        states.append(state.mean.copy())

    monkeypatch.setattr(iterations, 'SpatialLinear', RecordingLinear)
    monkeypatch.setattr(iterations, 'update', change)
    result, slopes, steps, trials = iterations.infer(raw, NeverFresh(), scale=.7,
        initial_variance=.4, controls=controls, policy=_policy(), initial_slopes=beta,
        observer=observe)
    assert [trial['after_iteration'] for trial in steps] == [1, 2, 3]
    assert not trials[-1]['applied']
    assert result.stopping_reason == 'MAX_ITERATIONS'
    np.testing.assert_allclose(slopes, .3)
    np.testing.assert_array_equal(used_operators[-1], phase_operator(raw.pilot, slopes))
    np.testing.assert_array_equal(result.estimate, states[-1]*.7)


def test_direct_iteration_does_not_call_physical_frontend(monkeypatch):
    from system.receiver import phase_estimation

    def prohibited(*args, **kwargs):
        raise AssertionError('Physical initialization must not be called')

    monkeypatch.setattr(phase_estimation, 'estimate', prohibited)
    raw = _input()
    result, slopes, _, _ = iterations.infer(raw, GaussianDenoiser(), scale=.7,
        initial_variance=.4, controls=_controls(iterations_count=3),
        policy=_policy(), initial_slopes=np.zeros(raw.pilot.shape[1]))
    assert np.isfinite(result.estimate).all() and np.isfinite(slopes).all()


def test_column_moment_is_the_positive_partial_trace_not_a_reshape_average():
    rng = np.random.default_rng(95)
    rows, n = 3, 2
    factor = rng.normal(size=(rows*n, rows*n))+1j*rng.normal(size=(rows*n, rows*n))
    full = factor@factor.conj().T
    expected = sum(full[r*n:(r+1)*n, r*n:(r+1)*n] for r in range(rows))/rows
    actual = column_moment(full, rows, n)
    np.testing.assert_allclose(actual, expected, rtol=1e-14, atol=1e-14)
    np.testing.assert_allclose(np.trace(actual), np.trace(full)/rows, rtol=1e-14)
    assert np.linalg.eigvalsh(actual).min() > 0


def test_cycle_mode_requires_conditional_stability(monkeypatch):
    def prohibited(*args, **kwargs):
        raise AssertionError('Unstable conditional messages must not update phase')

    class NeverFresh(GaussianDenoiser):
        def __call__(self, *args):
            state = super().__call__(*args)
            self.message_fresh = False
            return state

    monkeypatch.setattr(iterations, 'update', prohibited)
    raw = _input()
    policy = dict(_policy(), stopping_mode='cycle')
    result, slopes, steps, trials = iterations.infer(raw, NeverFresh(), scale=.7,
        initial_variance=.4, controls=_controls(iterations_count=8), policy=policy,
        initial_slopes=np.zeros(raw.pilot.shape[1]))
    assert not steps and not trials
    assert all(not row['phase_update_eligible'] for row in result.trace)
    assert result.stopping_reason == 'MAX_ITERATIONS'
