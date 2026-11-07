"""Independent runtime candidate; identical phase objective and solver settings.

Uses the retained training second moment only for initialization. Numerical
budgets are unchanged: 3 coordinate sweeps, 40 local / 500 joint iterations.
See paper/docs/PHASE_MESSAGE_GEM.md for equations and limitations.
"""
import time
import numpy as np
from scipy.linalg import cho_factor
from scipy.linalg import cho_solve
from scipy.optimize import minimize
from receiver.du.phase_math import observed_covariances
from receiver.du.phase_math import stationary_maximum


class _MemoizedObjective:
    """Reuse only an exactly repeated optimizer parameter vector."""
    def __init__(self, function, args):
        self.function, self.args = function, args
        self.x = self.result = None
        self.evaluations = self.hits = 0

    def __call__(self, x):
        if self.x is not None and np.array_equal(x, self.x):
            self.hits += 1
        else:
            value, gradient = self.function(x, *self.args)
            self.x = np.array(x, copy=True)
            self.result = float(value), np.array(gradient, copy=True)
            self.evaluations += 1
        return self.result[0], self.result[1].copy()


def factor_value(covariance,sample,*,weight_required=True):
    factor=cho_factor(covariance,lower=True,check_finite=False)
    inverse=cho_solve(factor,np.eye(len(covariance)),check_finite=False)
    value=float(2*np.log(np.diag(factor[0]).real).sum()+np.einsum('ij,ji->',inverse,sample).real)
    if not weight_required:
        return value,inverse,None
    weight=inverse-inverse@sample@inverse
    return value,inverse,(weight+weight.conj().T)/2


def objective(parameters,gram,sample,noise,frames,power_scale,phase_scale):
    k=len(gram);power=parameters[:k]*power_scale;beta=parameters[k:]/phase_scale
    phi=np.exp(1j*beta[:,None]*frames)
    rotated=gram*phi[:,:,None]*phi[:,None,:].conj()
    covariance=noise*np.eye(len(frames))+np.einsum('k,kij->ij',power,rotated)
    value,inverse,weight=factor_value(covariance,sample)
    power_gradient=power_scale*np.einsum('ji,kij->k',weight,rotated).real
    lag=frames[:,None]-frames[None,:]
    phase_gradient=power/phase_scale*np.einsum('ji,kij->k',weight,1j*lag*rotated).real
    return value,np.r_[power_gradient,phase_gradient]


def joint(gram,sample,noise,frames,beta,power,rho,maxiter=500):
    k=len(gram);scale=float(rho);span=float(max(frames.max(),1))
    x=np.r_[power/scale,beta*span];args=(gram,sample,noise,frames,scale,span)
    evaluate=_MemoizedObjective(objective,args)
    trace=[evaluate(x)[0]]
    solved=minimize(evaluate,x,jac=True,method='L-BFGS-B',
        bounds=[(0.,None)]*k+[(None,None)]*k,
        options=dict(maxiter=maxiter,maxls=40,ftol=1e-11,gtol=1e-7),
        callback=lambda current:trace.append(evaluate(current)[0]))
    value,gradient=evaluate(solved.x);trace.append(value)
    assert np.max(np.diff(trace),initial=0.)<=1e-8*max(1.,abs(trace[0]))
    projected=gradient.copy()
    projected[:k]=np.where((solved.x[:k]==0)&(gradient[:k]>0),0.,gradient[:k])
    return (solved.x[k:]/span+np.pi)%(2*np.pi)-np.pi,solved.x[:k]*scale,dict(
        objective=trace,iterations=int(solved.nit),evaluations=int(solved.nfev),
        success=bool(solved.success),message=str(solved.message),
        projected_gradient_max=float(np.max(abs(projected))),power_scale=scale,phase_scale=span,
        actual_objective_evaluations=evaluate.evaluations,reused_objective_evaluations=evaluate.hits)


def directional_phase(gram,weight,q,r,previous):
    # -dL/dgamma = <G(beta), -W>. Expand over frame lags.
    cross=np.sum(gram.conj().reshape(q,r,q,r)*(-weight).reshape(q,r,q,r),axis=(1,3))
    coefficients=np.array([np.trace(cross,offset=-order) for order in range(q)])
    return stationary_maximum(coefficients,previous)


def local_objective(x,gram,base,sample,frames,power_scale,phase_scale):
    gamma=x[0]*power_scale;beta=x[1]/phase_scale
    phi=np.exp(1j*frames*beta);rotated=gram*phi[:,None]*phi[None,:].conj()
    value,_,weight=factor_value(base+gamma*rotated,sample)
    derivative=1j*(frames[:,None]-frames[None,:])*rotated
    return value,np.array([power_scale*np.einsum('ji,ij->',weight,rotated).real,
        gamma/phase_scale*np.einsum('ji,ij->',weight,derivative).real])


def coordinate(gram,sample,noise,frames,rho,*,sweeps=3,local_maxiter=40):
    k=len(gram);q=int(frames.max()+1);r=len(frames)//q;span=float(max(q-1,1))
    beta=np.zeros(k);power=np.zeros(k);rotated=gram.copy()
    covariance=noise*np.eye(len(frames),dtype=complex)
    initial,_,weight=factor_value(covariance,sample)
    priorities=np.array([directional_phase(g,weight,q,r,0.)[1] for g in gram])
    order=np.argsort(-priorities,kind='stable');records=[];trace=[initial]
    for sweep in range(sweeps):
        for user in order:
            before=trace[-1]  # Same unchanged covariance as the preceding completed coordinate.
            base=covariance-power[user]*rotated[user]
            base=(base+base.conj().T)/2
            zero_value,inverse,weight=factor_value(base,sample)
            proposal,score,root_count=directional_phase(gram[user],weight,q,r,beta[user])
            phi=np.exp(1j*frames*proposal);proposal_gram=gram[user]*phi[:,None]*phi[None,:].conj()
            weighted=inverse@proposal_gram
            positive_curvature=float(np.einsum('ij,ji->',weighted,weighted).real)
            # This is a positive quadratic scale for the starting power, not
            # a new penalty or a statistical threshold. Final choice uses L.
            proposed_power=max(0.,score)/positive_curvature if positive_curvature>0 else 0.
            candidates=[(before,float(beta[user]),float(power[user]),'previous')]
            candidates.append((zero_value,float(proposal),0.,'zero_power_direction'))
            starts=[]
            if power[user]>0:starts.append((power[user],beta[user],'current_start'))
            if proposed_power>0:starts.append((proposed_power,proposal,'directional_start'))
            optimizers=[]
            for start_power,start_beta,label in starts:
                args=(gram[user],base,sample,frames,float(rho),span)
                evaluate=_MemoizedObjective(local_objective,args)
                solved=minimize(evaluate,np.array([start_power/rho,start_beta*span]),
                    jac=True,method='L-BFGS-B',bounds=[(0.,None),(None,None)],
                    options=dict(maxiter=local_maxiter,maxls=30,ftol=1e-11,gtol=1e-7))
                value,_=evaluate(solved.x)
                candidates.append((float(value),float(solved.x[1]/span),float(solved.x[0]*rho),label))
                optimizers.append(dict(start=label,iterations=int(solved.nit),success=bool(solved.success),
                    value=float(value),message=str(solved.message),
                    actual_objective_evaluations=evaluate.evaluations,reused_objective_evaluations=evaluate.hits))
            # At zero power beta is unidentified. Break exact likelihood ties
            # with the best direction for entering the nonnegative domain.
            if power[user]==0 and zero_value==before:candidates[0]=candidates[1]
            value,new_beta,new_power,chosen=min(candidates,key=lambda item:item[0])
            beta[user]=(new_beta+np.pi)%(2*np.pi)-np.pi;power[user]=new_power
            phi=np.exp(1j*frames*beta[user]);rotated[user]=gram[user]*phi[:,None]*phi[None,:].conj()
            covariance=base+power[user]*rotated[user]
            actual,_,_=factor_value(covariance,sample,weight_required=False)
            assert actual<=before+1e-8*max(1.,abs(before))
            trace.append(actual)
            records.append(dict(sweep=sweep+1,user=int(user),before=before,after=actual,
                null_power_negative_derivative=float(score),proposal_slope=float(proposal),
                starting_power=float(proposed_power),chosen=chosen,stationary_roots=root_count,
                power=float(new_power),slope=float(beta[user]),optimizers=optimizers))
    return beta,power,dict(objective=trace,coordinates=records,sweeps=sweeps,
        coordinate_order=order.tolist(),local_maxiter=local_maxiter,
        initialization='Zero covariance contribution; phase from exact marginal power directional derivative')


def estimate(observation, pilot, noise, moment, rho):
    """Accepted directional coordinate initialization followed by joint fitting."""
    start = time.perf_counter()
    q, _, _ = pilot.shape
    r = observation.shape[2]
    y = observation.transpose(0, 2, 1).reshape(q*r, -1)
    sample = y@y.conj().T/y.shape[1]
    gram = observed_covariances(pilot, moment)
    frames = np.repeat(np.arange(q), r)
    beta, power, initialization = coordinate(gram, sample, noise, frames, rho, sweeps=3, local_maxiter=40)
    initial_beta, initial_power = beta.copy(), power.copy()
    beta, power, optimization = joint(gram, sample, noise, frames, beta, power, rho, maxiter=500)
    return dict(phase_slopes=beta, phase=np.exp(1j*np.arange(q)[:, None]*beta),
        fitted_powers=power, initial_slopes=initial_beta, initial_powers=initial_power,
        noise_variance_estimate=np.asarray(noise)), dict(seconds=time.perf_counter()-start,
        method='directional_coordinate', initializer=initialization, optimization=optimization,
        objective='logdet(C)+trace(C^-1 YY^H/M)', phase_grid_used=False,
        sample_bank_used_in_inference=False, physical_path_search_used=False,
        activity_probability_routing=False, phase_update_penalty=False)

