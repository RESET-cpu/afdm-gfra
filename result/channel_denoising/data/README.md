# 独立去噪数据

current 为 Mac 上传并审核通过的历史九曲线去噪实验：500 场景，每场景 4 个候选信道。Proposed 是一阶去噪器，不是十层展开接收机。

| 入口 | 保存的状态 | 汇总文件 |
|---|---|---|
| [history/final2000](history/final2000/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [history/lstmp_v3_formal2000_20261021](history/lstmp_v3_formal2000_20261021/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [history/main2000_20261023](history/main2000_20261023/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [planned_2000_ten_layer](planned_2000_ten_layer/) | `PLANNED_NOT_STARTED` | 无 |
| [history/main2000_message_gem_20261022](history/main2000_message_gem_20261022/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [history/main2000_runtime_20261023](history/main2000_runtime_20261023/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [history/new_models_paired_20261019_v2](history/new_models_paired_20261019_v2/) | `COMPLETE` | 有 |
| [current](current/) | `COMPLETE_500_SCENES_9_CURVES` | 有 |
| [history/proposed_first_500_20261018](history/proposed_first_500_20261018/) | `HISTORICAL_SOURCE_RESULTS` | 有 |

有 SUMMARY.json 不代表结果完整；以文件内状态、计划和配对审核为准。
`planned_2000_ten_layer/` 为旧十层计划，本次未启动。
原始协议、方法名、场景身份与汇总数值保持原文；不得跨协议拼接。
实际来源见 [INDEX.json](INDEX.json)。
