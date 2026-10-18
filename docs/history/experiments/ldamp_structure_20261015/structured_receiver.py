"""Optional L-DAMP output TSVD with a separately calibrated activity readout.

The unchanged frozen DnCNN/AMP receiver runs first. TSVD is applied once to
its complete estimated channel, without truth, known activity or true angles.
This is an output refinement, not a newly trained network or changed recurrence.
"""
from copy import deepcopy
import hashlib,json,time
from pathlib import Path
import numpy as np
from afdm_jadcedd.algorithm.baselines.ldamp.receiver import LDAMPReceiver,signature as base_signature
from afdm_jadcedd.project import ROOT
from afdm_jadcedd.utils import sha256
from structure import rank_one

SCHEMA='afdm-ldamp-output-tsvd-v1'


def signature(config):
    if config['schema']!=SCHEMA or config['rank']!=1:raise ValueError('Rank-one output TSVD required')
    identity=base_signature(config['base_configuration'])
    if identity!=config['base_inference_sha256']:raise ValueError('Base inference identity mismatch')
    payload=dict(schema=SCHEMA,rank=1,base_inference_sha256=identity,
        activity_statistic='projected_channel_frobenius_energy',
        sources={p.name:sha256(p) for p in [Path(__file__),Path(__file__).with_name('structure.py')]})
    return hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()


class Receiver:
    def __init__(self,configuration,device='mps'):
        self.configuration=deepcopy(configuration);self.signature=signature(configuration)
        self.base=LDAMPReceiver(configuration['base_configuration'],device=device);self.readout=None
        if configuration.get('readout'):
            binding=configuration['readout'];path=ROOT/binding['path']
            if sha256(path)!=binding['sha256']:raise ValueError('Readout hash mismatch')
            self.readout=json.loads(path.read_text())
            if self.readout['inference_sha256']!=self.signature:raise ValueError('Readout inference mismatch')
            if not np.isfinite(self.readout['threshold']) or self.readout['threshold']<0:raise ValueError('Invalid threshold')

    def postprocess(self,base_arrays,base_record):
        started=time.monotonic()
        estimate=rank_one(base_arrays['estimate'])
        energy=np.sum(abs(estimate)**2,axis=(1,2,3))
        arrays=dict(estimate=estimate,channel_energy=energy,activity_score=energy.copy())
        if self.readout is not None:
            arrays['activity_decision']=(energy>=self.readout['threshold']) & (energy>0)
        elapsed=time.monotonic()-started
        record=dict(status='COMPLETE',method='ldamp_output_tsvd',inference_sha256=self.signature,
            base_inference_sha256=self.base.signature,seconds=base_record['seconds']+elapsed,
            base_seconds=base_record['seconds'],postprocessing_seconds=elapsed,
            activity_statistic='projected_channel_frobenius_energy',truth_used_in_inference=False,
            recurrence_modified=False,rank=1,configuration=self.configuration,
            outside_noise_support_calls=base_record.get('outside_noise_support_calls'))
        return arrays,record

    def infer_pair(self,inputs):
        base_arrays,base_record=self.base.infer(inputs)
        arrays,record=self.postprocess(base_arrays,base_record)
        return arrays,record,base_arrays,base_record

    def infer(self,inputs):
        arrays,record,_,_=self.infer_pair(inputs)
        return arrays,record
