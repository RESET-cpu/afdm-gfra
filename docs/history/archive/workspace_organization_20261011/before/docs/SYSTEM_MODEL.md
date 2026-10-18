# 观测模型、空间结构与实验信息

有效观测为
\[
Y_{qmr}=\sum_{k,n}A_{qkn}X_{kmrn}+W_{qmr},\quad X_k=\alpha_kH_k,
\quad W_{qmr}\sim\mathcal{CN}(0,\sigma^2).
\]

默认 K=40、Q=16、N=16、UPA 4×4，共同方向下 H_k=a(ω_k)G_k，展开为16×256矩阵。每用户各路径的连续时延、多普勒、增益进入 G_k。物理常数见 `src/afdm_jadcedd/system/config.py`，AFDM 路径算子见 `system/afdm/`。

接收机公开输入严格为 `observation`、`operator`、`noise_variance`、`activity_prior`。当前假定准确已知有效跨帧相位算子和噪声方差，活动、信道及方向未知；仿真真值只用于生成与事后评分。有效算子包含由仿真 Doppler形成的相位，这是明确的已知相位条件实验。

当前场景均要求至少一个活跃用户。设 Y₀=Σ_kA_kX_k，P_clean=||Y₀||²/(QMN)，并设置 σ²=P_clean×10^(−SNR_dB/10)。SNR表示所有活跃用户叠加后的无噪声接收能量与期望噪声能量之比，含用户间交叉项，不是逐用户 SNR。历史v3协议允许空场景，其固定参考噪声功率及已有统计保留。

活动生成先使用独立Bernoulli抽样概率p，再以J=Σₖαₖ≥1为条件重抽全零活动向量。归一化常数Z=1-(1-p)^K，实际单用户边缘概率ρ=p/Z，期望活跃人数Kρ。activity_probability表示p，公开activity_prior表示ρ；它由K、p计算，未输入场景真实人数。生成条件使各用户活动相关，式(S0)中的Π₀包含该条件分布；式(S2)仍采用独立边缘的工作近似。几何、完整活跃信道先验和其他随机流不因活动重抽而改变。

2026-10-10新增固定活跃人数的主对比条件：从K=40个候选用户中均匀随机选J=4人，
P(α)=1[Σₖαₖ=J]/C(K,J)，边缘活动先验ρ=J/K=0.1。活动集合独立于信道强弱，
单用户信道衰落分布、候选导频和有效相位规则未改，仍按当前总接收SNR定义噪声功率。
固定人数并不意味着活动独立；接收机仍采用原有独立Bernoulli工作近似和原生判决，
没有全局人数约束。该条件和J=2/6/8的配对补充见[固定人数实验协议](../experiments/fixed_activity_20261010/PROTOCOL.md)。
原非空Bernoulli默认生成方式及历史实验保留。

现有四轴开发面板的SNR取0、2、4、6 dB。论文六组实验安排见[实验协议](EXPERIMENT_PROTOCOL.md)：SNR组包含on-grid/off-grid两种条件，正式扫点待冻结。原低SNR结果完整归档，未来实验的范围不改变已有失败统计。Ding等AFDM-GFRA §IV-A与图3/4采用0–20 dB；不同论文归一化和信息条件须分别说明。

默认 `run.py simulate` 使用 `known_phase_geometry_v4`：沿用原地面位置、卫星几何、方向与时延／多普勒及固定阵列坐标系，并加入非空活动条件。原score训练及历史26个有效零错误输出采用独立随机阵列方向；后者不能直接转作默认几何分布上的独立性能结果。两种数据来源的原始配置与结果均可由归档索引定位。

## 给定公开输入后的条件模型

设ξ包含全部候选用户的几何、路径及导频生成变量，H_k=ℋ_k(ξ)为用户假设活跃时的信道，x_k(ξ,α)=α_k vec ℋ_k(ξ)。仿真生成有效算子 A=Φ(ξ)和按前述接收SNR规则得到的噪声方差 σ²=𝒱(ξ,α)。例如 Φ的跨帧项为 P_qkn exp(iqβ_k)，q从0计数、β_k=wrap[2πν_k(N+N_CPP)/BW]。若 Π₀(ξ,α)表示原场景生成分布，则完整联合分布为
\[
\begin{aligned}
dp_{\rm phys}(\xi,\alpha,A,\sigma^2,y)
={}&d\Pi_0(\xi,\alpha)\,
\delta_{\Phi(\xi)}(dA)\,
\delta_{\mathcal V(\xi,\alpha)}(d\sigma^2)\\
&\cdot\mathcal{CN}\bigl(y;A x(\xi,\alpha),\sigma^2I\bigr)\,dy.
\end{aligned}
\tag{S0}
\]

此式把准确已知算子、信号相关噪声功率和未知信道放在同一个生成模型中；ℋ、Φ、𝒱分别由物理路径模型、有效相位构造和观测生成规则确定。潜在信道H_k对非活跃用户不影响观测，保存的有效零信道也不增加接收机信息。

记 Π_phys(H,α|A,σ²) 为仿真物理联合分布在已知 A、σ² 下的条件先验。严格后验为
\[
dp_{\rm phys}(X,H,\alpha\mid y,A,\sigma^2)
\ \propto\
\mathcal{CN}(y;A x,\sigma^2I)
\prod_k\delta_{\alpha_kH_k}(dX_k)\,
d\Pi_{\rm phys}(H,\alpha\mid A,\sigma^2).
\tag{S1}
\]

这里用概率测度表示先验，允许秩一信道和非活跃零信号等不具有全维密度的情形。独立标准复 Gaussian 噪声在生成信道、算子和噪声方差之后采样，故式(S1)中的观测似然成立。

A 与 H 均由用户 Doppler及几何产生；共同使用这些变量尚不足以证明二者统计相关，也不足以证明独立。当前未证明 p(H|A)=p(H)。此外，σ²由所有有效信道叠加功率决定；给定 σ²一般可能改变活动先验、信道先验及用户间的条件独立性。历史空场景的固定参考方差属于原v3生成规则。接收机获得的是 σ²，并未获得 P_clean或活动数；条件信息的存在不等于接收机显式读取真值。

当前算法采用如下计算模型：
\[
dq(X,H,\alpha\mid y,A,\sigma^2)
\ \propto\
\mathcal{CN}(y;A x,\sigma^2I)
\prod_k\left[
\delta_{\alpha_kH_k}(dX_k)\,
q_{\rm tr}(dH_k)\,
\rho^{\alpha_k}(1-\rho)^{1-\alpha_k}
\right].
\tag{S2}
\]

q_tr是原score训练的活跃完整信道边缘先验，按固定尺度转换到相应信道变量单位；ρ是公开 `activity_prior`。式(S2)在固定已知算子下定义了完整的推断问题，采用 Cai §II-B式(5)的信道／活动因子分解。用 q_tr及独立 Bernoulli先验替代 Π_phys属于模型近似；式(S2)不声称等于式(S1)。同时，score去噪另采用标量 AWGN伪观测，实际有限 AFDM迭代是否符合该模型是另一项近似，不能由观测似然的正确性推出。

因此实验同时要报告已知算子、噪声方差的生成方式和训练先验来源。相同公开输入的算法比较可复现地评价本条件实验，但不能直接推及未知相位算子或不同噪声功率规则。两类近似的数学关系及验证范围见 [THEORY.md](THEORY.md)。

## 复包络、阵元编号和 Doppler 的统一符号

为完整解释当前生成器与路径算子的符号，明确采用
\[
 s_{\rm RF}(t)=\operatorname{Re}\{x(t)e^{-j2\pi f_ct}\},
 \qquad r(t)=g\,x(t-\tau(t))e^{+j2\pi f_c\tau(t)}
 \tag{S3}
\]
的复包络约定；第二式由接收端乘 \(e^{+j2\pi f_ct}\) 后低通得到，幅度常数归入 \(g\)。
令 \(L_k=\|g_k-s\|\)、\(u_k=(g_k-s)/L_k\)，固定地面终端有
\[
 \dot L_k=-v_{\rm sat}^{\mathsf T}u_k,\qquad
 \nu_k=f_c\dot L_k/c_0=-f_cv_{\rm sat}^{\mathsf T}u_k/c_0.
 \tag{S4}
\]
故块内载频相位的一阶变化为当前路径算子使用的 \(e^{+j2\pi\nu_k t}\)。
阵列投影轴为 \(e_y,e_z\)，明确以
\(s_m=s-n_yd_ye_y-n_zd_ze_z\)、\(m=n_z+M_zn_y\) 编号。
远场展开给出相对传播时延
\((n_yd_y\mu_{y,k}+n_zd_z\mu_{z,k})/c_0\)，从 S3 得到代码中的正号阵列响应。
负的索引位移和负载频复包络是一组配套约定；不能只改变其中一个符号再解释为同一表示。

这里采用阵列窄带、远场及块内固定包络时延／固定方向、保留一阶 Doppler 的模型近似。
静态载频传播相位归入复路径增益，公共参考时延在块参考时刻固定，不额外作公共 Doppler 补偿。
本次明确了此前未写出的复包络与阵元坐标约定，生成器、离散路径矩阵和已有训练数据均未改变。

分数延迟还需要连续时间波形定义：整数 IDAFT 样本和 CPP 不能单独确定非整数采样值。
当前 wrapped-chirp 基的实数时间定义、矩阵元素展开、整数长延迟极限与跨帧相位见
[论文草稿式(6a)–(13)](../paper/history/phase4_sections_20261008/draft.md)。
与 [Huang §II 式(5)，p.2950](../references/huang2026_prior_agnostic_afdm_diffusion.pdf) 的比较采用
\(k_{\nu,\rm Huang}=-\nu_{\rm here}NT_s\)，因为原式时间指数含负的 \(k_\nu\)，而本项目采用正的 \(\nu_{\rm here}\)。
