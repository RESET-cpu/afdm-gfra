"""Public command and protocol regression checks; no GPU or training needed."""
import ast
import json
from pathlib import Path

import numpy as np
import pytest

from workspace import ROOT
from experiment import cli, suite
from scenario.catalog import scene_rows, condition_key, DEFAULT


@pytest.mark.parametrize('name', list(cli.DESCRIPTIONS))
def test_every_final_entry_explains_its_commands(name, capsys):
    with pytest.raises(SystemExit) as error:
        cli.main([name, '--help'])
    assert error.value.code == 0
    assert 'plan,run,summarize,inspect' in capsys.readouterr().out


def test_legacy_is_deferred_in_public_list(capsys):
    assert cli.main(['list']) == 0
    text = capsys.readouterr().out
    assert text.count('ENABLED') == 7
    assert 'DEFERRED_BY_USER' in text


def test_shared_registry_identity_and_endpoints():
    rows = scene_rows()
    assert len(rows) == 2000
    assert rows[0]['seed'] == 202610219100001
    assert rows[-1]['seed'] == 202610219102000
    assert len({row['seed'] for row in rows}) == 2000
    assert condition_key(DEFAULT) == condition_key(dict(DEFAULT, snr_db=0.0))


def test_inference_package_has_no_historical_imports():
    for folder in ['receiver', 'experiment']:
        for path in (ROOT/'src'/folder).rglob('*.py'):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    assert not (node.module or '').startswith(('experiments.', '_support', '_common'))


def test_legacy_opt_in_and_registry_bounds_are_enforced(tmp_path):
    for count in ('0', '2001'):
        with pytest.raises(ValueError, match='outside the fixed registry subset'):
            suite.main('snr_comparison', ['plan', '--scenes', count, '--output', str(tmp_path/count)])
