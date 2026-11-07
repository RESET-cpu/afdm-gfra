"""A single Gaussian conditional family, shaped by independent pilot operators."""
import numpy as np
from scipy.linalg import cho_factor, cho_solve
from system.pilot import PartialDFTPilot
from system.phase import phase_operator


def build_pool(seed, operators):
    rng = np.random.default_rng(seed)
    values, vectors = [], []
    for _ in range(operators):
        a = PartialDFTPilot(40, 16, int(rng.integers(2**31))).dense().reshape(16, 40, 16)
        a = phase_operator(a, rng.uniform(-np.pi, np.pi, 40)).transpose(1, 0, 2)
        # A continuous family of proper incoming covariance matrices. None of
        # these operators, slopes, or moment scales come from evaluation cases.
        g = (rng.normal(size=(40, 16, 4))+1j*rng.normal(size=(40, 16, 4)))/np.sqrt(2)
        gram = g@g.conj().transpose(0, 2, 1)
        gram *= (16/np.trace(gram, axis1=1, axis2=2).real)[:, None, None]
        alpha = rng.uniform(0, .9, (40, 1, 1))
        v = ((1-alpha)*np.eye(16)+alpha*gram)*np.exp(rng.uniform(np.log(1e-5), 0, (40, 1, 1)))
        av = a@v@a.conj().transpose(0, 2, 1)
        noise = np.exp(rng.uniform(np.log(1e-3), np.log(100)))
        for k in range(40):
            s = noise*np.eye(16)+av[np.arange(40)!=k].sum(0)
            precision = a[k].conj().T@cho_solve(cho_factor(s, lower=True), a[k])
            precision = (precision+precision.conj().T)/2
            eig, u = np.linalg.eigh(precision)
            if eig.min() <= 0:
                raise FloatingPointError('Nonpositive generated likelihood; preserve failure')
            values.append(eig/eig.mean()); vectors.append(u)
    return dict(values=np.asarray(values, np.float32), vectors=np.asarray(vectors, np.complex64))


def draw(bank, chosen, pool, rng, scale, precision_range):
    h = np.asarray(bank[chosen])
    clean = np.stack((h.real, h.imag), 1).astype(np.float32)/scale
    ids = rng.integers(len(pool['values']), size=len(chosen))
    power = np.exp(rng.uniform(np.log(precision_range[0]), np.log(precision_range[1]), len(chosen)))
    lam = (pool['values'][ids]*power[:, None]).astype(np.float32)
    positive_noise = rng.standard_normal(clean.shape).astype(np.float32)
    negative_noise = rng.standard_normal(clean.shape).astype(np.float32)
    return clean, positive_noise, negative_noise, pool['vectors'][ids], lam
