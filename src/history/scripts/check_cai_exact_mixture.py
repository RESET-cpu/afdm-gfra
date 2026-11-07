"""Small exact Bernoulli-Gaussian posterior control; no networks or physical claims."""
import os
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[name]='1'
from itertools import product
from pathlib import Path
import numpy as np
from scipy.special import expit,logsumexp
import diagnose_cai_framework_sequence as d


def main():
    d.verify();P=d.P;out=d.OUT/'exact_mixture_supplement';assert not out.exists()
    protocol=dict(users=6,columns=16,replicates=2,activity_prior=.25,noise_variances=[.1,1.],
        priors=['iid','correlated_block'],seed=202610199000001,damping=.1,maximum=1200,
        stop='Both relative mean and scalar variance changes below 1e-9 for five steps after iteration 60',
        reference='Enumerate all 64 activity masks with exact Gaussian likelihood and conditional moments',
        selection='First six user blocks from each of the two K20 public development operators, before seeing synthetic data',
        scope='Synthetic matched prior and noise. Activity and Gaussian local moments exact. Global reference is diagnostic only; cannot certify physical K100 performance.',
        purpose='Gaussian fixed-point mean agreement does not validate nonlinear activity mixture projection',
        script_sha256=P.sha(Path(__file__)),training_started=False)
    P.save(out/'PROTOCOL.json',protocol)
    rng=np.random.default_rng(protocol['seed']);results=[];k=6;n=16;rep=2;rho=.25
    masks=np.asarray(list(product((0,1),repeat=k)))
    for scene in (0,1):
        data=P.arrays(d.SOURCE/'bank/development'/f'scene{scene:03d}_users20'/'input.npz')
        a=data['operator'][:,:k,:].reshape(16,k*n);u,s,vh=np.linalg.svd(a,full_matrices=False)
        for kind in protocol['priors']:
            vec=np.exp(2j*np.pi*np.arange(n)/n)
            cov=np.eye(n) if kind=='iid' else .05*np.eye(n)+.95*np.outer(vec,vec.conj())
            lam,basis=np.linalg.eigh(cov)
            apply=lambda matrix,x:np.einsum('ij,kjr->kir',matrix,x.reshape(k,n,-1)).reshape(k*n,-1)
            z=(rng.normal(size=(k*n,rep))+1j*rng.normal(size=(k*n,rep)))/np.sqrt(2)
            active=rng.random(k)<rho
            truth=apply((basis*np.sqrt(lam))@basis.conj().T,z)*np.repeat(active,n)[:,None]
            unit_noise=(rng.normal(size=(16,rep))+1j*rng.normal(size=(16,rep)))/np.sqrt(2)
            for noise in protocol['noise_variances']:
                y=a@truth+np.sqrt(noise)*unit_noise
                means=[];vars=[];logs=[]
                for mask in masks:
                    rat=apply(cov,a.conj().T)*np.repeat(mask,n)[:,None]
                    sy=noise*np.eye(16)+a@rat;solved=np.linalg.solve(sy,y)
                    mean=rat@solved
                    variance=(mask.sum()*np.trace(cov).real-np.trace(np.linalg.solve(sy,rat.conj().T@rat)).real)/(k*n)
                    logs.append(mask.sum()*np.log(rho)+(k-mask.sum())*np.log1p(-rho)-rep*np.linalg.slogdet(sy)[1]-np.vdot(y,solved).real)
                    means.append(mean);vars.append(variance)
                weight=np.exp(np.asarray(logs)-logsumexp(logs));assert abs(weight.sum()-1)<1e-12
                exact=np.einsum('s,sij->ij',weight,means);exact_p=weight@masks
                exact_v=float(weight@(np.asarray(vars)+np.mean(abs(np.asarray(means))**2,axis=(1,2)))-np.mean(abs(exact)**2))
                assert exact_v>0
                prior=np.zeros_like(truth);c=rho;prev=None;stable=clips=0;trace=[]
                for it in range(1,1201):
                    gain=c*s/(noise+c*s*s);fraction=np.sum(s*gain)/(k*n)
                    query=prior+(vh.conj().T*(gain/fraction))@(u.conj().T@(y-a@prior));v=c*(1-fraction)/fraction
                    if prev is not None:query=.9*prev['query']+.1*query;v=.9*prev['v']+.1*v
                    rotated=np.einsum('ij,kjr->kir',basis.conj().T,query.reshape(k,n,rep))
                    conditional=apply((basis*(lam/(lam+v)))@basis.conj().T,query)
                    log_ratio=-rep*np.sum(np.log1p(lam/v))+np.sum(abs(rotated)**2*(1/v-1/(lam+v))[None,:,None],axis=(1,2))
                    prob=expit(np.log(rho/(1-rho))+log_ratio)
                    mean=conditional*np.repeat(prob,n)[:,None]
                    tau=float(np.mean(prob*np.mean(v*lam/(lam+v))+prob*(1-prob)*np.mean(abs(conditional.reshape(k,n,rep))**2,axis=(1,2))))
                    frac=tau/v;used=np.clip(frac,1e-6,1-1e-6);clips+=int(frac!=used)
                    feedback_c=v*used/(1-used);feedback=feedback_c*(mean/(v*used)-query/v)
                    if prev is not None:feedback=.9*prev['feedback']+.1*feedback;feedback_c=.9*prev['c']+.1*feedback_c
                    change=None if prev is None else max(np.linalg.norm(mean-prev['mean'])/max(np.linalg.norm(mean),1e-15),abs(tau-prev['tau'])/max(tau,1e-15),np.max(abs(prob-prev['prob'])))
                    stable=stable+1 if it>=60 and change is not None and change<1e-9 else 0
                    trace.append(dict(iteration=it,relative_change=change,query_variance=v,probability=prob.tolist()))
                    prior,c=feedback,feedback_c;prev=dict(query=query,v=v,feedback=feedback,c=c,mean=mean,tau=tau,prob=prob)
                    if stable>=5:break
                row=dict(scene=scene,prior=kind,noise_variance=noise,synthetic_active=active.tolist(),iterations=it,
                    converged=stable>=5,clipped_iterations=clips,
                    exact_posterior_mean_relative_error=float(np.linalg.norm(mean-exact)/max(np.linalg.norm(exact),1e-15)),
                    normalized_excess_posterior_squared_error=float(np.mean(abs(mean-exact)**2)/exact_v),
                    activity_probability_max_abs_error=float(np.max(abs(prob-exact_p))),
                    approximate_probability=prob.tolist(),exact_probability=exact_p.tolist(),variance_ratio=tau/exact_v)
                folder=out/f'scene{scene:03d}_{kind}_noise{noise}'
                P.save(folder/'REPORT.json',row);P.save(folder/'TRACE.json',trace)
                P.save_arrays(folder/'arrays.npz',dict(estimate=mean,exact_mean=exact,truth=truth,observation=y,mask_posterior_probability=weight))
                results.append(row);print(row,flush=True)
    d.verify();P.save(out/'SUMMARY.json',dict(status='COMPLETE',results=results,training_started=False))


if __name__=='__main__':main()
