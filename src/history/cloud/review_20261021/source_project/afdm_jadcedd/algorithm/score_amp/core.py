"""Complex matrix AMP. See docs/PROPOSED_AMP.md for assumptions and indices.

No signal truth enters this module. The empirical residual covariance is
projected to one scalar only at the frozen AWGN-network interface. This is an
explicit approximation, not a claim that the AFDM query is white Gaussian.
"""
from dataclasses import dataclass, asdict
import time
import numpy as np
from afdm_jadcedd.system.observation import ReceiverInput


@dataclass(frozen=True)
class Controls:
    iterations: int = 10
    probes: int = 8
    relative_step: float = 0.01
    seed: int = 202610157301
    onsager: bool = True

    def __post_init__(self):
        if (not isinstance(self.iterations, int) or self.iterations < 1
                or not isinstance(self.probes, int) or self.probes < 1
                or not np.isfinite(self.relative_step) or self.relative_step <= 0
                or not isinstance(self.seed, int) or self.seed < 0
                or not isinstance(self.onsager, bool)):
            raise ValueError('Invalid AMP iteration or derivative controls')


class UnsupportedVariance(ValueError):
    """The actual query label is outside the frozen networks' training support."""


def to_matrix(channel):
    k, m, r, n = channel.shape
    return channel.transpose(0, 3, 1, 2).reshape(k*n, m*r)


def from_matrix(matrix, shape):
    k, m, r, n = shape
    return matrix.reshape(k, n, m, r).transpose(0, 2, 3, 1)


def residual_statistics(z):
    """C[a,b]=E Z[a] conj(Z[b]), NOT the transposed row Gram matrix."""
    q, c = z.shape
    covariance = np.einsum('qa,qb->ab', z, z.conj(), optimize=False)/q
    pseudo = np.einsum('qa,qb->ab', z, z, optimize=False)/q
    variance = float(np.trace(covariance).real/c)
    norm = float(np.linalg.norm(covariance))
    return covariance, dict(
        variance=variance,
        residual_covariance_offdiagonal_fraction=float(
            np.sum(abs(covariance-np.diag(np.diag(covariance)))**2)
            / max(norm**2, np.finfo(float).tiny)),
        residual_pseudocovariance_ratio=float(np.linalg.norm(pseudo)/max(norm, 1e-300)))


def isotropic_probe(rows, features, rng):
    """Random-phase DFT columns: E conj(U_ia) U_jb=delta_ij delta_ab.

    For features<=rows, U^H U=rows*I exactly. When features>rows, use
    independent unit-circle entries; the same expectation identity holds.
    """
    if features > rows:
        return np.exp(2j*np.pi*rng.random((rows, features)))
    positions = rng.permutation(rows)
    frequencies = rng.permutation(rows)[:features]
    phases = rng.uniform(0, 2*np.pi, rows)[:, None]
    phases = phases + rng.uniform(0, 2*np.pi, features)[None, :]
    return np.exp(1j*(2*np.pi*positions[:, None]*frequencies[None, :]/rows+phases))


def estimate_onsager(denoise, query, variance, *, measurements, probes,
                     relative_step, rng, residual=None, return_samples=False):
    """B[a,b]=sum_i partial D[i,b]/partial R[i,a] / measurements.

    denoise accepts a complex matrix. Its noise label is fixed for all four
    evaluations. Paired real directions isolate the Wirtinger derivative.
    Finite differences include the activity classifier's dependence on F(R),
    even if its training implementation contains a gradient detach.
    """
    if (variance <= 0 or not np.isfinite(variance) or measurements < 1
            or probes < 1 or relative_step <= 0):
        raise ValueError('Positive variance and derivative controls required')
    rows, features = query.shape
    epsilon = relative_step*np.sqrt(variance)
    matrices, products = [], []
    for _ in range(probes):
        u = isotropic_probe(rows, features, rng)
        plus = denoise(query+epsilon*u, variance)
        minus = denoise(query-epsilon*u, variance)
        iplus = denoise(query+1j*epsilon*u, variance)
        iminus = denoise(query-1j*epsilon*u, variance)
        direction = (plus-minus-1j*(iplus-iminus))/(4*epsilon)
        b = np.einsum('ia,ib->ab', u.conj(), direction, optimize=False)/measurements
        if not np.isfinite(b).all():
            raise FloatingPointError('Nonfinite Onsager matrix')
        matrices.append(b)
        if residual is not None:
            products.append(np.einsum('qa,ab->qb', residual, b, optimize=False))
    stack = np.stack(matrices)
    mean = stack.mean(axis=0)
    diagnostics = dict(epsilon=float(epsilon), probes=probes,
                       derivative_network_evaluations=4*probes)
    if products:
        products = np.stack(products)
        average = products.mean(axis=0)
        diagnostics['onsager_product_sample_rms_over_residual'] = float(
            np.sqrt(np.mean(np.sum(abs(products-average)**2, axis=(1, 2))))
            / max(np.linalg.norm(residual), 1e-300))
        # Orthogonal feature coordinates within each probe, independent probes.
        diagnostics['onsager_product_mc_se_over_residual'] = float(
            np.sqrt(np.sum(abs(products-average)**2)/(probes*(probes-1)))
            / max(np.linalg.norm(residual), 1e-300)) if probes > 1 else None
    if return_samples:
        return mean, diagnostics, stack
    return mean, diagnostics


def solve(inputs, denoiser, *, scale, controls=Controls(), observer=None):
    """Return the last finite estimate AND an explicit status on failure.

    A fixed iteration budget is completion, not a convergence certificate.
    No noise clipping, hard activity gating, damping or site reuse is applied.
    """
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
    probabilities = np.full(k, inputs.activity_prior)
    conditional = np.zeros(shape, complex)
    rng = np.random.default_rng(controls.seed)
    trace, attempted = [], None
    started = time.monotonic()
    status, reason, error = 'COMPLETE', 'FIXED_ITERATION_BUDGET', None
    column_power = np.sum(abs(a)**2, axis=0)
    for step in range(controls.iterations):
        query = x + np.einsum('qi,qc->ic', a.conj(), z, optimize=False)
        covariance, stats = residual_statistics(z)
        v = stats['variance']
        attempted = dict(iteration=step+1, **stats)
        try:
            output = denoiser.infer(from_matrix(query, shape), v, inputs.activity_prior)
            estimate = to_matrix(output['mean'])
            if estimate.shape != x.shape or not np.isfinite(estimate).all():
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
            ordinary_residual = y - np.einsum('qi,ic->qc', a, estimate, optimize=False)
            next_z = ordinary_residual + correction
            if not np.isfinite(next_z).all():
                raise FloatingPointError('Nonfinite AMP residual')
        except (UnsupportedVariance, FloatingPointError) as exc:
            status, reason, error = 'FAILED', type(exc).__name__, str(exc)
            break
        row = dict(iteration=step+1, **stats, **derivative,
            onsager_frobenius=float(np.linalg.norm(b)),
            onsager_trace_real=float(np.trace(b).real),
            onsager_trace_imag=float(np.trace(b).imag),
            onsager_product_norm=float(np.linalg.norm(correction)),
            ordinary_residual_energy=float(np.sum(abs(ordinary_residual)**2)),
            next_residual_variance=float(np.mean(abs(next_z)**2)),
            estimate_relative_change=float(np.linalg.norm(estimate-x)/max(np.linalg.norm(estimate), 1e-300)),
            activity_change=float(np.max(abs(output['probabilities']-probabilities))),
            first_network_evaluations=1+derivative['derivative_network_evaluations'])
        x, z = estimate, next_z
        probabilities = output['probabilities'].copy()
        conditional = output['conditional_mean'].copy()
        trace.append(row)
        if observer is not None:
            observer(dict(row), dict(estimate=scale*from_matrix(x, shape).copy(),
                probabilities=probabilities.copy(), query=from_matrix(query, shape).copy(),
                covariance=covariance.copy(), onsager=b.copy(), corrected_residual=z.copy()))
    return dict(estimate=scale*from_matrix(x, shape), probabilities=probabilities,
        conditional_matrix=scale*conditional, trace=trace, status=status,
        stopping_reason=reason, error=error, iterations=len(trace), converged=False,
        last_attempt=attempted, output_is_last_valid_before_failure=status=='FAILED',
        has_denoised_output=bool(trace), operator_normalization=gain,
        normalized_physical_noise_variance=float(inputs.noise_variance/(scale*gain)**2),
        normalized_column_energy_range=[float(column_power.min()), float(column_power.max())],
        controls=asdict(controls), seconds=time.monotonic()-started)
