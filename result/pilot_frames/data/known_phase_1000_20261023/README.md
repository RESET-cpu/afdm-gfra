# 导频帧数实验：1000 个 MC 场景

**2026-10-24 19:00（北京时间）：已完成。** 6 档导频 × 5 种方法 × 每条件 1000 MC（场景 0–999），共 30000 条结果，其中 5000 条复用、25000 条新算。原始完整性与最终 16 个文件的哈希核验通过，见 `MONITOR_FINAL_VERIFICATION.json` 和 `COMPLETE.json`。最终结果见 [固定门限报告](fixed_readout/REPORT.md)、[汇总数据](fixed_readout/SUMMARY.json)。baseline 应用 SNR 后 1000 场景校准出的固定门限，STMP 保持 0.5；信道 NMSE 和原始结果未改动。8 帧条件下 STMP 的 AER 为 0.807975、NMSE 为 33.029172 dB，已如实保留。并发耗时仅作诊断，不能作为独占算法时延。队列已因用户数 STOP 按要求退出，证据见 `QUEUE_PAUSE_VERIFIED.json`；用户数未启动新推断，保留 5000 条复用数据并暂缓。下方为历史安排。

**2026-10-24 用户更新：导频完成后暂停。** 当前导频继续跑完，随后核验原始结果并应用已冻结的 SNR baseline 门限，完成本批次汇总后暂停自动跟进；用户数实验暂缓。暂停请求及进程证据见 `PAUSE_AFTER_PILOT.json`。用户数批次的 `STOP.json` 只阻止下一项启动，不中断本导频。冻结队列届时会记录含 `Queue stopped` 的 `QUEUE_FAILURE.json` 并退出；仅在导频原始完成核验通过、用户数未启动且暂停证据吻合时，将其视为预期的用户暂停，保留原始记录。下方原队列顺序作为历史保留。

用户于 2026-10-23 明确授权：已结束的一阶去噪和收敛性实验保留原结果，其余后续实验只取前 1000 个场景；先复用，再补跑导频和用户数。

本批次固定 scene0000–scene0999，导频帧数 8、16、24、32、40、48；40 用户、0 dB、活动概率 0.1、D 信道、DFT 导频、已知相位、估计噪声。方法为 STMP、offgrid_sbl、gnn、gamp、somp，算法配置和权重与源 SNR 相同。STMP 最少 60 轮、最多 600 轮，相对变化阈值 0.0005。

16 帧条件与旧 SNR 的 0 dB 条件完全重合，已复用 **5000 份**结果；其余五档需补算 **25000 次**推断，完整批次为 **30000 份**结果。新指针引用旧导频目录中已逐份核验的本地副本，保留原始运行身份与计时。复用清单见 `REUSED_RESULTS.json`。

## 队列与进度

本目录的后台 `run_queue.py` 已启动。顺序为当前 SNR 补跑与门限校准完成 → 本导频实验 → [用户数实验](../../../user_count/data/known_phase_1000_20261023/README.md)。等待阶段不占用 GPU 或共享缓存锁。

- `QUEUE_STATUS.json`、`QUEUE_LAUNCH.json`：队列当前阶段及进程；准备或等待不等于推断已完成。
- `DEPENDENCY.json`：固定 SNR 依赖计划哈希；源实验失败或停止时不继续启动。
- `PLAN.json`、`PLAN_HASH.json`、`SOURCE_SNAPSHOT.json`：冻结的独立计划和源码快照。
- `PREPARATION_AUDIT.json`：准备、资产及复用检查。
- 启动计算后生成 `LAUNCH.json`、`STATUS.json`、`workers/`、`stdout.log`、`stderr.log`。
- `INFERENCE_COMPLETE.json`、`RAW_RESULT_AUDIT.json` 仅证明原始推断和数据审核结束。
- 最终活动判决统一应用 SNR 后 1000 场景校准出的固定 baseline 门限；STMP 保持 0.5。最终处理另用 `READOUT_APPLICATION_PLAN.json` 绑定，输出到 `fixed_readout/`，完成以 `COMPLETE.json` 为准。

四个 GPU 工作进程、一个 CPU 工作进程，各四线程，PASSIVE 等待；单批七天上限。并发耗时只作运行诊断，不能当作独占算法时延。共享场景复用不是新增独立样本。

本目录出现 `STOP.json` 时，队列停止继续启动；导频若正在运行，则停止派发并等待已派发任务结束。用户数已经启动时，应在用户数批次放置 `STOP.json`。进程异常退出保留全部输出，不自动重试、不删除锁。

旧 2000 场景导频计划已停用；其实际副本已裁剪到前 1000 场景，共 5000 份。删除了 2193 份超范围结果，记录见[清理审核](../known_phase_2000_20261023/TRIM_TO_1000.json)。旧冻结计划和源码保持原样。

Material Passport: academic-research-suite / experiment-agent；1000 场景独立执行批次。准备检查通过；实时进度以状态文件为准。
