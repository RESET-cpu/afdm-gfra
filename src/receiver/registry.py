"""Construct algorithms from the explicit catalog; no method-name dispatch."""
from copy import deepcopy
from importlib import import_module
import inspect
from pathlib import Path
import re

from workspace import CONFIGS
from workspace import ROOT
from workspace import repository_path
from fileio import read_json
from fileio import sha256

CATALOG = CONFIGS / 'organized/algorithms.json'


def load_catalog(path=None):
    value = read_json(path or CATALOG)
    if value.get('schema') != 'afdm-algorithm-catalog-v1':
        raise ValueError('Expected afdm-algorithm-catalog-v1 catalog')
    definitions = value['algorithms']
    for name, spec in definitions.items():
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', name):
            raise ValueError('Invalid algorithm identifier: '+name)
        if spec['kind'] not in ('receiver', 'denoiser') or spec['backend'] not in ('cpu', 'device'):
            raise ValueError('Invalid algorithm kind/backend: '+name)
        if ':' not in spec['factory']:
            raise ValueError('Factory must be module:callable: '+name)
    return definitions


def load_models():
    """Resolve the single STMP configuration into a self-contained model record."""
    value = read_json(CONFIGS / 'organized/models.json')
    value['STMP'] = read_json(repository_path(value.pop('STMP_configuration')))
    return value


def select(methods, definitions, kind, *, noise_mode='estimated', phase_mode='estimated'):
    if noise_mode not in ('estimated', 'known'):
        raise ValueError('noise_mode must be known or estimated')
    if phase_mode not in ('estimated', 'known'):
        raise ValueError('phase_mode must be known or estimated')
    if not methods or len(set(methods)) != len(methods):
        raise ValueError('Select a nonempty list of distinct methods')
    for method in methods:
        if method not in definitions:
            raise ValueError('Unregistered algorithm: '+method)
        if definitions[method]['kind'] != kind:
            raise ValueError(f'{method} is not a {kind}')
        modes = definitions[method].get('phase_modes', ('known', 'estimated'))
        if phase_mode not in modes:
            raise ValueError(f'{method} requires phase_mode={" or ".join(modes)}; '
                             'use GP_MP for known-phase GP-MP inference')
    selected = {name: deepcopy(definitions[name]) for name in methods}
    if noise_mode == 'known':
        for name, spec in selected.items():
            variant = spec.get('known_noise')
            if variant is None:
                raise ValueError('Known-noise receiver is not registered: '+name)
            spec.update(deepcopy(variant))
    for spec in selected.values():
        spec['phase_input'] = ('raw' if phase_mode == 'estimated' and
                              spec.get('estimates_phase_internally', False) else 'operator')
    return selected


def factory(spec):
    module, name = spec['factory'].split(':', 1)
    value = getattr(import_module(module), name)
    if not callable(value):
        raise TypeError('Algorithm factory is not callable: '+spec['factory'])
    return value


def arguments(spec, binding, device):
    values = deepcopy(spec.get('kwargs', {}))
    for name, relative in spec.get('path_kwargs', {}).items():
        values[name] = repository_path(relative)
    for name, key in spec.get('model_kwargs', {}).items():
        values[name] = deepcopy(binding[key] if key else binding)
    values['device'] = 'cpu' if spec['backend'] == 'cpu' else device
    return values


def source_files(spec, binding, device):
    """Validate construction arguments and record source without loading weights."""
    constructor = factory(spec)
    inspect.signature(constructor).bind(**arguments(spec, binding, device))
    source = inspect.getsourcefile(constructor)
    if source is None:
        raise ValueError('A reproducible Python factory source is required')
    files = [Path(source), *(repository_path(p) for p in spec.get('assets', [])),
             *(repository_path(p) for p in spec.get('path_kwargs', {}).values())]
    for section, keys in spec.get('model_files', {}).items():
        for key in keys:
            path = repository_path(binding[section][key])
            if sha256(path) != binding[section][key+'_sha256']:
                raise ValueError('Model asset changed: '+str(path))
            files.append(path)
    return files


def build_algorithm(algorithm, *, binding, device, definitions=None):
    definitions = load_catalog() if definitions is None else definitions
    if algorithm not in definitions:
        raise ValueError('Unregistered algorithm: '+algorithm)
    spec = definitions[algorithm]
    model = factory(spec)(**arguments(spec, binding, device))
    if not callable(getattr(model, 'infer', None)):
        raise TypeError('Algorithm must implement infer(): '+algorithm)
    model._experiment_spec = deepcopy(spec)
    return model


def build_receiver(algorithm='GP_MP', *, device='cpu', binding=None, definitions=None):
    definitions = load_catalog() if definitions is None else definitions
    select([algorithm], definitions, 'receiver')
    if binding is None:
        binding = load_models()
    return build_algorithm(algorithm, binding=binding, device=device, definitions=definitions)


ALGORITHMS = tuple(name for name, spec in load_catalog().items()
                   if spec['kind'] == 'receiver' and spec.get('group') != 'ablation'
                   and not spec.get('alias_of'))
