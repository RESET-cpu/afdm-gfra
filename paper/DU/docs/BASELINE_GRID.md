# 当前整数时延/Doppler 字典

配置集中在 [baselines.json](../../../src/configs/baselines.json)，实现为 `system/dictionary.py`。

| 项目 | 当前值 |
|---|---|
| N | 16 |
| 时延采样点 | 0,1,…,15，步长 1 |
| 归一化 Doppler | −2,−1,0,1,2 |
| 子载波间隔 / Doppler 步长 | 30 kHz |
| 每用户原子数 | 80 |

网格依据 [Ding p.2 式(8)、p.5 §IV-A](../../../reference/literature/ding2026.pdf) 的归一化步长，覆盖范围扩展到本项目的一个折叠时延周期与 ±41 kHz Doppler 支持。原文的物理 Doppler 步长为 15 kHz；本项目为 30 kHz，因此应表述为按归一化坐标适配。

场景生成仍使用连续 off-grid 时延与 Doppler。字典只用于接收机估计。SOMP 在单位范数列上求解，再转换为物理系数；GAMP-SBL MMV、GNN-ASPL 直接使用物理字典。EM 的原生坐标转换由其独立实现保持。

GNN 权重与当前字典严格绑定，沿用原整数网格训练结果。网格与推断方程的迁移回归见[核验记录](../../../result/code_consolidation_20261011/VERIFICATION.json)。历史网格比较及推导见[整理前文档](../../../archive/paper_layout_20261026/original_paper/docs/history/archive/code_consolidation_20261011/workspace/docs/BASELINE_GRID.md)。
