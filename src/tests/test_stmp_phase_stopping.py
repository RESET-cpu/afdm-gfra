"""Complete-cycle stopping uses observable outputs and preserves trajectories."""
import numpy as np
import pytest

from receiver.stmp.phase_stopping import CycleStopping


def settings(**kwargs):
    return dict(dict(comparison='completed_phase_update_cycles',consecutive_cycles=2,
        relative_tolerance=.005,activity_tolerance=.001,require_stable_decisions=10,
        require_raw_site_residual=False),**kwargs)


def check(stopping, iteration, *, mean=None, activity=None, prediction=None,
          input_covariance=None, feedback_covariance=None, current=True):
    values=dict(mean=np.ones((2,2,2,2)) if mean is None else mean,
        activity=np.array([.8,.001]) if activity is None else activity,
        prediction=np.ones((4,2,2)) if prediction is None else prediction,
        input_covariance=np.eye(2) if input_covariance is None else input_covariance,
        feedback_covariance=np.eye(2) if feedback_covariance is None else feedback_covariance)
    for _ in range(10):
        stopping.observe_decisions(values['activity'],.5,current_moments=current)
    return stopping.check(iteration,**values,noise_energy=1.)


def test_two_complete_cycles_and_minimum_iterations_are_required():
    s=CycleStopping(settings(),minimum_iterations=40)
    assert not check(s,10)['passed']
    assert check(s,20)['stable_cycles']==1
    assert not check(s,30)['stop']
    assert check(s,40)['stop']


@pytest.mark.parametrize('field,changed',[
    ('mean',np.ones((2,2,2,2))*1.01),
    ('prediction',np.ones((4,2,2))*1.01),
    ('activity',np.array([.802,.001])),
    ('input_covariance',np.eye(2)*1.01),
    ('feedback_covariance',np.eye(2)*1.01),
])
def test_each_changed_output_prevents_stopping_and_resets_cycle_count(field,changed):
    s=CycleStopping(settings(),minimum_iterations=1)
    check(s,10)
    assert check(s,20)['passed']
    result=check(s,30,**{field:changed})
    assert not result['stop'] and result['stable_cycles']==0


def test_small_probability_change_cannot_hide_a_recent_decision_flip():
    s=CycleStopping(settings(),minimum_iterations=1)
    check(s,10,activity=np.array([.5001,.001]))
    check(s,20,activity=np.array([.5001,.001]))
    for _ in range(9): s.observe_decisions(np.array([.5001,.001]),.5)
    s.observe_decisions(np.array([.4999,.001]),.5)
    result=s.check(30,np.ones((2,2,2,2)),np.array([.4999,.001]),
        np.ones((4,2,2)),np.eye(2),np.eye(2),noise_energy=1.)
    assert result['changes']['activity_change']<.001
    assert not result['stop'] and result['decision_stable_iterations']==1


def test_unsupported_or_retained_moments_cannot_count_as_stable_current_updates():
    s=CycleStopping(settings(),minimum_iterations=1)
    check(s,10)
    check(s,20)
    assert not check(s,30,current=False)['stop']


def test_previous_cycle_reference_is_copied_and_kept_in_physical_coordinates():
    s=CycleStopping(settings(),minimum_iterations=1)
    mean=np.ones((2,2,2,2),complex)
    check(s,10,mean=mean)
    mean*=np.exp(.1j)
    result=check(s,20,mean=mean)
    assert result['changes']['channel_change']>.09
    assert not result['passed']


def test_phase_operator_changes_are_detected_even_with_unchanged_channel():
    s=CycleStopping(settings(),minimum_iterations=1)
    check(s,10)
    result=check(s,20,prediction=np.ones((4,2,2))*np.exp(.1j))
    assert result['changes']['channel_change']==0
    assert result['changes']['prediction_change']>.09 and not result['passed']




def test_nonfinite_output_is_not_a_stable_solution():
    s=CycleStopping(settings(),minimum_iterations=1)
    with pytest.raises(FloatingPointError): check(s,10,mean=np.full((2,2,2,2),np.nan))


@pytest.mark.parametrize('override',[{'relative_tolerance':0.},{'activity_tolerance':float('nan')},
    {'consecutive_cycles':0},{'require_stable_decisions':True}])
def test_invalid_stopping_settings(override):
    with pytest.raises(ValueError): CycleStopping(settings(**override),minimum_iterations=1)
