"""Formula parity and independent derivatives for the candidate frontend."""
import numpy as np
from afdm_jadcedd.algorithm import phase_estimation as original
from afdm_jadcedd.algorithm import phase_estimation_candidate as candidate
from afdm_jadcedd.algorithm import phase_candidate_atoms as atoms
from afdm_jadcedd.algorithm.unknown_phase_model import sensed_atom
from afdm_jadcedd.system.pilot import PartialDFTPilot
from afdm_jadcedd.algorithm import phase_candidate_screening as screening
from afdm_jadcedd.algorithm import phase_estimation_vectorized as vectorized
from afdm_jadcedd.algorithm.unknown_phase_model import UnknownPhaseInput, FRAME_DURATION_S
from afdm_jadcedd.system import config as cfg
from afdm_jadcedd.system.phase import wrap
from threadpoolctl import threadpool_limits


def test_atoms_and_first_derivatives_preserve_original_arithmetic():
    p = PartialDFTPilot(2, 16, 20261017011).dense().reshape(16, 2, 16)
    for position in [(2.373, .213), (.001, -1.32), (15.991, 1.21)]:
        for user in range(2):
            a, d, _ = sensed_atom(p, user, position, derivatives=True)
            b, e, unused = atoms.sensed_atom(p, user, position, derivatives=True)
            np.testing.assert_array_equal(a, b)
            np.testing.assert_array_equal(d, e)
            assert unused is None


def test_batched_screening_matches_explicit_phase_dictionary():
    rng = np.random.default_rng(20261017012)
    raw = rng.normal(size=(3, 6, 4))+1j*rng.normal(size=(3, 6, 4))
    y = rng.normal(size=(6, 4, 2))+1j*rng.normal(size=(6, 4, 2))
    scores = candidate.coarse_scores(raw, y, 32, True)
    np.testing.assert_allclose(scores, original.coarse_scores(raw, y, 32), rtol=1e-13, atol=1e-13)
    for g in range(3):
        for b in range(32):
            a = raw[g]*np.exp(2j*np.pi*np.arange(6)*b/32)[:, None]
            corr = np.einsum('qr,qrm->m', a.conj(), y)
            expected = np.sum(abs(corr)**2)/np.sum(abs(a)**2)
            np.testing.assert_allclose(scores[g, b], expected, rtol=1e-12, atol=1e-12)


def test_candidate_gradient_matches_finite_difference():
    rng = np.random.default_rng(20261017013)
    p = PartialDFTPilot(2, 16, 20261017013).dense().reshape(16, 2, 16)
    y = rng.normal(size=(256, 3))+1j*rng.normal(size=(256, 3))
    position = np.array([2.373, .213])
    loss, grad = candidate.objective(position, p, 1, y)
    old_loss, old_grad = original.objective(position, p, 1, y)
    assert loss == old_loss
    np.testing.assert_array_equal(grad, old_grad)
    for j, eps in enumerate([1e-6, 1e-7]):
        delta = np.eye(2)[j]*eps
        plus = candidate.objective(position+delta, p, 1, y)[0]
        minus = candidate.objective(position-delta, p, 1, y)[0]
        np.testing.assert_allclose(grad[j], (plus-minus)/(2*eps), rtol=2e-6, atol=2e-5)


def test_batched_alias_atoms_and_selection_preserve_physical_dictionary():
    rng = np.random.default_rng(20261017014)
    p = PartialDFTPilot(2, 16, 20261017014).dense().reshape(16, 2, 16)
    pos = np.column_stack([rng.uniform(0, 16, 25), rng.uniform(-1.36, 1.36, 25)])
    actual = screening.atoms_at_positions(p, 1, pos)
    expected = np.stack([sensed_atom(p, 1, x) for x in pos])
    np.testing.assert_allclose(actual, expected, rtol=1e-13, atol=1e-13)
    y = rng.normal(size=(256, 3))+1j*rng.normal(size=(256, 3))
    peaks = [(2.3, 1.5, 1), (5.7, 2.1, 1), (10.6, .01, 1)]
    old = original.physical_candidates(p, 1, y, peaks, original.Controls(), pos[0])
    new = screening.physical_candidates(p, 1, y, peaks, original.Controls(), pos[0])
    np.testing.assert_array_equal(old, new)


def test_local_sweeps_recover_blind_path_and_do_not_use_supplied_noise():
    p = PartialDFTPilot(1, 16, 20261017015).dense().reshape(16, 1, 16)
    position = (2.373, .213)
    a = sensed_atom(p, 0, position)
    gains = np.array([.8+.1j, -.3+.7j, .2-.6j])
    y = (a[:, None]*gains).reshape(16, 16, 3).transpose(0, 2, 1)
    controls = vectorized.Controls(batched_correlations=True, local_second_sweep=True, sweeps=3)
    with threadpool_limits(1):
        first, record = vectorized.estimate(UnknownPhaseInput(y, p, 1e-8, .1), controls)
        second, _ = vectorized.estimate(UnknownPhaseInput(y, p, 2., .9), controls)
    for key in first:
        np.testing.assert_array_equal(first[key], second[key])
    expected = wrap(2*np.pi*position[1]*cfg.DELTA_F_HZ*FRAME_DURATION_S)
    assert abs(wrap(first['phase_slopes'][0]-expected)) < 1e-4
    assert np.linalg.norm(first['fitted_observation']-y)/np.linalg.norm(y) < 1e-4
    assert all(r['residual_energy'] <= r['previous_residual_energy']+1e-9 for r in record['trace'])
    assert not record['truth_used_in_inference'] and not record['known_activity_used']
