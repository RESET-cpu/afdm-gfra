"""Unknown cross-frame Doppler phase: inputs and physical AFDM atoms.

The public input contains the original pilot, never the truth-rotated operator.
One Doppler per user determines both the within-frame atom and frame phase.
These are model primitives, not a qualified activity/channel/phase estimator.
Phase-learning motivation: Shen et al., arXiv:2412.20806v1, Sec.III-C,
Eqs.(47)-(54). The AFDM parameterization and derivatives below are derived
from this project's forward model, not a reproduction of that OTFS receiver.
"""
import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import sys
import warnings

import numpy as np
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from afdm_jadcedd.algorithm.baselines.offgrid.atoms import path_atom
from afdm_jadcedd.experiment.generate import generate_case as known_phase_case
from afdm_jadcedd.system import config as cfg
from afdm_jadcedd.system.observation import ReceiverInput, array_sha256
from afdm_jadcedd.system.phase import phase_operator
from afdm_jadcedd.system.pilot import PartialDFTPilot
from afdm_jadcedd.utils import sha256

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


def generate_case(seed, snr_db, scale, **kwargs):
    known, truth, metadata = known_phase_case(seed, snr_db, scale, **kwargs)
    frames, users, n = known['operator'].shape
    # Regenerate from public pilot-design parameters, without reading beta.
    pilot = PartialDFTPilot(users, frames, seed + 10**12, input_size=n).dense().reshape(frames, users, n)
    inputs = UnknownPhaseInput(known['observation'], pilot, known['noise_variance'], known['activity_prior'])
    metadata.update(base_generator_version=metadata['generator_version'],
                    generator_version='unknown_phase_geometry_v1',
                    phase_scope='Unknown per-user cross-frame phase slope; true slope and Doppler are evaluation truth only',
                    phase_reference='q=0; constant phase is absorbed into complex path gains',
                    pilot_sha256=array_sha256(pilot),
                    public_input_fields=list(UnknownPhaseInput.__dataclass_fields__),
                    estimator_status='MODEL_PRIMITIVES_ONLY', source_sha256=sha256(Path(__file__)))
    return inputs, truth, metadata


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--snr', type=float, default=0.)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    with warnings.catch_warnings(record=True) as caught, threadpool_limits(1):
        warnings.simplefilter('always', RuntimeWarning)
        inputs, truth, metadata = generate_case(args.seed, args.snr, .2647966452702405)
    metadata['generation_warnings'] = [dict(message=str(w.message), filename=w.filename, line=w.lineno) for w in caught]
    args.output.mkdir(parents=True)
    np.savez_compressed(args.output / 'input.npz', **inputs.arguments())
    np.savez_compressed(args.output / 'truth.npz', **truth)
    (args.output / 'generation.json').write_text(json.dumps(metadata, indent=2)+'\n')
    print(json.dumps(dict(status='GENERATED_MODEL_PROTOTYPE', input=str(args.output / 'input.npz'),
                          public_input_fields=list(inputs.arguments()))))
