# 活动概率四 baseline：已完成

2026-10-26：五档活动概率 0.05/0.10/0.15/0.20/0.25，每条件 1000 MC、场景0–999，四方法共 **20000 条**（4000复用、16000新算）。原始输入、JSON、compact、唯一覆盖和采纳门限后的结果均核验通过；20组每组1000场景，NMSE未改变。p=0.10与用户数40实验的160000个baseline活动判决及汇总指标一致。NMSE/AER合图及单图均已生成并检查。

已知相位使用仿真真值、噪声估计；条件抽样至少一人活跃，公开边际先验为 `p/(1-(1-p)^40)`。门限开发与0–999评估场景重叠，属于**回顾性迁移评估**；并发耗时只作诊断，不代表独占算法时延。不含STMP/C-STMP。全baseline接续目标仍在进行，下一项为跨信道。

[报告](selected_readout_20261025/REPORT.md) · [NMSE/AER图](../../figures/baselines_selected_readout_20261025/activity_probability_baselines.png) · [完成记录](selected_readout_20261025/COMPLETE.json)

## 运行阶段历史（保留原文）

# 活动概率实验：四个 baseline，每条件 1000 MC

状态：**RUNNING**。2026-10-25 20:21（北京时间）首次正式启动；driver PID 89932、CPU worker PID 87028，已核对创建时间、命令行及父子关系，首个新条件的四方法结果已落盘并核验。启动前检查 PASS，4000 条复用结果均通过输入/原始/compact 哈希和已采用判决的配对核验。

- 方法：Off-grid SBL、GNN-ASPL、GAMP-SBL、SOMP，不含 STMP、C-STMP 或十层展开方法。
- 活动概率参数：0.05、0.10、0.15、0.20、0.25；每条件物理场景 0–999、1000 MC。
- 固定条件：40 个候选用户、16 帧、SNR 0 dB、D 信道、DFT 导频、已知相位（仿真真值）、估计噪声。
- 共 20 组、20000 条结果；p=0.10 的 4000 条复用经核验的同输入四 baseline 原始结果，其余 16000 条新推断。复用不是新增独立样本。
- CPU 单 worker、4 线程、GPU worker 为 0；其他线程的实验保持原样。并发耗时只作诊断，不代表独占算法时延。

## 活动抽样与判决口径

沿用原生成器：独立 Bernoulli 活动向量条件于至少一名活跃用户。横轴 p 是条件化前的 Bernoulli 参数；接收机获得的边际先验为 `p / (1 - (1-p)^40)`，不提供实际活跃用户数。条件化后的期望活跃数为 `40*p / (1 - (1-p)^40)`，不是严格的 `40*p`；详细数值保存在 PLAN 的 `activity_sampling`。不改生成器以追求特定曲线。

最终评分采用 [用户采纳的历史规则](../../../snr_comparison/data/adopted_baseline_readout_20261025/README.md)：Off-grid SBL、SOMP 按接收机估计 SNR 最近节点查表；GNN-ASPL、GAMP-SBL 使用历史固定门限。节点 −4/−2/0/2/4/6 dB，中点取低档、范围外取端点，float64 >=，全零能量判不活动。不根据真实 SNR 查表，不拟合或选择新门限。

门限原在场景 0–499 拟合、500–999 选择，本批次评估场景 0–999 与其重叠，因此属于回顾性迁移评估，不能称为独立测试。固定接收 SNR 的生成约定和给定相位的仿真信息口径均与先前实验一致。

## 冻结记录与执行

`PLAN.json`/`PLAN_HASH.json` 冻结推断；`READOUT_APPLICATION_PLAN.json`/`READOUT_APPLICATION_PLAN_HASH.json` 冻结独立后处理。旧实验所有计划、代码、哈希和结果保留。本批次以已完成用户数计划为模板，只在新目录创建活动概率计划；源闭包唯一变化为无关绘图样式，证据见 `SOURCE_COMPATIBILITY.json`，该绘图文件不加入新推断闭包。

`PREFLIGHT.json` 核验 4000 条复用 JSON、compact、输入哈希以及与已完成用户数评分的判决一致性；检查四方法白名单、CPU 限制、条件先验、门限边界及失败拒绝。`REUSED_RESULTS.json` 保留原始结果指针。

首次正式推断命令：

```powershell
D:\afdm-gfra\.venv\Scripts\python.exe -B -X utf8 -u D:\afdm-gfra\result\activity_probability\data\known_phase_1000_baselines_20261025\parallel_run.py --plan D:\afdm-gfra\result\activity_probability\data\known_phase_1000_baselines_20261025\PLAN.json
```

不得重复启动或自动重试。进度按实际可用 `sceneNNNN/conditionNN/方法.json` 统计，`STATUS.completed` 不能直接加 4000。用户停止时用本批次 STOP 保存在途结果；不干预其他任务。

原始推断全部完成、driver 和 worker 实际退出后，核验 `INFERENCE_COMPLETE.json` 和 `RAW_RESULT_AUDIT.json`，再执行本目录 `finalize.py`。`finalize.py --check` 只校验已有冻结绑定；不重新冻结、不运行推断。独立结果写入 `selected_readout_20261025`，保留每场景实际门限、NMSE、AER、漏检率和虚警率。只有该子目录的有效 `COMPLETE.json` 代表本次最终评分完成。已有有效 COMPLETE 时验证后跳过；输出目录存在但未有效完成时保留证据并暂停，不覆盖或自动重试。

结果完成后再更新本实验索引和图片；自动跟进沿用 30 分钟间隔，正常进展不通知，失败或完成只报告一次。
