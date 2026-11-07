"""Conditional mean on complete channels corrupted by scalar complex AWGN.

Queries and variances use checkpoint-normalized coordinates, as in the existing
channel-denoising experiment. This interface does not read or use channel truth.
"""
import numpy as np
import torch
from project import ROOT
from .configuration import verify
from .model import load_checkpoint
from .covariance import Covariance
from .operators import Spectral


class Denoiser:
    def __init__(self, configuration, *, device='auto', batch_size=4):
        if type(batch_size) is not int or batch_size < 1:
            raise ValueError('A positive integer denoising batch size is required')
        self.configuration, self.checkpoints = verify(configuration)
        self.device = ('cuda' if torch.cuda.is_available() else 'cpu') if device == 'auto' else device
        c = self.configuration
        self.network, blob = load_checkpoint(ROOT / c['first_checkpoint'], self.device)
        self.network.requires_grad_(False)
        self.batch_size = batch_size
        self.noise_support = (10.**(-blob['config']['snr_db_max']/10),
                              10.**(-blob['config']['snr_db_min']/10))

    @torch.inference_mode()
    def infer(self, query, variance, *, priors=None):
        if priors is not None:
            raise ValueError('GP-MP denoising does not accept truth-dependent priors')
        r = np.asarray(query, complex)
        v = np.array(np.broadcast_to(np.asarray(variance, float), (len(r),)), copy=True)
        if (r.ndim != 4 or r.shape[1:] != (16,16,16) or not len(r)
                or not np.isfinite(r).all() or not np.isfinite(v).all()
                or np.any(v < self.noise_support[0]) or np.any(v > self.noise_support[1])):
            raise ValueError('Finite supported complete channel query required')
        means = []
        for start in range(0,len(r),self.batch_size):
            stop = min(start+self.batch_size,len(r)); n = stop-start
            x = torch.as_tensor(np.stack((r[start:stop].real,r[start:stop].imag),1),
                                dtype=torch.float32,device=self.device)
            power = torch.as_tensor(v[start:stop],dtype=x.dtype,device=self.device)
            identity = torch.eye(16,dtype=torch.complex64,device=self.device).expand(n,-1,-1)
            covariance = Covariance(power,identity,identity)
            spectral = Spectral(identity,identity,(power[:,None,None]/2).expand(-1,16,16))
            mean = self.network(x,covariance,spectral)
            packed = mean.cpu().numpy().astype(float)
            means.append(packed[:,0]+1j*packed[:,1])
        return np.concatenate(means), dict(
            method='GP-MP', denoiser_training_noise='white Gaussian', query_covariance='vI',
            checkpoint_sha256=self.checkpoints['first_checkpoint'],
            scale=self.configuration['scale'], truth_used=False,
            coordinates='checkpoint-normalized complex channels',
            first_output='conditional_mean', second_network_loaded=False)
