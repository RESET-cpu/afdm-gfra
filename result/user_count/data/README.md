# 用户数量数据

状态：**COMPLETE**。2026-10-25 16:10（北京时间）完成后处理及最终核验。

[查看正式报告](known_phase_1000_baselines_20261025/selected_readout_20261025/REPORT.md)。四个 baseline：Off-grid SBL、GNN-ASPL、GAMP-SBL、SOMP；用户数 20/40/60/80/100，每条件 1000 MC（场景 0–999），20 组共 20,000 条，4,000 条复用、16,000 条新推断。

评分采用用户确认的历史规则：Off-grid SBL、SOMP 按接收机估计 SNR 最近节点查表；GNN-ASPL、GAMP-SBL 使用历史固定门限。节点为 −4/−2/0/2/4/6 dB，中点取低档，范围外取端点；float64 >=，全零能量判不活动。未重新拟合门限，未重新推断，NMSE 与全部原始结果一致。

门限在场景 0–499 拟合、500–999 选择，此次评估场景 0–999 与开发场景重叠，属于回顾性迁移评估，不是独立测试。并发耗时仅用于诊断，不代表独占算法时延。

本批次不包含 STMP。旧五方法批次保持 DEFERRED_BY_USER，原 PLAN、STOP 及复用结果保留。当前评分的完成标记是 selected_readout_20261025/COMPLETE.json；原始推断完成标记和旧固定门限应用文件均保留。

## 原运行与门限安排（历史记录，保留原文）

现行 [四个 baseline 的用户数批次](known_phase_1000_baselines_20261025/README.md)已于 2026-10-25 08:29（北京时间）启动，仅运行 Off-grid SBL、GNN-ASPL、GAMP-SBL、SOMP，不运行 STMP。用户数 20/40/60/80/100，每档 1000 MC（场景 0–999）；共 20,000 条结果，4,000 条复用、16,000 条新推断。CPU 单 worker、4 线程。后处理只应用既有 SNR 校准的固定门限。当前状态见 [CURRENT.json](CURRENT.json)。

旧 [五方法批次](known_phase_1000_20261023/README.md)于 2026-10-24 按用户要求暂缓，STOP 保留。其已复用的 5,000 条历史结果不变；本次独立批次只引用其中 4,000 条 baseline 结果。正式完整汇总尚未生成。

历史说明（保留原记录）：

> 现行 [1000 场景已知相位批次](known_phase_1000_20261023/README.md)已加入后台队列，在 SNR 和导频完成后计算。40 用户、16 帧、0 dB 的 5000 份结果已校验复用，其余四档补算 20000 次；当前进度见 `CURRENT.json` 指向的队列和批次状态。完整正式结果尚未生成；以下保留不同协议的旧计划与历史记录。

| 入口 | 保存的状态 | 汇总文件 |
|---|---|---|
| [history/final2000](history/final2000/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [history/lstmp_v3_formal2000_20261021](history/lstmp_v3_formal2000_20261021/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [history/main2000_20261023](history/main2000_20261023/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [planned_2000_ten_layer](planned_2000_ten_layer/) | `PLANNED_NOT_STARTED` | 无 |
| [history/main2000_message_gem_20261022](history/main2000_message_gem_20261022/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [history/main2000_runtime_20261023](history/main2000_runtime_20261023/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [history/new_models_paired_20261019](history/new_models_paired_20261019/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [history/new_models_paired_20261019_cuda_graph](history/new_models_paired_20261019_cuda_graph/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |
| [history/new_models_paired_20261019_v2](history/new_models_paired_20261019_v2/) | `HISTORICAL_PLAN_OR_PARTIAL_RESULTS` | 无 |

有 SUMMARY.json 不代表结果完整；以文件内状态、计划和配对审核为准。
`planned_2000_ten_layer/` 为旧十层计划，本次未启动。
原始协议、方法名、场景身份与汇总数值保持原文；不得跨协议拼接。
实际来源见 [INDEX.json](INDEX.json)。
