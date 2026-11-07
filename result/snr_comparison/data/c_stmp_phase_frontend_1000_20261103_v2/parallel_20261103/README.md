# RTX 5080 并发执行

用户请求：让 5080 充分运行。此次只调整已授权的 6000 份实验的执行方式。

原单进程调度在保存当前输入后停止，已完成 171 份。PRESERVED_OUTPUTS.json 核验并记录这些结果的哈希；后续只派发剩余输入。原接收机、配置、权重、GPU 精度设置和逐输入 worker 都不修改。

- 最多 4 份输入并行，每份使用原 worker、2 个 CPU 线程、完成后退出。
- 预留每个正在初始化的进程尚未分配的内存；可用内存不足时等待，不强行派发。
- 保留至少 1.25 GiB 系统内存余量作为派发门槛，每进程预估峰值 1.8 GiB。
- 每份输入仍为两小时硬超时；运行错误停止新派发，等待其他在途输入保存，不自动重试。
- 原批次目录或本目录的 STOP.json 均可请求保存完在途输入后停止。
- STATUS.json 和上一级 STATUS.json 同步更新，列出全部在途输入；telemetry.jsonl 记录 GPU 利用率、功耗、显存和系统内存。

串行基准连续采样 30 秒，平均 GPU 利用率 24.9%，平均功耗 102.8 W；它是当时运行环境的观测，不是独占硬件基准。原数据输入约一半推断时间用于 CPU 相位估计，并发使不同输入的前端和 GPU 计算重叠。

本目录 report.py 是独立的历史指针兼容修订：部分原已知相位指针没有 scene/index，完整身份从已冻结且哈希核验的结果 JSON 检查。原冻结报告保留。本修订不改变评分、样本范围或绘图数值。全量完成后自动重新评分并核验原 6000 输入及参照，原有输出哈希再次核验。

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run
- Origin Date: 2026-11-03
- State: independent execution handoff; see STATUS.json for live progress
- Scope: resource scheduling and historical result-pointer compatibility; no algorithm or precision change
- Verification: original bindings, preserved output hashes, scheduling checks and report-reader checks
