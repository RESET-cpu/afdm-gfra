# 收敛对比：50 个场景，每种方法实际运行 300 轮

独立配置为 `src/configs/experiments/convergence.json`，默认输出为
`result/snr_comparison/data/convergence_50x300_20261105`。本次只准备脚本与计划，不启动批量实验。

固定使用主 SNR 输入中的场景 0–49、0 dB、已知相位、观测估计噪声，五种配置共 250 次推断：
STMP、当前白噪声训练及匹配分类器的 GP-MP、Off-grid SBL (7/13/25)。场景按编号选择，不按性能或收敛状态筛选。
输入、权重、原配置、代码及活动检测规则均记录 SHA256。STMP 阻尼保持 0.2，GP-MP 保持 0.4。

通过独立函数副本关闭原求解器的提前停止，实际执行 300 轮，不用重复末值补齐曲线。
原停止判据仍逐轮记录，并报告首次满足的轮次；数值更新、SBL warmup、网格、候选预算和检测规则保持原定义。
原冻结模块不修改，不影响主 SNR 或正在运行的批次。

每轮记录每用户误差平方和、活动判决、活动概率或 SBL 分数，以及原生诊断。
SBL 采用该轮更新后的参数重算后验并重建信道，与原算法在该轮返回时的定义一致。
真值只进入被动指标收集器，不参与接收机更新。最终输出与第 300 轮记录必须一致。
NMSE 按 50 场景总误差能量除以总信号能量后转 dB；AER 按总错判人数除以总用户数。
缺少任何场景、失败或缺少任何轮次时，不产生完整汇总；保留失败及部分轨迹，不自动重试。
额外的 SBL 后验重算与逐轮计分会增加运行时间，本实验的时间不用于算法耗时比较。

在项目根目录运行：

```powershell
# 准备、检查：不加载网络、不推断
& .\.venv\Scripts\python.exe -X utf8 -B run_experiments.py convergence plan
& .\.venv\Scripts\python.exe -X utf8 -B run_experiments.py convergence inspect

# 显式执行：串行，每次推断使用独立进程，FP32 / TF32 关闭
& .\.venv\Scripts\python.exe -X utf8 -B run_experiments.py convergence run

# 全部完成后可独立重新核验并汇总
& .\.venv\Scripts\python.exe -X utf8 -B run_experiments.py convergence summarize
```

`plan` 要求新输出目录。`run` 可跳过已核验的完整结果；发现失败或未完整写入的目录会停下保留现场。
本入口不更新论文图片。待真实的 50×300 结果完整后，再将 `SUMMARY.json` 交给论文绘图流程。
