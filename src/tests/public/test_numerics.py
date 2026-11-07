"""Weight-free numerical contracts for the distributed source."""
import numpy as np
import pytest

from channel.observation import ReceiverInput
from experiment.demo import least_squares, run
from experiment.metrics import score_arrays
from waveform.pilot import PartialDFTPilot
from waveform.afdm.continuous import continuous_path_matrix


def test_pilot_fft_dense_and_adjoint_agree():
    pilot = PartialDFTPilot(3, 8, 417)
    rng = np.random.default_rng(28)
    x = rng.normal(size=(48, 4)) + 1j * rng.normal(size=(48, 4))
    y = rng.normal(size=(8, 4)) + 1j * rng.normal(size=(8, 4))
    np.testing.assert_allclose(pilot.forward(x), pilot.dense() @ x, atol=1e-12)
    np.testing.assert_allclose(np.vdot(pilot.forward(x), y), np.vdot(x, pilot.adjoint(y)), atol=1e-12)
    np.testing.assert_allclose(pilot.dense() @ pilot.dense().conj().T, 3 * np.eye(8), atol=1e-12)


def test_zero_delay_doppler_channel_is_identity():
    h = continuous_path_matrix(16, 0., 0., 1e-6, 32, 3/32, .001)
    np.testing.assert_allclose(h, np.eye(16), atol=2e-13)


@pytest.mark.parametrize('delay,doppler', [(2., 500.), (2.37, -700.5), (35.2, 100.25)])
def test_frame_origin_changes_only_doppler_rotation(delay, doppler):
    first = continuous_path_matrix(16, delay, doppler, 1e-6, 32, 3/32, .001)
    next_frame = continuous_path_matrix(16, delay, doppler, 1e-6, 80, 3/32, .001)
    np.testing.assert_allclose(next_frame, np.exp(2j*np.pi*doppler*48e-6)*first, atol=2e-13)


def test_noiseless_ls_recovers_complete_complex_channel():
    rng = np.random.default_rng(654)
    p = PartialDFTPilot(2, 32, 139).dense().reshape(32, 2, 16)
    h = rng.normal(size=(2, 4, 16, 16)) + 1j*rng.normal(size=(2, 4, 16, 16))
    y = np.einsum('qkn,kmrn->qmr', p, h)
    estimated, _ = least_squares(ReceiverInput(y, p, 1., .5))
    np.testing.assert_allclose(estimated, h, atol=2e-13)


def test_demo_is_deterministic_and_does_not_load_weights():
    a, truth, estimate = run()
    b, other_truth, other_estimate = run()
    np.testing.assert_array_equal(truth, other_truth)
    np.testing.assert_array_equal(estimate, other_estimate)
    assert a['nmse_db'] == b['nmse_db']
    assert np.isfinite(a['nmse_db']) and a['pilot_condition_number'] < 1e5
    assert not a['weights_loaded'] and not a['formal_experiment_started']


def test_scoring_keeps_inactive_error_and_both_detection_errors():
    h = np.array([2., 0., 1.]).reshape(3, 1, 1, 1)
    estimate = np.array([1., 1., 0.]).reshape(3, 1, 1, 1)
    score = score_arrays(dict(estimate=estimate, activity_decision=np.array([True, True, False])),
                         dict(channel=h, activity=np.array([True, False, True])))
    assert score['misses'] == score['false_alarms'] == 1
    assert score['full_error'] == 3 and score['inactive_error'] == 1
    assert score['signal_energy'] == 5
    assert score['nmse_db'] == pytest.approx(10*np.log10(3/5))
