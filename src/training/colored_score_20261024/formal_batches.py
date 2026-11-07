"""Colored DSM batches preserving the original variance/epsilon RNG stream.

One call is one original draw (16 samples in the formal recipe). Concatenate
four draws for the original optimizer batch of 64; drawing all 64 at once
would change the ordering of uniform and standard-normal RNG consumption.
Only covariance shapes use ``shape_rng``. Optimizer, clipping and EMA remain
the caller's responsibility.
"""
import numpy as np
import torch

from .noise import Covariance, pack, sample_covariance, unpack


def _principal_root(matrix):
    """CPU Hermitian root of the returned complex64 covariance factors."""
    values, vectors = np.linalg.eigh(matrix.astype(np.complex128))
    if not np.all(np.isfinite(values) & (values > 0)):
        raise ValueError('Positive definite covariance required; no eigenvalue clipping')
    root = (vectors * np.sqrt(values)[:, None, :]) @ vectors.conj().transpose(0, 2, 1)
    return root.astype(np.complex64)


def draw_arrays(channels, rng, shape_rng, scale, noise):
    """Return clean, noisy, v, Ra, Rc, Sa, Sc, epsilon as NumPy arrays.

    The first RNG has exactly the draw order and float64-to-float32 casts of
    ``make_cai_batch``. Epsilon is retained directly, never reconstructed by
    subtracting nearly equal noisy and clean observations.
    """
    channels = np.asarray(channels)
    if channels.ndim != 4 or channels.shape[1:] != (16, 16, 16):
        raise ValueError('Expected physical channels [B,16,16,16]')
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError('Positive fixed population RMS required')
    if rng is shape_rng:
        raise ValueError('Covariance shapes require a separate RNG')
    snr_db = noise['snr_db']
    if len(snr_db) != 2 or not np.all(np.isfinite(snr_db)) or snr_db[0] >= snr_db[1]:
        raise ValueError('Increasing finite SNR endpoints required')

    # Preserve the exact original statements and the uniform -> normal order.
    clean = np.stack((channels.real, channels.imag), axis=1).astype(np.float32) / scale
    levels = np.power(10., -rng.uniform(*snr_db, len(clean)) / 10)
    v = levels.astype(np.float32)
    epsilon = rng.standard_normal(clean.shape).astype(np.float32)

    covariance = sample_covariance(
        shape_rng, len(clean), 16, 16, snr_db=(0., 0.),
        max_strength=noise['max_strength'], rank=noise['rank'])
    ra, rc = covariance.antenna.numpy(), covariance.column.numpy()
    if noise['max_strength'] == 0:
        # This branch gives bit-for-bit AWGN observations, not merely an
        # identity-matmul approximation to the original NumPy expression.
        sa, sc = ra.copy(), rc.copy()
        transformed = epsilon
    else:
        sa, sc = _principal_root(ra), _principal_root(rc)
        z = epsilon[:, 0] + 1j * epsilon[:, 1]
        # Per output slice: Sa @ z @ Sc.T, not Sc.conj().T.
        colored = np.einsum('baj,bjok,bik->baoi', sa, z, sc, optimize=True)
        transformed = np.stack((colored.real, colored.imag), axis=1)
    noisy = clean + np.sqrt(v[:, None, None, None, None] / 2) * transformed
    return clean, noisy, v, ra, rc, sa, sc, epsilon


def loss_from_score(score, tensors):
    """Evaluate epsilon DSM using an already computed real-packed score.

    No eigendecomposition or data-dependent GPU boolean occurs here, so the
    forward/backward operations can be captured in a CUDA graph.
    """
    _, _, v, _, _, sa, sc, epsilon = tensors
    transformed = torch.einsum('baj,bjok,bik->baoi', sa, unpack(score), sc)
    residual = (v[:, None, None, None, None] / 2).sqrt() * pack(transformed) + epsilon
    return residual.square().mean()


def loss_unchecked(model, tensors):
    """Compute the model score and the unchanged epsilon DSM objective."""
    _, noisy, v, ra, rc, _, _, _ = tensors
    score = model(noisy, Covariance(v, ra, rc))
    return loss_from_score(score, tensors)


def posterior_mean(score, tensors):
    """Tweedie mean for a supplied real-packed score and exact covariance."""
    _, noisy, v, ra, rc, _, _, _ = tensors
    return noisy + Covariance(v, ra, rc).apply_real(score)


def validate_arrays(model, arrays):
    """Host-only checks; no validation is recorded inside CUDA capture."""
    if len(arrays) != 8:
        raise ValueError('Expected eight colored batch arrays')
    clean, noisy, v, ra, rc, sa, sc, epsilon = arrays
    expected = (len(clean), 2, model.config.antennas, model.config.side, model.config.side)
    for value in (clean, noisy, epsilon):
        if value.shape != expected or value.dtype != np.float32:
            raise ValueError('Expected float32 real-packed channel batches')
    if v.shape != (len(clean),) or v.dtype != np.float32:
        raise ValueError('Expected one float32 complex variance per sample')
    if not len(clean) or not np.all(np.isfinite(v) & (v > 0)):
        raise ValueError('Nonempty batch and positive finite variances required')
    for value, size in ((ra, model.config.antennas), (sa, model.config.antennas),
                        (rc, model.config.side), (sc, model.config.side)):
        if value.shape != (len(clean), size, size) or value.dtype != np.complex64:
            raise ValueError('Expected complex64 axis covariance/root batches')


class BatchGraph:
    """Capture one complete batch's forward/backward, following FirstGraph.

    A short final batch, ``use_graph=False``, or a CPU model uses eager mode.
    Call optimizer.zero_grad(set_to_none=True) before backward and perform
    clipping, optimizer.step and EMA outside this object. The return value is
    the batch mean loss multiplied by the actual number of samples.
    """
    def __init__(self, model, batch_size=64):
        self.model, self.batch_size = model, batch_size
        self.device = next(model.parameters()).device
        self.graph = None

    def backward(self, arrays, *, use_graph=True):
        validate_arrays(self.model, arrays)
        if (not use_graph or len(arrays[0]) != self.batch_size
                or self.device.type != 'cuda'):
            tensors = [torch.as_tensor(a, device=self.device) for a in arrays]
            loss = loss_unchecked(self.model, tensors)
            loss.backward()
        else:
            if self.graph is None:
                self.inputs = [torch.as_tensor(a, device=self.device).clone() for a in arrays]
                stream = torch.cuda.Stream(device=self.device)
                stream.wait_stream(torch.cuda.current_stream(self.device))
                with torch.cuda.stream(stream):
                    for _ in range(3):
                        self.model.zero_grad(set_to_none=True)
                        loss_unchecked(self.model, self.inputs).backward()
                torch.cuda.current_stream(self.device).wait_stream(stream)
                self.model.zero_grad(set_to_none=True)
                self.graph = torch.cuda.CUDAGraph()
                with torch.cuda.graph(self.graph, stream=stream):
                    self.loss = loss_unchecked(self.model, self.inputs)
                    self.loss.backward()
                self.gradients = [p.grad for p in self.model.parameters()]
            for destination, source in zip(self.inputs, arrays):
                destination.copy_(torch.from_numpy(source))
            self.graph.replay()
            for parameter, gradient in zip(self.model.parameters(), self.gradients):
                parameter.grad = gradient
            loss = self.loss
        value = float(loss.detach().cpu())
        if not np.isfinite(value):
            raise FloatingPointError('Nonfinite DSM loss; saved checkpoint preserved')
        return value * len(arrays[0])
