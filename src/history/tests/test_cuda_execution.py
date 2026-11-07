"""Execution batching must preserve the original samples and random noise."""
from copy import deepcopy
import numpy as np
import pytest
import torch
from afdm_jadcedd.experiment.training.scores.cuda_execution import execution_batches
from afdm_jadcedd.experiment.training.scores.trainer import ScoreTrainer


@pytest.mark.parametrize('count', [64, 16, 7])
def test_coalesced_queries_and_rng_are_identical(count):
    rng = np.random.default_rng(117)
    data = (rng.normal(size=(64,16,16,16)) + 1j*rng.normal(size=(64,16,16,16))).astype(np.complex64)
    chosen = rng.permutation(64)[:count]
    recipe = dict(scores=dict(global_complex_rms=.2647966452702405),
        training=dict(architecture=dict(snr_db_min=-20, snr_db_max=30, noise_conditioning='continuous')))
    reference = np.random.default_rng(555)
    candidate = np.random.default_rng(555)
    parts = [ScoreTrainer.make_batch(data[chosen[i:i+16]], reference, recipe) for i in range(0,count,16)]
    expected = [np.concatenate([p[j] for p in parts]) for j in range(4)]
    actual = list(execution_batches(data, chosen, candidate, recipe, ScoreTrainer.make_batch,
                                  draw_size=16, execution_size=64))
    assert len(actual) == 1
    for a, b in zip(actual[0], expected):
        np.testing.assert_array_equal(a, b)
    assert candidate.bit_generator.state == reference.bit_generator.state


@pytest.mark.skipif(not torch.cuda.is_available(), reason='CUDA required')
def test_foreach_ema_matches_scalar_lerp():
    torch.manual_seed(91)
    originals = [torch.randn(s, device='cuda') for s in [(64,32), (64,), (8,8,3,3)]]
    sources = [torch.randn_like(a) for a in originals]
    vectorized = deepcopy(originals)
    for a, b in zip(originals, sources):
        a.lerp_(b, .001)
    torch._foreach_lerp_(vectorized, sources, .001)
    assert all(torch.equal(a,b) for a,b in zip(originals, vectorized))
