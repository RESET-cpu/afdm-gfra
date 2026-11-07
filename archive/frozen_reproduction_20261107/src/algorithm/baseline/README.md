# 四个基准

| 文件 | 内容 |
|---|---|
| somp.py | SOMP 迭代与接收适配 |
| gamp.py | GAMP-SBL 后验、噪声更新与接收适配 |
| gnn.py | GNN-ASPL 网络、权重加载与接收适配 |
| offgrid_sbl.py | Off-grid SBL 后验、连续偏移、噪声更新与接收流程 |

以 `_` 开头的三个文件只处理共用流程：`_base.py` 是配置和输入输出，`_common.py` 是公共读出规则，
`_validation.py` 校验当前实现。物理 AFDM 原子、共用相位估计及噪声估计在 `system/receiver`。

此目录只有当前四个基准。候选与停用实现已归档，不参与当前运行。
