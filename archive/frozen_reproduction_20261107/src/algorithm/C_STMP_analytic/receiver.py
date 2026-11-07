"""Independent analytic-activity C-STMP; one frozen conditional-mean network."""
from copy import deepcopy
from pathlib import Path
import time
import numpy as np
import torch

from project import ROOT
from utils import read_json, sha256
from system.observation import ReceiverInput
from system.receiver.noise_estimation import estimate_spatial_noise
from algorithm.STMP.iterations import run_spatial_score
from algorithm.STMP.records import SpatialConfig
from algorithm.C_STMP.moments import ColoredMoments
from .denoiser import Denoiser


class Receiver:
    def __init__(self, configuration, *, device='cuda'):
        c = read_json(configuration) if isinstance(configuration, (str, Path)) else deepcopy(configuration)
        if (c['schema'] != 'colored-stmp-analytic-activity-v1'
                or c['activity_evidence'] != 'normalized_gaussian_site'
                or c['query_covariance'] != 'vI' or c['site_damping'] != 1
                or c['decision_threshold'] != .5
                or any(k.startswith(('classifier', 'evidence_checkpoint')) for k in c)):
            raise ValueError('Explicit classifier-free analytic candidate required')
        self.configuration, self.device = c, device
        self.checkpoints = {}
        for key in ('first_checkpoint', 'prior_definition'):
            digest = sha256(ROOT/c[key])
            if digest != c[key+'_sha256']:
                raise ValueError('Candidate asset changed: '+key)
            self.checkpoints[key] = digest
        first = torch.load(ROOT/c['first_checkpoint'], map_location='cpu', weights_only=False, mmap=True)
        if (first['schema'] != 'colored-preconditioned-first-v1'
                or first['output'] != 'conditional_mean'
                or first['global_complex_rms'] != c['scale']
                or first['metadata']['epoch'] != c['first_epoch']
                or read_json(ROOT/c['prior_definition'])['global_complex_rms'] != c['scale']):
            raise ValueError('Same-coordinate conditional mean required')
        self.controls = SpatialConfig(**c['ep'])
        self.controls.validate_stopping()
        if self.controls.covariance_mode != 'isotropic':
            raise ValueError('Scalar-variance candidate required')
        self.model = ColoredMoments(ROOT/c['first_checkpoint'], device=device,
                                   batch_size=c['batch_size'], **c['variance_estimator'])
        self.last_trace, self.denoiser = [], None

    def infer(self, inputs, *, observer=None):
        if (not isinstance(inputs, ReceiverInput)
                or inputs.observation.shape[1:] != (16, 16)
                or inputs.operator.shape[-1] != 16):
            raise ValueError('16-antenna/16x16 public ReceiverInput required')
        started = time.perf_counter()
        c = self.configuration
        noise, noise_record = estimate_spatial_noise(inputs.observation)
        current = ReceiverInput(inputs.observation, inputs.operator, noise, inputs.activity_prior)
        self.model.reset()
        before = self.model.samples, self.model.first_calls, self.model.network_samples
        floor = c['conditional_variance_floor_checkpoint_normalized']/self.model.scale_ratio**2
        self.denoiser = Denoiser(self.model, activity_prior=inputs.activity_prior,
            conditional_variance_floor=floor,
            raw_site_residual_tolerance=self.controls.raw_site_residual_tolerance,
            activity_weight_residual_tolerance=self.controls.activity_weight_residual_tolerance,
            activity_stopping_reference=self.controls.activity_stopping_reference)
        self.last_trace = []

        def observe(row, *state):
            self.last_trace.append(dict(row))
            if observer is not None:
                observer(row, *state)

        result = run_spatial_score(current, self.denoiser, scale=c['scale'],
            initial_variance=inputs.activity_prior*c['initialization']['normalized_training_second_moment'],
            config=self.controls, observer=observe, decision_threshold=c['decision_threshold'])
        if self.device == 'cuda':
            torch.cuda.synchronize()
        arrays = dict(estimate=result.estimate, conditional_matrix=result.conditional_matrix,
            probabilities=result.probabilities,
            activity_decision=result.probabilities >= c['decision_threshold'],
            spatial_covariance=result.spatial_covariance, noise_variance_estimate=np.asarray(noise))
        samples = self.model.samples-before[0]
        assert samples == sum(row['moment_samples'] for row in self.last_trace)
        effective = deepcopy(c)
        effective.update(device=self.device, activity_prior=float(inputs.activity_prior))
        record = dict(status='COMPLETE', method='C-STMP (analytic activity)',
            activity_evidence=c['activity_evidence'], configuration=effective,
            classifier_loaded=False, classifier_calls=0, classifier_samples=0,
            second_network_loaded=False, second_score_calls=0, second_score_samples=0,
            first_network_samples=self.model.network_samples-before[2], first_score_samples=samples,
            first_score_calls=self.model.first_calls-before[1],
            checkpoint_sha256=self.checkpoints, trace=self.last_trace,
            iterations=len(self.last_trace), stopping_reason=result.stopping_reason,
            converged=result.stopping_reason == 'CONVERGED', seconds=time.perf_counter()-started,
            channel_truth_loaded=False, noise_truth_used=False, noise_mode='estimated',
            noise_estimation=noise_record, phase_mode='supplied_operator', oracle_phase_supplied=True,
            query_covariance='vI', variance_source='finite_difference_conditional_mean',
            first_epoch=c['first_epoch'], first_output='conditional_mean',
            conditional_variance_floor_iterations=sum(t['conditional_variance_floored'] for t in self.last_trace),
            unsupported_user_queries=sum(t['unsupported_users'] for t in self.last_trace),
            accepted_site_iterations=sum(t['site_accepted'] for t in self.last_trace),
            reused_site_iterations=sum(t['reused_site'] for t in self.last_trace))
        return arrays, record
