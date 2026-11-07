"""Bounded conditional inference and phase minimization from the same moments.

Fixed phase reproduces C_STMP_variance_em_20261025 exactly. Between phase
changes, all message histories persist. Changing the linear operator resets
query damping/comparison histories, while retaining the channel site and
outgoing message as a warm start. This is approximate inference, not an exact
EM E step or a guarantee on observed likelihood/activity error.
"""
import time
import numpy as np

from algorithm.STMP.gaussian import gaussian_extrinsic, hermitian
from algorithm.STMP.linear import SpatialLinear
from algorithm.STMP.records import SpatialResult
from algorithm.STMP.iterations import moment_damp, _iteration_changes, _stopping_step, _message_diagnostics
from algorithm.C_STMP_variance_em_20261025.iterations import expected_residual_power
from system.phase import phase_operator
from .phase import update as update_phase


def infer(inputs, denoiser, *, scale, initial_variance, controls, policy,
          initial_slopes=None, phase_enabled=True, observer=None,
          phase_observer=None, decision_threshold=.5, adapt=True):
    cfg = controls
    cfg.validate_stopping()
    if cfg.covariance_mode != 'isotropic':
        raise ValueError('This candidate preserves the scalar receiver interface')
    block_size = int(policy['e_step_iterations'])
    if block_size < 1 or cfg.iterations < 1 or policy['phase_tolerance'] < 0:
        raise ValueError('Positive iteration budgets and nonnegative tolerance required')
    y, noise = inputs.observation/scale, inputs.noise_variance/scale**2
    beta = np.zeros(inputs.pilot.shape[1]) if initial_slopes is None else np.asarray(initial_slopes, float).copy()
    if beta.shape != (inputs.pilot.shape[1],) or not np.isfinite(beta).all():
        raise ValueError('One finite slope per user required')
    tick = time.monotonic()
    linear = SpatialLinear(phase_operator(inputs.pilot, beta), y.shape[1], noise)
    setup = time.monotonic()-tick
    eye = np.eye(linear.antennas)
    prior_cov = eye*max(float(initial_variance), 1e-12)
    prior = np.zeros((linear.users, linear.antennas, y.shape[2], linear.columns), complex)
    old_r = old_raw_v = old_v = old_out = old_out_v = old_mean = old_p = None
    stable = fresh = decision_stable = local_iteration = block_iteration = 0
    old_decision = None
    ratio = 1.
    trace, trials, reason = [], [], 'MAX_ITERATIONS'
    phase_count = 0
    started = time.monotonic()
    for iteration in range(1, cfg.iterations+1):
        local_iteration += 1
        block_iteration += 1
        tick = time.monotonic()
        _, _, r, raw_v = linear.update(y, prior, prior_cov)
        linear_seconds = time.monotonic()-tick
        r, raw_v = moment_damp(old_r, old_raw_v, r, raw_v, cfg.damping)
        raw_power = float(np.trace(raw_v).real/linear.antennas)
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
            local_iteration, change, estimate_change, activity_change, covariance_change,
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
        row.update(conditional_iteration=local_iteration, e_step_converged=converged,
            phase_updates_used=phase_count, phase_slopes_used=beta.tolist())
        trace.append(row)
        if observer is not None:
            observer(row, state, r, v, prior, prior_cov, out, out_v, posterior)
        old_r, old_raw_v, old_v = r, raw_v, v
        old_out, old_out_v = out, out_v
        old_mean, old_p = state.mean.copy(), state.activity.copy()
        prior, prior_cov, ratio = out, out_v, next_ratio
        if not phase_enabled:
            if converged:
                reason = 'CONVERGED'
                break
            continue
        # Reserve at least one full E block after an applied M step. The last
        # returned channel therefore always used the returned beta.
        if cfg.iterations-iteration < block_size:
            continue
        if not converged and block_iteration < block_size:
            continue
        proposal, report = update_phase(y, inputs.pilot, state.mean, beta,
                                       **policy['m_step'])
        delta = np.angle(np.exp(1j*(proposal-beta)))
        max_frame_step = float((len(inputs.pilot)-1)*np.max(abs(delta)))
        small = max_frame_step <= policy['phase_tolerance']
        changed = bool(np.any(proposal != beta))
        # A numerically negligible M step must not repeatedly clear the E-step
        # convergence history. Small M changes alone do not terminate inference.
        applied = changed and not small
        trial = dict(report, after_iteration=iteration,
            e_step_iterations=block_iteration, e_step_converged=converged,
            before_slopes=beta.tolist(), proposed_slopes=proposal.tolist(),
            maximum_frame_increment=max_frame_step, applied=applied,
            used_by_following_e_step=applied,
            query_history_reset=applied, query_variance_ratio_reset=False,
            retained_channel_site=True, linear_rebuild_seconds=0.)
        trials.append(trial)
        if applied:
            beta = proposal.copy()
            tick = time.monotonic()
            linear = SpatialLinear(phase_operator(inputs.pilot, beta), y.shape[1], noise)
            trial['linear_rebuild_seconds'] = time.monotonic()-tick
            setup += trial['linear_rebuild_seconds']
            phase_count += 1
            old_r = old_raw_v = old_v = old_mean = old_p = None
            stable = fresh = decision_stable = local_iteration = 0
            old_decision = None
        block_iteration = 0
        if phase_observer is not None:
            phase_observer(trial)
        if converged and small:
            reason = 'CONVERGED'
            break
    result = SpatialResult(state.mean*scale, state.conditional_mean*scale, state.activity,
        state.spatial_covariance*scale**2, tuple(trace), reason, setup, time.monotonic()-started)
    return result, beta, trials
