import numpy as np

from algorithm.proposed.covariance_phase import Controls, correlation_grid, covariance_atoms, estimate
from system.pilot import PartialDFTPilot


def test_fft_phase_correlation_matches_direct():
    rng = np.random.default_rng(123)
    x = rng.normal(size=(7, 7))+1j*rng.normal(size=(7, 7))
    y = rng.normal(size=(7, 7))+1j*rng.normal(size=(7, 7))
    lag = np.arange(7)[:, None]-np.arange(7)[None]
    expected = [np.vdot(x*np.exp(1j*lag*b), y).real for b in 2*np.pi*np.arange(64)/64]
    np.testing.assert_allclose(correlation_grid(x, y, 64), expected, atol=1e-12)


def test_unitary_single_user_phase_without_true_channel_input():
    rng = np.random.default_rng(456)
    p = PartialDFTPilot(1, 8, 789, input_size=16).dense().reshape(8, 1, 16)
    # With only one user partial DFT rows are orthogonal, hence phase is
    # unidentifiable from this covariance. Use a valid nonorthogonal pilot.
    p = rng.normal(size=(8, 1, 16))+1j*rng.normal(size=(8, 1, 16))
    p /= np.linalg.norm(p, axis=-1, keepdims=True)
    h, _ = np.linalg.qr(rng.normal(size=(16,16))+1j*rng.normal(size=(16,16)))
    true_phase = np.exp(1j*np.arange(8)*1.2345)
    y = (true_phase[:, None]*(p[:,0] @ h))[:,None,:]
    arrays, record = estimate(y, p, Controls(sweeps=2))
    np.testing.assert_allclose(arrays['phase'][:,0], true_phase, atol=1e-6)
    assert record['objective'][-1] < 1e-14


def test_row_orthogonal_pilot_has_no_phase_information():
    p = PartialDFTPilot(1, 8, 789, input_size=16).dense().reshape(8, 1, 16)
    assert np.linalg.norm(covariance_atoms(p)) < 1e-12
