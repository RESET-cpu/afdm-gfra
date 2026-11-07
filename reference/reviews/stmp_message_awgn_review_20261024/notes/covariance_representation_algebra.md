# 两网络 D-GEC 候选：协方差表示与闭合性

2026-10-24。独立推导笔记；仅阅读代码、原文及做一个 8 维确定性矩阵核验，没有训练或运行接收机。`C` 在此指 Gaussian 消息所声明的 query 噪声协方差族，不是物理信道先验协方差，也不自动等于实际迭代误差的协方差。第9节已纳入父任务完成的保存查询分析；据此提出初候选，尚未确定最终协方差族。

**主要判断：固定酉基、固定分组、每组一个精度是标准 GEC 最自然的起点。每用户完整 16×16 矩阵在 Gaussian quotient 下也闭合，但需要矩阵二阶约束和矩阵偏导部分迹；它不是直接把 D-GEC 的 `gdiag` 数值换成矩阵。可变单一 Kronecker 乘积通常不闭合，不宜因参数少就优先选用。** 第 9 节补入父任务新完成的离线诊断：在这些样本中输入列相关远强于最终轮空间相关，因此当前最小候选改为 **公开 `A_kᴴA_k` 特征基下的每用户输入列对角谱**，而非只保留空间 covariance。前文的族比较和闭合推导仍成立，空间族作为扩展/比较保留。

## 1. 本项目坐标与算子

已经核对：`src/system/observation.py`、`scenario/generate.py`、`pilot.py`、`phase.py`，以及 `src/algorithm/STMP/linear.py`、`gaussian.py`。

\[
Y_{qmr}=\sum_{k=1}^K\sum_{n=1}^{N_{in}} A_{qkn}H_{kmrn}+W_{qmr}.
\]

当前 `Q=16,K=40,M=16,Nout=Nin=16`。`linear.pack` 令 `i=(k,n)`、`b=(m,r)`，得到 `X∈C^(640×256)`、`A0∈C^(16×640)`。分析一个固定输出行 `r` 更方便：令 `x_r` 按 `(k,n,m)` 排列，`y_r` 按 `(q,m)` 排列，则

\[
y_r=B x_r+w_r,\qquad B=A_0\otimes I_M,\qquad r=1,\ldots,N_{out}.
\]

因此对每个输出行，观测维度 `QM=256`，未知维度 `K Nin M=10240`。若消息假设不同 `r` 独立且具有相同协方差，线性系统可共用，16 个 `r` 作为多个右端。

空间酉变换不会改变 `A0`：对每个 `H[k,:,r,n]` 和 `Y[q,:,r]` 同时乘 `U_Mᴴ`，测量仍为 `A0⊗I_M`。当前 4×4 UPA 的索引为 `m=n_z+M_z n_y`，见 `src/system/core/upa.py:17,36`；自然候选是 **二维 UPA DFT `U_M=F_y⊗F_z`**，不是未经说明的一维 16 点 DFT。DFT 是候选坐标，不意味着 off-grid 误差协方差必被它对角化。

`PartialDFTPilot` 包含随机列置换及相位；`phase_operator` 又对各用户加入不同跨帧相位。后者一般会破坏整个 `A0 A0ᴴ` 为标量单位阵的性质，不能用裸 partial-DFT 的理想 Gram 代替实际 `operator`。下文的小 `Q×Q` 求解不依赖这种理想性质。

## 2. 原文实际允许什么

### 2.1 标准 GEC 是投影后的矩匹配，不要求精确后验属于对角族

[Fletcher, Sahraee-Ardakan, Rangan, Schniter, *Expectation Consistent Approximate Inference: Generalizations and Convergence*, arXiv:1602.07795v2](https://arxiv.org/pdf/1602.07795v2)，PDF pp2–3，§II-A (6)–(12)、Algorithm 1；p4 (27)：

- `d(Q)` 为向量值对角化，包含逐元素、统一 trace 和 **block uniform diagonalization**。
- 原始 Algorithm 1 先形成 `Q_i = J_i Γ_i^{-1}`，再取 `η_i=1/d(Q_i)`；(12) 在 MMSE 情形把 scaled Jacobian 识别为条件协方差。
- 所匹配的是指定的一阶、二阶统计，非完整后验密度。

[Shastri et al., *Denoising Generalized Expectation-Consistent Approximation for MR Image Recovery*, 2022](https://arxiv.org/pdf/2206.05049v2)，本地 `18_shastri2022_dgec.pdf`：p13 (31)–(34)、Algorithm 2；p14 (35)–(36)、Algorithm 3；p16 (39)–(41)：

- 其 `gdiag` 将固定小波子带内 Jacobian 迹取平均；精度在同一子带内恒定，因而可以写成 `η_l=γ_l/α_l`。
- 线性模块是带对角精度的完整 Gaussian 解 (35)，随后做分组投影；不是先把 `BᴴB` 的非对角元删掉。
- corr+corr 可以把已知协方差的独立噪声样本作为网络条件，但它本身没有定义或估计外循环的 `C`。
- (36) 后明确说明各组 Gaussian 行为在其 MRI 实验中观察到，尚待严格分析。代数闭合不等于本 AFDM 具有 Gaussian 状态演化。

### 2.2 统一的闭合性判断

给定固定正交投影 `P_l`，满足 `P_l P_j=0(l≠j)`、`sum P_l=I`，设

\[
\Gamma=\sum_l\gamma_l P_l,\qquad C=\Gamma^{-1}=\sum_l\gamma_l^{-1}P_l.
\]

这个族在相同固定基和分组下对加法、减法、求逆闭合。正定性是另外一个条件：`η_l−γ_l` 必须为正，才可作为 proper Gaussian outgoing precision。线性 Gaussian 后验为

\[
P_A=(\sigma^{-2}B^HB+\Gamma)^{-1},\qquad
\hat x_A=P_A(\sigma^{-2}B^Hy+\Gamma r).
\]

`P_A` 通常不是组内白、组间独立；投影定义为

\[
\mathcal P(P_A)=\sum_l c_{A,l}P_l,\qquad
c_{A,l}=\operatorname{tr}(P_lP_A)/d_l,\quad d_l=\operatorname{tr}P_l.
\]

由于 `J_A=P_A Γ` 且 `ΓP_l=γ_lP_l`，

\[
\alpha_{A,l}=\operatorname{tr}(P_lJ_A)/d_l=\gamma_l c_{A,l},
\quad\eta_{A,l}=c_{A,l}^{-1},\quad
\Gamma_{out}=\mathcal P(P_A)^{-1}-\Gamma.
\]

这才是“同一表示”的准确含义：**精确模块估计 + 指定二阶矩投影 + 同族 Gaussian quotient**。并非线性后验精确对角。若输入误差真是独立 Gaussian、协方差声明正确、与观测噪声独立，线性步可得到相应组内平均误差方差；这些假设不能因为重复使用同一个观测就自动保留。

## 3. 候选 A：固定空间基的分组对角精度

### 3.1 空间轴候选的定义

以 `U_M=F_y⊗F_z` 或另一个**事先固定且有诊断支持**的空间酉基，固定分组 `G_g⊂{1,…,M}`。在变换坐标中设

\[
\operatorname{Cov}(e_{knr},e_{k'n'r'})
=\delta_{kk'}\delta_{nn'}\delta_{rr'}\,
U_M\operatorname{diag}(c_{k,g(s)})U_M^H.
\]

有两种合理粗细：

1. `c_g` 跨用户共享，参数数为 `G≤16`；组维度 `d_g=K Nin Nout |G_g|`。
2. `c_{k,g}` 逐用户，参数数为 `K G≤640`；组维度 `d_{k,g}=Nin Nout |G_g|`。

二者都是标准 GEC 的 fixed-group diagonalization。逐用户版本在代数上无需完整矩阵 GEC，但是**改变了矩匹配约束和外信息归一化**，不能称现有公共协方差模块的纯数据类型升级。

是否逐用户应由 query 的条件分布差异决定。若实际噪声在用户间相近，先共享可以减小估计波动；若差异明显，逐用户族是较低成本扩展。旧逐用户标量候选的负结果表明，用户特定方差本身不保证弱用户增益恢复。

### 3.2 线性模块只需 `Q×Q` 求解

对于一个空间模式 `s∈G_g` 和输出行 `r`，未知向量 `z_{s,r}∈C^(K Nin)`，令

\[
D_g=\operatorname{diag}(c_{k,g}\text{ repeated }N_{in}\text{ times}),\quad
S_g=\sigma^2I_Q+A_0D_gA_0^H.
\]

精确 Gaussian 线性估计为

\[
\hat z=m+D_gA_0^HS_g^{-1}(y-A_0m),\qquad
P_g=D_g-D_gA_0^HS_g^{-1}A_0D_g.
\]

同组所有空间模式和输出行共用 `S_g`；每轮最多 16 个 **16×16** 系统，可批量处理其右端。`diag(P_g)` 可以由 `A0` 列向量与 `S_g^{-1}` 精确计算，不必构造 640×640 的 `P_g`，也不必对线性模块用 Monte Carlo divergence。

逐用户投影为

\[
c_{A,k,g}=\frac1{N_{in}}\sum_{n=1}^{N_{in}}(P_g)_{(k,n),(k,n)}.
\]

共享用户时再对 `k` 平均。其他重复轴之所以消去，是因为**该线性工作模型**沿这些轴相同；非线性投影仍应对完整组的真实 Jacobian 求迹。

### 3.3 这里保留、丢弃了什么

- 保留：不同空间模式/组的噪声功率，必要时不同用户的噪声功率；物理天线域因此有空间有色 covariance。
- 丢弃：固定空间基内的非对角相关、不同 `Nin` 坐标之间的相关、不同 `Nout` 行之间的相关、跨用户相关、条件均值偏差、非 Gaussian 性。
- `G=16` 时每个空间模式一个精度，仍未保留模式间相关。它不等于每用户任意 16×16 covariance。
- D-GEC 的 MRI 组有测量矩阵近似组解耦的经验依据。空间模式在当前线性测量中确实解耦；但是**不同用户被同一个 `A0` 强烈混合**，用户分组没有同样的 MRI 依据。其代数允许性与统计有效性必须分别报告。

## 4. 候选 B：每用户完整 16×16 天线矩阵

设

\[
V=\operatorname{blockdiag}_{k,n}(C_k),\quad C_k\in\mathbb H_{++}^{M},
\]

沿 `Nout` 重复。该族对求逆和同块精度相减闭合，即不需要先同时对角化所有 `C_k`。但是当 `C_k` 不共用特征向量时，不能沿空间模式解耦，当前 `SpatialLinear` 的公共 `eigh(C)` + SVD 路径不能直接使用。

利用 Woodbury，仍只需每轮一个 `QM×QM=256×256` 系统：

\[
S=\sigma^2I_{QM}+BVB^H
=\sigma^2I_{QM}+\sum_k(A_kA_k^H)\otimes C_k,
\]
\[
\hat x=m+VB^HS^{-1}(y-Bm),\quad
P=V-VB^HS^{-1}BV.
\]

无需求逆 10240×10240。线性投影取每个用户的对应 `M×M` 对角块平均：

\[
\bar P_k=\frac1{N_{in}}\sum_n P_{(k,n),(k,n)}.
\]

外信息为

\[
\Gamma_{out,k}=\bar P_k^{-1}-C_k^{-1},\quad
r_{out,knr}=\Gamma_{out,k}^{-1}
(\bar P_k^{-1}\hat x_{knr}-C_k^{-1}r_{knr}).
\]

**非线性模块的配套二阶量不同了。** 在列向量 Jacobian 约定下，定义

\[
\bar J_k=\frac1{N_{in}N_{out}}\sum_{n,r}
\frac{\partial D_{knr}}{\partial r_{knr}^{T}}\in\mathbb C^{M\times M}.
\]

若 `D` 是该 proper Gaussian query 的 MMSE 均值，则

\[
\bar P_{D,k}=\bar J_k C_k,\qquad\eta_k=\bar P_{D,k}^{-1}.
\]

这里是**先乘输入 covariance 再求矩阵逆**；不能元素相除，也不能任意交换为 `C_k Jbar_k`。需要保留全部空间交叉偏导。对不精确的网络，`Jbar C_k` 不保证 Hermitian/正定；如何投影、稳定化必须定义为额外算法操作，不能援引 MMSE 恒等式宣称已经保证。

这是基于 EC/EP Gaussian 代数，把二阶约束扩展为矩阵块矩的方案；本文不把它冒称为 D-GEC 原文 Algorithm 2 已定义的接口。它与 Kunde 的 MMV 256×256 Onsager 又是不同对象：这里矩阵轴仅为天线 `m`，并对 `(n,r)` 取部分迹。

每个 16×16 complex Hermitian 矩阵有 256 个实自由度，40 用户共 10240 个；这显著多于 `G=16` 逐用户对角族的 640 个精度。相应噪声统计估计、训练覆盖与敏感度估计都要有足够证据支持。若主要残差结构是 `Nin` 相关，增加空间矩阵自由度可能完全没有对准问题。

## 5. 候选 C：输入列与天线的 Kronecker 或块结构

### 5.1 自由单一 Kronecker 乘积不闭合

假设用户内每个输出行的 covariance 是 `T_k⊗S_k`，两因子都可随模块更新。虽然求逆仍为 Kronecker 乘积，但 quotient 要求

\[
\Gamma_{out,k}=T_{post,k}^{-1}\otimes S_{post,k}^{-1}
-T_{in,k}^{-1}\otimes S_{in,k}^{-1},
\]

一般是两个乘积的差，不是一个乘积。即使所有因子都为对角阵也不闭合：

\[
\operatorname{diag}(3,4)\otimes\operatorname{diag}(2,3)
-\operatorname{diag}(1,2)\otimes I_2
=\operatorname{diag}(5,8,6,10).
\]

对应二维特征值表 `[[5,8],[6,10]]` 行列式为 2，非 rank one，无法写成单一两个 2×2 对角因子的 Kronecker 乘积；输出 covariance 的倒数表同样不可分。若另做低 Kronecker-rank 拟合，投影与 quotient 次序不再可互换，需要新目标和新算法说明。

**例外：一个因子事先固定且两模块完全相同。** 例如 `C_k=T0_k⊗S_k`，固定正定 `T0_k`，精度相减保持该固定因子。可在 `T0_k^{-1/2}` 坐标内转为候选 B 的重复空间矩阵，但线性算子、先验模块、噪声生成、投影都须同步变换。不能把估计的物理信道 covariance 随意放入 `T0_k` 当作噪声因子。

### 5.2 固定 tensor 酉基 + 任意二维方差表可以闭合

固定用户内部 `U_in` 和空间 `U_M`，用

\[
C_k=(U_{in}\otimes U_M)
\operatorname{diag}(c_{k,a,s})
(U_{in}\otimes U_M)^H
\]

并沿 `Nout` 重复，允许二维方差表任意取正值，而不强制 `c_{k,a,s}=t_{k,a}s_{k,s}`。这是 fixed-basis diagonal family，**仍是标准 GEC 分组精度**，可以对 `a,s` 分组降低参数数。

变换后 `A'_k=A_k U_in`，每个空间模式仍只需 `Q×Q` 求解；`D_s` 现在可沿 `(k,a)` 不同。代价主要来自更多分组的非线性敏感度、统计估计和训练噪声族，而不必然是线性大矩阵求逆。最细粒度是 `K Nin M=10240` 个标量精度，但每个单元只重复 `Nout=16` 次，统计量可能很不稳定。

固定 `U_in` 应由已保存 query 中跨输入列的中心误差结构决定。AFDM 信道有结构，不等于**query error** 在任意输入 DFT 基对角。不能仅据 clean channel 的能量图选择噪声分组。

### 5.3 固定输入分组 + 每组完整空间块也闭合，但需要矩阵接口

在固定 `U_in` 基中设 covariance 为 `blockdiag_a(C_{k,g(a)})`，沿 `Nout` 重复。同一固定块划分下，逆和精度相减闭合；这是候选 B 对输入坐标再分组的扩展。线性观测域仍为 256 维，非线性部分则需每个输入组一个 `M×M` Jacobian 部分迹。

若进一步使用每用户完整 `Nin M × Nin M =256×256` covariance，Gaussian quotient 也闭合，但自由度变为每用户 65536 个实参数；非线性敏感度和训练覆盖显著增加。并且在当前 `Q=Nin=16`、用户块满秩时，完整用户块 cavity 的线性均值退化为

\[
r_k=(A_k^{-1}\otimes I_M)
\left(y-\sum_{j\ne k}(A_j\otimes I_M)m_j\right),
\]

其均值不再利用干扰 covariance 权重，且可能放大噪声。因此完整用户块不应被预设为性能上界。

## 6. 不能省略的接口条件

1. **固定族与动态换基不同。** 每轮按当前残差重新选特征基，两个输入/输出 precision 往往不在同一对角族。重新对角化或删去非对角元都是新增投影；若基依赖网络输入，敏感度还涉及该选择，不能直接沿用 fixed `gdiag` 的意义。候选 B 在固定物理坐标保留完整矩阵时可以容纳旋转，但应使用矩阵接口。
2. **不要为对角化 `A0ᴴA0` 混合用户。** `A0` 的完整右奇异基一般混合不同用户；回到物理域的噪声会跨用户相关。此时逐用户两网络通常不再给出匹配的联合先验均值/活动证据。第一阶段应把固定变换限制在用户内部，保留活动块。
3. **对完整去噪映射求敏感度。** 若两网络输出 active-conditioned `μ` 与 `p`，则 `D=pμ`，导数包括 `p ∂μ + μ ∂p`，也包括 classifier 经由 first 特征的链式项。若 denoiser 已直接训练成含零用户的联合均值，则不能再乘一次 `p`。两个定义必须先固定。
4. **corr+corr 的辅助噪声在求导时固定。** 求当前 `D(r;C,Naux)` 对 `r` 的导数时，`C`、分组/基、辅助噪声样本均固定；否则差分混入额外随机噪声。网络所见 `Naux` 与真实 query 噪声应条件独立且具有相同 covariance。独立样本只编码 `C`，不会消除 query 的条件偏差或信号依赖。
5. **复实归一化必须明确。** Proper complex 方差 `c` 对应每个实/虚分量方差 `c/2`。标量分组敏感度可用实表示的 `2d` 维平均迹，等价于 `Re tr(J_Wirtinger)/d`；矩阵块则按 consistent complex derivative 恢复 Hermitian covariance。不要把论文实值 `γ` 与当前 complex variance 不经换算混用。
6. **activity 使用同一噪声条件。** 正负类应共享 `C` 采样律；训练条件和推断模块必须一致。使用全空间矩阵或 tensor 组后，不能继续给 activity 只提供 `trace(C)` 并宣称已经匹配。
7. **阻尼也受族约束。** 固定分组的 covariance/precision 参数插值仍在族内，但插值 covariance、插值 precision 和真实跨轮误差 covariance 是不同操作。自由单一 Kronecker 族甚至通常不对这种插值闭合。

## 7. 建议与适用条件

| 族 | Gaussian quotient | 线性后验返回方式 | 是否沿用 D-GEC scalar `gdiag` | 建议 |
|---|---|---|---|---|
| 固定空间酉基，组内标量，用户共享或逐用户 | 同族闭合；还须正精度 | 完整 `Q×Q` 解 + 对应组平均方差 | 是；fixed coordinate transform + fixed groups | 保留作空间轴比较；新诊断后的当前初候选见第9节 |
| 每用户任意 16×16 空间 covariance，沿输入列/输出行重复 | 同块闭合 | `QM×QM` 解 + 对角空间块平均 | 否；需矩阵块敏感度和矩阵 quotient | 固定空间基不能解释显著相关性，且相关主要在天线轴时再升级 |
| 自由 `T_k⊗S_k` | 一般不闭合 | 额外 Kronecker 拟合；顺序敏感 | 否，不能直接替换 | 不建议作为初始接口 |
| 固定 `U_in⊗U_M`，任意二维方差表 | 同族闭合 | `Q×Q` 解 + 固定 tensor groups 投影 | 是 | 当 `Nin` 方向确有可压缩误差结构时，是比自由 Kronecker 更清楚的扩展 |
| 固定输入分组，每组完整空间块 | 同块闭合 | `QM×QM` 解 + 矩阵块投影 | 否 | 只有空间/输入两类证据都支持时考虑 |
| 每用户完整 256×256 块 | 同块闭合 | 完整用户 marginal | 否；更高维敏感度 | 主要作代数参考；注意平方块无偏均值退化 |

**在尚无轴向诊断时的最小充分起点**不是预先认定哪个坐标一定白，而是先把一个可以实现、投影明确的 family 固定下来，再问它能解释多少已有 query 的中心误差：可比较 scalar、固定 UPA 空间基分组（共享/逐用户）、每用户完整空间 covariance 三者。第 9 节的新证据已表明本次样本的显著误差落在 `Nin` 轴，应相应调整优先级。不要同时引入自由特征基、逐用户矩阵、两因子 Kronecker 拟合和跨轮自适应，以致无法区分改善来自何处。

是否采用更复杂族的关键证据包括：固定基内的非对角残差、被投影丢弃的跨输入/输出坐标相关、用户间差异、组方差可预测性，以及控制 covariance 后仍存在的条件均值偏差/信号相关。仅以 `||C_hat−vI||` 大就选择全矩阵不充分；若主因是 `r≈G H+e` 的增益失配，任何零均值 `C` family 都无法单独修复。

## 8. 小维确定性代数核验

使用 NumPy complex128，仅构造 `Q=2,K=2,Nin=2,M=2` 的矩阵，没有加载模型或场景：

\[
A=\begin{bmatrix}1&.4+.2i&-.3+.1i&.7\\.2-.1i&1.1&.5+.3i&-.4+.1i\end{bmatrix},
\quad C_0=\begin{bmatrix}1&.2+.1i\\.2-.1i&.7\end{bmatrix},
\quad C_1=\begin{bmatrix}.6&-.1+.16i\\-.1-.16i&1.3\end{bmatrix},\quad\sigma^2=.4.
\]

取 `B=A⊗I2`、`V=blockdiag(C0,C0,C1,C1)`、`P=(V^{-1}+BᴴB/.4)^{-1}`、`J=P V^{-1}`。按第 4 节投影：

- 两用户 `||Jbar_k C_k−Pbar_k||_F` 分别为 `1.79e−16`、`1.12e−16`。
- 错序 `||C_k Jbar_k−Pbar_k||_F` 分别为 `0.02675`、`0.03089`，证实不能交换矩阵顺序。
- 两用户 outgoing precision 最小特征值约 `1.09076`、`0.38079`。
- 完整 `P` 与重复空间块投影的相对 Frobenius 差约 `0.51991`：即使工作模型完全 Gaussian，精确后验也通常不在该简化族内。
- 第 5.1 节 Kronecker 反例二维精度表行列式数值为 `1.9999999999999927`，与解析值 2 一致。

这些仅验证代数与实现约定，不提供 AFDM 性能或误差分布证据。

## 9. 新诊断后的具体初候选：公开用户输入基下的 16 个精度

本节使用父任务独立完成的 48 条件 × 3 阶段离线 mode-Gram 结果；我没有重复运行该分析。以下为事后机制诊断，不是新候选接收机的性能结果。

- uniform −4 dB final，active/inactive 输入列原基非对角平方和占比中位数约 `0.4715/0.4914`，普通输入 DFT 仍为 `0.4444/0.4622`；相同样本的天线轴约 `0.0847/0.0902`、输出行轴约 `0.0973/0.0971`。
- 仅从公开 `A_kᴴA_k` 取特征基 `V_k`，固定于整个 case，输入列非对角占比降为 final `0.0285/0.0274`，首轮 `0.0530/0.0626`，第 20 轮 `0.0711/0.0732`。0 dB 首轮、20 轮、final 对应约 `0.1106/0.1274`、`0.0962/0.1003`、`0.0291/0.0276`。
- 公开 `A_kᴴ(AAᴴ)^{-1}A_k` 基部分中间轮更好，但 final 约 0.037，弱于前者。不能据此跨多个候选事后挑最佳基而宣称独立验证。
- 早期空间非对角占比仍明显，首轮约 0.51，UPA DFT 后约 0.34；输入基 alone 不足以宣称每一轮都满足完整匹配 Gaussian 模型。

`0.028` 不表示“比 AWGN 更白”。16 维、256 个独立样本、各向同性 Gaussian 的有限样本参考约 0.055；非均匀对角谱的参考会降低。对 `S` 个 proper Gaussian 样本，未中心化样本 covariance 的期望能量之比近似为

\[
\frac{\mathbb E\sum_{i\ne j}|\widehat C_{ij}|^2}
{\mathbb E\|\widehat C\|_F^2}
=\frac{d_{eff}-1}{S+d_{eff}},\quad
d_{eff}=\frac{(\operatorname{tr}C)^2}{\operatorname{tr}C^2}
\]

（这里真实 `C` 在该基中对角，且样本独立）。这是“期望之比”，不声称等于逐样本比值的期望；当前物理误差的重复坐标也未证明独立。恰当比较需要保留估计的对角谱、采用一致的中心化及样本处理。

### 9.1 公开算子给出的局部右奇异基，可以使用标准 GEC

令 `A_kᴴA_k=V_k Λ_k V_kᴴ`，`V_k` 是完整 `Nin×Nin` 酉矩阵。用它定义

\[
T_k=V_k\operatorname{diag}(\tau_{k1},\ldots,\tau_{kN_{in}})V_k^H,
\qquad C_k=I_M\otimes I_{N_{out}}\otimes T_k.
\]

该式按网络物理展平 `(m,r,n)` 排列。变换坐标逐分量为

\[
z_{kmrj}=\sum_n(V_k)_{nj}^{*}H_{kmrn},\qquad
\widetilde A=[A_1V_1,\ldots,A_KV_K].
\]

不同用户只在其**用户内部**换基，不混合活动块。每个 `(k,j)` 是一个 GEC 组，沿 `(m,r)` 共享精度，组大小为 `M Nout=256`；共 `K Nin=640` 个标量参数。`V_k` 可以随**公开测量问题**改变，但在该 case 的整个推断过程中固定。这不同于按当前 query/error 逐轮重估基：对给定测量问题，它仍是固定坐标、固定分组的标准 `gdiag`。

值得注意，已知用户跨帧相位满足 `A_k=D_k P_k`、`D_kᴴD_k=I`，所以 `A_kᴴA_k=P_kᴴP_k`。这个局部输入基不受该用户跨帧相位斜率影响，不需要真实信道或误差。特征向量相位及重根子空间仍有规范不唯一；实现需固定确定性约定，或让 covariance/噪声条件与任何所选约定同步。接近重根时不能把单独特征向量解释成唯一物理方向。

### 9.2 线性更新、组迹和 quotient 的完整公式

对每个 `(m,r)` 有 `y=Ã z+w`。令 `D=diag(τ_{kj})`，输入消息均值为 `r_z`，则

\[
S=\sigma^2I_Q+\widetilde A D\widetilde A^H,
\]
\[
\hat z=r_z+D\widetilde A^HS^{-1}(y-\widetilde A r_z),
\qquad P=D-D\widetilde A^HS^{-1}\widetilde A D.
\]

每轮只解一个 **16×16** `S`，对全部 `M Nout=256` 个右端复用。设 `\tilde a_i` 是第 `i=(k,j)` 列，线性组投影为

\[
p_i=P_{ii}=\tau_i-\tau_i^2\tilde a_i^HS^{-1}\tilde a_i,
\qquad\alpha_{A,i}=p_i/\tau_i.
\]

因为线性工作模型对 `(m,r)` 相同，不需要 MC 估计这一步。设 `γ_i=1/τ_i`，则

\[
\eta_{A,i}=1/p_i,\quad\gamma_{out,i}=\eta_{A,i}-\gamma_i,
\quad r_{out,i,m,r}=
\frac{\eta_{A,i}\hat z_{i,m,r}-\gamma_i r_{z,i,m,r}}{\gamma_{out,i}}.
\]

`γout` 仍是同一基、同一组的标量精度，故 representation 对 Gaussian quotient 闭合。这里的投影丢弃了 `P` 的跨输入模式和跨用户非对角块，绝非声称完整后验已经对角。

非线性模块在物理坐标工作亦可：把 `r_out` 变回 `R_H`，用该 `C_k` 生成匹配辅助噪声，得到完整联合均值 `D_H`，再变换为 `D_z`。其组敏感度是

\[
\alpha_{D,kj}=\frac1{M N_{out}}\operatorname{Re}
\sum_{m,r}\frac{\partial (D_z)_{kmrj}}{\partial (R_z)_{kmrj}},
\qquad \eta_{D,kj}=\gamma_{in,kj}/\alpha_{D,kj}.
\]

复偏导与实表示归一化遵循第 6 节；对完整 `D=pμ` 求导，固定 `V_k,γ,Naux`。这是 D-GEC `gdiag` 的输入模式分组版本，不要求计算 16×16 的所有跨模式导数，也不需要原 second 网络预测完整 covariance。

网络的 covariance 条件可以通过物理域独立噪声实现：对每个 `(m,r)` 独立抽 `ξ∼CN(0,I_Nin)`，形成 `n_aux=V_k diag(sqrt(τ_k)) ξ`。其 covariance 就是 `T_k`。即使两个不同公开算子产生不同 `V_k`，corr+corr 的输入仍在同一个物理信道坐标中；训练需要覆盖相应的 covariance 家族。该条件样本并不保证网络能够有限样本精确辨识 `T_k`，更不保证实际 query 噪声属于这族。

### 9.3 为什么当前 query 的输入列 covariance 可能接近此基

可从**一次未施加 moment damping 的当前 isotropic `linear.update`** 推出工作模型结论。用 `c` 表示公共输入 covariance 标量，令

\[
S=\sigma^2I_Q+c A A^H,\quad
\beta=\frac{c}{K N_{in}}\operatorname{tr}(A^HS^{-1}A),\quad
F=\frac c\beta A^HS^{-1}.
\]

当前 query 为 `r=m+F(y−Am)`。设 `δ=m−x`，则

\[
r-x=(I-FA)\delta+Fw.
\]

若仅为计算这一步，假设 `δ` 零均值、covariance 为 `cI`，并与观测噪声独立，则其**完整**误差 covariance 恰为

\[
C_r=cI+c^2(\beta^{-2}-2\beta^{-1})A^HS^{-1}A.
\]

所以第 `k` 个用户的 marginal 为

\[
(C_r)_{kk}=cI_{N_{in}}
+c^2(\beta^{-2}-2\beta^{-1})A_k^HS^{-1}A_k.
\]

即使消息只传一个标量，有限矩阵上的实际工作模型 marginal 一般已有明确的输入列 covariance 结构。其精确特征基是 `A_kᴴS^{-1}A_k` 的基，而非无条件地等于 `A_kᴴA_k` 的基。

- 若 `σ²I` 主导 `c AAᴴ`，或 `AAᴴ≈λI`，则 `S^{-1}` 近似标量，得到 `V_k` 基。前者与低 SNR 下的解释相容，但当前 trace/calibration 本身尚不能证明这个近似有多好。
- 若 `c AAᴴ` 主导且满行秩，`A_kᴴ(AAᴴ)^{-1}A_k` 成为另一个极限基。这解释了为何后者可作为公开对照，但并不说明它对所有迭代更好。
- 一般 `A_kᴴ(σ²I+c AAᴴ)^{-1}A_k` 随 `c` 改变；若每轮动态使用其基，就不再是本节固定 `gdiag` 方案。先采用公开、整次固定的 `V_k` 是有意的模型约束，误差须由诊断检验。

若真实反馈误差 covariance 为 `C_δ`，与观测噪声的 cross-covariance 为 `T=Cov(δ,w)`，准确表达式还包括

\[
C_r=(I-FA)C_\delta(I-FA)^H+\sigma^2FF^H
+(I-FA)TF^H+FT^H(I-FA)^H.
\]

均值偏差与 query 跨轮 damping 另外改变统计。上述 covariance 计算本身甚至不要求 `δ` 与信号 `x` 独立，所以即使它精确，也不能推出 `r−x` 与 `x` 独立；零初始化 `m=0` 给出 `δ=−x` 就是直接例子。因而上面的 `A_kᴴS^{-1}A_k` 推导是工作模型解释，不能倒推出当前实际 final query 已经独立 Gaussian。

### 9.4 与完整输入列 16×16 矩阵比较

若每用户保留任意 `T_k∈H++^(Nin)`，沿 `(m,r)` 重复，则线性模块仍只需 `Q×Q`：

\[
S=\sigma^2I+\sum_k A_kT_kA_k^H,
\quad P_{kk}=T_k-T_kA_k^HS^{-1}A_kT_k.
\]

Gaussian quotient 对任意输入块矩阵闭合，但非线性二阶量要改为 `(m,r)` 上平均的完整 `Nin×Nin` Jacobian 块乘 `T_k`；它已经超出 scalar `gdiag`。线性成本较小不代表接口和统计成本也小。

更关键地，保留完整 `P_kk` 并做精确 quotient，在 `Q=Nin`、`A_k` 满秩时就已得到

\[
r_{out,k}=A_k^{-1}\left(y-\sum_{j\ne k}A_jm_j\right),
\quad C_{out,k}=A_k^{-1}S_{-k}A_k^{-H},
\quad S_{-k}=\sigma^2I+\sum_{j\ne k}A_jT_jA_j^H.
\]

**不需要升至 256×256 全块才出现该退化。** 每用户完整 16×16 输入列块已经足够。固定 `V_k` 的对角投影则没有施加完整用户块无偏条件，仍保留分组 GEC 近似，因此不是这个直接逆的同义写法。结合公开基对当前离线样本的较好拟合，固定谱族是更合理的初始候选。

### 9.5 空间扩展和仍待验证的事项

若早期空间相关影响实质性能，可扩展为固定分析坐标

\[
z_{kbrj}=\sum_{m,n}(U_{sp})_{mb}^{*}(V_k)_{nj}^{*}H_{kmrn},
\qquad\operatorname{Var}(e_{kbrj})=\tau_{kbj},
\]

其中 `Usp` 固定（例如 UPA 二维 DFT），每个 `(k,b,j)` 的精度沿 `Nout` 重复。二维表 `τ_kbj` 不要求分解成空间因子乘输入因子，因此仍对 quotient 闭合。每个空间模式/组一个 `Q×Q` 系统；可以合并空间模式减少参数和敏感度估计方差。完整不合并时每组只有 16 个输出行，统计条件明显弱于输入谱族的每组 256 个坐标。

目前可以支持“公开局部输入基值得作为最小候选”，尚不能支持：

1. 该基在独立场景、其他 SNR、用户数、导频数和新候选产生的 query 中保持相同解释力；
2. 16 个模式方差能由 GEC 组迹准确追踪，而非仅事后从真值拟合；
3. 固定基下 off-diagonal 小就意味着模式/天线/输出行独立、Gaussian，或误差与信号独立；
4. early 空间相关可忽略，或者固定 UPA-DFT + 二维谱足以覆盖；
5. 新两网络经过独立噪声族训练后能在闭环降低低 SNR 漏检；
6. 更细的分组必然更优，或完整输入矩阵优于对角谱。

因此建议初始数学接口固定为 `C_k=I_M⊗I_Nout⊗V_k diag(τ_k) V_kᴴ`，把 `Usp` 与二维谱作为明确的扩展条件；先验证组迹、实际误差与训练噪声条件是否一致，再决定是否增加空间自由度。
