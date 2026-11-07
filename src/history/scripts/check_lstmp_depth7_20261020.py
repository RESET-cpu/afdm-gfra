"""Independent development checks; all optimizer updates here are discarded."""
import copy
import gc
import importlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
from threadpoolctl import threadpool_limits

from prepare_lstmp_depth7_20261020 import ROOT, TARGET, SOURCE, CHECKS, read, write, sha

os.environ['AFDM_LSTMP_ROOT'] = str(ROOT)
os.environ['AFDM_LSTMP_CONFIG'] = str(TARGET/'source_code/experiments/lstmp_candidate_20261019/reuse_50000_fast.json')
sys.path.insert(0, str(TARGET/'source_code'))
from experiments.lstmp_candidate_20261019 import common, data, receiver, extension
from experiments.lstmp_candidate_20261019.execution import configure_execution
from experiments.lstmp_candidate_20261019.optimization import clip_gradient_norm


def model_at(depth, state):
    model = receiver.Receiver()
    for _ in range(5):
        model.add_layer(None)
    model.load_state_dict(state)
    while len(model.layers) < depth:
        extension.append_trained_layer(model)
    return model.cuda()


def main():
    started = time.time()
    assert not (TARGET/'RUNNING.lock').exists()
    assert not (CHECKS/'REPORT.json').exists()
    CHECKS.mkdir(exist_ok=True)
    torch.set_num_threads(4); threadpool_limits(4)
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cudnn.benchmark = True
    config = common.CONFIG
    checkpoint = TARGET/'checkpoints/depth_5/best.pt'
    digest = sha(checkpoint)
    saved = torch.load(checkpoint, map_location='cpu', weights_only=False, mmap=True)
    scale = config['pretrained_score']['global_complex_rms']
    specs = [(k, q, p, snr) for k, q, p in [(20,8,.05),(40,16,.1),(100,24,.2),(100,8,.1),(20,24,.1),(40,12,.2)]
             for snr in (-5, 0, 5, 10)]
    seeds = list(range(202610209100001, 202610209100025))
    write(CHECKS/'PLAN.json', dict(parent_sha256=digest, seeds=seeds,
        cases=[dict(users=k,frames=q,activity_probability=p,snr_db=s) for k,q,p,s in specs],
        no_test_inputs=True, stages=[6,7], purpose='Numerical, gradient, memory and execution checks, not trained performance',
        updates_discarded=True, thresholds=dict(prefix_rtol=1e-5,prefix_atol=1e-6,maximum_initial_nmse_ratio=100.)))
    cases = []
    for seed, (k, q, p, snr) in zip(seeds, specs):
        inputs, truth, _ = data.generate_case(seed, snr, scale, users=k, frames=q, activity_probability=p)
        public, _ = data.prepare_public(dict(y=inputs['observation'], a=inputs['operator'],
            noise=inputs['noise_variance'], rho=inputs['activity_prior']), scale, 'cpu', phase_mode='known', noise_mode='known')
        labels = dict(x=common.real_tensor(truth['channel']/scale,'cpu'),
                      active=torch.tensor(truth['activity'],dtype=torch.float32),physical_scale=scale)
        cases.append((public, labels))
    def move(case):
        return tuple({k:v.cuda() if torch.is_tensor(v) else v for k,v in x.items()} for x in case)
    model = model_at(7, saved['state']).eval()
    configure_execution(model, extension.make_optimizer(model, extension.eligible_parameters(model)), config['execution'], 'cuda')
    assert all(a.data_ptr() != b.data_ptr() for a,b in zip(model.layers[-2].parameters(),model.layers[-1].parameters()))
    initial = []
    with torch.no_grad():
        for seed, spec, case in zip(seeds,specs,cases):
            public, labels = move(case)
            outputs, diagnostics = model(public)
            ms = [receiver.metrics(outputs[:depth],labels) for depth in (5,6,7)]
            assert all(np.isfinite(m['nmse']) for m in ms)
            assert max(m['nmse'] for m in ms[1:]) < 100*ms[0]['nmse']
            assert all(d['next_variance']>0 and np.isfinite(d['next_variance']) for d in diagnostics)
            initial.append(dict(seed=seed,condition=spec,nmse=[m['nmse'] for m in ms],diagnostics=diagnostics))
    # Prefix and loss equality at depth5 against the parent's frozen receiver.
    parent_base_path=SOURCE/'source_code/experiments/lstmp_candidate_20261019/receiver_base.py'
    spec=importlib.util.spec_from_file_location('experiments.lstmp_candidate_20261019.parent_base_check',parent_base_path)
    parent_base=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent_base)
    public,labels=move(cases[5])
    with torch.no_grad():
        seven,_=model(public)
        last_two=model.layers[-2:]
        model.layers=model.layers[:5]
        five,_=model(public)
        for a,b in zip(five,seven[:5]):
            for x,y in zip(a,b):torch.testing.assert_close(x,y,rtol=1e-5,atol=1e-6)
        torch.testing.assert_close(receiver.loss(five,labels),parent_base.loss(five,labels),rtol=1e-7,atol=1e-7)
        model.layers.extend(last_two)
    del model,outputs,seven,five,public,labels,last_two;gc.collect();torch.cuda.empty_cache()
    profiles=[]
    # One representative scene per K/Q group. Training order/weights are not touched.
    positions=[0,4,8,12,16,20]
    for depth in (6,7):
        model=model_at(depth,saved['state'])
        eligible=extension.eligible_parameters(model)
        optimizer=extension.make_optimizer(model,eligible)
        configure_execution(model,optimizer,config['execution'],'cuda')
        for adaptation in (True,False):
            extension.set_phase(model,eligible,adaptation)
            before=common.cpu_state(model) if adaptation else None
            model.train();rows=[];torch.cuda.reset_peak_memory_stats()
            boundary_gradients=[]
            for position in positions*2:
                public,labels=move(cases[position])
                optimizer.zero_grad(set_to_none=True)
                torch.cuda.synchronize();t=time.perf_counter()
                outputs,diagnostics=model(public)
                value=receiver.loss(outputs,labels);assert bool(torch.isfinite(value))
                value.backward();norm=clip_gradient_norm(model.parameters(),1.)
                g=model.layers[-2].calibration.grad
                boundary_gradients.append(float(g[2]))
                if adaptation: assert torch.equal(g[:2],torch.zeros_like(g[:2]))
                optimizer.step();torch.cuda.synchronize()
                rows.append(dict(position=position,seconds=time.perf_counter()-t,loss=float(value.detach()),gradient_norm=float(norm)))
            if adaptation:
                changed=[]
                for name,value in model.state_dict().items():
                    if not torch.equal(value.cpu(),before[name]):changed.append(name)
                allowed=lambda n:n.startswith(f'layers.{depth-1}.') or n==f'layers.{depth-2}.calibration'
                assert all(allowed(n) for n in changed),changed
                torch.testing.assert_close(model.layers[-2].calibration[:2].cpu(),before[f'layers.{depth-2}.calibration'][:2],rtol=0,atol=0)
                assert any(abs(g)>0 for g in boundary_gradients)
                assert any('.score.' in n for n in changed) and any('.activity.' in n for n in changed)
                del before
            free,total=torch.cuda.mem_get_info()
            profile=dict(depth=depth,phase='ADAPTATION' if adaptation else 'JOINT',
                mean_step_seconds=float(np.mean([r['seconds'] for r in rows[6:]])),
                peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30,
                peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30,
                free_gib=free/2**30,rows=rows,boundary_gradients=boundary_gradients)
            profiles.append(profile);write(CHECKS/'PROGRESS.json',profiles)
            print(json.dumps({k:v for k,v in profile.items() if k not in ('rows','boundary_gradients')}),flush=True)
            assert free > 512*2**20, 'Insufficient measured memory margin'
        extension.set_phase(model,eligible,False)
        del model,optimizer,outputs,public,labels;gc.collect();torch.cuda.empty_cache()
    assert sha(checkpoint)==digest==sha(SOURCE/'checkpoints/depth_5/best.pt')
    elapsed=time.time()-started
    report=dict(status='PASSED',elapsed_seconds=elapsed,manifest_sha256=sha(TARGET/'MANIFEST.json'),
        parent_sha256=digest,initialization_rows=initial,profiles=profiles,independent_parameter_storage=True,
        depth5_outputs_and_loss_preserved=True,adaptation_scope_verified=True,boundary_gradient_verified=True,
        weights_discarded=True,optimizer_updates_persisted=0,
        scope='Numerical and capacity checks only; deeper receiver has not been trained or proven superior.')
    write(CHECKS/'REPORT.json',report)
    write(TARGET/'protocol/PREFLIGHT.json',dict(status='PASSED',manifest_sha256=sha(TARGET/'MANIFEST.json'),
        report=str(CHECKS/'REPORT.json'),report_sha256=sha(CHECKS/'REPORT.json'),elapsed_seconds=elapsed))
    usage=read(TARGET/'ACTIVE_TIME.json')
    usage['consumed_seconds']+=elapsed;usage['development_preflight_seconds']=elapsed
    write(TARGET/'ACTIVE_TIME.json',usage)
    print(json.dumps(dict(status='PASSED',elapsed_seconds=elapsed,training_step_estimate_seconds=sum(p['mean_step_seconds']*4800 for p in profiles))),flush=True)


if __name__=='__main__':main()
