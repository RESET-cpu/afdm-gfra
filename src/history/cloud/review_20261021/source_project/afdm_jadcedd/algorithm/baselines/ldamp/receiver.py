"""Public L-DAMP receiver and checkpoint-bound activity readout."""
from copy import deepcopy
from dataclasses import asdict,replace
import hashlib
import json
from pathlib import Path
import time
import numpy as np
import torch
from afdm_jadcedd.project import ROOT
from afdm_jadcedd.system.observation import ReceiverInput, load_input
from afdm_jadcedd.utils import sha256, write_json
from .core import Controls, solve
from .network import DnCNN, FrozenDenoiser, FrozenDenoiserBank
from .beam import BeamDenoiser
from .matrix import Controls as MatrixControls,solve as matrix_solve
from .representation import Representation,beam_transform

DEFAULT_CONFIG = ROOT/'configs/ldamp.json'


def load_configuration(path=None):
    return json.loads(Path(path or DEFAULT_CONFIG).read_text())


def signature(config):
    if config.get('schema')=='afdm-ldamp-beam-v2':
        payload={k:config[k] for k in ('schema','scale','solver','bank_sha256','batch_size')}
        payload['daft_sha256']=hashlib.sha256(Representation().a.tobytes()).hexdigest()
    else:
        payload = {k: config[k] for k in ('network', 'scale', 'solver', 'checkpoint_sha256', 'noise_boundaries')}
    paths=[Path(__file__).with_name(name) for name in ('receiver.py','network.py','beam.py','matrix.py','representation.py')] if config.get('schema')=='afdm-ldamp-beam-v2' else Path(__file__).parent.glob('*.py')
    payload['sources'] = {p.name: sha256(p) for p in paths}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def verify(config=None):
    c = config or load_configuration()
    if c.get('schema')=='afdm-ldamp-beam-v2':
        path=ROOT/c['bank_path']
        if not path.is_file() or sha256(path)!=c['bank_sha256']:raise ValueError('L-DAMP bank identity mismatch')
        bank=json.loads(path.read_text());edges=np.asarray(bank['edges'],float)
        if (not bank['complete'] or bank['scale']!=c['scale'] or bank['representation']!='beam_time_lag_dft'
                or not np.isfinite(edges).all() or np.any(np.diff(edges)<=0)
                or [e['index'] for e in bank['entries']]!=list(range(len(edges)-1))):
            raise ValueError('Invalid L-DAMP representation or noise intervals')
        for entry in bank['entries']:
            checkpoint=path.parent/entry['path']
            if not checkpoint.is_file() or sha256(checkpoint)!=entry['sha256']:
                raise ValueError('L-DAMP interval checkpoint identity mismatch')
        return dict(status='PASS',validation_status=c['validation_status'],inference_sha256=signature(c),bank_sha256=c['bank_sha256'])
    if not c.get('checkpoint_sha256'):
        return dict(status='PENDING_TRAINING', validation_status='NOT_READY_FOR_COMPARISON')
    path = ROOT/c['checkpoint_path']
    if not path.is_file() or sha256(path) != c['checkpoint_sha256']:
        raise ValueError('L-DAMP checkpoint identity mismatch')
    return dict(status='PASS', validation_status=c['validation_status'],
                inference_sha256=signature(c), checkpoint_sha256=c['checkpoint_sha256'])


class LDAMPReceiver:
    def __init__(self, configuration, *, device='auto'):
        self.configuration = c = deepcopy(configuration)
        if verify(c)['status'] != 'PASS':
            raise ValueError('L-DAMP requires trained weights; run scripts/train_ldamp.py first')
        self.device = ('mps' if torch.backends.mps.is_available() else 'cpu') if device == 'auto' else device
        self._beam=c.get('schema')=='afdm-ldamp-beam-v2'
        if self._beam:
            self.denoise=BeamDenoiser((ROOT/c['bank_path']).parent,device=self.device,batch_size=c['batch_size'])
        else:
            checkpoint = torch.load(ROOT/c['checkpoint_path'], map_location='cpu', weights_only=True)
            if checkpoint['network'] != c['network'] or checkpoint['scale'] != c['scale']:
                raise ValueError('L-DAMP training/inference representation mismatch')
            if checkpoint.get('noise_boundaries') != c['noise_boundaries']:
                raise ValueError('L-DAMP noise interval mismatch')
            self.denoise = FrozenDenoiserBank(checkpoint, device=self.device, batch_size=c['batch_size'])
        self.signature = signature(c)
        self.readout = None
        if c.get('readout'):
            binding = c['readout']
            if sha256(ROOT/binding['path']) != binding['sha256']:
                raise ValueError('L-DAMP activity readout hash mismatch')
            self.readout = json.loads((ROOT/binding['path']).read_text())
            if self.readout['inference_sha256'] != self.signature:
                raise ValueError('L-DAMP readout belongs to different inference settings')

    def infer(self, inputs, *, observer=None):
        c = self.configuration
        antennas=16 if self._beam else c['network']['antennas']
        if (not isinstance(inputs, ReceiverInput) or inputs.observation.shape[1:] != (antennas,16)
                or inputs.operator.shape[-1] != 16):
            raise ValueError('Public AFDM 16x16 channel input required')
        start=time.monotonic()
        if self._beam:
            self.denoise.selection_log=[]
            beam_observer=None if observer is None else lambda row,h:observer(row,beam_transform(h,inverse=True))
            result=matrix_solve(replace(inputs,observation=beam_transform(inputs.observation)),self.denoise,
                scale=c['scale'],controls=MatrixControls(**c['solver']),observer=beam_observer)
            result['estimate']=beam_transform(result['estimate'],inverse=True)
            calls=len(self.denoise.selection_log)
            outside=sum(any(v<self.denoise.manifest['edges'][0] or v>self.denoise.manifest['edges'][-1]
                            for v in call['variances']) for call in self.denoise.selection_log)
        else:
            before=self.denoise.calls;unsupported_before=self.denoise.outside_support_calls
            result = solve(inputs, self.denoise, scale=c['scale'], controls=Controls(**c['solver']), observer=observer)
            calls=self.denoise.calls-before;outside=self.denoise.outside_support_calls-unsupported_before
        energy = np.sum(abs(result['estimate'])**2, axis=(1,2,3))
        # The physical population scale is fixed across scenes. For v2, use
        # absolute channel energy: dividing by a weak scene's largest estimate
        # can move the entire inactive-user floor above a relative threshold.
        score = energy.copy() if self._beam else energy/max(float(energy.max()), 1e-30)
        arrays = dict(estimate=result.pop('estimate'), activity_score=score, channel_energy=energy)
        if self.readout is not None:
            arrays['activity_decision'] = (score >= self.readout['threshold']) & (energy > 0)
        record = dict(status='COMPLETE', method='ldamp', **result,
                      seconds=time.monotonic()-start, denoiser_calls=calls,
                      outside_noise_support_calls=outside,
                      activity_decision_available=self.readout is not None,
                      validation_status=c['validation_status'], inference_sha256=self.signature,
                      configuration=c, truth_used_in_inference=False,
                      input_fields=list(ReceiverInput.__dataclass_fields__), device=self.device)
        if self._beam:
            record.update(selected_intervals=self.denoise.selection_log,
                activity_statistic='channel_frobenius_energy',
                directional_derivative_evaluations=2*c['solver']['probes']*result['iterations'],
                derivative='Exact frozen-network real directions; Monte Carlo partial Wirtinger trace',
                effective_covariance_used_by_denoiser='Mean diagonal within each beam; correlated-error mismatch remains an empirical limitation')
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
