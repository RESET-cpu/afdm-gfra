"""Fixed scene/epoch continuation; old run assets are read-only."""
import json
import shutil
from pathlib import Path
import numpy as np
import torch
from .common import CONFIG, OUT, sha, save_json


def epochs_for_depth(depth):
    settings = CONFIG['receiver']
    schedule = settings.get('epoch_schedule')
    if schedule is None:
        return settings['epochs_per_depth']
    if len(schedule) != settings['maximum_depth'] or any(type(n) is not int or n < 1 for n in schedule):
        raise ValueError('One positive fixed epoch count is required for each depth')
    return schedule[depth-1]


def epoch_order(indices, depth, epoch):
    """Preserve the consumed prefix when reducing the original scene pool."""
    first = CONFIG['receiver'].get('first_epoch_pool_indices')
    if first is not None and depth == 1 and epoch == 1:
        if len(first) != len(indices) or set(first) != set(indices):
            raise ValueError('First epoch must visit every selected scene exactly once')
        positions = {pool_index:position for position,pool_index in enumerate(indices)}
        return np.asarray([positions[i] for i in first],dtype=np.int64)
    return np.random.default_rng(CONFIG['seed']+depth*100+epoch).permutation(len(indices))


def plateau_reached(epoch, stale):
    settings = CONFIG['receiver']
    return (settings.get('early_stopping',True) and epoch-1 >= settings['minimum_epochs']
            and stale >= settings['patience'])


def prepare_continuation():
    """Import model, Adam state and partial-epoch totals exactly once."""
    specification = CONFIG.get('continuation')
    if specification is None:
        return
    receipt_path = OUT/'CONTINUATION.json'
    if receipt_path.exists():
        if json.loads(receipt_path.read_text(encoding='utf-8'))['specification'] != specification:
            raise ValueError('Continuation specification changed')
        return
    source = Path(specification['source_run'])
    if (source/'RUNNING.lock').exists():
        raise ValueError('The source training run must remain paused')
    if sha(source/'MANIFEST.json') != specification['source_manifest_sha256']:
        raise ValueError('Source training manifest changed')
    manifest = json.loads((source/'MANIFEST.json').read_text(encoding='utf-8'))
    previous = manifest['configuration']
    for key in ('seed','backbone','pretrained_score','normalized_training_second_moment'):
        if previous[key] != CONFIG[key]:
            raise ValueError(f'Continuation changes model semantics: {key}')
    for key in ('learning_rate','activity_learning_rate','calibration_learning_rate',
                'activity_loss_weight','earlier_layer_loss_weight','variance_calibration_order',
                'variance_soft_floor_temperature_ratio','maximum_feedback_variance_ratio',
                'phase_mode','noise_mode'):
        if previous['receiver'][key] != CONFIG['receiver'][key]:
            raise ValueError(f'Continuation changes receiver semantics: {key}')
    source_folder = source/'checkpoints'/'depth_1'
    checkpoint = source_folder/'last.pt'
    if sha(checkpoint) != specification['checkpoint_sha256']:
        raise ValueError('Source checkpoint changed')
    state = torch.load(checkpoint,map_location='cpu',weights_only=False)
    cursor = specification['completed_updates']
    if any(state[k] != v for k,v in dict(depth=1,epoch=1,cursor=cursor,steps=cursor,samples=cursor).items()):
        raise ValueError('Continuation checkpoint is not the declared partial first epoch')
    previous_order = np.random.default_rng(previous['seed']+101).permutation(previous['receiver']['train_scenes'])
    first = CONFIG['receiver']['first_epoch_pool_indices']
    if first[:cursor] != previous_order[:cursor].tolist():
        raise ValueError('Already-trained scene order differs from the checkpoint')
    indices = CONFIG['receiver']['case_sources']['train']['indices']
    epoch_order(indices,1,1)
    folder = OUT/'checkpoints'/'depth_1'
    folder.mkdir(parents=True,exist_ok=True)
    files = {}
    for name in ('last.pt','best.pt','initial_validation.json'):
        original,target = source_folder/name,folder/name
        digest = sha(original)
        if target.exists():
            if sha(target) != digest:
                raise ValueError(f'An existing continuation checkpoint differs: {name}')
        else:
            temporary = target.with_suffix(target.suffix+'.tmp')
            shutil.copyfile(original,temporary)
            if sha(temporary) != digest:
                raise ValueError(f'Checkpoint copy verification failed: {name}')
            temporary.replace(target)
        files[name] = digest
    save_json(receipt_path,dict(specification=specification,imported_sha256=files,
        optimizer_state_preserved=True,partial_epoch_loss_preserved=True,
        consumed_prefix_preserved=True,source_run_modified=False))
