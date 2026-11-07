# P09–P13 来源措辞修订候选

仅提供精确替换候选，未改canonical。依据FINAL_AUDIT、本人本轮原PDF核查与Cai正式版/v2、Huang原句。

原9句SUPPORTED_PARAPHRASE中8句恢复原句结构或可定位分句组合；P12.S03经主审确认保留为作者公式说明，因为其源材料是Table II公式而没有英语原句。另将P12.S02的working posterior替换为joint posterior distribution。

保留q_tr、给定估计、独立性和所有数学含义；全部显示公式、标签、维度不变。内部eq:working-posterior标签保留，正文不再出现working posterior。没有新增working model等替代名称，也没有添加防御性句子。

## 逐项候选及原句来源

### P09.S01

新句：

```tex
We use an indicator function $\alpha_k$ to model the device activity as
\cite{cai2026}
\[
 \alpha_k=\begin{cases}
 1,&\text{if the $k$th device is active},\\
 0,&\text{otherwise}.
 \end{cases}
\]
```

处理：恢复Cai II-A “We use an indicator function ... to model the device activity as”原句骨架；二值公式逐字不变。

对应原句/定位：

- cai2026；PDF p.4 / journal p.3578；II-A；(1)

  > We use an indicator function αk to model the device activity as

  定位：Left column, below Table I; cases: 1, if the k-th device is active; 0, otherwise.
- cai2026_stmp_v2；PDF p.4；II-A；(1)

  定位：Same indicator sentence and cases (1) as the formal version.

### P09.S02

新句：

```tex
Let $\rho$ represent the probability of a device being active, i.e.,
$\Pr(\alpha_k=1)=\rho$, where $\rho\ll1$.
```

处理：恢复Cai II-A活动概率原句；仅λ→ρ及p→Pr符号适配，数学不变。

对应原句/定位：

- cai2026；PDF p.4 / journal p.3578；II-A；after (1)

  > Let λ represent the probability of a device being active, i.e., p(αk = 1) = λ, where λ ≪ 1.

### P09.S05

新句：

```tex
After removing the CPP and applying the DAFT, the received signal
$\mathbf Y_q\in\mathbb C^{M\times N}$ during the $q$th AFDM
frame is given by \cite{cai2026}
\begin{equation}
 Y_{qmr}=[\mathbf Y_q]_{mr}
 =\sum_{k=1}^K\sum_{n=0}^{N-1}A_{qkn}X_{kmrn}+W_{qmr},
 \label{eq:observation-tensor}
\end{equation}
where $\mathbf W_q=[W_{qmr}]_{m,r}\in\mathbb C^{M\times N}$ is an
AWGN matrix with the elements i.i.d. drawn from $\CN(0,\sigma^2)$.
```

处理：接收主句已按Cai的CP/DFT/OFDM替换为CPP/DAFT/AFDM，现只恢复where原词；W元素索引、双求和、全部维度是本稿数学适配，保持原字节。

对应原句/定位：

- cai2026；PDF p.4 / journal p.3578；II-A；(3)

  > After removing the CP and applying the DFT, the received signal Yt ∈ C^{N×M} during the t-th OFDM symbol is given by

  定位：Right column; Y_t = sum_k α_k Q_kt H_k + N_t, with Q_kt diagonal.
- cai2026；PDF p.4 / journal p.3578；II-A；where after (3)

  > where Nt ∈ C^{N×M} is an AWGN matrix with the elements i.i.d. drawn from CN(0, δ_0^2).
- huang2026；PDF p.2 / journal p.2950；II, System Model；(4)–(5)

  定位：AFDM effective input-output relation (4)–(5): an N×N effective channel matrix acts on an N-vector; supports non-diagonal symbol coupling.

### P09.S06

新句：

```tex
We express the received signal $\mathbf Y$ over the $Q$ AFDM frames
in a more compact form as
\begin{equation}
 \mathbf Y=\mathbf A\mathbf X+\mathbf W,
 \label{eq:mmv}
\end{equation}
where $\mathbf Y,\mathbf W\in\mathbb C^{Q\times MN}$,
$\mathbf A\in\mathbb C^{Q\times KN}$, and
$\mathbf X\in\mathbb C^{KN\times MN}$.
```

处理：恢复Cai II-A “We express the received signal Y over the T OFDM symbols in a more compact form as”主句；T/OFDM symbols→Q/AFDM frames。既有Q×MN、Q×KN、KN×MN及where定义不动，仍属本稿重排。

对应原句/定位：

- cai2026；PDF p.4 / journal p.3578；II-A；(4)

  > We express the received signal Y over the T OFDM symbols in a more compact form as

  定位：Y: NT×M; Q: NT×NK; X: NK×M. Stacks received subcarriers and time vertically.
- shen2025；PDF p.5；II-C；(15)

  > Next, we collect the Q received frames into a single matrix as

  定位：Collects OTFS observations Y_q^l over frames; this is not the present AFDM indexing.

### P09.S08

新句：

```tex
We directly estimate the full AFDM effective channel tensor $H_k$
without imposing sparsity assumptions
\cite{huang2026}.
```

处理：逐词采用Huang III-A “we directly estimate the full AFDM effective channel matrix ... without imposing sparsity assumptions”分句；仅去Since使其独立成句，并将matrix H_eff适配为tensor H_k，不搬入其单导频因果条件。

对应原句/定位：

- huang2026；PDF p.3 / journal p.2951；III-A；after (6)

  > Since we directly estimate the full AFDM effective channel matrix Heff without imposing sparsity assumptions, using only one pilot sequence makes (6) underdetermined, so that multiple pilot sequences are required.

### P09.S10

新句：

```tex
Due to the sporadic access of the devices, matrix $\mathbf X$ exhibits
a block-sparsity structure. Specifically, if the $k$th device is inactive,
we have $X_k=\alpha_kH_k=\mathbf 0$ \cite{cai2026}.
```

处理：恢复Cai II-A两条连续原句的结构与词汇，不再用新主谓和冒号转述；零块公式不变。

对应原句/定位：

- cai2026；PDF p.4 / journal p.3578；II-A；after (4)

  > Due to the sporadic access of the devices, matrix X exhibits a block-sparsity structure. Specifically, if the k-th device is inactive, we have Xk = αkHk = 0.

### P10.S01

新句：

```tex
In this paper, we aim to simultaneously detect the active devices
and estimate the corresponding channels based on the observation
$\mathbf Y$ under a Bayesian inference framework \cite{cai2026}.
```

处理：恢复Cai II-B首句完整原文句法，只把观测Y使用本稿LaTeX符号；没有增加算法性能主张。

对应原句/定位：

- cai2026；PDF p.4 / journal p.3578；II-B

  > In this paper, we aim to simultaneously detect the active devices and estimate the corresponding channels based on the observation Y under a Bayesian inference framework.

### P12.S02

新句：

```tex
Here, $q$ denotes the joint posterior distribution, and
$p(\mathbf y_j\mid\mathbf x_j)=\CN(\mathbf y_j;
\widehat{\mathbf A}\mathbf x_j,\widehat\sigma^2\I_Q)$ is the
Gaussian likelihood associated with \eqref{eq:mmv}.
```

处理：移除未找到原词出处的working posterior，采用Cai II-B明确使用的joint posterior distribution。q、q_tr、给定估计、Gaussian似然及其公式不变；内部标签eq:working-posterior依标签不动要求保留。

对应原句/定位：

- cai2026；PDF p.4 / journal p.3578；II-B；(5)

  > In message passing, we factorize the joint posterior distribution according to Baye’s theorem and the conditional independence relationships among the variables, expressed as

  定位：p(X,{H_k},{α_k}|Y) ∝ product_m p(y_m|x_m) product_k p(X_k|H_k,α_k)p(H_k)p(α_k).
- cai2026；PDF p.5 / journal p.3579；II-B, Table II

  定位：Table II rows: p(y_m|x_m)=CN(Qx_m,δ_0²I_NT); p(X_k|H_k,α_k)=δ(X_k−α_kH_k); p(H_k) unspecified; p(α_k)=(1−λ)δ(α_k)+λδ(1−α_k).

### P13.S01

新句：

```tex
Message-passing algorithms provide an iterative approach for
approximately calculating these quantities by plugging in deep
generative priors for efficient message calculation, eliminating
the need to compute high-dimensional integrals \cite{cai2026}.
```

处理：组合Cai II-B “message-passing algorithms ... provide ... iterative approach for approximately calculating”与“by plugging in deep generative priors for efficient message calculation”及“eliminating the need to compute high-dimensional integrals”三个可定位分句。these quantities指向本文q下两个目标；删去low-complexity修饰，不采用provable或新性能承诺。

对应原句/定位：

- cai2026；PDF p.4 / journal p.3578；II-B

  > Alternatively, message-passing algorithms [5], [6], [27], [47] provide a low-complexity iterative approach for approximately calculating the MMSE estimator.
- cai2026；PDF p.5 / journal p.3579；II-B, concluding paragraph

  > This paper seeks to address the aforementioned challenges by plugging in deep generative priors for efficient message calculation.
- cai2026；PDF p.5 / journal p.3579；II-B, continuation above III

  > This insight enables the integration of score-based generative networks for provable MMSE denoising, eliminating the need to compute high-dimensional integrals.
- cai2026；PDF p.4 / journal p.3578；II-B

  > Exact Bayesian estimators, e.g., the MMSE estimator, are generally intractable due to the high-dimensional integrals in the marginalization of the joint posterior distribution p(X,{Hk}_{k=1}^K,{αk}_{k=1}^K|Y).

## 每个旧句处理状态

| 旧句 | 状态 | 处理 |
|---|---|---|
| P09.S01 | RESTORED_SOURCE_WORDING | 恢复Cai II-A “We use an indicator function ... to model the device activity as”原句骨架；二值公式逐字不变。 |
| P09.S02 | RESTORED_SOURCE_WORDING | 恢复Cai II-A活动概率原句；仅λ→ρ及p→Pr符号适配，数学不变。 |
| P09.S03 | RETAINED_AUTHOR_DEFINITION_OR_DERIVATION | 保留本文明确给出的定义、假设、内部指引或推导；不冒充参考原句。 |
| P09.S04 | RETAINED_AUTHOR_DEFINITION_OR_DERIVATION | 保留本文明确给出的定义、假设、内部指引或推导；不冒充参考原句。 |
| P09.S05 | RESTORED_SOURCE_WORDING | 接收主句已按Cai的CP/DFT/OFDM替换为CPP/DAFT/AFDM，现只恢复where原词；W元素索引、双求和、全部维度是本稿数学适配，保持原字节。 |
| P09.S06 | RESTORED_SOURCE_WORDING | 恢复Cai II-A “We express the received signal Y over the T OFDM symbols in a more compact form as”主句；T/OFDM symbols→Q/AFDM frames。既有Q×MN、Q×KN、KN×MN及where定义不动，仍属本稿重排。 |
| P09.S07 | RETAINED_AUTHOR_DEFINITION_OR_DERIVATION | 保留本文明确给出的定义、假设、内部指引或推导；不冒充参考原句。 |
| P09.S08 | RESTORED_SOURCE_WORDING | 逐词采用Huang III-A “we directly estimate the full AFDM effective channel matrix ... without imposing sparsity assumptions”分句；仅去Since使其独立成句，并将matrix H_eff适配为tensor H_k，不搬入其单导频因果条件。 |
| P09.S09 | RETAINED_AUTHOR_DEFINITION_OR_DERIVATION | 保留本文明确给出的定义、假设、内部指引或推导；不冒充参考原句。 |
| P09.S10 | RESTORED_SOURCE_WORDING | 恢复Cai II-A两条连续原句的结构与词汇，不再用新主谓和冒号转述；零块公式不变。 |
| P10.S01 | RESTORED_SOURCE_WORDING | 恢复Cai II-B首句完整原文句法，只把观测Y使用本稿LaTeX符号；没有增加算法性能主张。 |
| P11.S01 | RETAINED_AUTHOR_DEFINITION_OR_DERIVATION | 保留本文明确给出的定义、假设、内部指引或推导；不冒充参考原句。 |
| P11.S02 | RETAINED_AUTHOR_DEFINITION_OR_DERIVATION | 保留本文明确给出的定义、假设、内部指引或推导；不冒充参考原句。 |
| P11.S03 | RETAINED_AUTHOR_DEFINITION_OR_DERIVATION | 保留本文明确给出的定义、假设、内部指引或推导；不冒充参考原句。 |
| P11.S04 | RETAINED_AUTHOR_DEFINITION_OR_DERIVATION | 保留本文明确给出的定义、假设、内部指引或推导；不冒充参考原句。 |
| P11.S05 | RETAINED_AUTHOR_DEFINITION_OR_DERIVATION | 保留本文明确给出的定义、假设、内部指引或推导；不冒充参考原句。 |
| P12.S01 | RETAINED_AUTHOR_DEFINITION_OR_DERIVATION | 保留本文明确给出的定义、假设、内部指引或推导；不冒充参考原句。 |
| P12.S02 | TERM_REPLACED_AUTHOR_DEFINITION_RETAINED | 移除未找到原词出处的working posterior，采用Cai II-B明确使用的joint posterior distribution。q、q_tr、给定估计、Gaussian似然及其公式不变；内部标签eq:working-posterior依标签不动要求保留。 |
| P12.S03 | RETAINED_AUTHOR_FORMULA_EXPLANATION | 经主审确认，直接来源是Cai Table II的确定性δ关系和Bernoulli分布，不存在对应英语整句。在所有公式不动的约束下保留直接公式说明，不伪造原句，也不新增术语。 |
| P12.S04 | RETAINED_AUTHOR_DEFINITION_OR_DERIVATION | 保留本文明确给出的定义、假设、内部指引或推导；不冒充参考原句。 |
| P13.S01 | REASONABLE_SOURCE_CLAUSE_COMBINATION | 组合Cai II-B “message-passing algorithms ... provide ... iterative approach for approximately calculating”与“by plugging in deep generative priors for efficient message calculation”及“eliminating the need to compute high-dimensional integrals”三个可定位分句。these quantities指向本文q下两个目标；删去low-complexity修饰，不采用provable或新性能承诺。 |

P12.S03保留的“enforces”仅解释已定义确定性等式，不作为命名方法；其Bernoulli质量函数与Cai Table II双原子表达数学等价。该句不再列为“恢复了英语原句”。

P13使用三个Cai分句组合，删除low-complexity修饰，避免把文献的复杂度主张自动加到本稿。没有使用provable；these quantities明确回指本稿既有两个q目标。

核验：9个old串在基准正文中各出现一次；模拟替换后显示公式和标签序列逐字相同；基准SHA256与FINAL_AUDIT一致。
