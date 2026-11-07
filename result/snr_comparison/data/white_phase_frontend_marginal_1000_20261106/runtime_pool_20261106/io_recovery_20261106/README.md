# 2026-11-06 协调器状态读取修复

原常驻队列在 23:19 读取 `worker1/STATE.json` 时遇到 Windows
`PermissionError`。协调器退出后，两名工作进程完成已接收的输入并正常退出。
原 STATUS 只登记到 4114；实际已完整保存 4116 份，无工作进程推断失败。

故障原文、当时状态和启动记录保存在 `BEFORE_*.json`；原根目录故障文件已移至
`RESOLVED_FAILURE.json`，未删除。`INCIDENT.json` 保存退出身份及前置完成证据。
`RESULT_AUDIT.json` 和 `prelaunch_validation/` 记录 4116 份完整预测的重评分、
来源及输出哈希检查；不存在不完整或无指针输出。

独立入口为 `evaluation.white_phase_pool_io_20261106.run coordinate`。它调用原常驻
协调器，仅对本批次 `sessions/<id>/worker<slot>/STATE.json` 的权限异常进行最多
11 次读取，间隔 0.05 秒；恢复或耗尽均记录日志。持续权限异常、坏 JSON、其他文件
错误和推断失败继续报错。旧池源码、推断、配置、权重、相位、精度、停止规则和预算
均保持。工作进程仍由原 `evaluation.white_phase_pool_20261106.run worker` 执行。

12 项 CPU 检查通过，包括真实 Windows 独占文件的访问失败及释放后恢复、持续异常
仍失败、非状态文件不重试、原 STOP/验证/重复进程门控。记录见 `CPU_CHECK.json/log`。
原四次 GPU 保存数组一致性验证继续适用；此修复没有运行额外 GPU 验证输入。

新适配绑定见 `AMENDMENT.json`，其 SHA-256 为
`bd3c0fe5e1139e70c84c2b12eebe5013ab0074d8d6cc209dc95f9d9008dc98cf`。
原 PLAN 和 runtime pool AMENDMENT 保持。`RESOLUTION.json` 关联修复和核验收据。

隐藏启动收据见 `LAUNCH.json`。实际协调 PID 34700，创建时间
1793978734.5316892，session `1793978739718595600`。START/STATUS 的
`execution_module` 仍记录原池；身份检查同时核对实际命令行中的新协调入口。
启动后原协调器再次完整核验 4116 份，再只派发缺少的 1884 份。
本次恢复不是无条件重试推断；若出现新的失败仍保留现场并检查。

自动跟进 `snr-2` 已更新，记录见 `AUTOMATION_UPDATE.json`；旧任务内容已备份。
最终 6000 份验证、18000 份配对重评分、主 SNR 图和稿件更新仍待完成。
