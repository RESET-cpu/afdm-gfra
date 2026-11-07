## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run
- Origin Date: 2026-10-25
- Verification Status: ANALYZED
- Version Label: colored_first_append_500_v2

## 实验结果

用户要求追加新 score 网络曲线。已完成 500 个原物理场景、每场景 4 个候选信道、6 档复 AWGN 方差；新曲线有 6 个点，合计 12000 次信道去噪。原九条曲线的全部 54 个点逐项保留。完整批次用时约 214.5 秒，退出码 0；共享 GPU，耗时不作为算法时延比较。

新方法：有色噪声训练的一阶网络，epoch 200 EMA，50,000 个训练信道。权重 SHA-256 为 `7327d01785f10e3e18d76f7085604e1d1d53baa9d8cd80e12943768015452b91`。输入 C=vI、实协方差 vI/2，直接使用均值输出；未使用二阶网络或活动分类器。

## 输入配对与结果核验

完整观测文件并未全部保留；按原种子 202610180500001–202610180500500 和生成代码重建。每个条件的真值、观测、标准噪声三项数组哈希均与旧 cloud 一阶网络输入逐字节相同：3000 条条件，9000 项哈希核验通过。用户编号、尺度和噪声方差也完全相同。500 份紧凑输出重新汇总后与新曲线一致；旧 50k 误差与能量复核一致。全部模型和源码哈希在运行结束前核验通过，执行源码已保存于 source/。

原图四基线与 cloud 曲线的跨平台输入差异沿用原核验说明，不将它们描述为逐字节同一输入。原数据、图片与接收机绑定保留原样。

## 数值结果

以下为汇总误差能量与信号能量之比的 NMSE；差值为新网络减旧 50k 网络，负数表示改善。

| SNR (dB) | 旧 50k NMSE (dB) | 新网络 NMSE (dB) | 新−旧 (dB) |
|---:|---:|---:|---:|
| -20 | -0.267829 | -2.003405 | -1.735577 |
| -10 | -9.854704 | -11.965667 | -2.110963 |
| -0 | -17.924736 | -17.982855 | -0.058118 |
| 10 | -25.363650 | -24.054300 | +1.309350 |
| 20 | -32.835655 | -31.469486 | +1.366169 |
| 30 | -40.215560 | -39.218389 | +0.997172 |

在 −20、−10 dB 新网络点估计更低；0 dB 接近；10–30 dB 比旧 50k 网络高约 1.00–1.37 dB。此处没有显著性检验，也不能由 AWGN 结果断言有色噪声性能。

## 执行异常与处理

首次批次在 336 个场景后因 Windows 状态文件原子替换遇到短暂读取占用而中断。原批次保留于 `../colored_first_500_20261025/`，失败与修复记录见 EXECUTION_NOTES.json。只为进度文件增加有限次重试，计算逻辑未变；本目录重新计算了全部 500 个场景。两批共同的前 336 个场景误差数组逐位一致，最大差为 0。

批量预检查尝试 batch=24 时，逐元素差异未通过预设检查；正式运行保留已接入的 batch=4，没有放宽检查标准。差异与处理详见 BATCH_CHECK.json。

## 图片与复现

最终图为 `../../figures/colored_first_500_20261025_v2/channel_denoising.png`，同时提供 PDF、SVG 和绘图数据。新曲线为蓝色实线、空心三角。初稿图例遮住一个 Genie 点，最终版只缩小参考图例字体；60 个测量点均未被图例遮挡，坐标和原 54 点未改。最终绘图源码单独保存于图片目录 source/，这一排版修改发生在推断完成后。

从项目根目录，在新的空输出路径复现：

```powershell
& .\.venv\Scripts\python.exe -B -u src/evaluation/append_colored_denoising_20261025.py --output result/channel_denoising/data/colored_first_500_reproduction
& .\.venv\Scripts\python.exe -B src/evaluation/plots/channel_denoising_colored_20261025.py --input result/channel_denoising/data/colored_first_500_reproduction --output result/channel_denoising/figures/colored_first_500_reproduction
```

证据：PLAN.json、SUMMARY.json、NEW_CURVE.csv、scenes/、VERIFICATION.json、FINAL_AUDIT.json；原始文件哈希及新模型绑定均在记录中。
