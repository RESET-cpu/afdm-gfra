"""Executable He et al. author-model reference, separate from the AFDM default.

Sources are pinned under references/ldamp_review_20261014. MatConvNet moments
store [mean, standard deviation INCLUDING epsilon], not a running variance.
"""
import numpy as np
import torch
from torch import nn
from scipy.io import loadmat


class AuthorDnCNN(nn.Module):
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


def load_author_model(path):
    source = loadmat(path, simplify_cells=True)['net']['layers']
    assert source[-1]['type'] == 'loss'
    source = source[:-1]
    model = AuthorDnCNN()
    assert len(source) == len(model.noise)
    with torch.no_grad():
        for saved, layer in zip(source, model.noise, strict=True):
            if saved['type'] == 'conv':
                assert isinstance(layer, nn.Conv2d)
                raw, bias = saved['weights']
                kernel = np.asarray(raw).reshape(3, 3, layer.in_channels, layer.out_channels)
                layer.weight.copy_(torch.from_numpy(kernel.transpose(3, 2, 0, 1).copy()))
                layer.bias.copy_(torch.as_tensor(np.asarray(bias).reshape(-1)))
            elif saved['type'] == 'bnorm':
                assert isinstance(layer, nn.BatchNorm2d)
                gamma, beta, moments = saved['weights']
                layer.eps = float(saved.get('epsilon', 1e-4))
                variance = np.asarray(moments)[:, 1]**2-layer.eps
                if not np.all(variance >= 0):
                    raise ValueError('Author moments incompatible with saved epsilon')
                layer.weight.copy_(torch.from_numpy(gamma))
                layer.bias.copy_(torch.from_numpy(beta))
                layer.running_mean.copy_(torch.from_numpy(moments[:, 0]))
                layer.running_var.copy_(torch.from_numpy(variance))
            else:
                assert saved['type'] == 'relu' and isinstance(layer, nn.ReLU)
    return model.eval(), source


def numpy_author_forward(query, source):
    """Independent NHWC float64 cross-correlation and explicit BN evaluation."""
    value = np.asarray(query, dtype=np.float64).transpose(0, 2, 3, 1)
    for saved in source:
        if saved['type'] == 'conv':
            raw, bias = saved['weights']
            weights = np.asarray(raw, dtype=np.float64).reshape(3, 3, value.shape[-1], -1)
            padded = np.pad(value, ((0, 0), (1, 1), (1, 1), (0, 0)))
            windows = np.lib.stride_tricks.sliding_window_view(padded, (3, 3), axis=(1, 2))
            value = np.einsum('bhwcij,ijco->bhwo', windows, weights, optimize=False)
            value += np.asarray(bias).reshape(1, 1, 1, -1)
        elif saved['type'] == 'bnorm':
            gamma, beta, moments = [np.asarray(x, dtype=np.float64) for x in saved['weights']]
            value = (value-moments[:, 0])/moments[:, 1]*gamma+beta
        else:
            assert saved['type'] == 'relu'
            value = np.maximum(value, 0)
    return np.asarray(query, dtype=np.float64)-value.transpose(0, 3, 1, 2)


def author_channels(rng, count, size=64):
    """channel_gen.m + test.m + LENS.m, with a distinct recorded NumPy RNG.

    Author MATLAB indices are 1..size and sinc is sin(pi*x)/(pi*x).
    Min-max scaling defines this synthetic reference problem only.
    """
    azimuth = rng.uniform(-np.pi/2, np.pi/2, (count, 4))
    elevation = rng.uniform(-np.pi/2, np.pi/2, (count, 4))
    gains = np.concatenate([np.ones((count, 1)), rng.standard_normal((count, 3))], axis=1)
    coordinates = np.arange(1, size+1)
    along_y = np.sinc(coordinates[None, None, :]-12*np.sin(azimuth[:, :, None]))
    along_z = np.sinc(coordinates[None, None, :]-12*np.sin(elevation[:, :, None]))
    channel = np.sqrt(size*size/4)*np.sqrt(20)*np.einsum('bl,bli,blj->bij', gains, along_y, along_z)
    minimum = channel.min(axis=(1, 2), keepdims=True)
    span = channel.max(axis=(1, 2), keepdims=True)-minimum
    assert np.all(span > 0)
    return ((channel-minimum)/span)[:, None].astype(np.float32)


class AuthorBank:
    intervals = [(0, 10), (10, 20), (20, 40), (40, 60), (60, 80),
                 (80, 100), (100, 150), (150, 300), (300, 500), (500, 1000)]

    def __init__(self, directory, device='mps'):
        self.device = device
        self.models = []
        for low, high in self.intervals:
            model, _ = load_author_model(directory/f'DnCNN_20Layer_sigma{low}to{high}-best.mat')
            self.models.append(model.to(device))

    @torch.inference_mode()
    def denoise(self, query, sigma):
        # denoise.m selects the 300..500 endpoint even above 500; its final
        # trained 500..1000 network is present on disk but not called there.
        index = int(np.searchsorted([10, 20, 40, 60, 80, 100, 150, 300], sigma*255, side='left'))
        value = torch.from_numpy(np.asarray(query, np.float32)).to(self.device)
        return self.models[index](value).cpu().numpy().astype(np.float64), index
