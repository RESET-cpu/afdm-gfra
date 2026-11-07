"""User-requested interim depth-six comparison on the original twenty scenes.

CPU only, two threads, below-normal priority. The pending depth-ten comparison
and the active training run are read-only inputs to this separate evaluation.
"""
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "2"
import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import shutil
import sys
import time
import traceback
sys.dont_write_bytecode = True
import numpy as np

ROOT = Path(r"C:\Users\25911\Desktop\afdm-gfra")
RUN = Path(r"D:\afdm-gfra-cpu\runs\lstmp_conditional_bce_v3_depth10_fast_20261020")
REFERENCE = ROOT / "results/lstmp_v3_depth10_previous20_20261020"
REFERENCE_PLAN_SHA = "55d6ea14481c608ff873401e275d1cd3d2e9d589c450fbafd83d3f8fcad0e9a9"
OUT = ROOT / "results/lstmp_v3_depth6_previous20_cpu_20261021"
NEW = "v3_six_layer_cpu"
BASELINES = ("new_seven_layer", "frozen_five_layer", "legacy_50000_damping01")
METHODS = (NEW,) + BASELINES
LABELS = ("第三版六层（本次CPU）", "此前七层（历史GPU）", "此前五层（历史GPU）", "旧三网络（历史GPU）")
CONFIG_REL = "source_code/experiments/lstmp_execution_v3_20261020/config.json"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temp.replace(path)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def core():
    spec = importlib.util.spec_from_file_location("previous20_scoring", OUT / "source/paired_core.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def selected_depth():
    folder = RUN / "checkpoints/depth_6"
    receipt, history = read(folder / "COMPLETE.json"), read(folder / "history.json")
    if receipt["depth"] != 6 or receipt["updates"] != 14250:
        raise ValueError("Depth six has not completed its fixed training budget")
    if [r["epoch"] for r in history] != [0, 1, 2, 3] or any(r["scenes"] != 1900 for r in history):
        raise ValueError("Depth-six validation is incomplete")
    chosen = min(history, key=lambda r: (r["selection_loss"], r["epoch"]))["epoch"]
    if chosen != receipt["selected_epoch"] or sha(folder / "best.pt") != receipt["best_sha256"]:
        raise ValueError("Depth-six selection/weight does not match its completion record")
    return receipt


def verify(plan):
    if sha(REFERENCE / "PLAN.json") != REFERENCE_PLAN_SHA:
        raise ValueError("Pending depth-ten frozen plan changed")
    for name, digest in plan["source_sha256"].items():
        if sha(OUT / "source" / name) != digest:
            raise ValueError("Evaluation source changed: " + name)
    for path, digest in plan["model_hashes"].items():
        if sha(path) != digest:
            raise ValueError("Frozen model/source changed: " + path)
    for name, digest in plan["reused_asset_sha256"].items():
        if sha(OUT / name) != digest or sha(REFERENCE / name) != digest:
            raise ValueError("Original input/reference prediction changed: " + name)
    for name, digest in plan["previous_reference_sha256"].items():
        if sha(Path(plan["previous_comparison"]) / name) != digest:
            raise ValueError("Historical reference record changed: " + name)
    receipt = selected_depth()
    if receipt["selected_epoch"] != plan["selected_epoch"]:
        raise ValueError("Selection changed")


def checked_rows(plan, method, C):
    rows = []
    for case in plan["cases"]:
        i = case["index"]
        folder = OUT / method
        row = read(folder / f"{i:03d}.json")
        if (row["status"] != "COMPLETE" or row["case_index"] != i or row["seed"] != case["seed"]
                or row["input_sha256"] != case["input_sha256"]
                or sha(folder / f"{i:03d}.npz") != row["prediction_sha256"]):
            raise ValueError(f"Invalid prediction binding: {method}/{i}")
        with np.load(folder / f"{i:03d}.npz", allow_pickle=False) as p:
            with np.load(OUT / "cases" / f"{i:03d}/truth.npz", allow_pickle=False) as t:
                scores = C.score_arrays(p["estimate"], p["probabilities"], t["channel"], t["activity"], threshold=.5)
        for key, value in scores.items():
            if not np.isclose(value, row[key], rtol=1e-12, atol=1e-12):
                raise ValueError(f"Rescoring mismatch: {method}/{i}/{key}")
        if not np.isclose(row["total_seconds"], row["preparation_seconds"] + row["inference_seconds"], rtol=1e-10, atol=1e-10):
            raise ValueError("Invalid timing sum")
        if method == NEW:
            trace = read(folder / f"{i:03d}_trace.json")
            if (row["iterations"] != 6 or row["first_score_calls"] != 6 or row["second_score_calls"] != 0
                    or row["stopping_reason"] != "FIXED_6_LAYERS" or len(trace["diagnostics"]) != 6):
                raise ValueError("Incorrect six-layer forward")
        rows.append(row)
    return rows


def prepare():
    if OUT.exists():
        raise FileExistsError(OUT)
    if sha(REFERENCE / "PLAN.json") != REFERENCE_PLAN_SHA:
        raise ValueError("Unexpected reference plan")
    original = read(REFERENCE / "PLAN.json")
    audit = read(REFERENCE / "PREPARATION_AUDIT.json")
    if audit["status"] != "PASSED" or audit["plan_sha256"] != REFERENCE_PLAN_SHA:
        raise ValueError("Unverified reference assets")
    if [c["seed"] for c in original["cases"]] != list(range(202610208700001, 202610208700021)):
        raise ValueError("Wrong twenty scenes")
    receipt = selected_depth()
    model_hashes = dict(original["training_source_hashes"])
    for p in (RUN / "MANIFEST.json", RUN / "checkpoints/depth_6/best.pt",
              RUN / "checkpoints/depth_6/COMPLETE.json", RUN / "checkpoints/depth_6/BEST.json",
              RUN / "checkpoints/depth_6/history.json"):
        model_hashes[str(p)] = sha(p)
    OUT.mkdir()
    (OUT / "source").mkdir()
    shutil.copy2(__file__, OUT / "source" / Path(__file__).name)
    shutil.copy2(REFERENCE / "source/paired_core.py", OUT / "source/paired_core.py")
    for name in ("cases", "warmup") + BASELINES:
        shutil.copytree(REFERENCE / name, OUT / name)
    plan = dict(schema="lstmp-v3-depth6-previous20-cpu-v1", created_unix=time.time(),
        authorization="2026-10-21 user requested running the same twenty scenes now; use completed selected depth six on CPU while training continues.",
        root=str(ROOT), training_run=str(RUN), depth=6, selected_epoch=receipt["selected_epoch"],
        checkpoint=str(RUN / "checkpoints/depth_6/best.pt"), checkpoint_sha256=receipt["best_sha256"],
        training_manifest_sha256=original["training_manifest_sha256"], model_hashes=model_hashes,
        reference_preparation=str(REFERENCE), reference_plan_sha256=REFERENCE_PLAN_SHA,
        previous_comparison=original["previous_comparison"], previous_reference_sha256=original["previous_reference_sha256"],
        reused_asset_sha256=original["reused_asset_sha256"],
        source_sha256={p.name: sha(p) for p in (OUT / "source").iterdir()},
        cases=original["cases"], warmup=original["warmup"], scene_count=20, condition=original["condition"],
        methods=list(METHODS), scale=original["scale"], activity_threshold=.5,
        phase_mode="known", noise_mode="known", device="cpu", cpu_threads=2,
        selection="Depth-six best selected by the existing 1900-scene validation selection_loss, before this evaluation; no selection on these twenty scenes.",
        bootstrap=dict(samples=10000, seed=2026102197, unit="paired physical scene", interpretation="Descriptive percentile intervals on previously revealed scenes."),
        timing="New six-layer receiver: two-thread CPU, one independent warmup, input preparation plus forward and CPU output conversion, excluding disk I/O/scoring/model loading. References: historical RTX 5080 CUDA/TF32 measurements. No cross-device speed ratio or speed claim.",
        limitations="Previously revealed twenty scenes at one K40/Q16/p0.1/5dB known-phase/noise condition. New inference is CPU float32; reference predictions used historical CUDA with TF32 enabled. Backend numerical differences are not isolated. This is an interim six-layer comparison, not the future ten-layer result, not a Q8 regression test and not independent confirmation. Depth, training objective and distribution changed together.")
    write(OUT / "PLAN.json", plan)
    verify(plan)
    C = core()
    for method in BASELINES:
        checked_rows(plan, method, C)
    write(OUT / "PREPARATION_AUDIT.json", dict(status="PASSED", plan_sha256=sha(OUT / "PLAN.json"),
          baseline_predictions_rescored=60, gpu_used=False, all_reference_bytes_unchanged=True))
    write(OUT / "STATUS.json", dict(stage="PREPARED", updated_unix=time.time()))
    print(json.dumps(dict(stage="PREPARED", output=str(OUT), depth=6, selected_epoch=receipt["selected_epoch"])), flush=True)


def aggregate(rows, C):
    result = C.summarize(rows)
    result.update(missed_detection_rate=result["misses"] / result["active"],
                  false_alarm_rate=result["false_alarms"] / result["inactive"],
                  fixed_depth_scenes=sum(r["stopping_reason"].startswith("FIXED_") for r in rows))
    return result


def report(plan, C):
    paired = {m: checked_rows(plan, m, C) for m in METHODS}
    summary = {m: dict(aggregate(paired[m], C), **read(OUT / m / "OVERHEAD.json"),
                       device="cpu" if m == NEW else "historical RTX 5080 CUDA") for m in METHODS}
    # CPU uses no CUDA allocations. Null makes the unavailable GPU comparison explicit.
    summary[NEW]["peak_allocated_bytes"] = None
    summary[NEW]["peak_reserved_bytes"] = None
    indices = np.random.default_rng(plan["bootstrap"]["seed"]).integers(0, 20, (10000, 20))
    boot = {}
    for m, rows in paired.items():
        sums = lambda k: np.asarray([r[k] for r in rows])[indices].sum(1)
        boot[m] = dict(pooled_nmse_db=10 * np.log10(sums("error_energy") / sums("truth_energy")),
            aer=(sums("misses") + sums("false_alarms")) / (sums("active") + sums("inactive")),
            missed_detection_rate=sums("misses") / sums("active"), false_alarm_rate=sums("false_alarms") / sums("inactive"))
    comparisons = {}
    for ref in BASELINES:
        differences = []
        for a, b in zip(paired[NEW], paired[ref]):
            differences.append(dict(case_index=a["case_index"], seed=a["seed"],
                nmse_db_delta=float(10 * np.log10(a["nmse"] / b["nmse"])),
                activity_error_delta=a["misses"] + a["false_alarms"] - b["misses"] - b["false_alarms"],
                misses_delta=a["misses"] - b["misses"], false_alarms_delta=a["false_alarms"] - b["false_alarms"]))
        comparisons[ref] = dict(new_minus_reference={k: summary[NEW][k] - summary[ref][k] for k in boot[NEW]},
            paired_95_percentile={k: np.quantile(boot[NEW][k] - boot[ref][k], [.025, .975]).tolist() for k in boot[NEW]},
            lower_nmse_scenes=sum(x["nmse_db_delta"] < 0 for x in differences),
            higher_nmse_scenes=sum(x["nmse_db_delta"] > 0 for x in differences), per_scene_differences=differences)
    boundary = {}
    for m in METHODS:
        close = []
        for c in plan["cases"]:
            with np.load(OUT / m / f'{c["index"]:03d}.npz', allow_pickle=False) as z:
                for u in np.flatnonzero(np.abs(z["probabilities"] - .5) <= .05):
                    close.append(dict(case_index=c["index"], user_index=int(u), probability=float(z["probabilities"][u])))
        boundary[m] = close
    write(OUT / "SUMMARY.json", dict(status="COMPLETE", condition=plan["condition"], methods=summary,
        comparisons=comparisons, binding=read(OUT / "BINDING.json"), probabilities_within_005_of_threshold=boundary,
        limitations=plan["limitations"], timing=plan["timing"]))
    for name, rows in (("summary.csv", [dict(method=m, **summary[m]) for m in METHODS]),
                       ("per_scene.csv", [dict(method=m, **r) for m in METHODS for r in paired[m]])):
        fields = list(dict.fromkeys(k for row in rows for k in row))
        with (OUT / name).open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fields)
            writer.writeheader()
            writer.writerows(rows)
    lines = ["第三版六层与此前路线：相同20场景的阶段性比较", "",
        "40用户、16导频、活动概率0.1、5 dB；已知相位和噪声；活动门限0.5。",
        "仅新增六层CPU两线程推断；此前七层、五层和旧三网络的输入、预测、逐场景记录及历史计时按字节复用。",
        f"六层使用既定1900场景验证规则选中的epoch {plan['selected_epoch']}；权重SHA256：{plan['checkpoint_sha256']}。", "",
        "方法 | 信道NMSE/dB | AER | 漏检率 | 虚警率 | 漏检/虚警 | 平均秒/场景（设备不同，不比较速度）"]
    for m, label in zip(METHODS, LABELS):
        s = summary[m]
        lines.append(f"{label} | {s['pooled_nmse_db']:.4f} | {s['aer']:.3%} | {s['missed_detection_rate']:.3%} | {s['false_alarm_rate']:.3%} | {s['misses']}/{s['false_alarms']} | {s['mean_seconds']:.4f}")
    lines += ["", "差值均为本次六层减参考方法，负值表示误差下降；10000次按物理场景配对重抽样，95%百分位区间仅作描述。"]
    for ref, label in zip(BASELINES, LABELS[1:]):
        c = comparisons[ref]
        lines.append(f"相对{label}：NMSE改善场景{c['lower_nmse_scenes']}/20，变差{c['higher_nmse_scenes']}/20。")
        for k in boot[NEW]:
            scale = 1 if k == "pooled_nmse_db" else 100
            unit = "dB" if scale == 1 else "百分点"
            lo, hi = c["paired_95_percentile"][k]
            lines.append(f"  {k}: {c['new_minus_reference'][k]*scale:+.4f} {unit}，区间[{lo*scale:+.4f}, {hi*scale:+.4f}]")
    lines += ["", "这20个场景共84个活跃用户和716个非活跃用户。零检测错误只表示本次样本中未观察到错误，不表示总体错误率为零。",
        "新结果为CPU float32，参考结果来自历史CUDA/TF32，未分离后端数值差异；接近门限的概率记录于SUMMARY.json。",
        "CPU耗时与历史GPU耗时不构成速度或等精度加速比较；CPU进程峰值内存与CUDA分配显存也不直接比较。",
        "这是已经揭示的单工况20场景，非新的独立确认，也不覆盖8导频退化场景。",
        "层数、损失及训练分布同时变化，不能把差异单独归因于层数。未据此选择模型或修改门限。",
        "当前十层训练及其冻结后续比较保持原计划；本报告仅记录完成六层时的阶段结果。"]
    (OUT / "REPORT.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 7.5), constrained_layout=True)
    for ax, key, title, multiplier in zip(axes.flat,
            ("pooled_nmse_db", "aer", "missed_detection_rate", "false_alarm_rate"),
            ("Channel NMSE (dB)", "Activity error (%)", "Missed detection (%)", "False alarm (%)"), (1, 100, 100, 100)):
        bars = ax.bar(("V3 six / CPU", "Prior seven", "Prior five", "Legacy"),
            [summary[m][key] * multiplier for m in METHODS], color=("#227C9D", "#65A879", "#9B80B4", "#ED8B3A"))
        ax.bar_label(bars, fmt="%.3f", padding=3, fontsize=9)
        ax.set_title(title)
        ax.margins(y=.25)
        ax.grid(axis="y", alpha=.2)
        ax.set_axisbelow(True)
    fig.suptitle("Same 20 revealed scenes | K40 / Q16 / p0.1 / 5 dB | Known phase and noise\n"
                 "V3 six: CPU float32; references: saved CUDA/TF32 predictions | No speed comparison", fontsize=11)
    fig.savefig(OUT / "comparison.png", dpi=180)
    fig.savefig(OUT / "comparison.pdf")
    plt.close(fig)
    write(OUT / "RESULT_AUDIT.json", dict(status="PASSED", checked_unix=time.time(), predictions_rescored=80,
        scene_counts=dict.fromkeys(METHODS, 20), original_inputs_and_reference_predictions_byte_identical=True,
        selected_weight_sha256=plan["checkpoint_sha256"], selected_before_test=True, gpu_used_for_new_inference=False,
        threshold=.5, all_twenty_retained=True, bootstrap_samples=10000,
        frozen_depth10_plan_unchanged=sha(REFERENCE / "PLAN.json") == REFERENCE_PLAN_SHA,
        plan_sha256=sha(OUT / "PLAN.json"), summary_sha256=sha(OUT / "SUMMARY.json")))
    write(OUT / "COMPLETE.json", dict(status="COMPLETE", completed_unix=time.time(),
        plan_sha256=sha(OUT / "PLAN.json"), summary_sha256=sha(OUT / "SUMMARY.json"),
        audit_sha256=sha(OUT / "RESULT_AUDIT.json"), scene_counts=dict.fromkeys(METHODS, 20)))


def run():
    plan = read(OUT / "PLAN.json")
    verify(plan)
    if (OUT / "COMPLETE.json").exists():
        print(json.dumps(dict(stage="ALREADY_COMPLETE")), flush=True)
        return
    lock = OUT / "RUNNING.lock"
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, str(os.getpid()).encode())
    os.close(fd)
    try:
        import psutil
        process = psutil.Process()
        if os.name == "nt":
            process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        import torch
        from threadpoolctl import threadpool_limits
        torch.set_num_threads(2)
        torch.set_num_interop_threads(1)
        threadpool_limits(2)
        os.environ["AFDM_LSTMP_ROOT"] = str(ROOT)
        os.environ["AFDM_LSTMP_CONFIG"] = str(RUN / CONFIG_REL)
        sys.path.insert(0, str(RUN / "source_code"))
        from experiments.lstmp_candidate_20261019 import common, data
        from experiments.lstmp_execution_v3_20261020.receiver import Receiver
        if common.OUT.resolve() != RUN.resolve():
            raise ValueError("Wrong frozen receiver import")
        C = core()
        binding = dict(plan_sha256=sha(OUT / "PLAN.json"), selected_checkpoint_sha256=plan["checkpoint_sha256"],
            selected_epoch=plan["selected_epoch"], depth=6, device="cpu", cpu_threads=2,
            torch=torch.__version__, python=platform.python_version(), cuda_visible_devices=os.environ["CUDA_VISIBLE_DEVICES"],
            checkpoint_complete_sha256=sha(RUN / "checkpoints/depth_6/COMPLETE.json"))
        if (OUT / "BINDING.json").exists() and read(OUT / "BINDING.json") != binding:
            raise ValueError("Binding changed")
        write(OUT / "BINDING.json", binding)
        write(OUT / "STATUS.json", dict(stage="LOADING_CPU", pid=os.getpid(), updated_unix=time.time()))
        started = time.perf_counter()
        state = torch.load(plan["checkpoint"], map_location="cpu", weights_only=False, mmap=True)
        if state["depth"] != 6 or state["epoch"] != plan["selected_epoch"] or state["manifest_sha256"] != plan["training_manifest_sha256"]:
            raise ValueError("Wrong checkpoint state")
        model = Receiver()
        for _ in range(6):
            model.add_layer(None)
        model.load_state_dict(state["state"], strict=True)
        del state
        model.eval()
        model.use_checkpoint = False
        model.graphs_enabled = False
        if any(p.device.type != "cpu" for p in model.parameters()):
            raise ValueError("Non-CPU parameter")
        folder = OUT / NEW
        folder.mkdir(exist_ok=True)
        overhead = dict(C.model_size([model]), checkpoint_file_bytes=Path(plan["checkpoint"]).stat().st_size,
                        model_load_seconds=time.perf_counter() - started)

        def infer(input_path):
            with np.load(input_path, allow_pickle=False) as z:
                public_input = dict(y=z["observation"], a=z["operator"], noise=z["noise_variance"], rho=z["activity_prior"])
            with torch.no_grad():
                before = time.perf_counter()
                public, _ = data.prepare_public(public_input, plan["scale"], "cpu", phase_mode="known", noise_mode="known")
                ready = time.perf_counter()
                calls = model.score_evaluations
                outputs, diagnostics = model(public)
                final = outputs[-1]
                def physical(t):
                    x = t.numpy()
                    return (x[:, 0].astype(np.float64) + 1j * x[:, 1].astype(np.float64)) * plan["scale"]
                arrays = dict(estimate=physical(final["estimate"]), conditional=physical(final["conditional"]),
                              probabilities=torch.sigmoid(final["logits"]).numpy())
                end = time.perf_counter()
            users = len(arrays["probabilities"])
            record = dict(iterations=6, converged=None, stopping_reason="FIXED_6_LAYERS",
                first_score_calls=model.score_evaluations - calls, first_score_samples=6 * users,
                second_score_calls=0, second_score_samples=0, classifier_calls=6, classifier_samples=6 * users,
                diagnostics=diagnostics)
            times = dict(preparation_seconds=ready - before, inference_seconds=end - ready, total_seconds=end - before,
                         peak_allocated_bytes=0, peak_reserved_bytes=0)
            return arrays, record, times

        infer(OUT / "warmup/input.npz")
        if not (folder / "OVERHEAD.json").exists():
            write(folder / "OVERHEAD.json", overhead)
        for case in plan["cases"]:
            i = case["index"]
            if (folder / f"{i:03d}.json").exists():
                continue
            write(OUT / "STATUS.json", dict(stage="EVALUATING_CPU", pid=os.getpid(), scene=i + 1, total=20, updated_unix=time.time()))
            arrays, record, times = infer(OUT / "cases" / f"{i:03d}/input.npz")
            with np.load(OUT / "cases" / f"{i:03d}/truth.npz", allow_pickle=False) as truth:
                scores = C.score_arrays(arrays["estimate"], arrays["probabilities"], truth["channel"], truth["activity"], threshold=.5)
            np.savez_compressed(folder / f"{i:03d}.npz", **arrays)
            write(folder / f"{i:03d}_trace.json", record)
            write(folder / f"{i:03d}.json", dict(status="COMPLETE", case_index=i, seed=case["seed"],
                input_sha256=case["input_sha256"], prediction_sha256=sha(folder / f"{i:03d}.npz"),
                **scores, **times, **{k: v for k, v in record.items() if k != "diagnostics"}))
            print(json.dumps(dict(scene=i + 1, total=20, nmse_db=10 * np.log10(scores["nmse"]),
                misses=scores["misses"], false_alarms=scores["false_alarms"], seconds=times["total_seconds"])), flush=True)
        memory = process.memory_info()
        retained = read(folder / "OVERHEAD.json")
        retained["cpu_process_peak_working_set_bytes"] = getattr(memory, "peak_wset", memory.rss)
        retained["cpu_memory_scope"] = "Process peak working set includes imports, model loading, warmup and scoring; not comparable to CUDA allocated memory."
        write(folder / "OVERHEAD.json", retained)
        verify(plan)
        report(plan, C)
        write(OUT / "STATUS.json", dict(stage="COMPLETE", updated_unix=time.time(), gpu_used=False))
        print(json.dumps(dict(stage="COMPLETE", output=str(OUT))), flush=True)
    except BaseException as error:
        write(OUT / f"FAILURE_{time.time_ns()}.json", dict(error=repr(error), traceback=traceback.format_exc()))
        write(OUT / "STATUS.json", dict(stage="FAILED", updated_unix=time.time(), error=repr(error)))
        raise
    finally:
        lock.unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--prepare", action="store_true")
    modes.add_argument("--run", action="store_true")
    args = parser.parse_args()
    prepare() if args.prepare else run()
