"""Freeze an independent v2 run and verify the original fixed scene selection."""
import argparse
import copy
import hashlib
import json
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('D:/afdm-gfra-cpu/runs/lstmp_refinenet_depth7_20261020')
TARGET = SOURCE.parent / 'lstmp_conditional_bce_v2_20261020'
PACKAGE = 'lstmp_training_v2_20261020'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as file:
        for chunk in iter(lambda: file.read(2**20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def configuration():
    config = copy.deepcopy(read(SOURCE / 'MANIFEST.json')['configuration'])
    for key in ('depth_extension', 'hard_time_budget_hours', 'execution_policy',
                'baseline_comparisons', 'prior_training_seconds'):
        config.pop(key, None)
    config.update(schema='afdm-lstmp-conditional-bce-v2', run_directory=TARGET.as_posix(),
        initialization='Every new layer independently loads the same 50k AWGN score; new activity output and log calibrations are zero.',
        scope='Main arm A only; known phase/noise; no independent test or automatic ablation sweep.',
        run_final_evaluation=False,
        objective=dict(channel='true-active conditional squared error / fixed training mean scene energy',
                       activity='summed natural-proportion BCE / fixed training mean users',
                       coefficients=[1., 1.], bce_updates_score=True),
        seed_policy='Existing fixed scene orders; torch/Python/NumPy initialization seed = seed + depth * 100000.',
        planned_updates=100800)
    settings = config['receiver']
    for key in ('minimum_epochs', 'patience', 'activity_loss_weight', 'auxiliary_total_weight',
                'convergence_curve'):
        settings.pop(key, None)
    settings.update(maximum_depth=7, epoch_schedule=[3] * 7, early_stopping=False,
        adaptation_epochs=1, joint_epochs=2, learning_rate=2e-5,
        activity_learning_rate=1e-4, calibration_learning_rate=1e-3,
        joint_lr_multiplier=.1, earlier_layer_loss_weight=.2,
        activity_threshold=.5, checkpoint_steps=256,
        selection='Mean final-layer conditional-channel loss + BCE; epoch0 eligible; earliest tie.',
        extensions='Accepted general-A damped messages; independent pretrained first scores and activity heads; three independent scalar calibrations; no second score.')
    return config


def scene_statistics(config):
    """No validation labels contribute to the two fixed training denominators."""
    scale = config['pretrained_score']['global_complex_rms']
    records = []
    for split in ('train', 'validation'):
        specification = config['receiver']['case_sources'][split]
        source_receipt = Path(specification['run_directory']) / f'data/receiver_{split}.json'
        if sha(source_receipt) != specification['receipt_sha256']:
            raise ValueError(f'Source receipt changed: {split}')
        receipt = read(TARGET / f'data/receiver_{split}.json')
        jobs = [(split, index, Path(specification['run_directory']) / f'data/receiver/{split}_{index:04d}.npz',
                 receipt['files'][f'{split}_{index:04d}.npz']) for index in specification['indices']]
        def inspect(job):
            kind, index, path, digest = job
            if sha(path) != digest:
                raise ValueError(f'Scene hash mismatch: {path}')
            if kind != 'train':
                return dict(split=kind, index=index)
            with np.load(path) as values:
                activity = values['active'].astype(bool)
                # Match float32 real/imaginary coordinates in data.Cases.
                x = values['x'] / scale
                if np.any(x[~activity] != 0) or not np.isfinite(x).all() or not activity.any():
                    raise ValueError(f'Invalid effective-channel labels: {path}')
                energy = float(np.square(x.real.astype(np.float64)).sum() +
                               np.square(x.imag.astype(np.float64)).sum())
                return dict(split=kind, index=index, users=len(activity),
                            active_users=int(activity.sum()), energy=energy)
        with ThreadPoolExecutor(max_workers=4) as pool:
            for position, row in enumerate(pool.map(inspect, jobs), 1):
                if split == 'train':
                    records.append(row)
                if position % 400 == 0 or position == len(jobs):
                    print(json.dumps(dict(stage='VERIFYING_DATA', split=split, scenes=position,
                                          total=len(jobs))), flush=True)
    scenes, users = len(records), sum(r['users'] for r in records)
    energy = sum(r['energy'] for r in records)
    if (scenes, users) != (4800, 256000) or energy <= 0:
        raise ValueError('The fixed training dataset differs from the protocol')
    result = dict(schema='lstmp-training-statistics-v2', training_scenes=scenes,
        training_users=users, active_training_users=sum(r['active_users'] for r in records),
        total_training_energy=energy, mean_scene_energy=energy / scenes,
        mean_users_per_scene=users / scenes, rms_scale=scale,
        coordinates='float32 real/imaginary labels, double-precision energy accumulation; no extra factor two',
        validation_labels_used=False, scene_records=records,
        train_receipt_sha256=sha(TARGET / 'data/receiver_train.json'),
        validation_receipt_sha256=sha(TARGET / 'data/receiver_validation.json'),
        all_selected_scene_hashes_verified=True)
    write(TARGET / 'protocol/TRAINING_STATISTICS.json', result)


def refresh_sources(config):
    if any((TARGET / name).exists() for name in ('TRAINING_LAUNCH.json', 'RUNNING.lock', 'checkpoints')):
        raise RuntimeError('Source refresh is allowed only before the first training launch')
    source = ROOT / 'experiments' / PACKAGE
    destination = TARGET / 'source_code/experiments' / PACKAGE
    shutil.copytree(source, destination, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    write(destination / 'config.json', config)
    shutil.copy2(ROOT / 'docs/LSTMP_TRAINING_PROTOCOL_20261020_V2.md',
                 TARGET / 'protocol/LSTMP_TRAINING_PROTOCOL_20261020_V2.md')
    shutil.copy2(Path(__file__), TARGET / 'protocol/prepare_run.py')
    preflight_script = ROOT / 'scripts/check_lstmp_training_v2_implementation_20261020.py'
    if preflight_script.exists():
        shutil.copy2(preflight_script, TARGET / 'protocol/check_implementation.py')
    test_source = ROOT / 'tests/test_lstmp_training_v2.py'
    if test_source.exists():
        shutil.copy2(test_source, TARGET / 'protocol/test_lstmp_training_v2.py')
    old_manifest = read(SOURCE / 'MANIFEST.json')
    snapshots = [path for parent in (TARGET / 'source_code', TARGET / 'source_project')
                 for path in parent.rglob('*') if path.is_file() and path.suffix in ('.py', '.json')]
    assets = [TARGET / 'initialization/first_50000.pt', TARGET / 'initialization/BINDING.json',
              TARGET / 'data/normalization.json', TARGET / 'data/receiver_train.json',
              TARGET / 'data/receiver_validation.json', TARGET / 'protocol/TRAINING_STATISTICS.json',
              TARGET / 'protocol/LSTMP_TRAINING_PROTOCOL_20261020_V2.md',
              TARGET / 'protocol/prepare_run.py']
    if preflight_script.exists():
        assets.append(TARGET / 'protocol/check_implementation.py')
    if test_source.exists():
        assets.append(TARGET / 'protocol/test_lstmp_training_v2.py')
    write(TARGET / 'MANIFEST.json', dict(schema='lstmp-conditional-bce-v2-frozen-run',
        configuration=config, snapshot_hashes={str(p): sha(p) for p in snapshots},
        bound_assets={str(p): sha(p) for p in assets},
        protected_assets=old_manifest['protected_assets'],
        implementation_source_run=str(SOURCE),
        source_manifest_sha256=sha(SOURCE / 'MANIFEST.json'),
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
$env:AFDM_LSTMP_CONFIG = Join-Path $trainingDirectory 'source_code\experiments\lstmp_training_v2_20261020\config.json'
$env:PYTHONUTF8 = '1'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$stdout = Join-Path $trainingDirectory ('stdout_' + $stamp + '.log')
$stderr = Join-Path $trainingDirectory ('stderr_' + $stamp + '.log')
$mode = if ($Resume) { '--resume' } else { '--fresh' }
$trainingProcess = Start-Process -FilePath $pythonExecutable -ArgumentList @('-u','-m','experiments.lstmp_training_v2_20261020.train','--train',$mode,'--device','cuda') -WorkingDirectory (Join-Path $trainingDirectory 'source_code') -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
@{launcher_pid=$trainingProcess.Id; launched_at=(Get-Date).ToString('o'); training_run=$trainingDirectory; stdout=$stdout; stderr=$stderr; resume=[bool]$Resume; planned_updates=100800; manifest_sha256=$manifestHash} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $trainingDirectory 'TRAINING_LAUNCH.json') -Encoding UTF8
Write-Output ('V2 training launched: ' + $trainingProcess.Id)
"""
    (TARGET / 'start_training.ps1').write_text(text.replace('__ROOT__', str(ROOT)), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--fresh', action='store_true')
    modes.add_argument('--refresh-before-launch', action='store_true')
    args = parser.parse_args()
    config = configuration()
    if args.fresh:
        if TARGET.exists():
            raise FileExistsError(TARGET)
        source_manifest = read(SOURCE / 'MANIFEST.json')
        for path, digest in source_manifest['snapshot_hashes'].items():
            if sha(path) != digest:
                raise ValueError(f'Historical implementation changed: {path}')
        for path, digest in source_manifest['protected_assets'].items():
            if sha(ROOT / path) != digest:
                raise ValueError(f'Historical protected asset changed: {path}')
        TARGET.mkdir()
        for name in ('source_code', 'source_project', 'data', 'initialization'):
            shutil.copytree(SOURCE / name, TARGET / name,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        binding = read(TARGET / 'initialization/BINDING.json')
        if (sha(TARGET / 'initialization/first_50000.pt') != binding['checkpoint_sha256'] or
            binding['identity']['source_sha256'] != config['pretrained_score']['sha256']):
            raise ValueError('AWGN initialization binding changed')
        scene_statistics(config)
    else:
        if not (TARGET / 'protocol/TRAINING_STATISTICS.json').exists():
            raise FileNotFoundError('Prepare the verified dataset before refreshing source')
    refresh_sources(config)
    write_launcher()
    write(TARGET / 'STATUS.json', dict(stage='PREPARED_PENDING_PREFLIGHT',
        updated_unix=time.time(), planned_updates=100800, protocol='v2 main A'))
    print(json.dumps(dict(run=str(TARGET), status='PREPARED_PENDING_PREFLIGHT',
                          manifest_sha256=sha(TARGET / 'MANIFEST.json'))), flush=True)


if __name__ == '__main__':
    main()
