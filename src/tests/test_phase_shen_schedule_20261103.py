"""Small deterministic schedule checks, independent of physical data or networks.

The projection algebra is checked in test_phase_shen_frames_20261103.py.
Here analytic Gaussian queries and controlled channel sequences expose the
Algorithm 1 line-19 order, retained histories, and capped-run phase semantics.
No trained receiver, initial phase search, or simulation truth is loaded.
"""
from types import SimpleNamespace

import numpy as np
import pytest

from algorithm.C_STMP_phase_shen_schedule_20261103 import iterations
from algorithm.C_STMP_phase_shen_frames_20261103.phase import effective_pilot
from algorithm.STMP.records import SpatialConfig
from test_phase_direct_integration_20261103 import _input


def _controls(count):
    # These old stopping controls would prohibit all updates in the former loop.
    # The new outer schedule must ignore them and use only its explicit H test.
    return SpatialConfig(iterations=count, min_iterations=999, damping=.4,
        convergence_tolerance=1e-30, convergence_patience=999,
        decision_stability_window=999, activity_convergence_tolerance=1e-30,
        covariance_mode='isotropic')


class _AnalyticDenoiser:
    """Known Gaussian posterior; changing prior parameters expose both histories."""
    def __init__(self, events, channel_sequence=None):
        self.events = events
        self.channel_sequence = channel_sequence
        self.calls = 0
        self.message_fresh = True
        self.fresh_at_entry = []
        self.locations, self.variances = [], []
        self.last = {}

    def __call__(self, query, covariance):
        self.events.append('denoise')
        self.fresh_at_entry.append(self.message_fresh)
        self.calls += 1
        k, m = query.shape[:2]
        v = float(np.trace(covariance).real/m)
        tau = 1.+.2*self.calls
        location = (.19+.13j)*self.calls
        self.locations.append(location)
        self.variances.append(tau)
        posterior_mean = (tau*query+v*location)/(tau+v)
        if self.channel_sequence is not None:
            posterior_mean = np.full(query.shape, self.channel_sequence[self.calls-1], complex)
        probability = .8 if self.calls % 2 else .2
        self.last = dict(site_accepted=False, unsupported_users=k, rejected_site_users=k,
                         reused_site=True, probability_source='analytic_test_only')
        self.message_fresh = True
        return SimpleNamespace(mean=posterior_mean, conditional_mean=posterior_mean,
            activity=np.full(k, probability),
            spatial_covariance=np.broadcast_to(np.eye(m)*v*tau/(v+tau), (k, m, m)))


def _record_linear(monkeypatch, events):
    original = iterations.SpatialLinear
    calls = []

    class RecordingLinear(original):
        def __init__(self, operator, *args):
            self.saved_operator = operator.copy()
            super().__init__(operator, *args)

        def update(self, observation, prior, covariance):
            events.append('linear')
            result = super().update(observation, prior, covariance)
            calls.append(dict(operator=self.saved_operator.copy(), prior=prior.copy(),
                prior_covariance=covariance.copy(), raw_query=result[2].copy(),
                raw_covariance=result[3].copy()))
            return result

    monkeypatch.setattr(iterations, 'SpatialLinear', RecordingLinear)
    return calls


def _controlled_phase(monkeypatch, events):
    calls = []

    def update(observation, pilot, mean, variance, noise, current):
        events.append('phase')
        q, k = current.shape
        increment = .07*np.arange(q)[:, None]**2*(1+np.arange(k)[None])
        proposed = current*np.exp(1j*increment)
        calls.append((current.copy(), proposed.copy()))
        return proposed, dict(seconds=0., maximum_frame_increment=float(np.max(abs(increment))),
            before_phase_real=current.real.tolist(), before_phase_imag=current.imag.tolist(),
            after_phase_real=proposed.real.tolist(), after_phase_imag=proposed.imag.tolist())

    monkeypatch.setattr(iterations, 'update_phase', update)
    return calls


def _run(denoiser, *, count=4, tolerance=1e-30, observer=None, adapt=True):
    return iterations.infer(_input(), denoiser, scale=.7, initial_variance=.4,
        controls=_controls(count), stopping_tolerance=tolerance,
        observer=observer, adapt=adapt)


@pytest.mark.parametrize('scale', [1e-12, 1., 1e12])
@pytest.mark.parametrize('factor,expected', [(.99, True), (1.01, False)])
def test_line19_uses_squared_relative_change_without_scale_floor(scale, factor, expected):
    tolerance = 2.5e-7
    previous = scale*np.array([[1.+2j, -.3j], [2.-1j, -.5+.7j]])
    delta = factor*np.sqrt(tolerance)
    current = previous*(1+delta)
    stop, record = iterations.channel_stopping(current, previous, tolerance)
    assert stop is expected
    np.testing.assert_allclose(record['channel_squared_relative_change'], delta**2,
                               rtol=2e-11, atol=1e-20)


def test_line19_exact_boundary_and_zero_reference():
    # Exact binary boundary: 1^2 == .25 * 2^2.
    assert iterations.channel_stopping(np.array([3.+0j]), np.array([2.+0j]), .25)[0]
    assert not iterations.channel_stopping(np.array([3.+0j]), np.array([2.+0j]),
                                            np.nextafter(.25, 0.))[0]
    zero = np.zeros((2, 3), complex)
    stop, record = iterations.channel_stopping(zero, zero, 2.5e-7)
    assert stop and record['channel_squared_relative_change'] == 0.
    stop, record = iterations.channel_stopping(np.full_like(zero, 1e-12+2e-12j), zero, 2.5e-7)
    assert not stop and record['channel_squared_relative_change'] is None


def test_actual_projection_runs_every_nonterminal_round_without_site_or_stability_gate(monkeypatch):
    events = []
    linear = _record_linear(monkeypatch, events)
    original_update = iterations.update_phase
    phase_calls = []

    def tracked(*args):
        events.append('phase')
        phase_calls.append(args[-1].copy())
        return original_update(*args)

    monkeypatch.setattr(iterations, 'update_phase', tracked)
    denoiser = _AnalyticDenoiser(events)
    result, used, following, trials = _run(denoiser)
    assert result.stopping_reason == 'MAX_ITERATIONS'
    assert len(result.trace) == denoiser.calls == len(phase_calls) == len(trials) == 4
    assert events == ['linear', 'denoise', 'phase']*4
    np.testing.assert_array_equal(linear[0]['operator'], _input().pilot)
    np.testing.assert_array_equal(phase_calls[0], np.ones(_input().pilot.shape[:2]))
    assert all(row['site_accepted'] is False and row['unsupported_users'] == 3 for row in result.trace)
    assert all(row['phase_update_eligible'] and row['phase_update_applied'] for row in result.trace)
    assert [row['phase_updates_used_by_current_message'] for row in result.trace] == [0, 1, 2, 3]
    assert [row['phase_updates_completed'] for row in result.trace] == [1, 2, 3, 4]
    assert [trial['used_by_next_message_step'] for trial in trials] == [True, True, True, False]
    np.testing.assert_array_equal(linear[-1]['operator'], effective_pilot(_input().pilot, used))
    np.testing.assert_array_equal(used, phase_calls[-1])
    np.testing.assert_array_equal(following, np.asarray(trials[-1]['after_phase_real'])
                                  +1j*np.asarray(trials[-1]['after_phase_imag']))
    assert np.max(abs(following-used)) > 1e-6


def test_query_feedback_ratio_and_denoiser_histories_continue_across_phase_changes(monkeypatch):
    events = []
    raw = _input()
    linear = _record_linear(monkeypatch, events)
    _controlled_phase(monkeypatch, events)
    denoiser = _AnalyticDenoiser(events)
    observed = []

    def observe(row, state, query, covariance, prior, prior_covariance, out, out_covariance, *unused):
        observed.append(dict(mean=state.mean.copy(), query=query.copy(), covariance=covariance.copy(),
            prior=prior.copy(), prior_covariance=prior_covariance.copy(),
            out=out.copy(), out_covariance=out_covariance.copy()))

    result, used, following, trials = _run(denoiser, observer=observe)
    weight = _controls(4).damping
    expected_out, expected_covariance = None, None
    for index, (row, values) in enumerate(zip(result.trace, observed)):
        location = np.full(values['out'].shape, denoiser.locations[index], complex)
        covariance = np.eye(values['out_covariance'].shape[0])*denoiser.variances[index]
        expected_out = location if index == 0 else (1-weight)*expected_out+weight*location
        expected_covariance = covariance if index == 0 else (1-weight)*expected_covariance+weight*covariance
        # Analytic Gaussian cavity subtraction gives exactly this prior; this
        # reference does not call the production damping or extrinsic functions.
        np.testing.assert_allclose(values['out'], expected_out, rtol=2e-12, atol=2e-12)
        np.testing.assert_allclose(values['out_covariance'], expected_covariance, rtol=2e-12, atol=2e-12)
        operator = linear[index]['operator'].reshape(len(raw.pilot), -1)
        packed = values['mean'].transpose(0, 3, 1, 2).reshape(operator.shape[1], -1)
        expected_residual = np.mean(abs(raw.observation.reshape(len(raw.pilot), -1)/.7-operator@packed)**2)
        np.testing.assert_allclose(row['residual_power'], expected_residual, rtol=2e-13, atol=2e-13)
        if index == 0:
            continue
        previous_row, previous = result.trace[index-1], observed[index-1]
        assert row['query_variance_ratio'] == previous_row['next_query_variance_ratio']
        np.testing.assert_array_equal(values['prior'], previous['out'])
        np.testing.assert_array_equal(values['prior_covariance'], previous['out_covariance'])
        expected_query = (1-weight)*previous['query']+weight*linear[index]['raw_query']
        previous_raw = previous['covariance']/previous_row['query_variance_ratio']
        expected_raw = (1-weight)*previous_raw+weight*linear[index]['raw_covariance']
        np.testing.assert_allclose(values['query'], expected_query, rtol=2e-13, atol=2e-13)
        np.testing.assert_allclose(values['covariance'], expected_raw*row['query_variance_ratio'],
                                   rtol=2e-13, atol=2e-13)
    assert any(abs(row['query_variance_ratio']-1.) > 1e-3 for row in result.trace[1:])
    assert denoiser.fresh_at_entry == [True]*4
    assert all(not trial['query_damping_history_reset'] and not trial['query_variance_ratio_reset']
               and not trial['raw_variance_history_reset'] and not trial['stopping_windows_reset']
               for trial in trials)
    np.testing.assert_array_equal(result.estimate, observed[-1]['mean']*.7)
    np.testing.assert_array_equal(linear[-1]['operator'], effective_pilot(raw.pilot, used))


def test_overall_convergence_stops_before_phase_and_ignores_old_minimum_iterations(monkeypatch):
    events = []
    linear = _record_linear(monkeypatch, events)
    phase_calls = _controlled_phase(monkeypatch, events)
    denoiser = _AnalyticDenoiser(events, [.2+.1j, .2+.1j])
    result, used, following, trials = _run(denoiser, count=6, tolerance=2.5e-7, adapt=False)
    assert result.stopping_reason == 'CONVERGED' and len(result.trace) == 2
    assert events == ['linear', 'denoise', 'phase', 'linear', 'denoise']
    assert len(phase_calls) == len(trials) == 1
    assert not result.trace[0]['converged'] and result.trace[1]['converged']
    assert result.trace[0]['previous_channel_norm_squared'] == 0.
    assert result.trace[1]['phase_update_applied'] is False
    assert result.trace[1]['current_phase_trial'] is None
    assert result.trace[1]['phase_updates_completed'] == 1
    np.testing.assert_array_equal(used, following)
    np.testing.assert_array_equal(used, phase_calls[0][1])
    np.testing.assert_array_equal(linear[-1]['operator'], effective_pilot(_input().pilot, used))


def test_zero_first_channel_obeys_line19_and_never_updates_phase(monkeypatch):
    events = []
    _record_linear(monkeypatch, events)
    phase_calls = _controlled_phase(monkeypatch, events)
    result, used, following, trials = _run(_AnalyticDenoiser(events, [0.]), count=3, adapt=False)
    assert result.stopping_reason == 'CONVERGED' and len(result.trace) == 1
    assert events == ['linear', 'denoise'] and not phase_calls and not trials
    np.testing.assert_array_equal(used, np.ones(_input().pilot.shape[:2]))
    np.testing.assert_array_equal(following, used)


@pytest.mark.parametrize('count', [1, 3])
def test_hard_cap_saves_unconsumed_next_phase_and_returns_phase_used_for_channel(monkeypatch, count):
    events = []
    linear = _record_linear(monkeypatch, events)
    calls = _controlled_phase(monkeypatch, events)
    sequence = [(.2+.1j)*(index+1) for index in range(count)]
    result, used, following, trials = _run(_AnalyticDenoiser(events, sequence), count=count, adapt=False)
    assert result.stopping_reason == 'MAX_ITERATIONS'
    assert len(result.trace) == len(calls) == len(trials) == count
    assert events == ['linear', 'denoise', 'phase']*count
    np.testing.assert_array_equal(used, calls[-1][0])
    np.testing.assert_array_equal(following, calls[-1][1])
    assert np.max(abs(following-used)) > .1
    np.testing.assert_array_equal(linear[-1]['operator'], effective_pilot(_input().pilot, used))
    np.testing.assert_array_equal(result.estimate, np.full(result.estimate.shape, sequence[-1])*.7)
    assert trials[-1]['applied'] and not trials[-1]['used_by_next_message_step']
    assert result.trace[-1]['phase_updates_used_by_current_message'] == count-1
    assert result.trace[-1]['phase_updates_completed'] == count
    np.testing.assert_array_equal(used[0], np.ones(3))
    np.testing.assert_array_equal(following[0], np.ones(3))
