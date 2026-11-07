"""Frozen GNSS-free delay and angle geometry. Not a scene generator."""

from __future__ import annotations

import math

from channel.core.conventions import ConfigError
from channel.core.upa import directional_cosines
from waveform.afdm.types import FoldedDelay
from channel.config import BANDWIDTH_HZ
from channel.config import D_PHYSICAL_MAX
from channel.config import N
from channel.config import NU_MAX_HZ
from channel.config import TAU_MAX_S
from channel.config import PhysicalPath

C_LIGHT_M_S = 299792458.0


def common_delay_s(closest_ground_range_m: float) -> float:
    """τ^c = d_0 / c. d_0 is the closest ground point in the current beam."""
    range_m = float(closest_ground_range_m)
    if range_m <= 0.0:
        raise ConfigError("closest-point range must be positive.")
    return range_m / C_LIGHT_M_S


def differential_delay_s(propagation_delay_s: float, tau_common_s: float) -> float:
    """τ = τ̃ - τ^c. Negative means τ^c was not the closest-point delay."""
    tau = float(propagation_delay_s) - float(tau_common_s)
    if tau < -1e-15:
        raise ConfigError(
            "differential delay is negative; τ^c must be the closest-point delay, not beam center."
        )
    if tau > TAU_MAX_S + 1e-15:
        raise ConfigError(f"differential delay {tau} exceeds τ_max={TAU_MAX_S}.")
    return max(tau, 0.0)


def integer_delay_samples(delay_s: float) -> int:
    """Quantize τ to the nearest sample. Forward I/O stays on integer d.

    Nonnegative half-up: d = clip(floor(τ B + 1/2), 0, d_max).
    This is Shen-style sampling-grid snap, not a fractional-delay operator.
    """
    samples = float(delay_s) * BANDWIDTH_HZ
    if samples < -1e-15:
        raise ConfigError("delay to quantize must be >= 0.")
    nearest = int(math.floor(samples + 0.5))
    if nearest < 0:
        nearest = 0
    if nearest > D_PHYSICAL_MAX:
        nearest = D_PHYSICAL_MAX
    return nearest


def path_from_geometry(
    *,
    user_id: int,
    path_id: int,
    gain_complex: complex,
    propagation_delay_s: float,
    closest_ground_range_m: float,
    doppler_hz: float,
    zenith_rad: float,
    azimuth_rad: float,
) -> PhysicalPath:
    tau_c = common_delay_s(closest_ground_range_m)
    tau = differential_delay_s(propagation_delay_s, tau_c)
    delay = FoldedDelay.from_full(integer_delay_samples(tau), N)
    mu_z, mu_y = directional_cosines(zenith_rad, azimuth_rad)
    if abs(float(doppler_hz)) > NU_MAX_HZ + 1e-9:
        raise ConfigError(f"Doppler {doppler_hz} exceeds ν_max={NU_MAX_HZ}.")
    return PhysicalPath(
        user_id=user_id,
        path_id=path_id,
        gain_complex=gain_complex,
        delay=delay,
        doppler_hz=float(doppler_hz),
        mu_z=mu_z,
        mu_y=mu_y,
    )
