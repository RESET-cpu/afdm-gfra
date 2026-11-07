"""Public inputs and AFDM atoms for estimating unknown cross-frame phase.

The input exposes the original pilot. The within-frame atom and cross-frame
phase share one physical Doppler per user. Constant phase belongs to the path
gain. Promoted from experiments/unknown_phase_20261015/model.py; source and
formula references are recorded in docs/TERMINOLOGY.md.
"""
from dataclasses import dataclass

import numpy as np

from system.receiver.atoms import path_atom
from system import config as cfg
from system.observation import ReceiverInput
from system.phase import phase_operator

FRAME_DURATION_S = (cfg.N + cfg.N_CPP) / cfg.BANDWIDTH_HZ


@dataclass(frozen=True)
class UnknownPhaseInput:
    observation: np.ndarray
    pilot: np.ndarray
    noise_variance: float
    activity_prior: float

    def __post_init__(self):
        # Reuse dimension/finiteness checks only; pilot is not a known operator.
        ReceiverInput(self.observation, self.pilot, self.noise_variance, self.activity_prior)

    def arguments(self):
        return dict(observation=self.observation, pilot=self.pilot,
                    noise_variance=float(self.noise_variance), activity_prior=float(self.activity_prior))

    def at_estimated_phase(self, slopes):
        """Build the conditional linear problem from caller-supplied estimates."""
        return ReceiverInput(self.observation, phase_operator(self.pilot, slopes),
                             self.noise_variance, self.activity_prior)


def load_input(path):
    with np.load(path, allow_pickle=False) as saved:
        if set(saved.files) != set(UnknownPhaseInput.__dataclass_fields__):
            raise ValueError('Unknown-phase input requires observation, pilot, noise_variance, activity_prior')
        return UnknownPhaseInput(saved['observation'], saved['pilot'],
                                 float(saved['noise_variance']), float(saved['activity_prior']))



def sensed_atom(pilot, user, position, derivatives=False):
    """A path in all frames; position=(folded delay, Doppler/DELTA_F_HZ).

    All paths assigned to a user must share the same frequency in a receiver.
    Delay derivatives apply strictly within the wrapped-chirp delay branch.
    A scalar path phase is absorbed into the free complex path gain, as in the
    existing off-grid model; frame-to-frame phase is retained explicitly.
    """
    p = np.asarray(pilot, dtype=np.complex128)
    if p.ndim != 3 or p.shape[-1] != cfg.N or not 0 <= user < p.shape[1] or not np.isfinite(p).all():
        raise ValueError('Finite pilot[frame,user,input] and valid user required')
    delay, frequency = position
    phase_derivative = 2*np.pi*cfg.DELTA_F_HZ*FRAME_DURATION_S*np.arange(len(p))[:, None]
    phase = np.exp(1j*phase_derivative*frequency)

    def sense(h):
        return np.einsum('qn,rn->qr', p[:, user], h, optimize=False)

    if not derivatives:
        return (phase*sense(path_atom(delay, frequency))).reshape(-1)
    h, first, second = path_atom(delay, frequency, derivatives=True)
    value = sense(h)
    hd, hf = (sense(item) for item in first)
    hdd, hdf, hff = (sense(item) for item in second)
    d = phase*hd
    f = phase*(hf + 1j*phase_derivative*value)
    dd = phase*hdd
    df = phase*(hdf + 1j*phase_derivative*hd)
    ff = phase*(hff + 2j*phase_derivative*hf - phase_derivative**2*value)
    return (phase*value).reshape(-1), np.stack([d.ravel(), f.ravel()]), np.stack([dd.ravel(), df.ravel(), ff.ravel()])

