"""Synthetic mathematical checks; no real observation or neural model is loaded."""
import numpy as np
import pytest

from algorithm.C_STMP_phase_direct_20261103 import grouped_initialization as grouped
from algorithm.STMP import fast_initialization as full
from system.receiver.unknown_phase import UnknownPhaseInput
from utils import sha256


def _case(seed=14, rows=4, n=2, q=3, users=2, antennas=3):
    rng = np.random.default_rng(seed)
    normal = lambda shape: (rng.normal(size=shape)+1j*rng.normal(size=shape))/np.sqrt(2)
    factor = normal((rows*n, rows*n))
    moment = factor@factor.conj().T/(rows*n)+np.eye(rows*n)*.1
    return normal((q, antennas, rows)), normal((q, users, n))/np.sqrt(n), moment, .4


def _finite_difference(function, x, step=1e-6):
    result = np.empty_like(x)
    for index in range(len(x)):
        delta = np.zeros_like(x)
        delta[index] = step
        result[index] = (function(x+delta)[0]-function(x-delta)[0])/(2*step)
    return result


def test_grouping_is_fixed_training_only_and_preserves_all_rows():
    _, _, moment, _ = _case(rows=8)
    first, details = grouped.training_groups(moment, 8, 2, 4)
    second, other = grouped.training_groups(moment.copy(), 8, 2, 4)
    assert details == other
    assert [group.tolist() for group in first] == [group.tolist() for group in second]
    assert sorted(row for group in first for row in group) == list(range(8))
    assert all(len(group) == 4 for group in first)
    assert 0 < details['retained_covariance_squared_frobenius_fraction'] <= 1
    single, details = grouped.training_groups(moment, 8, 2, 8)
    np.testing.assert_array_equal(single[0], np.arange(8))
    assert details['retained_covariance_squared_frobenius_fraction'] == 1.


def test_joint_and_local_gradients_match_finite_differences():
    y, p, moment, noise = _case()
    groups, _ = grouped.training_groups(moment, 4, 2, 2)
    grams, samples, frames = grouped.grouped_problem(y, p, moment, noise, groups)
    x, rho, span = np.array([.7, 1.2, -.6, .9]), .3, 2.
    function = lambda current: grouped.objective(current, grams, samples, noise, frames, rho, span)
    np.testing.assert_allclose(function(x)[1], _finite_difference(function, x), rtol=3e-6, atol=3e-7)
    bases = np.broadcast_to(noise*np.eye(len(frames)), (len(groups), len(frames), len(frames))).copy()
    local = lambda current: grouped._local_objective(current, grams[:, 0], bases, samples, frames, rho, span)
    np.testing.assert_allclose(local(x[:2])[1], _finite_difference(local, x[:2]), rtol=3e-6, atol=3e-7)


def test_one_group_matches_full_covariance_objective_and_direction():
    y, p, moment, noise = _case()
    groups, _ = grouped.training_groups(moment, 4, 2, 4)
    grams, samples, frames = grouped.grouped_problem(y, p, moment, noise, groups)
    parameters, rho, span = np.array([.6, .8, -.7, .4]), .3, 2.
    actual = grouped.objective(parameters, grams, samples, noise, frames, rho, span)
    expected = full.objective(parameters, grams[0], samples[0], noise, frames, rho, span)
    np.testing.assert_allclose(actual[0], expected[0], rtol=2e-13, atol=2e-13)
    np.testing.assert_allclose(actual[1], expected[1], rtol=2e-13, atol=2e-13)
    _, _, weight = full.factor_value(noise*np.eye(len(frames)), samples[0])
    candidate = grouped.directional_phase(grams[:, 0], weight[None], frames, .2)
    reference = full.directional_phase(grams[0, 0], weight, len(p), 4, .2)
    np.testing.assert_allclose(candidate[:2], reference[:2], rtol=2e-13, atol=2e-13)
    assert candidate[2] == reference[2]


def test_zero_power_direction_matches_actual_power_derivative():
    y, p, moment, noise = _case(seed=48)
    groups, _ = grouped.training_groups(moment, 4, 2, 2)
    grams, samples, frames = grouped.grouped_problem(y, p, moment, noise, groups)
    bases = np.broadcast_to(noise*np.eye(len(frames)), (len(groups), len(frames), len(frames))).copy()
    _, _, weights = grouped._factors(bases, samples)
    beta, score, _ = grouped.directional_phase(grams[:, 0], weights, frames, .1)
    _, gradient = grouped._local_objective(np.array([0., beta]), grams[:, 0], bases, samples, frames, 1., 1.)
    np.testing.assert_allclose(score, -gradient[0], rtol=3e-12, atol=3e-12)


def test_grouped_optimization_is_nonincreasing_and_keeps_power_nonnegative():
    y, p, moment, noise = _case(seed=71)
    groups, _ = grouped.training_groups(moment, 4, 2, 2)
    grams, samples, frames = grouped.grouped_problem(y, p, moment, noise, groups)
    beta, power, coordinate = grouped.coordinate(grams, samples, noise, frames, .3,
                                                sweeps=1, local_maxiter=4)
    beta, power, joint = grouped.joint(grams, samples, noise, frames, beta, power, .3, maxiter=5)
    assert np.max(np.diff(coordinate['objective'])) <= 1e-9
    assert np.max(np.diff(joint['objective'])) <= 1e-9
    np.testing.assert_allclose(joint['objective'][0], coordinate['objective'][-1], rtol=1e-12, atol=1e-12)
    value, _ = grouped.objective(np.r_[power/.3, beta*2], grams, samples, noise, frames, .3, 2.)
    np.testing.assert_allclose(value, joint['objective'][-1], rtol=1e-12, atol=1e-12)
    assert np.all(power >= 0) and np.all(abs(beta) <= np.pi)


def test_noise_and_training_moment_scaling_preserve_gradients():
    y, p, moment, noise = _case(seed=95)
    groups, _ = grouped.training_groups(moment, 4, 2, 2)
    grams, samples, frames = grouped.grouped_problem(y, p, moment, noise, groups)
    scale = 3.7
    scaled_grams, scaled_samples, _ = grouped.grouped_problem(y/scale, p, moment/scale**2, noise/scale**2, groups)
    parameters = np.array([.6, .8, -.7, .4])
    value, gradient = grouped.objective(parameters, grams, samples, noise, frames, .3, 2.)
    other_value, other_gradient = grouped.objective(parameters, scaled_grams, scaled_samples, noise/scale**2, frames, .3, 2.)
    np.testing.assert_allclose(other_gradient, gradient, rtol=2e-12, atol=2e-12)
    np.testing.assert_allclose(other_value-value, -len(p)*y.shape[2]*np.log(scale**2), rtol=2e-12, atol=2e-12)


def test_estimate_interface_binds_training_moment_and_reports_scope(tmp_path):
    y, p, moment, noise = _case(seed=21)
    path = tmp_path/'synthetic_training_moment.npz'
    np.savez(path, second_moment=moment)
    policy = dict(method='grouped_covariance', group_size=2, sweeps=1,
                  local_iterations=2, joint_iterations=3,
                  training_second_moment=str(path), training_second_moment_sha256=sha256(path))
    beta, record = grouped.estimate(UnknownPhaseInput(y, p, noise, .3), policy, dict(scale=.7))
    assert beta.shape == (p.shape[1],) and np.isfinite(beta).all()
    assert record['groups'] and record['covariance_orders'] == [6, 6]
    assert record['shared_user_powers'] and record['shared_user_slopes']
    assert not record['physical_path_search_used'] and not record['truth_used']
    np.savez(path, second_moment=moment*2)
    with pytest.raises(ValueError, match='Frozen training moment changed'):
        grouped.estimate(UnknownPhaseInput(y, p, noise, .3), policy, dict(scale=.7))
