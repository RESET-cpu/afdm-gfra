"""STMP with identical inference and reduced repeated execution overhead.

Known phase/noise handling is inherited unchanged; the unknown-phase path
uses the separately verified feedback rotation and fresh linear query.
"""
from copy import deepcopy
from dataclasses import replace
from dataclasses import asdict
import numpy as np
from fileio import sha256
from receiver.stmp import runtime_initialization as phase_initialization
from receiver.stmp.runtime_moments import GraphedMoments
from channel.unknown_phase import UnknownPhaseInput
from receiver.stmp.phase import PhaseSTMPReceiver as LegacyPhaseSTMPReceiver
from receiver.stmp.denoiser import Denoiser
from receiver.stmp import phase_supported_hypotheses_iterations


class PhaseSTMPReceiver(LegacyPhaseSTMPReceiver):
    def __init__(self, configuration, *, phase_configuration, device="auto", noise_mode="estimated"):
        super().__init__(configuration, phase_configuration=phase_configuration,
                         device=device, noise_mode=noise_mode)
        if self.phase_configuration.get("state_update") != "feedback_and_new_query":
            raise ValueError("Expected the validated feedback rotation and fresh-query configuration")
        if self.phase_configuration.get("initialization_candidates") != "original_directional_maximum":
            raise ValueError("Expected unchanged original observation-only initialization")
        if self.phase_configuration.get("phase_update_requires_stable_current_output") is not True:
            raise ValueError("Expected stable current outputs before phase updates")
        minimum = self.phase_configuration.get("minimum_conditional_iterations", self.base.controls.min_iterations)
        if type(minimum) is not int or not 1 <= minimum <= self.base.controls.iterations:
            raise ValueError("Valid minimum conditional iterations required")
        # This phase-specific limit does not alter the known-phase base receiver.
        self.unknown_controls = replace(self.base.controls, min_iterations=minimum)
        self.base.model = GraphedMoments(self.base.model)

    def release_runtime_cache(self):
        """Release captured GPU storage before the evaluator offloads weights."""
        model = self.base.model
        model.graph = None
        for name in ('static_x', 'static_v', 'static_first', 'static_second'):
            if hasattr(model, name):
                setattr(model, name, None)

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

        result, beta, steps, hypothesis_checks = phase_supported_hypotheses_iterations.infer(inputs, denoiser, scale=c["scale"],
            initial_variance=inputs.activity_prior * c["initialization"]["normalized_training_second_moment"],
            controls=self.unknown_controls, phase_configuration=self.phase_configuration,
            initial_slopes=initial["phase_slopes"], observer=observe,
            training_moment=self._moment(inputs.observation.shape[2]*inputs.pilot.shape[2])/c["scale"]**2,
            reference_power=c["initialization"]["normalized_training_second_moment"],
            decision_threshold=c["decision_threshold"])
        base.last_trace = list(result.trace)
        self.last_phase_steps = steps
        samples = base.model.samples - before[0]
        probe_samples = sum(check["neural_query_count"] for check in hypothesis_checks)
        if samples != sum(row["moment_samples"] for row in result.trace) + probe_samples:
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
            stopping_reason=result.stopping_reason, phase_mode="estimated", phase_method="gaussian_refinement_and_active_candidate_phase_hypotheses",
            phase_configuration=deepcopy(self.phase_configuration), phase_config_sha256=sha256(self.phase_path),
            phase_initialization=initialization, phase_initialization_seconds=initialization["seconds"],
            phase_updates=len(steps), phase_update_seconds=sum(s["seconds"] for s in steps),
            steps=steps, phase_hypothesis_checks=hypothesis_checks,
            phase_hypothesis_seconds=sum(check["seconds"] for check in hypothesis_checks),
            phase_hypothesis_samples=probe_samples,
            conditional_iteration_seconds=result.iteration_seconds,
            setup_seconds=result.setup_seconds,
            first_score_calls=base.model.first_calls-before[1],
            second_score_calls=base.model.second_calls-before[2], first_score_samples=samples,
            second_score_samples=samples, classifier_calls=denoiser.classifier_calls+sum(check["neural_query_count"]>0 for check in hypothesis_checks),
            classifier_samples=denoiser.classifier_samples+probe_samples,
            unsupported_user_queries=sum(r["unsupported_users"] for r in result.trace),
            phase_grid_used=False, repeated_complete_receiver_passes=0,
            activity_probability_routing=True, hard_activity_gating=False, candidate_activity_decision_required=True, global_neural_descent_claim=False,
            feedback_phase_absorbed=True, cached_queries_rotated=False,
            query_history_reset_after_phase=True,
            objective_scope="Ordinary Gaussian refinement has fixed-message descent; activity-based phase hypotheses use an explicitly approximate local query evidence, not a whole-receiver likelihood guarantee")
        record["configuration"]["ep"] = asdict(self.unknown_controls)
        return arrays, record
