"""Check actual pretrained integration and full-depth capacity before launch.

The disposable optimizer step tests memory and parameter updates. Its weights
are never used for the formal run, and no recovery-quality claim is made.
"""
import argparse
import json
import sys
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
import torch
from threadpoolctl import threadpool_limits
from experiments.lstmp_candidate_20261019 import common,data,receiver
from experiments.lstmp_candidate_20261019.optimization import clip_gradient_norm
from afdm_jadcedd.algorithm.proposed.network import load_direct_checkpoint
from afdm_jadcedd.experiment.generate import generate_case


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',required=True)
    parser.add_argument('--microbatch',type=int)
    args=parser.parse_args()
    output=Path(args.output)
    if output.exists():raise FileExistsError(output)
    cfg=common.CONFIG
    if args.microbatch:cfg['receiver']['microbatch']=args.microbatch
    torch.set_num_threads(cfg['cpu_threads']);threadpool_limits(cfg['cpu_threads'])
    torch.backends.cuda.matmul.allow_tf32=cfg['allow_tf32']
    torch.backends.cudnn.allow_tf32=cfg['allow_tf32']
    torch.backends.cudnn.benchmark=True
    source=ROOT/cfg['pretrained_score']['path'];before=common.sha(source)
    original,checkpoint=load_direct_checkpoint(source,'cuda')
    model=receiver.Receiver().cuda().train()
    torch.manual_seed(202610196900001)
    for _ in range(5):model.add_layer(checkpoint['state_dict'])
    model.cuda()
    pointers=[{p.data_ptr() for p in layer.score.parameters()} for layer in model.layers]
    assert all(not pointers[i]&pointers[j] for i in range(5) for j in range(i+1,5))
    x=torch.randn((3,2,16,16,16),device='cuda')
    v=torch.tensor([.001,.1,100.],device='cuda')
    with torch.no_grad():
        old=original(x,v);new=model.layers[0].score(x,v)
    torch.testing.assert_close(new,old,rtol=0,atol=0)
    del original,x,v,old,new
    scale=checkpoint['global_complex_rms'];del checkpoint
    records=[]
    for depth,users,frames in ((1,40,16),(5,100,24)):
        start=time.perf_counter()
        inp,truth,_=generate_case(202610196900010+depth,0.,scale,users=users,frames=frames,activity_probability=.2)
        generation_seconds=time.perf_counter()-start
        public,_=data.prepare_public(dict(y=inp['observation'],a=inp['operator'],noise=inp['noise_variance'],rho=inp['activity_prior']),
            scale,'cuda',phase_mode='known',noise_mode='known')
        labels=dict(x=common.real_tensor(truth['channel']/scale,'cuda'),active=torch.as_tensor(truth['activity'],dtype=torch.float32,device='cuda'))
        all_layers=model.layers
        model.layers=torch.nn.ModuleList(list(all_layers)[:depth])
        optimizer=torch.optim.Adam(model.parameters(),lr=2e-5,foreach=False)
        # Two passes measure warmed forward/backward; only the second takes an update.
        for repeat in range(2):
            optimizer.zero_grad(set_to_none=True);torch.cuda.reset_peak_memory_stats();torch.cuda.synchronize()
            start=time.perf_counter()
            outputs,diagnostics=model(public);value=receiver.loss(outputs,labels)
            assert torch.isfinite(value)
            value.backward()
            try:
                norm=clip_gradient_norm(model.parameters(),1.)
            except RuntimeError as error:
                gradient_details=[]
                for index,layer in enumerate(model.layers):
                    grads=[p.grad for p in layer.parameters() if p.grad is not None]
                    maximum=max(float(g.abs().max()) for g in grads)
                    gradient_details.append(dict(layer=index+1,finite=all(bool(torch.isfinite(g).all()) for g in grads),
                        max_abs=str(maximum),double_norm=str(float(torch.stack([g.double().norm() for g in grads]).norm()))))
                common.save_json(output.with_name('PREFLIGHT_FAILURE.json'),dict(error=str(error),records=records,
                    depth=depth,diagnostics=diagnostics,gradient_details=gradient_details,
                    source_preserved=common.sha(source)==before,formal_training_started=False))
                raise
            gradients=[]
            if repeat==1:
                for layer in model.layers:
                    gradients.append(dict(score_connected=any(p.grad is not None and bool((p.grad!=0).any()) for p in layer.score.parameters()),
                        activity_connected=any(p.grad is not None and bool((p.grad!=0).any()) for p in layer.activity.parameters()),
                        calibration_gradient=layer.calibration.grad.detach().cpu().tolist()))
                assert all(row['score_connected'] and row['activity_connected'] for row in gradients)
                optimizer.step()
            torch.cuda.synchronize();seconds=time.perf_counter()-start
            records.append(dict(depth=depth,users=users,frames=frames,repeat=repeat,seconds=seconds,
                peak_allocated_bytes=torch.cuda.max_memory_allocated(),gradient_norm=float(norm),
                gradients=gradients,disposable_optimizer_step=repeat==1,generation_seconds=generation_seconds))
            print(json.dumps(records[-1]),flush=True)
        del optimizer,outputs,value,public,labels
        model.zero_grad(set_to_none=True);model.layers=all_layers;torch.cuda.empty_cache()
    assert common.sha(source)==before
    report=dict(status='PASS',scope='Weight loading, coordinate equivalence, independent parameter storage, gradients and GPU capacity; not a recovery-quality evaluation',
        source_sha256=before,source_preserved=True,initial_score_output_exact=True,five_independent_scores=True,
        score_microbatch=cfg['receiver']['microbatch'],
        parameters_per_score=sum(p.numel() for p in model.layers[0].score.parameters()),records=records,
        formal_training_weights_unmodified=True,disposable_optimizer_steps=2)
    common.save_json(output,report)


if __name__=='__main__':main()
