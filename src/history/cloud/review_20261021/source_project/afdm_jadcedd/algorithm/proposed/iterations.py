"""Proposed receiver: linear update, denoising, extrinsic feedback, stopping.

The equations and the two damping operations follow docs/THEORY.md, T3–T5
and T13–T17. Diagnostic calculations are collected below the iteration loop.
"""

import time

import numpy as np
from scipy.linalg import eigh

from afdm_jadcedd.system.observation import ReceiverInput
from .gaussian import gaussian_extrinsic, hermitian
from .linear import SpatialLinear
from .records import SpatialConfig, SpatialResult


def moment_damp(old_mean, old_cov, mean, cov, weight):
    """Interpolate the two Gaussian parameters with the new-value weight."""
    if old_mean is None:
        return mean, cov
    return (
        (1 - weight) * old_mean + weight * mean,
        (1 - weight) * old_cov + weight * cov,
    )


def run_spatial_score(
    inputs, denoiser, *, scale, initial_variance, config=None, observer=None, decision_threshold=0.5
):
    """Run the shared-covariance message updates in normalized coordinates.

    ``prior, prior_cov`` are the incoming linear-module message;
    ``r, v`` are the denoiser query; ``out, out_v`` feed the next iteration.
    Activity probabilities and channel moments are returned by one denoiser.
    """
    if not isinstance(inputs, ReceiverInput):
        raise TypeError("four-field ReceiverInput required")
    cfg = SpatialConfig() if config is None else config
    cfg.validate_stopping()
    if cfg.covariance_mode not in ("spatial", "isotropic"):
        raise ValueError("unknown covariance mode")
    if cfg.decision_stability_window and (
        not np.isfinite(decision_threshold) or not 0 < decision_threshold < 1
    ):
        raise ValueError("finite decision threshold between zero and one required")

    # Initialization: x_p = 0, covariance = activity prior × training power.
    y = inputs.observation / scale
    noise = inputs.noise_variance / scale**2
    tick = time.monotonic()
    linear = SpatialLinear(inputs.operator, y.shape[1], noise)
    setup = time.monotonic() - tick
    initial = float(initial_variance)
    prior_cov = np.eye(linear.antennas) * max(initial, 1e-12)
    prior = np.zeros((linear.users, linear.antennas, y.shape[2], linear.columns), complex)
    old_r = old_v = old_out = old_out_v = old_mean = old_p = None
    stable = fresh = decision_stable = 0
    old_decision = None
    trace = []
    started = time.monotonic()
    reason = "MAX_ITERATIONS"

    for iteration in range(1, cfg.iterations + 1):
        # A. Linear posterior and extrinsic query, followed by damping (T3–T5).
        tick = time.monotonic()
        _, _, r, v = linear.update(y, prior, prior_cov)
        linear_seconds = time.monotonic() - tick
        r, v = moment_damp(old_r, old_v, r, v, cfg.damping)

        # B. Score moments, activity classification and joint moments (T13–T16).
        state = denoiser(r, v)
        posterior = hermitian(state.spatial_covariance.mean(axis=0))
        if cfg.covariance_mode == "isotropic":
            posterior = np.eye(linear.antennas) * np.trace(posterior).real / linear.antennas

        # Extrinsic feedback to A, followed by the second damping operation (T17).
        out, out_v, fraction, used = gaussian_extrinsic(
            state.mean,
            posterior,
            r,
            v,
            cfg.variance_fraction_floor,
            cfg.variance_fraction_ceiling,
        )
        out, out_v = moment_damp(old_out, old_out_v, out, out_v, cfg.damping)
        if not np.isfinite(out).all() or not np.isfinite(out_v).all():
            raise FloatingPointError("invalid extrinsic output")

        # Stop only after the completed update satisfies the configured windows.
        changes = _iteration_changes(state, old_mean, old_p, v, old_v)
        change, estimate_change, activity_change, input_covariance_change = changes
        stable, fresh, decision_stable, old_decision, converged = _stopping_step(
            cfg,
            iteration,
            change,
            estimate_change,
            activity_change,
            input_covariance_change,
            denoiser.message_fresh,
            state.activity,
            decision_threshold,
            stable,
            fresh,
            decision_stable,
            old_decision,
        )
        row = dict(
            iteration=iteration,
            convergence_change=change,
            converged=converged,
            estimate_change=estimate_change,
            activity_change=activity_change,
            input_covariance_change=input_covariance_change,
            stable_iterations=stable,
            fresh_iterations=fresh,
            linear_seconds=linear_seconds,
            **_message_diagnostics(linear, y, state.mean, v, posterior, fraction, used, noise),
            **denoiser.last,
        )
        if cfg.decision_stability_window:
            row["decision_stable_iterations"] = decision_stable
        trace.append(row)
        if observer is not None:
            observer(row, state, r, v, prior, prior_cov, out, out_v, posterior)

        old_r, old_v, old_out, old_out_v = r, v, out, out_v
        old_mean, old_p = state.mean.copy(), state.activity.copy()
        prior, prior_cov = out, out_v
        if converged:
            reason = "CONVERGED"
            break

    return SpatialResult(
        state.mean * scale,
        state.conditional_mean * scale,
        state.activity,
        state.spatial_covariance * scale**2,
        tuple(trace),
        reason,
        setup,
        time.monotonic() - started,
    )


def _iteration_changes(state, old_mean, old_p, covariance, old_covariance):
    if old_mean is None:
        return None, None, None, None
    estimate_change = float(
        np.linalg.norm(state.mean - old_mean)
        / max(np.linalg.norm(state.mean), np.linalg.norm(old_mean), 1e-12)
    )
    activity_change = float(np.max(abs(state.activity - old_p)))
    covariance_change = float(
        np.linalg.norm(covariance - old_covariance)
        / max(np.linalg.norm(covariance), np.linalg.norm(old_covariance))
    )
    return (
        max(estimate_change, activity_change, covariance_change),
        estimate_change,
        activity_change,
        covariance_change,
    )


def _stopping_step(
    cfg,
    iteration,
    change,
    estimate_change,
    activity_change,
    input_covariance_change,
    message_fresh,
    probabilities,
    decision_threshold,
    stable,
    fresh,
    decision_stable,
    old_decision,
):
    """Advance prefix-only counters; a decision window counts rows, not changes."""
    if cfg.activity_convergence_tolerance is None:
        stable_now = change is not None and change < cfg.convergence_tolerance
    else:
        stable_now = (
            estimate_change is not None
            and estimate_change < cfg.convergence_tolerance
            and input_covariance_change < cfg.convergence_tolerance
            and activity_change < cfg.activity_convergence_tolerance
        )
    stable = stable + 1 if stable_now else 0
    fresh = fresh + 1 if message_fresh else 0
    if cfg.decision_stability_window:
        decision = np.asarray(probabilities) >= decision_threshold
        decision_stable = (
            decision_stable + 1
            if old_decision is not None and np.array_equal(decision, old_decision)
            else 1
        )
        old_decision = decision.copy()
    converged = (
        iteration >= cfg.min_iterations
        and stable >= cfg.convergence_patience
        and fresh >= cfg.convergence_patience
        and decision_stable >= cfg.decision_stability_window
    )
    return stable, fresh, decision_stable, old_decision, bool(converged)


def _message_diagnostics(linear, observation, mean, covariance, posterior, fraction, used, noise):
    """Record message diagnostics without participating in the updates."""
    return dict(
        input_variance_trace=float(np.trace(covariance).real / linear.antennas),
        input_eigen_min=float(eigh(covariance, eigvals_only=True).min()),
        input_eigen_max=float(eigh(covariance, eigvals_only=True).max()),
        posterior_variance_trace=float(np.trace(posterior).real / linear.antennas),
        variance_fraction_min=float(fraction.min()),
        variance_fraction_max=float(fraction.max()),
        projected_eigenvalues=int(np.count_nonzero(fraction != used)),
        residual_power=float(np.mean(abs(observation - linear.forward(mean)) ** 2)),
        noise_variance=noise,
    )
