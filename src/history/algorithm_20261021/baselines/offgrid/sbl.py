"""Wei et al. first-order off-grid SBL, adapted to AFDM with shared MMV variance.

The exponential variance hyperprior, Gaussian posterior and bounded offset
quadratic follow Eqs.(35)-(57). Public noise is supplied. Screening is an
explicit project complexity adaptation and retains candidates for every user.
"""
from dataclasses import dataclass
import numpy as np
from scipy.linalg import cho_factor, cho_solve
from .atoms import (MAX_FREQUENCY, coarse_dictionary, delay_bounds, sensed_atom,
                    stack_observation, reconstruct)


@dataclass(frozen=True)
class Settings:
    iterations: int = 120
    tolerance: float = 1e-4
    rho: float = 1e-3
    candidates_per_user: int = 12
    offset_candidates: int = 48
    offset_sweeps: int = 5
    warmup: int = 5
    doppler_step: float = .5

    def __post_init__(self):
        if (any(type(v) is not int or v < 1 for v in (self.iterations,
                self.candidates_per_user,self.offset_candidates,self.offset_sweeps,self.warmup))
                or not all(np.isfinite(v) and v > 0 for v in
                           (self.tolerance,self.rho,self.doppler_step))):
            raise ValueError("positive finite SBL controls required")


def posterior(a,y,variance,noise):
    """Woodbury posterior without constructing the full dictionary covariance."""
    c = (a*variance)@a.conj().T+noise*np.eye(a.shape[0])
    factor = cho_factor(c,lower=True,check_finite=False)
    inv_a = cho_solve(factor,a,check_finite=False)
    mean = variance[:,None]*(a.conj().T@cho_solve(factor,y,check_finite=False))
    diagonal = variance-variance**2*np.real(np.sum(a.conj()*inv_a,axis=0))
    if diagonal.min() < -1e-8*variance.max():
        raise FloatingPointError("negative posterior variance beyond roundoff")
    return mean,np.maximum(diagonal,0.),inv_a


def variance_update(second_moment,antennas,rho):
    # Positive root of rho*alpha²+M*alpha-sum_m E|x_m|²=0.
    return 2*second_moment/(antennas+np.sqrt(antennas**2+4*rho*second_moment))


def offset_quadratic(a,y,mean,variance,inv_a,derivatives,selected,noise):
    """Expected residual quadratic for increments in selected offsets.

Ordering is [selected delays, selected Dopplers]. This includes posterior
cross-covariances and coupling to unselected columns, not just the mean fit.
"""
    m = y.shape[1]
    sub = variance[selected]
    covariance = np.diag(sub)-(sub[:,None]*(a[:,selected].conj().T@inv_a[:,selected]))*sub[None,:]
    covariance = (covariance+covariance.conj().T)/2
    moment = mean[selected]@mean[selected].conj().T+m*covariance
    # A Sigma[:,S] = sigma² C^{-1} A[:,S] Lambda_S.
    cross = (y-a@mean)@mean[selected].conj().T-m*noise*inv_a[:,selected]*sub
    derivative = np.column_stack([derivatives[0][:,selected],derivatives[1][:,selected]])
    repeated_moment = np.tile(moment,(2,2))
    b = np.real(np.sum(derivative.conj()*np.tile(cross,(1,2)),axis=0))
    q = np.real((derivative.conj().T@derivative)*repeated_moment.T)
    return (q+q.T)/2,b


def bounded_quadratic(q,b,lower,upper,sweeps):
    """Coordinate minimization of d^T Q d - 2 b^T d under box constraints."""
    delta = np.zeros(len(b))
    for _ in range(sweeps):
        for j in range(len(delta)):
            if q[j,j] > 1e-14:
                delta[j] = np.clip((b[j]-q[j]@delta+q[j,j]*delta[j])/q[j,j],lower[j],upper[j])
    return delta


def solve(inputs,settings=Settings()):
    p = np.asarray(inputs.operator,complex)
    y = stack_observation(inputs.observation)
    coarse,norms,coordinates,spacing = coarse_dictionary(p,settings.doppler_step)
    score = np.sum(abs(coarse.conj().T@y)**2,axis=1).reshape(p.shape[1],-1)
    count = min(settings.candidates_per_user,len(coordinates))
    indices = np.concatenate([u*len(coordinates)+np.argsort(-score[u],kind="stable")[:count]
                              for u in range(p.shape[1])])
    users = indices//len(coordinates)
    centers = coordinates[indices%len(coordinates)].copy()
    scales = norms[indices]
    a0 = coarse[:,indices].copy()
    coarse_columns = coarse.shape[1]
    del coarse,score,norms
    derivatives = np.empty((2,a0.shape[0],a0.shape[1]),complex)
    for j,(u,position) in enumerate(zip(users,centers)):
        derivatives[:,:,j] = sensed_atom(p,u,position,True)[1]/scales[j]
    bounds = np.array([delay_bounds(d)-d for d in centers[:,0]])
    lower = np.column_stack([bounds[:,0],np.maximum(-spacing/2,-MAX_FREQUENCY-centers[:,1])])
    upper = np.column_stack([bounds[:,1],np.minimum(spacing/2,MAX_FREQUENCY-centers[:,1])])
    offsets = np.zeros_like(centers)
    noise = float(inputs.noise_variance)
    initial = max((np.sum(abs(y)**2)-y.size*noise)/(y.shape[1]*a0.shape[1]),noise*1e-3)
    variance = np.full(a0.shape[1],initial)
    trace,status = [],"MAX_ITERATIONS"
    for iteration in range(1,settings.iterations+1):
        a = a0+derivatives[0]*offsets[:,0]+derivatives[1]*offsets[:,1]
        mean,diagonal,inv_a = posterior(a,y,variance,noise)
        updated = variance_update(np.sum(abs(mean)**2,axis=1)+y.shape[1]*diagonal,y.shape[1],settings.rho)
        updated = np.maximum(updated,np.finfo(float).eps*max(1.,initial))
        delta_size = 0.
        if iteration > settings.warmup:
            selected = np.argsort(-updated,kind="stable")[:settings.offset_candidates]
            q,b = offset_quadratic(a,y,mean,variance,inv_a,derivatives,selected,noise)
            low = (lower[selected]-offsets[selected]).T.reshape(-1)
            high = (upper[selected]-offsets[selected]).T.reshape(-1)
            delta = bounded_quadratic(q,b,low,high,settings.offset_sweeps).reshape(2,-1).T
            offsets[selected] += delta
            delta_size = float(np.max(abs(delta),initial=0.))
        relative = float(np.linalg.norm(updated-variance)/np.linalg.norm(variance))
        variance = updated
        trace.append(dict(iteration=iteration,variance_relative_change=relative,
                          max_offset_increment=delta_size))
        if iteration > settings.warmup and relative < settings.tolerance and delta_size < settings.tolerance:
            status = "HYPERPARAMETER_CHANGE"
            break
    a = a0+derivatives[0]*offsets[:,0]+derivatives[1]*offsets[:,1]
    mean,_,_ = posterior(a,y,variance,noise)
    positions = centers+offsets
    gains = mean/scales[:,None]
    h = reconstruct(p.shape[1],y.shape[1],users,positions,gains)
    exact_observation = np.einsum("qkn,kmrn->qmr",p,h,optimize=True)
    exact_y = stack_observation(exact_observation)
    return dict(estimate=h,user_ids=users,positions=positions,gains=gains,
        iterations=iteration,stopping_reason=status,trace=trace,coarse_columns=coarse_columns,
        screened_columns=len(indices),residual_energy=float(np.sum(abs(y-exact_y)**2)),
        linearization_relative_error=float(np.linalg.norm(exact_y-a@mean)/max(np.linalg.norm(exact_y),1e-30)))
