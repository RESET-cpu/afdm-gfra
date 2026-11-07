# 第二章论述与衔接修订

日期：2026-11-02。作者在逐段审查后授权完善第二章，要求避免工程化、防御化和前后脱节的表达。本轮以已完成的 [14 段审查](../ch2_paragraph_review_20261102/REVIEW.md)为依据，在当前 LaTeX 源稿中作局部修订。

## 实际修改

| 位置 | 改动 | 作用 |
|---|---|---|
| II-A 物理信道 | 时间原点移到信道式前；块内物理参数恒定假设移出阵列段，接在物理信道说明后 | 集中说明同一个模型的条件，不打断时延解释 |
| II-B 开头 | 先说明活跃设备在 Q 个连续 AFDM 帧发送导频，各帧分别调制、解调，接收信号用于 JADCE；替换原来单独分配 Q 帧的句子 | 建立传输过程，再进入导频符号、向量和矩阵 |
| 导频约束 | 删除 `For simplicity`，保留约束和设计章节指引 | 不借用 Cai 的简化 LMMSE 理由来解释本文不同的矩阵 |
| 调制段 | 采样间隔定义移到标量、矩阵表示之后 | 先完成等价表示，再引出 CPP 的时间长度 |
| 实数时间波形 | 改为 `To account for fractional delays, we define ...`；移除把整条定义直接归给 Bemani 的引用 | 明确该定义服务分数时延。标准 IDAFT/CPP 的文献依据仍在前文；本式的相容关系保留 |
| 跨帧关系 | 将 A 的原有定义移到相位旋转和参考信道近似不变之后 | 给出性质后，立即说明相位如何进入导频表达。没有新增相位已知假设 |
| 活动段 | 将少数设备活跃的结论移到低活动概率条件之后 | 让 `As a result` 对应真正的原因 |
| 多帧矩阵 | 增加一句“各帧共享 X，因此增加导频帧增加观测而不增加待估计信道系数” | 将引言中的方案作用落实到本节矩阵尺寸；不在其他位置重复这一结论 |
| 欠定性 | `Since Q<KN` 改为 `For Q<KN` | 把严格不等式明确作为所考虑的条件 |
| 贝叶斯问题 | 将泄漏句移到完整信道估计之前，以 `therefore` 连接原因与做法 | 避免打断跨帧推导，使估计对象选择有直接依据 |
| 信道先验 | 明确使用训练信道的分布作为 q_tr(H_k)，保留不逐元素分解 | 说明训练分布在推断中的角色，不展开训练实现 |
| 估计目标 | `The MMSE estimate` 改为 `The MMSE estimate of X_k` | 对齐原有条件均值公式 |

本轮没有增加新的缩写、方法名、性能保证或模型适用范围讨论。保留 CPP 覆盖、块内恒定、独立性和固定前端输入等实际用于公式的条件。摘要、引言及后续章节没有重新生成或修改。

## 改动句子的出处与归属

以下页码均对应 [本轮审查的版本清单](../ch2_paragraph_review_20261102/SOURCES.json)。旧映射中的“所有句子均为必要替换”不作为本轮前提。

| 修改后的文字或关系 | 原段与位置 | 支持范围 |
|---|---|---|
| `In the proposed scheme, each active device transmits pilot symbols over Q consecutive AFDM frames within one transmission block.` | Shen §II-B，PDF p.4：方案概述先交代设备符号跨 Q 个连续帧；Cai §II-A，PDF pp.3–4：导频符号与传输块；本文已确认引言第一项贡献 | 采用 Shen 原段的操作顺序，删除其数据扩频条件并换为本文导频传输。是方案内容的适配，不宣称 Shen 提出本文 AFDM 方案 |
| `AFDM modulation and demodulation are performed independently for each frame, and the received signals are collected for JADCE.` | Shen 同一原句含每帧独立 modulation/demodulation，随后 collected for further joint processing；本文引言已有 JADCE | 原段关系及核心搭配直接对应。OTFS 改为 AFDM，联合处理目标具体化为本文 JADCE；未增加其他发射/接收步骤 |
| 时间原点、参数恒定、采样间隔及 A 的定义位置 | 原句逐字移动；技术及出处边界见上一轮 P02/P03/P06/P11 报告 | 仅调整顺序，A 引出句的 `the phase rotation` 改为近指 `this phase rotation`。本文约定仍登记为本文约定 |
| `To account for fractional delays, we define the transmit waveform ... as` | Huang §II，PDF p.2，式(5)前说明纳入 fractional delay/Doppler effects 的作用；Shen §II-B，PDF p.4 有 transmit waveform；Bemani §III-A，PDF p.8 给离散基函数 | 目的、术语及公式引出写法有依据；含取整项的完整实数时间公式为本文现有定义，未核得完整母句。删除该处直接引文，前段的 IDAFT/CPP 引用保留 |
| `Since the Q frames share the same X, additional pilot frames provide more observations without increasing the number of channel coefficients to be estimated.` | Shen §II-B，PDF pp.4–5：参考信道近似不变后接增加观测的用途；本文已确认引言第一项贡献；本节 X∈C^(KN×MN) | 沿用原段性质→观测用途的关系；关于 X 尺寸与 Q 的关系是本文公式的直接推论，不登记为 Shen 的原句结论 |
| `As a result` 结论后移；`For Q<KN` | Cai §II-A，PDF p.4 活动句组；Wei–Yuan v1 §II-B，PDF p.2 欠定性句 | 保留原技术任务，纠正本文句序及条件表达；Cai 原文的简写亦不豁免独立逻辑检查 |
| 泄漏→`We therefore estimate the full H_k without imposing channel sparsity.` | Huang §II，PDF p.2，式(5)后泄漏/稀疏性；§III-A，PDF p.3 完整有效信道的学习与估计；本文原句 | 用原有技术陈述和已有连接词把原因与处理方式放在一起；不改变信道先验或设备活动的块稀疏定义 |
| `We use the distribution of the training channels as the channel prior q_tr(H_k), without factorizing this prior element-wise.` | Cai §II-B，PDF pp.4–5 后验中的 p(H_k)；§I-A，PDF p.2 整信道与非可分去噪；§IV-A/B，PDF p.9 训练信道样本与分布；本文 §III/IV 的 q_tr | channel prior、training samples/distribution 及整体信道处理有依据；q_tr 的具体训练/推断用途属于本文设定。完整句为本文说明，不冒称 Cai 原句或增加先验独立假设 |
| `The MMSE estimate of X_k ...` | Cai §II-B，PDF p.4 的 MMSE estimator；本文原目标式 | 给已有术语补上正确估计对象，公式不变 |

`NEW_WORDS.json` 记录相对改前第二章新增的英文词形与允许语料中的实际匹配。它仅检查词形先例，不替代本表的语义、搭配和原段任务核对。没有通过修改模型来迁就参考论文，也没有把本文推导称为参考论文的直接原式。

## 文件与验证

- [逐行差异](CHANGES.diff)，[改前第二章](before/sections/02_system_model.tex)。
- [验证记录](VALIDATION.json)：15 个编号公式及标签保持；2 个无编号陈列式保持。A 的编号公式由活动段移到跨帧段，相对无编号活动定义的位置改变，所有公式内容不变。
- 唯一完整阅读稿仍为 `paper/C-STMP/main.pdf`；本轮重新编译并检查第二章所在第 2–4 页。
- [缩写检查](ACRONYMS.md)为部分自动覆盖，相关复合词和已确认模块名称已人工核对；未将部分覆盖写成全通过。
- 不运行训练或实验，不修改其他稿件或研究主线。既有审查目录继续作为修订前版本记录保存。
