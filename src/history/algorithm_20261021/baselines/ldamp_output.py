"""Optional output TSVD for L-DAMP, retaining its original activity decisions.

Each user's spatial unfolding is approximated by one singular component.
This uses the zero path-direction-spread assumption; see docs/TERMINOLOGY.md
and results/ldamp_structure_20261015/independent_validation/REPORT.md.
The DnCNN, AMP recurrence and calibrated original activity rule are unchanged.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import time

import numpy as np

from afdm_jadcedd.algorithm.baselines.ldamp.receiver import LDAMPReceiver, signature as base_signature
from afdm_jadcedd.utils import sha256

SCHEMA = 'afdm-ldamp-output-tsvd-v1'


def signature(config):
    if config.get('schema') != SCHEMA or config.get('rank') != 1:
        raise ValueError('Rank-one L-DAMP output TSVD configuration required')
    rule = config.get('activity_rule', config.get('recommended_activity_rule', 'original'))
    if rule != 'original':
        raise ValueError('The unified output TSVD receiver retains the original activity rule')
    base = config['base_configuration']
    identity = base_signature(base)
    if identity != config['base_inference_sha256']:
        raise ValueError('Base inference identity mismatch')
    payload = dict(schema=SCHEMA, rank=1, base_inference_sha256=identity,
                   activity_rule=rule, activity_readout=base.get('readout'),
                   source_sha256=sha256(Path(__file__)))
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def rank_one(estimate):
    value = np.asarray(estimate, dtype=np.complex128)
    if value.ndim != 4 or not np.isfinite(value).all():
        raise ValueError('Finite channel[user, antenna, output, input] required')
    h = value.reshape(value.shape[0], value.shape[1], -1)
    gram = np.einsum('kic,kjc->kij', h, h.conj(), optimize=False)
    _, vectors = np.linalg.eigh(gram)
    u = vectors[:, :, -1]
    row = np.einsum('ki,kic->kc', u.conj(), h, optimize=False)
    # Only the final output is projected: no derivative or eigenvalue gap is
    # needed, including at a repeated leading singular value or a zero channel.
    return (u[:, :, None] * row[:, None, :]).reshape(value.shape)


class LDAMPOutputReceiver:
    def __init__(self, configuration, *, device='auto'):
        self.configuration = deepcopy(configuration)
        self.signature = signature(configuration)
        self.base = LDAMPReceiver(configuration['base_configuration'], device=device)

    def postprocess(self, base_arrays, base_record):
        start = time.monotonic()
        arrays = {key: value.copy() for key, value in base_arrays.items()}
        arrays['estimate'] = rank_one(base_arrays['estimate'])
        arrays['channel_energy'] = np.sum(abs(arrays['estimate'])**2, axis=(1, 2, 3))
        elapsed = time.monotonic() - start
        record = deepcopy(base_record)
        record.update(method='ldamp_output_tsvd', inference_sha256=self.signature,
                      base_inference_sha256=self.base.signature,
                      seconds=base_record['seconds'] + elapsed,
                      base_seconds=base_record['seconds'], postprocessing_seconds=elapsed,
                      configuration=self.configuration,
                      validation_status=self.configuration.get('validation_status', 'UNQUALIFIED'),
                      activity_rule='original',
                      activity_statistic='original_channel_frobenius_energy',
                      activity_rule_configuration=self.configuration['base_configuration'].get('readout'),
                      recurrence_modified=False, rank=1, truth_used_in_inference=False)
        return arrays, record

    def infer(self, inputs, *, observer=None):
        arrays, record = self.base.infer(inputs, observer=observer)
        return self.postprocess(arrays, record)

    def run(self, input_path, output_path, *, observer=None):
        return LDAMPReceiver.run(self, input_path, output_path, observer=observer)
