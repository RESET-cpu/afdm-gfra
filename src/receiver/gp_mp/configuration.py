"""Validate the adopted white-training budgets, hashes and receiver controls."""
from copy import deepcopy
from pathlib import Path
import math

import torch

from workspace import ROOT
from fileio import read_json
from fileio import sha256
from receiver.stmp.activity import SCHEMA
from receiver.stmp.activity import FEATURE_DEFINITION_FROZEN
from receiver.stmp.records import SpatialConfig


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(configuration):
    c = read_json(configuration) if isinstance(configuration, (str, Path)) else deepcopy(configuration)
    require(c['schema'] == 'white-matched-receiver-binding-v1' and c['method'] == 'GP-MP', 'Wrong binding')
    hashes = {}
    keys = ('first_checkpoint', 'evidence_checkpoint', 'prior_definition',
            'first_training_record', 'first_training_specification',
            'classifier_training_record', 'classifier_training_specification',
            'classifier_execution_record', 'classifier_history', 'classifier_initialization',
            'base_receiver_configuration', 'evaluation_plan')
    for key in keys:
        hashes[key] = sha256(ROOT / c[key])
        require(hashes[key] == c[key + '_sha256'], 'Changed binding asset: ' + key)
    base = read_json(ROOT / c['base_receiver_configuration'])
    planned = read_json(ROOT / c['evaluation_plan'])
    for key in planned['scientific_settings_to_preserve']:
        require(c[key] == base[key] == planned['scientific_settings_to_preserve'][key], 'Changed receiver control: ' + key)
    controls = SpatialConfig(**c['ep'])
    controls.validate_stopping()
    first = torch.load(ROOT / c['first_checkpoint'], map_location='cpu', weights_only=False, mmap=True)
    evidence = torch.load(ROOT / c['evidence_checkpoint'], map_location='cpu', weights_only=False, mmap=True)
    prior = read_json(ROOT / c['prior_definition'])
    dc = read_json(ROOT / c['first_training_record'])
    ds = read_json(ROOT / c['first_training_specification'])
    require(ds['configuration']['noise']['max_strength'] == 0.0, 'Denoiser specification must use white training noise')
    cc = read_json(ROOT / c['classifier_training_record'])
    spec = read_json(ROOT / c['classifier_training_specification'])
    history = read_json(ROOT / c['classifier_history'])
    meta = evidence['metadata']
    require(dc['status'] == 'COMPLETED' and dc['epochs'] == 200 and dc['optimizer_steps'] == 156400,
            'Incomplete denoiser training budget')
    require(dc['weight_sha256'] == hashes['first_checkpoint'] and dc['selected_epoch'] == c['first_epoch']
            and dc['specification_sha256'] == hashes['first_training_specification'], 'Denoiser completion binding mismatch')
    require(first['schema'] == 'colored-preconditioned-first-v1' and first['output'] == 'conditional_mean'
            and first['global_complex_rms'] == prior['global_complex_rms'] == c['scale']
            and first['metadata']['epoch'] == c['first_epoch']
            and first['metadata']['specification_sha256'] == hashes['first_training_specification']
            and first['metadata']['noise']['max_strength'] == 0.0, 'White conditional-mean checkpoint mismatch')
    require(cc['status'] == 'COMPLETED' and cc['epochs'] == 100 and cc['optimizer_steps'] == 156300
            and cc['initialization'] == 'random' and cc['pretrained_classifier'] is None
            and cc['weight_sha256'] == hashes['evidence_checkpoint']
            and cc['specification_sha256'] == hashes['classifier_training_specification']
            and cc['initialization_sha256'] == hashes['classifier_initialization']
            and cc['first_sha256'] == hashes['first_checkpoint'] and cc['second_sha256'] is None,
            'Classifier completed budget or teacher mismatch')
    require(evidence['schema'] == SCHEMA and evidence['training_class_prior'] == .5
            and evidence['feature_definition'] == FEATURE_DEFINITION_FROZEN
            and evidence['first_sha256'] == hashes['first_checkpoint'] and evidence['second_sha256'] is None
            and evidence['scale'] == c['scale'] and evidence['prior_definition'] == prior
            and meta['prior_definition_sha256'] == hashes['prior_definition']
            and meta['specification_sha256'] == hashes['classifier_training_specification']
            and meta['initialization_sha256'] == hashes['classifier_initialization']
            and evidence['selected_epoch'] == meta['epoch'] == cc['selected_epoch'] == c['classifier_epoch'],
            'Classifier checkpoint provenance mismatch')
    require(c['classifier_training_binding'] == dict(first_sha256=hashes['first_checkpoint'], second_sha256=None),
            'Classifier binding mismatch')
    training = spec['configuration']
    require(training['query_covariance'] == 'vI' and training['first_checkpoint_sha256'] == hashes['first_checkpoint']
            and training['activity']['maximum_epochs'] == 100 and training['activity']['training_class_prior'] == .5
            and training['first_training_record_sha256'] == hashes['first_training_record']
            and spec['initialization_sha256'] == hashes['classifier_initialization']
            and spec['initialization'] == 'random' and spec['pretrained_classifier'] is None,
            'Classifier specification mismatch')
    require([h['epoch'] for h in history] == list(range(101))
            and all(h['optimizer_steps'] == h['epoch'] * 1563 for h in history)
            and all(math.isfinite(h['validation']['loss']) for h in history), 'Incomplete classifier history')
    selected = min(history, key=lambda h: h['validation']['loss'])
    require(selected['epoch'] == c['classifier_epoch'] and selected['validation'] == evidence['validation'],
            'Selected classifier does not match fixed validation minimum')
    require(all(bool(torch.isfinite(t).all()) for b in (first, evidence) for t in b['state_dict'].values()),
            'Nonfinite trained weight')
    return c, hashes


