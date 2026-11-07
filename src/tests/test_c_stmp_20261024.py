"""Independent analytic checks of the new interface, not trained performance."""
import numpy as np
import pytest
import torch

from algorithm.C_STMP.moments import trace_variance
from algorithm.C_STMP.configuration import verify
from algorithm.registry import load_catalog,load_models,select,arguments,factory
from algorithm.STMP.denoiser import Denoiser
from algorithm.STMP.moments import MatrixMomentEstimate
from project import ROOT
from utils import read_json,sha256


def test_complex_gaussian_variance_factor_and_full_mean():
    # CN(0,aI) prior, CN(0,vI) noise: exact complex posterior variance av/(a+v).
    a,v = 1.3,2.7
    x = torch.arange(12,dtype=torch.float64).reshape(1,2,6)/7
    probes = torch.tensor([[[[1.,-1.,1.,-1.,1.,-1.],[-1.,1.,1.,-1.,-1.,1.]]]],dtype=x.dtype)
    result = trace_variance(lambda q:a/(a+v)*q,x,lambda z:(v/2)**.5*z,probes,.01)
    assert result.item() == pytest.approx(a*v/(a+v),rel=2e-13)


def test_correlated_real_gaussian_exact_trace_with_basis_probes():
    rng = np.random.default_rng(84)
    a = rng.normal(size=(8,8)); prior = a@a.T+.3*np.eye(8)
    a = rng.normal(size=(8,8)); sigma = a@a.T+.4*np.eye(8)
    gain = prior@np.linalg.inv(prior+sigma)
    posterior = prior-gain@prior
    expected = np.trace(posterior)/4
    g,s = torch.tensor(gain),torch.tensor(np.linalg.cholesky(sigma))
    x = torch.tensor(rng.normal(size=(1,2,4)))
    probes = (8**.5*torch.eye(8,dtype=x.dtype)).reshape(8,1,2,4)
    actual = trace_variance(lambda q:(q.flatten(1)@g.T).reshape_as(q),x,
        lambda z:(z.flatten(1)@s.T).reshape_as(z),probes,1e-3)
    assert actual.item() == pytest.approx(expected,rel=2e-12)


def test_bernoulli_feedback_uses_conditional_covariance_and_one_prior():
    class Moments:
        noise_support=(.001,100.)
        samples=0
        def infer(self,r,v):
            self.samples += len(r)
            return MatrixMomentEstimate(.5*r,np.full(len(r),.2))
    class Evidence:
        noise_support=(.001,100.)
        training_class_prior=.5
        def infer(self,r,v,mean):
            return np.zeros(len(r))
    r=np.full((2,2,2,2),.3+.4j)
    den=Denoiser(Moments(),Evidence(),activity_prior=.1,conditional_variance_floor=1e-4)
    state=den(r,np.eye(2))
    np.testing.assert_allclose(state.activity,.1)
    np.testing.assert_allclose(state.conditional_mean,.5*r)
    np.testing.assert_allclose(state.mean,.05*r)
    m=(.5*r).reshape(2,2,4)
    expected=.1*.2*np.eye(2)[None]+.1*.9*(m@m.conj().swapaxes(-1,-2))/4
    np.testing.assert_allclose(state.spatial_covariance,expected)


def test_names_and_original_assets_preserved():
    catalog=load_catalog()
    assert catalog['DU']['factory']==catalog['proposed']['factory']
    assert catalog['proposed']['alias_of']=='DU'
    assert catalog['C_STMP']['factory']=='algorithm.C_STMP.receiver:Receiver'
    previous=read_json(ROOT/'result/channel_denoising/data/c_stmp_integration_20261024/algorithms_before.json')
    assert catalog['STMP']==previous['algorithms']['STMP']
    for p,digest in read_json(ROOT/'result/channel_denoising/data/c_stmp_integration_20261024/PROTECTED_BEFORE.json').items():
        assert sha256(ROOT/p)==digest,p
    for name,spec in select(['STMP','C_STMP','DU'],catalog,'receiver',phase_mode='known').items():
        import inspect
        inspect.signature(factory(spec)).bind(**arguments(spec,load_models(),'cpu'))


def test_candidate_binding_does_not_claim_classifier_was_retrained():
    path=ROOT/'src/configs/candidates/C_STMP_20261024.json'
    c,hashes=verify(path)
    assert c['first_epoch']==200
    assert c['classifier_training_binding']['first_sha256']!=hashes['first_checkpoint']
    c['classifier_training_binding']['first_sha256']=hashes['first_checkpoint']
    with pytest.raises(ValueError,match='provenance'):
        verify(c)


@pytest.mark.parametrize('raw_tau,accepted,floored',[(-.1,True,True),(1.2,False,False)])
def test_inherited_variance_floor_and_positive_precision_constraint(raw_tau,accepted,floored):
    class Moments:
        noise_support=(.001,100.)
        samples=0
        def infer(self,r,v):
            self.samples += len(r)
            return MatrixMomentEstimate(.3*r,np.full(len(r),raw_tau))
    class Evidence:
        noise_support=(.001,100.)
        training_class_prior=.5
        def infer(self,r,v,mean):
            np.testing.assert_allclose(mean,.3*r)
            return np.zeros(len(r))
    den=Denoiser(Moments(),Evidence(),activity_prior=.1,conditional_variance_floor=1e-4)
    state=den(np.ones((2,2,2,2),complex),np.eye(2))
    assert den.last['site_accepted']==accepted
    assert den.last['conditional_variance_floored']==floored
    assert den.last['classifier_calls']==1
    assert np.isfinite(state.mean).all()


def test_identity_denoiser_returns_complex_noise_variance():
    x=torch.zeros((1,2,7),dtype=torch.float64)
    z=torch.ones((1,1,2,7),dtype=x.dtype)
    v=3.2
    result=trace_variance(lambda q:q,x,lambda w:w*np.sqrt(v/2),z,.01)
    assert result.item()==pytest.approx(v,rel=1e-14)
