"""Query damping plus output damping, with the complete history correction.

See docs/PROPOSED_AMP_QUERY_DAMPING.md. This is an explicit finite-AFDM
adaptation; neither Gaussian query errors nor convergence are guaranteed.
"""
from dataclasses import dataclass, asdict
import time
import numpy as np
from afdm_jadcedd.system.observation import ReceiverInput
from afdm_jadcedd.algorithm.score_amp.core import (
    UnsupportedVariance, to_matrix, from_matrix, residual_statistics, estimate_onsager,
)
from afdm_jadcedd.algorithm.score_amp_damped.core import (
    DampedControls, relaxed_update, relative_change,
)


@dataclass(frozen=True)
class QueryDampedControls(DampedControls):
    query_damping: float = .2

    def __post_init__(self):
        super().__post_init__()
        if not np.isfinite(self.query_damping) or not 0 < self.query_damping <= 1:
            raise ValueError('New-value query damping weight must lie in (0, 1]')


def mix_query(previous, current, weight):
    # The first query has weight one, so every query's history weights sum to one.
    if previous is None or weight == 1:
        return current
    return (1-weight)*previous + weight*current


def solve(inputs, denoiser, *, scale, controls=QueryDampedControls(), observer=None):
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
    z, history = y.copy(), np.zeros_like(y)
    previous_query = previous_mixed_residual = None
    probabilities = np.full(k, inputs.activity_prior)
    conditional = np.zeros(shape, complex)
    raw_mean = x.copy()
    rng = np.random.default_rng(controls.seed)
    trace, attempted = [], None
    started = time.monotonic()
    status, reason, error = 'COMPLETE', 'FIXED_ITERATION_BUDGET', None
    beta, alpha = controls.damping, controls.query_damping
    for step in range(controls.iterations):
        base_query = x + np.einsum('qi,qc->ic', a.conj(), z, optimize=False)
        query = mix_query(previous_query, base_query, alpha)
        mixed_residual = mix_query(previous_mixed_residual, z, alpha)
        covariance, stats = residual_statistics(mixed_residual)
        v = stats['variance']
        residual_power = float(np.mean(abs(z)**2))
        attempted = dict(iteration=step+1, **stats, base_residual_variance=residual_power)
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
                    relative_step=controls.relative_step, rng=rng, residual=mixed_residual)
                # B is the derivative with respect to the mixed query itself.
                # All query-history weights are already in mixed_residual.
                correction = np.einsum('qa,ab->qb', mixed_residual, b, optimize=False)
            else:
                b = np.zeros((m*r, m*r), complex)
                correction = np.zeros_like(z)
                derivative = dict(epsilon=None, probes=0, derivative_network_evaluations=0)
            ordinary_residual = y - np.einsum('qi,ic->qc', a, candidate, optimize=False)
            raw_next_z = ordinary_residual + correction
            next_x, next_z = relaxed_update(x, z, candidate, raw_next_z, beta)
            next_history = correction if beta == 1 else (1-beta)*history + beta*correction
            if not np.isfinite(next_x).all() or not np.isfinite(next_z).all():
                raise FloatingPointError('Nonfinite query-damped AMP update')
        except (UnsupportedVariance, FloatingPointError) as exc:
            status, reason, error = 'FAILED', type(exc).__name__, str(exc)
            break

        cross = float(np.real(np.vdot(z, raw_next_z))/(q*m*r))
        raw_power = float(np.mean(abs(raw_next_z)**2))
        expanded = (1-beta)**2*residual_power + beta**2*raw_power + 2*beta*(1-beta)*cross
        if previous_mixed_residual is None:
            query_cross, query_expanded = None, residual_power
        else:
            query_cross = float(np.real(np.vdot(previous_mixed_residual, z))/(q*m*r))
            query_expanded = ((1-alpha)**2*float(np.mean(abs(previous_mixed_residual)**2))
                              + alpha**2*residual_power + 2*alpha*(1-alpha)*query_cross)
        direct_z = y - np.einsum('qi,ic->qc', a, next_x, optimize=False) + next_history
        next_mixed = mix_query(mixed_residual, next_z, alpha)
        row = dict(iteration=step+1, **stats, **derivative, damping=beta, query_damping=alpha,
            base_residual_variance=residual_power,
            query_cross_power=query_cross,
            query_variance_expansion_absolute_error=float(abs(v-query_expanded)),
            query_relative_change=None if previous_query is None else relative_change(query, previous_query),
            undamped_query_defect=relative_change(base_query, query),
            onsager_frobenius=float(np.linalg.norm(b)),
            onsager_trace_real=float(np.trace(b).real), onsager_trace_imag=float(np.trace(b).imag),
            onsager_product_norm=float(np.linalg.norm(correction)),
            correction_history_norm=float(np.linalg.norm(next_history)),
            ordinary_residual_energy=float(np.sum(abs(ordinary_residual)**2)),
            raw_next_residual_variance=raw_power, residual_cross_power=cross,
            next_residual_variance=float(np.mean(abs(next_z)**2)),
            next_query_variance=float(np.mean(abs(next_mixed)**2)),
            variance_expansion_absolute_error=float(abs(expanded-np.mean(abs(next_z)**2))),
            history_identity_relative_error=relative_change(next_z, direct_z),
            estimate_relative_change=relative_change(next_x, x),
            undamped_estimate_defect=relative_change(candidate, x),
            undamped_residual_defect=relative_change(raw_next_z, z),
            activity_change=float(np.max(abs(output['probabilities']-probabilities))),
            first_network_evaluations=1+derivative['derivative_network_evaluations'])
        x, z, history = next_x, next_z, next_history
        previous_query, previous_mixed_residual = query, mixed_residual
        raw_mean = candidate
        probabilities, conditional = output['probabilities'].copy(), output['conditional_mean'].copy()
        trace.append(row)
        if observer is not None:
            observer(dict(row), dict(estimate=scale*from_matrix(x, shape).copy(),
                denoised_estimate=scale*from_matrix(raw_mean, shape).copy(),
                probabilities=probabilities.copy(), query=from_matrix(query, shape).copy(),
                base_query=from_matrix(base_query, shape).copy(),
                covariance=covariance.copy(), onsager=b.copy(),
                residual_for_query=mixed_residual.copy(),
                corrected_residual=z.copy(), correction_history=history.copy()))
    return dict(estimate=scale*from_matrix(x, shape), denoised_estimate=scale*from_matrix(raw_mean, shape),
        probabilities=probabilities, conditional_matrix=scale*conditional,
        trace=trace, status=status, stopping_reason=reason, error=error,
        iterations=len(trace), converged=False, last_attempt=attempted,
        output_is_last_valid_before_failure=status=='FAILED', has_denoised_output=bool(trace),
        operator_normalization=gain,
        normalized_physical_noise_variance=float(inputs.noise_variance/(scale*gain)**2),
        normalized_column_energy_range=[float(np.sum(abs(a)**2, axis=0).min()),
                                       float(np.sum(abs(a)**2, axis=0).max())],
        activity_output='Latest raw denoiser probability; no activity smoothing',
        channel_output='Output-damped iterate; raw denoiser output is saved separately',
        controls=asdict(controls), seconds=time.monotonic()-started)
