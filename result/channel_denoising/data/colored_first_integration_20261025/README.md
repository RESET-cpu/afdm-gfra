# 新一阶网络接入独立去噪

同日后续：用户已明确要求追加旧图，新网络的原 500 场景补算及十曲线图已完成，见[结果报告](../colored_first_500_20261025_v2/REPORT.md)。以下保留初次接入时的状态；独立 1000 场景计划仍未启动。

2026-10-25 用户要求将新 score 网络加入去噪实验。方法标识为 `pretrained_colored_first`，在默认配置中与 `pretrained_first`、noisy、Gaussian、Genie 一起比较。

权重来自 `colored_preconditioned_50000_matched_20261024/first_best.pt`：200 轮训练已完成，选中 epoch 200 EMA，SHA-256 为 `7327d01785f10e3e18d76f7085604e1d1d53baa9d8cd80e12943768015452b91`。配套二阶网络不参与一阶均值去噪。

适配器位于 `src/evaluation/colored_denoising.py`。统一入口提供相同的候选信道真值和复 AWGN 观测，复协方差为 `C=vI`，实坐标协方差为 `vI/2`；新 checkpoint 的 `forward` 直接返回条件均值，不再次执行 score 到均值的转换。输入、方差和输出按 checkpoint 的 population RMS 换算，普通方法无法读取 Genie 的真值先验。公式沿用 `paper/docs/COLORED_PRECONDITIONED_TRAINING_20261024.md`，未新增算法定义。

检查用 `smoke/` 保存一个独立开发场景、4 个候选信道、六档方差和五种方法的端到端结果；不据此判断总体优劣。`plan/` 为独立的 1000 场景新计划，六档方差为 0.001、0.01、0.1、1、10、100（标称 SNR 为 30、20、10、0、−10、−20 dB），仅准备，不启动批量推断。

已完成的 500 场景九曲线论文数据使用历史协议，仍保留在 `data/current/` 和 `figures/current/`。新计划的场景与协议不可直接混入原图；追加旧图需要在其保存输入上另行计算新网络结果。此次不改写旧计划、冻结模型绑定、原有权重或论文图。

从仓库根目录核验已准备的新计划：

```powershell
& .\.venv\Scripts\python.exe -B run_experiments.py channel_denoising inspect --output result/channel_denoising/data/colored_first_integration_20261025/plan
```

用户明确启动正式实验时执行（本次未执行）：

```powershell
& .\.venv\Scripts\python.exe -B run_experiments.py channel_denoising run --output result/channel_denoising/data/colored_first_integration_20261025/plan
& .\.venv\Scripts\python.exe -B src/evaluation/plots/channel_denoising.py --input result/channel_denoising/data/colored_first_integration_20261025/plan --output result/channel_denoising/figures/colored_first_20261025
```

修改前文件保存在 `before/`；测试及检查证据见 `VERIFICATION.json`。该记录不将一个开发场景当成正式实验结果。
