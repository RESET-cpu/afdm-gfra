# 算法

本目录保留冻结批次源码。日常入口使用 [工作登记](../configs/organized/algorithms.json) 和 `receiver.registry`；本目录旧登记与混合历史绑定不代表当前方法清单。

| 位置 | 用途 |
|---|---|
| `STMP/` | 三网络 STMP 及其已有相位处理实现 |
| `GP_MP/` | 当前白噪声主线：已知相位 Receiver、估计相位 PhaseReceiver、独立 Denoiser |
| `C_STMP_variance_em_20261025/` | 历史有色接收机；退出默认登记，冻结源码保留 |
| `C_STMP_phase_selection_20261030/` | 历史相位候选，保留用于旧结果复现 |
| `C_STMP/`、其他 `C_STMP_*`、`candidates/` | 既有实现和研究候选；保留原路径供配置、测试及历史结果引用 |
| `proposed/` | 旧路径保留的共用相位计算模块；DU 已退出工作入口和发布清单 |
| `baseline/` | `somp.py`、`gamp.py`、`gnn.py`、`offgrid_sbl.py` 四个基准实现 |
| `registry.py` | `build_algorithm` 统一构造入口及 `build_receiver` 接收机检查入口 |

基准的共用输入、噪声处理及保存逻辑在 `_base.py`，矩阵检查与活动读出在 `_common.py`，源码校验在 `_validation.py`。共用网络位于 `src/networks/`，相位与噪声估计位于 `src/system/receiver/`。

当前展示名称为 **GP-MP / GP-MP-EP**。`C_STMP` 仅保留为当前白噪声 GP-MP 的兼容标识；旧有色构造入口须显式使用[历史登记](../configs/historical/algorithms_colored_20261107.json)或旧冻结计划。新包不导入旧有色实现、训练包或实验适配器，权重加载严格验证白噪声训练来源。数值运算、参数及权重保持已有验证版本，见[提取对照](../../archive/white_mainline_20261107/EXTRACTION.json)和[GPU 回放](../../archive/white_mainline_20261107/VALIDATION.json)。
