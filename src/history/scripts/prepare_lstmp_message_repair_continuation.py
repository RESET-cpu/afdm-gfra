"""Prepare, but do not launch, a separately recorded continuation after acceptance."""
import copy,hashlib,json,shutil,time
from pathlib import Path
import torch
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path(r'D:\afdm-gfra-cpu\runs\lstmp_refinenet_50000_fast_20261019')
TARGET=SOURCE.parent/'lstmp_refinenet_50000_message_damping_20261019'
CHECKS=ROOT/'results/lstmp_message_damping_resume_checks_20261019'
DEV=ROOT/'results/lstmp_message_damping_development_20261019'


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(2**20),b''):h.update(b)
    return h.hexdigest()


def main():
    if TARGET.exists():raise FileExistsError(TARGET)
    if (SOURCE/'RUNNING.lock').exists():raise RuntimeError('Original training is still active')
    if read(SOURCE/'STATUS.json')['stage']!='FAILED':raise RuntimeError('Unexpected original state')
    checks=read(CHECKS/'REPORT.json');dev=read(DEV/'REPORT.json')
    if not checks['acceptance_passed'] or not dev['acceptance_passed']:raise RuntimeError('Repair not accepted')
    candidate=ROOT/'experiments/lstmp_message_damping_candidate_20261019/receiver.py'
    if sha(candidate)!=checks['candidate_sha256']:raise RuntimeError('Repair differs from evaluated source')
    original=read(SOURCE/'MANIFEST.json')
    for path,value in original['snapshot_hashes'].items():
        if sha(path)!=value:raise RuntimeError('Original frozen source changed: '+path)
    for path,value in original['protected_assets'].items():
        if sha(ROOT/path)!=value:raise RuntimeError('Protected asset changed: '+path)
    last=SOURCE/'checkpoints/depth_2/last.pt';saved=torch.load(last,map_location='cpu',weights_only=False)
    if (saved['depth'],saved['epoch'],saved['cursor'],saved['steps'])!=(2,3,0,9600):raise RuntimeError('Unexpected completed update count')
    if sha(last)!=read(DEV/'PLAN.json')['protected'][str(last)]:raise RuntimeError('Evaluated checkpoint changed')
    config=copy.deepcopy(original['configuration']);config['run_directory']=str(TARGET).replace('\\','/')
    config['receiver']['feedback_damping']=dict(parameterization='Gaussian natural parameters',coefficient='min(1, initial_variance / proposed_extrinsic_variance)',
        scope='Feedback only; current layer score, channel mean and activity logits unchanged')
    config['repair_continuation']=dict(source_run=str(SOURCE),source_manifest_sha256=sha(SOURCE/'MANIFEST.json'),source_checkpoint_sha256=sha(last),
        development_report_sha256=sha(DEV/'REPORT.json'),resume_checks_sha256=sha(CHECKS/'REPORT.json'),completed_optimizer_updates=19200,
        remaining_optimizer_updates=38400,source_depth2_selected_epoch=0,repaired_selected_epoch=2,
        stage2_selection='Re-evaluated epoch 0 and the already fully trained epoch 2 under the repaired forward; epoch 2 improves validation. No added depth-2 epochs or optimizer steps.')
    TARGET.mkdir()
    for name in ['checkpoints','data','initialization','source_code','source_project']:
        shutil.copytree(SOURCE/name,TARGET/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    shutil.copy2(SOURCE/'CONTINUATION.json',TARGET/'CONTINUATION.json')
    shutil.copy2(SOURCE/'history.jsonl',TARGET/'history_before_repair.jsonl')
    for name in ['STATUS.json','FAILURE.json','MANIFEST.json','ACTIVE_TIME.json']:
        dest=TARGET/'provenance/original_failed_run'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(SOURCE/name,dest)
    package=TARGET/'source_code/experiments/lstmp_candidate_20261019'
    shutil.copy2(package/'receiver.py',package/'receiver_base.py')
    code=candidate.read_text(encoding='utf-8').replace('from experiments.lstmp_candidate_20261019 import receiver as base','from . import receiver_base as base')
    (package/'message_damping.py').write_text(code,encoding='utf-8')
    (package/'receiver.py').write_text('"""Frozen repaired forward; original equations remain in receiver_base."""\nfrom .receiver_base import *\nfrom .message_damping import Receiver\n',encoding='utf-8')
    write(package/'reuse_50000_fast.json',config)
    folder=TARGET/'checkpoints/depth_2';archive=folder/'before_repair';archive.mkdir()
    for name in ['best.pt','history.json','initial_validation.json']:
        if (folder/name).exists():shutil.copy2(folder/name,archive/name)
    # last.pt, including optimizer, remains byte-for-byte the original failed end checkpoint.
    torch.save(dict(state=saved['state'],depth=2,scale=config['pretrained_score']['global_complex_rms'],epoch=2,
                    repair_origin=config['repair_continuation']),folder/'best.pt')
    selected=torch.load(folder/'best.pt',map_location='cpu',weights_only=False)['state']
    if not all(torch.equal(v,selected[k]) for k,v in saved['state'].items()):raise RuntimeError('Weight copy mismatch')
    del selected,saved
    for name,source in [('best_validation.json','epoch2_validation.json'),('initial_validation.json','epoch0_validation.json')]:
        shutil.copy2(CHECKS/source,folder/name)
    initial=checks['validation']['initial'];trained=checks['validation']['trained']
    write(folder/'history.json',[dict(epoch=0,validation=initial,selected=True,scope='Re-evaluated repaired forward; no optimization'),
        dict(epoch=2,validation=trained,selected=True,scope='Re-evaluated existing trained epoch-2 weights; no optimization',
             original_training_history='before_repair/history.json')])
    write(folder/'COMPLETE.json',dict(status='COMPLETE',selected_epoch=2,steps=9600,reason='REVALIDATED_COMPLETED_BUDGET_AFTER_MESSAGE_REPAIR',
        best_validation_loss=trained['loss'],checkpoint_sha256=sha(folder/'best.pt'),repair_record='../../protocol/MESSAGE_REPAIR_CONTINUATION.json'))
    # Count the whole resume verification in the existing cap; never reset the clock.
    original_seconds=read(SOURCE/'ACTIVE_TIME.json')['consumed_seconds']
    write(TARGET/'ACTIVE_TIME.json',dict(consumed_seconds=original_seconds+checks['elapsed_seconds'],
        inherited_training_seconds=original_seconds,resume_verification_seconds=checks['elapsed_seconds']))
    paths=[p for directory in [package,TARGET/'source_project/afdm_jadcedd'] for p in directory.rglob('*') if p.is_file() and p.suffix in ['.py','.json']]
    write(TARGET/'MANIFEST.json',dict(schema=original['schema'],configuration=config,snapshot_hashes={str(p.resolve()):sha(p) for p in paths},protected_assets=original['protected_assets']))
    receipt=dict(created_unix=time.time(),authorization='User requested stability repair, preservation and resuming only after independent validation; forward change explained before resuming.',
        **config['repair_continuation'],source_candidate_sha256=sha(candidate),frozen_candidate_sha256=sha(package/'message_damping.py'),
        only_candidate_source_difference='Import receiver_base rather than receiver; base equations are an exact copy of original frozen receiver.py.',
        frozen_base_matches_original=sha(package/'receiver_base.py')==sha(SOURCE/'source_code/experiments/lstmp_candidate_20261019/receiver.py'),
        last_checkpoint_copied_unchanged=sha(folder/'last.pt')==sha(last),first_layer_checkpoint_unchanged=sha(TARGET/'checkpoints/depth_1/best.pt')==sha(SOURCE/'checkpoints/depth_1/best.pt'),
        budget=dict(training_scenes=4800,validation_scenes=1200,epoch_schedule=[2,2,2,2,4],total_optimizer_updates=57600,hard_time_budget_hours=12),
        source_run_preserved=True,train_started=False)
    if not all(receipt[k] for k in ['frozen_base_matches_original','last_checkpoint_copied_unchanged','first_layer_checkpoint_unchanged']):raise RuntimeError('Provenance mismatch')
    write(TARGET/'protocol/MESSAGE_REPAIR_CONTINUATION.json',receipt)
    write(TARGET/'STATUS.json',dict(stage='PREPARED_AFTER_STABILITY_REPAIR',updated_unix=time.time(),next_depth=3,completed_optimizer_updates=19200))
    write(TARGET/'LAUNCH.json',dict(project_root=str(ROOT),running_configuration=str(package/'reuse_50000_fast.json'),source_snapshot=True,original_run_preserved=str(SOURCE),created_unix=time.time()))
    write(CHECKS/'PREPARED_RUN.json',dict(training_run=str(TARGET),manifest_sha256=sha(TARGET/'MANIFEST.json'),record=str(TARGET/'protocol/MESSAGE_REPAIR_CONTINUATION.json')))
    print(json.dumps(receipt),flush=True)


if __name__=='__main__':main()
