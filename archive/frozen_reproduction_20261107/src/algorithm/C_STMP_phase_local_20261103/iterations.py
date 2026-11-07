"""Preserved selected conditional loop with local phase steps and valid zero steps.

Output thresholds and stability gates match the selected receiver. Fixed/once
controls use the same periodic output checks after their budget is exhausted.
"""
import time
import numpy as np
from .phase import update as update_phase
from algorithm.C_STMP_phase_direct_20261103.phase import update as update_reduced_legacy
from system.phase import phase_operator
from algorithm.C_STMP_variance_em_20261025.iterations import expected_residual_power
from algorithm.STMP.gaussian import gaussian_extrinsic, hermitian
from algorithm.STMP.iterations import moment_damp, _iteration_changes, _stopping_step, _message_diagnostics
from algorithm.STMP.linear import SpatialLinear
from algorithm.STMP.records import SpatialResult
from .stopping import OutputCycleStopping
from algorithm.C_STMP_phase_selection_20261030.stopping import trial_changes


def infer(inputs, denoiser, *, scale, initial_variance, controls, phase_configuration,
          initial_slopes, observer=None, decision_threshold=.5, adapt=True):
    p = phase_configuration
    local = p['local_update']
    budget = local['maximum_updates']
    if budget is not None and (type(budget) is not int or budget < 0):
        raise ValueError('Phase update budget must be nonnegative or null')
    controls.validate_stopping()
    if controls.covariance_mode != 'isotropic':
        raise ValueError('Isotropic C-STMP feedback required')
    start, interval = p['periodic_update']['start'], p['periodic_update']['interval']
    settle = p['minimum_iterations_after_last_update']
    if (any(type(v) is not int or v < 1 for v in (start, interval, settle))
            or settle > interval or start+settle > controls.iterations):
        raise ValueError('Positive schedule with final conditional refinement required')
    if p['stopping_mode'] != 'cycle':
        raise ValueError('This independent candidate supports output-cycle stopping only')
    if not 0 < p['trial_relative_tolerance'] < 1:
        raise ValueError('Trial tolerance must lie between zero and one')
    q, k, n = inputs.pilot.shape
    m, rows = inputs.observation.shape[1:]
    beta = np.asarray(initial_slopes, float).copy()
    if beta.shape != (k,) or not np.isfinite(beta).all():
        raise ValueError('Finite per-user initial slopes required')
    y = inputs.observation/scale
    noise = inputs.noise_variance/scale**2
    frames = np.arange(q)
    tick = time.perf_counter()
    gram = np.einsum('qkn,skn->kqs', inputs.pilot, inputs.pilot.conj(), optimize=True)
    linear = SpatialLinear(phase_operator(inputs.pilot, beta), m, noise)
    setup = time.perf_counter()-tick
    started = time.perf_counter()
    prior = np.zeros((k,m,rows,n), complex)
    prior_cov = np.eye(m)*max(float(initial_variance), 1e-12)
    old_r = old_raw_v = old_v = old_out = old_out_v = old_mean = old_p = None
    ratio = 1.
    stable = fresh = decision_stable = 0
    old_decision = None
    trace, steps, trials = [], [], []
    reason, last_update, trial_stable = 'MAX_ITERATIONS', 0, 0
    stopping = OutputCycleStopping(p['stopping'], minimum_iterations=controls.min_iterations)

    for iteration in range(1, controls.iterations+1):
        tick = time.perf_counter()
        _, _, r, raw_v = linear.update(y, prior, prior_cov)
        linear_seconds = time.perf_counter()-tick
        r, raw_v = moment_damp(old_r, old_raw_v, r, raw_v, controls.damping)
        raw_power = float(np.trace(raw_v).real/m)
        v = raw_v*ratio
        power = raw_power*ratio
        state = denoiser(r, v)
        posterior = hermitian(state.spatial_covariance.mean(axis=0))
        posterior = np.eye(m)*np.trace(posterior).real/m
        target, residual, uncertainty = expected_residual_power(r, state.mean, state.spatial_covariance)
        em_residual = abs(target-power)/max(target, power)
        next_ratio = ((1-controls.damping)*ratio+controls.damping*target/raw_power) if adapt else 1.
        out, out_v, fraction, used = gaussian_extrinsic(state.mean, posterior, r, v,
            controls.variance_fraction_floor, controls.variance_fraction_ceiling)
        out, out_v = moment_damp(old_out, old_out_v, out, out_v, controls.damping)
        if not np.isfinite(out).all() or not np.isfinite(out_v).all():
            raise FloatingPointError('Invalid feedback')
        change, estimate_change, activity_change, covariance_change = _iteration_changes(state, old_mean, old_p, v, old_v)
        if adapt and covariance_change is not None:
            covariance_change = max(covariance_change, em_residual)
            change = max(change, em_residual)
        stable, fresh, decision_stable, old_decision, legacy = _stopping_step(controls, iteration,
            change, estimate_change, activity_change, covariance_change, denoiser.message_fresh,
            state.activity, decision_threshold, stable, fresh, decision_stable, old_decision)
        due = iteration >= start and (iteration-start) % interval == 0
        stopping.observe_decisions(state.activity, decision_threshold, current_moments=(
            denoiser.last.get('site_accepted', True) and denoiser.last.get('unsupported_users', 0) == 0))
        ready = bool(stable >= controls.convergence_patience
            and decision_stable >= controls.decision_stability_window
            and stopping.current_moment_iterations >= controls.convergence_patience)
        check = trial = None
        converged = False
        if due and ready:
            check = stopping.check(iteration, state.mean, state.activity, linear.forward(state.mean), v, out_v,
                noise_energy=noise*y.size, phase_updates_completed=len(steps))
            cycle_converged = bool(check['stop'] and iteration >= last_update+settle)
            # The same output-change thresholds also permit a valid zero step.
            if cycle_converged:
                converged = True
            elif (budget is None or len(steps) < budget) and iteration+settle <= controls.iterations:
                tick = time.perf_counter()
                scalar = float(np.trace(out_v).real/m)
                if not np.allclose(out_v, np.eye(m)*scalar, rtol=1e-10, atol=1e-12*scalar):
                    raise ValueError('Actual isotropic feedback required')
                physical = out*scale
                projected = np.einsum('qkn,kmrn->kqmr', inputs.pilot, physical, optimize=True).reshape(k,q,m*rows)
                projected *= np.exp(1j*beta[:,None]*frames)[:,:,None]
                if local['solver'] == 'local':
                    proposed_beta, angle, trial = update_phase(y, inputs.pilot, out, scalar, noise, beta,
                        radius=local['radius'], curvature_floor=local['curvature_floor'],
                        armijo=local['armijo'], max_backtracks=local['max_backtracks'])
                elif local['solver'] == 'legacy_reduced':
                    proposed_beta, angle, trial = update_reduced_legacy(y, inputs.pilot, out, scalar,
                        noise, beta, solver_kind='legacy_coordinate', fit_offset=True)
                    trial['moved'] = True
                else:
                    raise ValueError('Unknown independent local-phase solver')
                effect = trial_changes(projected, physical, frames, beta, proposed_beta, angle,
                    gram=gram, variance=scalar*scale**2, noise=inputs.noise_variance)
                # Trial effects are diagnostics, not extra stopping conditions.
                controlled_effects = ['prediction_change', 'channel_rotation_change',
                                      'observation_covariance_change']
                small = max(effect[key] for key in controlled_effects) < p['trial_relative_tolerance']
                trial_stable = trial_stable+1 if small and check['passed'] else 0
                trial.update(type='fixed_gaussian_local', after_iteration=iteration,
                    before_slopes=beta.tolist(), after_slopes=proposed_beta.tolist(), effect=effect,
                    channel_rotation=angle.tolist(),
                    trial_passed=bool(small), consecutive_small_trials=trial_stable,
                    controlled_effects=controlled_effects,
                    applied=False, seconds=time.perf_counter()-tick)
                trials.append(trial)
        row = dict(iteration=iteration, convergence_change=change, converged=converged,
            estimate_change=estimate_change, activity_change=activity_change, input_covariance_change=covariance_change,
            stable_iterations=stable, fresh_iterations=fresh, decision_stable_iterations=decision_stable,
            linear_seconds=linear_seconds, linear_reported_variance=raw_power,
            query_variance_ratio=ratio, next_query_variance_ratio=next_ratio,
            em_variance_target=target, em_residual_power=residual, em_posterior_uncertainty=uncertainty,
            em_relative_residual=em_residual, phase_update_due=due, phase_update_eligible=ready,
            phase_updates_completed=len(steps), legacy_converged=legacy, cycle_stopping=check,
            current_phase_trial=None if trial is None else trial['effect'],
            consecutive_small_trials=trial_stable, iterations_since_last_phase_update=iteration-last_update,
            **_message_diagnostics(linear,y,state.mean,v,posterior,fraction,used,noise), **denoiser.last)
        trace.append(row)
        if observer is not None:
            observer(row,state,r,v,prior,prior_cov,out,out_v,posterior)
        old_r, old_raw_v, old_v, old_out, old_out_v = r, raw_v, v, out, out_v
        old_mean, old_p = state.mean.copy(), state.activity.copy()
        if trial is not None and trial['moved'] and not converged and iteration+settle <= controls.iterations:
            beta = proposed_beta.copy()
            old_out = old_out*np.exp(1j*angle)[:,None,None,None]
            old_r = old_raw_v = None
            next_ratio = 1.
            tick = time.perf_counter()
            linear = SpatialLinear(phase_operator(inputs.pilot,beta), m, noise)
            rebuild_seconds = time.perf_counter()-tick
            stable = fresh = decision_stable = 0
            old_decision = None
            denoiser.message_fresh = False
            # Ten current valid moments must now belong to the changed operator.
            stopping.previous_decision = None
            stopping.decision_stable = stopping.current_moment_iterations = 0
            trial.update(applied=True, linear_rebuild_seconds=rebuild_seconds,
                rotated_cached_means=['feedback'], query_damping_history_reset=True,
                raw_variance_history_reset=True, query_variance_ratio_reset=1., stopping_windows_reset=True)
            steps.append(trial)
            last_update = iteration
            row.update(phase_update_index=len(steps), stopping_windows_reset=True)
        elif due:
            row['phase_update_skipped'] = ('stopping_criterion_met' if converged else
                'final_conditional_refinement' if iteration+settle > controls.iterations else
                'phase_update_budget_exhausted' if budget is not None and len(steps) >= budget else
                'zero_phase_step' if trial is not None and not trial['moved'] else 'current_output_windows_not_stable')
        prior, prior_cov, ratio = old_out, old_out_v, next_ratio
        if converged:
            reason = 'CONVERGED'
            break
    conditional_seconds = time.perf_counter()-started-sum(t['seconds'] for t in trials)
    result = SpatialResult(state.mean*scale,state.conditional_mean*scale,state.activity,
        state.spatial_covariance*scale**2,tuple(trace),reason,setup,conditional_seconds)
    return result, beta, steps, trials
