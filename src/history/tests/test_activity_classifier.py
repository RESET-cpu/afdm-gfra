"""Activity-classifier feature packing, query isolation and frozen gradients.
"""
from dataclasses import asdict
from types import SimpleNamespace

import numpy as np
import pytest
import torch
from torch.nn import functional as torch_functional

from afdm_jadcedd.system.observation import ReceiverInput
from afdm_jadcedd.algorithm.proposed import activity as model


@pytest.fixture(scope="module", autouse=True)
def bounded_cpu_threads():
    previous = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(previous)


def small_network(*, use_score_mean=True, antennas=2, side=4, live_head=True):
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(2026100507)
        network = model.EvidenceNetwork(model.Config(
            antennas=antennas, side=side, width=3, use_score_mean=use_score_mean)).double()
        if live_head:
            with torch.no_grad():
                network.readout[-1].weight.copy_(torch.linspace(
                    -.2, .3, network.readout[-1].weight.numel(), dtype=torch.float64)[None])
                network.readout[-1].bias.fill_(.07)
    return network


def packed(value):
    return torch.as_tensor(np.stack((value.real, value.imag), axis=1), dtype=torch.float64)


@pytest.mark.parametrize("use_score_mean", [False, True])
def test_complex_feature_units_and_complete_observation_recovery(use_score_mean):
    antennas, side = 2, 3
    dimension = antennas * side**2
    values = np.arange(1, 2*dimension+1).reshape(2, antennas, side, side)/13
    r = values + 1j*np.flip(values, axis=-1)/3
    f = .3*r + (.2-.1j)
    f[1] = -r[1]  # Exercise the negative signed inner-product feature.
    v = np.array([.2, 3.])
    network = small_network(use_score_mean=use_score_mean, antennas=antennas, side=side)
    maps, scalar = network.inputs(packed(r), torch.from_numpy(v), packed(f))
    used_f = f if use_score_mean else np.zeros_like(f)
    axes = (1, 2, 3)
    r_energy = np.sum(abs(r)**2, axis=axes)/(dimension*v)
    f_energy = np.sum(abs(used_f)**2, axis=axes)/(dimension*v)
    cross = np.sum((r.conj()*used_f).real, axis=axes)/(dimension*v)
    residual = np.sum(abs(r-used_f)**2, axis=axes)/(dimension*v)
    expected = np.column_stack((np.log(v)/5, np.log1p(r_energy), np.log1p(f_energy),
        np.sign(cross)*np.log1p(abs(cross)), np.log1p(residual)))
    np.testing.assert_allclose(scalar.numpy(), expected, rtol=2e-15, atol=2e-15)

    # Recover both v and every complex coordinate from the actual returned features.
    recovered_v = np.exp(5*scalar[:, 0].numpy())
    factor = np.sqrt(2/(1+recovered_v))[:, None, None, None]
    recovered = maps[:, :2*antennas].numpy()/factor
    recovered_r = recovered[:, :antennas]+1j*recovered[:, antennas:]
    np.testing.assert_allclose(recovered_v, v, rtol=2e-15)
    np.testing.assert_allclose(recovered_r, r, rtol=2e-15, atol=2e-15)
    recovered_f = maps[:, 2*antennas:].numpy()/factor
    np.testing.assert_allclose(recovered_f[:, :antennas]+1j*recovered_f[:, antennas:],
                               used_f, rtol=2e-15, atol=2e-15)
    if not use_score_mean:
        np.testing.assert_array_equal(scalar[:, 2:4].numpy(), np.zeros((2, 2)))
        np.testing.assert_array_equal(scalar[:, 1].numpy(), scalar[:, 4].numpy())


def test_both_arms_start_identically_and_raw_arm_ignores_mean_with_live_head():
    raw, augmented = small_network(use_score_mean=False), small_network(use_score_mean=True)
    for key, value in raw.state_dict().items():
        torch.testing.assert_close(value, augmented.state_dict()[key], rtol=0, atol=0)
    r = torch.arange(4*2*2*4*4, dtype=torch.float64).reshape(4, 2, 2, 4, 4)/37
    v = torch.tensor([.01, .4, 2., 50.], dtype=torch.float64)
    first, second = r.flip(0), 11*r-3
    assert torch.count_nonzero(raw.readout[-1].weight) > 0
    torch.testing.assert_close(raw(r, v, first), raw(r, v, second), rtol=0, atol=0)
    zero = torch.zeros_like(first)
    torch.testing.assert_close(raw(r, v, first), augmented(r, v, zero), rtol=0, atol=0)


def test_augmented_arm_really_uses_mean_after_zero_head_is_opened():
    network = small_network(antennas=1, side=4, live_head=False)
    r = torch.ones((2, 2, 1, 4, 4), dtype=torch.float64)
    v = torch.tensor([.5, 2.], dtype=torch.float64)
    zero, nonzero = torch.zeros_like(r), torch.full_like(r, 1.7)
    torch.testing.assert_close(network(r, v, zero), network(r, v, nonzero), rtol=0, atol=0)
    # A deterministic nonzero path from mean energy through the real readout.
    with torch.no_grad():
        for parameter in network.parameters():
            parameter.zero_()
        network.readout[0].weight[0, -3] = 1.
        network.readout[-1].weight[0, 0] = 1.
    result = network(r, v, nonzero)
    expected_energy = nonzero.square().flatten(1).sum(1)/(16*v)
    expected = torch_functional.silu(torch.log1p(expected_energy))
    torch.testing.assert_close(result, expected, rtol=2e-15, atol=2e-15)
    assert bool(torch.all(result > network(r, v, zero)))


@pytest.mark.parametrize("use_score_mean", [False, True])
def test_classifier_gradient_does_not_update_frozen_mean_producer(use_score_mean):
    network = small_network(use_score_mean=use_score_mean, antennas=1)
    r = torch.linspace(-1, 2, 2*2*4*4, dtype=torch.float64).reshape(2, 2, 1, 4, 4)
    r.requires_grad_(True)
    old_score_parameter = torch.nn.Parameter(torch.tensor(.4, dtype=torch.float64))
    mean = old_score_parameter*r + .15
    mean.retain_grad()
    logits = network(r, torch.tensor([.3, 1.1], dtype=torch.float64), mean)
    torch_functional.binary_cross_entropy_with_logits(logits, torch.tensor(
        [0., 1.], dtype=torch.float64)).backward()
    assert old_score_parameter.grad is None and mean.grad is None
    assert r.grad is not None and torch.linalg.vector_norm(r.grad) > 0
    assert any(p.grad is not None and torch.count_nonzero(p.grad) > 0 for p in network.parameters())


@pytest.mark.parametrize("use_score_mean", [False, True])
@pytest.mark.parametrize("training", [False, True])
def test_query_has_no_other_sample_or_batch_order_dependency(use_score_mean, training):
    network = small_network(use_score_mean=use_score_mean).train(training)
    r = torch.linspace(-2, 3, 4*2*2*4*4, dtype=torch.float64).reshape(4, 2, 2, 4, 4)
    f, v = .3*r.flip(-1)-.1, torch.tensor([.02, .5, 3., 90.], dtype=torch.float64)
    with torch.no_grad():
        full = network(r, v, f)
        singleton = network(r[:1], v[:1], f[:1])
        order = torch.tensor([2, 0, 3, 1])
        reordered = network(r[order], v[order], f[order])
        changed_r, changed_f, changed_v = r.clone(), f.clone(), v.clone()
        changed_r[1:] *= 17
        changed_f[1:] -= 9
        changed_v[1:] = torch.tensor([.01, 7., 99.], dtype=torch.float64)
        changed = network(changed_r, changed_v, changed_f)
    torch.testing.assert_close(singleton[0], full[0], rtol=2e-13, atol=2e-13)
    torch.testing.assert_close(reordered, full[order], rtol=2e-13, atol=2e-13)
    torch.testing.assert_close(changed[0], full[0], rtol=2e-13, atol=2e-13)


def test_frozen_inference_uses_training_feature_packing_without_disk_checkpoint(monkeypatch):
    config = model.Config(antennas=1, side=4, width=3, use_score_mean=True)
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(931)
        network = model.EvidenceNetwork(config)
    with torch.no_grad():
        network.readout[-1].weight.fill_(.02)
    blob = dict(schema=model.SCHEMA, config=asdict(config), training_class_prior=.5,
        feature_definition=model.FEATURE_DEFINITION, prior_definition=dict(global_complex_rms=1.7),
        state_dict=network.state_dict(), scale=1.7, prior_mean=np.zeros((1, 4, 4), complex),
        prior_second_moment=16., noise_support=[.001, 100.], first_sha256="0"*64,
        second_sha256="1"*64)
    loads = []

    def memory_load(path, **kwargs):
        loads.append((path, kwargs))
        return blob

    monkeypatch.setattr(model.torch, "load", memory_load)
    evidence = model.FrozenEvidence("synthetic-memory-only.pt", device="cpu")
    captured = []
    handle = evidence.network.register_forward_pre_hook(
        lambda module, args: captured.append(tuple(t.detach().clone() for t in args)))
    r = (np.arange(32).reshape(2, 1, 4, 4)/19)*(1+.3j)
    f, v = .2*r-.04j, np.array([.07, 4.])
    logits = evidence.infer(r, v, f)
    handle.remove()
    expected_args = (packed(r).float(), torch.as_tensor(v, dtype=torch.float32), packed(f).float())
    assert len(loads) == 1 and len(captured) == 1
    for actual, expected in zip(captured[0], expected_args):
        torch.testing.assert_close(actual, expected, rtol=0, atol=0)
    with torch.no_grad():
        expected_logits = network(*expected_args).numpy().astype(float)
    np.testing.assert_array_equal(logits, expected_logits)
    assert not evidence.network.training
    assert all(not parameter.requires_grad for parameter in evidence.network.parameters())

