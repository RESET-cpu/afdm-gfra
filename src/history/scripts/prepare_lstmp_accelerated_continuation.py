"""Fork a paused run with identical learning state and measured execution flags."""
import json
import shutil
import time
from pathlib import Path
import benchmark_lstmp_training_execution as B
import torch


def main():
    source=B.RUN
    target=source.parent/'lstmp_refinenet_50000_fast_20261019'
    if target.exists():raise FileExistsError(target)
    assert not (source/'RUNNING.lock').exists()
    assert json.loads((source/'STATUS.json').read_text())['stage']=='PAUSED'
    original=json.loads((source/'MANIFEST.json').read_text(encoding='utf-8'))
    for path,digest in original['snapshot_hashes'].items():assert B.common.sha(Path(path))==digest,path
    for path,digest in original['protected_assets'].items():assert B.common.sha(B.ROOT/path)==digest,path
    old_checkpoint=source/'checkpoints/depth_2/last.pt'
    saved=torch.load(old_checkpoint,map_location='cpu',weights_only=False)
    assert (saved['depth'],saved['epoch'],saved['cursor'],saved['steps'])==(2,1,776,776)
    capacity=json.loads((B.OUT/'SELECTIVE_FULL_DEPTH_CAPACITY.json').read_text())
    assert capacity['memory_margin_passed']
    config=json.loads(json.dumps(original['configuration']))
    config['run_directory']=str(target).replace('\\','/')
    config['execution']=capacity['settings']
    changed=[k for k in config if config[k]!=original['configuration'].get(k)]
    assert set(changed)=={'run_directory','execution'}
    target.mkdir()
    for name in ('checkpoints','data','initialization','source_code','source_project'):
        shutil.copytree(source/name,target/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    for name in ('CONTINUATION.json','ACTIVE_TIME.json','history.jsonl'):
        shutil.copy2(source/name,target/name)
    copied={}
    for folder in ('checkpoints','data','initialization'):
        for path in (source/folder).rglob('*'):
            if path.is_file():
                relative=path.relative_to(source)
                digest=B.common.sha(path)
                assert B.common.sha(target/relative)==digest
                copied[str(relative)]=digest
    candidate=target/'source_code/experiments/lstmp_candidate_20261019'
    for name in ('train.py','receiver.py','execution.py'):
        shutil.copy2(B.ROOT/'experiments/lstmp_candidate_20261019'/name,candidate/name)
    config_path=candidate/'reuse_50000_fast.json'
    B.common.save_json(config_path,config)
    B.common.save_json(B.ROOT/'experiments/lstmp_candidate_20261019/reuse_50000_fast.json',config)
    sources=[p for directory in (candidate,target/'source_project/afdm_jadcedd')
             for p in directory.rglob('*') if p.is_file() and p.suffix in ('.py','.json')]
    manifest=dict(schema=original['schema'],configuration=config,
        snapshot_hashes={str(p.resolve()):B.common.sha(p) for p in sources},
        protected_assets=original['protected_assets'])
    B.common.save_json(target/'MANIFEST.json',manifest)
    receipt=dict(created_unix=time.time(),authorization='User requested higher GPU utilization and faster training; learning protocol preserved',
        source_run=str(source),target_run=str(target),source_manifest_sha256=B.common.sha(source/'MANIFEST.json'),
        source_checkpoint_sha256=B.common.sha(old_checkpoint),copied_sha256=copied,
        depth=saved['depth'],epoch=saved['epoch'],cursor=saved['cursor'],depth_optimizer_steps=saved['steps'],
        total_optimizer_updates_completed=9600+saved['steps'],model_and_optimizer_copied_byte_for_byte=True,
        partial_epoch_loss_preserved=True,scene_order_and_selection_preserved=True,
        changed_top_level_configuration_keys=changed,execution=config['execution'],
        training_scenes=config['receiver']['train_scenes'],validation_scenes=config['receiver']['validation_scenes'],
        epoch_schedule=config['receiver']['epoch_schedule'],tests_passed=32,
        benchmark_report=str(B.OUT/'REPORT.json'),maximum_depth_capacity_report=str(B.OUT/'SELECTIVE_FULL_DEPTH_CAPACITY.json'),
        numerical_scope='Fused Adam and activation recomputation change floating-point execution; not bitwise identical subsequent training. Paired first update max parameter difference 1.1921e-7.',
        original_run_retained_paused=True,weights_from_benchmark_used=False)
    B.common.save_json(target/'protocol/EXECUTION_CONTINUATION.json',receipt)
    B.common.save_json(source/'protocol/EXECUTION_SUCCESSOR.json',dict(target_run=str(target),record=str(target/'protocol/EXECUTION_CONTINUATION.json')))
    B.common.save_json(target/'STATUS.json',dict(stage='PREPARED',updated_unix=time.time(),depth=2,epoch=1,scene=saved['cursor']))
    B.common.save_json(target/'LAUNCH.json',dict(project_root=str(B.ROOT),running_configuration=str(config_path),source_snapshot=True,
        original_run_preserved=str(source),created_unix=time.time(),authorization=receipt['authorization']))
    B.common.save_json(B.OUT/'ACTIVE_RUN.json',dict(run_directory=str(target),configuration=str(config_path)))
    print(json.dumps({k:v for k,v in receipt.items() if k!='copied_sha256'}),flush=True)


if __name__=='__main__':main()
