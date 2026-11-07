"""Paired checks for organization only; no training or formal experiments."""
import ast
from copy import deepcopy
import hashlib
import importlib
import json
from pathlib import Path

import numpy as np
import pytest

from workspace import ROOT, frozen_read_path


def same_tree(a, b):
    if isinstance(a, dict):
        assert a.keys() == b.keys()
        for key in a:
            same_tree(a[key], b[key])
    elif isinstance(a, (tuple, list)):
        assert len(a) == len(b)
        for x, y in zip(a, b):
            same_tree(x, y)
    elif isinstance(a, np.ndarray):
        np.testing.assert_array_equal(a, b)
    else:
        assert a == b


def test_frozen_source_files_keep_original_bytes():
    mapping = json.loads((ROOT/'archive/code_organization_20261107/MAPPING.json').read_text())
    retirement = json.loads((ROOT/'archive/du_removal_20261107/REMOVAL.json').read_text())
    excluded = {row['path'] for row in retirement['excluded_sources']}
    moved = {row['source']: row['destination'] for row in retirement['moved_working_helpers']}
    for row in mapping['files']:
        if row['source'] in excluded:
            continue  # Explicitly retired DU sources; retained sources still require identical bytes.
        assert hashlib.sha256(frozen_read_path(ROOT/row['source']).read_bytes()).hexdigest() == row['source_sha256']
        if row['destination'] not in excluded or row['destination'] in moved:
            destination = moved.get(row['destination'], row['destination']).replace('training/organized/', 'training/')
            assert (ROOT/destination).is_file()


@pytest.mark.parametrize('mode', ['generate', 'unknown_phase'])
def test_paired_scenario_observation_truth_and_metadata(mode):
    import subprocess, sys, pickle
    new = importlib.import_module('scenario.'+mode)
    # Explicit small diagnostic scene, independent of the formal scene panel.
    args = (926451, 0., 1.)
    kwargs = dict(users=3, frames=3, activity_probability=.5)
    script = """
import sys,pickle
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'archive/frozen_reproduction_20261107/src'))
import importlib
m=importlib.import_module('system.scenario.'+sys.argv[1])
sys.stdout.buffer.write(pickle.dumps(m.generate_case(926451,0.,1.,users=3,frames=3,activity_probability=.5)))
"""
    original = pickle.loads(subprocess.check_output([sys.executable,'-B','-c',script,mode],cwd=ROOT))
    same_tree(original, new.generate_case(*args, **kwargs))


@pytest.mark.parametrize('delay,doppler', [(2., 500.), (2.37, -700.5), (35.2, 100.25)])
def test_integer_fractional_and_multiframe_waveform(delay, doppler):
    import subprocess, sys, pickle
    from waveform.afdm.continuous import continuous_path_matrix as new
    args = (16, delay, doppler, 1/1e6, 32, 3/32, .001)
    script = """
import sys,pickle
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'archive/frozen_reproduction_20261107/src'))
from system.afdm.continuous import continuous_path_matrix
sys.stdout.buffer.write(pickle.dumps(continuous_path_matrix(16,float(sys.argv[1]),float(sys.argv[2]),1/1e6,32,3/32,.001)))
"""
    original=pickle.loads(subprocess.check_output([sys.executable,'-B','-c',script,str(delay),str(doppler)],cwd=ROOT))
    np.testing.assert_array_equal(original, new(*args))


def test_receiver_configuration_and_metric_results_match():
    from receiver import registry as new
    before=json.loads(frozen_read_path(ROOT/'src/configs/algorithms.json').read_text())['algorithms']
    after=new.load_catalog()
    assert before.keys() - {'DU', 'proposed'} == after.keys()
    for name, spec in after.items():
        assert new.factory(spec).__module__.startswith('receiver.')
        a, b = deepcopy(before[name]), deepcopy(spec)
        # Only source locations change, never scientific arguments or weights.
        for v in (a, b):
            v.pop('factory')
            if 'known_noise' in v:
                v['known_noise'].pop('factory', None)
            v['assets'] = [p for p in v.get('assets', []) if not p.endswith('.py')]
        assert a == b
    import importlib.util
    spec=importlib.util.spec_from_file_location('frozen_metrics',frozen_read_path(ROOT/'src/evaluation/metrics.py'))
    old_metrics=importlib.util.module_from_spec(spec);spec.loader.exec_module(old_metrics)
    old_score=old_metrics.score_arrays
    from experiment.metrics import score_arrays as new_score
    truth = dict(channel=np.array([1., 0.]).reshape(2,1,1,1), activity=np.array([1,0]))
    output = dict(estimate=np.array([.75, .1]).reshape(2,1,1,1), activity_decision=np.array([1,1]))
    same_tree(old_score(output, truth), new_score(output, truth))


def test_physics_does_not_import_inference_experiments_or_plotting():
    base = ROOT/'src'
    prohibited = ('receiver', 'experiment', 'plotting', 'training.organized')
    for area in ('scenario', 'waveform', 'channel'):
        for path in (base/area).rglob('*.py'):
            for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
                if isinstance(node, ast.ImportFrom):
                    assert not (node.module or '').startswith(prohibited), path
                if isinstance(node, ast.Import):
                    assert not any(a.name.startswith(prohibited) for a in node.names), path


def test_readonly_entry_points_and_frozen_followup_dispatch(monkeypatch, capsys):
    from experiment.commands import main
    assert main(['list']) == 0
    assert 'GP_MP' in capsys.readouterr().out
    assert main(['plot', '--list']) == 0
    assert 'channel_denoising' in capsys.readouterr().out
    from experiment.studies.white_followup import run
    monkeypatch.setattr(run, 'main', lambda argv: ('frozen', argv))
    assert main(['white_followup', 'inspect']) == ('frozen', ['inspect'])


def test_generic_output_cannot_default_to_a_frozen_batch():
    from experiment import suite
    assert suite.DEFAULT_OUTPUT == ROOT/'result/organized_default_20261107'
    from workspace import source_files, physical_source_files
    assert all(p.is_relative_to(ROOT/'src') for p in source_files())
    assert physical_source_files()
    assert set(physical_source_files()) <= set(source_files())
