"""The stopping decision depends on the observable returned quantities."""
import numpy as np

from algorithm.STMP.phase_output_cycle_stopping import OutputCycleStopping


def test_internal_message_changes_do_not_mask_stable_outputs():
    config = dict(comparison="completed_phase_update_cycles", require_raw_site_residual=False,
                  relative_tolerance=.005, activity_tolerance=.001,
                  consecutive_cycles=2, require_stable_decisions=10)
    stopping = OutputCycleStopping(config, minimum_iterations=80)
    h = np.array([1., 0.])
    def check(iteration, activity, covariance, updates, channel=h):
        for _ in range(20):
            stopping.observe_decisions(activity, .5, current_moments=True)
        return stopping.check(iteration, channel, activity, channel,
            np.eye(2)*covariance, np.eye(2)*covariance, noise_energy=1.,
            phase_updates_completed=updates)
    assert not check(20, np.array([.8, .2]), 1., 0)["stop"]
    assert not check(40, np.array([.9, .1]), 2., 0)["passed"]
    assert not check(60, np.array([.85, .15]), 1., 0)["passed"]
    first = check(80, np.array([.95, .05]), 2., 1)
    assert first["passed"] and not first["stop"]
    second = check(100, np.array([.85, .15]), 1., 2)
    assert second["stop"] and second["changes"]["feedback_covariance_change"] > .005
    assert not check(120, np.array([.85, .15]), 1., 3, channel=np.array([1.1, 0.]))["stop"]


def test_invalid_moments_or_changed_decision_prevent_stopping():
    config = dict(comparison="completed_phase_update_cycles", require_raw_site_residual=False,
                  relative_tolerance=.005, activity_tolerance=.001,
                  consecutive_cycles=1, require_stable_decisions=10)
    stopping = OutputCycleStopping(config, minimum_iterations=80)
    p = np.array([.8, .2]); h = np.array([1., 0.])
    def check(i):
        return stopping.check(i,h,p,h,np.eye(2),np.eye(2),noise_energy=1.,phase_updates_completed=1)
    for _ in range(20):stopping.observe_decisions(p,.5)
    check(60)
    stopping.observe_decisions(p,.5,current_moments=False)
    assert not check(80)["stop"]
    for _ in range(20):stopping.observe_decisions(p,.5)
    stopping.observe_decisions(np.array([.4,.2]),.5)
    assert not check(100)["stop"]
