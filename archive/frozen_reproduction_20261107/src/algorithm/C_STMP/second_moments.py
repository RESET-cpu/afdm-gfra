"""C=vI mean and raw second-score trace readout, in complex coordinates."""
import numpy as np
import torch

from algorithm.STMP.moments import MatrixMomentEstimate
from training.colored_preconditioned_20261024.model import load_checkpoint as load_first
from training.colored_second_20261025.model import load_checkpoint as load_second, variance_from_trace
from training.colored_preconditioned_20261024.operators import Spectral
from training.colored_score_20261024.noise import Covariance


class LearnedSecondMoments:
    def __init__(self, first_checkpoint, second_checkpoint, *, first_sha256, device, batch_size):
        if type(batch_size) is not int or batch_size < 1:
            raise ValueError('Positive integer batch size required')
        self.network, blob = load_first(first_checkpoint, device)
        self.second, _ = load_second(second_checkpoint, device, first_sha256=first_sha256)
        self.network.requires_grad_(False)
        self.second.requires_grad_(False)
        self.device, self.batch_size = device, batch_size
        self.noise_support = (10.**(-blob['config']['snr_db_max']/10),
                              10.**(-blob['config']['snr_db_min']/10))
        self.scale_ratio = 1.
        self.samples = self.first_calls = self.second_calls = 0
        self.network_samples = self.second_network_samples = 0
        self.last = {}

    def reset(self):
        self.last = {}

    @torch.inference_mode()
    def infer(self, observation, variance):
        r, v = np.asarray(observation, complex), np.asarray(variance, float)
        if (r.ndim != 4 or r.shape[1:] != (16,16,16) or v.shape != (len(r),)
                or not len(r) or not np.isfinite(r).all() or not np.isfinite(v).all()
                or np.any(v < self.noise_support[0]) or np.any(v > self.noise_support[1])):
            raise ValueError('Finite supported complete channel query required')
        means, variances, traces = [], [], []
        for start in range(0, len(r), self.batch_size):
            stop = min(start+self.batch_size, len(r)); n = stop-start
            x = torch.as_tensor(np.stack((r[start:stop].real, r[start:stop].imag), 1),
                                dtype=torch.float32, device=self.device)
            power = torch.as_tensor(v[start:stop], dtype=x.dtype, device=self.device)
            identity = torch.eye(16, dtype=torch.complex64, device=self.device).expand(n,-1,-1)
            covariance = Covariance(power, identity, identity)
            spectral = Spectral(identity, identity, (power[:,None,None]/2).expand(-1,16,16))
            mean = self.network(x, covariance, spectral)
            u = self.second(x, covariance, spectral)
            # Match the training readout exactly. Pooling/flooring belongs to Denoiser.
            tau = variance_from_trace(u, spectral)
            if u.shape != (n,) or not torch.isfinite(tau).all() or not torch.isfinite(mean).all():
                raise FloatingPointError('Invalid learned moments')
            packed = mean.cpu().numpy().astype(float)
            means.append(packed[:,0]+1j*packed[:,1])
            variances.append(tau.cpu().numpy().astype(float))
            traces.append(u.cpu().numpy().astype(float))
            self.first_calls += 1
            self.second_calls += 1
            self.network_samples += n
            self.second_network_samples += n
        self.samples += len(r)
        result = MatrixMomentEstimate(np.concatenate(means), np.concatenate(variances))
        self.last = dict(raw_variance=result.variance.tolist(), covariance='vI',
                         normalized_trace=np.concatenate(traces).tolist())
        return result
