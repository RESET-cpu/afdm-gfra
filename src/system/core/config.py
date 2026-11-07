"""Small shared configuration types used by both physical forwards."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from system.core.conventions import ConfigError


@dataclass(frozen=True)
class ArrayConfig:
    """Uniform planar array dimensions and normalized element spacings."""

    M_z: int
    M_y: int
    d_z_over_lambda: float = 0.5
    d_y_over_lambda: float = 0.5

    @property
    def M(self) -> int:
        return self.M_z * self.M_y

    def antenna_index(self, n_z: int, n_y: int) -> int:
        if not (0 <= n_z < self.M_z and 0 <= n_y < self.M_y):
            raise ConfigError("UPA indices out of range.")
        return int(n_z + self.M_z * n_y)

    def unravel(self, m: int) -> tuple[int, int]:
        if not (0 <= m < self.M):
            raise ConfigError(f"antenna index m={m} out of range.")
        n_y, n_z = divmod(m, self.M_z)
        return int(n_z), int(n_y)

    def validate(self) -> None:
        for name, value in (("M_z", self.M_z), ("M_y", self.M_y)):
            if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
                raise ConfigError(f"{name} must be an integer.")
            if int(value) <= 0:
                raise ConfigError(f"{name} must be positive.")
        for name, value in (
            ("d_z_over_lambda", self.d_z_over_lambda),
            ("d_y_over_lambda", self.d_y_over_lambda),
        ):
            if not np.isfinite(value) or float(value) <= 0.0:
                raise ConfigError(f"{name} must be finite and positive.")
