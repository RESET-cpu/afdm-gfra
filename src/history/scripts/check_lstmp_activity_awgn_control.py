"""Synthetic matched-variance AWGN control for the read-only classifier audit."""
import math
import sys
import json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_lstmp_activity_initialization import ROOT,RUN,OUT
import numpy as np
import torch
from threadpoolctl import threadpool_limits
from experiments.lstmp_candidate_20261019 import common,data,receiver
from afdm_jadcedd.algorithm.proposed.activity import FrozenEvidence


def main():
    target=OUT/'AWGN_CONTROL.json'
    if target.exists():raise FileExistsError(target)
    if (RUN/'RUNNING.lock').exists():raise RuntimeError('Training must remain paused')
    torch.set_num_threads(4);threadpool_limits(4)
    torch.backends.cuda.matmul.allow_tf32=True;torch.backends.cudnn.allow_tf32=True
    torch.backends.cudnn.benchmark=True
    first_path=ROOT/common.CONFIG['pretrained_score']['path']
    evidence_path=ROOT/'runs/proposed_auxiliary_100_cuda_graph_20261019/n50000/activity/evidence_best.pt'
    before={str(p):common.sha(p) for p in [first_path,evidence_path]}
    first=torch.load(first_path,map_location='cpu',weights_only=False)
    model=receiver.Receiver();model.add_layer(first['state_dict']);model.cuda().eval();model.use_checkpoint=False
    evidence=FrozenEvidence(evidence_path,device='cuda')
    cases=data.Cases('validation',first['global_complex_rms'],'cuda')
    generator=torch.Generator(device='cuda').manual_seed(202610197300001)
    rows=[]
    with torch.no_grad():
        for index in range(48):
            public,labels,info=cases[index]
            prior=torch.zeros_like(labels['x'])
            variance=prior.new_tensor(public['rho']*common.CONFIG['normalized_training_second_moment'])
            _,v,_=receiver.linear_query(public,prior,variance,prior.new_tensor(0.))
            h=labels['x'][labels['active'].bool()]
            count=len(h)
            noise=torch.randn(h.shape,generator=generator,device='cuda')*torch.sqrt(v/2)
            query=torch.cat((h+noise,noise),dim=0)
            variances=v.expand(len(query))
            mean=query+v/2*model.score_call(model.layers[0].score,query,variances)
            z=evidence.network(query,variances,mean)
            prior_logit=math.log(public['rho']/(1-public['rho']))
            logits=z+prior_logit
            probability=torch.sigmoid(logits)
            truth=dict(x=torch.cat((h,torch.zeros_like(h)),dim=0),
                active=torch.cat((torch.ones(count,device='cuda'),torch.zeros(count,device='cuda'))),
                physical_scale=first['global_complex_rms'])
            result=(probability[:,None,None,None,None]*mean,logits)
            rows.append(dict(**info,**receiver.metrics([result],truth),variance=float(v),
                logit_min=float(logits.min()),logit_max=float(logits.max()),
                active_probability_mean=float(probability[:count].mean()),
                inactive_probability_mean=float(probability[count:].mean())))
    assert all(common.sha(Path(p))==digest for p,digest in before.items())
    report=dict(scope='Synthetic AWGN diagnostic only. Active channels from the same 48 validation scenes; each active example paired with a pure-noise inactive example at the original first-layer query variance.',
        optimizer_updates=0,noise_seed=202610197300001,source_weights_unchanged=True,
        summary=receiver.summarize_rows(rows),rows=rows)
    common.save_json(target,report)
    print(json.dumps(report['summary']))


if __name__=='__main__':main()
