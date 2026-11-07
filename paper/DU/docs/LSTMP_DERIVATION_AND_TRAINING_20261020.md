# AFDM 联合活动检测与信道估计的消息推导及训练目标

本研究方案保留 Wei 的训练框架：先在 AWGN 条件下预训练一阶 score，再用独立参数实例初始化各展开层，在实际观测模型中逐层增加深度并联合微调。每层的联合活动与信道估计公式从 Cai 的因子分解和混合矩出发，推广到本项目的一般 AFDM 算子。冻结 score 用于隔离因素的对照，不作为默认训练流程。

关键改变是估计对象从单用户信道 \(H\) 变为有效信道 \(X_k=a_kH_k\)。活动概率、活跃条件信道均值和有效信道方差需要配套；这些统计关系不要求三个独立网络。残差方差仍可作为展开网络的反馈参数，但不能自动解释为严格后验方差。

原算法已有推导见 [THEORY](THEORY.md) 和论文第 III 至 IV 章。这里补全新五层算法与这些推导之间的关系，作为独立研究方案，不替换 `MAINLINE.json`、旧算法或当前五层训练副本。本文的严格等式分别限定于工作后验、局部 Gaussian 模型或明确的条件风险；有限 AFDM 迭代的准确性和收敛不由这些等式自动得到。

## 1 观测模型与工作后验

使用项目现有排列，将观测写为

\[
Y=AX+N,\quad
A\in\mathbb C^{Q\times KN},\quad
X\in\mathbb C^{KN\times MN},\quad
N_{ij}\sim\mathcal{CN}(0,\sigma_n^2).
\tag{D1}
\]

这里 \(M\) 为天线数，\(N\) 为帧内维数；每用户完整信道有 \(D=MN^2\) 个复系数。
矩阵中的用户块由
\(X_k=a_kH_k,\ a_k\in\{0,1\}\) 重排得到，
\(A_{q,kN+n}=P_{qkn}e^{jq\beta_k}\)。
具体索引与信道生成见 [SYSTEM_MODEL](SYSTEM_MODEL.md) 和论文式 `effective-pilot`、`mmv-indexing`。

给定 \(A,\sigma_n^2,\rho\)，计算采用

\[
dq(X,H,a\mid Y)\propto
\exp\!\left(-\frac{\|Y-AX\|_F^2}{\sigma_n^2}\right)
\prod_{k=1}^K
\left[
\delta_{a_kH_k}(dX_k)\,
P_H(dH_k)\,
\rho^{a_k}(1-\rho)^{1-a_k}
\right].
\tag{D2}
\]

\(P_H\) 是训练信道的边缘先验，可以集中在低秩集合上，不要求存在全维密度。
式 D2 沿用 Cai §II-B 式(5)的因子分解，但采用本项目的一般 AFDM 算子。

必须区分 D2 与完整物理条件后验。当前生成器以至少一用户活跃为条件，活动变量因此相关；准确相位算子和信道还共享几何变量，公开噪声方差由接收信号功率设置。D2 使用独立 Bernoulli 边缘及无条件训练先验，是明确的工作模型。未知相位时用估计的 \(\widehat A,\widehat\sigma_n^2\) 代入，还多一层点估计近似。当前五层诊断采用已知相位和噪声，不能把其失败归于相位估计。

## 2 线性 Gaussian 更新与消息相除

对每个测量向量，设输入消息为
\(\mathcal{CN}(x;m_A,wI)\)，其中 \(w>0\)，令 \(J=KN\)。
完成平方可得

\[
\begin{aligned}
C_A&=(w^{-1}I+\sigma_n^{-2}A^HA)^{-1},\\
M_A&=M_{\rm pri}
+wA^H(\sigma_n^2I+wAA^H)^{-1}(Y-AM_{\rm pri}),\\
t_A&=\frac{\operatorname{tr}C_A}{J}.
\end{aligned}
\tag{D3}
\]

这里 \(\sigma_n^{-2}=1/\sigma_n^2\)。D3 对指定 Gaussian 输入和一般 \(A\) 精确成立，不需要 \(AA^H=I\)。
用 \(t_AI\) 替代 \(C_A\) 才开始丢弃相关性。这个标量是固定均值下最小化
\(J\log t+\operatorname{tr}C_A/t\) 的结果，即各向同性 Gaussian 矩匹配。
Gaussian 投影和因子除法的来源是 Minka §2、§3，而非新定义的方法。

把投影后的 Gaussian 除以输入消息：

\[
v_B=(t_A^{-1}-w^{-1})^{-1},\qquad
R=v_B(M_A/t_A-M_{\rm pri}/w).
\tag{D4}
\]

当 \(A\ne0,\sigma_n^2>0\) 时，\(C_A\) 的特征值属于 \((0,w]\)，至少一个小于 \(w\)，所以 \(0<t_A<w\)，式 D4 有正方差。
令 \(f=t_A/w\)、\(\Delta=M_A-M_{\rm pri}\)，等价形式是

\[
v_B=w\frac{f}{1-f},\qquad
R=M_{\rm pri}+\frac{\Delta}{1-f}.
\tag{D5}
\]

令
\(L=wA^H(\sigma_n^2I+wAA^H)^{-1}/(1-f)\)，
实际查询误差满足

\[
R-X=(LA-I)(X-M_{\rm pri})+LN.
\tag{D6}
\]

因此，正确计算 LMMSE 与外信息，不等于查询误差已经独立、各向同性或 Gaussian。
若使用 \(\widehat A\)，D6 还包含 \(L(A-\widehat A)X\)。
有限 AFDM 迭代中将这些误差压缩为一个方差，是另一个模型近似。

## 3 局部联合后验决定三个统计量

非线性模块把每用户输入近似为

\[
r=ah+\varepsilon,\qquad
\varepsilon\sim\mathcal{CN}(0,vI_D),\qquad
h\sim P_H,\quad a\sim{\rm Bernoulli}(\rho).
\tag{D7}
\]

在这一局部模型内定义

\[
q_0(r;v)=\mathcal{CN}(r;0,vI),\qquad
q_1(r;v)=\int\mathcal{CN}(r;h,vI)P_H(dh).
\tag{D8}
\]

Bayes 公式直接给出

\[
\begin{aligned}
p^\star(r,v)&=
\frac{\rho q_1(r;v)}{(1-\rho)q_0(r;v)+\rho q_1(r;v)},\\
\mu^\star(r,v)&=E[h\mid r,v,a=1],\\
C_H^\star(r,v)&=\operatorname{Cov}(h\mid r,v,a=1).
\end{aligned}
\tag{D9}
\]

令 \(x=ah\)。全期望与全协方差公式给出

\[
\begin{aligned}
\widehat x^\star&=p^\star\mu^\star,\\
C_X^\star&=p^\star C_H^\star+
p^\star(1-p^\star)\mu^\star\mu^{\star H},\\
\tau_X^\star&=p^\star\tau_H^\star+
p^\star(1-p^\star)\frac{\|\mu^\star\|^2}{D},
\qquad \tau_H^\star=\frac{\operatorname{tr}C_H^\star}{D}.
\end{aligned}
\tag{D10}
\]

证明只需要
\(E[xx^H\mid r]=p^\star(C_H^\star+\mu^\star\mu^{\star H})\)，
再减去 \(E[x\mid r]E[x\mid r]^H\)。
与 Cai §III-B3 式(35)–(38)的混合矩相对应。

这说明每层可以先算条件信道均值，再算软活动概率，并联合反馈；不要求等信道“完全去噪”后才做活动检测。
但执行顺序并不决定反向传播路径，不能由 D10 推出“分类损失必须更新 score”或“绝不能更新 score”。

活动计算需要的是
\(\ell=\log q_1-\log q_0\)，而非仅有单次查询的均值和方差。
Cai §III-B2 式(26)–(30)用 Gaussian 外信息近似计算活动证据；它不是任意先验下由局部矩恢复精确 \(q_1\) 的恒等式。
分类器则可以直接近似 \(p^\star\) 或 \(\ell\)，但实际查询的分布是否匹配仍需核对。

## 4 score 与活动概率的必要一致性

将 \(r,h\) 转成 \(2D\) 维实向量 \(u,h_R\)，令 \(c=v/2\)，以下导数均固定 \(v,\rho\)。
对 Gaussian 卷积求导：

\[
\nabla_u\log q_1(u;v)
=\frac{E[h_R\mid u,v,a=1]-u}{c}.
\tag{D11}
\]

故一阶 score 的理想均值为

\[
\mu_R^\star=u+c\,s_1^\star(u,v).
\tag{D12}
\]

对条件均值的归一化积分再求导，分母导数消去非中心矩，得到

\[
J_{\mu^\star}=\frac{C_{H,R}^\star}{c},\qquad
C_{H,R}^\star=cI+c^2\nabla_u^2\log q_1.
\tag{D13}
\]

这对应 Cai §IV-A 的 Tweedie 关系和 Dytso–Poor–Shamai 的条件均值导数恒等式。由于复总平方误差等于实部、虚部平方误差之和，

\[
\tau_H^\star=
\frac{\operatorname{tr}C_{H,R}^\star}{D}
=\frac{v}{2D}\operatorname{tr}J_{\mu^\star}
=v+\frac{v^2}{4D}\operatorname{tr}\nabla_u^2\log q_1.
\tag{D14}
\]

因此二阶 score 网络只是获得方差的一种实现方式。精确均值的 Jacobian 也包含相同信息，但自动微分需要计算，而且有限网络的均值误差小并不保证导数误差小。

活动证据与均值也并非任意组合。因为
\(\nabla_u\log q_0=-u/c\)，

\[
\nabla_u\ell=\frac{\mu_R^\star}{c},\qquad
\nabla_u p^\star=
\frac{p^\star(1-p^\star)}{c}\mu_R^\star.
\tag{D15}
\]

对 \(p^\star\mu_R^\star\) 用乘积求导，得到

\[
cJ_{p^\star\mu^\star}
=p^\star C_{H,R}^\star+
p^\star(1-p^\star)\mu_R^\star\mu_R^{\star T}
=C_{X,R}^\star.
\tag{D16}
\]

固定 \(v\) 的偏导很重要：不能对整条迭代中 \(v(Y)\) 的依赖一并求导，然后仍将结果称为 D13 的后验协方差。

D15–D16 可以检查理想局部模型的一致性，不能仅凭分类准确率或去噪 MSE 宣称有限网络满足它们。相关历史推导及有限网络失败记录已经存在，见 [概率与条件矩](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_probability_consistency_20261016/DERIVATION.md)，不把导数方案当作尚未尝试过或已证明有效的新修复。

### 4.1 从单用户 score 更新到联合活动与信道更新

固定局部 Gaussian 查询的 \(v,\rho\)，有效信道的含噪密度为
\(q_X(u;v)=(1-\rho)q_0(u;v)+\rho q_1(u;v)\)。
对混合密度直接求导，得到

\[
\begin{aligned}
s_X^\star(u,v)
&=\nabla_u\log q_X(u;v)\\
&=p^\star s_1^\star(u,v)
 -(1-p^\star)\frac{u}{c},\qquad c=v/2,\\
u+c\,s_X^\star
&=p^\star\bigl(u+c\,s_1^\star\bigr)
=p^\star\mu_R^\star.
\end{aligned}
\tag{G1}
\]

G1 是由 D8–D12 直接得到的关系，与 Cai 式(35)的有效信道均值一致。它说明先验预训练仍可以只学习活跃信道的 \(s_1^\star\)，活动概率负责把这个条件去噪器组合为有效信道去噪器；不必为了引入未知活动重新训练一个包含零点质量的先验网络。选择直接学习混合先验也是另一种参数化，但不是当前方案。

据此，将 Wei 式(11)推广为本项目每层的学习更新：

\[
\begin{aligned}
\widetilde\mu_{k,R}^{(\ell)}
 &=u_k^{(\ell)}
   +\alpha_\ell\frac{v_\ell}{2}
      s_{\theta_\ell}(u_k^{(\ell)},v_\ell),\\
p_k^{(\ell)}
 &=g_{\psi_\ell}
   (u_k^{(\ell)},v_\ell,
      \widetilde\mu_{k,R}^{(\ell)},\rho),\\
\widehat x_{k,R}^{(\ell)}
 &=p_k^{(\ell)}\widetilde\mu_{k,R}^{(\ell)}.
\end{aligned}
\tag{G2}
\]

其中 \(g_{\psi_\ell}\) 输出活动概率，理想目标是 D9；用分类器计算它是本项目的近似选择，Cai 原文式(30)采用 Gaussian 外信息计算活动概率。每层的 \(\theta_\ell\) 独立存储和优化；同一层可以跨用户复用网络。D10 给出相应理论方差，§7 给出保留 Wei 残差反馈时的计算及其含义。

校准参数的位置也需要声明。若先形成 G1 的混合 score，再把 Wei 的 \(\alpha\) 直接乘在整个 score 修正上，则

\[
u+\alpha c s_X^\star
=p^\star(u+\alpha c s_1^\star)
 +(1-\alpha)(1-p^\star)u.
\tag{G3}
\]

它与 G2 并不相同；活动概率趋零时，额外项仍可能保留输入噪声。G2 选择先校准活跃条件去噪，再由活动概率组合有效信道。这是保持活动混合结构的学习参数化；只有在局部模型成立、网络精确、\(\alpha=1\) 时，才能把它直接解释为 D10 的 Bayes 条件均值。

当活动先验 \(\rho=1\) 时，\(p^\star=1\)；在 G2 中相应将活动概率固定为 1，更新退化为信道去噪。再取 \(K=1\)、\(AA^H=I\) 并采用 Wei 的校准与残差定义，线性更新、外信息、G2 和 D22 恢复其模块形式。这里的退化比较统一了实、复 score 的因子约定，不把本项目当前不同的 \(\gamma\) 参数化说成与 Wei 完全相同。

## 5 后验方差与有限估计器条件误差

固定一个有限均值估计器 \(\widetilde\mu(z)\)。这里 \(z\) 可以是 Gaussian 查询，也可以是部署时实际可用的查询特征。令
\(m(z)=E[h\mid z,a=1]\)，则

\[
\frac1D E[\|h-\widetilde\mu(z)\|^2\mid z,a=1]
=\frac1D\operatorname{tr}\operatorname{Cov}(h\mid z,a=1)
+\frac1D\|\widetilde\mu(z)-m(z)\|^2.
\tag{D17}
\]

证明是关于 \(m(z)\) 展开平方，交叉项的条件期望为零。
旧二阶网络在冻结有限一阶网络时，其迹训练目标对应左侧的条件误差，而非必然为右侧第一项的中心方差；已有证明见论文附录和 THEORY T9–T11。

这个区别会影响活动混合公式。若把左侧记为 \(r_H\)，直接计算
\(p r_H+p(1-p)\|\widetilde\mu\|^2/D\)，它可以定义一个近似 Gaussian 混合分布的方差，却一般不等于真实联合后验方差，也不等于实际估计器 \(p\widetilde\mu\) 的条件误差。

例如在某个固定查询处，取一个复系数，真实
\(p=0.3,m=2,\tau_H=0.5\)，有限均值 \(\widetilde\mu=1\)。
此时 \(r_H=1.5\)，上述代入给出 \(0.66\)，而

\[
E[|ah-p\widetilde\mu|^2\mid z]
=p\tau_H+p(1-p)|m|^2+|p\widetilde\mu-pm|^2
=1.08.
\tag{D18}
\]

这不是实际 AFDM 测量结果，而是一个解析反例。它说明新增“方差网络”之前必须先说明训练的是中心方差、条件误差还是反馈参数。三者不能只因都叫 variance 就互换。

若目标是校准现有有效信道估计的误差，可以直接拟合
\(E[\|X-\widehat X\|_F^2/(KD)\mid z]\)，不必先构造一个条件信道误差，再机械地追加活动项。
若目标是使用 D10 的精确矩解释，则均值、活动概率与中心方差需要对应同一个条件分布。

## 6 非线性反馈与正精度条件

若每用户得到局部后验矩，保持当前共同标量消息结构时，应先形成 D10，再投影：

\[
\bar\tau_X=\frac1K\sum_k\tau_{X,k},\qquad
q_B(X)\approx\mathcal{CN}(X;\widehat X,\bar\tau_XI).
\tag{D19}
\]

这里平均迹对应整个 \(KD\) 维有效信道误差；不是先平均活动概率、再替代各用户的 D10。
与入射 \(\mathcal{CN}(X;R,vI)\) 相除得到

\[
\lambda_{\rm ext}=\bar\tau_X^{-1}-v^{-1},\qquad
\eta_{\rm ext}=\widehat X/\bar\tau_X-R/v.
\tag{D20}
\]

当 \(\lambda_{\rm ext}>0\) 时，
\(w_{\rm ext}=1/\lambda_{\rm ext}\)、\(M_{\rm ext}=\eta_{\rm ext}/\lambda_{\rm ext}\)。
精确非 Gaussian 后验在某些查询处可以有 \(\bar\tau_X>v\)，所以“后验方差必须小于查询方差”不是一般定理。
当前上限是在限制消息的可积性，而非验证一个必然成立的统计性质。

自然参数阻尼具有明确的代数解释：

\[
\lambda_{\rm next}=(1-\delta)\lambda_{\rm old}+\delta\lambda_{\rm ext},\qquad
\eta_{\rm next}=(1-\delta)\eta_{\rm old}+\delta\eta_{\rm ext}.
\tag{D21}
\]

若两端精度为正，\(0\leq\delta\leq1\) 保持正性。若提议精度非正，在
\(\lambda_{\rm old}>\epsilon>0\) 时限制
\(\delta\leq(\lambda_{\rm old}-\epsilon)/(\lambda_{\rm old}-\lambda_{\rm ext})\)
可保持 \(\lambda_{\rm next}\geq\epsilon\)。
这是有定义的 Gaussian 更新条件，不是收敛或性能保证，也不意味着当前方差依赖的阻尼权重由 D2 唯一导出。

## 7 当前五层算法与推导之间的差别

Wei §III-C 式(12)使用

\[
d_\ell=
\frac{\|Y-A\widehat X_\ell\|_F^2-Q(MN)\sigma_n^2}
{(MN)\|A\|_F^2},\qquad
\tau_\ell=\beta_\ell d_\ell.
\tag{D22}
\]

这里将原文的单用户 \(BH\) 换成 AFDM 的 \(AX\)，只是在同一残差表达式中代入本项目变量。
当前实现另外先做温度 \(0.02v\) 的 softplus 正值化，限制 \(\tau/v<0.95\)，再进行自然参数阻尼。
这些映射是学习算法的参数化，不是由 D10 或 D19 推出的后验方差公式。

令 \(E=X-\widehat X\)。逐样本展开为

\[
\|Y-A\widehat X\|_F^2-Q(MN)\sigma_n^2
=\|AE\|_F^2+
(\|N\|_F^2-Q(MN)\sigma_n^2)
+2\operatorname{Re}\langle AE,N\rangle_F.
\tag{D23}
\]

只有在适当的误差各向同性和交叉项均值为零等条件下，归一化期望才等于信道平均误差。估计器依赖 \(Y\)，这些条件不会自动满足。
即便 \(x\sim\mathcal{CN}(0,s)\)、\(y=x+n\) 且使用精确 MMSE
\(\widehat x=sy/(s+\sigma_n^2)\)，也有

\[
E[|y-\widehat x|^2]-\sigma_n^2
=-\frac{s\sigma_n^2}{s+\sigma_n^2}<0,\qquad
E[|x-\widehat x|^2]=\frac{s\sigma_n^2}{s+\sigma_n^2}>0.
\tag{D24}
\]

因此 D22 是经验反馈量；它可能通过端到端训练有效，但不能因名字含“方差”就作为精确后验矩。
相反，D24 也不证明经验反馈会导致高 AER，更不证明需要一个额外网络。

另一个差别在 D5 的校准。当前实现为
\(v=w\gamma f/(1-f)\)；
Wei §III-B 式(8)–(10)先将 \(t_A\) 乘 \(\gamma\)，从而得到
\(v=w\gamma f/(1-\gamma f)\)，并要求 \(\gamma f<1\)。
两者是不同参数化。当前使用
\(\mu=u+\alpha(v/2)s_\theta(u,v)\) 时，若 \(\alpha\ne1\)，也不再自动等于 D12 对给定 \(q_1,v\) 的条件均值。

由此需要保留两个层次的解释：

| 解释 | 数学要求 | 能声称的结果 |
|---|---|---|
| 局部后验矩近似 | 各输出近似 D9，反馈按 D19–D20 构造 | 模块内的后验与矩关系有明确来源，真实查询仍可能失配 |
| 有限层学习算法 | 校准、残差及阻尼作为迭代参数，用任务风险学习 | 可以评价最终 AER 和 NMSE，不能未经验证给所有内部量赋予精确后验含义 |

Cai 主要提供前一种统计结构，Wei 提供有限层学习的方法。把两者组合时应逐项标明替换，不能同时默认拥有精确先验 score、精确后验方差和任意端到端微调的全部解释。

## 8 从条件风险推导训练目标

令 \(z\) 表示模块实际可用的信息，包括查询、方差标签及需要的公开配置。定义
\(\pi(z)=P(a=1\mid z)\)、
\(m(z)=E[h\mid z,a=1]\)。
以下最优目标相对于 \(z\) 而言，不等于保证已利用完整 \(Y\) 的全部信息。

### 8.1 活动概率

对二元交叉熵，

\[
\mathcal R_{\rm act}(p\mid z)
=-\pi\log p-(1-\pi)\log(1-p).
\]

其导数为 \((p-\pi)/(p(1-p))\)，故最优解为 \(p=\pi\)，并且

\[
\mathcal R_{\rm act}(p\mid z)-\mathcal R_{\rm act}(\pi\mid z)
=D_{\rm KL}({\rm Bern}(\pi)\|{\rm Bern}(p)).
\tag{D25}
\]

在等代价的活动错误下，相对于同一条件信息的 Bayes 判决为 \(p\geq1/2\)。
这一结论不要求去噪网络参与 BCE 反向传播。

若用相同方差抽样律生成两类 Gaussian 查询，训练活动先验为 \(\pi_{\rm tr}\)，最优 logit 是
\(\logit\pi_{\rm tr}+\log(q_1/q_0)\)。
在类别条件输入律保持不变时，减去训练先验 log odds、加入目标 \(\logit\rho\) 才得到目标后验。
这与 Menon–Ong §3、§4.2 对类别概率与密度比的关系一致。
实际消息会随用户数、活动率和迭代参数变化，不能无条件套用同一先验修正，代替实际消息上的适配。

### 8.2 条件信道均值

条件均值的合适目标为

\[
\mathcal L_\mu=
E\!\left[a\,\frac{\|h-\mu(z)\|^2}{D\,s_H^2}\right],
\tag{D26}
\]

其中 \(s_H^2>0\) 是固定训练统计量。
在 \(P(a=1\mid z)>0\) 处，对 \(h\mid z,a=1\) 展开平方，函数空间最优解就是 \(m(z)\)。
非活跃样本不应以 \(h=0\) 监督“假设活跃条件下的信道均值”；其有效信道 \(x=0\) 是另一个目标。

对理想 Gaussian 查询，也可以用

\[
\mathcal L_{\rm DSM}
=E\left[\frac1{2D}
\|\sqrt{v/2}\,s_\theta(u,v)+\epsilon\|^2\right],
\quad u=h_R+\sqrt{v/2}\epsilon.
\tag{D27}
\]

固定 \(u,v\) 后，最优解为
\(-E[\epsilon\mid u,v]/\sqrt{v/2}=\nabla_u\log q_1\)，即 Cai §IV-B 的 DSM 目标。
若改用真实消息上的 D26，所得函数是该消息分布下的条件均值；将其写成残差形式并不会自动使内部网络仍等于 Gaussian 平滑先验的 score。

### 8.3 每样本 NMSE 的目标不同

当前重建损失含
\(\|\widehat X-X\|^2/\max(\|X\|^2,\epsilon)\)。
一般地，若真值相关权重为 \(w(X)>0\)，则

\[
\arg\min_f E[w(X)\|X-f(z)\|^2\mid z]
=\frac{E[w(X)X\mid z]}{E[w(X)\mid z]}.
\tag{D28}
\]

它一般不等于 \(E[X\mid z]\)。
例如固定查询处 \(X=1,2\) 各占一半，普通平方误差最优估计为 \(1.5\)，每样本相对平方误差的最优估计为 \(1.2\)。

这不表示 NMSE 不能作为任务训练目标。若研究目标就是相对误差，它是合法选择；但不能同时未经证明把该训练后的均值称为 MMSE 条件均值并直接套用 D13。
采用训练库固定功率归一化，能在控制数值尺度的同时保留条件均值目标。NMSE 仍作为评价指标报告。

### 8.4 方差或误差校准

若固定均值估计器，令
\(e=\|h-\widetilde\mu(z)\|^2/D\)，对正函数 \(t(z)\) 最小化

\[
E[\log t(z)+e/t(z)\mid z,a=1]
\]

得到 \(t(z)=E[e\mid z,a=1]\)，即 D17 的条件误差。若均值恰为条件均值，才等于中心方差。

对现有残差方案，可以保持网络数量不变，固定估计器和用于生成查询的参数，令
\[
e_X=\frac{\|X-\widehat X\|_F^2}{KD},\qquad
\mathcal L_{\rm cal}=E[\log\tau_\phi(z)+e_X/\tau_\phi(z)].
\tag{D29}
\]

\(\tau_\phi\) 可以仍是现有残差与少量标量参数的函数，并不必须是神经网络。
函数不受限时最优目标为 \(E[e_X\mid z]\)；受限的残差参数化只能近似这个目标。
如对 \(\tau_\phi\) 设置上限，它拟合的是受约束的误差尺度。
训练时的真值只用于标签；推断输入不能包含实际误差。

D29 用于检验和校准现有误差尺度，不证明“真实误差尺度”一定是有限层算法最佳反馈参数。
若随后仅按最终任务损失继续优化它，输出应重新解释为学习的反馈参数，或保留校准项并明确权衡。

### 8.5 联合训练的数学含义

对一个以 Gaussian 近似活跃条件分布的输出族，可以考虑

\[
\mathcal L_{\rm fit}
=E\left[
{\rm BCE}(a,p(z))
+a\left(D\log t(z)+\frac{\|h-\mu(z)\|^2}{t(z)}\right)
\right].
\tag{D30}
\]

这是 Bernoulli 负对数概率与活跃条件 Gaussian 负对数密度的组合。
直接对条件期望求极值：在输出函数可独立选择、二阶矩有限且最优方差为正时，
\(p=\pi,\mu=m,t=\operatorname{tr}\operatorname{Cov}(h\mid z,a=1)/D\)。
即便真实信道先验奇异，这个期望拟合目标的矩计算仍成立；不将其无条件写成对奇异真实分布的有限 Gaussian KL。

因此联合训练并非在数学上天然不合理。问题在于有限共享网络、输入相互依赖、有限优化以及目标尺度，使各项未必同时达到理想最优解。
原样采用 D30 时 \(D\) 个复信道坐标与一个活动标签的损失尺度也不同，严谨的概率形式不等于已经满足工程上的 AER 优先级。

另一方面，若坚持 \(s_\theta\) 是 D27 的先验 score，随意加入 BCE 或任务 NMSE 更新同一参数，优化目标就已经改变。
冻结、分阶段训练或 DSM 约束是保持或检验该含义的设计选择，并非 D9 的因子分解强制禁止联合训练。

## 9 保留 Wei 训练框架的联合估计方案

本节 D31 保留为早期相对重建损失基线。[第二版训练协议](LSTMP_TRAINING_PROTOCOL_20261020_V2.md)采用 D26 对应的固定训练能量归一化条件信道监督及活动 BCE；其 T6–T7 说明两个目标如何在固定查询下导出有效信道条件均值，直接有效信道监督另作对照。下一轮训练阶段、梯度范围和统一选模规则以第二版为准，不把本节旧基线与新配方混为同一实验。

初始化、数据清单、逐场景损失权重、轮次上限及选模规则见[具体训练方案](LSTMP_TRAINING_PROTOCOL_20261020.md)。该协议是待落实到独立训练入口的研究配方，不代表已经运行。

Wei §III-D 明确采用逐层增加深度、新层与之前各层共同训练、预训练 score 与校准参数联合微调；§V-A 明确每层有独立 score 网络。这里保留这套流程，改变的是每层估计对象、活动概率与有效信道矩，以及相应任务损失。网络跨层共享、始终冻结 score 或增加二阶网络均不是主方案的前提。

| 阶段 | 学习对象与输入 | 目标及来源 |
|---|---|---|
| AWGN 信道先验预训练 | 活跃信道样本及独立 Gaussian 噪声；一阶 score | D27；Cai §IV-B 的 DSM 与 Wei §III-D 的先验预训练 |
| 展开层初始化 | 每层建立独立参数的 score，载入同一预训练权重；初始化活动头和校准参数 | Wei §V-A 的独立网络；同初始化不等于共享权重 |
| 逐层接收机微调 | 增加第 \(\ell\) 层后，联合优化第 1 至 \(\ell\) 层的 score、活动头及消息参数 | Wei §III-D 的训练方式，任务损失推广为 D31 |
| 固定深度的验证与选模 | 独立验证场景、预先声明的条件和用户权重 | 同时评价有效信道重建、活动错误及计算成本 |

接收机微调在每次前向传播中使用当前参数生成实际查询，活动头读取同层的查询和条件信道估计。AWGN 活动训练可以作为初始化；不能把只在旧查询上训练一次的分类器视为已经适配整个展开过程。已有合格的信道先验权重可以直接使用，不要求重训先验库。

一个明确的有限层任务目标是

\[
\mathcal J_{\rm task}
=\sum_{\ell=1}^{L}\omega_\ell
\left[
\frac1B\sum_{i=1}^{B}
 \frac{\|X_i-\widehat X_i^{(\ell)}\|_F^2}
 {\max(\|X_i\|_F^2,\epsilon)}
+\lambda_a
 \frac{\sum_{i,k}{\rm BCE}(a_{ik},p_{ik}^{(\ell)})}
 {\sum_iK_i}
\right],
\quad \omega_\ell\ge0,\quad \lambda_a\ge0.
\tag{D31}
\]

\(B\) 是场景数，\(\epsilon>0\) 固定。第一项沿用 Wei 的相对重建误差，但监督对象改为 \(X=aH\)；第二项监督新增的活动变量。此处 BCE 按总用户数归一化，与 pooled AER 的样本权重一致；若采用每场景平均用户 BCE 或各条件等权，应明确它是另一种权重。当前代码采用的逐场景损失不能未经修改就宣称已实现 D31 的全局用户权重。

按 D31 对所有展开参数正常反向传播，是可检验的联合微调基线。一阶网络在此阶段允许成为任务适配的去噪映射，保留预训练初始化、网络结构及 G2 的更新形式；不要求它在任务训练后仍精确等于原始 AWGN 先验的 score。NMSE 与严格 MMSE 的区别见 D28，这个区别不否定 Wei 式任务训练。

Wei 没有活动分类器，所以其论文不能证明新增 BCE 应当或不应当直接更新 score。阻断 BCE 到 score 参数的路径可作为配对消融，同时仍允许重建损失微调 score；若声称阻断，就须覆盖跨层路径。冻结 score、固定查询训练活动头、D29 残差误差校准，以及固定尺度平方误差，均用于区分机制，不替代上述默认展开训练。

\(\omega_\ell,\lambda_a\)、训练轮次和深度由资源与任务权衡决定，不由 Bayes 公式给出唯一值。可用 Wei 的末层权重 1、之前各层 0.2 作参照，但 GFRA 的活动权重和选模规则需要独立验证。最终输出为 \((p_L,\widehat X_L)\) 时，末层之后未使用的反馈方差没有 D31 的任务梯度。

训练与选模同时报告 AER、MD、FA 和 NMSE。若 AER 是主要目标，可预先限定允许的重建误差范围，再在范围内按验证 AER 选模；阈值和条件权重在独立测试前固定。固定尺度 MSE 可作为统计解释的辅助指标，不能用降低混合损失代替证明活动检测改善。

## 10 数学核验与研究决策

本轮确定性合成核验包括一般复矩阵的 Gaussian 条件均值、含零空间的协方差迹、Gaussian 相除再合并、离散先验 Gaussian 卷积的 Tweedie 关系、活动 log odds 导数、活动混合矩、复方差的二倍因子、负残差反例、条件误差与中心方差反例，以及相对平方误差的最优目标。

22 项核验全部通过，其中新增 G1 混合密度 score 的差分核对，以及 G3 在不同活动概率和校准系数下的核对。结果见 [MATH_CHECKS](../../../result/lstmp_derivation_20261020/MATH_CHECKS.json)，可复现程序见 [check_lstmp_derivation_20261020.py](../../../src/history/scripts/check_lstmp_derivation_20261020.py)。代数比较使用双精度，差分导数使用显式步长及 \(2\times10^{-8}\) 或 \(2\times10^{-6}\) 的容差。它们验证公式和数值因子，不构成实际接收机的 AER、收敛或网络必要性证据。

已有五层困难场景统计见 [残差与 Wei 对照](../../../result/lstmp_five_layer_diagnosis_20261020/RESIDUAL_WEI_REVIEW.json)。下一步控制实验应先固定深度与网络容量，分别比较统计目标、消息参数化和训练梯度路径。只有在这些控制下，现有残差函数仍无法表达有用的反馈尺度，且增加方差分支带来可重复的检测与重建收益，才支持增加该分支。反过来，单次换入真值构造的误差或旧二阶权重也不足以判定方差方案，因为它会改变已训练网络的输入分布。

## 文献与公式定位

| 来源 | 对应内容 |
|---|---|
| [Cai 等 2026](https://arxiv.org/html/2506.00581v2)，§II-B、§III-B2–3、§IV-A–C | 联合活动与信道模型；Gaussian 活动证据近似；式(35)–(38)混合矩；Tweedie 与一阶、二阶 DSM |
| [Wei 与 Yuan 2026](https://arxiv.org/html/2610.17785v1)，§III-B 式(8)–(10)、§III-C 式(11)–(12)、§III-D | 校准与外信息；学习均值和残差方差；逐层联合训练及中间输出监督 |
| [Minka 2001](https://tminka.github.io/papers/ep/minka-ep-uai.pdf)，§2 式(5)–(6)、§3 式(8)–(10) | Gaussian 矩匹配和因子除法 |
| [Dytso 等作者稿](https://arxiv.org/pdf/2104.01883)，§IV Proposition 1 式(22) | Gaussian 噪声下条件均值导数与条件协方差；本文采用输出行、输入列的 Jacobian |
| [Menon 与 Ong 2016](https://proceedings.mlr.press/v48/menon16.pdf)，§3 式(6)–(8)、§4.2 式(16)–(17) | 类别概率、logistic 损失和密度比关系 |

D17–D18、D23–D26、D28–D31 的具体排列、条件风险说明及训练阶段是本项目基于上述概率模型的直接推导或研究设计，不作为某篇论文已验证的 AFDM 算法。专业术语和对应记录见 [TERMINOLOGY](TERMINOLOGY.md)。
