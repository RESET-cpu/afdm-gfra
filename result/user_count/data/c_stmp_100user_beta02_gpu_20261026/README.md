# 100用户15个问题场景：GPU β=0.2复验

## Material Passport

- Mode: run; date: 2026-10-26; user explicitly authorized this bounded experiment.
- 固定场景（0起始）：18、19、20、43、49、50、55、56、58、71、78、90、95、96、98。
- 同一100用户、16帧、0 dB公开输入、已知相位、估计噪声；只改新消息权重β从0.4为0.2。
- 600轮上限、最少60轮、全部原收敛条件、权重、门限、探针和噪声规则保持原样。
- 单个独立GPU进程、2个CPU线程；使用与原运行相同的setup，关闭TF32和cudnn benchmark。
- 与原β=0.4的15份GPU原生输出配对；不复用之前120轮CPU结果，不额外重复β=0.4推断。
- 原500场景批次的进程、计划、代码、权重和控制文件不变。两批共享GPU算力，不能据此比较单次时延。

入口：`python -B -X utf8 -u result/user_count/data/c_stmp_100user_beta02_gpu_20261026/run.py prepare`（准备），之后`run`（执行一次）。

`START.json`记录真实PID、创建时间、完整命令及计划哈希；`STATUS.json`每20轮与每个场景结束更新。
`STOP.json`仅停止本独立批次后续派发、保留当前场景；不触及主实验。6小时上限，无崩溃自动重试。
有限未收敛输出完整保留。`INFERENCE_COMPLETE.json`之后还需完成保存结果重评分和核验；最终看`COMPLETE.json`与`STATUS COMPLETE`。

最终输出：15份NPZ与逐轮JSON、`SUMMARY.json`、`comparison.csv`、`REPORT.md`、`AUDIT.json`、`COMPLETE.json`。
每例报告NMSE、漏检、虚警、迭代数及是否满足原收敛条件。完成后本进程退出，不启动其他实验。
这是按原失败结果选择的诊断样本，不将15例的改善直接推广为完整500场景性能。
