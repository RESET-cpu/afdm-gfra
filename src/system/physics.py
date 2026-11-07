"""Continuous AFDM physical channel population."""
from dataclasses import dataclass
import numpy as np

from .scenario.continuous import draw_scene, full_h_and_phase


@dataclass(frozen=True)
class PhysicalConfig:
    version: str
    delay_spread_s: tuple[float, float] = (30e-9, 50e-9)

    def __post_init__(self):
        if self.version != 'continuous_delay_v1':
            raise ValueError('unknown physical version')
        lo, hi = self.delay_spread_s
        if not np.isfinite([lo, hi]).all() or not 0 < lo <= hi:
            raise ValueError('invalid continuous delay-spread range')

    @classmethod
    def from_mapping(cls, value):
        return cls(version=value['version'],
                   delay_spread_s=tuple(value.get('delay_spread_s', (30e-9, 50e-9))))


def sample_channel(seed, physics, *, users=40, frames=16, activity_probability=.1):
    """Continuous physical H and cross-frame phase, with fading power preserved."""
    scene=draw_scene(seed,n_users=users,activity_probability=activity_probability,
                     spread_range_s=physics.delay_spread_s)
    h,phase=full_h_and_phase(scene,frames=frames)
    return scene,h,phase
