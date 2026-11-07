# C-STMP：当前算法稿

[论文源码](main.tex) · [阅读稿](main.pdf) · [中文摘要](sections/00_abstract_zh.md) · [中文引言](sections/01_introduction_zh.md) · [研究文档](docs/README.md)

本目录包含本稿的全部现有正文、图片、参考文献与研究依据，可直接从本目录编译 `main.tex`，无需其他稿件目录。

| 内容 | 位置 |
|---|---|
| 编译入口与唯一阅读稿 | `main.tex`、`main.pdf` |
| 各章、中英文材料与附录 | `sections/` |
| 五幅论文图片的实际文件 | `figures/` |
| 本稿参考文献 | [references.bib](references.bib) |
| C-STMP 推导、训练、诊断和术语 | [docs/](docs/README.md) |
| 修订依据、来源核验与历史源文件 | `checks/` |

当前稿使用有色噪声训练的均值网络、条件均值导数方差、重新训练的活动分类器及标量查询方差更新；在线查询采用 C=vI。方法说明见 [C-STMP 推导](docs/C_STMP_DERIVATION_20261024.md)，术语依据见 [TERMINOLOGY.md](docs/TERMINOLOGY.md)。此处只登记既有稿件范围，未改变方法或实验结论。

第 VI 章依次包含去噪、收敛、SNR、导频数和用户数五图。当前用户数图为每档 500 场景，来源为 `result/user_count/figures/paper500_stmp_c_stmp_v3_20261027/user_count.pdf`。后续实验顺序和样式见 [绘图说明](../../src/configs/plots/README.md)。结论占位文件及旧二阶训练附录尚未编入当前阅读稿。

在本目录使用包含 IEEEtran 的 LaTeX 环境编译，例如 `latexmk -pdf main.tex`。完整论文的阅读稿只使用 `main.pdf`；后续编译直接更新它，不新增日期或版本 PDF，也不新增历史完整论文 PDF 备份。

[算法修订核验](checks/VALIDATION.json) · [复制及图源清单](checks/COPY_MANIFEST.json) · [当前摘要来源](checks/abstract_original_words_20261026/SENTENCE_SOURCES.md) · [用户数图核验](checks/user_count_final_sentence_20261026/VALIDATION.json)

此次只整理目录，正文、五幅图片和阅读 PDF 均保留原字节。整理前的完整说明及旧共用研究文档保存在[历史归档](../../archive/paper_layout_20261026/README.md)，共享文献原文仍在 [reference/](../../reference/README.md)。


## 2026-10-26 摘要接收部分原句修订

按作者要求，当前摘要接收部分使用 Cai2026 摘要第1页的两句完整原文，未改变句内词序、用词或标点；中文同步。两句分别说明生成先验引入消息传递及作为 MMSE 去噪器，完整摘录与逐句验证见 [原句核验](checks/abstract_original_words_20261026/CAI_VERBATIM_RECEIVER.json)，适用边界见 [来源说明](checks/abstract_original_words_20261026/SENTENCE_SOURCES.md)。全文185词，四篇来源词形核验通过；正文、算法和实验结果未由本次修订改动。现有阅读稿已直接更新并检查排版。


## 2026-10-26 摘要承接关系修订

根据作者后续反馈，将接收部分首句中的先验介绍缩为 the learned channel prior，明确回指第二点已学习的同一先验，并以 Finally 标出第三步。第一句现为 Cai 原句的最小衔接改写，第二句仍为完整原文；此前两句均照录的记录已被本条替代。全文175词，来源词形与28项表达核验通过，中文同步，原阅读稿已更新并检查。具体差异与来源边界见 [衔接核验](checks/abstract_original_words_20261026/CAI_RECEIVER_TRANSITION.json)。


## 2026-10-26 接收部分以已有先验承接

将 Finally 改为 With the learned channel prior available，采用 Cai2026 第 V-A 节（PDF p.9）的 With ... available 句式，明确接收机以第二点的所学先验为前提。第一句仍标为来源明确的句式适配，下一句保留 Cai 摘要完整原文；没有引入其两个得分网络。当前摘要177词，来源词形与27项表达核验通过；中文、原阅读稿及排版检查已同步。见 [句式出处](checks/abstract_original_words_20261026/CAI_PRIOR_AVAILABLE.json)。


## 2026-10-26 摘要删除目标性表述

按作者反馈，删除 so as to push towards the performance limit of JADCE 及对应中文；保留所学先验进入消息传递和作为 MMSE 去噪器的作用，不增加实现细节或新词。当前摘要167词，四篇来源词形核验通过；原阅读稿已直接更新并完成排版检查。见 [删减依据](checks/abstract_original_words_20261026/CAI_RECEIVER_CONCISE.json) 与 [源文件差异](checks/abstract_original_words_20261026/REMOVE_PERFORMANCE_ASPIRATION.diff)。


## 2026-10-26 摘要整体衔接修订（当前）

根据作者对连贯性的反馈，重核整段逻辑：多帧传输增加观测，随后学习有效信道先验及同一次有色噪声训练，再采用 TMP 整块信道建模，使 This design 明确指向支持 MMSE 去噪的接收结构；结句点明原始 score-based TMP 接收机。接收描述保留 Cai 摘要的技术从句，第一句为有来源的适配，第二句为完整原文。当前181词，四篇来源完整词形和31项技术表达核验通过，中英文同步；原阅读稿已直接更新并完成排版检查。见 [整体核验](checks/abstract_original_words_20261026/COHESION_CHECK.json)、[逐句来源](checks/abstract_original_words_20261026/SENTENCE_SOURCES.md) 和 [源文件差异](checks/abstract_original_words_20261026/COHESION_REVISION.diff)。


## 2026-10-26 摘要接收段改写

按作者最新要求，在含义不变的前提下重组接收段，与 Cai 原句区分：先说明所学先验经 MMSE 去噪器进入 TMP 接收机，再说明整块信道的超节点表示及不作逐元素先验分解。两句均为改写，之前的整句照录记录仅属历史版本。当前英文摘要177词，中英文已同步；四篇论文的逐词与32项短语核验通过。既有唯一阅读稿已原位更新，共12页，首页及全页缩略图检查通过。正文、模型和结果未由本次修改改动。见[改写及含义核验](checks/abstract_original_words_20261026/RECEIVER_PARAPHRASE_CHECK.json)和[逐句来源](checks/abstract_original_words_20261026/SENTENCE_SOURCES.md)。


## 2026-10-26 摘要连接表达修改，暂缓编译

当前源稿将 To this end 改为 Within this framework，中文同步为“在该框架中”，直接承接前句的 TMP 接收框架。作者明确要求确认措辞后再编译；本次未运行编译，现有阅读稿保留上一编译版本。后续文字调整也应遵循此要求。源稿及用词核验见[本次记录](checks/abstract_original_words_20261026/RECEIVER_FRAMEWORK_TRANSITION.json)。


## 2026-10-26 摘要改为整块信道联合去噪表述，继续暂缓编译

按作者要求，摘要删除 super node，直接描述对整个信道矩阵联合去噪以利用信道相关性，并保留不作逐元素先验分解的限定。中英文源稿与出处记录已同步，四篇来源逐词及短语核验通过；方法和正文引用不变。继续遵守确认措辞后再编译的要求，本次未运行编译，阅读 PDF 未更新。见[修订记录](checks/abstract_original_words_20261026/RECEIVER_JOINT_DENOISING.json)。


## 2026-10-26 摘要按三项重点重排，暂不编译

按作者确认，第一点突出处理大差分时延和多普勒，第二点采用 Huang 的有效信道先验表述并说明有色噪声训练，第三点突出 TMP 框架的线性估计/去噪迭代及 MMSE 先验使用。当前中英文已同步，英文148词、六句；四篇来源的逐词与29项短语检查通过。正文、方法、图表和实验结果不变。本次未编译，阅读 PDF 保留上一编译版本，确认措辞后再更新。见[三点重心核验](checks/abstract_original_words_20261026/THREE_CONTRIBUTION_FOCUS.json)。


## 2026-10-26 摘要主次与标题对齐，暂不编译

摘要以无GNSS辅助的 AFDM 接入及生成式先验/有色训练为主，TMP 仅一句交代所学先验用于 JADCE，删去其迭代和 MMSE 实现说明。当前英文134词、六句，中英文源稿与来源记录已同步，逐词与28项短语核验通过。标题、正文、图表和实验结果不变。按照作者要求，本次未编译，阅读稿仍是上一编译版本。见[标题对应与主次记录](checks/abstract_original_words_20261026/TITLE_ALIGNED_FOCUS.json)。


## 2026-10-26 摘要采用 MP 类别，强化学习先验的接收作用

按作者要求，摘要移除 TMP/STMP 名称，接收段保留两句、37词：所学先验用于 MMSE 去噪，所学去噪器与线性估计结合完成 JADCE。结句采用“基准接收机”，具体比较对象仍为正文定义的原始 STMP。前两点继续占主要篇幅；当前英文148词，中英文源稿、逐句来源与词形核验已同步。正文方法及 Cai 引用保持原样。仍按作者要求暂不编译，阅读 PDF 未更新。见[本轮记录](checks/abstract_original_words_20261026/LEARNED_PRIOR_MP_FOCUS.json)。

2026-10-26 摘要接收句进一步改为去噪器提供后验均值与方差估计，用于迭代 JADCE；中英文同步，仍暂不编译。当前核验见 [RECEIVER_POSTERIOR_ROLE.json](checks/abstract_original_words_20261026/RECEIVER_POSTERIOR_ROLE.json)。


## 2026-10-27 作者确认摘要并编译

采用作者提供的完整英文，仅将minimum mean-square error改为minimum mean-squared error；中文同步。delay–Doppler的连接号在TeX中以等价的--编码，显示保持原文。唯一阅读稿main.pdf已原位更新，共12页，摘要文字、首页及全篇缩略图检查通过；正文与参考文献10份文件哈希未变。此前“暂不编译”记录已由本次明确授权取代。见 [最终核验](checks/abstract_final_20261027/VALIDATION.json)。


## 2026-10-27 用户数 STMP 全500场景比较

用户数图现包含 STMP、C-STMP 和四基线，20/40/60/80/100用户每档500场景。STMP 的1477份达到迭代上限结果全部计入；C-STMP 的既有 K100 整档与 K80 场景372回顾性参数调整仍明确披露。仅调整图例位置的论文版绑定原已核验统计，冻结数据和报告保留。核验记录见 [本批检查](checks/user_count_stmp500_20261027/VALIDATION.json)。
