"""Independent STMP candidate: check observed activity evidence for phase alternatives."""
import time
import numpy as np
from receiver.frontend.phase_math import observed_covariances
from receiver.frontend.phase_update import update as update_phase
from receiver.frontend.phase_update import objective
from channel.phase import phase_operator
from receiver.stmp.gaussian import gaussian_extrinsic
from receiver.stmp.gaussian import hermitian
from receiver.stmp.iterations import moment_damp
from receiver.stmp.iterations import _iteration_changes
from receiver.stmp.iterations import _stopping_step
from receiver.stmp.iterations import _message_diagnostics
from receiver.stmp.linear import SpatialLinear
from receiver.stmp.records import SpatialResult
from receiver.stmp.phase_output_cycle_stopping import OutputCycleStopping
from receiver.stmp.phase_hypotheses import proposals
from receiver.stmp.phase_hypotheses import select_activity_hypothesis


def infer(inputs,denoiser,*,scale,initial_variance,controls,phase_configuration,
          initial_slopes,training_moment,reference_power,observer=None,decision_threshold=.5):
    if phase_configuration['stopping'].get('allow_original_stopping') is not False:
        raise ValueError('This candidate uses physical output cycle stopping')
    if phase_configuration.get('state_update')!='feedback_and_new_query':
        raise ValueError('Matched fresh queries required after phase changes')
    if phase_configuration.get('phase_update_requires_stable_current_output') is not True:
        raise ValueError('Current conditional output windows must stabilize')
    hc=phase_configuration['phase_hypotheses']
    if (hc['candidates']!='positive_directional_stationary_points'
        or hc['ranking']!='local_activity_normalizer_change' or hc['one_user_per_check'] is not True
        or hc['probability_change_tolerance']!=phase_configuration['stopping']['activity_tolerance']):
        raise ValueError('Expected declared all-user activity hypothesis check')
    if phase_configuration['stopping'].get('requires_current_hypothesis_check') is not True:
        raise ValueError('A current phase hypothesis check is required before stopping')
    controls.validate_stopping()
    if controls.covariance_mode!='isotropic':raise ValueError('Isotropic STMP messages required')
    schedule=phase_configuration['periodic_update'];start,interval=schedule['start'],schedule['interval']
    settle=phase_configuration['minimum_iterations_after_last_update']
    if (any(type(v) is not int or v<1 for v in (start,interval,settle)) or settle>interval or start+settle>controls.iterations):
        raise ValueError('Positive schedule and final conditional refinement required')
    q,k,n=inputs.pilot.shape;m,rows=inputs.observation.shape[1:]
    beta=np.asarray(initial_slopes,float).copy()
    if beta.shape!=(k,) or not np.isfinite(beta).all():raise ValueError('Finite per-user slopes required')
    y=inputs.observation/scale;noise=inputs.noise_variance/scale**2
    physical_y=inputs.observation.transpose(0,2,1).reshape(q*rows,m)
    frames=np.repeat(np.arange(q),rows)
    tick=time.perf_counter()
    gram=observed_covariances(inputs.pilot,np.eye(rows*n))
    hypothesis_gram=observed_covariances(inputs.pilot,training_moment)
    linear=SpatialLinear(phase_operator(inputs.pilot,beta),m,noise)
    setup=time.perf_counter()-tick;started=time.perf_counter()
    prior=np.zeros((k,m,rows,n),complex);prior_cov=np.eye(m)*max(float(initial_variance),1e-12)
    old_r=old_v=old_out=old_out_v=old_mean=old_p=None
    stable=fresh=decision_stable=0;old_decision=None
    trace=[];steps=[];hypothesis_checks=[];reason='MAX_ITERATIONS';last_update=0
    stopping=OutputCycleStopping(phase_configuration['stopping'],minimum_iterations=controls.min_iterations)

    for iteration in range(1,controls.iterations+1):
        tick=time.perf_counter()
        _,_,r,v=linear.update(y,prior,prior_cov)
        linear_seconds=time.perf_counter()-tick
        r,v=moment_damp(old_r,old_v,r,v,controls.damping)
        state=denoiser(r,v)
        posterior=hermitian(state.spatial_covariance.mean(axis=0))
        posterior=np.eye(m)*np.trace(posterior).real/m
        out,out_v,fraction,used=gaussian_extrinsic(state.mean,posterior,r,v,
            controls.variance_fraction_floor,controls.variance_fraction_ceiling)
        out,out_v=moment_damp(old_out,old_out_v,out,out_v,controls.damping)
        if not np.isfinite(out).all() or not np.isfinite(out_v).all():raise FloatingPointError('Invalid feedback')
        changes=_iteration_changes(state,old_mean,old_p,v,old_v)
        change,estimate_change,activity_change,covariance_change=changes
        stable,fresh,decision_stable,old_decision,legacy=_stopping_step(controls,iteration,*changes,
            denoiser.message_fresh,state.activity,decision_threshold,stable,fresh,decision_stable,old_decision)
        legacy=bool(legacy and steps and iteration>=last_update+settle)
        due=iteration>=start and (iteration-start)%interval==0
        stopping.observe_decisions(state.activity,decision_threshold,current_moments=(
            denoiser.last.get('site_accepted',True) and denoiser.last.get('unsupported_users',0)==0))
        ready=bool(stable>=controls.convergence_patience and decision_stable>=controls.decision_stability_window
            and stopping.current_moment_iterations>=controls.convergence_patience)
        check=None;hypothesis=None;selected=None;cycle_converged=False;converged=False
        if due:
            check=stopping.check(iteration,state.mean,state.activity,linear.forward(state.mean),v,out_v,
                noise_energy=noise*y.size,phase_updates_completed=len(steps))
            cycle_converged=bool(check['stop'] and steps and iteration>=last_update+settle)
            # Hidden missed users must be checked before a stable conditional
            # fixed point can stop. The same existing windows govern updates.
            if ready:
                tick=time.perf_counter();samples_before=denoiser.model.samples
                scalar=float(np.trace(out_v).real/m)
                if not np.allclose(out_v,np.eye(m)*scalar,rtol=1e-10,atol=1e-12*scalar):
                    raise ValueError('Actual isotropic feedback required')
                hypothesis=proposals(inputs.pilot,y,noise,out,scalar,beta,training_moment,
                    inputs.activity_prior,reference_power,denoiser.model,denoiser.evidence,proposal_gram=hypothesis_gram)
                selected=select_activity_hypothesis(hypothesis,inputs.activity_prior,hc['probability_change_tolerance'])
                hypothesis.update(iteration=iteration,selected=selected,seconds=time.perf_counter()-tick)
                assert denoiser.model.samples-samples_before==hypothesis['neural_query_count']
                hypothesis_checks.append(hypothesis)
                converged=bool(cycle_converged and selected is None)
        row=dict(iteration=iteration,convergence_change=change,converged=converged,
            estimate_change=estimate_change,activity_change=activity_change,input_covariance_change=covariance_change,
            stable_iterations=stable,fresh_iterations=fresh,decision_stable_iterations=decision_stable,
            linear_seconds=linear_seconds,phase_update_due=due,phase_update_eligible=ready,
            phase_updates_completed=len(steps),legacy_converged=legacy,cycle_stopping=check,
            phase_hypothesis_checked=hypothesis is not None,phase_hypothesis_selected=selected,
            stopping_trigger='physical_outputs_and_current_phase_hypotheses' if converged else None,
            iterations_since_last_phase_update=iteration-last_update,
            **_message_diagnostics(linear,y,state.mean,v,posterior,fraction,used,noise),**denoiser.last)
        trace.append(row)
        if observer is not None:observer(row,state,r,v,prior,prior_cov,out,out_v,posterior)
        old_r,old_v,old_out,old_out_v=r,v,out,out_v
        old_mean,old_p=state.mean.copy(),state.activity.copy()
        if due and ready and not converged and iteration+settle<=controls.iterations:
            tick=time.perf_counter();scalar=float(np.trace(out_v).real/m)
            physical=out*scale
            projected=np.einsum('qkn,kmrn->kqrm',inputs.pilot,physical,optimize=True).reshape(k,q*rows,m)
            projected*=np.exp(1j*beta[:,None]*frames)[:,:,None]
            previous_beta=beta.copy()
            if selected is None:
                beta,angle,step=update_phase(gram,projected,physical_y,inputs.noise_variance,frames,beta,scalar*scale**2)
                step['type']='fixed_gaussian_gem'
                old_out=old_out*np.exp(1j*angle)[:,None,None,None]
                rotated=['feedback']
            else:
                args=(gram,projected,physical_y,inputs.noise_variance,frames,beta,scalar*scale**2)
                before=objective(np.zeros(2*k),*args)[0]
                beta=beta.copy();beta[selected['user']]=selected['slope']
                inc=np.angle(np.exp(1j*(beta-previous_beta)));span=max(float(frames.max()),1.);center=float(frames.max())/2
                after=objective(np.r_[inc*span,center*inc],*args)[0]
                step=dict(type='activity_evidence_phase_hypothesis',before=before,after=after,
                    accepted=True,selected=selected,fixed_gaussian_likelihood_increased=bool(after>before),
                    global_descent_claim=False,channel_rotation=np.zeros(k).tolist(),
                    conditional_quadratic=dict(scope='Not used for this hypothesis step'),
                    hypothesis_check_index=len(hypothesis_checks)-1)
                rotated=[]
            old_r=None
            rebuild=time.perf_counter();linear=SpatialLinear(phase_operator(inputs.pilot,beta),m,noise)
            rebuild_seconds=time.perf_counter()-rebuild
            stable=fresh=decision_stable=0;old_decision=None;denoiser.message_fresh=False
            step['conditional_quadratic'].pop('users',None)
            step.update(after_iteration=iteration,message_variance=scalar*scale**2,
                before_slopes=previous_beta.tolist(),after_slopes=beta.tolist(),seconds=time.perf_counter()-tick,
                linear_rebuild_seconds=rebuild_seconds,rotated_cached_means=rotated,
                physical_query_history_retained=False,query_damping_history_reset=True,stopping_windows_reset=True)
            steps.append(step);last_update=iteration
            row.update(converged=False,phase_update_index=len(steps),stopping_windows_reset=True)
        elif due:
            row['phase_update_skipped']=('stopping_criterion_met' if converged else
                'final_conditional_refinement' if iteration+settle>controls.iterations else 'current_output_windows_not_stable')
        prior,prior_cov=old_out,old_out_v
        if converged:reason='CONVERGED';break
    conditional_seconds=time.perf_counter()-started-sum(s['seconds'] for s in steps)-sum(c['seconds'] for c in hypothesis_checks)
    result=SpatialResult(state.mean*scale,state.conditional_mean*scale,state.activity,state.spatial_covariance*scale**2,
        tuple(trace),reason,setup,conditional_seconds)
    return result,beta,steps,hypothesis_checks
