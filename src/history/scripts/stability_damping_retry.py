"""Try fixed damping values in order, using convergence alone for selection.

Each attempt resets the native receiver state and uses unchanged networks.
There is no truth argument. Failed attempts and their complete cost are retained.
"""
from copy import deepcopy
from pathlib import Path
import time
import numpy as np
from afdm_jadcedd.algorithm.proposed_noise_candidate import EstimatedNoiseProposedReceiver as NativeReceiver
from afdm_jadcedd.algorithm.proposed.records import SpatialConfig


class RetryReceiver(NativeReceiver):
    order=(.1,.05)
    last_instance=None
    audit_root=None

    def __init__(self,configuration,*,device='auto'):
        super().__init__(configuration,device=device)
        self.initial_configuration=deepcopy(configuration)
        self.attempts=[]
        type(self).last_instance=self

    def infer(self,inputs,*,observer=None):
        started=time.monotonic();self.attempts=[];offset=0
        for number,damping in enumerate(self.order):
            config=deepcopy(self.initial_configuration);config['ep']['damping']=damping
            self.base.configuration=config;self.configuration=config
            self.base.controls=SpatialConfig(**config['ep'])
            def observe(row,*args):
                if observer is not None:
                    observer(dict(row,iteration=offset+row['iteration'],
                        attempt_iteration=row['iteration'],attempt=number,damping=damping),*args)
            prediction,record=super().infer(inputs,observer=observe)
            self.attempts.append((prediction,record))
            offset+=record['iterations']
            if record['converged']:
                break
        final=deepcopy(record)
        final['trace']=[];offset=0
        for number,(_,native) in enumerate(self.attempts):
            for row in native['trace']:
                final['trace'].append(dict(row,iteration=offset+row['iteration'],
                    attempt_iteration=row['iteration'],attempt=number,damping=self.order[number]))
            offset+=native['iterations']
        for key in ('first_score_samples','second_score_samples','first_score_calls','second_score_calls',
                    'classifier_calls','classifier_samples','classifier_seconds','activity_evidence_calls',
                    'activity_evidence_samples','activity_evidence_seconds','conditional_variance_floor_iterations',
                    'supported_query_iterations','unsupported_user_queries','rejected_user_queries',
                    'raw_nonpositive_variance_user_queries','accepted_site_iterations','reused_site_iterations',
                    'noise_seconds','base_seconds'):
            if key in final:final[key]=sum(native[key] for _,native in self.attempts)
        final.update(iterations=offset,seconds=time.monotonic()-started,
            final_attempt_iterations=record['iterations'],attempt_count=len(self.attempts),
            retry_policy=dict(damping_order=list(self.order),iterations_per_attempt=config['ep']['iterations'],
                maximum_total_iterations=len(self.order)*config['ep']['iterations'],
                selection='First attempt satisfying the unchanged native stopping criteria; no truth or performance score is used',
                attempts=[dict(damping=self.order[i],iterations=r['iterations'],converged=r['converged'],seconds=r['seconds'])
                    for i,(_,r) in enumerate(self.attempts)]))
        self.base.configuration=deepcopy(self.initial_configuration)
        self.configuration=self.base.configuration
        self.base.controls=SpatialConfig(**self.configuration['ep'])
        if self.audit_root is not None and any(not r['converged'] for _,r in self.attempts):
            from _support.storage import save,save_arrays
            from afdm_jadcedd.system.observation import array_sha256
            root=Path(self.audit_root)/array_sha256(inputs.observation)
            for i,(arrays,native) in enumerate(self.attempts):
                save(root/f'attempt{i}.json',native)
                save_arrays(root/f'attempt{i}.npz',arrays)
            final['retained_attempts']=str(root)
        return prediction,final
