# 独立研究入口

当前比较为 Proposed 与四个 baseline，见 [README](../README.md)。L-DAMP 的已注册入口和资产继续保留。
本轮算法探索已结束；历史实验代码见[归档与恢复](../docs/history/archive/workspace_cleanup_20261016/README.md)，当前实验和依赖见[实验索引](../docs/history/experiments/README.md)。
独立研究入口保留 Zhao EM-GAMP：

```sh
.venv/bin/python -B run.py research --method em --input INPUT.npz --output NEW_EM.npz
```

该命令经 `algorithm/research.py` 分派，实现为 `algorithm/baselines/em_gamp_zhao2025.py`，
配置为 `configs/baselines.json`，验证范围见[检查报告](../docs/history/results/baseline_core_check_20261010/REPORT.md)。

Off-grid SBL 使用主图版 [offgrid_baselines.json](../configs/offgrid_baselines.json)，
配套 [offgrid_readout_policy.json](../configs/offgrid_readout_policy.json)，入口为 `run.py run --method offgrid_sbl`。

MNOMP 的源码、配置、专用实验和结果见[独立归档](../docs/history/archive/mnomp_20261014/README.md)。
已有实验结果及其中的冻结设置是历史来源记录，不作为当前配置入口。
