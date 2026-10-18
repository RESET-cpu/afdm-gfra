"""Per-beam score posterior-mean approximation and complete real directions."""
from pathlib import Path
import numpy as np
import torch

from afdm_jadcedd.algorithm.baselines.ldamp.representation import Representation
from .network import load_checkpoint


class UnsupportedVariance(ValueError):
    pass


class ScoreDenoiser:
    """One shared network, with independent examples for different beams.

    All inputs are already in normalized beam/AFDM coordinates. The fixed
    temporal transform is applied to inputs and directions and inverted on
    outputs. Noise labels are held fixed while taking a partial derivative.
    """
    def __init__(self, checkpoint, *, device='cpu', batch_size=128):
        self.model, self.metadata = load_checkpoint(Path(checkpoint), device=device)
        self.model.eval().requires_grad_(False)
        recipe = self.metadata['recipe']
        self.scale = float(recipe['scale'])
        self.noise_support = tuple(recipe['noise_support'])
        self.activity_probability = float(recipe['activity_probability'])
        self.device, self.batch_size = device, batch_size
        self.representation = Representation()
        self.calls = self.direction_evaluations = self.network_batches = 0
        self.noise_log = []

    @staticmethod
    def _pack(value):
        return np.stack((value.real, value.imag), axis=1).astype(np.float32)

    def linearize(self, query, covariance):
        query = np.asarray(query, complex)
        if query.ndim != 4 or query.shape[1:] != (16, 16, 16):
            raise ValueError('Expected K x 16 x 16 x 16 beam channel')
        k, m, r, n = query.shape
        variance = np.diag(covariance).real.reshape(m, r).mean(axis=1)
        if not np.isfinite(variance).all() or np.any(variance <= 0):
            raise UnsupportedVariance('Noise variance must be finite and positive')
        if np.any(variance < self.noise_support[0]) or np.any(variance > self.noise_support[1]):
            raise UnsupportedVariance(
                f'Per-beam variances [{variance.min():.8g}, {variance.max():.8g}] '
                f'outside trained range {self.noise_support}')
        coefficients = self.representation.forward(query).reshape(k*m, r, n)
        packed = self._pack(coefficients)
        labels = np.broadcast_to(variance, (k, m)).reshape(-1).astype(np.float32)
        chunks, outputs = [], []
        for start in range(0, k*m, self.batch_size):
            stop = min(start+self.batch_size, k*m)
            x = torch.as_tensor(packed[start:stop], device=self.device)
            v = torch.as_tensor(labels[start:stop], device=self.device)
            with torch.no_grad():
                prediction = self.model(x, v)
            outputs.append(prediction.cpu().numpy())
            chunks.append((start, stop, x, v))
            self.network_batches += 1
        values = np.concatenate(outputs)
        output = (values[:, 0]+1j*values[:, 1]).reshape(query.shape)
        self.calls += 1
        self.noise_log.append(variance.tolist())

        def directions(delta):
            delta = np.asarray(delta, complex)
            if delta.ndim != 5 or delta.shape[1:] != query.shape:
                raise ValueError('Directions must have shape count x query.shape')
            transformed = self.representation.forward(delta).reshape(len(delta), k*m, r, n)
            derivatives = []
            for direction in transformed:
                direction_packed = self._pack(direction)
                predictions = []
                for start, stop, x, v in chunks:
                    tangent = torch.as_tensor(direction_packed[start:stop], device=self.device)
                    with torch.no_grad():
                        _, value = torch.func.jvp(lambda z: self.model(z, v), (x,), (tangent,))
                    predictions.append(value.detach().cpu().numpy())
                    self.network_batches += 1
                value = np.concatenate(predictions)
                derivatives.append((value[:, 0]+1j*value[:, 1]).reshape(query.shape))
                self.direction_evaluations += 1
            return self.representation.inverse(np.stack(derivatives))

        return self.representation.inverse(output), directions

    def __call__(self, query, covariance):
        return self.linearize(query, covariance)[0]
