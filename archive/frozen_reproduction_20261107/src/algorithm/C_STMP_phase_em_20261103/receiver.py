"""Own-model phase candidate bound to the frozen known-phase receiver."""
from dataclasses import replace
import time
import numpy as np
import torch

from project import ROOT
from utils import read_json, sha256
from system.observation import ReceiverInput
from system.receiver.unknown_phase import UnknownPhaseInput
from system.receiver.noise_estimation import estimate_spatial_noise
from algorithm.STMP.denoiser import Denoiser
from algorithm.C_STMP_variance_em_20261025.receiver import Receiver as ConditionalReceiver
from algorithm.C_STMP_variance_em_20261025.iterations import run_spatial_score
from .denoiser import GuardedDenoiser
from .iterations import infer as iterate


class Receiver(ConditionalReceiver):
    def __init__(self, configuration, *, device='cpu', noise_mode='estimated'):
        binding = read_json(configuration)
        if binding['schema'] != 'c-stmp-phase-em-20261103-v1' or noise_mode != 'estimated':
            raise ValueError('Explicit candidate binding and estimated noise required')
        if (binding['initialization'] != 'zero_slopes'
                or binding['variance_policy'] not in ('legacy_floor', 'reject_nonpositive_pooled')):
            raise ValueError('Unknown candidate policy')
        if sha256(ROOT/binding['receiver_configuration']) != binding['receiver_configuration_sha256']:
            raise ValueError('Frozen conditional receiver binding changed')
        super().__init__(ROOT/binding['receiver_configuration'], device=device, noise_mode=noise_mode)
        self.candidate_binding = binding
        self.last_phase_steps = []

    def _denoiser(self, activity_prior):
        cls = (GuardedDenoiser if self.candidate_binding['variance_policy'] == 'reject_nonpositive_pooled'
               else Denoiser)
        return cls(self.model, self.evidence, activity_prior=activity_prior,
            conditional_variance_floor=self.configuration['conditional_variance_floor_checkpoint_normalized'],
            raw_site_residual_tolerance=self.controls.raw_site_residual_tolerance,
            activity_weight_residual_tolerance=self.controls.activity_weight_residual_tolerance,
            activity_stopping_reference=self.controls.activity_stopping_reference)

    def infer(self, inputs, *, observer=None, phase_observer=None):
        """UnknownPhaseInput estimates phase; ReceiverInput is explicit fixed-phase ablation.

        The unknown-phase branch never accepts initial slopes or an oracle operator.
        The fixed-phase branch is labelled supplied_operator in its result record.
        """
        if not isinstance(inputs, (UnknownPhaseInput, ReceiverInput)):
            raise TypeError('Raw unknown-phase or explicit fixed-operator input required')
        unknown = isinstance(inputs, UnknownPhaseInput)
        started = time.perf_counter()
        noise, noise_record = estimate_spatial_noise(inputs.observation)
        current = replace(inputs, noise_variance=float(noise))
        c = self.configuration
        self.model.reset()
        self.denoiser = self._denoiser(inputs.activity_prior)
        self.last_trace, self.last_phase_steps = [], []
        before = self.model.network_samples
        common = dict(scale=c['scale'],
            initial_variance=inputs.activity_prior*c['initialization']['normalized_training_second_moment'],
            observer=observer, decision_threshold=c['decision_threshold'],
            adapt=c.get('query_variance_update', {}).get('enabled', True))
        if unknown:
            result, beta, trials = iterate(current, self.denoiser,
                controls=self.controls, policy=self.candidate_binding['iteration_policy'],
                phase_observer=phase_observer, **common)
        else:
            result = run_spatial_score(current, self.denoiser, config=self.controls, **common)
            beta, trials = None, []
        self.last_trace, self.last_phase_steps = list(result.trace), trials
        if self.device == 'cuda':
            torch.cuda.synchronize()
        arrays = dict(estimate=result.estimate, conditional_matrix=result.conditional_matrix,
            probabilities=result.probabilities, activity_decision=result.probabilities >= c['decision_threshold'],
            spatial_covariance=result.spatial_covariance, noise_variance_estimate=np.asarray(noise))
        if unknown:
            arrays.update(initial_phase_slopes=np.zeros_like(beta), phase_slopes=beta,
                          phase=np.exp(1j*np.arange(len(current.pilot))[:, None]*beta[None]))
        record = self.context()
        record.update(status='COMPLETE', candidate=self.candidate_binding['name'],
            iterations=len(result.trace), converged=result.stopping_reason == 'CONVERGED',
            stopping_reason=result.stopping_reason, seconds=time.perf_counter()-started,
            first_network_samples=self.model.network_samples-before, noise_estimation=noise_record,
            receiver_truth_used=False, noise_truth_used=False,
            phase_mode='estimated' if unknown else 'supplied_operator_ablation',
            supplied_phase_operator_used=not unknown,
            phase_initialization='zero_slopes' if unknown else 'not_applicable',
            physical_path_search_used=False, path_search_during_updates=False,
            phase_method='local_minimization_of_fixed_joint_posterior_expected_residual',
            candidate_binding=self.candidate_binding,
            phase_updates_inside_receiver=sum(t['applied'] for t in trials),
            phase_seconds=sum(t.get('seconds', 0.)+t['linear_rebuild_seconds'] for t in trials),
            phase_trials=trials, trace=self.last_trace,
            phase_output_semantics='returned slopes formed returned channel',
            limitations=[
                'Approximate neural E step; no exact EM observed-likelihood or AER monotonicity guarantee.',
                'Independent-user working posterior; fixed within-user uncertainty contributes only a phase-independent constant.',
                'Finite E and M budgets and local phase optimization can leave bad stationary points.',
                'The trained marginal channel prior does not impose the full physical coupling between channel and Doppler.',
                'Rejecting a negative pooled trace retains the previous Gaussian site; it does not calibrate neural uncertainty.'])
        return arrays, record
