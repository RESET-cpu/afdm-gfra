"""Prepare the authorized 5 -> 7 block without altering the completed parent."""
import copy
import json
import shutil
import time
from pathlib import Path

from prepare_lstmp_epoch6_continuation_20261020 import read, write, sha, ROOT

SOURCE = Path(r'D:\afdm-gfra-cpu\runs\lstmp_refinenet_50000_epoch6_20261020')
TARGET = SOURCE.parent/'lstmp_refinenet_depth7_20261020'
CHECKS = ROOT/'results/lstmp_depth7_preflight_20261020'


def main():
    started = time.time()
    if TARGET.exists():
        raise FileExistsError(TARGET)
    assert not (SOURCE/'RUNNING.lock').exists()
    assert read(SOURCE/'COMPLETE.json')['status'] == 'COMPLETE'
    manifest = read(SOURCE/'MANIFEST.json')
    for path, digest in manifest['snapshot_hashes'].items():
        assert sha(path) == digest, path
    for path, digest in manifest['protected_assets'].items():
        assert sha(ROOT/path) == digest, path
    for depth, epochs in enumerate([2, 2, 2, 2, 6], 1):
        folder = SOURCE/f'checkpoints/depth_{depth}'
        receipt = read(folder/'COMPLETE.json')
        assert receipt['steps'] == epochs*4800
        assert sha(folder/'best.pt') == receipt['checkpoint_sha256']
    parent_sha = sha(SOURCE/'checkpoints/depth_5/best.pt')
    config = copy.deepcopy(manifest['configuration'])
    config['run_directory'] = TARGET.as_posix()
    for key in ('continuation', 'repair_continuation', 'fixed_budget', 'prior_training_seconds'):
        config.pop(key, None)
    config['receiver']['maximum_depth'] = 7
    config['receiver']['epoch_schedule'] = [2, 2, 2, 2, 6, 2, 2]
    config['receiver']['auxiliary_total_weight'] = .8
    config['execution'] = dict(activation_checkpointing=False, adam_implementation='fused',
        selective_checkpoint=dict(minimum_depth=6, minimum_users=100, first_layers=3))
    config['depth_extension'] = dict(parent_depth=5, target_depth=7, inherited_updates=67200,
        additional_updates=19200, total_updates=86400, parent_run=str(SOURCE),
        parent_checkpoint='checkpoints/depth_5/best.pt', parent_checkpoint_sha256=parent_sha,
        initialization='Independent copies of preceding trained score, activity head and calibration',
        phase_schedule=['one epoch new layer plus preceding feedback c[2]', 'one epoch all layers joint'],
        adam_policy='Fresh Adam at each new depth; preserve its moments between adaptation and joint epoch',
        followup='Compare after depth7; depth9 is a separate block after review and sufficient remaining cumulative budget')
    TARGET.mkdir()
    copied = {}
    for name in ('source_code', 'source_project', 'data', 'initialization'):
        shutil.copytree(SOURCE/name, TARGET/name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for depth in range(1, 6):
        for name in ('best.pt', 'COMPLETE.json', 'history.json', 'best_validation.json', 'initial_validation.json'):
            source = SOURCE/f'checkpoints/depth_{depth}'/name
            if source.exists():
                destination = TARGET/source.relative_to(SOURCE)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
                assert sha(source) == sha(destination)
                copied[str(destination.relative_to(TARGET))] = sha(destination)
    for name in ('MANIFEST.json', 'COMPLETE.json', 'ACTIVE_TIME.json'):
        destination = TARGET/'provenance'/name
        destination.parent.mkdir(exist_ok=True)
        shutil.copy2(SOURCE/name, destination)
    package = TARGET/'source_code/experiments/lstmp_candidate_20261019'
    shutil.copy2(ROOT/'experiments/lstmp_depth_extension_20261020/extension.py', package/'extension.py')
    train = (package/'train.py').read_text(encoding='utf-8')
    before = "    if CONFIG['receiver']['maximum_depth']!=5:\n        raise ValueError('This candidate retains five independent layers')"
    after = "    if CONFIG['receiver']['maximum_depth'] != CONFIG['depth_extension']['target_depth']:\n        raise ValueError('Depth differs from the authorized extension block')"
    assert train.count(before) == 1
    train = train.replace(before, after)
    before = '        train_receiver(pretrained,scale,device,started)'
    assert train.count(before) == 1
    train = train.replace(before, '        from .extension import train_receiver as extend_receiver\n        extend_receiver(pretrained,scale,device,started)')
    (package/'train.py').write_text(train, encoding='utf-8')
    base = (package/'receiver_base.py').read_text(encoding='utf-8')
    before = "    auxiliary = CONFIG['receiver']['earlier_layer_loss_weight']"
    assert base.count(before) == 1
    base = base.replace(before, before+"\n    if 'auxiliary_total_weight' in CONFIG['receiver'] and len(terms) > 1:\n        auxiliary = CONFIG['receiver']['auxiliary_total_weight'] / (len(terms)-1)")
    (package/'receiver_base.py').write_text(base, encoding='utf-8')
    write(package/'reuse_50000_fast.json', config)
    paths = [p for directory in (package, TARGET/'source_project/afdm_jadcedd')
             for p in directory.rglob('*') if p.is_file() and p.suffix in ('.py', '.json')]
    write(TARGET/'MANIFEST.json', dict(schema='afdm-progressive-depth-extension-v1', configuration=config,
        snapshot_hashes={str(p.resolve()):sha(p) for p in paths}, protected_assets=manifest['protected_assets']))
    elapsed = time.time()-started
    inherited = read(SOURCE/'ACTIVE_TIME.json')['consumed_seconds']
    write(TARGET/'ACTIVE_TIME.json', dict(consumed_seconds=inherited+elapsed,
        inherited_training_seconds=inherited, preparation_seconds=elapsed))
    write(TARGET/'protocol/DEPTH_EXTENSION.json', dict(schema='two-layer-extension-block-v1',
        authorization='User requested continuing expansion, a reasonable training plan, and comparison after every two added layers.',
        created_unix=time.time(), **config['depth_extension'],
        parent_manifest_sha256=sha(SOURCE/'MANIFEST.json'), copied_assets=copied,
        inherited_training_seconds=inherited, preparation_seconds=elapsed,
        hard_time_budget_hours=12, train_scenes=4800, validation_scenes=1200,
        unique_training_scenes=4800, reused_each_epoch=True,
        learning_rates=dict(score=2e-5, activity=1e-4, calibration=1e-3),
        auxiliary_loss='(L_last + 0.8*mean(L_earlier))/1.8; equals parent at depth5',
        numerical_message_equations_unchanged=True, known_phase_and_noise=True,
        comparison='After successful depth7: new7 vs frozen5 vs legacy, identical fresh 20 inputs; report full1200 validation strata too',
        original_assets_preserved=True, training_started=False))
    launcher = (SOURCE/'start_training.ps1').read_text(encoding='utf-8-sig')
    launcher = launcher.replace('CPU_PREFLIGHT.json', 'PREFLIGHT.json')
    launcher = launcher.replace('completed_updates_before_launch=57600; remaining_updates=9600; next_depth=5; next_epoch=5',
                                'completed_updates_before_launch=67200; remaining_updates=19200; next_depth=6; next_epoch=1')
    (TARGET/'start_training.ps1').write_text(launcher, encoding='utf-8')
    write(TARGET/'STATUS.json', dict(stage='PREPARED_PENDING_PREFLIGHT', updated_unix=time.time()))
    print(json.dumps(dict(run=str(TARGET), preparation_seconds=elapsed, inherited_seconds=inherited,
                         additional_updates=19200, training_started=False)))


if __name__ == '__main__':
    main()
