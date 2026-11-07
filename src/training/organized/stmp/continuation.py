"""Import an explicitly identified first-score trajectory into a new run."""
import json
import math
from pathlib import Path
import shutil

import torch

from fileio import sha256
from fileio import write_json
from training.organized.stmp.common import resolve


def import_first(configuration, output, specification_hash, device):
    settings = configuration['first']
    source = settings['continuation']
    paths = {key: resolve(source[key]) for key in
             ('checkpoint', 'specification', 'best_checkpoint', 'baseline')}
    for key, path in paths.items():
        if sha256(path) != source[key+'_sha256']:
            raise ValueError('First continuation source changed: ' + key)
        if Path(output).resolve() in path.resolve().parents:
            raise ValueError('First continuation source overlaps its output')
    parent = json.loads(paths['specification'].read_text())
    previous = parent['configuration']
    if (parent['prior_definition_sha256'] != configuration['prior_definition_sha256']
            or parent['device'] != str(device)):
        raise ValueError('First continuation prior or device differs')
    for key in ('generator', 'scale', 'normalization', 'shape', 'noise_support', 'bank'):
        if previous[key] != configuration[key]:
            raise ValueError('First continuation training distribution differs: ' + key)
    # Paths may move; the initializer's content hash and all optimization
    # settings except the declared duration/schedule must remain identical.
    allowed = {'initial_checkpoint', 'output', 'maximum_epochs', 'minimum_epochs',
               'stopping', 'continuation', 'continuation_schedule'}
    for key in (previous['first'].keys() | settings.keys()) - allowed:
        if previous['first'].get(key) != settings.get(key):
            raise ValueError('First continuation optimization setting differs: ' + key)
    state = torch.load(paths['checkpoint'], map_location='cpu', weights_only=False)
    if (state['schema'] != 'full-geometry-shared-first-resume-v1'
            or state['specification_sha256'] != source['specification_sha256']):
        raise ValueError('First continuation checkpoint and parent specification differ')
    if not state['epoch'] <= settings['minimum_epochs'] <= settings['maximum_epochs']:
        raise ValueError('First continuation must finish the declared cumulative budget')
    execution_only = source.get('execution_only', False)
    if execution_only:
        for key in ('maximum_epochs', 'minimum_epochs', 'stopping', 'continuation_schedule'):
            if previous['first'].get(key) != settings.get(key):
                raise ValueError('Execution-only continuation must preserve the original training schedule')
        from training.organized.stmp.first import learning_rate
        schedule = dict(kind='unchanged_original_schedule', start_epoch=state['epoch'],
                        start_learning_rate=learning_rate(settings, state['epoch']))
    else:
        schedule = settings['continuation_schedule']
    rates = [group['lr'] for group in state['optimizer']['param_groups']]
    if (schedule['start_epoch'] != state['epoch']
            or not all(math.isclose(rate, schedule['start_learning_rate'], rel_tol=1e-12)
                       for rate in rates)):
        raise ValueError('First continuation schedule must start at the saved learning rate')
    best = torch.load(paths['best_checkpoint'], map_location='cpu', weights_only=False)
    if (best['metadata']['specification_sha256'] != source['specification_sha256']
            or best['metadata']['validation']['loss'] != state['best']
            or best['metadata']['epoch'] >= state['epoch']):
        raise ValueError('First continuation selected checkpoint and trajectory differ')
    provenance = dict(
        schema='first-score-continuation-v1', source=source,
        parent_specification_sha256=source['specification_sha256'],
        specification_sha256=specification_hash, imported_epoch=state['epoch'],
        imported_cursor=state['cursor'], imported_optimizer_steps=state['steps'],
        inherited_history_epochs=len(state['history']),
        cumulative_target_epochs=settings['maximum_epochs'], schedule=schedule,
        restored=['model', 'ema', 'optimizer', 'rng', 'torch_rng', 'mps_rng', 'cuda_rng',
                  'indices', 'cursor', 'loss_sum', 'seen', 'history',
                  'best', 'meaningful_best', 'stale'],
        same_original_experiment=False,
        execution_only=execution_only,
        description='New run continuing an identified trajectory; parent artifacts remain unchanged.')
    if execution_only:
        # Keep inherited weights, but identify the new run and retain the parent
        # specification explicitly even if no later epoch beats this baseline.
        best['metadata']['inherited_specification_sha256'] = best['metadata']['specification_sha256']
        best['metadata']['specification_sha256'] = specification_hash
        best['metadata']['continuation'] = provenance
        torch.save(best, output/'first_best.pt')
    else:
        shutil.copy2(paths['best_checkpoint'], output/'first_best.pt')
    shutil.copy2(paths['baseline'], output/'baseline.json')
    write_json(output/'history.json', state['history'])
    write_json(output/'CONTINUATION.json', provenance)
    return state, provenance
