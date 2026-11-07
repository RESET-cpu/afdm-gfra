"""Reuse trained networks; no trainable adapter or covariance clipping.

The first-network wrapper is an algebraic re-expression of its old forward.
The activity features are a matrix extension, exact at C=vI, NOT a claim that
the old classifier learned calibrated evidence for arbitrary colored noise.
"""
from pathlib import Path
import torch
from torch import nn

from project import ROOT
from utils import read_json, sha256
from algorithm.STMP.activity import FrozenEvidence
from algorithm.C_STMP_column_20261025.receiver import Receiver as ColumnReceiver
from training.colored_preconditioned_20261024.model import load_checkpoint
from training.colored_score_20261024.noise import Covariance
from training.column_messages_20261025.interface import column


def old_covariance(u, lam):
    eigenvalues = lam.reciprocal()
    v = eigenvalues.mean(1)
    rc = (u*(eigenvalues/v[:, None])[:, None, :]) @ u.mH
    ra = torch.eye(16, dtype=u.dtype, device=u.device).expand(len(u), -1, -1)
    return Covariance(v, ra, rc)


class FirstAdapter(nn.Module):
    def __init__(self, original):
        super().__init__()
        self.original = original.eval().requires_grad_(False)

    def forward(self, x, z, u, lam):
        backbone = self.original.backbone
        embedding = backbone.condition(old_covariance(u, lam).condition())
        raw = backbone.trunk(x.flatten(1, 2), embedding).reshape_as(x)
        return z + column(raw, u, (.5/(1+lam)).sqrt())


class ActivityAdapter(nn.Module):
    def __init__(self, original):
        super().__init__()
        self.original = original.eval().requires_grad_(False)

    def features(self, x, u, lam, mean):
        # Exact old features at lambda=1/v. For general C, r^H C^-1 r
        # and the corresponding cross/residual energies use the SAME C.
        f = mean.detach() if self.original.config.use_score_mean else torch.zeros_like(mean)
        f_map = column(f, u, (2*lam/(1+lam)).sqrt())
        maps = torch.cat((x.flatten(1, 2), f_map.flatten(1, 2)), 1)
        qr = column(x, u, ((1+lam)/2).sqrt())
        qf = column(f, u, lam.sqrt())
        rx = 2*qr.square().flatten(1).mean(1)
        ff = 2*qf.square().flatten(1).mean(1)
        rf = 2*(qr*qf).flatten(1).mean(1)
        residual = 2*(qr-qf).square().flatten(1).mean(1)
        lv = lam.reciprocal().mean(1).log()/5
        scalar = torch.stack((lv, torch.log1p(rx), torch.log1p(ff),
                             torch.sign(rf)*torch.log1p(abs(rf)), torch.log1p(residual)), 1)
        return maps, scalar

    def forward(self, x, u, lam, mean):
        maps, scalar = self.features(x, u, lam, mean)
        net = self.original
        embedding = net.condition(scalar[:, :1])
        for block, bias in zip(net.blocks, net.biases):
            maps = block(maps)+bias(embedding)[:, :, None, None]
        return net.readout(torch.cat((maps.flatten(1), scalar), 1))[:, 0]


class Receiver(ColumnReceiver):
    def __init__(self, configuration, *, device='cuda', verify=True):
        self.config = read_json(configuration) if isinstance(configuration, (str, Path)) else dict(configuration)
        self.device = device
        c = self.config
        for name in ('first', 'activity'):
            if verify:
                assert sha256(ROOT/c[name+'_checkpoint']) == c[name+'_sha256']
        first, _ = load_checkpoint(ROOT/c['first_checkpoint'], device)
        evidence = FrozenEvidence(ROOT/c['activity_checkpoint'], device=device)
        self.first = FirstAdapter(first).eval().requires_grad_(False)
        self.activity = ActivityAdapter(evidence.network).eval().requires_grad_(False)
        self.last_trace = []

    def infer(self, inputs, *, observer=None):
        arrays, record = super().infer(inputs, observer=observer)
        record.update(candidate='reuse_trained_column_messages_20261025',
                      weights_retrained=False, first_adapter='algebraically_equivalent_old_conditioner',
                      activity_adapter='matrix_features_with_old_weights; scalar_limit_exact',
                      limitation='Old first extrapolates beyond training covariance support. Activity matrix features are an untrained extension, not calibrated colored-noise evidence. Gaussian messages and projected derivative covariance remain approximations.')
        return arrays, record
