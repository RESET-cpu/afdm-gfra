"""Independent algebra checks for CUDA execution of the phase likelihood."""
import numpy as np
import pytest
import torch
from receiver.frontend import phase_initialization as reference
from receiver.stmp import gpu_initialization as candidate
from receiver.stmp.initialization_cuda import CudaInitialization


def problem():
    rng=np.random.default_rng(2026102309)
    blocks=rng.normal(size=(3,6,4))+1j*rng.normal(size=(3,6,4))
    gram=np.einsum('kin,kjn->kij',blocks,blocks.conj())/4
    y=rng.normal(size=(6,5))+1j*rng.normal(size=(6,5))
    return gram,y,.6,np.repeat(np.arange(3),2),.1


@pytest.mark.skipif(not torch.cuda.is_available(),reason='CUDA required for the candidate kernel')
def test_cuda_covariance_value_inverse_and_weight_match_dense_reference():
    gram,y,noise,frames,rho=problem();sample=y@y.conj().T/y.shape[1]
    ctx=CudaInitialization(gram,y,noise,frames,rho,'cuda')
    for covariance in [noise*np.eye(6)+gram[0]*.2,noise*np.eye(6)+gram[2]*.7]:
        a=reference.factor_value(covariance,sample);b=ctx.factor(covariance)
        for expected,actual in zip(a,b):np.testing.assert_allclose(actual,expected,rtol=2e-12,atol=2e-12)
        value,inverse,weight=ctx.factor(covariance,False)
        np.testing.assert_allclose(value,a[0],rtol=2e-12,atol=2e-12)
        np.testing.assert_allclose(inverse,a[1],rtol=2e-12,atol=2e-12)
        assert weight is None


@pytest.mark.skipif(not torch.cuda.is_available(),reason='CUDA required for the candidate kernel')
def test_cuda_joint_and_local_gradients_match_finite_differences_and_changed_inputs():
    gram,y,noise,frames,rho=problem();sample=y@y.conj().T/y.shape[1];span=float(frames.max())
    ctx=CudaInitialization(gram,y,noise,frames,rho,'cuda')
    for x in [np.zeros(6),np.array([.2,.5,1.,-.4,.3,1.1]),np.array([2.,.1,.6,1.4,-2.,.2])]:
        expected=reference.objective(x,gram,sample,noise,frames,rho,span);value,gradient=ctx.joint(x)
        np.testing.assert_allclose(value,expected[0],rtol=2e-12,atol=2e-12)
        np.testing.assert_allclose(gradient,expected[1],rtol=2e-11,atol=2e-11)
        numerical=[]
        for i in range(len(x)):
            delta=np.zeros_like(x);delta[i]=1e-6
            numerical.append((reference.objective(x+delta,gram,sample,noise,frames,rho,span)[0]-
                              reference.objective(x-delta,gram,sample,noise,frames,rho,span)[0])/2e-6)
        np.testing.assert_allclose(gradient,numerical,rtol=2e-5,atol=2e-8)
    for i in [0,2,1]:
        base=noise*np.eye(6)+gram[(i+1)%3]*.3;x=np.array([.7,.9])
        expected=reference.local_objective(x,gram[i],base,sample,frames,rho,span)
        actual=ctx.local(x,gram[i],base)
        for a,b in zip(actual,expected):np.testing.assert_allclose(a,b,rtol=2e-11,atol=2e-11)


def test_cpu_initializer_fallback_is_exactly_the_previous_path():
    rng=np.random.default_rng(552)
    pilot=rng.normal(size=(3,2,2))+1j*rng.normal(size=(3,2,2))
    y=rng.normal(size=(3,3,2))+1j*rng.normal(size=(3,3,2))
    moment=np.eye(4)
    a,ra=reference.estimate(y,pilot,.5,moment,.1)
    b,rb=candidate.estimate(y,pilot,.5,moment,.1,device='cpu')
    for key in a:np.testing.assert_array_equal(a[key],b[key])
    np.testing.assert_array_equal(ra['optimization']['objective'],rb['optimization']['objective'])
    np.testing.assert_array_equal(ra['initializer']['objective'],rb['initializer']['objective'])
