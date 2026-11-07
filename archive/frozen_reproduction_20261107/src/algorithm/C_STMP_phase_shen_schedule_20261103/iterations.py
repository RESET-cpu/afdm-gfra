"""One phase update after every nonterminal message iteration.

Shen et al., arXiv:2412.20806v1, Algorithm 1 lines 18--22. The message
modules and Gaussian phase moments are AFDM adaptations. No stability gate,
update interval, post-update waiting period or state reset is used.
"""
import time
import numpy as np

from algorithm.C_STMP_phase_shen_frames_20261103.phase import effective_pilot, update as update_phase
from algorithm.C_STMP_variance_em_20261025.iterations import expected_residual_power
from algorithm.STMP.gaussian import gaussian_extrinsic, hermitian
from algorithm.STMP.iterations import moment_damp, _iteration_changes, _message_diagnostics
from algorithm.STMP.linear import SpatialLinear
from algorithm.STMP.records import SpatialResult


def channel_stopping(current, previous, tolerance):
    """Algorithm 1 line 19, including its zero-reference case without a floor."""
    difference = current-previous
    numerator = float(np.vdot(difference, difference).real)
    denominator = float(np.vdot(previous, previous).real)
    stop = numerator <= tolerance*denominator
    relative = numerator/denominator if denominator > 0 else (0. if numerator == 0 else None)
    return bool(stop), dict(channel_change_squared=numerator,
        previous_channel_norm_squared=denominator, channel_squared_relative_change=relative,
        stopping_squared_relative_tolerance=float(tolerance))


def infer(inputs, denoiser, *, scale, initial_variance, controls,
          stopping_tolerance, observer=None, decision_threshold=.5, adapt=True):
    if controls.covariance_mode != 'isotropic':
        raise ValueError('The current AFDM message model uses isotropic covariance')
    if (not np.isfinite(stopping_tolerance) or stopping_tolerance <= 0
            or not isinstance(controls.iterations, int) or controls.iterations < 1):
        raise ValueError('Positive stopping tolerance and iteration budget required')
    q, k, n = inputs.pilot.shape
    m, rows = inputs.observation.shape[1:]
    phase = np.ones((q, k), complex)
    y, noise = inputs.observation/scale, inputs.noise_variance/scale**2
    tick = time.perf_counter()
    linear = SpatialLinear(effective_pilot(inputs.pilot, phase), m, noise)
    setup = time.perf_counter()-tick
    prior = np.zeros((k, m, rows, n), complex)
    prior_cov = np.eye(m)*max(float(initial_variance), 1e-12)
    old_r = old_raw_v = old_v = old_out = old_out_v = old_p = None
    old_mean = np.zeros_like(prior)
    ratio = 1.
    trace, trials = [], []
    reason = 'MAX_ITERATIONS'
    started = time.perf_counter()
    for iteration in range(1, controls.iterations+1):
        used_phase = phase.copy()
        used_phase_update_count = len(trials)
        tick = time.perf_counter()
        _, _, r, raw_v = linear.update(y, prior, prior_cov)
        linear_seconds = time.perf_counter()-tick
        r, raw_v = moment_damp(old_r, old_raw_v, r, raw_v, controls.damping)
        raw_power = float(np.trace(raw_v).real/m)
        v = raw_v*ratio
        state = denoiser(r, v)
        posterior = hermitian(state.spatial_covariance.mean(axis=0))
        posterior = np.eye(m)*np.trace(posterior).real/m
        target, residual, uncertainty = expected_residual_power(r, state.mean, state.spatial_covariance)
        power = raw_power*ratio
        em_residual = abs(target-power)/max(target, power)
        next_ratio = ((1-controls.damping)*ratio+controls.damping*target/raw_power) if adapt else 1.
        out, out_v, fraction, used = gaussian_extrinsic(state.mean, posterior, r, v,
            controls.variance_fraction_floor, controls.variance_fraction_ceiling)
        out, out_v = moment_damp(old_out, old_out_v, out, out_v, controls.damping)
        if not np.isfinite(out).all() or not np.isfinite(out_v).all():
            raise FloatingPointError('Invalid Gaussian feedback')
        change, estimate_change, activity_change, covariance_change = _iteration_changes(
            state, old_mean if iteration > 1 else None, old_p, v, old_v)
        converged, stopping = channel_stopping(state.mean, old_mean, stopping_tolerance)
        diagnostics = _message_diagnostics(linear, y, state.mean, v, posterior, fraction, used, noise)
        trial = None
        if not converged:
            scalar = float(np.trace(out_v).real/m)
            if not np.allclose(out_v, np.eye(m)*scalar, rtol=1e-10, atol=1e-12*scalar):
                raise ValueError('Actual isotropic feedback required')
            phase, trial = update_phase(y, inputs.pilot, out, scalar, noise, used_phase)
            tick = time.perf_counter()
            linear = SpatialLinear(effective_pilot(inputs.pilot, phase), m, noise)
            trial.update(type='Shen_every_outer_iteration', after_iteration=iteration,
                applied=True, used_by_next_message_step=iteration < controls.iterations,
                linear_rebuild_seconds=time.perf_counter()-tick,
                query_damping_history_reset=False, raw_variance_history_reset=False,
                query_variance_ratio_reset=False, stopping_windows_reset=False,
                rotated_cached_means=[], channel_rotation=np.zeros(k).tolist())
            trials.append(trial)
        row = dict(iteration=iteration, converged=converged,
            convergence_change=change, estimate_change=estimate_change,
            activity_change=activity_change, input_covariance_change=covariance_change,
            linear_seconds=linear_seconds, linear_reported_variance=raw_power,
            query_variance_ratio=ratio, next_query_variance_ratio=next_ratio,
            em_variance_target=target, em_residual_power=residual,
            em_posterior_uncertainty=uncertainty, em_relative_residual=em_residual,
            phase_update_due=True, phase_update_eligible=not converged,
            phase_update_applied=trial is not None,
            phase_updates_completed=len(trials),
            phase_updates_used_by_current_message=used_phase_update_count,
            current_phase_trial=None if trial is None else dict(
                maximum_frame_increment=trial['maximum_frame_increment']),
            phase_update_skipped='overall_stopping_criterion_met' if converged else None,
            **stopping, **diagnostics, **denoiser.last)
        trace.append(row)
        if observer is not None:
            observer(row, state, r, v, prior, prior_cov, out, out_v, posterior)
        if converged:
            reason = 'CONVERGED'
            break
        old_r, old_raw_v, old_v = r, raw_v, v
        old_out, old_out_v = out, out_v
        old_mean, old_p = state.mean.copy(), state.activity.copy()
        prior, prior_cov, ratio = out, out_v, next_ratio
    elapsed = time.perf_counter()-started
    result = SpatialResult(state.mean*scale, state.conditional_mean*scale, state.activity,
        state.spatial_covariance*scale**2, tuple(trace), reason, setup,
        elapsed-sum(t['seconds']+t['linear_rebuild_seconds'] for t in trials))
    # At a hard cap the last updated phase has no corresponding channel pass.
    # Return the phase used to form H separately from this next phase state.
    return result, used_phase, phase.copy(), trials
