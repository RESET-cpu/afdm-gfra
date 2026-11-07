# 第三至第五章语言分析与修改候选

日期：2026-11-04。对象：当前 `sections/03_bayesian_receiver_design.tex`、`sections/04_generative_priors.tex`、`sections/05_overall_algorithm.tex`，包括图 2/3 的文字说明和 Algorithm 1。状态：**作者已授权全部 11 项，现已实施；IV02、V05 采用后续讨论确认的正面表述。**

以下原候选表及行号保留为分析时快照，最终写法以文末实施表为准。IV03 同步了第六章训练设置及网络输入的两处排列名称；没有开展第六章全文润色。两版 PDF 已更新并检查：13/14 页、46 个编号公式、42 篇参考文献。公式、伪代码、引用命令及图表资产保持。详细论述导读见[第三至第五章逻辑说明](CHAPTERS_III_V_LOGIC_GUIDE_20261104.md)。

## 总体判断

三章的任务分工清楚：第三章给出推断框架与局部估计目标；第四章给出学习方法；第五章将估计器组织为完整算法，说明参数处理和复杂度。当前适合局部修订，没有提出重写章节、重新划分段落或增加推导/实验的要求。

共 11 项候选：7 项建议修改，4 项可选优化。建议项主要涉及指代、名称一致性与交叉引用；可选项包括重复缩写定义和冗余类型说明。它们不是审稿严重程度分级。完整英文候选是针对本稿的编辑，不声称是参考文献原句。

沿用[写作规范](WRITING_GUIDE.md)、[33 段来源映射](../checks/paragraph_revision_20261103/PARAGRAPH_MAP.md)和[作者决定](REVIEW_DECISIONS.md)：保留已确认的三章组织，不恢复长 CPP、矩阵预条件或中央差分的额外推导，不恢复 κ 更新显示式、Gaussian evidence 兜底段或伪代码范围外分支。S01–S04 与摘要、引言既有决定不重开。

## 第三章

| 编号与位置 | 原文 | 判断与原因 | 完整候选 | 含义边界 |
|---|---|---|---|---|
| **III01** · 开头，L6–7 | `Figure ... represents the posterior in ...` | **建议修改**。图展示的是后验的因子图；明确图的类型比笼统的 represents 更清楚，也与图注一致。 | Figure~\ref{fig:receiver-structure} shows the factor graph of the posterior in \eqref{eq:working-posterior}. | 沿用现有 factor graph 及后验对象，图、公式和因子关系不变。对应旧语言表 P05。 |
| **III02** · III-B2，L102–104 | `Marginalizing the channel under the active hypothesis yields the likelihood q_{1,v}, whereas q_{0,v} is the Gaussian noise density under the inactive hypothesis, with the expectation over H∼q_tr:` | **建议修改**。补 over；句尾的 expectation 说明紧接 inactive hypothesis，但期望实际只出现在活跃密度 $q_{1,v}$ 中。将先验说明移到边缘化对象旁。 | Marginalizing over $\mathbf H$ with prior $q_{\rm tr}$ under the active hypothesis yields the likelihood $q_{1,v}$, whereas $q_{0,v}$ is the Gaussian noise density under the inactive hypothesis: | 只调整式前说明，两个密度公式和先验不变。原式没有算错，是句子挂接不够清楚。包含旧 P06，不重复计数。 |

第三章 L69–71 的 vec 定义建议保留。这里不只是说明对象有索引，而是在指定向量化时哪个位置变化最快；它与第四章 Kronecker 协方差以及网络重排有关。字形不能代替该顺序。本轮建议通过 IV03 统一后文名称，而不是删除这条定义。

## 第四章

| 编号与位置 | 原文 | 判断与原因 | 完整候选 | 含义边界 |
|---|---|---|---|---|
| **IV01** · IV-A，L19 | `The real observation is` | **建议修改**。这里指实数表示，real-valued 比 real 更明确。 | The real-valued observation is | 保留复数到实数的转换及协方差，不改变观测模型。对应旧 P07。 |
| **IV02** · IV-B，L75 | `For each fixed C, this differs from score matching weighted by Σ by a term independent of θ.` | **建议修改**。this 指的是损失；比较对象也应是损失，而不是笼统的 score matching 方法。 | For each fixed $\mathbf C$, this loss differs from the score matching loss weighted by $\bm\Sigma$ by a term independent of $\theta$. | 固定 C、Σ 权重和差项与 θ 无关的现有陈述保持，不增加显示公式，也不将“最优解相同”改成“两个损失值完全相同”。对应旧 P08。 |
| **IV03** · IV-B，L100 | `The Kronecker factors follow the antenna--output--input order.` | **建议修改**。第二、三章使用 received/transmitted symbols，这里换成 output/input，且缺少明确的指代对象。统一已有对象名称更清楚。 | The Kronecker factors correspond to the antennas, received symbols, and transmitted symbols, respectively. | 顺序与 $\mathbf R_{\rm a}\otimes\mathbf I_N\otimes\mathbf R_{\rm c}$ 保持：天线、接收符号、发送符号。与第三章“发送符号变化最快”相容。若选择此项，应同步 VI-A2 的 L79 与 VI-A3 的 L97 两处同类措辞，只统一名称，不改维度或数据排列。 |
| **IV04** · IV-B，L104–105 | `Reshaping ... defines the complex-valued matrix denoiser F_θ(R,C).` | **可选精简**。real/complex 的区别有意义；matrix 在此可省略，输出重排和粗体符号已说明形式。 | Reshaping the real and imaginary outputs of $\mathbf f_\theta$ defines the complex-valued denoiser $\mathbf F_\theta(\mathbf R,\mathbf C)$. | 只删 matrix；保留实虚重排、去噪器及全部参数。延续第二章的精简原则，不改变网络输出形状。 |

IV03 是名称统一，不是认定原排列错误。这里列出的 VI 两处只是该术语的同步位置，不构成对第六章的全面润色或修改授权。

## 第五章

| 编号与位置 | 原文 | 判断与原因 | 完整候选 | 含义边界 |
|---|---|---|---|---|
| **V01** · V-A，L7–9 | `GP-MP-CCD combines the multi-frame linear estimation (MFLE) ... with generative-prior-aided joint denoising (GPJD) ...` | **可选精简**。两项缩写已在引言正文定义，第五章再次全称加括号不是错误，但可以压缩。 | GP-MP-CCD combines MFLE in Section~\ref{sec:linear-estimation} with GPJD using the estimators in Section~\ref{sec:learning}. | 保留模块名称、对应章节和学习估计器的作用，不重命名模块。 |
| **V02** · V-A，L22 | `For a Gaussian input (R_k,v), the denoiser gives` | **建议修改**。$(\mathbf R_k,v)$ 是输入消息的均值、方差参数；写成 Gaussian input 容易混淆消息近似与输入观测本身的分布。 | For an input Gaussian message with mean $\mathbf R_k$ and variance $v$, the denoiser gives | 沿用第三章的消息定义，后面的去噪输出和活动概率公式保持。对应旧 P09。 |
| **V03** · V-B，L136–138 | `with the current approximate posterior \eqref{eq:mixture} held fixed` | **建议修改引用指向**。现稿式 (19) 只给出 $\widehat{\mathbf X}_k=p_k\mathbf H_k^{\rm post}$，即后验均值；近似后验分布本身在 III-B3 的文字中定义。当前把该均值公式直接当作后验的指代不够准确。 | Minimizing the expected Gaussian negative log likelihood over the input variance $v$, with the current approximate posterior in Section~\ref{sec:joint-extrinsic} held fixed \cite[Sec.~III-A]{vila2013}, gives | 只将后验指向 III-B3；期望负对数似然、固定后验条件、Vila 引用及方差更新式 (37) 均保持。不据此判定方差更新错误或要求重新推导。 |
| **V04** · V-C，L184–185 | `where C_FFT(n) is the cost of an n-point FFT or inverse FFT` | **可选完善**。FFT 在编入正文中尚未展开。它是常用缩写，但补全有助于与前面 DFT 的处理保持一致。 | where $C_{\rm FFT}(n)$ is the cost of an $n$-point fast Fourier transform (FFT) or inverse FFT. | 只展开已有缩写，不另引入 IFFT。前后乘法计数和已补好的 DFT 定义保持。 |
| **V05** · V-C，L219–221 | `excluding parameters and network activations.` | **可选明确**。这里排除的是网络参数；前文已有 shared network parameters，句尾可直接说清。 | excluding network parameters and activations. | 不改变存储复杂度的统计对象或量级，只使回指明确。对应旧 O06。 |

## 逐段覆盖与保留判断

| 范围 | 检查结果 |
|---|---|
| III 章首和图 2 图注 | III01；图注的变量节点、因子节点和设备块说明具有信息作用，保留。 |
| III-A 线性后验、协方差近似和外信息，L27–60 | 过程顺序清楚；per-column covariance 与 scalar variance 的区别必要，不按 matrix 出现次数删词。 |
| III-B 开头及局部观测，L65–79 | 先给条件信道估计与活动概率、再组合估计的顺序合理；vec 顺序和局部消息模型保留。 |
| III-B1 条件统计量，L84–96 | 条件、近似符号及通向 V-A 的计算引用清楚；不恢复此前已删的重复局部模型限定。 |
| III-B2 密度与概率，L101–119 | III02；保留精确目标 $p^\star$ 与所用近似 $p_k$ 的区别。 |
| III-B3 混合分布、空间协方差及反馈，L124–166 | 定义到矩计算、平均与外信息相除的衔接成立。$0<b<1$ 是正方差条件，保留；第五章裁剪是实现说明，不能因重复出现 b 就删除。 |
| IV 章首，L4–7 | 承接第三章均值/方差与活动概率两个任务，可保留。 |
| IV-A 有色观测与 Tweedie 关系，L12–56 | IV01；实表示、条件均值、协方差和白噪声特例分工清楚，不删除实复转换或固定 C 条件。 |
| IV-B 得分目标、去噪器参数化与损失，L61–92 | IV02；期望对象与条件均值最优性承担必要说明，不作为防御性文字删除。 |
| IV-B 有色训练及接收机调用，L94–109 | IV03/IV04；有色训练与白协方差调用是当前方法定义，不重新打开 M2/M3 技术路线讨论。 |
| IV-C 导数恒等式及有限差分，L114–145 | 当前只保留所需关系及实际估计式，文字顺畅；保持已确认的推导篇幅。 |
| IV-D 密度比、训练数据与后验概率，L150–197 | 从 log odds 到二分类学习及实际活动先验修正的顺序清楚。两类训练使用相同 v 分布、理想函数最优解与学习估计的区别都保留。 |
| V-A 模块总览、方差、site 及算法指引，L7–55 | V01/V02；Gaussian site 的相除和重新结合保持，不添加长解释或新的命名。 |
| Algorithm 1，L65–107 | 已确认的逐行伪代码、输入输出、控制结构与主算法顺序可以保留；不恢复 Gaussian evidence 兜底或训练范围外分支。 |
| V-B 相位与噪声估计，L118–134 | 估计对象、MDL 来源、低秩信号/白噪声条件明确，均保留。 |
| V-B 方差目标及 κ 更新，L136–149 | V03；κ 更新继续使用文字表达，不重新加显示公式。 |
| V-B 归一化与双向阻尼，L151–177 | 归一化定义、同符号约定、截断位置和首轮不阻尼都可保留；算法框的先归一化后初始化已解决，旧 D02 不再提出。 |
| V-C 波形成本与 SVD 形式，L182–204 | V04；固定相位条件、Q 范围、SVD 复用和公式关系保留。 |
| V-C 计算与存储复杂度，L206–221 | V05；每设备网络调用数已明确，旧 P11 不再提出。保持相位成本、分解成本和网络成本的区分。 |

## 来源、历史条目与核验

- 直接重读 Cai 期刊版 `reference/literature/cai2026.pdf`：PDF p.5 / §III 的因子图与两模块任务，p.8 / §IV-B 的 score matching objective 与 denoising score matching objective，p.9 / §V-A 的学习估计器接入算法，p.11 / §V-C 的 fast Fourier transform (FFT) 原词。该核对用于结构和术语依据，不把本文的有色目标、密度比或具体实现归为 Cai 原式。
- [既有 33 段来源映射](../checks/paragraph_revision_20261103/PARAGRAPH_MAP.md)和[公式呈现记录](FORMULA_PRESENTATION_AUDIT_20261104.md)继续适用。本轮候选只在原段内部处理句子或引用，不改变段落来源归类。
- III01/III02/IV01/IV02/V02/V05 分别复用或扩展旧语言表 P05/P06/P07/P08/P09/O06；不重复计为另一批缺陷。旧 P10/P11/D02 已被后来修改取代，不列入本表。
- IV03 使用本稿 II-B、III-B 已定义的接收/发送符号；Kronecker 排列不变。V03 的现稿编号通过 `main.aux` 核对：`eq:mixture` 为式 (19)，`sec:joint-extrinsic` 为 III-B3，`eq:query-variance-target` 为式 (37)。
- 本轮未修改任何 TeX、PDF、公式、图表或实验资产。26 个保护文件的 SHA-256 与[上轮完成后的记录](../checks/ch2_concise_definitions_20261104/VALIDATION.json)全部一致。只新增本建议表并更新文档导航和决定记录。

以上为原分析时状态；作者后续已明确授权全部候选，处理结果如下。

## 作者决定与实施结果

作者指出原 IV02 的 `differs from ...` 和 V05 的 `excluding ...` 带有防御性。随后明确要求：这两项按新建议修改，其余修改也全部执行。

| 编号 | 最终处理 |
|---|---|
| III01 | 用 `shows the factor graph of the posterior` 明确图 2 的对象。 |
| III02 | 将 `with prior q_tr` 放在活跃假设下的信道边缘化对象旁，避免误接到非活跃密度。 |
| IV01 | 改为 `real-valued observation`。 |
| IV02 | 采用 `For each fixed C, this objective has the same minimizers as the score matching objective weighted by Σ.`；保留固定协方差和权重，不再叙述参数无关差项，不声称损失值相等。 |
| IV03 | 统一为 antennas、received symbols、transmitted symbols；同步 VI-A1/A2 对应两处，Kronecker 因子、维度和数据排列保持。原分析表的 VI-A2/A3 是旧定位，当前训练和网络架构为 VI-A1/A2。 |
| IV04 | 删除 `complex-valued matrix denoiser` 中冗余的 matrix。 |
| V01 | 直接使用引言已定义的 MFLE、GPJD。 |
| V02 | 明确输入为均值 R_k、方差 v 的 Gaussian message。 |
| V03 | 近似后验由式 (19) 改指 III-B3；方差目标式 (37) 保持。 |
| V04 | 展开 `fast Fourier transform (FFT)`，保留原乘法计数。 |
| V05 | 采用 `The pilot matrix, SVD factors, channel messages, and spatial covariances require O(QKN+KMN²+KM²) memory.`；以正面列举限定统计对象，删除 shared network parameters 的引句和 excluding 尾句，复杂度量级保持。 |

本轮不新增公式、术语、引用或算法分支；不改网络、训练和实验配置。备份、逐处差异、编译日志、修改后分页渲染及核验见[本轮检查目录](../checks/chapters_iii_v_language_selected_20261104/)与[核验结果](../checks/chapters_iii_v_language_selected_20261104/VALIDATION.json)。原 11 项均关闭，后续不再作为等待作者选择的问题提出。
