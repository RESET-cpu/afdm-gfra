# 结果索引

各批结果按相位条件、噪声条件和场景集合分别使用。当前算法绑定见 [MAINLINE.json](../MAINLINE.json)，实验源码入口见 [experiments](../experiments/README.md)。

## 当前比较与复核

| 内容 | 规模与范围 | 入口 |
|---|---|---|
| 五方法最终配对比较 | 500场景 × 7 SNR × 5方法；估计相位和噪声 | [报告](baseline_comparison_500_20261018/REPORT.md) · [图](baseline_comparison_500_20261018/comparison.png) |
| 原导频八档比较 | 五方法 × 10 场景 × 8 SNR；估计相位、供给准确物理噪声方差 | [结果](proposed_original_snr8_10_20261016/FINDINGS.md) · [完成检查](proposed_original_snr8_10_20261016/COMPLETION_CHECK.json) |
| 四 baseline 大样本实验 | 四方法 × 1000 场景 × 6 SNR；估计相位和噪声 | [报告](baselines_1000_20261015/REPORT.md) · [完成检查](baselines_1000_20261015/COMPLETION_CHECK.json) |
| 历史五方法图 | 已知相位；Proposed 100、SOMP/GAMP/GNN 各 1000、SBL 20 场景 | [原图](baseline_comparison_20261012/comparison.png) · [原汇总](baseline_comparison_20261012/summary.json) |
| 历史图复核 | 30 个汇总点一致；两个关键样本按冻结代码逐元素复现 | [报告](historical_figure_verification_20261016/REPORT.md) |
| Proposed 冻结主线 | 三份权重、源码、配置及 60 组历史输入／输出 | [版本说明](../docs/PROPOSED_MAINLINE.md) · [冻结目录](../archive/proposed_mainline_20261015/README.md) |
| 本次工作区整理 | 历史结果和研究代码归档、额外副本去重 | [报告](workspace_cleanup_20261018/REPORT.md) · [执行清单](workspace_cleanup_20261018/EXECUTION.json) |

## 原始结果与依赖

- 历史 Proposed 100 场景：[proposed_snr_100_20261009](proposed_snr_100_20261009/)，保留 on-grid 和 off-grid；原图采用 off-grid。
- 历史三 baseline 1000 场景：[baselines_40_1000_20261011](baselines_40_1000_20261011/)。
- 原前 100 场景 baseline 及固定活动判决：[proposed_baselines_40_20261011](proposed_baselines_40_20261011/)。
- 历史 Off-grid SBL 接入：[offgrid_baselines_20261012](offgrid_baselines_20261012/)。
- 模型训练与来源：[models](../models/README.md)、[TRAINING](../docs/TRAINING.md)、[GNN 历史记录](ding_reproduction_20261009/)。
- 全部结果分类：[INDEX.json](INDEX.json)。旧结果中的已有符号链接和全部失败记录保持可读。

## 当前原始记录

500 场景报告引用 [baseline_comparison_600_20261017](baseline_comparison_600_20261017/) 的 scene000–scene499；目录名称记录原计划，不能按名称删除。前 200 场景来源 [baseline_comparison_200_20261017](baseline_comparison_200_20261017/) 与 [相位／噪声验收](phase_optimization_20261017/) 一并保留。

## 历史归档

115 个历史结果实体和 19 份散落日志已移至 [2026-10-18 归档](../archive/workspace_cleanup_20261018/README.md)。原位置保留链接，旧报告、数值证据和失败记录继续可读。重复命名目录中的完全相同副本已去重，独有内容保留在归档；详见执行清单。历史结果不混入当前 500 场景统计。
