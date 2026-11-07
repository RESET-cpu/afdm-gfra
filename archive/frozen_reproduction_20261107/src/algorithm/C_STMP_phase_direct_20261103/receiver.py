"""Candidate-only public-input receiver, with no physical parameter search."""
from dataclasses import asdict, replace
import time
import numpy as np
import torch
from project import ROOT
from utils import read_json, sha256
from system.receiver.unknown_phase import UnknownPhaseInput
from system.receiver.noise_estimation import estimate_spatial_noise
from algorithm.C_STMP_variance_em_20261025.receiver import Receiver as BaseReceiver
from algorithm.STMP.denoiser import Denoiser
from .iterations import infer


class Receiver(BaseReceiver):
    def __init__(self, configuration, *, device='cuda', noise_mode='estimated'):
        binding = read_json(configuration)
        if binding['schema'] != 'c-stmp-direct-phase-20261103-v1':
            raise ValueError('Independent candidate binding required')
        path = ROOT/binding['receiver_configuration']
        if sha256(path) != binding['receiver_configuration_sha256']:
            raise ValueError('Base receiver binding changed')
        super().__init__(path, device=device, noise_mode=noise_mode)
        self.binding = binding
        self.controls = replace(self.controls, **binding.get('iteration_overrides', {}))

    def infer(self, inputs, *, observer=None, phase_observer=None):
        if not isinstance(inputs, UnknownPhaseInput):
            raise TypeError('UnknownPhaseInput required; no true effective operator')
        started = time.perf_counter()
        noise, noise_record = estimate_spatial_noise(inputs.observation)
        raw = replace(inputs, noise_variance=float(noise))
        c = self.configuration
        self.model.reset()
        self.denoiser = Denoiser(self.model,self.evidence,activity_prior=raw.activity_prior,
            conditional_variance_floor=c['conditional_variance_floor_checkpoint_normalized'],
            raw_site_residual_tolerance=self.controls.raw_site_residual_tolerance,
            activity_weight_residual_tolerance=self.controls.activity_weight_residual_tolerance,
            activity_stopping_reference=self.controls.activity_stopping_reference)
        initial = np.zeros(raw.pilot.shape[1])
        initialization = dict(method='zero_slopes',seconds=0.,physical_path_search_used=False)
        if self.binding['initialization']['method'] != 'zero':
            if self.binding['initialization']['method'] == 'grouped_covariance':
                from .grouped_initialization import estimate
            else:
                from .initialization import estimate
            initial, initialization = estimate(raw, self.binding['initialization'], c)
        before = self.model.network_samples
        result,beta,steps,trials = infer(raw,self.denoiser,scale=c['scale'],
            initial_variance=raw.activity_prior*c['initialization']['normalized_training_second_moment'],
            controls=self.controls,policy=self.binding['phase_update'],initial_slopes=initial,
            observer=observer,decision_threshold=c['decision_threshold'])
        if self.device == 'cuda':
            torch.cuda.synchronize()
        self.last_trace = list(result.trace)
        self.last_phase_steps = steps
        arrays = dict(estimate=result.estimate,conditional_matrix=result.conditional_matrix,
            probabilities=result.probabilities,activity_decision=result.probabilities>=c['decision_threshold'],
            spatial_covariance=result.spatial_covariance,noise_variance_estimate=np.asarray(noise),
            phase_slopes=beta,phase=np.exp(1j*np.arange(len(raw.pilot))[:,None]*beta),
            initial_phase_slopes=initial)
        record = self.context()
        record.update(status='COMPLETE',candidate=self.binding['name'],iterations=len(result.trace),
            converged=result.stopping_reason=='CONVERGED',stopping_reason=result.stopping_reason,
            seconds=time.perf_counter()-started,first_network_samples=self.model.network_samples-before,
            phase_mode='estimated',receiver_truth_used=False,noise_truth_used=False,
            oracle_phase_supplied=False,physical_path_search_used=False,
            noise_estimation=noise_record,phase_initialization=initialization,
            phase_updates_inside_receiver=len(steps),steps=steps,phase_trials=trials,
            actual_iteration_controls=asdict(self.controls),candidate_binding=self.binding,
            phase_seconds=sum(t['seconds']+t.get('linear_rebuild_seconds',0.) for t in trials),
            trace=self.last_trace,limitations=[
                'Gaussian-message moments are exact for the declared surrogate, not the physical posterior.',
                'Early phase updates and a learned prior do not guarantee identifiability or global convergence.',
                'No batch selection or mainline promotion is implied.'])
        return arrays,record
