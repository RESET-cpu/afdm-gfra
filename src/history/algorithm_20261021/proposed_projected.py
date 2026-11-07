"""Use observation-estimated AFDM structure in Proposed's Gaussian moments.

The local atom and its two derivatives define a rank-three AFDM subspace.
Both mean and covariance are conditioned in that working Gaussian model.
The frozen classifier still receives its original same-query score features.
This is a local approximation, not an exact posterior for estimated geometry.
Formulae and source terminology are recorded in THEORY.md and TERMINOLOGY.md.
"""
from copy import copy,deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import time

import numpy as np

from afdm_jadcedd.algorithm import phase_estimation
from afdm_jadcedd.algorithm.baselines.offgrid.atoms import path_atom
from afdm_jadcedd.algorithm.proposed.unknown_phase import UnknownPhaseReceiver
from afdm_jadcedd.algorithm.unknown_phase_model import UnknownPhaseInput
from afdm_jadcedd.project import ROOT
from afdm_jadcedd.system.config import DELTA_F_HZ
from afdm_jadcedd.system.observation import array_sha256
from afdm_jadcedd.utils import sha256

SCHEMA='afdm-proposed-estimated-phase-projected-v1'


class LocalProjection:
    def __init__(self,phase):
        bases=[]
        for delay,doppler in zip(phase['folded_delay_samples'],phase['doppler_hz']):
            atom,first,_=path_atom(float(delay),float(doppler)/DELTA_F_HZ,True)
            raw=np.stack((atom,*first)).reshape(3,-1).T
            basis,s,_=np.linalg.svd(raw,full_matrices=False)
            if s[-1]<=1e-10*s[0]:raise ValueError('Local physical basis is rank deficient')
            bases.append(basis)
        self.basis=np.asarray(bases)
        self.rank=3
        self.dimension=self.basis.shape[1]

    def __call__(self,mean):
        flat=np.asarray(mean).reshape(len(mean),mean.shape[1],-1)
        coefficients=np.einsum('kmd,kdr->kmr',flat,self.basis.conj(),optimize=False)
        return np.einsum('kmr,kdr->kmd',coefficients,self.basis,optimize=False).reshape(mean.shape)


class ProjectedMoments:
    def __init__(self,model,projection):
        self.model,self.projection=model,projection
        self.raw_mean=None

    def __getattr__(self,name):return getattr(self.model,name)

    def infer(self,r,v):
        original=self.model.infer(r,v)
        self.raw_mean=original.mean
        return replace(original,mean=self.projection(original.mean),
            variance=original.variance*self.projection.rank/self.projection.dimension)


class OriginalEvidence:
    def __init__(self,evidence,moments):self.evidence,self.moments=evidence,moments
    def __getattr__(self,name):return getattr(self.evidence,name)
    def infer(self,r,v,mean):return self.evidence.infer(r,v,self.moments.raw_mean)


class ProjectedPhaseReceiver(UnknownPhaseReceiver):
    def __init__(self,configuration,*,device='auto'):
        if configuration.get('schema')!=SCHEMA or configuration.get('local_basis')!=['atom','delay_derivative','doppler_derivative']:
            raise ValueError('Rank-three estimated-phase projection configuration required')
        binding=configuration['base_configuration'];path=ROOT/binding['path']
        if sha256(path)!=binding['sha256']:raise ValueError('Unknown-phase base configuration identity mismatch')
        super().__init__(json.loads(path.read_text()),device=device)
        parent_signature=self.signature
        self.configuration=deepcopy(configuration)
        self.signature=hashlib.sha256(json.dumps(dict(configuration=configuration,
            base_signature=parent_signature,source_sha256=sha256(Path(__file__)),
            atoms_sha256=sha256(ROOT/'src/afdm_jadcedd/algorithm/baselines/offgrid/atoms.py')),sort_keys=True).encode()).hexdigest()
        self.working=None

    def context(self):
        record=super().context()
        if self.working is not None:record.update(self.working.context())
        record.update(method='proposed_estimated_phase_projected',configuration=self.configuration,
            inference_sha256=self.signature,truth_used_in_inference=False,
            input_fields=list(UnknownPhaseInput.__dataclass_fields__),phase_estimation=self.phase_record)
        return record

    def infer(self,inputs,*,observer=None,phase_observer=None):
        if not isinstance(inputs,UnknownPhaseInput):raise TypeError('UnknownPhaseInput with original pilot required')
        self.phase_arrays=self.phase_record=self.working=None;started=time.monotonic()
        phase,phase_record=phase_estimation.estimate(inputs,self.controls,observer=phase_observer)
        self.phase_arrays,self.phase_record=phase,phase_record
        conditional=inputs.at_estimated_phase(phase['phase_slopes'])
        tick=time.monotonic()
        projection=LocalProjection(phase)
        moments=ProjectedMoments(self.base.model,projection)
        self.working=copy(self.base)
        self.working.model=moments
        self.working.evidence=OriginalEvidence(self.base.evidence,moments)
        arrays,record=self.working.infer(conditional,observer=observer)
        base_seconds=time.monotonic()-tick
        arrays.update(phase_slopes=phase['phase_slopes'],phase_doppler_hz=phase['doppler_hz'],
            phase_folded_delay_samples=phase['folded_delay_samples'],phase_path_gains=phase['path_gains'],
            phase_fitted_observation=phase['fitted_observation'])
        record.update(method='proposed_estimated_phase_projected',configuration=self.configuration,
            base_configuration=deepcopy(self.base.configuration),inference_sha256=self.signature,
            base_inference_sha256=self.base_signature,phase_inference_sha256=self.phase_signature,
            input_fields=list(UnknownPhaseInput.__dataclass_fields__),truth_used_in_inference=False,
            observation_sha256=array_sha256(inputs.observation),pilot_sha256=array_sha256(inputs.pilot),
            estimated_operator_sha256=array_sha256(conditional.operator),phase_estimation=phase_record,
            phase_seconds=phase_record['seconds'],base_seconds=base_seconds,
            seconds=base_seconds+phase_record['seconds'],wall_seconds=time.monotonic()-started,
            local_basis=dict(rank=projection.rank,ambient_dimension=projection.dimension,
                delay_samples=phase['folded_delay_samples'].tolist(),doppler_hz=phase['doppler_hz'].tolist()),
            covariance_definition='Working Gaussian conditioned on estimated local span; spatial-average variance factor 3/256 followed by original positive floor',
            classifier_features='Original unprojected same-query network mean',
            primary_metrics=['full_channel_nmse','aer'],activity_threshold_scope='Original probability threshold 0.5')
        return arrays,record
