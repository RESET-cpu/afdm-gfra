# 算法

算法通过 [src/configs/algorithms.json](../configs/algorithms.json) 登记，由 `registry.py` 构造。具体实验使用计划中保存的算法配置。

| 位置 | 用途 |
|---|---|
| `STMP/` | 三网络 STMP 及其已有相位处理实现 |
| `C_STMP_variance_em_20261025/` | 当前 `C_STMP` 登记指向的实现 |
| `C_STMP_phase_selection_20261030/` | 独立相位版本，尚未替换默认登记 |
| `C_STMP/`、其他 `C_STMP_*`、`candidates/` | 既有实现和研究候选；保留原路径供配置、测试及历史结果引用 |
| `proposed/` | 固定十层深度展开；登记名 `DU` 与保留的 `proposed` 别名 |
| `baseline/` | `somp.py`、`gamp.py`、`gnn.py`、`offgrid_sbl.py` 四个基准实现 |
| `registry.py` | `build_algorithm` 统一构造入口及 `build_receiver` 接收机检查入口 |

基准的共用输入、噪声处理及保存逻辑在 `_base.py`，矩阵检查与活动读出在 `_common.py`，源码校验在 `_validation.py`。共用网络位于 `src/networks/`，相位与噪声估计位于 `src/system/receiver/`。

当前稿件的展示名称 **GP-MP-CCD** 与存储标识 `C_STMP` 的对应关系见[稿件术语表](../../paper/C-STMP/docs/TERMINOLOGY.md)。本页仅整理代码导航，不改变方法定义或模型绑定。
