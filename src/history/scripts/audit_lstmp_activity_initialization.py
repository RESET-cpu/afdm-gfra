"""Read-only paired initialization audit; no optimizer or training updates."""
import json
import math
import os
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RUN=Path(r'D:\afdm-gfra-cpu\runs\lstmp_refinenet_50000_fixed_budget_20261019')
OUT=ROOT/'results/lstmp_activity_initialization_20261019'
os.environ['AFDM_LSTMP_ROOT']=str(ROOT)
os.environ['AFDM_LSTMP_CONFIG']=str(RUN/'source_code/experiments/lstmp_candidate_20261019/reuse_50000_fixed_budget.json')
sys.path.insert(0,str(RUN/'source_code'))
import numpy as np
import torch
from threadpoolctl import threadpool_limits
from experiments.lstmp_candidate_20261019 import common,data,receiver
from afdm_jadcedd.algorithm.proposed.activity import Config,EvidenceNetwork,FrozenEvidence


def main():
    if OUT.exists():raise FileExistsError(OUT)
    if (RUN/'RUNNING.lock').exists():raise RuntimeError('Training must be paused during this audit')
    OUT.mkdir(parents=True)
    indices=list(range(48))  # two deterministic scenes per each of the 24 conditions
    common.save_json(OUT/'PLAN.json',dict(scope='Read-only first-layer initialization compatibility, not final receiver performance',
        validation_scene_indices=indices,selection='First two complete 24-condition cycles, selected before reading outcomes',
        branches=['completed pretrained classifier','current candidate classifier'],
        score_states=['original pretrained first score','selected depth-1 score after two epochs'],
        optimizer_updates=0,created_unix=time.time()))
    torch.set_num_threads(4);threadpool_limits(4)
    torch.backends.cuda.matmul.allow_tf32=True
    torch.backends.cudnn.allow_tf32=True
    torch.backends.cudnn.benchmark=True
    source=ROOT/'runs/proposed_auxiliary_100_cuda_graph_20261019/n50000/activity/evidence_best.pt'
    score_source=ROOT/common.CONFIG['pretrained_score']['path']
    selected=RUN/'checkpoints/depth_1/best.pt'
    protected={str(p):common.sha(p) for p in [source,score_source,selected,RUN/'checkpoints/depth_2/last.pt']}
    saved=torch.load(source,map_location='cpu',weights_only=False)
    completion=json.loads((source.parent/'complete.json').read_text(encoding='utf-8'))
    assert completion['weight_sha256']==protected[str(source)]
    assert saved['first_sha256']==protected[str(score_source)]
    assert saved['scale']==common.CONFIG['pretrained_score']['global_complex_rms']
    copies=[]
    for _ in range(5):
        net=EvidenceNetwork(Config(**saved['config']))
        net.load_state_dict(saved['state_dict'],strict=True)
        copies.append(net)
    for name,p in copies[0].named_parameters():
        tensors=[dict(net.named_parameters())[name] for net in copies]
        assert len({t.data_ptr() for t in tensors})==5
        assert all(torch.equal(t.detach(),saved['state_dict'][name]) for t in tensors)
    original=FrozenEvidence(source,device='cuda')
    parameters=sum(p.numel() for p in copies[0].parameters())
    del copies,saved
    first=torch.load(score_source,map_location='cpu',weights_only=False)
    torch.manual_seed(common.CONFIG['seed']+1)
    model=receiver.Receiver();model.add_layer(first['state_dict']);model.cuda().eval();model.use_checkpoint=False
    small_parameters=sum(p.numel() for p in model.layers[0].activity.parameters())
    cases=data.Cases('validation',first['global_complex_rms'],'cuda')
    results={};max_transfer_error=None
    with torch.no_grad():
        for stage in ['original_score','finetuned_depth1_score']:
            if stage=='finetuned_depth1_score':
                model.load_state_dict(torch.load(selected,map_location='cpu',weights_only=False)['state'])
            rows={'current_candidate_head':[],'pretrained_head':[]}
            probabilities={k:{'active':[],'inactive':[]} for k in rows}
            for position,index in enumerate(indices):
                public,labels,info=cases[index]
                outputs,diagnostics,messages=model(public,return_messages=True)
                r,mean=messages[0]['query'],messages[0]['conditional']
                v=r.new_full((len(r),),diagnostics[0]['query_variance'])
                z=original.network(r,v,mean)
                if max_transfer_error is None:
                    complex_array=lambda a:a[:,0].cpu().numpy()+1j*a[:,1].cpu().numpy()
                    reference=original.infer(complex_array(r),v.cpu().numpy(),complex_array(mean))
                    max_transfer_error=float(np.max(np.abs(reference-z.cpu().numpy())))
                    np.testing.assert_allclose(reference,z.cpu().numpy(),rtol=1e-5,atol=1e-5)
                pi=original.training_class_prior;rho=public['rho']
                logits=z-math.log(pi/(1-pi))+math.log(rho/(1-rho))
                p=torch.sigmoid(logits)
                alternatives={'current_candidate_head':outputs,
                    'pretrained_head':[(p[:,None,None,None,None]*mean,logits)]}
                active=labels['active'].bool()
                for branch,prediction in alternatives.items():
                    probability=torch.sigmoid(prediction[-1][1])
                    row=dict(**info,validation_index=index,**receiver.metrics(prediction,labels),
                        loss=float(receiver.loss(prediction,labels)),query_variance=float(v[0]),
                        active_probability_mean=float(probability[active].mean()),
                        inactive_probability_mean=float(probability[~active].mean()),
                        logit_min=float(prediction[-1][1].min()),logit_max=float(prediction[-1][1].max()),
                        out_of_pretraining_support=diagnostics[0]['out_of_pretraining_support'])
                    rows[branch].append(row)
                    probabilities[branch]['active'].extend(probability[active].cpu().tolist())
                    probabilities[branch]['inactive'].extend(probability[~active].cpu().tolist())
                if (position+1)%24==0:print(json.dumps(dict(stage=stage,scenes=position+1,total=len(indices))),flush=True)
            results[stage]={}
            for branch,branch_rows in rows.items():
                results[stage][branch]=dict(summary=receiver.summarize_rows(branch_rows),
                    probability_summary={group:dict(mean=float(np.mean(values)),median=float(np.median(values)))
                                         for group,values in probabilities[branch].items()},
                    by_condition=receiver.summarize_conditions(branch_rows),rows=branch_rows)
    assert all(common.sha(Path(p))==digest for p,digest in protected.items())
    report=dict(scope='48 fixed independent validation scenes; first-layer initialization diagnostic only. No evidence of final five-layer accuracy or stability.',
        optimizer_updates=0,source_hashes=protected,original_assets_unchanged=True,
        source_training_epochs=completion['epochs'],source_selected_epoch=completion['selected_epoch'],
        source_first_score_matched=True,scale_matched=True,five_independent_exact_copies=True,
        legacy_interface_max_absolute_logit_error=max_transfer_error,
        pretrained_classifier_parameters=parameters,current_small_classifier_parameters=small_parameters,
        posterior_conversion='z - logit(training_class_prior) + logit(public_activity_prior), applied exactly once',
        legacy_mean_feature_detached=True,
        training_gradient_note='Reusing the original EvidenceNetwork retains mean.detach(); any change to this gradient path must be an explicit training-protocol choice.',
        results=results)
    common.save_json(OUT/'REPORT.json',report)
    print(json.dumps({stage:{branch:dict(summary=value['summary'],probability_summary=value['probability_summary']) for branch,value in branches.items()}
        for stage,branches in results.items()},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
