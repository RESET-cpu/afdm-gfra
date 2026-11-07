"""One local phase step per user, with the full Gaussian conditional quadratic.

Derivation and source boundaries: paper/C-STMP/docs/PHASE_LOCAL_20261103.md.
The radius bounds each frame's phase increment, including channel rotation.
Only the frozen Gaussian objective is protected; true phase accuracy is not.
"""
import time
import numpy as np
from algorithm.proposed.phase_math import quadratic_objective
from algorithm.C_STMP_phase_direct_20261103.moments import conditional_quadratic, marginal_value


def local_derivatives(c, coordinates):
    """Gradient and Hessian of Re sum c*exp(-j*V@delta) at delta=0."""
    v = np.asarray(coordinates, float)
    c = np.asarray(c, complex)
    return v.T @ c.imag, -(v.T * c.real) @ v


def local_step(c, *, radius=.25, curvature_floor=1e-3, armijo=1e-4, max_backtracks=16):
    """Return center and endpoint-slope increments (a,b); Q=1 has only a."""
    c = np.asarray(c, complex)
    if c.ndim != 1 or not c.size or not np.isfinite(c).all():
        raise ValueError('Finite nonempty per-frame correlation required')
    if not (0 < radius < np.pi and 0 < curvature_floor <= 1 and 0 < armijo < 1):
        raise ValueError('Invalid local phase controls')
    if type(max_backtracks) is not int or max_backtracks < 0:
        raise ValueError('Nonnegative backtracking budget required')
    q = c.size
    s = np.linspace(-1., 1., q) if q > 1 else np.zeros(1)
    v = np.column_stack((np.ones(q), s)) if q > 1 else np.ones((1, 1))
    strength = float(np.sum(abs(c)))
    info = dict(accepted=False, backtracks=0, normalized_gain=0.,
                maximum_frame_increment=0., correlation_scale=strength)
    if strength == 0:
        info['reason'] = 'zero_correlation'
        return np.zeros(2), info
    cn = c / strength
    g, h = local_derivatives(cn, v)
    if np.linalg.norm(g) <= 32*np.finfo(float).eps:
        info['reason'] = 'stationary_at_numerical_precision'
        return np.zeros(2), info
    values, vectors = np.linalg.eigh(-h)
    curvature = np.maximum(values, curvature_floor)
    direction = vectors @ ((vectors.T @ g) / curvature)
    direction *= min(1., radius / np.sum(abs(direction)))
    predicted = float(g @ direction)
    info.update(gradient=g.tolist(), curvature_eigenvalues=values.tolist(),
                predicted_linear_gain=predicted)
    if not np.isfinite(predicted) or predicted <= 0:
        info['reason'] = 'no_ascent_direction'
        return np.zeros(2), info
    for count in range(max_backtracks + 1):
        fraction = 2.**(-count)
        step = fraction*direction
        increment = v @ step
        # expm1 avoids subtracting almost equal objective values near zero.
        gain = float(np.real(np.sum(cn*np.expm1(-1j*increment))))
        if gain > 0 and gain >= armijo*fraction*predicted:
            result = np.zeros(2)
            result[:len(step)] = step
            info.update(accepted=True, backtracks=count, normalized_gain=gain,
                        maximum_frame_increment=float(np.max(abs(increment))),
                        reason='sufficient_increase')
            return result, info
    info.update(backtracks=max_backtracks, reason='backtracking_budget_exhausted')
    return np.zeros(2), info


def rotations(beta, gram, matched, *, radius=.25, curvature_floor=1e-3,
              armijo=1e-4, max_backtracks=16):
    """One sequential user pass; covariance coupling is retained in each u."""
    beta = np.asarray(beta, float).copy()
    gram, matched = np.asarray(gram, complex), np.asarray(matched, complex)
    q, k = matched.shape
    if gram.shape != (q, k, k) or beta.shape != (k,):
        raise ValueError('Incompatible quadratic or slope shape')
    if not all(np.isfinite(x).all() for x in (beta, gram, matched)):
        raise ValueError('Finite conditional quadratic required')
    frames = np.arange(q)
    phase = np.exp(1j*frames[:, None]*beta)
    angle = np.zeros(k)
    before = quadratic_objective(phase, gram, matched)
    order = np.argsort(-np.diagonal(gram, axis1=1, axis2=2).real.sum(axis=0), kind='stable')
    accepted, user_records = 0, []
    for user in order:
        u = matched[:, user] - np.einsum('ql,ql->q', gram[:, user], phase)
        u += gram[:, user, user]*phase[:, user]
        c = phase[:, user].conj()*u
        increment, info = local_step(c, radius=radius, curvature_floor=curvature_floor,
                                    armijo=armijo, max_backtracks=max_backtracks)
        a, b = increment
        if info['accepted']:
            slope_delta = b/((q-1)/2) if q > 1 else 0.
            offset = a-b if q > 1 else a
            phase[:, user] *= np.exp(1j*(offset+frames*slope_delta))
            if q > 1:
                beta[user] = (beta[user]+slope_delta+np.pi)%(2*np.pi)-np.pi
            angle[user] = offset
            accepted += 1
        user_records.append(dict(user=int(user), center_increment=float(a),
                                 endpoint_slope_increment=float(b), **info))
    after = quadratic_objective(phase, gram, matched)
    tolerance = 2e-12*max(1., abs(before), float(np.sum(abs(gram))), float(np.sum(abs(matched))))
    if after > before+tolerance:
        raise FloatingPointError('Frozen conditional quadratic increased')
    return beta, angle, dict(
        sweeps=1, accepted_users=accepted, users=user_records,
        objectives=[before, after], radius=radius,
        maximum_frame_increment=max(r['maximum_frame_increment'] for r in user_records),
        guarantee='Sufficient increase per user; frozen Gaussian quadratic only')


def update(observation, pilot, mean, variance, noise, beta, **options):
    started = time.perf_counter()
    gram, matched, moments = conditional_quadratic(observation, pilot, mean, variance, noise, beta)
    new_beta, angle, solver = rotations(beta, gram, matched, **options)
    before = marginal_value(observation, pilot, mean, variance, noise, beta)
    rotated = mean*np.exp(1j*angle)[:, None, None, None]
    after = marginal_value(observation, pilot, rotated, variance, noise, new_beta)
    if after > before+1e-8*max(1., abs(before)):
        raise FloatingPointError('Frozen Gaussian marginal objective increased')
    return new_beta, angle, dict(before=before, after=after, conditional_quadratic=solver,
        moments=moments, moved=solver['accepted_users'] > 0,
        seconds=time.perf_counter()-started)
