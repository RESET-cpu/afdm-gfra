"""Shared numerical types and errors."""

from __future__ import annotations

import numpy as np

DTYPE_C = np.complex128
DTYPE_R = np.float64

EPS_NORM = 1e-15


class ConfigError(ValueError):
    """Illegal configuration."""
