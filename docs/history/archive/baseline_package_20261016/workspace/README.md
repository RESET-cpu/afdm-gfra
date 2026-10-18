# AFDM JADCE

当前研究主线为 **Proposed + SOMP、GAMP-SBL、GNN-ASPL、Off-grid SBL**。Proposed 使用原导频、原三网络和消息迭代，阻尼 0.2，活动概率门限 0.5。版本绑定见 [MAINLINE.json](MAINLINE.json)，冻结副本与重放入口见 [主线说明](docs/PROPOSED_MAINLINE.md)。

接收机默认从观测估计跨帧相位。Proposed 使用给定物理噪声方差；四个 baseline 默认估计噪声。比较时须按结果记录明确噪声信息条件。L-DAMP 的实现、配置与权重仍保留为可选基线，本轮比较不包含它。

## 当前结果

| 结果 | 场景与 SNR | 信息条件 |
|---|---|---|
| [原导频五方法配对实验](results/proposed_original_snr8_10_20261016/FINDINGS.md) | 10 个场景，−4～10 dB、间隔 2 dB；400 次推断完成 | 估计相位；统一供给准确物理噪声方差 |
| [四 baseline 的 1000 场景实验](results/baselines_1000_20261015/REPORT.md) | 1000 个场景，−4～6 dB、间隔 2 dB；24000 次推断完成 | 估计相位、估计噪声 |
| [历史图及复核](results/historical_figure_verification_20261016/REPORT.md) | Proposed 100、三个 baseline 各 1000、Off-grid SBL 20 场景；−4～6 dB | 已知相位；Proposed 阻尼 0.1 |

这些实验的场景与信息条件不同，分别记录和解释。完整结果入口见 [结果索引](results/README.md)。

## 常用入口

```sh
.venv/bin/python -B run.py info
.venv/bin/python -B run.py verify
.venv/bin/python -B run.py simulate --seed 202610090100001 --snr 0 --output NEW_CASE
.venv/bin/python -B run.py run --method proposed --input NEW_CASE/input.npz --output NEW_PROPOSED.npz --device mps
.venv/bin/python -B run.py run --method offgrid_sbl --input NEW_CASE/input.npz --output NEW_SBL.npz
.venv/bin/python -B run.py evaluate --estimate NEW_SBL.npz --truth NEW_CASE/truth.npz
.venv/bin/python -B run.py test
```

输出使用新路径。已知相位理想参考需在生成和推断时显式指定 `--phase-mode known`；基线的准确噪声参考显式指定 `--noise-mode known`。相位和噪声是分别控制的信息条件，见 [实验协议](docs/EXPERIMENT_PROTOCOL.md)与[噪声说明](docs/BASELINE_NOISE.md)。

## 代码与材料

| 内容 | 入口 |
|---|---|
| 系统模型、导频和观测 | [system](src/afdm_jadcedd/system/) |
| Proposed、基线与相位／噪声估计 | [algorithm](src/afdm_jadcedd/algorithm/) · [代码导读](docs/CODE_GUIDE.md) |
| Baseline 实现集中目录 | [baselines](src/afdm_jadcedd/algorithm/baselines/README.md) |
| 场景生成、评分和训练 | [experiment](src/afdm_jadcedd/experiment/) · [训练入口](scripts/README.md) |
| 配置、网络和数据 | [configs](configs/README.md) · [models](models/README.md) · [data](data/README.md) |
| 当前实验及复现依赖 | [实验目录](experiments/README.md) |
| 文档、论文与文献 | [docs](docs/README.md) · [paper](paper/README.md) · [references](references/README.md) |
| 历史探索与恢复清单 | [本次归档](archive/workspace_cleanup_20261016/README.md) · [归档总索引](archive/INDEX.md) |

[当前阶段](docs/CURRENT_STAGE.md)记录已完成工作；[工作区索引](docs/WORKSPACE_INDEX.md)说明材料位置。Git 自动快照保持停用。
