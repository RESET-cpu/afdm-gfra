"""Cai et al., STMP-JADCE v2, III-B2, equation (30).

The author's archived implementation lambda_post_gaussian uses a zero-mean
Gaussian active site with variance var_h. That is a special case of (30), not
the learned channel extrinsic site in equations (26)-(27). All variances here
are complex variances. A packed real/imaginary tensor has 2*D coordinates.
"""
import math

import torch
from torch import nn


def gaussian_site_log_odds(query, query_variance, site_mean, site_variance, rho):
    """Return log prior odds plus log CN(r;e,(v+c)I)/CN(r;0,vI)."""
    if query.shape != site_mean.shape or query.ndim < 3 or query.shape[1] != 2:
        raise ValueError('Matching packed real/imaginary channel tensors required')
    if not 0 < rho < 1:
        raise ValueError('Activity prior must lie strictly between zero and one')
    r, e = query.double(), site_mean.double()
    v = torch.as_tensor(query_variance, dtype=r.dtype, device=r.device).expand(len(r))
    c = torch.as_tensor(site_variance, dtype=r.dtype, device=r.device).expand(len(r))
    if not bool(torch.isfinite(v).all() and torch.isfinite(c).all() and (v > 0).all() and (c > 0).all()):
        raise ValueError('Positive finite complex query/site variances required')
    dimension = r[0].numel() // 2
    energy = r.square().flatten(1).sum(1)
    # Algebraic expansion avoids subtracting nearly equal large energies.
    cross = (r * e).flatten(1).sum(1)
    mean_energy = e.square().flatten(1).sum(1)
    evidence = energy * c / (v * (v + c)) + (2 * cross - mean_energy) / (v + c)
    evidence -= dimension * torch.log1p(c / v)
    return math.log(rho / (1 - rho)) + evidence


def site_from_conditional_moments(query, query_variance, mean, conditional_variance):
    """Equations (26)-(27); reject invalid Gaussian extrinsic precision.

    conditional_variance must concern the active-channel conditional posterior.
    A residual variance of the activity-weighted estimate is not interchangeable.
    """
    if query.shape != mean.shape:
        raise ValueError('Matching query and conditional mean required')
    v = torch.as_tensor(query_variance, dtype=torch.float64, device=query.device).expand(len(query))
    tau = torch.as_tensor(conditional_variance, dtype=torch.float64, device=query.device).expand(len(query))
    if not bool(torch.isfinite(v).all() and torch.isfinite(tau).all() and (tau > 0).all() and (tau < v).all()):
        raise ValueError('Conditional variance must give positive extrinsic precision: 0 < tau < v')
    c = tau * v / (v - tau)
    shape = (-1,) + (1,) * (query.ndim - 1)
    e = (v.reshape(shape) * mean.double() - tau.reshape(shape) * query.double()) / (v - tau).reshape(shape)
    return e, c


class GaussianPriorActivity(nn.Module):
    """Activity rule actually used by Cai's published code; no trained weights."""
    def __init__(self, active_prior_power):
        super().__init__()
        if not math.isfinite(active_prior_power) or active_prior_power <= 0:
            raise ValueError('Use a positive training-prior power, never test-user truth')
        self.active_prior_power = float(active_prior_power)

    def forward(self, query, query_variance, conditional_mean, rho):
        # conditional_mean is intentionally unused, matching the author function.
        logits = gaussian_site_log_odds(query, query_variance, torch.zeros_like(query),
                                       self.active_prior_power, rho)
        return logits.to(query.dtype)
