"""Public receiver for the declared joint-channel L-DAMP adaptation."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import time
import numpy as np
import torch
from afdm_jadcedd.project import ROOT
from afdm_jadcedd.algorithm.baselines.ldamp.representation import Representation, beam_transform
from afdm_jadcedd.system.observation import ReceiverInput, load_input
from afdm_jadcedd.utils import sha256, write_json
from .core import solve_projected
from .denoiser import JointDenoiser, verify_bundle

SCHEMA = 'afdm-ldamp-joint-v1'
DEFAULT_CONFIG = ROOT / 'configs/ldamp_joint.json'


def load_configuration(path=None):
    return json.loads(Path(path or DEFAULT_CONFIG).read_text())


def signature(config):
    payload = {key: config[key] for key in ('schema', 'bundle_sha256', 'solver')}
    payload['daft_sha256'] = hashlib.sha256(Representation().a.tobytes()).hexdigest()
    paths = list(Path(__file__).parent.glob('*.py'))
    paths += [Path(__file__).parent.parent / 'ldamp' / name
              for name in ('matrix.py', 'network.py', 'beam.py', 'representation.py')]
    payload['sources'] = {str(path.relative_to(ROOT)): sha256(path) for path in paths}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def verify(config=None):
    config = config or load_configuration()
    if config['schema'] != SCHEMA:
        raise ValueError('Joint L-DAMP configuration required')
    solver = config['solver']
    if (not isinstance(solver['iterations'], int) or solver['iterations'] < 1
            or not isinstance(solver['row_probes'], int) or not 1 <= solver['row_probes'] <= 16
            or not isinstance(solver['measurement_batch'], int) or not 1 <= solver['measurement_batch'] <= 16
            or not isinstance(solver['seed'], int)):
        raise ValueError('Invalid solver budget')
    path = ROOT / config['bundle_path']
    if sha256(path) != config['bundle_sha256']:
        raise ValueError('Joint L-DAMP bundle identity mismatch')
    verify_bundle(path)
    return dict(status='PASS', validation_status=config['validation_status'],
                inference_sha256=signature(config), bundle_sha256=config['bundle_sha256'])


class LDAMPJointReceiver:
    def __init__(self, configuration, *, device='auto'):
        self.configuration = config = deepcopy(configuration)
        verified = verify(config)
        self.signature = verified['inference_sha256']
        self.device = ('mps' if torch.backends.mps.is_available() else 'cpu') if device == 'auto' else device
        self.denoise = JointDenoiser(ROOT / config['bundle_path'], device=self.device)
        self.readout = None
        if config.get('readout'):
            binding = config['readout']
            path = ROOT / binding['path']
            if sha256(path) != binding['sha256']:
                raise ValueError('Joint L-DAMP readout identity mismatch')
            readout = json.loads(path.read_text())
            if (readout['inference_sha256'] != self.signature
                    or not np.isfinite(readout['threshold']) or readout['threshold'] < 0):
                raise ValueError('Joint L-DAMP readout belongs to different inference settings')
            self.readout = readout

    def infer(self, inputs, *, observer=None):
        if (not isinstance(inputs, ReceiverInput) or inputs.observation.shape != (16, 16, 16)
                or inputs.operator.shape[0] != 16 or inputs.operator.shape[2] != 16):
            raise ValueError('Q16 AFDM 16x16 input required')
        if np.linalg.norm(inputs.operator) == 0:
            raise ValueError('Nonzero measurement operator required')
        started = time.monotonic()
        self.denoise.log = []
        # The observer receives physical channels detached from the recurrence.
        callback = None
        if observer is not None:
            def callback(row, value, query, covariance):
                observer(row, self.denoise.scale * beam_transform(value, inverse=True))
        result = solve_projected(inputs, self.denoise, **self.configuration['solver'], observer=callback)
        estimate = result.pop('estimate')
        energy = result.pop('energy')
        arrays = dict(estimate=estimate, channel_energy=energy, activity_score=energy.copy())
        if self.readout is not None:
            arrays['activity_decision'] = (energy >= self.readout['threshold']) & (energy > 0)
        record = dict(**result, method='ldamp', status='COMPLETE',
                      configuration=deepcopy(self.configuration), inference_sha256=self.signature,
                      device=self.device, validation_status=self.configuration['validation_status'],
                      input_fields=list(ReceiverInput.__dataclass_fields__),
                      activity_prior_used=False, training_activity_probability=.1,
                      public_activity_prior=float(inputs.activity_prior),
                      activity_statistic='channel_frobenius_energy',
                      activity_decision_available=self.readout is not None,
                      denoiser_calls=len(self.denoise.log), selected_intervals=deepcopy(self.denoise.log),
                      outside_noise_support_calls=sum(row['outside_training_mean_range'] for row in self.denoise.log),
                      directional_derivative_evaluations=2 * inputs.observation.shape[0]
                          * self.configuration['solver']['row_probes'] * result['iterations'],
                      effective_covariance_used_by_denoiser='Mean diagonal within each beam; correlated-error mismatch remains empirical')
        record['seconds'] = time.monotonic() - started
        return arrays, record

    def run(self, input_path, output_path, *, observer=None):
        out = Path(output_path)
        if out.suffix != '.npz' or out.exists() or out.with_suffix('.json').exists():
            raise ValueError('Fresh .npz output required')
        arrays, record = self.infer(load_input(input_path), observer=observer)
        out.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(out, **arrays)
        record.update(input_sha256=sha256(input_path), output_sha256=sha256(out))
        write_json(out.with_suffix('.json'), record)
        return record
