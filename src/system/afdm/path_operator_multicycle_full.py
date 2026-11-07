"""Path B: full-delay matrix operator G = A D Ω(d) Π_ell A^H.

Must not import idaft_direct or the Path A simulator.
"""

from __future__ import annotations

import numpy as np

from system.core.conventions import DTYPE_C, DTYPE_R
from system.core.upa import steering_vector_operator
from system.afdm.closedform_periodic import omega_diag
from system.afdm.config import FoldingScene, FoldingSetup
from system.afdm.types import FoldedDelay, wrap_to_period


def daft_matrix(n: int, c1: float, c2: float) -> np.ndarray:
    output = np.arange(n, dtype=DTYPE_R)[:, None]
    time = np.arange(n, dtype=DTYPE_R)[None, :]
    phase = c2 * output**2 + output * time / n + c1 * time**2
    return (np.exp(-2j * np.pi * phase) / np.sqrt(n)).astype(DTYPE_C)


def cyclic_shift_matrix(n: int, folded_delay_samples: int) -> np.ndarray:
    ident = np.eye(n, dtype=DTYPE_C)
    return np.stack([np.roll(ident[:, col], folded_delay_samples) for col in range(n)], axis=1)


def doppler_diag(n: int, doppler_hz: float, sampling_period_s: float, useful_start: int) -> np.ndarray:
    time = np.arange(n, dtype=DTYPE_R)
    g = useful_start + time
    return np.exp(2j * np.pi * doppler_hz * g * sampling_period_s).astype(DTYPE_C)


def useful_start_sample(q: int, n: int, n_cpp: int) -> int:
    return q * (n + n_cpp) + n_cpp


def full_delay_path_matrix(
    n: int,
    delay: FoldedDelay,
    doppler_hz: float,
    sampling_period_s: float,
    useful_start: int,
    c1: float,
    c2: float,
) -> np.ndarray:
    delay.validate(n)
    ell = delay.folded_delay_samples
    matrix_a = daft_matrix(n, c1, c2)
    omega = np.diag(omega_diag(n, delay.full_delay_samples, c1))
    shift = cyclic_shift_matrix(n, ell)
    doppler = np.diag(doppler_diag(n, doppler_hz, sampling_period_s, useful_start))
    return matrix_a @ doppler @ omega @ shift @ matrix_a.conj().T


def simulate_matrix_full_delay(
    setup: FoldingSetup,
    x_daft: np.ndarray,
    scene: FoldingScene,
) -> np.ndarray:
    setup.validate()
    scene.validate(setup.system)
    n = setup.system.N
    n_cpp = setup.system.N_cpp
    n_frames = setup.system.Q
    n_ant = setup.array.M
    ts = setup.system.sampling_period_s
    x_daft = np.asarray(x_daft, dtype=DTYPE_C).reshape(setup.system.K, n_frames, n)
    y = np.zeros((n_frames, n_ant, n), dtype=DTYPE_C)
    for q in range(n_frames):
        c1 = setup.chirp.c1_of(q, n)
        c2 = float(setup.chirp.c2)
        g_q = useful_start_sample(q, n, n_cpp)
        for user in range(setup.system.K):
            if int(scene.activity[user]) == 0:
                continue
            for path in scene.paths_of(user):
                operator = full_delay_path_matrix(
                    n,
                    path.delay,
                    path.doppler_hz,
                    ts,
                    g_q,
                    c1,
                    c2,
                )
                steering = steering_vector_operator(setup.array, path.mu_z, path.mu_y)
                contribution = DTYPE_C(path.gain_complex) * (operator @ x_daft[user, q])
                y[q] += steering[:, None] * contribution[None, :]
    return y


def require_remainder_matches_delay(delay: FoldedDelay, n: int) -> int:
    delay.validate(n)
    if wrap_to_period(delay.full_delay_samples, n) != delay.folded_delay_samples:
        raise ValueError("folded remainder is inconsistent.")
    return delay.folded_delay_samples
