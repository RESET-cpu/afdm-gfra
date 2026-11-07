# 额外场景、固定门限校准

按用户 2026-10-23 的最新要求执行，取代主实验前 1000 场景的门限校准方案。

- 校准：额外 500 个物理场景，种子 `202610239300001` 起。
- 验证：额外 500 个物理场景，种子 `202610239400001` 起。
- 每个场景包含 −4、−2、0、2、4、6 dB；已知相位、估计噪声。
- 四个 baseline 各拟合一个固定标量门限，所有 SNR 共用；不使用分档门限。
- STMP 已采用固定后验活动概率门限 0.5，保持该值。
- 仅校准集用于最小化总误判数；相同时先选虚警少者，再选较小门限。
- 门限在验证前冻结；验证仅报告性能，不选择策略或重新调门限。
- 主实验种子不参与新拟合。主实验曾被查看过的历史事实保留。

复用原独立批次的推断程序、审核函数、独立种子及共享缓存。此前完成的 880 份校准输出按哈希复用，
后续输出继续存入该缓存；本批次的计划、指针、门限、统计与日志单独保存于当前目录。
原独立批次的旧 `run.py run` 保持停止，不启动其分档选择流程。

执行入口：

```powershell
.venv\Scripts\python.exe -B result\snr_comparison\data\baseline_fixed_independent_20261023\run.py check
.venv\Scripts\python.exe -B -u result\snr_comparison\data\baseline_fixed_independent_20261023\run.py run
```

采用一路 CPU、4 线程、PASSIVE 等待，不占用 STMP 的 GPU。不改变正在运行的 2000 场景实验。
进度见 `STATUS.json`、`stdout.log`；完成后生成 `FROZEN_READOUT.json` 和 `READY_FOR_MAIN_POSTPROCESSING.json`。
主实验结果可按保存的分数重新判决，不需重跑信道推断，NMSE 保持原值。
后续按授权对固定前 1000 场景重新统计与绘图；旧图保留，但不作为本协议结果。
