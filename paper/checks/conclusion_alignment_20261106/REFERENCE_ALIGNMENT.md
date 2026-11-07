# 结论对照与句段来源（2026-11-06）

## 已读取的母本

- Cai 等，IEEE JSAC 2026 期刊版，`reference/literature/cai2026.pdf`，§VII Conclusion and Discussion，印刷 pp.3588–3589／PDF pp.14–15。完整结论含两段：首段介绍 STMP-JADCE、消息传递与生成模型的结合、两类 score 网络及定性性能／收敛结果；次段讨论其他逆问题的应用。本文借鉴首段简短总结方法与结果的组织，不移植其所有基线占优、收敛或通用应用结论。
- Shen 等，`reference/literature/shen2025.pdf` 本地版本，§VI Conclusion，PDF p.15。完整结论依次回收无 GNSS 场景、多帧 OTFS 方案、MP 接收算法、CNN 检测改进及定性实验收益。本文借鉴该单段推进顺序，不带入其符号检测、CNN、三维稀疏假设或 OTFS 模型。

两篇结论的实验收束均未列出具体性能数字。本文依作者明确偏好保留定性结果；已有完整技术推导继续位于正文。

## 当前结论逐句映射

| 句子 | 段内任务及真实来源 |
|---|---|
| In this paper, we investigated ... | 回收研究场景。句式与 Shen §VI 首句相近；GNSS-independent GFRA、LEO satellite IoT 均为本文已确认摘要／引言的对象。 |
| We proposed a multi-frame AFDM ... | 回收传输方案。段内位置参考 Shen §VI 第二句；AFDM 及无设备侧预补偿来自本文摘要、第一个贡献和第二章，不归为 Shen 的 AFDM 结论。 |
| Under a shared effective-channel representation ... | 本文多帧共同未知信道模型及已确认引言第一项的概括；不是母本原句，不在结论重复相位推导或表示维度比较条件。 |
| We learned a score-based generative prior ... | 合并先验学习与去噪器收益，技术内容来自本文已确认摘要及引言第二项；均值与方差关系沿用现有 Manor–Michaeli／Dytso 来源，Cai 仅提供方法构成的总结粒度，不支持本文单去噪器方案。 |
| We incorporated this denoiser ... | 回收本文 MP 接收机和既有 MFLE、GPJD 模块；缩写已在摘要／引言及正文定义。参考 Cai §VII 首段将消息传递与生成模型放在同一句方法总结中的组织。 |
| The learned density-ratio estimator in GPJD ... | 本文已确认引言第三项和摘要的作用说明。沿用 Menon–Ong 分类概率与密度比来源，免于显式边缘似然计算是本稿应用；非 Cai／Shen 原文技术结论。 |
| Simulation results demonstrated ... | 结尾定性结果句的组织参考 Shen §VI 末句及 Cai §VII 首段末句；实际比较和导频收益仅来自本稿 §VI。以 comparable channel-estimation performance 保留比较含义，不列目标数值、帧数或百分比。 |
| The receiver also achieved ... | 保留旧结论已有的跨 NTN-TDL profile 结果与无需重训练条件，依据本稿 §VI-E。删去基线数量，只作定性总结，不将该结果扩大为优于所有学习方法。 |

本次为结构借鉴与本文技术内容的忠实改写，不声称整段照搬或逐句严格对应某一篇原文。无新方法名、公式、引文或实验。摘要、引言和其他章节保持。
