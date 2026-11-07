"""Mean damping with the matching weighted history of Onsager corrections.

See docs/PROPOSED_AMP_DAMPING.md. The recurrence is an explicit finite-AFDM
adaptation, not an AFDM state-evolution or convergence theorem. The original
score_amp implementation is kept unchanged for independent comparison.
"""
from dataclasses import dataclass, asdict
import time
import numpy as np
from afdm_jadcedd.system.observation import ReceiverInput
from afdm_jadcedd.algorithm.score_amp.core import (
    Controls, UnsupportedVariance, to_matrix, from_matrix,
    residual_statistics, estimate_onsager,
)


@dataclass(frozen=True)
class DampedControls(Controls):
    iterations: int = 100
    damping: float = 0.2

    def __post_init__(self):
        super().__post_init__()
        if not np.isfinite(self.damping) or not 0 < self.damping <= 1:
            raise ValueError('New-value damping weight must lie in (0, 1]')


def relaxed_update(x, z, raw_mean, raw_residual, weight):
    """Relax the complete AMP state; raw_residual uses raw_mean, not next_x."""
    if weight == 1:
        return raw_mean, raw_residual
    return ((1-weight)*x + weight*raw_mean,
            (1-weight)*z + weight*raw_residual)


def relative_change(new, old):
    return float(np.linalg.norm(new-old)/max(np.linalg.norm(new), np.linalg.norm(old), 1e-12))


def solve(inputs, denoiser, *, scale, controls=DampedControls(), observer=None):
    if not isinstance(inputs, ReceiverInput):
        raise TypeError('Public four-field ReceiverInput required')
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError('Positive population normalization required')
    p = np.asarray(inputs.operator, np.complex128)
    observation = np.asarray(inputs.observation, np.complex128)
    q, k, n = p.shape
    m, r = observation.shape[1:]
    shape = (k, m, r, n)
    gain = float(np.sqrt(np.sum(abs(p)**2)/(k*n)))
    if not np.isfinite(gain) or gain <= 0:
        raise ValueError('Nonzero finite operator required')
    a = p.reshape(q, k*n)/gain
    y = observation.reshape(q, m*r)/(scale*gain)
    x = np.zeros((k*n, m*r), complex)
    z = y.copy()
    history = np.zeros_like(z)
    probabilities = np.full(k, inputs.activity_prior)
    conditional = np.zeros(shape, complex)
    raw_mean = x.copy()
    rng = np.random.default_rng(controls.seed)
    trace, attempted = [], None
    started = time.monotonic()
    status, reason, error = 'COMPLETE', 'FIXED_ITERATION_BUDGET', None
    weight = controls.damping
    for step in range(controls.iterations):
        query = x + np.einsum('qi,qc->ic', a.conj(), z, optimize=False)
        covariance, stats = residual_statistics(z)
        v = stats['variance']
        attempted = dict(iteration=step+1, **stats)
        try:
            output = denoiser.infer(from_matrix(query, shape), v, inputs.activity_prior)
            candidate = to_matrix(output['mean'])
            if candidate.shape != x.shape or not np.isfinite(candidate).all():
                raise FloatingPointError('Invalid joint denoiser output')
            def mapping(value, noise):
                return to_matrix(denoiser.infer(
                    from_matrix(value, shape), noise, inputs.activity_prior)['mean'])
            if controls.onsager:
                b, derivative = estimate_onsager(
                    mapping, query, v, measurements=q, probes=controls.probes,
                    relative_step=controls.relative_step, rng=rng, residual=z)
                correction = np.einsum('qa,ab->qb', z, b, optimize=False)
            else:
                b = np.zeros((m*r, m*r), complex)
                correction = np.zeros_like(z)
                derivative = dict(epsilon=None, probes=0, derivative_network_evaluations=0)
            ordinary_residual = y - np.einsum('qi,ic->qc', a, candidate, optimize=False)
            raw_next_z = ordinary_residual + correction
            next_x, next_z = relaxed_update(x, z, candidate, raw_next_z, weight)
            next_history = correction if weight == 1 else (1-weight)*history + weight*correction
            if not np.isfinite(next_x).all() or not np.isfinite(next_z).all():
                raise FloatingPointError('Nonfinite damped AMP update')
        except (UnsupportedVariance, FloatingPointError) as exc:
            status, reason, error = 'FAILED', type(exc).__name__, str(exc)
            break

        # Exact complex cross term is included because the arrays, rather than
        # their scalar variances, are relaxed. No independent-error assumption.
        cross_power = float(np.real(np.vdot(z, raw_next_z))/(q*m*r))
        raw_power = float(np.mean(abs(raw_next_z)**2))
        expanded_power = (1-weight)**2*v + weight**2*raw_power + 2*weight*(1-weight)*cross_power
        direct_residual = y - np.einsum('qi,ic->qc', a, next_x, optimize=False) + next_history
        row = dict(iteration=step+1, **stats, **derivative, damping=weight,
            onsager_frobenius=float(np.linalg.norm(b)),
            onsager_trace_real=float(np.trace(b).real),
            onsager_trace_imag=float(np.trace(b).imag),
            onsager_product_norm=float(np.linalg.norm(correction)),
            correction_history_norm=float(np.linalg.norm(next_history)),
            ordinary_residual_energy=float(np.sum(abs(ordinary_residual)**2)),
            raw_next_residual_variance=raw_power,
            residual_cross_power=cross_power,
            next_residual_variance=float(np.mean(abs(next_z)**2)),
            variance_expansion_absolute_error=float(abs(expanded_power-np.mean(abs(next_z)**2))),
            history_identity_relative_error=relative_change(next_z, direct_residual),
            estimate_relative_change=relative_change(next_x, x),
            undamped_estimate_defect=relative_change(candidate, x),
            undamped_residual_defect=relative_change(raw_next_z, z),
            activity_change=float(np.max(abs(output['probabilities']-probabilities))),
            first_network_evaluations=1+derivative['derivative_network_evaluations'])
        x, z, history = next_x, next_z, next_history
        raw_mean = candidate
        probabilities = output['probabilities'].copy()
        conditional = output['conditional_mean'].copy()
        trace.append(row)
        if observer is not None:
            observer(dict(row), dict(estimate=scale*from_matrix(x, shape).copy(),
                denoised_estimate=scale*from_matrix(raw_mean, shape).copy(),
                probabilities=probabilities.copy(), query=from_matrix(query, shape).copy(),
                covariance=covariance.copy(), onsager=b.copy(),
                corrected_residual=z.copy(), correction_history=history.copy()))
    return dict(estimate=scale*from_matrix(x, shape),
        denoised_estimate=scale*from_matrix(raw_mean, shape),
        probabilities=probabilities, conditional_matrix=scale*conditional,
        trace=trace, status=status, stopping_reason=reason, error=error,
        iterations=len(trace), converged=False, last_attempt=attempted,
        output_is_last_valid_before_failure=status=='FAILED', has_denoised_output=bool(trace),
        operator_normalization=gain,
        normalized_physical_noise_variance=float(inputs.noise_variance/(scale*gain)**2),
        normalized_column_energy_range=[float(np.sum(abs(a)**2, axis=0).min()),
                                       float(np.sum(abs(a)**2, axis=0).max())],
        activity_output='Latest raw denoiser probability; no activity smoothing',
        channel_output='Damped iterate; raw denoiser output is saved separately',
        controls=asdict(controls), seconds=time.monotonic()-started)

