# 状态文件写入修复与续跑

用户于 2026-11-04 明确授权“可以，请你修复并续跑”。原并发批次完成 498/6000 后停止：场景 82、4 dB 的进程替换公共 WORKER_STATUS.json 时收到 Windows PermissionError。算法推断尚未保存，原失败目录只有 INPUT_MANIFEST.json。

本目录保留独立的恢复脚本和执行计划。每份输入各写 worker_status/sceneXXXX_conditionYY.json，汇总 STATUS.json 仅由协调进程写入。状态显示写入遇到 PermissionError 时最多尝试三次，仍失败则输出明确警告并继续推断；输入、预测、评分等科研文件的写入仍严格检查。这里的状态写入重试不重新运行推断。

原 worker 文件通过模块载入，只替换它写公共状态文件时的目标路径与失败处理。接收机、配置、权重、随机输入、精度设置、停止规则、评分及最终报告均沿用原冻结版本。

准备阶段核验全部 498 份完整结果的哈希。失败目录在同一磁盘移至 failed_attempts_20261104，保留所有原字节、日志与路径映射。先单独执行之前失败的场景 82、4 dB，保存核验成功后，再按原内存门槛恢复最多四路并发。已有完整结果不重跑。

新计算失败时停止新派发，等待在途任务结束，记录失败；不会自动重试。每份输入保留原两小时超时。原批次或本目录的 STOP.json 请求停止派发并保存当前在途结果。

全部 6000 份结果完成后运行原 parallel_20261103/report.py，重新评分并核验全量输入和参照；随后核验恢复源文件和全部保留结果。性能结论需要完整配对结果，计算完成不等于性能通过。

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run
- Origin Date: 2026-11-04
- Scope: user-authorized status I/O repair and recovery of the existing experiment
- Verification: concurrent status-write regression, actual Windows lock regression, preserved file hashes, real failed-case recovery
- State: see STATUS.json; verification records describe their own checkpoint only
