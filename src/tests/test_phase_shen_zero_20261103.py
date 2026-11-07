"""Check the all-one starting operator and absence of any physical initializer.

The integration check uses a synthetic Gaussian denoiser and a small raw input;
it is not a trained-network performance experiment.
"""
from copy import deepcopy
from dataclasses import replace

import numpy as np
import pytest

from project import ROOT
from utils import read_json, sha256
from algorithm.C_STMP_phase_shen_frames_20261103 import receiver as frame_receiver
from algorithm.C_STMP_phase_shen_zero_20261103.receiver import Receiver
from test_phase_shen_frames_20261103 import _NonzeroGaussian, _integration_settings
from test_phase_direct_integration_20261103 import _input


CONFIG = ROOT/'src/configs/candidates/c_stmp_phase_shen_zero_20261103/shen_frames_zero.json'
PHYSICAL = ROOT/'src/configs/candidates/c_stmp_phase_shen_frames_20261103/shen_frames_physical.json'


def test_configuration_changes_only_phase_initialization():
    zero_binding, physical_binding = read_json(CONFIG), read_json(PHYSICAL)
    assert zero_binding['phase_update'] == physical_binding['phase_update']
    assert sha256(ROOT/zero_binding['selected_configuration']) == zero_binding['selected_configuration_sha256']
    zero = read_json(ROOT/zero_binding['selected_configuration'])
    physical = read_json(ROOT/physical_binding['selected_configuration'])
    assert zero['phase']['initializer'] == 'zero'
    assert physical['phase']['initializer'] == 'physical'
    zero = deepcopy(zero)
    zero['name'], zero['selection_status'] = physical['name'], physical['selection_status']
    zero['phase']['initializer'] = 'physical'
    assert zero == physical


def test_raw_receiver_starts_at_one_without_search(monkeypatch):
    def forbidden_search(*args, **kwargs):
        raise AssertionError('Physical initialization must never be called')

    monkeypatch.setattr(frame_receiver.phase_estimation, 'estimate', forbidden_search)
    receiver = Receiver(CONFIG, device='cpu')
    raw = _input()
    _, controls = _integration_settings()
    receiver.unknown_controls = replace(controls, iterations=40, min_iterations=40)
    monkeypatch.setattr(frame_receiver, 'Denoiser', lambda *args, **kwargs: _NonzeroGaussian())
    monkeypatch.setattr(frame_receiver, 'estimate_spatial_noise',
                        lambda observation: (raw.noise_variance, dict(scope='synthetic test')))
    actual_iterate = frame_receiver.iterate
    initializations = []

    def record_start(*args, **kwargs):
        initializations.append(kwargs['initial_slopes'].copy())
        return actual_iterate(*args, **kwargs)

    monkeypatch.setattr(frame_receiver, 'iterate', record_start)
    arrays, record = receiver.infer(raw, phase_observer=forbidden_search)
    np.testing.assert_array_equal(initializations, np.zeros((1, raw.pilot.shape[1])))
    np.testing.assert_array_equal(arrays['initial_phase'], np.ones(raw.pilot.shape[:2]))
    assert 'phase_slopes' not in arrays
    assert not record['physical_path_search_used']
    assert not record['path_search_during_updates']
    assert record['phase_initialization']['seconds'] == 0.
    assert record['phase_initialization']['phase_matrix'] == 'all_one'
    assert not record['receiver_truth_used'] and not record['oracle_phase_supplied']
    assert record['phase_configuration']['initializer'] == 'zero'
    assert record['phase_updates_inside_receiver'] >= 1
    first = record['steps'][0]
    np.testing.assert_array_equal(np.asarray(first['before_phase_real'])
                                  +1j*np.asarray(first['before_phase_imag']),
                                  np.ones(raw.pilot.shape[:2]))
    with pytest.raises(TypeError, match='raw observations only'):
        receiver.infer(raw.at_estimated_phase(np.zeros(raw.pilot.shape[1])))
