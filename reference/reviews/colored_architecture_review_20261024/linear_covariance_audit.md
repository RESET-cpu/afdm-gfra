# 当前线性模块能否提供 v、Ra、Rc：独立代数核查

2026-10-24。仅只读代码、推导公式及读取主任务已生成的审计结果；本笔记没有修改接收机/训练，没有调用网络或启动接收机。

**结论：可以从已有 SVD 恢复当前未阻尼查询的每用户输入列工作协方差。当前 isotropic 配置下，它精确具有 `Ra=I`、`Rc=16×16 输入列矩阵` 的可分形式；但这不是已经识别的真实闭环误差协方差。实际查询阻尼所需的跨轮项、反馈误差与信号/测量噪声的相关性，不能从已有边缘消息参数唯一恢复。**

这里保持现有全局 trace 归一化及同一输入下的原查询 r，仅给它增加协方差描述。不采用此前逐输入模式重新归一化的查询。因此不存在由这项元数据计算本身造成的首轮约 27 倍 query MSE 改变；接入新去噪器后的闭环轨迹仍需另行验证。

## 1. 代码、维度与工作假设

- [linear.py L52–77](../../../src/algorithm/STMP/linear.py)：`SpatialLinear.update`，L62 是各天线特征模的增益，L63 是全640维 trace 归一化，L72 返回原查询 r，L73–76 只返回投影后的天线矩阵。
- [iterations.py](../../../src/algorithm/STMP/iterations.py)：L18–26 是 Gaussian 参数阻尼；L69 阻尼查询；L74–75 把后验天线矩阵投影为各向同性；L86 再阻尼反馈。
- [当前 STMP 配置](../../../src/configs/final/STMP.json)：`covariance_mode="isotropic"`，`damping=0.2`。本笔记的实际配置判断以此为依据。

写 `x_k=a_kH_k/s`，`s=0.2647966452702405`，先验消息均值为 m，反馈误差 `η=m−x`。当用户活跃时 x 就是归一化信道；P 是线性模块收到的公共天线**消息协方差参数**，不是已经知道的物理信道先验。

每用户张量为 `[M,R,N]=[16,16,16]`，依次表示天线、输出行、输入列。令 `L=KN=40×16=640`。线性模块对每个天线/输出行应用同一个 `A∈C^(16×640)`；256 个 MMV 列是天线×输出行，不是256根天线。

冻结 A、代码使用的归一化测量噪声方差 ν、输入 P，令

\[
P=U_P\operatorname{diag}(c_1,\ldots,c_M)U_P^H,
\qquad A=U_A\operatorname{diag}(s_i)V^H.
\tag{L1}
\]

在第 j 个天线特征模、一个输出行上，η 是 L 维向量。计算下述工作协方差所需的二阶假设为

\[
\operatorname{Cov}(\eta_j)=c_j I_L,\quad
\operatorname{Cov}(n_j)=\nu I,\quad
\operatorname{Cov}(\eta_j,n_j)=0,
\tag{L2}
\]

且各天线特征模、输出行之间没有误差互协方差。若 η、n 还联合 proper Gaussian，则线性输出误差也是 proper Gaussian；**要进一步得到训练所要求的 `e|x,C~CN(0,C)`，还必须有对 x 的独立性/零条件均值。L2 本身没有这一保证。** 把迭代得到的随机 P 临时固定是工作模型，不是对真实过程条件分布的证明。

## 2. 不改变现有 r 的完整工作协方差

对一个天线模 j 省略下标。定义

\[
g_i=\frac{c s_i}{\nu+c s_i^2},\quad
W=V\operatorname{diag}(g_i)U_A^H,\quad
H=WA=V\operatorname{diag}(d_i)V^H,\quad d_i=s_i g_i,
\tag{L3}
\]

\[
\alpha=\frac{\operatorname{tr}H}{L},\quad
B=\alpha^{-1}W,\quad D=I-\alpha^{-1}H.
\tag{L4}
\]

代码的原查询恰好是

\[
r=m+\alpha^{-1}W(y-Am),\qquad
e=r-x=D\eta+Bn.
\tag{L5}
\]

在 L2 下，

\[
E=\operatorname{Cov}(e)
=c(I-H/\alpha)^2+\nu WW^H/\alpha^2.
\tag{L6}
\]

逐个奇异值可核对

\[
cd_i^2+\nu g_i^2=cd_i,
\qquad cH^2+\nu WW^H=cH.
\tag{L7}
\]

因此主任务提出的公式正确：

\[
\boxed{E=c\left[I+(\alpha^{-2}-2\alpha^{-1})H\right].}
\tag{L8}
\]

这是固定 A 的精确二阶代数，不需要 Haar 矩阵或状态演化假设。对于当前尺寸，`α≤rank(A)/L≤16/640=0.025`，所以 L8 的 H 系数为正；E 正定。一般尺寸下也应按 L6 理解其半正定性，不能只看展开式某一系数的符号。

当前输出的标量并没有和 L8 冲突：

\[
\frac{\operatorname{tr}E}{L}
=c\frac{1-\alpha}{\alpha},\qquad
\frac1L\operatorname{tr}\{c(I-H)\}=c(1-\alpha).
\tag{L9}
\]

它们分别是 `cavity` 和 `post_c` 在该天线特征模上的参数。现有代码保留了全局平均方差，丢掉了输入列方向、用户差异及跨用户块，而非没有能力计算这些信息。

### 2.1 每用户块可直接从薄 SVD 得到

取 V 中用户 k 对应的16行 `V_k`，无需形成完整640×640矩阵：

\[
\boxed{
E_{k,j}=c_j I_N+c_j(\alpha_j^{-2}-2\alpha_j^{-1})
V_k\operatorname{diag}(d_{i,j})V_k^H.}
\tag{L10}
\]

已有对象一一对应：`self.v` 为 V；`self.s*gain[:,j]` 为 d；`fraction[j]` 为 α；输入 P 的 `eigh` 给 c、U_P。只需对用户块新增小矩阵乘法。

跨用户块同样存在：k≠ℓ 时，

\[
E_{k\ell,j}=c_j(\alpha_j^{-2}-2\alpha_j^{-1})
V_k\operatorname{diag}(d_{i,j})V_\ell^H.
\tag{L11}
\]

每用户独立调用去噪器只使用 L10 的边缘，不能据此声称不同用户的查询误差独立。

在自然 `[antenna,output,input]` C-order 下，每用户完整工作协方差是

\[
\boxed{
C_k^{\rm raw}=\sum_{j=1}^M
(u_j u_j^H)\otimes I_R\otimes E_{k,j},}
\tag{L12}
\]

u_j 是 U_P 的第 j 列。输出轴上的 I_R 来自 L2 的额外工作假设，不能由“同一个 A 被重复使用”单独推出。

## 3. 与 v、Ra、Rc 接口的对应

### 3.1 当前 isotropic 配置：未阻尼时可以精确对应

初始化 `P=cI`。在精确算术下，线性 cavity、各向同性后验投影、`gaussian_extrinsic` 及两次参数阻尼都保持天线矩阵为标量 I。因此当前配置的各 j 具有相同 c、H、α 和 E_k；L12 化为

\[
C_k^{\rm raw}=I_M\otimes I_R\otimes E_k.
\tag{L13}
\]

选择明确的 trace 归一化约定

\[
\boxed{v_k=\operatorname{tr}(E_k)/N,\quad
R_{a,k}=I_M,\quad R_{c,k}=E_k/v_k,}
\tag{L14}
\]

即 `tr(Ra)=M`、`tr(Rc)=N`，满足新网络的 `C=v Ra⊗I_R⊗Rc` 接口。平均用户方差满足

\[
\frac1K\sum_kv_k=c(1-\alpha)/\alpha,
\tag{L15}
\]

恰好还原旧全局 cavity 标量。此处 Ra=I 只描述当前线性工作模型；不否认真实信道、早期真实误差的天线相关。

若 E_k 恰为标量 I，Rc=I，退回白噪声标量描述。一般固定 A 下即使输入 P 各向同性，E_k 仍是有色的；不能将“输入各向同性”误解成“输出误差各向同性”。

### 3.2 若以后使用 spatial P：单一 Kronecker 乘积一般不精确

L12 是多个 Kronecker 项之和。只有所有 `E_k,j` 都与同一个输入列矩阵成比例时，才可精确写成一个 `v Ra⊗I_R⊗Rc`。一般 c_j 不同使 H_j 的谱响应不同，因此条件不成立。

若只需一个明确的可分近似，可用部分迹匹配：

\[
Q_a=\frac1N\sum_j\operatorname{tr}(E_{k,j})u_ju_j^H,
\quad Q_c=\frac1M\sum_jE_{k,j},
\quad v=\frac{\operatorname{tr}Q_a}{M}=\frac{\operatorname{tr}Q_c}{N},
\tag{L16}
\]

令 `Ra=Qa/v`、`Rc=Qc/v`。它保持两个轴的边缘二阶矩，但没有证明这是完整 C 或最优近似。当前 isotropic 情形无需这一步近似。

## 4. 实际阻尼查询缺少什么

设 `e_old` 是上一轮已阻尼查询误差，`e_raw` 是本轮未阻尼查询误差，代码权重为 ω。实际均值操作给

\[
e_{\rm new}=(1-\omega)e_{\rm old}+\omega e_{\rm raw}.
\tag{L17}
\]

它的中心协方差满足

\[
Q_{\rm new}=(1-\omega)^2Q_{\rm old}+\omega^2Q_{\rm raw}
 +\omega(1-\omega)(T+T^H),
\quad T=\operatorname{Cov}(e_{\rm old},e_{\rm raw}).
\tag{L18}
\]

现有 `moment_damp` 插值的是 Gaussian **参数**：

\[
V_{\rm new}=(1-\omega)V_{\rm old}+\omega V_{\rm raw}.
\tag{L19}
\]

它不是 L18 的完整误差协方差传播，**不能因此把现有参数阻尼称为新发现的 bug**。如果 V_old、V_raw 恰好是真实协方差，那么还存在恒等式

\[
(1-\omega)Q_{\rm old}+\omega Q_{\rm raw}-Q_{\rm new}
=\omega(1-\omega)\operatorname{Cov}(e_{\rm old}-e_{\rm raw})\succeq0.
\tag{L20}
\]

但当前 V 本来是投影后的工作参数，因此不能据 L20 保证它是实际误差的保守上界。

两轮都使用同一测量噪声，T 中即使忽略反馈相关也会含 `B_old ν B_raw^H`；真实反馈又依赖同一个 y，因此还含反馈误差跨轮协方差及其与 n 的交叉项。已有 P_t 的边缘值不提供这些量。直接把 T 设零、把 ω 改平方或只传播 ν，均不是由现有证据推出的修复。

最小的**工作参数**扩展可以保持同一 r，并同时维护

\[
\bar E_{k,t}=(1-\omega)\bar E_{k,t-1}+\omega E_{k,t}^{\rm raw}.
\tag{L21}
\]

其用户平均 trace 与旧标量参数阻尼完全一致。L21 为同一查询保留输入列方向信息，但它仍是参数插值，不能写成已经校准的 L18。第一轮没有历史查询，raw 与实际 r 相同；以后应在诊断记录中分开 raw C、阻尼参数 C 和真实误差检验。可保留未投影的16×16矩阵，另外生成网络输入的近似副本，避免将投影误差反馈到参数历史。

## 5. C 正确也不保证独立 Gaussian 输入

这是比 trace 投影更根本的边界。即便假设真信道本身是白 proper Gaussian、真实 `Cov(x)=cI`，首轮 `m=0` 也意味着 `η=−x`。L8 可给出正确的无条件误差协方差，但

\[
r=\alpha^{-1}Hx+\alpha^{-1}Wn,
\quad \operatorname{Cov}(r-x,x)=c(H/\alpha-I)\ne0.
\tag{L22}
\]

全局 trace 归一化只令 `tr(H/α−I)=0`，并不令整个矩阵为零。在当前欠定系统中，H 的秩至多16，而 I 的维度是640，所以二者不可能相等。对独立零均值用户，在首轮

\[
\mathbb E[r_k\mid x_k]=(H_{kk}/\alpha)x_k,
\tag{L23}
\]

其自响应矩阵一般不是 I；其他用户及噪声被平均掉后，这个增益误差仍存在。只把 L8 作为独立噪声 C 提供给训练于 `r=h+e` 的网络，不能消除该误差。

更一般地，设 `Qη=Cov(η)`、`Sηn=Cov(η,n)`，则固定线性算子的真实二阶式为

\[
Q_e=DQ_\eta D^H+BQ_nB^H
+DS_{\eta n}B^H+BS_{\eta n}^HD^H.
\tag{L24}
\]

而 `Cov(e,x)=D Cov(η,x)`（若 n 与 x 独立）。L8 用 `Qη=cI`、`Qn=νI`、`Sηn=0` 代替了这些未知量。真实结构化信道、用户活动混合、非线性反馈都会使这些替代不精确；P 的16×16参数不包含输入列、输出行、用户及跨轮的全部相关信息。若存在均值偏差，则还需区分中心协方差与未中心化误差二阶矩；proper 性也不能由一个 Hermitian C 保证。

若代码使用估计噪声 ν_hat，而真实方差为 ν_true，即使其余 L2 成立，也须在 L8 上增加 `(ν_true−ν_hat)BB^H`。若观测算子含相位误差，误差还会增加 `B(A_true−A_used)x` 及其交叉项。它们都不能由一次 SVD 的 trace 信息补齐。

## 6. 与正在训练的协方差族是否匹配

新训练沿用 [noise.py L61–83](../../../src/training/colored_score_20261024/noise.py) 的轴因子族

\[
R=(1-\zeta)I+\zeta\frac{16GG^H}{\operatorname{tr}(GG^H)},
\quad G\in\mathbb C^{16\times4},\quad 0\le\zeta\le0.5.
\tag{L25}
\]

所以每轴 `λ_min(R)≥0.5`，且至少12个特征值位于同一个底值 `1−ζ`。原始 L14 的 Rc 一般不满足这两个条件。**接口能表示 SPD C，不等于已训练噪声分布覆盖了该 C。**

读取主任务生成的 [RESULT.json](../../../result/snr_comparison/data/linear_covariance_interface_20261024/RESULT.json)，未复跑：

- 小尺寸直接逆矩阵核对：用户块 covariance 最大相对误差 `8.54e−16`；原 query 复现相对误差 `4.85e−15`。
- 48 个已有公开条件的首轮 query 复现通过。没有使用真值、调用网络或运行完整接收机。这些条件来自既有开发记录，不构成独立性能验证集。
- 48×40=1920条用户记录的原始 Rc 全部不属于 L25。−4/0 dB 的最小特征值中位数分别为 `0.01058/0.01600`，不可直接作为“在训练分布内”的条件输入。
- 保留前4个特征方向、把后12个特征值平均，再按既有 ζ≤0.5 范围处理的可表示近似，其相对 Frobenius 误差中位数为 `0.3016/0.3014`；单位阵近似为 `0.6869/0.6841`。这支持进一步检验已有训练族内的近似，不能宣称约30%的矩阵误差已足够小或会改善检测。
- 所需 ζ 中位数 `0.4675/0.4637`；多数样本无需额外收缩至0.5。这是对当前工作 C 的可表示性检查，不是从误差真值估计噪声族，也不构成重训理由。

若对阻尼后的参数矩阵采用相同近似，必须重新检查其谱；不同方向的秩4矩阵做凸组合后，一般不再属于相同秩4族。

## 7. 最小可行建议

1. 线性侧只读计算 L10，并保留旧 α 和 r；输出 `v_k、Ra=I、Rc_k` 以及与旧 pooled cavity 的 trace 一致性。当前已有公开量足够完成这一项。
2. 需要描述实际阻尼 query 时，可先采用明确标注的 L21 参数近似，并保留 raw/阻尼两个记录；不将其称为真实误差协方差，不自行删除跨轮项。
3. 网络条件先在已有训练族内做近似可行性核查，保留与原矩阵、单位阵的距离；不要把近奇异原 Rc 直接投入网络，也不因接口差异直接要求重训。
4. 是否能作为有效去噪条件，仍需独立开发诊断检验均值增益、信号依赖和协方差匹配，再决定接入；公开工作 C 的计算或谱拟合本身不需要真值，真值仅可用于离线诊断与评分。

本次结果回答的是“现有线性侧能计算什么”。它支持增加协方差信息，尚不支持“当前模块已经提供了新网络训练假设中的真实独立有色 Gaussian 噪声”。
