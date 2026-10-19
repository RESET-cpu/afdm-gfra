"""Wei Eqs. (45)--(46) noise learning in the existing AFDM/MMV SBL model."""
import numpy as np

from .offgrid.atoms import (MAX_FREQUENCY, coarse_dictionary, delay_bounds,
                           sensed_atom, stack_observation, reconstruct)
from .offgrid.sbl import posterior, variance_update, offset_quadratic, bounded_quadratic


def expected_residual_energy(a, y, mean, diagonal, variance, noise):
    """E||Y-AX||², with all posterior cross-covariances in the trace identity."""
    residual = float(np.sum(abs(y-a@mean)**2))
    uncertainty = y.shape[1]*noise*float(np.sum(1-diagonal/variance))
    if uncertainty < -1e-10*max(residual, noise*y.size):
        raise FloatingPointError('Negative posterior observation uncertainty')
    return residual+max(uncertainty, 0.)


def solve(inputs, settings, *, noise_shape=1e-4, noise_rate=1e-4,
          initial_noise_fraction=.01):
    p = np.asarray(inputs.operator, complex)
    y = stack_observation(inputs.observation)
    coarse, norms, coordinates, spacing = coarse_dictionary(p, settings.doppler_step)
    score = np.sum(abs(coarse.conj().T@y)**2, axis=1).reshape(p.shape[1], -1)
    count = min(settings.candidates_per_user, len(coordinates))
    indices = np.concatenate([u*len(coordinates)+np.argsort(-score[u], kind='stable')[:count]
                              for u in range(p.shape[1])])
    users = indices//len(coordinates)
    centers = coordinates[indices % len(coordinates)].copy()
    scales = norms[indices]
    a0 = coarse[:, indices].copy()
    coarse_columns = coarse.shape[1]
    del coarse, score, norms
    derivatives = np.empty((2, a0.shape[0], a0.shape[1]), complex)
    for j, (u, position) in enumerate(zip(users, centers)):
        derivatives[:, :, j] = sensed_atom(p, u, position, True)[1]/scales[j]
    bounds = np.array([delay_bounds(d)-d for d in centers[:, 0]])
    lower = np.column_stack([bounds[:, 0], np.maximum(-spacing/2, -MAX_FREQUENCY-centers[:, 1])])
    upper = np.column_stack([bounds[:, 1], np.minimum(spacing/2, MAX_FREQUENCY-centers[:, 1])])
    offsets = np.zeros_like(centers)
    noise = initial_noise_fraction*float(np.mean(abs(y)**2))
    if noise <= 0 or noise_rate <= 0 or y.size+noise_shape-1 <= 0:
        raise ValueError('Positive observed energy and valid Gamma noise prior required')
    initial_noise = noise
    initial = max((np.sum(abs(y)**2)-y.size*noise)/(y.shape[1]*a0.shape[1]), noise*1e-3)
    variance = np.full(a0.shape[1], initial)
    trace, status = [], 'MAX_ITERATIONS'
    for iteration in range(1, settings.iterations+1):
        a = a0+derivatives[0]*offsets[:, 0]+derivatives[1]*offsets[:, 1]
        mean, diagonal, inv_a = posterior(a, y, variance, noise)
        expected = expected_residual_energy(a, y, mean, diagonal, variance, noise)
        next_noise = (expected+noise_rate)/(y.size+noise_shape-1)
        updated = variance_update(np.sum(abs(mean)**2, axis=1)+y.shape[1]*diagonal,
                                  y.shape[1], settings.rho)
        updated = np.maximum(updated, np.finfo(float).eps*max(1., initial))
        delta_size = 0.
        if iteration > settings.warmup:
            selected = np.argsort(-updated, kind='stable')[:settings.offset_candidates]
            q, b = offset_quadratic(a, y, mean, variance, inv_a, derivatives, selected, noise)
            low = (lower[selected]-offsets[selected]).T.reshape(-1)
            high = (upper[selected]-offsets[selected]).T.reshape(-1)
            delta = bounded_quadratic(q, b, low, high, settings.offset_sweeps).reshape(2, -1).T
            offsets[selected] += delta
            delta_size = float(np.max(abs(delta), initial=0.))
        relative = float(np.linalg.norm(updated-variance)/np.linalg.norm(variance))
        noise_change = abs(next_noise-noise)/noise
        variance, noise = updated, float(next_noise)
        if not np.isfinite(noise) or noise <= 0:
            raise FloatingPointError('Nonfinite or nonpositive learned noise variance')
        trace.append(dict(iteration=iteration, variance_relative_change=relative,
            max_offset_increment=delta_size, noise_variance=noise,
            noise_relative_change=noise_change, expected_residual_energy=expected))
        if (iteration > settings.warmup and relative < settings.tolerance
                and delta_size < settings.tolerance and noise_change < settings.tolerance):
            status = 'HYPERPARAMETER_CHANGE'
            break
    a = a0+derivatives[0]*offsets[:, 0]+derivatives[1]*offsets[:, 1]
    mean, _, _ = posterior(a, y, variance, noise)
    positions = centers+offsets
    gains = mean/scales[:, None]
    h = reconstruct(p.shape[1], y.shape[1], users, positions, gains)
    exact_y = stack_observation(np.einsum('qkn,kmrn->qmr', p, h, optimize=False))
    return dict(estimate=h, user_ids=users, positions=positions, gains=gains,
        iterations=iteration, stopping_reason=status, trace=trace,
        coarse_columns=coarse_columns, screened_columns=len(indices),
        noise_variance=noise, initial_noise_variance=initial_noise,
        residual_energy=float(np.sum(abs(y-exact_y)**2)),
        linearization_relative_error=float(np.linalg.norm(exact_y-a@mean)/max(np.linalg.norm(exact_y), 1e-30)))
