"""Independent bindings; reuse the existing Gaussian evidence and inference loops.

Original STMP means its score-pair/Gaussian-evidence design adapted to the
same AFDM observation model, with the saved main-SNR numerical controls.
It is not a claim to reproduce Cai's different physical system verbatim.
"""
from copy import deepcopy
import time

import numpy as np
import torch

from project import ROOT
from utils import read_json
from system.observation import ReceiverInput
from system.receiver.noise_estimation import estimate_spatial_noise
from algorithm.STMP.runtime_moments import GraphedMoments
from evaluation.STMP_ablation.receiver import Receiver as GaussianSTMP
from algorithm.C_STMP_ablation_20261028.receiver import Receiver as GaussianGPMP
from algorithm.C_STMP.moments import ColoredMoments
from algorithm.STMP.records import SpatialConfig
from evaluation.white_matched_20261105.receiver import verify as verify_white


class OriginalSTMP(GaussianSTMP):
    def __init__(self, configuration, *, device='cuda'):
        c = read_json(configuration) if isinstance(configuration, str) else deepcopy(configuration)
        super().__init__(c, device=device)
        # The saved STMP comparator uses this already validated graph adapter.
        self.model = GraphedMoments(self.model)

    def infer(self, inputs, *, observer=None):
        if not isinstance(inputs, ReceiverInput):
            raise TypeError('Four-field public input required')
        began = time.perf_counter()
        noise, noise_record = estimate_spatial_noise(inputs.observation)
        selected = ReceiverInput(inputs.observation, inputs.operator, noise, inputs.activity_prior)
        arrays, record = super().infer(selected, observer=observer)
        if self.device == 'cuda':
            torch.cuda.synchronize()
        arrays['noise_variance_estimate'] = np.asarray(noise)
        record.update(method='STMP-original', seconds=time.perf_counter()-began,
                      activity_evidence='gaussian_site', classifier_loaded=False,
                      receiver_truth_used=False, noise_truth_used=False,
                      noise_mode='estimated', phase_mode='known', oracle_phase_supplied=True,
                      noise_estimation=noise_record,
                      adaptation='Original score-pair and Gaussian activity evidence on the shared AFDM model; saved main-SNR controls.')
        assert record['classifier_calls'] == 0
        return arrays, record


class WhiteGaussianGPMP(GaussianGPMP):
    def __init__(self, configuration, *, device='cuda'):
        # Verify the actual completed white teacher and its companion binding.
        # The classifier is inspected for provenance, never instantiated or queried.
        self.configuration, self.checkpoints = verify_white(configuration)
        c = self.configuration
        self.binding = dict(variant='gaussian_evidence', base_configuration=configuration,
                            training_noise='white Gaussian')
        self.controls = SpatialConfig(**c['ep'])
        self.variant, self.device = 'gaussian_evidence', device
        self.model = ColoredMoments(ROOT/c['first_checkpoint'], device=device,
                                   batch_size=c['batch_size'], **c['variance_estimator'])
        self.last_trace = []

    def infer(self, inputs, *, observer=None):
        arrays, record = super().infer(inputs, observer=observer)
        record.update(method='GP-MP-Gaussian', denoiser_training_noise='white Gaussian',
                      phase_mode='known', noise_mode='estimated', oracle_phase_supplied=True,
                      activity_evidence='gaussian_site',
                      limitations=['Gaussian-site evidence is a message approximation, not the learned-prior marginal likelihood.'])
        return arrays, record
