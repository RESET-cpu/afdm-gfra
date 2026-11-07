# 方法图的单栏与紧凑布局

> 本轮历史图和绘图脚本已移入归档；当前生图入口见 [统一说明](../../../src/evaluation/plots/manuscript/README.md)。以下记录描述当时版本。

2026-11-03。按作者要求，系统图和因子图改为单栏，接收机图保留双栏并收紧布局。

| 图 | 原生尺寸 | 正文位置 | 主要调整 |
|---|---|---|---|
| 系统图 | 252 × 166 pt（88.9 × 58.6 mm） | Fig. 1，第 3 页，单栏 | 帧结构、卫星、覆盖区和 UPA 贴近排布；按栏宽重新设置文字大小。 |
| 因子图 | 252 × 167 pt（88.9 × 58.9 mm） | Fig. 2，第 4 页，单栏 | 矩阵仅展开首末列，中间用省略号表示；保留三组设备因子与通用推断名称。 |
| 接收机图 | 468 × 140 pt（165.1 × 49.4 mm） | Fig. 3，第 8 页，双栏 | 压缩均值、方差、活动概率支路以及联合矩汇合、外信息反馈的间距；原生图高由 185 pt 降为 140 pt。 |

当前输出位于 [figures](../../figures/README.md)，各含矢量 PDF、文字转曲 SVG 和 600 dpi PNG。[打包下载](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/method_figures_column_layout_20261103/figures_column_layout.zip)含九个图文件。统一配色和图形改绘出处保留：Shen Fig. 1 / PDF p.3 的卫星、覆盖区、UPA；Cai Fig. 3 / PDF p.10 的均值网络。因子图按 Cai Fig. 2 / PDF p.5 的组织方式重新绘制。图注的来源标记保持。

## 正文与验证

本轮在第二、三章把对应 `figure*` 改为 `figure` 并使用 `\linewidth`；第五章接收机图仍用 `figure*`，宽度改为 `0.92\textwidth`。图注及技术内容没有因本轮布局调整而改写。

已重新编译完整稿，并用 Poppler 渲染全部 17 页；三张图所在页单独以 140 dpi 查看。引用无未定义项，无溢出框。两张单栏图以及双栏模块图无文字裁切、明显重叠或出栏。三张独立 PDF 均为矢量，无嵌入位图，字体已嵌入；SVG 文字转曲，PNG 为 600 dpi。第二、三、五章共 37 个编号公式环境及 Algorithm 1 与本轮开始时一致。

工作区在本轮期间另有第五章的相位更新说明、第六章、附录与 SNR 实验图更新，均保留当前内容。完整稿由当时的 15 页变为 17 页，不能将总页数变化归因于本轮缩图。实验图哈希记录显示六幅未变、`snr_comparison.pdf` 已变化；本轮脚本不生成实验图。初次编译的引用警告在当前源码完整后重编译已消失，未为此修改实验章节。

验证结果：[VALIDATION.json](VALIDATION.json)。正文快照差异：[CHANGES.diff](CHANGES.diff)，其中第五章的相位说明变化来自同时更新的工作区内容。渲染预览位于 `preview/`；旧图、旧阅读稿及原有插图源码在 `before/`。

## 重现

项目 Python 运行 [draw_figures.py](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/method_figures_column_layout_20261103/draw_figures.py) 输出三张图；在稿件目录用 Tectonic 编译 `main.tex`，再用 Poppler 渲染全文和插图页。最后运行 [validate_layout.py](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/method_figures_column_layout_20261103/validate_layout.py) 检查公式、算法、引用、字体、文字边界及输出格式。
