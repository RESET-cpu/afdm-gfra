"""Frozen standard-condition comparison, with shared estimated phase and noise.

The three unfolded models run on CPU. The existing formal three-network result
is reused without changing its damping, stopping, predictions or observations.
"""
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "2"
import argparse
import csv
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback
sys.dont_write_bytecode = True
import numpy as np

ROOT = Path(r"C:\Users\25911\Desktop\afdm-gfra")
OUT = ROOT / "results/lstmp_v3_depth6_standard20_cpu_20261021"
REFERENCE = ROOT / "results/convergence_sizes_pilots_gpu_20261019"
PRIOR = ROOT / "results/lstmp_v3_depth6_previous20_cpu_20261021"
TEN = ROOT / "results/lstmp_v3_depth10_previous20_20261020"
TEN_SHA = "55d6ea14481c608ff873401e275d1cd3d2e9d589c450fbafd83d3f8fcad0e9a9"
NEW = "v3_six_layer"
LEGACY = "legacy_formal_damping02"
METHODS = (NEW, "prior_seven_layer", "prior_five_layer", LEGACY)
LABELS = ("新六层", "此前七层", "此前五层", "旧三网络：正式配置阻尼0.2")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temp.replace(path)


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def scoring():
    spec = importlib.util.spec_from_file_location("standard20_scoring", OUT / "source/paired_core.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.score_arrays


def cpu_setup():
    import psutil
    if os.name == "nt":
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    import torch
    from threadpoolctl import threadpool_limits
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    threadpool_limits(2)
    return torch


def verify(plan):
    if sha(TEN / "PLAN.json") != TEN_SHA:
        raise ValueError("Pending depth-ten plan changed")
    for path, digest in plan["protected_hashes"].items():
        if sha(path) != digest:
            raise ValueError("Protected reference/model changed: " + path)
    for rel, digest in plan["local_hashes"].items():
        if sha(OUT / rel) != digest:
            raise ValueError("Frozen evaluation input/source changed: " + rel)


def prepare():
    if OUT.exists():
        raise FileExistsError(OUT)
    cpu_setup()
    sys.path[:0] = [str(ROOT), str(ROOT / "src")]
    from experiment._common import observation
    from afdm_jadcedd.system.observation import array_sha256
    from afdm_jadcedd.algorithm.baselines.noise_estimation import estimate_spatial_noise
    refplan = read(REFERENCE / "PLAN.json")
    refspec = refplan["experiment"]
    if read(REFERENCE / "SUMMARY.json")["status"] != "COMPLETE":
        raise ValueError("Formal reference panel incomplete")
    if (refspec["scenes"] != 20 or refspec["users"] != 40 or refspec["frames"] != 16
            or refspec["activity_probability"] != .1 or refspec["snr_db"] != [-4, 0, 4]):
        raise ValueError("Unexpected formal condition panel")
    legacy_config = refspec["proposed_bundles"]["proposed"]["configuration"]
    previous_legacy = read(TEN / "PLAN.json")["old_binding"]["applied_configuration"]
    prior_copy = json.loads(json.dumps(previous_legacy))
    prior_copy["ep"]["damping"] = .2
    if legacy_config != prior_copy:
        raise ValueError("Formal reference differs from previous legacy by more than its declared damping")
    protected = {str(REFERENCE / n): sha(REFERENCE / n) for n in ("PLAN.json", "SUMMARY.json", "GPU_EXECUTION.json")}
    models = {}
    definitions = (
        (NEW, "lstmp_conditional_bce_v3_depth10_fast_20261020", 6, "lstmp_execution_v3_20261020", "config.json", "91e37437b5683f05e67088ba52074a0c40e9a6bfc252d315e4c7fd29bf6ff00d"),
        ("prior_seven_layer", "lstmp_refinenet_depth7_20261020", 7, "lstmp_candidate_20261019", "reuse_50000_fast.json", "b04f9d4459fd92b203d71ca92664267b81655b00bf4dada1c7b4fb1f7d1bd85d"),
        ("prior_five_layer", "lstmp_refinenet_50000_epoch6_20261020", 5, "lstmp_candidate_20261019", "reuse_50000_fast.json", "06ca92cfa4457ce4937fa8bf1461176302e0704b2e8c9576f6e20284c09b881c"))
    for method, runname, depth, package, cfgname, expected in definitions:
        run = Path(r"D:\afdm-gfra-cpu\runs") / runname
        checkpoint = run / f"checkpoints/depth_{depth}/best.pt"
        receipt_path = checkpoint.parent / "COMPLETE.json"
        receipt = read(receipt_path)
        if sha(checkpoint) != expected or receipt.get("best_sha256", receipt.get("checkpoint_sha256")) != expected:
            raise ValueError("Wrong selected checkpoint: " + method)
        if method == NEW:
            history = read(checkpoint.parent / "history.json")
            chosen = min(history, key=lambda x: (x["selection_loss"], x["epoch"]))["epoch"]
            if receipt["updates"] != 14250 or chosen != receipt["selected_epoch"]:
                raise ValueError("Invalid six-layer training/selection")
        manifest = read(run / "MANIFEST.json")
        protected.update(manifest["snapshot_hashes"])
        for p in (checkpoint, receipt_path, run / "MANIFEST.json"):
            protected[str(p)] = sha(p)
        config = run / "source_code/experiments" / package / cfgname
        models[method] = dict(run=str(run), depth=depth, checkpoint=str(checkpoint), checkpoint_sha256=expected,
            selected_epoch=receipt["selected_epoch"], config=str(config), package=package,
            manifest_sha256=sha(run / "MANIFEST.json"))
        rc = read(config)["receiver"]
        seeds = set(range(refspec["seed"], refspec["seed"] + 20))
        for split in ("train", "validation", "test"):
            if f"{split}_seed" in rc and not seeds.isdisjoint(range(rc[f"{split}_seed"], rc[f"{split}_seed"] + rc[f"{split}_scenes"])):
                raise ValueError("Evaluation overlaps a training/selection seed range")
    OUT.mkdir()
    (OUT / "source").mkdir()
    shutil.copy2(__file__, OUT / "source" / Path(__file__).name)
    shutil.copy2(PRIOR / "source/paired_core.py", OUT / "source/paired_core.py")
    score = scoring()
    cases = []
    condition = dict(users=40, frames=16, activity_probability=.1, snr_db=0.)
    for i in range(20):
        source = REFERENCE / f"scene{i:03d}/snr01"
        dest = OUT / f"cases/{i:03d}"
        dest.mkdir(parents=True)
        old = read(source / "proposed.json")
        native = read(source / "proposed.native.json")
        cache = read(source / "PHASE_CACHE.json")
        if (old["status"] != "COMPLETE" or old["scene"] != i or old["snr_db"] != 0 or old["pilot_type"] != "dft"
                or not old["last_point_matches_native_output"] or sha(source / "proposed.npz") != old["output_sha256"]
                or sha(source / "phase.npz") != cache["phase_sha256"]):
            raise ValueError("Invalid legacy record")
        if native["checkpoint_sha256"] != {k: legacy_config[k + "_sha256"] for k in ("first_checkpoint", "second_checkpoint", "evidence_checkpoint")}:
            raise ValueError("Wrong historical three-network weights")
        seed = refspec["seed"] + i
        public, generated_truth, _ = observation(seed, condition, refspec["scale"])
        hashes = {k: array_sha256(v) for k, v in public.arguments().items()}
        if hashes != old["input_sha256"] or hashes != cache["identity"]["inputs"]:
            raise ValueError("Regenerated public observation does not match the historical input exactly")
        with np.load(source / "truth.npz", allow_pickle=False) as truth:
            for key in truth.files:
                np.testing.assert_array_equal(generated_truth[key], truth[key])
            with np.load(source / "proposed.npz", allow_pickle=False) as pred:
                scores = score(pred["estimate"], pred["probabilities"], truth["channel"], truth["activity"], threshold=.5)
                np.testing.assert_array_equal(pred["activity_decision"], pred["probabilities"] >= .5)
        if not np.isclose(scores["error_energy"], old["points"][-1]["full_error"], rtol=1e-12, atol=1e-12):
            raise ValueError("Historical endpoint NMSE rescoring mismatch")
        variance, noise_record = estimate_spatial_noise(public.observation)
        if native["noise_mode"] != "estimated" or native["supplied_noise_variance_used"] or not np.isclose(variance, native["noise_variance_estimate"], rtol=1e-12, atol=1e-12):
            raise ValueError("Historical and regenerated noise estimates differ")
        with np.load(source / "phase.npz", allow_pickle=False) as phase:
            conditional = public.at_estimated_phase(phase["phase_slopes"])
        np.savez_compressed(dest / "input.npz", observation=conditional.observation, operator=conditional.operator,
                            noise_variance=np.asarray(variance), activity_prior=np.asarray(conditional.activity_prior))
        np.savez_compressed(dest / "public.npz", **public.arguments())
        for name in ("truth.npz", "phase.npz", "PHASE_CACHE.json", "GENERATION.json"):
            shutil.copy2(source / name, dest / name)
        write(dest / "FRONTEND.json", dict(phase_mode="estimated", noise_mode="estimated", truth_used_in_inference=False,
            historical_input_hashes=hashes, original_phase_sha256=cache["phase_sha256"],
            noise_estimate=variance, noise_record=noise_record, internal_known_flags="Only consume already-estimated cached operator/noise; no oracle supplied."))
        target = OUT / LEGACY
        target.mkdir(exist_ok=True)
        shutil.copy2(source / "proposed.npz", target / f"{i:03d}.npz")
        shutil.copy2(source / "proposed.json", target / f"{i:03d}_original.json")
        shutil.copy2(source / "proposed.native.json", target / f"{i:03d}_native.json")
        write(target / f"{i:03d}.json", dict(status="COMPLETE", case_index=i, seed=seed,
            input_sha256=sha(dest / "input.npz"), prediction_sha256=old["output_sha256"], **scores,
            iterations=native["iterations"], stopping_reason=native["stopping_reason"],
            recorded_receiver_seconds=native["seconds"], device="historical CUDA float32; TF32 disabled",
            timing_scope="Historical convergence observer enabled; no isolated timing comparison."))
        for name in ("proposed.json", "proposed.native.json", "proposed.npz", "truth.npz", "phase.npz", "PHASE_CACHE.json", "GENERATION.json"):
            protected[str(source / name)] = sha(source / name)
        cases.append(dict(index=i, seed=seed, source=str(source), input_sha256=sha(dest / "input.npz")))
        print(json.dumps(dict(stage="PREPARING", scene=i + 1, public_input_exact=True, legacy_rescored=True)), flush=True)
    for module in list(sys.modules.values()):
        p = getattr(module, "__file__", None)
        if p and Path(p).is_file() and Path(p).resolve().is_relative_to(ROOT) and Path(p).suffix == ".py":
            protected[str(Path(p).resolve())] = sha(p)
    local = {p.relative_to(OUT).as_posix(): sha(p) for p in OUT.rglob("*") if p.is_file()}
    plan = dict(schema="standard20-unfolded-vs-formal-legacy-v1", created_unix=time.time(),
        authorization="User requested a further comparison under standard conditions on 2026-10-21.",
        condition=condition, scale=refspec["scale"], phase_mode="estimated", noise_mode="estimated", threshold=.5,
        scene_count=20, cases=cases, methods=list(METHODS), models=models, legacy_configuration=legacy_config,
        previous_5db_reference_difference="Same legacy network weights, formal damping 0.2 instead of prior known-phase 5dB comparison damping 0.1; different fixed physical scene panel and estimated phase/noise.",
        protected_hashes=protected, local_hashes=local, cpu_threads=2,
        checkpoint_selection="Existing original validation selections fixed before this evaluation; new model remains depth six throughout.",
        bootstrap=dict(samples=10000, seed=2026102198),
        scope="Complete original 20 DFT scenes at 0dB from the formal convergence panel, without selecting scenes by performance. Reference was previously revealed; no independent-confirmation claim.",
        timing="All three unfolded methods newly inferred on CPU two threads, untimed first-scene warmup, shared cached frontend excluded. Legacy retains historical GPU observer timing. No speed ranking.")
    write(OUT / "PLAN.json", plan)
    verify(plan)
    write(OUT / "PREPARATION_AUDIT.json", dict(status="PASSED", plan_sha256=sha(OUT / "PLAN.json"),
        historical_observation_hashes_matched=20, generated_truth_matched=20, legacy_predictions_rescored=20,
        phase_estimates_reused_exactly=True, noise_estimates_matched=True, gpu_used=False))
    write(OUT / "STATUS.json", dict(stage="PREPARED", updated_unix=time.time()))


def evaluate(method):
    plan = read(OUT / "PLAN.json")
    verify(plan)
    folder = OUT / method
    if (folder / "COMPLETE.json").exists():
        return
    folder.mkdir(exist_ok=True)
    lock = folder / "RUNNING.lock"
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, str(os.getpid()).encode())
    os.close(fd)
    try:
        torch = cpu_setup()
        bound = plan["models"][method]
        run = Path(bound["run"])
        os.environ["AFDM_LSTMP_ROOT"] = str(ROOT)
        os.environ["AFDM_LSTMP_CONFIG"] = bound["config"]
        sys.path.insert(0, str(run / "source_code"))
        from experiments.lstmp_candidate_20261019 import common, data
        receiver = importlib.import_module("experiments." + bound["package"] + ".receiver")
        if common.OUT.resolve() != run.resolve():
            raise ValueError("Wrong frozen model/config imported")
        state = torch.load(bound["checkpoint"], map_location="cpu", weights_only=False, mmap=True)
        if state["depth"] != bound["depth"] or state["epoch"] != bound["selected_epoch"]:
            raise ValueError("Wrong checkpoint state")
        if method == NEW and state["manifest_sha256"] != bound["manifest_sha256"]:
            raise ValueError("Wrong checkpoint manifest")
        if method != NEW and state["scale"] != plan["scale"]:
            raise ValueError("Wrong historical checkpoint normalization")
        model = receiver.Receiver()
        for _ in range(bound["depth"]):
            model.add_layer(None)
        model.load_state_dict(state["state"], strict=True)
        del state
        model.eval()
        model.use_checkpoint = False
        if hasattr(model, "graphs_enabled"):
            model.graphs_enabled = False
        if any(p.device.type != "cpu" for p in model.parameters()):
            raise ValueError("Non-CPU model")
        score = scoring()
        write(folder / "BINDING.json", dict(**bound, torch=torch.__version__, device="cpu", threads=2,
            plan_sha256=sha(OUT / "PLAN.json"), optimizer_updates=0))

        def forward(i):
            with np.load(OUT / f"cases/{i:03d}/input.npz", allow_pickle=False) as z:
                values = dict(y=z["observation"], a=z["operator"], noise=z["noise_variance"], rho=z["activity_prior"])
            with torch.no_grad():
                start = time.perf_counter()
                public, _ = data.prepare_public(values, plan["scale"], "cpu", phase_mode="known", noise_mode="known")
                outputs, diagnostics = model(public)
                final = outputs[-1]
                x, logits = (final["estimate"], final["logits"]) if isinstance(final, dict) else final
                a = x.numpy()
                arrays = dict(estimate=(a[:, 0].astype(np.float64) + 1j * a[:, 1].astype(np.float64)) * plan["scale"],
                              probabilities=torch.sigmoid(logits).numpy())
                seconds = time.perf_counter() - start
            return arrays, diagnostics, seconds

        forward(0)
        for case in plan["cases"]:
            i = case["index"]
            if (folder / f"{i:03d}.json").exists():
                continue
            write(OUT / "STATUS.json", dict(stage="EVALUATING_CPU", method=method, scene=i + 1, total=20,
                  pid=os.getpid(), updated_unix=time.time()))
            arrays, diagnostics, seconds = forward(i)
            with np.load(OUT / f"cases/{i:03d}/truth.npz", allow_pickle=False) as truth:
                metrics = score(arrays["estimate"], arrays["probabilities"], truth["channel"], truth["activity"], threshold=.5)
            np.savez_compressed(folder / f"{i:03d}.npz", **arrays)
            write(folder / f"{i:03d}_trace.json", dict(diagnostics=diagnostics, iterations=bound["depth"]))
            write(folder / f"{i:03d}.json", dict(status="COMPLETE", case_index=i, seed=case["seed"],
                input_sha256=case["input_sha256"], prediction_sha256=sha(folder / f"{i:03d}.npz"), **metrics,
                iterations=bound["depth"], stopping_reason=f"FIXED_{bound['depth']}_LAYERS",
                recorded_receiver_seconds=seconds, device="cpu two threads"))
            print(json.dumps(dict(method=method, scene=i + 1, nmse_db=10 * np.log10(metrics["nmse"]),
                misses=metrics["misses"], false_alarms=metrics["false_alarms"])), flush=True)
        verify(plan)
        write(folder / "COMPLETE.json", dict(status="COMPLETE", scenes=20, gpu_used=False))
    except BaseException as error:
        write(OUT / f"FAILURE_{time.time_ns()}.json", dict(method=method, error=repr(error), traceback=traceback.format_exc()))
        raise
    finally:
        lock.unlink(missing_ok=True)


def report():
    plan = read(OUT / "PLAN.json")
    verify(plan)
    score = scoring()
    paired, summaries = {}, {}
    for m in METHODS:
        rows = []
        for case in plan["cases"]:
            i = case["index"]
            row = read(OUT / m / f"{i:03d}.json")
            if row["case_index"] != i or row["seed"] != case["seed"] or row["input_sha256"] != case["input_sha256"] or row["prediction_sha256"] != sha(OUT / m / f"{i:03d}.npz"):
                raise ValueError("Prediction binding mismatch")
            with np.load(OUT / m / f"{i:03d}.npz", allow_pickle=False) as pred:
                with np.load(OUT / f"cases/{i:03d}/truth.npz", allow_pickle=False) as truth:
                    metrics = score(pred["estimate"], pred["probabilities"], truth["channel"], truth["activity"], threshold=.5)
            for k, v in metrics.items():
                if not np.isclose(v, row[k], rtol=1e-12, atol=1e-12):
                    raise ValueError("Independent rescoring mismatch")
            rows.append(row)
        paired[m] = rows
        total = lambda k: sum(r[k] for r in rows)
        summaries[m] = dict(scenes=20, pooled_nmse_db=float(10 * np.log10(total("error_energy") / total("truth_energy"))),
            aer=(total("misses") + total("false_alarms")) / (total("active") + total("inactive")),
            missed_detection_rate=total("misses") / total("active"), false_alarm_rate=total("false_alarms") / total("inactive"),
            misses=total("misses"), false_alarms=total("false_alarms"), active=total("active"), inactive=total("inactive"),
            mean_recorded_seconds=total("recorded_receiver_seconds") / 20, mean_iterations=total("iterations") / 20,
            device=rows[0]["device"], converged_scenes=sum(r["stopping_reason"] == "CONVERGED" for r in rows))
    index = np.random.default_rng(plan["bootstrap"]["seed"]).integers(0, 20, (10000, 20))
    boot = {}
    for m, rows in paired.items():
        sums = lambda k: np.asarray([r[k] for r in rows])[index].sum(1)
        boot[m] = dict(pooled_nmse_db=10 * np.log10(sums("error_energy") / sums("truth_energy")),
            aer=(sums("misses") + sums("false_alarms")) / (sums("active") + sums("inactive")),
            missed_detection_rate=sums("misses") / sums("active"), false_alarm_rate=sums("false_alarms") / sums("inactive"))
    comparisons = {}
    for other in METHODS[1:]:
        delta = [dict(case_index=a["case_index"], nmse_db_delta=float(10*np.log10(a["nmse"]/b["nmse"])),
                      misses_delta=a["misses"]-b["misses"], false_alarms_delta=a["false_alarms"]-b["false_alarms"])
                 for a,b in zip(paired[NEW],paired[other])]
        comparisons[other] = dict(new_minus_reference={k: summaries[NEW][k]-summaries[other][k] for k in boot[NEW]},
            paired_95_percentile={k:np.quantile(boot[NEW][k]-boot[other][k],[.025,.975]).tolist() for k in boot[NEW]},
            lower_nmse_scenes=sum(x["nmse_db_delta"]<0 for x in delta), per_scene=delta)
    write(OUT / "SUMMARY.json", dict(status="COMPLETE", condition=plan["condition"], phase_mode="estimated", noise_mode="estimated",
        methods=summaries, comparisons=comparisons, scope=plan["scope"], timing=plan["timing"],
        legacy_configuration_difference=plan["previous_5db_reference_difference"]))
    for name, rows in (("summary.csv", [dict(method=m, **summaries[m]) for m in METHODS]),
                       ("per_scene.csv", [dict(method=m, **r) for m in METHODS for r in paired[m]])):
        with (OUT / name).open("w", encoding="utf-8-sig", newline="") as f:
            fields=list(dict.fromkeys(k for r in rows for k in r))
            w=csv.DictWriter(f,fields); w.writeheader(); w.writerows(rows)
    lines=["标准工况：新六层、此前七层/五层与旧三网络的20场景配对比较", "",
        "40用户、16导频、16天线、0 dB、活动抽样概率0.1；估计相位和噪声；门限0.5。",
        "直接使用正式收敛实验全部20个DFT物理场景，种子202610180400001至202610180400020。",
        "重新生成的观测/导频/先验逐数组哈希与历史输入一致，真值逐元素一致。复用相同估计相位，并核对估计噪声一致。",
        "旧三网络三份权重与上次5dB对比相同，但此处采用正式配置阻尼0.2，上次为0.1；场景、SNR和前端条件也不同。",
        "三条展开路线在CPU两线程上重新推断；旧三网络复用历史GPU FP32预测，TF32关闭。没有更新权重或调整门限。", "",
        "方法 | 信道NMSE/dB | AER | 漏检率 | 虚警率 | 漏检/虚警 | 平均原始记录秒数（不比较速度）"]
    for m,label in zip(METHODS,LABELS):
        s=summaries[m]
        lines.append(f"{label} | {s['pooled_nmse_db']:.4f} | {s['aer']:.3%} | {s['missed_detection_rate']:.3%} | {s['false_alarm_rate']:.3%} | {s['misses']}/{s['false_alarms']} | {s['mean_recorded_seconds']:.3f}")
    lines += ["", "六层减参考方法的差值及10000次配对场景重抽样95%描述性区间；负值表示误差下降。"]
    for other,label in zip(METHODS[1:],LABELS[1:]):
        c=comparisons[other]
        lines.append(f"相对{label}：NMSE较低{c['lower_nmse_scenes']}/20场景。")
        for k,v in c["new_minus_reference"].items():
            scale=1 if k=="pooled_nmse_db" else 100
            lo,hi=c["paired_95_percentile"][k]
            lines.append(f"  {k}: {v*scale:+.4f}，区间[{lo*scale:+.4f}, {hi*scale:+.4f}]，单位为dB或百分点。")
    lines += ["", "这是已有标准工况面板上的阶段性对比，不是独立确认；未依据本次结果选择模型、场景或门限。",
        "CPU/GPU后端差异未单独分离；历史GPU计时包含收敛观察器，当前CPU复用前端，不作速度排名。",
        "本结果不覆盖8导频端点，也不能将与上次5dB比较的差异只归因于SNR。层数、损失和训练分布的作用未分离。",
        "十层训练及其原冻结20场景比较保持不变。本次固定使用已完成六层的原验证选择。"]
    (OUT / "REPORT.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,2,figsize=(11.5,7.5),constrained_layout=True)
    for ax,key,title,mult in zip(axes.flat,("pooled_nmse_db","aer","missed_detection_rate","false_alarm_rate"),
        ("Channel NMSE (dB)","Activity error (%)","Missed detection (%)","False alarm (%)"),(1,100,100,100)):
        bars=ax.bar(("V3 six","Prior seven","Prior five","Legacy d=0.2"),[summaries[m][key]*mult for m in METHODS],
                    color=("#227C9D","#65A879","#9B80B4","#ED8B3A"))
        ax.bar_label(bars,fmt="%.3f",padding=3,fontsize=9)
        ax.set_title(title); ax.margins(y=.25); ax.grid(axis="y",alpha=.2); ax.set_axisbelow(True)
    fig.suptitle("Same 20 formal DFT scenes | K40 / Q16 / p0.1 / 0 dB | Estimated phase and noise\n"
                 "Unfolded models: CPU; legacy: saved GPU FP32 | Fixed weights and threshold 0.5",fontsize=11)
    fig.savefig(OUT / "comparison.png",dpi=180); fig.savefig(OUT / "comparison.pdf"); plt.close(fig)
    write(OUT / "RESULT_AUDIT.json",dict(status="PASSED", predictions_rescored=80, scene_counts=dict.fromkeys(METHODS,20),
        plan_sha256=sha(OUT / "PLAN.json"), summary_sha256=sha(OUT / "SUMMARY.json"), all_scenes_retained=True,
        same_observation_phase_and_noise=True, historical_predictions_unchanged=True, gpu_used_for_new_inference=False,
        original_ten_layer_plan_unchanged=sha(TEN/"PLAN.json")==TEN_SHA))
    write(OUT / "COMPLETE.json",dict(status="COMPLETE", completed_unix=time.time(), scene_counts=dict.fromkeys(METHODS,20),
        plan_sha256=sha(OUT/"PLAN.json"), summary_sha256=sha(OUT/"SUMMARY.json"), audit_sha256=sha(OUT/"RESULT_AUDIT.json")))
    write(OUT / "STATUS.json",dict(stage="COMPLETE",updated_unix=time.time()))
    print(json.dumps(dict(stage="COMPLETE",output=str(OUT))),flush=True)


def run_all():
    if (OUT / "COMPLETE.json").exists():
        print(json.dumps(dict(stage="ALREADY_COMPLETE")),flush=True)
        return
    lock=OUT/"RUNNING.lock"
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    os.write(fd,str(os.getpid()).encode()); os.close(fd)
    try:
        for method in METHODS[:-1]:
            subprocess.run([sys.executable,"-B",str(Path(__file__).resolve()),"--method",method],check=True)
        report()
    except BaseException as error:
        write(OUT/f"FAILURE_{time.time_ns()}.json",dict(error=repr(error),traceback=traceback.format_exc()))
        raise
    finally:
        lock.unlink(missing_ok=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare",action="store_true")
    mode.add_argument("--run",action="store_true")
    mode.add_argument("--method",choices=METHODS[:-1])
    mode.add_argument("--report",action="store_true")
    args=parser.parse_args()
    if args.prepare: prepare()
    elif args.run: run_all()
    elif args.method: evaluate(args.method)
    else: report()
