"""Public input-only frozen score replacement for the retained L-DAMP baseline."""
from dataclasses import replace
from pathlib import Path
import hashlib,json,time
import numpy as np
import torch
from afdm_jadcedd.project import ROOT
from afdm_jadcedd.system.observation import load_input
from afdm_jadcedd.algorithm.baselines.ldamp.representation import beam_transform
from afdm_jadcedd.algorithm.baselines.ldamp.receiver import verify as verify_baseline
from afdm_jadcedd.utils import sha256,write_json
from .core import solve,Controls
from .denoiser import ScoreDenoiser

def load_configuration(path=None):
    return json.loads(Path(path or ROOT/'configs/ldamp_score.json').read_text())

class LDAMPScoreReceiver:
    def __init__(self,configuration=None,*,device='auto'):
        self.configuration=c=configuration or load_configuration()
        original=json.loads((ROOT/c['baseline_config']).read_text())
        if sha256(ROOT/c['baseline_config'])!=c['baseline_config_sha256']:
            raise ValueError('Baseline config changed')
        if verify_baseline(original)['inference_sha256']!=c['baseline_inference_sha256']:
            raise ValueError('Baseline identity changed')
        if c['solver']!=original['solver'] or c['networks']['scale']!=original['scale']:
            raise ValueError('Same frozen baseline controls and scale required')
        self.device=('mps' if torch.backends.mps.is_available() else 'cpu') if device=='auto' else device
        sources=[*Path(__file__).parent.glob('*.py'),ROOT/'src/afdm_jadcedd/algorithm/score_amp/denoiser.py',
                 ROOT/'src/afdm_jadcedd/algorithm/proposed/network.py',ROOT/'src/afdm_jadcedd/algorithm/proposed/activity.py']
        self.sources={str(p.relative_to(ROOT)):sha256(p) for p in sources}
        self.signature=hashlib.sha256(json.dumps(dict(configuration=c,sources=self.sources),sort_keys=True).encode()).hexdigest()

    def infer(self,inputs,*,observer=None):
        c=self.configuration;start=time.monotonic()
        denoiser=ScoreDenoiser(c['networks'],activity_prior=inputs.activity_prior,device=self.device,batch_size=c['batch_size'])
        result=solve(replace(inputs,observation=beam_transform(inputs.observation)),denoiser,
            scale=denoiser.scale,controls=Controls(**c['solver']),observer=observer)
        estimate=beam_transform(result.pop('estimate'),inverse=True);energy=np.sum(abs(estimate)**2,axis=(1,2,3))
        probability=result.pop('last_valid_probabilities')
        key='estimate' if result['status']=='COMPLETE' else 'last_valid_estimate'
        arrays={key:estimate,'channel_energy':energy}
        if probability is not None:
            arrays.update(last_probabilities=probability,
                activity_decision_probability_diagnostic=probability>=.5,
                activity_decision_transferred_energy_diagnostic=energy>=c['unrecalibrated_energy_threshold'])
        record=dict(method='ldamp_score',**result,seconds=time.monotonic()-start,configuration=c,
            inference_sha256=self.signature,sources=self.sources,device=self.device,truth_used_in_inference=False,
            denoiser_calls=denoiser.calls,directional_derivative_evaluations=denoiser.direction_evaluations,
            probability_iteration=result['iterations'] if probability is not None else None,
            scalar_noise_interface='trace covariance / feature count; fixed during differentiation',
            activity_readout_status='Diagnostic only; neither score probabilities nor transferred energy threshold are calibrated on this recurrence')
        return arrays,record

    def run(self,input_path,output_path,*,observer=None):
        path=Path(output_path)
        if path.suffix!='.npz' or path.exists() or path.with_suffix('.json').exists():raise ValueError('Fresh .npz output required')
        arrays,record=self.infer(load_input(input_path),observer=observer);path.parent.mkdir(parents=True,exist_ok=True)
        np.savez_compressed(path,**arrays)
        record.update(input_sha256=sha256(input_path),output_sha256=sha256(path))
        write_json(path.with_suffix('.json'),record);return record
