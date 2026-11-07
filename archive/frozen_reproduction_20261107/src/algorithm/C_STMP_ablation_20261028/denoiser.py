"""Analytic active Gaussian prior; Bernoulli activity is retained.

The learned-moment variant uses the existing Gaussian-site evidence adapter.
Both variants feed their own joint moments into the unchanged C-STMP loop.
"""
import time
import numpy as np

from algorithm.STMP.posterior import full_posterior
from evaluation.STMP_ablation.denoiser import Denoiser as GaussianSiteDenoiser


class GaussianPriorDenoiser:
    def __init__(self, *, variance, activity_prior, controls):
        if not np.isfinite(variance) or variance <= 0:
            raise ValueError('Positive training-population variance required')
        controls.validate_stopping()
        self.variance, self.activity_prior, self.controls = variance, activity_prior, controls
        self.mass = self.previous_activity = None
        self.message_fresh, self.last = False, {}

    def __call__(self, r, covariance):
        started = time.perf_counter()
        k, m = r.shape[:2]
        v = float(np.trace(covariance).real / m)
        if (not np.isfinite(r).all() or not np.isfinite(v) or v <= 0
                or not np.allclose(covariance, v*np.eye(m), rtol=1e-10, atol=1e-12*v)):
            raise ValueError('Finite scalar Gaussian query required')
        # e=0 and c=gamma are fixed prior parameters, not fitted posterior moments.
        state = full_posterior(r, v, np.zeros_like(r), np.full(k, self.variance), self.activity_prior)
        if self.mass is None:
            self.mass = np.full(k, self.activity_prior)
        weight_change = float(np.max(abs(state.activity-self.mass)))
        probability_change = (None if self.previous_activity is None else
                              float(np.max(abs(state.activity-self.previous_activity))))
        residual = probability_change if self.controls.activity_stopping_reference == 'previous' else weight_change
        self.message_fresh = bool(residual is not None and residual < self.controls.activity_weight_residual_tolerance)
        self.mass = .8*self.mass + .2*state.activity
        self.previous_activity = state.activity.copy()
        self.last = dict(moment_samples=0, classifier_calls=0, classifier_samples=0,
            score_seconds=0., classifier_seconds=0., prior_seconds=time.perf_counter()-started,
            raw_site_residual=0., activity_weight_residual=weight_change,
            probability_source='fixed_training_power_gaussian_prior',
            conditional_variance_fraction=self.variance/(self.variance+v),
            conditional_variance_floored=False, site_accepted=True, reused_site=False,
            probabilities_per_user=state.activity.tolist(),
            log_bayes_factor_min=float(state.log_evidence_bound.min()),
            log_bayes_factor_max=float(state.log_evidence_bound.max()), update_completed=True)
        return state
