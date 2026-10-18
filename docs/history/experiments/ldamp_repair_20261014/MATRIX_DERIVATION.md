# 复数多测量向量下的 L-DAMP 校正

这是当前场景适配的开发推导及实现约定。它保留 D-AMP 的去噪、残差更新和 Monte Carlo 导数思想，不声称结构化 AFDM 观测矩阵满足高斯矩阵状态演化条件。

参考：He 等 §III-A 式(4)–(8)；Chen–Sohrabi–Yu ICASSP 2018 §3.1 式(2)–(4)；Kunde 等 *Complex Approximate Message Passing with Non-separable Denoising*，作者稿 v1，§III-C、式(18)–(21)，PDF p.12，[原文](https://arxiv.org/pdf/2604.21115v1)、[本地稿](../../references/ldamp_review_20261014/kunde2026_complex_amp.pdf)。最后一篇是 2026 年预印本，其高斯矩阵结论不直接覆盖本项目。

## 索引与分量定义

将 H[k,m,r,n] 重排为 X[(k,n),(m,r)]，故 N=640 个被感知坐标，C=256 个特征，Q=16 次观测，Y=AX+W。去噪器可以联合处理同一用户的全部坐标。

采用下列显式定义避免矩阵导数的行/列约定混淆：

\[
B_{ab}^{t}=\frac1Q\sum_{i=1}^{N}
  \frac{\partial D_{i,b}(R^t;\Sigma^t)}{\partial R_{i,a}^{t}},
\qquad \frac{\partial}{\partial z}
=\tfrac12(\partial_{\Re z}-\mathrm i\partial_{\Im z}).
\]

即 B 的第一个下标为输入特征、第二个为输出特征。若 D(R)=RT+R*U，则 B=(N/Q)T，U 不进入 proper-complex 高斯观测的这一校正。代码和独立测试均使用一般非对称复矩阵 T，不能用只测实标量收缩掩盖转置或虚部错误。

从分量看，移去第 μ 个观测使 R[i,a] 改变 A*[μ,i] Z[μ,a]。线性化去噪输出并乘 A[μ,i]，其 ∂D/∂R 项产生 |A[μ,i]|² Z[μ,a] ∂D[i,b]/∂R[i,a]。对 i 求和，以 1/Q 替代随机高斯矩阵的平均 |A|²，即得到 (ZB)[μ,b]；共轭导数项乘 A[μ,i]²，在 proper-complex 独立高斯矩阵下均值为零。此平均替代用于实际 AFDM 矩阵是待实验检验的近似，不是已证明恒等式。

更新为

\[
R^t=X^t+A^H Z^t,\quad X^{t+1}=D(R^t;\Sigma^t),
\quad Z^{t+1}=Y-AX^{t+1}+Z^t B^t.
\]

\(\Sigma_{ab}^t=Q^{-1}\sum_\mu Z_{\mu a}^t\overline{Z_{\mu b}^t}\) 是复协方差约定；不把转置的 Gram 矩阵误用作协方差。若去噪器仅接收 trace(Σ)/C，仍未处理相关噪声，须在试验中明确标记。

## 随机部分迹

令 U 为 N×C 复扰动，满足 E[conj(U[i,a]) U[j,b]]=δijδab。固定当前 Σ 及网络选择，定义

\[
V=\frac{D(R+\epsilon U)-D(R-\epsilon U)
-\mathrm i[D(R+\mathrm i\epsilon U)-D(R-\mathrm i\epsilon U)]}{4\epsilon}.
\]

在可微点，小步长下 V 是 Wirtinger Jacobian 对 U 的作用，共轭导数被成对扰动抵消。\(\widehat B=U^H V/Q\) 的期望是上式的部分迹。ReLU 边界采用中心差分；有限步长、float32 和有限扰动数仍产生近似误差。

实现以随机行/列相位和行置换构造 DFT 的 C 个列，使 UᴴU=NI，同时保留上述二阶矩。这样，对常数线性特征映射 RT，一次扰动就无抽样误差；对任意联合非线性去噪器不保证一次扰动准确。它是项目的 Monte Carlo 取样选择，不命名为新算法。

独立坐标有限差分、复数非对称线性映射、共轭映射、非局部行混合及完整两步迭代的检查见 [MATRIX_ALGEBRA_CHECK.json](../../results/ldamp_implementation_20261014/MATRIX_ALGEBRA_CHECK.json)。非局部随机检查使用 512 个扰动，不能将其误差精度归给实际仅用少量扰动的接收机。

### 逐波束网络与随机估计精度

固定当前协方差和噪声区间时，逐波束共享网络没有跨波束输入依赖。因此 B 的跨波束块严格为零；实现仅估计各 16×16 块。这一结构来自具体网络的可分性，不是为了稳定而任意裁去 Jacobian 元素。

另作一个减少网络调用次数的开发对照：采用正频率 DFT 列、随机行符号、列相位和行置换，构造满足 UᴴU=NI、UᵀU=0 的扰动。随机行符号与列相位还保证二阶矩的各向同性和零伪协方差。仅用 [D(R+εU)−D(R−εU)]/(2ε)，其共轭导数贡献在期望下消失；对于常系数复线性和共轭线性映射，一次扰动即精确。一般非局部映射的有限抽样误差更大，不等同于每次扰动都显式抵消共轭导数。

该对照的非局部复线性检查，512 次扰动误差为 5.1095%，未满足预先采用的 5% 检查目标；同一随机流增加到 2048 次后为 2.9634%，保持原目标。两组数字均保留。两个 0 dB 开发场景的完整接收机结果也表明：这一对照用一次扰动时明显弱于成对方向的两次扰动；即使代数无偏，也不能把少量抽样直接当作准确校正。

冻结网络的 CPU/MPS 相对误差为 1.64×10⁻⁶。改变 CPU 推断批次大小的最大绝对差 1.69×10⁻⁵ 未通过最初 10⁻⁵ 的绝对检查；进一步相对误差为 4.45×10⁻⁶，同权重 float64 骨干批次差为零，符合 float32 卷积累计顺序变化。没有通过放松统计性能标准来消除此记录。见 [FROZEN_BEAM_CHECK.json](../../results/ldamp_implementation_20261014/FROZEN_BEAM_CHECK.json)。

## 冻结网络的精确实方向导数

最终候选不再用有限差分计算网络方向导数。固定区间、输入尺度、BatchNorm 运行统计和本次前向的 ReLU 掩码，对任意实参数方向 Δ 直接沿网络作链式计算：卷积只保留权重线性项，BN 乘 γ/sqrt(v+ε)，ReLU 乘前向掩码，残差输出的导数为 Δ 减去噪声预测支路导数。

令 L_R(Δ) 是完整复数表示下的实方向导数，则

\[
V=\tfrac12\{L_R(U)-\mathrm i L_R(\mathrm iU)\},\qquad
\widehat B_{ab}=Q^{-1}\sum_i \overline{U_{ia}}V_{ib}.
\]

该成对操作在每个探针上抵消共轭导数；ReLU 在零点采用与 PyTorch autograd 相同的零导数约定。CNN 方向导数没有有限差分步长误差，部分迹仍有有限探针的 Monte Carlo 误差。最终候选使用八个探针，每个探针两个实方向，十轮迭代；每轮的协方差和选择区间在求导期间固定。独立 autograd 检查见 [EXACT_DIRECTIONS_CHECK.json](../../results/ldamp_implementation_20261014/EXACT_DIRECTIONS_CHECK.json)。

固定 4×4 阵列 DFT 在感知算子的未感知空间轴作用，与公开 P 可交换。其后的双边 DAFT 变换和时间重排只在去噪器内部使用，并将输出及方向导数完整逆变换后再作上述部分迹；不是直接把原 P 当作变换后的感知矩阵。

实际代码还采用 g=sqrt(‖P‖²_F/(KN))，A=P/g，Y=Y_public/(scale·g)，X=H/scale。最终返回 scale·X。尺度只来自固定训练总体，不读取测试真值功率。

## 后续证据要求

先在相同冻结去噪器、相同开发场景上比较标量与矩阵校正，隔离更新变化；另检查增加扰动数量时结果是否稳定。随后训练与真实查询误差相匹配的去噪器。最终独立接收机验证及原场景统一比较通过前，不将这段开发代码安装为主线实现。
