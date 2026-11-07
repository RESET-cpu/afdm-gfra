# SNR 对比：四 baseline 当前入口

2026-10-25：用户采纳的历史规则已用于八档 SNR（−4 至 10 dB，每 2 dB 一档）、每条件每方法 1000 MC，共 32000 条。已逐判决核验既有重放并导出四 baseline；没有新推断、拟合或平滑。

当前[报告](baselines_adopted_20261025/REPORT.md)、[完成审计](baselines_adopted_20261025/COMPLETE.json)和[图](../figures/baselines_adopted_20261025/snr_baselines_preview.png)。Off-grid SBL/SOMP 按估计 SNR 查表，GNN-ASPL/GAMP-SBL 保留历史固定门限。场景0–999与门限开发重叠，属于回顾性迁移评估，不是独立测试。完整历史入口保留如下，旧文字中的“当前”只代表其当时状态。

## 历史记录（原文保留）

# SNR 对比数据

当前采用 [baseline_fixed_last500_20261023](baseline_fixed_last500_20261023/README.md)：
主实验编号 1000–1499 的 500 场景拟合固定门限，应用到编号 0–999 的 1000 场景重画图。
四个 baseline 各用一个跨全部 SNR 的固定门限，STMP 保持 0.5。
主实验已按用户要求安全暂停：baseline 各完成 1502 场景；STMP 完成 1184 场景另 3 个 SNR 输入。
原始输出和冻结配置不改写，不自动恢复。

此前 [baseline_fixed_independent_20261023](baseline_fixed_independent_20261023/README.md) 额外种子校准也已停止，
保存 1148 份校准输出，不用于当前后500场景方案。

此前 [baseline_calibration_20261023](baseline_calibration_20261023/README.md) 的独立种子、共享缓存和 880 份输出
在新固定门限批次中按哈希复用；旧的分档选择程序保持停止。

[baseline_calibration_reuse1000_20261023](baseline_calibration_reuse1000_20261023/README.md) 的前 1000 场景校准
及其图保留为历史诊断，用户已改用额外场景固定门限方案，不再采用该批次选择的门限。

新增 [interim_800](interim_800/)：固定场景 0–799，五种方法、六档 SNR，共 24,000 份结果已完成输入配对、输出哈希和评分审核。

当前为已知相位、估计噪声的 STMP 与四个 baseline 主实验；2000 场景计划现已暂停。interim_500 是固定前 500 个场景的已审核快照。

| 入口 | 保存的状态 | 汇总文件 |
|---|---|---|
| [current](current/) | `STOPPED_BY_USER` | 无 |
| [shared](shared/) | `SHARED_INPUTS` | 无 |
| [scene_registry](scene_registry/) | `FROZEN_2000_SCENES` | 无 |
| [interim_193](interim_193/) | `AUDITED_INTERIM_193` | 有 |
| [interim_500](interim_500/) | `AUDITED_INTERIM_500` | 有 |
| [history/final2000](history/final2000/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [history/known_phase500_20261022](history/known_phase500_20261022/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [history/lstmp_v3_formal2000_20261021](history/lstmp_v3_formal2000_20261021/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [history/main2000_20261023](history/main2000_20261023/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [planned_2000_ten_layer](planned_2000_ten_layer/) | `PLANNED_NOT_STARTED` | 无 |
| [history/main2000_message_gem_20261022](history/main2000_message_gem_20261022/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [history/main2000_runtime_20261023](history/main2000_runtime_20261023/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [history/baseline_comparison_500_20261018](history/baseline_comparison_500_20261018/) | `HISTORICAL_COMPLETE_DIFFERENT_PROTOCOL` | 有 |

有 SUMMARY.json 不代表结果完整；以文件内状态、计划和配对审核为准。
`planned_2000_ten_layer/` 为旧十层计划，本次未启动。
原始协议、方法名、场景身份与汇总数值保持原文；不得跨协议拼接。
实际来源见 [INDEX.json](INDEX.json)。
