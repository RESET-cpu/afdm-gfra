"""One damped approximate EM variance update per C-STMP outer iteration.

All network conditions and extrinsic subtraction use the same scalar variance.
The variance estimate is an auxiliary parameter, not physical observation noise.
"""
import time
import numpy as np
from algorithm.STMP.gaussian import gaussian_extrinsic, hermitian
from algorithm.STMP.linear import SpatialLinear
from algorithm.STMP.records import SpatialResult
from algorithm.STMP.iterations import moment_damp, _iteration_changes, _stopping_step, _message_diagnostics


def expected_residual_power(query, mean, spatial_covariance):
    """E[||r-H||^2]/D using joint activity/channel moments, complex coordinates."""
    residual = float(np.mean(abs(query-mean)**2))
    uncertainty = float(np.trace(spatial_covariance, axis1=-2, axis2=-1).real.mean()/query.shape[1])
    target = residual + uncertainty
    if not np.isfinite(target) or target <= 0 or uncertainty < -1e-12:
        raise FloatingPointError('Invalid posterior expected residual energy')
    return target, residual, uncertainty


def run_spatial_score(inputs, denoiser, *, scale, initial_variance, config,
                      observer=None, decision_threshold=.5, adapt=True):
    cfg = config
    cfg.validate_stopping()
    if cfg.covariance_mode != 'isotropic':
        raise ValueError('This candidate preserves the scalar C-STMP interface')
    y, noise = inputs.observation/scale, inputs.noise_variance/scale**2
    tick = time.monotonic()
    linear = SpatialLinear(inputs.operator, y.shape[1], noise)
    setup = time.monotonic()-tick
    eye = np.eye(linear.antennas)
    prior_cov = eye*max(float(initial_variance), 1e-12)
    prior = np.zeros((linear.users, linear.antennas, y.shape[2], linear.columns), complex)
    old_r = old_raw_v = old_v = old_out = old_out_v = old_mean = old_p = None
    stable = fresh = decision_stable = 0
    old_decision = None
    ratio = 1.
    trace, reason = [], 'MAX_ITERATIONS'
    started = time.monotonic()
    for iteration in range(1, cfg.iterations+1):
        tick = time.monotonic()
        _, _, r, raw_v = linear.update(y, prior, prior_cov)
        linear_seconds = time.monotonic()-tick
        r, raw_v = moment_damp(old_r, old_raw_v, r, raw_v, cfg.damping)
        raw_power = float(np.trace(raw_v).real/linear.antennas)
        # raw_v retains only the linear update history; do not feed the calibrated
        # variance into the raw linear-query damping history as in the old median trial.
        v = raw_v*ratio
        power = raw_power*ratio
        state = denoiser(r, v)
        posterior = eye*np.trace(hermitian(state.spatial_covariance.mean(0))).real/linear.antennas
        target, residual, uncertainty = expected_residual_power(r, state.mean, state.spatial_covariance)
        em_residual = abs(target-power)/max(target, power)
        next_ratio = ((1-cfg.damping)*ratio+cfg.damping*target/raw_power) if adapt else 1.
        out, out_v, fraction, used = gaussian_extrinsic(state.mean, posterior, r, v,
            cfg.variance_fraction_floor, cfg.variance_fraction_ceiling)
        out, out_v = moment_damp(old_out, old_out_v, out, out_v, cfg.damping)
        if not np.isfinite(out).all() or not np.isfinite(out_v).all():
            raise FloatingPointError('Invalid extrinsic output')
        change, estimate_change, activity_change, covariance_change = _iteration_changes(state, old_mean, old_p, v, old_v)
        if adapt and covariance_change is not None:
            covariance_change = max(covariance_change, em_residual)
            change = max(change, em_residual)
        stable, fresh, decision_stable, old_decision, converged = _stopping_step(cfg,
            iteration, change, estimate_change, activity_change, covariance_change,
            denoiser.message_fresh, state.activity, decision_threshold, stable, fresh,
            decision_stable, old_decision)
        row = dict(iteration=iteration, convergence_change=change, converged=converged,
            estimate_change=estimate_change, activity_change=activity_change,
            input_covariance_change=covariance_change, stable_iterations=stable,
            fresh_iterations=fresh, decision_stable_iterations=decision_stable,
            linear_seconds=linear_seconds, linear_reported_variance=raw_power,
            query_variance_ratio=ratio, next_query_variance_ratio=next_ratio,
            em_variance_target=target, em_residual_power=residual,
            em_posterior_uncertainty=uncertainty, em_relative_residual=em_residual,
            **_message_diagnostics(linear, y, state.mean, v, posterior, fraction, used, noise),
            **denoiser.last)
        trace.append(row)
        if observer is not None:
            observer(row, state, r, v, prior, prior_cov, out, out_v, posterior)
        old_r, old_raw_v, old_v = r, raw_v, v
        old_out, old_out_v = out, out_v
        old_mean, old_p = state.mean.copy(), state.activity.copy()
        prior, prior_cov, ratio = out, out_v, next_ratio
        if converged:
            reason = 'CONVERGED'
            break
    return SpatialResult(state.mean*scale, state.conditional_mean*scale, state.activity,
        state.spatial_covariance*scale**2, tuple(trace), reason, setup, time.monotonic()-started)
