"""Shen III-C (53) projected solve, with explicit AFDM slope adaptation.

Source: Shen et al., ``LEO Satellite-Enabled Random Access with Large
Differential Delay and Doppler Shift'', III-C, (49)--(53), PDF p. 9.
The caller supplies its full Gaussian-posterior quadratic, not a DU proxy.
Fixing frame zero to one and fitting exp(j*q*beta) are project adaptations;
the original per-frame projection does not enforce this shared slope.
"""
import numpy as np
from algorithm.proposed.phase_math import quadratic_objective, stationary_maximum


def rotations(beta, gram, matched, noise, *, guard=False):
    """Solve each (G_q+noise*I) z_q=b_q, project, then fit common slopes.

    No constant offset is fitted; returned channel rotations are exactly zero.
    guard=True rejects the complete proposal if its fixed quadratic increases.
    Neither the unguarded projection nor a guarded update establishes descent
    across changing neural messages.
    """
    beta = np.asarray(beta, dtype=float)
    gram = np.asarray(gram, dtype=complex)
    matched = np.asarray(matched, dtype=complex)
    if matched.ndim != 2:
        raise ValueError('matched must have shape [frames, users]')
    q, k = matched.shape
    if not q or not k or beta.shape != (k,) or gram.shape != (q, k, k):
        raise ValueError('Nonempty compatible beta, gram and matched required')
    if (not np.isfinite(beta).all() or not np.isfinite(gram).all()
            or not np.isfinite(matched).all() or not np.isfinite(noise) or noise <= 0):
        raise ValueError('Finite moments and positive noise required')
    hermitian_error = float(np.max(abs(gram - gram.conj().transpose(0, 2, 1))))
    if hermitian_error > 1e-10 * max(1., float(np.max(abs(gram)))):
        raise ValueError('Posterior Gram matrix must be Hermitian')

    frames = np.arange(q)
    old_phase = np.exp(1j * frames[:, None] * beta[None, :])
    system = gram + float(noise) * np.eye(k)[None, :, :]
    solution = np.linalg.solve(system, matched[..., None])[..., 0]
    if not np.isfinite(solution).all():
        raise FloatingPointError('Nonfinite projected-solve intermediate')
    linear_residual = np.einsum('qkl,ql->qk', system, solution) - matched
    linear_scale = np.linalg.norm(system) * np.linalg.norm(solution) + np.linalg.norm(matched)
    linear_backward_error = float(np.linalg.norm(linear_residual) / max(float(linear_scale), np.finfo(float).tiny))

    magnitude = abs(solution)
    zero_threshold = 64 * np.finfo(float).eps * np.maximum(1., magnitude.max(axis=1, keepdims=True))
    valid = magnitude > zero_threshold
    projected = old_phase.copy()
    projected[valid] = solution[valid] / magnitude[valid]
    projected[0] = 1.  # AFDM convention: constant path phase belongs to H.
    projected_residual = np.einsum('qkl,ql->qk', system, projected) - matched
    projected_scale = np.linalg.norm(system) * np.linalg.norm(projected) + np.linalg.norm(matched)

    proposed_beta = beta.copy()
    roots = 0
    for user in range(k):
        # Re sum_q phi_q exp(-j*q*beta), rather than its absolute value:
        # an absolute value would silently introduce a free constant offset.
        coefficients = projected[:, user] / 2
        coefficients[0] = projected[0, user].real
        proposed_beta[user], _, count = stationary_maximum(coefficients, beta[user])
        roots += count
    proposed_beta = (proposed_beta + np.pi) % (2 * np.pi) - np.pi
    slope_phase = np.exp(1j * frames[:, None] * proposed_beta[None, :])
    before = quadratic_objective(old_phase, gram, matched)
    after_frame = quadratic_objective(projected, gram, matched)
    after_slope = quadratic_objective(slope_phase, gram, matched)
    tolerance = 1e-10 * max(1., abs(before), float(np.sum(abs(gram))), float(np.sum(abs(matched))))
    increased = bool(after_slope > before)
    rejected = bool(guard and increased)
    new_beta = beta.copy() if rejected else proposed_beta
    after = before if rejected else after_slope
    record = dict(
        method='Shen projected solve followed by common-slope projection',
        source='Shen et al., III-C (53); (49)-(52) define the posterior quadratic',
        adaptations=['Full supplied posterior quadratic; no strongest-tap truncation',
                     'Frame q=0 fixed to one', 'Per-user common slope fitted without constant offset'],
        guard=bool(guard), accepted=not rejected, rejected_objective_increase=rejected,
        before=before, after_frame_projection=after_frame,
        after_slope_projection=after_slope, after=after,
        objectives=[before, after_frame, after_slope, after],
        proposed_objective_increased=increased,
        proposed_objective_materially_increased=bool(after_slope > before + tolerance),
        applied_objective_increased=bool(after > before), objective_roundoff_tolerance=tolerance,
        objective_definition='phi^H G phi - 2 Re b^H phi; noise*I adds the constant noise*Q*K on unit-modulus phases',
        regularization_noise=float(noise), posterior_gram_hermitian_error=hermitian_error,
        linear_solve_residual_norm=float(np.linalg.norm(linear_residual)),
        linear_solve_relative_residual=linear_backward_error,
        unitmod_linear_residual_norm=float(np.linalg.norm(projected_residual)),
        unitmod_linear_relative_residual=float(np.linalg.norm(projected_residual) /
                                               max(float(projected_scale), np.finfo(float).tiny)),
        frame_unit_modulus_error=float(np.max(abs(abs(projected) - 1))),
        frame_zero_gauge_error=float(np.max(abs(projected[0] - 1))),
        numerical_zero_components_kept=int(np.sum(~valid)),
        numerical_zero_rule='abs(z_qk) <= 64*eps*max(1,max_k abs(z_qk)) keeps old phi_qk',
        stationary_roots=int(roots), fit_offset=False,
        slope_projection_squared_error=float(np.sum(abs(slope_phase - projected) ** 2)),
        guarantee=('Rejects any increase of this fixed quadratic; no guarantee across neural messages'
                   if guard else 'No monotonicity guarantee, even for this fixed quadratic'))
    return new_beta, np.zeros(k), record
