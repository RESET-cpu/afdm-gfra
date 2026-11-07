"""Rebind the untouched 20 saved inputs to a separately frozen repaired training run."""
import copy,importlib.util,json,shutil,time
from pathlib import Path
from prepare_lstmp_message_repair_continuation import ROOT,TARGET,read,write,sha


def main():
    source=ROOT/'results/lstmp_vs_legacy20_20261019'
    target=ROOT/'results/lstmp_vs_legacy20_repaired_20261019'
    if target.exists():raise FileExistsError(target)
    if (source/'RUNNING.lock').exists() or (source/'COMPLETE.json').exists():raise RuntimeError('Original comparison already began')
    if not (TARGET/'protocol/MESSAGE_REPAIR_CONTINUATION.json').exists():raise RuntimeError('Repair continuation not prepared')
    original=read(source/'PLAN.json');target.mkdir()
    for name in ['cases','warmup','source']:shutil.copytree(source/name,target/name)
    shutil.copy2(source/'start_when_ready.ps1',target/'start_when_ready.ps1')
    plan=copy.deepcopy(original)
    plan.update(created_unix=time.time(),training_run=str(TARGET),training_manifest_sha256=sha(TARGET/'MANIFEST.json'))
    plan['new_selection']='Final depth-five validation-selected checkpoint after all 57600 updates; first 19200 inherited from preserved original training, with repaired depth 2 revalidated before remaining training.'
    plan['repair_binding']=dict(original_plan=str(source/'PLAN.json'),original_plan_sha256=sha(source/'PLAN.json'),
        continuation_record=str(TARGET/'protocol/MESSAGE_REPAIR_CONTINUATION.json'),
        continuation_record_sha256=sha(TARGET/'protocol/MESSAGE_REPAIR_CONTINUATION.json'),
        exact_inputs_copied=True,scenarios_thresholds_legacy_configuration_timing_and_metrics_unchanged=True)
    write(target/'PLAN.json',plan)
    write(target/'STATUS.json',dict(stage='WAITING_FOR_TRAINING',updated_unix=time.time()))
    script=target/'source/evaluate_lstmp_vs_legacy20.py'
    spec=importlib.util.spec_from_file_location('rebound_evaluation',script);evaluation=importlib.util.module_from_spec(spec);spec.loader.exec_module(evaluation)
    evaluation.verify_plan(target,plan)
    common,data,receiver=evaluation.modules(ROOT,TARGET)
    if receiver.Receiver.__module__!='experiments.lstmp_candidate_20261019.message_damping':raise RuntimeError('Evaluation does not use repaired forward')
    if read(source/'PLAN.json')!=original:raise RuntimeError('Original frozen plan changed')
    write(target/'PREFLIGHT.json',dict(status='PASSED',checked_unix=time.time(),scene_count=20,warmup_count=1,
        input_files_and_truth_files_byte_identical=True,evaluator_unchanged=True,legacy_binding_unchanged=True,
        receiver_class=receiver.Receiver.__module__+'.Receiver',manifest_verified=True,gpu_used=False,evaluation_started=False,
        source_plan_sha256=sha(source/'PLAN.json'),plan_sha256=sha(target/'PLAN.json')))
    print(json.dumps(dict(comparison_directory=str(target),preflight='PASSED',evaluation_started=False)),flush=True)


if __name__=='__main__':main()
