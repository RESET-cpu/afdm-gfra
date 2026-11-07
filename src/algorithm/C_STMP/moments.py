"""Conditional mean and a finite-difference covariance-trace approximation.

See paper/docs/C_STMP_DERIVATION_20261024.md. The checkpoint returns a mean,
not a score. In this first integrated candidate C=vI is used at inference.
"""
import numpy as np
import torch

from algorithm.STMP.moments import MatrixMomentEstimate
from training.colored_preconditioned_20261024.model import load_checkpoint
from training.colored_preconditioned_20261024.operators import Spectral
from training.colored_score_20261024.noise import Covariance


def trace_variance(mean_function, observation, root_apply, probes, epsilon):
    """Estimate tr(J_D Sigma)/d, d being the number of COMPLEX coordinates.

    probes has shape [P,B,2,...] and E[zz^T]=I in real coordinates.
    The covariance and all model conditions remain fixed inside mean_function.
    This is not an MSE estimator for a general finite neural network.
    """
    if not np.isfinite(epsilon) or epsilon <= 0 or len(probes) < 1:
        raise ValueError('Positive finite epsilon and nonempty probes required')
    d = observation[0].numel() // 2
    estimates = []
    for probe in probes:
        direction = root_apply(probe)
        derivative = (mean_function(observation + epsilon*direction).double()
                      - mean_function(observation - epsilon*direction).double())/(2*epsilon)
        estimates.append((direction.double()*derivative).flatten(1).sum(1)/d)
    return torch.stack(estimates).mean(0)


class ColoredMoments:
    def __init__(self, checkpoint, *, device, batch_size, probes=1,
                 epsilon=.01, seed=2026102407):
        if type(probes) is not int or probes < 1 or batch_size < 1:
            raise ValueError('Positive probe count and batch size required')
        if not np.isfinite(epsilon) or epsilon <= 0:
            raise ValueError('Positive finite finite-difference step required')
        self.network, blob = load_checkpoint(checkpoint, device)
        self.network.requires_grad_(False)
        self.device, self.batch_size = device, batch_size
        self.probes, self.epsilon, self.seed = probes, epsilon, seed
        self.noise_support = (10.**(-blob['config']['snr_db_max']/10),
                              10.**(-blob['config']['snr_db_min']/10))
        self.scale_ratio = 1.
        self.samples = self.first_calls = self.second_calls = 0
        self.network_samples = 0
        self.probe_tensor = None
        self.last = {}

    def reset(self):
        """Use reproducible fixed directions for each new receiver input."""
        self.probe_tensor = None

    @torch.inference_mode()
    def infer(self, observation, variance):
        r, v = np.asarray(observation, complex), np.asarray(variance, float)
        if (r.ndim != 4 or r.shape[1:] != (16,16,16) or v.shape != (len(r),)
                or not np.isfinite(r).all() or not np.isfinite(v).all()
                or np.any(v < self.noise_support[0]) or np.any(v > self.noise_support[1])):
            raise ValueError('Finite supported complete channel query required')
        shape = (self.probes,len(r),2,16,16,16)
        if self.probe_tensor is None or tuple(self.probe_tensor.shape) != shape:
            rng = np.random.default_rng(self.seed)
            self.probe_tensor = torch.as_tensor(2*rng.integers(0,2,shape,dtype=np.int8)-1,
                                               dtype=torch.float32,device=self.device)
        means, variances = [], []
        for start in range(0,len(r),self.batch_size):
            stop = min(start+self.batch_size,len(r)); n = stop-start
            x = torch.as_tensor(np.stack((r[start:stop].real,r[start:stop].imag),1),
                                dtype=torch.float32,device=self.device)
            power = torch.as_tensor(v[start:stop],dtype=x.dtype,device=self.device)
            identity = torch.eye(16,dtype=torch.complex64,device=self.device).expand(n,-1,-1)
            covariance = Covariance(power,identity,identity)
            spectral = Spectral(identity,identity,(power[:,None,None]/2).expand(-1,16,16))
            mean_function = lambda q: self.network(q,covariance,spectral)
            mean = mean_function(x)
            tau = trace_variance(mean_function,x,
                lambda z: spectral.apply(z,spectral.variance_eigenvalues.sqrt()),
                self.probe_tensor[:,start:stop],self.epsilon)
            packed = mean.cpu().numpy().astype(float)
            means.append(packed[:,0]+1j*packed[:,1]); variances.append(tau.cpu().numpy())
            self.first_calls += 1+2*self.probes
            self.network_samples += n*(1+2*self.probes)
        self.samples += len(r)
        result = MatrixMomentEstimate(np.concatenate(means),np.concatenate(variances))
        self.last = dict(raw_variance=result.variance.tolist(),covariance='vI')
        return result

