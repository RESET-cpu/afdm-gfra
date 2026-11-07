"""Existing STMP phase refinements driven by the current C-STMP feedback.

Use the same physical initializer as the fixed-phase candidate so the small
comparison measures adding within-iteration updates, not changing initialization.
"""
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
from algorithm.C_STMP_phase_frontend_20261027.receiver import Receiver as FrontendReceiver
from .iterations import infer as iterate


class Receiver(FrontendReceiver):
    def __init__(self, configuration, *, device='cpu', noise_mode='estimated'):
        binding = read_json(configuration)
        if binding['schema'] != 'c-stmp-iterative-phase-v1':
            raise ValueError('Explicit independent iterative-phase binding required')
        for key in ('frontend_binding', 'phase_configuration'):
            if sha256(ROOT / binding[key]) != binding[key + '_sha256']:
                raise ValueError('Bound configuration changed: ' + key)
        super().__init__(ROOT / binding['frontend_binding'], device=device, noise_mode=noise_mode)
        self.iterative_binding = binding
        self.phase_configuration = read_json(ROOT / binding['phase_configuration'])
        p = self.phase_configuration
        if (p['training_source_sha256'] != self.configuration['initialization']['training_sha256']
                or p['phase_update'] != dict(minimum_sweeps=2, maximum_sweeps=10, relative_tolerance=1e-7)):
            raise ValueError('Training population and existing phase solver must match')
        moment_path = ROOT / p['training_second_moment']
        if sha256(moment_path) != p['training_second_moment_sha256']:
            raise ValueError('Training moment changed')
        with np.load(moment_path, allow_pickle=False) as saved:
            self.training_moment = saved['second_moment'].copy() / self.configuration['scale']**2
        self.unknown_controls = replace(self.controls, min_iterations=p['minimum_conditional_iterations'])
        if (binding['phase_stopping_min_iterations'] != self.unknown_controls.min_iterations
                or binding['phase_change_query_variance_ratio'] != 'reset_to_one'):
            raise ValueError('Unsupported phase integration settings')
        self.last_phase_steps = []

    def infer(self, inputs, *, observer=None, phase_observer=None):
        if isinstance(inputs, ReceiverInput):
            return super().infer(inputs, observer=observer)
        if not isinstance(inputs, UnknownPhaseInput):
            raise TypeError('Raw observation and original pilots required')
        started = time.perf_counter()
        noise, noise_record = estimate_spatial_noise(inputs.observation)
        raw = replace(inputs, noise_variance=float(noise))
        initial, initialization = phase_estimation.estimate(raw, self.phase_controls, observer=phase_observer)
        c = self.configuration
        self.model.reset()
        self.denoiser = Denoiser(self.model, self.evidence, activity_prior=raw.activity_prior,
            conditional_variance_floor=c['conditional_variance_floor_checkpoint_normalized'],
            raw_site_residual_tolerance=self.controls.raw_site_residual_tolerance,
            activity_weight_residual_tolerance=self.controls.activity_weight_residual_tolerance,
            activity_stopping_reference=self.controls.activity_stopping_reference)
        before = self.model.network_samples
        result, beta, steps, checks = iterate(raw, self.denoiser, scale=c['scale'],
            initial_variance=raw.activity_prior*c['initialization']['normalized_training_second_moment'],
            controls=self.unknown_controls, phase_configuration=self.phase_configuration,
            initial_slopes=initial['phase_slopes'], training_moment=self.training_moment,
            reference_power=c['initialization']['normalized_training_second_moment'],
            observer=observer, decision_threshold=c['decision_threshold'],
            adapt=c.get('query_variance_update', {}).get('enabled', True))
        self.last_trace, self.last_phase_steps = list(result.trace), steps
        if self.device == 'cuda':
            torch.cuda.synchronize()
        arrays = dict(estimate=result.estimate, conditional_matrix=result.conditional_matrix,
            probabilities=result.probabilities, activity_decision=result.probabilities >= c['decision_threshold'],
            spatial_covariance=result.spatial_covariance, noise_variance_estimate=np.asarray(noise),
            phase_slopes=beta, phase=np.exp(1j*np.arange(len(raw.pilot))[:, None]*beta),
            initial_phase_slopes=initial['phase_slopes'])
        record = self.context()
        record.update(status='COMPLETE', candidate='c_stmp_iterative_phase_20261028',
            iterations=len(result.trace), converged=result.stopping_reason == 'CONVERGED',
            stopping_reason=result.stopping_reason, seconds=time.perf_counter()-started,
            first_network_samples=self.model.network_samples-before,
            noise_estimation=noise_record, phase_mode='estimated', oracle_phase_supplied=False,
            receiver_truth_used=False, noise_truth_used=False, supplied_phase_operator_used=False,
            input_noise_placeholder_ignored=True, input_fields=['observation', 'pilot', 'activity_prior'],
            phase_method='gaussian_refinement_and_active_candidate_phase_hypotheses',
            phase_initialization=initialization, phase_controls=asdict(self.phase_controls),
            phase_configuration=self.phase_configuration, actual_iteration_controls=asdict(self.unknown_controls),
            phase_initialization_override='Physical frontend shared with fixed-phase comparator; not STMP directional initialization',
            phase_updates_inside_receiver=len(steps), steps=steps, phase_hypothesis_checks=checks,
            query_history_reset_after_phase=True, query_variance_ratio_reset_after_phase=1.,
            query_variance_update='Same damped posterior-residual update as current C-STMP',
            global_neural_descent_claim=False, trace=self.last_trace,
            limitations=['Fixed-message Gaussian descent does not guarantee whole-receiver convergence.',
                         'Classifier phase candidates use approximate local evidence.',
                         'Phase-cycle stopping has an 80-iteration minimum; fixed-phase controls retain 60.'])
        return arrays, record
