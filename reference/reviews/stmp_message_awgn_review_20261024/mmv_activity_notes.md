# MMV、相关信道与活动检测：定向原文核查

核查日期：2026-10-24。这是本轮调研的独立分工笔记，不是系统综述；未运行实验、未改算法。公式和页码按链接的 arXiv PDF 版本；期刊年份另行标明。

## 1. 文献证据

### M1 — Liu & Yu：白噪声状态是特定模型下的结论

Liang Liu, Wei Yu, **Massive Connectivity with Massive MIMO—Part I: Device Activity Detection and Channel Estimation**, IEEE TSP 66(11), 2933–2946, 2018。核查 [arXiv:1706.06438v2](https://arxiv.org/pdf/1706.06438v2)。

- §II / PDF p4，(6)、(11)：i.i.d. complex Gaussian pilots，活动信道先验为 Bernoulli–Gaussian，活跃时协方差为 `β_n I`。
- §III-B–C / p5，(13)–(21)：向量 AMP、矩阵状态演化，以及用完整 `Σ_t` 的 MMSE 去噪和活动概率。
- §III-D / p6，Theorem 1、(22)–(29)：在大系统极限、该各向同性先验与 MMSE 去噪器下，`Σ_t=τ_t² I`；该节随后明确将它归因于各天线信道不相关。
- §IV-A / p7，Theorem 2、(34)–(37)：误检/漏检分析依赖前述高斯等效模型。不能将“很多天线”单独解释为任意短导频、强空间相关信道也能使消息白化。

### M2 — Djelouat et al.：承认有色有效噪声，并让推断使用其协方差

Hamza Djelouat, Leatile Marata, Markus Leinonen, Hirley Alves, Markku Juntti, **User Activity Detection and Channel Estimation of Spatially Correlated Channels via AMP in Massive MTC**, Asilomar 2021；[arXiv:2112.04295v1](https://arxiv.org/pdf/2112.04295v1)。

- §II-A / p2：各用户信道协方差 `R_i` 已知；采用随机复 Bernoulli pilots。
- §III / p3，(8)–(11)：等效输入是 `θ_i=x_i+e`，`e~CN(0,Σ)`，不要求 `Σ=vI`。去噪器为 `ψ_i R_i(R_i+Σ)^{-1}θ_i`；活动概率同时使用 log-determinant 和协方差加权二次型；SE 保留完整 `Σ`。
- §IV / p3，(13)：活动与非活动的等效输入协方差分别为 `R_i+Σ` 和 `Σ`。`R_i` 是信道先验协方差，`Σ` 是有效噪声协方差，二者不可混为一谈。
- 该方法更换了去噪和活动 likelihood 的统计模型；不是证明有色输入可原样交给标量 AWGN 分类器。

### M3 — Hannak et al.：MMV 的矩阵 Onsager 与联合对角化

Gabor Hannak, Alessandro Perelli, Norbert Goertz, Gerald Matz, Mike E. Davies, **Performance Analysis of Approximate Message Passing for Distributed Compressed Sensing**, IEEE JSTSP 12(5), 857–870, 2018，DOI 10.1109/JSTSP.2018.2850754；[arXiv:1712.04893v2](https://arxiv.org/pdf/1712.04893v2)。

- §II-A–C / pp2–3，Algorithm 1、(9)–(11)：Gaussian/Rademacher 随机矩阵；MMV 采用相同测量矩阵；Onsager 是 Jacobian **矩阵**的和，SE 跟踪完整误差协方差。独立测量矩阵的 DCS 才有不同的对角化简化。
- §III-A–C / p4，Algorithm 2、Theorem 1、(12)–(16)：可联合对角化信号和噪声，但必须同步变换先验、MMSE 估计器和导数。一般先验不保证后续噪声协方差保持对角；BG 是特殊情况。
- 正文明确提醒早期引用 [18] 的 Onsager 项有错误；实现时应从明确矩阵约定推导，不能照抄含混的标量式。

### M4 — Kunde et al.：复数、非可分去噪的矩阵修正

Vishnu Teja Kunde, Alessandro Mirri, Jean-Francois Chamberland, Enrico Paolini, **Complex Approximate Message Passing with Non-separable Denoising**, 2026 预印本；[arXiv:2604.21115v1](https://arxiv.org/pdf/2604.21115v1)，2026-04-22 提交。

- §III-B / p9，Assumption 8(A1)–(A4)：i.i.d. `CN(0,1/n)` 矩阵、统一 Lipschitz 等正则性及大系统极限。
- §III-C / p12，(18)–(21)、Proposition 13、Remark 14：多特征情况下 Onsager 为 `p×p` 矩阵，由 Wirtinger Jacobian 的对应对角块求和；状态也成为矩阵。推导在 Appendix B，pp24–27。
- §VI / p17：作者明确将 structured sensing operators、partial DFT、OTFS 的理论扩展列为未来工作。
- 因此“非可分神经网络不能用于 AMP”过强；但正确复数全映射导数也不能消除固定 AFDM 算子不满足上述假设的问题。

### M5 — Djelouat et al.：EP 保留协方差，EM 估计相关先验

Hamza Djelouat, Mikko J. Sillanpää, Markus Leinonen, Markku Juntti, **Hierarchical MTC User Activity Detection and Channel Estimation with Unknown Spatial Covariance**, IEEE TWC 23(10), 14620–14636, 2024，DOI 10.1109/TWC.2024.3417612；以下公式按 [2023 预印本](https://arxiv.org/pdf/2310.10204v1)，出版信息由 [Oulu 学术库](https://oulu.cris.fi/en/publications/ec03d69b-60de-4b93-aa77-4ed2852b3148)核查。

- §II-C / pp8–9，(2)–(4)：层次活动先验及逆 Wishart 协方差先验。
- §III-B / pp13–14，(17)–(22)：先除去自身近似因子形成 cavity distribution，再用完整协方差计算活动权重、均值和中心协方差，最后更新 Gaussian site。
- §III-C / pp14–15，(26)–(28)：EM 使用后验二阶矩估计先验协方差；为防止逐用户估计过拟合，共享簇内协方差。§III-D / p16 还讨论非正定 site 与剪枝。
- 这是结构先验 + 协方差推断路线，并未提供固定预训练 AWGN 网络的消息白化保证。其簇先验、协方差先验信息和剪枝行为不能无条件迁移到当前弱用户任务。

## 2. 对本项目的推断，而非论文已验证结论

1. **应首先区分目标。** 如果坚持三网络冻结且只接收标量噪声级，目标确实须是原坐标下 `x+CN(0,vI)` 的近似输入。上述 MMV 文献更一般的目标是 `x+CN(0,Σ)`，同时让非线性模块适配 `Σ`；它们不能被引用为“仅修线性模块即可保留现有网络”的保证。

2. **标量 MSE 校准不够。** 将 M2 的活动概率改写为统一记号：

   `logit p_i = logit ε - log det(I + Σ^{-1}R_i) + r_i^H[Σ^{-1}-(Σ+R_i)^{-1}]r_i`。

   即使两个误差协方差的迹相同，方向权重也可不同。但是该公式仍以零均值、独立高斯有效噪声和 Gaussian 活跃先验为前提；本项目查询的信号方向衰减不能仅靠替换 `Σ` 保证修复。也不建议把本式直接替换冻结学习分类器。

3. **全映射与矩阵统计是不同于“再试一个标量散度”的问题。** 当前输出均值含 `F(r)=p(r)μ(r)`，导数必须包含 `p Dμ + μ Dp`。若采用 MMV 矩阵框架，还须按明确特征维度处理相应 Jacobian 块，不能把一个实标量平均散度称作矩阵正交化。本项目已有全映射标量散度小试验的负结果，意味着此处需要审查结构和理论差异，不能把同一方案换名重试。

4. **直接估计 256×256 协方差有样本问题。** 对一场景的 `16×256` 原始残差按 16 行形成样本二阶矩，其秩至多 16（去均值至多 15）。所以完整协方差不能靠裸样本矩阵稳定得到；需要物理结构、跨场景统计或有依据的收缩/参数化。后者是候选设计选择，不是已由本次文献证明的修复。

5. **不要从已知信道协方差跳到已知误差协方差。** 物理先验 `R_i`、非线性模块后验中心协方差、残余多用户干扰协方差、线性输出有效噪声协方差是四个对象。当前第二网络估计的条件 MSE 也不能自动当成任一完整矩阵。推荐后续候选先明确每一对象如何获得、近似了什么，再评估是否改善查询均值增益、空间相关及活动判决。

6. **矩阵规模和算子条件仍是主要边界。** 将同一个 `16×640` 块重复 256 次不等于获得全空间的独立随机混合；M1/M3/M4 的大系统随机矩阵结论不能因此直接套用。本轮未发现覆盖这一固定 AFDM 算子、现有非可分冻结三网络及现有 damping 的现成性能定理。

## 3. 未作为已核实机制的线索

Cheng, Liu, Ping, *Orthogonal AMP for Massive Access in Channels with Spatial and Temporal Correlations*（JSAC 2021）的 [CityU 官方摘要](https://scholars.cityu.edu.hk/en/publications/orthogonal-amp-for-massive-access-in-channels-with-spatial-and-te/)确认提出 OAMP-MMV、group Gram–Schmidt orthogonalization，比较 Hadamard pilots 和相关信道；本分工未获得该 2021 正文，不补造公式/页码。后续可由同团队的 2023 MMV/MT 原文核查具体机制，已交由另一分工处理。
