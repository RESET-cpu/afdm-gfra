"""Evaluate the completed v2 depth-four selection on the saved twenty scenes."""
import os
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "1"
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import time
import warnings
import numpy as np

ROOT = Path(r"C:\Users\25911\Desktop\afdm-gfra")
RUN = Path(r"D:\afdm-gfra-cpu\runs\lstmp_conditional_bce_v2_20261020")
BASE = ROOT / "results/planned_edges_paired10_20261020"
SBL = ROOT / "results/planned_edges_sbl_paired10_20261020"
OUT = ROOT / "results/planned_edges_v2_depth4_paired10_20261020"
os.environ["AFDM_LSTMP_ROOT"] = str(ROOT)
os.environ["AFDM_LSTMP_CONFIG"] = str(
    RUN / "source_code/experiments/lstmp_training_v2_20261020/config.json")
sys.path.insert(0, str(RUN / "source_code"))
import torch
from threadpoolctl import threadpool_limits
from experiments.lstmp_candidate_20261019 import common, data
from experiments.lstmp_training_v2_20261020.receiver import Receiver

spec = importlib.util.spec_from_file_location("endpoint_helpers", BASE / "source/compare_planned_edges_20261020.py")
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)
read, write, sha = E.read, E.write, E.sha


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    torch.set_num_threads(1)
    threadpool_limits(1)
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    assert Path(common.OUT).resolve() == RUN.resolve()
    checkpoint = RUN / "checkpoints/depth_4/best.pt"
    receipt = read(checkpoint.parent / "COMPLETE.json")
    selection = read(checkpoint.parent / "BEST.json")
    assert receipt["depth"] == 4 and receipt["updates"] == 14400
    assert receipt["selected_epoch"] == selection["epoch"] == 3
    assert sha(checkpoint) == receipt["best_sha256"] == receipt["epoch_sha256"]["3"]
    manifest = read(RUN / "MANIFEST.json")
    assert common.CONFIG == manifest["configuration"]
    hashes = dict(manifest["snapshot_hashes"])
    for path in (checkpoint, checkpoint.parent / "BEST.json", checkpoint.parent / "COMPLETE.json",
                 RUN / "MANIFEST.json", BASE / "PLAN.json", SBL / "SUMMARY.json", SBL / "AUDIT.json"):
        hashes[str(path)] = sha(path)
    for path in (BASE / "source").glob("*.py"):
        hashes[str(path)] = sha(path)
    for path, digest in hashes.items():
        assert sha(path) == digest, path
    assert read(SBL / "AUDIT.json")["status"] == "PASSED"
    parent = read(BASE / "PLAN.json")
    scale = parent["scale"]
    assert np.isclose(scale, common.CONFIG["pretrained_score"]["global_complex_rms"])
    OUT.mkdir()
    (OUT / "source").mkdir()
    saved = OUT / "source" / Path(__file__).name
    shutil.copy2(__file__, saved)
    hashes[str(saved)] = sha(saved)
    plan = dict(cases=parent["cases"], checkpoint=str(checkpoint), selected_epoch=3, depth=4,
                checkpoint_sha256=sha(checkpoint), source_hashes=hashes, scale=scale,
                snr_db=0, activity_probability=.1, threshold=.5,
                phase_mode="estimated", noise_mode="estimated",
                training_status_at_start=read(RUN / "STATUS.json"),
                selection="Existing validation-selected completed depth-four best; no selection on these scenes.",
                input_policy="Use exact cached estimated operator and noise. Internal known flags only skip re-estimation.",
                inference_device="cuda", tf32=True, created_unix=time.time())
    write(OUT / "PLAN.json", plan)
    state = torch.load(checkpoint, map_location="cpu", weights_only=False)
    assert state["depth"] == 4
    model = Receiver()
    for _ in range(4):
        model.add_layer(None)
    model.load_state_dict(state["state"], strict=True)
    del state
    model.cuda().eval()
    model.use_checkpoint = False
    rows_by_group = {g: [] for g in E.GROUPS}
    for case in plan["cases"]:
        folder = Path(case["folder"])
        for name, digest in case["files"].items():
            assert sha(folder / name) == digest
        write(OUT / "STATUS.json", dict(status="RUNNING", group=case["group"], index=case["index"]))
        public = dict(np.load(folder / "input.npz"))
        started = time.perf_counter()
        with warnings.catch_warnings(record=True) as notices, torch.no_grad():
            prepared, frontend = data.prepare_public(dict(
                y=public["observation"], a=public["operator"], noise=public["noise_variance"],
                rho=public["activity_prior"]), scale, "cuda", phase_mode="known", noise_mode="known")
            torch.cuda.synchronize()
            ready = time.perf_counter()
            outputs, diagnostics = model(prepared)
            torch.cuda.synchronize()
            finished = time.perf_counter()
            final = outputs[-1]
            def physical(value):
                real = value.cpu().numpy()
                return (real[:, 0].astype(np.float64) + 1j*real[:, 1].astype(np.float64))*scale
            pred = dict(estimate=physical(final["estimate"]), conditional=physical(final["conditional"]),
                        probabilities=torch.sigmoid(final["logits"]).cpu().numpy(),
                        logits=final["logits"].cpu().numpy())
        assert all(np.isfinite(v).all() for v in pred.values())
        truth = dict(np.load(folder / "truth.npz"))
        metrics = E.C.score_arrays(pred["estimate"], pred["probabilities"], truth["channel"], truth["activity"])
        stem = OUT / case["group"] / f'{case["index"]:03d}'
        stem.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(stem.with_suffix(".npz"), **pred)
        write(stem.with_suffix(".record.json"), dict(iterations=4, diagnostics=diagnostics,
              phase_mode="estimated", noise_mode="estimated", truth_used_in_inference=False,
              cached_preparation=frontend,
              cached_preparation_note="known/oracle flags here refer to supplied cached estimates, not truth.",
              warnings=[str(w.message) for w in notices]))
        row = dict(status="COMPLETE", group=case["group"], index=case["index"], seed=case["seed"],
                   **metrics, iterations=4, converged=None, stopping_reason="FIXED_4_LAYERS",
                   zero_output=bool(np.count_nonzero(pred["estimate"]) == 0),
                   seconds=finished-ready, preparation_seconds=ready-started,
                   prediction_sha256=sha(stem.with_suffix(".npz")), input_sha256=case["files"]["input.npz"])
        write(stem.with_suffix(".json"), row)
        rows_by_group[case["group"]].append(row)
        print(f'{case["group"]} {case["index"]+1}/10: NMSE={10*np.log10(row["nmse"]):.4f} dB '
              f'MD={row["misses"]} FA={row["false_alarms"]}', flush=True)
    results = read(SBL / "SUMMARY.json")["groups"]
    for group, rows in rows_by_group.items():
        assert len(rows) == 10
        results[group]["v2_four_layer"] = E.aggregate(rows)
    # Reopen full predictions and independently check the reported scores.
    for case in plan["cases"]:
        stem = OUT / case["group"] / f'{case["index"]:03d}'
        row = read(stem.with_suffix(".json"))
        assert sha(stem.with_suffix(".npz")) == row["prediction_sha256"]
        pred = dict(np.load(stem.with_suffix(".npz")))
        truth = dict(np.load(Path(case["folder"]) / "truth.npz"))
        active = truth["activity"].astype(bool)
        decision = pred["probabilities"] >= .5
        err = abs(pred["estimate"]-truth["channel"].astype(np.complex128))**2
        for key, value in dict(error_energy=err.sum(), active_error_energy=err[active].sum(),
            truth_energy=(abs(truth["channel"].astype(np.complex128))**2).sum(),
            misses=int((active & ~decision).sum()), false_alarms=int((~active & decision).sum())).items():
            assert np.isclose(row[key], value, rtol=1e-12, atol=1e-12), key
    for path, digest in hashes.items():
        assert sha(path) == digest, path
    write(OUT / "SUMMARY.json", dict(status="COMPLETE", groups=results))
    write(OUT / "AUDIT.json", dict(status="PASSED", predictions=20, direct_array_rescoring=True,
          input_and_checkpoint_hashes_verified=True, training_modified=False, selection_before_test=True))
    lines = ["# 第二版四层：相同20场景配对比较", "",
        "每条件10场景，SNR=0 dB，活动概率0.1；复用已有观测、估计相位及估计噪声。"
        "第二版四层已完成14400次更新，使用原验证集选中的epoch 3，不按本次结果选权重。"
        "活动门限0.5，推断固定4层，无训练、调参或场景重选。", "",
        "| 条件 | 方法 | 整体NMSE/dB | 活跃用户误差/dB | AER | 漏检率 | 虚警率 | 漏检/虚警 |",
        "|---|---|---:|---:|---:|---:|---:|---:|"]
    for group in E.GROUPS:
        for method, name in (("v2_four_layer", "第二版四层"), ("new_seven_layer", "第一版七层"),
                             ("legacy_50000_damping01", "旧三网络"), ("offgrid_sbl", "Off-grid SBL")):
            s = results[group][method]
            lines.append(f'| {group} | {name} | {s["pooled_nmse_db"]:.4f} | {s["active_nmse_db"]:.4f} | '
                         f'{s["aer"]:.2%} | {s["md"]:.2%} | {s["fa"]:.2%} | {s["misses"]}/{s["false_alarms"]} |')
    lines += ["", "整体NMSE包含非活跃用户输出误差，按累计误差能量/累计真值能量计算。"
              "保留完整有效信道估计、条件信道估计、活动概率和逐层诊断；20份输出独立重评分通过。",
              "内部prepare_public使用known标志仅用于直接接收已经估计并缓存的算子/噪声，未使用真实相位或真实噪声。",
              "四层与七层的深度、训练目标及训练流程均不同，不能将差异单独归因于某项修复。"
              "每条件仅10场景，不代表正式大样本结论；本次不用于跨算法速度比较。"]
    (OUT / "REPORT.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    write(OUT / "STATUS.json", dict(status="COMPLETE", predictions=20))
    print(json.dumps({g:results[g]["v2_four_layer"] for g in E.GROUPS}, indent=2), flush=True)


if __name__ == "__main__":
    main()
