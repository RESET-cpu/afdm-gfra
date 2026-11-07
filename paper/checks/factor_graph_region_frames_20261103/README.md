# 因子图彩色分区框（2026-11-03）

> 本轮历史图和绘图脚本已移入归档；当前生图入口见 [统一说明](../../../src/evaluation/plots/manuscript/README.md)。以下记录描述当时版本。

参照项目内 Shen 论文第 6 页 Fig. 2 的彩色虚线框分区方式，将线性估计区标为蓝色、联合去噪区标为铜色，框下标题采用同色加粗文字。采用白色背景，不增加色块。参考截图见[Shen 第 6 页](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/ch5_sentence_revision_figures_20261102/sources/shen-06.png)。

为避开分区边界，将三个条件因子标签向右平移 11.5 pt。节点、24 条边、两组平行先验支路以及画布尺寸保持。正文文字、公式和图注均未修改。

输出为 [PDF](../../figures/factor_graph.pdf)、[SVG](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/figures/factor_graph.svg) 和 [600 dpi PNG](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/figures/factor_graph.png)，原生尺寸 252 × 167 pt。完整稿已重新编译，Fig. 2 位于第 4 页，全文 16 页。

核验见 [VALIDATION.json](VALIDATION.json)：PDF 无嵌入位图且字体内嵌；SVG 文字转曲；边的端点及路径与上一版完全相同；两种颜色的框均为无填充虚线矩形；正文源码与另外两张方法图保持。通过 Poppler 检查[单图](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/factor_graph_region_frames_20261103/preview/factor_poppler.png)和[正文第 4 页](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/factor_graph_region_frames_20261103/preview/paper-page-4.png)，未见文字压线或裁切。编译无未定义引用与越界警告，仍有此前的 Underfull 与 PDF 版本提示。

修改前文件保存在 `before/`，当前三张方法图九种文件汇总于 [figures_current.zip](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/factor_graph_region_frames_20261103/figures_current.zip)。
