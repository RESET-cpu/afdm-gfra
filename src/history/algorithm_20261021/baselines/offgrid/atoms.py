"""Physical AFDM atoms and derivatives within each wrapped-chirp delay interval.

Delay is in samples; frequency is in subcarrier spacings. A removable scalar
phase is absorbed into the free complex path gain. See docs/OFFGRID_BASELINES.md.
"""
from functools import lru_cache
import numpy as np
from afdm_jadcedd.system import config as physical
from afdm_jadcedd.system.afdm.path_operator_multicycle_full import daft_matrix

ORDER = int(round(2 * physical.N * physical.C1))
MAX_FREQUENCY = physical.NU_MAX_HZ / physical.DELTA_F_HZ


def path_atom(delay, frequency, derivatives=False):
    """Return H, first derivatives [d,v], and second derivatives [dd,dv,vv]."""
    n = physical.N
    if not (np.isfinite(delay) and np.isfinite(frequency) and 0 <= delay < n):
        raise ValueError("finite folded delay in [0,N) and frequency required")
    r, s = np.arange(n)[:, None], np.arange(n)[None, :]
    eta = r - delay
    wrapped = np.remainder(eta, n)
    rho = np.floor(2 * physical.C1 * wrapped + s / n)
    phase = (physical.C2*s**2 + physical.C1*(eta**2-delay**2)
             + s*wrapped/n - rho*wrapped + frequency*r/n)
    basis = np.exp(2j*np.pi*phase)/np.sqrt(n)
    transform = daft_matrix(n, physical.C1, physical.C2)
    apply = lambda x: np.einsum("ri,is->rs", transform, x, optimize=False)
    h = apply(basis)
    if not derivatives:
        return h
    # rho and the wrap index are constant strictly inside a delay interval.
    td = 2j*np.pi*(-2*physical.C1*r-s/n+rho)
    tv = 2j*np.pi*r/n
    first = np.stack([apply(basis*td), apply(basis*tv)])
    second = np.stack([apply(basis*td**2), apply(basis*td*tv), apply(basis*tv**2)])
    return h, first, second


def delay_bounds(delay):
    cell = min(int(np.floor(delay*ORDER)), physical.N*ORDER-1)
    # Stay on the same differentiable branch, including near a wrap point.
    return np.array([cell/ORDER+1e-10, (cell+1)/ORDER-1e-10])


@lru_cache(maxsize=4)
def sampling_grid(doppler_step=.5):
    if not np.isfinite(doppler_step) or doppler_step <= 0:
        raise ValueError("positive Doppler grid step required")
    delays = (np.arange(physical.N*ORDER)+.5)/ORDER
    frequencies = np.linspace(-MAX_FREQUENCY, MAX_FREQUENCY,
                               int(np.ceil(2*MAX_FREQUENCY/doppler_step))+1)
    coordinates = np.array([(d,v) for d in delays for v in frequencies])
    atoms = np.stack([path_atom(d,v) for d,v in coordinates])
    atoms.setflags(write=False); coordinates.setflags(write=False)
    return atoms, coordinates, float(frequencies[1]-frequencies[0])


def stack_observation(observation):
    y = np.asarray(observation, complex)
    return np.ascontiguousarray(y.transpose(0,2,1).reshape(-1,y.shape[1]))


def sensed_atom(operator, user, position, derivatives=False):
    def sense(h):
        return np.einsum("qn,rn->qr", operator[:,user], h, optimize=False).reshape(-1)
    if not derivatives:
        return sense(path_atom(*position))
    h, first, second = path_atom(*position, derivatives=True)
    return sense(h), np.stack([sense(h) for h in first]), np.stack([sense(h) for h in second])


def coarse_dictionary(operator, doppler_step=.5):
    atoms, coordinates, spacing = sampling_grid(doppler_step)
    # [observation, user*grid]. Shared by detection and SBL screening.
    raw = np.einsum("qkn,grn->qrkg", operator, atoms, optimize=True).reshape(
        operator.shape[0]*physical.N, -1)
    norms = np.linalg.norm(raw,axis=0)
    if np.any(norms <= 0):
        raise ValueError("nonzero public dictionary columns required")
    return np.ascontiguousarray(raw/norms), norms, coordinates, spacing


def reconstruct(users, antennas, user_ids, positions, gains):
    h = np.zeros((users,antennas,physical.N,physical.N),complex)
    for user, position, gain in zip(user_ids,positions,gains):
        h[user] += gain[:,None,None]*path_atom(*position)[None]
    return h


def activity_score(channel):
    energy = np.sum(abs(channel)**2,axis=(1,2,3))
    peak = float(energy.max(initial=0.))
    return energy/peak if peak > 0 else np.zeros_like(energy), energy
