"""Zhang Gaussian GAMP-SBL with shared MMV row precision and learned noise.

The complex Gamma MAP updates and project adaptation are documented in
docs/BASELINES.md. Public noise defines Gamma hyperparameters for the common
noise precision. Every antenna shares one row precision.
"""
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class MMVControls:
    iterations: int = 1000
    tolerance: float = 1e-6
    stopping_rule: str = 'paper_absolute_mean'
    alpha_shape: float = 1.
    alpha_rate: float = 1e-12
    noise_shape: float = 1.
    noise_rate: float = 1e-12
    initial_noise_fraction: float = .1
    variance_floor: float = 1e-12

    def __post_init__(self):
        if (type(self.iterations) is not int or self.iterations < 1
                or not 0 < self.initial_noise_fraction < 1
                or self.stopping_rule not in ('paper_absolute_mean', 'fixed')
                or not all(np.isfinite(x) and x > 0 for x in (
                    self.tolerance, self.alpha_shape, self.alpha_rate,
                    self.noise_shape, self.noise_rate, self.variance_floor))):
            raise ValueError('Positive finite MMV controls and a supported stopping rule required')


def solve_mmv(design, received, controls):
    """The frozen experimental MMV kernel, with no relaxation or refitting."""
    c = controls
    a, y = np.asarray(design, complex), np.asarray(received, complex)
    if (a.ndim != 2 or y.ndim != 2 or a.shape[0] != y.shape[0]
            or not a.size or not y.size or not all(np.isfinite(z).all() for z in (a, y))):
        raise ValueError('Finite nonempty MMV design and observations required')
    power = abs(a)**2
    ah = np.ascontiguousarray(a.conj().T)
    pt = np.ascontiguousarray(power.T)
    length, columns = y.shape
    floor = c.variance_floor
    energy = np.sum(abs(y)**2)/columns
    initial_noise = max(c.initial_noise_fraction*energy/length, floor)
    initial_variance = max((1-c.initial_noise_fraction)*energy/np.sum(power), floor)
    mean = np.zeros((a.shape[1], columns), complex)
    variance = np.full(mean.shape, initial_variance)
    alpha = np.full((a.shape[1], 1), 1/initial_variance)
    gamma = 1/initial_noise
    message = np.zeros_like(y)
    trace = []
    for iteration in range(1, c.iterations+1):
        vp = np.maximum(power@variance, floor)
        p = a@mean-vp*message
        noise = 1/gamma
        precision = 1/(vp+noise)
        message = (y-p)*precision
        output_mean = p+vp*message
        output_variance = vp*noise/(vp+noise)
        tau = 1/np.maximum(pt@precision, floor)
        r = mean+tau*(ah@message)
        gain = 1/(1+alpha*tau)
        new = gain*r
        variance = tau*gain
        alpha = (columns+c.alpha_shape-1)/(np.sum(abs(new)**2+variance, axis=1, keepdims=True)+c.alpha_rate)
        gamma = (length*columns+c.noise_shape-1)/(float(np.sum(abs(y-output_mean)**2+output_variance))+c.noise_rate)
        delta = np.sum(abs(new-mean)**2, axis=0)
        mean = new
        if not all(np.isfinite(z).all() for z in (mean, variance, alpha, gamma, message)):
            raise FloatingPointError(f'Nonfinite shared-precision GAMP state at iteration {iteration}')
        trace.append(dict(iteration=iteration, noise_variance=float(1/gamma),
                          max_column_mean_squared_change=float(delta.max())))
        if c.stopping_rule == 'paper_absolute_mean' and np.all(delta <= c.tolerance):
            break
    return dict(mean=mean, variance=variance, noise_variance=float(1/gamma), iterations=iteration,
                stopping_reason='MEAN_CHANGE_STOP' if iteration < c.iterations else 'MAX_ITERATIONS', trace=trace)

