"""Evaluate the selected v3 depth-ten receiver on the previously saved 20 inputs.

Preparation and inspection are CPU-only. Inference is gated on completion of all
ten training stages. Historical predictions and timings are reused verbatim.
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import traceback

for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "1"
import numpy as np

ROOT = Path(r"C:\Users\25911\Desktop\afdm-gfra")
RUN = Path(r"D:\afdm-gfra-cpu\runs\lstmp_conditional_bce_v3_depth10_fast_20261020")
PREVIOUS = ROOT / "results/lstmp_depth7_reuse_previous20_20261020"
OUT = ROOT / "results/lstmp_v3_depth10_previous20_20261020"
NEW = "v3_ten_layer"
BASELINES = ("new_seven_layer", "frozen_five_layer", "legacy_50000_damping01")
METHODS = (NEW,) + BASELINES
LABELS = ("第三版十层", "此前七层", "此前五层", "旧三网络")
CONFIG_REL = "source_code/experiments/lstmp_execution_v3_20261020/config.json"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False,
                                    allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def core(out):
    spec = importlib.util.spec_from_file_location("previous20_core", out / "source/paired_core.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def readiness(run):
    """No checkpoint is eligible until every scheduled training/validation ends."""
    if not (run / "COMPLETE.json").exists():
        status = read(run / "STATUS.json") if (run / "STATUS.json").exists() else {}
        return False, "TRAINING_" + status.get("stage", "NOT_COMPLETE")
    complete = read(run / "COMPLETE.json")
    if complete.get("status") != "COMPLETE" or complete.get("completed_updates") != 142500:
        raise ValueError("Unexpected final training budget/completion record")
    if (run / "RUNNING.lock").exists():
        return False, "WAITING_FOR_TRAINING_EXIT"
    for depth in range(1, 11):
        folder = run / "checkpoints" / f"depth_{depth}"
        receipt = read(folder / "COMPLETE.json")
        history = read(folder / "history.json")
        if receipt["depth"] != depth or receipt["updates"] != 14250:
            raise ValueError(f"Incomplete training budget at depth {depth}")
        if [r["epoch"] for r in history] != [0, 1, 2, 3]:
            raise ValueError(f"Incomplete validation history at depth {depth}")
        if any(r["scenes"] != 1900 for r in history):
            raise ValueError(f"Incomplete validation population at depth {depth}")
        selected = min(history, key=lambda r: (r["selection_loss"], r["epoch"]))["epoch"]
        if receipt["selected_epoch"] != selected:
            raise ValueError(f"Validation selection changed at depth {depth}")
        if any(not (folder / f"validation_epoch_{epoch}.json").exists() for epoch in range(4)):
            raise ValueError(f"Missing full validation file at depth {depth}")
    selected = run / "checkpoints/depth_10/best.pt"
    if Path(complete["selected_checkpoint"]).resolve() != selected.resolve():
        raise ValueError("Final checkpoint must be the selected depth-ten receiver")
    return True, "READY"


def verify_plan(out):
    plan = read(out / "PLAN.json")
    if sha(Path(plan["training_run"]) / "MANIFEST.json") != plan["training_manifest_sha256"]:
        raise ValueError("Training manifest changed")
    for path, digest in plan["training_source_hashes"].items():
        if sha(path) != digest:
            raise ValueError("Frozen training source changed: " + path)
    for name, digest in plan["source_sha256"].items():
        if sha(out / "source" / name) != digest:
            raise ValueError("Evaluation source changed: " + name)
    for relative, digest in plan["reused_asset_sha256"].items():
        if sha(out / relative) != digest or sha(PREVIOUS / relative) != digest:
            raise ValueError("Previously paired asset changed: " + relative)
    for name, digest in plan["previous_reference_sha256"].items():
        if sha(PREVIOUS / name) != digest:
            raise ValueError("Previous comparison reference changed: " + name)
    for case in plan["cases"] + [plan["warmup"]]:
        folder = out / "cases" / f'{case["index"]:03d}' if "index" in case else out / "warmup"
        for name, suffix in (("input", ".npz"), ("truth", ".npz"), ("generation", ".json")):
            if sha(folder / (name + suffix)) != case[name + "_sha256"]:
                raise ValueError("Saved scene differs from the original plan: " + str(folder))
    return plan


def checked_rows(out, plan, method, C):
    rows = []
    for case in plan["cases"]:
        index = case["index"]
        folder = out / method
        row = read(folder / f"{index:03d}.json")
        if (row["status"] != "COMPLETE" or row["case_index"] != index or
                row["seed"] != case["seed"] or row["input_sha256"] != case["input_sha256"] or
                row["prediction_sha256"] != sha(folder / f"{index:03d}.npz")):
            raise ValueError(f"Invalid saved prediction: {method}/{index}")
        with np.load(folder / f"{index:03d}.npz", allow_pickle=False) as pred:
            with np.load(out / "cases" / f"{index:03d}" / "truth.npz", allow_pickle=False) as truth:
                scores = C.score_arrays(pred["estimate"], pred["probabilities"],
                                        truth["channel"], truth["activity"], threshold=.5)
        for key, value in scores.items():
            if not np.isclose(value, row[key], rtol=1e-12, atol=1e-12):
                raise ValueError(f"Independent rescoring mismatch: {method}/{index}/{key}")
        if not np.isclose(row["total_seconds"],
                          row["preparation_seconds"] + row["inference_seconds"],
                          rtol=1e-10, atol=1e-10):
            raise ValueError("Invalid timing components")
        if method == NEW:
            trace = read(folder / f"{index:03d}_trace.json")
            if (row["iterations"] != 10 or row["stopping_reason"] != "FIXED_10_LAYERS" or
                    row["first_score_calls"] != 10 or row["second_score_calls"] != 0 or
                    len(trace["diagnostics"]) != 10):
                raise ValueError("Unexpected ten-layer inference trace")
        rows.append(row)
    return rows


def prepare(out):
    if out.exists():
        raise FileExistsError(out)
    old = read(PREVIOUS / "PLAN.json")
    complete, audit = read(PREVIOUS / "COMPLETE.json"), read(PREVIOUS / "RESULT_AUDIT.json")
    if complete["status"] != "COMPLETE" or audit["status"] != "PASSED":
        raise ValueError("Previous comparison was not verified")
    if complete["plan_sha256"] != sha(PREVIOUS / "PLAN.json"):
        raise ValueError("Previous plan changed")
    if complete["summary_sha256"] != sha(PREVIOUS / "SUMMARY.json"):
        raise ValueError("Previous summary changed")
    if old["scene_count"] != 20 or [c["seed"] for c in old["cases"]] != list(range(202610208700001, 202610208700021)):
        raise ValueError("Unexpected original twenty scenes")
    cfg, manifest = read(RUN / CONFIG_REL), read(RUN / "MANIFEST.json")
    if (cfg["planned_updates"] != 142500 or cfg["receiver"]["epoch_schedule"] != [3] * 10 or
            cfg["receiver"]["train_scenes"] != 4750 or cfg["receiver"]["validation_scenes"] != 1900):
        raise ValueError("Unexpected training protocol")
    out.mkdir(parents=True)
    (out / "source").mkdir()
    shutil.copy2(__file__, out / "source" / Path(__file__).name)
    shutil.copy2(PREVIOUS / "source/paired_core.py", out / "source/paired_core.py")
    assets = {}
    for name in ("cases", "warmup") + BASELINES:
        shutil.copytree(PREVIOUS / name, out / name)
        for path in sorted((out / name).rglob("*")):
            if path.is_file():
                assets[path.relative_to(out).as_posix()] = sha(path)
    plan = dict(
        schema="lstmp-v3-depth10-previous20-v1", created_unix=time.time(),
        authorization="User requested the same twenty scenes after ten-layer training completes.",
        root=str(ROOT), training_run=str(RUN), training_manifest_sha256=sha(RUN / "MANIFEST.json"),
        training_source_hashes=manifest["snapshot_hashes"],
        source_sha256={p.name: sha(p) for p in (out / "source").iterdir()},
        previous_comparison=str(PREVIOUS),
        previous_reference_sha256={name: sha(PREVIOUS / name) for name in
                                   ("PLAN.json", "COMPLETE.json", "RESULT_AUDIT.json", "BINDING.json", "SUMMARY.json")},
        reused_asset_sha256=assets, cases=old["cases"], warmup=old["warmup"], scene_count=20,
        condition=old["condition"], phase_mode="known", noise_mode="known",
        methods=list(METHODS), scale=old["scale"], activity_threshold=.5,
        allow_tf32=old["allow_tf32"], cpu_threads=old["cpu_threads"],
        new_checkpoint="checkpoints/depth_10/best.pt",
        selection="Minimum original validation selection_loss over epochs 0..3; earlier epoch on ties.",
        old_binding=old["old_binding"], five_layer_binding=old["five_layer_binding"],
        seven_layer_binding=read(PREVIOUS / "BINDING.json"),
        inference="Only the new selected ten-layer receiver is inferred. All three reference predictions remain byte-identical.",
        timing=old["timing"] + " Ten is measured after training exits. Every reference time is historical.",
        bootstrap=dict(samples=10000, seed=2026102097, unit="paired physical scene",
                       interpretation="Descriptive percentile intervals, not independent confirmation."),
        limitations="Previously revealed 20 scenes at one known-phase/noise condition. SNR remains 5 dB to preserve the original comparison. No test-based tuning or model selection. Historical timings are descriptive across sessions; depth and training changes cannot be causally separated.")
    write(out / "PLAN.json", plan)
    verify_plan(out)
    C = core(out)
    for method in BASELINES:
        checked_rows(out, plan, method, C)
    write(out / "PREPARATION_AUDIT.json", dict(
        status="PASSED", gpu_used=False, baseline_predictions_rescored=60,
        input_and_baseline_hashes_verified=True, plan_sha256=sha(out / "PLAN.json")))
    write(out / "STATUS.json", dict(stage="WAITING_FOR_TRAINING", updated_unix=time.time()))
    return dict(stage="PREPARED", output=str(out), reused_predictions=60, pending_predictions=20)


class Adapter:
    def __init__(self, plan):
        import torch
        run = Path(plan["training_run"])
        os.environ["AFDM_LSTMP_ROOT"] = str(ROOT)
        os.environ["AFDM_LSTMP_CONFIG"] = str(run / CONFIG_REL)
        sys.path.insert(0, str(run / "source_code"))
        from experiments.lstmp_candidate_20261019 import common, data
        from experiments.lstmp_execution_v3_20261020.receiver import Receiver
        if common.OUT.resolve() != run.resolve():
            raise ValueError("Wrong frozen receiver/config imported")
        self.data, self.scale = data, plan["scale"]
        path = run / plan["new_checkpoint"]
        state = torch.load(path, map_location="cpu", weights_only=False, mmap=True)
        receipt = read(run / "checkpoints/depth_10/COMPLETE.json")
        if (state["depth"] != 10 or state["epoch"] != receipt["selected_epoch"] or
                state["manifest_sha256"] != plan["training_manifest_sha256"]):
            raise ValueError("Wrong selected checkpoint")
        self.model = Receiver()
        for _ in range(10):
            self.model.add_layer(None)
        self.model.load_state_dict(state["state"], strict=True)
        self.model.cuda().eval()
        self.model.use_checkpoint = False
        self.model.graphs_enabled = False
        self.networks, self.checkpoint_bytes = [self.model], path.stat().st_size

    def prepare(self, public):
        values = dict(y=public.observation, a=public.operator,
                      noise=public.noise_variance, rho=public.activity_prior)
        return self.data.prepare_public(values, self.scale, "cuda",
                                        phase_mode="known", noise_mode="known")[0]

    def infer(self, prepared):
        import torch
        before = self.model.score_evaluations
        outputs, diagnostics = self.model(prepared)
        final = outputs[-1]
        x = final["estimate"].cpu().numpy()
        estimate = (x[:, 0].astype(np.float64) + 1j * x[:, 1].astype(np.float64)) * self.scale
        probabilities = torch.sigmoid(final["logits"]).cpu().numpy()
        users = len(probabilities)
        record = dict(iterations=10, converged=None, stopping_reason="FIXED_10_LAYERS",
                      first_score_calls=self.model.score_evaluations-before, first_score_samples=10*users,
                      second_score_calls=0, second_score_samples=0,
                      classifier_calls=10, classifier_samples=10*users, diagnostics=diagnostics)
        return dict(estimate=estimate, probabilities=probabilities), record


def report(out, plan, C):
    paired = {method: checked_rows(out, plan, method, C) for method in METHODS}
    summaries = {}
    for method, rows in paired.items():
        s = dict(C.summarize(rows), **read(out / method / "OVERHEAD.json"))
        s.update(missed_detection_rate=s["misses"]/s["active"], false_alarm_rate=s["false_alarms"]/s["inactive"],
                 fixed_depth_scenes=sum(r["stopping_reason"].startswith("FIXED_") for r in rows))
        summaries[method] = s
    indices = np.random.default_rng(plan["bootstrap"]["seed"]).integers(0, 20, (10000, 20))
    boot = {}
    for method, rows in paired.items():
        sums = lambda key: np.asarray([r[key] for r in rows])[indices].sum(1)
        boot[method] = dict(pooled_nmse_db=10*np.log10(sums("error_energy")/sums("truth_energy")),
                            aer=(sums("misses")+sums("false_alarms"))/(sums("active")+sums("inactive")),
                            missed_detection_rate=sums("misses")/sums("active"),
                            false_alarm_rate=sums("false_alarms")/sums("inactive"))
    comparisons = {}
    for other in BASELINES:
        comparisons[other] = dict(
            new_minus_reference={key: summaries[NEW][key]-summaries[other][key] for key in boot[NEW]},
            paired_95_percentile={key: np.quantile(boot[NEW][key]-boot[other][key], [.025,.975]).tolist()
                                  for key in boot[NEW]},
            lower_nmse_scenes=sum(a["nmse"] < b["nmse"] for a,b in zip(paired[NEW],paired[other])),
            historical_reference_over_new_time=summaries[other]["mean_seconds"]/summaries[NEW]["mean_seconds"])
    training = read(Path(plan["training_run"]) / "COMPLETE.json")
    binding = read(out / "BINDING.json")
    result = dict(status="COMPLETE", condition=plan["condition"], methods=summaries,
                  comparisons=comparisons, binding=binding,
                  training_seconds=training["elapsed_seconds"], limitations=plan["limitations"])
    write(out / "SUMMARY.json", result)
    for filename, rows in (("summary.csv", [dict(method=m, **summaries[m]) for m in METHODS]),
                           ("per_scene.csv", [dict(method=m, **r) for m in METHODS for r in paired[m]])):
        fields = list(dict.fromkeys(k for row in rows for k in row))
        with (out / filename).open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    lines = ["# 十层与此前路线：相同20场景", "",
             "40用户、16导频、活动概率0.1、5 dB，已知相位和噪声；活动门限0.5。"
             "仅新增十层推断，五层、七层、旧三网络的预测和计时逐字节复用。",
             f"十层使用原验证规则选择的第{binding['selected_epoch']}轮权重。", "",
             "| 方法 | 信道NMSE/dB | AER | 漏检率 | 虚警率 | 漏检/虚警 | 平均秒/场景 |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for method, label in zip(METHODS, LABELS):
        s = summaries[method]
        lines.append(f"| {label} | {s['pooled_nmse_db']:.4f} | {s['aer']:.3%} | "
                     f"{s['missed_detection_rate']:.3%} | {s['false_alarm_rate']:.3%} | "
                     f"{s['misses']}/{s['false_alarms']} | {s['mean_seconds']:.4f} |")
    lines += ["", "差值及按物理场景配对重抽样的95%描述性区间见SUMMARY.json；负差值表示误差较低。",
              "这是已经看过的20场景、单工况比较，不是新的独立确认；不据此调阈值或挑选权重。"
              "历史计时来自其他测量时段，速度比仅作描述，不表示等精度速度优势。"
              "层数、目标和训练分布同时变化，不能把性能差异单独归因于层数。",
              "此次只报告已知相位和噪声条件，不能代表完整接收机在估计相位、估计噪声下的结论。"]
    (out / "REPORT.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 4, figsize=(15, 4.3), constrained_layout=True)
    for ax, key, title, scale in zip(axes,
            ("pooled_nmse_db", "aer", "missed_detection_rate", "mean_seconds"),
            ("Channel NMSE (dB)", "Activity error (%)", "Missed detection (%)", "Mean seconds / scene"),
            (1, 100, 100, 1)):
        bars = ax.bar(("V3 ten", "Prior seven", "Prior five", "Legacy"),
                      [summaries[m][key]*scale for m in METHODS],
                      color=("#227C9D", "#65A879", "#9B80B4", "#ED8B3A"))
        ax.bar_label(bars, fmt="%.3f", padding=3, fontsize=8)
        ax.set_title(title, fontsize=10)
        ax.tick_params(axis="x", labelrotation=25)
        ax.margins(y=.25)
        if key == "mean_seconds":
            ax.set_yscale("log")
        ax.grid(axis="y", alpha=.2)
        ax.set_axisbelow(True)
    fig.suptitle("Same 20 revealed scenes | K40 / Q16 / p0.1 / 5 dB | Known phase and noise\n"
                 "Reference predictions and timings reused; historical timing ratios are descriptive", fontsize=11)
    fig.savefig(out / "comparison.png", dpi=180)
    fig.savefig(out / "comparison.pdf")
    plt.close(fig)
    write(out / "RESULT_AUDIT.json", dict(
        status="PASSED", checked_unix=time.time(), predictions_rescored=80,
        plan_sha256=sha(out / "PLAN.json"), summary_sha256=sha(out / "SUMMARY.json"),
        all_twenty_retained=True, threshold=.5, selected_before_test=True))
    write(out / "COMPLETE.json", dict(status="COMPLETE", completed_unix=time.time(),
                                     plan_sha256=sha(out / "PLAN.json"), summary_sha256=sha(out / "SUMMARY.json"),
                                     audit_sha256=sha(out / "RESULT_AUDIT.json"),
                                     scene_counts=dict.fromkeys(METHODS, 20)))


def run(out):
    plan = verify_plan(out)
    ready, stage = readiness(Path(plan["training_run"]))
    if not ready:
        return dict(stage=stage, evaluation_started=False)
    if (out / "COMPLETE.json").exists():
        return dict(stage="ALREADY_COMPLETE", evaluation_started=False)
    check = subprocess.run(["nvidia-smi", "--query-compute-apps=pid",
                            "--format=csv,noheader,nounits"], capture_output=True, text=True, check=True)
    pids = [int(x.strip()) for x in check.stdout.splitlines() if x.strip().isdigit()]
    if any(pid != os.getpid() for pid in pids):
        return dict(stage="WAITING_FOR_GPU", active_pids=pids, evaluation_started=False)
    lock = out / "RUNNING.lock"
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(descriptor, str(os.getpid()).encode())
    os.close(descriptor)
    try:
        C = core(out)
        import torch
        from threadpoolctl import threadpool_limits
        torch.set_num_threads(plan["cpu_threads"])
        threadpool_limits(plan["cpu_threads"])
        torch.backends.cuda.matmul.allow_tf32 = plan["allow_tf32"]
        torch.backends.cudnn.allow_tf32 = plan["allow_tf32"]
        torch.backends.cudnn.benchmark = True
        training_run = Path(plan["training_run"])
        receipt = read(training_run / "checkpoints/depth_10/COMPLETE.json")
        digest = sha(training_run / plan["new_checkpoint"])
        if digest != receipt["best_sha256"] or digest != read(training_run / "COMPLETE.json")["selected_sha256"]:
            raise ValueError("Selected checkpoint digest mismatch")
        identity = dict(plan_sha256=sha(out / "PLAN.json"), selected_checkpoint_sha256=digest,
                        selected_epoch=receipt["selected_epoch"],
                        training_complete_sha256=sha(training_run / "COMPLETE.json"),
                        torch=torch.__version__, cuda=torch.version.cuda, cudnn=torch.backends.cudnn.version(),
                        gpu=torch.cuda.get_device_name(), python=platform.python_version())
        if (out / "BINDING.json").exists() and read(out / "BINDING.json") != identity:
            raise ValueError("Weights/environment changed on comparison resume")
        write(out / "BINDING.json", identity)
        write(out / "STATUS.json", dict(stage="LOADING", pid=os.getpid(), updated_unix=time.time()))
        started = time.perf_counter()
        adapter = Adapter(plan)
        from afdm_jadcedd.system.observation import load_input
        torch.cuda.synchronize()
        overhead = dict(C.model_size(adapter.networks), checkpoint_file_bytes=adapter.checkpoint_bytes,
                        model_load_seconds=time.perf_counter()-started)
        folder = out / NEW
        folder.mkdir(exist_ok=True)
        C.timed_inference(adapter, load_input(out / "warmup/input.npz"))
        torch.cuda.empty_cache()
        if not (folder / "OVERHEAD.json").exists():
            write(folder / "OVERHEAD.json", overhead)
        for case in plan["cases"]:
            i = case["index"]
            if (folder / f"{i:03d}.json").exists():
                continue  # All retained rows are independently checked before completion.
            write(out / "STATUS.json", dict(stage="EVALUATING", pid=os.getpid(), scene=i+1,
                                             total=20, updated_unix=time.time()))
            arrays, record, times = C.timed_inference(adapter, load_input(out / "cases" / f"{i:03d}/input.npz"))
            with np.load(out / "cases" / f"{i:03d}/truth.npz", allow_pickle=False) as truth:
                scores = C.score_arrays(arrays["estimate"], arrays["probabilities"], truth["channel"], truth["activity"])
            np.savez_compressed(folder / f"{i:03d}.npz", **arrays)
            write(folder / f"{i:03d}_trace.json", record)
            write(folder / f"{i:03d}.json", dict(status="COMPLETE", case_index=i, seed=case["seed"],
                  input_sha256=case["input_sha256"], prediction_sha256=sha(folder / f"{i:03d}.npz"),
                  **scores, **times, **{k:v for k,v in record.items() if k != "diagnostics"}))
        del adapter
        torch.cuda.empty_cache()
        verify_plan(out)
        if sha(training_run / plan["new_checkpoint"]) != digest:
            raise ValueError("Checkpoint changed during evaluation")
        report(out, plan, C)
        write(out / "STATUS.json", dict(stage="COMPLETE", updated_unix=time.time()))
        return dict(stage="COMPLETE", output=str(out))
    except BaseException as error:
        write(out / f"FAILURE_{time.time_ns()}.json", dict(error=repr(error), traceback=traceback.format_exc()))
        write(out / "STATUS.json", dict(stage="FAILED", updated_unix=time.time(), error=repr(error)))
        raise
    finally:
        lock.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--prepare", action="store_true")
    modes.add_argument("--inspect", action="store_true")
    modes.add_argument("--run", action="store_true")
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    if args.prepare:
        result = prepare(args.output)
    elif args.run:
        result = run(args.output)
    else:
        plan = verify_plan(args.output)
        ready, stage = readiness(Path(plan["training_run"]))
        result = dict(ready=ready, stage=stage, comparison_status=read(args.output / "STATUS.json"))
    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
