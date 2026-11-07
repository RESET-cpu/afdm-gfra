# 当前四 baseline 导频结果：采纳门限版已完成

2026-10-26：Off-grid SBL、GNN-ASPL、GAMP-SBL、SOMP，8/16/24/32/40/48帧，每条件1000 MC，共24000条。原始推断中4000条复用公共SNR条件、20000条来自已完成导频；本次新增推断0，NMSE不变。采用用户确认的历史门限，不重新拟合。

[报告](adopted_baseline_readout_20261025/selected_readout_20261025/REPORT.md) · [汇总](adopted_baseline_readout_20261025/selected_readout_20261025/SUMMARY.json) · [NMSE/AER图](../figures/baselines_selected_readout_20261025/pilot_frames_baselines.png)。完成证书、24组完整覆盖、所有绑定文件与图片清单核验通过；公共条件与SNR及用户数结果逐判决一致。门限开发与评估场景0–999重叠，属于回顾性迁移评估，并非独立测试。并发耗时仅诊断。

旧五方法原始批次及旧固定门限结果保留原样。本入口只新增四baseline派生版本，不改变其他线程的C-STMP安排。

## 历史说明（保留原文）

# 导频帧数数据

现行 [1000 场景已知相位批次](known_phase_1000_20261023/README.md)已加入后台队列，等待当前 SNR 补跑与门限校准完成后计算，再接续用户数实验。
16 帧、0 dB 的 5000 份重合结果已校验复用，其余五档补算 25000 次。实时进度见该批次 `QUEUE_STATUS.json` 和 `STATUS.json`。
旧 2000 场景计划已停用，超出前 1000 场景的 2193 份副本已删除，保留 5000 份实际结果用于复用。以下保留不同协议的旧计划与历史记录。

| 入口 | 保存的状态 | 汇总文件 |
|---|---|---|
| [history/final2000](history/final2000/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [history/lstmp_v3_formal2000_20261021](history/lstmp_v3_formal2000_20261021/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [history/main2000_20261023](history/main2000_20261023/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [planned_2000_ten_layer](planned_2000_ten_layer/) | `PLANNED_NOT_STARTED` | 无 |
| [history/main2000_message_gem_20261022](history/main2000_message_gem_20261022/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [history/main2000_runtime_20261023](history/main2000_runtime_20261023/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |

有 SUMMARY.json 不代表结果完整；以文件内状态、计划和配对审核为准。
`planned_2000_ten_layer/` 为旧十层计划，本次未启动。
原始协议、方法名、场景身份与汇总数值保持原文；不得跨协议拼接。
实际来源见 [INDEX.json](INDEX.json)。
