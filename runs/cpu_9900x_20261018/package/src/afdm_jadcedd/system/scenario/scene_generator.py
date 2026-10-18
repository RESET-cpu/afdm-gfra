"""Nominal TSL scene generator.

The 30° floor is the satellite service region (elevation ≥ 30°). Each
draw samples one 128 km spot beam contained in that region. The rim
placement (far edge = 30°) is the outer envelope, not every seed.
Not a receiver.
"""

from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
from scipy.optimize import brentq

from afdm_jadcedd.system.core.conventions import DTYPE_C, DTYPE_R, ConfigError
from afdm_jadcedd.system.core.upa import directional_cosines
from afdm_jadcedd.system.afdm.types import FoldedDelay
from afdm_jadcedd.system.config import (
    AZIMUTH_MAX_RAD,
    AZIMUTH_MIN_RAD,
    BEAM_RADIUS_M,
    CARRIER_HZ,
    EARTH_RADIUS_M,
    K,
    LARGE_SCALE_COMPENSATED,
    MIN_ELEVATION_RAD,
    N,
    NTN_TDL_D_FADING,
    NTN_TDL_D_NORMALIZED_DELAYS,
    NTN_TDL_D_POWER_DB,
    NTN_TDL_D_RMS_DELAY_SPREAD_S,
    NU_MAX_HZ,
    ORBIT_ALTITUDE_M,
    P_ACTIVITY,
    RICIAN_K_DB,
    TAU_MAX_S,
    ZENITH_MAX_RAD,
    ZENITH_MIN_RAD,
    PhysicalPath,
    PhysicalScene,
)
from afdm_jadcedd.system.scenario.geometry import C_LIGHT_M_S, integer_delay_samples

if not LARGE_SCALE_COMPENSATED:
    raise ConfigError("Path gains are small-scale only.")

MU_EARTH = 3.986004418e14
N_TDL_PATHS = len(NTN_TDL_D_NORMALIZED_DELAYS)


def _elevation_central_angle(elevation_rad: float) -> float:
    arg = (EARTH_RADIUS_M / (EARTH_RADIUS_M + ORBIT_ALTITUDE_M)) * math.cos(elevation_rad)
    return math.acos(float(np.clip(arg, -1.0, 1.0))) - elevation_rad


def _unit(vector: np.ndarray) -> np.ndarray:
    return vector / np.linalg.norm(vector)


def _rotate_about_z(vector: np.ndarray, azimuth_rad: float) -> np.ndarray:
    cosine = math.cos(azimuth_rad)
    sine = math.sin(azimuth_rad)
    rotation = np.array(
        [[cosine, -sine, 0.0], [sine, cosine, 0.0], [0.0, 0.0, 1.0]],
        dtype=DTYPE_R,
    )
    return rotation @ np.asarray(vector, dtype=DTYPE_R)


def _elevation_from_vectors(ground: np.ndarray, sat: np.ndarray) -> float:
    slant = sat - ground
    sine = float(np.dot(_unit(ground), slant) / np.linalg.norm(slant))
    return math.asin(float(np.clip(sine, -1.0, 1.0)))


def _nadir_beam_center(center_elevation_rad: float) -> tuple[np.ndarray, np.ndarray]:
    """Beam center and north (increasing central angle) at ψ = 0."""
    gamma = _elevation_central_angle(center_elevation_rad)
    center = EARTH_RADIUS_M * np.array(
        [math.sin(gamma), 0.0, math.cos(gamma)],
        dtype=DTYPE_R,
    )
    north = np.array([math.cos(gamma), 0.0, -math.sin(gamma)], dtype=DTYPE_R)
    return center, north


def far_disk_edge_elevation_rad(center_elevation_rad: float) -> float:
    """Elevation at the far edge of the 128 km disk. Independent of ψ at t = 0."""
    sat = np.array([0.0, 0.0, EARTH_RADIUS_M + ORBIT_ALTITUDE_M], dtype=DTYPE_R)
    center, north = _nadir_beam_center(center_elevation_rad)
    far = EARTH_RADIUS_M * _unit(center + BEAM_RADIUS_M * north)
    return _elevation_from_vectors(far, sat)


@lru_cache(maxsize=1)
def outermost_center_elevation_rad() -> float:
    """Lowest legal beam-center elevation: far disk edge = MIN_ELEVATION_RAD.

    This is the outer envelope of a 128 km beam inside the 30° service region,
    not the elevation used on every draw. Solved from altitude / Earth radius /
    beam radius. Not a handwritten constant.
    """

    def residual(center_el: float) -> float:
        return far_disk_edge_elevation_rad(center_el) - MIN_ELEVATION_RAD

    low = MIN_ELEVATION_RAD + 1e-6
    high = 70.0 * math.pi / 180.0
    if residual(low) > 0.0:
        raise ConfigError("far disk edge is already above the minimum elevation.")
    if residual(high) <= 0.0:
        raise ConfigError("could not place the far disk edge at the minimum elevation.")
    return float(brentq(residual, low, high, xtol=1e-14))


def legal_center_central_angle_max() -> float:
    """Max Earth-central angle of a 128 km beam center that stays in the 30° cap."""
    return _elevation_central_angle(outermost_center_elevation_rad())


def sample_beam_central_angle(rng: np.random.Generator) -> float:
    """Area-uniform beam center in the legal cap around nadir, including nadir."""
    gamma_max = legal_center_central_angle_max()
    u = float(rng.random())
    cosine = 1.0 - u * (1.0 - math.cos(gamma_max))
    return math.acos(float(np.clip(cosine, -1.0, 1.0)))


def _closest_ground_in_beam(
    center: np.ndarray,
    east: np.ndarray,
    north: np.ndarray,
) -> np.ndarray:
    """Point in the 128 km disk closest to the satellite (nadir if it lies in-beam)."""
    nadir = np.array([0.0, 0.0, EARTH_RADIUS_M], dtype=DTYPE_R)
    offset = nadir - center
    u_e = float(np.dot(offset, east))
    u_n = float(np.dot(offset, north))
    rho = math.hypot(u_e, u_n)
    if rho <= BEAM_RADIUS_M:
        return nadir
    scale = BEAM_RADIUS_M / rho
    return EARTH_RADIUS_M * _unit(center + (scale * u_e) * east + (scale * u_n) * north)


def _require_support(tau_s: float, doppler_hz: float) -> tuple[float, float]:
    """Nominal geometry must lie in the frozen box. Clip is not a physical support."""
    tau = float(tau_s)
    nu = float(doppler_hz)
    if tau < -1e-15:
        raise ConfigError(
            "differential delay is negative; τ^c must be the closest-point delay."
        )
    tau = max(tau, 0.0)
    if tau > TAU_MAX_S + 1e-15:
        raise ConfigError(f"differential delay {tau} exceeds τ_max={TAU_MAX_S}.")
    if abs(nu) > NU_MAX_HZ + 1e-9:
        raise ConfigError(f"Doppler {nu} exceeds ν_max={NU_MAX_HZ}.")
    return tau, nu


def generate_activity(rng: np.random.Generator, n_users: int = K, *,
                      activity_probability: float = P_ACTIVITY) -> np.ndarray:
    if not np.isfinite(activity_probability) or not 0 <= activity_probability <= 1:
        raise ConfigError("activity probability must lie in [0,1].")
    return (rng.random(n_users) < activity_probability).astype(np.int64)


def _tdl_gain(kind: str, power_db: float, rng: np.random.Generator) -> complex:
    """Small-scale tap only. First tap is Rician with frozen K; others Rayleigh."""
    power = 10.0 ** (float(power_db) / 10.0)
    if kind == "los":
        k_lin = 10.0 ** (RICIAN_K_DB / 10.0)
        los = math.sqrt(k_lin / (k_lin + 1.0)) * np.exp(1j * rng.uniform(0.0, 2.0 * np.pi))
        scatter = math.sqrt(1.0 / (2.0 * (k_lin + 1.0))) * (
            rng.normal() + 1j * rng.normal()
        )
        return DTYPE_C(math.sqrt(power) * (los + scatter))
    if kind == "rayleigh":
        scale = math.sqrt(power / 2.0)
        return DTYPE_C(rng.normal(scale=scale) + 1j * rng.normal(scale=scale))
    raise ConfigError(f"unknown TDL fading {kind!r}.")


def generate_scene(
    rng: np.random.Generator,
    *,
    n_users: int = K,
    activity_probability: float = P_ACTIVITY,
) -> PhysicalScene:
    """Place K users in one 128 km beam inside the 30° service region.

    The service region is all ground points with elevation ≥ 30°. Each draw
    samples one 128 km disk contained in that region: azimuth ψ ~ Unif[0, 2π)
    and Earth-central angle of the beam center area-uniform in [0, γ_max],
    where γ_max is the rim placement (far edge = 30°). Users are area-uniform
    in the disk. Satellite velocity stays +x. Set-2 is an outer bound.
    """
    gamma = sample_beam_central_angle(rng)
    r_sat = np.array([0.0, 0.0, EARTH_RADIUS_M + ORBIT_ALTITUDE_M], dtype=DTYPE_R)
    speed = math.sqrt(MU_EARTH / (EARTH_RADIUS_M + ORBIT_ALTITUDE_M))
    v_sat = np.array([speed, 0.0, 0.0], dtype=DTYPE_R)
    beam_azimuth = float(rng.uniform(0.0, 2.0 * np.pi))
    center = _rotate_about_z(
        EARTH_RADIUS_M * np.array([math.sin(gamma), 0.0, math.cos(gamma)], dtype=DTYPE_R),
        beam_azimuth,
    )
    east = _rotate_about_z(np.array([0.0, 1.0, 0.0], dtype=DTYPE_R), beam_azimuth)
    north = _rotate_about_z(
        np.array([math.cos(gamma), 0.0, -math.sin(gamma)], dtype=DTYPE_R),
        beam_azimuth,
    )
    closest = _closest_ground_in_beam(center, east, north)
    tau_c = float(np.linalg.norm(r_sat - closest) / C_LIGHT_M_S)
    activity = generate_activity(rng, n_users, activity_probability=activity_probability)
    paths: list[PhysicalPath] = []
    for user in range(n_users):
        if int(activity[user]) == 0:
            continue
        radius = BEAM_RADIUS_M * math.sqrt(float(rng.random()))
        theta = float(rng.uniform(0.0, 2.0 * np.pi))
        ground = EARTH_RADIUS_M * _unit(
            center + radius * math.cos(theta) * east + radius * math.sin(theta) * north
        )
        elevation = _elevation_from_vectors(ground, r_sat)
        if elevation < MIN_ELEVATION_RAD - 1e-8:
            raise ConfigError(
                f"user elevation {math.degrees(elevation):.6f} deg is below 30 deg; "
                "the 128 km beam must lie in the service region."
            )
        slant = r_sat - ground
        tau, doppler = _require_support(
            float(np.linalg.norm(slant) / C_LIGHT_M_S - tau_c),
            float(CARRIER_HZ / C_LIGHT_M_S * float(np.dot(v_sat, _unit(slant)))),
        )
        zenith = float(rng.uniform(ZENITH_MIN_RAD, ZENITH_MAX_RAD))
        azimuth = float(rng.uniform(AZIMUTH_MIN_RAD, AZIMUTH_MAX_RAD))
        mu_z, mu_y = directional_cosines(zenith, azimuth)
        for path_id, (norm_delay, power_db, fading) in enumerate(
            zip(NTN_TDL_D_NORMALIZED_DELAYS, NTN_TDL_D_POWER_DB, NTN_TDL_D_FADING, strict=True)
        ):
            delay_s = tau + NTN_TDL_D_RMS_DELAY_SPREAD_S * float(norm_delay)
            if delay_s > TAU_MAX_S + 1e-15:
                raise ConfigError(
                    f"TDL delay {delay_s} exceeds τ_max={TAU_MAX_S}; clip is not allowed."
                )
            paths.append(
                PhysicalPath(
                    user_id=user,
                    path_id=path_id,
                    gain_complex=_tdl_gain(fading, power_db, rng),
                    delay=FoldedDelay.from_full(integer_delay_samples(delay_s), N),
                    doppler_hz=doppler,
                    mu_z=mu_z,
                    mu_y=mu_y,
                )
            )
    return PhysicalScene(activity=activity, paths=tuple(paths))


def generate_scene_from_seed(seed: int, *, n_users: int = K,
                             activity_probability: float = P_ACTIVITY) -> PhysicalScene:
    return generate_scene(np.random.default_rng(seed), n_users=n_users,
                          activity_probability=activity_probability)
