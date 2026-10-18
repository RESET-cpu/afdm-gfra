"""Report existing full-user AMP results without selecting settings or running inference."""
from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_comparison import ROOT, DEST, RUN, METHODS, SNRS, read, save, sha256, summarize

NAMES = {"joint_amp": "完整用户联合 score AMP", "proposed": "原 Proposed", "diffusion_amp": "原逐波束 score AMP"}
PLOT_NAMES = {"joint_amp": "Full-user score AMP", "proposed": "Original Proposed", "diffusion_amp": "Per-beam score AMP"}
COLORS = {"joint_amp": "#16826c", "proposed": "#2860b7", "diffusion_amp": "#b16a30"}
MARKERS = {"joint_amp": "o", "proposed": "s", "diffusion_amp": "^"}
MC_FIELDS = ("correction_mc_se_over_residual", "correction_norm_over_residual", "mc_se_over_correction_norm")
MC_NAMES = ("探针标准误差 / ‖Z‖", "估计校正幅度 / ‖Z‖", "探针标准误差 / 估计校正幅度")


def fmt(value, digits=3):
    return "—" if value is None else f"{value:.{digits}f}"


def percent(value):
    return "—" if value is None else f"{100 * value:.3f}%"


def mc_distribution(rows, expected):
    result = {}
    for field in MC_FIELDS:
        values = np.array([row[field] for row in rows if row.get(field) is not None], dtype=float)
        result[field] = dict(count=len(values), expected=expected, unavailable=expected - len(values),
                             mean=float(values.mean()) if len(values) else None,
                             median=float(np.median(values)) if len(values) else None,
                             p95=float(np.percentile(values, 95, method="linear")) if len(values) else None,
                             max=float(values.max()) if len(values) else None)
    return result


def onsager_mc_analysis():
    """Read joint AMP's native trace only, including saved steps of failed cases."""
    path = RUN / "test/joint_amp_ROWS.json"
    rows = read(path) if path.exists() else []
    sources = {str(path.relative_to(ROOT)): sha256(path)} if path.exists() else {}
    cases, points = [], []
    for row in rows:
        path = (ROOT / row["output"]).parent / "TRACE.json"
        trace = read(path).get("rows", []) if path.exists() else []
        if path.exists():
            sources[str(path.relative_to(ROOT))] = sha256(path)
        case = {key: row[key] for key in ("scene", "seed", "snr_db", "status")}
        observed, issues, values = [], [], {}
        for point in trace:
            iteration = point.get("iteration")
            if type(iteration) is not int or not 1 <= iteration <= 12:
                issues.append(f"Invalid or out-of-range iteration: {iteration}")
                continue
            observed.append(iteration)
            item = dict(iteration=iteration, unavailable_reasons={})
            for field in MC_FIELDS[:2]:
                value = point.get(field)
                valid = isinstance(value, (int, float)) and np.isfinite(value) and value >= 0
                item[field] = float(value) if valid else None
                if not valid:
                    item["unavailable_reasons"][field] = "Missing, nonfinite, or negative native diagnostic"
            se, norm = (item[field] for field in MC_FIELDS[:2])
            ratio = se / norm if se is not None and norm is not None and norm > 0 else None
            item[MC_FIELDS[2]] = ratio if ratio is not None and np.isfinite(ratio) else None
            if item[MC_FIELDS[2]] is None:
                item["unavailable_reasons"][MC_FIELDS[2]] = "Both native fields must be finite and correction norm must be positive"
            values[iteration] = item
        duplicates = sorted({iteration for iteration in observed if observed.count(iteration) > 1})
        for iteration in duplicates:
            values.pop(iteration)
            issues.append(f"Duplicate iteration has no unambiguous diagnostic: {iteration}")
        for iteration, item in sorted(values.items()):
            points.append(dict(case, **item))
        missing = sorted(set(range(1, 13)) - set(values))
        distribution = mc_distribution(list(values.values()), 12)
        case.update(trace_available=path.exists(), missing_iterations=missing, issues=issues,
                    complete_native_fields=not missing and not issues
                    and all(distribution[field]["count"] == 12 for field in MC_FIELDS[:2]),
                    distribution=distribution, rows=list(values.values()))
        cases.append(case)
    overall = mc_distribution(points, 24 * 12)
    complete = (len(cases) == 24 and all(case["status"] == "COMPLETE" and case["complete_native_fields"]
                                       for case in cases))
    by_iteration = {str(iteration): dict(
        overall=mc_distribution([point for point in points if point["iteration"] == iteration], 24),
        by_snr={str(snr): mc_distribution([point for point in points if point["iteration"] == iteration
                                          and point["snr_db"] == snr], 8) for snr in SNRS})
        for iteration in range(1, 13)}
    return dict(schema="joint-amp-onsager-mc-descriptive-v1",
                status="COMPLETE" if complete else ("PARTIAL" if points else "UNAVAILABLE"),
                method="joint_amp", expected_cases=24, attempted_cases=len(cases),
                native_complete_cases=sum(case["status"] == "COMPLETE" for case in cases),
                native_failed_cases=sum(case["status"] != "COMPLETE" for case in cases),
                cases_with_complete_native_fields=sum(case["complete_native_fields"] for case in cases),
                overall=overall, cases=cases, by_iteration=by_iteration,
                by_snr={str(snr): mc_distribution([point for point in points if point["snr_db"] == snr], 8 * 12)
                        for snr in SNRS}, source_sha256=sources,
                definitions={MC_FIELDS[0]: "Estimated Frobenius standard error of the probe mean ZB, divided by max(||Z||_F, 1e-30)",
                             MC_FIELDS[1]: "Frobenius norm of the estimated mean ZB, divided by max(||Z||_F, 1e-30)",
                             MC_FIELDS[2]: "Per-row first native diagnostic / second native diagnostic, only for positive denominator"},
                scope="Fixed-query probe sample standard error; not bias, AWGN, state-evolution, or convergence validation",
                pooling="Equal weight for each available case-iteration; rounds and SNRs are not independent samples; p95 uses linear interpolation",
                failed_cases="All available saved diagnostics retained regardless of native completion; missing fields/iterations remain unavailable",
                selection_use=False, truth_read=False,
                other_methods="No diagnostics are inferred for algorithms without these native fields")


def plot(summary):
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8), constrained_layout=True)
    for method in METHODS:
        by_snr = summary["methods"][method]["by_snr"]
        nmse = [by_snr[str(snr)]["nmse_db"] for snr in SNRS]
        activity = [100 * by_snr[str(snr)]["activity_error_rate"] for snr in SNRS]
        for axis, values in zip(axes[:2], (nmse, activity)):
            axis.plot(SNRS, values, label=PLOT_NAMES[method], color=COLORS[method],
                      marker=MARKERS[method], linewidth=1.8)
            axis.set_xlabel("Received SNR (dB)")
            axis.set_xticks(SNRS)
            axis.grid(alpha=.25)
    axes[0].set_ylabel("Pooled full-channel NMSE (dB)")
    axes[0].axhline(0., color="#777777", linestyle=":", linewidth=1.)
    axes[0].legend(fontsize=8)
    axes[1].set_ylabel("Activity error rate (%)")
    axes[1].set_ylim(bottom=0)
    seconds = [summary["methods"][method]["overall"].get("mean_seconds") for method in METHODS]
    if all(value is not None for value in seconds):
        axes[2].bar(np.arange(3), seconds, color=[COLORS[method] for method in METHODS], width=.65)
        for index, value in enumerate(seconds):
            axes[2].text(index, value, f"{value:.1f}", ha="center", va="bottom", fontsize=9)
        axes[2].set_ylim(0, max(seconds) * 1.15 if max(seconds) > 0 else 1)
    else:
        axes[2].text(.5, .5, "Native receiver timing unavailable", transform=axes[2].transAxes,
                     ha="center", va="center")
    axes[2].set_xticks(np.arange(3), ["Full-user\nscore AMP", "Proposed", "Per-beam\nscore AMP"])
    axes[2].set_ylabel("Mean receiver time (s)")
    axes[2].grid(axis="y", alpha=.25)
    axes[2].set_axisbelow(True)
    fig.suptitle("Independent AFDM comparison: 8 physical scenes, 3 paired SNRs", fontsize=12)
    fig.savefig(RUN / "comparison.png", dpi=180)
    fig.savefig(RUN / "comparison.pdf")
    plt.close(fig)


def iteration_analysis(summary):
    """Use saved raw errors only; neither missing states nor iteration zero are inferred."""
    if summary["status"] != "COMPLETE":
        return dict(status="UNAVAILABLE", reason="Three complete methods are required")
    methods, curves, sources = {}, {}, {}
    for method in METHODS:
        rows_path = RUN / "test" / f"{method}_ROWS.json"
        rows = read(rows_path)
        sources[str(rows_path.relative_to(ROOT))] = sha256(rows_path)
        cases, observations = [], {}
        for row in rows:
            path = (ROOT / row["output"]).parent / "ITERATION_METRICS.json"
            expected = 12 if method != "proposed" else int(row.get("iterations") or 0)
            values, issues, duplicates = {}, [], set()
            if row["status"] != "COMPLETE":
                issues.append("Native receiver did not complete")
            elif not path.exists():
                issues.append("Saved iteration metrics are unavailable")
            else:
                sources[str(path.relative_to(ROOT))] = sha256(path)
                for point in read(path).get("rows", []):
                    iteration = point.get("iteration")
                    error, energy = point.get("full_error"), point.get("signal_energy")
                    if (not isinstance(iteration, int) or iteration < 1
                            or not isinstance(error, (int, float)) or not np.isfinite(error) or error < 0
                            or not isinstance(energy, (int, float)) or not np.isfinite(energy) or energy <= 0):
                        issues.append(f"Invalid saved iteration point: {iteration}")
                        continue
                    if iteration in values:
                        duplicates.add(iteration)
                    values[iteration] = dict(full_error=error, signal_energy=energy,
                                            nmse_db=float(10 * np.log10(max(error / energy, np.finfo(float).tiny))))
                for iteration in sorted(duplicates):
                    values.pop(iteration)
                    issues.append(f"Duplicate iteration removed from analysis: {iteration}")
            missing = sorted(set(range(1, expected + 1)) - set(values))
            extra = sorted(set(values) - set(range(1, expected + 1)))
            complete_trace = expected > 0 and not missing and not extra and not issues
            adjacent = [dict(from_iteration=i, to_iteration=i + 1,
                             rise_db=values[i + 1]["nmse_db"] - values[i]["nmse_db"])
                        for i in sorted(values) if i + 1 in values]
            positive = [point for point in adjacent if point["rise_db"] > 0]
            worst = max(positive, key=lambda item: item["rise_db"]) if positive else None
            case = {key: row[key] for key in ("scene", "seed", "snr_db")}
            case.update(expected_iterations=expected, observed_iterations=sorted(values),
                        complete_trajectory=complete_trace, missing_iterations=missing,
                        extra_iterations=extra, issues=issues,
                        adjacent_steps=len(adjacent), positive_steps=len(positive),
                        max_single_step_rise_db=worst["rise_db"] if worst else (0. if adjacent else None),
                        largest_rise_step=worst,
                        final_minus_best_db=(values[expected]["nmse_db"] - min(p["nmse_db"] for p in values.values()))
                        if complete_trace else None,
                        final_trace_minus_native_nmse_db=(values[expected]["nmse_db"] - row["metrics"]["nmse_db"])
                        if expected in values else None)
            cases.append(case)
            observations[(row["scene"], row["snr_db"])] = values
        with_steps = [case for case in cases if case["adjacent_steps"]]
        with_complete_trace = [case for case in cases if case["complete_trajectory"]]
        worst = max(with_steps, key=lambda item: item["max_single_step_rise_db"]) if with_steps else None
        worst_final = max(with_complete_trace, key=lambda item: item["final_minus_best_db"]) if with_complete_trace else None
        location = lambda case: {key: case[key] for key in ("scene", "seed", "snr_db")} if case else None
        methods[method] = dict(expected_trajectories=24, complete_trajectories=len(with_complete_trace),
                               cases_with_observed_adjacent_steps=len(with_steps),
                               cases_with_positive_steps=sum(case["positive_steps"] > 0 for case in cases),
                               observed_adjacent_steps=sum(case["adjacent_steps"] for case in cases),
                               observed_positive_steps=sum(case["positive_steps"] for case in cases),
                               max_single_step_rise_db=worst["max_single_step_rise_db"] if worst else None,
                               max_single_step_rise_location=location(worst),
                               max_single_step_rise_iterations=worst["largest_rise_step"] if worst else None,
                               max_final_minus_best_db=worst_final["final_minus_best_db"] if worst_final else None,
                               max_final_minus_best_location=location(worst_final), cases=cases)
        if method != "proposed":
            curves[method] = {}
            for snr in SNRS:
                points = []
                for iteration in range(1, 13):
                    current = [observations.get((scene, snr), {}).get(iteration) for scene in range(8)]
                    available = [point for point in current if point is not None]
                    error = sum(point["full_error"] for point in available) if len(available) == 8 else None
                    energy = sum(point["signal_energy"] for point in available) if len(available) == 8 else None
                    points.append(dict(iteration=iteration, observed_scenes=len(available),
                                       full_error=error, signal_energy=energy,
                                       nmse_db=float(10 * np.log10(max(error / energy, np.finfo(float).tiny)))
                                       if error is not None else None))
                curves[method][str(snr)] = points
    missing_points = sum(point["nmse_db"] is None for data in curves.values()
                         for points in data.values() for point in points)
    return dict(status="COMPLETE" if all(value["complete_trajectories"] == 24 for value in methods.values()) else "PARTIAL",
                curves_status="COMPLETE" if missing_points == 0 else "PARTIAL",
                missing_curve_points=missing_points, curves=curves, methods=methods, source_sha256=sources,
                scope="Descriptive saved trajectories; no inference of missing states or convergence guarantee",
                curve_definition="At each AMP iteration and SNR, sum squared error / sum signal energy across all 8 scenes, then 10 log10",
                rise_definition="NMSE(t+1)-NMSE(t)>0 on an observed adjacent pair; no gap bridging or iteration-zero insertion",
                proposed_reference="Final pooled Proposed NMSE only, not a same-iteration result")


def plot_iterations(summary, analysis):
    if summary["status"] != "COMPLETE" or analysis["status"] == "UNAVAILABLE":
        return False
    fig, axes = plt.subplots(1, 3, figsize=(12, 4), constrained_layout=True, sharey=True)
    for axis, snr in zip(axes, SNRS):
        missing = 0
        for method in ("joint_amp", "diffusion_amp"):
            points = analysis["curves"][method][str(snr)]
            values = [point["nmse_db"] if point["nmse_db"] is not None else np.nan for point in points]
            missing += sum(point["nmse_db"] is None for point in points)
            axis.plot([point["iteration"] for point in points], values, label=PLOT_NAMES[method],
                      color=COLORS[method], marker=MARKERS[method], markersize=4, linewidth=1.6)
        final = summary["methods"]["proposed"]["by_snr"][str(snr)]["nmse_db"]
        axis.axhline(final, color=COLORS["proposed"], linestyle="--", linewidth=1.6,
                     label="Original Proposed (final only)")
        axis.set_title(f"Received SNR = {snr} dB")
        axis.set_xlabel("AMP iteration")
        axis.set_xticks([1, 3, 6, 9, 12])
        axis.set_xlim(.7, 12.3)
        axis.grid(alpha=.25)
        if missing:
            axis.text(.03, .03, f"{missing} pooled points unavailable", transform=axis.transAxes,
                      va="bottom", fontsize=8, color="#8c3e25")
    axes[0].set_ylabel("Pooled full-channel NMSE (dB)")
    axes[0].legend(fontsize=8)
    fig.suptitle("Eight paired scenes; Proposed dashed line is a final reference, not a same-iteration result", fontsize=11)
    fig.savefig(RUN / "iterations.png", dpi=180)
    fig.savefig(RUN / "iterations.pdf")
    plt.close(fig)
    return True


def main():
    summary = summarize()
    onsager_mc = onsager_mc_analysis()
    save(RUN / "ONSAGER_MC_DIAGNOSTICS.json", onsager_mc)
    rows = []
    for method in METHODS:
        for snr in SNRS:
            rows.append(dict(method=method, snr_db=snr, **summary["methods"][method]["by_snr"][str(snr)]))
    columns = sorted({key for row in rows for key in row})
    with (RUN / "STATISTICS.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    complete = summary["status"] == "COMPLETE"
    selection_path = RUN / "solver_validation/SELECTION.json"
    selection = read(selection_path) if selection_path.exists() else None
    config_path = RUN / "FROZEN_CONFIG.json"
    config = read(config_path) if config_path.exists() else None
    lines = ["# 完整用户联合 score AMP：独立比较", "",
             "本报告仅汇总当前已保存的原始输出；不选择或调整网络、求解器和活动阈值。", "",
             f"当前状态：**{'三方法完整比较已完成' if complete else '实验尚未形成三方法完整比较'}**。", "",
             "新方法、原 Proposed 和此前的逐波束 score AMP 使用同一批四字段公开输入。"
             "新模型从头训练，不复用旧模型权重。原算法和历史结果由主任务单独核对保护。", "",
             "## 数据与验证", "",
             "验证使用 4 个物理场景 × 3 个 SNR；独立测试使用另 8 个物理场景 × 3 个 SNR。"
             "同一场景的信道、导频和标准化热噪声跨 SNR 配对。既有训练/验证样本的场景身份已单独核对；"
             "所有真值在接收机返回之后才进入外部评分。", "",
             "[预先固定的方案](../../experiments/joint_amp_20261015/PROTOCOL.md) · "
             "[身份核查](comparison_v1/IDENTITY_AUDIT.json) · "
             "[逐输入记录](comparison_v1/test) · [统计汇总](comparison_v1/SUMMARY.json)", ""]
    if selection:
        lines += ["| 验证候选 | 完成/输入 | 失败 | 合并 NMSE / dB |", "|---|---:|---:|---:|"]
        for candidate in selection["candidates"]:
            metrics = candidate["metrics"]
            lines.append(f"| {candidate['label']} | {metrics['complete']}/{metrics['expected_cases']} | {metrics['failed']} | {fmt(metrics.get('nmse_db'))} |")
        lines += ["", f"验证状态：{selection['status']}；选中候选：{selection.get('chosen', '无')}。"
                  "选择要求全部输入零失败，再最小化合并全信道 NMSE；并列时取 β=1。", ""]
    else:
        lines += ["求解器验证尚未完成；未给出已选择参数。", ""]
    if config:
        lines += [f"冻结参数：12 轮、16 探针、β={config['solver']['damping']:g}、活动阈值 0.5。"
                  "没有另用活动校准集。", "",
                  "[模型与配置](comparison_v1/FROZEN_CONFIG.json) · [测试前资产冻结](comparison_v1/TEST_FREEZE.json)", ""]
    lines += ["## 独立测试执行状态", "",
              "| 方法 | 完成/预定输入 | 失败 | 尚未运行 | 合并 NMSE / dB | AER | Brier 分数 | 平均接收机时间 / s |",
              "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for method in METHODS:
        values = summary["methods"][method]["overall"]
        lines.append(f"| {NAMES[method]} | {values['complete']}/{values['expected_cases']} | {values['failed']} | {values['pending']} | {fmt(values.get('nmse_db'))} | {percent(values.get('activity_error_rate'))} | {fmt(values.get('brier_score'), 5)} | {fmt(values.get('mean_seconds'), 2)} |")
    lines += ["", "完整集指标只有该方法的 24 个输入全部成功时才填入；失败不会删除，"
              "失败后的最后有效状态不计作成功输出。三方法比较图和配对区间必须等待全部三方法完成。", "",
              "Brier 分数使用二元定义 Σ(p−a)² / N，N 为实际概率输出对应的用户观测数；越低越好。"
              "仅汇总原生输出的活动概率，不把逐波束能量分数转换成概率；该方法显示不可用。"
              "定义来源见[术语依据](../../docs/TERMINOLOGY.md)。逐例保留平方误差之和与用户数，"
              "逐 SNR 数值在统计 CSV 和 JSON 中。", ""]
    iteration_figure_created = False
    if complete:
        plot(summary)
        iteration = iteration_analysis(summary)
        save(RUN / "ITERATION_SUMMARY.json", iteration)
        iteration_figure_created = plot_iterations(summary, iteration)
        lines += ["## 完整配对结果", "",
                  "| SNR / dB | 联合 score AMP NMSE | 原 Proposed NMSE | 逐波束 score AMP NMSE |",
                  "|---:|---:|---:|---:|"]
        for snr in SNRS:
            values = [fmt(summary["methods"][method]["by_snr"][str(snr)]["nmse_db"]) for method in METHODS]
            lines.append(f"| {snr} | {' | '.join(values)} |")
        lines += ["", "NMSE 按全用户累积平方误差除以累积真实信道能量计算后转 dB；越低越好，"
                  "零估计为 0 dB。信道估计没有用真实活动门控，也未在输出时再次乘活动概率。", "",
                  "| 方法 | 活跃 NMSE / dB | 非活跃误差/信号能量 | 漏检率 | 虚警率 | 平均迭代数 |",
                  "|---|---:|---:|---:|---:|---:|"]
        for method in METHODS:
            value = summary["methods"][method]["overall"]
            lines.append(f"| {NAMES[method]} | {fmt(value.get('active_nmse_db'))} | {fmt(value.get('inactive_error_over_signal'))} | {percent(value.get('miss_rate'))} | {percent(value.get('false_alarm_rate'))} | {fmt(value.get('mean_iterations'), 1)} |")
        lines += ["", "![独立三方法比较](comparison_v1/comparison.png)", "",
                  "[导出 PDF](comparison_v1/comparison.pdf) · [逐 SNR 统计 CSV](comparison_v1/STATISTICS.csv)", "",
                  "## 按物理场景配对的差值", ""]
        for baseline, entries in summary["uncertainty"]["differences"].items():
            overall = next(entry for entry in entries if entry["snr"] == "all")
            value = overall["new_minus_baseline"]["nmse_db"]
            lo, hi = value["percentile_95"]
            lines.append(f"- 新方法减去{NAMES[baseline]}的合并 NMSE 差：{value['value']:.3f} dB；"
                         f"95% 百分位区间 [{lo:.3f}, {hi:.3f}] dB。负值表示新方法较低。")
        lines += ["", "区间按 8 个物理场景进行 5000 次有放回配对重抽样，保持每个场景的三个 SNR 和"
                  "三种方法一起抽取。活动错误率和耗时差值也保存在 JSON 汇总中。", ""]
        lines += ["## 迭代轨迹与数值回升", "",
                  "![逐 SNR 迭代曲线](comparison_v1/iterations.png)", "",
                  "[迭代图 PDF](comparison_v1/iterations.pdf) · [逐例轨迹与统计](comparison_v1/ITERATION_SUMMARY.json)", "",
                  "两个 AMP 方法各绘制 12 轮；每个 SNR、每一轮都先累加 8 个场景的平方误差与真实信道能量，"
                  "再计算合并 NMSE。原 Proposed 的水平虚线只表示其最终结果，不能解释为同轮结果。"
                  "缺少任何一个场景的该轮数据时，对应曲线点留空，不使用较少场景代替，不补造初始或缺失轨迹。", "",
                  "| 方法 | 完整轨迹/输入 | 发生回升/有相邻轮输入 | 最大单步回升 / dB | 最大最终值减逐例最优值 / dB |",
                  "|---|---:|---:|---:|---:|"]
        for method in METHODS:
            values = iteration["methods"][method]
            lines.append(f"| {NAMES[method]} | {values['complete_trajectories']}/{values['expected_trajectories']} | "
                         f"{values['cases_with_positive_steps']}/{values['cases_with_observed_adjacent_steps']} | "
                         f"{fmt(values['max_single_step_rise_db'])} | {fmt(values['max_final_minus_best_db'])} |")
        lines += ["", "单步回升定义为同一输入的 NMSE(t+1)−NMSE(t)>0，按未舍入值统计；只使用真实保存的相邻两轮，"
                  "不跨缺轮计算。最终值减逐例最优值只在该例完整轨迹上计算。各方法迭代次数和停止规则不同，"
                  "这些量仅描述本次运行中的回升，不能当作收敛证明或相同计算预算下的比较。", ""]
        for method in METHODS:
            values = iteration["methods"][method]
            location, step = values["max_single_step_rise_location"], values["max_single_step_rise_iterations"]
            if location and step:
                lines.append(f"- {NAMES[method]}最大单步回升出现在场景 {location['scene']}（seed={location['seed']}），"
                             f"SNR={location['snr_db']} dB，第 {step['from_iteration']}→{step['to_iteration']} 轮，"
                             f"回升 {step['rise_db']:.3f} dB。")
        lines += [""]
        if iteration["status"] != "COMPLETE":
            lines += [f"轨迹统计状态为 **{iteration['status']}**；两个 AMP 的 {iteration['missing_curve_points']} 个合并曲线点不可用。"
                      "上表回升指标只覆盖实际保存的数据；完整轨迹不足时，不据此声称整个测试过程稳定。", ""]
    lines += ["## Onsager 探针误差诊断", "",
              f"新联合算法的诊断覆盖状态：**{onsager_mc['status']}**；已运行 {onsager_mc['attempted_cases']}/24 个输入，"
              f"其中 {onsager_mc['native_failed_cases']} 个未成功完成。仅读取原生 TRACE 字段，"
              "保留失败输入中已经保存的轮次。", "",
              "| 量 | 可用/预定轮次 | 均值 | 中位数 | 95 分位数 | 最大值 |",
              "|---|---:|---:|---:|---:|---:|"]
    for field, name in zip(MC_FIELDS, MC_NAMES):
        values = onsager_mc["overall"][field]
        lines.append(f"| {name} | {values['count']}/{values['expected']} | "
                     f"{fmt(values['mean'])} | {fmt(values['median'])} | {fmt(values['p95'])} | {fmt(values['max'])} |")
    lines += ["", "以上按可用的输入与轮次等权汇总；每个输入、每轮及各 SNR 的分布和缺失数量见"
              "[诊断 JSON](comparison_v1/ONSAGER_MC_DIAGNOSTICS.json)。第三行先对每轮两字段相除，"
              "只在校正幅度大于零时定义，不用汇总均值之比代替。缺失或无效项留空；各轮和各 SNR 不视为独立样本。", "",
              "这里的标准误差由固定查询下探针样本的中心波动估计，幅度对应当前 ZB 估计，"
              "不是阻尼后全部历史记忆项。它不测量估计偏差，也不验证 AWGN、状态演化或收敛；"
              "曲线平稳不能代替对这项误差的检查。诊断不用于改变冻结参数或筛选输入。"
              "原 Proposed 和旧逐波束算法未输出同类字段，不补造其诊断。", ""]
    lines += ["## 结果边界", "",
              "联合方法的活动概率来自最后完整接受轮的查询，`probability_query_iteration` 随原始输出记录；"
              "输出信道 X 则是阻尼递推形成的历史混合，二者不被称作同一个精确联合后验的统计量。"
              "原逐波束方法保留原能量门限，只输出其实际活动分数，不将分数写成概率。", "",
              "当前联合网络条件化到 16 个逐束方差，未使用完整相关噪声协方差。完整用户先验、"
              "共同活动和跨束 Onsager 校正不等同于已经消除所有有色噪声失配。", "",
              "8 个物理场景、一份新训练权重属于初步证据；不能代表所有信道、负载或训练种子。"
              "这里比较的是完整接收机，网络结构、先验建模和迭代均有差别，不能把差距归因于 AMP 单因素。"
              "稳定完成和 NMSE 改善均不证明结构化有限 AFDM 下严格 AWGN、状态演化或收敛。", "",
              "时间包含实际 Onsager 方向导数和轻量回调，不含模型加载；外部墙钟时间另含文件读写，"
              "两者均逐例保存。同一主机顺序执行的时间仅描述本次运行。各方法保留冻结的迭代与停止规则。", "",
              "## 复现", "", "```sh",
              ".venv/bin/python experiments/joint_amp_20261015/run_comparison.py --stage evaluate --device mps",
              ".venv/bin/python experiments/joint_amp_20261015/report.py", "```", "",
              "测试执行需已有通过验证且未变更的 TEST_FREEZE.json；报告命令仅读取既有结果，"
              "不会训练、推断或生成新测试数据。", ""]
    (DEST / "REPORT.md").write_text("\n".join(lines))
    save(RUN / "REPORT_STATUS.json", dict(status=summary["status"], report=str((DEST / "REPORT.md").relative_to(ROOT)),
                                         full_comparison_figure_created=complete,
                                         iteration_figure_created=iteration_figure_created,
                                         onsager_mc_diagnostics_status=onsager_mc["status"],
                                         methods={key: value["overall"]["status"] for key, value in summary["methods"].items()}))
    print(json.dumps(dict(report=str(DEST / "REPORT.md"), status=summary["status"]), ensure_ascii=False))


if __name__ == "__main__":
    main()
