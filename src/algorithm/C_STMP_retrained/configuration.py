"""Verify the completed same-teacher classifier without changing old bindings."""
from copy import deepcopy
from pathlib import Path
import math
import torch

from project import ROOT
from utils import read_json, sha256
from algorithm.STMP.activity import SCHEMA, FEATURE_DEFINITION_FROZEN
from algorithm.STMP.records import SpatialConfig


def verify(configuration):
    c=read_json(configuration) if isinstance(configuration,(str,Path)) else deepcopy(configuration)
    if (c.get('schema')!='colored-stmp-candidate-v1' or c.get('method')!='C-STMP'
            or c.get('query_covariance')!='vI' or c.get('classifier_policy')!='retrained_colored_mean_vI'):
        raise ValueError('Explicit C-STMP with retrained same-teacher vI classifier required')
    controls=SpatialConfig(**c['ep']); controls.validate_stopping()
    if (controls.covariance_mode!='isotropic' or not 0<controls.damping<=1
            or not 1<=controls.min_iterations<=controls.iterations
            or c['site_damping']!=1 or c['decision_threshold']!=.5
            or not math.isfinite(c['scale']) or c['scale']<=0
            or c['conditional_variance_floor_checkpoint_normalized']<=0
            or c['initialization']['kind']!='activity_prior_times_training_power'):
        raise ValueError('Invalid candidate message controls')
    hashes={}
    for key in ('first_checkpoint','evidence_checkpoint','prior_definition',
                'classifier_training_record','classifier_training_specification','classifier_execution_record'):
        hashes[key]=sha256(ROOT/c[key])
        if hashes[key]!=c[key+'_sha256']:
            raise ValueError('Candidate asset changed: '+key)
    first=torch.load(ROOT/c['first_checkpoint'],map_location='cpu',weights_only=False,mmap=True)
    evidence=torch.load(ROOT/c['evidence_checkpoint'],map_location='cpu',weights_only=False,mmap=True)
    prior=read_json(ROOT/c['prior_definition'])
    if (first.get('schema')!='colored-preconditioned-first-v1' or first.get('output')!='conditional_mean'
            or first['global_complex_rms']!=c['scale'] or prior['global_complex_rms']!=c['scale']
            or first['metadata']['epoch']!=c['first_epoch']):
        raise ValueError('Same-coordinate completed conditional mean required')
    binding=c['classifier_training_binding']; meta=evidence['metadata']
    if (evidence.get('schema')!=SCHEMA or evidence['training_class_prior']!=.5
            or evidence.get('feature_definition')!=FEATURE_DEFINITION_FROZEN
            or evidence['first_sha256']!=hashes['first_checkpoint']
            or binding['first_sha256']!=hashes['first_checkpoint']
            or evidence['second_sha256'] is not None or binding['second_sha256'] is not None
            or evidence['scale']!=c['scale'] or evidence['prior_definition']!=prior
            or meta['prior_definition_sha256']!=hashes['prior_definition']
            or meta['specification_sha256']!=hashes['classifier_training_specification']
            or meta['execution_plan_sha256']!=hashes['classifier_execution_record']):
        raise ValueError('Classifier provenance must match the frozen colored first and prior')
    complete=read_json(ROOT/c['classifier_training_record'])
    spec=read_json(ROOT/c['classifier_training_specification'])
    training=spec['configuration']
    if (complete['status']!='COMPLETED' or complete['epochs']!=100
            or complete['optimizer_steps']!=156300 or complete['initialization']!='random'
            or complete['pretrained_classifier'] is not None
            or complete['weight_sha256']!=hashes['evidence_checkpoint']
            or complete['selected_epoch']!=c['classifier_epoch']
            or evidence['selected_epoch']!=c['classifier_epoch']
            or complete['specification_sha256']!=hashes['classifier_training_specification']
            or complete['execution_plan_sha256']!=hashes['classifier_execution_record']
            or complete['first_sha256']!=hashes['first_checkpoint']
            or training['query_covariance']!='vI' or training['activity']['maximum_epochs']!=100
            or training['activity']['training_class_prior']!=.5):
        raise ValueError('Completed random-start 100-epoch training and selected checkpoint required')
    return c,hashes
