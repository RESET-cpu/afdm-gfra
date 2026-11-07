"""GNSS-Free AFDM physical constants and channel geometry.

Frame count is supplied by the pilot-only experiment configuration.
"""


from __future__ import annotations


from dataclasses import dataclass


import numpy as np


from system.core.config import ArrayConfig


from system.core.conventions import DTYPE_C, ConfigError


from system.afdm.config import FoldingChirp, FoldingSetup, FoldingSystemConfig, siso_array, upa2x2, upa4x4


from system.afdm.types import FoldedDelay


N = 16


DELTA_F_HZ = 30000.0


BANDWIDTH_HZ = float(N) * DELTA_F_HZ


TAU_MAX_S = 699.0e-6


NU_MAX_HZ = 41000.0


N_CPP = int(np.ceil(TAU_MAX_S * BANDWIDTH_HZ))


D_PHYSICAL_MAX = int(np.floor(TAU_MAX_S * BANDWIDTH_HZ))


SLOPE = 7


C1 = 7.0 / 32.0


C2 = 1.0 / 320.0


K = 40


P_ACTIVITY = 0.1


M_Z = 4


M_Y = 4


M = M_Z * M_Y


E_TX_DEFAULT = float(N)


XI_CPP = 1.0 + N_CPP / N


CARRIER_HZ = 2.0e9


EARTH_RADIUS_M = 6371000.0


ORBIT_ALTITUDE_M = 600000.0


BEAM_RADIUS_M = 128000.0


MIN_ELEVATION_RAD = (
    30.0 * np.pi / 180.0
)  # service-region floor; 128 km beam stays inside


ZENITH_MIN_RAD = -0.5 * np.pi


ZENITH_MAX_RAD = 0.5 * np.pi


AZIMUTH_MIN_RAD = 0.0


AZIMUTH_MAX_RAD = 2.0 * np.pi


RICIAN_K_DB = 11.707


LARGE_SCALE_COMPENSATED = True


NTN_TDL_D_RMS_DELAY_SPREAD_S = 30.0e-9


NTN_TDL_D_NORMALIZED_DELAYS = (0.0, 0.0, 0.5596, 7.3340)


NTN_TDL_D_POWER_DB = (-0.284, -11.991, -9.887, -16.771)


NTN_TDL_D_FADING = ("los", "rayleigh", "rayleigh", "rayleigh")


SNR_RX_DEFAULT_DB = 0.0


def resolve_array(n_antennas: str):
    """Resolve one array supported by the AFDM physical link."""
    if n_antennas in ("upa4", "upa"):
        return upa4x4()
    if n_antennas == "upa2":
        return upa2x2()
    if n_antennas == "siso":
        return siso_array()
    raise ConfigError(
        f"n_antennas={n_antennas!r} must be 'upa4' (reference), 'upa2', or 'siso'."
    )


def pilot_folding_setup(*, n_users: int, frames: int,
                        n_antennas: str = 'upa4') -> FoldingSetup:
    """Construct the registered full-delay AFDM model for Q pilot frames."""
    for name, value in (('n_users', n_users), ('frames', frames)):
        if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value <= 0:
            raise ConfigError(f'{name} must be a positive integer.')
    setup = FoldingSetup(
        system=FoldingSystemConfig(
            bandwidth_hz=BANDWIDTH_HZ, N=N, N_cpp=N_CPP, Q=int(frames),
            K=int(n_users), tau_max_s=TAU_MAX_S, nu_max_hz=NU_MAX_HZ),
        chirp=FoldingChirp(c1=C1, c2=C2), array=resolve_array(n_antennas))
    setup.validate()
    return setup


@dataclass(frozen=True)
class PhysicalPath:
    user_id: int
    path_id: int
    gain_complex: complex
    delay: FoldedDelay
    doppler_hz: float
    mu_z: float
    mu_y: float

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if self.user_id < 0 or self.path_id < 0:
            raise ConfigError("user_id and path_id must be >= 0.")
        if abs(float(self.doppler_hz)) > NU_MAX_HZ + 1e-9:
            raise ConfigError(f"Doppler {self.doppler_hz} exceeds ν_max={NU_MAX_HZ}.")
        if abs(float(self.mu_z)) > 1.0 + 1e-12 or abs(float(self.mu_y)) > 1.0 + 1e-12:
            raise ConfigError(
                "μ_z and μ_y are directional cosines and must lie in [-1, 1]."
            )
        self.delay.validate(N)
        if self.delay.full_delay_samples > D_PHYSICAL_MAX:
            raise ConfigError(
                f"full delay {self.delay.full_delay_samples} exceeds d_max={D_PHYSICAL_MAX}."
            )


@dataclass(frozen=True)
class PhysicalScene:
    activity: np.ndarray
    paths: tuple[PhysicalPath, ...]

    def __post_init__(self) -> None:
        activity = np.asarray(self.activity)
        if activity.ndim != 1 or activity.size == 0:
            raise ConfigError("activity must be a nonempty 1-D 0/1 vector.")
        if not np.all(np.isin(activity, (0, 1))):
            raise ConfigError(
                "activity must be 0/1. Likelihood cannot separate a_k=0 from H_k=0."
            )
        for path in self.paths:
            path.validate()
            if path.user_id >= activity.shape[0]:
                raise ConfigError("path.user_id is outside activity.")

    def paths_of(self, user_id: int) -> tuple[PhysicalPath, ...]:
        return tuple(p for p in self.paths if p.user_id == user_id)
