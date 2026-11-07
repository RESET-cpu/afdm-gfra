"""Current output/moment validity differs from convergence of damped messages."""
from types import SimpleNamespace
import numpy as np
from algorithm.STMP import phase_output_stable_iterations as kernel
from algorithm.STMP.records import SpatialConfig
from system.receiver.unknown_phase import UnknownPhaseInput


def test_phase_waits_for_current_moments_without_requiring_message_residual_convergence(monkeypatch):
    rng=np.random.default_rng(498)
    normal=lambda s:rng.normal(size=s)+1j*rng.normal(size=s)
    inputs=UnknownPhaseInput(normal((4,2,2)),normal((4,3,2)),.3,.4)
    class Conditional:
        calls=0
        message_fresh=False
        last={}
        def __call__(self,r,v):
            self.calls+=1
            self.last=dict(site_accepted=self.calls>=9,unsupported_users=0)
            variance=np.trace(v).real/2;mean=r/(1+variance)
            return SimpleNamespace(mean=mean,conditional_mean=mean,activity=np.full(3,.8),
                spatial_covariance=np.tile(np.eye(2)*variance/(1+variance),(3,1,1)))
    def update(*args):
        return args[-2]+.001,np.zeros(3),dict(conditional_quadratic={'users':[]},before=1.,after=.9)
    monkeypatch.setattr(kernel,'update_phase',update)
    controls=SpatialConfig(iterations=16,min_iterations=16,damping=.2,covariance_mode='isotropic',
        convergence_tolerance=100.,activity_convergence_tolerance=100.,convergence_patience=2,decision_stability_window=3)
    phase=dict(state_update='feedback_and_new_query',phase_update_requires_stable_current_output=True,
        periodic_update=dict(start=4,interval=4),minimum_iterations_after_last_update=1,
        stopping=dict(allow_original_stopping=True,comparison='completed_phase_update_cycles',
            require_raw_site_residual=False,consecutive_cycles=100,relative_tolerance=.005,
            activity_tolerance=.001,require_stable_decisions=3))
    result,_,steps=kernel.infer(inputs,Conditional(),scale=.27,initial_variance=.4,
        controls=controls,phase_configuration=phase,initial_slopes=np.zeros(3))
    assert [s['after_iteration'] for s in steps]==[12]
    assert not result.trace[7]['phase_update_eligible']
    assert result.trace[11]['phase_update_eligible'] and result.trace[11]['fresh_iterations']==0
    assert result.stopping_reason=='MAX_ITERATIONS' and not result.trace[-1]['legacy_converged']
