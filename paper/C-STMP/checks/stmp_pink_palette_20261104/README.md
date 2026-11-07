# STMP 粉红配色与后续红色变体约定

2026-11-04，按作者要求修改当前七幅实验图：STMP 从红色改为粉红色 `#d65a9e`，原圆圈、虚线保持；GP-MP-C 保留红色 `#ff0000`、方块、实线。后续 GP-MP 白高斯噪声训练版和 GP-MP-C-EP 估计相位版同用红色，通过不同线型和标记区分。本轮没有添加尚未完成的消融或新相位曲线。

## 修改与核验

- 唯一绘图配置 `src/configs/plots/manuscript.json` 仅改变九处颜色字段：七幅图及两个双面板的嵌套配置；见 [COLOR_CHANGES.json](COLOR_CHANGES.json)。绘图程序没有修改。
- 使用统一入口重新生成七幅矢量 PDF；[PLOT_VALIDATION.json](PLOT_VALIDATION.json)核验原始输入哈希、547 个点、图例边界和遮挡。与上一轮保存的全部曲线值逐项相同，无位图嵌入。
- 两版论文编译成功，13/15 页，全文提取文本与改前逐页相同；150 dpi 比较只有第 10–12 页变化。TeX、书目和三幅方法图保持原哈希；[VALIDATION.json](VALIDATION.json)保存核验结果。一般 Underfull 和已有 PDF 版本提示保留，没有未定义引用、缺字或 Overfull 报告。
- 已查看七图预览及正文变动页：粉红色在白底可辨，STMP 与 GP-MP-C 同时由颜色、圆圈/方块、虚线/实线区分；图例、字号、坐标范围、画布和图注保持，没有新增裁切或遮挡。此次为既有实验折线图的局部配色修改，不扩大为整篇图形重设计。
- 没有运行训练、推断或新场景生成。原始结果、算法、权重、训练安排不变。

改前文件位于 `before/`，哈希见 [before_hashes.json](before_hashes.json)；两版编译日志位于 `build_main/`、`build_full/`；七图预览和正文页位于 `render/`。当前正式输出为 `paper/C-STMP/figures/` 下七幅实验 PDF 和 `paper/C-STMP/main.pdf`、`paper/C-STMP/main_full.pdf`。
