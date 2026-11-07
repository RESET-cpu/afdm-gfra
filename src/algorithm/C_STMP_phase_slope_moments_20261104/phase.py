"""Keep exp(j*q*beta[k]); compare Gaussian and receiver working moments.

Reuses the existing polynomial stationary-point solver, not a delay/Doppler
grid. The denoiser working distribution is the independent-user Bernoulli-
Gaussian approximation already documented in PHASE_EM_20261103.md. Only the
selected frozen expectation is guaranteed to decrease.
"""
import time
import numpy as np
from algorithm.proposed.phase_math import stationary_maximum, quadratic_objective
from algorithm.C_STMP_phase_shen_frames_20261103.moments import conditional_projected_moments, marginal_value
from algorithm.C_STMP_phase_conditional_schedule_20261104.phase import signal_change


def denoiser_quadratic(observation, pilot, state):
    """Exact projected moments for the declared independent-user BG model.

    Given activity, each vector has mean conditional_mean and covariance
    I_(R*N) tensor conditional_spatial_covariance. Activity is shared across
    ALL coefficients of a user; its rank-one covariance must not be discarded.
    """
    p = np.asarray(state.activity, float)
    mu = np.asarray(state.mean, complex)
    h = np.asarray(state.conditional_mean, complex)
    cov = np.asarray(state.conditional_spatial_covariance, complex)
    q,k,n = pilot.shape
    m,r = observation.shape[1:]
    if mu.shape != (k,m,r,n) or h.shape != mu.shape or p.shape != (k,) or cov.shape != (k,m,m):
        raise ValueError('Incompatible receiver moments')
    if not all(np.isfinite(x).all() for x in (mu,h,p,cov)) or np.any((p<0)|(p>1)):
        raise ValueError('Finite moments and activity probabilities required')
    if not np.allclose(mu,p[:,None,None,None]*h,rtol=1e-10,atol=1e-12):
        raise ValueError('Use the activity-weighted joint mean exactly once')
    if not np.allclose(cov,cov.conj().transpose(0,2,1),rtol=1e-10,atol=1e-12):
        raise ValueError('Hermitian conditional spatial covariance required')
    if np.linalg.eigvalsh(cov).min() < -1e-10*max(1.,float(abs(cov).max())):
        raise ValueError('Positive conditional spatial covariance required')
    active_z = np.einsum('qkn,kmrn->qkmr',pilot,h,optimize=True).reshape(q,k,-1)
    z = p[None,:,None]*active_z
    gram = np.einsum('qkd,qld->qkl',z.conj(),z,optimize=True)
    matched = np.einsum('qkd,qd->qk',z.conj(),observation.reshape(q,-1),optimize=True)
    uncertainty = p[None,:]*(1-p[None,:])*np.sum(abs(active_z)**2,axis=-1)
    uncertainty += p[None,:]*r*np.sum(abs(pilot)**2,axis=-1)*np.trace(cov,axis1=1,axis2=2).real[None,:]
    gram[:,np.arange(k),np.arange(k)] += uncertainty
    return gram,matched,z,dict(moment_scope='Independent-user Bernoulli-Gaussian receiver working distribution',
        activity_applied_once=True,shared_activity_rank_one_covariance_retained=True,
        cross_user_covariance_retained=False,projected_uncertainty=float(uncertainty.sum()))


def gaussian_quadratic(observation,pilot,mean,variance,noise,phase):
    z,cov,details = conditional_projected_moments(observation,pilot,mean,variance,noise,phase)
    q,d = z.shape[1:];k = z.shape[0]
    gram = np.einsum('kqd,lqd->qkl',z.conj(),z,optimize=True)+d*cov.conj()
    gram = (gram+gram.conj().transpose(0,2,1))/2
    matched = np.einsum('kqd,qd->qk',z.conj(),observation.reshape(q,d),optimize=True)
    return gram,matched,z.transpose(1,0,2),details


def rotations(beta,gram,matched):
    """One fixed-order coordinate sweep, preserving the common-slope model."""
    beta = np.array(beta,float,copy=True)
    q,k = matched.shape
    if beta.shape != (k,) or gram.shape != (q,k,k):
        raise ValueError('Incompatible slope quadratic')
    if not all(np.isfinite(x).all() for x in (beta,gram,matched)):
        raise ValueError('Finite slope quadratic required')
    if not np.allclose(gram,gram.conj().transpose(0,2,1),rtol=1e-10,atol=1e-12):
        raise ValueError('Hermitian quadratic required')
    frames = np.arange(q)
    phase = np.exp(1j*frames[:,None]*beta)
    before = quadratic_objective(phase,gram,matched)
    roots,changes = 0,[]
    for user in range(k):
        c = matched[:,user]-np.einsum('qj,qj->q',gram[:,user,:],phase)+gram[:,user,user]*phase[:,user]
        coefficients = c/2
        coefficients[0] = c[0].real
        proposed,_,count = stationary_maximum(coefficients,beta[user])
        candidate = np.exp(1j*frames*proposed)
        change = float(-2*np.vdot(candidate-phase[:,user],c).real)
        if change < 0:
            beta[user],phase[:,user] = proposed,candidate
            changes.append(change)
        else:
            changes.append(0.)
        roots += count
    after = quadratic_objective(phase,gram,matched)
    tolerance = 1e-10*max(1.,abs(before),float(np.sum(abs(gram))),float(np.sum(abs(matched))))
    if after > before+tolerance:
        raise FloatingPointError('Common-slope coordinate update increased its fixed expectation')
    return beta,phase,dict(conditional_before=before,conditional_after=after,
        conditional_objective_increased=bool(after>before),
        conditional_objective_materially_increased=bool(after>before+tolerance),
        conditional_roundoff_tolerance=tolerance,coordinate_objective_changes=changes,
        stationary_roots=roots,coordinate_sweeps=1,coordinate_order='fixed user index',
        free_phase_parameters=k if q>1 else 0,fit_channel_rotation=False,
        method='Common-slope coordinate minimization using polynomial stationary points',
        guarantee='Nonincrease of the selected frozen working-distribution objective only')


def update(observation,pilot,mean,variance,noise,beta,state,*,moment_source):
    started = time.perf_counter()
    current = np.exp(1j*np.arange(len(pilot))[:,None]*beta)
    gg,bg,zg,dg = gaussian_quadratic(observation,pilot,mean,variance,noise,current)
    gd,bd,zd,dd = denoiser_quadratic(observation,pilot,state)
    if moment_source=='gaussian':gram,matched,details = gg,bg,dg
    elif moment_source=='denoiser':gram,matched,details = gd,bd,dd
    else:raise ValueError('Explicit gaussian or denoiser moment source required')
    proposed_beta,proposed,solver = rotations(beta,gram,matched)
    before = marginal_value(observation,pilot,mean,variance,noise,current)
    after = marginal_value(observation,pilot,mean,variance,noise,proposed)
    tolerance = 1e-8*max(1.,abs(before),abs(after))
    if moment_source=='gaussian' and after>before+tolerance:
        raise FloatingPointError('Fixed Gaussian marginal failed its descent check')
    comparison = {}
    for label,g,b in [('gaussian',gg,bg),('denoiser',gd,bd)]:
        f0,f1 = quadratic_objective(current,g,b),quadratic_objective(proposed,g,b)
        comparison[label] = dict(before=f0,after=f1,change=f1-f0)
    gap = zg-zd
    increments = np.angle(proposed*current.conj())
    return proposed_beta,proposed,dict(**solver,moment_source=moment_source,moments=details,
        before=before,after=after,marginal_objective_increased=bool(after>before),
        marginal_objective_materially_increased=bool(after>before+tolerance),marginal_roundoff_tolerance=tolerance,
        fixed_objectives_for_same_proposal=comparison,
        projected_mean_relative_gap=float(np.linalg.norm(gap)/max(np.linalg.norm(zd),np.finfo(float).tiny)),
        observation_prediction_gap=float(np.linalg.norm(np.sum(current[:,:,None]*gap,axis=1))/max(np.linalg.norm(observation),np.finfo(float).tiny)),
        phase_effect=signal_change(current,proposed,gram,noise*np.asarray(observation).size),
        maximum_frame_increment=float(abs(increments).max()),rms_frame_increment=float(np.sqrt(np.mean(increments**2))),
        unit_modulus_error=float(np.max(abs(abs(proposed)-1))),reference_frame_error=float(np.max(abs(proposed[0]-1))),
        before_slopes=np.asarray(beta).tolist(),after_slopes=proposed_beta.tolist(),
        before_phase_real=current.real.tolist(),before_phase_imag=current.imag.tolist(),
        after_phase_real=proposed.real.tolist(),after_phase_imag=proposed.imag.tolist(),
        seconds=time.perf_counter()-started)
