"""Public-input boundary and unchanged conditional route, without model loading."""
import numpy as np
import pytest

from algorithm.C_STMP_phase_frontend_20261027 import receiver as module
from system.observation import ReceiverInput
from system.receiver.unknown_phase import UnknownPhaseInput
from system.phase import phase_operator


def test_estimated_route_ignores_noise_placeholder_and_builds_phase_operator(monkeypatch):
    y = np.ones((3, 2, 2), complex)
    pilot = np.arange(12).reshape(3, 2, 2).astype(complex) + 1
    slopes = np.array([.12, -.4])
    calls = []
    monkeypatch.setattr(module, 'estimate_spatial_noise', lambda _: (.7, {'source': 'observation'}))

    def phase(raw, controls, observer=None):
        assert raw.noise_variance == .7
        np.testing.assert_array_equal(raw.pilot, pilot)
        np.testing.assert_array_equal(raw.observation, y)
        return {'phase_slopes': slopes}, {'seconds': 1., 'truth_used_in_inference': False}

    def conditional(self, value, observer=None):
        calls.append(value)
        return {'noise_variance_estimate': np.asarray(.7)}, {'seconds': 2.}

    monkeypatch.setattr(module.phase_estimation, 'estimate', phase)
    monkeypatch.setattr(module.ConditionalReceiver, 'infer', conditional)
    model = module.Receiver.__new__(module.Receiver)
    model.phase_controls = module.phase_estimation.Controls()
    for placeholder in (1., 999.):
        arrays, record = model.infer(UnknownPhaseInput(y, pilot, placeholder, .1))
        assert not record['receiver_truth_used']
        assert record['input_noise_placeholder_ignored']
        assert record['phase_updates_inside_receiver'] == 0
        np.testing.assert_array_equal(arrays['phase_slopes'], slopes)
    for value in calls:
        np.testing.assert_array_equal(value.operator, phase_operator(pilot, slopes))
        np.testing.assert_array_equal(value.observation, y)
        assert value.activity_prior == .1


def test_known_phase_control_bypasses_frontend(monkeypatch):
    value = ReceiverInput(np.ones((3, 2, 2)), np.ones((3, 2, 2)), 1., .1)
    output = {'estimate': np.ones((2, 2, 2, 2))}

    def conditional(self, inputs, observer=None):
        assert inputs is value
        return output, {'seconds': 1.}

    def forbidden(*args, **kwargs):
        raise AssertionError('Known-phase route must not estimate phases')

    monkeypatch.setattr(module.ConditionalReceiver, 'infer', conditional)
    monkeypatch.setattr(module.phase_estimation, 'estimate', forbidden)
    model = module.Receiver.__new__(module.Receiver)
    arrays, record = model.infer(value)
    assert arrays is output
    assert record['oracle_phase_supplied'] and record['receiver_truth_used']


def test_rejects_untyped_input():
    model = module.Receiver.__new__(module.Receiver)
    with pytest.raises(TypeError, match='Raw observation'):
        model.infer({'observation': np.ones(2), 'true_phase': np.ones(2)})
