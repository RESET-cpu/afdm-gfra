"""Reuse the frozen physical frontend, then the ungated Shen outer schedule."""
from dataclasses import asdict, replace
import time
import numpy as np
import torch

from project import ROOT
from utils import read_json, sha256
from system.receiver.unknown_phase import UnknownPhaseInput
from system.receiver.noise_estimation import estimate_spatial_noise
from system.receiver import phase_estimation
from algorithm.STMP.denoiser import Denoiser
from algorithm.C_STMP_phase_frontend_20261027.receiver import Receiver as FrontendReceiver
from .iterations import infer as iterate


class Receiver(FrontendReceiver):
    def __init__(self, configuration, *, device='cpu', noise_mode='estimated'):
        binding = read_json(configuration)
        if binding['schema'] != 'c-stmp-shen-physical-every-20261104-v1':
            raise ValueError('Explicit independent candidate binding required')
        if sha256(ROOT / binding['frontend_binding']) != binding['frontend_binding_sha256']:
            raise ValueError('Frozen physical frontend binding changed')
        super().__init__(ROOT / binding['frontend_binding'], device=device, noise_mode=noise_mode)
        if binding['initialization'] != 'physical' or binding['outer_loop']['update'] != 'every_nonterminated_outer_iteration':
            raise ValueError('Physical initialization and ungated per-iteration update required')
        self.candidate_binding = binding
        self.stopping_tolerance = binding['outer_loop']['squared_relative_channel_tolerance']
        self.controls = replace(self.controls, iterations=binding['outer_loop']['maximum_iterations'],
            min_iterations=1, convergence_patience=1, activity_convergence_tolerance=None,
            decision_stability_window=0)

    def infer(self, inputs, *, observer=None, phase_observer=None):
        if not isinstance(inputs, UnknownPhaseInput):
            raise TypeError('Raw observation and original pilots required')
        started = time.perf_counter()
        noise, noise_record = estimate_spatial_noise(inputs.observation)
        raw = replace(inputs, noise_variance=float(noise))
        initial, initialization = phase_estimation.estimate(raw, self.phase_controls, observer=phase_observer)
        initial_phase = np.exp(1j*np.arange(len(raw.pilot))[:, None]*initial['phase_slopes'][None])
        c = self.configuration
        self.model.reset()
        self.denoiser = Denoiser(self.model, self.evidence, activity_prior=raw.activity_prior,
            conditional_variance_floor=c['conditional_variance_floor_checkpoint_normalized'],
            raw_site_residual_tolerance=self.controls.raw_site_residual_tolerance,
            activity_weight_residual_tolerance=self.controls.activity_weight_residual_tolerance,
            activity_stopping_reference=self.controls.activity_stopping_reference)
        result, phase, next_phase, trials = iterate(raw, self.denoiser, scale=c['scale'],
            initial_variance=raw.activity_prior*c['initialization']['normalized_training_second_moment'],
            controls=self.controls, stopping_tolerance=self.stopping_tolerance, initial_phase=initial_phase,
            observer=observer, decision_threshold=c['decision_threshold'],
            adapt=c.get('query_variance_update', {}).get('enabled', True))
        if self.device == 'cuda':
            torch.cuda.synchronize()
        arrays = dict(estimate=result.estimate, conditional_matrix=result.conditional_matrix,
            probabilities=result.probabilities, activity_decision=result.probabilities >= c['decision_threshold'],
            spatial_covariance=result.spatial_covariance, noise_variance_estimate=np.asarray(noise),
            initial_phase_slopes=initial['phase_slopes'], initial_phase=initial_phase,
            phase=phase, next_phase=next_phase)
        record = self.context()
        record.update(status='COMPLETE', candidate=self.candidate_binding['name'],
            iterations=len(result.trace), converged=result.stopping_reason == 'CONVERGED',
            stopping_reason=result.stopping_reason, seconds=time.perf_counter()-started,
            noise_estimation=noise_record, phase_initialization=initialization,
            phase_controls=asdict(self.phase_controls), candidate_binding=self.candidate_binding,
            actual_iteration_controls=asdict(self.controls), phase_mode='estimated',
            phase_method='Shen_per_frame_projection_every_outer_iteration_after_physical_initialization',
            oracle_phase_supplied=False, receiver_truth_used=False, noise_truth_used=False,
            supplied_phase_operator_used=False, input_noise_placeholder_ignored=True,
            input_fields=['observation', 'pilot', 'activity_prior'], physical_path_search_used=True,
            path_search_during_updates=False, phase_updates_inside_receiver=len(trials),
            phase_trials=trials, steps=trials, trace=list(result.trace),
            phase_seconds=sum(t['seconds']+t['linear_rebuild_seconds'] for t in trials),
            common_slope_projection=False, channel_feedback_rotation=False,
            query_history_reset_after_phase=False, query_variance_ratio_reset_after_phase=False,
            free_phase_parameters=(len(raw.pilot)-1)*raw.pilot.shape[1],
            phase_output_semantics='phase formed returned channel; next_phase is the final updated state',
            next_phase_has_following_message_pass=result.stopping_reason == 'CONVERGED',
            limitations=['AFDM learned messages and Gaussian phase moments; not full Shen OTFS receiver reproduction.',
                'Compared with the periodic arm, schedule, state-reset behavior and stopping differ.',
                'A capped final next_phase is not consumed by a subsequent channel pass.'])
        return arrays, record
