"""Discarded forward/backward benchmark, using previously exposed scenes."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import time
import numpy as np
import torch
from threadpoolctl import threadpool_limits
import evaluate_saved_baseline_inputs as P
from afdm_jadcedd.algorithm.unfolded_score_candidate import UnfoldedReceiver,objective
from afdm_jadcedd.algorithm.proposed.network import load_direct_checkpoint
from afdm_jadcedd.algorithm.proposed.activity import FrozenEvidence
from afdm_jadcedd.algorithm.baselines.noise_estimation import estimate_spatial_noise


def main():
    destination=P.ROOT/'runs/unfolded_score_benchmark_20261019_v3'
    assert not destination.exists();destination.mkdir()
    torch.set_num_threads(1);torch.manual_seed(172)
    cfg=P.read(P.MODEL);score,_=load_direct_checkpoint(P.ROOT/cfg['first_checkpoint'])
    evidence=FrozenEvidence(P.ROOT/cfg['evidence_checkpoint'],device='cpu').network
    model=UnfoldedReceiver()
    for _ in range(5):model.grow(score,evidence,64)
    model.cuda().train();del score,evidence
    optimizer=torch.optim.AdamW(model.parameters(),lr=1e-5,fused=True)
    rows=[]
    for users in (20,100):
        bank=P.ROOT/f'runs/receiver_covariance_confirmation_20261019/bank/development/scene000_users{users}'
        data=P.arrays(bank/'input.npz');truth=P.arrays(bank/'truth.npz')
        make=lambda a:torch.tensor(a,device='cuda')
        y=make(data['observation']/cfg['scale']);a=make(data['operator'])
        noise=make(np.asarray(estimate_spatial_noise(data['observation'])[0]/cfg['scale']**2))
        prior=make(np.asarray(data['activity_prior']));target=make(truth['channel']/cfg['scale']);active=make(truth['activity'])
        optimizer.zero_grad(set_to_none=True);torch.cuda.reset_peak_memory_stats();started=time.monotonic()
        output=model(y,a,noise,prior);loss,parts=objective(output,target,active,prior)
        torch.cuda.synchronize();forward_seconds=time.monotonic()-started
        assert torch.isfinite(loss);loss.backward()
        norm=torch.nn.utils.clip_grad_norm_(model.parameters(),10.,error_if_nonfinite=True)
        optimizer.step();torch.cuda.synchronize()
        rows.append(dict(users=users,parameters=sum(p.numel() for p in model.parameters()),
            trainable_parameters=sum(p.numel() for p in model.parameters() if p.requires_grad),
            seconds=time.monotonic()-started,forward_seconds=forward_seconds,
            peak_mib=torch.cuda.max_memory_allocated()/2**20,loss=float(loss.detach()),gradient_norm=float(norm),
            layer_nmse_db=[float(10*torch.log10(v.detach())) for v in parts['nmse']],
            variance=[{k:float(v.detach()) for k,v in o['diagnostics'].items()} for o in output]))
        P.save(destination/'PROGRESS.json',dict(results=rows,weights_discarded=True))
        print(rows[-1],flush=True)
        del output,loss,parts
    P.save(destination/'REPORT.json',dict(results=rows,weights_discarded=True,
        benchmark_cases_previously_exposed=True,training_weights_created=False))


if __name__=='__main__':
    with threadpool_limits(1):main()
