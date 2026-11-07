# IEEE 模板、摘要与篇幅核验（2026-10-22）

本轮直接修改 D 盘 TWC 稿件。当前阅读稿为 9 页 PDF（历史 PDF 已清理），修改前的 14 个源文件保存在 [备份目录](../../history/before_ieee_format_20261022/)。

## 模板依据与修改

- [TWC 官方投稿要求](https://www.comsoc.org/publications/journals/ieee-twc/policies-guidelines)的 “Submission Instructions and Requirements” 规定首投稿最多 13 页，双栏、单倍行距、10pt，标题、作者信息、摘要、图表、附录和参考文献均计入；“Paper Organization and Format” 规定摘要为 75–200 词。
- [IEEE 官方期刊模板](https://www.overleaf.com/latex/templates/ieee-journal-paper-template/jbbbdkztwxrd)使用 `IEEEtran` 的 `journal` 模式，并要求保留类文件的字体与版心设置。该模板由 [IEEE 官方模板入口](https://www.overleaf.com/org/ieee)列出。模板选择器当日返回 HTTP 418，因此本轮采用这一可访问的官方模板来源，并叠加 TWC 的具体投稿要求。
- 使用 `\documentclass[10pt,journal,letterpaper]{IEEEtran}`；未压缩页边距、栏宽、正文行距或正文字号。当前编译器中的 IEEEtran 1.8b 类文件与 [CTAN 发布的类文件](https://mirrors.ctan.org/macros/latex/contrib/IEEEtran/IEEEtran.cls)逐字节相同，文件及校验值保存在 [模板来源记录](template_reference/provenance.json)。
- 删除覆盖默认字体的 `lmodern`，恢复 IEEEtran 的 `ptm` Times 系列正文。将 T1 编码选择放在类文件之前，使 XeTeX/Tectonic 在初始化时也正确选用该字体；这不改变模板的字体族或版心。数学字体沿用官方一般期刊模板的默认设置。
- 多行公式的分页惩罚恢复为官方模板说明中的 `2500`；未改写公式或调整公式字号。
- 删除正文中可见的工作稿日期行，按作者提供的信息加入 Bo Wang 及单位、邮箱脚注；未填入未提供的基金、职称或 IEEE 会员信息。
- 英文摘要压缩至 **183 词**，若将连字符连接的各部分拆开计数则为 **194 词**。中文摘要同步。摘要依次保留多帧 AFDM 模型、基于得分的生成式先验、从后验分解得到的深度展开消息传递接收机，并保留活动概率影响后续消息、因而需要联合训练的因果关系。

## 内容保留与检查结果

I–V 各章、附录、图表源文件及参考文献数据库均与本轮备份逐字节一致。三项贡献、56 个编号公式、2 个无编号显示式、2 幅图和 2 张表保留。22 个引用键及文内交叉引用均可解析。具体差异见 [修改对照](revision.diff)，源文件校验值见 [核验记录](source_validation.json)。

本地 Tectonic 与桌面 LaTeX 编译器均成功编译。PDF 为 US Letter，612 × 792 PDF points；正文实际嵌入字体为 `NimbusRomNo9L-Regu`，即 IEEEtran 所用的 Times 系列实现，正文 10 TeX pt 对应约 9.96264 PDF points。全部 28 个字体资源均已嵌入，未出现 Latin Modern 正文字体、字体缺失警告、缺字、越栏或未解析引用。

保留的诊断为 3 处行内空白较宽的 `Underfull hbox` 提示和 3 处公式起始方括号提示；逐页检查 9 页渲染结果，确认公式、图表、标题和作者脚注均正常，无遮挡、裁切或重叠。英文摘要缩写检查无问题；该自动检查仅覆盖本次修改的英文摘要。见 [编译结果](compile_result.json)、[字体与版面数据](pdf_inspection.json)及 [摘要检查](acronym_check.json)。

## 实际分页与后续篇幅

第五章最后一句位于 **第 8 页右栏顶部**，附录随后开始。当前 PDF 共 9 页，最后一页右栏仍有空白。下表按 PDF 的双栏阅读位置估算有效篇幅，保留一至两位小数，避免把跨到下一页误认为完整占用一页。

| 内容 | 当前篇幅 |
|---|---:|
| 标题、作者栏、摘要、关键词和 I–V（至附录开始） | 约 7.53 页 |
| 现有附录 A | 约 0.71 页 |
| 现有参考文献 | 约 0.61 页 |
| 合计有效版面 | 约 8.85 页，实际输出 9 页 |
| 距首稿 13 页上限 | 约 4.15 页 |

建议为**实验与讨论安排约 3.5 页、结论约 0.3 页**，余下约 **0.35 页**用于后续图表浮动、作者或基金信息、摘要中的实验结果以及新增参考文献。当前单作者信息已计入以上预算。VI、VII 尚未编入本稿，最终分页需在加入实际图表与文字后确认。

此前非标准字体稿虽然输出 10 页，其有效版面约为 9.15 页；本轮净增加的可用空间约 **0.30 页**，不能把输出从 10 页变为 9 页理解为节省了整整 1 页。此前 README 中基于旧字体的篇幅估计由本记录替代。具体页码、栏位、坐标和计算方法见 [篇幅核算](layout_budget.json)。
