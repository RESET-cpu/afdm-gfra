"""Phase updates require the same existing message/estimate/decision windows."""
from types import SimpleNamespace
import numpy as np
from algorithm.STMP import phase_settled_iterations
from algorithm.STMP.records import SpatialConfig
from system.receiver.unknown_phase import UnknownPhaseInput


def test_due_phase_update_waits_for_existing_conditional_stability(monkeypatch):
    rng=np.random.default_rng(806)
    normal=lambda shape:rng.normal(size=shape)+1j*rng.normal(size=shape)
    inputs=UnknownPhaseInput(normal((4,2,2)),normal((4,3,2)),.3,.4)
    class Conditional:
        last={}
        message_fresh=False
        calls=0
        def __call__(self,r,v):
            self.calls+=1;self.message_fresh=self.calls>=13
            variance=np.trace(v).real/2;mean=r/(1+variance)
            return SimpleNamespace(mean=mean,conditional_mean=mean,activity=np.full(3,.8),
                spatial_covariance=np.tile(np.eye(2)*variance/(1+variance),(3,1,1)))
    def update(*args):
        return args[-2]+.001,np.zeros(3),dict(conditional_quadratic={'users':[]},before=1.,after=.9)
    monkeypatch.setattr(phase_settled_iterations,'update_phase',update)
    controls=SpatialConfig(iterations=20,min_iterations=20,damping=.2,covariance_mode='isotropic',
        convergence_tolerance=100.,activity_convergence_tolerance=100.,convergence_patience=2,
        decision_stability_window=3)
    phase=dict(state_update='feedback_and_new_query',phase_update_requires_conditional_stability=True,
        phase_stopping_requires_conditional_and_cycle=True,
        periodic_update=dict(start=4,interval=4),minimum_iterations_after_last_update=1,
        stopping=dict(allow_original_stopping=False,comparison='completed_phase_update_cycles',
            require_raw_site_residual=False,consecutive_cycles=2,relative_tolerance=100.,
            activity_tolerance=100.,require_stable_decisions=3))
    result,beta,steps=phase_settled_iterations.infer(inputs,Conditional(),scale=.27,
        initial_variance=.4,controls=controls,phase_configuration=phase,initial_slopes=np.zeros(3))
    assert [s['after_iteration'] for s in steps]==[16]
    for t in (4,8,12):
        row=result.trace[t-1]
        assert row['phase_update_due'] and not row['phase_update_eligible']
        assert row['phase_update_skipped']=='conditional_windows_not_stable'
    assert result.trace[15]['phase_update_eligible'] and result.trace[15]['stopping_windows_reset']
    assert len(result.trace)==20 and result.stopping_reason=='CONVERGED'
    phase['stopping']['consecutive_cycles']=100
    capped,_,_=phase_settled_iterations.infer(inputs,Conditional(),scale=.27,
        initial_variance=.4,controls=controls,phase_configuration=phase,initial_slopes=np.zeros(3))
    assert capped.trace[-1]['legacy_converged'] and not capped.trace[-1]['converged']
    assert capped.trace[-1]['stopping_trigger'] is None and capped.stopping_reason=='MAX_ITERATIONS'
