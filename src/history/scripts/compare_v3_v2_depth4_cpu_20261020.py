"""Paired CPU comparison of the two completed depth-four selections.

Only previously saved endpoint scenes are used. CUDA is hidden in this process;
the ongoing progressive training and its checkpoints are never modified.
"""
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "2"
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import time
import traceback
import numpy as np

ROOT = Path(r"C:\Users\25911\Desktop\afdm-gfra")
OUT = ROOT / "results/v3_vs_v2_depth4_paired20_cpu_20261020"
OLD = ROOT / "results/planned_edges_v2_depth4_paired10_20261020"
RUNS = dict(
    v2=Path(r"D:\afdm-gfra-cpu\runs\lstmp_conditional_bce_v2_20261020"),
    v3=Path(r"D:\afdm-gfra-cpu\runs\lstmp_conditional_bce_v3_depth10_fast_20261020"))
PACKAGES = dict(v2="lstmp_training_v2_20261020", v3="lstmp_execution_v3_20261020")
GROUPS = ("k100_q16", "k40_q8")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    temp.replace(path)


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def scoring():
    spec = importlib.util.spec_from_file_location("frozen_scoring", OUT / "source/paired_core.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.score_arrays


def verify(plan, method=None):
    for name, digest in plan["source_sha256"].items():
        if sha(OUT / "source" / name) != digest:
            raise ValueError("Comparison source changed: "+name)
    for case in plan["cases"]:
        for name, digest in case["files"].items():
            if sha(Path(case["folder"]) / name) != digest:
                raise ValueError("Paired input changed: "+name)
    for name in ([method] if method else RUNS):
        bound = plan["models"][name]
        for path, digest in bound["hashes"].items():
            if sha(path) != digest:
                raise ValueError("Selected model/source changed: "+path)


def prepare():
    if OUT.exists():
        raise FileExistsError(OUT)
    old = read(OLD / "PLAN.json")
    if read(OLD / "AUDIT.json")["status"] != "PASSED" or len(old["cases"]) != 20:
        raise ValueError("Unverified reference scenes")
    models = {}
    for name, run in RUNS.items():
        checkpoint = run / "checkpoints/depth_4/best.pt"
        receipt_path = checkpoint.parent / "COMPLETE.json"
        receipt = read(receipt_path)
        if receipt["selected_epoch"] != 3 or receipt["depth"] != 4:
            raise ValueError("Unexpected completed depth-four selection")
        if receipt["updates"] != (14400 if name == "v2" else 14250):
            raise ValueError("Incomplete depth-four training")
        if sha(checkpoint) != receipt["best_sha256"]:
            raise ValueError("Checkpoint digest mismatch")
        manifest = read(run / "MANIFEST.json")
        hashes = dict(manifest["snapshot_hashes"])
        hashes.update({str(p): sha(p) for p in (checkpoint, receipt_path, run / "MANIFEST.json")})
        models[name] = dict(run=str(run), checkpoint=str(checkpoint),
                            selected_epoch=3, depth=4, hashes=hashes,
                            config=str(run / "source_code/experiments" / PACKAGES[name] / "config.json"))
    OUT.mkdir()
    (OUT / "source").mkdir()
    shutil.copy2(__file__, OUT / "source" / Path(__file__).name)
    shutil.copy2(ROOT / "results/lstmp_depth7_reuse_previous20_20261020/source/paired_core.py",
                 OUT / "source/paired_core.py")
    plan = dict(created_unix=time.time(), cases=old["cases"], models=models,
                scale=old["scale"], device="cpu", cpu_threads=2, threshold=.5, depth=4,
                phase_mode="estimated", noise_mode="estimated", snr_db=0, activity_probability=.1,
                source_sha256={p.name: sha(p) for p in (OUT / "source").iterdir()},
                previous_gpu_reference=str(OLD),
                previous_plan_sha256=sha(OLD / "PLAN.json"),
                scoring="Pooled effective-channel error/truth energy; natural user-count denominators.",
                input_policy="Exact previously cached phase and noise estimates; no truth in inference.",
                inference_scope="Both versions recomputed on the same CPU backend; no speed comparison.",
                selection="Both existing depth-four epoch-three validation selections; no selection on these scenes.",
                limitations="Two previously revealed endpoint conditions, ten physical scenes each; descriptive pairing only.")
    write(OUT / "PLAN.json", plan)
    verify(plan)
    write(OUT / "STATUS.json", dict(stage="PREPARED", gpu_used=False))
    print(json.dumps(dict(stage="PREPARED", output=str(OUT))), flush=True)


def evaluate(method):
    plan = read(OUT / "PLAN.json")
    verify(plan, method)
    folder = OUT / method
    if (folder / "COMPLETE.json").exists():
        print(json.dumps(dict(stage="ALREADY_COMPLETE", method=method)), flush=True)
        return
    folder.mkdir(exist_ok=True)
    lock = folder / "RUNNING.lock"
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(descriptor, str(os.getpid()).encode())
    os.close(descriptor)
    try:
        import psutil
        if os.name == "nt":
            psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        bound = plan["models"][method]
        os.environ["AFDM_LSTMP_ROOT"] = str(ROOT)
        os.environ["AFDM_LSTMP_CONFIG"] = bound["config"]
        sys.path.insert(0, str(Path(bound["run"]) / "source_code"))
        import torch
        from threadpoolctl import threadpool_limits
        torch.set_num_threads(2)
        torch.set_num_interop_threads(1)
        threadpool_limits(2)
        from experiments.lstmp_candidate_20261019 import common, data
        receiver = importlib.import_module("experiments."+PACKAGES[method]+".receiver")
        if common.OUT.resolve() != Path(bound["run"]).resolve():
            raise ValueError("Wrong receiver source/config imported")
        state = torch.load(bound["checkpoint"], map_location="cpu", weights_only=False, mmap=True)
        if state["depth"] != 4 or state["epoch"] != 3:
            raise ValueError("Wrong checkpoint depth/epoch")
        model = receiver.Receiver()
        for _ in range(4):
            model.add_layer(None)
        model.load_state_dict(state["state"], strict=True)
        del state
        model.eval()
        model.use_checkpoint = False
        if hasattr(model, "graphs_enabled"):
            model.graphs_enabled = False
        score = scoring()
        write(folder / "EXECUTION.json", dict(device="cpu", cuda_visible_devices=os.environ["CUDA_VISIBLE_DEVICES"],
                cpu_threads=2, torch=torch.__version__, pid=os.getpid(), checkpoint=bound["checkpoint"]))
        for number, case in enumerate(plan["cases"], 1):
            stem = folder / case["group"] / f'{case["index"]:03d}'
            stem.parent.mkdir(parents=True, exist_ok=True)
            if stem.with_suffix(".json").exists():
                continue
            write(OUT / "STATUS.json", dict(stage="EVALUATING_CPU", method=method,
                    scene=number, total=20, pid=os.getpid(), updated_unix=time.time()))
            before = time.perf_counter()
            with np.load(Path(case["folder"]) / "input.npz", allow_pickle=False) as z:
                inputs = {k: z[k] for k in z.files}
            with torch.no_grad():
                public, _ = data.prepare_public(dict(y=inputs["observation"], a=inputs["operator"],
                    noise=inputs["noise_variance"], rho=inputs["activity_prior"]),
                    plan["scale"], "cpu", phase_mode="known", noise_mode="known")
                outputs, diagnostics = model(public)
                last = outputs[-1]
                def physical(x):
                    values = x.numpy()
                    return (values[:, 0].astype(np.float64) + 1j*values[:, 1].astype(np.float64))*plan["scale"]
                prediction = dict(estimate=physical(last["estimate"]),
                                  conditional=physical(last["conditional"]),
                                  probabilities=torch.sigmoid(last["logits"]).numpy())
            seconds = time.perf_counter()-before
            with np.load(Path(case["folder"]) / "truth.npz", allow_pickle=False) as truth:
                metrics = score(prediction["estimate"], prediction["probabilities"], truth["channel"], truth["activity"])
            np.savez_compressed(stem.with_suffix(".npz"), **prediction)
            write(stem.with_suffix(".trace.json"), dict(diagnostics=diagnostics, iterations=4))
            row = dict(status="COMPLETE", group=case["group"], index=case["index"], seed=case["seed"],
                       input_sha256=case["files"]["input.npz"], prediction_sha256=sha(stem.with_suffix(".npz")),
                       **metrics, elapsed_seconds=seconds)
            write(stem.with_suffix(".json"), row)
            print(json.dumps(dict(method=method, scene=number, group=case["group"], nmse_db=10*np.log10(row["nmse"]),
                                  misses=row["misses"], false_alarms=row["false_alarms"], seconds=seconds)), flush=True)
            del outputs, last, public, prediction, inputs
        verify(plan, method)
        write(folder / "COMPLETE.json", dict(status="COMPLETE", scenes=20, gpu_used=False))
    except BaseException as error:
        write(folder / f"FAILURE_{time.time_ns()}.json", dict(error=repr(error), traceback=traceback.format_exc()))
        raise
    finally:
        lock.unlink(missing_ok=True)


def aggregate(rows):
    total = lambda key: sum(r[key] for r in rows)
    return dict(scenes=len(rows), pooled_nmse_db=10*np.log10(total("error_energy")/total("truth_energy")),
                aer=(total("misses")+total("false_alarms"))/(total("active")+total("inactive")),
                missed_detection_rate=total("misses")/total("active"),
                false_alarm_rate=total("false_alarms")/total("inactive"),
                misses=total("misses"), false_alarms=total("false_alarms"),
                active=total("active"), inactive=total("inactive"))


def report():
    plan = read(OUT / "PLAN.json")
    verify(plan)
    if sha(OLD / "PLAN.json") != plan["previous_plan_sha256"]:
        raise ValueError("Previous GPU reference plan changed")
    score = scoring()
    paired = {group: {method: [] for method in RUNS} for group in GROUPS}
    parity = []
    for method in RUNS:
        if read(OUT / method / "COMPLETE.json")["scenes"] != 20:
            raise ValueError("Incomplete comparison")
        for case in plan["cases"]:
            stem = OUT / method / case["group"] / f'{case["index"]:03d}'
            row = read(stem.with_suffix(".json"))
            if (row["prediction_sha256"] != sha(stem.with_suffix(".npz")) or
                    row["input_sha256"] != case["files"]["input.npz"] or row["seed"] != case["seed"]):
                raise ValueError("Saved pairing changed")
            with np.load(stem.with_suffix(".npz"), allow_pickle=False) as pred:
                with np.load(Path(case["folder"]) / "truth.npz", allow_pickle=False) as truth:
                    checked = score(pred["estimate"], pred["probabilities"], truth["channel"], truth["activity"])
                if method == "v2":
                    old_stem = OLD / case["group"] / f'{case["index"]:03d}'
                    old_row = read(old_stem.with_suffix(".json"))
                    if sha(old_stem.with_suffix(".npz")) != old_row["prediction_sha256"]:
                        raise ValueError("Historical prediction changed")
                    with np.load(old_stem.with_suffix(".npz"), allow_pickle=False) as old:
                        parity.append(dict(group=case["group"], index=case["index"],
                            decision_differences=int(np.sum((pred["probabilities"] >= .5) != (old["probabilities"] >= .5))),
                            maximum_probability_difference=float(np.max(abs(pred["probabilities"]-old["probabilities"]))),
                            nmse_db_difference=10*np.log10(row["nmse"]/old_row["nmse"])))
            for key, value in checked.items():
                if not np.isclose(value, row[key], rtol=1e-12, atol=1e-12):
                    raise ValueError("Independent scoring failed: "+key)
            paired[case["group"]][method].append(row)
    groups = {}
    for group, methods in paired.items():
        summaries = {m: aggregate(rows) for m, rows in methods.items()}
        for a, b in zip(methods["v2"], methods["v3"]):
            for key in ("seed", "input_sha256", "active", "inactive", "truth_energy"):
                if a[key] != b[key]:
                    raise ValueError("Unpaired comparison: "+key)
        indices = np.random.default_rng(202610202204).integers(0, 10, (10000, 10))
        bootstrap = {}
        for method, rows in methods.items():
            sums = lambda key: np.asarray([r[key] for r in rows])[indices].sum(1)
            bootstrap[method] = dict(
                pooled_nmse_db=10*np.log10(sums("error_energy")/sums("truth_energy")),
                aer=(sums("misses")+sums("false_alarms"))/(sums("active")+sums("inactive")),
                missed_detection_rate=sums("misses")/sums("active"),
                false_alarm_rate=sums("false_alarms")/sums("inactive"))
        groups[group] = dict(methods=summaries,
            new_minus_v2={k:summaries["v3"][k]-summaries["v2"][k] for k in bootstrap["v2"]},
            paired_95_percentile={k:np.quantile(bootstrap["v3"][k]-bootstrap["v2"][k],[.025,.975]).tolist()
                                 for k in bootstrap["v2"]},
            new_lower_nmse_scenes=sum(b["nmse"] < a["nmse"] for a,b in zip(methods["v2"],methods["v3"])))
    write(OUT / "SUMMARY.json", dict(status="COMPLETE", groups=groups,
        cpu_vs_historical_gpu_v2=parity, gpu_used=False, training_modified=False,
        scope=plan["limitations"], timing_comparison_performed=False))
    lines = ["# 第三版与第二版四层：相同20场景CPU配对比较", "",
        "两版均使用各自原验证规则选中的四层第3轮权重；固定相同观测、缓存估计相位与估计噪声、0.5门限。"
        "每工况10场景，0 dB、活动概率0.1。双方均用CPU float32、2线程复算，未调用GPU，不进行速度比较。", "",
        "| 工况 | 模型 | 整体信道NMSE/dB | AER | 漏检率 | 虚警率 | 漏检/虚警 |",
        "|---|---|---:|---:|---:|---:|---:|"]
    for group in GROUPS:
        for method in RUNS:
            s = groups[group]["methods"][method]
            lines.append(f"| {group} | {method} | {s['pooled_nmse_db']:.4f} | {s['aer']:.3%} | "
                         f"{s['missed_detection_rate']:.3%} | {s['false_alarm_rate']:.3%} | "
                         f"{s['misses']}/{s['false_alarms']} |")
    lines += ["", "逐工况差值、10000次物理场景配对重抽样的描述性95%区间以及第二版CPU对历史GPU的数值核验见SUMMARY.json。",
              "这是已经揭示的两个实验端点，每工况10场景，不等同于全部19工况或独立大样本结论。"
              "两版初始化种子、损失和分阶段学习率一致；训练分布、训练样本及验证选模数据存在差异，不能把结果单独归因于某一项改变。"]
    (OUT / "REPORT.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    write(OUT / "AUDIT.json", dict(status="PASSED", independently_rescored_predictions=40,
        same_scene_input_and_truth_verified=True, checkpoint_and_source_hashes_verified=True,
        cpu_gpu_v2_decision_differences=sum(x["decision_differences"] for x in parity),
        maximum_scene_cpu_gpu_v2_nmse_db_difference=max(abs(x["nmse_db_difference"]) for x in parity),
        gpu_used=False, training_modified=False, plan_sha256=sha(OUT / "PLAN.json"),
        summary_sha256=sha(OUT / "SUMMARY.json")))
    write(OUT / "STATUS.json", dict(stage="COMPLETE", updated_unix=time.time()))
    print(json.dumps(dict(output=str(OUT), groups=groups, audit=read(OUT / "AUDIT.json")), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument("--method", choices=list(RUNS))
    mode.add_argument("--report", action="store_true")
    args = p.parse_args()
    if args.prepare:
        prepare()
    elif args.method:
        evaluate(args.method)
    else:
        report()
