"""Extend one known failure with unchanged damping, weights and stopping tests."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
from copy import deepcopy
from pathlib import Path
import json
import time
import numpy as np
import torch
from threadpoolctl import threadpool_limits
import repair_stability_development as d

P=d.paired;ROOT=d.ROOT
OUT=ROOT/'runs/known_k100_damping01_extension_20261019'
OLD=d.OUT/'evaluations/acceptance/damping0.1_budget1200_fp32/scene005_users100'
BANK=d.OUT/'bank/acceptance/scene005_users100'
MAXIMUM=6000

def prediction(state,scale):
    return dict(estimate=state.mean*scale,conditional_matrix=state.conditional_mean*scale,
        probabilities=state.activity,activity_decision=state.activity>=.5,
        spatial_covariance=state.spatial_covariance*scale**2)

def main():
    assert not OUT.exists(),'New output directory required'
    freeze=P.read(d.OUT/'FROZEN_CANDIDATE.json');P.verify_sources(freeze)
    manifest=P.read(BANK/'READY.json')
    for name,digest in manifest['sha256'].items():assert P.sha(BANK/name)==digest,name
    old_config=P.read(OLD/'PLAN.json')['config'];config=deepcopy(old_config)
    assert config['ep']['damping']==.1 and config['ep']['iterations']==1200
    config['ep']['iterations']=MAXIMUM
    data=P.arrays(BANK/'input.npz')
    inputs=P.ReceiverInput(data['observation'],data['operator'],float(data['noise_variance']),float(data['activity_prior']))
    old_trace=P.read(OLD/'record.json')['trace'];old_prediction=P.arrays(OLD/'prediction.npz')
    preserved=P.read(d.OUT/'PRESERVATION.json')
    extra={str(p.resolve()):P.sha(p) for p in [Path(__file__),BANK/'READY.json',OLD/'PLAN.json',OLD/'prediction.npz',OLD/'record.json',OLD/'SUMMARY.json']}
    P.save(OUT/'PROTOCOL.json',dict(created_unix=time.time(),configuration=config,
        original_configuration=old_config,only_configuration_change={'ep.iterations':[1200,MAXIMUM]},
        source_and_weight_sha256=freeze['source_and_weight_sha256']|extra,
        seed=manifest['seed'],scene=5,users=100,
        classification='Known-failure diagnostic, no longer an independent acceptance case. Original failed acceptance remains unchanged.',
        rule='Replay from original initialization; require exact old 1200-iteration trajectory and output, then continue without reset to first native convergence or 6000 iterations.',
        interpretation='Convergence is not evidence of accurate channel/activity recovery. Score every retained checkpoint only after receiver run.',
        original_stopping_tests_unchanged=True,training_started=False,formal_experiments='PAUSED',
        truth_policy='Receiver worker does not load truth until inference has returned. No truth selects parameters, stopping or checkpoints.',
        execution=dict(cudnn_allow_tf32=False,matmul_allow_tf32=False,cuda_graph_first_second=True)))
    torch.set_num_threads(1);torch.backends.cudnn.allow_tf32=False;torch.backends.cuda.matmul.allow_tf32=False
    model=P.EstimatedNoiseProposedReceiver(config,device='cuda')
    model.base.model.first=d.GraphForward(model.base.model.first);model.base.model.second=d.GraphForward(model.base.model.second)
    started=time.monotonic();prefix_checks=0;last_decision=None
    trace_path=OUT/'progress.jsonl'
    with trace_path.open('x',encoding='utf-8',buffering=1) as log:
        def observer(row,state,query,covariance,*unused):
            nonlocal prefix_checks,last_decision
            it=row['iteration']
            if it<=1200:
                ref=old_trace[it-1]
                for key in ('estimate_change','activity_change','input_covariance_change','raw_site_residual',
                            'activity_weight_residual','query_variance_min','probabilities_per_user','converged'):
                    assert row[key]==ref[key],(it,key)
                prefix_checks+=1
            decision=state.activity>=.5
            compact={key:row[key] for key in ('iteration','estimate_change','activity_change','input_covariance_change',
                'raw_site_residual','activity_weight_residual','query_variance_min','stable_iterations','fresh_iterations',
                'decision_stable_iterations','converged','site_accepted','unsupported_users','projected_eigenvalues')}
            compact.update(probabilities=state.activity.tolist(),decision_changes=None if last_decision is None else int(np.sum(decision!=last_decision)),elapsed_seconds=time.monotonic()-started)
            last_decision=decision.copy();log.write(json.dumps(compact,allow_nan=False)+'\n')
            if it==1 or it%100==0 or row['converged']:
                arrays=prediction(state,config['scale']);P.save_arrays(OUT/'checkpoints'/f'iteration{it:05d}.npz',arrays)
                if it==1200:
                    assert set(arrays)==set(old_prediction)
                    assert all(np.array_equal(arrays[k],old_prediction[k]) for k in arrays),'Old final output must reproduce exactly'
                    P.save(OUT/'PREFIX_CHECK.json',dict(passed=True,exact_iterations=prefix_checks,exact_prediction=True))
                P.save(OUT/'STATUS.json',dict(status='RUNNING',iteration=it,maximum_iterations=MAXIMUM,
                    elapsed_seconds=time.monotonic()-started,activity_change=row['activity_change'],
                    activity_weight_residual=row['activity_weight_residual'],converged=row['converged'],training_started=False,formal_experiments='PAUSED'))
                print('iteration',it,'seconds',round(time.monotonic()-started,1),'dp',row['activity_change'],
                    'activity residual',row['activity_weight_residual'],'fresh',row['fresh_iterations'],flush=True)
        with threadpool_limits(1):arrays,record=model.infer(inputs,observer=observer)
    assert prefix_checks==1200
    P.save_arrays(OUT/'prediction.npz',arrays);P.save(OUT/'record.json',record)
    truth=P.arrays(BANK/'truth.npz')
    checkpoints=[]
    for path in sorted((OUT/'checkpoints').glob('iteration*.npz')):
        checkpoints.append(dict(iteration=int(path.stem[9:]),metrics=P.score_arrays(P.arrays(path),truth),sha256=P.sha(path)))
    P.save(OUT/'CHECKPOINT_SCORES.json',checkpoints)
    P.verify_sources(freeze)
    for path,digest in extra.items():assert P.sha(Path(path))==digest,path
    for path,digest in preserved.items():assert P.sha(ROOT/path)==digest,path
    summary=dict(status='COMPLETE',iterations=record['iterations'],converged=record['converged'],
        stopping_reason=record['stopping_reason'],seconds=record['seconds'],metrics=P.score_arrays(arrays,truth),
        prefix_1200_exact=True,preserved_files_verified=len(preserved),training_started=False,
        formal_experiments='PAUSED',independent_acceptance=False)
    P.save(OUT/'SUMMARY.json',summary);P.save(OUT/'STATUS.json',{k:v for k,v in summary.items() if k!='metrics'})
    print('FINISHED',record['iterations'],record['stopping_reason'],summary['metrics']['nmse_db'],flush=True)

if __name__=='__main__':main()
