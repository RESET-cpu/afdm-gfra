"""Physical initialization followed by phase-coordinate minimization."""
from dataclasses import asdict, replace
import time
import numpy as np
import torch
from project import ROOT
from utils import read_json, sha256
from system.observation import ReceiverInput
from system.receiver.unknown_phase import UnknownPhaseInput
from system.receiver.noise_estimation import estimate_spatial_noise
from system.receiver import phase_estimation
from algorithm.STMP.denoiser import Denoiser
from algorithm.C_STMP_phase_selection_20261030.receiver import Receiver as SelectedReceiver
from .iterations import infer as conditional_iterate


class Receiver(SelectedReceiver):
    def __init__(self, configuration, *, device='cpu', noise_mode='estimated'):
        binding = read_json(configuration)
        if binding['schema'] != 'c-stmp-phase-coordinate-20261104-v1':
            raise ValueError('Explicit independent scheduling candidate required')
        if sha256(ROOT/binding['selected_configuration']) != binding['selected_configuration_sha256']:
            raise ValueError('Selected binding changed')
        super().__init__(ROOT/binding['selected_configuration'], device=device, noise_mode=noise_mode)
        self.candidate_binding = binding
        self.candidate_name = binding['name']
        self.policy = binding['policy']
        if self.policy != 'coordinate':
            raise ValueError('Unknown scheduling policy')
        self.phase_configuration = dict(binding['phase'])
        self.phase_configuration['initializer'] = 'physical'
        self.unknown_controls = self.controls

    def infer(self, inputs, *, observer=None, phase_observer=None):
        if isinstance(inputs, ReceiverInput):
            return super().infer(inputs, observer=observer)
        if not isinstance(inputs, UnknownPhaseInput):
            raise TypeError('Raw observation and original pilots required')
        started = time.perf_counter()
        noise, noise_record = estimate_spatial_noise(inputs.observation)
        raw = replace(inputs, noise_variance=float(noise))
        if self.phase_configuration['initializer'] == 'physical':
            initial, initialization = phase_estimation.estimate(raw, self.phase_controls, observer=phase_observer)
        else:
            initial = dict(phase_slopes=np.zeros(raw.pilot.shape[1]))
            initialization = dict(method='zero_slopes_without_frontend', seconds=0., truth_used_in_inference=False)
        c = self.configuration
        self.model.reset()
        self.denoiser = Denoiser(self.model, self.evidence, activity_prior=raw.activity_prior,
            conditional_variance_floor=c['conditional_variance_floor_checkpoint_normalized'],
            raw_site_residual_tolerance=self.controls.raw_site_residual_tolerance,
            activity_weight_residual_tolerance=self.controls.activity_weight_residual_tolerance,
            activity_stopping_reference=self.controls.activity_stopping_reference)
        before = self.model.network_samples
        iterate = conditional_iterate
        result, phase, steps, trials = iterate(raw, self.denoiser, scale=c['scale'],
            initial_variance=raw.activity_prior*c['initialization']['normalized_training_second_moment'],
            controls=self.unknown_controls, phase_configuration=self.phase_configuration,
            initial_slopes=initial['phase_slopes'], observer=observer, decision_threshold=c['decision_threshold'],
            adapt=c.get('query_variance_update', {}).get('enabled', True))
        self.last_trace, self.last_phase_steps = list(result.trace), steps
        if self.device == 'cuda':
            torch.cuda.synchronize()
        arrays = dict(estimate=result.estimate, conditional_matrix=result.conditional_matrix,
            probabilities=result.probabilities, activity_decision=result.probabilities >= c['decision_threshold'],
            spatial_covariance=result.spatial_covariance, noise_variance_estimate=np.asarray(noise),
            phase=phase, initial_phase=np.exp(1j*np.arange(len(raw.pilot))[:,None]*initial['phase_slopes']),
            initial_phase_slopes=initial['phase_slopes'])
        record = self.context()
        record.update(status='COMPLETE', candidate=self.candidate_name,
            iterations=len(result.trace), converged=result.stopping_reason == 'CONVERGED',
            stopping_reason=result.stopping_reason, seconds=time.perf_counter()-started,
            first_network_samples=self.model.network_samples-before, noise_estimation=noise_record,
            phase_mode='estimated', oracle_phase_supplied=False, receiver_truth_used=False,
            noise_truth_used=False, supplied_phase_operator_used=False, input_noise_placeholder_ignored=True,
            input_fields=['observation','pilot','activity_prior'], phase_method='Cyclic_unit_modulus_phase_coordinate_minimization',
            phase_parameterization='Independent per-user phase in each frame; q=0 fixed to one',
            common_slope_projection=False, channel_feedback_rotation=False,
            free_phase_parameters=(len(raw.pilot)-1)*raw.pilot.shape[1],
            physical_path_search_used=self.phase_configuration['initializer'] == 'physical',
            path_search_during_updates=False,
            candidate_binding=self.candidate_binding,
            phase_initialization=initialization, phase_controls=asdict(self.phase_controls),
            phase_configuration=self.phase_configuration, actual_iteration_controls=asdict(self.unknown_controls),
            phase_updates_inside_receiver=len(steps), steps=steps, phase_trials=trials,
            phase_seconds=sum(t['seconds']+t.get('linear_rebuild_seconds',0.) for t in trials),
            classifier_phase_hypotheses=False, query_history_reset_after_phase=False,
            query_variance_ratio_reset_after_phase=False, global_neural_descent_claim=False,
            trace=self.last_trace, limitations=[
                'Candidate pending paired selection; no global optimality or convergence guarantee.',
                'Stopping uses existing conditional controls and, in conditional mode, current expected signal change; no true phase error is used.',
                'Conditional stability may prevent phase updates; MAX_ITERATIONS remains a failure to meet stopping.',
                'Each exact coordinate sweep decreases the frozen conditional quadratic; this does not ensure global learned-receiver improvement.',
                'Uses our full Gaussian conditional moments and all users, not original OTFS tap truncation.',
                'Phase variables increase from K slopes to (Q-1)*K free angles; physical initialization remains.'])
        return arrays, record
