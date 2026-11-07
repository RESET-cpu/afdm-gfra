"""Gaussian algebra, message continuity, readiness and output stopping checks."""
from dataclasses import replace
from types import SimpleNamespace
import numpy as np
import pytest
from algorithm.C_STMP_phase_conditional_schedule_20261104 import phase, iterations
from algorithm.C_STMP_phase_shen_frames_20261103 import phase as frozen_phase, moments
from algorithm.STMP.records import SpatialConfig
from test_phase_shen_frames_20261103 import _case, _full_posterior
from test_phase_direct_integration_20261103 import _input


@pytest.mark.parametrize('seed', [19, 73])
def test_proposal_unchanged_and_signal_change_matches_dense_posterior(seed):
    case = _case(seed=seed)
    proposed, record = phase.update(*case)
    old, old_record = frozen_phase.update(*case)
    np.testing.assert_array_equal(proposed, old)
    for key in ('conditional_before', 'conditional_after', 'before', 'after'):
        assert record[key] == old_record[key]
    y, pilot, _, _, noise, current = case
    posterior, covariance, _, _ = _full_posterior(case)
    q, k, n = pilot.shape
    old_operator = (pilot*current[:, :, None]).reshape(q, k*n)
    delta = (pilot*(proposed-current)[:, :, None]).reshape(q, k*n)
    columns = y.shape[1]*y.shape[2]
    energy = lambda op: float(np.linalg.norm(op@posterior)**2 + columns*np.trace(op@covariance@op.conj().T).real)
    expected = np.sqrt(energy(delta)/(energy(old_operator)+noise*y.size))
    np.testing.assert_allclose(record['phase_effect']['relative_signal_change'], expected, rtol=2e-12)


def test_signal_change_does_not_require_unobservable_user_angles_to_settle():
    current = np.ones((3, 2), complex)
    proposed = current.copy(); proposed[1:, 1] = -1.
    gram = np.zeros((3, 2, 2), complex); gram[:, 0, 0] = 2.
    assert phase.signal_change(current, proposed, gram, 1.)['relative_signal_change'] == 0.
    proposed[1:, 0] = 1j
    assert phase.signal_change(current, proposed, gram, 1.)['relative_signal_change'] > .1


class ConstantDenoiser:
    message_fresh = True
    last = dict(site_accepted=True, unsupported_users=0)
    def __call__(self, r, v):
        k, m = r.shape[:2]
        mean = np.full_like(r, .15+.1j)
        return SimpleNamespace(mean=mean, conditional_mean=mean, activity=np.full(k, .8),
            spatial_covariance=np.broadcast_to(np.eye(m)*.2, (k, m, m)))


class Linear:
    def __init__(self, pilot, m, noise):
        self.pilot, self.antennas = pilot, m
    def update(self, y, prior, prior_cov):
        r = np.full_like(prior, .5+.2j)*self.pilot.mean()
        return None, None, r, np.eye(self.antennas)
    def forward(self, mean):
        return np.einsum('qkn,kmrn->qmr', self.pilot, mean)


def _run(monkeypatch, effects, *, count=6, minimum=2, accepted=True, queries=None):
    monkeypatch.setattr(iterations, 'SpatialLinear', Linear)
    controls = SpatialConfig(iterations=count, min_iterations=minimum, damping=.4,
        convergence_tolerance=1e3, convergence_patience=1, decision_stability_window=1,
        activity_convergence_tolerance=.01, covariance_mode='isotropic')
    proposed = []
    def update(y, pilot, mean, variance, noise, current):
        next_phase = current.copy();next_phase[1:] *= np.exp(.1j)
        effect = effects[min(len(proposed), len(effects)-1)]
        proposed.append((current.copy(), next_phase.copy()))
        return next_phase, dict(seconds=0., phase_effect=dict(relative_signal_change=effect))
    monkeypatch.setattr(iterations, 'update_phase', update)
    denoiser = ConstantDenoiser()
    denoiser.last = dict(site_accepted=accepted, unsupported_users=0)
    result = iterations.infer(_input(), denoiser, scale=.7, initial_variance=.4,
        controls=controls, phase_configuration=dict(relative_signal_change_tolerance=.01),
        initial_slopes=np.array([.1, -.2, .3]),
        observer=None if queries is None else lambda row, state, r, *args: queries.append(r.copy()))
    return result, proposed


def test_continuity_and_current_proposal_stopping_without_modulo_wait(monkeypatch):
    queries = []
    (result, used, steps, trials), proposals = _run(monkeypatch, [.2, .001], queries=queries)
    assert result.stopping_reason == 'CONVERGED'
    assert [t['after_iteration'] for t in trials] == [2, 3]
    assert len(steps) == 1 and not trials[-1]['applied']
    np.testing.assert_array_equal(used, proposals[0][1])
    assert result.trace[2]['query_variance_ratio'] == result.trace[1]['next_query_variance_ratio']
    assert result.trace[2]['query_variance_ratio'] != 1.
    assert not steps[0]['query_damping_history_reset']
    assert result.trace[-1]['conditional_converged']
    raw_next = np.full_like(queries[1], .5+.2j)*frozen_phase.effective_pilot(_input().pilot, proposals[0][1]).mean()
    np.testing.assert_allclose(queries[2], .6*queries[1]+.4*raw_next, rtol=1e-14, atol=1e-14)
    assert np.linalg.norm(queries[2]-raw_next) > 1e-5


def test_small_first_proposal_can_stop_without_forced_phase_update(monkeypatch):
    (result, used, steps, trials), proposals = _run(monkeypatch, [.001])
    assert result.stopping_reason == 'CONVERGED' and not steps
    np.testing.assert_array_equal(used, proposals[0][0])


def test_small_channel_change_alone_does_not_stop(monkeypatch):
    (result, used, steps, trials), proposals = _run(monkeypatch, [.2], count=4)
    assert result.stopping_reason == 'MAX_ITERATIONS'
    assert not trials[-1]['applied'] and trials[-1]['after_iteration'] == 4
    np.testing.assert_array_equal(used, proposals[-1][0])
    assert len(steps) == 2


def test_invalid_moments_prevent_update_and_stopping(monkeypatch):
    (result, used, steps, trials), proposals = _run(monkeypatch, [.001], accepted=False)
    assert result.stopping_reason == 'MAX_ITERATIONS' and not trials


def test_initial_conditional_minimum_is_honored(monkeypatch):
    (result, used, steps, trials), proposals = _run(monkeypatch, [.001], minimum=5)
    assert trials[0]['after_iteration'] == 5


def test_periodic_ablation_keeps_initial_path_and_only_changes_state_handoff(monkeypatch):
    import json
    from project import ROOT
    from algorithm.C_STMP_phase_conditional_schedule_20261104 import periodic
    from algorithm.C_STMP_phase_shen_frames_20261103 import iterations as frozen
    controls = SpatialConfig(iterations=6, min_iterations=2, damping=.4,
        convergence_tolerance=1e3, convergence_patience=1, decision_stability_window=1,
        activity_convergence_tolerance=.01, covariance_mode='isotropic')
    config = json.loads((ROOT/'src/configs/candidates/c_stmp_phase_selection_20261030/physical_no_hypotheses_legacy_stop.json').read_text())['phase']
    config['periodic_update'] = dict(start=2, interval=2)
    config['minimum_iterations_after_last_update'] = 1
    config['stopping']['require_stable_decisions'] = 1
    results = []
    for module in (frozen, periodic):
        monkeypatch.setattr(module, 'SpatialLinear', Linear)
        results.append(module.infer(_input(), ConstantDenoiser(), scale=.7, initial_variance=.4,
            controls=controls, phase_configuration=config, initial_slopes=np.array([.1,-.2,.3])))
    old, new = results
    assert old[2][0]['after_iteration'] == new[2][0]['after_iteration'] == 2
    assert old[0].trace[2]['query_variance_ratio'] == 1.
    assert new[0].trace[2]['query_variance_ratio'] == new[0].trace[1]['next_query_variance_ratio']
    assert new[0].trace[2]['query_variance_ratio'] != 1.
    np.testing.assert_array_equal(old[2][0]['after_phase_real'], new[2][0]['after_phase_real'])
    assert not new[2][0]['query_damping_history_reset']
