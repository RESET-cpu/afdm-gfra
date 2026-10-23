"""Real-equivalent complex D-AMP: He et al. (2018), Eqs. (4)-(8).

The denoiser acts on each user's full [antenna, output, input] channel block.
The Monte Carlo trace and measurement count both use REAL coordinates.
No state-evolution guarantee is asserted for the structured AFDM operator.
"""
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Controls:
    iterations: int = 10
    divergence_seed: int = 20261014071
    epsilon_relative: float = .001
    epsilon_floor: float = 1e-5


def forward(p, h):
    return np.einsum('qkn,kmrn->qmr', p, h, optimize=False)


def adjoint(p, y):
    return np.einsum('qkn,qmr->kmrn', p.conj(), y, optimize=False)


def real_divergence(denoise, query, estimate, probe, epsilon, variance):
    """Hutchinson finite difference in the 2*n dimensional real representation."""
    shifted = denoise(query + epsilon*probe, variance)
    return float(np.vdot(probe, shifted-estimate).real/epsilon)


def solve(inputs, denoise, *, scale, controls=Controls(), observer=None):
    if (scale <= 0 or not np.isfinite(scale) or controls.iterations < 1
            or controls.epsilon_relative <= 0 or controls.epsilon_floor <= 0):
        raise ValueError('Positive scale, iteration count and finite-difference step required')
    p = np.asarray(inputs.operator, np.complex128)
    # A unit average column norm is required by the AMP step-size convention.
    gain = float(np.sqrt(np.sum(abs(p)**2)/(p.shape[1]*p.shape[2])))
    if gain <= 0:
        raise ValueError('Nonzero public observation operator required')
    a, y = p/gain, np.asarray(inputs.observation)/(scale*gain)
    x = np.zeros((p.shape[1], y.shape[1], y.shape[2], p.shape[2]), complex)
    z = y.copy()
    rng = np.random.default_rng(controls.divergence_seed)
    trace = []
    for step in range(controls.iterations):
        query = x + adjoint(a, z)
        variance = float(np.mean(abs(z)**2))
        estimate = np.asarray(denoise(query, variance), complex)
        if estimate.shape != x.shape or not np.isfinite(estimate).all():
            raise FloatingPointError('Invalid L-DAMP denoiser output')
        # Two independent N(0,1) probes: no 1/sqrt(2), since this is a real trace.
        probe = rng.standard_normal(x.shape)+1j*rng.standard_normal(x.shape)
        amplitude = max(float(abs(query.real).max()), float(abs(query.imag).max()))
        epsilon = max(controls.epsilon_floor, controls.epsilon_relative*amplitude)
        divergence = real_divergence(denoise, query, estimate, probe, epsilon, variance)
        onsager = divergence/(2*y.size)
        residual = y-forward(a, estimate)
        next_z = residual+onsager*z
        if not np.isfinite(next_z).all():
            raise FloatingPointError('Nonfinite L-DAMP iterate')
        row = dict(iteration=step+1, effective_complex_variance=float(np.mean(abs(z)**2)),
                   divergence_real=divergence, onsager_coefficient=onsager, epsilon=epsilon,
                   residual_energy=float(np.sum(abs(residual)**2)),
                   relative_update=float(np.linalg.norm(estimate-x)/max(np.linalg.norm(estimate), 1e-12)))
        x, z = estimate, next_z
        trace.append(row)
        if observer is not None:
            observer(dict(row), lambda value=x.copy(): scale*value)
    return dict(estimate=scale*x, trace=trace, iterations=len(trace),
                stopping_reason='FIXED_LAYER_BUDGET', operator_normalization=gain)
