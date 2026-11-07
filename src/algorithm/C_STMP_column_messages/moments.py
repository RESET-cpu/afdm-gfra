"""Synthetic Gaussian likelihoods and column covariance from mean derivatives.

These utilities validate the candidate interface. They do not load weights or
claim that a finite learned mean has an exact Bayesian covariance.
"""
import numpy as np

from .messages import GaussianMessage, hermitian


def corrupt_information(clean, precision, rng):
    """Draw eta=Lambda h+Lambda^(1/2) epsilon, epsilon proper CN(0,I).

    This is equivalent to r=h+CN(0,Lambda^-1) for positive precision. It avoids
    forming the potentially huge r and covariance. A singular PSD precision is
    allowed; only eigenvalues within roundoff of zero are set to zero.
    """
    values, vectors = np.linalg.eigh(hermitian(precision))
    tolerance = 32*np.finfo(float).eps*max(1., float(np.max(abs(values))))
    if values.min() < -tolerance:
        raise ValueError('Positive semidefinite likelihood precision required')
    root = (vectors*np.sqrt(np.maximum(values, 0.))) @ vectors.conj().T
    epsilon = (rng.standard_normal(clean.shape)+1j*rng.standard_normal(clean.shape))/np.sqrt(2)
    return GaussianMessage(precision, precision @ clean + root @ epsilon)


def covariance_from_directions(mean_function, information, directions, epsilon=.01):
    """Estimate average N x N covariance over L repeated coordinates.

    mean_function maps eta[N,L] to the conditional mean at FIXED precision.
    directions are proper unit-complex probes [P,N,L]. For an exact posterior
    mean, E[(directional derivative of D) xi^H]/L is the average complex
    covariance. The real-coordinate factor of two is already canceled by the
    real/imaginary probe variances 1/2; do not add another factor of two.

    A finite-probe estimate (or a learned mean) can have negative eigenvalues.
    Return the Hermitian estimate without clipping or declaring it calibrated.
    """
    probes = np.asarray(directions)
    if probes.ndim != 3 or probes.shape[1:] != information.shape or len(probes) < 1:
        raise ValueError('Expected probes[P,N,L]')
    if not np.isfinite(epsilon) or epsilon <= 0:
        raise ValueError('Positive finite difference scale required')
    covariance = np.zeros((information.shape[0], information.shape[0]), complex)
    for probe in probes:
        differential = (mean_function(information+epsilon*probe)
                        - mean_function(information-epsilon*probe))/(2*epsilon)
        covariance += differential @ probe.conj().T
    return hermitian(covariance/(len(probes)*information.shape[1]))


def mixture_moments(active_probability, conditional_mean, conditional_covariance):
    """Bernoulli activity mixture, projected only across repeated coordinates."""
    p = float(active_probability)
    if not 0 <= p <= 1:
        raise ValueError('Activity probability must be in [0,1]')
    mu = np.asarray(conditional_mean)
    covariance = p*conditional_covariance + p*(1-p)*(mu @ mu.conj().T)/mu.shape[1]
    return p*mu, hermitian(covariance)
