# 限制相位增量的局部更新：完整推导与验证边界

日期：2026-11-03。状态：独立候选的数学定义；数值参数、测试和接收机结果由独立实验记录给出。本文件不变更已选定算法、冻结权重、初始化或主线绑定。

本方案从当前固定 Gaussian 反馈的精确条件矩出发，在每个用户当前相位附近计算一个有界增量。每次相位更新只扫描全部用户一次，不进行逐路径时延、多普勒参数搜索，不求全圆三角多项式的全部驻点。它是本项目适配，不是 Shen、SAGE、Kullback proximal 或 Ito 方法的完整复现，也不增加新的方法缩写。

文献核对记录见 [SOURCES.json](../../reference/reviews/phase_update_20261103/SOURCES.json)；既有模型和 Q 阶化简见 [PHASE_DIRECT_20261103.md](PHASE_DIRECT_20261103.md)。以下公式编号仅在本研究记录内使用，不是参考论文公式编号。

## 1. 模型、相位参数与本次冻结的量

把接收天线和输出位置合并为列索引 \(d=1,\ldots,D\)，其中 \(D=MR\)。记 \(q=0,\ldots,Q-1\)，用户 \(k=1,\ldots,K\)，则

\[
 Y=\sum_{k=1}^K S_k(\beta_k)P_kX_k+W,
 \qquad S_k(\beta_k)=\operatorname{diag}(e^{\mathrm jq\beta_k}),
 \tag{1}
\]

其中 \(Y\in\mathbb C^{Q\times D}\)、\(P_k\in\mathbb C^{Q\times N}\)、\(X_k\in\mathbb C^{N\times D}\)，且 \(W_{qd}\sim\mathcal{CN}(0,\sigma^2)\)。活动已经包含于有效信道；不按真实活动集合删除用户。\(\beta_k\) 是包裹斜率，周期为 \(2\pi\)；本式不确定绝对物理多普勒的模糊分支。

一次相位更新期间固定学习模块输出的 Gaussian 反馈

\[
 X_{k,:,d}\sim\mathcal{CN}(M_{k,:,d},vI_N),\qquad v>0,
 \tag{2}
\]

并假设各 \(k,d\) 在此反馈模型中独立。\(v\) 为所有用户共享的复数方差，\(\sigma^2>0\)；天线、输出位置和用户的这种各向同性独立结构是计算化简的前提，不是对真实学习先验的声明。反馈均值、反馈方差、噪声、导频和观测在整个一次用户扫描中保持不变。

为与现有常数信道旋转一致，在本次辅助优化中使用

\[
 \phi_{qk}=e^{\mathrm j(q\beta_k+\alpha_k)},\qquad
 S_k(\beta_k,\alpha_k)=e^{\mathrm j\alpha_k}S_k(\beta_k).
 \tag{3}
\]

进入本次更新时 \(\alpha_k=0\)。常数旋转并非增加一个待辨识的物理路径参数：优化结束后把它吸收为 \(M_k^{+}=e^{\mathrm j\alpha_k}M_k\)，观测算子仍只保存共同斜率。由于 (2) 是圆对称各向同性 Gaussian，旋转均值而保持 \(vI\) 不变，与在似然中使用 (3) 完全等价。若未来反馈协方差或先验结构改变，须重新检查这一等价关系。

## 2. 固定 Gaussian 模型的精确后验

以下 \(S_k\) 先取进入本次更新时的 \(S_k(\beta_k,0)\)。令

\[
 G_k=P_kP_k^H,\quad Z_k^0=P_kM_k,\quad
 E=Y-\sum_k S_kZ_k^0,
\]
\[
 C=\sigma^2I_Q+v\sum_k S_kG_kS_k^H,\qquad
 T_k=vG_kS_k^H.
 \tag{4}
\]

把没有乘相位的用户贡献记为 \(Z_k=P_kX_k\)。每个独立列的 Gaussian 条件公式给出

\[
 \widehat Z_k=Z_k^0+T_kC^{-1}E,
\]
\[
 K_{kl}=\operatorname{Cov}(Z_{k,:,d},Z_{l,:,d}\mid Y)
 =\delta_{kl}vG_k-T_kC^{-1}T_l^H.
 \tag{5}
\]

不同 \(d\) 具有相同条件协方差。每个 \(K_{kl}\) 是 \(Q\times Q\) 矩阵；约定为 \(E[(Z_k-\widehat Z_k)(Z_l-\widehat Z_l)^H]\)。条件化后不同用户不再独立，因此必须保留 \(k\ne l\) 项。计算只分解 \(Q\times Q\) 的 \(C\)，利用 Cholesky 解方程，不显式求逆。

现有实现对应 `C_STMP_phase_direct_20261103/moments.py` 的 `conditional_projected_moments`。这里的“精确”仅指 (1)–(2) 冻结 Gaussian 模型，不指学习接收机真实信道后验。

## 3. 期望残差二次目标

以 (5) 的后验为固定分布，对新相位最小化期望平方残差。去掉 \(\|Y\|_F^2\) 等不依赖相位的项，得到

\[
 J(\Phi)=\sum_q\left(\phi_q^HA_q\phi_q
                       -2\Re\{\phi_q^Hb_q\}\right),
 \tag{6}
\]

其中 \(\phi_q=(\phi_{q1},\ldots,\phi_{qK})^T\)，

\[
 A_q[k,l]=\sum_d\overline{\widehat Z_k[q,d]}\widehat Z_l[q,d]
                 +D\overline{K_{kl}[q,q]},
\]
\[
 b_q[k]=\sum_d\overline{\widehat Z_k[q,d]}Y[q,d].
 \tag{7}
\]

\(A_q\) 是 Hermitian 半正定矩阵。注意 (7) 的二阶矩采用 \(E[\overline{Z_k}Z_l]\)，与 (5) 的协方差共轭方向相反；漏掉该共轭、乘数 \(D\) 或跨用户协方差都会改变更新问题。实现可用 Hermitian 对称化消除舍入误差，不应随意删除非对角项。

该形式与 Shen [S1] III-C 式(48)–(51)使用后验均值和二阶矩构造相位目标的思路一致；共同斜率、常数旋转和 (4)–(7) 的具体索引是本项目推导。

固定其他用户后定义

\[
 u_q=b_q[k]-\sum_{l\ne k}A_q[k,l]\phi_{ql}.
 \tag{8}
\]

由于 \(|\phi_{qk}|=1\)，自项 \(A_q[k,k]|\phi_{qk}|^2\) 为常数。因此更新用户 \(k\) 等价于最大化

\[
 \Re\sum_q\overline{\phi_{qk}}u_q.
 \tag{9}
\]

使用当前扫描中已经接受的其他用户相位计算 (8)，但不重新计算 (5)；否则不同坐标不再优化同一个固定目标。

## 4. 中心化增量及其约束

对 \(Q>1\)，令

\[
 \bar q=(Q-1)/2,\qquad s_q=(q-\bar q)/\bar q\in[-1,1].
 \tag{10}
\]

以两个实数 \(a,b\) 描述相位变化：

\[
 \phi_{qk}^{+}=\phi_{qk}e^{\mathrm j(a+s_qb)},\qquad
 |a|+|b|\le\Delta,
 \tag{11}
\]

其中 \(\Delta>0\) 是本次每个用户允许的最大未包裹相位增量，单位为弧度。归一化坐标使两个变量具有相同的相位量纲，且不随帧数自动放大斜率方向的数值尺度。

因为采样包括 \(s_0=-1\) 和 \(s_{Q-1}=1\)，

\[
 \max_q|a+s_qb|=\max(|a-b|,|a+b|)=|a|+|b|.
 \tag{12}
\]

故 (11) 精确约束整条相位曲线的本次变化，不只是约束某个斜率数值。参数回写为

\[
 \beta_k^{+}=\operatorname{wrap}_{[-\pi,\pi)}(\beta_k+b/\bar q),\qquad
 \alpha_k^{+}=\alpha_k+a-b.
 \tag{13}
\]

验证来自恒等式 \(a+s_qb=(a-b)+q b/\bar q\)。不得把常数旋转误写为 \(a\)。包裹 \(\beta\) 不改变整数帧索引对应的相位值，但轨迹记录应另外保存未包裹增量，以免掩盖累计漂移。

对于 \(Q=1\)，斜率在 (1) 中不出现，保持原 \(\beta_k\) 不变，只用 \(a\) 并限制 \(|a|\le\Delta\)，常数旋转增加 \(a\)。

## 5. 梯度、Hessian 与局部方向

令 \(c_q=\overline{\phi_{qk}}u_q\)，并记 \(v_q=(1,s_q)^T\)、\(z=(a,b)^T\)。用户目标为

\[
 G(z)=\Re\sum_q c_q e^{-\mathrm jv_q^Tz}.
 \tag{14}
\]

由 \(\Re(-\mathrm jw)=\Im(w)\) 可得

\[
 \nabla G(z)=\sum_q\Im(c_qe^{-\mathrm jv_q^Tz})v_q,
\]
\[
 \nabla^2G(z)=-\sum_q\Re(c_qe^{-\mathrm jv_q^Tz})v_qv_q^T.
 \tag{15}
\]

特别地，零点的梯度与 Hessian 为

\[
 g=\sum_q\Im(c_q)v_q,\qquad H=-\sum_q\Re(c_q)v_qv_q^T.
 \tag{16}
\]

梯度是正的虚部求和；将其误写为负号会使方向颠倒。目标通常非凹，不能直接假设 \(-H\) 正定。

为使曲率下限不随信号幅度改变，先取 \(S=\sum_q|c_q|\)，在 \(S>0\) 时用 \(\widetilde c_q=c_q/S\) 计算归一化目标 \(\widetilde G=G/S\)、\(\widetilde g\) 和 \(\widetilde H\)。这不改变改善方向或 Armijo 检查的含义。\(S=0\) 时该坐标目标为常数，返回零步。

一种明确、低维的正定化方式为

\[
 -\widetilde H=U\operatorname{diag}(\lambda_i)U^T,\qquad
 B=U\operatorname{diag}(\max(\lambda_i,\mu))U^T,\quad\mu>0,
\]
\[
 p_0=B^{-1}\widetilde g,\qquad
 p=\min\left(1,\frac{\Delta}{\|p_0\|_1}\right)p_0.
 \tag{17}
\]

\(p_0=0\) 时直接返回零步；实际仅需求解一个实对称 \(2\times2\) 系统。若 \(\widetilde g\ne0\)，则 \(\widetilde g^Tp_0=\widetilde g^TB^{-1}\widetilde g>0\)，正比例限幅后仍为上升方向。\(Q=1\) 使用对应一维公式。

\(\mu\)、\(\Delta\) 及数值零点容差是实验配置，不能通过读取真实相位来确定。正定化是数值方向构造，不是相位置信度估计；很陡的错误目标也可能来自不准确消息。

## 6. 回溯、允许零步和固定目标保证

取 \(0<\eta<1\)、\(0<\rho<1\)，依次尝试 \(t=1,\rho,\rho^2,\ldots\)，接受第一个满足

\[
 \widetilde G(tp)-\widetilde G(0)
 \ge\eta t\widetilde g^Tp
 \tag{18}
\]

的候选。这里是最大化问题的 Armijo 充分上升条件。Armijo [S7] p.2 Corollary 2 式(2)给出最速下降和二分步长的原始充分下降形式；(18) 的上升方向、一般参数以及 (17) 是本项目适配。

在精确算术下，非零梯度的上升方向具有足够小的可接受步长。直接证明：\(\sum_q|\widetilde c_q|=1\)、\(\|v_q\|_2^2\le2\) 给出 \(\|\nabla^2\widetilde G(z)\|_2\le2\)，从而

\[
 \widetilde G(tp)-\widetilde G(0)
 \ge t\widetilde g^Tp-t^2\|p\|_2^2.
 \tag{19}
\]

当 \(0<t\le(1-\eta)\widetilde g^Tp/\|p\|_2^2\) 时满足 (18)。这是本次平滑三角目标的局部存在性证明，不是整个学习接收机收敛证明。

实现使用有限回溯预算。梯度在数值容差内为零、无有效上升方向、候选非有限或预算内没有可接受步时，保留原相位。不能因为到达最小步长就强制接受。小增量时可计算

\[
 \delta\widetilde G=
 \Re\sum_q\widetilde c_q\operatorname{expm1}(-\mathrm jt v_q^Tp)
 \tag{20}
\]

以避免两个接近目标值相减。数值验收应要求非负增益，必要时要求超过正的舍入余量；不以放宽负增益容差来宣称算法改善。

由于仅用户 \(k\) 改变，其完整二次目标差精确为

\[
 J(\Phi^+)-J(\Phi)=-2\,[G(tp)-G(0)]\le0.
 \tag{21}
\]

因此对所有用户顺序执行一次，接受的每步和整轮均不增加同一个固定 \(J\)。旧点始终可行；零步不破坏该结论。这里不要求解出有界子问题的精确最优点，也不要求每次内部目标达到驻点。有限条件改善的原则可参照 Fessler–Hero [S3] §II-C，但本方案不因逐用户更新而自动成为其 SAGE 算法。

## 7. 固定 Gaussian 边缘目标与保证的边界

对本次固定的反馈 \((M,v)\)，带相位和常数旋转的每列负对数边缘似然（去掉常数）为

\[
 L(\beta,\alpha;M,v)=\log\det C(\beta)
 +\frac1D\operatorname{tr}\{E(\beta,\alpha)^H
                    C(\beta)^{-1}E(\beta,\alpha)\}.
 \tag{22}
\]

常数旋转在 \(S_kG_kS_k^H\) 中消去，因此协方差仅依赖斜率。残差中的均值旋转保留。取 (5) 为旧点精确 Gaussian 后验，(6) 是本模型相位参数对应的期望完整数据负对数似然的变动部分，尺度为 \(1/\sigma^2\)。标准 EM 下界关系于是给出

\[
 D\{L(\beta^+,\alpha^+;M,v)-L(\beta,0;M,v)\}
 \le\frac{J(\Phi^+)-J(\Phi)}{\sigma^2}\le0.
 \tag{23}
\]

这可作为独立的实现核验。与代码等价的核验是比较 `marginal_value(Y,P,M,v,noise,beta)` 和 `marginal_value(Y,P,exp(j*alpha)*M,v,noise,beta_new)`。不是每个用户都重新调用一次边缘求解，整轮前后核验即可。

Neal–Hinton [S2] p.4 式(2)–(3)、p.5 Lemma 2 区分下界与边缘似然。对任意固定近似分布 \(q\)，有

\[
 \Delta\log p(Y;\theta)=\Delta F(q,\theta)
 +D_{\rm KL}(q\Vert p_{\theta^+})
 -D_{\rm KL}(q\Vert p_{\theta}).
 \tag{24}
\]

本次精确 Gaussian E 步使旧点的 KL 为零，故得到 (23)。但学习模块下一次改变反馈均值、方差及其近似含义后，已经不是同一个冻结统计模型。不能据 (23) 推出整个接收机共同目标单调，不能把新旧不同消息下的两个 \(L\) 直接比较并称为原似然改善。即使原统计模型似然确实改善，也不保证逐样本相位误差或 NMSE 改善。

本方案的有界区域借鉴 Chrétien–Hero [S4] 的局部步思想，但没有实现其后验 KL 近端项或“原目标实际改善／局部模型预测改善”的信赖域比值。因此不继承其全局最优或超线性收敛结论，也不将 (18) 称为该论文原算法。

## 8. 外层调度与完整操作

1. 保持选定版原初始化、冻结学习权重、活动阈值、消息阻尼和噪声设定。相位固定时执行原信道／活动条件迭代。
2. 到现有检查时机，且当前消息有效、条件变化和活动判决满足已有稳定准入后，才尝试本次相位更新。准入说明迭代变化小，不说明消息已准确。
3. 固定 \((M,v,\sigma^2)\)，由 (4)–(7)计算一次完整条件矩。按预先固定的用户顺序扫描一次，例如沿用现有二次型对角能量降序、相同值稳定排序；不按真实活动或相位误差排序。
4. 每个用户用当前其他用户相位计算 (8)，依次执行 (10)–(20)。不重新生成神经消息，不求每用户全圆最优，不进行第二轮坐标扫描。
5. 扫描后核对 (21)、(23)及相位曲线约束。若全部为零步，则不把它计为已提交更新，不为零步重建算子、清空历史或重置方差比例。
6. 有实际变化时按 (13)保存包裹斜率，将常数旋转吸收入反馈均值，按现有接收机约定重建线性算子并清理相应过期历史，之后重新进行条件迭代和稳定检查。
7. 只有经过相位提交后的条件迭代，才输出与当前相位算子一致的信道／活动结果；最后一次允许的迭代不提交没有后续推断的更新。一次修正、周期修正和固定相位的对照分别声明，不混用停止规则。

Noels [S5] §3.2 与 §4 的软信息同步分析支持检查内部推断与同步更新的相互影响，但不提供本项目固定的首次轮数和更新间隔。Vila [S6] 的消息自适应阻尼有特定 MAP／Bethe 代价；当前相位局部步控制是另一种操作，不能把 (18) 当作其 Bethe 代价。

## 9. 计算量、已知不足与需要验证的事项

在条件二次型已经获得后，每用户的导数、一个候选相位值与一次回溯都是 \(O(Q)\)，局部系统为常数阶。构造 (8)朴素地为 \(O(QK)\)，整轮为 \(O(QK^2+B_{\max}QK)\)，其中 \(B_{\max}\) 是回溯次数上限。这不包含后验矩形成、学习模块、算子重建及后续条件迭代成本。

Q 阶分解和完整跨用户条件矩沿用已验证的推导；初始化仍保持原版本，不声称整个接收机已经消除物理前端搜索。此次只研究既有初值的精修。

本方案有以下明确不足：错误消息可以产生错误局部方向，限幅不能自动修复方向；接近驻点时允许零步，即使该点可能是非最优驻点；限制单次变化不限制多次累计漂移；较差初值可能更难靠局部步骤离开；较小步长可能增加后续更新次数及总时间。以上均须以完整配对接收机结果判断，不能用条件目标下降代替。

必要的确定性检查包括：

- 梯度和 Hessian 与复数三角目标的中心差分相符，特别核对梯度符号和混合偏导。
- (11)–(13) 的相位值逐元素一致，覆盖包裹边界、\(Q=1\) 和 \(Q=2\)。
- 每用户及整轮的实际 \(J\) 差符合 (21)，后验共轭和跨用户协方差正确保留。
- 冻结 Gaussian 边缘目标满足 (23)，且与吸收常数旋转后的表示一致。
- 零相关、零梯度、非凹局部曲率及回溯拒绝均能返回合法零步；零步不触发接收机状态重置。
- 每个用户的未包裹相位曲线增量不超过 \(\Delta\)，配置参数和回溯预算在推断前固定。

接收机验证使用相同初始化、权重、场景和噪声，比较固定相位、稳定后仅一次局部更新、稳定后周期局部更新以及当前完整更新。记录 NMSE、漏检／虚警、达到迭代上限、实际更新时刻与次数、拒绝原因、相位增量及累计轨迹、初始化／相位／总耗时。真值只用于事后评价，不用于用户选择、步幅或停止。开发样本选择参数后，独立确认样本不得再用于调参；失败和退化结果必须保留。

## 10. 原始来源与适配范围

以下 [S1]–[S6] 与既有 `SOURCES.json` 的 id 对应；[S7] 是为本次回溯条件新增核验的原始来源。

- **[S1] `shen2025`**：Shen et al., *LEO Satellite-Enabled Random Access With Large Differential Delay and Doppler Shift*, TWC 2025。[原文](https://arxiv.org/html/2412.20806v1#S3.SS3)，III-C 式(47)–(54)、预印本 p.9。支持后验矩构造相位二次目标；共同斜率、有界增量及本记录公式不是其原式。
- **[S2] `neal_hinton1998`**：Neal–Hinton, *A View of the EM Algorithm that Justifies Incremental, Sparse, and Other Variants*, 1998。[作者 PDF](https://www.cs.toronto.edu/~hinton/absps/emk.pdf)，pp.4–5，式(2)–(5)、Lemma 2、Theorem 1。用于精确／近似 E 步、下界与似然的区分。
- **[S3] `fessler_hero1994`**：Fessler–Hero, *Space-Alternating Generalized Expectation-Maximization Algorithm*, TSP 42(10):2664–2677, 1994。[作者 PDF](https://web.eecs.umich.edu/~fessler/papers/files/jour/94/pre/tsp,sage.pdf)，§II-B Definition 2 式(2)、§II-C 式(3)–(7)、作者稿 pp.3–4 Theorem 1。仅采用合法条件目标与有限改善，不采用有勘误的 Theorem 2 速率论证。
- **[S4] `chretien_hero2000`**：Chrétien–Hero, *Kullback Proximal Algorithms for Maximum-Likelihood Estimation*, TIT 46(5):1800–1810, 2000。[作者稿](https://arxiv.org/pdf/1201.5907)，p.7 式(11)–(12)、p.9 式(13)和 Assumptions 1、§5.2–5.3 pp.15–16 式(30)–(32)。局部模型与原目标的验收前提不转移为当前学习接收机保证。
- **[S5] `noels2005`**：Noels et al., *A Theoretical Framework for Soft-Information-Based Synchronization in Iterative (Turbo) Receivers*, EURASIP JWCN 2005:2, 117–129。[原文](https://telin.ugent.be/~hs/full/j17.pdf)，§3.2 p.121、§4 p.122 式(22a)–(22b)。用于内部软信息可靠性与同步调度的讨论，模型不同，不导出本项目轮数。
- **[S6] `vila2015`**：Vila et al., *Adaptive Damping and Mean Removal for the Generalized Approximate Message Passing Algorithm*, ICASSP 2015。[作者稿](https://arxiv.org/pdf/1412.2005)，Table 1 R12–R18、§2.1–2.2 式(3)–(11)、pp.2–3。当前学习去噪器没有直接提供其 Bethe 代价，因此本方案仅使用自己声明的固定条件目标。
- **[S7] Armijo 1966**：Larry Armijo, *Minimization of Functions Having Lipschitz Continuous First Partial Derivatives*, Pacific Journal of Mathematics 16(1):1–3，DOI [10.2140/pjm.1966.16.1](https://doi.org/10.2140/pjm.1966.16.1)。[出版方 PDF](https://msp.org/pjm/1966/16-1/pjm-v16-n1-p01-p.pdf)，正文 p.2 Corollary 2 式(2)（PDF 第3页）。原文是最速下降、二分步长的充分下降条件；本次上升形式及正定化方向是适配，(19)给出当前目标的独立局部证明，不套用其全局最优假设。

## 11. 本轮固定实现参数

以下数值来自 `src/configs/candidates/c_stmp_phase_local_20261103/` 的独立配置、其绑定的选定版配置，以及 `C_STMP_phase_local_20261103/iterations.py`；不是文献推荐参数。

局部半径预先设为 \(\Delta=0.25\) 或 \(0.5\) rad，归一化曲率下限 \(\mu=10^{-3}\)，Armijo 参数 \(\eta=10^{-4}\)，回溯比例 \(\rho=1/2\)。最多二分16次，包含未缩短步在内最多评价17个候选。仅使用一轮用户扫描。更新预算分别为0、最多1次或不另设次数上限；是否实际更新仍由稳定准入、局部验收和剩余条件迭代预算决定。

当前实现仅支持 `cycle` 输出停止模式：从第20轮起每20轮检查，最少80轮、最多600轮，提交更新后至少再进行10轮条件推断。相邻有效检查时刻的信道与接收预测相对变化阈值为0.05，保持已有判决稳定和有效消息检查。当前试更新效果仅记录，不额外控制停止。允许0次提交时停止是新候选的明确变化；原选定版强制至少发生一次更新，所以精修公式的主配对对照应采用相同新停止规则的 `reduced_legacy`，原选定版另列参考。最多1次不能写成每份输入恰好1次。

## 12. 初始化与可辨识性边界

仅考虑 (1) 的观测残差，并允许有效信道 \(X_k\) 为任意复矩阵。若 \(P_k\in\mathbb C^{Q\times N}\) 满行秩，定义 \(P_k^\dagger=P_k^H(P_kP_k^H)^{-1}\)，则 \(P_kP_k^\dagger=I_Q\)。对任意另一斜率 \(\beta_k'\)，令

\[
 X_k'=P_k^\dagger S_k(\beta_k-\beta_k')P_kX_k
       +(I_N-P_k^\dagger P_k)U_k,
 \qquad U_k\in\mathbb C^{N\times D}\ \text{任意},
 \tag{25}
\]

可直接得到

\[
 S_k(\beta_k')P_kX_k'
 =S_k(\beta_k')S_k(\beta_k-\beta_k')P_kX_k
 =S_k(\beta_k)P_kX_k.
 \tag{26}
\]

因此每个用户的接收贡献、总预测及同一观测下的残差均保持不变。当 \(Q=N\) 且 \(P_k\) 可逆时，简化为

\[
 X_k'=P_k^{-1}S_k(\beta_k-\beta_k')P_kX_k.
 \tag{27}
\]

这是本模型在**不施加信道先验或其他结构约束**时的代数推论：残差本身不足以区分这些相位与信道组合。变换后的 \(X_k'\) 不一定满足原物理结构，也不一定具有相同的学习先验概率；所以该推论不能证明完整统计模型不可辨识，更不能证明必须使用物理频偏搜索。

它说明单纯最小残差或零相位初值没有自动成功的依据。物理约束、学习先验或其他观测结构可以提供区分信息，初始化算法也可以采用不同实现。本轮保留原初始化，是因为已试无物理搜索替代在开发实验中未达标，而不是已经证明频偏搜索不可避免。上述论证不涉及更新实验的源码或设置变更。
