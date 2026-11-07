"""Observation-only noise variance before unchanged conditional Proposed.

Uses the same spatial covariance MDL estimator already used by the baseline
frontends. No true activity, true channel, or supplied noise variance enters
the estimator. Three networks and all conditional inference settings remain
unchanged. See noise_estimation.py and docs/TERMINOLOGY.md for the estimator.
"""
from dataclasses import replace
import time
import numpy as np
from system.receiver.noise_estimation import estimate_spatial_noise
from algorithm.STMP.receiver import Receiver
from system.observation import ReceiverInput


class EstimatedNoiseSTMPReceiver:
    def __init__(self, configuration, *, device='auto'):
        self.base = Receiver(configuration, device=device)
        self.configuration = self.base.configuration
        self.device = self.base.device

    def infer(self, inputs, *, observer=None):
        if not isinstance(inputs, ReceiverInput):
            raise TypeError('Conditional ReceiverInput required')
        started = time.perf_counter()
        variance, noise_record = estimate_spatial_noise(inputs.observation)
        estimated = replace(inputs, noise_variance=variance)
        noise_seconds = time.perf_counter()-started
        arrays, record = self.base.infer(estimated, observer=observer)
        arrays = dict(arrays, noise_variance_estimate=np.asarray(variance))
        record = dict(record, noise_mode='estimated', supplied_noise_variance_used=False,
                      noise_variance_estimate=variance, noise_estimation=noise_record,
                      noise_seconds=noise_seconds, base_seconds=record['seconds'],
                      seconds=record['seconds']+noise_seconds,
                      truth_used_in_inference=False)
        return arrays, record
