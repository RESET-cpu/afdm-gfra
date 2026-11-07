# C-STMP 全文语言修改建议表（仅分析，未实施）

**当前版本提示（2026-11-04 后续复核）：下表是早期快照，并非所有条目仍待处理。** P03、P10、P11、P14、D02 已由后续修订解决或取代；O07 部分已处理，原附录 C 现为 B。尤其不得按旧 P10/P11/P14 恢复范围外兜底或固定设置自证。完整状态及当前润色前复核见 [POLISH_READINESS_20261104.md](POLISH_READINESS_20261104.md)。其余候选也须重新对应现稿，不构成全文修改授权。

日期：2026-11-04。对象：当前 `main.tex` 主稿及 `main_full.tex` 增补内容。

作者要求：先分析哪些需要改，列完整表格，不直接修改。前一轮直接改动的引言与两版 PDF 已撤回，恢复到该轮之前的版本；此前确认的图表改动仍保留。见[撤回记录](../checks/intro_language_polish_20261104/REVISION_NOTES.md)。

总体判断：全文已具备可读的学术英文结构，适合局部润色，无需整篇重写。本表是通读后的候选修改清单，不是错误数量或审稿严重等级。“建议修改”指有明确的清晰度收益，仍不意味着每句原文都不合语法；“可选优化”可以全部保留原文；“先判断再处理／随结果定稿”不作为本轮自动修改范围。

使用 paper-polish 与 Humanizer 作语言分析，并遵循本稿 [WRITING_GUIDE.md](WRITING_GUIDE.md)、[TERMINOLOGY.md](TERMINOLOGY.md) 和 [REVIEW_DECISIONS.md](REVIEW_DECISIONS.md)。第三至第五章保留已确认的段落组织。下表英文是候选表达，不宣称是参考论文原句；实施前仍需按既有出处记录核对涉及的专业表达。本轮没有新增技术名称、引用、实验事实或证据强度。

## 覆盖范围

| 范围 | 阅读与判断 |
|---|---|
| 标题、摘要、关键词、符号说明 | 已读；标题和关键词可保留，摘要建议明确对照方法。作者信息占位符属于既有定稿事项。 |
| I 引言 | 已逐段读；主要是首次缩写、少量修辞和一处衔接重复。贡献边界和已有术语保持。 |
| II 系统模型 | 已逐段读；建议修正少量搭配和公式引出句。既有独立性假设等已确认措辞保留。 |
| III 接收机框架 | 已逐段读；只建议两处对象/介词澄清，无段落重排。 |
| IV 先验学习 | 已逐段读；只建议明确实数表示和损失比较对象。 |
| V 算法与复杂度、Algorithm 1 | 已读；输入含义、分支指代、每设备调用数值得明确；初始化顺序文字另列判断项。 |
| VI 全部实验小节、两张表、图 1–10 的 LaTeX 图注 | 已读；实验参数说明和少量结果句可更清楚；图注未发现需要单独修改的语言问题。未重新核验图中全部像素标签或研究结果。 |
| VII 结论 | 已读；可保留，也可拆开一处长句。 |
| 附录 A：相位估计 | 已读；方案正在设计，随既有相位工作统一文字，不现在改写算法段落。 |
| 附录 B：AFDM 信道矩阵 | 已读；推导衔接和表述可保留，无单独修改建议。 |
| 附录 C：配置与评估协议，仅 full 版 | 已读；建议明确 pooled AER 与停止条件的比较对象，计数表达可选优化。 |
| 参考文献及未编入的草稿 | 本轮不重新审计书目信息；`appendix_second_order_training.tex`、中文摘要草稿未编入当前两版，未列入本次英文正文建议表。 |

## 完整建议表

所有条目均为 **未实施、未获批**。位置指本轮恢复后的源稿；原文以源文件为准，表内只合并换行。

合计 31 项：建议修改 19 项，可选优化 9 项，先判断或随结果定稿 3 项。

### A. 建议修改

| 编号与位置 | 当前原文 | 原因 | 候选修改 | 含义与范围边界 |
|---|---|---|---|---|
| **P01** 摘要<br>[L66](D:/afdm-gfra/paper/C-STMP/main.tex:66) | `outperforms the baseline receiver in activity detection and channel estimation.` | 摘要独立阅读时，the baseline receiver 没有明确指代；可直接写出现有对照名称。 | `outperforms the white-noise-trained GP-MP baseline in activity detection and channel estimation.` | 沿用第 VI 章和结论已明确的 GP-MP 对照；不扩大为优于所有方法，也不补新数值。 |
| **P02** I 引言，AFDM 介绍<br>[L42](D:/afdm-gfra/paper/C-STMP/sections/01_introduction.tex:42) | `Its modulator consists of an inverse DFT and multiplications by two diagonal chirp matrices` | DFT 在全文首次出现时没有展开；补全称谓便于独立阅读。 | `Its modulator consists of an inverse discrete Fourier transform (DFT) and multiplications by two diagonal chirp matrices` | 只展开已有缩写，不更换调制结构或新增方法名称；原有 Bemani 引用保留。 |
| **P03** II 观测模型<br>[L242](D:/afdm-gfra/paper/C-STMP/sections/02_system_model.tex:242) | `AWGN matrix with the elements i.i.d. drawn from $\CN(0,\sigma^2)$.` | with the elements i.i.d. drawn 的搭配生硬；用完整定语从句表达。 | `AWGN matrix whose entries are drawn independently from $\CN(0,\sigma^2)$.` | 所有元素来自同一给定分布，独立同分布条件保持。 |
| **P04** II 后验分解引出句<br>[L283](D:/afdm-gfra/paper/C-STMP/sections/02_system_model.tex:283) | `With $\widehat{\mathbf A}$ and $\widehat\sigma^2$ fixed as in Section~\ref{sec:frontend}, we factorize the joint posterior distribution according to Bayes' theorem and the conditional independence relationships among the variables, expressed as \cite{cai2026}` | 句尾 expressed as 的修饰对象不清；改为直接引出下一公式。 | `With $\widehat{\mathbf A}$ and $\widehat\sigma^2$ fixed as in Section~\ref{sec:frontend}, we factorize the joint posterior distribution using Bayes' theorem and the conditional independence relationships among the variables as follows \cite{cai2026}:` | 固定条件、独立性假设、引用及后验公式均保留。 |
| **P05** III 因子图引出句<br>[L6](D:/afdm-gfra/paper/C-STMP/sections/03_bayesian_receiver_design.tex:6) | `Figure~\ref{fig:receiver-structure} represents the posterior in \eqref{eq:working-posterior}.` | 明确图中展示的是后验的因子图，和现有图注一致。 | `Figure~\ref{fig:receiver-structure} shows the factor graph of the posterior in \eqref{eq:working-posterior}.` | factor graph 已在本稿图注及术语记录中使用；不改变图或概率模型。 |
| **P06** III 活动检测<br>[L107](D:/afdm-gfra/paper/C-STMP/sections/03_bayesian_receiver_design.tex:107) | `Marginalizing the channel under the active hypothesis yields the likelihood` | 补 over，直接说明对信道变量作边缘化。 | `Marginalizing over the channel under the active hypothesis yields the likelihood` | 保留 active hypothesis 与 likelihood，不修改积分和假设。 |
| **P07** IV 复数到实数表示<br>[L19](D:/afdm-gfra/paper/C-STMP/sections/04_generative_priors.tex:19) | `The real observation is` | real 也可被读成“实际的”；real-valued 明确表示实数形式。 | `The real-valued observation is` | 只澄清已有实虚堆叠表示，不改噪声模型。 |
| **P08** IV 一阶训练目标<br>[L75](D:/afdm-gfra/paper/C-STMP/sections/04_generative_priors.tex:75) | `For each fixed $\mathbf C$, this differs from score matching weighted by $\bm\Sigma$ by a term independent of $\theta$.` | this 的对象及“损失与方法相比较”的表述不够明确；写明比较的是两个损失。 | `For each fixed $\mathbf C$, this loss differs from the score matching loss weighted by $\bm\Sigma$ by a term independent of $\theta$.` | 保留固定 C、Sigma 权重及差项与 theta 无关的全部条件；不新增等价结论。 |
| **P09** V 去噪器输入<br>[L22](D:/afdm-gfra/paper/C-STMP/sections/05_overall_algorithm.tex:22) | `For a Gaussian input $(R_k,v)$, the denoiser gives` | 当前简写容易把参数对本身读成高斯随机输入；指出均值、方差对应的消息。 | `For an input Gaussian message with mean $R_k$ and variance $v$, the denoiser gives` | 沿用第三章 input Gaussian message 的定义，不改局部观测模型。 |
| **P10** V Algorithm 1，GPJD 分支<br>[L83](D:/afdm-gfra/paper/C-STMP/sections/05_overall_algorithm.tex:83) | `\item Otherwise, retain the sites and obtain $p_k$ from` | 上一行已经有一个 otherwise；第二个 Otherwise 容易被误接到 tau 条件。 | `\item If $v$ lies outside the training interval, retain the sites and obtain $p_k$ from` | 仅显式写出训练区间外这一既有分支，不改 sites 保留规则或概率公式。 |
| **P11** V 复杂度<br>[L201](D:/afdm-gfra/paper/C-STMP/sections/05_overall_algorithm.tex:201) | `The $1+2L_z$ denoiser evaluations and one classifier evaluation within the training interval give the per-iteration complexity` | 说清网络调用次数按每设备计，与下一式前面的 K 对应。 | `When $v$ lies within the training interval, each device requires $1+2L_z$ denoiser evaluations and one classifier evaluation, giving the per-iteration complexity` | 每设备成本已由前句定义；不增加调用次数或改变复杂度公式。 |
| **P12** VI 训练与验证数据<br>[L70](D:/afdm-gfra/paper/C-STMP/sections/06_simulation_results.tex:70) | `Training and validation use $50{,}000$ and $5{,}000$ clean $16\times16\times16$ channels from disjoint scenes, four per scene before multiplication by $\alpha_k$.` | 原句把两种用途、维度、场景分离和每场景数量压在一起；拆成两句消除尾部悬挂。 | `We use $50{,}000$ clean $16\times16\times16$ channels for training and $5{,}000$ for validation, drawn from disjoint sets of scenes. Each scene provides four channel samples before multiplication by $\alpha_k$.` | 样本数量、维度、场景互不重合及乘活动变量之前取样全部保持。 |
| **P13** VI 分类器训练<br>[L91](D:/afdm-gfra/paper/C-STMP/sections/06_simulation_results.tex:91) | `We then freeze the denoiser and train the classifier from random initialization by \eqref{eq:classifier-loss}, using batch size $32$,` | train ... by equation 搭配不自然；说明使用该式定义的损失。 | `We then freeze the denoiser and train the classifier from random initialization using the loss in \eqref{eq:classifier-loss}, with batch size $32$,` | 冻结去噪器、随机初始化、批量大小及后续学习率和轮次保留。 |
| **P14** VI 对比接收机设置<br>[L158](D:/afdm-gfra/paper/C-STMP/sections/06_simulation_results.tex:158) | `With fixed adaptations to multiantenna AFDM, weights, and activity decision rules, SOMP selects up to $64$ atoms,` | 当前 with 短语把 adaptations、weights、rules 挤在一起，weights 的对象也不够明白。 | `We keep the adaptations to multiantenna AFDM, the network weights, and the activity decision rules fixed. SOMP selects up to $64$ atoms,` | 仅明确现有固定条件，不新增基线设置；后续迭代数、层数原样保留。 |
| **P15** VI 阻尼参数<br>[L173](D:/afdm-gfra/paper/C-STMP/sections/06_simulation_results.tex:173) | `Their default damping factors are $0.2$ and $0.4$.` | 显式对应两个接收机与两个参数，避免依赖读者回看前句。 | `The default damping factors for GP-MP and GP-MP-CCD are $0.2$ and $0.4$, respectively.` | 只明确默认值的对应关系，不改变其他配置或特定实验设置。 |
| **P16** VI 主 SNR 结果<br>[L339](D:/afdm-gfra/paper/C-STMP/sections/06_simulation_results.tex:339) | `With known phases, GP-MP-CCD achieves the lowest NMSE and achieves lower AER than GP-MP.` | 同一句重复 achieves，删除一次即可。 | `With known phases, GP-MP-CCD achieves the lowest NMSE and a lower AER than GP-MP.` | 保留 known phases；不把 lower AER than GP-MP 扩大为 lowest AER。 |
| **P17** VI 跨信道剖面对比<br>[L394](D:/afdm-gfra/paper/C-STMP/sections/06_simulation_results.tex:394) | `Figure~\ref{fig:cstmp-cross} compares the training profile D with profiles A, B, and C without retraining.` | 图中对比的是不同剖面下的估计性能，而不是剖面本身。 | `Figure~\ref{fig:cstmp-cross} compares channel-estimation performance on the training profile D and on profiles A, B, and C without retraining.` | 保留不重新训练及后句的几何、导频、设置固定条件。 |
| **P18** 附录 C，活动概率对比<br>[L48](D:/afdm-gfra/paper/C-STMP/sections/appendix_evaluation_protocol.tex:48) | `AER is computed from all device decisions across these conditions, including outputs that reach the iteration limit.` | 现在表 II 同时报告分 SNR 与汇总值；此处 across these conditions 描述的是 pooled AER。 | `The pooled AER is computed from all device decisions across these conditions, including outputs that reach the iteration limit.` | 仅补限定词 pooled，不改统计口径、结果或样本纳入规则。 |
| **P19** 附录 C，停止条件<br>[L160](D:/afdm-gfra/paper/C-STMP/sections/appendix_evaluation_protocol.tex:160) | `together with a small difference from the previous exponential moving average,` | 补明与移动平均比较的对象，避免被理解为前面刚出现的 site 参数。 | `together with a small difference between the activity probabilities and their previous exponential moving averages,` | 比较对象由紧随其后的原公式明确给出；公式与阈值不变。 |

### B. 可选优化

| 编号与位置 | 当前原文 | 原因 | 候选修改 | 含义与范围边界 |
|---|---|---|---|---|
| **O01** I OTFS 表示<br>[L39](D:/afdm-gfra/paper/C-STMP/sections/01_introduction.tex:39) | `Its effective channel has three indices at each antenna, corresponding to Doppler, path delay, and the position of the received symbol along the delay dimension` | 原句正确；indexed by 比 has three indices ... corresponding to 更直接。 | `At each antenna, its effective channel is indexed by Doppler, path delay, and the position of the received symbol along the delay dimension` | 三个索引含义及 Shen 的引用保留；不按喜好更换技术术语。 |
| **O02** I JADCE 动机<br>[L52](D:/afdm-gfra/paper/C-STMP/sections/01_introduction.tex:52) | `To realize the full potential of AFDM-GFRA, accurate joint activity detection and channel estimation (JADCE) is a crucial prerequisite` | full potential 与 crucial prerequisite 有强调重复；压缩后观点不变。 | `Accurate joint activity detection and channel estimation (JADCE) is essential for AFDM-GFRA` | 这是减轻修辞，不是判定原句有技术问题；原 Ding 引用保留。 |
| **O03** I 文献叙述<br>[L69](D:/afdm-gfra/paper/C-STMP/sections/01_introduction.tex:69)、[L88](D:/afdm-gfra/paper/C-STMP/sections/01_introduction.tex:88) | `For massive random access, \cite{ying2026} proposes a two-stage algorithm that first identifies active devices through a Transformer-based detector and then uses generative diffusion models for joint channel estimation and data detection.`<br><br>`Moreover, \cite{cai2026} computes activity probabilities using Gaussian extrinsic messages obtained after projecting the channel posterior onto a Gaussian distribution.` | 可把引用编号作主语改为方法作主语或 in 引用结构，叙述更自然；原写法在工程论文中常见，不是语法硬伤。 | `For massive random access, the two-stage algorithm in \cite{ying2026} first identifies active devices through a Transformer-based detector and then uses generative diffusion models for joint channel estimation and data detection. / Moreover, in \cite{cai2026}, activity probabilities are computed using Gaussian extrinsic messages obtained after projecting the channel posterior onto a Gaussian distribution.` | 不改变对被引工作步骤或近似方式的描述。 |
| **O04** II 矩阵表示<br>[L171](D:/afdm-gfra/paper/C-STMP/sections/02_system_model.tex:171) | `the channel response can be expressed in a matrix form as` | in matrix form 更简洁常用；去掉不必要的 a。 | `the channel response can be expressed in matrix form as` | 只改普通搭配，矩阵表达和前后条件不变。 |
| **O05** II AFDM/OTFS 对比<br>[L211](D:/afdm-gfra/paper/C-STMP/sections/02_system_model.tex:211) | `With the same subcarrier spacing and prefix length, $L$ AFDM frames span the duration of one OTFS frame, with the same number of useful samples and the same energy in the useful symbols when the OTFS frame uses $LE_p$.` | 一句同时交代时长、有效采样数和能量，拆句更容易读；原句并非错误。 | `With the same subcarrier spacing and prefix length, $L$ AFDM frames span the duration of one OTFS frame and contain the same number of useful samples. The energy in the useful symbols is also the same when the OTFS frame uses $LE_p$.` | 保留子载波间隔、前缀长度和 OTFS 使用 LEp 的比较条件，不概括成无条件等价。 |
| **O06** V 内存开销<br>[L215](D:/afdm-gfra/paper/C-STMP/sections/05_overall_algorithm.tex:215) | `excluding parameters and network activations.` | parameters 泛指略宽；点明这里排除网络参数。 | `excluding network parameters and activations.` | 原句前文已说明 shared network parameters，故只是回指澄清。 |
| **O07** VI 导频及噪声设置<br>[L15](D:/afdm-gfra/paper/C-STMP/sections/06_simulation_results.tex:15)、[L32](D:/afdm-gfra/paper/C-STMP/sections/06_simulation_results.tex:32) | `For $Q\leq KN$, select distinct DFT rows`<br><br>`For the noiseless received signal $\mathbf Y_0=\mathbf A\mathbf X$, set` | 正文实验说明可统一为 we select / we set；算法框仍用祈使句。原祈使句也成立。 | `For $Q\leq KN$, we select distinct DFT rows / For the noiseless received signal $\mathbf Y_0=\mathbf A\mathbf X$, we set` | 不统一全文时态，不动导频或 SNR 定义。 |
| **O08** VII 结论<br>[L9](D:/afdm-gfra/paper/C-STMP/sections/07_conclusion.tex:9) | `Based on this model, we learned a score-based generative prior from multiantenna AFDM effective channels without imposing sparse or grid-aligned channel assumptions, with colored Gaussian noise used to account for correlations in denoiser-input errors.` | 原句同时交代先验对象、假设边界和训练动机；拆句可减轻阅读负担。 | `Based on this model, we learned a score-based generative prior from multiantenna AFDM effective channels without imposing sparse or grid-aligned channel assumptions. We used colored Gaussian noise to account for correlations in denoiser-input errors.` | 保留所有限定及既有动机强度，不把相关性训练动机改写成已消除失配。 |
| **O09** 附录 C，漏检与虚警计数<br>[L57](D:/afdm-gfra/paper/C-STMP/sections/appendix_evaluation_protocol.tex:57) | `The receivers using the learned density ratio and Gaussian approximation produce $(111,3)$ and $(187,31{,}207)$ missed detections and false alarms, respectively, over $84{,}960$ device decisions.` | 展开两组二元组，减少 respectively 的双重对应；原句可以理解，属于可读性选择。 | `Over $84{,}960$ device decisions, the receiver using the learned density ratio produces $111$ missed detections and $3$ false alarms; the receiver using the Gaussian approximation produces $187$ missed detections and $31{,}207$ false alarms.` | 四个计数、分母和方法对应关系原样保持。 |

### C. 先判断或随结果定稿

| 编号与位置 | 当前原文 | 原因 | 候选修改 | 含义与范围边界 |
|---|---|---|---|---|
| **D01** I 失配动机衔接<br>[L85](D:/afdm-gfra/paper/C-STMP/sections/01_introduction.tex:85) | `A similar limitation has been highlighted for structured sensing matrices.` | 这句话与前句相近，又没有明确“由谁指出、指哪种限制”；单纯换几个词不能补足指代。 | 倾向删去这一句，让前句的 denoiser-input errors / training-noise mismatch 直接接到 This mismatch can degrade ...；若作者希望保留独立文献事实，则应明确它所指的 limitation 及具体引用。 | 删句会移除一个独立陈述，因此只列建议，不归入可自动执行的纯语言修改。现有 M3 动机和技术路线不重审。 |
| **D02** V 正文与 Algorithm 1 的顺序<br>[L53](D:/afdm-gfra/paper/C-STMP/sections/05_overall_algorithm.tex:53)、[L70](D:/afdm-gfra/paper/C-STMP/sections/05_overall_algorithm.tex:70) | `After normalization, we initialize $\mathbf X^{{\rm pri},(0)}=\mathbf0$,`<br><br>`initialize as above and normalize as in Section~\ref{sec:frontend}.` | 正文与算法框的表述顺序不一致；目前只能确认文字不一致，不能据此判定实现出错。 | 正文已写先归一化再初始化；算法框若保持相同顺序，可写 normalize as in Section~\ref{sec:frontend}, then initialize as above。正式替换时应同时核对当前实现，避免仅凭语言偏好规定运算顺序。 | 本轮没有验证或改动算法执行顺序；不把此项升级为新的研究阻塞。 |
| **D03** VI 相位结果；附录 A/C 的相关段落<br>[L341](D:/afdm-gfra/paper/C-STMP/sections/06_simulation_results.tex:341) | `With estimated phases, GP-MP-CCD-EP retains most of the channel-estimation gain.` | most of the ... gain 的比较对象可更明确，但应先确定最终采用的相位方案和曲线，避免现在反复改写。 | 等正在设计的相位算法及对应实验定稿后，再统一这句比较对象、相位实验引出句、附录 A 算法说明和附录 C 的相位设置；当前保留原文。 | 属于已知 M4 工作的文字收尾，不是新增 major 问题；不增加实验要求，也不写入未完成的结果。 |

## 明确保留及本轮不扩展的内容

| 内容 | 本轮处理 |
|---|---|
| 结果段现在时、结论过去时 | 保留现有语境选择，不作全局时态替换。 |
| where、yield、denote、therefore 等数学常用词 | 根据句子任务保留，不按关键词计数判定“AI 味”。 |
| posterior probabilities of activity 等已确认、留有出处的表述 | 不为词汇变化而换成同义词；O03 只涉及句子主语组织。 |
| 第三至第五章分段及蔡文段落对应 | 保留；表内建议均限于句内或原段内，未提议重建章节结构。 |
| common per-device Doppler、known phases、without retraining 等条件 | 保留，不通过压缩句子扩大结论。 |
| 有色训练、二阶估计路线和相关性诊断 | 沿用既有决定，不要求正文补写开发历史，不重开 M2/M3。 |
| 摘要是否增加量化结果、相位实验和可选基线预算实验 | 随实际结果及作者的最终安排处理，不在语言润色时补造或提前承诺。 |
| 已确认的图字号、图 9 坐标范围、表 II 的分 SNR 报告 | 保留，不重新安排图表修改。 |

## 核验与后续使用

本表的 34 处原文摘录均按空白归一化后与当前源文件匹配，并记录真实行号。审阅前后的 26 个稿件、PDF、图形及书目文件以 SHA-256 核对；详见[核验记录](../checks/language_review_20261104/VALIDATION.json)。没有修改正文、公式、图表、书目或当前 PDF，没有编译或运行实验。此前撤回操作及其历史快照另行保留。

后续只按作者明确选定的条目实施；这份清单本身不构成修改授权。若实施 D01 或 D02，应将其与纯语言改动区分并说明实际依据；D03 等相位方案定稿时再处理。
