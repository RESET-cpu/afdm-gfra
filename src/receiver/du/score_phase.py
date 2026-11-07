"""Experimental phase selection by integrating a pretrained score along beta.

For an AWGN query r at fixed complex variance v, Tweedie's relation gives
grad log[p(r|active)/CN(r;0,vI)] = 2*E[H|r]/v in complex real-gradient
notation. We integrate this directional derivative around the phase circle.
The query's AWGN approximation and a learned, nonconservative score make the
result a candidate score, not an exact marginal likelihood for raw Y.
"""
import time
import numpy as np
import torch
from networks.score import load_direct_checkpoint
from receiver.frontend.noise_estimation import estimate_spatial_noise


class Estimator:
    def __init__(self,checkpoint,device='cuda',bins=128,batch=64):
        self.model,self.metadata=load_direct_checkpoint(checkpoint,device)
        self.scale=self.metadata['global_complex_rms']
        self.device,self.bins,self.batch=device,bins,batch

    def estimate(self,observation,pilot,rho):
        start=time.perf_counter();y=np.asarray(observation)/self.scale;p=np.asarray(pilot)
        q,k,n=p.shape
        noise,_=estimate_spatial_noise(observation);noise/=self.scale**2
        variance=(n/q)*noise+rho*(k*n/q-1)
        grid=2*np.pi*np.arange(self.bins)/self.bins
        phase=np.exp(-1j*grid[:,None]*np.arange(q))
        slopes=np.zeros(k);all_scores=[];circulation=[]
        with torch.inference_mode():
            for user in range(k):
                raw=(n/q)*np.einsum('bq,qn,qmr->bmrn',phase,p[:,user].conj(),y,optimize=True)
                derivative=(n/q)*np.einsum('bq,qn,qmr->bmrn',phase*(-1j*np.arange(q)),p[:,user].conj(),y,optimize=True)
                gradient=[]
                for begin in range(0,self.bins,self.batch):
                    block=raw[begin:begin+self.batch]
                    x=torch.as_tensor(np.stack((block.real,block.imag),axis=1),dtype=torch.float32,device=self.device)
                    v=torch.full((len(block),),variance,dtype=torch.float32,device=self.device)
                    mean=x+v[:,None,None,None,None]/2*self.model(x,v)
                    a=mean.cpu().numpy();complex_mean=a[:,0]+1j*a[:,1]
                    gradient.extend(((2/variance)*(complex_mean.conj()*derivative[begin:begin+self.batch]).real.sum(axis=(1,2,3))).tolist())
                gradient=np.array(gradient)
                frequencies=np.fft.fftfreq(self.bins,d=1/self.bins)
                transform=np.fft.fft(gradient);integral=np.zeros_like(transform)
                np.divide(transform,1j*frequencies,out=integral,where=frequencies!=0)
                score=np.fft.ifft(integral).real
                slopes[user]=grid[int(np.argmax(score))]
                all_scores.append(score)
                circulation.append(float(abs(gradient.mean())/max(np.sqrt(np.mean(gradient**2)),1e-30)))
        if self.device=='cuda':torch.cuda.synchronize()
        slopes=(slopes+np.pi)%(2*np.pi)-np.pi
        return dict(phase_slopes=slopes,phase=np.exp(1j*np.arange(q)[:,None]*slopes),
            integrated_score=np.stack(all_scores),circulation_relative=np.array(circulation)),dict(
            seconds=time.perf_counter()-start,variance=variance,bins=self.bins,
            score_blocks=k*self.bins,physical_path_search_used=False,truth_used_in_inference=False,
            interpretation='Approximate AWGN-query log density ratio integrated along phase; not raw-data likelihood',
            circulation='Mean derivative removed for periodic integration; nonzero circulation measures inconsistency')
