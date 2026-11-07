# AFDM 卫星 JADCE 论文

论文标题：**Generative-Model-Aided Grant-Free Random Access for GNSS-Independent MIMO-AFDM Satellite IoT Systems**

当前论文入口是 [main.tex](main.tex)。正文按章保存在 `sections/`，参考文献统一维护于 [references.bib](references.bib)。

2026-10-18：已修订第 II–V 章，与估计相位、估计噪声的当前 Proposed 主线对齐。
阅读版见 [main.pdf](main.pdf)；本轮修改、公式核验与排版记录见
[修订记录](checks/revision_II_V_20261018_112525/REVISION_REPORT.md)。
修订前源文件保存在 [历史副本](history/before_revision_II_V_20261018_112525)。

2026-10-18：完成第 II–V 章行文修订，当前阅读版为 10 页；公式与引文保持不变。
详见 [行文修订记录](checks/prose_revision_20261018_115730/REVISION_REPORT.md)。

2026-10-18：二阶学习目标与共享方差的详细推导移至附录 A；正文保留训练和迭代使用说明。当前阅读版为 10 页，正文 65 个编号公式，附录为 (A.1)–(A.3)。详见 [正文与附录调整记录](checks/learning_appendix_20261018_121248/REVISION_REPORT.md)。

```text
paper/
├── main.tex
├── references.bib
├── sections/
│   ├── 01_introduction.tex
│   ├── 02_system_model.tex
│   ├── 03_bayesian_receiver_design.tex
│   ├── 04_generative_priors.tex
│   ├── 05_overall_algorithm.tex
│   ├── 06_simulation_results.tex
│   ├── 07_conclusion.tex
│   └── appendix_second_order_training.tex
├── figures/          # 论文插图
├── literature/       # 已有原文 PDF 与章节核对材料
├── writing_profile/  # 14 篇语料、写作规则、小节蓝图及来源记录
├── history/          # 迁移前的稿件和检查记录
└── checks/           # 当前项目的结构与编译检查
```

2026-10-18：第 II–V 章按 Cai、Shen 的通用句式完成一轮修订。参见 [句式依据](writing_profile/pre_simulation_20261009/corpus_sentence_patterns.md)及[修订记录](checks/corpus_style_20261018_123401/REVISION_REPORT.md)。

2026-10-18：完成第 II–V 章逐段通读，压缩重复解释并修顺 32 处行文；当前 PDF 为 10 页。详见 [通读修订记录](checks/close_reading_20261018_124725/REVISION_REPORT.md)。

2026-10-18：完成当前正文及附录的术语核对，修正 TMP 全称并补充 Gaussian site 的定义与来源；当前阅读版为 11 页，末页延续参考文献。详见 [术语核对记录](checks/terminology_20261018_125231/TERM_AUDIT.md)。

2026-10-18：接收机按线性估计、信道与活动去噪、外信息更新组织表述。详见 [本轮说明](checks/receiver_description_20261018_125604/REVISION_REPORT.md)。

## 章节状态

| 章节 | 标题 | 状态 |
|---|---|---|
| I | Introduction | 已完成英文初稿及中文对照，已纳入主 PDF |
| II | System Model | 已修订；明确未知相位、未知噪声与估计参数下的工作后验 |
| III | Bayesian Receiver Design | 已修订；增加相位和噪声估计，统一条件接收机符号 |
| IV | Learning Channel and Activity Denoisers with Score-Based Generative Priors | 已修订；正文说明训练与读出，详细推导见附录 A |
| V | Overall Algorithm | 已修订；完整输入、执行顺序与前端／迭代成本 |
| VI | Simulation Results | 文件已建立，正文待写 |
| VII | Conclusion | 文件已建立，正文待写 |

第二章的三个小节为 **Terrestrial-Satellite Link Model**、**Transmission Scheme** 和 **Problem Formulation**。组织依据见[第二章蓝图](writing_profile/pre_simulation_20261009/system_model_writing_blueprint.md)。

`main.tex` 目前编译已有的 II–V 正文及附录 A。待 I、VI、VII 完成后，启用各自的 `\input`；启用引言时，同时删除 `\setcounter{section}{1}`。摘要、关键词和作者信息留在主文件中补充。宏包、符号宏及全局排版设置集中在主文件，各章节不再包含文档导言区。

## 文献与资料

`references.bib` 共 22 条，当前 II–V 正文引用其中 16 篇。本轮增加变量投影、MDL 与 L-BFGS-B 的方法来源。正文使用 `\cite{key}`，文末由 BibTeX 按实际引用自动生成。已有引用键保持不变；`bemani2022` 是原稿的键，其期刊出版年份仍为 2023。

已在本地保存的 Cai、Ding、Shen、Huang 原文集中在 `literature/`；其余语料的原文链接、版本和阅读位置见[语料清单](writing_profile/pre_simulation_20261009/corpus_manifest.md)。原项目中供算法和基线复核使用的参考资料保留原路径。

技术依据继续以项目[系统模型](../docs/SYSTEM_MODEL.md)、[理论推导](../docs/THEORY.md)和[术语记录](../docs/TERMINOLOGY.md)为准。

## 编译

采用 IEEEtran 单栏写作稿，便于审阅公式；排双栏时去掉 `\documentclass` 中的 `onecolumn`。这一步只设置写作版式，投稿前另核对期刊格式与页数。

在 `paper/` 目录下，使用已有 LaTeX 环境运行：

```sh
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

也可把 `main.tex`、`sections/`、`references.bib` 和 `figures/` 一起上传 Overleaf，主文件选 `main.tex`。资料目录不参与编译。

2026-10-09：结构检查已确认 59 个编号公式、原有标签及引用全部保留，III–V 正文保持不变。当前原生编译器所需资源包尚未缓存且下载失败，PDF 编译尚未验证；详见 [checks/](checks)。

2026-10-18：本轮已由 Tectonic 完成 LaTeX／BibTeX 编译，阅读版共 11 页。
修订后共 68 个编号公式；交叉引用和引文键检查通过，未出现公式溢出。
字体替代及 inputenc 的引擎提示保留于编译日志，页面已渲染检查。
上述 2026-10-09 编译失败记录属于历史状态。

2026-10-18：参考作者中文旧稿完成英文引言，纳入 Ding2026 的 AFDM 稀疏模式学习工作及 Shen、Huang、Cai 等相关研究；新增 Release 17 同步规范引用。中文对照见 [引言](sections/01_introduction_zh.md)，证据定位见 [来源记录](checks/introduction_20261018_134220/SOURCE_MAP.md)。
