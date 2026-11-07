"""Preserve the completed run and prepare the authorized two-epoch continuation."""
import copy
import hashlib
import json
import shutil
import time
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(r'D:\afdm-gfra-cpu\runs\lstmp_refinenet_50000_message_damping_20261019')
TARGET = SOURCE.parent / 'lstmp_refinenet_50000_epoch6_20261020'
PRIOR_COMPARISON = ROOT / 'results/lstmp_vs_legacy20_repaired_20261019'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(2**20), b''):
            digest.update(block)
    return digest.hexdigest()


def main():
    started = time.time()
    torch.set_num_threads(4)
    if TARGET.exists():
        raise FileExistsError(TARGET)
    assert not (SOURCE/'RUNNING.lock').exists()
    assert read(SOURCE/'STATUS.json')['stage'] == 'COMPLETE'
    assert read(SOURCE/'COMPLETE.json')['status'] == 'COMPLETE'
    assert not (SOURCE/'FAILURE.json').exists()
    original = read(SOURCE/'MANIFEST.json')
    assert original['configuration']['receiver']['epoch_schedule'] == [2, 2, 2, 2, 4]
    for path, digest in original['snapshot_hashes'].items():
        assert sha(path) == digest, path
    for path, digest in original['protected_assets'].items():
        assert sha(ROOT/path) == digest, path
    for depth, epochs in enumerate([2, 2, 2, 2, 4], 1):
        folder = SOURCE/f'checkpoints/depth_{depth}'
        receipt = read(folder/'COMPLETE.json')
        assert receipt['steps'] == 4800*epochs
        assert receipt['checkpoint_sha256'] == sha(folder/'best.pt')

    last_path = SOURCE/'checkpoints/depth_5/last.pt'
    best_path = SOURCE/'checkpoints/depth_5/best.pt'
    last = torch.load(last_path, map_location='cpu', weights_only=False, mmap=True)
    best = torch.load(best_path, map_location='cpu', weights_only=False, mmap=True)
    assert (last['depth'], last['epoch'], last['cursor'], last['steps'], last['samples']) == (5, 5, 0, 19200, 0)
    assert best['epoch'] == last['selected_epoch'] == 4
    assert last['state'].keys() == best['state'].keys()
    assert all(torch.equal(value, best['state'][key]) for key, value in last['state'].items())
    assert all(torch.isfinite(value).all() for value in last['state'].values())
    assert [group['lr'] for group in last['optimizer']['param_groups']] == [2e-5, 1e-4, 1e-3]
    assert last['optimizer']['state']
    optimizer_steps = set()
    for state in last['optimizer']['state'].values():
        optimizer_steps.add(int(state['step'].item()))
        assert all(torch.isfinite(value).all() for value in state.values() if torch.is_tensor(value))
    assert optimizer_steps == {19200}, optimizer_steps
    assert [row['epoch'] for row in last['history']] == [0, 1, 2, 3, 4]
    assert last['history'] == read(SOURCE/'checkpoints/depth_5/history.json')
    del last, best

    # Only the output directory and the final stage epoch count change.
    config = copy.deepcopy(original['configuration'])
    config['run_directory'] = TARGET.as_posix()
    config['receiver']['epoch_schedule'] = [2, 2, 2, 2, 6]
    restored = copy.deepcopy(config)
    restored['run_directory'] = original['configuration']['run_directory']
    restored['receiver']['epoch_schedule'] = [2, 2, 2, 2, 4]
    assert restored == original['configuration']
    assert config['hard_time_budget_hours'] == 12
    assert config['run_final_evaluation'] is False
    TARGET.mkdir()
    copied = {}

    def copy_file(path, relative=None):
        relative = path.relative_to(SOURCE) if relative is None else Path(relative)
        destination = TARGET/relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        digest = sha(path)
        assert sha(destination) == digest
        copied[str(relative)] = digest

    for folder_name in ('source_code', 'source_project', 'data', 'initialization'):
        for path in (SOURCE/folder_name).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
                copy_file(path)
    for depth in range(1, 6):
        folder = SOURCE/f'checkpoints/depth_{depth}'
        for name in ('best.pt', 'history.json', 'best_validation.json', 'initial_validation.json'):
            if (folder/name).exists():
                copy_file(folder/name)
        if depth < 5:
            copy_file(folder/'COMPLETE.json')
        else:
            copy_file(folder/'last.pt')
            copy_file(folder/'COMPLETE.json', 'provenance/depth_5_epoch4_COMPLETE.json')
    for name in ('CONTINUATION.json', 'history.jsonl'):
        copy_file(SOURCE/name)
    for name in ('MANIFEST.json', 'STATUS.json', 'COMPLETE.json', 'ACTIVE_TIME.json'):
        copy_file(SOURCE/name, 'provenance/source_run/'+name)
    for path in (SOURCE/'protocol').glob('*.json'):
        copy_file(path, Path('provenance/source_protocol')/path.name)

    package = TARGET/'source_code/experiments/lstmp_candidate_20261019'
    config_path = package/'reuse_50000_fast.json'
    write(config_path, config)
    # copied tracks immutable imported assets; the new runtime configuration is distinct.
    copied.pop(str(config_path.relative_to(TARGET)))
    paths = [p for directory in (package, TARGET/'source_project/afdm_jadcedd')
             for p in directory.rglob('*') if p.is_file() and p.suffix in ('.py', '.json')]
    manifest = dict(schema=original['schema'], configuration=config,
                    snapshot_hashes={str(p.resolve()): sha(p) for p in paths},
                    protected_assets=original['protected_assets'])
    write(TARGET/'MANIFEST.json', manifest)
    elapsed = time.time()-started
    inherited_seconds = read(SOURCE/'ACTIVE_TIME.json')['consumed_seconds']
    write(TARGET/'ACTIVE_TIME.json', dict(consumed_seconds=inherited_seconds+elapsed,
        inherited_training_seconds=inherited_seconds, continuation_preparation_seconds=elapsed))
    receipt = dict(
        schema='authorized-final-stage-extension-v1', created_unix=time.time(),
        authorization='User said 可以，请你继续 after the explicit proposal for five layers, 4800 scenes per epoch, final-stage 4 to 6 epochs, 9600 additional updates and fresh paired confirmation.',
        source_run=str(SOURCE), target_run=str(TARGET), source_manifest_sha256=sha(SOURCE/'MANIFEST.json'),
        source_last_checkpoint_sha256=sha(last_path), source_best_checkpoint_sha256=sha(best_path),
        prior_comparison=str(PRIOR_COMPARISON), prior_plan_sha256=sha(PRIOR_COMPARISON/'PLAN.json'),
        prior_summary_sha256=sha(PRIOR_COMPARISON/'SUMMARY.json'),
        proposal_sha256=sha(PRIOR_COMPARISON/'POSTCOMPARISON_REVIEW.json'),
        completed_updates=57600, remaining_updates=9600, total_updates=67200,
        epoch_schedule=[2, 2, 2, 2, 6], next_depth=5, next_epoch=5, next_scene=0,
        model_and_optimizer_copied_byte_for_byte=True, last_state_equals_validation_selected_epoch4=True,
        optimizer_state_steps=sorted(optimizer_steps), original_run_modified=False,
        training_scenes_per_epoch=4800, unique_training_scenes=4800, validation_scenes=1200,
        model_equations_sources_and_execution_unchanged=True,
        changed_configuration_fields=['run_directory', 'receiver.epoch_schedule[4]'],
        hard_time_budget_hours=12, inherited_training_seconds=inherited_seconds,
        continuation_preparation_seconds=elapsed, estimated_additional_minutes=[75, 90],
        copied_sha256=copied, training_started=False)
    write(TARGET/'protocol/EPOCH6_CONTINUATION.json', receipt)
    write(TARGET/'protocol/CPU_PREFLIGHT.json', dict(status='PASSED', created_unix=time.time(),
        manifest_sha256=sha(TARGET/'MANIFEST.json'), checkpoint_sha256=sha(TARGET/'checkpoints/depth_5/last.pt'),
        tests=['All five source stage budgets complete', 'Last epoch4 state equals selected best state',
               'Finite model and complete Adam moments with 19200 steps', 'Copied state, source and data receipts exact',
               'Only output directory and final epoch count changed', 'Existing cumulative time inherited'],
        gpu_used=False, optimizer_updates=0))
    write(TARGET/'STATUS.json', dict(stage='PREPARED_AUTHORIZED_EPOCH_EXTENSION', updated_unix=time.time(),
        depth=5, next_epoch=5, completed_updates=57600, remaining_updates=9600))
    print(json.dumps(dict(run=str(TARGET), status='PREPARED', next_epoch=5, remaining_updates=9600,
                         manifest_sha256=sha(TARGET/'MANIFEST.json'), preparation_seconds=elapsed)), flush=True)


if __name__ == '__main__':
    main()
