# 第三至第五章五类组合表述修订

日期：2026-10-30。依据作者“第二类全部改掉”的要求，将此前术语核对中列出的五类表述改为直接描述输入、计算步骤或网络结构。

## 修改范围

- 第 III 章：将 training-prior correction 改为说明从分类器输出中减去训练类别先验的 log odds，以估计对数密度比。
- 第 IV 章：将 covariance-weighted denoising loss 及相关组合表述改为直接说明由 Σ^{-1} 加权的信道平方误差，以及等价的由 Σ 加权的 score 平方误差。
- 第 IV 章：将 query、active/inactive query 和 query densities 改为 denoiser input、按活动标签构造的 R，以及给定活动标签的输入密度。
- 第 IV 章：将 conditional RefineNet 改为 RefineNet backbone，并另句说明条件输入为 v 和协方差因子。
- 第 V 章：将 activity evidence 改为由对应高斯密度计算的 log density ratio，再由其计算活动概率。
- 在 `docs/TERMINOLOGY.md` 追加本轮术语依据及原论文定位，保留既有历史记录与作者已登记的算法名称。

## 验证

- 与 `before/` 中的修改前快照比较：三个章节的编号公式内容、LaTeX 标签和引用命令均未改变；检查结果见 `SOURCE_CHECKS.json`，正文差异见 `REVISION.diff`。
- 对源码的可见正文和编译 PDF 中的第 III–V 章分别检索，五类目标词组均已移除。内部含 query/evidence 的交叉引用标签保留，不属于可见正文术语。
- Tectonic 编译成功，阅读稿共 15 页。未发现未定义引用、重复定义、Overfull、缺字或 LaTeX 错误；既有 Underfull 提示保留。PDF 摘要及检查结果见 `PDF_CHECKS.json`。
- 人工查看重新渲染的第 5–8 页（`page-05.png` 至 `page-08.png`），修订段落、公式、算法浮动体和双栏布局无重叠或截断。
- 缩写检查结果仍为 partial，详见 `acronym_report.md`；其中包括既有缩写定义位置、缺少定义和自动展开识别问题。本轮没有引入新缩写，也未扩展修改这些无关问题。

本轮仅修改术语表达，没有改变算法、模型、训练设置或实验数据，因此未运行训练或批量实验。
