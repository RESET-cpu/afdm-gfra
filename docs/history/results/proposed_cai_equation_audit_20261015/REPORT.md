# 当前 Proposed 与 Cai 的逐式数学核查

2026-10-15。对象为当前默认的相位估计前端、三个冻结网络及条件 TMP 接收机。比较对象为 Cai 的正式论文与 arXiv v2，作者公开程序只用于区分论文写法和实现细节。

**结论：若“同一个级别”指给定工作模型下、由概率计算和明确近似组成的推导完整性，当前 Proposed 与 Cai 的核心推导处于同一层级。本次未发现当前默认条件内核的符号、复数因子、维度归一化或 Gaussian 外信息计算错误。两者都包含统计近似与有限网络；这些共同限制不能仅用来否定本项目。**

该判断不等于两算法逐式相同。当前增加了未知相位的点估计、学习型活动证据、更强的方差共享及额外数值规则；本报告逐项给出它们的数学依据。有限网络是否逼近目标、实际 AFDM 查询是否匹配工作分布、完整循环是否全局收敛，是另外的命题。

## 核查材料与状态

- Origin Skill：academic-research-suite，数学推导与确定性核验。
- Verification Status：解析推导已核对，32项现有测试通过，15组新增合成数学检查通过；不包含新的接收机性能实验。
- [Cai 正式 PDF](../../references/cai2026_score_based_jadce.pdf)，PDF 共16页，结构预检通过；[arXiv v2](https://arxiv.org/html/2506.00581v2)。下文“PDF第几页”采用从1计数的文件页。
- [现有理论](../../docs/THEORY.md)、[当前配置](../../configs/proposed.json)、[未知相位配置](../../configs/proposed_unknown_phase.json)。
- [独立数学检查](MATH_CHECKS.json)、[已有测试记录](TESTS.xml)、[源码和资产身份](MATH_CHECKS.json)。

核查中的“精确”均附着于明确的模型或运算：Gaussian 条件化精确，不表示物理完整后验 Gaussian；Gaussian 消息相除精确，不表示被相除的消息就是精确的物理因子。

## 符号与当前维度

当前 K=40，导频帧数 Q=16，天线数 M=16，AFDM 输出和输入维度 N=P=16。每用户信道有 D=MNP=4096 个复坐标。

实现保存 A₀∈ℂ^(Q×KP)，将所有天线与输出坐标作为 C=MN=256 个测量向量，令 d=KP=640：

\[
Y_0=A_0X_0+W_0,\quad
Y_0\in\mathbb C^{Q\times C},\quad X_0\in\mathbb C^{d\times C}.
\tag{M1}
\]

完整向量算子与 I_C⊗A₀ 只相差固定坐标置换。因而单测量向量协方差的 tr(C_L)/d，与完整协方差的平均迹相同；这里没有漏除天线数或 AFDM 输出维数。

本文 v、γ、τ 都是每个复坐标的方差。实部或虚部噪声方差为 ν=v/2。s=0.2647966452702405 是固定尺度，归一化时 H、Y 除以 s，噪声方差除以 s²，导频不变。

## 观测与先验对应 Cai 式1至5

令 x_k=a_k vec(H_k)，a_k∈{0,1}。在给定固定算子的工作模型下：

\[
y=\mathcal A x+n,\qquad n\sim\mathcal{CN}(0,\sigma^2I),
\quad a_k\sim\mathrm{Bernoulli}(\rho),\quad H_k\sim P_H.
\tag{M2}
\]

假定这些先验因子独立，则 Bayes 公式给出

\[
dq(x,H,a\mid y)\propto
\mathcal{CN}(y;\mathcal A x,\sigma^2I)
\prod_k\left[\delta_{a_kH_k}(dx_k)\,P_H(dH_k)\,
\rho^{a_k}(1-\rho)^{1-a_k}\right].
\tag{M3}
\]

这与 Cai 式(5)是相同的因子分解逻辑。使用概率测度 P_H，允许真实信道先验位于低秩集合，不要求它有全维 Lebesgue 密度。

本项目生成场景条件于至少一人活跃，公开 ρ=p/[1−(1−p)^K] 是边缘概率，联合活动并不独立；此外，物理信道与有效相位共享几何变量，噪声功率随接收信号设置。因此 M3 是明确的计算模型，不能不加条件地称为完整物理生成模型的真实条件后验。这不破坏 M3 内部的后续推导。

Cai 式(1)是活动先验，式(2)是其 OFDM 信道参数化，式(3)–(4)是线性观测。当前 AFDM 参数化不同；矩阵线性关系和后验分解对应，物理模型不要求相同。

## 一般矩阵 LMMSE 对应 Cai 式6至8

对一个测量向量，以 Gaussian 输入消息
\(\mathcal{CN}(x;x_p,\gamma I_d)\) 乘观测似然。展开指数：

\[
\frac{\|y-A_0x\|^2}{\sigma^2}
+\frac{\|x-x_p\|^2}{\gamma}
=x^H\Lambda x-2\Re(x^H\eta)+\mathrm{const},
\quad
\Lambda=\gamma^{-1}I+\sigma^{-2}A_0^HA_0,\quad
\eta=\gamma^{-1}x_p+\sigma^{-2}A_0^Hy.
\tag{M4}
\]

配方得到精确 Gaussian 条件矩：

\[
C_L=\Lambda^{-1},\qquad m_L=C_L\eta.
\tag{M5}
\]

用矩阵求逆恒等式改写：

\[
G=\gamma A_0^H(\sigma^2I+\gamma A_0A_0^H)^{-1},
\quad m_L=x_p+G(y-A_0x_p),\quad
C_L=\gamma I-\gamma GA_0.
\tag{M6}
\]

共享标量是受限 Gaussian 矩匹配：

\[
t_L=\operatorname{tr}(C_L)/d
=\gamma-\frac{\gamma^2}{d}
\sum_i\frac{s_i^2}{\sigma^2+\gamma s_i^2}.
\tag{M7}
\]

s_i 是 A₀ 的奇异值。若 A₀≠0、γ>0、σ²>0，则 0<t_L<γ。证明是 C_L 的特征值为
\((\gamma^{-1}+\sigma^{-2}\lambda_i)^{-1}\)，均在(0,γ]，至少一个严格小于γ。

在 Cai 的部分正交设定 \(A_0A_0^H=\alpha I_q\) 下，

\[
m_L=x_p+\frac{\gamma}{\sigma^2+\gamma\alpha}A_0^H(y-A_0x_p),
\quad
t_L=\gamma-\frac qd\frac{\gamma^2\alpha}{\sigma^2+\gamma\alpha}.
\tag{M8}
\]

代入 q=TN、d=KN、α=KP_C，其中 P_C 是 Cai 的发射功率，即恢复其式(7)–(8)。当前 SVD 实现计算一般形式 M6–M7，是合理推广，线性代数精确度并未降低。Gaussian 共享标量投影则是双方均采用的近似。
这一推广只涉及LMMSE代数，并不把特定随机矩阵下的伪AWGN或状态演化保证一并推广到本项目算子。

实现：[linear.py](../../src/afdm_jadcedd/algorithm/proposed/linear.py)。验证包括一般矩阵与独立稠密精度求逆比较，以及退化到部分正交公式。

## 线性外信息对应 Cai 式9至14

先将 Gaussian 条件分布投影为 \(\mathcal{CN}(x;m_L,t_LI)\)，再除以输入消息。两个指数相减给出

\[
\lambda_{\rm ext}=t_L^{-1}-\gamma^{-1},\quad
\eta_{\rm ext}=m_L/t_L-x_p/\gamma,
\quad v=\lambda_{\rm ext}^{-1},\quad r=v\eta_{\rm ext}.
\tag{M9}
\]

由 M7，线性模块这一方向的外信息精度严格为正。**精确的是先投影后的 Gaussian 相除**；它不等同于完整协方差似然因子的无损传播。Cai 式(9)–(11)采取同一做法。

令 κ=1−t_L/γ、L=G/κ，可化简为

\[
r=x_p+L(y-A_0x_p),\qquad
v=\gamma(1-\kappa)/\kappa.
\tag{M10}
\]

当前代码的 fraction 是 κ，correction/fraction 即 M10。分块取出用户坐标、重排天线和信道坐标，对已投影的独立 Gaussian 消息只是坐标运算，对应 Cai 式(12)–(14)。

若实际算子为 A 而使用 \(\widehat A\)，冻结本次线性系数、先不计历史阻尼，直接展开可得

\[
r-x=(L\widehat A-I)(x-x_p)+L(A-\widehat A)x+Ln.
\tag{M11}
\]

这是一条代数恒等式；它没有断言右侧与 x 独立或为白 Gaussian。Cai 的伪 AWGN 解释也不是从 Gaussian 相除单独推出的。

## 活动条件分解对应 Cai 式15至23

给定单用户工作查询

\[
R=aH+W,\quad W\sim\mathcal{CN}(0,vI_D),\quad
q_0(R)=\mathcal{CN}(R;0,vI),\quad
q_1(R)=\int\mathcal{CN}(R;H,vI)P_H(dH),
\tag{M12}
\]

总归一化量为 \(Z=(1-\rho)q_0+\rho q_1\)。分别对 a=0、1 积分：

\[
p^*(R)=\Pr(a=1\mid R)=\frac{\rho q_1(R)}{Z},\qquad
dP(H\mid R,a=1)=\frac{\mathcal{CN}(R;H,vI)P_H(dH)}{q_1(R)}.
\tag{M13}
\]

记活跃条件均值 µ=E[H|R,a=1]、协方差 Σ_H。由于 X=aH，

\[
E[X\mid R]=p^*\mu,\qquad
\operatorname{Cov}(X\mid R)=p^*\Sigma_H+p^*(1-p^*)\mu\mu^H.
\tag{M14}
\]

推导只需 \(E[XX^H|R]=p^*(\Sigma_H+\mu\mu^H)\)，再减去均值外积。
**在 M12 下，活动与活跃条件信道分开计算然后组合，本身没有丢失 X 的一、二阶矩。**
µ 不能被混称为不条件于活动的潜在 H 的均值。a=0 时潜在 H 的分布仍是 P_H，而有效信道 X 为0。

Cai 式(15)的消息是关于 H 的“常数项＋Gaussian 项”，式(16)明确选择活跃条件项；作为原消息的替换属于近似。M13–M14说明，对于 X 的局部后验矩，另行正确计算活动证据后，这种条件分解可以严格成立。后续有限网络、Gaussian 条件密度和近似活动证据的替换，应分别评价。

Cai 式(17)是 Gaussian 矩投影，式(18)/(22)是条件均值，式(23)是按用户与坐标平均的条件中心方差。原式(20)/(21)和(43)提供伪 AWGN 工作模型；其在有限真实迭代中的正确性需要另证，双方标准相同。

### Cai 式19的中心与式23不一致

正式 PDF 第6页、印刷页3580，以及 arXiv v2 式(19)，积分内写的是
\(|h_{knm}-h^{\mathrm{pri}}_{knm}|^2\)；而式(23)称其为条件方差。恒等式为

\[
E[|H-R|^2\mid R]
=\operatorname{Var}(H\mid R)+|E[H\mid R]-R|^2.
\tag{M15}
\]

例如 H∼CN(0,1)、噪声 v=1、R=2，条件均值为1，条件方差为1/2，以 R 为中心的二阶矩却为3/2。
所以式(19)若要等于式(23)，中心应为 post 而非 pri。本报告按式(23)及 Tweedie 方差解释其意图；
这是核对到的局部符号不一致，尚无作者勘误确认，不能据此推断其实验代码使用了错误中心。
当前代码没有实现这个错误中心。

## 实复坐标 Tweedie 公式对应 Cai 式43至45及55至56

设 u=(Re R, Im R)∈ℝ^(2D)，h_R 为相同实坐标表示，ν=v/2。平滑密度

\[
q_\nu(u)=\int(2\pi\nu)^{-D}
\exp[-\|u-h_R\|^2/(2\nu)]P_H(dh_R).
\tag{M16}
\]

允许交换求导与积分时，对核求导得到

\[
\nabla_u\log q_\nu(u)=\frac{E[h_R\mid u]-u}{\nu}.
\tag{M17}
\]

因此 \(m_R=u+\nu\nabla\log q_\nu\)。再对归一化条件均值求导，分母导数消去均值外积，得到

\[
\frac{\partial m_R}{\partial u}=\frac{C_R}{\nu},\qquad
C_R=\nu I_{2D}+\nu^2\nabla_u^2\log q_\nu.
\tag{M18}
\]

复坐标平方误差等于实坐标总平方误差，故

\[
\tau_C=\frac{\operatorname{tr}C_R}{D}
=v+\frac{v^2}{4D}\operatorname{tr}(\nabla_u^2\log q_\nu).
\tag{M19}
\]

当前网络给出实坐标一阶 score 估计 S₁ 与二阶输出 S₂；记 \(\mathcal A\) 为2D个实坐标的平均，则读出为

\[
F=R+\frac v2(S_{1,\Re}+iS_{1,\Im}),\qquad
\widehat\tau=v\left[1+\frac v2\mathcal A(S_2)\right].
\tag{M20}
\]

当 S₂ 的平均对应真实 Hessian 的平均迹时，M19与M20一致：
\(\mathcal A(S_2)=\operatorname{tr}S_2/(2D)\)。有限网络的输出是否达到该目标须另行评价。
Cai 使用复梯度记号；按其 Gaussian 核导数约定换成实部、虚部实现，必须出现 v/2。当前实现与作者公开程序的实复换算相符。

Gaussian 卷积使 qν 有正的光滑密度，即使 P_H 支撑在低秩集合，M17仍有定义；适当矩及可积性条件下 M18成立。不能因为先验低秩就否定这些恒等式。

若 checkpoint 坐标为 cR，噪声标签必须是 c²v，最后均值除以 c、方差除以 c²：

\[
F(R,v)=c^{-1}F_{\rm ckpt}(cR,c^2v),\qquad
\widehat\tau(R,v)=c^{-2}\widehat\tau_{\rm ckpt}(cR,c^2v).
\tag{M21}
\]

[moments.py](../../src/afdm_jadcedd/algorithm/proposed/moments.py)实现该换算；当前 c=1。独立 Gaussian 闭式例子另检验了 c=1.7 的非平凡换算。

## 一阶与二阶训练对应 Cai 式46至54

令 \(\varepsilon=(u-h_R)/\sqrt\nu\)，则当前一阶损失为

\[
\mathcal L_1
=E\,\mathcal A[(\sqrt\nu S_1+\varepsilon)^2]
=E\frac{\|F-H\|^2}{Dv}.
\tag{M22}
\]

固定 u,v 后，平方损失的最优预测为条件均值，因此

\[
S_1^*(u,v)=-E[\varepsilon\mid u,v]/\sqrt\nu
=\nabla_u\log q_\nu(u).
\tag{M23}
\]

这直接给出 DSM 与一阶 score 的等价最优解，和 Cai 式(46)–(49)同层级。正的噪声权重、维度归一化和实复常数不改变每个噪声水平的函数空间最优解；当前连续噪声采样与 Cai 的离散噪声级并非同一有限优化问题。

冻结有限 S₁，令 \(b=\sqrt\nu S_1+\varepsilon=(F_R-h_R)/\sqrt\nu\)，当前二阶损失是

\[
\mathcal L_2
=E\{\mathcal A(\nu S_2-b^2+1)\}^2
=E\left[\frac{\widehat\tau}{v}
-\frac{\|F-H\|^2}{Dv}\right]^2.
\tag{M24}
\]

是先平均再平方，和 Cai 式(53)–(54)的总迹回归结构对应。固定 R,v 后写 U=||F−H||²/(Dv)，

\[
E[(a-U)^2\mid R,v]=(a-E[U\mid R,v])^2
+\operatorname{Var}(U\mid R,v).
\tag{M25}
\]

于是二阶读数的函数空间最优值为

\[
\tau_F=\frac1D E[\|F-H\|^2\mid R,v,a=1]
=\tau_C+\frac{\|F-m\|^2}{D}.
\tag{M26}
\]

最后一步展开 F−H=(F−m)+(m−H)，交叉项的条件期望为0。
**有限一阶网络下得到条件风险而非精确中心方差，这个结论同样适用于 Cai 式(52)–(54)用有限 S₁ 替代理想 score 的做法。**
它不应只被列为本项目特有缺陷。

### 总迹监督的识别范围

对任意逐样本 tr(Δ)=0 的扰动，以 S₂+Δ 替换 S₂，不改变 M24。故总迹损失只识别总迹。
Cai 式(53)按字面也是总迹损失，而式(56)读出逐天线的子迹；仅由式(53)，不能推出这些不同子迹各自正确。
若依赖额外架构或对称性约束，需要另外说明。这是监督目标的识别范围问题，不等于已证明其实际网络子迹错误。
当前全坐标平均读出与已监督的总迹相符，不能把输出张量的各元素直接当作已识别的 Hessian 对角元。

实现：[direct_objectives.py](../../src/afdm_jadcedd/experiment/training/scores/direct_objectives.py)。
独立检查同时验证实际两个损失与复数 MSE 的关系，以及改变天线子迹、保持总迹时损失不变。

## 共享条件方差与活跃 Gaussian 消息

当前先在用户内得到风险读数，再在用户间普通平均并施加下限：

\[
\bar\tau_{\rm raw}=K^{-1}\sum_k\widehat\tau_k,\qquad
\tau=\max(\bar\tau_{\rm raw},10^{-4}).
\tag{M27}
\]

其受限拟合解释是：对每用户“假定其活跃”的条件分布，用固定中心 F_k 和共同方差 τ 的 Gaussian 近似。期望负对数密度为

\[
\mathcal J(\tau)=KD\log(\pi\tau)+\frac{D\sum_k\tau_{F,k}}{\tau},
\quad
\mathcal J'(\tau)=\frac{KD(\tau-\bar\tau_F)}{\tau^2}.
\tag{M28}
\]

所以无下限时最优值为风险的普通平均；施加 τ≥10⁻⁴ 后得到相同形式的受限最优值。代码使用网络读数替代真实风险。这说明普通平均有明确的拟合目标；它仍会丢失用户间不确定性的差异。

Cai 式(23)/(38)本来也跨用户和信道坐标平均，并在式(43)前将查询的天线方差进一步平均。当前在整个循环采用共同各向同性方差，比其最终保留逐天线量更强，但属于同一 Gaussian 投影方法内的限制。不能把“我们跨用户平均、Cai完全不平均”作为差别。

用 \(\mathcal{CN}(H;F_k,\tau I)\) 除以查询因子 \(\mathcal{CN}(R_k;H,vI)\)，对应 Cai 式(24)–(27)：

\[
c_k=(\tau^{-1}-v^{-1})^{-1},\qquad
e_k=c_k(F_k/\tau-R_k/v).
\tag{M29}
\]

指数的二次项与一次项直接相减。再与查询相乘：

\[
t_k=(c_k^{-1}+v^{-1})^{-1},\qquad
\mu_k=t_k(e_k/c_k+R_k/v).
\tag{M30}
\]

若本轮接受新 site，则代入得 t_k=τ、µ_k=F_k，完全恢复原矩，和 Cai 式(33)–(34)一致。**这里没有对 F 再去噪一次，也没有重复扣噪。**

### 正精度条件的边界

当前只在 0<τ<v 时接受 M29，否则保留旧 e_k,c_k，再由 M30计算当前条件矩。
这是为了让活跃 Gaussian site 可单独归一化，属于实际算法的数值策略。

一般后验方差不必逐查询小于 v：令 H 均匀取 ±2、±2i，R=0、v=1，则条件方差为4；
M29 的精度为1/4−1<0。这个反例同样限制 Cai 式(25)–(27)把该比值直接称为 Gaussian pdf 的适用条件。
EP 可以在其他设计中保留不能单独归一化的 site，但那需要保证组合后的分布及后续活动积分有效，不能无条件套用这里的归一化 Gaussian 公式。

## 两种活动证据对应 Cai 式28至31

### 归一化 Gaussian site 的解析证据

若活跃工作先验为 CN(e_k,c_k I)，卷积直接给出

\[
q_1^G(R_k)=\int\mathcal{CN}(R_k;H,vI)
\mathcal{CN}(H;e_k,c_kI)dH
=\mathcal{CN}(R_k;e_k,(v+c_k)I).
\tag{M31}
\]

所以 log 密度比和活动概率为

\[
\ell_k^G=
\frac{\|R_k\|^2}{v}
-\frac{\|R_k-e_k\|^2}{v+c_k}
-D\log(1+c_k/v),\qquad
p_k^G=\operatorname{sigmoid}(\operatorname{logit}\rho+\ell_k^G).
\tag{M32}
\]

这正是 Cai 式(28)–(30)在共同方差下的 log 形式，归一化常数不可丢。当前仅在网络支持外使用此回退。
当 site 刚被接受时，等价式为

\[
\ell_k^G=\frac{\|R_k\|^2}{v}
-\frac{\|R_k-F_k\|^2}{v-\tau}
+D\log(1-\tau/v).
\tag{M33}
\]

M31–M33是对所选 Gaussian site 的精确计算。由于该 site 来自当前查询的矩匹配，它不自动等于原物理先验 P_H，更不自动给出原 P_H 的精确归一化证据。单点均值和协方差不足以唯一确定该证据。

### 当前支持范围内的 BCE 分类器

训练两类共享同一噪声方差抽样律 g(v)，训练活动比例 π=1/2，活跃类来自 P_H，非活跃类为0加噪声。
在固定 R,v 下，训练条件概率为

\[
\eta_{\rm tr}
=\frac{\pi q_1(R)}{(1-\pi)q_0(R)+\pi q_1(R)}.
\tag{M34}
\]

令 logit 输出 z，条件 BCE 为

\[
B(z)=\log(1+e^z)-\eta_{\rm tr}z,\quad
B'(z)=\operatorname{sigmoid}(z)-\eta_{\rm tr},\quad
B''(z)>0.
\tag{M35}
\]

因而最优 logit 为

\[
z^*=\operatorname{logit}\pi+\log(q_1/q_0),\qquad
p=\operatorname{sigmoid}\{\operatorname{logit}\rho+z_\phi-\operatorname{logit}\pi\}.
\tag{M36}
\]

这是一项有独立 Bayes 推导的替换。理想分类器下，它直接恢复 M13 的活动概率，无须先将活跃信道先验拟合成 Gaussian。
有限分类器是否准确，以及实际查询是否服从训练类条件分布，需另行验证；其理论依据并不比解析近似证据更低一层。

当前分类器保留完整 R、v，并额外使用确定性特征 F(R,v)。给定 R,v 后 F 不增加随机信息，也不会因为同时输入 F 而把物理观测在 Bayes 公式中计入两次。公开先验只在 M36加入一次。

代码即使拒绝新 site，只要 v∈[10⁻³,100]，仍使用本轮 R,v,F 查询分类器；支持外则复用 site 并使用 M32。
前一种情况下，活动概率与信道条件矩来自不同近似，仍可构成下节的有效混合分布，但不能称为某个固定先验下已验证的一致精确后验。

依据：[Menon–Ong 2016 §2.2、§3、§4.2](https://proceedings.mlr.press/v48/menon16.pdf)，以及本项目上述条件 BCE 直接推导。
实现：[activity.py](../../src/afdm_jadcedd/algorithm/proposed/activity.py)、[denoiser.py](../../src/afdm_jadcedd/algorithm/proposed/denoiser.py)、[posterior.py](../../src/afdm_jadcedd/algorithm/proposed/posterior.py)。

## 联合矩与反馈对应 Cai 式32至42

实际算法明确选定

\[
\widetilde q_k(X_k)=(1-p_k)\delta_0(X_k)
+p_k\mathcal{CN}(X_k;\mu_k,t_k I_D).
\tag{M37}
\]

只要 p_k∈[0,1]、t_k>0，这就是合法的局部混合分布。它的一、二阶矩为

\[
\widehat X_k=p_k\mu_k,\quad
\Sigma_{X,k}=p_kt_kI_D+p_k(1-p_k)\operatorname{vec}\mu_k
(\operatorname{vec}\mu_k)^H.
\tag{M38}
\]

令 B=NP=256，将 µ_k 排成 M×B。各列天线协方差的平均为

\[
C_{X,k}=p_kt_k I_M+\frac{p_k(1-p_k)}B\mu_k\mu_k^H,\qquad
\bar t_X=\frac1{KM}\sum_k\operatorname{tr}C_{X,k}.
\tag{M39}
\]

因此
\(\bar t_X=K^{-1}\sum_k[p_kt_k+p_k(1-p_k)\|\mu_k\|_F^2/D]\)。
分母 B、M、K共同恢复完整 D 维的平均方差；没有多乘或少乘一次 p_k。
Cai 式(35)–(36)与此一致；式(37)–(38)同样对混合矩作 Gaussian 投影。
当前虽临时构造 C_X,k，默认随后仅保留平均迹，不向下轮传递完整空间或跨信道坐标协方差。

未裁剪时，投影后验 CN(\(\widehat X,\bar t_X I\)) 除以查询 CN(r,vI)：

\[
b=\bar t_X/v,\quad
\gamma_{\rm out}=\frac{vb}{1-b},\qquad
x_{\rm out}=\frac{\widehat X-br}{1-b}.
\tag{M40}
\]

这与 Cai 式(39)–(42)相同，要求 0<b<1 才是可归一化的输出 Gaussian。
当前先令 \(\widetilde b=\operatorname{clip}(b,10^{-6},1-10^{-6})\)，再在 M40 中使用 \(\widetilde b\)。
于是它是对调整后方差 \(v\widetilde b\) 的精确 Gaussian 相除，不再是原始混合方差的精确相除；改变仅在裁剪触发时发生。

M38–M39严格对应所选混合分布，即使其参数是近似的。不能将“矩公式精确”误写成“该混合分布等于物理真实后验”。

## 阻尼、初始化与停止对应 Cai 式57至58及31

当前在线性模块到非线性模块、非线性模块到线性模块两个方向，分别插值均值与协方差。令新值权重 η=0.2：

\[
m^{(i)}=(1-\eta)m^{(i-1)}+\eta m_{\rm raw}^{(i)},\qquad
C^{(i)}=(1-\eta)C^{(i-1)}+\eta C_{\rm raw}^{(i)}.
\tag{M41}
\]

第一轮没有旧消息，直接采用新值。旧值是上一轮已阻尼的值。
这与Cai论文式(57)–(58)的均值、方差阻尼类型一致，也与作者冻结程序第110–127行的递归实现一致。
它既不是 Gaussian 自然参数的插值，也不是两个 Gaussian 分布的混合矩匹配：
后者还应有 \(\eta(1-\eta)(m_{\rm raw}-m_{\rm old})(m_{\rm raw}-m_{\rm old})^H\) 项。
因此，代码函数名 moment_damp 应按其实际算式理解，不能据名字赋予它额外的后验含义。

若一个确定性的完整状态更新为 T(z)，简单阻尼
\(z'=(1-\eta)z+\eta T(z)\) 在 η>0 时具有相同不动点，因为 z'=z 等价于 T(z)=z。
这不证明迭代必收敛，也不证明收敛点是全局最优。当前还有保留旧 site 的历史状态，分析时必须纳入完整状态。

初始化采用 \(x_p=0,\ \gamma_0=\rho\,1.0004404181394917\)，即公开活动率乘训练归一化信道二阶矩。
它是初始 Gaussian 消息的矩设定。实际正数下限只用于数值保护。

最终判决为

\[
\widehat a_k=\mathbf1\{p_k\ge0.5\}.
\tag{M42}
\]

对于正确的后验概率、相等的漏检与误报损失，0.5可由最小条件风险推出；对于近似 p，它是同一判决规则，不能自动声称真实 Bayes 最优。

当前最多600轮、至少60轮。连续5轮要求：信道均值与输入协方差相对变化小于0.003，
活动概率最大变化小于0.0001，并通过消息更新和原始 site 残差检查；活动判决需连续10轮一致。
site 自然参数残差阈值为0.01，活动概率与停止参考值的残差阈值为0.0001。
参考值按 \(w^{(i)}=0.8w^{(i-1)}+0.2p^{(i)}\) 更新，仅用于停止判据。
推断中的混合权重仍为本轮 p，不是 w。这些检查提供可复现的有限停止规则，不构成收敛定理。

实现：[iterations.py](../../src/afdm_jadcedd/algorithm/proposed/iterations.py)、[denoiser.py](../../src/afdm_jadcedd/algorithm/proposed/denoiser.py)。
作者程序参照：[冻结副本](../cai_alignment_20261014/author_main_stmp_jadce.py.txt)，来源提交
0c75680c966dcb8e46250de146f4c27e9294c283。该程序的活动证据使用固定零均值 Gaussian 先验，
不能把该实现细节反过来当作 Cai 式(30)的一般定义。

## 固定尺度与 Cai 式59至65的功率归一化

当前固定 s 的归一化和 M21 的 checkpoint 换算，是确定性的坐标变换。Cai 的逐查询功率归一化多了一步统计估计。
对于 R=H+W、W∼CN(0,vI_D)，直接展开：

\[
\|R\|^2-Dv
=\|H\|^2+2\Re(H^HW)+\|W\|^2-Dv.
\tag{M43}
\]

因此正确的期望关系与条件方差为

\[
E[\|R\|^2-Dv\mid H]=\|H\|^2,\qquad
\operatorname{Var}(\|R\|^2-Dv\mid H)
=Dv^2+2v\|H\|^2.
\tag{M44}
\]

证明：Gaussian 噪声的二次项方差为 Dv²，线性项方差为2v‖H‖²；其协方差由零三阶矩为0。
例如标量 H=1、W=1、v=1，观测功率减噪为3，而真实功率为1。
所以Cai正式 PDF 第10页、印刷页3584的式(59)，按字面不是逐样本恒等式。
它可以理解成期望关系下的功率估计，或在额外集中条件下的近似；还需处理估计值非正的情况。
这一点不否定后续坐标缩放的代数，但必须明确被缩放的量是估计值。

令每用户估计功率 \(\widehat P_k=(\|R_k\|^2-Dv)/D\)。
如果将尺度暂时视作固定，式(60)对输入使用 \(c_k=\widehat P_k^{-1/2}\) 后，配套噪声方差应为

\[
v_k'=c_k^2v=v/\widehat P_k,
\quad\text{而式(61)使用}\quad
\bar v'=\frac{v}{K^{-1}\sum_k\widehat P_k}.
\tag{M45}
\]

二者通常不相同。取两用户功率1、4，v=0.5，正确的各自标签为0.5、0.125，共同标签为0.2。
所以式(60)–(61)包括额外的噪声方差共享，并非严格的逐用户坐标变换。
此外，实际 c_k 是当前 R_k 的函数；随机归一化后的噪声与信道关系也不能直接沿用固定尺度的独立 AWGN 假设。
式(62)–(63)是在这个近似归一化工作模型上调用 Tweedie 读数，式(64)–(65)再按各自选定的尺度还原。
当前没有采用这组逐查询功率估计，不能把它当作本项目推导必须照搬的一环。

## 当前未知相位前端的独立推导

Cai 的式(1)–(66)不包含本项目的未知跨帧相位前端。当前先从观测估计相位，再构造固定算子交给上述循环。
对用户 k，以单个主导路径表示其用于相位拟合的观测，令 u(θ)∈ℂ^L 为给定时延和 Doppler 的导频响应，
g∈ℂ^(1×M)为自由复天线增益，R为暂时扣除其他用户后的观测：

\[
J(\theta,g)=\|R-u(\theta)g\|_F^2,\quad
g^*(\theta)=\frac{u(\theta)^HR}{u(\theta)^Hu(\theta)},
\quad
J_{\rm red}(\theta)=\|R\|_F^2-
\frac{\|u(\theta)^HR\|^2}{u(\theta)^Hu(\theta)}.
\tag{M46}
\]

这是对线性参数 g 的精确最小二乘消元，要求 u≠0。对复增益完成平方即可得到。
令 E=R−ug*，则 uᴴE=0；因此求导时含 ∂g*/∂θ 的项为0，得到

\[
\frac{\partial J_{\rm red}}{\partial\theta_j}
=-2\Re\langle(\partial u/\partial\theta_j)g^*,E\rangle_F.
\tag{M47}
\]

代码的梯度正是 M47。导数在既定时延分支内成立；跨分支由候选搜索处理。
相位与物理 Doppler 使用同一 ν_D：

\[
\beta_k=2\pi\nu_{D,k}T_{\rm frame},\qquad
\widehat A_{q,k,p}=P_{q,k,p}\exp(iq\widehat\beta_k).
\tag{M48}
\]

实际采用候选筛选、Doppler 混叠分支细化、有限次局部优化、两轮用户循环和联合增益最小二乘。
M46–M47对选定的单路径拟合模型成立，有限搜索不等于已找到全局最优，
单路径模型也不等于完整多径生成模型。后续条件循环使用 \(\widehat A\)，没有对相位不确定性积分。
所以可以称“相位点估计＋给定估计相位的条件推断”，不能声称完整的联合相位、活动、信道精确后验计算。

实现：[phase_estimation.py](../../src/afdm_jadcedd/algorithm/phase_estimation.py)、
[unknown_phase_model.py](../../src/afdm_jadcedd/algorithm/unknown_phase_model.py)。
variable projection 的原文来源已登记于 [TERMINOLOGY.md](../../docs/TERMINOLOGY.md)，
这里的 AFDM 代入和导数为项目推导。

## Cai 式1至66逐项覆盖表

“成立”均相对于表内指定的模型或运算；“近似”不等于推导错误。
同一式的条件、证明与代码入口见前文对应 M 式。

| Cai 式 | 原式作用 | 当前对应与核查结果 |
|---|---|---|
| (1) | 活动指示变量 | M2：二值变量及 Bernoulli 工作先验；非空场景条件化差异已说明。 |
| (2) | 物理 OFDM 信道 | 当前为 AFDM 信道；不要求同一参数式，不能直接移植其信道坐标。 |
| (3) | 每时频点观测 | M1–M2：对本项目物理模型构造线性观测；AFDM 展开有现有测试。 |
| (4) | 堆叠矩阵观测 | M1：MMV 重排等价；未知相位时条件于 M48 的估计算子。 |
| (5) | 后验因子分解 | M3：在独立先验及固定噪声工作模型下成立。 |
| (6) | 似然乘输入 Gaussian | M4–M5：配方严格成立。 |
| (7) | 线性后验均值 | M6、M8：一般矩阵公式严格退化到部分正交特例。 |
| (8) | 共享线性后验方差 | M7–M8：平均迹公式正确；共享是 Gaussian 投影约束。 |
| (9) | 线性后验除输入消息 | M9：对投影后 Gaussian 精确。 |
| (10) | 线性外信息方差 | M9–M10：精度相减且这一方向严格正。 |
| (11) | 线性外信息均值 | M9–M10：自然参数相减，代数与代码一致。 |
| (12) | 用户块边缘消息 | M9之后的坐标取块；对于独立 Gaussian 消息精确。 |
| (13) | 重排后的消息乘积 | M1、M9：对该投影消息的重排精确。 |
| (14) | 用户输入 Gaussian | M12：给出局部查询密度，不自动证明实际查询为 AWGN。 |
| (15) | 活动求和后的信道消息 | M12–M14：常数项加活跃 Gaussian 项，未误当单一 Gaussian。 |
| (16) | 选择活跃条件项 | M13：相对原信道消息是近似；与正确活动概率组合可给出 X 的精确局部矩。 |
| (17) | 信道 Gaussian 投影 | M19、M27–M28：受限均值和平均方差拟合。 |
| (18) | 活跃信道条件均值积分 | M13、M17：理想 score 下相同。 |
| (19) | 信道二阶积分 | M15：印刷的 pri 中心与式(23)中心方差不一致；按 post 中心理解。 |
| (20) | 伪 AWGN 模型 | M12：工作模型；不是任意有限 AFDM 迭代的恒等式。 |
| (21) | AWGN 似然乘积 | M12、M16：在独立白 Gaussian 假设下成立。 |
| (22) | 条件 MMSE 均值 | M13、M17：理想 score 成立，有限网络为近似。 |
| (23) | 条件中心方差平均 | M18–M20、M26：理想二阶 score 成立，有限一阶替代需区分条件风险。 |
| (24) | 活跃信道消息相除 | M29：对 Gaussian 矩近似相除。 |
| (25) | 相除后的 Gaussian 表示 | M29：要求可归一化的正精度；不对任意先验逐查询自动成立。 |
| (26) | 活跃 site 方差 | M29：当前只接受0<τ<v；否则沿用旧 site。 |
| (27) | 活跃 site 均值 | M29–M30：相除后再乘查询可恢复接受的条件矩。 |
| (28) | 活动证据积分 | M31：归一化 Gaussian site 卷积严格成立。 |
| (29) | Bernoulli 活动后验 | M32或M36：所选证据归一化为活动概率。 |
| (30) | Gaussian 活动概率 | M32–M33为对应式；当前支持内用有独立 Bayes 推导的M36替换。 |
| (31) | 活动门限判决 | M42：0.5规则；真实最优性取决于概率准确性及损失。 |
| (32) | 活跃／非活跃混合 | M37：合法 Bernoulli–Gaussian 工作分布。 |
| (33) | 活跃 Gaussian 乘积方差 | M30：精度相加，成立。 |
| (34) | 活跃 Gaussian 乘积均值 | M30：自然参数相加，成立。 |
| (35) | 有效信道后验均值 | M38：pµ，精确混合矩。 |
| (36) | 有效信道后验元素方差 | M38：p t+p(1−p)|µ|²，精确混合矩。 |
| (37) | 混合分布的 Gaussian 投影 | M38–M39：保留均值及受限协方差。 |
| (38) | 共享方差平均 | M39：当前进一步跨天线平均，归一化维度正确。 |
| (39) | 反馈消息相除 | M40：Gaussian 相除；发生裁剪时对应调整后的方差。 |
| (40) | 反馈 Gaussian 表示 | M40：正精度条件由裁剪保证。 |
| (41) | 反馈外信息方差 | M40：v b/(1−b)，与代码一致。 |
| (42) | 反馈外信息均值 | M40：(X̂−b r)/(1−b)，与代码一致。 |
| (43) | 统一噪声方差的 AWGN 模型 | M12、M16：Cai 也在此平均天线方差；当前整个默认循环共享标量。 |
| (44) | 一阶 Tweedie 均值 | M17、M20：实坐标系数v/2正确。 |
| (45) | 二阶 Tweedie 协方差 | M18–M20：复坐标平均方差与实 Hessian 迹换算正确。 |
| (46) | 一阶 score 匹配目标 | M22–M23：函数空间最优解一致。 |
| (47) | 一阶 denoising score matching | M22–M23：平方损失条件化证明成立。 |
| (48) | Gaussian 核导数代入 | M22：实噪声方差ν=v/2，实际代码已单独核验。 |
| (49) | 多噪声级加权训练 | M22–M23：当前连续采样，有限训练问题不逐项相同。 |
| (50) | 理想二阶 score 匹配 | M18：若理想 Hessian 可得，则给出条件协方差。 |
| (51) | 理想一阶 score 下的二阶目标 | M24–M26：理想F=m时，条件风险退化为中心方差。 |
| (52) | 有限一阶网络替代 | M26：多出‖F−m‖²/D；双方均有这一项。 |
| (53) | 总迹监督 | M24–M26：只识别总迹，不能单独识别逐天线子迹。 |
| (54) | 多噪声级二阶训练 | M24：实际训练损失与总条件风险回归代数一致。 |
| (55) | 一阶网络均值读出 | M20–M21：当前实复因子及尺度换算正确。 |
| (56) | 二阶网络方差读出 | M19–M20：当前读出总迹；原文逐天线子迹需额外识别依据。 |
| (57) | 均值阻尼 | M41：同类算术插值；不是新增后验恒等式。 |
| (58) | 方差阻尼 | M41：两个方向均实施；不是 Gaussian 混合协方差。 |
| (59) | 查询功率减噪 | M43–M44：应理解为无偏功率估计，不能写成逐样本精确等式。 |
| (60) | 逐用户输入缩放 | M45：原文使用估计尺度；当前固定尺度用M21。 |
| (61) | 共同噪声标签缩放 | M45：与逐用户尺度通常不一致，是额外共享近似。 |
| (62) | 归一化后的均值读出 | M20–M21：公式成立依赖输入及噪声标签匹配工作模型。 |
| (63) | 归一化后的方差读出 | M20、M26、M45：还受有限网络和总迹识别范围限制。 |
| (64) | 信道均值尺度还原 | M21：对于选定固定尺度，线性还原精确。 |
| (65) | 方差尺度还原 | M21、M45：当前固定尺度平方还原精确；原文含共同尺度近似。 |
| (66) | 部分正交导频 | M8：本项目不依赖该特例，一般矩阵LMMSE已覆盖。 |

## 独立数学核验与限制

新增检查使用小维度合成数据或解析反例，不调用真实信道真值来改善接收机输出，也不构成新的性能结论。
检查直接调用当前核心实现，再与独立矩阵计算、条件枚举或数值积分比较。

| 检查 | 结果 |
|---|---|
| 一般矩阵LMMSE与外信息，对比稠密精度矩阵条件化 | 最大绝对差2.07×10⁻¹⁵ |
| 含相位算子误差的查询误差恒等式M11 | 最大绝对差9.93×10⁻¹⁶ |
| Cai式(19)/(23)中心差异的Gaussian反例 | 中心方差0.5；按pri中心二阶矩1.5 |
| 活跃条件分解后重组，对比联合有限先验枚举 | 最大绝对差7.76×10⁻¹⁸ |
| 有限一阶网络的条件风险分解 | 最大绝对差1.11×10⁻¹⁶ |
| 实际一阶／二阶训练损失，对比复数MSE表达 | 最大绝对差8.53×10⁻¹⁴ |
| 总迹不变、天线子迹改变 | 损失差0；子迹变化+5.6与−5.6 |
| 实复因子及非平凡checkpoint尺度换算 | 最大绝对差2.48×10⁻¹⁶ |
| Gaussian site相除后重新相乘 | 最大绝对差3.33×10⁻¹⁶ |
| Gaussian活动证据及混合矩，对比独立实坐标求积 | 最大绝对差1.14×10⁻¹⁶ |
| 正site精度不是一般后验性质 | v=1、后验方差4、相除精度−0.75 |
| Cai式(59)逐样本反例及期望方差公式 | 估计功率3、真实功率1；展开误差0 |
| 逐用户缩放与共同噪声标签 | 0.5、0.125与共同0.2不相同 |
| Gaussian参数阻尼与混合矩匹配差异 | 参数协方差0.5；混合协方差1.9656 |
| 相位前端增益消元及完整物理时延／Doppler梯度 | 与独立最小二乘一致；中心差分最终相对差6.18×10⁻¹⁰ |

详见 [MATH_CHECKS.json](MATH_CHECKS.json) 和 [可复跑检查](check_math.py)。
首次检查记录 [math_check_initial.log](math_check_initial.log) 保留：
当时手选功率例子的非零余项为−0.06，不满足检查脚本要求其绝对值大于0.1的展示条件；
随后改用H=W=1的明确反例，没有放宽代数核验容差。
相位梯度补充检查首次在差分步长10⁻⁵时，相对差1.61×10⁻⁶，未达到2×10⁻⁷的最终容差；
减小步长后误差按中心差分的二阶趋势下降，步长10⁻⁷时为6.18×10⁻¹⁰。
最终检查同时要求差分误差随步长下降及细步长误差通过原阈值，未修改解析梯度或放宽最终容差。
首次记录与全部步长诊断分别保留于 [phase_check_initial.log](phase_check_initial.log)、
[phase_gradient_diagnostics.json](phase_gradient_diagnostics.json)。最终15组全部通过，见 [math_check.log](math_check.log)。

另执行已有的 Cai 推导审计、活动分类器、未知相位接口三组测试，32项通过。
其中包括有限先验 Tweedie 自动微分核对、同点矩不足以识别证据、BCE 最优概率及先验校正、
总迹损失的零空间、部分正交退化、裁剪后的外信息、AFDM 标量观测展开和输入信息边界等。
测试产生21条已有数值警告，均来自 AFDM continuous.py 第28行矩阵乘法的除零、溢出或无效值提示，
涉及7个测试用例；断言通过，警告全文保留于 [tests.log](tests.log)。本次未定位或修复警告根因，不能把“测试通过”写成“无数值警告”。

本次没有改动算法源代码、配置或网络权重。身份及最终复核见 [VERIFICATION.json](VERIFICATION.json)。
没有新增训练、Monte Carlo性能比较、完整循环收敛证明或状态演化证明；这些不由确定性代数检查替代。

## 对“同一级别”的最终判断

1. **核心概率计算与线性代数：同一层级。** 一般矩阵LMMSE、Gaussian外信息、条件分解、Tweedie读出和混合矩均有明确推导；当前没有发现必须靠错误公式才能运行的步骤。
2. **学习型活动证据：有独立的严格目标推导。** 理想BCE分类器给出密度比，先验校正由Bayes公式直接得到。它的有限估计误差需验证，但不能因用了第三个网络就判断推导降级。
3. **近似程度：并不逐项相同。** 当前共享更多方差信息，另有相位点估计、site接受／复用、裁剪、阻尼和停止规则；这些应作为方法定义公开写出。Cai也使用Gaussian投影、伪AWGN、有限网络、方差平均、阻尼和功率估计，必须采用对称标准。
4. **原文也有需要澄清之处。** 式(19)的中心、式(53)对式(56)子迹的识别、式(59)的样本等式及式(60)–(61)的尺度配对，不能仅因出现在已发表论文中就免于核查。这些局部问题不等于否定整篇论文。
5. **能据此写出的结论有边界。** 可以说当前方法是有完整公式依据的近似Bayesian消息传递算法；不能据此声称与Cai算法等价、有限网络精确、物理全后验精确、全局收敛或性能一定相同。论文新颖性和实验竞争力也不由“推导同级”直接推出。
