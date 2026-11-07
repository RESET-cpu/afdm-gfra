"""Isolated ablation; the public receiver and frozen configuration are unchanged."""
from afdm_jadcedd.algorithm.proposed_noise_candidate import EstimatedNoiseProposedReceiver
from .receiver import Receiver


class GaussianSiteReceiver(EstimatedNoiseProposedReceiver):
    def __init__(self, configuration, *, device="cpu"):
        self.base = Receiver(configuration, device=device)
        self.configuration = self.base.configuration
        self.device = self.base.device
