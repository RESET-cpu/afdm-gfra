"""Observation-only candidate: rank directional starts by finite likelihood.

Independent research implementation. Same covariance model, three coordinate
sweeps and final joint fit as the frozen initializer. A directional derivative
at zero power ranks infinitesimal changes, not finite-power likelihood values.
"""
import time
import numpy as np
from scipy.optimize import minimize
from receiver.du.phase_math import observed_covariances
from receiver.du.phase_initialization import factor_value
from receiver.du.phase_initialization import local_objective
from receiver.du.phase_initialization import directional_phase
from receiver.du.phase_initialization import joint


def maxima(coefficients, previous):
    """All positive stationary maxima of the existing directional polynomial."""
    c=np.asarray(coefficients,complex);orders=np.arange(1,len(c));degree=len(c)-1
    if not np.any(c[1:]):
        return [(float(previous),float(c[0].real))] if c[0].real>0 else []
    polynomial=np.zeros(2*degree+1,complex)
    for order in orders:
        polynomial[degree+order]=order*c[order].conjugate()
        polynomial[degree-order]=-order*c[order]
    roots=np.polynomial.polynomial.polyroots(polynomial/np.max(abs(polynomial)))
    selected=roots[np.isfinite(roots)&(abs(abs(roots)-1)<1e-5)]
    angles=np.angle(selected);exponential=np.exp(-1j*angles[:,None]*orders)
    values=c[0].real+2*np.real(exponential@c[1:])
    second=-2*np.real(exponential@(orders**2*c[1:]))
    result=[]
    for angle,value,derivative in zip(angles,values,second):
        if value<=0 or derivative>1e-10*max(1.,float(np.sum(abs(orders**2*c[1:])))):
            continue
        if any(abs(np.angle(np.exp(1j*(angle-a))))<1e-8 for a,_ in result):
            continue
        result.append((float(angle),float(value)))
    return result


def coordinate(gram,sample,noise,frames,rho,*,sweeps=3,local_maxiter=40):
    k=len(gram);q=int(frames.max()+1);r=len(frames)//q;span=float(max(q-1,1))
    beta=np.zeros(k);power=np.zeros(k);rotated=gram.copy()
    covariance=noise*np.eye(len(frames),dtype=complex)
    initial,_,weight=factor_value(covariance,sample)
    priorities=np.array([directional_phase(g,weight,q,r,0.)[1] for g in gram])
    order=np.argsort(-priorities,kind='stable');records=[];trace=[initial]
    for sweep in range(sweeps):
        for user in order:
            before,_,_=factor_value(covariance,sample)
            base=covariance-power[user]*rotated[user];base=(base+base.conj().T)/2
            zero_value,inverse,weight=factor_value(base,sample)
            cross=np.sum(gram[user].conj().reshape(q,r,q,r)*(-weight).reshape(q,r,q,r),axis=(1,3))
            coefficients=np.array([np.trace(cross,offset=-lag) for lag in range(q)])
            stationary=maxima(coefficients,beta[user]);args=(gram[user],base,sample,frames,float(rho),span)
            starts=[]
            for slope,gain in stationary:
                phi=np.exp(1j*frames*slope);g=gram[user]*phi[:,None]*phi[None,:].conj()
                weighted=inverse@g;curvature=float(np.einsum('ij,ji->',weighted,weighted).real)
                if curvature<=0:continue
                start_power=gain/curvature
                value=local_objective(np.array([start_power/rho,slope*span]),*args)[0]
                starts.append((float(value),slope,float(start_power),'finite_likelihood_start'))
            candidates=[(before,float(beta[user]),float(power[user]),'previous'),
                        (zero_value,float(beta[user]),0.,'zero_power')]
            optimizers=[];optimized_starts=[]
            if power[user]>0:
                optimized_starts.append((before,float(beta[user]),float(power[user]),'current_start'))
            if starts:
                best=min(starts,key=lambda item:item[0]);candidates.append(best);optimized_starts.append(best)
            for value,start_beta,start_power,label in optimized_starts:
                solved=minimize(local_objective,np.array([start_power/rho,start_beta*span]),args=args,
                    jac=True,method='L-BFGS-B',bounds=[(0.,None),(None,None)],
                    options=dict(maxiter=local_maxiter,maxls=30,ftol=1e-11,gtol=1e-7))
                value,_=local_objective(solved.x,*args)
                candidates.append((float(value),float(solved.x[1]/span),float(solved.x[0]*rho),label+'_optimized'))
                optimizers.append(dict(start=label,iterations=int(solved.nit),success=bool(solved.success),
                    value=float(value),message=str(solved.message)))
            value,new_beta,new_power,chosen=min(candidates,key=lambda item:item[0])
            beta[user]=(new_beta+np.pi)%(2*np.pi)-np.pi;power[user]=new_power
            phi=np.exp(1j*frames*beta[user]);rotated[user]=gram[user]*phi[:,None]*phi[None,:].conj()
            covariance=base+power[user]*rotated[user]
            actual,_,_=factor_value(covariance,sample)
            assert actual<=before+1e-8*max(1.,abs(before))
            trace.append(actual)
            records.append(dict(sweep=sweep+1,user=int(user),before=before,after=actual,
                chosen=chosen,power=float(new_power),slope=float(beta[user]),optimizers=optimizers,
                finite_likelihood_starts=[dict(value=v,slope=b,power=p) for v,b,p,_ in starts]))
    return beta,power,dict(objective=trace,coordinates=records,sweeps=sweeps,
        coordinate_order=order.tolist(),local_maxiter=local_maxiter,
        initialization='Zero covariance contribution; compare finite marginal likelihoods at all positive directional stationary maxima, optimize the best start and current point')


def estimate(observation,pilot,noise,moment,rho):
    tick=time.perf_counter();q,_,_=pilot.shape;r=observation.shape[2]
    y=observation.transpose(0,2,1).reshape(q*r,-1);sample=y@y.conj().T/y.shape[1]
    gram=observed_covariances(pilot,moment);frames=np.repeat(np.arange(q),r)
    beta,power,initialization=coordinate(gram,sample,noise,frames,rho)
    initial_beta,initial_power=beta.copy(),power.copy()
    beta,power,optimization=joint(gram,sample,noise,frames,beta,power,rho,maxiter=500)
    return dict(phase_slopes=beta,phase=np.exp(1j*np.arange(q)[:,None]*beta),fitted_powers=power,
        initial_slopes=initial_beta,initial_powers=initial_power,noise_variance_estimate=np.asarray(noise)),dict(
        seconds=time.perf_counter()-tick,method='directional_coordinate_finite_likelihood_candidates',
        initializer=initialization,optimization=optimization,objective='logdet(C)+trace(C^-1 YY^H/M)',
        phase_grid_used=False,sample_bank_used_in_inference=False,physical_path_search_used=False,
        activity_probability_routing=False,phase_update_penalty=False,truth_used=False)
