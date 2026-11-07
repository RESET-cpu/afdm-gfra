"""Original exits remain valid; full-cycle exits preserve the same trajectory."""
from dataclasses import replace
import numpy as np

from receiver.stmp import phase_periodic_combined_iterations as candidate
from receiver.stmp import phase_periodic_iterations as original
from receiver.stmp.records import SpatialConfig
from test_stmp_phase import GaussianDenoiser, public_input
from test_stmp_phase_periodic import NeverFresh, fixed_change
from test_stmp_phase_stopping import settings


def phase(**overrides):
    return dict(periodic_update=dict(start=20, interval=20),
        minimum_iterations_after_last_update=10,
        stopping=settings(allow_original_stopping=True, **overrides))


def solve(loop, denoiser, controls, configuration):
    return loop.infer(public_input(), denoiser, scale=.27, initial_variance=.4,
        controls=controls, initial_slopes=np.zeros(3), phase_configuration=configuration)


def test_original_exit_between_phase_updates_is_preserved(monkeypatch):
    monkeypatch.setattr(candidate, 'update_phase', fixed_change)
    control=SpatialConfig(iterations=200, min_iterations=151, damping=.2,
        covariance_mode='isotropic', convergence_tolerance=100.,
        convergence_patience=5, decision_stability_window=10)
    result, _, steps=solve(candidate, GaussianDenoiser(), control,
        phase(relative_tolerance=1e-12))
    assert len(result.trace)==151 and result.stopping_reason=='CONVERGED'
    last=result.trace[-1]
    assert last['stopping_trigger']=='original' and last['cycle_stopping'] is None
    assert [s['after_iteration'] for s in steps]==list(range(20, 141, 20))


def test_full_cycle_can_stop_without_raw_site_freshness_and_matches_prefix(monkeypatch):
    monkeypatch.setattr(candidate, 'update_phase', fixed_change)
    monkeypatch.setattr(original, 'update_phase', fixed_change)
    control=SpatialConfig(iterations=200, min_iterations=150, damping=.2,
        covariance_mode='isotropic', convergence_tolerance=100.,
        convergence_patience=5, decision_stability_window=10)
    config=phase(relative_tolerance=100.)
    result, slopes, steps=solve(candidate, NeverFresh(), control, config)
    assert len(result.trace)==160 and result.stopping_reason=='CONVERGED'
    assert result.trace[-1]['stopping_trigger']=='cycle'
    assert result.trace[-1]['fresh_iterations']==0
    assert [s['after_iteration'] for s in steps]==list(range(20, 160, 20))
    reference, expected_slopes, _=solve(original, NeverFresh(),
        replace(control, iterations=160), config)
    for name in ('estimate', 'conditional_matrix', 'probabilities', 'spatial_covariance'):
        np.testing.assert_array_equal(getattr(result, name), getattr(reference, name))
    np.testing.assert_array_equal(slopes, expected_slopes)


def test_actual_phase_solver_trajectory_is_unchanged_before_stopping():
    control=SpatialConfig(iterations=60, min_iterations=60, damping=.2,
        covariance_mode='isotropic')
    config=phase()
    result, slopes, steps=solve(candidate, GaussianDenoiser(), control, config)
    reference, expected_slopes, _=solve(original, GaussianDenoiser(), control, config)
    assert [s['after_iteration'] for s in steps]==[20, 40]
    for name in ('estimate', 'conditional_matrix', 'probabilities', 'spatial_covariance'):
        np.testing.assert_array_equal(getattr(result, name), getattr(reference, name))
    np.testing.assert_array_equal(slopes, expected_slopes)
