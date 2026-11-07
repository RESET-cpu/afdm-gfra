> 2026-10-18 本地 README 的历史副本。下文链接和命令以当时项目根目录为基准，不是当前十层入口说明。
> 当前本地结构见 [根 README](../README.md) 和[代码导读](../docs/CODE_GUIDE.md)。本文件的旧规模、收敛实验和未完成训练描述仅作历史记录。

# AFDM JADCE

当前主线为 Proposed、SOMP、GAMP-SBL、GNN-ASPL、Off-grid SBL，默认估计相位与噪声。版本和资产绑定见 [MAINLINE.json](MAINLINE.json)。Off-grid SBL 最多 120 轮；Proposed 保持原三网络及停止规则。

主线、训练资产和七项实验的运行依赖均位于正式目录，可以在不包含 `archive/` 的工作区中运行。独立性核验见[清理与验证记录](results/cleanup_20261018/REPORT.md)。

## 七项实验

每项实验一个入口，统一提供 `plan / run / summarize`；参数、分工和复用规则见 [experiment/README.md](experiment/README.md)。

| 实验 | 入口 | 默认条件 |
|---|---|---|
| SNR | [snr_comparison.py](experiment/snr_comparison.py) | −4、−2、0、2、4、6 dB；每点 500 场景 |
| 导频帧数 | [pilot_frames.py](experiment/pilot_frames.py) | 8、16、24、32、40、48 |
| 用户数 | [user_count.py](experiment/user_count.py) | 20、40、60、80、100 |
| 活动概率 | [activity_probability.py](experiment/activity_probability.py) | 0.05、0.10、0.15、0.20、0.25 |
| 收敛 | [convergence.py](experiment/convergence.py) | −4、0、4 dB；20 场景；含 Proposed 导频类型对照 |
| 独立去噪 | [channel_denoising.py](experiment/channel_denoising.py) | 六档噪声方差；含 Genie 下界 |
| 跨信道 | [cross_channel.py](experiment/cross_channel.py) | NTN-TDL-D/A/B/C；六档 SNR |

训练样本量对照仅用于 SNR 和去噪，小样本权重尚待训练。七项实验尚未全部正式运行。

## 已完成结果

[500 场景正式比较](results/baseline_comparison_500_20261018/REPORT.md)覆盖 −4～8 dB、五方法，共 17,500 份结果。完整原始数据在 [baseline_comparison_600_20261017](results/baseline_comparison_600_20261017/)，目录名沿用原计划。

当前六档 SNR 对应的 15,000 份结果可以复用；匹配配置、输入与相位后直接读取已有结果。历史结果的执行设备及耗时来源保留。

## 常用命令

```sh
.venv/bin/python -B run.py verify
.venv/bin/python -B scripts/train_proposed.py --inspect --check-assets
.venv/bin/python -B experiment/snr_comparison.py plan --output results/snr_new
.venv/bin/python -B experiment/snr_comparison.py run --output results/snr_new
.venv/bin/python -B experiment/snr_comparison.py summarize --output results/snr_new
.venv/bin/python -B -m pytest -q tests
```

新实验使用新的输出目录；已有计划和结果不覆盖。源码、配置或权重发生变化后重新创建计划。

核心算法在 `src/`，当前配置、模型和训练数据分别在 `configs/`、`models/`、`data/`；训练工具见 [scripts](scripts/README.md)。`experiments/` 仅保留冻结批次及当前训练所需的少量[辅助文件](experiments/README.md)。

旧实验的主要报告、日志和引用依据集中在 [docs/history](docs/history/README.md)。`archive/` 只保留按项目约定保存的 [Proposed 冻结副本](archive/proposed_mainline_20261015/README.md)，不参与当前运行。论文与文献位于 `paper/`、`references/`。Git 自动快照保持停用。
