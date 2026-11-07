"""The phase frontend hands only its estimated operator to the unchanged receiver."""
from dataclasses import dataclass
import numpy as np
import pytest
from algorithm.C_STMP_phase_frontend_marginal_20261104 import receiver as module
from system.observation import ReceiverInput
from system.receiver.unknown_phase import UnknownPhaseInput
from system.phase import phase_operator


@dataclass
class DummyControls:
    iterations: int = 600


def test_raw_route_keeps_initial_phase_and_only_passes_operator(monkeypatch):
    y=np.ones((3,2,2),complex)
    pilot=np.arange(12).reshape(3,2,2).astype(complex)+1
    slopes=np.array([.12,-.4]); calls=[]; init_calls=[]
    monkeypatch.setattr(module,'estimate_spatial_noise',lambda _: (.7,{'source':'observation'}))
    def initialize(raw,controls,observer=None):
        assert raw.noise_variance==.7
        init_calls.append(raw)
        return dict(phase_slopes=slopes, gains='not forwarded', powers='not forwarded'),dict(seconds=1.,truth_used_in_inference=False)
    def conditional(self,value,observer=None):
        calls.append(value)
        self.last_trace=[dict(iteration=1,converged=True)]
        return dict(noise_variance_estimate=np.asarray(.7)),dict(seconds=2.)
    monkeypatch.setattr(module.initialization,'estimate',initialize)
    monkeypatch.setattr(module.ConditionalReceiver,'infer',conditional)
    model=module.Receiver.__new__(module.Receiver)
    model.phase_controls=DummyControls();model.controls=DummyControls();model.frontend_binding={}
    for placeholder in (1.,999.):
        arrays,record=model.infer(UnknownPhaseInput(y,pilot,placeholder,.1))
        np.testing.assert_array_equal(arrays['phase'],arrays['initial_phase'])
        np.testing.assert_array_equal(arrays['phase_slopes'],slopes)
        assert record['phase_updates_inside_receiver']==0 and record['phase_trials']==[]
        assert not record['receiver_truth_used'] and not record['initializer_gain_or_power_forwarded']
    assert len(calls)==len(init_calls)==2
    for value in calls:
        assert isinstance(value,ReceiverInput)
        np.testing.assert_array_equal(value.operator,phase_operator(pilot,slopes))
        np.testing.assert_array_equal(value.observation,y)
        assert value.activity_prior==.1


def test_known_control_delegates_without_phase_fitting(monkeypatch):
    value=ReceiverInput(np.ones((3,2,2)),np.ones((3,2,2)),1.,.1)
    output={'estimate':np.ones((2,2,2,2))}
    def conditional(self,inputs,observer=None):
        assert inputs is value
        return output,{'seconds':1.}
    def forbidden(*args,**kwargs):raise AssertionError('No phase fitting on known control')
    monkeypatch.setattr(module.ConditionalReceiver,'infer',conditional)
    monkeypatch.setattr(module.initialization,'estimate',forbidden)
    model=module.Receiver.__new__(module.Receiver)
    arrays,record=model.infer(value)
    assert arrays is output and record['oracle_phase_supplied'] and record['receiver_truth_used']


def test_untyped_input_rejected():
    model=module.Receiver.__new__(module.Receiver)
    with pytest.raises(TypeError,match='Raw observation'):
        model.infer({'observation':np.ones(2),'true_phase':np.ones(2)})
