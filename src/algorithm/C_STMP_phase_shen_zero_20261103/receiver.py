"""Shen Algorithm 1's unrotated initial operator in our frame-phase receiver.

Only the initial phase changes. The frozen frame update, network and scheduling
are inherited without modification. No physical phase search is invoked.
"""
import numpy as np

from algorithm.C_STMP_phase_shen_frames_20261103.receiver import Receiver as FrameReceiver
from system.receiver.unknown_phase import UnknownPhaseInput


class Receiver(FrameReceiver):
    def __init__(self, configuration, *, device='cpu', noise_mode='estimated'):
        super().__init__(configuration, device=device, noise_mode=noise_mode)
        if self.phase_configuration['initializer'] != 'zero':
            raise ValueError('This independent candidate requires all-one initial phases')

    def infer(self, inputs, *, observer=None, phase_observer=None):
        if not isinstance(inputs, UnknownPhaseInput):
            raise TypeError('The zero-initialization experiment accepts raw observations only')
        arrays, record = super().infer(inputs, observer=observer, phase_observer=phase_observer)
        if (record['physical_path_search_used'] or record['path_search_during_updates']
                or not np.array_equal(arrays['initial_phase'], np.ones(inputs.pilot.shape[:2]))):
            raise AssertionError('Zero-initialization experiment violated its declared scope')
        record['phase_initialization'].update(phase_matrix='all_one',
            physical_path_search_used=False, reference='Shen Algorithm 1: initial C_phi=C')
        record['limitations'] = [item for item in record['limitations']
            if item != 'Phase variables increase from K slopes to (Q-1)*K free angles; physical initialization remains.']
        record['limitations'].append(
            'All phases start at one without frequency search; convergence and recovery remain empirical.')
        return arrays, record
