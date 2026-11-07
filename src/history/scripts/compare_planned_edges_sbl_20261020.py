"""Run frozen off-grid SBL on the twenty saved endpoint observations."""
import os
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "1"
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time
import traceback
import warnings

ROOT = Path(r"C:\Users\25911\Desktop\afdm-gfra")
BASE = ROOT / "results/planned_edges_paired10_20261020"
OUT = ROOT / "results/planned_edges_sbl_paired10_20261020"
sys.path.insert(0, str(ROOT / "src"))
import numpy as np
from threadpoolctl import threadpool_limits
from afdm_jadcedd.algorithm.baselines.offgrid import receiver as offgrid
from afdm_jadcedd.algorithm.baselines.baseline_noise import EstimatedNoiseBaselineReceiver
from afdm_jadcedd.system.observation import ReceiverInput

# Frozen signatures use POSIX relative paths. Only path serialization changes.
_sources = offgrid.inference_sources
offgrid.inference_sources = lambda: {k.replace("\\", "/"): v for k, v in _sources().items()}
GROUPS = ("k100_q16", "k40_q8")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def model():
    return EstimatedNoiseBaselineReceiver(
        "offgrid_sbl", config=ROOT / "configs/offgrid_baselines.json", device="cpu")


def prepare():
    if OUT.exists():
        raise FileExistsError(OUT)
    receiver = model()  # Enforces the frozen solver/activity-policy binding.
    parent = read(BASE / "PLAN.json")
    assert read(BASE / "AUDIT.json")["status"] == "PASSED"
    hashes = {str(ROOT / p): h for p, h in offgrid.inference_sources().items()}
    for folder in ("src/afdm_jadcedd/algorithm/baselines",):
        for path in (ROOT / folder).rglob("*.py"):
            hashes[str(path)] = sha(path)
    for path in (ROOT / "configs/offgrid_baselines.json",
                 ROOT / "configs/offgrid_readout_policy.json",
                 ROOT / "configs/baseline_noise.json",
                 BASE / "PLAN.json", BASE / "SUMMARY.json", BASE / "AUDIT.json"):
        hashes[str(path)] = sha(path)
    OUT.mkdir()
    (OUT / "source").mkdir()
    saved = OUT / "source" / Path(__file__).name
    shutil.copy2(__file__, saved)
    hashes[str(saved)] = sha(saved)
    for case in parent["cases"]:
        for name, digest in case["files"].items():
            assert sha(Path(case["folder"]) / name) == digest
    write(OUT / "PLAN.json", dict(
        created_unix=time.time(), cases=parent["cases"], expected_runs=20,
        snr_db=0, activity_probability=.1, phase_mode="estimated", noise_mode="estimated",
        parent=str(BASE), hashes=hashes, configuration=receiver.configuration,
        inference_sha256=receiver.signature,
        native_base_signature=receiver.base.signature,
        signature_path_normalization="POSIX relative paths, matching frozen policy; no numerical change",
        pairing="Exact saved observation/operator; spatial noise re-estimated from observation, then native SBL noise updates.",
        threshold="Native frozen SBL energy readout; no probability threshold substitution.",
        timing="CPU single-thread SBL while existing GPU training continues; not a controlled cross-method benchmark."))
    print("Prepared 20 paired SBL evaluations; frozen policy binding passed.", flush=True)


def verify(plan):
    for path, digest in plan["hashes"].items():
        assert sha(path) == digest, path


def score(pred, truth):
    estimate = np.asarray(pred["estimate"], np.complex128)
    channel = np.asarray(truth["channel"], np.complex128)
    active = np.asarray(truth["activity"], bool)
    decision = np.asarray(pred["activity_decision"], bool)
    assert estimate.shape == channel.shape and decision.shape == active.shape
    assert all(np.isfinite(v).all() for v in pred.values())
    error = np.abs(estimate - channel)**2
    power = np.abs(channel)**2
    return dict(error_energy=float(error.sum()), truth_energy=float(power.sum()),
                active_error_energy=float(error[active].sum()),
                nmse=float(error.sum()/power.sum()), active=int(active.sum()),
                inactive=int((~active).sum()), misses=int((active & ~decision).sum()),
                false_alarms=int((~active & decision).sum()))


def run(group):
    threadpool_limits(1)
    plan = read(OUT / "PLAN.json")
    verify(plan)
    receiver = model()
    assert receiver.signature == plan["inference_sha256"]
    cases = [c for c in plan["cases"] if c["group"] == group]
    for case in cases:
        folder = Path(case["folder"])
        for name, digest in case["files"].items():
            assert sha(folder / name) == digest
        stem = OUT / group / f'{case["index"]:03d}'
        stem.parent.mkdir(parents=True, exist_ok=True)
        if stem.with_suffix(".json").exists():
            row = read(stem.with_suffix(".json"))
            assert row["status"] == "COMPLETE"
            assert sha(stem.with_suffix(".npz")) == row["prediction_sha256"]
            continue
        write(OUT / f"STATUS_{group}.json", dict(status="RUNNING", pid=os.getpid(),
              index=case["index"], updated_unix=time.time()))
        inputs = ReceiverInput(**dict(np.load(folder / "input.npz")))
        started = time.perf_counter()
        with warnings.catch_warnings(record=True) as notices:
            warnings.simplefilter("always", RuntimeWarning)
            predictions, record = receiver.infer(inputs)
        elapsed = time.perf_counter()-started
        assert np.isclose(record["noise_prior_reference_variance"], inputs.noise_variance,
                          rtol=1e-12, atol=1e-12)
        assert record["truth_used_in_inference"] is False
        # Scoring truth is first opened after inference returns.
        metrics = score(predictions, dict(np.load(folder / "truth.npz")))
        np.savez_compressed(stem.with_suffix(".npz"), **predictions)
        record.update(public_phase_mode="estimated", shared_frontend=str(folder / "frontend.json"),
                      warnings=[str(w.message) for w in notices])
        write(stem.with_suffix(".record.json"), record)
        write(stem.with_suffix(".json"), dict(
            status="COMPLETE", group=group, index=case["index"], seed=case["seed"],
            **metrics, iterations=record["iterations"], stopping_reason=record["stopping_reason"],
            seconds=elapsed, zero_output=bool(np.count_nonzero(predictions["estimate"]) == 0),
            input_sha256=case["files"]["input.npz"], prediction_sha256=sha(stem.with_suffix(".npz"))))
        print(f'{group} {case["index"]+1}/10: NMSE={10*np.log10(metrics["nmse"]):.4f} dB '
              f'MD={metrics["misses"]} FA={metrics["false_alarms"]} '
              f'iterations={record["iterations"]} seconds={elapsed:.2f}', flush=True)
    verify(plan)
    write(OUT / f"STATUS_{group}.json", dict(status="COMPLETE", predictions=10, updated_unix=time.time()))


def summarize():
    plan = read(OUT / "PLAN.json")
    verify(plan)
    results = read(BASE / "SUMMARY.json")["groups"]
    audit = []
    for group in GROUPS:
        assert read(OUT / f"STATUS_{group}.json")["status"] == "COMPLETE"
        rows = []
        for case in [c for c in plan["cases"] if c["group"] == group]:
            stem = OUT / group / f'{case["index"]:03d}'
            row = read(stem.with_suffix(".json"))
            assert row["seed"] == case["seed"]
            assert sha(stem.with_suffix(".npz")) == row["prediction_sha256"]
            assert sha(Path(case["folder"]) / "input.npz") == row["input_sha256"]
            pred = dict(np.load(stem.with_suffix(".npz")))
            truth = dict(np.load(Path(case["folder"]) / "truth.npz"))
            active = truth["activity"].astype(bool)
            decision = pred["activity_decision"].astype(bool)
            error = abs(pred["estimate"].astype(np.complex128)-truth["channel"].astype(np.complex128))**2
            for key, value in dict(error_energy=float(error.sum()),
                active_error_energy=float(error[active].sum()),
                truth_energy=float((abs(truth["channel"].astype(np.complex128))**2).sum()),
                misses=int((active & ~decision).sum()), false_alarms=int((~active & decision).sum())).items():
                assert np.isclose(row[key], value, rtol=1e-12, atol=1e-12), key
            record = read(stem.with_suffix(".record.json"))
            assert np.array_equal(decision, (pred["activity_score"] >= record["activity_threshold"]) &
                                  (pred["channel_energy"] > 0))
            rows.append(row)
            audit.append(dict(group=group, index=case["index"], status="PASSED"))
        total = lambda k: sum(r[k] for r in rows)
        active, inactive = total("active"), total("inactive")
        results[group]["offgrid_sbl"] = dict(
            scenes=len(rows), pooled_nmse_db=float(10*np.log10(total("error_energy")/total("truth_energy"))),
            active_nmse_db=float(10*np.log10(total("active_error_energy")/total("truth_energy"))),
            misses=total("misses"), false_alarms=total("false_alarms"), active=active, inactive=inactive,
            aer=(total("misses")+total("false_alarms"))/(active+inactive),
            md=total("misses")/active, fa=total("false_alarms")/inactive,
            zero_outputs=total("zero_output"),
            mean_iterations=float(np.mean([r["iterations"] for r in rows])),
            stopping_reasons={s:sum(r["stopping_reason"] == s for r in rows)
                              for s in sorted({r["stopping_reason"] for r in rows})},
            mean_seconds=float(np.mean([r["seconds"] for r in rows])))
    write(OUT / "SUMMARY.json", dict(status="COMPLETE", groups=results))
    write(OUT / "AUDIT.json", dict(status="PASSED", direct_array_rescoring=True,
          native_activity_rule_verified=True, paired_inputs_unchanged=True, cases=audit))
    lines = ["# 两个实验端点：Off-grid SBL 补充配对比较", "",
        "每个条件10个原有场景，SNR=0 dB、活动概率0.1；未重新生成或筛选场景。"
        "三种方法共享观测及保存的估计相位算子。SBL从相同观测得到与缓存一致的初始空间噪声估计，"
        "随后按原生算法更新噪声方差。使用默认120轮预算、1e-4容差和冻结活动判决规则。", "",
        "| 条件 | 方法 | NMSE/dB | 活跃用户误差/dB | AER | 漏检率 | 虚警率 | 漏检/虚警 |",
        "|---|---|---:|---:|---:|---:|---:|---:|"]
    for group in GROUPS:
        for method, name in (("new_seven_layer", "既有七层"), ("legacy_50000_damping01", "旧三网络"),
                             ("offgrid_sbl", "Off-grid SBL")):
            s = results[group][method]
            lines.append(f'| {group} | {name} | {s["pooled_nmse_db"]:.4f} | {s["active_nmse_db"]:.4f} | '
                         f'{s["aer"]:.2%} | {s["md"]:.2%} | {s["fa"]:.2%} | {s["misses"]}/{s["false_alarms"]} |')
    lines += ["", "NMSE为所有用户累计误差能量与真值能量之比，不按真值活动掩码去除输出。"
              "SBL采用自身能量判决规则，七层和旧三网络采用概率门限0.5。"
              "20份SBL完整预测已独立重评分，并核对原生判决规则和输入文件哈希。",
              "旧算法为50k权重、0.1阻尼；七层为此前选定权重。本次没有重新训练、调参或修改推断算法。",
              "每条件仅10个场景，结果用于初步比较。SBL在CPU上运行，现有GPU训练继续；耗时不作为三算法公平速度比较。"]
    (OUT / "REPORT.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(json.dumps(results, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "run", "summarize"))
    parser.add_argument("--group", choices=GROUPS)
    args = parser.parse_args()
    try:
        if args.action == "prepare":
            prepare()
        elif args.action == "summarize":
            summarize()
        else:
            assert args.group
            run(args.group)
    except Exception:
        if OUT.exists():
            write(OUT / f"FAILURE_{args.group or args.action}.json",
                  dict(time=time.time(), traceback=traceback.format_exc()))
        raise
