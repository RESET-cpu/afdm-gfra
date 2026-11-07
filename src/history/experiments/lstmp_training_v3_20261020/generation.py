"""Use the formal experiment's existing 33--48-frame extension."""
import numpy as np
from afdm_jadcedd.experiment.generate import generate_case as original_generate_case
from afdm_jadcedd.system.phase import phase_operator
from afdm_jadcedd.system.pilot import PartialDFTPilot


def generate_case(seed, snr_db, scale, *, frames=16, users=40, **kwargs):
    if not isinstance(frames, (int, np.integer)) or not 1 <= frames <= min(48, users * 16):
        raise ValueError('Pilot frames must be in [1, min(48, users*16)]')
    if frames <= 32:
        return original_generate_case(seed, snr_db, scale, frames=frames, users=users, **kwargs)
    # Same construction as experiment/_common.py:observation, retaining the
    # exact known operator/noise for this controlled receiver experiment.
    inputs, truth, metadata = original_generate_case(
        seed, 0., scale, frames=32, users=users, **kwargs)
    clean32 = np.einsum('qkn,kmrn->qmr', inputs['operator'], truth['channel'], optimize=False)
    epsilon32 = (inputs['observation'] - clean32) / np.sqrt(inputs['noise_variance'])
    pilot = PartialDFTPilot(users, frames, seed + 10**12,
                            input_size=16).dense().reshape(frames, users, 16)
    original_pilot = PartialDFTPilot(users, 32, seed + 10**12,
                                     input_size=16).dense().reshape(32, users, 16)
    np.testing.assert_array_equal(pilot[:32], original_pilot)
    operator = phase_operator(pilot, truth['phase_slopes'])
    rng = np.random.default_rng(np.random.SeedSequence([seed, 2097]))
    shape = (16, *epsilon32.shape[1:])
    extra = (rng.normal(size=shape) + 1j * rng.normal(size=shape)) / np.sqrt(2)
    epsilon = np.concatenate([epsilon32, extra[:frames-32]])
    clean = np.einsum('qkn,kmrn->qmr', operator, truth['channel'], optimize=False)
    power = float(np.mean(abs(clean)**2))
    variance = power * 10**(-float(snr_db) / 10)
    return (dict(inputs, observation=clean + np.sqrt(variance) * epsilon,
                 operator=operator, noise_variance=variance),
            truth, dict(metadata, frames=frames, snr_db=float(snr_db),
                        noise_variance=variance, physical_clean_power=power,
                        frame_extension='paired_33_to_48_v1', extension_noise_seed=[seed, 2097]))
