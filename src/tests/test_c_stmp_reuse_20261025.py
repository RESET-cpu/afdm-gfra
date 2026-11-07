"""Checks of trained-weight reuse, not receiver performance assertions."""
import numpy as np
import torch
from project import ROOT
from algorithm.C_STMP_reuse_20261025.receiver import FirstAdapter, ActivityAdapter, old_covariance
from algorithm.STMP.activity import FrozenEvidence
from training.colored_preconditioned_20261024.model import load_checkpoint
from training.colored_preconditioned_20261024.operators import Spectral
from training.column_messages_20261025.interface import column

FIRST = ROOT/'result/channel_denoising/data/colored_preconditioned_50000_matched_20261024/first_best.pt'
ACTIVITY = ROOT/'result/snr_comparison/data/c_stmp_classifier_50000_100epochs_20261025/evidence_best.pt'


def test_trained_first_same_output_for_full_column_covariance():
    torch.set_num_threads(2)
    original, _ = load_checkpoint(FIRST, 'cpu')
    adapter = FirstAdapter(original)
    rng = np.random.default_rng(202610251921)
    g = rng.normal(size=(2,16,16))+1j*rng.normal(size=(2,16,16))
    u = torch.tensor(np.linalg.qr(g)[0], dtype=torch.complex64)
    lam = torch.tensor(np.exp(rng.uniform(-8,3,(2,16))), dtype=torch.float32)
    r = torch.tensor(rng.normal(size=(2,2,16,16,16)), dtype=torch.float32)
    covariance = old_covariance(u,lam)
    spectral = Spectral.from_covariance(covariance)
    with torch.inference_mode():
        direct = original(r,covariance,spectral)
        x = column(r,u,(2*lam/(1+lam)).sqrt())
        z = column(r,u,lam/(1+lam))
        adapted = adapter(x,z,u,lam)
    # Old float32 covariance eigendecomposition itself accumulates error at
    # these deliberately anisotropic C; compare meaningful relative norm.
    relative = float(torch.linalg.vector_norm(direct-adapted)/torch.linalg.vector_norm(direct))
    assert relative < 3e-4, relative
    assert all(not p.requires_grad for p in adapter.parameters())


def test_trained_classifier_exact_scalar_limit_and_matrix_energies():
    torch.set_num_threads(2)
    original = FrozenEvidence(ACTIVITY, device='cpu').network
    adapter = ActivityAdapter(original)
    rng = np.random.default_rng(202610251922)
    r = torch.tensor(rng.normal(size=(3,2,16,16,16)), dtype=torch.float32)
    f = torch.tensor(rng.normal(size=r.shape), dtype=torch.float32)
    v = torch.tensor([.01,1.,100.])
    lam = v.reciprocal()[:,None].expand(-1,16)
    u = torch.eye(16,dtype=torch.complex64).expand(3,-1,-1)
    x = column(r,u,(2*lam/(1+lam)).sqrt())
    old_maps, old_scalar = original.inputs(r,v,f)
    maps, scalar = adapter.features(x,u,lam,f)
    torch.testing.assert_close(maps,old_maps,rtol=2e-6,atol=2e-6)
    torch.testing.assert_close(scalar,old_scalar,rtol=2e-6,atol=2e-6)
    with torch.inference_mode():
        torch.testing.assert_close(adapter(x,u,lam,f), original(r,v,f), rtol=2e-5,atol=2e-5)
    g = rng.normal(size=(3,16,16))+1j*rng.normal(size=(3,16,16))
    u = torch.tensor(np.linalg.qr(g)[0], dtype=torch.complex64)
    lam = torch.tensor(np.exp(rng.uniform(-5,4,(3,16))),dtype=torch.float32)
    x = column(r,u,(2*lam/(1+lam)).sqrt())
    _, scalar = adapter.features(x,u,lam,f)
    rx = 2*(r*column(r,u,lam)).flatten(1).mean(1)
    torch.testing.assert_close(scalar[:,1],torch.log1p(rx),rtol=3e-6,atol=3e-6)
