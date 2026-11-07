"""Gaussian E-step and generalized M-step for each fixed neural message.

Full projected cross-user covariance is retained. This guarantees descent
only within the fixed Gaussian message, not across the learned network.
See paper/docs/PHASE_MESSAGE_GEM.md (Shen III-C and Dempster et al. Sec. 3).
"""
import numpy as np
from scipy.linalg import cho_factor
from scipy.linalg import cho_solve
from scipy.linalg import solve_triangular
from receiver.du.phase_math import polynomial_coefficients
from receiver.du.phase_math import quadratic_objective
from receiver.du.phase_math import stationary_maximum


def objective(x, gram, projected, y, noise, frames, beta, gamma):
    k=len(gram); span=max(float(frames.max()),1.); center=float(frames.max())/2
    increment=x[:k]/span; offset=x[k:]
    rotation=np.exp(1j*(increment[:,None]*(frames-center)+offset[:,None]))
    mean=projected*rotation[:,:,None]
    residual=y-mean.sum(axis=0)
    phi=np.exp(1j*(beta+increment)[:,None]*frames)
    rotated=gram*phi[:,:,None]*phi[:,None,:].conj()
    covariance=noise*np.eye(len(frames))+gamma*rotated.sum(axis=0)
    factor=cho_factor(covariance,lower=True,check_finite=False)
    v=cho_solve(factor,residual,check_finite=False)
    inverse=cho_solve(factor,np.eye(len(frames)),check_finite=False)
    m=y.shape[1]
    value=float(2*np.log(np.diag(factor[0]).real).sum()+np.vdot(residual,v).real/m)
    weight=inverse-v@v.conj().T/m
    slope=gamma/span*np.einsum('ji,kij->k',weight,1j*(frames[:,None]-frames[None,:])*rotated).real
    slope-=2/m/span*np.einsum('im,kim->k',v.conj(),1j*(frames-center)[None,:,None]*mean).real
    angle=-2/m*np.einsum('im,kim->k',v.conj(),1j*mean).real
    return value,np.r_[slope,angle]


def update_rotations(beta,gram,b,max_sweeps=10,relative_tolerance=1e-7):
    q,k=b.shape;frames=np.arange(q)
    beta=np.asarray(beta,float).copy();offset=np.zeros(k)
    phase=np.exp(1j*np.arange(q)[:, None]*np.asarray(beta)[None]);trace=[quadratic_objective(phase,gram,b)];details=[]
    off_diagonal=np.array(gram,copy=True);ix=np.arange(k);off_diagonal[:,ix,ix]=0
    normalization=max(1.,float(np.sum(abs(off_diagonal))+2*np.sum(abs(b))))
    order=np.argsort(-np.diagonal(gram,axis1=1,axis2=2).real.sum(axis=0),kind='stable')
    gains=[];converged=False
    for sweep in range(max_sweeps):
        for user in order:
            u=b[:,user]-np.einsum('ql,ql->q',gram[:,user],phase,optimize=True)+gram[:,user,user]*phase[:,user]
            previous=float(np.vdot(phase[:,user],u).real)
            slope,squared,count=stationary_maximum(polynomial_coefficients(u),beta[user])
            correlation=np.exp(-1j*frames*slope)@u
            delta=float(np.angle(correlation));value=float(abs(correlation))
            assert value>=previous-1e-9*max(1.,abs(previous))
            if value>=previous:
                beta[user],offset[user]=slope,delta
                phase[:,user]=np.exp(1j*(frames*slope+delta))
            details.append(dict(sweep=sweep,user=int(user),linear_term_before=previous,
                linear_term_after=max(value,previous),stationary_roots=count))
        trace.append(quadratic_objective(phase,gram,b))
        assert trace[-1]<=trace[-2]+1e-9*max(1.,abs(trace[-2]))
        gains.append((trace[-2]-trace[-1])/normalization)
        if sweep>=1 and gains[-1]<=relative_tolerance:
            converged=True;break
    beta=(beta+np.pi)%(2*np.pi)-np.pi
    return beta,offset,dict(sweeps=len(gains),maximum_sweeps=max_sweeps,
        relative_tolerance=relative_tolerance,normalization=normalization,normalized_gains=gains,
        converged=converged,objectives=trace,users=details,
        convergence_scope='Fixed conditional quadratic decrease only; not a phase-accuracy or global-optimum guarantee')


def update(gram,projected,y,noise,frames,beta,gamma):
    # The caller supplies isotropic message covariance, gamma equals v.
    k,length,_=gram.shape;q=int(frames.max()+1);r=length//q;m=y.shape[1]
    phi=np.exp(1j*beta[:,None]*frames)
    covariance=noise*np.eye(length)+gamma*(gram*phi[:,:,None]*phi[:,None,:].conj()).sum(axis=0)
    factor=cho_factor(covariance,lower=True,check_finite=False)
    residual=y-projected.sum(axis=0);v=cho_solve(factor,residual,check_finite=False)
    cross=gamma*gram*phi[:,None,:].conj()
    mean=projected*phi[:,:,None].conj()+cross@v
    lower=np.tril(factor[0]);whitened=np.empty_like(cross)
    for user in range(k):
        whitened[user]=solve_triangular(lower,cross[user].conj().T,lower=True,check_finite=False).conj().T
    diagonal=np.diagonal(gram,axis1=1,axis2=2).real.reshape(k,q,r).sum(axis=2)
    quadratic=np.empty((q,k,k),complex);linear=np.empty((q,k),complex)
    for frame in range(q):
        sl=slice(frame*r,(frame+1)*r);means=mean[:,sl].reshape(k,r*m);weights=whitened[:,sl].reshape(k,r*length)
        covariance_trace=gamma*np.diag(diagonal[:,frame])-weights.conj()@weights.T
        quadratic[frame]=means.conj()@means.T+m*covariance_trace
        quadratic[frame]=(quadratic[frame]+quadratic[frame].conj().T)/2
        linear[frame]=means.conj()@y[sl].reshape(-1)
    new_beta,angle,m_step=update_rotations(beta,quadratic,linear,max_sweeps=10,relative_tolerance=1e-7)
    increment=np.angle(np.exp(1j*(new_beta-beta)));span=max(float(q-1),1.);center=(q-1)/2
    args=(gram,projected,y,noise,frames,beta,gamma)
    before=objective(np.zeros(2*k),*args)[0]
    x=np.r_[increment*span,angle+center*increment]
    after,gradient=objective(x,*args)
    # For this fixed Gaussian model, the conditional quadratic reduction must
    # imply a nonincreasing marginal negative log likelihood.
    assert after<=before+1e-8*max(1.,abs(before)),(before,after)
    return new_beta,angle,dict(before=before,after=after,trial_value=after,accepted=True,
        trace=[before,after],iterations=m_step['sweeps'],success=m_step['converged'],
        message='Fixed conditional quadratic relative tolerance' if m_step['converged'] else 'Coordinate sweep cap',
        gradient_max=float(np.max(abs(gradient))),unwrapped_increment=increment.tolist(),
        centered_offset=(angle+center*increment).tolist(),channel_rotation=angle.tolist(),covariance_scale=float(gamma),
        conditional_quadratic=m_step,posterior_mean_norm=float(np.linalg.norm(mean)),
        posterior_covariance='Full Gaussian cross-user projected covariance; no diagonal-user approximation')
