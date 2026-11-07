"""STMP phase-coordinate transport, conditional equivalence and public inputs."""
from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest

from algorithm.STMP import phase, phase_iterations
from algorithm.STMP.iterations import run_spatial_score
from algorithm.STMP.records import SpatialConfig
from algorithm import registry
from evaluation import suite
from evaluation.scenes import DEFAULT
from system.receiver.unknown_phase import UnknownPhaseInput
from utils import read_json


class GaussianDenoiser:
    """Analytic CN(0, I) fixture, independent of the trained networks."""
    def __init__(self):
        self.site_mean = None
        self.message_fresh = True
        self.last = {}

    def __call__(self, query, covariance):
        k, m = query.shape[:2]
        variance = np.trace(covariance).real / m
        mean = query / (1 + variance)
        self.site_mean = np.zeros_like(query)
        self.message_fresh = True
        return SimpleNamespace(mean=mean, conditional_mean=mean,
            activity=np.full(k, .8),
            spatial_covariance=np.broadcast_to(np.eye(m)*variance/(1+variance), (k,m,m)))


def public_input():
    rng = np.random.default_rng(448)
    normal = lambda shape: rng.normal(size=shape)+1j*rng.normal(size=shape)
    return UnknownPhaseInput(normal((4,2,2)), normal((4,3,2)), .3, .4)


def test_no_phase_updates_matches_original_conditional_iterations():
    raw = public_input()
    beta = np.array([.2, -.1, .5])
    config = SpatialConfig(iterations=15, min_iterations=5, damping=.2,
                           convergence_tolerance=.01, covariance_mode='isotropic')
    expected = run_spatial_score(raw.at_estimated_phase(beta), GaussianDenoiser(),
        scale=.27, initial_variance=.4, config=config)
    actual, slopes, steps = phase_iterations.infer(raw, GaussianDenoiser(),
        scale=.27, initial_variance=.4, controls=config, initial_slopes=beta,
        phase_configuration=dict(update_after_iterations=[], minimum_iterations_after_last_update=1))
    for field in ('estimate','conditional_matrix','probabilities','spatial_covariance'):
        np.testing.assert_array_equal(getattr(actual, field), getattr(expected, field))
    assert actual.stopping_reason == expected.stopping_reason
    assert len(actual.trace) == len(expected.trace) and steps == []
    np.testing.assert_array_equal(slopes, beta)


def test_constant_rotation_transports_all_cached_means_and_keeps_variances():
    raw = public_input()
    shape = (3,2,2,2)
    means = np.arange(np.prod(shape)).reshape(shape)+1j
    denoiser = SimpleNamespace(site_mean=means.copy(), site_variance=np.array([1.,2.,3.]),
                              mass=np.array([.1,.2,.3]))
    angle = np.array([.3,-.7,.2])
    rotation = np.exp(1j*angle)[:,None,None,None]
    query, feedback, estimate = phase_iterations.rotate_messages(angle, means, 2*means, 3*means, denoiser)
    for value, factor in ((query,1),(feedback,2),(estimate,3),(denoiser.site_mean,1)):
        np.testing.assert_array_equal(value, factor*means*rotation)
    np.testing.assert_array_equal(denoiser.site_variance, [1.,2.,3.])
    np.testing.assert_array_equal(denoiser.mass, [.1,.2,.3])
    predicted = np.einsum('qkn,kmrn->kqrm',raw.pilot,feedback)
    unrotated = np.einsum('qkn,kmrn->kqrm',raw.pilot,2*means)
    np.testing.assert_allclose(predicted,unrotated*np.exp(1j*angle)[:,None,None,None],rtol=1e-14)


def test_phase_change_rebuilds_operator_and_resets_stopping_windows(monkeypatch):
    raw = public_input()
    real_linear = phase_iterations.SpatialLinear
    operators = []
    def build(operator, *args):
        operators.append(operator.copy())
        return real_linear(operator,*args)
    def change(*args):
        beta = args[-2]
        return beta+.1, np.ones(3)*.2, {'conditional_quadratic':{'users':[]}}
    monkeypatch.setattr(phase_iterations,'SpatialLinear',build)
    monkeypatch.setattr(phase_iterations,'update_phase',change)
    config = SpatialConfig(iterations=20,min_iterations=1,damping=.2,covariance_mode='isotropic',
        convergence_tolerance=100.,convergence_patience=2,decision_stability_window=3)
    result,beta,steps = phase_iterations.infer(raw,GaussianDenoiser(),scale=.27,
        initial_variance=.4,controls=config,initial_slopes=np.zeros(3),
        phase_configuration=dict(update_after_iterations=[5],minimum_iterations_after_last_update=1))
    assert len(operators)==2 and not np.array_equal(operators[0],operators[1])
    np.testing.assert_allclose(operators[1],raw.at_estimated_phase(beta).operator)
    assert len(result.trace)==8 and result.stopping_reason=='CONVERGED'
    assert result.trace[4]['stopping_windows_reset'] and not result.trace[4]['converged']
    assert result.trace[5]['decision_stable_iterations']==1
    assert result.trace[5]['fresh_iterations']==1
    assert len(steps)==1


def test_unknown_phase_ignores_noise_placeholder_and_known_phase_bypasses_fitting(monkeypatch):
    receiver = object.__new__(phase.PhaseSTMPReceiver)
    receiver.device, receiver.noise_mode = 'cpu','estimated'
    seen=[]
    def solve(inputs, observer=None):
        seen.append((type(inputs).__name__,inputs.noise_variance))
        return {'estimate':inputs.observation*inputs.noise_variance},{}
    receiver._unknown_phase = solve
    receiver.base = SimpleNamespace(infer=solve)
    monkeypatch.setattr(phase,'estimate_spatial_noise',lambda y:(.25,{'source':'analytic_fixture'}))
    raw=public_input()
    first,record=receiver.infer(raw)
    second,record=receiver.infer(replace(raw,noise_variance=12345.))
    np.testing.assert_array_equal(first['estimate'],second['estimate'])
    assert not record['truth_used_in_inference'] and not record['phase_truth_used']
    conditional=raw.at_estimated_phase(np.zeros(3))
    receiver.infer(conditional)
    assert seen==[('UnknownPhaseInput',.25),('UnknownPhaseInput',.25),('ReceiverInput',.25)]
    receiver.noise_mode='known'
    _,record=receiver.infer(raw)
    assert seen[-1]==('UnknownPhaseInput',raw.noise_variance)
    assert record['noise_truth_used'] and not record['phase_truth_used']


@pytest.mark.parametrize('schedule,settle', [([5,4],1),([5,5],1),([0],1),([5],0),([5],6)])
def test_invalid_schedule_cannot_return_channel_from_old_phase(schedule,settle):
    with pytest.raises(ValueError,match='final conditional refinement'):
        phase_iterations.infer(public_input(),GaussianDenoiser(),scale=.27,initial_variance=.4,
            controls=SpatialConfig(iterations=10,covariance_mode='isotropic'),initial_slopes=np.zeros(3),
            phase_configuration=dict(update_after_iterations=schedule,minimum_iterations_after_last_update=settle))


@pytest.mark.parametrize('noise_mode',['known','estimated'])
def test_registered_stmp_estimates_raw_phase_without_shared_frontend(tmp_path,monkeypatch,noise_mode):
    raw=public_input()
    truth=dict(phase_slopes=np.array([.1,.2,.3]),channel=np.ones((3,2,2,2)),activity=[True,False,True])
    monkeypatch.setattr(suite,'observation',lambda *a,**k:(raw,truth,dict(generated_noise_variance=.125)))
    monkeypatch.setattr(suite,'estimated_phase',lambda *a,**k:pytest.fail('Shared phase initializer was called'))
    specs=registry.select(['STMP'],registry.load_catalog(),'receiver',noise_mode=noise_mode,phase_mode='estimated')
    plan=dict(base_seed=1,cache=str(tmp_path),input_identity='analytic_fixture',algorithm_specs=specs,
              model_binding=registry.load_models(),phase_mode='estimated',noise_mode=noise_mode)
    inputs,_,receipt,folder=suite.method_case(plan,0,DEFAULT,'STMP')
    assert isinstance(inputs,UnknownPhaseInput)
    np.testing.assert_array_equal(inputs.pilot,raw.pilot)
    assert inputs.noise_variance==(.125 if noise_mode=='known' else 1.)
    assert receipt['phase_seconds']==0 and not read_json(folder/'PHASE.json')['initialized']
    selected=registry.select(['STMP'],registry.load_catalog(),'receiver',noise_mode=noise_mode,phase_mode='known')
    assert selected['STMP']['phase_input']=='operator'
    assert specs['STMP']['factory']=='algorithm.STMP.initialization_runtime_receiver:PhaseSTMPReceiver'
    if noise_mode=='known':
        assert specs['STMP']['kwargs']=={'noise_mode':'known'}
    files=registry.source_files(specs['STMP'],registry.load_models(),'cpu')
    assert any(p.name=='STMP_phase_supported_hypotheses.json' for p in files)


def test_actual_gaussian_phase_update_in_stmp_returns_refined_state():
    result,beta,steps=phase_iterations.infer(public_input(),GaussianDenoiser(),scale=.27,
        initial_variance=.4,controls=SpatialConfig(iterations=8,min_iterations=8,covariance_mode='isotropic'),
        initial_slopes=np.zeros(3),
        phase_configuration=dict(update_after_iterations=[4,6],minimum_iterations_after_last_update=2))
    assert len(steps)==2 and len(result.trace)==8
    assert np.isfinite(result.estimate).all() and np.isfinite(beta).all()
    assert all(s['after']<=s['before']+1e-9 for s in steps)
    assert 'phase_update_index' not in result.trace[-1]
