"""Receiver adapter checks: complex scaling, batching, and raw variance."""
import numpy as np
import pytest
import torch
from torch import nn
from algorithm.C_STMP import second_moments as module


class GaussianMean(nn.Module):
    def forward(self, x, cov, spec):
        return x / (1+cov.variance[:,None,None,None,None])


class GaussianTrace(nn.Module):
    def forward(self, x, cov, spec):
        return -cov.variance / (1+cov.variance)


@pytest.fixture
def moments(monkeypatch):
    monkeypatch.setattr(module, 'load_first', lambda *a: (GaussianMean(),
        {'config': {'snr_db_min': -20, 'snr_db_max': 30}}))
    def second(*args, first_sha256):
        assert first_sha256 == 'bound-first'
        return GaussianTrace(), {}
    monkeypatch.setattr(module, 'load_second', second)
    return module.LearnedSecondMoments('first', 'second', first_sha256='bound-first',
                                      device='cpu', batch_size=2)


def test_complex_gaussian_posterior_and_split_batches(moments):
    rng = np.random.default_rng(7)
    r = rng.normal(size=(3,16,16,16)) + 1j*rng.normal(size=(3,16,16,16))
    v = np.array([.001, 1., 100.])
    result = moments.infer(r, v)
    np.testing.assert_allclose(result.mean, r/(1+v[:,None,None,None]), rtol=3e-7, atol=3e-7)
    np.testing.assert_allclose(result.variance, v/(1+v), rtol=5e-6)
    assert (moments.first_calls, moments.second_calls, moments.samples) == (2,2,3)
    assert moments.network_samples == moments.second_network_samples == 3


def test_negative_variance_is_preserved_for_receiver_pooling(moments):
    class Negative(nn.Module):
        def forward(self, x, cov, spec):
            return torch.full((len(x),), -2., device=x.device)
    moments.second = Negative()
    result = moments.infer(np.zeros((1,16,16,16), complex), np.array([.1]))
    np.testing.assert_allclose(result.variance, [-.1], rtol=1e-6)
    with pytest.raises(ValueError):
        moments.infer(np.zeros((1,16,16,16), complex), np.array([101.]))
