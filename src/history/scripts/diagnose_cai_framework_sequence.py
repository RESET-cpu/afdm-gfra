"""Ordered Gaussian, oracle-activity, and oracle-phase diagnostics. No training."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
from copy import deepcopy
from pathlib import Path
import time
import numpy as np
import torch
from threadpoolctl import threadpool_limits
import evaluate_saved_baseline_inputs as P
from benchmark_receiver_execution import GraphForward

ROOT=P.ROOT
OUT=ROOT/'runs/cai_framework_sequence_20261019'
SOURCE=ROOT/'runs/receiver_covariance_confirmation_20261019'
CASES=[f'scene{s:03d}_users{k}' for s in (0,1) for k in (20,100)]


def prepare():
    assert not OUT.exists(),'Fresh output required'
    old=P.read(SOURCE/'PROTOCOL.json')
    for path,digest in old['source_and_weight_sha256'].items():
        assert P.sha(ROOT/path)==digest,path
    hashes=dict(old['source_and_weight_sha256'])
    hashes[str(Path(__file__).resolve())]=P.sha(Path(__file__))
    for name in CASES:
        bank=SOURCE/'bank/development'/name
        identity=P.read(bank/'READY.json')
        for filename,digest in identity['sha256'].items():
            assert P.sha(bank/filename)==digest
            hashes[str((bank/filename).resolve())]=digest
    P.save(OUT/'PROTOCOL.json',dict(configuration=old['config'],cases=CASES,
        physical_seeds=[202610195000001,202610195000002],training_started=False,
        formal_experiments='PAUSED',source_and_weight_sha256=hashes,
        stages=['gaussian_exact_local_moments','activity_feedback','phase_frontend'],
        gaussian=dict(priors=['iid','correlated_block'],replicates=4,seed=202610198000001,
            damping=.1,maximum=1200,min_iterations=60,relative_change=1e-9,patience=5,
            reference='Exact global Gaussian posterior mean and trace; no activities or networks',
            reference_tolerance=1e-6,scope='Synthetic matched Gaussian prior, not physical AFDM performance'),
        physical=dict(maximum=600,damping=.1,native_stopping_unchanged=True,
            variants=['estimated_phase_learned_activity','estimated_phase_oracle_activity',
                      'oracle_phase_learned_activity','oracle_phase_oracle_activity'],
            common_checkpoints=[1,30,120,300,600],
            noise='Same observation-only estimate in every variant',
            oracle_activity='Fix true activity probabilities to 0/1 in every nonlinear update; retain same channel networks and variance pooling.',
            oracle_phase='Replace estimated slopes by true slopes in pilot*exp(i*q*slope); preserve observations.',
            limits='Two reused independent development seeds, four conditions. Oracle controls are not deployable results. No formal acceptance; budget exhaustion remains failure to establish convergence.'),
        truth_policy='Baseline worker reads no truth until inference ends. Oracle variants read only activity and/or phase slopes before inference; full channel truth only after inference.',
        order='Complete and inspect Gaussian stage before activity; complete activity stage before phase.'))
    print('Prepared ordered diagnostic',flush=True)


def verify():
    p=P.read(OUT/'PROTOCOL.json')
    for path,digest in p['source_and_weight_sha256'].items():
        assert P.sha(ROOT/path)==digest,path
    return p


def gaussian():
    protocol=verify();cfg=protocol['gaussian'];dest=OUT/'stage1_gaussian'
    assert not dest.exists();dest.mkdir()
    rng=np.random.default_rng(cfg['seed']);all_results=[]
    for name in CASES:
        data=P.arrays(SOURCE/'bank/development'/name/'input.npz')
        op=data['operator'];m,k,n=op.shape;a=op.reshape(m,k*n)
        noise=float(data['noise_variance'])/protocol['configuration']['scale']**2
        u,s,vh=np.linalg.svd(a,full_matrices=False)
        for kind in cfg['priors']:
            vector=np.exp(2j*np.pi*np.arange(n)/n)
            cov=np.eye(n) if kind=='iid' else .05*np.eye(n)+.95*np.outer(vector,vector.conj())
            lam,basis=np.linalg.eigh(cov)
            apply=lambda mat,x:np.einsum('ij,kjr->kir',mat,x.reshape(k,n,-1)).reshape(k*n,-1)
            z=(rng.standard_normal((k*n,cfg['replicates']))+1j*rng.standard_normal((k*n,cfg['replicates'])))/np.sqrt(2)
            x=apply((basis*np.sqrt(lam))@basis.conj().T,z)
            y=a@x+np.sqrt(noise/2)*(rng.standard_normal((m,cfg['replicates']))+1j*rng.standard_normal((m,cfg['replicates'])))
            rat=apply(cov,a.conj().T)
            ref=rat@np.linalg.solve(noise*np.eye(m)+a@rat,y)
            ref_var=float(np.trace(cov).real/n-np.trace(np.linalg.solve(noise*np.eye(m)+a@rat,rat.conj().T@rat)).real/(k*n))
            prior=np.zeros_like(x);c=1.;old_r=old_v=old_out=old_c=old_mean=old_tau=None
            stable=clips=0;trace=[];start=time.monotonic()
            for it in range(1,cfg['maximum']+1):
                gain=c*s/(noise+c*s*s);fraction=np.sum(s*gain)/(k*n)
                r=prior+(vh.conj().T*(gain/fraction))@(u.conj().T@(y-a@prior))
                v=c*(1-fraction)/fraction
                if old_r is not None:
                    r=.9*old_r+.1*r;v=.9*old_v+.1*v
                # Exact Gaussian conditional mean/covariance for the declared scalar query.
                filt=lam/(lam+v)
                mean=apply((basis*filt)@basis.conj().T,r)
                tau=float(np.mean(v*filt));raw=tau/v
                clipped=float(np.clip(raw,1e-6,1-1e-6));clips+=int(clipped!=raw)
                used=v*clipped;out_c=1/(1/used-1/v);out=out_c*(mean/used-r/v)
                if old_out is not None:
                    out=.9*old_out+.1*out;out_c=.9*old_c+.1*out_c
                change=None if old_mean is None else float(max(np.linalg.norm(mean-old_mean)/max(np.linalg.norm(mean),1e-15),abs(tau-old_tau)/max(tau,1e-15)))
                stable=stable+1 if it>=cfg['min_iterations'] and change is not None and change<cfg['relative_change'] else 0
                trace.append(dict(iteration=it,relative_change=change,query_variance=v,posterior_variance=tau))
                prior,c=out,out_c;old_r,old_v,old_out,old_c,old_mean,old_tau=r,v,out,out_c,mean,tau
                if stable>=cfg['patience']:break
            error=float(np.linalg.norm(mean-ref)/np.linalg.norm(ref))
            result=dict(case=name,prior=kind,iterations=it,converged=stable>=cfg['patience'],
                exact_posterior_mean_relative_error=error,mean_reference_pass=error<cfg['reference_tolerance'],
                projected_variance=tau,exact_posterior_average_variance=ref_var,
                variance_ratio=tau/ref_var,clipped_iterations=clips,seconds=time.monotonic()-start)
            folder=dest/name/kind;P.save(folder/'REPORT.json',result);P.save(folder/'TRACE.json',trace)
            P.save_arrays(folder/'arrays.npz',dict(estimate=mean,exact_mean=ref,synthetic_truth=x,observation=y,prior_covariance=cov))
            all_results.append(result);print(result,flush=True)
    verify();P.save(dest/'SUMMARY.json',dict(status='COMPLETE',results=all_results,training_started=False))


class OracleEvidence:
    def __init__(self,original,activity):
        self.original=original;self.activity=np.asarray(activity,bool)
        self.noise_support=original.noise_support;self.training_class_prior=original.training_class_prior
    def infer(self,r,variance,mean):
        assert len(r)==len(self.activity)
        return np.where(self.activity,1000.,-1000.)


def physical(stage):
    protocol=verify()
    assert P.read(OUT/'stage1_gaussian/SUMMARY.json')['status']=='COMPLETE'
    if stage==3:assert P.read(OUT/'stage2_activity/SUMMARY.json')['status']=='COMPLETE'
    dest=OUT/('stage2_activity' if stage==2 else 'stage3_phase')
    assert not dest.exists();dest.mkdir()
    variants=protocol['physical']['variants'][:2] if stage==2 else protocol['physical']['variants'][2:]
    config=deepcopy(protocol['configuration'])
    assert config['ep']['iterations']==600 and config['ep']['damping']==.1
    torch.set_num_threads(1);torch.backends.cudnn.allow_tf32=False;torch.backends.cuda.matmul.allow_tf32=False
    receiver=P.EstimatedNoiseProposedReceiver(config,device='cuda')
    receiver.base.model.first=GraphForward(receiver.base.model.first)
    receiver.base.model.second=GraphForward(receiver.base.model.second)
    original=receiver.base.evidence;results=[]
    for name in CASES:
        bank=SOURCE/'bank/development'/name
        for variant in variants:
            folder=dest/name/variant;data=P.arrays(bank/'input.npz')
            oracle_activity=variant.endswith('oracle_activity');oracle_phase=variant.startswith('oracle_phase')
            # Oracle interface exposes only authorized diagnostic variables, never channel values.
            activity=slopes=None
            if oracle_activity or oracle_phase:
                with np.load(bank/'truth.npz') as t:
                    if oracle_activity:activity=t['activity'].astype(bool)
                    if oracle_phase:slopes=t['phase_slopes'].copy()
            receiver.base.evidence=OracleEvidence(original,activity) if oracle_activity else original
            if oracle_phase:
                with np.load(bank/'public.npz') as public:
                    pilot=public['pilot'].copy()
                data['operator']=pilot*np.exp(1j*np.arange(len(pilot))[:,None,None]*slopes[None,:,None])
            inputs=P.ReceiverInput(data['observation'],data['operator'],float(data['noise_variance']),float(data['activity_prior']))
            P.save(folder/'INPUT_POLICY.json',dict(oracle_activity=oracle_activity,oracle_phase=oracle_phase,
                supplied_channel_truth=False,operator_sha256=P.array_sha256(data['operator']),scope='Diagnostic only'))
            prefix=[];start=time.monotonic();rows=[]
            def observer(row,state,query,cov,*unused):
                it=row['iteration']
                rows.append({key:row[key] for key in ['iteration','converged','estimate_change','activity_change','query_variance_min','raw_site_residual','site_accepted','projected_eigenvalues']})
                if oracle_activity:assert np.array_equal(state.activity,activity.astype(float))
                snap=SOURCE/name/f'iteration{it:03d}'/'query.npz'
                if variant=='estimated_phase_learned_activity' and snap.exists():
                    expected=P.arrays(snap)['query'];difference=float(np.linalg.norm(query-expected)/max(np.linalg.norm(expected),1e-15))
                    assert difference<1e-9,(name,it,difference)
                    prefix.append(dict(iteration=it,relative_difference=difference))
                if it in protocol['physical']['common_checkpoints'] or row['converged']:
                    P.save_arrays(folder/'checkpoints'/f'iteration{it:04d}.npz',dict(estimate=state.mean*config['scale'],
                        conditional_matrix=state.conditional_mean*config['scale'],probabilities=state.activity,
                        activity_decision=state.activity>=.5,query=query,covariance=cov))
                if it==1 or it%50==0 or row['converged']:
                    P.save(OUT/'STATUS.json',dict(status='RUNNING',stage=stage,case=name,variant=variant,iteration=it,
                        completed=len(results),expected=8,elapsed_case_seconds=time.monotonic()-start,training_started=False))
                    print(stage,name,variant,it,round(time.monotonic()-start,1),flush=True)
            with threadpool_limits(1):pred,record=receiver.infer(inputs,observer=observer)
            # Override generic wrapper provenance: these variants deliberately use oracle variables.
            record['truth_used_in_inference']=oracle_activity or oracle_phase
            record['oracle_activity']=oracle_activity;record['oracle_phase']=oracle_phase
            if oracle_activity:
                record['activity_evidence']='oracle_activity';record['classifier_loaded']=True
                record['classifier_output_used']=False
            P.save_arrays(folder/'prediction.npz',pred);P.save(folder/'record.json',record)
            P.save(folder/'PREFIX.json',prefix)
            truth=P.arrays(bank/'truth.npz');checkpoints=[]
            for path in sorted((folder/'checkpoints').glob('*.npz')):
                arrays=P.arrays(path);target=truth['channel']/config['scale'];active=truth['activity'].astype(bool)
                error=arrays['query']-target
                beta=np.sum(target.conj()*error,axis=(1,2,3))/np.maximum(np.sum(abs(target)**2,axis=(1,2,3)),1e-30)
                checkpoints.append(dict(iteration=int(path.stem[9:]),metrics=P.score_arrays(arrays,truth),
                    active_signal_error_projection_real=beta[active].real.tolist(),
                    active_query_mse_over_declared_variance=float(np.mean(abs(error[active])**2)/(np.trace(arrays['covariance']).real/16))))
            result=dict(case=name,variant=variant,metrics=P.score_arrays(pred,truth),iterations=record['iterations'],
                converged=record['converged'],seconds=record['seconds'],stopping_reason=record['stopping_reason'],
                oracle_activity=oracle_activity,oracle_phase=oracle_phase,checkpoints=checkpoints,
                original_prefix_checks=prefix,noise_variance_estimate=record['noise_variance_estimate'])
            P.save(folder/'SUMMARY.json',result);results.append(result)
            print('FINISHED',name,variant,result['iterations'],result['metrics']['nmse_db'],flush=True)
            del truth
    receiver.base.evidence=original
    verify();P.save(dest/'SUMMARY.json',dict(status='COMPLETE',results=results,training_started=False))
    P.save(OUT/'STATUS.json',dict(status='STAGE_COMPLETE',stage=stage,completed=8,training_started=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','gaussian','activity','phase'])
    action=parser.parse_args().action
    if action=='prepare':prepare()
    elif action=='gaussian':gaussian()
    else:physical(2 if action=='activity' else 3)
