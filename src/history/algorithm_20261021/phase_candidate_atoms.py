"""First-derivative AFDM atoms for the candidate phase frontend.

Same formulas and contraction order as the frozen frontend; no second
derivatives are formed. The fixed DAFT matrix is cached by physical parameters.
"""
from functools import lru_cache
import numpy as np
from afdm_jadcedd.system import config as cfg
from afdm_jadcedd.system.afdm.path_operator_multicycle_full import daft_matrix
from afdm_jadcedd.algorithm.unknown_phase_model import FRAME_DURATION_S


@lru_cache(maxsize=4)
def geometry(n, c1, c2):
    r, s = np.arange(n)[:, None], np.arange(n)[None, :]
    transform = daft_matrix(n, c1, c2)
    for a in (r, s, transform):
        a.setflags(write=False)
    return r, s, transform


def path_atom(delay, frequency, derivatives=False):
    n = cfg.N
    if not (np.isfinite(delay) and np.isfinite(frequency) and 0 <= delay < n):
        raise ValueError('finite folded delay in [0,N) and frequency required')
    r, s, transform = geometry(n, cfg.C1, cfg.C2)
    eta = r-delay
    wrapped = np.remainder(eta, n)
    rho = np.floor(2*cfg.C1*wrapped+s/n)
    phase = (cfg.C2*s**2 + cfg.C1*(eta**2-delay**2)
             + s*wrapped/n-rho*wrapped+frequency*r/n)
    basis = np.exp(2j*np.pi*phase)/np.sqrt(n)
    def apply(x):
        return np.einsum('ri,is->rs', transform, x, optimize=False)
    h = apply(basis)
    if not derivatives:
        return h
    td = 2j*np.pi*(-2*cfg.C1*r-s/n+rho)
    tv = 2j*np.pi*r/n
    return h, np.stack([apply(basis*td), apply(basis*tv)])


def sensed_atom(pilot, user, position, derivatives=False):
    p = np.asarray(pilot, dtype=np.complex128)
    delay, frequency = position
    phase_derivative = 2*np.pi*cfg.DELTA_F_HZ*FRAME_DURATION_S*np.arange(len(p))[:, None]
    phase = np.exp(1j*phase_derivative*frequency)
    def sense(h):
        return np.einsum('qn,rn->qr', p[:, user], h, optimize=False)
    if not derivatives:
        return (phase*sense(path_atom(delay, frequency))).reshape(-1)
    h, first = path_atom(delay, frequency, derivatives=True)
    value = sense(h)
    hd, hf = (sense(item) for item in first)
    d = phase*hd
    f = phase*(hf+1j*phase_derivative*value)
    return (phase*value).reshape(-1), np.stack([d.ravel(), f.ravel()]), None
