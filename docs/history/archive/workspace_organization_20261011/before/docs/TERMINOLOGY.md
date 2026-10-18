# 主线术语依据

## 2026-10-11：常模导频与整数网格下的等价计算

| 原词或忠实译名 | 原文定位 | 当前使用范围 |
|---|---|---|
| affine Fourier domain / 仿射傅里叶域；delay-Doppler grid / 时延–Doppler网格 | [Ding接受稿](../paper/literature/ding2026.pdf)，§II–III-A式(1)–(9)；[Bemani作者稿](https://arxiv.org/html/2204.12798v2)，§III–IV的整数时延/Doppler响应 | 当前整数采样时延和整数倍子载波间隔Doppler下，AFDM原子为带相位的置换矩阵。结合项目partial DFT导频每元素模相同，单位范数字典满足|A_lg|²=1/L；这是本字典的代数性质，不将连续真实信道假设为on-grid |
| vector-valued variable nodes / 向量变量节点；covariance / 协方差 | [HyGAMP](https://arxiv.org/html/1111.2581v4#S5)，§V Algorithm 2式(28)–(38) | 将同一向量消息递推中的均匀元素平方模代入，合并共同输出/输入协方差，仅求后验协方差之和。保留BG后验与EM全部更新，不另造算法名；不是近似对角化或降低天线数量 |

[化简实现](../src/afdm_jadcedd/algorithm/baselines/em_gamp_spatial_uniform.py)由当前已明示的空间/MMV适配继续化简；[三项独立测试](../tests/test_em_spatial_uniform.py)及[六个开发条件](../results/baseline_scenario_audit_20261011/em_spatial_uniform_equivalence/RESULTS.json)核对等价性。当前性能范围固定−4～6 dB，实际结果见[100场景报告](../results/baseline_scenario_audit_20261011/em_snr_m4_p6_hundred/REPORT.md)。不将代数化简、零失败或有限预算结果包装为收敛证明。

## 2026-10-11：EM空间/MMV候选运行入口

| 原词或忠实译名 | 原文定位 | 当前使用范围 |
|---|---|---|
| Bernoulli–Gaussian / Bernoulli–Gaussian分布；EM update / EM更新 | [Zhao全文](../references/zhao2025_mixed_fronthaul_jadce.pdf)，Algorithm 1、式(29)–(30)、(36)、(38)–(39)、(49)；[Djelouat](https://arxiv.org/html/2112.04295)，式(9)–(10) | 新接收机每网格行共享支持及beta_g R slab，方差更新tr[R^-1(C_active+m_active m_activeᴴ)]/M，行支持概率平均更新稀疏率。局部模型下直接推导，不称为Zhao独立标量更新原样实现 |
| vector-valued variable nodes / 向量变量节点；covariance / 协方差 | [HyGAMP](https://arxiv.org/html/1111.2581v4#S5)，§V Algorithm 2式(28)–(38) | 新运行入口按复数A_lg I弱边传播完整矩阵，不使用此前固定E诊断的阻尼。先验坐标变换也完整变换噪声矩阵；不宣称结构化AFDM的状态演化已成立 |
| Gamma prior / Gamma先验；maximum a posteriori / 最大后验 | [Zhang全文](../references/zhang2023_gamp_sbl_grant_free_noma.pdf)，式(3)–(4)、(18)–(19)；Zhao式(49) | 新候选仍逐列学习噪声，公开噪声只设定精度先验shape=1+L、rate=Lσ²_public。这是明示MAP适配，不称为固定噪声或Zhao原生ML更新；先验强度零与M=1的原Zhao退化已核对 |
| log-likelihood ratio / 对数似然比；effective noise / 有效噪声 | [Djelouat](https://arxiv.org/html/2112.04295)，式(9)–(10)、(13)；[Liu–Yu](https://arxiv.org/html/1706.06438v2)，式(18)–(19)、Definition 1；Zhao式(51)–(55) | 新主判决使用伪观测r与同一E步参数，Gaussian零门限；后验均值Gaussian读出另存诊断。它改变了Zhao原读出输入，明确标为AFDM适配，不混称原文复现 |

代码与运行入口见[当前实现说明](BASELINE_RUNTIME_ADAPTATIONS.md)，开发配对结果见[报告](../results/baseline_scenario_audit_20261011/em_spatial_runtime_candidate/REPORT.md)。

## 2026-10-11：空间相关信道的BG先验控制

| 原词或忠实译名 | 原文定位 | 当前使用范围 |
|---|---|---|
| spatially correlated channels / 空间相关信道；channel covariance matrix / 信道协方差矩阵 | [Djelouat等作者稿](https://arxiv.org/html/2112.04295)，§II-A式(1)、§III式(9)–(11) | 区分βI与一般Gaussian slab协方差，以及信道先验与消息误差协方差。该文用户协方差已知；当前开发控制从公开导频二阶矩初始化一个共享相关矩阵，不输入真实用户方向，不归称为其原文协方差估计器 |
| MMSE-based denoiser / 基于MMSE的去噪器；Gaussian-Bernoulli distribution / Gaussian–Bernoulli分布 | 同文式(3)、(9)–(10)；[Zhao](../references/zhao2025_mixed_fronthaul_jadce.pdf)，式(3)、(29)–(30) | 在明示β_g R先验下用完整矩阵计算活动Gaussian后验，再混合零分量。阵元坐标的可逆线性变换把该模型及噪声同时转换到已核对的β_g I核；这一步是项目适配，不称为Zhao原Algorithm 1或其已证明的状态演化 |
| covariance / 协方差；array response / 阵列响应 | Djelouat同文式(1)；[Mao等](https://arxiv.org/html/2504.04686v2)，§II-A式(1)–(3) | 独立候选位置只用于E[a aᴴ]的阵列二阶矩诊断。不同波束平均不能等同当前用户/网格/公开相位的条件协方差；单波束矩阵只作诊断，不作为已知真值先验 |

证据见[独立阵列诊断](../results/baseline_scenario_audit_20261011/spatial_prior_covariance_audit/REPORT.md)及[相关slab固定E计划](../results/baseline_scenario_audit_20261011/em_spatial_covariance_fixed_e_probe/PLAN.json)。正半定投影、相关矩阵归一化和固定0.05单位阵收缩是明示的数值初始化操作，不归称为参考论文已公开的实现规则。

## 2026-10-11：Gaussian读出与完整协方差的固定E检查

| 原词或忠实译名 | 原文定位 | 当前使用范围 |
|---|---|---|
| posterior mean / 后验均值；log-likelihood ratio / 对数似然比 | [Zhao](../references/zhao2025_mixed_fronthaul_jadce.pdf)，式(23)–(24)、(29)–(30)、(51)–(55)；[Liu–Yu](https://arxiv.org/html/1706.06438v2)，式(18)–(19)、(26)–(27)、Definition 1 | 独立核对伪观测r与BG均值μ的密度配对。变量变换与收缩二次型关系由明确固定参数模型直接推导；不宣称实际AFDM状态演化成立，不自动更换Zhao主判决 |
| covariance / 协方差；effective noise / 有效噪声 | 同上Zhao式(52)–(55)、Liu–Yu式(18)及Theorem 1之后的多天线独立误差讨论 | 已保存终态中r/√φ的协方差只作真值标注的事后诊断。不能把空间相关性、网格失配及参数学习的混合影响分别归因，也不向接收机提供真实非活跃集合或经验协方差 |
| vector-valued variable nodes / 向量变量节点；weak edges / 弱边 | [Hybrid Approximate Message Passing作者稿](https://arxiv.org/html/1111.2581v4#S5)，§V Algorithm 2式(28)–(38) | 新固定E控制把每个网格行视为多天线复向量，完整协方差通过A_lg I块传播，并按proper complex Gaussian矩改写；是明确向量适配，不称为Zhao标量核原样实现或VAMP |
| adaptively damped GAMP / 自适应阻尼GAMP；Bethe free energy / Bethe自由能 | [Vila等作者稿](https://arxiv.org/html/1412.2005v1)，Table1 R1–R18、§2.2式(3)–(10) | 将原标量方差改为完整矩阵消息，复数AWGN成本与矩匹配另作恒等式核对；最低步长允许成本上升的分支计数保留。固定参数控制不意味着完整EM已稳定或原论文采用该矩阵扩展 |

证据见[Gaussian读出核对](../results/baseline_scenario_audit_20261011/em_gaussian_readout_consistency_audit/REPORT.md)、[伪误差协方差诊断](../results/baseline_scenario_audit_20261011/em_pseudo_noise_covariance_audit/REPORT.md)及[完整协方差固定E计划](../results/baseline_scenario_audit_20261011/em_full_covariance_adgamp_e_probe/PLAN.json)。

## 2026-10-11：学习参数冻结后的GAMP诊断

| 原词或忠实译名 | 原文定位 | 当前使用范围 |
|---|---|---|
| fixed points / 不动点；sum-product GAMP / 和积GAMP | [Rangan等作者稿](https://arxiv.org/html/1402.3210v3)，§I、§II-A式(6)、Algorithm 1 | 检查固定β、λ、噪声时原BG消息迭代是否满足均值、消息、方差更新的不动点；输出有限或均值范数有界不等于已经收敛 |
| GAMP with vector stepsizes and damping / 带向量步长和阻尼的GAMP | 同文Algorithm 1第9、12、13行、§II-B | 独立诊断只松弛均值和输出消息，方差更新不松弛；复数及消息符号使用当前Zhao坐标，阻尼0.2是事前指定的项目控制。不是原生Zhao Algorithm 1，不以Gaussian先验的收敛结论保证BG或EM收敛 |
| adaptively damped GAMP（AD-GAMP）/ 自适应阻尼GAMP；Bethe free energy / Bethe自由能 | [Vila等作者稿](https://arxiv.org/html/1412.2005v1)，Table1 R1–R18、§2.2式(3)–(10) | 新固定参数控制按成本调整步长，同时松弛消息、精度和相关方差。复数KL与AWGN矩匹配为明示转换，经独立推导核对；最小步长允许成本上升的R13分支次数保留。不是Zhao原算法，不作BG或完整EM的收敛保证 |
| expectation-maximization / 期望最大化；EM-GM-AMP | [Vila–Schniter作者稿](https://arxiv.org/html/1207.3107v3#S3.SS5)，TableII、作者PDF p.7；[Zhao](../references/zhao2025_mixed_fronthaul_jadce.pdf)，pp.4123–4126式(36)、(38)–(39)、(49)、Algorithm1 | 开发控制采用外层参数学习、内层固定参数GAMP，内层改用明示AD-GAMP并要求原1e−6不动点标准后才执行Zhao的M更新。这是项目收敛适配，不是Zhao每轮一E/M的逐字复现；Vila的GM均值学习、具体预算不归称为此控制的设置 |
| Gamma prior / Gamma先验；maximum a posteriori / 最大后验 | [Zhang 2023](../references/zhang2023_gamp_sbl_grant_free_noma.pdf)，pp.15058–15059式(3)–(4)、(18)–(19)；[Zhao](../references/zhao2025_mixed_fronthaul_jadce.pdf)，式(49) | 分离E/M控制对每个阵元分别学习噪声。复数AWGN的样本计数为L，与原实数推导的L/2区分；shape=1+L、rate=Lσ²_public是项目先验，得到(σ²_ML,m+σ²_public)/2。不是固定噪声、公共噪声或Zhao原生ML更新 |
| EM update / EM更新 | [Zhao](../references/zhao2025_mixed_fronthaul_jadce.pdf)，p.4124式(38)–(39)；[Mao等作者稿](https://arxiv.org/html/2504.04686v2)，§II-A式(1)–(3)的阵列响应 | 将同一Q函数限制为一个网格行的β在各阵元相等，得到β_g=Σ_mπ_gm(|μ_active,gm|²+v_active,gm)/Σ_mπ_gm。依据是当前同方向阵列响应各元素模相同；这是明示参数约束，不是原Zhao逐项方差更新，也不等于完整空间相关先验。总权重为零时保留此前β |

证据见[学习参数冻结报告](../results/baseline_scenario_audit_20261011/em_learned_parameter_stability_probe/REPORT.md)。BG后验方差/伪观测方差用于描述后验对伪观测的敏感性；复数归一化散度恒等式在独立有限差分控制中核对，不作为新的方法名称。

## 2026-10-11：baseline 场景诊断中的公式依据

| 原词或忠实译名 | 原文定位 | 当前使用范围 |
|---|---|---|
| least squares / 最小二乘 | Tropp，SOMP Algorithm 3.1 的限制支持最小二乘步骤；Ding p.2 式(8)–(9)的网格表示；Huang pp.2950–2951 式(5)–(6)的完整有效信道 | 对真实 H 独立计算网格子空间的最小二乘投影残差，仅作明确标注的真值诊断；不是恢复算法成绩，不证明稀疏恢复可达到该误差 |
| dual sparsity structure / 双重稀疏结构；spike-and-slab prior / 尖峰与厚尾先验 | [Ding 接受稿](../paper/literature/ding2026.pdf)，p.3 式(9)后的说明、式(10)；[Liu–Yu 作者稿](https://arxiv.org/html/1706.06438)，§III-C 式(19)–(22) | 用户活动与用户内部网格占用分开描述；新诊断中的 p、ρ 两层 Bernoulli 条件模型及全局 slab 方差是明确项目适配，不能称为 Zhao 原算法或 Ding 原先验的逐字复现 |
| Gamma prior / Gamma 先验；MAP update / MAP 更新 | [Zhang 2023](../references/zhang2023_gamp_sbl_grant_free_noma.pdf)，pp.15058–15059 式(3)–(4)、(16)、(18)–(19) | 用 shape=1+L、rate=Lσ² 的公开噪声精度先验检查噪声学习；参数取值为项目诊断，方差仍逐轮学习。应用到 Zhao 核心属于新增 MAP 适配，不称为其原生 ML-EM 更新 |
| damping / 阻尼 | [Rangan–Schniter–Fletcher–Sarkar 作者稿](https://arxiv.org/html/1402.3210v3)，Algorithm 1 第8–13行、§II-B | 分别检查均值与输出消息插值，成对后验矩用于参数学习；新共享 BG/EM 控制没有得到该文 Gaussian 固定参数的收敛保证，已失败的尝试不提升为正式 baseline |
| decision threshold / 判决门限 | Ding p.4 式(27) | 80 用户、20 独立物理种子与六 SNR 的一个跨 SNR 门限校准；判决公式和 >= 保留。数值门限及校准预算为项目设置，不归称为原文公开参数 |

原生算法、候选适配和全部失败分别记录于 [2026-10-11 场景诊断](../results/baseline_scenario_audit_20261011/REPORT.md)。

## 2026-10-10：GFRA 与 AFDM 导频观测的文献依据

| 原词或忠实译名 | 原文定位 | 当前使用范围 |
|---|---|---|
| two-phase transmission protocol / 两阶段传输协议 | [Liu–Yu，Massive Connectivity with Massive MIMO–Part I](https://arxiv.org/html/1706.06438)，§II、Fig.2；§III-A 式(8)–(11) | 活跃用户先发送已知导频进行活动检测和信道估计，再发送数据。支持单独研究导频阶段，不据此声称具体 AFDM 多帧设置与该文相同 |
| embedded pilot-aided channel estimation / 嵌入式导频辅助信道估计 | [Bemani–Ksairi–Kountouris 作者稿](https://arxiv.org/html/2204.12798v2)，§VI、式(66)–(67)；[Ding 接受稿](../paper/literature/ding2026.pdf)，p.2 §III-A 式(6)–(9) | 同一 AFDM 帧内放置导频、零保护符号及数据。Bemani 单导频符号与 Ding 导频块长度不同；不将 embedded 与 superimposed 视为同义词 |
| multiple pilot transmissions / 多次导频传输；transmitted pilot symbol matrix / 发送导频符号矩阵 | [Huang 2026](../paper/literature/huang2026.pdf)，pp.2950–2951 §III-A、式(6) | X 的每个元素为已知 QPSK 导频，多个 N 维向量共同估计完整 AFDM 有效信道；是当前整帧已知导频、多次观测的直接依据。原文是单用户单天线，未给当前部分 DFT 导频、Q=16 多用户协议或准确已知跨帧相位的等价性 |
| pilot signal / 导频信号 | [Mao 等，Grant-Free Random Access in Uplink LEO Satellite Communications with OFDM](https://arxiv.org/html/2504.04686)，§II-A 式(1)–(3)及其后定义 | 多用户向 UPA 卫星发送 M 个 OFDM 符号，N 个子载波上的输入均定义为导频。是 LEO GFRA 多符号已知导频观测的先例，波形及 BEM 信道表示与当前不同 |
| spreading-based multi-frame OTFS transmission scheme / 基于扩频的多帧 OTFS 传输方案 | [Shen 2025 作者稿](https://arxiv.org/html/2412.20806v1)，§II-B 式(2)–(15) | 支持大差分时延/Doppler 下多帧联合观测思路；发送量包含扩频的未知数据，不能列为整帧纯导频的直接先例 |

以上为代表性原始论文核验，不是导频方案占比的文献计量统计。“整帧已知导频”是对发送向量所有坐标均已知的直接描述，不作为新方法名称。

## 2026-10-10：Ding 系统对照中的参数含义

| 原词或忠实译名 | 原文定位 | 当前使用范围 |
|---|---|---|
| zero guard interval / 零保护区；pilot length / 导频长度 | [Ding 接受稿](../paper/literature/ding2026.pdf)，p.2 §III-A 式(6)–(9) | 原文 Q 表示保护区、Lp 表示导频长度；式(6)完整帧含数据，式(7)–(9)隔离导频用于活动检测和信道估计，不估计数据；不将原文 Q 与本项目多帧 Q 视为同一参数 |
| integer and fractional parts / 整数和分数部分；normalized Doppler / 归一化 Doppler | 同文 p.2 §II 式(3)前后、p.5 §IV-A | 原文理论含分数 Doppler、仿真真值对齐网格；比较 ν/Δf 和 Hz 两种范围时分别注明单位 |

实际配置与逐项证据见[系统对照](../results/baseline_core_check_20261010/DING_SYSTEM_COMPARISON.md)。

## 2026-10-10：Zhao 全文核验

| 原词或忠实译名 | 原文定位 | 本项目使用范围 |
|---|---|---|
| MMV-GAMP based JADCE method / 基于 MMV-GAMP 的 JADCE 方法 | [Zhao 2025](../references/zhao2025_mixed_fronthaul_jadce.pdf)，p.4126 Algorithm 1；pp.4123–4124 式(20)–(30)、(36)、(49) | 独立来源实现；标量 BG 后验、无阻尼、学习 β、各列噪声和平均稀疏率。AFDM 字典及用户块扩展均明确标注 |
| Bernoulli-Gaussian distribution / Bernoulli–Gaussian 分布 | 同文 p.4120 式(3) | 原文 slab 均值为零；不是删掉 Zhao 的均值学习步骤 |
| log-likelihood ratio (LLR) test / 对数似然比检验 | 同文 p.4125 §III-D、式(51)、(53)–(55) | 直接计算两个复数 Gaussian 密度的 log 比，阈值零；用户块求和和 νr 协方差估计为项目适配 |
| EM update / EM 更新 | 同文 p.4124 式(37)–(40) | 用户明确选择式(38)–(39)的驻点推导；记录与印刷式(40)的不一致，不称为式(40)的逐字复现 |

全文指纹与两版递推的检查见 [Zhao 来源报告](../results/zhao2025_20261010/REPORT.md)。以下“待取得全文”描述保留为此前状态。

## 2026-10-10：原文网格与活动判决恢复

| 原词或忠实译名 | 原文定位 | 此次使用范围 |
|---|---|---|
| uniformly divided grids / 均匀划分网格 | [Ding 接受稿](../paper/literature/ding2026.pdf)，p.2 式(8)及 p.5 §IV-A | 原文参数给出时延步长为一个采样点、Doppler 步长为一个子载波间隔。本项目恢复相同归一化步长，对新场景扩展支持；每用户 80 原子是项目覆盖范围，不归称为 Ding 原文 15 原子 |
| decision threshold / 判决门限 | 同文 p.4 式(27) | 对原生物理系数块平均能量作最大值归一化并使用 >=；η 数值未公开，独立校准选择明确标为项目设置 |
| GAMP with EM / 使用 EM 的 GAMP | 同文 p.5 §IV-A、参考文献 [10]；Zhao 等 IEEE TVT 74(3), pp.4117–4131, DOI 10.1109/TVT.2024.3483968 | 原文对照是 Zhao 2025，不能将 Vila–Schniter EM-BG-AMP 标为同一来源；Zhao 的具体参数学习与 CPU 判决公式待全文核对 |

对应代码与差异见[网格说明](BASELINE_GRID.md)、[活动判决说明](BASELINE_ACTIVITY_READOUT.md)。

2026-10-10：NNSPL 已退出当前比较并[归档](../archive/nnspl_20261010/README.md)。本文保留其历史论文名称、公式及出处；EM 共用的 Bernoulli–Gaussian 行后验改为独立文件，公式与原记录一致。

## 2026-10-10：固定活跃人数的实验条件

| 原词或忠实译名 | 原文定位 | 本项目使用范围 |
|---|---|---|
| device activity indicator / 设备活动指示量；device access probability / 设备接入概率 | [Senel–Larsson，*Grant-Free Massive MTC-Enabled Massive MIMO: A Compressive Sensing Approach*，§II式(3)及其后定义](https://arxiv.org/html/1806.10061#S2) | 区分单用户活动概率与每次实现的活跃人数；原文Bernoulli活动模型不被归称为固定人数设置 |
| number of active devices / 活跃设备数 | 同文§I、Fig.1及§III-A中K的说明 | 新实验直接规定Σₖαₖ=J，均匀抽取J个候选用户。P(α)=1[Σₖαₖ=J]/C(K,J)为项目明确的实验分布，不命名为新算法 |

固定J时各用户的边缘活动概率为J/K，但活动指示量相关；独立Bernoulli推断是工作近似。
实施和适用范围见[固定人数实验协议](../experiments/fixed_activity_20261010/PROTOCOL.md)。

2026-10-10 训练与评价条件：未来 GNN-ASPL 重训的 on-grid 条件依据 Ding 接受稿 p.5 §IV-A 的 grid points 设置；新增独立校准与性能评价采用下文 Shen §V 定义的 off-grid 条件。现有权重保留其历史混合网格预训练与联合微调身份。固定先验方差只由 on-grid 训练信道的真实占用行系数能量拟合，合并重合路径并核验完整 H 重构误差；受限支撑最小二乘沿用 Tropp Algorithm 3.1/§3.2 的通常含义，此训练统计选择为项目设置。

## 2026-10-10：四方法维护入口的来源与适配

| 原词或忠实译名 | 原文定位 | 此次使用范围 |
|---|---|---|
| simultaneous orthogonal matching pursuit / 同时正交匹配追踪 | [Tropp 等作者稿](https://tropp.caltech.edu/papers/TGS05-Algorithms-Simultaneous-I-preprint.pdf)，pp.6–7 Algorithm 3.1、§3.2 | 保留跨列相关绝对值之和选列及共同支撑最小二乘；秩限制与预算用尽是不同退出原因 |
| GAMP-SBL | [Zhang 2023 本地原文](../references/zhang2023_gamp_sbl_grant_free_noma.pdf)，pp.15058–15059 Eqs.(3)–(19)、Algorithm 1 | 保留单次 GAMP/精度更新顺序；复数共享行 MAP 由跨列 CN 密度乘积得到，属于本项目 MMV 适配 |
| EM-BG-AMP | [Vila–Schniter 2013](https://arxiv.org/html/1207.3107v3)，Tables I–II、Eqs.(27),(34),(41),(47)、§III-E | 行概率与 slab 参数的 EM 更新；式 (47) 使用旧 slab 均值，噪声更新使用当前输出后验 |
| damping / 阻尼；warm start / 热启动 | [Vila 等 2015](https://arxiv.org/html/1412.2005)，Table 1；[作者 warmStart 代码阅读记录](../results/baseline_resolution_20261009/em/author_code/READ_EVIDENCE.md) | 固定阻尼与跨 EM 轮保留完整状态；未声称实现该文完整自适应阻尼规则 |
| layer-wise training / 逐层训练 | [Ding 接受稿](../Learning_Sparsity_Pattern_An_Adaptive_Joint_Detection_for_AFDM_Grant-Free_System_in_LEO_Satellites_Communication.pdf)，pp.4–5 §III-C、Eq.(28) | 顺序训练前一层 GNN、当前 AMP、当前前缀全部参数；十层对应 29 个有效阶段。阶段 epoch 数、混合 SNR 与物理 H 损失是项目设置 |
| activity detection / 活动检测 | 同一 Ding 接受稿 p.4 Eq.(27) | 沿用最大用户能量归一化与 `>=`。本项目细网格非正交，使用完整 H 能量替代系数能量；保留相干交叉项并单独校准门限 |

`relative_state`、输出窗口与返回状态残差检查仅是本项目数值停止操作的代码标识，不是 Zhang 原文命名的算法，也不构成自适应 SBL 的收敛证明。

## 2026-10-09：第二章结构

| 原词或忠实译名 | 原文定位 | 本稿使用范围 |
|---|---|---|
| System Model / 系统模型 | [Shen 作者稿 §II](https://arxiv.org/html/2412.20806v1) | 本稿第二章标题 |
| Terrestrial-satellite Link Model / 星地链路模型 | 同文 §II-A | II-A，物理几何、时延、Doppler与阵列响应；本稿标题按标题式大小写书写 |
| Transmission Scheme / 传输方案 | 同文 §II-B | II-B，AFDM调制、路径算子、导频及接收模型的连续展开 |
| Problem Formulation / 问题表述 | 同文 §II-C | II-C，观测、未知量、先验与估计目标 |

用户已确认上述三小节结构；正文与展开蓝图分别见 [第二章源文件](../paper/sections/02_system_model.tex)和[写作蓝图](../paper/writing_profile/pre_simulation_20261009/system_model_writing_blueprint.md)。参考 Ding §II 的信号链、Cai §II-B 的贝叶斯问题表述组织相关段落，保留本项目既有模型与公式。

## 2026-10-09：II–V正文与14篇写作语料

语料、原文版本和小节/公式定位见[本轮清单](../paper/writing_profile/pre_simulation_20261009/corpus_manifest.md)；逐小节写作依据见[系统模型蓝图](../paper/writing_profile/pre_simulation_20261009/system_model_writing_blueprint.md)和[算法蓝图](../paper/writing_profile/pre_simulation_20261009/algorithm_writing_blueprint.md)。

| 原词或忠实译名 | 原文定位 | 本稿使用范围 |
|---|---|---|
| noise conditional score networks / 噪声条件得分网络 | [Song–Ermon, NeurIPS 2019](https://papers.nips.cc/paper/9361-generative-modeling-by-estimating-gradients-of-the-data-distribution.pdf)，§4.1，正文第5–6页 | IV-A/D用噪声水平条件化共享score网络；生成式先验通过受扰信道分布的score表示 |
| high-order denoising score matching / 高阶去噪得分匹配；trace / 迹 | [Lu等, ICML 2022](https://proceedings.mlr.press/v162/lu22f/lu22f.pdf)，§4.2，Theorem 4.1、Corollary 4.2，式(13)–(15)，正文第5页 | IV-B采用迹学习的原有思路，明确推导有限均值网络的条件MSE；只解释平均读数 |
| MMSE denoiser / MMSE去噪器；posterior mean / 后验均值 | [Liu–Yu, TSP 2018](https://arxiv.org/html/1706.06438v2)，§III-C式(19)–(22)；[Ke等, TSP 2020](https://arxiv.org/html/1906.09867v4)，§III-B式(13)–(17) | III-B先给局部后验和联合矩，再给网络近似及Gaussian消息 |
| density ratio estimation / 密度比估计；class-probability estimation / 类别概率估计 | [Menon–Ong, ICML 2016](https://proceedings.mlr.press/v48/menon16.pdf)，§3式(6)–(8)，§4.2式(16)–(17)，第305–306页 | IV-C推导BCE最优logit与训练/接入先验修正 |

其余DAFT、CPP、array response vector、Gaussian site、extrinsic message和damping沿用本页已有来源。本文的条件误差平均、site接受条件与停止规则以公式直接描述，不另命名。实噪声方差在本稿记为v_R=v/2，与物理Doppler ν_k区分；数学含义不变。

## 2026-10-09：方法章节命名

| 原词或忠实译名 | 原文定位 | 本稿使用范围 |
|---|---|---|
| Bayesian Receiver Design / 贝叶斯接收机设计 | [Han等作者稿§III](https://arxiv.org/html/2205.00138v2) | III直接复用章名，描述本稿已有近似贝叶斯迭代；不改变任务或后验假设 |
| Channel and Device Activity Denoisers / 信道与设备活动去噪器 | [Cai正式版§III-B，印刷页3579–3581](../references/cai2026_score_based_jadce.pdf)；[作者稿§III-B](https://arxiv.org/html/2506.00581v2) | IV标题采用Learning Channel and Activity Denoisers with Score-Based Generative Priors，以两类去噪器为共同学习对象；这一章名是描述性改写。信道侧学习均值与条件误差，活动侧通过密度比及公开先验得到活动概率 |
| Score-Based Generative Priors / 基于得分的生成式先验 | [Cai正式版§IV，印刷页3582–3583](../references/cai2026_score_based_jadce.pdf)；[作者稿§IV](https://arxiv.org/html/2506.00581v2) | IV标题中的先验表征方式；信道先验通过score表征，活动密度比分类器单独定义学习目标 |
| Score-Based Generative Modeling / 基于得分的生成式建模 | [Arvinte–Tamir作者稿§II-D](https://arxiv.org/html/2204.07122v2) | IV内生成式信道先验部分的术语依据 |
| Overall Algorithm / 整体算法；Computational Complexity Analysis / 计算复杂度分析 | [Ying等作者稿§V-D/E](https://arxiv.org/html/2505.12382v3)；后者亦见[Mei等§IV-B](https://arxiv.org/html/2011.07928) | 分别用作V及V-C标题；内容仍为本稿执行步骤和实际运算量 |
| Message Scheduling / 消息调度 | [Shen等作者稿§III-B](https://arxiv.org/html/2412.20806v1) | V-A定义初始化后的调用次序及消息反馈 |

Activity Detection、score matching、conditional MSE、density ratio estimation、extrinsic message与damping沿用本页已有来源。条件误差估计、外信息更新及阻尼与停止条件是对已有操作的普通描述，未设新方法名。完整命名依据见[结构提纲](../paper/writing_profile/section_structure_20261009/SECTION_STRUCTURE.md)。

## 2026-10-09：原导频模型下的联合行NNSPL适配与活动判决

| 原词或忠实译名 | 原文定位 | 本项目使用范围 |
|---|---|---|
| nearest neighbor sparsity pattern learning / 最近邻稀疏模式学习 | [Meng2016 §III Eq.(17)、Algorithm1](https://arxiv.org/html/1601.00543v1#S3) | 保留不含自身、无周期绕回、同用户DD轴向邻域；原SMV实现保留，联合行入口另标为适配 |
| posterior distribution / 后验分布 | Ding接受稿p.3 Eqs.(14)–(18)；Meng Eqs.(11)–(16)、(19)–(20) | 对所有天线的复Gaussian行似然乘积计算一个非零概率，再按Meng原近邻及EM方程更新；这不是对Ding未公开NNSPL代码的确认 |
| damping / 阻尼 | [Rangan等 arXiv:1402.3210v3 Algorithm1第9、13行](https://arxiv.org/html/1402.3210v3)；Ding接受稿p.3 Eqs.(19)–(20) | 消息和均值使用0.5权重；此外方差、近邻概率和EM参数也与旧值按0.5加权平均，是明示的项目数值设置，不能归称Meng原文规定或据此引用收敛保证 |
| activity detection / 活动检测 | Ding接受稿p.4 Eq.(27)、p.5 §IV-B | 使用物理系数用户能量除以本场景最大能量，按原文≥判决；门限由独立校准样本选定，评价样本不参与拟合 |

代码标识`amp_nnspl_mmv_afdm`表示已声明的复数联合行接入，不是另命名的学术算法。原导频NTN-TDL-A选择下初始行非零率为公开条件活动率/5，原200轮上限和1e−6均值停止量保持不变。12个开发输入的数值改善见`results/ding_reproduction_20261009/nnspl_mmv_complete_damping_200`；独立性能仍由单独校准/评价确定。

## 2026-10-09：Ding原导频观测模型

| 原词或忠实译名 | 原文定位 | 本项目使用范围 |
|---|---|---|
| zero guard interval / 零保护区；expanded pilot matrix / 扩展导频矩阵 | [Ding接受稿](../Learning_Sparsity_Pattern_An_Adaptive_Joint_Detection_for_AFDM_Grant-Free_System_in_LEO_Satellites_Communication.pdf)，p.2 §III-A Eqs.(6)–(9) | 新原设置入口按原取样索引构造65×1500的Ψ；Q在该段表示保护区长度15，与项目多帧数Q分别使用 |
| NTN-TDL-A；Rayleigh fading / Rayleigh衰落 | [3GPP TR38.811，ATIS V15.3.0](https://atisorg.s3.amazonaws.com/archive/3gpp-documents/Rel15/ATIS.3GPP.38.811.V1530.pdf)，printed p.89 Table6.9.2-1；p.88 §6.9.2 | 三抽头原归一化时延0、1.0811、2.8416，功率0、−4.675、−6.482 dB。本入口选择该profile并缩放、量化至0/1/2；Ding只写3GPP/P=3且引用V15.4.0，未指定profile，该选择不是作者参数的核实 |
| integer Doppler shifts / 整数Doppler；AFDM parameters / AFDM参数 | [Bemani等 arXiv:2204.12798v2](https://arxiv.org/html/2204.12798v2)，§III-D Eqs.(27)–(31)、§III-E Eq.(42) | 新入口用单个非零元素的路径矩阵和c1=(2αmax+1)/(2N)，再独立按IDAFT/CPP/时间移位/DAFT核对；N与c2具体值是实现设置 |

该原设置入口与现有多帧、完整物理信道接收机分别运行。来源、缺省设置及必要验证见[DING_REPRODUCTION_SCOPE.md](DING_REPRODUCTION_SCOPE.md)，源码为`system/scenario/ding2026.py`。

## 2026-10-08：五种基线原论文的网格条件

| 原词或忠实译名 | 原文定位 | 本项目使用范围 |
|---|---|---|
| grid points / 网格点 | [Ding，Learning Sparsity Pattern，DOI 10.1109/TVT.2026.3729877](https://doi.org/10.1109/TVT.2026.3729877)，本地PDF p.5 §IV-A；Fig.3共用该场景 | 原文真实delay/Doppler与网格点对齐，(Nl,Nk)=(2,4)。这是物理on-grid假设；不能从中推断各基线源头论文都建立了相同AFDM模型。 |
| dictionary、atoms / 字典、原子 | [Tropp–Gilbert–Strauss，作者稿§2.2 p.4](https://tropp.caltech.edu/papers/TGS05-Algorithms-Simultaneous-I-preprint.pdf) | SOMP的原字典是预先给定的有限单位范数原子集合；本项目将其原子指定为整数时延/Doppler原子。 |
| multiuser detection、sparse transmitted signal / 多用户检测、稀疏发送信号 | [Zhang 2023，DOI 10.1109/TVT.2023.3280919](https://doi.org/10.1109/TVT.2023.3280919)，§II Eqs.(1)–(2)，p.15058 | 原GAMP-SBL恢复b，H包含已知信道响应和扩频码；原文没有连续时延/Doppler恢复。本项目沿用推断更新，换成AFDM物理字典与待估信道系数。 |
| sparse (or compressible) signal / 稀疏（或可压缩）信号 | [Vila–Schniter 2013，§I–II](https://arxiv.org/html/1207.3107v3#S1) | 当前EM-BG-AMP源头为已知A的有限维线性模型y=Ax+w；不是Ding所引Zhao mixed-fronthaul论文的完整复现。 |
| clustered sparse signal / 簇状稀疏信号 | [Meng 2016，§II Eq.(1)、§III Eq.(17)](https://arxiv.org/html/1601.00543v1#S2) | AMP-NNSPL的原邻域对应有限向量/图像坐标，不能将该索引直接解释为原论文的物理时延/Doppler网格假设。 |

有限系数模型与物理on-grid条件分别记录：当前五种接收机使用固定整数时延/Doppler字典，均未包含连续参数细化；本次pilot的真实信道参数连续，因此属于固定字典下的off-grid性能验证，而非Ding的on-grid场景复现。原文定位与实际训练适配见[基线修订说明](BASELINE_REVISION.md)。

## 2026-10-08：SNR实验中的on-grid/off-grid条件

| 原词或忠实译名 | 原文定位 | 本项目实验中的使用 |
|---|---|---|
| on-grid、off-grid / 网格内、网格外 | [Shen等，*LEO Satellite-Enabled Random Access with Large Differential Delay and Doppler Shift*，§V，PDF p.12定义两种情况，p.13 Fig.7、p.14 Fig.9](../references/shen2025_large_differential_delay_doppler.pdf)；对应[arXiv:2412.20806v1 §V](https://arxiv.org/html/2412.20806v1#S5) | 借鉴在SNR组中同时评价两种条件的组织方式；本项目按共同AFDM时延/Doppler字典明确对齐与连续参数两种生成规则，详见[实验协议](EXPERIMENT_PROTOCOL.md) |

本地Shen文件为2024-12-30的v1作者稿。原文按分数Doppler为0或处于(−1/2,1/2]区分两种情况，off-grid还需估计额外相位；其传统基线仅在on-grid评估。本项目两分支都保持准确已知有效跨帧相位的信息条件，并不复用该文未知相位的实验结论。on-grid不表示只在接收机采用有限字典，也不表示所有AFDM跨帧相位都为零。

## 2026-10-08：Ying 2026 扩散模型论文的实验参照

核对论文为 Keke Ying 等，*Generative Diffusion Model Driven Massive Random Access in Massive MIMO Systems*，TWC 2026，DOI [10.1109/TWC.2025.3636585](https://doi.org/10.1109/TWC.2025.3636585)。以下章节和图号以[作者稿 arXiv:2505.12382v3](https://arxiv.org/html/2505.12382v3)为准；此处仅记录实验分析所用术语，不改变本项目算法或实验配置。

| 原词或忠实译名 | 原文定位 | 本次使用范围 |
|---|---|---|
| variable pilot length AUD network / VPL-AUDNet，可变导频长度活动用户检测网络 | §IV，Fig.1；§VI-B，Figs.6–9 | Ying 的第一阶段活动检测方法；用于参照导频长度、活动率和固定权重迁移实验，不作为本项目网络名称 |
| pilot length adaptive module / PLAM，导频长度适应模块；spatial correlation module / SCM，空间相关模块 | §IV-A/C；§VI-B，Figs.6–8 | 原论文模块消融及泛化设置；不能据此推定本项目固定维度网络支持天线数迁移 |
| joint channel estimation and data detection / JCEDD，联合信道估计与数据检测 | §III-B、§V；§VI-C，Figs.10–16 | Ying 的第二阶段任务，包含数据符号恢复；其 BER 与数据长度实验不是当前仅做活动检测和信道估计的必要指标 |
| activity error probability / AEP，活动错误概率 | §VI-A3 | 原文定义为 E[(1/K)Σ_k\|α_k−α̂_k\|]；比较时须另核对本项目活动抽样及聚合口径 |
| predictor-corrector sampler / 预测–校正采样器 | §V-B3，Algorithm 1；§VI-C，Fig.14 | Ying 反向扩散算法的步数实验；不能把其扩散步数等同于本项目消息传递迭代次数 |

## 2026-10-08：Meng AMP-NNSPL原论文实现

| 原词或忠实译名 | 论文出处及原文定位 | 本项目使用 |
|---|---|---|
| approximate message passing with nearest neighbor sparsity pattern learning / AMP-NNSPL，最近邻稀疏模式学习 | [Meng等2016，arXiv:1601.00543v1，p.1标题；pp.2–3 §III Eq.(17)、Algorithm 1](https://arxiv.org/pdf/1601.00543v1) | 轴向邻居后验非零概率的平均，不含自身；AFDM用户块之间和天线列之间独立 |
| spike and slab prior / spike-and-slab先验 | 同文p.2 Eq.(10)，pp.2–3 Eqs.(11)–(16) | 保留原实Gaussian后验；AFDM使用复Gaussian密度延拓 |
| expectation maximization / 期望最大化 | 同文p.3 Eqs.(18)–(20)、Algorithm 1 | 每轮AMP后学习均值、使用旧均值更新方差；噪声学习可选，AFDM默认固定公开噪声 |

200轮上限及1e−6停止常数见同文p.4 §IV；Algorithm 1的停止量为相邻均值差的无平方范数。初始SNR=100为线性比值，见p.3 Algorithm 1前段。复数、已知噪声和物理字典适配，以及原文与历史联合行概率实现的区别，见[来源记录](../results/baseline_completion_20261008/NNSPL_SOURCE.md)和[五方法实现说明](BASELINE_IMPLEMENTATIONS.md)。

原文§II是实数SMV；当前逐天线实现保留列间独立性，不能直接称为Ding的MMV NNSPL对照复现。Ding p.3式(14)–(16)明示的是所提方法的联合行后验，不能据此补写其未给出的NNSPL baseline完整配方。该界线及当前逐式/设置核对见[SOMP_NNSPL_FIDELITY_RECHECK.md](../results/baseline_pilot_20261008/paper_reaudit/SOMP_NNSPL_FIDELITY_RECHECK.md)。

本次初步实验另采用 damping / 阻尼，依据[Rangan–Schniter–Fletcher–Sarkar，arXiv:1402.3210v3，Algorithm 1第9、13行及§II-B](https://arxiv.org/html/1402.3210v3)。`message_damping`、`mean_damping`分别为原文 θ_s、θ_x 的新值权重；两者0.5为校准公共输入核验后的项目设置。固定噪声时，把Meng的Z/V更新换算为残差消息s，再对s和系数均值插值；方差、最近邻及EM仍完整更新。原Meng模式保留两权重1。达到停止条件时，阻尼模式报告相对阻尼均值步长，并记录未阻尼均值差；不将固定Gaussian或凸先验的收敛定理直接用于本次BG/EM模型。全部校准、异常与出处见[NNSPL稳定性记录](../results/baseline_pilot_20261008/NNSPL_STABILITY_ADAPTATION.md)。

## 2026-10-08：Cai 推导完整性核对

[审查记录](CAI_DERIVATION_AUDIT.md)以 Cai 原文为推导范围参照，未将作者程序的特定快照等同于原论文。
术语继续采用以下已有名称；本轮直接推导和合成反例不另命名算法。

| 原词或忠实译名 | 原文定位 | 当前补充 |
|---|---|---|
| turbo message passing、Gaussian projection、extrinsic message / turbo消息传递、Gaussian投影、外信息消息 | [Cai §III-A–B，式(6)–(42)，正式版pp.3579–3581](../references/cai2026_score_based_jadce.pdf) | THEORY T3–T6b、T13–T17与A6–A7明确局部后验、投影和Gaussian相除 |
| Tweedie's formula、denoising score matching、second-order score matching | 同文§IV-A–C，式(44)–(54)，pp.3582–3583 | THEORY A1–A3补求导与条件回归证明；总迹监督不逐坐标识别Hessian |
| density ratio estimation、class-probability estimation、logistic loss / 密度比估计、类别概率估计、logistic损失 | [Menon–Ong §3式(6)–(8)、§4.2式(16)–(17)，pp.305–306](https://proceedings.mlr.press/v48/menon16.pdf) | THEORY A5从点态BCE导数证明训练赔率及先验修正；有限网络和实际查询条件另行声明 |
| fractional delay、fractional Doppler、effective channel matrix / 分数时延、分数Doppler、有效信道矩阵 | [Huang §II式(4)–(5)，p.2950](../references/huang2026_prior_agnostic_afdm_diffusion.pdf)；[Bemani §II-B式(11)–(16)、§III-A式(18)–(19)](https://arxiv.org/html/2204.12798v2) | 草稿式(6a)、(8a)显式定义连续波形并展开当前路径矩阵；与Huang比较取 \(k_{\nu,\rm Huang}=-\nu_{\rm here}NT_s\)，不是同号复制 |
| array response vector、common spatial direction / 阵列响应向量、共同空间方向 | [Li–Gao–Xia §II-C式(8)](https://arxiv.org/html/2207.11958v2#S2.SS3) | SYSTEM_MODEL S3–S4另给本项目完整复包络、阵元索引与几何Doppler符号推导；不把特定编号约定归称原文定义 |

共享方差的受限期望负对数密度最优值、四相位先验的同矩异证据反例、正性传递及本实现复杂度，
分别由 THEORY A4、A8–A9、第11节直接推导。反例仅证明单个查询位置的一二阶条件矩不足以唯一确定边缘密度，
不声称整个score函数的信息不足，也不作为分类器性能或创新等级的证明。

## 2026-10-08：EM-BG-AMP与GNN-ASPL

| 原词或忠实译名 | 论文出处及原文定位 | 本项目使用 |
|---|---|---|
| expectation-maximization Bernoulli–Gaussian approximate message passing / EM-BG-AMP | [Vila–Schniter 2013 arXiv:1207.3107 §III-B pp.4–5 Eqs.(28),(34),(41),(47)，§III-E p.7 Table II](https://arxiv.org/pdf/1207.3107) | Gaussian分量数L=1；完整GAMP E步与EM外循环。软件名`em_bg_amp_vila2013`，公开噪声固定及阻尼值为项目设置 |
| circularly symmetric complex Gaussian / 圆对称复Gaussian | 同文§II p.2复数转换说明、Table I p.3 Eqs.(9)–(11),(15)–(17) | 复均值回投用Aᴴ、方差用\|A\|²；BG概率用CN密度，不保留实Gaussian的1/2 |
| graph neural network-based adaptive sparsity pattern learning / GNN-ASPL | [Ding等2026 PDF pp.4–5 §III-B/C Eqs.(20)–(26),(28)](../Learning_Sparsity_Pattern_An_Adaptive_Joint_Detection_for_AFDM_Grant-Free_System_in_LEO_Satellites_Communication.pdf) | 块内图网络预测下一层稀疏先验；32维网络及明确邻接集为项目设置 |
| attention mechanism、gated recurrent unit / 注意力机制、门控循环单元 | 同文p.4 Eqs.(22)–(26) | 原四维节点特征的attention加权消息输入GRU；跨层hidden递推和Sigmoid输出 |
| trainable damping、layer-wise training / 可训练阻尼、逐层训练 | 同文p.3 Eq.(12a)、p.4 Eq.(18a)、pp.4–5 §III-C；p.5 §IV-A | 输出方差与系数均值的两处阻尼；训练上一层GNN、当前AMP参数，再联合微调前t层 |

原文印刷式与可执行修正、来源检索及项目适配分别见[EM来源记录](../results/baseline_revision_20261008/phase2_sources/EM_GAMP_SOURCE.md)、[GNN最新逐式审查](../results/baseline_pilot_20261008/paper_reaudit/GNN_ASPL_PAPER_CODE_AUDIT.md)和[基线调整](BASELINE_REVISION.md)。Zhao 2025的EM-GAMP名称目前只用于Ding文献来源记录，不作为上述实现名称。

## 2026-10-08：Ding所引GAMP-SBL的论文流程

GAMP-SBL / generalized approximate message passing sparse Bayesian learning采用 [Zhang 2023 p.15057原文名称、p.15059 Algorithm 1](../references/zhang2023_gamp_sbl_grant_free_noma.pdf)。[Ding 2026 p.5 §IV-B、p.6参考文献[8]](../Learning_Sparsity_Pattern_An_Adaptive_Joint_Detection_for_AFDM_Grant-Free_System_in_LEO_Satellites_Communication.pdf)将该方法列为对比算法。Algorithm 1 Stage 2–3每次GAMP更新后学习精度，Stage 4使用每列相邻均值向量变化的平方和不超过1e−6的停止条件。本轮恢复该流程，0.2阻尼值、共同已知噪声及初始化为项目设置；Gaussian复数公式与相位不变性检查见 [DING_GAMP_ALIGNMENT.md](DING_GAMP_ALIGNMENT.md)。damping / 阻尼依据沿用 [Rangan Algorithm 1、§II-B](https://arxiv.org/html/1402.3210)。


## 2026-10-08：论文第二、三章初稿

初稿见 [sections_II_III.tex](../paper/main.tex)。以下补充波形术语与正文来源定位；已有 score、消息传递和活动分类术语沿用本页后续条目。

| 原词或忠实译名 | 一级来源与定位 | 初稿中的使用 |
|---|---|---|
| affine frequency division multiplexing、discrete affine Fourier transform、chirp-periodic prefix / AFDM、离散仿射傅里叶变换、啁啾周期前缀 | [Bemani–Ksairi–Kountouris arXiv:2204.12798v2 §II-B式(11)–(16)、§III-A式(18)–(19)](https://arxiv.org/html/2204.12798v2) | DAFT定义、整数采样的啁啾周期关系和前缀覆盖条件；正文用该周期关系写出跨多个周期的统一前缀表达 |
| fractional delay、fractional Doppler、effective channel matrix / 分数时延、分数多普勒、有效信道矩阵 | [Huang等2026 §II，p.2950，式(1)、(4)–(5)](https://doi.org/10.1109/LWC.2026.3689601) | 连续路径算子的物理依据；正文明确使用正号Doppler调制，延时基与整数极限按当前代码公式写出 |
| array response vector、common spatial direction / 阵列响应向量、共同空间方向 | [Li–Gao–Xia §II-C式(8)](https://arxiv.org/html/2207.11958v2#S2.SS3)；Huang §II式(2)后，p.2950 | 共同方向与每用户共同Doppler，空间展开的秩一结构由正文因式分解直接得到 |
| Tweedie's formula、denoising score matching / Tweedie公式、去噪得分匹配 | [Cai v2 §IV-A–C式(43)–(54)](https://arxiv.org/html/2506.00581v2#S4)；原始来源 Efron 2011 JASA pp.1602–1614、Vincent 2011 Neural Computation pp.1661–1674，Cai参考文献[29]–[30] | 实复方差换算、一阶均值与全坐标平均二阶损失；有限均值的条件MSE分解在正文直接推导 |
| Gaussian projection、extrinsic message、damping / Gaussian投影、外信息消息、阻尼 | [Minka §II–III式(5)–(6)、(9)–(12)，pp.363–364](https://tminka.github.io/papers/ep/minka-ep-uai.pdf)；[Cai §III、§V-B1式(57)–(58)](https://arxiv.org/html/2506.00581v2) | 两模块的迹投影、Gaussian自然参数相除，以及均值/方差算术插值 |
| density ratio estimation、class-probability estimation、logistic loss / 密度比估计、类别概率估计、logistic损失 | [Menon–Ong §III式(6)–(8)、§IV-B式(16)–(17)，pp.305–306](https://proceedings.mlr.press/v48/menon16.pdf) | 平衡分类器的logit与一次先验赔率校正；网络输入和消息接法按本项目实现定义 |

正文中的条件风险、共享方差、Gaussian site接受条件与停止统计均以公式定义，不另设方法缩写。

## 2026-10-08：GAMP 的有限矩阵后验参照

Gaussian posterior mean/covariance / Gaussian后验均值/协方差、E-step / E步，以及一般矩阵下近似 posterior variance 的用法，核对[Al-Shoukairi–Schniter–Rao §II-B式(7)–(9)、§III-B2](https://arxiv.org/html/1703.03044)。本次公开AFDM输入的一列在固定学习精度后，以Gaussian条件公式计算参照，不读取真实信道；GAMP方差固定点与该精确后验对角的差异是近似误差，不包装为编码错误或所有场景的性能结论。详细矩阵、误差分母与范围见[GAMP数值复核](../results/gamp_reassessment_20261008/REPORT.md)及[0.5候选条件后验参照](../results/gamp_damping_tuning_20261008/CONDITIONAL_POSTERIOR_REVIEW.md)。

damping / 阻尼及固定Gaussian先验下的收敛条件，核对[Rangan等 arXiv:1402.3210v3，Algorithm 1、§II-B、§IV–V](https://arxiv.org/html/1402.3210)。本次θ表示均值/消息新值权重、η表示项目精度目标新值权重，仅为公式参数，不能把固定先验的定理直接应用于每轮精度学习。

新增可选`mean_damping`与`message_damping`分别实现[Rangan Algorithm 1第13、9行](https://arxiv.org/html/1402.3210)的θx与θs；未指定时分别继承旧共同阻尼，未改变方差递推。`learning_damping`为项目精度目标的正插值，三者的代码名称是配置字段，不是新算法名称。公式审查见[FORMULA_REVIEW.md](../results/gamp_damping_tuning_20261008/FORMULA_REVIEW.md)，预定有界实验见[REPORT.md](../results/gamp_damping_tuning_20261008/REPORT.md)。

Zhang实值精度式(16)分子核对为`2a−1`，[本地原文第15059页](../references/zhang2023_gamp_sbl_grant_free_noma.pdf)。此前调度报告的`1+2a`转录在最新公式审查中明确更正；当前CN模型的proper-complex精度目标仍为`a/(Eabsx²+b)`。

## 2026-10-08：活动分类与密度比估计的来源核查

详细核对见 [ACTIVITY_EVIDENCE_SOURCES.md](ACTIVITY_EVIDENCE_SOURCES.md)。以下名称采用文献原词或忠实译名；当前网络的具体特征和MP接法属于项目设计。

| 原词或忠实译名 | 一级来源与定位 | 本项目使用范围 |
|---|---|---|
| density ratio estimation、class-probability estimation / 密度比估计、类别概率估计 | [Menon–Ong 2016 §3式(6)–(8)、§4.2式(16)–(17)，pp.305–306](https://proceedings.mlr.press/v48/menon16.pdf) | BCE/logistic输出经训练类别先验校正恢复活动/零信号密度比估计 |
| calibrated discriminative classifiers / 经校准的判别分类器 | [Cranmer–Pavez–Louppe 2015 §2.2 Theorem 1、式(2.4)、(2.10)，§2.3](https://arxiv.org/pdf/1506.02169) | 分类估计似然比的已有依据；本项目尚未实施该文单独校准程序 |
| deep neural network-based active user detection、binary cross entropy、sigmoid | [Sivalingam et al. 2021 §III-B式(11)–(12)后、§IV开头，PDF第4–5页](https://arxiv.org/pdf/2106.11198) | 神经网络AUD及逐设备BCE/sigmoid输出的通信先例，SCMA结构不移植为本项目已验证算法 |

## 2026-10-08：完整信道 score 与活动证据对照

当前定义见 [THEORY.md](THEORY.md)。full_score与activity_evidence_gaussian是软件配置标识；T1–T17是项目公式编号，不是文献中的新方法名称。

| 原词或忠实译名 | 原文定位 | 当前含义 |
|---|---|---|
| score-based generative priors、denoising score matching、second-order score matching | [Cai v2 §IV-A–C，式(43)–(54)](https://arxiv.org/html/2506.00581v2#S4) | 完整信道均值和二阶全样本平均迹；有限一阶下条件MSE由本文T9–T11说明 |
| pseudo AWGN observation model | [Cai v2 §IV-A 式(43)、§V-B1](https://arxiv.org/html/2506.00581v2) | 去噪模块的标量AWGN工作模型，实际有限AFDM查询为近似 |
| Gaussian approximation、device activity denoiser | [Cai v2 §III-B1–B2，式(26)–(30)](https://arxiv.org/html/2506.00581v2#S3.SS2) | 归一化活跃Gaussiansite的解析活动概率；Gaussiansite是项目操作描述 |
| density ratio estimation、class-probability estimation、logistic loss | [Menon–Ong 2016 §2.2、§3、§4.2，式(6)–(8)、(16)–(17)，页305–306](https://proceedings.mlr.press/v48/menon16.pdf) | 平衡活动分类的logit经训练先验校正得到密度比，再加入公开rho |
| damping | [Cai v2 §V-B1，式(57)–(58)](https://arxiv.org/html/2506.00581v2#S5.SS2.SSS1) | 本项目采用0.1新值权重的均值/方差算术插值，非Gaussian混合矩匹配 |

## 2026-10-08：至少一用户活跃的场景生成

Bernoulli先验的原定义参照[Cai v2 §II-B式(5)及§III Table II的p(αₖ)](https://arxiv.org/html/2506.00581v2#S2.SS2)。本项目以Σₖαₖ≥1为条件重抽活动向量，Z=1-(1-p)^K与边缘ρ=p/Z由条件概率直接计算；这是按用户要求预先定义的生成操作，不归称为参考论文使用的实验规则，不另命名算法。接收机的独立边缘工作近似及适用范围见[SYSTEM_MODEL.md](SYSTEM_MODEL.md)与[EXPERIMENT_PROTOCOL.md](EXPERIMENT_PROTOCOL.md)。

以下为原研究阶段的术语记录；其对应算法定义按当时版本保留。


## 2026-10-07：混合路线统一推导

当前混合路线定义见 [mixed_route/THEORY.md](mixed_route/THEORY.md)。
本轮 H1–H30 是项目公式编号，不是文献方法名；有限误差、投影改善条件、
Gaussian 评价量和查询分布变化的界均在正文直接证明。

| 原词或忠实译名 | 原文定位 | 本轮使用范围 |
|---|---|---|
| score-based generative priors、denoising score matching、second-order score matching | [Cai v2 §IV-A–C，式(43)–(54)](https://arxiv.org/html/2506.00581v2#S4) | H7–H11 使用完整实复坐标换算；有限 first 下二阶平均迹对应 F0 条件 MSE，不逐坐标认证 Hessian |
| rank-one、approximation of lower rank、singular value decomposition | 下列 Li–Gao–Xia、Eckart–Young 和 Ying 的已核对位置 | H12–H15 的受限估计和误差证明；物理秩一不推出后验均值秩一 |
| density ratio estimation、class-probability estimation、logistic loss | [Menon–Ong §2.2，p.305；§3式(6)–(8)、§4.2式(16)–(17)，p.306](https://proceedings.mlr.press/v48/menon16.pdf) | H17 的平衡 BCE、密度比和先验赔率修正；H18–H19 是本项目证明的有限误差和 AER 界 |
| total variation distance / 全变差距离；absolute continuity / 绝对连续 | [Sason–Verdú，§II-A定义1前段，p.7；§II-B式(55)–(58)，p.10，2016-12-06稿](https://arxiv.org/pdf/1508.00335) | H29–H30 的条件换测度与风险差；本文 TV=事件概率差的上确界，等于原文 \(\lvert P-Q\rvert/2\)。未声称已估得实际 MP 联合分布距离 |
| damping、pseudo AWGN、right-rotationally invariant | [Cai §V-B1，式(57)–(58)及前段](https://arxiv.org/html/2506.00581v2#S5.SS2.SSS1) | 两侧0.1递归参数插值、有限 AFDM cavity 的近似范围；不把局部误差界变成全局收敛证明 |

实际 cavity 的噪声能量、空间/AFDM相关性和单变量矩仅为已定义统计量，
不用新的算法名描述这些诊断，也不以有限诊断认证联合 Gaussian 性或独立性。

## 2026-10-06：两路线全几何训练与完整理论

本轮路线名称是项目内配置标识；新增操作按公式直接描述。完整来源与阅读范围见
[秩一路线SOURCES.md](route_rank_one/SOURCES.md)和[活动证据路线SOURCES.md](route_score_evidence/SOURCES.md)。

|原词或忠实译名|论文原文位置|本轮实际范围|
|---|---|---|
|score-based generative priors / 基于得分的生成先验；turbo message passing / turbo消息传递|[Cai v2 §I-A、§III、Algorithm 1–2](https://arxiv.org/html/2506.00581v2#S3)|两个模块反复交换Gaussian外信息，完整信道块由连续噪声score去噪；不要求每轮反向扩散采样|
|Tweedie's formula；denoising score matching / 去噪得分匹配|[Cai §IV-A–B，式(43)–(49)](https://arxiv.org/html/2506.00581v2#S4)|两路线R8–R11、E7–E10独立换算复方差v和实方差v/2，冻结有限均值与人口最优区分|
|second-order score matching / 二阶得分匹配|[Cai §IV-C，式(50)–(54)及式(54)后段](https://arxiv.org/html/2506.00581v2#S4.SS3)|当前两路线共用完整有限均值F0对应的平均迹目标；秩一路线在投影后复用为R28–R29说明的近似。专用投影风险回归属于可选操作，不将其输出命名为精确二阶score或Hessian|
|Gaussian projection、moment matching、extrinsic message / Gaussian投影、矩匹配、外信息消息|[Minka §2–3，式(5)–(6)、(9)–(12)，pp.363–364](https://tminka.github.io/papers/ep/minka-ep-uai.pdf)；[Cai §III，式(9)–(11)、(24)–(27)、(39)–(42)](https://arxiv.org/html/2506.00581v2#S3)|线性模块迹投影、Bernoulli混合矩与自然参数相除；固定秩一中心的Gaussian负对数密度最优方差由R18直接证明|
|rank-one、array response vector / 秩一、阵列响应向量|[Li–Gao–Xia §II-C，式(8)](https://arxiv.org/html/2207.11958v2#S2.SS3)|物理用户信道共同空间响应；估计投影不输入真实方向，也不保证改善精确MMSE|
|approximation of lower rank / 较低秩近似；singular value decomposition / 奇异值分解|[Eckart–Young 1936，原文题名及出版社摘要，pp.211–218](https://www.cambridge.org/core/journals/psychometrika/article/approximation-of-one-matrix-by-another-of-lower-rank/B29672E1EDD0FA1B7611D4DFAFC321B3)；[Ying §III-B，式(14)前](https://arxiv.org/html/2304.04484v1#S3.SS2)|R12–R14用空间Gram主特征向量实现最佳秩一近似，并直接给出证明；未声称核到Eckart–Young付费页内公式|
|density ratio estimation、class-probability estimation、logistic loss / 密度比估计、类别概率估计、logistic损失|[Menon–Ong §2.2 Table 1、§3式(6)–(8)，p.305；§4.2式(16)–(17)，p.306](https://proceedings.mlr.press/v48/menon16.pdf)|E15–E18的平衡BCE人口目标、训练赔率与部署活动率换算，有限误差另行评估|
|damping、pseudo AWGN、right-rotationally invariant / 阻尼、伪AWGN、右旋转不变|[Cai §V-B1，式(57)–(58)及前段](https://arxiv.org/html/2506.00581v2#S5.SS2.SSS1)|递归消息插值属于明确有限实现；未证明结构化AFDM满足随机矩阵大系统条件|
|orthogonal AMP / 正交近似消息传递|[Ma–Ping §III式(22)–(26)、§IV-B式(38)–(39)](https://arxiv.org/html/1602.06509)|路线⑫使用本项目MMV适配得到完整软初值，计入完整接收机成本；适配见[BASELINES.md](BASELINES.md)|
|Adam；cosine annealing / 余弦退火|[Kingma–Ba §2 Algorithm 1，p.2](https://arxiv.org/pdf/1412.6980)；[Loshchilov–Hutter §3式(5)，p.4](https://arxiv.org/pdf/1608.03983)|固定训练配方的优化器和单次学习率下降区间，不将其称为带warm restarts的完整SGDR，也不由训练预算推出优化收敛|

条件风险的平方分解、有限网络误差界、活动分数敏感性、正精度限制及给定固定点的关系，
分别由两路线正文明确证明，不包装成参考论文已给出的新定理或方法名。
本轮新增A的(R29d)–(R29g)、(R31a)–(R31e)和B的(E18a)、(E20a)–(E20e)沿用上述Gaussian评价量、
自然参数、KL、类别概率和条件矩表述，直接展示推导；没有将这些项目内条件界命名为既有算法。
A的(R31a)–(R31e)直接定义与函数空间最小损失的差，再由条件平方分解及Cauchy–Schwarz连接
有限两网络、投影残差和读数误差；不是Cai或其他参考论文原已给出的结论，也不新增网络名称。

bootstrap / 自助重抽样的基本操作核对于[Efron 1979 §2，式(2.4)–(2.5)，pp.2–4及Method 2](https://sites.stat.washington.edu/courses/stat527/s13/readings/ann_stat1979.pdf)。
本轮把一个场景下所有参数点和方法组成同一个观测向量，在每个实验轴内有放回抽取相同场景数，
不同轴独立抽取；重新计算总错误/总用户数及总误差能量比，取5000次的2.5%和97.5%分位数。
该具体配对和分轴方式是本项目预定的实验操作，不声称引用论文直接提供了本项目的覆盖率保证。
零真值能量导致的无定义重抽样次数保留；零活动差异的退化区间不能证明总体等效，未作统计非劣宣称。

## 2026-10-05：Ding图3的活动错误率

active device error rate（ADER）/ 活动设备错误率，原词及定义见
[Ding第5页§IV-B与Fig.3(b)](https://doi.org/10.1109/TVT.2026.3729877)。
二值活动下为(MD+FA)/K，分母为全部候选用户数；项目沿用AER标识，固定K面板上的合计比值与该定义一致。
原图读数只记为近似值，GAMP-SBL与pro. GNN-ASPL分别按紫色菱形、红色圆形辨认；
核对记录见[原论文AER比较](../archive/two_candidate_mainline_20261006/workspace/experiments/ding_paired80_20261005/DING_AER_COMPARISON.md)。

## 2026-10-05：已知噪声条件下的 Zhang 更新

当前配置固定复高斯似然的噪声精度γ=1/σ²；模型含义见Zhang2023第15058页式(2)–(4)，
保留第15059页Algorithm1的GAMP和α学习，跳过式(19)的γ更新，是项目明确的已知噪声适配。
不命名为新算法，也不声称作者已经采用本项目的固定噪声、阻尼和迭代上限。
对照算法共同使用生成噪声分布参数，不是实现噪声样本能量；活动判决继续使用Ding式(27)。
实施和参数来源见[Ding对齐说明](../archive/two_candidate_mainline_20261006/workspace/docs/DING_BASELINE_ALIGNMENT.md)。

## 2026-10-05：SBL 噪声学习与阻尼后的矩

Gaussian posterior / 高斯后验、posterior mean and covariance / 后验均值与协方差，以及
EM noise estimate / EM噪声估计，核对 Gerstoft et al., *DOA Estimation in heteroscedastic noise*,
Signal Processing 161 (2019), pp.63–73，式(17)–(18)及第69页§5.4.1式(49)。
该文报告其应用中EM噪声估计偏低，见第69页式(49)后及第70页图8；
不能把这一应用结论扩展为所有SBL必然低估或本项目唯一根因。
[机构存档全文](https://pure.tudelft.nl/ws/portalfiles/portal/96687021/1_s2.0_S016516841930101X_main.pdf)

本项目将α更新改用同一标量去噪器的未阻尼均值和方差，只描述此操作，不另造算法名称。
Zhang2023第15058–15059页式(9)–(10)、(16)提供其后验矩/精度更新来源；阻尼位置是项目明确的适配选择。
单步GAMP的近似后验不等于精确E步，不能由矩配对推断似然单调性或噪声估计一致性。
固定超参数下的条件高斯恒等式及两种空间的计算见
[数学核查](../archive/two_candidate_mainline_20261006/workspace/experiments/ding_baseline_diagnosis_20261005/math_review.md)。

Nannuru et al., *Sparse Bayesian learning with uncertainty models and multiple dictionaries*,
作者稿第5页§III-E式(43)、第6页§IV-A记录噪声向零偏差及使用已知源数的适用条件。
本项目没有据此引入真实活跃人数或真实支持。[作者稿](https://arxiv.org/pdf/1704.00436)

## 2026-10-05：Ding 所引 GAMP-SBL 与系数活动判决

`GAMP-SBL` 在 Ding 第5页 IV.B 的具体引用是 Zhang 等，TVT 2023，DOI
[10.1109/TVT.2023.3280919](https://doi.org/10.1109/TVT.2023.3280919)，第15058页式(3)–(4)、
第15058–15059页式(9)–(19)及Algorithm 1。新模块按该单轮消息与超参数更新顺序进行复数适配；
Gamma采用shape–rate参数化，CN模型对应的精度更新为本项目显式推导，不照抄原文实数的1/2系数。
现有Al-Shoukairi来源的共享行方差MMV版本保留独立名称和历史结果，不能与Zhang来源混称为同一具体实现。

活动判决操作依据[Ding 2026，第4页式(27)](https://doi.org/10.1109/TVT.2026.3729877)：
系数块平均平方范数除以所有用户中的最大值，再按大于等于门限判决。本文只描述这个操作，
不另创方法名称；`gamp_sbl_zhang2023_complex`仅为项目配置标识。
Ding未明确所有基线均用式(27)，所以将其用于本轮基线是声明的比较选择。
公式、缺失参数、共同真实跨帧相位条件及验证记录见[DING_BASELINE_ALIGNMENT.md](../archive/two_candidate_mainline_20261006/workspace/docs/DING_BASELINE_ALIGNMENT.md)。

2026-10-05诊断用语更正：`score_learning_pilot_20261004/query_control.py` 的末轴矩阵统计对应输入坐标，
不对应阵元。新的[同信道AWGN对照](../results/evidence_score_awgn_20261005/REPORT.md)按阵元轴计算
`E Eᴴ/L`，直接称为“未去均值阵元二阶矩”。此处是矩阵操作的字面说明，不引入新方法名称；
只有独立零均值AWGN下其期望为方差乘单位阵，实际非零均值残差不能直接作总体协方差解释。
Tweedie和伪AWGN的论文出处仍为下表 Cai §IV-A式(44)–(45)、§III-B式(20)及§V-B1。

术语采用论文原词或忠实中文译名。项目中的“原完整score＋秩一处理”是具体操作说明，不作为已有论文算法名称。

2026-10-05 的[旧网络比较](../archive/two_candidate_mainline_20261006/workspace/experiments/old_network_shared_variance_20261005/PROTOCOL.md)沿用 Cai §III-B 式(24)–(30)的 Gaussian 外信息和活动更新，以及已登记的空间秩一操作。协议中的消元似然比由同一 Gaussian 密度直接代数化简；依赖当前查询的 Gaussian 因子不自动等于生成先验的精确边缘似然。`old_full`、`old_rank_one`仅为实验配置标识，不作为新方法名称。

## 2026-10-04：完整推导与当前修复

2026-10-04修复定义见 [SCORE_MP_COMPLETE_DERIVATION.md](../archive/two_candidate_mainline_20261006/workspace/docs/SCORE_MP_COMPLETE_DERIVATION.md) 和 [SCORE_MP_TRAINING_TARGETS.md](../archive/two_candidate_mainline_20261006/workspace/docs/SCORE_MP_TRAINING_TARGETS.md)。2026-10-05当前旧网络测试的具体读出、初始化与共享方差调度另见 [OLD_SCORE_SHARED_MP.md](OLD_SCORE_SHARED_MP.md)，沿用本页已登记的术语和来源，不新命名算法。以下限定优先于后文历史候选的训练建议。

|术语或直接操作说明|论文原文位置|当前使用范围|
|---|---|---|
|expectation consistent (EC) approximate inference / 期望一致近似推断|[Opper–Winther 2005，§3式(13)–(19)，pp.2182–2183](https://www.jmlr.org/papers/volume6/opper05a/opper05a.pdf)|式(C5)–(C7)的两个模块、三个归一化分布及均值/二阶矩驻点条件。§4.1脚注3允许先验因子作用于不相交变量块；不把脚注解释为本文投影更新的收敛定理|
|block-uniform diagonalization / 分块统一对角化|[Rangan–Schniter–Fletcher，GEC §II-A式(9)，p.2](https://arxiv.org/pdf/1602.07795)|每用户只保留平均协方差迹；并未保留完整协方差。该文特定条件下的定理不无条件移用于本项目结构化矩阵与投影更新|
|Gaussian projection、moment matching、extrinsic message / Gaussian投影、矩匹配、外信息消息|[Minka §2式(5)–(6)、§3式(9)–(12)，pp.363–364](https://tminka.github.io/papers/ep/minka-ep-uai.pdf)；[Cai §III-B式(24)–(27)、(41)–(42)](https://arxiv.org/html/2506.00581v2#S3.SS2)|式(C8)–(C11)的线性块投影及自然参数相除。受限Gaussian交叉熵最小化是式(C15)–(C18)直接定义的操作，不冒充已有命名算法，也不把投影后固定点称为原EC驻点|
|denoising score matching / 去噪得分匹配；second-order score matching / 二阶得分匹配|[Cai §IV-A–C式(44)–(54)，以及式(54)后梯度隔离说明](https://arxiv.org/html/2506.00581v2#S4)|一阶DSM和冻结一阶后的条件风险回归。风险是二阶迹目标的相应参数化，有限均值偏差显式保留；不是有限网络Jacobian迹的无条件等价物|
|density ratio estimation、class-probability estimation / 密度比估计、类别概率估计|[Menon–Ong 2016，§3式(6)–(9)、§4.2式(16)–(17)，pp.305–306](https://proceedings.mlr.press/v48/menon16.pdf)|式(TT11)–(TT14)对同一归一化信道律进行BCE，训练赔率校正后得到活动证据。有限输出是密度比估计，不自动成为独立归一化先验|

正site必要性、受限交叉熵的显式最优解、投影后固定点以及有限统计误差界，均是主文档和训练文档给出的直接推导，不另造缩写或冠以新的既有方法名称。两份文档的同一模型独立复核用于发现问题，不作为不同模型或外部审稿人背书。

2026-10-04 的[消息更新核对](../archive/two_candidate_mainline_20261006/workspace/docs/CAI_SCHEDULE_AUDIT.md)沿用上述 Gaussian projection、extrinsic message、moment matching 与 damping。跨用户及频率平均方差是对 [Cai §III-B 式(23)、(38)及式(38)后说明](https://arxiv.org/html/2506.00581v2#S3.SS2)的直接操作描述；作者固定提交对应条件方差 L178–181、混合方差 L195–197，保留天线维度。当前逐用户方差投影与这一规则不等价，不把它们描述成仅波形不同的同一实现。源码 SHA、逐环节定位与结论边界见审计记录。

2026-10-05 的共享标量方差比较沿用同一 Gaussian projection / moment matching 定义，式(C22)–(C27)直接给出全局平均迹、Gaussian 相除和两个方差汇总顺序；不另命名算法。条件方差先平均参照 Cai 式(23)、(38)，本实现额外平均天线维度，明示为冻结标量辅助网络下的近似对照。\(c_1-c_0=-\operatorname{Cov}_K(p,\tau)\)是直接代数恒等式；不把原始矩残差未满足的收敛状态称为原先验的标准EC驻点。见[完整推导第10节](../archive/two_candidate_mainline_20261006/workspace/docs/SCORE_MP_COMPLETE_DERIVATION.md)与[实验协议](../archive/two_candidate_mainline_20261006/workspace/experiments/shared_variance_20261004/PROTOCOL.md)。

| 术语 | 论文及定位 | 本项目含义 |
|---|---|---|
| joint activity detection and channel estimation / 联合活动检测与信道估计 | Cai §II-B | 用户活动与完整信道联合估计 |
| score-based generative models / 基于得分的生成模型；denoising score matching / 去噪得分匹配 | Cai §IV-B式(46)–(49)、§IV-C式(51)–(54) | 保留原两score网络及训练目标 |
| non-separable denoiser / 不可分离去噪器 | Cai §I-A、§III-B | 完整矩阵联合去噪 |
| Tweedie’s formula / Tweedie公式；conditional mean / 条件均值 | Cai §IV-A式(44)–(45) | 理想AWGN条件矩关系，有限网络作替代 |
| Gaussian projection / Gaussian投影；extrinsic message / 外信息消息 | Cai §III-B式(17)、(24)–(30)、(35)–(42) | Gaussian近似中的均值、方差与活动反馈 |
| linear MMSE estimator / 线性最小均方误差估计 | Cai §III-A式(7)–(8)及说明 | 使用实际AFDM算子的通用LMMSE形式 |
| posterior distribution / 后验分布；prior distribution / 先验分布 | Cai §II-B式(5)、§III-B式(21)–(23) | SYSTEM_MODEL式(S1)–(S2)分别给定物理条件先验与训练边缘先验，未假定二者相等 |
| pseudo AWGN observation / 伪AWGN观测 | Cai §III-B式(20)、§V-B1 | THEORY式(T2)–(T4)区分有限线性外信息与独立标量AWGN替代 |
| rank-one structure / 秩一结构；array response vector / 阵列响应向量 | Li–Gao–Xia §II-C式(8)；Ying §II-B式(1)前角扩展说明 | 同一用户各路径共同空间响应 |
| singular value decomposition / 奇异值分解 | Ying §III-B式(14)前 | 保留估计矩阵最大奇异值分量 |
| relation matrix / 关系矩阵 | Picinbono 1996 §II式(1)、(8)–(9) | 完整复数二阶信息之一，proper Gaussian反馈省略 |
| deep unfolding / 深度展开 | [Cai v2 §I-B2第一段](https://arxiv.org/html/2506.00581v2)；[Borgerding–Schniter–Rangan，§V-A–B、图7，第8–9页](https://arxiv.org/pdf/1612.01183) | 将有限轮消息传递写成可训练层，用信道、活动和观测样本训练。2026-10-04下一步建议为在实际多轮MP查询上联合训练，保留score先验与已知线性算子；尚未实施，不等于已验证AFDM增益。实际非AWGN查询上的监督读出不自动成为原AWGN模型的精确后验，也不移植原论文的性能或收敛结论 |
| damping / 阻尼 | [Cai §V-B1式(57)–(58)、算法2第7/17行](https://arxiv.org/html/2506.00581v2#S5.SS2.SSS1)；[作者实现第104–119行](https://github.com/chang-cai/score-massive-connectivity/blob/0c75680c966dcb8e46250de146f4c27e9294c283/main_stmp_jadce.py#L104-L119) | 有限维消息参数插值。作者代码用上一轮已阻尼的均值／方差，两方向首轮均不阻尼；论文公式字面用上一轮raw外信息，二者分别记录。完整推导原候选仅作反馈自然参数0.2阻尼；[本轮固定权重对照](../archive/two_candidate_mainline_20261006/workspace/experiments/cai_damping_20261004/PROTOCOL.md)比较两个方向的均值／方差阻尼及上述历史定义。方差参数插值不是加权随机噪声的精确方差；固定点关系不等于收敛保证。此前linear_damping候选属于另一实现 |
| Channel Power Normalization / 信道功率归一化 | [Cai v2 §V-B2式(59)–(65)](https://arxiv.org/html/2506.00581v2#S5.SS2.SSS2) | 论文采用逐样本单位功率训练，并在推断中由伪观测估计功率后缩放输入、还原输出。此前候选采用固定全局RMS训练；2026-10-04的52条件隔离实验使用NEW一阶100轮及辅助104轮权重，加入该训练分布的每用户尺度族，不能算作当前旧first100/second50的功率对照，也未进行单位功率重训，见[实验结果](../results/score_mp_power_20261004/REPORT.md)。式(59)的有限样本能量减噪应解释为功率估计；在独立零均值AWGN替代模型下相应等式对条件期望成立。用户尺度须同时用于条件均值、条件方差及活动似然比。核对的公开脚本提交0c75680c966dcb8e46250de146f4c27e9294c283未实现论文这一归一化流程，公式与代码版本分别记录；固定功率恒等式与未知功率近似另见[一致性审查](../archive/two_candidate_mainline_20261006/workspace/docs/NORMALIZED_SCORE_POWER_REVIEW.md) |
| expectation propagation / 期望传播；moment matching / 矩匹配 | [Minka §2式(5)–(6)、§3式(9)–(12)，第363–364页](https://tminka.github.io/papers/ep/minka-ep-uai.pdf) | SCORE_MP_DERIVATION逐用户保留均值和协方差迹，Gaussian消息相除；明确区别于完整块协方差EP，不宣称全局收敛 |
| probability flow ODE / 概率流常微分方程；reverse-time SDE / 反向时间随机微分方程 | [Song等 §3式(6)、§4.3式(13)、附录D.1](https://arxiv.org/html/2011.13456v2) | 生成归一化信道分布；复噪声方差v对应每实坐标v/2，系数由此换算；有限场的生成分布与其Gaussian平滑score须另核对 |
| path sampling / 路径采样；thermodynamic integration / 热力学积分 | [Gelman–Meng §2.1式(6)–(7)，第165页；§2.2式(12)，第166页；§2.3式(15)，第167页](https://sites.stat.columbia.edu/gelman/research/published/path2.pdf) | SCORE_MP_DERIVATION式(33)–(45)对同一生成先验的归一化常数沿逆噪声方差积分；局部矩由score获得，不将归一化恒等式命名为新算法 |
| Hutchinson's trace estimator / Hutchinson迹估计 | [FFJORD §3.1式(7)–(8)，第4页](https://arxiv.org/pdf/1810.01367) | 用随机向量的Jacobian二次型估计同一score均值导数的迹；包含探针误差，不等同精确方差 |
| Gaussian mixture / Gaussian混合 | [Vila–Schniter §II式(3)，第2页](https://arxiv.org/pdf/1207.3107) | 活动修复开发中的固定分量、总权重为1的显式代理先验；UPA/AFDM完整模板似然由ACTIVITY_REPAIR式(A1)–(A2)直接推导，不复现其标量GM-GAMP算法 |
| likelihood ratio / 似然比；classification probability / 分类概率 | [Cranmer–Pavez–Louppe §2.2式(2.10)，正文第6页；附录A式(A.1)–(A.6)，第34–35页](https://arxiv.org/pdf/1506.02169) | 对同一训练信道分布生成的活动／非活动AWGN样本进行平衡分类；理想分类logit为对数似然比，接收机用实际伯努利活动率校正先验赔率 |
| cross-entropy / 交叉熵；calibrated classifier / 经校准的分类器 | [Cranmer–Pavez–Louppe 附录A末段，第35页；§2.3，第7–8页](https://arxiv.org/pdf/1506.02169) | 活动读出使用二元交叉熵。有限分类器不自动获得精确似然比或校准概率；压缩特征保留完整似然比所需条件见该文§2.2定理1及式(2.4)，第5页，本项目没有假定其成立 |
| density ratio estimation / 密度比估计；class-probability estimation / 类别概率估计 | [Menon–Ong 2016 §3式(6)–(9)、§4.2式(16)–(17)，第305–306页](https://proceedings.mlr.press/v48/menon16.pdf)；[Hermans–Begy–Louppe 2020 §2式(8)–(11)、§3.1及附录B](https://proceedings.mlr.press/v119/hermans20a/hermans20a.pdf) | SCORE_MP_DERIVATION第17节直接学习同一先验的活动对数似然比；纠正训练类别先验并加入实际活动率。理论最优分类器与有限训练、饱和概率及实际MP输入的校准区别记录于该节 |
| cosine annealing / 余弦退火 | [Loshchilov–Hutter 2017 §3式(5)，第4页](https://arxiv.org/pdf/1608.03983) | 新完整训练使用单个余弦学习率下降区间，随后保持正的学习率下限；不采用论文中的周期重启，也不称为完整SGDR复现 |
| 对普通平均后的条件方差设置下限（直接操作说明） | [Cai作者实现](https://github.com/chang-cai/score-massive-connectivity/blob/0c75680c966dcb8e46250de146f4c27e9294c283/main_stmp_jadce.py#L177-L185) 第177–185行；方差来自论文式(56) | 在用户平均后将复数条件方差下限设为10⁻⁴；转换到当前归一化坐标，保留原始方差与触发记录 |
| SOMP / 同时正交匹配追踪 | Tropp–Gilbert–Strauss Algorithm 3.1、§3.2 | 固定标准基线 |
| GAMP-SBL（历史实现） | Al-Shoukairi–Schniter–Rao §II-B、§III-B、Table II | 历史EM复数MMV适配；现用Zhang Algorithm 1的依据见本文件前部 |
| OAMP-MMV | Ma–Ping式(38)–(39)、附录C；Ying §III-B Algorithm 1 | 本项目固定共同支撑BG适配，非作者逐点复现声明 |
| AMP-NNSPL（历史适配） | Meng式(17)；Vila Table I | 历史邻域支撑和阻尼适配；现用Meng Algorithm 1独立列实现的依据见本文件前部 |
| signal-to-noise ratio / 信噪比 | [Ding 2026 §IV-B第5页SNR公式、§IV-A及图3/4](https://doi.org/10.1109/TVT.2026.3729877)；[Cai作者实现第273行](https://github.com/chang-cai/score-massive-connectivity/blob/0c75680c966dcb8e46250de146f4c27e9294c283/main_stmp_jadce.py#L273) | Ding写SNR=‖SZ‖²_F/(MLσ²)，前文式(9)的无噪声接收信号记为ΨZ，属于全用户叠加接收功率口径；图3/4覆盖0–20dB。本项目采用同类定义并逐场景按实际无噪声接收功率设置噪声，当前面板为0/2/4/6dB。Ding未给出明确的逐样本／期望功率噪声校准步骤，尚未核到作者生成代码，不能据公式宣称逐点复现。Cai所核公开实现按P/δ²设置横轴并固定δ；对比须统一信道与导频功率归一化，不能直接比较同名SNR数值 |

条件平方误差分解、秩一输出限制下的最优估计、原二阶读出复用及Gaussian分数的公式为 [METHOD.md](METHOD.md)的直接推导。真实信道秩一不等于未知方向后验均值秩一；原二阶读出不自动等于投影后精确covariance；Gaussian活动分数不自动等于原学习先验精确似然比。

2026-10-03的共享特征试验直接描述操作，不登记新的算法名称。正值方差读出以秩一估计的条件平方误差为训练目标，沿用THEORY式(T13)–(T14)的Gaussian评价量；它是有限估计器的误差近似，不改称精确后验协方差。同一训练分布上的多个读出也不自动满足Tweedie导数恒等式。统一的目标分布、分类最优解和现有有限近似的区别见 [本轮研究记录](../results/unified_prior_20261003/REPORT.md)。

2026-10-04的直接统计实现沿用density ratio estimation与Cai second-order score matching，不登记新算法名称。SCORE_MP_DERIVATION式(A8)–(A10)把Cai §IV-C式(52)–(54)的完整迹损失重参数化为正值条件平方误差；有限一阶网络带来的均值平方偏差显式保留。该实现的条件均值采用完整score输出，不沿用旧共享特征试验的秩一风险目标。

2026-10-04的[逐用户方差反馈实验](../archive/two_candidate_mainline_20261006/workspace/experiments/user_variance_20261004/PROTOCOL.md)沿用上述Gaussian projection、extrinsic message和Minka的moment matching术语，不另命名算法。给定逐用户Gaussian先验，线性均值与协方差按LMMSE求解，再取每用户块的协方差迹；Gaussian消息相除参照Minka §2式(5)–(6)、§3式(9)–(12)，第363–364页及Cai §III-A、§III-B。保留原网络、二阶输出的普通平均、秩一处理及Gaussian site活动证据；不把有限score读出、数据相关site或逐用户迹投影称为精确生成先验后验，也不据此宣称独立AWGN或全局收敛。本实验与历史主线均在均值和方差上作0.2算术阻尼；此前新训练score_mp候选的反馈自然参数阻尼属于另一版本。

[THEORY.md](THEORY.md)式(T1)–(T22)沿用上述术语并直接证明所列恒等式和界。期望负Gaussian对数密度是式(T13)写出的评价量，不将秩一奇异先验与全维Gaussian的比较称为有限密度KL散度；未将这些推导包装为新的既有方法名称。Cai原二阶迹损失的依据为§IV-C式(52)–(54)，其方差权重说明在式(54)后；本项目实复换算见式(T9)。

来源：[Cai v2](https://arxiv.org/html/2506.00581v2)，[Li–Gao–Xia](https://arxiv.org/html/2207.11958v2)，[Ying](https://arxiv.org/html/2304.04484v1)，[Picinbono](https://doi.org/10.1109/78.485954)，[SOMP](https://tropp.caltech.edu/papers/TGS05-Algorithms-Simultaneous-I-preprint.pdf)，[GAMP-SBL](https://arxiv.org/html/1703.03044)，[OAMP](https://arxiv.org/html/1602.06509)，[Meng](https://arxiv.org/html/1601.00543v1)，[Vila](https://arxiv.org/html/1412.2005)，[Ding](https://doi.org/10.1109/TVT.2026.3729877)。完整历史术语核查保存在本次归档。

## 2026-10-04：实际去噪器导数与反馈

| 术语 | 原文位置 | 本项目使用范围 |
|---|---|---|
| vector approximate message passing (VAMP) / 向量近似消息传递；divergence / 散度 | [Rangan–Schniter–Fletcher，Algorithm 2第5–8行，第4页；§III-B，第5页；§IV大系统分析](https://arxiv.org/pdf/1610.03082) | 对完整去噪器求平均导数，再构造外信息；不声称本项目结构化有限维矩阵满足论文全部状态演化条件 |
| denoising-based vector AMP (D-VAMP) / 基于去噪的向量近似消息传递 | [Schniter–Rangan–Fletcher，第1–2页](https://arxiv.org/pdf/1611.01376) | 将学习去噪器用于VAMP的文献依据；当前实验是针对本项目复数矩阵和活动概率的适配，不冒充作者实现 |
| divergence-free / 无散度 | [Ma–Ping v3，§III-G式(25)、Proposition 2式(26)，第5页](https://arxiv.org/pdf/1602.06509v3) | 只在所列理论条件或固定系数局部微分下使用；经验系数、有限维和截断情况下明确称近似 |

活动概率的算术阻尼只用操作本身描述，不另取方法名称。`DENOISER_FEEDBACK_DERIVATION.md`给出同一Bernoulli分布族中的概率插值及其固定点关系，不将其称为新的先验。

## 2026-10-04：训练统计量审查

[STATISTICAL_AUDIT_AND_RETRAINING.md](../archive/two_candidate_mainline_20261006/workspace/docs/STATISTICAL_AUDIT_AND_RETRAINING.md)沿用Tweedie、Cai second-order score matching、likelihood ratio、Hutchinson trace estimator与Gaussian projection术语。有限一阶条件风险、实际均值导数的迹和精确后验协方差的区别由式(S5)直接说明；式(S12)的迹回归与式(S13)的证据梯度训练项是本项目明确写出的操作，不包装成已有的命名方法。Cai的有限一阶替代与停止梯度依据为§IV-C式(52)–(54)及式(54)后段；它不是对有限网络Jacobian迹无条件等价的声明。

|术语|原文位置|本轮含义|
|---|---|---|
|Brier score / Brier评分|[Gneiting–Raftery 2007，§3.1 Example 1，第363页；§3.2 Table 1，第365页](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf)|二分类概率的平方误差，取Table 1奖励的负号作为损失；配对平衡样本按实际活动率0.1重加权。该评分同时受多个因素影响，不把其降低单独称为概率已校准|
|bootstrap / 自助法|[Efron 1979，§2式(2.4)–(2.5)，第3页](https://blogs.helsinki.fi/bk-club/files/2012/05/Efron_Bootstrap_AS1979.pdf)|每个固定噪声档以128个配对信道为单位有放回抽样2000次，记录新旧误差能量比的dB差值经验分位范围；用于本轮描述性不确定性，不据此宣称独立确认或多重比较的总体显著性|

式(S8)按Gaussian核的方差参数直接求导，不将少数点的微分一致性检查表述成全局密度存在或归一化证明。精确有限先验只作确定性数学控制，不接入实际接收机。

## 2026-10-04：全量训练前的完整MP审查

[PRETRAINING_THEORY_AUDIT.md](../archive/two_candidate_mainline_20261006/workspace/docs/PRETRAINING_THEORY_AUDIT.md)沿用 expectation propagation、moment matching、Gaussian projection 与 extrinsic message。site 指Minka §3式(9)–(12)、第364页的因子近似；相除更新见式(12)，不要求每个因子单独归一化。式(P9)–(P12)是该Gaussian因子在本项目复数自然参数下的直接展开，不另命名算法。联合精度与投影外信息精度的正性条件由该展开直接给出；不把它们说成普遍EP收敛定理。Minka §3.3、第365–366页讨论固定点与非收敛；Cai §V-B1限定伪AWGN的大系统、right-rotationally invariant随机算子条件。本轮枚举有限先验的精确后验仅作数学对照，独立于物理生成先验和学习性能。出处：[Minka](https://tminka.github.io/papers/ep/minka-ep-uai.pdf)，[Cai](https://arxiv.org/html/2506.00581v2#S5.SS2.SSS1)。


## 2026-10-05：活动证据的导数正则候选

[SCORE_MP_TRAINING_TARGETS.md](../archive/two_candidate_mainline_20261006/workspace/docs/SCORE_MP_TRAINING_TARGETS.md)第8.1节沿用 Tweedie formula、density ratio estimation 和 binary cross-entropy，不另命名算法。式(TT25)直接描述冻结完整score教师、仅在活动AWGN输入上附加平方导数误差的操作；其尺度关系依据[Cai §IV-A式(44)–(45)](https://arxiv.org/html/2506.00581v2#S4.SS1)，分类密度比定义依据[Menon–Ong §3、§4.2式(6)–(9)、(16)–(17)](https://proceedings.mlr.press/v48/menon16.pdf)。式(TT26)是本项目在所列比较函数和可积条件下由BCE超额风险非负及加权L2三角不等式推出的界，不归称为Cai已有定理。有限教师、有限容量、共享特征使原风险输出作废等限制见[数学审查](../results/evidence_consistency_20261005/MATH_REVIEW.md)。

## 2026-10-05：活动证据的能量函数参数化

后续[SCORE_MP_TRAINING_TARGETS.md第8.3节](../archive/two_candidate_mainline_20261006/workspace/docs/SCORE_MP_TRAINING_TARGETS.md)只沿用binary cross-entropy及density ratio estimation，
来源为[Menon–Ong §2.2–3、式(6)–(8)，第305页](https://proceedings.mlr.press/v48/menon16.pdf)。
在固定网络上最小化仅依赖噪声的附加常数，是式(TT29)直接定义的标量优化操作，不作为新的已有方法名称。
其平均类别概率条件与密度归一化不同；该区别由文中两点反例直接核对。
第8.6节将相同操作用于固定的完整观测与旧score均值输入，继续沿用上述术语和来源。
只检验加性logit偏移，不把它称作已经完成所有概率校准，也不把同一方差下的分数排序视为完整MP性能。

|术语|原文位置|本轮使用范围|
|---|---|---|
|energy parameterization / 能量函数参数化；pre-conditioning / 预条件|[Thornton等，2025，§3.3未编号预条件式、式(11)–(12)，PDF第5页](https://arxiv.org/pdf/2502.12786v1)|向量网络与输入的内积构成标量势，保留h+J_h^T y完整梯度；TT27独立换算复噪声尺度。未复现其教师初始化或生成采样，也不引用其ODE结论作为MP保证|
|denoising score matching / 去噪得分匹配|[Vincent，2011，§4.2式(4.3)–(4.5)，p.1667](https://gwern.net/doc/ai/nn/diffusion/2011-vincent.pdf)|TT28的干净标签目标经Tweedie换元是正噪声权重的DSM；相对旧目标改变了权重，有限样本及优化误差保留|

Gaussian项只称固定代数参考；残差目标log(q_v/qG_v)仍属于同一个物理P_H，不将其命名为新先验或新算法。
旧标量头的v趋零限制、TT28的残差二阶矩与干净目标常数分解均为本项目明确条件下的直接推导，
不归称为上述论文已有定理，也不据此解释全部开发误判。来源阅读和限制记录见[本轮复核](../results/evidence_parameterization_20261005/MATH_REVIEW.md)。

## 2026-10-05：固定噪声下对输入积分的公式审查

[下一项推导](../results/evidence_constant_20261005/NEXT_SCORE_PATH_DERIVATION.md)沿用
Tweedie’s formula / Tweedie公式、conditional mean / 条件均值与 likelihood ratio / 似然比。
其起点核对于[Cai §IV-A式(43)–(45)](https://arxiv.org/html/2506.00581v2#S4.SS1)；
复噪声方差转为实坐标方差后的系数、固定噪声下沿输入积分、Jacobian不对称项、
径向与横向方向的区别及Gaussian Monte Carlo相对方差均为文中直接推导。
“固定噪声下对输入积分”只描述式(2)的操作，不作为已有命名算法，
也不将其等同于已登记的沿噪声方差积分或归称为Cai原活动更新。

[固定输入积分诊断](../archive/two_candidate_mainline_20261006/workspace/experiments/evidence_input_path_20261005/PROTOCOL.md)使用
Gauss quadrature / Gauss求积，依据[Golub–Welsch (1969) §1，pp.221–222；§2，pp.222–223](https://web.stanford.edu/class/cme335/spr11/S0025-5718-69-99647-1.pdf)。
本轮取权函数1、区间[-1,1]的规则，再用t=(x+1)/2、w_new=w/2换至[0,1]。
该规则的多项式精确性不等于有限神经网络积分已达到给定误差；本轮仅报告8/16/32/64阶的变化，
不将阶数差当作论文中需要额外光滑性和导数控制的余项界。节点计算调用现有数值库，未宣称复现论文全部算法。

[同一证据函数的均值读出](../results/evidence_input_path_20261005/NEXT_JOINT_READOUT.md)及训练目标第8.4节
继续沿用Tweedie formula、conditional mean、binary cross-entropy与denoising score matching。
均值和二阶系数依据上述Cai §IV-A式(43)–(45)的实复换算；联合风险分解与有限均值的条件平方偏差
由文中公式直接给出，不包装成新的已有算法名称。有限读出的微分关系、先验归一化、二阶半正定和实测性能是不同命题。

## 2026-10-05：完整观测与冻结 score 均值输入活动网络

[本轮协议](../archive/two_candidate_mainline_20261006/workspace/experiments/evidence_score_input_20261005/PROTOCOL.md)继续使用 density ratio estimation、
class-probability estimation 与 binary cross-entropy，依据[Menon–Ong 2016 §2.2–3，式(6)–(8)，p.305](https://proceedings.mlr.press/v48/menon16.pdf)。
在完整r之外拼接它的确定性函数F_theta(r,v)，不改变给定v的活动条件概率，是TT32直接推导；
不另取方法名，也不将低维能量摘要默认称为充分统计量。
同一先验的有限统计量分别学习与有限误差的边界参照[Cai §IV-A、IV-C，式(43)–(45)、(52)–(54)](https://arxiv.org/html/2506.00581v2#S4.SS3)；
不把有限导数完全相等作为该文要求，也不因添加特征而宣称获得新的Bayes信息。

## 2026-10-05：固定旧网络的 GAMP 调度对照

“damped GAMP / 带阻尼 GAMP”及“scalar stepsizes / 标量步长”核对于
[Rangan 等，§II-B、§II-C、式(7)及 Algorithm 2，PDF第3页](https://arxiv.org/pdf/1402.3210)。
[实验协议](../archive/two_candidate_mainline_20261006/workspace/experiments/evidence_score_gamp_20261005/PROTOCOL.md)使用其两个均值阻尼位置；
残差正负号换算为[Rangan，Algorithm 1式(5)–(8)，PDF第4页；§IV-B、IV-C，PDF第7页](https://arxiv.org/pdf/1010.5141)的约定。
旧网络的整块均值、有限二阶统计及多右端项共同方差是本项目的明确近似，
不称作上述算法及收敛定理的完整复现；恒模导频也不等于IID算子。

[逐用户条件方差的比较](../archive/two_candidate_mainline_20261006/workspace/experiments/evidence_score_moment_pool_20261005/PROTOCOL.md)沿用
Gaussian moment matching / Gaussian矩匹配以及条件方差、混合后验方差的既有定义。
[Cai §III-B1式(23)、§III-B3式(35)–(38)](https://arxiv.org/html/2506.00581v2#S3.SS2)
本身包含两次不同层级的方差汇总；本轮差值及下限顺序分解是[数学复核](../results/evidence_score_moment_pool_20261005/MATH_REVIEW.md)的直接推导，
不命名为新算法，也不归称为Cai原公式错误或其逐式复现。

[两侧逐用户 Gaussian 消息比较](../archive/two_candidate_mainline_20261006/workspace/experiments/evidence_score_user_variance_20261005/PROTOCOL.md)
继续沿用 Gaussian moment matching / Gaussian 矩匹配及 extrinsic message / 外信息消息。
线性后验、块迹投影和 Gaussian 相除的依据仍为上述 Minka §2–3、pp.363–364 与
[Cai §III-A–B，式(24)–(27)、(41)–(42)](https://arxiv.org/html/2506.00581v2#S3)。
本项目每用户保留一个方差的具体投影由[本轮数学核对](../results/evidence_score_user_variance_20261005/MATH_REVIEW.md)直接定义；
不将其归称为 Cai 每天线方差结构，也不另造方法名。

## 2026-10-05：活动率参数路径

[活动率参数路径](../archive/two_candidate_mainline_20261006/workspace/experiments/evidence_score_continuation_20261005/PROTOCOL.md)只描述预定的rho_t变化。
continuation / 延拓的原词与思想参照[Hale–Yin–Zhang，Rice TR07-07，§6–6.2，pp.22–23；Algorithm 1，p.24](https://optimization-online.org/wp-content/uploads/2007/07/1721.pdf)：
参数逐步达到指定值，并将已有迭代状态用于后续问题。本轮不逐阶段求解到收敛，不称为其FPC算法或严格解路径跟踪，
不将该文凸问题的收敛结论移用于本项目。prior probability / 先验概率及 damping / 阻尼
沿用[Cai §III-B2–3，式(28)–(38)，§V-B1，式(57)–(58)](https://arxiv.org/html/2506.00581v2)。
改变活动率与混合消息参数是不同操作；最终恢复原活动率的具体规则由本项目协议直接定义，不称Cai已采用。

## 2026-10-07：包含查询历史的阻尼与局部条件

[实际阻尼递归与推导](route_score_evidence/OUTER_DAMPING.md)沿用 damping / 阻尼、Gaussian
消息和固定点；均值/方差插值的依据仍为 Cai §V-B1式(57)–(58)，递归历史的实现对应文中所列作者源码。
新出现的 local stability / 局部稳定性与 linearization / 线性化，核对于
[Rangan–Schniter–Fletcher–Sarkar，arXiv:1402.3210v3，§V Definition 1，PDF第6页；Appendix B，式(47)–(54)，PDF第9–10页](https://arxiv.org/pdf/1402.3210v3)。
前者描述足够接近固定点的初始状态是否趋于该点，后者考察固定点附近的导数矩阵。
本项目(D4)–(D12)是按实际学习接收机及查询历史独立展开的公式，不移用该文的GAMP、严格凸性或固定步长收敛结论。
合成矩阵的稳定区间不是实际网络的导数或收敛认证。

[维数与线性外信息方差](route_score_evidence/LINEAR_VARIANCE_DIMENSIONS.md)继续沿用已登记的
Gaussian projection、extrinsic message、singular value decomposition 与 damping。
(V1)–(V4)是从本项目(E3)–(E5)及正噪声条件直接推导的秩/维数关系，不另命名定理或方法，
也不由这些关系宣称实际查询误差为独立Gaussian。

## 2026-10-08：非空 full_score 开发比较的 bootstrap 单位

bootstrap / 自助重抽样沿用 [Efron 1979 §2，式(2.4)–(2.5)，pp.2–4及Method 2](https://sites.stat.washington.edu/courses/stat527/s13/readings/ann_stat1979.pdf) 的有放回重抽样定义。当前非空开发配置在全部实验轴复用相同的8个场景种子；汇总比较将同一种子在所有轴、所有参数点及两个配对方法上的错误数、判决数和信道误差/真值能量组成一个观测向量，并以种子为单位整体重抽。单参数点比较也以场景为单位重抽。采用5000次重抽样的2.5%和97.5%分位数作探索性区间。用户判决数、参数条件数和独立场景数分别报告；开发结果的零差异退化区间不能证明等效或非劣。该具体配对方式由本项目的种子复用规则决定，其有限样本覆盖率尚未验证。

执行与数据身份见 [本轮清单](../results/full_score_nonempty_20261008_100345/MANIFEST.json)。此前各轮的重抽样规则仍按各自冻结协议解释。

## 2026-10-08：三个现用基线的来源与适配

本段绑定 [BASELINES.md](BASELINES.md) 的当前定义及 [BASELINE_QUALIFICATION.md](BASELINE_QUALIFICATION.md) 的资格证据；上面的历史条目按其当时版本理解。

| 术语/操作 | 原文依据与准确定位 | 当前含义与边界 |
|---|---|---|
| simultaneous orthogonal matching pursuit / 同时正交匹配追踪（SOMP） | [Tropp–Gilbert–Strauss 作者预印本](https://tropp.caltech.edu/papers/TGS05-Algorithms-Simultaneous-I-preprint.pdf)，§2.2 p.4、Algorithm 3.1 pp.6–7、§3.2 p.7；期刊2006，DOI 10.1016/j.sigpro.2005.05.030 | 复数字典，跨天线绝对相关之和、共同支撑、正交残差和支撑LS。64原子、DD网格与已知噪声残差值是项目设置。最新逐项核对见[SOMP_NNSPL_FIDELITY_RECHECK.md](../results/baseline_pilot_20261008/paper_reaudit/SOMP_NNSPL_FIDELITY_RECHECK.md)；共同支撑是原算法机制，不能据其多天线收益认定实现偏离原文。 |
| orthogonal AMP / 正交近似消息传递；de-correlated / 去相关；divergence-free / 无散度 | [Ma–Ping v3](https://arxiv.org/pdf/1602.06509v3)，§III-A式(14)–(15) p.3；§III-B式(16)–(18)、§III-C式(19)–(20) p.4；经验系数在§III-G式(25)、Proposition 2式(26) p.5；§IV-B式(38)–(39) p.6、Appendix C pp.11–12。期刊 DOI 10.1109/ACCESS.2017.2653119 | 当前复数 Hermitian 线性更新与标量后验迹外信息。不能据名称保证有限AFDM字典的state evolution或全状态收敛。 |
| orthogonal approximate message passing–multiple measurement vector / OAMP-MMV | [Ying等 arXiv v1](https://arxiv.org/html/2304.04484v1#S3.SS2)，§III-B式(10)–(25)、Algorithm 1 | 原词确有卫星JADCE文献出处。当前工作先验用一行共同 Bernoulli 变量和各向同性激活协方差、联合全部天线似然、共同率EM；推导见BASELINES。本项目参数学习和完整AFDM重构不称为Ying作者实现复现。 |
| Bernoulli–Gaussian / 伯努利–高斯；expectation maximization / 期望最大化（EM） | [Vila–Schniter](https://arxiv.org/pdf/1207.3107)，§II式(3)、§III；初始化§III-D式(70)–(71) | MMV共同支撑的CN密度、完整协方差及共同率/方差M-step由本项目直接推导并独立验证；公开用户活动率不等于字典行激活率。 |
| generalized approximate message passing / 广义近似消息传递；sparse Bayesian learning / 稀疏贝叶斯学习（GAMP-SBL） | [Zhang等2023原文](../references/zhang2023_gamp_sbl_grant_free_noma.pdf)，p.15058式(3)–(4)、(8)–(10)；p.15059式(11)–(19)、Algorithm 1；DOI 10.1109/TVT.2023.3280919 | 每列独立的单循环。按声明CN模型修正实高斯1/2项及平方记法，得到proper-complex精度目标；固定公开噪声为项目条件。不能混称为历史Al-Shoukairi共享行MMV算法。 |
| damping / 阻尼 | [Rangan等](https://arxiv.org/html/1402.3210)，Algorithm 1第8–13行、§II-B；[Al-Shoukairi–Schniter–Rao](https://arxiv.org/html/1703.03044)，Table I A3/A4/A7/A8 | 文献中的s/x均值阻尼和未阻尼方差具有直接依据；本次alpha目标0.2正插值、相对残差、采样窗口和保存状态重算认证是项目数值选择。其固定点保持不等于全局收敛。 |
| energy based activity detector / 能量活动检测 | [Ying §III-B式(24)–(25)](https://arxiv.org/html/2304.04484v1#S3.SS2)；历史相对系数能量见[Ding第4页式(27)](https://doi.org/10.1109/TVT.2026.3729877) | 当前三方法直接按完整重构H的平均能量与独立校准门限判决，不移用上述论文的具体检测值。Ding相对系数能量保留为历史模式与诊断。 |

`group_bg_common_rate`、`relative_state`、`RELATIVE_STATE_AND_WINDOW_STOP` 是代码中的配方/状态标识，不当作新的学术方法名。具体残差和停止量由公式与配置直接定义；未把数值判停改称收敛定理。论文书目、原文页码、独立微型控制和当前原生物理场景的证据分别存档。

原细网格资格阶段三方法的DD网格时延步长统一为0.25、Doppler点数为9。这是项目离散化设置，原论文没有规定本项目的AFDM网格。SOMP原0.5网格、共同网格修订的pilot误差和补充资格面板按[资格记录](BASELINE_QUALIFICATION.md)保留；不将具体步长包装为文献方法名或普遍最优值。

## 2026-10-08：整数网格与连续参数估计

| 原文术语及忠实译名 | 核对来源与定位 | 本项目使用含义 |
|---|---|---|
| on-grid / 网格内；off-grid / 网格外 | [Wei et al., arXiv:2101.05629v1](https://arxiv.org/pdf/2101.05629v1)，§III-B pp.11–12式(17)–(24)；§VI-B pp.26–27 | 当前三基线只使用16×5有限整数网格，真实参数仍可偏离网格。原0.25/9也是有限字典，不能称为无网格算法。 |
| virtual sampling grid / 虚拟采样网格；first-order linear approximation / 一阶线性近似 | 同上，§III-B式(17)–(24) | 原文以网格附近的一阶项表示连续偏移，并用SBL学习。可作为后续粗网格细化依据，当前没有实现该偏移更新。 |
| fractional delay and Doppler frequency / 分数时延和Doppler频率 | [Chen et al., arXiv:2602.04316v2](https://arxiv.org/html/2602.04316v2)，§II式(6)参数定义，§III-B1–B2 | 原文整数部分与分数偏移的AFDM参数分解；该LOS估计器不是本项目多用户JADCE算法。 |
| atomic norm / 原子范数；atomic set / 原子集合 | [Zhang–Yuan–Greco, arXiv:2601.03639v1](https://arxiv.org/html/2601.03639v1)，§III-A式(28)–(31)，2026预印本 | 连续时延/Doppler区域Ω上的原子集合和范数。说明连续字典建模有文献依据；本项目未实现其SDP或ISAC方法。 |

16×5、30 kHz单位、80原子/用户均为项目离散化参数，没有将其命名为新算法。真实参数分布、GAMP论文流程及门限再校准见 [BASELINE_GRID.md](BASELINE_GRID.md)。


## 2026-10-08：原文流程与精确有限字典训练标签

| 原文术语/操作 | 原文定位 | 本轮代码含义 |
|---|---|---|
| approximate message passing with nearest neighbor sparsity pattern learning / 近邻稀疏模式学习的近似消息传递（AMP-NNSPL） | [Meng v1](https://arxiv.org/html/1601.00543v1)，§III Eqs.(9)–(20)、Algorithm1 pp.2–3，§IV | 原实数SMV、完整增量EM、近邻不含self、原200轮与严格未平方停止。复数/DD拓扑与单位列—物理坐标回代是明示的AFDM适配，见[执行合同](../results/baseline_fidelity_20261008/source/NNSPL_EXECUTION_CONTRACT.md)。 |
| EM-BG-AMP；sparse/heavy-tailed / 稀疏/重尾模式 | [Vila–Schniter v3](https://arxiv.org/pdf/1207.3107v3)，§III-E p.7的L=1定义、TableI p.3、TableII p.7、§III-D Eqs.(70)–(72)、§IV p.8 | 原实数及§II p.2允许的proper-complex转换；sparse学习均值、heavy-tailed固定零均值，均可执行完整噪声EM；不称为Zhao mixed-fronthaul MMV版本。 |
| stopping criterion / 停止准则；fixed number of iterations / 固定迭代次数 | [Tropp作者预印本](https://tropp.caltech.edu/papers/TGS05-Algorithms-Simultaneous-I-preprint.pdf)，Algorithm3.1 pp.6–7、§3.2及数值实例 | SOMP原算法接受停止准则输入。固定T及已知噪声残差两入口分别声明，AFDM T64是项目公开预算；不得输入真实支撑大小。 |
| GNN-ASPL；layer-wise training / 逐层训练；NMSE loss / NMSE损失 | [Ding接受稿](../Learning_Sparsity_Pattern_An_Adaptive_Joint_Detection_for_AFDM_Grant-Free_System_in_LEO_Satellites_Communication.pdf)，p.4–5 §III-C、p.5 Eq.(28)/§IV-A | 原十层逐SNR训练和逐样本系数NMSE；on-grid入口提供满足Y=ΨZ+W的精确物理系数标签。旧连续H投影标签另有模式身份；训练gamma拟合、图/宽度/epoch为项目选择，见[GNN合同](../results/baseline_fidelity_20261008/gnn/GNN_ASPL_EXECUTION_CONTRACT.md)。 |

`paper2016`、`paper2013`、`paper2023`、`unit_columns`与`grid_mode`是代码配方/坐标标识，不是新的学术方法名称；其适用源模型和AFDM差异见[本轮报告](../results/baseline_fidelity_20261008/REPORT.md)。Ding的联合行后验一般有非对角混合协方差，但Eq.(18b)及(12a)/(13a)递推的是对角方差；本轮没有把full-covariance AMP臆造成Ding规定步骤。


## 2026-10-09：前20场景排序与字典误差核查

| 术语或操作 | 原文定位 | 本次核查含义 |
|---|---|---|
| least-squares / 最小二乘；orthogonal / 正交 | [Tropp作者稿](https://tropp.caltech.edu/papers/TGS05-Algorithms-Simultaneous-I-preprint.pdf)，Algorithm3.1步骤4–5、§3.1 pp.6–7 | 对每个真实信道向量h和全部物理原子矩阵B，计算min_z‖h−Bz‖²=‖(I−UUᴴ)h‖²；这是使用真值的表示误差诊断，不是新的接收机或可实现基线。 |
| GAMP/EM tolerance；maximum iterations / 容差与迭代上限 | [Vila–Schniter v3](https://arxiv.org/html/1207.3107v3#S4)，PDF p.8 §IV首段，TableI/II | 本轮20次内层、20次外层及两个1e−5均有原文依据；达到预算上限或外层均值停止均不认证全部内层稳定。 |
| BOMP、SOMP、EM-GAMP | [Ding接受稿](../Learning_Sparsity_Pattern_An_Adaptive_Joint_Detection_for_AFDM_Grant-Free_System_in_LEO_Satellites_Communication.pdf)，pp.5–6 Fig.3/4、§IV-B和参考文献[7]/[10] | 原文贪婪基线名称不统一，不能据图名确认与Tropp-SOMP等同；原EM-GAMP引用Zhao2025，本轮Vila2013版本身份独立。排序随SNR和指标变化，见[核查报告](../results/baseline_ranking_audit_20261009/REPORT.md)。 |

## 2026-10-09：活动判决门限的原文依据

Ding接受稿第4页式(27)为每用户物理系数块平均平方范数除以所有用户块能量的最大值，以 `>= η` 判决；η仅定义为decision threshold。全文未给出η数值、标定过程或逐SNR选择规则。第5页§IV-A明确的逐SNR步骤是十层网络训练，不能推导出逐SNR门限。源文件SHA256为 `22dceda0036c892f44e961ce9ab6d094930e610befe0d51c18c3357aa1890ec5`，依据为[接受稿](../Learning_Sparsity_Pattern_An_Adaptive_Joint_Detection_for_AFDM_Grant-Free_System_in_LEO_Satellites_Communication.pdf)及[式(27)渲染](../results/baseline_pilot_20261008/paper_reaudit/ding_eq27_detail.png)。当前迁移配方使用完整H能量与逐SNR独立校准，是项目设置；当前直接转用原模型独立校准中已冻结的η，在全部SNR/网格共用；没有新增混合SNR校准。数值仍是原文未公开的实施设置。不能将式(27)未经声明地归称为Ding所有基线的共同判决方法。

## 2026-10-09：独立开发集上的细网格适配

本节仅对应 `results/baseline_resolution_20261009` 的新实验，不改写上文各历史实验的协议。

| 原文术语/直接数学操作 | 来源与定位 | 新实验中的范围 |
|---|---|---|
| damped GAMP / 阻尼GAMP | [Rangan et al., arXiv:1402.3210v3](https://arxiv.org/html/1402.3210v3)，§II-B、Algorithm 1第9/13行；§III–V | 对消息和均值作新旧值加权以检查相干细字典下的稳定性；一般BG先验和同时学习超参数不在其高斯全局收敛保证范围内，不能把该定理直接用于本实验。 |
| initialization / 初始化；noise variance learning / 噪声方差学习 | [Vila–Schniter v3](https://arxiv.org/html/1207.3107v3)，§III-A式(27)、§III-D式(70)–(71)、Tables I/II | 新增公共噪声仅作初值的选项，随后仍执行原噪声M步与非零均值学习。默认原初始SNR路径不变。已知噪声且不学习是另一配置，不与初始化混称。 |
| multiple measurement vectors、common sparsity pattern / 多测量向量、共同稀疏模式 | [Al-Shoukairi–Schniter–Rao作者稿](https://phil-schniter.web.app/pdf/tsp18_sbl.pdf)，§IV-A pp.299–300，§IV-C/Table II p.301 | 物理路径的DD位置跨天线共享。Zhang CN-MMV候选直接由共享行精度的复高斯乘积推导MAP更新；仍每次一轮GAMP后更新超参数，不能称为Al-Shoukairi内GAMP/外EM双循环原算法。推导见[候选定义](../results/baseline_resolution_20261009/gamp/ZHANG_CN_MMV_PLAN.md)。 |
| NMSE loss / NMSE损失；显式信道重建 | [Ding接受稿](../Learning_Sparsity_Pattern_An_Adaptive_Joint_Detection_for_AFDM_Grant-Free_System_in_LEO_Satellites_Communication.pdf)，§III-C式(28)；项目物理模型H=Σ_g z_g G_g | 非正交细字典上直接比较重建H与物理H；这是原系数NMSE损失的明示适配，不使用失效的GᴴH/N正交投影作系数标签，也不把最小范数密集系数当作真实稀疏路径。 |
| physical channel energy / 物理信道能量 | 数学定义Σ\|H_k\|²；归一化形式参考Ding p.4式(27) | 用重建H的用户能量除以最大用户能量。细字典非正交时与式(27)的系数能量不同；这是本项目判决量适配，计划在独立校准集上为每方法只拟合一个跨全部SNR/网格的门限。 |

0.25采样点时延步长、15 kHz Doppler步长、448原子/用户、迭代预算及训练日程均为项目设置，
不是新增方法名称。训练、开发、校准及确认样本的用途与种子见[新实验协议](../results/baseline_resolution_20261009/PLAN.json)。

本实验的 EM-BG-AMP 共同支撑扩展使用 Ding pp.3–4 式(18)的联合行BG后验，
配合 [Vila–Schniter v3](https://arxiv.org/html/1207.3107v3) Tables I/II 的内GAMP、
外EM流程；复数共享率、每列均值/方差及公共噪声M步是直接推导，见
[MMV推导](../results/baseline_resolution_20261009/em/MMV_DERIVATION.md)。
该实现仅递推对角方差，不称为完整协方差AMP或Zhao2025作者实现。

进一步的 fixed damping / 固定阻尼递推核对于
[Vila et al. 2015, Adaptive Damping and Mean Removal for the Generalized Approximate Message Passing Algorithm](https://arxiv.org/html/1412.2005)，
Table 1 I2–I3、R3/R4/R5/R6/R10：分别对输出消息精度、输出消息、输入均值中心、输入
伪观测方差、输出伪观测方差作新旧混合；R8/R9返回原始输入后验。
首步β=1来自I3，后续固定β是本实验检查的特例。
[执行计划](../results/baseline_resolution_20261009/em/VILA2015_DAMPING_PLAN.md)未实现
R12–R18的代价自适应接受/重试，也未实现mean removal，不能以该完整算法名指称当前候选。
这些递推没有为本项目一般复数共享行BG及EM迭代提供全局收敛保证。

AMP-NNSPL 的一次限定稳定性检查同样采用上述 Table 1 的方差/消息递推，保持
Meng §III 式(17)–(20)的近邻概率和slab参数原始更新目标；后者按相同正权重对
新旧值加权，是项目数值选择。固定点处新旧状态相等，故代入可恢复原
NN/EM方程；这不是收敛证明。阻尼为1时与现有MMV递推的12组逐步比较最大绝对差
1.12e−15，见[独立核对](../results/baseline_resolution_20261009/nnspl/TABLE1_CHECK.json)。
该候选只称为明确声明阻尼递推的AMP-NNSPL适配，未把两篇论文组合命名为新文献算法。

外层EM之间的GAMP状态初始化继续依据Vila–Schniter Tables I/II，并核对作者
[EMGMAMP.m](https://sourceforge.net/p/gampmatlab/code/HEAD/tree/trunk/code/EMGMAMP/EMGMAMP.m)
内部v5.3标记及其约396–408行的`warmStart`调用；状态字段见
[GampOpt.m](https://sourceforge.net/p/gampmatlab/code/HEAD/tree/trunk/code/main/GampOpt.m)
约237–282行，字段消费见
[gampEst.m](https://sourceforge.net/p/gampmatlab/code/HEAD/tree/trunk/code/main/gampEst.m)
的初始化与最终状态导出。网页浏览器为r633；尚未核验整套历史v5.3发行包。
本项目直接描述“跨外层迭代保留完整GAMP状态”，不另命名算法；保留当前/下一步p、vp
及均值、方差、消息和阻尼历史，以独立分段递推测试核对时间索引。实际读取范围、时间和
哈希见[源码阅读记录](../results/baseline_resolution_20261009/em/author_code/SAVED_READING_MANIFEST.json)，
不将局部源码阅读和本项目确定性核对写成作者MATLAB实现的整体复现。

AMP-NNSPL的有限次数数值重试只是项目操作说明：先按上述Vila2015 Table1固定阻尼
递推，只有达到迭代上限而未满足状态停止时，再从同一公开输入和先验矩按既有递推
重算一次。两者保留Meng式(17)–(20)和同一BG固定点方程，但消息初态、有限迭代和
停止状态列表不同；不设新方法名称，不称为Meng作者实现或Vila代价自适应算法。
邻域二分图的奇偶模式及其时间阻尼特征值是直接数学推论，未包装成文献中的收敛定理。
公式、来源页码及边界见[限定核对](../results/baseline_resolution_20261009/em/NN_FIXED_POINT_REVIEW.md)，
顺序选择只使用开发输入的停止覆盖和总迭代，不使用真值或NMSE。全部尝试与异常保存的
核对见[执行检查](../results/baseline_resolution_20261009/nnspl/RETRY_CHECK.json)。

## 2026-10-09：proposed 续训的抽样权重

importance sampling / 重要性采样：Katharopoulos & Fleuret,
*Not All Samples Are Created Equal: Deep Learning with Importance Sampling*,
[ICML 2018, §3.1，式(4)，PDF第3页](https://proceedings.mlr.press/v80/katharopoulos18a/katharopoulos18a.pdf)，
以 `w_i = 1/(N p_i)` 恢复均匀经验风险的期望梯度。
本轮对信道索引和连续噪声方差分别使用目标概率/抽样概率之比，再相乘加权原损失；
连续密度形式直接由换测度恒等式得到。弱功率子集与高方差区间的固定混合比例是
本项目训练设置，不是论文的梯度范数抽样器，不继承其总体方差下降或速度保证。
原始一阶、二阶目标继续对应 Cai §IV-B–C 式(48)–(49)、(53)–(54)。
实现范围、验证选择及32个独立开发场景见
[续训协议](../experiments/proposed_score_training_20261009/PROTOCOL.md)。

## 2026-10-10：终态残差活动判决

| 原文术语/直接数学操作 | 原文定位 | 本次适配范围 |
|---|---|---|
| generalized likelihood ratio test (GLRT) / 广义似然比检验；projection energy / 投影能量 | [Zhu et al., arXiv:1802.01266v3](https://arxiv.org/html/1802.01266v3)，§III-A式(5)–(6)，§III-B式(10) | 借用消去未知复增益后的归一化投影能量，对 score 终态残差搜索 AFDM/UPA 有限模板。不是联合重新拟合全部参数的完整GLRT，也未执行MNOMP的Newton refinement；详见[AUD公式](AUD_RESIDUAL.md)。 |
| stopping criterion、overestimating probability / 停止准则、过估计概率 | 同上，§IV-A式(11)–(16) | 原文分析DFT点和MMV噪声投影。这里对单位范数完整时空模板采用复高斯指数尾及并集界，阈值log(L/alpha)；仅纯噪声情形有界，拟合残差的实际虚警率由实验测量。alpha=.01是项目选择。 |
| energy-based activity decision / 按能量判决活动 | [Shen et al., arXiv:2412.20806v1](https://arxiv.org/html/2412.20806v1)，式(21)；[Ding接受稿](../Learning_Sparsity_Pattern_An_Adaptive_Joint_Detection_for_AFDM_Grant-Free_System_in_LEO_Satellites_Communication.pdf)，p.4式(27) | Shen对W信号块能量判决，Ding对归一化稀疏系数块能量判决。开发集探查完整H能量是显式适配，不等同于原文变量；最终候选使用观测残差投影。 |

本轮未将代码文件名 `residual_aud` 或多个原有操作的组合包装为新的既有学术方法名。

## 2026-10-11：MP 中的模板活动证据

| 原文术语/直接数学操作 | 原文定位 | 本次适配范围 |
|---|---|---|
| Gaussian mixture / 高斯混合；posterior activity probability / 活动后验概率 | [Vila–Schniter, arXiv:1207.3107](https://arxiv.org/pdf/1207.3107)，§II，PDF第2页式(3)与式(4)后复数扩展说明，式(9)–(17) | 对有限 AFDM/UPA 单位模板使用归一化混合权重，并积分消去复高斯增益；在完整信道向量上形成秩一高斯混合工作先验。没有采用原文标量独立先验或执行EM。 |
| device activity denoiser / 设备活动去噪器；Gaussian projection / 高斯投影 | [Cai et al., arXiv:2506.00581v2](https://arxiv.org/html/2506.00581v2)，§III-B2式(28)–(31)、§III-B3式(32)–(42) | 同一活动概率参与信道联合均值、方差与最终决策；保留现有空间协方差平均与外信息递推。物理模板证据是本项目替换项。 |
| score function、Tweedie's formula / score函数、Tweedie公式 | 同上，§IV-A式(43)–(45) | 用条件均值与对数观测密度导数的恒等式检查同一先验的一致性。保留冻结score条件矩时，模板活动证据与其一般不满足同一固定先验的精确关系，明确标为组合近似。 |
| GLRT 中消去未知复增益后的投影统计量 | [Zhu et al., arXiv:1802.01266v3](https://arxiv.org/html/1802.01266v3)，§III-A式(5)–(6) | 仅作为物理投影的来源。本次对增益与模板作先验积分，不将其称为原文GLRT或MNOMP。 |

完整模型、归一化项、矩公式和近似边界见 [AUD_PROJECTION_MP.md](AUD_PROJECTION_MP.md)。
“模板活动证据与冻结score条件矩的组合近似”是对项目操作的直述，不是自拟学术方法名。

## 2026-10-11：四个 baseline 的数值设置与多天线适配

| 原文术语或直接数学操作 | 原文定位 | 本次使用范围 |
|---|---|---|
| decision threshold / 判决门限 | [Ding 接受稿](../paper/literature/ding2026.pdf)，p.4 式(27) | 保留系数块能量相对最大值归一化及 >=。原文未公布数值 eta，也未要求跨 SNR 共用 eta；十个噪声条件下的数值门限由另外 20 个场景校准，公开接收功率与噪声方差决定使用哪一个门限。该调度及校准预算属于项目设置。 |
| 由公开接收功率与噪声方差估计 SNR | [本项目观测模型](SYSTEM_MODEL.md)，式(S0)–(S1) 的独立零均值 AWGN | 由 E_W[mean abs(Y)^2]=P_clean+sigma_squared 得到线性估计 mean abs(Y)^2/sigma_squared-1，再取正下界并转换 dB；不是读取生成 SNR 或 P_clean。最近节点及端点饱和是明确的数值规则，区间外没有性能保证。 |
| maximum number of iterations / 最大迭代次数，Tmax | [Zhao 2025](../references/zhao2025_mixed_fronthaul_jadce.pdf)，p.4126 Algorithm 1 | 原文未给数值 Tmax。保留原无阻尼、学习 beta/lambda/各列噪声及原 LLR > 0；5/10/15 次有限预算由独立开发数据选择后检查另外 20 场景。有限且不爆炸不等于收敛或论文资格。 |
| Gamma prior、MAP update / Gamma 先验、MAP 更新；共享行精度 | [Zhang 2023](../references/zhang2023_gamp_sbl_grant_free_noma.pdf)，pp.15058–15059 式(3)–(4)、(16)、(18)–(19)；[Ding](../paper/literature/ding2026.pdf)，p.2 式(9) 的共同网格支撑 | 对 M 个共址天线列约束同一行的精度相同。复高斯密度乘积给出 alpha_g=(M+a-1)/(sum_m E abs(z_gm)^2+b)，公共噪声精度为 (L*M+c-1)/(sum_lm E abs(y_lm-u_lm)^2+d)。属于明确 MMV 模型适配；M=1 与原复数 SMV 求解器的固定预算结果误差 <1e-12。 |
| 用公开噪声选择 Gamma 超参数 | 同上 Zhang 的 Gamma 噪声精度先验和 MAP 更新 | c=1+L*M、d=L*M*公开 sigma_squared 是项目开发设置。噪声仍逐轮学习，不是固定噪声；源作者没有公布这一组数值。仅开发结果改善尚不足以替换正式 baseline。 |
| Gaussian log-likelihood ratio / Gaussian 对数似然比；Gaussian mixture / Gaussian 混合 | [Zhao](../references/zhao2025_mixed_fronthaul_jadce.pdf)，p.4125 式(51)–(55)；[Liu–Yu](https://arxiv.org/html/1706.06438v2)，§III-C 式(19)–(22)；Ding 式(9)–(10) | 分别诊断后验均值/伪观测及其配对参数，并积分用户内部网格占用。非线性 BG 后验均值一般不满足 Zhao 式(52)的加性独立 Gaussian 假设。二原子精确枚举只验证混合似然公式；该读出在 AFDM 开发场景产生大量虚警，未采用。 |

本轮保留两种不同的开发选择规则：先前平均线性完整 H NMSE 选择全局 5 次预算；后续明确新增“平均线性完整 H NMSE + 平均 AER”数值目标，选择按公开噪声条件调度的有限预算。后者是项目参数选择，不能倒写成前一规则或源论文方法；验证标签不参与数值选择。完整 H NMSE 保留非活动用户估计误差，活跃 H NMSE 另列。

候选接收入口见 [public_conditioned.py](../src/afdm_jadcedd/algorithm/baselines/public_conditioned.py)，独立配置见 [80 用户候选配置](../configs/baselines_load80_public_conditioned_20261011.json)。SOMP 仍按 Tropp 的 SOMP 标记；Ding 的 BOMP/SOMP 称谓差异沿用 [复现范围](DING_REPRODUCTION_SCOPE.md)，不能以预期排序替代算法来源核验。
该文档末段提出多个增益方差的归一化混合，仍直接采用上述 Vila–Schniter §II
式(3)的混合权重定义；相应向量秩一复高斯似然为项目模型下的推导。这是待验证
扩展，当前代码和本轮性能结果只对应单个冻结增益方差。


## 2026-10-11：baseline 的共享方差、完整协方差与指标补充核对

| 原词或忠实译名 | 原文定位 | 当前使用范围 |
|---|---|---|
| EM update / EM 更新；conditional second moment / 条件二阶矩 | [Zhao 原文](../references/zhao2025_mixed_fronthaul_jadce.pdf)，p.4124 式(37)–(39) | 约束所有条目使用同一方差时，由同一个 Q 函数得 β=Σπq/Σπ；约束一行各天线共享时按行求和。是参数约束下的项目诊断，不称为原文逐项 β 的同一参数化；所有失败保留 |
| vector-valued variable nodes / 向量变量节点；covariance / 协方差 | [Rangan 等，Hybrid Approximate Message Passing 作者稿](https://arxiv.org/html/1111.2581v4#S5)，§V、Algorithm 2 式(28)–(38)；[Liu–Yu](https://arxiv.org/html/1706.06438v2#S3.SS3)，§III-C 式(19)–(22) | 新开发检查把一个 AFDM 网格行的多天线系数作为复向量，在 Gaussian 消息和 BG 后验中保留完整矩阵协方差。实数公式按 proper complex Gaussian 密度改写；不是 Zhao 原标量 Algorithm 1 的逐字复现 |
| normalized mean squared error (NMSE) / 归一化均方误差 | [Ding 原文](../paper/literature/ding2026.pdf)，p.5 式(28)、§IV-B | 分别核对总误差/总能量和逐场景线性归一化误差均值，均最后转 dB。前者是项目现有主统计，后者对应原文训练损失的平均形式；当前物理 H 与原文系数 Z 不混同 |
| activity detection / 活动检测 | Ding p.4 式(27)，Zhao p.4125 式(51)、(53)–(55) | 另计算用接收机自己的活动判决将非活跃估计置零后的物理 H 误差；未用真实活动集合作掩码。原文未明确该步骤用于其图3，故只报告为补充输出阶段，不替换原始主指标 |

状态与所有原始结果分别见 [场景适配报告](../results/baseline_scenario_audit_20261011/SCENARIO_ADAPTATION.md)、[20场景配对比较](../results/baseline_scenario_audit_20261011/paired_twenty/REPORT.md)、[指标核对](../results/baseline_scenario_audit_20261011/channel_metric_audit/REPORT.md)。完整协方差的局部密度和 M=1 退化检查不等于稳定性或论文资格证明。

## 2026-10-11：等价观测变换与 MMV 运行入口

| 原词或忠实译名 | 原文定位 | 当前使用范围 |
|---|---|---|
| unitary transformation / 酉变换；singular value decomposition / 奇异值分解 | [Guo–Xi，Approximate Message Passing with Unitary Transformation](https://arxiv.org/html/1504.04799)，§I 式(1)–(3)、§III Algorithm 3 | 开发诊断仅采用 UᴴA、UᴴY 的等价 AWGN 观测，核对似然能量、列范数、匹配滤波和初始化能量。仍运行原 Zhao 核；不是 UT-AMP 方差更新的实现，不能将 Gaussian 先验的收敛证明用于此 BG/EM 闭环 |
| Gamma prior / Gamma 先验；MAP-EM / 最大后验 EM | Zhang pp.15058–15059 式(3)–(4)、(18)–(19)；Zhao p.4124 式(37)–(39) | 新 MMV GAMP 入口明确采用共享行精度和共用学习噪声。EM 开发组合另外用 c=1+LM、d=LMσ²_public 学习共用噪声，并按 Σπq/Σπ 共享行 slab 方差；均为声明的项目适配，不是 Zhao 原逐元素参数化或固定噪声 |

新增运行配置与12条件等价核验见[场景适配报告](../results/baseline_scenario_audit_20261011/SCENARIO_ADAPTATION.md)；EM 所有开发候选及失效状态见[诊断报告](../results/baseline_scenario_audit_20261011/EM_DIAGNOSTICS.md)。

## 2026-10-11：状态演化关系与连续多径结构核对

| 原词或忠实译名 | 原文定位 | 本次使用范围 |
|---|---|---|
| state evolution equation / 状态演化方程；effective noise covariance / 有效噪声协方差 | [Zhao原文](../references/zhao2025_mixed_fronthaul_jadce.pdf)，p.4125式(52)后；[Liu–Yu作者稿](https://arxiv.org/html/1706.06438v2#S3)，§III-B状态演化与§III-C MMSE去噪器 | Zhao明确给出Σ_eff=diag(Σ_w)+(K/τ_p)E|x̂−x|²。新的读出诊断用模型后验方差估计期望，当前字典维度比为KG/L；不是oracle真实MSE，也不建立结构化AFDM矩阵的状态演化。保持原核后两种取法大多给出相同判决，未提升候选 |
| NTN-TDL-D、delay spread / NTN-TDL-D、时延扩展 | [Huang原文](../paper/literature/huang2026.pdf)，p.2950式(3)、Table I；Ding p.2式(3) | 配置归一化延迟(0,0,0.5596,7.3340)与30–50 ns尺度给出用户内部最大间隔0.176016采样点；区别于宏观用户间差分时延。两个同位置分量传播算子一致，其余分量仅较相关，并非整数网格真值 |
| least squares projection / 最小二乘投影 | Tropp SOMP Algorithm 3.1的限制支撑最小二乘；Huang式(4)–(6)的完整有效信道 | 真实连续LOS算子上的单算子投影明确标记oracle，只用于诊断全部候选物理信道的结构，不是SOMP结果或可达性能；共同方向下的空间秩一仍由当前H=aG直接得到 |

新的独立100场景完整对比见[冻结配方验证](../results/baseline_scenario_audit_20261011/frozen_four_hundred/REPORT.md)，物理结构诊断见[完整候选信道核对](../results/baseline_scenario_audit_20261011/channel_structure_audit/REPORT.md)。

## 2026-10-11：用户活动、网格占用及误差平台的诊断

| 原词或忠实译名 | 原文定位 | 本次使用范围 |
|---|---|---|
| group sparsity / 组稀疏；strong edges / 强边 | [HyGAMP作者稿](https://arxiv.org/html/1111.2581v4)，§VI式(39)–(44)；Ding p.2式(9)–(10) | 开发候选区分用户活动与用户内网格BG占用，局部支持密度精确积分；完整阵元消息但未传播网格间协方差，是明示的组件近似，未通过实际开发验证，不能称为Zhao原样实现 |
| Gaussian mixture / 高斯混合；log-likelihood ratio / 对数似然比 | Zhao p.4125式(51)–(55)；HyGAMP §VI式(39)–(44) | 独立行BG密度的用户读出为Σlog[(1−λ)+λ exp(b_g)]；与Gaussian分数Σb_g的包含关系是本项目局部模型下的数学推导，只作诊断，未替换正式规则 |
| least squares projection / 最小二乘投影 | Tropp SOMP Algorithm 3.1；Huang p.2950式(4)–(6)的完整有效信道 | 现有100个off-grid物理H向整数网格算子子空间的投影为oracle诊断。正交残差给出物理表示误差下界，不等于AER下界，不生成on-grid性能结果 |
| error floor / 误差平台 | Ding p.6图3讨论明确使用error floor描述SOMP与VAMP-ST | 本项目分别报告P_MD、P_FA与AER；−4～6 dB的后段虚警变化有限，尚未由该有限区间证明渐近AER下界 |

结果见[网格残差和AER组成](../results/baseline_scenario_audit_20261011/off_grid_aer_causes/REPORT.md)及[两层BG失败检查](../results/baseline_scenario_audit_20261011/em_spatial_user_grid_development/REPORT.md)。原100场景算法配置未据本次诊断重新拟合。

## 2026-10-11：接收方向残差、初始化与受约束EM控制

| 原词或忠实译名 | 原文定位 | 本次使用范围 |
|---|---|---|
| spatial covariance / 空间协方差 | [Djelouat等作者稿](https://arxiv.org/html/2112.04295)，式(1)、(9)–(11)；[Huang](../paper/literature/huang2026.pdf)，p.2950式(4)–(6) | 从公开Y的二阶矩选择最大特征向量是项目诊断操作。真值只用于该方向上的物理网格残差及实际热噪声能量，不给接收机协方差，不称为AER因果试验 |
| initialization / 初始化；noise variance learning / 噪声方差学习 | [Zhao](../references/zhao2025_mixed_fronthaul_jadce.pdf)，p.4126 Algorithm 1、p.4124式(37)–(39)、p.4125式(49) | 0.1接收功率比例是项目数值选择，Algorithm 1未规定它。公开噪声初值控制保留后续噪声学习，并同时改变互补的slab初始能量；未修复完整推断 |
| expectation maximization / 期望最大化 | Zhao p.4124式(37)–(38) | 用户内网格行共用β_k时，同一Q函数给出β_k=Σ_g π_kg q_kg/Σ_g π_kg；q为每阵元条件R白化二阶矩。该参数约束由项目直接推导，不包装成Zhao原逐条目参数化或新的既有方法名称 |

诊断和全部开发失败分别见[方向残差](../results/baseline_scenario_audit_20261011/spatial_grid_residual/REPORT.md)、[初始化控制](../results/baseline_scenario_audit_20261011/em_public_noise_spatial/REPORT.md)、[共享方差控制](../results/baseline_scenario_audit_20261011/em_shared_user_variance/REPORT.md)。三者均未改变主100场景接收机、阈值及论文资格标志。

## 2026-10-11：噪声谱边界、网格初值及局部Gaussian方差拟合

| 原词或忠实译名 | 原文定位 | 本次使用范围 |
|---|---|---|
| Marčenko–Pastur density / Marčenko–Pastur密度；sample covariance / 样本协方差 | [Nadakuditi–Edelman作者稿](https://arxiv.org/pdf/0705.2605v1)，§III Proposition3.1式(14)、p.6；实数或圆对称复数模型见式(1)、p.2 | 只用σ²(1+√(M/L))²渐近噪声谱边界选择公共Y中的先验方向，再作单位阵元方差归一化。不是该文的完整信号数估计器、有限样本检验或实际活动人数估计 |
| spatial covariance / 空间协方差 | [Djelouat](https://arxiv.org/html/2112.04295)，式(9)–(10)；HyGAMP §V Algorithm2 | x_g=Bξ_g、R=BBᴴ的潜在坐标为本项目直接Gaussian变换，物理阵元及噪声学习保留。满秩与现有空间EM等价；低秩控制虽公式核对通过，检测更差，未采用 |
| user activity / 用户活动；sparsity pattern / 稀疏模式 | [Ding](../paper/literature/ding2026.pdf)，p.2式(9)–(10) | pP/G只作为名义稀疏网格的行率初值，P=3为公开模型名义不同传播位置数；不把连续非零投影系数称为三支撑。初值之后仍按原公式学习行率 |
| maximum likelihood / 最大似然；log-likelihood ratio / 对数似然比 | [Zhao](../references/zhao2025_mixed_fronthaul_jadce.pdf)，p.4124式(37)–(38)；Djelouat式(9)–(10) | 固定Φ=φI的特例下，同一样本拟合β及零LLR的尺度关系为项目直接推导。Γ尾只核查此数学模型，不是当前AFDM活动误差率或完整EM固定点证明 |

结果：[空间先验秩控制](../results/baseline_scenario_audit_20261011/em_signal_subspace/REPORT.md)、[名义网格率初值](../results/baseline_scenario_audit_20261011/em_grid_rate_initialization/REPORT.md)、[局部方差拟合](../results/baseline_scenario_audit_20261011/gaussian_variance_readout/REPORT.md)。所有未采用的实际输出和失败均保留。

## 2026-10-11：用户活动先验下的共同BG方差学习

| 原词或忠实译名 | 原文定位 | 本次使用范围 |
|---|---|---|
| Bernoulli–Gaussian / Bernoulli–Gaussian；EM update of the noise and prior parameters / 噪声与先验参数的EM更新 | [Vila–Schniter作者稿](https://arxiv.org/html/1207.3107v3)，§III-B式(28)、(47) | 在用户/网格局部支持模型中将所有slab尺度约束为一个β，受约束Q给出β=Σπq/Σπ；q为潜在空间维数归一化的条件二阶矩。该约束有原文共同BG方差学习依据，但不是Zhao原逐项参数化，不包装成新的既有方法名称 |
| strong edges / 强边；group sparsity / 组稀疏 | [HyGAMP作者稿](https://arxiv.org/html/1111.2581v4)，§VI式(39)–(44)、§V Algorithm 2 | 用户活动与条件网格支持的局部密度积分保留，完整阵元协方差传播；跨网格后验协方差未传播，明确为分量近似。共同β和两个概率仍学习，实际开发失效，不能称为完整HyGAMP或原Zhao复现通过 |

数学检查、72次开发推断与全部失效见[报告](../results/baseline_scenario_audit_20261011/em_user_grid_population_variance/REPORT.md)。

## 2026-10-11：后验均值输入的条件用户似然比

| 原词或忠实译名 | 原文定位 | 本次使用范围 |
|---|---|---|
| log-likelihood ratio / 对数似然比 | [Zhao](../references/zhao2025_mixed_fronthaul_jadce.pdf)，p.4125式(51)–(55) | 保留后验均值作为输入及零条件LLR门限，不加入用户先验赔率。不是原平坦信道Gaussian H1的原样复制；多网格密度扩展明确记为AFDM适配 |
| user activity / 用户活动；sparsity pattern / 稀疏模式 | [Ding](../paper/literature/ding2026.pdf)，p.2式(9)–(10)；[HyGAMP](https://arxiv.org/html/1111.2581v4)，§VI式(39)–(44) | 用户活动H1下，每个网格位置采用(1−rho)CN(0,Phi)+rho CN(0,Phi+beta_g R)。独立网格积分直接给出Σ_g log[(1−rho)+rho exp(b_mu,g)]，不是完整HyGAMP强边消息传播 |
| Bernoulli–Gaussian / Bernoulli–Gaussian | Zhao p.4124式(29)–(30)、(38)–(40) | 当前推断继续使用逐行BG与条件二阶矩M步；读出的条件网格率rho=min(3/G,1)仅为公开名义位置近似，不反馈到E步，不宣称精确联合用户支持后验或连续真值只有三个非零投影系数 |
| covariance / 协方差；noise variance / 噪声方差 | Zhao p.4125式(49)、(52)；HyGAMP §V Algorithm2 | 完整残差Gaussian协方差控制及矩阵MAP惩罚为项目扩展，未采用。最后伪观测协方差作为后验均值Gaussian误差代理仍是近似，未证明AFDM状态演化 |
| expectation maximization / 期望最大化 | Zhao p.4124式(37)–(40) | 式(38)的条件BG方差驻点与打印式(40)中的概率因子不一致；保留打印式控制结果，当前采用与Q驻点一致的条件二阶矩，不将此差异隐去 |

三项密度/单网格退化检查、三个开发场景及20个独立场景分别见[开发读出](../results/baseline_scenario_audit_20261011/em_posterior_mean_sparse_llr/REPORT.md)、[独立验证](../results/baseline_scenario_audit_20261011/em_sparse_user_validation/REPORT.md)。完整协方差与打印式(40)的负结果见[协方差控制](../results/baseline_scenario_audit_20261011/em_spatial_error_covariance/REPORT.md)、[打印式控制](../results/baseline_scenario_audit_20261011/em_spatial_printed_beta/REPORT.md)。

同一100场景的600次不变核心导出、稀疏H1读出及三方法复用见[完整验证](../results/baseline_scenario_audit_20261011/em_sparse_user_hundred/REPORT.md)。可运行的独立配方已接入；其源名称使用EM-GAMP并明示AFDM/MMV适配，不宣称完整原样Zhao或全部迭代收敛。

## 2026-10-11：当前实现的代码位置

本次代码整理沿用本表已有算法名称与公式出处，软件标识集中于 `algorithm/registry.py`。
SOMP 对应 Tropp Algorithm 3.1；GAMP-SBL MMV 的共享行精度与 Gamma MAP 更新沿用上文
Zhang pp.15058–15059 式(3)–(4)、(16)、(18)–(19)及已声明的 MMV 适配；GNN-ASPL 对应
Ding pp.3–5 式(12)–(28)；Zhao EM-GAMP 使用式(38)的驻点更新并保持待验证状态。
完整信道 score 与活动分类器代码集中到 `algorithm/proposed/`，公式和来源仍见
[THEORY.md](THEORY.md)。`proposed`、`somp`、`gamp`、`gnn`、`em` 是命令行键，
不作为新的算法术语。当前 baseline 来源和项目设置见 [BASELINES.md](BASELINES.md)。
