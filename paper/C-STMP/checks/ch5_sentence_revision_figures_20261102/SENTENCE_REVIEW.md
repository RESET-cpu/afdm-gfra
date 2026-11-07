# 第五章逐句修订对照

覆盖 51 个原句单元；修改 20 个、保留 31 个。公式引出语计入句子单元；三处长句拆开，不能把该数等同于最终句号数量。

本记录对应本轮合并后的正文。段落组织及术语/句式来源按实际支持程度分别登记。Algorithm 1 另见末尾记录。

## ch5_a-P01-S01 — 保留

**原文**

```latex
Substituting the estimators developed in Section~\ref{sec:learning}
into the framework of Section~\ref{sec:algorithm} yields
GP-CCD-MP-DRE, which
combines a generative prior (GP), covariance-conditioned denoising
(CCD), message passing (MP), and density ratio estimation (DRE).
```

**改后**

```latex
Substituting the estimators developed in Section~\ref{sec:learning}
into the framework of Section~\ref{sec:algorithm} yields
GP-CCD-MP-DRE, which
combines a generative prior (GP), covariance-conditioned denoising
(CCD), message passing (MP), and density ratio estimation (DRE).
```

**理由**：现有句子已将 IV 的估计器代入 III 的框架并解释既定名称，完整保留，避免为换句而改变算法含义。

- Cai et al., arXiv:2506.00581v2；V-A, (55)–(56), Fig. 3 前后；PDF p.9。支持层次：原段论证关系。
  保留学习结果代入通用框架后得到具体算法的组织方式；本文模块名称和均值导数、活动分类器为既有方案，不把这些操作登记为蔡文原法。
  核对锚点：integration of the two score networks into the TMP framework
- 本文现有 C-STMP 稿件；III–V 现有公式和 Algorithm 1。支持层次：本文操作／定义／公式衔接。
  本句的具体估计器、Gaussian site、接受条件、参数、初始化和数值处理是本文既有内容。未在已读五篇母本中确认同一技术句，不假称来自某篇原句。
  核对锚点：current manuscript equations and algorithm conditions

## ch5_a-P01-S02 — 修改

**原文**

```latex
The linear estimation in Section~\ref{sec:linear-estimation}
forms the multi-frame linear estimation (MFLE) module.
```

**改后**

```latex
The multi-frame linear estimation (MFLE) module performs the linear estimation in Section~\ref{sec:linear-estimation}.
```

**理由**：以 MFLE 模块为主语直接交代其作用，与后一句 GPJD 的功能说明平行，少一层 forms 的反向命名。

- Wei and Yuan, arXiv:2610.17785v1；III-A, Network Overview；PDF p.2。支持层次：同任务段落关系／模块功能表述。
  读完该段中 Module A 处理观测、Module B 利用学习先验的分工；本文使用 MFLE/GPJD 的既定名称，不移入展开层、层间校准或训练参数。
  核对锚点：each layer follows the two-module structure of STMP
- 本文现有 C-STMP 稿件；III–V 现有公式和 Algorithm 1。支持层次：本文操作／定义／公式衔接。
  本句的具体估计器、Gaussian site、接受条件、参数、初始化和数值处理是本文既有内容。未在已读五篇母本中确认同一技术句，不假称来自某篇原句。
  核对锚点：current manuscript equations and algorithm conditions

## ch5_a-P01-S03 — 修改

**原文**

```latex
The joint
denoising in Section~\ref{sec:joint-denoising}, implemented with
the learned channel and activity estimators, forms the
generative-prior-aided joint denoising (GPJD) module.
```

**改后**

```latex
The generative-prior-aided joint denoising (GPJD) module implements the joint denoising in Section~\ref{sec:joint-denoising} using the learned channel and activity estimators.
```

**理由**：以 GPJD 模块为主语，将实现对象与所用估计器顺接，移除主语和谓语之间较长的插入修饰。

- Wei and Yuan, arXiv:2610.17785v1；III-A, Network Overview；PDF p.2。支持层次：同任务段落关系／模块功能表述。
  读完该段中 Module A 处理观测、Module B 利用学习先验的分工；本文使用 MFLE/GPJD 的既定名称，不移入展开层、层间校准或训练参数。
  核对锚点：each layer follows the two-module structure of STMP
- 本文现有 C-STMP 稿件；III–V 现有公式和 Algorithm 1。支持层次：本文操作／定义／公式衔接。
  本句的具体估计器、Gaussian site、接受条件、参数、初始化和数值处理是本文既有内容。未在已读五篇母本中确认同一技术句，不假称来自某篇原句。
  核对锚点：current manuscript equations and algorithm conditions

## ch5_a-P02-S01 — 保留

**原文**

```latex
For a Gaussian input $(R_k,v)$, the denoiser gives
$F_k=F_\theta(R_k,v\I_D)$, and the classifier gives $p_k$ in
\eqref{eq:activity-probability}.
```

**改后**

```latex
For a Gaussian input $(R_k,v)$, the denoiser gives
$F_k=F_\theta(R_k,v\I_D)$, and the classifier gives $p_k$ in
\eqref{eq:activity-probability}.
```

**理由**：输入、两个估计器及其输出已在同一句清楚对应，白噪声在线条件 vI 保留。

- Cai et al., arXiv:2506.00581v2；V-A, (55)–(56) 前后；PDF p.9。支持层次：同任务原段关系。
  从学习网络到所需矩的推进方式相同；本文均值、导数迹及跨设备平均保持现有数学式，不导入二阶网络。锚点省略公式变量。
  核对锚点：we are able to obtain the posterior mean ... and variance
- 本文现有 C-STMP 稿件；III–V 现有公式和 Algorithm 1。支持层次：本文操作／定义／公式衔接。
  本句的具体估计器、Gaussian site、接受条件、参数、初始化和数值处理是本文既有内容。未在已读五篇母本中确认同一技术句，不假称来自某篇原句。
  核对锚点：current manuscript equations and algorithm conditions

## ch5_a-P02-S02 — 保留

**原文**

```latex
With
$\widehat\tau_k=\widehat\tau_\theta(R_k,v\I_D)$ from
\eqref{eq:derivative-trace}, we use the common conditional variance
```

**改后**

```latex
With
$\widehat\tau_k=\widehat\tau_\theta(R_k,v\I_D)$ from
\eqref{eq:derivative-trace}, we use the common conditional variance
```

**理由**：承接均值和活动概率继续给出导数方差与共用方差，公式会显示平均及下限操作，不重复解释。

- Cai et al., arXiv:2506.00581v2；V-A, (55)–(56) 前后；PDF p.9。支持层次：同任务原段关系。
  从学习网络到所需矩的推进方式相同；本文均值、导数迹及跨设备平均保持现有数学式，不导入二阶网络。锚点省略公式变量。
  核对锚点：we are able to obtain the posterior mean ... and variance
- 本文现有 C-STMP 稿件；III–V 现有公式和 Algorithm 1。支持层次：本文操作／定义／公式衔接。
  本句的具体估计器、Gaussian site、接受条件、参数、初始化和数值处理是本文既有内容。未在已读五篇母本中确认同一技术句，不假称来自某篇原句。
  核对锚点：current manuscript equations and algorithm conditions

## ch5_a-P03-S01 — 保留

**原文**

```latex
Here $\tau_{\min}>0$ is a numerical floor.
```

**改后**

```latex
Here $\tau_{\min}>0$ is a numerical floor.
```

**理由**：简洁定义紧接新出现的下限符号，保留正值条件，不增加正值性辩解。

- 本文现有 C-STMP 稿件；III–V 现有公式和 Algorithm 1。支持层次：本文操作／定义／公式衔接。
  本句的具体估计器、Gaussian site、接受条件、参数、初始化和数值处理是本文既有内容。未在已读五篇母本中确认同一技术句，不假称来自某篇原句。
  核对锚点：current manuscript equations and algorithm conditions

## ch5_a-P04-S01 — 修改

**原文**

```latex
To represent the learned channel moments in Gaussian messages,
we use a site approximation to the channel prior
\cite[Sec.~2.1]{vehtari2020}, of the form
$\CN(\vect(H_k);\vect(E_k),c_k\I_D)$.
```

**改后**

```latex
We incorporate the learned channel moments into message passing through a site approximation to the channel prior \cite[Sec.~2.1]{vehtari2020}, of the form $\CN(\vect(H_k);\vect(E_k),c_k\I_D)$.
```

**理由**：直接说明学习矩如何进入消息传递，再给 Gaussian site 的形式，使本段承接前述估计结果；名称、引用和数学对象不变。

- 本文现有 C-STMP 稿件；III–V 现有公式和 Algorithm 1。支持层次：本文操作／定义／公式衔接。
  本句的具体估计器、Gaussian site、接受条件、参数、初始化和数值处理是本文既有内容。未在已读五篇母本中确认同一技术句，不假称来自某篇原句。
  核对锚点：current manuscript equations and algorithm conditions
- Vehtari et al., 2020（现有方法引用）；正文现有 Sec. 2.1 引用；TERMINOLOGY.md 登记 pp.5–6。支持层次：既有技术引用保留；非本轮语言母本。
  本轮不重写 site approximation 的理论来源，不把未重新读取的原文计作句式母本；Gaussian 相除/相乘衔接依据当前明确给出的两条公式。
  核对锚点：site approximation（本轮读到的是术语登记，未新增原文摘录）

## ch5_a-P04-S02 — 保留

**原文**

```latex
Dividing the Gaussian approximation with mean $F_k$ and variance
$\tau$ by the input likelihood gives
```

**改后**

```latex
Dividing the Gaussian approximation with mean $F_k$ and variance
$\tau$ by the input likelihood gives
```

**理由**：Gaussian 近似除以输入 likelihood 是 site-update 的实际操作，原句清楚，保留。

- 本文现有 C-STMP 稿件；III–V 现有公式和 Algorithm 1。支持层次：本文操作／定义／公式衔接。
  本句的具体估计器、Gaussian site、接受条件、参数、初始化和数值处理是本文既有内容。未在已读五篇母本中确认同一技术句，不假称来自某篇原句。
  核对锚点：current manuscript equations and algorithm conditions
- Vehtari et al., 2020（现有方法引用）；正文现有 Sec. 2.1 引用；TERMINOLOGY.md 登记 pp.5–6。支持层次：既有技术引用保留；非本轮语言母本。
  本轮不重写 site approximation 的理论来源，不把未重新读取的原文计作句式母本；Gaussian 相除/相乘衔接依据当前明确给出的两条公式。
  核对锚点：site approximation（本轮读到的是术语登记，未新增原文摘录）

## ch5_a-P05-S01 — 修改

**原文**

```latex
Combining the site with the current input then yields
```

**改后**

```latex
Multiplying this site by the current Gaussian input likelihood gives the conditional channel moments
```

**理由**：与前一句 Dividing 对应，明确重新组合是 Gaussian site 与输入 likelihood 相乘，指出下一式给出条件矩；未加回被删除的恢复一致性说明。

- 本文现有 C-STMP 稿件；III–V 现有公式和 Algorithm 1。支持层次：本文操作／定义／公式衔接。
  本句的具体估计器、Gaussian site、接受条件、参数、初始化和数值处理是本文既有内容。未在已读五篇母本中确认同一技术句，不假称来自某篇原句。
  核对锚点：current manuscript equations and algorithm conditions
- Ding et al., ding2026.pdf；III-B, Step 3–4, (14)–(18)；PDF p.3,4。支持层次：同任务完整搭配／原段关系。
  同为先给活动/稀疏概率和条件矩再形成整体后验矩；本文保留完整先验及空间协方差，不带入 Ding 逐元素 spike-and-slab、层间阻尼或能量检测。
  核对锚点：the posterior mean and variance are calculated as

## ch5_a-P06-S01 — 修改

**原文**

```latex
We accept the update within the training variance range when
$0<\tau<v$; otherwise, the previous site is retained.
```

**改后**

```latex
We update the site when the input variance lies within the training range and $0<\tau<v$; otherwise, the previous site is retained.
```

**理由**：明确训练范围约束的对象是输入方差，两个接受条件并列；保留旧 site 的分支不变。

- 本文现有 C-STMP 稿件；III–V 现有公式和 Algorithm 1。支持层次：本文操作／定义／公式衔接。
  本句的具体估计器、Gaussian site、接受条件、参数、初始化和数值处理是本文既有内容。未在已读五篇母本中确认同一技术句，不假称来自某篇原句。
  核对锚点：current manuscript equations and algorithm conditions

## ch5_a-P07-S01 — 保留

**原文**

```latex
Combining $p_k$ with $(\mu_k,t_k)$ gives the joint estimate in
\eqref{eq:mixture} and covariance in \eqref{eq:joint-spatial-covariance}.
```

**改后**

```latex
Combining $p_k$ with $(\mu_k,t_k)$ gives the joint estimate in
\eqref{eq:mixture} and covariance in \eqref{eq:joint-spatial-covariance}.
```

**理由**：直接用此前求得的概率和条件矩连到第三章联合估计及空间协方差，原句已经完成该任务。

- Ding et al., ding2026.pdf；III-B, Step 3–4, (14)–(18)；PDF p.3,4。支持层次：同任务完整搭配／原段关系。
  同为先给活动/稀疏概率和条件矩再形成整体后验矩；本文保留完整先验及空间协方差，不带入 Ding 逐元素 spike-and-slab、层间阻尼或能量检测。
  核对锚点：the posterior mean and variance are calculated as
- 本文现有 C-STMP 稿件；III–V 现有公式和 Algorithm 1。支持层次：本文操作／定义／公式衔接。
  本句的具体估计器、Gaussian site、接受条件、参数、初始化和数值处理是本文既有内容。未在已读五篇母本中确认同一技术句，不假称来自某篇原句。
  核对锚点：current manuscript equations and algorithm conditions

## ch5_a-P07-S02 — 修改

**原文**

```latex
The Gaussian extrinsic message in \eqref{eq:nonlinear-extrinsic} is then
passed to MFLE.
```

**改后**

```latex
The Gaussian extrinsic message in \eqref{eq:nonlinear-extrinsic} is then passed back to MFLE.
```

**理由**：补 back 明确 MFLE→GPJD→MFLE 的闭环，其他内容不变。

- Wei and Yuan, arXiv:2610.17785v1；III-C, (12) 后至 (13) 前；PDF p.3。支持层次：同任务信息流关系。
  参照外信息再次成为线性部分输入的闭环关系；本文迭代而非可训练展开层，不照搬残差方差。锚点省略公式变量。
  核对锚点：to generate the prior ... of the next layer
- Shen et al., shen2025.pdf；III 开篇；PDF p.5。支持层次：同任务信息流搭配。
  仅参照模块之间迭代交换信息的表达；本文是已确定的两部分结构，不移入 Shen 的三模块或在线相位 EM。
  核对锚点：the soft information is exchanged iteratively among them

## ch5_a-P07-S03 — 保留

**原文**

```latex
Algorithm~1 summarizes the iteration.
```

**改后**

```latex
Algorithm~1 summarizes the iteration.
```

**理由**：算法汇总句简洁，无需替换为相近套话。

- Shen et al., shen2025.pdf；III-C 末段及 Algorithm 1；PDF p.9,10。支持层次：算法汇总句式／原段关系。
  已读完整相邻说明和 Algorithm 1；仅为以伪代码汇总已推导规则的写法参照，本文初始化、停止和所有计算公式归本稿。
  核对锚点：as summarized in Algorithm 1
- Huang et al., huang2026.pdf；III-B 及 Algorithm 1；PDF p.3,4。支持层次：常规算法汇总句式。
  同样将训练模型用于推断后集中列出初始化、循环和输出；本文不使用 Huang 的 Langevin 采样、退火层级或其收敛阈值。
  核对锚点：The score-based inference procedure is summarized in Algorithm 1.
- Cai et al., arXiv:2506.00581v2；V-B 末及 Algorithm 2；PDF p.10。支持层次：算法汇总与执行顺序参照。
  读完 Algorithm 2 的线性更新、去噪、联合矩、反馈、停止与判决顺序；本文 Algorithm 1 整块保持，特有条件不能归属蔡文。
  核对锚点：Algorithm 2 provides the pseudo-code of STMP-JADCE

## ch5_a-P07-S04 — 保留

**原文**

```latex
In normalized coordinates,
we initialize $\mathbf X^{{\rm pri},(0)}=\mathbf0$,
$\gamma^{(0)}=\rho\widehat P_H$, $E_k=0$, $c_k=1$, and
$\kappa^{(1)}=1$, where $\widehat P_H$ is the training average
of $\norm{H}_F^2/D$.
```

**改后**

```latex
In normalized coordinates,
we initialize $\mathbf X^{{\rm pri},(0)}=\mathbf0$,
$\gamma^{(0)}=\rho\widehat P_H$, $E_k=0$, $c_k=1$, and
$\kappa^{(1)}=1$, where $\widehat P_H$ is the training average
of $\norm{H}_F^2/D$.
```

**理由**：全部初始化量及训练平均功率定义是执行算法所需的本文内容，保留每项数值和尺度条件。

- 本文现有 C-STMP 稿件；III–V 现有公式和 Algorithm 1。支持层次：本文操作／定义／公式衔接。
  本句的具体估计器、Gaussian site、接受条件、参数、初始化和数值处理是本文既有内容。未在已读五篇母本中确认同一技术句，不假称来自某篇原句。
  核对锚点：current manuscript equations and algorithm conditions

## ch5_a-P07-S05 — 保留

**原文**

```latex
The parameter estimates, normalization,
and message damping are specified below.
```

**改后**

```latex
The parameter estimates, normalization,
and message damping are specified below.
```

**理由**：自然引向下一节的参数估计和数值处理，保留。

- Cai et al., arXiv:2506.00581v2；V-A, (55)–(56), Fig. 3 前后；PDF p.9。支持层次：原段论证关系。
  保留学习结果代入通用框架后得到具体算法的组织方式；本文模块名称和均值导数、活动分类器为既有方案，不把这些操作登记为蔡文原法。
  核对锚点：integration of the two score networks into the TMP framework
- 本文现有 C-STMP 稿件；III–V 现有公式和 Algorithm 1。支持层次：本文操作／定义／公式衔接。
  本句的具体估计器、Gaussian site、接受条件、参数、初始化和数值处理是本文既有内容。未在已读五篇母本中确认同一技术句，不假称来自某篇原句。
  核对锚点：current manuscript equations and algorithm conditions

## ch5_bc-P01-S01 — 修改

**原文**

```latex
The preceding posterior calculations use a fixed observation matrix $\widehat{\mathbf A}$ and physical noise variance $\widehat\sigma^2$.
```

**改后**

```latex
Before message passing, we determine the observation matrix $\widehat{\mathbf A}$ and physical noise variance $\widehat\sigma^2$ used in the posterior calculations.
```

**理由**：用先确定参数的叙述引出估计方法，固定使用条件仍由本段末句明确，消除首尾重复。

- Shen et al. (2025)；本文既有前端；Shen PDF p.7，§III-B首段；本文 eq:effective-pilot 与 app:frontend。支持层次：原段关系：先交代给定参数，再进行后验消息计算；本文条件。
  Shen随后用EM更新参数，本稿前端输出在消息传递期间固定。只取交代已知量的叙述关系，不移入Shen的迭代EM更新。
  核对锚点：the noise variance, and the parameters
- 本文既有参数估计流程；V-B与Appendix app:frontend。支持层次：本文定义和交叉引用。
  观测矩阵、物理噪声估计的构成与固定使用方式保持；不是另引文献的同一接收机。

## ch5_bc-P01-S02 — 保留

**原文**

```latex
The matrix is formed from the available inter-frame phases through \eqref{eq:effective-pilot}; when the phases are unknown, they are estimated by variable projection \cite{oleary2013}.
```

**改后**

```latex
The matrix is formed from the available inter-frame phases through \eqref{eq:effective-pilot}; when the phases are unknown, they are estimated by variable projection \cite{oleary2013}.
```

**理由**：相位可用/未知两种情况、variable projection出处和矩阵构造关系已经清楚，保留。

- O’Leary–Rust (2013)；PDF pp.2、4，§1式(2)–(3)、§2式(5)–(6)。支持层次：技术来源与既有术语。
  给定非线性参数后以最小二乘消去线性增益；本稿逐设备相位估计与前端调用安排属本文适配，引用保持。
  核对锚点：separable least squares problem
- 本文既有参数估计流程；V-B与Appendix app:frontend。支持层次：本文定义和交叉引用。
  观测矩阵、物理噪声估计的构成与固定使用方式保持；不是另引文献的同一接收机。

## ch5_bc-P01-S03 — 修改

**原文**

```latex
For the noise variance, the spatial sample covariance separates the signal subspace from the trailing eigenvalues under a lower-rank spatial signal plus white noise.
```

**改后**

```latex
For a lower-rank spatial signal plus white noise, the noise variance is estimated from the trailing eigenvalues of the spatial sample covariance.
```

**理由**：把低秩加白噪声条件放在句首，直接说明尾部特征值的用途，下一句再说明如何选择其范围；不增加理想分离保证。

- Nadakuditi–Edelman (2008)；PDF pp.2–3／印刷pp.2626–2627，§II-A，式(5)–(7)及随后算术均值定义。支持层次：技术陈述及标准术语。
  沿用文中回顾的Wax–Kailath MDL，以空间秩和尾部特征值拟合白噪声；不将信号秩写成设备数，不改成该文后续新估计器。低秩信号加白噪声条件保留。
  核对锚点：sample covariance matrix (SCM)

## ch5_bc-P01-S04 — 修改

**原文**

```latex
The minimum description length (MDL) criterion selects the signal rank, and the mean of the remaining eigenvalues gives $\widehat\sigma^2$ \cite{nadakuditi2008}.
```

**改后**

```latex
After the minimum description length (MDL) criterion selects the signal rank, the mean of the remaining eigenvalues gives $\widehat\sigma^2$ \cite{nadakuditi2008}.
```

**理由**：将秩选择与尾部平均的先后依赖写清，公式对象、MDL全称和原引用保持。

- Nadakuditi–Edelman (2008)；PDF pp.2–3／印刷pp.2626–2627，§II-A，式(5)–(7)及随后算术均值定义。支持层次：技术陈述及标准术语。
  沿用文中回顾的Wax–Kailath MDL，以空间秩和尾部特征值拟合白噪声；不将信号秩写成设备数，不改成该文后续新估计器。低秩信号加白噪声条件保留。
  核对锚点：sample covariance matrix (SCM)

## ch5_bc-P01-S05 — 保留

**原文**

```latex
Appendix~\ref{app:frontend} gives both estimators.
```

**改后**

```latex
Appendix~\ref{app:frontend} gives both estimators.
```

**理由**：已有附录引用准确指向两项估计器，无需为了换词而修改。

- 本文既有参数估计流程；V-B与Appendix app:frontend。支持层次：本文定义和交叉引用。
  观测矩阵、物理噪声估计的构成与固定使用方式保持；不是另引文献的同一接收机。

## ch5_bc-P01-S06 — 保留

**原文**

```latex
Their outputs remain fixed throughout message passing.
```

**改后**

```latex
Their outputs remain fixed throughout message passing.
```

**理由**：这是固定前端与迭代内输入方差更新的必要区别，保留。

- 本文既有参数估计流程；V-B与Appendix app:frontend。支持层次：本文定义和交叉引用。
  观测矩阵、物理噪声估计的构成与固定使用方式保持；不是另引文献的同一接收机。
- Shen et al. (2025)；本文既有前端；Shen PDF p.7，§III-B首段；本文 eq:effective-pilot 与 app:frontend。支持层次：原段关系：先交代给定参数，再进行后验消息计算；本文条件。
  Shen随后用EM更新参数，本稿前端输出在消息传递期间固定。只取交代已知量的叙述关系，不移入Shen的迭代EM更新。
  核对锚点：the noise variance, and the parameters

## ch5_bc-P02-S01 — 保留

**原文**

```latex
The input variance $v$ in the local model \eqref{eq:pseudo-awgn} describes the uncertainty after linear estimation.
```

**改后**

```latex
The input variance $v$ in the local model \eqref{eq:pseudo-awgn} describes the uncertainty after linear estimation.
```

**理由**：局部方差的物理对象和线性估计后的用途已经明确，保留。

- 本文既有方差目标和尺度更新；eq:query-variance-target；eq:query-variance-update；eq:mixture。支持层次：本文推导和迭代调度。
  固定近似后验、KD归一化、通道与活动不确定性、kappa乘damped MFLE variance、下一轮才应用更新均保留。

## ch5_bc-P02-S02 — 保留

**原文**

```latex
Its update follows from the expected Gaussian negative log likelihood with the current approximate posterior \eqref{eq:mixture} held fixed \cite[Sec.~III-A]{vila2013}.
```

**改后**

```latex
Its update follows from the expected Gaussian negative log likelihood with the current approximate posterior \eqref{eq:mixture} held fixed \cite[Sec.~III-A]{vila2013}.
```

**理由**：固定当前近似后验是所述最小化的关键条件；句意与Vila技术关系一致，保留。

- Vila–Schniter (2013)；PDF p.4／印刷p.4661，§III-A，式(22)–(27)。支持层次：技术关系：固定当前后验的期望似然→方差更新。
  本稿在局部模型中更新输入方差v，不把它改称物理噪声估计或全局EM；本文复杂数据、活动混合后验、KD维度及后验方差均保留。缓存公式抽取缺符号，具体数学逐项保持本文原式，并依既有术语账本记录定位。
  核对锚点：EM Update of the Gaussian Noise Variance
- Shen et al. (2025)；PDF p.9，§III-C，式(47)–(59)，特别式(56)。支持层次：原段推进关系：近似后验→参数目标→更新；残差和后验方差的相关构成。
  Shen式(56)更新物理观测噪声，本稿更新局部去噪输入方差；仅参考推导顺序与残差加不确定性的解释，不移植参数或算法。
  核对锚点：Based on the previous approximated posterior distributions

## ch5_bc-P02-S03 — 保留

**原文**

```latex
For a candidate variance $\widetilde v$, the terms depending on it are $KD\log\widetilde v+ \sum_k\E_{\widetilde q_k}[\norm{R_k-X_k}_F^2]/\widetilde v$.
```

**改后**

```latex
For a candidate variance $\widetilde v$, the terms depending on it are $KD\log\widetilde v+ \sum_k\E_{\widetilde q_k}[\norm{R_k-X_k}_F^2]/\widetilde v$.
```

**理由**：候选方差与目标的对应项完整且无多余修饰，保留原行内公式。

- Vila–Schniter (2013)；PDF p.4／印刷p.4661，§III-A，式(22)–(27)。支持层次：技术关系：固定当前后验的期望似然→方差更新。
  本稿在局部模型中更新输入方差v，不把它改称物理噪声估计或全局EM；本文复杂数据、活动混合后验、KD维度及后验方差均保留。缓存公式抽取缺符号，具体数学逐项保持本文原式，并依既有术语账本记录定位。
  核对锚点：EM Update of the Gaussian Noise Variance
- 本文既有方差目标和尺度更新；eq:query-variance-target；eq:query-variance-update；eq:mixture。支持层次：本文推导和迭代调度。
  固定近似后验、KD归一化、通道与活动不确定性、kappa乘damped MFLE variance、下一轮才应用更新均保留。

## ch5_bc-P02-S04 — 保留

**原文**

```latex
Minimizing this expression and expanding the expected squared error gives
```

**改后**

```latex
Minimizing this expression and expanding the expected squared error gives
```

**理由**：已经按最小化→展开平方误差引出下式，直接推进推导，不作同义替换。

- Vila–Schniter (2013)；PDF p.4／印刷p.4661，§III-A，式(22)–(27)。支持层次：技术关系：固定当前后验的期望似然→方差更新。
  本稿在局部模型中更新输入方差v，不把它改称物理噪声估计或全局EM；本文复杂数据、活动混合后验、KD维度及后验方差均保留。缓存公式抽取缺符号，具体数学逐项保持本文原式，并依既有术语账本记录定位。
  核对锚点：EM Update of the Gaussian Noise Variance
- Shen et al. (2025)；PDF p.9，§III-C，式(47)–(59)，特别式(56)。支持层次：原段推进关系：近似后验→参数目标→更新；残差和后验方差的相关构成。
  Shen式(56)更新物理观测噪声，本稿更新局部去噪输入方差；仅参考推导顺序与残差加不确定性的解释，不移植参数或算法。
  核对锚点：Based on the previous approximated posterior distributions
- 本文既有方差目标和尺度更新；eq:query-variance-target；eq:query-variance-update；eq:mixture。支持层次：本文推导和迭代调度。
  固定近似后验、KD归一化、通道与活动不确定性、kappa乘damped MFLE variance、下一轮才应用更新均保留。

## ch5_bc-P03-S01 — 修改

**原文**

```latex
The residual measures the error of the posterior mean, while $\overline t_X$ accounts for the remaining channel and activity uncertainty.
```

**改后**

```latex
The first term is the average squared residual of the posterior mean, while $\overline t_X$ accounts for the remaining channel and activity uncertainty.
```

**理由**：将误称为“error of the posterior mean”的含糊表述具体化为平均平方残差，避免读成真实估计误差；另一项不确定性含义保持。

- Shen et al. (2025)；PDF p.9，§III-C，式(47)–(59)，特别式(56)。支持层次：原段推进关系：近似后验→参数目标→更新；残差和后验方差的相关构成。
  Shen式(56)更新物理观测噪声，本稿更新局部去噪输入方差；仅参考推导顺序与残差加不确定性的解释，不移植参数或算法。
  核对锚点：Based on the previous approximated posterior distributions
- 本文既有方差目标和尺度更新；eq:query-variance-target；eq:query-variance-update；eq:mixture。支持层次：本文推导和迭代调度。
  固定近似后验、KD归一化、通道与活动不确定性、kappa乘damped MFLE variance、下一轮才应用更新均保留。

## ch5_bc-P03-S02 — 修改

**原文**

```latex
Let $\bar v^{(i)}$ denote the damped MFLE variance and use $v^{(i)}=\kappa^{(i)}\bar v^{(i)}$ during iteration $i$.
```

**改后**

```latex
At iteration $i$, we use $v^{(i)}=\kappa^{(i)}\bar v^{(i)}$, where $\bar v^{(i)}$ denotes the damped MFLE variance.
```

**理由**：将当前迭代使用的量放在主句、辅助定义放在where从句，保持原有尺度关系。

- 本文既有方差目标和尺度更新；eq:query-variance-target；eq:query-variance-update；eq:mixture。支持层次：本文推导和迭代调度。
  固定近似后验、KD归一化、通道与活动不确定性、kappa乘damped MFLE variance、下一轮才应用更新均保留。

## ch5_bc-P03-S03 — 保留

**原文**

```latex
With new-message weight $\eta\in(0,1]$, the next scale is
```

**改后**

```latex
With new-message weight $\eta\in(0,1]$, the next scale is
```

**理由**：新消息权重的取值范围及“next scale”准确引出更新式，保留。

- 本文既有方差目标和尺度更新；eq:query-variance-target；eq:query-variance-update；eq:mixture。支持层次：本文推导和迭代调度。
  固定近似后验、KD归一化、通道与活动不确定性、kappa乘damped MFLE variance、下一轮才应用更新均保留。
- Cai et al. (2026), arXiv v2；PDF pp.9–10，§V-B1，式(57)–(58)及其后对另一模块的说明。支持层次：技术关系及短表达：均值与方差的迭代阻尼。
  本文保留已有eta、i>=2、当前已阻尼消息与新外信息的组合及两方向阻尼；不更改Cai/本文之间的具体历史索引差别。
  核对锚点：a linear combination of the current and previous updates

## ch5_bc-P04-S01 — 保留

**原文**

```latex
The current $v^{(i)}$ is used for both joint denoising and the extrinsic update; the updated scale enters the following iteration.
```

**改后**

```latex
The current $v^{(i)}$ is used for both joint denoising and the extrinsic update; the updated scale enters the following iteration.
```

**理由**：这句明确同轮使用当前v、下一轮应用更新尺度，属于必要调度，不是防御性说明。

- 本文既有方差目标和尺度更新；eq:query-variance-target；eq:query-variance-update；eq:mixture。支持层次：本文推导和迭代调度。
  固定近似后验、KD归一化、通道与活动不确定性、kappa乘damped MFLE variance、下一轮才应用更新均保留。

## ch5_bc-P05-S01 — 保留

**原文**

```latex
The channel prior and online observations use the same fixed normalization.
```

**改后**

```latex
The channel prior and online observations use the same fixed normalization.
```

**理由**：固定归一化是本稿必要训练/推断条件，保留。

- Cai et al. (2026), arXiv v2；PDF p.10，§V-B2，式(59)–(65)。支持层次：论述任务：说明训练和推断的尺度关系；本文具体归一化。
  Cai按样本功率归一化并在线估计输入尺度；本稿使用训练集系数的固定RMS。不移植Cai的样本依赖公式，不声称本稿与其归一化一致。
  核对锚点：Channel Power Normalization
- 本文既有参数估计流程；V-B与Appendix app:frontend。支持层次：本文定义和交叉引用。
  观测矩阵、物理噪声估计的构成与固定使用方式保持；不是另引文献的同一接收机。

## ch5_bc-P05-S02 — 修改

**原文**

```latex
If $s$ is the root mean square of the training-channel coefficients, we divide $(H_k,X_k,\mathbf Y,\mathbf W)$ by $s$ and the physical noise variance by $s^2$, retaining the same symbols for normalized quantities.
```

**改后**

```latex
Let $s$ denote the root mean square of the training-channel coefficients. We divide $(H_k,X_k,\mathbf Y,\mathbf W)$ by $s$ and the physical noise variance by $s^2$, retaining the same symbols for normalized quantities.
```

**理由**：将条件式If改为实际使用的尺度定义，再说明信号和方差的缩放，原定义和归一化量均不变。

- Cai et al. (2026), arXiv v2；PDF p.10，§V-B2，式(59)–(65)。支持层次：论述任务：说明训练和推断的尺度关系；本文具体归一化。
  Cai按样本功率归一化并在线估计输入尺度；本稿使用训练集系数的固定RMS。不移植Cai的样本依赖公式，不声称本稿与其归一化一致。
  核对锚点：Channel Power Normalization
- 本文既有参数估计流程；V-B与Appendix app:frontend。支持层次：本文定义和交叉引用。
  观测矩阵、物理噪声估计的构成与固定使用方式保持；不是另引文献的同一接收机。

## ch5_bc-P05-S03 — 保留

**原文**

```latex
The pilot matrix is unchanged.
```

**改后**

```latex
The pilot matrix is unchanged.
```

**理由**：保留归一化不作用于导频矩阵这一模型条件。

- 本文既有参数估计流程；V-B与Appendix app:frontend。支持层次：本文定义和交叉引用。
  观测矩阵、物理噪声估计的构成与固定使用方式保持；不是另引文献的同一接收机。

## ch5_bc-P05-S04 — 修改

**原文**

```latex
To moderate changes between successive Gaussian messages, we apply damping \cite[Sec.~V-B1]{cai2026} to the MFLE output for $i\geq2$:
```

**改后**

```latex
The MFLE output is damped by combining the current and previous messages \cite[Sec.~V-B1]{cai2026} for $i\geq2$:
```

**理由**：采用Cai已核实的当前/前一消息线性组合关系，直接引出本文阻尼式，不加入稳定性保证。

- Cai et al. (2026), arXiv v2；PDF pp.9–10，§V-B1，式(57)–(58)及其后对另一模块的说明。支持层次：技术关系及短表达：均值与方差的迭代阻尼。
  本文保留已有eta、i>=2、当前已阻尼消息与新外信息的组合及两方向阻尼；不更改Cai/本文之间的具体历史索引差别。
  核对锚点：a linear combination of the current and previous updates

## ch5_bc-P06-S01 — 保留

**原文**

```latex
For numerical evaluation of \eqref{eq:nonlinear-extrinsic}, we replace $b=\overline t_X/v$ by $b=\clip(\overline t_X/v,\varepsilon,1-\varepsilon)$, where $0<\varepsilon<1/2$.
```

**改后**

```latex
For numerical evaluation of \eqref{eq:nonlinear-extrinsic}, we replace $b=\overline t_X/v$ by $b=\clip(\overline t_X/v,\varepsilon,1-\varepsilon)$, where $0<\varepsilon<1/2$.
```

**理由**：只陈述已有比值裁剪和epsilon范围，无额外正值性辩解，保留原定义。

- 本文既有数值实现与Algorithm 1；eq:nonlinear-extrinsic；eq:input-damping；eq:output-damping；eq:gaussian-evidence；sec:simulation-settings。支持层次：本文实现条件和交叉引用。
  训练方差范围之外保留Gaussian sites；裁剪区间和首轮不阻尼保持。仅陈述操作，不补回正值性或合法性解释。

## ch5_bc-P06-S02 — 保留

**原文**

```latex
The feedback is then damped with the same weight:
```

**改后**

```latex
The feedback is then damped with the same weight:
```

**理由**：简明承接输入侧阻尼并明确反馈使用同一权重，保留。

- Cai et al. (2026), arXiv v2；PDF pp.9–10，§V-B1，式(57)–(58)及其后对另一模块的说明。支持层次：技术关系及短表达：均值与方差的迭代阻尼。
  本文保留已有eta、i>=2、当前已阻尼消息与新外信息的组合及两方向阻尼；不更改Cai/本文之间的具体历史索引差别。
  核对锚点：a linear combination of the current and previous updates
- 本文既有数值实现与Algorithm 1；eq:nonlinear-extrinsic；eq:input-damping；eq:output-damping；eq:gaussian-evidence；sec:simulation-settings。支持层次：本文实现条件和交叉引用。
  训练方差范围之外保留Gaussian sites；裁剪区间和首轮不阻尼保持。仅陈述操作，不补回正值性或合法性解释。

## ch5_bc-P07-S01 — 保留

**原文**

```latex
The first input and feedback messages are used without damping.
```

**改后**

```latex
The first input and feedback messages are used without damping.
```

**理由**：首轮不阻尼是实际算法条件，保留。

- 本文既有数值实现与Algorithm 1；eq:nonlinear-extrinsic；eq:input-damping；eq:output-damping；eq:gaussian-evidence；sec:simulation-settings。支持层次：本文实现条件和交叉引用。
  训练方差范围之外保留Gaussian sites；裁剪区间和首轮不阻尼保持。仅陈述操作，不补回正值性或合法性解释。

## ch5_bc-P07-S02 — 保留

**原文**

```latex
Outside the training variance range, the retained Gaussian sites provide the activity density ratio specified in \eqref{eq:gaussian-evidence}.
```

**改后**

```latex
Outside the training variance range, the retained Gaussian sites provide the activity density ratio specified in \eqref{eq:gaussian-evidence}.
```

**理由**：训练方差范围外的Gaussian sites和活动比值来源是算法所需分支，保留。

- 本文既有数值实现与Algorithm 1；eq:nonlinear-extrinsic；eq:input-damping；eq:output-damping；eq:gaussian-evidence；sec:simulation-settings。支持层次：本文实现条件和交叉引用。
  训练方差范围之外保留Gaussian sites；裁剪区间和首轮不阻尼保持。仅陈述操作，不补回正值性或合法性解释。

## ch5_bc-P07-S03 — 修改

**原文**

```latex
Iteration stops when the estimates and accepted site updates have stabilized, or at the maximum iteration count.
```

**改后**

```latex
Iterations continue until the estimates and accepted site updates have stabilized or the maximum iteration count is reached.
```

**理由**：用until统一两个终止分支，保留accepted site updates及迭代上限，不主张必然收敛。

- Cai et al. (2026), arXiv v2；Huang et al. (2026)；Cai PDF p.10 Algorithm 2终止行；Huang PDF p.4 Algorithm 1 while条件。支持层次：原段/伪代码任务：终止规则及迭代上限；非相同判据。
  本文保持估计与accepted site updates稳定或达到最大次数的既有判据；不移入Huang的Langevin相对变化阈值，不声称收敛保证。
  核对锚点：the stopping criterion is met
- 本文既有数值实现与Algorithm 1；eq:nonlinear-extrinsic；eq:input-damping；eq:output-damping；eq:gaussian-evidence；sec:simulation-settings。支持层次：本文实现条件和交叉引用。
  训练方差范围之外保留Gaussian sites；裁剪区间和首轮不阻尼保持。仅陈述操作，不补回正值性或合法性解释。

## ch5_bc-P07-S04 — 保留

**原文**

```latex
The corresponding checks and numerical settings are given in Section~\ref{sec:simulation-settings}.
```

**改后**

```latex
The corresponding checks and numerical settings are given in Section~\ref{sec:simulation-settings}.
```

**理由**：详细判据和数值设置已有唯一位置，保留。

- 本文既有数值实现与Algorithm 1；eq:nonlinear-extrinsic；eq:input-damping；eq:output-damping；eq:gaussian-evidence；sec:simulation-settings。支持层次：本文实现条件和交叉引用。
  训练方差范围之外保留Gaussian sites；裁剪区间和首轮不阻尼保持。仅陈述操作，不补回正值性或合法性解释。

## ch5_bc-P08-S01 — 保留

**原文**

```latex
The observation matrix is fixed within a transmission block, so its thin singular value decomposition (SVD), $\widehat{\mathbf A}=\mathbf U\diag(s_i)\mathbf V^{\mathsf H}$, can be reused across iterations.
```

**改后**

```latex
The observation matrix is fixed within a transmission block, so its thin singular value decomposition (SVD), $\widehat{\mathbf A}=\mathbf U\diag(s_i)\mathbf V^{\mathsf H}$, can be reused across iterations.
```

**理由**：固定矩阵→thin SVD复用已形成准确因果链，保留全部尺寸和分解式。

- 本文既有矩阵模型与SVD展开；eq:linear-variance至eq:linear-extrinsic；eq:linear-fraction。支持层次：本文代数变换及复杂度计算。
  块内固定观测矩阵、thin SVD、完整Gram矩阵及本文尺寸保留；不套用Cai部分正交/FFT或Wei行正交简化。

## ch5_bc-P08-S02 — 修改

**原文**

```latex
In particular, \eqref{eq:linear-variance}--\eqref{eq:linear-extrinsic} become
```

**改后**

```latex
With this decomposition, the scalar updates in \eqref{eq:linear-variance}--\eqref{eq:linear-extrinsic} can be written as
```

**理由**：明确下式是SVD下的标量更新写法，避免笼统become将整套矩阵公式都等同于三个标量式。

- 本文既有矩阵模型与SVD展开；eq:linear-variance至eq:linear-extrinsic；eq:linear-fraction。支持层次：本文代数变换及复杂度计算。
  块内固定观测矩阵、thin SVD、完整Gram矩阵及本文尺寸保留；不套用Cai部分正交/FFT或Wei行正交简化。

## ch5_bc-P09-S01 — 保留

**原文**

```latex
Here $\mathbf R_{\rm L}=\mathbf X^{\rm pri} +(\mathbf X_{\rm L}-\mathbf X^{\rm pri})/f_{\rm L}$.
```

**改后**

```latex
Here $\mathbf R_{\rm L}=\mathbf X^{\rm pri} +(\mathbf X_{\rm L}-\mathbf X^{\rm pri})/f_{\rm L}$.
```

**理由**：外信息均值由f_L表示的等价式正确，保持。

- 本文既有矩阵模型与SVD展开；eq:linear-variance至eq:linear-extrinsic；eq:linear-fraction。支持层次：本文代数变换及复杂度计算。
  块内固定观测矩阵、thin SVD、完整Gram矩阵及本文尺寸保留；不套用Cai部分正交/FFT或Wei行正交简化。

## ch5_bc-P09-S02 — 修改

**原文**

```latex
For $Q\leq KN$, the SVD costs $O(KNQ^2)$ once per block.
```

**改后**

```latex
For $Q\leq KN$, computing the SVD requires $O(KNQ^2)$ operations once per transmission block.
```

**理由**：使用计算对象→成本→频率的完整句式，保留Q条件和一次性成本。

- Shen et al. (2025)；PDF p.10，§III-C末复杂度段。支持层次：原段关系：逐项操作成本→合计；常规成本陈述。
  只参考按矩阵乘法、模块操作、参数估计分解成本的顺序；本文SVD/空间协方差/前端成本均独立保留，不移植其复杂度或稀疏可忽略结论。
  核对锚点：For each iteration
- 本文既有矩阵模型与SVD展开；eq:linear-variance至eq:linear-extrinsic；eq:linear-fraction。支持层次：本文代数变换及复杂度计算。
  块内固定观测矩阵、thin SVD、完整Gram矩阵及本文尺寸保留；不套用Cai部分正交/FFT或Wei行正交简化。

## ch5_bc-P09-S03 — 修改

**原文**

```latex
Noise estimation costs $O(QNM^2+M^3)$; let $C_{\rm phase}$ denote the phase-search, refinement, and gain-refitting cost in Appendix~\ref{app:frontend}.
```

**改后**

```latex
Noise estimation requires $O(QNM^2+M^3)$ operations. The phase-search, refinement, and gain-refitting cost in Appendix~\ref{app:frontend} is denoted by $C_{\rm phase}$.
```

**理由**：将噪声成本和相位成本定义拆成两句，使两个前端代价的对象分别清楚，数值量级不变。

- Shen et al. (2025)；PDF p.10，§III-C末复杂度段。支持层次：原段关系：逐项操作成本→合计；常规成本陈述。
  只参考按矩阵乘法、模块操作、参数估计分解成本的顺序；本文SVD/空间协方差/前端成本均独立保留，不移植其复杂度或稀疏可忽略结论。
  核对锚点：For each iteration
- 本文既有参数估计流程；V-B与Appendix app:frontend。支持层次：本文定义和交叉引用。
  观测矩阵、物理噪声估计的构成与固定使用方式保持；不是另引文献的同一接收机。

## ch5_bc-P09-S04 — 保留

**原文**

```latex
Per iteration, MFLE transformations cost $O(QKMN^2)$, spatial covariance operations cost $O(KM^2N^2)$, and matrix factorizations cost $O(M^3)$.
```

**改后**

```latex
Per iteration, MFLE transformations cost $O(QKMN^2)$, spatial covariance operations cost $O(KM^2N^2)$, and matrix factorizations cost $O(M^3)$.
```

**理由**：三个并列运算与量级一一对应、已较简洁，保留，不套用别篇模块计数。

- Shen et al. (2025)；PDF p.10，§III-C末复杂度段。支持层次：原段关系：逐项操作成本→合计；常规成本陈述。
  只参考按矩阵乘法、模块操作、参数估计分解成本的顺序；本文SVD/空间协方差/前端成本均独立保留，不移植其复杂度或稀疏可忽略结论。
  核对锚点：For each iteration
- Ding et al. (2026)；PDF p.5，§III-D，式(29)前后。支持层次：参考比较：运算分解及网络成本；未直接采用FLOP计数。
  Ding给具体层级FLOPs，本文只保留原有大O计算量及网络成本符号，不混淆计量单位、不移植其GNN结构独立性结论。
  核对锚点：the real-valued floating-point operations
- 本文既有矩阵模型与SVD展开；eq:linear-variance至eq:linear-extrinsic；eq:linear-fraction。支持层次：本文代数变换及复杂度计算。
  块内固定观测矩阵、thin SVD、完整Gram矩阵及本文尺寸保留；不套用Cai部分正交/FFT或Wei行正交简化。

## ch5_bc-P09-S05 — 修改

**原文**

```latex
If $C_\theta,C_\phi$ denote the per-device denoiser and classifier costs, GPJD uses $1+2L_z$ denoiser evaluations and one classifier evaluation within the training interval.
```

**改后**

```latex
Let $C_\theta,C_\phi$ denote the per-device denoiser and classifier costs. Within the training interval, GPJD requires $1+2L_z$ denoiser evaluations and one classifier evaluation.
```

**理由**：先定义每设备成本，再给GPJD网络评估次数，去掉不必要的假设式If；保留训练区间限制和所有调用数。

- Cai et al. (2026), arXiv v2；PDF p.11，§V-C复杂度完整段。支持层次：完整搭配与原段关系：矩阵运算、网络前向次数→单次迭代复杂度。
  本文网络为denoiser和classifier，含1+2L_z次denoiser调用；C_theta/C_phi定义、逐设备K倍及矩阵量级来自本文，不能登记为Cai原公式。
  核对锚点：the computational costs of a forward pass
- Huang et al. (2026)；PDF p.4，§IV Table II及其后网络评估成本说明。支持层次：原段关系：网络单次成本×评估次数。
  Huang的K为采样网络调用数，本文K为设备数；仅参考计次叙述，本文明确1+2L_z次与每设备成本，不移植其符号或采样算法。
  核对锚点：with K network evaluations
- 本文既有方差目标和尺度更新；eq:query-variance-target；eq:query-variance-update；eq:mixture。支持层次：本文推导和迭代调度。
  固定近似后验、KD归一化、通道与活动不确定性、kappa乘damped MFLE variance、下一轮才应用更新均保留。

## ch5_bc-P09-S06 — 修改

**原文**

```latex
Hence,
```

**改后**

```latex
The resulting per-iteration complexity is
```

**理由**：直接引出合计成本，与前文分项同一对象，未新增结论。

- Cai et al. (2026), arXiv v2；PDF p.11，§V-C复杂度完整段。支持层次：完整搭配与原段关系：矩阵运算、网络前向次数→单次迭代复杂度。
  本文网络为denoiser和classifier，含1+2L_z次denoiser调用；C_theta/C_phi定义、逐设备K倍及矩阵量级来自本文，不能登记为Cai原公式。
  核对锚点：the computational costs of a forward pass
- Shen et al. (2025)；PDF p.10，§III-C末复杂度段。支持层次：原段关系：逐项操作成本→合计；常规成本陈述。
  只参考按矩阵乘法、模块操作、参数估计分解成本的顺序；本文SVD/空间协方差/前端成本均独立保留，不移植其复杂度或稀疏可忽略结论。
  核对锚点：For each iteration

## ch5_bc-P10-S01 — 保留

**原文**

```latex
For $I$ iterations, the total online complexity is bounded by
```

**改后**

```latex
For $I$ iterations, the total online complexity is bounded by
```

**理由**：总复杂度是I次迭代的上界，条件及结论强度均准确，保留。

- Cai et al. (2026), arXiv v2；PDF p.11，§V-C复杂度完整段。支持层次：完整搭配与原段关系：矩阵运算、网络前向次数→单次迭代复杂度。
  本文网络为denoiser和classifier，含1+2L_z次denoiser调用；C_theta/C_phi定义、逐设备K倍及矩阵量级来自本文，不能登记为Cai原公式。
  核对锚点：the computational costs of a forward pass
- 本文既有矩阵模型与SVD展开；eq:linear-variance至eq:linear-extrinsic；eq:linear-fraction。支持层次：本文代数变换及复杂度计算。
  块内固定观测矩阵、thin SVD、完整Gram矩阵及本文尺寸保留；不套用Cai部分正交/FFT或Wei行正交简化。
- 本文既有参数估计流程；V-B与Appendix app:frontend。支持层次：本文定义和交叉引用。
  观测矩阵、物理噪声估计的构成与固定使用方式保持；不是另引文献的同一接收机。

## ch5_bc-P11-S01 — 保留

**原文**

```latex
For supplied phases, $C_{\rm phase}=0$.
```

**改后**

```latex
For supplied phases, $C_{\rm phase}=0$.
```

**理由**：已提供相位时的成本简化是实际特例，保留。

- 本文既有尺寸与参数共享实现；V-C；eq:linear-fraction；本文KN×MN消息、M×M空间协方差。支持层次：本文计算量/工作存储计数。
  给定phases时C_phase=0；共享训练权重；工作存储不包含权重和网络激活。各项量级逐字保留，不作外部原句来源认定。

## ch5_bc-P11-S02 — 保留

**原文**

```latex
All devices share the trained parameters.
```

**改后**

```latex
All devices share the trained parameters.
```

**理由**：共享参数这一实现条件简洁明确，保留。

- 本文既有尺寸与参数共享实现；V-C；eq:linear-fraction；本文KN×MN消息、M×M空间协方差。支持层次：本文计算量/工作存储计数。
  给定phases时C_phase=0；共享训练权重；工作存储不包含权重和网络激活。各项量级逐字保留，不作外部原句来源认定。

## ch5_bc-P11-S03 — 修改

**原文**

```latex
Excluding these parameters and network activations, the pilot/SVD factors, channel messages, and spatial covariance matrices require $O(QKN+KMN^2+KM^2)$ working storage.
```

**改后**

```latex
The working storage for the pilot/SVD factors, channel messages, and spatial covariance matrices is $O(QKN+KMN^2+KM^2)$, excluding trained parameters and network activations.
```

**理由**：将所统计的工作存储对象置于句首，排除范围放在句末，所有量级和边界保持。

- 本文既有尺寸与参数共享实现；V-C；eq:linear-fraction；本文KN×MN消息、M×M空间协方差。支持层次：本文计算量/工作存储计数。
  给定phases时C_phase=0；共享训练权重；工作存储不包含权重和网络激活。各项量级逐字保留，不作外部原句来源认定。

## Algorithm 1

标题、输入和输出等 3 项元信息，以及 10 项执行/控制单元均已审读。整个伪代码块逐字保持；逐项理由及原文出处见同名 JSON 和 agents/ch5_a_review.json。
