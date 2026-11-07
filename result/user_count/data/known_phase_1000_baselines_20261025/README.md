# 用户数实验：四个 baseline，每条件 1000 MC

状态：**COMPLETE**。2026-10-25 16:10（北京时间）完成后处理及最终核验。

[查看正式报告](selected_readout_20261025/REPORT.md)。四个 baseline：Off-grid SBL、GNN-ASPL、GAMP-SBL、SOMP；用户数 20/40/60/80/100，每条件 1000 MC（场景 0–999），20 组共 20,000 条，4,000 条复用、16,000 条新推断。

评分采用用户确认的历史规则：Off-grid SBL、SOMP 按接收机估计 SNR 最近节点查表；GNN-ASPL、GAMP-SBL 使用历史固定门限。节点为 −4/−2/0/2/4/6 dB，中点取低档，范围外取端点；float64 >=，全零能量判不活动。未重新拟合门限，未重新推断，NMSE 与全部原始结果一致。

门限在场景 0–499 拟合、500–999 选择，此次评估场景 0–999 与开发场景重叠，属于回顾性迁移评估，不是独立测试。并发耗时仅用于诊断，不代表独占算法时延。

本批次不包含 STMP。旧五方法批次保持 DEFERRED_BY_USER，原 PLAN、STOP 及复用结果保留。当前评分的完成标记是 selected_readout_20261025/COMPLETE.json；原始推断完成标记和旧固定门限应用文件均保留。

## 原运行与门限安排（历史记录，保留原文）

**2026-10-25 用户更新：后续 baseline 使用所确认历史 AER 图的完整规则。** Off-grid SBL/SOMP 按估计 SNR 分档，GNN-ASPL/GAMP-SBL 固定门限。原始推断继续按本目录冻结 PLAN 运行；本目录旧 `READOUT_APPLICATION_PLAN.json`、`finalize.py` 及哈希保留，以下“后1000场景四固定门限”的安排仅作历史，不再执行。新应用与已通过的验证见 [采纳说明](../../../snr_comparison/data/adopted_baseline_readout_20261025/README.md)；自动跟进完成核验后调用其中 `finalize_user_count.py`，输出本目录 `selected_readout_20261025/`。以该子目录 `COMPLETE.json` 为当前规则完成标记。不得改写原 PLAN 或重新推断；STMP 仍不运行。策略来源与当前评估场景重叠，按回顾性迁移结果报告。

状态：RUNNING，已于 2026-10-25 08:29（北京时间）启动。用户于 2026-10-25 明确要求继续用户数实验，仅运行 baseline，不运行 STMP。

- 方法：Off-grid SBL、GNN-ASPL、GAMP-SBL、SOMP。
- 用户数：20、40、60、80、100；每档固定物理场景编号 0–999。
- 其他条件：16 帧导频、SNR 0 dB、活动概率 0.1、D 信道、DFT 导频、已知相位（提供仿真真值）、估计噪声。
- 正式结果目标：20,000 条；用户数 40 的 4,000 条复用已验证的原始结果，另外 16,000 条新推断。
- 计算：CPU 单 worker、每 worker 4 线程，无 GPU worker。方法白名单排除 STMP；元数据保留原输入幅度等共享模型记录，不会构造 STMP 网络。
- 读出：仅应用 SNR 独立编号 1000–1999 场景校准并冻结的四个固定门限，不重新拟合。结果属于回顾性评估，同一场景的跨实验复用不视为新增独立样本。
- 配对汇总以 Off-grid SBL 为参照；完整保留四个方法的绝对指标。并发耗时仅用于诊断，不代表独占算法时延。

旧五方法批次 `../known_phase_1000_20261023` 和其 STOP 保留，STMP 继续暂缓。已完成的导频、一阶去噪和收敛性结果保持原样。本批次不重启旧队列，不进行训练。

## 证据与入口

- `PLAN.json` / `PLAN_HASH.json`：独立冻结计划。
- `SOURCE_COMPATIBILITY.json`：旧结果与新批次的 baseline 推断、输入和权重一致性证据。
- `REUSED_RESULTS.json`：4,000 条复用指针及原始哈希。
- `PREFLIGHT.json`：CPU/STMP 范围检查、冻结门限边界检查、全部复用 compact 结果重评分检查。
- `DEPENDENCY.json` / `READOUT_APPLICATION_PLAN.json`：既有 SNR 门限及本批次后处理代码绑定。
- `LAUNCH.json` / `RUN_PROCESS.json` / `STATUS.json`：启动记录、实际 PID/创建时间/命令行、运行状态。
- `INFERENCE_COMPLETE.json` / `RAW_RESULT_AUDIT.json`：完整 20,000 条原始结果核验。
- `fixed_readout/SUMMARY.json` / `fixed_readout/REPORT.md` / `COMPLETE.json`：核验后固定门限汇总及文件哈希。

进度按 `sceneNNNN/conditionNN/方法.json` 的实际可用结果统计。`STATUS.completed` 仅包含已访问的复用指针，不可再直接加 4,000。

只允许首次启动 `parallel_run.py --plan <本目录绝对 PLAN 路径>`。运行失败保留证据，不自动重试。原始推断完成、实际运行进程退出后，再核验并调用本目录 `finalize.py --plan <本目录绝对 PLAN 路径>`；已有有效 COMPLETE 时跳过正式结果写入。

## 状态历史

- 2026-10-25：按用户要求创建 baseline 专用计划；旧五方法计划与停止记录保留。

- 2026-10-25 08:29（北京时间）：启动前检查 PASS；实际 driver PID 87848、CPU worker PID 41672，已确认四方法新结果。自动跟进已启用，每 30 分钟静默检查。
