"""Tweedie moments from the configured frozen first- and second-order scores."""

from dataclasses import dataclass
from pathlib import Path
import numpy as np
import torch
from .network import load_direct_checkpoint


@dataclass
class MatrixMomentEstimate:
    mean: np.ndarray
    variance: np.ndarray


def convert_moments(r, variance, first, second, scale_ratio):
    """Scores are real derivatives at r_old=c*r and v_old=c^2*v.

    Complex noise variance v means real-coordinate variance v/2. The second score
    learns the global Hessian trace, so average ALL real and antenna axes.
    """
    v = np.broadcast_to(np.asarray(variance, float), (len(r),))
    c = float(scale_ratio)
    vo = v * c * c
    s1 = first[:, 0] + 1j * first[:, 1]
    mean = r + (vo / (2 * c))[:, None, None, None] * s1
    fraction = 1 + vo / 2 * np.mean(second, axis=(1, 2, 3, 4))
    return MatrixMomentEstimate(mean, v * fraction)


class FullChannelMoments:
    def __init__(self, scale, first_path, second_path, *, device="mps", batch_size=8):
        self.first, a = load_direct_checkpoint(first_path, device)
        self.second, b = load_direct_checkpoint(second_path, device)
        from hashlib import sha256

        if any(c.get('normalization') != 'population_rms' for c in (a, b)):
            raise ValueError('This receiver adapter requires population-RMS scores; unit-power scores need explicit power rescaling')

        first_hash = sha256(Path(first_path).read_bytes()).hexdigest()
        assert a["order"] == 1 and b["order"] == 2
        assert b["metadata"]["first_sha256"] == first_hash
        assert a["global_complex_rms"] == b["global_complex_rms"]
        assert b["metadata"]["objective"] == "direct_cai_global_trace"
        self.archive_scale = float(a["global_complex_rms"])
        self.scale_ratio = scale / self.archive_scale
        self.noise_support = (0.001 / self.scale_ratio**2, 100 / self.scale_ratio**2)
        self.device, self.batch_size = device, batch_size
        self.samples = self.first_calls = self.second_calls = 0
        self.last = {}
        self.parameter_counts = [
            sum(p.numel() for p in net.parameters()) for net in (self.first, self.second)
        ]

    def infer(self, observation, variance):
        r = np.asarray(observation, complex)
        v = np.broadcast_to(np.asarray(variance, float), (len(r),))
        if r.shape[1:] != (16, 16, 16) or np.any(v <= 0):
            raise ValueError("full-channel shape or variance mismatch")
        means, variances = [], []
        with torch.inference_mode():
            for start in range(0, len(r), self.batch_size):
                block = r[start : start + self.batch_size]
                vb = v[start : start + self.batch_size]
                packed = self.scale_ratio * np.stack((block.real, block.imag), axis=1)
                x = torch.tensor(packed, dtype=torch.float32, device=self.device)
                nv = torch.tensor(vb * self.scale_ratio**2, dtype=torch.float32, device=self.device)
                s1 = self.first(x, nv).cpu().numpy().astype(float)
                s2 = self.second(x, nv).cpu().numpy().astype(float)
                moment = convert_moments(block, vb, s1, s2, self.scale_ratio)
                means.append(moment.mean)
                variances.append(moment.variance)
                self.first_calls += 1
                self.second_calls += 1
        self.samples += len(r)
        moment = MatrixMomentEstimate(np.concatenate(means), np.concatenate(variances))
        self.last = dict(
            raw_network_variance=moment.variance.copy(), tweedie_ratio=moment.variance / v
        )
        return moment
