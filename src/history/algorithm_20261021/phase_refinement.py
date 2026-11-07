"""Update common user phase slopes using fixed soft channel means.

The expected-residual objective follows the phase-learning idea in Shen et al.,
arXiv:2412.20806v1 Sec. III-C (47)-(54). The constraint exp(j*q*beta_k)
and the scalar searches are this project's AFDM adaptation. Under the current
independent-user posterior approximation, covariance contributes a constant
to this unit-modulus objective. See docs/PROPOSED_UNKNOWN_PHASE.md.
"""
from dataclasses import asdict, dataclass
import time

import numpy as np
from scipy.optimize import minimize_scalar

from .unknown_phase_model import UnknownPhaseInput
from afdm_jadcedd.system.phase import wrap


@dataclass(frozen=True)
class Controls:
    outer_updates: int = 2
    sweeps: int = 2
    phase_bins: int = 256
    candidates: int = 4
    refinement_iterations: int = 50
    phase_weight: float = 1.0
    phase_tolerance: float = 1e-4

    def validate(self, frames):
        for key in ('outer_updates', 'sweeps', 'phase_bins', 'candidates', 'refinement_iterations'):
            value = getattr(self, key)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError('Positive integer phase budgets required')
        if self.phase_bins < frames or self.candidates > self.phase_bins:
            raise ValueError('Sufficient phase bins required')
        if not 0 < self.phase_weight <= 1 or not np.isfinite(self.phase_tolerance) or self.phase_tolerance <= 0:
            raise ValueError('Valid phase weight and tolerance required')


def contributions(inputs, mean):
    """z[q, measurement coordinate, k] from E[a_k H_k], already soft-weighted."""
    if not isinstance(inputs, UnknownPhaseInput):
        raise TypeError('UnknownPhaseInput with original pilot required')
    mean = np.asarray(mean)
    q, k, n = inputs.pilot.shape
    m, r = inputs.observation.shape[1:]
    if mean.shape != (k, m, r, n) or not np.isfinite(mean).all():
        raise ValueError('Finite full effective-channel mean required')
    return np.einsum('qkn,kmrn->qmrk', inputs.pilot, mean, optimize=False).reshape(q, m*r, k)


def quadratic(slopes, gram, matched):
    """Frozen-moment objective (minus observation energy) and exact gradient."""
    q = np.arange(len(gram))[:, None]
    phase = np.exp(1j*q*np.asarray(slopes)[None])
    response = np.einsum('qkl,ql->qk', gram, phase, optimize=False)
    value = np.vdot(phase, response).real - 2*np.vdot(matched, phase).real
    gradient = 2*np.sum(q*(phase.conj()*(response-matched)).imag, axis=0)
    return float(value), gradient


def refine(inputs, mean, slopes, controls=Controls()):
    """Two cyclic sweeps with retained old points and direct-residual acceptance.

    No user is filtered using an activity decision. The noise scale and the
    independent-user covariance term are constant for this phase update.
    """
    started = time.monotonic()
    z = contributions(inputs, mean)
    controls.validate(len(z))
    beta = np.asarray(slopes, dtype=float).copy()
    if beta.shape != (z.shape[-1],) or not np.isfinite(beta).all():
        raise ValueError('One finite phase slope per user required')
    initial = beta.copy()
    frames = np.arange(len(z))
    y = inputs.observation.reshape(len(z), -1)
    phase = np.exp(1j*frames[:, None]*beta[None])
    prediction = np.einsum('qdk,qk->qd', z, phase, optimize=False)
    energy = lambda x: float(np.sum(abs(x)**2))
    before = energy(y-prediction)
    grid = np.arange(controls.phase_bins)*(2*np.pi/controls.phase_bins)-np.pi
    basis = np.exp(-1j*frames[:, None]*grid[None])
    order = np.argsort(-np.sum(abs(z)**2, axis=(0, 1)), kind='stable')
    trace = []
    for sweep in range(controls.sweeps):
        sweep_before = energy(y-prediction)
        accepted = 0
        for k in order:
            old = z[:, :, k]*phase[:, k, None]
            residual = y-prediction+old
            correlation = np.sum(z[:, :, k].conj()*residual, axis=1)
            scores = np.einsum('q,qg->g', correlation, basis, optimize=False).real
            if not np.isfinite(scores).all():
                raise FloatingPointError('Nonfinite phase scores')
            if not np.any(correlation):
                continue
            def loss(value):
                return float(-2*np.real(np.sum(correlation*np.exp(-1j*frames*value))))
            best, best_loss = float(beta[k]), loss(beta[k])
            for index in np.argsort(scores, kind='stable')[-controls.candidates:]:
                center = float(grid[index]); step = 2*np.pi/controls.phase_bins
                fitted = minimize_scalar(loss, bounds=(center-step, center+step), method='bounded',
                    options=dict(maxiter=controls.refinement_iterations, xatol=1e-10))
                for candidate in (center, fitted.x):
                    candidate = beta[k]+controls.phase_weight*float(wrap(candidate-beta[k]))
                    value = loss(candidate)
                    if np.isfinite(value) and value < best_loss:
                        best, best_loss = float(candidate), value
            new_phase = np.exp(1j*frames*best)
            candidate = prediction-old+z[:, :, k]*new_phase[:, None]
            if energy(y-candidate) < energy(y-prediction):
                prediction = candidate
                phase[:, k] = new_phase
                beta[k] = float(wrap(best))
                accepted += 1
        after = energy(y-prediction)
        trace.append(dict(sweep=sweep+1, accepted_user_updates=accepted,
                          residual_before=sweep_before, residual_after=after))
        if after > sweep_before+1e-12*max(1., sweep_before):
            raise FloatingPointError('Phase update increased the fixed-mean objective')
    # Recompute from final slopes to detect packing or incremental-update errors.
    final_phase = np.exp(1j*frames[:, None]*beta[None])
    final = energy(y-np.einsum('qdk,qk->qd', z, final_phase, optimize=False))
    if not np.isfinite(final) or final > before+1e-12*max(1., before):
        raise FloatingPointError('Invalid final phase objective')
    change = abs(wrap(beta-initial))
    return beta, dict(controls=asdict(controls), seconds=time.monotonic()-started,
        objective_before=before, objective_after=final,
        relative_objective_decrease=(before-final)/max(before, np.finfo(float).tiny),
        max_phase_change=float(change.max(initial=0)), trace=trace,
        covariance_scope='Independent users; within-user covariance has phase-independent trace',
        mean_scope='E[a H], including soft activity once', known_activity_used=False,
        truth_used_in_inference=False)
