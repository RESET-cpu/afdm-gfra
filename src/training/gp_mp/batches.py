"""White Gaussian batches with the adopted RNG order and DSM arithmetic.

Identity factors retain the checkpoint architecture and numerical operation order.
No correlated-noise sampler or covariance-strength branch is included.
"""
import numpy as np
import torch
from receiver.gp_mp.covariance import Covariance
from receiver.gp_mp.operators import Spectral

def draw_white_arrays(channels, rng, shape_rng, scale, noise):
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
    snr_db = noise['snr_db']
    if len(snr_db) != 2 or not np.all(np.isfinite(snr_db)) or snr_db[0] >= snr_db[1]:
        raise ValueError('Increasing finite SNR endpoints required')

    # Preserve the exact original statements and the uniform -> normal order.
    clean = np.stack((channels.real, channels.imag), axis=1).astype(np.float32) / scale
    levels = np.power(10., -rng.uniform(*snr_db, len(clean)) / 10)
    v = levels.astype(np.float32)
    epsilon = rng.standard_normal(clean.shape).astype(np.float32)

    if noise.get('max_strength', 0.0) != 0.0:
        raise ValueError('GP-MP training requires white Gaussian noise')
    ra = np.broadcast_to(np.eye(16, dtype=np.complex64), (len(clean),16,16)).copy()
    rc = ra.copy()
    sa, sc = ra.copy(), rc.copy()
    transformed = epsilon
    noisy = clean + np.sqrt(v[:, None, None, None, None] / 2) * transformed
    return clean, noisy, v, ra, rc, sa, sc, epsilon

def validate_white_arrays(model, arrays):
    """Host-only checks; no validation is recorded inside CUDA capture."""
    if len(arrays) != 8:
        raise ValueError('Expected eight white-noise batch arrays')
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

def draw_arrays(channels, rng, shape_rng, scale, noise):
    original = draw_white_arrays(channels, rng, shape_rng, scale, noise)
    ea, qa = np.linalg.eigh(original[3].astype(np.complex128))
    ec, qc = np.linalg.eigh(original[4].astype(np.complex128))
    eigenvalues = original[2][:, None, None] / 2 * ea[:, :, None] * ec[:, None, :]
    if not np.all(np.isfinite(eigenvalues) & (eigenvalues > 0)):
        raise ValueError('Positive definite covariance required; no eigenvalue clipping')
    return (*original, qa.astype(np.complex64), qc.astype(np.complex64),
            eigenvalues.astype(np.float32))


def raw_output(model, tensors):
    covariance = Covariance(tensors[2], tensors[3], tensors[4])
    return model.raw(tensors[1], covariance, Spectral(*tensors[8:]))


def loss_from_raw(model, raw, tensors):
    residual = model.stable_residual(raw, tensors[0], tensors[7], Spectral(*tensors[8:]))
    return residual.square().mean()


def mean_from_raw(model, raw, tensors):
    return model.from_raw(raw, tensors[1], Spectral(*tensors[8:]))


def loss_unchecked(model, tensors):
    return loss_from_raw(model, raw_output(model, tensors), tensors)


def validate_arrays(model, arrays):
    if len(arrays) != 11:
        raise ValueError('Expected eight original arrays and three spectral arrays')
    validate_white_arrays(model, arrays[:8])
    qa, qc, eigenvalues = arrays[8:]
    for vectors, matrix in ((qa, arrays[3]), (qc, arrays[4])):
        if vectors.shape != matrix.shape or vectors.dtype != np.complex64:
            raise ValueError('Expected complex64 eigenvectors for each covariance factor')
    expected = (len(arrays[0]), model.config.antennas, model.config.side)
    if eigenvalues.shape != expected or eigenvalues.dtype != np.float32:
        raise ValueError('Expected float32 joint real-covariance eigenvalues')
    if not np.all(np.isfinite(eigenvalues) & (eigenvalues > 0)):
        raise ValueError('Positive finite real-covariance eigenvalues required')


class BatchGraph:
    """Capture forward/backward only; Adam, clipping and EMA remain outside.

    As in the original trainer, final short batches and CPU use eager mode.
    Graph gradient buffers are restored after optimizer.zero_grad(None).
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
