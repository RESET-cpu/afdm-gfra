"""Physical receiver inputs and separately returned simulation truth."""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import numpy as np
from .pilot import PartialDFTPilot
from .physics import PhysicalConfig, sample_channel
from .receiver.noise import noise_variance_from_reference_snr

def array_sha256(value):
    return hashlib.sha256(np.ascontiguousarray(value).tobytes()).hexdigest()


@dataclass(frozen=True)
class ReceiverInput:
    observation: np.ndarray  # [Q, antennas, Nout], physical complex units
    operator: np.ndarray     # [Q, users, Nin]
    noise_variance: float    # E|W|^2; each real component has half this variance
    activity_prior: float = .1

    def __post_init__(self):
        y, p = np.asarray(self.observation), np.asarray(self.operator)
        if (y.ndim != 3 or p.ndim != 3 or y.shape[0] != p.shape[0]
                or not all(y.shape) or not all(p.shape)
                or not np.isfinite(y).all() or not np.isfinite(p).all()
                or not np.isfinite(self.noise_variance) or self.noise_variance <= 0
                or not 0 < self.activity_prior < 1):
            raise ValueError('finite physical Y/P, positive complex noise variance and valid prior required')

    def arguments(self):
        return dict(observation=self.observation, operator=self.operator,
                    noise_variance=float(self.noise_variance), activity_prior=self.activity_prior)


@dataclass(frozen=True)
class ChannelTruth:
    channel: np.ndarray
    activity: np.ndarray
    scene: object


def simulate_observation(seed, snr_db, *, physics, frames=16, users=40,
                         activity_probability=.1, channel_scale=1., noise_draw_frames=32):
    """Coherent effective-pilot observation used by the registered Q16 experiment.

    Draw real and imaginary noise on the original 32-frame stream, then select Q.
    This explicit convention preserves paired Q16/Q32 observations. Pilots have
    unit energy per user per frame. Following the received-SNR convention in
    Shen 2025, Sec. V (R in Eq. 19 is noiseless), scale noise to clean received
    power. Empty scenes use K*rho*s^2 and have undefined received SNR.
    """
    if frames > noise_draw_frames or frames <= 0 or channel_scale <= 0:
        raise ValueError('invalid frame count or reference scale')
    scene, h, _ = sample_channel(seed, physics, users=users, frames=frames,
                                  activity_probability=activity_probability)
    active = np.asarray(scene.activity, bool)
    n = h.shape[-1]
    p = PartialDFTPilot(users, frames, seed+10**12,
                        input_size=n).dense().reshape(frames, users, n)
    clean=np.einsum('qkn,kmrn->qmr',p[:,active],h[active],optimize=True)
    signal_power = float(np.mean(abs(clean)**2))
    reference = signal_power if active.any() else channel_scale**2*users*activity_probability
    noise = noise_variance_from_reference_snr(reference, snr_db)
    rng = np.random.default_rng(np.random.SeedSequence([seed, 2096]))
    shape = (noise_draw_frames, h.shape[1], h.shape[2])
    raw = rng.normal(size=shape)+1j*rng.normal(size=shape)
    epsilon = (raw/np.sqrt(2))[:frames]
    y = clean+np.sqrt(noise)*epsilon
    metadata = dict(physics_version=physics.version, signal_power=signal_power,
                    snr_reference_power=reference, standardized_noise=array_sha256(epsilon),
                    observation=array_sha256(y), operator=array_sha256(p),
                    full_effective_h_sha256=array_sha256(h),
                    pilot_energy_per_user_per_frame=1., noise_draw_frames=noise_draw_frames,
                    phase_convention='coherent_effective_pilot',
                    population_version='candidate_population_v2',
                    noise_reference='clean received power; K*rho*s^2 for empty scenes only')
    return ReceiverInput(y, p, noise, activity_probability), ChannelTruth(h, active, scene), metadata


def load_input(path):
    with np.load(path, allow_pickle=False) as z:
        if set(z.files) != {'observation', 'operator', 'noise_variance', 'activity_prior'}:
            raise ValueError('Receiver input includes unexpected fields')
        return ReceiverInput(z['observation'], z['operator'], float(z['noise_variance']), float(z['activity_prior']))
