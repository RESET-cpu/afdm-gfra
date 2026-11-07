"""Explicit candidate binding; the frozen STMP verifier stays unchanged."""
from copy import deepcopy
from pathlib import Path
import math
import torch

from project import ROOT
from utils import read_json, sha256
from algorithm.STMP.activity import SCHEMA, FEATURE_DEFINITION_FROZEN
from algorithm.STMP.records import SpatialConfig


def verify(configuration):
    c = read_json(configuration) if isinstance(configuration,(str,Path)) else deepcopy(configuration)
    if c.get('schema') != 'colored-stmp-candidate-v1' or c.get('method') != 'C-STMP':
        raise ValueError('Explicit C-STMP candidate configuration required')
    if c.get('query_covariance') != 'vI' or c.get('classifier_policy') != 'frozen_legacy_teacher':
        raise ValueError('This candidate requires vI and explicitly retained legacy classifier')
    controls = SpatialConfig(**c['ep']); controls.validate_stopping()
    if (controls.covariance_mode != 'isotropic' or not 0 < controls.damping <= 1
            or not 1 <= controls.min_iterations <= controls.iterations
            or c['site_damping'] != 1 or c['decision_threshold'] != .5
            or not math.isfinite(c['scale']) or c['scale'] <= 0
            or c['conditional_variance_floor_checkpoint_normalized'] <= 0
            or c['initialization']['kind'] != 'activity_prior_times_training_power'):
        raise ValueError('Invalid candidate message controls')
    hashes, blobs = {}, {}
    for key in ('first_checkpoint','evidence_checkpoint','prior_definition'):
        digest = sha256(ROOT/c[key])
        if digest != c[key+'_sha256']:
            raise ValueError('Candidate asset changed: '+key)
        hashes[key] = digest
        if key != 'prior_definition':
            blobs[key] = torch.load(ROOT/c[key],map_location='cpu',weights_only=False,mmap=True)
    first,evidence = blobs['first_checkpoint'],blobs['evidence_checkpoint']
    prior = read_json(ROOT/c['prior_definition'])
    if (first.get('schema') != 'colored-preconditioned-first-v1'
            or first.get('output') != 'conditional_mean'
            or first['global_complex_rms'] != c['scale']
            or prior['global_complex_rms'] != c['scale']
            or first['metadata']['epoch'] != c['first_epoch']):
        raise ValueError('Same-coordinate conditional-mean checkpoint required')
    binding = c['classifier_training_binding']
    if (evidence.get('schema') != SCHEMA or evidence['training_class_prior'] != .5
            or evidence.get('feature_definition') != FEATURE_DEFINITION_FROZEN
            or evidence['first_sha256'] != binding['first_sha256']
            or evidence['second_sha256'] != binding['second_sha256']
            or evidence['scale'] != c['scale'] or evidence['prior_definition'] != prior
            or evidence['metadata']['prior_definition_sha256'] != hashes['prior_definition']):
        raise ValueError('Original classifier provenance and common prior must be explicit')
    return c, hashes

