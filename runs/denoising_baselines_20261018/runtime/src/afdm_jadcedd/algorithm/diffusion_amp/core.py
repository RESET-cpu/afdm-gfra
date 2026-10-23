"""Complex matrix D-AMP with optional synchronous state damping.

B[a,b] = sum_i partial D[i,b] / partial R[i,a] / Q. A complete
paired real derivative gives the Wirtinger part. Each beam is an independent
denoiser example, so cross-beam Jacobian blocks are identically zero.
"""
from dataclasses import dataclass
import numpy as np
from .denoiser import UnsupportedVariance


@dataclass(frozen=True)
class Controls:
    iterations: int = 12
    probes: int = 8
    damping: float = 1.
    divergence_seed: int = 202610151703


def to_matrix(channel):
    k, m, r, n = channel.shape
    return channel.transpose(0, 3, 1, 2).reshape(k*n, m*r)


def from_matrix(matrix, shape):
    k, m, r, n = shape
    return matrix.reshape(k, n, m, r).transpose(0, 2, 3, 1)


def orthogonal_probe(rows, features, rng):
    if not 0 < features <= rows:
        raise ValueError('Probe group size must lie between one and rows')
    frequencies = rng.permutation(rows)[:features]
    positions = rng.permutation(rows)
    phases = rng.uniform(0, 2*np.pi, rows)[:, None]+rng.uniform(0, 2*np.pi, features)[None, :]
    return np.exp(1j*(2*np.pi*positions[:, None]*frequencies[None, :]/rows+phases))


def partial_trace(directions, *, rows, features, measurements, group_size, rng, probes, residual=None):
    if probes < 1 or features % group_size:
        raise ValueError('Invalid probe count or group layout')
    samples = []
    for _ in range(probes):
        u = np.concatenate([orthogonal_probe(rows, group_size, rng)
                            for _ in range(features//group_size)], axis=1)
        real, imaginary = directions(np.stack((u, 1j*u)))
        dz = (real-1j*imaginary)/2
        value = np.zeros((features, features), complex)
        for start in range(0, features, group_size):
            sl = slice(start, start+group_size)
            value[sl, sl] = np.einsum('ni,nj->ij', u[:, sl].conj(), dz[:, sl], optimize=False)/measurements
        samples.append(value)
    samples = np.stack(samples)
    correction = samples.mean(axis=0)
    diagnostics = {}
    if residual is not None:
        products = np.einsum('qa,pab->pqb', residual, samples, optimize=False)
        denominator = max(float(np.linalg.norm(residual)), 1e-30)
        standard_error = (np.sqrt(np.sum(abs(products-products.mean(axis=0))**2)/(probes*(probes-1)))
                          if probes > 1 else None)
        diagnostics = dict(
            correction_mc_se_over_residual=None if standard_error is None else float(standard_error/denominator),
            correction_norm_over_residual=float(np.linalg.norm(products.mean(axis=0))/denominator))
    return correction, diagnostics


def solve(inputs, denoise, *, scale, controls=Controls(), observer=None):
    p = np.asarray(inputs.operator, np.complex128)
    observation = np.asarray(inputs.observation, np.complex128)
    q, k, n = p.shape
    m, r = observation.shape[1:]
    shape = (k, m, r, n)
    if not 0 < controls.damping <= 1 or controls.iterations < 1 or controls.probes < 1:
        raise ValueError('Positive iteration/probe counts and damping in (0,1] required')
    gain = float(np.sqrt(np.sum(abs(p)**2)/(k*n)))
    if not np.isfinite(gain) or gain <= 0 or not np.isfinite(scale) or scale <= 0:
        raise ValueError('Positive finite operator and population scales required')
    a, y = p.reshape(q, k*n)/gain, observation.reshape(q, m*r)/(scale*gain)
    x, z = np.zeros((k*n, m*r), complex), y.copy()
    memory = np.zeros_like(z)
    rng = np.random.default_rng(controls.divergence_seed)
    beta = controls.damping
    trace, status, failure = [], 'COMPLETE', None
    for step in range(controls.iterations):
        query = x+np.einsum('qn,qc->nc', a.conj(), z, optimize=False)
        covariance = np.einsum('qi,qj->ij', z, z.conj(), optimize=False)/q
        variances = np.diag(covariance).real.reshape(m, r).mean(axis=1)
        try:
            output, channel_directions = denoise.linearize(from_matrix(query, shape), covariance)
            raw = to_matrix(output)
            if raw.shape != x.shape or not np.isfinite(raw).all():
                raise FloatingPointError('Invalid score mean')

            def directions(deltas):
                values = channel_directions(np.stack([from_matrix(d, shape) for d in deltas]))
                return np.stack([to_matrix(value) for value in values])

            correction, diagnostic = partial_trace(directions, rows=k*n, features=m*r,
                measurements=q, group_size=r, rng=rng, probes=controls.probes, residual=z)
            next_x = (1-beta)*x+beta*raw
            next_memory = (1-beta)*memory+beta*np.einsum('qa,ab->qb', z, correction, optimize=False)
            residual = y-np.einsum('qn,nc->qc', a, next_x, optimize=False)
            next_z = residual+next_memory
            if not np.isfinite(next_z).all():
                raise FloatingPointError('Nonfinite AMP state')
        except (UnsupportedVariance, FloatingPointError, RuntimeError) as exc:
            status = 'FAILED'
            failure = dict(iteration=step+1, error_type=type(exc).__name__, error=str(exc),
                           per_beam_complex_variance=variances.tolist())
            break
        row = dict(iteration=step+1, per_beam_complex_variance=variances.tolist(),
            mean_complex_variance=float(variances.mean()), residual_energy=float(np.sum(abs(residual)**2)),
            correction_frobenius=float(np.linalg.norm(correction)),
            correction_diagonal_mean_real=float(np.trace(correction).real/(m*r)),
            damping=beta, **diagnostic)
        x, z, memory = next_x, next_z, next_memory
        trace.append(row)
        if observer is not None:
            observer(row, scale*from_matrix(x, shape))
    return dict(estimate=scale*from_matrix(x, shape), trace=trace, status=status,
                failure=failure, iterations=len(trace), operator_normalization=gain,
                stopping_reason='FIXED_ITERATIONS' if status == 'COMPLETE' else 'INVALID_QUERY_OR_UPDATE')
