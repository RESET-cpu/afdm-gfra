"""Continuous geometric/local delay scenes with fixed physical fading power."""
from dataclasses import dataclass
import math
import numpy as np
from afdm_jadcedd.system.core.upa import directional_cosines, steering_vector_operator
from afdm_jadcedd.system.afdm.continuous import continuous_path_matrix
from afdm_jadcedd.system import config as cfg
from . import scene_generator as geo
from .geometry import integer_delay_samples


@dataclass(frozen=True)
class ContinuousPath:
    user_id: int
    path_id: int
    macro_delay_s: float
    normalized_delay: float
    delay_spread_s: float
    gain: complex
    legacy_gain: complex
    doppler_hz: float
    mu_z: float
    mu_y: float

    @property
    def delay_s(self):
        return self.macro_delay_s + self.normalized_delay * self.delay_spread_s


@dataclass(frozen=True)
class ContinuousScene:
    activity: np.ndarray
    paths: tuple[ContinuousPath, ...]
    seed: int

    def paths_of(self, user):
        return tuple(p for p in self.paths if p.user_id == user)


def draw_scene(seed, *, n_users=40, activity_probability=.1, spread_range_s=(30e-9, 50e-9)):
    """Draw a full candidate population, independently of its activity mask.

    Every candidate has geometry, Doppler and channel parameters. Separate
    random streams bind those parameters to user identities, not active-user
    ranks. Activity only determines which candidates transmit.
    """
    lo, hi = spread_range_s
    if not 0 < lo <= hi:
        raise ValueError('invalid delay-spread range')
    rng = np.random.default_rng(seed)
    gamma = geo.sample_beam_central_angle(rng)
    sat = np.array([0., 0., cfg.EARTH_RADIUS_M + cfg.ORBIT_ALTITUDE_M])
    speed = math.sqrt(geo.MU_EARTH / (cfg.EARTH_RADIUS_M + cfg.ORBIT_ALTITUDE_M))
    velocity = np.array([speed, 0., 0.])
    beam_azimuth = float(rng.uniform(0., 2. * np.pi))
    center = geo._rotate_about_z(cfg.EARTH_RADIUS_M * np.array(
        [math.sin(gamma), 0., math.cos(gamma)]), beam_azimuth)
    east = geo._rotate_about_z(np.array([0., 1., 0.]), beam_azimuth)
    north = geo._rotate_about_z(np.array([math.cos(gamma), 0., -math.sin(gamma)]), beam_azimuth)
    closest = geo._closest_ground_in_beam(center, east, north)
    tau_c = float(np.linalg.norm(sat - closest) / geo.C_LIGHT_M_S)
    activity_rng = np.random.default_rng(np.random.SeedSequence([seed, 7102]))
    activity = geo.generate_activity(activity_rng, n_users, activity_probability=activity_probability)
    paths = []
    for user in range(n_users):
        rng = np.random.default_rng(np.random.SeedSequence([seed, 7101, user]))
        spread_rng = np.random.default_rng(np.random.SeedSequence([seed, 3050, user]))
        radius = cfg.BEAM_RADIUS_M * math.sqrt(float(rng.random()))
        angle = float(rng.uniform(0., 2. * np.pi))
        ground = cfg.EARTH_RADIUS_M * geo._unit(
            center + radius * math.cos(angle) * east + radius * math.sin(angle) * north)
        if geo._elevation_from_vectors(ground, sat) < cfg.MIN_ELEVATION_RAD - 1e-8:
            raise ValueError('user outside the current satellite service region')
        slant = sat - ground
        tau, nu = geo._require_support(
            float(np.linalg.norm(slant) / geo.C_LIGHT_M_S - tau_c),
            float(cfg.CARRIER_HZ / geo.C_LIGHT_M_S * np.dot(velocity, geo._unit(slant))))
        zenith = float(rng.uniform(cfg.ZENITH_MIN_RAD, cfg.ZENITH_MAX_RAD))
        azimuth = float(rng.uniform(cfg.AZIMUTH_MIN_RAD, cfg.AZIMUTH_MAX_RAD))
        mu_z, mu_y = directional_cosines(zenith, azimuth)
        spread = float(spread_rng.uniform(lo, hi))
        for index, (norm, power_db, kind) in enumerate(zip(
                cfg.NTN_TDL_D_NORMALIZED_DELAYS, cfg.NTN_TDL_D_POWER_DB,
                cfg.NTN_TDL_D_FADING, strict=True)):
            power = 10.**(power_db / 10.)
            if kind == 'los':
                k = 10.**(cfg.RICIAN_K_DB / 10.)
                phasor = np.exp(1j * rng.uniform(0., 2. * np.pi))
                diffuse = rng.normal() + 1j * rng.normal()
                gain = math.sqrt(power) * phasor
                legacy = math.sqrt(power) * (math.sqrt(k / (k + 1.)) * phasor
                         + math.sqrt(1. / (2. * (k + 1.))) * diffuse)
            else:
                scale = math.sqrt(power / 2.)
                gain = rng.normal(scale=scale) + 1j * rng.normal(scale=scale)
                legacy = gain
            path = ContinuousPath(int(user), index, tau, norm, spread,
                                  complex(gain), complex(legacy), nu, mu_z, mu_y)
            if path.delay_s > cfg.TAU_MAX_S + 1e-15:
                raise ValueError('continuous path exceeds the physical support')
            paths.append(path)
    return ContinuousScene(activity, tuple(paths), int(seed))


def user_channel(paths, *, delay_mode='continuous', gain_model='standard',
                 spread_s=None, start=cfg.N_CPP, array=None):
    """Return one full physical H[M,N,N], preserving fading and array power."""
    if delay_mode not in ('continuous', 'integer') or gain_model not in ('standard', 'legacy'):
        raise ValueError('unknown physical representation')
    array = cfg.upa4x4() if array is None else array
    array.validate()
    h = np.zeros((array.M, cfg.N, cfg.N), dtype=np.complex128)
    for path in paths:
        delay_s = path.macro_delay_s + path.normalized_delay * (
            path.delay_spread_s if spread_s is None else spread_s)
        if not 0 <= delay_s <= cfg.TAU_MAX_S + 1e-15:
            raise ValueError('path delay outside declared support')
        delay = delay_s * cfg.BANDWIDTH_HZ
        if delay_mode == 'integer':
            delay = integer_delay_samples(delay_s)
        if delay > cfg.N_CPP:
            raise ValueError('delay exceeds CPP')
        atom = continuous_path_matrix(cfg.N, delay, path.doppler_hz,
                                     1 / cfg.BANDWIDTH_HZ, start, cfg.C1, cfg.C2)
        steering = steering_vector_operator(array, path.mu_z, path.mu_y)
        gain = path.gain if gain_model == 'standard' else path.legacy_gain
        h += gain * steering[:, None, None] * atom[None]
    return h


def full_h_and_phase(scene, frames=32, **channel_options):
    array = channel_options.get('array') or cfg.upa4x4()
    h = np.zeros((len(scene.activity), array.M, cfg.N, cfg.N), dtype=complex)
    phase = np.ones((len(scene.activity), frames), dtype=complex)
    for user in range(len(scene.activity)):
        paths = scene.paths_of(user)
        if not paths or len({p.doppler_hz for p in paths}) != 1:
            raise ValueError('one common Doppler per candidate user required')
        if scene.activity[user]:
            h[user] = user_channel(paths, **channel_options)
        phase[user] = np.exp(2j * np.pi * paths[0].doppler_hz * np.arange(frames)
                            * (cfg.N + cfg.N_CPP) / cfg.BANDWIDTH_HZ)
    return h, phase
