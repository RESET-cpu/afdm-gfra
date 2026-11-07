"""Reject a nonpositive pooled derivative trace instead of making it precise.

The original denoiser already retains its previous positive Gaussian site when
tau/v >= 1. The adapter uses tau=2v solely to select that rejection branch;
it is NOT a replacement uncertainty estimate. Diagnostics restore the actual
network trace. Activity continues to use the same unchanged neural mean.
"""
import numpy as np

from algorithm.STMP.denoiser import Denoiser
from algorithm.STMP.moments import MatrixMomentEstimate


class _RejectNonpositive:
    def __init__(self, model):
        self.wrapped = model
        self.raw = None
        self.rejected = False

    def __getattr__(self, name):
        return getattr(self.wrapped, name)

    def infer(self, query, variance):
        moment = self.wrapped.infer(query, variance)
        self.raw = np.asarray(moment.variance, float).copy()
        # Leave invalid shapes/nonfinite values to the original strict validation.
        self.rejected = bool(self.raw.shape == (len(query),)
            and np.isfinite(self.raw).all() and self.raw.mean() <= 0)
        # Stay strictly above the boundary: averaging K copies of v can round
        # below v, incorrectly making tau/v < 1 (observed for K=40).
        return (MatrixMomentEstimate(moment.mean, 2*np.asarray(variance, float))
                if self.rejected else moment)


class GuardedDenoiser(Denoiser):
    def __init__(self, model, evidence, **kwargs):
        super().__init__(_RejectNonpositive(model), evidence, **kwargs)

    def __call__(self, query, covariance):
        self.model.raw, self.model.rejected = None, False
        state = super().__call__(query, covariance)
        rejected = self.model.rejected
        self.last.update(nonpositive_pooled_variance_rejected=rejected,
                         variance_policy='retain_site_for_nonpositive_pooled_trace')
        if rejected:
            raw = self.model.raw
            if self.last['site_accepted']:
                raise AssertionError('Nonpositive pooled trace must not update the site')
            self.last.update(raw_pooled_variance=float(raw.mean()),
                raw_variance_min=float(raw.min()), raw_variance_max=float(raw.max()),
                raw_negative_variances=int(np.count_nonzero(raw <= 0)),
                second_raw_per_user=raw.tolist(), conditional_variance_floored=False,
                conditional_variance_fraction=None,
                site_rejection_reason='nonpositive_pooled_derivative_trace')
            self.snapshot['raw_network_variance'] = raw.copy()
        return state
