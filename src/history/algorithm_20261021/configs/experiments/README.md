# 实验配置

七个实验的统一配置映射在 `experiment/_support/settings.py`，计划会保存实际配置路径。

- 当前 Off-grid SBL 使用 `../offgrid_baselines.json`：最多 120 轮、容差 1e-4，满足原条件提前停止。
- 活动阈值使用其绑定的 `../offgrid_readout_policy.json`，与已有 500 场景结果一致。

Proposed 继续使用 `../proposed.json` 的三网络和原停止规则；其他三种 baseline 使用 `../baselines.json`。
通用 `run.py` 与七项实验中的接收机入口均自动选择上述配置。

本目录的 `offgrid_sbl_600.json` 和 `offgrid_readout_600.json` 保存已完成的 10 场景预算补测配置，供该历史结果复现。
