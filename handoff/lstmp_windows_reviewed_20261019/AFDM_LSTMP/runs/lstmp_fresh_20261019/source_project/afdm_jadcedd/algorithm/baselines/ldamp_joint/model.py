"""Experimental noise-conditioned joint DnCNN inside unchanged matrix D-AMP.

The Conv/BN/ReLU backbone follows DnCNN. Per-beam noise conditioning and
diagonal moment preconditioning are explicit project adaptations; see PLAN.
No physical path coordinates, directions or activity truth enter inference.
"""
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


class JointDnCNN(nn.Module):
    def __init__(self, complex_power, mode="moment_skip", width=64, depth=20):
        super().__init__()
        if mode not in ("moment_skip", "identity_skip"):
            raise ValueError(mode)
        self.mode, self.width, self.depth = mode, width, depth
        power = torch.as_tensor(complex_power, dtype=torch.float32)
        if power.shape != (16,) or not torch.all(power > 0):
            raise ValueError("Sixteen positive training-only complex powers required")
        self.register_buffer("power", power)
        layers = [nn.Conv2d(48, width, 3, padding=1), nn.ReLU()]
        for _ in range(depth-2):
            layers += [nn.Conv2d(width, width, 3, padding=1, bias=False),
                       nn.BatchNorm2d(width), nn.ReLU()]
        layers += [nn.Conv2d(width, 32, 3, padding=1)]
        self.net = nn.Sequential(*layers)
        # Both controls start with the declared analytic skip and zero residual.
        nn.init.zeros_(self.net[-1].weight)
        nn.init.zeros_(self.net[-1].bias)

    def factors(self, variance):
        if variance.ndim != 2 or variance.shape[1] != 16:
            raise ValueError("One public complex variance per user and beam required")
        s, v = self.power[None], variance
        ci = torch.sqrt(2/(s+v))
        risk = s*v/(2*(s+v))
        if self.mode == "moment_skip":
            skip, co = s/(s+v), torch.sqrt(risk)
        else:
            skip, co = torch.ones_like(v), torch.sqrt(v/2)
        duplicate = lambda t: torch.cat([t,t], dim=1)[:,:,None,None]
        return duplicate(ci), duplicate(skip), duplicate(co), duplicate(risk)

    def inputs(self, query, variance):
        ci, skip, co, risk = self.factors(variance)
        noise = torch.log(variance)/4
        noise = noise[:,:,None,None].expand(-1,-1,*query.shape[-2:])
        return torch.cat([ci*query, noise],dim=1), skip, co, risk, ci

    def forward(self, query, variance):
        x, skip, co, _, _ = self.inputs(query, variance)
        return skip*query+co*self.net(x)

    @torch.no_grad()
    def linearize(self, query, variance):
        if self.training:
            raise ValueError("Freeze BN before computing inference derivatives")
        x, skip, co, _, ci = self.inputs(query, variance)
        masks = {}
        for index, layer in enumerate(self.net):
            x = layer(x)
            if isinstance(layer, nn.ReLU):
                masks[index] = x > 0
        result = skip*query+co*x

        @torch.no_grad()
        def directions(delta):
            count, batch = delta.shape[:2]
            hidden = torch.cat([delta*ci[None],
                torch.zeros_like(delta[:,:,:16])],dim=2).flatten(0,1)
            for index, layer in enumerate(self.net):
                if isinstance(layer, nn.Conv2d):
                    hidden = F.conv2d(hidden,layer.weight,None,padding=layer.padding)
                elif isinstance(layer, nn.BatchNorm2d):
                    factor = layer.weight/torch.sqrt(layer.running_var+layer.eps)
                    hidden = hidden*factor[None,:,None,None]
                elif isinstance(layer, nn.ReLU):
                    hidden = (hidden.reshape(count,batch,*hidden.shape[1:])*
                              masks[index][None]).flatten(0,1)
            return skip[None]*delta+co[None]*hidden.reshape_as(delta)
        return result, directions


def pack(value):
    return np.concatenate([value.real,value.imag],axis=-3).astype(np.float32)


def unpack(value):
    return value[..., :16,:,:]+1j*value[...,16:,:,:]
