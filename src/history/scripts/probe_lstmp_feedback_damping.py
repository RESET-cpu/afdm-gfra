"""No-training probes that damp Gaussian messages, separately from activity outputs."""
import json,math,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RUN=Path(r'D:\afdm-gfra-cpu\runs\lstmp_refinenet_50000_fast_20261019')
OUT=ROOT/'results/lstmp_feedback_damping_probe_20261019'
os.environ['AFDM_LSTMP_ROOT']=str(ROOT)
os.environ['AFDM_LSTMP_CONFIG']=str(RUN/'source_code/experiments/lstmp_candidate_20261019/reuse_50000_fast.json')
sys.path.insert(0,str(RUN/'source_code'))
import torch
from threadpoolctl import threadpool_limits
from experiments.lstmp_candidate_20261019 import common,data,receiver

MODES=['original','natural_variance_bound','natural_damp01','reject_uninformative','residual_line_preserve_probability']

def forward(model,public,mode):
    y,a,rho=public['y'],public['a'],public['rho']
    prior=y.new_zeros(public['channel_shape']);initial=y.new_tensor(rho*common.CONFIG['normalized_training_second_moment'])
    variance=initial;previous=prior
    outputs=[];diags=[]
    for layer in model.layers:
        r,v,_=receiver.linear_query(public,prior,variance,layer.calibration[0]);nv=v.expand(len(r))
        conditional=r+torch.exp(layer.calibration[1])*v/2*model.score_call(layer.score,r,nv)
        logits=layer.activity(r,nv,conditional,rho)
        estimate=torch.sigmoid(logits)[:,None,None,None,None]*conditional
        if mode=='residual_line_preserve_probability':
            res=a@data.pack(previous)-y;delta=estimate-previous;proj=a@data.pack(delta)
            b=(res.double()*proj.double()).sum();c=proj.double().square().sum()
            t=torch.where(2*b+c<=0,b.new_tensor(1.),(-b/c.clamp_min(1e-12)).clamp(0,1)).to(y.dtype)
            estimate=previous+t*delta
        residual=y-a@data.pack(estimate)
        frames,columns=y.shape[0]//2,y.shape[1]
        raw=(residual.square().sum()-frames*columns*public['noise'])/(columns*a.square().sum()/2)
        post,ratio=receiver.feedback_variance(raw,v,layer.calibration[2])
        new_mean=(estimate-ratio*r)/(1-ratio);new_var=post/(1-ratio)
        if mode=='natural_variance_bound':
            bounded=torch.minimum(new_var,initial)
            new_mean=new_mean*(bounded/new_var);new_var=bounded
        elif mode=='natural_damp01':
            mixed=1/(.9/variance+.1/new_var)
            new_mean=mixed*(.9*prior/variance+.1*new_mean/new_var);new_var=mixed
        elif mode=='reject_uninformative':
            new_mean=torch.where(new_var>initial,prior,new_mean)
            new_var=torch.where(new_var>initial,variance,new_var)
        diags.append(dict(query_variance=float(v),query_energy=float(2*r.square().mean()),raw_residual=float(raw),next_variance=float(new_var)))
        outputs.append((estimate,logits));prior,variance,previous=new_mean,new_var,estimate
    return outputs,diags

def main():
    if OUT.exists():raise FileExistsError(OUT)
    if (RUN/'RUNNING.lock').exists():raise RuntimeError('Training must remain stopped')
    OUT.mkdir(parents=True);torch.set_num_threads(4);threadpool_limits(4)
    torch.backends.cuda.matmul.allow_tf32=True;torch.backends.cudnn.allow_tf32=True;torch.backends.cudnn.benchmark=True
    state=torch.load(RUN/'checkpoints/depth_2/last.pt',map_location='cpu',weights_only=False)
    model=receiver.Receiver()
    for _ in range(2):model.add_layer(None)
    model.load_state_dict(state['state']);model.cuda().eval();model.use_checkpoint=False
    cases=data.Cases('validation',common.CONFIG['pretrained_score']['global_complex_rms'],'cuda')
    rows=[]
    with torch.no_grad():
        for index in [807,903]+list(range(24)):
            public,labels,info=cases[index]
            for mode in MODES:
                outputs,diags=forward(model,public,mode)
                row=dict(index=index,mode=mode,**receiver.metrics(outputs,labels),loss=float(receiver.loss(outputs,labels)),diagnostics=diags)
                rows.append(row)
                if index in [807,903]:print(json.dumps(dict(index=index,mode=mode,nmse_db=10*math.log10(row['nmse']),aer=(row['misses']+row['false_alarms'])/(row['active']+row['inactive']))),flush=True)
    summaries={m:receiver.summarize_rows([r for r in rows if r['mode']==m and r['index']<24]) for m in MODES}
    common.save_json(OUT/'REPORT.json',dict(scope='Development controls on already used validation cases; no independent acceptance, no optimizer steps.',rows=rows,normal_condition_summaries=summaries))
    print(json.dumps(summaries),flush=True)

if __name__=='__main__':main()
