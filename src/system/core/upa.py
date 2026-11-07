"""Two independent UPA steering implementations.

Directional cosines follow Shen / standard UPA:
mu_z = cos(zenith), mu_y = sin(zenith) * sin(azimuth).
Physical steering is not divided by sqrt(M).
"""

from __future__ import annotations

import numpy as np

from system.core.config import ArrayConfig
from system.core.conventions import DTYPE_C, DTYPE_R


def directional_cosines(zenith_rad: float, azimuth_rad: float) -> tuple[float, float]:
    """mu_z = cos θ^z, mu_y = sin θ^z sin θ^a."""
    mu_z = float(np.cos(zenith_rad))
    mu_y = float(np.sin(zenith_rad) * np.sin(azimuth_rad))
    return mu_z, mu_y


def steering_vector_reference(array: ArrayConfig, mu_z: float, mu_y: float) -> np.ndarray:
    """Explicit column-wise UPA vectorization: m = n_z + M_z n_y."""
    vec = np.empty(array.M, dtype=DTYPE_C)
    for n_y in range(array.M_y):
        for n_z in range(array.M_z):
            m = n_z + array.M_z * n_y
            phase = 2.0 * np.pi * (
                array.d_z_over_lambda * n_z * mu_z + array.d_y_over_lambda * n_y * mu_y
            )
            vec[m] = np.exp(1j * phase)
    return vec


def steering_vector_operator(array: ArrayConfig, mu_z: float, mu_y: float) -> np.ndarray:
    """Kronecker / mesh implementation, independent of the reference loop."""
    n_z = np.arange(array.M_z, dtype=DTYPE_R)
    n_y = np.arange(array.M_y, dtype=DTYPE_R)
    a_z = np.exp(1j * 2.0 * np.pi * array.d_z_over_lambda * n_z * mu_z)
    a_y = np.exp(1j * 2.0 * np.pi * array.d_y_over_lambda * n_y * mu_y)
    return np.kron(a_y, a_z).astype(DTYPE_C)
