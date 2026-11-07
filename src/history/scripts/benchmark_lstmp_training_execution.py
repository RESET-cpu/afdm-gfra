"""Discarded paired execution benchmarks, using existing training scenes only."""
import copy
import gc
import json
import os
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RUN=Path(r'D:\afdm-gfra-cpu\runs\lstmp_refinenet_50000_fixed_budget_20261019')
OUT=ROOT/'results/lstmp_execution_benchmark_20261019'
os.environ['AFDM_LSTMP_ROOT']=str(ROOT)
os.environ['AFDM_LSTMP_CONFIG']=str(RUN/'source_code/experiments/lstmp_candidate_20261019/reuse_50000_fixed_budget.json')
sys.path.insert(0,str(RUN/'source_code'))
import numpy as np
import torch
from threadpoolctl import threadpool_limits
from experiments.lstmp_candidate_20261019 import common,data,receiver
from experiments.lstmp_candidate_20261019.optimization import clip_gradient_norm


def make_optimizer(model,saved,mode):
    s=common.CONFIG['receiver']
    optimizer=torch.optim.Adam([
        dict(params=[p for layer in model.layers for p in layer.score.parameters() if p.requires_grad],lr=s['learning_rate']),
        dict(params=[p for layer in model.layers for p in layer.activity.parameters() if p.requires_grad],lr=s['activity_learning_rate']),
        dict(params=[layer.calibration for layer in model.layers],lr=s['calibration_learning_rate'])],foreach=False)
    optimizer.load_state_dict(copy.deepcopy(saved))
    for group in optimizer.param_groups:
        group['foreach']=mode=='foreach'
        group['fused']=mode=='fused'
    for state in optimizer.state.values():
        state['step']=state['step'].to('cuda' if mode=='fused' else 'cpu')
    return optimizer


def sync():torch.cuda.synchronize()


def step(model,optimizer,case,phases=False):
    public,labels,_=case
    optimizer.zero_grad(set_to_none=True)
    sync();start=time.perf_counter();last=start;times={}
    outputs,_=model(public)
    value=receiver.loss(outputs,labels)
    if not bool(torch.isfinite(value)):raise FloatingPointError('Nonfinite benchmark loss')
    if phases:sync();now=time.perf_counter();times['forward_loss']=now-last;last=now
    value.backward()
    if phases:sync();now=time.perf_counter();times['backward']=now-last;last=now
    norm=clip_gradient_norm(model.parameters(),1.)
    if phases:sync();now=time.perf_counter();times['clip']=now-last;last=now
    optimizer.step()
    sync();now=time.perf_counter()
    if phases:times['adam']=now-last
    return dict(seconds=now-start,loss=float(value.detach()),gradient_norm=float(norm),phases=times)


def main():
    assert not (RUN/'RUNNING.lock').exists()
    OUT.mkdir(exist_ok=True)
    if (OUT/'REPORT.json').exists():raise FileExistsError(OUT/'REPORT.json')
    torch.set_num_threads(4);threadpool_limits(4)
    torch.backends.cuda.matmul.allow_tf32=True
    torch.backends.cudnn.allow_tf32=True
    torch.backends.cudnn.benchmark=True
    path=RUN/'checkpoints/depth_2/last.pt'
    original_sha=common.sha(path)
    saved=torch.load(path,map_location='cpu',weights_only=False)
    first=torch.load(ROOT/common.CONFIG['pretrained_score']['path'],map_location='cpu',weights_only=False)
    cases=data.Cases('train',first['global_complex_rms'],'cuda')
    positions=[next(i for i,p in enumerate(cases.indices) if p%24==j) for j in (0,4,8,12,16,20)]
    fixed=[cases[i] for i in positions]
    common.save_json(OUT/'PLAN.json',dict(source_checkpoint=str(path),source_sha256=original_sha,
        source_steps=saved['steps'],source_depth=saved['depth'],training_positions=positions,
        training_source_indices=[cases.indices[i] for i in positions],fixed_warmup_steps=6,fixed_timed_steps=12,
        no_source_weight_updates=True,benchmark_weights_discarded=True))
    variants=[('reference',True,'single'),('fused_adam',True,'fused'),
              ('no_recomputation_fused_adam',False,'fused'),('foreach_adam',True,'foreach')]
    results={};reference_after=None;reference_first=None
    for name,use_checkpoint,mode in variants:
        gc.collect();torch.cuda.empty_cache()
        model=receiver.Receiver()
        for _ in range(2):model.add_layer(None)
        model.load_state_dict(saved['state']);model.cuda().train();model.use_checkpoint=use_checkpoint
        optimizer=make_optimizer(model,saved['optimizer'],mode)
        torch.cuda.reset_peak_memory_stats()
        try:
            first_step=step(model,optimizer,fixed[0])
            if reference_after is None:
                reference_after=common.cpu_state(model);reference_first=first_step
                comparison=dict(reference=True)
            else:
                errors=[];numerator=denominator=0.
                for k,t in model.state_dict().items():
                    a=t.detach().double().cpu();b=reference_after[k].double()
                    delta=(a-b).abs();errors.append(float(delta.max()))
                    numerator+=float((a-b).square().sum());denominator+=float(b.square().sum())
                comparison=dict(maximum_absolute_parameter_difference=max(errors),
                    relative_parameter_l2=(numerator/max(denominator,1e-30))**.5,
                    loss_absolute_difference=abs(first_step['loss']-reference_first['loss']))
            for case in fixed[1:]:step(model,optimizer,case)
            rows=[dict(case=i%6,**step(model,optimizer,fixed[i%6])) for i in range(12)]
            phased=step(model,optimizer,fixed[2],True)
            results[name]=dict(mean_seconds=float(np.mean([r['seconds'] for r in rows])),
                median_seconds=float(np.median([r['seconds'] for r in rows])),
                peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30,
                peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30,
                one_step_comparison=comparison,users100_phase_timing=phased,rows=rows)
        except torch.OutOfMemoryError as error:
            results[name]=dict(error=str(error),out_of_memory=True)
        common.save_json(OUT/'PROGRESS.json',results)
        print(json.dumps(dict(variant=name,**{k:v for k,v in results[name].items() if k!='rows'})),flush=True)
        del model,optimizer;gc.collect();torch.cuda.empty_cache()
    assert common.sha(path)==original_sha
    common.save_json(OUT/'REPORT.json',dict(source_preserved=True,weights_discarded=True,results=results))


if __name__=='__main__':main()
