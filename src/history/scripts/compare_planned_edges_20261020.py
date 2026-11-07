"""Fresh paired checks at the two endpoints of the planned one-variable sweeps."""
import os
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "1"
import argparse
import gc
import importlib.util
from pathlib import Path
import shutil
import time
import traceback
import warnings
import numpy as np

ROOT = Path(r"C:\Users\25911\Desktop\afdm-gfra")
RUN = Path(r"D:\afdm-gfra-cpu\runs\lstmp_refinenet_depth7_20261020")
OUT = ROOT / "results/planned_edges_paired10_20261020"
HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("paired_seven", HERE / "evaluate_lstmp_depth7_threeway_20261020.py")
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)
C = G.C
read, write, sha = C.read, C.write, C.sha
METHODS = ("new_seven_layer", "legacy_50000_damping01")
GROUPS = dict(k100_q16=dict(users=100, frames=16, seed=202610201600001),
              k40_q8=dict(users=40, frames=8, seed=202610200800001))


def check_seeds(common, seeds):
    cfg = common.CONFIG["receiver"]
    for split in ("train", "validation", "test"):
        start = cfg[f"{split}_seed"]
        count = cfg.get("case_sources", {}).get(split, {}).get("pool_count", cfg[f"{split}_scenes"])
        assert not any(start <= seed < start+count for seed in seeds)
    prior = read(ROOT / "runs/proposed_50000_cuda_20261018/data/prior_definition.json")
    for identity in prior["dataset_identities"].values():
        assert not set(seeds).intersection(identity["scene_seeds"])


def prepare():
    if OUT.exists():
        raise FileExistsError(OUT)
    common, _, _ = C.modules(ROOT, RUN)
    assert G.readiness(RUN)[0]
    from threadpoolctl import threadpool_limits
    threadpool_limits(1)
    from afdm_jadcedd.experiment.generate import generate_case
    from afdm_jadcedd.system.pilot import PartialDFTPilot
    from afdm_jadcedd.system.observation import array_sha256
    from afdm_jadcedd.algorithm.unknown_phase_model import UnknownPhaseInput
    from afdm_jadcedd.algorithm.baselines.noise_estimation import estimate_spatial_noise
    from afdm_jadcedd.algorithm import phase_estimation_optimized as phase
    old = read(ROOT / "results/lstmp_epoch6_vs_legacy20_20261020/PLAN.json")
    controls = read(ROOT / "configs/proposed_frontend.json")["phase_estimation"]
    scale = old["scale"]
    check_seeds(common, [g["seed"]+i for g in GROUPS.values() for i in range(10)])
    OUT.mkdir()
    (OUT / "source").mkdir()
    for path in (Path(__file__), HERE / "evaluate_lstmp_depth7_threeway_20261020.py",
                 HERE / "evaluate_lstmp_epoch6_vs_legacy20.py"):
        shutil.copy2(path, OUT / "source" / path.name)
    design = dict(groups=GROUPS, scenes_per_group=10, snr_db=0., activity_probability=.1,
                  phase_mode="estimated", noise_mode="estimated", threshold=.5,
                  selection="Ten consecutive fresh seeds per group, fixed before generation or inference.",
                  created_unix=time.time())
    write(OUT / "DESIGN.json", design)
    cases = []
    for group, condition in GROUPS.items():
        for index in range(10):
            seed = condition["seed"] + index
            folder = OUT / "cases" / group / f"{index:03d}"
            folder.mkdir(parents=True)
            inputs, truth, metadata = generate_case(seed, 0., scale, users=condition["users"],
                                                    frames=condition["frames"], activity_probability=.1)
            pilot = PartialDFTPilot(condition["users"], condition["frames"], seed+10**12,
                                   input_size=16).dense().reshape(condition["frames"], condition["users"], 16)
            np.savez_compressed(folder / "public.npz", observation=inputs["observation"],
                                pilot=pilot, activity_prior=inputs["activity_prior"])
            # Truth and ideal operator are preserved for scoring/provenance only.
            np.savez_compressed(folder / "truth.npz", **truth,
                                true_noise_variance=inputs["noise_variance"], true_operator=inputs["operator"])
            write(folder / "generation.json", metadata)
            del inputs, truth
            public = dict(np.load(folder / "public.npz"))
            assert set(public) == {"observation", "pilot", "activity_prior"}
            started = time.perf_counter()
            with warnings.catch_warnings(record=True) as notices:
                warnings.simplefilter("always", RuntimeWarning)
                noise, noise_record = estimate_spatial_noise(public["observation"])
                unknown = UnknownPhaseInput(public["observation"], public["pilot"], noise,
                                            float(public["activity_prior"]))
                fitted, phase_record = phase.estimate(unknown, phase.Controls(**controls))
                conditional = unknown.at_estimated_phase(fitted["phase_slopes"])
            np.savez_compressed(folder / "input.npz", **conditional.arguments())
            np.savez_compressed(folder / "phase.npz", **fitted)
            frontend = dict(phase_mode="estimated", noise_mode="estimated",
                            truth_used_in_inference=False, noise=noise_record, phase=phase_record,
                            seconds=time.perf_counter()-started,
                            warnings=[str(w.message) for w in notices],
                            public_arrays={k:array_sha256(v) for k,v in public.items()},
                            conditional_arrays={k:array_sha256(v) for k,v in conditional.arguments().items()})
            write(folder / "frontend.json", frontend)
            case = dict(group=group,index=index,seed=seed,folder=str(folder),
                        files={p.name:sha(p) for p in folder.iterdir() if p.is_file()})
            cases.append(case)
            write(OUT / "PREPARATION.json", dict(completed=len(cases),expected=20,cases=cases))
            print(f"Prepared {group} {index+1}/10; shared estimated phase/noise",flush=True)
    plan = dict(**design,root=str(ROOT),training_run=str(RUN),methods=list(METHODS),
                scale=scale,old_binding=old["old_binding"],
                new_checkpoint="checkpoints/depth_7/best.pt",
                checkpoint_sha256=sha(RUN / "checkpoints/depth_7/best.pt"),
                training_manifest_sha256=sha(RUN / "MANIFEST.json"),
                new_microbatch=common.CONFIG["receiver"]["microbatch"], cases=cases,
                frontend_controls=controls, frontend_signature=phase.signature(phase.Controls(**controls)),
                source_hashes={str(p):sha(p) for p in (OUT / "source").glob("*.py")},
                limitations="Ten fresh physical scenes per condition; no retuning. Seven-layer weights trained with known phase/noise are evaluated unchanged with estimated inputs. Existing GPU training continues; timings are not an isolated speed comparison.",
                dispatch="One group per worker, disjoint outputs; shared cached frontend per case.")
    write(OUT / "PLAN.json", plan)


def verify(plan):
    for path,digest in plan["source_hashes"].items():
        assert sha(path) == digest, path
    assert sha(RUN / "MANIFEST.json") == plan["training_manifest_sha256"]
    assert sha(RUN / plan["new_checkpoint"]) == plan["checkpoint_sha256"]
    manifest = read(RUN / "MANIFEST.json")
    for path,digest in manifest["snapshot_hashes"].items():
        assert sha(path) == digest, path
    cfg = plan["old_binding"]["applied_configuration"]
    for key in ("first_checkpoint","second_checkpoint","evidence_checkpoint"):
        assert sha(ROOT / cfg[key]) == cfg[key+"_sha256"]


def run(group):
    import torch
    from threadpoolctl import threadpool_limits
    torch.set_num_threads(1)
    threadpool_limits(1)
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    plan = read(OUT / "PLAN.json")
    verify(plan)
    common,data,receiver = C.modules(ROOT,RUN)
    from afdm_jadcedd.system.observation import ReceiverInput
    status_path = OUT / f"STATUS_{group}.json"
    for method in METHODS:
        adapter = G.Adapter(method,plan,common,data,receiver)
        for case in [c for c in plan["cases"] if c["group"] == group]:
            folder = Path(case["folder"])
            for name,digest in case["files"].items():
                assert sha(folder/name) == digest, str(folder/name)
            target = OUT / method / group / f'{case["index"]:03d}'
            target.parent.mkdir(parents=True,exist_ok=True)
            if target.with_suffix(".json").exists():
                continue
            public = ReceiverInput(**dict(np.load(folder/"input.npz")))
            write(status_path,dict(stage="RUNNING",group=group,method=method,index=case["index"],
                                   pid=os.getpid(),updated_unix=time.time()))
            with warnings.catch_warnings(record=True) as notices:
                warnings.simplefilter("always",RuntimeWarning)
                predictions,record,times = C.timed_inference(adapter,public)
            truth = dict(np.load(folder/"truth.npz"))
            metrics = C.score_arrays(predictions["estimate"],predictions["probabilities"],
                                    truth["channel"],truth["activity"])
            np.savez_compressed(target.with_suffix(".npz"),**predictions)
            record.update(public_phase_mode="estimated",public_noise_mode="estimated",
                          shared_frontend=str(folder/"frontend.json"),truth_used_in_inference=False,
                          warnings=[str(w.message) for w in notices])
            write(target.with_suffix(".record.json"),record)
            row = dict(status="COMPLETE",group=group,index=case["index"],seed=case["seed"],
                       **metrics,iterations=record["iterations"],converged=record.get("converged"),
                       stopping_reason=record.get("stopping_reason"),times=times,
                       zero_output=bool(np.count_nonzero(predictions["estimate"]) == 0),
                       predicted_active=int((predictions["probabilities"] >= .5).sum()),
                       input_sha256=case["files"]["input.npz"],
                       prediction_sha256=sha(target.with_suffix(".npz")))
            write(target.with_suffix(".json"),row)
            print(f'{group} {method} {case["index"]+1}/10: NMSE={10*np.log10(metrics["nmse"]):.4f}dB MD={metrics["misses"]} FA={metrics["false_alarms"]}',flush=True)
        del adapter
        gc.collect()
        torch.cuda.empty_cache()
    write(status_path,dict(stage="COMPLETE",group=group,updated_unix=time.time(),predictions=20))


def aggregate(rows):
    total = lambda k:sum(r[k] for r in rows)
    e,t = total("error_energy"),total("truth_energy")
    a,n = total("active"),total("inactive")
    return dict(scenes=len(rows),pooled_nmse_db=float(10*np.log10(e/t)),
                active_nmse_db=float(10*np.log10(total("active_error_energy")/t)),
                mean_scene_nmse_db=float(10*np.log10(np.mean([r["nmse"] for r in rows]))),
                misses=total("misses"),false_alarms=total("false_alarms"),active=a,inactive=n,
                aer=(total("misses")+total("false_alarms"))/(a+n),md=total("misses")/a,fa=total("false_alarms")/n,
                converged=sum(r["converged"] is True for r in rows),zero_outputs=total("zero_output"),
                mean_iterations=float(np.mean([r["iterations"] for r in rows])))


def summarize():
    plan = read(OUT / "PLAN.json")
    verify(plan)
    results,rows_all = {},{}
    for group in GROUPS:
        assert read(OUT/f"STATUS_{group}.json")["stage"] == "COMPLETE"
        results[group],rows_all[group] = {},{}
        for method in METHODS:
            rows = []
            for case in [c for c in plan["cases"] if c["group"] == group]:
                stem = OUT/method/group/f'{case["index"]:03d}'
                row = read(stem.with_suffix(".json"))
                assert row["seed"] == case["seed"]
                assert sha(stem.with_suffix(".npz")) == row["prediction_sha256"]
                assert sha(Path(case["folder"])/"input.npz") == row["input_sha256"]
                pred = dict(np.load(stem.with_suffix(".npz")))
                truth = dict(np.load(Path(case["folder"])/"truth.npz"))
                # Independent direct-array recomputation, including inactive-user error.
                err = np.abs(pred["estimate"].astype(np.complex128)-truth["channel"].astype(np.complex128))**2
                power = np.abs(truth["channel"].astype(np.complex128))**2
                active = truth["activity"].astype(bool)
                decision = pred["probabilities"] >= .5
                assert np.isfinite(err).all() and np.isfinite(pred["probabilities"]).all()
                for key,value in dict(error_energy=err.sum(),truth_energy=power.sum(),
                                      active_error_energy=err[active].sum(),
                                      misses=int((active & ~decision).sum()),
                                      false_alarms=int((~active & decision).sum())).items():
                    assert np.isclose(value,row[key],rtol=1e-12,atol=1e-12),key
                rows.append(row)
            results[group][method] = aggregate(rows)
            rows_all[group][method] = rows
    write(OUT/"SUMMARY.json",dict(status="COMPLETE",groups=results,limitations=plan["limitations"]))
    write(OUT/"AUDIT.json",dict(status="PASSED",predictions=40,paired_shared_inputs=True,
                               direct_array_rescoring=True,weights_unchanged=True))
    lines = ["# 正式扫描端点：旧三网络与七层的配对比较","",
             "每个条件10个独立新场景，SNR=0 dB、活动采样概率0.1。相位与噪声均从观测估计；"
             "两算法共享同一份前端输出。旧算法为50k权重、0.1阻尼、最多600轮；七层使用既有选中权重。","",
             "| 条件 | 方法 | NMSE/dB | 活跃用户误差/dB | AER | 漏检率 | 虚警率 | 漏检/虚警 |",
             "|---|---|---:|---:|---:|---:|---:|---:|"]
    for group in GROUPS:
        for method,name in zip(METHODS,("七层","旧三网络")):
            s=results[group][method]
            lines.append(f'| {group} | {name} | {s["pooled_nmse_db"]:.4f} | {s["active_nmse_db"]:.4f} | {s["aer"]:.2%} | {s["md"]:.2%} | {s["fa"]:.2%} | {s["misses"]}/{s["false_alarms"]} |')
    lines += ["","NMSE按累计误差能量与累计真值能量之比计算，包括非活跃用户误差。活动判决门限固定0.5。"
              "40份完整预测均经独立数组重评分；没有按结果删除场景、改变门限或重选权重。",
              "七层原训练采用已知相位和噪声，本次检验其直接用于估计前端的效果，未重新训练。"
              "每条件仅10场景，不能代替正式500场景结论。现有GPU训练继续运行，耗时不用于速度比较。"]
    (OUT/"REPORT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,3,figsize=(11,3.6))
    x=np.arange(2)
    for m,method in enumerate(METHODS):
        for ax,key,title,scale in zip(axes,("pooled_nmse_db","md","fa"),
                                     ("Channel NMSE (dB)","Missed detection (%)","False alarm (%)"),(1,100,100)):
            ax.bar(x+(m-.5)*.35,[results[g][method][key]*scale for g in GROUPS],width=.35,
                   label=("7-layer","Three-network")[m],color=("#167d8d","#c85c38")[m])
            ax.set_xticks(x,["K=100, Q=16","K=40, Q=8"])
            ax.set_title(title)
            ax.grid(axis="y",alpha=.2)
    axes[0].legend(fontsize=8)
    fig.suptitle("10 fresh paired scenes per condition | SNR=0 dB, p=0.1\nEstimated phase and noise; frozen weights and threshold",fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT/"comparison.png",dpi=180)
    print(results,flush=True)


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=("prepare","run","summarize"))
    parser.add_argument("--group",choices=GROUPS)
    args=parser.parse_args()
    try:
        if args.action == "prepare": prepare()
        elif args.action == "summarize": summarize()
        else:
            assert args.group
            run(args.group)
    except Exception:
        if OUT.exists():
            write(OUT/f"FAILURE_{args.group or args.action}.json",
                  dict(time=time.time(),traceback=traceback.format_exc()))
        raise
