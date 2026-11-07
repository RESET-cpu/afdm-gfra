"""Unchanged Shen proposal, plus its expected observation-change diagnostic."""
import time
import numpy as np
from algorithm.C_STMP_phase_shen_frames_20261103.phase import rotations
from algorithm.C_STMP_phase_shen_frames_20261103.moments import conditional_quadratic, marginal_value


def signal_change(current, proposed, gram, noise_energy):
    """sqrt(E||A(new)H-A(old)H||² / (E||A(old)H||² + E||noise||²)).

    Expectations use the SAME fixed-Gaussian conditional moments as the
    existing phase update. This is a numerical stopping measure, not NMSE.
    """
    delta = proposed-current
    quadratic = lambda x: float(np.einsum('qk,qkl,ql->', x.conj(), gram, x).real)
    change, energy = quadratic(delta), quadratic(current)
    tolerance = 1e-10*max(1., float(np.sum(abs(gram))))
    if min(change, energy) < -tolerance or not np.isfinite(noise_energy) or noise_energy <= 0:
        raise ValueError('Positive conditional energies and noise energy required')
    return dict(expected_signal_change_squared=max(0., change),
                expected_signal_energy=max(0., energy), noise_energy=float(noise_energy),
                relative_signal_change=float(np.sqrt(max(0., change)/(max(0., energy)+noise_energy))))


def update(observation, pilot, mean, variance, noise, phase):
    started = time.perf_counter()
    gram, matched, moments = conditional_quadratic(observation, pilot, mean, variance, noise, phase)
    proposed, solver = rotations(phase, gram, matched, noise)
    before = marginal_value(observation, pilot, mean, variance, noise, phase)
    after = marginal_value(observation, pilot, mean, variance, noise, proposed)
    if not np.isfinite(before) or not np.isfinite(after):
        raise FloatingPointError('Nonfinite frozen Gaussian objective')
    tolerance = 1e-8*max(1., abs(before), abs(after))
    return proposed, dict(**solver, before=before, after=after,
        marginal_objective_increased=bool(after > before),
        marginal_objective_materially_increased=bool(after > before+tolerance),
        marginal_roundoff_tolerance=tolerance, moments=moments,
        phase_effect=signal_change(phase, proposed, gram, noise*np.asarray(observation).size),
        seconds=time.perf_counter()-started,
        before_phase_real=np.asarray(phase).real.tolist(), before_phase_imag=np.asarray(phase).imag.tolist(),
        after_phase_real=proposed.real.tolist(), after_phase_imag=proposed.imag.tolist())
