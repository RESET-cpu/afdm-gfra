## 2026-10-30：第三至第五章结构、论证和语言修订

按作者确认的结构，第三章采用 Receiver Structure、Multi-Frame Linear Estimation、Generative-Prior-Aided Joint Denoising；第四章保留四个学习相关小节；第五章采用 Overall Algorithm 和 Computational Complexity Analysis。工程条件纳入整体算法，不独立设置阻尼、停止条件或工程技巧小节。

**MFLE（Multi-Frame Linear Estimation）和 GPJD（Generative-Prior-Aided Joint Denoising）是作者在本次讨论中明确批准的本文模块描述性名称及缩写，不是声称已有论文使用的算法名称。** 首次定义在 III-A。MFLE 的多帧对象来自本稿第二章模型；其线性 MMSE 与 Gaussian extrinsic messages 沿用 Cai §III-A、式(6)–(11)（本地 PDF pp.5–6／期刊pp.3579–3580）和 Ma §II-A/B、式(11a)–(11b)（作者稿pp.1–3）。GPJD 的条件信道估计与活动概率组合有 Cai §III-B、式(16)–(42)（PDF pp.6–8）及 Liu §III-B–D、式(17)–(29)（PDF pp.5–6）依据；generative prior 的学习依据沿用 Song、Arvinte。未把本稿模块组合名称归给上述文献。

- **Gaussian approximation、extrinsic message、site approximation**：Minka §§2–3、式(5)–(6)、(8)（作者稿pp.2–3）以及 Vehtari §2.1（JMLR PDF p.5，式(1)后 site/cavity/tilted 定义及更新商）、§2.2（p.6，自然参数）。本稿保留标量协方差近似、正精度条件与既有 site 保持规则；不宣称学习统计量是精确后验矩。
- **条件矩中的活动不确定性**：Cai §III-B 与 Liu §III-C–D 的活动加权均值、协方差；本稿先给局部模型的精确条件矩恒等式，再描述网络和高斯近似。期望残差方差更新据 Vila §III-A、式(22)–(27)（PDF p.4／期刊p.4661），应用对象是本稿局部去噪模型，不宣称全局 EM 单调性。
- **Tweedie's formula、denoising score matching**：Dytso 式(3)（PDF p.2）、Efron §2、式(2.7)–(2.8)（PDF p.4）、Vincent §4.2、式(4.3)–(4.5)（PDF pp.6–7／期刊pp.1666–1667）。新增加权 score residual 是本稿原损失的直接代数解释，未把协方差加权形式当作 Vincent 原文的各向同性公式。
- **input/skip/output preconditioning**：Karras §5、式(7)–(8)（PDF p.8）和表1（p.3）。正文明确本稿将标量预条件推广到矩阵协方差。Shastri §III-B、式(38)–(41)（PDF pp.15–16）支撑向去噪器提供相关噪声统计的思路，未将其独立噪声样本输入等同于本稿协方差输入。
- **conditional covariance、Jacobian、Monte Carlo divergence**：Dytso §II-A、式(9)（PDF p.4）的 Jacobian 约定与 §IV Proposition 1、式(22)（p.5）已核对；本稿采用 output-by-input 约定，因此为 P=JΣ。Metzler §V-B、式(21)为随机方向散度估计的依据；符号方向、协方差缩放、中心差分及块内复用是本稿既有实现，正文明确为适配，不宣称该组合逐字来自 Metzler 或闭环无偏。
- **density ratio estimation、binary classification、log odds**：Menon §II.2、§III式(6)–(8)、§IV.2式(16)–(17)（PDF pp.2–3／会议pp.305–306）。正文补明训练标签 a 和两类共享的方差采样法，区分总体最优 logit 与训练分类器的近似，再连接活动先验修正。
- **conditional RefineNet**：Song–Ermon Appendix A.3（arXiv v3 PDF p.14）及 Appendix A.1。128 基通道和本稿协方差条件输入由现有实现支撑；分类器的对数能量及保留符号的内积变换直接描述现有计算，不登记为独创方法名称。
- **整体算法的组织**：Shen §III-C末、Algorithm 1（PDF pp.9–10）用于参考其简短的初始化、阻尼、停止和复杂度说明；Cai §V-A/B、Algorithms 1–2（PDF pp.8–10）作为顺序组织的对照。没有移植 Shen 的消息算法、停止指标或 Cai 的依赖当前输入的归一化。前端 variable projection 与 minimum description length criterion 沿用原正文和附录依据，移入 V-A。
- **复杂度的计算口径**：按常规稠密矩阵乘法与分解计数，三矩阵乘积按两次矩阵乘法求值。此口径是本文分析约定，不归为某篇论文的命名方法。当前实现中未优化三矩阵收缩的额外 O(M^4) 成本已单独记录，不将正文公式宣称为每条现有 NumPy 指令的严格成本；本轮未修改实现或运行性能实验。

精确原文定位、访问方式、适配范围及实现核对见本轮 [III 来源记录](../checks/chapters_3_5_revision_20261030/ch3/SOURCES.md)、[IV 来源记录](../checks/chapters_3_5_revision_20261030/ch4/SOURCES.md)、[V 来源记录](../checks/chapters_3_5_revision_20261030/ch5/SOURCES.md) 和 [根审实现核对](../checks/chapters_3_5_revision_20261030/ROOT_VERIFICATION_NOTES.md)。本轮只修订 C-STMP 的结构与表述，未改动共用物理定义，因而不改写 STMP/DU 的术语记录；既有相位候选记录完整保留。
