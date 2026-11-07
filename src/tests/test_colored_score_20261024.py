"""Algebra, statistical sampler checks, and conditioner gradient smoke test."""
import numpy as np
import torch

from networks.score import DirectCaiConfig, DirectCaiNetwork
from training.scores.direct_objectives import direct_first_loss
from training.colored_score_20261024.model import ColoredScore
from training.colored_score_20261024.noise import (
    sample_covariance, corrupt, pack, unpack, score_loss, posterior_mean)


def dense_cov(c, outputs):
    return c.variance[0]*torch.kron(torch.kron(c.antenna[0].contiguous(),
        torch.eye(outputs, dtype=c.antenna.dtype)), c.column[0].contiguous())


def real_cov(c):
    return .5*torch.cat((torch.cat((c.real, -c.imag), 1),
                         torch.cat((c.imag, c.real), 1)), 0)


def test_complex_axis_order_and_real_embedding():
    rng = np.random.default_rng(230)
    c = sample_covariance(rng, 1, 3, 2, dtype=torch.float64)
    x = torch.tensor(rng.standard_normal((1, 2, 3, 2, 2)))
    dense = dense_cov(c, 2)
    torch.testing.assert_close(c.apply_complex(unpack(x)).flatten(), dense@unpack(x).flatten())
    sigma = real_cov(dense)
    torch.testing.assert_close(c.apply_real(x).flatten(), sigma@x.flatten())
    for p in (.5, -.5):
        val, vec = torch.linalg.eigh(sigma)
        expected = ((vec*val.pow(p))@vec.T)@x.flatten()
        torch.testing.assert_close(c.apply_real(x, p).flatten(), expected, atol=1e-12, rtol=1e-11)


def test_awgn_loss_and_mean_reduce_to_frozen_formulas():
    rng = np.random.default_rng(231)
    c = sample_covariance(rng, 3, 2, 2, max_strength=0., dtype=torch.float64)
    clean = torch.tensor(rng.standard_normal((3, 2, 2, 2, 2)))
    noisy = corrupt(clean, c, rng)
    score = torch.tensor(rng.standard_normal(clean.shape))
    v = c.variance[:, None, None, None].expand(3, 2, 2, 2)
    torch.testing.assert_close(score_loss(score, noisy, clean, c),
                                direct_first_loss(score, noisy, clean, v))
    torch.testing.assert_close(posterior_mean(noisy, score, c),
                                noisy + c.variance[:, None, None, None, None]/2*score)


def test_analytic_gaussian_posterior_and_exact_noise_score():
    rng = np.random.default_rng(232)
    c = sample_covariance(rng, 1, 2, 2, dtype=torch.float64)
    clean = torch.zeros(1, 2, 2, 1, 2, dtype=torch.float64)
    noisy = corrupt(clean, c, rng)
    dense = dense_cov(c, 1)
    prior = torch.diag(torch.tensor([.4, .7, 1.1, 2.], dtype=torch.complex128))
    r = unpack(noisy).flatten()
    # Real gradient, expressed as a complex vector: -2(P+C)^(-1)r.
    score = pack((-2*torch.linalg.solve(prior+dense, r)).reshape(1, 2, 1, 2))
    expected = prior@torch.linalg.solve(prior+dense, r)
    torch.testing.assert_close(unpack(posterior_mean(noisy, score, c)).flatten(), expected)
    exact_noise_score = -c.apply_real(noisy-clean, -1.)
    assert score_loss(exact_noise_score, noisy, clean, c).item() < 1e-24


def test_sampler_covariance_pseudocovariance_and_axis_independence():
    rng = np.random.default_rng(233)
    c = sample_covariance(rng, 1, 3, 2, snr_db=(0., 0.), dtype=torch.float64)
    # 60k iid vectors is a sampler check, not a physical-scene experiment.
    n = 60000
    from training.colored_score_20261024.noise import Covariance
    repeated = Covariance(c.variance.expand(n), c.antenna.expand(n, -1, -1),
                          c.column.expand(n, -1, -1))
    z = unpack(corrupt(torch.zeros(n, 2, 3, 2, 2, dtype=torch.float64), repeated, rng)).flatten(1)
    empirical = z.T@z.conj()/n
    pseudo = z.T@z/n
    expected = dense_cov(c, 2)
    assert torch.linalg.norm(empirical-expected)/torch.linalg.norm(expected) < .025
    assert torch.linalg.norm(pseudo)/torch.linalg.norm(expected) < .025
    assert torch.max(torch.abs(z.mean(0))) < .02


def test_single_covariance_family_trace_bounds_and_continuous_strengths():
    c = sample_covariance(np.random.default_rng(234), 1000)
    for r in (c.antenna, c.column):
        torch.testing.assert_close(r.diagonal(dim1=-2, dim2=-1).sum(-1).real,
                                   torch.full((1000,), 16.))
        assert torch.linalg.eigvalsh(r).min() >= .49999
        # No forced identity factors or discrete classes in the default sampler.
        assert ((r-torch.eye(16)).abs().flatten(1).amax(1) > 0).all()
        # Rank-4 PSD term has a nullspace: lambda_min(R)=1-alpha.
        strength = 1-torch.linalg.eigvalsh(r)[:, 0]
        assert strength.min() < .01 and strength.max() > .49
        assert abs(strength.mean().item()-.25) < .02
    assert c.condition().shape == (1000, 1025)


def test_warm_start_and_covariance_condition_gradient():
    torch.manual_seed(235)
    rng = np.random.default_rng(235)
    # Same network implementation at reduced width for a bounded CPU check.
    base = DirectCaiNetwork(DirectCaiConfig(base_channels=8)).eval()
    model = ColoredScore(base).eval()
    clean = torch.tensor(rng.standard_normal((2, 2, 16, 16, 16)), dtype=torch.float32)
    white = sample_covariance(rng, 2, max_strength=0.)
    noisy = corrupt(clean, white, rng)
    with torch.no_grad():
        torch.testing.assert_close(model(noisy, white), base(noisy, white.variance), atol=3e-5, rtol=3e-5)
    c = sample_covariance(rng, 2, snr_db=(0., 0.))
    noisy = corrupt(clean, c, rng)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-5)
    loss = score_loss(model(noisy, c), noisy, clean, c)
    loss.backward()
    grad = model.backbone.condition[0].weight.grad[:, 1:]
    assert torch.isfinite(grad).all() and grad.norm() > 0
    optimizer.step()
    assert torch.isfinite(score_loss(model(noisy, c), noisy, clean, c))


def test_candidate_checkpoint_round_trip(tmp_path):
    from training.colored_score_20261024.run import save_model, load_model
    torch.manual_seed(236)
    model = ColoredScore(DirectCaiNetwork(DirectCaiConfig(base_channels=8))).eval()
    path = tmp_path/'candidate.pt'
    save_model(path, model, {'test_only': True}, 'colored', 0, 'test-base')
    restored, record = load_model(path, 'cpu')
    assert record['base_sha256'] == 'test-base'
    rng = np.random.default_rng(236)
    c = sample_covariance(rng, 1)
    x = torch.tensor(rng.standard_normal((1, 2, 16, 16, 16)), dtype=torch.float32)
    with torch.no_grad():
        torch.testing.assert_close(restored(x, c), model(x, c), rtol=0, atol=0)
