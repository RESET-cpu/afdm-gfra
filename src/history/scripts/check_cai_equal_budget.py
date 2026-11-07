"""Resolve unequal-stop confounding in the two K=100 diagnostic conditions."""
from copy import deepcopy
from pathlib import Path
import time
import numpy as np
import torch
from threadpoolctl import threadpool_limits
import diagnose_cai_framework_sequence as d


def main():
    p=d.verify();P=d.P
    assert P.read(d.OUT/'stage3_phase/SUMMARY.json')['status']=='COMPLETE'
    out=d.OUT/'stage4_equal_budget';assert not out.exists()
    cfg=deepcopy(p['configuration']);cfg['ep']['iterations']=300;cfg['ep']['min_iterations']=301
    P.save(out/'PROTOCOL.json',dict(scope='Supplement: same 300-update budget for K=100 controls; do not call forced runs converged.',
        motivation='Native stopping occurs earlier under oracle activity, confounding final-output comparisons.',
        cases=[name for name in d.CASES if name.endswith('users100')],configuration=cfg,
        only_changes={'ep.iterations':[600,300],'ep.min_iterations':[60,301]},
        training_started=False,script_sha256=P.sha(Path(__file__))))
    torch.set_num_threads(1);torch.backends.cudnn.allow_tf32=False;torch.backends.cuda.matmul.allow_tf32=False
    receiver=P.EstimatedNoiseProposedReceiver(cfg,device='cuda')
    receiver.base.model.first=d.GraphForward(receiver.base.model.first);receiver.base.model.second=d.GraphForward(receiver.base.model.second)
    original=receiver.base.evidence;results=[]
    for name in [name for name in d.CASES if name.endswith('users100')]:
        bank=d.SOURCE/'bank/development'/name
        for variant in p['physical']['variants']:
            stage='stage3_phase' if variant.startswith('oracle_phase') else 'stage2_activity'
            previous=d.OUT/stage/name/variant
            old=P.read(previous/'SUMMARY.json');folder=out/name/variant
            # If a 300th native iterate already exists, reuse it rather than rerun.
            if old['iterations']>=300:
                pred=P.arrays(previous/'checkpoints/iteration0300.npz');seconds=0.;checks=[];reused=True
            else:
                reused=False;data=P.arrays(bank/'input.npz');is_activity=variant.endswith('oracle_activity');is_phase=variant.startswith('oracle_phase')
                activity=slopes=None
                if is_activity or is_phase:
                    with np.load(bank/'truth.npz') as t:
                        if is_activity:activity=t['activity'].astype(bool)
                        if is_phase:slopes=t['phase_slopes'].copy()
                receiver.base.evidence=d.OracleEvidence(original,activity) if is_activity else original
                if is_phase:
                    with np.load(bank/'public.npz') as public:pilot=public['pilot'].copy()
                    data['operator']=pilot*np.exp(1j*np.arange(len(pilot))[:,None,None]*slopes[None,:,None])
                inp=P.ReceiverInput(data['observation'],data['operator'],float(data['noise_variance']),float(data['activity_prior']))
                checks=[];start=time.monotonic()
                def observer(row,state,query,cov,*unused):
                    it=row['iteration'];src=previous/'checkpoints'/f'iteration{it:04d}.npz'
                    if src.exists():
                        ref=P.arrays(src)
                        exact=all(np.array_equal(ref[key],value) for key,value in dict(query=query,covariance=cov,probabilities=state.activity,estimate=state.mean*cfg['scale']).items())
                        assert exact,(name,variant,it)
                        checks.append(dict(iteration=it,exact=True))
                    if it%100==0:
                        print(name,variant,it,round(time.monotonic()-start,1),flush=True)
                        P.save(out/'STATUS.json',dict(status='RUNNING',case=name,variant=variant,iteration=it,completed=len(results)))
                with threadpool_limits(1):pred,record=receiver.infer(inp,observer=observer)
                assert record['iterations']==300 and not record['converged']
                record['truth_used_in_inference']=is_activity or is_phase
                record['truth_loaded']=is_activity or is_phase
                record['oracle_activity']=is_activity;record['oracle_phase']=is_phase
                if is_activity:record['classifier_output_used']=False
                P.save(folder/'record.json',record);seconds=record['seconds']
                assert any(x['iteration']==old['iterations'] for x in checks)
            P.save_arrays(folder/'prediction.npz',pred)
            truth=P.arrays(bank/'truth.npz');metrics=P.score_arrays(pred,truth);del truth
            result=dict(case=name,variant=variant,iterations=300,convergence_claim=False,seconds=seconds,
                metrics=metrics,original_final_nmse_db=old['metrics']['nmse_db'],original_iterations=old['iterations'],
                original_prefix_checks=checks,reused_native_checkpoint=reused)
            P.save(folder/'SUMMARY.json',result);results.append(result)
            print('FINISHED',name,variant,metrics['nmse_db'],flush=True)
    d.verify();P.save(out/'SUMMARY.json',dict(status='COMPLETE',results=results,training_started=False))


if __name__=='__main__':main()
