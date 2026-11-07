"""Observation-only noise handling for the five selected conditional baselines.

Native weights, dictionaries and activity thresholds retain their provenance.
The new inference identity explicitly binds the noise adaptation; reusing an
old threshold is not a claim that it has been calibrated for estimated noise.
"""
from copy import deepcopy
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import time
import warnings

import numpy as np

from afdm_jadcedd.project import ROOT, CONFIGS
from afdm_jadcedd.system.dictionary import AFDMGrid
from afdm_jadcedd.system.observation import ReceiverInput
from afdm_jadcedd.utils import sha256, write_json
from .ding import coefficient_activity
from .gamp_sbl_mmv import MMVControls, solve_mmv
from .readout import nearest_node, public_snr_db
from .noise_estimation import estimate_spatial_noise, load_unknown_noise_input
from .offgrid.atoms import activity_score
from . import offgrid_noise
from ..registry import ALGORITHMS, build_receiver


class EstimatedNoiseBaselineReceiver:
    def __init__(self, method, *, config=None, device='auto'):
        if method not in ALGORITHMS[1:]:
            raise ValueError('Estimated noise is currently implemented for the five baselines')
        self.method = method
        self.base = build_receiver(method, config=config, device=device)
        path = CONFIGS/'baseline_noise.json'
        self.noise_config = json.loads(path.read_text())
        self.configuration = dict(schema=self.noise_config['schema'], method=method,
            base_configuration=deepcopy(self.base.configuration), noise_estimation=self.noise_config)
        sources = [Path(__file__), Path(__file__).with_name('noise_estimation.py'),
                   Path(__file__).with_name('offgrid_noise.py'), path]
        self.sources = {str(p.relative_to(ROOT)): sha256(p) for p in sources}
        self.signature = hashlib.sha256(json.dumps(dict(configuration=self.configuration,
            base=self.base.signature, sources=self.sources), sort_keys=True).encode()).hexdigest()

    def infer(self, inputs, *, observer=None):
        if not isinstance(inputs, ReceiverInput):
            raise TypeError('ReceiverInput with a conditional pilot operator required')
        started = time.perf_counter()
        # Replace even the legacy object's field before invoking any native code.
        # The spatial estimate supplies both Bayesian noise priors' scale.
        # It is diagnostic only for L-DAMP, whose denoiser uses residual noise.
        spatial, spatial_record = estimate_spatial_noise(inputs.observation)
        estimated = replace(inputs, noise_variance=spatial)
        if self.method == 'gamp':
            if observer is not None:
                raise ValueError('GAMP-SBL MMV records its native trace without an observer')
            arrays, record, history = self._gamp(estimated)
        elif self.method == 'offgrid_sbl':
            if observer is not None:
                raise ValueError('Off-grid SBL records its native trace without an observer')
            arrays, record, history = self._offgrid(estimated)
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
            seconds=time.perf_counter()-started)
        if self.method == 'ldamp':
            record.update(physical_noise_estimate_role='diagnostic_only',
                inference_noise='Native residual covariance estimates equivalent denoiser noise in normalized units')
            if record.get('trace') and 'effective_complex_variance' in record['trace'][0]:
                arrays['effective_noise_variance_history_normalized'] = np.asarray(
                    [row['effective_complex_variance'] for row in record['trace']])
        else:
            record['physical_noise_estimate_role'] = 'inference_and_activity_readout'
        if not all(np.isfinite(value).all() for value in arrays.values()):
            raise FloatingPointError('Nonfinite estimated-noise baseline output')
        return arrays, record

    def _gamp(self, inputs):
        grid = AFDMGrid.from_operator(inputs.operator, **self.base.configuration['dictionary'])
        y = grid.stack(inputs.observation)
        prior_count = self.noise_config['gamp']['noise_prior_observation_weight']*y.size
        controls = MMVControls(**self.base.setting['solver'],
            noise_shape=1+prior_count, noise_rate=prior_count*inputs.noise_variance)
        result = solve_mmv(np.ascontiguousarray(grid.design*grid.norms[None, :]), y, controls)
        z = result['mean']
        score, energy = coefficient_activity(z, inputs.operator.shape[1])
        final_inputs = replace(inputs, noise_variance=result['noise_variance'])
        decision, rule = self.base.readout.decide(final_inputs, self.method, score, energy)
        arrays = dict(estimate=grid.reconstruct(z*grid.norms[:, None]), coefficients=z,
            activity_score=score, relative_coefficient_score=score,
            coefficient_energy=energy, activity_decision=decision)
        record = dict(iterations=result['iterations'], stopping_reason=result['stopping_reason'],
            trace=result['trace'], controls=asdict(controls), shared_row_precision=True,
            noise_update='Complex MMV Gamma MAP using the GAMP output posterior',
            noise_prior_reference_variance=inputs.noise_variance,
            noise_prior_reference_source='Spatial covariance MDL estimate of the same observation',
            noise_prior_observations=prior_count,
            noise_fixed=False, damping=1., dictionary=self.base.configuration['dictionary'],
            coefficient_coordinates='physical', activity_statistic='ding_eq27_normalized_coefficient_energy',
            activity_threshold=rule['threshold'], activity_comparator='>=',
            activity_decision_available=True, public_numeric_control=rule)
        initial = max(controls.initial_noise_fraction*float(np.mean(abs(y)**2)), controls.variance_floor)
        return arrays, record, [initial]+[row['noise_variance'] for row in result['trace']]

    def _offgrid(self, inputs):
        if inputs.observation.shape[-1] != 16 or inputs.operator.shape[-1] != 16:
            raise ValueError('Current AFDM physical model requires N=16')
        noise_setting = self.noise_config['offgrid_sbl']
        prior_count = noise_setting['noise_prior_observation_weight']*inputs.observation.size
        controls = dict(noise_shape=1+prior_count, noise_rate=prior_count*inputs.noise_variance,
                        initial_noise_fraction=noise_setting['initial_noise_fraction'])
        result = offgrid_noise.solve(inputs, self.base.settings, **controls)
        score, energy = activity_score(result['estimate'])
        value = public_snr_db(replace(inputs, noise_variance=result['noise_variance']))
        index = nearest_node(value, self.base.nodes)
        threshold = float(self.base.thresholds[index])
        arrays = dict(estimate=result['estimate'], component_user_ids=result['user_ids'],
            folded_delay_samples=result['positions'][:, 0], doppler_hz=result['positions'][:, 1]*30000.,
            component_coefficients=result['gains'], activity_score=score, channel_energy=energy,
            activity_decision=(score >= threshold)&(energy > 0))
        record = {key: value for key, value in result.items()
                  if key not in ('estimate', 'user_ids', 'positions', 'gains')}
        record.update(activity_threshold=threshold, readout_snr_node_db=float(self.base.nodes[index]),
            public_estimated_snr_db=value, activity_statistic=self.base.policy['statistic'],
            activity_comparator='>=', activity_decision_available=True,
            noise_controls=controls, noise_fixed=False,
            noise_prior_reference_variance=inputs.noise_variance,
            noise_prior_reference_source='Spatial covariance MDL estimate of the same observation',
            noise_prior_observations=prior_count,
            component_coefficient_convention='free complex coefficient of scalar-phase-normalized AFDM atom',
            component_count_meaning='screened dictionary rows', continuous_delay_doppler_estimation=True,
            paper_implementation_scope='AFDM/shared-MMV adaptation of Wei Eqs. (45)-(46), with an observation-estimated Gamma prior scale')
        return arrays, record, [result['initial_noise_variance']]+[
            row['noise_variance'] for row in result['trace']]

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
