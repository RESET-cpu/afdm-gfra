"""Expose original pilots while preserving the paired physical observation draw."""
from .generate import generate_case as generate_known_phase_case
from afdm_jadcedd.algorithm.unknown_phase_model import UnknownPhaseInput
from afdm_jadcedd.system.pilot import PartialDFTPilot
from afdm_jadcedd.system.observation import array_sha256


def generate_case(seed, snr_db, scale, **kwargs):
    known, truth, metadata = generate_known_phase_case(seed, snr_db, scale, **kwargs)
    frames, users, n = known['operator'].shape
    pilot = PartialDFTPilot(users, frames, seed+10**12, input_size=n).dense().reshape(frames, users, n)
    public = UnknownPhaseInput(known['observation'], pilot, known['noise_variance'], known['activity_prior'])
    metadata.update(base_generator_version=metadata['generator_version'],
        generator_version='unknown_phase_geometry_v1', phase_mode='estimated',
        phase_scope='Unknown per-user cross-frame phase estimated by the receiver',
        phase_reference='q=0; constant phase is absorbed into complex path gains',
        pilot_sha256=array_sha256(pilot), public_input_fields=list(UnknownPhaseInput.__dataclass_fields__))
    return public.arguments(), truth, metadata
