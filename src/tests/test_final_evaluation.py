"""Public command and protocol regression checks; no GPU or training needed."""
import ast
import json
from pathlib import Path

import numpy as np
import pytest

from project import ROOT
from evaluation import cli, suite
from evaluation.scenes import scene_rows, condition_key, DEFAULT
from algorithm.proposed.inputs import pack, unpack, prepare_public


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


@pytest.mark.parametrize('users,frames', [(20, 8), (40, 16), (100, 48)])
def test_public_packing_and_forward_operator_agree(users, frames):
    import torch
    rng = np.random.default_rng(72)
    operator = rng.normal(size=(frames, users, 16)) + 1j*rng.normal(size=(frames, users, 16))
    channel = rng.normal(size=(users, 16, 16, 16)) + 1j*rng.normal(size=(users, 16, 16, 16))
    received = np.einsum('qkn,kmrn->qmr', operator, channel)
    public, _ = prepare_public(dict(y=received, a=operator, noise=.1, rho=.1), 1., 'cpu',
                               phase_mode='known', noise_mode='known')
    tensor = torch.tensor(np.stack((channel.real, channel.imag), axis=1), dtype=torch.float32)
    torch.testing.assert_close(unpack(pack(tensor), tensor.shape), tensor, rtol=0, atol=0)
    torch.testing.assert_close(public['a']@pack(tensor), public['y'], rtol=2e-5, atol=2e-4)


def test_inference_package_has_no_historical_imports():
    for folder in ['algorithm/proposed', 'evaluation']:
        for path in (ROOT/'src'/folder).rglob('*.py'):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    assert not (node.module or '').startswith(('experiments.', '_support', '_common'))


def test_legacy_opt_in_and_registry_bounds_are_enforced(tmp_path):
    with pytest.raises(ValueError, match='deferred'):
        suite.main('snr_comparison', ['plan', '--methods', 'STMP', '--output', str(tmp_path/'STMP')])
    for count in ('0', '2001'):
        with pytest.raises(ValueError, match='outside the fixed registry subset'):
            suite.main('snr_comparison', ['plan', '--scenes', count, '--output', str(tmp_path/count)])
