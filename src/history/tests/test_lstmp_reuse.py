"""Focused regression tests for the pretrained-backbone integration."""
import copy
from dataclasses import asdict
import torch
import pytest
from experiments.lstmp_candidate_20261019 import backbone, common, receiver, reuse
from afdm_jadcedd.algorithm.proposed.network import DirectCaiConfig, DirectCaiNetwork


def test_reused_backbone_preserves_original_score_and_variance_gradient(monkeypatch):
    torch.set_num_threads(2)
    config=DirectCaiConfig(antennas=2,base_channels=8,snr_db_min=-20)
    monkeypatch.setitem(common.CONFIG,'backbone',dict(kind='direct_cai',config=asdict(config)))
    source=DirectCaiNetwork(config)
    adapted=backbone.make_score()
    adapted.load_state_dict(source.state_dict())
    x=torch.randn(3,2,2,16,16)
    v=torch.tensor([.001,.1,100.],requires_grad=True)
    expected=source(x,v)
    actual=adapted(x,v)
    torch.testing.assert_close(actual,expected,rtol=0,atol=0)
    derivative=torch.autograd.grad(actual.square().mean(),v)[0]
    assert torch.isfinite(derivative).all() and torch.all(derivative!=0)


def test_five_layers_start_equal_but_have_independent_parameters(monkeypatch):
    config=DirectCaiConfig(antennas=16,base_channels=8,snr_db_min=-20)
    monkeypatch.setitem(common.CONFIG,'backbone',dict(kind='direct_cai',config=asdict(config)))
    initial=DirectCaiNetwork(config).state_dict()
    model=receiver.Receiver()
    for _ in range(5):model.add_layer(initial)
    tensors=[dict(layer.score.named_parameters()) for layer in model.layers]
    for name in tensors[0]:
        assert len({row[name].data_ptr() for row in tensors})==5
        assert all(torch.equal(row[name],initial[name]) for row in tensors)
    name=next(iter(tensors[0]))
    with torch.no_grad():tensors[0][name].add_(1)
    assert torch.equal(tensors[1][name],initial[name])
    assert not torch.equal(tensors[0][name],initial[name])


def test_initialization_preserves_source_and_uses_checkpoint_scale(tmp_path,monkeypatch):
    config=DirectCaiConfig(antennas=16,base_channels=8,snr_db_min=-20)
    source=tmp_path/'source.pt'
    torch.save(dict(schema='afdm-cai-direct-score-v1',order=1,normalization='population_rms',
        config=asdict(config),global_complex_rms=.2647966452702405,
        state_dict=DirectCaiNetwork(config).state_dict()),source)
    digest=common.sha(source)
    monkeypatch.setattr(reuse,'OUT',tmp_path/'run')
    monkeypatch.setitem(common.CONFIG,'backbone',dict(kind='direct_cai',config=asdict(config)))
    monkeypatch.setitem(common.CONFIG,'pretrained_score',dict(path=str(source),sha256=digest,global_complex_rms=.2647966452702405))
    monkeypatch.setitem(common.CONFIG,'normalized_training_second_moment',1.0004404181394917)
    target,scale=reuse.prepare_initialization()
    assert scale==.2647966452702405 and common.sha(source)==digest
    assert target!=source
    assert reuse.prepare_initialization()==(target,scale)


def test_gradient_norm_overflow_is_not_confused_with_nonfinite_gradients():
    from experiments.lstmp_candidate_20261019.optimization import clip_gradient_norm
    parameter=torch.nn.Parameter(torch.zeros(2))
    parameter.grad=torch.tensor([3e25,4e25])
    norm=clip_gradient_norm([parameter])
    assert float(norm)==pytest.approx(5e25,rel=1e-6)
    torch.testing.assert_close(parameter.grad,torch.tensor([.6,.8]))
    parameter.grad=torch.tensor([float('inf'),1.])
    with pytest.raises(FloatingPointError):clip_gradient_norm([parameter])
