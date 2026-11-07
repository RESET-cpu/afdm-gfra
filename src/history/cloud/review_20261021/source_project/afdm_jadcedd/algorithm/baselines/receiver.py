"""One public receiver for the selected SOMP, GAMP-SBL, GNN-ASPL and EM kernels."""
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import time

import numpy as np

from afdm_jadcedd.project import ROOT
from afdm_jadcedd.system.dictionary import AFDMGrid
from afdm_jadcedd.system.observation import ReceiverInput, load_input
from afdm_jadcedd.utils import sha256, write_json
from .ding import coefficient_activity
from .gamp_sbl_mmv import MMVControls, solve_mmv
from .readout import FrozenReadout
from .somp import solve_somp

GRID = dict(delay_step=1., doppler_points=None, doppler_step_hz=30000.)
METHOD_KEYS = dict(somp='somp', gamp='gamp_sbl_mmv', gnn='gnn_aspl_ding2026',
                   em='em_gamp_zhao2025')
DEFAULT_CONFIG = ROOT/'configs/baselines.json'


def load_configuration(path=None):
    return json.loads((DEFAULT_CONFIG if path is None else Path(path)).read_text())


def inference_sources(method):
    names = ['receiver.py', 'readout.py', 'ding.py'] + {
        'somp': ['somp.py', 'common.py'], 'gamp': ['gamp_sbl_mmv.py'],
        'gnn': ['gnn_aspl.py'], 'em': ['em_gamp_zhao2025.py'],
    }[method]
    paths = [Path(__file__).with_name(name) for name in names]
    paths += sorted((ROOT/'src/afdm_jadcedd/system').rglob('*.py'))
    paths += [ROOT/'src/afdm_jadcedd/utils.py']
    return {str(path.relative_to(ROOT)): sha256(path) for path in paths}


def inference_signature(configuration, method):
    setting = deepcopy(configuration['methods'][METHOD_KEYS[method]])
    setting.pop('readout_inference_sha256', None)
    setting.pop('checkpoint_path', None)  # Identity is the verified checkpoint SHA.
    value = dict(method=method, dictionary=configuration['dictionary'], settings=setting,
                 sources=inference_sources(method))
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    allow_nan=False).encode()).hexdigest()


class BaselineReceiver:
    def __init__(self, configuration, method):
        if method not in METHOD_KEYS:
            raise ValueError('Select somp, gamp, gnn or em')
        self.configuration = deepcopy(configuration)
        self.method = method
        cfg = self.configuration
        if (cfg.get('schema') != 'afdm-selected-baselines-v1'
                or cfg.get('dictionary') != GRID
                or cfg.get('channel_output') != 'dictionary_reconstruction'):
            raise ValueError('Selected baseline configuration and common integer dictionary required')
        self.setting = cfg['methods'][METHOD_KEYS[method]]
        self.signature = inference_signature(cfg, method)
        self.native = None
        if method in ('somp', 'gamp', 'gnn'):
            if self.setting.get('readout_inference_sha256') != self.signature:
                raise ValueError('Frozen readout is bound to a different solver, settings or weights')
            self.readout = FrozenReadout(cfg['readout'])
        if method == 'gamp' and self.setting['noise_hyperparameters'] != 'public_noise_Gamma_MAP':
            raise ValueError('The selected MMV Gamma hyperparameters use public noise variance')
        if method == 'gnn':
            from .gnn_aspl import GNNASPLReceiver
            native_cfg = deepcopy(cfg)
            setting = native_cfg['methods'][METHOD_KEYS[method]]
            setting['checkpoint_path'] = str(ROOT/setting['checkpoint_path'])
            setting.update(activity_threshold=None,
                           activity_statistic='reconstructed_channel_energy', activity_comparator='>')
            self.native = GNNASPLReceiver(native_cfg)
        elif method == 'em':
            from .em_gamp_zhao2025 import ZhaoGAMPReceiver
            self.native = ZhaoGAMPReceiver(cfg)

    def infer(self, inputs, *, observer=None):
        if not isinstance(inputs, ReceiverInput):
            raise TypeError('Public four-field ReceiverInput required')
        started = time.perf_counter()
        method, cfg = self.method, self.configuration
        if self.native is not None:
            arrays, native = self.native.infer(inputs, observer=observer)
        else:
            grid = AFDMGrid.from_operator(inputs.operator, **cfg['dictionary'])
            y = grid.stack(inputs.observation)
            if method == 'somp':
                callback = None if observer is None else lambda row, z: observer(row, lambda: grid.reconstruct(z))
                result = solve_somp(grid.design, y, inputs.noise_variance,
                                    observer=callback, **self.setting['solver'])
                z = result['mean']/grid.norms[:, None]
                estimate = grid.reconstruct(result['mean'])
                native = dict(iterations=result['iterations'], stopping_reason=result['status'],
                              trace=result['trace'], supplied_noise_variance_used=True)
            else:
                if observer is not None:
                    raise ValueError('GAMP-SBL MMV records its native trace without an observer')
                design = np.ascontiguousarray(grid.design*grid.norms[None, :])
                controls = MMVControls(**self.setting['solver'], noise_shape=1+y.size,
                                       noise_rate=y.size*inputs.noise_variance)
                result = solve_mmv(design, y, controls)
                z = result['mean']
                estimate = grid.reconstruct(z*grid.norms[:, None])
                native = dict(iterations=result['iterations'], stopping_reason=result['stopping_reason'],
                    trace=result['trace'], controls=asdict(controls), shared_row_precision=True,
                    noise_variance_estimate=result['noise_variance'], noise_mode='common_learned_Gamma_MAP',
                    noise_fixed=False, damping=1., supplied_noise_variance_used=True)
            arrays = dict(estimate=estimate, coefficients=z)
        if method != 'em':
            score, energy = coefficient_activity(arrays['coefficients'], inputs.operator.shape[1])
            decision, rule = self.readout.decide(inputs, method, score, energy)
            arrays.update(activity_score=score, relative_coefficient_score=score,
                          coefficient_energy=energy, activity_decision=decision)
            native.update(activity_statistic='ding_eq27_normalized_coefficient_energy',
                          activity_threshold=rule['threshold'], activity_comparator='>=',
                          activity_decision_available=True, public_numeric_control=rule,
                          threshold_status='FROZEN_RULE_REUSED_ACROSS_USER_COUNTS')
        else:
            native['validation_status'] = 'PENDING_VALIDATION'
        if not all(np.isfinite(value).all() for value in arrays.values()):
            raise FloatingPointError('Nonfinite selected baseline output')
        native.update(status='COMPLETE', method=METHOD_KEYS[method], algorithm_id=method,
            configuration=cfg, seconds=time.perf_counter()-started,
            inference_sha256=self.signature, source_sha256=inference_sources(method),
            dictionary=cfg['dictionary'], coefficient_coordinates='physical',
            truth_loaded=False, truth_used_in_inference=False, activity_count_or_truth_used=False,
            true_snr_or_activity_count_used=False)
        return arrays, native

    def run(self, input_path, output_path, *, observer=None):
        output = Path(output_path)
        if output.suffix != '.npz' or output.exists() or output.with_suffix('.json').exists():
            raise ValueError('Fresh .npz output required')
        arrays, native = self.infer(load_input(input_path), observer=observer)
        output.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(output, **arrays)
        native.update(input_sha256=sha256(input_path), output_sha256=sha256(output))
        write_json(output.with_suffix('.json'), native)
        return native
