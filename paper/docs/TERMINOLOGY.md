# 当前术语与来源

> 记录说明（2026-11-07）：下文按日期保留研究依据和作者决定，“当前”“最新”均指记录当时。现行图源与采用状态见 [REPRODUCTION.md](REPRODUCTION.md)，运行进度见[实验索引](../../result/README.md)。本轮整理仅更新导航，不改变原判断；移出的旧说明通过固定版本链接查阅。

**2026-11-05 最新展示名称（作者要求）：** 论文方法统一使用已有作者标签 **GP-MP**，估计相位版本为 **GP-MP-EP**；STMP 基线保持。GP/MP 沿用 generative-prior/message passing，未新增文献术语。名称不再编码训练噪声颜色；数据、权重与历史标识按原记录溯源。此次先统一图例及正文名称，实验完成后另行替换数据。

### 2026-11-05：正文弱化训练噪声颜色，保留实验归属

本轮以已有作者标签 GP-MP 表示正文方法，采用白噪声形式展开公式；CGP-MP 继续标记第六章实际有色训练实现及其既有结果。两者不是引用文献中的原算法名称。STMP 仍指本项目三网络 AFDM 适配版本。此次是正文修订，不切换冻结权重或 FINAL.json。摘要和引言不再把预条件列为贡献。

| 表述 | 原文定位与采用范围 |
|---|---|
| channel prior / 信道先验；直接学习有效信道 | Huang，项目内 `reference/literature/huang2026.pdf`，摘要、贡献(i)，印刷 p.2949；§III-A 式(7)，p.2951。支持直接从 AFDM 有效信道学习而不施加稀疏、网格对齐假设；不称本文首次提出这一思路。 |
| conditional mean、conditional covariance / 条件均值、条件协方差 | Dytso–Poor–Shamai，正式出版 §III Proposition 1 式(17)，印刷 p.1885；[预印本](https://arxiv.org/pdf/2104.01883) §IV Proposition 1 式(22)。白噪声实表示满足 P=(v/2)J，复坐标平均方差为 v·div(m)/(2D)。 |
| denoiser / 去噪器；uncertainty quantification / 不确定性量化 | Manor–Michaeli，ICLR 2024，[原文](https://arxiv.org/html/2309.13598v2)，§3.2 Theorem 2 式(10)–(11)；§4.1 Algorithm 1 与式(15)。支持利用已训练去噪器及其输入导数估计后验不确定性，无需额外训练。本文使用随机方向中央差分估计平均方差；不将该具体估计器或原文运行时间结论照搬为本文原创/实证。 |
| without additional training for variance estimation | 本文对上述恒等式的实现描述：省去独立方差网络训练；仍需训练信道去噪器和活动分类器，有限差分仍有推理开销，不保证精度或收敛。Cai [v2](https://arxiv.org/html/2506.00581v2) §IV-C 式(52)–(54) 的二阶监督依赖一阶估计，既允许顺序训练也允许阻断目标梯度的同时训练。正文采用正面功能描述，不将 Cai 写成只允许一种训练流程。 |
| preconditioning / 预条件 | Karras 等，NeurIPS 2022，§5 式(7)–(8)、Table 1；归一化输入、输出与跳跃连接。保留为网络实现/训练设置，系数在推理中仍使用，并非训练结束后删除。白噪声实方差为 v/2。历史有色实现的矩阵推广据 Albuquerque–Pearson，NeurIPS 2024，Appendix B.1 式(67)–(68)、(73)、(77)–(78)。 |

公式及证据边界见[本轮核验](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/white_mainline_revision_20261105/README.md)。以下条目为历史记录。

**2026-11-04 最新名称简化（作者确认）：** **CGP-MP** 替代 GP-MP-C，C 表示 colored Gaussian noise training，GP/MP 对应 generative-prior/message passing。此名称是本文作者指定标签，未声称为已有文献的算法名；只是调整字母位置并减少一个连字符，原术语出处和方法含义沿用下文记录。估计相位版为 **CGP-MP-EP**；**GP-MP** 保留给当前结构的白噪声训练消融；**STMP** 为含学习密度比活动更新的三网络适配基线。历史名称按日期理解。见[同步记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/algorithm_name_cgp_mp_20261104/README.md)。

**2026-11-04 最新命名（作者确认）：** 现有三网络 AFDM 对照称 **STMP**，保留 Cai 的白噪声一、二阶网络与消息传递，并以学习密度比估计替换其活动概率公式；原文为 Cai §III-B, PDF p.7, 式(28)–(31)。**GP-MP-C** 为当前有色方法；**GP-MP** 为保持当前架构及接收机设置的白噪声训练消融，分类器随各自去噪器重新训练。GP-MP/GP-MP-C 是作者指定标签，不是文献既有方法名。历史同名记录按当时版本理解。Wei–Yuan *Learned Score-Based Turbo Message Passing for Channel Recovery From Spatially Compressed Measurements*, arXiv:2610.17785v1, Sec. I, PDF p.1 讨论有限维结构化压缩下的 AWGN 模型局限，只支撑失配动机，不提供本文 AFDM 有色训练的效果保证。原文、实现与比较边界见[本轮依据](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/stmp_baseline_white_ablation_20261104/README.md)。

**2026-11-03 最新完整搭配核查：** 见[逐项核查与替换表](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/prose_terminology_20261103/TERMINOLOGY_AUDIT.md)。出处必须支持完整搭配及其使用对象，不能以两个单词分别有出处代替搭配证据。当前稿件将 channel/conditional/joint moments 具体写成 mean and variance 或 mean and covariance；activity evidence、new-message weight、first-order atom approximation 等也已改为相应概率计算、damping factor 和 first-order linear approximation。本文模块名与算法标签继续明确登记为作者命名，不能冒充文献原名。

**当前算法展示名（2026-11-03 作者确认）：** 主算法为 **GP-MP-CCD**，白噪声训练基线为 **GP-MP**，估计相位版本为 **GP-MP-CCD-EP**；EP 表示 estimated phases。密度比估计仍属于完整算法，名称不再加 DRE 后缀。对应关系和出处见[本轮记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/algorithm_name_simplify_20261103/REVISION_NOTES.md)；下文按日期保留旧名称及其修订历史。

### 2026-10-25 有色噪声独立去噪实验

独立 AWGN 去噪沿用 Cai [v2 §VI-B、Fig.4](https://arxiv.org/html/2506.00581v2#S6.SS2)；相关噪声去噪的来源见 [D-GEC §III-B、§IV-A](https://arxiv.org/html/2206.05049v2#S3.SS2)。本项目采用的 Kronecker 协方差、固定平均功率、alpha 扫描和接收机列相关形状对照为明确的项目设置，见[实验协议](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/COLORED_DENOISING_EXPERIMENT_20261025.md)。alpha 是协方差因子的混合权重，不将其称为所有坐标对的相关系数；合成已知 C 与接收机估计 C 分开报告。

### 2026-10-24 C-STMP与DU的项目名称及接口

| 名称或术语 | 原文定位 | 本项目使用边界 |
|---|---|---|
| deep unfolding / 深度展开；DU（用户指定展示名） | Hershey、Le Roux、Weninger，[arXiv:1409.2574v4](https://arxiv.org/pdf/1409.2574)，PDF p.1摘要与§1；§2式(3)–(4)，PDF pp.4–5 | DU指项目已有十层展开模型；只改展示和登记名称，`proposed`作为历史别名保留，不把项目架构归为原文实证 |
| C-STMP（colored，用户指定项目候选名） | 母体STMP：Cai等，[v2](https://arxiv.org/html/2506.00581v2)，§III–V；有色Gaussian参数化来源见[前次核查](../../reference/reviews/colored_architecture_review_20261024/preconditioning.md) | C-STMP不是原文既有方法名；本次网络有色训练，但推断C=vI、标量反馈、旧分类器，不能称完整D-GEC或完整有色消息接口 |
| Jacobian of the conditional mean、conditional covariance / 条件均值Jacobian、条件协方差 | Dytso–Poor–Shamai，[v1](https://arxiv.org/pdf/2104.01883)，§IV Proposition 1式(22)、Corollary 1式(23)，PDF pp.5–6 | 本项目输出为行的Jacobian满足P=JΣ；复标量方差tr(P)/4096。随机符号中央差分及复维归一化为[本项目推导](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/C_STMP_DERIVATION_20261024.md)，有限网络导数迹不自动等于条件MSE |


### 2026-10-23 四基线的GFRA术语和判决来源

SOMP（simultaneous orthogonal matching pursuit）沿用 Tropp Algorithm 3.1；GFRA 应用另据 [Zhou v2](https://arxiv.org/pdf/2201.02084v2) §IV-C、PDF p.10 式(27)、脚注3及Algorithm 1。归一化能量门限0.1是该文经验设置；不能称为统计最优门限。CG-AD（channel gain-based activity detector）与BI-AD（belief indicator-based activity detector）沿用 [Ke v4](https://arxiv.org/pdf/1906.09867v4) §III-B、PDF p.7 式(39)–(41)，二者分别使用幅度和稀疏后验指标，并聚合跨观测判决；不能把任意路径概率改称用户活动后验。

MP-BSBL（message passing-based block sparse Bayesian learning）的GFRA原始来源为 Zhang 等 TVT 2018；此次原始全文未取得，具体用户块精度及噪声更新核对 [Zhaoji Zhang等2019原文](https://arxiv.org/pdf/1910.02953v1) §II-B/C、PDF pp.4–5及p.10 Table IV。GGAMP-SBL（Gaussian GAMP-based SBL）依据 [Al-Shoukairi等2018](https://phil-schniter.web.app/pdf/tsp18_sbl.pdf) §III、Table I、PDF pp.4–5；其内层GAMP/外层EM不能与当前单循环无阻尼实现混同。

GNN-ASPL依据 Ding六页稿（仅本地历史资料：`reference/literature/ding2026.pdf`） pp.3–5；p.4式(27)能量读出与路径稀疏概率须区分，p.5§IV-A每SNR单独训练不能改述为混合SNR共享权重。Off-grid SBL沿用 [Wei v1](https://arxiv.org/pdf/2101.05629v1) §III–IV、Algorithm 1及§VI-A；原文提供OTFS信道估计，不提供本项目GFRA用户读出。“AFDM/MMV适配”“跨SNR固定门限候选”仅描述项目操作，不是新增论文算法名称。来源、证据等级和当前差异见[专项报告](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/BASELINE_GFRA_AUDIT_20261023.md)。

**2026-10-23 稿件标签更新：** 原 DCN 改为 [TWC-1](https://github.com/RESET-cpu/afdm-gfra/blob/416a4dd4bd219dd9fb5049294bc02f4854f472f4/paper/STMP/README.md)，原 TWC 改为 TWC-2（历史路径，见迁移记录：`paper/DU/README.md`）。这是作者指定的稿件编号，不是算法名称；下文历史记录保留当时标签与文字路径，导航链接更新到新目录。文献中的期刊缩写 TWC 保持原义。

2026-10-12：协方差条件重训及完整二阶矩相关条目作为已归档研究（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/archive/covariance_training_20261012/README.md`）的来源记录保留；当前采用原三模块路线，状态与后续方向见 [CURRENT_STAGE.md](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/CURRENT_STAGE.md)。

本页记录当前系统模型和七个算法入口使用的术语。来源定位沿用已核对的论文记录；
完整日期记录、诊断公式和历史方法见整理前术语台账（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/archive/workspace_organization_20261011/before/docs/TERMINOLOGY.md`）。
项目参数、软件函数名和公式编号按操作直接描述。

| 原词或忠实译名 | 原文定位 | 当前使用 |
|---|---|---|
| affine frequency division multiplexing、discrete affine Fourier transform、chirp-periodic prefix / AFDM、离散仿射傅里叶变换、啁啾周期前缀 | [Bemani 等作者稿](https://arxiv.org/html/2204.12798v2)，§II-B 式(11)–(16)、§III-A 式(18)–(19) | 波形、DAFT 与前缀定义；具体展开见 SYSTEM_MODEL |
| fractional delay、fractional Doppler、effective channel matrix / 分数时延、分数 Doppler、有效信道矩阵 | Huang（历史路径，见迁移记录：`reference/huang2026_prior_agnostic_afdm_diffusion.pdf`），§II 式(4)–(5)，p.2950 | 连续物理路径；本项目的符号换算按 SYSTEM_MODEL 说明 |
| likelihood-annealed Langevin dynamics、posterior sampling / 似然退火 Langevin 动力学、后验采样 | Huang 2026（历史路径，见迁移记录：`reference/huang2026_prior_agnostic_afdm_diffusion.pdf`），摘要 p.2949，§III-B 式(8)–(10) p.2951，Algorithm 1、Fig.3 p.2952 | 文献对照：在单用户 SISO 的完整 AFDM 信道矩阵上，以观测残差、学习的先验 score 和随机扰动进行多噪声层级的迭代。当前主线是线性模块与局部 score 去噪器的消息传递；原文 Fig.4 的性能结论不自动成为当前 JADCE 的保证。 |
| annealed Langevin dynamics / 退火 Langevin 动力学 | [Arvinte–Tamir 作者稿 v2](https://arxiv.org/html/2204.07122v2)，§II-B 式(4)–(5)、§III-B 式(15)–(17)、Algorithm 1；[作者测试代码](https://github.com/utcsilab/score-based-channels/blob/main/src/score_based_channels/test_score.py) L129–157，2026-10-12 核对 | 已知活动集合诊断（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_known_activity_score_20261012/ALGORITHM.md`）使用同一冻结 first 网络和原始观测残差。复数方差、梯度、随机扰动统一按该文件推导；两种退火、步长、温度与固定末步读出为本实验设置。有限噪声下的似然是近似，有限网络和迭代不保证精确后验采样；不称为 Huang 实验复现。 |
| likelihood score、prior score / 似然 score、先验 score | Huang 2026 §III-B 式(9)–(10)，p.2951，Algorithm 1 p.2952 | 对照时从 log p(Y\|H)=−‖Y−HX‖²/σ_z²+常数直接求导：Wirtinger 导数 ∂log p/∂H*= (Y−HX)Xᴴ/σ_z²；对应实坐标梯度整体多因子2。原文式(10)和 Algorithm 1 印刷为 +(HX−Y)Xᴴ，与其梯度上升更新的符号不一致；已视觉核对并用合成有限差分检查正确方向。此处只记录复现所需的符号核查，不据此判定原实验代码采用了该印刷符号。 |
| array response vector、common spatial direction / 阵列响应向量、共同空间方向 | [Li–Gao–Xia](https://arxiv.org/html/2207.11958v2#S2.SS3)，§II-C 式(8) | 每用户共享方向的物理模型 |
| variational line spectral estimation (VALSE)；posterior probability density functions / 变分线谱估计、后验概率密度 | [Badiu–Hansen–Fleury](https://arxiv.org/pdf/1604.03744)，§II–III 式(6)–(12)，PDF pp.3–4 | 20261013未知方向调研：借鉴对连续方向分布取期望，不能把原Bernoulli–Gaussian幅度更新直接称为当前小网络算法；项目适配与限制见调研（历史路径，见迁移记录：`reference/direction_score_inference_20261013/REPORT.md`） |
| multisnapshot VALSE (MVALSE) / 多快拍VALSE | [Zhu等](https://arxiv.org/pdf/1803.06497)，§III 式(14b)、(16)、(19)–(20)，PDF pp.6–7 | 阵列响应的后验期望不同于在单一方向估计处取值；多快拍方向更新含其他分量和交叉协方差。当前G各元素有结构，不能原样采用独立Gaussian幅度模型 |
| multidimensional VALSE (MDVALSE) / 多维VALSE | [Zhang等](https://arxiv.org/pdf/1912.11759)，§III-A 式(14)–(16)，PDF p.5 | 二维方向分布近似的参考；项目物理方向余弦圆盘域和神经先验需另行适配，尚未实施 |
| likelihood ratio trick / 似然比技巧 | [Rizvi–Pettee–Nachman](https://arxiv.org/html/2305.10500v1#S2)，§II 式(6)–(12) | 平衡BCE的理想分类器odds对应密度比；有限证据网络需校准。方向积分的比值恒等式及全协方差展开为项目直接推导（历史路径，见迁移记录：`reference/direction_score_inference_20261013/REPORT.md`），非该论文现成算法 |
| local tilted expectation–maximization；damping / 局部倾斜分布期望最大化、阻尼 | [Na–Wadayama 2026预印本](https://arxiv.org/html/2607.14597v1)，§II-B 式(4)–(5)、Algorithm 1；§II-D | 借鉴模块内参数与矩更新的一致性；其Gaussian cavity、精确score及可辨识性假设并未在本项目成立，不能移植近oracle性能或固定点最优性结论 |
| turbo message passing、Gaussian projection、extrinsic message / turbo 消息传递、Gaussian 投影、外信息消息 | [Cai](https://arxiv.org/html/2506.00581v2#S3)，§III-A–B 式(6)–(42) | 两模块更新、受限协方差与 Gaussian 消息相除；THEORY T3–T5、T13–T17 |
| Generalized Expectation Consistency (GEC)、block uniform diagonalization / 广义期望一致性、分块均匀对角化 | [Fletcher等](https://arxiv.org/pdf/1602.07795v2)，§II-A 式(8)–(9)、§II-B Algorithm 1，PDF pp.2–3 | 20261012均值反馈研究的候选：每用户为一块、块内保留一个标量。复数MMV线性查询及外信息公式是项目推导（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_mean_feedback_20261012/ANALYSIS.md`）。已实现并完成六条件验证（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_mean_feedback_20261012/user_scalar_pilot/REPORT.md`）：完整候选未减少漏检，尚未采用；有限网络的均值/条件MSE不自动满足原文精确估计函数及收敛假设 |
| Tweedie's formula、denoising score matching、second-order score matching / Tweedie 公式、去噪得分匹配、二阶得分匹配 | [Cai](https://arxiv.org/html/2506.00581v2#S4)，§IV-A–C 式(43)–(54) | 一阶均值与二阶全坐标平均迹；有限一阶均值下的条件 MSE 关系见 THEORY T8–T11 |

2026-10-16的AWGN损失加权对照（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_awgn_weighting_20261016/PROTOCOL.md`）
沿用上述DSM/second-order score matching的术语。将原单样本损失分别乘v/E[v]和v²/E[v²]，
是根据Cai式(48)–(49)、(53)–(54)直接变换损失权重；
不将该项目选择另称为已有算法，也不声称正权重能保证有限网络读出改善。

后续均值尺度与辅助读出对照（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_awgn_mean_scale_20261016/REPORT.md`）
仍在 Cai §IV-A–C 式(43)–(54)的 AWGN 实坐标/复噪声方差约定下操作。
以训练数据最小化 E||cF−H||² 得到 c=E Re〈F,H〉/E||F||²，是本文明确展开的输出修正，
不是文献中另一个已命名算法，也不能将 cF 自动称为原物理先验的精确 Tweedie 均值。
有限均值风险 R_f=tr Cov(H|x)/D+||E[H|x]−f||²/D 来自条件平方误差直接展开；
原分类器仍可使用原 F0(x,v) 特征，另一均值输出的改变不强制改变该分类器的输入定义。
对应“活动证据/密度比”的来源和训练先验校正沿用下方 Menon–Ong §3–4.2 条目。

| pseudo AWGN observation model | Cai §IV-A 式(43)、§V-B1 | 去噪查询的工作模型；实际有限 AFDM 查询的适用性属于近似 |
| Gaussian approximation、device activity denoiser / Gaussian 近似、设备活动去噪器 | Cai §III-B1–B2 式(26)–(30) | 网络查询超出支持范围时，以保留的 Gaussian site 计算解析活动概率 |
| density ratio estimation、class-probability estimation、logistic loss / 密度比估计、类别概率估计、logistic 损失 | [Menon–Ong](https://proceedings.mlr.press/v48/menon16.pdf)，§3 式(6)–(8)、§4.2 式(16)–(17)，pp.305–306 | 分类器 logit 经训练先验校正，再加入公开活动先验；THEORY T15 |
| damping / 阻尼 | Cai §V-B1 式(57)–(58) | 均值与协方差的算术插值；当前新值权重 0.2 是项目设置，选择依据见 默认设置记录（历史路径，见迁移记录：`result/proposed_default_20261014/DEFAULT_SELECTION.json`）；历史图配置保留 0.1 |
| vector approximate message passing (VAMP)、divergence / 向量近似消息传递、散度 | [Rangan–Schniter–Fletcher](https://arxiv.org/pdf/1610.03082)，Algorithm 2 第5–8行，PDF p.4；§III-C，PDF p.6 | 20261012实验候选对完整联合映射 pF 取实坐标平均散度，并成对定义外信息均值和方差。有限差分、固定探针及沿用本项目比例裁剪是实验设置；不是原文的精度裁剪，消息方差不自动等于真实MSE |
| group averaging / 群平均 | [Chen–Dobriban–Lee](https://papers.nips.cc/paper_files/paper/2020/file/f4573fc71c731d5c362f0d7860945b88-Paper.pdf)，§3.1 Lemma 3.2、Proposition 3.3，§4 | 20261012实验检查公共复相位旋转；四相位组合和混合矩按实验协议定义。固定查询上的风险依据不保证闭环性能；条件分布平均与先验密度混合是不同操作。20261015增加对完整接收机输出的群平均候选：相位前端运行一次，四个整体旋转各自独立完成条件推断后合并；公式和期望平方误差的适用条件见 THEORY §12，门限 AER 另作独立验证 |
| equivariance / 等变性 | [Chen–Dobriban–Lee](https://papers.nips.cc/paper_files/paper/2020/file/f4573fc71c731d5c362f0d7860945b88-Paper.pdf)，§1 PDF p.1 对网络等变性的说明，§2 对群作用的定义 | 当前相位不变信道先验和AWGN下，F(gR,v)=gF(R,v)由项目条件均值定义推出。训练中惩罚偏离该关系的候选公式（历史文件已清理，原路径：`experiments/proposed_mean_feedback_20261012/PLAN.md`）已进入独立训练对照（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_phase_training_20261012/PROTOCOL.md`），效果待验证；它不是引用论文已验证的JADCE算法，部署仍使用一次一阶评估 |
| rank-r matrix approximation、low-rank matrix fitting / 秩r矩阵近似、低秩矩阵拟合 | [Xu等](https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/ell2.12379)，§3 “Low-rank matrix fitting based channel estimation”，式(7) | 20261012保存均值诊断对M×NP天线展开保留一个奇异分量，只用已有F；未采用该文矩阵补全流程。样本秩一不推出后验均值秩一，代数反例、NMSE与固定线性响应见分析记录（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_mean_feedback_20261012/evidence/mean_structure_analysis.json`），可选秩一均值反馈已接入Receiver；闭环实验（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_rank_one_20261012/REPORT.md`）在用户要求下停止，仅一个开发条件完成三版本配对，不能作总体性能结论。训练时对去噪均值的其余奇异值能量加惩罚属于项目待验证目标，不是该文已验证的score训练方法 |
| Jacobian of the conditional mean、conditional covariance / 条件均值的 Jacobian、条件协方差 | [Dytso–Poor–Shamai](https://arxiv.org/pdf/2104.01883)，§IV Proposition 1 式(22)、Corollary 1 式(23)，PDF pp.5–6 | 20261012固定查询检验：实坐标噪声为(v/2)I时，精确条件均值的Jacobian为(2/v)Cov，半正定。有限网络负方向响应违反该必要性质；这一判断不要求实际被查询R本身来自训练总体 |
| Tweedie's formula / Tweedie公式（一般协方差） | [Dytso–Poor–Shamai](https://arxiv.org/pdf/2104.01883)，PDF p.2 式(3)，§IV 式(22)；[Cai](https://arxiv.org/html/2506.00581v2#S4)，§IV 式(43)–(54)为标量噪声的DSM与二阶读出 | 20261012开发试验将一般实协方差公式写为F=R+C(s_re+i s_im)/2，C作用天线轴。加权DSM、白化条件风险与B≈aC均为本项目明确推导/约束，非原文已有算法名称。二阶理想迹对应Z=(C/v)^−1/2R的实坐标；有限first时为风险读出，不能称原R坐标的精确Hessian。推导和限制见docs/history/results/proposed_ablation_20261012/spatial_score_math_audit.md |
| non-isotropic Gaussian denoising diffusion models / 非各向同性 Gaussian 去噪扩散模型 | [Voleti–Pal–Oberman](https://arxiv.org/html/2210.12254v2)，§3 式(10)–(16)、Appendix E 式(93)–(100)、(103) | 有色 Gaussian 下训练 score 的先例；原文噪声形状 Σ 固定，不作为任意逐查询协方差条件网络的实证 |
| preconditioned score / 预条件 score | [Mathieu 等](https://arxiv.org/pdf/2307.05431v1)，§3.1 式(5)–(6)，App B.3 式(29)、(37)–(39)，Table 3，PDF pp.18–19 | 原文学习 K 乘 score，噪声协方差为 σ_t²K。项目候选 u=(C/v)s 只借鉴输出含义，白化均值损失和暖启动约束另行推导，尚未训练验证 |
| anisotropic denoising score matching、covariance conditioning / 非各向同性去噪得分匹配、协方差条件输入 | [Zilberstein 等](https://arxiv.org/html/2605.15487v1#S3)，§3.2 式(9)，§3.3，App C.1 式(41)–(46) | 变化的协方差下训练 score 的直接依据；原文实现为空间域或 Fourier 域对角族。项目完整天线 C 与采样律另行定义；旧试验为512→64条件分支，新从头训练方案为完整矩阵特征加尺度、512维条件注入。两者都不是原文已验证的本项目设计 |
| covariance score / 协方差 score | Zilberstein 等 §3.2 式(10)、App A | 指能量对噪声协方差的导数，不能与 Cai 的输入二阶 score 或本项目有限均值条件风险混称；当前仅调研，未接入算法 |
| network preconditioning / 网络预条件 | [Karras 等 EDM](https://proceedings.neurips.cc/paper_files/paper/2022/file/a98846e9d9cc01cfb87eb694d946ce6b-Paper-Conference.pdf)，§5 式(7)–(8)、Table 1；[作者实现 EDMPrecond](https://github.com/NVlabs/edm/blob/main/training/networks.py#L569-L603) | 20261012从头训练方案使用 F=(I+C)^−1R+[C(I+C)^−1]^(1/2)u((I+C)^−1/2R,C)，并对输出尺度作逆加权均方回归。这是本项目按单位复功率定义的矩阵推广，非原文已有完整矩阵公式；不是对物理信道严格白化的声明。见 docs/history/experiments/covariance_training_20261012/ALGORITHM.md A11–A12 |
| second-order score matching、conditional covariance / 二阶得分匹配、条件协方差 | Cai §IV 式(45)、(51)–(54)；Dytso §IV 式(22)–(23) | 新方案由理想 Hessian—条件协方差关系出发，直接回归冻结有限 F 的完整天线条件误差二阶矩 B_F=E[(H−F)(H−F)ᴴ/L\|R,C,a=1]。矩阵 Frobenius 回归及 PSD 输出是本项目推导，有限 F 时不能称为精确输入 Hessian；亦不是 Zilberstein 的 covariance score。见新方案 THEORY.md 式(9)–(14) |
| Gaussian projection、extrinsic message / Gaussian 投影、外信息消息（新协方差方案） | Cai §III-B 式(25)–(42) 为标量/受限消息的原文依据 | 新方案按用户和列对角块平均保留 M×M Hermitian 矩阵，活动混合后只作一次共同精度相减；精度与精度加权均值同权插值及其正定步长条件由新方案 ALGORITHM.md A18–A20 直接推导，不另造算法名称，不声称具有已有收敛定理 |
| Gaussian approximation、device activity denoiser / Gaussian 近似、设备活动去噪器（矩阵活动证据候选） | [Cai v2 §III-B1–B2](https://arxiv.org/html/2506.00581v2#S3.SS2)，式(24)–(30)；[作者代码固定提交](https://github.com/chang-cai/score-massive-connectivity/blob/0c75680c966dcb8e46250de146f4c27e9294c283/main_stmp_jadce.py#L193-L210) | 将论文的 Gaussian 相除与活动概率公式推广到天线矩阵 C、B；T=(B⁻¹−C⁻¹)⁻¹，U=T(B⁻¹F−C⁻¹R)，活动证据为 CN(R;U,C+T) 与 CN(R;0,C) 的逐列乘积比。要求 0≺B≺C，不声称该上界对一般先验逐点成立，也不把有限均值误差二阶矩等同于精确后验协方差。推导的等价白化表达和数值核对见 docs/history/experiments/covariance_training_20261012/check_analytic_activity.py 与 docs/history/results/covariance_training_20261012/analytic_activity_check002/RESULTS.json；当前仅为离线构造检查。所核对作者提交的活动函数实际用固定零均值 Gaussian 先验，没有使用学得的信道外信息参数，需与论文式(26)–(30)区分。 |
| power posterior、thermodynamic integration、marginal likelihood / 幂后验、热力学积分、边际似然 | [Friel–Pettitt 所读作者早期稿](https://www2.stat.duke.edu/~scs/Courses/Stat376/Papers/NormConstants/FrielPettitPath05.pdf)，§3 式(4)–(5)、§3.1 式(6)；[Friel–Hurn–Wyse v2](https://arxiv.org/html/1209.3198v2#S2)，§2 式(6)–(11) | 20261012活动证据调研：在固定C的proper complex Gaussian查询下，幂β的活跃后验等于(R,C/β)的后验。项目推导ell=∫₀¹[2Re tr(RᴴC⁻¹mβ)−tr(mβᴴC⁻¹mβ)−L tr(C⁻¹Vβ)]dβ；只需列对角协方差块平均，不要求后验Gaussian、各列独立或Vβ<C/β。用现有first/second代入是另行提出的近似，二阶条件误差矩不自动等于Vβ，端点和求积误差必须保留。推导、版本边界及精确合成检查见 调研来源（历史路径，见迁移记录：`reference/activity_evidence_20261012/SOURCES.json`） 和 数学检查（历史路径，见迁移记录：`reference/activity_evidence_20261012/MATH_CHECKS.json`）；尚未运行该候选的学习网络或接收机比较。 |
| pointwise MMSE、probability density via MMSE / 逐点MMSE、通过MMSE表示概率密度 | [Kong–Brekelmans–Ver Steeg](https://arxiv.org/html/2302.03792v1#S3)，§2 式(4)–(5)、§3 式(7)–(8)、Appendix A.1–A.2 | 去噪误差差值在噪声尺度上的积分恢复逐点log density ratio的原文依据。项目针对q1(R\|C)与q0(R\|C)的复矩阵转换、以及从H的去噪器恢复R的去噪器，记录于上述SOURCES.json；不能把平均I-MMSE关系或有限网络的任意MSE直接称为精确活动证据。 |
| probability flow ODE、instantaneous change of variables、Skilling–Hutchinson trace estimator / 概率流ODE、瞬时变量变换、Skilling–Hutchinson迹估计 | [Song 等](https://arxiv.org/html/2011.13456v2#S4.SS3)，§4.3 式(13)、Appendix D.2 式(38)–(40) | 调研备选：一阶网络转score后，通过ODE及散度积分求其流模型定义的似然。该密度与真实物理分布的偏差、数值积分和随机迹估计误差需区分；当前二阶条件误差矩不是有限一阶网络的精确Jacobian，不能直接替代其散度。尚未实施。 |
| calibrated discriminative classifier、likelihood ratio / 经校准的判别分类器、似然比 | [Cranmer–Pavez–Louppe v2](https://arxiv.org/html/1506.02169v2#S2.SS2)，§2.2 Theorem 1、式(2.4)、(2.10)，§2.3、§3.3 | 当前activity模块的补充依据：理想分类器或其单调变换与密度比相关；有限分类输出需验证校准与检测能力，条件C及训练/部署先验差异不能忽略。原文不保证任意分类器raw logit都是精确证据。 |
| denoising-based VDAMP (D-VDAMP)、colored noise denoising / 去噪型VDAMP、有色噪声去噪 | [Metzler–Wetzstein](https://arxiv.org/pdf/2010.13211v1)，§1末段、Algorithm 1，§2.2–2.3，PDF pp.1–3；VDAMP为variable density AMP | 子带方差消息与对应条件去噪网络协同设计的先例；其 weak state evolution 是经验模型，不移称为本项目的理论保证 |
| denoising generalized expectation-consistent approximation (D-GEC)、corr+corr | [Shastri 等](https://arxiv.org/pdf/2206.05049v2)，§III-B 式(39)–(41)，§IV-A 式(42)，PDF pp.16–18 | 用同协方差独立噪声样本作为去噪网络辅助输入；一般形式与小波子带训练族分开表述。当前用于文献对照，不是项目已采用算法 |
| Fast Iterative REnoising (FIRE)、colored renoising | [Bendel 等](https://arxiv.org/html/2501.17468v4#S3.SS1)，§3.1 式(8)–(19)、Theorem 1 | 通过补加有色噪声使查询误差近似白噪声的替代路线；依赖误差模型，未在本项目实施，也不能消除已有信号方向偏差 |
| MSE estimation / 均方误差估计 | [Ma–Ping OAMP](https://arxiv.org/pdf/1602.06509v3)，§III-I 式(30)–(31)，PDF p.5 | 20261012观测功率初始化控制采用零均值初始估计下的复数MMV能量式，扣除公开噪声后估算输入共同方差；不是在当前物理相关输入上认证点态无偏 |
| simultaneous orthogonal matching pursuit / 同时正交匹配追踪（SOMP） | [Tropp 作者预印本](https://tropp.caltech.edu/papers/TGS05-Algorithms-Simultaneous-I-preprint.pdf)，Algorithm 3.1，pp.6–7，§3.2 | 多测量列共享支撑；64 原子预算和已知噪声残差停止为项目设置 |
| generalized approximate message passing sparse Bayesian learning / GAMP-SBL | Zhang（历史路径，见迁移记录：`reference/zhang2023_gamp_sbl_grant_free_noma.pdf`），pp.15058–15059 式(3)–(19)、Algorithm 1 | 复数模型中跨天线共享行精度和公共噪声精度，明确作为 MMV 适配 |
| Gamma prior、MAP update / Gamma 先验、MAP 更新 | Zhang 式(3)–(4)、(16)、(18)–(19) | 共享行精度和噪声学习；用公开噪声确定 Gamma 超参数是项目数值设置 |
| graph neural network-based adaptive sparsity pattern learning / GNN-ASPL | Ding（仅本地历史资料：`reference/literature/ding2026.pdf`），pp.3–5 式(12)–(28)、§III-B/C | 当前十层展开网络、图内信息传播与逐层训练；具体训练分布见 TRAINING |
| decision threshold / 判决门限 | Ding p.4 式(27) | 系数块能量按用户间最大值归一化；公共 SNR 选取冻结节点的规则是项目设置。20261015 Proposed 可选最终判决使用完整估计能量除以公开噪声方差，并同时要求原概率不低于0.5；该归一化和两条件规则为项目明示公式 THEORY P3，不称为 Ding 的同一算法，也不将能量分数称为概率 |
| EM-GAMP；Gaussian log-likelihood ratio / Gaussian 对数似然比 | Zhao（历史路径，见迁移记录：`reference/zhao2025_mixed_fronthaul_jadce.pdf`），pp.4123–4126 式(20)–(40)、(49)、(51)–(57)、Algorithm 1 | 全分辨率特例，式(38)方差更新及 Gaussian block LLR；AFDM/MMV 适配与待验证状态见 BASELINES |
| on-grid / 网格内；off-grid / 网格外 | [Wei 等作者稿](https://arxiv.org/pdf/2101.05629v1)，§III-B pp.11–12 式(17)–(24)、§VI-B pp.26–27 | 基线使用有限整数网格，评价信道允许连续参数偏离网格 |
| spike-and-slab prior / 尖峰与连续分布混合先验；conditional slab variance / 非零分量条件方差 | Ding pp.3–4，§III-A 的 p(Z\|λ) 及 Σ 对角元 γ 定义 | 20261012逐 SNR 的 on-grid 训练拟合只统计物理占用行，合并同一行的路径碰撞。固定零均值和共享标量是项目设置；当前正式混合训练 checkpoint 已采用该口径 |
| off-grid sparse Bayesian learning / 网格外稀疏贝叶斯学习 | [Wei 等作者稿](https://arxiv.org/pdf/2101.05629v1)，§III-B 式(17)–(24)，§IV 式(35)–(57)、Algorithm 1（PDF p.18），§V Algorithm 2 | 已接入 `offgrid_sbl`。原文向量化“1D”模型包含时延和多普勒偏移；本项目的 AFDM/MMV 方差及偏移更新推导见 OFFGRID_BASELINES。固定公开噪声、每用户相关性筛选、区间约束是明确的项目设置 |
| first-order linear approximation / 一阶线性近似 | [Wei 等作者稿](https://arxiv.org/html/2101.05629v1)，§III-B 式(17)–(24) | SBL 在固定中心计算时延与 Doppler 导数，以偏移修正字典。20261012 审查另外记录精确预测与一阶预测的相对距离；这一诊断量由项目定义，不等同于信道 NMSE |
| virtual sampling grid、virtual sampling resolution / 虚拟采样网格、虚拟采样分辨率 | [Wei 作者稿 v1](https://arxiv.org/pdf/2101.05629v1)，§III-B p.11、式(18)前的定义，§VI pp.23–26、Fig.5–7 | 原稿扫描间距 0.2–0.9，Fig.5/6 分别为两维均 0.5/0.8。审查将 AFDM 固定时延采样点由 112 增至 448；四倍密度由项目校准确定，归一化间距不能跨波形直接照搬。完整配置来源见 OFFGRID_BASELINES 的 20261013 溯源 |
| convergence tolerance / 收敛容差 | [Wei 作者稿 v1](https://arxiv.org/pdf/2101.05629v1)，Algorithm 1 p.18、§VI p.24 | 原稿按方差超参数相对变化不超过 10^−3 停止，Tmax 未给出具体数值。本项目使用 10^−4 并额外检查偏移增量；600 次上限为项目校准预算 |
| hierarchical hyperprior distribution / 分层超先验分布（Wei SBL） | [Wei 作者稿 v1](https://arxiv.org/pdf/2101.05629v1)，§IV-A 式(26)–(29)，§IV-B 式(44)–(45)，Algorithm 1 | 20261013 独立对齐实验令物理系数方差先验 rho=0.01。列归一化 x_i=s_i h_i 后，方差乘 s_i²、Gamma 率参数除 s_i²；MMV 方差及噪声更新是项目推导，见 docs/history/experiments/offgrid_sbl_reference_20261013/PROTOCOL.md。原稿相关幅值初始化推广为跨天线相关幅值的均方根，明确不是原文已有 MMV 公式 |
| multi-snapshot Newtonized orthogonal matching pursuit (MNOMP) / 多快拍 Newton 化正交匹配追踪 | [Zhu 等作者稿](https://arxiv.org/pdf/1802.01266)，§II 式(1)，§III 式(6)、Algorithm 1（PDF p.7），§IV-A | 实现见 MNOMP 归档（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/archive/mnomp_20261014/README.md`）。原文为一维频率 MMV；AFDM 二维参数和范数可变的目标导数为项目适配 |
| learned denoising-based approximate message passing (LDAMP / L-DAMP) / 基于学习型去噪的近似消息传递 | [He等作者稿](https://arxiv.org/html/1802.01290v2)，§III-A式(4)–(8)、Fig.3；§IV-A；Huang p.2952 §IV / Fig.4、p.2953 [23] | 本项目加入完整复数AFDM信道、多天线通道和非活跃零信道训练，按作者仓库Algorithms/denoise.m的DnCNN分支选择噪声区间权重；GNN-ASPL同样属于学习型方法，但估计固定字典系数。L-DAMP不命名为连续路径参数估计器，适配与验证范围见LDAMP.md |
| Monte-Carlo approximation of divergence；Onsager correction term / 散度的Monte Carlo近似、Onsager校正项 | He等§III-A式(4)、(7)–(8)；复数矩阵扩展见本表2026-10-14/15补充 | 当前基线采用复数 Jacobian 部分迹 B_ab=(1/Q)Σ_i∂D_ib/∂R_ia，残差右乘B；BatchNorm推断统计冻结。早期实标量散度分母2QMNout仅属于历史实现，不是当前基线公式。代数核验不证明结构化AFDM满足AWGN或状态演化 |
| batch normalization / 批归一化 | [Ioffe–Szegedy 2015](https://proceedings.mlr.press/v37/ioffe15.pdf)，§3.1（PDF p.4）、Algorithm 2（PDF p.5）；He 等 Fig.3 | 区分训练时批统计与推断时固定统计。20261014 对照在训练期间也固定统计、继续学习仿射参数，这是项目实验选择，不归为原论文训练配方。噪声支路初始满足 F(x)=x 或 (1−a)x 是直接定义的参数设置，不另命名为已有方法 |
| stopping criterion / 停止条件；overestimating probability / 过估计概率 | Zhu §IV-A 式(11)–(16)，纯噪声多快拍投影及 DFT 网格停止分析 | 新 MNOMP 对每个单位范数粗列的 Gamma 尾概率取 0.01/D，再用事件并集上界；这是项目对相关字典的推导，不是原文公式原样复用，也不是自适应循环后的最终用户虚警率保证 |
| grid refinement SBL (GR-SBL)、grid evolution SBL (GE-SBL) / 网格细化、网格演化稀疏贝叶斯学习 | [AFDM 作者稿](https://arxiv.org/html/2512.14776v1)，§III-C/D 式(41)、(50)，Algorithm 1 | 候选文献原名；原文更新 Doppler，保留时延采样位置，不能据此称为本项目双分数参数方法 |
| normalized mean squared error / 归一化均方误差（NMSE） | Ding p.5 式(28)、§IV-B | 当前主统计为物理信道总误差能量除以总信号能量后转 dB；区别于逐场景归一化后求平均 |
| Brier score、logarithmic score / Brier 分数、对数分数 | [Dimitriadis–Gneiting–Jordan](https://publikationen.bibliothek.kit.edu/1000130510/106591216)，式(1)、Table 1；PNAS 2021，doi:10.1073/pnas.2016191118 | 活动验证使用二元形式 (p−a)² 及 −a log p−(1−a)log(1−p)。目标先验验证的正负类权重由项目另行定义，分数评价整体概率预测质量 |
| Cholesky parameterization、Gaussian log-likelihood / Cholesky 参数化、Gaussian 对数似然 | [Muschinski 等](https://arxiv.org/pdf/2102.13518)，§2.2 式(3)，PDF p.3；§4.2 式(11)–(13)，p.6；§4.4 式(17)，p.7 | 20261012二阶方向诊断以 S=LLᴴ 表示误差二阶矩，并考察 [log det S+tr(S⁻¹T)]/M。原文采用实 Gaussian 及逆 Cholesky 参数化；本项目复数形式、固定有限一阶均值时仍以条件误差二阶矩为最优解的推导见 REPAIR_PLAN。当前只完成保存输出与梯度诊断，替代训练目标尚未采用或验证 |
| reliability diagram、calibration / 可靠性图、校准 | Dimitriadis 等 PDF p.1，Reliability Diagrams: Binning and Counting；[Guo 等](https://proceedings.mlr.press/v70/guo17a/guo17a.pdf)，§2 式(1)–(3) | 活动验证保存概率分箱的平均预测、实测正类频率和样本数。公开先验校正后的概率与频率用同一目标先验类权重；分箱结果是描述性统计 |
| pairs cluster bootstrap / 成组 bootstrap | [Cameron–Miller](https://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015.pdf)，§II-F，pp.327–328 | 独立确认按物理 seed 有放回抽样，每次保留该 seed 的全部 SNR 和方法。原词的 pairs 指原文响应/设计联合抽取；本项目算法差值的配对结构由同一物理输入另行定义 |
| percentile method / 百分位法 | [Efron–Tibshirani](https://doi.org/10.1214/ss/1177013815)，§7 式(7.2)，p.68；正文通过[论文扫描转录](https://www.scribd.com/document/502901975/efron1986)核对 | 对按场景重抽样的算法差值取 2.5% 与 97.5% 分位数；重复次数、随机种子和差值方向在确认协议中固定，区间属于近似统计描述 |

至少一人活跃的活动生成、条件边缘概率和已知有效相位条件在
[SYSTEM_MODEL.md](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/SYSTEM_MODEL.md) 中直接定义；场景重抽样与结果复用范围见
[EXPERIMENT_PROTOCOL.md](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/EXPERIMENT_PROTOCOL.md)。这些条件按本项目公式和协议记录。

当前算法与源码位置见 [CODE_GUIDE.md](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/CODE_GUIDE.md)，其中 `proposed`、`somp`、`gamp`、`gnn`、`em`、`offgrid_sbl`、`ldamp`
是命令行标识。`run_spatial_score`、`SpatialConfig` 和 checkpoint 中的 `full_score` 为保留的软件字段。

2026-10-13 小网络训练审查补充，详见逐环节报告（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/small_training_audit_20261013/REPORT.md`）。

| 原词或忠实译名 | 原文定位 | 本轮使用范围 |
|---|---|---|
| RefineNet；multi-resolution fusion；cascaded residual pooling / RefineNet、多分辨率融合、级联残差池化 | Huang 2026，§III-A、Fig.1，p.2951；原文引用Lin等CVPR 2017 RefineNet | 原文指定的网络家族。当前16×16 `GlobalFirstScore`是残差卷积加全局线性混合，不能称同一RefineNet；本项目完整信道RefineNet的宽度及参数量也不能当作Huang披露的配置 |
| denoising score matching / 去噪得分匹配 | Huang 2026，§III-A 式(7)及其后实虚双通道说明，p.2951 | 原文复噪声方差、−N/σ²目标与实梯度措辞需区分约定。本项目按每实分量v/2训练缩放实score，均值为r+(v/2)s；核对通过但不宣称与未知作者代码逐项一致 |


2026-10-13 一阶网络训练与结构调研补充。以下仅为候选研究（历史路径，见迁移记录：`reference/first_score_improvements_20261012/REPORT.md`）的来源，不表示已经修改默认训练或获得性能收益。

| 原词或忠实译名 | 原文定位 | 本轮使用范围 |
|---|---|---|
| network preconditioning / 网络预条件化（标量 AWGN） | [Karras 等 EDM](https://proceedings.neurips.cc/paper_files/paper/2022/file/a98846e9d9cc01cfb87eb694d946ce6b-Paper-Conference.pdf)，§5 式(7)–(8)、Table 1–2 | 以 ν=v/2 及实坐标信号方差定义输入、跳连、输出尺度。参数化、损失权重、噪声采样分开比较；单位复功率对应实方差约 0.5，不是直接照搬图像 σdata=0.5。原有矩阵推广条目仍属先前研究 |
| magnitude-preserving；post-hoc EMA / 保持幅度；训练后构造 EMA | [Karras 等 EDM2](https://openaccess.thecvf.com/content/CVPR2024/papers/Karras_Analyzing_and_Improving_the_Training_Dynamics_of_Diffusion_Models_CVPR_2024_paper.pdf)，§2.2–2.5、§3.1–3.2、Appendix B.2/C | 记录激活、权重和更新尺度，比较 raw 与 EMA；后者需要训练期间的相应快照，不能从单个旧 EMA 任意恢复历史 |
| loss-second-moment sampling / 按损失二阶矩采样 | [Nichol–Dhariwal](https://proceedings.mlr.press/v139/nichol21a/nichol21a.pdf)，§3.3 式(17)，PDF p.5 | 改采样并保留逆概率修正；原文对 Lhybrid 未见帮助，损失二阶矩不等于梯度二阶矩，不宣称必然加速本项目 |
| Min-SNR-γ weighting / Min-SNR-γ 加权 | [Hang 等](https://arxiv.org/html/2303.09556)，§3.1–3.4、§4.2；ICCV 2023 | 对当前 clean-denoising 等价目标的相对乘子为 min(SNR,γ)/SNR，单位复功率时 SNR≈1/v；γ=5 直接降低 v<0.2 的相对权重。参数是候选而非 AFDM 最优值 |
| importance sampling；noise schedule / 重要性采样；噪声调度 | [Kingma–Gao](https://proceedings.neurips.cc/paper_files/paper/2023/file/ce79fbf9baef726645bc2337abb0ade2-Paper-Conference.pdf)，§3.1–3.2 式(5)–(7)、Appendix F 式(135)–(136) | 区分改变采样方差与改变积分目标；保持原目标需 p₀/q 修正，不能直接比较不同定义的训练 loss |
| Improved Noise Schedule for Diffusion Training；SpeeD | [Hang 等 ICCV 2025](https://openaccess.thecvf.com/content/ICCV2025/papers/Hang_Improved_Noise_Schedule_for_Diffusion_Training_ICCV_2025_paper.pdf)，§3.2–3.3 式(3)–(6)；[Wang 等作者稿](https://arxiv.org/html/2405.17403)，§2.3–2.4、§3.6 Table 5，CVPR 2025 发表 | 噪声分配的补充对照依据；图像中间噪声或 DDPM 时间阈值不能直接移为当前 v 阈值，原文加速倍数不移作本项目预期 |
| Perception Prioritized Training (P2) / 优先感知内容的训练 | [Choi 等](https://arxiv.org/html/2204.00227)，§3.2 式(8)、§3.4；CVPR 2022 | 仅作损失权重文献对照；不把图像感知偏好当作信道相位和小幅误差可以忽略的依据 |
| Co-domain Symmetry；Phase-Equivariant / 值域对称性；相位等变 | [Singhal 等作者稿 v2](https://arxiv.org/pdf/2112.01525v2)，§3.1–3.4，PDF pp.3–4，式(1)–(3)；CVPR 2022 版相应节为 pp.683–684，式号不同 | 构造公共相位等变层；不是任意逐天线旋转，也不要求固定先验下任意幅度缩放等变。普通复数卷积加非等变偏置/激活不能保证整体等变 |
| conditionally Gaussian；MMSE filter / 条件 Gaussian；MMSE 滤波器 | [Neumann–Wiese–Utschick 作者稿](https://arxiv.org/pdf/1707.05674)，§II–III 式(2)–(16)、§VI 式(47)–(50)；IEEE TSP 2018，DOI 10.1109/TSP.2018.2799164 | 未知潜参数时按后验平均条件滤波器，支持本项目多方向条件均值组合的设计动机；AFDM 与随机相位 LoS 不满足该文全部假设，不能直接套用闭式滤波器 |
| NCSNv2；CondInstanceNorm++；InstanceNorm++ | [Song–Ermon](https://arxiv.org/html/2006.09011v2)，§3.3 Technique 3、Appendix B.1 Tables 2–3 | 说明现有网络谱系；当前连续噪声 MLP 与条件 RefineNet 是项目变体，不能把输出 1/σ 缩放等同于采用完整 NCSNv2 |
| NCSN++；DDPM++；random Fourier feature embeddings | [Song 等](https://arxiv.org/html/2011.13456v2)，Appendix H.1–H.2、Fig.10 | 候选残差骨干与条件编码；attention 作用哪个轴由输入排布和实现决定，不自动代表天线交互 |
| posterior moments；posterior principal components / 后验矩；后验主分量 | [Manor–Michaeli](https://arxiv.org/html/2309.13598v2)，§3.2 Theorem 2 式(10)–(11)、§4.1；ICLR 2024 | 交叉核对均值导数与条件协方差，使用方向导数作诊断；有限网络的响应不自动是真实后验协方差 |
| Quasi-Conservative Score-Based Models (QCSBMs) | [Chao 等](https://proceedings.mlr.press/v202/chao23a/chao23a.pdf)，§4.1–4.2 式(12)–(16)、Algorithm 1；ICML 2023 | Jacobian 反对称部分的软惩罚；不等同于均值 Jacobian 半正定、正确 score 或 JADCE 收敛保证，需额外自动微分 |
| conditional flow matching / 条件流匹配 | [Zhang–Nadeem v1](https://arxiv.org/html/2601.13827v1)，§III-A–C 式(8)–(10) | 作为 MIMO 新近路线比较；线性 Gaussian 插值下的条件均值读出由公式直接推出，不移用其相对多步采样的加速倍数 |
| Preconditioned Flow Matching / 预条件流匹配 | [Ahamed 等 v2](https://arxiv.org/html/2603.02337v2)，§3.1–3.3，Theorem 3.3、Remark 3.6、Assumption 3.7；§4 Algorithm 1 | 2026 预印本补充：线性 Gaussian 与给定分量归属的混合模型中的方向尺度问题。不是当前 Adam/非线性网络收敛定理；非正交表示变换会改变 AWGN 协方差，不能直接套入原训练接口 |

2026-10-13 小网络数据物理审查补充，详见审查报告（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/small_data_physics_audit_20261013/REPORT.md`）。

| 原词或忠实译名 | 原文定位 | 本轮使用范围 |
|---|---|---|
| piecewise-continuous AFDM (PC-AFDM)；frequency wrapping；phase correction / 分段连续AFDM、频率折叠、相位修正 | [Cao–Shao 2026预印本](https://arxiv.org/html/2609.07480v1)，§II-A 式(1)–(3)、Proposition 1 | 用于描述并核对当前分数时延基函数的跳变性质；项目独立数值检查确认边界两侧存在非零矩阵差异。未采用其替代波形，未证明这种性质导致当前网络性能差距，也不把作者的命名追溯成Huang原文术语 |

2026-10-13 GNSS-Free、AFDM、off-grid场景来源补充，详见设定审查（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/scenario_assumptions_audit_20261013/REPORT.md`）。

| 原词或忠实译名 | 原文定位 | 本轮使用范围 |
|---|---|---|
| without GNSS capabilities；common delay；differential delay / 无GNSS能力、公共时延、差分时延 | [Shen作者稿](https://arxiv.org/html/2412.20806v1)，§II开头、§II-A式(1)，本地PDF p.3；§V Table I，p.12 | 支持终端不作个体差分时延/Doppler预补偿、卫星广播共同参考并在接收端处理残余量的场景。当前准确已知跨帧相位是额外条件，不由此文自动支持；2025正式发表，本地核对版为2024年末v1作者稿 |
| fractional Doppler shift；phase rotation / 分数Doppler、相位旋转 | Shen §II-B式(7)–(10)，PDF p.4；§III-C式(47)–(54)，p.9；§V off-grid说明，p.12 | 原文忽略分数时延，off-grid主要指分数Doppler；相位需要估计。当前增加连续时延，但将跨帧相位作为已知输入，须分别说明 |
| quasi-static property / 准静态性质 | Shen §II-B式(10)后讨论，PDF p.5 | 作为块内固定参数近似的文献依据；本项目11.7333 ms块长的圆轨道敏感性数字是另行计算，不是原文结果，也不是接收机性能验证 |
| full diversity / 全分集 | [Bemani等](https://arxiv.org/html/2204.12798v2)，§IV Theorem 1、式(51) | 原定理具有最大延迟/Doppler支持等适用条件，不能将其保证直接套用到本项目16点有用帧、335.52点最大完整时延。未满足充分条件不等同于已证明当前特定TDL模型不具备分集或无法估计 |

2026-10-13 单天线与多天线分解、两阶段估计的文献核查：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| channel direction vector / 信道方向向量 | [You等，Massive MIMO Transmission for LEO Satellite Communications](https://arxiv.org/pdf/2002.08148)，§II-B.3式(2)–(4)、§II-C式(8)–(10)，作者稿PDF pp.7–10 | 同一用户各路径采用共同阵列方向；时频标量响应乘方向向量。支持空间分解，不证明由单天线矩阵唯一恢复未知方向，也不是score估计论文 |
| two-stage channel estimation (TSCE) / 两阶段信道估计；per-subcarrier space domain processing / 逐子载波空间域处理；per-user frequency domain processing / 逐用户频域处理 | [Li–Gao–Xia，Channel Estimation for LEO Satellite Massive MIMO OFDM Communications](https://arxiv.org/html/2207.11958v2#S4.SS2)，TWC 2023，DOI 10.1109/TWC.2023.3252895；§II-B式(7)及角度已知说明；§IV-B式(31)–(35) | 已知方向下先空间处理、后低维信道估计的直接先例。采用OFDM和终端时延/Doppler预补偿，非GNSS-free AFDM JADCE；空间处理显式考虑用户间干扰，不能等同于任意查询上aᴴR/M；没有证明一次估计方向足够，也未使用本项目一阶/二阶/证据网络。原文阵列响应单位范数，与本项目物理响应范数平方M的约定需换算 |
| average signal-to-interference-plus-noise ratio (ASINR) / 平均信号与干扰加噪声功率之比 | [You等作者稿](https://arxiv.org/pdf/2002.08148)，§III-B式(26)、(29)–(30)，PDF pp.14–15 | 分子和分母分别取期望后相除，不是瞬时SINR的期望。原文输出wᵀy，移入bᴴy约定时b=w*；此式是统计CSI数据接收设计，不是方向获取或JADCE算法 |
| regularized zero-forcing (RZF) processing / 正则化迫零处理 | [Li等v2](https://arxiv.org/html/2207.11958v2#S4.SS3)，§IV-C Proposition 3式(38)–(41)，PDF p.9 | 空间权重依赖同导频用户方向与功率，正则项由共同PDP和噪声联合确定、通常不等于噪声方差。原文为导频子载波数趋于无穷的MSE设计；不能直接套给已作线性外信息更新的查询。原文与本项目推导分开记录于详细核查（历史路径，见迁移记录：`reference/spatial_combining_audit_20261013/REPORT.md`） |

2026-10-13 GNSS-independent 场景与方向先验的适用条件，详见可行性核查（历史路径，见迁移记录：`reference/gnss_direction_feasibility_20261013/REPORT.md`）。

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| GNSS independent operation；geographic location uncertainty / 不依赖GNSS的运行、地理位置不确定性 | [Caus–Shaat 2025作者稿v1](https://arxiv.org/html/2506.03852v1)，§I PDF p.1；§II及Fig.2，p.4 | 不依赖GNSS可以与粗略位置及不完美时频预补偿共存，不意味着位置或逐用户方向精确已知；原文不是本项目无个体预补偿的GFRA流程 |
| position-independent synchronization / 不依赖位置的同步 | [De Beelde等2026](https://www.nature.com/articles/s44459-026-00032-3)，PDF p.2 Methods开头及同页文献讨论 | 特指该文不依赖UE及卫星位置的连接态时频校正；与“终端没有GNSS接收机”区分，不移称未知活动用户的方向获取算法 |
| space angle pairs / 空间角度对 | [Li–Gao–Xia v2](https://arxiv.org/html/2207.11958v2#S2.SS2)，§II-B，PDF p.4；§II-C末，p.5 | 原文明确理想已知方向及慢变统计。不能据此推定GNSS-independent首次接入已获准确方向；本项目由方向反算几何时延/Doppler及固定错误方向下的最小重构误差，均为另行推导和确定性核查 |

2026-10-13 Cai score 学习对象与本项目完整信道网络的对照：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| channel power normalization / 信道功率归一化 | [Cai v2](https://arxiv.org/html/2506.00581v2#S5.SS2.SSS2)，§V-B2，式(59)–(65)及前导训练归一化定义 | 原文逐样本固定信道范数；本项目使用固定总体RMS，保留样本间功率变化。该差异改变所学先验，不能未经受控实验把性能差距归于归一化，也不能仅在推断时切换而保持原权重 |
| block-fading model；channel frequency response / 块衰落模型、信道频率响应 | [Cai v2](https://arxiv.org/html/2506.00581v2#S2.SS1)，§II-A，式(2)–(3) | 原文采用同步、块内准静态OFDM，单用户频率×天线矩阵。本项目完整score输入为天线×AFDM输出索引×输入索引，不把矩阵尺寸增大直接等同于独立自由度增加 |
| clustered delay line (CDL)；angle of arrival (AoA) / 簇时延线、到达角 | [Cai v2](https://arxiv.org/html/2506.00581v2#S6.SS1.SSS1)，§VI-A1及未编号信道展开式 | 原文CDL-C含24簇、每簇20条子路径，学习包含随机角度、时延及复增益的完整信道先验；并非给定真实方向后只学习路径增益。本项目H=aG采用用户内共同方向，不能笼统声称物理自由度比Cai更多 |


2026-10-13 GFRA中角域信道恢复与显式方向估计的区别：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| virtual angular domain；angular-frequency structured sparsity / 虚拟角域、角度—频率结构化稀疏性 | [Ke等作者稿v4](https://arxiv.org/html/1906.09867v4#S2.SS3)，§II-C式(7)–(10)，§II-A式(3) | 固定阵列变换不要求真实AoA已知；角域系数恢复可以利用方向信息而不输出连续角度；多路径角扩展不等于单一共同方向 |
| delay-Doppler-angle domain；Markov random field / 时延—多普勒—角域、马尔可夫随机场 | [Shen作者稿v1](https://arxiv.org/html/2412.20806v1)，§II-B式(11)–(12)、§III-A式(17)–(18)，本地PDF pp.5–6 | 空间二维DFT后联合恢复角域信道及稀疏支撑；角域泄漏包含未知方向信息，不等同于事先知道方向，也不等同于独立连续AoA估计 |

2026-10-13 天线维度与 score 网络结构调研，详见综合报告（历史路径，见迁移记录：`reference/antenna_score_architecture_20261013/REPORT.md`）：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| angular/beamspace domain；unitary Fourier transformation / 角域或波束域、酉傅里叶变换 | [Fesl等，WCL 2024作者稿v1](https://arxiv.org/html/2403.03545v1)，§III-A，Algorithms 1–2，PDF pp.2–3；§III-C/Fig.1，p.3 | 原文变换Rx×Tx两阵列轴；本项目空间变换沿UPA的y、z两轴。完整酉变换保留白噪声方差，不保证性能提升；论文轻量模型整体比较不是FFT单因素消融 |
| beam-delay domain；three-dimensional convolution / 波束—时延域、三维卷积 | [Artemasov等，ITU Journal 2024](https://www.itu.int/dms_pub/itu-s/opb/jnl/S-JNL-VOL5.ISSUE1-2024-A05-PDF-E.pdf)，§2.2式(8)–(9)，pp.63–64；§4.1式(23)–(24)，p.66 | 原文沿平面阵列两beam轴与delay卷积。我们的UPA两轴加AFDM矩阵两轴共四个物理轴，不能把普通Conv3d直接称为完全同构；交替处理两组二维轴是本项目待验证设计 |
| fully convolutional deep learning receiver / 全卷积深度学习接收机 | [Honkala等，DeepRx，TWC 2021](https://arxiv.org/html/2005.01494#S3)，§III/Fig.2、Table II | 原文天线信息放入特征通道、卷积沿时频，说明这种组织不是必然失效；其两Rx、LLR输出和数据辅助输入不能作为本项目score去噪的公平架构对照 |
| circular convolution / 圆周卷积 | [Fesl等，SPAWC 2021](https://arxiv.org/html/2104.12667)，§III–IV式(14)–(19) | 原文从块循环和移位假设得到DFT域二维圆周卷积；引用作结构设计依据，不声称其ULA统计假设已在本项目UPA/AFDM成立 |

上述阵列轴处理于2026-10-13曾进入[完整网络配对实验](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/CURRENT_STAGE.md)：保留原RefineNet，并增加交替处理UPA和AFDM两组轴的分支，采用同参数量的AFDM轴对照。该组合及其零输出初始化为本项目实现选择，不冠以新方法名称，也不宣称复现Artemasov或Fesl的原网络。角域变换不在此首轮对照中同时引入。


2026-10-13 完整角域原生实现与功率处理补充：

沿用上述 Fesl §III-A/C 的角域表示、Artemasov §4.1 的平面阵列组织及 Cai §IV 的 denoising score matching（去噪分数匹配）。四物理轴上交替两组二维卷积为项目设计，不命名为文献已有网络。该方案已按用户要求删除，历史说明见[精简记录](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/CURRENT_STAGE.md)。

Cai §V-B2 式(59)–(65)的 channel power normalization（信道功率归一化）在本项目评估中须区分真值范数与查询能量估计：式(59)右侧对白噪声取条件期望后等于左侧，有限随机查询上不是严格恒等式。功率估计方差、负值概率及缩放不确定性说明是项目推导，见功率评估（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/full_power_channels_20261013/PLAN.md`）。样本总功率不自动等同于慢变大尺度衰落，不能把解析缩放称为独立学习网络。


2026-10-13 用户授权执行逐样本功率归一化训练：沿用 Cai §V-B2 的 channel power normalization（信道功率归一化）定义，U=H/sqrt(mean(|H|²))。训练噪声相对于U独立采样；推断中的解析查询功率估计、固定正下限和模型支持限制明确记录于执行方案（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/full_power_channels_20261013/PLAN.md`）。扩大噪声范围、0.5dB继续训练门槛及其统计检查均为本项目选择，不归为Cai原文规定。


2026-10-13 数据张量阶数与卷积轴的核对：Fesl WCL 2024作者稿§II-A式(1)、§III-C/Fig.1以接收×发射二维复信道为输入，实虚作为两通道，采用2D卷积。Artemasov 2024 §4.1式(23)–(24)、Fig.3、p.66明确写四阶复张量 Nu×NR×NC×Nτ，其中Nu为UE天线数；卷积核为3×3×3，沿两beam轴与delay处理。不能将Nu误称批次/实虚维，也不能把“四阶输入”当成四轴卷积的证据。本项目4×4×16×16两beam轴加AFDM输入/输出索引，并交替两组2D卷积，是独立设计扩展，两文未直接验证该组合。

2026-10-13 二维角域展平的专项核查（历史路径，见迁移记录：`reference/afdm_network_axes_20261013/REPORT.md`）：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| beamspace channel vector / 波束域信道向量；Gaussian mixture LAMP (GM-LAMP) | [Wei–Hu–Dai，TCOM 2021正式全文](https://oa.ee.tsinghua.edu.cn/dailinglong/publications/paper/Deep%20learning%20for%20beamspace%20channel%20estimation%20in%20millimeter-wave%20massive%20MIMO%20systems.pdf)，§II-A式(3)、(6)–(8)，pp.183–184；§III，pp.186–188；§IV Fig.5、7，pp.190–191 | UPA二维导向基与完整N×1角域向量可以并存，后续采用学习线性映射和逐元素收缩；不是普通Conv1D，也未比较本项目4×4 beam卷积与通道组织方式 |
| convolutional input channels / 卷积输入通道 | [DeepRx作者稿](https://arxiv.org/html/2005.01494#S3)，§III、Fig.2、Table I | 天线及实虚部可放通道，通过通道混合联合使用；仅有逐通道卷积不等于全通道混合。本文是OFDM两Rx接收机，不能把其BER结果当成本项目score性能依据 |
| conditional mean estimation；conditional covariance / 条件均值估计、条件协方差 | [Dytso–Poor–Shamai，TIT 2023](https://doi.org/10.1109/TIT.2022.3216012)，式(3)、§III Proposition 1式(17) | 用实坐标Gaussian恒等式核对score/Jacobian变换；展平的置换只重排二阶对角，真正酉混合只保证全trace不变，不能从角域对角恢复天线域全部逐坐标方差 |

“将16个复波束作为32个实输入通道”“二维FFT后展平”“交替两组二维卷积”均为操作描述，不设立新方法名称。本轮128个样本的reshape恒等式与MAC检查属于项目验证，不归为参考论文结果。

2026-10-13 波束通道网络落实：沿用Fesl §III-A的angular/beamspace domain与DeepRx §III的convolutional input channels。`ChannelScoreNetwork`为项目类名，不是论文方法名。当前方案（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/full_power_channels_20261013/PLAN.md`）采用全部32实通道混合及AFDM平面残差卷积。输入/输出稠密线性层吸收固定DFT的关系是项目线性代数推导，已用非零输出网络验证；它说明函数类等价，不声称Adam训练轨迹等价。数据中的`C_ml=mean(U_m conj(U_l))`明确称空间二阶矩，未中心化，不把非对角能量减少解释为独立性或物理自由度减少。5000训练样本的数值来自本地诊断（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/full_power_channels_20261013/REPRESENTATION.json`），并非论文实验结果。

2026-10-14 强噪声 score 改进定向调研（历史路径，见迁移记录：`reference/low_snr_score_20261014/REPORT.md`）：EDM、Min-SNR、条件均值及后验矩沿用上表已核对条目，补充以下原词。

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Single-Step SNR-informed Denoiser / 单步 SNR 条件去噪器 | [Strasser–Bäro–Utschick，2025作者稿v1](https://arxiv.org/html/2509.07839v1)，§IV-B、式(10)–(12)、Algorithm 3；§V-F/G；arXiv元数据注明在WSA 2025报告 | 完整酉导频、单载波MIMO的单步去噪先例；文中单步性能不逊于或优于多步的实验不能直接成为AFDM JADCE结论。说明单步本身不是强噪声失败的充分解释 |
| effective noise；colored Gaussian noise；D-VDAMP / 有效噪声；有色Gaussian噪声；去噪型VDAMP | [Metzler–Wetzstein，2020作者稿](https://arxiv.org/html/2010.13211)，§1–2、Algorithm 1 | 为结构化测量下实际查询与AWGN的差异提供方法依据；MRI中的Fourier/wavelet条件不能直接套给AFDM。项目观测到的输入列误差二阶矩含偏差，不能直接称为纯噪声协方差，也未实现D-VDAMP |

2026-10-14 参数化对照执行：EDM 沿用 Karras 等 NeurIPS 2022 §5 式(7)–(8) 的 preconditioning，见上述已有条目。项目仅使用 c_in、c_skip、c_out，保留旧 DSM 权重；实坐标 nu=v/2，tau²取训练先验的实坐标二阶矩。固定 v 专门训练是实验条件描述，不冠以新方法名称。计划见 配对训练（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/low_snr_parameterization_20261014/PLAN.md`）。

2026-10-14 用户功率一致性核查：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Uplink power control / 上行功率控制 | 3GPP TR 38.821 V16.0.0 §6.2.2，印刷页62（PDF索引61），https://atisorg.s3.amazonaws.com/archive/3gpp-documents/Rel16/ATIS.3GPP.38.821.V1600.pdf | 该研究报告讨论NTN上行功控，并认为可使用Rel-15方案；不证明所有终端严格等接收功率，更不证明无GNSS场景能精确补偿 |
| downlink pathloss estimate / 下行路径损耗估计 | ETSI TS 138 213 V16.11.0，§7.1.1，pp.17–21，p.21给出referenceSignalPower减filtered RSRP；§7.4，pp.32–33给出PRACH功率控制，https://www.etsi.org/deliver/etsi_ts/138200_138299/138213/16.11.00_60/ts_138213v161100p.pdf | 参考信号测量是慢变功率补偿的信息来源，不要求读取真实瞬时信道范数；无GNSS与无下行测量是不同约束。本项目目前只有LARGE_SCALE_COMPENSATED=True假设，没有实现标准功控过程 |

“等发射功率”“补偿后平均功率一致”“逐实现信道范数相等”用于区分不同数学条件，不作新算法名称。当前生成器使用相同导频能量、共同TDL路径期望功率，并保留独立小尺度衰落，省略用户相关的大尺度幅度因子；配置中的大尺度补偿假设不等于实现了逐用户功率补偿。对小尺度衰落取期望的信道能量一致，与固定场景接收能量一致是不同条件，推导及口径见 references/power_control_scope_20261014/NOTE.md。几何损耗量级检查见 references/power_control_scope_20261014/GEOMETRY_CHECK.json，仅计算距离引起的自由空间损耗差，不含天线方向图、遮挡和功控误差。

2026-10-14 卫星 GFRA 场景对照：六篇 GFRA 与一篇相邻 AFDM CE 的来源、仿真条件及差异见 文献与代码综合核查（历史路径，见迁移记录：`reference/satellite_gfra_audit_20261014/SYNTHESIS.md`）。

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| discrete prolate spheroidal basis expansion model (DPS-BEM) / 离散长椭球基展开模型 | [Mao等，ICC 2025作者稿](https://arxiv.org/html/2504.04686v2)，§II-B式(6)–(9)，PDF pp.2–3 | 原文用全局最大Doppler构造基并估计未知系数；不同于把每用户准确跨帧相位作为输入。不声称本项目已实现此模型 |
| generalized complex exponential basis expansion model (GCE-BEM) / 广义复指数基展开模型 | [Shen等，JSAC 2025作者稿](https://arxiv.org/html/2408.02586v1)，§II-A式(3)–(4)，PDF p.3 | 用于对照未知时变信道参数化；多星联合数据检测结果不直接支持当前单星JADCE的性能主张 |
| phase rotation caused by fractional Doppler / 分数Doppler引起的相位旋转 | [Shen等，大差分时延作者稿](https://arxiv.org/html/2412.20806v1)，§II-B、§III-C；§V，PDF p.12 | 原文off-grid接收机更新相位；当前准确已知有效跨帧相位是条件实验，既不等于移除了帧内Doppler，也不能代表实现了未知相位估计 |
| large-scale fading compensation / 大尺度衰落补偿 | [Zuo等，TWC 2023作者稿](https://arxiv.org/pdf/2210.17355)，§V，PDF p.25；Shen大差分时延作者稿§V，PDF p.12 | 文献明确使用的幅度建模假设；与时延／频偏预补偿分开，不能据此宣称当前已执行功率控制 |

本次“投影到真实首径”的表达是结构诊断操作，不是新算法名称：固定真实原子B，取c=〈B,H〉_F/||B||_F²，报告||H−cB||_F²/||H||_F²。真值只用于诊断；结果不作为可实现接收机NMSE，详见上述核查目录的structure_diagnostic.json。

2026-10-15 未知跨帧相位模型原型：沿用上述相位旋转术语与 Shen §III-C 式(47)–(54)的相位学习背景，
在 `docs/history/experiments/unknown_phase_20261015/model.py` 中仅公开原始导频，
由同一候选 Doppler 构造帧内 AFDM 原子与 exp(j2πνqT_frame) 跨帧因子，并给出一、二阶导数。
这些公式直接来自本项目物理模型；未实现 Shen 的 OTFS 接收机或完成联合相位估计器。
`docs/history/experiments/phase_feasibility_20261015/diagnose.py` 的矩阵变换是自由完整信道模型的代数诊断，
不证明带物理 AFDM 结构或学习先验的模型不可辨识；真值只用于此诊断与模型验证。

2026-10-15 未知相位五基线重跑：`docs/history/experiments/unknown_phase_20261015/estimate_phase.py`
使用 separable nonlinear least squares / 可分离非线性最小二乘与 variable projection / 变量投影的含义，
依据 [O'Leary–Rust 作者全文](https://www.cs.umd.edu/users/oleary/software/varpro.pdf)，
§1 式(2)–(3)、§2 式(5)–(7)，PDF pp.2、4–5。
每个候选用户以一个主导 AFDM 路径近似相位拟合，解析消去复天线增益；
先用帧相位的离散 Fourier 相关筛选，再枚举物理 Doppler 别名并在连续时延、Doppler 上细化，
执行两轮逐用户更新及联合最小二乘增益更新。该步骤不使用真实活动、时延、Doppler、方向或相位。
五个冻结基线接收同一观测导出的相位估计，网络和已知相位条件下标定的活动阈值保持不变；
应称为“估计相位后运行原基线”的项目适配，不称为 Shen EM、MNOMP 或五篇原论文的未知相位逐项复现。
正式十场景参数和结果记录于 `docs/history/results/unknown_phase_baselines_20261015/evaluation/`；
相位拟合的单路径近似不改变最终基线各自的信道参数化。

2026-10-15 Proposed 未知相位适配：上述物理相位与变量投影计算整理至
`algorithm/unknown_phase_model.py` 和 `algorithm/phase_estimation.py`，
由 `algorithm/proposed/unknown_phase.py` 先估计跨帧相位，再调用原 Proposed 条件接收机。
术语、原文定位与前端数学操作沿用上段依据；这一两阶段适配以完整信道 NMSE 和 AER 为主要指标。
配置、公开输入和验证范围见 [PROPOSED_UNKNOWN_PHASE.md](https://github.com/RESET-cpu/afdm-gfra/blob/416a4dd4bd219dd9fb5049294bc02f4854f472f4/paper/STMP/docs/PROPOSED_UNKNOWN_PHASE.md)。

2026-10-15 Shen 相位学习适配核查：

| 原词或忠实译名 | 原文定位 | 本项目使用范围 |
|---|---|---|
| expectation-maximization (EM)；phase rotation / 期望最大化；相位旋转 | [Shen v1](https://arxiv.org/html/2412.20806v1#S3.SS3)，§III-C，式(47)–(52)，PDF p.9；Algorithm 1，p.10；正式发表 DOI 10.1109/TWC.2025.3525738 | 借鉴后验均值、方差驱动相位更新并重建测量矩阵的思路。现有 Proposed 使用学习近似后验，不自动继承精确 EM 的单调性结论。 |
| projected onto the unit circle / 投影到单位圆 | 同文式(53)–(54)及相邻说明，PDF p.9 | 原文先解无约束线性方程再逐元素归一化，属于近似更新。本文保留 exp(jq beta_k) 跨帧关系的目标和梯度另行推导；未把它命名为 Shen 原算法，未宣称投影是一般单位模问题的精确解。 |

对应推导、方差项适用条件和合成数值检查见 [Proposed 未知相位说明](https://github.com/RESET-cpu/afdm-gfra/blob/416a4dd4bd219dd9fb5049294bc02f4854f472f4/paper/STMP/docs/PROPOSED_UNKNOWN_PHASE.md#shen-2025-相位学习的适配核查2026-10-15)。后续已实现保留 exp(jq beta_k) 约束的相位更新，入口为 `configs/proposed_iterative_phase.json`，同十场景 NMSE/AER 比较见 实现验证（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/shen_phase_update_20261015/evaluation/REPORT.md`）。这是借鉴原文目标的 AFDM 适配，并非 Shen OTFS 算法复现；当前六方法比较仍采用原两阶段相位配置。

2026-10-15 GAMP-SBL / off-grid SBL 后验相位更新：继续采用上述 Shen §III-C 式(47)–(54)的“phase rotation”和“expectation-maximization”含义作为参考。项目实际操作称为“后验相位更新”，完整目标、Gaussian 协方差项及 exp(jq beta_k) 约束见 [BASELINE_PHASE.md](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/BASELINE_PHASE.md)。GAMP 的对角方差项在单位模约束下为常数；SBL 的跨用户协方差项保留。这里的逐用户一维搜索、圆周插值和一次更新预算是项目明确写出的操作，并非新算法名称或 Shen 原文的闭式解。不得由固定后验目标下降推出整体精确 EM 收敛。

2026-10-14 连续信道与Huang设定专项核对：

| 原词或忠实译名 | 原文定位 | 当前使用 |
|---|---|---|
| continuous-time waveform、frequency wrapping、complex-envelope discontinuity / 连续时间波形、频率折叠、复包络不连续 | [Bemani博士论文](https://www.eurecom.eu/publication/7447/download/comsys-publi-7447.pdf)，§3.1.1式(3.2)–(3.10)、§3.2式(3.14)，印刷pp23–29；[Cao–Shao预印本](https://arxiv.org/html/2609.07480v1)，§II-A式(1)–(3)、Proposition1 | 用于核对当前分数时延及多周期CPP的模拟解释；整数样点等价不能推出带限DAC输出等价。项目相位导数与跳变诊断见信道专项（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/implementation_audit_20261014/CHANNEL_MODEL_REVIEW.md`），未采用预印本的新波形替换当前生成器。 |

2026-10-14 线性查询误差处理核查：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| de-correlated linear estimator、divergence-free estimator / 去相关线性估计器、无散度估计器 | [Ma–Ping，Orthogonal AMP v3](https://arxiv.org/html/1602.06509v3#S3)，§III-A Definition 1后式(14)、§III-B Definition 2及式(17)–(18)、§III-E | 当前线性更新已满足迹归一化，但这一事实不推出有限AFDM查询是独立AWGN；需配套非线性估计条件，并核查误差分布。详见本轮报告（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_speed_20261014/WHITENING_ASSESSMENT.md`） |
| right-rotationally invariant random matrix、non-separable denoiser / 右旋转不变随机矩阵、非可分去噪器 | [Fletcher–Pandit–Rangan–Sarkar–Schniter，JSTAT 2019正式作者全文](https://phil-schniter.web.app/pdf/jstat19.pdf)，§3–4、Theorem 1；前身发表于NeurIPS 2018 | 高维VAMP分析的假设；不能仅凭基础DFT导频行正交，就认为重复块AFDM测量算子符合该随机矩阵模型 |

“按误差二阶矩补加Gaussian扰动”是上述报告中的直接协方差加法构造，不是既有算法名称。真实空间误差只用于明确标注的oracle诊断；不能把样本二阶矩等于标量阵写成已获得与信道独立的Gaussian噪声。

2026-10-14 空间协方差接收机候选：covariance shrinkage（协方差收缩）采用 [Chen–Wiesel–Eldar–Hero，作者稿](https://arxiv.org/pdf/0907.4698) §II式(3)–(4)、PDF p.4的标量单位阵混合形式。本项目先从接收二阶矩中减去公开热噪声，再投影正半定并固定混合10%；不是原文OAS/RBLW，也不主张其最优性。逐用户矩阵Gaussian更新、块平均及额外扰动按实现公式（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_spatial_feedback_20261014/ALGORITHM.md`）直接描述，不另造方法名。

2026-10-14 L-DAMP 原稿与作者训练代码复核，详见对照报告（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/ldamp_paper_audit_20261014/REPORT.md`）：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| denoiser-by-denoiser training / 分别训练各去噪器 | Metzler 等作者稿 v4（历史路径，见迁移记录：`reference/ldamp_review_20261014/metzler2017_learned_damp.pdf`），§3，PDF p.5；§4.2，p.7 | 按噪声区间训练 AWGN 去噪器，再在推断时选择网络，是原文训练选项。最优性论述依赖该文条件；不自动适用于本项目多用户、重复观测算子和相关误差 |
| state evolution / 状态演化 | 同上，§4.1，Finding 1，PDF pp.6–7 | 该文列出独立随机矩阵、Gaussian 测量噪声及 Lipschitz 去噪器等条件。本项目矩阵重排为 I⊗A，不能仅由 AMP 形式相同宣称满足这些条件 |
| covariance matrix / 协方差矩阵 | [Chen–Sohrabi–Yu，ICASSP 2018](https://www.comm.utoronto.ca/~weiyu/2018_ICASSP_massive_connectivity.pdf)，§3.1，PDF p.2，式(2)–(4)及式(6)前的简化条件 | 该文保留多测量向量误差协方差，并在特定先验下简化为标量。本项目诊断是对中心化误差计算经验协方差及其非对角能量占比；后者为明示公式的统计量，不设立新方法名，不据此声称已推导出当前 CNN 的矩阵校正 |
| residual learning / 残差学习 | Zhang 等 DnCNN 作者稿 v1（历史路径，见迁移记录：`reference/ldamp_review_20261014/zhang2017_dncnn.pdf`），§III-B，式(1)，PDF p.3；§IV-A，PDF p.6 | D(q)=q−F(q) 下清洁输出 MSE 与噪声预测 MSE 代数等价。He 信道版的 Adam、噪声分段和初始化另按其代码记录，不混同 DnCNN 原文的 SGD 配方 |

2026-10-14 各轮一致的接收机规则调研，详见综合报告与候选公式（历史路径，见迁移记录：`reference/uniform_receiver_literature_20261014/REPORT.md`）：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Fast Iterative REnoising (FIRE)、colored renoising / 快速迭代再加噪、有色再加噪 | [Bendel–Shastri–Ahmad–Schniter，TMLR 2025，v4](https://arxiv.org/html/2501.17468v4#S3.SS1)，§3.1，式(7)、(10)–(16)、Algorithm 1、Theorem 1 | 作为各轮统一调用 AWGN 去噪器、线性估计和协方差补加扰动的设计依据。复高斯 MMV、活动分类、可实现初值及任务输出是项目扩展；不宣称符合原文定理或已实现 AFDM 加速 |
| Denoising Generalized Expectation-Consistent approximation (D-GEC)、corr+corr | [Shastri等，JSAIT 2022正式全文](https://phil-schniter.web.app/pdf/jsait22_dgec.pdf)，§III-A/B，Algorithms 2–3、式(31)–(41)，pp.534–536 | 分组精度与有色噪声训练的先例。corr+corr 不能直接解释为对旧 AWGN 网络无训练包装；式(36)为经验支持，作者没有给出一般严格证明。p.535存在一次性加噪初始化先例 |
| sensitivity、divergence / 灵敏度、散度 | [Rangan–Schniter–Fletcher，TIT 2019正式全文](https://phil-schniter.web.app/pdf/tit19_vamp.pdf)，Algorithm 3，§IV-E式(54)–(55)、§V Theorem 2 | 灵敏度用完整去噪映射的归一化 Jacobian 迹定义。项目联合映射 pF 的链式求导须含分类器；一般有限网络下不能把条件 MSE、灵敏度与真实输入噪声标签等同 |
| long-memory message passing、damping / 长记忆消息传递、阻尼 | [Takeuchi，TIT 2022作者稿v2](https://arxiv.org/abs/2111.05522v2)，§III-C/D，式(27)–(28)、(44)–(45)，pp.6–7；§IV-B式(63)–(78)，pp.9–10 | 支持混合估计时跟踪跨轮协方差；与天线空间协方差不同。相关收敛证明依赖大系统随机矩阵及非线性条件，不直接覆盖当前固定 AFDM 算子 |
| sufficient-statistic memory AMP / 充分统计量记忆 AMP | [Liu等，SS-MAMP预印本v4](https://arxiv.org/abs/2112.15327v4)，Theorem 1，式(62)，pp.10–11；§VIII-C，p.16 | 协方差决定历史融合权重的先例；需要已正交化的 MAMP 及有效历史协方差，不能直接附加到任意学习回路。扩展版期刊发表未核实，保留预印本标记及有限系统不稳定边界 |

报告中的复高斯扰动采样式、模型协方差与真实协方差之差、联合活动去噪链式求导均按公式直接描述，不设立新缩写。它们属于本项目代数推导，未以新接收机实验验证；未改变当前主线。

2026-10-14 去噪输入误差与物理接收噪声的区分：

| 术语 | 原文定位 | 本项目含义与限制 |
|---|---|---|
| effective noise / 有效噪声；equivalent noise / 等效噪声 | Metzler 等作者稿（历史路径，见迁移记录：`reference/ldamp_review_20261014/metzler2017_learned_damp.pdf`），§2.1，PDF p.4，式(3)后 νᵗ 的定义；He 等作者稿（历史路径，见迁移记录：`reference/ldamp_review_20261014/he2018_ldamp.pdf`），§III-A，PDF p.2，式(6) | 指去噪输入减去真实目标的误差，包含残余干扰；不等于观测中的物理接收噪声 W。不同波束有效误差方差的训练适配不改变 W∼CN(0,σ²I)。独立 Gaussian 训练扰动仅是对有效误差的近似。 |

2026-10-14 L-DAMP 完整实现开发补充：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Wirtinger derivatives；Jacobian matrices / Wirtinger 导数；Jacobian 矩阵 | Kunde–Mirri–Chamberland–Paolini，2026预印本 v1（历史路径，见迁移记录：`reference/ldamp_review_20261014/kunde2026_complex_amp.pdf`），§III-C，PDF p.12，式(18)–(21) | 为复数非可分去噪的矩阵校正提供参考；项目用显式输入/输出下标定义部分迹并通过独立坐标差分核验，不沿用可能含歧义的转置简写。原文独立圆对称复 Gaussian 测量矩阵条件不覆盖当前 AFDM 导频；未声称理论收敛保证。 |

“双边逆 DAFT、按循环滞后重排、沿时间做 DFT”及“逐波束共享两通道 DnCNN”是代码操作描述。DAFT 定义沿用 Huang §II、PDF p.2 式(1)前与式(4)后；固定角域 DFT 沿用上述 Fesl §III-A、Wei–Hu–Dai §II-A。所有系数保留，不把变换系数命名为真实连续路径参数。MatConvNet 保存的 BN moments 为均值和含 epsilon 的标准差，按[官方接口定义](https://www.vlfeat.org/matconvnet/mfiles/vl_nnbnorm/)载入；训练库重估运行统计是明示适配，不能说成原作者训练轨迹复现。见开发报告（历史路径，见迁移记录：`result/ldamp_implementation_20261014/REFERENCE_REPORT.md`）。

2026-10-14 各轮一致推断规则的配对实现与试验：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| damped denoising VAMP (DD-VAMP)；damping / 带阻尼的去噪型 VAMP；阻尼 | [Sarkar–Ahmad–Schniter，ICASSP 2021 作者稿 v1](https://arxiv.org/abs/2010.11321)，§3.1、Algorithm 1 第10、15–16行，PDF p.3；本地原文（历史路径，见迁移记录：`reference/uniform_receiver_literature_20261014/phase2_vamp/ddvamp.txt`） | 灵敏度在平方根域阻尼，精度在逆平方根域阻尼。本项目取固定权重、完整联合映射 pF 的复探针差分、沿用原主线的灵敏度截断范围；这是 AFDM 接收机适配，不能宣称复现论文 MRI 性能或满足其随机矩阵条件。权重为新值权重，越大意味着阻尼越弱。 |
| plug-and-play ADMM (PnP-ADMM) / 即插即用 ADMM | 同上，§2.1 式(3a)–(3c)、§2.2，PDF p.2 | 保留高斯数据项更新及对偶递推，以旧联合去噪器代替近端映射。本项目将固定查询方差与线性正则化参数对应，并只试两个由公开热噪声和导频能量决定的参数；不声称已穷尽 PnP 参数或存在凸目标、收敛保证。 |

实现和选择记录见 配对试验协议（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_uniform_inference_20261014/PROTOCOL.md`） 与 冻结的新场景设置（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_uniform_inference_20261014/SELECTION.json`）。FIRE 的二阶网络方差替代、固定计算预算和活动读出均为项目实验选择；算法名称之后明确写出这些改动，不作为文献原算法的完整复现。

2026-10-14 旧网络计算与局部导数的优化判断，见诊断报告（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_optimization_20261014/REPORT.md`）：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Jacobian of the conditional expectation；conditional variance / 条件期望的Jacobian；条件方差 | [Dytso–Poor–Shamai作者稿](https://arxiv.org/pdf/2104.01883)，§IV Proposition 1式(22)、Corollary 1式(23)，PDF pp.5–6 | 在实噪声协方差为(v/2)I时，精确后验均值满足J=2C/v。项目比较的是3个探针、3个步长下的归一化迹估计；平均为正不等于完整Jacobian正半定。pF的两项导数按乘积公式直接分解，不设立新算法名称。 |
| second-order score matching / 二阶得分匹配 | [Cai v2](https://arxiv.org/html/2506.00581v2#S4.SS3)，§IV-C式(51)–(54) | 有限冻结一阶网络下，当前迹损失的最优读出对应以该均值为中心的条件误差风险。风险与真实协方差及实际Jacobian的区别按项目THEORY.md附录A代数解释，不将其等同。复用一阶特征输出标量风险是尚未训练的项目建议。 |
| gradient step denoiser；proximal gradient step denoiser / 梯度步去噪器；近端梯度步去噪器 | [Hurault–Leclaire–Papadakis，ICML 2022](https://proceedings.mlr.press/v162/hurault22a/hurault22a.pdf)，§3式(4)–(5)、Proposition 3.1，PDF p.3 | 标量势函数梯度给出对称Jacobian，命题的收缩条件进一步保证正定。这里只作为改变训练结构的文献先例，未实现该架构，也不将其PnP收敛结论移用于AFDM消息传递。随机方向负响应惩罚属于明示公式的项目建议，不能称为上述理论保证。 |

2026-10-14 旧网络的近似 AWGN 查询与一般去噪器反馈调研，见详细分析（历史路径，见迁移记录：`reference/awgn_linear_design_20261014/REPORT.md`）和来源定位（历史路径，见迁移记录：`reference/awgn_linear_design_20261014/SOURCE_NOTES.md`）：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| denoising-based OAMP (D-OAMP)；divergence-free denoiser / 基于去噪的 OAMP；无散度去噪器 | [Xue–Ma–Yuan，2016 作者稿 v1](https://arxiv.org/html/1610.05991v1)，Algorithm 2，PDF p.2；§3.3.1 式(7)–(8)，p.3 | 一般联合去噪器的散度扣除有来源；本项目复数 MMV 适配、旧网络活动读出和独立误差功率估计尚未完成接收机验证。经验散度和增益的数据依赖意味着有限维无散度性质只是近似，不保证当前 AFDM 误差为 AWGN。 |
| Stein’s unbiased risk estimate (SURE) / Stein 无偏风险估计 | 同上 §3.3.2 式(10)–(11)，PDF p.3 | 基于风险的增益选择；按本项目复数功率 v 和 2d 维实坐标重新推导归一化，式(14)中的功率为 ‖D−R‖²/d+2vα−v。无偏性需要正确 Gaussian 查询及相应正则条件，数据驱动调参还存在有限样本误差，不能用它自证输入已是 AWGN。 |
| state evolution；covariance matrix / 状态演化；协方差矩阵 | [Liu–Yu Part I 作者稿 v2](https://arxiv.org/html/1706.06438v2)，§III-B 式(14)–(17)，PDF pp.4–5；§III-D Theorem 1，p.6；[Kunde 等2026预印本](https://arxiv.org/html/2604.21115v1)，§III-C 式(18)–(21)、Remark 14，PDF p.12 | MMV 可以具有矩阵状态；重复 A 不自动排除 MMV 理论，但基础矩阵、信号各向同性和去噪器条件必须核对。本项目 256 个共同观测特征不能未经推导就简化成单个误差方差。 |
| algebraic estimator；polynomial estimator of divergence / 散度的代数估计器；多项式估计器 | [Skuratovs–Davies，TIT 2023 机构接收稿](https://www.pure.ed.ac.uk/ws/portalfiles/portal/361481237/Divergence_Estimation_in_MP_algorithms_reviewed_second_time_Final.pdf)，含封面 PDF p.4 Assumptions 1–3，p.6 Theorem 2 式(37)，p.8 Theorem 3，p.9 §III-E | 可减少额外网络调用的后续候选；其正交性、大系统和历史条件尚未在本项目成立，未替换当前导数估计，也不将经验选根规则改称严格保证。 |

本轮用户方形导频块的逆矩阵噪声倍率、每用户酉导频的自身响应与干扰协方差、负散度下的一般风险关系均为报告中明示的项目代数推导，不另造算法名称；未变更主线算法或权重。

2026-10-15：上述D-OAMP项目适配现已完成四条件开发试验；三类导频下均在第二轮超出网络支持范围，不能作为已成立的AFDM状态演化。每轮空间协方差、迹归一化及Gaussian扰动补齐按明确公式实施，统计改善但完整性能不通过，详见顺序实施报告（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_awgn_20261014/REPORT.md`）。该组合只描述具体操作，不赋予新的文献算法名称。

后续有色噪声条件训练设计沿用D-GEC §III-B、式(41)，印刷pp.535–536的corr+corr含义：有色噪声观测与同统计独立噪声样本同时输入；有限噪声样本不等于提供精确协方差。固定协方差C下，实坐标后验均值与Jacobian关系沿用Dytso–Poor–Shamai Proposition 1式(22)，并显式规定Jacobian第(i,j)项为∂D_i/∂r_j。矩阵加权条件去噪损失、隐式Gaussian误差生成器是NEXT_DESIGN.md（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_awgn_20261014/NEXT_DESIGN.md`）中的项目推导，尚未实施，不冠以既有方法名称。

2026-10-15 L-DAMP 联合去噪开发：noise level map（噪声水平图）沿用 Zhang–Zuo–Zhang FFDNet §III-A/B/E（https://arxiv.org/html/1710.04026v2#S3.SS2）。这里为每波束公开有效误差方差构造16个常量输入通道，并不复现 FFDNet 的子图下采样结构。network preconditioning 沿用上述 Karras §5 式(7)–(8)、Table 1 的名称；逐波束复数二阶矩到实坐标的尺度推广、32通道 DnCNN 和联合矩阵递推是项目适配，具体公式及受控比较见 `docs/history/results/ldamp_complete_20261015/PLAN.json`。所有候选仍属开发，不代表已安装或已获得独立接收机性能。

同日的后续对照保留上述 DnCNN residual learning 的名称：在冻结逐波束网络的输出上学习联合残差，属于项目自行定义的复合函数，不称作 He 原网络。残差分别按训练二阶矩或公开噪声标准差缩放，损失分母分别在 `PLAN.json` 中明写，未另造方法名称。整个函数参与 Wirtinger 部分迹；分开计算两支路后求和是 Jacobian 线性关系，不能省去“原网络输出作为新网络输入”这条链式导数。实际误差与同算子 Gaussian 对照、训练及数值证据见 `docs/history/results/ldamp_complete_20261015/REVIEW.md`。

2026-10-15 校正项数值检查：沿用 He §III-A 式(7)–(8) 的 Monte Carlo 导数估计及 Kunde §III-C 式(18)–(21) 的矩阵 Jacobian 约定。直接估计 `ZB`、在每用户 `N` 行上使用完整正交方向的安排属于项目推导，未包装为已有论文算法名称；公式、独立数值核验与适用条件见 PROJECTED_TRACE_DERIVATION（历史路径，见迁移记录：`src/history/experiments/ldamp_complete_20261015/PROJECTED_TRACE_DERIVATION.md`）。完整 `N` 个方向仅消除此处部分迹的抽样误差，不等于消除网络近似误差或证明 AFDM 状态演化。

2026-10-15 Proposed 协方差条件活动推断与矩阵反馈开发：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Gram–Schmidt orthogonalization (GSO)；orthogonal estimator / Gram–Schmidt 正交化；正交估计器 | [Cheng、Liu、Liang、Manton、Ping，OAMP-MMV 作者稿v1](https://arxiv.org/html/2304.08038v1#S3.SS6)，§III-F Definition 20、式(31)–(34)；§III-G Theorem 21 | 矩阵交叉协方差消除输入输出误差相关。项目仅聚合32维实空间特征，不等于消除全部用户、输入坐标或跨轮相关。§III-D Assumption 18 的 Haar 及 PIID-separable 条件未经本项目验证；§I-D也说明该文状态演化论述偏直观，不能援引为当前固定AFDM算子的严格保证。 |
| generalized SURE / 广义 Stein 无偏风险估计 | [Eldar，作者稿v2](https://arxiv.org/html/0804.3010v2#S5.SS1)，§III-B、§V-A式(39)–(43) | 支持已知协方差Gaussian观测下的风险及导数关系。项目通过完整相关Gaussian探针估计空间交叉矩阵；协方差由观测估计、系数由有限样本选择时无偏及正交性质只是近似。标量反馈增益另沿用已登记D-OAMP式(10)–(11)。 |

具体的实数化、每用户协方差边缘、完整相关探针及矩阵扣除公式见
实验协议（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_colored_20261015/matrix_feedback/PROTOCOL.md`）。
它们是有来源的操作与项目推导的组合，不为组合另设文献算法名；原 Proposed 保持冻结。

2026-10-15 完整协方差参与联合均值变换的开发：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Bernoulli–Gaussian distribution；MMSE denoiser / Bernoulli–Gaussian分布；最小均方误差去噪器 | [Liu–Yu作者稿v2](https://arxiv.org/html/1706.06438v2#S3.SS3)，§III-C式(19)–(22)，附录A Lemma 1式(57)–(61) | 作为已知Gaussian噪声协方差下的解析诊断。这里将用户4096维信道整体视为一个向量；Gaussian活动信道先验仅为对照近似，不宣称NTN信道具有该分布，也不新增主线baseline。 |
| network preconditioning / 网络预条件化 | [Karras等，NeurIPS 2022正式版](https://papers.neurips.cc/paper_files/paper/2022/file/a98846e9d9cc01cfb87eb694d946ce6b-Paper-Conference.pdf)，Table 1，p.3；§5式(7)–(8)，pp.8–9 | 原文以标量噪声方差设置输入、跳连、输出与损失尺度。项目明确推广为P=(βI+C)⁻¹/²、T=β(βI+C)⁻¹、B=[βC(βI+C)⁻¹]¹/²，D=Tr+Bf(Pr,C)。矩阵操作及联合活动先验是项目推导，不是原文的有色噪声定理。 |

本项目通过空间特征分解和逐空间模式的输入特征分解精确施加上述矩阵函数，沿用“特征分解”的通常含义，
不另造算法名称。具体训练范围、实复数尺度及总体损失最优解见
实验协议（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_colored_20261015/preconditioned_joint/PROTOCOL.md`）。

2026-10-15 训练信道二阶矩与受限线性响应核对：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| low-rank approximation；Karhunen–Loève transform；MSE floor / 低秩近似；Karhunen–Loève变换；均方误差下限 | [Edfors等，VTC 1996会议版作者全文](https://lucris.lub.lu.se/ws/portalfiles/portal/6289557/1056818.pdf)，§III-B式(6)–(9)、印刷p.925；§III-C式(10)–(11)、p.926（PDF pp.5–6） | 先验相关矩阵的特征向量及舍弃能量用于量化近似，不把路径数当作固定线性秩。本文献是1996会议版本，不能混写为1998期刊全文。项目用原50000个物理训练样本估计AFDM输出/输入二阶矩；V_kB_k=I的约束解、工作干扰加权和Gaussian协方差补齐另按显式公式推导，没有AFDM实际AWGN保证。 |

对应的统计范围、预定99%/99.9%能量阈值及全部支持失败记录见
子空间核对协议（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_subspace_20261015/PROTOCOL.md`）和
加权解公式（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_subspace_20261015/WEIGHTED_PROTOCOL.md`）。

2026-10-15 完整观测条件下的扩散查询核对：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Denoising Diffusion Restoration Models (DDRM)；Gaussian marginals / 高斯边缘分布 | [Kawar等，作者稿v2](https://arxiv.org/html/2201.11793v2#S3.SS2)，§3.2式(3)–(8)、Proposition 3.1；§3.3 Theorem 3.2；§5.1；[NeurIPS 2022出版记录](https://papers.neurips.cc/paper_files/paper/2022/hash/95504595b6169131b6ed6cd72eb05616-Abstract-Conference.html) | q的边缘对观测噪声积分且使用真实信号，不能据此宣称有限网络pθ的实际查询误差是AWGN。项目使用复数薄SVD、原first和activity的联合均值，以及32个连续噪声方差；这属于显式适配，不是原图像模型复现。反馈均值也没有AWGN保证。 |

适配范围和固定预算见DDRM隔离协议（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_ddrm_20261015/PROTOCOL.md`）。

2026-10-15 原闭环跨轮协方差与逐用户酉因子线性处理：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| damping、error covariance / 阻尼、误差协方差 | [Takeuchi作者稿v2](https://arxiv.org/html/2111.05522v2)，§III-C式(27)–(28)、§III-D式(44)–(45)，§IV-B Example 2式(63)–(78) | 两估计的有限数组MSE混合恒等式单独用于审计；以估计方差标签代入后可能不成立或为负，不冒充LM-OAMP实现，不用真值修改推断。 |
| polar decomposition、unitary polar factor / 极分解、酉极因子 | [Higham 1986作者机构全文](https://eprints.maths.manchester.ac.uk/694/1/high86p.pdf)，Theorem 1.1，§3.1 | 项目令A_k=U_kS_kV_kᴴ、W_k=gV_kU_kᴴ，以共同g归一化整体trace。逐用户热噪声协方差严格为σ²g²I；总误差的自身响应、干扰和历史项不据此成为AWGN。 |
| de-correlated linear estimator / 去相关线性估计器 | [Ma–Ping作者稿v3](https://arxiv.org/html/1602.06509v3)，§III-A式(12)–(14)，§III-I式(31) | 项目沿用迹归一化和工作功率公式，但逐用户极分解的拼接W不一定具有原文整体SVD滤波结构；不能仅凭trace条件继承OAMP的状态演化或误差独立性结论。 |

对应跨轮诊断协议（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_temporal_20261015/PROTOCOL.md`）与
线性候选协议（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_polar_20261015/PROTOCOL.md`）均保留原Proposed三网络和主线文件。

补充定位（2026-10-15）：Ma–Ping同一作者稿§III-D式(21)给出两端误差递推；
§III-E Assumptions 1–2区分线性查询的IID Gaussian要求与非线性反馈的IID及相对A/N独立要求，
后者没有另要求Gaussian；Appendix A说明非线性反馈误差一般可与信号相关。
项目所列完整协方差展开和逐用户白化热噪声的Cauchy–Schwarz下界是显式代数推导，
不是新命名算法或原论文的AFDM定理。推导和适用条件见
隔离线性实验报告（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_polar_20261015/REPORT.md`）。
其中V_kU_kᴴ严格说是A_kᴴ的酉极因子，即A_k的酉极因子的共轭转置；采用该方向是为了从观测映射回信道坐标。

2026-10-16，逐用户发射导频修改的补充定位：Higham同文§2.1式(2.2)、§2.2
Corollary 2.3（印刷pp.1161–1162，PDF pp.3–4）说明方阵的酉极因子是Frobenius
范数下的最近酉矩阵；满秩时唯一。本次对P_k=L_kΣ_kR_kᴴ取发射导频B_k=L_kR_kᴴ，
见配对验证协议（历史文件已清理，原路径：`experiments/proposed_pilot_polar_20261016/PROTOCOL.md`）及
推导（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_pilot_polar_20261016/DERIVATION.md`）。这里改变公开导频及其
仿真观测；数学性质不依赖网络重训，但实际查询仍含其他用户残余、历史依赖及相位估计误差。
准确固定相位下可严格保证用户内单位响应和白热噪声；估计相位时的WWᴴ=I只是一项
代数性质，不能单独推出实际噪声与数据自适应算子独立。

同一推导中对Cai用户块的比较以其v2 §II-A式(3)–(4)、§V-C式(66)的恒模DFT
设定为限；Q_k为NT×N，Q_kᴴQ_k=TP I。用户间耦合平方和(K/T−1)I是从该设定
另行推出的矩阵恒等式；不是新增文献术语，也不构成当前物理信道可辨识性的定理。

2026-10-15 首轮误差的逐维Gaussian离线对照：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| separable covariance；array normal distributions；Tucker product / 可分离协方差；张量正态分布；Tucker乘积 | [Hoff作者稿1008.2169v1](https://arxiv.org/pdf/1008.2169v1)，§2.2 Propositions 2.1–2.2、§3.1，PDF pp.4–5；[2011期刊书目](https://doi.org/10.1214/11-BA606) | 以独立Gaussian张量经过逐维线性变换构造协方差对照。项目将实正态线性构造扩展为proper complex Gaussian，并直接核对Kronecker协方差。三个边缘矩阵使用真实查询误差估计，属于oracle诊断；未证明真实AFDM误差可分离，也未把这些矩阵接入接收机。 |

逐用户功率保持、三维开关及有限差分均为预定诊断设计（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_axis_control_20261015/PROTOCOL.md`），
不设立新的方法名称。Gaussian误差仍可能有色；该区分也见已登记D-GEC §III-B式(39)–(41)。

2026-10-15 原标量反馈下的每轮残差空间处理：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| singular value shrinkage；optimal shrinker for Frobenius loss / 奇异值收缩；Frobenius损失的最优收缩函数 | [Gavish–Donoho作者稿1405.7511v3](https://arxiv.org/pdf/1405.7511v3)，式(7)、PDF p.5；§2.1，p.8；§4，pp.13–15；[TIT 2017](https://doi.org/10.1109/TIT.2017.2653801) | 本项目对16×256复残差使用同一标量函数，再将所得残差估计的空间二阶矩用于工作协方差。原文实矩阵、大系统、低秩及独立白噪声前提不直接覆盖闭环残差；不称其为当前协方差或接收机的最优估计。 |

残差二阶矩减去已知热噪声后投影正半定、共享空间LMMSE、支持范围内Gaussian补齐及原标量反馈的组合，
按协议中的公式（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_uniform_spatial_20261015/PROTOCOL.md`）直接描述；
不赋予新的方法名称，不将其称为FIRE原算法或已成立的AFDM状态演化。

2026-10-15 补噪顺序与有限样本噪声谱核查：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| sample covariance；largest sample eigenvalue；rank determination / 样本协方差；最大样本特征值；秩判定 | [Kritchman–Nadler 2008作者稿](https://www.weizmann.ac.il/math/Nadler/sites/math.Nadler/files/publications/determining_the_number_of_components_in_a_factor_model_from_limited_noisy_data.pdf)，§2，PDF pp.4–5（非中心样本协方差及有限样本噪声特征值离散）；[期刊DOI](https://doi.org/10.1016/j.chemolab.2008.06.002) | 以独立复白噪声模拟16×256数据的最大样本特征值，固定99%经验分位数，再用独立噪声确认。不是作者的Tracy–Widom/未知噪声水平算法；闭环残差与观测噪声相关，不能把参照百分位写成已校准的闭环p值。 |

2026-10-15后续实际查询检查继续采用Dytso–Poor–Shamai §IV式(22)–(23)的条件均值Jacobian术语。
24个已保存查询的中心差分对象为当次完整p(r,v)F(r,v)，不是带历史缓存site的接收机导数。
正的归一化迹不代表完整Jacobian正半定，二阶网络方差代理与该迹的差异单列报告。
OAMP §III-E Assumption 1/2分别约束去噪输入与反馈；Assumption 2并未要求反馈误差本身Gaussian。
因此“各轮输入近似AWGN”与“反馈满足所用推断的统计条件”须分开陈述，不能把反馈信号相关本身写成违反该条假设。

2026-10-15反馈代数检查继续使用D-OAMP §3.3式(7)–(11)的divergence-free denoiser及Stein's unbiased risk estimate术语。
实坐标归一化迹α=tr(J)/(2d)对应复坐标SURE=||D−R||²/d+2vα−v；不直接照搬原文式(10a)中与式(2)归一化约定可能重复的维数因子。
有限数组恒等式SURE−真实风险=(V−v)+2(vα−γ)，以及纯热噪声传播功率的Gaussian四阶矩计算均为项目直接推导，
不是新增的风险估计算法。由功率相对方差换算的“独立复坐标数”仅为所述代数比较，不包装为一般有效样本量定理。
相关来源与全部诊断分别保存于proposed_uniform_spatial_20261015的feedback_check和thermal_power结果目录。

固定W的平滑均值与未补噪查询的等价式、每用户空间部分迹系数、独立补噪在算术阻尼下的
β/(2−β)方差因子均是显式线性代数推导，分别见后续协议（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_uniform_spatial_20261015/ORDERED_PROTOCOL.md`）
和噪声参照设计（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_uniform_spatial_20261015/NOISE_REFERENCE_DESIGN.md`）。
这些式子不消除未知的真实反馈误差与热噪声交叉项。

2026-10-15 实际当轮反馈映射及相关Gaussian交叉项：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Monte Carlo divergence；divergence-free denoiser / Monte Carlo散度；无散度去噪器 | [D-OAMP作者稿](https://arxiv.org/html/1610.05991v1)，§2.1式(2)–(3)，§3.3式(7)–(11) | 中心差分作用于固定进入本轮之前的site历史后的实际Denoiser映射，包含site接受分支与当前分类器；不是整个迭代历史的总导数。双向阻尼和空间处理仍为项目适配；每轮额外网络调用全部计入成本。 |
| SURE for Correlated Gaussian Noise / 相关Gaussian噪声的SURE | [Raphan–Simoncelli，作者机构全文](https://www.cns.nyu.edu/pub/eero/raphan08-preprint.pdf)，§III-A式(7)–(10)，印刷p.1345（PDF p.4）；§III-B式(11)–(13) | 相关输入的Stein交叉项涉及协方差加权Jacobian迹，不能直接以v乘普通归一化迹替代。复坐标归一化及AFDM工作协方差块为直接推导；不据此宣称实际闭环误差为Gaussian或工作协方差是真实协方差。 |

对应完整接收机开发协议（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_uniform_spatial_20261015/feedback_receiver/PROTOCOL.md`）
与相关输入交叉项推导（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_uniform_spatial_20261015/feedback_receiver/COLORED_STEIN_NOTE.md`）。

2026-10-15后续固定导数探针对照（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_uniform_spatial_20261015/feedback_probe_control/PROTOCOL.md`）
只改变Monte Carlo方向在各轮之间是否重新抽取，不为此设立新算法名称，不声称继承状态演化保证。
输入维滤波与空间查询的组合推导（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_uniform_spatial_20261015/input_filter/DESIGN.md`）
沿用上述奇异值、迹归一化、极分解和协方差术语；逐用户迹/功率约束及空间部分迹均为显式代数推导。
该阶段纯公开算子检查不等同于接收机性能实验。

后续组合接收机确认（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_uniform_spatial_20261015/input_filter/confirmation/REPORT.md`）
已完成八个独立物理场景的48条运行。逐用户滤波与每轮空间处理仍按显式公式描述，未建立新算法名称。
查询的协方差偏离下降、点性能门槛通过不等于独立Gaussian成立；反馈的空间颜色及工作方差偏差仍保留。
物理场景配对bootstrap区间只作小样本描述，不能将预定容差的点估计检查称为已经证明总体非劣。

2026-10-15 历史协方差与原始观测风险：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| orthogonality；asymptotic IID Gaussianity / 正交性；渐近IID Gaussian性质 | [Memory AMP作者稿v7](https://arxiv.org/pdf/2012.10861v7)，§III式(20)、(24)、(30)、(32)，PDF pp.6–8 | 区分状态演化中的Gaussian等效变量、原坐标实际反馈及与全部历史输入误差的正交关系；不能将摘要简称扩大为非线性反馈必然独立于信号。匹配BPSK后验均值反例为项目解析核对，不是AFDM实验。 |
| Stein's unbiased risk estimate (SURE) / Stein无偏风险估计 | [Nobel、Candès、Boyd，TSP 2023作者机构全文](https://web.stanford.edu/~boyd/papers/pdf/sure_tractable_eval.pdf)，§I-A式(1)、§I-B，p.4330 | 对Y↦AF_t(Y)的公式目标是观测均值AH的风险。复坐标因子、历史交叉风险和完整历史依赖按显式公式展开；该文凸优化算法与弱可微结论不能直接套给当前有分支的神经接收机。 |

本轮报告（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_memory_requirements_20261015/REPORT.md`）保留残差协方差偏差的三项恒等式分解，
以及归一化权重下共同噪声扣除项为常数的代数核对，不为此创造新的算法名称。
四条原样重放与离线历史融合不等于完整Memory AMP实现；原始观测的完整映射求导仍属待验证设计。

2026-10-15 原始观测完整响应与补噪表示核对：

固定轮数协议（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_measurement_response_20261015/PROTOCOL.md`）沿用上述SURE术语。
有限差分对固定轮数的完整Y→AF_t映射求导，包含历史依赖；不包含自适应停止时间的导数。
由于分支与有限探针，该核对不等于证明弱可微或无偏风险估计成立。

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| positive semidefinite square root / 半正定平方根 | [Higham，Functions of Matrices，2014作者机构书章](https://eprints.maths.manchester.ac.uk/2109/1/fm2_final_njh.pdf)，§17.5 Fact 2，印刷p.17-7（PDF第8页） | 仅在已保存补噪协方差上离线比较U diag(sqrt(d))与唯一Hermitian半正定平方根U diag(sqrt(d)) U^H。相同协方差对应相同条件Gaussian分布，但固定随机数下路径可不同；该矩阵级检查不构成新接收机性能实验。 |

上述半正定平方根亦已核对期刊原文：[Higham–Schreiber，1990](https://eprints.maths.manchester.ac.uk/340/1/0911038.pdf)，
§1 p.648（唯一Hermitian半正定平方根）、§2 p.651（计算与特征分解形式）。
完整响应结果（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_measurement_response_20261015/REPORT.md`）已完成36条重放，
末轮交叉项解释与早期差分不稳定分别报告；半正定平方根目前仅作离线矩阵对照，尚未进入接收机。

后续进展（2026-10-15）：半正定平方根已进入独立数值映射的响应实验，
原路径复现1/4通过与自身严格复现4/4通过分别保留，原Proposed未替换。
空间矩阵扩展继续采用Raphan–Simoncelli §III-A式(7)–(10)、p.1345的Gaussian积分分部依据；
复数Jacobian的天线块部分迹、平滑反馈及逐样本Q+R分解是项目公式，
不是原论文已有算法名称。证据见阶段报告（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_measurement_root_20261015/self_response/REPORT.md`）。

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| nearest symmetric positive semidefinite matrix；positive approximant / 最近对称半正定矩阵；半正定近似 | [Higham 1988作者全文](https://nhigham.com/wp-content/uploads/2023/10/high88d.pdf)，§2 Theorem 2.1、式(2.1)–(2.2)，pp.105–106；§1 p.104说明可扩展到复矩阵 | 用于后续Hermitian矩阵正部投影的优化依据，不解释为当前统计模型最优。给定估计迹或各向同性约束为项目显式优化推导；本阶段未将这些候选接入推断。 |

上述三种矩阵约束的全轮离线比较（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_covariance_constraints_20261015/REPORT.md`）
已经完成；合法性改善未能稳定恢复方向信息，未接入推断。
实际查询分解（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_query_terms_20261015/REPORT.md`）沿用Ma–Ping §III-D式(21)
的误差递推，将完整二阶矩、噪声交叉项及补噪项逐项展开。
S=r0−W solve(I−AW,Y−A r0)直接来自原更新式；七项分解和Gaussian空间样本二阶矩RMS
是项目显式推导，不冠以新算法名称，不将样本非对角项直接当成总体非白的证明。

## L-DAMP 输出结构处理

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Truncated SVD (TSVD) / 截断奇异值分解（L-DAMP 结构对照） | [Gavish–Donoho，arXiv:1405.7511v3](https://arxiv.org/html/1405.7511v3#S1)，§1，式(2)后的 TSVD 定义及式(3)；2026-10-15 核对作者全文 | 将每用户估计信道展开为 16×256，保留一个奇异分量；只依赖估计。比较最终输出处理与每轮复合去噪，后者计算完整复数实方向导数及跨波束校正。秩一来自本项目零路径方向扩展条件，不将最小二乘近似性质等同于最优后验均值，不引用白噪声渐近最优性保证当前 AFDM 闭环。实现与对照：`docs/history/experiments/ldamp_structure_20261015/`。 |

## L-DAMP、Cai 与 Huang 的等效误差处理核对（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| effective noise / equivalent noise；Onsager correction / 等效噪声；Onsager 校正 | [He v2](https://arxiv.org/pdf/1802.01290v2)，§III-A 式(4)–(8)，PDF p.2；[Metzler 2017](https://proceedings.neurips.cc/paper_files/paper/2017/file/8597a6cfa74defcbde3047c891d78f90-Paper.pdf)，§2.1、§4.1 Finding 1 与脚注5，PDF pp.6–7 | 原路线以校正项抵消迭代偏差，使去噪查询近似匹配 AWGN。Metzler 当时将 D-AMP/LDAMP 状态演化标为经验发现，列出大系统、随机 Gaussian/subgaussian 测量及 Lipschitz 去噪器等条件；不能作为当前有限结构化 AFDM 算子的保证。He §II 的选择矩阵为归一化 ±1 元素，不能将其系统模型统一改述为精确 iid Gaussian。 |
| pseudo AWGN observation model；damping / 伪 AWGN 观测模型；阻尼 | [Cai v2](https://arxiv.org/html/2506.00581v2#S5.SS2.SSS1)，§V-B1，式(57)–(58) | 原文明示大系统及右旋转不变随机算子条件，承认有限维度和具体矩阵下等效噪声可能非 Gaussian，以均值、方差阻尼改善数值稳定性；并未证明阻尼恢复白性、Gaussian 性或准确方差校准。 |
| likelihood-annealed Langevin dynamics / 似然退火 Langevin 动力学 | Huang 2026 本地全文（历史路径，见迁移记录：`reference/huang2026_prior_agnostic_afdm_diffusion.pdf`），§III-A–B 式(6)–(10)，p.2951；Algorithm 1、§IV，p.2952；[DOI](https://doi.org/10.1109/LWC.2026.3689601) | 直接结合原始观测残差的似然梯度、学习的先验 score 和随机扰动；Algorithm 1 使用 1/(σ_z²+σ_i²) 退火权重，并衰减步长。这不是线性模块误差的白化或协方差估计，不依赖把当前状态解释成真值加独立 AWGN 的局部后验均值接口，但有限噪声层级的似然近似、网络误差和有限迭代仍存在。式(10)及 Algorithm 1 的残差符号问题沿用本页已有核查，不能直接照抄。§IV 的 L-DAMP baseline 引用 He [23]，正文未给出专门处理有色/非 Gaussian 伪观测误差的修正，不能从其曲线推断存在这种修正。 |

本次只核对原文、现有代码与术语边界，未训练网络、运行接收机比较或修改推断算法。

## 冻结 score 与活动分类器的复数矩阵 AMP（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| vector AMP algorithm；state evolution / 向量 AMP 算法；状态演化 | [Liu–Yu，作者稿 v2](https://arxiv.org/html/1706.06438v2#S3.SS2)，§III-B 式(14)–(17)，§III-D | 多测量向量共享感知矩阵时传播特征协方差；不能从矩阵 AMP 推出本项目相关信道的误差协方差自动为标量阵。 |
| Complex Approximate Message Passing with Non-separable Denoising；Wirtinger derivatives / 非可分去噪的复数近似消息传递；Wirtinger 导数 | [Kunde 等，2026 预印本 v1](https://arxiv.org/html/2604.21115v1#S3.SS3)，§III-C 式(18)–(21)、Remark 14，Appendix B；§III-B Assumption 8 | 完整联合去噪映射的复 Jacobian 部分迹与复矩阵校正。引用其 iid proper-complex Gaussian 及函数正则条件；当前有限 AFDM 不宣称满足其状态演化定理。 |
| Onsager correction；Monte Carlo approximation / Onsager 校正；Monte Carlo 近似 | [He 等，作者稿 v2](https://arxiv.org/html/1802.01290v2#S3.SS1)，§III-A 式(4)–(8) | 新循环保留完整活动概率与 score 均值的依赖；四次中心差分和复矩阵部分迹是按明确索引推导的实现，有限步长与有限探针误差均须报告。 |

本项目的具体重排、共同尺度变换、活动概率乘均值的完整链式导数、随机相位 DFT
探针及匹配尺寸 AWGN 参照均在 [完整推导](https://github.com/RESET-cpu/afdm-gfra/blob/416a4dd4bd219dd9fb5049294bc02f4854f472f4/paper/STMP/docs/PROPOSED_AMP.md) 中直接给出公式。
`score_amp` 是软件入口标识，不作为新造的学术算法名称；原 Proposed 保持独立。
运行条件、失败与代价见 本次结果（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_amp_20261015/REPORT.md`）。

## AMP首轮失配与后续稳定性的区分（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| state evolution；covariance matrix / 状态演化；协方差矩阵 | [Liu–Yu作者稿v2](https://arxiv.org/html/1706.06438v2#S3.SS2)，§III-B式(16)–(18)，§III-D Theorem 1式(23) | 一般MMV等效误差保留特征协方差；该文的标量阵简化使用各向同性Rayleigh先验与匹配MMSE等条件。不能将Onsager称为任意天线相关性的白化算子。 |
| Denoising Generalized Expectation-Consistent Approximation (D-GEC)；colored-noise-aware denoiser / 基于去噪的广义期望一致近似；适配有色噪声的去噪器 | [Shastri等2022期刊作者全文](https://phil-schniter.web.app/pdf/jsait22_dgec.pdf)，§III-A Algorithms 2–3、式(31)、(36)–(37)，pp.534–535；§III-B式(38)–(40) | 借鉴分组误差统计与匹配有色噪声的学习接口。MRI的分组模型和corr+corr训练并非本项目已完成方案；式(36)为经验误差模型。16×16天线协方差条件score与活动分类器按显式密度公式提出，不冠以新算法名。 |
| Damped Denoising Vector AMP (DD-VAMP)；denoiser sensitivity / 带阻尼的基于去噪的向量AMP；去噪器灵敏度 | [Sarkar等2021作者稿](https://arxiv.org/pdf/2010.11321v1)，§3.1 Algorithm 1、式(9)–(14)，p.3；§3.2初始化 | 为一致阻尼、Monte Carlo灵敏度波动及初始化消融提供依据，不将其标量正精度的平方根操作直接用于一般复数矩阵，也不宣称阻尼恢复AFDM查询白性或保证当前神经网络迭代收敛。 |

后续诊断（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_amp_20261015/diagnosis_followup/REPORT.md`）保留了40次真值辅助单次网络对照及旧Proposed首轮同样全判活跃、后续恢复的事实。
天线相关性足以复现这组固定输入的网络异常，不等于识别了完整循环失败的唯一原因。
实坐标协方差Tweedie式、白化改变先验的反例及残差天线二阶矩均以显式公式陈述；候选修改尚未训练或接入接收机。

## AMP阻尼与历史偏导（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| functions of all previous iterates；debiasing coefficients / 依赖全部历史迭代量的函数；去偏系数 | [Fan作者稿v5](https://arxiv.org/html/2008.11892v5#S5)，§5式(5.3)–(5.8)、(5.12)，Remark 5.1 | iid Gaussian特例的历史Onsager系数由对应历史输入的偏导平均给出。固定几何阻尼权重及其紧凑递推为本项目显式展开；不把原文旋转不变模型的全部谱校正替换成当前有限AFDM的保证。 |
| Wirtinger derivatives；matrix extension / Wirtinger导数；矩阵扩展 | [Kunde等2026预印本v1](https://arxiv.org/html/2604.21115v1#S3.SS3)，§III-C式(18)–(21)、Remark 14，Appendix B | 固定有限轮数的历史列扩展用于核对非可分复矩阵部分迹的块位置。实际仍用8探针有限差分；条件噪声标签冻结不等于已证明其自适应规则满足状态演化条件。 |
| full-memory AMP / 全历史AMP | [Rossetti–Nazer–Reeves作者稿v2](https://arxiv.org/html/2405.08225v2#A1)，Appendix A，Theorem 5式(59)–(62)，A.2.1式(70)–(72) | 以矩阵列表示固定有限轮数的历史，为本次独立代数核验提供依据。原文此定理使用GOE随机矩阵；不据此声称当前矩形复数AFDM实现满足其统计定理，也不将当前实现命名为OpAMP。 |

阻尼权重、历史校正、含交叉项的方差与确定性固定点谱均在[推导](https://github.com/RESET-cpu/afdm-gfra/blob/416a4dd4bd219dd9fb5049294bc02f4854f472f4/paper/STMP/docs/PROPOSED_AMP_DAMPING.md)按公式直接说明。
`score_amp_damped`为独立软件入口；没有把该递推包装成DD-VAMP或新增学术名称。
原Proposed及无阻尼score_amp保留；新版本的概率输出仍取当前原始分类器，主要信道输出为阻尼状态。


## AMP 查询阻尼与双重历史权重（2026-10-15）

沿用上节的 functions of all previous iterates、debiasing coefficients 和 Wirtinger derivatives，
不新增学术算法名称。依据仍为 [Fan v5](https://arxiv.org/html/2008.11892v5#S5)
§5式(5.3)–(5.8)、(5.12)、Remark 5.1，以及
[Kunde v1](https://arxiv.org/html/2604.21115v1#S3.SS3) §III-C式(18)–(21)、Remark 14、Appendix B。
查询/反馈两侧阻尼的经验动机参照 [Cai v2](https://arxiv.org/html/2506.00581v2#S5.SS2.SSS1)
§V-B1式(57)–(58)，但本实现并未照搬其方差递推。

[本次推导](https://github.com/RESET-cpu/afdm-gfra/blob/416a4dd4bd219dd9fb5049294bc02f4854f472f4/paper/STMP/docs/PROPOSED_AMP_QUERY_DAMPING.md) Q1–Q9显式展开查询权重和输出权重，
校正项用同查询权重混合的残差乘当前完整联合映射的复Jacobian部分迹。
混合残差能量包含跨轮交叉项；其等于实际查询误差功率需要额外统计条件，
有限AFDM下不能由代数恒等式宣称AWGN或收敛。`score_amp_query_damped`仅为软件入口。

## 固定 L-DAMP 中的冻结 score 替换（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| automatic differentiation；forward mode；Jacobian–vector product / 自动微分；前向模式；Jacobian 与向量的乘积 | [Baydin等，JMLR 2018](https://www.jmlr.org/papers/volume18/17-468/17-468.pdf)，§3.1，pp.9–11，式(4)；§3.2，pp.12–13 | 对完整活动概率乘 score 均值的实映射求方向导数；去掉训练特征上的 detach 仅为保留正确链式依赖，不改变原训练代码。方向导数按计算图求出；float32 误差与八探针部分迹采样误差仍存在。 |
| Tweedie's formula；Wirtinger derivatives；Onsager correction / Tweedie公式；Wirtinger导数；Onsager校正 | [Cai v2](https://arxiv.org/html/2506.00581v2#S4)，§IV-A–C，式(43)–(54)；[Kunde v1](https://arxiv.org/html/2604.21115v1#S3.SS3)，§III-C式(18)–(21)、Remark14；[He v2](https://arxiv.org/html/1802.01290v2#S3.SS1)，§III-A式(4)–(8) | 原逐波束 DnCNN 和全部天线 score 使用同一矩阵更新；后者需完整跨波束部分迹。将逐波束方差压成 tr(Σ)/C 是受检验的接口适配，不是已有论文对本AFDM的保证。 |

[推导与接口](https://github.com/RESET-cpu/afdm-gfra/blob/416a4dd4bd219dd9fb5049294bc02f4854f472f4/paper/STMP/docs/LDAMP_SCORE.md)明确坐标、归一化、完整链式导数和失败处理；
同查询与闭环记录（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/ldamp_score_swap_20261015/REPORT.md`）区分基线验收、四例开发诊断与候选失败。

## AMP 与扩散／score 先验结合的文献核对（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| denoising-based approximate message passing；reverse diffusion process / 基于去噪的近似消息传递；反向扩散过程 | [Dai 等，Enhancing Approximate Message Passing via Diffusion Models Towards On-Device Intelligence，ICC Workshops 2024](https://ieeexplore.ieee.org/document/10615843/)，出版社摘要，DOI:10.1109/ICCWorkshops59551.2024.10615843 | 摘要明确将反向扩散实现的噪声估计模块加入基于去噪的 AMP。本次仅核实出版社摘要与书目信息，未取得全文；不据此断言其具体 Onsager 公式、噪声调度或 AFDM 性能。 |
| Diffusion Message Passing (DMP)；DMP-DUN / 扩散消息传递；原文深度展开网络名称 | [Liao–Shen–Li–Wang，CVPR 2025，作者稿](https://arxiv.org/html/2503.08429v1#S4)，§4.1–4.3，Assumptions 1–3、式(2)、(5)–(8)；§4.5 式(9)及其前后训练说明；[作者代码](https://github.com/FengodChen/DMP-DUN-CVPR2025) | DMP 每次迭代包含一步反向扩散；DMP-DUN 用可训练 ResBlocks 实现输入调整与 Onsager 相关反馈操作，并学习时间和尺度参数。DMP-DUN 冻结预训练扩散模型、训练其余参数；DMP-DUN+ 连同扩散模型一起训练，训练参数还包括感知矩阵。理论陈述另假设 Gaussian 大系统、Lipschitz 去噪器、完美反向去噪与完美 Gaussian filter；不能视为固定 AFDM 算子及现有冻结 score 直接替换的保证。本次没有复现或独立验证其定理。 |
| score-based turbo message passing (STMP)；score-based MMSE denoising / 基于 score 的 Turbo 消息传递；基于 score 的 MMSE 去噪 | [Cai–Yuan–Zhang，Score-Based Turbo Message Passing for Plug-and-Play Compressive Image Recovery，SPAWC 2025，v2](https://arxiv.org/html/2503.22140v2#S2)，§II 式(3)–(13)，§III 式(14)–(15)，§IV–V；[扩展作者稿，Cai–Jiang–Yuan–Zhang，2025](https://arxiv.org/html/2512.14435v1#S4)，§III–V | 用第一、第二阶 score 构造近似 MMSE 均值与方差，经 LMMSE 和 Gaussian 外信息更新进行迭代，不要求运行完整反向扩散采样。属于 Turbo-CS／VAMP／EP 相关路线，不能混同于标准 D-AMP 残差更新。该结构与本项目原 Proposed 更接近；文献中的大系统误差模型不保证有限 AFDM 查询为 AWGN。 |

本次检索区分直接在 AMP 启发的迭代中嵌入反向扩散，与在 Turbo 消息传递中调用 score 构造的去噪器。
现有冻结 score 替换的失败只界定已测试接口和循环的表现，不构成扩散／score 先验与整个 AMP 类算法不相容的结论。

## 独立训练的 score 与矩阵 D-AMP（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本轮实现范围 |
|---|---|---|
| denoising score matching；score-based MMSE denoising / 去噪得分匹配；基于score的MMSE去噪 | STMP v2 本地全文（历史路径，见迁移记录：`reference/score_amp_20261015/cai2025_stmp_spawc_v2.pdf`），p.3，§III式(14)、§IV-A式(18)–(19) | 新模型学习活动混合的单波束汇总边缘先验。实方差τ=v/2；以D参数化score时 λ_s=λ_Dτ²。总体最优均值关系不等于有限CNN已达到MMSE。原文Turbo外信息更新未搬入此残差AMP。 |
| network preconditioning / 网络预条件化 | EDM本地全文（历史路径，见迁移记录：`reference/score_amp_20261015/karras2022_edm.pdf`），p.3 Table 1、式(2)–(3)；§5式(7)–(8) | 实坐标输入/跳连/输出尺度和权重沿原文公式；σdata²取当前混合总体实方差，非原图像常数。48通道4残差块、噪声控制通道仿射、log-uniform方差和独立训练均为本项目实现选择。 |
| Onsager correction；Wirtinger derivatives；functions of all previous iterates / Onsager校正；Wirtinger导数；依赖全部历史迭代量的函数 | He §III-A式(4)–(8)、Kunde §III-C式(18)–(21)/Remark14、Fan §5式(5.3)–(5.8)/Remark5.1，来源链接见前文 | 复矩阵1/Q部分迹、配对JVP与逐波束16×16块按显式索引核验；同步状态阻尼用历史校正递推。8探针近似、冻结噪声标签和有限结构化AFDM均保留统计适用性限制。 |

新入口 `diffusion_amp` 仅为软件标识。[完整推导](https://github.com/RESET-cpu/afdm-gfra/blob/416a4dd4bd219dd9fb5049294bc02f4854f472f4/paper/STMP/docs/DIFFUSION_AMP.md)记录具体公式，
文献审查（历史路径，见迁移记录：`reference/score_amp_20261015/AUDIT.md`）记录DMP-DUN补充p.1式(1)/(3)及(6)/(9)
的尺度关系差异；这些印刷式的代数问题不能据以断言作者端到端实验代码错误。
八份已下载PDF与ICC 2024全文尚缺的状态见下载索引（历史路径，见迁移记录：`reference/score_amp_20261015/README.md`）。

## 完整用户共同活动与矩阵 D-AMP（2026-10-15）

2026-10-15 正式验证前的校正计算修订：矩阵 Onsager 的定义仍采用 Kunde §III-C
式(18)–(21)及 Remark 14。利用当前网络的用户独立性，直接计算 ZB 的取样公式、
完整 N 行基恒等式和无放回样本标准误差是本项目的线性代数与抽样推导，未命名为
新的文献算法。式子与条件见 [JOINT_AMP](https://github.com/RESET-cpu/afdm-gfra/blob/416a4dd4bd219dd9fb5049294bc02f4854f472f4/paper/STMP/docs/JOINT_AMP.md) 式(15c)–(15e)及
独立数值审计（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/joint_amp_20261015/projected_development_v1/DERIVATION.md`）。
完整基只消除该固定 Jacobian 部分迹的抽样误差；不消除网络误差、不证明 AFDM
高斯性或状态演化。早期显式矩阵探针实现仍保留为开发对照。

| 原词或忠实译名 | 原文定位 | 本轮实现范围 |
|---|---|---|
| density ratio estimation；class-probability estimation；logistic loss / 密度比估计；类别概率估计；logistic 损失 | [Menon–Ong，2016](https://proceedings.mlr.press/v48/menon16.pdf)，§2.2、§3 式(6)–(8)、§4.2 式(16)–(17)，pp.305–306；[Rizvi–Pettee–Nachman v1](https://arxiv.org/html/2305.10500v1#S2)，§I 式(2)–(5)、脚注1，§II 式(6)–(12)、Table 1 | 完整用户共享活动变量；两类使用相同噪声标签采样律、平衡 BCE 学习 ℓ；p=sigmoid(logitρ+ℓ) 由公开活动先验修正。有限分类器不自动成为准确密度比或校准后验。 |
| denoising score matching；network preconditioning / 去噪得分匹配；网络预条件化 | STMP v2（历史路径，见迁移记录：`reference/score_amp_20261015/cai2025_stmp_spawc_v2.pdf`），p.3 §III 式(14)、§IV-A 式(18)–(19)；EDM（历史路径，见迁移记录：`reference/score_amp_20261015/karras2022_edm.pdf`），p.3 Table 1、§5 式(7)–(8) | F 只用活跃条件 MSE 训练，γ 为活跃实功率；16 束方差及完整用户网络为明确实现选择。L_F+L_BCE 不称为混合先验 DSM；理想两头组合 pF 给出混合均值，有限头不保证同一精确密度。 |
| Jacobian of the conditional mean；conditional covariance / 条件均值 Jacobian；条件协方差 | Dytso–Poor–Shamai，TIT 2023 正式版（历史路径，见迁移记录：`reference/afdm_network_axes_20261013/phase2_representation/dytso2023.pdf`），p.1883 式(3)，§III Proposition 1 式(17)，p.1885；式(9)定义输入在前的 Jacobian | 本项目采用输出行/输入列约定 J_D=Cov(x\|r)T⁻¹；异方差一般非对称。∇ℓ=T⁻¹F 与 pF 的完整乘积导数直接由 Gaussian 模型推导；有限双头一致性另行报告。 |
| Wirtinger derivatives；Onsager correction；functions of all previous iterates / Wirtinger 导数；Onsager 校正；依赖全部历史迭代量的函数 | [Kunde v1](https://arxiv.org/html/2604.21115v1#S3.SS3)，§III-C 式(18)–(21)、Remark 14、Appendix B；[Fan v5](https://arxiv.org/html/2008.11892v5#S5)，§5 式(5.3)–(5.8)、Remark 5.1 | 实际 pF 映射含全部用户内依赖；以配对 JVP、16 组随机相位 DFT 探针估计完整256×256部分迹，同步阻尼保存历史反馈。固定 V、ρ 的偏导不含标签估计总导数；当前 AFDM 不宣称满足随机矩阵状态演化条件。 |

`joint_amp` 仅为软件入口名。[完整推导](https://github.com/RESET-cpu/afdm-gfra/blob/416a4dd4bd219dd9fb5049294bc02f4854f472f4/paper/STMP/docs/JOINT_AMP.md)逐式定义全用户双头、
score 换算、完整跨束校正及活动读出。独立数学审查（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/joint_amp_20261015/MATH_AUDIT.md`）
记录解析混合例子、导数约定和统计限制。完整用户信号输入不等于完整有色噪声条件化；
网络仍只使用16个逐束方差。原 Proposed 和逐束 `diffusion_amp` 均保留。

上述实现还将 EDM 直接跳连 p c_skip I 的部分迹精确扣加，再用相同探针估计
剩余完整导数；操作按 [式(15b)](https://github.com/RESET-cpu/afdm-gfra/blob/416a4dd4bd219dd9fb5049294bc02f4854f472f4/paper/STMP/docs/JOINT_AMP.md)直接列式，不另造方法名称。
已知分量的期望是精确的，但有限探针方差可增可减；开发结果和合成核查
不构成当前AFDM状态演化保证。

## AWGN 去噪训练与闭环验证（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| layer-by-layer training；denoiser-by-denoiser training / 逐层训练；逐去噪器训练 | [Metzler–Mousavi–Baraniuk，NeurIPS 2017 正式版](https://papers.neurips.cc/paper/6774-learned-d-amp-principled-neural-network-based-compressive-image-recovery.pdf)，§3，p.5；§4.1 Finding 1、§4.2 Lemma 1，p.7 | 原文区分闭环逐层训练与独立 AWGN 去噪训练；其最优性分析依赖所列状态演化及单调性条件。当前连续噪声条件网络独立训练，不等同于已完成逐层或端到端训练。63k 权重的 AWGN 指标改善但 AFDM 闭环失败已保留，不能以该文保证结构化有限 AFDM 中二者单调对应。 |

当前开发阶段的检查点和阻尼选择是明确登记的实验操作，没有命名为新的论文方法。
首轮阻尼能量界只来自固定查询的二次式，不是状态演化或收敛定理。

## 低 SNR 下估计物理参数的局部约束（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| first-order linear approximation / 一阶线性近似 | [Wei 等，Off-grid Channel Estimation with Sparse Bayesian Learning for OTFS Systems](https://arxiv.org/html/2101.05629v1)，§III-B 式(17)–(24) | 使用当前 AFDM 原子及 delay、Doppler 导数张成三维局部空间；具体导数与 wrapped-delay 分支见 OFFGRID_BASELINES.md。这是本项目约束，并非原 OTFS SBL 接收机。 |
| Gaussian distribution conditioned on linear constraints / 线性约束下的 Gaussian 条件分布 | [Simpson–Turner–Pettitt，ANZIAM J.48，2008](https://journal.austms.org.au/ojs/index.php/ANZIAMJ/article/download/131/1104)，§2 式(2)，p.C1044 | 各向同性 Gaussian 在固定正交子空间中的均值与协方差为 Pμ、τP；按 AFDM 坐标平均给出 rank(P)/256。基由观测估计、分类器和风险近似的误差另行验证，不声称整个接收机等于精确条件后验。公式见 THEORY.md §13。 |

## AMP 基础控制与局部 Gaussian 似然（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Bernoulli–Gaussian；MMSE denoiser / Bernoulli–Gaussian 先验；MMSE 去噪器 | [Liu–Yu 作者稿 v2](https://arxiv.org/html/1706.06438v2)，§III-C 式(19)–(22)，Appendix A Lemma 1 式(57)–(61) | 本轮将一个活动变量扩展到用户的 N×C 块，显式推导均值 pαR、完整概率导数与矩阵反馈；精确性只针对独立 Gaussian 查询的局部模型。活跃条件 iid Gaussian 与物理信道结构不同，不能比较两者 NMSE 排名。 |
| conditionally Gaussian；MMSE filter / 条件 Gaussian；MMSE 滤波器 | [Neumann–Wiese–Utschick 作者稿](https://arxiv.org/pdf/1707.05674)，§II–III 式(2)–(16)，前文已有原文核对 | 首轮 R_k=A_kᴴA_kX_k+η_k 及其给定其他活动的协方差，直接从本项目 Y=AX+W 推导。保留 G_k 的局部似然和候选支撑相对后验见本轮数学审查§11–12；不称为该论文已有 AFDM 方法。用公共ρ替代其他活动仅匹配二阶矩，并非精确边际化；oracle仅给其他活动，不能作部署性能。 |
| Onsager correction；Wirtinger derivatives / Onsager 校正；Wirtinger 导数 | [Kunde v1](https://arxiv.org/html/2604.21115v1#S3.SS3)，§III-C 式(18)–(21)、Remark14、Appendix B；[Fan v5](https://arxiv.org/html/2008.11892v5#S5)，§5 式(5.3)–(5.8)、Remark5.1 | 本次用精确解析 ZB 排除随机探针误差，并独立核查同步反馈。固定Gaussian递推的LMMSE恒等式与稳定谱由项目直接推导；不把该代数通过等同于自适应标签、非线性活动或有限AFDM的状态演化已获证明。 |

完整推导与审查（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/amp_foundation_20261015/MATH_AUDIT.md`）与
全部控制结果（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/amp_foundation_20261015/REPORT.md`）分别记录代数、模拟证据和局限。
相关系数RMS、四阶量、相对更新与固定轮数AER均是显式定义的诊断量，不命名为新的算法。

## 查询偏离 AWGN 的方案调研（2026-10-15）

本节仅记录文献比较，不代表采用新算法；主报告见
方案调研（历史路径，见迁移记录：`reference/awgn_solution_review_20261015/REPORT.md`）。
既有 D-GEC、OAMP-MMV、VAMP、Memory AMP、FIRE、广义 Gaussian 条件均值术语沿用前述来源。

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| learned AMP (LAMP)；learned VAMP (LVAMP) / 学习型 AMP；学习型 VAMP | [Borgerding–Schniter–Rangan，TSP 2017作者稿](https://phil-schniter.web.app/pdf/tsp17_lamp.pdf)，§III-C Algorithms 2–3，pp.4298–4299；§V-A/B式(41)，pp.4300–4301；§VII | 展开迭代并学习线性/非线性参数的先例。真实 AFDM 查询微调、未知相位条件化和联合活动训练是待验证项目适配，不宣称已复现原论文。 |
| maximum likelihood estimation；activity detection via coordinate-wise optimization / 最大似然估计；逐坐标优化活动检测 | [Fengler等，TIT 2021作者稿v3](https://arxiv.org/html/1910.11266v3)，§II-A式(6)–(7)，§III-A式(8)–(9)，§III-C Algorithm 1；§IV-B4 | 直接观测协方差似然的来源。原文独立Rayleigh信道和用户标量导频不等于当前AFDM结构先验；256列不作256份独立天线样本。用于合成控制及备选设计，不替换主线分类器。 |
| anisotropic denoising score matching；normalized energy model / 非各向同性去噪得分匹配；归一化能量模型 | [Zilberstein–Segarra–Simoncelli–Guth，2026预印本v1](https://arxiv.org/html/2605.15487v1)，§3.1–3.3式(7)–(10)，Appendix C | 原文协方差族限制于空间域或Fourier域对角形式，不是任意full covariance的AFDM解决定理；本轮仅作研究储备。 |
| Exact Posterior Score Estimation (EPS) / 精确后验得分估计 | [Mammadov等，2026预印本v1](https://arxiv.org/html/2606.17048v1)，§3.2 Theorem 1式(11)–(12)，§3.4 Proposition 3式(15)–(16) | 精确关系基于已知线性Gaussian生成模型及对应条件去噪器。有限训练近似、同观测估计相位和任意已有迭代输入不自动继承精确性；未实施。 |

来源版本、最新非可分理论条件以及本地失败实验的适用范围分别见
理论笔记（历史路径，见迁移记录：`reference/awgn_solution_review_20261015/theory_notes.md`）与
有色噪声笔记（历史路径，见迁移记录：`reference/awgn_solution_review_20261015/colored_notes.md`）。

本轮后续实际查询实验（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/query_matched_20261015/REPORT.md`）只续训原分类器
最终线性层，沿用已登记的类别概率估计、logistic损失及先验概率修正；它不是
LAMP/LVAMP复现、逐层展开训练或三网络联合训练。控制中的16×16矩阵明确是
AFDM输入列轴的未中心化二阶矩，不称为完整误差协方差。
小系统的联合活动支撑枚举直接由Gaussian似然与Bernoulli先验求边缘后验，
依据为前述Gaussian条件模型和活动似然；未另立算法名称，oracle仅用于诊断。

## 未知活动的 Gaussian 观测后验控制（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| collapsed Gibbs sampler；grouping / blocking；full conditional distributions / 积分消元后的 Gibbs 采样；分组更新；完整条件分布 | [J. S. Liu，JASA 1994](https://www.cs.columbia.edu/~blei/fogm/2023F/readings/Liu1994.pdf)，§1、印刷p.958，所读PDF第2页（第1页为封面）；定义段无式号 | 积分掉iid Gaussian活跃信道，保留二元活动，联合更新两个用户的四状态条件概率。具体AFDM用户块公式为项目推导；不声称有限预算或任意分块有混合保证。 |
| sample covariance；maximum likelihood estimation / 样本协方差；最大似然估计 | [Fengler等，TIT 2021作者稿v3](https://arxiv.org/pdf/1910.11266v3)，§II-A PDF p.9式(6)–(7)；§III-A p.9式(8)–(9)、p.10式(11)、p.11式(12) | logdet＋trace观测似然的来源。原文有连续松弛ML及已知衰落时二元约束ML；本项目改为用户块AkAkᴴ并加Bernoulli先验、对活动作后验积分，不称为原文ML算法。列独立只属于本轮合成模型。 |
| mixture estimator / 混合估计量 | [Liu–Wong–Kong，Biometrika 1994](https://www2.stat.duke.edu/homeweb/scs/Courses/Stat376/Papers/ConvergeRates/GibbsSampling/LiuWongKongBiometrika1994.pdf)，§1、印刷pp.27–29，p.28式(1)–(2)；§2 p.30 | 在每个保留支持下计算Gaussian条件均值，再按全部支持样本频率平均。这里相同支持可合并计算；不能用平均活动或平均协方差后求逆代替。原文指定条件下的效率结论不外推为所有分块都更快混合。 |
| multiple chains；within-chain / between-chain information / 多链；链内与链间信息 | [Vehtari等，作者公开版](https://sites.stat.columbia.edu/gelman/research/published/rhat.pdf)，所读28页作者版首页标记2020，§1.1 pp.1–3、§2 pp.5–6 | 借用多链比较的动机。实际记录的是显式定义的边际范围、半链差、转移次数；未实现R-hat/ESS，不以≤0.05或零方差链宣称全局收敛。 |

具体模型与来源（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/activity_posterior_20261015/SOURCES.md`）、
独立数学审查（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/activity_posterior_20261015/MATH_AUDIT.md`）和
完整结果（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/activity_posterior_20261015/REPORT.md`）分别保存推导、术语边界和数值证据。
`activity_posterior_20261015`仅为实验目录名；本控制没有替换原Proposed或恢复score训练。

## 活动后验的局部提议与因子消息（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| informed proposals；balancing function；Barker choice / 利用目标分布的提议；平衡函数；Barker选择 | [Zanella，作者稿v1](https://arxiv.org/pdf/1711.07424v1)，§2.2 p.4式(2)–(4)，p.8 Table1与§4.1式(11)；期刊正式出版为JASA 115(530)，2020 | 实际核对v1的式号和页码。使用g(t)=sqrt(t)和g(t)=t/(1+t)作为提议权重，另作MH接受校正；后者不是Barker接受规则。单比特与活动交换的变度数图、0.1停留、归一化及非降邻边下界均为项目显式推导，未命名为新方法，不外推原文渐近最优性或全局混合保证。 |
| factor graph；sum-product；factor-to-variable message；clustering / 因子图；和积算法；因子到变量的消息；聚类 | [Kschischang–Frey–Loeliger，TIT 2001](https://www.mit.edu/~6.454/www_fall_2002/lizhong/factorgraph.pdf)，§II-C p.502式(5)–(6)，§V p.510，§VI-A p.513 | 标准边消息是单个目标变量的函数；本项目导出L=logit(p)−logit(实际输入ρ)。多个因子共享用户形成环时，正确单边相除不保证全局精确。保留联合活动的模块间传递与独立边际乘积必须区分；固定Gaussian反例仅用于核验。 |
| expectation propagation；moment matching / 期望传播；矩匹配 | [Minka，UAI 2001修订作者PDF](https://tminka.github.io/papers/ep/minka-ep-uai.pdf)，§2式(4)–(6)、§3式(8)–(10)，算法3(b)–3(d)，PDF pp.2–3 | 移除旧因子近似、乘真实因子、匹配矩、除去输入贡献；Gaussian自然参数相减按项目实坐标约定推导。程序仅核验恒等式，未完成新的物理接收机或score模块适配。 |
| cavity distribution；tilted distribution；site approximation；improper / cavity分布；tilted分布；因子近似；不能单独归一为概率分布 | [Vehtari等，JMLR 21(17)，2020](https://www.jmlr.org/papers/volume21/18-817/18-817.pdf)，§2.1 pp.5–6，§5.3 pp.18–19；阻尼讨论见§5.2 pp.17–18 | 使用原词避免把不同概率对象统称噪声。负Gaussian site精度不必导致总体分布不正常，但不能直接转成正AWGN方差；更新需要的cavity与匹配后分布须proper。本文献的阻尼讨论不当作当前AFDM收敛保证，本轮未新增阻尼实现。 |

完整消息推导（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/activity_posterior_refinement_20261015/MESSAGE_DERIVATION.md`）、
提议来源与直接证明（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/activity_posterior_refinement_20261015/SOURCES.md`）及
结果报告（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/activity_posterior_refinement_20261015/REPORT.md`）分别保存公式、适用条件和数值证据。
平方根提议在全一初态的失败是本项目观测；不误引Zanella §6.2针对g(t)=t的描述来证明该失败。

## AWGN参考递推与算子替换（2026-10-15）

沿用前述VAMP、OAMP-MMV、Haar矩阵、阻尼和状态演化术语，不新增方法名称。
本轮标量解析参考依据 [Rangan–Schniter–Fletcher，TIT 2019](https://phil-schniter.web.app/pdf/tit19_vamp.pdf)
Algorithm 3、§IV-A Theorem 1、§IV-E式(54)–(55)；矩阵/重复测量的边界依据
[Cheng等v1](https://arxiv.org/html/2304.08038v1) §III-B式(14)–(18)、Assumption18、Theorem19和§III-F。
双向算术阻尼沿用Cai §V-B1式(57)–(58)，不声称它自动包含
[Takeuchi](https://arxiv.org/html/2111.05522v2) §IV-B式(63)–(78)的历史协方差。

复Bernoulli–Gaussian混合后验、完整实Jacobian迹除以两倍复坐标数，以及
nu→0时迹归一化LMMSE极限W=nAᴴ/tr(AᴴA)、v=nσ²/tr(AᴴA)为显式代数计算；
以密度归一化、有限差分、直接矩阵解及小正nu极限独立核对。
零活动概率下的alpha=0允许通过，不人为添加方差地板，原先过严中断与修正后整组重跑均保留。

实验协议（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/awgn_reference_ladder_20261015/PROTOCOL.md`）区分解析控制、
真实信道下的人工算子、真相位oracle与原估计相位。随机化基础A的右子空间不等于
把完整A⊗I变成右酉不变矩阵。只有误差功率或四阶统计吻合不构成完整AWGN证明。
本轮未实现完整OAMP-MMV/LM-OAMP、未训练网络，性能和统计证据见
报告（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/awgn_reference_ladder_20261015/REPORT.md`）。

## 完整物理信道有限先验的Gaussian EP实现（2026-10-15）

本节更新前述因子消息条目的实施状态，不另立算法名称。

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| moment matching；cavity distribution；tilted distribution；site approximation / 矩匹配；cavity分布；tilted分布；因子近似 | [Minka，UAI 2001修订作者PDF](https://tminka.github.io/papers/ep/minka-ep-uai.pdf)，§2式(4)–(6)、§3式(8)–(10)、算法3(b)–3(d)，PDF pp.2–3；[Vehtari等，JMLR 2020](https://www.jmlr.org/papers/volume21/18-817/18-817.pdf)，§2.1 pp.5–6 | 已实现单个不可变Gaussian观测因子与逐用户可替换Gaussian sites；真实有限先验乘cavity后精确求矩。原子分布对连续Gaussian的通常KL不是有限值，本控制直接定义矩匹配，不宣称有限KL投影最优。 |
| damping；natural parameters；improper site / 阻尼；自然参数；不能单独归一化的site | 同上Vehtari，§5.2 pp.17–18，§5.3 pp.18–19，Appendix A | 已实现自然参数β=.5阻尼及最多12次减半回溯，允许负site精度；1e12条件数上限是本实验数值策略，不是proper的数学定义，也不保证AFDM收敛。该实现阶段不同于前述仅做恒等式审查阶段。 |
| Schur complement；marginalization / Schur补；边缘化 | [Walter–Eustice–Leonard，Exactly Sparse Extended Information Filters for Feature-Based SLAM，作者PDF](https://ttic.edu/ripl/assets/publications/walter07.pdf)，§II-A Table I，PDF p.4；§III-B2式(10a)–(10b)，PDF p.8 | 原文直接列出Gaussian信息矩阵和信息向量边缘化的Schur公式；本项目具体块积分见推导(P27)–(P28)。已另存数值计算修订，不把它称为新AMP算法，不将SLAM结论外推为本控制收敛。自身site不进入自己的cavity，其他用户site仍保留。 |

完整来源、S1/S2条件信息、实支撑表示及Gaussian查询成立条件见
物理因子推导（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/physical_message_20261015/PHYSICAL_DERIVATION.md`）。
有限先验、SVD支撑和条件数只是明确的模型与运算说明；未包装成既有论文中的方法名称。
本次query对角/各向同性近似在实SVD支撑坐标中，不能称为物理beam covariance验证。
原始相减缺陷和修订后仍有的Gaussian近似误差分别记录于
结果报告（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/physical_message_20261015/REPORT.md`）。

## 接收噪声方差学习（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Learning Hyperparameters；expectation-maximization / 超参数学习；期望最大化 | [Shen等，作者稿v1](https://arxiv.org/html/2412.20806v1#S3.SS3)，§III-C式(55)–(56)，Algorithm 1第5–6、21行 | 原文同时学习相位和接收噪声方差。式(56)使用无噪声接收信号的后验均值与方差；Proposed 的相位适配仍保留已知噪声，五基线的后续实现见“基线噪声估计实施”条目。 |
| EM Update of the Gaussian Noise Variance / Gaussian噪声方差的EM更新 | [Vila–Schniter，TSP 2013作者全文](https://phil-schniter.web.app/pdf/tsp13_emgm.pdf)，§III-A式(22)–(27)，p.4661（PDF p.4） | 后验期望残差包含均值残差和方差项。不能把一次拟合的残差能量直接解释为纯接收噪声，尤其在相位、信道或字典存在失配时。近似后验下的应用不自动获得精确EM的保证。 |

令z为无噪声接收信号、N_obs为复观测标量数，相应复Gaussian模型的操作写为
σ²_new = N_obs⁻¹ Σ_i (|y_i − E[z_i\|Y]|² + Var[z_i\|Y])。
均值和方差须来自同一轮观测后验；其中Var按E|z−Ez|²定义。

改动前代码核查：`experiment/generate.py`把生成噪声使用的准确方差写入公开输入。
Proposed、GNN-ASPL、off-grid SBL固定使用该值，SOMP用它设停止阈值；前三个baseline及off-grid SBL的SNR门限选择也依赖它。
GAMP-SBL虽更新噪声精度，其Gamma先验的rate仍由该值设置，因此仍利用准确噪声信息。
当前L-DAMP由校正残差估计等效误差协方差，使用固定活动能量门限，推断不使用该输入方差；相位前端仅用它记录归一化残差诊断。
等效迭代误差协方差和物理接收噪声方差须分别说明。本次记录为实现核查及公式依据。

## Cai 框架内逐项放宽近似（2026-10-15）

沿用上表 turbo message passing、Gaussian projection、extrinsic message、
second-order score matching 等术语。Cai v2 §III 首段明确结合 sum-product rule 与 EP algorithm；
方差共享见 §III-A 式(7)–(11)、§III-B 式(23)、(38)，score 方差读出为 §V-A 式(56)。
本次仅将跨用户二阶读数的平均延后到活动混合矩之后，差值
mean(p_k τ_k)−mean(p_k)mean(τ_k) 是项目联合矩的直接代数结果，
不作为新方法名称，也不宣称有限 second 读数已是精确后验方差。
来源定位补充见 SOURCE_NOTES（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_cai_relaxation_20261015/SOURCE_NOTES.md`），
近似与既有证据见 [PROPOSED_APPROXIMATIONS](https://github.com/RESET-cpu/afdm-gfra/blob/416a4dd4bd219dd9fb5049294bc02f4854f472f4/paper/STMP/docs/PROPOSED_APPROXIMATIONS.md)。

第二项沿用已登记的block uniform diagonalization（Fletcher等GEC，§II-A式(8)–(9)、
§II-B Algorithm 1，PDF pp.2–3），每用户一个Gaussian协方差标量。
复数MMV的分块平均迹、查询及外信息公式为项目推导，见
STEP2_PLAN（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_cai_relaxation_20261015/STEP2_PLAN.md`）；
不将有限score网络、site裁剪/复用或本AFDM算子归入原文保证。
当前估计相位两个预选困难条件未见AER下降，见
第二项结果（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_cai_relaxation_20261015/step2/REPORT.md`）。

第三项继续沿用Gaussian site、cavity distribution、moment matching及Bernoulli–Gaussian
等已登记术语。因子相除依据Minka §3式(8)–(10)、算法3(b)–3(d)，PDF p.3；
标量线性投影及活动证据定位为Cai v2 §III-A式(7)–(11)、§III-B式(24)–(30)。
将原混合矩表示成条件Gaussian密度，再以单用户矩阵似然替换原标量因子的末端处理，
是STEP3_PLAN（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_cai_relaxation_20261015/STEP3_PLAN.md`）中的项目推导。
本地相除不等于消除全局历史信息重复，工作因子的对数权重比不称为新的物理活动先验。
该候选未降低当前困难面板AER；不为此操作新造方法名称。

第四项使用sum-product algorithm（和积算法）及clustering（聚类），来源为
[Kschischang–Frey–Loeliger，IEEE TIT 2001](https://www.mit.edu/~6.454/www_fall_2002/lizhong/factorgraph.pdf)，
§II-C式(5)–(6)，p.502，以及§VI-A，p.513。这里仅保留一对用户的离散活动并求和，
不是实现完整junction tree，也不保证重叠局部边际是全局精确后验。
Gaussian因子相除沿用上述Minka定位，复MMV四状态Gaussian积分及全方差展开见
STEP4_PLAN（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_cai_relaxation_20261015/STEP4_PLAN.md`）。
伙伴选择分数为项目提出的活动混合均值不确定性传播能量，不作为已有论文的方法名。
这一候选未降低预选困难面板AER；具体有限范围见
第四项结果（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_cai_relaxation_20261015/step4/REPORT.md`）。

第五项沿用前文power posterior、thermodynamic integration、marginal likelihood及log Bayes factor。
来源为[Friel–Pettitt作者稿](https://www2.stat.duke.edu/~scs/Courses/Stat376/Papers/NormConstants/FrielPettitPath05.pdf)，
§3式(4)–(5)、§3.1式(6)，PDF pp.4–6；[Friel–Hurn–Wyse v2](https://arxiv.org/html/1209.3198v2#S2)，§2式(6)–(11)。
第五项复数条件矩积分、有限噪声支持起点项及旧网络代入见
STEP5_PLAN（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_cai_relaxation_20261015/STEP5_PLAN.md`）。数学恒等式不等于有限网络近似已正确；
该候选的负方差、先验积分集中及求积误差均未通过，未接入原Proposed。

| 原词或忠实译名 | 原文定位 | 本次使用范围 |
|---|---|---|
| effective sample size / 有效样本量 | [Elvira–Martino–Robert v2](https://arxiv.org/pdf/1809.04129v2)，§1式(1)、§2.2式(7)，PDF pp.2、4；限制见§3.2–3.3 | (Σw)²/Σw²仅报告先验积分权重集中程度，不把该近似当作独立样本数或精度保证。 |
| delta method / delta方法 | 同文Appendix A式(43)–(46)，PDF pp.23–24 | 对log均值作一阶方差传播，先对同场景4个样本分组；SE≈s_group/(sqrt(G) mean_group)是项目代入，不作严格有限样本区间或稀有事件保证。 |

## 原Proposed用户块矩阵消息核查（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用范围 |
|---|---|---|
| shared scalar variance；extrinsic message / 共享标量方差；外信息消息 | [Cai v2](https://arxiv.org/html/2506.00581v2#S3.SS1)，§III-A式(7)–(11)；§III-B式(37)–(42) | 核查当前线性后验先压缩协方差、再相除输入消息的操作；未声称原实现没有外信息。 |
| natural parameters；precision matrix；precision mean / 自然参数；精度矩阵；精度加权均值 | [Vehtari等，JMLR 2020](https://www.jmlr.org/papers/volume21/18-817/18-817.pdf)，§2.1 p.6、§5.3 p.18、Appendix A.1–A.2 p.32 | 复Gaussian因子写成exp(2 Re tr(BᴴX)−tr(XᴴJX))，以(J,B)保留用户内矩阵信息，避免显式J⁻¹。半正定J可以只定义似然因子，不要求其在X上单独归一化；不把数值换表示称为信息增加或噪声消除。 |
| moment matching / 矩匹配 | [Minka UAI 2001修订作者稿](https://tminka.github.io/papers/ep/minka-ep-uai.pdf)，§2式(4)–(6)、§3式(8)–(10)，PDF pp.2–3 | 在固定矩阵输入下，将输出限制为共同标量精度α，匹配各用户均值及全局平均二阶矩。期望负对数Gaussian密度的推导见MATRIX_MESSAGE_DESIGN (M3)；含原子/低维先验时不宣称有限KL投影。 |

自然参数形式、复MMV用户块积分、共同α的标量求根及各向同性退化均为
项目显式推导（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_cai_relaxation_20261015/MATRIX_MESSAGE_DESIGN.md`），
不是以上论文对AFDM的已有完整算法或性能保证。消息核查阶段只完成内核和数学核验；
后续矩阵条件非线性模块、阻尼及全接收机对比见闭环初筛（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_cai_relaxation_20261015/matrix_receiver/REPORT.md`）。

## 基线噪声估计实施（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| stopping criterion / 停止准则 | [Tropp–Gilbert–Strauss 作者稿](https://tropp.caltech.edu/papers/TGS05-Algorithms-Simultaneous-I-preprint.pdf)，§3.1 Algorithm 3.1 | SOMP 原文把停止准则作为输入，没有给出独立噪声估计。当前残差阈值使用下述空间噪声估计，是明确的项目适配。 |
| Gamma prior；EM / Gamma 先验；期望最大化 | Zhang 2023 原文（历史路径，见迁移记录：`reference/zhang2023_gamp_sbl_grant_free_noma.pdf`），式(17)–(19)、Algorithm 1 | 噪声精度采用含输出后验方差的 MAP 更新；复 MMV 计数为 LM+c−1。当前 c=1+LM、d=LMσ̂²_spatial，沿用既有项目先验强度并以空间噪声估计设置尺度；数值强度不是原文给定值，同一观测提供尺度和似然，不是独立额外信息。弱先验首版的低估结果保存在历史报告。 |
| sparsity pattern learning / 稀疏模式学习 | Ding 2026 原文（仅本地历史资料：`reference/literature/ding2026.pdf`），式(12)–(13)、(19)、(26) | 原文更新稀疏概率，不提供物理噪声更新式。当前 GNN-ASPL 保留网络，用空间噪声估计代入 σ²；不将补充前端称为 Ding 原算法的一步。 |
| noise precision / 噪声精度 | [Wei 2022 作者稿](https://arxiv.org/html/2101.05629v1)，式(45)–(46)、Algorithm 1、§VI-A | 共享 MMV 推广保留 M tr(AΣAᴴ)；初始化 mean|Y|²/100。原文 c=d=1e−4；当前 c=1+LM、d=LMσ̂²_spatial 是抑制弱先验持续低估的项目适配，同一观测提供尺度和似然，不是独立额外数据。噪声、行方差和偏移使用同一轮后验。先前固定噪声版本仍作为显式参考。 |
| equivalent noise variance / 等效噪声方差 | [He 2018 作者稿](https://arxiv.org/pdf/1802.01290v2)，§III-A 式(4)–(6)及式(5)后定义 | 原文 σ̂=‖z‖₂/√K，由校正残差估计。当前复数矩阵 L-DAMP 沿用残差协方差；归一化等效误差和物理噪声分开记录。 |
| minimum description length (MDL)；sample covariance matrix / 最小描述长度；样本协方差矩阵 | [Nadakuditi–Edelman，TSP 2008 作者全文](https://math.mit.edu/~edelman/publications/sample_eigenvalue.pdf)，§II-A 式(5)–(7)及尾部均值定义，期刊 pp.2626–2627，重述 Wax–Kailath 1985，DOI 10.1109/TASSP.1985.1164557 | 用 MDL 选空间信号秩，尾部特征值均值给出白噪声拟合值。未实现 Nadakuditi–Edelman 随后提出的新估计器。该空间秩不是活动人数，不使用真实活动数。 |

具体公式、公开输入边界及门限复用范围见 [BASELINE_NOISE.md](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/BASELINE_NOISE.md)。
SOMP/GNN-ASPL 的补充前端依赖低秩空间信号与白噪声模型；当前样本相关性与可能的模型失配不满足任意场景下的一致性保证。
GAMP/SBL 的近似模型可能吸收未建模信号或噪声，学习方差不能未经验证就当作真实热噪声。

## 当前 Proposed 与 Cai 逐式核查补充（2026-10-15）

本次沿用上文登记的术语；完整推导、适用条件、实现对应与 Cai 式(1)–(66)覆盖表见
逐式核查报告（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_cai_equation_audit_20261015/REPORT.md`）。
以下原文定位同时核对了正式 PDF 页面与 arXiv v2，不将项目推导包装成原文定理。

| 原词或忠实译名 | 原文定位 | 本次核查与使用边界 |
|---|---|---|
| posterior variance / 后验方差 | Cai 正式版（历史路径，见迁移记录：`reference/cai2026_score_based_jadce.pdf`），§III-B1 式(19)、(23)，PDF pp.6–7，印刷页3580–3581；[v2](https://arxiv.org/html/2506.00581v2#S3.SS2) | 式(19)印刷的pri中心与式(23)的条件中心方差不一致；按post中心解释才能对应。报告M15给出Gaussian反例；未得到作者勘误确认，不推断其代码照用了错误中心。 |
| second-order score matching / 二阶得分匹配 | 同文 §IV-C 式(50)–(54)、§V-A 式(56)，PDF p.9，印刷页3583 | 有限一阶网络下，总迹目标读出条件MSE，等于中心方差加均值偏差平方；这一限制同时适用于Cai与当前代码。总迹监督单独不识别逐天线子迹；报告M24–M26及零和扰动检查。 |
| channel power normalization / 信道功率归一化 | 同文 §V-B2 式(59)–(65)，PDF p.10，印刷页3584 | 式(59)按字面不是逐样本恒等式；报告M43–M44推导无偏功率估计及条件方差。式(60)逐用户尺度与式(61)共同噪声标签还包含共享近似。当前采用固定尺度，不直接采用该组功率估计。 |
| damping / 阻尼 | 同文 §V-B1 式(57)–(58)，PDF pp.9–10，印刷页3583–3584 | 当前均值和协方差分别算术插值，与作者代码的递归实现类型一致；不将其称为Gaussian分布混合的矩匹配或收敛证明。 |

观测矩阵适用性补充：[Cai §II-A式(3)–(4)、§V-C式(66)](https://arxiv.org/html/2506.00581v2#S5.SS3)
中的 partial orthogonal / 部分正交，指全局行Gram为标量阵，不能与单用户列块内部正交混同。
作者DFT实现的C_kᴴC_k=T P_tx I、单位自身响应和用户内白热噪声是根据原矩阵结构直接推导的性质，
并非任意部分正交矩阵都成立的新定理。当前AFDM的相应差异、实际矩阵检查及有限场景证据见
近似适用性补充报告（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_cai_equation_audit_20261015/APPROXIMATION_ASSESSMENT.md`）。
伪AWGN和右旋转不变条件沿用本文件已登记的Cai §V-B1及Fletcher等JSTAT 2019 §3–4、Theorem 1；
不把局部热噪声白化或平均方差匹配等同于实际完整查询服从独立AWGN。

矩阵消息的闭环初筛沿用以上 Gaussian、natural parameters、moment matching、damping、
conditional mean 和 posterior variance 术语。一般矩阵输入下的均值网络输出按条件均值回归解释；
有限均值网络下的条件均方误差仍包含均值偏差平方，参见上表Cai式(50)–(54)及项目推导。
均衡分类器logit与密度比的对应依据
[Menon–Ong](https://proceedings.mlr.press/v48/menon16.pdf)，§2.2、§3、§4.2式(6)–(8)、(16)–(17)，pp.305–306。
输入变换、矩阵阻尼等价式及正风险损失均明确写为本项目适配（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_cai_relaxation_20261015/matrix_receiver/PROTOCOL.md`），
不赋予新的已有算法名称；该小预算适配不能单独证明后验矩精确或物理迭代的Gaussian假设成立。


## 专利技术补充中的相位优化求解器（2026-10-15）

| 术语 | 原文定位 | 本项目使用范围 |
|---|---|---|
| L-BFGS-B；bound constrained optimization / 带边界约束的优化 | [Byrd等作者稿](https://users.iems.northwestern.edu/~nocedal/PDFfiles/limited.pdf)，§1式(1.1)–(1.2)，PDF p.1；[Zhu等L-BFGS-B作者稿](https://users.iems.northwestern.edu/~nocedal/PDFfiles/lbfgsb.pdf)，摘要，PDF p.1 | `algorithm/phase_estimation.py` 的 `refine` 使用解析梯度与时延、Doppler边界进行局部细化，每候选最多25次迭代。变量投影依据沿用本文件O’Leary–Rust条目；不将数值局部解解释为全局最优或相位真值。 |

## 实际查询分布与局部因子核查（2026-10-16）

| 原词或忠实译名 | 原文定位 | 本次使用边界 |
|---|---|---|
| IID Gaussian / 独立同分布Gaussian | [Ma–Ping, Orthogonal AMP](https://arxiv.org/html/1602.06509v3)，§III-E Assumptions 1–2，§III-D式(21) | Assumption 1要求线性输出误差为IID零均值Gaussian且独立于信号；Assumption 2要求非线性输出误差IID且独立于矩阵和观测噪声，没有额外要求其Gaussian。本次分别检查方向投影、轴向二阶矩与其他用户分量交叉项，不以边缘四阶矩代替独立性。 |
| moment matching；Expectation Propagation / 矩匹配；期望传播 | [Minka, UAI 2001](https://tminka.github.io/papers/ep/minka-ep-uai.pdf)，§2式(4)–(6)、§3式(8)–(10)，PDF pp.2–3 | 局部乘积、投影与因子相除必须针对同一个概率对象；实际轨迹上的监督条件矩不能未经重新推导便替换Gaussian工作因子的局部矩。本项目反例是概率代数检查，不是文献提出的新方法。 |
| conditional mean；posterior variance / 条件均值；后验方差 | [Cai v2](https://arxiv.org/html/2506.00581v2)，§III-B、§IV式(43)–(54)；前述逐式核查条目 | 精确AWGN条件矩对每个给定查询定义先验乘Gaussian因子的局部矩，不要求算法实际生成查询的机制就是AWGN；有限均值网络的条件MSE包含均值偏差平方。此区别不能为实际查询的独立Gaussian假设背书。 |

实验中的单位圆相位重抽和Gaussian系数重抽均按公式直接描述，属于使用真值的离线对照，
不是可部署接收机或已有算法名称。结论及失败候选见
分布核验报告（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_query_distribution_20261015/REPORT.md`）与
数学接口复审（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_query_distribution_20261015/MATHEMATICAL_INTERFACE_REVIEW.md`）。

## 保留活动混合的局部消息核验（2026-10-16）

Gaussian mixture / Gaussian混合、moment matching / 矩匹配、normalizing factor / 归一化因子
依据[Minka UAI 2001](https://tminka.github.io/papers/ep/minka-ep-uai.pdf)，§2式(4)–(7)、§3式(8)–(10)，PDF pp.2–3。
本轮有限分量积分、自然参数凸目标及正标量精度边界是
项目显式推导（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_mixture_message_20261016/DERIVATION.md`）。
矩匹配只覆盖均值和协方差迹，不等于全协方差匹配或完整后验精确恢复。
局部负site精度只在乘积可积域内作约束诊断，不能直接解释为原接收机可接受的负方差输入。

Barker balancing function / Barker平衡函数沿用本文件已有Zanella v1 §2.2式(2)–(4)、Table 1来源，
及已核验实现说明（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/activity_posterior_refinement_20261015/REPORT.md`）；保留MH接受步骤。
本轮把目标权重扩展为固定非零均值、逐用户方差的Gaussian混合因子，明确为本项目适配，
不把数据依赖拟合模型或有限链诊断称为真实物理后验精确解。

## 密度比与条件矩的导数关系（2026-10-16）

conditional mean / 条件均值、posterior covariance / 后验协方差及Tweedie公式继续沿用Cai §IV式(43)–(54)。
Gaussian局部因子下条件均值Jacobian的symmetric positive semi-definite / 对称半正定性质，
另核对[Gribonval–Nikolova v3](https://arxiv.org/pdf/1807.04021v3)，§2.5 Lemma 5，PDF p.15，
Appendix A.4，p.21。对称半正定是必要关系；不能把任意凸势函数都宣称为某个固定先验的Gaussian卷积。

denoising likelihood score matching / 去噪似然得分匹配与cross-entropy / 交叉熵的联合目标，
来源为[Chao等ICLR 2022](https://arxiv.org/abs/2203.14206)，§4.1–4.2，PDF pp.6–7，式(8)–(11)、Theorem 1。
本项目利用已知不活动Gaussian密度，直接推导log密度比梯度的条件均值监督目标；
公式见本次推导P6–P8（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_probability_consistency_20261016/DERIVATION.md`）。
该目标不是该文多类条件生成算法的原样移植，尚未完成候选训练或闭环验证。

参考密度采用Gaussian mixture，沿用前述Minka §2–3中的既有术语。
`log(q_1/q_0)=log(q_G/q_0)+log(q_1/q_G)`仅为密度比的恒等分解；
32组训练功率均值的参考构造及稳定求值均按操作和公式直接描述，未赋予新的算法名称。
条件均值与全方差分解见推导P9–P10（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_probability_consistency_20261016/DERIVATION.md`），
参考本身的失败样本及数值核验见开发对照（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_probability_consistency_20261016/reference_density/DEVELOPMENT_CHECK.json`）。

后续使用w(v)=1/(s+v)乘条件均值回归损失，其中s为训练先验的每复坐标二阶矩。
这是同一条件平方风险分解的正权重推论，按公式描述，不称为文献中的新算法或新损失名称；
理想目标不变而有限优化的折中可能变化，见后续候选推导与协议（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_probability_consistency_20261016/WEIGHTED_CANDIDATE_PROTOCOL.md`）。

固定几何下的均匀相位积分按项目公式G1–G8（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_probability_consistency_20261016/CONDITIONAL_GEOMETRY.md`）描述，
不赋予算法名称。相位期望的 I_n/I_0 表达式核对 Zhang 等
[Multidimensional Variational Line Spectra Estimation](https://arxiv.org/html/1912.11759)，§III-A 式(16b)后定义、式(17b)；
特殊函数积分定义补充核对 NIST DLMF §10.32 式(10.32.1)、(10.32.3)。
这里仅使用相位期望恒等式；没有采用该文多维频率的独立投影近似，也没有把固定几何控制称作未知几何接收机。

pseudo-covariance / 伪协方差依据 Neeser–Massey，
[Proper Complex Random Processes with Applications to Information Theory](https://www.isiweb.ee.ethz.ch/papers/arch/fneese-mass-inspec-1993-1.pdf)，
IEEE TIT 1993，§II-A 式(3)–(5)，期刊p.1294（PDF第2页）。
项目G7使用E[(H−μ)(H−μ)^T]，与复协方差E[(H−μ)(H−μ)^H]共同确定实坐标二阶矩；
G8是该定义对单个实投影的直接展开。原噪声圆对称并不自动推出条件后验该矩为零。

QR factorization / QR分解：依据 Demmel–Grigori–Hoemmen–Langou，
[Communication-Optimal Parallel and Sequential QR and LU Factorizations](https://arxiv.org/pdf/0808.2664)，
§1，PDF p.1（QR与Householder QR的术语）；复数矩阵的酉因子及三角求解定义补充核对
[LAPACK Users' Guide, QR Factorization](https://netlib.org/lapack/lug/node40.html)。
20261016几何积分使用普通QR分解[B/sqrt(v);I]=QR，使I+B^HB/v=R^HR；
未采用或宣称实现该文的TSQR/CAQR并行算法。u=Bc时d=BS^-1c为本项目直接代数化简，
不命名为新的既有方法。见docs/history/experiments/proposed_geometry_integral_20261016/DERIVATIVE_QR_PROTOCOL.md。

adaptive importance sampling / 自适应重要性采样、Gaussian mixture / Gaussian混合：
依据Cappé–Douc–Guillin–Marin–Robert，[Adaptive Importance Sampling in General Mixture Classes v4](https://arxiv.org/pdf/0710.4242)，
§2.1 Algorithm 1式(6)–(7)，PDF p.4；§3.1式(14)–(15)，PDF p.8。
本项目用上一轮归一化p/q权重拟合补充分量，保持先验及旧Gaussian分量，并另抽新样本。
多步固定样本EM、两个不同维度部分、协方差特征值下限与放大、0.2/0.4/0.4比例为项目开发设置；
不称原文M-PMC的逐项复现，也不援引其结论保证当前有限样本全局收敛。
公式及样本分工见docs/history/experiments/proposed_adaptive_geometry_20261016/PROTOCOL.md。

delta method / Delta方法用于比值估计的Monte Carlo方差近似：依据
[Elvira–Martino–Robert v2](https://arxiv.org/pdf/1809.04129v2)，§3.1式(10)，PDF p.5，
及Appendix A式(46)，PDF pp.23–24。局部积分均值、log归一化常数和协方差迹的
向量展开见docs/history/experiments/proposed_adaptive_geometry_20261016/MC_ERROR_DERIVATION.md。
这些有限样本误差诊断只条件于固定proposal，不是遗漏后验区域的界或真实接收机误差分布；
不以其替换预先规定的独立重复与前缀稳定性门槛。

一般观测矩阵及有色Gaussian外部因子的扩展见
项目直接推导L1–L6（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_physical_linear_factor_20261016/DERIVATION.md`）。
沿用Gaussian mixture、conditional mean、posterior covariance与QR factorization的上述原词；
相位积分仍依据NIST DLMF §10.32式(10.32.1)、(10.32.3)。
对给定协方差作Cholesky坐标变换只是Gaussian因子的代数计算，
不把它称作实际多用户反馈已独立化或Gaussian化，也不为这一组合另立方法名称。

## 保留 score 的 Gaussian 因子分解（2026-10-16）

| 术语 | 原文依据 | 本项目范围 |
|---|---|---|
| conditional score function；SNIPS / 条件 score 函数；文献算法名 SNIPS | [Kawar–Vaksman–Elad，NeurIPS 2021](https://papers.nips.cc/paper/2021/file/b5c01503041b70d41d80e3dbe31bbd8c-Paper.pdf)，§3.1 式(6)，§3.2 式(7)–(10)，PDF pp.5–6 | 仅借鉴所有观测奇异方向处于小噪声范围时的 Gaussian 噪声耦合。复数矩阵因子、归一化常数、活动混合及均值/方差恢复是 S1–S8（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_score_factor_split_20261016/DERIVATION.md`） 的直接推导；没有实现完整 SNIPS，也没有证明原网络给出精确可积 score。 |


## Proposed 物理噪声输入与方差消息（2026-10-16）

| 原词或忠实译名 | 原文定位 | 本次核查与建议范围 |
|---|---|---|
| AWGN；noise variance / 加性白高斯噪声；噪声方差 | [Cai v2](https://arxiv.org/html/2506.00581v2)，§II-A 式(3)，§III-A 式(7)–(8)，Algorithm 2 第1、5行 | 物理观测噪声 δ₀² 是输入参数；Algorithm 2 没有其估计步骤。[作者代码固定版本](https://github.com/chang-cai/score-massive-connectivity/blob/0c75680c966dcb8e46250de146f4c27e9294c283/main_stmp_jadce.py#L130-L139) 同样使用输入的 self.delta²。 |
| pseudo AWGN observation model；posterior variance / 等效 AWGN 观测模型；后验方差 | 同文 §III-B1 式(20)，§IV-A 式(44)–(45)，§V-A 式(55)–(56)，§V-B1 | TMP 产生的去噪输入方差及 score 网络恢复的后验方差均与物理噪声参数不同；更新前两者不表示已估计接收端噪声。 |

建议复用上文已登记的 Wax–Kailath MDL 空间协方差前端，将尾部特征值均值作为
Proposed 的物理噪声输入，归一化线性模块使用 σ̂²/s²，原迭代方差公式继续使用。
这项接收机适配尚未实施；它依赖低秩空间信号与白噪声模型，不称为 Cai 的噪声估计方法。
原论文及实现位置、已有 baseline 的噪声比值统计和验证范围保存在
NOISE_REVIEW.json（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_1000_20261016/NOISE_REVIEW.json`）。

2026-10-17 实施记录：上述适配已作为独立候选实现于
`src/afdm_jadcedd/algorithm/proposed_noise_candidate.py`，复用现有 MDL 估计器。
将 Q×N 个接收样本按天线维堆叠，令样本协方差的特征值降序为
λ₁≥⋯≥λ_M；MDL 所选空间信号秩为 r 时，使用
σ̂²=(λ_{r+1}+⋯+λ_M)/(M−r)。这是一次观测噪声方差估计，不是迭代更新物理噪声，
也不是重新训练三网络。低秩空间信号和空间白噪声是适用假设；有限样本、信号泄漏
及 MDL 秩选择可能造成偏差。真实性能验证及是否采用的记录位于
`docs/history/results/phase_optimization_20261017/noise_development`、`noise_fresh` 和
`NOISE_DECISION.json`；后两项在独立验证完成后生成。

## 保留矩阵因子的局部 Langevin 核对（2026-10-16）

| 原词或忠实译名 | 原文定位 | 本项目范围 |
|---|---|---|
| Langevin dynamics；unadjusted Langevin algorithm (ULA)；Ornstein–Uhlenbeck / Langevin动力学；未调整Langevin算法；Ornstein–Uhlenbeck过程 | [Wibisono, COLT 2018](https://proceedings.mlr.press/v75/wibisono18a/wibisono18a.pdf)，§2.1式(4)、Example 1，§2.2式(5)、Example 2，PDF p.4 | 局部推断规格（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_score_factor_split_20261016/LOCAL_INFERENCE_PROTOCOL.md`）将固定矩阵换元后写成复数更新，噪声系数和离散Gaussian协方差直接推导。原文明确ULA有限步长存在偏差；其强凸等条件没有在本有限三网络向量场上得到验证，不引用为收敛保证。 |

“保留矩阵因子”是操作描述：保留一个用户内16×16精度矩阵J，而不是压缩为标量单位阵。
它不是全体用户的精确联合精度，也不意味着外部Gaussian消息已经消除真实用户反馈依赖。

同一Wibisono文献§2.1 Example 1（PDF p.4）给出Ornstein–Uhlenbeck过程的精确Gaussian转移。
E1–E2（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_score_factor_split_20261016/GAUSSIAN_LINEAR_PROTOCOL.md`）
固定每步的网络非线性项后使用这一线性解；对零活动贡献的Gaussian部分保持精确协方差，
不宣称整个有限神经向量场或非线性目标已得到精确离散化，也不为这一组合另造方法名称。

## 原score提议的接受校正（2026-10-16）

| 原词或忠实译名 | 原文定位 | 本项目范围 |
|---|---|---|
| Metropolis–Hastings；reversibility；test ratio / Metropolis–Hastings、可逆性、检验比值 | [Hastings 1970](https://probability.ca/hastings/hastings.pdf)，§2.2 pp.99–101，式(4)–(8)及连续密度段 | A1–A3（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_score_factor_split_20261016/ACCEPTANCE_PROTOCOL.md`）以原first决定Gaussian提议，用原activity logit定义有限近似密度并计算接受比。可逆性只针对该明确近似密度；不保证分类器校准、first/second条件矩一致或有限时长混合，不冠以新算法名。 |

## 联合观测因子的噪声层级（2026-10-16）

| 原词或忠实译名 | 原文定位 | 本项目范围 |
|---|---|---|
| annealed Langevin dynamics / 退火 Langevin 动力学 | [Song–Ermon 2019 v3](https://arxiv.org/html/1907.05600v3#S4.SS3)，§4.3 Algorithm 1 | 原文按噪声层级递减并按噪声方差缩放步长。本项目的固定规格（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_joint_score_factor_20261016/PILOT_PROTOCOL.md`）同时改变似然强度，使用J1–J6（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_joint_score_factor_20261016/DERIVATION.md`）精确辅助分解及矩阵预条件；这是项目推导，不称为原文算法的直接复现，也不借用其名义保证当前有限网络的收敛。 |

“联合观测因子”仅描述保留 CN(Y;AZ,D) 及所有用户共享残差的操作；不另造算法名。
它去除了逐用户外部反馈的独立 Gaussian 工作近似，但有限网络、离散步长、混合及估计相位的误差仍存在。

| 原词或忠实译名 | 原文定位 | 本项目范围 |
|---|---|---|
| Kullback–Leibler (KL) divergence / Kullback–Leibler 散度 | [Zhang等，NeurIPS 2023](https://papers.neurips.cc/paper_files/paper/2023/file/b5b4d92374323c53c24bbbc8ee0e715c-Paper-Conference.pdf)，§1，PDF p.2，定义及式(1) | 初始化尺度诊断（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_joint_score_factor_20261016/INITIAL_NOISE_PROTOCOL.md`）用同协方差Gaussian的特例，转换到proper complex Gaussian后得到tr(δᴴP⁻¹δ)。只描述两个已指定的初始化条件分布，不是神经目标或真实后验间的散度，也不是满足三角不等式的距离。 |


## 酉导频下保留伙伴活动混合的消息更新（2026-10-16）

沿用既有 Bernoulli–Gaussian、Gaussian mixture、cavity distribution、site approximation、
moment matching 术语；依据 Minka 2001 §2式(4)–(6)、§3式(8)–(10)、Algorithm 3(b)–3(d)，
以及 Vehtari et al., JMLR 2020 §5.2 pp.17–18 的 natural-parameter damping。
来源：[Minka原文](https://tminka.github.io/papers/ep/minka-ep-uai.pdf)、
[Vehtari等原文](https://www.jmlr.org/papers/volume21/18-817/18-817.pdf)。

本轮协议（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_unitary_mixture_20261016/PROTOCOL.md`）在固定酉导频下，
保留一个伙伴的活动两分量，对其余用户作各向同性Gaussian矩近似；每个分量分别调用
冻结三网络，按完整密度常数组合，再对混合cavity乘Gaussian active site匹配条件矩，
并单独匹配活动概率。伙伴选择和至多三维实跨度求解是本项目显式操作，不冠以新算法名。
实际网络二阶风险不据此变成真实中心协方差；有限混合和自然参数阻尼也不构成整体收敛保证。


## 酉导频下完整活动混合矩的单一 Gaussian site 更新（2026-10-16）

沿用 expectation propagation、cavity distribution、tilted distribution、
site approximation、moment matching 的原词；依据
[Minka UAI 2001](https://tminka.github.io/papers/ep/minka-ep-uai.pdf)，
§2式(4)–(6)、§3式(8)–(10)、算法3(b)–(d)，PDF pp.2–3。
自然参数阻尼及非正规site的范围依据
[Vehtari等 JMLR 2020](https://www.jmlr.org/papers/volume21/18-817/18-817.pdf)，
§5.2–5.3，pp.17–19；原文允许非正规site，正site限制是本候选的实现约束。

本轮协议（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_unitary_joint_ep_20261016/PROTOCOL.md`）
每用户只存一个Gaussian site，在固定酉块下精确积分得到当前Gaussian近似的cavity；
将同查询三网络输出组成完整活动混合均值和方差平均迹，再除cavity得到site，
并对自然参数阻尼。采用已有EP因子替换结构，不为这一组合另造方法名称。
“精确”仅限指定Gaussian近似模型的消元与给定矩的相除；有限三网络的条件风险、
证据及均值不因此成为同一原物理先验的精确后验矩，也不获得实际AWGN或收敛保证。
含原子的tilted分布对纯连续Gaussian的通常KL非有限，故这里直接定义矩匹配，
不把该投影称作有限KL最小化最优解。正精度不可行及网络支持外查询分别明确记录。


## 估计物理子空间中的联合线性重拟合（2026-10-16）

沿用 least-squares / 最小二乘的已有术语，依据
[O’Leary–Rust 作者稿](https://www.cs.umd.edu/users/oleary/software/varpro.pdf)，
§1式(2)–(3)、§2式(5)–(7)，PDF pp.2、4–5；2026-10-16再次核对原文。
本轮协议（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_activity_repair_20261016/PROTOCOL.md`）固定观测估计的每用户
原子及两导数张成的三维空间，联合求解线性系数；这只是固定几何后的复数线性问题。
左逆、目标响应与补加Gaussian噪声的协方差恒等式为协议列出的直接代数推导，
不为这一组合另立算法名称。单位响应仅在指定子空间内成立；从同一观测估计几何造成的数据依赖、
真实信道的子空间外分量以及有限网络误差仍须单独验证，不能引用原文作为实际AWGN保证。

## 原导频下联合 Gaussian 线性矩与逐用户平均迹投影（2026-10-16）

expectation consistent (EC) approximation / 期望一致近似，依据
[Opper–Winther, JMLR 2005](https://www.jmlr.org/papers/volume6/opper05a/opper05a.pdf)，
§3式(14)–(18)，PDF pp.6–7（期刊pp.2182–2183）；要求所选矩在两个近似分布间一致。
block uniform diagonalization / 分块均匀对角化，依据
[Fletcher等 arXiv:1602.07795v2](https://arxiv.org/html/1602.07795#S2.SS1)，
§II-A式(8)–(9)、§II-B Algorithm 1及式(12)。§III-A Lemma 1给出固定点一致性，
其收敛条件不用于当前有限网络。2026-10-16核对原文。

本轮规格（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_structured_iteration_20261016/PROTOCOL.md`）采用上述矩形式：
精确计算指定 Gaussian sites 下的联合线性边缘，仅在逐用户网络接口作平均迹投影，再除旧site。
自然参数阻尼沿用上面已登记的EP来源。实际second为有限条件风险读出，此实现不计算完整
Jacobian sensitivity，故不能称为直接实现了满足原文MMSE假设的GEC，亦不继承自由能或收敛保证。
一般非酉用户块下，平均迹投影的自身响应及热噪声非白性均显式保存；未将统一迭代称为精确AWGN恢复。


## 专利交底书术语及变量含义核对（2026-10-16）

核对对象为《一种面向无GNSS辅助卫星接入的联合活动检测与信道估计方法》20261016114905版，修订输出为20261016122331版。下列编号为交底书公式编号。本节记录该稿的对外用语；研究历史中的内部变量名和代码接口继续按原记录理解。

| 核对对象 | 采用的表述及含义 | 文献或实现定位 |
|---|---|---|
| 信道查询、查询方差、公共查询方差 | 线性估计输出处用“外信息均值和方差”；经阻尼传入下一模块后用“去噪模块输入均值R、输入方差v”。原来的“查询”是项目内部叫法，不能当作该论文原词。v是所传递高斯消息的方差参数。 | [Cai等v2](https://arxiv.org/html/2506.00581v2)，Table I的extrinsic mean and variance；§III-A式(9)–(14)；交底书式(14)。 |
| 条件误差方差、共享条件误差方差 | 网络量写为“条件均方误差估计值”；按式(16)平均并设正下限后，将τ用作各终端共用的高斯近似方差。 | Cai §IV-C式(53)–(54)；本项目训练损失（历史路径，见迁移记录：`src/afdm_jadcedd/experiment/training/scores/direct_objectives.py`）的direct_second_loss；[THEORY](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/THEORY.md) T9–T10；交底书式(15)、(16)、(25)。 |
| 空间平均协方差 | 写明沿N²个AFDM输入、输出坐标组合取平均，保留M×M天线间信道误差协方差；属于文中高斯混合近似的矩。 | Cai §III-B3式(32)–(38)给出活动混合矩关系；本项目denoiser（历史路径，见迁移记录：`src/afdm_jadcedd/algorithm/proposed/denoiser.py`）的flat、gram、covariance计算；交底书式(21)。M×M形式及平均轴以本项目公式为准。 |
| 公共反馈方差（原用于bar t_X） | bar t_X称“有效信道平均方差”；γ_out称“返回线性估计的外信息方差”。两者分别位于高斯消息相除之前和之后。 | Cai §III-C式(39)–(42)；交底书式(22)、(23)。 |
| 训练支持区间 | 直接写“训练噪声方差范围”。 | score_matching（历史路径，见迁移记录：`src/afdm_jadcedd/experiment/training/scores/score_matching.py`）的噪声采样；denoiser的noise_support判断。0.001至100为当前实现参数。 |
| 折叠时延 | 实施例直接定义为“以采样点数表示的时延对16取余”；表中称“时延余数”。 | 路径响应（历史路径，见迁移记录：`src/afdm_jadcedd/algorithm/baselines/offgrid/atoms.py`）的path_atom时延定义及相位估计（历史路径，见迁移记录：`src/afdm_jadcedd/algorithm/phase_estimation.py`）的搜索范围。 |
| 物理候选、物理频率、时延—相位峰 | 分别写为候选路径响应、多普勒频率、评分峰值及其对应时延和相位。直接描述搜索对象。 | phase_estimation（历史路径，见迁移记录：`src/afdm_jadcedd/algorithm/phase_estimation.py`）的峰值筛选、频率枚举及连续参数细化；交底书第一步、式(8)–(10)。 |

条件均方误差的判断依据是实际训练目标，而不是另命名一种方差。固定一阶网络后，式(25)在给定带噪输入和噪声方差下拟合该网络估计误差的条件期望。按THEORY T10，条件均方误差等于平均条件协方差迹加上均值估计偏差的平方项；因此将有限网络读出直接称为精确后验方差会遗漏后一项。交底书只需准确说明“估计均方误差，再用于高斯近似方差”的处理关系，不展开研究诊断。

已核实并保留的名称：

| 术语 | 原文位置 | 在交底书中的使用 |
|---|---|---|
| first-order / second-order score network；一阶／二阶得分网络 | Cai §IV-A末段、§IV-B–C式(46)–(54) | 使用完整名称；图中“一阶网络”“二阶网络”为同一对象的简称。 |
| denoising score matching；去噪得分匹配 | Cai §IV-B式(47)–(49) | 对应式(24)，按复噪声每个实分量方差v/2换算。 |
| LMMSE；线性最小均方误差 | Cai §III-A式(6)–(8) | 本稿式(12)、(13)是一般导频矩阵下的高斯线性更新。 |
| damping；阻尼 | Cai §V-B1式(57)–(58) | 当前均值、方差按新值权重0.2插值；该权重为本项目配置。 |
| conditional residual block、refinement block；条件残差块、特征细化模块 | Cai §VI-A2、Table III | 对应本项目network（历史路径，见迁移记录：`src/afdm_jadcedd/algorithm/proposed/network.py`）的条件RefineNet结构；通道数及连续噪声条件为当前实现。 |
| AFDM、DAFT、chirp-periodic prefix；仿射频分复用、离散仿射傅里叶变换、啁啾周期前缀 | [Bemani等2204.12798v2](https://arxiv.org/html/2204.12798v2)，§II-B式(11)–(17)、§III-A式(18)–(19)；交底书[4]的[2104.11331](https://arxiv.org/abs/2104.11331)题名亦已核实 | 保留已有名称；式(2)的多周期前缀及式(5)–(8)的具体算子以项目模型为准。 |
| fractional delay、fractional Doppler；分数时延、分数多普勒 | Huang等原文（历史路径，见迁移记录：`reference/huang2026_prior_agnostic_afdm_diffusion.pdf`），§II式(4)–(5)，p.2950 | 连续时延、多普勒路径响应的来源；当前多用户、多天线观测和参数排列由项目定义。 |
| differential delay、Doppler shift；差分时延、多普勒频移 | [Shen等2412.20806v1](https://arxiv.org/html/2412.20806v1)，§II、§III-C | 场景术语有出处；β=wrap(2πνT_frame)及其观测估计流程由本项目式(8)–(10)定义，跨帧相位仍为未知量。 |
| variable projection；变量投影 | [O’Leary–Rust](https://www.cs.umd.edu/users/oleary/software/varpro.pdf)，§1式(2)–(3)、§2式(5)–(7)，PDF pp.2、4–5 | 固定时延和多普勒后最小二乘求复增益，将其从非线性搜索中消去。 |
| L-BFGS-B | [Zhu等作者稿](https://users.iems.northwestern.edu/~nocedal/PDFfiles/lbfgsb.pdf)，摘要、§1，PDF pp.1–2 | 对应代码中带边界的局部求解器；候选选择规则来自本项目。 |
| density ratio、class-probability estimation；密度比、类别概率估计 | [Menon–Ong](https://proceedings.mlr.press/v48/menon16.pdf)，§3式(6)–(8)、§4.2式(16)–(17)，pp.305–306 | 式(19)的类别先验校正有贝叶斯关系依据；活动分类器是本项目组合。 |

“有效信道X=αH”沿用Cai Table I的定义；“有效导频矩阵”在本稿中由原始导频乘估计跨帧旋转明确给出。完整AFDM信道数组、未知相位搜索与三网络接收机的组合均按项目公式说明，没有将组合另冠为已有算法名称。

背景引文逐项核对：CN108540410B说明书步骤S3–S6为模块间信息交换；CN114900904B步骤一至五为卫星信道模型及MMSE-AMP；CN111865845A的发明内容和具体实施方式为信道估计网络、用户检测网络及联合损失；CN118890069B步骤S2–S3明确结合生成对抗网络、降噪卷积网络和消息传递；CN116132227B步骤2–5为扩散模型训练和采样；CN118740562B步骤A1–A4为扩散模型训练及蒸馏。对应公开文本分别为[CN108540410B](https://patents.google.com/patent/CN108540410B/zh)、[CN114900904B](https://patents.google.com/patent/CN114900904B/zh)、[CN111865845A](https://patents.google.com/patent/CN111865845A/zh)、[CN118890069B](https://patents.google.com/patent/CN118890069B/zh)、[CN116132227B](https://patents.google.com/patent/CN116132227B/zh)、[CN118740562B](https://patents.google.com/patent/CN118740562B/zh)。本稿现有背景概述与这些内容相符。

本轮仅修改交底书表述及出处记录。25个显示公式、相位未知的模型、接收算法配置、冻结实现和既有仿真数据均未变更；没有运行新的性能实验。

## 专利交底书的 score 中文译名（2026-10-16）

本交底书统一采用“分数网络（score network）”“一阶／二阶分数网络（first-order / second-order score network）”和“去噪分数匹配（denoising score matching）”；相关 score learning 表述相应写为“分数学习”。

中文译名依据：管凤旭、张涵宇、路斯棋等，《扩散模型在计算机视觉领域的研究现状》，《智能系统学报》，2025，20(2)：265–282，DOI 10.11992/tis.202312041。[期刊全文](https://html.rhhz.net/tis/html/202312041.htm)第2.3节和第2.3.2节使用“噪声条件分数网络（noise conditional score network）”，第2.3.3节式(8)及其后说明使用“去噪分数匹配（denoising score matching）”。

一阶和二阶的技术含义沿用[Cai等论文v2](https://arxiv.org/html/2506.00581v2)第IV-A节末段、第IV-B至IV-C节式(46)–(54)。此次统一中文译名，公式及网络估计对象沿用上一稿。


## 专利交底书术语复核续（2026-10-16）

核对稿：20261016123942；修订稿：20261016124654。核对正文、公式说明、表格、图中文字、训练说明、实施例及保护点。

### 已调整的表述

| 原表述 | 修订表述或操作说明 | 依据与定位 |
|---|---|---|
| 基于分数学习的生成式AI模型 | 基于分数的生成模型；信道先验由该模型学习 | Cai等，[arXiv:2506.00581v2](https://arxiv.org/html/2506.00581v2)，标题、摘要、第I-B3节及第IV节的score-based generative models。score learning可描述学习过程，此处采用模型本身的名称。 |
| 接收活动先验、活动先验 | 活动先验概率 | Cai第II-A节的Bernoulli活动模型、第III-B2节式(28)–(30)；本稿ρ为概率标量。 |
| 活跃条件均值 | 终端活跃条件下的信道均值 | Cai第III-B3节式(33)–(35)；本稿式(18)与式(21)的条件均值和活动概率加权均值。 |
| 分类值、分类器输出 | 对数几率估计值 | Menon与Ong，[ICML 2016论文](https://proceedings.mlr.press/v48/menon16.pdf)，第2节PDF第2页的logistic loss链接函数Ψ(p)=log[p/(1-p)]，第3节式(6)–(8)的类别概率与密度比关系；实际代码activity.py的forward、auxiliary.py的binary_cross_entropy_with_logits以及denoiser.py的先验校正。该网络输出经校正和sigmoid后才得到本稿活动概率。 |
| 复天线增益 | 各接收天线的复信道增益 | Huang等《Prior-Agnostic AFDM Channel Estimation for High-Mobility LEO Satellite Communications Using Diffusion Models》第II节式(1)、(4)–(5)，p.2950的complex channel coefficient / complex gain；本项目式(9)最小二乘拟合的是信道复增益。 |
| 平均迹 | 协方差矩阵对角元素的平均值 | Cai第III-A节式(8)、第III-B3节式(36)–(38)的迹与维度归一化；本稿式(13)、(22)直接给出分母KN、KM。 |
| 延迟基函数、时延基函数 | 直接说明式(6)的矩阵B_d及其关于时延的可微区间 | 本稿式(5)–(6)与path_atom、delay_bounds实现；Bemani第II-B及III-A节为DAFT和AFDM波形依据。B_d是本项目公式定义的矩阵，无需另立“延迟基函数”名称。 |
| 高斯混合近似下的协方差 | 直接说明天线间信道误差协方差矩阵的近似值及两项来源 | Cai第III-B3节式(32)明确为Bernoulli–Gaussian pdf，式(35)–(38)给出活动加权矩。本稿式(21)保留条件信道误差与活动状态不确定性两项。 |
| 公共输入方差 | 首次说明各信道系数共用的输入方差，后文简称输入方差 | 本稿式(12)–(14)中的标量γ与单位矩阵；只是说明共用范围。 |
| 物理噪声方差、物理幅度尺度、归一化坐标 | 归一化前噪声方差、归一化前的幅度尺度、归一化后的数值 | 本稿归一化步骤为Y/s、σ²/s²；已保存实施例核验记录中的physical_noise_variance、normalized_noise_variance及scale。 |

### 已核对并保留

一阶／二阶分数网络、去噪分数匹配：Cai第IV-A至IV-C节式(43)–(54)；中文译名见管凤旭等《扩散模型在计算机视觉领域的研究现状》第2.3及2.3.3节。

外信息、线性最小均方误差、阻尼：Cai Table I、第III-A节式(6)–(14)、第V-B1节式(57)–(58)。条件均方误差沿用上一轮实际训练目标审计，对应本稿式(15)、(25)。

仿射频分复用、离散仿射傅里叶变换、啁啾周期前缀：[Bemani等](https://arxiv.org/html/2204.12798v2)第II-B节式(11)–(17)、第III-A节式(18)–(19)。

变量投影、最小二乘：[O’Leary–Rust](https://www.cs.umd.edu/users/oleary/software/varpro.pdf)第1节式(2)–(3)、第2节式(5)–(7)。L-BFGS-B：[Zhu等](https://users.iems.northwestern.edu/~nocedal/PDFfiles/lbfgsb.pdf)摘要及第1节。

条件残差块、特征细化模块：Cai第VI-A2节Table III；对应条件RefineNet实现。差分时延、多普勒频移：[Shen等](https://arxiv.org/html/2412.20806v1)第II节及III-C节。漏检、虚警与活动判决错误率：Cai第VI-C节及本稿明确的计数定义。

有效信道、有效导频矩阵、跨帧相位增量均在本稿中有明确公式定义。候选评分是匹配滤波搜索中的相关量，和生成模型的分数函数属于不同对象。两者按各自含义使用。

### 本轮范围

25个显示公式、5张表的数值、2张图、9项参考文献及未知跨帧相位模型沿用上一稿。此次进行术语及公式对象核对，未修改算法实现或重新运行性能仿真。

## 弱用户反馈修复的训练与消息依据（2026-10-16）

本次定向核查见 修复选择报告（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/proposed_repair_literature_20261016/REPORT.md`）。保留既有EP、GEC、OAMP-MMV、LM-OAMP名称及其原适用条件，不把16×16矩阵消息或以下参数化冠以新的文献算法名称。

| 原词或忠实表述 | 原文定位 | 本项目使用边界 |
|---|---|---|
| faithful heteroscedastic regression / 原标题及均值优化保持条件 | [Stirn等，AISTATS 2023](https://proceedings.mlr.press/v206/stirn23a/stirn23a.pdf)，§2 Definition 2、Proposals 1–2、式(5)、Theorem 1，PDF pp.3–4 | 均值用平方误差梯度；协方差NLL的均值和共享特征停止梯度。同优化随机性及等价更新条件下，均值与mean-only基线相符；不保证真实中心后验协方差、EP收敛或本项目检测改善。当前全模型裁剪可能重新耦合分支，需另核对。 |
| stop gradient / 停止梯度 | 同文式(5)之后对括号算子的定义，PDF p.4 | 本候选需同时隔离NLL的均值参数及协方差特征中的first输出；不能只detach损失中的残差。现有activity.inputs已经detach mean，不能把BCE经mean回传列为已存在故障。 |
| derivative of the conditional mean estimator / 条件均值估计器的导数 | [Dytso–Poor–Shamai预印本](https://arxiv.org/pdf/2104.01883)，§III Theorem 1式(19)、§IV Proposition 1式(22)，PDF pp.5–6；正式TIT版本DOI为10.1109/TIT.2022.3216012，式号不同 | 在输出行/输入列Jacobian约定下，独立实Gaussian噪声协方差T给出C=J_m T，m必须是精确条件均值；有限F的J_F T不一定对称正定。不能把旧second的条件风险自动替代此量。 |
| iterative (turbo) soft interference cancellation / 迭代（Turbo）软干扰抵消 | [Wang–Poor，TCOM 1999原文](https://cs.yale.edu/homes/yry/readings/wireless/wireless_readings/article23.pdf)，§IV-B1式(29)–(41)，印刷p.1051；§IV-B2式(47)–(50)，p.1052 | 在已知信道、编码CDMA的软符号检测中排除目标取消项并保留其他符号方差。当前酉导频查询已排除直接自身反馈；原文不证明其他用户估计中不含目标信息，也不保证AFDM网络查询AWGN。 |

报告中的C=s[I+(κ_max−1)BBᴴ/(1+||B||²_F)]是本项目直接定义的有界条件数参数族；其谱界是代数事实，不称为上述论文的参数化。有限均值风险=中心协方差+均值偏差外积也是直接条件期望展开；偏差外积非负，不能据此解释实际风险低估。

## 弱用户场景与功率设定的适用边界（2026-10-16）

| 原词或忠实表述 | 原文定位 | 本项目使用边界 |
|---|---|---|
| power control / 功率控制；statistical channel inversion / 统计信道反演 | [Fengler、Musa、Jung、Caire，Pilot-Based Unsourced Random Access with a Massive MIMO Receiver: Interference Cancellation and Power Control](https://arxiv.org/html/2109.10108)，§II-A，式(5)及随后四种策略定义 | 文中通过下行测量得到大尺度衰落系数，补偿该系数使发射功率与大尺度增益之积一致；小尺度Rayleigh衰落仍保留。支持功率控制作为明确系统假设，不能支持逐实现信道范数恒定或当前AFDM接收机必然改善。当前生成器省略用户相关大尺度幅度因子，进一步消除随机多径造成的能量差属于不同操作。 |

Cai的channel power normalization继续沿用上表条目；§V-B2明确逐训练样本归一化，§VI-A1仍给出35–200 m距离及用户相关路径损耗。§VI-B的单用户去噪对照另明确假定路径损耗完全补偿，不能外推成全部JADCE测试不存在弱用户。

本项目当前实验生成器`experiment/generate.py`以每个场景完整无噪接收信号的实现功率设置热噪声方差。固定总接收SNR、固定预先定义的单用户平均参考功率与噪声之比、逐用户固定实现能量是不同的实验条件；这里按公式描述，不引入新方法名。仅改变图上SNR标记不会改变观测。候选参考功率应独立于测试场景实际活跃数和最弱用户真值预先确定；逐实现等能量可以作为明确标记的诊断，但改变信道先验，不能自动视为已实现的大尺度功率补偿。本次只核对定义与文献，未修改生成器或运行新性能实验。

## 卫星 GFRA 的 SNR 定义及扫描范围核查（2026-10-16）

完整对照见八篇文献核查（历史路径，见迁移记录：`reference/satellite_gfra_snr_20261016/REPORT.md`）。这里的“总接收”仅说明公式分子包含所有活动用户，不作为新方法名称。

| 原词或忠实表述 | 原文定位 | 本项目使用边界 |
|---|---|---|
| signal-to-noise ratio / 信噪比：叠加接收信号功率基准 | [Ding 2026](https://doi.org/10.1109/TVT.2026.3729877)，§IV-B p.5；[Mao 2025](https://arxiv.org/html/2504.04686v2#S4)，§IV；[Zuo 2023](https://arxiv.org/pdf/2210.17355v1#page=25)，§V | Ding原印式为‖SZ‖²_F/(MLσ²)，模型式(9)用Ψ记号；Mao按角域位置累加‖Γg‖²；Zuo按超符号u累加‖G_u x_u‖²，u不是用户。都没有除活动用户数，支持当前总接收SNR作为一种已用口径，不证明作者代码逐实现调噪细节。 |
| signal-to-noise ratio / 信噪比：按卫星及观测窗口定义 | [Shen协作星座2025](https://arxiv.org/html/2408.02586v1#S5)，§V、式(18)–(19)、Fig.4；[Shen大差分时延2025](https://arxiv.org/html/2412.20806v1#S5)，§V、式(19)、Fig.7/9 | 前者每颗卫星的导频窗口；后者各时延块内Q帧全部用户信号。前者AER曲线−6至2 dB，后者−4至4 dB；不能宣称卫星GFRA不研究负SNR。 |
| normalized path power；average symbol energy / 归一化路径功率、平均符号能量 | [Shen GLOBECOM2022](https://arxiv.org/pdf/2208.01828v1#page=5)，§IV；[Xu TCOM](https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/AFDM-aided-Grant-Free-Random-Access-for-LEO/991050765702346)，§V | Shen明示Σ_i|h_ui|²=1、导频方差1/(MN)、SNR=10log10[1/(MNσ²)]；逐路径向量能量约束不等于实际接收能量恒定。Xu采用E_s/N_0且研究给定信道信息下的活动/数据检测，不能直接作为同任务JADCE的总接收SNR对照。 |

范围结论：Ding Fig.3的0、4、8、12、16、20 dB可作为本项目主评估扫描的文献参照。该取值是评估范围选择，不是统一物理下限，也不是功率分布或算法修复。此前单用户参考SNR的建议保留为可选的另一实验，不再表述为纠正当前总接收定义所必需。负SNR既有结果保留，任何新优势须在固定的新配对实验中验证。

2026-10-16 已知噪声条件核对：Cai [v2](https://arxiv.org/html/2506.00581v2) Algorithm 1、Algorithm 2 输入的 δ₀² 是物理热噪声方差；§III-A 式(7)–(8)直接使用它。迭代消息方差 v、τ 与该物理参数区分。[作者代码固定提交](https://github.com/chang-cai/score-massive-connectivity/blob/0c75680c966dcb8e46250de146f4c27e9294c283/main_stmp_jadce.py#L141-L149) 使用生成噪声的同一 delta²，未从观测重新估计该参数。当前原导频八点比较统一供给准确方差，详见 实验协议（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_original_snr8_10_20261016/PROTOCOL.md`）。

## 公共相位前端的计算优化调研（2026-10-17）

本次为定向文献核查，检索范围及建议见调研记录（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/results/phase_frontend_research_20261017/RESEARCH.json`）。未修改冻结算法，未测得优化后的加速比。

| 原词或忠实表述 | 原文定位 | 本项目使用边界 |
|---|---|---|
| variable projection / 变量投影 | [O’Leary–Rust 原文](https://www.cs.umd.edu/users/oleary/software/varpro.pdf)，§1 式(2)–(3)、§2 式(5)–(7) | 当前单路径相位拟合已通过最小二乘消去复增益，具有此结构。可考虑多路径共享用户多普勒、内层解增益，但这是项目扩展建议，不代表精度或全局收敛保证。 |
| Newtonized orthogonal matching pursuit；cyclic refinement / 原文算法名及循环精修 | [Zhu等 MNOMP 原文 v1](https://arxiv.org/html/1802.01266v1)，§III-A 式(5)–(10)、§III-B Algorithm 1、§IV-A | 原文为多快拍线谱估计，也允许已知压缩矩阵。粗检测、局部精修、循环精修和联合增益更新可供借鉴；本项目AFDM时延/多普勒原子需重新推导。第二轮从旧估计局部搜索、必要时回退全面搜索是项目建议，不是原文已证明的预算规则。 |
| posterior expectation phase update / 根据后验期望更新相位的操作描述 | [Shen等原文](https://arxiv.org/html/2412.20806v1)，§III-C 式(47)–(54) | 原文二阶矩目标及单位圆投影不等于本项目跨帧 exp(jqβ) 约束。已有项目改写在低SNR增加过漏检，不能以相位误差降低代替接收性能验证。 |
| stepwise maximum likelihood / 分步最大似然 | [Tang等 AFDM 原文 v1](https://arxiv.org/html/2310.07141v1)，§III 式(5)–(6)、(15)–(20)，§V | 使用时域CPP与对应数据样本的相关性，采用单链路共同频偏模型及粗频偏已补偿的范围条件。当前输入已移除CPP且多用户频偏不同，不能直接替换现有公共前端。 |
| continuous-frequency GLRT / 连续频率广义似然比检验 | [Jiang等 Enhanced MNOMP 预印本](https://arxiv.org/html/2607.17308v1)，§II Algorithm 1、§III-A | 2026年预印本讨论连续搜索与离散网格阈值差异；其虚警率标定不能直接用于本项目AFDM用户/路径字典。 |

去掉未使用的二阶导数、缓存固定DAFT矩阵及批量计算相关性均按实现操作描述，不冠以新算法名称。单个已保存场景的耗时剖析（历史文件已清理，原路径：`results/phase_frontend_research_20261017/PROFILE.json`）含分析器开销，仅定位瓶颈；全部五个输出数组与旧结果逐元素一致，不构成多场景耗时基准或性能改进证据。

2026-10-17 联合活动与相位候选的独立试验：

| 原词或忠实译名 | 原文定位 | 本项目使用范围 |
|---|---|---|
| structured sparsity；structured generalized approximate message passing (S-GAMP) / 结构化稀疏性；结构化广义近似消息传递 | [Sun等作者全文](https://livrepository.liverpool.ac.uk/3141858/1/Massive_Grant-free_OFDMA_with_Timing_and_Frequency_Offsets.pdf)，TWC 2022，DOI 10.1109/TWC.2021.3121066；§II-C 式(18)–(19)，PDF p.6；§III-A 式(20)–(41)，pp.6–9；§IV，pp.10–11 | 借鉴“用户不活跃或只对应一个偏移候选”的联合先验。完整信道块、冻结网络似然比、原公共标量EP反馈为项目适配；不宣称复现S-GAMP。独立候选查询、跨候选协方差投影和H/相位先验分解均显式记录于候选推导（仅本地历史资料：`archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_joint_phase_20261017/ALGORITHM.md`）。 |

## 七项实验新增术语依据（2026-10-18）

- NTN-TDL-A/B/C/D、Tapped Delay Line (TDL)、Rayleigh、Ricean：3GPP TR 38.811 V15.3.0 §6.9.2、表 6.9.2-1～4，印刷 pp.89–90，[原文](https://atisorg.s3.amazonaws.com/archive/3gpp-documents/Rel15/ATIS.3GPP.38.811.V1530.pdf)。`experiment/cross_channel.py` 使用其功率时延表；共同方向/卫星多普勒及分布级总功率匹配是项目的明确设定，不称为完整标准实现。Huang 2026 §IV、Fig.6（p.2952）采用 D 训练及 A/B/C/D 测试。
- 独立信道去噪与训练样本量：Cai §VI Fig.4（denoising performance）；Huang 2026 §IV Fig.4、pp.2952–2953 的 `N_train` 为训练 AFDM 信道矩阵数，不是测试场景数。本项目多个用户信道可能共享一个物理场景，分别报告两种计数。
- 二阶网络的条件 MSE 读出沿用上表 Cai 的二阶 score 术语及本项目 THEORY T8–T11。`predicted / observed MSE` 仅描述总体平均预测与实测误差之比，不引入新的方法名称，也不等同于逐查询条件校准证明。

## 收敛实验的导频类型对照（2026-10-18）

- Hadamard pilot matrix、different measurement matrices / Hadamard 导频矩阵、不同测量矩阵：Cai §VI-C Fig.12（本地排版 p.11）；[原文](https://arxiv.org/html/2506.00581v2#S6.SS3)。该实验固定生成先验，比较 DFT 与 Hadamard 的收敛行为及 NMSE。本项目在 `experiment/convergence.py` 中作相应 AFDM 配对实验，不宣称复现 Cai 的完整系统。
- Paley construction、Sylvester doubling / Paley 构造、Sylvester 倍增：[A database of constructions of Hadamard matrices](https://arxiv.org/html/2411.18897v1#S4)，§4.1 Theorem 1 与 §4.2 Theorem 3。使用 q=19 的二次剩余构造 20 阶矩阵，五次倍增得到 640 阶；行列排列、列符号与抽取部分行保留对应行 Gram 性质。矩阵尺寸与当前 K=40、N=16 一致。
## 2026-10-18：论文第 II–V 章与估计相位、估计噪声主线对齐

本条记录本轮新增或重新核对的术语及原文位置；接收机组合与公式编号属于本项目。

| 术语 | 原文与位置 | 本稿使用范围 |
|---|---|---|
| separable nonlinear least squares；variable projection / 可分离非线性最小二乘；变量投影 | O'Leary–Rust, *Variable Projection for Nonlinear Least Squares Problems*, Computational Optimization and Applications 54, 579–593 (2013), DOI 10.1007/s10589-012-9492-9；[作者稿](https://www.cs.umd.edu/users/oleary/software/varpro.pdf)，§1式(2)–(3)、§2式(5)–(7) | 第 III 章固定时延、Doppler 时最小二乘消去天线复增益。当前主导路径及逐用户搜索是项目适配，不宣称全局最优。 |
| L-BFGS-B；bound-constrained optimization / 带边界约束优化 | Zhu、Byrd、Lu、Nocedal, *Algorithm 778: L-BFGS-B: Fortran Subroutines for Large-Scale Bound-Constrained Optimization*, ACM TOMS 23(4), 550–560 (1997)；[作者书目信息](https://users.iems.northwestern.edu/~nocedal/Abstracts/erice.html)、[作者技术稿](https://users.iems.northwestern.edu/~nocedal/PDFfiles/lbfgsb.pdf)，摘要及§1 | 第 III 章候选时延、Doppler 的局部细化。限制在同一可微时延区间，预算为局部优化器迭代数，不等同于函数求值次数。 |
| minimum description length (MDL)；sample covariance matrix / 最小描述长度；样本协方差矩阵 | Nadakuditi–Edelman, IEEE TSP 56(7), 2625–2638 (2008), DOI 10.1109/TSP.2008.917356；[正式全文](https://math.mit.edu/~edelman/publications/sample_eigenvalue.pdf)，**§II-A式(5)–(7)**及p.2627的几何/算术均值定义 | 引用其中回顾的 Wax–Kailath 方法；使用空间样本协方差特征值选择信号秩，并用尾部均值拟合复噪声方差。不是活动人数估计，也不是该文后续提出的新估计器。此定位更正部分源码注释中的“§I-B”；本轮不修改冻结源码。 |
| pseudo AWGN observation model；extrinsic mean and variance / 等效AWGN观测模型；外信息均值和方差 | [Cai v2](https://arxiv.org/html/2506.00581v2)，Table I、§III-A式(9)–(14)、§III-B式(20)、§V-B1 | 正文将内部“query”表述为去噪模块输入或高斯消息；本稿误差恒等式显式保留估计相位造成的算子误差。 |
| density ratio；class-probability estimation / 密度比；类别概率估计 | [Menon–Ong](https://proceedings.mlr.press/v48/menon16.pdf)，§3式(6)–(8)、§4.2式(16)–(17) | 第 IV 章BCE总体最优目标与活动先验校正；不将有限分类器或失配迭代输入下的概率称为精确后验。 |

## 独立去噪下界（2026-10-18）

- Genie-aided lower bound / 辅助真值信息下界：[Cai v2](https://arxiv.org/html/2506.00581v2#S6.SS2)，§VI-B、Fig.4；本地 `reference/reviews/section_structure_20261009/cai.txt` 第 2099–2103 行明确假设路径功率、时延、角度已知，并对复增益使用 MMSE 估计。本项目采用同类信息辅助比较，但额外公开定模随机相位 LOS 的真实复增益，避免将非高斯先验的 LMMSE 误称 MMSE；同时公开 AFDM 所需多普勒。
- 条件 Gaussian MMSE 的具体表达式及侧信息增加不增大最优平均平方误差的推导见 `experiment/README.md` 的独立去噪段。这是针对现有信道模型的直接条件期望计算，不另造算法名；下界只约束总体平均 MSE，有限样本曲线不具有逐样本保证。

## 论文第 II–V 章及附录 A 术语核对（2026-10-18）

本轮针对当前论文英文正文逐项核对方法名、缩写和自拟复合表达。下表为当前稿用法；上文实验与历史候选的记录保留。详细修改见 核对报告（历史路径，见迁移记录：`paper/checks/terminology_20261018_125231/TERM_AUDIT.md`）。

| 原词、来源与精确位置 | 当前稿处理 |
|---|---|
| turbo message passing (TMP)；Cai §III 标题及首段；score-based turbo message passing (STMP) 见同文 §I-B3，[作者稿](https://arxiv.org/html/2506.00581v2)；本地文本行147、538–550 | 改正此前 score-based turbo message passing (TMP) 的缩写不一致。采用 turbo message passing (TMP) framework；conditional TMP 改为 TMP，固定参数条件仍保留在前句。 |
| Gaussian projection；extrinsic message；Cai §III-A 式(9)–(11)、§III-B 式(17)、(24)–(27)、(32)–(34)，本地文本行612、852、1110 | Gaussian moment projection 统一为原词 Gaussian projection。Gaussian division 改成对条件后验的 Gaussian 近似除以输入似然这一明确操作。 |
| site / site approximation；[Vehtari 等 JMLR 2020](https://www.jmlr.org/papers/volume21/18-817/18-817.pdf)，§2.1，pp.5–6，式(1)及其后定义；§5.3，pp.18–19 | site 不是自造术语。首次出现处解释为信道先验因子的 Gaussian 近似并新增 vehtari2020 引用；保留当前正精度约束和消息复用的项目规则。 |
| Tweedie's formula；second-order Tweedie's formula；Cai §IV-A 式(44)–(45) | 统一用 formula，不再在 identity/formula 间切换。保持实噪声方差 v/2 的约定。 |
| Second-Order Score Matching；Cai §IV-C 式(50)–(54)；[Lu 等 ICML 2022](https://proceedings.mlr.press/v162/lu22f/lu22f.pdf)，§4.2 Corollary 4.2，式(15)，PDF p.5；Appendix F.2 式(138)–(143)，PDF p.22 | IV-B 标题采用 Second-Order Score Matching。higher-order 的泛称缩小为 second-order denoising score matching；trace objective 说明该节采用的迹目标。冻结有限均值估计器时的条件 MSE 含义继续由本稿附录推导，不把各坐标输出宣称为精确 Hessian。 |
| density ratio estimation；class-probability estimation；[Menon–Ong](https://proceedings.mlr.press/v48/menon16.pdf)，§3 式(6)–(8)、§4.2 式(16)–(17)，pp.305–306 | activity density ratio 改为 density ratio for activity detection，说明用途而不另命名一种密度比；训练先验修正由上述 odds 等式直接给出。 |
| logistic loss；Menon–Ong §2.2 p.305；cross entropy：Shen §IV-A2 式(61) | 本稿的 binary cross-entropy (BCE) 是二分类交叉熵，未自造缩写。以 y=2a−1 代入 logistic loss 可得本稿 log(1+exp(z))−az；这是相同损失的标签转换，不是新训练方法。 |
| variable projection；separable nonlinear least squares；[O'Leary–Rust](https://www.cs.umd.edu/users/oleary/software/varpro.pdf)，§1 式(2)–(3)、§2；L-BFGS-B：[Zhu 等作者页面](https://users.iems.northwestern.edu/~nocedal/Abstracts/erice.html)，论文题名及摘要 | 保留方法名称。逐用户时延、Doppler 搜索及增益重拟合是本稿组合，不另赋予现成算法名称。 |
| minimum description length (MDL)；[Nadakuditi–Edelman](https://math.mit.edu/~edelman/publications/sample_eigenvalue.pdf)，§II-A 式(5)–(7)，pp.2626–2627 | 保留 Wax–Kailath MDL 的归属；使用文中回顾的准则，不称为 Nadakuditi–Edelman 新估计器。 |
| AFDM、DAFT、CPP；[Bemani 作者稿](https://arxiv.org/html/2204.12798v2)，摘要、§II-B 式(11)–(16)、§III-A 式(18)–(19)；LEO、UPA：Shen §II 开头与 §II-A；MMV：Cai §I-B1 | 现有缩写和模型用语有来源，保留。网络、维度和接收机组合以本稿定义为准。 |

以下旧表述属于本稿自拟压缩描述，本轮不再将它们用作固定名词：

| 原表述 | 当前直接描述 |
|---|---|
| access ensemble | activity model；仿真段直接使用 For simulations |
| candidate-channel distribution | distribution of normalized channels generated before activity masking |
| folded delay | 直接写搜索区间 d∈[0,N)，随后说明整数周期时延等价 |
| physical atom / coarse delay–Doppler atoms | 相位搜索写式(23)的 pilot response vector；复杂度按 path matrices 与 pilot responses 分别计数 |
| phase-operator mismatch | error in the observation matrix due to phase estimation |
| spatial unfolding | 明确说明 reshape 成每行对应一根天线的矩阵；保留张量重排操作本身 |
| active-conditional law | channel distribution conditioned on being active |
| shared-variance rule | 直接说明求公共方差所用的平均操作 |
| scalar/aggregate readout | scalar function/output 或 learned error estimates，按所在公式的对象使用 |

conditional mean-squared error 是已明确定义的条件平方损失期望，不是另一个方法名称；均值偏差分解和终端平均目标由附录 A 的式(A.1)–(A.3)直接推导。estimate-stability counter、site-stability counter 是本稿停止条件中明确规定的计数变量说明，不作为文献中的算法名称；无需为这些变量另造来源。

## 当前论文的接收机表述（2026-10-18）

当前正文以 linear estimation、channel and activity denoising、extrinsic message update 描述迭代。linear estimator、denoiser 和 extrinsic message 的原文依据为 Cai §III-A–B，式(6)–(42)；Gaussian projection 的定位为该文式(17)、(32)。模块组合和本稿具体更新按正文公式定义。引用继续保留在消息交换、Gaussian 近似、score 训练及阻尼的对应位置。此前缩写核对条目保留为历史记录，当前稿用语以本条为准。

当前论文通用称谓补充：message passing（MP）/ 消息传递。原文依据为 Cai §II-B（消息传递与 Gaussian 近似）、§III（外信息交换），以及 Shen §I 的 MP-based algorithm 表述与 §III 的模块间消息交换。当前正文首次出现写 message passing (MP)，后文用 MP iterations；具体更新仍由第 III–V 章公式定义。


## 引言用语与来源（2026-10-18）

| 用语 | 原文与位置 | 当前用途 |
|---|---|---|
| GNSS-independent operation / GNSS 独立运行；without GNSS assistance / 无 GNSS 辅助 | Caus–Shaat, An OTFS-based Random Access Scheme for GNSS Independent Operation in NTN, 2025, 标题与§I–II，https://arxiv.org/html/2506.03852v1；Shen §I、§II开头 p.3 | 本文限定终端不使用 GNSS 辅助，公共参考时延补偿后在卫星接收端处理用户差分量；不意味着卫星定轨亦不使用 GNSS |
| GNSS-capable UE、pre-compensation / 具备 GNSS 能力的终端、预补偿 | 3GPP TS 38.300 V17.2.0 §16.14.1 p.177、§16.14.2.2 pp.178–179 | Release 17 背景陈述；已添加主参考文献条目 3gpp38300 |
| sparsity pattern learning、delay-Doppler grid、graph nodes / 稀疏模式学习、时延–多普勒网格、图节点 | Ding2026 摘要、§I、§III；本地 reference/reviews/section_structure_20261009/ding.txt | 描述 Ding 的相关工作；承认其学习节点间相关性，与本稿直接有效信道先验区分 |
| AFDM effective channel、likelihood-annealed Langevin dynamics / AFDM 等效信道、似然退火 Langevin 动力学 | Huang2026 摘要 p.2949、§II eq.(4)、§III | 直接信道估计与生成先验相关工作；不将其采样算法描述为本文算法 |
| score-based generative models、posterior sampling / 基于得分的生成模型、后验采样 | Arvinte–Tamir2023 摘要、§III；Cai2026 §I、§IV | 区分采样式信道估计和 MP 中的矩估计 |

本轮引言的句子证据、贡献定位和结果来源见 paper/checks/introduction_20261018_134220/SOURCE_MAP.md。引言采用现有 MP 通称，不增加接收机缩写。

## 独立稳定性开发候选（2026-10-19，未切换冻结主线）

Anderson acceleration / Anderson 加速：Walker–Ni, *SIAM Journal on Numerical Analysis* 49(4), 1715–1735 (2011)，§1 Algorithm AA、式(1.1)–(1.2)，p.1716；[作者稿](https://users.wpi.edu/~walker/Papers/Walker-Ni,SINUM,V49,1715-1735.pdf)。候选对两组 Gaussian 消息的均值和对数方差进行有限历史残差最小化，仍使用原三网络与非线性矩计算。正则项、系数与步长拒绝界是本次实现的明确设置，不归为该文的收敛定理；不得由此声称结构化 AFDM 接收机全局收敛。候选源码、设置和独立开发结果保存在 `runs/stability_repair_20261019/`，冻结主线不变。

另一候选按预先固定的顺序尝试阻尼系数 0.1、0.05，只在前一次未满足原停止判据时重新初始化迭代，并选择首个收敛结果。单次 Gaussian 均值、方差的阻尼仍对应 Cai §V-B1，式(57)–(58)；尝试顺序与基于收敛状态的选择是本项目明确规定的执行规则，不包装为文献中的新方法名称，也不声称全局收敛。不得使用真值或 NMSE 选择尝试；总轮数、耗时和失败尝试必须保留。实现与验证见 `runs/stability_repair_retry_20261019/`。


## 当前正文基础方法的直接来源（2026-10-18）

本条补充基础方法的上游出处，当前正文按下表引用；既有历史核对记录保留。

| 用语／操作 | 直接来源与定位 | 当前用途 |
|---|---|---|
| extrinsic message；extrinsic mean/variance / 外信息消息；外信息均值和方差 | [Ma–Yuan–Ping, IEEE SPL 2015](https://lsec.cc.ac.cn/~mjj/papers/Ma2015b.pdf)，§II-A–B，Fig.1，式(11)、(22)–(24)，pp.159–160；Cai 参考文献[26] | 第 III 章线性估计器与非线性去噪器间的外信息交换。引用两模块结构及 Gaussian 外信息计算，不将该文部分 DFT 模型的状态演化结论移植到本稿。 |
| Gaussian projection / Gaussian 投影；moment matching / 矩匹配 | [Minka, UAI 2001](https://tminka.github.io/papers/ep/minka-ep-uai.pdf)，§2 的 Gaussian 矩匹配、§3 式(8)–(10)的因子除法与近似分布更新 | 第 III 章 Gaussian 近似与消息相除沿用现有 minka2001 引用；具体各向同性近似由本稿公式定义。 |
| Tweedie's formula / Tweedie 公式及其二阶形式 | [Efron, JASA 2011 作者稿](https://efron.ckirby.su.domains/papers/2011TweediesFormula.pdf)，§2 式(2.7)–(2.8)，PDF p.4；Cai 参考文献[29] | 第 IV 章均值与协方差表达。原文式(2.8)为标量正态位置族形式，本稿采用相应多元梯度／Hessian 形式和实方差 v/2 约定；不将 Efron 称为该公式最早提出者。 |
| second-order denoising score matching；trace / 二阶去噪得分匹配；迹 | [Lu 等, ICML 2022](https://proceedings.mlr.press/v162/lu22f/lu22f.pdf)，§4.2 Corollary 4.2 式(15)，PDF p.5；Appendix F.2 式(138)–(143)，PDF p.22；Cai 参考文献[31] | 第 IV 章先汇总坐标再平方的标量训练目标直接引 Lu。取 d=2D、σ²=v/2、α=1，并用各坐标输出之和参数化迹；本稿的噪声权重和归一化保持不变。 |

双得分网络用于 JADCE 的具体设计在第 IV 章开头引用 Cai §IV。均值与方差线性阻尼的术语依据保留为 Cai §V-B1，正文第 V 章直接说明更新操作与公式。引言相关工作保留 Cai；贡献列表直接陈述本文接收机的组成，技术来源在对应推导处说明。

## 观测模型与方差计算的正文表述（2026-10-18）

| 用语或操作 | 来源与定位 | 正文定义 |
|---|---|---|
| pseudo AWGN observation model / 等效 AWGN 观测模型；denoiser input / 去噪器输入 | [Cai v2](https://arxiv.org/html/2506.00581v2)，§III-B 式(20)、§V-B1首段 | 第 III 章以 AWGN observation model 描述去噪器输入，保留该模型用于近似迭代输入的说明；热噪声与去噪器输入中的等效噪声按各自公式区分。 |
| Gaussian projection / Gaussian 投影 | Cai §III-A 式(9)、§III-B 式(17)、(32)；[Minka §2–3](https://tminka.github.io/papers/ep/minka-ep-uai.pdf) | 线性模块明确将协方差替换为其归一化迹乘单位阵。 |
| conditional mean-squared error / 条件均方误差；对用户取平均 | 本稿附录 A 式(A.1)–(A.3)的条件期望与 Gaussian 拟合推导；二阶训练目标来源见上表 Lu §4.2 Corollary 4.2 | 对各用户条件均方误差估计取平均并施加下限，将所得标量用作每用户 Gaussian 近似的每坐标方差。反馈方差另由活动混合协方差的迹按用户与天线平均得到。两处分别描述所平均的对象及所得标量的用途。 |

## 接收端天线误差协方差的可观测估计对照（2026-10-19）

这里沿用 sample covariance / 样本协方差和 covariance / 协方差的含义；观测空间样本协方差及白噪声估计的来源见本文件已有 Wax–Kailath MDL 条目。计算实际使用未中心化二阶矩，零均值误差模型下才称为协方差，并另外记录误差均值的能量比例。

将每用户当前查询整理为 R_k ∈ C^(16×256)，对全部用户或按观测查询能量选出的较低一半用户，计算 Σ_k R_k R_k^H / (|S|×256)。用户选择比例 1/2 是本次预先固定的实验设置，不是文献算法名称，也不使用真实活动标签。它可能混入信道分量，不能在未经检验时当成精确误差协方差。开发与新场景确认记录分别见 runs/receiver_covariance_20261019/ 和 runs/receiver_covariance_confirmation_20261019/。

对照还计算 (R−m)(R−m)^H 的空间平均加上近似后验空间协方差。其条件期望关系直接来自二阶矩分解；当前 Bernoulli–Gaussian 联合矩的文献定位为 [Cai v2 §III-B3，式(32)–(38)](https://arxiv.org/html/2506.00581v2#S3.SS2.SSS3)。只有精确条件矩才得到精确条件期望，不能把有限网络的近似矩代入后称为已校准估计。

首轮线性传播对照由本项目 THEORY.md 的 T5 直接展开：若未知输入的各行独立且共享天线协方差 C_X，则平均误差协方差为 ||LA−I||_F² C_X / D + σ²||L||_F² I / D，D 为未知输入行数；观测空间协方差用于估计 C_X。这里各行独立是假设，并非当前 AFDM 信道已满足的性质。代数与复数旋转一致性核对保存在 ALGEBRA_CHECK.json。所有筛查容差均为预先声明的数值验证标准，不是统计置信界或全局收敛定理。

## 相关高斯噪声下的 score 训练文献核对（2026-10-19）

以下是文献依据与适用范围，不表示已修改接收机或启动训练。

| 原词／操作 | 原文定位 | 对本项目的含义与限制 |
|---|---|---|
| Non-Isotropic Gaussian Noise Models / 非各向同性高斯噪声模型 | Voleti–Oberman–Pal, *Score-based Denoising Diffusion with Non-Isotropic Gaussian Noise Models* (2022), [v2 §3 式(10)、(15)–(16)，附录 E.1–E.2、E.7 式(103)](https://arxiv.org/html/2210.12254v2) | 在 Gaussian 扰动中使用非单位协方差，配套修改训练与去噪表达。式(16)后明确指出前向扰动不同，不能直接复用原 DDPM 去噪网络。主要实验是 GFF 图像生成，不是 AFDM 消息传递；不能将其当成任意逐轮估计协方差的现成接收机。 |
| Whitened Score Diffusion / 白化得分扩散（作者命名） | Alido–Li–Sun–Tian, *Whitened Score Diffusion: A Structured Prior for Imaging Inverse Problems* (2025), [v1 §3.1、§3.3、§4.1–4.2](https://arxiv.org/html/2505.10311v1) | 学习 G_t G_t^T 乘 score，避免训练目标中的显式协方差求逆；训练随机改变 Gaussian 滤波相关结构。该名称不等于把输入白化后套用旧网络。实验为图像逆问题；§4.2 的似然权重以真值 PSNR 搜索，不能照搬为本项目无真值接收端调参。 |
| Architecture and covariance conditioning / 网络结构与协方差条件输入 | Zilberstein–Segarra–Simoncelli–Guth, *Learning Normalized Energy Models for Linear Inverse Problems* (2026), [v1 §3.1 式(7)–(8)、§3.2 式(9)、§3.3、附录 C.1 式(41)–(46)](https://arxiv.org/html/2605.15487v1) | 学习 U_theta(y,Sigma)，通过输入梯度得到 score；协方差嵌入调制网络特征。实现限于空间域或频域可对角化的结构，未验证本项目任意复天线协方差及消息反馈。该文 covariance score 指对协方差参数的能量导数，不等同于当前二阶网络的 Hessian 迹目标。 |

公开实现核对：[WS Diffusion 的 train.py](https://github.com/jeffreyalido/wsdiffusion/blob/main/train.py)，2026-10-19 读取的版本第 55–60 行默认 isotropic=True，第 71–81 行先采样扰动、构造目标，再调用 model(xt,t)，未显式传入协方差。该可变分支代码只支持本次接口观察，不作为固定版本复现资产；相关噪声训练与显式协方差条件输入必须区分。

项目适配时可用实数堆叠表示写 r=h+Lz、LL^T=C、z~N(0,I)。在给定 C、噪声独立于 h 的 Gaussian 模型下，条件扰动 score 为 −C^{-1}(r−h)，后验均值为 r+C∇_r log p(r|C)；这是上述 Gaussian 模型的直接表达，不是新方法名称。复数实现须明确实虚堆叠协方差及 v/2 约定。由同一观测估计的 C_hat 不自动满足条件独立性，实测相关性匹配也不证明误差 Gaussian 或无偏。

重训范围的表述：继续采用单次网络求条件矩、活动概率的当前接收机时，应训练匹配新扰动分布的候选并配套验证三网络；不能据此声称所有 colored-noise 逆问题都必须重训。保留先验模型、另行用含协方差的似然做后验推断是另一条路线，见上述 2026 文献 §5 对 Bayesian 与 regression 方法的区分，但不等价于直接把旧标量噪声网络用于新 Gaussian 消息。

## 活跃用户误差诊断的操作定义（2026-10-19）

本次不引入新算法名称。沿用本文件已有的 covariance、pseudo AWGN observation model、Gaussian 消息与外信息术语；下列为本项目 THEORY.md T5 的直接代数分解及离线统计量。

令 X 为真实活动加权信道，X_p 为线性模块输入均值，A 为估计相位对应算子，L 为当前线性外信息增益。用户 k 的原始查询误差分为 (L_k A_k−I)(X_k−X_{p,k})、Σ_{j≠k}L_k A_j(X_j−X_{p,j}) 和 L_k(Y−AX)。最后一项同时包含测量噪声和算子失配，不称为纯热噪声。各分量按原查询阻尼递推，二阶矩保留所有交叉项；能量分量不能当成互不重叠的百分比相加。

离线信道投影系数定义为 beta_k=<H_k,R_k−H_k>/||H_k||²，图中绘制 Re(1+beta_k)。它描述当前查询沿真实信道方向的投影，不是物理信道增益、保留信号能量比例或接收端可用的校正系数。按行奇偶两半拟合 beta、在另一半计算误差下降仅为诊断，同一物理信道内的两半不独立。采用相同每用户真实误差二阶矩生成独立列复高斯对照，也不把拟合协方差和有限 Monte Carlo 范围当成总体置信区间。

报告见 results/active_query_error_diagnosis_20261019/REPORT.json。结论范围：现有共享或逐用户天线协方差，加上独立零均值 Gaussian 误差的近似，不能解释观察到的全部信号相关误差；未训练或验证新的协方差条件网络，不能断言它没有改善作用，也不能宣称已解决稳定性问题。

## Score 网络训练输入与跨接收机复用（2026-10-19）

本条为文献核对及候选设计判断，未启动训练，未切换冻结主线。

| 原词／操作 | 原文定位 | 输入与适用范围 |
|---|---|---|
| Noise Conditional Score Networks；denoising score matching / 噪声条件得分网络；去噪得分匹配 | [Song–Ermon, NeurIPS 2019](https://papers.nips.cc/paper/9361-generative-modeling-by-estimating-gradients-of-the-data-distribution.pdf)，§2.1 式(2)，§4.1–4.2 式(5)–(6)，印刷页3、5–6 | 输入为受扰动数据与噪声尺度，不是单独的噪声样本；Gaussian 条件目标为 −(r−h)/σ²，平方损失最优解是受扰动数据边缘分布的 score。原始 score matching 也可直接从干净数据训练（§2.1 式(1)），因此 Gaussian 扰动并非 score 定义本身的限制。 |
| Training a Score-Based Model for Wireless Channels；posterior sampling / 信道得分模型训练；后验采样 | [Arvinte–Tamir, IEEE TWC 2023](https://arxiv.org/html/2204.07122v2)，§III-A 式(14)、§III-B 式(15)–(16) | 训练输入为干净 CSI 加合成 Gaussian 噪声；式(14)不使用导频矩阵与导频测量噪声功率。推断阶段才结合测量似然。这支持先验与测量模型分离，但不保证任意信道先验变化后的性能，也不等价于当前 EP 单次矩计算。 |
| Soft Score Matching / 软得分匹配（作者命名） | [Daras 等, Soft Diffusion v2](https://arxiv.org/html/2209.05442v2)，§3.1 式(4)–(7)、Theorem 3.1 | 可使用确定线性算子 C_t 作用于干净信号后加 Gaussian 噪声，网络输入 x_t、t。该文按预定 t 调度算子；不应描述成已验证任意未见算子作为额外输入的网络。一般 DSM 需要匹配条件扰动分布的 score，不能保留白噪声目标而任意替换训练输入。 |
| covariance conditioning；Bayesian approaches；regression-based approaches / 协方差条件输入；贝叶斯方法；回归方法 | [Zilberstein 等, 2026 v1](https://arxiv.org/html/2605.15487v1)，§2.2、§3.1–3.3、§5 | 模型可显式条件于协方差，相关 Gaussian 合成训练不必绑定具体接收机。已验证结构限于空间域或频域对角协方差。直接学习条件后验与先验加显式似然是不同设计；在扩散噪声尺度下似然项仍可能需要近似，不是免费获得精确后验。 |

本项目代码核对：`src/afdm_jadcedd/experiment/training/scores/score_matching.py` 的 `make_cai_batch` 构造归一化实虚堆叠干净信道 h，再生成 r=h+sqrt(v/2)ε，ε~N(0,I)。`algorithm/proposed/network.py` 接收 r 和复方差 v，以 log(v) 形成条件输入；v/2 是实坐标方差。当前 score 训练不输入用户数、导频矩阵、阻尼或迭代轮数。

以下是由上述目标和本项目代码推导的设计判断，不是已完成的性能验证：

- 将实际消息 r 与真值 h 配对做均方误差回归，最优解是该数据联合分布下的 E[h|r,条件]，并不自动保持原 Gaussian 平滑先验 score 的含义。实际消息误差不满足独立 Gaussian 时，直接把 −(r−h)/σ² 当 score 标签缺少原 DSM 的依据。
- 实际消息联合分布可能随导频、负载、阻尼、轮数及反馈网络权重变化。覆盖多配置并提供充分条件输入可能改善复用，不能断言实际消息训练必然无泛化能力，也不能默认它具有跨接收机普适性。
- 优先用独立开发消息检查合成扰动族的覆盖程度，并检验能否通过消息更新改善近似；如需训练，优先考虑明确且可控的合成扰动族及接收端可获得的条件。白 Gaussian 也保留为其中一种情形。不同先验、协方差结构与参数范围仍需留出验证。
- 对一般 r=B h+Lz，若给定 B、C=LL^T 后 z 独立于 h，条件扰动 score 为 −C^{-1}(r−B h)。由该边缘 score 得到的 r+C s(r,B,C) 对应 E[B h|r,B,C]，不能未经处理就称为 E[h|r,B,C]。信号相关误差与反馈偏差不应仅靠改变协方差掩盖。

## Huang 2026 训练输入与推断接口再核对（2026-10-19）

来源：本机完整五页 Huang 等 PDF（仅本地历史资料：`reference/literature/huang2026.pdf`），*Prior-Agnostic AFDM Channel Estimation for High-Mobility LEO Satellite Communications Using Diffusion Models*，IEEE WCL 15，2949–2953，DOI 10.1109/LWC.2026.3689601。本次提取全部正文，并视觉核对 p.2951、p.2952 的公式、Algorithm 1 与曲线；旧记录中的 2949–2952 未包含参考文献所在末页。

| 核查对象 | 原文证据 | 判断与边界 |
|---|---|---|
| 训练输入与目标 | §III-A，p.2951 式(7)及其后两段 | 干净 AFDM 有效信道加人工复白 Gaussian 噪声，以缩放的负噪声为训练目标；实虚两通道。没有使用实际接收机迭代消息训练的描述。 |
| 推断接口 | §III-B，p.2951 式(8)–(10)、Fig.2；p.2952 Algorithm 1 | 当前 H 作为 score 查询点，先验梯度与原始观测 Y=HX+Z 的似然梯度、随机扰动共同更新。没有将线性模块输出解释为真信道加独立 AWGN 后进行一次后验矩转换的接口。score 是空间点上的函数；理想精确 score 的求值不要求该点相对某个真值的误差满足 Gaussian 模型。有限网络仍有查询覆盖和近似误差。 |
| 噪声层级的条件输入 | 式(7)、Algorithm 1、Fig.1 均只标 s_theta(H)，正文声明多个训练／退火噪声层级 | 论文未明确展示 sigma 的网络条件输入或逐层级网络选择。不能据此确认作者实现没有条件输入；也不能替作者补写为已验证的 s_theta(H,sigma)。如果实际用同一无条件网络混合多个噪声层级，目标一般不等于每个指定层级的条件 score；这是条件性分析，并非作者代码的已证实错误。 |
| 似然退火 | Algorithm 1 分母 sigma_z²+sigma_i²，§III-B 的退火说明 | 是文中采用的标量退火权重，不是对线性模块误差协方差进行校准。Gaussian 平滑状态下的精确 p(Y|H_i) 需要对干净 H 积分，通常不等于将原似然方差简单相加；即便采用把状态扰动传播到观测的近似，还会涉及导频算子的几何结构。不能由该标量公式推出任意导频下精确后验采样。 |
| 公式符号 | p.2951 式(10)、p.2952 Algorithm 1 明确写 +(HX−Y)X^H | 在式(6)的通常 Gaussian 观测似然与梯度上升约定下，似然梯度方向应与 (Y−HX)X^H 一致（复梯度约定会影响常数，不改变方向）。正文疑有符号问题；无作者实现佐证时不能断言实际仿真使用错误符号。 |
| 先验泛化与曲线证据 | §IV，pp.2952–2953；Fig.3、Fig.6 | 用 NTN-TDL-D 生成 10,000 训练信道，每个 A/B/C/D profile 各 100 测试信道。作者承认 B 与训练分布失配导致较差表现。Fig.3 有局部回升后稳定，不能称逐轮单调；正文未报告迭代状态误差的白性、Gaussian 性、信号独立性诊断。该系统是单用户 SISO，不能把其结果直接移植到多用户活动检测闭环。 |

本项目结论：Huang 不依赖当前接收机局部矩计算所需的同一种伪 AWGN 解释，但仍受学习先验、有限噪声层级、近似似然和数值采样误差影响。该比较支持优先区分“先验 score 学得是否准确”和“消息接口是否满足矩转换假设”，不能单凭两种方法均以 Gaussian 扰动训练而判定二者具有相同故障，也不能据此决定重训或切换接收机。本轮没有训练、运行 Huang 基线或改动推断代码。

## Cai 消息传递框架在当前 AFDM 表示下的适用性审计（2026-10-19）

文献位置：[Cai v2](https://arxiv.org/html/2506.00581v2)，§II-A 式(3)–(4)的逐子载波对角导频与部分正交条件，§III-A Gaussian 线性更新与方差投影，§III-B 式(20)的 pseudo AWGN observation model，§V-B1 的大系统／right-rotationally invariant 条件与阻尼，§V-C 式(66)的 DFT 导频构造。部分正交 QQ^H=cI 与随机右旋转不变是不同性质，不能互相替代；Cai 自己的结构化 DFT 实验也不能视为完整满足任意右酉旋转不变性的证明。

核对的作者固定源码：[main_stmp_jadce.py, commit 0c75680c966dcb8e46250de146f4c27e9294c283](https://github.com/chang-cai/score-massive-connectivity/blob/0c75680c966dcb8e46250de146f4c27e9294c283/main_stmp_jadce.py)，45–63 行为子载波块对角 DFT 导频，103–118 行为递归双向阻尼，130–139 行为依赖部分正交条件的线性更新，161–164 行为按天线平均的二阶读数，176、193–210 行实际调用 Gaussian 活动先验检测，211–219 行的 NMSE 仅对真实活跃用户统计。这是所核查提交的实际路径，不将其等同于论文所有公式或全部实验版本。

本机实现存在独立修改：一般算子的 SVD 线性更新、所有实坐标汇总的二阶训练／单个共享方差、单独训练的活动证据分类器、固定总体 RMS 归一化及 site 接受／回退规则。其失败不能直接归因于未经修改的 Cai 原算法；网络匹配、活动证据、Gaussian 投影和原始算子须分别排查。此前 `results/stability_message_form_20261019/AUDIT.json` 的 20 条件线性代数检验最大查询相对误差约 2.64e-15，只验证实现了声明的公式，不验证统计校准。

### 本轮确定性算子对照

实现 `scripts/audit_cai_operator_applicability.py`；协议和完整结果 `results/cai_operator_applicability_20261019/{PROTOCOL,REPORT}.json`。使用已有独立开发库 4 个物理场景、K=20/40/60/80/100 共 20 条件的公开算子；不读真值，不调用网络。输入分布替换为明确标记的 synthetic iid Gaussian x~CN(0,cI)，c 取本机初始化值，热噪声方差取对应公开值。解析计算首轮外信息 r=W y，

W=c A^H(noise I+c AA^H)^{-1}/kappa，kappa=tr(c A^H(noise I+c AA^H)^{-1}A)/d。

误差协方差为 C_e=cI+W(cAA^H+noise I)W^H−c(WA+(WA)^H)，与输入的交叉协方差为 E[(r−x)x^H]=c(WA−I)。每用户块宽 n=16；记录 ||W_k A_k−I_n||_F/sqrt(n) 和 ||C_e,kk−tr(C_e,kk)I_n/n||_F/(tr(C_e,kk)/sqrt(n))。均是显式定义的相对 Frobenius 范数，不是错误率或 NMSE，也不是新方法名称。这里的块是混合的 AFDM 信道坐标，不能与此前天线协方差诊断混淆。

| 算子 | 每用户自身响应偏离，先按用户取中位数、再按20条件取中位数 | 每用户误差协方差偏离各向同性，同样汇总 |
|---|---:|---:|
| 当前 AFDM 公开算子 | 0.953652 | 0.947712 |
| 保持行空间、把所有非零奇异值设成相同值 | 0.949561 | 0.944714 |
| 保持奇异值和 AA^H，使用随机正交右向量 | 0.986774 | 0.983437 |
| 按 Cai 子载波分块的 synthetic T=1 对照，保持矩阵尺寸、总能量及标量观测比 | 约 2.15e-16 | 约 2.29e-16 |

所有 80 次解析计算的全局平均误差方差与声明的标量方差相对误差最大 1.56e-15；协方差半正定、匹配谱对照的 AA^H 相等、Cai 形式对照的自身响应恒等均检查通过。当前 A 行正交相对偏离 0.090–0.221，非零奇异值条件数 1.17–1.49；这里不是严重非零谱病态导致了全部偏差。28 项输入、配置、权重和核心源码哈希前后不变。

维度解释：当前 A 为 Q×(KN)，开发条件 Q=N=16，单列观测比 Q/(KN)=1/K；Cai 原形式为 NT×NK，比值 T/K。上述 T=1 对照专门保持标量观测比相同，未复制 Cai 原论文工作点，也不是可直接用于当前 AFDM 的物理导频设计。不能将自由矩阵坐标计数当作物理信道的独立自由度，更不能从这个计数直接宣称问题不可辨识。

结论边界：全局迹正确不足以使每用户查询成为与自身信号独立的白 Gaussian 扰动；在这些有限维条件下，精确行正交或随机右向量也不足以自动恢复整个16维用户块的该性质。对照未包含活动稀疏性、真实信道相关性、相位前端或后续反馈；不能据此证明完整 Cai 框架不适用或证明替代算法优越。现有证据优先支持排查每用户块的消息近似及活动反馈，再决定是否改先验网络。后续应在独立可计算先验下比较精确局部矩与当前投影闭环，并单独隔离活动证据和相位估计；正式实验继续暂停，未重训。

## Cai 框架的顺序隔离诊断（2026-10-19）

协议与原始结果：`runs/cai_framework_sequence_20261019/`。按纯 Gaussian 精确条件矩、活动反馈、相位前端顺序执行；主脚本 `scripts/diagnose_cai_framework_sequence.py`。沿用已有独立开发种子 202610195000001、202610195000002，每个种子取 K=20/100，共四个物理条件；这些场景已参与诊断，不能称为新的独立验收。物理运行使用现有新50,000样本三网络、阻尼0.1、600轮上限和原停止条件。

1. 精确 Gaussian 对照：两个种子、两种用户数、独立和相关块 Gaussian 先验，共8项。局部均值与方差解析计算，关闭活动变量与网络；以全局 Gaussian 后验为参考。全部收敛，后验均值最大相对误差2.22e-8，共享方差最大相对偏差2.48%。这是匹配 synthetic Gaussian 模型的结果，不是物理信道正确性证明。对 Gaussian 两模块而言，若到达一致固定点，外信息自然参数相加可恢复全局 Gaussian 后验均值的线性方程；因此均值吻合也不能替代非 Gaussian 先验测试。

2. 活动反馈对照：同一观测、估计相位和观测驱动噪声估计，分别使用原分类器或固定真实活动概率0/1。后者为 oracle 诊断；不提供真实信道数值，保留原信道网络、条件方差汇总和反馈公式。固定活动同时改变均值与活动混合协方差，是隔离活动分支的整体影响，不是只删除最终输出的虚警用户。第一轮活跃用户信道均值相同，后续活跃用户误差不同，可用于区分最终活动掩码的直接效果和反馈效应。

3. 相位前端对照：将公开 pilot 的跨帧乘子替换为 exp(i*q*true_slope)，保持观测、噪声估计、网络与其他设置；同时运行学习活动和 oracle 活动两个分支。估计相位公式重构的 A 与原输入逐元素精确相同。真实相位与真实活动只进入明确标注的 oracle 分支，不作为可部署结果。原接收机12个已保存查询快照重放差异均为0。主实验共16次物理运行，均满足各自原停止条件，但这不证明结果最优。

补充的相同预算比较：原活动与 oracle 活动分支停止轮数不同，故对两个 K100 条件的四个分支各执行固定300次更新（共8次）。仅将上限设为300、最少轮数设为301以禁止提前停止；其结果不标为原判据收敛。重放逐项比较原生停止前的已保存查询、协方差、活动概率和均值，要求精确一致。实现 `scripts/check_cai_equal_budget.py`，原始输出保留。

补充的精确 Bernoulli–Gaussian 联合后验：`scripts/check_cai_exact_mixture.py` 在两个公开K20算子中预先取前6个用户块，生成匹配的 synthetic 信道与观测；每用户活动概率0.25，独立／相关Gaussian活跃先验，两种噪声方差，共8项。穷举64种活动组合，计算精确全局后验；消息迭代使用解析局部活动概率与条件矩，不调用网络。全部收敛，但仍有近似偏差：活动概率最大绝对差0.09452、方差最大相对偏差9.83%。额外条件平方误差定义为 ||m_MP−E[X|Y]||² / tr Cov(X|Y)，按全部坐标取一致归一化；最大0.006184，即相对精确后验的最优条件风险增加约0.62%。这不是NMSE改善率、总体误差保证或K100性能结果。

精确参考通过独立按用户块构造的后验均值复核（最大相对差7.18e-15），并通过观测边缘对数密度的有限差分方向导数与 2 Re< A E[X|Y]−Y, direction >/noise 对照（最大相对差4.32e-10）。来源为本项目 Gaussian 观测模型和条件期望恒等式；不引入新算法名称。

完成记录：`results/cai_framework_sequence_20261019/FINAL_REPORT.json` 汇总三步主实验与两项补充。两个 K100 场景固定300轮后的全信道NMSE如下；真实变量仅用于 oracle 诊断。

| 诊断分支 | 种子202610195000001，11个活跃用户 | 种子202610195000002，9个活跃用户 |
|---|---:|---:|
| 估计相位＋学习活动 | −6.2350 dB，漏检2、虚警0 | −7.0478 dB，漏检0、虚警0 |
| 估计相位＋真实活动 | −6.1044 dB | −7.0374 dB |
| 真实相位＋学习活动 | −7.0298 dB，漏检1、虚警0 | −7.7259 dB，漏检0、虚警0 |
| 真实相位＋真实活动 | −8.1581 dB | −7.7215 dB |

在估计相位下，四个物理条件第30轮的活跃用户NMSE均因固定真实活动而降低，改善2.6107–10.8271 dB；这比最终直接去掉非活跃用户输出更能体现反馈影响。原停止时 oracle 活动分支较早停下导致的部分NMSE差距，在相同300轮预算下缩小。真实相位对两个K100学习活动分支分别改善0.7947、0.6781 dB。首个K100案例在真实相位下，再固定真实活动改善1.1284 dB；另一个案例差异仅−0.0044 dB，不能把活动与相位影响视为统一可加的增益。

最终判断：上述匹配先验对照未显示消息投影闭环必然失效；真实系统中活动反馈的早期放大与相位估计影响均有配对证据。仍不能证明当前框架已适配所有负载，也不能把剩余NMSE全部归因于框架或网络错误，因为噪声、后验不确定性、有限网络和其他模型近似尚未全部隔离。优先保留可验证的线性／外信息代数，继续检查实际消息下的活动证据校准与反馈统计。没有重训或恢复正式实验；552项历史资产及本轮协议绑定的源码／权重均验证未改动。

## 实际消息下的活动证据与早期反馈诊断（2026-10-19）

协议 `runs/activity_evidence_feedback_20261019/PROTOCOL.json`；执行脚本 `scripts/diagnose_activity_evidence_feedback.py`。仅使用冻结的新50,000样本网络和阻尼0.1，不拟合校准参数、不重训、不恢复正式实验。四个物理种子各取K20/K100，共8条件；后两个种子未参与上一轮四条件反馈对照，但此前已用于协方差诊断，不能称为封存的独立验收。同一种子的不同K不计作独立物理场景。

校准用语依据：[Guo et al., On Calibration of Modern Neural Networks, ICML 2017](https://proceedings.mlr.press/v70/guo17a.html)，§2式(1)说明预测置信度与实际正确概率的关系，式(6)为negative log likelihood；§4（PDF第6页）式(9)定义temperature scaling。本轮不实施温度拟合。二分类记录平均负对数似然 `mean(logaddexp(0,z)-a*z)`，其中 `z=logit(rho)+ell`；另记录显式定义的概率平方误差 `mean((sigmoid(z)-a)^2)`。这些损失同时受区分能力和概率准确性影响，不把单个损失当作纯粹校准误差。

另直接枚举活跃／不活跃用户对，计算 `mean(1[ell_active>ell_inactive]+0.5*1[ell_active=ell_inactive])`。这里写出统计量本身，不创造方法名称；有限小场景上的排序统计不作总体性能保证。对所有用户应用同一个严格递增logit映射保持该统计量不变，因此温度或统一偏移不能修复已有的用户间排序错误。这是代数结论，不是声称所有校准方法都无效。

纯噪声对照：使用原接收机保存的首轮、第30轮和第120轮（若此前停止则取最终轮）查询。按公开查询能量取较低的一半用户，其未中心化天线二阶矩重标定为 `tr(C)=16*v`，构造 `n=C^(1/2)z`；对照 `n=sqrt(v)z`，二者使用同一组128个标准复Gaussian随机数组。各自重新调用原一阶网络生成同查询条件均值，再调用原活动分类器；不使用真实活动标签选择协方差。只在完成网络计算后读取标签评估真实消息。该模拟仅包含天线相关、其余网格坐标独立，不等同于完整真实消息误差。活动证据输入包含一阶网络均值，故它不能单独定位为分类器本身的权重问题。

反馈对照：预先固定前30次非线性更新的 `ell=0`，因此联合均值和混合协方差中的活动概率均为公开先验rho；第31次起恢复原分类器。始终计算原分类器并单独保存其未使用logit，便于判断解除干预时的输入状态。使用相同观测、估计相位和噪声估计，两分支均强制300次更新，不宣称满足原收敛标准。30只是事先规定的机制诊断窗口，不是调优所得的推荐参数。此操作为可执行的因果干预对照，不命名为新的推断算法，不将其输出解释为经过校准的后验。真值仅用于结束后的逐轮评分，保留所有不利条件。

完成结果见 `results/activity_evidence_feedback_20261019/REPORT.json`、`activity_diagnosis.png`、`feedback_nmse.png`。12个快照共3072次synthetic纯噪声查询，四个首轮条件均为白Gaussian虚警0/128、接收端相关Gaussian虚警128/128；两类预期总功率完全相同，所有快照实测平均功率／声明方差范围分别0.99849–1.00240和0.99412–1.00321。真实首轮的215个不活跃用户全部被误判。第30轮首个K100条件真实虚警67/89，而相关Gaussian对照仅24/128，说明该空间协方差模型并未完整重现后续错误分布。两个K100条件的真实logit用户对排序统计从首轮0.7610、0.8974降到第30轮0.5158、0.5629；另一K20条件降至0.3281。真实相位分支同样出现首轮全部判活跃和部分后续排序恶化，不能将该现象全部归因于相位估计。

全部16次配对运行完成，相同300次更新后的全信道NMSE：

| 开发场景索引 | K | 原活动证据 / dB | 前30轮使用活动先验 / dB |
|---|---:|---:|---:|
| 000 | 20 | −17.31710 | −17.31689 |
| 000 | 100 | −6.23501 | −6.24884 |
| 001 | 20 | −12.41543 | −12.41670 |
| 001 | 100 | −7.04779 | −6.58343 |
| 002 | 20 | −17.56094 | −17.56098 |
| 002 | 100 | −7.10640 | −7.10715 |
| 003 | 20 | −19.48740 | −19.48742 |
| 003 | 100 | −11.61913 | −11.61905 |

七个条件的最终变化绝对值不超过0.01383 dB；场景001/K100恶化0.46436 dB，漏检从0增到1。没有一致改善，不采纳固定延迟30轮作为修复。早期NMSE峰值下降包含小活动概率对输出均值的直接收缩；接近零估计本身就能得到约0 dB，不能将其误读为条件信道估计准确。四个K20条件恢复分类器前，原始网络对所有不活跃用户仍有虚警；其后重新出现明显误差回升。两个新增种子的结果也不支持此干预优于原设置。

所有16次运行均无查询超出方差支持范围、无site拒绝回退，排除了这些运行中的相关分支切换混杂。15个已有基线快照精确重放；8对首轮原始网络logit精确相同；干预分支第31–300轮实际使用logit均与原网络输出逐元素相同。297项协议绑定文件与552项历史资产校验通过。现阶段明确证据是相关噪声足以使整个活动证据分支失配，且简单延迟反馈没有修复它；仍未单独拆开一阶均值输入与分类器的贡献，也未证明只提供协方差即可解决后期信号相关偏差。保留现有权重，正式实验暂停。

## L-STMP 文献核对（2026-10-19）

来源：Yiming Wei、Xiaojun Yuan，*Learned Score-Based Turbo Message Passing for Channel Recovery From Spatially Compressed Measurements*，[arXiv:2610.17785v1](https://arxiv.org/html/2610.17785v1)，2026-10-13作者预印本。L-STMP采用原文名称。§I、§III-A讨论实际结构化测量下伪AWGN条件失配；§III-B式(8)的gamma校准线性后验方差，§III-C式(11)的alpha控制score均值校正，式(12)的beta校准观测残差估计的方差。gamma不是直接乘在线性均值增量上的参数。§III-D采用逐层加入、联合微调score与校准参数的加权NMSE训练；§V-A为5层独立NCSN++。§II-A是单用户已知压缩算子，§IV的DFT行选择仍满足BB^H=I；无本项目的未知活动分支。引用[16]对应Cai等的[2025图像恢复论文](https://arxiv.org/html/2503.22140v1)，不是本项目此前重点核对的JADCE论文。

本项目判断（非论文定理）：值得参考闭环校准的设计，但未证明普遍恢复AWGN条件或解决AFDM活动检测。联合重建损失微调后，网络不能自动沿用原先精确先验score的解释；跨用户数、算子及信道族的泛化须另测。保留冻结网络、只研究消息参数，是本项目可考虑的独立消融，不能称为完整L-STMP复现或借用其性能结论。

式(12)迁移前的代数检查：令e=H−Hhat，则观测残差为Be+N。减去平均噪声能量后仍含交叉项2Re<E[Be,N]>，而Hhat依赖同一个Y时该项通常不能假定为零。另有Bz=0时，Hhat与Hhat+z拥有完全相同残差，说明残差不能单独确定未观测方向的误差；噪声扣除后的标量也可能为负。式(9)的正外信息方差还要求0<v_post<v_pri，仅令gamma正不充分。这些是公式自身的复现约束，不据此猜测作者实际代码是否缺少截断；本轮检索未找到可核对的作者实现。没有运行L-STMP、修改接收机或启动训练。

### 后续贡献候选的边界与一致性检查（2026-10-19，尚未实施）

已有工作边界：L-STMP的展开及逐层校准不能作为本项目新贡献；[Whitened Score Diffusion](https://arxiv.org/html/2505.10311v1) §3–4已研究非各向同性Gaussian扰动；[Zilberstein等，Learning Normalized Energy Models for Linear Inverse Problems](https://proceedings.mlr.press/v306/zilberstein26b.html)摘要及[作者实现README](https://github.com/nzilberstein/Anisotropic-energy-Model)已说明协方差条件去噪、归一化能量与跨测量条件一致性。因此，相关噪声训练、协方差条件输入或能量模型本身均不宣称首创。JADCE深度展开亦有[Proximal Gradient-Based Unfolding for Massive Random Access in IoT Networks](https://arxiv.org/abs/2212.01839)。本次为定向初查，不构成完整查新。

候选问题是：接收端可估计的消息统计，能否支持相互一致的活动证据、活跃条件均值与方差，并改善未知活动反馈及跨配置泛化。现有代码已经使用Bernoulli混合矩公式，不能把该公式再次当作新方法；待检验的是生成这些量的网络是否对应同一个声明的消息分布。以下仅是工作模型下的恒等式：将复数堆成实向量，设r=a*h+epsilon，epsilon~N(0,C)独立于h，固定正定C，ell(r,C)=log p(r|a=1,C)−log p(r|a=0,C)。由Gaussian似然求导及Tweedie关系可得

`E[h|r,a=1,C] = C * grad_r ell(r,C)`，

`Cov(h|r,a=1,C) = C * Hessian_r ell(r,C) * C`。

推导依据：[Efron, Tweedie's Formula and Selection Bias](https://pmc.ncbi.nlm.nih.gov/articles/PMC3325056/)，§2式(2.5)–(2.8)的后验累积量导数关系；多维形式由对Gaussian密度直接求导得到。这些恒等式不是新的理论贡献。二维非零均值Gaussian活跃先验的解析复核误差分别1.24e-16、1.83e-16，仅检查代数。固定C是求导前提；将C估计自同一个r之后，不应把dC/dr自动带入上述偏导公式，也不能据此声称真实误差满足该模型。

可以先在匹配合成查询上检查现有网络的一致性偏差，再研究是否以额外损失约束活动证据；不能用失配的一阶均值强制监督分类器。导数关系不能确定ell的加性常数，故活动概率仍需独立的证据校准；全Hessian还可能带来较高计算成本。候选新训练应覆盖参数化噪声统计族，避免只记忆某个用户数或某条迭代轨迹；是否泛化必须用未参与设计的物理种子、用户数、导频和活动概率组合验证。协方差尚未解释本项目后期的信号相关偏差，不能预先保证上述候选足够。

建议将L-STMP式标量校准作为参照，逐项比较：加入接收端相关性信息、再加入活动证据与条件矩一致性约束。比较时控制网络容量、训练数据与更新预算，同时记录NMSE、漏检、虚警、概率准确性及失败场景；满足关系本身不是性能成功。上述均为候选设计，本轮未改变冻结主线、训练网络或拟合校准参数。

### 三个独立校准候选的首轮实现（2026-10-19）

实现为 `src/afdm_jadcedd/algorithm/proposed_calibration_candidate.py`，协议及复现实验入口为 `scripts/validate_message_calibration.py`。这是受 L-STMP §III-B–D 启发的小规模冻结网络消融，不是其完整复现：没有复现 gamma 线性方差更新、残差 beta 方差、五层独立 NCSN++ 或端到端展开训练。冻结现有50,000样本一阶、二阶和活动网络；三个候选均采用同样13输入、32/32隐藏单元、4输出的校准网络，标量候选将六个相关性输入置零。参数量相同不代表有效输入信息量或实际函数空间完全相同。

三个输出操作为 `mu=r+alpha*(f-r)`、`tau=v*sigmoid(logit(clip(tau_raw/v,1e-5,1-1e-5))+8*tanh(z_tau))`、`ell=exp(log(100)*tanh(z_gain))*ell_raw+100*tanh(z_bias)`，其中 `alpha=exp(log(4)*tanh(z_alpha))`。均值与证据的原始量来自同一查询，旧分类器仍输入旧一阶网络的均值；不能把校准后的均值直接塞回冻结分类器。正方差与 `tau<v` 是便于原Gaussian site更新的候选限制，不是任意非Gaussian先验下的逐样本后验方差定理。现有接收机依然按用户汇总条件方差，且向外只传各向同性近似。

相关性输入采用查询能量较低的一半用户的未中心化天线二阶矩，重标定为 `tr(C_complex)=16*v`，再固定收缩为 `0.95*C_complex+0.05*v*I`。输入包括最大特征值比例、`tr(C^2)/tr(C)^2` 以及逆平方根变换后的能量和内积。这是从接收量估计的统计特征，不是真值协方差，不进行未知信道白化后仍复用原先验的错误替换。

校准训练使用原物理训练库中不重复的2,048个活跃信道，配2,048个不活跃查询；每组32个查询共享一种Gaussian空间噪声，四分之一组各向同性，其余组为不同强度的秩1–4相关项加各向同性项。验证和合成测试分别从原验证库取不重合的512个活跃信道，加各512个不活跃查询。复方差范围[0.001,100]按对数均匀生成。校准验证/测试划分对本轮拟合独立，但原网络曾使用该验证库，不能称为原网络全新测试。物理闭环另用两个未用于训练、历史诊断或正式实验的新种子，每个种子四种用户数/导频帧数/活动概率配置。所有候选先按同一合成验证预测损失选定权重，再打开物理测试；固定300次更新不称为已满足原收敛判据。

一致性候选采用上文固定C下的Gaussian导数恒等式作为软损失，并非强制构造精确联合密度。设复维数d、实维数D=2d、z的每个实/虚分量独立取±1，方向 `u=C_complex*z/sqrt(2*v)`，固定接收端估计C，对同一查询计算正负delta=0.02扰动。第一方向导数除以sqrt(D)，对照 `Re<z,mu>/sqrt(v*d)`；第二方向导数除以D，其对z的期望为 `tr(V_complex)/(d*v)=tau/v`。这利用 `C_real=real_block(C_complex)/2`；不能漏掉复/实方差的因子2。训练仅使用一个随机方向的有限差分，存在抽样和有限差分误差，并且估计C不一定等于生成C。固定delta，额外损失权重0.1，不用物理测试调参。共同预测损失为活跃样本MSE + 0.05倍 `log(tau)+MSE/tau` + 平衡二分类负对数似然；不活跃样本不用于监督“活跃条件均值”为零。概率损失在平衡合成集上不能直接当作rho=0.1总体校准误差。

四项单元检查覆盖：非零均值相关复Gaussian解析后验的方向导数及迹归一化；共同酉基变换下的空间统计特征；零校准和同查询证据配对；标量候选屏蔽相关性输入及有限梯度。测试不替代闭环性能验证。零校准均值达到double舍入误差，方差/证据使用float32校准计算的容差约2e-7；极端原始方差受候选预设边界影响，因此合成汇总里的identity候选明确标注有方差边界，并不冒充完整原接收机baseline。

## 新接收机设计的术语与来源（2026-10-19，未训练）

完整设计见 `docs/PROPOSED_ALGORITHM_DESIGN_20261019.md`。它与此前五层独立 RefineNet 的 `unfolded_score_candidate.py` 草稿不同；此处仅记录方案，不改变冻结主线和实际运行状态。

- **Learned score-based turbo message passing、展开、逐层训练**：Wei–Yuan [L-STMP v1](https://arxiv.org/html/2610.17785v1) 的本地原文 `reference/literature/wei_yuan_2026_lstmp_v1.pdf`，第2–3页 §III-A–D、式(5)–(13)，第4页 §V-A。Mac 上传与本机下载的 SHA-256 一致：`dee35d773df47f984b2022c2b7be07a01e3d942cde8fae84830ac3a0bfd2f7dd`。原文5层独立网络；本方案10层共享网络是拟定改动，不说成原文设置。
- **NCSN++、残差块、条件嵌入、注意力**：L-STMP 第3页 §III-D、第4页 §V-A 和文献[18]指向 Song 等的 *Score-Based Generative Modeling through Stochastic Differential Equations*；具体结构核对 [作者 `models/ncsnpp.py`](https://github.com/yang-song/score_sde_pytorch/blob/main/models/ncsnpp.py) 的 `NCSNpp` 定义及其条件映射、ResnetBlock、AttnBlock 和上下采样。本方案64/128/256宽、16/8/4空间尺度、三个输出分支是本项目选择，不称作者原始默认配置，也不预先宣称优于 RefineNet。
- **协方差乘 score**： [Whitened Score Diffusion](https://arxiv.org/html/2505.10311v1) §3.1式(11)–(13)讨论对非各向同性 Gaussian score 作协方差预条件。本文采用加性 Gaussian 的特例 d=C_real grad log q=E[h|r]−r，含复协方差到实协方差的1/2因子；该恒等式也来自 `docs/THEORY.md` T7 的多元 Gaussian 推导。仅在匹配的 Gaussian 模型及理想训练解下成立，实际消息微调后的输出不自动具有精确 score 解释。
- **活动混合矩、Gaussian 外信息与阻尼**：Cai [JADCE v2](https://arxiv.org/html/2506.00581v2) §III-A、§III-B3、§V-B1；本项目原有 `THEORY.md` T3–T6b、T13–T17，及 `proposed/gaussian.py` 已有白化后的协方差谱截断。新设计把这些操作写明，均不声称为新公式或新稳定性定理。
- **近似联合分布和空间协方差输出**：本方案显式定义 q(a,X)=(1−p)delta_0 + p CN(mu,I_T⊗Sigma)，依该分布计算均值与协方差。该定义只保证参数化分布归一化与矩计算一致，不保证对应物理真实后验或同一个归一化先验密度；共享网络也不自动保证 score 与活动证据的导数恒等式。
- **Cholesky 因子和 Gaussian 负对数似然**：采用下三角 L、Sigma=LL^H+epsilon I，以及 log det Sigma+tr(Sigma^-1 EE^H)/T 的标准矩阵运算和 Gaussian 密度，不起新的方法名称。有限均值下拟合的是相对该均值的条件误差二阶矩，不能无条件称为中心后验协方差。

相关噪声预训练、权重共享、展开、活动混合及 NCSN++ 均已有来源或先例；本方案的贡献只能由针对 AFDM 实际消息与未知活动的独立配对验证建立，不以组件组合宣称已完成创新证明。

## Mac 五层候选的复核与后续取舍（2026-10-19）

上节十层共享及完整空间协方差设计属于已撤回默认选择的历史候选。当前评审对象为提交 fdaeec3cea7c6ee165c4ccf56c72897b2a7e3cef 的五层独立候选，完整记录见 docs/MAC_LSTMP_DESIGN_REVIEW_20261019.md。不以“结合两篇论文”宣称已实现其全部推导或已验证泛化。

来源核对：Cai [JADCE v2](https://arxiv.org/html/2506.00581v2)参考文献[24]与Wei [L-STMP v1](https://arxiv.org/html/2610.17785v1)参考文献[16]均指向Cai–Yuan–Zhang的 Score-Based Turbo Message Passing for Plug-and-Play Compressive Image Recovery。Cai §III-B3式(35)–(38)给出活动混合矩；Wei第3页§III-C式(12)采用残差方差，§III-D和第4页§V-A给出逐层联合训练与五层独立网络。

本项目的代数检查：在Mac的 tau=0.95*v*tanh((0.02*v*softplus(exp(b)*d/(0.02*v))+1e-6)/(0.95*v)) 参数化下，d≤0时tau/v的上限是0.95*tanh((0.02*log(2)+1e-6/v)/0.95)，v=1时约0.01386296。该范围限制由单调性直接得到，不是论文原定理。将正乘子移到正值化之后只是待验证的参数化修改，不命名为新算法。Gaussian匹配模型下，精确LMMSE残差满足每观测列 E||Y-A Xhat||²=(sigma_n²)²*tr((v0*A*A^H+sigma_n²*I)^-1)，解释了扣噪残差的负期望；它不证明实际AFDM消息为Gaussian或受监督接收机一定失败。

“正外信息精度”沿用Cai §III-A与§III-B3的Gaussian相除；本文仅计算固定方差比例q时均值扰动系数为1/(1−q)，不将其称为完整网络收敛界。五个分别训练的深度模型是深度消融；最终同一个五层网络的中间输出才可构成该网络的逐层恢复轨迹。实际消息微调后的score与直接监督活动logit不自动对应同一个先验密度，独立去噪和密度比消融的权重及定义须另行明确。本轮未修改Mac候选、重训或恢复正式实验。

## 五层独立候选的数值实现修订（2026-10-19，未训练）

实现与检查范围见 `docs/LSTMP_INTERFACE_REPAIR_20261019.md`。沿用 Cai §III-A 式(7)–(11)的 LMMSE 与 Gaussian 外信息、Wei 第2–3页 §III-B–C 式(8)、(11)–(12)的标量校准思路。以信息比例 η 和后验比例 f 分别求和，写成 z=exp(g)*f/η、v_query=v_a*z、r_query=m_a+(1+z)*Δ。**2026-10-19训练失稳复核纠正：仅 g=0 时与未校准 Gaussian 外信息等价；g≠0 时这是本项目对外信息方差比的校准，不等于 Wei 式(8)–(10)的后验方差乘法校准。** 当前公式等效后验比例为 exp(g)f/[η+exp(g)f]，Wei 原式则为 exp(g)f。既有权重不在本次文档修正中改变。正值化后的乘法校准和反馈比率的平滑上下限也属于本项目的参数化选择，不标为 Wei 原式或收敛保证。

24 项公式和接口检查、一次五层合成反向传播已通过；参数不更新。未完成预训练的 score 与未训练活动头的冻结前向记录只描述初始化，不能判断训练后的恢复稳定性。实际联合训练、独立性能验收及泛化验证均尚未完成。


## 现有一阶权重的五层联合微调（2026-10-19）

Wei–Yuan，arXiv:2610.17785v1，第 3 页 §III-D 给出预训练后与校准参数联合微调，以及逐层增加深度、联合优化已有层和新增层；第 4 页 §V-A 给出五层独立 NCSN++。原文未明确说五层均复制同一预训练检查点。本项目采用同一完成的 50,000 样本 RefineNet 一阶权重初始化各独立层，是已声明的实现选择；独立指参数不共享，不是把五层分别隔离训练。复数实坐标 score 的 v/2 系数保持原定义。具体协议与来源边界见 `experiments/lstmp_candidate_20261019/REUSE_50000.md`。此条不宣称新模型已经完成训练或稳定性验收。

## 活动分类与能量阈值的文献依据和冻结诊断（2026-10-19）

- **Class-probability estimation、density ratio estimation / 类概率估计、密度比估计**：Menon–Ong，*Linking losses for density ratio and class-probability estimation*，ICML 2016，[原文](https://proceedings.mlr.press/v48/menon16.pdf)，§2.2、§3–4。理想 logistic loss 解对应训练分布的后验 log odds，减去训练类别先验 log odds 后可换算为类别条件密度比；这个关系不保证 AWGN 训练的有限分类器在接收机真实消息上仍给出正确密度比。
- **User activity detection、binary cross-entropy、sigmoid / 用户活动检测、二元交叉熵**：Elkeshawy–Nafkha–Farès，*Deep Learning Based Approach for User Activity Detection with Grant-Free Random Access in Cell-Free Massive MIMO*，[arXiv:2406.07160v1](https://arxiv.org/html/2406.07160v1)，§III-B 式(10)、§III-C 式(12)、(15)–(19)。原文从接收信号预测用户活动，训练 sigmoid 分类器并选择判决阈值。它支持活动检测作为分类任务的做法，不是本项目逐用户 r、mu、v 特征或五个独立活动网络的直接来源；Wei 的 L-STMP 研究信道恢复，也不是活动分类器方案的来源。
- **Threshold-based detector / 阈值检测器**：Liu–Yu，*Massive Connectivity with Massive MIMO–Part I: Device Activity Detection and Channel Estimation*，[2018 原文](https://arxiv.org/html/1706.06438)，§III-C 式(19)–(22)、§III-D 式(24)–(27)、§III-E Definition 1。先用消息的二次型计算活动软概率，在标量噪声协方差时化为消息能量；最后以能量阈值作活动判决。原文假定独立 Rayleigh 信道、已知大尺度衰落及 AMP 对应等效 Gaussian 模型，渐近检测结论不能直接套用到本项目相关的 AFDM 信道张量。
- **Cai 论文与代码的活动公式**：[JADCE v2](https://arxiv.org/html/2506.00581v2) §III-B2 式(28)–(31)使用信道 Gaussian 外信息的均值与方差。作者[固定版本代码](https://github.com/chang-cai/score-massive-connectivity/blob/0c75680c966dcb8e46250de146f4c27e9294c283/main_stmp_jadce.py)中 `module_B` 调用 `lambda_post_gaussian`，后者将活动证据使用的信道均值设为零、方差设为 `var_h`，而非代入上文学习外信息；按代码代数整理是各天线能量的加权和。各天线消息方差一致时才进一步化为总能量阈值。该版本的归档、SHA-256 见 `references/known_phase_iteration_review_20260928/cai_code_provenance.json`，不概括为所有代码版本或论文原式。
- **ROC、AUC**：Fawcett，*An introduction to ROC analysis*，Pattern Recognition Letters 27 (2006) 861–874，[原文](https://www.math.ucdavis.edu/~saito/data/roc/fawcett-roc.pdf)，§3–4、PDF 第8页（期刊第868页）。本次 AUC 以正负样本成对排序概率计算，相等得分计半；同时报告固定校准规则的漏检与虚警，不用 AUC 代替某个运行阈值的性能。

使用本项目符号，若 H0: r~CN(0,v I_D)，H1: r~CN(0,(v+beta) I_D)，则 ell=(1/v−1/(v+beta))*||r||²−D*log(1+beta/v)，p=sigmoid(logit(rho)+ell)。这是上述 Gaussian 模型的密度代数，MAP 的能量阈值还含先验项 log((1−rho)/rho)；不把带此项的有限维阈值冒充 Liu–Yu Definition 1 的原式。能量统计量本身不要求 Gaussian 分布，但解析阈值和错误概率保证依赖模型；经验阈值仍须在其他场景上确认。推断中不能用真实活跃集合、真实每用户信道功率或真值选择阈值。

本次仅运行 `scripts/compare_activity_energy_readonly.py`，报告 `results/activity_energy_comparison_20261019/REPORT.json`。固定480个训练之外的验证场景，前240个校准阈值、后240个检查；后者有1801个活跃用户、10999个非活跃用户。该验证池已用于第一层检查点选择，因此这是开发诊断，不是封存测试。均采用已知相位和噪声、冻结第一层；同时保留原始预训练 score 和两轮微调 score 的全部对照，无优化器更新。

两轮微调第一层下，每种统计量独立选择全局阈值，使校准集虚警不超过1%，检查集结果为：消息能量/v 漏检96.78%、虚警1.01%；条件去噪均值能量/v 漏检62.30%、虚警0.98%；原预训练分类器 log odds 漏检50.08%、虚警0.78%；当前活动头 log odds 漏检47.14%、虚警0.85%。条件去噪均值在此指乘活动概率之前的 mu，避免把原分类器决策混入能量比较。另记录按24种条件分别定阈值的结果；对应能量/v 漏检47.92%、虚警0.97%，但使用更多阈值且没有证明跨条件泛化。所有统计量、两个权重状态、全部条件和样本均保存，未删不利场景。

旧分类器以默认零 log odds 阈值在该检查集全部判活跃，但重新选择阈值后仍具有区分能力；这支持检查实际消息下的概率与判决校准，不支持“完全没有信息”或“能量已优于分类器”的判断。硬判决阈值的改善不等于迭代内软活动概率已正确，后续仍需分别验证活动概率反馈和最终判决。训练保持暂停，原权重与检查点散列未改动。

## 第二层失稳诊断中的阻尼与来源（2026-10-19）

- **Damping、natural parameters / 阻尼、自然参数**：Hernández-Lobato等，*Expectation Propagation in Linear Regression Models with Spike-and-slab Priors*，[作者PDF](https://jmhl.org/wp-content/uploads/2014/12/papermachinelearning2014.pdf)，PDF第11页式(12)及第13页§4.2式(21)–(22)。近似因子的几何插值对应Gaussian精度与精度乘均值的线性插值。本文仅采用这一代数操作，没有复现该文的spike-and-slab EP完整算法或使用其收敛结论。
- **Adaptive damping / 自适应阻尼**：Vila等，[Adaptive Damping and Mean Removal for the Generalized Approximate Message Passing Algorithm](https://arxiv.org/pdf/1412.2005)，§2.1、Table 1的R12–R18及§2.2。该文使用相应MAP或MMSE Bethe代价判断是否减小步幅。本项目曾测试的二次代价 `||AX−Y||²+noise/(rho*beta)||X||²` 是项目代理目标，不等于该文MMSE Bethe代价，也不等于学习信道先验的负对数后验。该候选虽压住误差爆炸，但独立480场景AER明显恶化，验收失败，记录保留于 `results/lstmp_stability_development_20261019/`。

候选 `experiments/lstmp_message_damping_candidate_20261019/receiver.py` 只改变相邻层的Gaussian消息。记原消息为 `(m_old,v_old)`、未经阻尼的新外信息为 `(m_new,v_new)`、初始化方差为 `v0=rho*beta_training`，采用

`a=min(1,v0/v_new)`，

`1/v_damped=(1−a)/v_old+a/v_new`，

`m_damped/v_damped=(1−a)*m_old/v_old+a*m_new/v_new`。

后两式是上引论文的Gaussian自然参数阻尼；第一式是本项目明确提出的启发式系数，并非论文原式，也不是“后验方差不能超过先验方差”的定理。真实条件后验方差可以大于先验方差。这里用初始化方差作参考，只降低过大反馈方差所对应更新的权重；不把残差方差重新解释为精确后验MSE。当前层的score、活动logit和信道输出不受这一步直接修改，下一层因输入消息改变而可能产生不同输出。

`results/lstmp_message_damping_development_20261019/PLAN.json` 在生成新开发样本之前冻结候选与验收准则，240个均衡条件加240个K=100/Q=8/SNR=10dB场景均保留。第二层冻结权重下验收通过，但困难组漏检仍较多，且这不是最终五层模型或封存20场景结果。后续深度初始化、梯度和完整验证的结果另记 `results/lstmp_message_damping_resume_checks_20261019/`；零优化器更新的检查不能表述为重新训练完成。


## Cai 活动证据的冻结替换检查（2026-10-19）

继续采用上述 Cai §III-B2 式(30)的 Gaussian 活动证据。信道 Gaussian 外信息均值 e、复方差 c 与线性消息 r、复方差 v 满足 logit(p)=logit(rho)+||r||²/v−||r−e||²/(v+c)−D log(1+c/v)，D 是每用户复系数个数。式(26)–(27)的外信息要求活跃条件信道后验均值 mu 和对应方差 tau；有效 Gaussian 相除要求 0<tau<v，得到 c=tau*v/(v−tau)、e=(v*mu−tau*r)/(v−tau)。当前展开接收机的活动加权残差反馈方差并非这个 tau，不能直接替代。

固定作者代码 `lambda_post_gaussian` 使用 e=0、c=var_h；本轮保留这一特例，在本项目归一化下以训练库平均功率 beta=1.0004404181394917 代替原代码的 var_h=1。没有使用真实用户功率或选择阈值。候选 `experiments/lstmp_cai_activity_candidate_20261019/evidence.py` 通过独立复 Gaussian 密度、作者归档函数数值一致性和 Gaussian 消息相除检查。

开发协议在 `results/lstmp_cai_activity_frozen_20261019/PLAN.json` 生成场景前冻结：仅用已完成第三阶段的第三层检查点，在96个新种子场景上比较当前分类器、同一消息上的解析活动概率，以及各层均替换活动概率后的反馈链。保留相同 score、校准参数、残差方差和自然参数阻尼，统一阈值0.5，无优化器更新，使用CPU。它是当前已训练接收机的组件替换诊断，不是Cai全算法复现、最终五层对照，也不能据此证明重新联合训练的无分类器网络必然不可行。预留20场景输入不参与本轮。

## 增加展开层数与训练方式的文献依据（2026-10-20，建议未执行）

- **Layer-by-layer and denoiser-by-denoiser learning / 逐层训练与逐去噪器训练**：Zhu等，*Deep-Learned Approximate Message Passing for Asynchronous Massive Connectivity*，[原文](https://arxiv.org/pdf/2101.00651)，§IV-B、Algorithm 1，PDF第15–16页；多天线版本见§V-B、Algorithm 2。先固定前面层，学习新增去噪器，再联合更新已有去噪器，最后整体细化。该文把增加一次深度的阶段称为epoch，其内部训练迭代数由性能停滞条件决定，不能读成每层仅遍历一次数据。§VI、PDF第24页使用100,000个独立训练样本、5,000个验证样本和100的minibatch；其解析收缩函数和模型规模与本项目大型score网络不同，这些数值不直接迁移。
- **Learned score-based turbo message passing / 学习的基于得分的Turbo消息传递**：Wei–Yuan，[L-STMP原文](https://arxiv.org/html/2610.17785v1)，§III-D、§V-A。报告五层独立NCSN++，预训练score后按增加深度的方式与已有层、校准参数联合微调，采用中间层加权NMSE。文中未提供可复用的具体样本总数与逐阶段训练轮数，不能据此声称某个轮数序列是Wei的方案。该文为单用户HBF信道恢复，不是多用户GFRA。
- **Deep unfolding / 深度展开**：Sun等，*Deep-Unfolded Massive Grant-Free Transmission in Cell-Free Wireless Communication Systems*，[原文](https://arxiv.org/html/2502.13390v1)，§V-D式(45)、§VI-B。DU-ABC与DU-POEM使用10层，展开参数与软活动检测模块联合训练。其目标为活动加权的数据检测误差，原文明确没有直接优化信道估计误差；不是10个大型score网络，不能将其层数或开销当成本项目的性能保证。

本项目当前代码在每个深度阶段联合更新所有已有层。因此阶段轮数`[1,1,2,2,3,3,4,4,5,5]`对应30次训练池遍历，第一层参与30次、最后一层参与5次；它不是各层各自独立的累计训练轮数。保留当前五层后，再逐层增加至十层、先适配新增层再联合微调，是上述训练思路的项目候选实现，具体预算属于建议，未修改或启动当前训练。

另外，当前损失为`(L_last + 0.2*sum(L_earlier))/(1+0.2*(depth-1))`。从五层扩为十层时，最终层系数由1/1.8降至1/2.8，这是代码代数事实，不是原实现错误。若希望保持最终输出与全部辅助输出的相对权重，可令辅助项每层系数为`0.8/(depth-1)`（depth>=5）；这是本项目待验证的权重选择，不是上述论文规定。当前最后一层反馈方差的校准参数只影响送往下一层的消息，而该消息尚无后续输出损失；增加下一层后，这一连接也需要适配。该结论来自冻结`message_damping.py`第31–43行与`receiver_base.py`第155–160行的计算图，不代表当前五层训练失败。

建议与开销推算保存在`results/lstmp_depth_budget_review_20261020/REVIEW.json`。依据仅为训练、验证及实现检查；已揭示的配对测试样本不用于选择新超参数。既有五层第5、6轮续训及配对确认仍遵循原授权，十层方案未获执行授权。

## L-STMP复杂度倍数与本机实测时长的区别（2026-10-20）

Wei–Yuan [L-STMP](https://arxiv.org/html/2610.17785v1)，§V-B、Table I（本地归档PDF第5页）比较score前向次数与FLOPs：STMP为100次迭代、200次score前向，五层L-STMP为5次，约40倍；相对2000步DPS则约400倍。这是论文中的推理复杂度比较，不是本机墙钟时间测量。

本项目`results/lstmp_epoch6_vs_legacy20_20261020/SUMMARY.json`的410.407倍来自46.9902秒/0.114497秒；旧算法20场景均到600次迭代上限，每场景一阶、二阶与分类器各600次调用，新算法分别为5、0、5次。两者的算子实现、网络开销与停止预算不同，不能将实测时间倍数完全归因于展开层数，更不能宣称等精度加速；本批新算法汇总NMSE差2.253 dB。将深度加倍时推理耗时近似加倍只是尚未实测的量级估计，不是精度改进保证。增加微调轮数改变离线训练成本；新增经过训练的展开层才增加单次推理计算。当前实验和冻结配置均不因这一解释而修改。

## Cai 的信道与活动去噪、训练梯度和推断反馈（2026-10-20）

本条为原文和源码分析，不改变接收机、权重或正在运行的训练。

| 原文术语或操作 | 来源与位置 | 本项目解释边界 |
|---|---|---|
| Denoiser of H_k；conditioning on the active case / 信道去噪器；以活跃情形为条件 | [Cai v2](https://arxiv.org/html/2506.00581v2#S3.SS2.SSS1)，§III-B1式(15)–(23) | 式(15)含与H无关的非活跃项；原文明确以只保留活跃项得到式(16)的Gaussian消息作为近似。不能把该近似说成完整联合后验的无条件恒等式。信道均值对应活跃分支，不能把非活跃用户的有效信道零标签直接当作该分支的干净H标签。 |
| First-order score matching；second-order score matching / 一阶、二阶得分匹配 | [Cai v2](https://arxiv.org/html/2506.00581v2#S4)，§IV-B式(46)–(49)、§IV-C式(50)–(54)及式(54)后段落 | 训练对象是Gaussian扰动的物理信道先验，不是活动加权信道的混合先验。原文明示先训练并冻结一阶网络再训练二阶网络，或同时训练但禁止二阶目标向一阶网络反传。原文没有神经活动分类器和活动BCE到score的联合训练。将这一分工扩展到本项目新增分类器是设计判断，不是原文规定该分类器的训练方式。 |
| Denoiser of alpha_k；posterior probability of activity；binary decision / 活动去噪器；活动后验概率；二元判决 | [Cai v2](https://arxiv.org/html/2506.00581v2#S3.SS2.SSS2)，§III-B2式(28)–(31)、Algorithm 1第9–17行、Algorithm 2 | 式(30)用输入Gaussian消息和信道外信息计算解析软活动概率。每轮更新软概率并以式(35)–(38)形成活动加权均值与方差，式(41)–(42)反馈到下一轮；终止后做硬判决。因此“在本轮信道去噪之后更新活动概率”与“整个推断结束才使用活动信息”不同，后者不是该算法。 |

作者[固定提交0c75680的main_stmp_jadce.py](https://github.com/chang-cai/score-massive-connectivity/blob/0c75680c966dcb8e46250de146f4c27e9294c283/main_stmp_jadce.py)的`module_B`在`eval`与`torch.no_grad()`下调用两score网络。其`lambda_post_gaussian`另设信道外信息均值为0、方差为`var_h`，没有使用同轮计算的score外信息；这是式(30)的Gaussian先验特例，不能混称原文的一般信道外信息实现。已归档源码及哈希见`references/known_phase_iteration_review_20260928/cai_code_provenance.json`。

对简化局部模型r=aH+w，固定噪声参数且a与H独立时，令q1(r)=p(r|a=1)、q0(r)=p(r|a=0)。直接由Bayes公式得p=P(a=1|r)=rho*q1/[(1-rho)*q0+rho*q1]、mu=E[H|r,a=1]、E[aH|r]=p*mu，协方差为p*Sigma+p*(1-p)*mu*mu^H。这里mu与p是不同条件量；上述精确局部恒等式不等于宣称Cai式(30)的Gaussian外信息近似恢复了精确q1，也不证明AFDM实际查询满足独立Gaussian噪声。

五层冻结源码`D:/afdm-gfra-cpu/runs/lstmp_refinenet_50000_epoch6_20261020/source_code/experiments/lstmp_candidate_20261019/`中，`message_damping.py`第33–35行将未截断梯度的条件均值输入活动网络，并以p*mu输出；`receiver_base.py`第155–160行使用有效信道NMSE与0.1倍BCE。因而BCE可以经同层mu及前层消息影响score，NMSE也可以影响活动网络。这是本项目的端到端训练选择，不是Cai的训练流程；存在梯度路径不等于已经证明该路径损害性能。只截断同层mu不能切断经r、v到前层score的路径；仅停止BCE反传也不能让已被有效信道NMSE微调的网络自动恢复先验score含义。严格保持一阶score定义需要保留其得分匹配目标或冻结相应网络；实际消息上的活跃条件均方误差训练只能说明相应条件均值回归，不能自动沿用Gaussian先验score解释。

建议中的梯度控制对照与分阶段训练均尚未执行。此前96场景的三层冻结解析活动替换检查是不同问题：它更换了推断规则，没有隔离BCE到score的训练梯度，不能用其失败否定分离训练，也不能据本文直接采用该解析替换。

## Cai、Wei 与 GFRA 深度展开的综合取舍（2026-10-20，研究建议）

本节记录文献依据与待检验设计，不替换冻结主线，不表示已实现、训练或优于现有接收机。

| 原文术语及来源 | 核对位置 | 对本项目的适用范围 |
|---|---|---|
| channel denoiser、activity denoiser、moment matching；Cai 等 [STMP-JADCE v2](https://arxiv.org/html/2506.00581v2) | §III-B1–3，式(22)–(42)；§IV，式(44)–(56)；Algorithm 1–2 | 保留活跃条件信道与活动概率的分解，以及活动加权的一、二阶矩。论文的消息投影有近似；不能将矩公式本身当成本项目创新，也不能由此保证有限维 AFDM 查询为白 Gaussian 噪声。 |
| learned score-based turbo message passing；Wei–Yuan [L-STMP v1](https://arxiv.org/html/2610.17785v1) | §III-B–D，式(8)–(13)；§V-A | 借鉴有限深度、逐层训练及消息参数校准。原文为单用户信道恢复，采用独立 score 联合微调和残差方差；本项目若共享/冻结网络或改用条件方差，须明确是项目选择。原文实验不能证明任意 GFRA 五层充分，也没有涵盖未知活动的混合方差。 |
| analytic learned proximal gradient method (ALPGM)、ALPGM with momentum (ALPGM-MM)、adaptive-tuning；Zou 等 [Proximal Gradient-Based Unfolding for Massive Random Access in IoT Networks](https://arxiv.org/pdf/2212.01839) | §III-A，式(13)–(15)，PDF p.8；§III-B，式(16)、Theorem 1及其后限制说明，pp.9–11；§III-C，式(29)–(32)，pp.11–12；§IV-D，Fig.9，pp.18–19 | 该文先依导频计算线性矩阵，再学习少量逐层参数，并检查活动率/SNR失配。支持把结构化计算与学习职责分开，而非必须把全部线性矩阵和大网络自由训练。其收敛结论依赖互相干性、稀疏度及参数条件，不能移植为本项目保证；不直接把其动量项添加到 Gaussian 外信息。 |
| trainable soft-output active user detection、joint training；Sun 等 [Deep-Unfolded Massive Grant-Free Transmission in Cell-Free Wireless Communication Systems](https://arxiv.org/html/2502.13390v1) | §V-C，式(43)–(44)；§V-D，式(45)及随后说明；§VI-D | 作者明确从分开训练转向联合调节展开参数与活动模块，目标为活动加权数据估计误差，且说明未直接优化信道估计。其模型没有需保持独立先验含义的 score。它反驳“活动判别梯度原则上不能参与接收机训练”的普遍断言，但不能证明应让 BCE 修改本项目一阶 score。 |

当前建议以 Cai 的分解组织每层：一般 AFDM 算子的 Gaussian 线性更新及外信息，随后得到活跃条件均值 mu、条件误差方差 tau_H 与软活动概率 p，再形成 Xhat=p*mu 和混合方差，最后作 Gaussian 外信息及受约束的阻尼。对每用户 D 个复系数，条件协方差 Sigma_H 的迹投影为 tau_H=tr(Sigma_H)/D，联合标量方差为 p*tau_H+p*(1-p)*||mu||^2/D；若下一线性模块需要共同方差，再对用户平均。首版不因此增加完整协方差网络。网络矩只是近似；实际消息上的误差二阶矩训练也不自动得到真实后验协方差。

优先复用同一套预训练信道先验及配套条件方差，跨层共享，在独立训练场景中学习活动证据与少量逐层消息参数。实际消息中的相关、信号相关误差已有历史诊断，故仅冻结旧网络不是充分修复；活动分支需在当前接收机生成的同层查询上适配，不能只训练白噪声查询，也不能只用统一温度改变已有错误排序。先验 score 的冻结是首版可控设计，不是文献规定或永久限制；如需适配信道均值，应由活跃条件信道重建目标驱动，并重新配套训练方差，明确其为任务去噪映射而非自动保有精确先验 score 含义。

训练职责建议分开：一阶 score 预训练用 DSM；配套方差训练冻结一阶；活动分支以 BCE 学习，截断其训练样本的 r、v、mu 到信道网络的路径；有限层闭环训练可联合优化消息参数，并同时评价有效信道误差与活动损失。冻结网络参数不等于在闭环中关闭对输入的自动求导，消息参数仍可通过固定网络的输入获得梯度。可选后续信道微调采用条件重建与 DSM 约束，BCE 不更新信道网络参数；仅截断同层 mu 不足以阻断跨层路径。以上是项目训练取舍，不是 Cai 或 Wei 的原训练流程。

恢复活动混合方差需要与当前均值配套的条件方差，不能给现有总残差方差直接再加活动项，也不能把旧二阶网络直接接到已联合微调的五层均值。正外信息精度所需的投影/限制应与原始预测分开记录：非 Gaussian 后验逐样本方差不必小于输入方差。共享网络只减少参数存储与拟合自由度，并不减少同深度网络调用次数或保证泛化。展开深度待同观测、同训练数据与预算的对照选择；比较含二阶网络与不含二阶网络的方案时同时报告实际耗时和调用次数，不只比较层数。

优先次序是固定五层分别核对训练梯度职责和条件/活动混合方差，再对通过的候选增加深度；这些控制对照用于区分原因，完整推荐方案仍须独立测试。现有五层逐层输出不是独立深度消融，六层一次适配验证不是深度单因素实验。参见 `results/lstmp_five_layer_diagnosis_20261020/ANALYSIS.json`，以及本文件已有实际活动证据、查询误差和解析活动替换的失败记录。最终选择同时依据 NMSE、漏检率、虚警率、AER 和推断成本，不能只按混合验证损失下降切换主线。

进一步明确方差网络的必要性：GFRA 比 Wei 的单用户恢复多出未知活动和用户间干扰，这加强了处理活动不确定性及实际消息失配的理由，但不能推出每层必须额外运行完整二阶 score 网络，更不能推出每层需要独立权重。上文配套条件方差网络是待比较的候选，不作为已证明必要的默认结构。当前建议先保留残差校准参照，优先检验少量校准参数或利用现有特征的小型方差输出分支；若输出条件方差，则以已有 p、mu 解析组合活动混合项；若输出总误差方差，则不再重复相加。小分支同样只是项目候选，其充分性尚未验证。

当前 `experiments/lstmp_message_damping_candidate_20261019/receiver.py` 第33–43行中，活动头读取 r、v、mu、rho，本层反馈方差在活动概率与均值之后计算。因此固定本层查询和均值时，仅替换反馈方差不会改变本层 AER，只能影响后续层。终层若不输出不确定性、也不再用方差更新活动概率，则没有必要为未使用的反馈额外执行方差网络。此判断不适用于 Cai 式(30)那种直接依赖条件外信息方差的解析活动更新。

完整二阶网络只有在同训练数据、同验证规则的控制对照中，相对于轻量方案呈现可重复的 NMSE/漏检/虚警收益，且实际推断开销可接受时，才有理由进入默认接收机。若考虑两套同量级主干，网络前向开销会明显增加，但不能未经计时声称整个接收机耗时恰好翻倍；共享权重只减少参数存储，不消除逐层第二次网络计算。旧算法与五层模型同时改变迭代数、均值、活动、方差及训练，现有对比不能把旧算法优势归因于其二阶网络。

## 二阶 score、条件误差估计与活动分类器的统一取舍（2026-10-20）

这三个对象须区分：二阶 score 对应平滑信道密度的对数 Hessian 或其迹；一般方差回归可拟合相对有限均值估计器的条件平方误差；活动分类器预测后验活动概率，平衡训练且分布匹配时可通过 odds 转换估计密度比。依据分别为 Cai §IV-A–C式(44)–(54)、本项目 `scores/direct_objectives.py` 的冻结一阶迹损失，以及本文件已有 Menon–Ong §3式(6)–(8)。有限一阶网络下，当前二阶迹目标的方差读出具有条件误差回归含义，不能自动把每个网络输出解释为真实 Hessian 元素。

单次查询的条件均值与方差一般不决定活动所需的边际似然值。直接计算的合成反例：实噪声方差为1，r=0，活跃先验分别为 N(0,1) 与 (1/3)N(0,1/4)+(2/3)N(0,4)。两者的活跃条件均值均为0、方差均为0.5，但活跃观测密度分别为0.2820947918与0.2378832155；取rho=0.5及不活跃观测N(0,1)，活动后验分别为0.4142135624与0.3735453700。本轮只作直接解析数值核算，不是AFDM实验。此结论只涉及单点矩；不否认完整精确score函数结合积分与归一化可以确定密度。Cai式(26)–(30)通过Gaussian外信息近似获得可计算活动规则，不是任意非Gaussian先验下由单点矩恢复精确边际似然的恒等式。

不保留独立二阶网络时，也可考虑由均值求导估计方差：在固定实Gaussian噪声协方差 sigma^2 I 及精确条件均值下，每实坐标平均方差为 sigma^2*tr(J_mu)/d。来源为 [Dytso–Poor–Shamai作者稿](https://arxiv.org/pdf/2104.01883)，§IV Proposition 1式(22)，PDF p.5（原作者Jacobian索引约定与项目相反，标量噪声下不影响迹）。复方差v对应sigma^2=v/2，平均复方差为v*tr(J_mu)/(2D)，D为复维数。随机迹估计/自动微分沿用本文件已有D-AMP与Jacobian条目；其计算并不免费，实际任务微调映射的导数也不自动等于其条件MSE，故本轮不将其直接指定为生产替换。

当前研究建议保留活动概率和条件误差两种输出功能，优先研究小型条件误差输出分支，暂不恢复每层一套完整二阶score主干。若将任何学习的方差输出分支称作方差网络，那么该建议属于“两种分支都保留”，不能表述为完全取消方差网络；若只能保留一个独立辅助网络，优先保留活动分类器，方差采用残差校准或经验证的导数估计。完整二阶score加分类器继续作为独立对照，是否值得保留由配对性能与实际开销决定。

小型条件误差分支可读取同查询r、v、mu及已有特征，输出每用户正标量tau_H。候选训练在活跃样本上固定/停止梯度通过mu和信道特征，令e=||H-mu||^2/D，最小化log(tau_H)+e/tau_H；该目标对给定输入特征的总体最优值为E[e|features,a=1]。这属于标准Gaussian负对数似然的标量形式，不保证误差Gaussian；有限均值下输出是条件风险而非必然为中心后验方差。防止方差损失改变均值的依据沿用 [Stirn等AISTATS 2023](https://proceedings.mlr.press/v206/stirn23a.html) §2 Proposals 1–2及式(5)，不借用其定理保证本项目全训练过程。再以p*tau_H+p*(1-p)*||mu||^2/D形成用于Gaussian投影的联合方差近似；不可给现有总残差方差直接追加活动项。真实消息训练、跨条件验证、分支容量与原始/投影后方差均需另外检查，尚未实施。

冻结epoch6五层源码的ActivityHead由三层卷积及两层全连接组成，直接按参数形状计数为78,433；结合配对汇总中五层总参数163,268,820以及每层3个校准参数，可得每层score为32,575,328参数，活动头约为其0.2408%。这不是运行时间占比。源码位于 `D:/afdm-gfra-cpu/runs/lstmp_refinenet_50000_epoch6_20261020/source_code/experiments/lstmp_candidate_20261019/receiver_base.py`，总数见 `results/lstmp_epoch6_vs_legacy20_20261020/summary.csv`。删除现有小型分类器并保留同量级二阶主干，不能直接视为有利的复杂度交换。

解析活动替换的已完成证据仍仅为96场景、冻结三层模型、e=0及训练先验功率c=beta的Gaussian特例：原分类器AER=5.3716%，同消息替换=9.5777%，反馈全替换=11.3007%。它不包含配套二阶矩的Cai一般活动更新，也没有重新训练，因此支持保留学习活动分支作为优先候选，但不能据此否定完整Cai方案。当前综合建议没有切换冻结主线或启动新训练。

## 残差方差与 Wei 的差异及困难场景归因（2026-10-20）

来源为 [Wei–Yuan 原文](https://arxiv.org/html/2610.17785v1) §III-B 式(8)–(10)、§III-C 式(12)、§III-D 及 §V-A；实现以 `D:/afdm-gfra-cpu/runs/lstmp_refinenet_50000_epoch6_20261020/source_code/experiments/lstmp_candidate_20261019/receiver_base.py` 和 `message_damping.py` 为准。Wei 的扣噪残差主体为 d=(||Y-B*Hhat||_F^2-M*Nsc*sigma^2)/(Nsc*||B||_F^2)，输出 beta*d。当前接收机采用同类归一化，但估计对象是 X=aH、均值为 p*mu，并将 d 先经温度 t=0.02v 的 softplus 正值化，再乘 beta，随后限制 tau/v<0.95，最后作外信息及自然参数阻尼。原文式(12)没有给出这些附加映射；不能据此断言作者代码一定没有其他数值处理。softplus 在较小正残差时同样改变结果，故不只是负数保护；上限和阻尼也不保证统计校准或收敛。

线性模块的差别独立于上述残差替换：设入射方差为 w、未校准 LMMSE 后验方差比例为 f，则本项目 query 方差为 w*gamma*f/(1-f)，Wei 式(8)–(10)为 w*gamma*f/(1-gamma*f)，后者要求 gamma*f<1。只有 gamma=1 时二者一般等价。前者是另外一种正值参数化，不能仅因与 Wei 不同判为公式错误；两种方案需要各自训练，不能直接搬用学到的 gamma 或据固定权重替换的损失判定优劣。一般 AFDM 算子使用奇异值计算 LMMSE，而 Wei 的闭式以 BB^H=I 为条件；测量算子的差别本身也不证明需要额外方差网络。

本轮仅重算既有1200场景、24条件记录，未运行网络前向、训练或更改阈值，源文件 SHA-256 与逐条件逐层统计见 `results/lstmp_five_layer_diagnosis_20261020/RESIDUAL_WEI_REVIEW.json`。K=100、Q=8、rho=0.1、SNR=10 dB 的50场景，前四层原始残差方差全部非负，但第2至3层AER由7.42%升至9.40%，末层8.78%；这排除该组退化由负残差触发的解释，不排除正残差估计有偏。全1200场景中，前四层只有第3层1个场景的反馈比超过0.5及0.9，不能把整体AER平台直接解释为普遍触及0.95上限。末层反馈在最终判决之后计算，不能用其682个负残差场景直接解释本层错误。

训练侧的直接证据为五层阶段 epoch5 至6：验证混合损失0.25811046降至0.25607751、pooled NMSE由-4.89087167 dB改善至-4.97399263 dB，但AER由5.2203125%升至5.9296875%，末层BCE由0.12254419升至0.14187587。各场景等权的训练/验证混合损失与按用户汇总的AER也有不同权重：K=100的两类配置占400/1200场景，却占40000/64000用户判决。这些事实支持优先核对训练目标、梯度路径及选模规则，不证明BCE系数0.1必然过小，也不证明联合训练在原则上错误。有限均值网络下，Xhat=p*mu 的重建误差允许p与mu相互补偿；这是该分解的代数性质，不是已测得的具体错误机制。

因果结论需收紧：此前优先研究小型条件方差分支是架构候选，不是由现有失败证据支持的必需修复。当前应保留残差方案作为对照，先在固定深度、同数据与验证规则下分别核对分类训练及消息参数化，再比较简单方差校准和方差网络。单用户恢复同样有压缩零空间和估计误差与观测噪声相关的问题；GFRA 增加活动不确定性不能自动推出必须添加网络。基于真值的实现误差反馈只能作为诊断，既不是可部署估计，也不保证构成性能上界；被冻结权重上的单次替换还会改变其输入分布。当前没有足够控制实验将困难场景AER的主要原因归于方差、消息或训练中的任意一项。

## 从联合后验到训练目标的推导记录（2026-10-20）

独立研究方案见 消息推导及训练目标（历史路径，见迁移记录：`paper/DU/docs/LSTMP_DERIVATION_AND_TRAINING_20261020.md`），不改写已冻结主线。复用 `THEORY.md` 的工作后验、Gaussian 条件化和局部混合矩，补齐新五层的校准、残差和训练风险解释。Gaussian projection、moment matching、expectation propagation、extrinsic message 仍分别采用 [Minka 2001](https://tminka.github.io/papers/ep/minka-ep-uai.pdf) §2式(5)–(6)、§3式(8)–(10)，以及 Cai §III 的用法；本项目各向同性协方差投影、自然参数阻尼和正精度约束逐式写明，不宣称全局收敛。

score、Tweedie formula、denoising score matching 的依据为 [Cai v2](https://arxiv.org/html/2506.00581v2) §IV-A–C；Jacobian 与条件协方差的依据为 [Dytso–Poor–Shamai作者稿](https://arxiv.org/pdf/2104.01883) §IV Proposition 1式(22)。固定复噪声方差v时，实坐标c=v/2、mu=u+c*s，Cov_R=c*J_mu，平均复方差为tr(Cov_R)/D。活动log odds满足grad ell=mu/c，并由乘积求导得到c*J_(p*mu)=p*Cov_H,R+p*(1-p)*mu*mu^T；这一直接推导已在历史 `proposed_probability_consistency_20261016/DERIVATION.md` 中出现，不作为新方法名称或已验证接收机改进。对v(Y)连同整条迭代求总导数不能冒充固定v的恒等式。

训练目标使用既有 BCE/logistic loss、conditional mean、conditional mean-squared error、Gaussian negative log density 等含义。BCE条件最优概率及密度比换算沿用 [Menon–Ong](https://proceedings.mlr.press/v48/menon16.pdf) §3式(6)–(8)、§4.2式(16)–(17)。固定训练功率归一化的活跃条件平方误差以E[H|z,a=1]为最优值；真值相关权重w(X)的平方误差则以E[wX|z]/E[w|z]为最优值。D28是直接完成平方的结果，不宣称某论文已证明本任务的NMSE损失不合理；若选择相对误差为任务目标，只需承认其估计器一般不同于MMSE条件均值。

对方差分支的解释进一步收紧：相对有限mu的条件MSE包含均值偏差平方。将它代入p*tau_H+p*(1-p)*||mu||^2/D，只定义一个近似混合分布的方差，一般不等于真实联合条件误差。D18解析例取p=0.3、真实条件均值2、条件方差0.5、有限均值1，代入结果0.66，实际p*mu估计器条件误差1.08。它不否定原Gaussian拟合近似，但排除把风险与中心协方差无条件互换的解释。现有残差参数也可通过固定估计器的总误差标签校准；数学不要求增加网络。

联合后验分解不自动规定梯度是否截断。D30用Bernoulli负对数概率加活跃条件Gaussian负对数密度，说明理想函数空间内可以同时得到活动概率、条件均值和中心方差；有限容量、共享特征与任务权重仍需实证。先固定score再训练分类器是保持定义和隔离影响的研究策略，不是“联合训练原则上错误”的定理。真实消息上的条件风险训练与Gaussian先验score预训练必须分开解释。

确定性合成核验初轮共20项，全部通过；后续补入混合 score 与校准位置核验，共22项，见下文。程序 `scripts/check_lstmp_derivation_20261020.py`，当前结果及程序SHA-256为 `results/lstmp_derivation_20261020/MATH_CHECKS.json`。其中差分导数使用显式步长及2e-8/2e-6容差，代数恒等式按双精度比较。没有运行AFDM接收机、网络训练或新增性能评测，核验不能证明AER收益、收敛或分支必要性。

## Adam 的偏差修正与部分参数解冻（2026-10-20，只读诊断）

**Adam；bias correction / 偏差修正**：Kingma–Ba，*Adam: A Method for Stochastic Optimization*，[原文](https://arxiv.org/pdf/1412.6980)，Algorithm 1、§2.1（PDF第2–3页）及§3。Algorithm 1定义一、二阶矩及基于步数t的偏差修正；§2.1讨论此前梯度为零、当前梯度非零时的更新幅度。不得将本项目的部分参数屏蔽实现命名为论文中已有的新优化算法。

本项目六层适配使用单个三元素校准参数向量和梯度掩码 `[0,0,1]`。前两元素的矩为零，但共享向量的Adam步数已累计4800次。相同betas=(0.9,0.999)，忽略epsilon时，解冻后第一次非零梯度的更新幅度相对新建Adam首次更新为 `(1-beta1)*sqrt(1-beta2^4801)/(sqrt(1-beta2)*(1-beta1^4801))`，约3.149。三标量CPU核算记录于 `results/lstmp_depth6_readonly_analysis_20261020/REPORT.json`；这不是实际接收机更新幅度的测量，也未证明其造成验证性能退化。对应实现为冻结 `extension.py` 第34–66行。六层检查点选择、七层训练源码、配置和权重均未因本分析改变。

## Wei 展开训练与 Cai 联合活动后验的对应（2026-10-20）

**逐层训练、联合微调、每层独立 score 网络**：采用 [Wei–Yuan v1](https://arxiv.org/html/2610.17785v1) §III-D 的 “trained progressively layer by layer”“each new layer trained jointly with the preceding layers”，以及 §V-A 的 “each with an independent NCSN++ score network”。本项目保留 AWGN 信道先验预训练、每层独立参数和接收机内任务微调；此前固定 score、跨层共享或先单独校准反馈的建议属于可选对照，不作为这一训练路线的前提。独立参数与相同预训练初始化并不矛盾。

**有效信道及活动混合矩**：依据 [Cai v2](https://arxiv.org/html/2506.00581v2) §II-B 式(5)、§III-B 式(35)–(38)，估计对象为 X=aH。固定局部 Gaussian 查询 r=X+w、复噪声方差v，实坐标c=v/2，由 q_X=(1-rho)q_0+rho*q_1 直接求导得到 s_X=p*s_H-(1-p)*r/c，因而 r+c*s_X=p*(r+c*s_H)。这是文档 G1 的直接代数推导，与 Cai 混合均值一致，不命名为新的既有方法。

Wei 式(11)的校准推广需说明位置。G2 采用先校准条件均值再按活动概率组合，即 p*(r+alpha*c*s_H)。若改成对整个混合 score 乘alpha，则多出 (1-alpha)*(1-p)*r，见 G3。理想活动模型退化为始终活跃时，应相应固定p=1；再取单用户、行正交算子及一致的校准定义，恢复 Wei 的模块形式。现有代码的gamma外信息参数化不同，不能因训练框架相同便声称全部公式相同。

Cai 式(30)使用 Gaussian 外信息计算活动概率；本项目活动分类器是对局部后验概率或证据的学习近似。保留分类器并沿用 Wei 式(12)的残差反馈是待验证的最小展开基线，不是 Cai 原论文的完整复现。残差要用有效信道 Xhat=p*mu 计算；若它作为总反馈尺度使用，不再额外重复相加 p*(1-p)*||mu||^2/D。使用 Cai 的理论混合方差则需要另行计算配套的条件方差，不能由任务差异直接推出独立二阶网络的必要性。

训练目标由 Wei 的逐层相对重建误差推广为有效信道 NMSE 与活动 BCE；D31 明确给出场景和用户权重。这是本项目多任务目标，既不是 Cai 的原训练配方，也不由 Wei 的单用户实验保证其最优性。Wei 没有活动头，所以 BCE 是否更新 score 仍是需要配对检验的梯度选择；阻断该路径并不等于冻结 score 的重建微调。任务微调后允许网络适配实际查询，不继续无条件赋予其精确 AWGN 先验 score 的含义。

更新后的 推导及训练方案（历史路径，见迁移记录：`paper/DU/docs/LSTMP_DERIVATION_AND_TRAINING_20261020.md`） §4.1、§9 记录上述关系。确定性数学核验22项全部通过；新增混合 score 检查以数值差分对照显式混合密度，校准位置检查覆盖p=0、p=1及中间概率。不包含接收机性能实验。

## 展开接收机训练协议与统计权重（2026-10-20）

具体训练方案（历史路径，见迁移记录：`paper/DU/docs/LSTMP_TRAINING_PROTOCOL_20261020.md`） 延续上述 Wei 的逐层联合训练、独立 score 网络及 Cai 的有效信道混合结构。首版五层、保留活动分类器与残差反馈；预训练与接收机微调分阶段，后者的默认方案允许所有任务梯度更新 score。阻断活动 BCE 到 score 参数的路径作为独立对照，不把这种对照描述为 Wei 或 Cai 的既定训练方法。

BCE 沿用本文件已有 Menon–Ong §3、§4.2 的 logistic loss 含义。按用户汇总的训练目标为 sum(BCE)/sum(K)；均匀抽取单场景时，将该场景的平均用户 BCE 乘 K/mean(K)，其期望梯度对应此数据集目标。这是有限和的直接重排，不是新方法名称。当前4800训练场景恰为24条件各200场景，mean(K)=160/3，因此K=20/40/100的乘数为0.375/0.75/1.875；开发验证的1200场景为24条件各50场景。来源为冻结五层MANIFEST中的实际索引，只读核对未生成新场景。

活动优先的检查点选择是本项目任务取舍：在当前深度平均场景NMSE距最佳值不超过0.3 dB的检查点中选择最低pooled AER；0.3 dB是事先声明的重建容差，不是文献结论或统计显著性界限。阈值0.5、初版BCE权重0.1、前层监督权重0.2及学习率与轮次均有明确配方；除Wei已报告的层监督权重外，其余数值不借论文名义声称最优。

该协议尚待独立训练入口实现，没有启动训练。理论恒等式通过核验、工作后验具有明确假设与真实接收机达到性能目标是三个不同层次；22项数学核验不证明五层足够、残差估计精确或联合梯度必然优于分开的梯度。

## 活动分类损失与 score 联合训练的文献依据（2026-10-20）

完整来源、章节、公式和适用边界见专题调研（历史路径，见迁移记录：`paper/DU/docs/LSTMP_CLASSIFIER_SCORE_TRAINING_REVIEW_20261020.md`）。本次仅补充研究文档，没有训练或新增接收机性能结果。

- **Soft-output active user detection／软输出活动用户检测、分别训练与联合训练**：采用 Sun 等 [ISWCS 2024 作者稿](https://arxiv.org/html/2312.12874v2) §III-B–C 式(21)、(24)–(25)，以及其 [2025 扩展稿](https://arxiv.org/html/2502.13390v1) §V-C–D 式(43)、(45)。前者分别使用数据重建误差与活动 BCE，后者采用活动加权数据重建误差共同训练；不得把后者误记为本项目的 NMSE＋BCE。
- **Energy-based model／基于能量的模型、联合分类与 score 学习**：依据 Guo 等 EGC，[ICCV 2023 官方页面](https://openaccess.thecvf.com/content/ICCV2023/html/Guo_EGC_Image_Generation_and_Classification_via_a_Diffusion_Energy-Based_Model_ICCV_2023_paper.html)及[作者稿 v3](https://arxiv.org/html/2304.02012v3) §3.2 式(14)–(17)、Algorithm 1。共同参数化概率模型的做法不同于两个任意输出头相加损失。
- **Classification-Denoising Networks**：Thiry–Guth [2024 v1](https://arxiv.org/html/2410.03505v1)，§3.3 式(13)为 CE＋DSM，§4.1 Table 1 提供同架构单任务与联合训练比较。该版本按预印本记录，不根据投稿抬头宣称会议录用。具体数值与适用范围见专题调研。
- **Denoising Likelihood Score Matching，DLSM**：Chao 等 [ICLR 2022 原文](https://arxiv.org/html/2203.14206v1)，§4.1–4.2 式(10)–(11)、Fig. 2，先训练 score，再固定它训练分类器。**Classifier guidance／分类器引导**涉及分类器对输入的梯度，不等同于分类损失对 score 参数的梯度。
- **Score Calibration loss**：Huang–Chen–Lin [NeurIPS 2022 Workshop on Score-Based Methods 原文](https://www.csie.ntu.edu.tw/~htlin/paper/doc/wssbm22cond.pdf)，§3–4 式(3)–(5)、Fig. 1、PDF 第2–3页。该名称仅对应原文对分类器能量导数的训练目标，不用于命名本项目的残差校准或活动概率阈值调整。
- **Soft-output joint channel estimation and data detection**：Song 等 [2021 作者稿](https://arxiv.org/html/2112.00330v1)，§IV-A–B 式(23)–(24)，以比特 BCE 训练展开参数的超网络。其检测对象是数据比特，不可当作活动 BCE 或 score 网络的直接实验。

专题调研中的按损失选择参数梯度，是本项目消融的精确定义，不赋予新的方法名称。阻断 BCE 更新全部 score 参数仍保留重建损失、活动混合与跨层反馈；数学后验耦合并不决定训练时必须采用哪一种梯度选择。Wei 的单用户微调和 Cai 的二阶损失截断均不足以单独决定这一问题。

进一步的条件风险核对见专题调研 §6，沿用本文件既有 conditional mean、squared error、BCE 与 KL divergence 的含义。固定查询与普通平方误差下，有效信道重建误差加正权重 BCE 可以同时以正确活动概率和活跃条件均值为最优值；不能将乘积误差存在多种分解，误述为完整目标在理想函数空间仍不可辨识。单独活跃条件信道监督沿用推导 D26，真值仅用于训练标签；当前仅提出独立对照，未落实为接收机改动。梯度中的活动概率因子只描述一条直接路径，不代表已经测得完整网络的梯度衰减或 AER 退化原因。

### 2026-10-20 七层结果对训练设计的证据补充

七层设计分析（历史路径，见迁移记录：`result/lstmp_depth7_design_review_20261020/REPORT.md`） 沿用上述 NMSE、MD、FA、BCE、conditional mean 与 Adam 的定义，不引入新方法名称。活跃用户误差明确指真实活跃用户上 `p*mu` 的误差，不将其写成未保存的 `mu` 条件去噪误差；负的原始扣噪声残差不等于最终传入网络的负方差。当前结果没有隔离 BCE 到 score 的梯度，也没有开展方差计算的单因素消融。

论文定位再次核对：[Wei §III-C 式(12)、§III-D、§V-A](https://arxiv.org/html/2610.17785v1) 分别对应残差方差、逐层联合微调和独立层 score；[Cai §III-B 式(35)–(38)](https://arxiv.org/html/2506.00581v2) 对应活动混合均值、方差与方差平均。新层适配时固定旧参数、较低旧层学习率、条件信道辅助监督及按 MD/FA 约束选模均是本项目待验证的训练选择，不表述为这些论文已经证明的最优组合。

## 统一的条件信道与活动监督协议第二版（2026-10-20）

第二版训练协议（历史路径，见迁移记录：`paper/DU/docs/LSTMP_TRAINING_PROTOCOL_20261020_V2.md`）沿用 conditional mean、DSM、BCE、layer-wise training 和 fine-tuning 的原有含义，不赋予新的方法名称。来源分别为 Cai §III-B 式(30)、(35)–(38)、§IV-B 式(48)–(49)，以及 Wei §III-D、§V-A；Adam 状态定义沿用本文件既有 Kingma–Ba Algorithm 1 记录。

第二版主目标改为固定训练能量归一化的活跃条件信道平方误差，加按用户平均的自然比例 BCE；有效信道以 `p*mu` 组合并独立评价，直接有效信道监督另作对照。T6–T7 是本项目的条件风险展开和全期望关系，不声称 Cai 或 Wei 已验证这个具体训练目标。固定查询、有限二阶矩和自由函数空间的条件须保留；共同最优输出不能证明有限展开网络的优化收敛或泛化。

主候选允许两项损失更新可训练参数，另以 T10 精确定义仅排除 BCE 对全部 score 参数梯度的对照。条件信道损失不直接依赖同层活动头，但可经后层查询依赖早期活动头。关闭 BCE 参数梯度不等于消除所有活动影响，也不等于恢复精确 AWGN 先验 score。

用户明确要求避免针对条件或既有结果进行特调。第二版不采用前述困难条件专属选模门槛、相对现有检查点的退化容差或带额外系数的第三项辅助监督；全部场景采用同一训练目标和验证选择规则。等系数、统一阶段预算及联合学习率倍率仍是公开的研究配方，不宣称不存在超参数或已被证明最优。此前讨论保留为研究历史，不作为最新执行规则。

## DCN / TWC稿件分离及新稿术语核对（2026-10-21）

DCN与TWC为作者指定的稿件版本标签，不是算法名称或发表状态。
旧稿保存在 paper/DCN；新稿位于 paper/TWC。新稿不另造算法缩写，
不把Wei–Yuan的L-STMP名称当作本项目原创名称。
逐章来源与实现对应见 TWC来源记录（历史路径，见迁移记录：`paper/DU/checks/SOURCE_MAP.md`）。

- **Gaussian projection / 高斯投影、moment matching / 矩匹配、message division / 消息相除**：
  Minka 2001，§2式(5)–(6)、§3式(8)–(10)。一般AFDM算子的LMMSE与SVD表达式为直接线性代数推导。
- **activity mixture / 活动混合的均值与协方差关系**：
  Cai v2，§III-B3式(35)–(38)。用于解释有效信道X=alpha*H，不把基本全期望/全协方差关系命名为新理论。
- **learned score-based turbo message passing (L-STMP)**：
  Wei–Yuan v1，§III，§III-D、§V-A，PDF第2–4页。
  本项目继承展开与逐层训练思想，增加活动分类及条件监督；gamma校准位置与原文式(8)–(10)不同。
- **natural parameters / 自然参数、damping / 阻尼**：
  [Vehtari等2020](https://jmlr.org/papers/volume21/18-817/18-817.pdf)，§5.2印刷第17–18页、
  附录A印刷第32页。本项目delta=min(1,w_ref/w_proposal)不是该文给出的权重规则。
- **conditional mean / 条件均值、binary cross-entropy / 二元交叉熵、denoising score matching / 去噪得分匹配**：
  延续本文件已记录的Cai §III-B及§IV-B、Wei §III-D与分类损失来源。
  当前新稿IV给出去噪及联合训练目标，附录A为相位和噪声估计；风险展开已移入历史研究笔记。

新稿直接描述由观测残差计算输出方差的过程，不再将该操作命名为“反馈尺度”；
一阶score经接收机训练后仍称去噪器，不另命名为“任务适配去噪器”。
新稿参考文献增加wei2026键，术语归属不改变已冻结研究主线。

### TWC当前正文的用词复核（2026-10-21）

核对范围为main.tex实际引入的I–V章及附录A。普通描述不要求被当成术语逐字引用，
但不将内部变量叫法或几个修饰语的组合包装成新的概念。历史副本保留原文。

| 当前处理 | 原文依据或具体含义 |
|---|---|
| 将query、query densities、extrinsic query改为denoiser input、densities of r或传给去噪器的均值和方差 | Cai §III-A式(9)–(11)、§III-B：extrinsic message；Wei §III-C第3页式(11)之前：noisy pseudo-observation。当前正文直接说明输入，不增加一个概念名。已核对本地原文文本。 |
| 将calibrated residual scale改为从观测残差估计方差，并在公式后直接解释乘法系数 | Wei §III-C第3页式(12)使用residual-based variance estimate；本项目的softplus及tanh映射按公式描述，不另命名。 |
| 将activity mixture structure、soft activity weighting改为将信道估计乘以活动概率 | Cai §III-B3式(35)给出两者乘积；保留关系，不把乘法操作命名为结构或机制。 |
| 将conditional operator、physical-scale outputs、training scales分别改为sensing matrix、恢复原尺度、normalization factor s与average channel power P_H | 直接说明矩阵和变量的含义；P_H是功率，不与幅度归一化因子s混称。 |
| 保留calibration factors和progressive/layer-wise training | Wei §III-B式(8)、§III-C式(11)–(12)、§III-D第3页明确使用；没有将本项目gamma的位置改称与Wei相同。 |
| 保留extrinsic message和Message Scheduling | Cai §III-A式(9)–(11)；Shen §III-B标题即Message Scheduling。本地cai.txt、shen.txt已核对。 |
| 保留natural parameters、damping | Vehtari等2020 §5.2印刷第17–18页；本轮重新读取JMLR原文，明确以自然参数差的缩放描述阻尼。 |

没有新增方法名称或缩写。57个编号公式、全部公式块和标签保持不变。

### TWC引言动机与正文衔接（2026-10-21）

当前论证顺序为：无GNSS辅助的差分时延/多普勒与未知活动；多帧AFDM表示；
连续离网条件下的有效信道学习先验；实际消息输入与AWGN预训练的差异；
联合活动和信道估计的深度展开。该顺序已写入英文引言及中文对照，III–V说明对应设计。

| 表述 | 已核对的来源定位及本文用法 |
|---|---|
| doubly dispersive channels；chirp parameters；multipath diversity | Bemani作者稿v2 §III-E、§IV及Theorem 1；Huang 2026引言第2949页。引言说明选择AFDM的动机，不将特定分集定理直接宣称为本文接收机性能。 |
| one-dimensional inverse DAFT | Huang 2026引言第2949页。当前写为简洁的调制结构，不声称同资源下信道矩阵必然比OTFS小或完整接收机必然更快。 |
| received delay coordinate；three-dimensional channel representation | Shen作者稿v1 §II-B式(9)、(14)–(15)：其大差分时延/多普勒有效信道依赖接收时延坐标。本文参考帧DAFT矩阵与跨帧相位分离是本文模型的描述，不声称该分离仅适用于AFDM。 |
| effective channel；fractional delay/Doppler；grid-aligned sparse prior | Huang 2026引言第2949页、§II式(4)–(5)、§III；Ding 2026摘要及引言的网格稀疏学习。信道系数不预设网格稀疏支撑，用户活动稀疏性仍由活动指示保留。 |
| pseudo AWGN observation model；right-rotationally invariant；damping | Cai v2 §III-A共享标量方差、§V-B1式(57)–(58)。一般AFDM矩阵下LMMSE仍可计算；输入分布近似是另一问题，不能仅因失去行正交性便断言失配程度或收敛失败。 |
| deep unfolding；layer-wise training；calibration parameters | Wei–Yuan v1 §III-A–D、§V-A。本文通过接收观测联合训练信道/活动及反馈，在固定层数下优化输出；尚未报告本文的性能或时延增益。 |

既有输入分布诊断仅作为研究动机的内部证据，未在引言新增未完成的性能比较。
本轮不改算法、公式、训练协议或冻结资产，也未将历史诊断的波动归因于单一因素。

## 训练中间结果的重计算（2026-10-20）

**Gradient checkpointing／梯度检查点与 re-computation／重计算**：Chen、Xu、Zhang、Guestrin，[Training Deep Nets with Sublinear Memory Cost](https://arxiv.org/pdf/1604.06174)，v2，§2第2页及§4.1第4–5页、Algorithm 1。这里指反向传播需要时重新计算部分前向中间结果，以增加计算换取较低存储需求，不指保存到磁盘的训练恢复断点。

第三版使用的 **activation checkpointing** 是 [PyTorch 2.7 `torch.utils.checkpoint` 文档](https://docs.pytorch.org/docs/2.7/checkpoint.html)所用实现名称；调用显式设置 `use_reentrant=False`，保留默认随机状态保存。它不定义新的损失或梯度截断。启用深度与重计算范围是本项目硬件执行配置，不归因于 Cai、Wei 或 Chen 的最优参数结论。当前推断入口关闭梯度，不启用该分支；实际数值等价性须通过同权重、同输入的输出及梯度配对检查，不能用该检查代替长期训练性能评价。


### 2026-10-21：TWC 当前稿移除 Wei–Yuan 引用

按作者要求，当前 TWC 正文、参考文献和中文引言移除 Wei–Yuan 预印本引用及具名介绍；保留深度展开、残差方差估计和逐层训练的操作与公式。本文件既有章节和公式出处作为研究溯源保留。删除稿件引用不改变方法来源，也不将上述已有操作改写为本文首创。


### 2026-10-21：TWC 深度展开动机与正式发表文献

引言引用 He、Wen、Jin、Li，*Model-Driven Deep Learning for MIMO Detection*，IEEE Transactions on Signal Processing，vol. 68，pp. 1702–1715，2020，[DOI](https://doi.org/10.1109/TSP.2020.2976585)。卷页及发表状态已通过 [IEEE Signal Processing Society 作者介绍](https://signalprocessingsociety.org/our-story/news-updates/2022/07/model-driven-deep-learning-mimo-detection)核实。技术内容对照[作者稿 v2](https://arxiv.org/html/1907.09439v2)：§IV-B1–2、式(24)–(28)为将 OAMP 迭代展开并在估计模块加入可训练参数；§IV-B4 说明有限维系统及相关信道下学习参数的动机。正文仅用该文支撑 deep unfolding 和迭代估计模块的可训练参数，不将本文的 score 网络、活动分类器或联合损失归因于该文。

Cai §V-B1 的 AWGN 近似讨论与本文感知矩阵的线性处理分开叙述，不用失去行正交性推导 AWGN 近似必然失效。引言的展开动机落在实际迭代输入、信道与活动估计反馈及预设层数下的联合训练；不预先宣称本文收敛或计算开销的改善。公式及算法定义保持不变。


### 2026-10-21：摘要、贡献点与 III–V 叙述一致性

本轮沿用本文件已核对的 effective channel、score-based denoising、conditional mean、activity probability、deep unfolding 和 denoising score matching，不新增方法名称。局部 Gaussian 消息下的后验分解沿用 Cai §III-B 式(30)、(35)；score 初始化的含义沿用 Cai §IV-A–B 的 Tweedie 关系及 DSM。联合训练保留该估计结构并优化实际层输入上的输出，不把微调后的网络无条件等同于预训练分布的精确 score。贡献点明确包含消息参数的联合训练；摘要新增模型及方法概述，尚不含新接收机的数值性能结论。第五章以已有复杂度公式解释固定深度的计算次数，不由此推出完整接收机优于基线的耗时结论。所有公式、标签与算法步骤保持不变。


### 2026-10-21：沿作者旧稿框架重写引言，以 off-grid 为先验动机

作者提供的《AFDM_引言_中文版.docx》用于背景—现有表示局限—学习先验—推断方法的递进结构参考；旧稿中的 FM 和 EM 相位更新不迁入当前 TWC 算法。本轮按作者进一步指定，将 off-grid 作为先验学习的主要动机，跨坐标及跨天线相关性仅为保留完整信道块的补充说明。

已重读本地 `reference/literature/huang2026.pdf` 第2949页摘要、§I及§II开头：使用 fractional delay–Doppler off-grid leakage、sparse or grid-aligned channel assumptions、AFDM effective channel 和 likelihood-annealed Langevin dynamics 的原有含义。正文逻辑为连续路径偏离离散网格、能量扩散削弱预设稀疏表示、直接学习有效信道先验。没有把消除网格假设归因于 AFDM 波形本身，也没有将 Huang 的单链路性能结论当作本文多用户接收机结果。

手工先验与积分困难参照 Cai v2 §I-B1、§II-B；Gaussian 消息及输入模型条件参照 §V-B1。深度展开的一般方法背景沿用已核对的 He 2020 §IV-B。本文多用户层间误差与独立 Gaussian 预训练的差异为结合接收机结构提出的动机，不声称已经测得其失配程度或推导出深度展开的性能保证。原稿中未核实的 Rel-19 标准条款、连续离网算法及超分辨率阶段的概括暂未新增；保留已核对的 Rel-17 和 Shen 场景依据。


### 2026-10-21：引言合并稀疏建模动机及引用形式统一

按作者要求，TWC 正文引用仅保留文献编号，章节及公式定位继续由本文件既有溯源记录保留。引言使用编号引述具体方案，不再以作者姓名作主语。稀疏建模与学习先验动机合为一段，依次说明压缩感知／稀疏贝叶斯建模、Ding 的网格稀疏先验学习、连续参数产生的 off-grid 失配及直接有效信道先验；不将失配夸大成所有稀疏算法必然失效。此处沿用本文件既有 compressed sensing、sparse Bayesian learning 及 Huang 第2949页 off-grid 来源。

实际迭代输入取决于观测算子和信道／活动反馈，是多用户迭代推断的一般问题。引言不再以无 GNSS AFDM 的帧间相位说明这一问题的独有性；具体帧间相位结构仍在系统模型及算法章节陈述。公式、标签和算法定义不变。


### 2026-10-21：区分先验学习与消息近似，重写 MP 至深度展开的动机

引言以三个不同层次推进：已有 score-MP 将学习先验接入 JADCE，但仍使用 Gaussian 消息近似；实际迭代输入含信道／活动反馈误差，Gaussian 去噪精度不直接保证接收机内估计精度；展开后通过信道与活动损失反向传播，共同训练去噪、分类和消息缩放参数。Cai 的 Gaussian 输入条件与阻尼讨论仍对应 §V-B1；He 的可训练展开模块对应 §IV-B。本文训练机制以 IV 章现有联合损失及跨层梯度为依据，不增加收敛、泛化或性能保证。

撤去“增加迭代开销因而必须预设层数”的动机推断。层数保留为展开结构与训练设置，不能单凭选定层数宣称加速。这里的联合训练也不声称恢复精确 Gaussian 输入或消除全部消息近似误差。中英文贡献点同步删除泛泛的“适应输入”表述，公式和训练目标未变。


### 2026-10-21：补充基础 GFRA 稀疏恢复工作并收紧引言动机

引言新增引用已有条目 `ke2020`，作者稿 https://arxiv.org/html/1906.09867v4 ：§II-B 式(5)–(6)说明用户活动造成的空频结构化稀疏性；§II-C 式(7)–(10)说明虚拟角域信道稀疏性；§III-B–C 给出 GMMV-AMP 与交替活动检测/信道估计。引言仅概述这两类稀疏性和 AMP，不将其误写为时延–多普勒网格算法。随后引入 Ding 的 GNN 稀疏先验，off-grid 时延/多普勒讨论限定于相应网格表示，避免将活动稀疏性与路径支撑稀疏性混同。

Cai 作者稿 v2 §V-B1 明确有限维和特定感知矩阵下等效噪声可能偏离高斯；不是“输入由迭代产生”本身否定高斯近似。引言以该局限、活动/信道反馈、接收观测上的跨层联合训练相衔接，不宣称展开消除近似误差或已经取得数值增益。贡献按连续偏移下的多用户模型、有效信道先验与接入稀疏性的结合、跨迭代联合训练组织；CPP、残差方差与训练步骤留在方法章节。算法公式及冻结资产不变。


### 2026-10-21：贡献一参照 Shen 的问题—传输—输入输出关系组织方式

对照 Shen 作者稿 https://arxiv.org/html/2412.20806v1 ，§I 贡献第一点及 §II-B：先说明大差分偏移下多帧传输的目的，再介绍输入输出关系分析。TWC 借鉴该论证顺序，写明无 GNSS LEO 多帧 AFDM 的输入输出推导及帧内/跨帧效应。具体内容依据本稿第二章式 `eq:path-operator`、`eq:path-entry-expansion`、`eq:effective-pilot` 和 `eq:mmv`；不移植 OTFS 扩频方案、欠采样比收益或其数值性能结论。第二项贡献去掉活动稀疏性的重复说明，保留 score-based 有效信道先验与 off-grid 动机。


### 2026-10-21：接收机定位与贝叶斯推导的范围

第三章标题由 Bayesian Receiver Design 改为 Deep-Unfolded Receiver Design。本文局部后验分解、Gaussian 消息除法和 Tweedie 关系保留为估计模块的构造依据；层间网络、去噪系数和反馈方差经过监督联合训练，不据此宣称全部层对应同一固定先验下的后验矩。方法整体称采用 score-based 先验的深度展开 MP 接收机。model-driven deep learning / unfolding 的定位参考 He 2020 作者稿 https://arxiv.org/html/1907.09439v2 §IV-B1–4 及 §IV-D：展开原迭代并学习参数，训练后作为迭代检测器使用。此调整不否认当前推导中的贝叶斯成分，不删除公式或归属引用。


### 2026-10-21：摘要、引言与 III–V 方法定位统一

方法统一描述为 deep-unfolded MP receiver with a score-based channel prior（采用 score-based 信道先验的深度展开 MP 接收机），沿用上条 He §IV-B/§IV-D 的展开方法定位。摘要回归连续偏移的 AFDM 算子、有效信道 score 先验和展开联合训练；不再以跨坐标/天线相关性或替换二阶网络为主旨。第三章保留局部 Gaussian 模型、Bayes 公式、条件均值乘活动概率及 Gaussian 消息除法，说明其用于构造估计模块。第四章区分 DSM 预训练的 score/条件均值关系（初始去噪系数为 1）与跨层监督联合优化；第五章统一算法名称。正文未新增全局后验一致性、Bayes 最优或数值性能断言；公式、标签、引用顺序和算法执行流程不变。


### 2026-10-21：作者原文替换引言开头及 Release 19 来源

按作者明确要求，中文引言前两段逐字采用作者提供文本（未插入引用编号）；英文同步翻译，保留 Liu 和 Release 17 引用，新增 `3gpp22865`。3GPP 官方规格页 https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=4089 确认 TR 22.865《Study on satellite access - Phase 3》、Release 19、V19.2.0、2023-12-22。官方 SA2 Rel-19 23Q3 satellite architecture moderated discussion v0.0.1 第1页将 GNSS independent operation 列入 SA1 Release 19 Phase 3 的新能力；对应 TR 内容定位为 §4 Overview 及 §6.4。官方 TR FTP 此次返回403，因此未声称取得该 Word 原件。相关方向写为研究方向，不作为已完成 NR 空口无 GNSS 支持的结论。中文后续引用编号随英文顺延。

### 2026-10-21：对照 Cai、Shen、Ding、Huang 润色英文摘要与引言

本轮重新读取 `reference/literature/` 中四篇 PDF 的摘要和引言，并核对 Cai 的等效噪声讨论。
修改范围为 TWC 英文摘要和第一章 Introduction，按作者澄清不修改第二章系统模型。
保留既有背景、相关工作次序及三项贡献；采用通用句法和原有技术术语，具体主张以本稿模型及训练过程为准。

| 原词或论述功能 | 原文定位 | 本稿用法 |
|---|---|---|
| sporadic transmission、short packets、signaling overhead、access latency | Cai §I，印刷第3575页；Ding §I，PDF第1页 | 描述机器类业务特点、GFRA动机及JADCE任务，先说明业务和资源限制，再引出接收机问题。 |
| large differential delay and Doppler shift；input-output relationship；multi-frame transmission | Shen 摘要及§I，PDF第1–3页 | 用于无GNSS场景、AFDM多帧模型及贡献一；按“传输场景—输入输出推导—模型刻画的效应”组织，不移植其OTFS方案。 |
| doubly selective channels、one-dimensional IDAFT、chirp parameters | Huang §I，印刷第2949页；Ding §I，PDF第1页 | AFDM波形动机仍为可调啁啾参数与一维调制结构，不增加相对于OTFS的普遍复杂度或矩阵维度优势。 |
| sparse Bayesian learning、sparsity pattern、delay-Doppler grid、graph nodes | Ding 摘要及§I，PDF第1页；Shen §I，PDF第1页 | 概述传统稀疏恢复及GNN先验学习；时延–多普勒离网问题不归因于Ke的虚拟角域模型。 |
| off-grid leakage；AFDM effective channel；sparse or grid-aligned channel assumptions | Huang 摘要及§I，印刷第2949页 | 用于连续时延/多普勒、离散支撑失配与直接学习有效信道先验之间的连接。 |
| score-based channel prior、reverse diffusion sampling、equivalent noise、damping | Cai §I，印刷第3575–3576页；§V-B1，印刷第3583页、式(57)–(58) | 说明score-MP如何利用先验，以及有限维和感知矩阵对等效Gaussian噪声模型的影响；阻尼调整消息，不等于对估计模块进行联合训练。 |

句式按论述功能选用：用 `In ...` 介绍已有方案，用 `However`、`whereas` 区分具体限制或代价，
用 `First`、`Next`、`Finally` 串联摘要中的模型、先验和完整接收机；贡献点用 derive、learn、develop
直接说明本稿工作。常规连接词不作为专门术语或方法名称。
摘要删除活动加权、反馈方差等实现层面的重复展开，保留score预训练、渐进训练和联合微调的因果关系。
深度展开背景继续引用已发表的 He 2020，跨层训练描述以本稿第四章损失及反向传播为依据。
未改变公式、引用顺序、数字引用形式或方法定位，也未加入新算法的性能结论。

### 2026-10-21：按作者修订明确摘要的学习先验与深度展开贡献

摘要沿用作者的无 GNSS 场景及多帧 AFDM 传输叙述，补明输入输出关系推导。
`channel prior learned by score-based generative models`、`hand-crafted channel priors`
参照 Cai 摘要，印刷第3575页；`AFDM effective channel`、`off-grid effects` 和
`grid-aligned` 的含义参照 Huang 摘要及§I–II，印刷第2949–2950页：直接学习
含连续时延和多普勒效应的有效信道，避免预设网格稀疏支撑。
深度展开的表述依据本稿第四章 `Joint Channel and Activity Training` 及
式 `eq:twc-layer-objective`，概括 score 预训练后在接收导频上的跨层联合优化。
摘要不再罗列渐进训练、相位和噪声估计及复杂度分析；未加入优于基线的性能断言。

### 2026-10-21：按作者要求重新对照 Shen、Cai、Wei 撰写摘要三项工作

仅修改摘要从 Firstly 开始的三项工作；之前的背景句保留作者原文。
重新读取本地 Shen、Cai 和 Wei 的摘要、引言贡献及 Wei 的训练小节。

| 摘要表述 | 原文定位与适用范围 |
|---|---|
| mitigate the doubly dispersive effect in time and frequency；input-output relationship | Shen 摘要，PDF第1页；第一项贡献，PDF第2页。沿用先说明多帧传输目的、再说明输入输出关系的顺序；具体波形为本稿 AFDM，不引入 Shen 的 OTFS 扩频或欠采样比收益。 |
| channel prior learned by score-based generative models；hand-crafted channel priors | Cai 摘要，印刷第3575页。保留作者已采用的先验表述，并写明其引入 MP；off-grid 部分仍依据 Huang 第2949–2950页，不归因于 Cai 的性能结论。 |
| learnable score priors；trainable parameters in each layer；progressive training and fine-tuning | Wei 作者稿 v1 摘要及§I，第1页；§III-A，第2页；§III-D，第3页。用于说明展开后的可训练组成与训练方式；本稿活动检测的联合训练以第四章式 `eq:twc-layer-objective` 为依据，非 Wei 单用户信道恢复的已有功能。 |
| Gaussian denoising model 与实际迭代输入的 mismatch | Cai §V-B1，印刷第3583页；Wei §III-A及§III-D，第2–3页。本稿写为联合训练的目标，不声称已证明消除近似误差、解除所有矩阵条件或取得迭代次数/耗时增益。 |

Wei 仅保留在内部来源记录中，本次未向 TWC 正文或参考文献表添加其引用。

### 2026-10-21：按 Cai、Shen、Ding、Huang 润色英文引言

作者确认本轮四篇对照文献为 Cai、Shen、Ding、Huang。修改对象仅为
`paper/TWC/sections/01_introduction.tex`；前两段已认可的背景原文保留。
维持背景—波形—稀疏建模与离网局限—学习先验—MP 消息近似—深度展开—
三项贡献的既有顺序，使用原文的标准术语、短语和通用论述句式。

| 段落功能与用语 | 本次核对的来源 | 本稿采用范围 |
|---|---|---|
| doubly selective channels；intercarrier interference；chirp parameters；one-dimensional inverse DAFT | Huang §I，第2949页；Ding §I，PDF第1页 | 说明波形选择的动机及 AFDM 调制结构；多径分集的技术引用仍为 Bemani，不移入相对 OTFS 的普遍复杂度结论。 |
| multi-frame transmission；large differential delays and Doppler shifts；input-output relationship | Shen 摘要及§I，PDF第1–2页 | 相关工作只将 OTFS 方案归属于 Shen；贡献一按传输方案、输入输出关系及其刻画效应组织，AFDM 算子依据本稿第二章。 |
| compressed sensing；sparse Bayesian learning；sparse prior；graph nodes；sparsity pattern | Ding 摘要及§I，PDF第1页 | 从传统稀疏建模引出网格先验学习；Ke 的活动/虚拟角域稀疏性与 Ding 的时延–多普勒网格分开说明。 |
| hand-crafted priors；score-based generative models；channel prior learned by score-based generative models | Cai 摘要及§I-A，印刷第3575–3576页 | 先说明先验可由样本学习，再介绍其用于接收机；保留数字引用，不以人名替代方案说明。 |
| off-grid effects；power leakage；AFDM effective channel；grid-aligned assumptions | Huang 摘要及§II，第2949–2950页 | 从连续路径与网格失配说明学习有效信道先验的作用，未将活动稀疏性与路径网格稀疏性混淆。 |
| linear estimation；score-based channel denoising；Gaussian noise model；damping | Cai §I-A及§V-B1，第3576、3583页 | 区分先验学习与消息输入近似；保留有限维/感知矩阵相关的近似局限，阻尼的作用不等同于训练去噪器。 |
| unfolding；trainable parameters；training with observations, channel and activity labels | Cai §I-B2，第3577页 | 深度展开段按迭代模块可训练、通过观测联合训练两个任务组织；正式方法背景继续引用已有 He 2020，未新增 Wei 引用。 |

段落使用 `In ...` 介绍已有工作、`However` 引出明确局限、`whereas` 对比
细网格与连续偏移估计的代价；贡献点采用 propose/derive、learn/incorporate、
develop/optimize 的动作结构。具体联合训练及跨层消息仍以本稿第三、四章为准。
本轮不迁入四篇论文的性能数字、收敛保证或算法模块；摘要和其余章节未改。

### 2026-10-21：前两段背景改用参考论文中的常见表达

作者要求前两段也对照参考论文重新表述，本轮仅修改英文引言的这两段。
采用已有术语、短语与通用句式，背景信息和前三个引用的顺序不变。

- `remote areas`、`terrestrial networks`、`pre-compensate`、`satellite ephemeris`、
  `large differential delay and Doppler shift`：Shen §I，PDF第1–2页。
  延续远程 IoT、GNSS 预补偿及终端能耗到接收机处理的论述次序。
- `grant`、`pilot resources`、`nonorthogonal pilots`：Cai §I，印刷第3575页；
  GFRA 的接入时延动机同时对照 Ding §I，PDF第1页。当前写明无需先获得授权、
  导频资源有限、接收机联合检测活动和估计信道，不再使用 `beam footprint`
  等额外表达。按作者进一步要求，删除短分组业务的前提，不将 Cai 的地面
  业务特征直接推广到卫星 IoT；GFRA 动机仅由授权流程的信令及接入时延说明。
- `timing and frequency offsets`、`block-fading channels`：Shen §I，PDF第1–2页
  对地面方案的讨论；用于表达原稿近似同步和块衰落的含义。
- Release 17/19 与 common timing advance 仍沿用本文件此前核对的
  `3gpp38300`、`3gpp22865`，不将标准版本信息归因于四篇论文的原句。

中文引言中作者指定保留的中文原文未改；摘要及英文引言第三段之后未改。

前两段衔接复核：第一段按 GFRA 减少授权信令、活动状态未知与导频资源有限、
JADCE 及卫星时延/多普勒依次展开，参照 Cai §I第3575页及 Ding §I第1页的
论述功能；第二段从 Release 17 预补偿承接上一段问题，再由硬件/能耗代价
引入无 GNSS 接入与接收端处理，参照 Shen §I第2页。`However` 表示限制，
`Meanwhile` 引出并行的导频限制，`therefore` 导出接收任务，`Specifically`
说明预补偿的信息来源，`In particular` 说明差分偏移尺度。未恢复短分组假设。

### 2026-10-21：第三段从 OTFS 切入并明确 AFDM 的波形优势

本轮仅改英文引言第三段，OTFS 概念介绍改引 Hadani 等的 WCNC 2017
论文 `hadani2017`，不再在该段引用 Shen。依据作者所在机构的
[论文摘要与出版记录](https://scholars.duke.edu/publication/1259298)，
采用 `delay-Doppler domain`、二维调制及时间/频率分集的表述。

AFDM 的可调参数与多径分集依据 Bemani 的
[作者稿 v2](https://arxiv.org/html/2204.12798v2) §III-E、§IV；
单次逆 FFT 加啁啾乘法由 §II-B 式(16)后的逆变换分解及 §III-A 式(18)
后的调制矩阵直接得到。本文据此说明调制实现简单、适合计算资源有限的终端；
这是波形选择动机，不构成本稿大差分偏移模型的路径完全分离或满分集证明，
也不推断 AFDM 在相同资源下具有普遍更小的信道矩阵或更低的接收机复杂度。

### 2026-10-21：补明阻尼的收敛代价及其与联合训练的区别

引言在 Cai 相关工作之后说明 strong damping 可能减慢收敛，并承接深度展开。
平滑消息的含义依据 Cai §V-B1，第3583页、式(57)–(58)；较强阻尼赋予新估计
更小权重。强阻尼与收敛速度的关系另引已发表的 Yoshida–Takeuchi 2023
`yoshida2023`，其[出版社原文](https://www.jstage.jst.go.jp/article/transfun/E106.A/3/E106.A_2022TAP0009/_pdf)
§1，第414–415页，讨论 strong damping、slow convergence 以及达到相近性能
所需的更多迭代。正文保留 can，不将该结论写成所有问题中阻尼必然减慢收敛。

更多迭代意味着更多线性估计及 score 网络调用，这是根据 Cai 算法及 §V-C
逐次计算开销作出的成本推论，并非本稿新完成的性能实验。
阻尼不更新预训练去噪器权重，因而不能直接训练其处理实际迭代残差；此点是
消息平滑与联合训练操作的区别。本文第三章仍保留阻尼，第四章通过联合损失
优化去噪器、活动检测器及层间消息参数；未将深度展开描述为取消阻尼或保证消除失配。

### 2026-10-21：深度展开与消息失配的衔接、贡献一的矩阵规模

深度展开段撤去单独介绍 OAMP 检测器的插叙，直接承接实际迭代输入与
Gaussian 预训练输入的差异。`deep unfolding`、保留 MP 结构并训练展开层
依据 He 2020（`he2020`）；本轮核对作者发表于 IEEE Signal Processing Society
的[论文说明](https://signalprocessingsociety.org/our-story/news-updates/2022/07/model-driven-deep-learning-mimo-detection)，
“Model-Driven Deep Learning”及“Model-Driven DL Detector”两节。
本稿的 channel denoisers、activity detectors 联合训练及误差对后续更新的影响，
具体由第四章式 `eq:twc-layer-objective` 及其后的梯度说明支持，不归作 He 的 JADCE 功能。

贡献一明确本文第二章已经给出的维度：每用户、每接收天线的有效信道为
$N\times N$，跨 $Q$ 个导频帧共享；完整用户信道张量为 $M\times N\times N$。
帧间相位进入 $A_{qkn}$，因此增加 $Q$ 不增加 $H_k$ 的元素数量。
依据为式 `eq:channel`、`eq:effective-pilot`、`eq:mmv`。此处的共享以正文中
块内固定几何/路径系数、每用户各路径共同 Doppler 及足够长 CPP 为模型依据。

同时核对 [Shen 作者稿](https://arxiv.org/html/2412.20806v1) §II-B 式(8)–(10)：
其每用户、每天线有效信道 $H^{\rm DDS}[k',l',l]$ 有 Doppler 索引、路径时延
索引和接收时延索引，完整存储为 $N_{\rm S}M_{\rm S}^2$ 个复数；其中一帧
有 $N_{\rm S}M_{\rm S}$ 个有用符号，不能直接与本稿的一个 $N$ 点 AFDM 帧等同。
张量的索引个数、完整存储元素数量和独立未知参数数目也不是同一概念。
尤其若在 Shen 式(9)中也采用每用户共同 Doppler，Doppler 响应及接收时延
相位可从路径增益之和中提出，故三维索引不必对应三组独立未知量。
本次未把二维/三维的差别写成 AFDM 相对所有 OTFS 方案的维度或复杂度优势；
贡献强调本稿推导得到的固定矩阵规模及跨帧共享，不增加未经配对比较的缩减倍数。

### 2026-10-21：参照 Shen 调整 OTFS 与 AFDM 的引出顺序

核对 Shen §I（作者稿第2页）：先说明终端预补偿的能耗与剩余时延/多普勒问题，
再以 OTFS 用于卫星 GFRA 的可靠通信引出其时延–多普勒域表征，随后讨论已有方案。
本稿第三段据此先交代 OTFS 对双选择性信道的作用，再以终端实现需求承接 AFDM，
避免从符号映射定义直接跳到二维/一维的比较。

OTFS 的可靠通信、时间/频率分集仍依据 `hadani2017` 摘要；AFDM 的可调啁啾、
多径分离与分集、逆 FFT 加啁啾乘法仍依据此前核对的 Bemani §II-B、§III-A、
§III-E、§IV。Shen 本轮用于论述结构对照，不恢复到第三段的概念性引用中。
终端计算资源限制是本稿的波形选择依据，没有据此宣称 OTFS 必然实现复杂，
也未加入 AFDM 普遍更低维或更低接收机复杂度的结论。

### 2026-10-21：参照 Wei 明确深度展开的作用及优势论证

本轮核对本地 Wei–Yuan 作者稿（仅本地历史资料：`reference/literature/wei_yuan_2026_lstmp_v1.pdf`）
摘要与 §I（第1页）、§III-A（第2页）、§III-D（第3页）、§V 与 Table I
（第4–5页）。原文先指出有限维结构化测量下 STMP 的 AWGN 等效输入近似可能失准，
再引入各层可训练的 score 网络和 calibration parameters，以补偿实际测量条件与
理想消息模型之间的偏差；少层推断的性能与开销优势由其数值比较支持。
`layer-specific` 对应原文 `layer-wise` 及各层独立网络，`update parameters`
在本稿中直接指第三章已定义的可学习更新参数，不另造方法名称。

引言据此将深度展开的作用写成学习各层去噪器与更新参数来补偿 Gaussian 消息
近似偏差，并保留由观测模型确定的线性估计。接收信号训练、活动检测与信道去噪
联合优化及其对后续干扰抑制的影响，由本稿第三章反馈公式及第四章
`eq:twc-layer-objective` 支持；Wei 的单用户信道恢复未包含本稿的活动检测任务。
贡献三同步说明学习参数的作用，删去前段对训练噪声与迭代残差的重复说明。

少迭代下保持估计质量是本稿训练目标，正文用 `aims to`，不将固定展开深度本身
当作同等精度加速的证据，也不移植 Wei 的五层、40 倍开销比较或性能数字。
未声称展开恢复严格 AWGN 性质、取消全部阻尼或获得对任意矩阵的理论保证。
按用户要求，Wei 仅作内部论述参考，不加入正文引用或参考文献；深度展开的一般
结构仍引用已正式发表的 `he2020`，其来源定位见本文件先前记录。

### 2026-10-21：按 Wei 的贡献表述顺序重写贡献三

再次对照 Wei §I 第1页 `Firstly` 后的贡献：先说明将 turbo MP 展开为多层网络，
再说明各层可学习参数与 score 网络的作用，随后说明推断收益。本文贡献三采用
“展开 MP 并引入各层可学习模块—训练去噪器及消息参数以补偿 Gaussian 近似误差—
逐层训练并联合优化信道与活动估计”的顺序，不再把预训练、逐层训练、联合微调
连续罗列在贡献的主句中。`multilayer network`、各层可学习 score 及参数依据
Wei §I、§III-A；`progressive training` 依据 §III-D 和本稿第四章。
活动检测属于本稿的多用户 JADCE 设计。`to compensate` 表示训练目的，有限层数
是接收机结构；未引入新的精度、加速或严格消除近似条件的结论，仍不引用未见刊的 Wei。

### 2026-10-21：分开贡献一中的连续偏移建模与跨帧共享

整数与分数偏移的保留依据第二章 `eq:continuous-basis`、`eq:path-operator`
及 `eq:path-entry-expansion`，不是分离帧间相位带来的结果。跨帧共享则依据
块内固定路径参数与每用户共同 Doppler 的现有模型，以及 `eq:channel`、
`eq:effective-pilot`、`eq:mmv`：帧间相位进入感知矩阵 A，Q 增加观测行数，
不为每帧新增一组 X 中的信道系数。贡献一据此分开两条逻辑，删除提前解释 N
的尺寸细节，并将收益写成多帧共同估计一组信道；未新增相对 OTFS 的维度结论。

### 2026-10-21：将确认后的引言衔接统一到英文正文

第二、三段明确接收端处理大偏移是减轻终端用户专属预补偿的方案选择，再由
处理时延/多普勒与终端调制简单这两项需求介绍 AFDM；不将 GNSS 独立运行解释为
必须采用 AFDM。依据沿用上文 Shen §I 的接收端处理动机及 Bemani 的波形性质。
第三段不加入提前宣布本文传输方案和接收机的结句，本文工作统一在贡献前引出。
同时保留已确认的 MIMO 学习先验合句、删除深度展开段的线性估计结构插叙，
以及区分连续偏移建模和跨帧共享的贡献一、按设计—作用—训练组织的贡献三。

### 2026-10-21：ARS 摘要与引言候选稿

候选路径为 `paper/TWC/revisions/ars_20261021/`。本次将已核对的术语用于
摘要和引言重写；当前 `paper/TWC` 原稿保留，未变更模型或接收机公式。

- `multi-frame OTFS` 与 `delay-Doppler-angle` 信道稀疏性：
  [Shen 作者稿](https://arxiv.org/html/2412.20806v1) §I 贡献及 §II-B。
  该文联合处理设备活动、信道系数与数据符号。本次作为独立相关工作句引用，
  不替代 Hadani 的 OTFS 概念出处，不将多帧接入本身表述为本文独有。
- `effective channel`、分数时延/多普勒与得分先验：沿用 Huang 2026
  第2949–2950页及本文件既有来源定位。摘要将分数偏移的作用表述为单路径
  能量扩散到多个网格系数，避免写成能量跑到整个离散网格的范围之外。
- 跨帧共享：对应本稿 `eq:channel`、`eq:effective-pilot`、`eq:mmv`；
  相位因子进入导频算子后，各帧共同估计一组有效信道。该结构结论与
  连续偏移建模分别陈述。
- 条件信道估计、活动概率及其乘积：对应 Cai 的混合先验分解与本稿
  `eq:twc-local-channel-target`、`eq:twc-local-activity-target`、
  `eq:twc-estimate`。乘积用于构造反馈，实际消息还经过
  `eq:twc-feedback-proposal` 和 `eq:twc-damping`；未把乘积直接等同于外信息。
- `deep unfolding`、`progressive training` 与联合监督：沿用本文件
  He 2020 及训练方法的既有定位。本文跨层信道/活动梯度的作用来自
  `eq:twc-layer-objective` 后的梯度路径说明，不作为参考文献已有的 JADCE
  创新归属。Wei 仍仅作此前内部参考，未新增到论文引用。

方法和结构性结论直接陈述；摘要的数值结果句待新接收机独立评价完成后补入。
未转用其他算法或论文的性能数据，也未增加新的方法名称或缩写。

### 2026-10-21：按作者要求回到 ARS 改写前的贡献结构

作者明确要求以原 TWC 版本继续修改，贡献主线为：大差分时延和多普勒下的
AFDM 传输方案及输入输出关系、score-based 生成式信道先验、深度展开 MP 接收机。
当前稿件入口恢复为 `paper/TWC/main.tex`，此前 ARS 候选标记为停用。

原英文引言的背景、相关工作及引用安排保留。贡献一沿用原文；跨帧共享信道
用于说明输入输出模型的具体作用。贡献二依据本稿第四章 `eq:twc-dsm` 与其前后的
连续参数信道样本说明，补明多天线有效信道先验的学习方式及 off-grid 作用；
术语来源仍为 Arvinte、Huang、Cai 的既有记录。贡献三以深度展开 MP 接收机
设计为主句，各层去噪器、活动检测器、消息参数及逐层联合训练作为该设计的
具体组成，依据本稿第三、四章及本文件中 He 2020 的既有定位。

本次未新增方法名称、算法缩写或文献。摘要保留原有问题—传输与建模—信道先验—
接收机顺序，并修正拼写及终端功耗、计算需求的英文表述。英文引言仅另补齐
首次使用的 3GPP、OFDM、MIMO 全称；中文稿按当前英文同步。

### 2026-10-21：摘要与引言对照 Cai、Shen、Ding、Huang、Wei

本次核对五篇本地原文的摘要、引言及直接相关方法段，评估当前 TWC 原稿
的贡献定位；未修改摘要、引言或文献表。以下记录为术语与对比依据。

- Cai：JSAC 第3576页 §I-A 明确以完整信道矩阵为 super node，分别处理
  信道与活动估计；第3582–3583页 §IV 与 §V-B1 给出一、二阶 score 及
  有限维、特定感知矩阵下的 AWGN 输入近似和阻尼。故不能把“生成式先验
  用于 MP-JADCE”或“信道/活动分解”本身当作本稿新增机制。
  [作者稿 v2](https://arxiv.org/html/2506.00581v2)。
- Shen：作者稿第1–3页 §I 及 §II-B 的多帧 OTFS 已针对无 GNSS、接收端
  处理大差分时延和多普勒，推导输入输出关系并联合处理活动、信道和符号。
  本稿贡献一应具体落在该场景下的 AFDM 传输与模型，而非仅以无 GNSS 或
  多帧为差异。原稿贡献一中跨帧共享有效信道的结果可用于说明模型作用。
  [作者稿](https://arxiv.org/html/2412.20806v1)。
- Ding：接受稿第2页 §II 已写出整数加分数 Doppler，时延近似为整数；
  §III-A 式(8)采用虚拟时延–多普勒网格近似。第3–4页 §III-B 包含 AMP
  unfolding 和 trainable damping，第4–5页 §III-C 包含逐层训练及前层联合
  优化，第5页式(28)采用信道 NMSE。第5页 §IV-A 的仿真明确采用粗预补偿后
  的残余偏移，并假定时延与 Doppler 均与网格对齐。不能概括为“不考虑
  分数 Doppler”或“没有深度展开”；可准确比较其网格支撑学习与本稿
  连续偏移有效信道分布学习，以及预补偿后的评价条件与本稿场景。
  [作者机构版本](https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/Learning-Sparsity-Pattern-An-Adaptive-Joint/991155194002346?institution=44SUR_INST)。
- Huang：第2949–2951页 §I–III 已在单用户单天线链路直接学习 AFDM
  有效信道的 score，覆盖分数时延与 Doppler，并采用 likelihood-annealed
  Langevin posterior inference。§III-A 也使用多个导频序列。因此本稿第二项
  需交代多天线、多用户 JADCE 中的先验对象及去噪用途，仅写 AFDM score
  prior 和 off-grid 效果不足以清楚区分。依据为 `reference/literature/huang2026.pdf`。
- Wei：作者稿第1页摘要/§I，第2–3页 §III-A–D 已包含每层可训练 score、
  calibration parameters、残差方差、逐层训练与所有已有层的加权信道误差。
  其任务为 HBF 压缩观测下的信道恢复。本稿第三项的具体依据包括未知用户
  活动、条件信道估计及活动概率、两类监督通过反馈共同参与接收机训练。
  [作者稿 v1](https://arxiv.org/html/2610.17785v1)。本轮内部对照未改变此前
  关于正文引用 Wei 的作者安排。

本稿定位依据：第二章 `eq:channel`、`eq:effective-pilot`、`eq:mmv`；第三章
`eq:twc-conditional-mean`、`eq:twc-activity`、`eq:twc-estimate`；第四章
`eq:twc-channel-loss`、`eq:twc-activity-loss`、`eq:twc-layer-objective` 及其
梯度路径说明。三项主贡献仍保持“传输及输入输出关系—生成式信道先验—
深度展开 MP 接收机”，具体结构与训练说明用于支撑各项主贡献。

### 2026-10-21：TWC 第二至五章的论证与网络结构修订

当前入口为 `paper/TWC/main.tex`。本轮依据 Cai、Shen 的方法章节调整论证顺序，
保留原有接收机更新式、训练目标与实现，不为残差映射、方差调整或跨帧关系另起名称。

| 术语或表述 | 原文定位 | 本稿使用范围 |
|---|---|---|
| multi-frame transmission；differential delay；Doppler shift | [Shen 作者稿](https://arxiv.org/html/2412.20806v1)，§II-A–B、§III-C | 公共时延补偿是模型起点；块内固定路径参数、每用户共同 Doppler 和充分长 CPP 推出本文 `eq:twc-frame-channel`。该恒等式是本稿已有路径算子的直接推导，不称 Shen 的原公式。 |
| Gaussian message；extrinsic message；conditional mean | [Cai 作者稿 v2](https://arxiv.org/html/2506.00581v2)，§III-A 式(6)–(11)、§III-B3 式(35)–(38) | 分别指 Gaussian 近似、消息相除后的外信息及条件信道均值。相除前的输出均值为 Xhat，真正返回的均值为经过相除和阻尼的 M。 |
| score；Tweedie's formula；denoising score matching | Cai §IV-A–C，式(44)、(46)–(49) | 第四章依次解释条件均值、未知 marginal score、可计算的 Gaussian perturbation score 及预训练目标。 |
| conditional residual block；refinement block；RefineNet | Cai §VI-A2、Table III；[Song–Ermon](https://arxiv.org/pdf/1907.05600)，Appendix A.3，PDF p.14 | 实际运行分支为 conditional RefineNet。网络宽度、连续噪声条件输入与张量尺寸按本地运行快照逐项记录，不写成 NCSN++。 |
| conditional instance normalization；dilated convolution；ELU | Song–Ermon，Appendix A.1–A.3，PDF p.14 | 归一化包含通道均值信息；以三个逐通道系数描述实际计算。保留 dilation 2、4 时空间尺寸不再下降的实现事实。ELU 使用其原有含义。 |
| binary cross-entropy；class-probability estimation；logistic loss | [Menon–Ong](https://proceedings.mlr.press/v48/menon16.pdf)，§2.2，印刷 p.305；§3 式(6)–(8) | 用于说明固定输入分布下的概率监督目标；与活跃用户上的平方误差分别对应活动概率和条件信道均值。 |
| partial-orthogonal matrix | Cai §V-C 式(66)及复杂度分析 | DFT 导频本身行正交，用户相关跨帧相位一般破坏该性质；因此本文保留一般矩阵分解与乘法代价。 |

SVD 名称沿用本文件已核对的 Gavish–Donoho §1 式(2)及其后说明；本轮未采用
该文的奇异值收缩或截断方法。一般矩阵 LMMSE 的 SVD 实现为直接线性代数推导。

均值与方差联动由 Gaussian 乘积均值直接求解。残差能量的期望关系以零均值、
各向同性且与噪声不相关的估计误差为推导条件；实际接收机将扣噪残差作为
可训练方差构造的输入。softplus、正乘子、tanh 和自然参数阻尼均直接按公式
解释用途，沿用本文件此前记录，不包装成新方法名称。

实际结构依据为 `cloud/review_20261021/MANIFEST.json` 的 `direct_cai` 选择，
及其 `source_project/.../network.py`、`cai_models/ncsn_channel_diffusion.py`、
`layers.py`、`normalization.py`；活动头与逐层训练依据同快照的
`source_code/experiments/lstmp_candidate_20261019/receiver_base.py` 和
`lstmp_training_v2_20261020/optimization.py`。其中连续条件向量为
log(v)/5 经 1→64→64 映射；其维度和激活是实现选择。新增消息图、网络表及
推导核验见 修订记录（历史路径，见迁移记录：`paper/DU/checks/argument_revision_20261021/README.md`）。

### 2026-10-21：TWC 后验因子图与消息定义

- `factor graph representation`、`variable node`、`factor node`：Cai 正式版本
  §II 式(5)、Fig. 2、Table II，印刷第3578–3579页；Shen §III-A 式(19)–(20)、
  Fig. 2，作者稿 PDF 第6页。当前图将观测似然合为 `f_y`，每个 `X_k`、`H_k`
  节点表示完整用户张量，约束因子 `g_k` 直接表示 `X_k=alpha_k H_k`。
- `belief`、`Gaussian message`、`extrinsic message`：Cai §III-A 式(6)–(11)
  及 §III-B；`moment matching`、Gaussian 相除沿用 Minka §2–3 的既有定位。
  当前第三章明确两个模块的输入消息、局部 belief、Gaussian 输出与外信息。
  线性模块匹配均值和平均边际方差；去噪模块的 Gaussian 输出方差仍采用本稿
  已定义的残差构造和可学习映射。
- `sum-product rule` 的操作对应约束代入、对信道先验积分以及对活动状态求和；
  来源为 Cai §III 首段和本文件既有 Kschischang–Frey–Loeliger 定位。
  `A`、`B` 仅用于指代线性估计和信道/活动去噪两个模块；新增因子和消息符号
  均为公式记号，没有另设方法名称或算法缩写。

原文文件为 `reference/literature/cai2026.pdf` 与 `shen2025.pdf`。
具体修改及检查见 因子图补充记录（历史路径，见迁移记录：`paper/DU/checks/factor_graph_20261021/README.md`）。

### 2026-10-21：相位估计改进调研

本节对应 [相位估计调研](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/PHASE_ESTIMATION_REVIEW_20261021.md)，用于候选分析，
不表示当前算法或实验配置已经改变。文献方法的原名与项目拟议操作分别说明。

| 原文术语 | 原文定位 | 本项目使用范围 |
|---|---|---|
| variable projection；separable nonlinear least squares | [O’Leary–Rust 作者原文](https://www.cs.umd.edu/users/oleary/software/varpro.pdf)，§1 式(2)–(3)、§2 | 当前已对给定时延、多普勒解析消去复增益；不将这一既有操作称作新方案。 |
| Newtonized Orthogonal Matching Pursuit (NOMP) | [Mamandipoor 等作者稿 v2](https://arxiv.org/pdf/1509.01942)，§II、Algorithm 1 | 借鉴粗候选检测、牛顿精化和循环修正。AFDM 物理字典的改写不能未经论证直接称为原 NOMP。 |
| Multi-snapshot Newtonized Orthogonal Matching Pursuit (MNOMP)；Refinement Acceptance Condition | [Zhu 等作者稿 v2](https://arxiv.org/html/1802.01266v2)，§III-A–B 式(5)–(8)、Algorithm 1 | 借鉴多测量向量联合评分和目标改善后接受精化的规则。原纯正弦模型的停止门限不可直接移植到相关 AFDM 字典及估计噪声条件。正式论文题名由出版社 2019 年版本核对。 |
| expectation-maximization；phase update | [Shen 等作者稿 v1](https://arxiv.org/html/2412.20806v1)，§III-C 式(47)–(54) | 原文后验期望目标与单位圆投影；式(53)–(54)不是本项目单一跨帧相位斜率的现成闭式解。项目旧改写的正负结果保留于历史报告。 |
| Estimation of Signal Parameters Via Rotational Invariance Techniques (ESPRIT) | [Roy–Kailath，1989 原论文](https://alumni.media.mit.edu/~aggelos/papers/roykailath89.pdf)，摘要，印刷 p.984 | 仅引用其旋转不变性结构条件；当前随机跨帧导频的可用性需另证。本次未核验全文公式，不给出公式级适用性结论。 |
| maximum likelihood estimation；FFT/IFFT | [Liu 等作者稿 v3](https://arxiv.org/html/2306.06734v3)，§II-A、§IV、Algorithm 3 | 引用 Rician 活动与偏移联合估计中的先验条件及特定目标的等价计算，不把其性能收益外推到本项目。 |

固定 DAFT 变换移到观测端的建议直接由酉变换保持 Frobenius 范数推出；
同一时延分段内预计算系数由当前原子公式推出。二者只描述计算操作，
不另造方法名、缩写，也不据此宣称有限精度实现逐位等价或已获得加速。

### 2026-10-21：摘要及前五章的论证衔接

本轮直接修改 `paper/TWC` 当前稿件；三项贡献仍为 AFDM 传输与输入输出模型、
score-based 有效信道先验、深度展开 MP 接收机。没有增加方法名称或缩写。

| 用语或推导环节 | 原文及定位 | 本轮使用方式 |
|---|---|---|
| factor graph；joint posterior distribution；Gaussian belief；extrinsic message | Cai 正式版，第3578–3581页，§II-B、Fig. 2、§III-A/B；Shen 作者稿 PDF 第6页，§III-A，式(19)–(20)与 Fig. 2 | 先由似然和用户先验的分工说明模块划分，再按输入消息、局部 belief、Gaussian quotient 说明更新。 |
| channel denoising；device activity denoising；posterior mean | Cai 第3580–3581页，§III-B，尤其式(35)–(38) | 说明条件信道均值与活动概率的乘积为何用于有效信道估计；保留既有乘积公式，不将此分解单独作为新方法。 |
| effective channel；fractional delay and Doppler；score-based generative model | Huang 第2949–2950页，§II–III；Cai §IV-A/B，第3582–3583页 | 用连续参数信道样本连接 off-grid 动机与 DSM；跨天线依赖作为整块信道建模的一部分。 |
| progressive training；deep unfolding | 沿用本文件已有 He 2020 与 Wei–Yuan v1 §III-D、§V-A 定位 | 保留前人术语，具体的两项监督和参数启用时机由本项目实现确定。Wei 仍仅作内部来源记录，未重新加入稿件引文。 |
| natural parameters；damping | Vehtari 2020 §5.2，第17–18页及 Appendix A；本稿 `eq:twc-damping` | 由正精度的凸组合直接说明阻尼后方差为正；未引申为迭代收敛结论。 |

多帧增加观测但不增加共享信道维度、Q≤KN 的导频选择条件、两项损失通过
分类器输入和返回消息传播的关系，分别由本稿已有矩阵维度、导频式及计算图直接说明，
不另起技术名称。当前代码 `src/algorithm/proposed/receiver.py:73–89` 支持所述梯度路径；
历史训练快照 `src/history/cloud/review_20261021/source_code/experiments/lstmp_training_v2_20261020/optimization.py:11–20`
明确在每个深度排除末层返回方差参数，接入下一层后再启用。

中英文摘要和引言同步；完整修订和核验见
摘要及前五章修订记录（历史路径，见迁移记录：`paper/DU/checks/abstract_ch1to5_polish_20261021/README.md`）。

### 2026-10-21/22：Shen 相位更新的 AFDM 候选实现

| 表述 | 原文定位 | 本项目使用与限制 |
|---|---|---|
| expectation-maximization；phase rotation；projection | Shen et al., arXiv:2412.20806v1, §III-C，式 (47)–(53)，Algorithm 1 | 保留二次型及 `A u=b` 后逐元素投影到单位圆的步骤。十层均值和经校准的反馈方差是 AFDM 适配；反馈方差仅为近似，不将候选称为精确 EM 或完整论文复现。 |
| posterior variance | 同文式 (38)、(49)–(51) | 原文通过消息传递获得。当前网络没有同样的后验方差；代码和报告明确标记 variance proxy，不混称为已验证的 posterior variance。 |

逐用户 `exp(j q beta_k)` 约束及对它的最小平方距离投影直接用公式描述，不新造算法名称。
它不包含时延、物理多普勒原子或别名搜索；斜率约束为项目适配，不归于原文式 (53)。
详见 [候选实现与验证协议](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/SHEN_PHASE_IMPLEMENTATION_20261021.md)。

### 2026-10-22：协方差候选及训练信道样本辅助相位估计

| 既有术语或运算 | 核验原文 | 当前使用及边界 |
|---|---|---|
| Non-Negative Least Squares；sample covariance | Fengler et al., arXiv:1910.11266v2，§III-B 式 (26)–(29)，[原文](https://arxiv.org/html/1910.11266v2) | 参考协方差矩阵拟合。AFDM 块导频和相位扩展是项目试验，未继承原文独立衰落假设下的恢复保证；该开发分支失败。 |
| separable nonlinear least squares；variable projection | O’Leary–Rust，*Variable Projection for Nonlinear Least Squares Problems*，§1 式 (2)–(3)、§2 式 (5)–(7)，[作者稿](https://www.cs.umd.edu/users/oleary/software/varpro.pdf) | 给定训练信道样本与相位时，解析消去一个复线性增益，再搜索相位。训练样本集合及三轮坐标更新是本项目具体近似，不称为原文算法的完整复现。 |

“完整训练信道样本匹配”“无相位证据时保留零斜率”等仅为运算描述，没有新造算法名称
或缩写。当前做的是最大匹配，不是对训练样本的边缘化；不得称作精确边缘似然或精确 EM。
固定匹配的复高斯噪声尾尺度只启发阈值，不能赋予相关样本、连续精化及失配残差未经
证明的虚警保证。详见 [进展和验证范围](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/PHASE_ESTIMATION_PROGRESS_20261022.md)。

### 2026-10-22：训练样本及相位加权候选

| 既有术语或运算 | 核验原文 | 当前使用及边界 |
|---|---|---|
| posterior model probability；integrated likelihood；posterior mean | Hoeting et al., *Bayesian Model Averaging: A Tutorial* (1999), §1，印刷 p.383，式 (1)–(3) 及紧随的均值公式，[作者单位原文](https://sites.stat.washington.edu/www/research/online/hoeting1999.pdf) | 在新增开发候选中，复高斯增益解析积分，有限训练方向和相位网格按条件概率求和；不把条件更新称为精确联合后验，也不继承原文预测性能结论。 |

复高斯协方差 `vI+szz^H` 的密度及条件均值按本候选假设直接计算；跨帧相位点估计通过
最小化明确写出的期望平方距离定义，不另造名称。高斯积分和期望损失另外核对
Rasmussen–Williams (2006) §2.1.1 式 (2.6)–(2.9)、§2.2 式 (2.30)、§2.4 式 (2.32)–(2.33)。
数学与假设边界见 `result/candidates/phase_sample_marginal_20261022/METHOD.md`。

### 2026-10-22：直接连续更新跨帧相位参数

| 既有术语或运算 | 核验原文 | 当前使用及边界 |
|---|---|---|
| expectation-maximization；phase rotation | [Shen 作者稿](https://arxiv.org/html/2412.20806v1#S3.SS3)，§III-C 式 (47)–(53) | 用后验矩构造相位二次型。直接代入本项目 `exp(j q beta_k)` 并对 beta 求导是项目推导；不声称这是 Shen 的原式 (53)。 |
| conditional Gaussian distribution | Rasmussen–Williams (2006)，§2.1.1 式 (2.6)–(2.9)，[原书](https://gaussianprocess.org/gpml/chapters/RW2.pdf) | 用神经网络传出的 Gaussian 消息构造近似先验，再计算线性观测下的均值及用户间协方差。条件公式在该 Gaussian 模型内精确，神经消息本身仍是近似。 |
| limited-memory quasi-Newton；L-BFGS-B | Byrd, Lu, Nocedal, Zhu (1995)，§1 式 (1.1)–(1.2)，[作者稿](https://users.iems.northwestern.edu/~nocedal/PDFfiles/limited.pdf)，[DOI](https://doi.org/10.1137/0916069) | 以解析梯度作连续局部相位更新；无相位网格、随机重启或训练样本匹配。不从优化器的收敛推导相位估计精度。 |

固定 Gaussian 先验的 E/M 更新与每轮重新生成神经消息的完整候选必须区分。
只有前者的边缘似然下降经过数学数值核验；后者不宣称精确 EM 或全程似然单调。
公式和预定开发范围见 `result/candidates/shen_parameter_update_20261022/METHOD.md`。

### 2026-10-22：连续协方差初始化与层内交替更新诊断

| 既有术语或运算 | 核验原文 | 当前使用及边界 |
|---|---|---|
| maximum likelihood estimation；sample covariance | [Fengler 等作者稿](https://arxiv.org/html/1910.11266v2)，§III-A 式(8)–(9) | 采用 `logdet(C)+tr(C^-1 S)`；块导频、用户功率及相位斜率的连续梯度为项目推导。当前各向同性、列独立 Gaussian 假设与实际 AFDM 相关信道存在失配；精度检查失败，未作为正式前端。 |
| message scheduling；expectation-maximization | [Shen 作者稿](https://arxiv.org/html/2412.20806v1)，§III-B、§III-C 式(47)–(53)、Algorithm 1 | 参考消息和参数交替更新的顺序，在冻结十层之间插入九次相位更新。十层网络、Gaussian 近似及共同斜率为项目适配，没有将其称为原算法复现或精确 EM。 |

受控初始化与真值信道控制均直接以所用信息描述，并明确标为 oracle 诊断。
优化目标下降、相位均方误差下降与最终信道/活动检测改善分别报告，不混为同一结论。

### 2026-10-22：完整二阶矩、协方差拟合与逐用户相位更新

| 既有术语或运算 | 核验原文 | 当前使用及边界 |
|---|---|---|
| log marginal likelihood | Rasmussen–Williams (2006)，[§2.2 式(2.30)，印刷 p.19](https://gaussianprocess.org/gpml/chapters/RW2.pdf) | 训练信道完整二阶矩构造 Gaussian 近似，实 Gaussian 公式改为复数形式。实际天线列独立性不成立，不宣称是真实信道精确似然。 |
| partial derivatives of the marginal likelihood | 同书 [§5.4 式(5.9)，印刷 p.114](https://gaussianprocess.org/gpml/chapters/RW5.pdf) | 使用 `Re tr((C^-1-C^-1 S C^-1) dC/dtheta)`；对数功率和相位斜率的导数由项目推导，并作有限差分核验。 |
| non-negative least squares；sample covariance | [Fengler 等作者稿](https://arxiv.org/html/1910.11266v2)，§III-B 式(26)–(29) | 固定相位后拟合非负用户功率；相位未知时的逐用户更新是项目扩展，整体并非仅含线性变量的 NNLS，未继承原文恢复保证。 |
| expectation-maximization；phase rotation | [Shen 作者稿](https://arxiv.org/html/2412.20806v1#S3.SS3)，§III-C 式(47)–(53) | 对期望二次型代入 `exp(j q beta_k)` 后逐用户更新。协方差拟合仅提供初始化；神经 Gaussian 消息与共同斜率为适配，不是完整复现。 |

将 `c0+2 Re sum_l c_l exp(-j l beta)` 的导数转为单位圆多项式，比较驻点及旧相位，
是直接代数运算描述。没有使用 root-MUSIC 等名称，也不自造方法名或缩写。推断没有
相位网格，但比较一个用户的多个相位驻点；训练信道仅离线累积二阶矩，推断不逐样本匹配。
推导和限制见 `result/candidates/phase_covariance_prior_20261022/METHOD.md`。

### 2026-10-22：空间协方差与相位矩的受控对照

| 既有术语或运算 | 原文定位 | 本项目使用及边界 |
|---|---|---|
| sample covariance matrix；minimum description length (MDL) | Nadakuditi–Edelman (2008)，[正式作者稿](https://math.mit.edu/~edelman/homepage/papers/signals.pdf)，§II-A 式(5)–(7)，印刷 p.2626–2627；该处回顾 Wax–Kailath | 沿用原噪声估计中的空间秩选择。秩不是活动用户数；信号特征值扣噪声、归一化并供所有用户共享是项目近似，不是原文相位估计方法。 |
| log marginal likelihood；covariance derivatives | Rasmussen–Williams (2006)，§2.2 式(2.30)、§5.4 式(5.9)，沿用前节链接 | 对固定空间特征向量基底中的各列采用不同协方差强度，直接写出 Gaussian 目标及梯度；忽略空间协方差估计不确定性，不宣称真实 AFDM 分布的精确似然。 |
| posterior expectation；phase rotation | [Shen 作者稿](https://arxiv.org/html/2412.20806v1#S3.SS3)，§III-C 式(47)–(51) | 去掉协方差项、仅使用条件均值或神经软均值是项目诊断性删减，不能继续称为完整后验期望或精确 EM。 |

来源定位校正：冻结的 `src/system/receiver/noise_estimation.py` 注释曾将 Nadakuditi–Edelman
定位写为 §I-B；本次核对正式版，相关式(5)–(7)实际位于 §II-A。冻结源码未修改，
此处记录正确出处。实际 MDL 运算和噪声估计均未变更。

### 2026-10-22：残差相位更新与已知相位对照

| 运算或术语 | 原文定位 | 本项目使用及边界 |
|---|---|---|
| message scheduling；phase rotation | [Shen 作者稿](https://arxiv.org/html/2412.20806v1#S3.SS3)，§III-C 式(47)–(53)、Algorithm 1 | 相同协方差初始化后，在冻结十层内部安排五次或九次连续相位更新；这是项目适配，未训练这些顺序，不宣称精确 EM。 |
| non-negative least squares；sample covariance | [Fengler 等作者稿](https://arxiv.org/html/1910.11266v2)，§III-B 式(26)–(29) | 先扣除其他用户的软信道点估计，再拟合剩余观测的协方差及本用户相位。扣除及相位非线性更新为项目扩展；忽略干扰不确定性，不称为原论文方法或 Shen 后验期望。 |

逐用户三角多项式驻点更新沿用上文直接代数推导，不增加新算法名称。真实活动分组
的混合相位输入明确标为 oracle 诊断；真实功率加权误差只用于事后解释，不进入推断。
用户指定的“估计相位相对已知相位无明显 AER/NMSE 损失”为比较目标；不能把描述性
差距小、优化目标下降或漏检数减少改称为统计等效证明。

## 20261022：相位参考变量替换的补充记录

- **posterior expectation / 后验期望、phase rotation / 相位旋转**：
  [Shen et al.](https://arxiv.org/html/2412.20806v1#S3.SS3)，§III-C 式(48)–(53)。
  本次沿用原文期望二次型的概念。把参考时刻改为 `(Q-1)/2`，同步旋转信道的一、
  二阶条件矩，以及解析消去每用户的共同标量旋转，均是项目自行列式的变量替换；
  未称其为 Shen 的原始更新或另造方法名。推导、半整数参考时刻下的包裹约定及
  适用限制见 METHOD.md（仅本地历史资料：`archive/result_legacy_20261023/candidates/phase_covariance_prior_20261022/METHOD.md`）。
- 基于固定活动概率门限组合连续更新与残差协方差更新，属于本项目实现选择。
  使用操作的直述，不将其包装为文献中的 EM 方法；组件目标下降不代表组合目标下降。

### 2026-10-22：固定十层内部的参数和消息更新

沿用上节 Shen §III-C 式(48)–(53) 的后验二次型出处及 Fengler §III-B
式(26)–(29) 的协方差拟合出处。以下均为本项目直接描述的操作，不另造方法名称：
将参考时刻固定在帧序列中心并随斜率更新转换 Gaussian 消息均值；将同帧协方差块
置零后拟合剩余项；用更新后的观测矩阵重算线性查询及外信息反馈。
后两项没有上述论文给出的性能保证，尤其不能把点估计扣除或未训练的网络顺序
称为精确 EM。具体式子、十层调用约束及失败结果见
实现说明（仅本地历史资料：`archive/result_legacy_20261023/candidates/phase_covariance_prior_20261022/METHOD.md`）和
开发记录（仅本地历史资料：`archive/result_legacy_20261023/candidates/shen_parameter_update_20261022/REPORT.md`）。

### 2026-10-22：本层软均值用于相位二次型

出处仍为 [Shen 作者稿](https://arxiv.org/html/2412.20806v1#S3.SS3)，§III-C
式(48)–(51)：相位目标使用信道均值与二阶矩，式(51)写作均值外积加对角方差。
本项目补充的代数事实是：若跨用户协方差为零，用户内协方差项在每用户单位模
相位下与斜率无关。可从相位优化中删去这些常数，但不能声称真实后验满足该
近似。使用神经软信道均值、共同斜率及中心参考仍为项目改写；不称为精确 EM
或原文投影规则。推导与独立数值检查见
实现说明（仅本地历史资料：`archive/result_legacy_20261023/candidates/phase_covariance_prior_20261022/METHOD.md`）。



### 2026-10-22：摘要及前五章的原文用语与推导归属

本轮修改 `paper/TWC` 当前稿件，作者再次要求采用 Cai 与 Huang 的原文术语。
三项贡献保留为 AFDM 传输与输入输出模型、基于得分的生成式信道先验、深度展开 MP 接收机。
具体对照及修改依据见 修订记录（历史路径，见迁移记录：`paper/DU/checks/logic_provenance_20261022/README.md`）。

| 原文用语或结果 | 原文定位 | 本稿使用及归属 |
|---|---|---|
| score-based generative channel prior / 基于得分的生成式信道先验 | Cai 正式版（仅本地历史资料：`reference/literature/cai2026.pdf`），§I-A，第3576页；§IV-A，第3582页 | 直接沿用这一名称。训练样本具有连续时延与多普勒频移，是样本生成说明，不另命名先验。 |
| AFDM effective channel / AFDM 有效信道；fractional delay and fractional Doppler；off-grid effects | Huang 正式版（仅本地历史资料：`reference/literature/huang2026.pdf`），§II，第2950页，式(4)–(5)及后文；§III-A，第2951页，式(6)–(7) | 描述学习对象和off-grid动机。多天线张量、长前缀条件、跨帧排列用本稿公式直接说明。连续基函数的坐标写法属于本稿模型表示，不称为原文逐字给出的公式。 |
| multi-frame transmission；quasi-static channel | Shen 作者稿（仅本地历史资料：`reference/literature/shen2025.pdf`），§II，PDF第4–5页，Proposition 1，式(8)–(10)及Q=8/Q=25讨论 | 借鉴共享信道增加观测及检查块内物理变化的思路。本稿的跨帧分离由AFDM路径算子直接代入推出。 |
| Gaussian extrinsic message；channel denoising；device activity denoising | Cai，§III-A/B，第3579–3581页，式(6)–(11)、(35)–(42) | 作为已有推断结构引用。现有可训练参数和残差方差构造沿用项目定义及既有来源记录。 |
| posterior mean；Tweedie's formula；denoising score matching | Cai，§III-B式(35)–(38)，第3581页；§IV-A/B，第3582页 | 区分已有混合均值与score关系、Gaussian消息近似和接收机训练。活动概率进入残差与后续消息的训练依赖由本项目计算图确认。 |
| equivalent Gaussian observation；damping | Cai，§V-B1，第3583页，式(57)之前的说明 | 原文支持感知矩阵和系统维度影响高斯近似。相位改变导频行内积属于本稿代数结论，不据此声称高斯近似必然失效。 |

新增圆轨道几何界直接从本稿 `eq:geometry` 求导得到：
`nu_dot=(fc/c0)[v^T(I-u u^T)v/r-u^T a]`；用 `r>=h` 与
`||a||=v^2/(R_E+h)` 上界得到正文的 `B_nu`，再积分得到时延变化及相位误差界。
这些是本稿自己的推导，数值来自 `src/system/config.py` 及场景几何常量；不是 Shen 的数值。
计算记录（历史路径，见迁移记录：`paper/DU/checks/logic_provenance_20261022/model_scale_check.json`）保留所有检查的帧数，
没有将几何上界作为接收机性能实验或块内所有信道参数恒定的证明。

联合训练的具体目标、参数启用时机和梯度路径沿用既有实现。
它们不归为 Cai/Huang 已提出的方案，也没有仅凭计算图宣称必然优于分开训练。
原有 deep unfolding、progressive training、残差方差参数化及自然参数阻尼的文献定位继续有效。
摘要重心和第四章顺序调整属于作者授权范围内的写作选择，不作为文献定理或TWC硬性标准。

### 2026-10-22：直接非负功率与固定消息边缘似然导数

沿用 [Fengler 作者稿](https://arxiv.org/html/1910.11266v2) §III-A 式(8)–(11) 的
Gaussian 协方差目标和非负功率约束，以及 [GPML §5.4 式(5.9)，印刷p.114](https://gaussianprocess.org/gpml/chapters/RW5.pdf)
的协方差导数。项目对非负功率作尺度变换、对共同相位斜率作尺度变换，并显式求出
`Y-A(beta)M` 中均值随相位变化的导数；这些是直接运算描述，没有新增技术名称。
所用 Gaussian 消息及天线列独立假设仅为近似，不称为真实信道精确似然，也不称为
Shen 原始 EM 的完整复现。公式、数值检查和未采用结果见
实现说明（仅本地历史资料：`archive/result_legacy_20261023/candidates/phase_covariance_prior_20261022/METHOD.md`）。


### 2026-10-22：相关Gaussian条件矩与固定功率相位更新

[GPML第2章](https://gaussianprocess.org/gpml/chapters/RW2.pdf) §2.1.1式(2.6)–(2.8)
（印刷p.9）的Gaussian后验均值/协方差公式、式(2.9)（p.11）的预测分布，以及§2.2式(2.30)（p.19）的
marginal likelihood，是本轮相关条件矩和协方差目标的依据。
[第5章](https://gaussianprocess.org/gpml/chapters/RW5.pdf) §5.4式(5.9)（p.114）
给出协方差参数导数。将完整训练二阶矩归一化后近似消息协方差形状、固定已有功率
只优化共同相位斜率，均是本项目的直接运算描述，不是文献另一个命名方法。
实际神经消息误差不必服从该Gaussian近似，天线列独立也只是近似。

残差式 `v_res=(||Y-AM||²-Q D noise)/(D||A||²)` 来自独立、零均值、各向同性
误差与噪声的二阶矩展开；本项目使用 `max(v_message,v_res)` 仅作候选检查。
未把这个proxy称为精确后验校准或Shen原始EM。真值相位干预是明确标注的事后诊断，
不称为可部署算法或统计等效检验。公式、合成检查及不利结果见
实现说明（仅本地历史资料：`archive/result_legacy_20261023/candidates/phase_covariance_prior_20261022/METHOD.md`）和
开发报告（仅本地历史资料：`archive/result_legacy_20261023/candidates/shen_parameter_update_20261022/REPORT.md`）。


### 2026-10-22：TWC正文中H与X的指代区分

沿用Huang正式版§II式(4)–(5)、第2950页的AFDM effective channel，以及Cai正式版§II-A、Table I、式(4)附近、第3578页的`X_k=alpha_k H_k`。在本稿共用语境中，`H_k`表示AFDM信道张量，`X_k`为它与活动指示量的乘积；后者直接用公式和符号说明，不另外命名。条件信道估计、活动概率及其乘积仍依据Cai§III-B式(35)–(38)、第3581页。术语未改变，修订只消除同一简称对不同对象的指代歧义。具体修改和本项目初始化、梯度路径依据见行文复核记录（历史路径，见迁移记录：`paper/DU/checks/style_logic_review_20261022/README.md`）。

### 2026-10-22：十层内部的斜率及信道旋转更新

沿用上文已核对的 Shen §III-C 式(48)–(53) 的期望二次型和相位旋转，及 GPML
§2.2式(2.30)、印刷p.19的 Gaussian marginal likelihood。固定用户的共同单位模
信道旋转并解析消元后，最大化复相关和的模平方；所得斜率目标为三角多项式，
使用驻点求值。该消元、共同斜率和按已有活动概率组合提议均为本项目直接列式，
没有把它们命名为文献中的新方法或称作Shen原始更新。

对扣除其他用户软信道均值后的剩余观测使用固定功率Gaussian目标，亦只是近似。
神经消息、天线独立假设及两个提议的组合不保证精确后验或整体目标下降。原110层
历史实现仅复用代数辅助函数，当前执行结构为十层各一次；具体公式和归属见
实现说明（仅本地历史资料：`archive/result_legacy_20261023/candidates/phase_covariance_prior_20261022/METHOD.md`）。

## 原场景上的初值半步、条件均值和相位更新次数检查

继续沿用前文已核对的 Shen §III-C 式(48)–(53) 的期望二次型及相位旋转，
与 GPML 第2章 §2.1.1 式(2.6)–(2.8)、印刷p.9 的Gaussian条件均值和协方差。
本轮“网络软均值加Gaussian条件协方差”直接描述项目实际代入，不称为文献提出的
新算法或精确神经后验。相位初值取主值差的一半、按固定二次型变化停止坐标扫描，
均直接给出公式和数值条件，不将数值停止解释为相位正确或统计收敛保证。
公式和适用边界见实现说明（仅本地历史资料：`archive/result_legacy_20261023/candidates/phase_covariance_prior_20261022/METHOD.md`）。

## 原场景上的初值更新惩罚、连续重求解及完整复现

沿用已核对的 GPML §2.2式(2.30)、印刷p.19的Gaussian marginal likelihood，
以及§5.4式(5.9)、印刷p.114的协方差参数梯度；共同相位斜率模型和固定功率限制是本项目
明确列式的近似。`M*L+lambda*改变坐标的个数`、固定lambda=1及接受坐标的连续重求解
直接描述操作，不另造方法名，不称为AIC、BIC、似然比检验或校准置信度。
神经层间二次型继续沿用前文Shen §III-C式(48)–(53)的出处及本项目改写边界；
本次组合不等于Shen原始EM，也不承诺整体目标或实际相位误差下降。
参见实现公式（仅本地历史资料：`archive/result_legacy_20261023/candidates/phase_covariance_prior_20261022/METHOD.md`）。

## 2026年10月22日 单一高斯边缘似然下的广义EM相位更新

`generalized EM algorithm`（GEM，广义EM算法）采用 Dempster、Laird、Rubin (1977)，
*Maximum Likelihood from Incomplete Data via the EM Algorithm*，§3、印刷p.7的定义与式(3.5)，
以及Theorem 1、式(3.7)–(3.10)的单调性；p.8明确区分这些性质与收敛到最大似然解。
[原论文](https://www.maths.usyd.edu.au/u/jchan/GLM/Dempster1977EM.pdf)。
本项目只对声明的高斯近似模型使用精确条件矩，并令每次参数更新不增大同一个负条件期望目标。
不将神经网络的软输出直接称为精确后验，不将整个冻结十层接收机称为EM算法。

条件均值、条件协方差及边缘似然沿用前文 GPML §2.1.1式(2.6)–(2.8)、p.9和
§2.2式(2.30)、p.19；连续非负方差尺度与协方差似然沿用 Fengler等 §III-A式(8)–(11)。
相位期望二次型对应 Shen §III-C式(48)及其二阶矩构造，但共同斜率约束、训练二阶矩先验
及由三角多项式驻点求解坐标参数是本项目明确列式的扩展，没有自拟命名或宣称完整复现Shen。
推导与边界（仅本地历史资料：`archive/result_legacy_20261023/candidates/phase_gaussian_em_20261022/DERIVATION.md`）。

## 2026年10月22日 连续相位求解与已知活动先验

`L-BFGS-B` 使用 Byrd、Lu、Nocedal、Zhu 的 *A Limited Memory Algorithm for Bound Constrained Optimization*，§2，作者预印本p.2–3；[原文](https://users.iems.northwestern.edu/~nocedal/PDFfiles/limited.pdf)。数值停止与投影梯度的区别依照 *Algorithm 778: L-BFGS-B* §5，作者预印本p.6；[原文](https://users.iems.northwestern.edu/~nocedal/PDFfiles/lbfgsb.pdf)。不将函数容差停止称为全局收敛或梯度达到指定阈值。

`maximum a posterior probability (MAP) estimation` 与独立 Bernoulli 活动先验采用 Jiang、Cui，*ML and MAP Device Activity Detections for Grant-Free Massive Access in Multi-Cell Networks*，§III-B、arXiv预印本p.13–16式(11)、(13)，Appendix D p.34式(36)；[原文](https://arxiv.org/pdf/2106.10438)。本项目的活动项系数 `log((1-rho)/rho)/M` 直接由已知活动概率导出；共同相位斜率、相关有效信道二阶矩及连续尺度拟合均明确为项目扩展，不称为原文算法复现。

“功率方向导数的驻点作为连续相位起点”“在固定活动集合内连续优化”仅描述公式和操作，不另造方法名。统一目标仅指相位前端，冻结十层网络不被包装为其精确后验求解器。见连续求解推导（仅本地历史资料：`archive/result_legacy_20261023/candidates/phase_likelihood_solver_20261022/DERIVATION.md`）及活动先验推导（仅本地历史资料：`archive/result_legacy_20261023/candidates/phase_activity_prior_20261022/DERIVATION.md`）。

### 2026年10月22日 固定神经消息下的非零均值边缘似然与广义EM

沿用 GPML 第2章 §2.1.1 式(2.6)–(2.8)、p.9和§2.2式(2.30)、p.19的 Gaussian 条件矩与 marginal likelihood，第5章§5.4式(5.9)、p.114的协方差导数。非零均值残差的导数、共同斜率和单位模信道旋转的坐标变换由本项目直接列式；不另命名为已有方法。

固定高斯消息时的一次条件矩计算和降低期望二次型，使用 Dempster等§3、p.7、式(3.5)、Theorem 1式(3.7)–(3.10)定义的 generalized EM；相位二次型沿用Shen§III-C式(48)–(53)的出处及上述项目改写边界。消息随神经层变化，不能因此宣称整个十层网络满足固定全局目标的EM单调性。详见非零均值目标（仅本地历史资料：`archive/result_legacy_20261023/candidates/phase_conditional_likelihood_20261022/DERIVATION.md`）与各向同性消息更新（仅本地历史资料：`archive/result_legacy_20261023/candidates/phase_message_gem_20261022/DERIVATION.md`）。

## 2026年10月22日 STMP 复用高斯消息相位更新

STMP 使用同一 generalized EM（广义EM）定义、同一 GPML 高斯条件矩和 Shen 期望二次型出处，章节、式号及适用范围见上一条。本项目将 STMP **阻尼后的实际高斯外信息**对应到该固定消息模型；活动概率已经通过联合信道矩进入外信息，不再另乘概率或按活动判决筛选用户。缓存信道均值同乘 `exp(i theta_k)`、重建线性算子、重置停止计数以及第60至140次的更新安排，均是明确写出的实现操作，不包装成文献已有的新方法名称。固定消息的目标不增加不能推广为整个 STMP 的全局单调性。见[STMP 接入说明](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/STMP_PHASE.md)。

### 2026年10月22日 活动概率 条件信道矩与反馈误差的候选方案

沿用 [Wei–Yuan 原文](https://arxiv.org/html/2610.17785v1) §III-A、§III-D 的 finite-depth unfolding 和训练思路，以及 §III-C 式(12)的 residual-based variance estimate；保留 [Cai 等原文](https://arxiv.org/html/2506.00581v2) §III-B3 式(35)–(42)的有效信道均值、混合方差、Gaussian projection 与 extrinsic message 定义。Cai §III-B2 式(26)–(30)采用 Gaussian 外信息近似计算活动概率，不能描述成由任意先验的单点均值和方差精确得到边际似然。

局部 Gaussian 查询下的条件均值 Jacobian 与条件协方差采用 [Dytso–Poor–Shamai](https://arxiv.org/pdf/2104.01883) §IV Proposition 1、式(22)、PDF p.5。活动 log odds 的梯度及有效信道均值的导数由本项目直接求导得到；固定复方差 v 时实坐标噪声方差为 v/2，不能混用整条接收机的总导数。该关系只作理想局部模型诊断，不作为有限 AFDM 查询的无条件约束。

条件误差、中心后验方差与学习反馈参数保持前文 D17–D21、D29–D30 的区分。以固定有限均值的平方误差训练正尺度，使用 Gaussian 负对数密度的标量形式 log(t)+e/t；函数空间最优值是相应特征下的条件误差。其代入 p*t+p*(1-p)*||mu||²/D 定义近似混合分布的方差，不自动等于真实联合条件误差。方案中的小型误差输出分支、分阶段梯度安排及配对选模属于本项目待验证设计，不另造算法名称，也不声称 Wei 或 Cai 已验证其性能。

具体关系、实现接口和对照组见 改进方案（历史路径，见迁移记录：`paper/DU/docs/WEI_CAI_ACTIVITY_CHANNEL_VARIANCE_PLAN_20261022.md`）。本轮仅进行确定性概率与代数核验；不启动训练、批量接收机实验或切换当前主线。

### 2026年10月22日 条件接收机的查询尺度与活动反馈核查

线性估计的 decorrelated 定义沿用 [Ma、Ping，Orthogonal AMP](https://arxiv.org/pdf/1602.06509v3) PDF p.3 式(12)–(15)；相应误差假设见 p.4 Assumptions 1–2，残差估计见 p.5 式(30)–(31)。本项目对当前 gamma 参数化直接计算固定标量参数时的迹导数与工作模型误差协方差；这些是代码公式的推导，不是 OAMP 对本项目有限 AFDM 接收机的保证。Gamma=1 只恢复所述迹条件及工作模型平均误差标签，不能据此称查询为独立 AWGN。

沿用 [Wei、Yuan](https://arxiv.org/html/2610.17785v1) §III-B 式(6)–(10)、§III-C 式(11)–(12)和 [Cai 等](https://arxiv.org/html/2506.00581v2) §III-B3 式(35)–(42)对 Gaussian 消息、经验残差估计及活动混合矩的表述。当前残差的二阶矩展开、零空间反例及概率到均值和共同尺度的导数均由项目独立列式，不能称为文献已证明的退化原因。旧冻结 STMP 同样采用各向同性投影。

Gaussian 查询下真实条件均值的 Jacobian—协方差关系继续采用 [Dytso、Poor、Shamai](https://arxiv.org/pdf/2104.01883) §IV Proposition 1、PDF p.5 式(22)。完整有效信道映射为 p*mu，其导数包含活动概率项；任务微调网络的导数只作局部增益诊断，不能自动视作真实后验方差。

围绕固定有限估计器的 Gaussian 标量负对数密度 log(t)+e/t，其最优输出是对应特征下的条件误差；本文将之称为误差尺度，继续区别于中心后验方差。精度增长上限、已存修正方向的真值最优缩放、可观测与零空间误差分解均直接给出公式，不新增方法名称；前者只保证指定上限，后两者仅为诊断。

完整公式、既有数据证据、未验证候选与回退条件见 条件接收机核查（历史路径，见迁移记录：`paper/DU/docs/CONDITIONAL_RECEIVER_AUDIT_20261022.md`）。本轮不修改冻结接收机，也不启动训练或接收机实验。

### 2026年10月22日 Cai 公开代码的固定 Gaussian 活动概率对照

用户随后授权小规模试验。本次沿用 [Cai v2 §III-B2 式(26)–(30)](https://arxiv.org/html/2506.00581v2#S3.SS2.SSS2) 的 Gaussian 活动证据表达，同时区分论文中的学习外信息与 [作者固定提交](https://github.com/chang-cai/score-massive-connectivity/blob/0c75680c966dcb8e46250de146f4c27e9294c283/main_stmp_jadce.py#L212-L229) 实际调用的 lambda_post_gaussian。公开代码第214–215行设置外信息均值为零、方差为固定信道功率，得到 logit(rho)+s*||r||²/[v*(v+s)]−D*log(1+s/v)。

“固定 Gaussian 活动近似”直接描述这一实现，不是新方法名称。AFDM 实虚坐标下 D=4096 为复维数，方差 v 为每复系数方差。训练功率、活动先验和0.5门限保持；仅将活动输出或反馈替换为解析式。不得将该对照称为完整 Cai STMP 或论文学习外信息版，也不得把当前联合残差尺度当作活跃条件方差。

公式、数据边界及配对设计见 试验说明（仅本地历史资料：`archive/result_legacy_20261023/candidates/cai_analytic_activity_20261022/METHOD.md`），实际结果以该目录保存的报告为准。试验保留冻结接收机和权重，不涉及训练。

### 2026年10月22日 冻结分类器与损失反传的区别

参数冻结以及停止指定训练目标向另一网络反传，参照 [Cai §IV-C、式(54)后的说明](https://arxiv.org/html/2506.00581v2#S4.SS3)。原文讨论一阶、二阶 score 网络，不能援引为本项目冻结活动分类器后更稳定的结论。当前活动 BCE 经固定分类器影响条件均值与先前查询的关系，按现有计算图直接应用链式法则；属于项目推导，不另起算法名称。PyTorch 参数冻结、输入梯度和 no-grad 的实现区别参照其官方 Autograd mechanics 文档。候选范围和未验证结论见 冻结分类器方案（历史路径，见迁移记录：`paper/DU/docs/FROZEN_CLASSIFIER_SCORE_ONLY_PLAN_20261022.md`）；本轮不启动训练。

### 2026年10月22日 Cai 的信道样本与多噪声训练范围

`channel dataset`、`noise levels` 和 `exponential moving average (EMA)` 沿用 Cai §VI-A1–2、正式版印刷 p.3585；多噪声 denoising score matching 目标依据 §IV-B 式(47)–(49)。单用户信道样本、多用户接收场景及接收 SNR 分别按实际生成过程说明，不将原文 41 个去噪噪声水平改称 41 个展开训练工况。Cai §IV-C 式(54)后的梯度安排见正式版 p.3583，仍不构成本项目冻结活动分类器的稳定性证明。当前提出的接收 SNR 连续抽样属于本项目实验设计。数值设置、公开配置与论文的差异，以及已中断试跑的状态，见 训练与场景核查（历史路径，见迁移记录：`paper/DU/docs/CAI_TRAINING_SCENARIOS_20261022.md`）。

### 2026年10月22日 Wei 的逐层加深与共同训练

`trained progressively layer by layer`、`each new layer trained jointly with the preceding layers`、`auxiliary supervision` 采用 [Wei、Yuan v1](https://arxiv.org/pdf/2610.17785v1#page=3) §III-D、PDF p.3 的原义。§V-A、p.4 报告五层、独立 score 网络及损失权重 0.2/1。当前深度内共同更新与跨训练阶段逐步增加深度需区分；原文未要求前层永久冻结，也未给出本项目“一轮新层适配加两轮共同训练”的具体安排。现有十层权重的训练历史与仅一阶候选的差别见 训练顺序核查（历史路径，见迁移记录：`paper/DU/docs/FROZEN_CLASSIFIER_SCORE_ONLY_PLAN_20261022.md`）。

本次重新训练采用上述顺序，保留前层共同更新，但固定原 STMP 分类器及校准标量；这一参数范围和活跃条件信道损失是项目选择，不能称为 Wei 全部训练方案的复现。原文 §V 未交代 M=32/64、随机 DFT/PMI 各曲线的权重是否共享，不能将其消息模型假设失配结论改写为跨工况训练测试的泛化保证。具体来源与范围见 重新训练协议（历史路径，见迁移记录：`paper/DU/docs/SCORE_ONLY_PROGRESSIVE_20261022.md`）。

### 2026年10月22日 不同工况下的消息误差诊断

IID、零均值 Gaussian、与信号独立以及 decorrelated 的适用范围，沿用 [Ma–Ping OAMP](https://arxiv.org/pdf/1602.06509v3#page=4) §III-E Assumptions 1–2、§III-F Proposition 1、PDF p.4–5；不将不相关写成独立。二阶矩非对角部分占比、标准化四阶矩、实测 MSE 与方差标签之比均直接给出计算公式，不包装为文献命名的新方法。Gaussian 替换和真值误差方差只用于诊断，不能称为部署算法或独立识别某项误差结构的因果证据。设计和统计边界见 [消息误差诊断](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/MESSAGE_AWGN_CONDITIONS_20261022.md)。

后续训练使用同一文献含义的逐层共同训练及辅助监督。用户撤回 30 种 K/Q 混合方案，固定 K=40、Q=16、活动概率 0.1，增加到 3000 个独立物理场景；这属于同一系统配置内的样本多样性，不能改称已验证的跨工况泛化。冻结分类器、固定校准标量和仅活跃条件信道损失仍是本项目选择，见 当前训练协议（历史路径，见迁移记录：`paper/DU/docs/SCORE_ONLY_FOCUSED_PROGRESSIVE_20261022.md`）。


### 2026年10月22日 连续相位更新时的停止判断

本候选沿用本文已有的 Gaussian 消息、外信息及活动混合矩术语：Cai §III-B 式(25)–(42)，相位的条件矩及固定消息目标见本表已有 GPML §2.1.1 式(2.6)–(2.8)、Shen §III-C 式(48)–(53)记录。本次只使用“相对变化”“活动概率变化”“停止条件”等直接描述数值操作的表述，不另造方法名称。

每10轮比较一次活动加权信道、当前相位算子下的预测观测及输入/反馈协方差，连续两次满足阈值后停止，是本项目定义的数值规则。0.005、0.001及两个周期不是上述论文给出的配置；不能称为其收敛定理，也不能把输出稳定等同于估计准确。具体公式、阈值及数据边界见 候选说明（仅本地历史资料：`archive/result_legacy_20261023/candidates/stmp_phase_stopping_20261022/METHOD.md`）。

### 2026年10月23日 STMP相位更新后的消息状态核对

Gaussian条件矩沿用 [GPML §2.1.1，式(2.6)–(2.8)，印刷p.9](https://gaussianprocess.org/gpml/chapters/RW2.pdf)；期望二次型依据 [Shen §III-C，式(48)–(53)](https://arxiv.org/html/2412.20806v1#S3.SS3)。generalized EM（广义EM）的固定模型下降性质核对 [Dempster、Laird、Rubin，§3，印刷p.7，式(3.5)、Theorem 1及式(3.7)–(3.10)](https://web.mit.edu/6.435/www/Dempster77.pdf)。2026-10-23重新核对上述原文；该EM扫描件包含一页封面，文件第8页对应印刷p.7。

“只更新相位斜率”“只旋转反馈均值”“重新计算线性查询”均直接描述本项目的操作，不是新方法名称。首帧相位固定为1、常数相位吸收入信道以及中心化参数换算见 候选推导（仅本地历史资料：`archive/result_legacy_20261023/candidates/stmp_phase_integration_20261023/DERIVATION.md`）。旧记录中缓存均值一并旋转是当时的实现选择，不能解释成该物理模型必需的坐标变换；真实观测预测保持不变还要求算子做反向变换。当前正在分别验证斜率约束与反馈消息更新后的缓存处理，不将单个高斯目标下降推广为全套神经迭代收敛。

实测查询误差与方差标签之比按 \(\|r-H/s\|_F^2/(D v)\) 逐用户计算，真值只用于更新结束后的诊断，不进入接收机；比值接近1也不证明误差独立或服从Gaussian分布。


### 2026年10月23日 按有限功率处的边缘似然比较相位初值

沿用 GPML §2.2式(2.30)、印刷p.19的 log marginal likelihood，以及[第5章§5.4式(5.9)、印刷p.114](https://gaussianprocess.org/gpml/chapters/RW5.pdf)的 covariance derivatives。2026-10-23再次核对原文PDF第10页（零基索引9）。复数Gaussian形式、逐用户非负协方差强度及三角多项式由项目直接列式。零功率处负方向导数最大与非零功率处负对数似然最小不是同一个优化问题。当前候选比较正方向导数驻点对应的实际似然起点，保留原点并做原局部优化；这些是操作描述，不另命名为已有方法，也不宣称全局最优。所用正功率尺度不是观测似然的完整二阶导数。真值纠正初始相位的分支仅是oracle诊断，不进入算法性能或采用条件。见公式、全部分支和验证边界（仅本地历史资料：`archive/result_legacy_20261023/candidates/stmp_phase_initial_candidates_20261023/METHOD.md`）。


### 2026年10月23日 条件迭代稳定窗口与相位更新时机

“条件迭代的稳定窗口”“每20轮检查输出变化”直接描述数值判据，不包装为已有具名算法。固定Gaussian消息的条件矩和广义EM边缘目标下降仅沿用前述GPML与Dempster定位；其定理不证明当前神经条件迭代、首次更新时间或整体停止的收敛性质。六分支同输入实验证明一个具体输入的第20轮消息尚未稳定，此时更新相位会使结果变差；候选用既有窗口决定更新时机，整体停止同时检查条件迭代与跨检查区间的物理输出变化。数学断言与经验流程明确区分，见说明与全部对照（仅本地历史资料：`archive/result_legacy_20261023/candidates/stmp_phase_settled_20261023/METHOD.md`）。

### 2026年10月23日 EC归一化诊断与逐用户相位候选

Expectation Consistent（EC，期望一致）近似采用 [Opper、Winther 2005](https://www.jmlr.org/papers/volume6/opper05a/opper05a.pdf) §3，印刷p.2182式(13)–(18)、p.2183式(19)–(20)。三个归一化量组合与矩匹配来自这些公式；§3及§3.1指出驻点可能为鞍点，近似量也不是一般的真实自由能界。[Fletcher、Schniter v4](https://arxiv.org/html/1602.08207) §III式(22)–(29)、Theorem 1讨论EM-VAMP固定点；§IV开头明确不保证迭代收敛。2026-10-23重新核对原文。本项目分别训练的矩网络与活动分类器未证明对应同一精确先验，不能套用其固定点或收敛结论。实际六分支诊断的EC形式排序失败，未用于相位接受或停止，见复算报告（仅本地历史资料：`archive/result_legacy_20261023/candidates/stmp_phase_evidence_diagnostic_20261023/REPORT.md`）。

“固定其他用户高斯消息”“检查全部用户的相位候选”“局部活动证据增加量”是操作说明，不是文献中的新方法名称。条件高斯均值、迹投影的外信息查询、活动混合归一化因子分别沿用前述GPML、Cai定位；将这些操作用于相位驻点候选并按局部分类器证据排序，是本项目待验证设计，不称为完整观测似然或广义EM步骤。公式、标量近似、选择规则及验证边界见候选设计（仅本地历史资料：`archive/result_legacy_20261023/candidates/stmp_phase_hypotheses_20261023/METHOD.md`）。原普通相位细化与此活动候选步骤分别记录，不能把前者的固定消息下降性质赋予后者。

后续独立候选（仅本地历史资料：`archive/result_legacy_20261023/candidates/stmp_phase_supported_hypotheses_20261023/METHOD.md`）要求新相位对应的局部查询达到已有0.5活动判决门限，且沿用0.001概率变化容差；全部用户仍生成候选，当前活动判决不用于提前筛除用户。这里只描述基于训练分类器的候选资格规则，不把搜索后的局部概率称为精确联合后验，也不声称是文献中的联合最大后验方法。跨周期比较改为仅记录具备实际更新条件的边界，并在候选替换后保留普通相位细化；这些是本项目的执行与停止规则，不新增收敛定理或方法名称。


### 2026年10月23日 相位初始化的GPU执行

相位初始化仍沿用本表 GPML §2.2式(2.30)、§5.4式(5.9)及既有连续非负功率、相位梯度定义。
用Z=C^-1 Y把C^-1 S C^-1写成ZZ^H/M是矩阵乘法的重组，不作协方差低秩截断，不另命名算法。
GPU、双精度和CUDA Graph仅描述实现；接口依据为PyTorch 2.7 `torch.linalg.cholesky_ex` 与 CUDA semantics
的 CUDA Graphs/Constraints，原文链接、精度检查及不同浮点路径的边界见
实现说明（仅本地历史资料：`archive/result_legacy_20261023/candidates/stmp_initialization_runtime_20261023/METHOD.md`）。

### 2026年10月23日 活动门限的统计量和条件依赖

`threshold factor` 沿用 [Zhou，PDF p.10，§IV-C 式(27)及脚注3](https://arxiv.org/pdf/2201.02084v2#page=10)：固定相对系数不等于固定绝对能量门限。`fixed threshold setting` 和 `dynamic threshold setting` 对应 [Quayum 等，ICC 2018，PDF p.4，§IV-A 式(9)、Fig.5](https://personal.utdallas.edu/~hxm025000/GrantFreePilots_ICC2018.pdf#page=4)，仅在其导频检测模型下解释，不能将任意 SNR 分档拟合称为该论文方法。

`threshold-based detector` 与有效方差的解析依赖，依据 [Liu–Yu，PDF p.6，§III-E Definition 1、式(30)](https://arxiv.org/pdf/1706.06438v2#page=6)。τ_t² 为 AMP 有效误差方差，不能偷换成物理噪声方差。用户活动 `posterior probability` 依据 [Cai，§III-B2 式(29)–(31)](https://arxiv.org/html/2506.00581v2#S3.SS2)，与归一化用户能量分数有本质区别。相等错误代价下的 0.5 判决是条件风险比较的直接推导，不等于声称 Cai 公布了该数值，也不保证条件漏检率等于虚警率。

“各方法一个跨 SNR 固定值”“估计 SNR 最近节点查表”“测试集逐点选最优门限”均直接描述实现或评估操作，不包装成已有命名算法。原文定位、适用条件及当前实验建议见 [门限核查](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/BASELINE_ACTIVITY_READOUT.md)。

### 2026年10月24日 用户活动判决与检测目标

`log-likelihood ratio (LLR)` 与用户 Bernoulli 活动消息依据 [Zhang 等，IoTJ 2020作者稿](https://arxiv.org/html/2005.09826)，§III-A2–A3式(15)–(19)，PDF pp.6–7；原文最终证据含活动先验，比较零。等错误代价下用户后验比较0.5、未含先验的似然比比较(1-rho)/rho，是条件风险与Bayes公式的直接推导，不将任意路径概率聚合称作用户后验。

`Neyman–Pearson` 检测与门限设计的GFRA例子为 [Zhao–El-Hajjar–Yang，OJVT 2025](https://eprints.soton.ac.uk/505524/)，*Joint User Activity Detection and Channel Estimation in MC-GFMA Systems by Block Sparse Bayesian Learning With Threshold Optimization*，§V-B式(24)–(31)。本次通过机构记录及检索返回的原文段落核读，整份PDF下载不可用。固定虚警约束与最小总体AER目标不同；该文Gamma拟合不构成当前AFDM估计能量的分布保证。

CG-AD、BI-AD仍采用本表已有Ke出处，补充§III-B及§V Fig.6/8：空间域与角域的检测优劣可能反转，不能将空间域90%投票套用到每用户仅少数非零路径的字典。物理噪声归一化能量仅描述项目待验证统计量，不自动称为恒虚警率检测。原文、实现对应及不重推断可验证的范围见 [活动检测核查](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/ACTIVITY_DETECTOR_REVIEW_20261024.md)。

### 2026年10月24日 STMP低SNR的冻结查询诊断

AWGN 查询模型沿用 [Cai 等，§III-B1 式(20)](https://arxiv.org/html/2506.00581v2#S3.SS2.SSS1)；同文 §V-B1 明确区分大系统、右旋转不变随机测量矩阵的依据与有限维、特定测量矩阵的实际情况，不能把工作模型当作有限 AFDM 查询的分布保证。活动加权均值沿用其 §III-B3 式(35)，本项目实际输出及反馈按 `src/algorithm/STMP/denoiser.py` 和 `iterations.py` 的代码关系核对。2026-10-24 已核读上述原文。

本次直接计算逐用户实测误差功率 `mean(abs(r-x)**2)`、沿真值信道的实投影系数 `Re(sum(conj(x)*r))/sum(abs(x)**2)` 以及误差空间二阶矩的非对角平方和占比，不将这些量命名为新方法。`x` 为按冻结尺度归一化的有效信道；实投影系数不是已识别的系统增益。以实测误差功率替换方差标签会同时重算一阶条件均值与活动输出，不等于单独改变分类器的方差特征；单次误差功率也不等于已知条件噪声方差。

同误差功率 AWGN 替换仅为合成诊断，方差按期望匹配，不对每次噪声样本强制归一化。真值只在原接收机完成后用于这些分支，结果不反馈。替换同时改变相关性、信号依赖及噪声实现；对原漏检用户重新抽样还包含结果筛选与均值回归影响，不能据此独立识别反馈导致漏检的因果关系。固定抽样、分支和验证门限见 [计划](../../result/snr_comparison/data/low_snr_query_check_20261024/PLAN.json)，完成状态及全部结果以该目录记录为准。

### 2026年10月24日 结构化观测下的消息失配文献复核

本次将已有术语按原文版本重新定位，不覆盖历史候选与负结果。综合判断见 [STMP 消息调研](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/STMP_MESSAGE_AWGN_REVIEW_20261024.md)，详细书目和核验范围见 [来源目录](../../reference/reviews/stmp_message_awgn_review_20261024)。以下 PDF 页码均从指定作者稿第一页起计数；不能与期刊页码混用。

| 原词或忠实译名 | 本次核验的原文定位 | 对当前项目的使用边界 |
|---|---|---|
| non-separable denoisers；uniformly Lipschitz；state evolution / 非可分去噪器；统一 Lipschitz；状态演化 | [Fletcher 等，JSTAT 2019](https://phil-schniter.web.app/pdf/jstat19.pdf)，§3 Definitions 1–2、Assumption 1，§4.1式(12)、§4.2 Theorem 1，PDF pp.5–9 | 可包含满足条件的 CNN；右奇异向量 Haar、独立性及大系统条件不自动覆盖固定重复 AFDM。不能把非可分性本身称作不适用的充分原因。 |
| denoising-based Turbo-CS；extrinsic / 基于去噪的 Turbo-CS；外信息 | [Xue–Ma–Yuan 2017 v1](https://arxiv.org/pdf/1703.08756v1)，§III-A/B式(13)–(21)，PDF pp.3–4；§V-C式(53)–(54)，pp.8–9 | 通用去噪器与精确 MMSE 外信息关系应区分；相关图像的正面随机化对照改变了实际测量矩阵，不能等同于接收端纯坐标变换。 |
| OAMP-MMV；Gram–Schmidt orthogonalization / 多测量向量 OAMP；Gram–Schmidt 正交化 | [Cheng 等 2023 v1](https://arxiv.org/pdf/2304.08038v1)，§III-B式(15)–(18)，§III-D Assumption 18，§III-E/F式(28)–(34)，PDF pp.5–6；§I-D p.2 | 消息保留矩阵增益及列间协方差，修正量为矩阵；作者明确该稿 SE 论述为直观分析。Haar 与局部函数条件不能省略；列间有色 Gaussian 不等于各元素 iid AWGN。 |
| MMV-BAMP；joint decorrelation / MMV 贝叶斯 AMP；联合去相关 | [Hannak 等 2018 v2](https://arxiv.org/pdf/1712.04893v2)，§II-B/C式(9)–(11)，§III-A/C Algorithm 2、Theorem 1、式(12)–(16)，PDF pp.3–4 | Jacobian 和 SE 均可为矩阵；变换后先验、估计器与导数须一起变化，一般先验不保证后续误差状态仍对角。 |
| spatially correlated channels；effective noise covariance / 空间相关信道；有效噪声协方差 | [Djelouat 等 2021 v1](https://arxiv.org/pdf/2112.04295v1)，§III–IV式(8)–(13)，PDF p.3 | 信道先验 R 与有效误差 Σ 是不同矩阵；活动 likelihood 同时依赖行列式和加权二次型。Gaussian 活跃先验的公式不能直接当作当前学习分类器的替代。 |
| complex AMP；Wirtinger Jacobian；matrix extension / 复数 AMP；Wirtinger Jacobian；矩阵扩展 | [Kunde 等 2026 v1](https://arxiv.org/pdf/2604.21115v1)，§III-B Assumption 8，§III-C式(18)–(21)、Remark 14，§VI，PDF pp.9、12、17 | 完整联合映射的分块部分迹有出处；原文 iid complex Gaussian 测量前提仍在，结构化算子扩展列为未来工作。 |
| memory AMP；sufficient statistic / 有记忆 AMP；充分统计量 | [Liu 等 MAMP v7](https://arxiv.org/pdf/2012.10861v7)，§III-A式(18)–(24)，PDF pp.6–7；[SS-MAMP v4](https://arxiv.org/pdf/2112.15327v4)，§IV-A Lemma 11式(40)、§V-B Theorem 1式(62)–(65)，PDF pp.8、10–11 | 跨轮正交与协方差融合不能简化成任意阻尼；真值协方差仅作 oracle 诊断，理论不自动覆盖有限 AFDM/CNN。 |
| long-memory OAMP；damping / 长记忆 OAMP；阻尼 | [Takeuchi v2](https://arxiv.org/pdf/2111.05522v2)，§III-C/D式(27)–(28)、(44)–(45)，§IV-B Example 2式(63)–(78)，§I-B与§VI | 重申历史 temporal 方向；原文同时报告有限维负结果。消息参数的线性阻尼不是一般的真实误差协方差递推，但不能因此直接称作代码错误或漏检的唯一原因。 |
| VDAMP；colored state evolution / VDAMP；有色状态演化 | [Millard 等 2020 v3](https://arxiv.org/pdf/2003.02701v3)，§I-C式(9)–(10)、Algorithm 2，PDF p.3；[D-VDAMP 2020 v1](https://arxiv.org/html/2010.13211v1)，§2.2 Finding 1、§2.3 | 分子带误差模型及有色噪声条件训练；不是全局白噪声，也不是任意结构矩阵的严格 SE。 |
| denoising GEC；corr+corr / 基于去噪的广义期望一致近似；corr+corr | [Shastri 等 2022 v2](https://arxiv.org/pdf/2206.05049v2)，§III-A/B式(28)、(36)、(38)–(41)，PDF pp.11–16 | 原坐标有色观测与独立同协方差噪声样本共同输入新训练网络。式(36)后承认严格分析待研究；本文的 AFDM/JADCE 适配只是建议。 |
| fast iterative renoising (FIRE)；colored renoising / 快速迭代加噪；有色加噪 | [Bendel 等，TMLR 2025 v4](https://arxiv.org/html/2501.17468v4)，§3.1式(14)–(21)、Theorem 1、Algorithm 1 line 7 | 保留预训练网络，通过新增噪声补齐工作协方差。定理假设去噪输出误差已白 Gaussian、方差已知且独立于测量噪声；补噪有 SNR 代价，不修复条件均值偏差。 |
| denoiser-by-denoiser training；layer-by-layer training / 逐去噪器独立训练；逐层训练 | [Metzler 等，NeurIPS 2017](https://papers.neurips.cc/paper/6774-learned-d-amp-principled-neural-network-based-compressive-image-recovery.pdf)，§3、§4.1/4.2、Footnote 5、Corollaries 1–2，PDF pp.5–7 | 原文最优性讨论依赖其 SE 与单调条件；当年的 LDAMP SE 属经验依据，不改写为固定 AFDM 上的严格结果。 |

“同协方差 Gaussian 对照”“物理天线分组”“独立训练协方差条件模块”是对拟议操作的直接描述，不另设具名算法。逐用户实投影系数不能视作已识别的条件增益；矩阵误差形状、偏差和信号依赖应分别检验。2021 年 Cheng 等相关 massive-access OAMP 论文本轮只核验作者机构摘要，未补造正文公式定位。

### 2026年10月24日 下载后重点阅读与接口推导

来源版本与完整获取状态以 [论文索引](../../reference/reviews/stmp_message_awgn_review_20261024/README.md) 为准；下表补充操作定位，不覆盖旧试验。下载后的 [阅读报告](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/STMP_PAPER_READING_NOTES_20261024.md) 已纠正此前未充分列出完整矩阵 Onsager、完整 FIRE/DD-VAMP、三轮残差融合的历史范围。

| 原词或操作 | 本地原文与定位 | 本项目使用边界 |
|---|---|---|
| gdiag operator；diagonalization subsets；subband error precisions / gdiag 算子；对角化分组；子带误差精度 | D-GEC（仅本地历史资料：`reference/literature/shastri2022_dgec.pdf`），p.13 式(31)后、p.14 式(35)后及 Algorithm 2；pp.15–16 corr+corr 式(38)–(41) | 同组平均 Jacobian 迹、对应精度和线性估计应配套；一般“分组精度”是本项目对操作的改写，MRI 小波分组不是任意 AFDM 分组的依据。将 corr+corr 用于活动分类器是项目建议，非论文已有结果。 |
| Gram–Schmidt model / Gram–Schmidt 模型；matrix gain / 矩阵增益 | OAMP-MMV（仅本地历史资料：`reference/literature/cheng2023_oamp_mmv.pdf`），p.5 式(15)–(18)、p.6 式(31)–(34)；On OAMP（仅本地历史资料：`reference/literature/liu2023_orthogonal_principle.pdf`），pp.7–8 式(27)–(34) | \(\widehat X=X\Theta+Z\) 的增益与误差协方差分开记录；矩阵修正后单位增益归一化与噪声代价是项目代数推导。不能仅将标量导数换矩阵便称完整 OAMP-MMV。 |
| sufficient statistic / 充分统计量及协方差加权 | SS-MAMP（仅本地历史资料：`reference/literature/liu2023_ssmamp.pdf`），p.8 Lemma 11式(40)，pp.10–11 Theorem 1 | Hermitian 约定的 \(w=V^{-1}\mathbf1/(\mathbf1^HV^{-1}\mathbf1)\) 需共同单位增益和可信联合误差模型；不能以当前公开残差 Gram 自动替代 \(V\)。 |
| FIRE posterior estimate；renoising / FIRE 后验估计与再加噪 | FIRE v4（仅本地历史资料：`reference/literature/bendel2025_fire.pdf`），pp.4–6 式(10)–(21)、Theorem 1；PDF Algorithm 1 line 6 | PDF 的半正定保障行号为 6，HTML 显示行号可能不同。原 posterior 的 \(C\) 不等于 STMP trace 归一化 extrinsic 的误差协方差。复数公式是项目转写，不称原文已证明当前复杂信道场景。 |
| density compensation / 密度补偿及低 SNR 实验 | D-VDAMP（仅本地历史资料：`reference/literature/metzler2020_dvdamp.pdf`），p.4 Table 2 及其后实验讨论 | 1/8 采样、5 dB 测量 SNR 时作者方法 PSNR 25.0 dB、PnP-ADMM(BM3D) 27.8 dB，说明其噪声放大代价；这是 MRI 的反例，非 AFDM 检测预测。 |
| learned score-based turbo message passing / 学习式 score turbo 消息传递 | Wei–Yuan v1（仅本地历史资料：`reference/literature/wei_yuan_2026_lstmp_v1.pdf`），pp.2–3 §III-B–D，式(6)、(8)、(11)–(13) | 式(6)要求行正交；式(13)为最终输出，训练损失位于 §III-D 未编号正文。单用户信道 NMSE 训练不等同于 JADCE 活动损失；随机 DFT 行选择不据此认定为 Haar 右酉不变。 |
| universality / 普适性 | Lovig–Wang–Fan v2（仅本地历史资料：`reference/literature/lovig2026_universality.pdf`），pp.1–3 Example 1.1、§1.1 | 已取得全文；本次只读主要问题、反例和条件概要，没有复核全部证明。非可分 Lipschitz 本身不足以保证跨矩阵分布普适，更不覆盖固定 AFDM。 |

“每用户方形满秩块的全块无偏估计退化为块逆”直接来自 \(L_kA_k=I\) 的线性代数，不另命名为一种已有接收机。分组/矩阵的维度含义、条件风险与后验中心协方差的区别、复数实坐标方差因子均应在具体实现前列清。关键 PDF 页面已渲染核对；D-Turbo-CS、DD-VAMP 及 EP 预印本存在需对照推导的公式显示不一致，详见对应阅读笔记，未据此断言作者代码或当前项目出错。

### 2026年10月24日 C 的具体表示与公开输入列基

对应 [C 表示分析](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/STMP_COVARIANCE_REPRESENTATION_20261024.md)。本轮的张量坐标、Gaussian 工作模型、二阶矩、原文算法和项目候选分开表述。

| 原词或操作 | 原文定位 | 使用边界 |
|---|---|---|
| gdiag；diagonalization subsets；block uniform diagonalization / gdiag、对角化分组、块内统一对角化 | [D-GEC v2](https://arxiv.org/html/2206.05049v2#S3.SS1)，§III-A 式(31)、(33)–(36)、Algorithm 3；[GEC v2](https://arxiv.org/pdf/1602.07795v2)，§II-A 式(6)–(12)、Algorithm 1，PDF pp.2–3 | 固定基、固定组的精度族及组迹有出处；本项目用公开每用户输入基代替 MRI 小波子带，是新适配。一般完整线性后验仍非对角，投影后才返回消息族。 |
| mode；k-mode matricization；separable covariance；Kronecker product / 轴、按第k轴矩阵化、可分协方差、Kronecker积 | [Hoff，arXiv:1008.2169v1](https://arxiv.org/pdf/1008.2169v1)，§2.1–2.2、式(1)、Proposition 2.1，PDF pp.3–5 | 仅引用数学表示；当前复数共轭与C-order由代码确定。三个轴的未中心化Gram不证明协方差可分。固定酉基任意二维谱与单一可分乘积是不同约束。 |
| correlated noise；corr+corr / 相关噪声、corr+corr | [D-GEC v2](https://arxiv.org/html/2206.05049v2#S3.SS2)，§III-B 式(38)–(41)，PDF pp.15–16 | 给定C的独立辅助噪声可作为条件；C在每任务依公开A改变是本项目候选。有限个辅助样本不保证精确识别C，也不证明实际query符合该条件模型。 |
| proper complex random vector；pseudo-covariance / proper复随机向量、伪协方差 | [Neeser–Massey，IEEE TIT 1993，作者机构原文](https://www.isiweb.ee.ethz.ch/papers/arch/fneese-mass-inspec-1993-1.pdf)，§II-A式(3)–(5)、§III-A Definition 1及式(7)–(8)，印刷pp.1294–1295，PDF pp.2–3 | proper指中心化伪协方差为零；协方差C单独不足以描述一般复Gaussian分布。本项目以proper条件噪声训练是工作假设，不是对实际query的已验证结论。 |

\(A_k^HA_k\) 的特征基、每用户输入模式的方差、按天线/输出行重复、以及精度相减后的闭合性，均用公式直接说明，不另起算法名称。小尺寸Gaussian求解、投影后quotient和式(5)的协方差恒等式只证明代数；输入列公开基的效果来自旧测试查询的探索性二阶矩分析，不作为新算法性能或Gaussian性证明。

### 2026年10月24日 C 候选的首轮验证与分组代价

对应 [C 验证报告](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/STMP_COVARIANCE_VALIDATION_20261024.md)。再次核对 [GEC v2](https://arxiv.org/pdf/1602.07795v2) §II-A/B，式(6)–(12)、Algorithm 1，PDF pp.2–3，以及 [D-GEC v2](https://arxiv.org/html/2206.05049v2#S3.SS1) §III-A Algorithm 2、式(31)、(34)。block uniform diagonalization / 块内统一对角化、diagonalization subsets / 对角化分组、precision / 精度均沿用原义。每用户16模式的选择是项目适配，不是论文已验证的AFDM设计；较粗分组只是下一步建议。

GEC §II-B式(10)的 scaled form 写作 \(\beta=\gamma r\)，依据其精度与自然参数操作解释精确零观测模式的 \(\gamma_{\rm out}=0,\beta_{\rm out}=0\) 极限；不把零精度写成有限方差Gaussian，也不称论文已经讨论当前近奇异样本。首轮 \(r_i=f_i/h_i\)、方差放大不等式、完整用户响应与单模式自身响应的区别均由本项目直接列式推导，不另命名算法。当前SVD判秩全部满秩，近奇异与精确零空间明确区分。

oracle逐模式功率白化、同流程Gaussian参考、实信号方向投影及按场景重抽样均为具体评价操作。拟合误差功率不是中心条件协方差；原始互补二阶矩不是已识别的中心化pseudo-covariance。16份模拟参考的分位范围不是置信区间，探索性场景配对区间不当作完整分布检验或因果证明。正式结果只使用修正到冻结观测噪声估计入口后的首轮数据；首版不匹配记录保留并标记拒绝。

### 2026年10月24日 固定分组、模式响应与可逆缩放

继续使用 [GEC v2](https://arxiv.org/pdf/1602.07795v2) §II-A式(6)–(9)、§II-B Algorithm 1及式(10)–(12)，PDF pp.2–3，和 [D-GEC v2](https://arxiv.org/html/2206.05049v2#S3.SS1) §III-A Algorithm 2、式(31)、(34) 的 block uniform diagonalization / 块内统一对角化与 gdiag。每用户1/2/4/8/16个连续等长组、按公开模式编号对折成4组，都是项目直接描述的分区规则，不另设已有算法名称；等编号平均不等于等实际灵敏度。

首轮 \(r_i=f_i/h_g\) 的自身响应 \(h_i/h_g\)、工作误差方差 \(\nu(1-2h_i/h_g+h_i/h_g^2)\)、组平均等于 \(\tau_g\)，以及逐模式校正后恢复 \(f_i/h_i\)，均是固定系数Gaussian工作模型的直接推导。嵌套分组细化使按维数加权的平均方差不降，需保持同一初始方差、算子及噪声参数；不能对不同闭环或非嵌套分区直接套用。可逆公开缩放在保留其元数据时不改变消息所含信息，不能将query原始MSE比改称信息量或检测性能比。增益与协方差分开记录的文献背景仍为前述OAMP-MMV的Gram–Schmidt模型，其MMV维度和随机矩阵条件不自动等于当前AFDM输入模式分组。详见[独立代数核查](../../reference/reviews/stmp_message_awgn_review_20261024/notes/covariance_grouping_algebra.md)。

### 2026年10月24日 有色噪声的一阶 score 训练

对应 [训练候选与验证记录](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/COLORED_SCORE_TRAINING_20261024.md)。denoising score matching / 去噪 score matching 沿用 [Cai 等 v2](https://arxiv.org/html/2506.00581v2#S4.SS2) §IV-B式(48)–(49)的原义；Tweedie's formula / Tweedie公式的一般正定协方差形式见 [Dytso–Poor–Shamai v1](https://arxiv.org/pdf/2104.01883v1)，PDF p.1式(1)假设、p.2式(3)。矩阵加权损失、复数实打包的1/2系数、C-order轴乘法是项目的显式展开，见[独立数学核查](../../reference/reviews/stmp_message_awgn_review_20261024/notes/colored_score_training_algebra.md)。

correlated noise / 相关噪声及 corr+corr 仍依据 [D-GEC v2](https://arxiv.org/html/2206.05049v2#S3.SS2) §III-B式(38)–(41)。原文用独立同协方差辅助噪声训练直接去噪映射；当前候选改为精确协方差因子条件的一阶 score，不宣称逐字复现 corr+corr。给定有限辅助样本时的加权 DSM 条件最优解另行推导，不能称其为原文已证明的结论。

separable covariance / 可分协方差、proper complex / proper复数噪声继续沿用上文 Hoff 与 Neeser–Massey 的原义。这里只令两个因子的 trace/dim=1，称为归一化协方差因子；不把非单位对角的矩阵称为 correlation matrix。低秩正半定矩阵与单位矩阵的凸组合、精确矩阵条件输入都是项目设计选择，不另造算法名，也不称为已识别的实际消息噪声分布。按用户后续要求，四类等比例采样已取消，当前两个因子独立连续抽取；同一条件Gaussian族不意味着边缘上是单个固定协方差Gaussian。

后续[相对近似检查](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/COLORED_COVARIANCE_RELATIVE_CHECK_20261024.md)中的Gaussian负对数密度，直接由proper复Gaussian密度的logdet和二次型展开，每复坐标归一且略去共同常数logπ；不引入实Gaussian的1/2。偶奇输出行拟合与评分、谱尾均值替换和向单位阵收缩均按操作描述，不另命名算法；它们不是独立场景交叉验证、最优联合协方差估计或真实Gaussian性的证明。

### 2026年10月24日 baseline 预算、重构和活动判据复核

对应[预算与判据报告](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/BASELINE_BUDGET_REVIEW_20261024.md)。`orthogonal projector` / 正交投影算子的原词依据 [Tropp–Gilbert–Strauss，Algorithm 3.1步骤4–5，PDF p.7](https://tropp.caltech.edu/papers/TGS05-Algorithms-Simultaneous-I-preprint.pdf)。对完整80原子物理信道空间计算真值投影及最小平方表示误差，是本项目直接应用该线性代数操作；使用真值，不能当作可实现接收机结果或AER下界。

`V-fold CV` / V折交叉验证依据 [Arlot–Celisse，arXiv:0907.4728v1，§4.3.2](https://arxiv.org/html/0907.4728v1)，数据分成近等大的V份，轮流留出。按物理场景ID对5取模、同一场景全部SNR留在同一折，是本项目分组规则，不声称论文已证明此AFDM实验的独立性或方差估计。校准集内比较不等于独立测试确认；32万用户判断不是32万个独立重复。

`first-order Taylor expansion` / 一阶Taylor展开沿用 [Wei 等，arXiv:2101.05629v1，§III-B式(17)–(24)](https://arxiv.org/html/2101.05629v1)。同文§II式(3)后及§VI-A式(76)将估计参数用于有效信道重构，因此不能把本项目一阶拟合后使用精确路径算子直接定性为原论文公式错误。固定参数改用一阶信道输出，是本项目的诊断候选；16场景NMSE改善不证明AER改善或原论文严格复现。

相对能量门限继续沿用 [Zhou 等，§IV-C式(27)](https://arxiv.org/html/2201.02084v2#S4.SS3)。绝对能量、除以估计物理噪声方差的能量均按操作描述，不自动称为活动后验或恒虚警率检测。GAMP绝对能量的小幅改善与Off-grid噪声归一化的高SNR回升，均仅按本轮校准集内五折计数报告。


### 2026年10月24日 有色噪声网络结构与参数化核查

对应[结构调研与权重诊断](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/COLORED_SCORE_ARCHITECTURE_REVIEW_20261024.md)。以下原词按所列论文原义使用；不将本项目适配包装为已有方法。

| 原文术语 / 中文表述 | 核对位置 | 本项目使用边界 |
|---|---|---|
| preconditioning / 预条件处理；skip connection / 跳连 | [Karras等EDM v2](https://arxiv.org/pdf/2206.00364v2)，PDF p.8 §5式(7)–(8)，p.3 Table 1，pp.28–29 Appendix B.6式(114)–(144) | 原文为标量各向同性噪声的输入、跳连和输出系数。一般SPD矩阵函数用于本项目是显式推广，不称为EDM已经验证的AFDM实现。 |
| matrix-form EDM / 矩阵形式EDM | [Ding等iCCDM v1](https://arxiv.org/pdf/2602.02114v1)，PDF p.5 §III-D2式(19)–(20)、§III-D3式(22)后 | 2026预印本；作者代码与实验采用对角噪声协方差。本项目使用任意旋转的Ra/Rc需另行验证；条件编码及损失权重不能机械照搬。 |
| noise level map / 噪声强度图 | [FFDNet v2](https://arxiv.org/html/1710.04026v2#S3.SS2)，§III-B，PDF p.4 | 原文允许多通道退化图，官方另有6参数RGB协方差版本；不等于任意高维复协方差已有现成实现。 |
| DRUNet；residual block / DRUNet、残差块 | [DPIR v2](https://arxiv.org/pdf/2008.13751v2)，Fig.1、§3.1–3.2，PDF pp.3–4 | 残差U-Net加标量噪声图，论文使用L1；作为条件均值/score候选需明确改用匹配的平方目标。 |
| Multi-Dconv Head Transposed Attention (MDTA) / 多头深度卷积转置注意力 | [Restormer](https://openaccess.thecvf.com/content/CVPR2022/papers/Zamir_Restormer_Efficient_Transformer_for_High-Resolution_Image_Restoration_CVPR_2022_paper.pdf)，§3.1，PDF pp.3–4 | 原词照录；其注意力在通道维计算。只用于说明候选主干，未将图像结果外推为AFDM收益。 |
| SimpleGate；Simplified Channel Attention (SCA) / SimpleGate、简化通道注意力 | [NAFNet](https://www.ecva.net/papers/eccv_2022/papers_ECCV/papers/136670017.pdf)，§4，PDF pp.7–9，式(4)、(6) | 原文模块名称；本次仅比较架构设计，未移植到项目。 |

corr+corr及子带标准差接口沿用上文D-GEC §III-B式(38)–(41)与D-VDAMP §2.3 PDF p.3的记录。条件均值、score转换和矩阵加权DSM继续沿用Tweedie公式与已有核查，不新造缩写。另核对[Zilberstein等v1](https://arxiv.org/pdf/2605.15487v1)，PDF p.3 §3.1式(7)–(8)、p.4 §3.2式(9)，但未采用其能量网络或协方差导数目标。

“224维协方差族经过64维条件压缩”、同输入条件置换、单位代理先验的线性估计、K/B/O矩阵函数及其损失恒等式，都是本项目直接描述和推导；不称为文献已经验证的性能结论。64场景CPU诊断为已有开发集上的机制检查，非1000场景正式比较。阅读范围、作者代码commit、原文与实现差异均记录于[调研资料目录](../../reference/reviews/colored_architecture_review_20261024/README.md)。

### 2026年10月25日 冻结一阶网络后学习二阶统计量的文献核对

本次为针对具体主张的原文核验，阅读范围为下表所列章节，不代表系统综述。Semantic Scholar 元数据查询返回 HTTP 429；作者、题名、年份与论证位置改由 arXiv 原文及会议官方论文集核对。

| 原文术语 / 中文表述 | 核对位置 | 本项目使用边界 |
|---|---|---|
| second-order score matching / 二阶得分匹配；trace / 迹 | [Cai 等，STMP-JADCE，arXiv:2506.00581v2，2026](https://arxiv.org/html/2506.00581v2#S4.SS3)，§IV-C式(50)–(54)，特别是式(53)前及式(54)后段落 | 原文明确允许先训练一阶网络，再冻结它训练二阶网络；消息方差只需二阶 score 的迹。支持冻结新一阶后重新学习配套二阶统计量，但不证明共享小型输出分支在本项目已经足够，也不证明有色查询闭环性能。有限一阶误差下的条件风险与精确后验协方差仍按已有记录区分。 |
| second-order score；diagonal；low-rank matrices / 二阶 score、对角、低秩矩阵 | [Meng–Song–Li–Ermon，Estimating High Order Gradients of the Data Distribution by Denoising，NeurIPS 2021](https://proceedings.neurips.cc/paper/2021/file/d582ac40970f9885836a61d7b2c662e4-Paper.pdf)，§1，§3.2，§4.1式(13)–(17)，§4.2–4.4，§5式(18) | 给出通过去噪监督学习高阶 score 的方法，比较直接学习与一阶网络自动微分，讨论对角与低秩输出。其实验采用一、二阶联合训练，不能写成已验证本项目冻结训练方案。完整二阶矩阵的加速结果不能直接外推给当前单探针有限差分迹估计。 |
| heteroscedastic regression；shared representation learner；covariance parameter head；stop gradient / 异方差回归、共享表征网络、协方差输出分支、停止梯度 | [Stirn 等，Faithful Heteroscedastic Regression with Neural Networks，AISTATS 2023](https://proceedings.mlr.press/v206/stirn23a/stirn23a.pdf)，§2，PDF pp.3–4，Figure 1、Proposal 1–2、式(5) | 原文给出共享主干、均值和协方差两个输出分支，并举单层 softplus 对角协方差输出例子；阻止协方差梯度更新共享主干，同时使均值按平方误差目标更新。支持轻量方差分支与保护均值训练的设计依据；并非二阶 score 或 JADCE 研究。冻结已训练主干及均值是本项目候选适配，非原文主要联合训练流程。 |

当前建议仅为：保留已训练一阶去噪器，用新的监督目标学习其配套方差，并比较独立网络和复用一阶特征的小型分支。直接拟合有限去噪器的条件平方误差时，学习对象应称条件误差风险；只有明确 score 定义、Gaussian 观测条件及相应恒等式后，才能解释为二阶 score 的相关读出。上述文献不保证该候选在 C-STMP 中优于现有导数估计，尚需方差校准、运行时间和接收机闭环比较。

2026-10-25 用户选择独立二阶网络并授权开始训练。实现继续沿用 Cai §IV-C式(50)–(54) 的 second-order score matching / 二阶得分匹配；归一化的协方差加权迹 \(u=\operatorname{tr}(\Sigma S_2\Sigma)/\operatorname{tr}\Sigma\) 及其监督目标为本项目明确推广，见 [C-STMP 推导第8节](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/C_STMP_DERIVATION_20261024.md)。只监督该标量迹，不声称输出图的每个像素是已学习的 Hessian 对角元；有限冻结一阶下仍按条件风险解释其方差读出。输入预条件、独立原二阶 RefineNet 初始化及 C 条件均为实现选择，不另造算法名称；当前未采用 Stirn 的共享方差分支。

### 2026年10月25日 负方差与截断的原文/作者实现核对

| 原文术语 / 中文表述 | 核对位置 | 本项目使用边界 |
|---|---|---|
| clipping / 截断 | [Sippel–Fischer，Stabilization Techniques for Iterative Algorithms in Compressed Sensing，arXiv:2109.14917v1，2021](https://arxiv.org/pdf/2109.14917)，§IV-C，PDF p.3；§V-C，PDF p.4 | 原文显式对精度作区间截断：一类精度限制到[10^-8,10^8]，其他精度到[10^-12,10^12]。这是VAMP稳定化先例，不能把其精度边界直接当成本项目后验方差阈值，也不据此声称截断保证收敛或统计校准。 |
| posterior variance / 后验方差；代码中的下界操作 | [Cai等作者固定提交0c75680c966dcb8e46250de146f4c27e9294c283](https://github.com/chang-cai/score-massive-connectivity/blob/0c75680c966dcb8e46250de146f4c27e9294c283/main_stmp_jadce.py)，`module_B` 的二阶score读出及其后的 `v_H_B_post[v_H_B_post < 1e-4] = 1e-4` | 作者先合并实虚方差、跨用户及子载波平均，保留天线维，再设10^-4下界。此证据来自作者代码，不能写成论文正文明确给出的阈值。本项目当前`STMP/denoiser.py`第119–120行先对用户原始标量读出平均，再在checkpoint归一化坐标下设10^-4下界；不是逐用户先截断再平均。 |

后验方差/条件平方误差必须非负，而二阶score本身可以为负；截断应作用于方差读出，不能要求Hessian逐项非负。当前外信息精度`1/tau - 1/v`若不为正，接收机保留旧site，这与负后验方差的下界操作是两个步骤。仅为方差设正下界不保证其小于输入方差，后者也不是一般非Gaussian先验下逐点成立的后验性质。截断避免非法数值，不校正整体低估；验证继续保留原始输出、触发比例和截断后读出。此次仅核查与记录，未修改训练损失、网络权重或接收机。

2026-10-25 高SNR排查沿用 damping / 阻尼及 Gaussian extrinsic information / Gaussian外信息，原文依据仍为上文 Cai v2 §III-A–B、§V-B1式(57)–(58)。代码中的β是新消息权重；β从0.4降为0.2是增加阻尼。固定v、τ对外信息均值求导得到的式(17)为本项目直接代数展开，见[C-STMP推导第10节](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/C_STMP_DERIVATION_20261024.md)，不是新的文献算法或完整稳定性证明。数值导数估计与有限去噪器条件误差风险的区别仍采用Dytso §IV及前述二阶监督的原义。相邻更新余弦、输入误差与报告方差比均按具体计算描述，不另造术语。

### 2026年10月25日 导数方差的完整推导与原文定位

对应 [C-STMP推导第12节](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/C_STMP_DERIVATION_20261024.md)。本次核对的是所列公式及其适用范围，不是新增系统综述。

| 原文术语 / 中文表述 | 核对位置 | 本项目使用边界 |
|---|---|---|
| Jacobian；conditional mean estimator；conditional covariance / Jacobian、条件均值估计器、条件协方差 | [Dytso–Poor–Shamai，arXiv:2104.01883v1](https://arxiv.org/pdf/2104.01883v1)，§II式(9)、PDF p.4；§IV Proposition 1式(22)、PDF p.5；Corollary 1式(23)、PDF p.6 | 原文 Jacobian 用输入坐标为行，本项目用输出坐标为行，因此对应式为 J_m=PΣ^-1、P=J_mΣ。仅在固定协方差的 Gaussian 观测条件下为精确恒等式；有限条件均值网络的导数读出只能作为方差近似。实/复转换和每复元素归一化是项目显式推导。 |
| divergence；Monte Carlo method / 散度、Monte Carlo方法 | [Metzler–Maleki–Baraniuk，From Denoising to Compressed Sensing，arXiv:1406.4175v2](https://arxiv.org/html/1406.4175v2)，§V-B式(21) | 原文用 Gaussian 方向和单侧有限差分估计散度。本项目用独立随机符号、协方差平方根缩放及中央差分，依据 E[zzᵀ]=I 明确推导；一个方向需要额外两次均值前向，与原文单侧差分的额外一次不同。固定方向跨迭代复用，不宣称闭环轨迹无偏。 |
| Tweedie’s formula；posterior mean / covariance；second-order score / Tweedie公式、后验均值/协方差、二阶score | [Cai等，arXiv:2506.00581v2](https://arxiv.org/html/2506.00581v2)，§IV-A式(43)–(45)；§III-B3式(35)–(36) | 精确均值的 Jacobian 读出与二阶score协方差读出等价。有限网络下，导数迹与冻结均值后监督平方误差得到的条件风险不必相同。活动条件方差与 Bernoulli 混合后方差分开书写；分类器仍是本项目学习接口。 |

“协方差缩放的随机符号中央差分”“由条件均值导数得到的方差近似”直接描述计算操作，不另造文献算法名。C-STMP继续作为用户指定的项目候选名称。推导覆盖一般C，但本轮实际接收机接口仍为C=vI；不能据此宣称已经实现完整D-GEC或一般有色矩阵消息传递。

2026-10-25 严谨性比较补充： [Meng等，NeurIPS 2021](https://proceedings.neurips.cc/paper/2021/file/d582ac40970f9885836a61d7b2c662e4-Paper.pdf) §1、PDF pp.1–2的 estimation error / 估计误差讨论明确区分一阶训练损失与高阶导数误差；§4.4、PDF p.6比较直接学习与自动微分。本文据此明确：小的一阶去噪误差不自动保证小的 Jacobian 迹误差。[Cai v2](https://arxiv.org/html/2506.00581v2) §IV-C式(52)后讨论一阶替换误差，式(53)直接监督二阶迹；§V-B1式(57)–(58)前明确大系统与 right-rotationally invariant / 右旋转不变随机矩阵的 AWGN 查询条件及有限维失配。以上均不提供当前有限 AFDM、学习分类器及阻尼接收机的无条件收敛保证。项目的误差分解与数学反例见[C-STMP推导第12.5节](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/C_STMP_DERIVATION_20261024.md)，不把项目代数结论冒充原论文定理。

### 2026年10月25日 预训练一阶网络导数协方差的应用先例

| 原文术语 / 中文表述 | 核对位置 | 本项目使用边界 |
|---|---|---|
| posterior covariance；posterior principal components；Jacobian-vector product / 后验协方差、后验主成分、Jacobian–向量乘积 | [Manor–Michaeli，ICLR 2024，arXiv v2](https://arxiv.org/html/2309.13598v2)，§3.2 Theorem 2式(10)–(11)，§4.1式(15)、Algorithm 1，Appendix H；会议信息见[作者页](https://hilamanor.github.io/GaussianDenoisingPosterior/) | 对预训练去噪器作单侧前向差分计算后验协方差主成分，无需另训二阶网络。支持使用已有均值映射的导数提取二阶信息；本项目随机符号中央差分迹不是其原Algorithm 1。 |
| Tweedie Moment Projected Diffusions (TMPD)；diagonal Tweedie Moment Projection (DTMPD)；vector-Jacobian product / 沿用论文名称及缩写、向量–Jacobian乘积 | [Boys等，TMLR 2024，arXiv v3](https://arxiv.org/html/2310.06721v3)，§3.1 Proposition 1式(5)–(6)，§3.2–3.4，Appendix E.1 | 用预训练一阶score得到均值及导数协方差，进入逆问题条件采样。其图像计算进一步使用Jacobian行和近似对角；该近似与本项目随机迹估计不同，不引入其采样理论作为AFDM闭环保证。 |
| precision；divergence；gdiag / 精度、散度、gdiag算子 | [Shastri等D-GEC，arXiv v2](https://arxiv.org/pdf/2206.05049v2)，Algorithm 1 line 10、PDF p.8；§III-A式(31)、(33)、Algorithms 2–3、PDF pp.13–14 | 标量精度满足η=γN/tr(J_f)，分组扩展采用Monte Carlo差分。作为去噪导数参与消息精度更新的先例，不能把任意DNN读出解释为已证明准确的后验协方差。 |

具体引用分工和与C-STMP的对应见[推导第12.6节](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/C_STMP_DERIVATION_20261024.md)。本次只核查列出的原文章节，未宣称全文阅读或新增接收实验。

### 2026年10月25日 有色噪声条件活动分类器的文献依据与扩展边界

本次按用户问题核对分类器的直接依据，未启动训练或恢复暂停的SNR实验。当前已训练分类器仍为白噪声查询；下述一般C接口属于待实现候选。

| 原文术语 / 中文表述 | 核对位置 | 本项目使用边界 |
|---|---|---|
| density ratio estimation；class-probability estimation；logistic loss / 密度比估计、类别概率估计、logistic损失 | [Menon–Ong，ICML 2016](https://proceedings.mlr.press/v48/menon16.pdf)，§2.2，§3式(6)–(8)，§4.2式(16)–(17)，印刷pp.305–306 | 平衡logistic训练的理想logit是对数密度比；有限网络只是估计，不能把低训练损失当作实际消息校准保证。该结果不要求两个类别的分布都是Gaussian。 |
| parameterized classification；parameterized calibration / 参数化分类、参数化校准 | [Cranmer–Pavez–Louppe，arXiv:1506.02169v2，2016版本](https://arxiv.org/html/1506.02169v2#S3.SS2)，§2.2 Theorem 1和式(2.10)，§2.3，§3.2 Algorithm 1，§3.3 | 原文把生成分布的参数作为分类器输入；以噪声协方差C作为条件是本项目的具体应用，原文没有AFDM活动分类器或当前一阶均值特征。原文§3.2明确提示未见参数组合和有限容量的泛化问题。 |
| likelihood ratio trick；binary cross-entropy / 似然比估计所用的分类转换、二分类交叉熵 | [Rizvi–Pettee–Nachman，arXiv:2305.10500v1，2023](https://arxiv.org/html/2305.10500v1#S1)，§I式(2)–(5)和脚注1，§II | BCE最优概率的odds转换及非平衡训练的先验因子；原文的有限样本实验说明损失与输出参数化会影响实际误差，不构成当前接收机性能保证。 |
| corr+corr；colored Gaussian noise / 沿用D-GEC的原名称、有色Gaussian噪声 | [Shastri等，D-GEC v2](https://arxiv.org/html/2206.05049v2#S3.SS2)，§III-B式(38)–(41) | 原文训练MSE去噪器，并用独立同协方差噪声样本携带统计信息；没有BCE活动分类器。我们直接输入协方差因子的接口不是原文corr+corr。 |

对项目工作模型r=a h+n、n给定C服从CN(0,C)，两类共用C采样律g(C)，将Menon–Ong式(6)逐条件应用即可得到：z*(r,C)=logit(pi_train)+log[q1(r|C)/q0(r|C)]。部署时估计活动概率为sigmoid(logit(rho)+z_phi-logit(pi_train))，前提是目标类别条件查询分布与训练模型一致。这是一般分类–密度比恒等式的条件化应用，不是上述论文已有的AFDM定理。保留完整r和C时，附加固定的一阶均值D_theta(r,C)是确定性特征，不增加条件信息；是否有助于有限网络训练需消融验证。卷积结构、协方差因子编码、复数打包和与STMP迭代的组合均属项目设计。

与Cai原文区分：[Cai等v2](https://arxiv.org/html/2506.00581v2#S3.SS2.SSS2) §III-B2式(28)–(30)使用Gaussian消息积分给出活动概率；§IV训练一、二阶score网络。原文没有本项目独立训练的第三个BCE分类器，不应把该分类器表述为Cai或D-GEC的原始网络。一般密度比理论不推出分类器必须依赖一阶网络；使用一阶均值是本项目的特征选择。

### 2026年10月25日 解析活动概率诊断候选

沿用 Cai v2 §III-B2 的 **Denoiser of α_k / 活动变量去噪器**、式(28)–(30)的 Gaussian 消息积分，以及 §III-B3 式(35)–(36)的活动加权均值和方差。`C-STMP (analytic activity)` 只是项目候选的描述性标签，不是论文既有算法名称。本候选将当前标量方差消息代入原积分，N=4096 是复坐标数，保留 Gaussian 归一化项。与论文逐天线方差和学习二阶网络不同，当前沿用共享标量导数方差；不表述为 Cai 算法的完整复现。详细公式、数值核对和诊断范围见 [解析活动概率说明](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/C_STMP_ANALYTIC_ACTIVITY_20261025.md)。

### 2026年10月25日 查询统计逐模块诊断

沿用 [Cai v2](https://arxiv.org/html/2506.00581v2#S3.SS2.SSS1) §III-B1 式(20)–(23)的 AWGN observation / AWGN 观测、posterior mean / 后验均值、posterior variance / 后验方差；式(20)前文字说明其 Gaussian 解释依赖大系统状态演化，不能改写为任意有限算子的保证。数值 Jacobian 核对沿用此前 Dytso、Meng 的已记录原义。本项目的 `R−H=(WA−I)(H−P)+Wn` 为对实际线性更新的直接代数展开，不新造方法名。实测协方差特征值比与矩阵归一化内积按公式描述；代码字段 `(tr C)^2/tr(C²)` 不直接命名为文献中的 effective rank。见[推导与适用边界](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/C_STMP_COMPONENT_DIAGNOSTIC_20261025.md)。


### 2026年10月25日 查询噪声功率修正候选

继续使用上述 Cai v2 §III-B1 式(20)–(23)的 AWGN observation，以及 §III-B3 式(35)–(36)的活动混合均值和方差。对当前查询各用户平均能量取中位数，以及在原迭代结束后重新计算一次共同条件下的输出，是本项目明确提出的近似操作，不对应上述论文已有算法名称，也不将其称为完整 D-GEC。中位数估计不声明无偏；最终重算不声明在新条件下达到消息固定点。严格逐用户线性关系及推导见 [修正说明](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/C_STMP_QUERY_POWER_REPAIR_20261025.md)。

### 2026年10月25日 每用户输入列协方差消息

| 使用的术语或表述 | 原文依据及位置 | 本项目边界 |
|---|---|---|
| MMSE estimation / MMSE估计；covariance / 协方差；precision / 精度 | Fletcher等，*Expectation Consistent Approximate Inference: Generalizations and Convergence*, [arXiv:1602.07795v2](https://arxiv.org/html/1602.07795v2)，§II-A式(4)–(5)，§II-B式(10)–(12) | 沿用后验均值、精度及缩放均值消息、Jacobian与后验协方差的关系；复数自然参数的2倍因子另由本项目推导和数值核对。 |
| vector-valued diagonalization / 向量对角化；block uniform diagonalization / 分块均匀对角化 | 同文§II-A式(6)–(9) | 原文返回对角或分块平均量，不是本项目保留每用户完整16×16列协方差的直接实现；不借用其收敛结论。 |
| correlated noise / 相关噪声；D-GEC | Shastri等，[arXiv:2206.05049v2](https://arxiv.org/html/2206.05049v2)，§III-A式(31)、Algorithm 3、式(36)后文字；§III-B式(38)–(41) | 只用来支持统计条件与去噪训练相匹配的思路；其误差Gaussian性仍有研究边界。当前精度参数及(z,J)输入不是原文corr+corr。 |

`ColumnLinear`、`C_STMP_column_messages`仅为本项目代码路径，不宣称新的既有算法名称。Λ=A_k^H S_{-k}^{-1}A_k、η=A_k^H S_{-k}^{-1}y_{-k}及J=(I+Λ)^{-1}Λ、z=(I+Λ)^{-1}η是明确给定独立Gaussian输入消息后的直接代数操作。详见[推导及数值验证](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/C_STMP_COLUMN_MESSAGES_20261025.md)。

2026年10月25日复用旧权重补充：`C_STMP_reuse_20261025`仍为项目代码路径。对旧一阶使用v=tr(C)/16、Ra=I、Rc=C/v只是原协方差表示的特例；输入/输出预条件继续沿用上述EDM来源与本项目明确的矩阵推广。对旧分类器，把标量归一化和能量改为同一C下的矩阵函数及二次型，是本项目未经重训的特征推广，不称为D-GEC、Cai或其他论文已经提出的活动检测器，也不由白噪声退化一致性推出一般C下的密度比校准。见[实现与边界，第9节](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/C_STMP_COLUMN_MESSAGES_20261025.md#9-复用已训练权重的接口评估不重训)。

### 2026年10月25日 当前标量 C-STMP 的查询方差更新候选

- **EM Update of the Gaussian Noise Variance / Gaussian 噪声方差的 EM 更新**：Vila–Schniter, *Expectation-Maximization Gaussian-Mixture Approximate Message Passing*, IEEE TSP 2013，[作者公开原文](https://phil-schniter.web.app/pdf/tsp13_emgm.pdf)，§III-A 式(22)–(27)，印刷 p.4661。原文使用后验残差平方加后验方差更新物理噪声；本项目将相同的条件期望恒等式用于近似查询模型 r=H+e，复坐标下 v_target=mean(|r−E[H]|²)+mean(tr Cov[H])/M。活动混合项 p(1−p)μμᴴ 必须保留。查询方差不是物理观测噪声方差。
- **variance auto-tuning / 方差自动调整**：Fletcher等，*Rigorous Dynamics and Consistent Estimation in Arbitrarily Conditioned Linear Systems*, NIPS 2017，[会议原文](https://proceedings.neurips.cc/paper_files/paper/2017/file/4e8412ad48562e3c9934f45c3e144d48-Paper.pdf)，§4（PDF p.7），Definition 1、Theorem 2。这里只支持对消息噪声参数进行估计的思路；论文的右旋转不变、大系统及可辨识性假设不直接适用于本项目有限维网络接收机。

`C_STMP_variance_em_20261025`是独立候选代码路径，不另立算法名称。每轮使用 v_t=a_t v_linear,t；所有一阶均值、固定条件下导数、活动概率及外信息减法共享 v_t。随后 a_{t+1}=(1−β)a_t+β v_target,t/v_linear,t，β沿用0.4；原始线性方差与调整后方差分别保存，避免将已调整的方差再次混入原始线性阻尼历史。停止时还检查 |v_target−v_t|/max(v_target,v_t) 小于原0.0005容差。此为本项目在近似后验下的一步交替更新，不声称精确EM似然单调性或论文的状态演化保证；没有增加网络前向、训练或使用真值。

同日数学核查补充：上述Vila–Schniter §III-A式(22)–(27)的期望对数似然更新，在本项目固定查询r与近似分布q后给出 Q(v)=const−D log(v)−D S/v，S=(||r−E_q g||²+tr Cov_q(g))/D；S>0时唯一最优方差为S。这是对所采用矩的精确代数关系，不把近似q命名为真实后验。比例阻尼只对本轮线性参考方差b_t下的虚拟值 b_t a_{t+1} 保证Q不下降；实际下一轮使用 b_{t+1}a_{t+1}，故不宣称全程EM单调性。

Gaussian外信息自然参数相除对应实现中投影、裁剪后的P_used；不将其等同于未投影真实后验的精确相除，也不据此称为完整EC固定点。[Fletcher–Schniter，Learning and Free Energies for Vector Approximate Message Passing，v4](https://arxiv.org/html/1602.08207v4) §III的固定点刻画与§IV开头的不保证收敛须同时保留，不能移用到当前神经接收机。逐步证明、400份保存结果的数值核查及近似边界见[C-STMP推导第13节](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/C_STMP_DERIVATION_20261024.md#13-当前标量查询方差修正的数学核查2026-10-25)。本补充没有为项目操作另造术语。


### 2026年10月26日 C-STMP 复制组装稿的有色噪声表述

- 稿件目录 `STMP`、`DU`、`C-STMP` 是作者指定的项目标签；旧 `TWC-1` 和 `TWC-2` 分别对应当前 `STMP` 和 `DU`。
- **colored Gaussian noise / 有色高斯噪声；denoising with correlated noise / 相关噪声去噪**：Shastri, Ahmad, Metzler, Schniter, *Denoising Generalized Expectation-Consistent Approximation for MR Image Recovery*, arXiv:2206.05049v2，§III-B “A DNN denoiser for correlated noise”，式(38)–(41)，[作者公开原文](https://arxiv.org/html/2206.05049v2#S3.SS2)，DOI 10.48550/arXiv.2206.05049。原文通过同协方差的独立噪声样本携带统计条件；本项目显式协方差条件输入不是其原 corr+corr 实现。该引用仅支持噪声统计条件下的有色训练动机，不提供当前 AFDM 接收机的收敛保证。
- `C-STMP/references.bib` 的 `shastri2022` 由上述原文核对。摘要与引言的训练描述对应当前有色预训练记录；该组装稿 III–V 章按作者要求保留 STMP 文字和公式，仅调整双栏断行，逐字节原件另存；后续理论改写范围尚未执行。


### 2026年10月26日 C-STMP 实验章补全与精简

- 组织与分析依据：Cai 等 [arXiv:2506.00581v2](https://arxiv.org/html/2506.00581v2)，§VI-A–C；正式版 pp.3585–3588。直接核对图4去噪、图5收敛、图6–7 SNR、图10导频分析，采用「主要趋势—关键比较—解释」的简短段落。未移用 Cai 的数值或结论。NMSE、检测错误及稀疏字典术语沿用原义；本文 AER 的计数归一化公式已明确给出。
- 补齐原实验章缺失的三个参考文献条目：Tropp–Gilbert–Strauss, Signal Processing 86(3):572–588, 2006（[作者原文](https://tropp.caltech.edu/papers/TGS05-Algorithms-Simultaneous-I-preprint.pdf)，Algorithm 3.1，PDF pp.6–7）；Zhang 等, TVT 72(11):15057–15061, 2023（元数据核对本地 Ding 原文参考文献[8]，方法位置沿用此前 pp.15058–15059、Algorithm 1 核验记录）；Wei 等, TWC 21(9):7407–7426, 2022（[原文](https://arxiv.org/abs/2101.05629)，§III–IV、Algorithm 1；DOI 10.1109/TWC.2022.3158616）。AFDM、多天线及活动读出仍声明为项目适配。
- 四图数值逐项对照保存结果；详细计数及完整长版分析保存在 [paper/checks/experiment_revision_20261026/](https://github.com/RESET-cpu/afdm-gfra/tree/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/experiment_revision_20261026)。正文保留有色训练高 SNR 略逊、−4 dB 检测排序例外、Q=8 原 STMP 收敛困难等影响结论的事实；未将整体接收机收益单独归因于有色训练。


### 2026年10月26日 C-STMP 当前算法稿与用户数实验

本次根据作者要求，以已复制的 STMP 第 III–V 章为基础改为当前 `C_STMP_variance_em_20261025` 实现；系统模型逐字节不变。沿用 Cai §III–V 的“推断框架—所需统计量的学习—完整算法”顺序，具体变化如下。

| 术语与公式 | 原文位置 | 当前稿件中的对应 |
|---|---|---|
| conditional mean / 条件均值；conditional covariance / 条件协方差 | [Dytso–Poor–Shamai，arXiv:2104.01883](https://arxiv.org/abs/2104.01883)，§IV Proposition 1 式(22)，PDF p.5；一般 Tweedie 关系见式(3) | 第 IV-A/B 章：实坐标协方差 Σ=1/2[Re C,−Im C;Im C,Re C]；采用输出为行的 Jacobian，P=JΣ，复坐标方差为 tr(P)/D。网络导数是该恒等式的近似应用，不再沿用独立二阶网络或条件 MSE 回归的解释。 |
| network preconditioning / 网络预条件 | [Karras 等，NeurIPS 2022 原文](https://proceedings.neurips.cc/paper_files/paper/2022/file/a98846e9d9cc01cfb87eb694d946ce6b-Paper-Conference.pdf)，§5 式(7)–(8)、Table 1 | 第 IV-A 章明确将其标量输入、跳连和输出系数推广至矩阵 Σ；实坐标名义方差 σ_d²=1/2。协方差加权损失是当前实现的损失，不冒称与 EDM 的全部训练设计相同。 |
| Monte Carlo divergence / Monte Carlo 散度估计 | [Metzler–Maleki–Baraniuk，arXiv:1406.4175](https://arxiv.org/abs/1406.4175)，§V-B 式(21) | 第 IV-B 章采用固定协方差下的随机符号中央差分迹，每用户一条固定方向、δ=0.01；这是该估计思路的具体变式，原文使用 Gaussian 方向和单侧差分。包括中心点共三次均值网络前向。 |
| Gaussian noise variance update / Gaussian 噪声方差更新 | [Vila–Schniter，IEEE TSP 2013 原文](https://phil-schniter.web.app/pdf/tsp13_emgm.pdf)，§III-A 式(22)–(27)，p.4661 | 第 III-D 章将后验期望残差更新用于近似查询模型，保留活动混合方差；物理噪声估计固定。原始线性方差历史与调整后方差分开保存。 |
| density ratio estimation / 密度比估计 | Menon–Ong，ICML 2016，§2.2、§3 式(6)–(8)；前文已核对 | 第 IV-C 章保留原 STMP 稿的 BCE 分类器及先验校正，当前分类器使用冻结有色训练均值的白噪声查询特征重新训练。 |

`C-STMP` 仍是作者指定的本项目名称。当前训练使用有色协方差，在线查询使用 C=vI；未引入完整有色反馈接口。旧二阶训练附录保留作历史源文件，已退出本稿编译。具体代码、权重绑定及恒等式核查见 [C-STMP/checks/cstmp_algorithm_revision_20261026/](https://github.com/RESET-cpu/afdm-gfra/tree/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/cstmp_algorithm_revision_20261026)。

用户数图直接复制已确认的 `result/user_count/figures/paper_interim100_20261026/user_count.pdf`，每个 K 为 100 场景，作为待替换的阶段结果。正文只比较总体趋势及 K=100 时的 NMSE/AER，不声称完整 500 场景结果或所有 K 上的检测排序最优。


### 2026年10月26日 C-STMP 引言动机修订

按作者反馈，开篇顺序改为“卫星物联网的覆盖与终端需求—稀疏短包业务下的免授权接入—卫星时延/多普勒—波形选择”，并补全有色训练的误差来源。

| 术语或表述 | 原文依据及位置 | 本稿使用范围 |
|---|---|---|
| satellite IoT / 卫星物联网；grant-free random access / 免授权随机接入 | Shen等，[arXiv:2412.20806v1](https://arxiv.org/html/2412.20806v1)，§I首段、GFRA段及GNSS终端负担段；Liu–Yu，[arXiv:1706.06438](https://arxiv.org/abs/1706.06438)，§I-A/B；Cai等，[arXiv:2506.00581v2](https://arxiv.org/html/2506.00581v2)，§I首两段 | 覆盖偏远地区、低功耗设备、稀疏活跃短包和逐次授权信令开销。卫星传播时延增加授权交互等待是这些条件的直接推论，不引用额外的定量节省或声称GFRA是唯一方案。 |
| DAFT；full diversity / 满分集；embedded channel estimation / 嵌入式信道估计 | Bemani等，[arXiv:2204.12798v2](https://arxiv.org/html/2204.12798v2)，§II-B式(12)、(16)后矩阵分解，§III-A式(18)–(20)，§III-E式(42)–(43)、§IV Theorem 1及式(51)，§VII图9及相邻导频开销比较 | 一维调制由一次IFFT和两组逐点啁啾乘法实现；路径分离和满分集有参数与信道条件。导频/保护符号优势明确归属于该文嵌入式导频比较，不作为本稿多帧GFRA相对OTFS的新实验结论；不声称所有OTFS实现复杂度都更高。 |
| AWGN observation / AWGN观测；colored Gaussian noise / 有色高斯噪声；correlated noise / 相关噪声 | Cai等上述v2 §III-B1式(20)前状态演化说明及式(20)–(23)，§IV；Shastri等，[arXiv:2206.05049v2](https://arxiv.org/html/2206.05049v2)，§III-A式(28)及后文、§III-B式(38)–(41) | 区分物理白噪声与线性滤波/反馈后的等效误差。本文实际算子的直接展开和已保存诊断见[C-STMP逐模块诊断](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/C_STMP_COMPONENT_DIAGNOSTIC_20261025.md)。有色训练扩大离线扰动分布；在线仍查询C=vI。未宣称训练协方差等于真实迭代误差协方差，未新增相关噪声下的实验收益或收敛保证。 |

本次只改C-STMP中英文引言与关联说明；英文贡献、摘要、系统模型、算法和实验源文件保留。中文贡献第3点和章节导航同步已有英文。原STMP、DU原件不变；修订前文件和差异见 [C-STMP/checks/introduction_motivation_20261026/](https://github.com/RESET-cpu/afdm-gfra/tree/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/introduction_motivation_20261026)。


### 2026年10月26日 C-STMP 摘要按指定文献重写

按作者要求，摘要分别以 Shen2025、Huang2026、Cai2026 及后续有色去噪文献为表述依据。本次“DEC”按项目已收藏的 D-GEC 理解，并核对 D-VDAMP。以下是表述来源与项目适配的界限；摘要不插入文献引文，详细引用仍由引言和算法正文承担。

| 摘要中的术语或表述 | 核对的原文位置 | 本稿使用范围 |
|---|---|---|
| multi-frame transmission scheme；large differential delay and Doppler shift；quasi-static property / 多帧传输方案、大差分时延与多普勒频移、准静态特性 | Shen 等作者稿（仅本地历史资料：`reference/literature/shen2025.pdf`），摘要、§II-B，Proposition 1、式(8)–(10)，PDF pp.1、4–5；[原文](https://arxiv.org/html/2412.20806v1#S2.SS2) | 采用原文的准静态特性与连续多帧表述：信道在连续多帧内近似不变，利用多帧增加观测。“共享信道观测”并非 Shen 原词，不作为文献术语。本项目使用 AFDM，采用块内信道不变及跨帧相位分离；不移用其 OTFS 扩频、数据符号检测或三模块稀疏接收机。 |
| AFDM effective channel；fractional delay；Doppler；grid-aligned channel assumptions / AFDM 有效信道、分数时延、多普勒、网格对齐信道假设 | Huang 等正式版（仅本地历史资料：`reference/literature/huang2026.pdf`），摘要及§I，p.2949；§II，p.2950；§III-A，式(6)–(7)，p.2951 | 直接学习完整有效信道分布，避免预设稀疏或路径网格对齐假设；多天线张量是本项目扩展。不写成无任何统计假设，不采用或宣称采用其 Langevin 后验采样。 |
| turbo message passing；channel and device activity denoisers；extrinsic messages / Turbo 消息传递、信道和设备活动去噪器、外信息消息 | Cai 等正式版（仅本地历史资料：`reference/literature/cai2026.pdf`），摘要、§I-A、§III-A/B、§IV-A；[作者稿§III](https://arxiv.org/html/2506.00581v2#S3) | 保留完整用户信道张量的联合去噪和线性模块之间的外信息交换。当前方差由条件均值导数估计，活动概率来自另训分类器；不描述为照搬 Cai 的二阶 score 网络和活动积分。 |
| colored Gaussian noise；covariance matrix / 有色高斯噪声、协方差矩阵 | D-GEC 作者稿（仅本地历史资料：`reference/literature/shastri2022_dgec.pdf`），§III-B式(38)–(41)，PDF pp.15–16；[原文](https://arxiv.org/html/2206.05049v2#S3.SS2)；D-VDAMP（仅本地历史资料：`reference/literature/metzler2020_dvdamp.pdf`），§2.3，PDF p.3；[原文](https://arxiv.org/html/2010.13211v1) | 两文支持按噪声统计条件训练有色去噪器。D-GEC 的 corr+corr 输入独立同协方差噪声样本，D-VDAMP 输入小波子带标准差；本项目输入协方差因子，两者都不是本项目实现的别名。在线仍用标量方差消息，不宣称训练协方差等于实际迭代误差协方差。 |
| conditional-mean derivatives；posterior expected residual energy / 条件均值导数、后验预期残差能量 | 沿用本文件“C-STMP 当前算法稿与用户数实验”中已核对的 Dytso Proposition 1、Vila–Schniter §III-A 式(22)–(27) | 对应本稿第 III-D、IV-B 章的当前实现，表述为估计和更新，不宣称精确神经后验或 EM 单调性。C-STMP 为作者已指定的项目方法名，不添加自拟英文展开。 |

结尾比较依据为当前六档 SNR 的保存汇总 `result/snr_comparison/data/c_stmp_variance_em_1000_snr_m4_p6_20261025/SUMMARY.json`，每档1000场景、已知跨帧相位、观测估计噪声；只声称相对项目原 STMP 在所评估信噪比下的 NMSE/AER 改善。未将收益单独归因于有色训练，未声称所有基线、未知相位或跨信道条件下最优。该评估的回顾性限制保留在实验章与原汇总中。

本次中英文含义对齐，沿用既有简体中文稿；原文提取、五篇PDF的结构核验、修订前备份及差异保存在 [C-STMP/checks/abstract_sources_20261026/](https://github.com/RESET-cpu/afdm-gfra/tree/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_sources_20261026)。文献核验脚本的 POSIX 侧文件接口不适用于 Windows，因此调用同一脚本的标准输出并原样保存 JSON；五篇结构核验均为 PASS。

### 2026年10月26日 C-STMP 摘要严格使用指定原文词汇

作者进一步要求英文摘要不使用指定论文中未出现的词。本次只改摘要、关键词与关联记录。对 Shen2025、Huang2026、Cai2026、D-GEC、D-VDAMP 的原始 PDF 重新校验文件哈希，沿用五篇均为 PASS 的结构预检与逐页文本；匹配范围截至各文 REFERENCES 标题之前。

英文逐词核验只统一大小写与 Unicode 排版字符；不做词干归并、近义词替换或拼写推导，不豁免功能词与缩写，连字符复合词按整个词形检索。摘要中的 C-STMP 方法名没有指定原文词汇依据，因此从本轮摘要移出，但稿件其他位置保留作者已经确定的名称。关键词 Internet of Things 改用原文 Internet-of-Things，中文关键词同步为物联网。

原文已有单词不等于任意拼接均可冒充原文术语。另对 32 个专业短语或关键词检查连续词序，逐项记录 PDF 页码与上下文。句子按本项目实际操作重新组织，不宣称为逐句引用。中文采用对应英文术语的忠实译名。

| 当前表述 | 原文位置与含义 | 本稿边界 |
|---|---|---|
| quasi-static property；consecutive frames / 准静态特性、连续多帧 | Shen，§II-B，式(10)后的说明，PDF pp.4–5：信道在连续 Q 帧中近似不变，多帧增加观测 | 删除“共享有效信道 / shared effective channel”。正文给定的块内信道模型与相位旋转仍由本文公式定义；不将自拟概括归于 Shen。 |
| score-based generative channel prior；AFDM effective channel / 基于得分的生成式信道先验、AFDM 有效信道 | Cai，§I 的贡献说明，PDF p.2；Huang，摘要与 §III-A，PDF pp.1、3（期刊 pp.2949、2951），式(6)–(7) | 先验建模依据 Huang 对完整 AFDM 有效信道的学习；多天线与消息传递接收机是本文实现。不移用其 Langevin 后验采样。 |
| channel and device activity denoisers；scalar variance / 信道和设备活动去噪器、标量方差 | Cai，§III-A/B，PDF pp.5–6 | 当前活动检测由神经网络实现，在线仍使用标量方差。不声称完整实现 Cai 的二阶得分网络。 |
| non-separable denoisers / 非可分离去噪器 | D-GEC，§II-C，PDF p.6 | 仅用作既有去噪器术语，描述本文利用信道相关性的操作；不把本接收机称为 D-GEC。 |
| colored Gaussian noise；covariance matrix / 有色高斯噪声、协方差矩阵 | D-GEC，§III-B，PDF pp.15–16，式(38)–(41)；D-VDAMP，§2.3，PDF p.3 | 前者以独立同协方差噪声样本作为条件，后者输入小波子带标准差；本文输入协方差因子，不能称为其原始网络实现。 |
| conditional mean；derivatives；variance of the denoiser / 条件均值、导数、去噪器方差 | 词汇分别见 D-GEC §II-C，PDF p.6；D-VDAMP §2.1，PDF p.2；Cai 摘要，PDF p.1 | 词汇出现不构成“这些论文提出当前方差估计公式”的证据。本文具体均值导数与协方差关系沿用本文件已核对的 Dytso Proposition 1（PDF p.5，式(22)）；神经网络导数只是近似应用。 |

结尾结果仍仅来自已保存的六档 SNR、每档 1000 场景比较；reference receiver 对应项目原 STMP。相位旋转已知的条件显式保留，不把本项目实验结果归于五篇参考文献，也不单独归因于有色训练。

完整[逐词检查](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/SOURCE_WORD_CHECK.md)、[词形与页码](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/WORD_AUDIT.json)、[短语与上下文](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/TERM_AUDIT.json)可复查；本轮修订前文件另存 before/。

2026年10月26日摘要衔接补充：采用 **Specifically / Subsequently / Building on this**，中文对应“具体而言 / 随后 / 在此基础上”，分别引出具体传输方案、推进至信道先验、再由该先验衔接接收机。Specifically 见 Cai2026 摘要（PDF p.1）；Subsequently 见 Shen2025 §I 贡献说明（PDF p.2）；Building on this 见 Shen2025 §I 相关工作（PDF p.2）。三个完整连接表达均核对原文连续词序，不借用被介绍工作的技术结论。其余摘要表述保持不变。


### 2026年10月26日 C-STMP 摘要四篇核心论文逐句复核

本次将最新摘要的词汇与表述依据限定为 Shen2025、Huang2026、Cai2026 和 D-GEC；不再依赖 D-VDAMP 的词汇。此前五篇范围的说明保留为修订历史，以下为当前版本。按作者要求，完整词形须在四篇参考文献列表之前的摘要或正文出现，大小写与 Unicode 排版统一后逐词匹配，不做词干归并或功能词豁免。

术语有出处不等于整句来自原文。当前八句摘要逐句记录原文位置、用词依据和本项目适配边界，见[逐句依据](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/SENTENCE_SOURCES.md)。传输采用 Shen 的多帧与输入输出关系描述，信道先验采用 Huang 的完整有效信道学习描述，接收机以 Cai 的消息传递框架及 D-GEC 的有色去噪训练为依据。保留 Specifically / Subsequently / Building on this 的递进；通过 we propose、we learn、we develop 的平行句式组织三部分。

| 当前术语 | 原文位置 | 本稿边界 |
|---|---|---|
| known covariance matrix；colored Gaussian noise / 已知协方差矩阵、有色高斯噪声 | D-GEC §III-B，PDF pp.15–16，式(38)–(41) | 本文以协方差因子作为训练条件；D-GEC 的 corr+corr 以独立同协方差噪声样本为条件。不得视为相同网络。在线仍用标量方差消息。 |
| conditional mean；Jacobian；posterior variance / 条件均值、雅可比矩阵、后验方差 | D-GEC §II-C，PDF p.6；Cai2026 §IV-A，PDF p.9，式(44)–(45) | 用 Jacobian 替代仅在此前五篇语料内匹配的 derivatives。四篇支持这些术语与相关背景，不构成本文活动分类特征与均值导数方差估计组合的完整来源；直接数学与分类依据仍见正文 Dytso、Menon–Ong 引用。 |
| baseline receiver / 基准接收机 | baseline 词形见 Cai2026；本项目对照定义见第 VI 节 | 此处仅指项目原 STMP。结果来自六档 SNR 每档 1000 场景的保存汇总；已知相位与比较范围保留，不归为四篇论文的结果。 |

当前中英文摘要同时更新；算法、模型公式、实验结果与权重不改动。完整稿继续只使用 main.pdf，不新增版本 PDF。


### 2026年10月26日 C-STMP 摘要精简为方案层面的表述

按作者反馈，摘要保留传输方案、有效信道先验、Turbo 接收方法三项贡献及已有实验结论。接收机部分压缩为一句：通过有色高斯噪声训练的信道去噪器引入所学先验。turbo message passing 与先验结合见 Cai2026 §I-A、§III-A/B（PDF pp.2、5–6）；channel denoiser 与 colored Gaussian noise 见四篇词形/短语记录，训练思想见 D-GEC §III-B（PDF pp.15–16，式(38)–(41)）。具体组合属于本项目，不当作原文整句或同一网络实现。

外信息交换、协方差条件、标量消息、条件均值、雅可比及方差估计不再出现在当前摘要；正文与其数学引用保持原样。此前八句版本的逐句说明由当前六句[来源对照](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/SENTENCE_SOURCES.md)替代；源文件差异见同目录 CONCISE_REVISION.diff。当前版本继续使用四篇范围的严格词形核验，保留 Specifically / Subsequently / Building on this 及已知相位的实验限定。


### 2026年10月26日 C-STMP 摘要补充有色训练动机

将仅说明噪声类型的 to handle colored Gaussian noise 改为“trained with colored Gaussian noise to account for correlations in the denoiser input error”。denoiser input error 采用 D-GEC 摘要（PDF p.1）与 §III-A（PDF p.11，式(28)）原词；correlations 的完整词形见 Cai2026 §I-A（PDF p.2），输入误差相关性的含义依据 D-GEC 对非白误差与算子关系的讨论及 §III-B 的 correlated noise / colored Gaussian noise（PDF pp.15–16，式(38)–(41)）。本项目引言第80–103行已经说明线性滤波、残余干扰和反馈可产生相关误差；摘要只交代训练目的，不声称消除失配、精确匹配实际误差分布或证明有色训练的独立收益。

按作者要求删除摘要末句的 with known phase rotations 及对应中文，仍保留 across the considered signal-to-noise ratios 的评估范围。当前已知相位设置继续保留在实验章和结果记录；未知相位是待补实验，不是已完成结果。本轮仅修改摘要及其来源记录，不运行实验。


### 2026年10月26日 C-STMP 摘要统一先验学习与有色训练的关系

根据作者指出的概念关系，将有色 Gaussian 训练归入信道先验学习：摘要第4句说明直接在 AFDM 有效信道上学习先验，第5句明确 this training 使用 colored Gaussian noise，第6句只说明 Turbo 接收机引入前述同一先验。不得将其描述成先单独学习一个先验，再另训一个信道去噪器。

本稿第IV-A节的协方差加权去噪损失与得分表示已说明，这一信道均值网络的训练就是先验学习的实现。Huang2026 提供在 AFDM 有效信道上直接学习先验的依据（摘要与 §III-A，PDF pp.1、3）；D-GEC 提供有色去噪训练的依据（§III-B，PDF pp.15–16，式(38)–(41)）；Cai2026 提供在消息传递中引入所学先验的依据（§I-A、§III-A/B，PDF pp.2、5–6）。本项目对这些方法的组合不是任一文献的完整原算法。现有活动分类器仍保留，摘要不引入新的网络或训练步骤。

四篇原文完整词形约束、三项贡献的衔接以及不在摘要强调已知相位的要求继续适用。术语与七句来源映射见当前逐句依据文件；本轮只调整摘要叙述，不修改模型、训练方法、推断实现或实验结果。


### 2026年10月26日 C-STMP 摘要以目的从句引出传输方案

按作者反馈，将第二句句首 Specifically 改为 To handle the large differential delay and Doppler shift，并将后面的方案与输入输出推导并列。中文同步为“针对大差分时延和多普勒频移，提出……并推导……”。该短语采用 Shen2025 原词：§II-B（PDF p.4）说明方案的处理目标，PDF p.15 可核对完整连续词序。正文语序将目的置前属于本稿改写，不声称整句照录或 Shen 已提出 AFDM 方案。

本次的衔接是“问题及目标—传输方案”，后面继续用 Subsequently 引出先验学习、Building on this 引出使用所学先验的接收机。保留有色训练属于先验学习的关系及此前精简范围；四篇原文完整词形约束继续适用。


## 2026-10-26：摘要显式标出第一步

采用 Shen2025 摘要（PDF p.1）的 We firstly propose，在谓语中标出多帧传输与建模是第一步；随后用 Shen PDF p.2 的 Subsequently 衔接有效信道先验学习，再用同页 Building on this 表示接收机以前述先验为基础。中文同步为“首先—随后—在此基础上”。这三个表达用于本文三项贡献的组织顺序，并非声称三项贡献都由 Shen 提出；Shen 原方案采用 OTFS，本文采用 AFDM。有色高斯噪声训练仍属于同一次信道先验学习。逐词、连续短语与逐句适配边界见 C-STMP/checks/abstract_original_words_20261026/ 下的 WORD_AUDIT.json、TERM_AUDIT.json 和 SENTENCE_SOURCES.md；本次源文件差异见 SEQUENCE_REVISION.diff。


## 2026-10-26：摘要结句概括性能比较

结句改为 Numerical simulations demonstrate that the proposed receiver outperforms the baseline in terms of activity detection and channel estimation. Numerical simulations 与 activity detection and channel estimation 采用 Cai2026 摘要（PDF p.1）的原词；比较句结构及 in terms of 参照 Shen2025 摘要（PDF p.1），the proposed receiver 见 Shen PDF p.10，outperforms 见 Huang2026 摘要（PDF p.1）。这里概括本项目活动检测与信道估计的性能比较，不将整句或比较结果归属于参考论文。baseline 仍指项目原 STMP；事实依据是已核验的六档 SNR、每档1000场景汇总，结果数据及其实际已知相位条件未变。未加入显著性、最优性、全部基准优越性或跨条件鲁棒性主张。源文件差异与逐句边界见 C-STMP/checks/abstract_original_words_20261026/CLOSING_SENTENCE_REVISION.diff 和 SENTENCE_SOURCES.md。


## 2026-10-26：按 Cai 摘要层次展开接收机

接收部分扩为四句：线性估计与信道、活动去噪；每个设备的完整信道块联合估计；所学去噪器及其雅可比给出均值和方差估计；活动概率参与外信息更新。linear estimation、channel matrix、factorizing it element-wise、posterior mean、posterior variance、posterior probability of activity（Cai PDF p.7，式(30)后）和 extrinsic message 的依据为 Cai2026 摘要及§I-A、§III–V（PDF pp.1–2、5–9），Jacobian 原词见 D-GEC PDF pp.6、13。原词与具体操作的依据分别记录，不将本稿所有操作都归给四篇论文：本稿条件均值的雅可比方差公式见第 IV-B 节，直接数学依据为正文已有 Dytso Proposition 1；活动概率沿用本稿已定义分类器及先验校正。保留用户块内部联合先验，不作逐元素独立分解，依据本稿第 II 节 working-posterior；跨用户仍采用既定边缘先验乘积。未训练额外方差网络，也未增加一项独立信道训练。逐句页码与适配边界见 C-STMP/checks/abstract_original_words_20261026/SENTENCE_SOURCES.md；源文件差异见 RECEIVER_DETAIL_REVISION.diff。


## 2026-10-26：接收机摘要回到 Cai 的设计层次

按作者反馈，将接收部分的雅可比、活动后验概率和外信息更新步骤收回正文，保留三句：每个设备整块信道的联合建模；所学先验以 minimum mean-squared error denoiser 形式融入接收机；由该去噪器获得消息传递所需的 posterior mean and variance。设计层次及术语参照 Cai2026 摘要（PDF p.1），均值和方差原词另见§III-B（PDF pp.6–7）。MMSE 是本稿第 IV-A 节去噪损失的条件均值目标，不声称学习网络精确达到理论最优；方差仍依据第 IV-B 节从同一均值映射的雅可比估计，没有新增方差网络或另行信道训练。整块先验依据本稿 working-posterior，跨用户独立近似不变。逐句适配边界与差异见 C-STMP/checks/abstract_original_words_20261026/SENTENCE_SOURCES.md 和 RECEIVER_CONCEPT_REVISION.diff。


## 2026-10-26：接收部分严格采用 Cai 完整原句

按作者最新要求，接收部分改为 Cai2026 摘要（PDF p.1）的两句完整原文，分别以 We propose to incorporate 和 This design enables 开头。两句并非相邻摘录，但句内词序、用词与标点均未改动；仅统一 PDF 排版连字和换行。完整摘录、PDF 哈希及逐句匹配位置见 [CAI_VERBATIM_RECEIVER.json](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/CAI_VERBATIM_RECEIVER.json)。没有将原文含 novel 的 TMP 框架句当作本稿新增框架贡献，也没有照搬方差学习句以暗示另训二阶得分网络。正文中的 TMP 结构、雅可比方差与活动分类器保持原定义。performance limit 为研究目标，MMSE 为条件均值目标，不作理论极限已达到的声明。句子来源明确归于 Cai；具体边界见 [SENTENCE_SOURCES.md](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/SENTENCE_SOURCES.md)，差异见 CAI_VERBATIM_RECEIVER_REVISION.diff（仅本地历史资料：`paper/checks/abstract_original_words_20261026/CAI_VERBATIM_RECEIVER_REVISION.diff`）。

缩写工具未能自动识别 minimum mean-squared error (MMSE) 中连字符连接的双 M/S 首字母，人工对照 Cai 原句确认定义正确；不为适配检查器改写原句或添加豁免。


## 2026-10-26：接收部分明确承接第二点的所学先验

作者指出，Cai 原摘要首次引出先验的句子放在本稿第二点之后会重复引出先验。本次在该句中以 the learned channel prior 回指本稿第4–5句同一次有色噪声训练所得先验，并增加 Finally（Cai PDF p.3）标明第三步；其余句式保留 Cai 摘要（PDF p.1），下一句 MMSE 去噪仍完整照录。第一句现为明确记录的最小衔接改写，不能再称整句照录；没有新增技术术语、另一先验或额外训练。逐段出处及完整差异见 [CAI_RECEIVER_TRANSITION.json](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/CAI_RECEIVER_TRANSITION.json) 和 RECEIVER_TRANSITION_REVISION.diff（仅本地历史资料：`paper/checks/abstract_original_words_20261026/RECEIVER_TRANSITION_REVISION.diff`）。


## 2026-10-26：以已有先验为接收机前提的衔接

根据作者对 Finally 的反馈，采用 Cai2026 第 V-A 节（PDF p.9）原句 With the two score networks available, we are able to obtain ... 的 With ... available 结构，适配为 With the learned channel prior available，并将后续重复名词短语改为 it。主句仍采用其摘要（PDF p.1）的引入消息传递表述，下一句 MMSE 去噪保持完整原文。这里仅适配连接句式，不引入 Cai 的两个得分网络，也不声称第一句逐字照录。来源与差异见 [CAI_PRIOR_AVAILABLE.json](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/CAI_PRIOR_AVAILABLE.json) 和 PRIOR_AVAILABLE_REVISION.diff（仅本地历史资料：`paper/checks/abstract_original_words_20261026/PRIOR_AVAILABLE_REVISION.diff`）。


## 2026-10-26：摘要删除性能极限的目标性表述

根据作者反馈，删除接收部分的 so as to push towards the performance limit of JADCE 及对应中文，仅保留将第二点所学先验引入消息传递，并由下一句说明 MMSE 去噪器的作用。删减没有引入新词、技术术语或结果主张；第一句仍为此前已披露的 Cai 句式适配，第二句仍为 Cai 摘要完整原文。依据与范围见 [CAI_RECEIVER_CONCISE.json](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/CAI_RECEIVER_CONCISE.json)，差异见 REMOVE_PERFORMANCE_ASPIRATION.diff（仅本地历史资料：`paper/checks/abstract_original_words_20261026/REMOVE_PERFORMANCE_ASPIRATION.diff`）。


## 2026-10-26：摘要恢复设计与作用的整体承接

整段重新核对后，保留传输—先验—接收顺序，将第二点写为直接学习含分数时延与多普勒的有效信道先验，并以 The training 回指同一次有色噪声训练。接收部分恢复 Cai2026 摘要（PDF p.1）的 turbo message passing (TMP) framework、models the entire channel matrix as a super node 与 rather than factorizing it element-wise，使后句 This design 有具体前项。句首沿用其 §V-A（PDF p.9）的 With ... available 结构，谓语用其 §I-A（PDF p.2）的 we employ，删除 novel 以表明采用既有框架。第一句是来源明确的句式适配，第二句保持完整原文；联合建模范围为每个用户的整块信道，跨用户先验仍按原模型近似分解。结句的 the original score-based TMP receiver 是本项目原 STMP 基线说明，score-based TMP 见 Cai 摘要；不作为自创方法名称。对应关系、实际方法边界及源文件差异见 [COHESION_CHECK.json](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/COHESION_CHECK.json)、[SENTENCE_SOURCES.md](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/SENTENCE_SOURCES.md) 与 COHESION_REVISION.diff（仅本地历史资料：`paper/checks/abstract_original_words_20261026/COHESION_REVISION.diff`）。


## 2026-10-26：接收段在保留技术含义的前提下与 Cai 原句区分

按作者最新要求，第6–7句不再完整照录 Cai，而是先说明所学先验通过 minimum mean-squared error (MMSE) denoiser 用于 turbo message passing (TMP) receiver，再以 To this end 解释整个信道矩阵的 super node 表示及不对先验作 element-wise 分解。技术依据仍为 Cai2026 摘要、§I-A、§III/III-B（PDF pp.1–2、5–7）；术语保留原词，整句明确记录为改写。联合范围仍限于每个设备的整块信道，跨用户边缘先验乘积不变；MMSE 仍指条件均值目标，前述有色训练所学先验就是接收机所用先验。未增加训练、网络或推断步骤。当前句式与含义对照见 [RECEIVER_PARAPHRASE_CHECK.json](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/RECEIVER_PARAPHRASE_CHECK.json)，逐句出处见 [SENTENCE_SOURCES.md](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/SENTENCE_SOURCES.md)。此前各版关于“完整原句”的说明仅适用于当时版本。


## 2026-10-26：接收段改用框架内的结构承接，暂不编译

按作者反馈，将 To this end 改为 Within this framework，以 this framework 回指上一句的 TMP 接收框架；中文同步为“在该框架中”。该表达为句式适配，不声称在 Cai 中逐句照录；技术含义及术语依据仍为 Cai2026 摘要、§I-A 与 §III（PDF pp.1–2、5–7）。本次只改源稿，作者要求确认措辞后再编译，现有阅读 PDF 保留上一编译版本。记录见 [RECEIVER_FRAMEWORK_TRANSITION.json](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/RECEIVER_FRAMEWORK_TRANSITION.json)。


## 2026-10-26：摘要删除 super node，直接说明整块信道联合去噪

按作者要求，摘要不再使用 super node，改为 the entire channel matrix is denoised jointly to exploit channel correlations，后接 without factorizing its prior element-wise。这里描述已有方法的统计作用，不新增方法名；channel correlations 的连续原词与非可分去噪含义依据为 Cai2026 §I-A（PDF p.2），每个设备的联合信道先验及 MMSE 去噪依据为其 §III-B（PDF pp.6–7）和本稿 working-posterior。联合范围不跨越独立用户先验；正文对 Cai 的方法引用保留。信道系数间的相关性与有色训练所针对的输入误差相关性应区分。中英文已同步，按作者要求继续只修改源稿、暂不编译。见 [RECEIVER_JOINT_DENOISING.json](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/RECEIVER_JOINT_DENOISING.json)。


## 2026-10-26：摘要聚焦三项内容，接收部分以 TMP 框架为主

按作者确认，摘要第一点聚焦处理大差分时延和多普勒，保留 Shen2025 摘要及 §II-B（PDF pp.1、4–5）的 multi-frame transmission scheme、large differential delay and Doppler shift 与 input-output relationship，并适配本稿 AFDM 模型。第二点保留 Huang2026 摘要及 §III-A（PDF pp.1、3）的有效信道学习和不预设限制性稀疏/网格对齐先验的表述，同时以 D-GEC §III-B（PDF pp.15–16）为有色训练依据。第三点突出 turbo message passing (TMP) framework、linear estimation 与 denoising 的迭代，以及 minimum mean-squared error (MMSE) denoiser 对所学先验的使用，技术出处为 Cai2026 摘要及 §III/III-B（PDF pp.1、5–7）。不将既有 TMP 框架声明为本稿首创。

摘要移除多帧准静态观测机制的单独解释，以及整块先验分解、信道相关性利用等接收细节；这些调整只改变叙述重心，不改变正文模型和实现。输入误差相关性仍作为有色噪声训练的动机，不能与信道自身的统计相关性混同。现为六句摘要，当前对应关系见 [SENTENCE_SOURCES.md](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/SENTENCE_SOURCES.md)。继续遵守作者要求，确认措辞后再编译。


## 2026-10-26：摘要以前两点对应标题，TMP 降为简短的推断说明

按作者最新意见，摘要主线对齐标题的 GNSS-Independent MIMO-AFDM 与 Generative-Model-Aided：先交代无GNSS辅助的卫星免授权接入，再说明卫星端处理大差分时延/多普勒及输入输出关系，随后集中描述直接学习有效信道先验与有色噪声训练。satellite receiver 采用 Shen2025 摘要及 §II-B（PDF pp.1、4）的原词；本稿系统模型开头保留公共定时和参考时延补偿条件，不声称完全无任何同步。Huang2026 与 D-GEC 的技术依据沿用当前逐句记录。

TMP 仅用一句说明所学先验用于 JADCE，其术语与方法依据仍为 Cai2026 摘要及 §III（PDF pp.1、5–7）。摘要移除线性估计迭代及 MMSE 缩写等实现说明，正文结构和引用保持原样。Cai 的标题和摘要强调消息传递与生成式先验结合及新 TMP 框架；这是对文稿内容的比较，不把作者写作动机当作已知事实。当前修订仅改变主次与语言组织，不改变技术方法或实验结论，仍按用户要求暂不编译。见 [TITLE_ALIGNED_FOCUS.json](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/TITLE_ALIGNED_FOCUS.json)。


## 2026-10-26：摘要使用 MP 类别，接收描述突出所学先验

按作者最新要求，摘要将具体 TMP/STMP 名称改为上位术语 message passing (MP)，并用两句保留接收过程：同一所学先验用于 minimum mean-squared error (MMSE) denoising，再将 linear estimation 与所学去噪器结合以迭代完成 JADCE。message passing (MP) 的原词与缩写见 Shen2025 §I（PDF p.1），MMSE 去噪与线性估计/去噪迭代依据为 Cai2026 摘要、§I-A、§III–IV（PDF pp.1–2、5–9）。摘要采用上位类别并不改变实际算法，正文第III节对 STMP 结构与 Cai 的引用完整保留；也不声明提出全新的 MP 框架。MMSE 是条件均值目标，活动分类器、均值导数方差及消息更新仍按正文。

结句用 the baseline receiver 指代同一个项目原始 STMP 对照，具体身份、配置与比较条件仍在实验章；不得据此泛化为优于所有 MP 接收机或所有基准。所有当前英文词形仍按四篇文献核对。完整句子是本稿适配，不因词形出现而成为原文引句。中英文源稿已同步，按作者要求暂不编译。当前记录见 [LEARNED_PRIOR_MP_FOCUS.json](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/LEARNED_PRIOR_MP_FOCUS.json)。


## 2026-10-26：接收句说明后验均值与方差估计的作用

摘要将笼统的线性估计与去噪结合改为：The denoiser provides posterior mean and variance estimates for iterative joint activity detection and channel estimation (JADCE). posterior mean and variance 见 Cai2026 §III-B、§IV–V-A（PDF pp.6–7、9–10）及结论（PDF p.15）。本稿由条件均值网络及其导数获得相应估计，活动概率另由分类器提供；不声称学习独立二阶网络，也不声称有限网络获得精确后验。句子为本稿改写，四篇来源核验只证明词形与短语存在。中英文已同步，摘要外正文未改，继续暂不编译。见 [RECEIVER_POSTERIOR_ROLE.json](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/RECEIVER_POSTERIOR_ROLE.json)。


## 2026-10-26：展开接收段的消息更新作用

摘要接收段现在依次说明所学先验用于MMSE去噪、每次迭代提供信道后验均值与方差估计、这些估计参与去噪与线性估计模块间的外信息消息更新。extrinsic message、linear estimation module、denoising module 见 Cai2026 §III（PDF pp.5–8）；后验统计量到信道外信息的关系见式(25)–(27)，随后结合活动估计回传线性模块。本文相应实现见第III节。摘要未声称直接传递原始信道后验均值，或由均值网络单独完成活动检测。posterior mean and variance 的来源沿用前条。中英文同步，当前摘要八句；正文、模型和PDF均未修改，暂不编译。见 [RECEIVER_MESSAGE_ROLE.json](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/RECEIVER_MESSAGE_ROLE.json)。


## 2026-10-26：摘要加入单独训练的活动概率网络

Cai2026 §III-B 式(28)–(31)（PDF p.7）通过解析消息计算活动概率；§V-A（PDF p.9）明确 device activity denoiser 与 linear estimator 为 analytically derived。本稿第IV-C–D节单独训练分类器，以查询、噪声水平及冻结信道去噪输出等特征估计对数密度比，经先验修正得到活动概率。该差异可在摘要中说明，但不能将“分开处理信道和活动”作为区别，因为 Cai 也已如此处理。

四篇核心论文正文未检出 classifier；为保留作者词汇限制，摘要采用 a separately trained neural network，并以 uses the denoiser output to estimate device activity probabilities 描述其功能。neural network 的原词见 Cai §I-B（PDF p.3），device activity 见其 §III-B 等。该句是本稿方法说明，不是 Cai 原句。分类与密度比估计的直接方法来源仍为既有 Menon–Ong §3 式(6)–(8)、§4.2 式(16)–(17)，不宣称分类方法首创，不声称去噪输出是唯一输入或已验证其独立收益。当前八句中英文摘要同步，未编译；见 [RECEIVER_ACTIVITY_NETWORK.json](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/RECEIVER_ACTIVITY_NETWORK.json)。


## 2026-10-26：从输出目标说明活动网络

参照 Shen2025 §IV-A 式(60)–(61)、§IV-B（PDF p.11）将CNN功能描述为估计发送符号后验分布的方式，本稿摘要改为 separately trained neural network is used to estimate the posterior probability of activity for each device。posterior probability of activity 连续原词见 Cai2026 §III-B 式(30)之后（PDF p.7）。两文检测对象不同，不将 Shen 的符号CNN写成本稿活动算法来源。

源码核对：STMP/activity.py forward 与 FrozenEvidence.infer 每个设备返回一个标量logit；平衡训练时理想logit为 log(q1/q0)，有限网络提供估计。STMP/denoiser.py 第171–172行先减训练先验log odds，再加实际活动先验log odds，经过sigmoid形成活动概率。摘要 is used to estimate 描述这一整体用途，避免声称网络原始输出直接是概率或硬判决。训练密度比与接收机真实输入分布仍可能不完全匹配，不声称精确后验。中文同步，未编译。见 [RECEIVER_ACTIVITY_OUTPUT.json](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/RECEIVER_ACTIVITY_OUTPUT.json)。


## 2026-10-26：活动网络的计算动机替代单独训练措辞

摘要去掉 separately trained，从活动推断中所需信息说明网络：To avoid high-dimensional integrals in activity detection, a neural network estimates the posterior probability of activity under the learned channel prior. high-dimensional integrals 是 Cai2026 §II-C、§III-B、§IV（PDF pp.5、7–8）的原词；posterior probability of activity 见其式(30)之后（PDF p.7）。Cai 原文关于高维积分的语境是信道后验矩，本稿活动场景的依据则是自身第III节 query-densities 与 local-activity：活跃密度 q1 对高维信道先验积分，活动概率需要 q1/q0。训练分类网络加活动先验修正提供避免接收阶段直接积分的计算途径，数学与训练来源仍为第IV-C节及 Menon–Ong。

分类器不是唯一可能的方法，不声称 Cai 的解析活动更新需要数值高维积分，也不声称完整信道均值函数理论上无法恢复密度。此处是本方法的计算动机，并非新的运行时间或性能比较。概率指网络logit经先验修正后的估计，不保证精确后验。中英文源稿同步，摘要外正文和PDF不变，暂不编译。见 [RECEIVER_ACTIVITY_MOTIVATION.json](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/RECEIVER_ACTIVITY_MOTIVATION.json)。


## 2026-10-26：摘要接收段缩为两句

按作者意见，删除摘要对高维积分、后验矩及外信息更新的详细展开，仅保留所学先验进入MP接收机以及神经网络估计后验活动概率、配合MMSE信道去噪的功能。术语沿用 Cai2026 摘要、§III-B式(30)之后、§IV（PDF pp.1、7–9）和 Shen2025 §I（PDF p.1）；to complement 表达两项任务的互补，不是新方法名或性能保证。分类概率仍包含网络logit之后的先验修正读出。详细数学依据保留正文，未修改引言或算法。当前中英文摘要七句、未编译；见 [RECEIVER_CONCISE_ROLES.json](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/RECEIVER_CONCISE_ROLES.json)。


## 2026-10-26：接收段两句建立明确承接

第二句改用 Within this receiver 回指上一句的MP接收机，并以 while 并列说明同一接收机内所学先验用于MMSE信道去噪、神经网络用于后验活动概率估计的分工。未新增技术主张，MMSE与活动概率的术语和边界沿用 Cai2026 摘要及§III-B式(30)之后（PDF pp.1、7），本稿分类器读出仍含活动先验修正。四篇词形与28项短语核验通过，中英文同步，暂不编译。见 [RECEIVER_LINKED_ROLES.json](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/RECEIVER_LINKED_ROLES.json)。


## 2026-10-26：摘要明确去噪特征与活动密度比估计

活动分支改为 uses the denoiser input and output to estimate the density ratio for activity detection，以本稿第IV-C/D节和STMP/activity.py的实际特征及目标区别于泛泛的概率预测。网络还使用噪声水平，句子不穷举特征；原始输出是平衡训练下估计对数密度比的logit。density ratio 的直接出处为既有 Menon–Ong（2016）标题及§3式(6)–(8)、§4.2式(16)–(17)，本轮重新读取官方PMLR标题与摘要：https://proceedings.mlr.press/v48/menon16.html 。此连续术语不冒称来自四篇核心论文，单词仍全部在四篇正文中检出；独立术语来源见 ACTIVITY_DENSITY_RATIO_SOURCE.json。该设计不声明普遍首创，特征是否单独改善性能仍需相应消融。中英文同步，摘要外正文未变，暂不编译。见 [RECEIVER_DENSITY_RATIO_FEATURES.json](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/RECEIVER_DENSITY_RATIO_FEATURES.json)。


## 2026-10-26：明确命名 learned density ratio estimator

摘要不再以泛称 neural network 为主语，改为 a learned density ratio estimator，直接突出活动推断模块，并保留其使用MMSE信道去噪器输入、输出的联系。density ratio estimator 是 Menon–Ong（2016）§4.2式(17)之前的连续原词，PDF p.3 / 印刷p.306；本轮直接核对官方PDF https://proceedings.mlr.press/v48/menon16.pdf 。该式之后说明logistic损失和平衡先验下以指数变换得到密度比，与本稿logit表示一致。learned 只说明训练获得，不声明密度比估计方法首创。四篇词形核验与26项核心短语核验通过，估计器术语独立依Menon–Ong记录。中英文同步、未编译；见 [RECEIVER_DENSITY_RATIO_ESTIMATOR.json](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/RECEIVER_DENSITY_RATIO_ESTIMATOR.json)。


## 2026-10-26：两类推断量及对应计算动机

摘要依次说明：学习先验用于MP中的MMSE去噪，以均值及其导数给出后验矩估计，避免直接后验高维积分；学习密度比估计器利用去噪输入输出获得活动概率，避免分别估计两种观测密度。后验矩积分的原文语境见 Cai2026 §III-B、§IV（PDF pp.7–8）；density ratio estimator见Menon–Ong §4.2式(17)，本稿实现见第IV-B/C节。

不能写成分类器“利用均值和后验方差直接输出活动概率”：STMP/activity.py inputs读取观测R、输入噪声方差v和去噪均值F，未使用后验方差tau；STMP/denoiser.py第171–172行还执行先验校正及sigmoid读出。英文input and output与obtain概括实际过程。两个避免不是独立性能或运行时间证明，也不声称Cai活动更新需要数值积分或本稿全部推断无Gaussian近似。中英文同步、未编译，见 [RECEIVER_TWO_INFERENCE_ROLES.json](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/RECEIVER_TWO_INFERENCE_ROLES.json)。


## 2026-10-26：以活动不确定性承接信道去噪与密度比估计

第二句改为 To incorporate activity uncertainty into channel estimation，删除重复的without estimating the two probability densities。activity uncertainty 为 Cai2026 §III-B 式(15)后（PDF p.6）的原词，原文明确条件于活跃假设进行信道去噪、另以活动更新处理不确定性。本稿第III节 exact-local-moments、mixture、joint-spatial-covariance分别给出活动概率加权的均值和包含p(1-p)项的协方差，故该动机与实现一致。活动网络仍以R、输入噪声方差v和F为特征，不使用后验方差tau；概率由logit经先验修正读出。

此改写不把活动不确定性处理本身当作相对Cai的创新；区别仍是本稿学习的密度比估计器。条件信道后验矩和活动后验概率分工形成衔接，未新增收益或精确性主张。中英文同步、未编译；见 [RECEIVER_ACTIVITY_UNCERTAINTY.json](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/RECEIVER_ACTIVITY_UNCERTAINTY.json)。


## 2026-10-26：摘要省略分类器特征枚举

核对STMP/activity.py inputs后，uses the denoiser input and output在概括意义上成立，但output实际仅为去噪均值F，另有输入噪声方差v与派生能量特征；它并非后验方差tau。摘要删去该实现细节，改用a learned density ratio estimator provides activity probabilities，保留活动不确定性的动机。provides描述密度比结合活动先验后的模块读出，不声明网络原始输出直接是概率。来源与方法边界沿用上一条、Menon–Ong §4.2式(17)及本稿第III/IV-C节。中英文同步、未编译，见 [RECEIVER_CONCISE_ACTIVITY_READOUT.json](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/RECEIVER_CONCISE_ACTIVITY_READOUT.json)。


## 2026-10-26：以MP中两类估计的配合收尾

摘要接收段增加收尾：The receiver combines the channel statistics and activity probabilities in iterative message updates for joint activity detection and channel estimation (JADCE). 本稿第III节mixture、joint-spatial-covariance与joint-average-variance先组合条件信道矩和活动概率，再进行外信息反馈和迭代，故该句概括实际协作关系。Cai2026 §III-B/C、算法1（PDF pp.7–8）为对应消息传递背景；具体概率由本稿密度比网络及先验修正给出。不声称两网络直接互换消息、独立决定全部更新或新增性能收益。所有词形四篇核验通过，密度比估计器术语继续单独引用Menon–Ong。中英文同步、未编译，见 [RECEIVER_MP_CLOSING.json](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/RECEIVER_MP_CLOSING.json)。


## 2026-10-26：参照Shen与Cai改写接收收尾

The resulting soft information is iteratively exchanged with the linear estimation module for joint activity detection and channel estimation (JADCE). soft information exchanged的句式依据为Shen2025摘要（PDF p.1），迭代交换见其§III（PDF pp.5–6）；linear estimation module及两模块迭代见Cai2026 §I-A、§III（PDF pp.2、5）。本稿第III节开头及外信息更新与此描述相符。resulting回指条件信道矩和活动概率所形成的软信息，不表示两个网络直接互相传递消息，亦非原始活动概率直接输入线性模块。句子是本稿适配，不是单篇原句。中英文同步、未编译，见 [RECEIVER_SOFT_INFORMATION_CLOSING.json](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_original_words_20261026/RECEIVER_SOFT_INFORMATION_CLOSING.json)。


## 2026-10-27：作者确认摘要定稿与编译

采用作者提供的七句摘要，唯一英文措辞调整为minimum mean-square error改成minimum mean-squared error（作者明确选择）。其余precompensation、perturbations、density-ratio等词形保留作者原文，不再冒称该版本满足旧四篇完整词形限定。minimum mean-squared error与Cai2026摘要一致；模型与方法对应关系见 [定稿逐句依据](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_final_20261027/SENTENCE_SOURCES.md)。密度比术语的直接来源仍为Menon–Ong §4.2式(17)。These posterior moments are combined with soft activity probabilities描述条件矩与活动概率的组合，不表示分类器输入了后验方差。

按作者授权更新唯一main.pdf，中文同步；delay–Doppler在源TeX中以等价的delay--Doppler编码以适配模板字体。此前所有源稿迭代记录为历史版本，当前措辞与编译状态见 [最终核验](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_final_20261027/VALIDATION.json)。

## 2026-10-27：引言结构修订（待审阅，未编译）

引言按多帧AFDM传输建模、有效信道生成式先验及有色扰动训练、结合密度比估计的MP接收机展开。Shen方案采用其spreading-based multi-frame OTFS transmission scheme及quasi-static properties原词（§I贡献，PDF p.2；§II-B，PDF p.4），不把shared channel作为Shen原文表述。Huang的AFDM effective channel与restrictive sparse or grid-aligned channel assumptions见摘要及§I（PDF p.1）；有色去噪动机采用Shastri §III-A/B（PDF pp.11、15–16）的generalized expectation-consistent approximation及colored Gaussian noise，不将该文的结论泛化为本稿AFDM误差白化保证。Cai的posterior mean and variance、activity uncertainty及模块交换沿用§III–IV（PDF pp.5–9）。密度比估计器新增既有menon2016引文，其术语来源为§4.2式(17)，不归于Cai。具体公式对应、页码及表述边界见[本轮来源记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/introduction_revision_20261027/SOURCES.md)。本轮不新增方法名称，不改摘要、模型或接收算法；按作者要求不编译。

## 2026-10-27：保存作者确认的引言前三段，第四段单独待审

按作者要求，将 C-STMP 的现行英文引言原字节保存为 sections/01_introduction_old.tex，并在 sections/01_introduction.tex 中仅放入本聊天确认的三段英文。内容逐段保留，仅将聊天编号引用改为 BibTeX 键、将 delay–Doppler 的短横编码为 LaTeX 的 --。原文内容和备份字节均已核验；Xu 的 xu2026 文献条目从此前核实的条目补入 references.bib。未编译，第四段仍为聊天草稿。

前三段术语依据：GNSS-assisted pre-compensation、large differential delays and Doppler shifts、multi-frame OTFS、quasi-static properties，见 Shen §I、§II-B（PDF pp.2、4–5）；Release 17 pre-compensation 见 TS 38.300 V17.2.0 §16.14.2.2（pp.178–179）；GNSS independent operation 见 TR 22.865 的研究范围及 3GPP Release 19 官方讨论材料；one-dimensional chirp modulation、modulation complexity、Doppler robustness 见 Ding §I、Huang §I（各 PDF p.1）；full diversity 及 chirp parameters 见 Bemani §III-E、§IV。此处复杂度比较限定于调制变换。

第四段待审术语依据：joint activity detection and channel estimation、compressed sensing、statistical channel model / discrete transform-domain sparsity 见 Cai §I（PDF pp.1–2）及 Ding §I（PDF p.1）；structured channel priors 见 Shen §III（PDF pp.5–6）；adaptive sparsity pattern learning、graph neural network、delay-Doppler domain 见 Ding §III-B（PDF p.3），其预设通道模型与离散稀疏表示见 §III-A 式(10)；fractional delays / Doppler shifts、power leakage、AFDM effective channel 及 restrictive sparse or grid-aligned channel assumptions 见 Huang 摘要、§II-B 式(5)后讨论（pp.2949–2950）。


## 2026-10-27：保存作者确认的引言第四段

将聊天确认的第四段追加至 sections/01_introduction.tex，并同步工作区英文阅读稿。前三段及所有 old 文件原字节保留；未编译。第五段仍单独在聊天中供作者审阅。

首句按作者要求沿用 Ding §I（PDF p.1）的 JADCE prerequisite 原句；CS formulation 和 structured priors 见 Ding §I、Shen §III。graph neural network / adaptive sparsity pattern learning / delay–Doppler grid 见 Ding 摘要及 §III-A/B（PDF pp.1、3），区分可学习的稀疏模式与预设的离散稀疏表示。实际传播环境、fractional Doppler shifts / fractional time delays、power leakage 与有效信道稀疏性减弱见 Huang §II-B 式(5)后的首句（p.2950）；按作者要求在句首增加 However，并省略式号及矩阵符号。末句学习有效信道先验的动机依据 Cai §I（PDF pp.1–2）和 Huang 摘要、§II-B。


## 2026-10-27：保存作者确认的引言第五段

将作者确认且已核对术语的第五段追加至 sections/01_introduction.tex，并同步工作区英文阅读稿。前四段及所有 old 文件保留；第六段尚未写入，未编译。

score-based generative models / score function 见 Song–Ermon（2019）摘要及 Arvinte–Tamir（2023）摘要；从信道样本学习信道分布的表述依据后者。AFDM effective channel、score-based learning、fractional delay–Doppler off-grid leakage 见 Huang（2026）摘要与 §I（p.2949），posterior-sampling-based inference 与迭代 Langevin 更新见 §III-B（p.2951）。two-stage algorithm、Transformer-based detector、generative diffusion models、joint channel estimation and data detection 见 Ying 等（arXiv:2505.12382v3）摘要及 §I-B；iterative posterior sampling 见 §III-B、§V，score function computations 及计算复杂度见 §V-E。两种方法重复进行 score 计算的开销为上述算法机制的概括，未添加实测运行时间或具体采样步数；本段完整随机接入接收方案对应 Ying（ying2026），不对应 Ding。


## 2026-10-27：按作者要求保存引言前六段并通读论证

将当前聊天第六段追加至 sections/01_introduction.tex，同步工作区 TeX 与英文阅读稿。前五段及 old 文件原字节保留；第七段各候选尚未确认，因此未写入。未编译。

第六段依据 Cai（arXiv:2506.00581v2）§I-A（p.2）的 score-based generative channel priors、turbo message passing、single-step minimum mean-squared error denoising；后验均值与方差及 Tweedie’s formulas 见 §IV-A 式(43)–(45)（p.8）。共享标量方差与白 Gaussian 输入模型见 §III-A 式(7)–(8)、§III-B 式(20)、§IV-A 式(43)。大系统与 right-rotationally invariant pilot matrix 条件、偏离条件的数值问题及其采用的 damping 见 §V-B1（p.9）。末两句是对白误差模型忽略输入误差相关性的分析，不是否定该论文学习物理信道相关性或联合更新活动概率的能力；本段没有宣称普遍性能退化或实测运行时间差异。


## 2026-10-27：保存作者确认的贡献引入段

将以 Against the above background 开头的第七段按作者确认文本追加至现行英文引言，同步工作区 TeX 与阅读稿；前六段和 old 文件保持不变。三条贡献仍在聊天中起草，未写入正文；未编译。

Against the above background 的过渡句式见 Ding §I 贡献引入；multi-frame transmission scheme、large differential delay and Doppler shift 见 Shen §I 贡献引入及第一条贡献（PDF p.2），本稿相应 AFDM 设计见 §II。message-passing algorithm、score-based generative channel priors 和 JADCE 见 Cai §I-A（PDF p.2）；此处将既有术语用于概括本文方法，并非声称该整句出自单篇文献。


## 2026-10-27：保存确认后的第六段与三条贡献

按作者确认版本替换第六段并加入三条 enumerate 贡献；前五段、贡献引入段和 old 文件保留。英文阅读稿此前缺少已确认的第七段，本次与现行 TeX 同步补齐。章节安排仍为本轮聊天草稿，未加入正文；未编译。

第六段：single-step MMSE denoising、first- and second-order score networks、Tweedie’s formulas 依据 Cai §I-A、§IV-A–C（PDF pp.2、8–9）；白 Gaussian 扰动训练见 §IV-B/C；denoiser input error 及相关误差动机见 Shastri 摘要、§III-A/B（PDF pp.1、11、15–16）。Cai §III-B 式(24)–(30)以 Gaussian extrinsic messages 计算活动概率。末句指出这种近似可能造成相对所学非 Gaussian 先验的活动似然比误差，属于根据更新公式作出的分析，不是原论文报告的实测退化。

贡献一：multi-frame transmission scheme / input–output relationship 见 Shen §I 第一条贡献（PDF p.2），AFDM effective channel / fractional delay–Doppler 见 Huang 摘要与 §II-B；本文具体长时延前缀相位、帧间相位分离与 MMV 关系见 §II 的 cpp、integer-prefix-phase、twc-frame-channel、effective-pilot 和 mmv-indexing。共享信道与估计维数不随导频帧数增加依据本文块内固定信道模型。

贡献二：score-based generative channel prior 见 Cai §I-A，AFDM effective channel 见 Huang 摘要；colored Gaussian noise / denoiser input error 及按噪声统计条件训练见 Shastri §III-A/B。本文协方差条件与有色训练见 §IV-A/D。本条限定为训练分布扩展，没有声称在线跟踪实际完整误差协方差。

贡献三：posterior mean and variance / conditional mean / second-order score network 见 Cai §III–IV；条件均值导数与条件协方差的数学依据见 Dytso Proposition 1、式(22)（PDF p.5），本文实现见 §IV-B。density ratio estimator 见 Menon–Ong §4.2 式(17)，本文分类训练和先验修正见 §IV-C。soft information / linear estimation module / extrinsic message 见 Shen 摘要与 §III、Cai §I-A与 §III。本条对应学习密度比及均值导数求方差，不将既有活动概率与条件信道矩的组合本身宣称为新增原理。

## 2026-10-27：C-STMP先估计相位再固定推断的小样本接入

本轮独立候选沿用本文件2026-10-15未知跨帧相位条目中的既有前端。variable projection / 变量投影、separable nonlinear least squares / 可分离非线性最小二乘的出处仍为O’Leary–Rust，§1式(2)–(3)、§2式(5)–(7)，作者稿pp.2、4–5。单主导路径拟合和两轮逐用户搜索为已有项目适配，不新增算法名称，不称为Shen EM或STMP内部联合相位更新。只将观测所得相位交给当前C-STMP；权重、阻尼和停止规则不变。独立协议见[C-STMP相位小样本验证](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/C_STMP_PHASE_PROBE_20261027.md)，结果以`result/candidates/c_stmp_phase_snr_probe_20261027/`中的记录为准。该条不改变共用相位定义或现有稿件正文。


## 2026-10-27：保存确认的章节安排并核对完整引言

按作者确认文本加入章节安排，现为八个正文段落与三条贡献；此前七段、三条贡献及 old 文件未变。章节编号依 main.tex 的有效输入顺序：II 系统模型与多帧输入输出，III 接收机设计，IV 信道和活动去噪器，V 总体算法及复杂度，VI 仿真结果。TeX 使用对应章节标签引用；英文阅读稿使用 II、III–V、VI。技术措辞沿用已记录术语及各节现行标题，无新增方法或性能主张。全文与英文阅读稿逐段核对一致，未编译。


## 2026-10-27：按作者要求仅保留确认后的英文引言

删除本稿旧引言、旧中文引言及引言修订备份和差异文件，当前 sections/01_introduction.tex 原字节保留。同步清理本聊天工作区的旧稿、分段草稿和旧替换包，最终引言保留八段正文及三条贡献，工作区仅保留对应 TeX 定稿。README 的引言入口改为现行英文源文件。文献原文、其他稿件、算法、实验结果及主论文文件不变；未编译。删除清单和文件哈希核验记录保存在本聊天工作区。

## 2026-10-27：在贡献引入段明确两项接收机设计

按作者确认，将贡献引入段的泛称 incorporates score-based generative channel priors 替换为 combines a channel denoiser trained with colored Gaussian perturbations with a learned density-ratio estimator for activity detection，前面的多帧AFDM总述保留。colored Gaussian noise / channel denoiser 的术语及训练动机沿用 Shastri §III-A/B 与本稿 §IV-A/D；density ratio estimator 沿用 Menon–Ong §4.2 式(17)，本稿 §IV-C 说明分类训练与先验修正。activity detection 沿用 Cai §I/III。该句说明训练分布与活动估计机制，不表示在线跟踪完整误差协方差。其余引言正文与三条贡献未变；实验总结句仍在聊天中讨论，未加入正文。同步工作区TeX，未重新编译。

## 2026-10-27：在第三条贡献末尾加入作者确认的实验总结

按作者确认追加 Simulation results demonstrate that the proposed receiver improves activity detection and channel estimation performance compared with STMP across different signal-to-noise ratios and device activity levels. 贡献引入段与三条贡献的既有内容不变。概括依据为本稿第VI节 Effect of SNR 和 Effect of Activity Probability；术语 activity detection、channel estimation、signal-to-noise ratios、device activity levels 沿用 Cai §I-A/VI-C。总结针对已报告的整体接收机比较，不把收益归因于单一模块，也未加入导频帧数或运行时间主张。同步工作区TeX；未重新编译。

## 2026-10-27：落实作者确认的四处引言细节修改

第六段首次介绍Cai方法时补出 score-based turbo message passing (STMP)，依据Cai §I及§I-A（arXiv:2506.00581v2）；第四段和贡献引入段统一使用作者指定的 AFDM-GFRA，规范连接号两侧不留空格。第三段结尾删除 reliable，并将 channel diversity 改为 full diversity，与前句及Bemani相关分集讨论保持一致。第二条贡献末句按确认版本压缩为 The denoiser is trained with colored Gaussian perturbations and conditioned on their covariance to account for correlations in the denoiser input error. 技术依据沿用本稿§IV-A/D与既有Shastri术语记录。除此之外正文、贡献内容和实验总结不变；已同步工作区TeX，未重新编译。


## 2026-10-28：在第三条贡献中明确结构化观测模型与接收机设计的联系

按作者确认，仅修改第三条贡献开头：We develop a message-passing JADCE receiver for the structured multi-frame AFDM observation model, incorporating the channel denoiser trained with colored Gaussian noise to account for correlated denoiser input errors. 原有后验矩求取句改由 The receiver obtains 承接；其余内容保留。第六段仍概括白噪声训练与相关输入误差、Gaussian extrinsic messages 下活动似然近似两项问题，不提前展开本文导频矩阵。

structured multi-frame AFDM observation model 是对本稿 §II effective-pilot、MMV 模型的描述，不是引用文献中的固定方法名称。论证位置参考 Wei–Yuan（arXiv:2610.17785v1）§I、§III-A（PDF pp.1–2）对 structured beam-selection designs、有限维 compression matrices 与 AWGN denoiser input 的讨论；未将该文加入参考文献，也不移植其 deep unfolding 方案。colored Gaussian noise 与 denoiser input error 沿用 Shastri §III-A/B（PDF pp.11、15–16），对应本稿 §IV-A/D 的有色噪声训练。该句陈述训练动机，不增加在线完整误差协方差跟踪或精确白化主张。源稿与工作区 TeX 已同步，未重新编译。

## 2026-10-28：C-STMP 迭代内相位更新的小样本接入

沿用 [PHASE_MESSAGE_GEM.md](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/PHASE_MESSAGE_GEM.md) 的 Gaussian conditional moments 与 generalized EM：GPML §2.1.1 式(2.6)–(2.8)、p.9；Shen §III-C 式(48)–(53) 的期望二次型；Dempster 等 §3、印刷p.7、式(3.5)及 Theorem 1。这里只在固定的实际高斯反馈消息下使用该性质，不声称神经迭代全局收敛。全部用户的候选相位检查沿用 STMP 已有局部分类器证据规则，明确是项目近似操作，不将其包装成新的已发表方法或完整广义EM步骤。

本轮固定前端与迭代内更新采用相同的物理相位初值；前端的 variable projection 来源沿用本文件2026-10-15和2026-10-27条目。C-STMP查询方差更新、导数方差及密度比分类器沿用既有对应条目；相位变化后的重新计算查询与方差比值重置是接入实现选择，不增加方法名称。协议见 [C_STMP_ITERATIVE_PHASE_PROBE_20261028.md](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/C_STMP_ITERATIVE_PHASE_PROBE_20261028.md)。不修改共用相位定义、STMP/DU冻结实现或论文正文。


## 2026-10-28：明确第一条贡献中的跨帧信道关系

按作者确认，将 shared effective channel 所在句替换为此前聊天确认的两句：Separating the phase evolution across frames yields a multiple measurement vector (MMV) model in which the effective channel of each device remains approximately constant over consecutive frames. Additional pilot frames therefore provide more observations without increasing the number of channel coefficients to be estimated.

remains approximately constant over consecutive frames 的表达参考 Shen 式(13)–(15)附近对连续帧信道的讨论；本文对应 §II 的帧间相位分离式 eq:twc-frame-channel、有效导频式 eq:effective-pilot 和 MMV 式 eq:mmv。这里描述同一设备在连续帧中的有效信道系数，避免 shared 未指明共享维度的歧义。仅修改第一条贡献末尾这一处，摘要与其余引言原字节保留；同步工作区 TeX，未重新编译。

## 2026-10-28：区分引言中的近似误差分析与本文贡献

按作者确认，第六段说明 STMP 的近似及其可能影响，贡献引入段压缩为研究对象与贡献列表的过渡，第三条贡献仅保留信道后验矩、学习的密度比与软活动概率、线性模块之间的迭代信息交换。删除本文接收机采用条件均值导数及无需单独二阶 score 网络的引言描述，相关计算仍在第 IV-B 节说明。摘要、前五段及前两条贡献保留。

- equivalent additive white Gaussian noise observations、posterior mean and variance：Cai（arXiv:2506.00581v2）§III-B1 式(20)–(23)、§IV-A 式(43)–(45)。输入误差未必白化的动机沿用 Shastri §III-A/B（PDF pp.11、15–16）和既有记录；针对本稿结构化 AFDM 观测的影响是理论上可能存在的失配，保留 need not、potentially、can，不写成已完成的误差相关性或因果实验结论。
- Gaussian projection、Gaussian extrinsic messages：Cai §III-B1 式(17)、(24)–(27)；基于这些消息的活动概率见 §III-B2 式(28)–(30)。marginal likelihood 对应 §III-B1 式(18)–(19)后的归一化常数 Z_k。匹配后验均值与方差通常不保留原边缘似然，是对这些近似步骤的数学分析，不归为 Cai 原文宣称的缺陷。
- activity-weighted channel estimates 是对 Cai §III-B3 式(35)及本稿 eq:exact-local-moments 中活动概率乘条件信道均值这一操作的直接描述，不是新增方法名称。后续线性模块的信息交换沿用两稿既有 MP 定义。
- density-ratio estimator 与二分类的依据仍为 Menon–Ong（2016）§3 式(6)–(8)、§4.2 式(16)–(17)；本稿相应关系见第 IV-C 节。第三条贡献未增加在线完整协方差跟踪、精确后验恢复或单组件性能归因的主张。

本轮只调整本稿引言表述，未变更共用技术定义；未重新编译 PDF。

## 2026-10-28：在第六段补充 AWGN 近似条件及结构化观测失配

按作者确认，第六段明确 STMP 等效 AWGN 模型依赖的大系统渐近条件与随机感知矩阵的右旋转不变性，并将本文有限维、结构化多帧 AFDM 观测与失配可能加剧的关系直接写出。影响统一表述为 channel denoising accuracy 和后续 JADCE performance，不再将信道估计任务与内部方差更新操作并列。活动概率的高斯近似讨论保留。

- large-system limit、right-rotationally invariant random sensing matrices：Cai（arXiv:2506.00581v2）§V-B1（PDF p.9，式(57)之前）明确给出 pseudo AWGN 模型的适用条件，并讨论有限维度、具体矩阵选择与阻尼处理。这里将其原有 Q 对应到一般 sensing matrix 表述，不将这项限制归为本文首次发现。
- finite-dimensional、structured compression matrices 及 AWGN 失配：Wei–Yuan，Learned Score-Based Turbo Message Passing for Channel Recovery From Spatially Compressed Measurements，arXiv:2610.17785v1，§I（PDF p.1）、§III-A（p.2）；PMI 选择下的具体矩阵限制及性能讨论见 §IV-B、§V-B（pp.3、5）。本稿 references.bib 新增 wei2026，按预印本引用。
- 本文 structured multi-frame AFDM system 对应 §II 的导频、帧间相位及有效观测矩阵。can exacerbate 是将上述机制联系到本稿模型的论述，不表示新增了跨论文失配强度实验或确定性的严重程度排序。channel denoising accuracy、JADCE performance 沿用 Cai §III-B、§VI 的任务和性能表述。

仅修改第六段及所需引文记录；摘要和其他引言段落保留，未重新编译 PDF。

## 2026-10-28：摘要与引言的轻度语言润色

按作者要求，仅调整英文表达：拆开摘要中先验学习与有色训练的长句，压缩重复连接语，优化 handshaking、score function evaluations 和活动概率误差的搭配，并简化第一条贡献的句式。保留引言段落顺序、三项贡献、Cai/Wei 的适用条件与失配论述、全部引用及结果主张。can、approximately、in general 等限定的含义不变；未增加技术方法或实验结论。

专业表述沿用上述术语来源：high-dimensional integrals、posterior moments、activity probabilities 见 Cai §III-B；score function evaluations 对应 Huang §III-B 与 Ying §V 的重复得分计算。其余调整为语法或衔接，不变更技术定义。中文摘要与润色后的英文含义保持对应，因此本轮不重新生成中文摘要；未重新编译 PDF。

**2026-11-03 更正：** 上段将 posterior moments 一并归于 Cai 的写法不够准确。Cai 正式版 PDF p.6 III-B1 确有 matched first- and second-order moments，但未检出 posterior moments 这一完整搭配；后者的直接用例见 Manor–Michaeli §3.2/Theorem 2。当前稿件采用具体的 mean and variance/covariance，不能用其他领域存在该搭配为本文保留它作理由。

## 2026-10-28：完善第二章的模型叙述与推断接口

按作者要求，对照文献完善第二章。将原 Transmission Scheme 中的多帧接收关系独立为 Multi-Frame Received Signal Model，小节标题只是内容描述；原有公式及标签保持不变。补充静止地面终端、路径索引、归一化超额时延、阵列单位轴、DAFT全称、啁啾参数、归一化时间及导频索引定义。文献的通用术语和句式按本稿变量与条件适配，不将适配后的句子登记为逐字原文。

| 表述 | 原文定位及本稿使用 |
|---|---|
| common delay、differential delay、multi-frame transmission、phase rotation | Shen，arXiv:2412.20806v1，§II开头与§II-A式(1)，PDF p.3；§II-B式(7)–(10)，pp.4–5。用于共同参考、残余偏移及块内近似；本文圆轨道变化界限为自身几何推导，未归为Shen的数值结果。 |
| stationary ground user、common Doppler | Huang，§II式(2)及后文，印刷p.2950。当前几何模型只保留卫星运动产生的Doppler；明确静止终端，避免省略该条件。 |
| array response vector、common spatial direction | Li–Gao–Xia，arXiv:2207.11958v2，§II-B式(3)前，PDF p.4；§II-C式(8)，p.5。用于同终端各路径共同空间响应与空间秩一结构；本稿继续采用阵列响应范数平方为M的约定。 |
| discrete affine Fourier transform、chirp-periodic prefix、chirp periodicity | Bemani，arXiv:2204.12798v2，§II-B式(11)–(17)，PDF pp.7–8；§III-A式(19)，p.8。该版共30页，§III-B p.9采用最大离散时延小于N；本文多周期CPP和完整长时延相位是由啁啾周期关系作出的扩展，不能当作原文现成的长时延模型。 |
| fractional delay、fractional Doppler、frequency wrapping、effective channel | Huang，§II式(4)–(5)，印刷p.2950；Bemani §II-B式(13)，PDF p.7。本文显式保留采样点之间的基函数定义，不能仅由整数IDAFT样本唯一确定分数时延响应。 |
| posterior、MMSE estimate、Bernoulli activity prior | 沿用本稿既有Cai §II–III的活动与信道推断关系；保持本文确定性约束X_k=alpha_k H_k及原后验测度表达。 |

相位接口统一为由可用相位构造A_c，未知时由既有附录初始化；后续算法记号widehat A=A_c。噪声采用观测估计并在消息迭代内固定。明确第VI章接收机比较使用已知跨帧相位，删除旧稿关于training使用真实A、sigma的分支；当前第IV章为独立信道及活动去噪器训练。保留非空活动抽样的边缘概率rho及推断时的独立边缘近似，未改动模型或实验设置。

独立只读核验包括连续路径展开、整数长时延极限、跨帧相位分离及MMV重排，小规模双精度检查最大绝对误差分别为2.06e-11、1.52e-11、3.39e-13、1.08e-14；原11.73 ms示例的变化界限与计算一致。这些检查用于代数与索引核验，不代表新增性能实验。未训练、未运行批量实验、未重新编译PDF。

## 2026-10-28：按Cai与Shen的论证方式重排第二章

作者指出上一轮仍偏向模型和实现说明。本轮直接对照Shen §II-A末至§II-B式(7)–(10)、§II-C式(15)（arXiv:2412.20806v1，PDF pp.4–5）以及Cai §II-A/B（正式刊印pp.3578–3579），调整段落任务：完整有效信道表示与单帧观测数引出多帧传输；公共路径Doppler引出跨帧相位分离；堆叠观测后明确未知信道维数不随Q增加；从JADCE目标、先验分解和后验计算困难引出消息传递与学习去噪器。沿用两文的论证顺序和通用技术表述，未逐段复制其原文，也未将Shen的OTFS适用条件移植为AFDM的证明。

新增时变冲激响应eq:physical-channel是将既有共同空间响应、共同Doppler和各路径时延/增益写成一个物理信道表达式。time-varying impulse response、path gain与Dirac delta对应Shen §II-A式(1)（PDF p.3）的多径叠加，并采用本稿既定复包络约定；该式与原G=F_A D B一致，不改变信号生成模型。主文的N²系数与N观测之比描述完整矩阵表示的估计规模，不声称有N²个独立物理参数，也不声称任何先验下单帧均不可恢复。

原RF符号说明、连续基函数、元素展开、整数长时延极限及轨道变化界限移入新增附录Details of the AFDM Channel Model，放在现前端附录之后。原公式和标签全部保留。导频构造移至传输小节；有效导频一般失去行正交性的说明移至III-B；归一化完整操作归入V-A；非空活动抽样与SNR定义归入VI-A。II保留边缘先验近似和归一化坐标引用。VI的Channels remain fixed相应明确为path parameters remain fixed，保留Doppler相位随时间演化。以上为正文重排和语义澄清，不改变算法、数据、训练配置或实验结果。未重新编译PDF。

## 2026-10-28：按模型推导所需粒度精简第二章

作者指出第二章仍像实现说明书。本轮以研究问题的定义和推导为取舍依据，保留物理信道、AFDM与CPP、多帧相位关系、MMV观测及贝叶斯目标；删除轨道坐标与路径时延生成式、天线绝对坐标、重复解释、独立编号的数组索引、第二章的归一化和参数估计接口。具体DFT导频构造移入VI-A；附录B仅保留分数时延波形、有效矩阵展开与整数长时延关系，删去复包络约定及轨道变化上界。此前条目中的位置和“原公式全部保留”描述属于上一轮状态，以本条为准。

- 粒度依据：Cai §II-A，正式刊印p.3578，式(3)–(4)，只定义导频与观测结构，具体导频设计置于§V-C；§II-B，pp.3578–3579，式(5)，从后验分解进入先验刻画及高维边缘化困难。Shen §II-A式(1)，PDF p.3，直接定义多径信道和方向余弦；§II-B–C，pp.4–5，式(8)–(16)，围绕跨帧有效信道、联合观测和估计目标展开。Shen对块内近似有效性的讨论确实存在，不能据此声称顶刊不写适用条件；本稿保留该建模假设，删去不参与后续推导的界限说明。
- 既有术语来源不变：共同Doppler与方向、DAFT、CPP、分数时延及有效信道沿用前两条的Huang、Li、Bemani与Shen定位；未增加方法名称。UPA式为原表达式的代数简写，长CPP仍使用完整时延相位。
- 后验仍采用分布记号$q_{\rm tr}(dH)$，不额外假定全维信道密度存在。第二章省略固定$A,\sigma^2$的条件记号，删除仅用于接口说明的$A_{\rm c},\sigma_{\rm c}^2$；第三章明确将观测参数估计值代入该似然。MMSE信道均值和活动后验概率保留，判决门限在算法部分说明。

本轮未改变物理模型、接收算法、训练或实验结果。正文与附录引用已同步；未重新编译PDF。

## 2026-10-28：重写第二章的公式组织与解释

作者再次指出精简稿仍像说明书。本轮纠正将问题主要归因于篇幅的处理：Shen §II-B（PDF pp.4–5）保留调制、传播和解调式(2)–(7)，并在命题1式(8)–(10)后分析信道维度、适用条件与跨帧共享；Cai §II-B（印刷pp.3578–3579）由式(5)定位信道先验因子的表征和消息积分困难。本文按这些具体段落的作用重写，未移植Shen的OTFS适用条件。

第二章改为Terrestrial-Satellite Link Model、Multi-Frame AFDM Transmission、Problem Formulation三个小节。合并传输与输入输出叙述；正文直接以参考信道张量H_k及跨帧关系H_k^(q)=exp(jq beta_k)H_k说明增加观测的依据，并从MMV式读出活动块稀疏与块内系数依赖。原G=F_A D B的组装及物理路径到H_k的表达移至附录B，补充由帧起点g_q得到共同相位因子的推导；前端附录增加对该路径矩阵的引用，原前端公式保持不变。此处张量相位关系与原G_k矩阵相位关系等价。

后验采用Cai §II-B式(5)的因子分解写法，正文保留Gaussian likelihood、确定性约束X_k=alpha_k H_k、channel prior和Bernoulli activity prior的含义。q_tr(H_k)在此表示先验分布因子，与后续积分中的q_tr(dH_k)是同一分布；这是因子图的简写，不增加全维Lebesgue密度存在的假设。末段直接说明该信道因子的解析表征与高维积分困难，不再展开接收机接口。新小节标题均为内容描述，未引入方法名称。

本轮只调整论文叙述及必要的附录衔接，未修改算法、模型参数或实验结果；未重新编译PDF。

## 2026-10-29：落实第二章的原文用语与句式依据

按作者“能复用参考文献原句的就复用”的要求，逐段对照原文修改 `sections/02_system_model.tex`。本轮以措辞为主，保留三个小节和全部十个编号公式。来源分为原句沿用、依原文适配、本文模型表述；不能把后二者称为逐字摘取，也不以引用替代模型适用性核对。

| 本文位置 | 原文定位 | 本轮处理与适配范围 |
|---|---|---|
| 章首：系统场景、共享资源及无终端预补偿 | Shen，§II开头，作者稿PDF p.3；Cai，§II-A，印刷pp.3577–3578 | 依原文适配：使用上行、单天线终端、卫星UPA及共享资源的常规表述；本文传输对象明确为导频。 |
| 章首：共同延时的定义句 | Shen，§II-A，式(1)之后，PDF p.3 | **原句沿用**：正文以 The common delay 开头的完整定义句，21词，保留原词序，仅将引用换为本稿文献键。共同延时的补偿操作仍按本文模型表述。 |
| 章首：活动指示量与活动概率 | Cai，§II-A式(1)，印刷p.3578 | 依原文适配：沿用活动指示量和概率的定义方式；符号和块内活动不变假设采用本文约定。 |
| II-A首段：双弥散信道 | Shen，§II-A开头，PDF p.3 | 依原文适配：由卫星移动和多径传播引出 doubly dispersive terrestrial-satellite channel，再引出物理信道式；不是从OTFS条件推断AFDM限制。 |
| II-A首段：共同Doppler假设 | Huang，§II式(2)及紧随段落，印刷p.2950 | 依原文适配：保留静止地面终端和同链路各路径共同卫星Doppler两个条件；将原来的直接断言改为建模假设。 |
| II-A首段与UPA式前：到达角和阵列响应 | Li–Gao–Xia，arXiv:2207.11958v2，§II-B式(2)–(3)附近，PDF pp.3–4；Shen §II-A式(1)，p.3 | 依原文适配：沿用 angles of arrival、array response vector、directional cosines；共同方向取近似，本稿阵列响应的范数平方仍为M。 |
| II-A末段：块内参数及时间演化 | Shen，§II-B式(8)–(10)附近，PDF pp.4–5；本文式eq:physical-channel | 本文模型表述：物理路径参数块内近似固定，时间变化保留共同Doppler相位。此句不是原文摘录。 |
| II-B首段：连续多帧与联合处理 | Shen，§II-B首段，PDF p.4 | 依原文适配：保留逐帧调制、解调和联合处理的叙述顺序；OTFS数据扩频改为本文AFDM导频，未移用其符号构造。 |
| II-B：IDAFT调制与CPP引导语 | Bemani，arXiv:2204.12798v2，§II-B式(11)–(17)，PDF pp.7–8；§III-A式(18)–(19)，p.8 | 依原文适配：使用时域映射、CPP及chirp periodicity的既有用语；超过一个有用符号时长的CPP仍是本文关系式及附录B的扩展，不归为原文已有结论。 |
| II-B：有效信道中的能量泄漏 | Huang，§II式(5)后的段落，印刷p.2950 | 依原文适配：将原来的泛称spread path energy改为energy leakage；保留分数时延与分数Doppler两项来源。完整矩阵表示是本文选择，不表示各系数独立。 |
| II-B：跨帧关系、参考信道与MMV堆叠 | Shen，§II-B式(8)–(10)、§II-C式(13)–(15)，PDF pp.4–5；本文式eq:twc-frame-channel、eq:mmv | 参考原文的论证方式；共同相位因子及堆叠维度为本文模型表述。仅在分离相位后描述参考信道不变。 |
| II-B末段：块稀疏性第一句 | Cai，§II-A式(4)之后，印刷p.3578 | **原句沿用**：正文以 Due to the sporadic access 开头的完整句子，14词（含矩阵符号X），仅增加引用并调整数学排版。后续N行同时为零的解释为维度适配；块内统计依赖为本文模型表述。 |
| II-C：联合检测估计目标与后验分解 | Cai，§II-B开头及式(5)，印刷p.3578 | 依原文适配：使用Bayesian inference framework、Bayes' theorem与joint posterior distribution等既有用语；保留本文终端独立先验、块内联合分布、固定A及噪声方差的条件。 |
| II-C末段：先验表征与后验计算两项困难 | Cai，§II-B两项困难及其后承接段，印刷p.3579 | 依原文适配：先说明共同物理参数造成的联合分布刻画困难，再说明解析先验可得时仍存在高维积分；以学习先验和去噪器消息计算承接。没有将Cai的总结句逐字搬入，也未新增无需积分或精确推断的主张。 |

原文核对入口：`reference/reviews/section_structure_20261009/cai.txt`、`reference/reviews/section_structure_20261009/shen.txt`、`paper/checks/abstract_sources_20261026/huang2026.txt`；Li与Bemani采用上述arXiv版本。原句沿用共两处，其余为有来源的适配或本文模型自身的说明，不能据此宣称第二章基本由参考文献原句组成。未修改摘要、引言、公式、算法或实验设置，未重新编译PDF。

核验：十个编号公式逐项一致；有效主文件及其输入文件无重复标签、缺失引用或未定义文献键，环境和括号检查通过。除第二章外，已核对的稿件TeX、参考文献及PDF哈希保持不变。缩写检查基于临时去除TeX命令的引言与第二章文本，下列行号仅对应检查文本；四项覆盖限制已人工核对其全称，不把部分覆盖报告称为完整通过。检查临时文件已清除。

```text
### Acronym check (advisory; no reply needed)
Coverage: body (partial)
Not checked:
- Body, line 9: IoT (the initials before its parentheses do not spell it)
- Body, line 18: GFRA (the initials before its parentheses do not spell it)
- Body, line 79: MMSE (the initials before its parentheses do not spell it)
- Body, line 207: CPP (the initials before its parentheses do not spell it)
No findings.
```

## 2026-10-29：补齐第二章的论证衔接与有效信道结构

按作者确认的比较意见，保留现有三个小节，修改第二章与附录B的衔接。此次不再按原句复用比例或篇幅判断质量，重点使模型定义、结构结果及推断困难相互对应。

- **多帧传输的目的。** 在II-B开头提前说明利用连续帧关系获得更多信道观测。论证顺序参考Shen §II-A末、§II-B式(8)–(10)附近（作者稿PDF pp.4–5）；仍由本文共同Doppler模型和跨帧相位式支撑，未移用OTFS维度或underspread条件，也未宣称单帧必然不可恢复。删除II-A末尾未提供额外信息的跨帧关系过渡语。
- **有效信道结构。** 将eq:channel从附录B原样移回II-B，正文解释参考帧中单位增益路径的有效矩阵G(d,nu;N_CPP)，并在块内统计依赖的说明中引用该式。参照Shen正文保留有效信道结构式(9)、(12)，附录承担证明的取舍（PDF pp.4–5）。本文单路径矩阵的具体形式及分数时延推导仍留在附录B；unit-gain指路径增益已由外部g_kl单独计入，是原路径叠加式的解释，没有引入新模型或新方法名称。
- **推断先验。** 明确推断时的跨终端独立性、每个终端活动与信道之间的独立性，以及Bernoulli活动先验；同时保留单个H_k内部的统计依赖。术语与因子分解依据Cai §II-A式(1)、§II-B式(5)，印刷pp.3578–3579。这里说明接收机的先验分解，不改变VI-A中非空活动抽样及独立Bernoulli推断近似的既有实验说明。
- **消息传递与学习去噪器的联系。** II-C末段先由后验因子分解引出后验统计量的近似计算，再定位涉及q_tr(H_k)的消息更新；分别说明简化解析先验可能遗漏实际联合统计，以及即使准确解析先验可得，相关消息通常仍涉及高维边缘化。依据Cai §II-B式(5)前后及两项困难（印刷pp.3578–3579）。末句将样本学习的统计量与去噪器明确用于信道先验相关更新，没有将全部接收机计算归给去噪器，也不再将“相关性”本身写成无法解析的充分理由。
- **措辞来源分类更新。** 块稀疏句中的devices统一为terminals；因此上一条记录中该句的“原句沿用”在现版本改为词语适配。共同延时定义句仍逐字沿用Shen。本轮其余新增或改写语句均为依据原文论证方式的适配，不登记为原句。

核验：两个修改TeX文件中的编号公式内容集合完全一致，eq:channel仅改变位置；第二章现有11个编号公式。主文与附录A/B中的标签及交叉引用均有效，无重复标签或缺失文献键，环境和括号检查通过。除第二章与附录B外，已核对的稿件TeX、参考文献及PDF哈希不变。未重新编译PDF，未运行实验或训练。

以下为临时去除TeX命令后的引言及第二章缩写检查原始报告，行号对应临时文本；四项覆盖限制沿用人工核对，不能将其称为完整自动通过。临时文件已清除。

```text
### Acronym check (advisory; no reply needed)
Coverage: body (partial)
Not checked:
- Body, line 9: IoT (the initials before its parentheses do not spell it)
- Body, line 18: GFRA (the initials before its parentheses do not spell it)
- Body, line 79: MMSE (the initials before its parentheses do not spell it)
- Body, line 209: CPP (the initials before its parentheses do not spell it)
No findings.
```

## 2026-10-29：按Shen组织第二章总述段

作者选择按Shen组织总述。本轮只重写第二章开头，并迁移两处已有定义：场景与AFDM、终端及卫星UPA、共享导频资源、无GNSS与无逐终端预补偿、共同传播时延补偿后的差分时延和Doppler。依据Shen §II总述（作者稿PDF p.3），将其OTFS场景适配为本文AFDM导频接入；没有引入该文的固定波束、再生载荷或广播共同延时机制。本文仍采用既定的卫星端共同延时补偿。

共同延时的几何定义原样移至II-A中残余路径时延的说明后，对应Shen §II-A式(1)之后（PDF p.3）。活动指示量alpha_k、概率rho与块内活动不变的三项说明原样移至接收观测模型中X_k=alpha_k H_k之前，参照Shen在§II-C接收模型处引入活动变量的安排（PDF p.5）；本文概率与块内假设保持原意。总述新增句均属依原文组织的适配，几何定义句仍为此前记录的原句沿用。

第二章11个编号公式逐项不变，已核对的其余稿件TeX、参考文献及PDF哈希不变；未重新编译。下面是引言与第二章临时去格式文本的缩写检查原始报告，部分覆盖的四项已沿用人工核对；行号仅对应临时文本，临时文件已清除。

```text
### Acronym check (advisory; no reply needed)
Coverage: body (partial)
Not checked:
- Body, line 9: IoT (the initials before its parentheses do not spell it)
- Body, line 18: GFRA (the initials before its parentheses do not spell it)
- Body, line 79: MMSE (the initials before its parentheses do not spell it)
- Body, line 211: CPP (the initials before its parentheses do not spell it)
No findings.
```


## 2026-10-29：按作者确认对照核心论文细修第二章

依据作者本轮指示，保持 II-A/B/C 结构，补充接入块起点的导频发送时间对齐、残余时延定义、路径算子紧凑式、MMV索引及导频行正交条件，并将物理参数估计与条件后验衔接。未修改接收机、导频构造、训练先验实现或实验；摘要、引言、第三章、附录B、参考文献与PDF保留。第二章编号公式由11个增加为13个；不重新编译。

术语和句式依据：Cai §II-A式(1)之前（期刊pp.3577–3578）的 synchronized 与 pilot transmission，用于明确本文导频在接入块起点的发送时序；本文仍保留传播导致的到达差分时延，不导入已预补偿的同步接收假设。Shen §II-A式(1)之后（作者稿p.3）的 differential delay / propagation delay / common delay 支持 tau=tilde(tau)-tau_c；§II-B式(10)–(15)附近（pp.4–5）的 remains approximately constant / phase rotation 支持多帧衔接和相位措辞，不把 common phase 作为独立术语。Huang §II式(4)后及式(5)后（p.2950）明确使用 effective channel matrix 和 power leakage；同页 Doppler shift 段支持各路径公共卫星诱导Doppler。Li §II-B的 array response vector 及各路径AoA近似一致仍沿用已有模型。

Ding §II式(1)–(2)（作者稿p.2）的 inverse discrete affine Fourier transform (IDAFT) 用于更正缩写。删除 per-frame energy 名称，直接限定为N个导频符号的能量，避免把CPP能量混入原有归一化。Bemani §III-A式(18)–(19)为IDAFT与chirp-periodic prefix的来源；跨多个有效符号周期、分数时延及其相位仍由本文附录B给出，不归为Bemani原结论。正文新式 eq:path-operator-system 复用本文附录B的G=F_A D B算子与定义，无新算法名称。

Cai §II-A式(4)之后的partial orthogonal、pilot design deferred to later section，以及其矩阵排列方式支持导频行正交与显式索引的组织；本文P的具体维数和P P^H=K E_p I来自第VI-A节既有DFT构造。Cai §IV的channel samples / training samples支持q_tr说明；Shen §III-B关于先给定phase rotation、noise variance再求消息的组织用于本文条件推断衔接，实际前端仍为既有第III-A节。所有新增专业表述均为已有术语或对本文公式的直接说明，未宣称整句逐字摘自文献。

## 2026-10-29：按作者确认统一第二章用词

本次依照作者在聊天中确认的逐项核查结果修改第二章。此前关于导频发送同步的新增声明已按作者要求删除，不再用Cai的同步假设解释本文。先前“术语均已核对”的概括不够准确：可解释的描述性组合不等于已核实的原文术语。此次保留全部13个编号公式及其标签，只调整已讨论的措辞。

- transmission block：Cai §II-A使用的原词，替换本章6处access block，不引入其块衰落或同步假设。pilot transmission同样见该节，保留。
- differential delay：Shen §II-A式(1)后对tau=tilde(tau)-tau_c的名称，统一本章4处原residual delay(s)/residual propagation delays。Ding §V-A虽有residual delay，其语境为粗预补偿后的小范围残余，不能仅因同词出现而移植。首段按Shen §II开头使用卫星接收端为主语衔接处理任务；本稿既有公共时延补偿设定保留，不改写为原文的广播机制。
- angles-of-arrival：Li §II-B式(2)后原词，统一此前angles of arrival与arrival directions。time-varying channel impulse response及array response vector也见该节，保留。
- DAFT-domain symbol：Huang §I–II的DAFT-domain symbols / DAFT-domain symbol vector，p.2949–2950。替换DAFT symbol；phi_n直接定义第n个输入符号为1、其余为0，不再用unit symbol或DAFT subcarrier称呼。effective channel matrix、power leakage、chirp parameters均有Huang原文依据，保留。
- posterior probability of activity：Cai §III-B2式(30)后的原词，替换posterior activity probability。末段采用Cai §II-B的channel prior、channel distribution、high-dimensional integrals，以及§V-A的channel denoiser，避免把自行组合的表达登记为原文术语。
- reference frame/reference channel、unit-gain path、useful-symbol duration/useful interval、antenna-symbol pair以及underdetermined regime/block-sparse observation model等辅助描述改用已定义的数学对象：frame 0、H_k、路径增益1、NT_s、去除CPP后N个样本及起点g、列索引mN+r、条件Q<KN。它们是本文变量的直接说明，不声称来自文献同名术语。
- X_k=alpha_k H_k按Cai §II-A式(3)后直接定义，不再重复称为effective channel incorporating terminal activity，避免与H_k的AFDM有效信道名称混淆。

继续保留有原文依据的phase rotation（Shen §II-B）、inter-frame interference（Shen附录A式(65)后）、inverse discrete affine Fourier transform与chirp-periodic prefix（Ding §II、Bemani §III-A）、block-sparsity structure（Cai §II-A式(4)后）。本稿多帧AFDM公式和多周期CPP扩展仍由本文定义及附录支撑，不将其归为参考论文的现成结论。

来源：Cai https://arxiv.org/html/2506.00581v2 ；Shen https://arxiv.org/html/2412.20806v1 ；Ding https://doi.org/10.1109/TVT.2026.3729877 （本地原文）；Huang https://doi.org/10.1109/LWC.2026.3689601 （本地原文）；Li https://arxiv.org/html/2207.11958 ；Bemani https://arxiv.org/html/2204.12798v2 。

## 2026-10-29：按原文句式重写第二章

作者本轮要求：先找到参考论文原句，再做必要的术语和模型替换，保留句式和连接词。本轮直接读取D盘Shen、Cai、Ding、Huang的原文，将第二章主要说明句改为原句适配。正文继续使用编号引用，作者名称仅用于本记录中的来源定位。数学定义与本文独有推导不登记为他文原句。

| 本文位置 | 核实的原句或句式 | 来源与必要替换 |
|---|---|---|
| II总述 | “We consider a LEO satellite-enabled grant-free random access system”; “The system comprises”; “During each time interval”; “Additionally, to minimize energy consumption” | Shen §II开头，PDF p.3。OTFS改为AFDM，U与Na改为K与M，time interval改为本文transmission block，signals改为pilots；删除图示、固定波束和再生载荷。最后一句保留本文卫星端共同传播时延补偿，不移用原文的广播机制。 |
| II-A物理信道引入 | “The TSLs will experience fast variations”; “Hence, this time variation and multipath propagation require a doubly dispersive channel model”; “Then, ... can be represented as” | Shen §II-A，PDF p.3。信道对象替换为本文时变脉冲响应。time-varying channel impulse response另有Li §II-B原词依据。 |
| II-A各路径Doppler与AoA | “Take the ground user as the stationary reference point”; “The resulting Doppler term ... is assumed to be common to all propagation paths within the same ... link”; “As a result of the long distance ... tend to be identical” | 前两句为Huang §II，PDF p.2/期刊p.2950，user改device、D(psi)改nu_k、S2G link改TSL；AoA句来自Li §II-B，UT改device。array response vector同处有来源。 |
| II-A时延定义 | “represents the differential delay for the ... path”; “where ... are denoted as propagation delay and common delay, respectively”; “The common delay corresponds to the propagation time ...” | Shen §II-A式(1)之后，PDF p.3。只替换路径与设备符号；共同延时几何定义沿用。 |
| II-B多帧和导频 | “The ... multi-frame ... transmission scheme is proposed to handle the large differential delay and Doppler shift”; “Specifically, in the ... frame”; “Assume that a total of ... are allocated for pilot transmission” | 前两项来自Shen §II-B，PDF p.4；第三项来自Cai §II-A。替换为本文AFDM、Q帧及导频向量。该句的语言来自Shen，不把本文AFDM方案归为Shen的已发表结果，故不在这一自述句后挂Shen引用。 |
| II-B调制 | “The time-domain transmitted signal is generated through the inverse discrete affine Fourier transform (IDAFT) applied to ... , mathematically formulated as”; “c1 and c2 are AFDM modulation parameters”; “Ts=1/(N Delta f) gives the sampling interval” | Ding §II，PDF p.2。输入改为本文pilot vector；保留本文既有DAFT矩阵与归一化，首次单独使用DAFT时补全全称。 |
| II-B CPP | “Assume that the ... length exceeds the maximum channel delay spread”; “With the periodicity ... , the prefix is” | 分别取Cai §II-A和Bemani §III-A的句式，必要替换为本稿CPP时长与最大差分时延不等式。多周期延拓公式、分数时延采样函数和长时延结论均属本文原定义及附录B，不标作两篇论文的原公式或原结论。 |
| II-B分数时延和Doppler | “To better capture the LEO channel dynamics, we incorporate fractional delay and fractional Doppler effects”; “In practical propagation environments, fractional Doppler shifts and fractional time delays can introduce significant power leakage in the effective channel matrix”; “To address this issue” | Huang §II式(5)附近，PDF p.2/期刊p.2950。信道矩阵对象改为本文H_k；处理方式替换为本稿保留完整N×N矩阵，没有移入Huang的接收算法。 |
| II-B跨帧关系 | “Furthermore, the phase rotation ... caused by ... accumulates across multiple frames”; “remains approximately constant over Q consecutive frames”; “This characteristic allows the proposed scheme to gather more observations, thereby facilitating ...” | Shen §II-B式(9)–(10)附近，PDF p.4。相位替换为本文nu_k和T_frame；H_k跨帧关系由本文式(1)、(7)支撑，末尾目标替换为信道估计。 |
| II-B活动变量及观测 | “We use an indicator function ... to model the device activity”; “Let ... represent the probability of a device being active”; “Let Xk=alpha_k Hk”; “Due to the sporadic access ... block-sparsity structure” | Cai §II-A，v2 PDF pp.3–4，活动概率改rho。特别核实：Cai表I确实将X_k称为effective channel matrix；本稿继续直接定义X_k，以免与AFDM的H_k混用同名对象。 |
| II-B叠加和堆叠 | “According to the superposition principle, the q-th received frame ... is given by”; “Next, we collect the Q received frames into a single matrix as” | Shen §II-C，PDF p.5。域替换为DAFT，矩阵仍采用本文Q×MN排列，不移用Shen的OTFS或数据符号模型。 |
| II-B导频设计 | “For simplicity, we impose the condition that ... is partial orthogonal, specifically requiring that ...”; “The design of partial orthogonal ... is deferred to Section ...” | Cai §II-A式(4)后。约束对象为本稿P，不是含跨帧相位的A；维度、KE_p归一化及后文节号保持本稿已有定义。 |
| II-C任务与后验 | “In this paper, we aim to simultaneously detect the active devices and estimate the corresponding channels ...”; “Exact Bayesian estimators, e.g., the MMSE estimator, are generally intractable ...”; “Alternatively, message-passing algorithms ...”; “In message passing, we factorize the joint posterior distribution according to ...” | Cai §II-B。使用本稿Y、q_tr及原后验因子分解，不移用其同步接收假设。给定前端估计量的引入借用Shen §III-B的“In this subsection, we assume that ... are known, which ...”句式，后半明确本稿III-A的估计来源。 |
| II-C结尾 | “The main difficulty ... lies in the message calculation associated with the factor node ...”; “Generally speaking, even if ...”; “To summarize, the message-passing framework faces a dilemma ...”; “This paper seeks to address the aforementioned challenges by plugging in deep generative priors for efficient message calculation” | Cai §II-B末。保留上述句式与连接词，仅将先验节点替换为q_tr(H_k)，省略其例举和指向原文第三章的括注。 |

必要保留的本文定义：阵列方向余弦及索引、时间原点、参数块内近似不变、导频能量、长CPP条件及延拓、G/D/B/phi_n及样本起点、wrap定义、跨帧关系、X和Y的矩阵索引、q_tr的训练样本含义、推断独立性。这些是对本文数学对象的说明，不宣称逐字摘自参考论文；没有为满足句式而改变数学模型。

核验：第二章13个编号公式及标签逐项不变；有效主文中无重复标签，第二章无缺失交叉引用或文献键，环境配对检查通过。主文件、引言、参考文献和附录B的哈希保持不变。未重新编译PDF，未运行实验或训练。

缩写检查基于临时去除TeX命令与公式的引言及第二章文本；发现DAFT在IDAFT后首次单独使用时未展开，现已补全。以下保留最终报告的部分覆盖限制，不将其称为完整自动通过；临时检查文本已删除。GFRA、IoT、MMSE在引言中的全称，以及TSLs与CPP在本章的全称已人工核对。公式后的两处本文定义仍以原稿“Here”起句，避免句号后接小写where。

```text
### Acronym check (advisory; no reply needed)
Coverage: body (partial)
Not checked:
- Body, line 5: GFRA (the initials before its parentheses do not spell it)
- Body, line 5: IoT (the initials before its parentheses do not spell it)
- Body, line 15: MMSE (the initials before its parentheses do not spell it)
- Body, line 32: TSL (the initials before its parentheses do not spell it)
- Body, line 54: CPP (the initials before its parentheses do not spell it)
No findings.
```


## 2026-10-29 第二章严格原句审查后的实际修订

本次已按用户“必须对照修改”的要求修订第二章并编译。更正此前记录中的过度概括：“有相同术语/句式来源”不等于“整句仅替换必要术语”。上轮严格审查为修订前基线，本次未把它当作修订后通过统计。

Ding（PDF p.2）：系统总述、IDAFT 完整引入及调制参数。Shen（PDF pp.3–5）：资源共享、GNSS/预补偿、物理路径与时延、多帧衔接和堆叠。Cai（PDF pp.4–5）：导频分配、活动变量、接收信号及噪声 where 从句、部分正交导频、贝叶斯推断与完整列向量定义。Huang（PDF pp.2–3）：AFDM 子载波、共用 Doppler 假设、分数时延/Doppler 泄漏及完整信道估计的多导频需求。

本文的长 CPP/路径算子、阵列/矩阵索引、跨帧关系、固定前端参数、q_tr 与工作后验定义仍属必要模型说明，不宣称为参考文献完整原句。没有引入同步、终端预补偿、参数迭代更新等不适用假设。TSLs 首次出现补全为 terrestrial-satellite links (TSLs)。

原 13 个公式标签保留，新增等价标量 IDAFT 公式后为 14 个编号公式。摘要、引言、其他章节、附录及文献文件未修改；PDF 重新编译为 14 页，第二章第 2–4 页已检查。

详见 checks/ch2_source_revision_20261029/REVISION_NOTES.md、chapter2.diff 和 verification.json。候选逐句来源文件与最终正文有合稿差异，不可直接充作最终全部通过证明。

## 2026-10-29：按作者确认理顺第二章结构

保留三个小节，按“物理信道—AFDM调制及跨帧关系—多用户观测与贝叶斯JADCE”展开。活动变量、单帧接收信号及矩阵堆叠移入II-C，参照Shen §II-C（本地PDF p.5）先建立接收模型再提出推断任务的顺序；导频矩阵与部分正交条件移至II-B导频向量之后，保留Cai §II-A（本地期刊PDF p.4）的原有表述。

跨帧关系先于多帧观测的说明；phase rotation有Shen §II-B（PDF pp.4–5）原词依据，本文H_k^(q)=exp(jq beta_k)H_k及g_q来自既有附录B。删除容易混淆H_k与H_k^(q)的“Fortunately”段。连续时间改记t_c，整数样本索引仍为t，并写明t_c=(g+t)T_s；这些是本文符号说明，不自称参考文献整句。sampling interval沿用Ding §II（PDF p.2）的术语。

MMV之后明确Q<KN；full AFDM effective channel、sparsity assumptions和underdetermined沿用Huang §II（PDF pp.2–3）的术语，条件及张量维数按本文模型表述。H_k系数不施加稀疏假设，与Cai §II-A的设备block-sparsity structure分别说明；q_tr保留信道系数依赖的原句未变。后文与附录四处access block统一为Cai §II-A已有用词transmission block。

本轮是经作者确认的结构及衔接修订，新增时间/跨帧说明不登记为他文完整原句。原14个编号公式及标签保留，只有物理信道连续时间符号改变；摘要和引言未改，PDF编译及第二章第2–4页视觉检查完成。记录见checks/ch2_structure_revision_20261029/REVISION_NOTES.md。

## 2026-10-30：第二章语言润色

按作者要求参照既有论文润色第二章，未新增专业术语、方法名称或缩写，未改变共用定义。本轮是保留原意的语言适配，不声称逐字照录参考论文。

- **doubly dispersive、terrestrial-satellite links、differential delay、common delay、directional cosines**：重新核对 Shen 本地 PDF p.3，§II/II-A、式(1)及其后说明。路径参数和阵列参数分别集中解释；一般阵距、时间原点和阵列相位约定仍为本稿既有定义。
- **common Doppler shift、AFDM chirp subcarriers、effective channel matrix、fractional delay、power leakage**：重新核对 Huang 本地 PDF p.2／期刊p.2950，§II、Doppler shift 段及式(4)–(5)之后。使用既有词语描述本稿公式，未引入新的信道或跨帧假设。
- **inverse discrete affine Fourier transform (IDAFT)、AFDM modulation parameters、sampling interval**：重新核对 Ding 本地 PDF p.2，§II、式(1)–(3)。合并调制公式的引入，删去重复导频符号解释。DAFT 矩阵及归一化沿用本稿。
- **pilot transmission、partial orthogonal、activity indicator、block-sparsity structure、Bayesian inference、MMSE、message calculation**：重新核对 Cai 期刊 PDF pp.4–5／期刊pp.3578–3579，§II-A/B、式(1)、(3)–(5)及解释。正文直接写既有导频行正交等式，未另起名称；其维度和能量预算仍为本稿定义。
- **chirp-periodic prefix (CPP)**：沿用此前核对的 Bemani §III-A、式(18)–(19)依据，本轮只调整公式引入。本文含 CPP 的时长等式由自身样本数定义得到；移除该等式后的 Huang 引用，因为 Huang p.2950 的 `T=N Δt` 仅描述有效符号时长。两者的公式均未被改写成彼此。

详细逐段出处、适配范围与核验见 [本轮记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch2_language_polish_20261030/REVISION_NOTES.md)。原有参考文献、术语来源记录及其他稿件定义保持原样。

## 2026-10-30：C-STMP相位调度与停止候选

沿用variable projection（O’Leary–Rust，§1式(2)–(3)、§2式(5)–(7)，作者稿pp.2、4–5）及generalized EM（Dempster–Laird–Rubin，§3、p.7、式(3.5)、Theorem 1）；原文链接与本项目适配边界见[C-STMP相位选择记录](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/C_STMP_PHASE_SELECTION_20261030.md)。高斯条件矩及Shen期望二次型继续使用PHASE_MESSAGE_GEM.md的已有原文定位。能量加权相位算子变化、观测协方差相对变化、完整周期输出变化、两周期数值停止及40/20等调度均为本文直接定义的操作，不自造方法名称，不归为引用论文的现成结论。反馈常数旋转不等于返回信道直接增量；v1不利预检和v2修订均保留。仅新增C-STMP候选，不变更共用物理定义、不宣称全局收敛或已选出最优参数。

本轮有限候选比较与预留验证现已完成，选中20/20检查、5%完整周期变化、一个合格周期停止的版本；
前述1%及连续两周期规则是已测替代候选，未被选中，不据此添加文献方法名称或普遍最优性主张。
事后相位诊断直接给出`sum(abs(e-1)^2)/count`及`sqrt(sum(angle(e)^2)/count)`，
e为估计单位相位乘真实单位相位的共轭；计算范围为q>0的全部真实活动用户，包括漏检者。
该操作沿用项目既有`_shen_phase_validation.py:phase_score`的定义，仅作真值评分，不参与推断或选型。
数值定义、完整结果、逐例退化及适用范围均记录于相位选择文档；STMP与DU共用物理定义未变。


## 2026-10-30：第三至第五章结构、论证和语言修订

按作者确认的结构，第三章采用 Receiver Structure、Multi-Frame Linear Estimation、Generative-Prior-Aided Joint Denoising；第四章保留四个学习相关小节；第五章采用 Overall Algorithm 和 Computational Complexity Analysis。工程条件纳入整体算法，不独立设置阻尼、停止条件或工程技巧小节。

**MFLE（Multi-Frame Linear Estimation）和 GPJD（Generative-Prior-Aided Joint Denoising）是作者在本次讨论中明确批准的本文模块描述性名称及缩写，不是声称已有论文使用的算法名称。** 首次定义在 III-A。MFLE 的多帧对象来自本稿第二章模型；其线性 MMSE 与 Gaussian extrinsic messages 沿用 Cai §III-A、式(6)–(11)（本地 PDF pp.5–6／期刊pp.3579–3580）和 Ma §II-A/B、式(11a)–(11b)（作者稿pp.1–3）。GPJD 的条件信道估计与活动概率组合有 Cai §III-B、式(16)–(42)（PDF pp.6–8）及 Liu §III-B–D、式(17)–(29)（PDF pp.5–6）依据；generative prior 的学习依据沿用 Song、Arvinte。未把本稿模块组合名称归给上述文献。

- **Gaussian approximation、extrinsic message、site approximation**：Minka §§2–3、式(5)–(6)、(8)（作者稿pp.2–3）以及 Vehtari §2.1（JMLR PDF p.5，式(1)后 site/cavity/tilted 定义及更新商）、§2.2（p.6，自然参数）。本稿保留标量协方差近似、正精度条件与既有 site 保持规则；不宣称学习统计量是精确后验矩。
- **条件矩中的活动不确定性**：Cai §III-B 与 Liu §III-C–D 的活动加权均值、协方差；本稿先给局部模型的精确条件矩恒等式，再描述网络和高斯近似。期望残差方差更新据 Vila §III-A、式(22)–(27)（PDF p.4／期刊p.4661），应用对象是本稿局部去噪模型，不宣称全局 EM 单调性。
- **Tweedie's formula、denoising score matching**：Dytso 式(3)（PDF p.2）、Efron §2、式(2.7)–(2.8)（PDF p.4）、Vincent §4.2、式(4.3)–(4.5)（PDF pp.6–7／期刊pp.1666–1667）。新增加权 score residual 是本稿原损失的直接代数解释，未把协方差加权形式当作 Vincent 原文的各向同性公式。
- **input/skip/output preconditioning**：Karras §5、式(7)–(8)（PDF p.8）和表1（p.3）。正文明确本稿将标量预条件推广到矩阵协方差。Shastri §III-B、式(38)–(41)（PDF pp.15–16）支撑向去噪器提供相关噪声统计的思路，未将其独立噪声样本输入等同于本稿协方差输入。
- **conditional covariance、Jacobian、Monte Carlo divergence**：Dytso §II-A、式(9)（PDF p.4）的 Jacobian 约定与 §IV Proposition 1、式(22)（p.5）已核对；本稿采用 output-by-input 约定，因此为 P=JΣ。Metzler §V-B、式(21)为随机方向散度估计的依据；符号方向、协方差缩放、中心差分及块内复用是本稿既有实现，正文明确为适配，不宣称该组合逐字来自 Metzler 或闭环无偏。
- **density ratio estimation、binary classification、log odds**：Menon §II.2、§III式(6)–(8)、§IV.2式(16)–(17)（PDF pp.2–3／会议pp.305–306）。正文补明训练标签 a 和两类共享的方差采样法，区分总体最优 logit 与训练分类器的近似，再连接活动先验修正。
- **conditional RefineNet**：Song–Ermon Appendix A.3（arXiv v3 PDF p.14）及 Appendix A.1。128 基通道和本稿协方差条件输入由现有实现支撑；分类器的对数能量及保留符号的内积变换直接描述现有计算，不登记为独创方法名称。
- **整体算法的组织**：Shen §III-C末、Algorithm 1（PDF pp.9–10）用于参考其简短的初始化、阻尼、停止和复杂度说明；Cai §V-A/B、Algorithms 1–2（PDF pp.8–10）作为顺序组织的对照。没有移植 Shen 的消息算法、停止指标或 Cai 的依赖当前输入的归一化。前端 variable projection 与 minimum description length criterion 沿用原正文和附录依据，移入 V-A。
- **复杂度的计算口径**：按常规稠密矩阵乘法与分解计数，三矩阵乘积按两次矩阵乘法求值。此口径是本文分析约定，不归为某篇论文的命名方法。当前实现中未优化三矩阵收缩的额外 O(M^4) 成本已单独记录，不将正文公式宣称为每条现有 NumPy 指令的严格成本；本轮未修改实现或运行性能实验。

精确原文定位、访问方式、适配范围及实现核对见本轮 [III 来源记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/chapters_3_5_revision_20261030/ch3/SOURCES.md)、[IV 来源记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/chapters_3_5_revision_20261030/ch4/SOURCES.md)、[V 来源记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/chapters_3_5_revision_20261030/ch5/SOURCES.md) 和 [根审实现核对](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/chapters_3_5_revision_20261030/ROOT_VERIFICATION_NOTES.md)。本轮只修订 C-STMP 的结构与表述，未改动共用物理定义，因而不改写 STMP/DU 的术语记录；既有相位候选记录完整保留。

## 2026-10-30：作者确认算法名 GP-CCD-MP-DRE

**GP-CCD-MP-DRE 是作者明确批准的本文描述性算法名，不是声称已有文献采用的现成名称。** 本次取代正文和图例中的 C-STMP；首次在第 III 章开头解释四个组成部分，Algorithm 1 使用该名称。MFLE、GPJD 的模块名及其定义不变。

| 组成部分 | 含义与既有出处 | 本文使用边界 |
|---|---|---|
| GP | generative prior；Cai §III–V，特别是 §IV 的 score-based channel-prior learning；Song–Ermon 的 score-based generative modeling 与 Arvinte 的 learned channel prior，详见既有 III、IV 来源记录 | 指本文学习的信道先验；不声称生成先验或其与消息传递的结合始于本文。 |
| CCD | covariance-conditioned denoising；Shastri §III-B、式(38)–(41)（本地 PDF pp.15–16）支撑相关噪声统计条件化；Karras §5、式(7)–(8)（PDF p.8）支撑预条件化 | CCD 是作者批准的描述性缩写；上述文献并未使用这一完整名称。Shastri 的噪声实现输入与本文协方差输入不同，Karras 的标量预条件推广到矩阵是本文适配；算法与训练/在线协方差设置不因更名而变化。 |
| MP | message passing；Cai §III–V、Ma §II-A/B、式(11a)–(11b)（作者稿 pp.1–3） | 指本文 MFLE 与 GPJD 的迭代外信息交换，仍采用既有高斯近似，不将更名解释为新建消息传递范式。 |
| DRE | density ratio estimation；[Menon–Ong](https://proceedings.mlr.press/v48/menon16.pdf) §II.2、§III 式(6)–(8)、§IV.2 式(16)–(17)（PDF pp.2–3／会议 pp.305–306） | 指经训练类别先验校正的分类器密度比估计；DRE 在每次适用的迭代内参与活动概率及联合矩更新，后缀位置不表示后处理。 |

命名组织参照 [Shen](https://arxiv.org/html/2412.20806v1) 的 **MRF-MP-GAMP**（§III-C 末、Algorithm 1，本地 `shen2025.pdf` pp.9–10）及 **MRF-MP-GAMP-CNN**（§IV-A/B、Fig.4，p.11）：整体算法用主要技术组成命名，功能模块另行定义。本文没有移植 Shen 的 MRF、GAMP 或 CNN 结构，也不把各缩写的连字符顺序当作流程执行顺序。

实验中的 STMP 标签不变。本地配置的 STMP 也包含学习的活动分类器，因此本次命名不支持“DRE 是相对于该本地比较基线的独有组件”这一表述。存储目录 `paper`、实验标识 `C_STMP`、历史文档、配置、权重与原始统计保留。共用物理定义未变，不修改 STMP/DU 术语表。

本轮具体改动与检查见 [命名修订记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/algorithm_name_20261030/REVISION_NOTES.md)。

## 2026-10-30：实验分析的论证和表述依据

本轮保留 GP-CCD-MP-DRE、MFLE、GPJD 及全部模型定义，不引入新算法名称或缩写。第 VI 章按各实验的问题组织分析；数字来自本稿已保存数据，未移植参考论文的性能结论。

- **去噪与整体接收机分开评估**：Cai §VI-B–C、Figs.4–5（正式期刊 PDF pp.11–12／pp.3585–3586）。本稿先比较均值估计器，再分析迭代轨迹；Gaussian-prior estimator 对所有系数乘同一因子的说法直接来自原有 $P_{\rm tr}R/(P_{\rm tr}+v)$ 公式。未将本稿与 genie 的明显差距描述为“接近下界”。
- **瞬态、稳定区间与停止轮数**：Cai §VI-C、Fig.5（PDF p.12）。原文对第二轮反弹使用推测性解释，本稿不套用其早期路径损耗失配原因；约30轮接近最终精度是本稿单场景轨迹事实，60轮是已有最小停止数。没有新增全局收敛主张。
- **由曲线差异构成论证**：Cai §VI-C、Figs.6–7（PDF pp.12–13）与 Shen §V、Figs.6–8（PDF pp.13–14）。本稿讨论两类基线随 SNR 改变的不同趋势，并按已有 NMSE/AER 定义解释排名差异。第 III 章式 `eq:mixture` 仅支持活动与信道估计的结构耦合，不能单独证明相对 STMP 的增益成因。
- **固定误差目标对应的资源需求**：Cai §VI-C、Figs.8–10（PDF pp.13–14）与 Shen §V、Figs.6–7（PDF pp.13–14）。本稿的24对32帧、80对40候选终端均来自所测离散网格，不插值成连续门槛，也不宣称一般容量倍增；帧数变化固定每帧能量，用户数实验固定的是名义活动概率。
- **负载与稀疏性**：Shen §V、Fig.8（PDF p.14）将活动负载和固定接收资源联系起来。本稿结合第 II 章观测维数与第 VI 章 SNR 定义，区分增大候选维数和增加活动密度。固定 aggregate received SNR 下典型每终端 SNR 降低，是独立随机相位、相近平均信道功率下的模型解释；不是新增实测曲线或逐场景单调性保证。非空条件抽样下实际边缘活动概率变化仍按原式保留。
- **跨信道比较**：Cai §VI-C、Fig.11（PDF pp.13–14）。本稿沿用固定网络跨 profile 评估的问题，但不照搬其全区间优于基线或随机训练产生泛化的因果结论；保留 A/B 高 SNR 下 STMP 更优及 B 在4 dB处近乎重合的事实。

来源原文：[Shen](https://arxiv.org/html/2412.20806v1)、[Cai](https://arxiv.org/html/2506.00581v2)。本地正式版页码以 `reference/literature/shen2025.pdf`、`reference/literature/cai2026.pdf` 为准。详细对照、数值依据和人工复核见 [本轮修订记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/experiment_analysis_20261030/REVISION_NOTES.md)。原有运行和参数选择事实移入附录 C，没有删去不利结果或改变统计口径；STMP/DU 的共用定义不变。

## 2026-10-30：第二章逐句来源核查后的修订

按作者“尤其是没有原词的必须替换”的要求，基于本轮[54句来源核查](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch2_sentence_source_check_20261030/FULL_AUDIT.md)修订当前第二章。此前21句“有依据但自主改写”中20句恢复可定位原句或分句组合；余下P12.S03直接解释Cai表II的确定性关系与Bernoulli分布，明确作为本稿公式说明保留，不伪造对应英语原句。

- **joint posterior distribution / 联合后验分布**：Cai正式版PDF p.4、期刊p.3578，§II-B式(5)的引入句有该原词。本轮用它替换正文中未查到对应原词出处的 **working posterior**。分布符号q、训练先验q_tr、给定前端估计和独立性假设均保留；内部标签`eq:working-posterior`仅为交叉引用标识，不在PDF中构成术语。
- **terrestrial-satellite links、doubly dispersive channel model、differential delay、common delay、directional cosines**：Shen PDF p.3，§II与§II-A式(1)前后。恢复源句的因果关系、定义谓词及指代，只更换本稿设备/路径索引、导频对象和符号。阵元间距、波长及相应轴向的定义分句另核Li PDF p.4、§II-B；未引入Li的归一化、相位符号或新的角度变量。
- **pilot symbol、AWGN matrix、block-sparsity structure、Bayesian inference framework**：Cai正式版PDF p.4，§II-A/B式(1)、(3)–(5)。恢复标量导频、活动概率、接收信号where分句、矩阵收集与目标句的源词。本文矩阵维度和双求和仍由第二章自己的AFDM模型定义。
- **sampling interval、inverse discrete affine Fourier transform (IDAFT)、discrete affine Fourier transform (DAFT)**：Ding PDF p.2，§II式(1)–(3)及Huang PDF p.2、§II首段。采样及IDAFT引入恢复Ding分句，DAFT矩阵命名采用Huang的对应分句；保留本稿正确的矩阵式，没有复制Ding式(2)及其文字的F/Fᴴ和A/Aᴴ不一致。
- **chirp-periodic prefix (CPP)**：Cai PDF p.4、§II-A的前缀条件主句与Bemani PDF p.8、§III-A式(19)前允许相等的长度条件组合。英文比较关系与本稿既有≥保持一致；长CPP及路径算子仍是本稿定义和推导。
- **fractional Doppler shifts、fractional time delays、power leakage、full AFDM effective channel、sparsity assumptions**：Huang PDF pp.2–3，§II式(5)后及§III-A式(6)后。恢复对应原句/分句，必要时将矩阵改为本稿张量；不宣称Huang给出了本文所有时延范围和起点约定下的完整算子。
- **message-passing algorithms、deep generative priors、message calculation**：Cai PDF pp.4–5、§II-B。结尾保留可定位的近似求解和生成先验分句组合。交叉复核后删除组合句中脱离具体得分网络/MMSE关系的高维积分尾从句，没有在正文增加解释段。

本轮保留全部14个编号公式和标签，不改变共有物理定义，故不修改STMP/DU术语记录。逐项修改、原句定位、公式保护检查和交叉复核见[修订记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch2_source_revision_20261030/REVISION_NOTES.md)。摘要未重新生成。

## 2026-10-30：去噪图纵轴比例调整预览

- **scale_y_cut / 将纵轴划分为多个区间并调整各区间的显示空间**：Xu 等，*Use ggbreak to Effectively Utilize Plotting Space to Deal With Large Datasets and Outliers*，Frontiers in Genetics，2021，12:774846，[出版者原文](https://www.frontiersin.org/journals/genetics/articles/10.3389/fgene.2021.774846/full)，Description / Overview、Example 3、Figure 3。该原词为 R 包函数名；本项目仅参考显示思路，以现有 Python 绘图代码实现，未使用或复现该软件包。
- **Scaling of Subaxes / 各段坐标轴的缩放**：Thorsøe 等，*A Framework for Axis Breaks in Charts*，VMV 2024，[作者全文](https://cs.au.dk/~hjschulz/pdfs/vmv24.pdf)，§2、PDF p.2 Step 3；PDF p.3 Steps 4–5 区分删除区间和保留连续区间，并讨论通过刻度间距与轴标记表达不同尺度。PDF p.7 说明尺度改变会影响斜率解读；本预览不将跨区间斜率用作性能改善速度的证据。

本次预览按用户指定完整保留 −45 至 5 dB 的线性刻度，两端每 dB 的显示距离取中间的 1/4；边界和比例为本项目的显示设置，不是上述论文推荐的参数或新方法名称。全部 54 个测量点、原始 dB 数值及来源记录保留，仅改变纵向显示比例；两端用浅灰底色、轴标记和比例文字说明。原论文图未替换。文献核验、显示参数与数值检查见[独立预览目录](../../result/channel_denoising/figures/axis_scale_preview_20261030)。


## 2026-10-30：第三至第五章五类组合表述改为直接描述

按作者“第二类全部改掉”的要求，本轮替换第 III–V 章中上轮核对列出的五类表述；保留已登记的 GP-CCD-MP-DRE、MFLE、GPJD、CCD 名称。

| 原表述 | 当前写法与出处 |
|---|---|
| query、active/inactive query、query densities | 使用 denoiser input，直接定义活动标签 a=1 时 R=H+W、a=0 时 R=W，并称为给定 a 的输入密度。denoiser input 原词见 [Shastri §III-B，式(38)](https://arxiv.org/html/2206.05049v2#S3.SS2)；本稿样本构造和变量仍由式 `eq:query-densities` 定义。 |
| activity evidence | 改为 log density ratio，直接说明由对应高斯密度计算其对数比，再计算活动概率。density ratio 原词及先验几率关系见 [Menon §III，式(6)–(8)，PDF p.2](https://proceedings.mlr.press/v48/menon16.pdf)；具体高斯密度和式 `eq:gaussian-evidence` 为本稿近似。 |
| training-prior correction | 直接说明从分类器输出中减去训练类别先验的 log odds 后得到对数密度比估计；依据仍为 Menon §III 式(6)–(8)及 §IV.2 式(16)–(17)，不命名为额外方法。 |
| covariance-weighted denoising loss / covariance-weighted form of denoising score matching | 直接说明信道平方误差由 Σ^{-1} 加权；变换为 score 误差后由 Σ 加权。denoising score matching 原词见 [Vincent §4.2，式(4.3)–(4.5)，PDF pp.6–7](https://gwern.net/doc/ai/nn/diffusion/2011-vincent.pdf)。矩阵加权形式是本稿现有损失的代数表达，不冒称 Vincent 原文给出同一协方差形式。 |
| conditional RefineNet | 改为 RefineNet backbone，另句描述本稿将 v 和协方差因子作为条件。RefineNet 原词见 [Song–Ermon Appendix A.3，PDF p.14](https://arxiv.org/pdf/1907.05600)，原文条件归一化见 A.1；本稿条件输入由现有实现定义，不归为原文已有架构名。 |

五类词组已从第 III–V 章的可见正文移除；含 query/evidence 的内部 LaTeX 标签只是交叉引用标识，保留以避免破坏引用。编号公式、引用条目、网络、训练设置和算法均未改动。旧术语记录保留历史原文，本条更新当前正文的用词。改动和检查见 [修订记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/terminology_plain_description_20261030/REVISION_NOTES.md)。

## 2026-10-30：有色扰动训练与接收机贡献的表述统一

本轮将摘要及第 I、III、IV、VI 章的概述统一为：以有色高斯扰动训练生成式信道先验，再将所学先验用于消息传递中的信道后验矩计算。删除摘要和贡献段中容易被理解为在线适配相关误差协方差的目的性措辞。第 II 章无需修改；第 V 章仅将均值网络与活动分类器合称为 trained networks。

- **score-based generative prior、colored Gaussian perturbations、denoising score matching**：沿用 Cai §IV、Song–Ermon、Arvinte 的信道先验学习用语，以及 Vincent §4.2、式(4.3)–(4.5)（PDF pp.6–7）的去噪得分匹配。本文的协方差加权损失与得分形式仍是第四章现有公式的直接代数对应；未将其包装为文献已有的新方法。来源定位沿用 [第四章来源记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/chapters_3_5_revision_20261030/ch4/SOURCES.md)。
- **covariance-conditioned denoising / CCD**：保留作者已确认的描述性算法名 GP-CCD-MP-DRE；第三章首次展开将 CCD 明确归于离线先验学习。第四章继续如实描述协方差条件输入与矩阵预条件。其实现分别为 `src/training/colored_score_20261024/noise.py` 的 `condition()`（第50–58行）和 `src/training/colored_preconditioned_20261024/model.py`（第27–48行）。Shastri §III-B、式(38)–(41)（本地PDF pp.15–16）及 Karras §5、式(7)–(8)（PDF p.8）仍仅支撑对应的既有思路，完整名称及本文矩阵适配不冒称原文原词。
- **在线调用**：现有 `src/algorithm/C_STMP/moments.py` 第75–79行使用单位协方差因子。正文原有的 (F_\theta(R,vI_D)) 与标量方差消息保持；本轮不新增训练与在线差异的说明段落。
- **性能主体**：第 VI 章将“Colored training gives ...”改为比较“the estimator trained with colored noise”与白噪声训练的估计器。白噪声网络与本稿网络还存在条件输入、预条件和均值参数化差异，现有曲线不单独识别噪声颜色的因果收益。数值、图例、实验条件及其既有说明均保持。

中英文摘要仅同步修改授权主题涉及的句子，未重新生成摘要；所有数学表达式、标签和引用保持。完整差异、实现定位与交叉复核见 [本轮修订记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/colored_prior_framing_20261030/REVISION_NOTES.md)。


## 2026-10-30：全篇术语出处与一致性清查（待修订清单）

本轮通读当前摘要、I–VI章、附录A–D、算法、表格、八幅图（接收机框图及七幅实验图），另核中文摘要。完整结果见[全篇核查报告](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/full_terminology_audit_20261030/REPORT.md)。这是清查记录，报告中的替换建议尚未应用于正文。

- 优先处理：CPP条件中maximum channel delay spread与最大差分时延的混称；表I的Residual-delay support；VI-A旧称first-order network；VI-A残留training queries、scalar query covariance、covariance-weighted loss；balanced binary cross-entropy的类别平衡/损失名称混写；附录B的frequency wrapping引文词面依据；N被称为AFDM block length而正文把Q帧称transmission block。
- 差分时延依据：Shen §II-A式(1)后（本地PDF p.3）和§V表I（p.12）；表中[0,699] μs原名为differential delay。本文30–50 ns的delay spread另指多径功率时延谱缩放量，两个量不能因润色合并。
- 合法别称复核：Cai §III-B标题（本地PDF p.6）明确使用Channel and Device Activity Denoisers；Vehtari §2.1（PDF pp.5–6）、§2.2、§5.3及Appendix A.1明确支持site approximation与natural parameters。不能把activity denoiser、Gaussian site approximation一概判为自造名称。
- proper complex Gaussian是标准术语，但本轮取得的当前引用全文未核到该完整原词。可补直接原文Neeser–Massey，[IEEE TIT 1993作者存档](https://www.isiweb.ee.ethz.ch/archive/massey_pub/pdf/BI437.pdf)，§III-A Definition 1（PDF p.2/期刊p.1294），以及摘要、引言对proper Gaussian的说明；当前未自动新增书目。对非零均值Gaussian，不把未中心化变量直接改称zero-mean或circularly symmetric。
- GP-CCD-MP-DRE、MFLE、GPJD、CCD继续按作者已批准的本文名称管理，不冒称文献原名。物理噪声方差与去噪输入方差、p/ρ/πtr/pk、H/X、C/Σ等定义本轮未发现需要合并的用词冲突。

当前32个引用键均能在书目中找到；本轮取得27篇全文，其中26份PDF完整性预检通过，Vila本地文件有修复告警。另5项仅元信息或在线片段可见，未做全文不存在断言。完整出处、逐项位置、65项辅助词面检索、缩写人工复核和未改稿哈希检查均保存在报告目录。未修改共用定义，无须同步STMP/DU。

## 2026-10-30：全篇清查项目落实（保留作者指定缩写）

作者已批准落实上一节清单，并明确 MIMO、GNN-ASPL、NTN-TDL-D 等缩写无须补展开。本轮完成 F01–F07、U01–U04、U06；U05 不实施，MSE 同样保留原写法。完整处置及核验见[修订记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/full_terminology_revision_20261030/REVISION_NOTES.md)。

| 统一后的用法 | 原文依据、定位与本稿边界 |
|---|---|
| differential delay；maximum differential delay；Differential-delay range | Shen §II-A、式 (1) 后（PDF p.3）及 §V、表 I（PDF p.12）。第二章 CPP 覆盖最大差分时延；表 I 的 [0,699] μs 与此一致，[30,50] ns 的多径 delay spread 不合并。 |
| channel denoiser | 本稿 fθ 输出条件均值，由第四章现有公式定义；channel denoiser 原词见 Cai §III-B（PDF p.6），denoiser 输入和噪声统计见 Shastri §III-B、式 (38)–(41)（PDF pp.15–16）。本文网络统一采用功能称呼，不再沿用 first-order network；介绍 Cai §IV-B/C 的 score networks 时保留原名。 |
| binary cross-entropy；等概率活动/非活动训练标签 | 损失与类别采样分开描述。Ying §III-D（PDF p.6）使用 binary cross-entropy；Menon §II.1–2、§III–IV.2 支持分类损失、类别概率和密度比的区分。等概率标签是本稿既有训练设定，不包装为另一个损失名。 |
| 输入噪声协方差 C=vI；第四章损失公式 | 沿用本稿第四章的直接数学定义。Shastri §III-B、式 (38)–(41) 支持 denoiser input/noise statistics 的说法；Vincent §4.2、式 (4.3)–(4.5) 支持 denoising score matching 的基本目标，不冒称其给出本稿矩阵加权形式。 |
| AFDM basis waveform；chirp-periodic prefix；chirp subcarriers | Huang §II、式 (5) 支持分数时延 AFDM 背景；Bemani §III-A、式 (19) 前后支持 CPP。附录 B 直接用 wξ、ζn 及波形公式定义本稿操作，删除未核到同名出处的 frequency wrapping；表 I 以每帧 chirp subcarriers 数说明 N。 |
| proper complex Gaussian | 新增 Neeser–Massey 1993（`neeser1993`）。[原文](https://www.isiweb.ee.ethz.ch/archive/massey_pub/pdf/BI437.pdf) §III-A、Definition 1（印刷 p.1294 / PDF p.2）给出 proper 的定义；Theorem 1、式 (10)（印刷 p.1295 / PDF p.3）给出一般均值复高斯密度。于符号说明处引用，保留非零均值的数学含义。 |
| candidate devices；nominal activity probability；NTN-TDL profiles | device 为正文主称呼；K、p、ρ 的定义沿用第二章与第六章。图 6、7 分别明确候选设备数和名义活动概率；图 8 标为 NTN-TDL-D/A/B/C，与正文、附录的固定几何下 profile 比较一致。这些是既有对象的描述，不引入新方法名称。 |

统一 subcarrier(s)、precompensation/precompensate 的拼写；内部路径、标签和引用论文正式题名保持。含公式定义的停止条件 residual 表述保留。GP-CCD-MP-DRE、MFLE、GPJD、CCD 继续按作者批准的本文名称使用。所有数学表达、实验数值、模型绑定和训练设置不变；中英文摘要未重写。仅维护当前稿的用词与引用，不改变三份稿件共用定义，因此不改 STMP/DU。

## 2026-10-30：篇幅压缩后的用词复核

本轮将完整阅读稿由 15 页压缩至 12 页，合并重复解释，沿用上文已核对的专业术语、原文出处和定义边界，不新增方法名称或缩写。保留 differential delay 与 delay spread、物理噪声方差与去噪输入方差、训练协方差与在线输入协方差的区分。训练方差的采样直接写为“uniformly on a logarithmic scale”，不另设名称；性能比较仍以 estimator trained with colored noise 为主体，不把完整模型比较归因于噪声颜色单一因素。保留作者指定缩写和已批准名称，中英文摘要未重新生成。未改变共用定义，不同步 STMP/DU。修改范围及核验见[篇幅压缩记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/compress_20261030/REVISION_NOTES.md)。

## 2026-10-31：按作者要求恢复原引言

引言恢复到本轮压缩前、已经完成全篇术语统一的版本，文件与 `checks/compress_20261030/before/sections/01_introduction.tex` 完全一致。恢复背景、方法动机和贡献的完整说明，并重新保留“approximately constant”等原有限定；其余章节的压缩和已核定术语不变，没有新增名称或引用，也不改变共用定义。中英文摘要保持原文。当前阅读稿为 13 页，完整记录见[恢复引言](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/restore_introduction_20261031/REVISION_NOTES.md)。

## 2026-10-31：附录 A、B、D 的内容移入对应正文

按作者“ABD 请你都处理一下，C 先不动”的要求调整内容位置；既有术语、方法、公式与数值设置不变，不新增名称或缩写。完整迁移及核验见[修订记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/appendices_restructure_20261031/REVISION_NOTES.md)。

| 内容 | 调整后位置与出处边界 |
|---|---|
| noise variance estimation；minimum description length (MDL) | 原附录 A 的噪声估计完整移至 V-A1；仍采用本稿已有空间协方差、尾部特征值和 MDL 公式，沿用 Nadakuditi–Edelman 的既有引用，不改称 Shen 的 EM 更新。 |
| inter-frame phase estimation；variable projection | 相位估计继续留在附录 A，并明确用于帧间相位不可用时；沿用 O’Leary–Rust 的既有引用和原推导。VI-A 的实验使用已知帧间相位，二者含义不混同。 |
| AFDM basis waveform；chirp-periodic prefix | 波形定义移至 II-B；重复路径矩阵公式与正文原式合并。逐元素展开、整数时延形式和跨帧关系保留在附录 B。沿用上文 Bemani §III-A、式 (19) 与 Huang §II、式 (5) 的来源边界，不宣称这些文献已给出本稿全部起点及长时延约定。 |
| singular value decomposition (SVD)；classifier inputs；stopping criteria | 原附录 D 的 SVD 计算式移至 III-B，分类器输入移至 IV-D，停止条件移至 V-A3，训练与导数估计的数值设置移至 VI-A。它们仍是本稿既有运算、输入和设置，不包装成新增方法。 |

组织方式参考 Cai v2 §V-B（PDF pp.9–10）和 §VI-A（pp.11–12）在正文介绍消息权重、归一化和实验设置，以及 Shen §II-B Proposition 1（p.4）在正文给出结果、Appendix A（p.15）保留证明，§III-C（p.9）在正文介绍参数估计。上述仅作为篇章组织依据，不是本稿估计器或实现细节的技术来源。本地核对版本为 `reference/literature/cai2026_stmp_v2.pdf`、`reference/literature/shen2025.pdf`，对应原文为 [Cai](https://arxiv.org/pdf/2506.00581)、[Shen](https://arxiv.org/pdf/2412.20806)。

附录 C 的源文件与编号均保持；中英文摘要和恢复后的引言完全未改，未重新生成摘要。未改变共用定义，因此不修改 STMP/DU 术语记录。

## 2026-10-31：摘要讨论中的 representation 与 spanning 用词核验

本条记录聊天讨论的词面核查与候选表达，未将讨论稿写回英文或中文摘要，也未重新编译论文。

- **sparse representation / 稀疏表示**：当前书目 Tropp–Gilbert–Strauss 的 *Algorithms for Simultaneous Sparse Approximation. Part I: Greedy Pursuit*，本地 `reference/literature/tropp2005_somp.pdf`，PDF p.2、§1 Introduction，明确使用该原词描述具有稀疏表示的信号。因此该术语并非自造，但来源不能自动证明本稿关于信道先验的具体作用。
- **sparse or grid-aligned channel assumptions**：Huang 等 *Prior-Agnostic AFDM Channel Estimation for High-Mobility LEO Satellite Communications Using Diffusion Models*，本地 `reference/literature/huang2026.pdf`，PDF p.1 摘要（印刷 p.2949）直接使用该表述；PDF p.3、§III-A、式 (6) 后（印刷 p.2951）明确说明估计完整 AFDM 有效信道时不施加 sparsity assumptions。摘要候选句据此优先采用该组原词，保留不依赖信道稀疏及网格对齐假设的含义，不能扩大为不利用设备活动稀疏性或不依赖任何统计假设。
- **spanning different noise levels and correlation structures**：此前聊天中的自主概括，不是已核到的文献原词组合；撤回该候选表述。改用 colored Gaussian noise 与 covariance matrices 直接描述训练：Shastri 等 §III-B、式 (38)–(41)（PDF pp.15–16，[原文](https://arxiv.org/html/2206.05049v2#S3.SS2)）给出协方差参数变化的有色高斯噪声训练；本稿 §IV-D/VI-A 定义自己的协方差采样。候选表述为训练使用不同协方差矩阵的有色高斯噪声，不宣称文献证明了本稿在线误差匹配或收益。

完整句子为本稿基于已核术语和现有实现作出的表述，不伪称参考论文的逐字原句；物理模型、算法及共用定义均不变。

## 2026-10-31：按作者确认修改摘要的训练动机与命名

作者确认采用 “Motivated by the potential mismatch ... caused by the finite-dimensional, structured multi-frame AFDM observation model” 句式。本轮将该句写入英文摘要并同步中文摘要，保留生成式先验不依赖信道稀疏和网格对齐假设的作用；补入 GP-CCD-MP-DRE 名称以及 multi-frame linear estimation、generative-prior-aided joint denoising 两个既有模块全称，不在摘要新增 MFLE/GPJD 缩写。保留后验均值与方差、密度比估计、软活动概率和模块迭代交换的原有说明。

- **sparse or grid-aligned channel assumptions**：沿用上一条已核的 Huang 摘要及 §III-A 术语；限定为信道假设，不取消设备活动稀疏性。
- **denoiser-input errors、white Gaussian training noise、colored Gaussian noise、covariance matrices**：Shastri §I、§III-A 式 (28) 与 §III-B 式 (38)–(41)，以及 Wei–Yuan §I（[原文](https://arxiv.org/html/2610.17785v1#S1)）对有限维、结构化压缩矩阵及 STMP 白高斯模型条件的讨论。来源支持一般失配问题；本稿对多帧 AFDM 的联系作为设计动机表述，保留 potential，不宣称已证明实际误差分布或有色训练消除了失配。
- **不同协方差的有色训练**：本稿 §IV-A/D、§VI-A 与现有训练实现；在线调用仍为 C=vI，本轮没有改变网络、消息或参数。
- **接收机与模块命名**：沿用作者已批准的命名以及 §III-A 的定义，不冒称 Shen 摘要采用同样的命名安排。

中英文摘要此次同步修订；引言、正文、附录（包括 C）、图表、实验结果和书目均保持。本轮仅更新源稿并核对文本，未重新编译 PDF；旧阅读 PDF 暂时保留上一轮内容。源文件备份与核验记录见 [../checks/abstract_motivation_20261031/](https://github.com/RESET-cpu/afdm-gfra/tree/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_motivation_20261031)。

## 2026-10-31：摘要中的名称按组成部分依次引出

按作者要求，摘要先完整介绍 generative prior learned by covariance-conditioned denoising（GP-CCD），再与 message passing（MP）相结合引出 GP-CCD-MP；在介绍活动概率的学习分类器时展开 density ratio estimation（DRE），之后才出现完整名称 GP-CCD-MP-DRE。GP 和 CCD 的含义沿用第三章开头及既有命名登记：CCD 属于先验学习，未改成新的在线协方差估计模块。DRE 仍展开为 density ratio estimation，而不是将 E 改释为 estimator。

上述为摘要内的介绍顺序，未新增一项单独评估的算法或无 DRE 对照实验；正文、算法框和图例的完整方法名均维持 GP-CCD-MP-DRE。density ratio estimation 的来源继续为 Menon–Ong §4.2，学习分类器的具体关系由本稿 §IV-C 给出；GP-CCD 及组合名称继续按作者批准的描述性命名管理。已确认的有色训练动机句逐字保留。中英文摘要同步，其他章节、附录 C 和书目未变；未重新编译 PDF。备份和检查见 [../checks/abstract_naming_order_20261031/](https://github.com/RESET-cpu/afdm-gfra/tree/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_naming_order_20261031)。

## 2026-10-31：按作者原段落仅补两个模块名称

作者重新指定摘要后半段以其贴出的四句原文为基础，仅补模块命名，取代上一条逐步介绍完整算法名的安排。当前摘要在先验去噪处补入 generative-prior-aided joint denoising（GPJD），在线性估计处补入 multi-frame linear estimation（MFLE）；二者的全称、缩写与第三章 §III-A 完全一致，继续作为作者已批准的本文模块名称管理。恢复 learned density-ratio estimator、后验矩与软活动概率结合、模块间软信息交换及原仿真结论的表述，不在摘要展开 GP-CCD、GP-CCD-MP 或 GP-CCD-MP-DRE。完整算法名在正文、算法框和图例中仍保留。

摘要前半段（含生成式先验作用和已确认的有色训练动机）保持；中英文同步。技术来源及方法含义沿用既有记录，没有新增方法或术语。引言、正文、附录 C、图表和书目均未变；仅更新源稿，未重新编译 PDF。备份与核验见 [../checks/abstract_module_names_20261031/](https://github.com/RESET-cpu/afdm-gfra/tree/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_module_names_20261031)。

## 2026-10-31：摘要模块顺序与正文接收机结构对齐

按作者反馈，将摘要中的首次介绍顺序改为 multi-frame linear estimation（MFLE）在前、generative-prior-aided joint denoising（GPJD）在后，与 §III-A 和 Algorithm 1 的处理顺序一致。先用一句说明两个模块的接收机结构，再说明 GPJD 的后验矩及软活动概率计算，最后说明软信息与 MFLE 迭代交换。名称及含义沿用既有登记，没有新增术语；没有将迭代接收机改述为两个独立估计阶段。

摘要前半段、密度比估计器说明及仿真结论保持，中英文同步；正文和附录不变，未重新编译 PDF。源稿备份及核验见 [../checks/abstract_module_order_20261031/](https://github.com/RESET-cpu/afdm-gfra/tree/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_module_order_20261031)。

## 2026-10-31：摘要精简重复背景与先验表述

按作者确认的精简范围，仅删除第二句中重复的 GNSS 辅助预补偿背景，并合并接收机模块介绍中重复的 module 与 learned prior 表述。首句保留无 GNSS 辅助的系统范围；生成式先验不施加信道稀疏和网格对齐假设的句子、有色训练动机句、后验矩与活动概率结合、软信息交换和仿真结论均保留。MFLE、GPJD 的全称和首次出现顺序不变，MMSE 去噪及后验均值、方差含义不变。

中英文摘要同步；术语和来源沿用上述记录，没有新增技术名称或结论。其他正文、附录 C 和书目未变；仅更新源稿，未重新编译 PDF。源稿备份、词数与文本核验见 [../checks/abstract_concise_20261031/](https://github.com/RESET-cpu/afdm-gfra/tree/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_concise_20261031)。

## 2026-10-31：摘要动词、衔接及句式与参考文献核对

本轮按作者反馈调整现有摘要的局部句式，不把普通学术用词因个人风格偏好判定为错误或自造术语。出处与处理如下：

| 用词或句式 | 原文定位与本稿处理 |
|---|---|
| handle；Based on this model | [Shen 原文](https://arxiv.org/html/2412.20806v1)，§II-B 首段用 handle 描述大差分时延与多普勒频移；§I 讨论文献 [25] 后用 Based on this model 引出算法。本稿据此替换 To accommodate、Building on this model。Shen §I 本身亦有 accommodate 和 Building on this 的实际用例，替换属于贴近对应语境的风格选择，不是纠错。 |
| 接收机由两个模块组成；模块交换软信息 | Shen 摘要先介绍 receiver structure 与三个模块，再介绍 soft information 交换。本稿沿用这一介绍顺序，以 with two modules 后接本稿 MFLE、GPJD 两个已批准名称，并以 The two modules 为交换动作的主语；不沿用 Shen 的模块或算法定义。 |
| incorporate；demonstrate；outperform | [Cai v2 摘要](https://arxiv.org/html/2506.00581v2)用 incorporate 描述将生成式先验用于 message passing；Shen 摘要用 demonstrate 与 outperform 报告仿真结论。本稿保留这些有原文用例的词，不新增强调性能幅度的形容词或副词。 |
| 后验矩、活动不确定性及 MMSE 去噪 | Cai §III-B1、§III-B3、§IV-A 的术语与本稿第三、四章现有公式继续作为依据。将 providing 改为 to obtain，并将 thereby incorporating 改为 to account for，属于普通语法调整；不声称完整句子是参考论文的原句，也不引入新的估计方法。 |

有色训练的 Motivated by ... caused by ... 句子及 potential 限定逐字保留，先验不施加信道稀疏或网格对齐假设的表述保持。finite-dimensional、structured、colored、posterior、soft 等具有技术含义的修饰语保留，依据仍为前述各条。中英文摘要同步；引言、正文、附录、书目及 PDF 不变。备份、差异与核验见 [../checks/abstract_reference_style_20261031/](https://github.com/RESET-cpu/afdm-gfra/tree/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_reference_style_20261031)。


## 2026-10-31：摘要以并列 which 从句说明模块作用

按作者要求，将 MFLE、GPJD 的功能分别紧接在各自名称后的 which 从句中。MFLE 说明跨帧线性 minimum mean-squared error（MMSE）估计，依据本稿 §III-B 的式 `eq:linear-mean`、`eq:linear-variance`，对应既有 Cai v2 §III-A 的 linear MMSE estimation；GPJD 说明 MMSE 去噪及后验均值、方差估计，沿用本稿 §III-C/IV 与 Cai §III-B/IV-A 的既有依据。MMSE 全称移至首次出现的 MFLE 从句，后文使用其缩写；MFLE、GPJD 的名称与顺序不变。

中英文摘要同步。此前确认的生成式先验作用、有色训练动机、软活动概率与密度比估计器、活动不确定性和模块交换说明均保持。没有新增方法、实验结果或术语；正文、附录、书目及 PDF 未变。备份与文本核验见 [../checks/abstract_module_clauses_20261031/](https://github.com/RESET-cpu/afdm-gfra/tree/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_module_clauses_20261031)。


## 2026-10-31：摘要按模块功能简化 MMSE 描述

按作者要求重新对照 Cai 和 Shen 的摘要，保留两个并列 which 从句，删去 MFLE 从句中的线性 MMSE 准则说明，转为概述其干扰抑制作用。GPJD 从句只说明将所学先验用于 MMSE 去噪；后验均值、方差与软活动概率合并在下一句说明。MMSE 在摘要中只出现一次。

- **篇章层次依据**：[Cai v2 摘要](https://arxiv.org/html/2506.00581v2)介绍生成式先验用于 MMSE 去噪及方差计算，没有在摘要中另行解释 LMMSE；[Shen 摘要](https://arxiv.org/html/2412.20806v1)按各模块承担的任务介绍接收机，再说明模块间软信息交换。此处借鉴介绍层次，不沿用两篇论文的模块定义。
- **inter-user interference**：Shen 摘要明确使用该术语描述线性模块的干扰处理。对本稿，第二章 `eq:observation-tensor`/`eq:mmv` 给出多设备叠加，第三章 `eq:linear-mean` 的联合线性更新保留完整有效导频矩阵的 Gram 矩阵；据此将 MFLE 的作用概述为 suppresses inter-user interference。该句是对本稿已有联合线性估计的功能描述，不声称完全消除干扰，也不新增单独测量过的干扰抑制指标。
- **MMSE denoising、posterior mean and variance、soft activity probabilities、density-ratio estimator**：沿用此前登记的 Cai §III-B/IV-A、Menon §III/IV.2 与本稿第三、四章现有公式；没有改变去噪、活动概率或后验矩的计算。

有色训练动机、先验不施加信道稀疏或网格对齐假设、MFLE→GPJD 顺序、活动不确定性、软信息交换及仿真结论保持。中英文摘要同步；引言、正文、附录、书目及 PDF 未变。备份与文本核验见 [../checks/abstract_module_functions_20261031/](https://github.com/RESET-cpu/afdm-gfra/tree/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_module_functions_20261031)。


## 2026-10-31：摘要中先验训练与接收机的衔接

按作者反馈，将接收机介绍的起句改为 The learned prior is then incorporated into ...，直接承接上一句的去噪器训练；GPJD 从句相应简化为 performs ... denoising，避免重复说明所学先验。此处仅调整篇章衔接，技术术语及来源沿用此前核定记录，两个模块的功能、顺序、后验矩、软活动概率和结论不变。中英文摘要同步；其余正文与 PDF 不变。备份与文本核验见 [../checks/abstract_transition_20261031/](https://github.com/RESET-cpu/afdm-gfra/tree/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_transition_20261031)。

## 2026-10-31：摘要两处句法优化

按作者确认的两处候选表达，将有色训练动机拆为潜在失配与训练措施两句，以 may cause 保留原来的不确定性限定；将后验矩与软活动概率结合的句子改以 GPJD 为主语。中英文摘要同步，模块名称、功能、顺序、技术内容、贡献表述及仿真结论保持。

本轮没有新增术语或技术主张。有限维结构化观测模型与训练失配的动机沿用本稿引言及既有出处记录；GPJD 的操作范围对应本稿 §III-C 的 `eq:exact-local-moments`、`eq:conditional-moments` 和 `eq:activity-probability`，后验矩与活动概率的含义沿用前述 Cai §III-B/IV-A 及 Menon §III/IV.2 的登记。本轮是句法调整，不声称新句子为参考论文的原句，也不改变共用定义。

唯一阅读稿 main.pdf 已重新编译，仍为 13 页；第 1、2 页已检查，摘要和正文衔接正常。备份、差异与核验见 [../checks/abstract_readability_20261031/](https://github.com/RESET-cpu/afdm-gfra/tree/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_readability_20261031)。

## 2026-10-31：摘要中的活动概率与训练噪声表述

按作者要求替换两个尚未找到完整搭配逐字用例的表述，并同步中文摘要：

- `soft activity probabilities` → `posterior probabilities of activity`（活动后验概率）。Cai v2 §III-B2、式 (30) 后明确使用 `posterior probability of activity`，此处仅改为复数以对应多个设备：[原文](https://arxiv.org/html/2506.00581v2#S3.SS2.SSS2)。本稿 §III-C 的 `eq:activity-probability` 与 `eq:mixture` 给出学习分类器所得的活动后验概率估计及其混合权重作用；仍指概率值而非阈值后的活动判决，不声称学习估计精确等于真实后验。
- `white Gaussian training noise` → `white Gaussian noise used for training`（用于训练的白高斯噪声）。Shastri 等摘要和 §V 使用 `white Gaussian noise`，并明确讨论去噪器的训练噪声与输入误差之间的差异：[原文](https://arxiv.org/html/2206.05049v2#S5)。`used for training` 是说明用途的普通后置修饰，不登记为来自该论文的完整逐字短语。保留 may 对失配动机的限定，未改变后文有色噪声训练方式。

仅改变摘要的对应措辞，不改变任何技术定义或实现，因此不涉及 STMP/DU 的共用定义同步。main.pdf 已重新编译，仍为 13 页；源稿备份、差异与核验见 [../checks/abstract_probability_noise_terms_20261031/](https://github.com/RESET-cpu/afdm-gfra/tree/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_probability_noise_terms_20261031)。

## 2026-10-31：摘要补明 AFDM 选用理由并确认措辞

按作者确认，将 AFDM 优势限定为 Doppler robustness over doubly dispersive channels，并将方案提出与输入输出分析合并为同一句，以 we 为主语并列使用 propose 和 analyze。未加入相对 OTFS 的信道矩阵维度、未知系数数量或接收复杂度优势。

- **Doppler robustness over doubly dispersive channels / 双弥散信道下的多普勒鲁棒性**：Huang 等，*Prior-Agnostic AFDM Channel Estimation for High-Mobility LEO Satellite Communications Using Diffusion Models*，§I，印刷 p.2949／本地 PDF p.1，原文说明适当设计的 chirp parameters 带来该性质；本地来源为 `reference/literature/huang2026.pdf`，DOI：[10.1109/LWC.2026.3689601](https://doi.org/10.1109/LWC.2026.3689601)。本摘要用于说明波形选用动机，省去原文 strong 修饰；不声称本稿证明了全分集、完全消除多普勒影响或优于 OTFS。
- **propose、analyze、input-output relationship**：沿用 Shen 摘要及 §II-B 的既有用语与本稿前述登记；本句为作者确认的本稿表述，不作为参考论文完整原句登记。

中英文摘要同步，其余摘要内容与术语定义不变。此次定稿指当前摘要的文字和结构确认，不代表整篇论文已完成投稿前审查。源稿备份、差异及编译核验见 [../checks/abstract_afdm_final_20261031/](https://github.com/RESET-cpu/afdm-gfra/tree/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_afdm_final_20261031)。

## 2026-10-31：引言与已确认摘要对齐

按作者指定，仅落实对照意见中的前四点及第六点：统一活动后验概率用词；在贡献第 2 点补齐不施加信道稀疏或网格对齐假设、不同协方差矩阵的有色高斯训练噪声；在贡献第 3 点补明 MFLE 与 GPJD 的结构、作用及活动不确定性处理；将失配动机改为 may cause a mismatch。作者要求保留的 AFDM/OTFS 优势比较段逐字不变。

- **posterior probabilities of activity**：继续使用已核定的 Cai v2 §III-B2、式 (30) 后 posterior probability of activity 的复数形式；替换引言贡献第 3 点的 soft activity probabilities。来源、学习估计与真实后验的区别沿用上文“摘要中的活动概率与训练噪声表述”。
- **without imposing sparse or grid-aligned channel assumptions**：Huang §摘要，印刷 p.2949／PDF p.1；§III-A、式 (6) 后，印刷 p.2951／PDF p.3。指有效信道估计不依赖上述假设，不取消设备活动稀疏性，也不声称没有统计先验。
- **colored Gaussian noise with different covariance matrices；white Gaussian noise used for training**：沿用摘要与前述 Shastri §III-A、式 (28)、§III-B、式 (38)–(41)、§V 的术语依据；不同协方差矩阵的训练操作对应本稿 §IV-A、式 `eq:colored-query`、`eq:first-loss` 及其后对协方差取期望的说明，不作为 Shastri 完整原句登记。
- **multi-frame linear estimation (MFLE)、generative-prior-aided joint denoising (GPJD)**：沿用作者已批准的本稿模块名称，非声称文献已使用这两个完整名称。功能与本稿 §III-A–C、`eq:linear-mean`、`eq:exact-local-moments` 一致；inter-user interference、MMSE denoising、Gaussian extrinsic messages、activity uncertainty 继续沿用前述 Shen 摘要、Cai §III/IV 与本稿模块定义的来源记录。
- **may cause a mismatch**：与摘要统一为潜在失配的设计动机，替换 can exacerbate the mismatch；同时将 denoiser input errors、white Gaussian perturbations used for training 统一为摘要中的 denoiser-input errors、white Gaussian noise used for training。不是新增误差分布证明或实验结论。

摘要、引言贡献第 1 点、仿真结论及其余章节均保持原文。没有更改共用定义或算法，因此不需要同步修改 STMP/DU。源稿备份、差异与编译核验见 [../checks/introduction_abstract_alignment_20261031/](https://github.com/RESET-cpu/afdm-gfra/tree/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/introduction_abstract_alignment_20261031)。

## 2026-10-31：引言词面出处与使用习惯复核（未改正文）

按作者关于术语、动词、形容词及连接词是否已有文献用例的询问，直接核对 Shen、Cai v2、Ding、Huang、Wei–Yuan、Shastri 的原文，六份本地 PDF 结构预检均 PASS；另核 Menon–Ong、Bemani、Friel–Hurn–Wyse 及 Gu 等在线原文。具体章节、页码、词面匹配和语境边界见[引言语言核查](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/introduction_language_audit_20261031/LANGUAGE_AUDIT.md)。

本次明确：既有条目“依据某文献”不自动表示完整搭配在该文中连续出现。posterior probabilities of activity 是 Cai §III-B2 式(30)后单数原词的复数变化；activity uncertainty 可直接核于 §III-B1 式(16)前。denoiser-input errors 是 Shastri 摘要 denoiser input error 的连字符及复数变化；density-ratio estimator 对应 Menon–Ong §4.2 式(17)前 density ratio estimator。

Gaussian extrinsic messages 已核实 Cai §III-A/B 中 extrinsic message 的名称与 Gaussian 形式，但本轮未核得该完整连续搭配，登记为忠实的性质描述。activity-weighted channel estimates 为活动概率乘条件均值的操作描述，structured multi-frame AFDM observation model 为本文模型的限定组合；二者不登记为既有专名。MFLE/GPJD 继续按作者已批准的本文模块名称处理。

动词和连接词总体符合参考文献习惯；Against this background 另核于 [Gu 等摘要](https://arxiv.org/abs/2409.17707)，仅为用法核验，不向稿件新增引用。技术词汇可共用，但本稿第四段首句与 Ding §I（PDF p.1）几乎逐字相同，同段泄漏句与 Huang §II 式(5)后（PDF p.2／印刷 p.2950）高度接近；建议保留术语与引文、独立重述这两句。该建议尚未实施。此次只更新出处记录，不修改引言、摘要、阅读 PDF、书目或共用定义。

## 2026-11-01：按作者确认落实引言两句最小调整

作者确认保留句首 To 引出的目的状语及 AFDM-GFRA 整体潜力的论述范围；首句仅将 unleash 改为 realize、critical 改为 crucial，采用 a crucial prerequisite。该完整搭配可直接核于 Baur 等 *Channel Estimation in Underdetermined Systems Utilizing Variational Autoencoders* 的[摘要（arXiv v2；ICASSP 2024）](https://arxiv.org/abs/2309.08411v2)，原文用于描述训练时完美 CSI 这一前提。这里只作为用词先例，不将该文的技术主张移植到本文；本稿句末继续保留 Ding 引文。这是作者选择的最小措辞调整，不称为对原句的全面重述。

同段泄漏句按作者确认，以 significant power leakage 为主语，将分数 Doppler/时延置于 caused by 修饰中，再说明 can weaken the sparsity of the effective channel matrix。保留 practical propagation environments、significant、can 及 Huang 引文；技术依据仍为 Huang §II 式(5)后，PDF p.2／印刷 p.2950。

补记前一轮短语核查：with different covariance matrices 并非无人使用。[Van Wieringen 等（2021），*Penalized estimation of the Gaussian graphical model from data with replicates*，§2](https://onlinelibrary.wiley.com/doi/full/10.1002/sim.9028) 在信号与误差的多元正态分布描述中直接使用该短语。本稿训练句仍为对自身训练设置的表述，保持不变；该来源只作语言用例，不加入正文书目。

此次只改引言上述两句，摘要、AFDM/OTFS 优势段、三项贡献、其余正文和书目保持。未改变技术定义或共用定义，不同步修改 STMP/DU。备份与核验见 [../checks/introduction_final_wording_20261101/](https://github.com/RESET-cpu/afdm-gfra/tree/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/introduction_final_wording_20261101)。

## 2026-11-01：按作者确认减少引言重复段首与转折词

仅落实本轮确认的五处语言调整：OTFS 段将 to mitigate these effects 后置；STMP 段改为 The score-based turbo message passing (STMP) algorithm in ... 作主语，并用 without iterative posterior sampling 保留与上一段的联系；删除能耗、实际传播泄漏及两种采样方法共同代价三句开头的 However。OTFS 调制复杂度和 AWGN 条件两处 However 保留，作者已确认的 To realize ... is a crucial prerequisite 句保持原文。

专业术语、技术含义和引用均沿用此前核对的 Shen/Hadani、Cai 等来源。OTFS 仍以时延–多普勒域的准静态性质缓解上一段所述影响；STMP 仍以无需迭代后验采样的生成先验消息传递承接计算代价问题，后文继续解释 Tweedie 公式的作用。不新增术语、技术主张或书目条目，也不改变共用定义。摘要、三项贡献及其余章节保持。

段首 To 从三处减为一处，However 从五处减为两处；此数量仅记录本次结果，不作为写作规则。源稿备份、差异及编译检查见 [../checks/introduction_transitions_20261101/](https://github.com/RESET-cpu/afdm-gfra/tree/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/introduction_transitions_20261101)。

## 2026-11-01：引言调整后的语言出处复核（未改正文）

按作者要求复核当前引言的论证、术语、动词、修饰语和连接。沿用 2026-10-31 逐页摘录，并核对 Shen、Cai v2、Ding、Huang、Wei–Yuan、Shastri 六份源 PDF 的 SHA-256 与原结构预检旁文件一致；六份原预检均为 PASS。另重新查阅 Cai、Shen、Shastri、Baur、Van Wieringen、Gu 的在线原文，确认前述术语及短语定位仍成立。

本轮补充两项普通学术搭配的词面先例：

- **realize the full potential**：Tabak 等，*Video-Capable Ultrasonic Wireless Communications through Biological Tissues*，[摘要](https://arxiv.org/abs/1909.13172)，在描述适配信号处理与通信技术以发挥超声信道潜力时使用。这里只核实动词搭配，不把其技术对象移植到 AFDM，也不声称本稿整个 JADCE 句是该文原句。
- **substantial computational cost**：Wang 等，*Differentiable Solver Search for Fast Diffusion Sampling*，ICML 2025，PMLR 267，§1／PDF p.1（印刷 p.63549）。[出版页](https://proceedings.mlr.press/v267/wang25bh.html)及其[论文 PDF](https://raw.githubusercontent.com/mlresearch/v267/main/assets/wang25bh/wang25bh.pdf)的检索原文在讨论扩散推断需要多次去噪时使用该完整搭配。本次已读取出版页及索引返回的 §1 文本；PDF 直接浏览返回不支持的内容类型，因此不登记为完整 PDF 阅读。该来源仅补充语言先例，本稿关于 Huang/Ying 的具体计算代价仍依据两篇方法的迭代采样过程，不新增实测比较或书目。

当前核心术语与常用动词、形容词、连接词具有文献先例或已记录的概念依据；不能据此宣称所有完整动宾搭配均逐字出自同一参考论文。Gaussian extrinsic messages 继续登记为高斯形式与 extrinsic message 术语的忠实描述，activity-weighted channel estimates 和 structured multi-frame AFDM observation model 继续作为操作／模型描述；未核得完整用例不等于整个学界从未使用。MFLE、GPJD 为作者批准的本文模块名称。

论证链与已确认摘要对齐。当前两处 However 分别标记 OTFS 复杂度限制及 AWGN 适用条件；STMP 段的 without iterative posterior sampling 承接上一段采样代价；保留的 To realize 句引出 AFDM-GFRA 的 JADCE 需求。未发现必须继续改词或重排的语言问题。该结论限于引言文字与论证组织，不把本文失配／活动似然分析改称为参考文献原有结论。本轮仅补充出处记录，未修改正文、摘要、书目或 PDF。

## 2026-11-01：按作者要求修正第二章无明确出处的表达

作者本轮明确要求：“有明确替代依据的都给我换成有出处的表达，不通过的请你修正”。以已恢复的第二章原稿为基线，仅修正第二章措辞；此前撤回记录保持。完整替换对照、原词和句式的区别、章节及页码见[本轮修改记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch2_source_wording_20261101/REVISION_NOTES.md)。

- **number of physical paths、Dirac delta function、differential delay、propagation delay、common delay、beam coverage、directional cosines**：Shen，PDF p.3，Notations／§II-A 式(1)后。替换 path count、beam footprint 及以 differential delay 为主语的 subtracts。阵元间距用 **the spacing between adjacent antennas along the … axis**，依据 Li，PDF p.4，§II-B；按本稿 y/z 轴代入。
- **Assume that a total of … are allocated for pilot transmission；After removing … and applying …；Due to the sporadic access of the devices；exhibits a block-sparsity structure；we factorize the joint posterior distribution**：Cai，PDF p.4，§II-A/B，式(3)–(5)附近。分别用于导频分配、接收操作、活动稀疏性和后验分解，按本稿 AFDM/CPP/DAFT 对象代入，未将 OFDM 原模型移植为本文模型。
- **the prefix is**：Bemani，PDF p.8，§III-A 式(19)前，替换未核得的 chirp periodicity 组合。**AFDM basis waveform、integer useful samples、unit-gain path、path matrix、useful interval、integer-delay form** 等不再作为名称使用；采用既有 path gain、delay、Doppler shift、channel matrix 及原参数、索引范围直接说明。路径增益／Doppler 用词见 Shen p.3 §II-A，channel matrix 见 Huang p.2 §II；连续波形和 g 的具体公式仍为本文原定义。
- **Separating the phase evolution across frames yields**：沿用当前引言贡献第1点，替换 up to phase rotation 句式。**are assumed to remain constant during one block transmission**：Shen p.1 §I；仅借用句式表达本文原活动不变假设。
- **channel prior；rather than factorizing it element-wise**：前者沿用摘要／引言及 Cai，后者为 Cai p.1 摘要原短语，替换 training prior／retains dependence within。**are independent for different**：Li p.5 §II-C；以原 H_k、α_k 和 k 明确写出本稿原独立性假设。Bernoulli 分布继续由原概率公式给出。

本次没有新增术语、缩写或模型假设，也没有新增参考文献。15 个编号公式及 2 个无编号陈列公式保持；部分原文字改为等价的行内公式，详见修改记录。摘要、引言、其余章节、书目和插图均保持。未改变共用定义，无需同步 STMP/DU。正文 254 种英文词形已逐项匹配允许语料（closest 为 PDF 人工确认）；完整搭配另按上述来源核对。唯一阅读稿 main.pdf 已编译为 13 页并检查第二章所在第 2–4 页。

## 2026-11-01：第二章按 Shen、Cai、Xu、Ding、Wei 原段原句修订

作者进一步明确要求在原段原句基础上作最小合理替换，并补充 Xu、Ding、Wei 作为母本。本轮只修改第二章文字，按原文的技术适用性选择来源。73 个句子或公式定义单元、17 个内容组的原句、页码、实际改后文字与必要替换见[逐句对照](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch2_shen_cai_rewrite_20261101/SENTENCE_ALIGNMENT.md)，概览及完整差异见[修改说明](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch2_shen_cai_rewrite_20261101/REVISION_NOTES.md)。

- **Shen**：PDF p.3 §II/II-A 的系统场景、TSL、物理路径与差分时延段；p.4 §II-B 的定义、跨帧关系与近似不变性句；p.5 §II-C 的矩阵元素说明。保留本稿 AFDM、共同 Doppler、接收端公共时延补偿和 UPA 公式，不引入其 OTFS 模型或未采用的载荷假设。
- **Cai**：PDF pp.3–5 §II-A/B 的导频、活动、接收信号、块稀疏性、贝叶斯目标及后验分解段；p.5 Table II 为似然、约束和 Bernoulli 因子的来源；p.1 摘要为 entire channel matrix / rather than factorizing it element-wise 的来源。按本文 AFDM/CPP/DAFT、维度与原条件替换，表格转述明确标记，不冒称完整原句。
- **Ding**：本地 ding2026.pdf，PDF p.2 §II，The time-domain transmitted signal is generated through the inverse discrete affine Fourier transform…mathematically formulated as，以及 sampling interval、subcarrier spacing、AFDM modulation parameters 等定义。使用本文已有的变换符号及共轭转置约定；不是另一个 ding2026_iccdm.pdf。
- **Xu**：[Surrey 作者稿](https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/AFDM-aided-Grant-Free-Random-Access-for-LEO/991050765702346)，§II-B、印刷 p.3／PDF p.4、式(6)前，The time-domain signal can be obtained by。只采用已读取的一句；来源为在线 PDF 文本，未取得本地 PDF 或页面截图。
- **Wei**：Yiming Wei 与 Xiaojun Yuan 的 L-STMP 作者稿，PDF p.2 §II-A/B；Let…denote a known…matrix… 与 Since…this inverse problem is…underdetermined 的定义、条件句。代入本文已知导频矩阵和 Q<KN 条件，不引入混合波束成形硬件或压缩矩阵设定。

连续波形、跨帧 gq、wrap、固定前端估计等本文特有内容，按母本定义句作必要数学适配并保留原定义；不能据此声称母本文献已有本文公式。Huang、Li、Bemani 继续作为相关技术内容的依据。此次不改变共用定义，不同步改动 STMP/DU。

本轮 15 个编号公式和 2 个无编号陈列公式逐字保持。摘要、引言、其余章节、书目与七幅图等 20 个保护文件保持；本记录以前的术语条目完整保留。唯一阅读稿 main.pdf 编译为 13 页，已检查第二章第 2–4 页及后续第 5 页。原稿备份、来源哈希、词形来源和核验记录均保存在上述检查目录。

## 2026-11-01：纠正 UPA response 出处与机械定义句

作者指出 The notations a_k, t_c, and δ(·) denote… 的完整句源不成立且表述生硬。本轮确认，该句是不同符号说明的拼接，并不是 Shen 的原句最小替换；撤回上一轮对这一句及 UPA response 的合格归类。对已查本地语料未检得 UPA response 完整搭配，不能用 UPA 和 response 分别出现过来证明该搭配已被文献使用。

采用 **array response vector**，来源为 Li–Gao–Xia，PDF p.3 §II-B 式(2)后的阵列响应定义；p.4 紧接的阵列段提供 can be written as 句式和 d_v 的阵元间距定义。按本稿 a_k、y/z 轴代入，保留原阵列公式及归一化约定。物理参数、时间原点和 Dirac 函数按各自数学作用解释，不再硬并为一个 The notations…respectively 句。

同时依据 Ding §II、PDF p.2 式(1)–(2)的连续说明，连接时域信号与矩阵形式；依据 Bemani §III-A、PDF p.8 的信号式后 where 组织方式，将连续波形的辅助变量定义移至公式后；依据 Cai、Shen 的相关原句，合并参考帧定义、跨帧推导和后验条件中的重复起句。本文特有时间原点、连续波形、g_q 和固定前端条件继续明确标为必要适配，不冒称母本的相同模型。

旧整章对照保留为历史版本，受影响条目由[本轮修改说明](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch2_natural_expression_20261101/REVISION_NOTES.md)及逐行差异替代。15 个编号公式、2 个无编号陈列公式及其余章节保持；摘要未重新生成。此轮是表达和出处修正，不更改共用数学定义，无需同步 STMP/DU。

## 2026-11-01：汇总修订规范并登记剩余问题

按作者要求，将第二章修改经验整理为[用词出处与段落修订规范](WRITING_GUIDE.md)，供后续章节使用。该文档区分词形、术语、搭配、句式、段落与技术陈述的证据，列出已改实例、修订步骤及当前仍待处理的七项表达或出处问题。本轮只新增规范及索引，没有改动正文或 PDF。

补充更正：第二章的跨设备独立性以及 H_k 与 α_k 的独立性，属于本文原有建模假设。此前 Cai 关于不同列消息独立的原句，以及 Li 关于其他随机量独立的原文，至多提供相关句式；不能据此称本文这两个假设就是相应文献的相同结论。当前 channel prior for training 表达的是本文 q_tr 的用途，不能登记为 Cai 已使用的完整名称；factorizing it 的指代仍待进一步明确。这里纠正的是出处支持范围，不改变既有数学假设。

## 2026-11-01：落实写作规范登记的七项第二章修正

作者要求修正并完整展示第二章。本轮删除相邻重复的 a total of，用 We set 明示时间原点，以变量为主语说明 directional cosines，补出一条路径作为式(8)的描述对象，将 factorizing it 明确为 factorizing this prior，并用 We assume that… and that… 标明独立性假设。式(2)、(6)、(8)仅将句末句号改为逗号，以衔接 where。

逐项原文、改后文字和页码见[七项修正记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch2_remaining_fixes_20261101/REVISION_NOTES.md)。Cai §II-A/p.4 提供导频分配句，Shen §II-A/p.3 提供方向余弦与路径参数术语，Cai 摘要/p.1 及 §II-B/pp.4–5 提供完整信道处理与先验因子依据。We set 见 Cai §III-B2/p.7；独立性假设句式见 Li §II-C/p.5。后两项仅支持语言用法，本文时间原点、q_tr 的训练用途及独立性仍按本文原有设定登记，不能把不同随机对象的原句当作本文假设的技术证明。

写作规范已同步记录这七项的实际处理；上一条中“仍待处理”“指代仍待进一步明确”描述的是修改前状态。正文干净稿不加审阅粗体。未新增术语、模型条件或参考文献，不改共用定义，无需同步 STMP/DU。数学核验单独允许三处标点差异，其余公式、摘要、引言和其他章节保持。

## 2026-11-01：第二章变量英文名称逐项核查

作者澄清本轮核查的是变量的英文名称和释义，而非变量字母是否在母本出现。完整清单见 [VARIABLE_NAMES_AUDIT.md](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/VARIABLE_NAMES_AUDIT.md)。逐项区分直接原词、补查用例、适配描述、未核得完整搭配，以及正文没有单独英文命名的辅助量；没有将核查者拟出的名称反填为正文名称。

array response vector、directional cosines、common Doppler shift、AFDM modulation parameters、effective channel、channel prior、joint posterior distribution、MMSE estimate 和 posterior probability of activity 等均核到实际用例与页码。补查 pilot vector 见 Quayum §II/p.2；antenna index 见 Ke Appendix A/p.13；pilot energy 见 Tang 等 arXiv:2610.23420 §III-A/p.3、式(10)前。Tang 为本轮外部新增用词来源，三项均不能追认成 Cai/Shen 原词，也未向正文书目新增引用。

本轮仍未核得同义完整论文用例的有 transmitted symbol position、inter-frame phase rotation，以及英文函数名 wrap。known pilot matrix 与 time duration of an AFDM frame with CPP 只登记核心术语有出处、完整说明属于本文适配；q_tr 的 for training 是本文用途，不作为额外的既有专名。不能据此声称全章所有完整英文表达均已通过。

只新增清单、来源摘录与索引；第二章、其余正文及 main.pdf 均未修改。数学记号及变量字母不作调整，不改变共用定义，不涉及 STMP/DU 同步修改。

## 2026-11-01：第二章全部具名对象与技术表达扩大核查

按作者“把所有有名称的都检查一遍是不是从参考文献中来的”的要求，通读当前第二章全部正文、标题和公式中的具名算子，合并重复与单复数后登记 96 项，见 [CHAPTER_II_NAMES_AUDIT.md](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/CHAPTER_II_NAMES_AUDIT.md)。核查英文名称及同义语境，不以数学字母相同为条件；不把不同论文里的独立单词拼成完整名称后登记为原词。

结果为：83 项由当前 PDF 已引用的参考论文直接支持；1 项 antenna index 有 Ke Appendix A／PDF p.13 原词，Ke 已在 references.bib，但当前 PDF 未引用；7 项是基于已有术语的完整表达适配；1 项 pilot energy 目前仅有书目外 Tang 的已查用例；4 项 pilot resources、arrival angles、transmitted symbol position、wrap 仍未核得现有参考语料中的同义原词。后三类均不登记为完整名称通过。

补充确认 **pilot vector** 见 Arvinte §II-A／PDF p.3 式(1)后，原文使用 pilot vectors，且该论文已在当前 PDF 参考文献中；不再只依赖 Quayum。**activity states** 对应 Ding §II／PDF p.2 式(4)后 activity state，单复数变化可以通过。**discrete affine Fourier transform (DAFT) matrix** 的完整名称已重新在线核对 Xu 作者稿 §II-B／印刷 p.3（带封面 PDF p.4）式(6)后；Ding 同时提供 DAFT matrix 原词。

七项适配为 Multi-Frame AFDM Transmission、receiver compensation for the common delay、known pilot matrix、time duration of an AFDM frame with CPP、CPP relation、phase evolution across frames、inter-frame phase rotation。其核心术语或对应技术操作有依据，但完整表达不得冒称参考论文原词。phase evolution across frames 在本稿引言出现过，也不能据此证明参考论文已经使用过。

已核得的修订依据包括：pilot resources 对应 Cai PDF p.1 的 resources for pilot transmission；arrival angles 可采用 Li §II-B／PDF p.4 的 angles-of-arrival；跨帧相位可使用 Shen PDF p.5 的 phase rotation，并在句子中说明 accumulates across multiple frames。这里只登记原词，不在本轮改写正文。Cai 的 transmit power budget 不自动等于本文 pilot energy，不为满足词面审计而混淆能量与功率。

完整定位、原词上下文、检索范围、在线证据和未改正文的校验保存在 `checks/ch2_all_names_20261101`。名称出处通过不代表本文公式、假设或完整句子均来自该文献；此前任何全章“所有内容均出自已有论文”的笼统保证，以本次逐项限定替代。本轮仅更新核查文档与索引，第二章、其他章节、书目和 main.pdf 均保持，不更改共用定义。

## 2026-11-01：按作者要求替换全部可处理的具名表达

作者指令：“能替换的全部替换”。上一轮特别列出的 13 项全部落实，见[逐项替换记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch2_named_expressions_revision_20261101/REVISION_NOTES.md)。第二章采用 **resources for pilot transmission**（Cai §I/p.1）、**delay compensation**（Li §II-B/p.4）、**angles of arrival**（Li §II-B/p.4 的 angles-of-arrival）、**Transmission Scheme**（Shen §II-B/p.4）和 **phase rotation**（Shen §II-B/p.5）。接收端公共时延补偿仍是本文原有设定，不将 Li 的终端补偿模型带入。

已知导频拆为 **pilot matrix**（Cai §II-A/p.4）与 **The pilot symbols are known at the satellite receiver.**（Wei §II-A/p.2 原句仅增加 satellite）。帧时长沿用 Huang §II/p.2 的 **Each AFDM frame spans a duration of…**，代入原有含 CPP 的 T_frame=(N+N_CPP)T_s。索引说明使用 Bemani §III-D/p.10 同段的 **transmitted symbols / received symbols**，同时明示 m=0,…,M−1；不再另称 transmitted symbol position 或 antenna index，不新增 Ke 引用。

pilot energy 改为直接写原来的范数条件 ‖p_qk‖²=E_p 对所有 k、q 成立，既不将能量改称功率，也不新增 Tang。CPP relation 改为直接引用式(5)。wrap 用 β_k=2π(ν_k T_frame−⌊ν_k T_frame+1/2⌋) 展开，取值区间仍为 [-π,π)，原跨帧关系严格保持；附录 A 原 wrap 调用改为按式(9)代入估计 Doppler。floor 是原稿已使用的数学算子，此处为数学等价展开，不宣称是参考文献已有的完整公式。

跨帧说明采用 Shen p.5 的 **phase rotation…accumulates across multiple frames**，后接原有 H_k 在 Q 帧内近似不变的说明；删除 phase evolution across frames 与 inter-frame phase rotation 复合命名。术语来源与完整改句的必要适配仍分别记录，不把拼接后的整句误称为母本原句。

第二章 12 处局部替换覆盖上述 13 项，附录 A 仅一处依赖同步；除 β_k 的等价展开外，15 个编号式中其余 14 个、2 个无编号陈列式及附录 A 编号公式保持。19 个保护文件未改，引用命令和 references.bib 未改。唯一阅读稿已成功编译为 13 页，已检查 pp.2–4 与 p.11。旧审计加注历史状态，改后哈希与校验见本轮 VALIDATION.json。未改变共用定义或模型，不涉及 STMP/DU 同步改动。


## 2026-11-01：引言第一项贡献的最终措辞

作者确认以三句版本为基础调整表达，并删除 `symbol-level`。本次仅修改 `sections/01_introduction.tex` 第一项贡献；论证顺序为传输方案的目标、利用信道性质增加观测、分析输入输出关系。改后全文、历史版本与差异见 [修订记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/introduction_contribution1_20261101/REVISION_NOTES.md)。

| 当前表达及用途 | 出处与位置 | 本文适配范围 |
|---|---|---|
| `accommodates large differential delays and Doppler shifts at the satellite receiver` | 本稿引言前文已有 `the satellite receiver must accommodate large differential delays and Doppler shifts`；Shen 引言 PDF p.2 讨论卫星接收端处理大差分时延与多普勒 | 延续本文既有目标，未新增性能结论。 |
| `exploits the quasi-static properties of the effective channel over consecutive frames` | Shen 引言 PDF p.2 的 `by exploiting the quasi-static properties of the channel`；§II-B PDF pp.4–5，式(9)有效信道在 Q 个连续帧内近似不变 | 对应本文 H_k；H_k^(q)=exp(jq beta_k)H_k 中的帧间相位仍计入观测矩阵，不把 H_k^(q) 本身视为跨帧常量。完整改句为本文适配，非 Shen 原句。 |
| `obtain additional observations for JADCE` | Shen §II-B PDF p.5 首段 `gather more observations`，§II-C 式(15)后 `allows for more observations`；本文先前引言已使用 additional / more observations | 对应 Q 个导频帧对同一组 X 的观测。删去贡献中的 `increase the undersampling ratio`，直接表达增加观测的作用；不声称增加 Q 必然带来单调性能改善。 |
| `analyze the input--output relationship of the proposed scheme in detail` | Shen 引言 PDF p.2 第一项贡献第二句提供详细分析输入输出关系的表达依据；本文摘要、引言原有 `input--output relationship` | 按作者确认调整句式，并删除 `symbol-level` 限定。删除该限定不表示本稿没有逐符号输入输出关系，而是不在贡献中强调这一层次。 |

术语对象、系统模型和引用保持；第一项贡献以外的稿件内容不在本次修改范围。旧版本措辞保存在本轮 `before_final/`，不再作为当前正文登记。


## 2026-11-02：第一项贡献明确调制复杂度与有效信道表示

作者确认采用本轮讨论的三句版本。正文仅替换第一项贡献，保留传输方案目标，增加一维 chirp 调制降低调制复杂度及有效信道表示维度较低的说明，最后说明利用跨帧准静态性质增加 JADCE 观测。上一条 2026-11-01 的“最终措辞”是本轮之前的历史版本。改前文本与逐行差异见 [本轮记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/introduction_contribution1_dimensions_20261102/REVISION_NOTES.md)。

| 表达及用途 | 出处与位置 | 本文适配范围 |
|---|---|---|
| `reduces modulation complexity through one-dimensional chirp modulation` | Ding 引言 PDF p.1：OTFS 的二维变换复杂度与 AFDM 的一维 chirp 调制；Huang 引言 PDF p.1：一维 IDAFT 及相对 OTFS 较低的实现复杂度。本稿引言前文已有 `one-dimensional chirp modulation` 和 `lower modulation complexity than OTFS`。 | 将既有 AFDM 特性用于本方案；只指调制复杂度，不推导整个接收机复杂度降低，也不把该性质称为本文首次发现。 |
| `a lower-dimensional effective-channel representation` | Shen §II-B PDF p.4，式(8)–(9)的每设备、每接收天线有效信道为 H[k',l',l]；本文 §II 的有效信道元素为 H_{kmrn}，固定设备 k 和天线 m 后为 N_A×N_A 矩阵；此处用 N_A 区分本文 N 与 Shen 的 M_O、N_O。Shen §V Table I／PDF p.12 给出 M_O=16、N_O=7；本文当前 N_A=16。 | 作者确认的描述性比较，完整搭配不登记为参考论文原句或既有方法名。比较本文二维数组与 Shen 的 N_O×M_O×M_O 三维数组；在两者子载波数同为 16 时，密集系数条目为 256 与 1792。该比较不是独立物理自由度或运行时间比较，也不是额外的降维算法。本文采用设备内公共多普勒，Shen 允许路径相关多普勒；两种帧的时长及观测组织也不同，不能据此宣称任意相同总帧长下都减少系数，或运行时间减少七倍。贡献中按作者要求不点名 Shen、不展开其数组结构。 |
| `By exploiting the quasi-static properties of the effective channel over consecutive frames, the scheme provides additional observations for JADCE.` | Shen 引言 PDF p.2 的准静态性质表述、§II-B PDF pp.4–5 的连续帧有效信道，以及 p.5 的 `gather more observations`；本文原有 additional observations。 | 对应本文分离帧间相位后的 H_k；相位因子仍包含在观测矩阵中。完整句为本文适配，不将随帧旋转的 H_k^(q) 本身当作常量。 |

未改第二、三项贡献、第二章、公式或书目；上述对比范围登记于本文措辞依据，不更改共用定义，也不要求同步 STMP/DU。


## 2026-11-02：落实作者确认的摘要与引言对齐修改

作者审阅逐处建议后，将摘要传输方案句确定为简洁版，并同意其余修改。本轮更新英文摘要、对应中文摘要、引言相关工作一处、近似误差分析末尾以及第二、三项贡献；第一项贡献采用此前已确认版本。具体改前、改后文本与逐行差异见 [修订记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_introduction_alignment_20261102/REVISION_NOTES.md)。

| 位置与表达 | 已核出处 | 本轮处理与归属 |
|---|---|---|
| 摘要 `propose a multi-frame ... transmission scheme and analyze its input-output relationship` | Shen 摘要／PDF p.1：提出传输方案并分析输入输出关系；本文原摘要已有全部核心术语 | 删除 AFDM Doppler robustness 从句；不向摘要增加跨帧准静态性质、观测数或维度比较。JADCE 仍在摘要后部首次给出全称。 |
| 引言 `a three-dimensional tensor at each antenna` 与 `requires more observations for channel estimation` | Shen §II-A 末尾／PDF p.4，紧邻 §II-B 之前，原文明确有效信道在每根天线是 3D tensor，并需要更多观测以利于信道估计；具体有效信道见 §II-B 式(8)–(9) | 按作者确认增加对 Shen 所研究情形的介绍，提供第一项贡献维度比较的背景。完整改句是原段的语言适配，引用 Shen；不是新增本文的维度定理或计算量比较。比较范围沿用上一条记录。 |
| 信道后验的 Gaussian approximation、Gaussian extrinsic messages、posterior probabilities of activity | Cai §III-B1 式(24)–(27)与 §III-B2 式(28)–(30)／PDF pp.6–7；本文已有引言及第三章 | 保留“匹配后验矩一般不保留边缘似然”的分析，将活动概率误差及其对信道反馈的影响合并成一句。近似误差分析属于本文对这些步骤的数学判断，不冒称 Cai 原文对自身方法的评价。 |
| 第二项贡献的训练失配与 `colored Gaussian noise with different covariance matrices` | Shastri §III-B／PDF pp.15–16 的有色噪声条件训练；Wei §I、§III-A／PDF pp.1–2 的结构化矩阵与 AWGN 输入条件讨论；本文摘要及 §IV-A/D | 第一处信道先验学习表述保留，将第二句改成训练失配的动机与有色噪声训练做法，去掉提前介绍后验矩用途的并列分句。本文具体协方差训练分布仍以第四章为准。 |
| 摘要和第三项贡献 `a learned density-ratio estimator to obtain posterior probabilities of activity` | density ratio estimator：Menon–Ong §4.2、式(17)／PDF p.3；活动后验概率名称：Cai §III-B2 式(30)后／PDF p.7；本文 §IV-C | 使用作者确认的完整句说明减少高斯近似相关误差的动机及活动概率输出。这是本文接收机设计，不声称 Menon 或 Cai 使用了同一实现，也不将训练目标写成精确后验恢复保证。 |
| 第三项贡献的 MFLE、GPJD、MMSE denoising 和 Gaussian extrinsic messages | 模块名称沿用作者已确认命名；MMSE denoising、线性估计及外信息交换沿用 Cai §III-A/B、本文第三章；Shen 引言／PDF pp.2–3 提供模块任务及软信息交换的论证组织 | 按最终确认稿说明 MFLE 抑制用户间干扰，GPJD 使用所学先验去噪，密度比估计器获得活动概率，两个模块迭代交换 Gaussian extrinsic messages。删除同段重复的 incorporates 和 interference suppression，迭代关系仅说明一次。 |

英文正文不加入审阅粗体。未改公式、模型、算法实现、实验结果、书目或其他稿件；中文摘要只同步英文摘要的两处变动。相关定义未改变，无需同步 STMP/DU。旧条目中“第二、三项贡献未改”指当时修订范围，当前版本以本条及本轮差异为准。

## 2026-11-02：第二章按逐段审查完善论述与衔接

作者在 14 段审查后授权修改第二章。实际改句、原段页码及支持范围见 [修订记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch2_flow_revision_20261102/REVISION_NOTES.md)，对应 逐行差异（仅本地历史资料：`paper/checks/ch2_flow_revision_20261102/CHANGES.diff`）。本轮没有改变术语定义、公式或模型，也没有新增方法名。

| 表达或关系 | 已核出处 | 本文归属与修订范围 |
|---|---|---|
| 连续帧导频发送、各帧独立 modulation and demodulation、接收信号 collected for JADCE | Shen §II-B，PDF p.4 的方案概述；Cai §II-A，PDF pp.3–4 的导频和传输块；本文已确认引言 | 按原段过程顺序适配本文方案，不移植数据扩频机制。JADCE 已在引言定义，不新增缩写 |
| `To account for fractional delays, we define the transmit waveform ...` | Huang §II，PDF p.2 式(5)前的分数效应目的；Shen §II-B，PDF p.4 的 transmit waveform；Bemani §III-A，PDF p.8 离散基函数 | 明确本文采用的实数时间定义服务分数时延求值。撤除该句后将完整取整式直接归给 Bemani 的引用，标准 IDAFT/CPP 依据仍保留在前文；不宣称已找到完整原式 |
| 多帧共享 X、更多观测及待估计系数数目不随 Q 增加 | Shen §II-B，PDF pp.4–5 的准静态性质→更多观测；本文矩阵尺寸和已确认引言 | 前半沿原段论述关系，维度结论为本文公式的推论。只在矩阵模型后集中说明，不加入性能单调性保证 |
| 泄漏→完整 H_k 估计；训练信道分布作为 channel prior q_tr(H_k)，不逐元素分解 | Huang §II，PDF p.2 与 §III-A，PDF p.3；Cai §II-B，PDF pp.4–5、§I-A，PDF p.2、§IV-A/B，PDF p.9；本文 §III/IV | 泄漏句与估计方式相邻；明确 q_tr 是接收机使用的训练信道分布，仍是本文先验设定，不登记为 Cai 的完整原句 |
| `As a result`、`For Q<KN`、`MMSE estimate of X_k` | Cai §II-A/B，PDF p.4；Wei–Yuan v1 §II-B，PDF p.2；本文估计目标 | 调整因果句序、把欠定范围写成条件、点名已有 MMSE 目标，技术含义保持 |

本条及本轮记录替代受影响的旧句表述；此前逐句对照和 14 段审查仍保留为历史证据。本文时间原点、物理参数恒定、矩阵排列、跨帧公式和联合先验应继续如实登记其本文定义/假设/推导部分，不能因术语或句式有出处就统一算作原文最小替换。摘要、引言、其余章节与共用定义没有改动，无需同步 STMP/DU。


## 第三至第五章论证结构修订（2026-11-02）

按作者确认的结构修订 III–V，详见[段落关系及内容迁移](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch3_ch5_argument_revision_20261102/REVISION_NOTES.md)。新正文为本文写作，不登记为母本整段或原句的最小替换。

| 沿用术语或技术关系 | 原文位置 | 本轮用途与归属 |
|---|---|---|
| turbo message passing；Gaussian approximation；extrinsic message；MMSE denoising | [Cai v2](https://arxiv.org/html/2506.00581v2)，III-A 式 (6)–(11)、III-B1 式 (17)–(23)、III-B3 式 (32)–(42)；Minka UAI 2001 §2 式 (4)–(6)、§3 式 (8)–(10) | III 从后验因子关系引出模块，从 Gaussian 消息得到局部去噪问题。保留本文完整 Gram 矩阵及标量迹投影。 |
| posterior factorization；conditional mean；conditional covariance | Cai II-B 式 (5)、III-B1 式 (18)–(23)；[Shen v1](https://arxiv.org/html/2412.20806v1)，III-A 式 (17)–(20) | III-C 新增活动条件后验及均值/协方差积分，是本文原局部模型的 Bayes 展开。Shen 仅支持段落推进方式，不作为本文独立性假设的依据；小节标题为本文内容概括。 |
| Tweedie's formula；denoising score matching | Cai IV-A–B 式 (44)–(49)；Vincent 2011；Efron 2011；Dytso v1 §IV Proposition 1 式 (22)（上述技术源已在本文件登记） | IV-A 由后验均值确定学习对象，再说明协方差加权损失的最优条件均值及 score 重参数化。矩阵协方差、有色采样与在线 C=vI 保持原定义。 |
| Jacobian of the conditional mean；conditional covariance；Monte Carlo finite differences | [Dytso v1](https://arxiv.org/pdf/2104.01883)，§IV Proposition 1 式 (22)、Corollary 1 式 (23)，PDF pp.5–6；Metzler 2014 §V-B | IV-B 沿用输出行/输入列 Jacobian、P=JΣ、每复坐标迹归一化，以及现有中央差分与汇总方差；理想恒等式与有限网络近似分别陈述。 |
| density ratio estimation；class-probability estimation；logistic loss；posterior odds | [Menon–Ong](https://proceedings.mlr.press/v48/menon16.pdf)，§3 式 (6)–(8)、§4.2 式 (16)–(17)，pp.305–306 | IV-C 新增 log odds 式为原 Bayes 概率式的等价改写。训练类别先验修正、接收端 rho 和冻结去噪特征保持原定义；最优 logit 关系限于总体、无限制函数类。 |
| site approximation；moment matching | [Vehtari et al.](https://www.jmlr.org/papers/volume21/18-817/18-817.pdf)，§2.1 pp.5–6；Minka §2–3 | V-A 解释 Gaussian site 参数来自后验近似与输入消息相除；0<tau<v 的接受条件与保留旧 site 行为未改。 |
| Gaussian noise variance update | Vila–Schniter 2013 §III-A（既有登记） | V-B 补出固定局部近似后验的期望 Gaussian 负对数似然，再展开平方误差得到原 v_tar；不新增全局 EM 或收敛主张。 |

preconditioning、RefineNet、MDL、SVD、damping 和 stopping criteria 沿用已有出处及定义，仅迁移位置。GP-CCD-MP-DRE、MFLE、GPJD 继续采用作者已批准名称。本轮未改变共用模型或定义，无需同步 STMP/DU。


## 2026-11-02：第三章先按 Cai 的推导顺序落实论述逻辑

作者明确要求先落实论述逻辑，并将密度比估计器留在后文。第三章改为 MFLE、GPJD 两个主节；GPJD 下依次为 Channel Estimation、Activity Detection、Joint Estimation and Extrinsic Message。细项与归属见 [本轮对应记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch3_cai_logic_20261102/REVISION_NOTES.md)。上一轮 III–V 修订中的第三章段落组织为历史版本，本轮不改 IV–V。

| 术语或关系 | 已读原文位置 | 本轮处理 |
|---|---|---|
| turbo message passing、linear estimator、extrinsic message | Cai v2 III 开篇及 III-A，PDF pp.5–6，式(6)–(11) | 开篇直接说明采用 Cai 的两模块框架；线性估计保留本文完整观测矩阵。没有新造框架名，也不主张两模块结构为本文首次提出。 |
| conditional posterior、MMSE channel estimation、posterior mean / covariance | Cai v2 III-B1，PDF pp.6–7，式(17)–(23)；本文既有 Bayes 公式 | 信道小节先说明活跃条件，再给出后验及其矩。πᵥ 的比例式与原归一化式等价；没有将 Cai 的状态演化条件移入本文。 |
| posterior probability of activity | Cai v2 III-B2，PDF p.7，式(28)–(30) | 本文第三章只保留两种活动假设的似然与 Bayes 目标；密度比估计器、分类及训练目标仍在 IV-C。本文完整先验积分与 Cai 高斯近似似然的差别如实保留。 |
| Bernoulli–Gaussian distribution、Gaussian projection | Cai v2 III-B3，PDF pp.7–8，式(32)–(38) | 活动概率与条件信道矩合成后验，继续使用本文已有 μₖ、tₖ、pₖ、空间协方差及标量平均式。 |
| extrinsic variance and mean | Cai v2 III-B3，PDF p.8，式(39)–(42) | 以高斯后验近似除以输入消息，得到下一轮 MFLE 输入；保留本稿原裁剪和反馈公式。 |

小节标题是对已有技术内容的概括，不作为新增方法名称。MFLE、GPJD 沿用作者批准名称；新正文为自有表述，不登记为参考论文原句。只调整 C-STMP 的第三章说明和公式顺序，共用模型及算法定义未变，无需同步 STMP/DU。

## 2026-11-02：式 (6) 的连续波形出处补充

按作者确认，在 II-B 引出式 (6) 的原句末尾并列引用 `huang2026` 与新增的 `bemani2023thesis`，句子和公式保持原文。

- Huang，§II、式 (5)，印刷 p.2950／PDF p.2：含分数时延与多普勒的 AFDM 等效信道建模依据。
- A. Bemani，*Affine Frequency Division Multiplexing (AFDM) for Wireless Communications*，Sorbonne Université 博士论文，2023，§3.1.1、式 (3.7)、(3.9)，印刷 pp.26–27／PDF pp.52–53：统一时间和幅度归一化后，给出本稿式 (6) 在有效符号区间内的连续波形。式 (3.14)，印刷 p.29／PDF p.55，提供单周期 CPP 关系；本文多周期扩展仍属于自身推导。[官方 PDF](https://www.eurecom.eu/publication/7447/download/comsys-publi-7447.pdf)。

本条补正先前“未找到完整连续波形直接出处”的历史记录，具体推导、原式下标与区间的适配边界见[逐式核查报告](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/huang_shen_model_audit_20261102/REPORT.md)。不把多周期 CPP 扩展归为 Huang 的原有结论；本轮仅补引文，不改变共用模型或定义，无需同步 STMP/DU。


## 2026-11-02：Cai 第三章逐段对照与自有正文润色

本轮直接提取项目内 Cai arXiv:2506.00581v2 的第三章（PDF pp.5–8），按式(6)–(42)及 Algorithm 1 核对，形成 [18 项对应说明](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch3_cai_comparison_polish_20261102/01_comparison_notes.md)、带出处批注的论述稿和独立润色稿。正文采用润色稿；它并非 Cai 原文的少量替换稿。此前结构稿保留作为第一份论述稿，论述稿中的注释指向文献位置，不把自有句子登记为原文。

本轮沿用既有 MFLE、GPJD、turbo message passing、Gaussian extrinsic message、conditional mean/covariance、posterior probability of activity、Bernoulli–Gaussian 等名称和定义，没有新增方法名。Gaussian message 相除的说明对应 Cai III-A 式(9)–(11)／PDF pp.5–6；联合矩与反馈对应 III-B3 式(32)–(42)／pp.7–8。

信道协方差的引出句明确改为 conditional mean and covariance，避免将随机信道的条件协方差含糊地称为条件估计值本身的协方差。Cai PDF p.6 式(19)的平方差中心已与原图核对，和 p.7 式(23)的条件方差表示存在区别；本文原有公式一直围绕后验条件均值计算，本轮保持。反馈段说明使用经裁剪的方差，不把它描述为未经修正的精确矩匹配。

## 2026-11-02：通用推断框架、后验量学习与具体算法分章

作者确认将第三章定位为通用消息传递框架，第四章解决后验量的计算，第五章介绍具体接收算法。本条更新上述第三章的组织和模块命名位置；此前对照稿属于历史版本。修改与核验见 [本轮记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch3_general_framework_20261102/REVISION_NOTES.md)。

| 表述与位置 | 原文依据 | 本稿采用方式 |
|---|---|---|
| Turbo Message Passing Framework；linear estimation；joint denoising | Cai v2 III 标题和开篇、III-A、III-B，PDF pp.5–8，式(6)–(42) | 第三章标题采用已有框架名；正文与框图用线性估计、联合去噪说明消息交换，不引入专用模块名称。III-B 下仍依次讨论信道、活动和联合估计。 |
| 条件矩积分引出学习方法 | Cai v2 IV 开篇、IV-A，PDF p.8，式(22)–(23)到式(44)–(45) | III 末尾点出后验量的计算问题，IV 从条件均值、方差和活动概率出发。本文采用均值导数估计方差、密度比估计活动概率，未将这两项具体做法归为 Cai 原方法。 |
| 学习结果代入框架；具体算法与数值处理 | Cai v2 V-A/B，PDF pp.9–10，式(55)–(65)、Fig.3、Algorithm 2；III 的 Algorithm 1 在 PDF p.8 | V 说明 MFLE、GPJD 与 III 中两部分的对应，再给共用方差、Gaussian site、迭代与裁剪/阻尼。Cai 第三章本来就包含通用算法伪代码；本稿按论证分工借鉴，并非声称其第三章完全没有算法步骤。 |

MFLE、GPJD 仍采用作者已确认的本文名称，只调整详细定义的位置；摘要及引言中的贡献概述保持。第三章令 b 为未经裁剪的后验方差与输入方差之比，并明确正高斯外信息要求 0<b<1；第五章保留原有 clip 操作及其取值范围。裁剪是本稿原有数值处理，不登记为 Cai 的原式。第四章的导数迹估计仍保留，共用方差及下限的原公式迁至第五章。所有编号公式的数学内容保持，共用模型及实验设置未变。

全部 13 个编号式、模型和算法保留。第四章继续介绍密度比学习，第三章仅保留 Bayes 后验目标；第五章保留高斯 site 的实际表示与更新。此项写作修订不改变共用定义，无需同步 STMP/DU，摘要没有重新生成。

## 2026-11-02：第四章按后验量的求解顺序展开

本轮第四章改为四节：Bridging Score Function and MMSE Denoising、First-Order Score Matching、Variance from Conditional-Mean Derivatives、Activity Detection via Density Ratio Estimation。前两节沿 Cai 的论证顺序展开，后两节从本稿需要的方差和活动概率自然引出。方差段落直接推导条件协方差与均值 Jacobian 的关系，不使用网络替换或方法对比作为动机。详见[本轮记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch4_cai_continuity_20261102/REVISION_NOTES.md)。

| 术语或技术关系 | 原文位置 | 本稿的表达与适配 |
|---|---|---|
| first-order score；second-order score；MMSE denoising | Cai v2 IV-A，PDF p.8，式(43)–(45) | IV-A 先给条件均值，再给条件协方差。二阶 score 指对数密度的 Hessian；本文采用实表示和一般正定噪声协方差，不引入二阶网络。 |
| score matching；denoising score matching | Cai v2 IV-B，PDF pp.8–9，式(46)–(49)；Vincent 2011 的 denoising score matching 关系 | IV-B 先写涉及未知 score 的目标，再用已知 Gaussian 条件 score 得到可训练目标。协方差加权与 Sθ=Σ⁻¹(fθ−u) 是本文既有均值损失的等价表达；两个目标相差与参数无关的项。 |
| colored Gaussian perturbations；covariance-conditioned denoising | Shastri 2022 III-B；Cai v2 IV-B 的多噪声水平训练，式(49) | 从多个噪声方差过渡到本文已有的 C=v(Ra⊗I⊗Rc) 训练分布；在线仍按第三章标量方差消息取 C=vI。完整 Kronecker 形式属于本文设定。 |
| Jacobian of the conditional mean；conditional covariance | Dytso v1 IV，Proposition 1、式(22)，PDF pp.5–6 | IV-C 对本章 Tweedie 均值式求导，采用输出行、输入列 Jacobian，固定 C 得到 P=JΣ，再以 tr(P)/D 给出每复坐标方差。小节标题描述所用操作，不作为新算法名称。 |
| Monte Carlo finite differences | Metzler 2014 V-B | 沿用已有随机符号方向、中央差分及归一化。引用支持导数迹估计思路，本文所用方向分布和双侧差分形式仍明确为本稿实现。 |
| density ratio estimation；posterior odds；logistic loss | Menon–Ong 2016 §3、§4.2，式(6)–(8)、(16)–(17)，pp.305–306 | IV-D 从剩余的活动后验概率转向两种假设的似然比，再给分类训练和训练先验修正。已有白噪声采样、冻结均值特征及在线 Bayes 修正保持。 |

第四章原有九个编号公式的数学内容保持；补出协方差与二阶 score 的恒等式、加权 score matching 目标和等价 denoising score matching 目标。三项技术适配仍为有色噪声训练、均值导数方差估计、密度比活动估计，均值参数化不另列为新贡献。此前逐段审查中的第四章文字和段数属于修改前快照；新正文延续参考文献的论证顺序，不登记为逐句原文对照稿。未改变共用模型、算法或实验设置，无需同步 STMP/DU；摘要没有重新生成。

## 2026-11-02：第三、四章逐句表达修订

按作者要求保留第三、四章现有的 Cai 论证结构、技术含义和公式，参照 Shen、Xu、Huang、Ding、Wei 的适用表达逐句核对。三个子代理分别审读第三章、第四章开篇及 A/B、第四章 C/D，主代理统一复核并合并。43 个文字单元覆盖 119 个句子单元，其中调整 67 个、保留 52 个。这里的文字单元按公式前后划分，以便核查；不把每一处都算作独立排版段落。当前逐句文本及出处见 [前后对照](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch3_ch4_sentence_revision_20261102/SENTENCE_REVIEW.md)。

| 沿用或调整的表达 | 核得位置 | 实际采用范围 |
|---|---|---|
| Gaussian extrinsic messages；information exchange；incoming prior information | Shen III 开篇、III-A，PDF pp.5–7，式(20)前后及后验均值段；Wei III-B/C，PDF pp.2–3，式(9)–(12)附近 | 用于第三章信息交换、后验均值与下一轮输入的衔接。保留 Cai 的两部分框架，不移入 Shen 的三模块结构或 Wei 的可学习校准系数。 |
| normalized conditional posterior；posterior mean and covariance | Xu IV-A/B，印刷 pp.7–8，式(53)、(60)前的 Bayes 和矩描述；Cai III-A/B，PDF pp.5–7 | 第三章明确似然与先验合成条件后验，再给均值和协方差；归一化及完整先验仍为本文 Bayes 公式含义。Xu 仅提供同任务的表述关系，其离散数据检测不是本文信道先验。 |
| complex-valued channel；real and imaginary parts；Gaussian noise added to clean channel samples | Huang III-A，PDF p.3，式(7)后训练段；Wei III-C，PDF p.3，式(11)前 | 第四章由复信道引入实表示，采用对干净信道施加 Gaussian 噪声的训练搭配；本文的一般协方差、Kronecker 有色采样及在线 C=vI 保持。没有引入 Huang 的 Langevin 采样或 Wei 的残差方差。 |
| likelihood ratio；posterior activity probability；posterior moments（历史写法，见本行更正） | Ding III-B，PDF pp.3–4，式(14)–(18)；Shen III-A/B，PDF pp.6–7 | 2026-11-03 更正：这些公式支持后验概率及均值/方差关系，不证明 posterior moments 的词面出现。Shen 当前本地版本未检出 moment(s)，IV-A/PDF p.11 使用 posterior means and variances。当前稿件按具体统计量改写。 |
| cross-entropy loss；parameters kept fixed during training | Shen IV-A2，PDF p.11，式(60)–(61)；Ding III-C，PDF p.4 | 分类样本段由命令式改为训练分布陈述，再引出损失；保留先训去噪器、冻结后训练分类器的原有顺序，不移入 Ding 随后的联合解冻。 |

均值导数、随机有限差分和分类密度比的技术出处仍为 Dytso、Metzler、Menon；所用语言参照不替代方法出处。主代理将 Metzler 引文紧接 Monte Carlo finite differences，避免误读为其论文提供了本文的均值网络。没有新增方法名或缩写，也没有改变共用定义。

来源记录逐句区分原段关系、完整搭配、句式和本文定义/推导；本文特有条件不强行登记为参考文献原句。五份本地母本通过页数结构检查；Xu 本轮依据机构作者稿的网页文本索引，保留印刷页码和公式定位，不声称做了其原页图像检查。全部 25 个编号公式、图、原引用命令及 III/IV 标题保持。之前的文字对照为历史快照，以本轮前后对照对应当前正文。

## 2026-11-02：第三、四章删除防御性与重复说明

作者要求删除只为防止质疑、未推进论证的句子。本轮删除四处共五句话：III-A 与 Cai 简化条件的对照两句，IV-B 重复的一阶 score 最优解说明，IV-C 重复的完整均值映射及预条件求导说明，IV-D 确定性去噪特征不改变最优 logit 关系的补充解释。具体原句及衔接见[本轮记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch3_ch4_remove_defensive_20261102/REVISION_NOTES.md)。

未新增术语、定义或公式。固定协方差求导、不受函数类限制的均值最优解及分类器总体最优解条件保留；预条件映射仍由原公式定义。III-A 随删句去掉一个重复的 Cai 引用，公式前和其他位置的来源引用保留。上一轮逐句对照为删句前快照；当前正文以该对照结合本轮删除记录为准。共用模型和算法未变。

## 2026-11-02：第五章精简补充辩解及重复解释

按作者要求，将第三、四章的修订标准应用到第五章，保留整体算法、参数估计与数值实现、复杂度分析的原有结构。重读 Cai v2 V-A/B/C（PDF pp.9–11），据此检查学习结果代入消息传递、数值处理及计算代价之间的衔接。详见[本轮记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch5_prose_revision_20261102/REVISION_NOTES.md)。

删除 Gaussian site 恢复输入学习矩的重复一致性说明、反馈裁剪正值性的重复解释，以及已经计入复杂度公式的额外去噪调用说明。算法汇总前改为直接说明本稿式（25）、（26）、（28）之间的关系；这些连接句属于本文公式说明，不登记为参考论文原句。Gaussian extrinsic message 与联合矩的技术依据仍为 Cai III-B3 式（32）–（42），site approximation 仍引 Vehtari §2.1。未引入术语、缩写或新方法，原有 10 个编号公式、伪代码、引文和必要条件保持。

## 2026-11-02：第五章逐句表达修订与配图核对

按作者要求补做第五章与第三、四章同等粒度的语言审读。两个子代理分别核对 V-A 和 V-B/C，主代理连续复核合并后的全章。18 个公式前后文字单元共覆盖 51 个原句单元，调整 20 个、保留 31 个；另审读 Algorithm 1 的 10 项执行/控制单元及 3 项元信息，伪代码整块保持。逐句原文、改后句、来源位置和支持层次见[本轮对照](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch5_sentence_revision_figures_20261102/SENTENCE_REVIEW.md)。此前第五章精简记录为本轮修改前快照。

| 沿用的表述或关系 | 本轮核对位置 | 本文采用范围 |
|---|---|---|
| 学习估计量进入消息传递；模块功能与反馈 | Cai v2 V-A，PDF p.9，式(55)–(56)及 Fig.3；Shen III，PDF pp.5、9–10；Wei III-A，PDF p.2 | 用模块作主语说明线性估计与联合去噪，随后让学习矩进入 Gaussian site 并闭合反馈。本文既有名称和 site 公式保持；不移入参考论文的网络数量或展开层。 |
| posterior mean and variance；conditional channel moments（历史写法，已替换） | Ding III-B Step 3–4，PDF pp.3–4，式(14)–(18)；本文式(41)–(43) | 2026-11-03 更正：公式关系的支持不等同于 conditional channel moments 完整搭配的支持。当前 V-A 使用 conditional channel mean and variance；附录 A 按实际对象使用 mean and covariance。site approximation 的原词出处仍为 Vehtari §2.1。 |
| 给定参数、近似后验与方差更新 | Shen III-B 首段，PDF p.7；III-C，p.9，式(47)–(59)，尤其式(56)；Vila III-A，PDF p.4／印刷 p.4661，式(22)–(27) | 先确定前端输出，再写固定局部近似后验下的方差目标。明确第一项是 posterior mean 的平均平方 residual。保留物理噪声与局部输入方差的不同定义，不改变参数调度。 |
| variable projection；MDL；sample covariance matrix | O’Leary–Rust PDF pp.2、4，式(2)–(3)、(5)–(6)；Nadakuditi–Edelman PDF pp.2–3／印刷 pp.2626–2627，II-A 式(5)–(7) | 仍用既有相位估计与低秩空间信号加白噪声下的尾部特征值估计；改为先选秩、后求尾部均值的顺接表达。 |
| damping；channel power normalization | Cai v2 V-B1/B2，PDF p.10，式(57)–(65) | 阻尼直接表述为当前与先前消息的组合。本文归一化仍为固定训练 RMS；没有移入 Cai 依赖每个输入功率的缩放。 |
| per-iteration computational complexity；network evaluations | Cai V-C，PDF p.11；Shen III-C 末，PDF p.10；Ding III-D，PDF p.5，式(29)；Huang IV，PDF p.4，Table II 及相邻复杂度段 | 按块内一次计算、每轮矩阵与网络计算、总复杂度和存储组织句子。所有量级和网络调用次数保持本文原式，不移植其他算法的 FLOP 数或 Langevin 迭代。 |

没有新增专业名称、缩写、技术定义或共用模型。必要的固定后验、训练方差范围、site 接受、首轮阻尼例外和停止条件保留；未补回上一轮删除的解释。术语来源和语言参照分别登记，不将全文称为 Cai 原句的最小替换稿。

配图核对包括 Cai Fig.1–3／PDF pp.4、5、10，Shen Fig.1–4／pp.3、6、7、11，Ding Fig.1／p.3，Huang Fig.1–2／p.3。对应原页已渲染查看。[补图方案](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch5_sentence_revision_figures_20261102/FIGURE_PLAN.md)只建议本文系统/多帧关系及学习接收机图，不引入新方法或图示数据；本轮未改现有图。

## 2026-11-03：系统图、因子图和学习接收机图

本轮完成三张方法示意图的 PDF、SVG、PNG，沿用正文已登记术语和符号。图注、对应公式与原图位置见[绘图记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/method_figures_20261103/README.md)。不引入新的方法名称、随机变量或模型假设；正文和共用定义保持。

- **System model / multi-frame AFDM pilot transmission**：场景组织参考 Cai Fig.1／PDF p.4 和 Shen Fig.1／p.3；AFDM、UPA、CPP、IDAFT、共同活动状态、跨帧相位和有效导频来自本文第二章及其现有来源。帧长度画为示意。
- **Factor graph / reorganization / Gaussian extrinsic message**：参考 Cai Fig.2／p.5 的 vector-matrix reorganization，以及 Shen Fig.2–3／pp.6–7 的因子分组和模块消息交换。本文按 working-posterior 保留列似然、设备关系因子、完整信道先验与 Bernoulli 活动先验。第三章图只标通用线性估计和联合去噪；虚线表示同一 X 的条目重组。
- **Conditional mean / mean derivatives / finite differences / density-ratio classifier / Bayes correction / Gaussian site**：均为 IV–V 既有计算与术语。输入输出组织参考 Cai Fig.3／p.10、Shen Fig.4／p.11、Ding Fig.1／p.3、Huang Fig.1–2／p.3。方差支路使用同一个均值去噪器；分类训练和在线输入采用 vI_D；F_k 进入分类器；技术依据继续采用正文既有 Dytso、Metzler、Menon、Vehtari 引用，不由图形参照文献替代。

此前“不优先画因子图”的建议已撤回。本轮图形是按本文公式独立重画，未嵌入原论文截图或实验样本图。


## 2026-11-03 后续：方法图直接采用原图矢量元素

按作者反馈，当前三图替换为[原图改绘版](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/method_figures_source_adaptation_20261103/README.md)。Shen Fig.1／PDF p.3 的卫星、地面设备与 UPA，以及 Cai Fig.1／p.4 的资源格子、Fig.2／p.5 的因子图、Fig.3／p.10 的网络图形均直接提取矢量元素。当前图注注明 Adapted from；上节“独立重画”的说明仅对应已归档第一版。

当前因子图按原文形状保留 column-to-block reorganization（Cai 原词为 vector-matrix reorganization），作为图中的普通操作描述，不设新方法名。j=1,...,MN，x_{kn,j} 仅为 X 的行列索引记法。线性估计与联合去噪仍是第三章通用名称；第五章小图使用正文已有 MFLE / GPJD。

图中 colored-noise training、finite differences、density-ratio estimation、Gaussian site、conditional/joint moments、Gaussian extrinsic message 沿用 IV–V 已登记定义，术语依据仍为相应正文引文；图形来源与技术来源分开记录。方差从同一均值网络获得，分类器接收 R_k、v、F_k，不增加二阶网络。没有修改正文公式或共用模型。


## 2026-11-03：方法图进一步重组构图

按作者要求，在原图改绘基础上调整构图，见[本轮记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/method_figures_distinct_layout_20261103/README.md)。系统图展示已有 AFDM/CPP、共同活动状态和跨帧相位关系；因子图改为每个设备的 H_k 与 alpha_k 成对展开，原后验分解保持；接收机图改为 MFLE/GPJD 消息交换与学习更新上下两部分。所有名称、公式及条件沿用第二至第五章，不新增专业术语或共用定义。

当前直接保留的图形元素来源为 Shen Fig.1／PDF p.3、Cai Fig.2／p.5 与 Fig.3／p.10；Cai Fig.1 的资源格子已被本文连续帧示意替换，图注来源相应更新。

## 2026-11-03：方法图压缩布局与主次调整

本轮仅调整图形布局，见[记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/method_figures_compact_20261103/README.md)。沿用已登记的 linear estimation、joint denoising、conditional channel moments、finite differences、Bayes rule 和 Gaussian extrinsic message。接收机图中 Channel moments 表示 V-A 的条件矩 $\mu_k,t_k$，Gaussian site 的 $E_k,c_k$ 留在图注对应公式中；两者没有混用。未新增名称、定义或技术假设。

Shen Fig.1／PDF p.3 的卫星、覆盖椭圆与 UPA，以及 Cai Fig.3／p.10 的均值网络保留原矢量路径。因子图按 Cai Fig.2／p.5 的矩阵与节点组织重新绘制，按设备配对的因子关系保持。以上是图形参照；方法依据仍以正文原引用为准。

## 2026-11-03：系统图改为统一接入场景

本轮仅改系统图的构图，见记录（仅本地历史资料：`paper/checks/method_system_scene_20261103/README.md`）。多帧 AFDM 导频、共同活动状态、参考信道及跨帧相位仍对应第二章 Transmission Scheme；跨帧相位关系放在信道一侧。UPA、共同延迟补偿和观测矩阵均为第二章已有定义，没有新增术语。Shen Fig.1／PDF p.3 的卫星、覆盖椭圆及 UPA 矢量图形继续保留并注明来源。

## 2026-11-03：大差分时延与多普勒下的异步前导码检测候选

本节记录用户提出的独立研究候选，尚无新实验结果，不修改当前模型、算法或冻结主线。拟研究有限长度多块 AFDM 前导码的设计与联合检测，输出前导码索引、接收端到达时间和频偏；该组合是本次建议，不作为既有方法名称，也不宣称已确认新颖性。

| 原文术语与中文表述 | 论文及核对位置 | 已核对内容与使用边界 |
|---|---|---|
| preamble detection；asynchronous grant-free random access / 前导码检测；异步免授权随机接入 | Khan 等，*Preamble Detection in Asynchronous Random Access Using Deep Learning*，WCL 13(2), 279–283，2024；[机构记录](https://cris.unibo.it/handle/11585/963671)，[机构原文](https://cris.unibo.it/retrieve/6cebec1b-ac8d-44ab-95b0-b9ebecbc844e/Preamble_Detection_in_Asynchronous_Random_Access_Using_Deep_Learning_.pdf)，摘要及 §I，p.279 | 多天线异步前导码检测与 CNN 已有研究。本次核对范围为摘要和第一页，不以未读章节推断其完整能力或缺失。 |
| joint activity-delay detection and channel estimation；guard interval / 联合活跃性与时延检测及信道估计；保护间隔 | Bian、Mao、Zhang，2024 [作者稿](https://arxiv.org/html/2402.17996v1#S2)，§II，Fig.1 与式(1)前；§III 式(13) | 帧级异步、符号级同步，整数时延属于 0 到 T；导频和数据之间插入 T 个符号的保护间隔。用户专属导频和每用户至多一个时延候选不能直接解释为每用户只有一条多径。 |
| AFDM preambles；carrier frequency offset；timing advance / AFDM 前导码；载波频偏；定时提前 | Wang 等，*AFDM-Based Preamble Sequence Transmission for 6G Mobile Satellite Communication Systems*，TWC 24(10), 8445–8460，2025，DOI 10.1109/TWC.2025.3566588；[IEEE](https://ieeexplore.ieee.org/document/10996536/)，摘要 | 已有卫星 AFDM 前导码、频偏影响、首径检测及多种前导码格式。本次只核对摘要，不据此断言其未考虑某种时延范围或多用户情况。 |
| auto-ambiguity function；cross-ambiguity function / 自模糊函数；互模糊函数 | Yin 等，*Ambiguity Function Analysis of AFDM Signals for Integrated Sensing and Communications*，2025 [作者稿](https://arxiv.org/html/2507.08293v1)，§III-A 式(15)–(16)，§III-B–C、§IV | AFDM 子载波的局部峰、全局类周期结构及无模糊区域已有分析。将有限时长多块前导码的自、互模糊函数作为随机接入设计指标是本次适配；单目标结论不直接保证多用户可辨识性。 |
| chirp-based pilot；OMP-SIC / 基于啁啾的导频；正交匹配追踪与串行干扰消除 | Xu、Guo，IEICE Communications Express 14(9), 349–352，2025；[原文](https://www.jstage.jst.go.jp/article/comex/14/9/14_2025XBL0076/_pdf/-char/en)，§II 式(1)，§III-B 式(6)–(10)，§IV-B，p.350 | 双啁啾索引和候选集缩减已有工作。§IV-B 使用最大时延不超过单段长度四分之一的条件，§II 模型没有显式频偏项；该判断仅限已读模型与算法。 |
| dual-offset chirp；segmented correlation and index reorganization-aided orthogonal matching pursuit / dual-offset chirp 保留原词；分段相关与索引重组辅助正交匹配追踪 | Li 等，*Dual-Offset Chirp-Based Random Access Preamble Design and Detection for AFDM-Enabled LEO Satellite Communication Systems*，ICC 2026，DOI 10.1109/ICC59461.2026.11586984；[作者机构记录](https://openresearch.surrey.ac.uk/esploro/outputs/conferenceProceeding/Dual-Offset-Chirp-Based-Random-Access-Preamble-Design/991148958202346)，摘要 | 已有不对称频移啁啾拼接、码池扩展及多用户识别和定时估计；SCIR-OMP 是作者名称。仅核对机构摘要；增加第二段啁啾、峰配对或 OMP 本身不能作为本项目创新。 |
| multiple hypothesis testing；observation window；Mirage detector / 多重假设检验；观测窗口；Mirage 检测器 | *Mirage Detector: A Reliable Multiuser Preamble Detector for 6G-NTN*，OJCOMS 7, 3724–3744，2026，DOI 10.1109/OJCOMS.2026.3679839；[IEEE 摘要](https://ieeexplore.ieee.org/document/11460211/)，[机构作者稿](https://orbilu.uni.lu/bitstream/10993/68160/1/Mirage_Detector_A_Reliable_Multiuser_Preamble_Detector_for_6G-NTN.pdf)，§IV-B、Algorithm 2、p.11 的可检索原文 | 大差分时延下动态移动窗口核查疑似峰已有工作；滑动窗口或重定位核验本身不能作为新算法。 |
| off-grid model / 离网模型 | Huang 等，*Joint Terminal Identification and Channel Estimation of Asynchronous Grant-Free Access for LEO Satellite-IoT Network*，TCOMM 74, 9125–9137，2026；[IEEE 摘要](https://doi.org/10.1109/TCOMM.2026.3693170) | 摘要已有时延、多普勒、联合终端识别与信道估计及 Taylor 展开离网模型。增加分数偏移或联合估计变量本身不足以建立新颖性。 |

候选范围与论证约定：

- 用户的“大差分实验”按“大差分时延”理解。`src/system/config.py` 给出带宽 480 kHz、N=16、时延支持上限 699 微秒、频偏上限 41 kHz；有效块时长为 33.333 微秒，时延上限约为其 20.97 倍。这是配置计算，不是实验结果，也不是包含 CPP 的帧时长比值；支持矩形的每个角点不一定同时满足某个具体卫星几何场景。
- 区分差分传播时延、用户发射起点偏移与多径时延扩展。未知发射时刻时，前导码只能辨识发射时刻与传播时延之和，即接收端到达时间；不能声称分别估出传播时延和定时提前。估计频偏可能同时包含多普勒与振荡器误差。
- 拟比较 Q=2、3、4 个有限训练块，至少考察两种已知 AFDM chirp 参数设置，以及用户相关的导频索引和块间相位；固定总时长、总能量和占用带宽，不能把增加块数本身当作贡献。优化完整波形的非主瓣自模糊函数和互模糊函数；若到达范围为 [0,T_a]、频偏范围为 [-F_max,F_max]，候选差集合为 [-T_a,T_a] × [-2F_max,2F_max]。
- 对离散单啁啾内部有效样本，取 s[n]=exp(j2π(c1 n²+m n/N))。整数时移 d、归一化频偏 f 经过相同二次相位去除后，有效频率为 m/N+f−2c1d（模 1），常数相位可并入未知增益。这是本次由二次相位展开得到的说明性恒等式；不代表任意连续时间 AFDM、有限包边缘或分数时延都遵循单峰近似。不同块参数是否足以排除给定范围内全部模糊解，仍需分析完整有限波形。
- 原始采样检测须使用有限支持、线性时移和真实脉冲成形；包起点来自扫描，不能按真值分段或将跨块到达替换成循环时移。各块联合拟合同一个到达时间、频偏及满足相干条件的天线信道。若任意独立拟合每块复增益，会丢失相位区分信息；多径应共享包起点并具有路径相对时延，不能每条路径都计为用户。
- 不以长保护区覆盖总差分时延作为前导检测前提，是待验证目标。必须生成其他用户数据与前导码的重叠，计入缓存、等待和搜索成本；不能由前导检测结果直接宣称数据阶段也不需要长 CPP。若用高斯近似处理重叠数据，应标记近似并检验失配。
- 初始采用用户与前导码一一对应的码本。共享前导码时输出仅为前导码索引；相同波形、起点和频偏的两个发送不能凭前导码保证身份区分。多天线收益须在项目 UPA 几何和相关信道下检验，不默认任意用户可空间分离。
- 主要验证固定整体虚警预算下，完整前导码的索引、起点和频偏联合检测成功率及总开销。成功检测条件下的误差单列，保留漏检与错误关联；阈值在完整扫描流程中校准，不能以固定单搜索单元阈值比较不同搜索范围。
- Wang 2025 与 Li 2026 的完整差异仍需全文核对；本次未启动批量实验或训练，不承诺性能收益和论文录用层级。

## 2026-11-03：Li 前导码与 Khan 异步检测的组合范围

本条补充候选研究的来源核对，不修改当前论文模型、算法或实验配置。

| 术语或操作 | 核对位置 | 适用范围 |
|---|---|---|
| asynchronous grant-free random access；preamble detection；CNN / 异步免授权随机接入、前导码检测、卷积神经网络 | Khan，*Deep Learning for Massive Multiple Access in 6G*，2024 博士论文，[机构全文](https://amsdottorato.unibo.it/11414/1/PhD_Thesis_Final.pdf)，§3.2 pp.52–54、式(3.1)，§3.3.1 pp.54–56、式(3.2)–(3.5)；为该作者 WCL 研究对应章节，不能把博士论文章节编号作为期刊论文编号 | 所有用户共用前导码；包异步但符号同步；Rayleigh 块衰落；模型显式包含其他用户的数据。CNN 输入接收样本实虚部及参考序列，输出前导码有无的二分类。不是多用户身份、到达时刻、频偏的联合估计器。 |
| dual-offset chirp；joint user identification and TA estimation / 保留原词；联合用户识别与定时提前量估计 | Li 等 ICC 2026，[作者机构摘要](https://openresearch.surrey.ac.uk/esploro/outputs/conferenceProceeding/Dual-Offset-Chirp-Based-Random-Access-Preamble-Design/991148958202346) | 已核实的是 DAFT 域设计、不对称频移 chirp 拼接及 SCIR-OMP。没有核实全文，不能将其改述为给每个 UE 任意分配不同 c1/c2，也不能断言其未覆盖大多普勒。 |

- 拟固定 Li 类前导码集合，先研究检测端：在扫描得到的候选位置计算各段相关响应，使用 CNN 判断候选前导码是否存在，再依完整有限波形估计到达时刻和频偏。允许同一窗口存在多个用户，不采用只允许一个用户胜出的分类输出。以上为本项目候选操作，不是已有算法名称或已验证贡献。
- 在一段观测内任意未知发射时刻与固定差分传播时延可合并为到达时刻。因此，单纯放大差分时延不必改变局部检测问题；须说明缓存、扫描范围、检测等待或保护时间约束，才能量化大时延代价。前导码检测输出的到达时刻不等于单独可识别的传播时延。
- 现有代码的 CPP 覆盖最大差分时延；异步突发检测须另行生成含数据重叠的时域流。不能按真值裁剪或直接把原有对齐导频矩阵当作扫描输入。Khan 已包含数据重叠，不能把加入该项本身宣称为新贡献。
- 直接用 Li 前导码重新训练 Khan 类网络应作为对照。候选方法须在同一波形、带宽、能量、观察时间、训练预算及整体虚警预算下，证明新增结构对用户误认、漏检或总搜索成本有独立收益。未启动实验或训练。

## 2026-11-03：系统图精简标注

对照 Cai Fig.1／PDF p.4 与 Shen Fig.1／PDF p.3，系统图删去推导等式和解释性长句，见[记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/method_system_minimal_20261103/README.md)。链路标签使用第二章已定义的 terrestrial-satellite link（TSL），来源为 Shen Fig.1 及本文 II-A；其余 UPA、AFDM、CPP、设备与帧索引均沿用已有定义。模型、公式和技术术语没有变更。

## 2026-11-03：三张方法图编入第二、三、五章

系统图、因子图和学习接收机图已编入正文，见[插入记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/method_figures_integration_20261103/README.md)。正文只增加或调整图引用，图注使用已有系统模型、factor graph、Gaussian extrinsic message、conditional/joint moments 等术语，保留 Shen Fig.1 与 Cai Fig.2–3 的图形改绘出处。方法依据与模型公式没有变化。三张图及七幅实验图文件保持原字节。


## 2026-11-03：方法图单栏与紧凑布局

系统图与因子图按单栏宽度重新排布，学习接收机图保留双栏并缩短支路，见[记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/method_figures_column_layout_20261103/README.md)。图中术语、符号及来源沿用既有登记。因子图以省略号表示中间矩阵列，不改变 X 的行列索引、变量或因子关系；第三章继续使用 linear estimation、joint denoising，第五章继续使用 MFLE / GPJD。没有新增专业名称、模型假设或共用定义。


## 2026-11-03：第六章实验组织与结果分析

见[逐段来源与证据](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch6_revision_20261103/PARAGRAPH_EVIDENCE.md)及[修订记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch6_revision_20261103/REVISION_NOTES.md)。实际读取 Cai v2 VI-A–C / PDF pp.11–15、Shen V / PDF pp.12–13 以及 III-C / PDF p.9；借鉴去噪、完整接收机、参数变化与跨信道评价的组织，本文数值与解释全部对应自己的保存结果。

- **density ratio estimation、posterior probabilities of activity、Gaussian approximation**：沿用本文 III–IV 与前述 Menon–Ong §3/§4.2、Cai III-B 的登记。C 节标题使用 Effect of Density Ratio Estimation；表中的 activity evidence 描述当前两种似然比计算方式，不是新增方法名称。解析近似来自本文 Gaussian site 公式，不能称为真实学习先验的精确边际似然。
- **channel denoising、NMSE、AER、channel model mismatch、without retraining**：Cai VI-B/C、Fig.4–11 / PDF pp.12–14；Shen V / PDF p.12。采用既有指标与评价概念；本稿有色训练方案的高低 SNR 取舍、AER 消融以及跨 NTN-TDL 结果均为本文结果，不是参考论文结论。
- **phase rotation、conditional moments、expected squared residual**：Shen III-C 式(47)–(54) / PDF p.9 与本稿已有 `PHASE_MESSAGE_GEM.md` 的固定 Gaussian 消息推导。第五章及附录新增的是已选定实现的操作说明：固定反馈消息后细化相位，更新观测矩阵，并重置相应历史；共同帧间斜率约束和每设备常相位的处理是本文适配，不称 Shen 原算法复现。
- **SVD、coordinate updates、relative-change tolerance**：沿用第五章和既有相位推导中的数值操作名称。20 次迭代检查间隔、80–600 次迭代及输出变化阈值来自本项目选定配置，不是文献推荐参数。

仅同步当前 C-STMP 稿件的实验叙述与实际实现，没有新增共用模型定义，也未改变 STMP / DU 稿件。此前“所有主图均为已知相位”“SNR 每点 1000 场景”的记录属于历史版本；当前主 SNR 图为 500 个配对场景，并明确区分已知与估计相位。


## 2026-11-03：系统图对齐与因子图交叉排列

系统图修正终端圆周及 UPA 局部展开的几何位置。因子图恢复 Cai Fig.2 / PDF p.5 上方 H_k、下方 alpha_k 的分组排列，交叉位置不设节点；每个设备因子仍连接自己的 X_k、H_k、alpha_k，与本文式(14)一致。Shen Fig.2 / PDF p.6 与式(20)只用于核对交叉边的表示方式，未引入其变量或依赖。所有术语、模型和方法定义保持；见[修正记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/method_figures_alignment_crossing_20261103/README.md)。


## 2026-11-03：第六章重复限定精简

见[记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch6_prose_streamline_20261103/REVISION_NOTES.md)。本轮删除重复的实验范围说明、运行时间免责声明与附录提示，未新增专业术语或文献主张。保留训练配置、相位条件、样本和能量设置，以及不利结果；来源沿用前一条第六章修订登记。此前逐段对照是精简前版本，当前措辞及删除位置以本轮 CHANGES.diff 为准。


## 2026-11-03：因子图改用设备块变量

图中 device blocks X_k、likelihood factor、channel/activity priors 沿用第二章式(13)–(14)及第三章现有定义。删除完整矩阵与逐元素索引后，每个 p(y_j|x_j) 作为所有设备块对应列条目的函数，与全部 X_k 连接；设备约束因子仍只连接 X_k、H_k、alpha_k。右侧先验分组的图形参照仍为 Cai Fig.2 / PDF p.5，图注保留该出处。未增加术语、方法名、随机变量或模型假设，见[记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/factor_graph_device_blocks_20261103/README.md)。

## 2026-11-03：AFDM–OTFS 表示、资源与调制比较

详见[公式与术语依据](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/afdm_otfs_comparison_20261103/SOURCES.md)。

| 术语 / 表述 | 原始出处与位置 | 本稿用法及边界 |
|---|---|---|
| discrete affine Fourier transform / 离散仿射傅里叶变换；inverse DAFT / 逆 DAFT；chirp-periodic prefix / 啁啾周期前缀 | Bemani et al., TWC 2023，[原文](https://arxiv.org/html/2204.12798v2)，II-B 式 (16)、III-A 式 (18) | 第二章及附录 B 沿用原定义；L 帧的 FFT 与啁啾乘法数量是本文对矩阵分解的直接计数。 |
| effective channel / 等效信道；multi-frame transmission / 多帧传输；phase rotation / 相位旋转 | Shen et al.，[原文](https://arxiv.org/html/2412.20806v1)，II-B 式 (3)、(7)–(10) 与 Proposition 1 | 原文子载波数 M、时隙数 N 改记 N、L，M 表示本文天线数。条目数 MN² 与 MLN² 仅比较显式稠密表示，不称为自由度或导频节省。共同多普勒后的 OTFS 分解为本文受限模型推导。 |
| inverse symplectic finite Fourier transform / 逆辛有限傅里叶变换；rectangular waveforms / 矩形波形；transmit windows / 发射窗口 | Xu et al., 2019，[原文](https://arxiv.org/html/1911.08133v1)，II-A 式 (1)、II-B 式 (4)–(5) | 单位发射窗口下，OFDM 逆 DFT 与 ISFFT 的子载波 DFT 消去；用剩余的 N 次 L 点逆 FFT 比较调制成本。不从“一维对二维”推出普遍复杂度优势。 |

本文的共同多普勒、分数时延和帧间相位模型保持原定义。仅为比较引入 OTFS 时隙计数 L 和匹配的帧数 Q_A、Q_O，未新增方法名称。基线及评估差异移至附录 C，密度比消融沿用原始配对统计。STMP 与 DU 稿件无共用定义变更。

## 2026-11-03：当前全文变量名称、符号来源与重名检查

完整覆盖及位置见 [NOTATION_AUDIT_20261103.md](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/NOTATION_AUDIT_20261103.md)。本轮仅检查当前 I–VI、附录 A–C、算法与图表；未修改正文、图、PDF 或共用定义。

重新核实：Cai v2 §II-A/Table I（PDF p.4）的活动先验使用 lambda、导频使用 q_ktn；Shen §II-B 式 (2)–(10)（PDF p.4）的子载波数、时隙数使用 M、N。本文 rho/P/Q 和比较中的 N/L 是适配，不登记为原符号。Dytso §IV Proposition 1 式 (22)（PDF p.5）、Menon–Ong §2.2/§3/§4.2（PDF pp.2–3）、Vehtari §2.1（PDF pp.5–6）、Karras Table 1/§5 支持相应数学概念，而不支持“本文 J_m、z_phi、E_k/c_k、矩阵 B_Sigma/K_Sigma/O_Sigma 都是原文原名”的说法。详见报告中的原文链接与来源边界。

实际发现 L（OTFS 时隙数/噪声样本数）、R（去噪观测/协方差因子）、G（随机矩阵/前缀长度）、xi（时间参数/相关系数）、tau（时延/汇总方差）、h_k（物理信道/前端导频响应）的跨章复用，并登记首次定义和索引问题。重命名方案尚未实施，不将建议的新下标包装为已有方法名称。MFLE/GPJD 继续按作者已批准的本文名称处理。

VI-A 仍称 E_p 为 pilot energy。该名称可在 Tang 等 [arXiv:2610.23420 摘要](https://arxiv.org/abs/2610.23420) 核得，属于书目外论文用例；Cai 的 transmit power budget 不能作为同一完整词面出处。第二章曾改为直接数学定义，不等于第六章已完成同样的出处处理。本轮只如实登记，没有新增书目条目或改变能量定义。

## 2026-11-03：直接相位估计候选的公式与来源

见 [PHASE_DIRECT_20261103.md](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/PHASE_DIRECT_20261103.md) 及独立候选实验目录；本条只登记新候选，不改变论文已选定模型。

- **phase rotation、EM update、posterior mean/variance、projection onto the unit circle**：Shen et al., III-C 式 (47)–(54)，PDF p.9，Algorithm 1（pp.9–10）；[原文](https://arxiv.org/html/2412.20806v1#S3.SS3)。零角度初始化对应 Algorithm 1 初始 C^{phi,l}=C^l。共同帧间斜率约束、Gaussian 反馈条件矩、固定第零帧及斜率拟合均为本项目 AFDM 适配，不称为 Shen 完整算法复现。
- **Gaussian posterior、log marginal likelihood**：沿用本稿已有 Gaussian 消息表述；Rasmussen–Williams, GPML §2.1.1 式 (2.6)–(2.8), p.9，及 Ch.2 式 (2.30), p.19，[公式核对](https://gaussianprocess.org/gpml/chapters/RW2.pdf)。复数多列形式、Q 阶条件矩及训练二阶矩构造为本项目推导，书中实数公式不是该 AFDM 算法的来源声明。
- **coordinate updates、stationary points、relative tolerance**：沿用现有相位推导与数值求解表述。新代码比较三角多项式驻点及当前点；不引入新的方法名称，也不从固定 Gaussian 目标下降推断全接收机或相位真值收敛。
- 分组初始化仅作为开发近似：输出行按固定训练协方差块的相关强度分组，省略组间相关性；代码调用 SciPy `linkage(method='average')`，其距离更新定义见[官方文档](https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html)。该分组不是本文命名的新算法，完整单组候选不进行此分组。

理论等价检查与学习接收机统计实验分开记录；失败初值、迭代上限、检测错误均保留。无共用系统定义改变，故不修改 STMP/DU 的术语记录。

## 2026-11-03：参照 Cai、Shen 实施当前稿符号统一

作者在全文符号检查后要求参照 Cai、Shen 实施处理。直接复查 Cai v2 §I-C / PDF p.3、§II-A / Table I / PDF p.4，以及 Shen Notations / PDF p.3、§II-B 式 (2)–(10) / PDF pp.4–5；详见[本轮实施记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/notation_cai_shen_20261103/REVISION_NOTES.md)。本条更新此前“尚未实施”的状态，旧核查保留为修改前证据。

- **符号组织依据**：Cai 的字体约定、常用符号表及 pri/post/ext 消息上标；Shen 的矩阵/向量字体、虚数单位、领域上标及就地定义。本文增加 Notation 说明及 Table I，保留现有主符号，不把 AFDM 张量维度和本文辅助下标归为两文原定义。来源：[Cai v2](https://arxiv.org/html/2506.00581v2)、[Shen](https://arxiv.org/html/2412.20806v1)及本轮记录中的本地 PDF。
- **已区分的量**：汇总条件方差 tau^post、噪声估计样本数 N_s、前端导频响应粗体 h_k^p、共同前缀长度 N_pre、训练相关因子粗体 R_corr / Z_tr / xi_corr、有限差分步长 delta_FD、历史平滑权重 zeta_hist。corr、tr、FD、hist、p、pre 是本文说明性上下标，不是新增算法或技术名称，也不声称逐字取自参考论文。
- **字体与定义**：复扰动协方差 C 和因子 R_a/R_c 统一粗体；单位虚数用直立 j；定义可训练参数 theta/phi、零点概率测度 delta_0、随机方向数 L_z、机器精度 epsilon_mach、Doppler 搜索界和裁剪算子。沿用当前引用和公式含义，没有引入新的专业术语。
- **实现与符号对应**：明确 j=mN+r+1 和 n 最快的张量展开顺序；经现有训练噪声代码及小尺寸 Kronecker/复实展开恒等式核对。独立去噪 Gaussian 基线和接收机初始化均读取 normalized_training_second_moment，故 P_tr 统一为 V-A 已定义的 hat P_H，而非凭名称相近合并。
- **保留的区别**：p/rho/pi_tr/p_k、物理/消息/后验方差继续分别定义；局部求和哑元、不同完整下标的量允许复用。MFLE/GPJD 及作者确定的接收机名称保持。pilot energy 的书目外用例边界仍按上一轮核查记录，不追加不必要的归属声明。

正文、Algorithm 1、Fig. 3 和阅读稿同步。71 个公式块经声明的记号逆映射核对一致，第六章数字和七幅实验图保持；当前 PDF 为 18 页。仅修改本稿记号与定义说明，不改变共用模型、算法计算、配置、权重或实验结果，因此无需同步 STMP/DU 的模型定义。


## 2026-11-03：撤回符号表，保留重名修复与正文必要定义

按作者最新要求，删除上一轮新增的符号表及扩写的 Notation 段，恢复原来的简短篇首说明。重名修复、同义量统一、索引和首次定义保留；虚数单位、转置、单位阵与对角算子移至第二章首次使用处简短解释。具体见[回退及核验记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/notation_inline_only_20261103/REVISION_NOTES.md)。

上述运算的含义与来源仍沿用 Cai §I-C / PDF p.3、Shen Notations / PDF p.3 的既有登记，但不再采用蔡文的符号表组织方式。没有新增专业术语、方法名、模型或共用定义。71 个公式块与回退前相同，算法、图和实验内容保持，旧符号表记录仅作为历史版本保留。

## 2026-11-03：正文保守删减与第六章分析精简

按作者要求保留摘要、引言、第二章和全部附录；第三至五章仅删除重复说明，第六章 B–E 精简重复报数和机理复述。直接对照 Cai v2 §VI-B / Fig.4 / PDF p.12、§VI-C / Figs.5–11 / PDF pp.12–14 的分析组织；既保留其收敛分析较详细的事实，也参考设备数、活动概率和导频数分析采用少量代表性数值的写法。出处只用于编辑尺度，不作为本稿结果来源，见[对照与核验记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/content_trim_cai_20261103/REVISION_NOTES.md)。

本轮没有新增专业术语、方法名称、公式或模型定义，保留既有引用和必要的变量说明。全部图表、实验设置和不利结果保持；没有共用定义变化，无需同步 STMP/DU。当前完整稿由 18 页降为 17 页，附录 C 仍保留。

## 2026-11-03：第六章改为总体趋势分析

按作者要求进一步精简八处结果解释，并删除回落、交叉等局部现象的专门分析。分析粒度对照 Cai v2 §VI-B–C / PDF pp.12–14（Figs.4–10）及 Shen §V / PDF pp.12–14（Figs.5–9）；两篇在核心比较处也会展开，不能概括为均无细节。具体范围及核验见[本轮记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch6_trend_summary_20261103/REVISION_NOTES.md)。

error floor 沿用通信性能分析的既有术语，Shen PDF p.14 / Fig.7 分析使用 error floors 描述 SER 曲线；本稿用于去噪 NMSE 平台，对应本稿 Fig.4 的现有曲线，是指标适配而非借用 Shen 的实验结论。其余名称、指标与变量沿用原稿，无新增方法或共用定义。当前文字只概括既有结果，图表、设置和附录全部保持，完整稿为 16 页。

## 2026-11-03：相位更新调度、局部步幅与不确定性的文献核对

本条为下一候选的研究依据，不改变论文已选定算法、配置或模型。完整书目、原文位置、适用限制及既有实验对应关系见 [SOURCES.json](../../reference/reviews/phase_update_20261103/SOURCES.json)。本轮没有运行新的接收机实验或训练。

| 术语／操作 | 原文与位置 | 本项目适用范围 |
|---|---|---|
| soft information、turbo synchronization、APP | Noels et al., 2005，[原文](https://telin.ugent.be/~hs/full/j17.pdf)，§3.2 p.121；§4 式(22a)–(22b) p.122 | 两次同步更新间需要足够可靠的检测／解码软信息；不是“越晚越好”，也不提供本项目固定轮数。本文活动与信道推断是不同模型。 |
| global iterations、decoder iterations / 全局迭代、译码器内部迭代 | Krishnan et al., TSP 2015，[机构作者稿](https://publications.lib.chalmers.se/records/fulltext/217287/local_217287.pdf)，§VII–VIII，PDF第10–13页，Table I、Fig.7；DOI 10.1109/TSP.2015.2420533 | 2026-11-04核对：LDet为检测器与译码器之间的迭代数，LDec为LDPC内部迭代数；(2,30)、(15,1)、(10,1)对照用于说明调度的性能／复杂度权衡，不能把30解释成本项目相位更新间隔。与Noels、Shen的逐项证据见[核查记录](../../reference/reviews/phase_update_schedule_20261104/VERIFICATION.md)。未改变共用定义或既有算法。 |
| Gaussian mixture (GM)、soft replica、MMSE criterion、second-order Taylor approximation | Ito et al., TWC 2025，[原文](https://ir.library.osaka-u.ac.jp/repo/ouka/all/101415/IEEETransWirelessCommun_24_3_1898.pdf)，§III-A pp.1903–1904；式(38b)、(46)–(50) pp.1906–1907 | 方差加权复数相位软值和旧 CFO 附近的局部修正可作参考。式(46)采用 MMSE criterion，方差式(49)–(50)使用 EM；不将其混称为精确相位 EM 更新。完整方案保留多候选，不是无候选搜索初始化。 |
| SAGE、ECM、CFO estimation、phase tracking | Wang–Liew, TVT 2016，[原文](https://arxiv.org/html/1505.00082v3)，§III-B/C 式(7)–(9)、(26)、(29)–(35)，Appendix B 式(40)–(42) | 参考软信息驱动的逐块局部修正；其前导、编码和独立块相位假设不直接移植。我们的坐标更新不因此改名为 SAGE 或 ECM。 |
| phase rotation、posterior mean/variance、unit-circle projection | Shen et al.，[原文](https://arxiv.org/html/2412.20806v1#S3.SS3)，§III-C 式(47)–(54)，Algorithm 1 | 沿用前次核对。自由相位变量不同于共同斜率；一般耦合二次型的无约束解再投影不保证精确条件最优，此限制为本文数学判断。 |
| generalized expectation-maximization、conditional update | Fessler–Hero, TSP 1994，[原文](https://web.eecs.umich.edu/~fessler/papers/files/jour/94/pre/tsp,sage.pdf)，§II-B/C 式(2)–(7)、Theorem 1 | 合法隐藏数据空间与真实条件期望下，只需改善条件目标。不能据此声称当前学习接收机有共同单调目标；不采用有勘误的 Theorem 2 速率论证。 |
| adaptive damping、Bethe cost、moment matching | Vila et al., ICASSP 2015，[原文](https://arxiv.org/pdf/1412.2005)，Table 1 R12–R18，§2.1–2.2 式(3)–(11) | 借鉴按明确代价回退步幅；当前学习去噪器不能直接提供该文的 Bethe cost。相位步幅控制与现有消息阻尼是不同操作。 |

Neal–Hinton [作者稿](https://www.cs.toronto.edu/~hinton/absps/emk.pdf) pp.4–5 式(2)–(5)用于核对近似分布、下界与似然的区别；Chrétien–Hero [作者稿](https://arxiv.org/pdf/1201.5907) §5.2–5.3 式(30)–(32)用于核对信赖域对原目标的验收要求。仅检查冻结消息目标，不能继承原似然保证。Sarkar et al. [原文](https://phil-schniter.web.app/pdf/tsp19_badvamp.pdf) §IV-B/D 作为参数变化、方差调节和消息阻尼的补充依据，不作为当前接收机收敛定理。

本次建议的操作用普通描述“限制相位增量的局部更新”，不引入缩写或新方法名称。令 t_q=q−(Q−1)/2，同时限制常数与斜率增量 max_q|δa+t_qδβ|≤Δ；一轮局部条件更新后返回信道／活动推断，失败允许零步。该约束和与现有参数的映射为本文适配，详见 SOURCES.json；并非上述论文原公式。稳定性不等于准确性，固定条件目标下降也不等于真实相位或 NMSE 改善。初值失效与精修步幅应分开验证；没有改变共用定义，故不修改 STMP/DU 记录。

## 2026-11-03：局部相位更新的完整推导与独立实现

作者进一步要求完整推导并实验验证。推导见 [PHASE_LOCAL_20261103.md](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/PHASE_LOCAL_20261103.md)，独立实现为 `src/algorithm/C_STMP_phase_local_20261103`，计划与结果位于 `result/candidates/c_stmp_phase_local_20261103`。不改冻结主线；实验是否达标以该目录最终报告为准。

- **Armijo condition／充分下降条件、modified steepest descent**：Larry Armijo, *Minimization of Functions Having Lipschitz Continuous First Partial Derivatives*, Pacific Journal of Mathematics 16(1):1–3, 1966，DOI 10.2140/pjm.1966.16.1；[出版方原文](https://msp.org/pjm/1966/16-1/pjm-v16-n1-p01-p.pdf)，正文 p.2 Corollary 2 式(2)，PDF 第3页。本文转换为最大化问题的充分上升，并采用正定化方向；一般参数形式和局部步长存在性证明为本次推导，不宣称继承原文全局最优条件。
- **Gaussian conditional moments、generalized EM、posterior covariance、Hessian**：沿用前述 Shen、Neal–Hinton、Fessler–Hero 的登记。完整跨用户二阶矩、相位目标到二维梯度／Hessian 的具体推导见本次文档式(4)–(16)。只保证同一冻结 Gaussian 模型的期望残差和边缘目标不恶化，不跨学习消息宣称共同目标单调。
- 中心坐标改为无量纲 s_q=(q−(Q−1)/2)/((Q−1)/2)，限制 |a|+|b|≤Δ；斜率增量为 b/((Q−1)/2)，吸收入信道的常数旋转为 a−b。Q=1只更新常数旋转。此变量选择和约束为本文适配，没有新方法名称。
- Δ=0.25/0.50 rad、归一化曲率下限 10^-3、充分上升系数 10^-4 和最多16次二分回退，是本次预先声明的数值设置，不是文献给出的最优参数。原初始化仍使用物理搜索；“无需路径搜索”只描述更新步骤。

新候选允许零步和零次更新后满足输出停止规则，零步不清空消息或重置方差；最多一次更新不等于每个输入强制更新一次。设置采用相同新停止规则的原完整 M 步作为额外对照，避免把停止变化误归因为局部求解收益。没有共用模型或术语定义变更，无需同步 STMP/DU。


## 2026-11-03：第三至六章、附录 A/B 压缩与双版本命名

按作者要求进行删减和归位，见[当前修订与核验](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/initial_submission_compression_20261103/REVISION_NOTES.md)。main 为不含 C 的版本，main_full 为包含 C 的完整版本；两版共享正文，C 的源文件保持。

- **sample covariance matrix、minimum description length (MDL)**：沿用本文件已核对的 Nadakuditi–Edelman §II-A 式(5)–(7)，印刷 pp.2626–2627。原附录噪声估计移至 V-B，以协方差和尾部特征值均值配合 MDL 引用说明，不将标准秩选择称为本文新方法。
- **denoising score matching**：Vincent §4.2 式(4.3)–(4.5)，PDF pp.6–7；Cai §IV-B。删去未知边缘 score 目标的独立陈列，保留 DSM 目标、条件均值损失及固定协方差下的等价关系。协方差权重仍属于本稿适配。
- **effective channel、IDAFT、rectangular waveforms、transmit windows**：沿用 Shen §II-B 式(3)/(9)、Bemani §II-B 式(16)、Xu 2019 §II-A/B 式(1)/(4)/(5)，具体原文和支持范围见[此前来源核对](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/afdm_otfs_comparison_20261103/SOURCES.md)。比较短段放在 II-B/V-C，删除附录的表格、示例和额外展开；没有新增普遍 AFDM 优势的论断。
- **variable projection、L-BFGS-B、phase refinement**：沿用原有 O’Leary–Rust、Zhu 和 Shen §III-C 来源，保留固定 Gaussian 反馈条件下的相位更新。按作者最后确认，C 中的调度和停止参数只留在 C，不搬至 A；main_full 继续指向完整 C，main 省去该引用。

无新增专业术语、方法名称或共用模型定义，不同步改写 STMP/DU。正文数学的删去、行内化和合并清单见上述记录，不再将前一轮“全部陈列公式不变”的历史结论套用到当前稿。两版结论均尚未加入，正式页数须在成稿时复核。

## 2026-11-03：网络结构说明与结论草稿

本轮仅补充 C-STMP 稿 VI-A2 的实际网络结构，并构思结论；对应[修订记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/network_structure_conclusion_20261103/REVISION_NOTES.md)。数字来自当前 C_STMP 配置绑定的已保存权重和实现，不移植参考论文的配置。没有改变共用模型、算法或训练，STMP/DU 不随之修改。

| 术语 | 原文定位与含义 | 本稿适用范围 |
|---|---|---|
| RefineNet、residual block、refinement block、conditional instance normalization、dilated convolution、ELU | [Song–Ermon, arXiv:1907.05600v3](https://arxiv.org/html/1907.05600v3#A1)，Appendix A.1–A.3；Cai 正式版 VI-A2、Table III，PDF p.11 | RefineNet 主干及归一化、残差与细化结构；四级宽度 128/256/256/256、细化宽度 256/256/128/128 和 dilation 2/4 经本地实现及绑定权重核对。扩写 ELU 为 exponential linear unit，不改其含义。 |
| sigmoid-weighted linear unit (SiLU) | [Elfwing、Uchibe、Doya, arXiv:1702.03118v3](https://arxiv.org/abs/1702.03118v3)，摘要直接定义 SiLU 为输入乘 sigmoid | 本稿去噪器条件映射与分类器使用该已有激活函数；两层 64 维条件映射、分类器 64/128/128 通道与 128/1 输出层是实际实现配置，不归为原论文设计。 |
| convolutional layer、fully connected layer、activation function | Shen IV-B、Fig.4、Table II，PDF pp.11–12；Cai VI-A2、Table III，PDF p.11 | 采用现有网络描述用语。分类器按实际六个卷积层、步长和展平特征与五个标量拼接说明，不写成 Shen 的残差 CNN、平均池化或 Softmax 输出。 |

实现核对入口：`src/networks/score.py`、`src/networks/cai_models/ncsn_channel_diffusion.py`、`src/networks/cai_models/layers.py`、`src/training/colored_score_20261024/model.py`、`src/algorithm/STMP/activity.py`。冻结权重哈希、阶段输出尺寸与读出维度见本轮 `ARCHITECTURE_CHECK.json`；该核对不代表新增性能实验。

结论草稿仅概括本文已有模型、先验学习、接收机与实验，不新增方法名称、理论保证或结果。Cai VII（PDF pp.14–15）压缩引言贡献后讨论更一般意义；Shen VI（p.15）依次回顾引言的传输、接收机、CNN 与实验；Wei VI（p.5）围绕方法改进及实验收益；Huang V（p.5）概括有效信道学习并提出后续方向。这里借鉴组织方式，不把四篇原文的性能或适用范围移用于本文。

## 2026-11-03：补充原始方法引用与 13 页压缩

本轮未新增技术命名或改变模型。结论已在上一轮纳入两版；本轮保留其原文。参考文献、正文压缩及验证见[修订记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/references_compression_20261103/REVISION_NOTES.md)。

| 已有术语或方法 | 补充的原始出处 | 本轮引用与边界 |
|---|---|---|
| LMMSE linear estimation | Ma–Ping, *Orthogonal AMP*, IEEE Access 5:2020–2033, 2017；本地作者版 PDF p.3，III-B，式(15c)，DOI 10.1109/ACCESS.2017.2653119 | III-A 均值更新的线性估计形式；不把本文接收机改称 OAMP，不把该文当作一般后验协方差投影的直接出处 |
| right-rotationally invariant random sensing matrices | Rangan–Schniter–Fletcher, *Vector Approximate Message Passing*, IEEE TIT 65(10):6664–6684, 2019；本地作者版摘要、I-D，PDF pp.1–2，DOI 10.1109/TIT.2019.2916359 | I 中大系统等效高斯模型背景；原文为 right-orthogonally invariant 实模型，本文沿用 Cai 的复模型用词，不声称当前有限维网络满足 VAMP 定理全部条件 |
| score function | Hyvärinen, *Estimation of Non-Normalized Statistical Models by Score Matching*, JMLR 6:695–709, 2005；[原文摘要](https://www.jmlr.org/papers/v6/hyvarinen05a.html)明确为对数密度梯度 | IV-A 定义后补原始来源；有色加权 DSM 和本文条件均值参数化仍沿用已有推导与 Vincent 引文 |
| minimum description length (MDL) | Wax–Kailath, *Detection of Signals by Information Theoretic Criteria*, IEEE TASSP 33(2):387–392, 1985，DOI 10.1109/TASSP.1985.1164557 | V-B 补原始参考文献；本轮核对出版记录，公式含义继续依据本账本已核的 Nadakuditi–Edelman II-A，式(5)–(7)，pp.2626–2627，不新增理论保证 |
| RefineNet | Lin–Milan–Shen–Reid, CVPR 2017，DOI 10.1109/CVPR.2017.549；[CVF 论文摘要](https://openaccess.thecvf.com/content_cvpr_2017/html/Lin_RefineNet_Multi-Path_Refinement_CVPR_2017_paper.html) | VI-A2 补架构原始出处，仍保留 Song Appendix A 的改型出处；四级宽度、条件归一化和分类器结构仍来自本稿实现 |

第五、六章仅合并既有术语下的重复说明。对网络能量及内积特征，仍明确先按 Dv 归一化，再作对数变换；不因压缩改变运算次序。新增 Kodheli、Mei、Ke 仅支撑已有引言背景，具体来源和支持范围见本轮修订记录。共用定义未改变，STMP/DU 无需同步修改。


## 2026-11-03 逐帧相位投影适配

| 术语或操作 | 原文依据 | 本项目适用范围 |
|---|---|---|
| phase rotation; projection onto the unit circle / 相位旋转、投影到单位圆 | [Shen作者稿](https://arxiv.org/html/2412.20806v1#S3.SS3)，§III-C式(47)–(54)，p.9，算法1 | 独立候选直接更新逐帧单位模相位；当前AFDM条件矩、固定首帧、全部用户和保留原调度均是项目适配。放宽共同斜率约束，不声称原式为精确约束M步或具有目标单调性。推导见[PHASE_SHEN_FRAMES_20261103.md](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/PHASE_SHEN_FRAMES_20261103.md)。 |


## 2026-11-03：正式版本替换与保留引言论述

按作者要求，将原来作为预印本引用的四篇文献更新为正式出版记录，移除 Wei2026 条目并保留其对应引言句，仅去掉标号及悬空介词。历史阅读依据继续保留，不把保留句登记为新验证的独立结论。完整元数据、范围与核验见[本轮记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/published_references_20261103/REVISION_NOTES.md)。

| 既有术语或公式 | 本轮核对与版本边界 |
|---|---|
| conditional mean、conditional covariance、Tweedie's formula | Dytso et al., IEEE TIT 69(3):1883–1898, 2023，DOI 10.1109/TIT.2022.3216012；正式 PDF p.1（1883）式(3)、p.3（1885）III 节 Prop.1 式(17)。按本稿既有 Jacobian 定义使用相应转置，公式不变。 |
| colored Gaussian noise、DNN denoiser for correlated noise | Shastri et al., IEEE JSAIT 3(3):528–542, 2022，DOI 10.1109/JSAIT.2022.3207109；正式 PDF p.8（535）III-B、式(38)。只支持已知相关协方差下的去噪器设计，具体 Kronecker 结构为本文适配。 |
| Monte Carlo method、divergence | Metzler et al., IEEE TIT 62(9):5117–5144, 2016，DOI 10.1109/TIT.2016.2556683；原方法定位为作者公开稿 p.15 V-B。未核实出版社版本节号，正文只引正式文献；本文随机符号探针和协方差加权含义保持。 |
| rectangular waveforms、transmit windows、OTFS transform cancellation | 正式记录改为 Zou et al., ICC Workshops 2021, pp.1–6，DOI 10.1109/ICCWorkshops50388.2021.9473771，第一作者 Zou。公式依据仍为已核对作者稿 II-A/B 式(1)/(4)/(5)；未将其编号直接迁入未读取的正式 PDF，正文只保留正式文献引用。 |

这是来源版本更新，不引入新术语、算法或共用模型定义，不同步改写 STMP/DU。历史记录中旧键及旧作者稿名称用于溯源；当前引用以本轮记录为准。


## 2026-11-03：当前全文的完整搭配、操作对象与压缩

作者进一步明确：检查应以完整搭配在同类论文中的自然程度和使用位置为单位，不能把两个单词各自有出处当成组合有出处。本轮据此审阅实际编入的摘要、I–VII、A–C 及三张方法图；[完整核查表](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/prose_terminology_20261103/TERMINOLOGY_AUDIT.md)列出保留项、替换项、本文名称及原文位置。

- Cai 正式版 III-B1/PDF p.6 的 matched first- and second-order moments 与 posterior moments 并非同一个完整搭配。Shen 当前本地版本未检出 moment(s)，IV-A/PDF p.11 使用 posterior means and variances。Manor–Michaeli §3.2/Theorem 2 的 posterior moments 是完整用例，但其存在不构成本稿保留笼统表述的理由。当前正文与图用 mean and variance 或 mean and covariance，按实际对象区分。
- activity evidence 统一按具体含义写成 activity probability、density ratio 或 Gaussian approximation；new-message weight 改为 Cai V-B1 的 damping factor；first-order atom approximation 改为 Wei IV-B 的 first-order linear approximation。block-fixed、query variance、phase-policy、native convergence、valid-moment iterations 等改为普通操作描述。
- site approximation 保留 Vehtari §2.1 pp.5–6 的完整用例，明确其是信道先验因子的近似；precision/natural parameter 的依据为 §5.3 p.18 与 Appendix A p.32。完整停止检查移至附录 C-G，公式及阈值保持。
- MFLE、GPJD、GP-MP、GP-MP-CCD 与 GP-MP-CCD-EP 是作者确认的本文名称。尤其 covariance-conditioned denoising/CCD 不归为 Shastri 原方法名；原文 III-B 标题是 DNN Denoiser for Correlated Noise。本文的 Kronecker 训练分布、矩阵预条件和停止调度均按明确公式/配置登记。
- 更新 Fig. 3 的两个统计量标签及其 PDF/SVG/PNG。未改变共用模型定义、实现、权重、实验结果或其他稿件。

## 2026-11-03：基于已知相位接收机的近似 EM 候选

推导与实现对应见 [PHASE_EM_20261103.md](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/PHASE_EM_20261103.md)。只登记独立候选，不命名新的方法或切换冻结主线。

- **EM / generalized EM、posterior mean and covariance**：沿用 Dempster–Laird–Rubin §3 p.7 式(3.5)、Theorem1（[DOI](https://doi.org/10.1111/j.2517-6161.1977.tb01600.x)）及 Neal–Hinton 作者稿 pp.4–5 式(2)–(5)（[原文](https://www.cs.toronto.edu/~hinton/absps/emk.pdf)）。本候选的神经消息推断仅称近似E步；只能验证固定工作分布下的M步目标下降，不能继承精确EM的似然单调性。
- **Armijo condition / 充分下降条件**：Armijo 1966，正文 p.2 Corollary2 式(2)，[原文](https://msp.org/pjm/1966/16-1/pjm-v16-n1-p01-p.pdf)。归一化、共同斜率的对角曲率上界、20内步／12次回退为本项目推导与设置；不是引用论文给出的AFDM更新算法。
- **conditional covariance、Jacobian of the conditional mean**：Dytso–Poor–Shamai 作者稿 §IV Proposition1 式(22)、Corollary1 式(23)，PDF pp.5–6，[原文](https://arxiv.org/pdf/2104.01883)。非正汇总导数迹拒绝沿用已有正精度消息接受条件；不将保留方差称为校准正确的后验方差。
- 共同相位斜率、独立用户Bernoulli–Gaussian工作分布、期望残差中的相位不变协方差项、60次消息迭代后进行一次M步及历史保留／清除规则，均由本项目明确公式或配置定义，不包装成 Shen 原算法或新命名技术。没有共用物理定义变更，因此不修改 STMP/DU。

## 2026-11-03：进一步逐词修订及 Cai 段落骨架核查

[逐词修订记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/wording_pass_20261103/REVISION_NOTES.md)记录了完整搭配、修饰范围及操作对象的进一步调整；[逐段核查](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/cai_paragraph_alignment_20261103/PARAGRAPH_AUDIT.md)另对第3–5章47段逐项定位蔡文母段，结论为**尚未一一对应**。两类核查不可相互代替；用户最新要求停止编译，段落结构调整尚未执行。

| 修改或保留 | 原文定位及本稿含义 |
|---|---|
| Frobenius norm | Shen，Notation，PDF p.3；本文表示矩阵或张量全部元素平方和的平方根。 |
| 接收符号在延迟维的位置 | Shen II-B，PDF p.4，三索引有效信道的第三个索引；将 received-symbol delay position 展开为相应位置描述，避免误指路径时延。 |
| denoiser；complex-valued denoiser | Cai IV-A/B、V-A，PDF pp.8–9 的去噪函数用途；complex-valued 只说明本文输出类型，不宣称整个修饰组合为原方法名称。替换 mean function、complex mean map。 |
| proper complex Gaussian noise with covariance | Neeser–Massey 的 proper complex 随机量约定；Shastri 正式版 III-B/PDF p.8 的相关噪声去噪。Gaussian/proper 不修饰 covariance 矩阵本身。 |
| finite differences；Monte Carlo averaging | Metzler [作者稿](https://arxiv.org/pdf/1406.4175)，V-B/PDF p.15，标题 Monte Carlo method。本文分开叙述导数近似与随机迹估计；中心差分、随机符号和协方差加权不归为原论文相同配置。 |
| expected loss、posterior log odds、Bayes' rule | Menon–Ong [原文](https://proceedings.mlr.press/v48/menon16.pdf)，§2.1–2.2/PDF p.2 及 §4.2/PDF p.3。保留无约束函数类的最优性条件；将 population optimum over unrestricted logits 和 Bayes correction 改成明确操作。 |
| noise-variance estimate、low-rank signal covariance | Nadakuditi–Edelman II-A，式(5)–(7)，pp.2626–2627；估计的是噪声方差，低秩修饰信号协方差。MP 中固定该估计是本文选择。 |
| single-step denoising；fractional delay-Doppler off-grid leakage | 分别核到 Cai PDF p.2 和 Huang 摘要/PDF p.1 的完整表达；保留，不因组合较长判成自造。 |
| damping factor；停止条件满足/达到迭代上限 | Cai V-B1/PDF pp.9–10，式(57)–(58)支持阻尼名称；停止状态按本文实际数值检查描述，不扩大成数学收敛保证。 |
| pilot correlations、previous parameter estimates、objective | 本地 phase_estimation.py 的 coarse_scores/candidates/refine/estimate 与附录公式核对；表达实际的相关评分、时延/Doppler 参数和残差平方目标，不是新方法名称。 |

已按已读实现将附录中的 valid mean and covariance estimates 具体化为训练方差范围内被接受的 site 更新及相应窗口。没有改变模型、公式、数值阈值、图文件或实验。MFLE、GPJD 与 GP-MP 系列作者确认的名称保持；无共用定义变更，不修改其他稿件。

本次 Cai 段落索引采用正式版 PDF pp.5–11，印刷 pp.3579–3585，并以作者 v2 HTML 的段落锚点定位。第三、四、五章分别12、9、7个原段。旧记录中的“内容对应”“句式借鉴”不应升级为当前47段已逐段对应，也不证明每个句子都有某篇参考论文的整句母本。

## 2026-11-03：确认分段判断后的第3–5章修订

作者确认保留合理分段、合并碎段后，正文由47段整理为33段，见[本轮记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/paragraph_revision_20261103/REVISION_NOTES.md)、[逐段来源](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/paragraph_revision_20261103/PARAGRAPH_MAP.md)和[原文语境核查](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/paragraph_revision_20261103/SOURCES.md)。此条更新上一条“结构调整尚未执行”的状态；不编译的要求继续执行。

| 本轮表达 | 原文定位与核查结果 | 处理 |
|---|---|---|
| extrinsic message、posterior covariance | Cai III-A，PDF p.5／3579，式(6)–(11)；III-B3，PDF pp.7–8／3581–3582，式(39)–(42) | 按后验近似、相除、消息传送的原顺序组织；协方差近似归回后验段，外信息条件接回公式段。 |
| conditional Gaussian density 的 score | Cai IV-B，PDF p.8／3582，式(46)–(48)，比较边缘密度与条件密度的对数梯度 | 改为直接说明条件密度的 score，不再写扰动本身具有 conditional score。协方差权重为本文适配。 |
| conditional mean、conditional covariance、Jacobian | Dytso 正式版 III，PDF p.3／1885，Proposition 1 式(17)；Cai IV-A，PDF p.8／3582 | 定义和白噪声特例紧跟相关公式；保留本文 Jacobian 方向及一般协方差条件。 |
| colored Gaussian noise、correlated noise | Shastri 正式版 III-B，PDF p.8／535，式(38)–(40) | 直接写训练样本生成和条件输入，删去笼统的有限维相关误差解释；Kronecker 分布不归为原文同一设置。 |
| density ratio estimation、交叉熵理想解及先验代入 | Menon–Ong §2.1–2.2，PDF p.2；§4.2 式(16)–(17)，PDF p.3；Shen IV-A2 式(60)–(61)，PDF p.11 | 按目标、训练、输出组织三段；把 training prior log odds 改为直接减 logit(pi_tr)；不把网络训练结果说成已达到无约束最优解。 |
| site approximation | Vehtari §2.1，pp.5–6 | 先写近似因子的 Gaussian 形式，再连续说明相除及相乘，不增加新的组合名称。 |
| damping factor、singular value decomposition (SVD) | Cai V-B1，PDF pp.9–10，式(57)–(58)；Rangan 作者稿 III，PDF pp.3–4，式(11)、Algorithm 2 | 两向阻尼及首次迭代集中说明；SVD 删除 thin 修饰并同步 Algorithm 1，矩阵分解与更新式不变。 |

本轮没有新增专业名称或共用模型定义；本文既有 MFLE、GPJD、GP-MP-CCD 等名称沿用作者确认的记录，不改 STMP/DU。没有变更公式、数值阈值、训练设置或实验；摘要未重新生成，PDF 保留旧版。

### 2026-11-04：Off-grid SBL 不同网格设置的实验动机

- **block-wise linear model、number of sub-blocks、model accuracy、number of free variables**：Cai 等 [§VI-C](https://arxiv.org/html/2506.00581v2#S6.SS3)，本地 `reference/literature/cai2026.pdf` PDF pp.12–13／印刷 pp.3586–3587，TMP-EM 基线说明及 Fig.6 分析。忠实译为“分块线性模型”“子块数”“模型精度”“自由变量数”。Cai 改变频域子块数，不能将该参数记作时延–多普勒网格大小；原文报告低、高 SNR 对子块数的偏好不同。
- **virtual sampling resolution**：Wei 等 [§VI-A–B](https://arxiv.org/html/2101.05629v1#S6.SS2)，不同虚拟采样分辨率下的 NMSE/SNR 比较。本文候选实验改变时延–多普勒网格分辨率及明确说明的候选预算，沿用既有网格和连续偏移定义；与 Cai 的联系是比较人工设定的表示精细程度及其性能敏感性，参数和算法机制并不相同。

以上仅记录实验动机与术语对应，不新增方法名称、不声称新的性能结果，未改变 STMP/DU 的共用模型定义。


## 2026-11-04：设备矩阵记号与公式归属（已实施）

作者已明确授权修正前一轮变量/公式审查。本节为当前正文记号；此前张量记号的出处记录作为历史保留。

| 当前表达 | 原表达/关系 | 依据与范围 |
|---|---|---|
| 设备矩阵 H_k，N×MN | 各天线 N×N 信道矩阵转置后横向拼接；原实现仍为 M×N×N 数组 | Cai §II-A 式 (4) 的分块形式、Shen §II-C 式 (14)–(15) 的多帧组织。当前维度及排列是本文适配，vec 顺序已核对。 |
| H_k^post | 原 μ_k；与网络输出 F_k 区别保留 | Cai §III-B1 式 (22) 用 H_k^post 表示条件信道均值。本文经 site 相乘获得近似矩，保留 site 时不保证等于新网络输出。 |
| τ_k^ext | 原 c_k，避免与 AFDM 的 c1/c2 同形 | Cai §III-B1 式 (24)–(27) 的 extrinsic variance；本文设备下标及保留规则为适配。site 用法依据 Vehtari §2.1。 |
| Y_sig | 原无噪声观测 Y_0 | 本文记号修复，Y_0 已用于第 0 帧观测；不增加方法名称。 |
| continuous-time AFDM waveform；chirp-periodic extension | 原式 (6) 的取模波形 | Bemani 学位论文 §3.1.1 式 (3.7)、(3.9)，印刷 pp.26–27（PDF pp.52–53）；§3.2 式 (3.14)，印刷 p.29（PDF p.55）。时间归一化、CPP 多周期延拓属于本文。已重新读取原页并核验采样关系。 |
| conditional-mean derivative | 保留 P_R=J_mΣ 的右乘次序 | Dytso 正式版 §I-B 式 (9)、§III Prop.1 式 (17)，PDF p.3/印刷 p.1885。原文采用输入行/输出列 Jacobian；本文采用输出行/输入列。旧作者稿式号不能冒充正式版。 |
| density ratio estimation | 均衡训练时 log ratio 直接由 classifier logit 给出 | Menon §3 式 (6)–(9)、§4.2 式 (17)及其后 logistic loss 例，PDF pp.2–3。接收端先验 ρ 保留；删除零值训练先验校正。 |
| Monte Carlo trace / finite differences | Σ 加权随机符号方向与中央差分 | Metzler 作者稿 v5 §V-B，PDF p.15，原文是 Gaussian 方向和单边差分；当前组合是本文按 E[zz^T]=I 的适配，非原文原式。 |
| matrix preconditioning | BΣ/KΣ/OΣ | Karras Table 1（PDF p.3）、§5 式 (7)–(8)（PDF p.8）、App.B.6 为标量基础。当前矩阵函数是扩展，已核验白噪声退化、名义输入及残差协方差。 |

完整 57 个当前编号公式、原号映射、逐式来源和推导边界见 [公式出处复核](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/FORMULA_PROVENANCE_20261104.md)。旧模型推导/实现文档中的张量索引仍可用于代码阅读；与正文矩阵之间仅是无损重排。本次为 C-STMP 稿件的表达调整，未改变共用物理模型或 STMP/DU 研究定义。

## 2026-11-04：推导呈现精简后的状态

上条“57 个当前编号公式”对应当天先完成的记号修订。经作者后续授权，已移出单独的 CPP 延拓式及 AFDM 信道展开附录，当前为 53 个编号公式，详见 [呈现精简记录](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/DERIVATION_PRESENTATION_20261104.md)。术语含义、物理条件和算法运算保持；没有新增共用定义，无须同步改写 STMP/DU。

| 表述 | 原文依据 | 当前呈现 |
|---|---|---|
| chirp-periodic prefix / continuous-time AFDM waveform | Bemani 学位论文 §3.1.1 式 (3.7)、(3.9)，印刷 pp.26–27；§3.2 式 (3.14)，印刷 p.29 | 正文保留波形及取模定义，CPP 单独展开移至内部记录；多周期适配仍属本文 |
| conditional covariance / Jacobian | Dytso 正式版 §III Proposition 1 式 (17)，印刷 p.1885 | 直接给 P_R = J_m Σ，保留本文 Jacobian 方向、固定 C 条件和每复坐标的归一化；省去逐步求导说明 |
| Monte Carlo finite differences | Metzler 作者稿 v5 §V-B，PDF p.15 | 引出句明确本文采用中央差分；随机符号方向与 Σ 加权仍为本文实现，不归为原文同式 |
| preconditioning | Karras Table 1，PDF p.3；§5 式 (7)–(8)，PDF p.8 | 网络设置中保留矩阵扩展的定义，不作为独立理论贡献或新增证明 |

作为篇幅组织对照，Shen §II-B 式 (3)、T_sym = T + T_cp 的定义、Proposition 1 及附录 A 式 (67)–(69) 实际涉及 CP；其最终信道式吸收了部分前缀相关相位。不能据此宣称 CP 完全不进公式。此处未引入任何新术语或将 OTFS 的整数时延模型移植为本文 AFDM 分数时延模型。

## 2026-11-04：与 Cai 的公式对应范围

[当前 53 式逐项对照](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/CAI_FORMULA_CORRESPONDENCE_20261104.md)核对 Cai 期刊版 §II–VI，PDF pp.4–13。Gaussian 外信息、混合矩和后验分解有明确对应；一般 LMMSE、实数有色噪声和平均方式需适配。不得将中央差分、分类密度比、矩阵预条件、输入尺度更新或相位前端说成 Cai 原式。

**damping** 继续使用已有术语。Cai §V-B1 式 (57)–(58) 和 Algorithm 2，PDF pp.9–10，写出相邻两轮原始外信息的加权；本文式 (40)–(41) 使用上一轮已阻尼状态递归更新。同属阻尼，不是完全相同的迭代。此条只校准来源对应等级，不改算法或既有参数决定。

## 2026-11-04：递归阻尼与矩阵预条件的补充原型

详细映射见[专项核查](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/DAMPING_AND_FORMULA_PROTOTYPES_20261104.md)。本节补充前述出处，不改术语或共用系统定义。

| 术语/操作 | 已核原文位置 | 适配边界 |
|---|---|---|
| damping（递归旧状态加权） | Rangan et al., On the Convergence of Approximate Message Passing With Arbitrary Matrices, IEEE TIT 2019，§II，Algorithm 1 第 9/13 行，PDF p.2/印刷 p.5340；Rangan et al., Vector Approximate Message Passing，作者稿 §III-C 式 (26)–(27)，PDF p.6 | 本文均值及 variance 参数递归插值；VAMP 原式 (27) 插值 precision。用来支持方法家族与递归形式，不冒充完整同式或直接套用收敛定理 |
| matrix preconditioning | de Albuquerque–Pearson, Inflationary Flows: Calibrated Bayesian Inference with Diffusion-Based Models, NeurIPS 2024，App.B.1，PDF pp.23–24，式 (67)–(68)、(73)、(77)–(78) | 取原文 Σ0=σ_d²I、C(t)=本文Σ，得到本文 (47) 的 BΣ、KΣ、OΣ；原文 loss weighting、网络、噪声日程不与本文等同。此前仅追溯到 Karras 标量式的记录现补全 |
| Hutchinson trace estimator / Rademacher random variables | Avron–Toledo, Randomized Algorithms for Estimating the Trace of an Implicit Symmetric Positive Semi-Definite Matrix, JACM 2011，§2 Lemma 2.1，PDF p.2；§3 Definition 3.3，PDF p.3 | 支持随机符号方向的迹估计；与 Metzler §V-B 的差分散度估计结合，再作 Σ 加权与中央差分，是本文实现适配，不声称所有组合出自同一原式 |

公开原文：[Rangan 阻尼](https://phil-schniter.web.app/pdf/tit19_gamplin.pdf)、[Inflationary Flows](https://proceedings.nips.cc/paper_files/paper/2024/hash/af85ade5e70a6e1eb07a9541fb529baf-Abstract-Conference.html)、[Avron–Toledo](https://www.cs.tau.ac.il/~stoledo/Bib/Pubs/randomized-trace.pdf)。

## 2026-11-04：两项实现设置改为文字呈现

κ 更新与训练协方差采样依作者要求取消独立编号式，保留其等义文字说明，见[修订记录](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/IMPLEMENTATION_SETTINGS_PROSE_20261104.md)。weighted average、damping factor、covariance matrix、conjugate transpose 和 convex combination 均按既有含义使用；未引入方法名称或新增理论归属。κ 阻尼原型沿用前述 Rangan，协方差的具体随机采样仍是本文训练设置，不冒称 Shastri 的原式。

## 2026-11-04：普通实现操作与指标转为文内说明

依据 Cai §V-C/PDF p.11 的行内 complexity、§VI-A 脚注 1 的 NMSE，Shen §V/PDF p.12 的行内 received SNR/NMSE/AER，以及 Rangan VAMP §III-C/PDF p.6 的 clipping 文字说明，本稿完成[呈现复查](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/FORMULA_PRESENTATION_AUDIT_20261104.md)。保留既有术语与统计含义，取消五个独立编号式；不新增方法名称，不把纯呈现选择解释为公式无依据。递归 damping 的引出句现使用 Rangan §III-C 来源；相应方差参数适配边界仍按此前记录。


## 2026-11-04：固定相位条件推断与当前相位提议的停止检查

本次独立候选`C_STMP_phase_conditional_schedule_20261104`沿用Noels §3.2的内部推断／同步参数更新区分，以及现有Shen式(47)–(54)对应的Gaussian条件矩和逐帧投影。不新增方法名称。更新后的查询、反馈和方差比例保持连续；条件推断用已知相位接收机原标准判定稳定。

相位提议的停止量为预测观测变化的条件期望平方范数，除以旧预测观测的条件期望能量加噪声能量后开方。该量由已有G_q直接展开，是本项目数值检查，未归为文献现成准则。1%容差沿用此前phase trial数值，但指标定义不同，不声称同等精度、总体最优或神经EM收敛。完整定义、对照和冻结计划见候选说明（仅本地历史资料：`archive/result_legacy_20261023/candidates/c_stmp_phase_conditional_schedule_20261104/README.md`）。主线与共用系统定义保持不变，1000场景批次不恢复。


## 2026-11-04：算法框形式的参考位置

[伪代码修订](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/PSEUDOCODE_STYLE_20261104.md)对照 Cai Algorithm 2（PDF p.10／印刷 p.3584）、Shen Algorithm 1（PDF p.10）和 Huang Algorithm 1（PDF p.4／印刷 p.2952）的输入输出、初始化、循环、行号与公式引用形式；不引入新方法名称或声称本文运算等于这些算法。作者不要求在伪代码中呈现训练区间外的 Gaussian evidence 兜底；该分支已从算法框移除，代码及既有实现说明保持。

### 2026-11-04：固定二次式上的逐相位最小化

- 原词来源：Waldspurger, d’Aspremont, Mallat, *Phase recovery, MaxCut and complex semidefinite programming*, arXiv:1206.0102v3，§2.3 “Greedy Optimization in Phase”、式(3)、Algorithm 2，PDF第4页。https://arxiv.org/pdf/1206.0102v3 。逐个固定其他相位求单坐标单位模二次式最小值，依次更新。
- 本项目使用描述“逐相位闭式最小化”；对含线性项的F=phi^H G phi−2Re(phi^H b)，更新phi_k=(b_k−sum_{j!=k}G_kj phi_j)/abs(b_k−sum_{j!=k}G_kj phi_j)，参考帧固定，数值零保持。它不是PhaseCut半正定松弛，也不是Shen的解方程后归一化。
- 只声明同一冻结条件二次式不增加。调度及相对预测观测变化停止量仍为本项目适配，不扩展为学习接收机的全局收敛保证。独立候选与验证：result/candidates/c_stmp_phase_coordinate_20261104/README.md。


## 2026-11-04：Gaussian 活动概率对照的呈现位置

[正文精简](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/DEFENSIVE_LANGUAGE_REVIEW_20261104.md)将既有 Gaussian approximation 活动概率式 (43) 从 VI-A3 移到 VI-C 的消融对照定义，原式、记号及来源归属保持。GPJD 的计算量按 Algorithm 1 主更新表述；stopping criterion、paired scenes、AER 等均沿用既有含义，没有新增专业名称或改变统计定义。

## 2026-11-04：按作者选择简化引言表示与缩写

- **three-dimensional tensor at each antenna**：本轮重新读取 Shen 本地 PDF p.4，§II-A 末段及 §II-B 式 (9) 后，均明确其所研究有效信道在每根天线用 3D tensor 表示。引言改为 `The effective channel at each antenna is represented by a three-dimensional tensor`，保留 §II-B 引用；不再提前罗列 Doppler、path delay、received symbol position 三项索引。这是既有模型的简洁概述，不新增比较结论。
- **effective-channel representation**：沿用本稿引言、第二章比较及结论中的已有描述，替换第一项贡献的 channel tensor。本文每根天线为矩阵，跨天线组成 device matrix，网络再重排为 arrays；这些名称各有明确对象，保留其区别。Shen 的 tensor 不随本方法名称统一而删除。
- **discrete Fourier transform / DFT**：引言将原 inverse DFT 展开为 inverse discrete Fourier transform，保留原 Bemani §§II-B/III-A 引用；第五章调制复杂度首次使用缩写时定义 discrete Fourier transform (DFT)，第六章直接沿用。没有将 DFT 改名为 DAFT，也没有为一次展开新增 IDFT 缩写。

其他技术名称及来源保持，未改共同定义、公式、方法或实验，不涉及 STMP/DU 同步。作者对摘要定性结果及引用编号作主语的保留意见，见[逐项决定](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/ABSTRACT_INTRO_LANGUAGE_REVIEW_20261104.md)。

## 2026-11-04：共同斜率与接收机工作分布的配对检验

本轮沿用2026-11-03近似EM条目、PHASE_EM_20261103.md式(2)–(5)及PHASE_DIRECT_20261103.md的既有出处，不新增方法名称。独立用户Bernoulli–Gaussian工作分布、joint mean（活动概率加权联合均值）与重新条件化外信息所得Gaussian后验明确区分。前者共享每用户活动变量，其投影方差包含p(1−p)||P h||²项；固定单位模相位时此用户内协方差不进入相位梯度，但进入预期预测观测变化。

用普通公式描述共同斜率phi[q,k]=exp(j*q*beta[k])。单用户目标是Re sum_q c_qk exp(−j*q*beta_k)，复用既有数值驻点求解与旧值比较；无时延／多普勒网格，仍是相位斜率优化，不称“无需估计频偏”。本轮不继承精确EM的物理似然单调性，也不称两个工作分布等同。完整范围见result/candidates/c_stmp_phase_slope_moments_20261104/README.md。共用系统模型不变，不修改STMP/DU术语定义。


## 2026-11-04：物理相位初始化的边缘似然对照

- **Gaussian marginal likelihood / 高斯边缘似然**、**sparse Bayesian learning / 稀疏贝叶斯学习**：Tipping and Faul, *Fast Marginal Likelihood Maximisation for Sparse Bayesian Models* (2003)，作者排版稿§2.1式(7)–(8)、p.3，https://www.miketipping.com/papers/met-fastsbl.pdf 。出版信息https://proceedings.mlr.press/r4/tipping03a.html 。原文使用实值标量观测和基函数精度参数；本项目改成复数、多天线观测、每用户共享非负增益方差及连续物理原子，不能称原算法完整复现。
- 本次坐标贡献`log(1+γs)−γt/[M(1+γs)]`和`γ*=max(0,(t/(Ms)−1)/s)`由声明的复高斯模型直接推导；具体推导、假设及固定实验门槛见`result/candidates/c_stmp_phase_init_marginal_20261104/README.md`。
- 该候选只改物理初始化，仍保留原时延/多普勒搜索范围和预算；后续共同斜率迭代复用上一轮实现。内部文件标识不作为论文新方法名称；不宣称降低初始化目标就保证AER或NMSE改善。

## 2026-11-04：新初始化之后的局部相位更新建议（尚未实施）

- **MM / majorize-minimize**：Hunter–Lange (2004), *A Tutorial on MM Algorithms*, The American Statistician 58(1):30–37，§1/p.30的一般原则；本次核对[出版方摘要](https://www.tandfonline.com/doi/abs/10.1198/0003130042836)，全文镜像未成功读取，不宣称全文核验。具体复相位逐坐标曲率上界与下降不等式为[本项目推导](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/PHASE_AFTER_MARGINAL_INIT_20261104.md)，不是原文公式或新方法名称。
- 新记录区分初始化的物理增益模型与后续Gaussian消息模型；同属边缘似然思路不等于共享一个全程目标。按噪声能量归一化的候选观测变化只是自定义数值诊断量，不称既有统计检验。实验仅提出，尚未执行；共用系统定义及STMP/DU术语不变。


## 2026-11-04：第三至第五章语言修订中的已有名称

- **factor graph**：沿用 Cai §III、Fig. 2（本地期刊 PDF p.5）及本稿图 2 图注，章首改为 shows the factor graph，不改变图的因子关系。
- **score matching objective / denoising score matching**：沿用 Cai §IV-B（PDF p.8）及 Vincent 2011 的既有依据。本稿式 (26) 后改为固定 C 下与 Σ 加权目标具有相同最优解；这是原参数无关差项陈述的编辑，不声称与 Cai 的标量噪声公式完全同形。
- **antennas / received symbols / transmitted symbols**：沿用本稿 II-B、III-B 的对象定义。IV-B 及 VI-A1/A2 统一这些名称；Ra⊗I_N⊗Rc 对应外层至内层的天线、接收符号、发送符号，vec 列堆叠时发送符号变化最快。无新术语或排列定义。
- **fast Fourier transform (FFT)**：原词见 Cai §V-C（PDF p.11）；本稿 V-C 补全首次缩写，原 Bemani/Zou 波形成本依据和计数保持。

原文核对记录见[III–V 语言分析及实施表](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/CHAPTERS_III_V_LANGUAGE_REVIEW_20261104.md)的来源条目；本轮没有新增方法名称或共用系统定义，不涉及 STMP/DU 同步。


## 2026-11-04：图 3 精简与模块名称的位置

图 3 直接复用正文既有变量与式 (19)–(22)、(29)、(33)–(35)，去掉重复说明性标签，无新增方法名称。表达方式对照 Cai 期刊版 Fig. 3（PDF p.10／印刷 p.3584）及 Huang Fig. 2（PDF p.3／印刷 p.2951）；沿用原 Cai 网络矢量图形并保留图注出处。Huang 仅供少文字、变量及箭头表达参考，没有采用其采样公式或复制数据图。参考与改动见[图形修订记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/method_figures_simplified_20261104/README.md)。

MFLE/GPJD 在摘要、引言预先概述，第三章正文仍使用 linear estimation / joint denoising，第五章用于具体算法组织；作者本轮核对后继续维持。V-B 为 Parameter Estimation and Numerical Implementation，不新增两种方差区别的独立章节。共用定义不变，不涉及 STMP/DU 同步。


## 2026-11-04：图 3 的迭代总览与 GPJD 展开

图形采用左侧 MFLE/GPJD 两模块迭代、右侧展开 GPJD 的层级。此种总览/展开表达参考已核对的 Cai Fig. 3（期刊版 PDF p.10／印刷 p.3584），不新增算法模块；原网络示意路径及 Cai 图注出处保留。Gaussian extrinsic message、MFLE、GPJD、变量和公式编号均为现稿已有定义。具体线框颜色、布局与核验见[本轮记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/receiver_overview_expansion_20261104/README.md)。无共用定义变化。

## 2026-11-04：图 3 的去噪输入输出展示

重新核对 Cai 期刊 Fig. 3（PDF p.10／印刷 p.3584）的含噪信道—score 网络—后验信道排列及相邻式 (62)，借鉴其前后矩阵纹理对照；本文使用 IV-B 已定义的直接去噪器 F_theta，输入 R_k、输出 F_k 对应 V-A 首段及 Algorithm 1。图内 Denoiser 沿用本文 IV-B 的既有用词，Cai §III-B／Algorithm 2 亦使用 channel and device activity denoisers。没有引入新方法或声称本文分类器等于 Cai 二阶网络。

图中矩阵幅度来自本项目已保存的同一独立去噪样本，前后使用相同色标；具体文件、索引和出处见[图形修订记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/receiver_denoising_pair_20261104/README.md)。此处仅借鉴原图的表达关系，未复制蔡文的信道数据或把其频域矩阵当作本文 AFDM 信道。共用定义不变。

## 2026-11-04：图 3 流程标签与已有操作对应

本轮图形修正仅使用正文已有操作名称：Finite differences 对应 IV-C 式 (29) 及既有 Metzler 导数估计依据；Gaussian site 对应 V-A 式 (34)–(35) 及 Vehtari §2.1；Damping 对应 V-B 式 (39) 及既有 Rangan §III-C 依据。Average over k 是 Algorithm 1 对设备方差求平均的普通操作说明，不是新增方法名。图内扰动调用直接取自式 (29)，ell_k、tbar_X、X_k,out、gamma_out 直接取自式 (21)、(22)、(33)，没有新增公式或缩写。实施见[流程修正记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/receiver_flow_corrected_20261104/README.md)。

## 2026-11-04：有限差分来源范围及图内精简

复核 Metzler 2016 作者稿 PDF p.15、§V-B，原小节标题是 Monte Carlo method，该处给出随机高斯扰动下的一侧导数/散度估计；未将 Finite differences 用作模块名称。Metzler 2017 L-DAMP 的 PDF p.4–5 使用 Monte-Carlo approximation。前一条“Finite differences 对应既有 Metzler 依据”仅指操作思想来源，不能理解为原文逐字标签或与本文式 (29) 完全同形。本文中央差分、随机符号及协方差加权是既有稿件声明的适配。

Finite differences 的含义为有限差分，用微小扰动前后的函数值变化近似导数。术语本身不因作者要求精简图形而撤回；本轮仅删图内标签与扰动表达式，正文 IV-C 和式 (29) 保持。Gaussian site、Extrinsic 及其变量沿用既有来源，无新名称、无共同定义变化，不涉及 STMP/DU 同步。见[本轮来源和实施记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/receiver_concise_flow_20261104/README.md)。

## 2026-11-04：相位 AER 反转后的局部后验性质核对

沿用 conditional mean、conditional covariance、density ratio 和 expectation maximization 的既有术语，没有命名新算法。Dytso 等 arXiv:2104.01883v1 §IV Proposition 1、式 (22)、PDF p.5 给出条件均值 Jacobian 与条件协方差关系；Menon and Ong 2016 §2.2、§4.2、式 (16)–(17)、PDF pp.2,4 给出理想分类概率与密度比关系；Vila and Schniter 2013 §III、式 (19)–(23) 区分精确 E 步与近似后验。报告中的固定各向同性查询下 `grad ell = 2m/v` 是将条件均值关系与纯高斯噪声密度梯度相减所得的项目内推导，不冒称原文定理或已经满足的网络性质。

证据、适用条件和未完成检查见[本轮理论核对](../../result/snr_comparison/data/c_stmp_phase_frontend_marginal_1000_20261104/case0144_theory_check_20261104/REPORT.md)。本次未改正文公式或共用系统定义，不涉及 STMP/DU 同步。

## 2026-11-04：作者确认 GP-MP-C 命名

当前展示名称采用 **GP-MP-C** 与 **GP-MP-C-EP**，替代 GP-MP-CCD 与 GP-MP-CCD-EP；基线保持 GP-MP。GP-MP 是本文 generative-prior message-passing 的描述性名称，C 是作者确认的有色高斯噪声训练版本标记，EP 沿用 estimated phases。以上名称属于本文命名，不声称是参考论文的既有算法名称。

colored Gaussian noise / correlated noise 沿用已核对的 Shastri 正式版 §III-B、PDF p.8／印刷 p.535、式 (38)–(40)，对应本地作者稿 §III-B、PDF p.15 的 A DNN denoiser for correlated noise。本文的协方差结构和采样设置仍是明确登记的适配；C 不把这些细节归为原文同一实现。正文使用 trained with colored Gaussian noise，并直接说明协方差是额外网络输入，不再用 covariance-conditioned denoising 展开算法名。

仅统一本文展示名称和相关措辞，未变更模型、公式或共享定义，不涉及 STMP/DU 同步；内部 C_STMP 标识和历史记录保持。见[命名实施记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/algorithm_name_c_20261104/REVISION_NOTES.md)。


## 2026-11-04：第六、七章修订与矩阵预条件补引

沿用现有 preconditioning、channel-estimation performance、sparse-recovery baselines 等表述，没有命名新方法。新增引用 de Albuquerque and Pearson, Inflationary Flows, NeurIPS 2024，Appendix B.1 “Derivation of Training preconditioning Terms”，PDF pp.23–24，式 (67)–(68)、(73)、(77)–(78)。原文把输入、skip、输出的预条件系数推广为矩阵；取 Σ₀=σ_d²I 后对应本文现式 (42)。正文写 with matrix coefficients as in，来源范围只覆盖三个矩阵系数，不覆盖本文损失权重、网络、训练采样或接收机。

官方元数据及实施核验见[记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/chapters_vi_vii_language_selected_20261104/README.md)，数学对应沿用[已有来源核查](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/DAMPING_AND_FORMULA_PROTOTYPES_20261104.md)。本轮没有改变公式或共用定义，不涉及 STMP/DU 同步。


## 2026-11-04：第六章网络表与基线介绍

本轮采用 Cai 期刊版 VI-A2 / Table III（PDF p.11／印刷 p.3585）的网络表呈现方式，以及 VI-B/C（PDF p.12／印刷 p.3586）的加粗算法名列表。Network Architectures、residual stage、refinement block、channel denoiser、activity classifier 沿用本稿既有网络及 RefineNet/Song 引用；表内配置来自既有实现核验，不声称与 Cai 的网络参数相同。具体对应见[来源与段落映射](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch6_cai_revision_20261104/CAI_PARAGRAPH_MAP.md)。

GNN-ASPL 的 adaptive sparsity pattern learning 及 AMP 信道估计与 GNN 更新交替过程，核对 Ding §III-B、PDF p.4、式 (19)–(26) 和该节末段；正文保留原方法名和引用。GAMP-SBL 沿用原 Zhang 等引用，但共享行精度的多天线扩展明确写为 Our multiantenna implementation，依据 src/algorithm/baseline/gamp.py，不冒称已经重新全文核验 Zhang 原算法或逐项复现其设置。SOMP、Off-grid SBL 和 genie-aided conditional MMSE 继续使用既有名称和来源，没有另造缩写或新增方法名。

NMSE、AER、iteration-limit rate 和 paired scenes 含义保持；删除错误类别细分只是结果段落精简，不改变指标定义。无共用模型定义变化，不涉及 STMP/DU 同步。


## 2026-11-04：实验结果顺序与图例统一

Denoiser (AWGN) 和 Denoiser (colored) 为本稿已有去噪器的简短图例，AWGN/colored 指训练噪声，不把去噪器命名成完整 GP-MP/GP-MP-C 接收机。Genie MMSE 为既有 genie-aided conditional MMSE 参考的图例简称，定义继续在 VI-B。SOMP、GAMP-SBL、GNN-ASPL、Off-grid SBL 名称及原引用保持，仅统一视觉样式；跨信道 A/B/C/D 为原 NTN-TDL profile 名称，不是新模型。

结果分析沿用 Cai §VI、Figs.6–10（期刊 PDF pp.12–14）与 Shen §V、Figs.7–8（PDF pp.13–14）的代表性比较和固定资源解释方式。本文 0 dB 下 1.6 dB NMSE 差值由自己的 1000 场景数据计算，不移植文献结果；没有新增方法名或将完整接收机收益归因于单一模块。具体改动、图源及核验见[本轮记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch6_results_order_style_20261104/README.md)。无共用系统定义变化，不涉及 STMP/DU 同步。


## 2026-11-04：摘要明确生成式先验用于 GPJD 去噪

按作者反馈，GPJD 的功能从句明确写为 uses the learned generative prior for minimum mean-squared error (MMSE) denoising。该描述与现稿引言第三项贡献的 uses the learned effective-channel prior for MMSE denoising、第四章条件均值学习及第五章 GPJD 操作一致。generative prior、MMSE denoising 沿用本文件已登记的 Cai v2 §III-B1、§IV-A 依据；GPJD 沿用作者批准名称。属于本稿已有技术内容的句法澄清，不登记为文献原句，也未新增共用定义，无需修改 STMP/DU。中英文摘要及两版 PDF 同步，见[核验](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_gpjd_prior_20261104/README.md)。


## 2026-11-04：完整相位前端结果加入主 SNR 与附录 A 同步

- **CGP-MP-EP** 沿用作者已确认的估计相位版本展示名，本次明确绑定 `C_STMP_phase_frontend_marginal_20261104`，不是新提出的文献术语。其操作为先估计一次相位，再固定相位运行 CGP-MP；接收机内相位更新次数为零。此条覆盖此前边迭代边精化相位的方法描述，不改共用系统模型与 STMP/DU 定义。
- **Gaussian marginal likelihood / 高斯边缘似然**：沿用本文件“物理相位初始化的边缘似然对照”出处，Tipping–Faul (2003)，作者排版稿 §2.1、PDF p.3 式 (7)–(8)，[作者全文](https://www.miketipping.com/papers/met-fastsbl.pdf)；[出版元数据](https://proceedings.mlr.press/r4/tipping03a.html)已复核，AISTATS 2003, pp.276–283。新增参考文献键 `tipping2003`。
- 本稿附录 A.2 为独立复高斯增益与多天线列的必要适配；A.3 为本项目从该模型得到的坐标最优方差，不能登记为 Tipping–Faul 的同形原式或完整算法复现。由矩阵行列式引理和 Sherman–Morrison 公式，单用户贡献为 `log(1+γs)−γt/[M(1+γs)]`，求导得 `γ*=max(0,(t/(Ms)−1)/s)`。消去 γ 后以 `t/s` 排序并做连续位置搜索。完整推导保留于 `result/candidates/c_stmp_phase_init_marginal_20261104/README.md`。
- **L-BFGS-B** 继续采用 Zhu et al. (1997), Algorithm 778 的既有出处。128 个相位格点、3 个粗候选、12 个别名起点、每候选至多 25 次局部迭代和 2 轮坐标扫描均来自冻结的 `src/configs/final/phase.json`。当前位置继续作为候选；不据边缘目标下降声称 NMSE 或 AER 必然改进。
- 单路径与独立天线增益仅为相位前端工作近似；后端仅接收相位，仍使用既有学习先验和权重，不接收前端的功率、增益或硬活动判决。正文在相位附录与 V 章明确这一边界，B 附录补充复现细节。删除旧 LS/variable projection 和迭代相位更新段落，旧源码与 PDF 保存在本轮 before/ 中。
- 本轮属于新实验入稿所需的技术同步，不扩大为全文语言润色。第六章只新增范围性结果描述：相对已知相位参考，NMSE 增加 0.30–0.61 dB，AER 接近而非相等。原六条曲线不变，不宣称统计等价或有色训练机制已证实。


## 2026-11-04：EP 释义集中放在算法比较中

按作者要求，VI-A3 的 CGP-MP 条目说明 “EP denotes estimated phases”，并在比较列表前集中说明其余配置采用已知相位。EP 沿用作者已确认的展示后缀，不新增文献方法名；相位方法、来源和结果仍沿用前条。删除图注及实验设置中的重复说明，保留方法附录与完整稿评估协议的技术定义。


## 2026-11-05：相位估计改为正文 V-B

按作者确认，将原相位附录的多帧响应和 Gaussian marginal-likelihood objective 移入 V-B，解析功率更新推导留在[内部文档](derivations/phase_estimation.md)。phase estimation 指 MP 前估计一次并在后续固定；不重新使用迭代相位更新的旧描述。Gaussian marginal likelihood 沿用 Tipping–Faul (2003) §2.1、作者稿 p.3 式(7)–(8)，复高斯多天线形式为项目既有适配；L-BFGS-B 沿用 Zhu et al. (1997), Algorithm 778。搜索参数归入 VI-A4，配置与含义不变；无共用模型定义变更。

## 2026-11-05：第二点贡献中的信道先验与不确定性量化

- **generative channel prior / 生成式信道先验、channel denoiser / 信道去噪器**：沿用 Cai 的生成式先验与 MMSE 去噪、Huang 的有效信道学习对象。重新核对 Huang 期刊版 PDF pp.1,3（印刷 pp.2949,2951），摘要、贡献 (i)、§III-A/B 式 (7)–(10)。本文描述多天线 AFDM 有效信道学习与消息传递中的使用，不将学习先验等同于对先验密度进行条件均值参数化。
- **uncertainty quantification / 不确定性量化**：采用 Manor–Michaeli ICLR 2024 论文标题、摘要及 §I（PDF pp.1–2）的原词，限指本稿的平均后验方差近似；不主张已证明概率校准。Dytso 正式版 §III Proposition 1、式 (17)，PDF p.3／印刷 p.1885，为均值导数与条件协方差关系的来源；已有的随机方向数值估计仍见第四章。
- **second-order training targets depend on first-order score estimates**：本文对 Cai v2 §IV-C、式 (52)–(54)、PDF p.9 的忠实概述，不登记为原文逐字表达。Cai 允许顺序或同时训练；本稿的同一去噪器均值/方差计算省去此额外训练依赖，并不消除去噪器导数的估计误差。
- “single trained denoiser” 和“不为方差估计额外训练”描述本稿具体实现，参照 Manor–Michaeli 的已训练去噪器不确定性估计；不是新的方法名。无后验采样是当前推断流程的既有性质，Cai 也具有该性质，不据此宣称首创。

仅调整 C-STMP 摘要与引言的贡献呈现，不改变共享数学定义，故不涉及 STMP/DU 同步。[修订与验证](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/second_contribution_restore_20261105/README.md)。

## 2026-11-05：候选第二点补入 Tweedie 公式的衔接

重新核对 Cai v2 §IV-A “Bridging Score Function and MMSE Denoising”，式 (44)、PDF p.8：Tweedie's formula 联系受扰数据的 score function 与 posterior mean，用于构造 MMSE denoiser。候选中的 “Using Tweedie's formula to relate the score function to the posterior mean” 为忠实概述，不是原文逐字引用。后续 variance 关系沿用 Dytso 正式版 §III、式 (17) 和 Manor–Michaeli §3.2、式 (11)；本文实际计算 average posterior variance，其学习与数值误差保留。

中文“耦合”具体指 Cai v2 §IV-C、式 (52)–(54)、PDF p.9 中二阶学习目标使用一阶估计的依赖，英文候选直接描述该依赖，不造 “coupled-score” 方法名。training and storage 开销只归属于被省去的独立二阶模型，不作为整体推理速度或总模型规模的实验证据。候选尚未入稿，见[最新讨论](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/WHITE_MAINLINE_REVISION_PLAN_20261105.md)。

作者随后确认采用这条数学链及中文三句。现已写入中英文摘要和引言第二项；上述术语、出处和收益范围均保持，状态由候选转为已实施。英文表述使用 “the dependence of second-order score learning on first-order score estimates” 和 “the additional training and storage required by a separate second-order model”，不新增方法名称，不改变共用数学定义。见[采用记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/second_contribution_adopted_20261105/README.md)。

## 2026-11-05：独立 NTN GBRA 前导码检测选题调研

本条仅对应[独立调研](https://github.com/RESET-cpu/afdm-gfra/blob/fb2815c5b10a753b12e3bdecd4d4659d4f49b692/paper/docs/NTN_GBRA_PREAMBLE_REVIEW_20261105.md)，不改 CGP-MP 稿件或共用系统定义，无需同步 STMP/DU。

- **preamble collision / 前导码碰撞、collision multiplicity / 碰撞人数、zero-correlation zone (ZCZ) / 零相关区**：Lee et al., arXiv:2512.07053v3（2026-06-02），§III、§IV-B，PDF pp.5–7；[原文](https://arxiv.org/html/2512.07053v3)。前导存在、碰撞人数与具体 UE 身份分别讨论，不把公共前导索引当唯一身份。
- **carrier frequency offset (CFO) / 载波频偏、coherent combining / 相干合并、power combining / 功率合并**：Alarcón-Martín et al., arXiv:2512.03096v1，§III-B/D、§VI；[原文](https://arxiv.org/html/2512.03096v1)。该文 §III-A 的理想开环功控与时间对齐是原假设，报告中非理想情形属于待验证扩展。
- **generalized likelihood ratio test (GLRT) / 广义似然比检验、peak validation / 峰验证**：Khaleghi–Lucidarme 2026，§2–5；[正式论文](https://www.mdpi.com/2079-9292/15/13/2798)。§6.2 的联合多用户处理范围限制单独注明。
- **near-far effect / 近远效应、parallel interference cancellation / 并行干扰消除**：Wang–Ren–Wu 2017，出版社 Abstract，论文 pp.104–116；[原始摘要](https://link.springer.com/chapter/10.1007/978-981-10-4403-8_10)。仅据摘要确认已有主题，不据此复原其全部算法。
- **residual frequency error / 残余频率误差、residual time error / 残余时间误差**：Lin 2025，正式摘要，JIOT 12(15):29961–29974；[作者机构记录](https://scholars.ncu.edu.tw/en/publications/estimation-of-residual-frequency-and-time-errors-on-nprach-in-non/)。该文是 NPRACH，不能将其波形结构直接等同于 NR PRACH。
- 报告中的同前导不可区分例子是线性叠加模型的直接推导，不命名新定理；两个建议题目是描述性工作标题，不是文献方法名。功率、空间相关与残余不同步的联合研究方案尚未完成实验，不能登记为已有性能结果。


## 2026-11-06：白噪声训练表述统一至实验设置与附录

本轮沿用第四章已有白噪声模型与术语，不引入新的方法名称或共用系统定义。proper complex white Gaussian noise 对应复协方差 vI_D，实、虚堆叠后的协方差为 (v/2)I_{2D}；沿用 Neeser (1993) 的 proper complex Gaussian 定义及本稿第四章训练观测公式。均值损失继续使用 1/(Dv) 权重，不改为未加权均方误差。标量 preconditioning 沿用已核对的 Karras (2022) Table 1、§5 式 (7)–(8)，取名义实坐标方差 σ_d²=1/2。

删除第六章的协方差因子采样、额外协方差条件输入及矩阵预条件推广，移除该处 Albuquerque–Pearson App.B.1 引用；书目库与历史出处记录保留。实际引用因此由 43 篇降为 42 篇。附录中的方法定义同步为白噪声去噪器，并保留比较完整接收机配置的范围说明。

工作稿数据说明是项目状态陈述，不是文献术语：图 5 和表 III 已采用白噪声网络，图 4、6–10 仍保留历史权重结果；保存的图数据未改，其比较不能归属于尚未替换的白噪声结果。正文仅集中注明 earlier checkpoints with different training perturbations，不再展开旧训练模型。此项仅针对 GP-MP 的当前写作版本，无 STMP/DU 共用定义变化。见[修订与验证](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/white_noise_wording_20261106/README.md)。


## 2026-11-06：确认后的摘要定稿

作者确认采用聊天中逐句审阅的最终摘要。英文 212 词，中文摘要同步；本轮仅调整摘要，不改变数学定义或引言。

- uncertainty quantification / estimation uncertainty：Manor–Michaeli, ICLR 2024，摘要、§3.1–3.2 式 (11)、§4.1 式 (15)；数学依据为 Dytso 等正式版 §III Proposition 1、式 (17)、印刷 p.1885。摘要正面描述同一去噪器提供信道估计和估计不确定性；本文具体量为平均方差，不声称完整分布重建。原文：https://arxiv.org/html/2309.13598v2 。
- density-ratio estimator / likelihood ratio / marginal likelihood：Menon–Ong, ICML 2016，§1、§3 式 (6)–(8)、§4.2 式 (16)–(17)，印刷 pp.304–306，https://proceedings.mlr.press/v48/menon16.pdf 。直接从样本估计比值的动机来自原文；绕过本文活动判决中的边缘似然计算，是依据本稿 §III-B2 的信道积分及 §IV-D 的分类密度比构造作出的应用说明，不冒称原文研究 AFDM 或本项目接收机。
- Additional pilot frames ... without increasing the number of channel coefficients：依据本稿 §II-B 的跨帧相位吸收及共同未知信道表示；不是新方法名称，也不表示原始各帧信道无相位变化。
- fewer pilot frames to reach the same channel-estimation target：依据现有 §VI 导频实验，已评估帧数中 GP-MP 在 Q=24 达到 −14 dB NMSE，而 STMP 为 Q=32；摘要未新增实验或扩大指标范围。

最终文字、修改前副本及核验见 [摘要采用记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/abstract_final_20261106/README.md)。


### 2026-11-06：作者补入 time and frequency precompensation

采用作者的 time and frequency precompensation 表述，指设备侧对时延及多普勒偏移的预补偿。与本稿 §II-A、§I 已有定义一致；原有文献依据沿用 Shen 摘要（PDF p.1：GNSS 非辅助终端、在卫星接收端处理大差分时延及多普勒）及正文既有 shen2025 引用。此为既有系统设定在摘要中的明示，不是新增方法名称或同步假设。


## 2026-11-06：最终引言中的三项贡献表述

本轮采用作者确认的精简表述，不引入新方法名称或共享模型定义；MFLE、GPJD 沿用本稿既有模块名，不将其作为原始文献中的名称。

- **effective channels across frames / Doppler-induced phase rotations / shared effective channel matrix**：本稿第二章多帧关系 `H^(q) = exp(j q beta) H` 的文字说明，适用条件仍由该章共同多普勒及块内路径参数设定给出。Shen (2025) §II-B、式 (9) 为多帧 OTFS 三维有效信道表示的比较对象；紧凑性条件沿用本稿第二章比较，不声称跨帧共享本身为相对 Shen 的独有性质。
- **Tweedie's formula / denoiser derivatives / estimation uncertainty / average variance**：Tweedie 到均值的衔接参照 Cai (2026) §IV-A、式 (44)；均值导数到协方差依据 Dytso 等正式版 §III Proposition 1、式 (17)，印刷 p.1885。Manor–Michaeli (ICLR 2024) 摘要、§3.2 式 (11)、§4.1 式 (15) 支持从已训练去噪器及其导数估计不确定性、无需额外训练。引言的“denoiser derivatives and estimation uncertainty”是上述关系的忠实概述，不是新定理名称；本文取平均方差，不声称原文采用完全相同的数值估计器。Cai §IV-C、式 (52)–(54) 是单独二阶训练模型及训练依赖的来源。
- **density ratios / class probabilities / density-ratio estimator**：Menon–Ong (ICML 2016) §3、式 (6)–(8) 及 §4.2、式 (16)–(17)，印刷 pp.305–306，说明二分类类别概率与密度比的关系。原文：https://proceedings.mlr.press/v48/menon16.pdf 。在本文 GPJD 中绕过显式边缘似然计算是该关系对活动检测的应用，参照本稿第三章活动边缘似然和第四章分类器构造；不把 AFDM 接收机归于 Menon–Ong。
- **fewer pilot frames ... same channel-estimation accuracy**：沿用现有第六章导频结果与已确认摘要的结论范围，指已评估场景的信道估计目标，不扩展为同时达到任意活动检测指标的普遍结论。

本次仅修改引言呈现方式，无 STMP/DU 共用定义变更。见[采用与核验记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/introduction_final_20261106/README.md)。


## 2026-11-06：结论与摘要／引言同步

结论继续使用已确认的 GNSS-independent GFRA、multi-frame AFDM、score-based generative prior、MFLE、GPJD、density-ratio estimator 和 marginal-likelihood evaluation。MFLE、GPJD 为本稿既有模块名称；channel estimates and average variance 概括本稿去噪器输出与方差估计，不改变数学定义或精度主张。其 Manor–Michaeli、Dytso、Menon–Ong 技术来源沿用前述引言记录，不归于 Cai／Shen。

段落组织对照 Cai 期刊版 §VII（PDF pp.14–15／印刷 pp.3588–3589）及 Shen 本地版本 §VI（PDF p.15），两处完整结论均已读取。Cai 支持消息传递与生成模型结合的简洁总结方式；Shen 支持场景、传输方案、接收算法、定性实验结果的推进顺序。本文共享 AFDM 表示、单去噪器方差和密度比活动更新均按自身内容改写，不声称母本包含这些结论。句级映射及具体适配见[结论对照记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/conclusion_alignment_20261106/REFERENCE_ALIGNMENT.md)。无新术语、引文或 STMP／DU 共用定义变更。


## 2026-11-06：语言润色沿用的术语及原段

本轮不新增方法名、缩写、数学定义或共用系统条件。doubly dispersive、terrestrial-satellite links、Bayesian inference framework、Gaussian extrinsic messages、denoising score matching、NMSE 和 genie-aided reference 均沿用既有含义。

Shen §II／II-A（本地 PDF p.3）提供卫星链路模型原段；Cai §II-B／III（PDF pp.4–5／印刷 pp.3578–3579）提供推断目标与两模块交换原段；Cai §IV-B（PDF pp.8–9／印刷 pp.3582–3583）提供未知边缘 score 与条件 Gaussian score 的 DSM 关系；§VI-B/C（PDF pp.12–13／印刷 pp.3586–3587）提供去噪器及按 NMSE 比较结果的组织。本文实坐标系数、单去噪器方差估计、相位估计流程及实际实验趋势均保留本稿归属。

Huang 摘要／§I（PDF p.1／印刷 p.2949）和 Xu 接受稿摘要／§I（PDF p.2）仅作为领域语境辅助阅读，不声称每一改句来自这些论文。网络版本说明、配对条件和相位执行者等为本稿实现／协议的普通语言调整。14 项改前改后及实际出处支持层次见[语言润色记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/language_polish_20261106/LANGUAGE_EDITS.md)；无需同步 STMP／DU 共用定义。


## 2026-11-06：第 II–VI 章叙述修订中的用词与出处

本轮沿用现有术语和方法定义，不新增方法名、缩写或共享模型条件。MFLE/GPJD 保留为作者已确认的模块名称。derivative-based variance estimate 是对既有均值导数方差计算的描述，不登记为新方法名称。

Cai 期刊版 §III/III-B（PDF pp.5–8，印刷 pp.3579–3582）支持 Gaussian 输入、活动假设下的去噪、Bernoulli–Gaussian 矩及 Gaussian extrinsic messages 的组织；§IV-A/B（PDF pp.8–9）支持 score functions、DSM 与跨噪声水平训练的衔接；§V-A/B、复杂度及 §VI-A/B（PDF pp.9、11）分别用于接收机构成、阻尼、计算量与网络/实验段落组织。本轮实际读取完整相关段落，不把本文改写登记为原文逐字表达或严格逐段对应。

III-B3 关于信道与活动不确定性的句子解释本稿已有协方差两项，并与已确认引言一致，不是新增定理。IV-C 沿用 Dytso §III Proposition 1、式 (17)，印刷 p.1885，以及 Manor–Michaeli §3.2 式 (11)、§4.1 式 (15) 的既有核对；IV-D 沿用 Menon–Ong §3 式 (6)–(8)、§4.2 式 (16)–(17)，印刷 pp.305–306。Gaussian site 继续沿用 Vehtari §2.1；相位、噪声与阻尼术语沿用对应既有来源。单次相位估计与学习信道先验的用途采用正面陈述，技术边界仍保持。

第二章共享信道与相位关系属于本稿已有 AFDM 推导；Shen §II/II-A（本地 PDF p.3）仅提供场景和模型组织参照。第六章网络、训练参数与比较协议均属本稿设置，未将其归于 Cai。无 STMP/DU 共用定义变更。具体位置、改前改后和来源层次见[修订记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/chapters_ii_vi_narrative_20261106/REVISION_NOTES.md)。


## 2026-11-06：第四章三个小节的估计对象

采用 Channel Mean Estimation、Channel Variance Estimation、Activity Probability Estimation，分别概括本稿已定义的活动假设下信道条件均值、平均条件方差和后验活动概率。这是章节组织名称，不是新增算法术语；正文 conditional/posterior 的数学含义保持。Cai §III-B1/2（PDF pp.6–7，式 (22)、(23)、(30)）给出均值、方差及活动概率的原始语境；Tweedie 与 DSM 沿用 §IV-A/B（PDF pp.8–9）的既有核对。

本稿方差估计继续采用 Dytso 正式版 §III Proposition 1、式 (17)，印刷 p.1885，及 Manor–Michaeli §3.2 式 (11)、§4.1 式 (15)；活动概率继续采用 Menon–Ong §3/§4.2 的分类密度比关系。小节重组不改变这些技术归属，也不改变 STMP/DU 的共享定义。原 IV-C/IV-D 的历史位置分别对应当前 IV-B/IV-C；公式编号迁移见[本轮记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch4_moments_activity_structure_20261106/README.md)。


## 2026-11-06：第四章得分目标与方差推导的衔接

- **score of the perturbed channel distribution / mean-squared error**：Cai 期刊版 §IV-B，式 (46) 为扰动后分布得分的均方匹配目标，式 (47) 及相邻段落给出 DSM 与该目标的关系（PDF pp.8–9，印刷 pp.3582–3583）。本稿 IV-A 将原来未解释的 score matching objective 写明为该目标；沿用 Vincent (2011) 引用，不新增技术主张。
- **mean Jacobian / covariance trace / average variance**：均值导数关系依据 Dytso 正式版 §III Proposition 1、式 (17)，印刷 p.1885；正文新增句是本稿式 (28)、(31) 到式 (32) 的直接代数衔接。只需协方差迹的叙述与 Cai §IV-C 式 (53) 前段（PDF p.9，印刷 p.3583）的估计目标相应；本稿采用均值导数及随机方向估计，技术依据仍为 Manor–Michaeli §3.2 式 (11)、§4.1 式 (15) 以及既有 Metzler 引文，不将其归于 Cai 的二阶网络训练方法。

本轮是已有术语和公式关系的解释，无新方法名称或 STMP/DU 共用定义变更；新增句为本文适配叙述，不是对参考论文原句的逐字转载。

## 2026-11-06：引言 AFDM 的低复杂度调制表述

- **low-complexity modulation structure / one-dimensional chirp signals**：Ding §I（本地 `reference/literature/ding2026.pdf`，PDF p.1）以一维 chirp modulation 说明低复杂度；Huang §I（`reference/literature/huang2026.pdf`，印刷 p.2949）以一维 IDAFT 说明实现复杂度。本稿采用其低复杂度背景动机，不逐字搬用相对 OTFS 的一般比较，也不将此性质计作本文新贡献。该句为依据原文含义的改写。
- **inverse fast Fourier transform / pointwise chirp multiplication**：Bemani、Ksairi、Kountouris，TWC 2023，arXiv:2204.12798v2 §II-B 式 (16) 后的逆矩阵表达式与 §III-A 式 (18)：IDAFT 分解为两个对角啁啾矩阵与一个逆 DFT。一次 IFFT 与两组逐点啁啾乘法是该分解的实现描述，不是本文新增算法；正文保留相应章节引用。
- **full diversity / doubly dispersive channels / chirp parameters**：沿用 Bemani §III-E、§IV 的原有依据与有条件表述。

本轮移除背景段中本文 stationary-device 跨帧模型的提前说明，相关模型与第一项贡献保持。无共用模型定义或 STMP/DU 术语变更。具体修改见 [本轮记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/afdm_intro_complexity_20261106/README.md)。

随后作者指出满分集对本文接入问题的动机作用有限，已删除引言第三段的满分集句。上列 full diversity 出处保留为历史核验，不表示当前背景段仍使用该主张；低复杂度调制与 IFFT/逐点啁啾乘法两句及其引用保持。


## 2026-11-06：引言活动更新的高斯近似与密度比衔接

- **Gaussian extrinsic messages / projecting the channel posterior onto a Gaussian distribution**：Cai 作者稿 §III-B，PDF pp.6–7，式 (17) 及其后说明、式 (24)–(30)。前者为原文术语，后者为对 moment-matching Gaussian projection 的忠实描述；句子是操作概述，并非逐字引文。
- **posterior mean and variance / marginal likelihood**：本轮保留非高斯后验矩匹配一般不保留边缘似然的分析。此为本稿数学判断，不归为 Cai 的性能结论，也不把局部矩的信息局限扩大为完整得分函数无法恢复密度。
- **density ratios / class probabilities / activity likelihood ratio**：Menon–Ong §3 式 (6)–(8)、§4.2 式 (16)–(17)，pp.305–306，提供密度比与类别概率关系；activity likelihood ratio 是本稿第三章两活动假设似然比及第四章分类器应用的描述，不是新算法名。绕过显式边缘似然计算及上述高斯投影是本稿应用方式，不是对 Menon–Ong 原文应用场景的陈述。

本轮无新术语定义或 STMP/DU 共用模型变更。具体句级归属、修改前后及编译检查见[本轮记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/activity_intro_revision_20261106/README.md)。


## 2026-11-06：引言两句删除后的出处状态

作者确认删除背景段的 three-dimensional tensor 句及相关工作段的 second-order training targets depend on first-order score estimates 句。此前 Shen §II-B 和 Cai §IV-C 式 (51)–(54) 的核验记录仍作为历史出处保留，不表示当前引言仍含这两句，也不否定其事实。当前第一项贡献/第二章的信道表示比较及去噪器导数、不确定性相关表述保持。无新术语或 STMP/DU 共用定义变更。见[本轮记录](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/intro_causal_cleanup_20261106/README.md)。


## 2026-11-07：第三章条件信道矩与高维积分的表述

沿用 conditional mean、average variance、channel prior、high-dimensional integrals、Bernoulli–Gaussian approximation、Gaussian extrinsic messages，无新增方法名或缩写。Cai 作者稿 `cai2026_stmp_v2.pdf` §III-B1，PDF p.7，式 (22)–(23) 及其后段落，支持“定义后验矩，再指出高维积分困难”的技术语境；§IV 首段与 IV-A，PDF p.8，支持下一章再给出 score 表示与学习计算的分工。本轮已重新读取完整相关段落与相邻内容，正文是适配本稿 q_tr、H_k 和平均方差定义后的改写，不是逐字引文。

活动概率中 q_1 的高维积分困难是本稿既有观测密度公式的直接说明；Cai §III-B2 式 (30) 为高斯外信息下的解析活动更新，不作为该分支的相同算法依据。III-B3 继续使用原有 Liu/Cai 引文，只调整已定义统计量到联合近似的叙述顺序。没有修改共用定义，不需同步 STMP/DU。[逐项改动与支持范围](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/ch3_framework_boundary_20261107/README.md)。


## 2026-11-08：逐句核验后的术语与对象确认

- **array response vector**：恢复既有 Li–Gao–Xia §II-B 式(2)及相邻阵列段的完整名称；本轮读取版本见逐句记录 II-016。正文说明同设备路径共享该向量，公式保持。
- **posterior spatial covariance**：III-B3 的 M×M 矩阵沿 N² 个信道系数求平均，空间维保留；不能将其平均对象写成 across antennas。它来自本稿 Bernoulli–Gaussian 混合矩的直接计算，Cai III-B3 提供混合矩到外信息的论证顺序。
- **Gaussian approximation to the posterior**：近似对象为后验分布，均值为点估计；III-030 明确对象，不改原矩或回传更新。
- **Monte Carlo method / divergence**：Metzler 作者稿 [arXiv:1406.4175](https://arxiv.org/pdf/1406.4175)，§V-B、PDF p.15；本文中央差分和随机符号方向沿用既有推导。IV-023采用原方法名称并直接说明中央差分。
- **negative log marginal likelihood**：本稿 logdet+trace 为最小化的负对数目标。Tipping–Faul [PMLR正式PDF](https://proceedings.mlr.press/r4/tipping03a/tipping03a.pdf)，§2.1 式(7)–(8)在PDF第2页；此前作者排版稿页码属于另一版本。多列复Gaussian形式仍为本文适配。
- **average conditional variance**：VI的 tau_min 对应 V 中汇总的条件方差 tau^post，不是系统噪声方差。训练两类别的白Gaussian扰动用 vI，系统观测噪声用 sigma²I；正文明确各自对象。

完整句子、精确来源与处理见 [逐句核验](SENTENCE_REVIEW_20261108.md)。

## 2026-11-08：第二章经作者逐段确认后入稿

作者确认采用聊天中的第二章原段适配稿，并用随后核实的三句建模假设替换其中的初稿表述。总述、物理链路、多帧组织及跨帧讨论以 Shen 第二章（本地 PDF pp.3–5）为段落底稿；导频、活动变量、观测矩阵及后验分解以 Cai 正式版第二章（PDF pp.3–4，印刷 pp.3577–3578）为底稿。AFDM 波形和本文矩阵排列按本稿模型适配，不归为 Cai/Shen 的相同公式。

- **common Doppler shift**：Huang §II，式(2)及后段，PDF p.2／印刷 p.2950，以静止地面用户为参考，并明确同一 S2G 链路各路径共享 Doppler term；原文理由还包括较远星地距离下较小的路径角度差异。正文保留 `is assumed to be common to all propagation paths`，不把静止本身当作充分条件。
- **common array response / angles of arrival**：Li–Gao–Xia §II-B，PDF p.4、式(3)之前，说明长距离使同一用户不同路径的 AoAs 趋于一致，并给出 θ_(k,q)=θ_k、g_(k,q)=g_k；本稿 a_k 对应其 g_k。该因果与共同 Doppler 分开陈述。
- **approximately constant in the delay-Doppler domain**：Shen §II-B，式(10)后，PDF pp.4–5，明确有效信道在连续 Q 帧内近似不变，并分析 delay/Doppler 的变化。本稿采用该准静态假设，不再把路径增益、时延、多普勒及到达角四项罗列登记为 Shen 的直接原句；跨帧相位仍显式保留。
- **Kronecker product**：Shen Notations，PDF p.3，原词 `⊗ denotes Kronecker product`。本稿 H_k 的 Kronecker 形式是原各天线转置信道横向拼接的代数等价式，维度 N×MN；普通转置及天线排列保持。
- **unit-gain path / effective pilot matrix / block-sparsity structure**：沿用本稿已定义的单径响应、相位并入导频和活动零块；删去 D_(ν,g)、B_d、H_(k,m)、g_q 等中间记号不改变其运算。Cai §II-A、式(4)后（PDF p.4）支持 block-sparsity 的表达；P 的行正交条件没有转移为 A 的行正交假设。

本轮直接读取的本地来源：Shen `/Users/wangbo/Desktop/OTFS/shen2025_large_differential_delay_doppler.pdf`；Cai `/Users/wangbo/Desktop/桌面 - 王博的MacBook Pro/论文/JADCE/(2026 JSAC) Joint_Activity_Detection_and_Channel_Estimation_for_Massive_Connectivity_Where_Message_Passing_Meets_Score-Based_Generative_Priors.pdf`；Huang 和 Li 分别为 `/Users/wangbo/Desktop/科研/hybrid access/references/satellite_parameter_review_20261018/huang2026.pdf` 和同目录 `li2023.pdf`。正文仅保留文献编号，精确定位保存在本条。

### 第二章再次审阅后的三处适配修正

作者确认本轮审阅建议后，共同多普勒句中的 satellite-to-ground link 改为已定义的 TSL，以适配本文上行场景，Huang 的共同多普勒假设及引用保持。跨帧式前明确共同 ν_k 与帧起点变化的因果，属于本稿式(7)的直接结果；式后采用 Under the quasi-static assumption，保持 approximately constant。Shen §II-A 式(1)（PDF p.3）是时延–多普勒–空间域表达，本稿式(1)是 h_k(t_c,τ)，因此删除此前由母句迁移而来的 of (1) in the delay-Doppler domain 回指，准静态依据仍为 Shen §II-B、PDF pp.4–5。式(9)前明确 effective pilot matrix 名称；后验引式沿用 Cai §II-B 式(5)前的 Bayes/独立性表述，调整主语及条件位置。没有新增术语、引用或模型假设。

### 两项信道假设的简短依据

共同 Doppler 句补入 `the long satellite-to-ground distance leads to only a small angular spread across multipath components`，直接依据 Huang §II、式(2)后解释句（PDF p.2／印刷 p.2950）。随后共同 AoA 句承接同一物理原因，Li 的引用及共同阵列响应定义保持。

跨帧准静态段采用 Shen §II-B、式(10)后（PDF p.5）的“代表性仰角与帧数→参数变化→短块近似”顺序，数值按本文配置重新计算。取圆轨道、轨道面内固定地面设备、初始仰角50°，地球半径6371 km、轨道高度600 km、载频2 GHz、光速299792458 m/s、地球引力常数3.986004418e14 m³/s²；卫星速度7561.7331 m/s。N=16、N_CPP=336、带宽480 kHz，Q=16给出T=11.733333 ms。块内固定共同延迟参考。

令r_s=R+h、ω=sqrt(μ/r_s³)、γ=acos[(R/r_s)cos(50°)]−50°，沿轨接近设备的斜距为r(t)=sqrt[r_s²+R²−2r_sR cos(γ−ωt)]。由ν(t)=(f_c/c)r'(t)、Δτ=[r(T)−r(0)]/c，得到|Δν|=3.333378 Hz、|Δτ|=0.173851 μs（0.083449 T_s）。固定初始Doppler的块末相位偏差为2π(f_c/c)|r(T)−r(0)−r'(0)T|=0.122869 rad。正文分别取3.33 Hz、0.174 μs、0.123 rad；此为所述代表性几何的计算例子，未作为接收机实验结果。独立计算一致，编号公式和参考文献保持。


## 2026-11-08：第三章确认稿的句式来源与标量方差精简

作者允许以 Cai、Shen 等论文的用句和段落推进为依据，并按本文模型适配。第三章采用已在聊天逐段展示的五组修订；本条区分原文依据与本文公式解释，不将适配后的整句标为逐字引文。

- **逐列线性估计与逐设备块去噪**：Cai 正式版第3579页、§III首段，原句含 `separately estimates each column of X`、`Module B is a denoiser of Xk exploiting the priors`。本稿将两模块职责用 while 连接，并代入多帧似然、完整设备信道矩阵及活动先验。
- **Gaussian posterior / mean and covariance**：Cai 第3579页、§III-A式(6)后，先说明两高斯密度的乘积仍为高斯，再求均值和协方差。本文压缩成引式句，保留一般有效导频矩阵下的完整均值、协方差公式。
- **模块输入、输出与回传**：Shen 作者稿PDF第6页右栏、§III-A，原文采用 `processes the received signal Y along with this soft message`、`is returned ... as the likelihood` 和 `takes ... as input and produces the soft message`。本稿按两模块关系衔接；末尾回传同时对应 Cai 第3582页、§III-B末段的 `serving as the prior message of module A in the next iteration`。未引入 Shen 的 GAMP、三模块划分或不同先验。
- **联合矩及共同标量方差**：Cai 第3581页、§III-B3式(32)–(38)，提供 Bernoulli–Gaussian 混合均值、方差及平均投影顺序。本文不再展示 U_k、C_X,k 中间层，直接保留 tbar_X=(1/K)sum_k[p_k t_k+p_k(1-p_k)||H_k^post||_F²/D]。等价性来自 tr(U_k U_k^H)=||H_k^post||_F² 和 D=MN²；原式(23)删除，原式(24)现为(23)。
- **两项方差解释**：`conditional channel variance` 沿用本文已定义 t_k；第一项是 p_k 加权的条件方差，第二项为活动不确定性，是本稿混合矩公式的直接解释。`activity uncertainty` 可见 Cai §III-B1、式(15)后。本句按本稿公式适配，不声称是 Cai/Shen 的完整原句。

III-B1、III-B2的原有文字及近似号保持。原 `posterior spatial covariance` 核验作为历史记录保留；当前正文改为直接标量表达。当前实现仍可能计算空间矩阵，其复杂度计数保持。

来源：Cai本地正式版 `/Users/wangbo/Desktop/桌面 - 王博的MacBook Pro/论文/JADCE/(2026 JSAC) Joint_Activity_Detection_and_Channel_Estimation_for_Massive_Connectivity_Where_Message_Passing_Meets_Score-Based_Generative_Priors.pdf`；Shen本地作者稿 `/Users/wangbo/Desktop/OTFS/shen2025_large_differential_delay_doppler.pdf`。正文仍仅使用文献编号。


## 2026-11-08：第四、五章确认稿的表达依据与联合核验

- **得分网络与训练目标**：Cai 正式版 §IV-B、印刷第3582页、式(46)–(48)采用未知得分、参数化网络、DSM 目标的推进；Vincent 的 DSM 等价关系支持本稿已有训练目标。本文按实表示的噪声方差 v/2 与去噪器参数化适配，两个固定 v 下的最优解说明均保留。
- **conditional covariance / normalized trace / average variance**：Dytso 作者稿 §IV、Proposition 1、式(22)、PDF第5页给出均值导数与条件协方差关系；Manor–Michaeli §3.2式(11)、PDF第4–5页及 §4.1式(15)、第6页支持由去噪器估计不确定性的技术路线。Cai §IV-C、印刷第3583页、式(53)前先说明只需协方差的迹。本稿采用自身的导数方差方法，不采用 Cai 的第二个得分网络。
- **Monte Carlo method / variance estimate**：Metzler §V-B、PDF第15页为散度数值估计依据；本稿随机符号方向与中央差分保持原公式。本次只明确结果是 variance estimate。
- **estimated log likelihood ratio / activity update**：Menon–Ong §3式(6)–(8)及 §4.2式(16)–(17)、PDF第3页，支持类别概率与密度比联系。本文使用平衡训练、同一方差采样分布和已有活动先验，先说明训练输出的估计对象，再代入对数几率式。
- **Gaussian site / update / retained parameters**：沿用 Vehtari 等的 site 术语与本文原公式。更新条件及保留分支直接来自本稿 Algorithm 1 和 src/receiver/stmp/denoiser.py 第123–138、171–180行，属于本文实现说明。正文顺序为条件、更新式、另一分支、与当前似然的组合。
- **single path / common Doppler shift / line-of-sight component**：单径近似及相位处理为本文原有方法；补入的动机来自本稿第二章共同 Doppler 与第六章默认 NTN-TDL-D/既有 Rician 参数。没有将多径模型改为精确单径模型，也不将本稿该近似归为 Cai/Shen 的算法。
- **recursive damping / expected Gaussian negative log likelihood**：沿用 Rangan 与 Vila 的原引文和术语。按本稿实际顺序先输入阻尼，再使用 kappa^(i)bar_v^(i)，联合去噪后更新下一轮比例，最后反馈阻尼。Cai §V-A/B、印刷第3583–3584页及 Shen §III-A、PDF第6页和 §III-C 的算法整合段支持按消息流组织的表达；具体方差更新及执行时序仍以本文公式和实现为准。

本轮无新缩写或方法名。以上区分文献中的组织/用语依据与本文公式的直接说明，不把适配后的句子标为整句原文。Cai/Shen 使用本文件前条所列本地 PDF；其余技术来源沿用此前逐句核验对应的本地原文与定位。


### 2026-11-08：Gaussian site 段的推导与执行分工

Cai 正式版第3581页（PDF第7页）§III-B1式(26)–(27)给出高斯外信息相除，§III-B3式(33)–(34)给出与输入消息的组合；第3584页（PDF第10页）Algorithm 2 第13行直接调用外信息更新式。本文保留对应推导及既有 site 术语；方差条件与参数保留规则保留在本稿算法表中，以现行实现为依据。上述文献位置支持外信息推导的表达，不作为本文条件保留规则的来源。本次仅调整叙述分工，无新术语或算法变化。


## 2026-11-08：第三章原段适配稿正式采用

第三章以 Cai 正式版第三章为段落及用句依据，采用本文的 MP 框架、逐列线性估计和逐设备块联合去噪表达。精确段落映射及已采用的文字调整见 [第三章来源记录](../checks/ch3_5_proposal_20261108/ch3_minimal_sources.json)。以下位置均为此前已核对的本地正式版 PDF。

- **message-passing framework / sum-product rule / expectation propagation / linear estimator / joint denoiser**：Cai 第3579页（PDF第5页）第三章首段给出两个模块迭代及其估计对象。本文使用功能描述，具体接收机和模块命名由第五章算法介绍。
- **Gaussian belief / LMMSE estimator / scalar variance / extrinsic message**：Cai 第3579–3580页 III-A，原式(6)–(11)。本文保留一般有效导频矩阵下的均值矩阵和列协方差，再取迹形成共享方差；不使用 Cai 特定矩阵结构下的简化更新。高斯乘积、配方、相除及消息传递用句按本文对象适配。
- **MMSE denoising / Gaussian pseudo-likelihood / channel prior / high-dimensional integrals**：Cai 第3580–3581页 III-B1，原式(20)–(23)及相邻段落。本文条件于活动状态，使用 q_tr；t_k 在单个设备的 D 个复信道系数上平均。高维积分句为计算对象的客观说明。
- **Bernoulli distribution / posterior probability of activity**：Cai 第3581页 III-B2，原式(28)–(30)给出相应分布与贝叶斯活动更新的表述。本文式(19)–(21)对 q_tr 边缘化得到活动似然，不把该非高斯边缘化等同于 Cai 的高斯信道外信息计算；p_k 为 pstar 的实际近似。
- **Bernoulli–Gaussian pdf / Gaussian projection / projected Gaussian belief**：Cai 第3581页 III-B3，原式(32)–(42)；回传关系见第3582页。本文式(23)合并混合方差及平均操作，对所有设备与全部信道系数平均；投影后的高斯密度用于随后的外信息相除。

作者随后要求删除无推导增量的说明。采用稿保留均值、方差、投影、消息相除及变量传递关系，精简导航、重复参数、重复高斯性质及重复 MMSE/活动概率解释。外信息正值的独立说明句已删除；第五章已有的 b 截断范围及算法步骤保持。此决定更新此前将该独立说明句列为必须保留的文字要求。编号公式、近似号和算法规则均未改动。


## 2026-11-08：信道外信息推导移入第三章

作者确认采用 Cai 的章节分工：消息关系集中于第三章，第四章给出学习计算，第五章接入训练模型并汇总实际算法。Cai 正式版第3581页（本地PDF第7页）III-B1式(22)–(27)先定义去噪矩、再求信道外信息，III-B3式(32)–(34)先组合信道消息、再形成 Bernoulli–Gaussian 分布；第五章第3583页（PDF第9页）式(55)–(56)及相邻段落接入训练好的网络。本次仅借鉴上述组织与已有术语，活动概率仍按本稿 q_tr 边缘化，不转用 Cai 的高斯活动似然。

- **Gaussian belief / Gaussian site / extrinsic message**：将原第五章式(38)–(39)移至III-B1末，现为式(19)–(20)；原式(40)–(41)移至III-B3开头，现为式(24)–(25)。四条代数关系逐字保持，Vehtari 的 site 引文随段落前移。相除与组合的文献位置同上，site术语依据仍为Vehtari §2.1、§5.3。
- **channel mean / shared average variance**：III-B1用 F_k 表示当轮去噪均值，tau^post 表示共享去噪方差。式(17)的左端由H_k^post改为F_k；式(18)改为(1/(KD))sum_k tr Cov(vec(H_k)|R_k,alpha_k=1)的近似，明确对全部K个设备、D个复信道系数平均。此为原第五章设备平均操作的前置定义，与Cai式(23)的共享方差组织对应；不更改先平均、后施加下界的算法次序。
- **conditional channel moments**：H_k^post与t_k由式(24)–(25)的site组合给出，再用于式(26)–(29)的联合估计与反馈。第四章保留每设备tau^star的导数关系，并补其设备平均与共享方差目标的衔接。第五章用F_k=F_theta(R_k,v)实例化一般去噪均值；分类器仍输入F_k。没有提前在第三章介绍网络或具体模块名称。
- **receiver integration**：第五章A采用Cai第五章“训练模型接入框架—实际算法”的推进，保留网络输出、共享方差、相位与初始化及算法汇总，删除已经迁移的推导和重复反馈说明。site执行分支继续只放算法表。

图3现分别引用式(19)–(20)与(24)–(25)，不将二者合成包含中间活动推导的连续区间。其余引用同步为(37)、(41)、(26)–(27)、(28)–(29)；图中去噪器的第二参数同步为正文采用的标量v，绘图源同步更新。图的示例数据、连线和其他标记保持。

## 2026-11-08：第四章原文适配重写草稿（待采用）

作者要求重新按原始论文组织第四章。此次生成独立审阅草稿，正式第四章和两版正式 PDF 尚未替换。逐段原文锚点、必要适配及公式核验见[第四章来源记录](../checks/ch3_5_proposal_20261108/ch4_source_sources.json)。

- **Bridging Score Function and MMSE Denoising / First-Order Score Matching**：采用 Cai 正式版 IV-A、IV-B 的原标题及推进顺序，PDF 第8–9页、印刷第3582–3583页，式(43)–(49)。复实堆叠、v/2、采样噪声方差、现有训练权重及 denoiser 参数化按本稿替换。固定 v 的 score-MSE 目标由原正文文字展开为不编号公式。
- **conditional covariance / Jacobian / divergence / Monte Carlo method**：Manor–Michaeli §3.2式(11)、PDF第4–5页及 §4.1式(15)、第6页；Dytso 作者稿式(3)和 §IV Proposition 1式(22)；Metzler 作者稿 §V-B、PDF第15页。本文按复坐标平均取迹，保留既有随机符号方向与中央差分，这些是本稿适配。
- **class-conditional densities / Bayes-optimal logit / density ratio**：Menon–Ong §3式(6)、PDF第2页给出类别几率与密度比；§2.1–2.2给出 Bayes-optimal scorer 和 logistic loss 的 logit link；§4开头及 §4.2式(16)–(17)、PDF第3页给出均衡训练和对应比值估计。草稿的 Bayes-optimal logit 是以上对象在本文交叉熵表达下的称呼，随后以 trained classifier / estimate 区分实际网络；两类样本构造、共同 v 分布、F_theta 特征与实际活动先验修正均为本稿适配。


### 同日：第四章草稿仅调整顺序

作者确认按前章的均值、方差、活动概率三个未知量编排，并明确要求保留已有内容。本轮将上轮 A/B 合并为 Channel Mean Estimation，将协方差整段和公式移至 Channel Variance Estimation 开头，Activity Probability Estimation 保持。上述 Cai 原标题仅作为上一轮草稿记录，当前候选使用三小节标题。所有正文块、公式及引用逐字保留；公式编号随顺序恢复为 DSM(32)、去噪损失(33)、协方差(34)。预览仍为13页，本轮未写入正式正文及两版正式PDF。核验见[仅顺序调整记录](../checks/ch3_5_proposal_20261108/ch4_reorder_checks.json)。

作者随后确认 A 标题为 Channel Mean Estimation via Denoising Score Matching，C 标题为 Activity Probability Estimation Based on Density Ratios；B 保留 Channel Variance Estimation。DSM 术语依据沿用 Cai IV-B／Vincent，density ratios 沿用 Menon–Ong §3／§4.2。此次仅扩展候选 A、C 标题，未改正文。

第四章候选 A 标题最终确认为 Channel Mean Estimation with a Score-Based Generative Prior。score-based generative priors 沿用 Cai 第四章章题及 IV-A/B，PDF 第8–9页、印刷第3582–3583页；单数形式对应本稿学习的信道先验。B、C 标题及正文保持。


## 2026-11-08：第五章原文适配重写候选（待采用）

作者要求第五章沿用第三、四章的原文适配标准。当前候选保留 Overall Algorithm、Parameter Estimation and Numerical Implementation、Computational Complexity Analysis 三小节；逐段原文锚点和本稿适配见[第五章来源记录](../checks/ch3_5_proposal_20261108/ch5_source_sources.json)。

- **hybrid structure / integration / forward pass**：Cai V-A、印刷3583／PDF9，以及 V-C、3585／PDF11。接入对象为本稿去噪器、导数方差和活动分类器；MFLE为解析线性估计，GPJD使用学习模型。网络调用次数及操作成本采用本稿现有计算。
- **sample covariance / eigenvalues / minimum description length**：Nadakuditi–Edelman II–II-A，印刷2626–2627／PDF2–3，对 Wax–Kailath 的样本特征值MDL规则作明确介绍。保留本稿噪声估计式、低秩/空间白噪声条件及固定噪声估计的时序。
- **Gaussian prior / marginal likelihood**：Tipping–Faul §2.1，PDF2，式(2)–(8)。本文复矩阵观测、相位响应、独立增益方差及负对数目标按现有模型适配。L-BFGS-B沿用Zhu等摘要与§1的有界优化方法；坐标更新组合及Doppler到有效导频的关系为本稿已有定义。
- **recursive damping / variance update**：Cai V-B1、3583–3584／PDF9–10提供两向阻尼句式；Rangan VAMP III-C式(26)–(27)、作者PDF6支持前轮阻尼状态的递归插值。Vila–Schniter III-A式(22)–(27)、4661／PDF4提供固定近似后验下的高斯方差求导。候选补明令导数为零的引式步骤，方差目标、κ索引和更新时序保持。
- **complexity analysis**：Cai V-C、3585／PDF11的网络前向计算说明与Shen III-C末尾、PDF10的逐模块计数组织。全部复杂度阶数、内存、SVD关系、AFDM/OTFS调制条件均沿用本稿既有内容。Shen此处正确位置是III-C末尾。


### 同日：第五章候选语态适配

作者确认将第五章重复的作者动作句改为以研究对象作主语的表述。Cai V-B2（印刷3584／PDF10）交替采用作者主动句和 scaled input is given by 等表达；Shen III-C末尾（PDF9–10）以作者提出算法、计算复杂度受具体操作决定等不同主语组织文字。本轮据此作语法适配，未增加专业术语或方法名称；各方法的原文出处仍以上述逐段来源记录为准。公式、条件、操作次序与论断强度保持。


### 同日：第四五章确认稿正式采用

作者已确认将上述第四五章原文适配候选及第五章语态调整写入正式正文。此前“候选／待采用”记载为历史阶段，当前以paper/sections中的采用稿为准。逐段来源与方法术语保持；新的第一至五章通读建议记录在ch1_5_review_after_adoption.json，尚未追加修改。


## 2026-11-08：跨帧有效信道的句子表述

作者确认以直接说明矩阵关系的普通句法替代 shared effective-channel representation 这一概括。引言现用 “the received pilot frames to be expressed in terms of the same effective channel matrix for each device”；结论相应说明各帧观测依赖每个设备的同一个有效信道矩阵。the same 是句中的限定语，不登记为新的技术名称。引言与OTFS的比较直接指明 the effective channel matrix in our model。

技术依据为本稿第二章的跨帧关系 H_k^(q)=exp(jq beta_k)H_k、相位并入 A_k 以及 Y=sum_k A_k X_k+W；这几句是本文公式的直接说明。Shen §II-B、式(10)后、PDF pp.4–5 使用 effective channel、remains approximately constant over Q consecutive frames、quasi-static property，并说明多帧增加观测；原文为 https://arxiv.org/html/2412.20806v1#S2.SS2 。这些原词和关系提供表达依据，不将改后句称为Shen的逐字原句。

本轮未找到 shared effective-channel representation 的可靠完整文献用例；此前将其登记为本文描述不构成文献术语依据。现行三处写法以上述作者确认结果为准，保留早期记录以便追溯。数学含义、比较条件、引用和编号保持。


### 同日：多帧贡献的精简表述

按作者最新确认，引言以跨帧有效信道的Doppler-induced phase rotations直接引出增加导频帧的观测收益；结论以multi-frame AFDM transmission scheme、input-output relationship及观测收益概括第一项贡献。两处不再重复说明各帧观测对应的矩阵关系。该关系仍由第二章式(8)–(10)定义，技术含义及上述Shen §II-B的来源记录保持；本轮未引入新术语。现行措辞以正式正文为准。


## 2026-11-08：第六章 Cai／Shen 参考分析候选

本轮没有新增方法名称或缩写。以下记录分析组织与既有术语的出处，具体比较仍使用本稿实验数据。逐段映射见 [第六章来源记录](../checks/ch6_reference_revision_20261108/SOURCES.json)。

- **channel denoising / genie-aided MMSE / forward pass**：Cai VI-B，PDF第11–12页、印刷第3585–3586页，先独立比较去噪，再进入完整接收机评估；本稿保留自身genie条件及高SNR排序，仅说明均值网络的一次前向计算。
- **convergence / NMSE / activity error rate**：Cai VI-C的Fig.5–7讨论，PDF第12–13页、印刷第3586–3587页；Shen V的Fig.5、7和9讨论，PDF第12–14页。本稿按实际曲线分别说明NMSE与AER，约40轮后曲线基本稳定不等同于满足接收机停止规则。
- **number of devices / pilot length**：Cai VI-C的Fig.8与Fig.10讨论，PDF第13–14页、印刷第3587–3588页，以共同误差目标比较可支持设备数和导频开销。本稿对象分别为candidate devices和pilot frames，报告满足目标的已测点；Shen V的Fig.6讨论，PDF第13页，提供多帧观测的分析组织。
- **activity probability / phase estimation**：Shen V的Fig.7–9讨论，PDF第14页，及Cai VI-C的Fig.9讨论，PDF第13页、印刷第3587页。本稿负载分析限定固定资源下待恢复活动信道增加；相位比较采用本稿known-phase与estimated-phase设置。
- **channel mismatch / without retraining**：Cai VI-C的Fig.11讨论，PDF第13–14页、印刷第3587–3588页。训练与测试profile分别使用本稿NTN-TDL设置，保留profile A/B在6 dB时STMP更优的观测。

当前为独立审阅候选。来源全文沿用本地cai.txt与shen.txt及此前登记的原始PDF，未将参考论文的数值、算法差异或机制解释直接转移为本文结论。


### 同日：第六章以 Shen 为主的分析组织

按作者最新要求，当前候选以 Shen 第V节的整体趋势、主要比较、结果意义为主要组织依据：Fig.5–6讨论位于作者稿PDF第13页，Fig.7–9位于第14页。Cai 第VI-B与VI-C仅补充独立去噪及跨信道部分的参考。密度比消融是本文独有的实验，Shen只提供段落组织参照；相位设置仍使用本文定义。本文关于无需单独训练方差模型的说明来自现有第四、五章，不借整机结果宣称方差估计更准或推理更快。

本轮未引入新方法名、缩写或技术术语。具体段落及来源定位见[Shen为主的第六章来源记录](../checks/ch6_shen_revision_20261108/SOURCES.json)。

作者随后明确要求将该第六章候选直接写入正式正文，现已逐字采用。上述来源与术语依据保持，正式稿及两版PDF同步完成，见同目录ADOPTION.json。


## 2026-11-09：第三、五章语言修订中的消息指代

作者确认四处语言修改，并要求核查消息的方向性称谓。第三章现按上下文使用 this message、prior message 和 Gaussian message from the linear estimator，分别指前一句已定义的高斯消息、线性估计使用的先验消息和线性估计器传向联合去噪器的消息。消息来源和相除对象保持原有公式含义。

- **Gaussian message / Gaussian belief / likelihood**：Cai 正式版 III-A，印刷第3579页／PDF第5页，式(6)及相邻段落明确节点间消息、似然与belief的乘积关系。本稿式(12)前用 this message 回指已写出的 CN(x_j; x_j^pri, gamma I)，并保留Ma2017原引文。
- **prior message / message from the linear estimator**：Cai III-A，印刷第3580页／PDF第6页，式(10)–(11)后说明线性模块外信息传向去噪模块；III-B3末，印刷第3582页／PDF第8页，说明返回消息作为下一轮线性模块的prior message。本稿沿用对应方向和作用，未新增方法名称。
- **MMSE denoising / GPJD与MFLE分工 / 训练尺度归一化**：沿用[第三章来源记录](../checks/ch3_5_proposal_20261108/ch3_minimal_sources.json)与[第五章来源记录](../checks/ch3_5_proposal_20261108/ch5_source_sources.json)。GPJD使用训练去噪器和分类器；全局训练条目RMS的除法及噪声方差除以s²保持。


## 2026-11-09：按具体统计量统一均值与方差表述

作者要求全文尽量使用明确的均值、方差或协方差名称。现行主稿及评估协议附录的可见文字逐项检索后，第三章计算说明采用 channel mean and shared average variance，第四章章首采用 channel mean and variance；定义与公式保持。本条沿用并再次确认2026-11-03完整搭配核查中的具体统计量原则，后续改稿优先按对象命名。

Cai正式版III-B1、印刷第3580–3581页／PDF第6–7页使用posterior mean and variance描述计算对象；同章Gaussian projection段的matched first- and second-order moments描述匹配性质，不能据此将所有均值／方差说明改成笼统的channel moments。Shen当前本地全文未检出moment(s)，IV-A／PDF第11页使用posterior means and variances。已有相应出处见本文件2026-11-03条目；本轮全文核对结果为主稿与完整稿的可见文字均无moment或moments。内部公式标签保持以维持引用稳定。

第二章以without increasing the number of unknown channel coefficients说明观测数量增加而未知系数数量不变。underdetermined限定于式(10)的linear system，Q<KN的维数关系保持；这一条件来自本稿A的Q×KN维数，不推断使用先验后无法估计。


## 2026-11-09：对象明确的措辞与新版导频结果

本轮按作者确认采用五组语言修改，并在作者明确授权后采用新版导频实验。未新增算法名、缩写或专业术语。

- unknown phases 是对本文第五章“已知或估计一次的相位”这一参数状态的直接描述；message-passing updates 沿用第三章、第五章的现有消息更新关系，Gaussian message / extrinsic message 的来源仍为 Cai (2026) §III 与本文件此前登记。附录完整句是本文配置说明，不宣称为 Cai 原句。
- denoiser、NMSE、activity update 沿用本文第四章、VI-B、VI-C及既有术语记录。独立去噪比较与整机比较的对象区分可参见 Cai (2026) §VI-B；本轮具体排序由本文图4决定。活动更新的比较由表III决定，不由密度比这个数值本身执行操作。
- expected number of active devices 直接描述第二章设备活动概率模型的统计含义，并沿用第六章设备数分析中的原有表达，不把概率增加写成每个场景都确定增加活跃设备。
- severe degradation / sensitive to limited pilot observations 是本文导频曲线的普通结果描述，不是新机制或算法名称。数值依据为 result/pilot_frames/latest_20261109/SUMMARY.json，GitHub固定提交50dd757cdca668f5ddf357d8033434b957d1577d；依据位置为STMP的Q=8、12行及GP_MP对应行。−12 dB目标下16/20帧与20%节省限定于已测试帧数，见同目录ADOPTION.json。既有正文全部编号公式和文献来源保持。


## 2026-11-09：Monte Carlo统计设置与图注组织

- **Monte Carlo trials**：Cai (2026), *Joint Activity Detection and Channel Estimation for Massive Connectivity: Where Message Passing Meets Score-Based Generative Priors*, VI-A3 “Evaluation Settings”，正式版PDF第11页／印刷第3585页。原文集中说明NMSE与检测错误概率每点分别平均500与5,000次Monte Carlo trials。本稿沿用该统计术语；每点1,000次为作者确定的评估协议，不能归为Cai原有参数。[本地核对文本](../../reference/reviews/section_structure_20261009/cai.txt)第2038–2044行。
- **图注组织参考**：Shen (2025)本地版本第V节，PDF第13–14页图5–9，图注主要交代收敛／SNR／导频数／设备活动概率等比较对象和固定参数。全文未检出Monte Carlo或trials，故不以其支持统一1,000次的说法。[本地核对文本](../../reference/reviews/section_structure_20261009/shen.txt)第1495、1519、1539及1601–1602行。此项是组织参考，不新增专业术语或实验结论。
