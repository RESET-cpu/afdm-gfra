# 协方差条件三个学习模块与完整主迭代

日期：2026-10-12。状态：新网络和独立接收机已实现并通过局部数学及接入检查，一阶正式训练已启动，三模块训练与闭环验证尚未完成。它不替代当前已部署算法的 `docs/THEORY.md`。

本次修改同时涉及查询噪声模型、三个模块的训练目标和迭代消息。基本次序仍为线性观测更新、非线性条件估计、活动混合、Gaussian 投影、外信息反馈。天线协方差方向来自本项目已完成的受控消融；文献提供匹配训练和消息设计的依据。详细学习目标证明见 [THEORY.md](THEORY.md)，执行次序见 [REPAIR_PLAN.md](REPAIR_PLAN.md)。

## 1. 系统模型与保留的统计量

沿用当前物理模型和归一化：信道及观测除以固定尺度 \(s=0.2647966452702405\)，协方差及噪声方差除以 \(s^2\)。以下均为归一化坐标。

\[
 y=\mathcal A x+w,\qquad w\sim\mathcal{CN}(0,\sigma_w^2I),\qquad X_k=a_kH_k,
 \quad a_k\in\{0,1\}. \tag{A1}
\]

每个 \(H_k\in\mathbb C^{M\times L}\)，\(L=NP\)，\(D=ML\)。当前 \(K=40\)，\(M=N=P=16\)。活动工作先验为独立 Bernoulli(\(\rho\))，活跃信道先验为训练物理边缘 \(P_H\)。物理活动联合分布的非空约束、信道与算子/噪声设置的依赖仍按当前工作后验近似处理。

把每列的 M 个天线坐标连续排列。每轮保留的协方差是完整 Hermitian \(M\times M\) 矩阵，在用户和 L 列之间共享；没有构造或学习完整 \(D\times D\) 矩阵。\(H\) 的列可以相关，后验也可以相关；被约束为列独立的是所选 Gaussian 消息族。

网络使用同一个条件观测模型：

\[
 R_k=X_k+C^{1/2}Z_k,\qquad (Z_k)_{m\ell}\overset{\mathrm{iid}}\sim\mathcal{CN}(0,1),
 \quad C=C^H\succ0. \tag{A2}
\]

即向量噪声协方差为 \(I_L\otimes C\)。它替代旧的 \(vI_D\)。C 描述有效查询误差，不等同于接收端热噪声 \(\sigma_w^2I\)。实际迭代中零均值、Gaussian、与信号条件独立，以及省略的跨列相关仍是近似。

## 2. 线性观测模块

设上一轮反馈给线性模块的均值为 \(m_k^t\)，共同协方差为 \(V_t\succ0\)，定义

\[
 q_t(x)\propto\prod_{k,\ell}\mathcal{CN}(x_{k\ell};m_{k\ell}^t,V_t),
 \qquad \mathcal V_t=I_{KL}\otimes V_t.
\]

将其与观测似然相乘，Gaussian conditioning 给出

\[
 \mathcal T_t=(\mathcal V_t^{-1}+\sigma_w^{-2}\mathcal A^H\mathcal A)^{-1},\qquad
 \mu_t=\mathcal T_t(\mathcal V_t^{-1}m_t+\sigma_w^{-2}\mathcal A^Hy). \tag{A3}
\]

投影到共同天线协方差族，保持均值，取

\[
 \bar T_t=\frac1{KL}\sum_{k,\ell}[\mathcal T_t]_{k\ell,k\ell}. \tag{A4}
\]

这里取的是 M×M 对角块的平均，**没有再取矩阵的迹**。投影后的 Gaussian 除以输入 Gaussian，得到送给三个学习模块的同一组查询：

\[
 C_t=(\bar T_t^{-1}-V_t^{-1})^{-1},\qquad
 R_k^t=C_t(\bar T_t^{-1}\mu_k^t-V_t^{-1}m_k^t). \tag{A5}
\]

相乘、投影和相除是所选消息族内明确的运算，但不保证真实 \(R-X\) 满足 A2。令
\(W_t=\mathcal V_t\mathcal A^H(\sigma_w^2I+\mathcal A\mathcal V_t\mathcal A^H)^{-1}\)，
\(\bar{\mathcal T}_t=I_{KL}\otimes\bar T_t\)，\(\mathcal C_t=I_{KL}\otimes C_t\)，
\(G_t=\mathcal C_t\bar{\mathcal T}_t^{-1}W_t\)，则有精确代数式

\[
 R_t-x=(G_t\mathcal A-I)(x-m_t)+G_tw. \tag{A6}
\]

这说明其他用户均值误差、方向性残余干扰和历史依赖如何进入下一轮查询。保留 C 主要修复方向性二阶统计，不能仅凭 A5 断言 A6 中的偏差和相关性已消失。

### 可计算形式

实现存储 \(A_0\in\mathbb C^{Q\times KP}\)，完整算子与 \(I_{MN}\otimes A_0\) 只差排列。设 \(V_t=U\operatorname{diag}(\gamma_j)U^H\)，\(A_0\) 非零奇异值为 \(d_i\)，秩为 r，\(J_0=KP\)，则

\[
 t_j=\frac1{J_0}\left\{\sum_{i=1}^r(\gamma_j^{-1}+d_i^2/\sigma_w^2)^{-1}
 +(J_0-r)\gamma_j\right\},\quad
 \bar T_t=U\operatorname{diag}(t_j)U^H. \tag{A7}
\]

非零观测算子下 \(0<t_j<\gamma_j\)，所以 A5 的 C 正定。现有 `SpatialLinear` 已实现这种运算，可复用。无需形成 A3 的巨大矩阵。

## 3. 局部密度、均值与 score

在 A2 内定义活跃和不活跃似然：

\[
 q_1(R\mid C)=\int\prod_\ell\mathcal{CN}(R_{:\ell};H_{:\ell},C)P_H(dH),\qquad
 q_0(R\mid C)=\frac{\exp[-\operatorname{tr}(C^{-1}RR^H)]}{\pi^{ML}\det(C)^L}. \tag{A8}
\]

\(P_H\) 可以没有全维密度；正定 Gaussian 卷积仍有光滑正密度。用每列的实、虚部构成实向量 u，噪声协方差为

\[
 \Sigma_C=\tfrac12 I_L\otimes\begin{pmatrix}\Re C&-\Im C\\\Im C&\Re C\end{pmatrix}.
\]

对给定 C 的 Gaussian 条件模型，一般协方差 Tweedie 公式为

\[
 m_{\mathbb R}=u+\Sigma_C\nabla_u\log q_1(u\mid C),\qquad
 \operatorname{Cov}(H_{\mathbb R}\mid u,C,a=1)
 =\Sigma_C+\Sigma_C\nabla_u^2\log q_1(u\mid C)\Sigma_C. \tag{A9}
\]

若把实梯度打包为 \(s=s_{\Re}+is_{\Im}\)，第一式等价于

\[
 m(R,C)=R+\tfrac12 Cs(R,C). \tag{A10}
\]

因子 1/2 来自复噪声实、虚部各承担一半方差；不能与 Wirtinger 梯度的约定混用。一般公式来源为 [Dytso–Poor–Shamai，式(3)、(22)–(23)](https://arxiv.org/pdf/2104.01883)；本处复数排列和部分协方差投影为直接推导。

## 4. 第一个模块：协方差条件均值及一阶 score

新网络直接以 R 和完整 C 为条件，用以下可逆参数化表示均值：

\[
 A_C=(I+C)^{-1/2},\quad K_C=(I+C)^{-1},\quad
 B_C=[C(I+C)^{-1}]^{1/2},
\]
\[
 F_\theta(R,C)=K_CR+B_Cu_\theta(A_CR,C),\qquad
 \mathcal L_1=\mathbb E\frac{\|B_C^{-1}(F_\theta-H)\|_F^2}{D}. \tag{A11}
\]

这是 [Karras 等 EDM §5、式(7)–(8)、Table 1](https://proceedings.neurips.cc/paper_files/paper/2022/file/a98846e9d9cc01cfb87eb694d946ce6b-Paper-Conference.pdf) 的标量输入/输出预条件思想在本项目中的矩阵推广。I 是归一化单位复功率的参考尺度，不把真实物理先验假定为独立 Gaussian；A_CR 也不被声称为物理信道严格白化。

给定 \((R,C)\) 时，\(B_C^{-2}=I+C^{-1}\) 正定且与 H 无关。条件平方误差分解证明函数空间最优解为 \(F^*=\mathbb E[H\mid R,C,a=1]\)。对应的 score 读出为

\[
 s_\theta=2C^{-1}(F_\theta-R). \tag{A12}
\]

因此直接预测均值没有丢掉一阶 score 的统计对象。A11 与加权 DSM 有相同的上述总体最优解，但它不是旧 AWGN 损失的原样复用。其有限容量解和训练权重会不同。网络权重全部新建，不载入旧 checkpoint；输入 C 的实、虚部形状与总尺度。

## 5. 第二个模块：完整天线条件误差二阶矩

训练好第一模块后冻结 F。对同一个 \((H,R,C)\) 定义

\[
 E=C^{-1/2}(F-H),\qquad T=EE^H/L.
\]

第二网络输出复下三角矩阵 \(L_\psi\)，并取

\[
 S_\psi=L_\psi L_\psi^H,\quad
 \mathcal L_2=\mathbb E\frac{\|S_\psi(R,C,F)-T\|_F^2}{M},\quad
 B_\psi=C^{1/2}S_\psi C^{1/2}. \tag{A13}
\]

逐样本先形成矩阵目标与损失，再对 batch 平均。PSD 参数化保留任意天线方向的误差矩，不限制为 \(aC\)，也不要求 \(S_\psi<I\)。后者不是一般先验下的点态理论性质。

由条件最小二乘，理想二阶回归得到

\[
 B_F(R,C)=\mathbb E[(H-F)(H-F)^H/L\mid R,C,a=1]
 =B_*+(F-m)(F-m)^H/L, \tag{A14}
\]

其中 \(B_*=L^{-1}\sum_\ell\operatorname{Cov}(H_{:\ell}\mid R,C,a=1)\)。这沿用 Cai 有限一阶输出代入二阶损失的逻辑，将标量条件 MSE 推广为矩阵；不是需要额外消除或审批的障碍。理想 F=m 时，A14 是 A9 后验协方差的天线对角块平均。

以有限 F 为固定 Gaussian 中心时，期望负对数密度中依赖 B 的项为
\(L\{\log\det B+\operatorname{tr}(B^{-1}B_F)\}\)，其正定最优解正是 \(B_F\)。因此 A14 给出固定均值下有明确拟合意义的 Gaussian 协方差；它不被称为精确物理后验协方差。[Cai §IV 式(51)–(54)](https://arxiv.org/html/2506.00581v2#S4) 给出原二阶训练结构；矩阵回归、PSD 输出及有限 F 分解为这里的推广。

## 6. 第三个模块：协方差条件活动证据

训练正负类各半：

\[
 a=1:\ R=H+C^{1/2}Z;\qquad a=0:\ R=C^{1/2}Z.
\]

两类使用相同 C 分布；第一模块固定。分类器 \(z_\phi(R,C,F)\) 最小化普通 balanced BCE。函数空间最优 logit 为

\[
 z^*(R,C)=\log\frac{q_1(R\mid C)}{q_0(R\mid C)}.
\]

部署加入公开先验一次：

\[
 p_k=\operatorname{sigmoid}\!\left(z_\phi(R_k,C,F_k)+\log\frac\rho{1-\rho}\right). \tag{A15}
\]

若训练活动比例不是 1/2，要再减去训练先验 logit。保留 R、C 后，F 是确定性特征，不改变理想密度比。C 在实际迭代中依赖观测，所以训练中的 a、H 与 C 独立依然是工作模型条件。密度比与分类损失的依据见 [Menon–Ong §3、§4.2](https://proceedings.mlr.press/v48/menon16.pdf)。

## 7. 活动混合、共同矩与反馈

采用由三个模块共同确定的近似局部后验

\[
 \widetilde q_k=(1-p_k)\delta_0+p_k\prod_\ell\mathcal{CN}(X_{:\ell};F_{k,:\ell},B_{\psi,k}).
\]

它的均值和天线对角块平均协方差为

\[
 \widehat X_k=p_kF_k,\qquad
 V_{X,k}=p_kB_{\psi,k}+p_k(1-p_k)F_kF_k^H/L. \tag{A16}
\]

第二项来自活动不确定性，必须参与反馈。对所有用户作共同 Gaussian 投影：

\[
 \bar V_X=\frac1K\sum_kV_{X,k}. \tag{A17}
\]

A16 是所选近似后验的精确矩；有限 F、有限 p 下不是实际联合估计器的精确条件 MSE。这个近似与 A14 的有限 first 含义在详细推导中分别列明。

此处直接使用分类器证据，无需先为每个活跃信道构造可归一化 Gaussian site，因而不再以逐用户 \(B_{\psi,k}<C\) 为接受当前均值/活动证据的条件。共同反馈才做一次 Gaussian 相除：

\[
 \Lambda_{\rm raw}=\bar V_X^{-1}-C_t^{-1},\qquad
 J_{{\rm raw},k}=\bar V_X^{-1}\widehat X_k-C_t^{-1}R_k^t. \tag{A18}
\]

若精度正定，输出协方差为 \(\Lambda_{\rm raw}^{-1}\)，输出均值为 \(\Lambda_{\rm raw}^{-1}J_{{\rm raw},k}\)。矩阵乘法不能交换；不能复制旧的标量方差比例公式。

## 8. 阻尼的定义及正定性

设旧消息精度 \(\Lambda_t=V_t^{-1}\)、精度加权均值 \(J_{t,k}=\Lambda_tm_k^t\)。只在反馈端使用同一新值权重 δ：

\[
 \Lambda_{t+1}=(1-\delta_t)\Lambda_t+\delta_t\Lambda_{\rm raw},\qquad
 J_{t+1,k}=(1-\delta_t)J_{t,k}+\delta_tJ_{{\rm raw},k}, \tag{A19}
\]
\[
 V_{t+1}=\Lambda_{t+1}^{-1},\qquad m_k^{t+1}=V_{t+1}J_{t+1,k}.
\]

这对应 Gaussian 形式因子的加权乘积。若候选精度不正定，降低 δ 使更新后的精度正定。令
\(d_{\min}=\lambda_{\min}(\Lambda_t^{-1/2}\Lambda_{\rm raw}\Lambda_t^{-1/2})\)，则该次更新正定当且仅当

\[
 1-\delta_t+\delta_td_{\min}>0. \tag{A20}
\]

实际实现以 δ 上限开始二分回退，要求上式不小于预先记录的相对数值余量，例如 \(10^{-6}\)。旧精度正定使足够小的正步长可行，但这不证明收敛；长期极小步长必须记为停滞。记录原始矩、原始精度、实际 δ 及回退比例，不把数值调整描述为后验恒等式。

每轮 \((R_t,C_t)\) 直接采用 A5，取消独立的跨轮查询均值/协方差算术混合。若混合真实查询误差，正确协方差含跨轮交叉项，不能仅靠相同权重混合旧、新 C 得到；A19 避免再赋予这种混合错误的已知噪声解释。它同样没有使实际跨轮误差自动独立。

## 9. 初始化、停止与完整循环

将接收观测整理为 \(Y_{\rm sp}\in\mathbb C^{M\times QN}\)，令

\[
 S_y=Y_{\rm sp}Y_{\rm sp}^H/(QN),\quad
 \alpha_A=\|A_0\|_F^2/Q,\qquad
 V_0=\operatorname{PDfloor}\!\left(\frac{S_y-\sigma_w^2I}{\alpha_A}\right),\quad m_0=0. \tag{A21}
\]

PDfloor 对 Hermitian 特征值设置相对下限；建议初值下限为正特征值均值的 \(10^{-6}\)，绝对下限 \(10^{-12}\)，实际处理和触发率均记录。A21 仅用公开观测、算子及噪声，是共同输入独立近似下的二阶矩估计，不是当前物理模型的点态无偏定理。它给出 V0；网络噪声 C0 仍需经线性模块 A5 产生。此初始化已有四个开发条件首轮的协方差匹配证据，后续闭环尚未验证。

一次迭代依次执行：

1. 由 \((m_t,V_t)\)、观测和算子，用 A3–A7 得到 \((R_t,C_t)\)。
2. 每用户运行 Fθ、Sψ、zφ，得到 \(F_k,B_{\psi,k},p_k\)。
3. 用 A16–A17 形成 \(\widehat X,\bar V_X\)。
4. 用 A18 求候选外信息，用 A19–A20 更新反馈消息。
5. 记录联合估计、活动概率、协方差、未阻尼固定点残差和实际步长，再判断停止。

停止除估计、协方差和活动概率稳定外，还检查**未阻尼**反馈候选与旧消息的相对差异，避免 δ 很小时把小更新误认为收敛。沿用现有最少 60、最多 600 轮作为首轮配对比较预算，判决向量连续 10 轮稳定；估计/协方差、活动概率和未阻尼参数差异的初始容差分别采用当前量级 \(3\times10^{-3},10^{-4},10^{-2}\)，连续 5 轮。具体范数、零附近尺度与规则在实现配置中冻结。预算耗尽单列报告。

输出联合信道估计 \(\widehat X\) 和 \(\widehat a_k=1[p_k\ge0.5]\)，按 s 恢复物理单位。主结果来自这个循环自身。

## 10. 理论成立范围与验证重点

Gaussian conditioning、矩阵相除、Tweedie 恒等式、条件回归最优解和所选混合分布的矩均有明确推导。实际有限 AFDM 查询是否接近 A2、有限网络的误差、共同天线矩能否概括每个用户及其跨列相关、以及闭环是否收敛，仍需实验。

已有消融支持天线协方差失配是早期网络严重失准的重要来源；末态真实查询比同协方差 Gaussian 控制更差，说明尚有信号相关偏差。此次重训旨在先修复已定位的统计失配，再通过主迭代检验方向偏差是否随其他用户估计改善而减小。

文献关系： [Zilberstein 等 §3.2–3.3、App C.1](https://arxiv.org/html/2605.15487v1#S3) 提供协方差条件 score 训练的先例；[D-GEC §III-B 式(39)–(41)](https://arxiv.org/pdf/2206.05049v2) 提供有色误差统计与匹配去噪器的消息传递先例。它们实际验证的协方差族与本项目不同，不能据此宣称本算法已被验证；这些基本思想也不单独构成新颖性。
