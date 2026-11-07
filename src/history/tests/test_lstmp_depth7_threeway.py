"""Training gate and checkpoint routing checks for the three-method comparison."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import torch

SCRIPT = Path(__file__).resolve().parents[1]/'scripts/evaluate_lstmp_depth7_threeway_20261020.py'
spec = importlib.util.spec_from_file_location('paired_depth7', SCRIPT)
E = importlib.util.module_from_spec(spec); spec.loader.exec_module(E)


def test_depth_five_complete_does_not_allow_seven_evaluation(tmp_path):
    E.write(tmp_path/'COMPLETE.json', dict(status='COMPLETE', protected_assets_preserved={'x': True}))
    for depth, epochs in enumerate(E.SCHEDULE[:5], 1):
        folder = tmp_path/f'checkpoints/depth_{depth}'; folder.mkdir(parents=True)
        (folder/'best.pt').write_bytes(b'checkpoint')
        E.write(folder/'COMPLETE.json', dict(status='COMPLETE', steps=epochs*4800, selected_epoch=1,
            checkpoint_sha256=E.sha(folder/'best.pt')))
    with pytest.raises(FileNotFoundError): E.readiness(tmp_path)
    for depth in (6, 7):
        folder = tmp_path/f'checkpoints/depth_{depth}'; folder.mkdir(parents=True)
        (folder/'best.pt').write_bytes(b'checkpoint')
        E.write(folder/'COMPLETE.json', dict(status='COMPLETE', steps=9600, selected_epoch=1,
            checkpoint_sha256=E.sha(folder/'best.pt')))
    assert E.readiness(tmp_path) == (True, 'READY')
    (tmp_path/'RUNNING.lock').write_text('1')
    assert not E.readiness(tmp_path)[0]
    (tmp_path/'RUNNING.lock').unlink()
    receipt = tmp_path/'checkpoints/depth_7/COMPLETE.json'; value = E.read(receipt); value['steps'] = 4800
    E.write(receipt, value)
    with pytest.raises(ValueError, match='depth 7'): E.readiness(tmp_path)


@pytest.mark.parametrize('method,depth', [('new_seven_layer',7), ('frozen_five_layer',5)])
def test_each_unfolded_method_uses_its_own_checkpoint_and_depth(tmp_path, monkeypatch, method, depth):
    seven, five = tmp_path/'run7', tmp_path/'parent5'; seven.mkdir(); five.mkdir()
    (seven/'new.pt').write_bytes(b'7'); (five/'frozen.pt').write_bytes(b'5')
    loaded = []
    def load(path, **kwargs):
        loaded.append(Path(path)); return dict(depth=depth, state={})
    monkeypatch.setattr(torch, 'load', load)
    class Fake:
        def __init__(self): self.count = 0
        def add_layer(self, state): self.count += 1
        def load_state_dict(self, state): pass
        def cuda(self): return self
        def eval(self): return self
        def __call__(self, public):
            x = torch.tensor([[[[[2.]]],[[[4.]]]], [[[[6.]]],[[[8.]]]]])
            return [(x, torch.tensor([0., 2.]))], [{}]*self.count
    plan = dict(scale=.25, training_run=str(seven), new_checkpoint='new.pt', new_microbatch=100,
                five_layer_binding=dict(run=str(five), checkpoint='frozen.pt'))
    a = E.Adapter(method, plan, None, None, SimpleNamespace(Receiver=Fake))
    assert loaded == [seven/'new.pt' if depth == 7 else five/'frozen.pt']
    arrays, record = a.infer({})
    np.testing.assert_array_equal(arrays['estimate'].ravel(), [.5+1j, 1.5+2j])
    assert a.model.count == record['iterations'] == record['first_score_calls'] == depth
    assert record['first_score_samples'] == 2*depth and record['second_score_calls'] == 0
    assert record['converged'] is None


def test_incomplete_training_cannot_start_a_gpu_comparison(tmp_path, monkeypatch):
    E.write(tmp_path/'PLAN.json', dict(root=str(tmp_path), training_run=str(tmp_path/'train')))
    monkeypatch.setattr(E.C, 'modules', lambda *a: pytest.fail('Receiver modules loaded before training completion'))
    assert E.run_comparison(tmp_path)['evaluation_started'] is False
    assert not (tmp_path/'RUNNING.lock').exists()


def test_report_keeps_three_methods_and_rejects_changed_predictions(tmp_path):
    plan = dict(scene_count=20, cases=[], training_run=str(tmp_path/'train'),
                condition=E.C.CONDITION, limitations='Synthetic reporting fixture only')
    E.write(tmp_path/'train/COMPLETE.json', dict(seconds=200))
    E.write(tmp_path/'train/protocol/DEPTH_EXTENSION.json', dict(inherited_training_seconds=100))
    for method in E.METHODS:
        folder = tmp_path/method; folder.mkdir()
        E.write(folder/'OVERHEAD.json', dict(parameters=10, parameter_bytes=40, state_tensor_bytes=40,
            checkpoint_file_bytes=100, model_load_seconds=1.))
        for i in range(20):
            case = dict(index=i, seed=i+100, input_sha256=f'input{i}')
            if method == E.METHODS[0]: plan['cases'].append(case)
            path = folder/f'{i:03d}.npz'; path.write_bytes(method.encode())
            depth = E.DEPTHS.get(method, 600)
            row = dict(status='COMPLETE', case_index=i, seed=i+100, input_sha256=case['input_sha256'],
                prediction_sha256=E.sha(path), error_energy=1., truth_energy=10., nmse=.1,
                active=2, inactive=38, misses=1, false_alarms=1, aer=.05, total_seconds=2.,
                preparation_seconds=.2, inference_seconds=1.8, peak_allocated_bytes=1024, peak_reserved_bytes=2048,
                iterations=depth, converged=None if depth < 600 else False,
                stopping_reason=f'FIXED_{depth}_LAYERS' if depth < 600 else 'MAX_ITERATIONS',
                first_score_calls=depth, second_score_calls=0 if depth < 600 else 600, classifier_calls=depth)
            E.write(folder/f'{i:03d}.json', row)
    E.write(tmp_path/'PLAN.json', plan)
    result = E.make_report(tmp_path, plan, dict(synthetic_fixture=True))
    assert set(result['methods']) == set(E.METHODS)
    assert result['methods']['new_seven_layer']['fixed_depth_scenes'] == 20
    assert result['methods']['frozen_five_layer']['missed_detection_rate'] == .5
    assert result['methods']['legacy_50000_damping01']['iteration_limit_scenes'] == 20
    assert E.read(tmp_path/'COMPLETE.json')['scene_counts'] == dict.fromkeys(E.METHODS, 20)
    (tmp_path/'new_seven_layer/000.npz').write_bytes(b'changed')
    with pytest.raises(ValueError, match='prediction changed'): E.make_report(tmp_path, plan, {})
