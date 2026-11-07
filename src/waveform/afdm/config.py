"""Configuration and path records for the long-CPP AFDM forwards."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from channel.core.config import ArrayConfig
from channel.core.conventions import DTYPE_R
from channel.core.conventions import ConfigError
from waveform.afdm.types import FoldedDelay


@dataclass(frozen=True)
class FoldingSystemConfig:
    bandwidth_hz: float
    N: int
    N_cpp: int
    Q: int
    K: int
    tau_max_s: float | None = None
    nu_max_hz: float | None = None

    @property
    def sampling_period_s(self) -> float:
        return DTYPE_R(1.0 / self.bandwidth_hz)

    def validate(self) -> None:
        for name, value in (("N", self.N), ("N_cpp", self.N_cpp), ("Q", self.Q), ("K", self.K)):
            if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
                raise ConfigError(f"{name} must be an integer.")
        if self.N <= 0 or self.Q <= 0 or self.K <= 0:
            raise ConfigError("N, Q, and K must be positive.")
        if self.N_cpp < 0:
            raise ConfigError("N_cpp must be nonnegative.")
        if not np.isfinite(self.bandwidth_hz) or self.bandwidth_hz <= 0.0:
            raise ConfigError("bandwidth_hz must be finite and positive.")
        if self.tau_max_s is not None:
            if not np.isfinite(self.tau_max_s) or self.tau_max_s < 0.0:
                raise ConfigError("tau_max_s must be finite and nonnegative.")
            if self.N_cpp * self.sampling_period_s + 1e-15 < self.tau_max_s:
                raise ConfigError("N_cpp T_s must cover tau_max_s.")
        if self.nu_max_hz is not None and (
            not np.isfinite(self.nu_max_hz) or self.nu_max_hz < 0.0
        ):
            raise ConfigError("nu_max_hz must be finite and nonnegative.")


@dataclass(frozen=True)
class FoldingChirp:
    """The fixed AFDM chirp shared by every block in the current model."""

    c1: float
    c2: float

    def c1_of(self, q: int, n: int) -> float:
        del q, n
        return DTYPE_R(self.c1)

    def validate(self) -> None:
        if not np.isfinite(self.c1) or not np.isfinite(self.c2):
            raise ConfigError("c1 and c2 must be finite.")


@dataclass(frozen=True)
class FoldingSetup:
    system: FoldingSystemConfig
    chirp: FoldingChirp
    array: ArrayConfig

    def validate(self) -> None:
        self.system.validate()
        self.chirp.validate()
        self.array.validate()


@dataclass(frozen=True)
class FoldingPathRecord:
    user_id: int
    path_id: int
    gain_complex: complex
    delay: FoldedDelay
    doppler_hz: float
    mu_z: float
    mu_y: float

    def validate(self, system: FoldingSystemConfig) -> None:
        if self.user_id < 0 or self.user_id >= system.K:
            raise ConfigError("user_id out of range.")
        if self.path_id < 0:
            raise ConfigError("path_id must be nonnegative.")
        if not np.isfinite(self.gain_complex):
            raise ConfigError("gain_complex must be finite.")
        self.delay.validate(system.N)
        delay = self.delay.full_delay_samples
        if delay > system.N_cpp:
            raise ConfigError("full delay exceeds the CPP and would cause IBI.")
        if system.tau_max_s is not None:
            physical_max = int(np.floor(system.tau_max_s * system.bandwidth_hz + 1e-15))
            if delay > physical_max:
                raise ConfigError("full delay exceeds the configured physical support.")
        if not np.isfinite(self.doppler_hz):
            raise ConfigError("doppler_hz must be finite.")
        if system.nu_max_hz is not None and abs(self.doppler_hz) > system.nu_max_hz + 1e-15:
            raise ConfigError("doppler_hz exceeds nu_max_hz.")
        if not np.isfinite(self.mu_z) or not np.isfinite(self.mu_y):
            raise ConfigError("direction cosines must be finite.")
        if self.mu_z**2 + self.mu_y**2 > 1.0 + 1e-12:
            raise ConfigError("mu_z^2 + mu_y^2 must not exceed one.")


@dataclass(frozen=True)
class FoldingScene:
    activity: np.ndarray
    paths: tuple[FoldingPathRecord, ...]

    def validate(self, system: FoldingSystemConfig) -> None:
        if self.activity.shape != (system.K,) or not np.all(np.isin(self.activity, (0, 1))):
            raise ConfigError("activity must be a length-K binary vector.")
        for path in self.paths:
            path.validate(system)

    def paths_of(self, user_id: int) -> tuple[FoldingPathRecord, ...]:
        return tuple(path for path in self.paths if path.user_id == user_id)


def siso_array() -> ArrayConfig:
    return ArrayConfig(M_z=1, M_y=1)


def upa2x2() -> ArrayConfig:
    return ArrayConfig(M_z=2, M_y=2)


def upa4x4() -> ArrayConfig:
    return ArrayConfig(M_z=4, M_y=4)
