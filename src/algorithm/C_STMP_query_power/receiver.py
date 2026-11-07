"""C-STMP with one common, observable noise condition for both networks."""
import time
import numpy as np
from system.observation import ReceiverInput
from system.receiver.noise_estimation import estimate_spatial_noise
from algorithm.C_STMP_retrained.receiver import Receiver as FrozenReceiver
from algorithm.STMP.denoiser import Denoiser
from .iterations import run_spatial_score


class Receiver(FrozenReceiver):
    def infer(self, inputs, *, observer=None):
        if not isinstance(inputs, ReceiverInput):
            raise TypeError('Public four-field input required')
        started=time.perf_counter();c=self.configuration
        if self.noise_mode=='estimated':
            noise,noise_record=estimate_spatial_noise(inputs.observation)
        else:
            noise=inputs.noise_variance;noise_record={'source':'supplied_noise_variance'}
        current=ReceiverInput(inputs.observation,inputs.operator,noise,inputs.activity_prior)
        self.model.reset()
        self.denoiser=Denoiser(self.model,self.evidence,activity_prior=inputs.activity_prior,
            conditional_variance_floor=c['conditional_variance_floor_checkpoint_normalized'],
            raw_site_residual_tolerance=self.controls.raw_site_residual_tolerance,
            activity_weight_residual_tolerance=self.controls.activity_weight_residual_tolerance,
            activity_stopping_reference=self.controls.activity_stopping_reference)
        self.last_trace=[]
        before=self.model.network_samples
        def observe(row,*args):
            self.last_trace.append(dict(row))
            if observer is not None:observer(row,*args)
        result=run_spatial_score(current,self.denoiser,scale=c['scale'],
            initial_variance=inputs.activity_prior*c['initialization']['normalized_training_second_moment'],
            config=self.controls,observer=observe,decision_threshold=c['decision_threshold'])
        arrays=dict(estimate=result.estimate,conditional_matrix=result.conditional_matrix,
            probabilities=result.probabilities,activity_decision=result.probabilities>=c['decision_threshold'],
            spatial_covariance=result.spatial_covariance,noise_variance_estimate=np.asarray(noise))
        record=self.context()
        record.update(status='COMPLETE',candidate='observable_query_power',
            query_variance_estimator='median over users of mean squared query magnitude',
            receiver_truth_used=False,noise_estimation=noise_record,
            iterations=len(result.trace),converged=result.stopping_reason=='CONVERGED',
            stopping_reason=result.stopping_reason,seconds=time.perf_counter()-started,
            first_network_samples=self.model.network_samples-before,
            limitations=['Assumes a majority of inactive users; a common scalar power does not model column correlations.'])
        return arrays,record
