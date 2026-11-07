"""Metric, successful-completion gate, and physical-input regression tests."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import torch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/evaluate_lstmp_vs_legacy20.py'
spec = importlib.util.spec_from_file_location('paired20', SCRIPT)
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)


def test_endpoint_probabilities_and_inactive_channel_error_are_retained():
    truth = np.array([1+1j, 0, 2, 0]).reshape(4,1,1,1)
    estimate = np.array([1+1j, 1, 0, 0]).reshape(4,1,1,1)
    result = E.score_arrays(estimate, [1.,1.,0.,0.], truth, [1,0,1,0])
    assert result['error_energy'] == pytest.approx(5)
    assert result['truth_energy'] == pytest.approx(6)
    assert result['nmse'] == pytest.approx(5/6)
    assert result['aer'] == .5
    assert result['misses'] == result['false_alarms'] == 1
    assert result['active_error_energy'] == pytest.approx(4)


def test_failed_outputs_are_not_clipped_or_silently_removed():
    for p in ([1.01,.3], [float('nan'),.3]):
        with pytest.raises(FloatingPointError):
            E.score_arrays(np.ones((2,1)), p, np.ones((2,1)), [1,0])


def test_waits_for_all_training_even_when_depth5_checkpoint_exists(tmp_path):
    (tmp_path/'checkpoints/depth_5').mkdir(parents=True)
    (tmp_path/'checkpoints/depth_5/best.pt').write_bytes(b'partial')
    assert not E.readiness(tmp_path)[0]
    E.write(tmp_path/'COMPLETE.json',dict(status='COMPLETE',protected_assets_preserved={'x':True}))
    (tmp_path/'RUNNING.lock').write_text('123')
    assert E.readiness(tmp_path) == (False,'WAITING_FOR_TRAINING_PROCESS_RELEASE')
    (tmp_path/'RUNNING.lock').unlink()
    for depth,epochs in enumerate((2,2,2,2,4),1):
        folder=tmp_path/'checkpoints'/f'depth_{depth}'
        folder.mkdir(exist_ok=True)
        (folder/'best.pt').write_bytes(f'completed {depth}'.encode())
        E.write(folder/'COMPLETE.json',dict(status='COMPLETE',steps=4800*epochs,
            selected_epoch=1,checkpoint_sha256=E.sha(folder/'best.pt')))
    assert E.readiness(tmp_path) == (True,'READY')
    (tmp_path/'checkpoints/depth_5/best.pt').write_bytes(b'changed')
    with pytest.raises(ValueError,match='changed selected checkpoint'):
        E.readiness(tmp_path)


def test_new_adapter_converts_normalized_real_imaginary_to_physical_complex():
    adapter=E.Adapter.__new__(E.Adapter)
    adapter.method=E.METHODS[0];adapter.scale=.25;adapter.plan={'new_microbatch':100}
    x=torch.tensor([[[[[2.]]],[[[4.]]]],[[[[6.]]],[[[8.]]]]])
    adapter.model=lambda public: ([(x,torch.tensor([0.,float('inf')]))],[])
    arrays,record=adapter.infer({})
    np.testing.assert_array_equal(arrays['estimate'].ravel(),[.5+1j,1.5+2j])
    np.testing.assert_array_equal(arrays['probabilities'],[.5,1.])
    assert record['iterations']==5 and record['converged'] is None
    assert record['first_score_samples']==10 and record['second_score_calls']==0


def test_only_four_public_input_fields_enter_new_preparation():
    from afdm_jadcedd.system.observation import ReceiverInput
    adapter=E.Adapter.__new__(E.Adapter)
    adapter.method=E.METHODS[0];adapter.scale=.25
    captured={}
    def prepare(values,scale,device,**kwargs):
        captured.update(values)
        assert kwargs==dict(phase_mode='known',noise_mode='known')
        return 'prepared',{}
    adapter.data=SimpleNamespace(prepare_public=prepare)
    public=ReceiverInput(np.zeros((16,16,16),complex),np.ones((16,40,16),complex),.3,.1)
    assert adapter.prepare(public)=='prepared'
    assert set(captured)=={'y','a','noise','rho'}
    assert captured['y'] is public.observation and captured['a'] is public.operator


def summary_row(error,energy,reason):
    return dict(status='COMPLETE',error_energy=error,truth_energy=energy,nmse=error/energy,
        active=2,inactive=38,misses=1,false_alarms=1,aer=.05,total_seconds=2.,preparation_seconds=.2,
        inference_seconds=1.8,peak_allocated_bytes=1024,peak_reserved_bytes=2048,
        iterations=600,converged=False,stopping_reason=reason,first_score_calls=600,
        second_score_calls=600,classifier_calls=600)


def test_pooled_and_scene_average_nmse_differ_and_iteration_limit_is_included():
    rows=[summary_row(1.,1.,'CONVERGED'),summary_row(1.,9.,'MAX_ITERATIONS')]
    out=E.summarize(rows)
    assert out['pooled_nmse']==pytest.approx(.2)
    assert out['mean_scene_nmse']==pytest.approx(5/9)
    assert out['aer']==pytest.approx(.05)
    assert out['iteration_limit_scenes']==1 and out['scenes']==2
    rows[1]['status']='FAILED'
    with pytest.raises(ValueError):E.summarize(rows)


def test_report_preserves_all_twenty_paired_rows_and_renders(tmp_path):
    plan=dict(scene_count=20,cases=[],condition=E.CONDITION,phase_mode='known',noise_mode='known',
              training_run=str(tmp_path/'train'),limitations='Synthetic integration fixture, not research data')
    E.write(tmp_path/'train/COMPLETE.json',dict(seconds=3600))
    for method in E.METHODS:
        folder=tmp_path/method;folder.mkdir()
        E.write(folder/'OVERHEAD.json',dict(parameters=10,parameter_bytes=40,state_tensor_bytes=40,
            checkpoint_file_bytes=100,model_load_seconds=1.))
        for i in range(20):
            case=dict(index=i,seed=i+100,input_sha256=f'input_{i}')
            if method==E.METHODS[0]:plan['cases'].append(case)
            prediction=folder/f'{i:03d}.npz';prediction.write_bytes(f'{method}_{i}'.encode())
            row=summary_row(.2 if method==E.METHODS[0] else .3,1.,'MAX_ITERATIONS')
            row.update(case_index=i,seed=case['seed'],input_sha256=case['input_sha256'],
                       prediction_sha256=E.sha(prediction))
            E.write(folder/f'{i:03d}.json',row)
    E.write(tmp_path/'PLAN.json',plan)
    result=E.make_report(tmp_path,plan,{'synthetic_fixture':True})
    assert result['paired_new_minus_legacy']['new_lower_nmse_scenes']==20
    assert E.read(tmp_path/'COMPLETE.json')['scene_counts']==dict.fromkeys(E.METHODS,20)
    from PIL import Image
    with Image.open(tmp_path/'comparison.png') as im:
        assert im.size[0]>1000
    (tmp_path/E.METHODS[0]/'001.npz').write_bytes(b'changed')
    with pytest.raises(ValueError,match='paired input'):E.make_report(tmp_path,plan,{})
