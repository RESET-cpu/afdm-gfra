"""Prepare and freeze a new, independently generated nineteen-condition run."""
import argparse
import copy
import hashlib
import json
import shutil
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments.lstmp_training_v3_20261020.plan import (
    conditions, planned_updates, TRAIN_PER_CONDITION, VALIDATION_PER_CONDITION,
    MAXIMUM_DEPTH, SNR_VALUES)

SOURCE = Path('D:/afdm-gfra-cpu/runs/lstmp_conditional_bce_v2_20261020')
TARGET = SOURCE.parent / 'lstmp_conditional_bce_v3_depth10_20261020'
PACKAGE = 'lstmp_training_v3_20261020'
DOC = 'LSTMP_TRAINING_PROTOCOL_20261020_V3.md'
SCOPE_FILES = ['experiment/_support/settings.py', 'experiment/_common.py', 'experiment/snr_comparison.py',
               'experiment/user_count.py', 'experiment/pilot_frames.py',
               'experiment/activity_probability.py']


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2,
                                   allow_nan=False) + '\n', encoding='utf-8')
    temporary.replace(path)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as file:
        for block in iter(lambda: file.read(2**20), b''):
            digest.update(block)
    return digest.hexdigest()


def configuration():
    config = copy.deepcopy(read(SOURCE / 'MANIFEST.json')['configuration'])
    config.update(schema='afdm-lstmp-conditional-bce-v3',
        run_directory=TARGET.as_posix(), planned_updates=planned_updates(),
        scope='Ten layers; explicit nineteen formal conditions; known phase/noise; '
              'independent physical scenes; no independent test or automatic ablation.',
        seed_policy='New disjoint physical scene seeds; initialization and epoch-order rules inherited from v2.',
        condition_design='Union of four one-variable sweeps; default appears once; no Cartesian product.')
    settings = config['receiver']
    settings.pop('case_sources', None)
    settings.pop('first_epoch_pool_indices', None)
    settings.update(maximum_depth=MAXIMUM_DEPTH, epoch_schedule=[3] * MAXIMUM_DEPTH,
        train_scenes=len(conditions()) * TRAIN_PER_CONDITION,
        validation_scenes=len(conditions()) * VALIDATION_PER_CONDITION,
        test_scenes=0, train_seed=202610206100001, validation_seed=202610206200001,
        test_seed=202610206300001, snr_db=SNR_VALUES,
        conditions={split: conditions() for split in ('train', 'validation', 'test')},
        generation_workers=4)
    config['execution']['selective_checkpoint'] = dict(
        minimum_depth=6, minimum_users=1, first_layers=MAXIMUM_DEPTH)
    return config


def refresh_sources(config):
    if any((TARGET / name).exists() for name in ('TRAINING_LAUNCH.json', 'RUNNING.lock', 'checkpoints')):
        raise RuntimeError('Frozen source can only change before the first training launch')
    destination = TARGET / 'source_code/experiments' / PACKAGE
    shutil.copytree(ROOT / 'experiments' / PACKAGE, destination, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    write(destination / 'config.json', config)
    (TARGET / 'protocol').mkdir(exist_ok=True)
    shutil.copy2(ROOT / 'docs' / DOC, TARGET / 'protocol' / DOC)
    shutil.copy2(Path(__file__), TARGET / 'protocol/prepare_run.py')
    for source, name in [
        (ROOT / 'scripts/check_lstmp_training_v3_implementation_20261020.py', 'check_implementation.py'),
        (ROOT / 'tests/test_lstmp_training_v3.py', 'test_lstmp_training_v3.py'),
    ]:
        if source.exists():
            shutil.copy2(source, TARGET / 'protocol' / name)
    write(TARGET / 'protocol/CONDITIONS.json', dict(
        construction='Union, not Cartesian product', conditions=conditions(),
        train_per_condition=TRAIN_PER_CONDITION, validation_per_condition=VALIDATION_PER_CONDITION,
        planned_updates=config['planned_updates'],
        scope_sources={path: sha(ROOT / path) for path in SCOPE_FILES},
        independent_test_generated=False))


def verify_seed_ranges(config):
    proposed = {split: (config['receiver'][f'{split}_seed'],
                        config['receiver'][f'{split}_seed'] +
                        config['receiver'][f'{split}_scenes'])
                for split in ('train', 'validation')}
    assert proposed['train'][1] <= proposed['validation'][0]
    checked = []
    for folder in TARGET.parent.iterdir():
        if folder == TARGET or not folder.is_dir():
            continue
        for file in folder.glob('data/receiver_*.json'):
            value = read(file)
            identity = value.get('identity', {})
            if 'base_seed' not in identity or 'count' not in identity:
                continue
            lo, hi = identity['base_seed'], identity['base_seed'] + identity['count']
            for split, (begin, end) in proposed.items():
                if max(lo, begin) < min(hi, end):
                    raise ValueError(f'Physical scene seed overlap: {split} / {file}')
            checked.append(dict(receipt=str(file), begin=lo, end_exclusive=hi))
    write(TARGET / 'protocol/SEED_SEPARATION.json', dict(
        new_ranges=proposed, previous_receiver_receipts=checked,
        all_checked_ranges_disjoint=True,
        scope='Saved receiver receipts in sibling runs; no test examples generated or read.'))


def scene_statistics(config):
    scale = config['pretrained_score']['global_complex_rms']
    records = []
    coverage = {}
    settings = config['receiver']
    for split in ('train', 'validation'):
        receipt = read(TARGET / f'data/receiver_{split}.json')
        count = settings[f'{split}_scenes']
        if len(receipt['files']) != count:
            raise ValueError(f'Incomplete generated data: {split}')
        groups = Counter()

        def inspect(index):
            path = TARGET / f'data/receiver/{split}_{index:04d}.npz'
            if sha(path) != receipt['files'].get(path.name):
                raise ValueError(f'Scene hash mismatch: {path}')
            condition = settings['conditions'][split][index % len(conditions())]
            with np.load(path) as values:
                if (int(values['seed']) != settings[f'{split}_seed'] + index or
                    float(values['snr']) != condition['snr_db'] or
                    len(values['active']) != condition['users'] or
                    len(values['y']) != condition['frames']):
                    raise ValueError(f'Scene identity mismatch: {path}')
                row = dict(split=split, index=index, condition=condition)
                if split == 'train':
                    active = values['active'].astype(bool)
                    normalized = values['x'] / scale
                    if not active.any() or np.any(normalized[~active] != 0):
                        raise ValueError(f'Invalid channel labels: {path}')
                    energy = float(np.square(normalized.real.astype(np.float64)).sum() +
                                   np.square(normalized.imag.astype(np.float64)).sum())
                    if not np.isfinite(energy) or energy <= 0:
                        raise ValueError(f'Invalid training energy: {path}')
                    row.update(users=len(active), active_users=int(active.sum()), energy=energy)
                return row

        with ThreadPoolExecutor(max_workers=4) as pool:
            for position, row in enumerate(pool.map(inspect, range(count)), 1):
                groups[tuple(sorted(row['condition'].items()))] += 1
                if split == 'train':
                    records.append(row)
                if position % 500 == 0 or position == count:
                    print(json.dumps(dict(stage='VERIFYING_DATA', split=split,
                                          scenes=position, total=count)), flush=True)
        per_condition = TRAIN_PER_CONDITION if split == 'train' else VALIDATION_PER_CONDITION
        if len(groups) != 19 or set(groups.values()) != {per_condition}:
            raise ValueError(f'Unbalanced explicit conditions: {split}')
        coverage[split] = [dict(condition=dict(key), scenes=value) for key, value in groups.items()]
    scenes = len(records)
    users = sum(row['users'] for row in records)
    energy = sum(row['energy'] for row in records)
    assert scenes == 4750 and users == 215000
    write(TARGET / 'protocol/TRAINING_STATISTICS.json', dict(
        schema='lstmp-training-statistics-v3', training_scenes=scenes, training_users=users,
        active_training_users=sum(r['active_users'] for r in records),
        total_training_energy=energy, mean_scene_energy=energy / scenes,
        mean_users_per_scene=users / scenes, rms_scale=scale, validation_labels_used=False,
        coordinates='float32 normalized real/imaginary labels; double energy sums; no extra factor two',
        scene_records=records, coverage=coverage, all_selected_scene_hashes_verified=True,
        train_receipt_sha256=sha(TARGET / 'data/receiver_train.json'),
        validation_receipt_sha256=sha(TARGET / 'data/receiver_validation.json')))


def freeze(config):
    refresh_sources(config)
    snapshots = [path for folder in (TARGET / 'source_code', TARGET / 'source_project')
                 for path in folder.rglob('*') if path.is_file() and path.suffix in ('.py', '.json')]
    assets = [TARGET / 'initialization/first_50000.pt', TARGET / 'initialization/BINDING.json',
              TARGET / 'data/normalization.json', TARGET / 'data/receiver_train.json',
              TARGET / 'data/receiver_validation.json']
    assets += [p for p in (TARGET / 'protocol').iterdir()
               if p.is_file() and p.name != 'PREFLIGHT.json']
    previous = read(SOURCE / 'MANIFEST.json')
    write(TARGET / 'MANIFEST.json', dict(
        schema='lstmp-conditional-bce-v3-frozen-run', configuration=config,
        snapshot_hashes={str(p): sha(p) for p in snapshots},
        bound_assets={str(p): sha(p) for p in assets},
        protected_assets=previous['protected_assets'],
        implementation_source_run=str(SOURCE), source_manifest_sha256=sha(SOURCE / 'MANIFEST.json'),
        previous_results_used_for_initialization=False))


def write_launcher():
    text = r"""param([switch]$Resume)
$ErrorActionPreference = 'Stop'
$trainingDirectory = $PSScriptRoot
$projectDirectory = '__ROOT__'
$pythonExecutable = Join-Path $projectDirectory '.venv\Scripts\python.exe'
$preflight = Get-Content -LiteralPath (Join-Path $trainingDirectory 'protocol\PREFLIGHT.json') -Raw | ConvertFrom-Json
$manifestHash = (Get-FileHash -LiteralPath (Join-Path $trainingDirectory 'MANIFEST.json') -Algorithm SHA256).Hash.ToLower()
if ($preflight.status -ne 'PASSED' -or $preflight.manifest_sha256 -ne $manifestHash) { throw 'Preflight does not cover this frozen run.' }
if (!$Resume -and (Test-Path -LiteralPath (Join-Path $trainingDirectory 'TRAINING_LAUNCH.json'))) { throw 'Already launched; inspect before using -Resume.' }
$env:AFDM_LSTMP_ROOT = $projectDirectory
$env:AFDM_LSTMP_CONFIG = Join-Path $trainingDirectory 'source_code\experiments\lstmp_training_v3_20261020\config.json'
$env:PYTHONUTF8 = '1'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$stdout = Join-Path $trainingDirectory ('stdout_' + $stamp + '.log')
$stderr = Join-Path $trainingDirectory ('stderr_' + $stamp + '.log')
$mode = if ($Resume) { '--resume' } else { '--fresh' }
$trainingProcess = Start-Process -FilePath $pythonExecutable -ArgumentList @('-u','-m','experiments.lstmp_training_v3_20261020.train','--train',$mode,'--device','cuda') -WorkingDirectory (Join-Path $trainingDirectory 'source_code') -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
@{launcher_pid=$trainingProcess.Id; launched_at=(Get-Date).ToString('o'); training_run=$trainingDirectory; stdout=$stdout; stderr=$stderr; resume=[bool]$Resume; planned_updates=142500; manifest_sha256=$manifestHash} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $trainingDirectory 'TRAINING_LAUNCH.json') -Encoding UTF8
Write-Output ('V3 training launched: ' + $trainingProcess.Id)
"""
    (TARGET / 'start_training.ps1').write_text(text.replace('__ROOT__', str(ROOT)), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--prepare', action='store_true')
    modes.add_argument('--freeze', action='store_true')
    modes.add_argument('--refresh-before-launch', action='store_true')
    args = parser.parse_args()
    config = configuration()
    if args.prepare:
        if TARGET.exists():
            raise FileExistsError(TARGET)
        if (SOURCE / 'RUNNING.lock').exists() or read(SOURCE / 'STATUS.json')['stage'] != 'PAUSED':
            raise RuntimeError('Previous run must be safely stopped first')
        source_manifest = read(SOURCE / 'MANIFEST.json')
        for group in ('snapshot_hashes', 'bound_assets'):
            for path, digest in source_manifest[group].items():
                if sha(path) != digest:
                    raise ValueError(f'Previous frozen source changed: {path}')
        TARGET.mkdir()
        for name in ('source_code', 'source_project', 'initialization'):
            shutil.copytree(SOURCE / name, TARGET / name,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        (TARGET / 'data').mkdir()
        shutil.copy2(SOURCE / 'data/normalization.json', TARGET / 'data/normalization.json')
        refresh_sources(config)
        verify_seed_ranges(config)
        old_folder = SOURCE / 'checkpoints'
        write(TARGET / 'protocol/PREVIOUS_RUN_STOP.json', dict(
            source=str(SOURCE), status=read(SOURCE / 'STATUS.json'),
            checkpoint=str(old_folder / 'depth_5/last.pt'),
            checkpoint_sha256=sha(old_folder / 'depth_5/last.pt'),
            depth=5, epoch=1, cursor=4294, completed_updates=61894,
            completed_depths={str(d): read(old_folder / f'depth_{d}/COMPLETE.json')['best_sha256']
                              for d in range(1, 5)}, resumed_into_new_run=False))
        write(TARGET / 'STATUS.json', dict(stage='PREPARED_PENDING_DATA', updated_unix=time.time(),
                                          planned_updates=config['planned_updates']))
    else:
        current = read(TARGET / f'source_code/experiments/{PACKAGE}/config.json')
        if current != config:
            raise ValueError('Prepared data configuration changed')
        if args.freeze:
            scene_statistics(config)
        elif not (TARGET / 'protocol/TRAINING_STATISTICS.json').exists():
            raise FileNotFoundError('Generate and freeze data before refreshing sources')
        freeze(config)
        write_launcher()
        write(TARGET / 'STATUS.json', dict(stage='PREPARED_PENDING_PREFLIGHT',
            updated_unix=time.time(), planned_updates=config['planned_updates']))
    print(json.dumps(dict(run=str(TARGET), planned_updates=config['planned_updates'],
                          conditions=len(conditions()))), flush=True)


if __name__ == '__main__':
    main()
