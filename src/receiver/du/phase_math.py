"""Projected covariance and stationary points of a trigonometric polynomial.

Numerical functions retained from the accepted development implementation.
Derivation and terminology: paper/docs/PHASE_MESSAGE_GEM.md and TERMINOLOGY.md.
"""
import numpy as np


def observed_covariances(pilot, moment):
    q, k, n = pilot.shape
    r = len(moment)//n
    covariance = np.asarray(moment, complex).reshape(r, n, r, n)
    g = np.einsum('qkn,rntu,sku->kqrst', pilot, covariance,
                  pilot.conj(), optimize=True).reshape(k, q*r, q*r)
    return (g+g.conj().transpose(0, 2, 1))/2


def stationary_maximum(coefficients, previous):
    """Maximize c0 + 2 Re sum c_l exp(-i l beta) using stationary roots.

    The old point is always evaluated, so imperfect root extraction cannot
    worsen the coordinate objective. A dense grid is never used here.
    Algebraic implementation follows the project's stationary.py helper.
    """
    c = np.asarray(coefficients, complex)
    degree = len(c)-1
    if not np.any(c[1:]):
        return float(previous), float(c[0].real), 0
    polynomial = np.zeros(2*degree+1, complex)
    for order in range(1, degree+1):
        polynomial[degree+order] = order*c[order].conjugate()
        polynomial[degree-order] = -order*c[order]
    roots = np.polynomial.polynomial.polyroots(polynomial/np.max(abs(polynomial)))
    selected = roots[np.isfinite(roots) & (abs(abs(roots)-1) < 1e-5)]
    angles = np.r_[previous, np.angle(selected)]
    values = c[0].real+2*np.real(
        np.exp(-1j*angles[:, None]*np.arange(1, len(c)))@c[1:])
    chosen = int(np.argmax(values))
    return float(angles[chosen]), float(values[chosen]), len(selected)


def polynomial_coefficients(u):
    return np.array([np.vdot(u[:len(u)-lag],u[lag:]) for lag in range(len(u))])


def quadratic_objective(phase,gram,b):
    return float(np.einsum('qk,qkl,ql->',phase.conj(),gram,phase,optimize=True).real-2*np.vdot(b,phase).real)
