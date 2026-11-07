"""Post-freeze regression diagnostic; never counted as an independent test."""
from pathlib import Path
import time
import numpy as np
import torch
import repair_stability_retry as r
from stability_damping_retry import RetryReceiver
from benchmark_receiver_execution import GraphForward


if __name__=='__main__':
    out=r.OUT/'regression_previous_failure'
    if out.exists():raise ValueError('Preserve the previous regression attempt')
    freeze=r.d.paired.read(r.OUT/'FROZEN_CANDIDATE.json');r.d.paired.verify_sources(freeze)
    source=r.OLD/'bank/acceptance/scene005_users100'
    identity=r.d.paired.read(source/'READY.json')
    for name,digest in identity['sha256'].items():assert r.d.paired.sha(source/name)==digest
    previous=r.OLD/'evaluations/acceptance/damping0.1_budget1200_fp32/scene005_users100'
    assert r.d.paired.read(previous/'SUMMARY.json')['stopping_reason']=='MAX_ITERATIONS'
    r.d.paired.save(out/'PLAN.json',dict(created_unix=time.time(),frozen_candidate_sha256=r.d.paired.sha(r.OUT/'FROZEN_CANDIDATE.json'),
        input_manifest_sha256=r.d.paired.sha(source/'READY.json'),previous_summary_sha256=r.d.paired.sha(previous/'SUMMARY.json'),
        purpose='Post-freeze known-failure regression diagnostic. Excluded from the new 60 independent acceptance cases and from parameter selection.',
        rule='No candidate or threshold changes may be made in response to this result. Failure must remain visible and prevents an unqualified repair claim.',
        source_sha256={str(Path(__file__)):r.d.paired.sha(Path(__file__))}))
    data=r.d.paired.arrays(source/'input.npz');truth=r.d.paired.arrays(source/'truth.npz')
    inputs=r.d.paired.ReceiverInput(data['observation'],data['operator'],float(data['noise_variance']),float(data['activity_prior']))
    config=freeze['configuration'];torch.set_num_threads(1)
    torch.backends.cudnn.allow_tf32=False;torch.backends.cuda.matmul.allow_tf32=False
    model=RetryReceiver(config,device='cuda');model.base.model.first=GraphForward(model.base.model.first);model.base.model.second=GraphForward(model.base.model.second)
    rows=[]
    def observe(row,state,*unused):
        target=truth['channel']/config['scale']
        rows.append(dict(iteration=row['iteration'],attempt=row['attempt'],attempt_iteration=row['attempt_iteration'],
            nmse_db=float(10*np.log10(np.sum(abs(state.mean-target)**2)/np.sum(abs(target)**2))),
            activity_change=row['activity_change'],raw_site_residual=row['raw_site_residual']))
    with r.d.threadpool_limits(1):prediction,record=model.infer(inputs,observer=observe)
    for i,(arrays,native) in enumerate(model.attempts):
        r.d.paired.save_arrays(out/f'attempt{i}.npz',arrays);r.d.paired.save(out/f'attempt{i}.json',native)
    old=r.d.paired.arrays(previous/'prediction.npz');first=model.attempts[0][0]
    exact=set(old)==set(first) and all(np.array_equal(old[k],first[k]) for k in old)
    assert exact,'The first attempt must exactly reproduce the known failure'
    r.d.paired.verify_sources(freeze)
    r.d.paired.save(out/'record.json',record);r.d.paired.save(out/'TRACE.json',rows)
    r.d.paired.save_arrays(out/'prediction.npz',prediction)
    result=dict(passed=bool(record['converged']),known_failure_first_attempt_exact=True,
        independent_test=False,parameter_selection=False,attempt_count=record['attempt_count'],iterations=record['iterations'],
        stopping_reason=record['stopping_reason'],metrics=r.d.paired.score_arrays(prediction,truth),seconds=record['seconds'])
    r.d.paired.save(out/'SUMMARY.json',result)
    print(result,flush=True)
