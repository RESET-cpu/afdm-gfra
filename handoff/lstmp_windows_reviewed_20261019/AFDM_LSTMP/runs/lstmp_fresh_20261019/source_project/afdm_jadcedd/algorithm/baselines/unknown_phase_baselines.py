"""Estimate cross-frame phase from public inputs for each selected baseline."""
from copy import deepcopy
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import time
import warnings

import numpy as np

from .. import phase_estimation
from ..registry import ALGORITHMS, build_receiver
from ..unknown_phase_model import UnknownPhaseInput, load_input
from .noise_estimation import estimate_spatial_noise, load_unknown_noise_input
from .baseline_noise import EstimatedNoiseBaselineReceiver
from afdm_jadcedd.project import ROOT
from afdm_jadcedd.system.observation import array_sha256
from afdm_jadcedd.utils import sha256, write_json


def default_noise_mode(method):
    mainline = json.loads((ROOT/'MAINLINE.json').read_text())
    return mainline['algorithms'][method].get('noise_mode', 'known' if method == 'proposed' else 'estimated')


def phase_implementation(name=None):
    if name is None:
        name = json.loads((ROOT/'MAINLINE.json').read_text()).get('phase_policy', {}).get('frontend', 'original')
    if name == 'original':
        return phase_estimation
    if name == 'optimized':
        from .. import phase_estimation_optimized
        return phase_estimation_optimized
    raise ValueError('Unknown phase frontend: '+str(name))


class UnknownPhaseBaselineReceiver:
    def __init__(self, method, *, config=None, device='auto', noise_mode=None, phase_frontend=None):
        if method not in ALGORITHMS[1:]:
            raise ValueError('Select one of the five mainline baselines')
        self.method = method
        noise_mode = noise_mode or default_noise_mode(method)
        self.phase_module = phase_implementation(phase_frontend)
        if noise_mode not in ('estimated', 'known'):
            raise ValueError('Select estimated or known noise')
        self.noise_mode = noise_mode
        factory = EstimatedNoiseBaselineReceiver if noise_mode == 'estimated' else build_receiver
        self.base = factory(method, config=config, device=device)
        self.controls = self.phase_module.Controls()
        self.phase_signature = self.phase_module.signature(self.controls)
        self.configuration = dict(schema='afdm-baseline-estimated-phase-v1', method=method,
            base_configuration=deepcopy(self.base.configuration), phase_estimation=asdict(self.controls),
            noise_mode=noise_mode, phase_implementation=self.phase_module.__name__)
        self.signature = hashlib.sha256(json.dumps(dict(configuration=self.configuration,
            base=self.base.signature, phase=self.phase_signature, source=sha256(Path(__file__))),
            sort_keys=True).encode()).hexdigest()

    def infer(self, inputs, *, observer=None, phase_observer=None):
        if not isinstance(inputs, UnknownPhaseInput):
            raise TypeError('UnknownPhaseInput with the original pilot required')
        started = time.perf_counter()
        if self.noise_mode == 'estimated':
            noise, _ = estimate_spatial_noise(inputs.observation)
            inputs = replace(inputs, noise_variance=noise)
        phase, phase_record = self.phase_module.estimate(inputs, self.controls, observer=phase_observer)
        phase_record['residual_normalization_noise_variance'] = inputs.noise_variance
        phase_record['noise_mode'] = self.noise_mode
        conditional = inputs.at_estimated_phase(phase['phase_slopes'])
        native_arrays, native_record = self.base.infer(conditional, observer=observer)
        arrays = dict(native_arrays, phase_slopes=phase['phase_slopes'],
            phase_doppler_hz=phase['doppler_hz'], phase_folded_delay_samples=phase['folded_delay_samples'],
            phase_path_gains=phase['path_gains'], phase_fitted_observation=phase['fitted_observation'])
        if not all(np.isfinite(value).all() for value in arrays.values()):
            raise FloatingPointError('Nonfinite estimated-phase baseline output')
        record = dict(native_record, method=self.method+'_estimated_phase',
            configuration=self.configuration, inference_sha256=self.signature,
            base_inference_sha256=self.base.signature, phase_inference_sha256=self.phase_signature,
            input_fields=(['observation', 'pilot', 'activity_prior'] if self.noise_mode == 'estimated'
                          else list(UnknownPhaseInput.__dataclass_fields__)),
            phase_mode='estimated', noise_mode=self.noise_mode,
            observation_sha256=array_sha256(inputs.observation), pilot_sha256=array_sha256(inputs.pilot),
            estimated_operator_sha256=array_sha256(conditional.operator), phase_estimation=phase_record,
            base_seconds=native_record['seconds'], phase_seconds=phase_record['seconds'],
            seconds=native_record['seconds']+phase_record['seconds'], wall_seconds=time.perf_counter()-started,
            truth_used_in_inference=False,
            procedure='Estimate phase from observation and original pilot, then run the conditional baseline')
        return arrays, record

    def run(self, input_path, output_path, *, observer=None):
        output = Path(output_path)
        if output.suffix != '.npz' or output.exists() or output.with_suffix('.json').exists():
            raise ValueError('Fresh .npz output required')
        output.parent.mkdir(parents=True, exist_ok=True)
        caught = []
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always', RuntimeWarning)
                inputs = (load_unknown_noise_input(input_path, phase_mode='estimated')
                          if self.noise_mode == 'estimated' else load_input(input_path))
                arrays, record = self.infer(inputs, observer=observer)
            np.savez_compressed(output, **arrays)
            record.update(input_sha256=sha256(input_path), output_sha256=sha256(output))
            write_json(output.with_suffix('.json'), record)
            return record
        except Exception as error:
            write_json(output.with_suffix('.json'), dict(status='FAILED', method=self.method+'_estimated_phase',
                error=repr(error), inference_sha256=self.signature, truth_used_in_inference=False))
            raise
        finally:
            write_json(output.with_suffix('.warnings.json'), [dict(category=w.category.__name__,
                message=str(w.message), filename=w.filename, lineno=w.lineno) for w in caught])


def build_estimated_phase_receiver(method, *, config=None, device='auto', noise_mode=None):
    noise_mode = noise_mode or default_noise_mode(method)
    if method != 'proposed':
        return UnknownPhaseBaselineReceiver(method, config=config, device=device,
                                            noise_mode=noise_mode)
    selected = json.loads((ROOT/'MAINLINE.json').read_text())['algorithms']['proposed']['configuration']
    path = ROOT/selected if config is None else Path(config)
    configuration = json.loads(path.read_text())
    schema = configuration.get('schema', '')
    if schema == 'afdm-proposed-estimated-phase-v2' or (schema == 'afdm-proposed-estimated-phase-v1' and noise_mode == 'estimated'):
        from ..proposed_frontend_candidate import FrontendReceiver, SCHEMA
        return FrontendReceiver(dict(configuration, schema=SCHEMA, noise_mode=noise_mode), device=device)
    if schema.startswith(('afdm-proposed-estimated-phase-', 'afdm-proposed-iterative-phase-')):
        if noise_mode != 'known':
            raise ValueError('Estimated noise is supported for the selected Proposed frontend')
        return build_receiver(method, config=path, device=device)
    if noise_mode == 'estimated' or phase_implementation().__name__.endswith('phase_estimation_optimized'):
        from ..proposed_frontend_candidate import FrontendReceiver, SCHEMA
        return FrontendReceiver(dict(schema=SCHEMA, noise_mode=noise_mode,
            base_configuration=dict(path=str(path.resolve()), sha256=sha256(path)),
            phase_estimation=asdict(phase_implementation().Controls())), device=device)
    from ..proposed.unknown_phase import UnknownPhaseReceiver, SCHEMA
    return UnknownPhaseReceiver(dict(schema=SCHEMA,
        base_configuration=dict(path=str(path.resolve()), sha256=sha256(path)),
        phase_estimation=asdict(phase_estimation.Controls())), device=device)
