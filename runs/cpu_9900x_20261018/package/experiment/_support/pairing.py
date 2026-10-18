"""Persist the actual public and conditional arrays for cross-machine evaluation."""
import numpy as np
from .storage import read, save, sha, save_arrays, arrays
from afdm_jadcedd.system.observation import array_sha256, ReceiverInput
from afdm_jadcedd.algorithm.unknown_phase_model import UnknownPhaseInput


def _keep_arrays(path, values):
    expected = {k: array_sha256(v) for k, v in values.items()}
    if path.exists():
        actual = {k: array_sha256(v) for k, v in arrays(path).items()}
        if actual != expected:
            raise ValueError('Saved pairing arrays differ: ' + str(path))
    else:
        save_arrays(path, values)
    return dict(sha256=sha(path), arrays=expected)


def preserve(folder, inputs, conditional, truth, metadata):
    """Truth is stored separately and is never an argument to a receiver."""
    manifest = folder / 'PAIRING.json'
    # Verify a previous manifest before touching any file.
    if manifest.exists():
        verify(folder)
    files = {}
    for name, values in [('public.npz', inputs.arguments()),
                         ('operator.npz', dict(operator=conditional.operator)),
                         ('truth.npz', truth)]:
        files[name] = _keep_arrays(folder / name, values)
    for name in ('phase.npz', 'PHASE_CACHE.json', 'PHASE.json'):
        files[name] = dict(sha256=sha(folder / name))
    record = dict(schema='saved-experiment-inputs-v1', files=files,
                  generation=metadata, conditional_noise_variance=float(conditional.noise_variance),
                  information='Estimated phase and noise. noise_variance=1 is an unused placeholder; truth is scoring-only.')
    if manifest.exists() and read(manifest) != record:
        raise ValueError('Saved pairing metadata differs: ' + str(folder))
    save(manifest, record)
    return record


def verify(folder):
    record = read(folder / 'PAIRING.json')
    for name, identity in record['files'].items():
        if sha(folder / name) != identity['sha256']:
            raise ValueError('Pairing file changed: ' + str(folder / name))
    return record


def load(folder):
    """Read exact inference arrays, with separate scoring truth, on any machine."""
    record = verify(folder)
    public = arrays(folder / 'public.npz')
    inputs = UnknownPhaseInput(public['observation'], public['pilot'],
                               float(public['noise_variance']), float(public['activity_prior']))
    conditional = ReceiverInput(inputs.observation, arrays(folder / 'operator.npz')['operator'],
                                record['conditional_noise_variance'], inputs.activity_prior)
    return inputs, conditional, arrays(folder / 'truth.npz'), record
