"""Noise-scaled residual control, retaining all synthetic variance bands.

The correction is expressed in units of real noise standard deviation. Loss
is physical squared error divided by real noise variance, conditional on the
public variance. Unlike signal-risk weighting, high-variance extrapolation of
the frozen bank does not receive a factor proportional to variance/signal.
"""
import torch
from .residual_model import ResidualJointDnCNN


class NoiseScaledResidualDnCNN(ResidualJointDnCNN):
    def factors(self,variance):
        ci,skip,_,_=super().factors(variance)
        noise_variance=torch.cat([variance,variance],dim=1)[:,:,None,None]/2
        return ci,skip,torch.sqrt(noise_variance),noise_variance
