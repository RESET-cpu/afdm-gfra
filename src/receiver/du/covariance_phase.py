"""Experimental phase initialization from pilot covariance, without path atoms.

Covariance matching / nonnegative least squares: Fengler et al.,
arXiv:1910.11266v2, III-B. The user-specific phase slopes and effective-channel
isotropy approximation here are AFDM adaptations, not that paper's algorithm.
"""
from dataclasses import asdict
from dataclasses import dataclass
import time

import numpy as np
from scipy.optimize import minimize_scalar


@dataclass(frozen=True)
class Controls:
    phase_bins: int = 256
    sweeps: int = 20
    refinement_iterations: int = 40


def covariance_atoms(pilot):
    """G[k,q,s] = P[q,k,:] P[s,k,:]^H, with diagonal discarded."""
    p = np.asarray(pilot, complex)
    g = np.einsum('qkn,skn->kqs', p, p.conj(), optimize=True)
    g[:, np.arange(len(p)), np.arange(len(p))] = 0.
    return g


def correlation_grid(atom, residual, bins):
    """Re <D(beta) G D(beta)^H, residual> on beta=2*pi*j/bins."""
    q = len(atom)
    product = atom.conj()*residual
    lag = np.arange(q)[:, None]-np.arange(q)[None]
    coefficients = np.zeros(bins, complex)
    np.add.at(coefficients, (lag % bins).ravel(), product.ravel())
    return np.fft.fft(coefficients).real


def estimate(observation, pilot, controls=Controls()):
    """Use only Y and raw pilots. All users stay eligible in every sweep.

    Minimize the off-diagonal covariance residual over nonnegative user
    powers and one wrapped phase increment per user. No true activity, noise,
    channel, delay, Doppler or angle is accepted. This is an initialization;
    inferred powers are not used as a detector or to truncate users.
    """
    started = time.perf_counter()
    y, p = np.asarray(observation, complex), np.asarray(pilot, complex)
    if (y.ndim != 3 or p.ndim != 3 or len(y) != len(p)
            or not np.isfinite(y).all() or not np.isfinite(p).all()):
        raise ValueError('Finite observation[Q,M,R] and pilot[Q,K,N] required')
    q, k, _ = p.shape
    if controls.phase_bins < 4*q or controls.sweeps < 1:
        raise ValueError('Positive sweep budget and adequate phase grid required')
    z = y.reshape(q, -1)
    covariance = z @ z.conj().T/z.shape[1]
    diagonal = np.arange(q)
    covariance[diagonal, diagonal] = 0.
    atoms = covariance_atoms(p)
    norms = np.sum(abs(atoms)**2, axis=(1, 2))
    lag = np.arange(q)[:, None]-np.arange(q)[None]
    slopes, powers = np.zeros(k), np.zeros(k)
    fitted_atoms = atoms.copy()
    prediction = np.zeros_like(covariance)
    step = 2*np.pi/controls.phase_bins
    initial = np.array([np.max(correlation_grid(g, covariance, controls.phase_bins))**2 /
                        max(norm, np.finfo(float).tiny) for g, norm in zip(atoms, norms)])
    order = np.argsort(-initial, kind='stable')
    trace = [float(np.sum(abs(covariance)**2))]
    for sweep in range(controls.sweeps):
        for user in order:
            if norms[user] < np.finfo(float).eps:
                continue
            old = powers[user]*fitted_atoms[user]
            residual = covariance-prediction+old
            grid = correlation_grid(atoms[user], residual, controls.phase_bins)
            center = int(np.argmax(grid))*step

            def negative_correlation(beta):
                return -float(np.vdot(atoms[user]*np.exp(1j*lag*beta), residual).real)

            refined = minimize_scalar(negative_correlation, bounds=(center-step, center+step),
                method='bounded', options={'maxiter': controls.refinement_iterations, 'xatol': 1e-10})
            beta = min([slopes[user], center, float(refined.x)], key=negative_correlation)
            gamma = max(0., -negative_correlation(beta)/norms[user])
            atom = atoms[user]*np.exp(1j*lag*beta)
            prediction += gamma*atom-old
            powers[user], slopes[user], fitted_atoms[user] = gamma, beta, atom
        loss = float(np.sum(abs(covariance-prediction)**2))
        if loss > trace[-1]+1e-10*max(1., trace[-1]):
            raise FloatingPointError('Covariance coordinate update increased objective')
        trace.append(loss)
    slopes = (slopes+np.pi) % (2*np.pi)-np.pi
    phase = np.exp(1j*np.arange(q)[:, None]*slopes[None])
    return dict(phase_slopes=slopes, phase=phase, covariance_powers=powers), dict(
        seconds=time.perf_counter()-started, controls=asdict(controls), objective=trace,
        truth_used_in_inference=False, physical_path_search_used=False,
        assumption='Approximate isotropic input-coordinate channel covariance; cross-user terms ignored',
        use='Phase initialization only, not an activity detector')
