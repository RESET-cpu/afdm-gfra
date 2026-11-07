"""Independent phase/noise modes and unknown-phase-only minimum iterations."""
from dataclasses import replace
from types import SimpleNamespace
import numpy as np
import pytest
from receiver.stmp import phase, phase_refresh
from receiver.stmp.records import SpatialConfig
from channel.unknown_phase import UnknownPhaseInput


def test_phase_specific_minimum_does_not_change_known_phase_controls(monkeypatch):
    def setup(self, configuration, **kwargs):
        self.base=SimpleNamespace(controls=SpatialConfig(iterations=600,min_iterations=150))
        self.phase_configuration=dict(state_update='feedback_and_new_query',minimum_conditional_iterations=80)
    monkeypatch.setattr(phase.PhaseSTMPReceiver,'__init__',setup)
    receiver=phase_refresh.PhaseSTMPReceiver({},phase_configuration='unused')
    assert receiver.base.controls.min_iterations==150 and receiver.unknown_controls.min_iterations==80
    assert replace(receiver.unknown_controls,min_iterations=150)==receiver.base.controls


@pytest.mark.parametrize('known_phase',[False,True])
@pytest.mark.parametrize('known_noise',[False,True])
def test_four_phase_noise_modes_are_independent(monkeypatch,known_phase,known_noise):
    receiver=object.__new__(phase_refresh.PhaseSTMPReceiver)
    receiver.device='cpu';receiver.noise_mode='known' if known_noise else 'estimated'
    calls=[]
    def conditional(inputs,observer=None):
        calls.append(('conditional',inputs.noise_variance))
        return dict(estimate=inputs.observation*inputs.noise_variance),{}
    def unknown(inputs,observer=None):
        calls.append(('unknown',inputs.noise_variance))
        return dict(estimate=inputs.observation*inputs.noise_variance),{}
    receiver.base=SimpleNamespace(infer=conditional);receiver._unknown_phase=unknown
    def estimate(y):
        if known_noise:pytest.fail('Known-noise path must not estimate noise')
        return .25,dict(source='fixture')
    monkeypatch.setattr(phase,'estimate_spatial_noise',estimate)
    raw=UnknownPhaseInput(np.ones((4,2,2)),np.ones((4,3,2)),.75,.1)
    inputs=raw.at_estimated_phase(np.zeros(3)) if known_phase else raw
    arrays,record=receiver.infer(inputs)
    assert calls==[('conditional' if known_phase else 'unknown',.75 if known_noise else .25)]
    assert record['phase_truth_used']==known_phase and record['noise_truth_used']==known_noise
    if known_phase:assert record['phase_updates']==0
