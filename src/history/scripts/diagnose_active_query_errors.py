"""Offline active-user diagnostics. Frozen weights; never perform optimization."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
from pathlib import Path
import time
import numpy as np
import torch
from threadpoolctl import threadpool_limits
import confirm_receiver_covariance as source
from receiver_covariance_candidates import second_moment,compare
from afdm_jadcedd.algorithm.proposed.linear import SpatialLinear

P=source.P; ROOT=source.ROOT; SRC=source.OUT
OUT=ROOT/'runs/active_query_error_diagnosis_20261019'
REPEATS=199

def verify():
    protocol=P.read(SRC/'PROTOCOL.json')
    for path,digest in protocol['source_and_weight_sha256'].items():
        assert P.sha(ROOT/path)==digest,path
    return protocol

def prepare():
    assert not OUT.exists(),'Fresh output required'
    protocol=verify()
    paths=list(SRC.glob('scene*/iteration*/query.npz'))
    assert len(paths)==32
    assets={str(p.resolve()):P.sha(p) for p in paths}
    for name in ('receiver_estimates.npz','ESTIMATION.json','SCORES.json'):
        assets.update({str(p.with_name(name).resolve()):P.sha(p.with_name(name)) for p in paths})
    assets[str(Path(__file__).resolve())]=P.sha(Path(__file__))
    P.save(OUT/'PROTOCOL.json',dict(created_unix=time.time(),source_protocol=protocol,
        assets_sha256=assets,training_started=False,formal_experiments='PAUSED',
        scope='All 32 preserved confirmation snapshots; four physical scenes, two later trajectories per K. Two K20 trajectories replayed for exact algebraic decomposition.',
        monte_carlo_repeats=REPEATS,seed_base=202610196000001,
        shared_covariance_null='Independent proper complex Gaussian columns with receiver lower-half covariance, same number of active users and coordinates. Compare aggregate active covariance shape and trace.',
        per_user_oracle_null='Independent proper complex Gaussian columns with each true-error user second moment. Truth-assisted diagnostic only; conditional on fixed channel. Not a new deployable estimator.',
        metrics=['signal_error_absolute_correlation','cross_row_half_signal_projection_energy_reduction','error_energy_on_top_10_percent_signal_coordinates','standardized_fourth_moment','pseudo_covariance_ratio'],
        statistical_limits='Monte Carlo ranges are model-reference diagnostics, not confidence intervals across physical scenes; 256 channel coordinates are not assumed independent in real data. No multiplicity-corrected population hypothesis test. Oracle fitted second moments are reused in simulation.',
        decision='No claim that covariance alone fixes receiver performance without testing a matched model. Systematic structure beyond independent-column Gaussian covariance is grounds not to assume sufficiency.',
        decomposition='Exact linear self, other-user and combined measurement residual components, including recursive query damping and all covariance cross terms. Measurement residual includes operator mismatch; never label as pure thermal noise.'))
    print('Prepared 32-snapshot diagnostic',flush=True)

def replay():
    protocol=verify(); config=protocol['config']
    torch.set_num_threads(1);torch.backends.cudnn.allow_tf32=False;torch.backends.cuda.matmul.allow_tf32=False
    receiver=P.EstimatedNoiseProposedReceiver(config,device='cuda')
    receiver.base.model.first=source.GraphForward(receiver.base.model.first)
    receiver.base.model.second=source.GraphForward(receiver.base.model.second)
    class Done(Exception):pass
    for scene in (0,1):
        name=f'scene{scene:03d}_users20'; bank=SRC/'bank/development'/name
        manifest=P.read(bank/'READY.json')
        for name0,digest in manifest['sha256'].items():assert P.sha(bank/name0)==digest
        data=P.arrays(bank/'input.npz')
        inp=P.ReceiverInput(data['observation'],data['operator'],float(data['noise_variance']),float(data['activity_prior']))
        wanted={int(p.name[9:]) for p in (SRC/name).glob('iteration*')}
        def observer(row,state,query,cov,prior,prior_cov,*unused):
            iteration=row['iteration']; folder=OUT/'replay'/name/f'iteration{iteration:03d}'
            # No truth is read in this phase. Save all priors to reconstruct damping exactly offline.
            P.save_arrays(folder/'state.npz',dict(query=query,prior=prior,prior_covariance=prior_cov,
                mean=state.mean,conditional_mean=state.conditional_mean,probability=state.activity))
            P.save(folder/'RECORD.json',row)
            if iteration in wanted:
                original=P.arrays(SRC/name/f'iteration{iteration:03d}'/'query.npz')['query']
                relative=float(np.linalg.norm(query-original)/np.linalg.norm(original))
                assert relative<1e-9,(scene,iteration,relative)
                print('Replay',scene,iteration,'query relative difference',relative,flush=True)
            if iteration==max(wanted):raise Done()
        try:
            with threadpool_limits(1):receiver.infer(inp,observer=observer)
        except Done:pass
        P.save(OUT/'replay'/name/'COMPLETE.json',dict(truth_used=False,iterations=max(wanted)))
    verify()
    P.save(OUT/'REPLAY_COMPLETE.json',dict(training_started=False,weights_unchanged=True))

def tr(c):return float(np.trace(c).real)

def metrics(e,h,c):
    # e: [repeats, antenna, row, column]; h: [antenna,row,column].
    z=e.reshape(len(e),e.shape[1],-1);hf=h.reshape(h.shape[0],-1)
    energy=np.sum(abs(z)**2,axis=(1,2));he=np.sum(abs(hf)**2)
    inner=np.einsum('md,bmd->b',hf.conj(),z)
    corr=abs(inner)/np.sqrt(energy*he)
    residual=np.empty_like(e)
    for parity in (0,1):
        ht=h[:,parity::2,:];et=e[:,:,parity::2,:]
        beta=np.sum(ht.conj()[None]*et,axis=(1,2,3))/np.sum(abs(ht)**2)
        residual[:,:,1-parity::2,:]=e[:,:,1-parity::2,:]-beta[:,None,None,None]*h[None,:,1-parity::2,:]
    gain=1-np.sum(abs(residual)**2,axis=(1,2,3))/energy
    selected=np.argsort(np.sum(abs(hf)**2,axis=0))[-int(np.ceil(.1*hf.shape[1])):]
    concentrated=np.sum(abs(z[:,:,selected])**2,axis=(1,2))/energy
    fourth=np.mean(abs(z)**4/(np.diag(c).real[None,:,None]**2),axis=(1,2))/2
    pseudo=np.einsum('bmi,bni->bmn',z,z)/z.shape[-1]
    cov=np.einsum('bmi,bni->bmn',z,z.conj())/z.shape[-1]
    proper=np.linalg.norm(pseudo,axis=(1,2))/np.linalg.norm(cov,axis=(1,2))
    return dict(signal_error_absolute_correlation=corr,
        cross_row_half_signal_projection_energy_reduction=gain,
        error_energy_on_top_10_percent_signal_coordinates=concentrated,
        standardized_fourth_moment=fourth,pseudo_covariance_ratio=proper)

def factor(c):
    ev,u=np.linalg.eigh((c+c.conj().T)/2)
    assert ev.min()>-1e-8*ev.max()
    return u*np.sqrt(np.maximum(ev,0))

def gaussian(rng,c,count,rows=16,columns=16):
    z=(rng.standard_normal((count,len(c),rows*columns))+1j*rng.standard_normal((count,len(c),rows*columns)))/np.sqrt(2)
    return (factor(c)[None]@z).reshape(count,len(c),rows,columns)

def null_summary(values,actual):
    return dict(actual=float(actual),reference_median=float(np.median(values)),
        reference_q025=float(np.quantile(values,.025)),reference_q975=float(np.quantile(values,.975)),
        reference_max=float(np.max(values)),upper_tail_fraction=float((1+np.count_nonzero(values>=actual))/(len(values)+1)))

def statistics():
    protocol=verify();config=protocol['config'];rng=np.random.default_rng(202610196000001)
    records=[]
    for snapshot in sorted(SRC.glob('scene*/iteration*/query.npz')):
        name=snapshot.parent.parent.name;iteration=int(snapshot.parent.name[9:]);scene=int(name[5:8]);users=int(name.split('users')[1])
        truth=P.arrays(SRC/'bank/development'/name/'truth.npz')
        h=truth['channel']/config['scale'];active=np.flatnonzero(truth['activity'])
        q=P.arrays(snapshot)['query'];e=q-h
        estimates=P.arrays(snapshot.with_name('receiver_estimates.npz'));chat=estimates['lower_half_query_second_moment']
        actual_cmp=compare(chat,second_moment(e[active]));nullshape=[];nulltrace=[]
        # Reference finite-sample covariance variability for the actual active group size.
        for _ in range(REPEATS):
            sample=gaussian(rng,chat,len(active))
            cmp=compare(chat,second_moment(sample));nullshape.append(cmp['shape_relative_error']);nulltrace.append(cmp['trace_ratio'])
        peruser=[]
        for k in active:
            ck=second_moment(e[k:k+1]);obs=metrics(e[k:k+1],h[k],ck)
            null=metrics(gaussian(rng,ck,REPEATS),h[k],ck)
            beta=np.vdot(h[k],e[k])/np.sum(abs(h[k])**2)
            peruser.append(dict(user=int(k),error_energy=float(np.sum(abs(e[k])**2)),signal_energy=float(np.sum(abs(h[k])**2)),
                projection_coefficient_real=float(beta.real),projection_coefficient_imag=float(beta.imag),
                mean_energy_fraction=float(np.sum(abs(e[k].reshape(16,-1).mean(axis=1))**2)/tr(ck)),
                covariance_vs_common=compare(chat,ck),
                oracle_per_user_gaussian_reference={key:null_summary(null[key],val[0]) for key,val in obs.items()}))
        row=dict(scene=scene,users=users,iteration=iteration,active_users=active.tolist(),
            common_covariance_active=actual_cmp,
            shared_covariance_gaussian_reference=dict(shape=null_summary(np.array(nullshape),actual_cmp['shape_relative_error']),
                trace=null_summary(np.array(nulltrace),actual_cmp['trace_ratio'])),per_user=peruser)
        P.save(OUT/'statistics'/name/snapshot.parent.name/'SCORES.json',row);records.append(row)
        print('Statistics',len(records),'/32',scene,users,iteration,'active',len(active),'shape',round(actual_cmp['shape_relative_error'],3),flush=True)
    P.save(OUT/'STATISTICS.json',records)

def decomposition():
    config=verify()['config'];results=[]
    for scene in (0,1):
        name=f'scene{scene:03d}_users20';bank=SRC/'bank/development'/name
        data=P.arrays(bank/'input.npz');truth=P.arrays(bank/'truth.npz')
        h=truth['channel']/config['scale'];active=truth['activity'].astype(bool)
        y=data['observation']/config['scale'];noise,_=source.old.estimate_spatial_noise(data['observation']);noise/=config['scale']**2
        linear=SpatialLinear(data['operator'],16,noise);a=linear.a;x=linear.pack(h)
        measurement=y.reshape(len(a),-1)-a@x
        old_components=None;history=[]
        wanted={int(p.name[9:]) for p in (SRC/name).glob('iteration*')}
        for folder in sorted((OUT/'replay'/name).glob('iteration*')):
            state=P.arrays(folder/'state.npz');row=P.read(folder/'RECORD.json');it=row['iteration']
            c=state['prior_covariance'];gamma=tr(c)/16
            assert np.allclose(c,gamma*np.eye(16),rtol=1e-10,atol=1e-12*gamma)
            gain=linear.s*gamma/(noise+linear.s**2*gamma)
            fraction=np.sum(linear.s*gain)/a.shape[1]
            L=(linear.v*(gain/fraction))@linear.uh
            delta=x-linear.pack(state['prior'])
            total=L@(a@delta);selfpart=np.empty_like(delta)
            for k in range(len(h)):
                sl=slice(k*16,(k+1)*16)
                selfpart[sl]=(L[sl]@a[:,sl]-np.eye(16))@delta[sl]
            other=total-delta-selfpart
            raw=np.stack([linear.unpack(selfpart),linear.unpack(other),linear.unpack(L@measurement)])
            components=raw if old_components is None else .9*old_components+.1*raw
            old_components=components
            error=state['query']-h
            relative=float(np.linalg.norm(components.sum(axis=0)-error)/np.linalg.norm(error))
            assert relative<1e-10,(scene,it,relative)
            conditional=state['conditional_mean'];mean=state['mean'];prob=state['probability']
            history.append(dict(iteration=it,query_nmse_db=float(10*np.log10(np.sum(abs(error[active])**2)/np.sum(abs(h)**2))),
                estimate_nmse_db=float(10*np.log10(np.sum(abs(mean-h)**2)/np.sum(abs(h)**2))),
                active_probabilities=prob[active].tolist(),misses=int(np.sum(prob[active]<.5)),false_alarms=int(np.sum(prob[~active]>=.5)),
                active_conditional_nmse_db=float(10*np.log10(np.sum(abs(conditional[active]-h[active])**2)/np.sum(abs(h)**2))),
                query_decomposition_relative_error=relative))
            if it not in wanted:continue
            group={}
            for label,mask in [('active',active),('inactive',~active)]:
                parts=components[:,mask].reshape(3,-1);e0=error[mask].reshape(-1);den=np.vdot(e0,e0).real
                gram=parts.conj()@parts.T/den
                # E = sum_i C_ii + 2*Re(sum_i<j C_ij), with no independence assumption.
                self_removed=error[mask]-components[0,mask]
                group[label]=dict(component_names=['self','other_users','measurement_residual'],
                    energy_gram_real=gram.real.tolist(),diagonal_energy_fractions=np.diag(gram).real.tolist(),
                    cross_energy_fraction=float(gram.real.sum()-np.trace(gram).real),
                    reconstructed_total=float(gram.real.sum()),
                    common_covariance_after_oracle_self_removal=compare(P.arrays(SRC/name/f'iteration{it:03d}'/'receiver_estimates.npz')['lower_half_query_second_moment'],second_moment(self_removed)))
            user=[]
            for k in np.flatnonzero(active):
                he=np.sum(abs(h[k])**2);ee=np.sum(abs(error[k])**2)
                user.append(dict(user=int(k),probability=float(prob[k]),
                    signal_projection_by_component=[dict(real=float((np.vdot(h[k],part[k])/he).real),imag=float((np.vdot(h[k],part[k])/he).imag)) for part in components],
                    component_energy_over_total=[float(np.sum(abs(part[k])**2)/ee) for part in components]))
            result=dict(scene=scene,users=20,iteration=it,algebra_relative_error=relative,groups=group,active_users=user,network=history[-1])
            P.save_arrays(OUT/'decomposition'/name/f'iteration{it:03d}.npz',dict(self_component=components[0],other_users_component=components[1],measurement_residual_component=components[2]))
            results.append(result)
        P.save(OUT/'replay'/name/'HISTORY.json',history)
    P.save(OUT/'DECOMPOSITION.json',results)
    print('Exact decomposition complete',len(results),'snapshots',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','replay','statistics','decomposition']);args=parser.parse_args()
    with threadpool_limits(1):globals()[args.action]()
