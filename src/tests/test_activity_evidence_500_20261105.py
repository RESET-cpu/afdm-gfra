"""Independent density identity and receiver public-input boundary checks."""
import numpy as np
from scipy.special import expit,logit
from algorithm.STMP.posterior import full_posterior

def test_nonzero_gaussian_site_matches_normalized_complex_densities():
    rng=np.random.default_rng(50)
    r=rng.normal(size=(4,2,2,3))+1j*rng.normal(size=(4,2,2,3))
    e=.3*(rng.normal(size=r.shape)+1j*rng.normal(size=r.shape))
    c=np.array([.15,.4,1.,2.]);v=.8;rho=.17;d=12
    result=full_posterior(r,v,e,c,rho)
    log_active=np.array([-d*np.log(np.pi*(x+v))-np.vdot(y-z,y-z).real/(x+v) for x,y,z in zip(c,r,e)])
    log_inactive=np.array([-d*np.log(np.pi*v)-np.vdot(y,y).real/v for y in r])
    np.testing.assert_allclose(result.activity,expit(logit(rho)+log_active-log_inactive),rtol=2e-13)
    np.testing.assert_allclose(result.log_evidence_bound,log_active-log_inactive,rtol=2e-13,atol=2e-13)

def test_stmp_adapter_ignores_supplied_noise_and_passes_only_public_input(monkeypatch):
    from evaluation.activity_evidence_500_20261105 import receivers as r
    from system.observation import ReceiverInput
    captured=[]
    def infer(self,inputs,observer=None):
        captured.append(inputs)
        return {},dict(classifier_calls=0)
    monkeypatch.setattr(r.GaussianSTMP,'infer',infer)
    monkeypatch.setattr(r,'estimate_spatial_noise',lambda y:(.75,dict(source='synthetic test')))
    receiver=r.OriginalSTMP.__new__(r.OriginalSTMP);receiver.device='cpu'
    y=np.ones((2,2,2),complex);a=np.ones((2,4,2),complex)
    for noise in (.001,999.):
        _,record=receiver.infer(ReceiverInput(y,a,noise,.1))
        assert not record['noise_truth_used'] and not record['receiver_truth_used']
    assert all(i.noise_variance==.75 for i in captured)
    assert all(i.observation is y and i.operator is a for i in captured)
    assert set(captured[0].__dataclass_fields__)=={'observation','operator','noise_variance','activity_prior'}

def test_historical_compact_activity_is_rescored_and_channel_statistics_verified(tmp_path):
    from evaluation.activity_evidence_500_20261105.common import reuse_metrics
    from evaluation.metrics import score_arrays
    from evaluation.storage import save_arrays
    import pytest
    active=np.arange(40)%4==0
    channel=np.zeros((40,16,16,16),complex);channel[active]=.1
    decision=active.copy();decision[0]=False;decision[1]=True
    estimate=.8*channel
    truth=dict(channel=channel,activity=active)
    metrics=score_arrays(dict(estimate=estimate,activity_decision=decision),truth)
    path=tmp_path/'compact.npz'
    compact=dict(probabilities=decision.astype(float),activity_decision=decision,
        per_user_error=np.asarray(metrics['per_user_error']),truth_activity=active)
    save_arrays(path,compact)
    measured=reuse_metrics(dict(prediction=None,compact=str(path)),truth,metrics)
    assert measured['misses']==1 and measured['false_alarms']==1
    compact['per_user_error'][0]+=1
    save_arrays(path,compact)
    with pytest.raises(AssertionError):
        reuse_metrics(dict(prediction=None,compact=str(path)),truth,metrics)
