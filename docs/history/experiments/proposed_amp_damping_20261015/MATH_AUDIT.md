# 新 AMP 阻尼递推的独立数学审查

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent。
- Origin Mode: validate；本次范围为数学与合成数组的代数核对。
- Origin Date: 2026-10-15。
- Verification Status: ANALYZED；下述合成代数检查已执行通过，不表示已验证状态演化或真实接收机性能。
- Version Label: damping_math_audit_v1。
- 审查者：原生子代理 `/root/amp_math_audit`；继承父对话上下文，因此不是盲审或跨模型审查。
- 修改范围：仅本目录的新审查文档、合成检查脚本及其结果。未修改接收机、旧 Proposed 或既有无阻尼实现；未调用真实网络、训练数据或场景真值。
- 输入：当前无阻尼 `score_amp/core.py` 的公式与索引、父代理给定的阻尼候选、冻结实验协议及下列原始论文。

**结论：候选历史 Onsager 项可以压缩成一个递归变量。** 在相同初始化、同一新值权重、对原始联合映射求导的约定下，

\[
X_{t+1}=(1-\beta)X_t+\beta D_t,\qquad
C_{t+1}=(1-\beta)C_t+\beta Z_t B_t,\qquad
Z_{t+1}=Y-AX_{t+1}+C_{t+1}
\tag{1}
\]

与同时阻尼完整无阻尼更新严格等价。这个代数结论对任意有限矩阵及任意给定的 \(B_t\) 序列成立。把 \(B_t\) 解释为正确 Onsager 校正及把查询解释为 Gaussian 有效观测，还需要另外的随机矩阵、正则性和导数估计条件。当前 AFDM 实现是经验适配。

## 1. 索引及初始化

使用归一化后的模型

\[
Y=AX_\star+W,\quad A\in\mathbb C^{Q\times L},\quad
X_\star\in\mathbb C^{L\times C},\quad L=KN,\ C=MN_{\rm out}.
\]

下标 \(t=0\) 为第一次网络查询之前。固定

\[
X_0=0,\quad C_0=0,\quad Z_0=Y,\quad
R_t=X_t+A^H Z_t,\quad D_t=D(R_t;v_t).
\tag{2}
\]

\(D_k=p_kF_k\) 是完整的活动加权信道映射。保持原来的矩阵部分迹约定：

\[
(B_t)_{ab}=\frac1Q\sum_{i=1}^{L}
\frac{\partial D_{ib}(R_t;v_t)}{\partial R_{ia}},
\quad a=\text{输入特征},\quad b=\text{输出特征}.
\tag{3}
\]

导数为 Wirtinger 偏导，求导时冻结本次标签 \(v_t\)。它包括 \(p\) 与 \(F\) 的所有输入依赖。\(B_t\) 不因阻尼而先乘 \(\beta\)；权重只出现在式(1)。若先估计 \(\partial(\beta D)/\partial R\)，式(1)再乘一次 \(\beta\) 会造成错误的 \(\beta^2\)。此索引与复数非可分矩阵 AMP 的部分迹结构相符；原文记号的转置须按分量定义核对。[Kunde 等，§III-C 式(18)–(21)、Remark 14](https://arxiv.org/html/2604.21115v1#S3.SS3)

## 2. 从带历史的去噪映射得到校正项

先设 \(0<\beta\leq1\) 为预先固定常数。重复展开信道阻尼得到

\[
X_{t+1}=(1-\beta)^{t+1}X_0+
\sum_{s=0}^{t}w_{t,s}D(R_s;v_s),\qquad
w_{t,s}=\beta(1-\beta)^{t-s}.
\tag{4}
\]

因为 \(X_0=0\)，初始化项消失；但 \(\sum_s w_{t,s}=1-(1-\beta)^{t+1}\)，**并非1**。不能把这些权重重新归一化，否则会改变首轮及整个算法。推导误差协方差时，初始估计误差仍是 \(E_0=-X_\star\)，也不能删除。

把式(4)视为历史输入相互独立的多元函数

\[
\mathcal D_t(R_0,\ldots,R_t)=\sum_{s=0}^{t}w_{t,s}D(R_s;v_s).
\]

这里“独立”仅指求偏导时是不同的自变量，**不表示不同轮的随机误差统计独立**。冻结全部 \(v_s\)，其历史部分迹为

\[
(H_{t,s})_{ab}=\frac1Q\sum_i
\frac{\partial (\mathcal D_t)_{ib}}{\partial (R_s)_{ia}}
=w_{t,s}(B_s)_{ab}.
\tag{5}
\]

在 iid Gaussian AMP 的带历史公式中，测量端必须使用全部这些偏导块：

\[
Z_{t+1}=Y-A X_{t+1}+\sum_{s=0}^{t}Z_s H_{t,s}
=Y-A X_{t+1}+\sum_{s=0}^{t}w_{t,s}Z_s B_s.
\tag{6}
\]

实数矩形原始依据是 Fan 的完整历史更新式(5.3)–(5.8)，以及式(5.12)和 Remark 5.1 的 iid Gaussian 特例：其历史系数化为对应输入的偏导平均。该论文的更一般旋转不变矩阵需要额外的谱相关项，不能把 Gaussian 特例直接外推到任意算子。[Fan，§5](https://arxiv.org/html/2008.11892v5#S5)

查询为何仍为式(2)：以 \(E_t=X_t-X_\star\) 为信道误差，把测量侧写为

\[
P_t=AE_t-\sum_{s<t}Z_sH_{t-1,s},\qquad Z_t=W-P_t.
\]

测量侧函数 \(g_t(P_0,\ldots,P_t;W)=W-P_t\) 对当前输入的导数为 \(-I\)，对更早输入的偏导为零。因此另一侧的 Onsager 项仍是 \(+E_t\)，给出
\(R_t-X_\star=A^H Z_t+E_t\)。不能因为信道去噪有历史，就额外随意加入查询历史项。

复数 cavity 展开的对应解释是：移去观测行 \(\mu\) 会在每个历史输入中产生第一阶扰动
\(\Delta(R_s)_{ja}\simeq-\overline A_{\mu j}(Z_s)_{\mu a}\)。一般实可微复映射同时产生
\(A_{\mu i}\overline A_{\mu j}\,\partial\mathcal D_t/\partial R_s\)
与
\(A_{\mu i}A_{\mu j}\,\partial\mathcal D_t/\partial\overline R_s\)
两类项。在独立 proper-complex Gaussian 及 cavity 集中条件下，前者收缩为行对角部分迹，后者的均值为零，得到式(6)。在当前有限 AFDM 算子上，舍弃非对角与共轭项是近似，阻尼并未使这一步变成恒等式。

## 3. 历史和的精确递推压缩

定义

\[
C_{t+1}=\sum_{s=0}^{t}\beta(1-\beta)^{t-s}Z_sB_s.
\]

把最新项分离即得式(1)中的递推；只需保存一个 \(Q\times C\) 数组，不必保存所有历史 \(B_s\)。由不变量
\(Z_t=Y-AX_t+C_t\)，有

\[
\begin{aligned}
Z_{t+1}
&=Y-A[(1-\beta)X_t+\beta D_t]
 +(1-\beta)C_t+\beta Z_tB_t\\
&=(1-\beta)Z_t+\beta[Y-AD_t+Z_tB_t].
\end{aligned}
\tag{7}
\]

式(7)是实现时的简单形式。它与式(1)、(6)在代数上完全一致，不要求 \(A\) 随机，也不要求 \(B_t\) 为精确导数。有限差分和随机探针会影响统计质量，但不会破坏这三个表达式之间的代数等价。

仅将校正替换为 \(\beta Z_tB_t\)、同时丢弃 \((1-\beta)C_t\)，从第二次更新开始一般不再等价。仅阻尼 \(X\) 而仍使用原来的最新一项 \(Z_tB_t\) 也不是式(6)。

对预先确定的时变权重 \(\beta_t\)，相同结论成立，只需将

\[
w_{t,s}=\beta_s\prod_{\ell=s+1}^{t}(1-\beta_\ell),\quad
C_{t+1}=(1-\beta_t)C_t+\beta_tZ_tB_t.
\tag{8}
\]

本轮实验使用固定权重。数据自适应权重若被视为输入的函数，历史偏导还可能出现权重的导数；不能仅在程序中冻结权重，就宣称已经验证了相应自适应状态演化。

## 4. 与普通矩阵 AMP 的历史列扩展核对

固定一个有限轮数 \(T\)，将 \(T+1\) 个历史块并列为特征列。构造重复观测
\(\widetilde Y=[Y,\ldots,Y]\)，初始化
\(\widetilde X_0=0,\widetilde Z_0=\widetilde Y\)。在全局第 \(t\) 轮，定义普通矩阵 AMP 去噪器的第 \(j\) 个输出块：

\[
\widetilde D_{t,j}(\widetilde R)=
\begin{cases}
0,&j=0\text{ 或 }j>t+1,\\
\sum_{s=0}^{j-1}w_{j-1,s}D(\widetilde R_s;v_s),&1\leq j\leq t+1.
\end{cases}
\tag{9}
\]

完整矩阵部分迹的历史块为

\[
\widetilde B_t[s,j]=w_{j-1,s}B_s,\qquad 0\leq s<j\leq t+1,
\tag{10}
\]

其余块为零。普通更新

\[
\widetilde X_{t+1}=\widetilde D_t(\widetilde R_t),\quad
\widetilde Z_{t+1}=\widetilde Y-A\widetilde X_{t+1}
 +\widetilde Z_t\widetilde B_t
\]

恰好保留历史 \((X_j,Z_j,R_j)\) 并生成新的 \((X_{t+1},Z_{t+1})\)。本次合成检查独立构建了式(9)–(10)，再与式(1)逐轮比较。此构造也说明：块内非可分去噪与历史记忆可以同时存在；每轮只需原始 \(D\) 的部分迹，不需要重新对整条迭代链进行总微分。

把历史列作为矩阵特征是已有 AMP 理论中的证明方法。Rossetti–Nazer–Reeves 的 Appendix A 给出 full-memory AMP，Theorem 5 式(59)–(62)使用历史偏导，Appendix A.2.1将其嵌入矩阵迭代。其定理针对 Gaussian 随机矩阵与固定有限轮数，不是“随着轮数无限增加必收敛”的定理。[OpAMP 原文，Appendix A](https://arxiv.org/html/2405.08225v2#A1)

上述历史列构造在这里首先是**精确代数嵌入**。若要引用一个完整统计定理，还须核对历史扩展后的函数正则性、初始化、固定特征数、重复观测所产生的跨特征噪声协方差及其可能奇异性。本文不把几篇不同设定的定理拼接成当前神经网络 AFDM 接收机的已证定理。

## 5. 首轮、方差标签与输出语义

所有 \(\beta\) 必须共有

\[
R_0=A^HY,\quad v_0=\|Y\|_F^2/(QC),\quad
D_0=D(R_0;v_0),\quad p_0,\quad B_0.
\]

第一步才开始分叉：

\[
X_1=\beta D_0,\quad C_1=\beta YB_0,\quad
Z_1=Y-\beta AD_0+\beta YB_0.
\tag{11}
\]

因此，原始首轮分类器饱和若存在，阻尼不会在第一次网络调用之前将其消除。将首轮设为不阻尼是一种不同的预设时变策略，不能默认为本方案。

建议沿用与原实现精确兼容的标签：

\[
\widehat\Sigma_t[a,b]=\frac1Q\sum_\mu
(Z_t)_{\mu a}\overline{(Z_t)_{\mu b}},\qquad
v_t=\operatorname{tr}(\widehat\Sigma_t)/C
=\|Z_t\|_F^2/(QC).
\tag{12}
\]

这里必须使用本轮**经过历史校正及阻尼后的** \(Z_t\)。不能换成未校正的 \(Y-AX_t\)，不能再独立平滑标签，也不能误用 \(\beta^2 v_t\)。例如令
\(Z^{\rm raw}_{t+1}=Y-AD_t+Z_tB_t\)，则严格有

\[
\|Z_{t+1}\|_F^2=(1-\beta)^2\|Z_t\|_F^2
 +\beta^2\|Z^{\rm raw}_{t+1}\|_F^2
 +2\beta(1-\beta)\Re\langle Z_t,Z^{\rm raw}_{t+1}\rangle_F.
\tag{13}
\]

直接计算更新后残差能量包含全部交叉项。长记忆方法跟踪跨轮协方差的原始例子可见 Takeuchi 式(27)–(28)、(44)–(45)；这些式子用于 LM-OAMP 的外信息消息，不能把本方案称为 LM-OAMP 复现。[Takeuchi，§III-C/D](https://arxiv.org/html/2111.05522v2#S3.SS3)

在满足 iid Gaussian AMP 条件的理想模型中，带历史的状态演化应追踪联合时间协方差。以 \(E_t=X_t-X_\star\) 为例，候选协方差形式为

\[
\Sigma_{t,u}=\Sigma_W+
\lim\frac1Q\mathbb E[E_t^T\overline{E_u}],
\qquad R_t=X_\star+G_t,
\tag{14}
\]

其中 \(\mathbb E[G_{t,ia}\overline{G_{u,ib}}]=(\Sigma_{t,u})_{ab}\)。\(E_{t+1}=(1-\beta)E_t+\beta(D_t-X_\star)\)的二阶矩含跨轮交叉项。式(12)是这个理想统计结构下的自然经验标签，而不是有限 AFDM 中真实查询 MSE 的恒等式。矩阵特征协方差一般也不等于 \(v_tI\)；把其迹平均输入冻结 AWGN 网络的既有近似仍然存在。

对导数冻结 \(v_t\) 的约定，式(5)首先对应标签已给定的函数族。若标签由残差经验估计，要获得状态演化结论，还需额外证明参数估计集中及映射连续性；代数等价本身不提供这项证明。

实验主输出应固定为迭代状态 \(X_{t+1}\)，原始 \(D_t\)另存用于诊断。保留最新网络的原始活动输出 \(p_t\)是清楚且可复现的选择，但它不是式(4)历史混合后信道均值的唯一对应后验概率。不能在 \(X\)、\(D\)及不同轮数之间依据真值挑选输出。关闭 Onsager 时 \(C_t=0\)，同一递推准确退化为 \(Z_t=Y-AX_t\)的阻尼去噪迭代。

## 6. 固定点与局部稳定性的边界

对于**确定性的、时间不变的完整映射** \(\mathcal T:(X,Z)\mapsto(D,Y-AD+ZB)\)，例如精确导数，或固定探针与固定差分规则产生的确定映射，同步阻尼是

\[
\mathcal T_\beta=(1-\beta)I+\beta\mathcal T.
\]

对 \(\beta>0\)，两映射的固定点相同。如果固定点附近可微，则完整实坐标状态 Jacobian 的特征值 \(\lambda\)变为

\[
\lambda_\beta=1-\beta+\beta\lambda.
\tag{15}
\]

这是直接微分得到的恒等式；\(\lambda\)是整个 \((X,Z)\)更新的特征值，**不是 Onsager 矩阵 \(B\) 的特征值**。局部稳定需要 \(|\lambda_\beta|<1\)。阻尼能够缩小某些振荡方向，但若 \(\Re\lambda\geq1\)，任意正 \(\beta\)均不能使该方向严格收缩。该分析也不排除非正规矩阵的暂态放大或远离固定点时的非线性失败。

当前实际实现每轮重新抽取8个探针，并使用非零步长的中心差分。因此实现是随机、有限差分的近似递推，通常不存在一个每轮相同的确定性 \(\mathcal T\)。式(15)可解释一个理想或冻结版本，**不能推出实际随机样本路径收敛**。每轮抽样后，式(1)/(6)/(7)的代数等价仍成立，所保存的历史校正对应当轮实际使用过的 \(\widehat B_s\)；不应回头重抽旧轮探针并替换历史项。

有限轮数没有越过训练标签范围，只能报告完成该轮数预算；小 \(\beta\)导致的变化量较小也不是收敛证据。未阻尼映射的残差、活动输出、误差标签校准和网络调用成本应一起报告。本轮协议预设主权重0.2、敏感性0.1/0.5及0.2无 Onsager，对这一解释边界是合适的。

## 7. 独立数值证据

运行 `audit_damping_algebra.py`，随机种子202610158217，\(Q=7,L=12,C=3,T=6\)。去噪映射包含跨行与跨特征的复线性项、共轭线性项和分别作用于实虚部的光滑非线性；没有调用项目接收机或学习网络。覆盖 \(\beta=1,0.5,0.2\)及预设变化权重。结果存于 `DAMPING_ALGEBRA_CHECK.json`。

| 检查 | 实测结果 |
|---|---:|
| 递归 \(X\) 对显式历史和，最大相对误差 | \(1.19\times10^{-16}\) |
| 递归 \(C\) 对显式历史和，最大相对误差 | \(1.45\times10^{-16}\) |
| 历史校正式对同步阻尼残差，最大相对误差 | \(1.61\times10^{-16}\) |
| 普通矩阵 AMP 历史列扩展对原递推全部历史查询/状态 | 最大 \(1.95\times10^{-16}\) |
| \(\beta=1\)对独立无阻尼实现的整条轨迹 | 0 |
| 不同 \(\beta\)的第一查询差异 | 0 |
| 各历史输入偏导对四方向中心差分 | 最大 \(4.24\times10^{-10}\) |
| 显式坐标导数部分迹对解析式 | 最大 \(9.56\times10^{-17}\) |
| 协方差混合公式包含交叉项 | 相对误差 \(3.24\times10^{-16}\) |
| 负对照：省略历史校正，\(\beta=0.2\) | 校正相对差异最高0.695 |
| 负对照：忽略跨轮协方差 | 协方差相对误差0.290 |

这些是有限数组恒等式及导数的数值核对，没有统计显著性检验、性能排名或真实场景收敛结论。特别是跨轮协方差负对照为人为构造的相关合成数组，仅用于证明忽略交叉项可以产生明显错误。

## 8. 术语及原文定位交接

本审查的写权限仅在本实验目录，因此未改 `docs/TERMINOLOGY.md`。父代理可将以下新定位汇入统一术语表；不需要新造方法名称或缩写。

| 术语/依据 | 核对到的原始位置 | 本次使用范围 |
|---|---|---|
| AMP with all previous iterates；Onsager corrections | [Fan，arXiv:2008.11892v5](https://arxiv.org/html/2008.11892v5#S5)，§5 式(5.3)–(5.8)、(5.12)，Remark 5.1 | iid Gaussian 特例下的历史偏导系数；不移植一般旋转不变谱公式 |
| full-memory AMP | [Rossetti–Nazer–Reeves，arXiv:2405.08225v2](https://arxiv.org/html/2405.08225v2#A1)，Appendix A，Theorem 5 式(59)–(62)，A.2.1 | 以矩阵特征表示固定有限轮数的历史；不宣称AFDM统计定理 |
| complex AMP；non-separable denoising；Wirtinger derivatives；matrix extension | [Kunde 等，arXiv:2604.21115v1](https://arxiv.org/html/2604.21115v1#S3.SS3)，§III-B Assumption 8，§III-C 式(18)–(21)、Remark 14 | 复数矩阵部分迹和随机矩阵/函数条件；预印本 |
| long-memory message passing；damping；error covariance | [Takeuchi，arXiv:2111.05522v2](https://arxiv.org/html/2111.05522v2#S3.SS3)，§III-C 式(27)–(29)，§III-D 式(44)–(46) | 历史混合必须考虑跨轮协方差；当前递推不是其LM-OAMP算法 |

核查日期为2026-10-15。所有上述公式位置均直接核对原始作者稿HTML；本次未依赖二手解释来认定递推正确。
