# 配置入口

默认算法与版本以 [MAINLINE.json](../MAINLINE.json) 为准。当前正式比较为五方法、500 场景、估计相位和估计噪声。

| 配置 | 用途 |
|---|---|
| [proposed_frontend.json](proposed_frontend.json) | Proposed 当前默认公开入口：估计相位与噪声，再调用条件内核 |
| [proposed.json](proposed.json) | 三网络条件内核，阻尼 0.2、最多 600 轮、活动门限 0.5 |
| [baselines.json](baselines.json) | SOMP、GAMP-SBL、GNN-ASPL |
| [offgrid_baselines.json](offgrid_baselines.json) | Off-grid SBL，原网格与 120 轮预算 |
| [baseline_noise.json](baseline_noise.json) | 基线观测驱动噪声估计设置 |
| [readout_policy.json](readout_policy.json)、[offgrid_readout_policy.json](offgrid_readout_policy.json) | 冻结的活动判决规则 |
| [mainline_assets.json](mainline_assets.json) | 接收机资产校验清单 |
| [training/proposed.json](training/proposed.json)、[training/ldamp.json](training/ldamp.json) | 训练配方；新训练写入独立目录 |
| [ldamp.json](ldamp.json) | 保留的可选 L-DAMP 基线；当前 500 场景面板不包含它 |

## 历史配置与独立候选

`proposed_figure_20261009.json`、`evaluation.json` 对应历史已知相位比较。
`proposed_unknown_phase.json` 对应原未知相位、已知噪声入口。
其他 AMP、迭代相位、投影、平均及联合 L-DAMP 配置保留用于历史实验复现，不能替代当前默认配置。
这些 JSON 保持原内容和路径，以满足冻结源码及配置清单的绑定。当前运行所需的校准和权重均为正式目录中的实际文件。旧候选的大数组与训练断点已清理，历史配置本身不代表完整旧实验仍可运行。主要记录见 [docs/history](../docs/history/README.md)。
