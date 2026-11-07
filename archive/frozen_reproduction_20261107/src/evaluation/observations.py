"""Paired observations and observation-only phase estimation."""
import warnings
from dataclasses import asdict
import numpy as np
from .storage import save_arrays, arrays
from utils import read_json, write_json, sha256
from system.receiver import phase_estimation as phase
from system.receiver.unknown_phase import UnknownPhaseInput
from system.scenario.unknown_phase import generate_case
from system.observation import array_sha256
from system.phase import phase_operator
from system.pilot import PartialDFTPilot

def observation(seed, parameters, scale, *, generator=generate_case):
    """Use the completed 500-scene protocol's zero-dB draw and paired noise."""
    kwargs = {k: parameters[k] for k in ('frames', 'users', 'activity_probability')}
    frames = int(kwargs['frames'])
    if not 1 <= frames <= min(48, int(kwargs['users'])*16):
        raise ValueError('Pilot frames must be in [1, min(48, users*16)]')
    kwargs['frames'] = min(frames, 32)
    if 'channel_model' in parameters:
        public, truth, metadata = generator(seed, 0., scale, profile=parameters['channel_model'], **kwargs)
    else:
        public, truth, metadata = generator(seed, 0., scale, **kwargs)
    clean = np.einsum('qkn,kmrn->qmr', phase_operator(public['pilot'], truth['phase_slopes']),
                      truth['channel'], optimize=False)
    power = float(np.mean(abs(clean)**2))
    epsilon = (public['observation'] - clean) / np.sqrt(public['noise_variance'])
    pilot = public['pilot']
    if frames > 32:
        # Preserve the frozen generator and all <=32-frame numerical results.
        pilot = PartialDFTPilot(parameters['users'], frames, seed+10**12).dense().reshape(frames, parameters['users'], 16)
        np.testing.assert_array_equal(pilot[:32], public['pilot'])
        rng = np.random.default_rng(np.random.SeedSequence([seed, 2097]))
        shape = (16, *epsilon.shape[1:])
        extra = (rng.normal(size=shape)+1j*rng.normal(size=shape))/np.sqrt(2)
        epsilon = np.concatenate([epsilon, extra[:frames-32]])
        clean = np.einsum('qkn,kmrn->qmr', phase_operator(pilot, truth['phase_slopes']), truth['channel'], optimize=False)
        power = float(np.mean(abs(clean)**2))
        metadata = dict(metadata, frames=frames, parent_generator_version=metadata['generator_version'],
                        generator_version='unknown_phase_extended_frames_v1', frame_extension='paired_33_to_48_v1',
                        extension_noise_seed=[seed, 2097], pilot_sha256=array_sha256(pilot),
                        standardized_noise_sha256=array_sha256(epsilon), physical_clean_power=power)
    variance = power * 10**(-parameters['snr_db'] / 10)
    # Only observation, pilot and prior go to the estimated-noise receiver.
    inputs = UnknownPhaseInput(clean + np.sqrt(variance)*epsilon, pilot, 1., public['activity_prior'])
    metadata = dict(metadata, snr_db=parameters['snr_db'], noise_mode='estimated',
                    generated_noise_variance=variance)
    if frames > 32:
        metadata['noise_variance'] = variance
    return inputs, truth, metadata


def estimated_phase(inputs, folder, controls, *, reused=None):
    """Reuse a verified local or historical phase estimate before computing it."""
    identity = dict(inputs={k: array_sha256(v) for k, v in inputs.arguments().items()}, controls=asdict(controls))
    cache = folder / 'PHASE_CACHE.json'
    if cache.exists():
        saved = read_json(cache)
        if saved['identity'] != identity or saved['phase_sha256'] != sha256(folder / 'phase.npz'):
            raise ValueError('Saved phase input, configuration or arrays changed')
        return arrays(folder / 'phase.npz'), read_json(folder / 'PHASE.json')
    if reused is None:
        with warnings.catch_warnings(record=True) as notices:
            warnings.simplefilter('always', RuntimeWarning)
            values, record = phase.estimate(inputs, controls)
        notices = [str(w.message) for w in notices]
    else:
        values, record, notices = reused
    save_arrays(folder / 'phase.npz', values)
    write_json(folder / 'PHASE.json', record)
    write_json(folder / 'PHASE_WARNINGS.json', notices)
    write_json(cache, dict(identity=identity, phase_sha256=sha256(folder / 'phase.npz'), reused=reused is not None))
    return values, record
