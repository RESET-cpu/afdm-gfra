"""Verify the exported 5,000-sample run without training or receiver experiments."""
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'experiment'))

import numpy as np
import torch
from afdm_jadcedd.utils import sha256
from afdm_jadcedd.experiment.training.proposed.common import load_recipe, load_prior, load_data
from channel_denoising import first_score_bundles, FirstChannelMean

torch.set_num_threads(1)
manifest = json.loads((ROOT / 'cloud/SAMPLE_5000_ASSETS.json').read_text())
for name, expected in manifest['files'].items():
    path = ROOT / name
    assert path.stat().st_size == expected['bytes'], name
    assert sha256(path) == expected['sha256'], name
base = ROOT / 'runs/proposed_sample_sizes_20261018'
recipe = load_recipe(base / 'configs/n5000.json', device='cpu')
prior = load_prior(recipe)
data = load_data(recipe, prior)
for stage in ('first', 'second', 'activity'):
    assert sha256(ROOT / recipe[stage]['initial_checkpoint']) == recipe[stage]['initial_checkpoint_sha256'], stage
bundles, _ = first_score_bundles(base / 'n5000/first_receiver.json')
config = bundles['proposed']['configuration']
model = FirstChannelMean(config['scale'], ROOT / config['first_checkpoint'], device='cpu')
rng = np.random.default_rng(20261018)
query = (rng.standard_normal((1,16,16,16)) + 1j*rng.standard_normal((1,16,16,16))) / np.sqrt(2)
mean = model.infer(query, np.array([1.])).mean
assert mean.shape == query.shape and np.isfinite(mean).all()
print(json.dumps(dict(status='PASS', files=len(manifest['files']),
    train_shape=list(data['train'].shape), validation_shape=list(data['validation'].shape),
    completed_stages=manifest['completed_stages'], first_epochs=manifest['first_epochs'],
    untrained_stages=manifest['untrained_stages'], synthetic_forward_queries=1,
    training_run=False), indent=2))
