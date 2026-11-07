"""Residual DnCNN networks for full complex AFDM channel denoising.

He et al., Sec. III-A / Fig. 3: Conv-ReLU, 18 Conv-BN-ReLU, Conv.
BeamDnCNN uses the checked author initialization and two real channels per
beam. The joint-antenna DnCNN constructor is retained for reproducing prior
training controls. Interval networks share weights across AMP iterations.
"""
import numpy as np
import torch
from torch import nn


class DnCNN(nn.Module):
    def __init__(self, antennas=16, width=64, depth=20):
        super().__init__()
        if depth < 3 or antennas < 1 or width < 1:
            raise ValueError('Invalid DnCNN dimensions')
        self.antennas = antennas
        layers = [nn.Conv2d(2*antennas, width, 3, padding=1), nn.ReLU()]
        for _ in range(depth-2):
            layers.extend([nn.Conv2d(width, width, 3, padding=1, bias=False),
                           nn.BatchNorm2d(width), nn.ReLU()])
        layers.append(nn.Conv2d(width, 2*antennas, 3, padding=1))
        self.noise = nn.Sequential(*layers)

    def forward(self, query):
        return query-self.noise(query)


def pack(channel):
    return np.concatenate((channel.real, channel.imag), axis=1).astype(np.float32)


class FrozenDenoiser:
    def __init__(self, model, *, device='cpu', batch_size=40):
        self.model, self.device, self.batch_size = model.to(device).eval(), device, batch_size
        self.calls = 0

    @torch.inference_mode()
    def __call__(self, query, variance=None):
        self.calls += 1
        parts = []
        for start in range(0, len(query), self.batch_size):
            real = torch.from_numpy(pack(query[start:start+self.batch_size])).to(self.device)
            output = self.model(real).cpu().numpy()
            m = self.model.antennas
            parts.append(output[:, :m]+1j*output[:, m:])
        return np.concatenate(parts).astype(np.complex128)


class FrozenDenoiserBank:
    """Author code denoise.m selects weights using sigma_hat, fixed during MC.

Boundaries here are COMPLEX variances in population-normalized channel units.
Each band's fixed input scaling is a project normalization, not test truth.
"""
    def __init__(self, payload, *, device='cpu', batch_size=40):
        self.boundaries = np.asarray(payload['noise_boundaries'], float)
        self.input_scales = payload['input_scales']
        if len(payload['models']) != len(self.boundaries)-1:
            raise ValueError('Incomplete L-DAMP denoiser bank')
        self.models = []
        for state in payload['models']:
            model = DnCNN(**payload['network'])
            model.load_state_dict(state)
            self.models.append(FrozenDenoiser(model, device=device, batch_size=batch_size))
        self.calls = self.outside_support_calls = 0

    def __call__(self, query, variance):
        index = int(np.clip(np.searchsorted(self.boundaries[1:-1],variance,side='right'),0,len(self.models)-1))
        self.outside_support_calls += int(variance < self.boundaries[0] or variance > self.boundaries[-1])
        self.calls += 1
        scale = self.input_scales[index]
        return scale*self.models[index](query/scale)


class BeamDnCNN(nn.Module):
    def __init__(self, channels=1, width=64, depth=20, epsilon=1e-5):
        super().__init__()
        layers = [nn.Conv2d(channels, width, 3, padding=1), nn.ReLU()]
        for _ in range(depth-2):
            conv = nn.Conv2d(width, width, 3, padding=1)
            conv.bias.requires_grad_(False)
            layers.extend([conv, nn.BatchNorm2d(width, eps=epsilon, momentum=1), nn.ReLU()])
        layers.append(nn.Conv2d(width, channels, 3, padding=1))
        self.noise = nn.Sequential(*layers)
        self.channels = channels
        with torch.no_grad():
            for layer in self.noise:
                if isinstance(layer, nn.Conv2d):
                    layer.weight.normal_(0, np.sqrt(2/(9*width)))
                    layer.bias.zero_()
                elif isinstance(layer, nn.BatchNorm2d):
                    layer.weight.normal_(0, np.sqrt(2/(9*width)))
                    layer.weight.copy_(layer.weight.sign()*layer.weight.abs().clamp_min(.025))
                    layer.bias.zero_()
                    layer.running_mean.zero_()
                    # Author initial saved moments are [0, .01].
                    layer.running_var.fill_(.01**2-layer.eps)

    def forward(self, query):
        return query-self.noise(query)
