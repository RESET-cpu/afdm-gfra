# 当前术语与来源

2026-10-12：协方差条件重训及完整二阶矩相关条目作为[已归档研究](history/archive/covariance_training_20261012/README.md)的来源记录保留；当前采用原三模块路线，状态与后续方向见 [CURRENT_STAGE.md](CURRENT_STAGE.md)。

本页记录当前系统模型和七个算法入口使用的术语。来源定位沿用已核对的论文记录；
完整日期记录、诊断公式和历史方法见[整理前术语台账](../docs/history/archive/workspace_organization_20261011/before/docs/TERMINOLOGY.md)。
项目参数、软件函数名和公式编号按操作直接描述。

| 原词或忠实译名 | 原文定位 | 当前使用 |
|---|---|---|
| affine frequency division multiplexing、discrete affine Fourier transform、chirp-periodic prefix / AFDM、离散仿射傅里叶变换、啁啾周期前缀 | [Bemani 等作者稿](https://arxiv.org/html/2204.12798v2)，§II-B 式(11)–(16)、§III-A 式(18)–(19) | 波形、DAFT 与前缀定义；具体展开见 SYSTEM_MODEL |
| fractional delay、fractional Doppler、effective channel matrix / 分数时延、分数 Doppler、有效信道矩阵 | [Huang](../references/huang2026_prior_agnostic_afdm_diffusion.pdf)，§II 式(4)–(5)，p.2950 | 连续物理路径；本项目的符号换算按 SYSTEM_MODEL 说明 |
| likelihood-annealed Langevin dynamics、posterior sampling / 似然退火 Langevin 动力学、后验采样 | [Huang 2026](../references/huang2026_prior_agnostic_afdm_diffusion.pdf)，摘要 p.2949，§III-B 式(8)–(10) p.2951，Algorithm 1、Fig.3 p.2952 | 文献对照：在单用户 SISO 的完整 AFDM 信道矩阵上，以观测残差、学习的先验 score 和随机扰动进行多噪声层级的迭代。当前主线是线性模块与局部 score 去噪器的消息传递；原文 Fig.4 的性能结论不自动成为当前 JADCE 的保证。 |
| annealed Langevin dynamics / 退火 Langevin 动力学 | [Arvinte–Tamir 作者稿 v2](https://arxiv.org/html/2204.07122v2)，§II-B 式(4)–(5)、§III-B 式(15)–(17)、Algorithm 1；[作者测试代码](https://github.com/utcsilab/score-based-channels/blob/main/src/score_based_channels/test_score.py) L129–157，2026-10-12 核对 | [已知活动集合诊断](history/experiments/proposed_known_activity_score_20261012/ALGORITHM.md)使用同一冻结 first 网络和原始观测残差。复数方差、梯度、随机扰动统一按该文件推导；两种退火、步长、温度与固定末步读出为本实验设置。有限噪声下的似然是近似，有限网络和迭代不保证精确后验采样；不称为 Huang 实验复现。 |
| likelihood score、prior score / 似然 score、先验 score | Huang 2026 §III-B 式(9)–(10)，p.2951，Algorithm 1 p.2952 | 对照时从 log p(Y\|H)=−‖Y−HX‖²/σ_z²+常数直接求导：Wirtinger 导数 ∂log p/∂H*= (Y−HX)Xᴴ/σ_z²；对应实坐标梯度整体多因子2。原文式(10)和 Algorithm 1 印刷为 +(HX−Y)Xᴴ，与其梯度上升更新的符号不一致；已视觉核对并用合成有限差分检查正确方向。此处只记录复现所需的符号核查，不据此判定原实验代码采用了该印刷符号。 |
| array response vector、common spatial direction / 阵列响应向量、共同空间方向 | [Li–Gao–Xia](https://arxiv.org/html/2207.11958v2#S2.SS3)，§II-C 式(8) | 每用户共享方向的物理模型 |
| variational line spectral estimation (VALSE)；posterior probability density functions / 变分线谱估计、后验概率密度 | [Badiu–Hansen–Fleury](https://arxiv.org/pdf/1604.03744)，§II–III 式(6)–(12)，PDF pp.3–4 | 20261013未知方向调研：借鉴对连续方向分布取期望，不能把原Bernoulli–Gaussian幅度更新直接称为当前小网络算法；项目适配与限制见[调研](../references/direction_score_inference_20261013/REPORT.md) |
| multisnapshot VALSE (MVALSE) / 多快拍VALSE | [Zhu等](https://arxiv.org/pdf/1803.06497)，§III 式(14b)、(16)、(19)–(20)，PDF pp.6–7 | 阵列响应的后验期望不同于在单一方向估计处取值；多快拍方向更新含其他分量和交叉协方差。当前G各元素有结构，不能原样采用独立Gaussian幅度模型 |
| multidimensional VALSE (MDVALSE) / 多维VALSE | [Zhang等](https://arxiv.org/pdf/1912.11759)，§III-A 式(14)–(16)，PDF p.5 | 二维方向分布近似的参考；项目物理方向余弦圆盘域和神经先验需另行适配，尚未实施 |
| likelihood ratio trick / 似然比技巧 | [Rizvi–Pettee–Nachman](https://arxiv.org/html/2305.10500v1#S2)，§II 式(6)–(12) | 平衡BCE的理想分类器odds对应密度比；有限证据网络需校准。方向积分的比值恒等式及全协方差展开为[项目直接推导](../references/direction_score_inference_20261013/REPORT.md)，非该论文现成算法 |
| local tilted expectation–maximization；damping / 局部倾斜分布期望最大化、阻尼 | [Na–Wadayama 2026预印本](https://arxiv.org/html/2607.14597v1)，§II-B 式(4)–(5)、Algorithm 1；§II-D | 借鉴模块内参数与矩更新的一致性；其Gaussian cavity、精确score及可辨识性假设并未在本项目成立，不能移植近oracle性能或固定点最优性结论 |
| turbo message passing、Gaussian projection、extrinsic message / turbo 消息传递、Gaussian 投影、外信息消息 | [Cai](https://arxiv.org/html/2506.00581v2#S3)，§III-A–B 式(6)–(42) | 两模块更新、受限协方差与 Gaussian 消息相除；THEORY T3–T5、T13–T17 |
| Generalized Expectation Consistency (GEC)、block uniform diagonalization / 广义期望一致性、分块均匀对角化 | [Fletcher等](https://arxiv.org/pdf/1602.07795v2)，§II-A 式(8)–(9)、§II-B Algorithm 1，PDF pp.2–3 | 20261012均值反馈研究的候选：每用户为一块、块内保留一个标量。复数MMV线性查询及外信息公式是[项目推导](../docs/history/experiments/proposed_mean_feedback_20261012/ANALYSIS.md)。已实现并完成[六条件验证](../docs/history/results/proposed_mean_feedback_20261012/user_scalar_pilot/REPORT.md)：完整候选未减少漏检，尚未采用；有限网络的均值/条件MSE不自动满足原文精确估计函数及收敛假设 |
| Tweedie's formula、denoising score matching、second-order score matching / Tweedie 公式、去噪得分匹配、二阶得分匹配 | [Cai](https://arxiv.org/html/2506.00581v2#S4)，§IV-A–C 式(43)–(54) | 一阶均值与二阶全坐标平均迹；有限一阶均值下的条件 MSE 关系见 THEORY T8–T11 |

2026-10-16的[AWGN损失加权对照](../docs/history/experiments/proposed_awgn_weighting_20261016/PROTOCOL.md)
沿用上述DSM/second-order score matching的术语。将原单样本损失分别乘v/E[v]和v²/E[v²]，
是根据Cai式(48)–(49)、(53)–(54)直接变换损失权重；
不将该项目选择另称为已有算法，也不声称正权重能保证有限网络读出改善。

后续[均值尺度与辅助读出对照](../docs/history/results/proposed_awgn_mean_scale_20261016/REPORT.md)
仍在 Cai §IV-A–C 式(43)–(54)的 AWGN 实坐标/复噪声方差约定下操作。
以训练数据最小化 E||cF−H||² 得到 c=E Re〈F,H〉/E||F||²，是本文明确展开的输出修正，
不是文献中另一个已命名算法，也不能将 cF 自动称为原物理先验的精确 Tweedie 均值。
有限均值风险 R_f=tr Cov(H|x)/D+||E[H|x]−f||²/D 来自条件平方误差直接展开；
原分类器仍可使用原 F0(x,v) 特征，另一均值输出的改变不强制改变该分类器的输入定义。
对应“活动证据/密度比”的来源和训练先验校正沿用下方 Menon–Ong §3–4.2 条目。

| pseudo AWGN observation model | Cai §IV-A 式(43)、§V-B1 | 去噪查询的工作模型；实际有限 AFDM 查询的适用性属于近似 |
| Gaussian approximation、device activity denoiser / Gaussian 近似、设备活动去噪器 | Cai §III-B1–B2 式(26)–(30) | 网络查询超出支持范围时，以保留的 Gaussian site 计算解析活动概率 |
| density ratio estimation、class-probability estimation、logistic loss / 密度比估计、类别概率估计、logistic 损失 | [Menon–Ong](https://proceedings.mlr.press/v48/menon16.pdf)，§3 式(6)–(8)、§4.2 式(16)–(17)，pp.305–306 | 分类器 logit 经训练先验校正，再加入公开活动先验；THEORY T15 |
| damping / 阻尼 | Cai §V-B1 式(57)–(58) | 均值与协方差的算术插值；当前新值权重 0.2 是项目设置，选择依据见 [默认设置记录](../results/proposed_default_20261014/DEFAULT_SELECTION.json)；历史图配置保留 0.1 |
| vector approximate message passing (VAMP)、divergence / 向量近似消息传递、散度 | [Rangan–Schniter–Fletcher](https://arxiv.org/pdf/1610.03082)，Algorithm 2 第5–8行，PDF p.4；§III-C，PDF p.6 | 20261012实验候选对完整联合映射 pF 取实坐标平均散度，并成对定义外信息均值和方差。有限差分、固定探针及沿用本项目比例裁剪是实验设置；不是原文的精度裁剪，消息方差不自动等于真实MSE |
| group averaging / 群平均 | [Chen–Dobriban–Lee](https://papers.nips.cc/paper_files/paper/2020/file/f4573fc71c731d5c362f0d7860945b88-Paper.pdf)，§3.1 Lemma 3.2、Proposition 3.3，§4 | 20261012实验检查公共复相位旋转；四相位组合和混合矩按实验协议定义。固定查询上的风险依据不保证闭环性能；条件分布平均与先验密度混合是不同操作。20261015增加对完整接收机输出的群平均候选：相位前端运行一次，四个整体旋转各自独立完成条件推断后合并；公式和期望平方误差的适用条件见 THEORY §12，门限 AER 另作独立验证 |
| equivariance / 等变性 | [Chen–Dobriban–Lee](https://papers.nips.cc/paper_files/paper/2020/file/f4573fc71c731d5c362f0d7860945b88-Paper.pdf)，§1 PDF p.1 对网络等变性的说明，§2 对群作用的定义 | 当前相位不变信道先验和AWGN下，F(gR,v)=gF(R,v)由项目条件均值定义推出。训练中惩罚偏离该关系的候选公式（历史文件已清理，原路径：`experiments/proposed_mean_feedback_20261012/PLAN.md`）已进入[独立训练对照](../docs/history/experiments/proposed_phase_training_20261012/PROTOCOL.md)，效果待验证；它不是引用论文已验证的JADCE算法，部署仍使用一次一阶评估 |
| rank-r matrix approximation、low-rank matrix fitting / 秩r矩阵近似、低秩矩阵拟合 | [Xu等](https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/ell2.12379)，§3 “Low-rank matrix fitting based channel estimation”，式(7) | 20261012保存均值诊断对M×NP天线展开保留一个奇异分量，只用已有F；未采用该文矩阵补全流程。样本秩一不推出后验均值秩一，代数反例、NMSE与固定线性响应见[分析记录](../docs/history/experiments/proposed_mean_feedback_20261012/evidence/mean_structure_analysis.json)，可选秩一均值反馈已接入Receiver；[闭环实验](history/results/proposed_rank_one_20261012/REPORT.md)在用户要求下停止，仅一个开发条件完成三版本配对，不能作总体性能结论。训练时对去噪均值的其余奇异值能量加惩罚属于项目待验证目标，不是该文已验证的score训练方法 |
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
| power posterior、thermodynamic integration、marginal likelihood / 幂后验、热力学积分、边际似然 | [Friel–Pettitt 所读作者早期稿](https://www2.stat.duke.edu/~scs/Courses/Stat376/Papers/NormConstants/FrielPettitPath05.pdf)，§3 式(4)–(5)、§3.1 式(6)；[Friel–Hurn–Wyse v2](https://arxiv.org/html/1209.3198v2#S2)，§2 式(6)–(11) | 20261012活动证据调研：在固定C的proper complex Gaussian查询下，幂β的活跃后验等于(R,C/β)的后验。项目推导ell=∫₀¹[2Re tr(RᴴC⁻¹mβ)−tr(mβᴴC⁻¹mβ)−L tr(C⁻¹Vβ)]dβ；只需列对角协方差块平均，不要求后验Gaussian、各列独立或Vβ<C/β。用现有first/second代入是另行提出的近似，二阶条件误差矩不自动等于Vβ，端点和求积误差必须保留。推导、版本边界及精确合成检查见 [调研来源](../references/activity_evidence_20261012/SOURCES.json) 和 [数学检查](../references/activity_evidence_20261012/MATH_CHECKS.json)；尚未运行该候选的学习网络或接收机比较。 |
| pointwise MMSE、probability density via MMSE / 逐点MMSE、通过MMSE表示概率密度 | [Kong–Brekelmans–Ver Steeg](https://arxiv.org/html/2302.03792v1#S3)，§2 式(4)–(5)、§3 式(7)–(8)、Appendix A.1–A.2 | 去噪误差差值在噪声尺度上的积分恢复逐点log density ratio的原文依据。项目针对q1(R\|C)与q0(R\|C)的复矩阵转换、以及从H的去噪器恢复R的去噪器，记录于上述SOURCES.json；不能把平均I-MMSE关系或有限网络的任意MSE直接称为精确活动证据。 |
| probability flow ODE、instantaneous change of variables、Skilling–Hutchinson trace estimator / 概率流ODE、瞬时变量变换、Skilling–Hutchinson迹估计 | [Song 等](https://arxiv.org/html/2011.13456v2#S4.SS3)，§4.3 式(13)、Appendix D.2 式(38)–(40) | 调研备选：一阶网络转score后，通过ODE及散度积分求其流模型定义的似然。该密度与真实物理分布的偏差、数值积分和随机迹估计误差需区分；当前二阶条件误差矩不是有限一阶网络的精确Jacobian，不能直接替代其散度。尚未实施。 |
| calibrated discriminative classifier、likelihood ratio / 经校准的判别分类器、似然比 | [Cranmer–Pavez–Louppe v2](https://arxiv.org/html/1506.02169v2#S2.SS2)，§2.2 Theorem 1、式(2.4)、(2.10)，§2.3、§3.3 | 当前activity模块的补充依据：理想分类器或其单调变换与密度比相关；有限分类输出需验证校准与检测能力，条件C及训练/部署先验差异不能忽略。原文不保证任意分类器raw logit都是精确证据。 |
| denoising-based VDAMP (D-VDAMP)、colored noise denoising / 去噪型VDAMP、有色噪声去噪 | [Metzler–Wetzstein](https://arxiv.org/pdf/2010.13211v1)，§1末段、Algorithm 1，§2.2–2.3，PDF pp.1–3；VDAMP为variable density AMP | 子带方差消息与对应条件去噪网络协同设计的先例；其 weak state evolution 是经验模型，不移称为本项目的理论保证 |
| denoising generalized expectation-consistent approximation (D-GEC)、corr+corr | [Shastri 等](https://arxiv.org/pdf/2206.05049v2)，§III-B 式(39)–(41)，§IV-A 式(42)，PDF pp.16–18 | 用同协方差独立噪声样本作为去噪网络辅助输入；一般形式与小波子带训练族分开表述。当前用于文献对照，不是项目已采用算法 |
| Fast Iterative REnoising (FIRE)、colored renoising | [Bendel 等](https://arxiv.org/html/2501.17468v4#S3.SS1)，§3.1 式(8)–(19)、Theorem 1 | 通过补加有色噪声使查询误差近似白噪声的替代路线；依赖误差模型，未在本项目实施，也不能消除已有信号方向偏差 |
| MSE estimation / 均方误差估计 | [Ma–Ping OAMP](https://arxiv.org/pdf/1602.06509v3)，§III-I 式(30)–(31)，PDF p.5 | 20261012观测功率初始化控制采用零均值初始估计下的复数MMV能量式，扣除公开噪声后估算输入共同方差；不是在当前物理相关输入上认证点态无偏 |
| simultaneous orthogonal matching pursuit / 同时正交匹配追踪（SOMP） | [Tropp 作者预印本](https://tropp.caltech.edu/papers/TGS05-Algorithms-Simultaneous-I-preprint.pdf)，Algorithm 3.1，pp.6–7，§3.2 | 多测量列共享支撑；64 原子预算和已知噪声残差停止为项目设置 |
| generalized approximate message passing sparse Bayesian learning / GAMP-SBL | [Zhang](../references/zhang2023_gamp_sbl_grant_free_noma.pdf)，pp.15058–15059 式(3)–(19)、Algorithm 1 | 复数模型中跨天线共享行精度和公共噪声精度，明确作为 MMV 适配 |
| Gamma prior、MAP update / Gamma 先验、MAP 更新 | Zhang 式(3)–(4)、(16)、(18)–(19) | 共享行精度和噪声学习；用公开噪声确定 Gamma 超参数是项目数值设置 |
| graph neural network-based adaptive sparsity pattern learning / GNN-ASPL | [Ding](../paper/literature/ding2026.pdf)，pp.3–5 式(12)–(28)、§III-B/C | 当前十层展开网络、图内信息传播与逐层训练；具体训练分布见 TRAINING |
| decision threshold / 判决门限 | Ding p.4 式(27) | 系数块能量按用户间最大值归一化；公共 SNR 选取冻结节点的规则是项目设置。20261015 Proposed 可选最终判决使用完整估计能量除以公开噪声方差，并同时要求原概率不低于0.5；该归一化和两条件规则为项目明示公式 THEORY P3，不称为 Ding 的同一算法，也不将能量分数称为概率 |
| EM-GAMP；Gaussian log-likelihood ratio / Gaussian 对数似然比 | [Zhao](../references/zhao2025_mixed_fronthaul_jadce.pdf)，pp.4123–4126 式(20)–(40)、(49)、(51)–(57)、Algorithm 1 | 全分辨率特例，式(38)方差更新及 Gaussian block LLR；AFDM/MMV 适配与待验证状态见 BASELINES |
| on-grid / 网格内；off-grid / 网格外 | [Wei 等作者稿](https://arxiv.org/pdf/2101.05629v1)，§III-B pp.11–12 式(17)–(24)、§VI-B pp.26–27 | 基线使用有限整数网格，评价信道允许连续参数偏离网格 |
| spike-and-slab prior / 尖峰与连续分布混合先验；conditional slab variance / 非零分量条件方差 | Ding pp.3–4，§III-A 的 p(Z\|λ) 及 Σ 对角元 γ 定义 | 20261012逐 SNR 的 on-grid 训练拟合只统计物理占用行，合并同一行的路径碰撞。固定零均值和共享标量是项目设置；当前正式混合训练 checkpoint 已采用该口径 |
| off-grid sparse Bayesian learning / 网格外稀疏贝叶斯学习 | [Wei 等作者稿](https://arxiv.org/pdf/2101.05629v1)，§III-B 式(17)–(24)，§IV 式(35)–(57)、Algorithm 1（PDF p.18），§V Algorithm 2 | 已接入 `offgrid_sbl`。原文向量化“1D”模型包含时延和多普勒偏移；本项目的 AFDM/MMV 方差及偏移更新推导见 OFFGRID_BASELINES。固定公开噪声、每用户相关性筛选、区间约束是明确的项目设置 |
| first-order linear approximation / 一阶线性近似 | [Wei 等作者稿](https://arxiv.org/html/2101.05629v1)，§III-B 式(17)–(24) | SBL 在固定中心计算时延与 Doppler 导数，以偏移修正字典。20261012 审查另外记录精确预测与一阶预测的相对距离；这一诊断量由项目定义，不等同于信道 NMSE |
| virtual sampling grid、virtual sampling resolution / 虚拟采样网格、虚拟采样分辨率 | [Wei 作者稿 v1](https://arxiv.org/pdf/2101.05629v1)，§III-B p.11、式(18)前的定义，§VI pp.23–26、Fig.5–7 | 原稿扫描间距 0.2–0.9，Fig.5/6 分别为两维均 0.5/0.8。审查将 AFDM 固定时延采样点由 112 增至 448；四倍密度由项目校准确定，归一化间距不能跨波形直接照搬。完整配置来源见 OFFGRID_BASELINES 的 20261013 溯源 |
| convergence tolerance / 收敛容差 | [Wei 作者稿 v1](https://arxiv.org/pdf/2101.05629v1)，Algorithm 1 p.18、§VI p.24 | 原稿按方差超参数相对变化不超过 10^−3 停止，Tmax 未给出具体数值。本项目使用 10^−4 并额外检查偏移增量；600 次上限为项目校准预算 |
| hierarchical hyperprior distribution / 分层超先验分布（Wei SBL） | [Wei 作者稿 v1](https://arxiv.org/pdf/2101.05629v1)，§IV-A 式(26)–(29)，§IV-B 式(44)–(45)，Algorithm 1 | 20261013 独立对齐实验令物理系数方差先验 rho=0.01。列归一化 x_i=s_i h_i 后，方差乘 s_i²、Gamma 率参数除 s_i²；MMV 方差及噪声更新是项目推导，见 docs/history/experiments/offgrid_sbl_reference_20261013/PROTOCOL.md。原稿相关幅值初始化推广为跨天线相关幅值的均方根，明确不是原文已有 MMV 公式 |
| multi-snapshot Newtonized orthogonal matching pursuit (MNOMP) / 多快拍 Newton 化正交匹配追踪 | [Zhu 等作者稿](https://arxiv.org/pdf/1802.01266)，§II 式(1)，§III 式(6)、Algorithm 1（PDF p.7），§IV-A | 实现见 [MNOMP 归档](../docs/history/archive/mnomp_20261014/README.md)。原文为一维频率 MMV；AFDM 二维参数和范数可变的目标导数为项目适配 |
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

2026-10-13 小网络训练审查补充，详见[逐环节报告](../docs/history/results/small_training_audit_20261013/REPORT.md)。

| 原词或忠实译名 | 原文定位 | 本轮使用范围 |
|---|---|---|
| RefineNet；multi-resolution fusion；cascaded residual pooling / RefineNet、多分辨率融合、级联残差池化 | Huang 2026，§III-A、Fig.1，p.2951；原文引用Lin等CVPR 2017 RefineNet | 原文指定的网络家族。当前16×16 `GlobalFirstScore`是残差卷积加全局线性混合，不能称同一RefineNet；本项目完整信道RefineNet的宽度及参数量也不能当作Huang披露的配置 |
| denoising score matching / 去噪得分匹配 | Huang 2026，§III-A 式(7)及其后实虚双通道说明，p.2951 | 原文复噪声方差、−N/σ²目标与实梯度措辞需区分约定。本项目按每实分量v/2训练缩放实score，均值为r+(v/2)s；核对通过但不宣称与未知作者代码逐项一致 |


2026-10-13 一阶网络训练与结构调研补充。以下仅为[候选研究](../references/first_score_improvements_20261012/REPORT.md)的来源，不表示已经修改默认训练或获得性能收益。

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

2026-10-13 小网络数据物理审查补充，详见[审查报告](../docs/history/results/small_data_physics_audit_20261013/REPORT.md)。

| 原词或忠实译名 | 原文定位 | 本轮使用范围 |
|---|---|---|
| piecewise-continuous AFDM (PC-AFDM)；frequency wrapping；phase correction / 分段连续AFDM、频率折叠、相位修正 | [Cao–Shao 2026预印本](https://arxiv.org/html/2609.07480v1)，§II-A 式(1)–(3)、Proposition 1 | 用于描述并核对当前分数时延基函数的跳变性质；项目独立数值检查确认边界两侧存在非零矩阵差异。未采用其替代波形，未证明这种性质导致当前网络性能差距，也不把作者的命名追溯成Huang原文术语 |

2026-10-13 GNSS-Free、AFDM、off-grid场景来源补充，详见[设定审查](../docs/history/results/scenario_assumptions_audit_20261013/REPORT.md)。

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
| regularized zero-forcing (RZF) processing / 正则化迫零处理 | [Li等v2](https://arxiv.org/html/2207.11958v2#S4.SS3)，§IV-C Proposition 3式(38)–(41)，PDF p.9 | 空间权重依赖同导频用户方向与功率，正则项由共同PDP和噪声联合确定、通常不等于噪声方差。原文为导频子载波数趋于无穷的MSE设计；不能直接套给已作线性外信息更新的查询。原文与本项目推导分开记录于[详细核查](../references/spatial_combining_audit_20261013/REPORT.md) |

2026-10-13 GNSS-independent 场景与方向先验的适用条件，详见[可行性核查](../references/gnss_direction_feasibility_20261013/REPORT.md)。

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

2026-10-13 天线维度与 score 网络结构调研，详见[综合报告](../references/antenna_score_architecture_20261013/REPORT.md)：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| angular/beamspace domain；unitary Fourier transformation / 角域或波束域、酉傅里叶变换 | [Fesl等，WCL 2024作者稿v1](https://arxiv.org/html/2403.03545v1)，§III-A，Algorithms 1–2，PDF pp.2–3；§III-C/Fig.1，p.3 | 原文变换Rx×Tx两阵列轴；本项目空间变换沿UPA的y、z两轴。完整酉变换保留白噪声方差，不保证性能提升；论文轻量模型整体比较不是FFT单因素消融 |
| beam-delay domain；three-dimensional convolution / 波束—时延域、三维卷积 | [Artemasov等，ITU Journal 2024](https://www.itu.int/dms_pub/itu-s/opb/jnl/S-JNL-VOL5.ISSUE1-2024-A05-PDF-E.pdf)，§2.2式(8)–(9)，pp.63–64；§4.1式(23)–(24)，p.66 | 原文沿平面阵列两beam轴与delay卷积。我们的UPA两轴加AFDM矩阵两轴共四个物理轴，不能把普通Conv3d直接称为完全同构；交替处理两组二维轴是本项目待验证设计 |
| fully convolutional deep learning receiver / 全卷积深度学习接收机 | [Honkala等，DeepRx，TWC 2021](https://arxiv.org/html/2005.01494#S3)，§III/Fig.2、Table II | 原文天线信息放入特征通道、卷积沿时频，说明这种组织不是必然失效；其两Rx、LLR输出和数据辅助输入不能作为本项目score去噪的公平架构对照 |
| circular convolution / 圆周卷积 | [Fesl等，SPAWC 2021](https://arxiv.org/html/2104.12667)，§III–IV式(14)–(19) | 原文从块循环和移位假设得到DFT域二维圆周卷积；引用作结构设计依据，不声称其ULA统计假设已在本项目UPA/AFDM成立 |

上述阵列轴处理于2026-10-13曾进入[完整网络配对实验](CURRENT_STAGE.md)：保留原RefineNet，并增加交替处理UPA和AFDM两组轴的分支，采用同参数量的AFDM轴对照。该组合及其零输出初始化为本项目实现选择，不冠以新方法名称，也不宣称复现Artemasov或Fesl的原网络。角域变换不在此首轮对照中同时引入。


2026-10-13 完整角域原生实现与功率处理补充：

沿用上述 Fesl §III-A/C 的角域表示、Artemasov §4.1 的平面阵列组织及 Cai §IV 的 denoising score matching（去噪分数匹配）。四物理轴上交替两组二维卷积为项目设计，不命名为文献已有网络。该方案已按用户要求删除，历史说明见[精简记录](CURRENT_STAGE.md)。

Cai §V-B2 式(59)–(65)的 channel power normalization（信道功率归一化）在本项目评估中须区分真值范数与查询能量估计：式(59)右侧对白噪声取条件期望后等于左侧，有限随机查询上不是严格恒等式。功率估计方差、负值概率及缩放不确定性说明是项目推导，见[功率评估](../docs/history/experiments/full_power_channels_20261013/PLAN.md)。样本总功率不自动等同于慢变大尺度衰落，不能把解析缩放称为独立学习网络。


2026-10-13 用户授权执行逐样本功率归一化训练：沿用 Cai §V-B2 的 channel power normalization（信道功率归一化）定义，U=H/sqrt(mean(|H|²))。训练噪声相对于U独立采样；推断中的解析查询功率估计、固定正下限和模型支持限制明确记录于[执行方案](../docs/history/experiments/full_power_channels_20261013/PLAN.md)。扩大噪声范围、0.5dB继续训练门槛及其统计检查均为本项目选择，不归为Cai原文规定。


2026-10-13 数据张量阶数与卷积轴的核对：Fesl WCL 2024作者稿§II-A式(1)、§III-C/Fig.1以接收×发射二维复信道为输入，实虚作为两通道，采用2D卷积。Artemasov 2024 §4.1式(23)–(24)、Fig.3、p.66明确写四阶复张量 Nu×NR×NC×Nτ，其中Nu为UE天线数；卷积核为3×3×3，沿两beam轴与delay处理。不能将Nu误称批次/实虚维，也不能把“四阶输入”当成四轴卷积的证据。本项目4×4×16×16两beam轴加AFDM输入/输出索引，并交替两组2D卷积，是独立设计扩展，两文未直接验证该组合。

2026-10-13 二维角域展平的[专项核查](../references/afdm_network_axes_20261013/REPORT.md)：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| beamspace channel vector / 波束域信道向量；Gaussian mixture LAMP (GM-LAMP) | [Wei–Hu–Dai，TCOM 2021正式全文](https://oa.ee.tsinghua.edu.cn/dailinglong/publications/paper/Deep%20learning%20for%20beamspace%20channel%20estimation%20in%20millimeter-wave%20massive%20MIMO%20systems.pdf)，§II-A式(3)、(6)–(8)，pp.183–184；§III，pp.186–188；§IV Fig.5、7，pp.190–191 | UPA二维导向基与完整N×1角域向量可以并存，后续采用学习线性映射和逐元素收缩；不是普通Conv1D，也未比较本项目4×4 beam卷积与通道组织方式 |
| convolutional input channels / 卷积输入通道 | [DeepRx作者稿](https://arxiv.org/html/2005.01494#S3)，§III、Fig.2、Table I | 天线及实虚部可放通道，通过通道混合联合使用；仅有逐通道卷积不等于全通道混合。本文是OFDM两Rx接收机，不能把其BER结果当成本项目score性能依据 |
| conditional mean estimation；conditional covariance / 条件均值估计、条件协方差 | [Dytso–Poor–Shamai，TIT 2023](https://doi.org/10.1109/TIT.2022.3216012)，式(3)、§III Proposition 1式(17) | 用实坐标Gaussian恒等式核对score/Jacobian变换；展平的置换只重排二阶对角，真正酉混合只保证全trace不变，不能从角域对角恢复天线域全部逐坐标方差 |

“将16个复波束作为32个实输入通道”“二维FFT后展平”“交替两组二维卷积”均为操作描述，不设立新方法名称。本轮128个样本的reshape恒等式与MAC检查属于项目验证，不归为参考论文结果。

2026-10-13 波束通道网络落实：沿用Fesl §III-A的angular/beamspace domain与DeepRx §III的convolutional input channels。`ChannelScoreNetwork`为项目类名，不是论文方法名。[当前方案](history/experiments/full_power_channels_20261013/PLAN.md)采用全部32实通道混合及AFDM平面残差卷积。输入/输出稠密线性层吸收固定DFT的关系是项目线性代数推导，已用非零输出网络验证；它说明函数类等价，不声称Adam训练轨迹等价。数据中的`C_ml=mean(U_m conj(U_l))`明确称空间二阶矩，未中心化，不把非对角能量减少解释为独立性或物理自由度减少。5000训练样本的数值来自[本地诊断](../docs/history/results/full_power_channels_20261013/REPRESENTATION.json)，并非论文实验结果。

2026-10-14 强噪声 score 改进[定向调研](../references/low_snr_score_20261014/REPORT.md)：EDM、Min-SNR、条件均值及后验矩沿用上表已核对条目，补充以下原词。

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Single-Step SNR-informed Denoiser / 单步 SNR 条件去噪器 | [Strasser–Bäro–Utschick，2025作者稿v1](https://arxiv.org/html/2509.07839v1)，§IV-B、式(10)–(12)、Algorithm 3；§V-F/G；arXiv元数据注明在WSA 2025报告 | 完整酉导频、单载波MIMO的单步去噪先例；文中单步性能不逊于或优于多步的实验不能直接成为AFDM JADCE结论。说明单步本身不是强噪声失败的充分解释 |
| effective noise；colored Gaussian noise；D-VDAMP / 有效噪声；有色Gaussian噪声；去噪型VDAMP | [Metzler–Wetzstein，2020作者稿](https://arxiv.org/html/2010.13211)，§1–2、Algorithm 1 | 为结构化测量下实际查询与AWGN的差异提供方法依据；MRI中的Fourier/wavelet条件不能直接套给AFDM。项目观测到的输入列误差二阶矩含偏差，不能直接称为纯噪声协方差，也未实现D-VDAMP |

2026-10-14 参数化对照执行：EDM 沿用 Karras 等 NeurIPS 2022 §5 式(7)–(8) 的 preconditioning，见上述已有条目。项目仅使用 c_in、c_skip、c_out，保留旧 DSM 权重；实坐标 nu=v/2，tau²取训练先验的实坐标二阶矩。固定 v 专门训练是实验条件描述，不冠以新方法名称。计划见 [配对训练](../docs/history/experiments/low_snr_parameterization_20261014/PLAN.md)。

2026-10-14 用户功率一致性核查：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Uplink power control / 上行功率控制 | 3GPP TR 38.821 V16.0.0 §6.2.2，印刷页62（PDF索引61），https://atisorg.s3.amazonaws.com/archive/3gpp-documents/Rel16/ATIS.3GPP.38.821.V1600.pdf | 该研究报告讨论NTN上行功控，并认为可使用Rel-15方案；不证明所有终端严格等接收功率，更不证明无GNSS场景能精确补偿 |
| downlink pathloss estimate / 下行路径损耗估计 | ETSI TS 138 213 V16.11.0，§7.1.1，pp.17–21，p.21给出referenceSignalPower减filtered RSRP；§7.4，pp.32–33给出PRACH功率控制，https://www.etsi.org/deliver/etsi_ts/138200_138299/138213/16.11.00_60/ts_138213v161100p.pdf | 参考信号测量是慢变功率补偿的信息来源，不要求读取真实瞬时信道范数；无GNSS与无下行测量是不同约束。本项目目前只有LARGE_SCALE_COMPENSATED=True假设，没有实现标准功控过程 |

“等发射功率”“补偿后平均功率一致”“逐实现信道范数相等”用于区分不同数学条件，不作新算法名称。当前生成器使用相同导频能量、共同TDL路径期望功率，并保留独立小尺度衰落，省略用户相关的大尺度幅度因子；配置中的大尺度补偿假设不等于实现了逐用户功率补偿。对小尺度衰落取期望的信道能量一致，与固定场景接收能量一致是不同条件，推导及口径见 references/power_control_scope_20261014/NOTE.md。几何损耗量级检查见 references/power_control_scope_20261014/GEOMETRY_CHECK.json，仅计算距离引起的自由空间损耗差，不含天线方向图、遮挡和功控误差。

2026-10-14 卫星 GFRA 场景对照：六篇 GFRA 与一篇相邻 AFDM CE 的来源、仿真条件及差异见 [文献与代码综合核查](../references/satellite_gfra_audit_20261014/SYNTHESIS.md)。

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
配置、公开输入和验证范围见 [PROPOSED_UNKNOWN_PHASE.md](PROPOSED_UNKNOWN_PHASE.md)。

2026-10-15 Shen 相位学习适配核查：

| 原词或忠实译名 | 原文定位 | 本项目使用范围 |
|---|---|---|
| expectation-maximization (EM)；phase rotation / 期望最大化；相位旋转 | [Shen v1](https://arxiv.org/html/2412.20806v1#S3.SS3)，§III-C，式(47)–(52)，PDF p.9；Algorithm 1，p.10；正式发表 DOI 10.1109/TWC.2025.3525738 | 借鉴后验均值、方差驱动相位更新并重建测量矩阵的思路。现有 Proposed 使用学习近似后验，不自动继承精确 EM 的单调性结论。 |
| projected onto the unit circle / 投影到单位圆 | 同文式(53)–(54)及相邻说明，PDF p.9 | 原文先解无约束线性方程再逐元素归一化，属于近似更新。本文保留 exp(jq beta_k) 跨帧关系的目标和梯度另行推导；未把它命名为 Shen 原算法，未宣称投影是一般单位模问题的精确解。 |

对应推导、方差项适用条件和合成数值检查见 [Proposed 未知相位说明](PROPOSED_UNKNOWN_PHASE.md#shen-2025-相位学习的适配核查2026-10-15)。后续已实现保留 exp(jq beta_k) 约束的相位更新，入口为 `configs/proposed_iterative_phase.json`，同十场景 NMSE/AER 比较见 [实现验证](../docs/history/results/shen_phase_update_20261015/evaluation/REPORT.md)。这是借鉴原文目标的 AFDM 适配，并非 Shen OTFS 算法复现；当前六方法比较仍采用原两阶段相位配置。

2026-10-15 GAMP-SBL / off-grid SBL 后验相位更新：继续采用上述 Shen §III-C 式(47)–(54)的“phase rotation”和“expectation-maximization”含义作为参考。项目实际操作称为“后验相位更新”，完整目标、Gaussian 协方差项及 exp(jq beta_k) 约束见 [BASELINE_PHASE.md](BASELINE_PHASE.md)。GAMP 的对角方差项在单位模约束下为常数；SBL 的跨用户协方差项保留。这里的逐用户一维搜索、圆周插值和一次更新预算是项目明确写出的操作，并非新算法名称或 Shen 原文的闭式解。不得由固定后验目标下降推出整体精确 EM 收敛。

2026-10-14 连续信道与Huang设定专项核对：

| 原词或忠实译名 | 原文定位 | 当前使用 |
|---|---|---|
| continuous-time waveform、frequency wrapping、complex-envelope discontinuity / 连续时间波形、频率折叠、复包络不连续 | [Bemani博士论文](https://www.eurecom.eu/publication/7447/download/comsys-publi-7447.pdf)，§3.1.1式(3.2)–(3.10)、§3.2式(3.14)，印刷pp23–29；[Cao–Shao预印本](https://arxiv.org/html/2609.07480v1)，§II-A式(1)–(3)、Proposition1 | 用于核对当前分数时延及多周期CPP的模拟解释；整数样点等价不能推出带限DAC输出等价。项目相位导数与跳变诊断见[信道专项](../docs/history/results/implementation_audit_20261014/CHANNEL_MODEL_REVIEW.md)，未采用预印本的新波形替换当前生成器。 |

2026-10-14 线性查询误差处理核查：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| de-correlated linear estimator、divergence-free estimator / 去相关线性估计器、无散度估计器 | [Ma–Ping，Orthogonal AMP v3](https://arxiv.org/html/1602.06509v3#S3)，§III-A Definition 1后式(14)、§III-B Definition 2及式(17)–(18)、§III-E | 当前线性更新已满足迹归一化，但这一事实不推出有限AFDM查询是独立AWGN；需配套非线性估计条件，并核查误差分布。详见[本轮报告](../docs/history/results/proposed_speed_20261014/WHITENING_ASSESSMENT.md) |
| right-rotationally invariant random matrix、non-separable denoiser / 右旋转不变随机矩阵、非可分去噪器 | [Fletcher–Pandit–Rangan–Sarkar–Schniter，JSTAT 2019正式作者全文](https://phil-schniter.web.app/pdf/jstat19.pdf)，§3–4、Theorem 1；前身发表于NeurIPS 2018 | 高维VAMP分析的假设；不能仅凭基础DFT导频行正交，就认为重复块AFDM测量算子符合该随机矩阵模型 |

“按误差二阶矩补加Gaussian扰动”是上述报告中的直接协方差加法构造，不是既有算法名称。真实空间误差只用于明确标注的oracle诊断；不能把样本二阶矩等于标量阵写成已获得与信道独立的Gaussian噪声。

2026-10-14 空间协方差接收机候选：covariance shrinkage（协方差收缩）采用 [Chen–Wiesel–Eldar–Hero，作者稿](https://arxiv.org/pdf/0907.4698) §II式(3)–(4)、PDF p.4的标量单位阵混合形式。本项目先从接收二阶矩中减去公开热噪声，再投影正半定并固定混合10%；不是原文OAS/RBLW，也不主张其最优性。逐用户矩阵Gaussian更新、块平均及额外扰动按[实现公式](history/experiments/proposed_spatial_feedback_20261014/ALGORITHM.md)直接描述，不另造方法名。

2026-10-14 L-DAMP 原稿与作者训练代码复核，详见[对照报告](../docs/history/results/ldamp_paper_audit_20261014/REPORT.md)：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| denoiser-by-denoiser training / 分别训练各去噪器 | [Metzler 等作者稿 v4](../references/ldamp_review_20261014/metzler2017_learned_damp.pdf)，§3，PDF p.5；§4.2，p.7 | 按噪声区间训练 AWGN 去噪器，再在推断时选择网络，是原文训练选项。最优性论述依赖该文条件；不自动适用于本项目多用户、重复观测算子和相关误差 |
| state evolution / 状态演化 | 同上，§4.1，Finding 1，PDF pp.6–7 | 该文列出独立随机矩阵、Gaussian 测量噪声及 Lipschitz 去噪器等条件。本项目矩阵重排为 I⊗A，不能仅由 AMP 形式相同宣称满足这些条件 |
| covariance matrix / 协方差矩阵 | [Chen–Sohrabi–Yu，ICASSP 2018](https://www.comm.utoronto.ca/~weiyu/2018_ICASSP_massive_connectivity.pdf)，§3.1，PDF p.2，式(2)–(4)及式(6)前的简化条件 | 该文保留多测量向量误差协方差，并在特定先验下简化为标量。本项目诊断是对中心化误差计算经验协方差及其非对角能量占比；后者为明示公式的统计量，不设立新方法名，不据此声称已推导出当前 CNN 的矩阵校正 |
| residual learning / 残差学习 | [Zhang 等 DnCNN 作者稿 v1](../references/ldamp_review_20261014/zhang2017_dncnn.pdf)，§III-B，式(1)，PDF p.3；§IV-A，PDF p.6 | D(q)=q−F(q) 下清洁输出 MSE 与噪声预测 MSE 代数等价。He 信道版的 Adam、噪声分段和初始化另按其代码记录，不混同 DnCNN 原文的 SGD 配方 |

2026-10-14 各轮一致的接收机规则调研，详见[综合报告与候选公式](../references/uniform_receiver_literature_20261014/REPORT.md)：

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
| effective noise / 有效噪声；equivalent noise / 等效噪声 | [Metzler 等作者稿](../references/ldamp_review_20261014/metzler2017_learned_damp.pdf)，§2.1，PDF p.4，式(3)后 νᵗ 的定义；[He 等作者稿](../references/ldamp_review_20261014/he2018_ldamp.pdf)，§III-A，PDF p.2，式(6) | 指去噪输入减去真实目标的误差，包含残余干扰；不等于观测中的物理接收噪声 W。不同波束有效误差方差的训练适配不改变 W∼CN(0,σ²I)。独立 Gaussian 训练扰动仅是对有效误差的近似。 |

2026-10-14 L-DAMP 完整实现开发补充：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Wirtinger derivatives；Jacobian matrices / Wirtinger 导数；Jacobian 矩阵 | [Kunde–Mirri–Chamberland–Paolini，2026预印本 v1](../references/ldamp_review_20261014/kunde2026_complex_amp.pdf)，§III-C，PDF p.12，式(18)–(21) | 为复数非可分去噪的矩阵校正提供参考；项目用显式输入/输出下标定义部分迹并通过独立坐标差分核验，不沿用可能含歧义的转置简写。原文独立圆对称复 Gaussian 测量矩阵条件不覆盖当前 AFDM 导频；未声称理论收敛保证。 |

“双边逆 DAFT、按循环滞后重排、沿时间做 DFT”及“逐波束共享两通道 DnCNN”是代码操作描述。DAFT 定义沿用 Huang §II、PDF p.2 式(1)前与式(4)后；固定角域 DFT 沿用上述 Fesl §III-A、Wei–Hu–Dai §II-A。所有系数保留，不把变换系数命名为真实连续路径参数。MatConvNet 保存的 BN moments 为均值和含 epsilon 的标准差，按[官方接口定义](https://www.vlfeat.org/matconvnet/mfiles/vl_nnbnorm/)载入；训练库重估运行统计是明示适配，不能说成原作者训练轨迹复现。见[开发报告](../results/ldamp_implementation_20261014/REFERENCE_REPORT.md)。

2026-10-14 各轮一致推断规则的配对实现与试验：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| damped denoising VAMP (DD-VAMP)；damping / 带阻尼的去噪型 VAMP；阻尼 | [Sarkar–Ahmad–Schniter，ICASSP 2021 作者稿 v1](https://arxiv.org/abs/2010.11321)，§3.1、Algorithm 1 第10、15–16行，PDF p.3；[本地原文](../references/uniform_receiver_literature_20261014/phase2_vamp/ddvamp.txt) | 灵敏度在平方根域阻尼，精度在逆平方根域阻尼。本项目取固定权重、完整联合映射 pF 的复探针差分、沿用原主线的灵敏度截断范围；这是 AFDM 接收机适配，不能宣称复现论文 MRI 性能或满足其随机矩阵条件。权重为新值权重，越大意味着阻尼越弱。 |
| plug-and-play ADMM (PnP-ADMM) / 即插即用 ADMM | 同上，§2.1 式(3a)–(3c)、§2.2，PDF p.2 | 保留高斯数据项更新及对偶递推，以旧联合去噪器代替近端映射。本项目将固定查询方差与线性正则化参数对应，并只试两个由公开热噪声和导频能量决定的参数；不声称已穷尽 PnP 参数或存在凸目标、收敛保证。 |

实现和选择记录见 [配对试验协议](../docs/history/experiments/proposed_uniform_inference_20261014/PROTOCOL.md) 与 [冻结的新场景设置](../docs/history/results/proposed_uniform_inference_20261014/SELECTION.json)。FIRE 的二阶网络方差替代、固定计算预算和活动读出均为项目实验选择；算法名称之后明确写出这些改动，不作为文献原算法的完整复现。

2026-10-14 旧网络计算与局部导数的优化判断，见[诊断报告](../docs/history/results/proposed_optimization_20261014/REPORT.md)：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Jacobian of the conditional expectation；conditional variance / 条件期望的Jacobian；条件方差 | [Dytso–Poor–Shamai作者稿](https://arxiv.org/pdf/2104.01883)，§IV Proposition 1式(22)、Corollary 1式(23)，PDF pp.5–6 | 在实噪声协方差为(v/2)I时，精确后验均值满足J=2C/v。项目比较的是3个探针、3个步长下的归一化迹估计；平均为正不等于完整Jacobian正半定。pF的两项导数按乘积公式直接分解，不设立新算法名称。 |
| second-order score matching / 二阶得分匹配 | [Cai v2](https://arxiv.org/html/2506.00581v2#S4.SS3)，§IV-C式(51)–(54) | 有限冻结一阶网络下，当前迹损失的最优读出对应以该均值为中心的条件误差风险。风险与真实协方差及实际Jacobian的区别按项目THEORY.md附录A代数解释，不将其等同。复用一阶特征输出标量风险是尚未训练的项目建议。 |
| gradient step denoiser；proximal gradient step denoiser / 梯度步去噪器；近端梯度步去噪器 | [Hurault–Leclaire–Papadakis，ICML 2022](https://proceedings.mlr.press/v162/hurault22a/hurault22a.pdf)，§3式(4)–(5)、Proposition 3.1，PDF p.3 | 标量势函数梯度给出对称Jacobian，命题的收缩条件进一步保证正定。这里只作为改变训练结构的文献先例，未实现该架构，也不将其PnP收敛结论移用于AFDM消息传递。随机方向负响应惩罚属于明示公式的项目建议，不能称为上述理论保证。 |

2026-10-14 旧网络的近似 AWGN 查询与一般去噪器反馈调研，见[详细分析](../references/awgn_linear_design_20261014/REPORT.md)和[来源定位](../references/awgn_linear_design_20261014/SOURCE_NOTES.md)：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| denoising-based OAMP (D-OAMP)；divergence-free denoiser / 基于去噪的 OAMP；无散度去噪器 | [Xue–Ma–Yuan，2016 作者稿 v1](https://arxiv.org/html/1610.05991v1)，Algorithm 2，PDF p.2；§3.3.1 式(7)–(8)，p.3 | 一般联合去噪器的散度扣除有来源；本项目复数 MMV 适配、旧网络活动读出和独立误差功率估计尚未完成接收机验证。经验散度和增益的数据依赖意味着有限维无散度性质只是近似，不保证当前 AFDM 误差为 AWGN。 |
| Stein’s unbiased risk estimate (SURE) / Stein 无偏风险估计 | 同上 §3.3.2 式(10)–(11)，PDF p.3 | 基于风险的增益选择；按本项目复数功率 v 和 2d 维实坐标重新推导归一化，式(14)中的功率为 ‖D−R‖²/d+2vα−v。无偏性需要正确 Gaussian 查询及相应正则条件，数据驱动调参还存在有限样本误差，不能用它自证输入已是 AWGN。 |
| state evolution；covariance matrix / 状态演化；协方差矩阵 | [Liu–Yu Part I 作者稿 v2](https://arxiv.org/html/1706.06438v2)，§III-B 式(14)–(17)，PDF pp.4–5；§III-D Theorem 1，p.6；[Kunde 等2026预印本](https://arxiv.org/html/2604.21115v1)，§III-C 式(18)–(21)、Remark 14，PDF p.12 | MMV 可以具有矩阵状态；重复 A 不自动排除 MMV 理论，但基础矩阵、信号各向同性和去噪器条件必须核对。本项目 256 个共同观测特征不能未经推导就简化成单个误差方差。 |
| algebraic estimator；polynomial estimator of divergence / 散度的代数估计器；多项式估计器 | [Skuratovs–Davies，TIT 2023 机构接收稿](https://www.pure.ed.ac.uk/ws/portalfiles/portal/361481237/Divergence_Estimation_in_MP_algorithms_reviewed_second_time_Final.pdf)，含封面 PDF p.4 Assumptions 1–3，p.6 Theorem 2 式(37)，p.8 Theorem 3，p.9 §III-E | 可减少额外网络调用的后续候选；其正交性、大系统和历史条件尚未在本项目成立，未替换当前导数估计，也不将经验选根规则改称严格保证。 |

本轮用户方形导频块的逆矩阵噪声倍率、每用户酉导频的自身响应与干扰协方差、负散度下的一般风险关系均为报告中明示的项目代数推导，不另造算法名称；未变更主线算法或权重。

2026-10-15：上述D-OAMP项目适配现已完成四条件开发试验；三类导频下均在第二轮超出网络支持范围，不能作为已成立的AFDM状态演化。每轮空间协方差、迹归一化及Gaussian扰动补齐按明确公式实施，统计改善但完整性能不通过，详见[顺序实施报告](../docs/history/results/proposed_awgn_20261014/REPORT.md)。该组合只描述具体操作，不赋予新的文献算法名称。

后续有色噪声条件训练设计沿用D-GEC §III-B、式(41)，印刷pp.535–536的corr+corr含义：有色噪声观测与同统计独立噪声样本同时输入；有限噪声样本不等于提供精确协方差。固定协方差C下，实坐标后验均值与Jacobian关系沿用Dytso–Poor–Shamai Proposition 1式(22)，并显式规定Jacobian第(i,j)项为∂D_i/∂r_j。矩阵加权条件去噪损失、隐式Gaussian误差生成器是[NEXT_DESIGN.md](history/results/proposed_awgn_20261014/NEXT_DESIGN.md)中的项目推导，尚未实施，不冠以既有方法名称。

2026-10-15 L-DAMP 联合去噪开发：noise level map（噪声水平图）沿用 Zhang–Zuo–Zhang FFDNet §III-A/B/E（https://arxiv.org/html/1710.04026v2#S3.SS2）。这里为每波束公开有效误差方差构造16个常量输入通道，并不复现 FFDNet 的子图下采样结构。network preconditioning 沿用上述 Karras §5 式(7)–(8)、Table 1 的名称；逐波束复数二阶矩到实坐标的尺度推广、32通道 DnCNN 和联合矩阵递推是项目适配，具体公式及受控比较见 `docs/history/results/ldamp_complete_20261015/PLAN.json`。所有候选仍属开发，不代表已安装或已获得独立接收机性能。

同日的后续对照保留上述 DnCNN residual learning 的名称：在冻结逐波束网络的输出上学习联合残差，属于项目自行定义的复合函数，不称作 He 原网络。残差分别按训练二阶矩或公开噪声标准差缩放，损失分母分别在 `PLAN.json` 中明写，未另造方法名称。整个函数参与 Wirtinger 部分迹；分开计算两支路后求和是 Jacobian 线性关系，不能省去“原网络输出作为新网络输入”这条链式导数。实际误差与同算子 Gaussian 对照、训练及数值证据见 `docs/history/results/ldamp_complete_20261015/REVIEW.md`。

2026-10-15 校正项数值检查：沿用 He §III-A 式(7)–(8) 的 Monte Carlo 导数估计及 Kunde §III-C 式(18)–(21) 的矩阵 Jacobian 约定。直接估计 `ZB`、在每用户 `N` 行上使用完整正交方向的安排属于项目推导，未包装为已有论文算法名称；公式、独立数值核验与适用条件见 [PROJECTED_TRACE_DERIVATION](../experiments/ldamp_complete_20261015/PROJECTED_TRACE_DERIVATION.md)。完整 `N` 个方向仅消除此处部分迹的抽样误差，不等于消除网络近似误差或证明 AFDM 状态演化。

2026-10-15 Proposed 协方差条件活动推断与矩阵反馈开发：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Gram–Schmidt orthogonalization (GSO)；orthogonal estimator / Gram–Schmidt 正交化；正交估计器 | [Cheng、Liu、Liang、Manton、Ping，OAMP-MMV 作者稿v1](https://arxiv.org/html/2304.08038v1#S3.SS6)，§III-F Definition 20、式(31)–(34)；§III-G Theorem 21 | 矩阵交叉协方差消除输入输出误差相关。项目仅聚合32维实空间特征，不等于消除全部用户、输入坐标或跨轮相关。§III-D Assumption 18 的 Haar 及 PIID-separable 条件未经本项目验证；§I-D也说明该文状态演化论述偏直观，不能援引为当前固定AFDM算子的严格保证。 |
| generalized SURE / 广义 Stein 无偏风险估计 | [Eldar，作者稿v2](https://arxiv.org/html/0804.3010v2#S5.SS1)，§III-B、§V-A式(39)–(43) | 支持已知协方差Gaussian观测下的风险及导数关系。项目通过完整相关Gaussian探针估计空间交叉矩阵；协方差由观测估计、系数由有限样本选择时无偏及正交性质只是近似。标量反馈增益另沿用已登记D-OAMP式(10)–(11)。 |

具体的实数化、每用户协方差边缘、完整相关探针及矩阵扣除公式见
[实验协议](../docs/history/experiments/proposed_colored_20261015/matrix_feedback/PROTOCOL.md)。
它们是有来源的操作与项目推导的组合，不为组合另设文献算法名；原 Proposed 保持冻结。

2026-10-15 完整协方差参与联合均值变换的开发：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Bernoulli–Gaussian distribution；MMSE denoiser / Bernoulli–Gaussian分布；最小均方误差去噪器 | [Liu–Yu作者稿v2](https://arxiv.org/html/1706.06438v2#S3.SS3)，§III-C式(19)–(22)，附录A Lemma 1式(57)–(61) | 作为已知Gaussian噪声协方差下的解析诊断。这里将用户4096维信道整体视为一个向量；Gaussian活动信道先验仅为对照近似，不宣称NTN信道具有该分布，也不新增主线baseline。 |
| network preconditioning / 网络预条件化 | [Karras等，NeurIPS 2022正式版](https://papers.neurips.cc/paper_files/paper/2022/file/a98846e9d9cc01cfb87eb694d946ce6b-Paper-Conference.pdf)，Table 1，p.3；§5式(7)–(8)，pp.8–9 | 原文以标量噪声方差设置输入、跳连、输出与损失尺度。项目明确推广为P=(βI+C)⁻¹/²、T=β(βI+C)⁻¹、B=[βC(βI+C)⁻¹]¹/²，D=Tr+Bf(Pr,C)。矩阵操作及联合活动先验是项目推导，不是原文的有色噪声定理。 |

本项目通过空间特征分解和逐空间模式的输入特征分解精确施加上述矩阵函数，沿用“特征分解”的通常含义，
不另造算法名称。具体训练范围、实复数尺度及总体损失最优解见
[实验协议](../docs/history/experiments/proposed_colored_20261015/preconditioned_joint/PROTOCOL.md)。

2026-10-15 训练信道二阶矩与受限线性响应核对：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| low-rank approximation；Karhunen–Loève transform；MSE floor / 低秩近似；Karhunen–Loève变换；均方误差下限 | [Edfors等，VTC 1996会议版作者全文](https://lucris.lub.lu.se/ws/portalfiles/portal/6289557/1056818.pdf)，§III-B式(6)–(9)、印刷p.925；§III-C式(10)–(11)、p.926（PDF pp.5–6） | 先验相关矩阵的特征向量及舍弃能量用于量化近似，不把路径数当作固定线性秩。本文献是1996会议版本，不能混写为1998期刊全文。项目用原50000个物理训练样本估计AFDM输出/输入二阶矩；V_kB_k=I的约束解、工作干扰加权和Gaussian协方差补齐另按显式公式推导，没有AFDM实际AWGN保证。 |

对应的统计范围、预定99%/99.9%能量阈值及全部支持失败记录见
[子空间核对协议](history/experiments/proposed_subspace_20261015/PROTOCOL.md)和
[加权解公式](../docs/history/experiments/proposed_subspace_20261015/WEIGHTED_PROTOCOL.md)。

2026-10-15 完整观测条件下的扩散查询核对：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Denoising Diffusion Restoration Models (DDRM)；Gaussian marginals / 高斯边缘分布 | [Kawar等，作者稿v2](https://arxiv.org/html/2201.11793v2#S3.SS2)，§3.2式(3)–(8)、Proposition 3.1；§3.3 Theorem 3.2；§5.1；[NeurIPS 2022出版记录](https://papers.neurips.cc/paper_files/paper/2022/hash/95504595b6169131b6ed6cd72eb05616-Abstract-Conference.html) | q的边缘对观测噪声积分且使用真实信号，不能据此宣称有限网络pθ的实际查询误差是AWGN。项目使用复数薄SVD、原first和activity的联合均值，以及32个连续噪声方差；这属于显式适配，不是原图像模型复现。反馈均值也没有AWGN保证。 |

适配范围和固定预算见[DDRM隔离协议](../docs/history/experiments/proposed_ddrm_20261015/PROTOCOL.md)。

2026-10-15 原闭环跨轮协方差与逐用户酉因子线性处理：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| damping、error covariance / 阻尼、误差协方差 | [Takeuchi作者稿v2](https://arxiv.org/html/2111.05522v2)，§III-C式(27)–(28)、§III-D式(44)–(45)，§IV-B Example 2式(63)–(78) | 两估计的有限数组MSE混合恒等式单独用于审计；以估计方差标签代入后可能不成立或为负，不冒充LM-OAMP实现，不用真值修改推断。 |
| polar decomposition、unitary polar factor / 极分解、酉极因子 | [Higham 1986作者机构全文](https://eprints.maths.manchester.ac.uk/694/1/high86p.pdf)，Theorem 1.1，§3.1 | 项目令A_k=U_kS_kV_kᴴ、W_k=gV_kU_kᴴ，以共同g归一化整体trace。逐用户热噪声协方差严格为σ²g²I；总误差的自身响应、干扰和历史项不据此成为AWGN。 |
| de-correlated linear estimator / 去相关线性估计器 | [Ma–Ping作者稿v3](https://arxiv.org/html/1602.06509v3)，§III-A式(12)–(14)，§III-I式(31) | 项目沿用迹归一化和工作功率公式，但逐用户极分解的拼接W不一定具有原文整体SVD滤波结构；不能仅凭trace条件继承OAMP的状态演化或误差独立性结论。 |

对应[跨轮诊断协议](history/experiments/proposed_temporal_20261015/PROTOCOL.md)与
[线性候选协议](history/experiments/proposed_polar_20261015/PROTOCOL.md)均保留原Proposed三网络和主线文件。

补充定位（2026-10-15）：Ma–Ping同一作者稿§III-D式(21)给出两端误差递推；
§III-E Assumptions 1–2区分线性查询的IID Gaussian要求与非线性反馈的IID及相对A/N独立要求，
后者没有另要求Gaussian；Appendix A说明非线性反馈误差一般可与信号相关。
项目所列完整协方差展开和逐用户白化热噪声的Cauchy–Schwarz下界是显式代数推导，
不是新命名算法或原论文的AFDM定理。推导和适用条件见
[隔离线性实验报告](../docs/history/results/proposed_polar_20261015/REPORT.md)。
其中V_kU_kᴴ严格说是A_kᴴ的酉极因子，即A_k的酉极因子的共轭转置；采用该方向是为了从观测映射回信道坐标。

2026-10-16，逐用户发射导频修改的补充定位：Higham同文§2.1式(2.2)、§2.2
Corollary 2.3（印刷pp.1161–1162，PDF pp.3–4）说明方阵的酉极因子是Frobenius
范数下的最近酉矩阵；满秩时唯一。本次对P_k=L_kΣ_kR_kᴴ取发射导频B_k=L_kR_kᴴ，
见配对验证协议（历史文件已清理，原路径：`experiments/proposed_pilot_polar_20261016/PROTOCOL.md`）及
[推导](../docs/history/experiments/proposed_pilot_polar_20261016/DERIVATION.md)。这里改变公开导频及其
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

逐用户功率保持、三维开关及有限差分均为[预定诊断设计](../docs/history/experiments/proposed_axis_control_20261015/PROTOCOL.md)，
不设立新的方法名称。Gaussian误差仍可能有色；该区分也见已登记D-GEC §III-B式(39)–(41)。

2026-10-15 原标量反馈下的每轮残差空间处理：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| singular value shrinkage；optimal shrinker for Frobenius loss / 奇异值收缩；Frobenius损失的最优收缩函数 | [Gavish–Donoho作者稿1405.7511v3](https://arxiv.org/pdf/1405.7511v3)，式(7)、PDF p.5；§2.1，p.8；§4，pp.13–15；[TIT 2017](https://doi.org/10.1109/TIT.2017.2653801) | 本项目对16×256复残差使用同一标量函数，再将所得残差估计的空间二阶矩用于工作协方差。原文实矩阵、大系统、低秩及独立白噪声前提不直接覆盖闭环残差；不称其为当前协方差或接收机的最优估计。 |

残差二阶矩减去已知热噪声后投影正半定、共享空间LMMSE、支持范围内Gaussian补齐及原标量反馈的组合，
按[协议中的公式](history/experiments/proposed_uniform_spatial_20261015/PROTOCOL.md)直接描述；
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
β/(2−β)方差因子均是显式线性代数推导，分别见[后续协议](../docs/history/experiments/proposed_uniform_spatial_20261015/ORDERED_PROTOCOL.md)
和[噪声参照设计](../docs/history/experiments/proposed_uniform_spatial_20261015/NOISE_REFERENCE_DESIGN.md)。
这些式子不消除未知的真实反馈误差与热噪声交叉项。

2026-10-15 实际当轮反馈映射及相关Gaussian交叉项：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| Monte Carlo divergence；divergence-free denoiser / Monte Carlo散度；无散度去噪器 | [D-OAMP作者稿](https://arxiv.org/html/1610.05991v1)，§2.1式(2)–(3)，§3.3式(7)–(11) | 中心差分作用于固定进入本轮之前的site历史后的实际Denoiser映射，包含site接受分支与当前分类器；不是整个迭代历史的总导数。双向阻尼和空间处理仍为项目适配；每轮额外网络调用全部计入成本。 |
| SURE for Correlated Gaussian Noise / 相关Gaussian噪声的SURE | [Raphan–Simoncelli，作者机构全文](https://www.cns.nyu.edu/pub/eero/raphan08-preprint.pdf)，§III-A式(7)–(10)，印刷p.1345（PDF p.4）；§III-B式(11)–(13) | 相关输入的Stein交叉项涉及协方差加权Jacobian迹，不能直接以v乘普通归一化迹替代。复坐标归一化及AFDM工作协方差块为直接推导；不据此宣称实际闭环误差为Gaussian或工作协方差是真实协方差。 |

对应[完整接收机开发协议](../docs/history/experiments/proposed_uniform_spatial_20261015/feedback_receiver/PROTOCOL.md)
与[相关输入交叉项推导](../docs/history/experiments/proposed_uniform_spatial_20261015/feedback_receiver/COLORED_STEIN_NOTE.md)。

2026-10-15后续[固定导数探针对照](../docs/history/experiments/proposed_uniform_spatial_20261015/feedback_probe_control/PROTOCOL.md)
只改变Monte Carlo方向在各轮之间是否重新抽取，不为此设立新算法名称，不声称继承状态演化保证。
[输入维滤波与空间查询的组合推导](../docs/history/experiments/proposed_uniform_spatial_20261015/input_filter/DESIGN.md)
沿用上述奇异值、迹归一化、极分解和协方差术语；逐用户迹/功率约束及空间部分迹均为显式代数推导。
该阶段纯公开算子检查不等同于接收机性能实验。

后续[组合接收机确认](../docs/history/results/proposed_uniform_spatial_20261015/input_filter/confirmation/REPORT.md)
已完成八个独立物理场景的48条运行。逐用户滤波与每轮空间处理仍按显式公式描述，未建立新算法名称。
查询的协方差偏离下降、点性能门槛通过不等于独立Gaussian成立；反馈的空间颜色及工作方差偏差仍保留。
物理场景配对bootstrap区间只作小样本描述，不能将预定容差的点估计检查称为已经证明总体非劣。

2026-10-15 历史协方差与原始观测风险：

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| orthogonality；asymptotic IID Gaussianity / 正交性；渐近IID Gaussian性质 | [Memory AMP作者稿v7](https://arxiv.org/pdf/2012.10861v7)，§III式(20)、(24)、(30)、(32)，PDF pp.6–8 | 区分状态演化中的Gaussian等效变量、原坐标实际反馈及与全部历史输入误差的正交关系；不能将摘要简称扩大为非线性反馈必然独立于信号。匹配BPSK后验均值反例为项目解析核对，不是AFDM实验。 |
| Stein's unbiased risk estimate (SURE) / Stein无偏风险估计 | [Nobel、Candès、Boyd，TSP 2023作者机构全文](https://web.stanford.edu/~boyd/papers/pdf/sure_tractable_eval.pdf)，§I-A式(1)、§I-B，p.4330 | 对Y↦AF_t(Y)的公式目标是观测均值AH的风险。复坐标因子、历史交叉风险和完整历史依赖按显式公式展开；该文凸优化算法与弱可微结论不能直接套给当前有分支的神经接收机。 |

[本轮报告](history/results/proposed_memory_requirements_20261015/REPORT.md)保留残差协方差偏差的三项恒等式分解，
以及归一化权重下共同噪声扣除项为常数的代数核对，不为此创造新的算法名称。
四条原样重放与离线历史融合不等于完整Memory AMP实现；原始观测的完整映射求导仍属待验证设计。

2026-10-15 原始观测完整响应与补噪表示核对：

[固定轮数协议](history/experiments/proposed_measurement_response_20261015/PROTOCOL.md)沿用上述SURE术语。
有限差分对固定轮数的完整Y→AF_t映射求导，包含历史依赖；不包含自适应停止时间的导数。
由于分支与有限探针，该核对不等于证明弱可微或无偏风险估计成立。

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| positive semidefinite square root / 半正定平方根 | [Higham，Functions of Matrices，2014作者机构书章](https://eprints.maths.manchester.ac.uk/2109/1/fm2_final_njh.pdf)，§17.5 Fact 2，印刷p.17-7（PDF第8页） | 仅在已保存补噪协方差上离线比较U diag(sqrt(d))与唯一Hermitian半正定平方根U diag(sqrt(d)) U^H。相同协方差对应相同条件Gaussian分布，但固定随机数下路径可不同；该矩阵级检查不构成新接收机性能实验。 |

上述半正定平方根亦已核对期刊原文：[Higham–Schreiber，1990](https://eprints.maths.manchester.ac.uk/340/1/0911038.pdf)，
§1 p.648（唯一Hermitian半正定平方根）、§2 p.651（计算与特征分解形式）。
[完整响应结果](history/results/proposed_measurement_response_20261015/REPORT.md)已完成36条重放，
末轮交叉项解释与早期差分不稳定分别报告；半正定平方根目前仅作离线矩阵对照，尚未进入接收机。

后续进展（2026-10-15）：半正定平方根已进入独立数值映射的响应实验，
原路径复现1/4通过与自身严格复现4/4通过分别保留，原Proposed未替换。
空间矩阵扩展继续采用Raphan–Simoncelli §III-A式(7)–(10)、p.1345的Gaussian积分分部依据；
复数Jacobian的天线块部分迹、平滑反馈及逐样本Q+R分解是项目公式，
不是原论文已有算法名称。证据见[阶段报告](../docs/history/results/proposed_measurement_root_20261015/self_response/REPORT.md)。

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| nearest symmetric positive semidefinite matrix；positive approximant / 最近对称半正定矩阵；半正定近似 | [Higham 1988作者全文](https://nhigham.com/wp-content/uploads/2023/10/high88d.pdf)，§2 Theorem 2.1、式(2.1)–(2.2)，pp.105–106；§1 p.104说明可扩展到复矩阵 | 用于后续Hermitian矩阵正部投影的优化依据，不解释为当前统计模型最优。给定估计迹或各向同性约束为项目显式优化推导；本阶段未将这些候选接入推断。 |

上述三种矩阵约束的[全轮离线比较](../docs/history/results/proposed_covariance_constraints_20261015/REPORT.md)
已经完成；合法性改善未能稳定恢复方向信息，未接入推断。
[实际查询分解](history/results/proposed_query_terms_20261015/REPORT.md)沿用Ma–Ping §III-D式(21)
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
| likelihood-annealed Langevin dynamics / 似然退火 Langevin 动力学 | [Huang 2026 本地全文](../references/huang2026_prior_agnostic_afdm_diffusion.pdf)，§III-A–B 式(6)–(10)，p.2951；Algorithm 1、§IV，p.2952；[DOI](https://doi.org/10.1109/LWC.2026.3689601) | 直接结合原始观测残差的似然梯度、学习的先验 score 和随机扰动；Algorithm 1 使用 1/(σ_z²+σ_i²) 退火权重，并衰减步长。这不是线性模块误差的白化或协方差估计，不依赖把当前状态解释成真值加独立 AWGN 的局部后验均值接口，但有限噪声层级的似然近似、网络误差和有限迭代仍存在。式(10)及 Algorithm 1 的残差符号问题沿用本页已有核查，不能直接照抄。§IV 的 L-DAMP baseline 引用 He [23]，正文未给出专门处理有色/非 Gaussian 伪观测误差的修正，不能从其曲线推断存在这种修正。 |

本次只核对原文、现有代码与术语边界，未训练网络、运行接收机比较或修改推断算法。

## 冻结 score 与活动分类器的复数矩阵 AMP（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| vector AMP algorithm；state evolution / 向量 AMP 算法；状态演化 | [Liu–Yu，作者稿 v2](https://arxiv.org/html/1706.06438v2#S3.SS2)，§III-B 式(14)–(17)，§III-D | 多测量向量共享感知矩阵时传播特征协方差；不能从矩阵 AMP 推出本项目相关信道的误差协方差自动为标量阵。 |
| Complex Approximate Message Passing with Non-separable Denoising；Wirtinger derivatives / 非可分去噪的复数近似消息传递；Wirtinger 导数 | [Kunde 等，2026 预印本 v1](https://arxiv.org/html/2604.21115v1#S3.SS3)，§III-C 式(18)–(21)、Remark 14，Appendix B；§III-B Assumption 8 | 完整联合去噪映射的复 Jacobian 部分迹与复矩阵校正。引用其 iid proper-complex Gaussian 及函数正则条件；当前有限 AFDM 不宣称满足其状态演化定理。 |
| Onsager correction；Monte Carlo approximation / Onsager 校正；Monte Carlo 近似 | [He 等，作者稿 v2](https://arxiv.org/html/1802.01290v2#S3.SS1)，§III-A 式(4)–(8) | 新循环保留完整活动概率与 score 均值的依赖；四次中心差分和复矩阵部分迹是按明确索引推导的实现，有限步长与有限探针误差均须报告。 |

本项目的具体重排、共同尺度变换、活动概率乘均值的完整链式导数、随机相位 DFT
探针及匹配尺寸 AWGN 参照均在 [完整推导](PROPOSED_AMP.md) 中直接给出公式。
`score_amp` 是软件入口标识，不作为新造的学术算法名称；原 Proposed 保持独立。
运行条件、失败与代价见 [本次结果](../docs/history/results/proposed_amp_20261015/REPORT.md)。

## AMP首轮失配与后续稳定性的区分（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| state evolution；covariance matrix / 状态演化；协方差矩阵 | [Liu–Yu作者稿v2](https://arxiv.org/html/1706.06438v2#S3.SS2)，§III-B式(16)–(18)，§III-D Theorem 1式(23) | 一般MMV等效误差保留特征协方差；该文的标量阵简化使用各向同性Rayleigh先验与匹配MMSE等条件。不能将Onsager称为任意天线相关性的白化算子。 |
| Denoising Generalized Expectation-Consistent Approximation (D-GEC)；colored-noise-aware denoiser / 基于去噪的广义期望一致近似；适配有色噪声的去噪器 | [Shastri等2022期刊作者全文](https://phil-schniter.web.app/pdf/jsait22_dgec.pdf)，§III-A Algorithms 2–3、式(31)、(36)–(37)，pp.534–535；§III-B式(38)–(40) | 借鉴分组误差统计与匹配有色噪声的学习接口。MRI的分组模型和corr+corr训练并非本项目已完成方案；式(36)为经验误差模型。16×16天线协方差条件score与活动分类器按显式密度公式提出，不冠以新算法名。 |
| Damped Denoising Vector AMP (DD-VAMP)；denoiser sensitivity / 带阻尼的基于去噪的向量AMP；去噪器灵敏度 | [Sarkar等2021作者稿](https://arxiv.org/pdf/2010.11321v1)，§3.1 Algorithm 1、式(9)–(14)，p.3；§3.2初始化 | 为一致阻尼、Monte Carlo灵敏度波动及初始化消融提供依据，不将其标量正精度的平方根操作直接用于一般复数矩阵，也不宣称阻尼恢复AFDM查询白性或保证当前神经网络迭代收敛。 |

[后续诊断](history/results/proposed_amp_20261015/diagnosis_followup/REPORT.md)保留了40次真值辅助单次网络对照及旧Proposed首轮同样全判活跃、后续恢复的事实。
天线相关性足以复现这组固定输入的网络异常，不等于识别了完整循环失败的唯一原因。
实坐标协方差Tweedie式、白化改变先验的反例及残差天线二阶矩均以显式公式陈述；候选修改尚未训练或接入接收机。

## AMP阻尼与历史偏导（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| functions of all previous iterates；debiasing coefficients / 依赖全部历史迭代量的函数；去偏系数 | [Fan作者稿v5](https://arxiv.org/html/2008.11892v5#S5)，§5式(5.3)–(5.8)、(5.12)，Remark 5.1 | iid Gaussian特例的历史Onsager系数由对应历史输入的偏导平均给出。固定几何阻尼权重及其紧凑递推为本项目显式展开；不把原文旋转不变模型的全部谱校正替换成当前有限AFDM的保证。 |
| Wirtinger derivatives；matrix extension / Wirtinger导数；矩阵扩展 | [Kunde等2026预印本v1](https://arxiv.org/html/2604.21115v1#S3.SS3)，§III-C式(18)–(21)、Remark 14，Appendix B | 固定有限轮数的历史列扩展用于核对非可分复矩阵部分迹的块位置。实际仍用8探针有限差分；条件噪声标签冻结不等于已证明其自适应规则满足状态演化条件。 |
| full-memory AMP / 全历史AMP | [Rossetti–Nazer–Reeves作者稿v2](https://arxiv.org/html/2405.08225v2#A1)，Appendix A，Theorem 5式(59)–(62)，A.2.1式(70)–(72) | 以矩阵列表示固定有限轮数的历史，为本次独立代数核验提供依据。原文此定理使用GOE随机矩阵；不据此声称当前矩形复数AFDM实现满足其统计定理，也不将当前实现命名为OpAMP。 |

阻尼权重、历史校正、含交叉项的方差与确定性固定点谱均在[推导](PROPOSED_AMP_DAMPING.md)按公式直接说明。
`score_amp_damped`为独立软件入口；没有把该递推包装成DD-VAMP或新增学术名称。
原Proposed及无阻尼score_amp保留；新版本的概率输出仍取当前原始分类器，主要信道输出为阻尼状态。


## AMP 查询阻尼与双重历史权重（2026-10-15）

沿用上节的 functions of all previous iterates、debiasing coefficients 和 Wirtinger derivatives，
不新增学术算法名称。依据仍为 [Fan v5](https://arxiv.org/html/2008.11892v5#S5)
§5式(5.3)–(5.8)、(5.12)、Remark 5.1，以及
[Kunde v1](https://arxiv.org/html/2604.21115v1#S3.SS3) §III-C式(18)–(21)、Remark 14、Appendix B。
查询/反馈两侧阻尼的经验动机参照 [Cai v2](https://arxiv.org/html/2506.00581v2#S5.SS2.SSS1)
§V-B1式(57)–(58)，但本实现并未照搬其方差递推。

[本次推导](PROPOSED_AMP_QUERY_DAMPING.md) Q1–Q9显式展开查询权重和输出权重，
校正项用同查询权重混合的残差乘当前完整联合映射的复Jacobian部分迹。
混合残差能量包含跨轮交叉项；其等于实际查询误差功率需要额外统计条件，
有限AFDM下不能由代数恒等式宣称AWGN或收敛。`score_amp_query_damped`仅为软件入口。

## 固定 L-DAMP 中的冻结 score 替换（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| automatic differentiation；forward mode；Jacobian–vector product / 自动微分；前向模式；Jacobian 与向量的乘积 | [Baydin等，JMLR 2018](https://www.jmlr.org/papers/volume18/17-468/17-468.pdf)，§3.1，pp.9–11，式(4)；§3.2，pp.12–13 | 对完整活动概率乘 score 均值的实映射求方向导数；去掉训练特征上的 detach 仅为保留正确链式依赖，不改变原训练代码。方向导数按计算图求出；float32 误差与八探针部分迹采样误差仍存在。 |
| Tweedie's formula；Wirtinger derivatives；Onsager correction / Tweedie公式；Wirtinger导数；Onsager校正 | [Cai v2](https://arxiv.org/html/2506.00581v2#S4)，§IV-A–C，式(43)–(54)；[Kunde v1](https://arxiv.org/html/2604.21115v1#S3.SS3)，§III-C式(18)–(21)、Remark14；[He v2](https://arxiv.org/html/1802.01290v2#S3.SS1)，§III-A式(4)–(8) | 原逐波束 DnCNN 和全部天线 score 使用同一矩阵更新；后者需完整跨波束部分迹。将逐波束方差压成 tr(Σ)/C 是受检验的接口适配，不是已有论文对本AFDM的保证。 |

[推导与接口](LDAMP_SCORE.md)明确坐标、归一化、完整链式导数和失败处理；
[同查询与闭环记录](history/results/ldamp_score_swap_20261015/REPORT.md)区分基线验收、四例开发诊断与候选失败。

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
| denoising score matching；score-based MMSE denoising / 去噪得分匹配；基于score的MMSE去噪 | [STMP v2 本地全文](../references/score_amp_20261015/cai2025_stmp_spawc_v2.pdf)，p.3，§III式(14)、§IV-A式(18)–(19) | 新模型学习活动混合的单波束汇总边缘先验。实方差τ=v/2；以D参数化score时 λ_s=λ_Dτ²。总体最优均值关系不等于有限CNN已达到MMSE。原文Turbo外信息更新未搬入此残差AMP。 |
| network preconditioning / 网络预条件化 | [EDM本地全文](../references/score_amp_20261015/karras2022_edm.pdf)，p.3 Table 1、式(2)–(3)；§5式(7)–(8) | 实坐标输入/跳连/输出尺度和权重沿原文公式；σdata²取当前混合总体实方差，非原图像常数。48通道4残差块、噪声控制通道仿射、log-uniform方差和独立训练均为本项目实现选择。 |
| Onsager correction；Wirtinger derivatives；functions of all previous iterates / Onsager校正；Wirtinger导数；依赖全部历史迭代量的函数 | He §III-A式(4)–(8)、Kunde §III-C式(18)–(21)/Remark14、Fan §5式(5.3)–(5.8)/Remark5.1，来源链接见前文 | 复矩阵1/Q部分迹、配对JVP与逐波束16×16块按显式索引核验；同步状态阻尼用历史校正递推。8探针近似、冻结噪声标签和有限结构化AFDM均保留统计适用性限制。 |

新入口 `diffusion_amp` 仅为软件标识。[完整推导](DIFFUSION_AMP.md)记录具体公式，
[文献审查](../references/score_amp_20261015/AUDIT.md)记录DMP-DUN补充p.1式(1)/(3)及(6)/(9)
的尺度关系差异；这些印刷式的代数问题不能据以断言作者端到端实验代码错误。
八份已下载PDF与ICC 2024全文尚缺的状态见[下载索引](../references/score_amp_20261015/README.md)。

## 完整用户共同活动与矩阵 D-AMP（2026-10-15）

2026-10-15 正式验证前的校正计算修订：矩阵 Onsager 的定义仍采用 Kunde §III-C
式(18)–(21)及 Remark 14。利用当前网络的用户独立性，直接计算 ZB 的取样公式、
完整 N 行基恒等式和无放回样本标准误差是本项目的线性代数与抽样推导，未命名为
新的文献算法。式子与条件见 [JOINT_AMP](JOINT_AMP.md) 式(15c)–(15e)及
[独立数值审计](../docs/history/results/joint_amp_20261015/projected_development_v1/DERIVATION.md)。
完整基只消除该固定 Jacobian 部分迹的抽样误差；不消除网络误差、不证明 AFDM
高斯性或状态演化。早期显式矩阵探针实现仍保留为开发对照。

| 原词或忠实译名 | 原文定位 | 本轮实现范围 |
|---|---|---|
| density ratio estimation；class-probability estimation；logistic loss / 密度比估计；类别概率估计；logistic 损失 | [Menon–Ong，2016](https://proceedings.mlr.press/v48/menon16.pdf)，§2.2、§3 式(6)–(8)、§4.2 式(16)–(17)，pp.305–306；[Rizvi–Pettee–Nachman v1](https://arxiv.org/html/2305.10500v1#S2)，§I 式(2)–(5)、脚注1，§II 式(6)–(12)、Table 1 | 完整用户共享活动变量；两类使用相同噪声标签采样律、平衡 BCE 学习 ℓ；p=sigmoid(logitρ+ℓ) 由公开活动先验修正。有限分类器不自动成为准确密度比或校准后验。 |
| denoising score matching；network preconditioning / 去噪得分匹配；网络预条件化 | [STMP v2](../references/score_amp_20261015/cai2025_stmp_spawc_v2.pdf)，p.3 §III 式(14)、§IV-A 式(18)–(19)；[EDM](../references/score_amp_20261015/karras2022_edm.pdf)，p.3 Table 1、§5 式(7)–(8) | F 只用活跃条件 MSE 训练，γ 为活跃实功率；16 束方差及完整用户网络为明确实现选择。L_F+L_BCE 不称为混合先验 DSM；理想两头组合 pF 给出混合均值，有限头不保证同一精确密度。 |
| Jacobian of the conditional mean；conditional covariance / 条件均值 Jacobian；条件协方差 | [Dytso–Poor–Shamai，TIT 2023 正式版](../references/afdm_network_axes_20261013/phase2_representation/dytso2023.pdf)，p.1883 式(3)，§III Proposition 1 式(17)，p.1885；式(9)定义输入在前的 Jacobian | 本项目采用输出行/输入列约定 J_D=Cov(x\|r)T⁻¹；异方差一般非对称。∇ℓ=T⁻¹F 与 pF 的完整乘积导数直接由 Gaussian 模型推导；有限双头一致性另行报告。 |
| Wirtinger derivatives；Onsager correction；functions of all previous iterates / Wirtinger 导数；Onsager 校正；依赖全部历史迭代量的函数 | [Kunde v1](https://arxiv.org/html/2604.21115v1#S3.SS3)，§III-C 式(18)–(21)、Remark 14、Appendix B；[Fan v5](https://arxiv.org/html/2008.11892v5#S5)，§5 式(5.3)–(5.8)、Remark 5.1 | 实际 pF 映射含全部用户内依赖；以配对 JVP、16 组随机相位 DFT 探针估计完整256×256部分迹，同步阻尼保存历史反馈。固定 V、ρ 的偏导不含标签估计总导数；当前 AFDM 不宣称满足随机矩阵状态演化条件。 |

`joint_amp` 仅为软件入口名。[完整推导](JOINT_AMP.md)逐式定义全用户双头、
score 换算、完整跨束校正及活动读出。[独立数学审查](../docs/history/experiments/joint_amp_20261015/MATH_AUDIT.md)
记录解析混合例子、导数约定和统计限制。完整用户信号输入不等于完整有色噪声条件化；
网络仍只使用16个逐束方差。原 Proposed 和逐束 `diffusion_amp` 均保留。

上述实现还将 EDM 直接跳连 p c_skip I 的部分迹精确扣加，再用相同探针估计
剩余完整导数；操作按 [式(15b)](JOINT_AMP.md)直接列式，不另造方法名称。
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

[完整推导与审查](history/experiments/amp_foundation_20261015/MATH_AUDIT.md)与
[全部控制结果](history/results/amp_foundation_20261015/REPORT.md)分别记录代数、模拟证据和局限。
相关系数RMS、四阶量、相对更新与固定轮数AER均是显式定义的诊断量，不命名为新的算法。

## 查询偏离 AWGN 的方案调研（2026-10-15）

本节仅记录文献比较，不代表采用新算法；主报告见
[方案调研](../references/awgn_solution_review_20261015/REPORT.md)。
既有 D-GEC、OAMP-MMV、VAMP、Memory AMP、FIRE、广义 Gaussian 条件均值术语沿用前述来源。

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| learned AMP (LAMP)；learned VAMP (LVAMP) / 学习型 AMP；学习型 VAMP | [Borgerding–Schniter–Rangan，TSP 2017作者稿](https://phil-schniter.web.app/pdf/tsp17_lamp.pdf)，§III-C Algorithms 2–3，pp.4298–4299；§V-A/B式(41)，pp.4300–4301；§VII | 展开迭代并学习线性/非线性参数的先例。真实 AFDM 查询微调、未知相位条件化和联合活动训练是待验证项目适配，不宣称已复现原论文。 |
| maximum likelihood estimation；activity detection via coordinate-wise optimization / 最大似然估计；逐坐标优化活动检测 | [Fengler等，TIT 2021作者稿v3](https://arxiv.org/html/1910.11266v3)，§II-A式(6)–(7)，§III-A式(8)–(9)，§III-C Algorithm 1；§IV-B4 | 直接观测协方差似然的来源。原文独立Rayleigh信道和用户标量导频不等于当前AFDM结构先验；256列不作256份独立天线样本。用于合成控制及备选设计，不替换主线分类器。 |
| anisotropic denoising score matching；normalized energy model / 非各向同性去噪得分匹配；归一化能量模型 | [Zilberstein–Segarra–Simoncelli–Guth，2026预印本v1](https://arxiv.org/html/2605.15487v1)，§3.1–3.3式(7)–(10)，Appendix C | 原文协方差族限制于空间域或Fourier域对角形式，不是任意full covariance的AFDM解决定理；本轮仅作研究储备。 |
| Exact Posterior Score Estimation (EPS) / 精确后验得分估计 | [Mammadov等，2026预印本v1](https://arxiv.org/html/2606.17048v1)，§3.2 Theorem 1式(11)–(12)，§3.4 Proposition 3式(15)–(16) | 精确关系基于已知线性Gaussian生成模型及对应条件去噪器。有限训练近似、同观测估计相位和任意已有迭代输入不自动继承精确性；未实施。 |

来源版本、最新非可分理论条件以及本地失败实验的适用范围分别见
[理论笔记](../references/awgn_solution_review_20261015/theory_notes.md)与
[有色噪声笔记](../references/awgn_solution_review_20261015/colored_notes.md)。

本轮后续[实际查询实验](history/results/query_matched_20261015/REPORT.md)只续训原分类器
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

[具体模型与来源](../docs/history/experiments/activity_posterior_20261015/SOURCES.md)、
[独立数学审查](history/experiments/activity_posterior_20261015/MATH_AUDIT.md)和
[完整结果](history/results/activity_posterior_20261015/REPORT.md)分别保存推导、术语边界和数值证据。
`activity_posterior_20261015`仅为实验目录名；本控制没有替换原Proposed或恢复score训练。

## 活动后验的局部提议与因子消息（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| informed proposals；balancing function；Barker choice / 利用目标分布的提议；平衡函数；Barker选择 | [Zanella，作者稿v1](https://arxiv.org/pdf/1711.07424v1)，§2.2 p.4式(2)–(4)，p.8 Table1与§4.1式(11)；期刊正式出版为JASA 115(530)，2020 | 实际核对v1的式号和页码。使用g(t)=sqrt(t)和g(t)=t/(1+t)作为提议权重，另作MH接受校正；后者不是Barker接受规则。单比特与活动交换的变度数图、0.1停留、归一化及非降邻边下界均为项目显式推导，未命名为新方法，不外推原文渐近最优性或全局混合保证。 |
| factor graph；sum-product；factor-to-variable message；clustering / 因子图；和积算法；因子到变量的消息；聚类 | [Kschischang–Frey–Loeliger，TIT 2001](https://www.mit.edu/~6.454/www_fall_2002/lizhong/factorgraph.pdf)，§II-C p.502式(5)–(6)，§V p.510，§VI-A p.513 | 标准边消息是单个目标变量的函数；本项目导出L=logit(p)−logit(实际输入ρ)。多个因子共享用户形成环时，正确单边相除不保证全局精确。保留联合活动的模块间传递与独立边际乘积必须区分；固定Gaussian反例仅用于核验。 |
| expectation propagation；moment matching / 期望传播；矩匹配 | [Minka，UAI 2001修订作者PDF](https://tminka.github.io/papers/ep/minka-ep-uai.pdf)，§2式(4)–(6)、§3式(8)–(10)，算法3(b)–3(d)，PDF pp.2–3 | 移除旧因子近似、乘真实因子、匹配矩、除去输入贡献；Gaussian自然参数相减按项目实坐标约定推导。程序仅核验恒等式，未完成新的物理接收机或score模块适配。 |
| cavity distribution；tilted distribution；site approximation；improper / cavity分布；tilted分布；因子近似；不能单独归一为概率分布 | [Vehtari等，JMLR 21(17)，2020](https://www.jmlr.org/papers/volume21/18-817/18-817.pdf)，§2.1 pp.5–6，§5.3 pp.18–19；阻尼讨论见§5.2 pp.17–18 | 使用原词避免把不同概率对象统称噪声。负Gaussian site精度不必导致总体分布不正常，但不能直接转成正AWGN方差；更新需要的cavity与匹配后分布须proper。本文献的阻尼讨论不当作当前AFDM收敛保证，本轮未新增阻尼实现。 |

[完整消息推导](../docs/history/experiments/activity_posterior_refinement_20261015/MESSAGE_DERIVATION.md)、
[提议来源与直接证明](history/experiments/activity_posterior_refinement_20261015/SOURCES.md)及
[结果报告](history/results/activity_posterior_refinement_20261015/REPORT.md)分别保存公式、适用条件和数值证据。
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

[实验协议](history/experiments/awgn_reference_ladder_20261015/PROTOCOL.md)区分解析控制、
真实信道下的人工算子、真相位oracle与原估计相位。随机化基础A的右子空间不等于
把完整A⊗I变成右酉不变矩阵。只有误差功率或四阶统计吻合不构成完整AWGN证明。
本轮未实现完整OAMP-MMV/LM-OAMP、未训练网络，性能和统计证据见
[报告](../docs/history/results/awgn_reference_ladder_20261015/REPORT.md)。

## 完整物理信道有限先验的Gaussian EP实现（2026-10-15）

本节更新前述因子消息条目的实施状态，不另立算法名称。

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| moment matching；cavity distribution；tilted distribution；site approximation / 矩匹配；cavity分布；tilted分布；因子近似 | [Minka，UAI 2001修订作者PDF](https://tminka.github.io/papers/ep/minka-ep-uai.pdf)，§2式(4)–(6)、§3式(8)–(10)、算法3(b)–3(d)，PDF pp.2–3；[Vehtari等，JMLR 2020](https://www.jmlr.org/papers/volume21/18-817/18-817.pdf)，§2.1 pp.5–6 | 已实现单个不可变Gaussian观测因子与逐用户可替换Gaussian sites；真实有限先验乘cavity后精确求矩。原子分布对连续Gaussian的通常KL不是有限值，本控制直接定义矩匹配，不宣称有限KL投影最优。 |
| damping；natural parameters；improper site / 阻尼；自然参数；不能单独归一化的site | 同上Vehtari，§5.2 pp.17–18，§5.3 pp.18–19，Appendix A | 已实现自然参数β=.5阻尼及最多12次减半回溯，允许负site精度；1e12条件数上限是本实验数值策略，不是proper的数学定义，也不保证AFDM收敛。该实现阶段不同于前述仅做恒等式审查阶段。 |
| Schur complement；marginalization / Schur补；边缘化 | [Walter–Eustice–Leonard，Exactly Sparse Extended Information Filters for Feature-Based SLAM，作者PDF](https://ttic.edu/ripl/assets/publications/walter07.pdf)，§II-A Table I，PDF p.4；§III-B2式(10a)–(10b)，PDF p.8 | 原文直接列出Gaussian信息矩阵和信息向量边缘化的Schur公式；本项目具体块积分见推导(P27)–(P28)。已另存数值计算修订，不把它称为新AMP算法，不将SLAM结论外推为本控制收敛。自身site不进入自己的cavity，其他用户site仍保留。 |

完整来源、S1/S2条件信息、实支撑表示及Gaussian查询成立条件见
[物理因子推导](../docs/history/experiments/physical_message_20261015/PHYSICAL_DERIVATION.md)。
有限先验、SVD支撑和条件数只是明确的模型与运算说明；未包装成既有论文中的方法名称。
本次query对角/各向同性近似在实SVD支撑坐标中，不能称为物理beam covariance验证。
原始相减缺陷和修订后仍有的Gaussian近似误差分别记录于
[结果报告](../docs/history/results/physical_message_20261015/REPORT.md)。

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
来源定位补充见 [SOURCE_NOTES](../docs/history/experiments/proposed_cai_relaxation_20261015/SOURCE_NOTES.md)，
近似与既有证据见 [PROPOSED_APPROXIMATIONS](PROPOSED_APPROXIMATIONS.md)。

第二项沿用已登记的block uniform diagonalization（Fletcher等GEC，§II-A式(8)–(9)、
§II-B Algorithm 1，PDF pp.2–3），每用户一个Gaussian协方差标量。
复数MMV的分块平均迹、查询及外信息公式为项目推导，见
[STEP2_PLAN](../docs/history/experiments/proposed_cai_relaxation_20261015/STEP2_PLAN.md)；
不将有限score网络、site裁剪/复用或本AFDM算子归入原文保证。
当前估计相位两个预选困难条件未见AER下降，见
[第二项结果](../docs/history/results/proposed_cai_relaxation_20261015/step2/REPORT.md)。

第三项继续沿用Gaussian site、cavity distribution、moment matching及Bernoulli–Gaussian
等已登记术语。因子相除依据Minka §3式(8)–(10)、算法3(b)–3(d)，PDF p.3；
标量线性投影及活动证据定位为Cai v2 §III-A式(7)–(11)、§III-B式(24)–(30)。
将原混合矩表示成条件Gaussian密度，再以单用户矩阵似然替换原标量因子的末端处理，
是[STEP3_PLAN](history/experiments/proposed_cai_relaxation_20261015/STEP3_PLAN.md)中的项目推导。
本地相除不等于消除全局历史信息重复，工作因子的对数权重比不称为新的物理活动先验。
该候选未降低当前困难面板AER；不为此操作新造方法名称。

第四项使用sum-product algorithm（和积算法）及clustering（聚类），来源为
[Kschischang–Frey–Loeliger，IEEE TIT 2001](https://www.mit.edu/~6.454/www_fall_2002/lizhong/factorgraph.pdf)，
§II-C式(5)–(6)，p.502，以及§VI-A，p.513。这里仅保留一对用户的离散活动并求和，
不是实现完整junction tree，也不保证重叠局部边际是全局精确后验。
Gaussian因子相除沿用上述Minka定位，复MMV四状态Gaussian积分及全方差展开见
[STEP4_PLAN](../docs/history/experiments/proposed_cai_relaxation_20261015/STEP4_PLAN.md)。
伙伴选择分数为项目提出的活动混合均值不确定性传播能量，不作为已有论文的方法名。
这一候选未降低预选困难面板AER；具体有限范围见
[第四项结果](../docs/history/results/proposed_cai_relaxation_20261015/step4/REPORT.md)。

第五项沿用前文power posterior、thermodynamic integration、marginal likelihood及log Bayes factor。
来源为[Friel–Pettitt作者稿](https://www2.stat.duke.edu/~scs/Courses/Stat376/Papers/NormConstants/FrielPettitPath05.pdf)，
§3式(4)–(5)、§3.1式(6)，PDF pp.4–6；[Friel–Hurn–Wyse v2](https://arxiv.org/html/1209.3198v2#S2)，§2式(6)–(11)。
第五项复数条件矩积分、有限噪声支持起点项及旧网络代入见
[STEP5_PLAN](../docs/history/experiments/proposed_cai_relaxation_20261015/STEP5_PLAN.md)。数学恒等式不等于有限网络近似已正确；
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
[项目显式推导](../docs/history/experiments/proposed_cai_relaxation_20261015/MATRIX_MESSAGE_DESIGN.md)，
不是以上论文对AFDM的已有完整算法或性能保证。消息核查阶段只完成内核和数学核验；
后续矩阵条件非线性模块、阻尼及全接收机对比见[闭环初筛](../docs/history/results/proposed_cai_relaxation_20261015/matrix_receiver/REPORT.md)。

## 基线噪声估计实施（2026-10-15）

| 原词或忠实译名 | 原文定位 | 本项目使用边界 |
|---|---|---|
| stopping criterion / 停止准则 | [Tropp–Gilbert–Strauss 作者稿](https://tropp.caltech.edu/papers/TGS05-Algorithms-Simultaneous-I-preprint.pdf)，§3.1 Algorithm 3.1 | SOMP 原文把停止准则作为输入，没有给出独立噪声估计。当前残差阈值使用下述空间噪声估计，是明确的项目适配。 |
| Gamma prior；EM / Gamma 先验；期望最大化 | [Zhang 2023 原文](../references/zhang2023_gamp_sbl_grant_free_noma.pdf)，式(17)–(19)、Algorithm 1 | 噪声精度采用含输出后验方差的 MAP 更新；复 MMV 计数为 LM+c−1。当前 c=1+LM、d=LMσ̂²_spatial，沿用既有项目先验强度并以空间噪声估计设置尺度；数值强度不是原文给定值，同一观测提供尺度和似然，不是独立额外信息。弱先验首版的低估结果保存在历史报告。 |
| sparsity pattern learning / 稀疏模式学习 | [Ding 2026 原文](../paper/literature/ding2026.pdf)，式(12)–(13)、(19)、(26) | 原文更新稀疏概率，不提供物理噪声更新式。当前 GNN-ASPL 保留网络，用空间噪声估计代入 σ²；不将补充前端称为 Ding 原算法的一步。 |
| noise precision / 噪声精度 | [Wei 2022 作者稿](https://arxiv.org/html/2101.05629v1)，式(45)–(46)、Algorithm 1、§VI-A | 共享 MMV 推广保留 M tr(AΣAᴴ)；初始化 mean|Y|²/100。原文 c=d=1e−4；当前 c=1+LM、d=LMσ̂²_spatial 是抑制弱先验持续低估的项目适配，同一观测提供尺度和似然，不是独立额外数据。噪声、行方差和偏移使用同一轮后验。先前固定噪声版本仍作为显式参考。 |
| equivalent noise variance / 等效噪声方差 | [He 2018 作者稿](https://arxiv.org/pdf/1802.01290v2)，§III-A 式(4)–(6)及式(5)后定义 | 原文 σ̂=‖z‖₂/√K，由校正残差估计。当前复数矩阵 L-DAMP 沿用残差协方差；归一化等效误差和物理噪声分开记录。 |
| minimum description length (MDL)；sample covariance matrix / 最小描述长度；样本协方差矩阵 | [Nadakuditi–Edelman，TSP 2008 作者全文](https://math.mit.edu/~edelman/publications/sample_eigenvalue.pdf)，§II-A 式(5)–(7)及尾部均值定义，期刊 pp.2626–2627，重述 Wax–Kailath 1985，DOI 10.1109/TASSP.1985.1164557 | 用 MDL 选空间信号秩，尾部特征值均值给出白噪声拟合值。未实现 Nadakuditi–Edelman 随后提出的新估计器。该空间秩不是活动人数，不使用真实活动数。 |

具体公式、公开输入边界及门限复用范围见 [BASELINE_NOISE.md](BASELINE_NOISE.md)。
SOMP/GNN-ASPL 的补充前端依赖低秩空间信号与白噪声模型；当前样本相关性与可能的模型失配不满足任意场景下的一致性保证。
GAMP/SBL 的近似模型可能吸收未建模信号或噪声，学习方差不能未经验证就当作真实热噪声。

## 当前 Proposed 与 Cai 逐式核查补充（2026-10-15）

本次沿用上文登记的术语；完整推导、适用条件、实现对应与 Cai 式(1)–(66)覆盖表见
[逐式核查报告](../docs/history/results/proposed_cai_equation_audit_20261015/REPORT.md)。
以下原文定位同时核对了正式 PDF 页面与 arXiv v2，不将项目推导包装成原文定理。

| 原词或忠实译名 | 原文定位 | 本次核查与使用边界 |
|---|---|---|
| posterior variance / 后验方差 | [Cai 正式版](../references/cai2026_score_based_jadce.pdf)，§III-B1 式(19)、(23)，PDF pp.6–7，印刷页3580–3581；[v2](https://arxiv.org/html/2506.00581v2#S3.SS2) | 式(19)印刷的pri中心与式(23)的条件中心方差不一致；按post中心解释才能对应。报告M15给出Gaussian反例；未得到作者勘误确认，不推断其代码照用了错误中心。 |
| second-order score matching / 二阶得分匹配 | 同文 §IV-C 式(50)–(54)、§V-A 式(56)，PDF p.9，印刷页3583 | 有限一阶网络下，总迹目标读出条件MSE，等于中心方差加均值偏差平方；这一限制同时适用于Cai与当前代码。总迹监督单独不识别逐天线子迹；报告M24–M26及零和扰动检查。 |
| channel power normalization / 信道功率归一化 | 同文 §V-B2 式(59)–(65)，PDF p.10，印刷页3584 | 式(59)按字面不是逐样本恒等式；报告M43–M44推导无偏功率估计及条件方差。式(60)逐用户尺度与式(61)共同噪声标签还包含共享近似。当前采用固定尺度，不直接采用该组功率估计。 |
| damping / 阻尼 | 同文 §V-B1 式(57)–(58)，PDF pp.9–10，印刷页3583–3584 | 当前均值和协方差分别算术插值，与作者代码的递归实现类型一致；不将其称为Gaussian分布混合的矩匹配或收敛证明。 |

观测矩阵适用性补充：[Cai §II-A式(3)–(4)、§V-C式(66)](https://arxiv.org/html/2506.00581v2#S5.SS3)
中的 partial orthogonal / 部分正交，指全局行Gram为标量阵，不能与单用户列块内部正交混同。
作者DFT实现的C_kᴴC_k=T P_tx I、单位自身响应和用户内白热噪声是根据原矩阵结构直接推导的性质，
并非任意部分正交矩阵都成立的新定理。当前AFDM的相应差异、实际矩阵检查及有限场景证据见
[近似适用性补充报告](../docs/history/results/proposed_cai_equation_audit_20261015/APPROXIMATION_ASSESSMENT.md)。
伪AWGN和右旋转不变条件沿用本文件已登记的Cai §V-B1及Fletcher等JSTAT 2019 §3–4、Theorem 1；
不把局部热噪声白化或平均方差匹配等同于实际完整查询服从独立AWGN。

矩阵消息的闭环初筛沿用以上 Gaussian、natural parameters、moment matching、damping、
conditional mean 和 posterior variance 术语。一般矩阵输入下的均值网络输出按条件均值回归解释；
有限均值网络下的条件均方误差仍包含均值偏差平方，参见上表Cai式(50)–(54)及项目推导。
均衡分类器logit与密度比的对应依据
[Menon–Ong](https://proceedings.mlr.press/v48/menon16.pdf)，§2.2、§3、§4.2式(6)–(8)、(16)–(17)，pp.305–306。
输入变换、矩阵阻尼等价式及正风险损失均明确写为[本项目适配](../docs/history/experiments/proposed_cai_relaxation_20261015/matrix_receiver/PROTOCOL.md)，
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
[分布核验报告](history/results/proposed_query_distribution_20261015/REPORT.md)与
[数学接口复审](../docs/history/results/proposed_query_distribution_20261015/MATHEMATICAL_INTERFACE_REVIEW.md)。

## 保留活动混合的局部消息核验（2026-10-16）

Gaussian mixture / Gaussian混合、moment matching / 矩匹配、normalizing factor / 归一化因子
依据[Minka UAI 2001](https://tminka.github.io/papers/ep/minka-ep-uai.pdf)，§2式(4)–(7)、§3式(8)–(10)，PDF pp.2–3。
本轮有限分量积分、自然参数凸目标及正标量精度边界是
[项目显式推导](../docs/history/experiments/proposed_mixture_message_20261016/DERIVATION.md)。
矩匹配只覆盖均值和协方差迹，不等于全协方差匹配或完整后验精确恢复。
局部负site精度只在乘积可积域内作约束诊断，不能直接解释为原接收机可接受的负方差输入。

Barker balancing function / Barker平衡函数沿用本文件已有Zanella v1 §2.2式(2)–(4)、Table 1来源，
及[已核验实现说明](../docs/history/results/activity_posterior_refinement_20261015/REPORT.md)；保留MH接受步骤。
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
公式见[本次推导P6–P8](../docs/history/experiments/proposed_probability_consistency_20261016/DERIVATION.md)。
该目标不是该文多类条件生成算法的原样移植，尚未完成候选训练或闭环验证。

参考密度采用Gaussian mixture，沿用前述Minka §2–3中的既有术语。
`log(q_1/q_0)=log(q_G/q_0)+log(q_1/q_G)`仅为密度比的恒等分解；
32组训练功率均值的参考构造及稳定求值均按操作和公式直接描述，未赋予新的算法名称。
条件均值与全方差分解见[推导P9–P10](../docs/history/experiments/proposed_probability_consistency_20261016/DERIVATION.md)，
参考本身的失败样本及数值核验见[开发对照](../docs/history/results/proposed_probability_consistency_20261016/reference_density/DEVELOPMENT_CHECK.json)。

后续使用w(v)=1/(s+v)乘条件均值回归损失，其中s为训练先验的每复坐标二阶矩。
这是同一条件平方风险分解的正权重推论，按公式描述，不称为文献中的新算法或新损失名称；
理想目标不变而有限优化的折中可能变化，见[后续候选推导与协议](../docs/history/experiments/proposed_probability_consistency_20261016/WEIGHTED_CANDIDATE_PROTOCOL.md)。

固定几何下的均匀相位积分按[项目公式G1–G8](history/experiments/proposed_probability_consistency_20261016/CONDITIONAL_GEOMETRY.md)描述，
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
[项目直接推导L1–L6](../docs/history/experiments/proposed_physical_linear_factor_20261016/DERIVATION.md)。
沿用Gaussian mixture、conditional mean、posterior covariance与QR factorization的上述原词；
相位积分仍依据NIST DLMF §10.32式(10.32.1)、(10.32.3)。
对给定协方差作Cholesky坐标变换只是Gaussian因子的代数计算，
不把它称作实际多用户反馈已独立化或Gaussian化，也不为这一组合另立方法名称。

## 保留 score 的 Gaussian 因子分解（2026-10-16）

| 术语 | 原文依据 | 本项目范围 |
|---|---|---|
| conditional score function；SNIPS / 条件 score 函数；文献算法名 SNIPS | [Kawar–Vaksman–Elad，NeurIPS 2021](https://papers.nips.cc/paper/2021/file/b5c01503041b70d41d80e3dbe31bbd8c-Paper.pdf)，§3.1 式(6)，§3.2 式(7)–(10)，PDF pp.5–6 | 仅借鉴所有观测奇异方向处于小噪声范围时的 Gaussian 噪声耦合。复数矩阵因子、归一化常数、活动混合及均值/方差恢复是 [S1–S8](../docs/history/experiments/proposed_score_factor_split_20261016/DERIVATION.md) 的直接推导；没有实现完整 SNIPS，也没有证明原网络给出精确可积 score。 |


## Proposed 物理噪声输入与方差消息（2026-10-16）

| 原词或忠实译名 | 原文定位 | 本次核查与建议范围 |
|---|---|---|
| AWGN；noise variance / 加性白高斯噪声；噪声方差 | [Cai v2](https://arxiv.org/html/2506.00581v2)，§II-A 式(3)，§III-A 式(7)–(8)，Algorithm 2 第1、5行 | 物理观测噪声 δ₀² 是输入参数；Algorithm 2 没有其估计步骤。[作者代码固定版本](https://github.com/chang-cai/score-massive-connectivity/blob/0c75680c966dcb8e46250de146f4c27e9294c283/main_stmp_jadce.py#L130-L139) 同样使用输入的 self.delta²。 |
| pseudo AWGN observation model；posterior variance / 等效 AWGN 观测模型；后验方差 | 同文 §III-B1 式(20)，§IV-A 式(44)–(45)，§V-A 式(55)–(56)，§V-B1 | TMP 产生的去噪输入方差及 score 网络恢复的后验方差均与物理噪声参数不同；更新前两者不表示已估计接收端噪声。 |

建议复用上文已登记的 Wax–Kailath MDL 空间协方差前端，将尾部特征值均值作为
Proposed 的物理噪声输入，归一化线性模块使用 σ̂²/s²，原迭代方差公式继续使用。
这项接收机适配尚未实施；它依赖低秩空间信号与白噪声模型，不称为 Cai 的噪声估计方法。
原论文及实现位置、已有 baseline 的噪声比值统计和验证范围保存在
[NOISE_REVIEW.json](../docs/history/results/proposed_1000_20261016/NOISE_REVIEW.json)。

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
| Langevin dynamics；unadjusted Langevin algorithm (ULA)；Ornstein–Uhlenbeck / Langevin动力学；未调整Langevin算法；Ornstein–Uhlenbeck过程 | [Wibisono, COLT 2018](https://proceedings.mlr.press/v75/wibisono18a/wibisono18a.pdf)，§2.1式(4)、Example 1，§2.2式(5)、Example 2，PDF p.4 | [局部推断规格](history/experiments/proposed_score_factor_split_20261016/LOCAL_INFERENCE_PROTOCOL.md)将固定矩阵换元后写成复数更新，噪声系数和离散Gaussian协方差直接推导。原文明确ULA有限步长存在偏差；其强凸等条件没有在本有限三网络向量场上得到验证，不引用为收敛保证。 |

“保留矩阵因子”是操作描述：保留一个用户内16×16精度矩阵J，而不是压缩为标量单位阵。
它不是全体用户的精确联合精度，也不意味着外部Gaussian消息已经消除真实用户反馈依赖。

同一Wibisono文献§2.1 Example 1（PDF p.4）给出Ornstein–Uhlenbeck过程的精确Gaussian转移。
[E1–E2](../docs/history/experiments/proposed_score_factor_split_20261016/GAUSSIAN_LINEAR_PROTOCOL.md)
固定每步的网络非线性项后使用这一线性解；对零活动贡献的Gaussian部分保持精确协方差，
不宣称整个有限神经向量场或非线性目标已得到精确离散化，也不为这一组合另造方法名称。

## 原score提议的接受校正（2026-10-16）

| 原词或忠实译名 | 原文定位 | 本项目范围 |
|---|---|---|
| Metropolis–Hastings；reversibility；test ratio / Metropolis–Hastings、可逆性、检验比值 | [Hastings 1970](https://probability.ca/hastings/hastings.pdf)，§2.2 pp.99–101，式(4)–(8)及连续密度段 | [A1–A3](history/experiments/proposed_score_factor_split_20261016/ACCEPTANCE_PROTOCOL.md)以原first决定Gaussian提议，用原activity logit定义有限近似密度并计算接受比。可逆性只针对该明确近似密度；不保证分类器校准、first/second条件矩一致或有限时长混合，不冠以新算法名。 |

## 联合观测因子的噪声层级（2026-10-16）

| 原词或忠实译名 | 原文定位 | 本项目范围 |
|---|---|---|
| annealed Langevin dynamics / 退火 Langevin 动力学 | [Song–Ermon 2019 v3](https://arxiv.org/html/1907.05600v3#S4.SS3)，§4.3 Algorithm 1 | 原文按噪声层级递减并按噪声方差缩放步长。本项目的[固定规格](history/experiments/proposed_joint_score_factor_20261016/PILOT_PROTOCOL.md)同时改变似然强度，使用[J1–J6](history/experiments/proposed_joint_score_factor_20261016/DERIVATION.md)精确辅助分解及矩阵预条件；这是项目推导，不称为原文算法的直接复现，也不借用其名义保证当前有限网络的收敛。 |

“联合观测因子”仅描述保留 CN(Y;AZ,D) 及所有用户共享残差的操作；不另造算法名。
它去除了逐用户外部反馈的独立 Gaussian 工作近似，但有限网络、离散步长、混合及估计相位的误差仍存在。

| 原词或忠实译名 | 原文定位 | 本项目范围 |
|---|---|---|
| Kullback–Leibler (KL) divergence / Kullback–Leibler 散度 | [Zhang等，NeurIPS 2023](https://papers.neurips.cc/paper_files/paper/2023/file/b5b4d92374323c53c24bbbc8ee0e715c-Paper-Conference.pdf)，§1，PDF p.2，定义及式(1) | [初始化尺度诊断](history/experiments/proposed_joint_score_factor_20261016/INITIAL_NOISE_PROTOCOL.md)用同协方差Gaussian的特例，转换到proper complex Gaussian后得到tr(δᴴP⁻¹δ)。只描述两个已指定的初始化条件分布，不是神经目标或真实后验间的散度，也不是满足三角不等式的距离。 |


## 酉导频下保留伙伴活动混合的消息更新（2026-10-16）

沿用既有 Bernoulli–Gaussian、Gaussian mixture、cavity distribution、site approximation、
moment matching 术语；依据 Minka 2001 §2式(4)–(6)、§3式(8)–(10)、Algorithm 3(b)–3(d)，
以及 Vehtari et al., JMLR 2020 §5.2 pp.17–18 的 natural-parameter damping。
来源：[Minka原文](https://tminka.github.io/papers/ep/minka-ep-uai.pdf)、
[Vehtari等原文](https://www.jmlr.org/papers/volume21/18-817/18-817.pdf)。

[本轮协议](history/experiments/proposed_unitary_mixture_20261016/PROTOCOL.md)在固定酉导频下，
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

[本轮协议](../docs/history/experiments/proposed_unitary_joint_ep_20261016/PROTOCOL.md)
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
[本轮协议](history/experiments/proposed_activity_repair_20261016/PROTOCOL.md)固定观测估计的每用户
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

[本轮规格](history/experiments/proposed_structured_iteration_20261016/PROTOCOL.md)采用上述矩形式：
精确计算指定 Gaussian sites 下的联合线性边缘，仅在逐用户网络接口作平均迹投影，再除旧site。
自然参数阻尼沿用上面已登记的EP来源。实际second为有限条件风险读出，此实现不计算完整
Jacobian sensitivity，故不能称为直接实现了满足原文MMSE假设的GEC，亦不继承自由能或收敛保证。
一般非酉用户块下，平均迹投影的自身响应及热噪声非白性均显式保存；未将统一迭代称为精确AWGN恢复。


## 专利交底书术语及变量含义核对（2026-10-16）

核对对象为《一种面向无GNSS辅助卫星接入的联合活动检测与信道估计方法》20261016114905版，修订输出为20261016122331版。下列编号为交底书公式编号。本节记录该稿的对外用语；研究历史中的内部变量名和代码接口继续按原记录理解。

| 核对对象 | 采用的表述及含义 | 文献或实现定位 |
|---|---|---|
| 信道查询、查询方差、公共查询方差 | 线性估计输出处用“外信息均值和方差”；经阻尼传入下一模块后用“去噪模块输入均值R、输入方差v”。原来的“查询”是项目内部叫法，不能当作该论文原词。v是所传递高斯消息的方差参数。 | [Cai等v2](https://arxiv.org/html/2506.00581v2)，Table I的extrinsic mean and variance；§III-A式(9)–(14)；交底书式(14)。 |
| 条件误差方差、共享条件误差方差 | 网络量写为“条件均方误差估计值”；按式(16)平均并设正下限后，将τ用作各终端共用的高斯近似方差。 | Cai §IV-C式(53)–(54)；本项目[训练损失](../src/afdm_jadcedd/experiment/training/scores/direct_objectives.py)的direct_second_loss；[THEORY](THEORY.md) T9–T10；交底书式(15)、(16)、(25)。 |
| 空间平均协方差 | 写明沿N²个AFDM输入、输出坐标组合取平均，保留M×M天线间信道误差协方差；属于文中高斯混合近似的矩。 | Cai §III-B3式(32)–(38)给出活动混合矩关系；本项目[denoiser](../src/afdm_jadcedd/algorithm/proposed/denoiser.py)的flat、gram、covariance计算；交底书式(21)。M×M形式及平均轴以本项目公式为准。 |
| 公共反馈方差（原用于bar t_X） | bar t_X称“有效信道平均方差”；γ_out称“返回线性估计的外信息方差”。两者分别位于高斯消息相除之前和之后。 | Cai §III-C式(39)–(42)；交底书式(22)、(23)。 |
| 训练支持区间 | 直接写“训练噪声方差范围”。 | [score_matching](../src/afdm_jadcedd/experiment/training/scores/score_matching.py)的噪声采样；denoiser的noise_support判断。0.001至100为当前实现参数。 |
| 折叠时延 | 实施例直接定义为“以采样点数表示的时延对16取余”；表中称“时延余数”。 | [路径响应](../src/afdm_jadcedd/algorithm/baselines/offgrid/atoms.py)的path_atom时延定义及[相位估计](../src/afdm_jadcedd/algorithm/phase_estimation.py)的搜索范围。 |
| 物理候选、物理频率、时延—相位峰 | 分别写为候选路径响应、多普勒频率、评分峰值及其对应时延和相位。直接描述搜索对象。 | [phase_estimation](../src/afdm_jadcedd/algorithm/phase_estimation.py)的峰值筛选、频率枚举及连续参数细化；交底书第一步、式(8)–(10)。 |

条件均方误差的判断依据是实际训练目标，而不是另命名一种方差。固定一阶网络后，式(25)在给定带噪输入和噪声方差下拟合该网络估计误差的条件期望。按THEORY T10，条件均方误差等于平均条件协方差迹加上均值估计偏差的平方项；因此将有限网络读出直接称为精确后验方差会遗漏后一项。交底书只需准确说明“估计均方误差，再用于高斯近似方差”的处理关系，不展开研究诊断。

已核实并保留的名称：

| 术语 | 原文位置 | 在交底书中的使用 |
|---|---|---|
| first-order / second-order score network；一阶／二阶得分网络 | Cai §IV-A末段、§IV-B–C式(46)–(54) | 使用完整名称；图中“一阶网络”“二阶网络”为同一对象的简称。 |
| denoising score matching；去噪得分匹配 | Cai §IV-B式(47)–(49) | 对应式(24)，按复噪声每个实分量方差v/2换算。 |
| LMMSE；线性最小均方误差 | Cai §III-A式(6)–(8) | 本稿式(12)、(13)是一般导频矩阵下的高斯线性更新。 |
| damping；阻尼 | Cai §V-B1式(57)–(58) | 当前均值、方差按新值权重0.2插值；该权重为本项目配置。 |
| conditional residual block、refinement block；条件残差块、特征细化模块 | Cai §VI-A2、Table III | 对应本项目[network](../src/afdm_jadcedd/algorithm/proposed/network.py)的条件RefineNet结构；通道数及连续噪声条件为当前实现。 |
| AFDM、DAFT、chirp-periodic prefix；仿射频分复用、离散仿射傅里叶变换、啁啾周期前缀 | [Bemani等2204.12798v2](https://arxiv.org/html/2204.12798v2)，§II-B式(11)–(17)、§III-A式(18)–(19)；交底书[4]的[2104.11331](https://arxiv.org/abs/2104.11331)题名亦已核实 | 保留已有名称；式(2)的多周期前缀及式(5)–(8)的具体算子以项目模型为准。 |
| fractional delay、fractional Doppler；分数时延、分数多普勒 | [Huang等原文](../references/huang2026_prior_agnostic_afdm_diffusion.pdf)，§II式(4)–(5)，p.2950 | 连续时延、多普勒路径响应的来源；当前多用户、多天线观测和参数排列由项目定义。 |
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

本次定向核查见 [修复选择报告](../docs/history/results/proposed_repair_literature_20261016/REPORT.md)。保留既有EP、GEC、OAMP-MMV、LM-OAMP名称及其原适用条件，不把16×16矩阵消息或以下参数化冠以新的文献算法名称。

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

完整对照见[八篇文献核查](../references/satellite_gfra_snr_20261016/REPORT.md)。这里的“总接收”仅说明公式分子包含所有活动用户，不作为新方法名称。

| 原词或忠实表述 | 原文定位 | 本项目使用边界 |
|---|---|---|
| signal-to-noise ratio / 信噪比：叠加接收信号功率基准 | [Ding 2026](https://doi.org/10.1109/TVT.2026.3729877)，§IV-B p.5；[Mao 2025](https://arxiv.org/html/2504.04686v2#S4)，§IV；[Zuo 2023](https://arxiv.org/pdf/2210.17355v1#page=25)，§V | Ding原印式为‖SZ‖²_F/(MLσ²)，模型式(9)用Ψ记号；Mao按角域位置累加‖Γg‖²；Zuo按超符号u累加‖G_u x_u‖²，u不是用户。都没有除活动用户数，支持当前总接收SNR作为一种已用口径，不证明作者代码逐实现调噪细节。 |
| signal-to-noise ratio / 信噪比：按卫星及观测窗口定义 | [Shen协作星座2025](https://arxiv.org/html/2408.02586v1#S5)，§V、式(18)–(19)、Fig.4；[Shen大差分时延2025](https://arxiv.org/html/2412.20806v1#S5)，§V、式(19)、Fig.7/9 | 前者每颗卫星的导频窗口；后者各时延块内Q帧全部用户信号。前者AER曲线−6至2 dB，后者−4至4 dB；不能宣称卫星GFRA不研究负SNR。 |
| normalized path power；average symbol energy / 归一化路径功率、平均符号能量 | [Shen GLOBECOM2022](https://arxiv.org/pdf/2208.01828v1#page=5)，§IV；[Xu TCOM](https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/AFDM-aided-Grant-Free-Random-Access-for-LEO/991050765702346)，§V | Shen明示Σ_i|h_ui|²=1、导频方差1/(MN)、SNR=10log10[1/(MNσ²)]；逐路径向量能量约束不等于实际接收能量恒定。Xu采用E_s/N_0且研究给定信道信息下的活动/数据检测，不能直接作为同任务JADCE的总接收SNR对照。 |

范围结论：Ding Fig.3的0、4、8、12、16、20 dB可作为本项目主评估扫描的文献参照。该取值是评估范围选择，不是统一物理下限，也不是功率分布或算法修复。此前单用户参考SNR的建议保留为可选的另一实验，不再表述为纠正当前总接收定义所必需。负SNR既有结果保留，任何新优势须在固定的新配对实验中验证。

2026-10-16 已知噪声条件核对：Cai [v2](https://arxiv.org/html/2506.00581v2) Algorithm 1、Algorithm 2 输入的 δ₀² 是物理热噪声方差；§III-A 式(7)–(8)直接使用它。迭代消息方差 v、τ 与该物理参数区分。[作者代码固定提交](https://github.com/chang-cai/score-massive-connectivity/blob/0c75680c966dcb8e46250de146f4c27e9294c283/main_stmp_jadce.py#L141-L149) 使用生成噪声的同一 delta²，未从观测重新估计该参数。当前原导频八点比较统一供给准确方差，详见 [实验协议](../docs/history/experiments/proposed_original_snr8_10_20261016/PROTOCOL.md)。

## 公共相位前端的计算优化调研（2026-10-17）

本次为定向文献核查，检索范围及建议见[调研记录](../docs/history/results/phase_frontend_research_20261017/RESEARCH.json)。未修改冻结算法，未测得优化后的加速比。

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
| structured sparsity；structured generalized approximate message passing (S-GAMP) / 结构化稀疏性；结构化广义近似消息传递 | [Sun等作者全文](https://livrepository.liverpool.ac.uk/3141858/1/Massive_Grant-free_OFDMA_with_Timing_and_Frequency_Offsets.pdf)，TWC 2022，DOI 10.1109/TWC.2021.3121066；§II-C 式(18)–(19)，PDF p.6；§III-A 式(20)–(41)，pp.6–9；§IV，pp.10–11 | 借鉴“用户不活跃或只对应一个偏移候选”的联合先验。完整信道块、冻结网络似然比、原公共标量EP反馈为项目适配；不宣称复现S-GAMP。独立候选查询、跨候选协方差投影和H/相位先验分解均显式记录于[候选推导](../docs/history/experiments/proposed_joint_phase_20261017/ALGORITHM.md)。 |

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

- Genie-aided lower bound / 辅助真值信息下界：[Cai v2](https://arxiv.org/html/2506.00581v2#S6.SS2)，§VI-B、Fig.4；本地 `paper/literature/section_structure_20261009/cai.txt` 第 2099–2103 行明确假设路径功率、时延、角度已知，并对复增益使用 MMSE 估计。本项目采用同类信息辅助比较，但额外公开定模随机相位 LOS 的真实复增益，避免将非高斯先验的 LMMSE 误称 MMSE；同时公开 AFDM 所需多普勒。
- 条件 Gaussian MMSE 的具体表达式及侧信息增加不增大最优平均平方误差的推导见 `experiment/README.md` 的独立去噪段。这是针对现有信道模型的直接条件期望计算，不另造算法名；下界只约束总体平均 MSE，有限样本曲线不具有逐样本保证。

### 独立去噪对照方法核对（2026-10-18）

来源：[Cai v2，§VI-B、Fig.4，PDF p.12](https://arxiv.org/pdf/2506.00581v2#page=12)。本条记录原文方法及当前实现的对应关系，不表示新增方法已实现或已完成实验。

| 原文名称 | 原文定义与本项目对应 |
|---|---|
| Least square (LS) | 对直接 AWGN 观测 Y=H+N，输出 Y；当前 `noisy` 方法直接输出 query，与此对应。 |
| Orthogonal matching pursuit (OMP) | 在均匀采样的时延–角度字典中依次选择 100 个原子，再以 LS 估计系数。当前独立去噪入口未包含此方法；本项目的适配需要按实际信道参数定义字典与预算。 |
| Element-wise MMSE | 在与 OMP 相同的变换域，对 i.i.d. Bernoulli–Gaussian 系数采用逐元素 MMSE，原文稀疏度为 0.15。当前 `gaussian` 为 P/(P+v) 乘 query 的各向同性 Gaussian 先验线性估计，不对应这条 BG 曲线。 |
| Variational line spectral estimation (VALSE) | 近似推断时延、角度、路径系数的后验分布；Cai 引用 [58] Badiu–Hansen–Fleury, IEEE TSP 65(9), 2247–2261 (2017)。当前独立去噪入口未包含 VALSE。 |

当前 5,000 与 50,000 样本的两条 Proposed 曲线属于训练样本量比较。接收机实验已有的 SOMP、GAMP-SBL、GNN-ASPL、Off-grid SBL 结果对应不同观测任务；若加入独立去噪比较，应在同一直接 AWGN 输入上单独运行并评分。

## 论文第 II–V 章及附录 A 术语核对（2026-10-18）

本轮针对当前论文英文正文逐项核对方法名、缩写和自拟复合表达。下表为当前稿用法；上文实验与历史候选的记录保留。详细修改见 [核对报告](../paper/checks/terminology_20261018_125231/TERM_AUDIT.md)。

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
| sparsity pattern learning、delay-Doppler grid、graph nodes / 稀疏模式学习、时延–多普勒网格、图节点 | Ding2026 摘要、§I、§III；本地 paper/literature/section_structure_20261009/ding.txt | 描述 Ding 的相关工作；承认其学习节点间相关性，与本稿直接有效信道先验区分 |
| AFDM effective channel、likelihood-annealed Langevin dynamics / AFDM 等效信道、似然退火 Langevin 动力学 | Huang2026 摘要 p.2949、§II eq.(4)、§III | 直接信道估计与生成先验相关工作；不将其采样算法描述为本文算法 |
| score-based generative models、posterior sampling / 基于得分的生成模型、后验采样 | Arvinte–Tamir2023 摘要、§III；Cai2026 §I、§IV | 区分采样式信道估计和 MP 中的矩估计 |

本轮引言的句子证据、贡献定位和结果来源见 paper/checks/introduction_20261018_134220/SOURCE_MAP.md。引言采用现有 MP 通称，不增加接收机缩写。


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

## 当前正文术语一致性（2026-10-18）

正文引文统一采用文献编号，不附章节、公式或推论定位；精确出处继续保留在本记录及论文核对材料中。正文中的本稿章节和公式交叉引用用于连接推导，予以保留。

以下约定用于第 I–V 章、附录 A–C 及中文引言对照稿。直接描述本稿变量或运算的句子不作为独立方法名称；已有方法名称沿用原文及其适用范围。

| 当前用语 | 来源、定位与适用范围 |
|---|---|
| marginal activity probability / 边缘活动概率 | 本稿式 `activity-generation` 对单个活动变量求边缘概率得到 ρ=p/Z；它是标量概率。第 II 章的 channel and activity marginals 指边缘分布，保留其分布含义。 |
| conditional mean-squared error estimate / 条件均方误差估计 | 本稿附录 A 式 `conditional-risk`、`risk-decomposition`；训练目标依据 [Lu §4.2 Corollary 4.2](https://proceedings.mlr.press/v162/lu22f/lu22f.pdf)。一阶网络有限精度时，二阶网络目标仍为相应估计器的条件 MSE，不直接等同于后验协方差迹。引言、训练、调度与附录统一使用这一称谓。 |
| first-order score network；second-order score network；activity classifier / 一阶得分网络；二阶得分网络；活动分类器 | [Cai §IV-A–C](https://arxiv.org/html/2506.00581v2) 的一阶、二阶得分与网络设计；本稿第 IV-C 章的活动分类器以 BCE 训练，密度比依据 [Menon–Ong §3、§4.2](https://proceedings.mlr.press/v48/menon16.pdf)。按各自目标称呼三种网络；本稿 Tψ 的坐标输出之和用于估计迹，不宣称逐坐标 Hessian 已被识别。 |
| smoothed activity probability / 平滑活动概率 | 直接描述本稿式 `activity-history` 中 w 的指数加权递推；w 用于停止检查，p 为接收机报告的概率，ρ 为固定先验参数。 |
| damping factor / 阻尼因子 | Cai §V-B1，式(57)–(58)。本稿第 V-B 章明确 η 为当前消息的权重，首次更新直接采用当前消息。 |
| 两个计数器的直接定义 | 本稿附录 C 式 `iterate-stopping`、`site-stopping` 之后分别说明满足对应条件的连续迭代次数，不另设技术名称。保留独立清零、接受 site 更新的条件以及最少／最多迭代次数和硬判决窗口。 |
| noise-free received signal / 无噪声接收信号 | 直接描述第 II 章 Y₀=AX；SNR 按包含用户交叉项的实际接收功率定义。 |
| expected negative log density / 负对数密度的期望 | 本稿附录 A 式 `shared-error-objective` 明确给出目标、固定均值、协方差 τI 和约束 τ≥τmin；第 IV 章直接说明最小化该目标得到用户平均值及其下限。 |
| AFDM effective channel / AFDM 等效信道 | [Huang2026](https://doi.org/10.1109/LWC.2026.3689601)，§II 式(4)、§III。本稿此名称对应 H；X 直接定义为 αH，并说明不活跃时为零。 |
| sensing matrix / 感知矩阵 | [Cai §II-B](https://arxiv.org/html/2506.00581v2) 的线性观测模型及本稿第 II 章式 `effective-pilot`、`mmv-indexing`、`mmv`。本稿以 A 和 Â 区分真实相位与估计相位构造的矩阵；P 为原始导频，G 为单路径算子，按各自对象表述。 |
| physical scene / 物理场景 | 本稿仿真抽样单位的说明性称谓：终端几何、路径系数与活动向量共同构成一个场景。第 II 章明确该含义及 SNR 扫描复用场景；训练／验证按场景划分，不把同场景内的多个用户信道称为独立场景。配对协议见 `experiment/README.md`。 |
| shared scalar variance / 共享标量方差 | Cai §III-A 式(7)–(8)之前明确使用原词 shared scalar variance。本稿采用具体计算式解释协方差近似与平均范围；该原词本身具有文献出处。 |

2026-10-18 论证结构调整：原有术语和公式标签保留；参数估计移至 III-D，路径矩阵展开移至附录 B，停止量与计数器的详细定义移至附录 C。正文外部引文仍不附章节定位。此次写作结构的证据不作为新增技术术语或方法名称，详见 `paper/writing_profile/argument_structure_20261018_175516/ARGUMENT_ANALYSIS.md`。

## 推导衔接的来源定位（2026-10-18）

| 用语与数学操作 | 原文定位 | 本稿对应与范围 |
|---|---|---|
| Gaussian projection；extrinsic message / Gaussian 投影、外信息消息 | Cai 正式版 §III-A，式(6)–(11)，pp.3579–3580；Minka2001 §2–3，式(8)–(10) | 新增 `linear-belief`、`linear-message-division`：先乘似然和输入 Gaussian，再匹配总方差并相除。一般感知矩阵下的均值与协方差保持原式；精度及精度加权均值相加／相减直接由 Gaussian 指数项得到。 |
| denoising score matching / 去噪得分匹配 | [Cai §IV-B](https://arxiv.org/html/2506.00581v2#S4.SS2)，式(46)–(49)，正式版 pp.3582–3583；Vincent2011 DOI 10.1162/NECO_a_00142 为既有一手来源 | 新增 `conditional-score-target`、`first-loss-equivalence`。由 Gaussian 混合密度求导和条件平方误差分解直接推导，使用本稿的实噪声方差 v/2 和实维度 2D。噪声层固定时的加性常数不依赖参数；总体最优解的结论限定于训练噪声范围内的无约束函数。 |
| trace of second-order denoising score matching / 二阶去噪得分匹配的迹 | [Lu2022](https://proceedings.mlr.press/v162/lu22f/lu22f.pdf)，§4.2 Corollary 4.2 式(15)，PDF p.5；附录 F.2 式(138)–(143)，PDF p.22；Cai §IV-C 式(50)–(54)，正式版 p.3583 | 新增 `second-trace-target` 并在附录 A 给出 Gaussian 二次求导的中间式。以 d=2D、σ²=v/2 写出条件迹恒等式；替换为固定的一阶网络后，对样本迹残差施加 v_R²/(2D)² 权重，得到原有训练目标。有限一阶误差对应条件 MSE，原有 `conditional-risk`、`risk-decomposition` 保留。 |

本次补充属于既有 Gaussian 消息、DSM 和条件期望关系的展开，不新增算法名称或独立理论创新主张。Vincent 的出版信息已由 MIT Press 核对，作者 PDF 本轮访问被拒；精确公式定位使用已读 Cai 和 Lu 原文，未声称重新通读 Vincent 全文。推导与实现的核对见 `paper/checks/derivation_bridges_20261018_182142/ALGEBRA_CHECKS.json`。

## 相位估计子算法的公式与实现（2026-10-18）

正文 Algorithm 1 为 inter-frame phase estimation，整体接收机顺次编号为 Algorithm 2。沿用上文登记的 variable projection（O'Leary–Rust §1 式(2)–(3)、§2 式(5)–(7)）和 L-BFGS-B（Zhu 等摘要、§1）；粗相关、候选选择和循环更新按本项目实际运算直接描述。

新增 `phase-screening-score` 是逐帧 pilot response 与残差的相关系数，经相位维 Fourier 变换后求天线能量和，再除以响应能量。公式、正负相位约定、Hz 与归一化 Doppler 的换算均对照 `phase_estimation_optimized.py` 的 `coarse_scores`、`candidates`、`refine`，以及 `phase_candidate_screening.py` 的 `physical_candidates`。时延网格及细化区间对应 `baselines/offgrid/atoms.py` 的 `sampling_grid`、`delay_bounds`。子算法保留当前配置的完整逐轮候选搜索、固定用户顺序和联合增益重估。

正文同时简要明确边缘信道先验、叠加信号的空间秩条件及 Gaussian 消息方差参数的含义。公式与代码对应核验见 `paper/checks/phase_algorithm_20261018_184933/PHASE_FORMULA_CHECKS.json`。

## 活动证据对照与局部说明（2026-10-18）

- **Gaussian channel messages / Gaussian 信道消息与活动概率**：Cai 正式版 §III-B 式(24)–(31)，p.3581；活动混合矩见式(35)–(38)。引言明确其活动概率由 Gaussian 信道消息计算，本稿则在训练范围内通过分类器学习活动与静默密度比；密度比与分类概率的来源仍为 Menon–Ong §3、§4.2。贡献列表沿用已有 Gaussian message updates 表述及 Cai 引用。
- **协方差矩阵分解的实现成本**：第 V 章的 M³ 项直接对应 `proposed/linear.py:54`、`proposed/gaussian.py:27–35` 的矩阵运算；这是当前实现的成本说明。
- **时延折返与自然参数符号**：附录 B 的未编号恒等式由 `continuous-basis` 在整数 `2Nc1` 下直接展开，核对依据见 `paper/checks/three_reviewers_20261018_190255/REVIEWER_1_MATH.md`。附录 C 将 `E_k/c_k` 的符号统一为 Ξ_k，Gaussian site 和自然参数的既有定义保持不变。


### 2026-10-18 后验因子图与模块消息对应

| 术语 | 原文位置 | 本稿使用范围 |
|---|---|---|
| factor graph；variable node；factor node / 因子图、变量节点、因子节点 | Cai v2 §III，Fig. 2、Table II；§III-A 式(6)–(11)、§III-B 式(12)–(42)，https://arxiv.org/html/2506.00581v2 | 第 III 章图 `fig:receiver-factor-graph` 对应本稿 `eq:working-posterior`：共享似然连接全部 X_k；每用户的约束连接 X_k、H_k 和 α_k，另有信道及活动先验因子。估计相位形成的 A_hat 与估计噪声为固定条件参数。图为本稿后验的重新绘制，采用 Cai 的两模块组织依据。 |
| Gaussian projection；extrinsic message / Gaussian 投影、外信息消息 | Cai v2 §III-A 式(9)–(11)、§III-B 式(32)–(42)；Minka2001 §2–3；Ma2015 §II-A–B | 图下部用现有正文符号 R_L,k、v_L 和 X_k,out、γ_out 标出阻尼前的双向消息。学习模型为去噪模块提供条件信道统计量和活动密度比。 |


## 论文细节精简后的定位更新（2026-10-18）

本轮未新增方法名称或改变已有术语含义。当前正文为 60 个编号公式；旧记录中的附录编号是对应历史版本的定位。conditional mean-squared error 与均值误差分解现在合写于 IV-B 的 `conditional-risk`（式(48)）；共享方差的期望负对数 Gaussian 密度解释在 III-B，更新式 `pooled-variance` 不变。原停止附录 C 现在是附录 A，其三个公式和两个计数器定义保留。标准 DSM 证明和路径展开的原始源文件仍保存于 `paper/sections/appendix_second_order_training.tex`、`paper/sections/appendix_path_operator.tex`，不再编入主 PDF。Cai、Shen 的逐项原文位置与删减依据见 `paper/checks/detail_revision_20261018_224215/REVISION_REPORT.md`。


## 三张矢量图的来源及当前对应（2026-10-18）

本轮图中文字沿用既有正文符号与已登记术语，不新增方法名称。下列页码为本地文献 PDF 页码。图形均依据本项目模型重新绘制，参考论文仅作为图形组织及标注粒度的依据。

| 图 | 参考原文位置 | 本稿对应与边界 |
|---|---|---|
| 系统与传输方案 | Shen，Fig. 1，PDF p.3，卫星场景与 UPA 插图 | 本稿 II 的用户活动、参考时延、残余时延／Doppler、Q 帧 AFDM、CPP 和跨帧相位。场景图为示意，无测量数据含义。 |
| 后验因子图与矩阵重组 | Cai，Fig. 2，PDF p.5，变量／因子节点及矩阵重组 | 本稿 III 的工作后验与 X 的逐用户张量重组；蓝色表示选定用户块，并不表示已检出活动。原图下部的模块消息示意迁至 Fig. 3，本节以前的图下部定位属于历史版本。 |
| 整体接收机与去噪网络结构 | Cai，Fig. 3，PDF p.10；Shen，Fig. 3，PDF p.7；Fig. 4，PDF p.11 | 本稿 III–V 的一次性参数估计、线性估计、输入／输出阻尼、外信息反馈；Sθ 与 Tψ 并行接收 R_k,v，分类器另接收当前 F_k；共享方差、site 更新、先验校正和活动混合矩按本文公式与实现绘制。网络权重在接收迭代中固定。 |

绘图与核验详见 `paper/checks/vector_figures_20261018_225446/FIGURE_REPORT.md`。


2026-10-18 第一幅图的视觉来源补充：Shen Fig. 1（本地 PDF p.3）的接入场景与 UPA 组织；Ding Fig. 1（本地 PDF p.3，The Architecture of GNN-ASPL）的整体／局部展开组织。Ding 此图不是卫星场景或导频帧图；本稿的 CPP、Q 帧和相位因子均依据本稿 II。借用图形组织不引入 GNN-ASPL、层展开训练等方法定义。核对记录：`paper/checks/shen_ding_figure_20261018_231306/REFERENCE_AND_REVISION.md`。


2026-10-18 系统图物理标注修订：以本稿 II-A 的 `geometry`、`path-delay`、`upa` 为准，使用已有符号 ‖g_k−s‖、c₀τ_c、u_k、e_y、e_z；未新增技术术语。图中阵元位于参考点 s 的 −e_y/−e_z 方向。Shen Fig. 1（PDF p.3）的距离与差分时延分开表达是视觉参考，本稿每终端共享 Doppler 的假设保持不变。详见 `paper/checks/figure_physics_20261018_231920/REVISION_REPORT.md`。


## Figure 1：卫星物理量与 AFDM 域的当前定位（2026-10-18，文献复核后）

本条为第一幅图的最新对应；上面的历次绘图说明保留作历史记录。本稿 ν_k 未经公共 Doppler 补偿，不能称为“补偿后的残余 Doppler”。τ_kℓ 为公共时延补偿后的路径时延，含额外多径项；‖g_k−s‖ 与 c₀τ_c 才是图中距离。

| 既有术语/操作 | 原文定位 | 当前图中含义 |
|---|---|---|
| common delay、Doppler shift / 公共时延、多普勒频移 | Shen arXiv:2412.20806v1，Fig. 1、II-A 式(1)，PDF p.3；Li/Gao/Xia arXiv:2207.11958，II-B 式(2)及说明，PDF pp.3–4 | 以本稿 geometry、path-delay 为准；Shen 的每路径 Doppler 与本稿共同用户 Doppler 不是同一假设。图只保留几何距离及参考距离。 |
| DAFT domain、IDAFT、chirp-periodic prefix / DAFT 域、逆离散仿射 Fourier 变换、啁啾周期前缀 | Bemani ISWCS2021，Fig. 1/式(1)–(6)，PDF p.2；Fig. 2–3，p.3；Bemani arXiv:2204.12798v2 Fig. 1、6–7，PDF pp.8、20 | p_qk 是 DAFT 域全导频，经 IDAFT 成为 s_qk，再添加时域 CPP。嵌入式方案的 DAFT 域零保护不是 CPP。 |
| AFDM modulation / AFDM 调制 | Xu，DOI 10.1109/TCOMM.2025.3628748，Fig. 1、II 式(4)–(8)，PDF p.3（印刷 p.2） | 借鉴场景与信号/变换分层；导频内容和符号沿用本稿，不移植其未知数据检测问题。 |
| time-domain pilot arrangement / 时域导频安排 | Li 等，EURECOM report 8323，Fig. 2/式(11)，PDF p.4；Fig. 3，p.6 | 仅用于辨清时域与 DAFT 域及图形组织；本稿没有该文的 ZC 导频和 CP/CCP 数据结构。 |
| inter-frame phase increment / 帧间相位增量 | 本稿 effective-pilot 与 observation-tensor；实现 continuous.py 的逐帧 Doppler 相位 | exp(jqβ_k) 为信道演化在感知矩阵中的表示，从发送帧示意移除，正文定义保持。 |

逐篇来源链接、原图裁片、实现对应与验证见 `paper/checks/figure_literature_20261018/REVIEW_AND_REVISION.md`。此次未新增方法名或改变术语含义。


2026-10-18 Figure 1 元素复用：场景图直接采用 Shen Fig. 1（arXiv:2412.20806v1，PDF p.3）的选定矢量路径，保留卫星、覆盖区、终端、链路与阵元的原有形状和相对比例。文字以本文的 geometry、path-delay 及 UPA 定义为准；图注已引用 shen2025。本文 AFDM 帧内容沿用上一条记录。源路径、提取脚本和逐元素索引见 `paper/checks/figure_reuse_20261018/REUSE_RECORD.md`。


2026-10-18 Figure 1 帧图复用：直接采用 Bemani arXiv:2204.12798v2 Fig. 6（PDF p.20）的矩形与分组括号矢量路径，按本文全导频结构组合。域转换排列参考 Li EURECOM 8323 Fig. 2（PDF p.4），以 p_qk 经 IDAFT 对应 s_qk，时域每帧为 CPP 与 N 个有效采样；Q 为本稿帧数。图注引用 bemani2022，精确版本和路径索引见 `paper/checks/frame_reuse_20261018/REUSE_RECORD.md`。该复用只涉及图形元素，不改变 pilot、cpp 或 effective-pilot 定义。


2026-10-18 Figure 1 图标与参考距离：卫星和 UPA 面板/阵元路径改用 Li/Gao/Xia（arXiv:2207.11958）Fig. 1，PDF p.3。图上 d_ref 表示卫星到波束覆盖区内最近地面点的距离，第 II-A 章定义 τ_c=d_ref/c₀；物理对应依据 Shen Fig. 1 与 II-A（PDF p.3）的 d₀ 和公共时延关系。采用 d_ref 避开本文 III-D 已有的归一化时延搜索初值 d₀。此为既有物理量的记号简化，原有路径时延公式保持不变。图标路径和修订证据见 `paper/checks/scene_icons_20261018/REVISION_RECORD.md`。


2026-10-19 Figure 1 完整 AFDM 链路：沿用 Xu Fig. 1（本地接收稿 PDF p.3/印刷 p.2）和 Bemani Fig. 1 中的 AFDM modulation and demodulation、IDAFT、DAFT、Add CPP、Remove CPP。新增记号 Λ_c 的对角元定义为 exp(−j2πcr²)，F 为单位酉 DFT；本稿既有 DAFT 元素式给出 F_A=Λ_c2 F Λ_c1。发送处理顺序为 Λ_c2^H → IFFT → Λ_c1^H；接收为 Λ_c1 → FFT → Λ_c2。图中的 y_qm 是既有 Y_qmr 按 r 排列的 N 维向量。未新增方法名称。Xu 的模块与分组括号直接提取为 TikZ 路径，图注已引用 xu2026。出处、元数据及矩阵验证见 `paper/checks/full_afdm_20261019/REVISION_RECORD.md`。


2026-10-19 Figure 1 文字精简：未新增术语；既有 y_qm 定义移至正文 observation-tensor 后，变换与帧长定义沿用第 II 章。图内仅保留模块名称与必要标注。见 `paper/checks/figure_text_trim_20261019/REVISION_RECORD.md`。

## BG-TMP 同框架先验对照（2026-10-19）

| 原词 / 中文 | 原文位置 | 本项目使用范围 |
|---|---|---|
| BG-TMP；i.i.d. Gaussian channel denoiser / 独立同分布高斯信道去噪器 | [Cai et al. v2](https://arxiv.org/html/2506.00581v2#S6.SS3)，§VI-C、Fig. 5；TMP 框架见 Algorithm 1 | 用户授权新增 AFDM 适配对照，复用 Proposed 线性/外信息更新、阻尼、归一化、估噪，采用固定训练功率的 Gaussian 活跃信道先验及一致的解析 Bernoulli 活动后验。不是完整复现 Cai OFDM 接收机；与 Proposed 的对照包含活动证据替换。定义与验证见 `runs/bg_tmp_convergence_300_20261019/PROTOCOL.md`。 |


2026-10-19 Figure 2 审查（未改图）：Cai Fig. 2 / Table II / III-A（PDF p.5，印刷 p.3579）的 factor graph、variable nodes、factor nodes 与 vector-matrix reorganization；Shen Fig. 2 / III-A（PDF p.6）、Fig. 3（p.7）的因子图与模块分离。本文维数与重排仍以式(13)为准，j=mN+r，矩阵用户块 N×MN 对应张量 M×N×N；未引入新术语。详见 `paper/checks/figure2_audit_20261019/AUDIT.md`。


2026-10-19 Figure 2 精简版：按上述审查实施，继续使用已有 factor graph、variable/factor nodes 和 reshape 描述。m、r、n 分别对应天线、DAFT 输出及输入索引；图注与正文明确按式(13)组织，j=mN+r。无新算法名，因子连接与式(17)保持。见 `paper/checks/figure2_revision_20261019/REVISION_RECORD.md`。


2026-10-19 Figure 2 当前对应：仅展示本文式(17)的 posterior factor graph，节点类型及先验/约束含义沿用 Cai Fig. 2 / Table II（PDF p.5）与本文 III 开头；各因子和变量记号保持不变。见 `paper/checks/figure2_factor_graph_20261019/REVISION_RECORD.md`。


2026-10-19 Figure 2 完整因子图：图形组织参考 Cai Fig. 2、Table II、III-A（本地 PDF p.5，印刷 p.3579；后验分解见 Eq. (5)，PDF p.4）的逐列似然、变量／因子节点、vector-matrix reorganization 和模块划分；Shen Fig. 2 / III-A（PDF p.6）及 Fig. 3（p.7）用于核对因子图与模块边界的表达。图内 Linear estimation 与 Channel and activity denoising 沿用本文 III 的既有操作名称。本文列索引 j=mN+r，f_{Y,j}=CN(y_j; Ahat x_j, sigmahat² I_Q)，不同列的似然相乘对应式(17)的观测因子；中央 KN×MN 矩阵按式(13)展示同一组元素的列分组和用户块分组，不引入额外随机变量或概率因子。各用户的 f_delta、f_H、f_alpha 均按本文工作后验展开，不移植参考文献的未知数据或 MRF 模型。详见 `paper/checks/figure2_complete_20261019/REVISION_RECORD.md`。


2026-10-19 Figure 2 中央矩阵改用 Cai Fig. 2（PDF p.5／印刷 p.3579）的显式元素、灰色列带和蓝色用户块表达。图注定义 x_{kn}^{(j)}=[X]_{(k−1)N+n,j}，其中 j=mN+r；该标记仅是既有矩阵元素的简写，维数仍为 KN×MN，不改变本文式(13)的张量映射或任何概率因子。见 `paper/checks/figure2_cai_matrix_20261019/REVISION_RECORD.md`。


2026-10-19 Figure 3 图形与数据依据：Cai Fig. 3（本地 PDF p.10／印刷 p.3584）用于输入、条件均值／外信息及 score 网络分支的图形组织；Shen Fig. 3（PDF p.7）与 Fig. 4（p.11）用于模块消息和局部展开的组织。本文 First-order score、Second-order score、Gaussian site、conditional moments、activity mixture 和 prior correction 均沿用 III–V 的既有含义与来源。R_k 经 S_theta 的式(44)读出 F_k；T_psi 经式(46)读出标量误差估计，分类器 z_phi 与活动先验修正给出 p_k，式(27)–(30)得到最终均值。彩色矩阵来自固定验证信道上的一次 AWGN 查询，展示同一天线的 DAFT 输出／输入平面幅度，统一色标，不表示 score 原始输出或完整接收机迭代性能。生成脚本、数据及冻结权重绑定见 `paper/checks/figure3_revision_20261019/EXAMPLE.json`。


2026-10-19 Figure 3 神经网络示意：依 Cai Fig. 3（本地 PDF p.10／印刷 p.3584）使用输入、隐藏与输出节点表示学习映射 S_theta、T_psi、z_phi。两条 score 映射为多维输出，分类器为单个 logit 输出。图示层数及连线为示意；实际模型仍是冻结的 DirectCaiNetwork / ContinuousCaiBackbone / NCSN 与 EvidenceNetwork。未新增算法术语或改变神经网络实现。详见 `paper/checks/figure3_network_symbols_20261019/REVISION_RECORD.md`。


## 论文独立去噪实验（2026-10-19）

第 VI 章沿用 Cai §VI-A 的样本、训练与评价设置，以及 §VI-B / Fig.4 的独立去噪组织；参数表形式参考 Shen 仿真部分 Table I。仅借鉴组织方式，数值取自本项目冻结运行配置。

- SOMP：沿用本表 Tropp Algorithm 3.1、§3.2 的名称；GAMP-SBL：沿用 Zhang pp.15058–15059、式(3)–(19)、Algorithm 1；GNN-ASPL：Ding pp.3–5、式(12)–(28)；off-grid SBL：Wei §III-B、§IV、Algorithm 1。本节评价它们在恒等观测算子下的项目适配，保留原配置和 GNN 权重。
- LS、Gaussian-prior estimate、genie-aided conditional MMSE：沿用“独立去噪下界”和“独立去噪对照方法核对”已有出处。Gaussian 曲线明确为 P_tr/(P_tr+v) 乘输入，Genie 使用真实几何、路径功率、LOS 复增益及解析条件误差。
- NMSE：与 Cai §VI-B 的归一化均方误差及 Shen 仿真评价指标名称一致；本文明确使用全部测试信道误差能量与信道能量之比，不平均逐样本 dB。
- 字典表示误差和 Off-grid 一阶原子近似／精确重建差异是本项目诊断结论，依据 `results/denoising_baseline_diagnosis_20261019/REPORT.md`；不表述为参考文献算法本身的固有限制。

逐段证据及数值核验见 `paper/checks/denoising_section_20261019/REVISION_RECORD.md`。


## 接收机模块简称（2026-10-19）

用户批准在第三幅图使用 PNE、LE、CAD 作为本文模块简称；它们用于定位已有操作，不构成新的算法名称，也不声称这些缩写均为参考文献原有用法。

| 本文简称 | 全称与本稿对应 | 命名依据与边界 |
|---|---|---|
| PNE | phase and noise estimation；III-D Parameter Estimation | 概括本文相位和噪声估计两个既有步骤；PNE 是本文定义的简称。 |
| LE | linear estimation；III-A | 沿用 Cai §III-A 的 linear estimator 含义，对应本文线性估计模块。 |
| CAD | channel and activity denoising；III-B | 对应 Cai §III-B 的 Channel and Device Activity Denoisers 及本稿既有信道和活动去噪操作；CAD 是本文定义的简称。 |

仅参考 Shen §I（PDF pp.2–3）及 Fig.3（PDF p.7）以 DDAI、JCESD、TSE 标识模块的组织方式，不移用其模块功能。本文全称在第 V 章开头与 Fig.3 图注定义，图中同尺寸模块统一使用三个简称。

## Score 网络与 MP/AMP 替代方法核查（2026-10-19）

本节是用户要求的文献检索，不代表采用新算法。来源、检索范围、反证和项目推断见 `references/score_mp_alternatives_20261019/SOURCE_AUDIT.json`；没有新增接收机实验或修改冻结主线。

| 文献原词／忠实译名 | 原始来源与定位 | 本项目使用边界 |
|---|---|---|
| block-diagonal covariance matrix approximation / 块对角协方差矩阵近似 | [Yao–McLaughlin–Altmann，Patch-Based Image Restoration using Expectation Propagation](https://arxiv.org/html/2106.15327v2)，SIAM JIS 2022，§2.2–2.4、§7 | 原文块内保留非对角协方差，先验是显式 GMM；不是已发表的 score-AFDM 算法。§7 明确强远距离相关、压缩感知等情形可能效果不佳，不能照搬图像分块。用户局部 Gaussian site 不等于联合后验块对角；保留实际似然诱导的跨用户耦合是待验证的项目设计。 |
| diagonal plus low-rank constraints / 对角加低秩约束 | [Shen–McLaughlin–Altmann，Expectation-Propagation with Low-Rank Constraints for Linear Inverse Problems](https://pure.hw.ac.uk/ws/portalfiles/portal/96064854/Shen_EUSIPCO2023_final.pdf)，EUSIPCO 2023，§III，印刷 pp.1829–1830 | 为保留部分相关性提供结构化 Gaussian 协方差先例；原文为中等规模显式稀疏先验研究。接入非可分 score、活动变量与 AFDM 均需另行推导，低秩截断仍是近似。 |
| block uniform diagonalization / 分块均匀对角化 | [Fletcher 等 GEC](https://arxiv.org/html/1602.07795v2)，§II-A 式(6)–(9)；[D-GEC](https://arxiv.org/html/2206.05049v2)，§III-A 式(31)、(34)，§III-B | 每块／子带一标量，不是块内完整协方差。D-GEC 的变换域有色去噪是依据，不保证固定 AFDM 的消息 Gaussian 化。 |
| Score-Based VAMP (SC-VAMP)；Fisher-information-based Onsager correction / 基于得分的 VAMP、基于 Fisher 信息的 Onsager 校正 | [Wadayama–Takahashi 2026预印本](https://arxiv.org/html/2601.07095v1)，§III-A 式(1)–(7)、§III-D 式(40)–(46)、§VI-D | 直接 score 接口及无 Jacobian 的校正计算；保留标量 AWGN cavity、大系统与混合条件，不能将其描述为消除本项目有色、信号相关消息的算法。 |
| Factor-Wise Parameter Learning in Score-Based VAMP / 基于得分的 VAMP 中逐因子参数学习 | [Na–Wadayama 2026预印本v2](https://arxiv.org/html/2607.14597v2)，§II 式(1)–(2)、§II-C 式(5)–(6) | v2 日期2026-09-16，标题不同于此前记录的 v1。逐坐标 Bernoulli–Gaussian 参数学习不等于用户块 score JADCE；已知右旋转不变算子与标量 cavity 条件仍在。历史 v1 定位保留。 |
| multiuser OAMP (MU-OAMP) / 多用户 OAMP | [Çakmak 等 2026预印本](https://arxiv.org/html/2606.26777v1)，§I 式(1)–(4)、§II-A 式(7)后的方差约束、§III | 非可分用户先验与独立右酉不变预编码的多用户框架；每用户仍一标量方差。当前重复 MMV 算子不是整个用户向量上的 Haar 混合，不能通过纯坐标旋转继承定理。 |
| Approximate Message Passing with Unitary Transformation (UT-AMP) / 使用酉变换的近似消息传递 | [Guo–Xi 2015](https://arxiv.org/html/1504.04799v1)，§III-A 式(8)–(11)、§III-B Theorem 1及后文 | 平均方差等近似仍在；任意矩阵收敛结论限定 Gaussian 先验，不直接覆盖非可分 score 网络。 |
| Plug-and-Play Diffusion Models (PnP-DM)；Split Gibbs Sampler (SGS) / 即插即用扩散模型、分裂 Gibbs 采样器 | [Wu 等，Principled Probabilistic Imaging using Diffusion Models as Plug-and-Play Priors](https://arxiv.org/html/2405.18782v2)，NeurIPS 2024，§2 式(3)–(4)、§3.1–3.2 式(5)–(7)、§3.4、Appendix A.3 | MP/AMP 之外的对照路线：Gaussian 条件来自辅助概率模型，不依赖实际 LE 误差白化。有限分裂参数、采样、离散与 score 误差仍需分开；固定输入下确定性 probability-flow ODE 不能替代随机 SDE 的条件后验采样保证；活动变量需适配。 |

### 不依赖标量伪 AWGN 的 MP 补充核查（2026-10-19）

前次候选以 AMP/VAMP/GEC 为主，遗漏了以下直接相关的 MP 文献；不能将该检索范围限制表述为所有 MP 的必要条件。以下方法并非已验证的 AFDM 接收机。

| 原文术语 | 原始来源与定位 | 适用边界与本项目推断 |
|---|---|---|
| Stein Variational Message Passing；graphical SVGD / Stein 变分消息传递 | [Wang、Zeng、Liu，ICML 2018](https://proceedings.mlr.press/v80/wang18l/wang18l.pdf)，§3、§3.1 式(8)、Algorithm 1、§3.3 | 用目标 log-density 梯度与局部核推进粒子，不要求 LE 伪观测为独立 AWGN；属于图结构变分 MP，不是 AMP，也不等同于 sum-product BP。§3.3 的局部条件匹配不一般保证联合分布恢复。固定算子、已知活动时，用先验 score 加精确似然梯度是本项目拟议适配；有限噪声网络给平滑先验 score，不能直接称原后验精确推断。密集耦合会削弱局部核的计算优势。 |
| Stein Variational Belief Propagation (SVBP) / Stein 变分置信传播 | [Pavlasek 等原文](https://arxiv.org/html/2311.16916v2)，§III-B 式(4)、§IV 式(7)–(9)、Algorithm 1 | 基于粒子 BP 消息与 Stein 粒子更新，可表达非高斯、多峰边缘，无 LE 白噪声前提。式(4)、(9)一般涉及势函数数值／重要性比，不能仅凭现有 score 就宣称即插即用；原文当前 belief 作 proposal 的实践简化亦需核对有限粒子实现。有环 BP 与粒子近似仍在。 |
| Nonparametric Belief Propagation (NBP) / 非参数置信传播 | [Sudderth 等作者全文，CACM 2010](https://ics.uci.edu/~sudderth/papers/cacm10nbp.pdf)，§2–3；原始 CVPR 2003 工作由原文注明 | 连续非高斯消息以粒子／混合分布近似；Gaussian 核不等于把 LE 误差假设为独立 AWGN。高维积分、粒子数量与环路误差是另外的限制。 |

本次仅补充检索与术语依据，没有运行新实验。需要区分三项独立判断：方法属于 MP、不依赖伪 AWGN、适合当前 AFDM 且有可接受成本；前两项不推出第三项。

### 学习展开与粒子 MP 的进一步区分（2026-10-19）

| 原文术语 | 原始来源与定位 | 适用边界 |
|---|---|---|
| Learned Score-Based Turbo Message Passing (L-STMP) / 学习式基于得分的 Turbo 消息传递 | [Wei–Yuan，2026-10-13预印本](https://arxiv.org/html/2610.17785v1)，§III-A–D，式(8)–(12)，§IV–V | 原文明确针对有限维、结构化压缩矩阵导致的 AWGN 外信息失配，联合训练逐层校准参数和预训练 score 网络。仍保留标量／通道级方差、Tweedie 形式更新与外信息公式；属于通过学习补偿失配的展开方法，不能说已严格消除 Gaussian 消息近似或证明任意 AFDM 适用。验证对象为单用户空间压缩，非多用户 AFDM 活动检测。微调后的网络也不能未经检查仍视为准确的先验密度梯度。 |
| Message Passing Stein Variational Gradient Descent (MP-SVGD) / 消息传递 Stein 变分梯度下降 | [Zhuo等，ICML 2018](https://proceedings.mlr.press/v80/zhuo18a/zhuo18a.pdf)，§2式(2)–(3)、§4、Algorithm 1 | 基于图结构、目标密度梯度和局部核的粒子推断，没有 LE 独立 AWGN 接口；原文未嵌入现代扩散 score 网络。以学习的先验梯度替换解析先验梯度属于拟议适配；密集 AFDM 图、有限粒子、平滑先验及活动变量需另行处理，不继承原文全部理论保证。 |

L-STMP 细读与本地实现映射见 `references/score_mp_alternatives_20261019/LSTMP_CLOSE_READING.json`。§III-B 式(8)的 gamma 作用于线性后验方差，再通过式(9)–(10)影响外信息；不能误写成直接乘在线性均值残差上。§III-D 的 progressively layer-by-layer training（逐层渐进训练）联合更新新层与前面各层，和仅在人工 AWGN 查询上重训先验不同。本文建议的有界方差比参数化、活动监督及实际消息训练属于项目适配，并非该论文已给出的多用户 AFDM 算法。残差方差式(12)的零空间不可辨识与同观测噪声交叉项问题是本项目公式审查推论，不是原论文实验结论。

本机三个网络的小规模适配验证见 `experiments/lstmp_three_networks_20261019/run.py` 与 `results/lstmp_three_networks_20261019/PLAN.json`、`RESULTS.json`、`ANALYSIS.json`。该实现使用一般观测矩阵的 LMMSE，保留二阶 score 的方差更新，五层共享三个网络；方差乘子作用于二阶 score 给出的后验方差，并非原论文式(12)的观测残差方差。活动 logit 校准、可学习阻尼、有界线性后验方差比均为本项目适配。采用完整五层共同优化，未复现原文逐层渐进训练或逐层独立网络。结果只覆盖已知相位、已知噪声、0 dB 的独立 8/4/8 训练／验证／测试场景，不能据此判断原版 L-STMP 的性能，也没有验证消息已成为独立 AWGN。

2026-10-19 按用户要求下载的 L-STMP v1 全文保存在 `references/lstmp_2610_17785/wei_yuan_2026_lstmp_v1.pdf`（5页）；重新训练路线的阅读记录见同目录 `READING_AND_RETRAINING.json`。p.3 §III-D 明确使用预训练后联合训练，p.4 §V-A 明确各层独立 NCSN++、VE SDE 和层间损失权重；p.3 Fig.1／式(12)明确采用残差方差而非二阶 score。重新从 AFDM 数据预训练一套新权重再逐层训练，与继续微调本机旧三个权重是不同实验；随机初始化后跳过 score 预训练直接端到端训练则未被原文实验覆盖。新训练路线尚未执行。

### L-STMP 新权重训练候选启动（2026-10-19）

用户随后授权开始新路线，执行记录见 `runs/lstmp_fresh_20261019/MANIFEST.json`、`STATUS.json`，源实现见 `experiments/lstmp_fresh_20261019/`。NCSN++ 骨干来自 [Song 等官方实现](https://github.com/yang-song/score_sde_pytorch/blob/cb1f359f4aadf0ff9a5e122fe8fffc9451fd6e44/models/ncsnpp.py)，固定提交 `cb1f359f4aadf0ff9a5e122fe8fffc9451fd6e44`；许可证、原文件哈希和最小依赖适配记录于候选 `vendor/PROVENANCE.json`。16×16 输入、32 个实数通道、基础宽度64、关闭 FIR 等是本项目实现选择，非 L-STMP 作者披露的完整配置。

候选从随机初始化进行一阶 denoising score matching（去噪得分匹配），复噪声方差 v 对应每实坐标方差 v/2；目标为实坐标平均的 `||sqrt(v/2)*s_theta(r,v)+epsilon||^2`。随后按 L-STMP §III-D 的顺序逐层增加独立 score 网络，每阶段联合更新已有层；新活动分支、一般矩阵 LMMSE，以及残差方差的 softplus 正性处理和有界外信息方差比均为项目扩展。最后一层残差方差系数在该深度下不影响最终均值损失，加入下一层后才获得该反馈路径的训练梯度。预训练与展开训练均不载入旧网络；旧权重仅用于最后的独立测试对照。当前先运行已知相位、已知噪声诊断，不能将其结果称为未知相位接收机性能；进度和结果以运行目录为准。
