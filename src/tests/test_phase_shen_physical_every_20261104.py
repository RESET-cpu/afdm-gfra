"""Test nonzero initialization, phase consumption and continuous scheduling."""
import numpy as np
import pytest
from algorithm.C_STMP_phase_shen_physical_every_20261104 import iterations
from algorithm.C_STMP_phase_shen_schedule_20261103 import iterations as old
from algorithm.C_STMP_phase_shen_frames_20261103.phase import effective_pilot
from test_phase_direct_integration_20261103 import _input
from test_phase_shen_schedule_20261103 import _controls, _AnalyticDenoiser


def test_all_one_special_case_matches_frozen_schedule():
    raw = _input()
    kw = dict(scale=.7, initial_variance=.4, controls=_controls(4), stopping_tolerance=1e-30)
    a = old.infer(raw, _AnalyticDenoiser([]), **kw)
    b = iterations.infer(raw, _AnalyticDenoiser([]), initial_phase=np.ones(raw.pilot.shape[:2]), **kw)
    for x, y in zip(a[1:3], b[1:3]):
        np.testing.assert_array_equal(x, y)
    np.testing.assert_array_equal(a[0].estimate, b[0].estimate)
    assert a[0].stopping_reason == b[0].stopping_reason


def test_nonzero_initial_phase_reaches_first_operator_and_updates_each_round(monkeypatch):
    raw = _input()
    phase = np.exp(1j*np.arange(len(raw.pilot))[:, None]*np.array([.3, -.8, 1.2])[None])
    before = phase.copy()
    original = iterations.SpatialLinear
    operators = []
    class Tracked(original):
        def __init__(self, a, *args):
            operators.append(a.copy())
            super().__init__(a, *args)
    monkeypatch.setattr(iterations, 'SpatialLinear', Tracked)
    result, used, following, trials = iterations.infer(raw, _AnalyticDenoiser([]), scale=.7,
        initial_variance=.4, controls=_controls(4), stopping_tolerance=1e-30, initial_phase=phase)
    np.testing.assert_array_equal(phase, before)
    np.testing.assert_array_equal(operators[0], effective_pilot(raw.pilot, before))
    assert len(trials) == len(result.trace) == 4
    assert [x['after_iteration'] for x in trials] == [1, 2, 3, 4]
    assert [x['used_by_next_message_step'] for x in trials] == [True, True, True, False]
    np.testing.assert_array_equal(operators[-2], effective_pilot(raw.pilot, used))
    np.testing.assert_array_equal(operators[-1], effective_pilot(raw.pilot, following))
    for i, row in enumerate(result.trace[1:], 1):
        assert row['query_variance_ratio'] == result.trace[i-1]['next_query_variance_ratio']
    assert all(not x['query_damping_history_reset'] for x in trials)


def test_nonzero_phase_stopping_does_not_apply_unused_update():
    raw = _input()
    phase = np.exp(1j*np.arange(len(raw.pilot))[:, None]*np.array([.3, -.8, 1.2])[None])
    result, used, following, trials = iterations.infer(raw, _AnalyticDenoiser([], [.1, .1]),
        scale=.7, initial_variance=.4, controls=_controls(6), stopping_tolerance=2.5e-7,
        initial_phase=phase, adapt=False)
    assert result.stopping_reason == 'CONVERGED' and len(result.trace) == 2
    assert len(trials) == 1
    np.testing.assert_array_equal(used, following)


@pytest.mark.parametrize('kind', ['shape', 'reference', 'magnitude', 'nan'])
def test_invalid_phase_rejected(kind):
    raw = _input(); phase = np.ones(raw.pilot.shape[:2], complex)
    if kind == 'shape': phase = phase[:, :1]
    elif kind == 'reference': phase[0, 0] = 1j
    elif kind == 'magnitude': phase[1, 0] = .5
    else: phase[1, 0] = np.nan
    with pytest.raises(ValueError, match='initial phases'):
        iterations.infer(raw, _AnalyticDenoiser([]), scale=.7, initial_variance=.4,
            controls=_controls(3), stopping_tolerance=2.5e-7, initial_phase=phase)
