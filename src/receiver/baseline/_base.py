"""Shared configuration, activity readout, estimated-noise input and result IO.

Solver equations and solver-specific adapters are in somp.py, gamp.py, gnn.py
and offgrid_sbl.py. The common layer never selects or retunes a threshold.
"""
from copy import deepcopy
from dataclasses import replace
from importlib import import_module
from pathlib import Path
import hashlib
import json
import time
import warnings

import numpy as np

from workspace import ROOT
from workspace import CONFIGS
from channel.observation import ReceiverInput
from receiver.frontend.noise_estimation import estimate_spatial_noise
from receiver.frontend.noise_estimation import load_unknown_noise_input
from fileio import sha256
from fileio import write_json
from receiver.baseline import METHODS
from receiver.baseline._common import coefficient_activity
from receiver.baseline._common import FrozenReadout
from receiver.baseline._validation import METHOD_KEYS
from receiver.baseline._validation import inference_sources
from receiver.baseline._validation import inference_signature
from receiver.baseline._validation import verify_current_sources

GRID = dict(delay_step=1., doppler_points=None, doppler_step_hz=30000.)


class ConditionalReceiver:
    """Common dictionary/readout boundary for SOMP, GAMP-SBL and GNN-ASPL."""
    def __init__(self, configuration, method, kernel):
        self.configuration = deepcopy(configuration)
        self.method, self.kernel = method, kernel
        cfg = self.configuration
        if (cfg.get('schema') != 'afdm-selected-baselines-v1'
                or cfg.get('dictionary') != GRID
                or cfg.get('channel_output') != 'dictionary_reconstruction'):
            raise ValueError('Selected baseline configuration and common integer dictionary required')
        self.setting = cfg['methods'][METHOD_KEYS[method]]
        self.signature = inference_signature(cfg, method)
        if self.setting.get('readout_inference_sha256') != self.signature:
            raise ValueError('Activity readout is bound to a different solver, settings or weights')
        self.readout = FrozenReadout(cfg['readout'])
        if method == 'gamp' and self.setting['noise_hyperparameters'] != 'public_noise_Gamma_MAP':
            raise ValueError('The selected MMV Gamma hyperparameters use public noise variance')
        self.native = kernel.create_native(self) if hasattr(kernel, 'create_native') else None

    def infer(self, inputs, *, observer=None):
        if not isinstance(inputs, ReceiverInput):
            raise TypeError('Public four-field ReceiverInput required')
        started = time.perf_counter()
        method, cfg = self.method, self.configuration
        arrays, native = self.kernel.infer_known(self, inputs, observer=observer)
        score, energy = coefficient_activity(arrays['coefficients'], inputs.operator.shape[1])
        decision, rule = self.readout.decide(inputs, method, score, energy)
        arrays.update(activity_score=score, relative_coefficient_score=score,
                      coefficient_energy=energy, activity_decision=decision)
        native.update(activity_statistic='ding_eq27_normalized_coefficient_energy',
                      activity_threshold=rule['threshold'], activity_comparator='>=',
                      activity_decision_available=True, public_numeric_control=rule,
                      threshold_status='FROZEN_RULE_REUSED_ACROSS_USER_COUNTS')
        if not all(np.isfinite(value).all() for value in arrays.values()):
            raise FloatingPointError('Nonfinite selected baseline output')
        native.update(status='COMPLETE', method=METHOD_KEYS[method], algorithm_id=method,
            configuration=cfg, seconds=time.perf_counter()-started,
            inference_sha256=self.signature, source_sha256=inference_sources(method),
            dictionary=cfg['dictionary'], coefficient_coordinates='physical',
            truth_loaded=False, truth_used_in_inference=False, activity_count_or_truth_used=False,
            true_snr_or_activity_count_used=False)
        return arrays, native


class EstimatedNoiseBaselineReceiver:
    """The four baselines share the same observation-only noise boundary."""
    def __init__(self, method, *, config=None, device='cpu'):
        if method not in METHODS:
            raise ValueError('Select one baseline: '+', '.join(METHODS))
        verify_current_sources()
        self.method = method
        self.kernel = import_module('.'+method, __package__)
        filename = 'offgrid_sbl.json' if method == 'offgrid_sbl' else 'baselines.json'
        configuration = json.loads(Path(config or CONFIGS/'final'/filename).read_text())
        # Resolve only current resource paths. There are no historical path aliases.
        configuration['readout']['path'] = str(ROOT/configuration['readout']['path'])
        if method == 'gnn':
            setting = configuration['methods'][METHOD_KEYS[method]]
            setting['checkpoint_path'] = str(ROOT/setting['checkpoint_path'])
        self.base = (self.kernel.OffGridReceiver(configuration, method) if method == 'offgrid_sbl'
                     else ConditionalReceiver(configuration, method, self.kernel))
        path = CONFIGS/'final/baseline_noise.json'
        self.noise_config = json.loads(path.read_text())
        self.configuration = dict(schema=self.noise_config['schema'], method=method,
            base_configuration=deepcopy(self.base.configuration), noise_estimation=self.noise_config)
        self.sources = inference_sources(method)
        self.sources[path.relative_to(ROOT).as_posix()] = sha256(path)
        self.signature = hashlib.sha256(json.dumps(dict(configuration=self.configuration,
            base=self.base.signature, sources=self.sources), sort_keys=True).encode()).hexdigest()

    def infer(self, inputs, *, observer=None):
        if not isinstance(inputs, ReceiverInput):
            raise TypeError('ReceiverInput with a conditional pilot operator required')
        started = time.perf_counter()
        spatial, spatial_record = estimate_spatial_noise(inputs.observation)
        estimated = replace(inputs, noise_variance=spatial)
        if hasattr(self.kernel, 'infer_estimated'):
            if observer is not None:
                raise ValueError('This baseline records its native trace without an observer')
            arrays, record, history = self.kernel.infer_estimated(self, estimated)
        else:
            arrays, record = self.base.infer(estimated, observer=observer)
            history = [spatial]
        noise = float(history[-1])
        arrays = dict(arrays, noise_variance_estimate=np.asarray(noise),
                      noise_variance_history=np.asarray(history))
        record.update(status='COMPLETE', algorithm_id=self.method,
            method=self.method+'_estimated_noise', noise_mode='estimated',
            noise_variance_estimate=noise, noise_estimation_source=self.noise_config['sources'][self.method],
            spatial_noise_estimation=spatial_record, supplied_noise_variance_used=False,
            noise_truth_used=False, truth_used_in_inference=False, truth_loaded=False,
            true_snr_or_activity_count_used=False, activity_count_or_truth_used=False,
            input_fields=['observation', 'operator', 'activity_prior'],
            configuration=self.configuration, inference_sha256=self.signature,
            base_inference_sha256=self.base.signature, noise_source_sha256=self.sources,
            threshold_status='EXISTING_RULE_REUSED_WITH_ESTIMATED_NOISE',
            threshold_scope=self.noise_config['activity_rule'],
            seconds=time.perf_counter()-started,
            physical_noise_estimate_role='inference_and_activity_readout')
        if not all(np.isfinite(value).all() for value in arrays.values()):
            raise FloatingPointError('Nonfinite estimated-noise baseline output')
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
                arrays, record = self.infer(load_unknown_noise_input(input_path, phase_mode='known'),
                                           observer=observer)
            np.savez_compressed(output, **arrays)
            record.update(input_sha256=sha256(input_path), output_sha256=sha256(output))
            write_json(output.with_suffix('.json'), record)
            return record
        except Exception as error:
            write_json(output.with_suffix('.json'), dict(status='FAILED', method=self.method,
                error=repr(error), inference_sha256=self.signature, noise_mode='estimated'))
            raise
        finally:
            write_json(output.with_suffix('.warnings.json'), [dict(category=w.category.__name__,
                message=str(w.message), filename=w.filename, lineno=w.lineno) for w in caught])
