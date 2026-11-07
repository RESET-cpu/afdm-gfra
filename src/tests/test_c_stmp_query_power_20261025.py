"""Verify shared noise conditioning and inference independence from truth."""
import numpy as np
from algorithm.C_STMP_query_power.iterations import run_spatial_score
from algorithm.STMP.denoiser import Denoiser
from algorithm.STMP.moments import MatrixMomentEstimate
from algorithm.STMP.records import SpatialConfig
from system.observation import ReceiverInput


def test_calibrated_variance_is_shared_by_mean_classifier_and_feedback():
    class Moments:
        noise_support=(1e-8,1e8)
        samples=0
        calls=[]
        def infer(self,r,v):
            self.samples+=len(r)
            self.calls.append((r.copy(),v.copy()))
            return MatrixMomentEstimate(.3*r,.2*v)
    class Evidence:
        noise_support=Moments.noise_support
        training_class_prior=.5
        calls=[]
        def infer(self,r,v,mean):
            self.calls.append((r.copy(),v.copy(),mean.copy()))
            return np.zeros(len(r))
    rng=np.random.default_rng(251025)
    a=(rng.normal(size=(3,4,2))+1j*rng.normal(size=(3,4,2)))/np.sqrt(2)
    y=rng.normal(size=(3,2,2))+1j*rng.normal(size=(3,2,2))
    moments,evidence=Moments(),Evidence()
    den=Denoiser(moments,evidence,activity_prior=.1,conditional_variance_floor=1e-8)
    rows=[]
    def observe(row,state,r,v,prior,prior_cov,out,out_v,posterior):
        expected=np.median(np.mean(abs(r)**2,axis=(1,2,3)))
        np.testing.assert_allclose(v,expected*np.eye(2))
        np.testing.assert_allclose(moments.calls[-1][1],expected)
        np.testing.assert_array_equal(evidence.calls[-1][1],moments.calls[-1][1])
        np.testing.assert_allclose(evidence.calls[-1][2],.3*r)
        np.testing.assert_allclose(state.conditional_mean,.3*r,rtol=1e-12,atol=1e-12)
        assert row['observable_query_variance']==expected
        assert np.isfinite(out).all() and np.isfinite(out_v).all()
        rows.append(row)
    cfg=SpatialConfig(iterations=3,min_iterations=3,covariance_mode='isotropic',damping=.4)
    result=run_spatial_score(ReceiverInput(y,a,.7,.1),den,scale=1.,initial_variance=.1,config=cfg,observer=observe)
    assert len(rows)==3
    assert np.isfinite(result.estimate).all()


def test_final_readout_keeps_original_iteration_and_common_condition(monkeypatch):
    from algorithm.C_STMP_query_power.readout import Receiver
    from algorithm.C_STMP_retrained.receiver import Receiver as Original
    class Moments:
        noise_support=(1e-8,1e8)
        network_samples=0
        first_calls=0
        def infer(self,r,v):
            self.seen=(r.copy(),v.copy())
            self.network_samples+=3*len(r);self.first_calls+=3
            return MatrixMomentEstimate(.5*r,.2*v)
    class Evidence:
        training_class_prior=.5
        def infer(self,r,v,mean):
            np.testing.assert_array_equal(v,receiver.model.seen[1])
            np.testing.assert_allclose(mean,.5*r)
            return np.zeros(len(r))
    receiver=object.__new__(Receiver)
    receiver.model=Moments();receiver.evidence=Evidence()
    receiver.configuration={'scale':2.,'conditional_variance_floor_checkpoint_normalized':1e-4,'decision_threshold':.5}
    query=np.ones((4,2,2,2),complex)*(.3+.4j)
    def original(self,inputs,*,observer):
        for i in range(3):observer({'iteration':i+1},None,query,np.eye(2))
        return {'probabilities':np.ones(4)*.2},dict(iterations=3,trace=[1,2,3],seconds=1.,
            first_network_samples=36,first_score_calls=9,first_score_samples=12,first_mean_samples=12,
            classifier_calls=3,classifier_samples=12,activity_evidence_calls=3,activity_evidence_samples=12)
    monkeypatch.setattr(Original,'infer',original)
    seen=[]
    arrays,record=receiver.infer(ReceiverInput(np.ones((2,2,2)),np.ones((2,4,2)),.1,.1),observer=lambda row,*args:seen.append(row['iteration']))
    assert seen==[1,2,3] and record['iterations']==3 and record['trace']==[1,2,3]
    assert record['first_network_samples']==48
    np.testing.assert_allclose(receiver.model.seen[1],.25)
    np.testing.assert_allclose(arrays['probabilities'],.1)
    np.testing.assert_allclose(arrays['estimate'],.1*query)
    gram=(.5*query).reshape(4,2,4)
    expected=(.1*.05*np.eye(2)+.1*.9*(gram@gram.conj().swapaxes(-1,-2))/4)*4
    np.testing.assert_allclose(arrays['spatial_covariance'],expected)
    assert record['final_readout']['feedback'] is False
