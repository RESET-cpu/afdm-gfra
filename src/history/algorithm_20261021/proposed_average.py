"""Average independent Proposed runs under four equivalent global phases.

The unknown cross-frame phase is estimated once from public observations.
Each branch then runs the unchanged conditional receiver on gY, with the same
estimated operator, weights, initialization and stopping rules. Rotated-back
outputs are combined by the law of total covariance; branches are not treated
as independent evidence. These remain approximate posterior distributions.

The group-averaging terminology and its scope are recorded in TERMINOLOGY.md.
"""
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import time
import warnings

import numpy as np

from afdm_jadcedd.algorithm import phase_estimation
from afdm_jadcedd.algorithm.proposed.unknown_phase import UnknownPhaseReceiver
from afdm_jadcedd.algorithm.unknown_phase_model import UnknownPhaseInput, load_input
from afdm_jadcedd.project import ROOT
from afdm_jadcedd.system.observation import array_sha256
from afdm_jadcedd.utils import sha256, write_json

SCHEMA = 'afdm-proposed-estimated-phase-average-v1'
PHASES = (1+0j, 1j, -1+0j, -1j)


def combine_predictions(predictions):
    """Mixture moments after bringing each branch back to the input frame."""
    if len(predictions) != len(PHASES):
        raise ValueError('Exactly four complete receiver outputs required')
    probabilities = np.stack([p['probabilities'] for p in predictions])
    means = np.stack([g.conjugate()*p['estimate'] for g,p in zip(PHASES,predictions)])
    conditional = np.stack([g.conjugate()*p['conditional_matrix'] for g,p in zip(PHASES,predictions)])
    pbar = probabilities.mean(axis=0)
    mean = means.mean(axis=0)
    weights = np.divide(probabilities, probabilities.sum(axis=0)[None],
        out=np.full_like(probabilities, .25), where=probabilities.sum(axis=0)[None]>0)
    conditional_mean = np.sum(weights[:,:,None,None,None]*conditional, axis=0)
    difference = means - mean[None]
    covariance = np.mean([p['spatial_covariance'] for p in predictions], axis=0)
    covariance += np.einsum('gkmnp,gklnp->kml', difference, difference.conj(), optimize=False) / (4*mean.shape[2]*mean.shape[3])
    return dict(estimate=mean, conditional_matrix=conditional_mean, probabilities=pbar,
                activity_decision=pbar>=.5, spatial_covariance=covariance)


class AveragedPhaseReceiver:
    def __init__(self, configuration, *, device='auto'):
        self.configuration = deepcopy(configuration)
        if configuration.get('schema') != SCHEMA:
            raise ValueError('Estimated-phase receiver averaging configuration required')
        if configuration.get('rotation_degrees') != [0,90,180,270]:
            raise ValueError('The four declared global rotations are required')
        binding=configuration['base_configuration']; path=ROOT/binding['path']
        if sha256(path)!=binding['sha256']:
            raise ValueError('Unknown-phase base configuration identity mismatch')
        self.base=UnknownPhaseReceiver(json.loads(path.read_text()),device=device)
        self.device=self.base.device
        self.signature=hashlib.sha256(json.dumps(dict(configuration=configuration,
            base_signature=self.base.signature,source_sha256=sha256(Path(__file__))),sort_keys=True).encode()).hexdigest()
        self.phase_arrays=self.phase_record=None
        self.branch_records=[]

    def context(self):
        return dict(method='proposed_estimated_phase_average',configuration=self.configuration,
            inference_sha256=self.signature,base_inference_sha256=self.base.signature,
            input_fields=list(UnknownPhaseInput.__dataclass_fields__),truth_used_in_inference=False,
            branch_records=deepcopy(self.branch_records),phase_estimation=self.phase_record)

    def infer(self, inputs, *, observer=None, phase_observer=None):
        if not isinstance(inputs,UnknownPhaseInput):
            raise TypeError('UnknownPhaseInput with original pilot required')
        self.phase_arrays=self.phase_record=None;self.branch_records=[]
        started=time.monotonic()
        phase,phase_record=phase_estimation.estimate(inputs,self.base.controls,observer=phase_observer)
        self.phase_arrays,self.phase_record=phase,phase_record
        conditional=inputs.at_estimated_phase(phase['phase_slopes'])
        predictions=[]
        for branch,g in enumerate(PHASES):
            def observe(row,*state):
                if observer is not None:
                    observer(dict(row,rotation_branch=branch),*state)
            output,record=self.base.base.infer(replace(conditional,observation=g*conditional.observation),observer=observe)
            predictions.append(output)
            self.branch_records.append(dict(record,rotation_branch=branch,rotation_degrees=90*branch))
        arrays=combine_predictions(predictions)
        arrays.update(phase_slopes=phase['phase_slopes'],phase_doppler_hz=phase['doppler_hz'],
            phase_folded_delay_samples=phase['folded_delay_samples'],phase_path_gains=phase['path_gains'],
            phase_fitted_observation=phase['fitted_observation'])
        record=self.context()
        sums=('iterations','first_score_samples','second_score_samples','first_score_calls','second_score_calls',
            'classifier_calls','classifier_samples','classifier_seconds','activity_evidence_calls',
            'activity_evidence_samples','activity_evidence_seconds','conditional_variance_floor_iterations',
            'supported_query_iterations','unsupported_user_queries','rejected_user_queries',
            'raw_nonpositive_variance_user_queries','accepted_site_iterations','reused_site_iterations')
        record.update({key:sum(r[key] for r in self.branch_records) for key in sums})
        converged=all(r['stopping_reason']=='CONVERGED' for r in self.branch_records)
        base_seconds=sum(r['seconds'] for r in self.branch_records)
        record.update(status='COMPLETE',converged=converged,
            stopping_reason='CONVERGED' if converged else 'MAX_ITERATIONS',
            branch_iterations=[r['iterations'] for r in self.branch_records],
            branch_stopping_reasons=[r['stopping_reason'] for r in self.branch_records],
            phase_seconds=phase_record['seconds'],base_seconds=base_seconds,
            seconds=base_seconds+phase_record['seconds'],wall_seconds=time.monotonic()-started,
            scale=self.base.base.configuration['scale'],activity_evidence='classifier',classifier_loaded=True,
            checkpoint_sha256=self.base.base.checkpoints,
            observation_sha256=array_sha256(inputs.observation),pilot_sha256=array_sha256(inputs.pilot),
            estimated_operator_sha256=array_sha256(conditional.operator),
            primary_metrics=['full_channel_nmse','aer'],decision_threshold=.5,
            probability_combination='Arithmetic mean of four dependent branch probabilities',
            covariance_definition='Covariance of the mixture of approximate branch distributions',
            trace=[dict(row,rotation_branch=i) for i,r in enumerate(self.branch_records) for row in r['trace']])
        return arrays,record

    def run(self,input_path,output_path,*,observer=None,phase_observer=None):
        output=Path(output_path)
        paths=(output,output.with_suffix('.json'),output.with_suffix('.warnings.json'))
        if output.suffix!='.npz' or any(p.exists() for p in paths):
            raise ValueError('Fresh native .npz output required; existing attempts are preserved')
        output.parent.mkdir(parents=True,exist_ok=True);caught=[]
        self.branch_records=[];self.phase_arrays=self.phase_record=None
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always',RuntimeWarning)
                arrays,record=self.infer(load_input(input_path),observer=observer,phase_observer=phase_observer)
                if not all(np.isfinite(a).all() for a in arrays.values()):
                    raise FloatingPointError('Nonfinite averaged receiver output')
            np.savez_compressed(output,**arrays)
            record.update(input_sha256=sha256(input_path),output_sha256=sha256(output))
            write_json(output.with_suffix('.json'),record)
            return record
        except BaseException as error:
            record=self.context();record.update(status='FAILED',error=repr(error))
            write_json(output.with_suffix('.json'),record)
            raise
        finally:
            write_json(output.with_suffix('.warnings.json'),[
                dict(category=w.category.__name__,message=str(w.message),filename=w.filename,lineno=w.lineno)
                for w in caught])
