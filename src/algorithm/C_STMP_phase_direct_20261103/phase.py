"""Common-slope conditional quadratic updates, adapted from Shen (48).

Unlike Shen (53), optimize the existing exp(j*q*beta) constraint directly.
Each coordinate compares numerical stationary-point candidates and the old point.
No delay, Doppler alias, phase grid, or true activity enters this module.
"""
import time
import numpy as np
from algorithm.proposed.phase_math import stationary_maximum, polynomial_coefficients, quadratic_objective
from .moments import conditional_quadratic, marginal_value


def rotations(beta, gram, matched, *, sweeps=1, fit_offset=False):
    beta = np.asarray(beta, float).copy()
    q, k = matched.shape
    frames = np.arange(q)
    offset = np.zeros(k)
    phase = np.exp(1j*frames[:, None]*beta)
    objectives = [quadratic_objective(phase, gram, matched)]
    order = np.argsort(-np.diagonal(gram, axis1=1, axis2=2).real.sum(axis=0), kind='stable')
    roots = 0
    for _ in range(sweeps):
        for user in order:
            u = matched[:, user] - np.einsum('ql,ql->q', gram[:, user], phase)
            u += gram[:, user, user]*phase[:, user]
            if fit_offset:
                coefficients = polynomial_coefficients(u)
            else:
                coefficients = u/2
                coefficients[0] = u[0].real
            slope, _, count = stationary_maximum(coefficients, beta[user])
            angle = float(np.angle(np.exp(-1j*frames*slope)@u)) if fit_offset else 0.
            proposed = np.exp(1j*(frames*slope+angle))
            previous = float(np.vdot(phase[:, user], u).real)
            value = float(np.vdot(proposed, u).real)
            if value >= previous:
                beta[user], offset[user], phase[:, user] = slope, angle, proposed
            roots += count
        objectives.append(quadratic_objective(phase, gram, matched))
    tolerance = 1e-9*max(1., abs(objectives[0]), float(np.sum(abs(gram))), float(np.sum(abs(matched))))
    if np.max(np.diff(objectives), initial=0.) > tolerance:
        raise FloatingPointError('Conditional phase objective increased')
    return (beta+np.pi)%(2*np.pi)-np.pi, offset, dict(
        sweeps=sweeps, stationary_roots=roots, objectives=objectives,
        fit_offset=fit_offset, guarantee='Fixed Gaussian-message quadratic only')


def update(observation, pilot, mean, variance, noise, beta, *, sweeps=1, fit_offset=False,
           solver_kind='coordinate', guard=False):
    started = time.perf_counter()
    gram, matched, details = conditional_quadratic(observation, pilot, mean, variance, noise, beta)
    if solver_kind == 'coordinate':
        new_beta, angle, solver = rotations(beta, gram, matched, sweeps=sweeps, fit_offset=fit_offset)
    elif solver_kind == 'legacy_coordinate':
        if not fit_offset:
            raise ValueError('The original coordinate rule includes a constant channel rotation')
        from algorithm.proposed.phase_update import update_rotations
        new_beta, angle, solver = update_rotations(beta, gram, matched,
            max_sweeps=10, relative_tolerance=1e-7)
        solver.pop('users', None)
    elif solver_kind == 'shen':
        from .shen_update import rotations as shen_rotations
        new_beta, angle, solver = shen_rotations(beta, gram, matched, noise, guard=guard)
    else:
        raise ValueError('Unknown phase update solver')
    q = len(pilot)
    old_phase = np.exp(1j*np.arange(q)[:, None]*beta)
    new_phase = np.exp(1j*np.arange(q)[:, None]*new_beta)
    z = np.einsum('qkn,kmrn->qkmr', pilot, mean, optimize=True)
    energy = np.sum(abs(z)**2, axis=(2, 3))
    delta = new_phase*np.exp(1j*angle)[None]-old_phase
    prediction_change = float(np.sqrt(np.sum(energy*abs(delta)**2)/max(float(energy.sum()), 1e-30)))
    g = np.einsum('qkn,skn->kqs', pilot, pilot.conj(), optimize=True)
    def covariance(phase):
        return noise*np.eye(q)+variance*np.einsum('qk,kqs,sk->qs', phase, g, phase.conj(), optimize=True)
    old_c, new_c = covariance(old_phase), covariance(new_phase)
    covariance_change = float(np.linalg.norm(new_c-old_c)/max(np.linalg.norm(new_c), np.linalg.norm(old_c)))
    before = marginal_value(observation, pilot, mean, variance, noise, beta)
    rotated = mean*np.exp(1j*angle)[:, None, None, None]
    after = marginal_value(observation, pilot, rotated, variance, noise, new_beta)
    if (solver_kind in ('coordinate','legacy_coordinate') or guard) and after > before+1e-8*max(1., abs(before)):
        raise FloatingPointError('Fixed-message marginal objective increased')
    return new_beta, angle, dict(before=before, after=after, conditional_quadratic=solver,
        moments=details, prediction_change=prediction_change, covariance_change=covariance_change,
        maximum_slope_change=float(np.max(abs(np.angle(np.exp(1j*(new_beta-beta)))))),
        seconds=time.perf_counter()-started)
