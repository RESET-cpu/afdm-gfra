"""Working-distribution moments, common-slope objective and state continuity."""
from dataclasses import replace
from types import SimpleNamespace
import numpy as np
import pytest
from algorithm.C_STMP_phase_slope_moments_20261104 import phase, iterations
from algorithm.C_STMP_phase_shen_frames_20261103.moments import conditional_quadratic
from algorithm.proposed.phase_math import quadratic_objective
from algorithm.STMP.records import SpatialConfig
from test_phase_shen_frames_20261103 import _case
from test_phase_conditional_schedule_20261104 import ConstantDenoiser, Linear
from test_phase_direct_integration_20261103 import _input


def _state(case):
    _,_,h,_,_,_ = case
    k,m = h.shape[:2]
    p = np.linspace(.15,.9,k)
    c = np.broadcast_to(np.eye(m)*.27,(k,m,m)).copy()
    return SimpleNamespace(mean=p[:,None,None,None]*h,conditional_mean=h,activity=p,
        conditional_spatial_covariance=c)


def test_denoiser_quadratic_equals_dense_shared_activity_BG_expectation():
    case = _case(seed=17);y,pilot,*_ = case;state = _state(case)
    g,b,z,_ = phase.denoiser_quadratic(y,pilot,state)
    q,k,n = pilot.shape;m,r = y.shape[1:]
    expected = np.empty_like(g)
    for frame in range(q):
        projected = []
        uncertainty = []
        for user in range(k):
            a = np.kron(np.eye(m*r),pilot[frame,user][None])
            h = state.conditional_mean[user].ravel();rho = state.activity[user]
            cov = rho*np.kron(state.conditional_spatial_covariance[user],np.eye(r*n))
            cov = cov.astype(complex)+rho*(1-rho)*np.outer(h,h.conj())
            projected.append(a@state.mean[user].ravel())
            uncertainty.append(np.trace(a@cov@a.conj().T).real)
        projected = np.asarray(projected)
        expected[frame] = projected.conj()@projected.T+np.diag(uncertainty)
        np.testing.assert_allclose(b[frame],projected.conj()@y[frame].ravel(),rtol=1e-12,atol=1e-12)
    np.testing.assert_allclose(g,expected,rtol=1e-12,atol=1e-12)
    # Without shared-activity cross-coefficient covariance, this would disagree.
    phi = case[-1]
    residual_mean = y.reshape(q,-1)-np.sum(phi[:,:,None]*z,axis=1)
    diag_uncertainty = np.trace(g-np.einsum('qkd,qld->qkl',z.conj(),z),axis1=1,axis2=2).real.sum()
    np.testing.assert_allclose(np.vdot(y,y).real+quadratic_objective(phi,g,b),
        np.linalg.norm(residual_mean)**2+diag_uncertainty,rtol=1e-12)


def test_gaussian_quadratic_reuses_exact_existing_conditional_moments():
    case = _case(seed=73)
    g,b,_,_ = phase.gaussian_quadratic(*case)
    old_g,old_b,_ = conditional_quadratic(*case)
    np.testing.assert_array_equal(g,old_g)
    np.testing.assert_array_equal(b,old_b)


@pytest.mark.parametrize('seed',[3,19,73])
def test_common_slope_coordinate_minimum_and_constant_diagonal_invariance(seed):
    case = _case(seed=seed,k=1);y,pilot,*_ = case
    g,b,_,_ = phase.denoiser_quadratic(y,pilot,_state(case))
    old=np.array([.4]);beta,phi,report = phase.rotations(old,g,b)
    grid=np.linspace(-np.pi,np.pi,10001)
    points=np.exp(1j*np.arange(len(pilot))[:,None]*grid[None])
    scores=np.sum(g[:,0,0].real)-2*np.real(b[:,0].conj()@points)
    assert report['conditional_after']<=min(scores)+1e-9
    np.testing.assert_allclose(phi,np.exp(1j*np.arange(len(pilot))[:,None]*beta),atol=1e-14)
    added=g+17*np.eye(1)[None]
    shifted,_,_=phase.rotations(old,added,b)
    np.testing.assert_allclose(np.exp(1j*beta),np.exp(1j*shifted),atol=1e-11)
    assert max(report['coordinate_objective_changes'])<=0


@pytest.mark.parametrize('source',['gaussian','denoiser'])
def test_selected_working_objective_decreases_and_units_are_invariant(source):
    case=_case(seed=13);y,pilot,mean,v,noise,_=case;state=_state(case);old=np.array([.2,-.4,.8])
    beta,phi,report=phase.update(y,pilot,mean,v,noise,old,state,moment_source=source)
    assert not report['conditional_objective_materially_increased']
    if source=='gaussian':assert not report['marginal_objective_materially_increased']
    a=2.7
    scaled=SimpleNamespace(mean=state.mean*a,conditional_mean=state.conditional_mean*a,
        activity=state.activity,conditional_spatial_covariance=state.conditional_spatial_covariance*a*a)
    scaled_beta,scaled_phi,scaled_report=phase.update(y*a,pilot,mean*a,v*a*a,noise*a*a,old,scaled,moment_source=source)
    np.testing.assert_allclose(phi,scaled_phi,atol=2e-10)
    np.testing.assert_allclose(report['phase_effect']['relative_signal_change'],
        scaled_report['phase_effect']['relative_signal_change'],rtol=2e-10)


def test_inactive_user_remains_unobservable_and_probability_is_not_squared():
    case=_case(seed=73);state=_state(case);state.activity[0]=0;state.mean[0]=0
    g,b,_,_=phase.denoiser_quadratic(case[0],case[1],state)
    assert np.count_nonzero(g[:,0])==0 and np.count_nonzero(b[:,0])==0
    old=np.array([.8,-.2,.3]);beta,_,_=phase.rotations(old,g,b)
    assert beta[0]==old[0]
    bad=SimpleNamespace(**vars(state));bad.mean=state.mean*state.activity[:,None,None,None]
    with pytest.raises(ValueError,match='exactly once'):phase.denoiser_quadratic(case[0],case[1],bad)


def _run(monkeypatch,effects,count=6):
    monkeypatch.setattr(iterations,'SpatialLinear',Linear)
    calls=[];queries=[]
    def update(y,p,mean,v,noise,beta,state,*,moment_source):
        effect=effects[min(len(calls),len(effects)-1)];new=beta+.02
        calls.append((beta.copy(),new.copy(),state.mean.copy()))
        return new,np.exp(1j*np.arange(len(p))[:,None]*new),dict(seconds=0.,phase_effect=dict(relative_signal_change=effect))
    monkeypatch.setattr(iterations,'update_phase',update)
    cfg=SpatialConfig(iterations=count,min_iterations=2,damping=.4,convergence_tolerance=1e3,
        convergence_patience=1,decision_stability_window=1,activity_convergence_tolerance=.01,covariance_mode='isotropic')
    result=iterations.infer(_input(),ConstantDenoiser(),scale=.7,initial_variance=.4,controls=cfg,
        phase_configuration=dict(relative_signal_change_tolerance=.01,moment_source='denoiser'),
        initial_slopes=np.array([.1,-.2,.3]),observer=lambda row,state,r,*unused:queries.append(r.copy()))
    return result,calls,queries


def test_iteration_uses_current_posterior_and_keeps_messages_continuous(monkeypatch):
    (result,used,steps,trials),calls,queries=_run(monkeypatch,[.2,.001])
    assert result.stopping_reason=='CONVERGED' and len(steps)==1
    np.testing.assert_allclose(calls[0][2],.15+.1j)
    np.testing.assert_array_equal(calls[1][0],calls[0][1])
    np.testing.assert_allclose(used,np.exp(1j*np.arange(len(used))[:,None]*calls[1][0]))
    assert not trials[-1]['applied']
    assert result.trace[2]['query_variance_ratio']==result.trace[1]['next_query_variance_ratio']
    new_raw=np.full_like(queries[1],.5+.2j)*( _input().pilot*used[:,:,None]).mean()
    np.testing.assert_allclose(queries[2],.6*queries[1]+.4*new_raw,rtol=1e-14,atol=1e-14)


def test_iteration_does_not_apply_phase_without_following_message_budget(monkeypatch):
    (result,used,steps,trials),calls,_=_run(monkeypatch,[.2],count=4)
    assert result.stopping_reason=='MAX_ITERATIONS' and not trials[-1]['applied']
    np.testing.assert_allclose(used,np.exp(1j*np.arange(len(used))[:,None]*calls[-1][0]))
