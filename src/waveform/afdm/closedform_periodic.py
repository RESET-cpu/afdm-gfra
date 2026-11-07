"""Path B/C primitive: closed-form chirp-periodic extension.

This module must not import idaft_direct.py. It never evaluates an IDAFT sum.
"""

from __future__ import annotations

import numpy as np

from channel.core.conventions import DTYPE_C
from channel.core.conventions import DTYPE_R
from channel.core.conventions import ConfigError
from waveform.afdm.types import wrap_to_period


def _cis_cycles(cycles: float) -> complex:
    """Independent copy of exp(j 2π x mod 1). Must not import idaft_direct."""
    reduced = DTYPE_R(cycles) - np.floor(DTYPE_R(cycles))
    return DTYPE_C(np.exp(2j * np.pi * reduced))


def closedform_extension_factor(n_logical: int, n: int, c1: float) -> complex:
    """Candidate ρ_q(n) = exp(j 2π c1 (n^2 - <n>_N^2)).

    Derived from the warehouse IDAFT element formula; not an imported authority.
    """
    if n <= 0:
        raise ConfigError("N must be positive.")
    n_bar = wrap_to_period(int(n_logical), n)
    delta = int(n_logical) * int(n_logical) - int(n_bar) * int(n_bar)
    return _cis_cycles(c1 * DTYPE_R(delta))


def extend_useful_sample(s_useful: np.ndarray, n_logical: int, c1: float) -> complex:
    """s[n] ≈ ρ(n) s[<n>_N] using a useful-window vector only."""
    s = np.asarray(s_useful, dtype=DTYPE_C).reshape(-1)
    n = s.size
    n_bar = wrap_to_period(int(n_logical), n)
    return closedform_extension_factor(int(n_logical), n, c1) * s[n_bar]


def omega_factor(full_delay_samples: int, n_sample: int, n: int, c1: float) -> complex:
    """ω_q(d,n) = exp(j 2π c1 ((n-d)^2 - <n-d>_N^2))."""
    source = int(n_sample) - int(full_delay_samples)
    return closedform_extension_factor(source, n, c1)


def omega_diag(n: int, full_delay_samples: int, c1: float) -> np.ndarray:
    """Ω_q(d) = diag(ω_q(d,0),...,ω_q(d,N-1))."""
    diag = np.empty(n, dtype=DTYPE_C)
    for n_sample in range(n):
        diag[n_sample] = omega_factor(full_delay_samples, n_sample, n, c1)
    return diag


def ordinary_cp_sample(s_useful: np.ndarray, n_logical: int) -> complex:
    """Ordinary cyclic prefix copy. Negative-control only; not a CPP."""
    s = np.asarray(s_useful, dtype=DTYPE_C).reshape(-1)
    n = s.size
    n_bar = wrap_to_period(int(n_logical), n)
    return DTYPE_C(s[n_bar])
