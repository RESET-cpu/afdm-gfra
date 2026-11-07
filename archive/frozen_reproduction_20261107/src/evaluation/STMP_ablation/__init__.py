"""Isolated ablation; the public receiver and frozen configuration are unchanged."""
from algorithm.STMP.noise import EstimatedNoiseSTMPReceiver
from .receiver import Receiver


class GaussianSiteReceiver(EstimatedNoiseSTMPReceiver):
    def __init__(self, configuration, *, device="cpu"):
        self.base = Receiver(configuration, device=device)
        self.configuration = self.base.configuration
        self.device = self.base.device
