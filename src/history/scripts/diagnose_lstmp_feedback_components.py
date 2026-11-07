"""Frozen-weight causal probes; oracle controls are diagnostic only."""
import json, math, os, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RUN=Path(r'D:\afdm-gfra-cpu\runs\lstmp_refinenet_50000_fast_20261019')
OUT=ROOT/'results/lstmp_feedback_components_20261019'
os.environ['AFDM_LSTMP_ROOT']=str(ROOT)
os.environ['AFDM_LSTMP_CONFIG']=str(RUN/'source_code/experiments/lstmp_candidate_20261019/reuse_50000_fast.json')
sys.path.insert(0,str(RUN/'source_code'))
import torch
from threadpoolctl import threadpool_limits
from experiments.lstmp_candidate_20261019 import common,data,receiver
from experiments.lstmp_candidate_20261019.backbone import make_score


def report(output,labels):
    result=receiver.metrics([output],labels)
    result['nmse_db']=10*math.log10(result['nmse'])
    result['aer']=(result['misses']+result['false_alarms'])/(result['active']+result['inactive'])
    return result


def nonlinear(model,layer,r,v,rho,score_model=None,unit_scale=False):
    score=model.score_call(score_model or layer.score,r,v.expand(len(r)))
    denoised=r+(1 if unit_scale else torch.exp(layer.calibration[1]))*v/2*score
    logits=layer.activity(r,v.expand(len(r)),denoised,rho)
    return torch.sigmoid(logits)[:,None,None,None,None]*denoised,logits,denoised


def main():
    if OUT.exists():raise FileExistsError(OUT)
    if (RUN/'RUNNING.lock').exists():raise RuntimeError('Training must remain stopped')
    OUT.mkdir(parents=True)
    torch.set_num_threads(4);threadpool_limits(4)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    state=torch.load(RUN/'checkpoints/depth_2/last.pt',map_location='cpu',weights_only=False)
    model=receiver.Receiver()
    for _ in range(2):model.add_layer(None)
    model.load_state_dict(state['state']);model.cuda().eval();model.use_checkpoint=False
    pretrained=make_score().cuda().eval()
    pretrained.load_state_dict(torch.load(ROOT/common.CONFIG['pretrained_score']['path'],map_location='cpu',weights_only=False)['state_dict'])
    cases=data.Cases('validation',common.CONFIG['pretrained_score']['global_complex_rms'],'cuda')
    results=[]
    with torch.no_grad():
        for index in [807,903,0,1,2,3,7,11,15,19,23]:
            public,labels,info=cases[index]
            native,diagnostics,messages=model(public,return_messages=True)
            row=dict(index=index,info=info,layers=[],feedback_controls=[])
            for k,(layer,msg,diag) in enumerate(zip(model.layers,messages,diagnostics)):
                r=msg['query'];v=r.new_tensor(diag['query_variance'])
                actual_mse=2*(r-labels['x']).square().mean()
                item=dict(layer=k+1,query_variance=float(v),query_actual_mse=float(actual_mse),native=report(native[k],labels),scores=[])
                for name,net,unit in [('current',layer.score,False),('current_unit_scale',layer.score,True),('pretrained_unit_scale',pretrained,True)]:
                    for source in ['actual_message','matched_awgn']:
                        if source=='actual_message':query=r
                        else:
                            gen=torch.Generator(device='cuda').manual_seed(index*17+k+101)
                            query=labels['x']+torch.randn(r.shape,generator=gen,device='cuda')*torch.sqrt(v/2)
                        x,logits,conditional=nonlinear(model,layer,query,v,public['rho'],net,unit)
                        active=labels['active'].bool()
                        item['scores'].append(dict(network=name,input=source,**report((x,logits),labels),
                            conditional_active_nmse=float((conditional[active]-labels['x'][active]).square().sum()/labels['x'][active].square().sum()),
                            conditional_energy=float(2*conditional.square().mean())))
                row['layers'].append(item)
            first=model.layers[0];r=messages[0]['query'];v=r.new_tensor(diagnostics[0]['query_variance'])
            x,logits=native[0];variance0=r.new_tensor(public['rho']*common.CONFIG['normalized_training_second_moment'])
            projected=data.pack(r);f0=2*(x-labels['x']).square().mean()/v
            alpha=[]
            for n in range(4):
                gen=torch.Generator(device='cuda').manual_seed(index*100+n+55)
                z=torch.randn(r.shape,generator=gen,device='cuda')
                eps=torch.sqrt(v/2)*1e-3
                plus=nonlinear(model,first,r+eps*z,v,public['rho'])[0]
                minus=nonlinear(model,first,r-eps*z,v,public['rho'])[0]
                alpha.append(float((z*(plus-minus)/(2*eps)).mean()))
            row['derivative_probes']=alpha
            controls=[('native_residual_ratio',r.new_tensor(diagnostics[0]['feedback_ratio'])),
                      ('zero_extrinsic_subtraction',r.new_tensor(0.)),
                      ('oracle_actual_mse_ratio',f0),
                      ('hutchinson_derivative_ratio',r.new_tensor(sum(alpha)/len(alpha)).clamp(1e-6,.95))]
            for name,ratio in controls:
                prior=(x-ratio*r)/(1-ratio)
                nextv=(v*ratio/(1-ratio)).clamp_min(1e-6) if name!='zero_extrinsic_subtraction' else variance0
                query,nv,_=receiver.linear_query(public,prior,nextv,model.layers[1].calibration[0])
                ox,ol,conditional=nonlinear(model,model.layers[1],query,nv,public['rho'])
                row['feedback_controls'].append(dict(control=name,ratio=float(ratio),query_variance=float(nv),
                    query_actual_mse=float(2*(query-labels['x']).square().mean()),**report((ox,ol),labels)))
            results.append(row)
            print(json.dumps(dict(index=index,controls=[{k:v for k,v in p.items() if k in ['control','nmse_db','aer','ratio','query_variance']} for p in row['feedback_controls']])),flush=True)
    common.save_json(OUT/'REPORT.json',dict(scope='Frozen trained checkpoint. Oracle actual MSE controls use truth, are not deployable repairs. No optimizer steps.',rows=results))


if __name__=='__main__':main()
