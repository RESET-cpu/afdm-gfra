"""Matrix D-AMP using the full cross-beam Wirtinger partial trace.

The nonlinear map includes the common activity probability of each user.
Gaussian query statistics remain an approximation for finite AFDM operators.
"""
from dataclasses import dataclass
import numpy as np

from .denoiser import UnsupportedVariance


@dataclass(frozen=True)
class Controls:
    iterations: int = 12
    probes: int = 16
    damping: float = .5
    divergence_seed: int = 202610152703
    correction_estimator: str = 'matrix'


def to_matrix(channel):
    k, m, r, n = channel.shape
    return channel.transpose(0, 3, 1, 2).reshape(k*n, m*r)


def from_matrix(matrix, shape):
    k, m, r, n = shape
    return matrix.reshape(k, n, m, r).transpose(0, 2, 3, 1)


def orthogonal_probe(rows, features, rng):
    if not 0 < features <= rows:
        raise ValueError('The orthogonal-column estimator requires features <= rows')
    frequencies = rng.permutation(rows)[:features]
    positions = rng.permutation(rows)
    phases = rng.uniform(0, 2*np.pi, rows)[:, None]+rng.uniform(0, 2*np.pi, features)[None, :]
    return np.exp(1j*(2*np.pi*positions[:, None]*frequencies[None, :]/rows+phases))


def partial_trace(directions, *, rows, features, measurements, rng, probes, residual=None,
                  linear_diagonal=None):
    """B[a,b] = sum_i d D[i,b] / d R[i,a] / Q, without a beam mask."""
    if probes < 1 or measurements < 1:
        raise ValueError('Positive probe and measurement counts required')
    exact = np.zeros((features, features), complex)
    if linear_diagonal is not None:
        linear_diagonal = np.asarray(linear_diagonal, complex)
        if linear_diagonal.shape != (rows, features) or not np.isfinite(linear_diagonal).all():
            raise FloatingPointError('Invalid known diagonal derivative component')
        np.fill_diagonal(exact, linear_diagonal.sum(axis=0)/measurements)
    samples = []
    for _ in range(probes):
        u = orthogonal_probe(rows, features, rng)
        real, imaginary = directions(np.stack((u, 1j*u)))
        dz = (real-1j*imaginary)/2
        if linear_diagonal is not None:
            dz = dz-linear_diagonal*u
        samples.append(exact+np.einsum('ia,ib->ab', u.conj(), dz, optimize=True)/measurements)
    samples = np.stack(samples)
    correction = samples.mean(axis=0)
    diagnostics = {}
    if residual is not None:
        products = np.einsum('qa,pab->pqb', residual, samples, optimize=True)
        denominator = max(float(np.linalg.norm(residual)), 1e-30)
        standard_error = (np.sqrt(np.sum(abs(products-products.mean(axis=0))**2)/(probes*(probes-1)))
                          if probes > 1 else None)
        diagnostics = dict(
            correction_mc_se_over_residual=None if standard_error is None else float(standard_error/denominator),
            correction_norm_over_residual=float(np.linalg.norm(products.mean(axis=0))/denominator))
    return correction, diagnostics


def user_row_correction(directions, residual, *, rows, row_block_size, rng, probes):
    """Estimate the complete ZB action for a user-separable frozen Jacobian.

    Each row direction costs Q complex directions (2Q real JVPs). A complete
    N-column frame gives the partial trace exactly, apart from JVP arithmetic.
    Partial frames use a uniform subset without replacement; the SE below
    includes that finite-population correction and is unavailable for P=1.
    """
    if row_block_size < 1 or rows % row_block_size or not 1 <= probes <= row_block_size:
        raise ValueError('One to N row directions and independent N-row user blocks required')
    q, features = residual.shape
    frame = np.concatenate([orthogonal_probe(row_block_size, row_block_size, rng)
                            for _ in range(rows//row_block_size)], axis=0)
    order = rng.permutation(row_block_size)
    samples = []
    for column in order[:probes]:
        eta = frame[:, column]
        sample = np.empty_like(residual, dtype=np.complex128)
        for observation_row in range(q):
            u = eta[:, None]*residual[observation_row]
            real, imaginary = directions(np.stack((u, 1j*u)))
            dz = (real-1j*imaginary)/2
            sample[observation_row] = np.einsum('i,ib->b', eta.conj(), dz)/q
        samples.append(sample)
    samples = np.stack(samples)
    feedback = samples.mean(axis=0)
    if probes == row_block_size:
        standard_error = 0.
    elif probes > 1:
        standard_error = np.sqrt((1-probes/row_block_size)*np.sum(abs(samples-feedback)**2)
                                 /(probes*(probes-1)))
    else:
        standard_error = None
    denominator = max(float(np.linalg.norm(residual)), 1e-30)
    diagnostics = dict(
        correction_mc_se_over_residual=None if standard_error is None else float(standard_error/denominator),
        correction_norm_over_residual=float(np.linalg.norm(feedback)/denominator),
        correction_estimator='user_row', correction_sample_count=probes,
        correction_complex_directions=q*probes,
        correction_se_sampling='Uniform subset without replacement from N-column user frames',
        correction_se_finite_population_factor=1-probes/row_block_size)
    return feedback, diagnostics


def solve(inputs, denoise, *, scale, controls=Controls(), observer=None):
    p = np.asarray(inputs.operator, np.complex128)
    observation = np.asarray(inputs.observation, np.complex128)
    q, k, n = p.shape
    m, r = observation.shape[1:]
    shape = (k, m, r, n)
    if not 0 < controls.damping <= 1 or controls.iterations < 1 or controls.probes < 1:
        raise ValueError('Positive iteration/probe counts and damping in (0,1] required')
    if controls.correction_estimator not in ('matrix', 'user_row'):
        raise ValueError('Expected matrix or user_row correction estimator')
    if controls.correction_estimator == 'user_row' and controls.probes > n:
        raise ValueError('At most N user-row directions are available')
    gain = float(np.sqrt(np.sum(abs(p)**2)/(k*n)))
    if not np.isfinite(gain) or gain <= 0 or not np.isfinite(scale) or scale <= 0:
        raise ValueError('Positive finite operator and population scales required')
    a, y = p.reshape(q, k*n)/gain, observation.reshape(q, m*r)/(scale*gain)
    x, z = np.zeros((k*n, m*r), complex), y.copy()
    memory = np.zeros_like(z)
    rng = np.random.default_rng(controls.divergence_seed)
    beta = controls.damping
    trace, status, failure, probabilities = [], 'COMPLETE', None, None
    for step in range(controls.iterations):
        query = x+np.einsum('qn,qc->nc', a.conj(), z, optimize=True)
        covariance = np.einsum('qi,qj->ij', z, z.conj(), optimize=True)/q
        variances = np.diag(covariance).real.reshape(m, r).mean(axis=1)
        try:
            output, channel_directions = denoise.linearize(from_matrix(query, shape), covariance)
            raw = to_matrix(output)
            candidate_probability = np.asarray(denoise.probabilities, float).copy()
            if (raw.shape != x.shape or not np.isfinite(raw).all()
                    or candidate_probability.shape != (k,)
                    or not np.isfinite(candidate_probability).all()
                    or np.any((candidate_probability < 0) | (candidate_probability > 1))):
                raise FloatingPointError('Invalid joint mean or activity probabilities')

            def directions(deltas):
                values = channel_directions(np.stack([from_matrix(d, shape) for d in deltas]))
                return np.stack([to_matrix(value) for value in values])

            matrix_diagnostics = dict(correction_frobenius=None,
                correction_cross_beam_frobenius=None, correction_diagonal_mean_real=None)
            if controls.correction_estimator == 'user_row':
                feedback, diagnostic = user_row_correction(directions, z, rows=k*n,
                    row_block_size=n, rng=rng, probes=controls.probes)
            else:
                known = getattr(denoise, 'linear_diagonal', None)
                correction, diagnostic = partial_trace(directions, rows=k*n, features=m*r,
                    measurements=q, rng=rng, probes=controls.probes, residual=z,
                    linear_diagonal=None if known is None else to_matrix(known))
                feedback = np.einsum('qa,ab->qb', z, correction, optimize=True)
                same_beam = np.repeat(np.arange(m), r)
                cross_beam = same_beam[:, None] != same_beam[None, :]
                matrix_diagnostics = dict(correction_frobenius=float(np.linalg.norm(correction)),
                    correction_cross_beam_frobenius=float(np.linalg.norm(correction[cross_beam])),
                    correction_diagonal_mean_real=float(np.trace(correction).real/(m*r)))
                diagnostic.update(correction_estimator='matrix', correction_sample_count=controls.probes,
                    correction_complex_directions=controls.probes,
                    correction_se_sampling='Independent random matrix probes',
                    correction_se_finite_population_factor=None)
            next_x = (1-beta)*x+beta*raw
            next_memory = (1-beta)*memory+beta*feedback
            residual = y-np.einsum('qn,nc->qc', a, next_x, optimize=True)
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
            activity_probability_min=float(candidate_probability.min()),
            activity_probability_max=float(candidate_probability.max()),
            activity_probability_sum=float(candidate_probability.sum()), damping=beta,
            **matrix_diagnostics, **diagnostic)
        x, z, memory, probabilities = next_x, next_z, next_memory, candidate_probability
        trace.append(row)
        if observer is not None:
            observer(row, scale*from_matrix(x, shape))
    return dict(estimate=scale*from_matrix(x, shape), probabilities=probabilities,
                probability_query_iteration=len(trace) if probabilities is not None else None,
                probability_scope='Last accepted query; not the posterior probability of the damped channel state',
                trace=trace, status=status, failure=failure, iterations=len(trace), operator_normalization=gain,
                stopping_reason='FIXED_ITERATIONS' if status == 'COMPLETE' else 'INVALID_QUERY_OR_UPDATE')
