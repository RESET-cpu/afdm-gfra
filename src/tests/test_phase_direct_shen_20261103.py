"""Small algebraic checks for the optional Shen projected-solve comparator."""
import numpy as np
from algorithm.C_STMP_phase_direct_20261103.shen_update import rotations
from algorithm.proposed.phase_math import quadratic_objective


def test_diagonal_solve_recovers_exact_common_slopes():
    frames, users = 5, 2
    slopes = np.array([.43, -.71])
    phase = np.exp(1j * np.arange(frames)[:, None] * slopes)
    diagonal = np.arange(1, frames * users + 1).reshape(frames, users)
    gram = np.array([np.diag(d) for d in diagonal], complex)
    noise = .3
    amplitude = np.array([.4, 1.7])[None, :]
    matched = (diagonal + noise) * amplitude * phase
    new, angle, record = rotations(np.array([-.2, .8]), gram, matched, noise)
    np.testing.assert_allclose(np.angle(np.exp(1j * (new - slopes))), 0., atol=2e-12)
    np.testing.assert_array_equal(angle, np.zeros(users))
    assert record['linear_solve_relative_residual'] < 1e-15
    assert record['frame_unit_modulus_error'] < 1e-15
    assert record['frame_zero_gauge_error'] == 0
    assert record['slope_projection_squared_error'] < 1e-23
    assert record['after_slope_projection'] < record['before']
    # Unit-circle projection changes magnitudes, so A phi=b need not hold.
    assert record['unitmod_linear_relative_residual'] > .01


def test_q0_is_fixed_and_zero_solutions_keep_old_phase():
    beta = np.array([.31, -.66])
    gram = np.broadcast_to(np.eye(2), (4, 2, 2)).copy()
    matched = np.zeros((4, 2), complex)
    new, angle, record = rotations(beta, gram, matched, .5)
    np.testing.assert_allclose(np.angle(np.exp(1j * (new - beta))), 0., atol=2e-12)
    np.testing.assert_array_equal(angle, [0., 0.])
    assert record['numerical_zero_components_kept'] == 8
    assert record['linear_solve_relative_residual'] == 0
    assert record['frame_zero_gauge_error'] == 0
    # A raw frame-zero phase inconsistent with AFDM is explicitly clamped.
    matched[0] = [1j, -1j]
    _, _, record = rotations(beta, gram, matched, .5)
    assert record['frame_zero_gauge_error'] == 0
    assert record['frame_unit_modulus_error'] < 1e-15


def test_guard_rejects_known_increasing_random_projection():
    rng = np.random.default_rng(2026110307)
    frames, users = 4, 3
    raw = rng.normal(size=(frames, users, users)) + 1j * rng.normal(size=(frames, users, users))
    gram = raw @ raw.conj().transpose(0, 2, 1) + .2 * np.eye(users)
    beta = rng.uniform(-np.pi, np.pi, users)
    old_phase = np.exp(1j * np.arange(frames)[:, None] * beta)
    # This b makes old_phase the unconstrained minimizer of the original
    # quadratic. Regularized solve + phase/slope projection can move away.
    matched = np.einsum('qkl,ql->qk', gram, old_phase)
    new, angle, unguarded = rotations(beta, gram, matched, .7, guard=False)
    actual = quadratic_objective(np.exp(1j * np.arange(frames)[:, None] * new), gram, matched)
    assert unguarded['after_slope_projection'] > unguarded['before'] + 1e-5
    np.testing.assert_allclose(actual, unguarded['after'], rtol=1e-13, atol=1e-13)
    assert unguarded['proposed_objective_materially_increased']
    assert unguarded['accepted'] and unguarded['applied_objective_increased']
    assert unguarded['linear_solve_relative_residual'] < 1e-14
    kept, kept_angle, guarded = rotations(beta, gram, matched, .7, guard=True)
    np.testing.assert_array_equal(kept, beta)
    np.testing.assert_array_equal(kept_angle, np.zeros(users))
    assert guarded['rejected_objective_increase'] and not guarded['accepted']
    assert guarded['after'] == guarded['before']
    assert not guarded['applied_objective_increased']
    np.testing.assert_allclose(guarded['after_slope_projection'], unguarded['after_slope_projection'])
