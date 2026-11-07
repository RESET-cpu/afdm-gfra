"""Public commands, portable paths and current configurations; no local weights."""
import json
from pathlib import Path

import pytest
import workspace
from experiment.commands import main
from receiver import registry


def test_readonly_commands_use_repository_configurations(capsys):
    assert main(['list']) == 0
    assert 'GP_MP' in capsys.readouterr().out
    assert main(['plot', '--list']) == 0
    assert 'channel_denoising' in capsys.readouterr().out


def test_demo_writes_new_output_and_preserves_existing_output(tmp_path, capsys):
    out = tmp_path / 'demo'
    assert main(['demo', '--output', str(out)]) == 0
    assert (out/'channel.png').is_file()
    before = (out/'SUMMARY.json').read_bytes()
    with pytest.raises(SystemExit):
        main(['demo', '--output', str(out)])
    assert (out/'SUMMARY.json').read_bytes() == before
    capsys.readouterr()


@pytest.mark.parametrize('value', [r'D:\afdm-gfra\result\models\a.pt',
                                   'D:/afdm-gfra/result/models/a.pt', 'models/a.pt'])
def test_old_project_paths_follow_the_new_checkout(value, tmp_path, monkeypatch):
    monkeypatch.setattr(workspace, 'ROOT', tmp_path)
    assert workspace.repository_path(value) == tmp_path/'result/models/a.pt'


def test_other_external_paths_are_not_rebound(tmp_path, monkeypatch):
    monkeypatch.setattr(workspace, 'ROOT', tmp_path)
    assert workspace.repository_path('E:/external/a.pt') == Path('E:/external/a.pt')
    assert workspace.repository_path('D:/afdm-gfra-other/result/a.pt') == Path('D:/afdm-gfra-other/result/a.pt')
    assert workspace.repository_path('configs/organized/algorithms.json') == workspace.CONFIGS/'organized/algorithms.json'


def test_model_relocation_preserves_hashes_and_frozen_json(tmp_path, monkeypatch):
    source = workspace.CONFIGS/'final/models.json'
    before = source.read_bytes()
    monkeypatch.setattr(workspace, 'ROOT', tmp_path)
    actual = registry.load_models()
    frozen = json.loads(before)
    assert Path(actual['proposed']['checkpoint']).is_relative_to(tmp_path)
    assert actual['proposed']['checkpoint_sha256'] == frozen['proposed']['checkpoint_sha256']
    assert source.read_bytes() == before


def test_documented_diagnostic_selects_only_gp_mp():
    config = json.loads((workspace.CONFIGS/'release/gp_mp_diagnostic.json').read_text())
    assert config['methods'] == ['GP_MP']
    assert config['scenes'] == 1 and config['values'] == [0]
    # The general experiment's STMP opt-in must not add a second receiver.
    assert config['include_stmp'] is False
    assert config['phase_mode'] == 'known'


@pytest.mark.parametrize('name', ['activity_probability', 'channel_denoising', 'cross_channel',
                                  'density_ratio_ablation', 'pilot_frames', 'runtime_comparison',
                                  'snr_comparison', 'user_count'])
def test_current_experiment_defaults_are_registered(name):
    from experiment.suite import experiment_config
    _, config = experiment_config(name)
    catalog = registry.load_catalog()
    # The adopted main-SNR plan uses 1000; the authorized follow-up sweeps
    # use 500. Keep the historical runtime/ablation configuration at 1000.
    expected_scenes = 1000 if name in ('snr_comparison', 'runtime_comparison', 'density_ratio_ablation') else 500
    assert config['scenes'] == expected_scenes
    assert len(set(config['methods'])) == len(config['methods'])
    assert all(method in catalog for method in config['methods'])
    if name == 'channel_denoising':
        assert 'pretrained_white_first' in config['methods']
        assert 'pretrained_colored_first' not in config['methods']
    if name == 'snr_comparison':
        assert config['values'] == [-4, -2, 0, 2, 4, 6]
        assert 'GP_MP' in config['methods']


def test_asset_check_reports_missing_and_changed_bytes(tmp_path, monkeypatch):
    from experiment import assets
    folder = tmp_path/'release'
    folder.mkdir()
    target = tmp_path/'weight.pt'
    target.write_bytes(b'fixture, not a model')
    manifest = dict(scope_notes={'gp-mp': 'test'}, assets=[
        dict(path='weight.pt', scopes=['gp-mp'], sha256=assets.digest(target)),
        dict(path='missing.pt', scopes=['gp-mp'], sha256='0'*64)])
    (folder/'assets.json').write_text(json.dumps(manifest))
    monkeypatch.setattr(assets, 'CONFIGS', tmp_path)
    monkeypatch.setattr(assets, 'repository_path', lambda value: tmp_path/value)
    before = assets.inspect(verify=True)
    assert before['missing'] == 1 and before['hash_mismatches'] == 0
    target.write_bytes(b'changed fixture')
    after = assets.inspect(verify=True)
    assert after['missing'] == 1 and after['hash_mismatches'] == 1
    assert not after['inference_started']
