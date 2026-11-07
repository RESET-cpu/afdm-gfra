"""Periodic phase timing, cache consistency and stopping without a count cap."""
from dataclasses import replace

import numpy as np
import pytest

from algorithm.STMP import phase_iterations, phase_periodic_iterations as periodic
from algorithm.STMP.records import SpatialConfig
from test_stmp_phase import GaussianDenoiser, public_input


def controls(**kwargs):
    return replace(SpatialConfig(iterations=200, min_iterations=150, damping=.2,
        covariance_mode='isotropic', convergence_tolerance=100.,
        convergence_patience=2, decision_stability_window=10), **kwargs)


def solve(config, denoiser=None, **phase):
    return periodic.infer(public_input(), denoiser or GaussianDenoiser(),
        scale=.27, initial_variance=.4, controls=config, initial_slopes=np.zeros(3),
        phase_configuration=dict(periodic_update=dict(start=10, interval=10),
                                 minimum_iterations_after_last_update=10, **phase))


def fixed_change(*args):
    return args[-2]+.01, np.full(3, .02), {'conditional_quadratic': {'users': []}}


def test_periodic_stops_before_next_update_and_resets_all_windows(monkeypatch):
    monkeypatch.setattr(periodic, 'update_phase', fixed_change)
    result, slopes, steps = solve(controls())
    assert len(result.trace) == 150 and result.stopping_reason == 'CONVERGED'
    assert [s['after_iteration'] for s in steps] == list(range(10, 150, 10))
    assert len(steps) == 14  # More than the previous nine-update cap.
    assert result.trace[-1]['phase_update_skipped'] == 'conditional_stmp_converged'
    assert result.trace[-1]['decision_stable_iterations'] == 10
    assert result.trace[140]['decision_stable_iterations'] == 1
    assert result.trace[140]['fresh_iterations'] == 1
    assert result.trace[140]['stable_iterations'] == 1
    assert all(not r['converged'] for r in result.trace[:-1])
    np.testing.assert_allclose(slopes, .14)


def test_no_stale_convergence_before_first_update_or_during_refinement(monkeypatch):
    monkeypatch.setattr(periodic, 'update_phase', fixed_change)
    result, _, steps = solve(controls(min_iterations=1, decision_stability_window=2))
    assert len(result.trace) == 20
    assert [s['after_iteration'] for s in steps] == [10]
    assert result.trace[-1]['iterations_since_last_phase_update'] == 10


class NeverFresh(GaussianDenoiser):
    def __call__(self, *args):
        state = super().__call__(*args)
        self.message_fresh = False
        return state


def test_updates_continue_past_140_and_max_returns_current_phase_channel(monkeypatch):
    monkeypatch.setattr(periodic, 'update_phase', fixed_change)
    monkeypatch.setattr(phase_iterations, 'update_phase', fixed_change)
    config = controls(iterations=200)
    actual, slopes, steps = solve(config, NeverFresh())
    schedule = list(range(10, 200, 10))
    assert [s['after_iteration'] for s in steps] == schedule
    assert actual.stopping_reason == 'MAX_ITERATIONS' and len(actual.trace) == 200
    assert actual.trace[-1]['phase_update_skipped'] == 'final_conditional_refinement'
    expected, expected_slopes, _ = phase_iterations.infer(public_input(), NeverFresh(),
        scale=.27, initial_variance=.4, controls=config, initial_slopes=np.zeros(3),
        phase_configuration=dict(update_after_iterations=schedule,
                                 minimum_iterations_after_last_update=10))
    for field in ('estimate', 'conditional_matrix', 'probabilities', 'spatial_covariance'):
        np.testing.assert_array_equal(getattr(actual, field), getattr(expected, field))
    np.testing.assert_array_equal(slopes, expected_slopes)


def test_real_gaussian_solver_matches_fixed_schedule_at_the_same_endpoint():
    config = controls(iterations=30, min_iterations=30)
    actual, slopes, steps = solve(config)
    expected, expected_slopes, _ = phase_iterations.infer(public_input(), GaussianDenoiser(),
        scale=.27, initial_variance=.4, controls=config, initial_slopes=np.zeros(3),
        phase_configuration=dict(update_after_iterations=[10, 20],
                                 minimum_iterations_after_last_update=10))
    assert [s['after_iteration'] for s in steps] == [10, 20]
    assert all(s['after'] <= s['before']+1e-9 for s in steps)
    for field in ('estimate', 'conditional_matrix', 'probabilities', 'spatial_covariance'):
        np.testing.assert_array_equal(getattr(actual, field), getattr(expected, field))
    np.testing.assert_array_equal(slopes, expected_slopes)


@pytest.mark.parametrize('start,interval,settle', [(0,10,10), (10,0,10), (10,10,0),
                                                (10,5,10), (195,10,10), (True,10,10)])
def test_invalid_periodic_controls(start, interval, settle):
    with pytest.raises(ValueError, match='final conditional refinement'):
        periodic.infer(public_input(), GaussianDenoiser(), scale=.27, initial_variance=.4,
            controls=controls(), initial_slopes=np.zeros(3),
            phase_configuration=dict(periodic_update=dict(start=start,interval=interval),
                                     minimum_iterations_after_last_update=settle))
