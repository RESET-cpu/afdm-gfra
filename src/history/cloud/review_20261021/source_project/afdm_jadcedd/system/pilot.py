"""Coherent partial-DFT pilot in full AFDM H input coordinates.

P includes the declared known cross-frame phase handling.
"""
from dataclasses import dataclass
import numpy as np

@dataclass
class PartialDFTPilot:
    users: int
    frames: int
    seed: int
    input_size: int = 16
    frame_power: float = 1.

    def __post_init__(self):
        self.dimension = self.users*self.input_size
        if not 0 < self.frames <= self.dimension or self.frame_power <= 0:
            raise ValueError('positive power and 0 < Q <= K*Nin required')
        rng = np.random.default_rng(self.seed)
        self.rows = rng.permutation(self.dimension)[:self.frames]
        self.columns = rng.permutation(self.dimension)
        self.phases = np.exp(2j*np.pi*rng.random(self.dimension))
        self.amplitude = np.sqrt(self.frame_power/self.input_size)
        self.row_gram = self.users*self.frame_power

    def forward(self, x):
        x = np.asarray(x)
        if x.shape[0] != self.dimension: raise ValueError('wrong number of channel coordinates')
        tmp = np.empty_like(x, dtype=np.complex128)
        shape = (self.dimension,)+(1,)*(x.ndim-1)
        tmp[self.columns] = self.phases.reshape(shape)*x
        return self.amplitude*np.fft.fft(tmp, axis=0)[self.rows]

    def adjoint(self, y):
        y = np.asarray(y)
        if y.shape[0] != self.frames: raise ValueError('wrong number of observations')
        tmp = np.zeros((self.dimension, *y.shape[1:]), dtype=np.complex128)
        tmp[self.rows] = y
        shape = (self.dimension,)+(1,)*(y.ndim-1)
        return (self.amplitude*self.dimension)*self.phases.conj().reshape(shape)*np.fft.ifft(tmp, axis=0)[self.columns]

    def dense(self):
        """Return the explicit (Q, K*Nin) matrix consumed by module A."""
        return self.amplitude*np.exp(-2j*np.pi*self.rows[:, None]*self.columns/self.dimension)*self.phases


@dataclass
class PerUserDFTPilot:
    """Each Q x N user block has orthogonal rows, for Q <= N.

    P_k P_k^H = frame_power I makes sum_k D_k P_k P_k^H D_k^H
    invariant under user-specific unit-modulus diagonal frame phases.
    """
    users: int
    frames: int
    seed: int
    input_size: int = 16
    frame_power: float = 1.

    def __post_init__(self):
        if (self.users < 1 or not 0 < self.frames <= self.input_size
                or not np.isfinite(self.frame_power) or self.frame_power <= 0):
            raise ValueError('Per-user row-orthogonal pilots require users>0 and 0<Q<=N')
        self.row_gram = self.users*self.frame_power

    def dense(self):
        rng = np.random.default_rng(self.seed)
        n = self.input_size
        blocks = []
        for _ in range(self.users):
            rows, columns = rng.permutation(n)[:self.frames], rng.permutation(n)
            phases = np.exp(2j*np.pi*rng.random(n))
            blocks.append(np.sqrt(self.frame_power/n)*
                np.exp(-2j*np.pi*rows[:, None]*columns/n)*phases)
        return np.stack(blocks, axis=1).reshape(self.frames, self.users*n)
