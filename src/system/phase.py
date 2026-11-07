"""Effective-pilot cross-frame phase conventions."""
import numpy as np


def wrap(angle):
    return (np.asarray(angle) + np.pi) % (2 * np.pi) - np.pi


def phase_operator(pilot, slopes):
    p = np.asarray(pilot, complex)
    slopes = np.asarray(slopes, float)
    if p.ndim != 3 or slopes.shape != (p.shape[1],):
        raise ValueError('Expected pilot[frame,user,input] and one slope per user')
    if not np.isfinite(p).all() or not np.isfinite(slopes).all():
        raise ValueError('Finite pilot and slopes required')
    phase = np.exp(1j * np.arange(len(p))[:, None] * slopes[None])
    return p * phase[:, :, None]
