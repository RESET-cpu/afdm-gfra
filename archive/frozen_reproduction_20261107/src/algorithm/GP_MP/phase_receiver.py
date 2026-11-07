"""Estimate the physical phase once, then use the white conditional receiver."""
from copy import deepcopy
from pathlib import Path
from dataclasses import asdict, replace
import time
import numpy as np
from project import ROOT
from utils import read_json, sha256
from system.receiver.unknown_phase import UnknownPhaseInput
from system.receiver.noise_estimation import estimate_spatial_noise
from . import initialization
from .receiver import Receiver


class PhaseReceiver(Receiver):
    def __init__(self, configuration, *, device='auto', noise_mode='estimated'):
        binding = read_json(configuration) if isinstance(configuration, (str, Path)) else deepcopy(configuration)
        if binding['schema'] != 'c-stmp-marginal-phase-frontend-20261104-v1':
            raise ValueError('Explicit frozen phase binding required')
        for key in ('receiver_configuration', 'phase_configuration', 'initializer_source'):
            if sha256(ROOT / binding[key]) != binding[key + '_sha256']:
                raise ValueError('Changed phase binding: ' + key)
        self.frontend_binding = binding
        self.phase_controls = initialization.Controls(
            **read_json(ROOT / binding['phase_configuration'])['phase_estimation'])
        super().__init__(ROOT / binding['receiver_configuration'], device=device, noise_mode=noise_mode)

    def context(self):
        record = super().context()
        record.update(method='GP-MP-EP', implementation='algorithm.GP_MP.phase_receiver:PhaseReceiver',
                      phase_mode='estimated', supplied_phase_operator_used=False,
                      oracle_phase_supplied=False, receiver_truth_used=False,
                      input_fields=['observation', 'pilot', 'activity_prior'],
                      phase_method='Marginal physical phase estimate once, then hold fixed',
                      phase_controls=asdict(self.phase_controls), frontend_binding=self.frontend_binding)
        return record

    def infer(self, inputs, *, observer=None, phase_observer=None):
        if not isinstance(inputs, UnknownPhaseInput):
            raise TypeError('Estimated-phase GP-MP requires raw observation and original pilots')
        started = time.perf_counter()
        noise, noise_record = estimate_spatial_noise(inputs.observation)
        raw = replace(inputs, noise_variance=float(noise))
        fitted, phase_record = initialization.estimate(raw, self.phase_controls, observer=phase_observer)
        slopes = np.array(fitted['phase_slopes'], dtype=float, copy=True)
        arrays, record = super().infer(raw.at_estimated_phase(slopes), observer=observer)
        if not np.isclose(float(arrays['noise_variance_estimate']), noise, rtol=1e-12, atol=0):
            raise AssertionError('Frontend and conditional receiver noise estimates differ')
        phase = np.exp(1j * np.arange(len(raw.pilot))[:, None] * slopes[None])
        arrays.update(phase_slopes=slopes, initial_phase_slopes=slopes.copy(),
                      phase=phase, initial_phase=phase.copy())
        conditional_seconds = record['seconds']
        record.update(candidate='marginal_frontend_fixed', phase_mode='estimated',
            oracle_phase_supplied=False, receiver_truth_used=False, noise_truth_used=False,
            supplied_phase_operator_used=False, input_noise_placeholder_ignored=True,
            input_fields=['observation', 'pilot', 'activity_prior'],
            phase_method='Marginal physical phase estimate once, then hold fixed',
            phase_controls=asdict(self.phase_controls), phase_initialization=phase_record,
            phase_noise_estimation=noise_record, frontend_binding=self.frontend_binding,
            actual_iteration_controls=asdict(self.controls),
            phase_updates_inside_receiver=0, steps=[], phase_trials=[], phase_seconds=0.,
            conditional_receiver_seconds=conditional_seconds,
            seconds=time.perf_counter()-started, trace=self.last_trace,
            physical_path_search_used=True, path_search_during_updates=False,
            initializer_gain_or_power_forwarded=False)
        return arrays, record
