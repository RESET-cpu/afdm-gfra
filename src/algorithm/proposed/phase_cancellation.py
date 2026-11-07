"""Development candidate: conditional means, cancellation, and phase hypotheses.

Only a pretrained first-order effective-channel denoiser is used to assess
the hypotheses. This operation is explicitly heuristic, not exact EM or a
calibrated marginal likelihood. No physical delay/Doppler/angle search.
"""
import time
import numpy as np
import torch
from system.observation import ReceiverInput
from system.receiver.noise_estimation import estimate_spatial_noise
from .shen_phase import contributions


def infer(receiver,pretrained,observation,pilot,rho,initial_slopes,rounds=4,bins=128,observer=None):
    start=time.perf_counter();observer_seconds=0.
    y,p=np.asarray(observation),np.asarray(pilot)
    q,k,n=p.shape;beta=np.asarray(initial_slopes).copy()
    scale=pretrained.scale
    noise,_=estimate_spatial_noise(y)
    grid=2*np.pi*np.arange(bins)/bins
    phase_history=[];trace=[]
    for outer in range(rounds+1):
        phase=np.exp(1j*np.arange(q)[:,None]*beta)
        phase_history.append(phase.copy())
        values,record=receiver.infer(ReceiverInput(y,p*phase[:,:,None],1.,rho))
        if observer:
            t=time.perf_counter();observer(outer,phase,values,record);observer_seconds+=time.perf_counter()-t
        if outer==rounds:break
        z=contributions(p,values['estimate']).reshape(q,*y.shape[1:],k)
        fitted=np.einsum('qmrk,qk->qmr',z,phase,optimize=True)
        new_beta=beta.copy();scores=[]
        with torch.inference_mode():
            for user in range(k):
                residual=(y-fitted+z[:,:,:,user]*phase[:,user,None,None])/scale
                choices=np.r_[grid,beta[user]]
                signed=np.exp(-1j*choices[:,None]*np.arange(q))
                raw=(n/q)*np.einsum('bq,qn,qmr->bmrn',signed,p[:,user].conj(),residual,optimize=True)
                variance=max(n/q*noise/scale**2,n/q*float(np.mean(abs(residual)**2))-1.,.001)
                all_scores=[]
                for begin in range(0,len(choices),pretrained.batch):
                    r=raw[begin:begin+pretrained.batch]
                    x=torch.as_tensor(np.stack((r.real,r.imag),axis=1),dtype=torch.float32,device=receiver.device)
                    v=torch.full((len(r),),variance,dtype=torch.float32,device=receiver.device)
                    mean=x+v[:,None,None,None,None]/2*pretrained.model(x,v)
                    a=mean.cpu().numpy();mean=a[:,0]+1j*a[:,1]
                    response=np.einsum('bq,qn,bmrn->bqmr',signed[begin:begin+pretrained.batch].conj(),p[:,user],mean,optimize=True)
                    # Unit-gain posterior mean, no truth-dependent gain fitting.
                    gain=(2*(response.conj()*residual).real-abs(response)**2).sum(axis=(1,2,3))
                    all_scores.extend(gain.tolist())
                all_scores=np.array(all_scores)
                selected=int(np.argmax(all_scores));new_beta[user]=choices[selected]
                scores.append(dict(user=user,selected=selected,improvement=float(all_scores[selected]-all_scores[-1])))
        beta=(new_beta+np.pi)%(2*np.pi)-np.pi
        trace.append(scores)
    return dict(values,phase=phase,phase_slopes=beta,phase_history=np.stack(phase_history)),dict(
        seconds=time.perf_counter()-start-observer_seconds,rounds=rounds,bins=bins,
        conditional_calls=rounds+1,unfolded_layers_executed=(rounds+1)*10,
        pretrained_score_blocks=rounds*k*(bins+1),truth_used_in_inference=False,
        physical_path_search_used=False,trace=trace,final_conditional=record,
        objective='Per-user residual fit of one pretrained Tweedie mean; heuristic variance')
