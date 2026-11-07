"""Verify the shared STMP prior bank before white-noise training."""
import json
import numpy as np
from workspace import ROOT, repository_path
from fileio import sha256

def assets(config):
    binding = json.loads(repository_path(config['base_config']).read_text(encoding='utf-8'))
    prior_path = repository_path(binding['prior_definition'])
    if sha256(prior_path) != binding['prior_definition_sha256']:
        raise ValueError('Frozen prior hash changed')
    prior = json.loads(prior_path.read_text(encoding='utf-8'))
    checkpoint = repository_path(binding['first_checkpoint'])
    if sha256(checkpoint) != binding['first_checkpoint_sha256']:
        raise ValueError('Frozen first-score hash changed')
    paths = {s: repository_path(prior['data_files'][s]) for s in ('train', 'validation')}
    ids = {s: repository_path(prior['dataset_identities'][s]['identities_path']) for s in paths}
    records = {}
    for s in paths:
        for p, expected in ((paths[s], prior['sample_files_sha256'][s]),
                            (ids[s], prior['dataset_identities'][s]['identities_sha256'])):
            actual = sha256(p)
            if actual != expected:
                raise ValueError('Dataset hash changed: '+str(p))
            records[str(p.relative_to(ROOT))] = actual
    identities = {s: np.load(ids[s], allow_pickle=False) for s in ids}
    if np.intersect1d(identities['train'][:, 0], identities['validation'][:, 0]).size:
        raise ValueError('Train/validation scenes overlap')
    _, rows = np.unique(identities['validation'][:, 0], return_index=True)
    rows = rows[:config['evaluation_scenes']]
    if len(rows) != 1000:
        raise ValueError('This candidate evaluation requires 1000 distinct scenes')
    return binding, checkpoint, paths, identities, rows, records
