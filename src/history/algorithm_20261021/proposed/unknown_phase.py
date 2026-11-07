"""Estimate frame phase from public observations, then run Proposed.

The phase fit is the same two-sweep physical fit evaluated with the baselines.
The score networks, classifier and message-passing updates operate conditional
on the resulting estimated operator. No simulation truth is an input.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import time
import warnings

import numpy as np

from afdm_jadcedd.algorithm import phase_estimation
from afdm_jadcedd.project import ROOT
from afdm_jadcedd.system.observation import array_sha256
from afdm_jadcedd.algorithm.unknown_phase_model import UnknownPhaseInput, load_input
from afdm_jadcedd.utils import sha256, write_json
from .configuration import load_configuration
from .receiver import Receiver

SCHEMA = 'afdm-proposed-estimated-phase-v1'


class UnknownPhaseReceiver:
    def __init__(self, configuration, *, device='auto'):
        self.configuration = deepcopy(configuration)
        if configuration.get('schema') != SCHEMA:
            raise ValueError('Estimated-phase Proposed configuration required')
        binding = configuration['base_configuration']
        path = ROOT/binding['path']
        if sha256(path) != binding['sha256']:
            raise ValueError('Conditional Proposed configuration identity mismatch')
        self.controls = phase_estimation.Controls(**configuration['phase_estimation'])
        self.phase_signature = phase_estimation.signature(self.controls)
        base_configuration = load_configuration(path)
        sources = {str(p.relative_to(ROOT)):sha256(p)
                   for p in Path(__file__).parent.rglob('*.py') if p != Path(__file__)}
        self.base_signature = hashlib.sha256(json.dumps(
            dict(configuration=base_configuration,sources=sources),sort_keys=True).encode()).hexdigest()
        self.signature = hashlib.sha256(json.dumps(dict(
            configuration=configuration,base=self.base_signature,phase=self.phase_signature,
            source_sha256=sha256(Path(__file__))),sort_keys=True).encode()).hexdigest()
        self.base = Receiver(base_configuration, device=device)
        self.device = self.base.device
        self.phase_arrays, self.phase_record = None, None

    def context(self):
        record = self.base.context()
        record.update(method='proposed_estimated_phase',configuration=self.configuration,
                      inference_sha256=self.signature,base_inference_sha256=self.base_signature,
                      phase_inference_sha256=self.phase_signature,
                      input_fields=list(UnknownPhaseInput.__dataclass_fields__),
                      truth_used_in_inference=False,phase_estimation=self.phase_record)
        return record

    def infer(self, inputs, *, observer=None, phase_observer=None):
        if not isinstance(inputs, UnknownPhaseInput):
            raise TypeError('UnknownPhaseInput with original pilot required')
        self.phase_arrays, self.phase_record = None, None
        started = time.monotonic()
        phase, phase_record = phase_estimation.estimate(inputs,self.controls,observer=phase_observer)
        self.phase_arrays, self.phase_record = phase, phase_record
        conditional = inputs.at_estimated_phase(phase['phase_slopes'])
        arrays, record = self.base.infer(conditional,observer=observer)
        arrays = dict(arrays,phase_slopes=phase['phase_slopes'],
                      phase_doppler_hz=phase['doppler_hz'],
                      phase_folded_delay_samples=phase['folded_delay_samples'],
                      phase_path_gains=phase['path_gains'],
                      phase_fitted_observation=phase['fitted_observation'])
        record = deepcopy(record)
        base_seconds = record['seconds']
        record.update(method='proposed_estimated_phase',configuration=self.configuration,
                      base_configuration=deepcopy(self.base.configuration),
                      inference_sha256=self.signature,base_inference_sha256=self.base_signature,
                      phase_inference_sha256=self.phase_signature,
                      input_fields=list(UnknownPhaseInput.__dataclass_fields__),
                      observation_sha256=array_sha256(inputs.observation),
                      pilot_sha256=array_sha256(inputs.pilot),
                      estimated_operator_sha256=array_sha256(conditional.operator),
                      phase_estimation=phase_record,phase_seconds=phase_record['seconds'],
                      base_seconds=base_seconds,seconds=base_seconds+phase_record['seconds'],
                      wall_seconds=time.monotonic()-started,truth_used_in_inference=False,
                      procedure='Estimate phase from observation and original pilot, then run Proposed',
                      primary_metrics=['full_channel_nmse','aer'],
                      activity_threshold_scope='Original classifier probability threshold 0.5')
        return arrays, record

    def run(self, input_path, output_path, *, observer=None, phase_observer=None):
        output = Path(output_path)
        paths = (output,output.with_suffix('.json'),output.with_suffix('.warnings.json'))
        if output.suffix != '.npz' or any(p.exists() for p in paths):
            raise ValueError('Fresh native .npz output required; existing attempts are preserved')
        output.parent.mkdir(parents=True,exist_ok=True)
        self.phase_arrays, self.phase_record = None, None
        caught = []
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always',RuntimeWarning)
                arrays, record = self.infer(load_input(input_path),observer=observer,
                                            phase_observer=phase_observer)
                if not all(np.isfinite(a).all() for a in arrays.values()):
                    raise FloatingPointError('Nonfinite unknown-phase Proposed output')
            np.savez_compressed(output,**arrays)
            record.update(input_sha256=sha256(input_path),output_sha256=sha256(output))
            write_json(output.with_suffix('.json'),record)
            return record
        except BaseException as error:
            record = self.context()
            record.update(status='FAILED',error=repr(error),
                          input_sha256=sha256(input_path) if Path(input_path).is_file() else None)
            write_json(output.with_suffix('.json'),record)
            raise
        finally:
            write_json(output.with_suffix('.warnings.json'),[
                dict(category=w.category.__name__,message=str(w.message),filename=w.filename,lineno=w.lineno)
                for w in caught])
