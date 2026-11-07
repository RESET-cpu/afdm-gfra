# 当前术语与来源

**2026-11-05 最新展示名称（作者要求）：** 论文方法统一使用已有作者标签 **GP-MP**，估计相位版本为 **GP-MP-EP**；STMP 基线保持。GP/MP 沿用 generative-prior/message passing，未新增文献术语。名称不再编码训练噪声颜色；数据、权重与历史标识按原记录溯源。此次先统一图例及正文名称，实验完成后另行替换数据。

**2026-11-04 最新名称简化（作者确认）：** **CGP-MP** 替代 GP-MP-C，C 表示 colored Gaussian noise training，GP/MP 对应 generative-prior/message passing。此名称是本文作者指定标签，未声称为已有文献的算法名；只是调整字母位置并减少一个连字符，原术语出处和方法含义沿用下文记录。估计相位版为 **CGP-MP-EP**；**GP-MP** 保留给当前结构的白噪声训练消融；**STMP** 为含学习密度比活动更新的三网络适配基线。历史名称按日期理解。见[同步记录](../../C-STMP/checks/algorithm_name_cgp_mp_20261104/README.md)。

**2026-11-04 共用名称同步：** C-STMP 稿件中，旧三网络 GP-MP 对照改称 STMP （AFDM 适配并使用学习密度比活动估计），GP-MP 留给当前方法的同结构白噪声训练消融，GP-MP-C 仍为有色方法。内部算法 ID、该稿历史结果和冻结资产不变。出处与定义见 [C-STMP 术语最新记录](../../C-STMP/docs/TERMINOLOGY.md)。

### 2026-10-25 有色噪声独立去噪实验

独立 AWGN 去噪沿用 Cai [v2 §VI-B、Fig.4](https://arxiv.org/html/2506.00581v2#S6.SS2)；相关噪声去噪的来源见 [D-GEC §III-B、§IV-A](https://arxiv.org/html/2206.05049v2#S3.SS2)。本项目采用的 Kronecker 协方差、固定平均功率、alpha 扫描和接收机列相关形状对照为明确的项目设置，见[实验协议](../../C-STMP/docs/COLORED_DENOISING_EXPERIMENT_20261025.md)。alpha 是协方差因子的混合权重，不将其称为所有坐标对的相关系数；合成已知 C 与接收机估计 C 分开报告。

### 2026-10-24 C-STMP与DU的项目名称及接口

| 名称或术语 | 原文定位 | 本项目使用边界 |
|---|---|---|
| deep unfolding / 深度展开；DU（用户指定展示名） | Hershey、Le Roux、Weninger，[arXiv:1409.2574v4](https://arxiv.org/pdf/1409.2574)，PDF p.1摘要与§1；§2式(3)–(4)，PDF pp.4–5 | DU指项目已有十层展开模型；只改展示和登记名称，`proposed`作为历史别名保留，不把项目架构归为原文实证 |
| C-STMP（colored，用户指定项目候选名） | 母体STMP：Cai等，[v2](https://arxiv.org/html/2506.00581v2)，§III–V；有色Gaussian参数化来源见[前次核查](../../../reference/reviews/colored_architecture_review_20261024/preconditioning.md) | C-STMP不是原文既有方法名；本次网络有色训练，但推断C=vI、标量反馈、旧分类器，不能称完整D-GEC或完整有色消息接口 |
| Jacobian of the conditional mean、conditional covariance / 条件均值Jacobian、条件协方差 | Dytso–Poor–Shamai，[v1](https://arxiv.org/pdf/2104.01883)，§IV Proposition 1式(22)、Corollary 1式(23)，PDF pp.5–6 | 本项目输出为行的Jacobian满足P=JΣ；复标量方差tr(P)/4096。随机符号中央差分及复维归一化为[本项目推导](../../C-STMP/docs/C_STMP_DERIVATION_20261024.md)，有限网络导数迹不自动等于条件MSE |


### 2026-10-23 四基线的GFRA术语和判决来源

SOMP（simultaneous orthogonal matching pursuit）沿用 Tropp Algorithm 3.1；GFRA 应用另据 [Zhou v2](https://arxiv.org/pdf/2201.02084v2) §IV-C、PDF p.10 式(27)、脚注3及Algorithm 1。归一化能量门限0.1是该文经验设置；不能称为统计最优门限。CG-AD（channel gain-based activity detector）与BI-AD（belief indicator-based activity detector）沿用 [Ke v4](https://arxiv.org/pdf/1906.09867v4) §III-B、PDF p.7 式(39)–(41)，二者分别使用幅度和稀疏后验指标，并聚合跨观测判决；不能把任意路径概率改称用户活动后验。

MP-BSBL（message passing-based block sparse Bayesian learning）的GFRA原始来源为 Zhang 等 TVT 2018；此次原始全文未取得，具体用户块精度及噪声更新核对 [Zhaoji Zhang等2019原文](https://arxiv.org/pdf/1910.02953v1) §II-B/C、PDF pp.4–5及p.10 Table IV。GGAMP-SBL（Gaussian GAMP-based SBL）依据 [Al-Shoukairi等2018](https://phil-schniter.web.app/pdf/tsp18_sbl.pdf) §III、Table I、PDF pp.4–5；其内层GAMP/外层EM不能与当前单循环无阻尼实现混同。

GNN-ASPL依据 [Ding六页稿](../../../reference/literature/ding2026.pdf) pp.3–5；p.4式(27)能量读出与路径稀疏概率须区分，p.5§IV-A每SNR单独训练不能改述为混合SNR共享权重。Off-grid SBL沿用 [Wei v1](https://arxiv.org/pdf/2101.05629v1) §III–IV、Algorithm 1及§VI-A；原文提供OTFS信道估计，不提供本项目GFRA用户读出。“AFDM/MMV适配”“跨SNR固定门限候选”仅描述项目操作，不是新增论文算法名称。来源、证据等级和当前差异见[专项报告](BASELINE_GFRA_AUDIT_20261023.md)。

**2026-10-23 稿件标签更新：** 原 DCN 改为 [TWC-1](../../STMP/README.md)，原 TWC 改为 [TWC-2](../README.md)。这是作者指定的稿件编号，不是算法名称；下文历史记录保留当时标签与文字路径，导航链接更新到新目录。文献中的期刊缩写 TWC 保持原义。

2026-10-12：协方差条件重训及完整二阶矩相关条目作为[已归档研究](../../../archive/paper_layout_20261026/original_paper/docs/history/archive/covariance_training_20261012/README.md)的来源记录保留；当前采用原三模块路线，状态与后续方向见 [CURRENT_STAGE.md](CURRENT_STAGE.md)。

本页记录当前系统模型和七个算法入口使用的术语。来源定位沿用已核对的论文记录；
完整日期记录、诊断公式和历史方法见[整理前术语台账](../../../archive/paper_layout_20261026/original_paper/docs/history/archive/workspace_organization_20261011/before/docs/TERMINOLOGY.md)。
项目参数、软件函数名和公式编号按操作直接描述。

| 原词或忠实译名 | 原文定位 | 当前使用 |
|---|---|---|
| affine frequency division multiplexing、discrete affine Fourier transform、chirp-periodic prefix / AFDM、离散仿射傅里叶变换、啁啾周期前缀 | [Bemani 等作者稿](https://arxiv.org/html/2204.12798v2)，§II-B 式(11)–(16)、§III-A 式(18)–(19) | 波形、DAFT 与前缀定义；具体展开见 SYSTEM_MODEL |
| fractional delay、fractional Doppler、effective channel matrix / 分数时延、分数 Doppler、有效信道矩阵 | [Huang](../../../reference/huang2026_prior_agnostic_afdm_diffusion.pdf)，§II 式(4)–(5)，p.2950 | 连续物理路径；本项目的符号换算按 SYSTEM_MODEL 说明 |
| likelihood-annealed Langevin dynamics、posterior sampling / 似然退火 Langevin 动力学、后验采样 | [Huang 2026](../../../reference/huang2026_prior_agnostic_afdm_diffusion.pdf)，摘要 p.2949，§III-B 式(8)–(10) p.2951，Algorithm 1、Fig.3 p.2952 | 文献对照：在单用户 SISO 的完整 AFDM 信道矩阵上，以观测残差、学习的先验 score 和随机扰动进行多噪声层级的迭代。当前主线是线性模块与局部 score 去噪器的消息传递；原文 Fig.4 的性能结论不自动成为当前 JADCE 的保证。 |
| annealed Langevin dynamics / 退火 Langevin 动力学 | [Arvinte–Tamir 作者稿 v2](https://arxiv.org/html/2204.07122v2)，§II-B 式(4)–(5)、§III-B 式(15)–(17)、Algorithm 1；[作者测试代码](https://github.com/utcsilab/score-based-channels/blob/main/src/score_based_channels/test_score.py) L129–157，2026-10-12 核对 | [已知活动集合诊断](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_known_activity_score_20261012/ALGORITHM.md)使用同一冻结 first 网络和原始观测残差。复数方差、梯度、随机扰动统一按该文件推导；两种退火、步长、温度与固定末步读出为本实验设置。有限噪声下的似然是近似，有限网络和迭代不保证精确后验采样；不称为 Huang 实验复现。 |
| likelihood score、prior score / 似然 score、先验 score | Huang 2026 §III-B 式(9)–(10)，p.2951，Algorithm 1 p.2952 | 对照时从 log p(Y\|H)=−‖Y−HX‖²/σ_z²+常数直接求导：Wirtinger 导数 ∂log p/∂H*= (Y−HX)Xᴴ/σ_z²；对应实坐标梯度整体多因子2。原文式(10)和 Algorithm 1 印刷为 +(HX−Y)Xᴴ，与其梯度上升更新的符号不一致；已视觉核对并用合成有限差分检查正确方向。此处只记录复现所需的符号核查，不据此判定原实验代码采用了该印刷符号。 |
| array response vector、common spatial direction / 阵列响应向量、共同空间方向 | [Li–Gao–Xia](https://arxiv.org/html/2207.11958v2#S2.SS3)，§II-C 式(8) | 每用户共享方向的物理模型 |
| variational line spectral estimation (VALSE)；posterior probability density functions / 变分线谱估计、后验概率密度 | [Badiu–Hansen–Fleury](https://arxiv.org/pdf/1604.03744)，§II–III 式(6)–(12)，PDF pp.3–4 | 20261013未知方向调研：借鉴对连续方向分布取期望，不能把原Bernoulli–Gaussian幅度更新直接称为当前小网络算法；项目适配与限制见[调研](../../../reference/direction_score_inference_20261013/REPORT.md) |
| multisnapshot VALSE (MVALSE) / 多快拍VALSE | [Zhu等](https://arxiv.org/pdf/1803.06497)，§III 式(14b)、(16)、(19)–(20)，PDF pp.6–7 | 阵列响应的后验期望不同于在单一方向估计处取值；多快拍方向更新含其他分量和交叉协方差。当前G各元素有结构，不能原样采用独立Gaussian幅度模型 |
| multidimensional VALSE (MDVALSE) / 多维VALSE | [Zhang等](https://arxiv.org/pdf/1912.11759)，§III-A 式(14)–(16)，PDF p.5 | 二维方向分布近似的参考；项目物理方向余弦圆盘域和神经先验需另行适配，尚未实施 |
| likelihood ratio trick / 似然比技巧 | [Rizvi–Pettee–Nachman](https://arxiv.org/html/2305.10500v1#S2)，§II 式(6)–(12) | 平衡BCE的理想分类器odds对应密度比；有限证据网络需校准。方向积分的比值恒等式及全协方差展开为[项目直接推导](../../../reference/direction_score_inference_20261013/REPORT.md)，非该论文现成算法 |
| local tilted expectation–maximization；damping / 局部倾斜分布期望最大化、阻尼 | [Na–Wadayama 2026预印本](https://arxiv.org/html/2607.14597v1)，§II-B 式(4)–(5)、Algorithm 1；§II-D | 借鉴模块内参数与矩更新的一致性；其Gaussian cavity、精确score及可辨识性假设并未在本项目成立，不能移植近oracle性能或固定点最优性结论 |
| turbo message passing、Gaussian projection、extrinsic message / turbo 消息传递、Gaussian 投影、外信息消息 | [Cai](https://arxiv.org/html/2506.00581v2#S3)，§III-A–B 式(6)–(42) | 两模块更新、受限协方差与 Gaussian 消息相除；THEORY T3–T5、T13–T17 |
| Generalized Expectation Consistency (GEC)、block uniform diagonalization / 广义期望一致性、分块均匀对角化 | [Fletcher等](https://arxiv.org/pdf/1602.07795v2)，§II-A 式(8)–(9)、§II-B Algorithm 1，PDF pp.2–3 | 20261012均值反馈研究的候选：每用户为一块、块内保留一个标量。复数MMV线性查询及外信息公式是[项目推导](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_mean_feedback_20261012/ANALYSIS.md)。已实现并完成[六条件验证](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_mean_feedback_20261012/user_scalar_pilot/REPORT.md)：完整候选未减少漏检，尚未采用；有限网络的均值/条件MSE不自动满足原文精确估计函数及收敛假设 |
| Tweedie's formula、denoising score matching、second-order score matching / Tweedie 公式、去噪得分匹配、二阶得分匹配 | [Cai](https://arxiv.org/html/2506.00581v2#S4)，§IV-A–C 式(43)–(54) | 一阶均值与二阶全坐标平均迹；有限一阶均值下的条件 MSE 关系见 THEORY T8–T11 |

2026-10-16的[AWGN损失加权对照](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_awgn_weighting_20261016/PROTOCOL.md)
沿用上述DSM/second-order score matching的术语。将原单样本损失分别乘v/E[v]和v²/E[v²]，
是根据Cai式(48)–(49)、(53)–(54)直接变换损失权重；
不将该项目选择另称为已有算法，也不声称正权重能保证有限网络读出改善。

后续[均值尺度与辅助读出对照](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_awgn_mean_scale_20261016/REPORT.md)
仍在 Cai §IV-A–C 式(43)–(54)的 AWGN 实坐标/复噪声方差约定下操作。
以训练数据最小化 E||cF−H||² 得到 c=E Re〈F,H〉/E||F||²，是本文明确展开的输出修正，
不是文献中另一个已命名算法，也不能将 cF 自动称为原物理先验的精确 Tweedie 均值。
有限均值风险 R_f=tr Cov(H|x)/D+||E[H|x]−f||²/D 来自条件平方误差直接展开；
原分类器仍可使用原 F0(x,v) 特征，另一均值输出的改变不强制改变该分类器的输入定义。
对应“活动证据/密度比”的来源和训练先验校正沿用下方 Menon–Ong §3–4.2 条目。

| pseudo AWGN observation model | Cai §IV-A 式(43)、§V-B1 | 去噪查询的工作模型；实际有限 AFDM 查询的适用性属于近似 |
| Gaussian approximation、device activity denoiser / Gaussian 近似、设备活动去噪器 | Cai §III-B1–B2 式(26)–(30) | 网络查询超出支持范围时，以保留的 Gaussian site 计算解析活动概率 |
| density ratio estimation、class-probability estimation、logistic loss / 密度比估计、类别概率估计、logistic 损失 | [Menon–Ong](https://proceedings.mlr.press/v48/menon16.pdf)，§3 式(6)–(8)、§4.2 式(16)–(17)，pp.305–306 | 分类器 logit 经训练先验校正，再加入公开活动先验；THEORY T15 |
| damping / 阻尼 | Cai §V-B1 式(57)–(58) | 均值与协方差的算术插值；当前新值权重 0.2 是项目设置，选择依据见 [默认设置记录](../../../result/proposed_default_20261014/DEFAULT_SELECTION.json)；历史图配置保留 0.1 |
| vector approximate message passing (VAMP)、divergence / 向量近似消息传递、散度 | [Rangan–Schniter–Fletcher](https://arxiv.org/pdf/1610.03082)，Algorithm 2 第5–8行，PDF p.4；§III-C，PDF p.6 | 20261012实验候选对完整联合映射 pF 取实坐标平均散度，并成对定义外信息均值和方差。有限差分、固定探针及沿用本项目比例裁剪是实验设置；不是原文的精度裁剪，消息方差不自动等于真实MSE |
| group averaging / 群平均 | [Chen–Dobriban–Lee](https://papers.nips.cc/paper_files/paper/2020/file/f4573fc71c731d5c362f0d7860945b88-Paper.pdf)，§3.1 Lemma 3.2、Proposition 3.3，§4 | 20261012实验检查公共复相位旋转；四相位组合和混合矩按实验协议定义。固定查询上的风险依据不保证闭环性能；条件分布平均与先验密度混合是不同操作。20261015增加对完整接收机输出的群平均候选：相位前端运行一次，四个整体旋转各自独立完成条件推断后合并；公式和期望平方误差的适用条件见 THEORY §12，门限 AER 另作独立验证 |
| equivariance / 等变性 | [Chen–Dobriban–Lee](https://papers.nips.cc/paper_files/paper/2020/file/f4573fc71c731d5c362f0d7860945b88-Paper.pdf)，§1 PDF p.1 对网络等变性的说明，§2 对群作用的定义 | 当前相位不变信道先验和AWGN下，F(gR,v)=gF(R,v)由项目条件均值定义推出。训练中惩罚偏离该关系的候选公式（历史文件已清理，原路径：`experiments/proposed_mean_feedback_20261012/PLAN.md`）已进入[独立训练对照](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_phase_training_20261012/PROTOCOL.md)，效果待验证；它不是引用论文已验证的JADCE算法，部署仍使用一次一阶评估 |
| rank-r matrix approximation、low-rank matrix fitting / 秩r矩阵近似、低秩矩阵拟合 | [Xu等](https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/ell2.12379)，§3 “Low-rank matrix fitting based channel estimation”，式(7) | 20261012保存均值诊断对M×NP天线展开保留一个奇异分量，只用已有F；未采用该文矩阵补全流程。样本秩一不推出后验均值秩一，代数反例、NMSE与固定线性响应见[分析记录](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_mean_feedback_20261012/evidence/mean_structure_analysis.json)，可选秩一均值反馈已接入Receiver；[闭环实验](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_rank_one_20261012/REPORT.md)在用户要求下停止，仅一个开发条件完成三版本配对，不能作总体性能结论。训练时对去噪均值的其余奇异值能量加惩罚属于项目待验证目标，不是该文已验证的score训练方法 |
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
| power posterior、thermodynamic integration、marginal likelihood / 幂后验、热力学积分、边际似然 | [Friel–Pettitt 所读作者早期稿](https://www2.stat.duke.edu/~scs/Courses/Stat376/Papers/NormConstants/FrielPettitPath05.pdf)，§3 式(4)–(5)、§3.1 式(6)；[Friel–Hurn–Wyse v2](https://arxiv.org/html/1209.3198v2#S2)，§2 式(6)–(11) | 20261012活动证据调研：在固定C的proper complex Gaussian查询下，幂β的活跃后验等于(R,C/β)的后验。项目推导ell=∫₀¹[2Re tr(RᴴC⁻¹mβ)−tr(mβᴴC⁻¹mβ)−L tr(C⁻¹Vβ)]dβ；只需列对角协方差块平均，不要求后验Gaussian、各列独立或Vβ<C/β。用现有first/second代入是另行提出的近似，二阶条件误差矩不自动等于Vβ，端点和求积误差必须保留。推导、版本边界及精确合成检查见 [调研来源](../../../reference/activity_evidence_20261012/SOURCES.json) 和 [数学检查](../../../reference/activity_evidence_20261012/MATH_CHECKS.json)；尚未运行该候选的学习网络或接收机比较。 |
| pointwise MMSE、probability density via MMSE / 逐点MMSE、通过MMSE表示概率密度 | [Kong–Brekelmans–Ver Steeg](https://arxiv.org/html/2302.03792v1#S3)，§2 式(4)–(5)、§3 式(7)–(8)、Appendix A.1–A.2 | 去噪误差差值在噪声尺度上的积分恢复逐点log density ratio的原文依据。项目针对q1(R\|C)与q0(R\|C)的复矩阵转换、以及从H的去噪器恢复R的去噪器，记录于上述SOURCES.json；不能把平均I-MMSE关系或有限网络的任意MSE直接称为精确活动证据。 |
| probability flow ODE、instantaneous change of variables、Skilling–Hutchinson trace estimator / 概率流ODE、瞬时变量变换、Skilling–Hutchinson迹估计 | [Song 等](https://arxiv.org/html/2011.13456v2#S4.SS3)，§4.3 式(13)、Appendix D.2 式(38)–(40) | 调研备选：一阶网络转score后，通过ODE及散度积分求其流模型定义的似然。该密度与真实物理分布的偏差、数值积分和随机迹估计误差需区分；当前二阶条件误差矩不是有限一阶网络的精确Jacobian，不能直接替代其散度。尚未实施。 |
| calibrated discriminative classifier、likelihood ratio / 经校准的判别分类器、似然比 | [Cranmer–Pavez–Louppe v2](https://arxiv.org/html/1506.02169v2#S2.SS2)，§2.2 Theorem 1、式(2.4)、(2.10)，§2.3、§3.3 | 当前activity模块的补充依据：理想分类器或其单调变换与密度比相关；有限分类输出需验证校准与检测能力，条件C及训练/部署先验差异不能忽略。原文不保证任意分类器raw logit都是精确证据。 |
| denoising-based VDAMP (D-VDAMP)、colored noise denoising / 去噪型VDAMP、有色噪声去噪 | [Metzler–Wetzstein](https://arxiv.org/pdf/2010.13211v1)，§1末段、Algorithm 1，§2.2–2.3，PDF pp.1–3；VDAMP为variable density AMP | 子带方差消息与对应条件去噪网络协同设计的先例；其 weak state evolution 是经验模型，不移称为本项目的理论保证 |
| denoising generalized expectation-consistent approximation (D-GEC)、corr+corr | [Shastri 等](https://arxiv.org/pdf/2206.05049v2)，§III-B 式(39)–(41)，§IV-A 式(42)，PDF pp.16–18 | 用同协方差独立噪声样本作为去噪网络辅助输入；一般形式与小波子带训练族分开表述。当前用于文献对照，不是项目已采用算法 |
| Fast Iterative REnoising (FIRE)、colored renoising | [Bendel 等](https://arxiv.org/html/2501.17468v4#S3.SS1)，§3.1 式(8)–(19)、Theorem 1 | 通过补加有色噪声使查询误差近似白噪声的替代路线；依赖误差模型，未在本项目实施，也不能消除已有信号方向偏差 |
| MSE estimation / 均方误差估计 | [Ma–Ping OAMP](https://arxiv.org/pdf/1602.06509v3)，§III-I 式(30)–(31)，PDF p.5 | 20261012观测功率初始化控制采用零均值初始估计下的复数MMV能量式，扣除公开噪声后估算输入共同方差；不是在当前物理相关输入上认证点态无偏 |
| simultaneous orthogonal matching pursuit / 同时正交匹配追踪（SOMP） | [Tropp 作者预印本](https://tropp.caltech.edu/papers/TGS05-Algorithms-Simultaneous-I-preprint.pdf)，Algorithm 3.1，pp.6–7，§3.2 | 多测量列共享支撑；64 原子预算和已知噪声残差停止为项目设置 |
| generalized approximate message passing sparse Bayesian learning / GAMP-SBL | [Zhang](../../../reference/zhang2023_gamp_sbl_grant_free_noma.pdf)，pp.15058–15059 式(3)–(19)、Algorithm 1 | 复数模型中跨天线共享行精度和公共噪声精度，明确作为 MMV 适配 |
| Gamma prior、MAP update / Gamma 先验、MAP 更新 | Zhang 式(3)–(4)、(16)、(18)–(19) | 共享行精度和噪声学习；用公开噪声确定 Gamma 超参数是项目数值设置 |
| graph neural network-based adaptive sparsity pattern learning / GNN-ASPL | [Ding](../../../reference/literature/ding2026.pdf)，pp.3–5 式(12)–(28)、§III-B/C | 当前十层展开网络、图内信息传播与逐层训练；具体训练分布见 TRAINING |
| decision threshold / 判决门限 | Ding p.4 式(27) | 系数块能量按用户间最大值归一化；公共 SNR 选取冻结节点的规则是项目设置。20261015 Proposed 可选最终判决使用完整估计能量除以公开噪声方差，并同时要求原概率不低于0.5；该归一化和两条件规则为项目明示公式 THEORY P3，不称为 Ding 的同一算法，也不将能量分数称为概率 |
| EM-GAMP；Gaussian log-likelihood ratio / Gaussian 对数似然比 | [Zhao](../../../reference/zhao2025_mixed_fronthaul_jadce.pdf)，pp.4123–4126 式(20)–(40)、(49)、(51)–(57)、Algorithm 1 | 全分辨率特例，式(38)方差更新及 Gaussian block LLR；AFDM/MMV 适配与待验证状态见 BASELINES |
| on-grid / 网格内；off-grid / 网格外 | [Wei 等作者稿](https://arxiv.org/pdf/2101.05629v1)，§III-B pp.11–12 式(17)–(24)、§VI-B pp.26–27 | 基线使用有限整数网格，评价信道允许连续参数偏离网格 |
| spike-and-slab prior / 尖峰与连续分布混合先验；conditional slab variance / 非零分量条件方差 | Ding pp.3–4，§III-A 的 p(Z\|λ) 及 Σ 对角元 γ 定义 | 20261012逐 SNR 的 on-grid 训练拟合只统计物理占用行，合并同一行的路径碰撞。固定零均值和共享标量是项目设置；当前正式混合训练 checkpoint 已采用该口径 |
| off-grid sparse Bayesian learning / 网格外稀疏贝叶斯学习 | [Wei 等作者稿](https://arxiv.org/pdf/2101.05629v1)，§III-B 式(17)–(24)，§IV 式(35)–(57)、Algorithm 1（PDF p.18），§V Algorithm 2 | 已接入 `offgrid_sbl`。原文向量化“1D”模型包含时延和多普勒偏移；本项目的 AFDM/MMV 方差及偏移更新推导见 OFFGRID_BASELINES。固定公开噪声、每用户相关性筛选、区间约束是明确的项目设置 |
| first-order linear approximation / 一阶线性近似 | [Wei 等作者稿](https://arxiv.org/html/2101.05629v1)，§III-B 式(17)–(24) | SBL 在固定中心计算时延与 Doppler 导数，以偏移修正字典。20261012 审查另外记录精确预测与一阶预测的相对距离；这一诊断量由项目定义，不等同于信道 NMSE |
| virtual sampling grid、virtual sampling resolution / 虚拟采样网格、虚拟采样分辨率 | [Wei 作者稿 v1](https://arxiv.org/pdf/2101.05629v1)，§III-B p.11、式(18)前的定义，§VI pp.23–26、Fig.5–7 | 原稿扫描间距 0.2–0.9，Fig.5/6 分别为两维均 0.5/0.8。审查将 AFDM 固定时延采样点由 112 增至 448；四倍密度由项目校准确定，归一化间距不能跨波形直接照搬。完整配置来源见 OFFGRID_BASELINES 的 20261013 溯源 |
| convergence tolerance / 收敛容差 | [Wei 作者稿 v1](https://arxiv.org/pdf/2101.05629v1)，Algorithm 1 p.18、§VI p.24 | 原稿按方差超参数相对变化不超过 10^−3 停止，Tmax 未给出具体数值。本项目使用 10^−4 并额外检查偏移增量；600 次上限为项目校准预算 |
| hierarchical hyperprior distribution / 分层超先验分布（Wei SBL） | [Wei 作者稿 v1](https://arxiv.org/pdf/2101.05629v1)，§IV-A 式(26)–(29)，§IV-B 式(44)–(45)，Algorithm 1 | 20261013 独立对齐实验令物理系数方差先验 rho=0.01。列归一化 x_i=s_i h_i 后，方差乘 s_i²、Gamma 率参数除 s_i²；MMV 方差及噪声更新是项目推导，见 docs/history/experiments/offgrid_sbl_reference_20261013/PROTOCOL.md。原稿相关幅值初始化推广为跨天线相关幅值的均方根，明确不是原文已有 MMV 公式 |
| multi-snapshot Newtonized orthogonal matching pursuit (MNOMP) / 多快拍 Newton 化正交匹配追踪 | [Zhu 等作者稿](https://arxiv.org/pdf/1802.01266)，§II 式(1)，§III 式(6)、Algorithm 1（PDF p.7），§IV-A | 实现见 [MNOMP 归档](../../../archive/paper_layout_20261026/original_paper/docs/history/archive/mnomp_20261014/README.md)。原文为一维频率 MMV；AFDM 二维参数和范数可变的目标导数为项目适配 |
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
[SYSTEM_MODEL.md](SYSTEM_MODEL.md) 中直接定义；场景重抽样与结果复用范围见
[EXPERIMENT_PROTOCOL.md](EXPERIMENT_PROTOCOL.md)。这些条件按本项目公式和协议记录。

当前算法与源码位置见 [CODE_GUIDE.md](CODE_GUIDE.md)，其中 `proposed`、`somp`、`gamp`、`gnn`、`em`、`offgrid_sbl`、`ldamp`
是命令行标识。`run_spatial_score`、`SpatialConfig` 和 checkpoint 中的 `full_score` 为保留的软件字段。

2026-10-13 小网络训练审查补充，详见[逐环节报告](../../../archive/paper_layout_20261026/original_paper/docs/history/results/small_training_audit_20261013/REPORT.md)。

| 原词或忠实译名 | 原文定位 | 本轮使用范围 |
|---|---|---|
| RefineNet；multi-resolution fusion；cascaded residual pooling / RefineNet、多分辨率融合、级联残差池化 | Huang 2026，§III-A、Fig.1，p.2951；原文引用Lin等CVPR 2017 RefineNet | 原文指定的网络家族。当前16×16 `GlobalFirstScore`是残差卷积加全局线性混合，不能称同一RefineNet；本项目完整信道RefineNet的宽度及参数量也不能当作Huang披露的配置 |
| denoising score matching / 去噪得分匹配 | Huang 2026，§III-A 式(7)及其后实虚双通道说明，p.2951 | 原文复噪声方差、−N/σ²目标与实梯度措辞需区分约定。本项目按每实分量v/2训练缩放实score，均值为r+(v/2)s；核对通过但不宣称与未知作者代码逐项一致 |


2026-10-13 一阶网络训练与结构调研补充。以下仅为[候选研究](../../../reference/first_score_improvements_20261012/REPORT.md)的来源，不表示已经修改默认训练或获得性能收益。

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

2026-10-13 小网络数据物理审查补充，详见[审查报告](../../../archive/paper_layout_20261026/original_paper/docs/history/results/small_data_physics_audit_20261013/REPORT.md)。

| 原词或忠实译名 | 原文定位 | 本轮使用范围 |
|---|---|---|
| piecewise-continuous AFDM (PC-AFDM)；frequency wrapping；phase correction / 分段连续AFDM、频率折叠、相位修正 | [Cao–Shao 2026预印本](https://arxiv.org/html/2609.07480v1)，§II-A 式(1)–(3)、Proposition 1 | 用于描述并核对当前分数时延基函数的跳变性质；项目独立数值检查确认边界两侧存在非零矩阵差异。未采用其替代波形，未证明这种性质导致当前网络性能差距，也不把作者的命名追溯成Huang原文术语 |

2026-10-13 GNSS-Free、AFDM、off-grid场景来源补充，详见[设定审查](../../../archive/paper_layout_20261026/original_paper/docs/history/results/scenario_assumptions_audit_20261013/REPORT.md)。

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
| regularized zero-forcing (RZF) processing / 正则化迫零处理 | [Li等v2](https://arxiv.org/html/2207.11958v2#S4.SS3)，§IV-C Proposition 3式(38)–(41)，PDF p.9 | 空间权重依赖同导频用户方向与功率，正则项由共同PDP和噪声联合确定、通常不等于噪声方差。原文为导频子载波数趋于无穷的MSE设计；不能直接套给已作线性外信息更新的查询。原文与本项目推导分开记录于[详细核查](../../../reference/spatial_combining_audit_20261013/REPORT.md) |

2026-10-13 GNSS-independent 场景与方向先验的适用条件，详见[可行性核查](../../../reference/gnss_direction_feasibility_20261013/REPORT.md)。

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

2026-10-13 天线维度与 score 网络结构调研，详见[综合报告](../../../reference/antenna_score_architecture_20261013/REPORT.md)：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| angular/beamspace domain；unitary Fourier transformation / 角域或波束域、酉傅里叶变换 | [Fesl等，WCL 2024作者稿v1](https://arxiv.org/html/2403.03545v1)，§III-A，Algorithms 1–2，PDF pp.2–3；§III-C/Fig.1，p.3 | 原文变换Rx×Tx两阵列轴；本项目空间变换沿UPA的y、z两轴。完整酉变换保留白噪声方差，不保证性能提升；论文轻量模型整体比较不是FFT单因素消融 |
| beam-delay domain；three-dimensional convolution / 波束—时延域、三维卷积 | [Artemasov等，ITU Journal 2024](https://www.itu.int/dms_pub/itu-s/opb/jnl/S-JNL-VOL5.ISSUE1-2024-A05-PDF-E.pdf)，§2.2式(8)–(9)，pp.63–64；§4.1式(23)–(24)，p.66 | 原文沿平面阵列两beam轴与delay卷积。我们的UPA两轴加AFDM矩阵两轴共四个物理轴，不能把普通Conv3d直接称为完全同构；交替处理两组二维轴是本项目待验证设计 |
| fully convolutional deep learning receiver / 全卷积深度学习接收机 | [Honkala等，DeepRx，TWC 2021](https://arxiv.org/html/2005.01494#S3)，§III/Fig.2、Table II | 原文天线信息放入特征通道、卷积沿时频，说明这种组织不是必然失效；其两Rx、LLR输出和数据辅助输入不能作为本项目score去噪的公平架构对照 |
| circular convolution / 圆周卷积 | [Fesl等，SPAWC 2021](https://arxiv.org/html/2104.12667)，§III–IV式(14)–(19) | 原文从块循环和移位假设得到DFT域二维圆周卷积；引用作结构设计依据，不声称其ULA统计假设已在本项目UPA/AFDM成立 |

上述阵列轴处理于2026-10-13曾进入[完整网络配对实验](CURRENT_STAGE.md)：保留原RefineNet，并增加交替处理UPA和AFDM两组轴的分支，采用同参数量的AFDM轴对照。该组合及其零输出初始化为本项目实现选择，不冠以新方法名称，也不宣称复现Artemasov或Fesl的原网络。角域变换不在此首轮对照中同时引入。


2026-10-13 完整角域原生实现与功率处理补充：

沿用上述 Fesl §III-A/C 的角域表示、Artemasov §4.1 的平面阵列组织及 Cai §IV 的 denoising score matching（去噪分数匹配）。四物理轴上交替两组二维卷积为项目设计，不命名为文献已有网络。该方案已按用户要求删除，历史说明见[精简记录](CURRENT_STAGE.md)。

Cai §V-B2 式(59)–(65)的 channel power normalization（信道功率归一化）在本项目评估中须区分真值范数与查询能量估计：式(59)右侧对白噪声取条件期望后等于左侧，有限随机查询上不是严格恒等式。功率估计方差、负值概率及缩放不确定性说明是项目推导，见[功率评估](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/full_power_channels_20261013/PLAN.md)。样本总功率不自动等同于慢变大尺度衰落，不能把解析缩放称为独立学习网络。


2026-10-13 用户授权执行逐样本功率归一化训练：沿用 Cai §V-B2 的 channel power normalization（信道功率归一化）定义，U=H/sqrt(mean(|H|²))。训练噪声相对于U独立采样；推断中的解析查询功率估计、固定正下限和模型支持限制明确记录于[执行方案](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/full_power_channels_20261013/PLAN.md)。扩大噪声范围、0.5dB继续训练门槛及其统计检查均为本项目选择，不归为Cai原文规定。


2026-10-13 数据张量阶数与卷积轴的核对：Fesl WCL 2024作者稿§II-A式(1)、§III-C/Fig.1以接收×发射二维复信道为输入，实虚作为两通道，采用2D卷积。Artemasov 2024 §4.1式(23)–(24)、Fig.3、p.66明确写四阶复张量 Nu×NR×NC×Nτ，其中Nu为UE天线数；卷积核为3×3×3，沿两beam轴与delay处理。不能将Nu误称批次/实虚维，也不能把“四阶输入”当成四轴卷积的证据。本项目4×4×16×16两beam轴加AFDM输入/输出索引，并交替两组2D卷积，是独立设计扩展，两文未直接验证该组合。

2026-10-13 二维角域展平的[专项核查](../../../reference/afdm_network_axes_20261013/REPORT.md)：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| beamspace channel vector / 波束域信道向量；Gaussian mixture LAMP (GM-LAMP) | [Wei–Hu–Dai，TCOM 2021正式全文](https://oa.ee.tsinghua.edu.cn/dailinglong/publications/paper/Deep%20learning%20for%20beamspace%20channel%20estimation%20in%20millimeter-wave%20massive%20MIMO%20systems.pdf)，§II-A式(3)、(6)–(8)，pp.183–184；§III，pp.186–188；§IV Fig.5、7，pp.190–191 | UPA二维导向基与完整N×1角域向量可以并存，后续采用学习线性映射和逐元素收缩；不是普通Conv1D，也未比较本项目4×4 beam卷积与通道组织方式 |
| convolutional input channels / 卷积输入通道 | [DeepRx作者稿](https://arxiv.org/html/2005.01494#S3)，§III、Fig.2、Table I | 天线及实虚部可放通道，通过通道混合联合使用；仅有逐通道卷积不等于全通道混合。本文是OFDM两Rx接收机，不能把其BER结果当成本项目score性能依据 |
| conditional mean estimation；conditional covariance / 条件均值估计、条件协方差 | [Dytso–Poor–Shamai，TIT 2023](https://doi.org/10.1109/TIT.2022.3216012)，式(3)、§III Proposition 1式(17) | 用实坐标Gaussian恒等式核对score/Jacobian变换；展平的置换只重排二阶对角，真正酉混合只保证全trace不变，不能从角域对角恢复天线域全部逐坐标方差 |

“将16个复波束作为32个实输入通道”“二维FFT后展平”“交替两组二维卷积”均为操作描述，不设立新方法名称。本轮128个样本的reshape恒等式与MAC检查属于项目验证，不归为参考论文结果。

2026-10-13 波束通道网络落实：沿用Fesl §III-A的angular/beamspace domain与DeepRx §III的convolutional input channels。`ChannelScoreNetwork`为项目类名，不是论文方法名。[当前方案](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/full_power_channels_20261013/PLAN.md)采用全部32实通道混合及AFDM平面残差卷积。输入/输出稠密线性层吸收固定DFT的关系是项目线性代数推导，已用非零输出网络验证；它说明函数类等价，不声称Adam训练轨迹等价。数据中的`C_ml=mean(U_m conj(U_l))`明确称空间二阶矩，未中心化，不把非对角能量减少解释为独立性或物理自由度减少。5000训练样本的数值来自[本地诊断](../../../archive/paper_layout_20261026/original_paper/docs/history/results/full_power_channels_20261013/REPRESENTATION.json)，并非论文实验结果。

2026-10-14 强噪声 score 改进[定向调研](../../../reference/low_snr_score_20261014/REPORT.md)：EDM、Min-SNR、条件均值及后验矩沿用上表已核对条目，补充以下原词。

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Single-Step SNR-informed Denoiser / 单步 SNR 条件去噪器 | [Strasser–Bäro–Utschick，2025作者稿v1](https://arxiv.org/html/2509.07839v1)，§IV-B、式(10)–(12)、Algorithm 3；§V-F/G；arXiv元数据注明在WSA 2025报告 | 完整酉导频、单载波MIMO的单步去噪先例；文中单步性能不逊于或优于多步的实验不能直接成为AFDM JADCE结论。说明单步本身不是强噪声失败的充分解释 |
| effective noise；colored Gaussian noise；D-VDAMP / 有效噪声；有色Gaussian噪声；去噪型VDAMP | [Metzler–Wetzstein，2020作者稿](https://arxiv.org/html/2010.13211)，§1–2、Algorithm 1 | 为结构化测量下实际查询与AWGN的差异提供方法依据；MRI中的Fourier/wavelet条件不能直接套给AFDM。项目观测到的输入列误差二阶矩含偏差，不能直接称为纯噪声协方差，也未实现D-VDAMP |

2026-10-14 参数化对照执行：EDM 沿用 Karras 等 NeurIPS 2022 §5 式(7)–(8) 的 preconditioning，见上述已有条目。项目仅使用 c_in、c_skip、c_out，保留旧 DSM 权重；实坐标 nu=v/2，tau²取训练先验的实坐标二阶矩。固定 v 专门训练是实验条件描述，不冠以新方法名称。计划见 [配对训练](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/low_snr_parameterization_20261014/PLAN.md)。

2026-10-14 用户功率一致性核查：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Uplink power control / 上行功率控制 | 3GPP TR 38.821 V16.0.0 §6.2.2，印刷页62（PDF索引61），https://atisorg.s3.amazonaws.com/archive/3gpp-documents/Rel16/ATIS.3GPP.38.821.V1600.pdf | 该研究报告讨论NTN上行功控，并认为可使用Rel-15方案；不证明所有终端严格等接收功率，更不证明无GNSS场景能精确补偿 |
| downlink pathloss estimate / 下行路径损耗估计 | ETSI TS 138 213 V16.11.0，§7.1.1，pp.17–21，p.21给出referenceSignalPower减filtered RSRP；§7.4，pp.32–33给出PRACH功率控制，https://www.etsi.org/deliver/etsi_ts/138200_138299/138213/16.11.00_60/ts_138213v161100p.pdf | 参考信号测量是慢变功率补偿的信息来源，不要求读取真实瞬时信道范数；无GNSS与无下行测量是不同约束。本项目目前只有LARGE_SCALE_COMPENSATED=True假设，没有实现标准功控过程 |

“等发射功率”“补偿后平均功率一致”“逐实现信道范数相等”用于区分不同数学条件，不作新算法名称。当前生成器使用相同导频能量、共同TDL路径期望功率，并保留独立小尺度衰落，省略用户相关的大尺度幅度因子；配置中的大尺度补偿假设不等于实现了逐用户功率补偿。对小尺度衰落取期望的信道能量一致，与固定场景接收能量一致是不同条件，推导及口径见 references/power_control_scope_20261014/NOTE.md。几何损耗量级检查见 references/power_control_scope_20261014/GEOMETRY_CHECK.json，仅计算距离引起的自由空间损耗差，不含天线方向图、遮挡和功控误差。

2026-10-14 卫星 GFRA 场景对照：六篇 GFRA 与一篇相邻 AFDM CE 的来源、仿真条件及差异见 [文献与代码综合核查](../../../reference/satellite_gfra_audit_20261014/SYNTHESIS.md)。

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
配置、公开输入和验证范围见 [PROPOSED_UNKNOWN_PHASE.md](../../STMP/docs/PROPOSED_UNKNOWN_PHASE.md)。

2026-10-15 Shen 相位学习适配核查：

| 原词或忠实译名 | 原文定位 | 本项目使用范围 |
|---|---|---|
| expectation-maximization (EM)；phase rotation / 期望最大化；相位旋转 | [Shen v1](https://arxiv.org/html/2412.20806v1#S3.SS3)，§III-C，式(47)–(52)，PDF p.9；Algorithm 1，p.10；正式发表 DOI 10.1109/TWC.2025.3525738 | 借鉴后验均值、方差驱动相位更新并重建测量矩阵的思路。现有 Proposed 使用学习近似后验，不自动继承精确 EM 的单调性结论。 |
| projected onto the unit circle / 投影到单位圆 | 同文式(53)–(54)及相邻说明，PDF p.9 | 原文先解无约束线性方程再逐元素归一化，属于近似更新。本文保留 exp(jq beta_k) 跨帧关系的目标和梯度另行推导；未把它命名为 Shen 原算法，未宣称投影是一般单位模问题的精确解。 |

对应推导、方差项适用条件和合成数值检查见 [Proposed 未知相位说明](../../STMP/docs/PROPOSED_UNKNOWN_PHASE.md#shen-2025-相位学习的适配核查2026-10-15)。后续已实现保留 exp(jq beta_k) 约束的相位更新，入口为 `configs/proposed_iterative_phase.json`，同十场景 NMSE/AER 比较见 [实现验证](../../../archive/paper_layout_20261026/original_paper/docs/history/results/shen_phase_update_20261015/evaluation/REPORT.md)。这是借鉴原文目标的 AFDM 适配，并非 Shen OTFS 算法复现；当前六方法比较仍采用原两阶段相位配置。

2026-10-15 GAMP-SBL / off-grid SBL 后验相位更新：继续采用上述 Shen §III-C 式(47)–(54)的“phase rotation”和“expectation-maximization”含义作为参考。项目实际操作称为“后验相位更新”，完整目标、Gaussian 协方差项及 exp(jq beta_k) 约束见 [BASELINE_PHASE.md](BASELINE_PHASE.md)。GAMP 的对角方差项在单位模约束下为常数；SBL 的跨用户协方差项保留。这里的逐用户一维搜索、圆周插值和一次更新预算是项目明确写出的操作，并非新算法名称或 Shen 原文的闭式解。不得由固定后验目标下降推出整体精确 EM 收敛。

2026-10-14 连续信道与Huang设定专项核对：

| 原词或忠实译名 | 原文定位 | 当前使用 |
|---|---|---|
| continuous-time waveform、frequency wrapping、complex-envelope discontinuity / 连续时间波形、频率折叠、复包络不连续 | [Bemani博士论文](https://www.eurecom.eu/publication/7447/download/comsys-publi-7447.pdf)，§3.1.1式(3.2)–(3.10)、§3.2式(3.14)，印刷pp23–29；[Cao–Shao预印本](https://arxiv.org/html/2609.07480v1)，§II-A式(1)–(3)、Proposition1 | 用于核对当前分数时延及多周期CPP的模拟解释；整数样点等价不能推出带限DAC输出等价。项目相位导数与跳变诊断见[信道专项](../../../archive/paper_layout_20261026/original_paper/docs/history/results/implementation_audit_20261014/CHANNEL_MODEL_REVIEW.md)，未采用预印本的新波形替换当前生成器。 |

2026-10-14 线性查询误差处理核查：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| de-correlated linear estimator、divergence-free estimator / 去相关线性估计器、无散度估计器 | [Ma–Ping，Orthogonal AMP v3](https://arxiv.org/html/1602.06509v3#S3)，§III-A Definition 1后式(14)、§III-B Definition 2及式(17)–(18)、§III-E | 当前线性更新已满足迹归一化，但这一事实不推出有限AFDM查询是独立AWGN；需配套非线性估计条件，并核查误差分布。详见[本轮报告](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_speed_20261014/WHITENING_ASSESSMENT.md) |
| right-rotationally invariant random matrix、non-separable denoiser / 右旋转不变随机矩阵、非可分去噪器 | [Fletcher–Pandit–Rangan–Sarkar–Schniter，JSTAT 2019正式作者全文](https://phil-schniter.web.app/pdf/jstat19.pdf)，§3–4、Theorem 1；前身发表于NeurIPS 2018 | 高维VAMP分析的假设；不能仅凭基础DFT导频行正交，就认为重复块AFDM测量算子符合该随机矩阵模型 |

“按误差二阶矩补加Gaussian扰动”是上述报告中的直接协方差加法构造，不是既有算法名称。真实空间误差只用于明确标注的oracle诊断；不能把样本二阶矩等于标量阵写成已获得与信道独立的Gaussian噪声。

2026-10-14 空间协方差接收机候选：covariance shrinkage（协方差收缩）采用 [Chen–Wiesel–Eldar–Hero，作者稿](https://arxiv.org/pdf/0907.4698) §II式(3)–(4)、PDF p.4的标量单位阵混合形式。本项目先从接收二阶矩中减去公开热噪声，再投影正半定并固定混合10%；不是原文OAS/RBLW，也不主张其最优性。逐用户矩阵Gaussian更新、块平均及额外扰动按[实现公式](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_spatial_feedback_20261014/ALGORITHM.md)直接描述，不另造方法名。

2026-10-14 L-DAMP 原稿与作者训练代码复核，详见[对照报告](../../../archive/paper_layout_20261026/original_paper/docs/history/results/ldamp_paper_audit_20261014/REPORT.md)：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| denoiser-by-denoiser training / 分别训练各去噪器 | [Metzler 等作者稿 v4](../../../reference/ldamp_review_20261014/metzler2017_learned_damp.pdf)，§3，PDF p.5；§4.2，p.7 | 按噪声区间训练 AWGN 去噪器，再在推断时选择网络，是原文训练选项。最优性论述依赖该文条件；不自动适用于本项目多用户、重复观测算子和相关误差 |
| state evolution / 状态演化 | 同上，§4.1，Finding 1，PDF pp.6–7 | 该文列出独立随机矩阵、Gaussian 测量噪声及 Lipschitz 去噪器等条件。本项目矩阵重排为 I⊗A，不能仅由 AMP 形式相同宣称满足这些条件 |
| covariance matrix / 协方差矩阵 | [Chen–Sohrabi–Yu，ICASSP 2018](https://www.comm.utoronto.ca/~weiyu/2018_ICASSP_massive_connectivity.pdf)，§3.1，PDF p.2，式(2)–(4)及式(6)前的简化条件 | 该文保留多测量向量误差协方差，并在特定先验下简化为标量。本项目诊断是对中心化误差计算经验协方差及其非对角能量占比；后者为明示公式的统计量，不设立新方法名，不据此声称已推导出当前 CNN 的矩阵校正 |
| residual learning / 残差学习 | [Zhang 等 DnCNN 作者稿 v1](../../../reference/ldamp_review_20261014/zhang2017_dncnn.pdf)，§III-B，式(1)，PDF p.3；§IV-A，PDF p.6 | D(q)=q−F(q) 下清洁输出 MSE 与噪声预测 MSE 代数等价。He 信道版的 Adam、噪声分段和初始化另按其代码记录，不混同 DnCNN 原文的 SGD 配方 |

2026-10-14 各轮一致的接收机规则调研，详见[综合报告与候选公式](../../../reference/uniform_receiver_literature_20261014/REPORT.md)：

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
| effective noise / 有效噪声；equivalent noise / 等效噪声 | [Metzler 等作者稿](../../../reference/ldamp_review_20261014/metzler2017_learned_damp.pdf)，§2.1，PDF p.4，式(3)后 νᵗ 的定义；[He 等作者稿](../../../reference/ldamp_review_20261014/he2018_ldamp.pdf)，§III-A，PDF p.2，式(6) | 指去噪输入减去真实目标的误差，包含残余干扰；不等于观测中的物理接收噪声 W。不同波束有效误差方差的训练适配不改变 W∼CN(0,σ²I)。独立 Gaussian 训练扰动仅是对有效误差的近似。 |

2026-10-14 L-DAMP 完整实现开发补充：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Wirtinger derivatives；Jacobian matrices / Wirtinger 导数；Jacobian 矩阵 | [Kunde–Mirri–Chamberland–Paolini，2026预印本 v1](../../../reference/ldamp_review_20261014/kunde2026_complex_amp.pdf)，§III-C，PDF p.12，式(18)–(21) | 为复数非可分去噪的矩阵校正提供参考；项目用显式输入/输出下标定义部分迹并通过独立坐标差分核验，不沿用可能含歧义的转置简写。原文独立圆对称复 Gaussian 测量矩阵条件不覆盖当前 AFDM 导频；未声称理论收敛保证。 |

“双边逆 DAFT、按循环滞后重排、沿时间做 DFT”及“逐波束共享两通道 DnCNN”是代码操作描述。DAFT 定义沿用 Huang §II、PDF p.2 式(1)前与式(4)后；固定角域 DFT 沿用上述 Fesl §III-A、Wei–Hu–Dai §II-A。所有系数保留，不把变换系数命名为真实连续路径参数。MatConvNet 保存的 BN moments 为均值和含 epsilon 的标准差，按[官方接口定义](https://www.vlfeat.org/matconvnet/mfiles/vl_nnbnorm/)载入；训练库重估运行统计是明示适配，不能说成原作者训练轨迹复现。见[开发报告](../../../result/ldamp_implementation_20261014/REFERENCE_REPORT.md)。

2026-10-14 各轮一致推断规则的配对实现与试验：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| damped denoising VAMP (DD-VAMP)；damping / 带阻尼的去噪型 VAMP；阻尼 | [Sarkar–Ahmad–Schniter，ICASSP 2021 作者稿 v1](https://arxiv.org/abs/2010.11321)，§3.1、Algorithm 1 第10、15–16行，PDF p.3；[本地原文](../../../reference/uniform_receiver_literature_20261014/phase2_vamp/ddvamp.txt) | 灵敏度在平方根域阻尼，精度在逆平方根域阻尼。本项目取固定权重、完整联合映射 pF 的复探针差分、沿用原主线的灵敏度截断范围；这是 AFDM 接收机适配，不能宣称复现论文 MRI 性能或满足其随机矩阵条件。权重为新值权重，越大意味着阻尼越弱。 |
| plug-and-play ADMM (PnP-ADMM) / 即插即用 ADMM | 同上，§2.1 式(3a)–(3c)、§2.2，PDF p.2 | 保留高斯数据项更新及对偶递推，以旧联合去噪器代替近端映射。本项目将固定查询方差与线性正则化参数对应，并只试两个由公开热噪声和导频能量决定的参数；不声称已穷尽 PnP 参数或存在凸目标、收敛保证。 |

实现和选择记录见 [配对试验协议](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_uniform_inference_20261014/PROTOCOL.md) 与 [冻结的新场景设置](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_uniform_inference_20261014/SELECTION.json)。FIRE 的二阶网络方差替代、固定计算预算和活动读出均为项目实验选择；算法名称之后明确写出这些改动，不作为文献原算法的完整复现。

2026-10-14 旧网络计算与局部导数的优化判断，见[诊断报告](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_optimization_20261014/REPORT.md)：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Jacobian of the conditional expectation；conditional variance / 条件期望的Jacobian；条件方差 | [Dytso–Poor–Shamai作者稿](https://arxiv.org/pdf/2104.01883)，§IV Proposition 1式(22)、Corollary 1式(23)，PDF pp.5–6 | 在实噪声协方差为(v/2)I时，精确后验均值满足J=2C/v。项目比较的是3个探针、3个步长下的归一化迹估计；平均为正不等于完整Jacobian正半定。pF的两项导数按乘积公式直接分解，不设立新算法名称。 |
| second-order score matching / 二阶得分匹配 | [Cai v2](https://arxiv.org/html/2506.00581v2#S4.SS3)，§IV-C式(51)–(54) | 有限冻结一阶网络下，当前迹损失的最优读出对应以该均值为中心的条件误差风险。风险与真实协方差及实际Jacobian的区别按项目THEORY.md附录A代数解释，不将其等同。复用一阶特征输出标量风险是尚未训练的项目建议。 |
| gradient step denoiser；proximal gradient step denoiser / 梯度步去噪器；近端梯度步去噪器 | [Hurault–Leclaire–Papadakis，ICML 2022](https://proceedings.mlr.press/v162/hurault22a/hurault22a.pdf)，§3式(4)–(5)、Proposition 3.1，PDF p.3 | 标量势函数梯度给出对称Jacobian，命题的收缩条件进一步保证正定。这里只作为改变训练结构的文献先例，未实现该架构，也不将其PnP收敛结论移用于AFDM消息传递。随机方向负响应惩罚属于明示公式的项目建议，不能称为上述理论保证。 |

2026-10-14 旧网络的近似 AWGN 查询与一般去噪器反馈调研，见[详细分析](../../../reference/awgn_linear_design_20261014/REPORT.md)和[来源定位](../../../reference/awgn_linear_design_20261014/SOURCE_NOTES.md)：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| denoising-based OAMP (D-OAMP)；divergence-free denoiser / 基于去噪的 OAMP；无散度去噪器 | [Xue–Ma–Yuan，2016 作者稿 v1](https://arxiv.org/html/1610.05991v1)，Algorithm 2，PDF p.2；§3.3.1 式(7)–(8)，p.3 | 一般联合去噪器的散度扣除有来源；本项目复数 MMV 适配、旧网络活动读出和独立误差功率估计尚未完成接收机验证。经验散度和增益的数据依赖意味着有限维无散度性质只是近似，不保证当前 AFDM 误差为 AWGN。 |
| Stein’s unbiased risk estimate (SURE) / Stein 无偏风险估计 | 同上 §3.3.2 式(10)–(11)，PDF p.3 | 基于风险的增益选择；按本项目复数功率 v 和 2d 维实坐标重新推导归一化，式(14)中的功率为 ‖D−R‖²/d+2vα−v。无偏性需要正确 Gaussian 查询及相应正则条件，数据驱动调参还存在有限样本误差，不能用它自证输入已是 AWGN。 |
| state evolution；covariance matrix / 状态演化；协方差矩阵 | [Liu–Yu Part I 作者稿 v2](https://arxiv.org/html/1706.06438v2)，§III-B 式(14)–(17)，PDF pp.4–5；§III-D Theorem 1，p.6；[Kunde 等2026预印本](https://arxiv.org/html/2604.21115v1)，§III-C 式(18)–(21)、Remark 14，PDF p.12 | MMV 可以具有矩阵状态；重复 A 不自动排除 MMV 理论，但基础矩阵、信号各向同性和去噪器条件必须核对。本项目 256 个共同观测特征不能未经推导就简化成单个误差方差。 |
| algebraic estimator；polynomial estimator of divergence / 散度的代数估计器；多项式估计器 | [Skuratovs–Davies，TIT 2023 机构接收稿](https://www.pure.ed.ac.uk/ws/portalfiles/portal/361481237/Divergence_Estimation_in_MP_algorithms_reviewed_second_time_Final.pdf)，含封面 PDF p.4 Assumptions 1–3，p.6 Theorem 2 式(37)，p.8 Theorem 3，p.9 §III-E | 可减少额外网络调用的后续候选；其正交性、大系统和历史条件尚未在本项目成立，未替换当前导数估计，也不将经验选根规则改称严格保证。 |

本轮用户方形导频块的逆矩阵噪声倍率、每用户酉导频的自身响应与干扰协方差、负散度下的一般风险关系均为报告中明示的项目代数推导，不另造算法名称；未变更主线算法或权重。

2026-10-15：上述D-OAMP项目适配现已完成四条件开发试验；三类导频下均在第二轮超出网络支持范围，不能作为已成立的AFDM状态演化。每轮空间协方差、迹归一化及Gaussian扰动补齐按明确公式实施，统计改善但完整性能不通过，详见[顺序实施报告](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_awgn_20261014/REPORT.md)。该组合只描述具体操作，不赋予新的文献算法名称。

后续有色噪声条件训练设计沿用D-GEC §III-B、式(41)，印刷pp.535–536的corr+corr含义：有色噪声观测与同统计独立噪声样本同时输入；有限噪声样本不等于提供精确协方差。固定协方差C下，实坐标后验均值与Jacobian关系沿用Dytso–Poor–Shamai Proposition 1式(22)，并显式规定Jacobian第(i,j)项为∂D_i/∂r_j。矩阵加权条件去噪损失、隐式Gaussian误差生成器是[NEXT_DESIGN.md](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_awgn_20261014/NEXT_DESIGN.md)中的项目推导，尚未实施，不冠以既有方法名称。

2026-10-15 L-DAMP 联合去噪开发：noise level map（噪声水平图）沿用 Zhang–Zuo–Zhang FFDNet §III-A/B/E（https://arxiv.org/html/1710.04026v2#S3.SS2）。这里为每波束公开有效误差方差构造16个常量输入通道，并不复现 FFDNet 的子图下采样结构。network preconditioning 沿用上述 Karras §5 式(7)–(8)、Table 1 的名称；逐波束复数二阶矩到实坐标的尺度推广、32通道 DnCNN 和联合矩阵递推是项目适配，具体公式及受控比较见 `docs/history/results/ldamp_complete_20261015/PLAN.json`。所有候选仍属开发，不代表已安装或已获得独立接收机性能。

同日的后续对照保留上述 DnCNN residual learning 的名称：在冻结逐波束网络的输出上学习联合残差，属于项目自行定义的复合函数，不称作 He 原网络。残差分别按训练二阶矩或公开噪声标准差缩放，损失分母分别在 `PLAN.json` 中明写，未另造方法名称。整个函数参与 Wirtinger 部分迹；分开计算两支路后求和是 Jacobian 线性关系，不能省去“原网络输出作为新网络输入”这条链式导数。实际误差与同算子 Gaussian 对照、训练及数值证据见 `docs/history/results/ldamp_complete_20261015/REVIEW.md`。

2026-10-15 校正项数值检查：沿用 He §III-A 式(7)–(8) 的 Monte Carlo 导数估计及 Kunde §III-C 式(18)–(21) 的矩阵 Jacobian 约定。直接估计 `ZB`、在每用户 `N` 行上使用完整正交方向的安排属于项目推导，未包装为已有论文算法名称；公式、独立数值核验与适用条件见 [PROJECTED_TRACE_DERIVATION](../../../src/history/experiments/ldamp_complete_20261015/PROJECTED_TRACE_DERIVATION.md)。完整 `N` 个方向仅消除此处部分迹的抽样误差，不等于消除网络近似误差或证明 AFDM 状态演化。

2026-10-15 Proposed 协方差条件活动推断与矩阵反馈开发：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Gram–Schmidt orthogonalization (GSO)；orthogonal estimator / Gram–Schmidt 正交化；正交估计器 | [Cheng、Liu、Liang、Manton、Ping，OAMP-MMV 作者稿v1](https://arxiv.org/html/2304.08038v1#S3.SS6)，§III-F Definition 20、式(31)–(34)；§III-G Theorem 21 | 矩阵交叉协方差消除输入输出误差相关。项目仅聚合32维实空间特征，不等于消除全部用户、输入坐标或跨轮相关。§III-D Assumption 18 的 Haar 及 PIID-separable 条件未经本项目验证；§I-D也说明该文状态演化论述偏直观，不能援引为当前固定AFDM算子的严格保证。 |
| generalized SURE / 广义 Stein 无偏风险估计 | [Eldar，作者稿v2](https://arxiv.org/html/0804.3010v2#S5.SS1)，§III-B、§V-A式(39)–(43) | 支持已知协方差Gaussian观测下的风险及导数关系。项目通过完整相关Gaussian探针估计空间交叉矩阵；协方差由观测估计、系数由有限样本选择时无偏及正交性质只是近似。标量反馈增益另沿用已登记D-OAMP式(10)–(11)。 |

具体的实数化、每用户协方差边缘、完整相关探针及矩阵扣除公式见
[实验协议](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_colored_20261015/matrix_feedback/PROTOCOL.md)。
它们是有来源的操作与项目推导的组合，不为组合另设文献算法名；原 Proposed 保持冻结。

2026-10-15 完整协方差参与联合均值变换的开发：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Bernoulli–Gaussian distribution；MMSE denoiser / Bernoulli–Gaussian分布；最小均方误差去噪器 | [Liu–Yu作者稿v2](https://arxiv.org/html/1706.06438v2#S3.SS3)，§III-C式(19)–(22)，附录A Lemma 1式(57)–(61) | 作为已知Gaussian噪声协方差下的解析诊断。这里将用户4096维信道整体视为一个向量；Gaussian活动信道先验仅为对照近似，不宣称NTN信道具有该分布，也不新增主线baseline。 |
| network preconditioning / 网络预条件化 | [Karras等，NeurIPS 2022正式版](https://papers.neurips.cc/paper_files/paper/2022/file/a98846e9d9cc01cfb87eb694d946ce6b-Paper-Conference.pdf)，Table 1，p.3；§5式(7)–(8)，pp.8–9 | 原文以标量噪声方差设置输入、跳连、输出与损失尺度。项目明确推广为P=(βI+C)⁻¹/²、T=β(βI+C)⁻¹、B=[βC(βI+C)⁻¹]¹/²，D=Tr+Bf(Pr,C)。矩阵操作及联合活动先验是项目推导，不是原文的有色噪声定理。 |

本项目通过空间特征分解和逐空间模式的输入特征分解精确施加上述矩阵函数，沿用“特征分解”的通常含义，
不另造算法名称。具体训练范围、实复数尺度及总体损失最优解见
[实验协议](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_colored_20261015/preconditioned_joint/PROTOCOL.md)。

2026-10-15 训练信道二阶矩与受限线性响应核对：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| low-rank approximation；Karhunen–Loève transform；MSE floor / 低秩近似；Karhunen–Loève变换；均方误差下限 | [Edfors等，VTC 1996会议版作者全文](https://lucris.lub.lu.se/ws/portalfiles/portal/6289557/1056818.pdf)，§III-B式(6)–(9)、印刷p.925；§III-C式(10)–(11)、p.926（PDF pp.5–6） | 先验相关矩阵的特征向量及舍弃能量用于量化近似，不把路径数当作固定线性秩。本文献是1996会议版本，不能混写为1998期刊全文。项目用原50000个物理训练样本估计AFDM输出/输入二阶矩；V_kB_k=I的约束解、工作干扰加权和Gaussian协方差补齐另按显式公式推导，没有AFDM实际AWGN保证。 |

对应的统计范围、预定99%/99.9%能量阈值及全部支持失败记录见
[子空间核对协议](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_subspace_20261015/PROTOCOL.md)和
[加权解公式](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_subspace_20261015/WEIGHTED_PROTOCOL.md)。

2026-10-15 完整观测条件下的扩散查询核对：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Denoising Diffusion Restoration Models (DDRM)；Gaussian marginals / 高斯边缘分布 | [Kawar等，作者稿v2](https://arxiv.org/html/2201.11793v2#S3.SS2)，§3.2式(3)–(8)、Proposition 3.1；§3.3 Theorem 3.2；§5.1；[NeurIPS 2022出版记录](https://papers.neurips.cc/paper_files/paper/2022/hash/95504595b6169131b6ed6cd72eb05616-Abstract-Conference.html) | q的边缘对观测噪声积分且使用真实信号，不能据此宣称有限网络pθ的实际查询误差是AWGN。项目使用复数薄SVD、原first和activity的联合均值，以及32个连续噪声方差；这属于显式适配，不是原图像模型复现。反馈均值也没有AWGN保证。 |

适配范围和固定预算见[DDRM隔离协议](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_ddrm_20261015/PROTOCOL.md)。

2026-10-15 原闭环跨轮协方差与逐用户酉因子线性处理：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| damping、error covariance / 阻尼、误差协方差 | [Takeuchi作者稿v2](https://arxiv.org/html/2111.05522v2)，§III-C式(27)–(28)、§III-D式(44)–(45)，§IV-B Example 2式(63)–(78) | 两估计的有限数组MSE混合恒等式单独用于审计；以估计方差标签代入后可能不成立或为负，不冒充LM-OAMP实现，不用真值修改推断。 |
| polar decomposition、unitary polar factor / 极分解、酉极因子 | [Higham 1986作者机构全文](https://eprints.maths.manchester.ac.uk/694/1/high86p.pdf)，Theorem 1.1，§3.1 | 项目令A_k=U_kS_kV_kᴴ、W_k=gV_kU_kᴴ，以共同g归一化整体trace。逐用户热噪声协方差严格为σ²g²I；总误差的自身响应、干扰和历史项不据此成为AWGN。 |
| de-correlated linear estimator / 去相关线性估计器 | [Ma–Ping作者稿v3](https://arxiv.org/html/1602.06509v3)，§III-A式(12)–(14)，§III-I式(31) | 项目沿用迹归一化和工作功率公式，但逐用户极分解的拼接W不一定具有原文整体SVD滤波结构；不能仅凭trace条件继承OAMP的状态演化或误差独立性结论。 |

对应[跨轮诊断协议](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_temporal_20261015/PROTOCOL.md)与
[线性候选协议](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_polar_20261015/PROTOCOL.md)均保留原Proposed三网络和主线文件。

补充定位（2026-10-15）：Ma–Ping同一作者稿§III-D式(21)给出两端误差递推；
§III-E Assumptions 1–2区分线性查询的IID Gaussian要求与非线性反馈的IID及相对A/N独立要求，
后者没有另要求Gaussian；Appendix A说明非线性反馈误差一般可与信号相关。
项目所列完整协方差展开和逐用户白化热噪声的Cauchy–Schwarz下界是显式代数推导，
不是新命名算法或原论文的AFDM定理。推导和适用条件见
[隔离线性实验报告](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_polar_20261015/REPORT.md)。
其中V_kU_kᴴ严格说是A_kᴴ的酉极因子，即A_k的酉极因子的共轭转置；采用该方向是为了从观测映射回信道坐标。

2026-10-16，逐用户发射导频修改的补充定位：Higham同文§2.1式(2.2)、§2.2
Corollary 2.3（印刷pp.1161–1162，PDF pp.3–4）说明方阵的酉极因子是Frobenius
范数下的最近酉矩阵；满秩时唯一。本次对P_k=L_kΣ_kR_kᴴ取发射导频B_k=L_kR_kᴴ，
见配对验证协议（历史文件已清理，原路径：`experiments/proposed_pilot_polar_20261016/PROTOCOL.md`）及
[推导](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_pilot_polar_20261016/DERIVATION.md)。这里改变公开导频及其
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

逐用户功率保持、三维开关及有限差分均为[预定诊断设计](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_axis_control_20261015/PROTOCOL.md)，
不设立新的方法名称。Gaussian误差仍可能有色；该区分也见已登记D-GEC §III-B式(39)–(41)。

2026-10-15 原标量反馈下的每轮残差空间处理：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| singular value shrinkage；optimal shrinker for Frobenius loss / 奇异值收缩；Frobenius损失的最优收缩函数 | [Gavish–Donoho作者稿1405.7511v3](https://arxiv.org/pdf/1405.7511v3)，式(7)、PDF p.5；§2.1，p.8；§4，pp.13–15；[TIT 2017](https://doi.org/10.1109/TIT.2017.2653801) | 本项目对16×256复残差使用同一标量函数，再将所得残差估计的空间二阶矩用于工作协方差。原文实矩阵、大系统、低秩及独立白噪声前提不直接覆盖闭环残差；不称其为当前协方差或接收机的最优估计。 |

残差二阶矩减去已知热噪声后投影正半定、共享空间LMMSE、支持范围内Gaussian补齐及原标量反馈的组合，
按[协议中的公式](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_uniform_spatial_20261015/PROTOCOL.md)直接描述；
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
β/(2−β)方差因子均是显式线性代数推导，分别见[后续协议](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_uniform_spatial_20261015/ORDERED_PROTOCOL.md)
和[噪声参照设计](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_uniform_spatial_20261015/NOISE_REFERENCE_DESIGN.md)。
这些式子不消除未知的真实反馈误差与热噪声交叉项。

2026-10-15 实际当轮反馈映射及相关Gaussian交叉项：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Monte Carlo divergence；divergence-free denoiser / Monte Carlo散度；无散度去噪器 | [D-OAMP作者稿](https://arxiv.org/html/1610.05991v1)，§2.1式(2)–(3)，§3.3式(7)–(11) | 中心差分作用于固定进入本轮之前的site历史后的实际Denoiser映射，包含site接受分支与当前分类器；不是整个迭代历史的总导数。双向阻尼和空间处理仍为项目适配；每轮额外网络调用全部计入成本。 |
| SURE for Correlated Gaussian Noise / 相关Gaussian噪声的SURE | [Raphan–Simoncelli，作者机构全文](https://www.cns.nyu.edu/pub/eero/raphan08-preprint.pdf)，§III-A式(7)–(10)，印刷p.1345（PDF p.4）；§III-B式(11)–(13) | 相关输入的Stein交叉项涉及协方差加权Jacobian迹，不能直接以v乘普通归一化迹替代。复坐标归一化及AFDM工作协方差块为直接推导；不据此宣称实际闭环误差为Gaussian或工作协方差是真实协方差。 |

对应[完整接收机开发协议](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_uniform_spatial_20261015/feedback_receiver/PROTOCOL.md)
与[相关输入交叉项推导](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_uniform_spatial_20261015/feedback_receiver/COLORED_STEIN_NOTE.md)。

2026-10-15后续[固定导数探针对照](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_uniform_spatial_20261015/feedback_probe_control/PROTOCOL.md)
只改变Monte Carlo方向在各轮之间是否重新抽取，不为此设立新算法名称，不声称继承状态演化保证。
[输入维滤波与空间查询的组合推导](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_uniform_spatial_20261015/input_filter/DESIGN.md)
沿用上述奇异值、迹归一化、极分解和协方差术语；逐用户迹/功率约束及空间部分迹均为显式代数推导。
该阶段纯公开算子检查不等同于接收机性能实验。

后续[组合接收机确认](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_uniform_spatial_20261015/input_filter/confirmation/REPORT.md)
已完成八个独立物理场景的48条运行。逐用户滤波与每轮空间处理仍按显式公式描述，未建立新算法名称。
查询的协方差偏离下降、点性能门槛通过不等于独立Gaussian成立；反馈的空间颜色及工作方差偏差仍保留。
物理场景配对bootstrap区间只作小样本描述，不能将预定容差的点估计检查称为已经证明总体非劣。

2026-10-15 历史协方差与原始观测风险：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| orthogonality；asymptotic IID Gaussianity / 正交性；渐近IID Gaussian性质 | [Memory AMP作者稿v7](https://arxiv.org/pdf/2012.10861v7)，§III式(20)、(24)、(30)、(32)，PDF pp.6–8 | 区分状态演化中的Gaussian等效变量、原坐标实际反馈及与全部历史输入误差的正交关系；不能将摘要简称扩大为非线性反馈必然独立于信号。匹配BPSK后验均值反例为项目解析核对，不是AFDM实验。 |
| Stein's unbiased risk estimate (SURE) / Stein无偏风险估计 | [Nobel、Candès、Boyd，TSP 2023作者机构全文](https://web.stanford.edu/~boyd/papers/pdf/sure_tractable_eval.pdf)，§I-A式(1)、§I-B，p.4330 | 对Y↦AF_t(Y)的公式目标是观测均值AH的风险。复坐标因子、历史交叉风险和完整历史依赖按显式公式展开；该文凸优化算法与弱可微结论不能直接套给当前有分支的神经接收机。 |

[本轮报告](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_memory_requirements_20261015/REPORT.md)保留残差协方差偏差的三项恒等式分解，
以及归一化权重下共同噪声扣除项为常数的代数核对，不为此创造新的算法名称。
四条原样重放与离线历史融合不等于完整Memory AMP实现；原始观测的完整映射求导仍属待验证设计。

2026-10-15 原始观测完整响应与补噪表示核对：

[固定轮数协议](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_measurement_response_20261015/PROTOCOL.md)沿用上述SURE术语。
有限差分对固定轮数的完整Y→AF_t映射求导，包含历史依赖；不包含自适应停止时间的导数。
由于分支与有限探针，该核对不等于证明弱可微或无偏风险估计成立。

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| positive semidefinite square root / 半正定平方根 | [Higham，Functions of Matrices，2014作者机构书章](https://eprints.maths.manchester.ac.uk/2109/1/fm2_final_njh.pdf)，§17.5 Fact 2，印刷p.17-7（PDF第8页） | 仅在已保存补噪协方差上离线比较U diag(sqrt(d))与唯一Hermitian半正定平方根U diag(sqrt(d)) U^H。相同协方差对应相同条件Gaussian分布，但固定随机数下路径可不同；该矩阵级检查不构成新接收机性能实验。 |

上述半正定平方根亦已核对期刊原文：[Higham–Schreiber，1990](https://eprints.maths.manchester.ac.uk/340/1/0911038.pdf)，
§1 p.648（唯一Hermitian半正定平方根）、§2 p.651（计算与特征分解形式）。
[完整响应结果](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_measurement_response_20261015/REPORT.md)已完成36条重放，
末轮交叉项解释与早期差分不稳定分别报告；半正定平方根目前仅作离线矩阵对照，尚未进入接收机。

后续进展（2026-10-15）：半正定平方根已进入独立数值映射的响应实验，
原路径复现1/4通过与自身严格复现4/4通过分别保留，原Proposed未替换。
空间矩阵扩展继续采用Raphan–Simoncelli §III-A式(7)–(10)、p.1345的Gaussian积分分部依据；
复数Jacobian的天线块部分迹、平滑反馈及逐样本Q+R分解是项目公式，
不是原论文已有算法名称。证据见[阶段报告](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_measurement_root_20261015/self_response/REPORT.md)。

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| nearest symmetric positive semidefinite matrix；positive approximant / 最近对称半正定矩阵；半正定近似 | [Higham 1988作者全文](https://nhigham.com/wp-content/uploads/2023/10/high88d.pdf)，§2 Theorem 2.1、式(2.1)–(2.2)，pp.105–106；§1 p.104说明可扩展到复矩阵 | 用于后续Hermitian矩阵正部投影的优化依据，不解释为当前统计模型最优。给定估计迹或各向同性约束为项目显式优化推导；本阶段未将这些候选接入推断。 |

上述三种矩阵约束的[全轮离线比较](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_covariance_constraints_20261015/REPORT.md)
已经完成；合法性改善未能稳定恢复方向信息，未接入推断。
[实际查询分解](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_query_terms_20261015/REPORT.md)沿用Ma–Ping §III-D式(21)
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
| likelihood-annealed Langevin dynamics / 似然退火 Langevin 动力学 | [Huang 2026 本地全文](../../../reference/huang2026_prior_agnostic_afdm_diffusion.pdf)，§III-A–B 式(6)–(10)，p.2951；Algorithm 1、§IV，p.2952；[DOI](https://doi.org/10.1109/LWC.2026.3689601) | 直接结合原始观测残差的似然梯度、学习的先验 score 和随机扰动；Algorithm 1 使用 1/(σ_z²+σ_i²) 退火权重，并衰减步长。这不是线性模块误差的白化或协方差估计，不依赖把当前状态解释成真值加独立 AWGN 的局部后验均值接口，但有限噪声层级的似然近似、网络误差和有限迭代仍存在。式(10)及 Algorithm 1 的残差符号问题沿用本页已有核查，不能直接照抄。§IV 的 L-DAMP baseline 引用 He [23]，正文未给出专门处理有色/非 Gaussian 伪观测误差的修正，不能从其曲线推断存在这种修正。 |

本次只核对原文、现有代码与术语边界，未训练网络、运行接收机比较或修改推断算法。

## 冻结 score 与活动分类器的复数矩阵 AMP（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| vector AMP algorithm；state evolution / 向量 AMP 算法；状态演化 | [Liu–Yu，作者稿 v2](https://arxiv.org/html/1706.06438v2#S3.SS2)，§III-B 式(14)–(17)，§III-D | 多测量向量共享感知矩阵时传播特征协方差；不能从矩阵 AMP 推出本项目相关信道的误差协方差自动为标量阵。 |
| Complex Approximate Message Passing with Non-separable Denoising；Wirtinger derivatives / 非可分去噪的复数近似消息传递；Wirtinger 导数 | [Kunde 等，2026 预印本 v1](https://arxiv.org/html/2604.21115v1#S3.SS3)，§III-C 式(18)–(21)、Remark 14，Appendix B；§III-B Assumption 8 | 完整联合去噪映射的复 Jacobian 部分迹与复矩阵校正。引用其 iid proper-complex Gaussian 及函数正则条件；当前有限 AFDM 不宣称满足其状态演化定理。 |
| Onsager correction；Monte Carlo approximation / Onsager 校正；Monte Carlo 近似 | [He 等，作者稿 v2](https://arxiv.org/html/1802.01290v2#S3.SS1)，§III-A 式(4)–(8) | 新循环保留完整活动概率与 score 均值的依赖；四次中心差分和复矩阵部分迹是按明确索引推导的实现，有限步长与有限探针误差均须报告。 |

本项目的具体重排、共同尺度变换、活动概率乘均值的完整链式导数、随机相位 DFT
探针及匹配尺寸 AWGN 参照均在 [完整推导](../../STMP/docs/PROPOSED_AMP.md) 中直接给出公式。
`score_amp` 是软件入口标识，不作为新造的学术算法名称；原 Proposed 保持独立。
运行条件、失败与代价见 [本次结果](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_amp_20261015/REPORT.md)。

## AMP首轮失配与后续稳定性的区分（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| state evolution；covariance matrix / 状态演化；协方差矩阵 | [Liu–Yu作者稿v2](https://arxiv.org/html/1706.06438v2#S3.SS2)，§III-B式(16)–(18)，§III-D Theorem 1式(23) | 一般MMV等效误差保留特征协方差；该文的标量阵简化使用各向同性Rayleigh先验与匹配MMSE等条件。不能将Onsager称为任意天线相关性的白化算子。 |
| Denoising Generalized Expectation-Consistent Approximation (D-GEC)；colored-noise-aware denoiser / 基于去噪的广义期望一致近似；适配有色噪声的去噪器 | [Shastri等2022期刊作者全文](https://phil-schniter.web.app/pdf/jsait22_dgec.pdf)，§III-A Algorithms 2–3、式(31)、(36)–(37)，pp.534–535；§III-B式(38)–(40) | 借鉴分组误差统计与匹配有色噪声的学习接口。MRI的分组模型和corr+corr训练并非本项目已完成方案；式(36)为经验误差模型。16×16天线协方差条件score与活动分类器按显式密度公式提出，不冠以新算法名。 |
| Damped Denoising Vector AMP (DD-VAMP)；denoiser sensitivity / 带阻尼的基于去噪的向量AMP；去噪器灵敏度 | [Sarkar等2021作者稿](https://arxiv.org/pdf/2010.11321v1)，§3.1 Algorithm 1、式(9)–(14)，p.3；§3.2初始化 | 为一致阻尼、Monte Carlo灵敏度波动及初始化消融提供依据，不将其标量正精度的平方根操作直接用于一般复数矩阵，也不宣称阻尼恢复AFDM查询白性或保证当前神经网络迭代收敛。 |

[后续诊断](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_amp_20261015/diagnosis_followup/REPORT.md)保留了40次真值辅助单次网络对照及旧Proposed首轮同样全判活跃、后续恢复的事实。
天线相关性足以复现这组固定输入的网络异常，不等于识别了完整循环失败的唯一原因。
实坐标协方差Tweedie式、白化改变先验的反例及残差天线二阶矩均以显式公式陈述；候选修改尚未训练或接入接收机。

## AMP阻尼与历史偏导（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| functions of all previous iterates；debiasing coefficients / 依赖全部历史迭代量的函数；去偏系数 | [Fan作者稿v5](https://arxiv.org/html/2008.11892v5#S5)，§5式(5.3)–(5.8)、(5.12)，Remark 5.1 | iid Gaussian特例的历史Onsager系数由对应历史输入的偏导平均给出。固定几何阻尼权重及其紧凑递推为本项目显式展开；不把原文旋转不变模型的全部谱校正替换成当前有限AFDM的保证。 |
| Wirtinger derivatives；matrix extension / Wirtinger导数；矩阵扩展 | [Kunde等2026预印本v1](https://arxiv.org/html/2604.21115v1#S3.SS3)，§III-C式(18)–(21)、Remark 14，Appendix B | 固定有限轮数的历史列扩展用于核对非可分复矩阵部分迹的块位置。实际仍用8探针有限差分；条件噪声标签冻结不等于已证明其自适应规则满足状态演化条件。 |
| full-memory AMP / 全历史AMP | [Rossetti–Nazer–Reeves作者稿v2](https://arxiv.org/html/2405.08225v2#A1)，Appendix A，Theorem 5式(59)–(62)，A.2.1式(70)–(72) | 以矩阵列表示固定有限轮数的历史，为本次独立代数核验提供依据。原文此定理使用GOE随机矩阵；不据此声称当前矩形复数AFDM实现满足其统计定理，也不将当前实现命名为OpAMP。 |

阻尼权重、历史校正、含交叉项的方差与确定性固定点谱均在[推导](../../STMP/docs/PROPOSED_AMP_DAMPING.md)按公式直接说明。
`score_amp_damped`为独立软件入口；没有把该递推包装成DD-VAMP或新增学术名称。
原Proposed及无阻尼score_amp保留；新版本的概率输出仍取当前原始分类器，主要信道输出为阻尼状态。


## AMP 查询阻尼与双重历史权重（2026-10-15）

沿用上节的 functions of all previous iterates、debiasing coefficients 和 Wirtinger derivatives，
不新增学术算法名称。依据仍为 [Fan v5](https://arxiv.org/html/2008.11892v5#S5)
§5式(5.3)–(5.8)、(5.12)、Remark 5.1，以及
[Kunde v1](https://arxiv.org/html/2604.21115v1#S3.SS3) §III-C式(18)–(21)、Remark 14、Appendix B。
查询/反馈两侧阻尼的经验动机参照 [Cai v2](https://arxiv.org/html/2506.00581v2#S5.SS2.SSS1)
§V-B1式(57)–(58)，但本实现并未照搬其方差递推。

[本次推导](../../STMP/docs/PROPOSED_AMP_QUERY_DAMPING.md) Q1–Q9显式展开查询权重和输出权重，
校正项用同查询权重混合的残差乘当前完整联合映射的复Jacobian部分迹。
混合残差能量包含跨轮交叉项；其等于实际查询误差功率需要额外统计条件，
有限AFDM下不能由代数恒等式宣称AWGN或收敛。`score_amp_query_damped`仅为软件入口。

## 固定 L-DAMP 中的冻结 score 替换（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| automatic differentiation；forward mode；Jacobian–vector product / 自动微分；前向模式；Jacobian 与向量的乘积 | [Baydin等，JMLR 2018](https://www.jmlr.org/papers/volume18/17-468/17-468.pdf)，§3.1，pp.9–11，式(4)；§3.2，pp.12–13 | 对完整活动概率乘 score 均值的实映射求方向导数；去掉训练特征上的 detach 仅为保留正确链式依赖，不改变原训练代码。方向导数按计算图求出；float32 误差与八探针部分迹采样误差仍存在。 |
| Tweedie's formula；Wirtinger derivatives；Onsager correction / Tweedie公式；Wirtinger导数；Onsager校正 | [Cai v2](https://arxiv.org/html/2506.00581v2#S4)，§IV-A–C，式(43)–(54)；[Kunde v1](https://arxiv.org/html/2604.21115v1#S3.SS3)，§III-C式(18)–(21)、Remark14；[He v2](https://arxiv.org/html/1802.01290v2#S3.SS1)，§III-A式(4)–(8) | 原逐波束 DnCNN 和全部天线 score 使用同一矩阵更新；后者需完整跨波束部分迹。将逐波束方差压成 tr(Σ)/C 是受检验的接口适配，不是已有论文对本AFDM的保证。 |

[推导与接口](../../STMP/docs/LDAMP_SCORE.md)明确坐标、归一化、完整链式导数和失败处理；
[同查询与闭环记录](../../../archive/paper_layout_20261026/original_paper/docs/history/results/ldamp_score_swap_20261015/REPORT.md)区分基线验收、四例开发诊断与候选失败。

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
| denoising score matching；score-based MMSE denoising / 去噪得分匹配；基于score的MMSE去噪 | [STMP v2 本地全文](../../../reference/score_amp_20261015/cai2025_stmp_spawc_v2.pdf)，p.3，§III式(14)、§IV-A式(18)–(19) | 新模型学习活动混合的单波束汇总边缘先验。实方差τ=v/2；以D参数化score时 λ_s=λ_Dτ²。总体最优均值关系不等于有限CNN已达到MMSE。原文Turbo外信息更新未搬入此残差AMP。 |
| network preconditioning / 网络预条件化 | [EDM本地全文](../../../reference/score_amp_20261015/karras2022_edm.pdf)，p.3 Table 1、式(2)–(3)；§5式(7)–(8) | 实坐标输入/跳连/输出尺度和权重沿原文公式；σdata²取当前混合总体实方差，非原图像常数。48通道4残差块、噪声控制通道仿射、log-uniform方差和独立训练均为本项目实现选择。 |
| Onsager correction；Wirtinger derivatives；functions of all previous iterates / Onsager校正；Wirtinger导数；依赖全部历史迭代量的函数 | He §III-A式(4)–(8)、Kunde §III-C式(18)–(21)/Remark14、Fan §5式(5.3)–(5.8)/Remark5.1，来源链接见前文 | 复矩阵1/Q部分迹、配对JVP与逐波束16×16块按显式索引核验；同步状态阻尼用历史校正递推。8探针近似、冻结噪声标签和有限结构化AFDM均保留统计适用性限制。 |

新入口 `diffusion_amp` 仅为软件标识。[完整推导](../../STMP/docs/DIFFUSION_AMP.md)记录具体公式，
[文献审查](../../../reference/score_amp_20261015/AUDIT.md)记录DMP-DUN补充p.1式(1)/(3)及(6)/(9)
的尺度关系差异；这些印刷式的代数问题不能据以断言作者端到端实验代码错误。
八份已下载PDF与ICC 2024全文尚缺的状态见[下载索引](../../../reference/score_amp_20261015/README.md)。

## 完整用户共同活动与矩阵 D-AMP（2026-10-15）

2026-10-15 正式验证前的校正计算修订：矩阵 Onsager 的定义仍采用 Kunde §III-C
式(18)–(21)及 Remark 14。利用当前网络的用户独立性，直接计算 ZB 的取样公式、
完整 N 行基恒等式和无放回样本标准误差是本项目的线性代数与抽样推导，未命名为
新的文献算法。式子与条件见 [JOINT_AMP](../../STMP/docs/JOINT_AMP.md) 式(15c)–(15e)及
[独立数值审计](../../../archive/paper_layout_20261026/original_paper/docs/history/results/joint_amp_20261015/projected_development_v1/DERIVATION.md)。
完整基只消除该固定 Jacobian 部分迹的抽样误差；不消除网络误差、不证明 AFDM
高斯性或状态演化。早期显式矩阵探针实现仍保留为开发对照。

| 原词或忠实译名 | 原文定位 | 本轮实现范围 |
|---|---|---|
| density ratio estimation；class-probability estimation；logistic loss / 密度比估计；类别概率估计；logistic 损失 | [Menon–Ong，2016](https://proceedings.mlr.press/v48/menon16.pdf)，§2.2、§3 式(6)–(8)、§4.2 式(16)–(17)，pp.305–306；[Rizvi–Pettee–Nachman v1](https://arxiv.org/html/2305.10500v1#S2)，§I 式(2)–(5)、脚注1，§II 式(6)–(12)、Table 1 | 完整用户共享活动变量；两类使用相同噪声标签采样律、平衡 BCE 学习 ℓ；p=sigmoid(logitρ+ℓ) 由公开活动先验修正。有限分类器不自动成为准确密度比或校准后验。 |
| denoising score matching；network preconditioning / 去噪得分匹配；网络预条件化 | [STMP v2](../../../reference/score_amp_20261015/cai2025_stmp_spawc_v2.pdf)，p.3 §III 式(14)、§IV-A 式(18)–(19)；[EDM](../../../reference/score_amp_20261015/karras2022_edm.pdf)，p.3 Table 1、§5 式(7)–(8) | F 只用活跃条件 MSE 训练，γ 为活跃实功率；16 束方差及完整用户网络为明确实现选择。L_F+L_BCE 不称为混合先验 DSM；理想两头组合 pF 给出混合均值，有限头不保证同一精确密度。 |
| Jacobian of the conditional mean；conditional covariance / 条件均值 Jacobian；条件协方差 | [Dytso–Poor–Shamai，TIT 2023 正式版](../../../reference/afdm_network_axes_20261013/phase2_representation/dytso2023.pdf)，p.1883 式(3)，§III Proposition 1 式(17)，p.1885；式(9)定义输入在前的 Jacobian | 本项目采用输出行/输入列约定 J_D=Cov(x\|r)T⁻¹；异方差一般非对称。∇ℓ=T⁻¹F 与 pF 的完整乘积导数直接由 Gaussian 模型推导；有限双头一致性另行报告。 |
| Wirtinger derivatives；Onsager correction；functions of all previous iterates / Wirtinger 导数；Onsager 校正；依赖全部历史迭代量的函数 | [Kunde v1](https://arxiv.org/html/2604.21115v1#S3.SS3)，§III-C 式(18)–(21)、Remark 14、Appendix B；[Fan v5](https://arxiv.org/html/2008.11892v5#S5)，§5 式(5.3)–(5.8)、Remark 5.1 | 实际 pF 映射含全部用户内依赖；以配对 JVP、16 组随机相位 DFT 探针估计完整256×256部分迹，同步阻尼保存历史反馈。固定 V、ρ 的偏导不含标签估计总导数；当前 AFDM 不宣称满足随机矩阵状态演化条件。 |

`joint_amp` 仅为软件入口名。[完整推导](../../STMP/docs/JOINT_AMP.md)逐式定义全用户双头、
score 换算、完整跨束校正及活动读出。[独立数学审查](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/joint_amp_20261015/MATH_AUDIT.md)
记录解析混合例子、导数约定和统计限制。完整用户信号输入不等于完整有色噪声条件化；
网络仍只使用16个逐束方差。原 Proposed 和逐束 `diffusion_amp` 均保留。

上述实现还将 EDM 直接跳连 p c_skip I 的部分迹精确扣加，再用相同探针估计
剩余完整导数；操作按 [式(15b)](../../STMP/docs/JOINT_AMP.md)直接列式，不另造方法名称。
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

[完整推导与审查](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/amp_foundation_20261015/MATH_AUDIT.md)与
[全部控制结果](../../../archive/paper_layout_20261026/original_paper/docs/history/results/amp_foundation_20261015/REPORT.md)分别记录代数、模拟证据和局限。
相关系数RMS、四阶量、相对更新与固定轮数AER均是显式定义的诊断量，不命名为新的算法。

## 查询偏离 AWGN 的方案调研（2026-10-15）

本节仅记录文献比较，不代表采用新算法；主报告见
[方案调研](../../../reference/awgn_solution_review_20261015/REPORT.md)。
既有 D-GEC、OAMP-MMV、VAMP、Memory AMP、FIRE、广义 Gaussian 条件均值术语沿用前述来源。

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| learned AMP (LAMP)；learned VAMP (LVAMP) / 学习型 AMP；学习型 VAMP | [Borgerding–Schniter–Rangan，TSP 2017作者稿](https://phil-schniter.web.app/pdf/tsp17_lamp.pdf)，§III-C Algorithms 2–3，pp.4298–4299；§V-A/B式(41)，pp.4300–4301；§VII | 展开迭代并学习线性/非线性参数的先例。真实 AFDM 查询微调、未知相位条件化和联合活动训练是待验证项目适配，不宣称已复现原论文。 |
| maximum likelihood estimation；activity detection via coordinate-wise optimization / 最大似然估计；逐坐标优化活动检测 | [Fengler等，TIT 2021作者稿v3](https://arxiv.org/html/1910.11266v3)，§II-A式(6)–(7)，§III-A式(8)–(9)，§III-C Algorithm 1；§IV-B4 | 直接观测协方差似然的来源。原文独立Rayleigh信道和用户标量导频不等于当前AFDM结构先验；256列不作256份独立天线样本。用于合成控制及备选设计，不替换主线分类器。 |
| anisotropic denoising score matching；normalized energy model / 非各向同性去噪得分匹配；归一化能量模型 | [Zilberstein–Segarra–Simoncelli–Guth，2026预印本v1](https://arxiv.org/html/2605.15487v1)，§3.1–3.3式(7)–(10)，Appendix C | 原文协方差族限制于空间域或Fourier域对角形式，不是任意full covariance的AFDM解决定理；本轮仅作研究储备。 |
| Exact Posterior Score Estimation (EPS) / 精确后验得分估计 | [Mammadov等，2026预印本v1](https://arxiv.org/html/2606.17048v1)，§3.2 Theorem 1式(11)–(12)，§3.4 Proposition 3式(15)–(16) | 精确关系基于已知线性Gaussian生成模型及对应条件去噪器。有限训练近似、同观测估计相位和任意已有迭代输入不自动继承精确性；未实施。 |

来源版本、最新非可分理论条件以及本地失败实验的适用范围分别见
[理论笔记](../../../reference/awgn_solution_review_20261015/theory_notes.md)与
[有色噪声笔记](../../../reference/awgn_solution_review_20261015/colored_notes.md)。

本轮后续[实际查询实验](../../../archive/paper_layout_20261026/original_paper/docs/history/results/query_matched_20261015/REPORT.md)只续训原分类器
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

[具体模型与来源](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/activity_posterior_20261015/SOURCES.md)、
[独立数学审查](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/activity_posterior_20261015/MATH_AUDIT.md)和
[完整结果](../../../archive/paper_layout_20261026/original_paper/docs/history/results/activity_posterior_20261015/REPORT.md)分别保存推导、术语边界和数值证据。
`activity_posterior_20261015`仅为实验目录名；本控制没有替换原Proposed或恢复score训练。

## 活动后验的局部提议与因子消息（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| informed proposals；balancing function；Barker choice / 利用目标分布的提议；平衡函数；Barker选择 | [Zanella，作者稿v1](https://arxiv.org/pdf/1711.07424v1)，§2.2 p.4式(2)–(4)，p.8 Table1与§4.1式(11)；期刊正式出版为JASA 115(530)，2020 | 实际核对v1的式号和页码。使用g(t)=sqrt(t)和g(t)=t/(1+t)作为提议权重，另作MH接受校正；后者不是Barker接受规则。单比特与活动交换的变度数图、0.1停留、归一化及非降邻边下界均为项目显式推导，未命名为新方法，不外推原文渐近最优性或全局混合保证。 |
| factor graph；sum-product；factor-to-variable message；clustering / 因子图；和积算法；因子到变量的消息；聚类 | [Kschischang–Frey–Loeliger，TIT 2001](https://www.mit.edu/~6.454/www_fall_2002/lizhong/factorgraph.pdf)，§II-C p.502式(5)–(6)，§V p.510，§VI-A p.513 | 标准边消息是单个目标变量的函数；本项目导出L=logit(p)−logit(实际输入ρ)。多个因子共享用户形成环时，正确单边相除不保证全局精确。保留联合活动的模块间传递与独立边际乘积必须区分；固定Gaussian反例仅用于核验。 |
| expectation propagation；moment matching / 期望传播；矩匹配 | [Minka，UAI 2001修订作者PDF](https://tminka.github.io/papers/ep/minka-ep-uai.pdf)，§2式(4)–(6)、§3式(8)–(10)，算法3(b)–3(d)，PDF pp.2–3 | 移除旧因子近似、乘真实因子、匹配矩、除去输入贡献；Gaussian自然参数相减按项目实坐标约定推导。程序仅核验恒等式，未完成新的物理接收机或score模块适配。 |
| cavity distribution；tilted distribution；site approximation；improper / cavity分布；tilted分布；因子近似；不能单独归一为概率分布 | [Vehtari等，JMLR 21(17)，2020](https://www.jmlr.org/papers/volume21/18-817/18-817.pdf)，§2.1 pp.5–6，§5.3 pp.18–19；阻尼讨论见§5.2 pp.17–18 | 使用原词避免把不同概率对象统称噪声。负Gaussian site精度不必导致总体分布不正常，但不能直接转成正AWGN方差；更新需要的cavity与匹配后分布须proper。本文献的阻尼讨论不当作当前AFDM收敛保证，本轮未新增阻尼实现。 |

[完整消息推导](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/activity_posterior_refinement_20261015/MESSAGE_DERIVATION.md)、
[提议来源与直接证明](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/activity_posterior_refinement_20261015/SOURCES.md)及
[结果报告](../../../archive/paper_layout_20261026/original_paper/docs/history/results/activity_posterior_refinement_20261015/REPORT.md)分别保存公式、适用条件和数值证据。
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

[实验协议](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/awgn_reference_ladder_20261015/PROTOCOL.md)区分解析控制、
真实信道下的人工算子、真相位oracle与原估计相位。随机化基础A的右子空间不等于
把完整A⊗I变成右酉不变矩阵。只有误差功率或四阶统计吻合不构成完整AWGN证明。
本轮未实现完整OAMP-MMV/LM-OAMP、未训练网络，性能和统计证据见
[报告](../../../archive/paper_layout_20261026/original_paper/docs/history/results/awgn_reference_ladder_20261015/REPORT.md)。

## 完整物理信道有限先验的Gaussian EP实现（2026-10-15）

本节更新前述因子消息条目的实施状态，不另立算法名称。

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| moment matching；cavity distribution；tilted distribution；site approximation / 矩匹配；cavity分布；tilted分布；因子近似 | [Minka，UAI 2001修订作者PDF](https://tminka.github.io/papers/ep/minka-ep-uai.pdf)，§2式(4)–(6)、§3式(8)–(10)、算法3(b)–3(d)，PDF pp.2–3；[Vehtari等，JMLR 2020](https://www.jmlr.org/papers/volume21/18-817/18-817.pdf)，§2.1 pp.5–6 | 已实现单个不可变Gaussian观测因子与逐用户可替换Gaussian sites；真实有限先验乘cavity后精确求矩。原子分布对连续Gaussian的通常KL不是有限值，本控制直接定义矩匹配，不宣称有限KL投影最优。 |
| damping；natural parameters；improper site / 阻尼；自然参数；不能单独归一化的site | 同上Vehtari，§5.2 pp.17–18，§5.3 pp.18–19，Appendix A | 已实现自然参数β=.5阻尼及最多12次减半回溯，允许负site精度；1e12条件数上限是本实验数值策略，不是proper的数学定义，也不保证AFDM收敛。该实现阶段不同于前述仅做恒等式审查阶段。 |
| Schur complement；marginalization / Schur补；边缘化 | [Walter–Eustice–Leonard，Exactly Sparse Extended Information Filters for Feature-Based SLAM，作者PDF](https://ttic.edu/ripl/assets/publications/walter07.pdf)，§II-A Table I，PDF p.4；§III-B2式(10a)–(10b)，PDF p.8 | 原文直接列出Gaussian信息矩阵和信息向量边缘化的Schur公式；本项目具体块积分见推导(P27)–(P28)。已另存数值计算修订，不把它称为新AMP算法，不将SLAM结论外推为本控制收敛。自身site不进入自己的cavity，其他用户site仍保留。 |

完整来源、S1/S2条件信息、实支撑表示及Gaussian查询成立条件见
[物理因子推导](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/physical_message_20261015/PHYSICAL_DERIVATION.md)。
有限先验、SVD支撑和条件数只是明确的模型与运算说明；未包装成既有论文中的方法名称。
本次query对角/各向同性近似在实SVD支撑坐标中，不能称为物理beam covariance验证。
原始相减缺陷和修订后仍有的Gaussian近似误差分别记录于
[结果报告](../../../archive/paper_layout_20261026/original_paper/docs/history/results/physical_message_20261015/REPORT.md)。

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
来源定位补充见 [SOURCE_NOTES](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_cai_relaxation_20261015/SOURCE_NOTES.md)，
近似与既有证据见 [PROPOSED_APPROXIMATIONS](../../STMP/docs/PROPOSED_APPROXIMATIONS.md)。

第二项沿用已登记的block uniform diagonalization（Fletcher等GEC，§II-A式(8)–(9)、
§II-B Algorithm 1，PDF pp.2–3），每用户一个Gaussian协方差标量。
复数MMV的分块平均迹、查询及外信息公式为项目推导，见
[STEP2_PLAN](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_cai_relaxation_20261015/STEP2_PLAN.md)；
不将有限score网络、site裁剪/复用或本AFDM算子归入原文保证。
当前估计相位两个预选困难条件未见AER下降，见
[第二项结果](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_cai_relaxation_20261015/step2/REPORT.md)。

第三项继续沿用Gaussian site、cavity distribution、moment matching及Bernoulli–Gaussian
等已登记术语。因子相除依据Minka §3式(8)–(10)、算法3(b)–3(d)，PDF p.3；
标量线性投影及活动证据定位为Cai v2 §III-A式(7)–(11)、§III-B式(24)–(30)。
将原混合矩表示成条件Gaussian密度，再以单用户矩阵似然替换原标量因子的末端处理，
是[STEP3_PLAN](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_cai_relaxation_20261015/STEP3_PLAN.md)中的项目推导。
本地相除不等于消除全局历史信息重复，工作因子的对数权重比不称为新的物理活动先验。
该候选未降低当前困难面板AER；不为此操作新造方法名称。

第四项使用sum-product algorithm（和积算法）及clustering（聚类），来源为
[Kschischang–Frey–Loeliger，IEEE TIT 2001](https://www.mit.edu/~6.454/www_fall_2002/lizhong/factorgraph.pdf)，
§II-C式(5)–(6)，p.502，以及§VI-A，p.513。这里仅保留一对用户的离散活动并求和，
不是实现完整junction tree，也不保证重叠局部边际是全局精确后验。
Gaussian因子相除沿用上述Minka定位，复MMV四状态Gaussian积分及全方差展开见
[STEP4_PLAN](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_cai_relaxation_20261015/STEP4_PLAN.md)。
伙伴选择分数为项目提出的活动混合均值不确定性传播能量，不作为已有论文的方法名。
这一候选未降低预选困难面板AER；具体有限范围见
[第四项结果](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_cai_relaxation_20261015/step4/REPORT.md)。

第五项沿用前文power posterior、thermodynamic integration、marginal likelihood及log Bayes factor。
来源为[Friel–Pettitt作者稿](https://www2.stat.duke.edu/~scs/Courses/Stat376/Papers/NormConstants/FrielPettitPath05.pdf)，
§3式(4)–(5)、§3.1式(6)，PDF pp.4–6；[Friel–Hurn–Wyse v2](https://arxiv.org/html/1209.3198v2#S2)，§2式(6)–(11)。
第五项复数条件矩积分、有限噪声支持起点项及旧网络代入见
[STEP5_PLAN](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_cai_relaxation_20261015/STEP5_PLAN.md)。数学恒等式不等于有限网络近似已正确；
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
[项目显式推导](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_cai_relaxation_20261015/MATRIX_MESSAGE_DESIGN.md)，
不是以上论文对AFDM的已有完整算法或性能保证。消息核查阶段只完成内核和数学核验；
后续矩阵条件非线性模块、阻尼及全接收机对比见[闭环初筛](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_cai_relaxation_20261015/matrix_receiver/REPORT.md)。

## 基线噪声估计实施（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| stopping criterion / 停止准则 | [Tropp–Gilbert–Strauss 作者稿](https://tropp.caltech.edu/papers/TGS05-Algorithms-Simultaneous-I-preprint.pdf)，§3.1 Algorithm 3.1 | SOMP 原文把停止准则作为输入，没有给出独立噪声估计。当前残差阈值使用下述空间噪声估计，是明确的项目适配。 |
| Gamma prior；EM / Gamma 先验；期望最大化 | [Zhang 2023 原文](../../../reference/zhang2023_gamp_sbl_grant_free_noma.pdf)，式(17)–(19)、Algorithm 1 | 噪声精度采用含输出后验方差的 MAP 更新；复 MMV 计数为 LM+c−1。当前 c=1+LM、d=LMσ̂²_spatial，沿用既有项目先验强度并以空间噪声估计设置尺度；数值强度不是原文给定值，同一观测提供尺度和似然，不是独立额外信息。弱先验首版的低估结果保存在历史报告。 |
| sparsity pattern learning / 稀疏模式学习 | [Ding 2026 原文](../../../reference/literature/ding2026.pdf)，式(12)–(13)、(19)、(26) | 原文更新稀疏概率，不提供物理噪声更新式。当前 GNN-ASPL 保留网络，用空间噪声估计代入 σ²；不将补充前端称为 Ding 原算法的一步。 |
| noise precision / 噪声精度 | [Wei 2022 作者稿](https://arxiv.org/html/2101.05629v1)，式(45)–(46)、Algorithm 1、§VI-A | 共享 MMV 推广保留 M tr(AΣAᴴ)；初始化 mean|Y|²/100。原文 c=d=1e−4；当前 c=1+LM、d=LMσ̂²_spatial 是抑制弱先验持续低估的项目适配，同一观测提供尺度和似然，不是独立额外数据。噪声、行方差和偏移使用同一轮后验。先前固定噪声版本仍作为显式参考。 |
| equivalent noise variance / 等效噪声方差 | [He 2018 作者稿](https://arxiv.org/pdf/1802.01290v2)，§III-A 式(4)–(6)及式(5)后定义 | 原文 σ̂=‖z‖₂/√K，由校正残差估计。当前复数矩阵 L-DAMP 沿用残差协方差；归一化等效误差和物理噪声分开记录。 |
| minimum description length (MDL)；sample covariance matrix / 最小描述长度；样本协方差矩阵 | [Nadakuditi–Edelman，TSP 2008 作者全文](https://math.mit.edu/~edelman/publications/sample_eigenvalue.pdf)，§II-A 式(5)–(7)及尾部均值定义，期刊 pp.2626–2627，重述 Wax–Kailath 1985，DOI 10.1109/TASSP.1985.1164557 | 用 MDL 选空间信号秩，尾部特征值均值给出白噪声拟合值。未实现 Nadakuditi–Edelman 随后提出的新估计器。该空间秩不是活动人数，不使用真实活动数。 |

具体公式、公开输入边界及门限复用范围见 [BASELINE_NOISE.md](BASELINE_NOISE.md)。
SOMP/GNN-ASPL 的补充前端依赖低秩空间信号与白噪声模型；当前样本相关性与可能的模型失配不满足任意场景下的一致性保证。
GAMP/SBL 的近似模型可能吸收未建模信号或噪声，学习方差不能未经验证就当作真实热噪声。

## 当前 Proposed 与 Cai 逐式核查补充（2026-10-15）

本次沿用上文登记的术语；完整推导、适用条件、实现对应与 Cai 式(1)–(66)覆盖表见
[逐式核查报告](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_cai_equation_audit_20261015/REPORT.md)。
以下原文定位同时核对了正式 PDF 页面与 arXiv v2，不将项目推导包装成原文定理。

| 原词或忠实译名 | 原文定位 | 本次核查与使用边界 |
|---|---|---|
| posterior variance / 后验方差 | [Cai 正式版](../../../reference/cai2026_score_based_jadce.pdf)，§III-B1 式(19)、(23)，PDF pp.6–7，印刷页3580–3581；[v2](https://arxiv.org/html/2506.00581v2#S3.SS2) | 式(19)印刷的pri中心与式(23)的条件中心方差不一致；按post中心解释才能对应。报告M15给出Gaussian反例；未得到作者勘误确认，不推断其代码照用了错误中心。 |
| second-order score matching / 二阶得分匹配 | 同文 §IV-C 式(50)–(54)、§V-A 式(56)，PDF p.9，印刷页3583 | 有限一阶网络下，总迹目标读出条件MSE，等于中心方差加均值偏差平方；这一限制同时适用于Cai与当前代码。总迹监督单独不识别逐天线子迹；报告M24–M26及零和扰动检查。 |
| channel power normalization / 信道功率归一化 | 同文 §V-B2 式(59)–(65)，PDF p.10，印刷页3584 | 式(59)按字面不是逐样本恒等式；报告M43–M44推导无偏功率估计及条件方差。式(60)逐用户尺度与式(61)共同噪声标签还包含共享近似。当前采用固定尺度，不直接采用该组功率估计。 |
| damping / 阻尼 | 同文 §V-B1 式(57)–(58)，PDF pp.9–10，印刷页3583–3584 | 当前均值和协方差分别算术插值，与作者代码的递归实现类型一致；不将其称为Gaussian分布混合的矩匹配或收敛证明。 |

观测矩阵适用性补充：[Cai §II-A式(3)–(4)、§V-C式(66)](https://arxiv.org/html/2506.00581v2#S5.SS3)
中的 partial orthogonal / 部分正交，指全局行Gram为标量阵，不能与单用户列块内部正交混同。
作者DFT实现的C_kᴴC_k=T P_tx I、单位自身响应和用户内白热噪声是根据原矩阵结构直接推导的性质，
并非任意部分正交矩阵都成立的新定理。当前AFDM的相应差异、实际矩阵检查及有限场景证据见
[近似适用性补充报告](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_cai_equation_audit_20261015/APPROXIMATION_ASSESSMENT.md)。
伪AWGN和右旋转不变条件沿用本文件已登记的Cai §V-B1及Fletcher等JSTAT 2019 §3–4、Theorem 1；
不把局部热噪声白化或平均方差匹配等同于实际完整查询服从独立AWGN。

矩阵消息的闭环初筛沿用以上 Gaussian、natural parameters、moment matching、damping、
conditional mean 和 posterior variance 术语。一般矩阵输入下的均值网络输出按条件均值回归解释；
有限均值网络下的条件均方误差仍包含均值偏差平方，参见上表Cai式(50)–(54)及项目推导。
均衡分类器logit与密度比的对应依据
[Menon–Ong](https://proceedings.mlr.press/v48/menon16.pdf)，§2.2、§3、§4.2式(6)–(8)、(16)–(17)，pp.305–306。
输入变换、矩阵阻尼等价式及正风险损失均明确写为[本项目适配](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_cai_relaxation_20261015/matrix_receiver/PROTOCOL.md)，
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
[分布核验报告](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_query_distribution_20261015/REPORT.md)与
[数学接口复审](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_query_distribution_20261015/MATHEMATICAL_INTERFACE_REVIEW.md)。

## 保留活动混合的局部消息核验（2026-10-16）

Gaussian mixture / Gaussian混合、moment matching / 矩匹配、normalizing factor / 归一化因子
依据[Minka UAI 2001](https://tminka.github.io/papers/ep/minka-ep-uai.pdf)，§2式(4)–(7)、§3式(8)–(10)，PDF pp.2–3。
本轮有限分量积分、自然参数凸目标及正标量精度边界是
[项目显式推导](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_mixture_message_20261016/DERIVATION.md)。
矩匹配只覆盖均值和协方差迹，不等于全协方差匹配或完整后验精确恢复。
局部负site精度只在乘积可积域内作约束诊断，不能直接解释为原接收机可接受的负方差输入。

Barker balancing function / Barker平衡函数沿用本文件已有Zanella v1 §2.2式(2)–(4)、Table 1来源，
及[已核验实现说明](../../../archive/paper_layout_20261026/original_paper/docs/history/results/activity_posterior_refinement_20261015/REPORT.md)；保留MH接受步骤。
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
公式见[本次推导P6–P8](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_probability_consistency_20261016/DERIVATION.md)。
该目标不是该文多类条件生成算法的原样移植，尚未完成候选训练或闭环验证。

参考密度采用Gaussian mixture，沿用前述Minka §2–3中的既有术语。
`log(q_1/q_0)=log(q_G/q_0)+log(q_1/q_G)`仅为密度比的恒等分解；
32组训练功率均值的参考构造及稳定求值均按操作和公式直接描述，未赋予新的算法名称。
条件均值与全方差分解见[推导P9–P10](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_probability_consistency_20261016/DERIVATION.md)，
参考本身的失败样本及数值核验见[开发对照](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_probability_consistency_20261016/reference_density/DEVELOPMENT_CHECK.json)。

后续使用w(v)=1/(s+v)乘条件均值回归损失，其中s为训练先验的每复坐标二阶矩。
这是同一条件平方风险分解的正权重推论，按公式描述，不称为文献中的新算法或新损失名称；
理想目标不变而有限优化的折中可能变化，见[后续候选推导与协议](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_probability_consistency_20261016/WEIGHTED_CANDIDATE_PROTOCOL.md)。

固定几何下的均匀相位积分按[项目公式G1–G8](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_probability_consistency_20261016/CONDITIONAL_GEOMETRY.md)描述，
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
[项目直接推导L1–L6](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_physical_linear_factor_20261016/DERIVATION.md)。
沿用Gaussian mixture、conditional mean、posterior covariance与QR factorization的上述原词；
相位积分仍依据NIST DLMF §10.32式(10.32.1)、(10.32.3)。
对给定协方差作Cholesky坐标变换只是Gaussian因子的代数计算，
不把它称作实际多用户反馈已独立化或Gaussian化，也不为这一组合另立方法名称。

## 保留 score 的 Gaussian 因子分解（2026-10-16）

| 术语 | 原文依据 | 本项目范围 |
|---|---|---|
| conditional score function；SNIPS / 条件 score 函数；文献算法名 SNIPS | [Kawar–Vaksman–Elad，NeurIPS 2021](https://papers.nips.cc/paper/2021/file/b5c01503041b70d41d80e3dbe31bbd8c-Paper.pdf)，§3.1 式(6)，§3.2 式(7)–(10)，PDF pp.5–6 | 仅借鉴所有观测奇异方向处于小噪声范围时的 Gaussian 噪声耦合。复数矩阵因子、归一化常数、活动混合及均值/方差恢复是 [S1–S8](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_score_factor_split_20261016/DERIVATION.md) 的直接推导；没有实现完整 SNIPS，也没有证明原网络给出精确可积 score。 |


## Proposed 物理噪声输入与方差消息（2026-10-16）

| 原词或忠实译名 | 原文定位 | 本次核查与建议范围 |
|---|---|---|
| AWGN；noise variance / 加性白高斯噪声；噪声方差 | [Cai v2](https://arxiv.org/html/2506.00581v2)，§II-A 式(3)，§III-A 式(7)–(8)，Algorithm 2 第1、5行 | 物理观测噪声 δ₀² 是输入参数；Algorithm 2 没有其估计步骤。[作者代码固定版本](https://github.com/chang-cai/score-massive-connectivity/blob/0c75680c966dcb8e46250de146f4c27e9294c283/main_stmp_jadce.py#L130-L139) 同样使用输入的 self.delta²。 |
| pseudo AWGN observation model；posterior variance / 等效 AWGN 观测模型；后验方差 | 同文 §III-B1 式(20)，§IV-A 式(44)–(45)，§V-A 式(55)–(56)，§V-B1 | TMP 产生的去噪输入方差及 score 网络恢复的后验方差均与物理噪声参数不同；更新前两者不表示已估计接收端噪声。 |

建议复用上文已登记的 Wax–Kailath MDL 空间协方差前端，将尾部特征值均值作为
Proposed 的物理噪声输入，归一化线性模块使用 σ̂²/s²，原迭代方差公式继续使用。
这项接收机适配尚未实施；它依赖低秩空间信号与白噪声模型，不称为 Cai 的噪声估计方法。
原论文及实现位置、已有 baseline 的噪声比值统计和验证范围保存在
[NOISE_REVIEW.json](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_1000_20261016/NOISE_REVIEW.json)。

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
| Langevin dynamics；unadjusted Langevin algorithm (ULA)；Ornstein–Uhlenbeck / Langevin动力学；未调整Langevin算法；Ornstein–Uhlenbeck过程 | [Wibisono, COLT 2018](https://proceedings.mlr.press/v75/wibisono18a/wibisono18a.pdf)，§2.1式(4)、Example 1，§2.2式(5)、Example 2，PDF p.4 | [局部推断规格](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_score_factor_split_20261016/LOCAL_INFERENCE_PROTOCOL.md)将固定矩阵换元后写成复数更新，噪声系数和离散Gaussian协方差直接推导。原文明确ULA有限步长存在偏差；其强凸等条件没有在本有限三网络向量场上得到验证，不引用为收敛保证。 |

“保留矩阵因子”是操作描述：保留一个用户内16×16精度矩阵J，而不是压缩为标量单位阵。
它不是全体用户的精确联合精度，也不意味着外部Gaussian消息已经消除真实用户反馈依赖。

同一Wibisono文献§2.1 Example 1（PDF p.4）给出Ornstein–Uhlenbeck过程的精确Gaussian转移。
[E1–E2](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_score_factor_split_20261016/GAUSSIAN_LINEAR_PROTOCOL.md)
固定每步的网络非线性项后使用这一线性解；对零活动贡献的Gaussian部分保持精确协方差，
不宣称整个有限神经向量场或非线性目标已得到精确离散化，也不为这一组合另造方法名称。

## 原score提议的接受校正（2026-10-16）

| 原词或忠实译名 | 原文定位 | 本项目范围 |
|---|---|---|
| Metropolis–Hastings；reversibility；test ratio / Metropolis–Hastings、可逆性、检验比值 | [Hastings 1970](https://probability.ca/hastings/hastings.pdf)，§2.2 pp.99–101，式(4)–(8)及连续密度段 | [A1–A3](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_score_factor_split_20261016/ACCEPTANCE_PROTOCOL.md)以原first决定Gaussian提议，用原activity logit定义有限近似密度并计算接受比。可逆性只针对该明确近似密度；不保证分类器校准、first/second条件矩一致或有限时长混合，不冠以新算法名。 |

## 联合观测因子的噪声层级（2026-10-16）

| 原词或忠实译名 | 原文定位 | 本项目范围 |
|---|---|---|
| annealed Langevin dynamics / 退火 Langevin 动力学 | [Song–Ermon 2019 v3](https://arxiv.org/html/1907.05600v3#S4.SS3)，§4.3 Algorithm 1 | 原文按噪声层级递减并按噪声方差缩放步长。本项目的[固定规格](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_joint_score_factor_20261016/PILOT_PROTOCOL.md)同时改变似然强度，使用[J1–J6](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_joint_score_factor_20261016/DERIVATION.md)精确辅助分解及矩阵预条件；这是项目推导，不称为原文算法的直接复现，也不借用其名义保证当前有限网络的收敛。 |

“联合观测因子”仅描述保留 CN(Y;AZ,D) 及所有用户共享残差的操作；不另造算法名。
它去除了逐用户外部反馈的独立 Gaussian 工作近似，但有限网络、离散步长、混合及估计相位的误差仍存在。

| 原词或忠实译名 | 原文定位 | 本项目范围 |
|---|---|---|
| Kullback–Leibler (KL) divergence / Kullback–Leibler 散度 | [Zhang等，NeurIPS 2023](https://papers.neurips.cc/paper_files/paper/2023/file/b5b4d92374323c53c24bbbc8ee0e715c-Paper-Conference.pdf)，§1，PDF p.2，定义及式(1) | [初始化尺度诊断](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_joint_score_factor_20261016/INITIAL_NOISE_PROTOCOL.md)用同协方差Gaussian的特例，转换到proper complex Gaussian后得到tr(δᴴP⁻¹δ)。只描述两个已指定的初始化条件分布，不是神经目标或真实后验间的散度，也不是满足三角不等式的距离。 |


## 酉导频下保留伙伴活动混合的消息更新（2026-10-16）

沿用既有 Bernoulli–Gaussian、Gaussian mixture、cavity distribution、site approximation、
moment matching 术语；依据 Minka 2001 §2式(4)–(6)、§3式(8)–(10)、Algorithm 3(b)–3(d)，
以及 Vehtari et al., JMLR 2020 §5.2 pp.17–18 的 natural-parameter damping。
来源：[Minka原文](https://tminka.github.io/papers/ep/minka-ep-uai.pdf)、
[Vehtari等原文](https://www.jmlr.org/papers/volume21/18-817/18-817.pdf)。

[本轮协议](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_unitary_mixture_20261016/PROTOCOL.md)在固定酉导频下，
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

[本轮协议](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_unitary_joint_ep_20261016/PROTOCOL.md)
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
[本轮协议](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_activity_repair_20261016/PROTOCOL.md)固定观测估计的每用户
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

[本轮规格](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_structured_iteration_20261016/PROTOCOL.md)采用上述矩形式：
精确计算指定 Gaussian sites 下的联合线性边缘，仅在逐用户网络接口作平均迹投影，再除旧site。
自然参数阻尼沿用上面已登记的EP来源。实际second为有限条件风险读出，此实现不计算完整
Jacobian sensitivity，故不能称为直接实现了满足原文MMSE假设的GEC，亦不继承自由能或收敛保证。
一般非酉用户块下，平均迹投影的自身响应及热噪声非白性均显式保存；未将统一迭代称为精确AWGN恢复。


## 专利交底书术语及变量含义核对（2026-10-16）

核对对象为《一种面向无GNSS辅助卫星接入的联合活动检测与信道估计方法》20261016114905版，修订输出为20261016122331版。下列编号为交底书公式编号。本节记录该稿的对外用语；研究历史中的内部变量名和代码接口继续按原记录理解。

| 核对对象 | 采用的表述及含义 | 文献或实现定位 |
|---|---|---|
| 信道查询、查询方差、公共查询方差 | 线性估计输出处用“外信息均值和方差”；经阻尼传入下一模块后用“去噪模块输入均值R、输入方差v”。原来的“查询”是项目内部叫法，不能当作该论文原词。v是所传递高斯消息的方差参数。 | [Cai等v2](https://arxiv.org/html/2506.00581v2)，Table I的extrinsic mean and variance；§III-A式(9)–(14)；交底书式(14)。 |
| 条件误差方差、共享条件误差方差 | 网络量写为“条件均方误差估计值”；按式(16)平均并设正下限后，将τ用作各终端共用的高斯近似方差。 | Cai §IV-C式(53)–(54)；本项目[训练损失](../../../src/afdm_jadcedd/experiment/training/scores/direct_objectives.py)的direct_second_loss；[THEORY](THEORY.md) T9–T10；交底书式(15)、(16)、(25)。 |
| 空间平均协方差 | 写明沿N²个AFDM输入、输出坐标组合取平均，保留M×M天线间信道误差协方差；属于文中高斯混合近似的矩。 | Cai §III-B3式(32)–(38)给出活动混合矩关系；本项目[denoiser](../../../src/afdm_jadcedd/algorithm/proposed/denoiser.py)的flat、gram、covariance计算；交底书式(21)。M×M形式及平均轴以本项目公式为准。 |
| 公共反馈方差（原用于bar t_X） | bar t_X称“有效信道平均方差”；γ_out称“返回线性估计的外信息方差”。两者分别位于高斯消息相除之前和之后。 | Cai §III-C式(39)–(42)；交底书式(22)、(23)。 |
| 训练支持区间 | 直接写“训练噪声方差范围”。 | [score_matching](../../../src/afdm_jadcedd/experiment/training/scores/score_matching.py)的噪声采样；denoiser的noise_support判断。0.001至100为当前实现参数。 |
| 折叠时延 | 实施例直接定义为“以采样点数表示的时延对16取余”；表中称“时延余数”。 | [路径响应](../../../src/afdm_jadcedd/algorithm/baselines/offgrid/atoms.py)的path_atom时延定义及[相位估计](../../../src/afdm_jadcedd/algorithm/phase_estimation.py)的搜索范围。 |
| 物理候选、物理频率、时延—相位峰 | 分别写为候选路径响应、多普勒频率、评分峰值及其对应时延和相位。直接描述搜索对象。 | [phase_estimation](../../../src/afdm_jadcedd/algorithm/phase_estimation.py)的峰值筛选、频率枚举及连续参数细化；交底书第一步、式(8)–(10)。 |

条件均方误差的判断依据是实际训练目标，而不是另命名一种方差。固定一阶网络后，式(25)在给定带噪输入和噪声方差下拟合该网络估计误差的条件期望。按THEORY T10，条件均方误差等于平均条件协方差迹加上均值估计偏差的平方项；因此将有限网络读出直接称为精确后验方差会遗漏后一项。交底书只需准确说明“估计均方误差，再用于高斯近似方差”的处理关系，不展开研究诊断。

已核实并保留的名称：

| 术语 | 原文位置 | 在交底书中的使用 |
|---|---|---|
| first-order / second-order score network；一阶／二阶得分网络 | Cai §IV-A末段、§IV-B–C式(46)–(54) | 使用完整名称；图中“一阶网络”“二阶网络”为同一对象的简称。 |
| denoising score matching；去噪得分匹配 | Cai §IV-B式(47)–(49) | 对应式(24)，按复噪声每个实分量方差v/2换算。 |
| LMMSE；线性最小均方误差 | Cai §III-A式(6)–(8) | 本稿式(12)、(13)是一般导频矩阵下的高斯线性更新。 |
| damping；阻尼 | Cai §V-B1式(57)–(58) | 当前均值、方差按新值权重0.2插值；该权重为本项目配置。 |
| conditional residual block、refinement block；条件残差块、特征细化模块 | Cai §VI-A2、Table III | 对应本项目[network](../../../src/afdm_jadcedd/algorithm/proposed/network.py)的条件RefineNet结构；通道数及连续噪声条件为当前实现。 |
| AFDM、DAFT、chirp-periodic prefix；仿射频分复用、离散仿射傅里叶变换、啁啾周期前缀 | [Bemani等2204.12798v2](https://arxiv.org/html/2204.12798v2)，§II-B式(11)–(17)、§III-A式(18)–(19)；交底书[4]的[2104.11331](https://arxiv.org/abs/2104.11331)题名亦已核实 | 保留已有名称；式(2)的多周期前缀及式(5)–(8)的具体算子以项目模型为准。 |
| fractional delay、fractional Doppler；分数时延、分数多普勒 | [Huang等原文](../../../reference/huang2026_prior_agnostic_afdm_diffusion.pdf)，§II式(4)–(5)，p.2950 | 连续时延、多普勒路径响应的来源；当前多用户、多天线观测和参数排列由项目定义。 |
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

本次定向核查见 [修复选择报告](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_repair_literature_20261016/REPORT.md)。保留既有EP、GEC、OAMP-MMV、LM-OAMP名称及其原适用条件，不把16×16矩阵消息或以下参数化冠以新的文献算法名称。

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

完整对照见[八篇文献核查](../../../reference/satellite_gfra_snr_20261016/REPORT.md)。这里的“总接收”仅说明公式分子包含所有活动用户，不作为新方法名称。

| 原词或忠实表述 | 原文定位 | 本项目使用边界 |
|---|---|---|
| signal-to-noise ratio / 信噪比：叠加接收信号功率基准 | [Ding 2026](https://doi.org/10.1109/TVT.2026.3729877)，§IV-B p.5；[Mao 2025](https://arxiv.org/html/2504.04686v2#S4)，§IV；[Zuo 2023](https://arxiv.org/pdf/2210.17355v1#page=25)，§V | Ding原印式为‖SZ‖²_F/(MLσ²)，模型式(9)用Ψ记号；Mao按角域位置累加‖Γg‖²；Zuo按超符号u累加‖G_u x_u‖²，u不是用户。都没有除活动用户数，支持当前总接收SNR作为一种已用口径，不证明作者代码逐实现调噪细节。 |
| signal-to-noise ratio / 信噪比：按卫星及观测窗口定义 | [Shen协作星座2025](https://arxiv.org/html/2408.02586v1#S5)，§V、式(18)–(19)、Fig.4；[Shen大差分时延2025](https://arxiv.org/html/2412.20806v1#S5)，§V、式(19)、Fig.7/9 | 前者每颗卫星的导频窗口；后者各时延块内Q帧全部用户信号。前者AER曲线−6至2 dB，后者−4至4 dB；不能宣称卫星GFRA不研究负SNR。 |
| normalized path power；average symbol energy / 归一化路径功率、平均符号能量 | [Shen GLOBECOM2022](https://arxiv.org/pdf/2208.01828v1#page=5)，§IV；[Xu TCOM](https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/AFDM-aided-Grant-Free-Random-Access-for-LEO/991050765702346)，§V | Shen明示Σ_i|h_ui|²=1、导频方差1/(MN)、SNR=10log10[1/(MNσ²)]；逐路径向量能量约束不等于实际接收能量恒定。Xu采用E_s/N_0且研究给定信道信息下的活动/数据检测，不能直接作为同任务JADCE的总接收SNR对照。 |

范围结论：Ding Fig.3的0、4、8、12、16、20 dB可作为本项目主评估扫描的文献参照。该取值是评估范围选择，不是统一物理下限，也不是功率分布或算法修复。此前单用户参考SNR的建议保留为可选的另一实验，不再表述为纠正当前总接收定义所必需。负SNR既有结果保留，任何新优势须在固定的新配对实验中验证。

2026-10-16 已知噪声条件核对：Cai [v2](https://arxiv.org/html/2506.00581v2) Algorithm 1、Algorithm 2 输入的 δ₀² 是物理热噪声方差；§III-A 式(7)–(8)直接使用它。迭代消息方差 v、τ 与该物理参数区分。[作者代码固定提交](https://github.com/chang-cai/score-massive-connectivity/blob/0c75680c966dcb8e46250de146f4c27e9294c283/main_stmp_jadce.py#L141-L149) 使用生成噪声的同一 delta²，未从观测重新估计该参数。当前原导频八点比较统一供给准确方差，详见 [实验协议](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_original_snr8_10_20261016/PROTOCOL.md)。

## 公共相位前端的计算优化调研（2026-10-17）

本次为定向文献核查，检索范围及建议见[调研记录](../../../archive/paper_layout_20261026/original_paper/docs/history/results/phase_frontend_research_20261017/RESEARCH.json)。未修改冻结算法，未测得优化后的加速比。

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
| structured sparsity；structured generalized approximate message passing (S-GAMP) / 结构化稀疏性；结构化广义近似消息传递 | [Sun等作者全文](https://livrepository.liverpool.ac.uk/3141858/1/Massive_Grant-free_OFDMA_with_Timing_and_Frequency_Offsets.pdf)，TWC 2022，DOI 10.1109/TWC.2021.3121066；§II-C 式(18)–(19)，PDF p.6；§III-A 式(20)–(41)，pp.6–9；§IV，pp.10–11 | 借鉴“用户不活跃或只对应一个偏移候选”的联合先验。完整信道块、冻结网络似然比、原公共标量EP反馈为项目适配；不宣称复现S-GAMP。独立候选查询、跨候选协方差投影和H/相位先验分解均显式记录于[候选推导](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_joint_phase_20261017/ALGORITHM.md)。 |

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

本轮针对当前论文英文正文逐项核对方法名、缩写和自拟复合表达。下表为当前稿用法；上文实验与历史候选的记录保留。详细修改见 [核对报告](../../checks/terminology_20261018_125231/TERM_AUDIT.md)。

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

来源：本机完整五页 [Huang 等 PDF](../../../reference/literature/huang2026.pdf)，*Prior-Agnostic AFDM Channel Estimation for High-Mobility LEO Satellite Communications Using Diffusion Models*，IEEE WCL 15，2949–2953，DOI 10.1109/LWC.2026.3689601。本次提取全部正文，并视觉核对 p.2951、p.2952 的公式、Algorithm 1 与曲线；旧记录中的 2949–2952 未包含参考文献所在末页。

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

独立研究方案见 [消息推导及训练目标](LSTMP_DERIVATION_AND_TRAINING_20261020.md)，不改写已冻结主线。复用 `THEORY.md` 的工作后验、Gaussian 条件化和局部混合矩，补齐新五层的校准、残差和训练风险解释。Gaussian projection、moment matching、expectation propagation、extrinsic message 仍分别采用 [Minka 2001](https://tminka.github.io/papers/ep/minka-ep-uai.pdf) §2式(5)–(6)、§3式(8)–(10)，以及 Cai §III 的用法；本项目各向同性协方差投影、自然参数阻尼和正精度约束逐式写明，不宣称全局收敛。

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

更新后的 [推导及训练方案](LSTMP_DERIVATION_AND_TRAINING_20261020.md) §4.1、§9 记录上述关系。确定性数学核验22项全部通过；新增混合 score 检查以数值差分对照显式混合密度，校准位置检查覆盖p=0、p=1及中间概率。不包含接收机性能实验。

## 展开接收机训练协议与统计权重（2026-10-20）

[具体训练方案](LSTMP_TRAINING_PROTOCOL_20261020.md) 延续上述 Wei 的逐层联合训练、独立 score 网络及 Cai 的有效信道混合结构。首版五层、保留活动分类器与残差反馈；预训练与接收机微调分阶段，后者的默认方案允许所有任务梯度更新 score。阻断活动 BCE 到 score 参数的路径作为独立对照，不把这种对照描述为 Wei 或 Cai 的既定训练方法。

BCE 沿用本文件已有 Menon–Ong §3、§4.2 的 logistic loss 含义。按用户汇总的训练目标为 sum(BCE)/sum(K)；均匀抽取单场景时，将该场景的平均用户 BCE 乘 K/mean(K)，其期望梯度对应此数据集目标。这是有限和的直接重排，不是新方法名称。当前4800训练场景恰为24条件各200场景，mean(K)=160/3，因此K=20/40/100的乘数为0.375/0.75/1.875；开发验证的1200场景为24条件各50场景。来源为冻结五层MANIFEST中的实际索引，只读核对未生成新场景。

活动优先的检查点选择是本项目任务取舍：在当前深度平均场景NMSE距最佳值不超过0.3 dB的检查点中选择最低pooled AER；0.3 dB是事先声明的重建容差，不是文献结论或统计显著性界限。阈值0.5、初版BCE权重0.1、前层监督权重0.2及学习率与轮次均有明确配方；除Wei已报告的层监督权重外，其余数值不借论文名义声称最优。

该协议尚待独立训练入口实现，没有启动训练。理论恒等式通过核验、工作后验具有明确假设与真实接收机达到性能目标是三个不同层次；22项数学核验不证明五层足够、残差估计精确或联合梯度必然优于分开的梯度。

## 活动分类损失与 score 联合训练的文献依据（2026-10-20）

完整来源、章节、公式和适用边界见[专题调研](LSTMP_CLASSIFIER_SCORE_TRAINING_REVIEW_20261020.md)。本次仅补充研究文档，没有训练或新增接收机性能结果。

- **Soft-output active user detection／软输出活动用户检测、分别训练与联合训练**：采用 Sun 等 [ISWCS 2024 作者稿](https://arxiv.org/html/2312.12874v2) §III-B–C 式(21)、(24)–(25)，以及其 [2025 扩展稿](https://arxiv.org/html/2502.13390v1) §V-C–D 式(43)、(45)。前者分别使用数据重建误差与活动 BCE，后者采用活动加权数据重建误差共同训练；不得把后者误记为本项目的 NMSE＋BCE。
- **Energy-based model／基于能量的模型、联合分类与 score 学习**：依据 Guo 等 EGC，[ICCV 2023 官方页面](https://openaccess.thecvf.com/content/ICCV2023/html/Guo_EGC_Image_Generation_and_Classification_via_a_Diffusion_Energy-Based_Model_ICCV_2023_paper.html)及[作者稿 v3](https://arxiv.org/html/2304.02012v3) §3.2 式(14)–(17)、Algorithm 1。共同参数化概率模型的做法不同于两个任意输出头相加损失。
- **Classification-Denoising Networks**：Thiry–Guth [2024 v1](https://arxiv.org/html/2410.03505v1)，§3.3 式(13)为 CE＋DSM，§4.1 Table 1 提供同架构单任务与联合训练比较。该版本按预印本记录，不根据投稿抬头宣称会议录用。具体数值与适用范围见专题调研。
- **Denoising Likelihood Score Matching，DLSM**：Chao 等 [ICLR 2022 原文](https://arxiv.org/html/2203.14206v1)，§4.1–4.2 式(10)–(11)、Fig. 2，先训练 score，再固定它训练分类器。**Classifier guidance／分类器引导**涉及分类器对输入的梯度，不等同于分类损失对 score 参数的梯度。
- **Score Calibration loss**：Huang–Chen–Lin [NeurIPS 2022 Workshop on Score-Based Methods 原文](https://www.csie.ntu.edu.tw/~htlin/paper/doc/wssbm22cond.pdf)，§3–4 式(3)–(5)、Fig. 1、PDF 第2–3页。该名称仅对应原文对分类器能量导数的训练目标，不用于命名本项目的残差校准或活动概率阈值调整。
- **Soft-output joint channel estimation and data detection**：Song 等 [2021 作者稿](https://arxiv.org/html/2112.00330v1)，§IV-A–B 式(23)–(24)，以比特 BCE 训练展开参数的超网络。其检测对象是数据比特，不可当作活动 BCE 或 score 网络的直接实验。

专题调研中的按损失选择参数梯度，是本项目消融的精确定义，不赋予新的方法名称。阻断 BCE 更新全部 score 参数仍保留重建损失、活动混合与跨层反馈；数学后验耦合并不决定训练时必须采用哪一种梯度选择。Wei 的单用户微调和 Cai 的二阶损失截断均不足以单独决定这一问题。

进一步的条件风险核对见专题调研 §6，沿用本文件既有 conditional mean、squared error、BCE 与 KL divergence 的含义。固定查询与普通平方误差下，有效信道重建误差加正权重 BCE 可以同时以正确活动概率和活跃条件均值为最优值；不能将乘积误差存在多种分解，误述为完整目标在理想函数空间仍不可辨识。单独活跃条件信道监督沿用推导 D26，真值仅用于训练标签；当前仅提出独立对照，未落实为接收机改动。梯度中的活动概率因子只描述一条直接路径，不代表已经测得完整网络的梯度衰减或 AER 退化原因。

### 2026-10-20 七层结果对训练设计的证据补充

[七层设计分析](../../../result/lstmp_depth7_design_review_20261020/REPORT.md) 沿用上述 NMSE、MD、FA、BCE、conditional mean 与 Adam 的定义，不引入新方法名称。活跃用户误差明确指真实活跃用户上 `p*mu` 的误差，不将其写成未保存的 `mu` 条件去噪误差；负的原始扣噪声残差不等于最终传入网络的负方差。当前结果没有隔离 BCE 到 score 的梯度，也没有开展方差计算的单因素消融。

论文定位再次核对：[Wei §III-C 式(12)、§III-D、§V-A](https://arxiv.org/html/2610.17785v1) 分别对应残差方差、逐层联合微调和独立层 score；[Cai §III-B 式(35)–(38)](https://arxiv.org/html/2506.00581v2) 对应活动混合均值、方差与方差平均。新层适配时固定旧参数、较低旧层学习率、条件信道辅助监督及按 MD/FA 约束选模均是本项目待验证的训练选择，不表述为这些论文已经证明的最优组合。

## 统一的条件信道与活动监督协议第二版（2026-10-20）

[第二版训练协议](LSTMP_TRAINING_PROTOCOL_20261020_V2.md)沿用 conditional mean、DSM、BCE、layer-wise training 和 fine-tuning 的原有含义，不赋予新的方法名称。来源分别为 Cai §III-B 式(30)、(35)–(38)、§IV-B 式(48)–(49)，以及 Wei §III-D、§V-A；Adam 状态定义沿用本文件既有 Kingma–Ba Algorithm 1 记录。

第二版主目标改为固定训练能量归一化的活跃条件信道平方误差，加按用户平均的自然比例 BCE；有效信道以 `p*mu` 组合并独立评价，直接有效信道监督另作对照。T6–T7 是本项目的条件风险展开和全期望关系，不声称 Cai 或 Wei 已验证这个具体训练目标。固定查询、有限二阶矩和自由函数空间的条件须保留；共同最优输出不能证明有限展开网络的优化收敛或泛化。

主候选允许两项损失更新可训练参数，另以 T10 精确定义仅排除 BCE 对全部 score 参数梯度的对照。条件信道损失不直接依赖同层活动头，但可经后层查询依赖早期活动头。关闭 BCE 参数梯度不等于消除所有活动影响，也不等于恢复精确 AWGN 先验 score。

用户明确要求避免针对条件或既有结果进行特调。第二版不采用前述困难条件专属选模门槛、相对现有检查点的退化容差或带额外系数的第三项辅助监督；全部场景采用同一训练目标和验证选择规则。等系数、统一阶段预算及联合学习率倍率仍是公开的研究配方，不宣称不存在超参数或已被证明最优。此前讨论保留为研究历史，不作为最新执行规则。

## DCN / TWC稿件分离及新稿术语核对（2026-10-21）

DCN与TWC为作者指定的稿件版本标签，不是算法名称或发表状态。
旧稿保存在 paper/DCN；新稿位于 paper/TWC。新稿不另造算法缩写，
不把Wei–Yuan的L-STMP名称当作本项目原创名称。
逐章来源与实现对应见 [TWC来源记录](../checks/SOURCE_MAP.md)。

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

本轮核对本地 [Wei–Yuan 作者稿](../../../reference/literature/wei_yuan_2026_lstmp_v1.pdf)
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
推导核验见 [修订记录](../checks/argument_revision_20261021/README.md)。

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
具体修改及检查见 [因子图补充记录](../checks/factor_graph_20261021/README.md)。

### 2026-10-21：相位估计改进调研

本节对应 [相位估计调研](PHASE_ESTIMATION_REVIEW_20261021.md)，用于候选分析，
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
[摘要及前五章修订记录](../checks/abstract_ch1to5_polish_20261021/README.md)。

### 2026-10-21/22：Shen 相位更新的 AFDM 候选实现

| 表述 | 原文定位 | 本项目使用与限制 |
|---|---|---|
| expectation-maximization；phase rotation；projection | Shen et al., arXiv:2412.20806v1, §III-C，式 (47)–(53)，Algorithm 1 | 保留二次型及 `A u=b` 后逐元素投影到单位圆的步骤。十层均值和经校准的反馈方差是 AFDM 适配；反馈方差仅为近似，不将候选称为精确 EM 或完整论文复现。 |
| posterior variance | 同文式 (38)、(49)–(51) | 原文通过消息传递获得。当前网络没有同样的后验方差；代码和报告明确标记 variance proxy，不混称为已验证的 posterior variance。 |

逐用户 `exp(j q beta_k)` 约束及对它的最小平方距离投影直接用公式描述，不新造算法名称。
它不包含时延、物理多普勒原子或别名搜索；斜率约束为项目适配，不归于原文式 (53)。
详见 [候选实现与验证协议](SHEN_PHASE_IMPLEMENTATION_20261021.md)。

### 2026-10-22：协方差候选及训练信道样本辅助相位估计

| 既有术语或运算 | 核验原文 | 当前使用及边界 |
|---|---|---|
| Non-Negative Least Squares；sample covariance | Fengler et al., arXiv:1910.11266v2，§III-B 式 (26)–(29)，[原文](https://arxiv.org/html/1910.11266v2) | 参考协方差矩阵拟合。AFDM 块导频和相位扩展是项目试验，未继承原文独立衰落假设下的恢复保证；该开发分支失败。 |
| separable nonlinear least squares；variable projection | O’Leary–Rust，*Variable Projection for Nonlinear Least Squares Problems*，§1 式 (2)–(3)、§2 式 (5)–(7)，[作者稿](https://www.cs.umd.edu/users/oleary/software/varpro.pdf) | 给定训练信道样本与相位时，解析消去一个复线性增益，再搜索相位。训练样本集合及三轮坐标更新是本项目具体近似，不称为原文算法的完整复现。 |

“完整训练信道样本匹配”“无相位证据时保留零斜率”等仅为运算描述，没有新造算法名称
或缩写。当前做的是最大匹配，不是对训练样本的边缘化；不得称作精确边缘似然或精确 EM。
固定匹配的复高斯噪声尾尺度只启发阈值，不能赋予相关样本、连续精化及失配残差未经
证明的虚警保证。详见 [进展和验证范围](PHASE_ESTIMATION_PROGRESS_20261022.md)。

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
  适用限制见 [METHOD.md](../../../result/candidates/phase_covariance_prior_20261022/METHOD.md)。
- 基于固定活动概率门限组合连续更新与残差协方差更新，属于本项目实现选择。
  使用操作的直述，不将其包装为文献中的 EM 方法；组件目标下降不代表组合目标下降。

### 2026-10-22：固定十层内部的参数和消息更新

沿用上节 Shen §III-C 式(48)–(53) 的后验二次型出处及 Fengler §III-B
式(26)–(29) 的协方差拟合出处。以下均为本项目直接描述的操作，不另造方法名称：
将参考时刻固定在帧序列中心并随斜率更新转换 Gaussian 消息均值；将同帧协方差块
置零后拟合剩余项；用更新后的观测矩阵重算线性查询及外信息反馈。
后两项没有上述论文给出的性能保证，尤其不能把点估计扣除或未训练的网络顺序
称为精确 EM。具体式子、十层调用约束及失败结果见
[实现说明](../../../result/candidates/phase_covariance_prior_20261022/METHOD.md)和
[开发记录](../../../result/candidates/shen_parameter_update_20261022/REPORT.md)。

### 2026-10-22：本层软均值用于相位二次型

出处仍为 [Shen 作者稿](https://arxiv.org/html/2412.20806v1#S3.SS3)，§III-C
式(48)–(51)：相位目标使用信道均值与二阶矩，式(51)写作均值外积加对角方差。
本项目补充的代数事实是：若跨用户协方差为零，用户内协方差项在每用户单位模
相位下与斜率无关。可从相位优化中删去这些常数，但不能声称真实后验满足该
近似。使用神经软信道均值、共同斜率及中心参考仍为项目改写；不称为精确 EM
或原文投影规则。推导与独立数值检查见
[实现说明](../../../result/candidates/phase_covariance_prior_20261022/METHOD.md)。



### 2026-10-22：摘要及前五章的原文用语与推导归属

本轮修改 `paper/TWC` 当前稿件，作者再次要求采用 Cai 与 Huang 的原文术语。
三项贡献保留为 AFDM 传输与输入输出模型、基于得分的生成式信道先验、深度展开 MP 接收机。
具体对照及修改依据见 [修订记录](../checks/logic_provenance_20261022/README.md)。

| 原文用语或结果 | 原文定位 | 本稿使用及归属 |
|---|---|---|
| score-based generative channel prior / 基于得分的生成式信道先验 | [Cai 正式版](../../../reference/literature/cai2026.pdf)，§I-A，第3576页；§IV-A，第3582页 | 直接沿用这一名称。训练样本具有连续时延与多普勒频移，是样本生成说明，不另命名先验。 |
| AFDM effective channel / AFDM 有效信道；fractional delay and fractional Doppler；off-grid effects | [Huang 正式版](../../../reference/literature/huang2026.pdf)，§II，第2950页，式(4)–(5)及后文；§III-A，第2951页，式(6)–(7) | 描述学习对象和off-grid动机。多天线张量、长前缀条件、跨帧排列用本稿公式直接说明。连续基函数的坐标写法属于本稿模型表示，不称为原文逐字给出的公式。 |
| multi-frame transmission；quasi-static channel | [Shen 作者稿](../../../reference/literature/shen2025.pdf)，§II，PDF第4–5页，Proposition 1，式(8)–(10)及Q=8/Q=25讨论 | 借鉴共享信道增加观测及检查块内物理变化的思路。本稿的跨帧分离由AFDM路径算子直接代入推出。 |
| Gaussian extrinsic message；channel denoising；device activity denoising | Cai，§III-A/B，第3579–3581页，式(6)–(11)、(35)–(42) | 作为已有推断结构引用。现有可训练参数和残差方差构造沿用项目定义及既有来源记录。 |
| posterior mean；Tweedie's formula；denoising score matching | Cai，§III-B式(35)–(38)，第3581页；§IV-A/B，第3582页 | 区分已有混合均值与score关系、Gaussian消息近似和接收机训练。活动概率进入残差与后续消息的训练依赖由本项目计算图确认。 |
| equivalent Gaussian observation；damping | Cai，§V-B1，第3583页，式(57)之前的说明 | 原文支持感知矩阵和系统维度影响高斯近似。相位改变导频行内积属于本稿代数结论，不据此声称高斯近似必然失效。 |

新增圆轨道几何界直接从本稿 `eq:geometry` 求导得到：
`nu_dot=(fc/c0)[v^T(I-u u^T)v/r-u^T a]`；用 `r>=h` 与
`||a||=v^2/(R_E+h)` 上界得到正文的 `B_nu`，再积分得到时延变化及相位误差界。
这些是本稿自己的推导，数值来自 `src/system/config.py` 及场景几何常量；不是 Shen 的数值。
[计算记录](../checks/logic_provenance_20261022/model_scale_check.json)保留所有检查的帧数，
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
[实现说明](../../../result/candidates/phase_covariance_prior_20261022/METHOD.md)。


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
[实现说明](../../../result/candidates/phase_covariance_prior_20261022/METHOD.md)和
[开发报告](../../../result/candidates/shen_parameter_update_20261022/REPORT.md)。


### 2026-10-22：TWC正文中H与X的指代区分

沿用Huang正式版§II式(4)–(5)、第2950页的AFDM effective channel，以及Cai正式版§II-A、Table I、式(4)附近、第3578页的`X_k=alpha_k H_k`。在本稿共用语境中，`H_k`表示AFDM信道张量，`X_k`为它与活动指示量的乘积；后者直接用公式和符号说明，不另外命名。条件信道估计、活动概率及其乘积仍依据Cai§III-B式(35)–(38)、第3581页。术语未改变，修订只消除同一简称对不同对象的指代歧义。具体修改和本项目初始化、梯度路径依据见[行文复核记录](../checks/style_logic_review_20261022/README.md)。

### 2026-10-22：十层内部的斜率及信道旋转更新

沿用上文已核对的 Shen §III-C 式(48)–(53) 的期望二次型和相位旋转，及 GPML
§2.2式(2.30)、印刷p.19的 Gaussian marginal likelihood。固定用户的共同单位模
信道旋转并解析消元后，最大化复相关和的模平方；所得斜率目标为三角多项式，
使用驻点求值。该消元、共同斜率和按已有活动概率组合提议均为本项目直接列式，
没有把它们命名为文献中的新方法或称作Shen原始更新。

对扣除其他用户软信道均值后的剩余观测使用固定功率Gaussian目标，亦只是近似。
神经消息、天线独立假设及两个提议的组合不保证精确后验或整体目标下降。原110层
历史实现仅复用代数辅助函数，当前执行结构为十层各一次；具体公式和归属见
[实现说明](../../../result/candidates/phase_covariance_prior_20261022/METHOD.md)。

## 原场景上的初值半步、条件均值和相位更新次数检查

继续沿用前文已核对的 Shen §III-C 式(48)–(53) 的期望二次型及相位旋转，
与 GPML 第2章 §2.1.1 式(2.6)–(2.8)、印刷p.9 的Gaussian条件均值和协方差。
本轮“网络软均值加Gaussian条件协方差”直接描述项目实际代入，不称为文献提出的
新算法或精确神经后验。相位初值取主值差的一半、按固定二次型变化停止坐标扫描，
均直接给出公式和数值条件，不将数值停止解释为相位正确或统计收敛保证。
公式和适用边界见[实现说明](../../../result/candidates/phase_covariance_prior_20261022/METHOD.md)。

## 原场景上的初值更新惩罚、连续重求解及完整复现

沿用已核对的 GPML §2.2式(2.30)、印刷p.19的Gaussian marginal likelihood，
以及§5.4式(5.9)、印刷p.114的协方差参数梯度；共同相位斜率模型和固定功率限制是本项目
明确列式的近似。`M*L+lambda*改变坐标的个数`、固定lambda=1及接受坐标的连续重求解
直接描述操作，不另造方法名，不称为AIC、BIC、似然比检验或校准置信度。
神经层间二次型继续沿用前文Shen §III-C式(48)–(53)的出处及本项目改写边界；
本次组合不等于Shen原始EM，也不承诺整体目标或实际相位误差下降。
参见[实现公式](../../../result/candidates/phase_covariance_prior_20261022/METHOD.md)。

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
[推导与边界](../../../result/candidates/phase_gaussian_em_20261022/DERIVATION.md)。

## 2026年10月22日 连续相位求解与已知活动先验

`L-BFGS-B` 使用 Byrd、Lu、Nocedal、Zhu 的 *A Limited Memory Algorithm for Bound Constrained Optimization*，§2，作者预印本p.2–3；[原文](https://users.iems.northwestern.edu/~nocedal/PDFfiles/limited.pdf)。数值停止与投影梯度的区别依照 *Algorithm 778: L-BFGS-B* §5，作者预印本p.6；[原文](https://users.iems.northwestern.edu/~nocedal/PDFfiles/lbfgsb.pdf)。不将函数容差停止称为全局收敛或梯度达到指定阈值。

`maximum a posterior probability (MAP) estimation` 与独立 Bernoulli 活动先验采用 Jiang、Cui，*ML and MAP Device Activity Detections for Grant-Free Massive Access in Multi-Cell Networks*，§III-B、arXiv预印本p.13–16式(11)、(13)，Appendix D p.34式(36)；[原文](https://arxiv.org/pdf/2106.10438)。本项目的活动项系数 `log((1-rho)/rho)/M` 直接由已知活动概率导出；共同相位斜率、相关有效信道二阶矩及连续尺度拟合均明确为项目扩展，不称为原文算法复现。

“功率方向导数的驻点作为连续相位起点”“在固定活动集合内连续优化”仅描述公式和操作，不另造方法名。统一目标仅指相位前端，冻结十层网络不被包装为其精确后验求解器。见[连续求解推导](../../../result/candidates/phase_likelihood_solver_20261022/DERIVATION.md)及[活动先验推导](../../../result/candidates/phase_activity_prior_20261022/DERIVATION.md)。

### 2026年10月22日 固定神经消息下的非零均值边缘似然与广义EM

沿用 GPML 第2章 §2.1.1 式(2.6)–(2.8)、p.9和§2.2式(2.30)、p.19的 Gaussian 条件矩与 marginal likelihood，第5章§5.4式(5.9)、p.114的协方差导数。非零均值残差的导数、共同斜率和单位模信道旋转的坐标变换由本项目直接列式；不另命名为已有方法。

固定高斯消息时的一次条件矩计算和降低期望二次型，使用 Dempster等§3、p.7、式(3.5)、Theorem 1式(3.7)–(3.10)定义的 generalized EM；相位二次型沿用Shen§III-C式(48)–(53)的出处及上述项目改写边界。消息随神经层变化，不能因此宣称整个十层网络满足固定全局目标的EM单调性。详见[非零均值目标](../../../result/candidates/phase_conditional_likelihood_20261022/DERIVATION.md)与[各向同性消息更新](../../../result/candidates/phase_message_gem_20261022/DERIVATION.md)。

## 2026年10月22日 STMP 复用高斯消息相位更新

STMP 使用同一 generalized EM（广义EM）定义、同一 GPML 高斯条件矩和 Shen 期望二次型出处，章节、式号及适用范围见上一条。本项目将 STMP **阻尼后的实际高斯外信息**对应到该固定消息模型；活动概率已经通过联合信道矩进入外信息，不再另乘概率或按活动判决筛选用户。缓存信道均值同乘 `exp(i theta_k)`、重建线性算子、重置停止计数以及第60至140次的更新安排，均是明确写出的实现操作，不包装成文献已有的新方法名称。固定消息的目标不增加不能推广为整个 STMP 的全局单调性。见[STMP 接入说明](../../STMP/docs/STMP_PHASE.md)。

### 2026年10月22日 活动概率 条件信道矩与反馈误差的候选方案

沿用 [Wei–Yuan 原文](https://arxiv.org/html/2610.17785v1) §III-A、§III-D 的 finite-depth unfolding 和训练思路，以及 §III-C 式(12)的 residual-based variance estimate；保留 [Cai 等原文](https://arxiv.org/html/2506.00581v2) §III-B3 式(35)–(42)的有效信道均值、混合方差、Gaussian projection 与 extrinsic message 定义。Cai §III-B2 式(26)–(30)采用 Gaussian 外信息近似计算活动概率，不能描述成由任意先验的单点均值和方差精确得到边际似然。

局部 Gaussian 查询下的条件均值 Jacobian 与条件协方差采用 [Dytso–Poor–Shamai](https://arxiv.org/pdf/2104.01883) §IV Proposition 1、式(22)、PDF p.5。活动 log odds 的梯度及有效信道均值的导数由本项目直接求导得到；固定复方差 v 时实坐标噪声方差为 v/2，不能混用整条接收机的总导数。该关系只作理想局部模型诊断，不作为有限 AFDM 查询的无条件约束。

条件误差、中心后验方差与学习反馈参数保持前文 D17–D21、D29–D30 的区分。以固定有限均值的平方误差训练正尺度，使用 Gaussian 负对数密度的标量形式 log(t)+e/t；函数空间最优值是相应特征下的条件误差。其代入 p*t+p*(1-p)*||mu||²/D 定义近似混合分布的方差，不自动等于真实联合条件误差。方案中的小型误差输出分支、分阶段梯度安排及配对选模属于本项目待验证设计，不另造算法名称，也不声称 Wei 或 Cai 已验证其性能。

具体关系、实现接口和对照组见 [改进方案](WEI_CAI_ACTIVITY_CHANNEL_VARIANCE_PLAN_20261022.md)。本轮仅进行确定性概率与代数核验；不启动训练、批量接收机实验或切换当前主线。

### 2026年10月22日 条件接收机的查询尺度与活动反馈核查

线性估计的 decorrelated 定义沿用 [Ma、Ping，Orthogonal AMP](https://arxiv.org/pdf/1602.06509v3) PDF p.3 式(12)–(15)；相应误差假设见 p.4 Assumptions 1–2，残差估计见 p.5 式(30)–(31)。本项目对当前 gamma 参数化直接计算固定标量参数时的迹导数与工作模型误差协方差；这些是代码公式的推导，不是 OAMP 对本项目有限 AFDM 接收机的保证。Gamma=1 只恢复所述迹条件及工作模型平均误差标签，不能据此称查询为独立 AWGN。

沿用 [Wei、Yuan](https://arxiv.org/html/2610.17785v1) §III-B 式(6)–(10)、§III-C 式(11)–(12)和 [Cai 等](https://arxiv.org/html/2506.00581v2) §III-B3 式(35)–(42)对 Gaussian 消息、经验残差估计及活动混合矩的表述。当前残差的二阶矩展开、零空间反例及概率到均值和共同尺度的导数均由项目独立列式，不能称为文献已证明的退化原因。旧冻结 STMP 同样采用各向同性投影。

Gaussian 查询下真实条件均值的 Jacobian—协方差关系继续采用 [Dytso、Poor、Shamai](https://arxiv.org/pdf/2104.01883) §IV Proposition 1、PDF p.5 式(22)。完整有效信道映射为 p*mu，其导数包含活动概率项；任务微调网络的导数只作局部增益诊断，不能自动视作真实后验方差。

围绕固定有限估计器的 Gaussian 标量负对数密度 log(t)+e/t，其最优输出是对应特征下的条件误差；本文将之称为误差尺度，继续区别于中心后验方差。精度增长上限、已存修正方向的真值最优缩放、可观测与零空间误差分解均直接给出公式，不新增方法名称；前者只保证指定上限，后两者仅为诊断。

完整公式、既有数据证据、未验证候选与回退条件见 [条件接收机核查](CONDITIONAL_RECEIVER_AUDIT_20261022.md)。本轮不修改冻结接收机，也不启动训练或接收机实验。

### 2026年10月22日 Cai 公开代码的固定 Gaussian 活动概率对照

用户随后授权小规模试验。本次沿用 [Cai v2 §III-B2 式(26)–(30)](https://arxiv.org/html/2506.00581v2#S3.SS2.SSS2) 的 Gaussian 活动证据表达，同时区分论文中的学习外信息与 [作者固定提交](https://github.com/chang-cai/score-massive-connectivity/blob/0c75680c966dcb8e46250de146f4c27e9294c283/main_stmp_jadce.py#L212-L229) 实际调用的 lambda_post_gaussian。公开代码第214–215行设置外信息均值为零、方差为固定信道功率，得到 logit(rho)+s*||r||²/[v*(v+s)]−D*log(1+s/v)。

“固定 Gaussian 活动近似”直接描述这一实现，不是新方法名称。AFDM 实虚坐标下 D=4096 为复维数，方差 v 为每复系数方差。训练功率、活动先验和0.5门限保持；仅将活动输出或反馈替换为解析式。不得将该对照称为完整 Cai STMP 或论文学习外信息版，也不得把当前联合残差尺度当作活跃条件方差。

公式、数据边界及配对设计见 [试验说明](../../../result/candidates/cai_analytic_activity_20261022/METHOD.md)，实际结果以该目录保存的报告为准。试验保留冻结接收机和权重，不涉及训练。

### 2026年10月22日 冻结分类器与损失反传的区别

参数冻结以及停止指定训练目标向另一网络反传，参照 [Cai §IV-C、式(54)后的说明](https://arxiv.org/html/2506.00581v2#S4.SS3)。原文讨论一阶、二阶 score 网络，不能援引为本项目冻结活动分类器后更稳定的结论。当前活动 BCE 经固定分类器影响条件均值与先前查询的关系，按现有计算图直接应用链式法则；属于项目推导，不另起算法名称。PyTorch 参数冻结、输入梯度和 no-grad 的实现区别参照其官方 Autograd mechanics 文档。候选范围和未验证结论见 [冻结分类器方案](FROZEN_CLASSIFIER_SCORE_ONLY_PLAN_20261022.md)；本轮不启动训练。

### 2026年10月22日 Cai 的信道样本与多噪声训练范围

`channel dataset`、`noise levels` 和 `exponential moving average (EMA)` 沿用 Cai §VI-A1–2、正式版印刷 p.3585；多噪声 denoising score matching 目标依据 §IV-B 式(47)–(49)。单用户信道样本、多用户接收场景及接收 SNR 分别按实际生成过程说明，不将原文 41 个去噪噪声水平改称 41 个展开训练工况。Cai §IV-C 式(54)后的梯度安排见正式版 p.3583，仍不构成本项目冻结活动分类器的稳定性证明。当前提出的接收 SNR 连续抽样属于本项目实验设计。数值设置、公开配置与论文的差异，以及已中断试跑的状态，见 [训练与场景核查](CAI_TRAINING_SCENARIOS_20261022.md)。

### 2026年10月22日 Wei 的逐层加深与共同训练

`trained progressively layer by layer`、`each new layer trained jointly with the preceding layers`、`auxiliary supervision` 采用 [Wei、Yuan v1](https://arxiv.org/pdf/2610.17785v1#page=3) §III-D、PDF p.3 的原义。§V-A、p.4 报告五层、独立 score 网络及损失权重 0.2/1。当前深度内共同更新与跨训练阶段逐步增加深度需区分；原文未要求前层永久冻结，也未给出本项目“一轮新层适配加两轮共同训练”的具体安排。现有十层权重的训练历史与仅一阶候选的差别见 [训练顺序核查](FROZEN_CLASSIFIER_SCORE_ONLY_PLAN_20261022.md)。

本次重新训练采用上述顺序，保留前层共同更新，但固定原 STMP 分类器及校准标量；这一参数范围和活跃条件信道损失是项目选择，不能称为 Wei 全部训练方案的复现。原文 §V 未交代 M=32/64、随机 DFT/PMI 各曲线的权重是否共享，不能将其消息模型假设失配结论改写为跨工况训练测试的泛化保证。具体来源与范围见 [重新训练协议](SCORE_ONLY_PROGRESSIVE_20261022.md)。

### 2026年10月22日 不同工况下的消息误差诊断

IID、零均值 Gaussian、与信号独立以及 decorrelated 的适用范围，沿用 [Ma–Ping OAMP](https://arxiv.org/pdf/1602.06509v3#page=4) §III-E Assumptions 1–2、§III-F Proposition 1、PDF p.4–5；不将不相关写成独立。二阶矩非对角部分占比、标准化四阶矩、实测 MSE 与方差标签之比均直接给出计算公式，不包装为文献命名的新方法。Gaussian 替换和真值误差方差只用于诊断，不能称为部署算法或独立识别某项误差结构的因果证据。设计和统计边界见 [消息误差诊断](MESSAGE_AWGN_CONDITIONS_20261022.md)。

后续训练使用同一文献含义的逐层共同训练及辅助监督。用户撤回 30 种 K/Q 混合方案，固定 K=40、Q=16、活动概率 0.1，增加到 3000 个独立物理场景；这属于同一系统配置内的样本多样性，不能改称已验证的跨工况泛化。冻结分类器、固定校准标量和仅活跃条件信道损失仍是本项目选择，见 [当前训练协议](SCORE_ONLY_FOCUSED_PROGRESSIVE_20261022.md)。


### 2026年10月22日 连续相位更新时的停止判断

本候选沿用本文已有的 Gaussian 消息、外信息及活动混合矩术语：Cai §III-B 式(25)–(42)，相位的条件矩及固定消息目标见本表已有 GPML §2.1.1 式(2.6)–(2.8)、Shen §III-C 式(48)–(53)记录。本次只使用“相对变化”“活动概率变化”“停止条件”等直接描述数值操作的表述，不另造方法名称。

每10轮比较一次活动加权信道、当前相位算子下的预测观测及输入/反馈协方差，连续两次满足阈值后停止，是本项目定义的数值规则。0.005、0.001及两个周期不是上述论文给出的配置；不能称为其收敛定理，也不能把输出稳定等同于估计准确。具体公式、阈值及数据边界见 [候选说明](../../../result/candidates/stmp_phase_stopping_20261022/METHOD.md)。

### 2026年10月23日 STMP相位更新后的消息状态核对

Gaussian条件矩沿用 [GPML §2.1.1，式(2.6)–(2.8)，印刷p.9](https://gaussianprocess.org/gpml/chapters/RW2.pdf)；期望二次型依据 [Shen §III-C，式(48)–(53)](https://arxiv.org/html/2412.20806v1#S3.SS3)。generalized EM（广义EM）的固定模型下降性质核对 [Dempster、Laird、Rubin，§3，印刷p.7，式(3.5)、Theorem 1及式(3.7)–(3.10)](https://web.mit.edu/6.435/www/Dempster77.pdf)。2026-10-23重新核对上述原文；该EM扫描件包含一页封面，文件第8页对应印刷p.7。

“只更新相位斜率”“只旋转反馈均值”“重新计算线性查询”均直接描述本项目的操作，不是新方法名称。首帧相位固定为1、常数相位吸收入信道以及中心化参数换算见 [候选推导](../../../result/candidates/stmp_phase_integration_20261023/DERIVATION.md)。旧记录中缓存均值一并旋转是当时的实现选择，不能解释成该物理模型必需的坐标变换；真实观测预测保持不变还要求算子做反向变换。当前正在分别验证斜率约束与反馈消息更新后的缓存处理，不将单个高斯目标下降推广为全套神经迭代收敛。

实测查询误差与方差标签之比按 \(\|r-H/s\|_F^2/(D v)\) 逐用户计算，真值只用于更新结束后的诊断，不进入接收机；比值接近1也不证明误差独立或服从Gaussian分布。


### 2026年10月23日 按有限功率处的边缘似然比较相位初值

沿用 GPML §2.2式(2.30)、印刷p.19的 log marginal likelihood，以及[第5章§5.4式(5.9)、印刷p.114](https://gaussianprocess.org/gpml/chapters/RW5.pdf)的 covariance derivatives。2026-10-23再次核对原文PDF第10页（零基索引9）。复数Gaussian形式、逐用户非负协方差强度及三角多项式由项目直接列式。零功率处负方向导数最大与非零功率处负对数似然最小不是同一个优化问题。当前候选比较正方向导数驻点对应的实际似然起点，保留原点并做原局部优化；这些是操作描述，不另命名为已有方法，也不宣称全局最优。所用正功率尺度不是观测似然的完整二阶导数。真值纠正初始相位的分支仅是oracle诊断，不进入算法性能或采用条件。见[公式、全部分支和验证边界](../../../result/candidates/stmp_phase_initial_candidates_20261023/METHOD.md)。


### 2026年10月23日 条件迭代稳定窗口与相位更新时机

“条件迭代的稳定窗口”“每20轮检查输出变化”直接描述数值判据，不包装为已有具名算法。固定Gaussian消息的条件矩和广义EM边缘目标下降仅沿用前述GPML与Dempster定位；其定理不证明当前神经条件迭代、首次更新时间或整体停止的收敛性质。六分支同输入实验证明一个具体输入的第20轮消息尚未稳定，此时更新相位会使结果变差；候选用既有窗口决定更新时机，整体停止同时检查条件迭代与跨检查区间的物理输出变化。数学断言与经验流程明确区分，见[说明与全部对照](../../../result/candidates/stmp_phase_settled_20261023/METHOD.md)。

### 2026年10月23日 EC归一化诊断与逐用户相位候选

Expectation Consistent（EC，期望一致）近似采用 [Opper、Winther 2005](https://www.jmlr.org/papers/volume6/opper05a/opper05a.pdf) §3，印刷p.2182式(13)–(18)、p.2183式(19)–(20)。三个归一化量组合与矩匹配来自这些公式；§3及§3.1指出驻点可能为鞍点，近似量也不是一般的真实自由能界。[Fletcher、Schniter v4](https://arxiv.org/html/1602.08207) §III式(22)–(29)、Theorem 1讨论EM-VAMP固定点；§IV开头明确不保证迭代收敛。2026-10-23重新核对原文。本项目分别训练的矩网络与活动分类器未证明对应同一精确先验，不能套用其固定点或收敛结论。实际六分支诊断的EC形式排序失败，未用于相位接受或停止，见[复算报告](../../../result/candidates/stmp_phase_evidence_diagnostic_20261023/REPORT.md)。

“固定其他用户高斯消息”“检查全部用户的相位候选”“局部活动证据增加量”是操作说明，不是文献中的新方法名称。条件高斯均值、迹投影的外信息查询、活动混合归一化因子分别沿用前述GPML、Cai定位；将这些操作用于相位驻点候选并按局部分类器证据排序，是本项目待验证设计，不称为完整观测似然或广义EM步骤。公式、标量近似、选择规则及验证边界见[候选设计](../../../result/candidates/stmp_phase_hypotheses_20261023/METHOD.md)。原普通相位细化与此活动候选步骤分别记录，不能把前者的固定消息下降性质赋予后者。

后续[独立候选](../../../result/candidates/stmp_phase_supported_hypotheses_20261023/METHOD.md)要求新相位对应的局部查询达到已有0.5活动判决门限，且沿用0.001概率变化容差；全部用户仍生成候选，当前活动判决不用于提前筛除用户。这里只描述基于训练分类器的候选资格规则，不把搜索后的局部概率称为精确联合后验，也不声称是文献中的联合最大后验方法。跨周期比较改为仅记录具备实际更新条件的边界，并在候选替换后保留普通相位细化；这些是本项目的执行与停止规则，不新增收敛定理或方法名称。


### 2026年10月23日 相位初始化的GPU执行

相位初始化仍沿用本表 GPML §2.2式(2.30)、§5.4式(5.9)及既有连续非负功率、相位梯度定义。
用Z=C^-1 Y把C^-1 S C^-1写成ZZ^H/M是矩阵乘法的重组，不作协方差低秩截断，不另命名算法。
GPU、双精度和CUDA Graph仅描述实现；接口依据为PyTorch 2.7 `torch.linalg.cholesky_ex` 与 CUDA semantics
的 CUDA Graphs/Constraints，原文链接、精度检查及不同浮点路径的边界见
[实现说明](../../../result/candidates/stmp_initialization_runtime_20261023/METHOD.md)。

### 2026年10月23日 活动门限的统计量和条件依赖

`threshold factor` 沿用 [Zhou，PDF p.10，§IV-C 式(27)及脚注3](https://arxiv.org/pdf/2201.02084v2#page=10)：固定相对系数不等于固定绝对能量门限。`fixed threshold setting` 和 `dynamic threshold setting` 对应 [Quayum 等，ICC 2018，PDF p.4，§IV-A 式(9)、Fig.5](https://personal.utdallas.edu/~hxm025000/GrantFreePilots_ICC2018.pdf#page=4)，仅在其导频检测模型下解释，不能将任意 SNR 分档拟合称为该论文方法。

`threshold-based detector` 与有效方差的解析依赖，依据 [Liu–Yu，PDF p.6，§III-E Definition 1、式(30)](https://arxiv.org/pdf/1706.06438v2#page=6)。τ_t² 为 AMP 有效误差方差，不能偷换成物理噪声方差。用户活动 `posterior probability` 依据 [Cai，§III-B2 式(29)–(31)](https://arxiv.org/html/2506.00581v2#S3.SS2)，与归一化用户能量分数有本质区别。相等错误代价下的 0.5 判决是条件风险比较的直接推导，不等于声称 Cai 公布了该数值，也不保证条件漏检率等于虚警率。

“各方法一个跨 SNR 固定值”“估计 SNR 最近节点查表”“测试集逐点选最优门限”均直接描述实现或评估操作，不包装成已有命名算法。原文定位、适用条件及当前实验建议见 [门限核查](BASELINE_ACTIVITY_READOUT.md)。

### 2026年10月24日 用户活动判决与检测目标

`log-likelihood ratio (LLR)` 与用户 Bernoulli 活动消息依据 [Zhang 等，IoTJ 2020作者稿](https://arxiv.org/html/2005.09826)，§III-A2–A3式(15)–(19)，PDF pp.6–7；原文最终证据含活动先验，比较零。等错误代价下用户后验比较0.5、未含先验的似然比比较(1-rho)/rho，是条件风险与Bayes公式的直接推导，不将任意路径概率聚合称作用户后验。

`Neyman–Pearson` 检测与门限设计的GFRA例子为 [Zhao–El-Hajjar–Yang，OJVT 2025](https://eprints.soton.ac.uk/505524/)，*Joint User Activity Detection and Channel Estimation in MC-GFMA Systems by Block Sparse Bayesian Learning With Threshold Optimization*，§V-B式(24)–(31)。本次通过机构记录及检索返回的原文段落核读，整份PDF下载不可用。固定虚警约束与最小总体AER目标不同；该文Gamma拟合不构成当前AFDM估计能量的分布保证。

CG-AD、BI-AD仍采用本表已有Ke出处，补充§III-B及§V Fig.6/8：空间域与角域的检测优劣可能反转，不能将空间域90%投票套用到每用户仅少数非零路径的字典。物理噪声归一化能量仅描述项目待验证统计量，不自动称为恒虚警率检测。原文、实现对应及不重推断可验证的范围见 [活动检测核查](ACTIVITY_DETECTOR_REVIEW_20261024.md)。

### 2026年10月24日 STMP低SNR的冻结查询诊断

AWGN 查询模型沿用 [Cai 等，§III-B1 式(20)](https://arxiv.org/html/2506.00581v2#S3.SS2.SSS1)；同文 §V-B1 明确区分大系统、右旋转不变随机测量矩阵的依据与有限维、特定测量矩阵的实际情况，不能把工作模型当作有限 AFDM 查询的分布保证。活动加权均值沿用其 §III-B3 式(35)，本项目实际输出及反馈按 `src/algorithm/STMP/denoiser.py` 和 `iterations.py` 的代码关系核对。2026-10-24 已核读上述原文。

本次直接计算逐用户实测误差功率 `mean(abs(r-x)**2)`、沿真值信道的实投影系数 `Re(sum(conj(x)*r))/sum(abs(x)**2)` 以及误差空间二阶矩的非对角平方和占比，不将这些量命名为新方法。`x` 为按冻结尺度归一化的有效信道；实投影系数不是已识别的系统增益。以实测误差功率替换方差标签会同时重算一阶条件均值与活动输出，不等于单独改变分类器的方差特征；单次误差功率也不等于已知条件噪声方差。

同误差功率 AWGN 替换仅为合成诊断，方差按期望匹配，不对每次噪声样本强制归一化。真值只在原接收机完成后用于这些分支，结果不反馈。替换同时改变相关性、信号依赖及噪声实现；对原漏检用户重新抽样还包含结果筛选与均值回归影响，不能据此独立识别反馈导致漏检的因果关系。固定抽样、分支和验证门限见 [计划](../../../result/snr_comparison/data/low_snr_query_check_20261024/PLAN.json)，完成状态及全部结果以该目录记录为准。

### 2026年10月24日 结构化观测下的消息失配文献复核

本次将已有术语按原文版本重新定位，不覆盖历史候选与负结果。综合判断见 [STMP 消息调研](../../STMP/docs/STMP_MESSAGE_AWGN_REVIEW_20261024.md)，详细书目和核验范围见 [来源目录](../../../reference/reviews/stmp_message_awgn_review_20261024)。以下 PDF 页码均从指定作者稿第一页起计数；不能与期刊页码混用。

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

来源版本与完整获取状态以 [论文索引](../../../reference/reviews/stmp_message_awgn_review_20261024/README.md) 为准；下表补充操作定位，不覆盖旧试验。下载后的 [阅读报告](../../STMP/docs/STMP_PAPER_READING_NOTES_20261024.md) 已纠正此前未充分列出完整矩阵 Onsager、完整 FIRE/DD-VAMP、三轮残差融合的历史范围。

| 原词或操作 | 本地原文与定位 | 本项目使用边界 |
|---|---|---|
| gdiag operator；diagonalization subsets；subband error precisions / gdiag 算子；对角化分组；子带误差精度 | [D-GEC](../../../reference/literature/shastri2022_dgec.pdf)，p.13 式(31)后、p.14 式(35)后及 Algorithm 2；pp.15–16 corr+corr 式(38)–(41) | 同组平均 Jacobian 迹、对应精度和线性估计应配套；一般“分组精度”是本项目对操作的改写，MRI 小波分组不是任意 AFDM 分组的依据。将 corr+corr 用于活动分类器是项目建议，非论文已有结果。 |
| Gram–Schmidt model / Gram–Schmidt 模型；matrix gain / 矩阵增益 | [OAMP-MMV](../../../reference/literature/cheng2023_oamp_mmv.pdf)，p.5 式(15)–(18)、p.6 式(31)–(34)；[On OAMP](../../../reference/literature/liu2023_orthogonal_principle.pdf)，pp.7–8 式(27)–(34) | \(\widehat X=X\Theta+Z\) 的增益与误差协方差分开记录；矩阵修正后单位增益归一化与噪声代价是项目代数推导。不能仅将标量导数换矩阵便称完整 OAMP-MMV。 |
| sufficient statistic / 充分统计量及协方差加权 | [SS-MAMP](../../../reference/literature/liu2023_ssmamp.pdf)，p.8 Lemma 11式(40)，pp.10–11 Theorem 1 | Hermitian 约定的 \(w=V^{-1}\mathbf1/(\mathbf1^HV^{-1}\mathbf1)\) 需共同单位增益和可信联合误差模型；不能以当前公开残差 Gram 自动替代 \(V\)。 |
| FIRE posterior estimate；renoising / FIRE 后验估计与再加噪 | [FIRE v4](../../../reference/literature/bendel2025_fire.pdf)，pp.4–6 式(10)–(21)、Theorem 1；PDF Algorithm 1 line 6 | PDF 的半正定保障行号为 6，HTML 显示行号可能不同。原 posterior 的 \(C\) 不等于 STMP trace 归一化 extrinsic 的误差协方差。复数公式是项目转写，不称原文已证明当前复杂信道场景。 |
| density compensation / 密度补偿及低 SNR 实验 | [D-VDAMP](../../../reference/literature/metzler2020_dvdamp.pdf)，p.4 Table 2 及其后实验讨论 | 1/8 采样、5 dB 测量 SNR 时作者方法 PSNR 25.0 dB、PnP-ADMM(BM3D) 27.8 dB，说明其噪声放大代价；这是 MRI 的反例，非 AFDM 检测预测。 |
| learned score-based turbo message passing / 学习式 score turbo 消息传递 | [Wei–Yuan v1](../../../reference/literature/wei_yuan_2026_lstmp_v1.pdf)，pp.2–3 §III-B–D，式(6)、(8)、(11)–(13) | 式(6)要求行正交；式(13)为最终输出，训练损失位于 §III-D 未编号正文。单用户信道 NMSE 训练不等同于 JADCE 活动损失；随机 DFT 行选择不据此认定为 Haar 右酉不变。 |
| universality / 普适性 | [Lovig–Wang–Fan v2](../../../reference/literature/lovig2026_universality.pdf)，pp.1–3 Example 1.1、§1.1 | 已取得全文；本次只读主要问题、反例和条件概要，没有复核全部证明。非可分 Lipschitz 本身不足以保证跨矩阵分布普适，更不覆盖固定 AFDM。 |

“每用户方形满秩块的全块无偏估计退化为块逆”直接来自 \(L_kA_k=I\) 的线性代数，不另命名为一种已有接收机。分组/矩阵的维度含义、条件风险与后验中心协方差的区别、复数实坐标方差因子均应在具体实现前列清。关键 PDF 页面已渲染核对；D-Turbo-CS、DD-VAMP 及 EP 预印本存在需对照推导的公式显示不一致，详见对应阅读笔记，未据此断言作者代码或当前项目出错。

### 2026年10月24日 C 的具体表示与公开输入列基

对应 [C 表示分析](../../STMP/docs/STMP_COVARIANCE_REPRESENTATION_20261024.md)。本轮的张量坐标、Gaussian 工作模型、二阶矩、原文算法和项目候选分开表述。

| 原词或操作 | 原文定位 | 使用边界 |
|---|---|---|
| gdiag；diagonalization subsets；block uniform diagonalization / gdiag、对角化分组、块内统一对角化 | [D-GEC v2](https://arxiv.org/html/2206.05049v2#S3.SS1)，§III-A 式(31)、(33)–(36)、Algorithm 3；[GEC v2](https://arxiv.org/pdf/1602.07795v2)，§II-A 式(6)–(12)、Algorithm 1，PDF pp.2–3 | 固定基、固定组的精度族及组迹有出处；本项目用公开每用户输入基代替 MRI 小波子带，是新适配。一般完整线性后验仍非对角，投影后才返回消息族。 |
| mode；k-mode matricization；separable covariance；Kronecker product / 轴、按第k轴矩阵化、可分协方差、Kronecker积 | [Hoff，arXiv:1008.2169v1](https://arxiv.org/pdf/1008.2169v1)，§2.1–2.2、式(1)、Proposition 2.1，PDF pp.3–5 | 仅引用数学表示；当前复数共轭与C-order由代码确定。三个轴的未中心化Gram不证明协方差可分。固定酉基任意二维谱与单一可分乘积是不同约束。 |
| correlated noise；corr+corr / 相关噪声、corr+corr | [D-GEC v2](https://arxiv.org/html/2206.05049v2#S3.SS2)，§III-B 式(38)–(41)，PDF pp.15–16 | 给定C的独立辅助噪声可作为条件；C在每任务依公开A改变是本项目候选。有限个辅助样本不保证精确识别C，也不证明实际query符合该条件模型。 |
| proper complex random vector；pseudo-covariance / proper复随机向量、伪协方差 | [Neeser–Massey，IEEE TIT 1993，作者机构原文](https://www.isiweb.ee.ethz.ch/papers/arch/fneese-mass-inspec-1993-1.pdf)，§II-A式(3)–(5)、§III-A Definition 1及式(7)–(8)，印刷pp.1294–1295，PDF pp.2–3 | proper指中心化伪协方差为零；协方差C单独不足以描述一般复Gaussian分布。本项目以proper条件噪声训练是工作假设，不是对实际query的已验证结论。 |

\(A_k^HA_k\) 的特征基、每用户输入模式的方差、按天线/输出行重复、以及精度相减后的闭合性，均用公式直接说明，不另起算法名称。小尺寸Gaussian求解、投影后quotient和式(5)的协方差恒等式只证明代数；输入列公开基的效果来自旧测试查询的探索性二阶矩分析，不作为新算法性能或Gaussian性证明。

### 2026年10月24日 C 候选的首轮验证与分组代价

对应 [C 验证报告](../../STMP/docs/STMP_COVARIANCE_VALIDATION_20261024.md)。再次核对 [GEC v2](https://arxiv.org/pdf/1602.07795v2) §II-A/B，式(6)–(12)、Algorithm 1，PDF pp.2–3，以及 [D-GEC v2](https://arxiv.org/html/2206.05049v2#S3.SS1) §III-A Algorithm 2、式(31)、(34)。block uniform diagonalization / 块内统一对角化、diagonalization subsets / 对角化分组、precision / 精度均沿用原义。每用户16模式的选择是项目适配，不是论文已验证的AFDM设计；较粗分组只是下一步建议。

GEC §II-B式(10)的 scaled form 写作 \(\beta=\gamma r\)，依据其精度与自然参数操作解释精确零观测模式的 \(\gamma_{\rm out}=0,\beta_{\rm out}=0\) 极限；不把零精度写成有限方差Gaussian，也不称论文已经讨论当前近奇异样本。首轮 \(r_i=f_i/h_i\)、方差放大不等式、完整用户响应与单模式自身响应的区别均由本项目直接列式推导，不另命名算法。当前SVD判秩全部满秩，近奇异与精确零空间明确区分。

oracle逐模式功率白化、同流程Gaussian参考、实信号方向投影及按场景重抽样均为具体评价操作。拟合误差功率不是中心条件协方差；原始互补二阶矩不是已识别的中心化pseudo-covariance。16份模拟参考的分位范围不是置信区间，探索性场景配对区间不当作完整分布检验或因果证明。正式结果只使用修正到冻结观测噪声估计入口后的首轮数据；首版不匹配记录保留并标记拒绝。

### 2026年10月24日 固定分组、模式响应与可逆缩放

继续使用 [GEC v2](https://arxiv.org/pdf/1602.07795v2) §II-A式(6)–(9)、§II-B Algorithm 1及式(10)–(12)，PDF pp.2–3，和 [D-GEC v2](https://arxiv.org/html/2206.05049v2#S3.SS1) §III-A Algorithm 2、式(31)、(34) 的 block uniform diagonalization / 块内统一对角化与 gdiag。每用户1/2/4/8/16个连续等长组、按公开模式编号对折成4组，都是项目直接描述的分区规则，不另设已有算法名称；等编号平均不等于等实际灵敏度。

首轮 \(r_i=f_i/h_g\) 的自身响应 \(h_i/h_g\)、工作误差方差 \(\nu(1-2h_i/h_g+h_i/h_g^2)\)、组平均等于 \(\tau_g\)，以及逐模式校正后恢复 \(f_i/h_i\)，均是固定系数Gaussian工作模型的直接推导。嵌套分组细化使按维数加权的平均方差不降，需保持同一初始方差、算子及噪声参数；不能对不同闭环或非嵌套分区直接套用。可逆公开缩放在保留其元数据时不改变消息所含信息，不能将query原始MSE比改称信息量或检测性能比。增益与协方差分开记录的文献背景仍为前述OAMP-MMV的Gram–Schmidt模型，其MMV维度和随机矩阵条件不自动等于当前AFDM输入模式分组。详见[独立代数核查](../../../reference/reviews/stmp_message_awgn_review_20261024/notes/covariance_grouping_algebra.md)。

### 2026年10月24日 有色噪声的一阶 score 训练

对应 [训练候选与验证记录](../../C-STMP/docs/COLORED_SCORE_TRAINING_20261024.md)。denoising score matching / 去噪 score matching 沿用 [Cai 等 v2](https://arxiv.org/html/2506.00581v2#S4.SS2) §IV-B式(48)–(49)的原义；Tweedie's formula / Tweedie公式的一般正定协方差形式见 [Dytso–Poor–Shamai v1](https://arxiv.org/pdf/2104.01883v1)，PDF p.1式(1)假设、p.2式(3)。矩阵加权损失、复数实打包的1/2系数、C-order轴乘法是项目的显式展开，见[独立数学核查](../../../reference/reviews/stmp_message_awgn_review_20261024/notes/colored_score_training_algebra.md)。

correlated noise / 相关噪声及 corr+corr 仍依据 [D-GEC v2](https://arxiv.org/html/2206.05049v2#S3.SS2) §III-B式(38)–(41)。原文用独立同协方差辅助噪声训练直接去噪映射；当前候选改为精确协方差因子条件的一阶 score，不宣称逐字复现 corr+corr。给定有限辅助样本时的加权 DSM 条件最优解另行推导，不能称其为原文已证明的结论。

separable covariance / 可分协方差、proper complex / proper复数噪声继续沿用上文 Hoff 与 Neeser–Massey 的原义。这里只令两个因子的 trace/dim=1，称为归一化协方差因子；不把非单位对角的矩阵称为 correlation matrix。低秩正半定矩阵与单位矩阵的凸组合、精确矩阵条件输入都是项目设计选择，不另造算法名，也不称为已识别的实际消息噪声分布。按用户后续要求，四类等比例采样已取消，当前两个因子独立连续抽取；同一条件Gaussian族不意味着边缘上是单个固定协方差Gaussian。

后续[相对近似检查](../../C-STMP/docs/COLORED_COVARIANCE_RELATIVE_CHECK_20261024.md)中的Gaussian负对数密度，直接由proper复Gaussian密度的logdet和二次型展开，每复坐标归一且略去共同常数logπ；不引入实Gaussian的1/2。偶奇输出行拟合与评分、谱尾均值替换和向单位阵收缩均按操作描述，不另命名算法；它们不是独立场景交叉验证、最优联合协方差估计或真实Gaussian性的证明。

### 2026年10月24日 baseline 预算、重构和活动判据复核

对应[预算与判据报告](BASELINE_BUDGET_REVIEW_20261024.md)。`orthogonal projector` / 正交投影算子的原词依据 [Tropp–Gilbert–Strauss，Algorithm 3.1步骤4–5，PDF p.7](https://tropp.caltech.edu/papers/TGS05-Algorithms-Simultaneous-I-preprint.pdf)。对完整80原子物理信道空间计算真值投影及最小平方表示误差，是本项目直接应用该线性代数操作；使用真值，不能当作可实现接收机结果或AER下界。

`V-fold CV` / V折交叉验证依据 [Arlot–Celisse，arXiv:0907.4728v1，§4.3.2](https://arxiv.org/html/0907.4728v1)，数据分成近等大的V份，轮流留出。按物理场景ID对5取模、同一场景全部SNR留在同一折，是本项目分组规则，不声称论文已证明此AFDM实验的独立性或方差估计。校准集内比较不等于独立测试确认；32万用户判断不是32万个独立重复。

`first-order Taylor expansion` / 一阶Taylor展开沿用 [Wei 等，arXiv:2101.05629v1，§III-B式(17)–(24)](https://arxiv.org/html/2101.05629v1)。同文§II式(3)后及§VI-A式(76)将估计参数用于有效信道重构，因此不能把本项目一阶拟合后使用精确路径算子直接定性为原论文公式错误。固定参数改用一阶信道输出，是本项目的诊断候选；16场景NMSE改善不证明AER改善或原论文严格复现。

相对能量门限继续沿用 [Zhou 等，§IV-C式(27)](https://arxiv.org/html/2201.02084v2#S4.SS3)。绝对能量、除以估计物理噪声方差的能量均按操作描述，不自动称为活动后验或恒虚警率检测。GAMP绝对能量的小幅改善与Off-grid噪声归一化的高SNR回升，均仅按本轮校准集内五折计数报告。


### 2026年10月24日 有色噪声网络结构与参数化核查

对应[结构调研与权重诊断](../../C-STMP/docs/COLORED_SCORE_ARCHITECTURE_REVIEW_20261024.md)。以下原词按所列论文原义使用；不将本项目适配包装为已有方法。

| 原文术语 / 中文表述 | 核对位置 | 本项目使用边界 |
|---|---|---|
| preconditioning / 预条件处理；skip connection / 跳连 | [Karras等EDM v2](https://arxiv.org/pdf/2206.00364v2)，PDF p.8 §5式(7)–(8)，p.3 Table 1，pp.28–29 Appendix B.6式(114)–(144) | 原文为标量各向同性噪声的输入、跳连和输出系数。一般SPD矩阵函数用于本项目是显式推广，不称为EDM已经验证的AFDM实现。 |
| matrix-form EDM / 矩阵形式EDM | [Ding等iCCDM v1](https://arxiv.org/pdf/2602.02114v1)，PDF p.5 §III-D2式(19)–(20)、§III-D3式(22)后 | 2026预印本；作者代码与实验采用对角噪声协方差。本项目使用任意旋转的Ra/Rc需另行验证；条件编码及损失权重不能机械照搬。 |
| noise level map / 噪声强度图 | [FFDNet v2](https://arxiv.org/html/1710.04026v2#S3.SS2)，§III-B，PDF p.4 | 原文允许多通道退化图，官方另有6参数RGB协方差版本；不等于任意高维复协方差已有现成实现。 |
| DRUNet；residual block / DRUNet、残差块 | [DPIR v2](https://arxiv.org/pdf/2008.13751v2)，Fig.1、§3.1–3.2，PDF pp.3–4 | 残差U-Net加标量噪声图，论文使用L1；作为条件均值/score候选需明确改用匹配的平方目标。 |
| Multi-Dconv Head Transposed Attention (MDTA) / 多头深度卷积转置注意力 | [Restormer](https://openaccess.thecvf.com/content/CVPR2022/papers/Zamir_Restormer_Efficient_Transformer_for_High-Resolution_Image_Restoration_CVPR_2022_paper.pdf)，§3.1，PDF pp.3–4 | 原词照录；其注意力在通道维计算。只用于说明候选主干，未将图像结果外推为AFDM收益。 |
| SimpleGate；Simplified Channel Attention (SCA) / SimpleGate、简化通道注意力 | [NAFNet](https://www.ecva.net/papers/eccv_2022/papers_ECCV/papers/136670017.pdf)，§4，PDF pp.7–9，式(4)、(6) | 原文模块名称；本次仅比较架构设计，未移植到项目。 |

corr+corr及子带标准差接口沿用上文D-GEC §III-B式(38)–(41)与D-VDAMP §2.3 PDF p.3的记录。条件均值、score转换和矩阵加权DSM继续沿用Tweedie公式与已有核查，不新造缩写。另核对[Zilberstein等v1](https://arxiv.org/pdf/2605.15487v1)，PDF p.3 §3.1式(7)–(8)、p.4 §3.2式(9)，但未采用其能量网络或协方差导数目标。

“224维协方差族经过64维条件压缩”、同输入条件置换、单位代理先验的线性估计、K/B/O矩阵函数及其损失恒等式，都是本项目直接描述和推导；不称为文献已经验证的性能结论。64场景CPU诊断为已有开发集上的机制检查，非1000场景正式比较。阅读范围、作者代码commit、原文与实现差异均记录于[调研资料目录](../../../reference/reviews/colored_architecture_review_20261024/README.md)。

### 2026年10月25日 冻结一阶网络后学习二阶统计量的文献核对

本次为针对具体主张的原文核验，阅读范围为下表所列章节，不代表系统综述。Semantic Scholar 元数据查询返回 HTTP 429；作者、题名、年份与论证位置改由 arXiv 原文及会议官方论文集核对。

| 原文术语 / 中文表述 | 核对位置 | 本项目使用边界 |
|---|---|---|
| second-order score matching / 二阶得分匹配；trace / 迹 | [Cai 等，STMP-JADCE，arXiv:2506.00581v2，2026](https://arxiv.org/html/2506.00581v2#S4.SS3)，§IV-C式(50)–(54)，特别是式(53)前及式(54)后段落 | 原文明确允许先训练一阶网络，再冻结它训练二阶网络；消息方差只需二阶 score 的迹。支持冻结新一阶后重新学习配套二阶统计量，但不证明共享小型输出分支在本项目已经足够，也不证明有色查询闭环性能。有限一阶误差下的条件风险与精确后验协方差仍按已有记录区分。 |
| second-order score；diagonal；low-rank matrices / 二阶 score、对角、低秩矩阵 | [Meng–Song–Li–Ermon，Estimating High Order Gradients of the Data Distribution by Denoising，NeurIPS 2021](https://proceedings.neurips.cc/paper/2021/file/d582ac40970f9885836a61d7b2c662e4-Paper.pdf)，§1，§3.2，§4.1式(13)–(17)，§4.2–4.4，§5式(18) | 给出通过去噪监督学习高阶 score 的方法，比较直接学习与一阶网络自动微分，讨论对角与低秩输出。其实验采用一、二阶联合训练，不能写成已验证本项目冻结训练方案。完整二阶矩阵的加速结果不能直接外推给当前单探针有限差分迹估计。 |
| heteroscedastic regression；shared representation learner；covariance parameter head；stop gradient / 异方差回归、共享表征网络、协方差输出分支、停止梯度 | [Stirn 等，Faithful Heteroscedastic Regression with Neural Networks，AISTATS 2023](https://proceedings.mlr.press/v206/stirn23a/stirn23a.pdf)，§2，PDF pp.3–4，Figure 1、Proposal 1–2、式(5) | 原文给出共享主干、均值和协方差两个输出分支，并举单层 softplus 对角协方差输出例子；阻止协方差梯度更新共享主干，同时使均值按平方误差目标更新。支持轻量方差分支与保护均值训练的设计依据；并非二阶 score 或 JADCE 研究。冻结已训练主干及均值是本项目候选适配，非原文主要联合训练流程。 |

当前建议仅为：保留已训练一阶去噪器，用新的监督目标学习其配套方差，并比较独立网络和复用一阶特征的小型分支。直接拟合有限去噪器的条件平方误差时，学习对象应称条件误差风险；只有明确 score 定义、Gaussian 观测条件及相应恒等式后，才能解释为二阶 score 的相关读出。上述文献不保证该候选在 C-STMP 中优于现有导数估计，尚需方差校准、运行时间和接收机闭环比较。

2026-10-25 用户选择独立二阶网络并授权开始训练。实现继续沿用 Cai §IV-C式(50)–(54) 的 second-order score matching / 二阶得分匹配；归一化的协方差加权迹 \(u=\operatorname{tr}(\Sigma S_2\Sigma)/\operatorname{tr}\Sigma\) 及其监督目标为本项目明确推广，见 [C-STMP 推导第8节](../../C-STMP/docs/C_STMP_DERIVATION_20261024.md)。只监督该标量迹，不声称输出图的每个像素是已学习的 Hessian 对角元；有限冻结一阶下仍按条件风险解释其方差读出。输入预条件、独立原二阶 RefineNet 初始化及 C 条件均为实现选择，不另造算法名称；当前未采用 Stirn 的共享方差分支。

### 2026年10月25日 负方差与截断的原文/作者实现核对

| 原文术语 / 中文表述 | 核对位置 | 本项目使用边界 |
|---|---|---|
| clipping / 截断 | [Sippel–Fischer，Stabilization Techniques for Iterative Algorithms in Compressed Sensing，arXiv:2109.14917v1，2021](https://arxiv.org/pdf/2109.14917)，§IV-C，PDF p.3；§V-C，PDF p.4 | 原文显式对精度作区间截断：一类精度限制到[10^-8,10^8]，其他精度到[10^-12,10^12]。这是VAMP稳定化先例，不能把其精度边界直接当成本项目后验方差阈值，也不据此声称截断保证收敛或统计校准。 |
| posterior variance / 后验方差；代码中的下界操作 | [Cai等作者固定提交0c75680c966dcb8e46250de146f4c27e9294c283](https://github.com/chang-cai/score-massive-connectivity/blob/0c75680c966dcb8e46250de146f4c27e9294c283/main_stmp_jadce.py)，`module_B` 的二阶score读出及其后的 `v_H_B_post[v_H_B_post < 1e-4] = 1e-4` | 作者先合并实虚方差、跨用户及子载波平均，保留天线维，再设10^-4下界。此证据来自作者代码，不能写成论文正文明确给出的阈值。本项目当前`STMP/denoiser.py`第119–120行先对用户原始标量读出平均，再在checkpoint归一化坐标下设10^-4下界；不是逐用户先截断再平均。 |

后验方差/条件平方误差必须非负，而二阶score本身可以为负；截断应作用于方差读出，不能要求Hessian逐项非负。当前外信息精度`1/tau - 1/v`若不为正，接收机保留旧site，这与负后验方差的下界操作是两个步骤。仅为方差设正下界不保证其小于输入方差，后者也不是一般非Gaussian先验下逐点成立的后验性质。截断避免非法数值，不校正整体低估；验证继续保留原始输出、触发比例和截断后读出。此次仅核查与记录，未修改训练损失、网络权重或接收机。

2026-10-25 高SNR排查沿用 damping / 阻尼及 Gaussian extrinsic information / Gaussian外信息，原文依据仍为上文 Cai v2 §III-A–B、§V-B1式(57)–(58)。代码中的β是新消息权重；β从0.4降为0.2是增加阻尼。固定v、τ对外信息均值求导得到的式(17)为本项目直接代数展开，见[C-STMP推导第10节](../../C-STMP/docs/C_STMP_DERIVATION_20261024.md)，不是新的文献算法或完整稳定性证明。数值导数估计与有限去噪器条件误差风险的区别仍采用Dytso §IV及前述二阶监督的原义。相邻更新余弦、输入误差与报告方差比均按具体计算描述，不另造术语。

### 2026年10月25日 导数方差的完整推导与原文定位

对应 [C-STMP推导第12节](../../C-STMP/docs/C_STMP_DERIVATION_20261024.md)。本次核对的是所列公式及其适用范围，不是新增系统综述。

| 原文术语 / 中文表述 | 核对位置 | 本项目使用边界 |
|---|---|---|
| Jacobian；conditional mean estimator；conditional covariance / Jacobian、条件均值估计器、条件协方差 | [Dytso–Poor–Shamai，arXiv:2104.01883v1](https://arxiv.org/pdf/2104.01883v1)，§II式(9)、PDF p.4；§IV Proposition 1式(22)、PDF p.5；Corollary 1式(23)、PDF p.6 | 原文 Jacobian 用输入坐标为行，本项目用输出坐标为行，因此对应式为 J_m=PΣ^-1、P=J_mΣ。仅在固定协方差的 Gaussian 观测条件下为精确恒等式；有限条件均值网络的导数读出只能作为方差近似。实/复转换和每复元素归一化是项目显式推导。 |
| divergence；Monte Carlo method / 散度、Monte Carlo方法 | [Metzler–Maleki–Baraniuk，From Denoising to Compressed Sensing，arXiv:1406.4175v2](https://arxiv.org/html/1406.4175v2)，§V-B式(21) | 原文用 Gaussian 方向和单侧有限差分估计散度。本项目用独立随机符号、协方差平方根缩放及中央差分，依据 E[zzᵀ]=I 明确推导；一个方向需要额外两次均值前向，与原文单侧差分的额外一次不同。固定方向跨迭代复用，不宣称闭环轨迹无偏。 |
| Tweedie’s formula；posterior mean / covariance；second-order score / Tweedie公式、后验均值/协方差、二阶score | [Cai等，arXiv:2506.00581v2](https://arxiv.org/html/2506.00581v2)，§IV-A式(43)–(45)；§III-B3式(35)–(36) | 精确均值的 Jacobian 读出与二阶score协方差读出等价。有限网络下，导数迹与冻结均值后监督平方误差得到的条件风险不必相同。活动条件方差与 Bernoulli 混合后方差分开书写；分类器仍是本项目学习接口。 |

“协方差缩放的随机符号中央差分”“由条件均值导数得到的方差近似”直接描述计算操作，不另造文献算法名。C-STMP继续作为用户指定的项目候选名称。推导覆盖一般C，但本轮实际接收机接口仍为C=vI；不能据此宣称已经实现完整D-GEC或一般有色矩阵消息传递。

2026-10-25 严谨性比较补充： [Meng等，NeurIPS 2021](https://proceedings.neurips.cc/paper/2021/file/d582ac40970f9885836a61d7b2c662e4-Paper.pdf) §1、PDF pp.1–2的 estimation error / 估计误差讨论明确区分一阶训练损失与高阶导数误差；§4.4、PDF p.6比较直接学习与自动微分。本文据此明确：小的一阶去噪误差不自动保证小的 Jacobian 迹误差。[Cai v2](https://arxiv.org/html/2506.00581v2) §IV-C式(52)后讨论一阶替换误差，式(53)直接监督二阶迹；§V-B1式(57)–(58)前明确大系统与 right-rotationally invariant / 右旋转不变随机矩阵的 AWGN 查询条件及有限维失配。以上均不提供当前有限 AFDM、学习分类器及阻尼接收机的无条件收敛保证。项目的误差分解与数学反例见[C-STMP推导第12.5节](../../C-STMP/docs/C_STMP_DERIVATION_20261024.md)，不把项目代数结论冒充原论文定理。

### 2026年10月25日 预训练一阶网络导数协方差的应用先例

| 原文术语 / 中文表述 | 核对位置 | 本项目使用边界 |
|---|---|---|
| posterior covariance；posterior principal components；Jacobian-vector product / 后验协方差、后验主成分、Jacobian–向量乘积 | [Manor–Michaeli，ICLR 2024，arXiv v2](https://arxiv.org/html/2309.13598v2)，§3.2 Theorem 2式(10)–(11)，§4.1式(15)、Algorithm 1，Appendix H；会议信息见[作者页](https://hilamanor.github.io/GaussianDenoisingPosterior/) | 对预训练去噪器作单侧前向差分计算后验协方差主成分，无需另训二阶网络。支持使用已有均值映射的导数提取二阶信息；本项目随机符号中央差分迹不是其原Algorithm 1。 |
| Tweedie Moment Projected Diffusions (TMPD)；diagonal Tweedie Moment Projection (DTMPD)；vector-Jacobian product / 沿用论文名称及缩写、向量–Jacobian乘积 | [Boys等，TMLR 2024，arXiv v3](https://arxiv.org/html/2310.06721v3)，§3.1 Proposition 1式(5)–(6)，§3.2–3.4，Appendix E.1 | 用预训练一阶score得到均值及导数协方差，进入逆问题条件采样。其图像计算进一步使用Jacobian行和近似对角；该近似与本项目随机迹估计不同，不引入其采样理论作为AFDM闭环保证。 |
| precision；divergence；gdiag / 精度、散度、gdiag算子 | [Shastri等D-GEC，arXiv v2](https://arxiv.org/pdf/2206.05049v2)，Algorithm 1 line 10、PDF p.8；§III-A式(31)、(33)、Algorithms 2–3、PDF pp.13–14 | 标量精度满足η=γN/tr(J_f)，分组扩展采用Monte Carlo差分。作为去噪导数参与消息精度更新的先例，不能把任意DNN读出解释为已证明准确的后验协方差。 |

具体引用分工和与C-STMP的对应见[推导第12.6节](../../C-STMP/docs/C_STMP_DERIVATION_20261024.md)。本次只核查列出的原文章节，未宣称全文阅读或新增接收实验。

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

沿用 Cai v2 §III-B2 的 **Denoiser of α_k / 活动变量去噪器**、式(28)–(30)的 Gaussian 消息积分，以及 §III-B3 式(35)–(36)的活动加权均值和方差。`C-STMP (analytic activity)` 只是项目候选的描述性标签，不是论文既有算法名称。本候选将当前标量方差消息代入原积分，N=4096 是复坐标数，保留 Gaussian 归一化项。与论文逐天线方差和学习二阶网络不同，当前沿用共享标量导数方差；不表述为 Cai 算法的完整复现。详细公式、数值核对和诊断范围见 [解析活动概率说明](../../C-STMP/docs/C_STMP_ANALYTIC_ACTIVITY_20261025.md)。

### 2026年10月25日 查询统计逐模块诊断

沿用 [Cai v2](https://arxiv.org/html/2506.00581v2#S3.SS2.SSS1) §III-B1 式(20)–(23)的 AWGN observation / AWGN 观测、posterior mean / 后验均值、posterior variance / 后验方差；式(20)前文字说明其 Gaussian 解释依赖大系统状态演化，不能改写为任意有限算子的保证。数值 Jacobian 核对沿用此前 Dytso、Meng 的已记录原义。本项目的 `R−H=(WA−I)(H−P)+Wn` 为对实际线性更新的直接代数展开，不新造方法名。实测协方差特征值比与矩阵归一化内积按公式描述；代码字段 `(tr C)^2/tr(C²)` 不直接命名为文献中的 effective rank。见[推导与适用边界](../../C-STMP/docs/C_STMP_COMPONENT_DIAGNOSTIC_20261025.md)。


### 2026年10月25日 查询噪声功率修正候选

继续使用上述 Cai v2 §III-B1 式(20)–(23)的 AWGN observation，以及 §III-B3 式(35)–(36)的活动混合均值和方差。对当前查询各用户平均能量取中位数，以及在原迭代结束后重新计算一次共同条件下的输出，是本项目明确提出的近似操作，不对应上述论文已有算法名称，也不将其称为完整 D-GEC。中位数估计不声明无偏；最终重算不声明在新条件下达到消息固定点。严格逐用户线性关系及推导见 [修正说明](../../C-STMP/docs/C_STMP_QUERY_POWER_REPAIR_20261025.md)。

### 2026年10月25日 每用户输入列协方差消息

| 使用的术语或表述 | 原文依据及位置 | 本项目边界 |
|---|---|---|
| MMSE estimation / MMSE估计；covariance / 协方差；precision / 精度 | Fletcher等，*Expectation Consistent Approximate Inference: Generalizations and Convergence*, [arXiv:1602.07795v2](https://arxiv.org/html/1602.07795v2)，§II-A式(4)–(5)，§II-B式(10)–(12) | 沿用后验均值、精度及缩放均值消息、Jacobian与后验协方差的关系；复数自然参数的2倍因子另由本项目推导和数值核对。 |
| vector-valued diagonalization / 向量对角化；block uniform diagonalization / 分块均匀对角化 | 同文§II-A式(6)–(9) | 原文返回对角或分块平均量，不是本项目保留每用户完整16×16列协方差的直接实现；不借用其收敛结论。 |
| correlated noise / 相关噪声；D-GEC | Shastri等，[arXiv:2206.05049v2](https://arxiv.org/html/2206.05049v2)，§III-A式(31)、Algorithm 3、式(36)后文字；§III-B式(38)–(41) | 只用来支持统计条件与去噪训练相匹配的思路；其误差Gaussian性仍有研究边界。当前精度参数及(z,J)输入不是原文corr+corr。 |

`ColumnLinear`、`C_STMP_column_messages`仅为本项目代码路径，不宣称新的既有算法名称。Λ=A_k^H S_{-k}^{-1}A_k、η=A_k^H S_{-k}^{-1}y_{-k}及J=(I+Λ)^{-1}Λ、z=(I+Λ)^{-1}η是明确给定独立Gaussian输入消息后的直接代数操作。详见[推导及数值验证](../../C-STMP/docs/C_STMP_COLUMN_MESSAGES_20261025.md)。

2026年10月25日复用旧权重补充：`C_STMP_reuse_20261025`仍为项目代码路径。对旧一阶使用v=tr(C)/16、Ra=I、Rc=C/v只是原协方差表示的特例；输入/输出预条件继续沿用上述EDM来源与本项目明确的矩阵推广。对旧分类器，把标量归一化和能量改为同一C下的矩阵函数及二次型，是本项目未经重训的特征推广，不称为D-GEC、Cai或其他论文已经提出的活动检测器，也不由白噪声退化一致性推出一般C下的密度比校准。见[实现与边界，第9节](../../C-STMP/docs/C_STMP_COLUMN_MESSAGES_20261025.md#9-复用已训练权重的接口评估不重训)。

### 2026年10月25日 当前标量 C-STMP 的查询方差更新候选

- **EM Update of the Gaussian Noise Variance / Gaussian 噪声方差的 EM 更新**：Vila–Schniter, *Expectation-Maximization Gaussian-Mixture Approximate Message Passing*, IEEE TSP 2013，[作者公开原文](https://phil-schniter.web.app/pdf/tsp13_emgm.pdf)，§III-A 式(22)–(27)，印刷 p.4661。原文使用后验残差平方加后验方差更新物理噪声；本项目将相同的条件期望恒等式用于近似查询模型 r=H+e，复坐标下 v_target=mean(|r−E[H]|²)+mean(tr Cov[H])/M。活动混合项 p(1−p)μμᴴ 必须保留。查询方差不是物理观测噪声方差。
- **variance auto-tuning / 方差自动调整**：Fletcher等，*Rigorous Dynamics and Consistent Estimation in Arbitrarily Conditioned Linear Systems*, NIPS 2017，[会议原文](https://proceedings.neurips.cc/paper_files/paper/2017/file/4e8412ad48562e3c9934f45c3e144d48-Paper.pdf)，§4（PDF p.7），Definition 1、Theorem 2。这里只支持对消息噪声参数进行估计的思路；论文的右旋转不变、大系统及可辨识性假设不直接适用于本项目有限维网络接收机。

`C_STMP_variance_em_20261025`是独立候选代码路径，不另立算法名称。每轮使用 v_t=a_t v_linear,t；所有一阶均值、固定条件下导数、活动概率及外信息减法共享 v_t。随后 a_{t+1}=(1−β)a_t+β v_target,t/v_linear,t，β沿用0.4；原始线性方差与调整后方差分别保存，避免将已调整的方差再次混入原始线性阻尼历史。停止时还检查 |v_target−v_t|/max(v_target,v_t) 小于原0.0005容差。此为本项目在近似后验下的一步交替更新，不声称精确EM似然单调性或论文的状态演化保证；没有增加网络前向、训练或使用真值。

同日数学核查补充：上述Vila–Schniter §III-A式(22)–(27)的期望对数似然更新，在本项目固定查询r与近似分布q后给出 Q(v)=const−D log(v)−D S/v，S=(||r−E_q g||²+tr Cov_q(g))/D；S>0时唯一最优方差为S。这是对所采用矩的精确代数关系，不把近似q命名为真实后验。比例阻尼只对本轮线性参考方差b_t下的虚拟值 b_t a_{t+1} 保证Q不下降；实际下一轮使用 b_{t+1}a_{t+1}，故不宣称全程EM单调性。

Gaussian外信息自然参数相除对应实现中投影、裁剪后的P_used；不将其等同于未投影真实后验的精确相除，也不据此称为完整EC固定点。[Fletcher–Schniter，Learning and Free Energies for Vector Approximate Message Passing，v4](https://arxiv.org/html/1602.08207v4) §III的固定点刻画与§IV开头的不保证收敛须同时保留，不能移用到当前神经接收机。逐步证明、400份保存结果的数值核查及近似边界见[C-STMP推导第13节](../../C-STMP/docs/C_STMP_DERIVATION_20261024.md#13-当前标量查询方差修正的数学核查2026-10-25)。本补充没有为项目操作另造术语。


### 2026年10月26日 C-STMP 复制组装稿的有色噪声表述

- 稿件目录 `STMP`、`DU`、`C-STMP` 是作者指定的项目标签；旧 `TWC-1` 和 `TWC-2` 分别对应当前 `STMP` 和 `DU`。
- **colored Gaussian noise / 有色高斯噪声；denoising with correlated noise / 相关噪声去噪**：Shastri, Ahmad, Metzler, Schniter, *Denoising Generalized Expectation-Consistent Approximation for MR Image Recovery*, arXiv:2206.05049v2，§III-B “A DNN denoiser for correlated noise”，式(38)–(41)，[作者公开原文](https://arxiv.org/html/2206.05049v2#S3.SS2)，DOI 10.48550/arXiv.2206.05049。原文通过同协方差的独立噪声样本携带统计条件；本项目显式协方差条件输入不是其原 corr+corr 实现。该引用仅支持噪声统计条件下的有色训练动机，不提供当前 AFDM 接收机的收敛保证。
- `C-STMP/references.bib` 的 `shastri2022` 由上述原文核对。摘要与引言的训练描述对应当前有色预训练记录；该组装稿 III–V 章按作者要求保留 STMP 文字和公式，仅调整双栏断行，逐字节原件另存；后续理论改写范围尚未执行。


### 2026年10月26日 C-STMP 实验章补全与精简

- 组织与分析依据：Cai 等 [arXiv:2506.00581v2](https://arxiv.org/html/2506.00581v2)，§VI-A–C；正式版 pp.3585–3588。直接核对图4去噪、图5收敛、图6–7 SNR、图10导频分析，采用「主要趋势—关键比较—解释」的简短段落。未移用 Cai 的数值或结论。NMSE、检测错误及稀疏字典术语沿用原义；本文 AER 的计数归一化公式已明确给出。
- 补齐原实验章缺失的三个参考文献条目：Tropp–Gilbert–Strauss, Signal Processing 86(3):572–588, 2006（[作者原文](https://tropp.caltech.edu/papers/TGS05-Algorithms-Simultaneous-I-preprint.pdf)，Algorithm 3.1，PDF pp.6–7）；Zhang 等, TVT 72(11):15057–15061, 2023（元数据核对本地 Ding 原文参考文献[8]，方法位置沿用此前 pp.15058–15059、Algorithm 1 核验记录）；Wei 等, TWC 21(9):7407–7426, 2022（[原文](https://arxiv.org/abs/2101.05629)，§III–IV、Algorithm 1；DOI 10.1109/TWC.2022.3158616）。AFDM、多天线及活动读出仍声明为项目适配。
- 四图数值逐项对照保存结果；详细计数及完整长版分析保存在 `paper/C-STMP/checks/experiment_revision_20261026/`。正文保留有色训练高 SNR 略逊、−4 dB 检测排序例外、Q=8 原 STMP 收敛困难等影响结论的事实；未将整体接收机收益单独归因于有色训练。


### 2026年10月26日 C-STMP 当前算法稿与用户数实验

本次根据作者要求，以已复制的 STMP 第 III–V 章为基础改为当前 `C_STMP_variance_em_20261025` 实现；系统模型逐字节不变。沿用 Cai §III–V 的“推断框架—所需统计量的学习—完整算法”顺序，具体变化如下。

| 术语与公式 | 原文位置 | 当前稿件中的对应 |
|---|---|---|
| conditional mean / 条件均值；conditional covariance / 条件协方差 | [Dytso–Poor–Shamai，arXiv:2104.01883](https://arxiv.org/abs/2104.01883)，§IV Proposition 1 式(22)，PDF p.5；一般 Tweedie 关系见式(3) | 第 IV-A/B 章：实坐标协方差 Σ=1/2[Re C,−Im C;Im C,Re C]；采用输出为行的 Jacobian，P=JΣ，复坐标方差为 tr(P)/D。网络导数是该恒等式的近似应用，不再沿用独立二阶网络或条件 MSE 回归的解释。 |
| network preconditioning / 网络预条件 | [Karras 等，NeurIPS 2022 原文](https://proceedings.neurips.cc/paper_files/paper/2022/file/a98846e9d9cc01cfb87eb694d946ce6b-Paper-Conference.pdf)，§5 式(7)–(8)、Table 1 | 第 IV-A 章明确将其标量输入、跳连和输出系数推广至矩阵 Σ；实坐标名义方差 σ_d²=1/2。协方差加权损失是当前实现的损失，不冒称与 EDM 的全部训练设计相同。 |
| Monte Carlo divergence / Monte Carlo 散度估计 | [Metzler–Maleki–Baraniuk，arXiv:1406.4175](https://arxiv.org/abs/1406.4175)，§V-B 式(21) | 第 IV-B 章采用固定协方差下的随机符号中央差分迹，每用户一条固定方向、δ=0.01；这是该估计思路的具体变式，原文使用 Gaussian 方向和单侧差分。包括中心点共三次均值网络前向。 |
| Gaussian noise variance update / Gaussian 噪声方差更新 | [Vila–Schniter，IEEE TSP 2013 原文](https://phil-schniter.web.app/pdf/tsp13_emgm.pdf)，§III-A 式(22)–(27)，p.4661 | 第 III-D 章将后验期望残差更新用于近似查询模型，保留活动混合方差；物理噪声估计固定。原始线性方差历史与调整后方差分开保存。 |
| density ratio estimation / 密度比估计 | Menon–Ong，ICML 2016，§2.2、§3 式(6)–(8)；前文已核对 | 第 IV-C 章保留原 STMP 稿的 BCE 分类器及先验校正，当前分类器使用冻结有色训练均值的白噪声查询特征重新训练。 |

`C-STMP` 仍是作者指定的本项目名称。当前训练使用有色协方差，在线查询使用 C=vI；未引入完整有色反馈接口。旧二阶训练附录保留作历史源文件，已退出本稿编译。具体代码、权重绑定及恒等式核查见 `C-STMP/checks/cstmp_algorithm_revision_20261026/`。

用户数图直接复制已确认的 `result/user_count/figures/paper_interim100_20261026/user_count.pdf`，每个 K 为 100 场景，作为待替换的阶段结果。正文只比较总体趋势及 K=100 时的 NMSE/AER，不声称完整 500 场景结果或所有 K 上的检测排序最优。


### 2026年10月26日 C-STMP 引言动机修订

按作者反馈，开篇顺序改为“卫星物联网的覆盖与终端需求—稀疏短包业务下的免授权接入—卫星时延/多普勒—波形选择”，并补全有色训练的误差来源。

| 术语或表述 | 原文依据及位置 | 本稿使用范围 |
|---|---|---|
| satellite IoT / 卫星物联网；grant-free random access / 免授权随机接入 | Shen等，[arXiv:2412.20806v1](https://arxiv.org/html/2412.20806v1)，§I首段、GFRA段及GNSS终端负担段；Liu–Yu，[arXiv:1706.06438](https://arxiv.org/abs/1706.06438)，§I-A/B；Cai等，[arXiv:2506.00581v2](https://arxiv.org/html/2506.00581v2)，§I首两段 | 覆盖偏远地区、低功耗设备、稀疏活跃短包和逐次授权信令开销。卫星传播时延增加授权交互等待是这些条件的直接推论，不引用额外的定量节省或声称GFRA是唯一方案。 |
| DAFT；full diversity / 满分集；embedded channel estimation / 嵌入式信道估计 | Bemani等，[arXiv:2204.12798v2](https://arxiv.org/html/2204.12798v2)，§II-B式(12)、(16)后矩阵分解，§III-A式(18)–(20)，§III-E式(42)–(43)、§IV Theorem 1及式(51)，§VII图9及相邻导频开销比较 | 一维调制由一次IFFT和两组逐点啁啾乘法实现；路径分离和满分集有参数与信道条件。导频/保护符号优势明确归属于该文嵌入式导频比较，不作为本稿多帧GFRA相对OTFS的新实验结论；不声称所有OTFS实现复杂度都更高。 |
| AWGN observation / AWGN观测；colored Gaussian noise / 有色高斯噪声；correlated noise / 相关噪声 | Cai等上述v2 §III-B1式(20)前状态演化说明及式(20)–(23)，§IV；Shastri等，[arXiv:2206.05049v2](https://arxiv.org/html/2206.05049v2)，§III-A式(28)及后文、§III-B式(38)–(41) | 区分物理白噪声与线性滤波/反馈后的等效误差。本文实际算子的直接展开和已保存诊断见[C-STMP逐模块诊断](../../C-STMP/docs/C_STMP_COMPONENT_DIAGNOSTIC_20261025.md)。有色训练扩大离线扰动分布；在线仍查询C=vI。未宣称训练协方差等于真实迭代误差协方差，未新增相关噪声下的实验收益或收敛保证。 |

本次只改C-STMP中英文引言与关联说明；英文贡献、摘要、系统模型、算法和实验源文件保留。中文贡献第3点和章节导航同步已有英文。原STMP、DU原件不变；修订前文件和差异见 `C-STMP/checks/introduction_motivation_20261026/`。


### 2026年10月26日 C-STMP 摘要按指定文献重写

按作者要求，摘要分别以 Shen2025、Huang2026、Cai2026 及后续有色去噪文献为表述依据。本次“DEC”按项目已收藏的 D-GEC 理解，并核对 D-VDAMP。以下是表述来源与项目适配的界限；摘要不插入文献引文，详细引用仍由引言和算法正文承担。

| 摘要中的术语或表述 | 核对的原文位置 | 本稿使用范围 |
|---|---|---|
| multi-frame transmission scheme；large differential delay and Doppler shift；quasi-static property / 多帧传输方案、大差分时延与多普勒频移、准静态特性 | [Shen 等作者稿](../../../reference/literature/shen2025.pdf)，摘要、§II-B，Proposition 1、式(8)–(10)，PDF pp.1、4–5；[原文](https://arxiv.org/html/2412.20806v1#S2.SS2) | 采用原文的准静态特性与连续多帧表述：信道在连续多帧内近似不变，利用多帧增加观测。“共享信道观测”并非 Shen 原词，不作为文献术语。本项目使用 AFDM，采用块内信道不变及跨帧相位分离；不移用其 OTFS 扩频、数据符号检测或三模块稀疏接收机。 |
| AFDM effective channel；fractional delay；Doppler；grid-aligned channel assumptions / AFDM 有效信道、分数时延、多普勒、网格对齐信道假设 | [Huang 等正式版](../../../reference/literature/huang2026.pdf)，摘要及§I，p.2949；§II，p.2950；§III-A，式(6)–(7)，p.2951 | 直接学习完整有效信道分布，避免预设稀疏或路径网格对齐假设；多天线张量是本项目扩展。不写成无任何统计假设，不采用或宣称采用其 Langevin 后验采样。 |
| turbo message passing；channel and device activity denoisers；extrinsic messages / Turbo 消息传递、信道和设备活动去噪器、外信息消息 | [Cai 等正式版](../../../reference/literature/cai2026.pdf)，摘要、§I-A、§III-A/B、§IV-A；[作者稿§III](https://arxiv.org/html/2506.00581v2#S3) | 保留完整用户信道张量的联合去噪和线性模块之间的外信息交换。当前方差由条件均值导数估计，活动概率来自另训分类器；不描述为照搬 Cai 的二阶 score 网络和活动积分。 |
| colored Gaussian noise；covariance matrix / 有色高斯噪声、协方差矩阵 | [D-GEC 作者稿](../../../reference/literature/shastri2022_dgec.pdf)，§III-B式(38)–(41)，PDF pp.15–16；[原文](https://arxiv.org/html/2206.05049v2#S3.SS2)；[D-VDAMP](../../../reference/literature/metzler2020_dvdamp.pdf)，§2.3，PDF p.3；[原文](https://arxiv.org/html/2010.13211v1) | 两文支持按噪声统计条件训练有色去噪器。D-GEC 的 corr+corr 输入独立同协方差噪声样本，D-VDAMP 输入小波子带标准差；本项目输入协方差因子，两者都不是本项目实现的别名。在线仍用标量方差消息，不宣称训练协方差等于实际迭代误差协方差。 |
| conditional-mean derivatives；posterior expected residual energy / 条件均值导数、后验预期残差能量 | 沿用本文件“C-STMP 当前算法稿与用户数实验”中已核对的 Dytso Proposition 1、Vila–Schniter §III-A 式(22)–(27) | 对应本稿第 III-D、IV-B 章的当前实现，表述为估计和更新，不宣称精确神经后验或 EM 单调性。C-STMP 为作者已指定的项目方法名，不添加自拟英文展开。 |

结尾比较依据为当前六档 SNR 的保存汇总 `result/snr_comparison/data/c_stmp_variance_em_1000_snr_m4_p6_20261025/SUMMARY.json`，每档1000场景、已知跨帧相位、观测估计噪声；只声称相对项目原 STMP 在所评估信噪比下的 NMSE/AER 改善。未将收益单独归因于有色训练，未声称所有基线、未知相位或跨信道条件下最优。该评估的回顾性限制保留在实验章与原汇总中。

本次中英文含义对齐，沿用既有简体中文稿；原文提取、五篇PDF的结构核验、修订前备份及差异保存在 `C-STMP/checks/abstract_sources_20261026/`。文献核验脚本的 POSIX 侧文件接口不适用于 Windows，因此调用同一脚本的标准输出并原样保存 JSON；五篇结构核验均为 PASS。

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

完整[逐词检查](../../C-STMP/checks/abstract_original_words_20261026/SOURCE_WORD_CHECK.md)、[词形与页码](../../C-STMP/checks/abstract_original_words_20261026/WORD_AUDIT.json)、[短语与上下文](../../C-STMP/checks/abstract_original_words_20261026/TERM_AUDIT.json)可复查；本轮修订前文件另存 before/。

2026年10月26日摘要衔接补充：采用 **Specifically / Subsequently / Building on this**，中文对应“具体而言 / 随后 / 在此基础上”，分别引出具体传输方案、推进至信道先验、再由该先验衔接接收机。Specifically 见 Cai2026 摘要（PDF p.1）；Subsequently 见 Shen2025 §I 贡献说明（PDF p.2）；Building on this 见 Shen2025 §I 相关工作（PDF p.2）。三个完整连接表达均核对原文连续词序，不借用被介绍工作的技术结论。其余摘要表述保持不变。


### 2026年10月26日 C-STMP 摘要四篇核心论文逐句复核

本次将最新摘要的词汇与表述依据限定为 Shen2025、Huang2026、Cai2026 和 D-GEC；不再依赖 D-VDAMP 的词汇。此前五篇范围的说明保留为修订历史，以下为当前版本。按作者要求，完整词形须在四篇参考文献列表之前的摘要或正文出现，大小写与 Unicode 排版统一后逐词匹配，不做词干归并或功能词豁免。

术语有出处不等于整句来自原文。当前八句摘要逐句记录原文位置、用词依据和本项目适配边界，见[逐句依据](../../C-STMP/checks/abstract_original_words_20261026/SENTENCE_SOURCES.md)。传输采用 Shen 的多帧与输入输出关系描述，信道先验采用 Huang 的完整有效信道学习描述，接收机以 Cai 的消息传递框架及 D-GEC 的有色去噪训练为依据。保留 Specifically / Subsequently / Building on this 的递进；通过 we propose、we learn、we develop 的平行句式组织三部分。

| 当前术语 | 原文位置 | 本稿边界 |
|---|---|---|
| known covariance matrix；colored Gaussian noise / 已知协方差矩阵、有色高斯噪声 | D-GEC §III-B，PDF pp.15–16，式(38)–(41) | 本文以协方差因子作为训练条件；D-GEC 的 corr+corr 以独立同协方差噪声样本为条件。不得视为相同网络。在线仍用标量方差消息。 |
| conditional mean；Jacobian；posterior variance / 条件均值、雅可比矩阵、后验方差 | D-GEC §II-C，PDF p.6；Cai2026 §IV-A，PDF p.9，式(44)–(45) | 用 Jacobian 替代仅在此前五篇语料内匹配的 derivatives。四篇支持这些术语与相关背景，不构成本文活动分类特征与均值导数方差估计组合的完整来源；直接数学与分类依据仍见正文 Dytso、Menon–Ong 引用。 |
| baseline receiver / 基准接收机 | baseline 词形见 Cai2026；本项目对照定义见第 VI 节 | 此处仅指项目原 STMP。结果来自六档 SNR 每档 1000 场景的保存汇总；已知相位与比较范围保留，不归为四篇论文的结果。 |

当前中英文摘要同时更新；算法、模型公式、实验结果与权重不改动。完整稿继续只使用 main.pdf，不新增版本 PDF。


### 2026年10月26日 C-STMP 摘要精简为方案层面的表述

按作者反馈，摘要保留传输方案、有效信道先验、Turbo 接收方法三项贡献及已有实验结论。接收机部分压缩为一句：通过有色高斯噪声训练的信道去噪器引入所学先验。turbo message passing 与先验结合见 Cai2026 §I-A、§III-A/B（PDF pp.2、5–6）；channel denoiser 与 colored Gaussian noise 见四篇词形/短语记录，训练思想见 D-GEC §III-B（PDF pp.15–16，式(38)–(41)）。具体组合属于本项目，不当作原文整句或同一网络实现。

外信息交换、协方差条件、标量消息、条件均值、雅可比及方差估计不再出现在当前摘要；正文与其数学引用保持原样。此前八句版本的逐句说明由当前六句[来源对照](../../C-STMP/checks/abstract_original_words_20261026/SENTENCE_SOURCES.md)替代；源文件差异见同目录 CONCISE_REVISION.diff。当前版本继续使用四篇范围的严格词形核验，保留 Specifically / Subsequently / Building on this 及已知相位的实验限定。


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
