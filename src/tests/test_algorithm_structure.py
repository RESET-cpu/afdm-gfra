"""Check the public algorithm names and fail-closed current-source validation."""
from pathlib import Path
import ast

import pytest

from project import ROOT
from algorithm import registry
from algorithm.baseline import _validation


def test_three_public_algorithm_groups_and_current_names():
    folder = ROOT/'src/algorithm'
    assert {p.name for p in folder.iterdir() if p.is_dir() and not p.name.startswith('_')} == {
        'proposed', 'STMP', 'baseline', 'candidates'}
    assert registry.ALGORITHMS == ('proposed','STMP','offgrid_sbl','gnn','gamp','somp')
    # Independent research candidates are retained outside the public catalog.
    catalog = registry.load_catalog()
    assert {catalog[name]['group'] for name in registry.ALGORITHMS} == {
        'proposed', 'STMP', 'baseline'}
    assert all(not catalog[name]['factory'].startswith('algorithm.candidates.')
               for name in registry.ALGORITHMS)
    assert not any(p.is_dir() for p in (folder/'baseline').iterdir() if not p.name.startswith('_'))
    for path in folder.rglob('*.py'):
        source = path.read_text(encoding='utf-8')
        assert 'src/history' not in source and 'algorithm.baselines' not in source
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or '').startswith(('history.', 'experiments.'))


def test_changed_baseline_source_is_rejected(monkeypatch):
    sources = _validation.inference_sources()
    sources['src/algorithm/baseline/gnn.py'] = '0'*64
    monkeypatch.setattr(_validation, 'inference_sources', lambda *args: sources)
    with pytest.raises(ValueError, match='differs from the verified current version'):
        _validation.verify_current_sources()
