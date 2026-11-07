"""Regression checks for valid inputs and reproducible execution; no training."""
import json
from types import SimpleNamespace

import numpy as np
import pytest

from workspace import ROOT
from fileio import read_json, write_json, sha256


def test_training_identity_includes_trainers_and_shared_physics(monkeypatch, tmp_path):
    from training.stmp import common
    hashes = common.source_hashes()
    for package in ('training/stmp', 'training/scores', 'scenario', 'waveform', 'channel'):
        for path in (ROOT/'src'/package).rglob('*.py'):
            assert hashes[path.relative_to(ROOT).as_posix()] == sha256(path)
    monkeypatch.setattr(common, 'ROOT', tmp_path)
    with pytest.raises(FileNotFoundError):
        common.source_hashes()


def test_recipe_inspection_needs_no_prior_or_training_assets(monkeypatch, capsys):
    from training.stmp import cli
    monkeypatch.setattr(cli, 'load_prior', lambda *_: pytest.fail('Inspection loaded a prior'))
    cli.main(['--inspect'])
    assert json.loads(capsys.readouterr().out)['optimizer_updates'] == 0
    config = cli.load_recipe()
    assert cli.resolve(config['receiver_template']).is_file()
    assert config['runtime']['device'] == 'cpu'


def test_gp_mp_ep_phase_contract_is_checked_before_loading_weights():
    from receiver.registry import select, load_catalog
    definitions = load_catalog()
    with pytest.raises(ValueError, match='use GP_MP'):
        select(['GP_MP_EP'], definitions, 'receiver', phase_mode='known')
    assert select(['GP_MP_EP'], definitions, 'receiver')['GP_MP_EP']['phase_input'] == 'raw'
    assert select(['GP_MP'], definitions, 'receiver', phase_mode='known')['GP_MP']['phase_input'] == 'operator'


def test_factor_graph_only_checks_its_own_dependencies(monkeypatch):
    from plotting import render_paper
    config = render_paper.read(render_paper.DEFAULT_CONFIG)
    monkeypatch.setattr(render_paper, 'sha', lambda _: pytest.fail('Unrelated source requested'))
    assert render_paper.verify_sources(config, ['factor_graph']) == {}
    assert 'paper/build/main.aux' in config['figures']['learned_receiver']['dependencies']


def record(active=2, inactive=0):
    return dict(metrics=dict(full_error=2., signal_energy=4., active=active, inactive=inactive,
                             misses=1, false_alarms=0, nmse_db=10*np.log10(.5)),
                receiver_seconds=1., phase_seconds=0., end_to_end_seconds=1., backend='cpu',
                parameter_count=0, iterations=1)


def test_all_active_results_complete_without_inventing_false_alarm_rate(tmp_path, monkeypatch):
    from experiment.reporting import finish
    monkeypatch.setattr('plotting.summary.plot', lambda *_: None)
    compact = tmp_path/'fixture.npz'
    np.savez(compact, truth_activity=np.ones(2, bool), activity_decision=np.array([True, False]),
             per_user_error=np.ones(2))
    row = dict(record(), status='COMPLETE', compact_sha256=sha256(compact))
    saved = tmp_path/'fixture.json'
    write_json(saved, row)
    write_json(tmp_path/'scene0000/condition00/fixture.json', dict(result=str(saved), sha256=sha256(saved)))
    plan = dict(algorithm_specs={'fixture': {'label': 'Synthetic fixture'}}, experiment_kind='receiver',
                conditions=[{'users': 2}], methods=['fixture'], scene_count=1, base_seed=0,
                reference_method='fixture', extra_comparisons=[], device='cpu', mode='diagnostic',
                experiment='user_count', phase_mode='known', noise_mode='known', timing={},
                ablation_scope=None, denoising_scope=None, timing_repeats=1, assets={}, formal_panel_sha256='synthetic')
    assert finish(tmp_path, plan) == 0
    summary = read_json(tmp_path/'SUMMARY.json')
    actual = summary['rows'][0]
    assert summary['status'] == 'COMPLETE' and actual['completed'] == 1
    assert actual['false_alarm_rate'] is None and actual['inactive'] == 0
    assert actual['miss_rate'] == actual['aer'] == .5
    assert actual['nmse_db'] == pytest.approx(10*np.log10(.5))
    assert 'N/A' in (tmp_path/'REPORT.md').read_text(encoding='utf-8')


def test_bootstrap_keeps_undefined_resamples_and_reports_their_count():
    from experiment.reporting import pair_intervals
    rows = [record(), record(inactive=1)]
    plan = dict(bootstrap_seed=23, bootstrap_replicates=40)
    result = pair_intervals(rows, rows, plan)
    picks = np.random.default_rng(23).integers(0, 2, size=(40, 2))
    assert result['delta_false_alarm_rate'] == 0.
    assert result['delta_false_alarm_rate_ci95'] is None
    assert result['delta_false_alarm_rate_undefined_resamples'] == np.all(picks == 0, axis=1).sum()
    assert result['delta_aer_ci95'] == [0., 0.]
    assert result['delta_nmse_db_ci95'] == [0., 0.]
    json.dumps(result, allow_nan=False)


class AnalyticMoments:
    noise_support = (.01, 10.)
    scale_ratio = 1.

    def __init__(self):
        self.samples = self.first_calls = self.second_calls = 0
        self.fraction = .5

    def infer(self, query, variance):
        self.samples += len(query)
        self.first_calls += 1
        self.second_calls += 1
        return SimpleNamespace(mean=query/(1+variance[:, None, None, None]), variance=self.fraction*variance)


def test_gaussian_ablation_uses_no_classifier_and_keeps_fallback_site():
    from receiver.stmp.denoiser import Denoiser
    from receiver.stmp_ablation.denoiser import Denoiser as Gaussian
    from receiver.stmp.posterior import full_posterior
    model = AnalyticMoments()
    with pytest.raises(ValueError, match='balanced classifier'):
        Denoiser(model, None, activity_prior=.2, conditional_variance_floor=1e-6)
    denoiser = Gaussian(model, None, activity_prior=.2, conditional_variance_floor=1e-6)
    query = np.ones((2, 2, 2, 2), complex)*(.1+.2j)
    for variance, fraction in ((1., .5), (1., 2.), (20., .5)):
        model.fraction = fraction
        actual = denoiser(query, np.eye(2)*variance)
        expected = full_posterior(query, variance, denoiser.site_mean, denoiser.site_variance, .2)
        np.testing.assert_array_equal(actual.mean, expected.mean)
        np.testing.assert_array_equal(actual.activity, expected.activity)
        assert denoiser.classifier_calls == denoiser.activity_evidence_calls == 0
    assert denoiser.last['probability_source'] == 'reused_gaussian_site_fallback'
    assert model.samples == 4
