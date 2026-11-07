"""Observation-only channel-window stopping; not a full-state convergence claim."""
from collections import deque
import numpy as np


class ChannelWindowStop:
    def __init__(self, controls, reconstruct):
        if reconstruct is None:
            raise ValueError('channel reconstruction is required for output stopping')
        self.controls = controls
        self.reconstruct = reconstruct
        self.history = deque(maxlen=controls.output_window_interval//controls.output_window_stride+1)
        self.stable = 0

    def update(self, iteration, coefficients, valid):
        c = self.controls
        delta = None
        ready = False
        if iteration % c.output_window_stride == 0:
            channel = self.reconstruct(coefficients)
            if not np.isfinite(channel).all():
                raise FloatingPointError('nonfinite channel in output stop')
            self.history.append(channel.copy())
            if len(self.history) == self.history.maxlen:
                previous = self.history[0]
                delta = float(np.linalg.norm(channel-previous)/max(
                    np.linalg.norm(channel), np.linalg.norm(previous), 1e-30))
            passed = (iteration >= c.output_min_iterations and valid
                      and delta is not None and delta < c.output_window_tolerance)
            self.stable = self.stable+1 if passed else 0
            ready = self.stable >= c.output_patience
        return ready, dict(output_window=delta, output_stable=self.stable)
