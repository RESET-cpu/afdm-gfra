"""Experiment-local receiver using Gaussian-site activity evidence.

The numerical iteration is in iterations.py; this module handles configuration,
checkpoint identity, timing, and files. Truth is read by the separate evaluator.
"""

from copy import deepcopy

import torch

from workspace import ROOT
from channel.observation import ReceiverInput
from receiver.stmp.receiver import Receiver as STMPReceiver
from receiver.stmp.moments import FullChannelMoments
from receiver.stmp.records import SpatialConfig
from receiver.stmp.configuration import METHOD
from receiver.stmp.configuration import verify
from receiver.stmp_ablation.denoiser import Denoiser


class Receiver(STMPReceiver):
    denoiser_type = Denoiser

    def __init__(self, configuration, *, device="auto"):
        # Verify the same frozen bundle; classifier weights are never evaluated.
        self.configuration = deepcopy(configuration)
        self.checkpoints = verify(self.configuration)["checkpoint_sha256"]
        self.device = (
            ("mps" if torch.backends.mps.is_available() else "cpu") if device == "auto" else device
        )
        c = self.configuration
        self.controls = SpatialConfig(**c["ep"])
        self.model = FullChannelMoments(
            c["scale"],
            ROOT / c["first_checkpoint"],
            ROOT / c["second_checkpoint"],
            device=self.device,
            batch_size=c["batch_size"],
        )
        self.evidence = None
        self.last_trace, self.denoiser = [], None

    def context(self):
        return dict(
            method=METHOD,
            activity_evidence="gaussian_site",
            classifier_loaded=False,
            configuration=self.configuration,
            truth_loaded=False,
            array_response_loaded=False,
            input_fields=list(ReceiverInput.__dataclass_fields__),
            checkpoint_sha256=self.checkpoints,
            trace=list(self.last_trace),
            failed_denoiser_diagnostics={} if self.denoiser is None else self.denoiser.last,
        )

