"""Keep the frozen first network and classifier; adapt only scalar query power."""
import time
import numpy as np
import torch
from system.observation import ReceiverInput
from system.receiver.noise_estimation import estimate_spatial_noise
from algorithm.C_STMP_retrained.receiver import Receiver as FrozenReceiver
from algorithm.STMP.denoiser import Denoiser
from .iterations import run_spatial_score


class Receiver(FrozenReceiver):
    def infer(self, inputs, *, observer=None):
        if not isinstance(inputs, ReceiverInput):
            raise TypeError('Public four-field input required')
        started = time.perf_counter()
        c = self.configuration
        if self.noise_mode == 'estimated':
            noise, noise_record = estimate_spatial_noise(inputs.observation)
        else:
            noise, noise_record = inputs.noise_variance, {'source':'supplied_noise_variance'}
        current = ReceiverInput(inputs.observation, inputs.operator, noise, inputs.activity_prior)
        self.model.reset()
        self.denoiser = Denoiser(self.model, self.evidence, activity_prior=inputs.activity_prior,
            conditional_variance_floor=c['conditional_variance_floor_checkpoint_normalized'],
            raw_site_residual_tolerance=self.controls.raw_site_residual_tolerance,
            activity_weight_residual_tolerance=self.controls.activity_weight_residual_tolerance,
            activity_stopping_reference=self.controls.activity_stopping_reference)
        self.last_trace = []
        before = self.model.network_samples
        def observe(row, *args):
            self.last_trace.append(dict(row))
            if observer is not None:
                observer(row, *args)
        result = run_spatial_score(current, self.denoiser, scale=c['scale'],
            initial_variance=inputs.activity_prior*c['initialization']['normalized_training_second_moment'],
            config=self.controls, observer=observe, decision_threshold=c['decision_threshold'],
            adapt=c.get('query_variance_update', {}).get('enabled', True))
        if self.device == 'cuda':
            torch.cuda.synchronize()
        arrays = dict(estimate=result.estimate, conditional_matrix=result.conditional_matrix,
            probabilities=result.probabilities, activity_decision=result.probabilities>=c['decision_threshold'],
            spatial_covariance=result.spatial_covariance, noise_variance_estimate=np.asarray(noise))
        record = self.context()
        record.update(status='COMPLETE', candidate='posterior_expected_residual_query_variance',
            iterations=len(result.trace), converged=result.stopping_reason=='CONVERGED',
            stopping_reason=result.stopping_reason, seconds=time.perf_counter()-started,
            first_network_samples=self.model.network_samples-before, noise_estimation=noise_record,
            receiver_truth_used=False, query_variance_update='one damped posterior residual-energy update per outer iteration',
            limitations=['Approximate neural posterior; no exact EM likelihood monotonicity or VAMP state-evolution guarantee.',
                         'Scalar covariance and derivative approximation remain; physical noise estimate unchanged.'])
        return arrays, record
