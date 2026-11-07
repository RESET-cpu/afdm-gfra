"""Closed-form phase-coordinate optimum, descent and receiver integration."""
import numpy as np
import pytest
from algorithm.C_STMP_phase_coordinate_20261104 import phase, iterations
from algorithm.C_STMP_phase_shen_frames_20261103.moments import conditional_quadratic
from test_phase_shen_frames_20261103 import _case
import test_phase_conditional_schedule_20261104 as schedule_tests


@pytest.mark.parametrize('seed', [3, 19, 73, 93])
def test_each_coordinate_and_frozen_gaussian_marginal_decrease(seed):
    case = _case(seed=seed)
    proposed, report = phase.update(*case)
    assert report['conditional_after'] <= report['conditional_before'] + 1e-11
    assert report['after'] <= report['before'] + 1e-11
    assert max(report['coordinate_objective_changes']) <= 1e-11
    np.testing.assert_allclose(report['conditional_after']-report['conditional_before'],
        report['coordinate_change_sum'], rtol=1e-10, atol=1e-11)
    np.testing.assert_array_equal(proposed[0], case[-1][0])
    np.testing.assert_allclose(abs(proposed), 1., rtol=0., atol=5e-16)


def test_single_phase_matches_exhaustive_angle_search():
    # Synthetic algebra fixture, not a communication performance experiment.
    g = np.array([[[3.]], [[7.]]], complex)
    b = np.array([[.1j], [2.-3j]])
    current = np.array([[1.], [np.exp(.8j)]])
    proposed, _ = phase.rotations(current, g, b, .1)
    np.testing.assert_allclose(proposed[1, 0], b[1, 0]/abs(b[1, 0]), atol=1e-15)
    grid = np.exp(1j*np.linspace(-np.pi, np.pi, 20001))
    exact = 7.-2*np.real(proposed[1, 0].conjugate()*b[1, 0])
    assert exact <= np.min(7.-2*np.real(grid.conj()*b[1, 0]))+1e-13


def test_zero_information_and_diagonal_loading_leave_update_unchanged():
    case = _case(seed=73)
    gram, matched, _ = conditional_quadratic(*case)
    a, _ = phase.rotations(case[-1], gram, matched, case[-2])
    b, _ = phase.rotations(case[-1], gram+5*np.eye(gram.shape[-1]), matched, case[-2])
    np.testing.assert_allclose(a, b, rtol=1e-12, atol=1e-12)
    old = case[-1]
    unchanged, report = phase.rotations(old, np.zeros_like(gram), np.zeros_like(matched), case[-2])
    np.testing.assert_array_equal(old, unchanged)
    assert not report['moved']


@pytest.mark.parametrize('name', [
    'test_continuity_and_current_proposal_stopping_without_modulo_wait',
    'test_small_first_proposal_can_stop_without_forced_phase_update',
    'test_small_channel_change_alone_does_not_stop',
    'test_invalid_moments_prevent_update_and_stopping',
    'test_initial_conditional_minimum_is_honored'])
def test_actual_new_iteration_uses_same_verified_schedule(monkeypatch, name):
    monkeypatch.setattr(schedule_tests, 'iterations', iterations)
    getattr(schedule_tests, name)(monkeypatch)
