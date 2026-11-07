# 活动概率四 baseline：已完成

2026-10-26：五档活动概率 0.05/0.10/0.15/0.20/0.25，每条件 1000 MC、场景0–999，四方法共 **20000 条**（4000复用、16000新算）。原始输入、JSON、compact、唯一覆盖和采纳门限后的结果均核验通过；20组每组1000场景，NMSE未改变。p=0.10与用户数40实验的160000个baseline活动判决及汇总指标一致。NMSE/AER合图及单图均已生成并检查。

已知相位使用仿真真值、噪声估计；条件抽样至少一人活跃，公开边际先验为 `p/(1-(1-p)^40)`。门限开发与0–999评估场景重叠，属于**回顾性迁移评估**；并发耗时只作诊断，不代表独占算法时延。不含STMP/C-STMP。全baseline接续目标仍在进行，下一项为跨信道。

[报告](known_phase_1000_baselines_20261025/selected_readout_20261025/REPORT.md) · [NMSE/AER图](../figures/baselines_selected_readout_20261025/activity_probability_baselines.png) · [完成记录](known_phase_1000_baselines_20261025/selected_readout_20261025/COMPLETE.json)

## 历史状态（保留原文）

# 活动概率数据

2026-10-25 20:21：四个 baseline 的五档活动概率实验已启动，每条件1000MC；总20000条、4000复用、16000新算，不含STMP。

[当前运行说明](known_phase_1000_baselines_20261025/README.md) · [实时状态](known_phase_1000_baselines_20261025/STATUS.json) · [启动前检查](known_phase_1000_baselines_20261025/PREFLIGHT.json)。使用用户采纳的历史判决规则，披露为回顾性迁移评估；详细条件抽样规则见运行说明。

## 历史说明（保留原文）

# 活动概率数据

尚无本轮 STMP 正式结果；以下保留不同协议的旧计划与历史记录。

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
