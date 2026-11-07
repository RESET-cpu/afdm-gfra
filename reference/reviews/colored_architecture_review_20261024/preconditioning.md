# 已知有色 Gaussian 协方差下的 score / denoiser 参数化

2026-10-24。有界文献核查与解析推导；未修改训练、术语表、冻结模型，未启动训练或接收机实验。本文的 `h` 始终是除以既有尺度 `0.2647966452702405` 后的信道。原复数张量轴为 `[antenna, output, input]=[16,16,16]`，实数打包为 `[2,16,16,16]`。

## 1. 结论与证据强度

**建议优先检验：保留 CNN 主干，用已知协方差显式构造输入预条件、线性跳连和有界输出缩放，让 CNN 学线性估计的剩余部分。第一项对照保留原 DSM 损失及原数据/噪声分布；之后才单独比较 EDM 权重。** 这既有 EDM 的标量依据，也有 iCCDM 的对角协方差先例。推广到本项目任意旋转的 Kronecker 协方差，下面给出独立代数核查；论文没有验证本项目的网络、信道或接收机。

当前参数化和损失在数学上成立。问题是其有限训练阶段的条件数、误差传递与目标权重可能不利；不能把合法的 score matching 说成公式错误，也不能由早期 NMSE 断定 CNN 容量不足或条件 MLP 是唯一原因。

“改成 mean 输出”有两种不同含义。仅把当前 `r+Σs` 改名为 mean，保留全部计算，优化完全不变。真正可检验的改动是改变原始 CNN 输出的目标及其解析输入/输出映射，而不是换变量名。

## 2. 直接核实的一手来源

### 2.1 EDM：标量预条件及大噪声下的相消问题

Tero Karras, Miika Aittala, Timo Aila, Samuli Laine, **Elucidating the Design Space of Diffusion-Based Generative Models**, NeurIPS 2022，读取 [arXiv v2 PDF](https://arxiv.org/pdf/2206.00364v2)。PDF p8 §5 Eq(7)–(8) 讨论以标准化噪声构造 `D=x−σF` 时，大噪声下须精确相消且原始网络误差被 σ 放大，提出输入、跳连、输出预条件。p3 Table 1 给出系数；pp28–29 Appendix B.6 Eq(114)–(144) 推导单位输入/目标方差及损失权重。p9 Table 2 显示预条件本身并非在所有设置下提高 FID，主要收益包括训练稳健性；图像 FID 结果不能当作本项目 NMSE 保证。

官方实现版本 `008a4e5316c8e3bfe61a62f874bddba254295afb`：

- [`training/networks.py` L632–668](https://github.com/NVlabs/edm/blob/008a4e5316c8e3bfe61a62f874bddba254295afb/training/networks.py#L632-L668)：`EDMPrecond`；L660–667 实现 `c_skip/c_out/c_in/c_noise` 及 `D=c_skip*x+c_out*F`。
- [`training/loss.py` L66–80](https://github.com/NVlabs/edm/blob/008a4e5316c8e3bfe61a62f874bddba254295afb/training/loss.py#L66-L80)：`EDMLoss`；L75、79 是权重和加权 mean MSE。

图像默认 `sigma_data=0.5` 是**标准差**，不可直接移植为归一化复信道的实坐标方差。原论文是各向同性噪声，不应把以下非对角协方差应用归给 Karras 原文。

### 2.2 iCCDM：确实存在矩阵预条件，但实验采用对角协方差

Xin Ding, Yun Chen, Sen Zhang, Kao Zhang, Nenglun Chen, Peibei Cao, Yongwei Wang, Fei Wu, **Enhancing Diffusion-Based Quantitatively Controllable Image Generation via Matrix-Form EDM and Adaptive Vicinal Training**, arXiv:2602.02114v1, 2026，[PDF](https://arxiv.org/pdf/2602.02114v1)。PDF p3 §III-C Eq(7)–(9) 明确构造对角噪声协方差；p5 §III-D2 Eq(19)–(20) 给矩阵输入、跳连、输出系数；同页 §III-D3 Eq(22) 后给对角损失权重。它不是“batch/label 排成矩阵”的命名，确实处理不同坐标的不同 Gaussian 方差；但未验证本项目非对角、随机旋转的 `Ra⊗I⊗Rc`。

**编号差异：** arXiv HTML 把多行公式拆号，HTML 的 Eq(40)–(42)、(50)，分别对应实际下载 PDF 的 Eq(19)–(20)、Eq(22) 后的未编号权重。引用优先用上述 PDF 页码和编号。

官方 [CCDM 仓库 `iCCDM/diffusion.py`](https://github.com/UBCDingXin/CCDM/blob/a63aa63010255b0b3107411c2d53e7869b8af9c3/iCCDM/diffusion.py)，版本 `a63aa63010255b0b3107411c2d53e7869b8af9c3`：L183–214 为三项预条件，L245–270 是应用，L495–502 是损失平方根权重。代码处理 `cov_diag`，不是稠密矩阵运算。

值得保留的原文/代码差异：PDF Eq(20) 写 `C_noise=log(Σ)/4`；若 Σ=σ²I，此项是 `logσ/2`，不同于 EDM 的 `logσ/4`。官方代码 L216–218 实际使用 `logσ/4`，并解释 Σ 由 σ 和标签共同确定。故不应机械复制论文的 noise embedding。本项目随机 Ra/Rc 不能由标量 v 推出，仍须保留它们的条件信息。

### 2.3 一般协方差 Tweedie 与 DSM

Nicolas Zilberstein, Santiago Segarra, Eero P. Simoncelli, Florentin Guth, **Learning Normalized Energy Models for Linear Inverse Problems**, arXiv:2605.15487v1, 2026，[PDF](https://arxiv.org/pdf/2605.15487v1)。PDF p3 §3.1 Eq(7)–(8) 对 `r=h+Σ^(1/2)ε` 给 `E[h|r,Σ]=r−Σ∇U(r,Σ)`，其中 U 是负对数密度；p4 §3.2 Eq(9) 给 Σ^(1/2) 加权的 anisotropic DSM，正好对应本项目当前 loss 的 score 符号。其额外 covariance-score 正则化 Eq(10) 主要用于约束不同协方差下的能量及归一化。§3.3 实现限制为在空间或 Fourier 域对角的协方差，并使用位置相关的条件调制。

本文据此采用一般协方差 Tweedie/DSM 身份，但不引入能量网络、协方差导数目标或密度归一化任务。完整协方差条件不能由一个标量噪声等级替代。引用的是已读取的 v1 标题和正文，不把后续发表题名、版本差异混入。

### 2.4 EDA 的适用性筛查

Xingyu Qiu, Mengying Yang, Xinghua Ma, Dong Liang, Fanding Li, Gongning Luo, Wei Wang, Kuanquan Wang, Shuo Li, **Elucidating the Design Space of Arbitrary-Noise-Based Diffusion Models**, arXiv:2507.18534v2, 2026，[PDF](https://arxiv.org/pdf/2507.18534v2)。PDF pp3–4 §3.1 Eq(9)–(11) 用可依赖干净样本的基 `H_x0` 和随机性参数 η 表示结构退化，包括非零条件均值；p4 Eq(17)–(18) 保留标量形式的 denoiser 训练/包装。其主要问题是 MRI 偏置、CT 伪影、阴影等退化及生成路径，不是为本项目已知、独立、零均值 Gaussian C 提供更直接的输入/输出矩阵预条件。因此本轮不采用它的采样器或任意噪声框架。

另检索到 TEDM（Carrillo、Naveenachandran、Niebling，ICLR 2026）的作者记录，但 [OpenReview PDF](https://openreview.net/pdf?id=kQee8MObMc) 此次返回 HTTP 403；未依据第三方摘要写入其公式，不作为已精读证据。

## 3. 当前代码对应的数学对象

本段是代码核查及本项目代数，不是文献实验结论。

设实数向量 `r,h∈R^n`，`n=2×16³=8192`。复数协方差为

\[
C=v(R_a\otimes I_{16}\otimes R_c),\qquad
\Sigma=\tfrac12\mathcal R(C),\quad
\mathcal R(C)=\begin{bmatrix}\Re C&-\Im C\\\Im C&\Re C\end{bmatrix}.
\tag{P1}
\]

这里 `real(C)` 必须表示**实数块表示** `𝓡(C)`，不是逐元素取实部。项目实虚打包次序与式(P1)一致；更换向量化次序时须加置换。因噪声 proper complex，实协方差有 1/2 因子。C 是 4096×4096 的复数算子，Σ 是 8192×8192 的实数算子，实际均不必构造。

条件生成模型为

\[
r=h+\Sigma^{1/2}\epsilon,\qquad
\epsilon\sim\mathcal N(0,I),\quad \epsilon\perp h\mid\Sigma.
\tag{P2}
\]

[`model.py` L26–35](../../../src/training/colored_score_20261024/model.py) 目前是 `sθ=fθ/σ0`，其中 `σ0=√(v/2)`；CNN 直接接收 r，1025 维协方差信息经原有 64 维条件支路调制。该支路是否足以表达全部条件作用尚未验证。

[`noise.py` L37–54、94–101](../../../src/training/colored_score_20261024/noise.py) 及实际训练使用的 [`formal_batches.py` L67–89](../../../src/training/colored_score_20261024/formal_batches.py) 实现

\[
L_{\rm DSM}=\mathbb E\|\Sigma^{1/2}s_\theta+\epsilon\|^2,
\qquad D_\theta=r+\Sigma s_\theta.
\tag{P3}
\]

代码用逐元素平均；以下省略不影响比较的共同 `1/n` 因子。由 P2–P3，逐样本严格有

\[
\boxed{L_{\rm DSM}=\mathbb E\|\Sigma^{-1/2}(D_\theta-h)\|^2.}
\tag{P4}
\]

因此当前 loss 是 **mean 误差的 Mahalanobis 加权平方损失**，并非普通 mean MSE。较大噪声特征值方向的同等 mean 误差被较小权重计入。这不改变无限表达能力且优化充分时的条件均值最优解，但会改变有限模型和有限训练的取舍；不能只比较两个候选的原始 loss 数值。

令 `R=𝓡(Ra⊗I⊗Rc)`，则 `Σ=σ0²R`，当前原始 CNN 输出的形式为

\[
L_{\rm DSM}=\mathbb E\|R^{1/2}f_\theta+\epsilon\|^2,
\qquad D_\theta=r+\sigma_0R f_\theta.
\tag{P5}
\]

原始输出误差 δf 沿 R 特征值 ρ 的方向被 `σ0ρ` 放大到 mean。它解释了一种可能的优化困难，**不是已识别的唯一失败原因**；不同参数化的原始输出误差分布并不相同，不能仅比较该倍率就断言性能优劣。

## 4. 三种可实现的参数化及目标差别

### 4.1 直接 mean 或噪声输出

直接定义 CNN 输出 `Dθ` 并用 P4 训练，仍以条件均值为最优解，但输入/目标量级仍随噪声变化。若用普通 `||D−h||²`，则已改变原 loss，需单列为目标权重对照。

也可让 CNN 预测标准白噪声 `qθ=−Σ^(1/2)sθ`：

\[
D_\theta=r-\Sigma^{1/2}q_\theta,\quad
L=\mathbb E\|q_\theta-\epsilon\|^2.
\tag{P6}
\]

这把已知相关结构显式放在输出中，省去网络表示 Σ^(-1/2) 的部分任务；但大噪声下仍须相消，且原始误差被 √λ(Σ) 放大。单独把输入变成 `Σ^(-1/2)r` 也会同时变换信道先验，并不等于原白噪声网络已见过的任务。因此 P6 不是最优先候选。

### 4.2 建议的矩阵输入/跳连/输出映射

选择固定的实坐标参考方差 `d²>0`，定义

\[
B=(d^2I+\Sigma)^{-1/2},\qquad
K=d^2(d^2I+\Sigma)^{-1},\qquad
O=d\Sigma^{1/2}(d^2I+\Sigma)^{-1/2},
\tag{P7}
\]

\[
\boxed{D_\theta(r,\Sigma)=K r+O F_\theta(B r,\operatorname{condition}(v,R_a,R_c)).}
\tag{P8}
\]

P7–P8 与 iCCDM 的对角矩阵公式一致。**将其视为 SPD 矩阵函数并用于本项目非对角 Kronecker C、以下矩阵恒等式和实现方式，是本项目推导与待验证应用，不是 EDM 原文的结论。** 本式默认参考均值为零；若需要非零参考均值 μ，则输入改为 `B(r−μ)`，输出为 `μ+K(r−μ)+OF`；μ 只可由训练数据确定。

这里 B 是输入预条件，通常**不把噪声变为白噪声**。在参考二阶模型 `Cov(h)=d²I`、噪声独立时，`Cov(Br)=I`，且原始训练目标

\[
F_{\rm target}=O^{-1}(h-Kr)
\tag{P9}
\]

的协方差为 I。证明只需二阶矩，不要求参考信道 Gaussian：

\[
\operatorname{Cov}(h-Kr)
=d^2\Sigma(d^2I+\Sigma)^{-1}=O^2.
\tag{P10}
\]

实际信道高度相关，所以本项目不应宣称 P9 的真实协方差已严格为 I。`d²I` 是解析预条件的参考二阶模型，不是已测量的真实信道先验。

P8 有以下确定性性质：

- `F=0` 时得到参考线性估计 `Kr`，无需由 MLP 学出该协方差作用。
- O 的任一特征值为 `d√λ/√(d²+λ)≤d`，故固定输入下原始输出误差的线性放大有上界。
- λ 很大时，K→0、O→d，不再要求 CNN 先复制大噪声再与 r 抵消。
- λ 很小时，K→I、O≈Σ^(1/2)，保留小噪声残差学习形式。

这些性质不保证完整 CNN Lipschitz 常数、接收机收敛或 NMSE 改善。O 有界也不保证训练后的 `F` 不会破坏线性基准。

`d²` 可由既有训练样本的实坐标二阶矩确定并冻结。若采用“归一化复数参考协方差 I”，对应的实参考方差是 **d²=1/2、d=1/√2**，此时 K 在复数域正好是 `(I+C)^−1`。不要把 EDM 图像默认标准差 `0.5` 当成这里的 `d²=0.5`。不使用 48 个接收机测试条件或此处 64 个开发诊断样本来拟合 d²、C 分布或方向基。

### 4.3 最容易混淆的损失权重

令 `a=Fθ−F_target`，有 `D−h=Oa`，于是：

| 要保持的 mean 目标 | 原始 CNN 输出损失 | 关系 |
|---|---|---|
| 原 DSM：`(D−h)^TΣ⁻¹(D−h)` | `a^T K a` | `OΣ⁻¹O=K`，与当前目标完全一致 |
| EDM/iCCDM 对应权重 | `||a||²` | mean 权重 `O⁻²=Σ⁻¹+d⁻²I` |
| 普通 mean MSE：`||D−h||²` | `a^T O² a` | 与前两者不同 |

因此先实施 P8 并保留原 DSM 权重时，**不能无说明地把 raw residual loss 写成无权 MSE**。无权 raw residual MSE 会增加普通 mean MSE 权重：

\[
L_{\rm EDM\,weight}
=L_{\rm DSM}+d^{-2}\mathbb E\|D-h\|^2.
\tag{P11}
\]

给定 r、Σ，上述三个正定且只依赖已知条件的权重均以 `E[h|r,Σ]` 为总体最优解；实际训练轨迹、梯度尺度和能力分配不同。第一轮保持 DSM，有利于隔离参数化作用；P11 应作为另一个候选，而非混在同一次改动中归因。

白噪声退化：Σ=σ²I 时，

\[
B=\frac I{\sqrt{d^2+\sigma^2}},\quad
K=\frac{d^2I}{d^2+\sigma^2},\quad
O=\frac{d\sigma I}{\sqrt{d^2+\sigma^2}},\quad
O^{-2}=\frac{d^2+\sigma^2}{d^2\sigma^2}I.
\tag{P12}
\]

这四项分别严格退化为 EDM 的 `c_in,c_skip,c_out,λ`。原 DSM 对应的 raw 权重仍是 `d²/(d²+σ²)`，**不是** EDM 的单位 raw 权重。条件编码可继续用现有的 log v 和完整轴因子，不能宣称它等同 EDM 的经验性 `logσ/4` 编码。

### 4.4 若以后使用非各向同性参考信道协方差

仅作为解析边界：给参考 SPD 二阶矩 S，线性系数应是 `K=S(S+Σ)^−1`，输入 `B=(S+Σ)^−1/2`，残差协方差

\[
P=S-S(S+\Sigma)^{-1}S=(S^{-1}+\Sigma^{-1})^{-1},
\qquad O=P^{1/2}.
\tag{P13}
\]

一般 S 与 Σ 不可交换，不能任意改变乘法次序；保留 DSM 的 raw 权重是 `OΣ⁻¹O`，一般不等于 K。第一项候选不建议额外拟合完整 S：会增加训练数据估计、正则化、维数和归因问题；P7 已能显式利用已知 C。

## 5. Kronecker C 的可实现性与网络条件边界

对两个 16×16 Hermitian 因子分解

\[
R_a=U_a\operatorname{diag}(\alpha)U_a^H,\quad
R_c=U_c\operatorname{diag}(\gamma)U_c^H.
\tag{P14}
\]

C 的复数特征基是 `U=Ua⊗I16⊗Uc`，对应实算子 Σ 的特征值是 `λ=(v/2)α_iγ_j`，输出轴上重复，实虚上再重复。先按明确的自然轴顺序进入该基，在 `(i,j)` 的联合特征值网格上计算 P7 的三个标量函数，再回到原坐标即可。**B、K、O 一般不是两个轴函数的 Kronecker 积**；例如 `(d²I+Σ)^−1` 不能错拆成两个独立的 `(...+Ra)^−1`、`(...+Rc)^−1`。

因此无需构造 4096×4096 复数或 8192×8192 实数矩阵，更无需让条件 MLP 学矩阵求逆。可以在原坐标输出预条件后的张量再送入现有 CNN，保持其原来的空间布局。直接在每个样本不同的特征基上做卷积是另一项架构选择，会改变信道结构与卷积归纳偏置，不能悄悄一并加入。

P8 的三个已知线性算子绕过 1025→64 条件压缩，保留完整 C 的解析作用；但剩余非 Gaussian 后验修正仍可能依赖 C，故保留现有完整条件输入，并把“64 维足够”留作待验证问题。显式算子也不等于解决全部条件表达。

若下游确实需要 score，可用已知算子 `s=Σ⁻¹(D−r)` 恢复，而非新建一个学习逆矩阵的网络。若下游只需要 mean，则可避免这次求解。在固定 Σ 下，

\[
J_D=K+O J_F B.
\tag{P15}
\]

应对整个预条件映射求导，不能只用 CNN 主干的 Jacobian。实数与复数 score 的定义及 1/2 因子必须与 P1 保持一致。有限训练的任意 D 未必对应一个保守 score 场或合法后验协方差；P15 不自动提供这些性质。

## 6. 已有开发证据与有限建议

读取本目录 [CONDITION_PROBE.json](CONDITION_PROBE.json)，未复跑。它是 epoch 20 的保存权重 `first_best.pt`（SHA256 `1315fd2e2e1bef1cb5ef0e44c5665336816fdd1da1189790f75c70c13494bb57`），共 64 个独立开发场景，每档 16 个，真实合成 C 已知、真值 h 仅用于评分：

| 合成噪声 SNR 范围 | 正确 C 条件网络 mean NMSE/dB | 打乱 C 条件 | I 条件 | 参考线性 `(I+C)⁻¹r` | 零估计 |
|---|---:|---:|---:|---:|---:|
| [−20,−10] | +13.953 | +14.252 | +14.466 | −0.194 | 0 |
| [−10,0] | +3.329 | +3.439 | +3.649 | −1.914 | 0 |
| [0,10] | −5.488 | −5.288 | −5.007 | −5.595 | 0 |
| [10,30] | −19.496 | −19.298 | −19.176 | −18.039 | 0 |

这里线性估计采用**参考复信道协方差 I**，不是实际先验已知的 oracle。结果支持“显式线性跳连值得检验”，也显示当前网络确实对 C 条件有响应；它不能证明唯一原因是 MLP 压缩，也不能证明预条件后的 CNN 能学好剩余量。样本量不足以报告正式总体增益，且这是合成去噪开发诊断，不是 STMP 1000 场景结果。

后续最小对照范围：

1. P8 保留原 CNN、原训练信道、原噪声族、原 DSM 权重和相同预算，单独记录输入/输出预条件改变。初始化策略也须明确；把输出层额外置零会改变初始化，不应在“同初始化”对照中隐瞒。
2. 同时检查 mean NMSE、原 DSM、零估计和参考线性估计，按噪声档及协方差谱分层；若原 DSM 继续下降而低 SNR mean 不改善，不能仅依赖加权 loss 选出“更优”模型。
3. 只有参数化对照有结果后，再单独检验 P11 的权重；不顺便改成 EDM 图像 lognormal 噪声采样或引入扩散采样器。

这仍是“一阶条件去噪器如何学习已知 Gaussian 输入族”的问题，与通过端到端十层展开适配实际迭代消息的训练范围不同。它不处理实际消息的条件均值偏差、信号依赖、跨用户/跨轮相关或伪协方差；若接收机 query 不满足 P2，解析预条件不能把这些失配自动修复。

## 7. 下载与代码定位记录

下载时间：2026-10-24。均验证 `%PDF` 文件头；PDF 页码为从 1 起计的物理页。未把未取得的 TEDM 全文写成已读。

| 本地文件 | 来源 | 字节数 | SHA256 |
|---|---|---:|---|
| `papers/karras2022_edm.pdf` | `https://arxiv.org/pdf/2206.00364v2` | 19211841 | `0cf53de9ac234366fdba08d472afa236d46edd8202fda340f579aa2db866087a` |
| `papers/ding2026_iccdm.pdf` | `https://arxiv.org/pdf/2602.02114v1` | 1326824 | `9806118d8a241613634cb0a51426fa75bfb951e4131d118b46e49e373fcc7b81` |
| `papers/zilberstein2026_anisotropic_energy.pdf` | `https://arxiv.org/pdf/2605.15487`，下载为 v1 | 13255006 | `6a3bfecd2c53d5dd805aa1cf25d256266abf005be03a31c01a455a52a699e496` |
| `papers/qiu2026_eda.pdf` | `https://arxiv.org/pdf/2507.18534v2` | 1778988 | `561ab3d988926d054617710543a85ee920f07260e190bf907958ebe025b97400` |

读取的官方代码文件 SHA256（未覆盖或引入项目算法）：

- NVlabs/edm `training/networks.py`：`5db27dcd96674b95c72d5e6491b879cdc35e24039ada3411b4b46a28ed1fe284`。
- NVlabs/edm `training/loss.py`：`b26f0937bc72b18cc5f9869c86035ca9b872138cdfae7994237e9733951e4415`。
- UBCDingXin/CCDM `iCCDM/diffusion.py`：`28f7c1c818f4593ba3922954869e119975c558a3e15b2d075a189722822a82c8`。

以上事实、项目恒等式与建议已分开；尚无本项目 P8 训练效果、接收机增益或统计显著性的验证结果。
