"""A local phase parameter update for a fixed approximate neural posterior.

The supplied mean is the JOINT mean E[H_k] = p_k E[H_k | active].
For a posterior independent across users, its covariance contribution to the
expected squared residual is constant when |exp(i q beta_k)| = 1.  Consequently
only this mean enters the phase-dependent objective.  No second conditioning,
posterior reconstruction, frequency grid, or physical path search is performed.

Descent is checked for this fixed quadratic only.  It does not establish a
monotone observed likelihood, an exact EM E-step, or monotone detection error.
"""
from time import perf_counter

import numpy as np


def projected_quadratic(observation, pilot, joint_mean):
    """Return summed Gram/matched moments, with data in identical units.

    observation[Q,M,R], pilot[Q,K,N], joint_mean[K,M,R,N].  The resulting
    gram[q,k,l] = sum_d conj(z[q,k,d])*z[q,l,d] and matched[q,k] =
    sum_d conj(z[q,k,d])*y[q,d] use D=M*R complex observation coordinates.
    """
    started = perf_counter()
    y = np.asarray(observation, dtype=complex)
    p = np.asarray(pilot, dtype=complex)
    mean = np.asarray(joint_mean, dtype=complex)
    if y.ndim != 3 or p.ndim != 3 or mean.ndim != 4:
        raise ValueError("Expected observation[Q,M,R], pilot[Q,K,N], joint_mean[K,M,R,N].")
    q, k, n = p.shape
    if min(q, k, n, *y.shape[1:]) < 1 or y.shape[0] != q:
        raise ValueError("Observation and pilot must have equal positive frame counts.")
    if mean.shape != (k, y.shape[1], y.shape[2], n):
        raise ValueError("The joint mean shape is incompatible with observation/pilot.")
    if not all(np.all(np.isfinite(a)) for a in (y, p, mean)):
        raise ValueError("Inputs must be finite.")
    projected = np.einsum("qkn,kmrn->qkmr", p, mean, optimize=True).reshape(q, k, -1)
    flat_y = y.reshape(q, -1)
    gram = np.einsum("qkd,qld->qkl", projected.conj(), projected, optimize=True)
    matched = np.einsum("qkd,qd->qk", projected.conj(), flat_y, optimize=True)
    details = {
        "observation_shape": list(y.shape), "pilot_shape": list(p.shape),
        "joint_mean_shape": list(mean.shape), "projected_shape": list(projected.shape),
        "observation_energy": float(np.vdot(y, y).real),
        "max_gram_hermitian_error": float(np.max(abs(gram-gram.conj().transpose(0, 2, 1)))),
        "moment_sum_coordinates": int(flat_y.shape[1]),
        "elapsed_seconds": float(perf_counter()-started),
    }
    return gram, matched, details


def _arguments(beta, gram, matched):
    beta = np.asarray(beta, dtype=float)
    gram = np.asarray(gram, dtype=complex)
    matched = np.asarray(matched, dtype=complex)
    if matched.ndim != 2 or min(matched.shape) < 1:
        raise ValueError("matched must have positive shape [Q,K].")
    q, k = matched.shape
    if beta.shape != (k,) or gram.shape != (q, k, k):
        raise ValueError("Expected beta[K], gram[Q,K,K], matched[Q,K].")
    if not all(np.all(np.isfinite(a)) for a in (beta, gram, matched)):
        raise ValueError("The quadratic and beta must be finite.")
    # Only the Hermitian part contributes to a real quadratic.  This also
    # removes harmless floating-point antisymmetry without mutating callers.
    gram = (gram+gram.conj().transpose(0, 2, 1))/2
    return beta, gram, matched


def _phases(beta, q):
    return np.exp(1j*np.arange(q)[:, None]*beta[None, :])


def _value_and_action(phi, gram, matched):
    action = np.einsum("qkl,ql->qk", gram, phi, optimize=True)
    value = np.vdot(phi, action).real-2*np.vdot(phi, matched).real
    return float(value), action-matched


def value_gradient(beta, gram, matched):
    """Return the summed quadratic and its derivative with respect to beta.

    J = sum_q phi_q^H G_q phi_q - 2 Re(phi_q^H b_q), phi[q,k]=exp(i*q*beta[k]).
    The omitted data energy and independent-user posterior variance are constant.
    """
    beta, gram, matched = _arguments(beta, gram, matched)
    phi = _phases(beta, matched.shape[0])
    value, action = _value_and_action(phi, gram, matched)
    gradient = 2*np.sum(np.arange(len(phi))[:, None]*(phi.conj()*action).imag, axis=0)
    return value, gradient


def _wrap(beta):
    result = np.array(beta, dtype=float, copy=True)
    outside = (result < -np.pi) | (result >= np.pi)
    result[outside] = (result[outside]+np.pi) % (2*np.pi)-np.pi
    return result


def minimize(beta, gram, matched, *, max_steps=20, gradient_tolerance=1e-7,
             armijo=1e-4, max_backtracks=12):
    """Use a global diagonal curvature bound and Armijo backtracking.

    Optimize theta=(Q-1)*beta, with frame coordinates s=q/(Q-1).  Discard
    constant diagonal/q=0 terms and normalize the remaining coefficients by
    S=sum|G_off|+2*sum|b|.  This makes steps and the gradient stopping tolerance
    invariant to a common positive signal-energy scale.  For the normalized
    objective, diag(D) bounds the Hessian from above globally, where

        D[k] = 2 sum_q s[q]^2 (|b[q,k]| + 2 sum_{l != k}|G[q,k,l]|).

    Thus -gradient/D is a descent direction; a unit trial step satisfies the
    quadratic upper bound in exact arithmetic.  The explicit Armijo check also
    protects finite precision.  There is no phase grid or per-update angle cap.
    """
    started = perf_counter()
    if int(max_steps) != max_steps or max_steps < 0:
        raise ValueError("max_steps must be a nonnegative integer.")
    if int(max_backtracks) != max_backtracks or max_backtracks < 0:
        raise ValueError("max_backtracks must be a nonnegative integer.")
    if not np.isfinite(gradient_tolerance) or gradient_tolerance < 0:
        raise ValueError("gradient_tolerance must be finite and nonnegative.")
    if not np.isfinite(armijo) or not 0 < armijo < .5:
        raise ValueError("armijo must lie strictly between 0 and 0.5.")
    beta, gram, matched = _arguments(beta, gram, matched)
    original = _wrap(beta)
    current = original.copy()
    q, k = matched.shape
    phi = _phases(current, q)
    objective_before, _ = _value_and_action(phi, gram, matched)

    # Make constants exactly absent rather than relying on cancellation of
    # their gradient.  In particular an arbitrary BG covariance diagonal must
    # not affect the steps or the stopping scale.
    off = gram.copy()
    off[:, np.arange(k), np.arange(k)] = 0
    off[0] = 0
    linear = matched.copy()
    linear[0] = 0
    scale = float(np.sum(abs(off))+2*np.sum(abs(linear)))
    if not np.isfinite(scale):
        raise ValueError("The quadratic magnitude overflows floating-point range.")
    frame = np.arange(q, dtype=float)/max(q-1, 1)
    if scale > 0:
        off /= scale
        linear /= scale
    curvature = 2*np.sum(frame[:, None]**2*(abs(linear)+2*np.sum(abs(off), axis=2)), axis=0)
    value, action = _value_and_action(phi, off, linear)
    history = [value]
    gradient = 2*np.sum(frame[:, None]*(phi.conj()*action).imag, axis=0)
    accepted = attempts = rejected = 0
    changes = []
    step_sizes = []
    stop = "zero_phase_dependence" if scale == 0 else "max_steps"
    for _ in range(int(max_steps)):
        if scale == 0:
            break
        if np.max(abs(gradient)) <= gradient_tolerance:
            stop = "gradient_tolerance"
            break
        direction = np.divide(-gradient, curvature, out=np.zeros(k), where=curvature > 0)
        slope = float(gradient@direction)
        if not np.isfinite(slope) or slope >= 0:
            stop = "no_descent_direction"
            break
        attempts += 1
        found = False
        for backtrack in range(int(max_backtracks)+1):
            step = .5**backtrack
            candidate = _wrap(current+step*direction/max(q-1, 1))
            candidate_phi = _phases(candidate, q)
            delta_phi = candidate_phi-phi
            # Evaluate the change directly, avoiding subtraction of nearly
            # equal objective values and all phase-independent terms.
            change = float(2*np.vdot(delta_phi, action).real
                           +np.einsum("qk,qkl,ql->", delta_phi.conj(), off,
                                      delta_phi, optimize=True).real)
            if change <= armijo*step*slope:
                found = True
                break
            rejected += 1
        if not found:
            stop = "line_search_exhausted"
            break
        current, phi = candidate, candidate_phi
        accepted += 1
        changes.append(change)
        step_sizes.append(step)
        value, action = _value_and_action(phi, off, linear)
        history.append(value)
        gradient = 2*np.sum(frame[:, None]*(phi.conj()*action).imag, axis=0)
    if scale > 0 and np.max(abs(gradient)) <= gradient_tolerance:
        stop = "gradient_tolerance"
    objective_after, _ = _value_and_action(phi, gram, matched)
    report = {
        "objective_before": objective_before, "objective_after": objective_after,
        "objective_change": float(scale*sum(changes)),
        "phase_objective_before": float(scale*history[0]),
        "phase_objective_after": float(scale*history[-1]),
        "objective_scale": scale, "normalized_objective_history": history,
        "normalized_gradient_inf": float(np.max(abs(gradient))),
        "accepted_steps": accepted, "attempted_steps": attempts,
        "backtracks": rejected, "step_sizes": step_sizes, "stop_reason": stop,
        "moved": bool(np.any(current != original)),
        "max_wrapped_slope_change": float(np.max(abs(np.angle(np.exp(1j*(current-original)))))),
        "max_frame_phase_change": float(np.max(abs(np.angle(phi*_phases(original, q).conj())))),
        "max_steps": int(max_steps), "max_backtracks": int(max_backtracks),
        "gradient_tolerance": float(gradient_tolerance), "armijo": float(armijo),
        "reference_frame": 0, "fixed_posterior_descent_only": True,
        "elapsed_seconds": float(perf_counter()-started),
    }
    return current, report


def update(observation, pilot, joint_mean, beta, **options):
    """Build moments once, then update beta with the joint posterior held fixed."""
    started = perf_counter()
    gram, matched, details = projected_quadratic(observation, pilot, joint_mean)
    updated, report = minimize(beta, gram, matched, **options)
    report["moments"] = details
    report["mean_residual_energy_before"] = details["observation_energy"]+report["objective_before"]
    report["mean_residual_energy_after"] = details["observation_energy"]+report["objective_after"]
    report["elapsed_seconds"] = float(perf_counter()-started)
    report["seconds"] = report["elapsed_seconds"]
    return updated, report
