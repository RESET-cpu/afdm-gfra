"""Three-network STMP with optional internal phase estimation from raw pilots."""
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
import time

import numpy as np
import torch

from workspace import ROOT
from fileio import read_json
from fileio import sha256
from channel.observation import ReceiverInput
from receiver.frontend.noise_estimation import estimate_spatial_noise
from channel.unknown_phase import UnknownPhaseInput
from receiver.du import phase_initialization
from receiver.stmp.denoiser import Denoiser
from receiver.stmp.receiver import Receiver
from receiver.stmp import phase_iterations


class PhaseSTMPReceiver:
    def __init__(self, configuration, *, phase_configuration, device="auto", noise_mode="estimated"):
        if noise_mode not in ("known", "estimated"):
            raise ValueError("noise_mode must be known or estimated")
        self.base = Receiver(configuration, device=device)
        self.configuration, self.device = self.base.configuration, self.base.device
        self.noise_mode = noise_mode
        self.phase_path = Path(phase_configuration)
        self.phase_configuration = read_json(self.phase_path)
        p = self.phase_configuration
        if (p["method"] != "message_gem" or p["initializer"] != "directional_coordinate"
                or p["initialization"] != dict(coordinate_sweeps=3, local_maxiter=40, joint_maxiter=500)
                or p["phase_update"] != dict(minimum_sweeps=2, maximum_sweeps=10, relative_tolerance=1e-7)):
            raise ValueError("Phase settings must match the reused, verified numerical solver")
        if p["training_source_sha256"] != configuration["initialization"]["training_sha256"]:
            raise ValueError("Phase initialization must use the same STMP training population")
        self.phase_moment = None
        self.last_phase_steps = []

    def _moment(self, dimension):
        if self.phase_moment is None:
            p = self.phase_configuration
            path = ROOT / p["training_second_moment"]
            if sha256(path) != p["training_second_moment_sha256"]:
                raise ValueError("Training second moment changed")
            with np.load(path, allow_pickle=False) as saved:
                self.phase_moment = np.array(saved["second_moment"], copy=True)
        if self.phase_moment.shape != (dimension, dimension):
            raise ValueError("Phase initialization moment and channel dimensions differ")
        return self.phase_moment

    def infer(self, inputs, *, observer=None):
        if not isinstance(inputs, (ReceiverInput, UnknownPhaseInput)):
            raise TypeError("ReceiverInput or raw-pilot UnknownPhaseInput required")
        started = time.perf_counter()
        if self.noise_mode == "estimated":
            noise, noise_record = estimate_spatial_noise(inputs.observation)
        else:
            noise = float(inputs.noise_variance)
            noise_record = dict(source="supplied_noise_variance", noise_variance=noise)
        selected = replace(inputs, noise_variance=noise)
        noise_seconds = time.perf_counter() - started
        if isinstance(selected, ReceiverInput):
            # Exact old conditional path: phase initialization and fitting are bypassed.
            arrays, record = self.base.infer(selected, observer=observer)
            record = dict(record, phase_mode="known", phase_updates=0)
            self.last_phase_steps = []
        else:
            arrays, record = self._unknown_phase(selected, observer)
        if self.device == "cuda":
            torch.cuda.synchronize()
        arrays["noise_variance_estimate"] = np.asarray(noise)
        record.update(seconds=time.perf_counter() - started, noise_seconds=noise_seconds,
            noise_mode=self.noise_mode, noise_estimation=noise_record,
            supplied_noise_variance_used=self.noise_mode == "known",
            noise_truth_used=self.noise_mode == "known",
            phase_truth_used=isinstance(selected, ReceiverInput),
            supplied_phase_operator_used=isinstance(selected, ReceiverInput),
            truth_used_in_inference=self.noise_mode == "known" or isinstance(selected, ReceiverInput))
        return arrays, record

    def _unknown_phase(self, inputs, observer):
        if inputs.observation.shape[1:] != (16, 16) or inputs.pilot.shape[-1] != 16:
            raise ValueError("STMP requires 16 antennas and a 16 by 16 channel")
        initial, initialization = phase_initialization.estimate(inputs.observation,
            inputs.pilot, inputs.noise_variance,
            self._moment(inputs.observation.shape[2] * inputs.pilot.shape[2]), inputs.activity_prior)
        c, base = self.configuration, self.base
        floor = c["conditional_variance_floor_checkpoint_normalized"] / base.model.scale_ratio**2
        denoiser = Denoiser(base.model, base.evidence, activity_prior=inputs.activity_prior,
            conditional_variance_floor=floor,
            raw_site_residual_tolerance=base.controls.raw_site_residual_tolerance,
            activity_weight_residual_tolerance=base.controls.activity_weight_residual_tolerance,
            activity_stopping_reference=base.controls.activity_stopping_reference,
            conditional_mean_projection=c.get("conditional_mean_projection", "none"))
        base.denoiser = denoiser
        base.last_trace, self.last_phase_steps = [], []
        before = base.model.samples, base.model.first_calls, base.model.second_calls

        def observe(row, *state):
            base.last_trace.append(row)
            if observer is not None:
                observer(row, *state)

        result, beta, steps = phase_iterations.infer(inputs, denoiser, scale=c["scale"],
            initial_variance=inputs.activity_prior * c["initialization"]["normalized_training_second_moment"],
            controls=base.controls, phase_configuration=self.phase_configuration,
            initial_slopes=initial["phase_slopes"], observer=observe,
            decision_threshold=c["decision_threshold"])
        base.last_trace = list(result.trace)
        self.last_phase_steps = steps
        samples = base.model.samples - before[0]
        if samples != sum(row["moment_samples"] for row in result.trace):
            raise AssertionError("Score sample counts differ from the completed iteration trace")
        initialization["initializer"].pop("coordinates", None)
        arrays = dict(estimate=result.estimate, conditional_matrix=result.conditional_matrix,
            probabilities=result.probabilities, activity_decision=result.probabilities >= c["decision_threshold"],
            spatial_covariance=result.spatial_covariance, phase_slopes=beta,
            phase=np.exp(1j * np.arange(len(inputs.pilot))[:, None] * beta),
            initial_phase_slopes=initial["phase_slopes"])
        record = base.context()
        record.pop("failed_denoiser_diagnostics")
        record.update(status="COMPLETE", configuration=dict(deepcopy(c), device=self.device,
            activity_prior=float(inputs.activity_prior)), input_fields=list(UnknownPhaseInput.__dataclass_fields__),
            iterations=len(result.trace), converged=result.stopping_reason == "CONVERGED",
            stopping_reason=result.stopping_reason, phase_mode="estimated", phase_method="message_gem",
            phase_configuration=deepcopy(self.phase_configuration), phase_config_sha256=sha256(self.phase_path),
            phase_initialization=initialization, phase_initialization_seconds=initialization["seconds"],
            phase_updates=len(steps), phase_update_seconds=sum(s["seconds"] for s in steps),
            steps=steps, conditional_iteration_seconds=result.iteration_seconds,
            setup_seconds=result.setup_seconds,
            first_score_calls=base.model.first_calls-before[1],
            second_score_calls=base.model.second_calls-before[2], first_score_samples=samples,
            second_score_samples=samples, classifier_calls=denoiser.classifier_calls,
            classifier_samples=denoiser.classifier_samples,
            unsupported_user_queries=sum(r["unsupported_users"] for r in result.trace),
            phase_grid_used=False, repeated_complete_receiver_passes=0,
            activity_probability_routing=False, global_neural_descent_claim=False,
            objective_scope="Fixed isotropic Gaussian feedback message only; neural iterations need not share a global objective")
        return arrays, record
