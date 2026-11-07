"""Synthetic experiment pipeline checks for the organized working package."""
from copy import deepcopy


import json


from pathlib import Path


import numpy as np


import pytest


from receiver import registry


from receiver.baseline import _validation


from experiment import suite


from experiment import experiments


from experiment.experiments.channel_denoising import evaluate_case


from workspace import ROOT


from fileio import read_json


from fileio import sha256


from channel.observation import ReceiverInput


def write(path, value):
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')
    return path


def test_unknown_duplicate_and_wrong_kind_methods_rejected():
    catalog = registry.load_catalog()
    with pytest.raises(ValueError, match='Unregistered'):
        registry.select(['missing'], catalog, 'receiver')
    with pytest.raises(ValueError, match='distinct'):
        registry.select(['somp', 'somp'], catalog, 'receiver')
    with pytest.raises(ValueError, match='not a receiver'):
        registry.select(['noisy'], catalog, 'receiver')


def test_baseline_only_plan_does_not_require_unselected_network_weights():
    definitions = registry.select(['somp'], registry.load_catalog(), 'receiver')
    config, _ = suite.experiment_config('snr_comparison')
    binding = registry.load_models()
    # These files intentionally do not exist. A selected SOMP plan still works.
    binding['proposed']['checkpoint'] = 'absent_proposed.pt'
    binding['proposed']['run'] = 'absent_training'
    binding['STMP']['first_checkpoint'] = 'absent_first.pt'
    assets = suite.assets(binding, definitions, config, 'cpu')
    assert not any(p.endswith('.pt') for p in assets)


def test_configured_receiver_runs_and_reports_without_editing_dispatch(tmp_path, monkeypatch):
    # A deliberately synthetic contract fixture, not a research baseline.
    module = tmp_path/'fixture_receiver.py'
    module.write_text('''import numpy as np
class Receiver:
    def __init__(self, gain, *, device):
        assert device == 'cpu'
        self.gain = gain
    def infer(self, inputs):
        estimate = np.full((2, 1, 1, 1), self.gain, complex)
        return dict(estimate=estimate, activity_decision=np.array([True, False])), dict(
            iterations=1, stopping_reason='synthetic contract fixture')
''', encoding='utf-8')
    monkeypatch.syspath_prepend(str(tmp_path))
    specs = {name: dict(kind='receiver', factory='fixture_receiver:Receiver', label=name,
                       backend='cpu', kwargs={'gain':gain}) for name,gain in [('fixture_a',.5),('fixture_b',.6)]}
    catalog = write(tmp_path/'catalog.json', dict(schema='afdm-algorithm-catalog-v1',algorithms=specs))
    _, config = suite.experiment_config('runtime_comparison')
    config.update(methods=list(specs), snr_db=[0])
    configuration = write(tmp_path/'experiment.json', config)
    def small_assets(binding, definitions, config_path, device):
        files = {config_path}
        for spec in definitions.values():
            files.update(registry.source_files(spec, binding, device))
        return {str(p):sha256(p) for p in files}
    monkeypatch.setattr(suite, 'assets', small_assets)
    def small_case(plan, scene, condition):
        public = ReceiverInput(np.ones((1,1,1),complex),np.ones((1,2,1),complex),1.,.5)
        truth = dict(channel=np.array([1.,0.],complex).reshape(2,1,1,1),activity=np.array([True,False]))
        return public,truth,dict(files={'truth':'synthetic'},phase_seconds=0.),tmp_path
    monkeypatch.setattr(suite, 'prepared_case', small_case)
    out = tmp_path/'run'
    assert suite.main('runtime_comparison', ['plan','--smoke','--scenes','2','--device','cpu',
        '--config',str(configuration),'--catalog',str(catalog),'--output',str(out)]) == 0
    plan = read_json(out/'PLAN.json')
    assert plan['methods'] == list(specs)
    assert plan['reference_method'] == 'fixture_a'
    # Execution uses the frozen selected definitions, not a mutable catalog.
    write(catalog, dict(schema='afdm-algorithm-catalog-v1', algorithms={}))
    assert suite.main('runtime_comparison', ['run','--output',str(out)]) == 0
    summary = read_json(out/'SUMMARY.json')
    assert {r['method'] for r in summary['rows']} == set(specs)
    assert summary['paired_differences'][0]['first'] == 'fixture_a'
    assert summary['rows'][0]['full_error'] != summary['rows'][1]['full_error']
    assert (out/'runtime_accuracy.png').exists() and (out/'comparison.pdf').exists()
    assert suite.main('runtime_comparison', ['run','--output',str(out)]) == 0
    module.write_text(module.read_text()+'\n# changed\n')
    with pytest.raises(ValueError, match='asset changed'):
        suite.verify(plan)


