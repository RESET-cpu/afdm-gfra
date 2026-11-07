# 第六、七章九项修订完成

> 本轮历史图和绘图脚本已移入归档；当前生图入口见 [统一说明](../../../../src/evaluation/plots/manuscript/README.md)。以下记录描述当时版本。

2026-11-04，作者确认“就按你说修改吧”。按[复审表](../../docs/CHAPTERS_VI_VII_REVIEW_20261104.md)落实 VI01–VI07、VII01–VII02，共六处建议小修和三项可选调整。

## 修改范围

- VI01：训练/验证数量与每场景取样拆句；VI02：分类器训练改为 using the loss in；VI03：明确两个默认阻尼值的对应关系。
- VI04：删除重复 achieves；VI05：明确跨信道图比较的是性能；VI06：导频设置使用 we select。
- VI07：保留 Karras 标量来源，并补充 de Albuquerque–Pearson 的矩阵系数出处，仅指向 Appendix B.1。
- VII01：结论明确跨信道收益相对四个稀疏恢复基线；VII02：先验学习与有色噪声训练动机拆句，保留原假设边界和结论强度。

仅修改第六、七章获批文字和新增一条书目。公式、参数、Algorithm 1、图表文件和所有其他章节源码保持；未修改图 7 统计或实验。此次补引和比较对象澄清已在上一轮提出并由本轮用户确认，不构成额外待批准内容。

## 新增文献核验

[官方条目](https://proceedings.neurips.cc/paper_files/paper/2024/hash/af85ade5e70a6e1eb07a9541fb529baf-Abstract-Conference.html)及[原始官方 BibTeX](inflationary_flows_official.bib)：

D. de Albuquerque and J. Pearson, “Inflationary Flows: Calibrated Bayesian Inference with Diffusion-Based Models,” Advances in Neural Information Processing Systems, vol. 37, pp. 96847–96891, 2024, doi: 10.52202/079017-3070.

本地原文：[PDF](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/formula_prototypes_20261104/inflationary_flows_2024.pdf)，Appendix B.1，PDF pp.23–24，式 (67)–(68)、(73)、(77)–(78)。本轮重读提取文字并查看第 24 页；与此前核查一致，取名义信号协方差 Σ₀=σ_d²I 可对应本文现式 (42) 的三个矩阵系数。未声称本文损失函数、网络、训练协方差采样或接收机均来自该文。详细映射见[既有推导记录](../../docs/DAMPING_AND_FORMULA_PROTOTYPES_20261104.md)。

## 核验

- 两版编译成功，主稿 13 页、完整稿 14 页；参考文献由 42 增至 43。
- 两章行内数学表达的集合、全部陈列公式及编号保持；既有 42 条书目逐条保持。
- 保护清单中 26 项资产不变，全部图文件不变。
- 无未定义引用、重复标签或 Overfull；保留已有类别的 Underfull 和插入 PDF 版本提示。
- 已查看变动页缩略图，并放大核对主稿第 9 页新增引用/设置以及第 11 页的结果说明/结论，未发现遮挡或缺字。
- 未运行训练、推断或修改任何实验配置与结果。

[源码差异](SOURCE_DIFF.txt) · [核验结果](VALIDATION.json) · [核验入口](verify_revision.py) · [备份](before/) · [版面预览](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/chapters_vi_vii_language_selected_20261104/previews/changed_pages.png)

[主稿](../../main.pdf) · [完整稿](../../main_full.pdf)

