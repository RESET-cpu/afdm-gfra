"""Check the public algorithm names and fail-closed current-source validation."""
from pathlib import Path
import ast

import pytest

from workspace import ROOT
from receiver import registry
from receiver.baseline import _validation


def test_current_public_algorithm_names_and_factories():
    catalog = registry.load_catalog()
    assert set(registry.ALGORITHMS) == {'GP_MP', 'GP_MP_EP', 'STMP', 'offgrid_sbl', 'gnn', 'gamp', 'somp'}
    assert not (ROOT/'src/algorithm').exists()
    for name in registry.ALGORITHMS:
        assert catalog[name]['factory'].startswith('receiver.')
        assert callable(registry.factory(catalog[name]))


def test_changed_baseline_source_is_rejected(monkeypatch):
    sources = _validation.inference_sources()
    sources['src/receiver/baseline/gnn.py'] = '0'*64
    monkeypatch.setattr(_validation, 'inference_sources', lambda *args: sources)
    with pytest.raises(ValueError, match='differs from the verified current version'):
        _validation.verify_current_sources()
