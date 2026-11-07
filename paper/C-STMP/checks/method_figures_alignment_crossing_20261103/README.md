# 系统图对齐与因子图交叉排列

> 本轮历史图和绘图脚本已移入归档；当前生图入口见 [统一说明](../../../../src/evaluation/plots/manuscript/README.md)。以下记录描述当时版本。

2026-11-03。回应作者对终端位置、卫星到 UPA 连线和因子图交叉排列的反馈。

系统图将靠近圆盘边界的终端移入覆盖区，并移开与上行链路重叠的非活跃终端。卫星到 UPA 的虚线从卫星本体的原矢量顶点出发，连接 UPA 右上阵元；上行链路从活跃终端边缘接出。画布仍为 252 × 166 pt，单栏排版。

因子图右侧改回上半部 `H_1,H_2,...,H_K`、下半部 `alpha_1,alpha_2,...,alpha_K`。上一版按设备交替排列两类变量，消除了交叉，但没有改变变量与因子的连接关系。当前每个 `p(X_k|H_k,alpha_k)` 仍仅连接自己的 `X_k,H_k,alpha_k`，交叉处没有节点；三个可见交叉不引入跨设备依赖。图注末句相应改为每个设备因子连接其信道和活动变量。画布仍为 252 × 167 pt。

## 原图核对

- [Cai v2 原文](../../../../reference/literature/cai2026_stmp_v2.pdf)，Fig. 2，PDF p.5：信道变量集中在上半部，活动变量集中在下半部，设备因子分别向两组变量连边；本次恢复此排列。图形预览见此前提取的 [Cai 因子图](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/method_figures_source_adaptation_20261103/sources/cai_factor.png)。
- [Shen 原文](../../../../reference/literature/shen2025.pdf)，Fig. 2，PDF p.6 及式(20)：原图也有交叉边，但对应其变量分裂后的依赖关系；本图的连边仍由本文式(14)决定，没有移入 Shen 的其他变量或边。

## 交付与检查

两图的 PDF、SVG、600 dpi PNG 已更新至 [figures](../../figures/README.md)，并重新编译 [完整稿](../../main.pdf)。系统图和因子图仍为第 3、4 页的单栏图；完整稿 17 页。接收机图及七幅实验图字节未变；正文只更新上述图注一句，公式与算法未改。

[检查结果](VALIDATION.json)记录了终端圆周与圆盘边界的间距、虚线两端与原图几何坐标的吻合、每个设备的因子连边、三处无节点交叉、矢量与字体检查。Poppler 渲染后的两张独立图及正文第 3、4 页已查看，无文字裁切、图形越界或连线错位；编译无未定义引用及溢出框。

[最新三图打包](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/method_figures_alignment_crossing_20261103/figures_current.zip)含当前三张方法图的 PDF、SVG、PNG。旧系统图、因子图及阅读稿保存在 `before/`；绘图源为 [draw_figures.py](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/method_figures_alignment_crossing_20261103/draw_figures.py)，检查源为 [check_figures.py](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/method_figures_alignment_crossing_20261103/check_figures.py)。
