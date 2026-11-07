"""Local training assets, frozen identities and source records."""
from copy import deepcopy
import json
from pathlib import Path

import numpy as np

from workspace import ROOT
from workspace import CONFIGS
from workspace import repository_path
from fileio import sha256

DEFAULT_CONFIG = CONFIGS / 'training/STMP.json'


def resolve(path):
    return repository_path(path)


def relative(path):
    path = Path(path).resolve()
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def source_hashes():
    training = ROOT / 'src/training/organized'
    model = ROOT / 'src/receiver/stmp'
    paths = sorted((training / 'stmp').glob('*.py'))
    paths += sorted((training / 'scores').glob('*.py'))
    paths += [model / 'activity.py', model / 'configuration.py']
    paths += sorted((ROOT/'src/networks').rglob('*.py'))
    return {relative(path): sha256(path) for path in paths}


def load_recipe(path=DEFAULT_CONFIG, *, prior_path=None, data_directory=None, device=None):
    config = json.loads(Path(path).read_text())
    if config['schema'] != 'proposed-three-stage-training-v1':
        raise ValueError('Selected three-stage proposed recipe required')
    if prior_path is not None:
        config['prior_definition'] = relative(prior_path)
        config['prior_definition_sha256'] = sha256(resolve(config['prior_definition']))
    if data_directory is not None:
        directory = Path(data_directory).resolve()
        config['data_files'] = {s: relative(directory/f'{s}_channel.npy') for s in ('train', 'validation')}
        config['moments_file'] = relative(directory/'train_moments.npz')
    if device is not None:
        config['runtime']['device'] = device
    return config


def load_prior(config):
    path = resolve(config['prior_definition'])
    if sha256(path) != config['prior_definition_sha256']:
        raise ValueError('Training prior identity changed')
    prior = json.loads(path.read_text())
    if (prior['shape'] != config['shape'] or prior['global_complex_rms'] != config['scale']
            or prior['noise_support'] != config['noise_support']):
        raise ValueError('Prior and training coordinates differ')
    for split in ('train', 'validation'):
        if prior[split+'_samples'] != config['bank'][split+'_samples']:
            raise ValueError('Prior and recipe sample counts differ')
    return prior


def load_data(config, prior):
    """Use relocatable paths; retain the checkpoint-bound prior bytes verbatim."""
    data = {}
    for split in ('train', 'validation'):
        path = resolve(config['data_files'][split])
        if sha256(path) != prior['sample_files_sha256'][split]:
            raise ValueError('Prior bank changed: ' + split)
        bank = np.load(path, mmap_mode='r', allow_pickle=False)
        if bank.shape != (prior[split+'_samples'], *prior['shape']) or bank.dtype != np.complex64:
            raise ValueError('Complete physical prior bank shape/dtype differs')
        data[split] = bank
    if sha256(resolve(config['moments_file'])) != prior['moments_sha256']:
        raise ValueError('Prior moment artifact changed')
    return data


def training_record(config, stage):
    """Verify completion, weight, specification and prior as one identity."""
    record_path = resolve(config[f'{stage}_training_record'])
    spec_path = resolve(config[f'{stage}_training_specification'])
    record = json.loads(record_path.read_text())
    spec = json.loads(spec_path.read_text())
    if (record['status'] != 'COMPLETED' or record['optimizer_steps'] < 1
            or record['weight_sha256'] != sha256(resolve(config[f'{stage}_checkpoint']))
            or record['specification_sha256'] != sha256(spec_path)
            or spec['prior_definition_sha256'] != config['prior_definition_sha256']):
        raise ValueError('Completed training identity differs: ' + stage)
    if stage == 'second' and record['first_sha256'] != sha256(resolve(config['first_checkpoint'])):
        raise ValueError('Second score belongs to a different first teacher')
    return record


def with_output(config, output, *, teachers):
    config = deepcopy(config)
    output = Path(output).resolve()
    # An existing run can resume, but frozen assets cannot be an output directory.
    assets = [config['prior_definition'], config['moments_file'], *config['data_files'].values()]
    for stage in ('first', 'second', 'activity'):
        assets.append(config[stage]['initial_checkpoint'])
    for stage in ('first', 'second'):
        assets += [config[f'{stage}_checkpoint'], config[f'{stage}_training_record'],
                   config[f'{stage}_training_specification']]
    for asset in assets:
        parent = resolve(asset).resolve().parent
        if output == parent or output in parent.parents or parent in output.parents:
            raise ValueError('Training output overlaps a frozen asset directory')
    config['output'] = relative(output)
    config['first']['output'] = relative(output/'first')
    if teachers == 'run':
        for stage in ('first', 'second'):
            config[f'{stage}_checkpoint'] = relative(output/stage/f'{stage}_best.pt')
            config[f'{stage}_training_record'] = relative(output/stage/'complete.json')
            config[f'{stage}_training_specification'] = relative(output/stage/'specification.json')
    return config
