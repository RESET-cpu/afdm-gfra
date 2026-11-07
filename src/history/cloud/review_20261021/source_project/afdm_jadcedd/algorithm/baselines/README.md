# Baseline 实现

所有 baseline 推断实现的实体文件集中在本目录。

| 位置 | 内容 |
|---|---|
| `somp.py` | SOMP |
| `gamp_sbl_mmv.py` | GAMP-SBL |
| `gnn_aspl.py` | GNN-ASPL |
| `em_gamp_zhao2025.py` | EM-BG-AMP 研究实现 |
| `receiver.py`、`common.py`、`ding.py`、`readout.py` | 公共接收机、计算与活动判决 |
| `offgrid/` | Off-grid SBL |
| `ldamp/` | L-DAMP；当前比较不启用 |
| `ldamp_joint/`、`ldamp_score/`、`ldamp_output.py` | 保留的 L-DAMP 变体 |
| `unknown_phase_baselines.py` | 估计相位接入与公共接收机分派 |
| `baseline_noise.py`、`noise_estimation.py`、`offgrid_noise.py` | 基线噪声估计与推断接入 |
| `baseline_phase.py`、`baseline_phase_posterior.py` | 保留的相位不确定性处理实现 |

## 导入与运行

所有 baseline 模块统一从 `afdm_jadcedd.algorithm.baselines` 导入，例如：

```python
from afdm_jadcedd.algorithm.baselines.offgrid.receiver import OffGridReceiver
from afdm_jadcedd.algorithm.baselines.ldamp.receiver import LDAMPReceiver
from afdm_jadcedd.algorithm.baselines.baseline_noise import EstimatedNoiseBaselineReceiver
```

命令入口仍为项目根目录的 `run.py`。配置、权重、训练入口和历史实验按项目统一目录管理。
共享相位估计 `algorithm/phase_estimation.py`、输入模型 `algorithm/unknown_phase_model.py`
和总入口 `algorithm/registry.py` 位于公共层。

当前源码与活动判决绑定见 `configs/mainline_assets.json`。
目录迁移和数值核对见 [整理记录](../../../../results/baseline_package_20261016/REPORT.md)。
