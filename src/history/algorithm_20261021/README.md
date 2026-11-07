# 整理前的算法原件

本目录保存 2026-10-21 整理前完整的 `src/afdm_jadcedd/algorithm`，包括停用候选算法。
`configs/` 保存迁移前的配置，`experiment_run.py` 和 `train_full_score.py` 保存停用入口。
这些文件只供研究溯源；当前代码不会导入这里的实现，也没有旧名称转发入口。

需要复现历史运行时，在独立目录按原布局恢复。
当前实现见 `src/afdm_jadcedd/algorithm/{proposed,STMP,baseline}`，
迁移前完整运行代码、配置与验证记录在 `result/algorithm_layout_20261021/`。
