"""Candidate: retain antenna covariance while matching pilot phase rotations.

This is an AFDM covariance-matching adaptation, not a published algorithm
name. User covariance factors are PSD rank one, without an angle dictionary.
No delay/Doppler/path atom is formed. Cross-user finite-sample terms and
nonunitary multipath channel effects remain model error.
"""
from dataclasses import asdict, dataclass
import time

import numpy as np
from scipy.optimize import minimize_scalar

from .covariance_phase import covariance_atoms
from system.receiver.noise_estimation import estimate_spatial_noise


@dataclass(frozen=True)
class Controls:
    phase_bins: int = 128
    sweeps: int = 6
    refinement_iterations: int = 25
    whiten: bool = True


def estimate(observation, pilot, controls=Controls()):
    start=time.perf_counter()
    y, p=np.asarray(observation, complex), np.asarray(pilot, complex)
    q,k,_=p.shape
    if y.ndim != 3 or len(y)!=q or controls.phase_bins<4*q:
        raise ValueError('Valid public dimensions and adequate grid required')
    noise, noise_record=estimate_spatial_noise(y)
    flat=y.transpose(1,0,2).reshape(y.shape[1],-1)
    scov=flat @ flat.conj().T/flat.shape[1]
    values,vectors=np.linalg.eigh(scov)
    # MDL gives a spatial rank, never the true active user count.
    rank=max(1,noise_record['estimated_signal_rank'])
    basis=vectors[:,-rank:]
    scales=np.sqrt(np.maximum(values[-rank:]-noise, noise)) if controls.whiten else np.ones(rank)
    white=basis.conj().T/scales[:,None]
    z=np.einsum('am,qmr->qar',white,y,optimize=True)
    target=np.einsum('qar,sbr->qsab',z,z.conj(),optimize=True)/y.shape[-1]
    target[np.arange(q),np.arange(q)]=0
    atoms=covariance_atoms(p)
    norms=np.sum(abs(atoms)**2,axis=(1,2))
    lag=np.arange(q)[:,None]-np.arange(q)[None]
    bins=controls.phase_bins
    beta_grid=2*np.pi*np.arange(bins)/bins
    exponentials=np.exp(-1j*beta_grid[:,None,None]*lag)
    slopes=np.zeros(k); factors=np.zeros((k,rank,rank),complex)
    fitted_atoms=atoms.copy(); prediction=np.zeros_like(target)
    step=2*np.pi/bins

    def matrix_for_beta(atom,residual,beta):
        weights=atom.conj()*np.exp(-1j*lag*beta)
        value=np.einsum('qs,qsab->ab',weights,residual,optimize=True)
        return (value+value.conj().T)/2

    def search(atom,residual,norm,previous):
        coefficients=atom.conj()[:,:,None,None]*residual
        matrices=np.einsum('gqs,qsab->gab',exponentials,coefficients,optimize=True)
        matrices=(matrices+matrices.conj().transpose(0,2,1))/2
        largest=np.linalg.eigvalsh(matrices)[:,-1]
        center=beta_grid[int(np.argmax(largest))]
        def loss(beta):
            return -float(np.linalg.eigvalsh(matrix_for_beta(atom,residual,beta))[-1])
        fitted=minimize_scalar(loss,bounds=(center-step,center+step),method='bounded',
            options={'maxiter':controls.refinement_iterations,'xatol':1e-9})
        beta=min([previous,center,float(fitted.x)],key=loss)
        values,vectors=np.linalg.eigh(matrix_for_beta(atom,residual,beta))
        magnitude=max(float(values[-1]),0.)
        factor=(magnitude/norm)*np.outer(vectors[:,-1],vectors[:,-1].conj())
        return beta,factor,magnitude*magnitude/norm

    initial=[]
    for user in range(k):
        initial.append(search(atoms[user],target,norms[user],0.)[2])
    order=np.argsort(-np.array(initial),kind='stable')
    trace=[float(np.sum(abs(target)**2))]
    for sweep in range(controls.sweeps):
        for user in order:
            if norms[user]<np.finfo(float).eps: continue
            old=fitted_atoms[user,:,:,None,None]*factors[user]
            residual=target-prediction+old
            beta,factor,_=search(atoms[user],residual,norms[user],slopes[user])
            atom=atoms[user]*np.exp(1j*lag*beta)
            new=atom[:,:,None,None]*factor
            # Keep old solution if a global grid plus local refinement misses it.
            if np.sum(abs(residual-new)**2)<=np.sum(abs(residual-old)**2):
                prediction+=new-old
                fitted_atoms[user],factors[user],slopes[user]=atom,factor,beta
        loss=float(np.sum(abs(target-prediction)**2))
        if loss>trace[-1]+1e-10*max(1.,trace[-1]): raise FloatingPointError('Objective increased')
        trace.append(loss)
    slopes=(slopes+np.pi)%(2*np.pi)-np.pi
    return dict(phase_slopes=slopes,phase=np.exp(1j*np.arange(q)[:,None]*slopes),
        spatial_covariance_factors=factors),dict(seconds=time.perf_counter()-start,
        controls=asdict(controls),objective=trace,estimated_spatial_rank=rank,
        noise_estimate=noise,truth_used_in_inference=False,physical_path_search_used=False,
        approximation='Rank-one spatial factor and isotropic input covariance per user')
