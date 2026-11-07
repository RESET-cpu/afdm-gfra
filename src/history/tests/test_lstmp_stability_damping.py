"""Analytical acceptance/gradient checks, independent of physical performance."""
import numpy as np
import pytest
import torch
from experiments.lstmp_candidate_20261019.data import pack
from experiments.lstmp_stability_candidate_20261019.receiver import damp_proposal


def fixture():
    torch.manual_seed(202610191)
    old=torch.randn(3,2,2,2,2,dtype=torch.float64)
    a=torch.randn(5,12,dtype=torch.float64)
    y=torch.randn(5,4,dtype=torch.float64)
    return dict(a=a,y=y,noise=.2),old,torch.full((3,),.1,dtype=torch.float64)


def test_quadratic_cost_cannot_increase_and_segment_minimum_is_correct():
    public,old,p=fixture()
    proposal=(20*torch.randn_like(old)).requires_grad_()
    logits=torch.randn(3,dtype=torch.float64,requires_grad=True)
    result,_,info=damp_proposal(public,old,p,proposal,logits,.1)
    assert 0<=info['damping']<=1 and info['quadratic_cost_after']<=info['quadratic_cost_before']+1e-10
    assert info['damping']<1
    cost=lambda x:(public['a']@pack(x)-public['y']).square().sum()+2*x.square().sum()
    for coefficient in np.linspace(0,1,101):
        assert cost(result)<=cost(old+coefficient*(proposal-old))+1e-9


def test_accepted_proposal_and_logits_are_unchanged():
    public,old,p=fixture()
    proposal=torch.zeros_like(old);logits=torch.randn(3,dtype=torch.float64)
    result,got,info=damp_proposal(public,old,p,proposal,logits,.1)
    assert info['damping']==1
    assert torch.equal(result,proposal) and torch.equal(got,logits)


def test_damping_is_invariant_to_real_orthogonal_observation_transform():
    public,old,p=fixture()
    q,_=torch.linalg.qr(torch.randn(5,5,dtype=torch.float64))
    proposal=10*torch.randn_like(old);logits=torch.zeros(3,dtype=torch.float64)
    a,_,x=damp_proposal(public,old,p,proposal,logits,.1)
    transformed=dict(public,a=q@public['a'],y=q@public['y'])
    b,_,y=damp_proposal(transformed,old,p,proposal,logits,.1)
    torch.testing.assert_close(a,b,rtol=1e-12,atol=1e-12)
    assert x['damping']==pytest.approx(y['damping'],abs=1e-12)


def test_interpolated_probability_and_gradients():
    public,old,p=fixture()
    # Overshoot toward zero creates a strict interior minimizer.
    proposal=(-10*old).requires_grad_();logits=torch.ones(3,dtype=torch.float64,requires_grad=True)
    result,got,info=damp_proposal(public,old,p,proposal,logits,.1)
    assert 0<info['damping']<1
    expected=p+info['damping']*(torch.sigmoid(logits)-p)
    torch.testing.assert_close(torch.sigmoid(got),expected)
    assert torch.autograd.gradcheck(lambda x,z:damp_proposal(public,old,p,x,z,.1)[:2],(proposal,logits),eps=1e-6,atol=1e-5)
