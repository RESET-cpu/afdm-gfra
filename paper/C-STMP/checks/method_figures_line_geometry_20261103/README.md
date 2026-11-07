# 方法图线宽、直线与平行关系修正

> 本轮历史图和绘图脚本已移入归档；当前生图入口见 [统一说明](../../../../src/evaluation/plots/manuscript/README.md)。以下记录描述当时版本。

2026-11-03。按作者反馈修正三处图形几何问题，两图继续按单栏排版。

- 多帧示意：CPP 与 AFDM 只绘制填充色，共用一个外框及一条分隔线；三个帧外框、三条分隔线与下方总括线均使用同一灰色、0.5 pt 线宽，避免共用边重复描画。
- 卫星到 UPA：改为一条直虚线，从卫星本体下端顶点直接连接 UPA 右上阵元。移动 UPA 标签以避开该直线，保留两端的实际图形锚点。
- 因子图：因子行与左右对应变量重新对齐。所有信道节点相对其设备因子上移 36 pt，所有活动节点下移 36 pt；斜线水平跨度均为 32 pt，因此两组斜率分别为 -1.125 与 1.125。矩阵块同步收紧并重新调整文字间距，保留原字号、全部变量与因子关系。

当前两张独立图为 252 × 166 pt、252 × 167 pt。PDF、SVG、600 dpi PNG 位于 [figures](../../figures/README.md)。[当前三图打包](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/method_figures_line_geometry_20261103/figures_current.zip)包括未改动的接收机图。旧系统图、因子图与阅读稿在 `before/`。

[检查结果](VALIDATION.json)直接核对输出 PDF 的描边宽度、颜色、直线端点与因子连边，并确认两组斜线平行。终端圆周仍完整位于圆盘内，上行链路未经过非活跃终端。文字在画布内，PDF 为矢量、字体嵌入，SVG 文字转曲。接收机图、七幅实验图及全部 TeX 源码字节保持。

已重新编译完整稿并用 Poppler 查看两张独立图及正文第 3、4 页；无未定义引用或溢出框。本轮编译当前完整稿为 16 页，图号及插图页码保持；总页数以编译时的工作区正文为准。

绘图源：[draw_figures.py](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/method_figures_line_geometry_20261103/draw_figures.py)；检查源：[check_figures.py](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/method_figures_line_geometry_20261103/check_figures.py)。本轮只调整图形几何，不引入术语、模型或算法变化；图形出处沿用既有图注。
