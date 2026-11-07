"""Independent finite Gaussian checks for the Shen per-frame adaptation.

References: Shen et al., arXiv:2412.20806v1, III-C (47)--(54), Algorithm 1.
These checks use synthetic arrays and a full KN-dimensional Gaussian posterior;
they do not load trained priors, physical samples, or a receiver experiment.
Frame zero is a declared project constraint, not part of Shen's projection.
"""
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path

import numpy as np
import pytest

from algorithm.C_STMP_phase_shen_frames_20261103 import iterations, moments, phase
from algorithm.C_STMP_phase_direct_20261103 import moments as slope_moments
from algorithm.C_STMP_phase_selection_20261030 import iterations as selected_iterations
from algorithm.STMP.linear import SpatialLinear
from algorithm.STMP.records import SpatialConfig
from system.phase import phase_operator
from test_phase_direct_integration_20261103 import GaussianDenoiser, _input


def _case(seed=73, q=5, k=3, n=2, m=2, rows=3):
    rng = np.random.default_rng(seed)
    normal = lambda shape: (rng.normal(size=shape)+1j*rng.normal(size=shape))/np.sqrt(2)
    phi = np.exp(1j*rng.uniform(-np.pi, np.pi, (q, k)))
    phi[0] = 1.
    return (normal((q, m, rows)), normal((q, k, n))/np.sqrt(n),
            normal((k, m, rows, n)), .37, .21, phi)


def _full_posterior(case):
    """Condition all KN coefficients directly, without the Q-dimensional kernel."""
    observation, pilot, mean, variance, noise, phi = case
    q, k, n = pilot.shape
    y = observation.reshape(q, -1)
    center = mean.transpose(0, 3, 1, 2).reshape(k*n, -1)
    operator = (pilot*phi[:, :, None]).reshape(q, k*n)
    precision = np.eye(k*n)/variance + operator.conj().T@operator/noise
    covariance = np.linalg.solve(precision, np.eye(k*n))
    posterior = np.linalg.solve(precision, center/variance + operator.conj().T@y/noise)
    projected = np.empty((k, q, y.shape[1]), complex)
    blocks = np.empty((q, k, k), complex)
    for user in range(k):
        projected[user] = pilot[:, user]@posterior[user*n:(user+1)*n]
    for frame in range(q):
        projection = np.zeros((k, k*n), complex)
        for user in range(k):
            projection[user, user*n:(user+1)*n] = pilot[frame, user]
        blocks[frame] = projection@covariance@projection.conj().T
    return posterior, covariance, projected, blocks


def _quadratic(phi, gram, matched):
    return sum(float(np.vdot(row, g@row).real-2*np.vdot(row, b).real)
               for row, g, b in zip(phi, gram, matched))


def _expected_residual(case, candidate):
    observation, pilot, _, _, _, _ = case
    posterior, covariance, _, _ = _full_posterior(case)
    q, k, n = pilot.shape
    y = observation.reshape(q, -1)
    operator = (pilot*candidate[:, :, None]).reshape(q, k*n)
    residual = y-operator@posterior
    return float(np.vdot(residual, residual).real
                 + y.shape[1]*np.trace(operator@covariance@operator.conj().T).real)


def _dense_marginal(case):
    observation, pilot, mean, variance, noise, phi = case
    q, k, n = pilot.shape
    y = observation.reshape(q, -1)
    center = mean.transpose(0, 3, 1, 2).reshape(k*n, -1)
    operator = (pilot*phi[:, :, None]).reshape(q, k*n)
    covariance = noise*np.eye(q)+variance*operator@operator.conj().T
    residual = y-operator@center
    return float(np.linalg.slogdet(covariance)[1]
                 + np.vdot(residual, np.linalg.solve(covariance, residual)).real/y.shape[1])


@pytest.mark.parametrize('seed,q,k,n,m,rows', [
    (73, 5, 3, 2, 2, 3), (19, 3, 2, 5, 3, 2), (41, 1, 2, 3, 2, 4)])
def test_arbitrary_phases_match_full_kn_posterior(seed, q, k, n, m, rows):
    case = _case(seed, q, k, n, m, rows)
    _, _, expected_mean, expected_covariance = _full_posterior(case)
    actual_mean, actual_covariance, details = moments.conditional_projected_moments(*case)
    np.testing.assert_allclose(actual_mean, expected_mean, rtol=3e-12, atol=3e-12)
    np.testing.assert_allclose(actual_covariance, expected_covariance, rtol=3e-12, atol=3e-12)
    assert np.linalg.eigvalsh(actual_covariance).min() > -2e-12
    assert details['covariance_shape'] == [q, q]
    assert details['cross_user_covariance_retained']
    # These examples deliberately have R != N and M != R to expose packing errors.
    assert rows != n
    gram, matched, _ = moments.conditional_quadratic(*case)
    y = case[0].reshape(q, -1)
    expected_gram = np.empty_like(gram)
    expected_matched = np.empty_like(matched)
    for frame in range(q):
        z = expected_mean[:, frame]
        expected_gram[frame] = z.conj()@z.T+y.shape[1]*expected_covariance[frame].conj()
        expected_matched[frame] = z.conj()@y[frame]
    np.testing.assert_allclose(gram, expected_gram, rtol=3e-12, atol=3e-12)
    np.testing.assert_allclose(matched, expected_matched, rtol=3e-12, atol=3e-12)
    assert np.linalg.eigvalsh(gram).min() > -2e-12


def test_quadratic_is_actual_posterior_expected_residual():
    case = _case(seed=71)
    gram, matched, _ = moments.conditional_quadratic(*case)
    old = case[-1]
    rng = np.random.default_rng(102)
    candidate = np.exp(1j*rng.uniform(-np.pi, np.pi, old.shape))
    candidate[0] = 1.
    constant = float(np.vdot(case[0], case[0]).real)
    for phi in (old, candidate):
        np.testing.assert_allclose(_quadratic(phi, gram, matched)+constant,
                                   _expected_residual(case, phi), rtol=3e-12, atol=3e-12)
    np.testing.assert_allclose(_quadratic(candidate, gram, matched)-_quadratic(old, gram, matched),
                               _expected_residual(case, candidate)-_expected_residual(case, old),
                               rtol=3e-12, atol=3e-12)


@pytest.mark.parametrize('seed', [4, 39])
def test_common_slope_subset_matches_existing_exact_kernel(seed):
    case = list(_case(seed=seed))
    beta = np.array([.51, -1.23, 2.77])
    case[-1] = np.exp(1j*np.arange(len(case[0]))[:, None]*beta)
    slope_case = (*case[:-1], beta)
    projected, covariance, _ = moments.conditional_projected_moments(*case)
    old_projected, old_covariance, _ = slope_moments.conditional_projected_moments(*slope_case)
    np.testing.assert_allclose(projected, old_projected, rtol=2e-12, atol=2e-12)
    np.testing.assert_allclose(covariance, old_covariance, rtol=2e-12, atol=2e-12)
    gram, matched, _ = moments.conditional_quadratic(*case)
    old_gram, old_matched, _ = slope_moments.conditional_quadratic(*slope_case)
    np.testing.assert_allclose(gram, old_gram, rtol=2e-12, atol=2e-12)
    np.testing.assert_allclose(matched, old_matched, rtol=2e-12, atol=2e-12)
    np.testing.assert_allclose(moments.marginal_value(*case),
                               slope_moments.marginal_value(*slope_case), rtol=2e-12, atol=2e-12)


def test_arbitrary_phase_marginal_and_physical_unit_scaling():
    case = _case(seed=17)
    observation, pilot, mean, variance, noise, phi = case
    np.testing.assert_allclose(moments.marginal_value(*case), _dense_marginal(case),
                               rtol=3e-12, atol=3e-12)
    scale = 7.3
    scaled = (observation*scale, pilot, mean*scale, variance*scale**2, noise*scale**2, phi)
    gram, matched, _ = moments.conditional_quadratic(*case)
    scaled_gram, scaled_matched, _ = moments.conditional_quadratic(*scaled)
    np.testing.assert_allclose(scaled_gram, scale**2*gram, rtol=3e-12, atol=3e-12)
    np.testing.assert_allclose(scaled_matched, scale**2*matched, rtol=3e-12, atol=3e-12)
    np.testing.assert_allclose(moments.marginal_value(*scaled)-moments.marginal_value(*case),
                               len(pilot)*np.log(scale**2), rtol=3e-12, atol=3e-12)
    first, _ = phase.update(*case)
    second, _ = phase.update(*scaled)
    np.testing.assert_allclose(first, second, rtol=3e-12, atol=3e-12)


def test_frame_solve_has_noise_prior_and_elementwise_projection():
    old = np.exp(1j*np.array([[0., 0.], [.2, -.3], [.4, 1.1]]))
    gram = np.array([[[2., 1j], [-1j, 2.]], [[3., .4+.7j], [.4-.7j, 2.]],
                     [[1., -.2+.3j], [-.2-.3j, 2.]]], complex)
    matched = np.array([[1j, -1j], [1.+.3j, -.7+.5j], [.2-.6j, .9+.4j]])
    noise = .43
    raw = np.array([np.linalg.solve(g+noise*np.eye(2), b) for g, b in zip(gram, matched)])
    expected = raw/abs(raw)
    expected[0] = 1.
    actual, report = phase.rotations(old, gram, matched, noise)
    np.testing.assert_allclose(actual, expected, rtol=2e-13, atol=2e-13)
    np.testing.assert_array_equal(actual[0], np.ones(2))
    np.testing.assert_allclose(abs(actual), 1., rtol=0, atol=2e-15)
    assert report['moved']
    np.testing.assert_allclose(report['conditional_before'], _quadratic(old, gram, matched))
    np.testing.assert_allclose(report['conditional_after'], _quadratic(actual, gram, matched))
    # Projection satisfies the modulus constraint; it need not solve A phi=b.
    assert np.linalg.norm((gram[1]+noise*np.eye(2))@actual[1]-matched[1]) > .1


def test_reference_frame_is_not_a_global_rephasing_or_slope_projection():
    old = np.ones((4, 2), complex)
    target = np.exp(1j*np.array([[.8, -.4], [.2, -.7], [1.4, .1], [-.3, 1.9]]))
    gram = np.broadcast_to(np.eye(2), (4, 2, 2)).copy()
    matched = 1.3*target
    actual, _ = phase.rotations(old, gram, matched, .3)
    np.testing.assert_array_equal(actual[0], np.ones(2))
    np.testing.assert_allclose(actual[1:], target[1:], rtol=2e-13, atol=2e-13)
    assert np.max(abs(actual[2]-actual[1]**2)) > .5
    assert np.max(abs(actual[1:]-target[1:]/target[0])) > .2


def test_zero_solution_preserves_old_components_and_q1_is_fixed():
    old = np.exp(1j*np.array([[0., 0.], [.2, -.3], [.4, 1.1]]))
    gram = np.broadcast_to(np.eye(2), (3, 2, 2)).copy()
    actual, report = phase.rotations(old, gram, np.zeros((3, 2), complex), .3)
    np.testing.assert_array_equal(actual, old)
    assert not report['moved']
    partial = np.zeros((3, 2), complex)
    partial[2, 1] = 1j
    actual, report = phase.rotations(old, gram, partial, .3)
    np.testing.assert_array_equal(actual[:2], old[:2])
    assert actual[2, 0] == old[2, 0]
    np.testing.assert_allclose(actual[2, 1], 1j, atol=2e-15)
    single, report = phase.rotations(np.ones((1, 2), complex), gram[:1],
                                     np.array([[1j, -1j]]), .3)
    np.testing.assert_array_equal(single, np.ones((1, 2)))
    assert not report['moved']


def test_projected_solve_can_increase_quadratic_and_is_not_rejected():
    # Old phase is the exact unconstrained minimizer of this positive quadratic.
    # With G=[[2,i],[-i,2]], b=G*1 and noise=1, raw=(5+i,5-i)/8.
    # Its projection moves away from the minimizer despite a valid linear solve.
    old = np.ones((2, 2), complex)
    gram = np.array([[[2., 1j], [-1j, 2.]]]*2)
    matched = np.array([g@row for g, row in zip(gram, old)])
    actual, report = phase.rotations(old, gram, matched, 1.)
    expected = np.array([5.+1j, 5.-1j])/np.sqrt(26)
    np.testing.assert_allclose(actual[1], expected, rtol=2e-13, atol=2e-13)
    change = actual[1]-old[1]
    increase = float(np.vdot(change, gram[1]@change).real)
    assert increase > .05
    np.testing.assert_allclose(_quadratic(actual, gram, matched)-_quadratic(old, gram, matched),
                               increase, rtol=2e-13, atol=2e-13)
    assert report['conditional_after'] > report['conditional_before']+.05
    assert report['moved']


def test_full_update_uses_current_arbitrary_phase_and_keeps_inputs_unrotated():
    case = _case(seed=29)
    backups = [v.copy() if isinstance(v, np.ndarray) else v for v in case]
    gram, matched, _ = moments.conditional_quadratic(*case)
    expected, _ = phase.rotations(case[-1], gram, matched, case[-2])
    actual, report = phase.update(*case)
    np.testing.assert_allclose(actual, expected, rtol=2e-13, atol=2e-13)
    np.testing.assert_allclose([report['before'], report['after']],
                               [_dense_marginal(case), _dense_marginal((*case[:-1], actual))],
                               rtol=3e-12, atol=3e-12)
    np.testing.assert_array_equal(np.asarray(report['before_phase_real'])
                                  +1j*np.asarray(report['before_phase_imag']), case[-1])
    np.testing.assert_array_equal(np.asarray(report['after_phase_real'])
                                  +1j*np.asarray(report['after_phase_imag']), actual)
    assert report['guard'] is False and report['fit_channel_rotation'] is False
    for original, backup in zip(case, backups):
        np.testing.assert_array_equal(original, backup)


def test_direct_phase_operator_and_linear_adjoint_match_explicit_sum():
    observation, pilot, mean, _, noise, phi = _case(seed=83, q=4, k=3, n=2, m=2, rows=3)
    effective = phase.effective_pilot(pilot, phi)
    np.testing.assert_array_equal(effective, pilot*phi[:, :, None])
    q, k, _ = pilot.shape
    _, m, rows, _ = mean.shape
    expected = np.zeros((q, m, rows), complex)
    for frame in range(q):
        for user in range(k):
            for antenna in range(m):
                for row in range(rows):
                    expected[frame, antenna, row] += phi[frame, user]*np.dot(
                        pilot[frame, user], mean[user, antenna, row])
    linear = SpatialLinear(effective, m, noise)
    np.testing.assert_allclose(linear.forward(mean), expected, rtol=2e-13, atol=2e-13)
    np.testing.assert_allclose(np.vdot(linear.forward(mean), observation),
                               np.vdot(mean, linear.adjoint(observation)), rtol=2e-13, atol=2e-13)
    slopes = np.array([.3, -.5, 1.1])
    slope_phase = np.exp(1j*np.arange(q)[:, None]*slopes)
    np.testing.assert_array_equal(phase.effective_pilot(pilot, slope_phase),
                                  phase_operator(pilot, slopes))


def _integration_settings():
    root = Path(__file__).resolve().parents[2]
    selected = root/'src/configs/candidates/c_stmp_phase_selection_20261030/physical_no_hypotheses_legacy_stop.json'
    base = root/'src/configs/candidates/C_STMP_variance_em_20261025.json'
    policy = deepcopy(json.loads(selected.read_text(encoding='utf-8'))['phase'])
    # Relax only the toy message-stability tolerance; retain the 20-step schedule,
    # five stable messages, ten stable decisions, and ten post-update iterations.
    controls = replace(SpatialConfig(**json.loads(base.read_text(encoding='utf-8'))['ep']),
                       iterations=40, min_iterations=40, convergence_tolerance=1.1)
    return policy, controls


class _NonzeroGaussian(GaussianDenoiser):
    def __call__(self, query, covariance):
        state = super().__call__(query, covariance)
        variance = np.trace(covariance).real/query.shape[1]
        state.mean = (query+variance*(.19+.13j))/(1+variance)
        state.conditional_mean = state.mean
        return state


def test_iteration_uses_final_applied_phase_without_feedback_rotation(monkeypatch):
    raw, beta = _input(), np.array([.3, -.2, .1])
    policy, controls = _integration_settings()
    base_linear = iterations.SpatialLinear
    used, observed = [], []

    class RecordingLinear(base_linear):
        def __init__(self, operator, *args):
            self.saved_operator = operator.copy()
            super().__init__(operator, *args)

        def update(self, observation, prior, covariance):
            used.append((self.saved_operator.copy(), prior.copy()))
            return super().update(observation, prior, covariance)

    def observe(row, state, query, covariance, prior, prior_covariance, out, *unused):
        observed.append((state.mean.copy(), out.copy()))

    monkeypatch.setattr(iterations, 'SpatialLinear', RecordingLinear)
    result, current, steps, trials = iterations.infer(raw, _NonzeroGaussian(), scale=.7,
        initial_variance=.4, controls=controls, phase_configuration=policy,
        initial_slopes=beta, observer=observe, adapt=False)
    assert [step['after_iteration'] for step in steps] == [20]
    assert steps[0]['moved'] and steps[0]['rotated_cached_means'] == []
    np.testing.assert_array_equal(steps[0]['channel_rotation'], np.zeros(3))
    np.testing.assert_array_equal(used[20][1], observed[19][1])
    np.testing.assert_array_equal(used[-1][0], phase.effective_pilot(raw.pilot, current))
    np.testing.assert_array_equal(result.estimate, observed[-1][0]*.7)
    np.testing.assert_array_equal(current, np.asarray(steps[-1]['after_phase_real'])
                                  +1j*np.asarray(steps[-1]['after_phase_imag']))
    np.testing.assert_array_equal(current[0], np.ones(3))
    assert len(result.trace) == 40
    assert all(step['after_iteration']+10 <= len(result.trace) for step in steps)
    assert all(trial['applied'] is False for trial in trials if trial['after_iteration'] == 40)


def test_conditional_prefix_matches_selected_before_first_phase_update():
    raw, beta = _input(), np.array([.3, -.2, .1])
    policy, controls = _integration_settings()

    def run(module):
        seen = []
        def observe(row, state, query, covariance, prior, prior_covariance, *unused):
            seen.append((state.mean.copy(), query.copy(), covariance.copy(),
                         prior.copy(), prior_covariance.copy()))
        result, _, steps, _ = module.infer(raw, _NonzeroGaussian(), scale=.7,
            initial_variance=.4, controls=controls, phase_configuration=policy,
            initial_slopes=beta, observer=observe, adapt=False)
        return result, steps, seen

    actual, new_steps, seen = run(iterations)
    expected, old_steps, reference = run(selected_iterations)
    assert new_steps[0]['after_iteration'] == old_steps[0]['after_iteration'] == 20
    for actual_row, expected_row in zip(seen[:20], reference[:20]):
        for first, second in zip(actual_row, expected_row):
            np.testing.assert_array_equal(first, second)
    for field in ('phase_update_eligible', 'phase_update_due', 'stable_iterations',
                  'decision_stable_iterations', 'query_variance_ratio'):
        assert [row[field] for row in actual.trace[:20]] == [row[field] for row in expected.trace[:20]]
