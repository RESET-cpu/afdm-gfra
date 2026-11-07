"""Independent mathematical and oracle-positive checks; no GPU/physical search."""
import numpy as np
import pytest
from algorithm.proposed import shen_phase as s


def complex_normal(rng, shape):
    return (rng.normal(size=shape)+1j*rng.normal(size=shape))/np.sqrt(2)


def fixture_values():
    rng = np.random.default_rng(382114)
    pilot = complex_normal(rng, (8, 3, 2))
    mean = complex_normal(rng, (3, 3, 4, 2))
    y = complex_normal(rng, (8, 3, 4))
    return rng, pilot, mean, y


def test_contraction_and_quadratic_equal_explicit_residual():
    _, pilot, mean, y = fixture_values()
    z = s.contributions(pilot, mean)
    for q in range(8):
        for k in range(3):
            np.testing.assert_allclose(z[q, :, k], (mean[k]@pilot[q, k]).ravel())
    variance = np.array([.1, .3, .2]); noise = .7
    a, b = s.moments(y, pilot, mean, variance, noise)
    phase = np.exp(1j*np.arange(8)[:, None]*np.array([.2, -.4, 1.1]))
    residual = y.reshape(8, -1)-np.einsum('qdk,qk->qd', z, phase)
    expected = np.sum(abs(residual)**2)-np.sum(abs(y)**2)
    expected += np.sum(12*np.sum(abs(pilot)**2, axis=-1)*variance)+8*3*noise
    np.testing.assert_allclose(s.objective(phase, a, b), expected, rtol=2e-13)


def test_variance_term_matches_monte_carlo():
    rng, pilot, mean, y = fixture_values()
    variance, noise = .23, .6
    a, b = s.moments(y, pilot, mean, variance, noise)
    estimates = []
    for _ in range(2500):
        draw = mean+np.sqrt(variance)*complex_normal(rng, mean.shape)
        z = s.contributions(pilot, draw)
        estimates.append(np.einsum('qdk,qdl->qkl', z.conj(), z))
    empirical = np.mean(estimates, axis=0)
    exact = a-noise*np.eye(3)[None]
    assert np.linalg.norm(empirical-exact)/np.linalg.norm(exact) < .012


def test_oracle_mean_positive_control_recovers_phase():
    # Explicit oracle unit test only. The inference wrapper never receives H.
    rng = np.random.default_rng(7741)
    pilot = complex_normal(rng, (16, 4, 3))
    mean = complex_normal(rng, (4, 5, 6, 3))
    beta = np.array([-.77, .32, 2.91, -3.12])
    phase = np.exp(1j*np.arange(16)[:, None]*beta)
    y = np.einsum('qdk,qk->qd', s.contributions(pilot, mean), phase).reshape(16, 5, 6)
    a, b = s.moments(y, pilot, mean, 0., 1e-10)
    fitted, record = s.projected_solve(a, b, np.ones((16, 4)))
    np.testing.assert_allclose(fitted, phase, atol=1e-10)
    constrained, slopes = s.project_slopes(fitted, np.zeros(4))
    np.testing.assert_allclose(constrained, phase, atol=3e-6)
    assert record['linear_solve_relative_residual'] < 1e-12
    assert max(abs(np.angle(np.exp(1j*(slopes-beta))))) < 2e-7


def test_zero_information_retains_previous_phase():
    phase = np.exp(1j*np.arange(8)[:, None]*np.array([.3, -.2]))
    new, row = s.projected_solve(np.tile(np.eye(2), (8, 1, 1)), np.zeros((8, 2)), phase)
    np.testing.assert_array_equal(new, phase)
    assert row['numerically_uninformative_entries'] == 16


def test_projection_is_not_claimed_to_solve_constrained_problem():
    # A deterministic counterexample prevents incorrectly claiming EM ascent.
    a = np.array([[[2., .9], [.9, 1.]], [[2., .9], [.9, 1.]]], complex)
    b = np.array([[1., 1j], [1., 1j]])
    old = np.ones((2, 2), complex)
    fitted, _ = s.projected_solve(a, b, old)
    gradient = 2*np.imag(fitted.conj()*(np.einsum('qkl,ql->qk', a, fitted)-b))
    assert np.linalg.norm(gradient[1]) > .01


def test_bad_variance_rejected():
    _, pilot, mean, y = fixture_values()
    with pytest.raises(ValueError):
        s.moments(y, pilot, mean, -.1, 1.)


def test_wrapper_starts_without_phase_and_counts_repeated_network_calls():
    from types import SimpleNamespace
    _, pilot, mean, _ = fixture_values()
    beta = np.array([.4,-1.2,2.7])
    phase = np.exp(1j*np.arange(8)[:,None]*beta)
    y = np.einsum('qdk,qk->qd', s.contributions(pilot,mean),phase).reshape(8,3,4)
    class OracleMeanTestDouble:
        # Deliberately oracle, confined to this positive unit-test fixture.
        scale=1.
        def __init__(self):
            self.model=SimpleNamespace(score_evaluations=0)
            self.calls=[]
        def infer(self, public):
            self.calls.append(public.operator.copy());self.model.score_evaluations+=10
            return dict(estimate=mean,activity_decision=np.ones(3,bool),
                        probabilities=np.ones(3),noise_variance_estimate=np.array(1e-10)), dict(
                        diagnostics=[dict(feedback_variance=0.)])
    receiver=OracleMeanTestDouble()
    values, record=s.infer(receiver,y,pilot,.1,s.Controls(outer_updates=2))
    np.testing.assert_array_equal(receiver.calls[0],pilot)
    np.testing.assert_allclose(values['phase'],phase,atol=2e-6)
    assert record['conditional_calls']==3 and record['unfolded_layers_executed']==30
    assert record['physical_path_search_used'] is False
