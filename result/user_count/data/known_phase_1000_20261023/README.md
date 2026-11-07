# 用户数实验：1000 个 MC 场景

**2026-10-24 用户更新：导频完成后暂停。** 本用户数批次状态为 `DEFERRED_BY_USER`，尚未启动新推断。已放置 `STOP.json` 阻止顺序队列自动启动本批次；保留 5000 份复用结果，20000 次新推断暂缓。后续须由用户重新明确授权，不自动删除停止文件或重新启动。下方原接续安排作为历史保留。

固定 scene0000–scene0999，候选用户数 20、40、60、80、100；16 导频帧、0 dB、活动概率 0.1、D 信道、DFT 导频、已知相位、估计噪声。STMP 和四个 baseline 的算法配置、权重与本轮 SNR、导频批次一致。

40 用户条件与旧 SNR 的 0 dB 条件完全重合，已复用 **5000 份**结果；其余四档需补算 **20000 次**推断，完整批次 **25000 份**。复用数据指向旧导频目录中保留的前 1000 场景本地副本，来源、身份和哈希逐份核验，记录见 `REUSED_RESULTS.json`。

本批次已加入[后台顺序队列](../../../pilot_frames/data/known_phase_1000_20261023/README.md)：SNR 补跑及校准 → 导频 → 用户数。队列已启动；是否进入用户数计算，以本目录 `LAUNCH.json`、`STATUS.json` 和队列状态为准。

`PLAN.json`、`PLAN_HASH.json` 绑定本批次；`PREPARATION_AUDIT.json` 记录检查结果。推断结束生成 `INFERENCE_COMPLETE.json`、`RAW_RESULT_AUDIT.json`。随后应用 SNR 后 1000 场景得到的固定 baseline 门限，保留原始输出，另存 `fixed_readout/`，最终以 `COMPLETE.json` 为准。STMP 门限保持 0.5，不在本实验重新拟合门限。

四个 GPU 工作进程、一个 CPU 工作进程，各四线程，PASSIVE 等待，单批七天上限。并发耗时只作诊断，不代表独占算法时延。出现 `STOP.json` 时停止派发并等待已派发任务结束；异常不自动重试。

已结束的一阶去噪和收敛性实验保留原结果；本批次不重跑这两项。

Material Passport: academic-research-suite / experiment-agent；1000 场景独立执行批次。准备检查通过；实时进度以状态文件为准。
