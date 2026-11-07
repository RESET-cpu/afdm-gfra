"""Conditional-prefix equivalence and phase-change state consistency."""
from copy import deepcopy
from types import SimpleNamespace
import numpy as np
import pytest
from project import ROOT
from utils import read_json
from algorithm.C_STMP_phase_iterative_20261028 import iterations as kernel, receiver
from algorithm.C_STMP_variance_em_20261025.iterations import run_spatial_score
from algorithm.STMP.records import SpatialConfig
from algorithm.STMP.linear import SpatialLinear
from system.phase import phase_operator
from system.receiver.unknown_phase import UnknownPhaseInput


class Gaussian:
    def __init__(self, accepted=True):
        self.accepted = accepted
        self.model = SimpleNamespace(samples=0)
        self.evidence = None
        self.message_fresh = True
        self.last = {}

    def __call__(self, r, v):
        power = np.trace(v).real/r.shape[1]
        mean = r/(1+power)
        self.last = dict(site_accepted=self.accepted, unsupported_users=0)
        self.message_fresh = True
        return SimpleNamespace(mean=mean, conditional_mean=mean,
            activity=np.full(len(r), .8), spatial_covariance=np.tile(
                np.eye(r.shape[1])*power/(1+power), (len(r), 1, 1)))


def fixture():
    rng = np.random.default_rng(2810)
    normal = lambda shape: (rng.normal(size=shape)+1j*rng.normal(size=shape))/np.sqrt(2)
    raw = UnknownPhaseInput(normal((4,2,2)), normal((4,3,2)), .3, .4)
    p = deepcopy(read_json(ROOT/'src/configs/final/STMP_phase_supported_hypotheses.json'))
    p['periodic_update'] = dict(start=4, interval=4)
    p['minimum_iterations_after_last_update'] = 1
    return raw, p


def test_before_phase_update_matches_current_c_stmp_including_query_variance():
    raw, p = fixture()
    controls = SpatialConfig(iterations=8, min_iterations=8, damping=.4, covariance_mode='isotropic')
    kwargs = dict(scale=.27, initial_variance=.4)
    old = run_spatial_score(raw.at_estimated_phase(np.zeros(3)), Gaussian(False), config=controls, **kwargs)
    new, slopes, steps, checks = kernel.infer(raw, Gaussian(False), controls=controls,
        phase_configuration=p, initial_slopes=np.zeros(3), training_moment=np.eye(4), reference_power=1., **kwargs)
    assert not steps and not checks
    np.testing.assert_array_equal(new.estimate, old.estimate)
    np.testing.assert_array_equal(new.spatial_covariance, old.spatial_covariance)
    for a,b in zip(new.trace, old.trace):
        for key in ('query_variance_ratio','next_query_variance_ratio','input_variance_trace',
                    'em_variance_target','em_relative_residual','residual_power'):
            assert a[key] == b[key]


def test_phase_change_refreshes_query_covariance_and_calibration(monkeypatch):
    raw, p = fixture()
    controls = SpatialConfig(iterations=8, min_iterations=8, damping=.4, covariance_mode='isotropic',
        convergence_tolerance=100., activity_convergence_tolerance=100.,
        convergence_patience=1, decision_stability_window=1)
    monkeypatch.setattr(kernel, 'proposals', lambda *a, **k: dict(users=[], neural_query_count=0))
    rotation = np.array([.3,-.2,.5])
    monkeypatch.setattr(kernel, 'update_phase', lambda *a: (a[-2]+.04, rotation,
        dict(conditional_quadratic={'users':[]}, before=1., after=.9)))
    observed = []
    def observe(row,state,r,v,prior,prior_cov,out,out_v,posterior):
        observed.append((r.copy(),v.copy(),out.copy(),out_v.copy()))
    result,beta,steps,_ = kernel.infer(raw,Gaussian(),scale=.27,initial_variance=.4,controls=controls,
        phase_configuration=p,initial_slopes=np.zeros(3),training_moment=np.eye(4),reference_power=1.,observer=observe)
    assert [s['after_iteration'] for s in steps] == [4]
    _,_,feedback,feedback_v = observed[3]
    feedback *= np.exp(1j*rotation)[:,None,None,None]
    linear = SpatialLinear(phase_operator(raw.pilot,np.full(3,.04)),2,.3/.27**2)
    _,_,expected_r,expected_v = linear.update(raw.observation/.27,feedback,feedback_v)
    np.testing.assert_array_equal(observed[4][0],expected_r)
    np.testing.assert_array_equal(observed[4][1],expected_v)
    assert result.trace[4]['query_variance_ratio'] == 1.
    assert steps[0]['raw_variance_history_reset']
    assert steps[0]['rotated_cached_means'] == ['feedback']
    assert len(result.trace) == 8


def test_known_phase_bypasses_all_iterative_phase_code(monkeypatch):
    raw,_ = fixture()
    value = raw.at_estimated_phase(np.zeros(3))
    output = ({'estimate':np.ones(2)}, {'phase_mode':'known'})
    def unchanged(self, inputs, observer=None):
        assert inputs is value
        return output
    monkeypatch.setattr(receiver.FrontendReceiver,'infer',unchanged)
    model = receiver.Receiver.__new__(receiver.Receiver)
    assert model.infer(value) is output


def test_unknown_noise_placeholder_is_replaced_before_initialization_and_iteration(monkeypatch):
    raw,p = fixture()
    calls=[]
    monkeypatch.setattr(receiver,'estimate_spatial_noise',lambda y:(.7, {'source':'test_observation'}))
    def initialize(inputs, controls, observer=None):
        calls.append(inputs.noise_variance)
        return {'phase_slopes':np.zeros(3)}, {'truth_used_in_inference':False}
    monkeypatch.setattr(receiver.phase_estimation,'estimate',initialize)
    monkeypatch.setattr(receiver,'Denoiser',lambda *a,**k:object())
    def iterate(inputs, denoiser, **kwargs):
        calls.append(inputs.noise_variance)
        result=SimpleNamespace(estimate=np.ones((3,2,2,2)),conditional_matrix=np.ones((3,2,2,2)),
            probabilities=np.full(3,.8),spatial_covariance=np.tile(np.eye(2),(3,1,1)),
            trace=(),stopping_reason='MAX_ITERATIONS')
        return result,np.zeros(3),[],[]
    monkeypatch.setattr(receiver,'iterate',iterate)
    model=receiver.Receiver.__new__(receiver.Receiver)
    model.configuration=dict(scale=.27,conditional_variance_floor_checkpoint_normalized=.0001,
        initialization={'normalized_training_second_moment':1.},decision_threshold=.5)
    model.model=SimpleNamespace(reset=lambda:None,network_samples=0)
    model.evidence=None; model.controls=model.unknown_controls=SpatialConfig()
    model.phase_controls=receiver.phase_estimation.Controls()
    model.phase_configuration=p; model.training_moment=np.eye(4); model.device='cpu'
    model.context=lambda:{}
    arrays,record=model.infer(raw)
    assert calls == [.7,.7]
    assert not record['receiver_truth_used'] and record['input_noise_placeholder_ignored']
    assert arrays['noise_variance_estimate'] == .7


def test_reject_untyped_input():
    with pytest.raises(TypeError,match='Raw observation'):
        receiver.Receiver.__new__(receiver.Receiver).infer({'true_phase':[0.]})
