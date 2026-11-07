"""Moment, iteration-control and inference-result records."""

from dataclasses import dataclass
import numpy as np


@dataclass
class SpatialMoments:
    mean: np.ndarray
    conditional_mean: np.ndarray
    activity: np.ndarray
    spatial_covariance: np.ndarray  # [K,M,M], average over the D coordinates
    conditional_spatial_covariance: np.ndarray
    log_evidence_bound: np.ndarray
    phase_kl: np.ndarray
    g_kl: np.ndarray


@dataclass(frozen=True)
class SpatialConfig:
    iterations: int = 600
    damping: float = 0.2
    min_iterations: int = 60
    convergence_tolerance: float = 1e-4
    convergence_patience: int = 10
    variance_fraction_floor: float = 1e-6
    variance_fraction_ceiling: float = 1 - 1e-6
    covariance_mode: str = "spatial"
    activity_convergence_tolerance: float | None = None
    raw_site_residual_tolerance: float = 1e-4
    activity_weight_residual_tolerance: float = 1e-4
    decision_stability_window: int = 0
    activity_stopping_reference: str = "smoothed"

    def validate_stopping(self):
        """Validate optional stopping controls without changing legacy defaults."""
        if self.activity_stopping_reference not in ("smoothed", "previous"):
            raise ValueError("activity_stopping_reference must be smoothed or previous")
        for name in (
            "activity_convergence_tolerance",
            "raw_site_residual_tolerance",
            "activity_weight_residual_tolerance",
        ):
            value = getattr(self, name)
            if name == "activity_convergence_tolerance" and value is None:
                continue
            if (
                isinstance(value, (bool, np.bool_))
                or not isinstance(value, (int, float, np.integer, np.floating))
                or not np.isfinite(value)
                or value <= 0
            ):
                raise ValueError(name + " must be positive and finite")
        window = self.decision_stability_window
        if (
            isinstance(window, (bool, np.bool_))
            or not isinstance(window, (int, np.integer))
            or window < 0
        ):
            raise ValueError("decision_stability_window must be a nonnegative integer")


@dataclass
class SpatialResult:
    estimate: np.ndarray
    conditional_matrix: np.ndarray
    probabilities: np.ndarray
    spatial_covariance: np.ndarray
    trace: tuple
    stopping_reason: str
    setup_seconds: float
    iteration_seconds: float
