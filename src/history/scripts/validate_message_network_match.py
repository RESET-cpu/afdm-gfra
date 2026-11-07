"""Frozen-network, truth-assisted development diagnostics; no training."""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
from copy import deepcopy
from pathlib import Path
import time
import numpy as np
import torch
from scipy.special import expit, logit
from threadpoolctl import threadpool_limits
import repair_stability_development as d
from benchmark_receiver_execution import GraphForward

OUT = d.ROOT/'runs/message_network_match_20261019'
P = d.paired


def evaluate(model, query, label, target, active, prior):
    label = np.broadcast_to(np.asarray(label, float), (len(query),))
    low, high = model.model.noise_support
    if np.any((label < low) | (label > high)):
        return dict(status='OUTSIDE_SUPPORT',label_min=float(label.min()),label_max=float(label.max()))
    moments = model.model.infer(query, label)
    logits = model.evidence.infer(query, label, moments.mean)
    probability = expit(logit(prior)+logits)
    estimate = probability[:,None,None,None]*moments.mean
    errors = np.mean(abs(moments.mean-target)**2, axis=(1,2,3))
    energy = float(np.sum(abs(target)**2))
    full_error = float(np.sum(abs(estimate-target)**2))
    active_error = float(np.sum(abs(moments.mean[active]-target[active])**2))
    predicted = moments.variance[active]
    calibration = float(errors[active].sum()/predicted.sum()) if predicted.sum()>0 else None
    return dict(status='COMPLETE', full_error=full_error, signal_energy=energy,
        nmse_db=float(10*np.log10(full_error/energy)),
        oracle_activity_error=active_error, oracle_activity_nmse_db=float(10*np.log10(active_error/energy)),
        active=int(active.sum()),inactive=int((~active).sum()),
        misses=int(np.count_nonzero((probability<.5)&active)),
        false_alarms=int(np.count_nonzero((probability>=.5)&~active)),
        brier_score=float(np.mean((probability-active)**2)),
        active_probability=float(probability[active].mean()),
        inactive_probability=float(probability[~active].mean()),
        active_conditional_mse=float(errors[active].mean()),
        active_predicted_variance=float(predicted.mean()),
        active_mse_over_predicted_variance=calibration,
        negative_predicted_variances=int(np.count_nonzero(moments.variance<=0)),
        query_mse_over_label=float(np.mean(np.mean(abs(query-target)**2,axis=(1,2,3))/label)),
        probabilities=probability.tolist(), per_user_conditional_mse=errors.tolist(),
        predicted_variance=moments.variance.tolist(),label_min=float(label.min()),label_max=float(label.max()))


def diagnose(model, snapshot, truth, prior, seed):
    query = snapshot['query']; variance = float(np.trace(snapshot['covariance']).real/16)
    target = truth['channel']/model.configuration['scale'];active=truth['activity'].astype(bool)
    error = query-target
    packed = error.transpose(1,0,2,3).reshape(16,-1)
    covariance = packed@packed.conj().T/packed.shape[1]
    total = float(np.trace(covariance).real/16)
    normalized = covariance*(variance/total)
    eigen, basis = np.linalg.eigh(normalized)
    assert eigen.min()>-1e-10*eigen.max()
    factor = basis*np.sqrt(np.maximum(eigen,0))
    per_user = np.mean(abs(error)**2,axis=(1,2,3))
    inner = np.vdot(target[active],error[active])
    correlation = float(abs(inner)/max(np.linalg.norm(target[active])*np.linalg.norm(error[active]),1e-15))
    rows=[]
    def one(kind,q,v,repeat=None):
        row=evaluate(model,q,v,target,active,prior)
        rows.append(dict(kind=kind,repeat=repeat,query_sha256=P.array_sha256(q),**row))
    one('actual',query,variance)
    one('actual_oracle_global_variance',query,total)
    one('actual_oracle_per_user_variance',query,per_user)
    for repeat in range(3):
        rng=np.random.default_rng(seed+repeat)
        white=(rng.normal(size=target.shape)+1j*rng.normal(size=target.shape))/np.sqrt(2)
        one('white',target+np.sqrt(variance)*white,variance,repeat)
        diagonal=np.sqrt(np.diag(normalized).real)[None,:,None,None]*white
        one('diagonal_antenna',target+diagonal,variance,repeat)
        correlated=np.einsum('mn,knrc->kmrc',factor,white,optimize=False)
        one('correlated_antenna',target+correlated,variance,repeat)
    return dict(nominal_variance=variance,actual_query_mse=total,
        largest_antenna_eigen_fraction=float(eigen[-1]/eigen.sum()),
        active_signal_error_absolute_correlation=correlation,
        per_user_error_variance_min=float(per_user.min()),per_user_error_variance_max=float(per_user.max()),
        oracle_quantities_not_available_to_receiver=True,rows=rows)


def main():
    if OUT.exists():raise ValueError('Fresh output required; never overwrite diagnosis')
    config=deepcopy(P.read(P.MODEL));config['ep']['damping']=.1
    sources=P.identities()
    for path in [Path(__file__), P.MODEL]+[d.ROOT/config[k] for k in ('first_checkpoint','second_checkpoint','evidence_checkpoint','prior_definition')]:
        sources[str(path.resolve())]=P.sha(path)
    P.save(OUT/'PROTOCOL.json',dict(created_unix=time.time(),
        development_seed_base=d.SEEDS['development'],development_scenes=4,users=[20,40,60,80,100],
        first_query_cases=20,trajectory_cases=[dict(scene=0,users=k,iterations=[30,120]) for k in (20,60,100)],
        controls=['actual','actual_oracle_global_variance','actual_oracle_per_user_variance','white','diagonal_antenna','correlated_antenna'],
        gaussian_repetitions=3,gaussian_seed_base=202610194100001,
        config=config,cudnn_allow_tf32=False,matmul_allow_tf32=False,
        training_started=False,weights_changed=False,formal_experiments='PAUSED',
        interpretation='Exploratory development diagnosis, four independent physical scene seeds. All conditions retained. Not a sealed acceptance or formal performance comparison.',
        truth_policy='Receiver prefix uses only public inputs. Offline query construction, variance recalibration, activity masking and scores use truth and are explicitly oracle diagnostics, never deployable corrections.',
        purpose='Separate noise shape, noise magnitude, conditional mean, variance and activity miscalibration before deciding on retraining.',
        no_retraining_before_user_notification=True,source_and_weight_sha256=sources))
    torch.set_num_threads(1);torch.backends.cudnn.allow_tf32=False;torch.backends.cuda.matmul.allow_tf32=False
    receiver=P.EstimatedNoiseProposedReceiver(config,device='cuda')
    receiver.base.model.first=GraphForward(receiver.base.model.first)
    receiver.base.model.second=GraphForward(receiver.base.model.second)
    completed=[]
    class PrefixComplete(Exception):pass
    for scene in range(4):
        for users in [20,40,60,80,100]:
            inputs,truth,bank=d.bank('development',scene,users)
            wanted=[1,30,120] if scene==0 and users in (20,60,100) else [1]
            folder=OUT/f'scene{scene:03d}_users{users}'
            P.save(folder/'INPUT.json',dict(bank=str(bank),manifest_sha256=P.sha(bank/'READY.json')))
            def observe(row,state,query,covariance,*unused):
                if row['iteration'] in wanted:
                    path=folder/f'iteration{row["iteration"]:03d}.npz'
                    P.save_arrays(path,dict(query=query,covariance=covariance))
                    P.save(path.with_suffix('.json'),dict(iteration=row['iteration'],truth_used_in_inference=False,
                        query_sha256=P.array_sha256(query),native_record=row))
                if row['iteration']==max(wanted):raise PrefixComplete()
            with threadpool_limits(1):
                try:receiver.infer(inputs,observer=observe)
                except PrefixComplete:pass
                for iteration in wanted:
                    source=folder/f'iteration{iteration:03d}.npz'
                    if not source.exists():
                        raise RuntimeError('Native receiver stopped before a predeclared snapshot; retain and inspect')
                    seed=202610194100001+scene*100000+users*100+iteration*3
                    result=diagnose(receiver.base,P.arrays(source),truth,inputs.activity_prior,seed)
                    P.save(folder/f'diagnosis{iteration:03d}.json',dict(scene=scene,users=users,iteration=iteration,
                        source_sha256=P.sha(source),**result))
                    completed.append(dict(scene=scene,users=users,iteration=iteration))
                    P.save(OUT/'STATUS.json',dict(status='RUNNING',completed=len(completed),expected=26,
                        cases=completed,training_started=False,formal_experiments='PAUSED'))
                    print(len(completed),'/26',scene,users,iteration,
                        [(x['kind'],round(x.get('nmse_db',float('nan')),2)) for x in result['rows'][:3]],flush=True)
    for path,digest in sources.items():assert P.sha(d.ROOT/path)==digest,path
    P.save(OUT/'STATUS.json',dict(status='COMPLETE',completed=len(completed),expected=26,
        cases=completed,training_started=False,weights_unchanged_sha256_verified=True,formal_experiments='PAUSED'))


if __name__=='__main__':main()
