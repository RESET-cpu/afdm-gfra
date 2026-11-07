# Memory AMP 与 OAMP-MMV 文献核验笔记

日期：2026-10-24。范围：冻结 AWGN 网络时，对跨轮相关、MMV 列相关、非单位增益消息的处理。未运行实验。下列页码均指指定 arXiv PDF 从 1 开始计数，不能直接套用期刊页码。5 篇阅读全文相关部分，另 1 篇只核验作者机构摘要，明确标识。

## 1. Memory AMP

Lei Liu, Shunqi Huang, Brian M. Kurkoski. **Memory AMP**. IEEE Transactions on Information Theory, 68(12):8015–8039, 2022. 全文版本：[arXiv:2012.10861v7](https://arxiv.org/pdf/2012.10861v7)，2022-06-23。

**原文证据。** §II-B，PDF p.4，Assumptions 1–2：零均值 IID 信号；大系统固定测量比；右酉不变测量矩阵，右奇异向量 Haar 分布。§III-A，pp.6–7，Eqs.(18)–(24)、Lemma 4：有记忆的迭代须让当前输出误差与此前各输入误差正交，逐步输入/输出正交一般不够。其高斯性结论还要求可分且 Lipschitz 连续的非线性处理器。BO-MAMP 用长记忆匹配滤波降低线性模块成本。§V-D，p.13，Eq.(71) 给有限阻尼窗口实现，不能把它理解成任意固定矩阵的高斯化保证。

**本项目推断。** 双向阻尼已经引入历史信息，值得检查跨轮误差内积；但重复的 16×640 AFDM 算子与耦合 CNN 不符合上述标量定理的直接条件。MAMP 的主要计算动机是替代昂贵 LMMSE，而本项目行维度只有 16，因此不宜只为“有记忆”整体换算法。

## 2. Sufficient-Statistic Memory AMP

Lei Liu, Shunqi Huang, Yuzhi Yang, Zhaoyang Zhang, Brian M. Kurkoski. **Sufficient-Statistic Memory AMP**. [arXiv:2112.15327v4](https://arxiv.org/pdf/2112.15327v4)，2023-06-30；初稿 2021。此次只按已核验预印本引用，不宣称已核验期刊接收。不要与三作者 ISIT 2022 短文 arXiv:2206.11674 混为同一版本。

**原文证据。** §IV-A，PDF p.8，Lemma 11 / Eq.(40)：对具有已知联合高斯误差协方差 V 的多个单位增益观测，权重 ζ=V⁻¹1/(1ᵀV⁻¹1) 形成充分统计量。§V-B，pp.10–11，Theorem 1 / Eqs.(62)–(65)：在 MAMP 正交性与原有假设下，以跨轮协方差选择阻尼，保持正交性并得到收敛的状态演化。§VI，p.13，Remark 6 明确说明有限维时其严格结论不成立，阻尼仍可能有效。

**本项目推断。** 可借鉴的是“均值融合应配套跨轮协方差”，并非直接引用其收敛定理。用真值估计 V 只能作为 oracle 诊断；部署必须从接收量、可验证模型或独立校准估计。若估计偏差大，逆协方差权重可能放大误差。

## 3. OAMP-MMV / OAMP-MT

Yiyao Cheng, Lei Liu, Shansuo Liang, Jonathan H. Manton, Li Ping. **Orthogonal AMP for Problems With Multiple Measurement Vectors and/or Multiple Transforms**. IEEE Transactions on Signal Processing, 71:4423–4440, 2023, DOI [10.1109/TSP.2023.3327609](https://doi.org/10.1109/TSP.2023.3327609)。核验全文为较早的 [arXiv:2304.08038v1](https://arxiv.org/pdf/2304.08038v1)，14 页，故以下公式号限此版本。

**原文证据。** §III-B，PDF p.5，Eqs.(15)–(18) 使用矩阵消息模型 X̂=XΘ+Z，保存列间协方差 Σ。§III-D，p.5，Assumption 18 / Theorem 19 要求 Haar 变换及与之独立的 PIID-separable 局部处理器，给出列方向渐近高斯、行内联合高斯结论。§III-E–F，p.6，Eqs.(28)–(34) 的状态演化与 Gram–Schmidt 正交化均为矩阵形式；Eq.(34) 的修正量是矩阵 Δ，而非单个平均散度。§IV-E，p.8，Assumption 24 要求多个变换独立 Haar。

**本项目推断。** 这支持先审计“矩阵增益与相关误差是否被标量化丢失”。它不保证天线方向误差协方差变成 vI，更不保证固定 AFDM 上所有元素独立 AWGN；即使实现矩阵 GSO，冻结标量 AWGN 网络仍可能面临有色输入。全 256×256 矩阵修正需要可靠估计和足够样本，不建议直接以稀疏单场景经验矩阵求逆。可先按物理相关结构考察较小分组，作为候选近似而非论文原算法。

## 4. 用积分/Monte Carlo 构造正交化，而不训练网络

Lei Liu, Yiyao Cheng, Shansuo Liang, Jonathan H. Manton, Li Ping. **On OAMP: Impact of the Orthogonal Principle**. IEEE Transactions on Communications, 71(5):2992–3007, 2023, DOI [10.1109/TCOMM.2023.3262304](https://doi.org/10.1109/TCOMM.2023.3262304)。全文核验版本标题为 **On Orthogonal Approximate Message Passing**，[arXiv:2203.00224v2](https://arxiv.org/pdf/2203.00224v2)，2023-01-13。

**原文证据。** §IV-A，PDF p.7，Eqs.(27)–(29) 通过输入误差与黑盒输出的相关矩构造 GSO。§IV-C，p.8，Eq.(30) 讨论已知信号先验下的积分/Monte Carlo 计算，可离线制表。§IV-D，Eqs.(31)–(34) 才转为可分可微函数的导数形式。§I-D，p.2 明确其 Haar 系综平均分析不自动适用于每个固定变换；文中还以单位变换说明这一限制。

**本项目推断。** 合成信道先验可采样，因此能在冻结完整映射 F(r)=p(r)μ(r) 下测量正交化系数，无须微调 CNN。这是估计实现的替代方式，不是新的高斯化原理；原项目已有完整映射散度负结果，不能把换成 Monte Carlo 计算包装成已解决问题。更有价值的是对照标量与分组相关矩是否存在实质差异。

## 5. 直接面向相关 massive access 的先例（本轮仅摘要核验）

Yiyao Cheng, Lei Liu, Li Ping. **Orthogonal AMP for Massive Access in Channels With Spatial and Temporal Correlations**. IEEE Journal on Selected Areas in Communications, 39(3):726–740, 2021；在线 2020-08-24，DOI [10.1109/JSAC.2020.3018799](https://doi.org/10.1109/JSAC.2020.3018799)。已核验[作者机构记录](https://scholars.cityu.edu.hk/en/publications/orthogonal-amp-for-massive-access-in-channels-with-spatial-and-te/)。

**已核实范围。** 摘要明确：将相关信道 JACE 建模为 MMV；提出 OAMP-MMV 及 group Gram–Schmidt orthogonalization；以数值结果核验状态演化；对 Hadamard pilots 比较 AMP-MMV，并与 GTurbo-MMV 比较相关信道性能。未取得可读全文，因此不为该文编写公式号、协方差细节或定理假设。2023 MMV 全文能支撑上面的数学讨论，不能倒推成已读这篇 2021 正文。

## 6. 长记忆 OAMP 的协方差追踪，以及有限维负结果

Keigo Takeuchi. **On the Convergence of Orthogonal/Vector AMP: Long-Memory Message-Passing Strategy**. 核验全文 [arXiv:2111.05522v2](https://arxiv.org/pdf/2111.05522v2)，2022-04-22；初稿 2021。

**原文证据。** §III-C，PDF p.6，Eqs.(27)–(28)：阻尼均值与跨轮协方差一起传播；§III-D，p.7，Eqs.(44)–(45) 给另一方向对应关系。§IV-B，pp.9–10，Example 2 / Eqs.(63)–(78) 明确比较正确协方差递推与启发式方差阻尼。§IV-A，pp.7–8，Assumptions 1–5 仍有 IID 信号、右正交不变矩阵、Lipschitz 标量去噪器等条件。§I-B，p.2 及 §VI 明确报告有限维负结果：长记忆方案比普通 OAMP 更需要大系统，较小系统上可能弱于启发式阻尼。

**本项目推断。** 这直接反对“理论上更精确的方差更新必然修复低 SNR”的推断；历史 temporal 20261015 已审计阻尼恒等式，应先复核已有记录，避免重复当作新问题。

## 对当前实现的具体审计切入点（已有方向的复核，不是新 bug）

`src/algorithm/STMP/iterations.py:18–25` 中 `moment_damp` 对均值和协方差分别线性插值。若两次查询均有单位增益 r_old=x+e_old、r_new=x+e_new，则 r_d=(1−λ)r_old+λr_new 的真实平均误差功率为

\[
v_d=(1-\lambda)^2v_{old}+\lambda^2v_{new}
+2\lambda(1-\lambda)\operatorname{Re}c_{old,new},
\quad c_{old,new}=\mathbb E[e_{old}^{H}e_{new}]/d.
\]

它一般不等于当前插值标签 `(1−λ)v_old+λv_new`。这是此前 temporal 20261015 已涉及的代数审计方向，不是新发现的 bug：参数阻尼本来可作为启发式算法；若原标签本身不是误差功率，不能直接代入；在两次查询一致的收敛处差异也消失。既有诊断中选定漏检用户最终 MSE/v 中位数约 0.995，均匀样本终态去噪性能也良好，因此不能把最终漏检归咎于这一个公式。

建议优先做已有轨迹可支持的比较：查询增益、天线误差协方差、跨轮误差协方差、完整映射输入/输出误差相关。只有发现明显跨轮失配并能构造无需真值的估计器，才值得独立实现有限窗口协方差阻尼。MAMP、SS-MAMP、OAMP-MMV 均不构成在当前固定算子上“保持网络不动就能保证独立 AWGN”的证明。
