"""Mathematical readout and resumability checks for second-score training."""
from copy import deepcopy
from dataclasses import asdict
import json

import numpy as np
import pytest
import torch
from torch import nn

from networks.score import DirectCaiConfig, DirectCaiNetwork
from training.colored_score_20261024.noise import Covariance, sample_covariance
from training.colored_preconditioned_20261024.operators import Spectral
from training.colored_second_20261025.model import (
    ColoredSecondScore, trace_loss, noise_power, variance_from_trace, conditional_error)
from training.scores.direct_objectives import direct_second_loss


def test_white_loss_is_original_cai_trace_loss():
    torch.manual_seed(7)
    b,a,o,c = 4,2,3,2
    h,r,s1,s2 = [torch.randn(b,2,a,o,c,dtype=torch.float64) for _ in range(4)]
    v = torch.tensor([.001,.1,1.,100.],dtype=torch.float64)
    eye = torch.eye(a,dtype=torch.complex128).expand(b,-1,-1)
    spectral = Spectral(eye,eye,(v[:,None,None]/2).expand(-1,a,c))
    mean = r+(v[:,None,None,None,None]/2)*s1
    u = (v/2)*s2.flatten(1).mean(1)
    expected = direct_second_loss(s2,s1,r,h,v[:,None,None,None])
    torch.testing.assert_close(trace_loss(u,mean,h,spectral),expected,rtol=1e-13,atol=1e-13)
    torch.testing.assert_close(variance_from_trace(u,spectral),v*(1+u),rtol=1e-14,atol=1e-14)


def test_colored_noncommuting_gaussian_and_finite_teacher_bias():
    """Exact deterministic conditional second moments; no Monte Carlo tolerance."""
    rng = np.random.default_rng(30)
    d = 8
    a,b = rng.normal(size=(d,d)),rng.normal(size=(d,d))
    prior,sigma = a@a.T+.3*np.eye(d), b@b.T+.7*np.eye(d)
    hessian = -np.linalg.inv(prior+sigma)
    posterior = np.linalg.inv(np.linalg.inv(prior)+np.linalg.inv(sigma))
    np.testing.assert_allclose(posterior,sigma+sigma@hessian@sigma,rtol=2e-14,atol=2e-14)
    assert np.linalg.norm(prior@sigma-sigma@prior) > 1
    u = np.trace(sigma@hessian@sigma)/np.trace(sigma)
    nu = np.trace(sigma)/(d/2)
    np.testing.assert_allclose(nu*(1+u),np.trace(posterior)/(d/2),rtol=2e-14)
    root = np.linalg.cholesky(posterior)
    errors = np.concatenate((np.sqrt(d)*root.T,-np.sqrt(d)*root.T))
    targets = np.sum(errors**2,axis=1)/np.trace(sigma)-1
    np.testing.assert_allclose(targets.mean(),u,rtol=2e-14,atol=2e-14)
    bias = rng.normal(size=d)
    biased = np.sum((errors+bias)**2,axis=1)/np.trace(sigma)-1
    np.testing.assert_allclose(biased.mean(),u+bias@bias/np.trace(sigma),rtol=2e-14,atol=2e-14)


def test_real_complex_scale_and_frozen_target():
    cov = sample_covariance(np.random.default_rng(8),3,2,2,dtype=torch.float64)
    spec = Spectral.from_covariance(cov)
    torch.testing.assert_close(noise_power(spec),cov.variance,rtol=1e-13,atol=1e-13)
    mean = torch.randn(3,2,2,2,2,dtype=torch.float64,requires_grad=True)
    clean = torch.randn_like(mean)
    u = torch.randn(3,dtype=torch.float64,requires_grad=True)
    trace_loss(u,mean,clean,spec).backward()
    assert mean.grad is None and u.grad is not None
    torch.testing.assert_close(conditional_error(mean,clean),
                              (mean.detach()-clean).square().flatten(1).sum(1)/8)
    assert variance_from_trace(torch.full_like(u,-2),spec).lt(0).all()


def test_independent_network_covariance_gradients_and_shape():
    torch.set_num_threads(1)
    torch.manual_seed(9)
    base = DirectCaiNetwork(DirectCaiConfig(base_channels=4,input_transform='identity',snr_db_min=-20),order=2)
    model = ColoredSecondScore(base)
    assert not {p.data_ptr() for p in base.parameters()} & {p.data_ptr() for p in model.parameters()}
    cov = sample_covariance(np.random.default_rng(9),2).to('cpu')
    spec = Spectral.from_covariance(cov)
    x = torch.randn(2,2,16,16,16)
    u = model(x,cov,spec)
    assert u.shape == (2,)
    u.square().sum().backward()
    grad = model.backbone.condition[0].weight.grad[:,1:]
    assert torch.isfinite(grad).all() and grad.norm() > 0


class TinyMean(nn.Module):
    def __init__(self):
        super().__init__()
        self.weight = nn.Parameter(torch.tensor(.3),requires_grad=False)
    def forward(self,x,cov,spec):
        return x*self.weight


class TinySecond(nn.Module):
    config = DirectCaiConfig(input_transform='identity',snr_db_min=-20)
    reference_real_variance = .5
    def __init__(self):
        super().__init__()
        self.weight = nn.Parameter(torch.tensor(.1))
    def forward(self,x,cov,spec):
        return self.weight*torch.log1p(cov.variance)


def test_interrupted_resume_keeps_samples_rng_adam_and_ema(tmp_path,monkeypatch):
    from training.colored_second_20261025 import run
    from utils import sha256
    teacher = tmp_path/'teacher.pt'
    teacher.write_bytes(b'test teacher identity')
    cfg = dict(scale=1.,first_checkpoint=str(teacher),first_checkpoint_sha256=sha256(teacher),
        noise=dict(snr_db=[-20,30],max_strength=.5,rank=4),shape_seed=33,validation_shape_seed=34,
        runtime=dict(device='cpu',cuda_graph=False,maximum_invocation_seconds=1000),scope='test',
        second=dict(seed=31,validation_seed=32,batch_size=4,microbatch_size=2,
            learning_rate=1e-3,minimum_learning_rate=1e-5,ema_decay=.9,gradient_clip=1.,
            checkpoint_seconds=1000,maximum_epochs=2,minimum_epochs=2,validation_patience=10,
            meaningful_relative_improvement=.001,initial_checkpoint_sha256='test'))
    rng = np.random.default_rng(13)
    data = {s:(rng.normal(size=(n,16,16,16))+1j*rng.normal(size=(n,16,16,16))).astype(np.complex64)
            for s,n in (('train',9),('validation',3))}
    monkeypatch.setattr(run,'initialize',lambda cfg,device:(TinyMean().eval(),TinySecond()))
    full,partial = tmp_path/'full',tmp_path/'partial'
    full.mkdir(); partial.mkdir()
    run.Trainer(full,cfg,'same').run(data)
    interrupted = run.Trainer(partial,cfg,'same')
    original = run.BatchGraph.backward
    def pause_after_batch(self,*args,**kwargs):
        value = original(self,*args,**kwargs)
        interrupted.stop = True
        return value
    monkeypatch.setattr(run.BatchGraph,'backward',pause_after_batch)
    interrupted.run(data)
    assert json.loads((partial/'status.json').read_text())['status'] == 'PAUSED'
    monkeypatch.setattr(run.BatchGraph,'backward',original)
    run.Trainer(partial,cfg,'same').run(data)
    x,y = [torch.load(p/'last.pt',weights_only=False) for p in (full,partial)]
    for key in ('epoch','cursor','steps','seen','best','selected_epoch','rng','shape_rng'):
        assert x[key] == y[key]
    for key in ('model','ema'):
        for name in x[key]:
            torch.testing.assert_close(x[key][name],y[key][name],rtol=0,atol=0)
    for key in ('exp_avg','exp_avg_sq','step'):
        torch.testing.assert_close(x['optimizer']['state'][0][key],y['optimizer']['state'][0][key],rtol=0,atol=0)
    assert x['steps'] == 6
    for a,b in zip(x['history'],y['history']):
        assert a['train_loss'] == b['train_loss'] and a['validation'] == b['validation']
