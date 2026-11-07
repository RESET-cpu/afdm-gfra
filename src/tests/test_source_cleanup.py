"""Storage and shared STMP controls; no trained receiver is executed."""
import ast
import gzip
import hashlib
import importlib
import json
import warnings

import numpy as np
import pytest

from algorithm import registry
from algorithm.STMP import receiver as stmp
from algorithm.STMP.denoiser import Denoiser
from evaluation.STMP_ablation.receiver import Receiver as AblationReceiver
from evaluation.STMP_ablation.denoiser import Denoiser as AblationDenoiser
from project import ROOT, SOURCE_PACKAGES, source_files
from utils import read_json, write_json, sha256, json_digest


def test_json_unicode_bom_gzip_and_identity(tmp_path):
    value = {'说明': '共享场景', 'results': [1, .5, None]}
    path = tmp_path/'record.json'
    write_json(path, value)
    assert read_json(path) == value
    assert '共享场景' in path.read_text(encoding='utf-8')
    assert sha256(path) == hashlib.sha256(path.read_bytes()).hexdigest()
    assert json_digest(value) == json_digest(dict(reversed(list(value.items()))))
    path.write_text(json.dumps(value), encoding='utf-8-sig')
    assert read_json(path) == value
    with gzip.open(tmp_path/'record.json.gz', 'wt', encoding='utf-8-sig') as stream:
        json.dump(value, stream, ensure_ascii=False)
    assert read_json(tmp_path/'record.json.gz') == value


def test_invalid_json_cannot_replace_a_valid_record(tmp_path):
    path = tmp_path/'record.json'
    write_json(path, {'status': 'COMPLETE'})
    before = path.read_bytes()
    with pytest.raises(ValueError):
        write_json(path, {'metric': float('nan')})
    assert path.read_bytes() == before
    assert list(tmp_path.iterdir()) == [path]


def test_stmp_configuration_is_resolved_once_and_saved_in_full(tmp_path, monkeypatch):
    config = {'scale': .25, 'ep': {'iterations': 600}}
    (tmp_path/'final').mkdir()
    write_json(tmp_path/'STMP.json', config)
    write_json(tmp_path/'final/models.json', {'STMP_configuration': 'STMP.json', 'proposed': {'depth': 10}})
    monkeypatch.setattr(registry, 'CONFIGS', tmp_path)
    monkeypatch.setattr(registry, 'ROOT', tmp_path)
    saved = registry.load_models()
    assert saved['STMP'] == config and 'STMP_configuration' not in saved
    config['scale'] = .5
    write_json(tmp_path/'STMP.json', config)
    assert registry.load_models()['STMP']['scale'] == .5
    assert saved['STMP']['scale'] == .25  # A frozen plan retains its resolved settings.


def test_current_package_has_unambiguous_responsibilities():
    assert not (ROOT/'src/afdm_jadcedd').exists()
    for name in SOURCE_PACKAGES:
        assert (ROOT/'src'/name/'__init__.py').is_file()
    for path in source_files():
        assert not {'history', 'configs', 'tests'}.intersection(path.relative_to(ROOT/'src').parts)
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8-sig'))):
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or '').startswith(('afdm_jadcedd', 'history'))
            if isinstance(node, ast.Import):
                assert not any(item.name.startswith(('afdm_jadcedd', 'history')) for item in node.names)
    for module in ['evaluation.metrics', 'system.scenario.generate', 'system.scenario.unknown_phase',
                   'training.STMP.cli', 'training.gnn.cli', 'training.gnn.common']:
        importlib.import_module(module)


def test_training_source_record_uses_existing_package_files():
    from training.gnn import common
    record = common.source_identity(common.__file__)
    assert record['generator_sha256'] == sha256(ROOT/'src/system/scenario/generate.py')
    assert all(sha256(ROOT/path) == expected for path, expected in record['source_sha256'].items())
    # The historical report string is provenance, not a runtime dependency.
    assert record['source_report'] == 'results/baseline_revision_20261008/phase2_sources/GNN_ASPL_SOURCE.md'


@pytest.mark.parametrize('accepted,residual,change,expected', [
    (True, .009, .00009, True), (False, .009, .00009, False),
    (True, .01, .00009, False), (True, .009, .0001, False),
    (True, None, .00009, False), (True, .009, None, False),
])
def test_ablation_uses_the_identical_freshness_decision(accepted, residual, change, expected):
    assert AblationDenoiser.message_is_fresh is Denoiser.message_is_fresh
    model = object.__new__(AblationDenoiser)
    model.raw_site_residual_tolerance = .01
    model.activity_weight_residual_tolerance = .0001
    assert model.message_is_fresh(accepted, residual, change) is expected


@pytest.mark.parametrize('parent', [stmp.Receiver, AblationReceiver])
@pytest.mark.parametrize('fail', [False, True])
def test_shared_file_runner_preserves_success_failure_and_warnings(tmp_path, monkeypatch, parent, fail):
    assert AblationReceiver.run is stmp.Receiver.run
    token = object()
    monkeypatch.setattr(stmp, 'load_input', lambda path: token)

    class SyntheticReceiver(parent):
        def __init__(self):
            pass

        def context(self):
            return {'synthetic_fixture': True}

        def infer(self, inputs, *, observer=None):
            assert inputs is token
            warnings.warn('synthetic warning', RuntimeWarning)
            if fail:
                raise RuntimeError('synthetic failure')
            return {'estimate': np.array([1., 2.])}, dict(self.context(), status='COMPLETE')

    inputs = tmp_path/'input.npz'
    np.savez(inputs, value=np.array([1]))
    output = tmp_path/'output.npz'
    model = SyntheticReceiver()
    if fail:
        with pytest.raises(RuntimeError, match='synthetic failure'):
            model.run(inputs, output)
        record = read_json(output.with_suffix('.json'))
        assert record['status'] == 'FAILED' and 'synthetic failure' in record['error']
        assert not output.exists()
    else:
        record = model.run(inputs, output)
        assert record['status'] == 'COMPLETE' and record['output_sha256'] == sha256(output)
        with np.load(output) as data:
            np.testing.assert_array_equal(data['estimate'], [1., 2.])
    assert record['input_sha256'] == sha256(inputs)
    assert read_json(output.with_suffix('.warnings.json'))[0]['message'] == 'synthetic warning'
    original = output.with_suffix('.json').read_bytes()
    with pytest.raises(ValueError, match='existing attempts are preserved'):
        model.run(inputs, output)
    assert output.with_suffix('.json').read_bytes() == original
