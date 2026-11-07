"""MMV OAMP with a shared-row BG prior and common-rate EM.

Ma/Ping supplies the de-correlated linear and divergence-free nonlinear
modules. The MMV row posterior and shared-rate EM are explicit adaptations;
this implementation is not Ying's printed-equation algorithm. Stability for
the structured AFDM dictionary is an empirical claim requiring validation.
"""
from collections import deque
import numpy as np
from scipy.special import ndtr
from afdm_jadcedd.algorithm.baselines.common import validate, bg_moments


def relative(new, old):
    return float(np.linalg.norm(new-old)/max(np.linalg.norm(new), np.linalg.norm(old), 1e-30))


def solve_common_rate_oamp(design, received, noise_variance, *, controls,
                           channel_reconstruct=None, observer=None):
    a, y = validate(design, received, noise_variance)
    c = controls
    if c.stopping_rule == 'state' and channel_reconstruct is None:
        raise ValueError('channel reconstruction is required for the OAMP output-window stop')
    rows, n = a.shape
    m = y.shape[1]
    ah = a.conj().T.copy()
    eigen, u = np.linalg.eigh(a@ah)
    eigen = np.maximum(eigen, 0.)
    alpha = rows/n
    z = np.linspace(0, 10, 1024)[1:]
    tail = (1+z*z)*ndtr(-z)-z*np.exp(-z*z/2)/np.sqrt(2*np.pi)
    rho = np.array([[alpha*np.max((1-2*tail/alpha)/(1+z*z-2*tail))]])
    power = (np.sum(abs(y)**2)/m-rows*noise_variance)/np.sum(abs(a)**2)
    gamma = np.array([[max(power/rho.item(), c.variance_floor)]])
    v = np.array([[max(power, c.variance_floor)]])
    d = np.zeros((n, m), complex)
    x = d.copy()
    stride = c.oamp_window_stride or c.oamp_window_interval
    channels = deque(maxlen=c.oamp_window_interval//stride+1)
    trace = []
    stable = 0
    status = 'MAX_ITERATIONS' if c.stopping_rule != 'fixed' else 'FIXED_BUDGET'
    for iteration in range(1, c.iterations+1):
        residual = y-a@d
        gain = 1/(eigen[:, None]*v+noise_variance)
        gain *= n/np.sum(eigen[:, None]*gain, axis=0, keepdims=True)
        r = d+ah@(u@(gain*(u.conj().T@residual)))
        wa = eigen[:, None]*gain
        tau = (v*(n-2*wa.sum()+(wa**2).sum())+
               noise_variance*np.sum(gain**2*eigen[:, None]))/n
        mean, variance, pi, cm, cv = bg_moments(r, tau, gamma, rho, 0.)
        q = float(variance.mean())
        ratio = q/tau.item()
        if ratio >= 1:
            raise FloatingPointError('nonpositive OAMP extrinsic precision')
        next_d = (mean-ratio*r)/(1-ratio)
        next_v = tau*ratio/(1-ratio)
        next_gamma = np.array([[(pi*(abs(cm)**2+cv)).sum()/(m*pi.sum())]])
        next_rho = np.array([[np.clip(pi.mean(), 1e-8, 1-1e-8)]])
        raw = dict(probability=abs(next_rho.item()-rho.item()),
                   prior_variance=relative(next_gamma, gamma),
                   extrinsic=relative(next_d, d), coefficient=relative(mean, x),
                   variance=relative(next_v, v))
        coefficient_change = float(np.linalg.norm(mean-x)/max(np.linalg.norm(x), 1e-30))
        d = (1-c.damping)*d+c.damping*next_d
        v = (1-c.damping)*v+c.damping*next_v
        gamma, rho, x = next_gamma, next_rho, mean
        if not all(np.isfinite(value).all() for value in (d, v, gamma, rho, x, variance)):
            raise FloatingPointError('nonfinite common-rate OAMP state')
        raw_max = max(raw.values())
        statistic = coefficient_change if c.oamp_stopping_statistic == 'coefficient' else raw_max
        stable = stable+1 if statistic < c.tolerance else 0
        delta = None
        if c.stopping_rule == 'state' and iteration % stride == 0:
            channel = channel_reconstruct(x)
            channels.append(channel.copy())
            # More frequent checks retain the declared full window span.
            delta = None if len(channels) < channels.maxlen else relative(channel, channels[0])
        row = dict(iteration=iteration, raw=raw, raw_max=raw_max, stopping_statistic=statistic,
            coefficient_change=coefficient_change, stopping_statistic_kind=c.oamp_stopping_statistic,
            gamma=gamma.item(), rho=rho.item(), max_ratio=ratio,
            stable_iterations=stable, channel_window_change=delta,
            stopping_rule=c.stopping_rule, oamp_variant='group_bg_common_rate')
        trace.append(row)
        if observer is not None:
            observer(row, x)
        if (c.stopping_rule == 'state' and iteration >= c.min_iterations and
                stable >= c.convergence_patience and delta is not None and
                delta < c.oamp_window_tolerance):
            status = ('COEFFICIENT_AND_WINDOW_STOP' if c.oamp_stopping_statistic == 'coefficient'
                      else 'RAW_AND_WINDOW_STOP')
            break
    return dict(mean=x, variance=variance, row_probability=pi[:, 0], sparsity_rate=rho.item(),
                trace=trace, iterations=len(trace), status=status)
