"""Receiver-only estimation first; separate truth-assisted covariance scoring."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
from pathlib import Path
import time
import numpy as np
import torch
from scipy.special import expit,logit
from threadpoolctl import threadpool_limits
import validate_message_network_match as previous
from receiver_covariance_candidates import receiver_candidates,second_moment,compare
from afdm_jadcedd.algorithm.baselines.noise_estimation import estimate_spatial_noise
from benchmark_receiver_execution import GraphForward

P=previous.P;ROOT=previous.d.ROOT
OUT=ROOT/'runs/receiver_covariance_20261019'


def run():
    if OUT.exists():raise ValueError('Fresh output required')
    original=P.read(previous.OUT/'PROTOCOL.json')
    for path,digest in original['source_and_weight_sha256'].items():assert P.sha(ROOT/path)==digest,path
    paths=sorted(previous.OUT.glob('scene*/iteration*.npz'));assert len(paths)==26
    sources=dict(original['source_and_weight_sha256'])
    for path in [Path(__file__),ROOT/'scripts/receiver_covariance_candidates.py']:
        sources[str(path.resolve())]=P.sha(path)
    P.save(OUT/'PROTOCOL.json',dict(created_unix=time.time(),source_and_weight_sha256=sources,
        source_snapshots=[str(x) for x in paths],physical_development_scenes=4,first_query_cases=20,later_cases=6,
        training_started=False,formal_experiments='PAUSED',
        estimation_inputs=['observation','operator','estimated thermal noise','activity prior','current query and nominal variance','current frozen-network posterior moments'],
        estimators=['nominal_isotropic','query_second_moment','query_shape_nominal_power','lower_half_query_second_moment',
            'lower_half_shape_nominal_power','observation_shape_nominal_power','posterior_residual_plus_covariance','first_linear_propagation'],
        lower_energy_selection_fraction=.5,correlation_subspace_dimension=3,
        practical_screen=dict(trace_ratio=[.8,1.25],shape_relative_error_max=.25,top3_error_energy_recovery_min=.9,
            direction_gate_applies_when_largest_eigen_fraction_at_least=.15,
            first_query_minimum_passes=18,first_query_total=20,later_minimum_passes=5,later_total=6,
            interpretation='Predeclared engineering screen, not a theorem or statistical confidence bound. First and later stages evaluated separately; no threshold changes.'),
        truth_policy='Estimator module has no truth argument or file access. Covariance estimates and selection indices are saved and hashed BEFORE evaluator loads truth for each case.',
        audit='Evaluate all users, active/inactive groups and even/odd user splits. Splits share observations and are not independent trials.',
        centered_covariance_note='Uncentered error second moment is the target for a zero-mean noise approximation; mean energy fraction is also reported.',
        scope='Feasibility diagnostics only. No correction is installed in the live receiver.'))
    torch.set_num_threads(1);torch.backends.cudnn.allow_tf32=False;torch.backends.cuda.matmul.allow_tf32=False
    config=original['config'];model=P.EstimatedNoiseProposedReceiver(config,device='cuda').base
    model.model.first=GraphForward(model.model.first);model.model.second=GraphForward(model.model.second)
    complete=[]
    for source in paths:
        snapshot=P.arrays(source);query=snapshot['query'];v=float(np.trace(snapshot['covariance']).real/16)
        scene=int(source.parent.name[5:8]);users=int(source.parent.name.split('users')[1]);iteration=int(source.stem[9:])
        bank=previous.d.OUT/'bank/development'/source.parent.name
        manifest=P.read(bank/'READY.json')
        for name,digest in manifest['sha256'].items():assert P.sha(bank/name)==digest
        public=P.arrays(bank/'input.npz');prior=float(public['activity_prior'])
        noise,_=estimate_spatial_noise(public['observation']);noise/=config['scale']**2
        observation=public['observation']/config['scale'];operator=public['operator']
        with threadpool_limits(1):
            moment=model.model.infer(query,np.full(users,v))
            logits=model.evidence.infer(query,np.full(users,v),moment.mean)
        probability=expit(logit(prior)+logits)
        tau=max(float(moment.variance.mean()),config['conditional_variance_floor_checkpoint_normalized'])
        assert tau<v,'Only accepted native same-query moments are supported in this audit'
        mean=probability[:,None,None,None]*moment.mean
        flat=moment.mean.reshape(users,16,-1)
        gram=flat@flat.conj().transpose(0,2,1)/flat.shape[-1]
        posterior=(probability*tau)[:,None,None]*np.eye(16)+(probability*(1-probability))[:,None,None]*gram
        saved=P.read(source.with_suffix('.json'))['native_record']
        assert np.max(abs(probability-np.asarray(saved['probabilities_per_user'])))<1e-8
        kwargs=dict(nominal_variance=v,observation=observation,operator=operator,noise=noise,
            activity_prior=prior,initial_power=config['initialization']['normalized_training_second_moment'],iteration=iteration)
        estimates,selected=receiver_candidates(query,mean=mean,posterior_covariance=posterior,**kwargs)
        halves=[]
        for parity in (0,1):
            train=np.arange(parity,users,2);test=np.arange(1-parity,users,2)
            candidates,indices=receiver_candidates(query[train],mean=mean[train],posterior_covariance=posterior[train],**kwargs)
            halves.append((candidates,train,test,train[indices]))
        folder=OUT/source.parent.name/source.stem
        arrays=dict(estimates)
        for i,(candidates,_,_,_) in enumerate(halves):arrays.update({f'half{i}_{key}':value for key,value in candidates.items()})
        P.save_arrays(folder/'receiver_estimates.npz',arrays)
        P.save(folder/'ESTIMATION.json',dict(truth_used=False,source_sha256=P.sha(source),
            estimate_sha256=P.sha(folder/'receiver_estimates.npz'),selected_lower_energy_users=selected.tolist(),
            split_selected_users=[x[3].tolist() for x in halves],probabilities=probability.tolist()))
        # No truth was loaded above this point for the current case.
        truth=P.arrays(bank/'truth.npz');target=truth['channel']/config['scale'];active=truth['activity'].astype(bool)
        error=query-target;reference=second_moment(error)
        results=[]
        for name,cov in estimates.items():
            groups={label:compare(cov,second_moment(error[index])) for label,index in
                [('all',np.arange(users)),('active',np.flatnonzero(active)),('inactive',np.flatnonzero(~active))] if len(index)}
            splits=[compare(part[0][name],second_moment(error[part[2]])) for part in halves]
            results.append(dict(method=name,groups=groups,split_checks=splits))
        packed=error.transpose(1,0,2,3).reshape(16,-1)
        center=packed.mean(axis=1)
        P.save_arrays(folder/'oracle_reference.npz',dict(error_second_moment=reference,signal_second_moment=second_moment(target)))
        row=dict(scene=scene,users=users,iteration=iteration,results=results,
            selected_active_fraction=float(active[selected].mean()),actual_active_fraction=float(active.mean()),
            error_mean_energy_fraction=float(np.sum(abs(center)**2)/np.trace(reference).real),
            signal_to_error_trace_ratio=float(np.trace(second_moment(target)).real/np.trace(reference).real),
            estimate_sha256=P.sha(folder/'receiver_estimates.npz'),truth_only_in_evaluator=True)
        P.save(folder/'SCORES.json',row);complete.append(row)
        P.save(OUT/'STATUS.json',dict(status='RUNNING',completed=len(complete),expected=26,training_started=False))
        print(len(complete),'/26',scene,users,iteration,[(x['method'],round(x['groups']['all']['shape_relative_error'],2),round(x['groups']['all']['trace_ratio'],2)) for x in results],flush=True)
    for path,digest in sources.items():assert P.sha(ROOT/path)==digest,path
    P.save(OUT/'RESULTS.json',complete)
    P.save(OUT/'STATUS.json',dict(status='COMPLETE',completed=26,expected=26,training_started=False,weights_unchanged=True,formal_experiments='PAUSED'))


if __name__=='__main__':run()
