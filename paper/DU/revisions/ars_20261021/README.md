# ARS 摘要与引言候选稿

**已停用（2026-10-21）：** 作者要求回到 ARS 改写前的版本继续修改。当前稿件入口为 [TWC 原稿](../../main.tex)，贡献按“大差分时延多普勒下的 AFDM 传输方案与输入输出关系—生成式信道先验—深度展开 MP 接收机”组织。以下保留本候选生成时的说明与检查记录。

本稿使用 Academic Research Skills 的论文写作、摘要写作和质量检查指南，重写 TWC 版本的摘要与引言，并同步中文稿。它是供作者对照的写作候选，未替换 `paper/TWC` 当前稿。

- [英文全文与双栏预览入口](main.tex)：摘要和第一节为新版，其余章节保留原稿。
- [中文摘要](sections/00_abstract_zh.md)
- [中文引言](sections/01_introduction_zh.md)
- [英文摘要与引言阅读稿](checks/writing_draft.md)

## 写作调整

摘要按接入问题、跨帧模型、联合接收机制和训练作用展开。三项贡献分别说明：分离帧间相位后共享信道所增加的观测；学习先验如何与活动概率一起形成多用户反馈；两类监督如何沿层间消息共同优化后续估计。已完成的模型与设计直接陈述。

引言保留“无 GNSS 接入—终端实现需求—AFDM—信道先验—联合训练”的研究动机。Shen 的多帧 OTFS 工作单独放入相关工作段；OTFS 概念仍引 Hadani。Huang 与 Cai 分别说明有效信道学习先验和多用户 MP 的已有基础。术语和来源定位记录在项目 `docs/TERMINOLOGY.md`。

当前摘要尚无新接收机的数值结果句；待独立评价完成后补入最有代表性的比较结果。第六、七节仍延续原稿的待完成状态。

## 检查记录

- 引文键、交叉引用和标签检查通过，见 [source_check.json](checks/source_check.json)。
- 原 TWC 稿件文件与开始写作时的快照一致；候选稿的模型、方法、训练和附录文件与原稿逐字节一致。
- ARS 缩写检查已运行，原始报告见 [英文及中英文摘要](checks/acronyms_en_and_abstracts.md) 和 [中文引言](checks/acronyms_zh_intro.md)。工具对连字符复合词及大小写有识别限制；人工核对说明见 [acronym_manual_review.md](checks/acronym_manual_review.md)。
- 使用桌面 LaTeX 编译器检查；最终结果见 [compile_result.json](checks/compile_result.json)。

使用的技能：`academic-research-suite` 3.23.1，来源 [academic-research-skills-codex](https://github.com/Imbad0202/academic-research-skills-codex)。本次采用限定范围的写作与检查模块，未把自动检查记作独立同行评审或投稿认证。
