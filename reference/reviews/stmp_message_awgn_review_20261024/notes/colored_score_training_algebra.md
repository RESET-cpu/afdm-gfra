# 精确协方差条件的有色 score 训练：独立代数核查

2026-10-24。延续 ARS experiment / validate 的有界核查，Verification Status: **ANALYZED**。只核对训练噪声模型、实复系数、张量约定与最优目标；未运行训练、网络或新实验，未修改代码。不在本文重新讨论 GEC 分组。

**结论：在网络直接接收精确 \(C\)、对输入求 score 时固定 \(C\)、且噪声与信道在给定 \(C\) 后独立的条件下，所提实协方差、加权 DSM 及 \(0.5C\) 的复数 Tweedie 读出均正确。** 列轴乘法必须按既定展平顺序使用转置。有限辅助噪声样本不能一般替代精确 \(C\) 条件；尤其不能将这种条件下的网络输出直接乘当次真实 \(C\)，就称为同一个条件 Tweedie 公式。

## 1. 协方差及轴约定

每用户信道张量记为 \(h_{m,o,c}\)，轴顺序为 `[M, Nout, Nin]`；按 C-order 展平，输入列 \(c\) 最快。令 \(d=M N_{\rm out}N_{\rm in}\)，\(d_{\mathbb R}=2d\)。采用

\[
e\mid C\sim\mathcal{CN}(0,C),\qquad
C=vR_a\otimes I_{N_{\rm out}}\otimes R_c,
\]
\[
v>0,\quad R_a\succ0,\quad R_c\succ0,\quad
\operatorname{tr}R_a/M=\operatorname{tr}R_c/N_{\rm in}=1.
\tag{1}
\]

于是 \(\operatorname{tr}C/d=v\)，即 \(v\) 是平均复方差。只有两个因子的对角均为 1 时，每个复元素的方差才都等于 \(v\)；仅 trace 归一化不能称为单位对角的 correlation matrix。这里宜称为归一化协方差因子。

明确索引为

\[
C_{(m,o,c),(m',o',c')}
=v(R_a)_{mm'}\delta_{oo'}(R_c)_{cc'}.
\tag{2}
\]

令 \(R_a=L_aL_a^H\)、\(R_c=L_cL_c^H\)，各输出行的 \(Z_o\in\mathbb C^{M\times N_{\rm in}}\) 元素独立为 \(\mathcal{CN}(0,1)\)。正确噪声生成是

\[
E_o=\sqrt v\,L_a Z_o L_c^T.
\tag{3}
\]

即 \(E_{moc}=\sqrt v\sum_{a,b}(L_a)_{ma}Z_{aob}(L_c)_{cb}\)。**右侧是 \(L_c^T\)，不是 \(L_c^H\)。** 后者在本展平约定下会产生列因子 \(R_c^T\)，其虚部相关方向错误；实对称测试会掩盖这个错误。proper 性由不含共轭的复线性生成及 proper \(Z\) 保证。

同理，协方差作用于任意张量切片的方式是

\[
(CX)_o=vR_aX_oR_c^T.
\tag{4}
\]

Hermitian 主平方根/逆平方根分别使用 \(v^{\pm1/2}R_a^{\pm1/2}X_o(R_c^{\pm1/2})^T\)。不必形成 \(d\times d\) 矩阵。当前源码 `MMVLinear.pack` 另行置换成 `[K*Nin, M*Nout]`；若在该布局处理协方差，必须同步置换，不能原样套用式 (1) 的 Kronecker 次序。当前网络实打包是 `[batch, 2, M, Nout, Nin]`，对应下节的 `[Re; Im]`。

## 2. 实复系数和 Tweedie

定义 \(\mathcal R(A)=\begin{bmatrix}\Re A&-\Im A\\\Im A&\Re A\end{bmatrix}\)，以及 \(e_{\mathbb R}=[\Re e;\Im e]\)。proper complex 噪声给出

\[
\Sigma=\operatorname{Cov}(e_{\mathbb R}\mid C)
=\frac12\mathcal R(C).
\tag{5}
\]

这里 \(s=\nabla_{r_{\mathbb R}}\log p(r_{\mathbb R}\mid C)\) 是 **\(2d\) 维实梯度**，不是直接采用另一种复导数定义。固定 \(C\) 下

\[
\mathbb E[h_{\mathbb R}\mid r,C]=r_{\mathbb R}+\Sigma s.
\tag{6}
\]

若 \(s_{\mathbb C}=s_{\Re}+i s_{\Im}\)，复合成后正是

\[
\boxed{\ \mathbb E[h\mid r,C]=r+\tfrac12Cs_{\mathbb C}\ }.
\tag{7}
\]

等价的 Wirtinger score 为 \(\partial_{r^*}\log p=\tfrac12s_{\mathbb C}\)；只有采用这个 score 定义，读出才写成 \(r+C\partial_{r^*}\log p\)。两者不能混用。\(C=vI\) 时式 (7) 退化为现有实现的 \(r+(v/2)s_{\mathbb C}\)。

## 3. 按 \(C\) 加权 DSM 的最优解

令 \(\varepsilon=r_{\mathbb R}-h_{\mathbb R}\)。所提损失

\[
\mathcal L=rac1{d_{\mathbb R}}
\left\|\Sigma^{1/2}s_\theta(r,C)
+\Sigma^{-1/2}\varepsilon\right\|^2
\tag{8}
\]

采用对称正定主平方根时，等于
\(\|s_\theta+\Sigma^{-1}\varepsilon\|_\Sigma^2/d_{\mathbb R}\)。条件于 \((r,C)\) 后对输出求极小值：

\[
\Sigma s^*(r,C)+\mathbb E[\varepsilon\mid r,C]=0,
\]
\[
s^*(r,C)=\Sigma^{-1}
\bigl(\mathbb E[h_{\mathbb R}\mid r,C]-r_{\mathbb R}\bigr)
=\nabla_{r_{\mathbb R}}\log p(r_{\mathbb R}\mid C).
\tag{9}
\]

因此该权重不改变每个精确 \(C\) 条件下的无限容量最优 score。它会改变有限共享网络的优化和误差分配，不能据此保证有限网络训练优劣。无需加 log determinant；这不是训练协方差估计器的 likelihood 损失。若训练中 \(C\) 与干净信道独立，卷积先验就是同一个 \(p(h)\)；若二者有关，式 (9) 学到的是 \(p(h\mid C)\) 对应的条件 score，须按该目标解释。

用复数运算计算同一损失可写为

\[
\mathcal L=\frac1{2d}
\left\|\frac1{\sqrt2}C^{1/2}s_{\mathbb C}
+\sqrt2 C^{-1/2}(r-h)\right\|_2^2.
\tag{10}
\]

**平方根的实现约定：** 若用 Cholesky \(\Sigma=LL^T\)，式 (8) 必须实现为 \(\|L^Ts+L^{-1}\varepsilon\|^2\)，不能一般写成 \(\|Ls+L^{-1}\varepsilon\|^2\)。对应复 Cholesky \(C=KK^H\) 时，式 (10) 应使用 \(K^Hs_{\mathbb C}/\sqrt2+\sqrt2K^{-1}(r-h)\)。主 Hermitian 平方根则无需这一替换。

## 4. 只有有限辅助噪声条件时，目标为什么改变

令 \(U=(u_1,\ldots,u_J)\)，其中给定 \(C\) 后 \(u_j\sim\mathcal{CN}(0,C)\)，彼此独立且独立于 \((h,e)\)。若网络只接收 \((r,U)\)，训练时在变化的 \(C\) 上使用式 (8)，条件极小值变成

\[
\boxed{\ s^*_{\rm weighted}(r,U)
=\mathbb E[\Sigma_C\mid r,U]^{-1}
\bigl(\mathbb E[h_{\mathbb R}\mid r,U]-r_{\mathbb R}\bigr)\ }.
\tag{11}
\]

这通常既不是给定当次真实 \(C\) 的 score，也不是 \(p(r\mid U)\) 的 score。若改用**不带矩阵权重**的 DSM，最优输出才是

\[
\mathbb E[-\Sigma_C^{-1}\varepsilon\mid r,U]
=\nabla_r\log p(r\mid U),
\tag{12}
\]

但此时噪声是协方差混合，仍不能一般以某一次真实 \(\Sigma_C\) 乘这个 marginal score 得到条件均值。对于式 (11)，乘 \(\mathbb E[\Sigma_C\mid r,U]\) 可恢复相应均值，而乘真实 \(\Sigma_C\) 一般不行；该后验平均协方差也不是现成的有限样本 covariance。

有限个 Gaussian 辅助样本在不同 PD 协方差下具有重叠的支持，通常无法逐样本精确识别 \(C\)。特殊情况包括 \(C\) 在整个任务固定已知、或条件输入已经确定 \(C\)。**当前方案直接输入精确 \(C\) 的参数/矩阵，因而应使用式 (9)，不存在上述条件混合问题。** 如额外再给辅助噪声，保留精确 \(C\) 并按条件独立生成即可；它不替代精确条件。

## 5. 最小约定与原文依据

- 精确紧凑条件必须确定协方差的幅度和方向；只给特征值而不给非固定特征基，不等价于精确 \(C\)。trace 归一化固定两个因子的尺度，\(v\) 承担总体尺度。
- 若内部采用天线酉变换 \(U_a\)，条件因子同步为 \(U_aR_aU_a^H\)；信道、噪声、score 与条件要在同一坐标中。若使用固定幅度归一化 \(h'=h/a\)，则 \(C'=C/a^2\)、物理 score 为归一化 score 除以 \(a\)。
- 训练只保证所选噪声族下的目标定义正确，不证明实际迭代误差属于该 Kronecker/proper/条件独立族。这里没有作这样的外推。

原文核对：

1. Dytso–Poor–Shamai，*A General Derivative Identity for the Conditional Mean Estimator in Gaussian Noise and Some Applications*，[作者稿 v1](https://arxiv.org/pdf/2104.01883v1)，PDF p. 1 原式 (1) 的独立 Gaussian/PD 假设，p. 2 原式 (3) 的一般协方差 Tweedie 公式。本文复实系数与张量乘法为据此明确展开的项目推导。
2. Cai 等，[STMP 作者稿 v2](https://arxiv.org/pdf/2506.00581v2)，[本地 PDF](../../../literature/cai2026_stmp_v2.pdf)，PDF pp. 8–9，§IV-A–B 原式 (43)–(49) 的噪声条件 score、Tweedie 和 DSM。本文显式采用实梯度，因此不能把原文复 score 写法的系数直接移到 `[Re;Im]`。
3. Shastri–Ahmad–Metzler–Schniter，*Denoising Generalized Expectation-Consistent Approximation for MR Image Recovery*，[作者稿 v2](https://arxiv.org/pdf/2206.05049v2)，[本地 PDF](../../../literature/shastri2022_dgec.pdf)，PDF p. 16，§III-B 原式 (39)–(41)：corr+corr 给出同协方差的独立辅助样本，论文采用直接去噪损失，其推断希望网络从有限样本提取相关统计；没有证明这些样本等同于精确 \(C\) 条件。式 (11)–(12) 是本次条件最优化的直接推导，不归为原文结论。
