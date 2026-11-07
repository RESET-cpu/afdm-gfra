"""Small deterministic M-step checks without a trained model or true channel.

References are explicit observation operators and a dense independent-user
Bernoulli--Gaussian covariance, rather than a second use of the implementation's
Gram construction.  No claim about outer-loop EM or detection monotonicity is
tested or assumed here.
"""
import numpy as np
import pytest

from algorithm.C_STMP_phase_em_20261103 import phase


def _normal(rng, shape):
    return (rng.normal(size=shape)+1j*rng.normal(size=shape))/np.sqrt(2)


def _case(seed=21, q=7, k=3, m=2, r=3, n=2):
    rng = np.random.default_rng(seed)
    return (_normal(rng, (q, m, r)), _normal(rng, (q, k, n)),
            _normal(rng, (k, m, r, n)), rng.uniform(-np.pi, np.pi, k))


def _prediction(pilot, mean, beta):
    """Literal per-frame/user contraction, independent of production einsums."""
    q, k, _ = pilot.shape
    out = np.zeros((q, *mean.shape[1:3]), complex)
    for frame in range(q):
        for user in range(k):
            out[frame] += np.exp(1j*frame*beta[user])*(mean[user]@pilot[frame, user])
    return out


def _residual(y, pilot, mean, beta):
    error = y-_prediction(pilot, mean, beta)
    return float(np.vdot(error, error).real)


def _dense_operator(pilot, beta, d):
    q, k, n = pilot.shape
    result = np.zeros((q*d, k*d*n), complex)
    for frame in range(q):
        for user in range(k):
            for column in range(d):
                start = (user*d+column)*n
                result[frame*d+column, start:start+n] = (
                    np.exp(1j*frame*beta[user])*pilot[frame, user])
    return result


@pytest.mark.parametrize("q", [1, 2, 7])
def test_gram_value_and_beta_gradient_against_direct_observation(q):
    y, pilot, mean, beta = _case(q=q)
    gram, matched, details = phase.projected_quadratic(y, pilot, mean)
    value, gradient = phase.value_gradient(beta, gram, matched)
    np.testing.assert_allclose(value+np.vdot(y, y).real,
                               _residual(y, pilot, mean, beta), atol=2e-12, rtol=2e-14)
    eps = 2e-6
    numeric = np.array([(_residual(y, pilot, mean, beta+eps*axis)
                         -_residual(y, pilot, mean, beta-eps*axis))/(2*eps)
                        for axis in np.eye(len(beta))])
    np.testing.assert_allclose(gradient, numeric, atol=1e-7, rtol=2e-8)
    assert details["moment_sum_coordinates"] == y.shape[1]*y.shape[2]
    assert details["projected_shape"] == [q, len(beta), y.shape[1]*y.shape[2]]
    assert details["max_gram_hermitian_error"] < 1e-12


def test_gradient_sign_and_local_solution_on_identifiable_single_user():
    # q=1 supplies a positive desired angle; its derivative at zero is negative.
    pilot = np.ones((2, 1, 1), complex)
    mean = np.ones((1, 1, 1, 1), complex)
    target = .47
    y = np.array([1, np.exp(1j*target)], complex).reshape(2, 1, 1)
    gram, matched, _ = phase.projected_quadratic(y, pilot, mean)
    _, gradient = phase.value_gradient(np.zeros(1), gram, matched)
    np.testing.assert_allclose(gradient, [-2*np.sin(target)], atol=1e-14)
    updated, report = phase.update(y, pilot, mean, np.zeros(1))
    np.testing.assert_allclose(updated, [target], atol=2e-7)
    assert report["mean_residual_energy_after"] < 1e-12
    assert report["accepted_steps"] > 0
    assert report["backtracks"] == 0
    assert report["seconds"] == report["elapsed_seconds"]
    assert report["seconds"] >= report["moments"]["elapsed_seconds"] >= 0


def test_independent_bg_covariance_is_phase_constant_even_when_not_isotropic():
    y, pilot, conditional, beta = _case(seed=38, q=4, k=3, m=2, r=3, n=2)
    rng = np.random.default_rng(81)
    k, m, r, n = conditional.shape
    probabilities = np.array([.13, .72, .91])
    joint = probabilities[:, None, None, None]*conditional
    size = m*r*n
    covariance = np.zeros((k*size, k*size), complex)
    for user in range(k):
        # Dense conditional covariance includes cross-row/column correlations.
        root = _normal(rng, (size, size))/np.sqrt(size)
        conditional_covariance = root@root.conj().T
        h = conditional[user].reshape(-1)
        p = probabilities[user]
        block = p*conditional_covariance+p*(1-p)*np.outer(h, h.conj())
        covariance[user*size:(user+1)*size, user*size:(user+1)*size] = block
    gram, matched, _ = phase.projected_quadratic(y, pilot, joint)
    updated, report = phase.minimize(beta, gram, matched)
    trials = [beta, updated, rng.uniform(-np.pi, np.pi, k)]
    covariance_terms, expected, quadratic = [], [], []
    for trial in trials:
        operator = _dense_operator(pilot, trial, m*r)
        error = y.reshape(-1)-operator@joint.reshape(-1)
        covariance_terms.append(np.trace(operator@covariance@operator.conj().T).real)
        expected.append(np.vdot(error, error).real+covariance_terms[-1])
        quadratic.append(phase.value_gradient(trial, gram, matched)[0])
    np.testing.assert_allclose(covariance_terms, covariance_terms[0], atol=2e-12, rtol=2e-14)
    np.testing.assert_allclose(np.diff(expected), np.diff(quadratic), atol=2e-12, rtol=2e-13)
    assert expected[1] <= expected[0]+1e-12
    assert report["objective_change"] < 0


def test_cross_user_covariance_would_break_the_constant_variance_assumption():
    # This is a scope check: a correlated posterior cannot be silently treated
    # as the user-independent posterior accepted by this M-step.
    pilot = np.ones((2, 2, 1), complex)
    covariance = np.array([[1, .6], [.6, 1]], complex)
    first = _dense_operator(pilot, np.zeros(2), 1)
    second = _dense_operator(pilot, np.array([0, np.pi]), 1)
    before = np.trace(first@covariance@first.conj().T).real
    after = np.trace(second@covariance@second.conj().T).real
    assert abs(before-after) > 1


@pytest.mark.parametrize("seed", [4, 17, 132])
def test_fixed_quadratic_and_direct_residual_decrease_with_cross_user_coupling(seed):
    y, pilot, joint, beta = _case(seed=seed, q=9, k=4)
    updated, report = phase.update(y, pilot, joint, beta)
    before = _residual(y, pilot, joint, beta)
    after = _residual(y, pilot, joint, updated)
    assert after < before-1e-7
    np.testing.assert_allclose(report["mean_residual_energy_before"], before, atol=2e-12)
    np.testing.assert_allclose(report["mean_residual_energy_after"], after, atol=2e-12)
    np.testing.assert_allclose(report["objective_change"], after-before, atol=2e-12)
    assert np.max(np.diff(report["normalized_objective_history"])) <= 1e-14
    assert 0 < report["accepted_steps"] <= 20
    # This provides a numerical check of the global curvature bound, rather than
    # merely checking that backtracking eventually rescued a bad step.
    assert report["backtracks"] == 0
    assert all(step == 1 for step in report["step_sizes"])
    assert np.all(updated >= -np.pi) and np.all(updated < np.pi)


@pytest.mark.parametrize("factor", [1e-9, 7.3, 1e6])
def test_common_signal_unit_scaling_preserves_step_and_stop(factor):
    y, pilot, joint, beta = _case(seed=42)
    expected, baseline = phase.update(y, pilot, joint, beta)
    updated, report = phase.update(factor*y, pilot, factor*joint, beta)
    np.testing.assert_allclose(updated, expected, atol=2e-12, rtol=2e-12)
    np.testing.assert_allclose(report["normalized_objective_history"],
                               baseline["normalized_objective_history"], atol=1e-14)
    np.testing.assert_allclose(report["objective_change"],
                               factor**2*baseline["objective_change"], rtol=3e-13)
    assert report["accepted_steps"] == baseline["accepted_steps"]
    assert report["stop_reason"] == baseline["stop_reason"]


def test_phase_independent_diagonal_and_reference_frame_do_not_change_optimizer():
    y, pilot, joint, beta = _case(seed=39)
    gram, matched, _ = phase.projected_quadratic(y, pilot, joint)
    expected, baseline = phase.minimize(beta, gram, matched)
    altered = gram.copy()
    altered[:, np.arange(len(beta)), np.arange(len(beta))] += 1e15
    altered[0] += 1e13*np.ones((len(beta), len(beta)))
    altered_b = matched.copy()
    altered_b[0] += 1e12*(1+2j)
    updated, report = phase.minimize(beta, altered, altered_b)
    np.testing.assert_array_equal(updated, expected)
    np.testing.assert_array_equal(report["normalized_objective_history"],
                                  baseline["normalized_objective_history"])
    assert report["objective_change"] == baseline["objective_change"]
    assert report["objective_scale"] == baseline["objective_scale"]


@pytest.mark.parametrize("q", [1, 6])
def test_zero_contribution_and_no_phase_information_preserve_slopes(q):
    y, pilot, joint, beta = _case(q=q)
    joint[1] = 0
    updated, report = phase.update(y, pilot, joint, beta)
    assert updated[1] == beta[1]
    # The reference frame phase is fixed for every user irrespective of beta.
    np.testing.assert_array_equal(np.exp(0j*updated), np.ones(len(beta)))
    if q == 1:
        np.testing.assert_array_equal(updated, beta)
        assert not report["moved"]
        assert report["stop_reason"] == "zero_phase_dependence"
    joint[:] = 0
    updated, report = phase.update(y, pilot, joint, beta)
    np.testing.assert_array_equal(updated, beta)
    assert not report["moved"] and report["accepted_steps"] == 0
    assert report["objective_scale"] == 0
    assert report["objective_change"] == 0


def test_fixed_posterior_inputs_and_quadratic_arrays_are_not_mutated():
    y, pilot, joint, beta = _case(seed=72)
    saved = [a.copy() for a in (y, pilot, joint, beta)]
    for a in (y, pilot, joint, beta):
        a.setflags(write=False)
    _, report = phase.update(y, pilot, joint, beta, max_steps=3)
    for value, original in zip((y, pilot, joint, beta), saved):
        np.testing.assert_array_equal(value, original)
    gram, matched, _ = phase.projected_quadratic(y, pilot, joint)
    gram_before, matched_before = gram.copy(), matched.copy()
    gram.setflags(write=False)
    matched.setflags(write=False)
    phase.minimize(beta, gram, matched, max_steps=3)
    np.testing.assert_array_equal(gram, gram_before)
    np.testing.assert_array_equal(matched, matched_before)
    assert report["accepted_steps"] <= 3


def test_zero_budget_stationary_point_and_wrapping_semantics():
    y, pilot, joint, beta = _case(seed=55)
    updated, report = phase.update(y, pilot, joint, beta+4*np.pi, max_steps=0)
    np.testing.assert_allclose(updated, beta, atol=2e-15)
    assert not report["moved"] and report["accepted_steps"] == 0
    assert report["stop_reason"] == "max_steps"
    # At an exactly representable stationary point, no spurious rotation occurs.
    pilot = np.ones((3, 1, 1), complex)
    joint = np.ones((1, 1, 1, 1), complex)
    y = np.ones((3, 1, 1), complex)
    updated, report = phase.update(y, pilot, joint, np.zeros(1))
    np.testing.assert_array_equal(updated, np.zeros(1))
    assert not report["moved"] and report["accepted_steps"] == 0
    assert report["normalized_gradient_inf"] == 0
    assert report["stop_reason"] == "gradient_tolerance"
