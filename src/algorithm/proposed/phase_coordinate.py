"""Direct scalar phase minimization with a frozen conditional channel estimate.

The unit-modulus observation quadratic is Shen III-C (48). The per-user
exp(j*q*beta) constraint and scalar coordinate minimization here are our
AFDM adaptation. No delay/Doppler/angle parameters are estimated.
"""
import time
import numpy as np
from scipy.optimize import minimize_scalar
from system.observation import ReceiverInput
from .shen_phase import contributions


def update(observation,pilot,mean,previous,bins=256,sweeps=2):
    z=contributions(pilot,mean)
    q,d,k=z.shape
    y=np.asarray(observation).reshape(q,d)
    beta=np.asarray(previous).copy()
    phase=np.exp(1j*np.arange(q)[:,None]*beta)
    prediction=np.einsum('qdk,qk->qd',z,phase,optimize=True)
    order=np.argsort(-np.sum(abs(z)**2,axis=(0,1)),kind='stable')
    step=2*np.pi/bins; frames=np.arange(q)
    objectives=[float(np.sum(abs(y-prediction)**2))]
    for _ in range(sweeps):
        for user in order:
            old=z[:,:,user]*phase[:,user,None]
            residual=y-prediction+old
            matched=np.sum(z[:,:,user].conj()*residual,axis=1)
            scores=np.fft.fft(matched,n=bins).real
            center=int(np.argmax(scores))*step
            def loss(value):return -float(np.real(np.exp(-1j*frames*value)@matched))
            fit=minimize_scalar(loss,bounds=(center-step,center+step),method='bounded',
                options={'maxiter':40,'xatol':1e-10})
            beta[user]=min([beta[user],center,float(fit.x)],key=loss)
            phase[:,user]=np.exp(1j*frames*beta[user])
            prediction+=z[:,:,user]*phase[:,user,None]-old
        objectives.append(float(np.sum(abs(y-prediction)**2)))
        if objectives[-1]>objectives[-2]+1e-10*max(1.,objectives[-2]):
            raise FloatingPointError('Fixed-channel phase objective increased')
    return (beta+np.pi)%(2*np.pi)-np.pi,objectives


def infer(receiver,observation,pilot,rho,initial_slopes,updates=10,observer=None):
    start=time.perf_counter();observer_seconds=0.
    beta=np.asarray(initial_slopes).copy();q=len(pilot)
    history=[];trace=[]
    for outer in range(updates+1):
        phase=np.exp(1j*np.arange(q)[:,None]*beta)
        history.append(phase.copy())
        values,conditional=receiver.infer(ReceiverInput(observation,pilot*phase[:,:,None],1.,rho))
        if observer:
            t=time.perf_counter();observer(outer,phase,values,conditional);observer_seconds+=time.perf_counter()-t
        if outer<updates:
            beta,objective=update(observation,pilot,values['estimate'],beta)
            trace.append(objective)
    return dict(values,phase=phase,phase_slopes=beta,phase_history=np.stack(history)),dict(
        seconds=time.perf_counter()-start-observer_seconds,updates=updates,conditional_calls=updates+1,
        unfolded_layers_executed=10*(updates+1),fixed_channel_objectives=trace,
        truth_used_in_inference=False,physical_path_search_used=False,
        initialization='Caller-supplied observation-only estimate',final_conditional=conditional)
