"""Summarize saved diagnostic results; no receiver execution."""
from diagnose_v3_v2_depth4_q8_20261020 import ROOT, PREVIOUS, OUT, read, write, sha
from pathlib import Path
import math
import shutil
import time
import numpy as np


def main():
    assert read(OUT / "AUDIT.json")["status"] == "PASSED"
    assert read(OUT / "first_layer_followup/AUDIT.json")["status"] == "PASSED"
    traces = {n: read(OUT / "traces" / f"{n}_005.json") for n in ("v2", "v3")}
    hybrids = {r["variant"]: r for r in read(OUT / "HYBRIDS.json")}
    messages = {r["variant"]: r for r in read(OUT / "MESSAGE_REPLAYS.json")}
    follow = {r["variant"]: r for r in read(OUT / "first_layer_followup/RESULTS.json")}
    stages = read(OUT / "training_stages/RESULTS.json")
    joint = {r["variant"]: r for r in read(OUT / "joint_component_replay/RESULTS.json")}
    raw_score = {r["variant"]: r for r in read(OUT / "joint_raw_score_replay/RESULTS.json")}
    for sub in ("training_stages", "joint_component_replay", "joint_raw_score_replay"):
        assert read(OUT/sub/"AUDIT.json")["status"] == "PASSED"
    swaps = next(r for r in read(OUT / "OUTPUT_SWAPS.json") if r["group"] == "k40_q8" and r["index"] == 5)
    plan = read(PREVIOUS / "PLAN.json")
    selected_validation = []
    validation_ids = []
    evidence_hashes = {}
    for epoch in (1, 2, 3):
        path = Path(plan["models"]["v3"]["run"]) / "checkpoints/depth_4" / f"validation_epoch_{epoch}.json"
        evidence_hashes[str(path)] = sha(path)
        value = read(path)
        selected_validation.append(dict(epoch=epoch,
            **next(r for r in value["by_condition"] if r["condition"]["frames"] == 8)))
        validation_ids.append([(r["seed"], r["truth_energy"], r["active"], r["inactive"])
                               for r in value["rows"] if r["frames"] == 8])
    assert validation_ids[0] == validation_ids[1] == validation_ids[2]
    statistics = read(OUT / "TRAINING_STATISTICS.json")
    coefficients = {n: s["mean_users_per_scene"]/s["mean_scene_energy"] for n, s in statistics.items()}
    conditions = {}
    for n, b in plan["models"].items():
        c = read(b["config"])["receiver"]
        profiles = c["conditions"]["train"]
        q8_profiles = sum(p["frames"] == 8 for p in profiles)
        per_condition = c["train_scenes"] // (len(profiles)*(len(c["snr_db"]) if n == "v2" else 1))
        q8 = q8_profiles*per_condition*(len(c["snr_db"]) if n == "v2" else 1)
        conditions[n] = dict(training_scenes=c["train_scenes"], q8_scenes=q8,
                             q8_fraction=q8/c["train_scenes"], q8_profiles=[p for p in profiles if p["frames"] == 8])
    baseline = read(OUT / "BASELINE_SUMMARY.json")
    indexed = {n: {r["index"]: r for r in baseline if r["method"] == n} for n in ("v2", "v3")}
    scene_deltas = [indexed["v3"][i]["nmse_db"]-indexed["v2"][i]["nmse_db"] for i in range(10)]
    total_increase = traces["v3"][-1]["error_energy"] - traces["v2"][-1]["error_energy"]
    target_increase = (traces["v3"][-1]["users"][27]["estimate_error_energy"]
                       - traces["v2"][-1]["users"][27]["estimate_error_energy"])
    source_case = next(c for c in plan["cases"] if c["group"] == "k40_q8" and c["index"] == 5)
    folder = Path(source_case["folder"])
    with np.load(folder / "input.npz") as v, np.load(folder / "truth.npz") as t:
        operator_errors = (abs(v["operator"]-t["true_operator"])**2).sum((0, 2)) / (
            abs(t["true_operator"])**2).sum((0, 2))
        frontend = dict(noise_estimate_to_truth_ratio=float(v["noise_variance"]/t["true_noise_variance"]),
                        operator_relative_squared_error_target_user=float(operator_errors[27]),
                        active_operator_relative_squared_errors={
                            str(u): float(operator_errors[u]) for u in np.flatnonzero(t["activity"])},
                        oracle_values_used_only_for_scoring=True)
    explanation = dict(
        status="COMPLETE", target_case=source_case, training_distributions=conditions,
        channel_to_bce_raw_sum_coefficient=coefficients,
        relative_channel_coefficient_change=coefficients["v3"]/coefficients["v2"]-1,
        selected_validation_q8=selected_validation, same_validation_cases_verified=True,
        target_error_increase_share=target_increase/total_increase,
        scene_delta_nmse_db=scene_deltas, frontend=frontend,
        validation_source_hashes=evidence_hashes,
        training_stage_replay=stages, joint_component_replay=list(joint.values()),
        joint_raw_score_replay=list(raw_score.values()),
        main_finding="This revealed case regresses during the second joint epoch. "
                     "Restoring only score network weights from the preceding epoch recovers detection "
                     "while keeping the final classifier and all scalar calibrations. Restoring only "
                     "classifiers, alpha or gamma/beta does not. The differences propagate through "
                     "early feedback means; old first-layer mean restores the v3-v2 case comparison "
                     "while replacing outgoing scalar variance does not.",
        causal_limit="This local intervention diagnosis does not prove that the changed training distribution "
                     "or BCE-to-score gradients caused the learned differences. No training ablation was run.")
    write(OUT / "EXPLANATION.json", explanation)

    lines = [
        "第三版与第二版四层：8导频退化场景的受控诊断",
        "2026-10-20；CPU两线程；固定权重；未调用GPU、未更新训练、未修改阈值。",
        "",
        "主要结论",
        "该场景在第二轮联合微调时出现退化。相邻轮次组件替换将主要差异定位到score网络参数更新："
        "只恢复上一轮score权重、保留最后一轮活动分类器与全部标量参数即可恢复检测；"
        "只恢复分类器、去噪缩放或消息标量参数均不能恢复。"
        "前层去噪与活动概率形成的反馈均值把差异传到后层，最终出现持续漏检。"
        "这不等于消息公式已被证明错误，也不证明是BCE而非信道损失的梯度造成了score参数变化，"
        "更不代表所有场景或AWGN去噪能力整体退化。",
        "",
        "比较范围",
        "此前已揭示的K40/Q8/p=0.1/0dB十个物理场景，复用相同观测、估计相位和估计噪声。"
        "两版都用原规则选中的四层epoch 3权重和0.5活动门限。目标是第六个场景，"
        "seed=202610200800006；目标用户代码索引27（从0开始计数）。",
        "全部十场景两版CPU重放与各自冻结原输出逐元素完全相同；原生forward与诊断forward也完全相同。",
        "新版在十场景中的九个NMSE改善，但一个较大退化使汇总没有明显优势；所有场景均保留。",
        "",
        "1. 目标用户逐层变化",
        "层数 | 第二版活动概率 | 新版活动概率 | 第二版条件信道误差能量 | 新版条件信道误差能量"]
    for i in range(4):
        a, b = traces["v2"][i]["users"][27], traces["v3"][i]["users"][27]
        lines.append(f"{i+1} | {a['probability']:.6f} | {b['probability']:.6f} | "
                     f"{a['conditional_error_energy']:.3f} | {b['conditional_error_energy']:.3f}")
    lines += [
        "目标用户真实信道能量319.516，占该场景总能量约20.3%，不是异常弱用户。"
        f"该用户解释了两版总误差增量的{target_increase/total_increase:.1%}。",
        "最终输出是活动概率乘条件信道均值，0.5门限只用于活动判决。"
        "单独改二元标签并不能恢复已经衰减的信道输出。",
        "",
        "2. 只替换一个中间量、保持后续全部新版网络",
        "操作 | 最终场景NMSE/dB | 目标用户活动概率 | 漏检/虚警",
        f"原新版 | {traces['v3'][-1]['nmse_db']:.4f} | "
        f"{traces['v3'][-1]['users'][27]['probability']:.6f} | 1/0"]
    for key, label in [
        ("old_message_after_layer_1_prior", "第一层反馈均值换第二版"),
        ("old_message_after_layer_1_variance", "只将第一层反馈方差换第二版"),
        ("old_message_after_layer_2_prior", "第二层反馈均值换第二版"),
        ("old_message_after_layer_2_variance", "只将第二层反馈方差换第二版")]:
        r = messages[key]
        lines.append(f"{label} | {r['nmse_db']:.4f} | {r['target_user']['probability']:.6f} | "
                     f"{r['misses']}/{r['false_alarms']}")
    lines += [
        "方差重放不是方差最优性证明，但表明本例中的版本差异主要不来自这一标量。"
        "两版每层阻尼系数均为1，反馈方差/查询方差约0.006—0.018，远离分母趋零；"
        "因此也没有消息数值爆炸的证据。",
        "",
        "3. 第一层反馈均值由什么造成",
        "以下固定新版第一层查询、反馈比例和传出标量方差，只替换均值构成所用的冻结旧输出。",
        "替换内容 | 最终NMSE/dB | 目标概率 | 漏检/虚警"]
    for key, label in [
        ("first_mean_old_probabilities_new_scalar_variance", "只替换第一层活动概率"),
        ("first_mean_old_conditional_new_scalar_variance", "只替换第一层条件信道均值"),
        ("first_mean_old_probabilities_conditional_new_scalar_variance", "同时替换概率和条件均值")]:
        r = follow[key]
        lines.append(f"{label} | {r['nmse_db']:.4f} | {r['probability_user27']:.6f} | "
                     f"{r['misses']}/{r['false_alarms']}")
    lines += [
        "两部分都有作用，不能将二者的改善相加或分成唯一百分比。",
        "更换第一层成套score、去噪缩放系数和活动头，同时保持新版消息参数与后续网络，"
        f"NMSE={follow['old_matched_networks_layers_1']['nmse_db']:.4f} dB；"
        "仅交叉替换score或分类头可能严重失配，不能据此评价任一模块的独立好坏。",
        "进一步按真值选择用户位置进行诊断（此处是oracle定位，不是可部署算法）："
        "只替换目标用户27的第一层均值仍漏检；"
        f"只替换其他用户22和31的第一层均值，最终NMSE={follow['first_old_mean_users_22_31']['nmse_db']:.4f} dB，"
        f"目标概率={follow['first_old_mean_users_22_31']['probability_user27']:.6f}，漏检消失。"
        "说明这是跨用户的反馈影响，不能只查看最终漏检用户自己的去噪结果。",
        "",
        "4. 固定同一查询评价末层网络",
        "在第二版第四层查询上，第二版条件均值对目标用户的误差能量73.679；"
        "新版score及新版缩放系数为67.480，新版活动概率0.98989。",
        "在新版第四层查询上，第二版成套去噪器的目标误差261.06，"
        "新版为242.33；旧网络也不能修复这个已经改变的输入。",
        "因此，末层score有能力恢复该用户，主要问题在进入后续层的消息。",
        "",
        "5. 为何训练分布对齐正式实验不保证每个端点提高",
        f"第二版8导频：{conditions['v2']['q8_scenes']}/{conditions['v2']['training_scenes']} "
        f"({conditions['v2']['q8_fraction']:.2%})，覆盖K20/p0.05、K100/p0.1各四种SNR。",
        f"新版8导频：{conditions['v3']['q8_scenes']}/{conditions['v3']['training_scenes']} "
        f"({conditions['v3']['q8_fraction']:.2%})，精确覆盖K40/p0.1/0dB。",
        "这是用较窄但更匹配的分布替代较广的低导频训练；并非在原训练样本上额外增加目标工况。"
        "低导频总体训练占比下降是一条合理解释，但尚无固定其他因素的重训练消融，不能当成已证实因果，"
        "也不能据此自动恢复用户排除的极端场景。",
        "两版训练能量与平均用户数归一化常量不同。若把单场景损失写成"
        "SSE/Ebar + BCE_sum/Kbar，新版原始SSE相对BCE_sum的系数Kbar/Ebar提高"
        f"{(coefficients['v3']/coefficients['v2']-1)*100:.2f}%。"
        "名义损失系数仍为1:1，但换分布同时改变了固定归一化常量；这不是训练权重失当的充分证据。",
        "两版初始化种子、预训练score、损失形式和分阶段学习率一致；训练样本、分布、验证集和每层更新预算略有差异。"
        "因此不可将结果单独归于分布或层数。",
        "",
        "6. 退化具体发生在哪个训练阶段",
        "同一固定场景、同一前端、同一阈值，使用现有epoch 1/2/3权重，只读重放；没有更改选模。",
        "阶段 | 场景NMSE/dB | 目标用户活动概率 | 漏检/虚警"]
    for s in stages:
        r = s["trace"][-1]
        label = {1: "新增层适应后", 2: "联合微调第1轮", 3: "联合微调第2轮"}[s["epoch"]]
        lines.append(f"{label} | {r['nmse_db']:.4f} | {r['target_probability']:.6f} | "
                     f"{r['misses']}/{r['false_alarms']}")
    lines += [
        "以最后一轮模型为基础，每次只替换指定组件为上一轮权重；其他组件全部不变。",
        "替换内容 | 场景NMSE/dB | 目标用户活动概率 | 漏检/虚警"]
    for source, key, label in [
        (raw_score, "epoch2_raw_score_all_layers", "只替换四层score网络参数，alpha保持最后一轮"),
        (joint, "score_epoch3_activity_epoch2_messages_epoch3", "只替换四层活动分类器"),
        (joint, "score_epoch3_activity_epoch3_messages_epoch2", "只替换四层gamma/beta消息标量参数"),
        (raw_score, "epoch2_alpha_all_layers", "只替换四层去噪缩放alpha"),
        (raw_score, "epoch2_score_and_alpha_layer2", "只替换第二层score及alpha")]:
        r = source[key]
        lines.append(f"{label} | {r['nmse_db']:.4f} | {r['target_probability']:.6f} | "
                     f"{r['misses']}/{r['false_alarms']}")
    lines += [
        "因此，对这次具体退化，score网络参数变化是较直接的触发，均值反馈是传播途径，"
        "活动概率降低是后果并进一步抑制信道反馈。第二层是敏感位置之一，"
        "不能仅从最终分类错误就认定分类器参数本身需要重做。",
        "",
        "7. 局部退化与整体改善同时存在：新版自身相同100个Q8验证场景",
        "阶段 | AER | 漏检率 | 虚警率 | 信道NMSE/dB"]
    for s in selected_validation:
        label = {1: "新增层适应后", 2: "联合微调第1轮", 3: "联合微调第2轮"}[s["epoch"]]
        lines.append(f"{label} | {s['aer']:.3%} | {s['missed_detection_rate']:.3%} | "
                     f"{s['false_alarm_rate']:.3%} | {s['pooled_nmse_db']:.4f}")
    lines += [
        "联合微调最后相对适应阶段：AER、漏检率、虚警率及NMSE均改善。"
        "第2次联合相对第1次联合漏检上升、虚警下降，存在检测取舍，但不支持‘联合训练整体破坏score’的结论。"
        "Q8子集selection_loss也从第1次联合0.21654下降到第2次0.20034。"
        "当前平均选模规则可以接受少数场景或漏检指标的退化；选中最后一轮不是实现错误。",
        "这里仅在同一新版验证集内部比较，不与第二版不同验证集的均值配对。",
        "两版训练使用已知相位和噪声，而这十场景使用同一缓存估计前端；"
        f"目标场景噪声估计偏高{(frontend['noise_estimate_to_truth_ratio']-1)*100:.2f}%，"
        f"目标用户算子相对平方误差{frontend['operator_relative_squared_error_target_user']:.3g}。"
        "该差异应在训练/测试协议中明确，但同一前端不直接解释两版差距；没有执行oracle前端替代推断。",
        "",
        "建议与证据边界",
        "本次优先关注前层条件信道均值与活动概率形成的反馈，以及联合训练后这种配合在少导频场景中的稳定性。"
        "现有结果没有给出增加方差网络的依据，也不能保证单纯加深层数能恢复此类漏检。"
        "若后续修改训练，应在固定场景、相同初始化与更新预算下区分低导频采样权重、"
        "BCE是否回传score、以及条件信道误差与最终有效信道误差的作用；不得针对这一场景调门限。",
        "本次有推断阶段的组件替换，没有重新训练的梯度消融，不能宣称已证明BCE梯度有害、"
        "必须停止联合训练，或某种混合网络可以推广。"
        "当前十层训练继续原计划；所有本次干预仅为已揭示单场景的诊断，没有替换主线。",
        "",
        "可复核数据：PLAN.json、AUDIT.json、EXPLANATION.json、FIXED_QUERY.json、HYBRIDS.json、"
        "MESSAGE_REPLAYS.json、first_layer_followup/RESULTS.json、training_stages/RESULTS.json、"
        "joint_component_replay/RESULTS.json、joint_raw_score_replay/RESULTS.json；脚本冻结副本保存在对应目录。"]
    (OUT / "REPORT.txt").write_text("\n".join(lines)+"\n", encoding="utf-8")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "savefig.dpi": 180})
    fig, axes = plt.subplots(2, 2, figsize=(13.4, 9), constrained_layout=True)
    ax = axes[0, 0]
    ax.bar(np.arange(1, 11), scene_deltas,
           color=["#c95042" if x > 0 else "#268b8b" for x in scene_deltas])
    ax.axhline(0, color="#555555", lw=.8)
    ax.set(xticks=np.arange(1, 11), xlabel="Previously revealed scene", ylabel="New - v2 NMSE (dB)",
           title="A. Nine improve; scene 6 regresses")
    ax.text(6, scene_deltas[5]+.08, f"+{scene_deltas[5]:.2f}", ha="center", color="#a8372a")
    ax.set_ylim(min(scene_deltas)-.35, max(scene_deltas)+.65)
    colors = {"v2": "#426da9", "v3": "#c95042"}
    names = {"v2": "Previous v2", "v3": "New v3"}
    ax = axes[0, 1]
    for n in ("v2", "v3"):
        ax.plot(range(1, 5), [r["users"][27]["probability"] for r in traces[n]],
                "o-", label=names[n], color=colors[n], lw=2)
    ax.axhline(.5, color="#888888", ls="--", lw=1)
    ax.set(xticks=range(1, 5), xlabel="Unfolded layer", ylabel="Activity probability",
           title="B. Scene 6, missed user (zero-based ID 27)", ylim=(-.03, 1.05))
    ax.legend()
    ax = axes[1, 0]
    labels = ["Original new", "Old first feedback mean", "Old first feedback variance",
              "Old first activity probabilities", "Old first conditional means"]
    values = [traces["v3"][-1]["nmse_db"], messages["old_message_after_layer_1_prior"]["nmse_db"],
              messages["old_message_after_layer_1_variance"]["nmse_db"],
              follow["first_mean_old_probabilities_new_scalar_variance"]["nmse_db"],
              follow["first_mean_old_conditional_new_scalar_variance"]["nmse_db"]]
    ys = np.arange(len(labels))
    ax.scatter(values, ys, s=65, color=["#c95042", "#268b8b", "#c95042", "#268b8b", "#268b8b"])
    for v, y in zip(values, ys):
        ax.annotate(f"{v:.2f}", (v, y), xytext=(0, -14), textcoords="offset points", ha="center")
    ax.set(yticks=ys, yticklabels=labels, xlabel="Scene NMSE (dB; lower is better)",
           title="C. One-case interventions; later networks unchanged", xlim=(-8.2, -4.1), ylim=(4.7, -.5))
    ax.grid(axis="x", alpha=.2)
    ax = axes[1, 1]
    for n in ("v2", "v3"):
        vals = [10*math.log10(r["users"][27]["conditional_error_energy"]/r["users"][27]["true_energy"])
                for r in traces[n]]
        ax.plot(range(1, 5), vals, "o-", label=names[n], color=colors[n], lw=2)
    ax.set(xticks=range(1, 5), xlabel="Unfolded layer", ylabel="Conditional channel NMSE (dB)",
           title="D. User 27: estimate before activity weighting")
    ax.legend()
    fig.suptitle("K=40, Q=8, SNR=0 dB: fixed-weight CPU diagnosis\n"
                 "Observed examples and post-hoc interventions; no training or threshold changes", fontsize=13)
    fig.savefig(OUT / "diagnosis.png")
    fig.savefig(OUT / "diagnosis.pdf")
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.6), constrained_layout=True)
    ax = axes[0]
    x = np.arange(3)
    values = [s["trace"][-1]["nmse_db"] for s in stages]
    ax.plot(x, values, "o-", color="#c95042", lw=2)
    for xx, y, stage in zip(x, values, stages):
        ax.annotate(f"{y:.2f} dB\np={stage['trace'][-1]['target_probability']:.3f}",
                    (xx, y), xytext=(0, 12), textcoords="offset points", ha="center")
    ax.set(xticks=x, xticklabels=["Adaptation", "Joint epoch 1", "Joint epoch 2"],
           ylabel="Scene NMSE (dB; lower is better)", ylim=(-8, -3.5), xlim=(-.4, 2.4),
           title="Same revealed scene through training")
    ax.grid(axis="y", alpha=.2)
    ax = axes[1]
    labels = ["Final model", "Previous score weights only", "Previous activity heads only",
              "Previous message scalars only", "Previous alpha only", "Previous layer-2 score + alpha"]
    vals = [values[-1], raw_score["epoch2_raw_score_all_layers"]["nmse_db"],
            joint["score_epoch3_activity_epoch2_messages_epoch3"]["nmse_db"],
            joint["score_epoch3_activity_epoch3_messages_epoch2"]["nmse_db"],
            raw_score["epoch2_alpha_all_layers"]["nmse_db"],
            raw_score["epoch2_score_and_alpha_layer2"]["nmse_db"]]
    ys = np.arange(len(vals))
    ax.scatter(vals, ys, s=60, color=["#c95042", "#268b8b", "#c95042", "#c95042", "#c95042", "#268b8b"])
    for v, y in zip(vals, ys):
        ax.annotate(f"{v:.2f}", (v, y), xytext=(0, -13), textcoords="offset points", ha="center")
    ax.set(yticks=ys, yticklabels=labels, xlim=(-7.9, -4.05), ylim=(5.6, -.5),
           xlabel="Scene NMSE (dB; lower is better)", title="Final model with one component restored")
    ax.grid(axis="x", alpha=.2)
    fig.suptitle("Second joint epoch: score-weight changes explain this case's regression\n"
                 "Post-hoc CPU diagnosis only; no weight updates or model reselection", fontsize=12)
    fig.savefig(OUT/"joint_stage_diagnosis.png")
    fig.savefig(OUT/"joint_stage_diagnosis.pdf")
    plt.close(fig)
    shutil.copy2(__file__, OUT/"source"/Path(__file__).name)
    write(OUT / "REPORT_AUDIT.json", dict(status="PASSED", created_unix=time.time(),
        report_sha256=sha(OUT / "REPORT.txt"), figure_sha256=sha(OUT / "diagnosis.png"),
        joint_figure_sha256=sha(OUT/"joint_stage_diagnosis.png"),
        source_sha256=sha(OUT/"source"/Path(__file__).name),
        evidence_sha256=sha(OUT / "EXPLANATION.json"), same_q8_validation_cases_verified=True))
    print(str(OUT / "REPORT.txt"))


if __name__ == "__main__":
    main()
