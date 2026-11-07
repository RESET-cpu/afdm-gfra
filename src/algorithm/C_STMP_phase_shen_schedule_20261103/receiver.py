"""All-one initialization and Shen Algorithm 1's outer-loop order for AFDM."""
from dataclasses import asdict, replace
import time
import numpy as np
import torch

from project import ROOT
from utils import read_json, sha256
from system.receiver.unknown_phase import UnknownPhaseInput
from system.receiver.noise_estimation import estimate_spatial_noise
from algorithm.STMP.denoiser import Denoiser
from algorithm.C_STMP_variance_em_20261025.receiver import Receiver as ConditionalReceiver
from .iterations import infer as iterate


class Receiver(ConditionalReceiver):
    def __init__(self, configuration, *, device='cpu', noise_mode='estimated'):
        binding = read_json(configuration)
        if binding['schema'] != 'c-stmp-shen-schedule-20261103-v1' or noise_mode != 'estimated':
            raise ValueError('Explicit all-one Shen schedule with estimated observation noise required')
        if (binding['initialization'] != 'all_one_phase'
                or binding['outer_loop']['update'] != 'every_nonterminated_outer_iteration'
                or binding['phase_update'] != dict(rule='Shen equation53 projected linear solve',
                    reference_frame=0, all_users=True, objective_descent_guard=False,
                    common_slope_projection=False)):
            raise ValueError('Configuration must describe the implemented Shen iteration order')
        if sha256(ROOT/binding['receiver_configuration']) != binding['receiver_configuration_sha256']:
            raise ValueError('Frozen conditional receiver binding changed')
        super().__init__(ROOT/binding['receiver_configuration'], device=device, noise_mode=noise_mode)
        self.candidate_binding = binding
        self.candidate_name = binding['name']
        self.stopping_tolerance = float(binding['outer_loop']['squared_relative_channel_tolerance'])
        self.controls = replace(self.controls,
            iterations=int(binding['outer_loop']['maximum_iterations']), min_iterations=1,
            convergence_tolerance=float(np.sqrt(self.stopping_tolerance)),
            convergence_patience=1, activity_convergence_tolerance=None, decision_stability_window=0)

    def infer(self, inputs, *, observer=None, phase_observer=None):
        if not isinstance(inputs, UnknownPhaseInput):
            raise TypeError('Raw observations and original pilots required')
        started = time.perf_counter()
        noise, noise_record = estimate_spatial_noise(inputs.observation)
        raw = replace(inputs, noise_variance=float(noise))
        c = self.configuration
        self.model.reset()
        self.denoiser = Denoiser(self.model, self.evidence, activity_prior=raw.activity_prior,
            conditional_variance_floor=c['conditional_variance_floor_checkpoint_normalized'],
            raw_site_residual_tolerance=self.controls.raw_site_residual_tolerance,
            activity_weight_residual_tolerance=self.controls.activity_weight_residual_tolerance,
            activity_stopping_reference=self.controls.activity_stopping_reference)
        before = self.model.network_samples
        result, phase, next_phase, trials = iterate(raw, self.denoiser, scale=c['scale'],
            initial_variance=raw.activity_prior*c['initialization']['normalized_training_second_moment'],
            controls=self.controls, stopping_tolerance=self.stopping_tolerance,
            observer=observer, decision_threshold=c['decision_threshold'],
            adapt=c.get('query_variance_update', {}).get('enabled', True))
        self.last_trace, self.last_phase_steps = list(result.trace), trials
        if self.device == 'cuda':
            torch.cuda.synchronize()
        arrays = dict(estimate=result.estimate, conditional_matrix=result.conditional_matrix,
            probabilities=result.probabilities, activity_decision=result.probabilities >= c['decision_threshold'],
            spatial_covariance=result.spatial_covariance, noise_variance_estimate=np.asarray(noise),
            initial_phase=np.ones(raw.pilot.shape[:2], complex), phase=phase, next_phase=next_phase)
        record = self.context()
        record.update(status='COMPLETE', candidate=self.candidate_name,
            iterations=len(result.trace), converged=result.stopping_reason == 'CONVERGED',
            stopping_reason=result.stopping_reason, seconds=time.perf_counter()-started,
            first_network_samples=self.model.network_samples-before, noise_estimation=noise_record,
            phase_mode='estimated', oracle_phase_supplied=False, receiver_truth_used=False,
            noise_truth_used=False, supplied_phase_operator_used=False, input_noise_placeholder_ignored=True,
            input_fields=['observation','pilot','activity_prior'],
            phase_method='Shen_per_frame_projection_every_outer_iteration',
            phase_initialization=dict(method='all_one', seconds=0., physical_path_search_used=False),
            physical_path_search_used=False, path_search_during_updates=False,
            candidate_binding=self.candidate_binding, actual_iteration_controls=asdict(self.controls),
            phase_updates_inside_receiver=len(trials), steps=trials, phase_trials=trials,
            phase_seconds=sum(t['seconds']+t['linear_rebuild_seconds'] for t in trials),
            common_slope_projection=False, channel_feedback_rotation=False,
            free_phase_parameters=(len(raw.pilot)-1)*raw.pilot.shape[1],
            query_history_reset_after_phase=False, query_variance_ratio_reset_after_phase=False,
            phase_output_semantics='phase formed returned channel; next_phase is the final updated state',
            next_phase_has_following_message_pass=result.stopping_reason == 'CONVERGED',
            trace=self.last_trace, limitations=[
                'AFDM message modules and full Gaussian phase moments, not a full OTFS receiver reproduction.',
                'All users and fixed q0 are model adaptations; no original delay-tap energy truncation.',
                'Observation noise and trained prior remain fixed; scalar query variance is adapted separately.',
                'Channel stopping does not imply accurate phase, correct activity or global convergence.',
                'At MAX_ITERATIONS, next_phase has no following channel update and is not used for phase scoring.'])
        return arrays, record
