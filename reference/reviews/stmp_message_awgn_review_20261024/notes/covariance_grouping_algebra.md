# 固定公开输入基的分组 GEC：独立代数复核

2026-10-24。按 academic-research-suite 作有界复核；仅公式与已有原文核对，未运行网络、接收机或新实验。

**结论：粗分组保留不同模式的自身增益，以较弱的组平均矩匹配约束换取较小的工作误差；逐模式校正为单位自身增益会精确回到 fine 查询，噪声放大也一同返回。** 首轮分组查询在保留缩放元数据时含有相同信息，不等于冻结网络有相同效果。

## 记号与工作模型

令 \(n=KN_{\rm in}=640\)，重复列数 \(T=MN_{\rm out}=256\)。固定公开基
\(A_k^HA_k=V_k\Lambda_kV_k^H\)，模式按 \(\Lambda_k\) 升序排列，\(B=[A_1V_1,\ldots,A_KV_K]\)。
对单个重复列采用**固定系数辅助模型**

\[
y=Bz+w,\quad z\sim\mathcal{CN}(0,\nu I),\quad
w\sim\mathcal{CN}(0,\sigma^2I),\quad z\perp w,
\]
\[
S=\sigma^2I+\nu BB^H,\quad H=\nu B^HS^{-1}B,\quad
h_i=H_{ii},\quad f=\nu B^HS^{-1}y .
\]

此处 \(H\) 是响应矩阵，不是物理信道。后验协方差为 \(P=\nu(I-H)\)。
分区 \(\mathcal P\) 中 \(d_g=|g|\)、\(h_g=d_g^{-1}\sum_{i\in g}h_i\)，\(D_{ii}=h_{g(i)}\)。
后验组平均方差 \(v_g=\nu(1-h_g)\) 与初始 prior 作 Gaussian quotient：

\[
\gamma_{2,g}=v_g^{-1}-\nu^{-1}
=\frac{h_g}{\nu(1-h_g)},\qquad
r_i=\frac{v_g^{-1}f_i}{\gamma_{2,g}}=\frac{f_i}{h_g},
\qquad \tau_g=\nu\frac{1-h_g}{h_g}.
\tag{1}
\]

各组沿相同的 \(T\) 个重复列使用同一精度，组迹平均中的共同倍数 \(T\) 消去。以下假设涉及的 \(h_i,h_g>0\)。

## 1. 自身模式增益

\[
r=D^{-1}Hz+\nu D^{-1}B^HS^{-1}w,\qquad
a_i=(D^{-1}H)_{ii}=\frac{h_i}{h_g}.
\tag{2}
\]

因此组平均 \(d_g^{-1}\sum_{i\in g}a_i=1\)，但一般不是逐模式为 1。\(a_i\) 只描述自身模式，完整响应还含 \(H_{ij}/h_g\)。即使单模式成组，完整响应 \(D^{-1}H\) 仍一般不等于 \(I\)；其秩至多为 \(Q<n\)。

## 2. 工作误差对角：标签只匹配组平均

由 \(\operatorname{Cov}(f)=\operatorname{Cov}(f,z)=\nu H\)，

\[
C_e=\operatorname{Cov}(r-z)
=\nu[I+D^{-1}HD^{-1}-D^{-1}H-HD^{-1}],
\]
\[
q_i=(C_e)_{ii}
=\nu\left(1-\frac{2h_i}{h_g}+\frac{h_i}{h_g^2}\right),
\qquad
\frac1{d_g}\sum_{i\in g}q_i=\nu(1/h_g-1)=\tau_g.
\tag{3}
\]

逐模式误差与组标签的差为
\(q_i-\tau_g=\nu(h_i-h_g)(1-2h_g)/h_g^2\)。
同时

\[
\operatorname{Cov}(r-z,z)=\nu(D^{-1}H-I).
\tag{4}
\]

粗组只使该交叉协方差的组平均对角为零；fine 只使每个对角为零，跨模式项仍可能非零。组平均方差匹配不证明完整误差独立于信号，也不证明各轴独立。式 (3) 的二阶矩恒等式只需相应二阶矩与信号/测量噪声不相关；Gaussian 分布解释需要更多条件。

## 3. 分组细化使平均标签不降的条件

按模式数加权，
\[
\overline\tau(\mathcal P)
=\nu\left(\sum_g\frac{d_g/n}{h_g}-1\right).
\]

在**同一 \(B,\nu,S,h_i\)** 下，若 \(\mathcal P'\) 是 \(\mathcal P\) 的嵌套细化，父组 \(g\) 的子组权重 \(w_{c|g}=d_c/d_g\)，则 \(h_g=\sum_cw_{c|g}h_c\)。由 \(1/x\) 凸，

\[
\overline\tau(\mathcal P')-\overline\tau(\mathcal P)
=\nu\sum_g\frac{d_g/n}{h_g^2}
\sum_{c\subseteq g}w_{c|g}\frac{(h_c-h_g)^2}{h_c}\ge0.
\tag{5}
\]

等号当且仅当每个父组的所有子组均值相同。故全局 scalar 与每用户连续等长 1/2/4/8/16 组满足

\[
\overline\tau_{\rm global}\le\overline\tau_{\rm user,1}
\le\overline\tau_{\rm user,2}\le\overline\tau_{\rm user,4}
\le\overline\tau_{\rm user,8}\le\overline\tau_{\rm user,16}.
\tag{6}
\]

对折四组 \([0,7,8,15],[1,6,9,14],[2,5,10,13],[3,4,11,12]\) 只直接满足
\(\overline\tau_{\rm user,1}\le\overline\tau_{\rm fold,4}\le\overline\tau_{\rm user,16}\)。
它与连续 2/4/8 组一般不嵌套，不能由式 (5) 排序。
按 \(A_k^HA_k\) 特征值排序也不自动等于按 \(h_i=\nu b_i^HS^{-1}b_i\) 排序，因为后者还受左方向及全体用户构成的 \(S^{-1}\) 影响。

这只比较固定首轮的算术平均标签及相应工作模型期望 MSE，不保证中位数、单个活跃子群、单场景实际 MSE或后续迭代的排序；后续分组改变网络输出和 \(S\) 后，前提不再相同。

## 4. 校正自身增益必然返回 fine

工作模型下可写成
\[
r_i=a_i z_i+\zeta_i,\qquad
\operatorname{Var}(\zeta_i)=\frac{\nu h_i(1-h_i)}{h_g^2},
\tag{7}
\]
其中 \(\zeta_i\) 包含其他模式和热噪声，与自身 \(z_i\) 独立，但不必与整个信号或其他 \(\zeta_j\) 独立。这不是纯物理热噪声方差。

于是
\[
q_i=\nu(a_i-1)^2+\operatorname{Var}(\zeta_i),\qquad
\frac{r_i}{a_i}=\frac{f_i}{h_i},\qquad
\frac{\operatorname{Var}(\zeta_i)}{a_i^2}
=\nu\frac{1-h_i}{h_i}.
\tag{8}
\]

查询恒等式对任意实际 \(y\) 都成立，不依赖工作模型。增益校正后所有真实查询误差也返回 fine 值，不能仍使用粗组较小的 \(\tau_g\) 宣称“单位增益且免费降噪”。

若保留不同 \(a_i\) 并训练网络，应配套考虑增益、相对该增益的误差与活动 likelihood。只使用 \(z+\mathcal{CN}(0,\tau_gI)\) 训练，不能由组平均式 (3) 保证匹配。若仍按标准 GEC 组投影运行，则其消息分布近似性需另外验证。

## 5. 相同信息与不同网络效果并不矛盾

任意两分区在同一首轮满足
\[
r^{\mathcal Q}=D_{\mathcal Q}^{-1}D_{\mathcal P}r^{\mathcal P}.
\tag{9}
\]

正组均值下这是已知可逆缩放。因此**保留必要缩放元数据的查询接口**互为可逆表示；单纯缩放不创造新活动信息。此处不需额外宣称 \(f\) 保留了 \(Y\) 的全部信息。

训练分布、网络容量、归一化、提供的元数据、有限精度和后续闭环均可改变实际效果。冻结 AWGN 网络一般不对任意模式缩放等变；只给组平均 \(\tau_g\) 也不等于给出了所有 \(a_i\) 和交叉协方差。

## 限制与最小正确验证

- **观测依赖噪声估计：** 当前 \(\widehat\sigma^2=\widehat\sigma^2(Y)\)。式 (9) 对同一个 \(Y\) 仍逐点成立，但信息等价应保留 \(B,\nu,\widehat\sigma^2(Y)\) 等缩放元数据，裸 \(r\) 不自动可逆。统计恒等式应解释为“将选定系数冻结后的辅助模型”；条件于 \(\widehat\sigma^2(Y)\) 不会自动恢复原始信号/噪声独立性，不能据此宣称真实条件或无条件协方差已被算准。
- **实际信道：** 固定系数但真实协方差为 \(\Sigma_z\) 时，记 \(L=\nu D^{-1}B^HS^{-1}\)，零均值独立信号/噪声下真实误差为 \((LB-I)\Sigma_z(LB-I)^H+\sigma_w^2LL^H\)。空间相关、活动条件或非零条件均值都可能使式 (3) 失去真实校准含义。
- **数值边界：** 父任务修正版 80000 用户条件记录按 \(16\epsilon s_{\max}\) 的 SVD 阈值均为 rank 16，最大条件数约 \(1.94\times10^{14}\)；不能说已观察到精确 null 或该标准的数值秩亏。极端近奇异块存在 Gram 小特征值/基的有限精度敏感性。理论 \(h_i=0\) 时 fine 外信息精度应为 0、方差无穷，不能除以 \(a_i=0\)；这只是边界，并非本次已观测事实。设 floor 会改变算法与上述精确式。
- **最低指标：** 同系数保存并比较 \(h_i,h_g,a_i,\tau_g,q_i\)，验证嵌套平均关系；报告实际绝对 MSE、模式误差、活跃/不活跃分层与场景配对结果；把增益/信号交叉项、跨模式及其他轴相关与误差功率分开。检查粗组增益校正后是否逐元素返回 fine；任何 floor/截断都须另标。较小标签或归一化误差接近 1 均不能代替真实误差与网络评价。

上述指标并非本笔记新执行的实验。现有结果及噪声版本更正见[父任务验证报告](../../../../paper/STMP/docs/STMP_COVARIANCE_VALIDATION_20261024.md)。

## 原文定位与外推边界

1. Fletcher, Sahraee-Ardakan, Rangan, Schniter，*Expectation Consistent Approximate Inference: Generalizations and Convergence*，[作者稿 v2](https://arxiv.org/pdf/1602.07795v2)，PDF pp. 2–3，§II-A 原式 (6)–(9) 的 diagonal/uniform/block-uniform diagonalization、Algorithm 1 的精度差和自然参数差；原式 (12) 的 MMSE 导数与协方差关系；p. 4 原式 (27) 的矩匹配。支持分组投影与式 (1)，不保证任意固定 AFDM 分组的独立 Gaussian 误差。
2. Shastri, Ahmad, Metzler, Schniter，*Denoising Generalized Expectation-Consistent Approximation for MR Image Recovery*，[作者稿 v2](https://arxiv.org/pdf/2206.05049v2)，[本地 PDF](../../../literature/shastri2022_dgec.pdf)：p. 13 Algorithm 2、原式 (31) 为组迹/组大小，原式 (34) 为组内相同精度；p. 14 Algorithm 3、原式 (35) 为对角 prior 精度下的线性更新，原式 (36) 的子带 Gaussian 模型有实验与理论分析边界；p. 16 原式 (39)–(41) 以已知协方差构造配套噪声输入。不能把 MRI 小波组的经验有效性转写为当前输入列分组的保证。
3. Cheng, Liu, Liang, Manton, Ping，*Orthogonal AMP for Problems with Multiple Measurement Vectors and/or Multiple Transforms*，2023，[作者稿 v1](https://arxiv.org/pdf/2304.08038v1)，[本地 PDF](../../../literature/cheng2023_oamp_mmv.pdf)：pp. 4–5 §III-B 原式 (14)–(16) 同时保留 GS 增益 \(\Theta\) 与误差协方差 \(\Sigma\)；p. 5 原式 (17)–(18)、p. 6 原式 (27)–(30) 追踪两者。p. 6 §III-F Definition 20、原式 (31)–(34) 的矩阵 Gram–Schmidt orthogonalization 不等于强制 \(\Theta=I\)。pp. 5–6 Assumption 18、Theorem 19 的 Gaussian 结论要求 Haar 变换及相应估计器和大系统条件；公开特征基与有限维组迹恒等式不证明这些条件。本文自身系数 \(a_i\) 也不自动等同于论文按 MMV 轴定义的完整 \(\Theta\)。

以上均为所列作者稿 PDF 页/式号，本文推导并非论文原式。现阶段可比较粗分组，但没有代数依据认定某一组数已同时解决噪声放大、信号增益失配和跨轴相关。
