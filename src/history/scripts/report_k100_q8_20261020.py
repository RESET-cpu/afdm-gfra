"""Describe paired recovery and message diagnostics; never alter predictions."""
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/k100_q8_legacy_vs_seven_20_20261020"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    plan = read(OUT / "PLAN.json")
    assert read(OUT / "AUDIT.json")["status"] == "PASSED"
    summary = read(OUT / "SUMMARY.json")
    methods = plan["methods"]
    all_rows, diagnostics, replay = {}, [], []
    for method in methods:
        rows = []
        for case in plan["cases"]:
            stem = OUT / method / f'{case["index"]:03d}'
            row = read(stem.with_suffix(".json"))
            pred = dict(np.load(stem.with_suffix(".npz")))
            row["zero_estimate"] = bool(np.count_nonzero(pred["estimate"]) == 0)
            row["predicted_active"] = int((pred["probabilities"] >= .5).sum())
            rows.append(row)
            if method == "legacy_50000_damping01":
                record = read(stem.with_suffix(".record.json"))
                trace = record["trace"]
                vs = np.array([r["query_variance_min"] for r in trace])
                unsupported = sum(r["unsupported_users"] > 0 for r in trace)
                diagnostics.append(dict(seed=row["seed"], snr=row["snr"],
                    zero_estimate=row["zero_estimate"], predicted_active=row["predicted_active"],
                    iterations=row["iterations"], converged=row["converged"],
                    unsupported_iterations=unsupported,
                    rejected_site_iterations=sum(r["rejected_site_users"] > 0 for r in trace),
                    reused_site_iterations=record["reused_site_iterations"],
                    initial_query_variance=float(vs[0]), final_query_variance=float(vs[-1]),
                    min_query_variance=float(vs.min()), max_query_variance=float(vs.max())))
            else:
                saved = case["saved_seven"]
                replay.append(dict(seed=row["seed"], snr=row["snr"],
                    nmse_db_difference=float(10*np.log10(row["nmse"]/saved["nmse"])),
                    misses_difference=row["misses"]-saved["misses"],
                    false_alarm_difference=row["false_alarms"]-saved["false_alarms"]))
        all_rows[method] = rows
    rng = np.random.default_rng(202610201008)
    groups = [[i for i,c in enumerate(plan["cases"]) if c["snr"] == snr]
              for snr in (-5.,0.,5.,10.)]
    indices = np.concatenate([rng.choice(ids, size=(10000,len(ids))) for ids in groups], axis=1)
    def stats(rows):
        total = lambda k: np.array([r[k] for r in rows])[indices].sum(1)
        return dict(nmse_db=10*np.log10(total("error_energy")/total("truth_energy")),
                    aer=(total("misses")+total("false_alarms"))/(total("active")+total("inactive")),
                    md=total("misses")/total("active"), fa=total("false_alarms")/total("inactive"))
    new, old = [stats(all_rows[m]) for m in methods]
    difference = {k: np.quantile(new[k]-old[k],[.025,.975]).tolist() for k in new}
    result = dict(status="COMPLETE", legacy_diagnostics=diagnostics,
        seven_replay_differences=replay,
        new_lower_nmse_scenes=sum(a["nmse"] < b["nmse"] for a,b in zip(*[all_rows[m] for m in methods])),
        legacy_zero_output_scenes=sum(r["zero_estimate"] for r in diagnostics),
        legacy_all_inactive_decisions=sum(r["predicted_active"] == 0 for r in diagnostics),
        paired_stratified_scene_bootstrap_95_percent_new_minus_old=difference,
        interval_scope="Descriptive, within this revealed 20-case development subset; no training-seed or selection correction.")
    (OUT / "DIAGNOSTICS.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1,3,figsize=(12,3.8))
    snrs = [-5,0,5,10]
    for method, label, color in zip(methods,("Trained 7-layer","Three-network, 600 max"),("#167d8d","#c85c38")):
        groups = summary["methods"][method]["by_snr"]
        for ax,key,title,scale in zip(axes,("pooled_nmse_db","md","fa"),
                                     ("Channel NMSE (dB)","Missed detection (%)","False alarm (%)"),(1,100,100)):
            ax.plot(snrs,[groups[str(float(s))][key]*scale for s in snrs],marker="o",
                    label=label,color=color,lw=2)
            ax.set(title=title,xlabel="SNR (dB)",xticks=snrs)
            ax.grid(alpha=.25)
    axes[0].legend(fontsize=8)
    fig.suptitle("K=100, Q=8, activity p=0.1 | 5 paired development scenes per SNR\nKnown phase and noise; fixed checkpoints and threshold 0.5",fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "comparison.png",dpi=180)
    plt.close(fig)
    text = "\n## 反馈与复算核对\n\n"
    text += f'旧算法有 {result["legacy_zero_output_scenes"]}/20 场景输出严格全零信道，'
    text += f'{result["legacy_all_inactive_decisions"]}/20 场景判定全部用户不活跃。'
    text += f'七层在 {result["new_lower_nmse_scenes"]}/20 场景的NMSE较低。\n\n'
    text += ("逐场景的查询范围、超范围轮数、消息拒绝及停止原因见 DIAGNOSTICS.json。"
             "这些轨迹说明发生了哪些更新，不能单独证明更换某个模块就能修复。\n\n")
    text += f'七层重新推断与原验证记录的单场景NMSE最大绝对差为 {max(abs(r["nmse_db_difference"]) for r in replay):.6f} dB，'
    text += f'漏检计数差的绝对值合计 {sum(abs(r["misses_difference"]) for r in replay)}，'
    text += f'虚警计数差的绝对值合计 {sum(abs(r["false_alarm_difference"]) for r in replay)}。'
    text += "当前比较全部采用本次复算值，未混合挑选历史较优值；没有宣称逐位重现，也未定位该数值差异的来源。\n\n"
    text += ("按SNR分层、场景配对的10000次bootstrap描述性区间见DIAGNOSTICS.json；"
             "每档仅5场景，不能作为总体或未见条件的显著性结论。\n")
    report = OUT / "REPORT.md"
    report.write_text(report.read_text(encoding="utf-8")+text,encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k not in ("legacy_diagnostics","seven_replay_differences")}))


if __name__ == "__main__":
    main()
