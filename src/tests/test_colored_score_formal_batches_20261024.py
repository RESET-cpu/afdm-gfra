"""Bounded CPU checks of the formal colored-batch adapter, without training."""
from copy import deepcopy
from types import SimpleNamespace

import numpy as np
import torch
from torch import nn

from training.scores.score_matching import make_cai_batch
from training.colored_score_20261024.formal_batches import (
    BatchGraph, draw_arrays, loss_from_score, loss_unchecked, posterior_mean)
from training.colored_score_20261024.noise import (
    Covariance, posterior_mean as reference_mean, score_loss)


NOISE = dict(snr_db=(-20, 30), rank=4, max_strength=.5)


def _channels(batch):
    rng = np.random.default_rng(24081)
    shape = (batch, 16, 16, 16)
    return (rng.standard_normal(shape) + 1j*rng.standard_normal(shape)).astype(np.complex64)


class _AffineScore(nn.Module):
    """Small differentiable probe, not a network training run."""
    config = SimpleNamespace(antennas=16, side=16)

    def __init__(self):
        super().__init__()
        self.gain = nn.Parameter(torch.tensor(.07))
        self.bias = nn.Parameter(torch.tensor(-.03))

    def forward(self, observation, covariance):
        condition = covariance.antenna[:, 0, 1].real[:, None, None, None, None]
        return self.gain * observation + self.bias * (1 + condition)


def test_awgn_preserves_original_draw16_batch64_data_and_rng_exactly():
    channels = _channels(67)
    actual_rng, old_rng = np.random.default_rng(24082), np.random.default_rng(24082)
    shape_rng = np.random.default_rng(24083)
    white = dict(NOISE, max_strength=0.)
    for start in range(0, len(channels), 16):
        selected = channels[start:start+16]
        # Reproduce the epsilon independently from the pre-draw state, rather
        # than extracting it by noisy-minus-clean subtraction.
        replay = np.random.default_rng()
        replay.bit_generator.state = deepcopy(actual_rng.bit_generator.state)
        replay.uniform(*NOISE['snr_db'], len(selected))
        epsilon = replay.standard_normal((len(selected), 2, 16, 16, 16)).astype(np.float32)
        arrays = draw_arrays(selected, actual_rng, shape_rng, 1.234, white)
        h, r, variance, labels = make_cai_batch(selected, old_rng, 1.234)
        np.testing.assert_array_equal(arrays[0], h)
        np.testing.assert_array_equal(arrays[1], r)
        np.testing.assert_array_equal(arrays[2], labels)
        np.testing.assert_array_equal(arrays[2], variance[:, 0, 0, 0])
        np.testing.assert_array_equal(arrays[7], epsilon)
        assert actual_rng.bit_generator.state == old_rng.bit_generator.state
        identity = np.broadcast_to(np.eye(16, dtype=np.complex64), arrays[3].shape)
        for matrix in arrays[3:7]:
            np.testing.assert_array_equal(matrix, identity)
        for index in (0, 1, 2, 7):
            assert arrays[index].dtype == np.float32
        assert all(value.dtype == np.complex64 for value in arrays[3:7])


def test_covariance_shape_rng_does_not_change_variance_epsilon_or_main_rng():
    channels = _channels(3)
    seeds = (24084, 24085)
    first = draw_arrays(channels, np.random.default_rng(24086),
                        np.random.default_rng(seeds[0]), 1., NOISE)
    main = np.random.default_rng(24086)
    second = draw_arrays(channels, main, np.random.default_rng(seeds[1]), 1., NOISE)
    old = np.random.default_rng(24086)
    make_cai_batch(channels, old, 1.)
    assert main.bit_generator.state == old.bit_generator.state
    for i in (0, 2, 7):
        np.testing.assert_array_equal(first[i], second[i])
    assert not np.array_equal(first[3], second[3])
    assert not np.array_equal(first[1], second[1])
    for matrix, root in ((first[3], first[5]), (first[4], first[6])):
        np.testing.assert_allclose(root @ root.conj().transpose(0, 2, 1), matrix,
                                   atol=4e-7, rtol=4e-7)
    z = first[7][:, 0] + 1j*first[7][:, 1]
    # Explicit slice multiplication catches an accidental Sc.H on the column
    # side; the sampled factors have nonzero imaginary off-diagonal entries.
    expected = np.empty_like(z)
    for b in range(len(z)):
        for o in range(16):
            expected[b, :, o] = first[5][b] @ z[b, :, o] @ first[6][b].T
    packed = np.stack((expected.real, expected.imag), 1)
    noisy = first[0] + np.sqrt(first[2][:, None, None, None, None]/2)*packed
    np.testing.assert_allclose(first[1], noisy, atol=4e-6, rtol=4e-6)


def test_loss_mean_and_parameter_gradients_match_existing_colored_objective():
    arrays = draw_arrays(_channels(2), np.random.default_rng(24087),
                         np.random.default_rng(24088), 1., dict(NOISE, snr_db=(-4, 4)))
    tensors = tuple(torch.from_numpy(a) for a in arrays)
    model, reference = _AffineScore(), _AffineScore()
    actual = loss_unchecked(model, tensors)
    clean, noisy, v, ra, rc, _, _, _ = tensors
    covariance = Covariance(v, ra, rc)
    torch.testing.assert_close(loss_from_score(model(noisy, covariance), tensors),
                               actual, atol=0, rtol=0)
    expected = score_loss(reference(noisy, covariance), noisy, clean, covariance)
    torch.testing.assert_close(actual, expected, atol=3e-6, rtol=3e-6)
    actual.backward()
    expected.backward()
    for parameter, other in zip(model.parameters(), reference.parameters()):
        assert torch.isfinite(parameter.grad).all()
        torch.testing.assert_close(parameter.grad, other.grad, atol=3e-6, rtol=8e-6)
    score = model(noisy, covariance)
    torch.testing.assert_close(posterior_mean(score, tensors),
                               reference_mean(noisy, score, covariance), atol=0, rtol=0)


def test_cpu_batch_graph_eager_fallback_returns_weighted_loss_and_same_gradients():
    arrays = draw_arrays(_channels(2), np.random.default_rng(24089),
                         np.random.default_rng(24090), 1., dict(NOISE, snr_db=(-4, 4)))
    model, reference = _AffineScore(), _AffineScore()
    graph = BatchGraph(model, batch_size=64)
    model.zero_grad(set_to_none=True)
    weighted = graph.backward(arrays)
    loss = loss_unchecked(reference, tuple(torch.from_numpy(a) for a in arrays))
    loss.backward()
    assert weighted == float(loss.detach())*len(arrays[0])
    assert graph.graph is None
    for parameter, other in zip(model.parameters(), reference.parameters()):
        torch.testing.assert_close(parameter.grad, other.grad, atol=0, rtol=0)
