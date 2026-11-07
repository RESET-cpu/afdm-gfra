"""Evaluate the covariance-conditioned first network on the shared AWGN query."""
import numpy as np
import torch

from training.colored_preconditioned_20261024.model import load_checkpoint
from training.colored_preconditioned_20261024.operators import Spectral
from training.colored_score_20261024.noise import Covariance
from utils import sha256


class PretrainedColoredFirst:
    """The checkpoint returns D(r,C) directly; AWGN supplies C=vI.

    This is only the first-network mean, without receiver variance estimation
    or activity classification. See COLORED_PRECONDITIONED_TRAINING_20261024.md.
    """

    def __init__(self, configuration, checkpoint, checkpoint_sha256, *,
                 epoch=200, device='cpu', batch_size=4):
        if sha256(checkpoint) != checkpoint_sha256:
            raise ValueError('Colored first checkpoint changed')
        self.network, blob = load_checkpoint(checkpoint, device)
        if (blob.get('order') != 1 or blob.get('normalization') != 'population_rms'
                or blob['metadata']['epoch'] != epoch):
            raise ValueError('Expected the selected population-coordinate first network')
        self.scale_ratio = configuration['scale'] / blob['global_complex_rms']
        if not np.isfinite(self.scale_ratio) or self.scale_ratio <= 0 or batch_size < 1:
            raise ValueError('Positive finite coordinate scale and batch size required')
        config = blob['config']
        self.shape = (config['antennas'], config['side'], config['side'])
        self.noise_support = (10.**(-config['snr_db_max']/10)/self.scale_ratio**2,
                              10.**(-config['snr_db_min']/10)/self.scale_ratio**2)
        self.network.requires_grad_(False)
        self.device, self.batch_size = device, batch_size

    @torch.inference_mode()
    def infer(self, query, variance, *, priors):
        query = np.asarray(query, complex)
        if query.ndim != 4 or query.shape[1:] != self.shape or len(query) == 0:
            raise ValueError('Expected complete candidate channel queries')
        variance = np.broadcast_to(np.asarray(variance, float), (len(query),))
        if (not np.isfinite(query).all() or not np.isfinite(variance).all()
                or np.any(variance < self.noise_support[0])
                or np.any(variance > self.noise_support[1])):
            raise ValueError('Finite query and variance within training support required')
        means = []
        for start in range(0, len(query), self.batch_size):
            block = query[start:start+self.batch_size]
            x = torch.as_tensor(self.scale_ratio*np.stack((block.real, block.imag), 1),
                                dtype=torch.float32, device=self.device)
            power = torch.as_tensor(variance[start:start+len(block)]*self.scale_ratio**2,
                                    dtype=x.dtype, device=self.device)
            spatial = torch.eye(self.shape[0], dtype=torch.complex64, device=self.device).expand(len(block), -1, -1)
            delay = torch.eye(self.shape[2], dtype=torch.complex64, device=self.device).expand(len(block), -1, -1)
            covariance = Covariance(power, spatial, delay)
            # C is complex covariance; the packed real covariance is vI/2.
            spectral = Spectral(spatial, delay,
                                (power[:, None, None]/2).expand(-1, self.shape[0], self.shape[2]))
            packed = self.network(x, covariance, spectral).cpu().numpy().astype(float)
            means.append((packed[:, 0]+1j*packed[:, 1])/self.scale_ratio)
        return np.concatenate(means), {}
