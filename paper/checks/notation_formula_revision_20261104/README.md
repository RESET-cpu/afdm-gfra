# 2026-11-04 变量与公式修订

作者已授权实施此前建议，并要求继续检查无文献同类式的情况。

当前结果见 [57 个公式逐项出处及修订说明](../../docs/FORMULA_PROVENANCE_20261104.md)。本目录保存修改前副本、完整差异、来源页文字、32 项小尺寸代数验证、两版编译检查和页面预览。正文及完整稿保持 13/15 页、42 篇参考文献；七幅实验图、引言、结论、书目及实验表格核对保持。

- `CHANGES.diff`：最终源码改动，包括首轮转换后的人工复查修正。
- `EQUATION_INVENTORY.json`：57 个公式、位置、新旧编号和来源边界。
- `MATH_VALIDATION.json`：32 项恒等式检查，最大残差约 3.63e-13。
- `VALIDATION.json`：保护文件、编译、表格及目视检查。
- `draw_figures.py`：当前 Fig.2/3 导出入口；只更新这两张方法图。
- `validate_math.py`：不运行接收机或训练的确定性代数检查。
- `revise.py`：一次性的首轮记号转换记录，最终稿还包含后续逐处修正；不作为当前稿重放入口。

编译：Tectonic 0.17.0，分别对 main.tex 和 main_full.tex 使用 --only-cached --keep-logs --keep-intermediates。两版无缺失引用/字符或 Overfull；各有 3 处 Underfull hbox，main 另有 1 处 Underfull vbox，目视无裁切、重叠。图 PDF 1.7 与输出版本提示沿用既有状态。

本轮不改物理模型、接收机实现、配置、权重或实验结果。数学检查不代表训练网络的性能证明，也不代表 M4 相位研究已经结束。
