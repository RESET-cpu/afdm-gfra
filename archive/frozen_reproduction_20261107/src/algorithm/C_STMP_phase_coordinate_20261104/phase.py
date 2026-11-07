"""One cyclic exact minimization sweep on the fixed phase quadratic.

Waldspurger et al., arXiv:1206.0102v3, Sec. 2.3, Eq. (3), Algorithm 2.
Here the linear term is included explicitly and frame zero remains fixed.
This is not Shen's projected linear solve and is not a global EM guarantee.
"""
import time
import numpy as np
from algorithm.proposed.phase_math import quadratic_objective
from algorithm.C_STMP_phase_shen_frames_20261103.moments import conditional_quadratic, marginal_value
from algorithm.C_STMP_phase_conditional_schedule_20261104.phase import signal_change


def rotations(phase, gram, matched, noise):
    phase, gram, matched = (np.asarray(x, complex) for x in (phase, gram, matched))
    if matched.ndim != 2 or not all(matched.shape):
        raise ValueError('Nonempty matched[Q,K] required')
    q, k = matched.shape
    if phase.shape != (q, k) or gram.shape != (q, k, k):
        raise ValueError('Incompatible phase quadratic')
    if not all(np.isfinite(x).all() for x in (phase, gram, matched)) or not np.isfinite(noise) or noise <= 0:
        raise ValueError('Finite quadratic and positive noise required')
    if not np.allclose(abs(phase), 1., rtol=0., atol=1e-10) or not np.allclose(phase[0], 1., rtol=0., atol=1e-10):
        raise ValueError('Unit phases with reference frame equal to one required')
    if not np.allclose(gram, gram.conj().transpose(0, 2, 1), rtol=1e-10, atol=1e-12):
        raise ValueError('Hermitian conditional Gram required')
    proposed = phase.copy()
    zero_components, deltas = 0, []
    for user in range(k):
        old = proposed[1:, user].copy()
        # Latest earlier coordinates, old later coordinates: a cyclic sweep.
        c = (matched[1:, user]
             - np.einsum('qj,qj->q', gram[1:, user, :], proposed[1:])
             + gram[1:, user, user]*old)
        threshold = 64*np.finfo(float).eps*np.maximum(
            1., abs(matched[1:, user])+np.sum(abs(gram[1:, user, :]), axis=1))
        valid = abs(c) > threshold
        new = old.copy()
        new[valid] = c[valid]/abs(c[valid])
        delta = -2*np.real((new-old).conj()*c)
        proposed[1:, user] = new
        deltas.extend(delta.tolist())
        zero_components += int(np.sum(~valid))
    before = quadratic_objective(phase, gram, matched)
    after = quadratic_objective(proposed, gram, matched)
    tolerance = 1e-10*max(1., abs(before), float(np.sum(abs(gram))), float(np.sum(abs(matched))))
    if after > before+tolerance:
        raise FloatingPointError('Exact phase-coordinate sweep increased the fixed objective')
    increments = np.angle(proposed*phase.conj())
    return proposed, dict(method='Cyclic exact minimization of each unit-modulus phase',
        conditional_before=before, conditional_after=after,
        conditional_objective_increased=bool(after > before),
        conditional_objective_materially_increased=bool(after > before+tolerance),
        conditional_roundoff_tolerance=tolerance,
        coordinate_objective_changes=deltas,
        coordinate_change_sum=float(sum(deltas)), coordinate_sweeps=1,
        numerical_zero_components_kept=zero_components,
        maximum_frame_increment=float(np.max(abs(increments))),
        rms_frame_increment=float(np.sqrt(np.mean(increments**2))),
        per_user_rms_increment=np.sqrt(np.mean(increments**2, axis=0)).tolist(),
        unit_modulus_error=float(np.max(abs(abs(proposed)-1))),
        reference_frame_error=float(np.max(abs(proposed[0]-1))),
        moved=bool(np.max(abs(proposed-phase)) > 32*np.finfo(float).eps),
        accepted=True, guard=False, fit_common_slope=False, fit_channel_rotation=False,
        free_phase_parameters=(q-1)*k,
        guarantee='Nonincrease of this fixed conditional quadratic only; no global receiver guarantee')


def update(observation, pilot, mean, variance, noise, phase):
    started = time.perf_counter()
    gram, matched, moments = conditional_quadratic(observation, pilot, mean, variance, noise, phase)
    proposed, solver = rotations(phase, gram, matched, noise)
    before = marginal_value(observation, pilot, mean, variance, noise, phase)
    after = marginal_value(observation, pilot, mean, variance, noise, proposed)
    tolerance = 1e-8*max(1., abs(before), abs(after))
    if not np.isfinite(before) or not np.isfinite(after) or after > before+tolerance:
        raise FloatingPointError('Fixed-Gaussian marginal objective failed descent verification')
    return proposed, dict(**solver, before=before, after=after,
        marginal_objective_increased=bool(after > before),
        marginal_objective_materially_increased=bool(after > before+tolerance),
        marginal_roundoff_tolerance=tolerance, moments=moments,
        phase_effect=signal_change(phase, proposed, gram, noise*np.asarray(observation).size),
        seconds=time.perf_counter()-started,
        before_phase_real=np.asarray(phase).real.tolist(), before_phase_imag=np.asarray(phase).imag.tolist(),
        after_phase_real=proposed.real.tolist(), after_phase_imag=proposed.imag.tolist())
