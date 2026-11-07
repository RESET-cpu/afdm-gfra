"""Experimental phase candidates evaluated by the frozen first-layer classifier.

This is a heuristic AFDM initialization, NOT a calibrated phase likelihood.
No delay/Doppler/angle dictionary, new training or truth inputs are used.
The first-layer Gaussian query is computed exactly for each changed user
block; all other user phase blocks remain at the supplied initialization.
"""
import time
import numpy as np
import torch
from .configuration import CONFIG
from system.receiver.noise_estimation import estimate_spatial_noise


def queries(y, operator, user, betas, variance, noise, log_gamma):
    """Exact complex form of linear_query at zero incoming mean."""
    q,k,n=operator.shape
    raw=operator[:,user]
    # Caller supplies baseline phase separately through operator; remove it
    # from raw before requesting queries if changing an absolute slope.
    choices=np.exp(1j*np.arange(q)[None,:,None]*np.asarray(betas)[:,None,None])*raw[None]
    matrix=operator.reshape(q,-1)
    gram=matrix @ matrix.conj().T-raw @ raw.conj().T
    all_gram=gram[None]+choices @ choices.conj().transpose(0,2,1)
    covariance=all_gram+noise/variance*np.eye(q)[None]
    solved=np.linalg.solve(covariance,np.broadcast_to(y.reshape(q,-1),(len(betas),q,y.shape[1]*y.shape[2])))
    information=np.trace(np.linalg.solve(covariance,all_gram),axis1=1,axis2=2).real/(k*n)
    quotient=np.exp(log_gamma)*(1-information)/information
    r=(1+quotient)[:,None,None]*(choices.conj().transpose(0,2,1) @ solved)
    r=r.reshape(len(betas),n,*y.shape[1:]).transpose(0,2,3,1)
    return r,variance*quotient


def estimate(receiver, observation, pilot, rho, initial_slopes=None, bins=128):
    start=time.perf_counter()
    y,p=np.asarray(observation),np.asarray(pilot)
    q,k,n=p.shape
    if bins<4*q:raise ValueError('Adequate fixed phase grid required')
    baseline=np.zeros(k) if initial_slopes is None else np.asarray(initial_slopes).copy()
    operator=p*np.exp(1j*np.arange(q)[:,None]*baseline)[...,None]
    noise,noise_record=estimate_spatial_noise(y)
    y=y/receiver.scale; noise=noise/receiver.scale**2
    variance=rho*CONFIG['normalized_training_second_moment']
    layer=receiver.model.layers[0]
    log_gamma=float(layer.c_gamma.detach().cpu())
    grid=2*np.pi*np.arange(bins)/bins
    slopes=baseline.copy(); scores=[]
    # Include initial slope for each user in addition to the complete grid.
    with torch.inference_mode():
        for user in range(k):
            candidate=np.r_[grid,baseline[user]]
            r,v=queries(y,operator,user,candidate-baseline[user],variance,noise,log_gamma)
            reals=np.stack((r.real,r.imag),axis=1)
            tensor=torch.as_tensor(reals,dtype=torch.float32,device=receiver.device)
            v_tensor=torch.as_tensor(v,dtype=torch.float32,device=receiver.device)
            values=[]
            for begin in range(0,len(candidate),CONFIG['receiver']['microbatch']):
                x=tensor[begin:begin+CONFIG['receiver']['microbatch']]
                nv=v_tensor[begin:begin+CONFIG['receiver']['microbatch']]
                conditional=x+torch.exp(layer.c_alpha)*nv[:,None,None,None,None]/2*layer.score(x,nv)
                values.append(layer.activity(x,nv,conditional,rho).cpu().numpy())
            logits=np.concatenate(values)
            scores.append(logits)
            slopes[user]=candidate[int(np.argmax(logits))]
    if receiver.device=='cuda':torch.cuda.synchronize()
    slopes=(slopes+np.pi)%(2*np.pi)-np.pi
    return dict(phase_slopes=slopes,phase=np.exp(1j*np.arange(q)[:,None]*slopes),
        candidate_logits=np.stack(scores),initial_slopes=baseline),dict(seconds=time.perf_counter()-start,
        bins=bins,first_layer_blocks_evaluated=k*(bins+1),truth_used_in_inference=False,
        physical_path_search_used=False,noise_estimation=noise_record,
        phase_selection='Maximum first-layer activity logit; not a calibrated phase likelihood',
        other_users='Fixed supplied initialization during all candidate comparisons')
