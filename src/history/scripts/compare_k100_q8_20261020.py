"""Paired diagnostic on a predeclared seed-ordered subset of development data."""
import os
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "1"
import argparse
import gc
import importlib.util
import json
from pathlib import Path
import shutil
import time
import traceback
import numpy as np

ROOT = Path(r"C:\Users\25911\Desktop\afdm-gfra")
RUN = Path(r"D:\afdm-gfra-cpu\runs\lstmp_refinenet_depth7_20261020")
OUT = ROOT / "results/k100_q8_legacy_vs_seven_20_20261020"
SOURCE = Path(__file__).parent
CORE = SOURCE / "evaluate_lstmp_depth7_threeway_20261020.py"
spec = importlib.util.spec_from_file_location("paired_seven", CORE)
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)
C = G.C
read, write, sha = C.read, C.write, C.sha
METHODS = ("new_seven_layer", "legacy_50000_damping01")


def prepare():
    if OUT.exists():
        raise FileExistsError(OUT)
    common, data, _ = C.modules(ROOT, RUN)
    assert G.readiness(RUN)[0]
    validation = RUN / "checkpoints/depth_7/validation_epoch_1.json"
    rows = read(validation)["rows"]
    selected = []
    for snr in (-5., 0., 5., 10.):
        group = sorted((r for r in rows if r["users"] == 100 and r["frames"] == 8
                        and r["snr"] == snr and r["condition"]["activity_probability"] == .1),
                       key=lambda r: r["seed"])
        assert len(group) == 50
        selected.extend(group[:5])
    old_plan = read(ROOT / "results/lstmp_epoch6_vs_legacy20_20261020/PLAN.json")
    from afdm_jadcedd.system.observation import array_sha256
    OUT.mkdir()
    (OUT / "source").mkdir()
    for path in (Path(__file__), CORE, C.CORE_PATH if hasattr(C, "CORE_PATH") else
                 ROOT / "scripts/evaluate_lstmp_epoch6_vs_legacy20.py"):
        shutil.copy2(path, OUT / "source" / path.name)
    cases = []
    for i, row in enumerate(selected):
        path = data.case_path("validation", row["source_pool_index"])
        values = dict(np.load(path))
        data.validate_case(values, "validation", row["source_pool_index"])
        assert int(values["seed"]) == row["seed"]
        assert array_sha256(values["y"]) == row["frontend"]["observation_sha256"]
        assert array_sha256(values["a"]) == row["frontend"]["operator_sha256"]
        cases.append(dict(index=i, seed=row["seed"], snr=row["snr"],
                          path=str(path), sha256=sha(path), saved_seven=row))
    plan = dict(root=str(ROOT), training_run=str(RUN), methods=list(METHODS),
                scale=old_plan["scale"], old_binding=old_plan["old_binding"],
                new_checkpoint="checkpoints/depth_7/best.pt",
                checkpoint_sha256=sha(RUN / "checkpoints/depth_7/best.pt"),
                new_microbatch=common.CONFIG["receiver"]["microbatch"], cases=cases,
                phase_mode="known", noise_mode="known", threshold=.5,
                selection="First five seeds per SNR among all fifty saved K100/Q8/p0.1 development cases; selected before inference.",
                validation_source=str(validation), validation_sha256=sha(validation),
                manifest_sha256=sha(RUN / "MANIFEST.json"),
                source_hashes={str(p): sha(p) for p in (OUT / "source").glob("*.py")},
                limitations="Revealed development subset, not an independent test. Concurrent existing GPU training; times are diagnostic only, not a speed comparison. Both algorithms unchanged.",
                created_unix=time.time())
    write(OUT / "PLAN.json", plan)
    print(json.dumps(dict(prepared=len(cases), output=str(OUT))), flush=True)


def aggregate(rows):
    total = lambda k: sum(r[k] for r in rows)
    e, t = total("error_energy"), total("truth_energy")
    a, n = total("active"), total("inactive")
    return dict(scenes=len(rows), pooled_nmse_db=10*np.log10(e/t),
                active_nmse_db=10*np.log10(total("active_error_energy")/t),
                mean_scene_nmse_db=10*np.log10(np.mean([r["nmse"] for r in rows])),
                misses=total("misses"), false_alarms=total("false_alarms"),
                active=a, inactive=n, aer=(total("misses")+total("false_alarms"))/(a+n),
                md=total("misses")/a, fa=total("false_alarms")/n,
                error_energy=e, truth_energy=t,
                converged=sum(r["converged"] is True for r in rows),
                mean_iterations=np.mean([r["iterations"] for r in rows]))


def audit_report(plan):
    metrics = {}
    for method in METHODS:
        rows = []
        for case in plan["cases"]:
            path = OUT / method / f'{case["index"]:03d}'
            row = read(path.with_suffix(".json"))
            assert row["input_sha256"] == case["sha256"] == sha(case["path"])
            assert row["prediction_sha256"] == sha(path.with_suffix(".npz"))
            pred = dict(np.load(path.with_suffix(".npz")))
            values = dict(np.load(case["path"]))
            score = C.score_arrays(pred["estimate"], pred["probabilities"], values["x"], values["active"])
            for key in score:
                assert np.isclose(score[key], row[key], rtol=1e-12, atol=1e-12), key
            rows.append(row)
        metrics[method] = dict(overall=aggregate(rows), by_snr={
            str(snr): aggregate([r for r in rows if r["snr"] == snr]) for snr in (-5.,0.,5.,10.)})
    summary = dict(status="COMPLETE", methods=metrics, audited_predictions=40,
                   limitations=plan["limitations"])
    write(OUT / "SUMMARY.json", summary)
    lines = ["# K=100、Q=8：旧三网络与七层的20场景配对比较", "",
             "活动采样概率0.1，已知相位和噪声。每档SNR按种子取开发验证集前5场景；"
             "不是独立测试。旧算法为50k权重、0.1阻尼、最多600轮；七层为既有选中权重。",
             "", "| SNR | 方法 | NMSE/dB | AER | 漏检率 | 虚警率 | 漏检/虚警 |",
             "|---:|---|---:|---:|---:|---:|---:|"]
    for snr in ("-5.0","0.0","5.0","10.0","all"):
        for method, name in zip(METHODS, ("七层","旧三网络")):
            s = metrics[method]["overall"] if snr == "all" else metrics[method]["by_snr"][snr]
            lines.append(f'| {snr} | {name} | {s["pooled_nmse_db"]:.4f} | {s["aer"]:.2%} | {s["md"]:.2%} | {s["fa"]:.2%} | {s["misses"]}/{s["false_alarms"]} |')
    lines += ["", "40份完整预测均从保存数组独立重评分。活动门限0.5，保留非活跃用户误差，"
              "未按结果删除场景或修改权重、阻尼和迭代预算。现有GPU训练同时运行，耗时不用于速度比较。"]
    (OUT / "REPORT.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    write(OUT / "AUDIT.json", dict(status="PASSED", predictions=40, rescored=True,
                                   checkpoint_unchanged=sha(RUN/plan["new_checkpoint"]) == plan["checkpoint_sha256"]))
    return summary


def run():
    import torch
    from threadpoolctl import threadpool_limits
    torch.set_num_threads(1)
    threadpool_limits(1)
    torch.backends.cuda.matmul.allow_tf32 = True
    plan = read(OUT / "PLAN.json")
    for path, digest in plan["source_hashes"].items():
        assert sha(path) == digest
    assert sha(RUN / "MANIFEST.json") == plan["manifest_sha256"]
    assert sha(RUN / plan["new_checkpoint"]) == plan["checkpoint_sha256"]
    common, data, receiver = C.modules(ROOT, RUN)
    from afdm_jadcedd.system.observation import ReceiverInput
    manifest = read(RUN / "MANIFEST.json")
    for path, digest in manifest["snapshot_hashes"].items():
        assert sha(path) == digest, path
    for key in ("first_checkpoint", "second_checkpoint", "evidence_checkpoint"):
        cfg = plan["old_binding"]["applied_configuration"]
        assert sha(ROOT / cfg[key]) == cfg[key+"_sha256"]
    for method in METHODS:
        adapter = G.Adapter(method, plan, common, data, receiver)
        folder = OUT / method
        folder.mkdir(exist_ok=True)
        for case in plan["cases"]:
            target = folder / f'{case["index"]:03d}'
            if target.with_suffix(".json").exists():
                continue
            assert sha(case["path"]) == case["sha256"]
            values = dict(np.load(case["path"]))
            public = ReceiverInput(values["y"], values["a"], float(values["noise"]), float(values["rho"]))
            write(OUT / "STATUS.json", dict(stage="RUNNING", method=method, index=case["index"],
                   snr=case["snr"], pid=os.getpid(), updated_unix=time.time()))
            predictions, record, times = C.timed_inference(adapter, public)
            if "probabilities" not in predictions:
                predictions["probabilities"] = predictions["activity_probability"]
            score = C.score_arrays(predictions["estimate"], predictions["probabilities"],
                                   values["x"], values["active"])
            np.savez_compressed(target.with_suffix(".npz"), **predictions)
            write(target.with_suffix(".record.json"), record)
            row = dict(status="COMPLETE", seed=case["seed"], snr=case["snr"], **score,
                       iterations=record["iterations"], converged=record.get("converged"),
                       stopping_reason=record.get("stopping_reason"), times=times,
                       input_sha256=case["sha256"], prediction_sha256=sha(target.with_suffix(".npz")))
            if method == METHODS[0]:
                old = case["saved_seven"]
                row["saved_validation_difference"] = dict(
                    nmse=score["nmse"]-old["nmse"], misses=score["misses"]-old["misses"],
                    false_alarms=score["false_alarms"]-old["false_alarms"])
            write(target.with_suffix(".json"), row)
            print(json.dumps(dict(method=method,index=case["index"],snr=case["snr"],
                    nmse_db=10*np.log10(score["nmse"]),misses=score["misses"],
                    false_alarms=score["false_alarms"],seconds=times["total_seconds"])),flush=True)
        del adapter
        gc.collect()
        torch.cuda.empty_cache()
    result = audit_report(plan)
    write(OUT / "STATUS.json", dict(stage="COMPLETE", updated_unix=time.time()))
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "run"))
    args = parser.parse_args()
    try:
        prepare() if args.action == "prepare" else run()
    except Exception:
        if OUT.exists():
            write(OUT / "FAILURE.json", dict(time=time.time(), traceback=traceback.format_exc()))
        raise
