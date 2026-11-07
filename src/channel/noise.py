"""Receiver-neutral DAFT observation-noise calibration."""

from __future__ import annotations

import numpy as np

from channel.core.conventions import DTYPE_C
from channel.core.conventions import ConfigError


def _circularly_symmetric_noise(
    shape: tuple[int, ...],
    variance: float,
    rng: np.random.Generator,
) -> np.ndarray:
    scale = np.sqrt(variance / 2.0)
    return np.asarray(
        scale * (rng.standard_normal(shape) + 1j * rng.standard_normal(shape)),
        dtype=DTYPE_C,
    )


def add_daft_observation_noise(
    observation: np.ndarray,
    noise_variance: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Add proper complex Gaussian noise after CPP removal and the DAFT."""

    variance = float(noise_variance)
    if not np.isfinite(variance) or variance <= 0.0:
        raise ConfigError("noise variance must be finite and positive.")
    value = np.asarray(observation, dtype=DTYPE_C)
    return value + _circularly_symmetric_noise(value.shape, variance, rng)


def reference_received_power(reference_signals: np.ndarray) -> float:
    """Return average noiseless power per observation over an ensemble."""

    signals = np.asarray(reference_signals, dtype=DTYPE_C)
    if signals.size == 0:
        raise ConfigError("reference ensemble must contain an observation.")
    if not np.all(np.isfinite(signals)):
        raise ConfigError("reference ensemble must be finite.")
    power = float(np.mean(np.abs(signals) ** 2))
    if power <= 0.0:
        raise ConfigError("reference ensemble must have positive average power.")
    return power


def noise_variance_from_reference_snr(
    reference_power_per_observation: float,
    snr_db: float,
) -> float:
    """Calibrate one fixed noise variance from reference power and target SNR."""

    power = float(reference_power_per_observation)
    target = float(snr_db)
    if not np.isfinite(power) or power <= 0.0:
        raise ConfigError("reference receive power must be finite and positive.")
    if not np.isfinite(target):
        raise ConfigError("target SNR must be finite.")
    variance = float(power / 10.0 ** (target / 10.0))
    if not np.isfinite(variance) or variance <= 0.0:
        raise ConfigError("calibrated noise variance must be finite and positive.")
    return variance


def received_snr_db(signal: np.ndarray, noise_variance: float) -> float:
    """Return realized receive SNR for reporting."""

    variance = float(noise_variance)
    if not np.isfinite(variance) or variance <= 0.0:
        raise ConfigError("receive SNR requires a finite positive noise variance.")
    value = np.asarray(signal, dtype=DTYPE_C)
    if value.size == 0:
        raise ConfigError("receive SNR requires a nonempty noiseless signal.")
    energy = float(np.sum(np.abs(value) ** 2))
    if energy == 0.0:
        return float("-inf")
    return float(10.0 * np.log10(energy / (value.size * variance)))


__all__ = [
    "add_daft_observation_noise",
    "noise_variance_from_reference_snr",
    "received_snr_db",
    "reference_received_power",
]
