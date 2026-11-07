"""Accepted activity head and Gaussian message operations, preserved verbatim."""
import math
import torch
from torch import nn
from torch.nn import functional as F
from receiver.du.configuration import CONFIG
from receiver.du.inputs import pack
from receiver.du.inputs import unpack

class ActivityHead(nn.Module):
    def __init__(self):
        super().__init__()
        self.maps = nn.Sequential(nn.Conv2d(64,32,3,padding=1),nn.SiLU(),
                                  nn.Conv2d(32,64,3,stride=2,padding=1),nn.SiLU(),
                                  nn.Conv2d(64,64,3,stride=2,padding=1),nn.SiLU(),nn.AdaptiveAvgPool2d(1))
        self.head = nn.Sequential(nn.Linear(69,64),nn.SiLU(),nn.Linear(64,1))
        nn.init.zeros_(self.head[-1].weight); nn.init.zeros_(self.head[-1].bias)

    def forward(self, r, v, mean, rho):
        x, f = r.flatten(1,2), mean.flatten(1,2)
        maps = torch.cat((x,f),dim=1) / torch.sqrt(1+v)[:,None,None,None]
        energy = lambda t: 2*t.square().flatten(1).mean(1)
        scalars = torch.stack((torch.log(v), torch.log1p(energy(x)/v),
                               torch.log1p(energy(f)/v),torch.log1p(energy(x-f)/v),
                               torch.full_like(v,math.log(rho/(1-rho)))),dim=1)
        # This is a directly supervised posterior classifier, not an AWGN likelihood-ratio identity.
        return self.head(torch.cat((self.maps(maps).flatten(1),scalars),dim=1))[:,0] + math.log(rho/(1-rho))


def _linear_terms(public, prior, variance):
    s, noise = public['s'], public['noise']
    gain = s*variance/(noise+s.square()*variance)
    residual = public['y']-public['a']@pack(prior)
    correction = unpack(public['vv']@(gain.repeat(2)[:,None]*(public['uh']@residual)),prior.shape)
    unknowns = public['a'].shape[1]//2
    # Trace over all complex unknowns, including the null space. This form also
    # avoids cancellation for a full-column-rank operator at high SNR.
    posterior_fraction = ((unknowns-len(s))+(noise/(noise+s.square()*variance)).sum())/unknowns
    information_fraction = (s*gain).sum()/unknowns
    return correction,posterior_fraction,information_fraction


def linear_query(public, prior, variance, log_gamma):
    """Same calibrated Gaussian extrinsic equations, without subtracting 1-g.

    Computing the information fraction directly avoids catastrophic cancellation
    when a tiny incoming variance makes the posterior/prior ratio round to one.
    """
    correction,posterior_fraction,information_fraction=_linear_terms(public,prior,variance)
    quotient=torch.exp(log_gamma)*posterior_fraction/information_fraction
    return prior+(1+quotient)*correction,variance*quotient,variance*posterior_fraction


def feedback_variance(raw, query_variance, log_beta, *, order='after_positive'):
    """Learn a positive scale after positive mapping (project parameterization).

    The residual is an iteration parameter, not an unbiased posterior MSE.
    `before_positive` exists only for paired regression against the Mac source.
    """
    temperature = CONFIG['receiver']['variance_soft_floor_temperature_ratio']*query_variance
    if order=='after_positive':
        positive = torch.exp(log_beta)*(temperature*F.softplus(raw/temperature)+1e-6)
    elif order=='before_positive':
        positive = temperature*F.softplus(torch.exp(log_beta)*raw/temperature)+1e-6
    else:
        raise ValueError('Unknown variance calibration order')
    ceiling = CONFIG['receiver']['maximum_feedback_variance_ratio']
    if order=='before_positive':
        ratio=(ceiling*torch.tanh(positive/(ceiling*query_variance))).clamp_min(1e-6)
    else:
        # A smooth lower bound preserves the beta gradient when the residual is
        # very negative. A hard clamp here disconnected beta in a regression.
        lower=1e-6
        ratio=lower+(ceiling-lower)*torch.tanh(positive/((ceiling-lower)*query_variance))
    return query_variance*ratio,ratio


def damp_gaussian(previous_mean,previous_variance,proposed_mean,proposed_variance,reference_variance):
    """Geometric interpolation of two Gaussian messages with positive variance."""
    amount=(reference_variance/proposed_variance).clamp(max=1.)
    variance=1/((1-amount)/previous_variance+amount/proposed_variance)
    mean=variance*((1-amount)*previous_mean/previous_variance+amount*proposed_mean/proposed_variance)
    # Preserve the accepted original message exactly, including rounding.
    return (torch.where(amount==1,proposed_mean,mean),
            torch.where(amount==1,proposed_variance,variance),amount)
