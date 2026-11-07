"""Freeze fresh paired scenes for the authorized final-stage continuation."""
import ast
import importlib.util
import json
import shutil
import time
from pathlib import Path

from prepare_lstmp_epoch6_continuation_20261020 import ROOT, SOURCE, TARGET, PRIOR_COMPARISON, read, write, sha

OUTPUT = ROOT/'results/lstmp_epoch6_vs_legacy20_20261020'


def main():
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    original_path = PRIOR_COMPARISON/'source/evaluate_lstmp_vs_legacy20.py'
    original = original_path.read_text(encoding='utf-8-sig')
    variant = original
    changes = [
        ("RUN = Path(r'D:\\afdm-gfra-cpu\\runs\\lstmp_refinenet_50000_fast_20261019')", f"RUN = Path(r'{TARGET}')"),
        ("OUT = ROOT / 'results/lstmp_vs_legacy20_20261019'", "OUT = ROOT / 'results/lstmp_epoch6_vs_legacy20_20261020'"),
        ('range(202610198700001, 202610198700021)', 'range(202610208700001, 202610208700021)'),
        ('WARMUP_SEED = 202610198799999', 'WARMUP_SEED = 202610208799999'),
        ('enumerate((2, 2, 2, 2, 4), 1)', 'enumerate((2, 2, 2, 2, 6), 1)'),
        ('only after all 57600 updates finish', 'only after all 67200 updates finish, including the inherited 57600'),
    ]
    for before, after in changes:
        assert variant.count(before) == 1, before
        variant = variant.replace(before, after)
    marker = "    write(out / 'PLAN.json', plan)"
    extension = '''    previous = root / 'results/lstmp_vs_legacy20_repaired_20261019'
    old_plan = read(previous/'PLAN.json')
    old_seeds = {c['seed'] for c in old_plan['cases']} | {old_plan['warmup']['seed']}
    if old_seeds.intersection(SEEDS + [WARMUP_SEED]):
        raise ValueError('Fresh confirmation overlaps the revealed prior comparison')
    if plan['old_binding'] != old_plan['old_binding']:
        raise ValueError('Legacy receiver binding differs from the prior comparison')
    continuation = run/'protocol/EPOCH6_CONTINUATION.json'
    plan['epoch_extension'] = dict(record=str(continuation), record_sha256=sha(continuation),
        inherited_updates=57600, additional_updates=9600, total_updates=67200,
        epoch_schedule=[2,2,2,2,6], previous_comparison=str(previous),
        previous_plan_sha256=sha(previous/'PLAN.json'),
        previous_summary_sha256=sha(previous/'SUMMARY.json'),
        independent_fresh_confirmation=True)
'''
    assert variant.count(marker) == 1
    variant = variant.replace(marker, extension+marker)
    marker = "    write(out / 'SUMMARY.json', report)"
    extension = '''    inherited = read(Path(plan['training_run'])/'protocol/EPOCH6_CONTINUATION.json')['inherited_training_seconds']
    report['training_overhead']['inherited_finetuning_seconds'] = inherited
    report['training_overhead']['current_continuation_seconds'] = report['training_overhead']['additional_finetuning_seconds'] - inherited
    report['training_overhead']['cumulative_time_limit_hours'] = 12
    report['training_overhead']['additional_finetuning_seconds_scope'] = 'Cumulative fine-tuning across the preserved parent and this continuation; current_continuation_seconds is this extension alone.'
'''
    assert variant.count(marker) == 1
    variant = variant.replace(marker, extension+marker)
    before = {n.name:ast.dump(n) for n in ast.parse(original).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
    after = {n.name:ast.dump(n) for n in ast.parse(variant).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
    changed_functions = [name for name in before if before[name] != after[name]]
    assert set(changed_functions) == {'readiness','prepare','make_report'}
    # Every numerical receiver, scoring and timing function is retained exactly.
    script = ROOT/'scripts/evaluate_lstmp_epoch6_vs_legacy20.py'
    if script.exists():
        raise FileExistsError(script)
    script.write_text(variant, encoding='utf-8')
    spec = importlib.util.spec_from_file_location('epoch6_evaluation', script)
    evaluation = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(evaluation)
    assert evaluation.readiness(TARGET)[0] is False
    try:
        evaluation.readiness(SOURCE)
    except ValueError as error:
        assert 'depth 5' in str(error)
    else:
        raise AssertionError('Old four-epoch completion was incorrectly accepted')
    original_plan_hash = sha(PRIOR_COMPARISON/'PLAN.json')
    original_summary_hash = sha(PRIOR_COMPARISON/'SUMMARY.json')
    evaluation.prepare(ROOT, TARGET, OUTPUT)
    # Inspect the copied evaluator, since its exact path is bound by PLAN.json.
    frozen_path = OUTPUT/'source'/script.name
    frozen_spec = importlib.util.spec_from_file_location('frozen_epoch6_evaluation', frozen_path)
    frozen = importlib.util.module_from_spec(frozen_spec)
    frozen_spec.loader.exec_module(frozen)
    plan = read(OUTPUT/'PLAN.json')
    frozen.verify_plan(OUTPUT, plan)
    common, _, receiver = frozen.modules(ROOT, TARGET)
    assert receiver.Receiver.__module__ == 'experiments.lstmp_candidate_20261019.message_damping'
    assert common.CONFIG['receiver']['epoch_schedule'] == [2,2,2,2,6]
    assert sha(PRIOR_COMPARISON/'PLAN.json') == original_plan_hash
    assert sha(PRIOR_COMPARISON/'SUMMARY.json') == original_summary_hash
    launcher = (PRIOR_COMPARISON/'start_when_ready.ps1').read_text(encoding='utf-8-sig')
    launcher = launcher.replace('source\\evaluate_lstmp_vs_legacy20.py', 'source\\evaluate_lstmp_epoch6_vs_legacy20.py')
    (OUTPUT/'start_when_ready.ps1').write_text(launcher, encoding='utf-8')
    auditor = (ROOT/'scripts/verify_lstmp_comparison20_20261020.py').read_text(encoding='utf-8-sig')
    auditor = auditor.replace("OUT=ROOT/'results/lstmp_vs_legacy20_repaired_20261019'", "OUT=ROOT/'results/lstmp_epoch6_vs_legacy20_20261020'")
    auditor = auditor.replace('enumerate([2,2,2,2,4],1)', 'enumerate([2,2,2,2,6],1)')
    auditor = auditor.replace('source/evaluate_lstmp_vs_legacy20.py', 'source/evaluate_lstmp_epoch6_vs_legacy20.py')
    (ROOT/'scripts/verify_lstmp_epoch6_comparison20_20261020.py').write_text(auditor, encoding='utf-8')
    receipt = dict(status='PASSED', checked_unix=time.time(), scene_count=20, warmup_count=1,
        expected_total_optimizer_updates=67200, rejects_old_epoch4_completion=True,
        incomplete_training_gate_verified=True, receiver_class=receiver.Receiver.__module__+'.Receiver',
        fresh_seed_range=[evaluation.SEEDS[0],evaluation.SEEDS[-1]],
        seeds_disjoint_from_prior_comparison_and_training=True, legacy_binding_unchanged=True,
        numerical_scoring_and_timing_functions_unchanged=True,
        changed_evaluator_functions=changed_functions, source_evaluator_sha256=sha(original_path),
        evaluator_sha256=sha(frozen_path), plan_sha256=sha(OUTPUT/'PLAN.json'),
        gpu_used=False, evaluation_started=False, prior_results_unchanged=True)
    write(OUTPUT/'PREFLIGHT.json', receipt)
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
