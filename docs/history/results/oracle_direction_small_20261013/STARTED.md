# 16×16 一阶续训已启动

后续状态：本次三阶段训练及预定评估已完成，见 [REPORT.md](REPORT.md)。下文保留启动时的记录。

启动日期：2026-10-13（Asia/Shanghai）。已启动的是小一阶网络；不是完整 16×16×16 网络。

- 已有40轮；新增最多360轮；累计上限400轮。
- 每轮50,000信道，固定5,000验证信道。当前数据及方向合并后的噪声范围与历史不同，基线重新测得验证loss **0.4214598298**。
- 收敛判定采用固定验证loss的平台期，包含学习率降到1e-6后的检查；预算耗尽独立标记。
- 一阶结束后自动重训配套二阶、按当前平衡BCE方法训练小证据网络、运行新场景真实方向对照。
- 初始权重保存在weights，选定权重及恢复状态保存在first、second、activity。正式完整网络已单独复制并校验，作为固定对照。

本文件仅记录启动事实；实时状态见 [PIPELINE_STATUS.json](PIPELINE_STATUS.json)、
[一阶状态](first/status.json)、[一阶历史](first/history.json)。
数值与梯度检查见 [CHECKS.json](CHECKS.json)；底层矩阵乘法出现过已有运行时警告，
检查输出均有限且代数等式达到报告的误差，不将检查通过解释为警告原因已解决。

实际命令（在项目根目录运行，可读取恢复状态）：

```sh
.venv/bin/python -B results/oracle_direction_small_20261013/runtime/experiment/train.py
```

重新运行前必须确认既有进程已经退出；PID和日志路径见 [LAUNCH.json](LAUNCH.json)。
不要并发启动第二份。训练期间可在当前阶段目录添加 `pause.request`，程序将保存状态后退出。

运行来源：academic-research-suite / experiment-agent；用户已明确授权续训与后续对照。
尚无本次训练完成或新NMSE/AER改善的结论。
