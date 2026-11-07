"""SOMP with orthogonal residual updates and noise-discrepancy stopping."""
import numpy as np
from receiver.baseline._common import validate


def solve_somp(design, received, noise_variance=None, *, max_atoms=64, noise_multiplier=1.,
               stopping_rule='noise_discrepancy', observer=None, **unused):
    if stopping_rule not in ('noise_discrepancy', 'fixed_atoms'):
        raise ValueError('SOMP stopping_rule must be noise_discrepancy or fixed_atoms')
    if stopping_rule == 'noise_discrepancy' and noise_variance is None:
        raise ValueError('positive noise variance required for discrepancy stopping')
    # Tropp Algorithm 3.1 takes a stopping criterion as input; its fixed-T
    # numerical experiments do not require a noise-variance oracle.
    a, y = validate(design, received, 1. if stopping_rule == 'fixed_atoms' else noise_variance)
    if max_atoms < 1 or noise_multiplier <= 0:
        raise ValueError('positive SOMP budget and discrepancy factor required')
    if not np.allclose(np.linalg.norm(a, axis=0), 1., atol=1e-10):
        raise ValueError('SOMP expects unit-norm columns')
    residual, support, basis, trace = y.copy(), [], [], []
    excluded = np.zeros(a.shape[1], bool)
    threshold = (None if stopping_rule == 'fixed_atoms' else
                 max(noise_variance*y.size*noise_multiplier, 1e-20*np.sum(abs(y)**2)))
    adjoint = a.conj().T.copy()
    while len(support) < min(max_atoms, *a.shape):
        if threshold is not None and np.sum(abs(residual)**2) <= threshold:
            break
        scores = np.sum(abs(adjoint@residual), axis=1); scores[excluded] = -np.inf
        if not np.isfinite(scores).any():
            break
        index = int(np.argmax(scores)); excluded[index] = True
        direction = a[:, index].copy()
        if basis:
            q = np.stack(basis, axis=1)
            for _ in range(2):
                direction -= q@(q.conj().T@direction)
        length = np.linalg.norm(direction)
        if length <= 1e-10:
            continue
        direction /= length; basis.append(direction); support.append(index)
        residual -= direction[:, None]*(direction.conj()@y)[None]
        trace.append(dict(iteration=len(support), residual_energy=float(np.sum(abs(residual)**2))))
        if observer is not None:
            interim = np.zeros((a.shape[1], y.shape[1]), complex)
            interim[support] = np.linalg.lstsq(a[:, support], y, rcond=None)[0]
            observer(trace[-1], interim)
    x = np.zeros((a.shape[1], y.shape[1]), complex)
    if support:
        value, _, rank, _ = np.linalg.lstsq(a[:, support], y, rcond=None)
        if rank != len(support):
            raise FloatingPointError('SOMP rank-deficient accepted support')
        x[support] = value
    if stopping_rule == 'fixed_atoms':
        status = 'FIXED_ATOMS' if len(support) == max_atoms else 'RANK_LIMIT'
    else:
        if np.sum(abs(y-a@x)**2) <= threshold:
            status = 'NOISE_DISCREPANCY'
        elif len(support) >= max_atoms:
            status = 'MAX_ATOMS'
        elif np.sum(abs(residual)**2) <= threshold:
            # A finite-precision projection is not a certificate for the
            # actual least-squares coefficients returned to the receiver.
            status = 'RESIDUAL_CHECK_FAILED'
        else:
            status = 'RANK_LIMIT'
    return dict(mean=x, trace=trace, iterations=len(trace), support=support,
                status=status, stopping_rule=stopping_rule)

from channel.dictionary import AFDMGrid
from dataclasses import asdict
from dataclasses import replace


def infer_known(self, inputs, *, observer=None):
    grid = AFDMGrid.from_operator(inputs.operator, **self.configuration['dictionary'])
    y = grid.stack(inputs.observation)
    callback = None if observer is None else lambda row, z: observer(row, lambda: grid.reconstruct(z))
    result = solve_somp(grid.design, y, inputs.noise_variance,
                        observer=callback, **self.setting['solver'])
    z = result['mean']/grid.norms[:, None]
    estimate = grid.reconstruct(result['mean'])
    native = dict(iterations=result['iterations'], stopping_reason=result['status'],
                  trace=result['trace'], supplied_noise_variance_used=True)
    return dict(estimate=estimate, coefficients=z), native
