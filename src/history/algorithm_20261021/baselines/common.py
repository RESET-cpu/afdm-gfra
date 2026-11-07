"""Shared baseline matrix validation."""
import numpy as np


def validate(design, received, noise):
    a, y = np.asarray(design, complex), np.asarray(received, complex)
    if (a.ndim != 2 or y.ndim != 2 or a.shape[0] != y.shape[0] or not a.size or not y.size
            or not np.isfinite(a).all() or not np.isfinite(y).all() or not np.isfinite(noise) or noise <= 0):
        raise ValueError('finite complex MMV observation and positive noise variance required')
    return a, y

