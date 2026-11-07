"""Independent formula checks for the train/inference implementation."""
import numpy as np
from numpy.testing import assert_allclose
import torch
from training.column_messages_20261025.interface import training_query,information_query,column
from algorithm.C_STMP_column_20261025.receiver import proper_orthogonal_probes,projected_feedback


def draw(seed=91):
    rng=np.random.default_rng(seed)
    g=rng.normal(size=(2,16,16))+1j*rng.normal(size=(2,16,16))
    u,_=np.linalg.qr(g)
    lam=np.exp(rng.uniform(-4,4,(2,16)))
    h=torch.tensor(rng.normal(size=(2,2,16,16,16)),dtype=torch.float64)
    e=torch.tensor(rng.normal(size=h.shape),dtype=torch.float64)
    return rng,h,e,torch.tensor(u),torch.tensor(lam)


def test_training_query_is_same_likelihood_as_receiver_information():
    _,h,e,u,lam=draw()
    x,z=training_query(h,e,u,lam)
    eta=column(h,u,lam)+column(e,u,(lam/2).sqrt())
    a,b=information_query(eta,u,lam)
    torch.testing.assert_close(a,x,atol=2e-12,rtol=2e-12)
    torch.testing.assert_close(b,z,atol=2e-12,rtol=2e-12)


def test_stable_loss_equals_original_covariance_weighted_dsm():
    rng,h,e,u,lam=draw()
    _,z=training_query(h,e,u,lam)
    raw=torch.tensor(rng.normal(size=h.shape),dtype=torch.float64)
    j=lam/(1+lam)
    mean=z+column(raw,u,(.5/(1+lam)).sqrt())
    direct=column(mean-h,u,(2*lam).sqrt())
    stable=column(raw,u,j.sqrt())-column(h,u,(2*j*(1-j)).sqrt())+column(e,u,j)
    torch.testing.assert_close(stable,direct,atol=2e-12,rtol=2e-12)


def test_matrix_derivative_and_feedback_recover_gaussian_prior_without_clipping():
    rng=np.random.default_rng(912)
    g=rng.normal(size=(2,16,16))+1j*rng.normal(size=(2,16,16))
    u,_=np.linalg.qr(g)
    lam=np.exp(rng.uniform(-10,2,(2,16)))
    precision=(u*lam[:,None,:])@u.conj().transpose(0,2,1)
    g=rng.normal(size=(2,16,16))+1j*rng.normal(size=(2,16,16))
    prior_cov=g@g.conj().transpose(0,2,1)/16+.2*np.eye(16)
    prior_precision=np.linalg.inv(prior_cov)
    posterior=np.linalg.inv(prior_precision+precision)
    eta=rng.normal(size=(2,16,256))+1j*rng.normal(size=(2,16,256))
    mu=posterior@eta
    xi=proper_orthogonal_probes(rng,2,1)[0]
    direction=u@(np.sqrt(lam)[:,:,None]*xi)
    derivative=posterior@direction
    modal=u.conj().transpose(0,2,1)@derivative
    fraction=(np.sqrt(lam)[:,:,None]*modal)@xi.conj().transpose(0,2,1)/256
    expected=(u.conj().transpose(0,2,1)@posterior@u)*np.sqrt(lam)[:,:,None]*np.sqrt(lam)[:,None,:]
    assert_allclose(fraction,expected,atol=3e-14,rtol=3e-11)
    out,b,raw,used=projected_feedback(mu,fraction,lam,u,eta,1e-12,1-1e-12)
    assert_allclose(raw,used,atol=0,rtol=0)
    assert_allclose(out,prior_precision,atol=2e-11,rtol=2e-10)
    assert_allclose(b,0,atol=5e-11)
