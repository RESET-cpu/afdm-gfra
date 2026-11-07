# 摘要、引言复查与第二章语言建议

日期：2026-11-04。对象：`main.tex` 摘要、`sections/01_introduction.tex` 和 `sections/02_system_model.tex`。下方保留实施前分析；当前状态以本节作者选择及实施记录为准。

## 最新作者选择与实施

| 编号 | 作者反馈与处理状态 |
|---|---|
| S01 及相邻三处 | 作者在连读复核后授权精简，并指出 collect 不够合适。四处已完成：有效信道直接引式、rows and columns、Define 引出跨天线定义、删去 in a matrix form。不是早先只删 a 的方案。 |
| S02 | 已获同意并实施。资源比较拆为两句，保持同段，保留时长、采样数及有用符号能量条件。 |
| S03 | 已获同意并实施。改为 `within a transmission block`。 |
| S04 | 已获同意并实施。改为 `variables as follows`，保留引用并以冒号引出公式。 |

S02–S04 的实施证据见[三处差异](../checks/ch2_language_selected_20261104/CHANGES.diff)及[核验记录](../checks/ch2_language_selected_20261104/VALIDATION.json)。随后新增的四处精简见[本轮差异](../checks/ch2_concise_definitions_20261104/CHANGES.diff)及[本轮核验](../checks/ch2_concise_definitions_20261104/VALIDATION.json)。两版仍为 13/14 页、46 个编号公式、42 篇参考文献；本轮所有行内及陈列数学内容、引用命令及其他章节保持，仅第 3 页文字变化，修改页已目视检查。

### 四处精简的最终写法

- `from device k to antenna m is the matrix` 改为 `from device k to antenna m can be expressed as`。
- `whose row and column indices correspond to ...` 改为 `whose rows and columns correspond to ...`，保留接收/发送符号的对应和天线范围。
- 原 `We collect the antenna channels in the device matrix` 整段引式文字改为 **Define**，紧接原有 $\mathbf H_k$ 定义。collect 不是语法错误，但这句的任务只是引入按公式排列的 $\mathbf H_k$，用 Define 更直接；不另外换成新的拼接术语。
- `the channel response can be expressed in a matrix form as` 改为 `the channel response can be expressed as`。

跨天线定义的转置、横向排列和维度全部保持。S01 及相邻三处已经关闭；下方“未实施／可选”的措辞属于之前的分析快照，不再代表当前状态。

## 实施前连读复核：摘要、引言与系统模型

作者再次要求将这三部分通读检查。本轮完整重读英文摘要、引言全部段落及贡献、Notation、第二章全部文字与公式、图 1 图注；以已完成 S02–S04 的现稿为准。结论是：未发现新的必要语言修改、前后术语冲突或模型表述矛盾。摘要和引言可以保持，第二章剩下的是上轮已讨论的 matrix/indices 类可选精简，不新增一批独立问题，也不重开已关闭事项。

| 检查维度 | 现稿判断 |
|---|---|
| 摘要到引言的对应 | 多帧 AFDM、完整有效信道先验、有色噪声训练和密度比活动检测的对象及作用一致。摘要用 soft information、引言进一步说明 Gaussian extrinsic messages，属于概述与具体说明的区别。 |
| 引言的论证顺序 | 卫星免授权接入、无 GNSS 需求、OTFS/AFDM 表示、稀疏先验限制、生成先验与 STMP、本文两项接收机动机和三点贡献能够衔接。没有必要新增泛指连接句。 |
| 引言到系统模型的条件 | 静止设备、设备各路径共同 Doppler、跨帧相位与固定参考信道相互对应；接收端公共时延补偿与设备不做预补偿不矛盾。 |
| 名称与缩写 | 摘要和正文分别定义缩写合理。当前三部分使用的 MFLE、GPJD、JADCE、AFDM、GNSS 一致；引言的三维 tensor 与本文每根天线的 matrix 是不同表示的比较。 |
| 数学对象及排列 | 物理信道向量、每根天线有效信道、跨天线拼接和跨设备堆叠分工清楚。按现有定义核对，$\mathbf A\in\mathbb C^{Q\times KN}$、$\mathbf X\in\mathbb C^{KN\times MN}$ 与 $\mathbf Y\in\mathbb C^{Q\times MN}$ 相容；$\mathbf H_{k,m}^{\mathsf T}$ 的拼接与 $\operatorname{vec}(\mathbf Y_q^{\mathsf T})$ 的次序相容。此处为现稿的静态阅读核对，没有新增公式推导或实验。 |
| 稀疏性与估计目标 | 由活动引起的设备块稀疏，与不对活动设备信道施加稀疏先验，已清楚区分；未发现两者混用。 |
| 已修改 S02–S04 | 拆句后的资源比较条件完整；transmission block 统一；后验引出句直接承接分解公式。三处均不再列为待修改。 |

可进一步简化的地方集中在 II-B 的一个段落，现稿行号如下。它们都是上轮讨论范围内的文字取舍，不是新的模型缺陷，也没有在本轮实施。

| 位置 | 当前表达 | 可选候选 | 保留的信息 |
|---|---|---|---|
| L144–145：有效信道引式句 | `the reference-frame channel from device k to antenna m is the matrix` | `the reference-frame channel from device k to antenna m can be expressed as` | 参考帧、设备、天线及后续完整公式。只省去重复报矩阵类型。 |
| L152–153：行列含义 | `whose row and column indices correspond to received and transmitted symbols, respectively` | `whose rows and columns correspond to received and transmitted symbols, respectively` | 行对应接收符号、列对应发送符号；后面的天线索引范围保持。 |
| L154：跨天线汇集 | `We collect the antenna channels in the device matrix` | `We collect the antenna channels as` | 后面的 $\mathbf H_k$ 定义、转置、排列和维度全部保持。 |
| L157–158：原 S01 | `the channel response can be expressed in a matrix form as` | `the channel response can be expressed as` | 增益、时延、Doppler 条件和后续公式全部保持。 |

以上候选只是普通引式词和重复类型说明的删改，不新增专业术语，也不冒充参考论文原句。matrix/indices 出现次数不作为缺陷依据：阵列响应、导频矩阵、DAFT 矩阵、对角矩阵和 AFDM/OTFS 维度比较中的名称仍有实际信息作用。

复用摘要 A01–A03、引言 I04/I05/I07 等已有决定，不再要求量化摘要、删除 CS 或改写引用作主语。此次没有修改任何稿件资产；核对上轮完成后的 26 个保护文件哈希，全部一致。只补充本记录，不重新编译 PDF。

## S01 追加讨论：字形能替代哪些文字

本稿 Notation 段已经约定粗体小写/大写分别表示向量/矩阵，因此不需要在每次出现符号时再报一次类型。应当看文字是否增加符号本身未说明的信息，而不是要求 matrix 或 indices 必须出现。

- **S01 的 `in a matrix form` 可以整段删除。** 这一句直接定义单路径信道响应，并非在对比一个刚给出的标量式与它的矩阵形式；候选为 `For a path with gain $1$, delay $dT_s$, and Doppler shift $\nu$, the channel response can be expressed as`。这是对本稿的删词建议，不声称为某篇文献原句。
- **`indices` 一词也不是必需。** 现有 `whose row and column indices correspond to received and transmitted symbols, respectively` 可以简化为 `whose rows and columns correspond to received and transmitted symbols, respectively`；后面的 $m=0,\ldots,M-1$ 保留。但行对应接收符号、列对应发送符号的含义应保留：粗体 $\mathbf H_{k,m}$ 以及设备/天线下标 $k,m$ 本身没有表达这层对应关系。
- **标量式到矩阵式的转换说明有作用。** L108–109 的 `The signal in ... can be represented in matrix form as` 在说明前后两个公式的关系，保留合理。此处与 S01 的句子任务不同。
- **identity matrix、diagonal matrix、DAFT matrix、pilot matrix 等名称不应仅凭字形删除。** 它们说明对象的性质或功能；粗体大写只说明类型。AFDM/OTFS 比较中的 $N\times N$ matrix 与三维 tensor 则直接承载表示维度比较。
- **`is the matrix`、`in the device matrix` 等引式搭配可以更简洁，但不需要全章机械替换。** 当前公式附近的设备、天线与排列关系清楚；是否进一步压缩按具体句子选择。本轮未将作者的询问当成全章删词授权。

以上是本轮针对作者问题的语言判断；S01 及相邻索引句仍为候选，未实施。S02–S04 已完成，不再列为待解决项。

## 摘要与引言复查结论

重新通读已修订版本后，没有发现新的、值得继续修改的语言或衔接问题，可以进入第二章。研究背景、文献不足、两个方法动机与三点贡献能够对应；本轮不再增加摘要或引言修改项。

继续执行[已有作者决定](ABSTRACT_INTRO_LANGUAGE_REVIEW_20261104.md)：A01/A02 保留，A03 暂不添加量化结果；I04 保留 CS，I05 保留引用编号作主语，I07 保持同一段。I01/I02/I03/I06/I08 的选定改动已落实。摘要与正文各自定义缩写合理；引言采用变换全称，第五章首次使用 DFT 缩写时定义，后文沿用。Shen 的 tensor 与本文的 channel matrix、device matrix、网络 arrays 表示不同对象，不作机械统一。

这项结论针对当前语言、术语一致性和段落衔接，不替代实验定稿，也不重开已经记录的研究问题。

## 第二章逐段覆盖

| 范围 | 复查判断 |
|---|---|
| 章首系统介绍及图 1 图注，L4–24 | 可保留。设备、卫星阵列、导频资源和无 GNSS 条件清楚；图注与正文说明活动在一块内不变，各自承担阅读任务，不算需要删除的重复。 |
| II-A 物理信道及差分时延，L30–58 | 可保留。时间变化、共同 Doppler、块内参数近似不变和接收端公共时延补偿的对象已有交代。前面的信道变化与后面的参数近似不变不是语言矛盾，不据此要求增加辩护。 |
| II-A 阵列响应，L60–71 | 可保留。array response vector、方向余弦和阵元间距的名称、索引定义对应清楚。 |
| II-B 多帧导频及设计条件，L76–96 | 可保留。按传输块、帧、导频向量、导频矩阵及能量条件依次引入，后文指向实验设置合理。 |
| II-B IDAFT、DAFT 及采样间隔，L98–124 | 可保留。标量信号到矩阵形式的关系明确，缩写已展开，不额外添加无必要的缩写或推导。 |
| II-B CPP 与分数时延波形，L126–142 | 可保留。沿用已批准的简洁呈现，不恢复长 CPP 推导。 |
| II-B 有效信道与单路径响应，L144–170 | 仅 S01 可选优化。接收/发送符号的行列索引承担必要定义，与引言已删除的索引罗列不同，应保留。 |
| II-B 跨帧相位和有效导频矩阵，L172–190 | 可保留。时间起点、相位累积及并入导频的叙述连贯。 |
| II-B AFDM/OTFS 表示比较，L192–199 | S02 可选拆句；维度、时长、采样数和有用符号能量的比较条件保持。 |
| II-C 活动变量，L203–217 | S03 可选统一 transmission block 的表达；不改变活动概率或块内恒定假设。 |
| II-C 堆叠观测及块稀疏性，L219–244 | 可保留。噪声句已在先前修订中解决；不恢复旧 Y/ A/ X/ W 的 entire 展开。来源句保留，不自动视为防御性说明。 |
| II-C 推断目标、先验与独立性，L246–255 | 可保留。完整信道先验与设备活动导致的块稀疏性已经区分。独立性明确为本文假设，沿用已记录的归属，不重新包装成参考论文同一技术陈述。 |
| II-C 后验引出句及估计目标，L256–280 | S04 建议修改引式句；固定参数条件、后验分解、似然、活动先验和最终估计目标保持。 |

## 完整候选表

以下为实施前的 4 项候选快照：1 项建议修改、3 项可选优化。行号对应当时源码；当前选择与实施状态见上文。候选是对本稿的语言编辑，不声称为参考论文原句；不增加专业术语、模型条件、公式或结论。

| 编号与位置 | 当前原文 | 判断 | 完整候选修改 | 边界与优先级 |
|---|---|---|---|---|
| **S01** · II-B 单路径响应，L157–158 | `For a path with gain 1, delay dT_s, and Doppler shift ν, the channel response can be expressed in a matrix form as` | `in a matrix form` 并非技术问题，但可与前文已有 `in matrix form` 统一。 | For a path with gain $1$, delay $dT_s$, and Doppler shift $\nu$, the channel response can be expressed in matrix form as | **可选**。只删 `a`；不另造 unit-gain path 等名称，不改变响应矩阵及条件。对应旧语言表 O04。 |
| **S02** · II-B AFDM/OTFS 比较，L197–199 | `With the same subcarrier spacing and prefix length, L AFDM frames span the duration of one OTFS frame, with the same number of useful samples and the same energy in the useful symbols when the OTFS frame uses LE_p.` | 一句同时承载时长、有效采样数和能量条件，读到句末才看到能量限定。原句成立，拆句仅提高可读性。 | With the same subcarrier spacing and prefix length, $L$ AFDM frames span the duration of one OTFS frame and contain the same number of useful samples. The energy in the useful symbols is also the same when the OTFS frame uses $LE_p$. | **可选**。只拆句，不另起段；保留全部资源匹配条件，不将有用符号能量扩写为含前缀的总发射能量。对应旧语言表 O05。 |
| **S03** · II-C 活动状态，L215–216 | `The activity states are assumed to remain constant during one block transmission.` | `one block transmission` 可理解，但前文已统一使用 `transmission block`，这里没有必要换一种语序。 | The activity states are assumed to remain constant within a transmission block. | **可选**。统一已有用语，保留 `assumed` 和块内活动恒定假设，不是新增术语或模型变更。 |
| **S04** · II-C 后验分解引出句，L256–260 | With $\widehat{\mathbf A}$ and $\widehat\sigma^2$ fixed as in Section~\ref{sec:frontend}, we factorize the joint posterior distribution according to Bayes' theorem and the conditional independence relationships among the variables, expressed as \cite{cai2026} | 句尾 `expressed as` 紧接 `variables`，引出下一式的句法关系不够清楚；可以直接接回主句的 `we factorize`。 | With $\widehat{\mathbf A}$ and $\widehat\sigma^2$ fixed as in Section~\ref{sec:frontend}, we factorize the joint posterior distribution according to Bayes' theorem and the conditional independence relationships among the variables as follows \cite{cai2026}: | **建议修改**。将 `, expressed as` 改为 `as follows` 并以冒号引式；其他词、固定条件、引用及整个公式保持。对应旧语言表 P04。 |

## 依据与未改动核验

- 已复用[写作规范](WRITING_GUIDE.md)、[作者决定记录](REVIEW_DECISIONS.md)和[第二章此前修订记录](../checks/ch2_remaining_fixes_20261101/REVISION_NOTES.md)。S01 使用本章 L108–109 已有、且写作规范已核到 Ding §II / PDF p.2 的搭配；只据此说明搭配依据，不声称整个路径响应句来自 Ding。
- S02 是本稿既有比较句的拆分，S03 复用本章 L36 的 `Within a transmission block`，S04 仅处理引式句法。均未增加文献事实或变更技术归属，无需新增术语条目。
- 本轮分析对象与[上轮完成后的核验记录](../checks/intro_language_selected_20261104/VALIDATION.json)一致：26 个受保护稿件资产的 SHA-256 全部匹配，包括所有正文、两版 PDF、书目和图件。只更新研究记录，不编译或修改论文。
- 上述哈希说明对应最初只分析的轮次；后续已按作者选择完成 S02–S04，当前核验见本文件顶部链接。S01 追加候选不自动升级为待解决缺陷。
