"""Candidate only: Shen et al., arXiv:2412.20806v1, III-C (48)--(53).

The projected linear solve is from Shen. Effective AFDM channel moments,
per-user phases, the q=0 reference and optional common-slope projection are
project adaptations. This is NOT a reproduction of their OTFS receiver.
No path dictionary, delay estimate or physical-Doppler search is used.
"""
from dataclasses import asdict, dataclass
import time

import numpy as np
from scipy.optimize import minimize_scalar

from system.observation import ReceiverInput


@dataclass(frozen=True)
class Controls:
    outer_updates: int = 10
    phase_constraint: str = 'slope'
    slope_grid: int = 256
    slope_refinement_iterations: int = 50

    def validate(self, frames):
        if self.phase_constraint not in ('frame', 'slope'):
            raise ValueError('Expected frame or slope phase constraint')
        for field in ('outer_updates', 'slope_grid', 'slope_refinement_iterations'):
            value = getattr(self, field)
            if type(value) is not int or value < 1:
                raise ValueError('Positive integer budgets required')
        if self.slope_grid < 4 * frames:
            raise ValueError('Slope grid must resolve the frame span')


def contributions(pilot, mean):
    """Z[q,d,k] from the SOFT E[a_k H_k]; do not apply activity twice."""
    pilot, mean = np.asarray(pilot, complex), np.asarray(mean, complex)
    if (pilot.ndim != 3 or mean.ndim != 4 or
            (pilot.shape[1], pilot.shape[2]) != (mean.shape[0], mean.shape[-1])):
        raise ValueError('Expected pilot[Q,K,N] and mean[K,M,R,N]')
    if not np.isfinite(pilot).all() or not np.isfinite(mean).all():
        raise ValueError('Finite pilot and mean required')
    return np.einsum('qkn,kmrn->qmrk', pilot, mean, optimize=True).reshape(
        len(pilot), -1, pilot.shape[1])


def moments(observation, pilot, mean, complex_variance, noise):
    """AFDM equivalent of (49)--(51), with independent isotropic user errors.

    variance[k] is per complex H coefficient, in physical units. The caller
    must disclose whether this is a posterior variance or merely a proxy.
    The sigma^2 I term is Shen's Gaussian phase prior. Both diagonal terms
    are constant ON the unit circle, but affect his unconstrained solve.
    """
    z = contributions(pilot, mean)
    y = np.asarray(observation, complex).reshape(len(z), -1)
    if y.shape != z.shape[:2] or not np.isfinite(y).all():
        raise ValueError('Observation shape must match predicted contributions')
    variance = np.broadcast_to(np.asarray(complex_variance, float), (z.shape[-1],))
    if not np.isfinite(variance).all() or (variance < 0).any() or not np.isfinite(noise) or noise <= 0:
        raise ValueError('Nonnegative variance and positive noise required')
    gram = np.einsum('qdk,qdl->qkl', z.conj(), z, optimize=True)
    matched = np.einsum('qdk,qd->qk', z.conj(), y, optimize=True)
    diagonal = z.shape[1] * np.sum(abs(pilot)**2, axis=-1) * variance[None] + noise
    index = np.arange(z.shape[-1])
    gram[:, index, index] += diagonal
    return gram, matched


def objective(phase, gram, matched):
    response = np.einsum('qkl,ql->qk', gram, phase, optimize=True)
    return float(np.vdot(phase, response).real - 2*np.vdot(matched, phase).real)


def projected_solve(gram, matched, previous):
    """Shen (53): solve A z=b, then z/|z|. No monotonicity is assumed."""
    gram, matched, previous = (np.asarray(x, complex) for x in (gram, matched, previous))
    if (gram.ndim != 3 or gram.shape[1:] != (matched.shape[-1],)*2 or
            matched.shape != previous.shape or len(gram) != len(matched)):
        raise ValueError('Invalid quadratic dimensions')
    if not all(np.isfinite(x).all() for x in (gram, matched, previous)):
        raise ValueError('Finite quadratic and previous phase required')
    np.testing.assert_allclose(gram, gram.conj().transpose(0, 2, 1), rtol=1e-12, atol=1e-12)
    solved = np.linalg.solve(gram, matched[..., None])[..., 0]
    modulus = abs(solved)
    phase = previous.copy()
    threshold = np.finfo(float).eps * np.maximum(1., modulus.max(axis=1, keepdims=True))
    np.divide(solved, modulus, out=phase, where=modulus > threshold)
    # q=0 is the chosen AFDM channel reference, not a simulated true phase.
    phase[0] = 1.
    return phase, dict(linear_solve_relative_residual=float(
        np.linalg.norm(np.einsum('qkl,ql->qk', gram, solved)-matched) /
        max(np.linalg.norm(matched), np.finfo(float).tiny)),
        numerically_uninformative_entries=int(np.sum(modulus <= threshold)),
        objective_before=objective(previous, gram, matched),
        objective_after_frame_projection=objective(phase, gram, matched))


def project_slopes(phase, previous, bins=256, maxiter=50):
    """Nearest exp(j*q*beta_k) to frame phases; NOT a delay/Doppler grid.

    The grid covers only wrapped phase increments [-pi,pi), with no physical
    path parameters or alias resolution. This constraint is absent from (53).
    """
    phase = np.asarray(phase, complex)
    q = np.arange(len(phase))
    previous = np.asarray(previous, float)
    if previous.shape != (phase.shape[1],) or bins < 4*len(phase):
        raise ValueError('Valid previous slopes and adequate grid required')
    grid = -np.pi + 2*np.pi*np.arange(bins)/bins
    scores = (np.exp(-1j*grid[:, None]*q) @ phase).real
    beta = previous.copy()
    step = 2*np.pi/bins
    for k in range(len(beta)):
        def loss(value):
            return float(-np.real(np.exp(-1j*q*value) @ phase[:, k]))
        center = grid[int(np.argmax(scores[:, k]))]
        fitted = minimize_scalar(loss, bounds=(center-step, center+step), method='bounded',
                                 options=dict(maxiter=maxiter, xatol=1e-11))
        candidates = [beta[k], center, float(fitted.x)]
        beta[k] = min(candidates, key=loss)
    beta = (beta+np.pi) % (2*np.pi)-np.pi
    return np.exp(1j*q[:, None]*beta), beta


def infer(receiver, observation, pilot, activity_prior, controls=Controls(), *, observer=None):
    """Alternate the frozen ten-layer receiver with ten phase updates.

    Requires ONLY public Y, P and activity prior. Truth is not an argument.
    Each conditional call restarts the frozen network. Thus ten outer updates
    cost 11 x 10 layers, NOT ten total layers. No new weights are trained.
    """
    started = time.perf_counter()
    y, pilot = np.asarray(observation), np.asarray(pilot)
    controls.validate(len(pilot))
    phase = np.ones(pilot.shape[:2], complex)
    slopes = np.zeros(pilot.shape[1])
    trace, phase_history = [], [phase.copy()]
    observer_seconds = 0.
    before_calls = receiver.model.score_evaluations
    for outer in range(controls.outer_updates+1):
        public = ReceiverInput(y, pilot*phase[:, :, None], 1., activity_prior)
        arrays, conditional = receiver.infer(public)
        if observer is not None:
            observer_started = time.perf_counter()
            observer(outer, phase.copy(), arrays, conditional)
            observer_seconds += time.perf_counter()-observer_started
        if outer == controls.outer_updates:
            break
        # This calibrated residual feedback is explicitly a variance PROXY,
        # not the posterior variance computed by Shen's message passing.
        variance = conditional['diagnostics'][-1]['feedback_variance'] * receiver.scale**2
        noise = float(arrays['noise_variance_estimate'])
        gram, matched = moments(y, pilot, arrays['estimate'], variance, noise)
        next_phase, step_record = projected_solve(gram, matched, phase)
        if controls.phase_constraint == 'slope':
            next_phase, slopes = project_slopes(next_phase, slopes, controls.slope_grid,
                                               controls.slope_refinement_iterations)
        step_record.update(outer_update=outer+1, variance_proxy=float(variance), noise_estimate=noise,
            objective_after=objective(next_phase, gram, matched),
            max_phase_change=float(np.max(abs(np.angle(next_phase*phase.conj())))))
        trace.append(step_record)
        phase = next_phase
        phase_history.append(phase.copy())
    arrays = dict(arrays, phase=phase, phase_history=np.stack(phase_history))
    if controls.phase_constraint == 'slope':
        arrays['phase_slopes'] = slopes
    return arrays, dict(status='COMPLETE', controls=asdict(controls), trace=trace,
        seconds=time.perf_counter()-started-observer_seconds, observer_seconds=observer_seconds,
        conditional_calls=controls.outer_updates+1,
        unfolded_layers_executed=10*(controls.outer_updates+1),
        score_calls=receiver.model.score_evaluations-before_calls,
        initialization='All phase multipliers one; no physical parameter estimation',
        moment_scope='Soft ten-layer mean; independent isotropic calibrated-feedback variance PROXY',
        source='Shen et al. arXiv:2412.20806v1 III-C (48)-(53); AFDM adaptations documented',
        activity_threshold=.5, truth_used_in_inference=False, physical_path_search_used=False,
        final_conditional=conditional)
