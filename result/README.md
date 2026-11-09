# 实验索引

新实验的运行方法见[实验说明](../src/experiment/README.md)。各历史批次的参数、覆盖范围及验证以自己的 `PLAN.json`、`COMPLETION.json` 和采用记录为准。

| 实验 | 配置 | 论文图 |
|---|---|---|
| 信道去噪 | [channel_denoising](../src/configs/experiments/channel_denoising.json) | [图 4](../paper/figures/channel_denoising.pdf) |
| SNR | [snr_comparison](../src/configs/experiments/snr_comparison.json) | [图 6](../paper/figures/snr_comparison.pdf) |
| 导频帧数 | [pilot_frames](../src/configs/experiments/pilot_frames.json) | [图 7](../paper/figures/pilot_frames.pdf) |
| 设备数 | [user_count](../src/configs/experiments/user_count.json) | [图 8](../paper/figures/user_count.pdf) |
| 活动概率 | [activity_probability](../src/configs/experiments/activity_probability.json) | [图 9](../paper/figures/activity_probability.pdf) |
| 跨信道 | [cross_channel](../src/configs/experiments/cross_channel.json) | [图 10](../paper/figures/cross_channel.pdf) |
| 密度比消融 | [density_ratio_ablation](../src/configs/experiments/density_ratio_ablation.json) | 批次记录；通用新入口当前为 deferred |
| 运行时间 | [runtime_comparison](../src/configs/experiments/runtime_comparison.json) | 批次报告 |

收敛图来自独立的已采用 30 场景批次，见[图 5 与其他图源](../paper/docs/REPRODUCTION.md)。上述新实验默认配置与历史图的配置分别保存。

## 当前研究进度

2026-11-07：白噪声主 SNR 和信道去噪已采用。导频数实验在已有 2906 份结果核验通过后恢复续跑；原计划共 12000 份，包含 2000 份匹配输入的复用结果。恢复依据见[记录](../archive/pilot_resume_20261107/README.md)。图 7 尚未采用新批次，图 8–10 的后续替换尚未启动。

查看本地实时进度：

```text
python run_experiments.py white_followup inspect
```

本地实时状态文件位于 `pilot_frames/data/white_mainline_500_20261107/STATUS.json`，不纳入静态发布清单。检查时的进度快照见[本轮验证记录](../archive/code_fixes_20261107/VALIDATION.json)，GitHub 不提供实时进度。完整输入与逐场景预测不随小型汇总发布；当前批次完成并通过全量核验、更新图稿后，再进入下一阶段。

## 最新导频图（2026-11-09）

[查看三列图例版导频 NMSE 图与复现说明](pilot_frames/latest_20261109/README.md)。8、12、16、20、24 帧，九条曲线，每点 500 场景；仅更新独立实验结果，论文采用另行处理。
