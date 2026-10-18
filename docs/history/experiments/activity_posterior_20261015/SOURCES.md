# 未知活动后验：最小文献依据

核验日期：2026-10-15。这里只核验术语和公式来源；没有运行推断，没有上传项目内容。
以下页码均明确对应所读版本。模型与运行方案见同目录 `PROTOCOL.md`；本文不改变方案。

## 1. 原始论文与可定位依据

| 来源 | 已核验位置 | 本方案采用的依据与边界 |
|---|---|---|
| Jun S. Liu, “The Collapsed Gibbs Sampler in Bayesian Computations With Applications to a Gene Regulation Problem,” *JASA*, 89(427), 958–966, 1994. [DOI](https://doi.org/10.1080/01621459.1994.10476829)；[公开全文](https://www.cs.columbia.edu/~blei/fogm/2023F/readings/Liu1994.pdf) | §1，印刷页 958；所读 PDF 第 2 页（第 1 页是出版社封面）。定义所在段落没有式号。 | 逐变量从完整条件分布抽样是 Gibbs 更新；多个变量从联合条件分布同时抽样称 grouping / blocking；先积分消去部分变量再对剩余变量采样称 collapsing。这里分别消去 Gaussian 信道、联合更新两个活动变量。 |
| Alexander Fengler, Saeid Haghighatshoar, Peter Jung, Giuseppe Caire, “Non-Bayesian Activity Detection, Large-Scale Fading Coefficient Estimation, and Unsourced Random Access with a Massive MIMO Receiver,” *IEEE TIT*, 67(5), 2925–2951, 2021. [DOI](https://doi.org/10.1109/TIT.2021.3065291)；[版本及出版元数据](https://arxiv.org/abs/1910.11266v3)；[公开全文 v3](https://arxiv.org/pdf/1910.11266v3) | 所读 v3（2021-09-21），PDF 共 59 页。§II-A，第 9 页式 (6)–(7)：协方差与样本协方差；§III-A，第 9 页式 (8)–(9)：负对数似然；第 10 页式 (11)：非负连续域上的 relaxed ML；第 11 页式 (12)：已知衰落系数时的二元约束 ML。 | iid 复 Gaussian 观测列产生 logdet＋trace 似然。本文主要实用估计器优化连续非负活动功率，同时也分析二元约束 ML；不能把整个原文概括成“只有连续变量”。本项目的 Bernoulli 先验、二元支持后验及 Gibbs 积分是本项目的模型适配，不是该文的 ML 算法。 |
| Aki Vehtari, Andrew Gelman, Daniel Simpson, Bob Carpenter, Paul-Christian Bürkner, “Rank-Normalization, Folding, and Localization: An Improved R-hat for Assessing Convergence of MCMC.” [DOI](https://doi.org/10.1214/20-BA1221)；[作者公开全文](https://sites.stat.columbia.edu/gelman/research/published/rhat.pdf) | 所读作者版 28 页，首页标记 2020、页码 1–28；不混用期刊版页码。§1.1，第 1–3 页；§2，第 5–6 页。 | 多链及链内信息有助于发现不同模式与非平稳行为；§2 建议默认至少四条链。这里仅借此说明多链比较的动机；本方案不声称实现该文的 R-hat / ESS 方法。 |

## 2. 本项目的公式适配（自行推导，并非上述论文原式）

令 \(A=[A_1,\ldots,A_K]\)，\(A_k\in\mathbb C^{Q\times N}\)，
\(Y\in\mathbb C^{Q\times C}\)。采用当前方案的独立 Bernoulli 活动先验，
以及活跃用户独立、列间独立的 \(\mathcal{CN}(0,qI_N)\) 信道。
对信道积分后，

\[
\Sigma(a)=\sigma^2 I_Q+q\sum_{k=1}^K a_k A_k A_k^H,
\qquad \widehat S=YY^H/C,
\]

\[
\begin{aligned}
\ell(a)&=\log p(a\mid Y)+\text{与 }a\text{ 无关的常数}\\
&=-C\log\det\Sigma(a)
  -C\operatorname{tr}\{\Sigma(a)^{-1}\widehat S\}
  +\sum_k a_k\log\frac{\rho}{1-\rho}.
\end{aligned}
\]

这将 Fengler 等的 rank-one 用户协方差贡献替换为本模型的用户块贡献
\(q a_k A_kA_k^H\)，并加上明确的 Bernoulli 对数先验。
当前协议保留空活动状态，因此支持域是完整的 \(\{0,1\}^K\)。
\(\sigma^2>0\) 时协方差正定。复 Gaussian 密度中上述两个数据项没有实 Gaussian
密度的 \(1/2\) 因子。等价地，trace 项为
\(\operatorname{tr}(Y^H\Sigma^{-1}Y)\)，避免重复乘 \(C\)。

**单变量 Gibbs 对照。** 固定其余活动变量，记 \(a^{k\leftarrow b}\) 为第 \(k\)
位设为 \(b\) 的支持，则

\[
P(a_k=1\mid a_{-k},Y)
=\operatorname{sigmoid}\big[\ell(a^{k\leftarrow1})-\ell(a^{k\leftarrow0})\big].
\]

**两个变量的 blocked Gibbs 主候选。** 对块 \(B=\{i,j\}\)，精确枚举
\(s\in\{0,1\}^2\) 的四个条件权重：

\[
w_s=\ell(a_{-B},s),\quad m=\max_s w_s,\qquad
P(a_B=s\mid a_{-B},Y)=\frac{e^{w_s-m}}{\sum_u e^{w_u-m}}.
\]

据此抽取一个联合四状态样本；两次独立地按边际 Bernoulli 抽样一般不等价。
每个完整条件更新保持目标后验不变，更新的顺序组合也保持它不变；不能未经核验就
把一次完整 sweep 的组合核称为满足详细平衡。有限预算的近似精度须按方案实测。
术语依据为 Liu §1；上述二元条件公式是本项目对通用定义的具体代入。

**信道输出。** 给定支持，Gaussian 条件均值同时是该条件下的 LMMSE 估计：

\[
M_k(a)=a_k q A_k^H\Sigma(a)^{-1}Y,\qquad
E[X_k\mid Y]=E_{a\mid Y}[M_k(a)].
\]

第二个等式来自全期望公式。用保留的支持样本平均 \(M_k\) 是对此期望的 Monte Carlo
近似；活动概率同样用支持指示量的样本平均。以硬阈值选一个支持再做条件均值不等于
这两个后验平均。本文使用现有术语直接描述这些操作，不另造算法名称。

## 3. 证据范围与报告措辞

本次协方差似然的精确性依赖协议中的独立 Gaussian 信道模型；它没有证明真实物理
AFDM 信道也满足列独立假设。原论文也不为本项目的矩阵、先验或有限链长提供性能保证。
对两个变量联合更新的收益仍由小规模全枚举对照检验。

链间边际差异、前后半段差异、状态转移次数与访问支持数量都是本方案明确计算的描述量，
不是 Vehtari 等提出的 R-hat / ESS，也不是收敛证明。多个链同时停滞可以产生看似一致的
边际；有转移也不意味着覆盖全部后验模式。小规模精确枚举检验近似误差，大规模结果
保留有限预算与未能枚举的限制。
