"""Independent bindings; mainline receivers, networks and controls are untouched."""
from dataclasses import asdict
import time
import numpy as np
import torch

from project import ROOT
from utils import read_json, sha256
from system.observation import ReceiverInput
from system.receiver.noise_estimation import estimate_spatial_noise
from algorithm.C_STMP_retrained.configuration import verify
from algorithm.C_STMP.moments import ColoredMoments
from algorithm.STMP.records import SpatialConfig
from algorithm.C_STMP_variance_em_20261025.iterations import run_spatial_score
from .denoiser import GaussianPriorDenoiser, GaussianSiteDenoiser


class Receiver:
    def __init__(self, binding, *, device='cpu'):
        self.binding = read_json(binding)
        b = self.binding
        if b['schema'] != 'c-stmp-gaussian-ablation-v1' or b['variant'] not in ('gaussian_prior', 'gaussian_evidence'):
            raise ValueError('Explicit Gaussian ablation binding required')
        path = ROOT / b['base_configuration']
        if sha256(path) != b['base_configuration_sha256']:
            raise ValueError('Frozen C-STMP configuration changed')
        self.configuration, self.checkpoints = verify(path)
        c = self.configuration
        self.controls = SpatialConfig(**c['ep'])
        self.variant = b['variant']
        self.device = device if self.variant == 'gaussian_evidence' else 'cpu'
        self.model = (ColoredMoments(ROOT/c['first_checkpoint'], device=self.device,
                      batch_size=c['batch_size'], **c['variance_estimator'])
                      if self.variant == 'gaussian_evidence' else None)
        self.last_trace = []

    def infer(self, inputs, *, observer=None):
        if not isinstance(inputs, ReceiverInput):
            raise TypeError('Public four-field ReceiverInput required')
        started = time.perf_counter()
        c = self.configuration
        noise, noise_record = estimate_spatial_noise(inputs.observation)
        current = ReceiverInput(inputs.observation, inputs.operator, noise, inputs.activity_prior)
        if self.model is None:
            self.denoiser = GaussianPriorDenoiser(
                variance=c['initialization']['normalized_training_second_moment'],
                activity_prior=inputs.activity_prior, controls=self.controls)
        else:
            self.model.reset()
            self.denoiser = GaussianSiteDenoiser(self.model, None, activity_prior=inputs.activity_prior,
                conditional_variance_floor=c['conditional_variance_floor_checkpoint_normalized'],
                raw_site_residual_tolerance=self.controls.raw_site_residual_tolerance,
                activity_weight_residual_tolerance=self.controls.activity_weight_residual_tolerance,
                activity_stopping_reference=self.controls.activity_stopping_reference)
        before = self.model.network_samples if self.model is not None else 0
        result = run_spatial_score(current, self.denoiser, scale=c['scale'],
            initial_variance=inputs.activity_prior*c['initialization']['normalized_training_second_moment'],
            config=self.controls, observer=observer, decision_threshold=c['decision_threshold'],
            adapt=c['query_variance_update']['enabled'])
        self.last_trace = list(result.trace)
        if self.device == 'cuda':
            torch.cuda.synchronize()
        arrays = dict(estimate=result.estimate, conditional_matrix=result.conditional_matrix,
            probabilities=result.probabilities, activity_decision=result.probabilities >= c['decision_threshold'],
            spatial_covariance=result.spatial_covariance, noise_variance_estimate=np.asarray(noise))
        record = dict(status='COMPLETE', method='C-STMP', ablation=self.variant,
            binding=self.binding, configuration=c, actual_iteration_controls=asdict(self.controls),
            checkpoint_sha256=self.checkpoints, device=self.device,
            iterations=len(result.trace), converged=result.stopping_reason == 'CONVERGED',
            stopping_reason=result.stopping_reason, seconds=time.perf_counter()-started,
            first_network_samples=0 if self.model is None else self.model.network_samples-before,
            first_network_loaded=self.model is not None, classifier_loaded=False, classifier_calls=0,
            receiver_truth_used=False, noise_truth_used=False, noise_estimation=noise_record,
            phase_mode='known', supplied_phase_operator_used=True, trace=self.last_trace,
            gaussian_prior_variance=(c['initialization']['normalized_training_second_moment']
                                     if self.model is None else None),
            query_variance_update=c['query_variance_update'],
            limitations=['Gaussian-site evidence is a message approximation, not the learned-prior marginal likelihood.',
                         'The isotropic Gaussian prior removes correlation and non-Gaussian structure together.'])
        return arrays, record
