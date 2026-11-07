# 波形与导频

`afdm/` 保存 DAFT、chirp、CPP、整数及分数时延多普勒的路径算子；`pilot.py` 保存导频生成。

主要入口是 `afdm/continuous.py` 的 `continuous_path_matrix`、`afdm/path_operator_multicycle_full.py` 的 `daft_matrix` 和 `pilot.py` 的 `PartialDFTPilot`。保留原浮点运算顺序与单位，不在波形模块选择接收算法、管理实验或画图。参数来自 `channel/config.py` 及显式函数参数。

已有公式依据仍见各稿件的 `docs/TERMINOLOGY.md`；此次只调整源码归属和导入路径，没有新建波形或术语。
