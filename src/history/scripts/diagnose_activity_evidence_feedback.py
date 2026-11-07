"""Frozen-weight activity diagnostics on preserved development inputs; no fitting."""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
from copy import deepcopy
from pathlib import Path
import time
import numpy as np
import torch
from scipy.special import expit, logit
from threadpoolctl import threadpool_limits
import diagnose_cai_framework_sequence as D
from receiver_covariance_candidates import second_moment

P = D.P
OUT = P.ROOT/'runs/activity_evidence_feedback_20261019'
RESULT = P.ROOT/'results/activity_evidence_feedback_20261019'
CASES = [f'scene{s:03d}_users{k}' for s in range(4) for k in (20, 100)]


def verify():
    protocol = P.read(OUT/'PROTOCOL.json')
    for path, digest in protocol['source_and_weight_sha256'].items():
        assert P.sha(P.ROOT/path) == digest, path
    return protocol


def prepare():
    assert not OUT.exists(), 'Use a fresh output directory'
    old = D.verify()
    cfg = deepcopy(old['configuration'])
    cfg['ep']['iterations'] = 300
    cfg['ep']['min_iterations'] = 301
    hashes = dict(old['source_and_weight_sha256'])
    hashes[str(Path(__file__).resolve())] = P.sha(Path(__file__))
    hashes[str((P.ROOT/'scripts/receiver_covariance_candidates.py').resolve())] = P.sha(P.ROOT/'scripts/receiver_covariance_candidates.py')
    for name in CASES:
        bank = D.SOURCE/'bank/development'/name
        for filename, digest in P.read(bank/'READY.json')['sha256'].items():
            assert P.sha(bank/filename) == digest
            hashes[str((bank/filename).resolve())] = digest
    P.save(OUT/'PROTOCOL.json', dict(configuration=cfg, cases=CASES,
        existing_diagnostic_scenes=[0, 1], additional_development_scenes=[2, 3],
        limits='All four seeds previously used for covariance diagnosis; no pristine or formal acceptance claim. K values sharing a seed are not independent scenes.',
        training_started=False, fitted_parameters=False, formal_experiments='PAUSED',
        feedback=dict(variants=['baseline', 'prior_first30'], iterations=300,
            intervention='For the first 30 nonlinear updates, replace evidence log-likelihood ratio by zero, so p=rho; then restore the unchanged classifier. Fixed before new runs, no parameter sweep.',
            interpretation='Receiver-available diagnostic intervention only; not a calibrated likelihood or accepted repair. All other equations/weights/damping0.1 retained; stopping disabled equally.'),
        null=dict(samples=128, chunk=32, seed=202610199100001,
            covariance='Uncentered spatial second moment of lowest-energy half of query users, rescaled to the declared variance; no activity labels used.',
            controls=['white', 'receiver_correlated'],
            interpretation='Synthetic inactive-only Gaussian queries, with same random white draws and expected total power. No claim of a posterior activity probability or full joint error model.'),
        truth_policy='No truth enters feedback runs or null construction. Read channel/activity truth only for offline scoring.',
        source_and_weight_sha256=hashes))
    verify()


def metrics(logits, active, prior):
    l = np.asarray(logits, float); a = np.asarray(active, bool)
    z = l + logit(prior); probability = expit(z)
    auc = float(np.mean((l[a, None] > l[None, ~a]) + .5*(l[a, None] == l[None, ~a]))) if a.any() and (~a).any() else None
    return dict(active=int(a.sum()), inactive=int((~a).sum()), ranking_pair_probability=auc,
        mean_probability=float(probability.mean()), probability_squared_error=float(np.mean((probability-a)**2)),
        negative_log_likelihood=float(np.mean(np.logaddexp(0, z)-a*z)),
        misses=int(np.sum(a & (z < 0))), false_alarms=int(np.sum(~a & (z >= 0))),
        active_logit_quantiles=np.quantile(l[a], [0, .5, 1]).tolist() if a.any() else [],
        inactive_logit_quantiles=np.quantile(l[~a], [0, .5, 1]).tolist() if (~a).any() else [])


def offline():
    verify(); rows=[]
    for stage in ('stage2_activity', 'stage3_phase'):
        variant = 'estimated_phase_learned_activity' if stage == 'stage2_activity' else 'oracle_phase_learned_activity'
        for name in D.CASES:
            bank=D.SOURCE/'bank/development'/name
            active=P.arrays(bank/'truth.npz')['activity'].astype(bool)
            prior=float(P.arrays(bank/'input.npz')['activity_prior'])
            source=D.OUT/stage/name/variant/'record.json'
            trace=P.read(source)['trace']
            result=dict(case=name, variant=variant, source_sha256=P.sha(source),
                trace=[dict(iteration=x['iteration'], **metrics(x['classifier_logit_per_user'], active, prior)) for x in trace])
            P.save(OUT/'offline'/name/f'{variant}.json', result); rows.append(result)
    P.save(OUT/'offline/SUMMARY.json', dict(status='COMPLETE', results=rows))
    print('Offline activity traces complete', flush=True)


def receiver(cfg):
    torch.set_num_threads(1)
    torch.backends.cudnn.allow_tf32=False; torch.backends.cuda.matmul.allow_tf32=False
    obj=P.EstimatedNoiseProposedReceiver(cfg, device='cuda')
    obj.base.model.first=D.GraphForward(obj.base.model.first)
    obj.base.model.second=D.GraphForward(obj.base.model.second)
    return obj


def null_controls():
    protocol=verify(); assert not (OUT/'null/SUMMARY.json').exists()
    model=receiver(protocol['configuration']).base
    results=[]; index=0
    for name in D.CASES:
        folder=D.OUT/'stage2_activity'/name/'estimated_phase_learned_activity'
        last=P.read(folder/'SUMMARY.json')['iterations']
        for iteration in sorted(set([1,30,min(120,last)])):
            snap=P.arrays(folder/'checkpoints'/f'iteration{iteration:04d}.npz')
            query=snap['query'];v=float(np.trace(snap['covariance']).real/16)
            selected=np.argsort(np.mean(abs(query)**2,axis=(1,2,3)),kind='stable')[:len(query)//2]
            raw=second_moment(query[selected]);cov=raw*(16*v/np.trace(raw).real)
            eig,u=np.linalg.eigh(cov)
            assert eig.min()>-1e-10*eig.max()
            factor=u*np.sqrt(np.maximum(eig,0))
            rng=np.random.default_rng(protocol['null']['seed']+index);index+=1
            prior=float(P.arrays(D.SOURCE/'bank/development'/name/'input.npz')['activity_prior'])
            scores={'white':[], 'receiver_correlated':[]}; energies={key:[] for key in scores}
            with threadpool_limits(1):
                for start in range(0,protocol['null']['samples'],protocol['null']['chunk']):
                    shape=(min(protocol['null']['chunk'],protocol['null']['samples']-start),16,16,16)
                    z=(rng.normal(size=shape)+1j*rng.normal(size=shape))/np.sqrt(2)
                    for kind,noise in [('white',np.sqrt(v)*z),('receiver_correlated',np.einsum('mn,knrc->kmrc',factor,z,optimize=False))]:
                        label=np.full(len(noise),v)
                        moments=model.model.infer(noise,label)
                        scores[kind].extend(model.evidence.infer(noise,label,moments.mean).tolist())
                        energies[kind].extend(np.mean(abs(noise)**2,axis=(1,2,3)).tolist())
            # Truth is loaded after construction and network evaluation, only for scoring.
            truth=P.arrays(D.SOURCE/'bank/development'/name/'truth.npz');active=truth['activity'].astype(bool)
            trace=P.read(folder/'record.json')['trace'][iteration-1]
            row=dict(case=name,iteration=iteration,query_variance=v,selected_users=selected.tolist(),
                largest_covariance_eigen_fraction=float(eig[-1]/eig.sum()),
                actual=metrics(trace['classifier_logit_per_user'],active,prior), controls={})
            for kind,values in scores.items():
                row['controls'][kind]=dict(**metrics(values,np.zeros(len(values),bool),prior),
                    sample_power_over_declared_variance=float(np.mean(energies[kind])/v), logits=values)
            dest=OUT/'null'/name/f'iteration{iteration:04d}'
            P.save(dest/'REPORT.json',row);P.save_arrays(dest/'covariance.npz',dict(covariance=cov,raw_covariance=raw))
            results.append(row)
            print('NULL',name,iteration,[(k,row['controls'][k]['false_alarms']) for k in scores],flush=True)
    verify();P.save(OUT/'null/SUMMARY.json',dict(status='COMPLETE',results=results))


class PriorFirst30:
    def __init__(self, original):
        self.original=original;self.noise_support=original.noise_support
        self.training_class_prior=original.training_class_prior;self.iteration=0;self.raw=[]

    def infer(self, query, variance, mean):
        self.iteration+=1
        raw=self.original.infer(query,variance,mean)
        self.raw.append(raw.tolist())
        return np.zeros_like(raw) if self.iteration<=30 else raw


def feedback():
    protocol=verify();cfg=protocol['configuration'];obj=receiver(cfg);original=obj.base.evidence
    results=[]
    for name in CASES:
        bank=D.SOURCE/'bank/development'/name
        for variant in protocol['feedback']['variants']:
            dest=OUT/'feedback'/name/variant
            assert not dest.exists(), 'Do not overwrite a diagnostic'
            data=P.arrays(bank/'input.npz');prior=float(data['activity_prior'])
            inp=P.ReceiverInput(data['observation'],data['operator'],float(data['noise_variance']),prior)
            wrapper=PriorFirst30(original) if variant=='prior_first30' else None
            obj.base.evidence=wrapper or original
            snapshots=[];prefix=[];start=time.monotonic()
            def observer(row,state,query,cov,*unused):
                it=row['iteration']
                if wrapper is not None:
                    assert wrapper.iteration==it, 'One evidence call per iteration required'
                    if it<=30:assert np.allclose(state.activity,prior,rtol=0,atol=1e-15)
                if variant=='baseline' and name in D.CASES:
                    previous=D.OUT/'stage2_activity'/name/'estimated_phase_learned_activity/checkpoints'/f'iteration{it:04d}.npz'
                    if previous.exists():
                        expected=P.arrays(previous)
                        exact=all(np.array_equal(expected[key],value) for key,value in dict(query=query,covariance=cov,probabilities=state.activity,estimate=state.mean*cfg['scale']).items())
                        assert exact,(name,it);prefix.append(dict(iteration=it,exact=True))
                # Keep per-iteration arrays in memory until inference finishes; truth not read here.
                snapshots.append(dict(estimate=(state.mean*cfg['scale']).copy(),probabilities=state.activity.copy(),activity_decision=(state.activity>=.5).copy()))
                if it in (1,30,31,120,300):
                    P.save_arrays(dest/'checkpoints'/f'iteration{it:04d}.npz',dict(**snapshots[-1],query=query,covariance=cov))
                if it%100==0:
                    print('FEEDBACK',name,variant,it,round(time.monotonic()-start,1),flush=True)
                    P.save(OUT/'STATUS.json',dict(status='RUNNING',case=name,variant=variant,iteration=it,completed=len(results),expected=16))
            with threadpool_limits(1):pred,record=obj.infer(inp,observer=observer)
            assert record['iterations']==300 and not record['converged']
            record['truth_used_in_inference']=False;record['truth_loaded']=False
            record['activity_intervention']=variant
            if wrapper is not None:record['original_classifier_logit_trace']=wrapper.raw
            P.save(dest/'record.json',record);P.save_arrays(dest/'prediction.npz',pred)
            truth=P.arrays(bank/'truth.npz')
            trace=[]
            for i,values in enumerate(snapshots):
                l=record['trace'][i]['classifier_logit_per_user']
                trace.append(dict(iteration=i+1,**P.score_arrays(values,truth),activity_metrics=metrics(l,truth['activity'],prior)))
            result=dict(case=name,variant=variant,metrics=P.score_arrays(pred,truth),
                iterations=300,convergence_claim=False,seconds=record['seconds'],prefix_checks=prefix,trace=trace)
            P.save(dest/'SUMMARY.json',result);results.append(result)
            print('FINISHED',name,variant,result['metrics']['nmse_db'],flush=True)
            del truth,snapshots
    verify();P.save(OUT/'feedback/SUMMARY.json',dict(status='COMPLETE',results=results))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','offline','null','feedback'])
    action=p.parse_args().action
    if action=='prepare':prepare()
    elif action=='offline':offline()
    elif action=='null':null_controls()
    else:feedback()
