"""Frozen covariance estimators on new physical seeds, without retraining."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
from pathlib import Path
import time
import numpy as np
import torch
from threadpoolctl import threadpool_limits
import validate_receiver_covariance as old
from receiver_covariance_candidates import receiver_candidates,second_moment,compare
from benchmark_receiver_execution import GraphForward

P=old.P;ROOT=old.ROOT
OUT=ROOT/'runs/receiver_covariance_confirmation_20261019'
BASE=202610195000001
METHODS=['nominal_isotropic','query_second_moment','lower_half_query_second_moment','first_linear_propagation']


def prepare():
    if OUT.exists():raise ValueError('Fresh confirmation output required')
    prior_protocol=P.read(old.OUT/'PROTOCOL.json')
    sources=dict(prior_protocol['source_and_weight_sha256'])
    for path,digest in sources.items():assert P.sha(ROOT/path)==digest,path
    sources[str(Path(__file__).resolve())]=P.sha(Path(__file__))
    config=P.read(old.previous.OUT/'PROTOCOL.json')['config']
    training=set()
    def collect(value):
        if isinstance(value,dict):
            for key,item in value.items():
                if key=='scene_seeds':training.update(item)
                else:collect(item)
        elif isinstance(value,list):
            for item in value:collect(item)
    collect(P.read(ROOT/config['prior_definition']))
    excluded=set(training)
    for base,count in [(202610191000001,4),(202610192000001,12),(202610193000001,12),
        (202610172000001,500),(202610180100001,500),(202610180200001,500),
        (202610180300001,500),(202610180400001,500),(202610180500001,500),(202610180600001,500)]:
        excluded.update(range(base,base+count))
    assert not set(range(BASE,BASE+4))&excluded
    P.save(OUT/'PROTOCOL.json',dict(created_unix=time.time(),config=config,seed_base=BASE,
        physical_scenes=4,users=[20,40,60,80,100],first_query_cases=20,later_query_cases=12,
        trajectory_cases=[dict(scene=s,users=k) for s in (0,1) for k in (20,60,100)],
        snapshots='Iteration 1; trajectory cases also iteration 30 and 120, or native convergence if before 120. Do not force iterations after convergence.',
        methods=METHODS,source_and_weight_sha256=sources,training_started=False,formal_experiments='PAUSED',
        independent_seed_check=dict(overlap=False,training_validation_seeds=len(training),excluded_seeds=len(excluded)),
        primary_estimators=['query_second_moment','lower_half_query_second_moment'],
        practical_screen=prior_protocol['practical_screen']|dict(first_query_minimum_passes=18,first_query_total=20,later_minimum_passes=11,later_total=12),
        interpretation='Same predeclared per-case thresholds, at least 90% separately for first and later queries. Four independent scene seeds; no population guarantee.',
        truth_policy='Prepare process generates the banks. Run process reads public inputs and saves covariance estimates before loading truth. Estimator function has no truth inputs.',
        lower_half_selection='Lowest observed user query energies, fixed fraction 0.5; never selected by true activity'))
    d=old.previous.d;d.OUT=OUT;d.SEEDS=dict(development=BASE)
    for scene in range(4):
        for users in (20,40,60,80,100):
            d.bank('development',scene,users)
    P.save(OUT/'STATUS.json',dict(status='PREPARED',completed=0,expected=32,training_started=False))
    print('Prepared new seeds',BASE,'through',BASE+3,flush=True)


def run():
    protocol=P.read(OUT/'PROTOCOL.json');config=protocol['config']
    for path,digest in protocol['source_and_weight_sha256'].items():assert P.sha(ROOT/path)==digest,path
    torch.set_num_threads(1);torch.backends.cudnn.allow_tf32=False;torch.backends.cuda.matmul.allow_tf32=False
    receiver=P.EstimatedNoiseProposedReceiver(config,device='cuda')
    receiver.base.model.first=GraphForward(receiver.base.model.first);receiver.base.model.second=GraphForward(receiver.base.model.second)
    all_scores=[]
    class PrefixComplete(Exception):pass
    for scene in range(4):
        for users in (20,40,60,80,100):
            bank=OUT/'bank/development'/f'scene{scene:03d}_users{users}'
            manifest=P.read(bank/'READY.json')
            for name,digest in manifest['sha256'].items():assert P.sha(bank/name)==digest
            data=P.arrays(bank/'input.npz')
            inputs=P.ReceiverInput(data['observation'],data['operator'],float(data['noise_variance']),float(data['activity_prior']))
            noise,_=old.estimate_spatial_noise(inputs.observation);noise/=config['scale']**2
            trajectory=scene<2 and users in (20,60,100)
            limit=120 if trajectory else 1
            collected=[]
            def observer(row,state,query,covariance,*unused):
                it=row['iteration']
                if it not in (1,30,limit) and not row['converged']:return
                kwargs=dict(nominal_variance=float(np.trace(covariance).real/16),
                    observation=inputs.observation/config['scale'],operator=inputs.operator,noise=noise,
                    activity_prior=inputs.activity_prior,initial_power=config['initialization']['normalized_training_second_moment'],iteration=it)
                estimated,selected=receiver_candidates(query,mean=state.mean,posterior_covariance=state.spatial_covariance,**kwargs)
                estimated={k:v for k,v in estimated.items() if k in METHODS}
                splits=[]
                for parity in (0,1):
                    train=np.arange(parity,users,2);test=np.arange(1-parity,users,2)
                    candidate,_=receiver_candidates(query[train],mean=state.mean[train],posterior_covariance=state.spatial_covariance[train],**kwargs)
                    splits.append(({k:v for k,v in candidate.items() if k in METHODS},test))
                folder=OUT/f'scene{scene:03d}_users{users}'/f'iteration{it:03d}'
                arrays=dict(estimated)
                for i,(candidate,_) in enumerate(splits):arrays.update({f'half{i}_{k}':v for k,v in candidate.items()})
                P.save_arrays(folder/'receiver_estimates.npz',arrays)
                P.save_arrays(folder/'query.npz',dict(query=query,covariance=covariance))
                P.save(folder/'ESTIMATION.json',dict(truth_used=False,selected_lower_energy_users=selected.tolist(),
                    estimate_sha256=P.sha(folder/'receiver_estimates.npz'),native_converged=row['converged']))
                collected.append((it,folder,estimated,splits,selected))
                if it==limit:raise PrefixComplete()
            with threadpool_limits(1):
                try:receiver.infer(inputs,observer=observer)
                except PrefixComplete:pass
            assert len(collected)==(3 if trajectory else 1)
            # Truth is loaded only after all receiver-only prefix estimates have been saved.
            truth=P.arrays(bank/'truth.npz');target=truth['channel']/config['scale'];active=truth['activity'].astype(bool)
            for iteration,folder,estimated,splits,selected in collected:
                query=P.arrays(folder/'query.npz')['query'];error=query-target;reference=second_moment(error)
                values=[]
                for method,cov in estimated.items():
                    groups={label:compare(cov,second_moment(error[index])) for label,index in
                        [('all',np.arange(users)),('active',np.flatnonzero(active)),('inactive',np.flatnonzero(~active))] if len(index)}
                    values.append(dict(method=method,groups=groups,split_checks=[compare(part[0][method],second_moment(error[part[1]])) for part in splits]))
                packed=error.transpose(1,0,2,3).reshape(16,-1)
                result=dict(scene=scene,seed=BASE+scene,users=users,iteration=iteration,results=values,
                    selected_active_fraction=float(active[selected].mean()),actual_active_fraction=float(active.mean()),
                    signal_to_error_trace_ratio=float(np.trace(second_moment(target)).real/np.trace(reference).real),
                    error_mean_energy_fraction=float(np.sum(abs(packed.mean(axis=1))**2)/np.trace(reference).real),
                    estimate_sha256=P.sha(folder/'receiver_estimates.npz'),truth_only_in_evaluator=True)
                P.save_arrays(folder/'oracle_reference.npz',dict(error_second_moment=reference,signal_second_moment=second_moment(target)))
                P.save(folder/'SCORES.json',result);all_scores.append(result)
                P.save(OUT/'STATUS.json',dict(status='RUNNING',completed=len(all_scores),expected=32,training_started=False,formal_experiments='PAUSED'))
                print(len(all_scores),'/32',scene,users,iteration,
                    [(x['method'],round(x['groups']['all']['shape_relative_error'],3),round(x['groups']['all']['trace_ratio'],3)) for x in values],flush=True)
    for path,digest in protocol['source_and_weight_sha256'].items():assert P.sha(ROOT/path)==digest,path
    P.save(OUT/'RESULTS.json',all_scores)
    P.save(OUT/'STATUS.json',dict(status='COMPLETE',completed=len(all_scores),expected=32,training_started=False,weights_unchanged=True,formal_experiments='PAUSED'))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','run']);args=parser.parse_args()
    if args.action=='prepare':prepare()
    else:run()
