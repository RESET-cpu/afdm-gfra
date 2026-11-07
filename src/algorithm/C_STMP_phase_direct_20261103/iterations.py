"""Alternate unchanged C-STMP messages and low-dimensional phase updates.

Compare early updates and updates admitted after conditional stability.
The selected schedule is declared by each independent candidate configuration.
"""
import time
import numpy as np
from system.phase import phase_operator
from algorithm.C_STMP_variance_em_20261025.iterations import expected_residual_power
from algorithm.STMP.gaussian import gaussian_extrinsic, hermitian
from algorithm.STMP.iterations import moment_damp, _iteration_changes, _stopping_step, _message_diagnostics
from algorithm.STMP.linear import SpatialLinear
from algorithm.STMP.records import SpatialResult
from algorithm.STMP.phase_output_cycle_stopping import OutputCycleStopping
from .phase import update


def infer(inputs, denoiser, *, scale, initial_variance, controls, policy,
          initial_slopes, observer=None, decision_threshold=.5):
    controls.validate_stopping()
    if controls.covariance_mode != 'isotropic':
        raise ValueError('The exact Q-dimensional reduction requires isotropic feedback')
    q, k, n = inputs.pilot.shape
    m, rows = inputs.observation.shape[1:]
    beta = np.array(initial_slopes, float, copy=True)
    y, noise = inputs.observation/scale, inputs.noise_variance/scale**2
    tick = time.perf_counter()
    linear = SpatialLinear(phase_operator(inputs.pilot, beta), m, noise)
    setup = time.perf_counter()-tick
    prior = np.zeros((k,m,rows,n), complex)
    prior_cov = np.eye(m)*initial_variance
    old_r = old_raw_v = old_v = old_out = old_out_v = old_mean = old_p = None
    ratio = 1.
    stable = fresh = decision_stable = 0
    old_decision = None
    trace, trials, steps = [], [], []
    cycle = None
    if policy.get('stopping_mode') == 'cycle':
        cycle = OutputCycleStopping(dict(relative_tolerance=.05,activity_tolerance=.001,
            consecutive_cycles=1,require_stable_decisions=10,
            comparison='completed_phase_update_cycles',require_raw_site_residual=False),
            minimum_iterations=controls.min_iterations)
    reason, last_update = 'MAX_ITERATIONS', -controls.iterations
    started = time.perf_counter()
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
        next_ratio = (1-controls.damping)*ratio+controls.damping*target/raw_power
        out, out_v, fraction, used = gaussian_extrinsic(state.mean, posterior, r, v,
            controls.variance_fraction_floor, controls.variance_fraction_ceiling)
        out, out_v = moment_damp(old_out, old_out_v, out, out_v, controls.damping)
        if not np.isfinite(out).all() or not np.isfinite(out_v).all():
            raise FloatingPointError('Nonfinite feedback')
        change, estimate_change, activity_change, covariance_change = _iteration_changes(state, old_mean, old_p, v, old_v)
        if covariance_change is not None:
            covariance_change = max(covariance_change, em_residual)
            change = max(change, em_residual)
        stable, fresh, decision_stable, old_decision, conditional_converged = _stopping_step(
            controls, iteration, change, estimate_change, activity_change, covariance_change,
            denoiser.message_fresh, state.activity, decision_threshold, stable, fresh, decision_stable, old_decision)
        due = iteration >= policy['start'] and (iteration-policy['start'])%policy['interval']==0
        trial = None
        check = None
        converged = False
        eligible = True
        if cycle is not None:
            cycle.observe_decisions(state.activity,decision_threshold,current_moments=(
                denoiser.last.get('site_accepted',True) and denoiser.last.get('unsupported_users',0)==0))
            eligible = bool(stable >= controls.convergence_patience
                and decision_stable >= controls.decision_stability_window
                and cycle.current_moment_iterations >= controls.convergence_patience)
            if due and eligible:
                check = cycle.check(iteration,state.mean,state.activity,linear.forward(state.mean),v,out_v,
                    noise_energy=noise*y.size,phase_updates_completed=len(steps))
                converged = bool(check['stop'] and steps and iteration-last_update >= policy['settle_iterations'])
        room_for_update = cycle is None or iteration+policy['settle_iterations'] <= controls.iterations
        if due and eligible and not converged and room_for_update:
            scalar = float(np.trace(out_v).real/m)
            new_beta, angle, trial = update(y, inputs.pilot, out, scalar, noise, beta,
                sweeps=policy['sweeps'], fit_offset=policy['fit_offset'],
                solver_kind=policy.get('solver','coordinate'),guard=policy.get('guard',False))
            small = max(trial['prediction_change'], trial['covariance_change']) <= policy['phase_tolerance']
            if cycle is None:
                converged = bool(conditional_converged and small
                    and iteration-last_update >= policy['settle_iterations'])
            trial.update(after_iteration=iteration, before_slopes=beta.tolist(), after_slopes=new_beta.tolist(),
                small=small, applied=False)
            trials.append(trial)
        row = dict(iteration=iteration, convergence_change=change, estimate_change=estimate_change,
            activity_change=activity_change, input_covariance_change=covariance_change,
            stable_iterations=stable, fresh_iterations=fresh, decision_stable_iterations=decision_stable,
            linear_seconds=linear_seconds, linear_reported_variance=raw_power,
            query_variance_ratio=ratio, next_query_variance_ratio=next_ratio,
            em_variance_target=target, em_relative_residual=em_residual,
            phase_update_due=due, phase_update_eligible=eligible, phase_cycle_check=check,
            phase_updates_completed=len(steps), converged=converged,
            **_message_diagnostics(linear,y,state.mean,v,posterior,fraction,used,noise), **denoiser.last)
        trace.append(row)
        if observer is not None:
            observer(row,state,r,v,prior,prior_cov,out,out_v,posterior)
        old_r, old_raw_v, old_v, old_out, old_out_v = r, raw_v, v, out, out_v
        old_mean, old_p = state.mean.copy(), state.activity.copy()
        # Tiny proposals are checked but not committed, so conditional messages
        # can settle. The last saved channel always corresponds to saved beta.
        if trial is not None and (cycle is not None or not trial['small']) and not converged and iteration < controls.iterations:
            beta = new_beta
            old_out = old_out*np.exp(1j*angle)[:,None,None,None]
            old_r = old_raw_v = None
            if policy.get('reset_variance_ratio', True):
                next_ratio = 1.
            tick = time.perf_counter()
            linear = SpatialLinear(phase_operator(inputs.pilot, beta),m,noise)
            trial.update(applied=True, linear_rebuild_seconds=time.perf_counter()-tick)
            stable = fresh = decision_stable = 0
            old_decision = None
            denoiser.message_fresh = False
            if cycle is not None:
                cycle.previous_decision = None
                cycle.decision_stable = cycle.current_moment_iterations = 0
            steps.append(trial)
            last_update = iteration
        row['applied_next_query_variance_ratio'] = next_ratio
        row['query_variance_ratio_reset'] = bool(trial is not None and trial['applied']
            and policy.get('reset_variance_ratio', True))
        prior, prior_cov, ratio = old_out, old_out_v, next_ratio
        if converged:
            reason = 'CONVERGED'
            break
    return SpatialResult(state.mean*scale,state.conditional_mean*scale,state.activity,
        state.spatial_covariance*scale**2,tuple(trace),reason,setup,time.perf_counter()-started), beta, steps, trials
