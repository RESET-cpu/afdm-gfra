"""Frozen final activity decision for the estimated-geometry projected receiver.

Use the original classifier and one development-calibrated channel-energy
threshold. This readout does not change inference, moments, or channel NMSE.
The energy statistic is not a posterior probability or a second independent
likelihood. It only refines the final reported activity decision.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import time

import numpy as np

from afdm_jadcedd.algorithm.proposed_projected import ProjectedPhaseReceiver
from afdm_jadcedd.project import ROOT
from afdm_jadcedd.utils import sha256

SCHEMA = 'afdm-proposed-estimated-phase-projected-energy-v1'


def read_activity(arrays, noise_variance, threshold):
    if not np.isfinite(threshold) or threshold <= 0 or not np.isfinite(noise_variance) or noise_variance <= 0:
        raise ValueError('Positive finite energy threshold and public noise variance required')
    energy = np.sum(abs(arrays['estimate'])**2, axis=(1, 2, 3)) / noise_variance
    probability = arrays['probabilities']
    # A score of one implements both thresholds; it is not a probability.
    score = np.minimum(probability / .5, energy / threshold)
    return dict(arrays, classifier_activity_decision=probability >= .5,
                activity_energy_over_noise=energy, activity_score=score,
                activity_decision=score >= 1.)


class ProjectedEnergyReceiver(ProjectedPhaseReceiver):
    def __init__(self, configuration, *, device='auto'):
        if configuration.get('schema') != SCHEMA:
            raise ValueError('Projected receiver with calibrated final activity readout required')
        binding = configuration['base_configuration']
        path = ROOT / binding['path']
        if sha256(path) != binding['sha256']:
            raise ValueError('Projected base configuration identity mismatch')
        rule = configuration['activity_readout']
        if rule['probability_threshold'] != .5:
            raise ValueError('Original classifier threshold required')
        self.energy_threshold = float(rule['energy_over_noise_threshold'])
        calibration = rule['calibration']
        certificate = ROOT / calibration['path']
        if sha256(certificate) != calibration['sha256']:
            raise ValueError('Readout calibration identity mismatch')
        saved = json.loads(certificate.read_text())
        if saved['threshold'] != self.energy_threshold or saved['confirmation_labels_used']:
            raise ValueError('Readout differs from development calibration')
        super().__init__(json.loads(path.read_text()), device=device)
        parent_signature = self.signature
        self.configuration = deepcopy(configuration)
        self.signature = hashlib.sha256(json.dumps(dict(configuration=configuration,
            base_signature=parent_signature, source_sha256=sha256(Path(__file__))), sort_keys=True).encode()).hexdigest()

    def context(self):
        record = super().context()
        record.update(method='proposed_estimated_phase_projected_energy', configuration=self.configuration,
                      inference_sha256=self.signature, unified_activity_probability=False)
        return record

    def infer(self, inputs, *, observer=None, phase_observer=None):
        arrays, record = super().infer(inputs, observer=observer, phase_observer=phase_observer)
        started = time.monotonic()
        arrays = read_activity(arrays, inputs.noise_variance, self.energy_threshold)
        elapsed = time.monotonic() - started
        record.update(method='proposed_estimated_phase_projected_energy',
            unified_activity_probability=False,
            activity_readout=deepcopy(self.configuration['activity_readout']),
            activity_threshold_scope='p >= 0.5 and complete-channel energy / public noise >= frozen threshold',
            activity_score_definition='min(p/0.5, energy_over_noise/threshold); score >= 1; not a probability',
            probabilities_definition='Original classifier probabilities before final energy decision',
            readout_seconds=elapsed, seconds=record['seconds']+elapsed,
            wall_seconds=record['wall_seconds']+elapsed, complete_estimate_masked=False)
        return arrays, record
