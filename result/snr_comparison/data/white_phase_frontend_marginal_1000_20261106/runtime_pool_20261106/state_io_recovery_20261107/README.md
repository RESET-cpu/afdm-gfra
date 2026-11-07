# 2026-11-07 状态文件写入修复

旧 session `1793978739718595600` 的 worker0 在写入 position 4483 的 BUSY 状态时，
原子文件替换遇到 Windows `PermissionError`。错误发生在调用推断前；该位置没有
原生输出目录或结果指针。FAILURE 中四条记录是同一故障的重复观察。

协调器停止派发，另一工作进程正常排空。全部进程退出后，4483 份已有结果通过
保存数组重评分、哈希、来源和覆盖检查，无不完整或无指针输出。记录见
`INCIDENT.json`、`RESULT_AUDIT.json`、`prelaunch_validation/`。原故障移至
`RESOLVED_FAILURE.json`，另保留 `BEFORE_*.json`，没有删除失败或已有结果。

此前独立修复只覆盖读取；本次同时覆盖工作状态的读取与写入。新启动入口为
`evaluation.white_phase_pool_stateio_20261107.run`，协调器和 worker 均使用它。
它调用原 pool 的 coordinate、worker、execute_case 函数，源码和数值计算保持。
只有 `sessions/<id>/worker<slot>/STATE.json` 的 PermissionError 最多尝试 11 次，
每次间隔 0.05 秒；写入重用原原子 JSON 写入器与同一个状态值。持续错误、坏 JSON、
其他文件错误和推断失败不会自动重试。成功或耗尽均记入每进程的状态 I/O 日志。

19 项 CPU 检查通过，包括真实 Windows 读取占用阻止原子替换、释放后恢复，以及
连续并发读写检查。见 `CPU_CHECK.json/log`。冻结推断、权重、配置、输入、相位、
FP32、停止规则与 6000 份预算保持，原四次 GPU 数值验证继续适用，没有新增验证推断。

新 AMENDMENT SHA-256：
`ad1077c20d66ab15f7a61327413ef1db194fbc198418767ec2308a01c6c02e94`。
原 PLAN、pool AMENDMENT 和上一版读取修复均保持。新结果 execution.module 标识新
启动入口，parent amendment 仍指向原 pool；需要同时核对本适配绑定和启动收据。

隐藏启动记录见 `LAUNCH.json`。实际协调 PID 103312，创建时间
1793982309.0433996，session `1793982314807331900`。原协调器会再次核验 4483 份，
仅派发剩余 1517 份；position 4483 先前尚未开始推断。最多三个常驻工作进程，
仍按原 RAM/VRAM 门控启用。自动跟进已更新至新入口，旧配置完整备份。

最终 6000 份核验、三种方法共 18000 份数组重评分、主 SNR 图与稿件更新仍待完成。
