"""Compare execution paths on a disposable copy of a paused checkpoint."""
from copy import deepcopy
import json
from pathlib import Path
import time

import numpy as np
import torch

from project import ROOT
from utils import sha256, state_sha
from training.STMP.auxiliary import atomic_json
from training.colored_activity_20261025.run import Trainer, read
from training.colored_activity_20261025.batches import ActivityGraph
from training.scores.cuda_graph_auxiliary import query_parts
from .execution import Prefetch, PinnedActivityGraph


def main():
    torch.set_num_threads(1)
    cfg=read(ROOT/'src/configs/training/colored_activity_20261025.json')
    out=ROOT/cfg['output']; status=read(out/'status.json')
    if status['status']!='PAUSED':
        raise ValueError('Pause original trainer for an uncontended benchmark')
    trainer=Trainer(cfg,out,read(out/'specification.json'))
    state=torch.load(out/'last.pt',map_location='cpu',weights_only=False)
    first_hash=state_sha(trainer.first)
    indices=state['indices'] if state['indices'] is not None else np.arange(50000)
    # Benchmark own stream on real training data; never write candidate weights.
    indices=np.tile(indices,2)
    def rng():
        r=np.random.default_rng();r.bit_generator.state=deepcopy(state['rng']);return r
    def build(fast):
        model=trainer.model();model.load_state_dict(state['model']);model.train()
        ema=deepcopy(model).eval().requires_grad_(False);ema.load_state_dict(state['ema'])
        optimizer=torch.optim.Adam(model.parameters(),lr=cfg['activity']['learning_rate'])
        optimizer.load_state_dict(deepcopy(state['optimizer']))
        graph=(PinnedActivityGraph if fast else ActivityGraph)(model,trainer.first,'activity',32)
        return model,ema,optimizer,graph
    def step(objects,parts):
        model,ema,optimizer,graph=objects
        optimizer.zero_grad(set_to_none=True)
        losses=graph.backward(parts)
        norm=torch.nn.utils.clip_grad_norm_(model.parameters(),1.,error_if_nonfinite=True)
        optimizer.step()
        with torch.no_grad():
            torch._foreach_lerp_(list(ema.parameters()),list(model.parameters()),.001)
        return losses,norm
    old,new=build(False),build(True)
    a,b=rng(),rng();prefetch=Prefetch(trainer.data['train'],indices,0,b,trainer.prior,trainer.settings,new[3].validate)
    max_parameter=0.;max_gradient=0.;max_loss=0.
    try:
        for i in range(8):
            arrays=query_parts(trainer.data['train'],indices[i*32:(i+1)*32],a,trainer.prior,trainer.settings,'activity')
            batch=prefetch.next(i*32,b)
            for p,q in zip(arrays,batch.arrays):
                for x,y in zip(p,q):np.testing.assert_array_equal(x,y)
            assert a.bit_generator.state==b.bit_generator.state
            l1,_=step(old,arrays);l2,_=step(new,batch)
            np.testing.assert_allclose(l1,l2,rtol=2e-5,atol=2e-6)
            max_loss=max(max_loss,float(abs(np.asarray(l1)-np.asarray(l2)).max()))
            for p,q in zip(old[0].parameters(),new[0].parameters()):
                torch.testing.assert_close(p,q,rtol=1e-5,atol=2e-7)
                torch.testing.assert_close(p.grad,q.grad,rtol=1e-4,atol=1e-6)
                max_parameter=max(max_parameter,float((p-q).abs().max()))
                max_gradient=max(max_gradient,float((p.grad-q.grad).abs().max()))
            for p,q in zip(old[1].parameters(),new[1].parameters()):
                torch.testing.assert_close(p,q,rtol=1e-5,atol=2e-7)
    finally:prefetch.close()
    # Discarding a future at a checkpoint must not consume its RNG sequence.
    saved=deepcopy(b.bit_generator.state)
    resumed=np.random.default_rng();resumed.bit_generator.state=saved
    prefetched=Prefetch(trainer.data['train'],indices,8*32,b,trainer.prior,trainer.settings,new[3].validate)
    try:
        batch=prefetched.next(8*32,b)
        reference=query_parts(trainer.data['train'],indices[8*32:9*32],resumed,trainer.prior,trainer.settings,'activity')
        for p,q in zip(reference,batch.arrays):
            for x,y in zip(p,q):np.testing.assert_array_equal(x,y)
        assert resumed.bit_generator.state==b.bit_generator.state
    finally:prefetched.close()
    timings=[]
    for fast in (False,True,True,False):
        objects=new if fast else old
        r=rng();pf=Prefetch(trainer.data['train'],indices,0,r,trainer.prior,trainer.settings,objects[3].validate) if fast else None
        started=time.perf_counter()
        try:
            for i in range(150):
                parts=pf.next(i*32,r) if fast else query_parts(trainer.data['train'],indices[i*32:(i+1)*32],r,trainer.prior,trainer.settings,'activity')
                step(objects,parts)
            torch.cuda.synchronize()
            timings.append(dict(fast=fast,steps=150,seconds=time.perf_counter()-started))
        finally:
            if pf:pf.close()
    old_time=np.mean([t['seconds'] for t in timings if not t['fast']])
    new_time=np.mean([t['seconds'] for t in timings if t['fast']])
    assert state_sha(trainer.first)==first_hash
    result=dict(status='PASS',parent_checkpoint_sha256=sha256(out/'last.pt'),
        original_specification_sha256=sha256(out/'specification.json'),query_rng_exact=True,
        resume_rng_exact=True,teacher_unchanged=True,maximum_parameter_difference=max_parameter,
        maximum_gradient_difference=max_gradient,maximum_loss_difference=max_loss,
        timings=timings,speedup=float(old_time/new_time),old_step_seconds=float(old_time/150),
        new_step_seconds=float(new_time/150),checkpoint_epoch=state['epoch'],checkpoint_cursor=state['cursor'],
        source_hashes={str(p.relative_to(ROOT)):sha256(p) for p in Path(__file__).parent.glob('*.py')},
        scope='Disposable paired performance check; all training samples/noise and Adam/EMA kept identical; no weight selection or receiver evaluation')
    atomic_json(out/'acceleration_20261025'/'BENCHMARK.json',result)
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
