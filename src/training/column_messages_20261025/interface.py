"""Shared train/inference representation of the SAME Gaussian likelihood.

Lambda=U diag(lam) U^H, j=lam/(1+lam), J=U diag(j) U^H.
x=sqrt(2) J^(1/2) r, z=J r. The reference complex signal variance is one.
No covariance clipping and no truth-dependent input calibration occur here.
"""
from copy import deepcopy
from dataclasses import asdict
import numpy as np
import torch
from torch import nn
from networks.score import DirectCaiConfig, DirectCaiNetwork
from algorithm.STMP.activity import EvidenceNetwork, Config


def pack(z):
    return torch.stack((z.real, z.imag), 1)


def unpack(x):
    return torch.complex(x[:, 0], x[:, 1])


def column(x, u, eigenvalues):
    z = unpack(x)
    modes = torch.einsum('bci,baoc->baoi', u.conj(), z)
    result = torch.einsum('bci,baoi->baoc', u, modes*eigenvalues[:, None, None, :])
    return pack(result)


def condition(u, lam):
    j = lam/(1+lam)
    matrix = (u*j[:, None, :]) @ u.mH
    return torch.cat((lam.mean(1).log()[:, None]/5,
                      matrix.real.flatten(1), matrix.imag.flatten(1)), 1)


def training_query(clean, epsilon, u, lam):
    j = lam/(1+lam)
    x = column(clean, u, (2*j).sqrt()) + column(epsilon, u, (1-j).sqrt())
    z = column(clean, u, j) + column(epsilon, u, (.5*j*(1-j)).sqrt())
    return x, z


def information_query(eta, u, lam):
    # eta is real-packed in physical antenna/output/input coordinates.
    return (column(eta, u, (2/(lam*(1+lam))).sqrt()),
            column(eta, u, (1+lam).reciprocal()))


class First(nn.Module):
    def __init__(self, base):
        super().__init__()
        self.config = base.config
        self.backbone = deepcopy(base.network)
        old = self.backbone.condition[0]
        new = nn.Linear(1+2*self.config.side**2, old.out_features)
        with torch.no_grad():
            new.weight.zero_()
            # log precision has opposite sign to old log noise power.
            new.weight[:, :1].copy_(-old.weight.cpu())
            new.bias.copy_(old.bias.cpu())
        self.backbone.condition[0] = new

    def raw(self, x, u, lam):
        embedding = self.backbone.condition(condition(u, lam))
        shape = x.shape
        return self.backbone.trunk(x.reshape(len(x), -1, shape[-2], shape[-1]), embedding).reshape(shape)

    def from_raw(self, raw, z, u, lam):
        return z + column(raw, u, (.5/(1+lam)).sqrt())

    def forward(self, x, z, u, lam):
        return self.from_raw(self.raw(x, u, lam), z, u, lam)

    def information_mean(self, eta, u, lam):
        x, z = information_query(eta, u, lam)
        return self(x, z, u, lam)

    def dsm_loss(self, raw, clean, epsilon, u, lam):
        # Exact old covariance-weighted DSM, evaluated without large r or C.
        j = lam/(1+lam)
        residual = (column(raw, u, j.sqrt())
                    - column(clean, u, (2*j*(1-j)).sqrt())
                    + column(epsilon, u, j))
        return residual.square().mean()


class Activity(EvidenceNetwork):
    def __init__(self, config=Config()):
        super().__init__(config)
        self.condition[0] = nn.Linear(1+2*config.side**2, 64)

    def forward(self, x, u, lam, mean):
        f = column(mean.detach(), u, (2*lam/(1+lam)).sqrt())
        maps = torch.cat((x.flatten(1, 2), f.flatten(1, 2)), 1)
        xx = x.square().flatten(1).mean(1)
        ff = f.square().flatten(1).mean(1)
        xf = (x*f).flatten(1).mean(1)
        rr = (x-f).square().flatten(1).mean(1)
        scalar = torch.stack((lam.mean(1).log()/5, torch.log1p(xx), torch.log1p(ff),
                              torch.sign(xf)*torch.log1p(abs(xf)), torch.log1p(rr)), 1)
        embedding = self.condition(condition(u, lam))
        for block, bias in zip(self.blocks, self.biases):
            maps = block(maps)+bias(embedding)[:, :, None, None]
        return self.readout(torch.cat((maps.flatten(1), scalar), 1))[:, 0]


def save_weight(path, model, stage, metadata):
    from training.scores.trainer import cpu_state
    payload = dict(schema='column-message-network-v1', stage=stage,
        config=asdict(model.config), state_dict=cpu_state(model), metadata=metadata,
        interface='eta_Lambda_reference_complex_variance_1', training_class_prior=.5)
    temporary = path.with_suffix('.tmp')
    torch.save(payload, temporary); temporary.replace(path)


def load_weight(path, device='cuda'):
    data = torch.load(path, map_location='cpu', weights_only=False)
    if data['schema'] != 'column-message-network-v1':
        raise ValueError('Matching column-message network required')
    if data['stage'] == 'first':
        model = First(DirectCaiNetwork(DirectCaiConfig(**data['config']), order=1))
    else:
        model = Activity(Config(**data['config']))
    model.load_state_dict(data['state_dict'], strict=True)
    return model.to(device).eval().requires_grad_(False), data


def numpy_spectral(precision, device):
    values, vectors = np.linalg.eigh((precision+precision.conj().swapaxes(-1, -2))/2)
    if not np.all(np.isfinite(values) & (values > 0)):
        raise FloatingPointError('Proper full-column likelihood required for this candidate')
    return (torch.as_tensor(vectors.astype(np.complex64), device=device),
            torch.as_tensor(values.astype(np.float32), device=device))


def numpy_information_query(information, precision, device):
    """Double-precision spectral solve before converting bounded tensors to float32.

    This avoids mixing a large information coordinate into a nearly null
    precision direction through float32 eigensystem roundoff.
    """
    lam, u = np.linalg.eigh((precision+precision.conj().swapaxes(-1,-2))/2)
    if not np.all(np.isfinite(lam) & (lam>0)):
        raise FloatingPointError('Positive full-column precision required')
    modal = u.conj().transpose(0,2,1)@information
    x = u@(np.sqrt(2/(lam*(1+lam)))[:,:,None]*modal)
    z = u@(modal/(1+lam)[:,:,None])
    def tensor(a):
        physical = a.reshape(len(a),16,16,16).transpose(0,2,3,1)
        return pack(torch.as_tensor(physical,dtype=torch.complex64,device=device))
    return tensor(x),tensor(z),torch.as_tensor(u,dtype=torch.complex64,device=device),torch.as_tensor(lam,dtype=torch.float32,device=device),u,lam
