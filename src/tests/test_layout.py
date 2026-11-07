"""Relocation must preserve the public entry points and frozen baseline bindings."""
from pathlib import Path
import json
import subprocess
import sys

import pytest

from project import ROOT, CONFIGS, repository_path
from algorithm import registry
from utils import sha256


def test_four_visible_top_level_folders():
    assert {p.name for p in ROOT.iterdir() if p.is_dir() and not p.name.startswith('.')} == {
        'src', 'result', 'paper', 'reference'}


def test_installed_imports_and_entrypoints_work_outside_repository(tmp_path):
    code = """
import importlib, importlib.util, json
names = ['algorithm', 'evaluation', 'networks', 'system', 'training', 'project', 'utils']
assert importlib.util.find_spec('afdm_jadcedd') is None
print(json.dumps({name: importlib.import_module(name).__file__ for name in names}))
"""
    result = subprocess.run([sys.executable, '-I', '-B', '-c', code], cwd=tmp_path,
                            check=True, capture_output=True, text=True)
    for name, filename in json.loads(result.stdout).items():
        expected = ROOT/'src'/name/'__init__.py' if name not in {'project', 'utils'} else ROOT/'src'/(name+'.py')
        assert Path(filename).resolve() == expected
    console = Path(sys.executable).parent/('jadce.exe' if sys.platform == 'win32' else 'jadce')
    for command in ([sys.executable, '-I', '-B', str(ROOT/'run_experiments.py'), 'list'],
                    [str(console), 'list'],
                    [sys.executable, '-I', '-B', str(ROOT/'src/evaluation/experiments/snr_comparison.py'), '--help']):
        result = subprocess.run(command, cwd=tmp_path, check=True, capture_output=True, text=True)
        assert 'snr_comparison' in result.stdout or 'plan,run,summarize,inspect' in result.stdout


def test_old_and_new_asset_locations_resolve_to_same_bytes():
    assert repository_path('configs/final/receiver.json') == CONFIGS/'final/receiver.json'
    assert repository_path('src/configs/final/receiver.json') == CONFIGS/'final/receiver.json'
    assert repository_path('models/gnn/checkpoint.pt') == ROOT/'result/models/gnn/checkpoint.pt'
    binding = registry.load_models()
    for name in ('first_checkpoint', 'second_checkpoint', 'evidence_checkpoint', 'prior_definition'):
        path = repository_path(binding['STMP'][name])
        assert sha256(path) == binding['STMP'][name+'_sha256']
    # External training locations must never be redirected into the workspace.
    path = Path(binding['proposed']['checkpoint'])
    assert repository_path(path) == path


@pytest.mark.parametrize('method', ['somp', 'gamp', 'gnn', 'offgrid_sbl'])
def test_baseline_factory_retains_frozen_solver_and_activity_binding(method):
    # Construction verifies the existing source signatures, policies and GNN SHA.
    # No inference or old three-network experiment is run here.
    model = registry.build_receiver(method, binding={}, device='cpu')
    assert model.base.signature
    assert model.method == method
