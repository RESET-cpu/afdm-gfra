"""Independent public entry for optimized phase and optional estimated noise.

The conditional receiver, three networks and activity rule remain unchanged.
The original public entry is preserved until paired qualification is accepted.
"""
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import time
import warnings
import numpy as np

from afdm_jadcedd.algorithm import phase_estimation_optimized as phase
from afdm_jadcedd.algorithm.baselines.noise_estimation import estimate_spatial_noise
from afdm_jadcedd.algorithm.proposed.configuration import load_configuration
from afdm_jadcedd.algorithm.proposed.receiver import Receiver
from afdm_jadcedd.algorithm.proposed_noise_candidate import EstimatedNoiseProposedReceiver
from afdm_jadcedd.algorithm.unknown_phase_model import UnknownPhaseInput,load_input
from afdm_jadcedd.project import ROOT
from afdm_jadcedd.system.observation import array_sha256
from afdm_jadcedd.utils import sha256,write_json

SCHEMA='afdm-proposed-estimated-phase-v2'

class FrontendReceiver:
    def __init__(self,configuration,*,device='auto'):
        if configuration.get('schema')!=SCHEMA:
            raise ValueError('Optimized phase receiver configuration required')
        self.configuration=deepcopy(configuration)
        self.noise_mode=configuration['noise_mode']
        if self.noise_mode not in ('known','estimated'):
            raise ValueError('Select known or estimated noise')
        binding=configuration['base_configuration'];path=ROOT/binding['path']
        if sha256(path)!=binding['sha256']:
            raise ValueError('Conditional configuration identity mismatch')
        self.controls=phase.Controls(**configuration['phase_estimation'])
        self.phase_signature=phase.signature(self.controls)
        factory=EstimatedNoiseProposedReceiver if self.noise_mode=='estimated' else Receiver
        self.base=factory(load_configuration(path),device=device)
        self.device=self.base.device
        sources=[Path(__file__),ROOT/'src/afdm_jadcedd/algorithm/proposed_noise_candidate.py',
                 ROOT/'src/afdm_jadcedd/algorithm/baselines/noise_estimation.py']
        sources+=list((ROOT/'src/afdm_jadcedd/algorithm/proposed').rglob('*.py'))
        self.signature=hashlib.sha256(json.dumps(dict(configuration=configuration,
            phase=self.phase_signature,sources={str(p.relative_to(ROOT)):sha256(p) for p in sources}),
            sort_keys=True).encode()).hexdigest()

    def infer(self,inputs,*,observer=None,phase_observer=None):
        if not isinstance(inputs,UnknownPhaseInput):
            raise TypeError('UnknownPhaseInput with the original pilot required')
        started=time.perf_counter()
        if self.noise_mode=='estimated':
            # This value only normalizes the phase fit diagnostic; phase estimates
            # do not depend on noise variance. The conditional wrapper re-estimates
            # from Y, enforcing its own observation-only information boundary.
            variance,_=estimate_spatial_noise(inputs.observation)
            inputs=replace(inputs,noise_variance=variance)
        values,phase_record=phase.estimate(inputs,self.controls,observer=phase_observer)
        conditional=inputs.at_estimated_phase(values['phase_slopes'])
        native,record=self.base.infer(conditional,observer=observer)
        arrays=dict(native,phase_slopes=values['phase_slopes'],phase_doppler_hz=values['doppler_hz'],
            phase_folded_delay_samples=values['folded_delay_samples'],phase_path_gains=values['path_gains'],
            phase_fitted_observation=values['fitted_observation'])
        if not all(np.isfinite(v).all() for v in arrays.values()):
            raise FloatingPointError('Nonfinite Proposed frontend output')
        phase_record=dict(phase_record,residual_normalization_noise_variance=inputs.noise_variance,
                          noise_mode=self.noise_mode)
        record=dict(record,method='proposed_estimated_phase',configuration=self.configuration,
            phase_mode='estimated',noise_mode=self.noise_mode,inference_sha256=self.signature,
            phase_inference_sha256=self.phase_signature,phase_estimation=phase_record,
            phase_seconds=phase_record['seconds'],conditional_seconds=record['seconds'],
            seconds=time.perf_counter()-started,truth_used_in_inference=False,
            input_fields=(['observation','pilot','activity_prior'] if self.noise_mode=='estimated'
                          else list(UnknownPhaseInput.__dataclass_fields__)),
            observation_sha256=array_sha256(inputs.observation),pilot_sha256=array_sha256(inputs.pilot),
            estimated_operator_sha256=array_sha256(conditional.operator))
        return arrays,record

    def run(self,input_path,output_path,*,observer=None):
        output=Path(output_path)
        paths=[output,output.with_suffix('.json'),output.with_suffix('.warnings.json')]
        if output.suffix!='.npz' or any(p.exists() for p in paths):
            raise ValueError('Fresh native .npz output required')
        output.parent.mkdir(parents=True,exist_ok=True);caught=[]
        try:
            if self.noise_mode=='known':inputs=load_input(input_path)
            else:
                # Legacy variance values are never read, even if present.
                with np.load(input_path,allow_pickle=False) as saved:
                    required={'observation','pilot','activity_prior'}
                    if not required<=set(saved.files) or set(saved.files)-required-{'noise_variance'}:
                        raise ValueError('Expected observation, pilot and activity_prior')
                    inputs=UnknownPhaseInput(saved['observation'],saved['pilot'],1.,float(saved['activity_prior']))
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always',RuntimeWarning)
                arrays,record=self.infer(inputs,observer=observer)
            np.savez_compressed(output,**arrays)
            record.update(input_sha256=sha256(input_path),output_sha256=sha256(output))
            write_json(output.with_suffix('.json'),record)
            return record
        except BaseException as error:
            write_json(output.with_suffix('.json'),dict(status='FAILED',error=repr(error),
                method='proposed_estimated_phase',noise_mode=self.noise_mode,inference_sha256=self.signature))
            raise
        finally:
            write_json(output.with_suffix('.warnings.json'),[dict(category=w.category.__name__,message=str(w.message),
                filename=w.filename,lineno=w.lineno) for w in caught])
