# 摘要与引言语言建议及作者决定

## 最新决定与实施（2026-11-04）

作者已逐项选择，以下状态取代后文早期分析中的“建议修改／待选择”。本轮仅修改引言及第五章 DFT 首次缩写定义，英文和中文摘要保持。

| 编号 | 作者决定与当前状态 |
|---|---|
| A01 | 保留摘要的定性对照表述。重读 Cai、Shen 摘要确认其结果句也未逐项点名基线；具体化对照名称不是必改要求，本项关闭。 |
| A02 | 保留原有模块介绍句及 MP 缩写，不拆句，本项关闭。 |
| A03 | 暂不增加量化结果；作者仍有实验待最终完成或定稿，不因某一批次完成就自动改写摘要。 |
| I01 | 已按作者新要求取消索引罗列，改为 `The effective channel at each antenna is represented by a three-dimensional tensor`；Shen §II-B 引用保持。不是采用旧候选 `is indexed by`。 |
| I02 | 引言改为 `inverse discrete Fourier transform`；第五章首次需要缩写时写 `discrete Fourier transform (DFT)`，其后的 inverse DFT 及第六章 DFT 直接沿用。 |
| I03 | 已改为 `Accurate joint activity detection and channel estimation (JADCE) is essential for AFDM-GFRA`，Ding 引用保持。 |
| I04 | 作者询问后文是否还需定义；全文核查表明 CS 只出现这一次。该项本来可选，本轮保留 `(CS)`，后文无需补定义。 |
| I05 | 保留以引用编号作主语的两句。这是可接受的学术写法，不再列为必须润色。 |
| I06 | 已删除 `A similar limitation has been highlighted for structured sensing matrices.`，前后失配说明直接衔接。 |
| I07 | 按作者要求保持同一段，用独立句子说明两条动机；没有在 Moreover 前插入段落分隔。 |
| I08 | 已将本方法贡献中的 `channel tensor` 改为 `effective-channel representation`，与前文及结论一致。 |

同时复查实际编入正文中的相关名称：Shen 的三维 tensor、本文每根天线的 channel matrix、跨天线的 device matrix 和网络输入 arrays 各自对应不同排列层次，现有定义明确，保留其区别；不机械替换第二章和第三章用于定义矩阵、向量顺序的 indices。

两版均已编译并检查修改页，仍为 13/14 页、46 个编号公式和 42 篇参考文献；摘要、公式、引用命令、图表及实验数值保持。见[本轮差异](../checks/intro_language_selected_20261104/CHANGES.diff)和[核验记录](../checks/intro_language_selected_20261104/VALIDATION.json)。

## 以下为选择前的分析快照

日期：2026-11-04。以下依据为作者选择前的 main.tex 摘要和 sections/01_introduction.tex 全文；其中行号、原文和未实施状态保留为历史快照，当前状态以上表为准。

总体判断：论证顺序完整，适合局部润色。摘要按空白分词约 193 词，不需要为了压缩篇幅而删掉既有方法动机。引言从卫星 GFRA 与 GNSS 独立需求，过渡到 OTFS/AFDM、稀疏恢复和生成先验，再到 STMP 的两项不足和本文贡献，衔接成立；没有提出重写引言或更换贡献组织。

共 11 项：4 项建议修改、5 项可选优化、2 项涉及内容增删，等待作者决定。所有候选均未实施，本表不构成修改授权。英文候选是基于本稿的改写，不冒充参考论文原句；引文键、专业术语和已有条件保持。

## 逐段覆盖

| 范围 | 判断与对应条目 |
|---|---|
| 摘要全部 9 句 | 对照对象建议明确；模块介绍可拆句；定量结果只是可选内容。其余研究目标、有色训练及密度比说明保持。A01–A03。 |
| 引言第 1 段：卫星 IoT 与 GFRA | 可保留。先说明握手开销再说明 GFRA 降低开销，是问题与方案对应，不作为无意义重复删除。 |
| 第 2 段：GNSS、预补偿与接收端需求 | 可保留。现有条件承担研究动机，不按语言简化删去；本轮未重新做标准时效审计。 |
| 第 3 段：OTFS 与 AFDM | I01 可优化索引表述，I02 展开 DFT；保留三个 OTFS 索引、静止设备和单天线有效矩阵等条件。 |
| 第 4 段：JADCE 与稀疏恢复 | I03 减少强调，I04 可删一次性 CS 缩写；其余按原论证保留。 |
| 第 5 段：生成先验与迭代采样 | I05 第一处调整句法可选。保留 Huang/Ying 的步骤与计算代价论述，不添加新批评。 |
| 第 6 段：STMP、训练失配与活动概率 | I05 第二处、I06、I07；不改 AWGN 条件、Tweedie 关系及 Gaussian 近似的原有判断。 |
| 三点贡献及其引出句 | 第一项 I08 统一表示名称；第二、第三项可保留。贡献再次概括前文是正常写法，不为避免重复而删除技术动机。 |
| 章节安排 | 可保留；没有必要机械拆成多个单句。 |

## 摘要

| 编号与位置 | 当前原文 | 问题判断 | 候选修改 | 含义边界与建议 |
|---|---|---|---|---|
| A01 · 摘要<br>[L70](../main.tex:70) | `Numerical simulations demonstrate that the proposed receiver outperforms the baseline receiver in activity detection and channel estimation.` | 摘要独立阅读时，the baseline receiver 没有明确指代。 | Numerical simulations demonstrate that the proposed receiver outperforms the white-noise-trained GP-MP baseline in activity detection and channel estimation. | **建议修改**。明确正文已定义的比较对象；不扩大成优于全部基线。GP-MP 是本文对照名称，不是新增技术术语。 |
| A02 · 摘要<br>[L61](../main.tex:61) | `The learned prior is then incorporated into a message-passing (MP) receiver with two modules: multi-frame linear estimation (MFLE), which suppresses inter-user interference; and generative-prior-aided joint denoising (GPJD), which performs minimum mean-squared error (MMSE) denoising.` | 一句同时介绍接收机、两个模块名、缩写和各自功能，阅读负担较集中；MP 在摘要只出现一次。原句语法成立。 | We incorporate the learned prior into a message-passing receiver with two modules: multi-frame linear estimation (MFLE) and generative-prior-aided joint denoising (GPJD). MFLE suppresses inter-user interference, while GPJD performs minimum mean-squared error (MMSE) denoising. | **可选优化**。仅拆句并去掉一次性 MP 缩写，模块名称、职责和 MMSE 表述保持；不是要求删掉所有缩写。原句也可保留。 |
| A03 · 摘要<br>[L72](../main.tex:72) | `outperforms the baseline receiver in activity detection and channel estimation.` | 结果句只有定性比较。加入量化结果可使贡献更具体，但目前摘要约 193 词，结构完整，不存在必须补数字才能成立的问题。 | 若决定增加，可接在结果句后：With known phases and fixed per-frame pilot energy at a received signal-to-noise ratio of 0 dB, the proposed receiver reaches a normalized mean-squared error of −14 dB using 25% fewer frames than GP-MP among the evaluated pilot-frame counts. | **内容选择；建议本轮暂不加**。这是将正文已验证结果加入摘要，不属于纯语言修正。24 对 32 帧的依据见上一轮核验；不能删除测试帧数、已知相位及能量条件，把它概括为普遍节省 25%。本轮倾向不加，避免结果句挤占方法说明。 |

## 引言

| 编号与位置 | 当前原文 | 问题判断 | 候选修改 | 含义边界与建议 |
|---|---|---|---|---|
| I01 · 引言第3段<br>[L39](../sections/01_introduction.tex:39) | `Its effective channel has three indices at each antenna, corresponding to Doppler, path delay, and the position of the received symbol along the delay dimension` | has three indices ... corresponding to 可以更直接，但原句没有技术或语法错误。 | At each antenna, its effective channel is indexed by Doppler, path delay, and the position of the received symbol along the delay dimension | **可选优化**。Shen 的三个索引含义与原有引用保持；不为了压缩而把第三个索引误写成接收天线或删掉。 |
| I02 · 引言第3段<br>[L42](../sections/01_introduction.tex:42) | `Its modulator consists of an inverse DFT and multiplications by two diagonal chirp matrices` | DFT 首次出现时未展开。该段之后不再使用此缩写，直接写全称即可。 | Its modulator consists of an inverse discrete Fourier transform and multiplications by two diagonal chirp matrices | **建议修改**。只展开现有变换名称，保留 Bemani 引用；不新增 IDFT 缩写，不把 DFT 与 DAFT 混同。后续章节实际使用 DFT 缩写时，可在那一处再定义。 |
| I03 · 引言第4段开头<br>[L52](../sections/01_introduction.tex:52) | `To realize the full potential of AFDM-GFRA, accurate joint activity detection and channel estimation (JADCE) is a crucial prerequisite` | full potential 与 crucial prerequisite 叠加强调，没有增加具体技术信息；可以更直接。 | Accurate joint activity detection and channel estimation (JADCE) is essential for AFDM-GFRA | **建议修改**。保留 JADCE 的必要性及 Ding 引用。不是因为 crucial 命中词表就认定有问题，而是整句强调重复。 |
| I04 · 引言第4段<br>[L54](../sections/01_introduction.tex:54) | `a compressed sensing (CS) problem` | CS 在引言只使用一次，括号缩写没有后续复用。原写法并不错误。 | a compressed sensing problem | **可选优化**。只删除一次性缩写，compressed sensing 的含义、稀疏性论述及引用不变。 |
| I05 · 引言第5、6段<br>[L69](../sections/01_introduction.tex:69)、[L88](../sections/01_introduction.tex:88) | `For massive random access, \cite{ying2026} proposes a two-stage algorithm that first identifies active devices through a Transformer-based detector and then uses generative diffusion models for joint channel estimation and data detection.`<br><br>`Moreover, \cite{cai2026} computes activity probabilities using Gaussian extrinsic messages obtained after projecting the channel posterior onto a Gaussian distribution.` | 两个句子都以引用编号作动作主语。工程论文常见，但改成方法或被动结构时，操作对象更自然。 | For massive random access, the two-stage algorithm in \cite{ying2026} first identifies active devices through a Transformer-based detector and then uses generative diffusion models for joint channel estimation and data detection.<br><br>Moreover, in \cite{cai2026}, activity probabilities are computed using Gaussian extrinsic messages obtained after projecting the channel posterior onto a Gaussian distribution. | **可选优化**。不改变对 Ying、Cai 的方法描述，不添加局限判断。两个位置可单独选择，不要求全篇改成同一种引文句法。 |
| I06 · 引言第6段<br>[L85](../sections/01_introduction.tex:85) | `A similar limitation has been highlighted for structured sensing matrices.` | similar limitation 与前句近似重复，has been highlighted 没有明确由谁指出。该句承接不到一个新的具体事实。 | 删除这一句。前句结尾 errors and the white Gaussian noise used for training. 直接接下一句 This mismatch can degrade channel denoising accuracy and, consequently, JADCE performance. | **删句选择；建议删除**。这是删去一条泛指文献陈述，不包装成语法修正。此前移除 Wei 引用时作者要求保留对应论述，所以本轮必须等作者选定；不自动恢复旧引用，也不重开 M3。 |
| I07 · 引言第6段<br>[L76](../sections/01_introduction.tex:76)、[L88](../sections/01_introduction.tex:88) | `The score-based turbo message passing (STMP) algorithm in \cite{cai2026}`<br><br>`performance. Moreover, \cite{cai2026} computes activity probabilities using` | 同一段先讲 AWGN 失配，再讲 Gaussian 近似对活动概率的影响，两条动机可以分开阅读。不是依据段落行数判定缺陷。 | 在 Moreover, ... 之前另起一段。前段保留 STMP、AWGN 条件与训练失配；后段保留活动概率及 Gaussian 近似。其余句序、内容和引用均保持。 | **可选优化**。仅改变段落边界，不新增相关性诊断或技术路线辩护。若希望保持现有紧凑结构，也可不分。与 I05 的句法调整、I06 的删句相互独立。 |
| I08 · 第一项贡献<br>[L104](../sections/01_introduction.tex:104) | `Additional pilot frames provide more observations without enlarging the channel tensor used by the learned prior.` | 第二章现已使用设备矩阵，网络部分才重排成三维数组；此处突然说 channel tensor，容易让人以为又引入不同对象。 | Additional pilot frames provide more observations without enlarging the effective-channel representation used by the learned prior. | **建议修改**。用已有 effective-channel representation 统一呈现层次。矩阵与网络数组是同一组系数的重排，不能把原句说成维度错误；不改变随帧数增加而保持信道表示大小的结论。 |

## 推荐的第一批范围

建议先选 A01、I02、I03、I08：明确摘要对照、展开首次缩写、减少一处重复强调、统一信道表示名称。

I06 倾向删除，但此前作者曾要求去掉 Wei 引用并保留对应论述，因此单独等待作者决定。A03 属于增加摘要内容，本轮倾向暂不添加。其余五项均为可选，保留原句也成立。I05 两个位置可以分开选；I05/I06/I07 分别对应句法、删句和分段，互不捆绑。

## 明确保留

- `score-based generative prior`、`colored Gaussian noise`、`density-ratio estimator`、`posterior probabilities of activity`、MFLE、GPJD 和 MMSE 继续采用已确认表述。
- 不将 `without imposing sparse or grid-aligned channel assumptions` 改成“没有稀疏性”：设备活动的块稀疏与信道本身的稀疏假设是不同对象。
- 保留 `may`、`can`、`Under the common per-device Doppler model`、`at matched bandwidth and transmission duration` 和 `across the evaluated ...`；不通过润色扩大适用范围。
- 保留摘要及引言各自首次定义常用缩写的安排；不把这种独立阅读需要误判为重复定义。
- 保留三点贡献及其技术内容，不新增“首次”“最优”“彻底消除失配”或优于所有方法等断言，不补回正文兜底或开发过程。
- 输入输出、delay–Doppler 等技术复合词与公式记号不按 Humanizer 通用破折号规则机械更换；没有依据单个词认定文本为 AI 写作。

## 依据与验证

应用 paper-polish 和 Humanizer，并以 [WRITING_GUIDE.md](WRITING_GUIDE.md)、[TERMINOLOGY.md](TERMINOLOGY.md) 及 [REVIEW_DECISIONS.md](REVIEW_DECISIONS.md) 的作者决定为准。重新阅读 Cai、Shen 本地 PDF 的摘要作为表达层次参考；这不代表候选英文来自其原句，也不把它们的修辞和模块设置机械移植到本文。

I01 的索引内容沿用现稿已核查的 Shen §II-B；I02 保留原 Bemani §§II-B/III-A 引用；I03 保留 Ding 引用；I08 使用本稿已确认的描述性 `effective-channel representation`，不是新方法名称。A03 的数量依据来自上一轮 [润色前复核](POLISH_READINESS_20261104.md) 中的 24/32 帧核验，没有新增结果。已批准的密度比及模块措辞，按术语记录 2026-11-02 的确认版本保留。

旧全文语言表的 P01/P02/O01/O02/O03/D01 与本表对应条目不重复计数。此表定位于当前摘要和引言，旧行号不能代替本表位置。

13 处原文摘录均与当前源码匹配；定位信息与候选见 [SUGGESTIONS.json](../checks/abstract_intro_language_review_20261104/SUGGESTIONS.json)。包括源码、两版 PDF、图形及书目在内的 26 个受保护文件保持不变，见 [VALIDATION.json](../checks/abstract_intro_language_review_20261104/VALIDATION.json)。
