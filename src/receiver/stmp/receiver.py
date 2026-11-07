"""Load the selected networks, run the proposed receiver, and save its outputs.

The numerical iteration is in iterations.py; this module handles configuration,
checkpoint identity, timing, and files. Truth is read by the separate evaluator.
"""

from copy import deepcopy
from pathlib import Path
import time
import warnings

import numpy as np
import torch

from workspace import ROOT
from channel.observation import ReceiverInput
from channel.observation import load_input
from fileio import sha256
from fileio import write_json
from receiver.stmp.iterations import run_spatial_score
from receiver.stmp.moments import FullChannelMoments
from receiver.stmp.records import SpatialConfig
from receiver.stmp.activity import FrozenEvidence
from receiver.stmp.configuration import METHOD
from receiver.stmp.configuration import verify
from receiver.stmp.denoiser import Denoiser


class Receiver:
    def __init__(self, configuration, *, device="auto"):
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
        self.evidence = FrozenEvidence(ROOT / c["evidence_checkpoint"], device=self.device)
        self.last_trace, self.denoiser = [], None

    def context(self):
        return dict(
            method=METHOD,
            activity_evidence=self.configuration["activity_evidence"],
            classifier_loaded=self.configuration["activity_evidence"] == "classifier",
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
        effective.update(device=self.device, activity_prior=float(inputs.activity_prior))
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

    def run(self, input_path, output_path, *, observer=None):
        output = Path(output_path)
        paths = (output, output.with_suffix(".json"), output.with_suffix(".warnings.json"))
        if output.suffix != ".npz" or any(path.exists() for path in paths):
            raise ValueError("Fresh native .npz output required; existing attempts are preserved")
        output.parent.mkdir(parents=True, exist_ok=True)
        caught = []
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always", RuntimeWarning)
                arrays, record = self.infer(load_input(input_path), observer=observer)
                if not all(np.isfinite(a).all() for a in arrays.values()):
                    raise FloatingPointError("Nonfinite native output")
            np.savez_compressed(output, **arrays)
            record.update(input_sha256=sha256(input_path), output_sha256=sha256(output))
            write_json(output.with_suffix(".json"), record)
            return record
        except BaseException as error:
            record = self.context()
            record.update(
                status="FAILED",
                error=repr(error),
                input_sha256=sha256(input_path) if Path(input_path).is_file() else None,
            )
            write_json(output.with_suffix(".json"), record)
            raise
        finally:
            write_json(
                output.with_suffix(".warnings.json"),
                [
                    dict(
                        category=w.category.__name__,
                        message=str(w.message),
                        filename=w.filename,
                        lineno=w.lineno,
                    )
                    for w in caught
                ],
            )
