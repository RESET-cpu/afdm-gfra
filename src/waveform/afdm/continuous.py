"""Continuous-delay wrapped-chirp AFDM path operator (Huang convention)."""
import numpy as np
from waveform.afdm.path_operator_multicycle_full import daft_matrix


def continuous_path_matrix(n, delay_samples, doppler_hz, ts, start, c1, c2):
    """Huang Eq. (5), evaluated by its time-domain wrapped-chirp basis.

    For eta=r-d, w=eta mod N, rho=floor(2*c1*w+s/N), the delayed
    basis is exp(j*2*pi*[c2*s²+c1*eta²+s*w/N-rho*w])/sqrt(N).
    c1*(eta²-w²) implements the generalized CPP, including every wrap.
    At integer d this reduces to the existing A D Omega Pi A^H.
    """
    values = (delay_samples, doppler_hz, ts, start, c1, c2)
    if n <= 0 or not np.isfinite(values).all() or delay_samples < 0 or ts <= 0:
        raise ValueError('finite nonnegative delay and a positive sample rate required')
    order = 2 * n * c1
    if order < 1 or abs(order - round(order)) > 1e-12:
        raise ValueError('Huang folded chirps require positive integer 2*N*c1')
    r = np.arange(n, dtype=float)[:, None]
    s = np.arange(n, dtype=float)[None, :]
    eta = r - float(delay_samples)
    w = np.remainder(eta, n)
    rho = np.floor(2 * c1 * w + s / n)
    phase = c2 * s**2 + c1 * eta**2 + s * w / n - rho * w
    delayed = np.exp(2j * np.pi * phase) / np.sqrt(n)
    doppler = np.exp(2j * np.pi * doppler_hz * ts * (start + r))
    return daft_matrix(n, c1, c2) @ (doppler * delayed)


