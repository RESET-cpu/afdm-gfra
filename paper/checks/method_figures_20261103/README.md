# 三张方法图：原图依据、输出与核对

日期：2026-11-03。用户要求基于 Cai、Shen、Ding、Huang 的配图组织方式，组合适用元素、统一配色，并导出矢量图和 PNG。本轮只绘图及维护图文件说明，不修改正文或实验结果。

## 输出

正式文件在 `../../figures/`：`system_multiframe`、`factor_graph`、`learned_receiver`，每张均有 `.pdf`、`.svg`、`.png`。三张图采用同一套蓝、青绿、橙配色，宽度 177.8 mm；PNG 宽 4200 像素、600 dpi。具体尺寸及散列见 `EXPORTS.json`，格式检查见 `FORMAT_VALIDATION.json`。

图形为从正文定义重新绘制的矢量形状和文字。没有裁剪或嵌入原论文图，也没有生成、伪装信道样本或实验数据。矩阵格子用于说明变量组织方式，不表示信道取值。

## 原图组织方式及本文适配

页码为 PDF 页码。上一轮已查看的原页图像保存在 `../ch5_sentence_revision_figures_20261102/sources/`。

| 本图 | 参考原图及作用 | 本文绘制内容 |
|---|---|---|
| 系统与多帧传输 | Cai v2 Fig.1 / p.4 的活动设备与传输资源；Shen Fig.1 / p.3 的卫星、设备、UPA 及公共/差分时延 | 左侧画卫星上行接入，右侧画 Q 帧的共同活动状态和参考信道、各帧相位及有效观测矩阵。AFDM、CPP、跨帧关系均来自本文第二章，不沿用 OFDM 或 OTFS 的信号链。 |
| 因子图与消息交换 | Cai Fig.2 / p.5 的列向量/设备信道块重组和后验因子；Shen Fig.2–3 / pp.6–7 的因子分组及消息交换 | 按本文 working-posterior 画列似然、X 的两种组织方式、设备关系因子、完整信道先验与 Bernoulli 活动先验，下方给通用的两部分消息交换。第三章图中不使用 MFLE/GPJD 专用名称。 |
| 学习接收机 | Cai Fig.3 / p.10 的学习矩进入接收机；Ding Fig.1 / p.3 的整体关系与局部展开；Shen Fig.4 / p.11 的推断统计量进入学习器；Huang Fig.1–2 / p.3 的网络输入输出与迭代用途 | 上部画先有色去噪训练、再冻结去噪器训练分类器；下部展开 GPJD 的均值、同一均值函数的导数方差和密度比活动估计，并合成为联合矩和外信息。没有画成 Ding 的可训练展开层，也没有 Huang 的 Langevin 采样支路。 |

源文件：`reference/literature/cai2026_stmp_v2.pdf`、`shen2025.pdf`、`ding2026.pdf`、`huang2026.pdf`。建议图注中的文献引用已写入 `figure_inserts.tex`，可在插入正文时统一调整。

## 与当前正文的对应

- 系统图：`02_system_model.tex` 的 physical-channel、upa、effective-pilot、mmv，以及跨帧相位关系。导频矢量沿用 p_qk，帧时长沿用 T_frame。公共时延补偿发生在卫星接收端；Q 帧共享 alpha_k 和参考 H_k。CPP 长度仅作示意。
- 因子图：working-posterior 的四种因子逐项保留。列索引 j=1,…,MN；每列长 KN；设备信道块 X_k 由同一 X 的 N 行重组。虚线表示同一变量条目的重组，不是新增概率依赖或随机变量副本。完整 q_tr(H_k) 不作元素独立分解。
- 接收机图：第四章 colored-query、first-loss、derivative-trace、classifier-loss、activity-probability，以及第五章 pooled-variance、site-update、conditional-moments。分类训练噪声及在线输入均为 vI_D，去噪训练采用有色协方差；F_k 同时进入 site 和分类器。有限差分使用同一个 F_theta，方差支路没有另一张网络。
- 外信息节点同时接收联合矩与当前 R_k、v；反馈到下一轮线性估计。图展示训练范围内的学习分支和主要消息关系，site 保留/接受、归一化恢复和方差尺度调度仍由 Algorithm 1 定义。图中信道量采用归一化坐标。

## 检查

PDF 与 SVG 均不含嵌入位图；PDF 为单页且含可提取文字，SVG 保留文字元素。PNG 尺寸和 DPI 已核验，所有文字都在画布内。

已用 Poppler 从实际 PDF 渲染逐图检查字体、上下标、连线和边界；先后修正设备标注、列节点文字与边的重叠、列节点与高亮列的对齐，以及去噪特征进入分类器的路径。变量节点为圆、因子节点为方形；算法图交叉线使用跨线弧表示不相连。

正式三张 PDF 的图形宽度是论文双栏宽度，文字主字号约 8–10 pt。图的尺寸和字体是整体设计的一部分，后续不宜把完整算法图压成单栏。

## 重绘

在项目根目录运行：

```powershell
& .\.venv\Scripts\python.exe paper/C-STMP/checks/method_figures_20261103/draw_method_figures.py
```

只更新这三张方法图及本目录的预览/导出登记，不访问训练数据或启动实验。
