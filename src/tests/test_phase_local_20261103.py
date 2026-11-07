"""Independent small Gaussian checks; no trained model or physical input is read.

Full KN-dimensional conditioning supplies the reference for the EM inequality.
Integration uses an analytic Gaussian denoiser and the selected 20-step cadence;
only its toy conditional-stability tolerance is relaxed to exercise the gates.
"""
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path

import numpy as np
import pytest

from algorithm.C_STMP_phase_direct_20261103.moments import conditional_quadratic
from algorithm.C_STMP_phase_local_20261103 import iterations, phase
from algorithm.C_STMP_phase_selection_20261030 import iterations as selected_iterations
from algorithm.STMP.records import SpatialConfig
from system.phase import phase_operator
from system.receiver.unknown_phase import UnknownPhaseInput
from test_phase_direct_integration_20261103 import GaussianDenoiser, _input


ROOT = Path(__file__).resolve().parents[2]


def _case(seed=61, q=5, k=3, n=2, m=2, rows=3):
    rng = np.random.default_rng(seed)
    normal = lambda shape: (rng.normal(size=shape)+1j*rng.normal(size=shape))/np.sqrt(2)
    return (normal((q, m, rows)), normal((q, k, n))/np.sqrt(n),
            normal((k, m, rows, n)), .37, .21, rng.uniform(-np.pi, np.pi, k))


def _quadratic(phi, gram, matched):
    # Independent per-frame matrix products, not the production einsum helper.
    return sum(float(np.vdot(row, a@row).real-2*np.vdot(row, b).real)
               for row, a, b in zip(phi, gram, matched))


def _dense_reference(case, next_beta, angle):
    """Expected residual and NLL from a full KN-dimensional posterior."""
    y, pilot, mean, variance, noise, beta = case
    q, k, n = pilot.shape
    y = y.reshape(q, -1)
    center = mean.transpose(0, 3, 1, 2).reshape(k*n, -1)
    old = (pilot*np.exp(1j*np.arange(q)[:, None]*beta)[:, :, None]).reshape(q, k*n)
    new = (pilot*np.exp(1j*(np.arange(q)[:, None]*next_beta+angle))[:, :, None]).reshape(q, k*n)
    precision = np.eye(k*n)/variance+old.conj().T@old/noise
    covariance = np.linalg.solve(precision, np.eye(k*n))
    posterior = np.linalg.solve(precision, center/variance+old.conj().T@y/noise)
    expected, marginal = [], []
    for operator in (old, new):
        residual = y-operator@posterior
        expected.append(float(np.vdot(residual, residual).real
                              +y.shape[1]*np.trace(operator@covariance@operator.conj().T).real))
        total = noise*np.eye(q)+variance*operator@operator.conj().T
        residual = y-operator@center
        marginal.append(float(np.linalg.slogdet(total)[1]
                              +np.vdot(residual, np.linalg.solve(total, residual)).real/y.shape[1]))
    return np.asarray(expected), np.asarray(marginal)


@pytest.mark.parametrize('q', [1, 2, 7])
def test_gradient_and_hessian_match_scalar_objective_differences(q):
    rng = np.random.default_rng(92+q)
    c = rng.normal(size=q)+1j*rng.normal(size=q)
    coordinates = (np.column_stack((np.ones(q), np.linspace(-1, 1, q)))
                   if q > 1 else np.ones((1, 1)))
    size = coordinates.shape[1]
    point = np.linspace(-.19, .23, size)
    objective = lambda x: float(np.real(np.sum(c*np.exp(-1j*(coordinates@x)))))
    # Evaluate away from zero too: this catches the sign of the mixed Hessian.
    gradient, hessian = phase.local_derivatives(c*np.exp(-1j*(coordinates@point)), coordinates)
    axes = np.eye(size)
    eg, eh = 1e-6, 2e-4
    numeric_gradient = [(objective(point+eg*axis)-objective(point-eg*axis))/(2*eg) for axis in axes]
    numeric_hessian = np.empty((size, size))
    for i, first in enumerate(axes):
        for j, second in enumerate(axes):
            numeric_hessian[i, j] = (objective(point+eh*(first+second))
                -objective(point+eh*(first-second))-objective(point+eh*(-first+second))
                +objective(point-eh*(first+second)))/(4*eh**2)
    np.testing.assert_allclose(gradient, numeric_gradient, atol=2e-9, rtol=2e-8)
    np.testing.assert_allclose(hessian, numeric_hessian, atol=2e-7, rtol=2e-7)


def test_positive_rescaling_leaves_local_step_and_gain_unchanged():
    c = np.array([-.3+.4j, .7-.2j, -.5+.8j, .2+.3j])
    expected, report = phase.local_step(c)
    assert report['accepted']
    for factor in (1e-12, 7.3, 1e12):
        actual, other = phase.local_step(factor*c)
        np.testing.assert_allclose(actual, expected, atol=3e-14, rtol=3e-13)
        assert other['backtracks'] == report['backtracks']
        np.testing.assert_allclose(other['normalized_gain'], report['normalized_gain'], atol=1e-15)


@pytest.mark.parametrize('c,reason', [
    (np.zeros(4, complex), 'zero_correlation'),
    (np.array([1., 2., 3.]), 'stationary_at_numerical_precision'),
    (-np.ones(4), 'stationary_at_numerical_precision'),
])
def test_zero_correlation_and_true_stationary_points_return_exact_zero(c, reason):
    # The negative-real example is a minimum: zero-step validity is not optimality.
    step, info = phase.local_step(c)
    np.testing.assert_array_equal(step, np.zeros(2))
    assert not info['accepted'] and info['reason'] == reason
    assert info['maximum_frame_increment'] == 0.


def test_nonconcave_curvature_and_finite_backtracking_rejection():
    c = np.array([-1.+.1j, -.4+.5j, -.5+.3j])
    step, info = phase.local_step(c)
    assert info['accepted'] and min(info['curvature_eigenvalues']) < 0
    increments = step[0]+np.linspace(-1, 1, len(c))*step[1]
    assert np.real(np.sum(c*np.exp(-1j*increments))) > np.real(c.sum())
    rejected, report = phase.local_step(np.array([1j]), radius=3., armijo=.99, max_backtracks=0)
    np.testing.assert_array_equal(rejected, np.zeros(2))
    assert not report['accepted'] and report['reason'] == 'backtracking_budget_exhausted'
    accepted, report = phase.local_step(np.array([1j]), radius=3., armijo=.99, max_backtracks=16)
    assert report['accepted'] and report['backtracks'] > 0 and accepted[1] == 0.


@pytest.mark.parametrize('q', [1, 5])
def test_true_zero_step_preserves_even_noncanonical_beta_bitwise(q):
    beta = np.array([4*np.pi+.123456789, -np.pi/7])
    gram = np.broadcast_to(np.eye(2), (q, 2, 2)).copy()
    updated, angle, report = phase.rotations(beta, gram, np.zeros((q, 2), complex))
    np.testing.assert_array_equal(updated, beta)
    np.testing.assert_array_equal(angle, np.zeros(2))
    assert report['accepted_users'] == 0
    if q == 1:
        # Even an accepted constant rotation cannot change an unidentifiable slope.
        updated, angle, report = phase.rotations(beta, gram, np.full((1, 2), 1j))
        assert report['accepted_users'] == 2 and np.all(angle != 0.)
        np.testing.assert_array_equal(updated, beta)


@pytest.mark.parametrize('q', [1, 2, 7])
def test_frame_radius_includes_constant_rotation_and_wrapped_slope(q):
    beta = np.array([np.pi-.01])
    phi = np.exp(1j*np.arange(q)[:, None]*beta)
    c = 1j*np.linspace(-1, 1, q) if q > 1 else np.array([1j])
    gram, matched = np.ones((q, 1, 1)), phi*c[:, None]
    updated, angle, report = phase.rotations(beta, gram, matched, radius=.25)
    user = report['users'][0]
    a, b = user['center_increment'], user['endpoint_slope_increment']
    increment = a+(np.linspace(-1, 1, q) if q > 1 else np.zeros(1))*b
    returned = np.exp(1j*(np.arange(q)*updated[0]+angle[0]))
    np.testing.assert_allclose(returned, phi[:, 0]*np.exp(1j*increment), atol=2e-15)
    assert report['accepted_users'] == 1
    assert np.max(abs(increment)) <= .25+2e-15
    np.testing.assert_allclose(abs(a)+abs(b), np.max(abs(increment)), atol=2e-15)
    if q > 1:
        assert updated[0] < 0  # The test actually crosses the wrapping boundary.
        np.testing.assert_allclose(angle[0], a-b, atol=2e-15)
        assert abs(angle[0]-a) > .1  # A mistaken offset=a would fail this case.
    else:
        np.testing.assert_array_equal(updated, beta)
        assert b == 0. and angle[0] == a

    rng = np.random.default_rng(q)
    pilot = rng.normal(size=(q, 1, 2))+1j*rng.normal(size=(q, 1, 2))
    mean = rng.normal(size=(1, 2, 3, 2))+1j*rng.normal(size=(1, 2, 3, 2))
    old_prediction = np.einsum('qkn,kmrn->qmr', phase_operator(pilot, beta), mean)
    rotated = mean*np.exp(1j*angle)[:, None, None, None]
    new_prediction = np.einsum('qkn,kmrn->qmr', phase_operator(pilot, updated), rotated)
    np.testing.assert_allclose(new_prediction, old_prediction*np.exp(1j*increment)[:, None, None],
                               atol=5e-14, rtol=3e-14)


@pytest.mark.parametrize('seed', [61, 72, 83])
def test_coupled_quadratic_steps_and_full_gaussian_em_bound(seed):
    case = _case(seed)
    y, pilot, mean, variance, noise, beta = case
    gram, matched, _ = conditional_quadratic(*case)
    off_diagonal = gram.copy()
    for frame in off_diagonal:
        np.fill_diagonal(frame, 0.)
    assert np.linalg.norm(off_diagonal) > .1*np.linalg.norm(gram)
    updated, angle, report = phase.update(*case, radius=.25)
    solver = report['conditional_quadratic']
    q, k, _ = pilot.shape
    phi = np.exp(1j*np.arange(q)[:, None]*beta)
    initial_objective = _quadratic(phi, gram, matched)
    for user in solver['users']:
        before = _quadratic(phi, gram, matched)
        increment = user['center_increment']+np.linspace(-1, 1, q)*user['endpoint_slope_increment']
        phi[:, user['user']] *= np.exp(1j*increment)
        difference = _quadratic(phi, gram, matched)-before
        # Tests the actual coupled objective, including already updated users.
        expected = -2*user['correlation_scale']*user['normalized_gain']
        np.testing.assert_allclose(difference, expected, rtol=2e-11, atol=2e-11)
        assert difference <= 2e-11 and np.max(abs(increment)) <= .25+2e-15
    final_objective = _quadratic(phi, gram, matched)
    np.testing.assert_allclose(phi, np.exp(1j*(np.arange(q)[:, None]*updated+angle)), atol=2e-14)
    expected_residual, marginal = _dense_reference(case, updated, angle)
    np.testing.assert_allclose(expected_residual[1]-expected_residual[0],
                               final_objective-initial_objective, atol=8e-11, rtol=3e-11)
    np.testing.assert_allclose([report['before'], report['after']], marginal, atol=3e-12, rtol=3e-12)
    bound = (final_objective-initial_objective)/noise
    assert y.shape[1]*y.shape[2]*(marginal[1]-marginal[0]) <= bound+1e-9
    assert bound < 0. and report['moved']


def test_complete_update_is_invariant_to_physical_units():
    case = _case()
    y, pilot, mean, variance, noise, beta = case
    slope, angle, report = phase.update(*case)
    scale = 7.3
    other_slope, other_angle, other = phase.update(
        y*scale, pilot, mean*scale, variance*scale**2, noise*scale**2, beta)
    np.testing.assert_allclose(other_slope, slope, atol=2e-13, rtol=2e-13)
    np.testing.assert_allclose(other_angle, angle, atol=2e-13, rtol=2e-13)
    np.testing.assert_allclose(other['after']-other['before'], report['after']-report['before'],
                               atol=2e-12, rtol=2e-12)


def _policy(maximum_updates=None, solver='local'):
    path = ROOT/'src/configs/candidates/c_stmp_phase_selection_20261030/physical_no_hypotheses_legacy_stop.json'
    policy = deepcopy(json.loads(path.read_text(encoding='utf-8'))['phase'])
    policy['local_update'] = dict(solver=solver, maximum_updates=maximum_updates,
        radius=.25, curvature_floor=.001, armijo=.0001, max_backtracks=16)
    return policy


def _controls():
    configuration = json.loads((ROOT/'src/configs/candidates/C_STMP_variance_em_20261025.json').read_text(encoding='utf-8'))
    # The relaxed toy tolerance makes scheduling reachable without neural inference.
    return replace(SpatialConfig(**configuration['ep']), iterations=100, min_iterations=80,
                   convergence_tolerance=1.1)


class ShiftedGaussianDenoiser(GaussianDenoiser):
    """Exact known Gaussian prior with nonzero mean, used to test rotation."""
    def __call__(self, query, covariance):
        state = super().__call__(query, covariance)
        variance = np.trace(covariance).real/query.shape[1]
        location = np.full(query.shape, .19+.13j)
        state.mean = (query+variance*location)/(1+variance)
        state.conditional_mean = state.mean
        return state


def _run(raw, denoiser, policy, **kwargs):
    return iterations.infer(raw, denoiser, scale=.7, initial_variance=.4,
        controls=_controls(), phase_configuration=policy,
        initial_slopes=np.array([.3, -.2, .1]), **kwargs)


def test_real_zero_step_preserves_all_conditional_histories_and_can_stop(monkeypatch):
    raw = _input()
    raw = UnknownPhaseInput(np.zeros_like(raw.observation), raw.pilot.real, raw.noise_variance, raw.activity_prior)
    linear_type = iterations.SpatialLinear
    builds = []

    class RecordingLinear(linear_type):
        def __init__(self, operator, *args):
            builds.append(operator.copy())
            super().__init__(operator, *args)

    monkeypatch.setattr(iterations, 'SpatialLinear', RecordingLinear)
    states = []

    def observe(row, state, query, covariance, prior, prior_covariance, *unused):
        states.append((query.copy(), covariance.copy(), prior.copy(), prior_covariance.copy()))

    actual = iterations.infer(raw, GaussianDenoiser(), scale=.7, initial_variance=.4,
        controls=_controls(), phase_configuration=_policy(), initial_slopes=np.zeros(3), observer=observe)
    result, slopes, steps, trials = actual
    assert len(builds) == 1 and not steps
    assert [trial['after_iteration'] for trial in trials] == [20, 40, 60]
    assert all(not trial['moved'] and not trial['applied'] for trial in trials)
    assert result.stopping_reason == 'CONVERGED' and len(result.trace) == 80
    np.testing.assert_array_equal(slopes, np.zeros(3))
    for previous, current in zip(result.trace, result.trace[1:]):
        assert current['query_variance_ratio'] == previous['next_query_variance_ratio']
    assert result.trace[19]['next_query_variance_ratio'] != 1.

    fixed_states = []
    def observe_fixed(row, state, query, covariance, prior, prior_covariance, *unused):
        fixed_states.append((query.copy(), covariance.copy(), prior.copy(), prior_covariance.copy()))
    fixed, _, fixed_steps, fixed_trials = iterations.infer(raw, GaussianDenoiser(), scale=.7,
        initial_variance=.4, controls=_controls(), phase_configuration=_policy(maximum_updates=0),
        initial_slopes=np.zeros(3), observer=observe_fixed)
    assert not fixed_steps and not fixed_trials and len(fixed.trace) == 80
    for actual_state, expected_state in zip(states, fixed_states):
        for value, expected in zip(actual_state, expected_state):
            np.testing.assert_array_equal(value, expected)


def test_fixed_phase_uses_twenty_iteration_output_checks_without_forced_update(monkeypatch):
    def prohibited(*args, **kwargs):
        pytest.fail('Fixed-phase control must never call the phase updater')
    monkeypatch.setattr(iterations, 'update_phase', prohibited)
    result, beta, steps, trials = _run(_input(), ShiftedGaussianDenoiser(), _policy(0), adapt=False)
    assert not steps and not trials
    checks = [row['iteration'] for row in result.trace if row['cycle_stopping'] is not None]
    assert checks == [20, 40, 60, 80]
    assert result.stopping_reason == 'CONVERGED' and len(result.trace) == 80
    np.testing.assert_array_equal(beta, np.array([.3, -.2, .1]))


def test_once_update_rotates_feedback_and_returns_channel_for_final_operator(monkeypatch):
    raw = _input()
    linear_type = iterations.SpatialLinear
    used, observed = [], []

    class RecordingLinear(linear_type):
        def __init__(self, operator, *args):
            self.saved_operator = operator.copy()
            super().__init__(operator, *args)

        def update(self, observation, prior, covariance):
            used.append((self.saved_operator.copy(), prior.copy()))
            return super().update(observation, prior, covariance)

    def observe(row, state, query, covariance, prior, prior_covariance, out, *unused):
        observed.append((state.mean.copy(), out.copy()))

    monkeypatch.setattr(iterations, 'SpatialLinear', RecordingLinear)
    result, beta, steps, trials = _run(raw, ShiftedGaussianDenoiser(), _policy(1),
                                     adapt=False, observer=observe)
    assert len(steps) == len(trials) == 1 and steps[0]['after_iteration'] == 20
    angle = np.asarray(steps[0]['channel_rotation'])
    assert np.linalg.norm(angle) > 1e-6
    np.testing.assert_allclose(used[20][1], observed[19][1]*np.exp(1j*angle)[:, None, None, None],
                               atol=2e-15, rtol=2e-15)
    np.testing.assert_array_equal(used[-1][0], phase_operator(raw.pilot, beta))
    np.testing.assert_array_equal(result.estimate, observed[-1][0]*.7)
    checks = [row['iteration'] for row in result.trace if row['cycle_stopping'] is not None]
    assert checks == [20, 40, 60, 80]
    assert result.stopping_reason == 'CONVERGED' and len(result.trace) == 80


def test_reduced_legacy_integration_matches_selected_on_identical_toy_inputs():
    raw, policy = _input(), _policy(solver='legacy_reduced')
    actual, beta, steps, _ = _run(raw, ShiftedGaussianDenoiser(), policy, adapt=False)
    expected, old_beta, old_steps, _ = selected_iterations.infer(raw, ShiftedGaussianDenoiser(),
        scale=.7, initial_variance=.4, controls=_controls(), phase_configuration=policy,
        initial_slopes=np.array([.3, -.2, .1]), adapt=False)
    assert steps and [s['after_iteration'] for s in steps] == [s['after_iteration'] for s in old_steps]
    assert len(actual.trace) == len(expected.trace)
    assert actual.stopping_reason == expected.stopping_reason
    np.testing.assert_allclose(np.angle(np.exp(1j*(beta-old_beta))), 0., atol=2e-9)
    for field in ('estimate', 'conditional_matrix', 'probabilities', 'spatial_covariance'):
        np.testing.assert_allclose(getattr(actual, field), getattr(expected, field), rtol=2e-9, atol=2e-10)


def test_final_boundary_never_submits_an_update_without_conditional_refinement():
    raw = _input()
    controls = replace(_controls(), iterations=40, min_iterations=40)
    observed = []
    def observe(row, state, *unused):
        observed.append(state.mean.copy())
    result, beta, steps, trials = iterations.infer(raw, ShiftedGaussianDenoiser(), scale=.7,
        initial_variance=.4, controls=controls, phase_configuration=_policy(),
        initial_slopes=np.array([.3, -.2, .1]), adapt=False, observer=observe)
    assert len(result.trace) == 40 and steps
    assert [step['after_iteration'] for step in steps] == [20]
    assert [trial['after_iteration'] for trial in trials] == [20]
    np.testing.assert_array_equal(beta, np.asarray(steps[-1]['after_slopes']))
    np.testing.assert_array_equal(result.estimate, observed[-1]*.7)
