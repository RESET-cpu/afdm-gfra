"""Controlled frozen-weight probes on the two previously identified failures."""
import json,math,os,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RUN=Path(r'D:\afdm-gfra-cpu\runs\lstmp_refinenet_50000_fast_20261019')
OUT=ROOT/'results/lstmp_depth2_stability_probe_quadratic_20261019'
os.environ['AFDM_LSTMP_ROOT']=str(ROOT)
os.environ['AFDM_LSTMP_CONFIG']=str(RUN/'source_code/experiments/lstmp_candidate_20261019/reuse_50000_fast.json')
sys.path.insert(0,str(RUN/'source_code'))
import torch
import numpy as np
from threadpoolctl import threadpool_limits
from experiments.lstmp_candidate_20261019 import common,data,receiver

MODES=('original','quadratic_line_search','residual_line_search')


def forward(model,public,mode):
    y,a,rho=public['y'],public['a'],public['rho']
    prior=y.new_zeros(public['channel_shape'])
    initial=rho*common.CONFIG['normalized_training_second_moment']
    variance=y.new_tensor(initial)
    previous=prior
    previous_probability=y.new_full((len(prior),),rho)
    outputs,diags=[],[]
    for i,layer in enumerate(model.layers):
        r,v,analytical=receiver.linear_query(public,prior,variance,layer.calibration[0])
        original_v=v
        score_input=r
        if mode=='query_variance_only_cap':v=v.clamp(max=100.)
        nv=v.expand(len(r))
        if mode=='condition_only_cap':nv=nv.clamp(max=100.)
        factor=torch.sqrt((100./v).clamp(max=1.)) if mode=='rescale_query' else r.new_tensor(1.)
        score_input=r*factor
        score=model.score_call(layer.score,score_input,nv*factor.square())
        conditional=(score_input+torch.exp(layer.calibration[1])*v*factor.square()/2*score)/factor
        if mode=='gaussian_outside_support' and bool(v>100):conditional=r/(1+v)
        logits=layer.activity(r,nv,conditional,rho)
        probability=torch.sigmoid(logits)
        estimate=probability[:,None,None,None,None]*conditional
        damping=y.new_tensor(1.)
        if mode in ('quadratic_line_search','residual_line_search'):
            penalty=public['noise']/initial if mode=='quadratic_line_search' else 0.
            old_residual=a@data.pack(previous)-y
            difference=estimate-previous
            projected=a@data.pack(difference)
            slope=(old_residual*projected).sum()+penalty*(previous*difference).sum()
            curvature=projected.square().sum()+penalty*difference.square().sum()
            minimizer=(-slope/curvature.clamp_min(torch.finfo(y.dtype).tiny)).clamp(0.,1.)
            damping=torch.where(2*slope+curvature<=0,y.new_tensor(1.),minimizer)
            estimate=previous+damping*difference
            mixed=previous_probability+damping*(probability-previous_probability)
            logits=torch.where(damping==1,logits,torch.logit(mixed.clamp(1e-7,1-1e-7)))
            previous,previous_probability=estimate,torch.sigmoid(logits)
        if mode=='previous_outside_support' and bool(v>100) and outputs:
            estimate,logits=outputs[-1]
        residual=y-a@data.pack(estimate)
        frames,columns=y.shape[0]//2,y.shape[1]
        raw=(residual.square().sum()-frames*columns*public['noise'])/(columns*a.square().sum()/2)
        post_v,ratio=receiver.feedback_variance(raw,v,layer.calibration[2])
        raw_post_v=post_v
        if mode=='posterior_variance_prior_cap':post_v=post_v.clamp(max=initial);ratio=post_v/v
        if mode=='posterior_variance_incoming_cap':post_v=torch.minimum(post_v,variance);ratio=post_v/v
        diags.append(dict(layer=i+1,query_variance=float(original_v),effective_query_variance=float(v),
            damping=float(damping),
            query_energy=float(2*r.square().mean()),conditional_energy=float(2*conditional.square().mean()),
            raw_feedback=float(raw_post_v),feedback=float(post_v),ratio=float(ratio),
            min_probability=float(torch.sigmoid(logits).min()),max_probability=float(torch.sigmoid(logits).max())))
        prior=(estimate-ratio*r)/(1-ratio);variance=post_v/(1-ratio)
        outputs.append((estimate,logits))
    return outputs,diags


def main():
    if OUT.exists():raise FileExistsError(OUT)
    OUT.mkdir(parents=True)
    if (RUN/'RUNNING.lock').exists():raise RuntimeError('Training must remain stopped')
    torch.set_num_threads(4);threadpool_limits(4)
    torch.backends.cuda.matmul.allow_tf32=True;torch.backends.cudnn.allow_tf32=True;torch.backends.cudnn.benchmark=True
    path=RUN/'checkpoints/depth_2/last.pt';digest=common.sha(path)
    state=torch.load(path,map_location='cpu',weights_only=False)
    model=receiver.Receiver()
    for _ in range(2):model.add_layer(None)
    model.load_state_dict(state['state']);del state
    model.cuda().eval();model.use_checkpoint=False
    cases=data.Cases('validation',common.CONFIG['pretrained_score']['global_complex_rms'],'cuda')
    rows=[]
    with torch.no_grad():
        for index in (807,903):
            public,labels,info=cases[index]
            native,_=model(public)
            for mode in MODES:
                outputs,diagnostics=forward(model,public,mode)
                if mode=='original':
                    for a,b in zip(outputs,native):
                        torch.testing.assert_close(a[0],b[0],rtol=1e-5,atol=1e-5)
                row=dict(case_index=index,mode=mode,**receiver.metrics(outputs,labels),
                    loss=float(receiver.loss(outputs,labels)),diagnostics=diagnostics)
                rows.append(row)
                print(json.dumps(dict(case=index,mode=mode,nmse_db=10*math.log10(row['nmse']),aer=(row['misses']+row['false_alarms'])/(row['active']+row['inactive']),query_variance=diagnostics[-1]['query_variance'])),flush=True)
    assert common.sha(path)==digest
    common.save_json(OUT/'REPORT.json',dict(scope='Two known validation failures; diagnostic interventions, not independent acceptance. No optimizer updates.',checkpoint_sha256=digest,modes=MODES,rows=rows))


if __name__=='__main__':main()
