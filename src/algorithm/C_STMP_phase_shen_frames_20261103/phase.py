"""Shen III-C (53) applied to this model's per-user, per-frame phases.

Source: https://arxiv.org/html/2412.20806v1#S3.SS3, (47)--(54).
Adaptations: full fixed-Gaussian conditional moments; all users; q=0 fixed
to one. There is no common-slope fitting, channel rotation, or descent guard.
The prior term noise*I is for a SUM over observation columns, not an average.
"""
import time
import numpy as np
from algorithm.proposed.phase_math import quadratic_objective
from .moments import conditional_quadratic, marginal_value


def effective_pilot(pilot, phase):
    pilot, phase = np.asarray(pilot, complex), np.asarray(phase, complex)
    if pilot.ndim != 3 or phase.shape != pilot.shape[:2]:
        raise ValueError('Expected pilot[Q,K,N] and phase[Q,K]')
    if not np.isfinite(pilot).all() or not np.isfinite(phase).all():
        raise ValueError('Finite operator inputs required')
    if not np.allclose(abs(phase), 1., rtol=0., atol=1e-10):
        raise ValueError('Unit-modulus phase required')
    return pilot*phase[:, :, None]


def rotations(phase, gram, matched, noise):
    phase, gram, matched = (np.asarray(x, complex) for x in (phase, gram, matched))
    if matched.ndim != 2 or not all(matched.shape):
        raise ValueError('Nonempty matched[Q,K] required')
    q, k = matched.shape
    if phase.shape != (q, k) or gram.shape != (q, k, k):
        raise ValueError('Incompatible phase quadratic')
    if not all(np.isfinite(x).all() for x in (phase, gram, matched)) or not np.isfinite(noise) or noise <= 0:
        raise ValueError('Finite arrays and positive noise required')
    if not np.allclose(abs(phase), 1., rtol=0., atol=1e-10) or not np.allclose(phase[0], 1., rtol=0., atol=1e-10):
        raise ValueError('Unit phases with reference frame equal to one required')
    if not np.allclose(gram, gram.conj().transpose(0, 2, 1), rtol=1e-10, atol=1e-12):
        raise ValueError('Hermitian conditional Gram required')
    proposed = phase.copy()
    backward_error = 0.
    zero_components = 0
    if q > 1:
        system = gram[1:]+float(noise)*np.eye(k)[None]
        solution = np.linalg.solve(system, matched[1:, :, None])[..., 0]
        if not np.isfinite(solution).all():
            raise FloatingPointError('Nonfinite phase solution')
        residual = np.einsum('qkl,ql->qk', system, solution)-matched[1:]
        normalizer = np.linalg.norm(system)*np.linalg.norm(solution)+np.linalg.norm(matched[1:])
        backward_error = float(np.linalg.norm(residual)/max(normalizer, np.finfo(float).tiny))
        magnitude = abs(solution)
        threshold = 64*np.finfo(float).eps*np.maximum(1., magnitude.max(axis=1, keepdims=True))
        valid = magnitude > threshold
        block = proposed[1:].copy()
        block[valid] = solution[valid]/magnitude[valid]
        proposed[1:] = block
        zero_components = int(np.sum(~valid))
    before = quadratic_objective(phase, gram, matched)
    after = quadratic_objective(proposed, gram, matched)
    tolerance = 1e-10*max(1., abs(before), float(np.sum(abs(gram))), float(np.sum(abs(matched))))
    increments = np.angle(proposed*phase.conj())
    return proposed, dict(
        method='Shen projected linear solve with fixed reference frame',
        conditional_before=before, conditional_after=after,
        conditional_objective_increased=bool(after > before),
        conditional_objective_materially_increased=bool(after > before+tolerance),
        conditional_roundoff_tolerance=tolerance,
        linear_solve_relative_residual=backward_error,
        numerical_zero_components_kept=zero_components,
        maximum_frame_increment=float(np.max(abs(increments))),
        rms_frame_increment=float(np.sqrt(np.mean(increments**2))),
        per_user_rms_increment=np.sqrt(np.mean(increments**2, axis=0)).tolist(),
        unit_modulus_error=float(np.max(abs(abs(proposed)-1))),
        reference_frame_error=float(np.max(abs(proposed[0]-1))),
        moved=bool(np.max(abs(proposed-phase)) > 32*np.finfo(float).eps),
        accepted=True, guard=False, fit_common_slope=False, fit_channel_rotation=False,
        regularization_noise=float(noise), free_phase_parameters=(q-1)*k,
        guarantee='No descent guarantee for projected rule; increases are applied and recorded')


def update(observation, pilot, mean, variance, noise, phase):
    started = time.perf_counter()
    gram, matched, moments = conditional_quadratic(observation, pilot, mean, variance, noise, phase)
    proposed, solver = rotations(phase, gram, matched, noise)
    before = marginal_value(observation, pilot, mean, variance, noise, phase)
    after = marginal_value(observation, pilot, mean, variance, noise, proposed)
    if not np.isfinite(before) or not np.isfinite(after):
        raise FloatingPointError('Nonfinite frozen Gaussian objective')
    tolerance = 1e-8*max(1., abs(before), abs(after))
    return proposed, dict(**solver, before=before, after=after,
        marginal_objective_increased=bool(after > before),
        marginal_objective_materially_increased=bool(after > before+tolerance),
        marginal_roundoff_tolerance=tolerance, moments=moments,
        units=dict(conditional='Summed expected residual quadratic, receiver-normalized signal units, additive constant omitted',
                   marginal='Gaussian negative log likelihood per independent observation column, additive constant omitted'),
        seconds=time.perf_counter()-started,
        before_phase_real=np.asarray(phase).real.tolist(),
        before_phase_imag=np.asarray(phase).imag.tolist(),
        after_phase_real=proposed.real.tolist(), after_phase_imag=proposed.imag.tolist())
