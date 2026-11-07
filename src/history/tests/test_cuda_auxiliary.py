"""Auxiliary execution preserves query order, guards and classifier features."""
import numpy as np
import pytest
import torch
from afdm_jadcedd.algorithm.proposed.activity import Config, EvidenceNetwork
from afdm_jadcedd.experiment.training.proposed.auxiliary import draw_queries
from afdm_jadcedd.experiment.training.scores.cuda_graph_auxiliary import (
    AuxiliaryGraph, activity_forward, query_parts,
)


@pytest.mark.parametrize('stage,count', [('second',64), ('second',16), ('second',8),
                                         ('activity',32), ('activity',16), ('activity',8)])
def test_original_query_sequence(stage, count):
    rng = np.random.default_rng(17)
    data = (rng.normal(size=(64,16,16,16))+1j*rng.normal(size=(64,16,16,16))).astype(np.complex64)
    chosen = rng.permutation(64)[:count]
    a, b = np.random.default_rng(19), np.random.default_rng(19)
    prior = dict(global_complex_rms=.2647966452702405, noise_support=[.001,100.])
    actual = query_parts(data, chosen, a, prior, dict(microbatch_size=16), stage)
    for offset, part in zip(range(0,count,16), actual):
        batch = draw_queries(data[chosen[offset:offset+16]], b, prior['global_complex_rms'],
            prior['noise_support'], paired=stage == 'activity')
        expected = ((batch['observation'], batch['variance'], batch['clean']) if stage == 'second'
                    else (np.concatenate((batch['positive'],batch['negative'])), np.tile(batch['variance'],2)))
        for x, y in zip(part, expected):
            np.testing.assert_array_equal(x, y)
    assert a.bit_generator.state == b.bit_generator.state


def test_classifier_forward_and_gradients_match():
    torch.manual_seed(73)
    model = EvidenceNetwork(Config(width=8))
    # Nonzero readout checks upstream gradients as well as output-layer gradients.
    torch.nn.init.normal_(model.readout[-1].weight, std=.01)
    r = torch.randn(8,2,16,16,16)
    mean = torch.randn_like(r)
    v = torch.logspace(-3,2,8)
    expected = model(r,v,mean)
    expected.sum().backward()
    grads = [p.grad.clone() for p in model.parameters()]
    model.zero_grad(set_to_none=True)
    actual = activity_forward(model,r,v,mean)
    actual.sum().backward()
    torch.testing.assert_close(actual, expected, rtol=0, atol=0)
    for p,g in zip(model.parameters(),grads):
        torch.testing.assert_close(p.grad, g, rtol=0, atol=0)


def test_host_guard_rejects_invalid_variance():
    from types import SimpleNamespace
    first = SimpleNamespace(config=Config())
    graph = AuxiliaryGraph(None, first, 'second', 64)
    r = np.zeros((16,2,16,16,16), np.float32)
    for bad in (0., -1., np.nan, np.inf):
        v = np.ones(16, np.float32)
        v[3] = bad
        with pytest.raises(ValueError):
            graph.validate([(r,v,r.copy())])
