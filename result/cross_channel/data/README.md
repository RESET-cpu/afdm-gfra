# 跨信道四 baseline：已完成并核验

2026-10-27：原始推断于北京时间 2026-10-26 23:52 完成；固定历史门限后处理于 2026-10-27 00:41 完成。正式 COMPLETE、全部绑定文件、96000 条结果及 384 万个活动判决均已核验，D 复用部分与原 SNR 的 96 万个判决逐项一致。每条件 1000 MC，D/A/B/C × 六档 SNR × 四方法共 96 组：24000 条复用、72000 条新算。四类信道的 NMSE/AER 图使用全部场景，已核对来源与版式。

采用既有接收机估计 SNR 判决规则，不重新拟合门限，原始 NMSE 不变。场景与门限开发重叠，属回顾性迁移评估；固定几何的表列信道剖面不代表完整时变多普勒谱，并发耗时仅诊断。后续独立运行时间实验仍须单独通过安静资源窗口，不能用本批次并发计时替代。

[正式报告](known_phase_1000_baselines_20261025/selected_readout_20261025/REPORT.md) · [四类信道图片](../figures/baselines_selected_readout_20261027/README.md)

## 历史状态（原文保留）

# 跨信道四 baseline：正在运行

2026-10-26 01:58（北京时间）首次启动。活动概率已完成原始审计、采纳门限汇总与三幅图，进程和共享锁均正常结束后，本批次24条件输入预检PASS。driver **91668**（创建1792951140.0647013）、CPU worker **92792**（创建1792951144.4054163）及启动器91408均已核对；首个新条件四方法结果已完成输入/raw/compact哈希核验。

D/A/B/C × SNR −4/−2/0/2/4/6 dB，每条件1000MC、场景0–999，四baseline共96000条：D复用24000，A/B/C新算72000。40用户、16帧、p=0.1、已知相位、估计噪声；CPU单worker4线程、GPU0。不运行STMP/C-STMP或训练。已启动，**禁止重复启动、重新冻结或自动重试**；实际进度按结果指针计数，不能把STATUS.completed直接加24000。

沿用用户采纳的历史判决规则，门限开发与评估场景重叠，属回顾性迁移评估；并发耗时仅作诊断。保留既有固定几何和表列功率/时延/衰落剖面，不宣称完整时变多普勒谱。完整结果、图、索引核验后才接续运行时间实验。

[运行说明](known_phase_1000_baselines_20261025/README.md) · [运行状态](known_phase_1000_baselines_20261025/STATUS.json) · [启动核验](known_phase_1000_baselines_20261025/LAUNCH_VERIFICATION.json)

## 历史说明（保留原文）

# 跨信道数据

尚无本轮 STMP 正式结果；以下保留不同协议的旧计划与历史记录。

| 入口 | 保存的状态 | 汇总文件 |
|---|---|---|
| [history/final2000](history/final2000/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [history/lstmp_v3_formal2000_20261021](history/lstmp_v3_formal2000_20261021/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [history/main2000_20261023](history/main2000_20261023/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [planned_2000_ten_layer](planned_2000_ten_layer/) | `PLANNED_NOT_STARTED` | 无 |
| [history/main2000_message_gem_20261022](history/main2000_message_gem_20261022/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [history/main2000_runtime_20261023](history/main2000_runtime_20261023/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [history/new_models_paired_20261019](history/new_models_paired_20261019/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [history/new_models_paired_20261019_v2](history/new_models_paired_20261019_v2/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |

有 SUMMARY.json 不代表结果完整；以文件内状态、计划和配对审核为准。
`planned_2000_ten_layer/` 为旧十层计划，本次未启动。
原始协议、方法名、场景身份与汇总数值保持原文；不得跨协议拼接。
实际来源见 [INDEX.json](INDEX.json)。
