"""Phase stopping must check the current proposal and preserve matched outputs."""
from copy import deepcopy
from types import SimpleNamespace
import numpy as np
import pytest
from project import ROOT
from utils import read_json
from algorithm.C_STMP_phase_selection_20261030 import iterations as kernel, receiver
from algorithm.C_STMP_phase_selection_20261030.stopping import trial_changes
from algorithm.C_STMP_variance_em_20261025.iterations import run_spatial_score
from algorithm.STMP.linear import SpatialLinear
from algorithm.STMP.records import SpatialConfig
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
        return SimpleNamespace(mean=mean, conditional_mean=mean, activity=np.full(len(r), .8),
            spatial_covariance=np.tile(np.eye(r.shape[1])*power/(1+power), (len(r),1,1)))


def fixture():
    rng = np.random.default_rng(3010)
    normal = lambda shape: (rng.normal(size=shape)+1j*rng.normal(size=shape))/np.sqrt(2)
    raw = UnknownPhaseInput(normal((4,2,2)), normal((4,3,2)), .3, .4)
    p = deepcopy(read_json(ROOT/'src/configs/candidates/c_stmp_phase_selection_20261030/physical_40_20.json')['phase'])
    p['periodic_update'] = dict(start=4, interval=4)
    p['minimum_iterations_after_last_update'] = 1
    p['stopping'].update(require_stable_decisions=1, consecutive_cycles=1)
    return raw, p


def controls(n=8):
    return SpatialConfig(iterations=n, min_iterations=n, damping=.4, covariance_mode='isotropic',
        convergence_tolerance=100., activity_convergence_tolerance=100.,
        convergence_patience=1, decision_stability_window=1)


def test_exact_conditional_prefix_without_valid_phase_moments():
    raw, p = fixture()
    c = controls()
    old = run_spatial_score(raw.at_estimated_phase(np.zeros(3)),Gaussian(False),config=c,scale=.27,initial_variance=.4)
    new,beta,steps,trials = kernel.infer(raw,Gaussian(False),scale=.27,initial_variance=.4,controls=c,
        phase_configuration=p,initial_slopes=np.zeros(3))
    assert not steps and not trials
    np.testing.assert_array_equal(new.estimate,old.estimate)
    np.testing.assert_array_equal(new.spatial_covariance,old.spatial_covariance)
    for a,b in zip(new.trace,old.trace):
        for key in ('query_variance_ratio','next_query_variance_ratio','input_variance_trace',
                    'em_variance_target','em_relative_residual','residual_power'):
            assert a[key] == b[key]


def test_trial_metric_catches_channel_rotation_cancelled_in_observed_frame():
    # Only the last frame has mean energy: theta cancels the slope there.
    projected = np.zeros((1,4,1),complex); projected[0,-1] = 2.
    feedback = np.ones((1,1,1,1),complex)
    effect = trial_changes(projected,feedback,np.arange(4),np.zeros(1),np.array([.1]),np.array([-.3]),
        gram=np.ones((1,4,4)),variance=.1,noise=1.)
    assert effect['prediction_change'] < 1e-15
    assert effect['channel_rotation_change'] > .29
    assert effect['slope_prediction_change'] > .29


def test_zero_means_still_check_phase_dependent_uncertainty():
    effect = trial_changes(np.zeros((1,4,1)),np.zeros((1,1,1,1)),np.arange(4),np.zeros(1),np.array([.5]),np.zeros(1),
        gram=np.ones((1,4,4)),variance=1.,noise=.1)
    assert effect['zero_mean_contribution']
    assert effect['prediction_change'] == effect['channel_rotation_change'] == 0
    assert effect['observation_covariance_change'] > .1


def test_metric_is_invariant_to_wrapping_and_zero_power_user():
    args=(np.ones((2,4,1)),np.ones((2,1,1,1)),np.arange(4),np.zeros(2),2*np.pi*np.ones(2),np.zeros(2))
    effect=trial_changes(*args,gram=np.tile(np.eye(4),(2,1,1)),variance=1.,noise=1.)
    assert max(effect[k] for k in ('prediction_change','channel_rotation_change','observation_covariance_change')) < 1e-14


def fake_update(*args):
    beta = args[-2]
    return beta+.04,np.array([.3,-.2,.5]),dict(before=1.,after=.9,conditional_quadratic={})


def test_changed_operator_uses_fresh_query_and_resets_calibration(monkeypatch):
    raw,p=fixture(); observed=[]
    monkeypatch.setattr(kernel,'update_phase',fake_update)
    def observe(row,state,r,v,prior,prior_cov,out,out_v,posterior):
        observed.append((r.copy(),v.copy(),out.copy(),out_v.copy()))
    result,beta,steps,trials=kernel.infer(raw,Gaussian(),scale=.27,initial_variance=.4,controls=controls(),
        phase_configuration=p,initial_slopes=np.zeros(3),observer=observe)
    assert [s['after_iteration'] for s in steps] == [4]
    feedback=observed[3][2]*np.exp(1j*np.array([.3,-.2,.5]))[:,None,None,None]
    linear=SpatialLinear(phase_operator(raw.pilot,np.full(3,.04)),2,.3/.27**2)
    _,_,r,v=linear.update(raw.observation/.27,feedback,observed[3][3])
    np.testing.assert_array_equal(observed[4][0],r)
    np.testing.assert_array_equal(observed[4][1],v)
    assert result.trace[4]['query_variance_ratio'] == 1.
    np.testing.assert_array_equal(beta,np.full(3,.04))
    assert trials[-1]['after_iteration'] == 8 and not trials[-1]['applied']
    assert result.stopping_reason == 'MAX_ITERATIONS'


def test_old_cycle_pass_cannot_hide_large_current_trial(monkeypatch):
    raw,p=fixture()
    class Passing:
        current_moment_iterations=100
        def __init__(self,*a,**k): pass
        def observe_decisions(self,*a,**k): self.current_moment_iterations=100
        def check(self,*a,**k): return dict(stop=True,passed=True)
    monkeypatch.setattr(kernel,'OutputCycleStopping',Passing)
    monkeypatch.setattr(kernel,'update_phase',fake_update)
    result,beta,steps,trials=kernel.infer(raw,Gaussian(),scale=.27,initial_variance=.4,controls=controls(),
        phase_configuration=p,initial_slopes=np.zeros(3))
    assert result.stopping_reason == 'MAX_ITERATIONS'
    assert all(not t['trial_passed'] for t in trials)


def test_slope_rule_does_not_require_message_rotation_to_vanish(monkeypatch):
    raw,p=fixture()
    class Passing:
        current_moment_iterations=100
        def __init__(self,*a,**k): pass
        def observe_decisions(self,*a,**k): self.current_moment_iterations=100
        def check(self,*a,**k): return dict(stop=True,passed=True)
    monkeypatch.setattr(kernel,'OutputCycleStopping',Passing)
    monkeypatch.setattr(kernel,'update_phase',lambda *a:(a[-2].copy(),np.full(3,.3),
        dict(before=1.,after=.9,conditional_quadratic={})))
    result,beta,steps,trials=kernel.infer(raw,Gaussian(),scale=.27,initial_variance=.4,controls=controls(),
        phase_configuration=p,initial_slopes=np.zeros(3))
    assert result.stopping_reason=='CONVERGED'
    assert trials[-1]['effect']['channel_rotation_change'] > .29
    assert trials[-1]['effect']['slope_prediction_change']==0
    np.testing.assert_array_equal(beta,np.zeros(3))


def test_two_joint_cycles_restart_after_large_trial(monkeypatch):
    raw,p=fixture();p['stopping']['consecutive_cycles']=2
    class Passing:
        current_moment_iterations=100
        def __init__(self,*a,**k): pass
        def observe_decisions(self,*a,**k): self.current_moment_iterations=100
        def check(self,*a,**k): return dict(stop=True,passed=True)
    monkeypatch.setattr(kernel,'OutputCycleStopping',Passing)
    count=[]
    def update(*a):
        count.append(1); delta=.1 if len(count)==2 else 0.
        return a[-2]+delta,np.zeros(3),dict(before=1.,after=.9,conditional_quadratic={})
    monkeypatch.setattr(kernel,'update_phase',update)
    from dataclasses import replace
    c=replace(controls(16),min_iterations=4)
    result,beta,steps,trials=kernel.infer(raw,Gaussian(),scale=.27,initial_variance=.4,controls=c,
        phase_configuration=p,initial_slopes=np.zeros(3))
    assert [t['consecutive_small_trials'] for t in trials]==[1,0,1,2]
    assert len(result.trace)==16 and result.stopping_reason=='CONVERGED'


def test_stop_returns_existing_phase_not_unapplied_trial(monkeypatch):
    raw,p=fixture()
    class Passing:
        current_moment_iterations=100
        def __init__(self,*a,**k): pass
        def observe_decisions(self,*a,**k): self.current_moment_iterations=100
        def check(self,*a,**k): return dict(stop=True,passed=True)
    monkeypatch.setattr(kernel,'OutputCycleStopping',Passing)
    def small(*args):
        return args[-2]+1e-5,np.zeros(3),dict(before=1.,after=.99,conditional_quadratic={})
    monkeypatch.setattr(kernel,'update_phase',small)
    result,beta,steps,trials=kernel.infer(raw,Gaussian(),scale=.27,initial_variance=.4,controls=controls(),
        phase_configuration=p,initial_slopes=np.zeros(3))
    assert result.stopping_reason == 'CONVERGED'
    assert len(steps)==1 and len(trials)==2 and not trials[-1]['applied']
    np.testing.assert_array_equal(beta,np.full(3,1e-5))


def test_zero_initialization_ignores_noise_placeholder_and_never_calls_frontend(monkeypatch):
    raw,p=fixture(); p['initializer']='zero'; calls=[]
    monkeypatch.setattr(receiver,'estimate_spatial_noise',lambda y:(.7,{}))
    monkeypatch.setattr(receiver.phase_estimation,'estimate',lambda *a,**k:pytest.fail('Physical initializer was called'))
    monkeypatch.setattr(receiver,'Denoiser',lambda *a,**k:object())
    def iterate(inputs, denoiser, **kwargs):
        calls.append(inputs.noise_variance)
        np.testing.assert_array_equal(kwargs['initial_slopes'],np.zeros(3))
        return SimpleNamespace(estimate=np.ones((3,2,2,2)),conditional_matrix=np.ones((3,2,2,2)),
            probabilities=np.full(3,.8),spatial_covariance=np.tile(np.eye(2),(3,1,1)),trace=(),
            stopping_reason='MAX_ITERATIONS'),np.zeros(3),[],[]
    monkeypatch.setattr(receiver,'iterate',iterate)
    model=receiver.Receiver.__new__(receiver.Receiver)
    model.phase_configuration=p;model.candidate_name='test';model.device='cpu'
    model.configuration=dict(scale=.27,conditional_variance_floor_checkpoint_normalized=.0001,
        initialization={'normalized_training_second_moment':1.},decision_threshold=.5)
    model.model=SimpleNamespace(reset=lambda:None,network_samples=0)
    model.controls=model.unknown_controls=controls();model.evidence=None
    model.phase_controls=receiver.phase_estimation.Controls();model.context=lambda:{}
    arrays,record=model.infer(raw)
    assert calls==[.7] and not record['receiver_truth_used']
    assert arrays['noise_variance_estimate']==.7
