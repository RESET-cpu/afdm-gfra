# 第二章变量英文名称逐项核查

> 后续扩大核查见 [第二章全部名称清单](CHAPTER_II_NAMES_AUDIT.md)。其中 pilot vector 已另在当前引用的 Arvinte 论文核得；activity states 已核得 Ding 的单数原词；Ke 已在书目库但未列入当前 PDF；Tang 的 pilot energy 不属于现有书目。下文保留当轮记录，来源状态以扩大核查中的逐项补充为准。

> 作者随后要求替换，扩大清单特别列出的 13 项现已全部通过原词替换或直接数学表达处理；见[实际修改记录](../checks/ch2_named_expressions_revision_20261101/REVISION_NOTES.md)。本页仍是修改前的变量审计，不是当前待处理列表。

核查日期：2026-11-01。对象为 `sections/02_system_model.tex`，SHA-256：`ee2a176d5eda597807fbb028171a82b62cbc24d1dc111f134539c59f70b49f16`。本文档核查变量的英文名称、释义及完整搭配；不以字母是否与原论文相同判定通过。正文和阅读 PDF 本轮均未修改。

## 判定口径

- **有出处**：原文实际使用该英文名称，并且对应的对象类型适用。符号、序号及单复数可变化，不因此要求字母照抄。
- **补查有出处**：找到了明确论文用例，但该用例来自原主要母本之外。单独记录，不能追认成 Cai/Shen 的原词。
- **适配说明**：核心英文名称有出处，但当前完整修饰语或用途说明是本文的适配，不能称为完整原词。
- **待核**：本轮未核得含义匹配的完整论文用例；不能标为通过，也不表示整个学界从未使用。
- **未单独命名**：正文只给出公式、范围、索引或继承定义，没有另取英文名称。不能把核查者补写的名称算成正文原词；这本身不等于数学定义错误。

名称有出处，不代表本文公式、假设和参数设置已在该论文出现。检索完整搭配时允许 PDF 连字、断行与大小写归一化，不用单词的并集代替短语证据。

## 物理信道与阵列

| 变量 | 当前英文名称或释义 | 判定及原文定位 |
|---|---|---|
| $K$ | single-antenna terrestrial devices，数量由 $K$ 给出 | 有出处：Shen §II，PDF p.3，原文同一完整表达。 |
| $M$ | antennas，数量由 $M$ 给出 | 有出处：Shen §II，PDF p.3；Ding §II，PDF p.2。 |
| $M_y$ | 未单独写出英文名称 | 未单独命名：通过 $M=M_yM_z$ 及后续索引范围给出阵列维度。不能把另拟的名称冒充正文文字。 |
| $M_z$ | 未单独写出英文名称 | 未单独命名：同上。 |
| $k$ | $k$th device / $k$-th device | 有出处：Cai §II-A，PDF p.4；序号形式不构成新术语。 |
| $L_k$ | number of physical paths | 有出处：Shen §II-A，PDF p.3，式(1)后原词。 |
| $\ell$ | $\ell$th path | 有出处：Shen §II-A，PDF p.3 的 $i$-th path，仅改索引。 |
| $\mathbf h_k(t_{\rm c},\tau)$ | channel impulse response | 有出处：Li §II-B，PDF p.3，式(1)–(2)附近。 |
| $t_{\rm c}$ | time instant | 有出处：Li §II-B，PDF p.3，式(1)前。以块起点为零是本文约定，不是新的英文名称。 |
| $\tau$ | 未单独写出英文名称 | 未单独命名：式(1)的函数自变量；不要把补写的 delay variable 登记为正文已有名称。 |
| $\nu_k$ | common Doppler shift | 有出处：Huang §IV，PDF p.4 明确使用 common Doppler shift 描述同一链路各路径共享的 Doppler；不只是分别匹配 common 和 Doppler shift。 |
| $g_{k\ell}$ | path gain | 有出处：Shen §II-A，PDF p.3，式(1)后。 |
| $\tau_{k\ell}$ | differential delay | 有出处：Shen §II-A，PDF p.3，式(1)后。 |
| $\widetilde\tau_{k\ell}$ | propagation delay | 有出处：Shen §II-A，PDF p.3，式(1)后。 |
| $\tau_c$ | common delay | 有出处：Shen §II-A，PDF p.3，式(1)后及图1。 |
| $\mathbf a_k$ | array response vector | 有出处：Li §II-B，PDF p.3，式(2)后；p.4 阵列段。不能将其改称为已核实的 UPA response。 |
| $[\mathbf a_k]_{n_z+M_zn_y}$、$[\mathbf a_k]_m$ | 未另取名称，均为 $\mathbf a_k$ 的分量 | 继承 array response vector 的定义；不存在需要另作出处保证的新名称。 |
| $\delta(\cdot)$ | Dirac delta function | 有出处：Shen p.3 Notations；Li §II-B，p.3，式(2)后。 |
| $n_z$ | 未单独写出英文名称，只列取值范围 | 未单独命名。 |
| $n_y$ | 未单独写出英文名称，只列取值范围 | 未单独命名。 |
| $\lambda$ | wavelength | 有出处：Li §II-B，PDF p.4，阵列响应向量定义后。 |
| $d_v$ | spacing between adjacent antennas along the $v$-axis | 有出处：Li §II-B，PDF p.4，原文同一表达。 |
| $d_y$ | 由 $d_v$ 定义继承，取 $v=y$ | 有出处：沿用上项 spacing between adjacent antennas；坐标方向是本文选择。 |
| $d_z$ | 由 $d_v$ 定义继承，取 $v=z$ | 有出处：沿用上项；Li 的坐标为 $x/y$，本文为 $y/z$，不称其公式完全相同。 |
| $v$ | $v$-axis 中的方向索引 | 有出处：Li §II-B，PDF p.4 使用 $v$-axis；方向集合的变化是本文坐标适配。 |
| $\mu_{z,k}$ | directional cosines，沿 z-axis | 有出处：Shen §II-A，PDF p.3 的 directional cosines 及 z-axis。字母不一致不影响英文名称成立。 |
| $\mu_{y,k}$ | directional cosines，沿 y-axis | 有出处：Shen §II-A，PDF p.3 的 directional cosines 及 y-axis。 |

## AFDM、导频与跨帧关系

| 变量 | 当前英文名称或释义 | 判定及原文定位 |
|---|---|---|
| $N$ | chirp subcarriers，数量由 $N$ 给出 | 有出处：Huang §II，PDF p.2 首段的 AFDM chirp subcarriers。 |
| $Q$ | AFDM frames，数量由 $Q$ 给出 | 有出处：Huang §II，PDF p.2 的 AFDM frame；Shen §II-B，p.4 提供多帧安排的技术组织，不能混称为同一 AFDM 模型。 |
| $q$ | $q$th AFDM frame | 有出处：名称为 AFDM frame，Huang §II，p.2；序号是本文索引。 |
| $P_{qkn}$ | pilot symbol | 有出处：Cai §II-A，PDF p.4，式(2)之后。 |
| $n$（导频定义处） | $n$-th chirp subcarrier | 有出处：chirp subcarrier 为 Huang §II，p.2 原词的单数；序号是索引。 |
| $n$（式(7)后） | transmitted symbol position，原句与 received 合写为复数 | **待核**：Shen §II-B，p.4 只核得 received symbol position。本轮检得其他语境中的 transmitted symbol position 指星座点位置，不能为本文 DAFT 输入索引背书。 |
| $\mathbf p_{qk}$ | pilot vector | 补查有出处：Quayum 等，§II，PDF p.2，frequency domain pilot vector / time domain pilot vector。主要母本中未核得该完整搭配，不能归给 Cai 的 pilot matrix 原句。 |
| $\mathbf P$ | known pilot matrix | **适配说明**：pilot matrix 直接见 Cai §II-A，p.4；已知性是本文条件。Wei §II-A，p.2 的原词是 known analog spatial compression matrix，不能据此宣称 known pilot matrix 是该文原句。 |
| $[\mathbf P]_{q,(k-1)N+n}$ | entries | 有出处：Cai PDF p.14，Fig.12 附近的 pilot matrix whose entries…；具体索引为本文排列。 |
| $E_p$ | pilot energy | 补查有出处：Tang 等，*Pilot-Based Sensing With OFDM and AFDM: A Resource-Matched Performance Comparison*，§III-A，PDF p.3，式(10)前使用 pilot energy，且以平方模之和定义能量。**Cai p.4 的原词是 transmit power budget，不能直接作为 pilot energy 的词面出处。** Tang 为本轮新增检索到的预印本，只记录用词依据，未加入正文书目。 |
| $s_{qk}[t]$ | time-domain transmitted signal | 有出处：Ding §II，PDF p.2，式(1)前的完整原词。 |
| $t$ | 未单独命名，只给出离散取值范围 | 未单独命名；不补造 useful-sample index 等名称。 |
| $c_1$ | AFDM modulation parameters | 有出处：Ding §II，PDF p.2，式(1)后。 |
| $c_2$ | AFDM modulation parameters | 有出处：同上。 |
| $T_s$ | sampling interval | 有出处：Ding §II，PDF p.2，式(3)后；Li §II-A，p.3。 |
| $\Delta f$ | subcarrier spacing | 有出处：Li §II-A，PDF p.3；Shen §II-B，p.4。 |
| $\mathbf s_{qk}$ | signal in (3)，作为其 matrix form 引出 | 有出处：Ding §II，PDF p.2，The signal in (1) can be represented in matrix form as。继承前述 time-domain transmitted signal，不另取名称。 |
| $\mathbf F_{\rm A}$ | discrete affine Fourier transform (DAFT) matrix | 有出处：Xu §II-B，印刷 p.3／含封面 PDF p.4，式(6)–(7)之间的完整名称；Huang §II，PDF p.2 也使用 DAFT matrix。 |
| $r$ | received symbol position，正文并列句为复数 | 有出处：Shen §II-B，PDF p.4，式(9)后的 received symbol position；本文域和索引不同，不声称公式同源。 |
| $N_{\rm CPP}$ | chirp-periodic prefix (CPP) length | 有出处：Bemani §III-A，PDF p.8 给出 chirp-periodic prefix (CPP)，§III-B，p.9 明确使用 CPP length。 |
| $\langle x\rangle_N$ | 只有公式定义，没有英文名称 | 未单独命名。不要由 Shen 同形符号推断同一定义：Shen p.3 是居中的余数定义，本文为 $x-N\lfloor x/N\rfloor$。这是符号定义边界，不是本轮英文名称不通过项。 |
| $x$（取余定义中） | 无英文名称，函数自变量 | 未单独命名。 |
| $T_{\rm frame}$ | time duration of an AFDM frame with CPP | **适配说明**：Shen §II-B，p.4 原句为 time duration of a OFDM symbol with CP；AFDM frame、CPP 分别有 Huang/Bemani 来源。完整当前描述是 OFDM→AFDM、CP→CPP 的必要适配，不冒称逐字原词。 |
| $\varphi_n(\xi)$ | transmit waveform | 有出处：Shen §II-B，PDF p.4，式(3)前有 transmit waveform；Bemani §III-A，p.8 提供 AFDM 调制语境。本文完整连续波形公式不因此变成原文公式。 |
| $\xi$ | 未单独命名；正文写 at time $\xi T_s$ | 未单独命名；没有使用 normalized continuous time 等复合名称。 |
| $w_\xi$ | 仅由 $w_\xi=\langle\xi\rangle_N$ 定义 | 未单独命名。 |
| $\zeta_n(w)$ | 仅由 floor 公式定义 | 未单独命名；没有 frequency-folding index 等英文名称。 |
| $w$ | 无英文名称，函数自变量 | 未单独命名。 |
| $H_k^{(q)}$ | effective channel | 有出处：Shen §II-B，PDF p.4，式(9)后；Huang §II，p.2，式(4)后。 |
| $H_k^{(0)}$ | effective channel，$q=0$ 的情况 | 有出处：继承同一名称；未取额外专名。 |
| $H_k$ | effective channel | 有出处：同上；reference channel / canonical channel 等不在当前正文中。 |
| $H_{kmrn}$ | 未另取名称，$H_k$ 的分量 | 继承 effective channel 的定义，无独立英文名称。 |
| $m$ | antenna index | 补查有出处：Ke 等，*Compressive Sensing Based Adaptive Active User Detection and Channel Estimation: Massive Access Meets Massive MIMO*，Appendix A，PDF p.13；Appendix C，p.14 也有相同用词。 |
| $\mathbf G(d,\nu;g)$ | channel response，in a matrix form | 有出处：Ding §III-A，PDF p.2 使用 channel response；Bemani §III，p.8 使用 Fourier domain channel response。矩阵分解和参数化仍为本文已有定义。 |
| $dT_s$ | delay | 有出处：Shen §II-A，PDF p.3；Bemani §III-B，p.9。英文名字并非 unit-gain path。 |
| $d$ | 未另取名称；由 delay $dT_s$ 说明含义 | 未单独命名；integer $d$ 是条件描述，不是新名称。 |
| $\nu$ | Doppler shift | 有出处：Shen §II-A，PDF p.3；Li §II-B，p.3。 |
| $g$ | 仅用 $t_{\rm c}=(g+t)T_s$ 及 $g=N_{\rm CPP}$ 定义 | 未单独命名；不是 g_{kℓ}，也未在正文命名为 path gain。 |
| $\mathbf D_{\nu,g}$ | 仅定义矩阵公式 | 未单独命名。Ding p.2 的 Doppler matrix 是可核实的已有名称，但正文没有将该名称赋给此变量，不能虚报已完成命名。 |
| $\mathbf B_d$ | 仅定义矩阵元素 | 未单独命名；不补称为既有 delay matrix / interpolation matrix。 |
| $g_q$ | 仅给出 $g_q=N_{\rm CPP}+q(N+N_{\rm CPP})$ | 未单独命名。 |
| $\beta_k$ | 仅给出 wrap 公式；后文讨论 phase evolution across frames | 未单独命名；phase evolution across frames 是本文引言已有描述，不是给 β_k 核得了完整新专名。 |
| $\operatorname{wrap}(\cdot)$ | wrap；正文描述 maps an angle to $[-\pi,\pi)$ | **待核**：这是实际出现的英文函数名；主要母本中未核得相同函数名称及定义，不能把常见程序函数名自动算成论文出处。映射含义在正文已明确。 |
| $e^{jq\beta_k}$、$A_{qkn}$ 的相关限定 | inter-frame phase rotation | **待核**：Shen §II-B，PDF pp.4–5 有 phase rotation，并说明其跨多帧累积；本轮未核得 inter-frame phase rotation 的同义完整论文用例。检索到的专利不计入“论文出处”。 |

## 接收观测与贝叶斯推断

| 变量 | 当前英文名称或释义 | 判定及原文定位 |
|---|---|---|
| $\alpha_k$ | indicator function，描述 device activity | 有出处：Cai §II-A，PDF p.4，式(1)前后。 |
| $\rho$ | probability of a device being active | 有出处：Cai §II-A，PDF p.4，式(1)后的完整原词。该文用 λ，本文用 ρ，不影响英文名称通过。 |
| $X_k$ | 仅由 $X_k=\alpha_kH_k$ 定义 | 未单独命名；Cai §II-A，p.4 有同类定义，但当前正文没有 activity-weighted channel 等名称。 |
| $X_{kmrn}$ | 未另取名称，$X_k$ 的分量 | 未单独命名，继承式(11)、(13)的关系。 |
| $A_{qkn}$ | pilot symbols including the inter-frame phase rotation | **适配且限定词待核**：pilot symbols 为 Cai §II-A，p.4 原词；乘相位因子的作用由本文式(10)定义。完整后半句不作原词通过，见上一表。 |
| $\mathbf Y_q$ | received signal | 有出处：Cai §II-A，PDF p.4，式(3)前。 |
| $Y_{qmr}$ | 未另取名称，$\mathbf Y_q$ 的分量 | 继承 received signal；不是新名称。 |
| $\mathbf W_q$ | AWGN matrix | 有出处：Cai §II-A，PDF p.4，式(3)后；Wei §II-A，PDF p.2 也有完整词组。 |
| $W_{qmr}$ | 未另取名称，$\mathbf W_q$ 的分量 | 继承 AWGN matrix 的分量含义，无独立新名称。 |
| $\sigma^2$ | 第二章未单独写出英文名称，只出现在高斯分布中 | 未单独命名。noise variance 是 Shen §III，PDF p.7 的原词，但此处不能把解释性补充当作正文已经出现的名称。 |
| $\mathbf Y$ | received signal；observation | 有出处：Cai §II-A/B，PDF p.4，式(4)前及贝叶斯目标句。 |
| $\mathbf W$ | matrices 中的一项，式(13)由 $W_{qmr}$ 定义 | 未另取名称，继承噪声的定义。 |
| $\mathbf A$ | matrices 中的一项，式(13)由 $A_{qkn}$ 定义 | 未单独命名；当前第二章没有 effective pilot matrix / sensing matrix 这样的名称。 |
| $\mathbf X$ | matrix；性质为 block-sparsity structure | 有出处：Cai §II-A，PDF p.4，式(4)后的 matrix X exhibits a block-sparsity structure。性质不是给矩阵另造的名称。 |
| $[\mathbf Y]_{q,mN+r}$ | entries | 有出处：常规矩阵元素描述；Shen §II-C，PDF p.5 给出 matrix element 的具体索引说明，Cai p.14、Fig.12 附近使用 entries。 |
| $[\mathbf W]_{q,mN+r}$ | entries | 有出处：同上，具体排列是本文定义。 |
| $[\mathbf A]_{q,(k-1)N+n}$ | entries | 有出处：同上。 |
| $[\mathbf X]_{(k-1)N+n,mN+r}$ | entries | 有出处：同上。 |
| $q_{\rm tr}(H_k)$ | channel prior；for training 是用途说明 | 有出处：Cai 摘要，p.1；§II-B，p.5 使用 channel prior。**不把 channel prior for training 登记为 Cai 的完整专名**，也不把 q_tr 的具体分布归给 Cai。 |
| $\widehat{\mathbf A}$ | 第二章未单独命名，引用 Section V-A1 | 未单独命名；其估计来源由后文说明，不在本轮替正文新造名称。 |
| $\widehat\sigma^2$ | 第二章未单独命名，引用 Section V-A1 | 未单独命名；同上。 |
| $q(\mathbf X,\{H_k\},\{\alpha_k\}\mid\mathbf Y)$ | joint posterior distribution | 有出处：Cai §II-B，PDF p.4，式(5)前。q 与 p 的选择不影响名称，但不据此声称两文后验相同。 |
| $j$（列索引） | $j$th column | 有出处：Cai §II-B，PDF p.5 的 $m$-th column；Shen §III，p.9 也直接使用 j-th column。 |
| $\mathbf x_j$ | $j$th column of $\mathbf X$ | 有出处：Cai §II-B，PDF p.5 的 column of X，改列索引。 |
| $\mathbf y_j$ | $j$th column of $\mathbf Y$ | 有出处：Cai §II-B，PDF p.5 的 column of Y，改列索引。 |
| $p(\mathbf y_j\mid\mathbf x_j)$ | 第二章直接给出高斯分布，未单独写英文名称 | 未单独命名；likelihood 在 Cai §III，p.5 有出处，但当前第二章没有用该词给此因子命名。 |
| $p(X_k\mid H_k,\alpha_k)$ | enforces $X_k=\alpha_kH_k$，没有独立名词名称 | 未单独命名；enforces 是操作说明，不是一个技术名称。 |
| $p(\alpha_k)$ | 直接给出概率公式，未单独写英文名称 | 未单独命名；当前第二章没有称 Bernoulli prior，不能作为已出现英文名称登记。 |
| $X_k^{\rm MMSE}$ | MMSE estimate | 有出处：Li §IV-A，PDF p.8，Proposition 2、式(29)前；Cai §II-B，p.4 另有 MMSE estimator。 |
| $p_k^{\rm Bayes}$ | posterior probability of activity | 有出处：Cai §III-B2，PDF p.7，式(30)后，完整原词。 |

## 数学常量与通用运算记号

以下也逐项登记，防止把它们误当作遗漏的专业变量名称。它们在第二章多数没有附加英文定义句；本表不为其拟造英文专名。

| 记号 | 第二章的使用情况 | 依据或边界 |
|---|---|---|
| $\mathbf I_Q$ | 单位矩阵记号，无独立英文定义句 | Cai p.5 式(7)–(8)、Shen p.5 式(14)后的 identity matrix 是已有用法；Q 为本文维度。 |
| $\mathbb C$ | 复数域及向量/矩阵空间，无独立英文定义句 | Ding p.2 Notations 中 complex number field 的用法。 |
| $\mathbb N_+$ | 正整数集合，无独立英文定义句 | 本文用数学记号限制参数，没有为其另取英文名称。 |
| $\lfloor\cdot\rfloor$ | 向下取整，无英文定义句 | 当前没有 floor function 之类英文名称；不是本轮名称核查的通过项或失败项。 |
| $\operatorname{diag}$ | 对角矩阵运算，无英文定义句 | Shen p.3 Notations 的 diag(x) denotes the diagonal matrix…；Ding p.2 也使用。 |
| $\mathcal{CN}$ | 高斯分布记号 | Ding p.2 Notations；Cai p.4 式(3)后。本轮不复审引言 Notation 中完整统计术语。 |
| $\Pr(\cdot)$ | 概率运算记号 | 当前名称由 ρ 的 probability of a device being active 解释，具体事件由公式给出。 |
| $\mathbb E_q$ | 对 q 的期望记号，无英文定义句 | 下标 q 指本文式(14)的分布，不能说该完整带下标记号来自 Cai。 |
| $(\cdot)^{\mathsf T}$ | 转置记号，无第二章英文定义句 | Ding p.2 Notations：transpose。 |
| $(\cdot)^{\mathsf H}$ | 共轭转置记号，无第二章英文定义句 | Ding p.2 Notations：Hermitian transpose；Shen p.3 Notations。 |
| $\|\mathbf p_{qk}\|^2$ | 平方范数表达式，无独立英文名称 | 不将整个表达式作为新变量；其物理称谓 pilot energy 已单独核查。 |
| $\mathbf0$ | 零块记号 | Cai §II-A，p.4 同类 inactive-device 公式使用 0；无新英文名称。 |
| $j$（指数中） | 虚数单位 | Li §II-B，p.4 明确 $j=\sqrt{-1}$；与列索引的语境不同，不属于英文命名问题。 |
| $\pi$、$e$ | 数学常量 | 不另取英文名称，不因论文中重复出现而宣称需要专门术语出处。 |
| $\sum$、$\prod$、$\max$、$\propto$ | 求和、乘积、最大值、比例关系 | 数学运算记号，当前没有额外英文命名。 |
| 下标 y/z、下标 tr、上标 MMSE/Bayes | 坐标、训练用途及估计量标签 | y/z 见阵列定义；MMSE 对应现有名称；tr 和 Bayes 为本文标签，不是另一个已核实的方法名称。 |

## 本轮发现与处理建议（尚未改正文）

1. **不能笼统判定所有完整英文表达均来自原论文。** 核心名称多数有直接出处；known pilot matrix、time duration of an AFDM frame with CPP 是透明的适配描述，不能登记成母本完整原词。
2. **三项尚不能按严格标准通过：** transmitted symbol position、inter-frame phase rotation、wrap。第一项可优先回到 Ding/Xu 的 DAFT domain index 表述核对；第二项可用 Shen 已有的 phase rotation 并在句中说明帧索引；第三项可考虑直接保留角度映射的数学定义而不赋英文函数名。本轮只是建议，没有改动。
3. **三项补查来源应如实归属：** pilot vector→Quayum；pilot energy→Tang；antenna index→Ke。原主文书目未新增这些用词引用。pilot energy 不能从 Cai 的 transmit power budget 直接认定词面通过，能量与功率也不能在修改时互换。
4. **没有英文名称不等于自造名称。** 对 g、g_q、w_ξ、ζ_n、B_d 等，当前做法是公式直接定义。若以后需要添加文字称谓，应另核出处，不能把本报告的中文解释直接包装成已验证英文名。
5. 当前 source/PDF 的哈希与审计前一致；本轮只记录核查结果及来源，不改变量字母、公式或正文。

## 可复查来源

主核资料为 Shen、Cai（本地已发表版本及 v2）、Xu 作者稿、Ding、Wei；补用已有 Li、Huang、Bemani 原文。表中页码均为 PDF 页码，Xu 特别注明含封面的偏移。

- [Shen 原文](../../../reference/literature/shen2025.pdf)：PDF pp.3–5；[Cai 原文](../../../reference/literature/cai2026.pdf)：PDF pp.4–5、7、14。
- [Ding 原文](../../../reference/literature/ding2026.pdf)：PDF p.2；[Huang 原文](../../../reference/literature/huang2026.pdf)：PDF pp.2、4；[Wei 原文](../../../reference/literature/wei_yuan_2026_lstmp_v1.pdf)：PDF p.2。
- [Li 原文](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/strict_sentence_audit_20261029/sources/li2023.pdf)：PDF pp.3–4、8；[Bemani 原文](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/strict_sentence_audit_20261029/sources/bemani2022.pdf)：PDF pp.8–9。
- [Xu 作者稿入口](https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/AFDM-aided-Grant-Free-Random-Access-for-LEO/991050765702346)：本轮读取其仓储 PDF 的在线文本，§II-B、印刷 p.3／PDF p.4，式(6)–(7)。
- [Quayum 原文](../../../reference/literature/quayum2018_grantfree_pilots.pdf)：*Non-Orthogonal Pilot Designs with Collision Detection Capability For Grant-Free Access*，§II、PDF p.2。
- [Ke 原文](../../../reference/literature/ke2020_gmmv_amp.pdf)：Appendix A/C，PDF pp.13–14。
- [Tang 等预印本](https://arxiv.org/pdf/2610.23420)：§III-A，PDF p.3，式(10)前。原文短语为 “total useful-sample pilot energy per frame”；本轮只用来确认 pilot energy 的语言和能量含义。
- [本轮逐页摘录](../checks/ch2_variable_names_20261101/EVIDENCE.json)；[审计基线](../checks/ch2_variable_names_20261101/BASELINE.json)。

没有核得的完整表达只报告本轮检索边界，不作“无人使用”的断言；网络检索中的专利、培训材料及星座几何语境未被充当本文命名的论文依据。
