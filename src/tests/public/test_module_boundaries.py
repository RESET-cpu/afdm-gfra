"""Scientific layer boundaries and verification of the code actually executed."""
import ast
import json

import numpy as np
import pytest

from workspace import ROOT


@pytest.mark.parametrize('folder,forbidden', [
    ('waveform', ('receiver', 'training', 'experiment', 'plotting')),
    ('channel', ('receiver', 'training', 'experiment', 'plotting')),
    ('scenario', ('receiver', 'training', 'experiment', 'plotting')),
    ('receiver', ('training', 'experiment', 'plotting')),
])
def test_scientific_layers_do_not_import_their_callers(folder, forbidden):
    for path in (ROOT/'src'/folder).rglob('*.py'):
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            names = ([node.module or ''] if isinstance(node, ast.ImportFrom)
                     else [a.name for a in node.names] if isinstance(node, ast.Import) else [])
            assert not any(n.split('.')[0] in forbidden for n in names), path


def test_baseline_verification_detects_changes_in_working_solver(monkeypatch):
    from receiver.baseline import _validation
    original = _validation.sha256
    monkeypatch.setattr(_validation, 'sha256', lambda p:
                        'changed' if str(p).replace('\\', '/').endswith('/receiver/baseline/somp.py')
                        else original(p))
    with pytest.raises(ValueError, match='implementation differs'):
        _validation.verify_current_sources()


def test_baseline_verification_uses_working_dependencies():
    from receiver.baseline import _validation
    _validation.verify_current_sources()
    sources = _validation.inference_sources()
    assert 'src/receiver/baseline/somp.py' in sources
    assert not any(p.startswith(('src/algorithm/', 'src/system/')) for p in sources)


def test_registered_receiver_factories_belong_to_receiver_layer():
    from receiver.registry import load_catalog
    for spec in load_catalog().values():
        assert spec['factory'].startswith('receiver.')
        if 'factory' in spec.get('known_noise', {}):
            assert spec['known_noise']['factory'].startswith('receiver.')


def test_white_training_batch_preserves_awgn_rng_and_rejects_nonwhite_noise():
    from training.gp_mp.batches import draw_arrays
    clean = np.ones((2,16,16,16), dtype=np.complex64)
    noise = dict(snr_db=[-20,30], max_strength=0., rank=4)
    args = lambda: (clean, np.random.default_rng(541), np.random.default_rng(921), 2.)
    batch = draw_arrays(*args(), noise)
    for identity in batch[3:7]:
        np.testing.assert_array_equal(identity, np.broadcast_to(np.eye(16), identity.shape))
    np.testing.assert_array_equal(batch[1], batch[0] + np.sqrt(batch[2][:,None,None,None,None]/2)*batch[7])
    with pytest.raises(ValueError, match='white Gaussian'):
        draw_arrays(*args(), dict(noise, max_strength=.2))


def test_reproduction_training_outputs_do_not_overwrite_adopted_models():
    for name in ('gp_mp_first', 'gp_mp_activity'):
        cfg = json.loads((ROOT/f'src/configs/training/{name}.json').read_text())
        assert cfg['output'].endswith('_reproduction')
        assert cfg['schema'].startswith('white-')
