"""Bind the user's requested original 20 scenes; infer only the frozen seven-layer model."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import time

ROOT = Path(r"C:\Users\25911\Desktop\afdm-gfra")
PREVIOUS = ROOT / "results/lstmp_epoch6_vs_legacy20_20261020"
INTERRUPTED = ROOT / "results/lstmp_depth7_threeway20_20261020"
OUT = ROOT / "results/lstmp_depth7_reuse_previous20_20261020"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"Expected one source fragment: {old[:100]}")
    return text.replace(old, new, 1)


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    previous = read(PREVIOUS / "PLAN.json")
    previous_complete = read(PREVIOUS / "COMPLETE.json")
    previous_audit = read(PREVIOUS / "RESULT_AUDIT.json")
    previous_binding = read(PREVIOUS / "BINDING.json")
    plan = copy.deepcopy(read(INTERRUPTED / "PLAN.json"))
    assert previous_complete["status"] == "COMPLETE" and previous_audit["status"] == "PASSED"
    assert previous_audit["plan_sha256"] == previous_complete["plan_sha256"] == sha(PREVIOUS / "PLAN.json")
    assert previous_audit["summary_sha256"] == previous_complete["summary_sha256"] == sha(PREVIOUS / "SUMMARY.json")
    assert previous_binding["selected_checkpoint_sha256"] == plan["five_layer_binding"]["checkpoint_sha256"]
    assert previous["old_binding"] == plan["old_binding"]
    assert previous["condition"] == plan["condition"]
    assert previous["scene_count"] == 20
    assert not (INTERRUPTED / "RUNNING.lock").exists()
    assert read(INTERRUPTED / "STATUS.json")["stage"] == "INTERRUPTED_BY_USER"
    run = Path(plan["training_run"])
    assert read(run / "COMPLETE.json")["status"] == "COMPLETE"
    assert not (run / "RUNNING.lock").exists()
    seven = read(run / "checkpoints/depth_7/COMPLETE.json")
    assert seven["selected_epoch"] == 1 and seven["steps"] == 9600
    assert seven["checkpoint_sha256"] == sha(run / plan["new_checkpoint"])

    OUT.mkdir()
    (OUT / "source").mkdir()
    assets = {}
    for source_name, target_name in (
        ("cases", "cases"), ("warmup", "warmup"),
        ("new_five_layer", "frozen_five_layer"),
        ("legacy_50000_damping01", "legacy_50000_damping01"),
    ):
        shutil.copytree(PREVIOUS / source_name, OUT / target_name)
        for original in sorted((PREVIOUS / source_name).rglob("*")):
            if original.is_file():
                target = Path(target_name) / original.relative_to(PREVIOUS / source_name)
                digest = sha(original)
                assert sha(OUT / target) == digest
                assets[target.as_posix()] = dict(origin=str(original), sha256=digest)
    references = {
        name: sha(PREVIOUS / name)
        for name in ("PLAN.json", "SUMMARY.json", "COMPLETE.json", "BINDING.json",
                     "RESULT_AUDIT.json", "per_scene.csv", "summary.csv")
    }
    evaluator_name = "evaluate_lstmp_depth7_threeway_20261020.py"
    auditor_name = "verify_lstmp_depth7_threeway20_20261020.py"
    for name, key in ((evaluator_name, "evaluator_sha256"),
                      (auditor_name, "auditor_sha256"), ("paired_core.py", "core_sha256")):
        assert sha(INTERRUPTED / "source" / name) == plan[key]
        shutil.copy2(INTERRUPTED / "source" / name, OUT / "source" / name)

    evaluator_path = OUT / "source" / evaluator_name
    source = evaluator_path.read_text(encoding="utf-8")
    source = replace_once(source, "class Adapter:\n", """def verify_reused_assets(out, plan):
    reuse = plan['reuse']
    previous = Path(reuse['previous_comparison'])
    for name, digest in reuse['reference_sha256'].items():
        if sha(previous/name) != digest:
            raise ValueError('Original comparison reference changed: '+name)
    for relative, item in reuse['copied_assets'].items():
        if sha(Path(item['origin'])) != item['sha256'] or sha(out/relative) != item['sha256']:
            raise ValueError('Reused input or baseline output changed: '+relative)
    original = read(previous/'PLAN.json')
    if original['cases'] != plan['cases'] or original['warmup'] != plan['warmup']:
        raise ValueError('Reused scene list changed')
    if original['old_binding'] != plan['old_binding']:
        raise ValueError('Historical legacy configuration changed')
    if read(previous/'BINDING.json')['selected_checkpoint_sha256'] != plan['five_layer_binding']['checkpoint_sha256']:
        raise ValueError('Historical five-layer model changed')


class Adapter:
""")
    source = replace_once(source,
        "            if sha(path) != case[name+'_sha256']: raise ValueError('Paired input changed: '+str(path))\n",
        "            if sha(path) != case[name+'_sha256']: raise ValueError('Paired input changed: '+str(path))\n"
        "    verify_reused_assets(out, plan)\n")
    source = replace_once(source,
        "    def __init__(self, method, plan, common, data, receiver):\n        import torch\n",
        "    def __init__(self, method, plan, common, data, receiver):\n"
        "        if method != 'new_seven_layer':\n"
        "            raise ValueError('User requested seven-layer inference only; baseline reruns are forbidden')\n"
        "        import torch\n")
    source = replace_once(source,
        "            adapter = Adapter(method, plan, common, data, receiver); torch.cuda.synchronize()\n",
        "            write(out/'INFERENCE_EXECUTION.json', dict(newly_inferred_methods=[method],\n"
        "                reused_methods=list(METHODS[1:]), pid=os.getpid(), started_unix=time.time()))\n"
        "            adapter = Adapter(method, plan, common, data, receiver); torch.cuda.synchronize()\n")
    source = replace_once(source,
        "    write(out/'SUMMARY.json', report)\n",
        "    report['reuse'] = dict(previous_comparison=plan['reuse']['previous_comparison'],\n"
        "        only_seven_newly_inferred=True, baseline_predictions_and_timings_reused=True,\n"
        "        prior_results_informed_depth_decision=True,\n"
        "        timing_note='Same frozen timing procedure and GPU model; different measurement sessions. Speed ratios are descriptive.')\n"
        "    write(out/'SUMMARY.json', report)\n")
    source = replace_once(source,
        "20 paired new scenes | K=40, Q=16, p=0.1, SNR=5 dB | Known phase/noise",
        "20 reused paired scenes | K=40, Q=16, p=0.1, SNR=5 dB | Known phase/noise\\nFive-layer and legacy timings reused from the previous session")
    evaluator_path.write_text(source, encoding="utf-8")

    auditor_path = OUT / "source" / auditor_name
    source = auditor_path.read_text(encoding="utf-8")
    source = replace_once(source,
        "assert row['stopping_reason'] == f'FIXED_{depth}_LAYERS' and len(trace['diagnostics']) == depth",
        "assert row['stopping_reason'] in ((f'FIXED_{depth}_LAYERS', 'FIXED_FIVE_LAYERS') if depth == 5 else (f'FIXED_{depth}_LAYERS',)) and len(trace['diagnostics']) == depth")
    source = replace_once(source,
        "    E.verify_plan(out, plan)\n",
        "    E.verify_plan(out, plan)\n"
        "    assert E.read(out/'INFERENCE_EXECUTION.json')['newly_inferred_methods'] == ['new_seven_layer']\n")
    source = replace_once(source,
        "'Same 1200 validation scenes and conditions retained'",
        "'Same 1200 validation scenes and conditions retained',\n"
        "                'All original baseline predictions and timings reused byte-for-byte; only seven newly inferred'")
    source = replace_once(source,
        "Descriptive paired scene bootstrap for one condition; not an equal-accuracy speed guarantee or population zero-error claim.",
        "Descriptive paired bootstrap of 20 previously revealed scenes; baseline timing is from a previous session. Not independent confirmation of the depth decision, an equal-accuracy speed guarantee, or a population zero-error claim.")
    auditor_path.write_text(source, encoding="utf-8")
    shutil.copy2(__file__, OUT / "source" / Path(__file__).name)
    plan.update(
        schema="depth7-threeway-reused20-v1", created_unix=time.time(),
        cases=previous["cases"], warmup=previous["warmup"],
        evaluator_sha256=sha(evaluator_path), auditor_sha256=sha(auditor_path),
        new_selection="Depth-seven epoch 1 selected by the original 1200-scene validation rule before this reused-scene evaluation; weights and threshold fixed.",
        seeds_independent_of_training_and_selection=False,
        seeds_independent_of_training=True,
        execution="Only seven-layer inference is executed. Frozen five-layer and legacy outputs, traces, overhead and timings are reused byte-for-byte from the completed original 20-scene comparison.",
        timing=previous["timing"] + " Seven is measured now; five and legacy timings come from the previous measurement session.",
        limitations="Twenty previously revealed scenes at K40/Q16/p0.1/SNR5dB, known phase/noise; their previous results informed the decision to increase depth. Paired comparison on identical inputs, not a fresh independent confirmation of that decision. Timing uses different sessions. Speed is not an equal-accuracy comparison; legacy's 600-iteration cap and fixed network depth do not establish convergence.",
        reuse=dict(previous_comparison=str(PREVIOUS), interrupted_new_batch=str(INTERRUPTED),
            authorization="User requested the previous 20 scenes and only a seven-layer supplement.",
            reference_sha256=references, copied_assets=assets,
            selected_seven_sha256=seven["checkpoint_sha256"]),
    )
    write(OUT / "PLAN.json", plan)
    write(OUT / "STATUS.json", dict(stage="READY_FOR_SEVEN_ONLY", updated_unix=time.time()))
    write(OUT / "PREPARATION_AUDIT.json", dict(
        status="PASSED", checked_unix=time.time(), copied_files=len(assets),
        original_case_list_retained=True, original_baselines_byte_identical=True,
        newly_inferred_methods=["new_seven_layer"], gpu_used=False,
        plan_sha256=sha(OUT / "PLAN.json"),
    ))
    print(json.dumps(dict(output=str(OUT), copied_files=len(assets), only_seven_inference=True)))


if __name__ == "__main__":
    main()
