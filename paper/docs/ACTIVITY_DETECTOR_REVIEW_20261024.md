# 当前 GFRA 实验的活动检测判据核查

日期：2026-10-24。范围：已知相位、估计噪声的 STMP、SOMP、GAMP-SBL、GNN-ASPL 和 off-grid SBL。本文是针对当前实现的原文核查与方案建议，不是穷尽性系统综述。没有修改接收机、门限、权重、冻结计划或正在运行的实验，没有进行新的推断、训练或门限拟合。

**当前问题不是所有活动判决都错了，而是不能默认最强用户归一化能量适合四个不同的恢复器。应统一可用信息、校准预算和检测目标，分别选择有模型依据的统计量。** 固定用户后验门限、固定相对能量比例、依据有效误差计算的能量门限是三种不同规则。

## 原文给出的不同选择

| 来源与定位 | 原文检测量 | 对本项目的含义 |
|---|---|---|
| Ding，TVT 2026，本地六页稿 p.4 式(27) | 每用户系数块平均平方范数，再除以最大用户块能量，与 eta 比较 | 当前 GNN 读出的形式有直接原文依据。内部路径非零概率不是最终用户活动后验；改成路径概率聚合应另标适配版。该页已目视核对，确为平方范数。原文未公布可复现的 eta 数值/校准程序。 |
| Zhou 等，TWC 2023，作者稿 §IV-C 式(27)、脚注3 | SOMP 输出的用户能量；绝对门限为最大用户能量乘经验系数 0.1 | 相对能量有直接 GFRA/SOMP 先例，但 0.1 并非跨信道、跨算法最优值。 |
| Shen 等，TWC 2025，作者稿 §III-A 式(21) | 汇总每用户 W 的 Frobenius 能量，与经验预设门限比较 | 不除以最强用户；不等于把 GAMP 内部路径概率直接当用户概率。该式没有给出可复现的逐 SNR 数值表。 |
| Liu–Yu，TSP 2018，作者稿 p.6 §III-E Definition 1、式(30) | AMP 去噪前伪观测的能量，门限依赖有效方差 tau_t^2、用户大尺度系数 beta_n 和天线数 | 检测规则可以固定，但换算成能量门限后数值会变化。不能将有效误差方差替换成物理噪声，也不能将伪观测替换成任意收缩后的均值。该定义不是带活动先验修正的有限维 MAP 原式。 |
| Cai 等，2026，§III-B2 式(29)–(31)，本地 PDF p.7 | 包含活动先验和 Gaussian 消息的用户活动后验 lambda_post | 支持用户级活动概率判决。0.5 的等损失依据来自条件风险推导，不能声称所核查段落公开了 0.5 数值。 |
| Zhang 等，IoTJ 2020，§III-A3 式(15)–(19)，PDF pp.6–7 | BR-MP-EM 融合用户 Bernoulli 消息、活动先验及 CE 证据，最终 LLR 大于零判活跃 | 直接 LEO GFRA 的用户层证据例子；CE 证据使用 Gaussian 误差近似，不能照抄到任意估计器后声称精确后验。 |
| Zhang 等，TVT 2019，§II-C、§III-D、Table IV | 用户块共同精度的倒数，即用户方差，与门限比较；数值示例 0.1 | 不等于当前逐字典行 Gaussian SBL，也不等于按最大用户归一化的能量。 |
| Ke 等，TSP 2020，§III-B 式(39)–(41)、§V Fig.6/8 讨论 | CG-AD 为信道幅度读出；BI-AD 为系数 belief indicator 判决后投票 | 空间域 BI-AD 更可靠，角域则 CG-AD 更可靠；不存在脱离稀疏结构的一律概率优于能量。空间域 90% 投票不能照搬到每用户仅少数字典路径非零的情形。 |
| Zhao–El-Hajjar–Yang，OJVT 2025，§V-B 式(24)–(31) | EM-BSBL 活动权重的条件分布建模，使用 Neyman–Pearson 方法控制虚警 | 直接研究 GFRA 的门限设计。是固定虚警约束目标，不自动最小化 AER。这里核到机构记录及检索返回的原文段落；整份 PDF 下载 403，不声称完成全文核读或验证 Gamma 拟合在 AFDM 中成立。 |

Ke 的结论对本次尤其重要：其空间域中，信道增益判决可以出现错误平台，belief indicator 判决更好；换到角域，共同稀疏关系改变，反而是 belief indicator 出现明显平台。故不能从我们当前平台推出某类检测方法普遍错误，也不能只为使曲线下降而换统计量。

## 我们实际应优化什么

当前 AER 统计每次用户判决的错误，因此总体风险是

\[
R=\rho P_{\rm MD}+(1-\rho)P_{\rm FA}.
\]

rho 是部署活动先验；本实验设定为 0.1，有限样本实际占比会变化。若 q_k 确为包含该先验的用户活动后验，则判活跃的条件风险为 1-q_k，判不活跃为 q_k。等错误代价下，q_k >= 0.5 最小化这一条件风险。它不保证条件漏检率等于虚警率。

令 s_k 为所使用的观测或有效统计量，若有相应的两类条件密度，则等价判决为

\[
\log\frac{p(s_k\mid a_k=1)}{p(s_k\mid a_k=0)}
+\log\frac{\rho}{1-\rho}\geq0.
\]

rho=0.1 时，未包含先验的似然比需达到 9；包含先验的后验概率才比较 0.5。两者不能混用。对压缩统计量构建的后验，最优性也仅相对于该统计量，不等于完整观测的最优检测。

如果任务改为固定 P_FA 下尽量降低 P_MD，则应采用 Neyman–Pearson 目标。Zhao 2025 提供直接 GFRA/BSBL 例子，但它与当前最小 AER 不是同一个目标。论文可补充 P_MD–P_FA 曲线，以显示工作点变化是否改变方法排序；不应仅凭 AER 曲线平滑度选判据。

## 五种实现的具体建议

**STMP：保留用户概率判决和 0.5。** 当前 `src/algorithm/STMP/denoiser.py` 确实先从分类器 logit 减去训练先验 logit，再加部署先验 logit；并非把任意 sigmoid 直接称为后验。需要验证有限网络在实际迭代查询上的概率可靠性与检出能力，而不是改成最大用户能量归一化。这里的概率仍是近似量，理论上的 0.5 最优性不自动证明有限模型完全校准。

**GNN-ASPL：原文读出保留为忠实基线。** Ding 式(27)有明确出处，不能说它没有活动检测或实现该式就是错误。若另评估绝对能量、噪声归一化能量、路径概率聚合，需明确是同一恢复器的读出变体。max、均值、90%投票和 1-product(1-pi) 都不自动等于用户后验：特别是乘积公式需要合适的联合/条件独立模型，且当前图网络在同用户路径间耦合。

**SOMP：保留噪声相关恢复停止与有出处的最终用户检测；两者分开验证。** 相对能量可作原文参考。若为当前系统采用其他能量统计量，必须独立校准与验证，不能把被选中一个原子就等同于用户必然活跃；噪声也可能选中原子。

**GAMP-SBL：不要伪造用户后验或套 MP-BSBL 的 0.1。** 当前实现为每字典行跨天线共享精度，没有用户层 Bernoulli 活动变量。短期可评估均值能量读出；若追求模型内生的 GFRA 活动判决，更有依据的长期候选是具有用户共享活动变量或用户块超参数的模型，同时保留组内路径稀疏。引入该模型会改变推断，需要单独实现与运行，不只是改最终门限。

**Off-grid SBL：活动检测必须明确为项目适配。** Wei 原方法解决单用户 off-grid 信道估计，不提供本项目用户检测。当前每原子方差不是用户共享方差。应优先验证不依赖最强用户的检测量，并为其误差/非活跃分布建立依据；有模型的用户层活动扩展是另一个需重推断的候选，不能将原子方差随意相加后冒称原生 BSBL。

## 为什么不能直接宣布能量除噪声就是正确方案

对固定支持的最小二乘估计，噪声协方差已经变为 sigma²(A_S^H A_S)^-1；它取决于字典相关性。SOMP 的支持又由同一数据选择；GAMP/GNN 有非线性收缩；off-grid 存在参数近似和残余干扰。因此，物理噪声不等于输出估计误差方差。

若经过验证的有效观测为 r_k，在 H0 下为 CN(0,C0_k)，在 H1 下为 CN(0,C0_k+R_k)，则相应 Gaussian 对数似然比为

\[
r_k^H[C_{0,k}^{-1}-(C_{0,k}+R_k)^{-1}]r_k
-\log\frac{\det(C_{0,k}+R_k)}{\det C_{0,k}}.
\]

再加上述活动先验项即可比较零。这是明确假设下的密度代数，不是当前四个 baseline 已验证可用的公式。C0_k 必须描述该有效观测在非活跃条件下的尺度和相关性，不能未经核查就用物理噪声或后验方差替换。若 H1 有非零均值或非 Gaussian 分布，也须相应修改。

因此 E_hat/noise_hat 可以作为低成本经验候选，但不能直接称为恒虚警率检测器。物理噪声下降时，未同比消失的泄漏可能被放大，从而增加虚警。原始绝对能量固定门限同样可能对弱用户造成平台，不是移除 max 之后就自动解决。

## 最小充分验证与数据复用

先保持恢复器固定，在编号1000–1999的既有校准场景内部按物理场景成组交叉验证。只比较预先列明的少数统计量：原相对能量、绝对能量、物理噪声归一化能量。每个候选先用一个跨 SNR 固定标量门限，以当前 pooled AER 为目标，同时检查逐 SNR P_MD、P_FA 和波动区间；不得用真实 SNR 或真实活动数在接收机内选工作点。胜出与否尚无本轮结果。

若低成本统计量均无法给出合适的工作点，再研究有效误差/非活跃条件分布与相应似然比。此时必须声明新统计模型和估计方式，不能给经验分数套概率名称。只有完成校准内验证后，才对前1000场景一次性报告。前1000已反复查看，须保留开发记录，不能描述为从未查看过的最终测试集。

原文读出结果应始终保留。读出变体胜出时，不应悄悄替换后仍声称完全复现原文。对导频数、用户数等其他实验也不保证本条件下的门限自动迁移；需要核查维度归一化及非活跃统计分布。

目前缓存支持如下：

- 四个 baseline 有每用户能量、相对分数和最终物理噪声估计，三项能量候选可离线重判，无需重推断。
- GNN 另存有 `row_probability[3200]` 与每用户 `channel_energy`，可研究聚合统计量，但不是原生用户后验。
- SOMP/GAMP 的多数场景仅保留系数块能量，不含完整重构信道。非正交字典下不能从该能量精确推出物理信道能量。
- GAMP/off-grid 未保存足以恢复用户块方差或完整有效误差协方差的最终状态。不能用现有能量缓存冒充 Liu 型伪观测检测或用户块 SBL 判决。
- 只改变最终活动读出时，本项目当前未按硬判决截断的完整信道 NMSE 保持不变；若修改先验、迭代、支持或硬截断信道，需重新计算相应结果。

先前“每个方法校准一个固定门限”的建议只解决了校准程序，没有证明统计量本身合适。本次补上这一限制，不改写既有实验记录。上轮真实信道诊断中 off-grid 的30个门限漏检，仅支持该批场景和该历史固定门限的结论；它不是任何估计器的严格性能下界。

## 来源与核查范围

1. Ding et al., *Learning Sparsity Pattern: An Adaptive Joint Detection for AFDM Grant-Free System in LEO Satellites Communication*, TVT, 2026. [机构记录](https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/Learning-Sparsity-Pattern-An-Adaptive-Joint/991155194002346?institution=44SUR_INST)；[本地原文](../../reference/literature/ding2026.pdf)。p.4式(27)已目视核读。
2. Zhou et al., *Active Terminal Identification, Channel Estimation, and Signal Detection for Grant-Free NOMA-OTFS in LEO Satellite Internet-of-Things*, TWC, 2023. [作者稿](https://arxiv.org/html/2201.02084v2#S4.SS3)。核读§IV-C及门限脚注。
3. Shen et al., *LEO Satellite-Enabled Random Access with Large Differential Delay and Doppler Shift*, TWC, 2025. [作者稿](https://arxiv.org/html/2412.20806v1#S3.SS1)。核读式(21)及其说明。
4. Liu and Yu, *Massive Connectivity With Massive MIMO—Part I: Device Activity Detection and Channel Estimation*, TSP, 2018. [作者稿](https://arxiv.org/html/1706.06438)。核读§III-C–E及§IV-A的分布假设；本地原文 p.6定位复核。
5. Cai et al., *Joint Activity Detection and Channel Estimation for Massive Connectivity: Where Message Passing Meets Score-Based Generative Priors*, 2026. [作者稿v2](https://arxiv.org/html/2506.00581v2#S3.SS2)；[本地期刊原文](../../reference/literature/cai2026.pdf)。核读§III-B2，本地p.7已目视核读。
6. Zhaoji Zhang et al., *User Activity Detection and Channel Estimation for Grant-Free Random Access in LEO Satellite-Enabled Internet-of-Things*, IoTJ, 2020. [作者稿](https://arxiv.org/html/2005.09826)。核读§III-A3，PDF p.6已目视核读，p.7式(19)文本核读。
7. Zhaoji Zhang et al., *DNN-Aided Block Sparse Bayesian Learning for User Activity Detection and Channel Estimation in Grant-Free Non-Orthogonal Random Access*, TVT, 2019. [作者稿](https://arxiv.org/html/1910.02953v1)。核读§II-C、§III-D及Table IV。
8. Ke et al., *Compressive Sensing-Based Adaptive Active User Detection and Channel Estimation: Massive Access Meets Massive MIMO*, TSP, 2020. [作者稿](https://arxiv.org/html/1906.09867v4)。核读§III-B和§V Fig.6/8相关讨论。
9. Yi Zhao, Mohammed El-Hajjar, and Lie-Liang Yang, *Joint User Activity Detection and Channel Estimation in MC-GFMA Systems by Block Sparse Bayesian Learning With Threshold Optimization*, OJVT, 6, 2441–2458, 2025. [机构记录](https://eprints.soton.ac.uk/505524/)，DOI 10.1109/OJVT.2025.3603690。范围限机构元数据/摘要和检索可读的原文§V-B段落，下载全文不可用。

检索日期为2026-10-24，检索围绕 grant-free activity detection、likelihood ratio、effective noise、block sparse Bayesian learning、threshold optimization，并复核前一轮 Ding/Shen/Cai/Zhou/Ke 原文。优先使用作者稿、机构库和原始论文；未把搜索到的相邻数据检测论文自动当作未知信道 JADCE。证据文件、结构预检和页面文本保存在 `reference/reviews/activity_detector_review_20261024/`。结构预检通过只说明PDF结构可读，不代表整篇论文已逐式验证。文献检索、代码阅读与本报告由 AI 辅助完成，另有一次只读代码核查；未模拟外部同行评审。
