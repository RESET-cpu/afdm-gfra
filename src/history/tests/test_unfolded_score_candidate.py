"""Analytic linear references and differentiable closed-loop checks."""
import numpy as np
import torch
from torch import nn
from afdm_jadcedd.algorithm.proposed.activity import EvidenceNetwork,Config
from afdm_jadcedd.algorithm.unfolded_score_candidate import (
    linear_posterior,extrinsic,pack,unpack,UnfoldedReceiver,objective,evidence_forward)


def case():
    torch.manual_seed(31)
    rand=lambda *s:torch.randn(*s,dtype=torch.complex128)
    operator=rand(3,2,4)/3
    mean=rand(2,2,4,4);y=rand(3,2,4)
    return y,operator,mean,torch.tensor(.7),torch.tensor(.3)


def test_arbitrary_operator_lmmse_matches_full_precision_reference():
    y,op,mean,v,n=case();v=v.double();n=n.double()
    post,tau=linear_posterior(y,op,mean,v,n)
    a=op.reshape(3,-1);c=torch.linalg.inv(torch.eye(8,dtype=a.dtype)/v+a.mH@a/n)
    expected=c@(pack(mean)/v+a.mH@y.reshape(3,-1)/n)
    torch.testing.assert_close(pack(post),expected,rtol=2e-13,atol=2e-13)
    torch.testing.assert_close(tau,c.trace().real/8,rtol=2e-13,atol=2e-13)
    r,vc=extrinsic(post,tau,mean,v)
    recombined=(r/vc+mean/v)/(1/vc+1/v)
    torch.testing.assert_close(recombined,post,rtol=2e-13,atol=2e-13)
    torch.testing.assert_close(unpack(pack(mean),mean.shape),mean,rtol=0,atol=0)


def test_row_orthogonal_case_reduces_to_paper_equations_6_7():
    y,op,mean,v,n=case();v=v.double();n=n.double()
    a=torch.linalg.qr(op.reshape(3,8).mH)[0].mH
    post,tau=linear_posterior(y,a.reshape_as(op),mean,v,n)
    expected=pack(mean)+v/(v+n)*a.mH@(y.reshape(3,-1)-a@pack(mean))
    torch.testing.assert_close(pack(post),expected,rtol=2e-13,atol=2e-13)
    torch.testing.assert_close(tau,v-(3/8)*v*v/(v+n),rtol=2e-13,atol=2e-13)


def test_evidence_forward_preserves_values_and_removes_mean_gradient_stop():
    torch.manual_seed(7);net=EvidenceNetwork(Config(antennas=2,side=4,width=4)).double()
    nn.init.normal_(net.readout[-1].weight,std=.02)
    x=torch.randn(3,2,2,4,4,dtype=torch.float64)
    f=torch.randn_like(x,requires_grad=True);v=torch.full((3,),.4,dtype=torch.float64)
    actual=evidence_forward(net,x,v,f)
    torch.testing.assert_close(actual,net(x,v,f),rtol=0,atol=0)
    actual.sum().backward()
    assert f.grad is not None and torch.isfinite(f.grad).all() and f.grad.norm()>0


class SmallScore(nn.Module):
    def __init__(self):
        super().__init__();self.gain=nn.Parameter(torch.tensor(-.6))
    def forward(self,x,v):return self.gain*x/(1+v[:,None,None,None])


def test_three_layer_gradients_reach_first_score_and_activity():
    score=nn.Module();score.network=SmallScore()
    evidence=EvidenceNetwork(Config(antennas=2,side=4,width=4))
    nn.init.normal_(evidence.readout[-1].weight,std=.02)
    model=UnfoldedReceiver()
    for _ in range(3):model.grow(score,evidence,microbatch=1)
    y,a,truth,_,noise=case();prior=torch.tensor(.2,dtype=torch.float64)
    outputs=model(y,a,noise.double(),prior)
    loss,_=objective(outputs,truth,torch.tensor([1.,0.]),prior)
    assert torch.isfinite(loss)
    loss.backward()
    for layer in model.layers:
        for p in (layer.score.network.gain,layer.activity.readout[-1].weight,layer.gamma_raw,layer.alpha_raw):
            assert p.grad is not None and torch.isfinite(p.grad).all() and p.grad.norm()>0
        assert all(torch.isfinite(p.grad).all() for p in layer.parameters() if p.grad is not None)
    for out in outputs:
        diag=out['diagnostics']
        assert 0<diag['posterior_variance']<diag['query_variance']
        assert out['next_variance']>0
