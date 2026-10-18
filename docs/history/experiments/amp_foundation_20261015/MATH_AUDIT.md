# AMP 基础控制实验：独立数学审查

审查日期：2026-10-15。审查人角色：独立数学审查代理；继承了主代理的讨论上下文，公式与小维数值检查重新推导。本文只审查当前基础控制实验，不修改原 Proposed、joint_amp、训练源或已冻结实验。独立计算仅用 CPU NumPy；没有运行神经网络或物理接收机。

## 1. 结论与证据范围

当前 `PROTOCOL.md`、`analytic.py` 和 `run_foundation.py` 的固定方差根、复数方差单位、完整导数、部分迹方向、精确残差反馈及同步阻尼相互一致，未发现阻断本阶段的数学或实现错误。共享活动先验的去噪器是**局部独立 Gaussian-query 模型下**的精确后验均值；这不等于真实观测下的全局 Bernoulli 混合后验已被精确求解。

三个问题须分开判定：

1. 递推是否正确计算了所声明的映射，以及在固定方差控制中是否到达全局 Gaussian LMMSE。
2. 残差能量是否给出了适合局部去噪器的方差标签。
3. 局部查询误差在去噪器实际使用的用户块统计上是否足够接近独立 Gaussian 噪声。

第 1 项通过不能代替第 2、3 项。反过来，给定有限矩阵时完整查询协方差有非零非对角项，**本身也不是否定 AMP 的充分证据**；通常的状态演化表述并不要求整个高维联合分布在协方差算子范数下等于独立 AWGN。

本次读取到的正式 Gaussian 控制结果为 96 次全部完成，其中 48 次固定方差的最大相对 LMMSE 误差为 `1.2296822672275412e-11`。它支持第 1 项。自适应方差控制与物理查询统计仍需独立解释，不能从“完成”推出 AWGN 接口已通过。

## 2. 约定与同步阻尼

模型为

\[
Y=AX+W,\qquad A\in\mathbb C^{Q\times L},\quad
X\in\mathbb C^{L\times C},\quad L=KN.
\]

本项目采用 \(Q=16,L=640,K=40,N=16,C=256\)，\(c=L/Q=40\)。行索引 \(i=(k,n)\)，特征索引 \(a=(m,r)\)。\(\mathcal{CN}(0,q)\) 表示**复方差** \(\mathbb E|x|^2=q\)，实部、虚部方差各为 \(q/2\)。热噪声复方差记为 \(\sigma^2>0\)。

以 \(H_t\) 表示历史校正状态，避免与特征维数 \(C\) 混淆。实际同步阻尼递推为

\[
\begin{aligned}
R_t&=X_t+A^H Z_t,\\
D_t&=D(R_t;v_t),\\
X_{t+1}&=(1-\beta)X_t+\beta D_t,\\
H_{t+1}&=(1-\beta)H_t+\beta Z_t B_t,\\
Z_{t+1}&=Y-AX_{t+1}+H_{t+1},
\end{aligned}\tag{1}
\]

其中 \(X_0=H_0=0,Z_0=Y\)，\(0<\beta\le1\)。当直接计算反馈时，用精确 \(T_t=Z_tB_t\) 替代乘积即可，不能再额外乘一次 \(Z_t\)。每轮始终有 \(H_t=Z_t-Y+AX_t\)。本阶段精确解析反馈排除了 Monte Carlo 导数误差。

## 3. 固定 Gaussian 方差：全局 LMMSE 与精确稳定谱

### 3.1 固定点恒等式

先验为所有元素独立 \(X_{ia}\sim\mathcal{CN}(0,q)\)。局部 Gaussian 去噪器为

\[
D(R;v)=\alpha R,\qquad \alpha=\frac{q}{q+v},\qquad
B=c\alpha I_C.\tag{2}
\]

选固定 \(v>0\) 满足

\[
v\left(1-c\frac{q}{q+v}\right)=\sigma^2.\tag{3}
\]

其唯一正根为

\[
v_* = \frac{\sigma^2+(c-1)q+
\sqrt{[\sigma^2+(c-1)q]^2+4\sigma^2q}}2.\tag{4}
\]

因此 \(0<\alpha<1\) 且 \(c\alpha<1\)。对任意 \(\beta>0\)，式 (1) 的固定点满足

\[
X=\alpha(X+A^HZ),\qquad H=c\alpha Z,
\qquad (1-c\alpha)Z=Y-AX.
\]

第一式给出 \(X=(q/v)A^HZ\)，再利用 (3) 得

\[
X=\frac q{\sigma^2}A^H(Y-AX),
\]

从而

\[
X_*=qA^H(qAA^H+\sigma^2 I_Q)^{-1}Y.\tag{5}
\]

式 (5) 是本 Gaussian 先验下的**全局后验均值**。该固定点代数对任意确定矩阵 \(A\) 成立，不需要先声称 \(A\) 为 iid Gaussian，也不要求残差能量恰好等于 \(v_*\)。固定点存在、递推收敛、标签校准是不同命题。

### 3.2 同步阻尼的线性谱

令 \(d=1-\beta,b=\beta\alpha\)，消去 \(H_t\) 可得

\[
\begin{aligned}
X_{t+1}&=(d+b)X_t+bA^HZ_t,\\
Z_{t+1}&=\beta Y-bAX_t+
\big[(d+cb)I_Q-bAA^H\big]Z_t.
\end{aligned}\tag{6}
\]

对每个非零奇异值 \(s\)（\(\lambda=s^2\)），误差状态的二维块为

\[
T_\beta(s)=(1-\beta)I_2+
\beta\alpha\begin{bmatrix}1&s\\-s&c-s^2\end{bmatrix}.\tag{7}
\]

先定义未阻尼特征值

\[
\mu_\pm(\lambda)=\frac\alpha2
\left[1+c-\lambda\pm
\sqrt{(1+c-\lambda)^2-4c}\right].\tag{8}
\]

阻尼后的特征值为 \(\nu_\pm=1-\beta+\beta\mu_\pm\)。右零空间特征值为 \(1-\beta+\beta\alpha\)；若有左零空间，其特征值为 \(1-\beta+\beta c\alpha\)。这些模式均须计入谱半径。对每个 \(\mu\)，稳定条件可写成

\[
\operatorname{Re}\mu<1,\qquad
0<\beta<\frac{2(1-\operatorname{Re}\mu)}{|1-\mu|^2}.\tag{9}
\]

在 (3) 的正根和 \(0<\beta\le1\) 下，也可写出只依赖最大奇异值的等价条件：

\[
\lambda_{\max}(AA^H)<
1+c+\frac{2-\beta}{\beta\alpha}
       +\frac{\beta c\alpha}{2-\beta}.\tag{10}
\]

推导：令 \(t=\operatorname{tr}T_\beta\)、\(e=\det T_\beta\)，二阶实多项式的根位于单位圆内要求 \(1-t+e>0,1+t+e>0,1-e>0\)。也可直接将 \(\nu=(1+s)/(1-s)\) 代入多项式，得到系数为上述三个量的二阶左半平面问题。此处

\[
1-t+e=\beta^2[(1-\alpha)(1-c\alpha)+\alpha\lambda]>0.
\]

而 \(e\le(d+b)(d+cb)<1\)，故仅剩 \(1+t+e>0\)，化简即 (10)。边界相等时不能声称渐近收敛。

谱半径小于 1 保证该**固定线性映射**渐近收敛，不保证每轮误差单调。非正规矩阵可有瞬态放大，也不能只用 \(\rho(T)^t\) 冒充无系数的严格误差上界。对当前固定 Gaussian 检查，实际误差、正规方程残差和谱半径共同构成证据。

### 3.3 自适应残差方差不能套用上述线性证明

当前逐束标签为

\[
\widehat v_{t,m}=\frac1{Q C_m}
\sum_{q=1}^Q\sum_{a\in m}|Z_{t,qa}|^2.\tag{11}
\]

改用 (11) 后 \(\alpha_t\) 随数据变化，迭代已不是 (6) 的同一固定线性映射。即使收敛，若极限标签没有满足 (3)，由同样的固定点消元得到的有效正则化为

\[
\frac{v(1-cq/(q+v))}{q},\tag{12}
\]

未必等于 \(\sigma^2/q\)；若逐束标签不同，连有效正则化也会逐束不同。因此残差模式偏离已知 LMMSE 完全可能来自标签闭环，而无需假设导数或转置错误。

解析 Onsager 使用 \(D\) 对查询 \(R\) 的偏导，固定该轮 \(v,q,\rho\)。这对应当前算法定义。不能把固定标签偏导的正确性延伸为包含标签更新的整个闭环 Jacobian 已被线性谱分析覆盖。

还可在固定标签的 LMMSE 固定点精确分析残差标签：由 \(Z_*=(Y-AX_*)/(1-c\alpha)\) 及 (3)、(5)，有

\[
\Sigma_{Z,*}=v^2(qAA^H+\sigma^2I)^{-1},\qquad
\mathbb E\widehat v_m=\frac{\operatorname{tr}\Sigma_{Z,*}}Q,
\quad
\operatorname{Var}(\widehat v_m)=
\frac{\operatorname{tr}(\Sigma_{Z,*}^2)}{Q^2C_m}.\tag{12a}
\]

这里利用的是给定 \(A\) 后各特征列独立，\(C_m=16\)。有限矩阵未必使 \(\mathbb E\widehat v_m=v\)；即使 \(\Sigma_{Z,*}\) 接近各向同性，每束标签的相对标准差也约为 \(1/\sqrt{QC_m}=6.25\%\)。因此自适应输出相对 LMMSE 有数个百分点差异，可能包含标签抽样波动及有限矩阵效应。式 (12a) 是**冻结标签固定点**的参考，不能直接当作自适应闭环的精确分布，也不单独解释全部差异。

## 4. 用户共享活动的解析局部后验

### 4.1 匹配模型与均值

设每个用户 \(a_k\sim\operatorname{Bernoulli}(\rho)\)，独立于其他用户；活跃时 \(X_{kna}\) 独立服从 \(\mathcal{CN}(0,q)\)，非活跃时整个 \(N\times C\) 块为零。**局部去噪模型**另假设

\[
R_{kna}=X_{kna}+E_{kna},\qquad
E_{kna}\overset{\mathrm{ind}}\sim\mathcal{CN}(0,v_a),\tag{13}
\]

且 \(E\) 与 \(X\) 独立。\(v_a>0\) 可以逐特征不同；本实验每束内重复同一标签。

令

\[
\alpha_a=\frac q{q+v_a},\qquad
\delta_a=\frac1{v_a}-\frac1{q+v_a}=\frac{\alpha_a}{v_a}.
\]

相对于非活跃的对数似然比、后验活动概率、条件均值及联合均值分别为

\[
\begin{aligned}
\ell_k&=-N\sum_a\log(1+q/v_a)
       +\sum_{n,a}\delta_a|R_{kna}|^2,\\
p_k&=\operatorname{sigmoid}(\operatorname{logit}\rho+\ell_k),\\
F_{kna}&=\alpha_aR_{kna},\qquad D_{kna}=p_kF_{kna}.
\end{aligned}\tag{14}
\]

这里没有把活动后的均值近似为仅条件 Gaussian 均值。局部总协方差还含有活动不确定项：

\[
\operatorname{Cov}(x_k\mid r_k)=
p_k\operatorname{diag}\!\left(\frac{qv_a}{q+v_a}\right)_{n,a}
\quad +p_k(1-p_k)f_kf_k^H.\tag{15}
\]

`analytic.py` 使用 `log1p` 和分支稳定 sigmoid，与 (14) 一致。\(q,v_a\) 都是复方差，不应再乘或除以 2。

### 4.2 全导数与精确部分迹

对同一用户的任意两个行、特征坐标，固定标签的 Wirtinger 导数为

\[
\frac{\partial D_{knb}}{\partial R_{kn'a}}=
p_k\alpha_b\mathbf1_{n=n'}\mathbf1_{a=b}
\quad +p_k(1-p_k)\alpha_bR_{knb}\delta_a\overline{R_{kn'a}},\tag{16}
\]

\[
\frac{\partial D_{knb}}{\partial \overline{R_{kn'a}}}=
p_k(1-p_k)\alpha_bR_{knb}\delta_aR_{kn'a}.\tag{17}
\]

跨用户导数为零。式 (17) 一般非零，故实方向导数必须包含它：

\[
L[U]=J_z[U]+J_{\bar z}[\overline U],\qquad
J_z[U]=\tfrac12\{L[U]-\mathrm iL[\mathrm iU]\}.\tag{18}
\]

proper complex iid 测量矩阵下标准复 AMP 的校正对应 \(J_z\) 的部分迹；不是对整个实 Jacobian 随意取实部。当前实际 AFDM 使用相同公式属于所测试的有限维适配，不能凭导数计算正确就声称 cavity 近似已成为恒等式。

本项目采用残差右乘方向

\[
B_{ab}=\frac1Q\sum_{k,n}
\frac{\partial D_{knb}}{\partial R_{kna}}.
\]

由 (16) 得

\[
B=\operatorname{diag}\left(\frac NQ\sum_k p_k\alpha\right)
 +\frac1Q\sum_k p_k(1-p_k)
 \operatorname{diag}(\delta)R_k^HR_k\operatorname{diag}(\alpha).\tag{19}
\]

矩阵中第一个索引是输入特征、第二个是输出特征；因此反馈为 \(ZB\)，不是 \(ZB^T\) 或 \(ZB^H\)。异方差时 \(B\) 不必 Hermitian，不能强行对称化。

直接反馈可精确写成

\[
ZB=Z\operatorname{diag}\left(\frac NQ\sum_kp_k\alpha\right)
 +\frac1Q\sum_kp_k(1-p_k)
 \big[Z\operatorname{diag}(\delta)R_k^H\big]
 \big[R_k\operatorname{diag}(\alpha)\big].\tag{20}
\]

括号尺寸分别为 \(Q\times N\) 和 \(N\times C\)。式 (20) 不需要 Monte Carlo，也不丢弃用户块内跨行、跨特征依赖。`partial_trace()` 与 `exact_feedback()` 的索引、复共轭、\(1/Q\) 均与 (19)、(20) 一致。

### 4.3 解析范围与物理模型边界

匹配生成 (14) 的先验只保证先验被正确指定。真实查询由迭代与 \(A\) 共同产生，不会因为先验解析就自动满足 (13)。尤其 \(Q=N=16\)，一个用户的 \(A_k^HA_k\) 未必接近单位阵，用户块内行相关可能直接影响对数似然比。

活跃块 4096 个独立 Gaussian 系数与原物理信道的有限路径、时延、多普勒、空间相关结构不同。即使解析活动控制成功，也不能把其 NMSE 与原 Proposed 在物理信道上的成绩直接排名；它的意义是隔离算法与观测算子。

给定活动支撑后的 Gaussian LMMSE 可以精确计算，适合作为明确标记的 oracle 评价。未知活动时，全局后验仍是不同支撑的混合；本文没有枚举或精确积分该全局后验。

## 5. 有限维 Gaussian 参考：先验证正确矩，而非预设白噪声

### 5.1 首轮精确协方差

固定 \(A\)，令 \(G=A^HA\)。首轮 \(R_0=A^HY\)，故

\[
E_0=R_0-X=(G-I)X+A^HW.
\]

对 dense Gaussian 先验，每个特征列的联合分布精确为 proper Gaussian，且

\[
\begin{aligned}
\Sigma_{E,0}&=q(G-I)^2+\sigma^2G,\\
\operatorname{Cov}(E_0,X)&=q(G-I),\\
\Sigma_Y&=qAA^H+\sigma^2I_Q.
\end{aligned}\tag{21}
\]

因此“精确 Gaussian”并不等于“白且与信号独立”。对于已固定活动支撑，令 \(\Xi=\operatorname{diag}(qa_kI_N)_k\)，相应表达为

\[
\Sigma_{E,0}=(G-I)\Xi(G-I)^H+\sigma^2G,\qquad
\operatorname{Cov}(E_0,X)=(G-I)\Xi.\tag{22}
\]

在 (21) 的 dense 首轮，特征列在给定 \(A\) 后独立。若 \(T=C^{-1}\|E_0\|_F^2\)，则

\[
\mathbb ET=\operatorname{tr}\Sigma_{E,0},\qquad
\operatorname{sd}(T)=
\sqrt{\operatorname{tr}(\Sigma_{E,0}^2)/C}.\tag{23}
\]

复 proper Gaussian 的式 (23) 没有额外实 Gaussian 的因子 2。`first_gaussian_moments()` 用 \(AA^H\) 的特征值和 \(L-Q\) 个零空间特征值计算 (23)，正确利用了独立特征列，**没有把相关行误作独立样本**。标准化偏差只表示距离精确均值多少个精确标准差，不应无检验地声称其分布精确为标准正态。

公共 Frobenius 归一化令 \(\operatorname{tr}G=L\)，所以

\[
\mathbb E\langle X,E_0\rangle/C=q\operatorname{tr}(G-I)=0.\tag{24}
\]

即使 (24) 为零，完整交叉协方差仍可很大。全局一个内积可能发生抵消，不能据此排除用户块依赖。另一方面，完整交叉协方差 Frobenius 范数也不能被设成标准 AMP 必须趋零的门槛；应检查去噪器实际依赖的局部统计和有限维 Gaussian 参考。

### 5.2 可选的全轮线性参考

固定 \(v,\beta\) 时，存在确定传递矩阵 \(X_t=P_tY,Z_t=S_tY\)。令 \(T_t=P_t+A^HS_t\)，则

\[
\begin{aligned}
\Sigma_{E,t}&=(T_tA-I)\Xi(T_tA-I)^H+\sigma^2T_tT_t^H,\\
\operatorname{Cov}(E_t,X)&=(T_tA-I)\Xi,\\
\Sigma_{Z,t}&=S_t(A\Xi A^H+\sigma^2I)S_t^H.
\end{aligned}\tag{25}
\]

这给出无需 AMP 渐近近似的逐轮参考。当前首轮精确矩已经足以完成最小代码核验；如后续需要区分有限维协方差与残差标签问题，式 (25) 是比继续训练网络更直接的新增控制。自适应标签依赖样本时，不能把同一组 \(P_t,S_t\) 当作确定矩阵套用 (25)。

## 6. 查询校准与统计设计

### 6.1 参考与统计单位

本实验同一场景跨矩阵、SNR、阻尼和标签模式共用信道或标准化噪声，是有价值的配对设计；这些运行不是独立重复。四个场景仍只提供四个独立外层样本，三种 SNR 不能把它变成十二个独立场景。当前协议正确将结果定位为描述性诊断。

应区分以下参考：

- **精确有限维参考**：式 (21)—(23)，检查代码和数据生成是否正确；它允许有色和信号相关误差。
- **标签匹配独立 Gaussian 参考**：固定实际记录的 \(v_{t,a}\)，生成独立 \(E^G_{kna}=\sqrt{v_{t,a}}G_{kna}\)，与同一 \(X\) 配对；检查去噪接口需要的统计是否合理。
- **协方差或真实误差能量匹配参考**：可进一步隔离高阶分布差异，但必须标记为 oracle 诊断，不能以重新匹配的方差反过来宣称原标签已校准。

残差标签和查询误差来自同一样本。将理论误差能量除以观测到的随机标签，是有用的描述性比较，但一般不是随机比值期望的精确解析预测。首轮确定矩验证应优先比较未归一化二阶矩，再看标签比值。

### 6.2 应预先固定的局部诊断

对 \(E_t=R_t-X\)，建议至少报告：

1. 每束及活跃/非活跃用户分组的 \(\sum|E|^2/\sum v\)，并记录实际标签范围；不能只报告全局平均。
2. \(E/\sqrt v\) 的均值、properness 对应的伪协方差，以及归一化四阶矩。四阶矩分母中使用观测能量会消去尺度差异，因此它不能代替方差校准。
3. 用户块内 \(N\times N\) 行相关；固定行与特征投影下的跨特征/跨束相关。有限样本的非对角样本协方差不可能恰为零，应比较同尺寸 Gaussian 参考的分布。
4. 信号相关的复内积及活跃用户分组/预定投影统计；不得仅用式 (24) 会抵消的全局平均。
5. **去噪器自身使用的对数似然比 \(\ell_k\)、活动概率分布和块能量**与标签匹配 Gaussian-query 参考的比较。共享活动头汇聚整个块，这是比只检验单个系数直方图更贴近当前失败机制的指标。

对于同一矩阵、同一活动支撑，不能把 4096 个系数统一当作独立抽样单位。dense 固定线性首轮可利用给定 \(A\) 后独立的特征列推导式 (23)；一般共享活动非线性与自适应标签会重新耦合特征。整体置信区间应由独立外层场景或独立重复生成的 \((X,W)\) 构建，并保留配对结构。

### 6.3 推进门槛

本阶段的 `1e-8` 解析/固定点目标和 `1e-9` 原 core 对照目标，与 double 精度、确定映射的检查相称。固定点目标还须确认所用迭代数与实际谱半径允许达到该精度；当前 Gaussian 正式结果已通过。

查询近似的门槛不能要求所有经验相关等于零，也不能仅因“没有显著拒绝”就认定匹配。当前四场景只作描述性定位是合理的。若据此决定重新接入网络，应先预定与去噪风险有关的实际容许偏差，并用独立开发重复及匹配 Gaussian 参考验证，而非看完结果后放宽范围。多个轮次/指标若要作正式显著性判断，应使用预先指定的联合参考范围或多重比较处理；本次协议没有声称已经完成这种正式判定。

如果小 \(Q\) 的 Gaussian 矩阵也不匹配局部查询，并不能直接判定 AMP 推导或程序错误。后续最有区分力的补充是保持维数比的 iid 尺寸扩展，或者直接使用式 (25) 检查有限维效应；不宜先通过裁导数或扩大训练预算隐藏偏差。

## 7. 数据与实现审查

以下设计已在本次读取的代码中落实：

- dense 使用 \(q=0.1\)；活动先验使用 \(q=1,\rho=0.1\)，两者无条件二阶矩相同。
- 期望接收功率给出 \(\sigma^2=q\rho(L/Q)10^{-\mathrm{SNR}/10}\)，没有按某次真实信道能量调整噪声。
- Gaussian 算子先由 \(\mathcal{CN}(0,1/Q)\) 生成，再作公共 Frobenius 归一化。最终元素不再严格独立；协议已明确这一点。它是当前归一化对照，不应被写成逐元素严格 iid 的有限维定理验证。若后续要精确对应 iid 假设，可另外保留不再归一化的原始 Gaussian 组，不能改写本组标签。
- `iterate()` 不接收信道真值或活动真值；真值仅在返回后的评价中使用。固定轮数输出，不按真值选择迭代轮次。
- 零活跃样本不拒绝或补抽；零信号能量时 NMSE 缺省，活动错误仍保留。
- 真实支撑只用于单列标记的 oracle LMMSE 评价；没有进入解析活动递推。
- 两种先验都通过精确反馈与现有 `core.solve` 的完整行基对照，验证同步历史状态和输出方向。

`query_statistics()` 当前覆盖全局/活动分组方差、四阶矩和标量信号相关；它本身并未完成上述所有行/跨特征/似然证据诊断。物理查询诊断须作为单独证据读取，不能把这些尚未报告的统计视为已经通过。

## 8. 独立数值核查与现有实验记录

审查自有脚本为 `scratch_math_audit/check_math.py`，结果为 `scratch_math_audit/CHECK.json`。它不调用被审查的解析实现，而由显式完整 Jacobian、独立线性状态及完整行基重新核验：

| 检查 | 结果 |
|---|---:|
| 固定方差方程绝对误差 | 5.55e-17 |
| 全线性状态谱与奇异值块谱最大匹配误差 | 1.43e-15 |
| 两个阻尼值收敛到 LMMSE 的最大相对误差 | 5.85e-16 |
| 式 (10) 与直接特征值比较 | 1632 点，0 不一致 |
| 共享活动实方向导数中心差分相对误差 | 2.61e-10 |
| 解析部分迹与显式完整 Jacobian | 1.95e-16 |
| 直接反馈与完整矩阵乘积 | 2.12e-16 |
| 完整用户行基与精确反馈 | 1.54e-16 |

自有检查使用两个未饱和的活动概率约 0.184，且共轭导数范数非零，避免只在 \(p=0\) 或 \(p=1\) 的退化情形检验。

只读加载 scene00 的公开观测算子（未读物理信道真值）得到 \(AA^H\) 特征值区间 `[30.5806368134, 51.2905184060]`。在本协议 \(q=.1,\mathrm{SNR}=-4\) 下，\(v_*=14.0192155402\)，固定方差谱半径为 \(\beta=1\) 时 `0.0447939569`、\(\beta=.2\) 时 `0.8073955411`。这些是该矩阵、该噪声设置的有限维计算，不推广为所有 AFDM 算子性质。

主实验已保存的记录：

- `ANALYTIC_VERIFICATION.json`：4 项检查通过，含自动微分、异方差方向及显式错误转置反例。
- `CORE_VERIFICATION.json`：Gaussian 和共享活动相对差异分别约 `1.48e-16`、`4.95e-16`。
- `gaussian/SUMMARY.json`：96 次完成，固定方差 48 次全部通过，最大相对 LMMSE 差异 `1.22968e-11`。
- `NUMERIC_CROSSCHECK.json`：macOS NumPy 矩阵乘法出现除零/溢出/invalid 警告，但保存结果全部有限；独立显式 contraction 分别以 `2.12e-16`、`9.53e-16` 相对差异核验回投影和 Gram。原警告保留，不能把警告文字直接当作真实迭代溢出，也不能删除不利记录。

审查自有首轮运行也遇到同类矩阵乘法警告；相关 contraction 改为自有脚本内的 `einsum(..., optimize=False)` 后重验得到相同有限数值，最终结果见脚本哈希。没有因此修改已冻结主实验源码。

本审查读取的主实验冻结哈希如下：

```
run_foundation.py  f4bcf55fa7b8dc12ac5f65748a73ed602b6a48168ce5b33f4107edfb98609858
analytic.py        37dfe72e49b19f7c6d6624681cd55dd9c689ad008e5df813bc0d0e65a4b30621
PROTOCOL.md        a4774313e3c999d6eb88219cadd99f7c7593350f4002496c88b674760a0aa103
joint_amp/core.py  bcd401996690f201bacde3943714438fcbab6cec898f75bfc9e4bc58e1b8f1c3
```

## 9. 原文依据与适用范围

1. Liu and Yu, *Massive Connectivity with Massive MIMO–Part I: Device Activity Detection and Channel Estimation*, [§III-B (14)—(18)、§III-C (19)—(22)](https://arxiv.org/html/1706.06438v2#S3.SS3)：vector AMP、局部 Gaussian 等效观测和 Bernoulli–Gaussian MMSE 去噪器。这里将其局部 Gaussian 密度计算独立推广到用户内 \(N\times C\) 坐标和对角异方差，得到 (14)—(20)；不是声称原文已证明本项目结构化 AFDM 的状态演化。原文 §III-B 的渐近条件和 §III-D Theorem 1 不能仅凭当前维数/共同活动形式直接移植。
2. Bayati and Montanari, *The dynamics of message passing on dense graphs, with applications to compressed sensing*, [原文摘要及正文](https://arxiv.org/abs/1001.3448v4)：为 iid Gaussian、大系统条件下的状态演化提供严谨基础。该引用用于标明经典结论的条件，不用于声称它直接覆盖当前所有非可分、阻尼、结构化复矩阵设置。
3. 本文 (3)—(12)、(16)—(25) 是针对当前定义逐项重推的有限维代数。同步历史反馈、Wirtinger 导数、部分迹等术语继续沿用 `docs/TERMINOLOGY.md` 已登记来源；此次不新增方法名称，也不把本控制实验包装成一种已有命名算法。

本阶段足以继续完成解析先验与查询统计控制。恢复神经网络前，仍须看自适应标签和用户块查询分布的实际证据；解析均值正确、完整 Onsager 正确和固定 Gaussian 控制通过，均不能单独保证该恢复步骤成功。

## 10. 完成后的活动控制与最小尺度后续

随后只读核查了 `activity/ROWS.json`、各例末轮 `TRACE.json` 和 `physical_query_audit/REPORT.md`。48 次解析活动控制全部生成有限输出，但 `COMPLETE` 在这里表示完成固定预算，**不表示数值收敛**。按各组 4 场景×3 SNR 的固定预算输出汇总：

| 算子 | 阻尼 | 平均 AER | 末轮相对更新最小值—最大值 |
|---|---:|---:|---:|
| Gaussian 公共归一化 | 1 | 0.1770833 | 0.0186—0.9460 |
| Gaussian 公共归一化 | 0.2 | 0.1937500 | 2.01e-5—0.2370 |
| AFDM | 1 | 0.0520833 | 2.00e-16—0.6630 |
| AFDM | 0.2 | 0.0708333 | 2.34e-11—0.00131 |

这些结果不支持把“Gaussian 算子”直接等同于本尺寸下已经有效的独立 Gaussian-query 接口，也不支持把当前问题简单归结为 AFDM 算子比 Gaussian 更坏。活动摘要中的 `fixed_variance_lmmse_pass=false` 是该阶段没有固定 Gaussian 子项的通用字段结果，不是之前 48 次固定 Gaussian 检查失败。

物理首轮诊断在同形状、同标签参考之外显示了明显的**用户块内行相关**：行相关 RMS 为约 0.253—0.290，而独立 Gaussian 有限样本参考约为 0.0625。完整特征相关的参考背景本来就约为 0.25，报告也已据此比较，未把“经验非零”误作证据。部分束间相关更大。与此同时平均功率比接近 1，说明仅校准平均方差仍可能遗漏去噪器使用的联合结构。这里还没有 Onsager 或网络参与，不能据此单独判定后续 Onsager 的效果或某个网络的失败原因。

建议的最小尺度控制是：Gaussian 算子由 \((Q,K)=(16,40)\) 增至 \((64,160)\)，固定 \(N=16,C=256,L/Q=40,\rho=.1,q=1,\beta=.2\)，沿用同一归一化规则、固定预算及预定 SNR，不搜索参数。这是合理的有限维诊断，但需保留三条解释边界：

1. 它同时降低 \(N/Q\)、增大期望活跃数 4→16、减小活动负载的相对抽样波动；若改善，不能唯一归因于 \(N/Q\)。
2. 不同尺度不是同一样本配对；应报告实际活跃数、\(NK_{\mathrm{active}}/Q\)、用户自 Gram 偏离和相同的查询统计。
3. 应继续区分有限输出、数值收敛、活动正确和查询匹配。固定预算中尚未收敛的 AER 不能描述成稳定解的性能。

同一个真实 \(X\)、同一标签 \(v\) 下，比较解析去噪器对实际首轮查询和人工独立 Gaussian-query 的输出，是有效的离线接口诊断。人工参考使用真值构造，必须明确标为评价层参考，不得进入接收机，也不能把一次对照结果解释成完整闭环性能保证。

## 11. 下一步边界：先核对局部线性增益与似然

2026-10-15 补充：修复式 (15)、(16) 分行时丢失的两个加号，并检查其他分行公式；未发现其他同类遗漏。此修正未改动数学定义或任何实验源。以下是后续可复核的推导建议，尚未运行新实验。

如果解析去噪器在理想 AWGN 查询上正确、在实际首轮查询上错误，应优先检验局部似然的**线性增益和噪声结构**。只估计一个特征协方差后继续训练，不足以解决被忽略的用户自身 Gram 矩阵。

随后读取的 `awgn_control/REPORT.md` 已给出这种差距的条件性证据：Gaussian 算子实际首轮合并 AER 为 18.3333%，同真值/同标签独立 Gaussian 参考为 0.325521%；AFDM 相应为 1.04167% 与 0.208333%。AFDM 在 0、6 dB 的这批实际首轮本来就没有活动错误，不能写成所有实际查询都失效。参考标签来自原观测，可能依赖真值，因此这是固定 \(X,V\) 下的离线响应对照，不是标签独立于信号的总体 Bayes 校准证明。

将 \(A=[A_1,\ldots,A_K]\)，\(A_k\in\mathbb C^{Q\times N}\)，首轮严格分解为

\[
R_k=A_k^HY=G_kX_k+\eta_k,\qquad G_k=A_k^HA_k,
\quad
\eta_k=\sum_{\ell\ne k}A_k^HA_\ell X_\ell+A_k^HW.\tag{26}
\]

对当前匹配 Gaussian 活跃先验，给定其他用户的活动支撑 \(a_{-k}\)，\(\eta_k\) 独立于 \(X_k\)，各特征列为独立 proper Gaussian，行协方差为

\[
S_k(a_{-k})=
q\sum_{\ell\ne k}a_\ell
(A_k^HA_\ell)(A_k^HA_\ell)^H
\quad +\sigma^2G_k.\tag{27}
\]

在活跃条件下，若仍定义 \(E_k=R_k-X_k\)，则

\[
\operatorname{Cov}(E_{k,:,a},X_{k,:,a}\mid a_k=1,a_{-k})
=q(G_k-I_N).\tag{28}
\]

因此把 \(E_k\) 的边际协方差估计准确，也不等于它已成为与 \(X_k\) 独立的噪声。仅在特征维作右侧白化，更不能把左侧增益 \(G_k\) 变成单位阵。

在 \(S_k\) 正定时，局部线性 Gaussian 似然的两种活动协方差为

\[
\Sigma_{0,k}=S_k,\qquad
\Sigma_{1,k}=S_k+qG_kG_k^H.
\]

若 \(r_{k,a}=R_{k,:,a}\)，则

\[
\begin{aligned}
\ell_k&=C[\log\det\Sigma_{0,k}-\log\det\Sigma_{1,k}]
\quad +\sum_a r_{k,a}^H
(\Sigma_{0,k}^{-1}-\Sigma_{1,k}^{-1})r_{k,a},\\
p_k&=\operatorname{sigmoid}(\operatorname{logit}\rho+\ell_k),\\
F_{k,:,a}&=qG_k^H\Sigma_{1,k}^{-1}r_{k,a},\qquad
D_k=p_kF_k.
\end{aligned}\tag{29}
\]

这组公式同时修正均值增益与行协方差，不能用只改 \(C\times C\) 特征协方差的模型代替。它是对 Gaussian 密度和条件均值的直接推导；与第 9 节的局部 Gaussian 去噪原理一致，并未新增方法名称。

给定 \(a_{-k}\) 的式 (27)、(29) 只可用作明确标记的 oracle 诊断。未知其他支撑时，最小的无真值近似是将 (27) 中 \(a_\ell\) 换成公开 \(\rho\)。所得协方差是先验二阶矩匹配，但实际干扰仍是共享活动导致的 Gaussian 混合，特征列在边际上也未必独立；不能称为精确未知支撑后验。

若 \(A_k\) 不满列秩，\(S_k\) 可能奇异，不可机械求逆。可在其支撑子空间使用相应密度，或者先用始终有 \(\sigma^2I_Q\) 正定项的测量域检查：

\[
T_{0,k}=\sigma^2I_Q+q\sum_{\ell\ne k}a_\ell A_\ell A_\ell^H,
\qquad T_{1,k}=T_{0,k}+qA_kA_k^H.\tag{30}
\]

相应对数似然比为

\[
\ell_k^{Y}=C[\log\det T_{0,k}-\log\det T_{1,k}]
\quad +\operatorname{tr}\{Y^H(T_{0,k}^{-1}-T_{1,k}^{-1})Y\},
\qquad F_k^{Y}=qA_k^HT_{1,k}^{-1}Y.\tag{31}
\]

当 \(Q=N\) 且 \(A_k\) 可逆时，\(A_k^HY\) 是可逆变换，式 (29)、(31) 等价。一般 \(Q>N\) 且干扰有色时，未经白化的 \(A_k^HY\) 未必是测量域的充分统计量，二者不能无条件宣称等价。

最小后续是对已有匹配先验数据进行单次局部似然比较：原独立 Gaussian-query 公式、含 \(G_k\) 与先验矩匹配 \(S_k\) 的公式、以及只作诊断的其他支撑已知参考。先区分遗漏线性增益、遗漏行协方差和 Gaussian 混合近似，之后再决定是否需要学习模型。这些首轮公式不能原样推广到后续迭代；若要进入 AMP 闭环，还须重新建立该轮有效查询模型并重算完整导数和历史校正，不能直接沿用旧 Onsager。

## 12. 局部似然控制的只读终审

审查文件为 `local_likelihood_control.py` 及对应 `results/amp_foundation_20261015/local_likelihood_control/{QA.json,SUMMARY.json,REPORT.md}`。脚本 SHA256 为 `c30a5f315a62b0ca43febbaede31c2e8881736818e3d6f4f25c701eaa238e5dd`。本审查未运行该脚本或追加实验。

未发现以下关键接口和数学环节的错误：

- `local_likelihood()` 只接受目标块、其他 \(K-1\) 个块及对应权重。实际 oracle 调用使用 `indices != target_index` 形成 `active[indices]`；自身真实标签只进入评分和保存，没有进入似然或先验概率。
- \(M_0=\sigma^2I+q\sum_{\ell\ne k}\omega_\ell A_\ell A_\ell^H\)、\(S_0=A_k^HM_0A_k\)、\(S_1=S_0+qG_kG_k^H\) 的索引和复共轭正确。
- 两种活动假设共用 \(\operatorname{range}(A_k^H)\) 的 SVD 右奇异子空间。数值秩阈值为 `max(Q,N)*eps*s_max`。零秩退回公开先验；没有对秩亏矩阵直接作全维行列式或逆。
- 复 Gaussian 密度使用 \(C\) 倍 log-determinant 和复二次型，没有多余的实 Gaussian 因子 \(1/2\)。支撑内 Cholesky 与独立特征分解密度分别核验。
- 只评活动概率，不输出均值、更新接收机或计算 Onsager。任何失败都保留，并提供包括失败用户在内的 AER 上下界。

确定性 QA 中，\(Q=N\) 可逆目标的投影/测量域似然差为 `5.33e-15`；秩亏例的支撑内基旋转差为 `1.78e-15`；零秩概率等于先验，多余目标权重被接口拒绝。实际 1920 个用户似然全部完成，支撑秩均为 16，最小正支撑特征值为 `2.22486e-05`，最大条件数约 `9.13890e5`；Cholesky 与特征分解的最大缩放差为 `1.09171e-12`。没有添加对角 ridge，旧冻结源哈希均保持一致。

结果不支持把无条件二阶矩直接视为可用修复：

| 算子 | 原首轮 AER | 保留 \(G_k\)，其他活动取 \(\rho\) | 只给定其他真实活动的 oracle |
|---|---:|---:|---:|
| Gaussian 公共归一化 | 18.3333% | 25.8333% | 0% |
| AFDM | 1.04167% | 25% | 0% |

oracle 合计为 0/960 错误，其余活动的真实支撑是实质性的额外信息。没有泄漏目标标签不等于该 oracle 可以部署。非 oracle 版本的恶化说明：在本批匹配 Gaussian 数据中，保留自 Gram 和无条件协方差仍未正确处理未知干扰活动。不能把这一结果改写为“完整协方差已经解决问题”，也不能据此跳到学习协方差或继续扩大学习模型。

若继续追踪，匹配先验下的整体统计目标可以明确写出。给定一个候选活动向量 \(a\)，各特征列的测量协方差为

\[
\Sigma(a)=\sigma^2I_Q+q\sum_k a_kA_kA_k^H,
\qquad \widehat S_Y=YY^H/C.
\]

于是活动的未归一化对数后验为

\[
\log p(a\mid Y)=\text{const}
\quad -C\{\log\det\Sigma(a)
\quad +\operatorname{tr}[\Sigma(a)^{-1}\widehat S_Y]\}
\quad +\sum_k a_k\operatorname{logit}\rho.\tag{32}
\]

式 (32) 是给定候选支撑的精确 Gaussian 似然加 Bernoulli 先验；未知支撑的求和、边际概率和全局均值仍需推断，不因能计算一个候选的目标值而成为解析解。它指出接下来需检验的对象是**干扰活动的条件化或边际化**，而不是仅用 \(\rho\) 填充协方差。任何近似更新若复用同一观测，也需检查信息重复使用；不能直接把旧概率代入协方差就宣称得到正确消息传递。

这一控制仍然只涉及合成匹配先验的首轮活动判断；不是新 AMP 闭环、物理信道性能或神经网络恢复条件已通过的证据。
