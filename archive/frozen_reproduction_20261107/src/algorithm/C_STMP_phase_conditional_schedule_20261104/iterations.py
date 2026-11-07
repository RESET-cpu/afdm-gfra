"""Fix phase until conditional inference stabilizes, then propose one update.

No modulo schedule, post-update waiting count, query reset or ratio reset.
Existing conditional convergence controls are reused. Stopping also requires
a small CURRENT phase proposal in expected observation energy. The Gaussian
phase moments remain an approximation to the learned receiver posterior.
"""
import time
import numpy as np
from .phase import update as update_phase
from algorithm.C_STMP_phase_shen_frames_20261103.phase import effective_pilot
from algorithm.C_STMP_variance_em_20261025.iterations import expected_residual_power
from algorithm.STMP.gaussian import gaussian_extrinsic, hermitian
from algorithm.STMP.iterations import moment_damp, _iteration_changes, _stopping_step, _message_diagnostics
from algorithm.STMP.linear import SpatialLinear
from algorithm.STMP.records import SpatialResult


def infer(inputs, denoiser, *, scale, initial_variance, controls, phase_configuration,
          initial_slopes, observer=None, decision_threshold=.5, adapt=True):
    controls.validate_stopping()
    tolerance = phase_configuration['relative_signal_change_tolerance']
    if controls.covariance_mode != 'isotropic' or not 0 < tolerance < 1:
        raise ValueError('Isotropic feedback and explicit positive phase tolerance required')
    q, k, n = inputs.pilot.shape
    m, rows = inputs.observation.shape[1:]
    beta = np.asarray(initial_slopes, float)
    if beta.shape != (k,) or not np.isfinite(beta).all():
        raise ValueError('Finite physical initial slopes required')
    phase = np.exp(1j*np.arange(q)[:, None]*beta[None])
    y, noise = inputs.observation/scale, inputs.noise_variance/scale**2
    tick = time.perf_counter()
    linear = SpatialLinear(effective_pilot(inputs.pilot, phase), m, noise)
    setup = time.perf_counter()-tick
    prior = np.zeros((k, m, rows, n), complex)
    prior_cov = np.eye(m)*max(float(initial_variance), 1e-12)
    old_r = old_raw_v = old_v = old_out = old_out_v = old_mean = old_p = None
    ratio = 1.
    stable = fresh = decision_stable = 0
    old_decision = None
    trace, steps, trials = [], [], []
    reason, last_update = 'MAX_ITERATIONS', 0
    started = time.perf_counter()
    for iteration in range(1, controls.iterations+1):
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
            state, old_mean, old_p, v, old_v)
        if adapt and covariance_change is not None:
            covariance_change = max(covariance_change, em_residual)
            change = max(change, em_residual)
        current = bool(denoiser.message_fresh and denoiser.last.get('site_accepted', True)
                       and denoiser.last.get('unsupported_users', 0) == 0)
        stable, fresh, decision_stable, old_decision, ready = _stopping_step(
            controls, iteration, change, estimate_change, activity_change, covariance_change,
            current, state.activity, decision_threshold, stable, fresh, decision_stable, old_decision)
        trial = None
        converged = False
        diagnostics = _message_diagnostics(linear, y, state.mean, v, posterior, fraction, used, noise)
        if ready:
            scalar = float(np.trace(out_v).real/m)
            if not np.allclose(out_v, np.eye(m)*scalar, rtol=1e-10, atol=1e-12*scalar):
                raise ValueError('Isotropic Gaussian feedback required')
            proposed, trial = update_phase(y, inputs.pilot, out, scalar, noise, phase)
            converged = trial['phase_effect']['relative_signal_change'] <= tolerance
            trial.update(after_iteration=iteration, applied=False,
                type='Shen_proposal_after_conditional_convergence',
                relative_signal_change_tolerance=tolerance,
                phase_stopping_passed=converged,
                query_damping_history_reset=False, raw_variance_history_reset=False,
                query_variance_ratio_reset=False, stopping_windows_reset=not converged,
                channel_rotation=np.zeros(k).tolist(), rotated_cached_means=[])
            trials.append(trial)
        row = dict(iteration=iteration, converged=converged, convergence_change=change,
            estimate_change=estimate_change, activity_change=activity_change,
            input_covariance_change=covariance_change, stable_iterations=stable,
            fresh_iterations=fresh, decision_stable_iterations=decision_stable,
            linear_seconds=linear_seconds, linear_reported_variance=raw_power,
            query_variance_ratio=ratio, next_query_variance_ratio=next_ratio,
            em_variance_target=target, em_residual_power=residual,
            em_posterior_uncertainty=uncertainty, em_relative_residual=em_residual,
            conditional_converged=ready, phase_update_due=ready,
            phase_update_eligible=ready, phase_updates_completed=len(steps),
            iterations_since_last_phase_update=iteration-last_update,
            current_phase_trial=None if trial is None else trial['phase_effect'],
            **diagnostics, **denoiser.last)
        trace.append(row)
        if observer is not None:
            observer(row, state, r, v, prior, prior_cov, out, out_v, posterior)
        old_r, old_raw_v, old_v = r, raw_v, v
        old_out, old_out_v = out, out_v
        old_mean, old_p = state.mean.copy(), state.activity.copy()
        if converged:
            reason = 'CONVERGED'
            break
        if trial is not None and iteration < controls.iterations:
            phase = proposed.copy()
            tick = time.perf_counter()
            linear = SpatialLinear(effective_pilot(inputs.pilot, phase), m, noise)
            trial.update(applied=True, linear_rebuild_seconds=time.perf_counter()-tick,
                         used_by_next_message_step=True)
            steps.append(trial)
            last_update = iteration
            # Only convergence counters restart; numerical messages remain warm.
            stable = fresh = decision_stable = 0
            old_decision = None
            row['phase_update_index'] = len(steps)
        elif trial is not None:
            trial.update(used_by_next_message_step=False, not_applied_reason='no_following_message_budget')
        prior, prior_cov, ratio = out, out_v, next_ratio
    elapsed = time.perf_counter()-started
    result = SpatialResult(state.mean*scale, state.conditional_mean*scale, state.activity,
        state.spatial_covariance*scale**2, tuple(trace), reason, setup,
        elapsed-sum(t['seconds']+t.get('linear_rebuild_seconds', 0.) for t in trials))
    return result, phase, steps, trials
