import numpy as np
import pytest
import torch
from structure import linearize_rank_one


def test_projection_and_complete_complex_direction():
    rng=np.random.default_rng(813)
    h=rng.normal(size=(3,4,3,5))+1j*rng.normal(size=(3,4,3,5))
    delta=rng.normal(size=(2,*h.shape))+1j*rng.normal(size=(2,*h.shape))
    value,jvp=linearize_rank_one(h)
    def reference(t):
        a=t.reshape(3,4,-1);u,s,vh=torch.linalg.svd(a,full_matrices=False)
        return (u[:,:,:1]*s[:,:1,None].transpose(1,2))@vh[:,:1,:]
    reference_value=reference(torch.tensor(h)).numpy().reshape(h.shape)
    np.testing.assert_allclose(value,reference_value,rtol=1e-12,atol=1e-12)
    for i in range(2):
        _,direction=torch.autograd.functional.jvp(reference,torch.tensor(h),torch.tensor(delta[i]))
        np.testing.assert_allclose(jvp(delta)[i],direction.numpy().reshape(h.shape),rtol=2e-11,atol=2e-11)
    # Central differences independently verify real and imaginary directions.
    eps=1e-5
    for d in [delta[0],1j*delta[0]]:
        finite=(linearize_rank_one(h+eps*d)[0]-linearize_rank_one(h-eps*d)[0])/(2*eps)
        np.testing.assert_allclose(jvp(d[None])[0],finite,rtol=2e-7,atol=2e-8)


def test_zero_and_nondifferentiable_tie():
    h=np.zeros((2,4,3,5),complex);v,j=linearize_rank_one(h)
    assert np.count_nonzero(v)==0 and np.count_nonzero(j(np.ones((1,*h.shape))))==0
    h=np.eye(4,dtype=complex).reshape(1,4,2,2)
    with pytest.raises(FloatingPointError):linearize_rank_one(h)


def test_full_composition_including_conjugate_path():
    from structure import StructuredDenoiser
    class Base:
        scale=1.
        def linearize(self,x,covariance):
            # Explicit non-holomorphic map tests both real-direction paths.
            return x+.1*x.conj()**2, lambda d:d+.2*x.conj()[None]*d.conj()
    rng=np.random.default_rng(814)
    h=rng.normal(size=(2,3,2,4))+1j*rng.normal(size=(2,3,2,4))
    d=rng.normal(size=h.shape)+1j*rng.normal(size=h.shape)
    result,derivative=StructuredDenoiser(Base()).linearize(h,None)
    def reference(t):
        x=t+.1*t.conj()**2;a=x.reshape(2,3,-1)
        e,u=torch.linalg.eigh(a@a.mH);v=u[:,:,-1:]
        return (v@(v.mH@a)).reshape(t.shape)
    y,dy=torch.autograd.functional.jvp(reference,torch.tensor(h),torch.tensor(d))
    np.testing.assert_allclose(result,y.numpy(),rtol=1e-12,atol=1e-12)
    np.testing.assert_allclose(derivative(d[None])[0],dy.numpy(),rtol=1e-11,atol=1e-11)
