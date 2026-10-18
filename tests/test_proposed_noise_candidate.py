"""Prove that supplied noise information is discarded by the candidate."""
import numpy as np
from afdm_jadcedd.algorithm import proposed_noise_candidate as candidate
from afdm_jadcedd.system.observation import ReceiverInput


def test_supplied_variance_cannot_affect_conditional_receiver(monkeypatch):
    calls = []
    class SpyReceiver:
        def __init__(self, configuration, *, device):
            self.configuration = configuration
            self.device = device
        def infer(self, inputs, *, observer=None):
            calls.append(inputs)
            return {'used_variance': np.asarray(inputs.noise_variance)}, {'seconds': 0.}
    monkeypatch.setattr(candidate, 'Receiver', SpyReceiver)
    rng = np.random.default_rng(20261017031)
    y = rng.normal(size=(16, 16, 16))+1j*rng.normal(size=(16, 16, 16))
    operator = rng.normal(size=(16, 2, 16))+1j*rng.normal(size=(16, 2, 16))
    inputs = ReceiverInput(y, operator, 1e-8, .1)
    other = ReceiverInput(y, operator, 1e8, .1)
    receiver = candidate.EstimatedNoiseProposedReceiver({}, device='cpu')
    a, record_a = receiver.infer(inputs)
    b, record_b = receiver.infer(other)
    np.testing.assert_array_equal(a['used_variance'], b['used_variance'])
    assert calls[0].noise_variance == calls[1].noise_variance > 0
    assert inputs.noise_variance == 1e-8 and other.noise_variance == 1e8
    np.testing.assert_array_equal(calls[0].observation, y)
    np.testing.assert_array_equal(calls[0].operator, operator)
    assert not record_a['supplied_noise_variance_used']
    assert not record_b['supplied_noise_variance_used']
