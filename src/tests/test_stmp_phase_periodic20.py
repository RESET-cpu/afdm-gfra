"""Original stopping may finish between updates spaced twenty iterations apart."""
from dataclasses import replace
import numpy as np

from algorithm.STMP import phase_iterations, phase_periodic_iterations as periodic
from algorithm.STMP.records import SpatialConfig
from test_stmp_phase import GaussianDenoiser, public_input
from test_stmp_phase_periodic import NeverFresh, fixed_change


def solve(denoiser, minimum=150):
    config=SpatialConfig(iterations=200,min_iterations=minimum,damping=.2,covariance_mode='isotropic',
        convergence_tolerance=100.,convergence_patience=5,decision_stability_window=10)
    return periodic.infer(public_input(),denoiser,scale=.27,initial_variance=.4,
        controls=config,initial_slopes=np.zeros(3),phase_configuration=dict(
            periodic_update=dict(start=20,interval=20),minimum_iterations_after_last_update=10))


def test_twenty_interval_can_stop_between_scheduled_updates(monkeypatch):
    monkeypatch.setattr(periodic,'update_phase',fixed_change)
    result,_,steps=solve(GaussianDenoiser(),minimum=151)
    assert len(result.trace)==151 and result.stopping_reason=='CONVERGED'
    assert [s['after_iteration'] for s in steps]==list(range(20,141,20))
    assert not result.trace[-1]['phase_update_due']
    assert result.trace[-1]['fresh_iterations']>=5
    assert result.trace[-1]['decision_stable_iterations']==11


def test_original_message_freshness_gate_is_required_again(monkeypatch):
    monkeypatch.setattr(periodic,'update_phase',fixed_change)
    result,_,steps=solve(NeverFresh())
    assert len(result.trace)==200 and result.stopping_reason=='MAX_ITERATIONS'
    assert [s['after_iteration'] for s in steps]==list(range(20,181,20))
    assert result.trace[-1]['fresh_iterations']==0
    assert 'cycle_stopping' not in result.trace[-1]


def test_actual_phase_solver_matches_fixed_twenty_step_schedule():
    config=SpatialConfig(iterations=60,min_iterations=60,damping=.2,covariance_mode='isotropic')
    raw=public_input()
    arguments=dict(scale=.27,initial_variance=.4,controls=config,initial_slopes=np.zeros(3))
    actual,beta,steps=periodic.infer(raw,GaussianDenoiser(),**arguments,phase_configuration=dict(
        periodic_update=dict(start=20,interval=20),minimum_iterations_after_last_update=10))
    expected,beta_expected,_=phase_iterations.infer(raw,GaussianDenoiser(),**arguments,
        phase_configuration=dict(update_after_iterations=[20,40],minimum_iterations_after_last_update=10))
    assert [s['after_iteration'] for s in steps]==[20,40]
    for name in ('estimate','conditional_matrix','probabilities','spatial_covariance'):
        np.testing.assert_array_equal(getattr(actual,name),getattr(expected,name))
    np.testing.assert_array_equal(beta,beta_expected)
