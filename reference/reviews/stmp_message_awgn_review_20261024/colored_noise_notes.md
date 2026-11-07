# 结构化观测与有色去噪误差：一手文献核验

核验日期：2026-10-24。范围为针对 STMP 的技术性叙述调研；不宣称系统综述或穷尽检索。未运行训练或接收机实验。下列页码均为所链接 arXiv PDF 的物理页码，从 1 开始；HTML 文献用章节、公式、算法行定位。

## 1. D-Turbo-CS：通用去噪器的外信息，以及相关信号下的反例

**Zhipeng Xue, Junjie Ma, Xiaojun Yuan (2017), “Denoising-based Turbo Compressed Sensing.”** [作者稿 v1](https://arxiv.org/pdf/1703.08756v1)

- 核验位置：§III-A，PDF p.3 最后段；§III-B，p.4，式(13)–(21)；§V-B/C，pp.7–9，式(53)–(54)，Figs.3–8。
- 原文区分 MMSE 去噪器与通用去噪器；更换为通用去噪器后，不能直接沿用原 MMSE 外信息公式。其构造是 `D_ext(r)=c[D(r)−αr]`，其中 α 用平均散度估计；推导使用输入的独立 Gaussian 模型和大维度平均近似。
- 重要反例：partial DCT 测量对相关图像时，误差非零均值、非 Gaussian，MSE evolution 与仿真不一致；把**实际测量矩阵**从 `A₁=SW` 改为 `A₂=SWΘ`，Θ 为随机 ±1 对角矩阵后，实验显示匹配改善。
- 网络权重可保留；但相关信号的正面证据同时改变了测量算子。不能据此声称当前 AFDM 固定算子只加一个散度项就能恢复 AWGN，也不能把接收端纯重参数化等同于实际发射测量随机化。

## 2. VDAMP：把标量误差模型改为分组有色模型

**Charles Millard, Aaron T. Hess, Boris Mailhé, Jared Tanner (2020), “Approximate Message Passing with a Colored Aliasing Model for Variable Density Fourier Sampled Images.”** [作者稿 v3](https://arxiv.org/pdf/2003.02701v3)

- 核验位置：§I-B/C，PDF pp.2–3；式(9)–(10)、Algorithm 2（p.3）；§III-E，pp.8–9。
- 面向独立 Bernoulli 变密度 Fourier 点采样，以小波子带表示误差；每个子带有自己的方差、散度修正和去噪参数，使用密度补偿。
- 得到的模型是变换域各子带内白 Gaussian、子带间方差不同，回到原信号域通常仍有色。其 “colored state evolution” 证据是经验结果，并非任意结构化算子的普适定理。
- 对项目的启示是保留具有物理意义的误差方向/分组；论文没有证明简单“逐用户一个标量”足够，更未证明重复的 16×640 AFDM 用户块具备 Fourier–小波的解耦结构。

## 3. D-VDAMP：明确重训能接收有色噪声条件的网络

**Christopher A. Metzler, Gordon Wetzstein (2020), “D-VDAMP: Denoising-based Approximate Message Passing for Compressive MRI.”** [作者稿 v1 全文](https://arxiv.org/html/2010.13211v1)

- 核验位置：§2 Algorithm 1，lines 4–11；§2.2 Finding 1；§2.3。
- 保留 VDAMP 的有色模型，以每个小波子带的噪声标准差作为 CNN 各层的额外通道，并用合成有色 Gaussian 噪声训练网络。原始 AWGN 网络权重不能视为直接兼容。
- §2.2 明确指出其方差预测依赖实际残差，弱于封闭的 AMP state evolution，不能据此分析收敛/噪声敏感性。Algorithm 1 在预测误差增大时提前停止；密度补偿会增强测量噪声影响。
- 这提供了第三种选择：独立训练可处理参数化 Gaussian 协方差的模块，无须端到端展开或收集某一固定迭代轨迹。但它不再是“完全冻结现有三个 AWGN 网络”的路线。

## 4. D-GEC / corr+corr：在保持原信号坐标的网络中显式传递协方差信息

**Saurav K. Shastri, Rizwan Ahmad, Christopher A. Metzler, Philip Schniter (2022 作者稿), “Denoising Generalized Expectation-Consistent Approximation for MR Image Recovery.”** [作者稿 v2](https://arxiv.org/pdf/2206.05049v2)

- 核验位置：§III-A，PDF pp.11–14，式(28)–(36)、Algorithms 2–3；§III-B，pp.15–16，式(38)–(41)；§V，pp.27–28。
- 式(28)写出 `e₂=VDVᴴe₁+u`；`tr(D)=0` 对非旋转不变矩阵并不足以保证白 Gaussian。其方案在小波子带分组计算精度及平均 Jacobian。
- 原坐标下去噪输入为 `x+n`，噪声协方差已知且有色。corr+corr 向网络额外提供独立、同协方差噪声样本，以合成有色 Gaussian 数据重训；没有直接对信号做白化。
- 式(36)后的文字明确说 Gaussian 行为获得实验支持，严格分析仍待研究；因此不能将其转述成已证明的 AFDM 解耦定理。可借鉴协方差参数化与完整分组 Jacobian，但冻结原网络的承诺需要改变。

## 5. DD-VAMP：改善稳定性，不能等同于恢复 AWGN 分布

**Subrata Sarkar, Rizwan Ahmad, Philip Schniter (2020), “MRI Image Recovery using Damped Denoising Vector AMP.”** [作者稿 v1](https://arxiv.org/pdf/2010.11321v1)

- 核验位置：§2.4，PDF p.2；§3.1–3.2，pp.3–4，Algorithm 1、式(13)–(14)；§4，p.4。
- 对非 ROI 的 Cartesian Fourier 观测，保留现有 DnCNN，阻尼消息均值、精度及 Monte Carlo Jacobian；方差型量先转成幅度再阻尼，并用 ADMM-PR 初始化加快迭代。
- 研究目标和验证是恢复准确度、稳定性及速度；正文的强凸收敛依据只覆盖所引双循环特例，不能直接推广到任意神经去噪器。
- 当前低 SNR STMP 几乎全收敛，因此“再调阻尼”缺少直指漏检原因的证据。可作为数值对照，不能仅凭收敛宣布 query 已符合 AWGN。

## 6. FIRE / DDfire：保留预训练 AWGN 网络，主动补入有色 Gaussian 噪声

**Matthew C. Bendel, Saurav K. Shastri, Rizwan Ahmad, Philip Schniter (TMLR 2025), “Solving Inverse Problems using Diffusion with Iterative Colored Renoising.”** [最终作者稿 v4](https://arxiv.org/html/2501.17468v4)，[期刊版本入口](https://openreview.net/forum?id=RZv8FcQDPW)

- 核验位置：§3.1，式(8)–(21)、Theorem 1、Algorithm 1 line 7；§4.1 Table 1；Appendix E。
- 在线性 Gaussian 工作模型下，线性更新误差协方差为 `C=(AᵀA/σ_y²+I/ν)⁻¹`，随后添加独立噪声，协方差 `Σ=σ²I−C`。Algorithm 1 使用 `σ²←max{σ²/ρ,ν}` 保证 Σ 半正定；可用 SVD 或算子近似生成补噪。
- Theorem 1 假定每次去噪输出误差已是白 Gaussian、方差已知且小于输入方差，并独立于测量噪声。正文承认这一假设实际可能不满足；额外 stochastic denoising 可减弱结构却损失 SNR。线性成像实验默认没有这一额外步骤。
- 这是冻结 AWGN 网络的真实文献路线，但补噪不能消除均值偏差或证明与信号独立；论文成像效果不保证 AFDM 活跃检测收益。

## 对本项目的综合判断（以下为推断，不是论文结论）

1. 需要区分四个目标：降低算法振荡；消除输入输出误差相关；使误差为可预测 Gaussian；进一步使其白且与信号独立。不同论文只解决其中部分，不能互换。
2. 重复 MMV 算子不会仅因总维度大而自动拥有 Haar 右奇异向量。空间方向共享造成的多用户干扰也不会因 trace 归一化自动消失。
3. 对 `r=x+e` 直接乘白化矩阵会把目标改成 `Wx`。D-GEC 的做法是让网络知道原坐标里的有色噪声；FIRE 的做法是补噪而不变换 x；这两者应与直接白化严格区分。
4. 一般补噪若要把真实协方差 C 变成 τI，必须满足 τ≥λ_max(C)。最小新噪声平均功率是 `λ_max(C)−tr(C)/d`。这是线性代数推导；若 C 高度各向异性，损失可大。已有项目 oracle noise-filling 的 7–11 dB 增益损失及超支持范围，应约束 FIRE 类候选，不应因找到新论文而重复宣称其必然可行。
5. FIRE 采用各向同性去噪输出工作模型时，在当前欠定矩阵的零空间有 λ(C)=ν；其 PSD 门限合理，但若真实去噪误差具有结构、偏差或噪声复用相关，模型 C 可能严重低估某些方向。应先检验协方差模型而不是把观测残差功率当成足够验证。
6. 若坚持冻结网络和固定导频，优先研究实际外信息/协方差与历史相关是否被正确表示，并用合成 AWGN 对照验证每个改动；不要仅优化平均 NMSE。若这些限制排除了有效白化，独立的有色 Gaussian 条件网络是一条有文献支持的模块化路线，与十层端到端展开仍有清楚区别。

## 检索范围与审计

使用公开一手 arXiv、作者全文及 OpenReview/期刊记录，检索组合包括 D-GEC/corr+corr、D-VDAMP/VDAMP、D-Turbo-CS、structured measurements、pre-trained colored-noise denoiser、2024–2026 follow-up。本轮最晚纳入核心工作为 2025 FIRE；未将检索结果页面的 crawl 时间误认为论文年份。未以综述网站的自动摘要支持技术断言。原文的公式、算法、理论假设和实验段落已经分别核验。
