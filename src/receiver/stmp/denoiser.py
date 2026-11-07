"""Full-channel score conditional moments and learned activity probabilities."""

import time

import numpy as np
from scipy.special import expit
from scipy.special import logit

from receiver.stmp.posterior import full_posterior
from receiver.stmp.records import SpatialConfig
from receiver.stmp.records import SpatialMoments
from receiver.stmp.rank_one import rank_one_spatial_mean


class Denoiser:
    def __init__(
        self,
        moments,
        evidence,
        *,
        activity_prior,
        conditional_variance_floor,
        raw_site_residual_tolerance=1e-4,
        activity_weight_residual_tolerance=1e-4,
        activity_stopping_reference="smoothed",
        conditional_mean_projection="none",
    ):
        if not np.isfinite(conditional_variance_floor) or conditional_variance_floor <= 0:
            raise ValueError("positive finite conditional variance floor required")
        self.model, self.activity_prior = moments, activity_prior
        self.conditional_variance_floor = conditional_variance_floor
        if conditional_mean_projection not in ("none", "rank_one"):
            raise ValueError("conditional_mean_projection must be none or rank_one")
        self.conditional_mean_projection = conditional_mean_projection
        self.site_mean = self.site_variance = self.mass = None
        self.message_fresh = False
        self.last, self.snapshot = {}, {}
        SpatialConfig(
            raw_site_residual_tolerance=raw_site_residual_tolerance,
            activity_weight_residual_tolerance=activity_weight_residual_tolerance,
            activity_stopping_reference=activity_stopping_reference,
        ).validate_stopping()
        self.raw_site_residual_tolerance = raw_site_residual_tolerance
        self.activity_weight_residual_tolerance = activity_weight_residual_tolerance
        self.activity_stopping_reference = activity_stopping_reference
        self.previous_activity = None
        if (
            evidence is None
            or tuple(moments.noise_support) != tuple(evidence.noise_support)
            or evidence.training_class_prior != 0.5
        ):
            raise ValueError("Same-query support and balanced classifier required")
        self.evidence = evidence
        self.classifier_calls = self.classifier_samples = 0
        self.classifier_seconds = 0.0
        self.activity_evidence_calls = self.activity_evidence_samples = 0
        self.activity_evidence_seconds = 0.0

    def message_is_fresh(self, accepted, residual, weight_change):
        """Inspect the current site and the configured probability residual."""
        return bool(
            accepted
            and residual is not None
            and residual < self.raw_site_residual_tolerance
            and weight_change is not None
            and weight_change < self.activity_weight_residual_tolerance
        )

    def __call__(self, r, cov):
        """Map the current query to active-channel and activity-weighted moments.

        See THEORY.md T12–T16: shared conditional variance, Gaussian site,
        classifier likelihood ratio, then Bernoulli–Gaussian moments.
        """
        started = time.perf_counter()
        k, m, nr, nc = r.shape
        v = float(np.trace(cov).real / m)
        self.message_fresh = False
        self.last = dict(
            failure_phase="cavity_validation",
            update_completed=False,
            query_variance_min=v,
            query_variance_max=v,
        )
        if (
            v <= 0
            or not np.isfinite(v)
            or not np.isfinite(r).all()
            or not np.allclose(cov, v * np.eye(m), rtol=1e-10, atol=1e-12 * v)
        ):
            raise ValueError("Finite isotropic cavity required")
        if self.site_mean is None:
            self.site_mean = np.zeros_like(r)
            self.site_variance = np.ones(k)
            self.mass = np.full(k, self.activity_prior)
        # Retain the previous Gaussian site until a positive-precision update is accepted.
        e, c, w = self.site_mean.copy(), self.site_variance.copy(), self.mass.copy()
        precision, natural = 1 / c, e / c[:, None, None, None]
        new_precision, new_natural = precision.copy(), natural.copy()
        supported = self.model.noise_support[0] <= v <= self.model.noise_support[1]
        accepted = floored = False
        fraction = raw_tau = None
        full_mean = np.full_like(r, np.nan)
        feedback_mean = full_mean
        projection_seconds = 0.0
        raw, logits = np.full(k, np.nan), np.full(k, np.nan)
        before = self.model.samples
        score_started = time.perf_counter()
        # Conditional mean and pooled variance from the two scores (T12–T13).
        if supported:
            self.last.update(failure_phase="score_moments", supported=True)
            moment = self.model.infer(r, np.full(k, v))
            full_mean, raw = np.asarray(moment.mean, complex), np.asarray(moment.variance, float)
            if (
                full_mean.shape != r.shape
                or raw.shape != (k,)
                or not all(np.isfinite(a).all() for a in (full_mean, raw))
            ):
                raise FloatingPointError("Nonfinite/mismatched full-score moments")
            feedback_mean = full_mean
            raw_tau = float(raw.mean())
            tau = max(raw_tau, self.conditional_variance_floor)
            floored = raw_tau < self.conditional_variance_floor
            if not np.isfinite(tau) or tau <= 0:
                raise FloatingPointError("Invalid pooled conditional variance")
            fraction = tau / v
            if fraction < 1:
                accepted = True
                if self.conditional_mean_projection == "rank_one":
                    projection_started = time.perf_counter()
                    feedback_mean = rank_one_spatial_mean(full_mean)
                    projection_seconds = time.perf_counter() - projection_started
                # The old second-network variance is deliberately retained for
                # this controlled comparison; it is not calibrated to this mean.
                new_precision[:] = 1 / tau - 1 / v
                new_natural = feedback_mean / tau - r / v
        score_seconds = time.perf_counter() - score_started
        if self.model.samples - before != (k if supported else 0):
            raise AssertionError("Exactly one same-query score pair required")

        # Activity uses the same current query and score mean, including when
        # the Gaussian site was retained rather than updated (T15).
        evidence_seconds = classifier_seconds = 0.0
        use_evidence = use_classifier = supported
        if use_evidence:
            self.last["failure_phase"] = "classifier" if use_classifier else "activity_evidence"
            evidence_started = time.perf_counter()
            self.activity_evidence_calls += 1
            self.activity_evidence_samples += k
            if use_classifier:
                self.classifier_calls += 1
                self.classifier_samples += k
            logits = np.asarray(self.evidence.infer(r, np.full(k, v), full_mean), float)
            evidence_seconds = time.perf_counter() - evidence_started
            self.activity_evidence_seconds += evidence_seconds
            if use_classifier:
                classifier_seconds = evidence_seconds
                self.classifier_seconds += classifier_seconds
            if logits.shape != (k,) or not np.isfinite(logits).all():
                raise FloatingPointError("Nonfinite/mismatched activity evidence")

        # Commit the Gaussian site and compute the activity-weighted moments (T16).
        dp = abs(new_precision - precision) / np.maximum(abs(new_precision), abs(precision))
        norm = lambda x: np.linalg.norm(x.reshape(k, -1), axis=1)
        dh = norm(new_natural - natural) / np.maximum(
            1.0, np.maximum(norm(new_natural), norm(natural))
        )
        residual = float(np.maximum(dp, dh).max()) if accepted else None
        self.site_variance = 1 / new_precision
        self.site_mean = new_natural / new_precision[:, None, None, None]
        self.last["failure_phase"] = "joint_moments"
        if use_evidence:
            ell = logits - logit(self.evidence.training_class_prior)
            probability = expit(logit(self.activity_prior) + ell)
            site_c = self.site_variance
            used_tau = site_c * v / (site_c + v)
            conditional = (site_c[:, None, None, None] * r + v * self.site_mean) / (site_c + v)[
                :, None, None, None
            ]
            flat = conditional.reshape(k, m, -1)
            gram = np.einsum("kmd,knd->kmn", flat, flat.conj(), optimize=False) / (nr * nc)
            conditional_cov = used_tau[:, None, None] * np.eye(m)
            covariance = (
                probability[:, None, None] * conditional_cov
                + (probability * (1 - probability))[:, None, None] * gram
            )
            state = SpatialMoments(
                probability[:, None, None, None] * conditional,
                conditional,
                probability,
                covariance,
                conditional_cov,
                ell,
                np.zeros(k),
                np.zeros(k),
            )
            source = "current_full_input_classifier"
        else:
            state = full_posterior(r, v, self.site_mean, self.site_variance, self.activity_prior)
            used_tau = np.trace(state.conditional_spatial_covariance, axis1=1, axis2=2).real / m
            source = "current_gaussian_site" if supported else "reused_gaussian_site_fallback"
        if not all(
            np.isfinite(a).all()
            for a in (
                state.mean,
                state.activity,
                state.spatial_covariance,
                state.conditional_mean,
                state.conditional_spatial_covariance,
                state.log_evidence_bound,
            )
        ):
            raise FloatingPointError("Invalid Bernoulli-Gaussian moments")
        # The running activity average is used only by the stopping check.
        weight_change = float(np.max(abs(state.activity - w)))
        self.mass = 0.8 * w + 0.2 * state.activity
        probability_change = (
            None
            if self.previous_activity is None
            else float(np.max(abs(state.activity - self.previous_activity)))
        )
        stopping_residual = (
            probability_change if self.activity_stopping_reference == "previous" else weight_change
        )
        self.message_fresh = self.message_is_fresh(accepted, residual, stopping_residual)
        self.previous_activity = state.activity.copy()
        # Diagnostics are recorded after the completed numerical update.
        self.last = dict(
            moment_samples=k if supported else 0,
            unsupported_users=0 if supported else k,
            rejected_site_users=k if supported and not accepted else 0,
            score_seconds=score_seconds,
            classifier_seconds=classifier_seconds,
            classifier_calls=int(use_classifier),
            classifier_samples=k if use_classifier else 0,
            activity_evidence_calls=int(use_evidence),
            activity_evidence_samples=k if use_evidence else 0,
            activity_evidence_seconds=evidence_seconds,
            prior_seconds=time.perf_counter() - started - score_seconds - evidence_seconds,
            raw_site_residual=residual,
            activity_weight_residual=weight_change,
            query_variance_min=v,
            query_variance_max=v,
            conditional_variance_fraction=fraction,
            raw_pooled_variance=raw_tau,
            conditional_variance_floor=self.conditional_variance_floor,
            conditional_variance_floored=floored,
            raw_variance_min=float(raw.min()) if supported else None,
            raw_variance_max=float(raw.max()) if supported else None,
            raw_negative_variances=int(np.count_nonzero(raw <= 0)),
            site_accepted=bool(accepted),
            full_mean_used=bool(accepted),
            reused_site=not accepted,
            probability_source=source,
            evidence_kind=source,
            saturated_probability_users=int(
                np.count_nonzero((state.activity == 0) | (state.activity == 1))
            ),
            second_raw_per_user=raw.tolist() if supported else None,
            classifier_logit_per_user=logits.tolist() if use_classifier else None,
            probabilities_per_user=state.activity.tolist(),
            used_conditional_variance_per_user=used_tau.tolist(),
            log_bayes_factor_min=float(state.log_evidence_bound.min()),
            log_bayes_factor_max=float(state.log_evidence_bound.max()),
            maximum_activity=float(state.activity.max()),
            update_completed=True,
        )
        if self.activity_stopping_reference == "previous":
            self.last.update(
                activity_stopping_reference="previous", activity_stopping_residual=stopping_residual
            )
        self.snapshot = dict(
            full_score_mean=full_mean,
            raw_network_variance=raw,
            classifier_logit=logits,
            site_mean=self.site_mean.copy(),
            site_variance=self.site_variance.copy(),
            used_conditional_mean=state.conditional_mean.copy(),
            log_evidence=state.log_evidence_bound.copy(),
            probability_source=source,
        )
        if self.conditional_mean_projection == "rank_one":
            self.last.update(
                conditional_mean_projection="rank_one",
                rank_one_projection_applied=bool(accepted),
                rank_one_projection_seconds=projection_seconds,
                classifier_mean="raw_full_score_mean",
                conditional_variance_policy="original_second_network",
            )
            self.snapshot["feedback_score_mean"] = feedback_mean
        return state
