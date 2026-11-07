"""Algebra and receiver-boundary checks for the separate calibration candidate."""
import numpy as np
import pytest
import torch
from types import SimpleNamespace
from afdm_jadcedd.algorithm.proposed.moments import MatrixMomentEstimate
from afdm_jadcedd.algorithm.proposed_calibration_candidate import (
    Calibration, CalibratedMoments, CalibratedEvidence,
    covariance_from_query, feature_values)


def test_complex_directional_derivatives_and_trace_normalization():
    # Analytic proper complex Gaussian active prior, with nonzero mean and
    # correlated noise. Every real coordinate is probed, eliminating MC error.
    c=np.array([[1.2,.2+.1j],[.2-.1j,.8]])
    s=np.array([[.6,.1-.05j],[.1+.05j,.9]])
    m=np.array([.3+.2j,-.1+.4j]);r=np.array([.6-.4j,.5+.1j])
    inv=np.linalg.inv(c);joint=np.linalg.inv(c+s)
    mu=m+s@joint@(r-m);posterior=s-s@joint@s
    ell=lambda x: float(np.vdot(x,inv@x).real-np.vdot(x-m,joint@(x-m)).real)
    v=np.trace(c).real/2;dim=4;delta=.002;curvatures=[]
    for k in range(dim):
        z=np.zeros(2,complex);z[k%2]=np.sqrt(dim)*(1 if k<2 else 1j)
        direction=c@z/np.sqrt(2*v)
        first=(ell(r+delta*direction)-ell(r-delta*direction))/(2*delta*np.sqrt(dim))
        expected=np.vdot(z,mu).real/np.sqrt(v*2)
        np.testing.assert_allclose(first,expected,atol=2e-11,rtol=1e-10)
        curvatures.append((ell(r+delta*direction)-2*ell(r)+ell(r-delta*direction))/(delta**2*dim))
    np.testing.assert_allclose(np.mean(curvatures),np.trace(posterior).real/(2*v),rtol=1e-9,atol=1e-10)


def test_covariance_features_respect_spatial_unitary_basis():
    rng=np.random.default_rng(89)
    r=rng.normal(size=(6,3,4,4))+1j*rng.normal(size=(6,3,4,4))
    f=.3*r+.2;v=np.full(6,2.);tau=np.full(6,.4);ell=np.arange(6.)
    u=np.linalg.qr(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))[0]
    rotate=lambda a:np.einsum('mn,knrc->kmrc',u,a)
    c=covariance_from_query(r,2.)
    np.testing.assert_allclose(np.trace(c).real,6.,atol=1e-13)
    assert np.linalg.eigvalsh(c).min()>0
    cr=covariance_from_query(rotate(r),2.)
    np.testing.assert_allclose(cr,u@c@u.conj().T,atol=1e-13)
    np.testing.assert_allclose(feature_values(r,v,f,tau,ell,c),
                               feature_values(rotate(r),v,rotate(f),tau,ell,cr),rtol=1e-6,atol=1e-6)


def test_zero_head_and_same_query_evidence_contract():
    rng=np.random.default_rng(17)
    query=rng.normal(size=(4,3,4,4))+1j*rng.normal(size=(4,3,4,4))
    v=np.ones(4);f=.4*query;tau=np.linspace(.1,.4,4);ell=np.linspace(-2,3,4)
    calls=[]
    def frozen_evidence(r,variance,mean):
        np.testing.assert_array_equal(mean,f)
        calls.append(1)
        return ell
    original=SimpleNamespace(infer=lambda r,v:MatrixMomentEstimate(f,tau),noise_support=(.001,100.))
    evidence=SimpleNamespace(infer=frozen_evidence,noise_support=(.001,100.),training_class_prior=.5)
    adapter=CalibratedMoments(original,evidence,Calibration('correlation'))
    paired=CalibratedEvidence(adapter)
    actual=adapter.infer(query,v)
    np.testing.assert_allclose(actual.mean,f,rtol=1e-14,atol=1e-14)
    np.testing.assert_allclose(actual.variance,tau,rtol=2e-7,atol=1e-8)
    with pytest.raises(AssertionError):paired.infer(query+.01,v,actual.mean)
    np.testing.assert_allclose(paired.infer(query,v,actual.mean),ell,atol=2e-7,rtol=2e-7)
    assert len(calls)==1 and adapter.cache is None
    with pytest.raises(AssertionError):paired.infer(query,v,actual.mean)


def test_scalar_cannot_see_correlation_features_and_gradients_are_finite():
    torch.manual_seed(6);model=Calibration('scalar')
    torch.nn.init.normal_(model.layers[-1].weight,std=.03)
    x=torch.randn(12,13);changed=x.clone();changed[:,7:]+=10
    ratio=torch.linspace(.01,.99,12);ell=torch.linspace(-20,20,12)
    a=model(x,ratio,ell);b=model(changed,ratio,ell)
    for left,right in zip(a,b):torch.testing.assert_close(left,right,rtol=0,atol=0)
    sum(t.square().mean() for t in a).backward()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
    assert torch.all((a[0]>.25)&(a[0]<4)) and torch.all((a[1]>0)&(a[1]<1))
