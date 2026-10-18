"""Immutable delay records. API never accepts an ambiguous delay_samples alone."""

from __future__ import annotations

from dataclasses import dataclass

from afdm_jadcedd.system.core.conventions import ConfigError


def wrap_to_period(index: int, period: int) -> int:
    """Return <n>_N in {0,...,N-1} without Python negative array indexing."""
    if period <= 0:
        raise ConfigError("period must be positive.")
    quotient = index // period
    remainder = index - quotient * period
    if remainder < 0 or remainder >= period:
        raise RuntimeError(f"wrap_to_period produced {remainder} for n={index}, N={period}.")
    return remainder


@dataclass(frozen=True)
class FoldedDelay:
    """Shen-style quotient-remainder parameterization of one integer delay.

    This is only a parameterization. It does not assert operator folding.
    """

    full_delay_samples: int
    wrap_index: int
    folded_delay_samples: int

    @classmethod
    def from_full(cls, full_delay_samples: int, n: int) -> FoldedDelay:
        if n <= 0:
            raise ConfigError("N must be positive when forming FoldedDelay.")
        if isinstance(full_delay_samples, bool) or not isinstance(full_delay_samples, int):
            raise ConfigError("full_delay_samples must be an int.")
        if full_delay_samples < 0:
            raise ConfigError("full_delay_samples must be >= 0.")
        wrap_index = full_delay_samples // n
        folded = wrap_to_period(full_delay_samples, n)
        record = cls(full_delay_samples, wrap_index, folded)
        record.validate(n)
        return record

    def validate(self, n: int) -> None:
        if n <= 0:
            raise ConfigError("N must be positive.")
        d = self.full_delay_samples
        b = self.wrap_index
        ell = self.folded_delay_samples
        if d < 0 or b < 0:
            raise ConfigError("full delay and wrap_index must be non-negative.")
        if ell < 0 or ell >= n:
            raise ConfigError(f"folded_delay_samples={ell} is outside 0,...,N-1.")
        if d != b * n + ell:
            raise ConfigError(
                f"FoldedDelay invariant failed: {d} != {b}*{n}+{ell}."
            )
