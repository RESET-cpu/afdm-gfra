"""Create an independent execution continuation without resetting learning."""
import argparse
import copy
import json
import shutil
import time
from pathlib import Path

from prepare_lstmp_training_v3_20261020 import ROOT, TARGET as SOURCE, read, write, sha

TARGET = SOURCE.parent / 'lstmp_conditional_bce_v3_depth10_fast_20261020'
PACKAGE = 'lstmp_execution_v3_20261020'


def configuration():
    parent = read(SOURCE / 'MANIFEST.json')
    config = copy.deepcopy(parent['configuration'])
    config['run_directory'] = TARGET.as_posix()
    config['execution_acceleration'] = dict(
        graph_users=40, graph_all_layers_through_depth=5, graph_deep_layers=3,
        data_workers=1, prefetch_scenes=4, loss_precision_unchanged=True,
        diagnostic_host_transfer='batched; training status cadence unchanged',
        graph_scope='score backbone only; single total-loss backward; eager diagnostics and evaluation')
    config['execution_continuation'] = dict(
        source_run=str(SOURCE), source_manifest_sha256=sha(SOURCE / 'MANIFEST.json'),
        source_checkpoint=str(SOURCE / 'checkpoints/depth_1/last.pt'),
        source_checkpoint_sha256=sha(SOURCE / 'checkpoints/depth_1/last.pt'),
        source_depth=1, source_epoch=1, source_cursor=3159,
        completed_updates_preserved=3159, optimizer_and_rng_preserved=True,
        sample_order_and_validation_selection_preserved=True)
    return config


def freeze():
    if (TARGET / 'TRAINING_LAUNCH.json').exists():
        raise RuntimeError('Cannot modify a launched continuation')
    config = configuration()
    package_dir = TARGET / 'source_code/experiments' / PACKAGE
    shutil.copytree(ROOT / 'experiments' / PACKAGE, package_dir, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    write(package_dir / 'config.json', config)
    for name in ('prepare_lstmp_v3_gpu_continuation_20261020.py',
                 'check_lstmp_v3_gpu_continuation_20261020.py'):
        path = ROOT / 'scripts' / name
        if path.exists():
            shutil.copy2(path, TARGET / 'protocol' / name)
    write(TARGET / 'protocol/EXECUTION_CHANGE.json', dict(
        authorization='User request on 2026-10-20: maximize RTX 5080 training throughput.',
        original_update=3159, parent_configuration_preserved_except=[
            'run_directory', 'execution_acceleration', 'execution_continuation'],
        changes=config['execution_acceleration'],
        no_changes_to=['conditions', 'losses', 'gradient scope', 'learning rates',
                      'precision settings', 'sample order', 'update count', 'selection rules'],
        source_retained=True, immutable_data_hardlinked=True,
        all_benchmark_weight_updates_discarded=True))
    previous = read(SOURCE / 'MANIFEST.json')
    snapshots = [p for directory in (TARGET / 'source_code', TARGET / 'source_project')
                 for p in directory.rglob('*') if p.is_file() and p.suffix in ('.py', '.json')]
    assets = [p for p in (TARGET / 'protocol').iterdir() if p.is_file() and p.name != 'PREFLIGHT.json']
    assets += [TARGET / 'initialization/first_50000.pt', TARGET / 'initialization/BINDING.json',
               TARGET / 'data/normalization.json', TARGET / 'data/receiver_train.json',
               TARGET / 'data/receiver_validation.json']
    write(TARGET / 'MANIFEST.json', dict(
        schema='lstmp-v3-execution-continuation', configuration=config,
        snapshot_hashes={str(p): sha(p) for p in snapshots},
        bound_assets={str(p): sha(p) for p in assets},
        protected_assets=previous['protected_assets'],
        source_manifest_sha256=sha(SOURCE / 'MANIFEST.json')))
    launcher = (SOURCE / 'start_training.ps1').read_text(encoding='utf-8')
    launcher = launcher.replace('lstmp_training_v3_20261020', PACKAGE)
    launcher = launcher.replace('V3 training launched:', 'V3 accelerated continuation launched:')
    (TARGET / 'start_training.ps1').write_text(launcher, encoding='utf-8')
    write(TARGET / 'STATUS.json', dict(stage='PREPARED_PENDING_PREFLIGHT',
        source_cursor=3159, planned_updates=config['planned_updates'], updated_unix=time.time()))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--refresh', action='store_true')
    args = parser.parse_args()
    if args.refresh:
        freeze()
        return
    if TARGET.exists():
        raise FileExistsError(TARGET)
    assert read(SOURCE / 'STATUS.json')['stage'] == 'PAUSED'
    assert not (SOURCE / 'RUNNING.lock').exists()
    parent = read(SOURCE / 'MANIFEST.json')
    for group in ('snapshot_hashes', 'bound_assets'):
        for path, digest in parent[group].items():
            assert sha(path) == digest, path
    TARGET.mkdir()
    for name in ('source_code', 'source_project', 'initialization', 'checkpoints', 'protocol'):
        shutil.copytree(SOURCE / name, TARGET / name,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'PREFLIGHT.json'))
    for name in ('ACTIVE_TIME.json',):
        shutil.copy2(SOURCE / name, TARGET / name)
    (TARGET / 'data/receiver').mkdir(parents=True)
    for name in ('normalization.json', 'receiver_train.json', 'receiver_validation.json'):
        shutil.copy2(SOURCE / 'data' / name, TARGET / 'data' / name)
    count = 0
    for path in (SOURCE / 'data/receiver').glob('*.npz'):
        (TARGET / 'data/receiver' / path.name).hardlink_to(path)
        count += 1
    assert count == 6650
    write(TARGET / 'protocol/CONTINUATION_SOURCE.json', dict(
        source=str(SOURCE), source_status=read(SOURCE / 'STATUS.json'),
        source_manifest_sha256=sha(SOURCE / 'MANIFEST.json'), scenes_linked=count,
        inherited_checkpoint_sha256=sha(TARGET / 'checkpoints/depth_1/last.pt'),
        source_checkpoint_sha256=sha(SOURCE / 'checkpoints/depth_1/last.pt'),
        completed_updates=3159))
    freeze()
    print(json.dumps(dict(status='PREPARED', run=str(TARGET), scenes_linked=count)), flush=True)


if __name__ == '__main__':
    main()
