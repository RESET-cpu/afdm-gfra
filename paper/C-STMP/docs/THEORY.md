# 完整信道 score 与消息传递

本文件定义当前 proposed：完整信道 score 消息传递与活动分类器。归一化 Gaussian site 的解析密度比用于查询超出支持范围时的回退。公式编号仅用于项目定位。推断实现见 `src/afdm_jadcedd/algorithm/proposed/`，配置见 [proposed.json](../../../src/configs/proposed.json)。

## 1. 系统模型与工作后验

实际物理生成、已知跨帧相位和接收 SNR 的含义见 [SYSTEM_MODEL.md](SYSTEM_MODEL.md)。四项公开输入为 \((Y,A,\sigma^2,\rho)\)。以固定 \(s=0.2647966452702405\) 将信道、观测及噪声方差分别除以 \(s,s,s^2\)；以下使用归一化坐标。

启用 [未知相位配置](../../STMP/docs/PROPOSED_UNKNOWN_PHASE.md) 时，公开输入为 \((Y,P,\sigma^2,\rho)\)，先从观测估计跨帧相位斜率并构造 \(\widehat A\)，再将 \(\widehat A\) 代入以下条件接收机。该两阶段计算以完整信道 NMSE 和 AER 评价。

\[
 y=Ax+n,\quad n\sim\mathcal{CN}(0,\sigma^2 I),\quad
 x_k=a_k\operatorname{vec}H_k,\quad a_k\in\{0,1\}. \tag{T1}
\]
每用户 \(H_k\in\mathbb C^{M\times NP}\)，\(M=N=P=16\)，\(D=MNP=4096\)。活跃信道边缘先验 \(P_H\) 由共同物理训练集给出，允许支撑于低秩集合。计算后验为
\[
 dq\propto\mathcal{CN}(y;Ax,\sigma^2I)
 \prod_k\{\delta_{a_kH_k}(dx_k)P_H(dH_k)\rho^{a_k}(1-\rho)^{1-a_k}\}. \tag{T2}
\]
物理条件先验 \(\Pi(H,a\mid A,\sigma^2)\) 一般不能直接替换成上述独立边缘先验：算子由几何/Doppler生成，噪声方差由接收信号功率设置。当前生成还以至少一用户活跃为条件；若原活动抽样概率为p，则公开ρ=p/[1-(1-p)^K]，活动联合分布不再独立。T2使用该边缘ρ的独立近似，是明确的工作模型，未施加全局非空活动约束。

T1–T5 的 \(A\) 是作用于完整向量 \(x\) 的算子。实现只存储 \(A_0\in\mathbb C^{Q\times KP}\)，把观测整理为 \(Q\times MN\)、未知量整理为 \(KP\times MN\)。完整算子与 \(I_{MN}\otimes A_0\) 仅相差按用户组织坐标的固定置换；所以完整协方差的平均迹除以 \(KD\)，等于单个测量向量协方差的平均迹除以 \(KP\)。当前 \(P=N\) 时的排列和物理路径到观测的推导见[论文草稿式(1)–(19)](../../history/phase4_sections_20261008/draft.md)。

## 2. 线性模块与 pseudo AWGN 观测模型

设 \(0<\rho<1\)、\(\gamma>0\)、\(\sigma^2>0\)，且 \(A\ne0\)。Gaussian 输入 \(\mathcal{CN}(x;x_p,\gamma I)\) 下，
\[
 C_L=(\gamma^{-1}I+\sigma^{-2}A^HA)^{-1},\quad
 m_L=C_L(\gamma^{-1}x_p+\sigma^{-2}A^Hy),\quad
 t_L=\operatorname{tr}C_L/(KD). \tag{T3}
\]
先把 \(C_L\) 投影为 \(t_LI\)，保留均值，再与输入 Gaussian 相除。由 \(C_L\) 的特征值可知 \(0<t_L<\gamma\)，因此以下外信息方差正且有限：
\[
 v=(t_L^{-1}-\gamma^{-1})^{-1},\qquad
 r=v(m_L/t_L-x_p/\gamma). \tag{T4}
\]
令 \(\kappa=1-t_L/\gamma\in(0,1)\)、\(L=\gamma A^H(\sigma^2I+\gamma AA^H)^{-1}/\kappa\)，未阻尼线性查询满足
\[
 r-x=(LA-I)(x-x_p)+Ln. \tag{T5}
\]
T3–T5 是 Gaussian conditioning 和矩阵代数恒等式。它们不推出实际误差独立、白化或 Gaussian。学习模块采用工作模型
\[
 R=H+W\ (a=1),\qquad R=W\ (a=0),\qquad
 W\sim\mathcal{CN}(0,vI_D). \tag{T6}
\]
训练时独立采样 \(v\) 并构造 AWGN；实际有限 AFDM 迭代中的 T6 是近似。Cai 对此提出大系统和算子条件，并采用阻尼；不能将该条件自动移植到当前算子。[Cai v2 §III-A、§V-B1](https://arxiv.org/html/2506.00581v2)

在 T6 的局部工作模型内，活动和完整信道属于同一个后验：
\[
 dq_v(a,H\mid R)=
 \frac{\rho^a(1-\rho)^{1-a}\mathcal{CN}(R;aH,vI_D)P_H(dH)}
 {(1-\rho)q_{0,v}(R)+\rho q_{1,v}(R)},\quad
 q_{0,v}(R)=\mathcal{CN}(R;0,vI_D),\quad
 q_{1,v}(R)=\int\mathcal{CN}(R;H,vI_D)P_H(dH).
 \tag{T6a}
\]
令 \(X=aH\)、\(m=E[H\mid R,v,a=1]\)、\(\Sigma_H=\operatorname{Cov}(\operatorname{vec}H\mid R,v,a=1)\)，则
\[
 p^*=\frac{\rho q_{1,v}}{(1-\rho)q_{0,v}+\rho q_{1,v}},\quad
 E[X\mid R,v]=p^*m,\quad
 \operatorname{Cov}(\operatorname{vec}X\mid R,v)
 =p^*\Sigma_H+p^*(1-p^*)(\operatorname{vec}m)(\operatorname{vec}m)^H.
 \tag{T6b}
\]
这两式连接局部信道去噪、活动证据和联合矩，对 T6 精确成立；后文用有限网络、共同方差和 Gaussian 分布近似这些量。它们不把 T6 升格为实际迭代误差的精确分布。

## 3. 一阶均值、二阶平均迹及有限网络目标

令 \(u=(\Re R,\Im R)\)、\(\nu=v/2\)、
\(q_v(r)=\int\mathcal{CN}(r;h,vI)P_H(dh)\)。
Gaussian 卷积具有全维密度，即使原先验集中于低秩集合。对卷积核求导，在所需矩及求导交换条件下，
\[
 m_R=u+\nu\nabla_u\log q_v,\qquad
 C_R=\nu I_{2D}+\nu^2\nabla_u^2\log q_v,\qquad
 \tau_C=\operatorname{tr}C_R/D. \tag{T7}
\]
这里 \(m=E[H\mid R,v,a=1]\)。实部与虚部的噪声方差均为 \(v/2\)，复平方误差的平均应除以 \(D\)。

冻结一阶网络后，当前均值和二阶读数为
\[
 F_0=R+\tfrac v2(S_{1,\Re}+iS_{1,\Im}),\qquad
 \widehat a_0=1+\tfrac v2\,\mathcal A(S_2),\qquad
 \widehat\tau_0=v\widehat a_0, \tag{T8}
\]
其中 \(\mathcal A\) 是全部 \(2D\) 实坐标的普通平均。当前接收机与 checkpoint 的坐标尺度相同。一般尺度比 \(c\) 下，应在 \(cR,c^2v\) 查询并将均值与方差分别除以 \(c,c^2\)。

令 \(\varepsilon=(u-H_R)/\sqrt\nu\)、\(b=\sqrt\nu S_1+\varepsilon\)，训练损失实际为
\[
 \mathcal L_1=E\,\mathcal A(b^2),\quad
 \mathcal L_2=E\{\mathcal A(\nu S_2-b^2+1)\}^2
            =E\left(\widehat a_0-\frac{\|F_0-H\|_F^2}{Dv}\right)^2. \tag{T9}
\]
二阶损失在完整样本平均之后平方，训练时冻结一阶网络。由条件平方误差分解，
\[
 \tau_0(R,v)=D^{-1}E[\|F_0-H\|_F^2\mid R,v,a=1]
 =\tau_C+D^{-1}\|F_0-m\|_F^2. \tag{T10}
\]
因此二阶函数空间最优读数对应有限 \(F_0\) 的条件 MSE。只有理想一阶均值时，它才等于中心协方差平均迹；有限网络不能逐坐标认证 Hessian。T9 的条件回归分解为
\[
 \mathcal L_2
 =E(\widehat a_0-\tau_0/v)^2
  +E\operatorname{Var}(\|F_0-H\|_F^2/(Dv)\mid R,v,a=1). \tag{T11}
\]
T10–T11 由平方误差的交叉项条件期望为零得到，给出了真实训练目标的含义。学习公式的对应位置见 [Cai v2 §IV，式(43)–(54)](https://arxiv.org/html/2506.00581v2#S4)。

## 4. 共享方差与活跃 Gaussian site

当前实现对所有用户原始读数普通平均，再下限处理：
\[
 \bar\tau_{\rm raw}=K^{-1}\sum_k\widehat\tau_{0,k},\qquad
 \tau=\max(\bar\tau_{\rm raw},10^{-4}). \tag{T12}
\]
共享近似 Gaussian 的中心固定为各 \(F_{0,k}\)。其期望负对数密度关于共享方差的目标为
\(KD\log(\pi\tau)+D\sum_k\tau_{0,k}/\tau\)，正方差最优值为 \(K^{-1}\sum_k\tau_{0,k}\)。这解释了普通平均的受限拟合含义；原始读数误差、用户间差异和下限处理仍是近似。

只在支持范围内且 \(0<\tau<v\) 接受新活跃 site：
\[
 c_k=(\tau^{-1}-v^{-1})^{-1},\qquad
 e_k=c_k(F_{0,k}/\tau-R_k/v),\qquad
 t_k=c_kv/(c_k+v),\quad
 \mu_k=(c_kR_k+ve_k)/(c_k+v). \tag{T13}
\]
接受后，代回可得 \(t_k=\tau,\mu_k=F_{0,k}\)。若不满足正精度条件，则沿用之前 \(e_k,c_k\)，在当前 \(R,v\) 上计算 \(t_k,\mu_k\)。初始 site 为 \(e_k=0,c_k=1\)。\(v\) 超出 checkpoint 支持范围 \([10^{-3},100]\) 时，采用旧 site 的解析证据，并且不查询网络。

\(\tau<v\) 是当前接收机要求 site 可归一化的接受条件，不是一般先验下精确条件方差逐查询必然小于噪声方差的结论。条件方差超过 \(v\) 或有限网络不满足该条件，都由上述复用分支处理。

## 5. 两种活动证据

回退时对归一化 \(\mathcal{CN}(H;e_k,c_kI_D)\) site 计算
\[
 \ell_k^{G}=\frac{\|R_k\|^2}{v}
 -\frac{\|R_k-e_k\|^2}{c_k+v}
 -D\log(1+c_k/v),\qquad
 p_k^G=\operatorname{sigmoid}(\operatorname{logit}\rho+\ell_k^G). \tag{T14}
\]
这是 Gaussian 积分密度比。当前 site 被接受时可等价写成
\(\ell_k^G=\|R_k\|^2/v-\|R_k-F_{0,k}\|^2/(v-\tau)+D\log(1-\tau/v)\)。
归一化常数不可省略。[Cai v2 §III-B2，式(28)–(30)](https://arxiv.org/html/2506.00581v2#S3.SS2.SSS2)

支持范围内，分类器用当前完整 \(R,v,F_0(R,v)\) 输出 logit \(z_\phi\)。训练活动比例 \(\pi_{\rm tr}=1/2\)，两类共享噪声方差律；BCE 的函数空间最优解满足
\[
 z^*(R,v)=\operatorname{logit}\pi_{\rm tr}
   +\log\frac{q_v(R)}{\mathcal{CN}(R;0,vI_D)},\quad
 \ell_k^C=z_\phi(R_k,v,F_{0,k})-\operatorname{logit}\pi_{\rm tr},\quad
 p_k^C=\operatorname{sigmoid}(\operatorname{logit}\rho+\ell_k^C). \tag{T15}
\]
保留完整 \(R\) 时，确定性特征 \(F_0(R,v)\) 不改变查询信息；有限网络仍有估计误差。条件 BCE 的超额风险是 Bernoulli KL 的期望，故理想密度比结论不能直接当作实际 MP 校准保证。分类器估计密度比的依据见 [Menon–Ong 2016 §2.2、§3、§4.2，式(6)–(8)、(16)–(17)，页305–306](https://proceedings.mlr.press/v48/menon16.pdf)。

T14 对近似 Gaussian site 是精确代数，T15 对训练 pseudo AWGN 模型的理想分类器成立。两者均不可写成物理完整后验的精确证据。公开先验 \(\rho\) 只加入一次。支持范围内，即使当前 site 拒绝更新，分类器仍使用当前 \(R,v,F_0\)；超出支持范围时使用沿用 site 的 T14。

## 6. 联合矩、反馈和停止

选择活动概率 \(p_k\) 后，令 \(G_k=\mu_k\mu_k^H/(NP)\)，
\[
 \widehat X_k=p_k\mu_k,\qquad
 C_{X,k}=p_kt_kI_M+p_k(1-p_k)G_k,\qquad
 \bar t_X=(KM)^{-1}\sum_k\operatorname{tr}C_{X,k}. \tag{T16}
\]
它们是所选 Bernoulli-Gaussian 近似分布的均值与空间平均协方差。由全方差分解直接得到，不额外截断活动概率。共享反馈将
\[
 b=\operatorname{clip}(\bar t_X/v,10^{-6},1-10^{-6}),\qquad
 \gamma_{\rm out}=vb/(1-b),\qquad
 x_{\rm out}=(\widehat X-br)/(1-b). \tag{T17}
\]
T17 使用了稳定性裁剪，和未裁剪的精度相减须分别表述。[Cai v2 §III-B3，式(32)–(42)](https://arxiv.org/html/2506.00581v2#S3.SS2.SSS3)

初始化为 \(x_p=0,\gamma_0=\rho\times1.0004404181394917\)。输入查询和输出消息均以新值权重0.2递归做均值、方差的算术插值，首次直接采用新值。内部 site 更新权重为1。

上限600轮，至少60轮。估计与输入协方差的相对变化小于 \(3\times10^{-3}\)，最大活动概率变化小于 \(10^{-4}\)，连续5轮；接受新 site、精度/自然参数相对变化小于 \(10^{-2}\)，且 \(\max_k|p_k-w_k^{\rm old}|<10^{-4}\)，连续5轮。同时完整活动判决向量连续10轮相同（首轮计入窗口）才停止。历史活动质量按 \(w\leftarrow0.8w+0.2p\) 更新；它只参与停止检查。这些停止规则沿用已有100场景设置；原图阻尼为0.1，当前配置为0.2，版本区别见 CURRENT_STAGE。MAX_ITERATIONS 返回有效的有限预算输出，不能称为收敛。

## 7. 严谨性的适用范围

本主线的闭合链条为：工作后验 → 线性 Gaussian conditioning → pseudo AWGN 条件学习 → 有限均值对应的条件 MSE → Gaussian site → 所选活动证据 → 联合矩 → 共同反馈。T3–T5、T9–T11、T13–T17 的代数/条件回归关系可以逐步核验。

统计近似包括：独立边缘先验、实际查询 AWGN、有限训练误差、共同各向同性方差、Gaussian site、支持范围回退及反馈裁剪。当前没有完整有限 AFDM 迭代的全局收敛定理，也没有活动分类器在实际查询分布上的校准保证。相对 Cai 的结构接近和本项目数学一致性不能替代独立性能证据或新颖性判断。

确定性检验采用显式 synthetic 控制；它们不是实际接收机 AER 结果。已有六条件证据及独立确认状态见 [CURRENT_STAGE.md](CURRENT_STAGE.md)，后续证据比较见 [EXPERIMENT_PROTOCOL.md](EXPERIMENT_PROTOCOL.md)。

## 8. 条件矩和训练目标的证明

本节补全前述等式的连接步骤。假定所用期望有限；例如先验具有有限四阶矩、查询方差位于正的有限区间，且网络输出满足相应可积性，是训练风险及以下条件平方误差分解的充分条件。有限训练库满足先验矩条件。Gaussian 卷积在 \(v>0\) 时具有正的光滑密度，不要求 \(P_H\) 本身具有全维密度。

对实 Gaussian 卷积核求导，得
\[
 \nabla_u\log q_v^{\mathbb R}(u)=\frac{m_{\mathbb R}(u,v)-u}{\nu},
 \qquad
 \frac{\partial m_{\mathbb R}}{\partial u}=\frac{C_{\mathbb R}}{\nu}.
 \tag{A1}
\]
第二式由对归一化的条件期望求导得到：分子导数减去分母导数产生
\(E[H_{\mathbb R}H_{\mathbb R}^{\mathsf T}\mid u]-m_{\mathbb R}m_{\mathbb R}^{\mathsf T}\)。
再对第一式求导即得 T7。复总平方误差等于相应 \(2D\) 实坐标的平方误差，故 \(\operatorname{tr}C_{\mathbb R}/D\) 为所有 \(D\) 个复坐标的平均条件方差。

一阶损失在固定 \((u,v)\) 下关于 \(S_1\) 最小化，满足
\[
 S_1^*(u,v)=-\frac{E[\varepsilon\mid u,v,a=1]}{\sqrt\nu}
           =\frac{m_{\mathbb R}-u}{\nu}.
 \tag{A2}
\]
这给出 T8 的理想条件均值解释。对实际有限 \(S_1\)，
\(F_{0,\mathbb R}-H_{\mathbb R}=\sqrt\nu\,b\) 和 \(2D\nu=Dv\)，直接得到 T9 的第二个表达式。

令 \(U=\|F_0-H\|_F^2/(Dv)\)。固定一阶网络后，平方损失满足
\[
 E[(\widehat a_0-U)^2\mid R,v,a=1]
 =(\widehat a_0-E[U\mid R,v,a=1])^2
  +\operatorname{Var}(U\mid R,v,a=1).
 \tag{A3}
\]
因此函数空间最优 \(\widehat\tau_0=v\widehat a_0\) 是 T10 的条件 MSE。
将 \(F_0-H=(F_0-m)+(m-H)\) 展开，交叉项的条件期望为零，得到 T10–T11。
对 \(S_2\) 加上任意逐样本满足 \(\sum_i\Delta_i=0\) 的扰动，T9 完全不变；故该目标仅识别总迹，不能单独识别各坐标的 Hessian 对角元或每根天线的子迹。

共享方差拟合针对每个用户的“假定其活跃”条件分布，固定各中心 \(F_{0,k}\)，各用户等权。令 \(\bar\tau_0=K^{-1}\sum_k\tau_{0,k}\)，则
\[
 {\cal J}(\tau)=KD\log(\pi\tau)+\frac{KD\bar\tau_0}{\tau},
 \qquad
 {\cal J}'(\tau)=\frac{KD(\tau-\bar\tau_0)}{\tau^2}.
 \tag{A4}
\]
当 \(\bar\tau_0>0\) 时唯一正方差最优值为 \(\bar\tau_0\)；施加 \(\tau\ge\tau_{\min}>0\) 后最优值为
\(\max(\bar\tau_0,\tau_{\min})\)，也覆盖零风险情形。当前实现用网络读数替代真实条件风险再作这个运算。
这是期望负对数密度的受限拟合；真实先验可能奇异，不能无条件把它写成有限的 \(D_{\rm KL}(P\|G)\)。
它也不是以活动概率加权的另一个最优化问题。

## 9. 活动证据与联合矩的证明

设两类训练查询共用方差采样律 \(g(v)\)，训练类别先验为 \(\pi_{\rm tr}\in(0,1)\)。
固定 \(R,v\) 后，训练条件活动概率为
\[
 \eta_{\rm tr}
 =\frac{\pi_{\rm tr}q_{1,v}(R)}
 {(1-\pi_{\rm tr})q_{0,v}(R)+\pi_{\rm tr}q_{1,v}(R)}.
 \tag{A5}
\]
方差采样律在比值中抵消。点态 BCE 是
\(B(z)=\log(1+e^z)-\eta_{\rm tr}z\)，其导数为
\(\operatorname{sigmoid}(z)-\eta_{\rm tr}\)，二阶导数为
\(\operatorname{sigmoid}(z)(1-\operatorname{sigmoid}(z))>0\)。
因此唯一有限最优解是 T15。点态超额风险恰为
\(D_{\rm KL}(\operatorname{Bern}(\eta_{\rm tr})\|
\operatorname{Bern}(\operatorname{sigmoid}z))\)。
完整 \(R\) 连同 \(v\) 保留在分类器输入中，添加确定性的 \(F_0(R,v)\) 不改变其条件信息。
在两类条件查询律不变时，把训练先验赔率换成 \(\rho/(1-\rho)\) 即得到 T6b 的 \(p^*\)。
这些是训练工作模型的函数空间结论；有限容量、有限训练及实际消息查询失配仍需实验评价。

对于归一化 Gaussian site，卷积恒等式给出
\[
 \int \mathcal{CN}(R;H,vI_D)\mathcal{CN}(H;e,cI_D)\,dH
 =\mathcal{CN}(R;e,(v+c)I_D).
 \tag{A6}
\]
与不活动密度相除并取对数得到 T14，包括不可省略的 \(D\log(1+c/v)\) 项。
展开两个 Gaussian 的二次项，精度和自然参数相加／相减分别得到 T13 的乘积和除法。
这里的 site 参数可以依赖当前及历史查询；逐查询使用的归一化 Gaussian 不自动对应一个与查询无关的真实生成先验。

对于当前选择的 \(p_k,\mu_k,t_k\)，明确采用
\[
 \widetilde q_k(dX_k)
 =(1-p_k)\delta_0(dX_k)
 +p_k\mathcal{CN}(\operatorname{vec}X_k;\operatorname{vec}\mu_k,t_kI_D)\,dX_k.
 \tag{A7}
\]
此分布在 \(0\le p_k\le1,t_k>0\) 时归一化。其均值为 \(p_k\mu_k\)；
由全方差公式，完整协方差为
\(p_kt_kI_D+p_k(1-p_k)\operatorname{vec}\mu_k\operatorname{vec}\mu_k^H\)。
取各空间列的 \(M\times M\) 对角块并平均，即得 T16；再对用户及天线取平均迹得到 \(\bar t_X\)。
所以 T16 是所选近似分布的正确矩；这不要求有限分类器与有限 score 输出已经是同一固定先验的精确后验。

## 10. 单点条件矩不能唯一确定活动证据

以下为可精确枚举的合成数学例子，不是物理信道样本或性能实验。设 \(D=1,v=1,R=0\)，
\({\cal U}=\{1,-1,i,-i\}\)，比较两个先验
\[
 P_A=\frac14\sum_{u\in{\cal U}}\delta_{u/\sqrt2},\qquad
 P_B=\frac{1}{1+\mathrm e}\delta_0
     +\frac{\mathrm e}{4(1+\mathrm e)}\sum_{u\in{\cal U}}\delta_u.
 \tag{A8}
\]
用 \(\mathcal{CN}(0;h,1)/\mathcal{CN}(0;0,1)=e^{-|h|^2}\) 计算，A 的活跃条件后验仍在四点各取 \(1/4\)；
B 的后验在零点取 \(1/2\)，其余四点各取 \(1/8\)。
两者均满足 \(E[H\mid R,a=1]=0\)、\(E[|H|^2\mid R,a=1]=1/2\)、
\(E[H^2\mid R,a=1]=0\)，完整实协方差同为 \(I_2/4\)。
但真实活动密度比分别为
\[
 \frac{q_{1,A}(0)}{q_0(0)}=e^{-1/2}\approx0.6065306597,\qquad
 \frac{q_{1,B}(0)}{q_0(0)}=\frac{2}{1+\mathrm e}\approx0.5378828427.
 \tag{A9}
\]
相同条件均值和方差代入 T13 都得到 \(e=0,c=1\)，T14 的 Gaussian 证据比均为 \(1/2\)。
因此单个查询位置的条件一、二阶矩不足以唯一确定该处边缘密度值。
该例解释直接密度比估计与局部 Gaussian 矩近似的区别；它不证明某个训练后的分类器一定优于解析证据，也不否定整个 score 函数所含的信息。

## 11. 数值更新的闭合性及复杂度

当前初始化满足 \(\gamma_0>0,c_k=1\)。在有限网络输出下，T12 给出正方差，
T13 仅接受正 site 精度；拒绝或超范围时保留原正 site。
T16 的协方差半正定；T17 使用 \(b\in[\varepsilon,1-\varepsilon]\)，故
\(\gamma_{\rm out}=vb/(1-b)>0\)，均值和方差的分母非零。
权重 \(0<\eta\le1\) 的方差算术阻尼保持正性。结合 T3–T4 的条件，下一轮所需参数继续有定义。
这说明声明分支下 Gaussian 参数的代数可用性，不是浮点溢出排除或全局收敛证明；非有限数值由实现报告失败。

T17 实际把混合矩的方差替换为 \(bv\)，再将
\(\mathcal{CN}(x;\widehat X,bvI)\) 除以 \(\mathcal{CN}(x;r,vI)\)。
因此即使发生裁剪，它仍是对“调整后 Gaussian”的精确除法，而非未裁剪混合矩的原始除法。
两向阻尼均采用上一轮已阻尼参数，首轮直接采用新值。
这些操作不表示两个随机 Gaussian 噪声的相加，也不要求混合噪声方差等于方差参数的算术平均。

外层停止量明确为
\[
 \delta_X^{(i)}
 =\frac{\|\widehat X^{(i)}-\widehat X^{(i-1)}\|_F}
 {\max(\|\widehat X^{(i)}\|_F,\|\widehat X^{(i-1)}\|_F,10^{-12})},
 \quad
 \delta_p^{(i)}=\max_k|p_k^{(i)}-p_k^{(i-1)}|,
 \quad
 \delta_v^{(i)}=\frac{|v^{(i)}-v^{(i-1)}|}
 {\max(v^{(i)},v^{(i-1)})}.
 \tag{A10}
\]
同时检查已接受 site 的精度及自然参数变化：
\[
 \delta_{\lambda,k}
 =\frac{|\lambda_k-\lambda_k^{\rm old}|}{\max(\lambda_k,\lambda_k^{\rm old})},
 \qquad
 \delta_{J,k}
 =\frac{\|J_k-J_k^{\rm old}\|_F}{\max(1,\|J_k\|_F,\|J_k^{\rm old}\|_F)},
 \quad \lambda_k=c_k^{-1},\quad J_k=e_k/c_k .
 \tag{A11}
\]
外层均值与输入协方差相对变化小于 \(3\times10^{-3}\)，活动概率变化小于 \(10^{-4}\)；
接受新 site 且 \(\max_k\{\delta_{\lambda,k},\delta_{J,k}\}<10^{-2}\)，
\(\max_k|p_k-w_k^{\rm old}|<10^{-4}\)。两类检查分别连续成立5轮，完整活动判决向量连续10轮相同，且总轮数至少60时报告数值收敛。历史量按第6节更新。
达到600轮时返回最后的联合均值、条件均值、活动概率、0.5门限判决和迭代上限状态。
联合均值与条件均值均乘回 \(s\)，协方差乘回 \(s^2\)。

实现以 \(A_0\) 的薄 SVD 计算线性更新。令奇异值为 \(s_j\)，
\[
 f=\frac1{KP}\sum_j\frac{\gamma s_j^2}{\sigma^2+\gamma s_j^2},\quad
 t_L=\gamma(1-f),\quad v=t_L/f,\quad
 R=X_p+(X_L-X_p)/f .
 \tag{A12}
\]
当 \(A_0A_0^H=cI_Q\) 时，
\(t_L=\gamma-(Q/(KP))c\gamma^2/(\sigma^2+c\gamma)\)，
均值增益为 \(\gamma A_0^H/(\sigma^2+c\gamma)\)，退化为 Cai 部分正交情形的同一 LMMSE 代数。
当前有效矩阵无需满足这个特殊条件。

在当前 \(P=N,Q\le KN\) 下，一次 SVD 成本为 \(O(KNQ^2)\)。
包含实现中的空间矩和小矩阵分解，每轮支持范围内更新的成本可写为
\[
 O\!\left(QKMN^2+KM^2N^2+M^3+
 K(C_\theta+C_\psi+C_\phi)\right).
 \tag{A13}
\]
前三项分别覆盖测量矩阵乘法、空间变换／二阶矩以及 \(M\times M\) 分解；
后三个 \(C\) 为相应网络的单用户前向成本。超出支持范围时不查询这些网络。
超出支持范围时不进行网络前向。除网络参数与激活缓存外，主要存储为
\(O(QKN+KMN^2+KM^2)\)。当前实际网络固定 \(M=N=16\)，复杂度表达式不意味着权重支持任意维度。

与 Cai 逐项对照、公式到代码定位和本轮确定性核验见 [推导完整性审查](../../../archive/paper_layout_20261026/original_paper/docs/history/archive/workspace_organization_20261011/before/docs/CAI_DERIVATION_AUDIT.md)。

## 12. 等价整体相位下的接收机输出平均

2026-10-15 的实验实现见 [proposed_average.py](../../../src/afdm_jadcedd/algorithm/proposed_average.py)，
保留用于结果复核。当前主线继续采用原两阶段推断及原分类器。
当前物理增益及复 Gaussian 噪声具有整体旋转对称性；对任意单位模常数 \(g\)，
令 \(X_k=a_kH_k\)，则 \(Y=A(\beta)X+N\) 对应 \(gY=A(\beta)(gX)+gN\)。跨帧斜率 \(\beta\) 保持不变，
由接收功率定义的噪声方差也不变。相位前端的平方相关和消去复增益后的残差目标
同样在该旋转下不变。因此先从原观测估计一次 \(\widehat\beta\)，再复用同一
\(\widehat A\)，不需要真实相位。

取 \(G=\{1,i,-1,-i\}\)，每个分支分别在 \(gY\) 上完成原接收机的全部迭代。
设转回原坐标后的联合均值、活动概率、条件均值和空间协方差分别为
\(X_g=g^*\widehat X(gY)\)、\(p_g\)、\(\mu_g=g^*\widehat\mu(gY)\)、\(C_g\)。
沿用 T16 的空间平均记号 \(\mathcal G(V)=VV^H/(NP)\)，输出为
\[
 \bar p_k=\tfrac14\sum_g p_{g,k},\qquad
 \bar X_k=\tfrac14\sum_g X_{g,k},\qquad
 \bar\mu_k=\sum_g\frac{p_{g,k}}{\sum_h p_{h,k}}\mu_{g,k},
 \qquad
 \bar C_k=\tfrac14\sum_g\{C_{g,k}+\mathcal G(X_{g,k}-\bar X_k)\}.
 \tag{G1}
\]
当活动概率之和为零时，条件分支权重按约定取 \(1/4\)；该零概率条件下的
条件均值不影响联合输出。G1 满足 \(\bar X_k=\bar p_k\bar\mu_k\)，
是四个近似分布混合后的矩，并非原工作后验的精确矩。
活动判决仍为 \(\bar p_k\ge0.5\)。四条轨迹来自同一观测，概率相乘没有独立证据依据。
每条轨迹独立使用原停止条件；达到600轮的分支保留其有限预算输出并报告该状态。
合并结果不反馈到任何分支。

群平均的通用依据见 [Chen–Dobriban–Lee，§3.1 Lemma 3.2、Proposition 3.3、§4](https://papers.nips.cc/paper_files/paper/2020/file/f4573fc71c731d5c362f0d7860945b88-Paper.pdf)。
在上述联合分布旋转对称、相位估计映射满足
\(\widehat\beta(gY)=\widehat\beta(Y)\) 且估计器的平方风险有限时，平方损失凸性给出
\(E\|\bar X-X\|_F^2\le\frac14\sum_gE\|X_g-X\|_F^2=E\|\widehat X(Y)-X\|_F^2\)。
该期望结论不保证每个有限场景的 NMSE 改善；0.5门限的活动错误也不由此得到改善保证。
优化目标旋转不变本身不保证有限精度求解器和平局选择逐位不变；理论结论需上述映射前提。
本项目的四旋转选择、已有网络和有限迭代效果须以独立场景验证，不能由该引用代替实验。

## 13. 估计物理原子下的条件均值与协方差

2026-10-15 的实验实现为 [proposed_projected.py](../../../src/afdm_jadcedd/algorithm/proposed_projected.py)，
以下公式记录该候选的工作假设；当前主线继续采用原两阶段推断及原分类器。
相位前端同时给出观测估计的折叠时延和 Doppler，记为 \((\widehat d_k,\widehat f_k)\)，其中
\(f=\nu/\Delta f\)。用当前 wrapped-chirp AFDM 原子及其两个一阶导数构造
\[
 B_k=\operatorname{orth}\left[
 \operatorname{vec}\widetilde H(\widehat d_k,\widehat f_k),\;
 \operatorname{vec}\partial_d\widetilde H(\widehat d_k,\widehat f_k),\;
 \operatorname{vec}\partial_f\widetilde H(\widehat d_k,\widehat f_k)\right],
 \quad P_k=B_kB_k^H,\quad B_k^HB_k=I_3 . \tag{P1}
\]
一阶线性近似的出处为 Wei 等 §III-B 式(17)–(24)；具体 AFDM 导数见
[OFFGRID_BASELINES](OFFGRID_BASELINES.md)。P1 是局部近似，不把固定 Doppler 的连续时延信道
假设为整数循环移位空间。导数仅在当前 wrapped-delay 分支内部成立；跨分支、多径展开和
Doppler 别名都可能产生投影误差。每个用户的基在相位估计后固定，构造不读取真值或活动集合。

对于固定的基和正标量 \(\tau\)，在工作模型
\(h\sim\mathcal{CN}(\mu,\tau I_{N^2})\) 中条件化到 \(h\in\operatorname{range}B_k\)，
均值与协方差为 \(P_k\mu\) 和 \(\tau P_k\)。这是线性约束下的 Gaussian 条件分布；
[Simpson–Turner–Pettitt (2008), §2 式(2), p.C1044](https://journal.austms.org.au/ojs/index.php/ANZIAMJ/article/download/131/1104)
给出的实 Gaussian 约束采样式取各向同性协方差后即为正交投影，实虚部表示得到这里的复数形式。
各天线使用相同 AFDM 基、保留原独立标量 Gaussian 近似时，对 \(N^2=256\) 个 AFDM 坐标平均，
条件空间协方差为 \(\tau\operatorname{tr}(P_k)I_M/N^2=3\tau I_M/256\)。
该因子由维数给出，并非根据测试标签选择的倍率。
实现随后沿用原标量 Gaussian site：只保留这个空间平均，不向下一模块传递
\(\tau P_k\) 的跨 AFDM 坐标相关性。因此这里是条件化后再作标量消息近似，
并非完整受约束 Gaussian 协方差的精确传播。

实际实现对每根天线分别令 \(F'_{k,m}=\operatorname{unvec}(P_k\operatorname{vec}F_{k,m})\)，
将原 second 的每用户原始风险读数乘 \(3/256\)，再按 T12 共同平均并应用原正值下限：
\[
 \tau'=\max\left\{\frac3{256K}\sum_k\widehat\tau_k,\;10^{-4}\right\},\qquad
 p_k=\operatorname{sigmoid}\{\operatorname{logit}\rho+\ell(R_k,v,F_k)\}. \tag{P2}
\]
这里采用当前相同的归一化坐标；一般接收机缩放仍按原配置换算下限。
Gaussian site 在正精度条件成立时由 \((F'_k,\tau')\) 构造。分类器输入仍是原未投影的
同查询 \(F_k\)，随后使用投影后条件均值重算 T16 的 Bernoulli 混合空间协方差。
阈值、阻尼、最小/最大轮数及停止窗口全部保持原配置。

P1 的基由同一观测估计，原网络均值、二阶读数和分类器也不是精确条件矩。
因此整个接收机仍是明确的工作近似：P2 的活动概率不是重新积分局部受约束先验得到的精确证据，
\(3/256\) 也不是已校准的实际误差倍率。负的原始风险读数与正值下限继续记录。
只改变均值而保留原方差的开发对照产生大量误报；它保留在结果目录中。
采用配套均值与协方差的版本须以冻结后的独立场景 NMSE、漏检及误报检验。

### 最终活动判决

投影后的迭代仍使用原分类器概率。在已观察的开发场景上，该概率有时很高，
但对应的完整信道估计能量很小。可选入口
[proposed_projected_energy.py](../../../src/afdm_jadcedd/algorithm/proposed_projected_energy.py)
在全部迭代结束后采用
\[
 E_k=\|\widehat X_k\|_F^2/\sigma_z^2,\qquad
 \widehat a_k=\mathbf1\{p_k\ge0.5\}\mathbf1\{E_k\ge\eta\}. \tag{P3}
\]
这里的 \(\widehat X\) 和公开噪声方差都采用物理尺度。\(E_k\) 是明确给出的
无量纲能量统计量，不是接收 SNR 或后验概率。判决门限的既有用法见术语表 Ding 式(27)；
使用公开噪声作分母、与原概率判决同时成立是本项目设置，不归为该论文的公式。

在 8 个开发场景和 10 个已观察历史场景、每场景两个低 SNR 条件上，
对全部 SNR 共用的一个 \(\eta\) 最小化活动错误数，同优区间取最小区间中点，
得到 \(\eta=30.6738313887353\)。这 18 个场景均作为开发数据，
留一物理场景检查只衡量已选规则的门限稳定性，不能替代新场景确认。
冻结记录为 [ENERGY_READOUT_SELECTION_V2.json](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_low_snr_20261015/ENERGY_READOUT_SELECTION_V2.json)。

P3 不回馈迭代、不修改 \(p_k\)、条件均值、协方差或完整信道输出。
输出 `probabilities` 仍是原分类器值；`activity_score=min(p/0.5,E/eta)`
在大于等于 1 时判活动，它不是概率。`activity_decision` 是最终 P3 判决，
`classifier_activity_decision` 保留原概率判决。完整 NMSE 对原 \(\widehat X\) 评分，
不按最终活动集合清零。该门限在当前维度和导频、噪声约定下标定，
不同系统规模需另行验证。它只能删除活动判决，可能新增漏检；必须计入 AER。

### 验证范围

P1–P3 在各 SNR 使用同一计算过程。独立确认中，低 SNR 改善未延续到中高 SNR：
0 dB 的 AER 退化，+6 dB 的 NMSE 与 AER 均退化。
因此该实现仍为实验候选，不能把条件 Gaussian 的代数恒等式当成整个学习接收机的性能保证。
逐档结果和下一轮统一推断的验证要求见 [PROPOSED_UNKNOWN_PHASE](../../STMP/docs/PROPOSED_UNKNOWN_PHASE.md)。


## 2026-11-04 正文矩阵记号映射

当前 C-STMP 正文使用 N×MN 设备矩阵 H_k：按天线将原 N×N 有效信道转置并横向拼接。原三维数组 H[k,m,r,n] 对应矩阵 [H_k]_{n,mN+r}；矩阵列 vec 与原数组 n 最快、r 次之、m 最慢的排列一致。本文件先前的物理分量推导和代码仍按原数组阅读，无需改变算法/网络布局。正文 μ_k 改为 H_k^post，c_k 改为 τ_k^ext。见 [本次公式复核](FORMULA_PROVENANCE_20261104.md)，包含全式出处及多周期/分数时延代数检查。
