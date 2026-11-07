"""Independent C-STMP variant; only the variance estimator is replaced."""
import time
import numpy as np
import torch

from project import ROOT
from system.observation import ReceiverInput
from system.receiver.noise_estimation import estimate_spatial_noise
from algorithm.STMP.receiver import Receiver as ScalarReceiver
from algorithm.STMP.activity import FrozenEvidence
from algorithm.STMP.records import SpatialConfig
from .second_configuration import verify
from .second_moments import LearnedSecondMoments


class Receiver(ScalarReceiver):
    def __init__(self, configuration, *, device='auto', noise_mode='estimated'):
        if noise_mode not in ('known', 'estimated'):
            raise ValueError('noise_mode must be known or estimated')
        self.configuration, self.checkpoints = verify(configuration)
        self.device = ('cuda' if torch.cuda.is_available() else 'cpu') if device == 'auto' else device
        self.noise_mode = noise_mode
        c = self.configuration
        self.controls = SpatialConfig(**c['ep'])
        self.model = LearnedSecondMoments(ROOT/c['first_checkpoint'], ROOT/c['second_checkpoint'],
            first_sha256=c['first_checkpoint_sha256'], device=self.device, batch_size=c['batch_size'])
        self.evidence = FrozenEvidence(ROOT/c['evidence_checkpoint'], device=self.device)
        self.last_trace, self.denoiser = [], None

    def context(self):
        record = super().context()
        record.update(method='C-STMP', classifier_policy='frozen_legacy_teacher',
                      classifier_retrained=False, query_covariance='vI',
                      variance_source='learned_second_score_trace', full_D_GEC=False,
                      second_network_loaded=True)
        return record

    def infer(self, inputs, *, observer=None):
        if not isinstance(inputs, ReceiverInput):
            raise TypeError('C-STMP requires the public four-field ReceiverInput')
        started = time.perf_counter()
        if self.noise_mode == 'estimated':
            noise, noise_record = estimate_spatial_noise(inputs.observation)
        else:
            noise = inputs.noise_variance
            noise_record = dict(source='supplied_noise_variance', noise_variance=float(noise))
        current = ReceiverInput(inputs.observation, inputs.operator, noise, inputs.activity_prior)
        self.model.reset()
        before = self.model.network_samples, self.model.second_network_samples
        arrays, record = super().infer(current, observer=observer)
        if self.device == 'cuda':
            torch.cuda.synchronize()
        record.update(seconds=time.perf_counter()-started, noise_mode=self.noise_mode,
                      noise_estimation=noise_record, first_mean_samples=record['first_score_samples'],
                      first_network_samples=self.model.network_samples-before[0],
                      second_network_samples=self.model.second_network_samples-before[1],
                      first_output='conditional_mean', first_epoch=self.configuration['first_epoch'],
                      second_epoch=self.configuration['second_epoch'],
                      phase_mode='supplied_operator', channel_truth_loaded=False,
                      supplied_phase_operator_used=True, noise_truth_used=self.noise_mode == 'known')
        arrays['noise_variance_estimate'] = np.asarray(noise)
        return arrays, record
