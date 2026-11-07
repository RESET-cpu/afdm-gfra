"""Estimate frame phases once, then run the unchanged current C-STMP.

This reuses the existing physical phase frontend; it does not perform the
STMP joint phase updates. See paper/C-STMP/docs/C_STMP_PHASE_PROBE_20261027.md.
"""
from dataclasses import asdict
import time

import numpy as np

from project import ROOT
from utils import read_json, sha256
from system.observation import ReceiverInput
from system.receiver.unknown_phase import UnknownPhaseInput
from system.receiver.noise_estimation import estimate_spatial_noise
from system.receiver import phase_estimation
from algorithm.C_STMP_variance_em_20261025.receiver import Receiver as ConditionalReceiver


class Receiver(ConditionalReceiver):
    def __init__(self, configuration, *, device='cpu', noise_mode='estimated'):
        if noise_mode != 'estimated':
            raise ValueError('This candidate estimates noise from the observations')
        binding = read_json(configuration)
        if binding['schema'] != 'c-stmp-fixed-estimated-phase-v1':
            raise ValueError('Explicit independent phase binding required')
        for key in ('receiver_configuration', 'phase_configuration'):
            if sha256(ROOT / binding[key]) != binding[key + '_sha256']:
                raise ValueError('Bound configuration changed: ' + key)
        self.phase_controls = phase_estimation.Controls(
            **read_json(ROOT / binding['phase_configuration'])['phase_estimation'])
        self.phase_binding = binding
        super().__init__(ROOT / binding['receiver_configuration'],
                         device=device, noise_mode=noise_mode)

    def infer(self, inputs, *, observer=None, phase_observer=None):
        if isinstance(inputs, ReceiverInput):
            # Retain a control route with exactly the inherited computation.
            arrays, record = super().infer(inputs, observer=observer)
            record.update(phase_mode='known', oracle_phase_supplied=True,
                          receiver_truth_used=True)
            return arrays, record
        if not isinstance(inputs, UnknownPhaseInput):
            raise TypeError('Raw observation and original pilots required')
        started = time.perf_counter()
        noise, noise_record = estimate_spatial_noise(inputs.observation)
        # Discard the input noise placeholder; phase fitting also uses estimated noise.
        raw = UnknownPhaseInput(inputs.observation, inputs.pilot,
                                float(noise), inputs.activity_prior)
        fitted, phase_record = phase_estimation.estimate(
            raw, self.phase_controls, observer=phase_observer)
        arrays, record = super().infer(
            raw.at_estimated_phase(fitted['phase_slopes']), observer=observer)
        if not np.isclose(float(arrays['noise_variance_estimate']), noise,
                          rtol=1e-12, atol=0):
            raise AssertionError('Phase and conditional receiver noise estimates differ')
        conditional_seconds = record['seconds']
        arrays.update(phase_slopes=fitted['phase_slopes'],
                      phase=np.exp(1j * np.arange(len(inputs.pilot))[:, None]
                                   * fitted['phase_slopes']))
        record.update(
            phase_mode='estimated', oracle_phase_supplied=False,
            receiver_truth_used=False, noise_truth_used=False,
            supplied_phase_operator_used=False,
            phase_method='estimate_once_then_hold_fixed',
            phase_updates_inside_receiver=0,
            phase_controls=asdict(self.phase_controls),
            phase_estimation=phase_record,
            phase_noise_estimation=noise_record,
            conditional_receiver_seconds=conditional_seconds,
            seconds=time.perf_counter() - started,
            input_fields=['observation', 'pilot', 'activity_prior'],
            input_noise_placeholder_ignored=True)
        return arrays, record
