"""Full-user mean and activity map with complete input directional derivatives."""
from pathlib import Path
import numpy as np
import torch

from afdm_jadcedd.algorithm.baselines.ldamp.representation import Representation
from .network import load_checkpoint


class UnsupportedVariance(ValueError):
    pass


class JointDenoiser:
    def __init__(self, checkpoint, *, activity_prior=.1, device='cpu', batch_size=8):
        self.model, self.metadata = load_checkpoint(Path(checkpoint), device=device)
        self.model.eval().requires_grad_(False)
        recipe = self.metadata['recipe']
        self.scale = float(recipe['scale'])
        self.noise_support = tuple(recipe['noise_support'])
        self.activity_prior = float(activity_prior)
        self.device, self.batch_size = device, batch_size
        self.representation = Representation()
        self.calls = self.direction_evaluations = self.network_batches = 0
        self.probabilities = None
        self.linear_diagonal = None

    @staticmethod
    def _pack(value):
        return np.stack((value.real, value.imag), axis=1).astype(np.float32)

    def linearize(self, query, covariance):
        query = np.asarray(query, complex)
        if query.ndim != 4 or query.shape[1:] != (16, 16, 16):
            raise ValueError('Expected K x 16 x 16 x 16 full-user beam channel')
        k, m, r, n = query.shape
        variance = np.diag(covariance).real.reshape(m, r).mean(axis=1)
        if (not np.isfinite(variance).all() or np.any(variance <= 0)
                or np.any(variance < self.noise_support[0]) or np.any(variance > self.noise_support[1])):
            raise UnsupportedVariance(f'Per-beam complex variance outside {self.noise_support}: {variance.tolist()}')
        if not 0 < self.activity_prior < 1:
            raise ValueError('Public activity prior must be strictly between zero and one')
        packed = self._pack(self.representation.forward(query))
        labels = np.broadcast_to(variance, (k, m)).astype(np.float32).copy()
        prior = float(self.activity_prior)
        chunks, outputs, probabilities = [], [], []
        for start in range(0, k, self.batch_size):
            stop = min(start+self.batch_size, k)
            x = torch.as_tensor(packed[start:stop], device=self.device)
            v = torch.as_tensor(labels[start:stop], device=self.device)
            with torch.no_grad():
                parts = self.model.components(x, v, prior)
            outputs.append(parts['mean'].cpu().numpy())
            probabilities.append(parts['probability'].cpu().numpy())
            chunks.append((start, stop, x, v))
            self.network_batches += 1
        values = np.concatenate(outputs)
        output = values[:, 0]+1j*values[:, 1]
        self.probabilities = np.concatenate(probabilities).reshape(k)
        # Only the direct p*c_skip*I component is evaluated analytically.
        # The full JVP below still contains dp, the CNN, and all fixed transforms.
        q = self.model.sigma_data**2
        skip = q/(q+variance/2)
        self.linear_diagonal = np.broadcast_to(
            self.probabilities[:, None, None, None]*skip[None, :, None, None], query.shape).copy()
        self.calls += 1

        def directions(delta):
            delta = np.asarray(delta, complex)
            if delta.ndim != 5 or delta.shape[1:] != query.shape:
                raise ValueError('Directions must have shape count x query.shape')
            transformed = self.representation.forward(delta)
            derivatives = []
            for direction in transformed:
                direction_packed = self._pack(direction)
                predictions = []
                for start, stop, x, v in chunks:
                    tangent = torch.as_tensor(direction_packed[start:stop], device=self.device)
                    with torch.no_grad():
                        _, value = torch.func.jvp(lambda z: self.model(z, v, prior), (x,), (tangent,))
                    predictions.append(value.detach().cpu().numpy())
                    self.network_batches += 1
                value = np.concatenate(predictions)
                derivatives.append(value[:, 0]+1j*value[:, 1])
                self.direction_evaluations += 1
            return self.representation.inverse(np.stack(derivatives))

        return self.representation.inverse(output), directions

    def __call__(self, query, covariance):
        return self.linearize(query, covariance)[0]
