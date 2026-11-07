"""Experiment-local receiver using Gaussian-site activity evidence.

The numerical iteration is in iterations.py; this module handles configuration,
checkpoint identity, timing, and files. Truth is read by the separate evaluator.
"""

from copy import deepcopy
import time

import torch

from project import ROOT
from system.observation import ReceiverInput
from algorithm.STMP.receiver import Receiver as STMPReceiver
from algorithm.STMP.iterations import run_spatial_score
from algorithm.STMP.moments import FullChannelMoments
from algorithm.STMP.records import SpatialConfig
from algorithm.STMP.configuration import METHOD, verify
from .denoiser import Denoiser


class Receiver(STMPReceiver):
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

    def infer(self, inputs, *, observer=None):
        if (
            not isinstance(inputs, ReceiverInput)
            or inputs.observation.shape[1:] != (16, 16)
            or inputs.operator.shape[-1] != 16
        ):
            raise ValueError("16-antenna/16x16 four-field input required")
        c = self.configuration
        floor = c["conditional_variance_floor_checkpoint_normalized"] / self.model.scale_ratio**2
        self.denoiser = Denoiser(
            self.model,
            self.evidence,
            activity_prior=inputs.activity_prior,
            conditional_variance_floor=floor,
            raw_site_residual_tolerance=self.controls.raw_site_residual_tolerance,
            activity_weight_residual_tolerance=self.controls.activity_weight_residual_tolerance,
            activity_stopping_reference=self.controls.activity_stopping_reference,
            conditional_mean_projection=c.get("conditional_mean_projection", "none"),
        )
        self.last_trace = []
        before = self.model.samples, self.model.first_calls, self.model.second_calls

        def observe(row, *state):
            self.last_trace.append(dict(row))
            if observer is not None:
                observer(row, *state)

        started = time.monotonic()
        result = run_spatial_score(
            inputs,
            self.denoiser,
            scale=c["scale"],
            initial_variance=inputs.activity_prior
            * c["initialization"]["normalized_training_second_moment"],
            config=self.controls,
            observer=observe,
            decision_threshold=c["decision_threshold"],
        )
        if self.device == "mps":
            torch.mps.synchronize()
        arrays = dict(
            estimate=result.estimate,
            conditional_matrix=result.conditional_matrix,
            probabilities=result.probabilities,
            activity_decision=result.probabilities >= c["decision_threshold"],
            spatial_covariance=result.spatial_covariance,
        )
        samples = self.model.samples - before[0]
        if samples != sum(row["moment_samples"] for row in self.last_trace):
            raise AssertionError("Score samples differ from completed native trace")
        record = self.context()
        record.pop("failed_denoiser_diagnostics")
        effective = deepcopy(c)
        effective.update(device=self.device, activity_prior=float(inputs.activity_prior), activity_evidence="gaussian_site")
        record.update(
            status="COMPLETE",
            configuration=effective,
            scale=c["scale"],
            iterations=len(self.last_trace),
            stopping_reason=result.stopping_reason,
            converged=result.stopping_reason == "CONVERGED",
            seconds=time.monotonic() - started,
            first_score_samples=samples,
            second_score_samples=samples,
            first_score_calls=self.model.first_calls - before[1],
            second_score_calls=self.model.second_calls - before[2],
            classifier_calls=self.denoiser.classifier_calls,
            classifier_samples=self.denoiser.classifier_samples,
            classifier_seconds=self.denoiser.classifier_seconds,
            activity_evidence_calls=self.denoiser.activity_evidence_calls,
            activity_evidence_samples=self.denoiser.activity_evidence_samples,
            activity_evidence_seconds=self.denoiser.activity_evidence_seconds,
            unified_activity_probability=True,
            conditional_variance_floor_receiver_normalized=floor,
            conditional_variance_floor_iterations=sum(
                row["conditional_variance_floored"] for row in self.last_trace
            ),
            supported_query_iterations=sum(row["moment_samples"] > 0 for row in self.last_trace),
            unsupported_user_queries=sum(row["unsupported_users"] for row in self.last_trace),
            rejected_user_queries=sum(row["rejected_site_users"] for row in self.last_trace),
            raw_nonpositive_variance_user_queries=sum(
                row["raw_negative_variances"] for row in self.last_trace
            ),
            accepted_site_iterations=sum(row["site_accepted"] for row in self.last_trace),
            reused_site_iterations=sum(row["reused_site"] for row in self.last_trace),
        )
        return arrays, record
