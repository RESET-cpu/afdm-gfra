"""Alternate frozen Proposed inference and observation-based phase updates."""
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import time

import numpy as np

from . import phase_refinement
from .proposed.unknown_phase import UnknownPhaseReceiver, SCHEMA as INITIAL_SCHEMA
from .unknown_phase_model import UnknownPhaseInput
from afdm_jadcedd.system.observation import array_sha256
from afdm_jadcedd.utils import sha256

SCHEMA = 'afdm-proposed-iterative-phase-v1'


class IterativePhaseReceiver(UnknownPhaseReceiver):
    def __init__(self, configuration, *, device='auto'):
        if configuration.get('schema') != SCHEMA:
            raise ValueError('Iterative-phase Proposed configuration required')
        initial = deepcopy(configuration)
        self.refinement_controls = phase_refinement.Controls(**initial.pop('phase_refinement'))
        self.refinement_controls.validate(16)
        initial['schema'] = INITIAL_SCHEMA
        super().__init__(initial, device=device)
        self.initial_configuration = initial
        self.initial_signature = self.signature
        self.configuration = deepcopy(configuration)
        self.signature = hashlib.sha256(json.dumps(dict(configuration=configuration,
            initial=self.initial_signature, source_sha256=sha256(Path(__file__)),
            refinement_sha256=sha256(Path(phase_refinement.__file__))), sort_keys=True).encode()).hexdigest()
        self.refinement_trace = []

    def context(self):
        record = super().context()
        record.update(method='proposed_iterative_phase', phase_refinement=self.refinement_trace)
        return record

    def infer(self, inputs, *, observer=None, phase_observer=None):
        self.refinement_trace = []
        start = time.monotonic()
        arrays, record = super().infer(inputs, observer=observer, phase_observer=phase_observer)
        arrays, record = self.refine_from_initial(inputs, arrays, record, observer=observer)
        record.update(initial_result_reused=False, full_pipeline_wall_seconds=time.monotonic()-start)
        return arrays, record

    def refine_from_initial(self, inputs, initial_arrays, initial_record, *, observer=None):
        """Reuse an audited observation-only initializer; the evaluator binds files.

        Public infer/run always recomputes the initializer. This entry point
        avoids repeating a bitwise-audited frozen initial pass during comparisons.
        """
        if not isinstance(inputs, UnknownPhaseInput):
            raise TypeError('UnknownPhaseInput with original pilot required')
        if (initial_record['observation_sha256'] != array_sha256(inputs.observation)
                or initial_record['pilot_sha256'] != array_sha256(inputs.pilot)
                or initial_record['base_configuration'] != self.base.configuration
                or initial_record['truth_used_in_inference']):
            raise ValueError('Initial result must bind the same public input and base configuration')
        self.refinement_trace = []
        started = time.monotonic()
        arrays = {k: np.array(v, copy=True) for k, v in initial_arrays.items()}
        slopes = arrays['phase_slopes'].copy()
        conditional = inputs.at_estimated_phase(slopes)
        if initial_record['estimated_operator_sha256'] != array_sha256(conditional.operator):
            raise ValueError('Initial operator does not match its estimated phase')
        phase_history = [slopes.copy()]
        records = [deepcopy(initial_record)]
        native_keys = ('estimate', 'conditional_matrix', 'probabilities', 'activity_decision', 'spatial_covariance')
        native = {k: arrays[k] for k in native_keys}
        reason = 'OUTER_UPDATE_BUDGET'
        for outer in range(1, self.refinement_controls.outer_updates+1):
            proposed_slopes, phase_record = phase_refinement.refine(
                inputs, native['estimate'], slopes, self.refinement_controls)
            phase_record['outer_update'] = outer
            self.refinement_trace.append(phase_record)
            if phase_record['max_phase_change'] <= self.refinement_controls.phase_tolerance:
                phase_record['applied'] = False
                reason = 'PHASE_STABLE'
                break
            phase_record['applied'] = True
            slopes = proposed_slopes
            conditional = inputs.at_estimated_phase(slopes)
            def observe(row, *state):
                if observer is not None:
                    observer(dict(row, outer_update=outer), *state)
            native, base_record = self.base.infer(conditional, observer=observe)
            records.append(base_record)
            phase_history.append(slopes.copy())
        outputs = dict(native, phase_slopes=slopes, phase_slope_history=np.stack(phase_history))
        for key in ('phase_slopes', 'phase_doppler_hz', 'phase_folded_delay_samples',
                    'phase_path_gains', 'phase_fitted_observation'):
            outputs['initial_'+key] = arrays[key]
        record = deepcopy(records[-1])
        counters = ('first_score_samples', 'second_score_samples', 'first_score_calls', 'second_score_calls',
                    'classifier_calls', 'classifier_samples', 'classifier_seconds', 'activity_evidence_calls',
                    'activity_evidence_samples', 'activity_evidence_seconds')
        record.update({k: sum(r.get(k, 0) for r in records) for k in counters})
        trace = [dict(row, outer_update=i) for i, r in enumerate(records) for row in r['trace']]
        refinement_seconds = sum(r['seconds'] for r in self.refinement_trace)
        base_seconds = initial_record['base_seconds']+sum(r['seconds'] for r in records[1:])
        record.update(method='proposed_iterative_phase', configuration=self.configuration,
            base_configuration=deepcopy(self.base.configuration), inference_sha256=self.signature,
            base_inference_sha256=self.base_signature, initial_inference_sha256=self.initial_signature,
            phase_inference_sha256=self.phase_signature, input_fields=list(inputs.arguments()),
            observation_sha256=array_sha256(inputs.observation), pilot_sha256=array_sha256(inputs.pilot),
            estimated_operator_sha256=array_sha256(conditional.operator),
            initial_phase_estimation=deepcopy(initial_record['phase_estimation']),
            phase_refinement=deepcopy(self.refinement_trace), phase_refinement_controls=asdict(self.refinement_controls),
            conditional_runs=len(records), conditional_iterations=[r['iterations'] for r in records],
            conditional_stopping_reasons=[r['stopping_reason'] for r in records],
            iterations=sum(r['iterations'] for r in records), trace=trace, stopping_reason=reason,
            converged=reason=='PHASE_STABLE' and records[-1]['converged'],
            phase_seconds=initial_record['phase_seconds'], phase_refinement_seconds=refinement_seconds,
            base_seconds=base_seconds, seconds=initial_record['phase_seconds']+base_seconds+refinement_seconds,
            incremental_seconds=time.monotonic()-started, initial_result_reused=True,
            initial_seconds=initial_record['seconds'], truth_used_in_inference=False, truth_loaded=False,
            phase_output_scope='phase_slopes final; initial_phase_* belong only to the physical initializer',
            inner_state_policy='Fresh original initialization after each operator update',
            procedure='Alternate soft full-channel Proposed inference and constrained phase-slope updates',
            primary_metrics=['full_channel_nmse', 'aer'])
        record.pop('phase_estimation', None)
        record.pop('wall_seconds', None)
        return outputs, record
