# 第二章语言润色（2026-10-30）

## 授权与范围

作者要求：“先修第二章，做语言润色，尽可能参照已有的参考论文”。本轮只润色当前 C-STMP 稿第二章，保留三个小节、全部数学定义、系统假设和推断目标。摘要、引言和其余章节不重新生成。未启动实验或训练。

本轮依据实际读取的本地论文原文调整表达，不把句式适配标为逐字引用，也不要求保留参考论文中的不自然语法。此前严格原句审查的统计不适用于本轮润色稿。

## 来源与修改对应

| 位置 | 核对的原文位置 | 本轮处理 |
|---|---|---|
| 系统总述 | Ding，`reference/literature/ding2026.pdf`，PDF p.2，§II；Shen，`reference/literature/shen2025.pdf`，PDF p.3，§II开头 | 保留设备、卫星天线及共享资源的叙述次序；用 in which 引入系统，删去无必要的 Additionally，缩短资源共享句。 |
| II-A 信道和路径参数 | Shen，PDF p.3，§II-A、式(1)及其后说明；Huang，`reference/literature/huang2026.pdf`，PDF p.2／期刊p.2950，§II 的 Doppler shift 段 | 整合双弥散信道动机，将祈使句改为连续陈述；保留公共 Doppler 假设。路径数、复增益及 Dirac delta 随信道式集中解释，时延符号直接对应物理量。 |
| II-A 阵列定义 | Shen，PDF p.3，§II-A 的阵列索引与 directional cosines；本稿原 UPA 公式和一般阵距定义 | 将天线索引移到阵列式前，将方向余弦、阵距和波长合为式后一组定义。本文一般阵距、相位约定和时间原点仍属原有模型，不归为 Shen 的原公式。 |
| II-B 导频与调制 | Cai，`reference/literature/cai2026.pdf`，PDF p.4／期刊p.3578，§II-A、式(3)–(4)附近；Ding，PDF p.2，§II、式(1)–(2)；Huang，PDF p.2／期刊p.2950，§II首段 | 保留帧、子载波、导频向量及矩阵的定义顺序；直接写原有行正交条件，省去 partial orthogonal 的重复介绍；删去 IDAFT 后重复的导频符号定义。导频归一化和维度均为本稿既有定义。 |
| II-B CPP | Bemani，§III-A、式(18)–(19)，沿用本稿已核实的术语与引用；本稿 CPP 式与附录B | 仅改公式引入和时长衔接；长 CPP、完整时延相位和多周期延拓仍由本稿定义及附录支撑。未重新核验 Bemani 全文，也未新增归属于该文的结论。 |
| II-B 分数时延和路径响应 | Huang，PDF p.2／期刊p.2950，§II、式(4)–(5)及其后说明 | 沿用 effective channel、fractional delay、Doppler shift 和 power leakage；简化冗长的公式引入，明确由帧0的路径矩阵转入一般起始样本 g。G、B、D、波形及张量维度仍为本稿原定义。 |
| II-B 跨帧关系与 II-C 观测堆叠 | Shen，PDF pp.4–5，§II-B/C、式(8)–(15)；本稿原跨帧关系 | 用相位关系承接多帧观测；将孤立的 Let 和 Define 改为明确指向有效导频或矩阵元素的句子。未引入 Shen 的 OTFS、数据检测或终端补偿设定。 |
| II-C 活动和贝叶斯目标 | Cai，PDF pp.4–5／期刊pp.3578–3579，§II-A/B、式(1)、(4)–(5)及后续解释 | 沿用 activity indicator、block-sparsity structure、Bayesian inference、MMSE 和 message calculation 的概念；明确给定估计量、训练先验、后验因子和估计目标之间的承接；结尾直接引向后续接收机。 |

## 引用边界修正

Huang PDF p.2 写的是有效 AFDM 帧时长 `T=N Δt`。本稿 `T_frame=(N+N_CPP) T_s` 包含 CPP，由本稿样本数定义直接得到。因此移除该时长公式末尾单独的 Huang 引用，保留其在 AFDM 子载波、分数时延和有效信道处的引用。公式未变。

## 主要语言处理

- 将路径和阵列符号分别集中解释，减少连续短句和孤立定义引导词。
- 以 denotes / is 直接描述符号与物理量的对应，修正原文适配中不自然的名词组合。
- 删除重复的导频定义及公式引入中的冗余措辞。
- 保留物理信道、调制与跨帧关系、接收观测与贝叶斯问题的原有顺序。
- 没有增加方法名称、算法缩写、实验主张或新的系统假设。

## 核验记录

修改前源码见 `02_system_model.before.tex`，22份稿件资产的原始哈希见 `baseline.json`。逐项公式和引用核验、最终文件哈希、编译与页面检查结果记录于 `verification.json`；源码差异见 `chapter2.diff`。缩写工具的原始报告和人工复核说明另存于本目录，覆盖范围以工具实际结果为准。

缩写工具报告为 partial，未报出问题；其未自动确认的 GFRA、IoT、MMSE 在引言、CPP 在第二章均已人工核对全称。原始报告见 `acronyms_report.md`。本次为同一会话内的文字与含义复核，未声称独立审稿。

最终核验：14个编号公式和2处未编号显示公式逐项一致（忽略空白），没有新增行内数学表达式；19份受保护的其他稿件及图表资产哈希一致。Tectonic 0.17.0 编译成功，阅读稿仍为14页，无未定义引用、缺失文献或 overfull box。第二章第2–4页逐页视觉检查及全篇缩略图检查完成，未见裁切、重叠或公式异常。日志保留其他章节的 underfull 提示，以及原矩阵索引公式的 amsmath bracket-group 提示；该公式显示正常。临时页面图片的清理被工具自动策略拦截（仅返回 blocked by policy，未提供具体原因），故暂留于项目 tmp/pdfs/ch2_language_polish_20261030；页面哈希保留于 verification.json。
