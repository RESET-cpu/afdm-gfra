# 三张方法图：保留论文图风格，调整构图与表达

日期：2026-11-03。作者要求在上一版原图改绘基础上，与参考原图形成更明显的差异。本轮采用重新组织构图和突出本稿技术关系的方式，保留白底、细线、数学字体、变量圆节点与因子方节点。

## 改动

| 图 | 上一版 | 当前版 |
|---|---|---|
| 系统图 | 基本沿用 Shen 的卫星位于地面右上方的布局，右侧为 Cai 的二维资源格子 | 卫星移至左上方，UPA 独立放在右上方，重排地面设备及上行链路；右侧改为连续 AFDM 帧，明确 CPP、跨帧相位、共同活动状态和有效观测矩阵。 |
| 因子图 | Cai 的所有 H 分支在上、所有 alpha 分支在下，连线交叉 | 每个设备单独展开一对 H_k / alpha_k 分支，两类先验紧邻对应设备，去掉跨设备交叉线。左侧保留原图矩阵及列似然组织，补充矩阵维度。 |
| 接收机图 | 左边小因子图，通过虚线向右放大 | 改为上下两部分：上部为 MFLE 与 GPJD 的消息交换，下部直接展开 GPJD；均值与导数方差进入 Gaussian site，标量输出的分类器独立画在下方，再汇入联合矩与外信息。 |

系统图和接收机图为双栏宽度；因子图重新安排为更宽的设备分组结构，建议通栏环境中以约 0.78 倍正文宽度居中。三图均提供 PDF、SVG、600 dpi PNG。旧版九个图文件及说明存于 `before/`。

## 保留的原图元素与来源

- Shen Fig.1 / PDF p.3：保留卫星、地面轮廓及 UPA 的矢量形状，重新安排其位置；地面设备节点和链路重新布置。当前系统图已不用 Cai Fig.1 的资源格子。
- Cai v2 Fig.2 / PDF p.5：通过上一版改绘文件保留左侧矩阵、列似然、灰色列底纹及设备块底纹；右侧设备成对分支重新绘制。矩阵相邻的旧模块文字及连接残端已清理。
- Cai v2 Fig.3 / PDF p.10：保留均值网络的抽象矢量图标，下方分类器改为更紧凑的单输出图标；整体双层构图和更新路径重新安排。图标表示网络功能，不表示真实层数或神经元数。

当前图注继续明确写出 Adapted from 和相应图号。参考文献 PDF 保持原文件。原图位置及上一版提取记录见 `../method_figures_source_adaptation_20261103/`。

## 数学关系

1. 系统图：第二章的时延关系、UPA、effective-pilot 与 mmv；相位系数按 q=0,1,...,Q-1 示意，Q 帧共享 alpha_k 和参考 H_k。CPP/AFDM 长度仅为图示比例。
2. 因子图：working-posterior 的四类因子不变。每个 X_k 同时连接 H_k 与 alpha_k，q_tr(H_k) 是完整信道先验；列 x_j 与设备块 X_k 对应同一 X 的条目。此处只使用第三章通用名称。
3. 接收机图：沿用 IV–V 的 colored-query、derivative-trace、pooled-variance、site-update、conditional-moments、activity-probability。F_k 显式进入分类器；分类器还接收 R_k、v。方差是同一均值函数的有限差分估计并跨设备平均。site 与外信息使用当前 R_k、v。图显示训练范围内采用学习器的主要关系，完整调度仍由 Algorithm 1 给出。
4. tau 通道与 F_k 特征通道相交处采用断线，表示跨线而非连接点。没有增加随机变量、训练网络、假设或实验结果。

## 检查与重绘

三张 PDF 已用 Poppler 渲染检查。检查包括矩阵括号、变量和下标、节点连接、字体、裁切边界及输入依赖；PDF/SVG 均无嵌入位图，PNG 为 600 dpi。详细尺寸及散列见 `EXPORTS.json`，验证结果见 `VALIDATION.json`。

源码为 `recompose_figures.py`、`vector_base.py`；矩阵源片段依赖 `before/factor_graph.pdf`。三者一并包含在下载包中。在项目根目录运行：

```powershell
& .\.venv\Scripts\python.exe paper/C-STMP/checks/method_figures_distinct_layout_20261103/recompose_figures.py
```

当前正文、`main.pdf`、七张实验图和参考文献 PDF 没有修改。插入片段在 `figure_inserts.tex`，尚未编入正文。
