"""Finite AFDM delay-Doppler dictionaries and the common MMV observation."""
from dataclasses import dataclass
from functools import lru_cache
import numpy as np
from afdm_jadcedd.system.afdm.continuous import continuous_path_matrix
from . import config as physical


@lru_cache(maxsize=8)
def physical_atoms(delay_step=.25, doppler_points=9, doppler_step_hz=None):
    if not np.isfinite(delay_step) or delay_step <= 0:
        raise ValueError('finite positive delay step required')
    delay = np.arange(0., physical.N, delay_step)
    if doppler_step_hz is None:
        if not isinstance(doppler_points, (int, np.integer)) or doppler_points < 2:
            raise ValueError('at least two integral Doppler points required')
        doppler = np.linspace(-physical.NU_MAX_HZ, physical.NU_MAX_HZ, doppler_points)
    else:
        if (doppler_points is not None or not np.isfinite(doppler_step_hz)
                or doppler_step_hz <= 0):
            raise ValueError('explicit Doppler step requires positive Hz and doppler_points=None')
        # Integer multiples of a physical frequency step. Include the outer
        # bins so the supplied maximum Doppler lies inside the grid span.
        limit = int(np.ceil(physical.NU_MAX_HZ/doppler_step_hz))
        doppler = np.arange(-limit, limit+1)*doppler_step_hz
    coordinates = np.array([(d, v) for d in delay for v in doppler])
    atoms = np.stack([continuous_path_matrix(physical.N, d, v, 1/physical.BANDWIDTH_HZ,
        physical.N_CPP, physical.C1, physical.C2) for d, v in coordinates])
    atoms.setflags(write=False); coordinates.setflags(write=False)
    return atoms, coordinates, (len(delay), len(doppler))


@dataclass
class AFDMGrid:
    design: np.ndarray
    norms: np.ndarray
    atoms: np.ndarray
    coordinates: np.ndarray
    grid_shape: tuple
    users: int
    frames: int

    @classmethod
    def from_operator(cls, operator, delay_step=.25, doppler_points=9, doppler_step_hz=None):
        p = np.asarray(operator, complex)
        atoms, coordinates, shape = physical_atoms(delay_step, doppler_points, doppler_step_hz)
        if p.ndim != 3 or p.shape[-1] != physical.N or not np.isfinite(p).all():
            raise ValueError('finite effective operator[frame,user,input] required')
        raw = np.einsum('qkn,grn->qrkg', p, atoms, optimize=True).reshape(p.shape[0]*physical.N, -1)
        norms = np.linalg.norm(raw, axis=0)
        if np.any(norms <= 0):
            raise ValueError('zero dictionary column')
        return cls(np.ascontiguousarray(raw/norms), norms, atoms, coordinates, shape, p.shape[1], p.shape[0])

    def stack(self, observation):
        y = np.asarray(observation, complex)
        if y.ndim != 3 or y.shape[0] != self.frames or y.shape[2] != physical.N:
            raise ValueError('observation[frame,antenna,output] required')
        return y.transpose(0, 2, 1).reshape(self.design.shape[0], -1)

    def reconstruct(self, coefficients):
        x = np.asarray(coefficients) / self.norms[:, None]
        return np.einsum('kgm,grn->kmrn', x.reshape(self.users, len(self.atoms), -1), self.atoms, optimize=True)

    def project(self, channel, operator):
        return np.einsum('qkn,kmrn->qmr', operator, channel, optimize=True)


def neighbor_average(probability, users, grid_shape):
    """Meng Eq.17: four nearest neighbours, no self, no wrapping between users."""
    p = np.asarray(probability).reshape(users, *grid_shape)
    total, count = np.zeros_like(p), np.zeros_like(p)
    total[:, 1:] += p[:, :-1]; count[:, 1:] += 1
    total[:, :-1] += p[:, 1:]; count[:, :-1] += 1
    total[:, :, 1:] += p[:, :, :-1]; count[:, :, 1:] += 1
    total[:, :, :-1] += p[:, :, 1:]; count[:, :, :-1] += 1
    if np.any(count == 0):
        raise ValueError('NNSPL needs a grid with neighbours')
    return (total/count).reshape(-1, 1)
