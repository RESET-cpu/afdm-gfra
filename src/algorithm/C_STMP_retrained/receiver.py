"""Reuse the C-STMP inference equations; bind only the new activity classifier."""
import torch
from project import ROOT
from algorithm.C_STMP.receiver import Receiver as PreviousReceiver
from algorithm.C_STMP.moments import ColoredMoments
from algorithm.STMP.activity import FrozenEvidence
from algorithm.STMP.records import SpatialConfig
from .configuration import verify


class Receiver(PreviousReceiver):
    def __init__(self,configuration,*,device='auto',noise_mode='estimated'):
        if noise_mode not in ('known','estimated'):
            raise ValueError('noise_mode must be known or estimated')
        self.configuration,self.checkpoints=verify(configuration)
        self.device=('cuda' if torch.cuda.is_available() else 'cpu') if device=='auto' else device
        self.noise_mode=noise_mode
        c=self.configuration
        self.controls=SpatialConfig(**c['ep'])
        self.model=ColoredMoments(ROOT/c['first_checkpoint'],device=self.device,
                                 batch_size=c['batch_size'],**c['variance_estimator'])
        self.evidence=FrozenEvidence(ROOT/c['evidence_checkpoint'],device=self.device)
        self.last_trace,self.denoiser=[],None

    def context(self):
        record=super().context()
        record.update(classifier_policy=self.configuration['classifier_policy'],classifier_retrained=True,
            classifier_epoch=self.configuration['classifier_epoch'],classifier_training_epochs=100,
            classifier_training_first_sha256=self.evidence.first_sha256,
            classifier_initialization='random',classifier_training_covariance='vI')
        return record
