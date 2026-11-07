"""One satellite geometry for delays, Dopplers and UPA direction cosines.

The historical continuous sampler remains frozen for reproducibility. This
version preserves its candidate positions, fading draws and activity streams,
and replaces its independently drawn array angles by physical look directions.
"""
from dataclasses import dataclass, replace
import math

import numpy as np

from .. import config as cfg
from . import continuous, scene_generator as geo

VERSION = 'continuous_geometry_v3'


@dataclass(frozen=True)
class CandidateGeometry:
    satellite: np.ndarray
    velocity: np.ndarray
    ground: np.ndarray
    array_axes: np.ndarray  # rows: normal x, lattice y, lattice z
    reference_delay_s: float

    @property
    def look(self):
        ray = self.ground - self.satellite
        return ray / np.linalg.norm(ray, axis=1, keepdims=True)

    @property
    def direction_cosines(self):
        local = self.look @ self.array_axes.T
        return local[:, [2, 1]]  # physical steering convention: mu_z, mu_y

    @property
    def delay_s(self):
        return np.linalg.norm(self.ground - self.satellite, axis=1) / geo.C_LIGHT_M_S - self.reference_delay_s

    @property
    def doppler_hz(self):
        return -cfg.CARRIER_HZ / geo.C_LIGHT_M_S * (self.look @ self.velocity)


def candidate_geometry(seed, n_users=40):
    """Reconstruct the registered candidate positions before activity masking.

    One fixed right-handed frame is used for the entire population: the array
    normal points to nadir, y is global Y, and z is global X (along velocity).
    No user-specific rotation or orientation optimization is performed.
    """
    rng = np.random.default_rng(seed)
    gamma = geo.sample_beam_central_angle(rng)
    azimuth = float(rng.uniform(0., 2 * np.pi))
    satellite = np.array([0., 0., cfg.EARTH_RADIUS_M + cfg.ORBIT_ALTITUDE_M])
    speed = math.sqrt(geo.MU_EARTH / (cfg.EARTH_RADIUS_M + cfg.ORBIT_ALTITUDE_M))
    center = geo._rotate_about_z(cfg.EARTH_RADIUS_M * np.array(
        [math.sin(gamma), 0., math.cos(gamma)]), azimuth)
    east = geo._rotate_about_z(np.array([0., 1., 0.]), azimuth)
    north = geo._rotate_about_z(np.array([math.cos(gamma), 0., -math.sin(gamma)]), azimuth)
    closest = geo._closest_ground_in_beam(center, east, north)
    reference = float(np.linalg.norm(satellite - closest) / geo.C_LIGHT_M_S)
    positions = []
    for user in range(n_users):
        user_rng = np.random.default_rng(np.random.SeedSequence([seed, 7101, user]))
        radius = cfg.BEAM_RADIUS_M * math.sqrt(float(user_rng.random()))
        angle = float(user_rng.uniform(0., 2 * np.pi))
        positions.append(cfg.EARTH_RADIUS_M * geo._unit(
            center + radius * math.cos(angle) * east + radius * math.sin(angle) * north))
    axes = np.array([[0., 0., -1.], [0., 1., 0.], [1., 0., 0.]])
    return CandidateGeometry(satellite, np.array([speed, 0., 0.]), np.array(positions), axes, reference)


def draw_scene(seed, *, n_users=40, activity_probability=.1, spread_range_s=(30e-9, 50e-9)):
    """Return the repaired scene and the geometry that determines its array."""
    scene = continuous.draw_scene(seed, n_users=n_users, activity_probability=activity_probability,
                                  spread_range_s=spread_range_s)
    geometry = candidate_geometry(seed, n_users)
    delay, doppler, mu = geometry.delay_s, geometry.doppler_hz, geometry.direction_cosines
    for k in range(n_users):
        p = scene.paths_of(k)[0]
        if abs(delay[k] - p.macro_delay_s) > 1e-14 or abs(doppler[k] - p.doppler_hz) > 1e-8:
            raise AssertionError('candidate position stream differs from the registered physical sampler')
    paths = tuple(replace(p, mu_z=float(mu[p.user_id, 0]), mu_y=float(mu[p.user_id, 1]))
                  for p in scene.paths)
    return continuous.ContinuousScene(scene.activity.copy(), paths, scene.seed), geometry
