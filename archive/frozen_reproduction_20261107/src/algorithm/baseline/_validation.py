"""Source identity for the current implementation; no archived code is loaded."""
from copy import deepcopy
from pathlib import Path
import hashlib
import json

from project import ROOT, CONFIGS
from utils import sha256

METHOD_KEYS = dict(somp='somp', gamp='gamp_sbl_mmv', gnn='gnn_aspl_ding2026')


def inference_sources(method=None):
    # Pin the existing solvers' dependency inventory. Adding an independent
    # baseline must not invalidate their calibrated readout identities.
    inventory = json.loads((CONFIGS/'final/baseline_sources.json').read_text())['sha256']
    return {relative: sha256(ROOT/relative) for relative in inventory}


def verify_current_sources():
    expected = json.loads((CONFIGS/'final/baseline_sources.json').read_text())['sha256']
    if inference_sources() != expected:
        raise ValueError('Baseline implementation differs from the verified current version')


def inference_signature(configuration, method):
    if method == 'offgrid_sbl':
        value = dict(method=method, schema=configuration['schema'],
                     solver=configuration['methods'][method]['solver'], sources=inference_sources(method))
    else:
        setting = deepcopy(configuration['methods'][METHOD_KEYS[method]])
        setting.pop('readout_inference_sha256', None)
        setting.pop('checkpoint_path', None)
        value = dict(method=method, dictionary=configuration['dictionary'],
                     settings=setting, sources=inference_sources(method))
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    allow_nan=False).encode()).hexdigest()
