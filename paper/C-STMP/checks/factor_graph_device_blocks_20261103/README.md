# 因子图改为设备块变量表示

> 本轮历史图和绘图脚本已移入归档；当前生图入口见 [统一说明](../../../../src/evaluation/plots/manuscript/README.md)。以下记录描述当时版本。

2026-11-03。按作者确认的方案，删除中间的完整矩阵展开，围绕观测似然、设备块、信道与活动先验重画 Fig. 2。

## 图形与数学关系

原图中的矩阵括号、逐元素索引和单独的列变量节点已移除。当前变量节点为 `X_1,X_2,...,X_K`；每个观测似然 `p(y_j|x_j)` 连接全部设备块，因为列 `x_j` 从各设备块取出对应条目。每个设备约束因子 `p(X_k|H_k,alpha_k)` 则连接自己的设备块、信道变量和活动变量，两个先验各自接在对应变量后。

这使用本文第二章式(13)的索引关系和式(14)的同一后验分解，不改变模型或更新公式。左侧不再用矩阵重排来表示关联；右侧信道、活动先验的上下分组仍参照 Cai Fig. 2 / PDF p.5，图注保留这部分的改绘出处。新图全部用节点、线段及文字绘制，没有复制原图的矩阵或矢量路径。

图宽仍为 252 pt（88.9 mm），使用单栏；两组先验分支分别平行。配色和字号沿用此前版本。图注删除逐元素索引说明，改为说明观测因子与所有设备块之间的关系。

## 输出与检查

- 当前独立图：[PDF](../../figures/factor_graph.pdf)、[SVG](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/figures/factor_graph.svg)、[600 dpi PNG](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/figures/factor_graph.png)。
- [完整稿](../../main.pdf)已重编译，当前为 16 页；Fig. 2 仍在第 4 页。[当前三图各格式打包](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/factor_graph_device_blocks_20261103/figures_current.zip)。
- [VALIDATION.json](VALIDATION.json)核对 9 条观测到设备块连边及 15 条设备约束、先验连边，确认所有连接均属于对应后验因子。
- PDF 内嵌字体且无嵌入位图，SVG 文字转曲，文字位于画布内。独立图及正文第 4 页已用 Poppler 渲染检查。
- 系统图、接收机图和七幅实验图字节未变；TeX 仅改 Fig. 2 图注，正文论述、公式和算法保持；无未定义引用或溢出框。

旧图、旧阅读稿和原第三章源码在 `before/`。绘图源为 [draw_factor.py](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/factor_graph_device_blocks_20261103/draw_factor.py)，检查源为 [check_graph.py](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/factor_graph_device_blocks_20261103/check_graph.py)，图注差异为 [CAPTION_CHANGE.diff](CAPTION_CHANGE.diff)。
