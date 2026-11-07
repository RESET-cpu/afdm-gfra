# 基础论文、STMP 与展开：下载后复核

日期：2026-10-24。按本地 PDF 页码定位；这是围绕本项目问题的相关章节阅读，不宣称逐页审完全部证明。与其他三份 follow-up 合并使用。

| 本地原文 | 核读位置 | 可参考内容及边界 |
|---|---|---|
| [01 OAMP](../../../literature/ma2017_oamp_v3.pdf) | pp.3–5，§III-A–I，式(12)–(31) | 线性模块的迹去相关；非线性模块的散度修正；最终输出可用原去噪器，反馈使用修正量。§III-E 明确当时论证并非严格证明；§III-F/G 的正交关系不能升级为有限 AFDM 下独立 AWGN。当前线性外信息已有相关操作，不是遗漏整个 OAMP 原则。 |
| [02 VAMP](../../../literature/rangan2019_vamp.pdf) | pp.2、5，§I-C/D、§III-B，Algorithm 3，式(24)–(25) | 对称地写清两个模块的后验估计、归一化散度和外信息，便于审查接口。VAMP 的 vector 不表示自动保留 MMV 列间完整协方差；本算法仍使用标量精度。其右正交不变条件不被固定 A0 满足。 |
| [03 非可分 VAMP](../../../literature/fletcher2019_nonseparable_vamp.pdf) | pp.5–9，Definitions 1–2、Assumption 1、式(12)、(18)–(21)、Theorem 1 | CNN 非可分不是否定模块化推断的理由；但需统一 Lipschitz、Gaussian 输入极限、Haar 右奇异向量与独立性。特别是 Gaussian 误差结论中的第二误差是 \(V^T(r_2-x)\)，不可改写为原坐标反馈误差必然白 Gaussian。 |
| [04 D-OAMP](../../../literature/xue2016_doamp.pdf) | pp.2–3，Algorithm 2，§3.3，式(7)–(13) | 通用去噪器的无散度反馈与 SURE 缩放。式(8)用大系统下散度自平均近似忽略其输入依赖；不是任意有限神经映射的严格零散度。项目完整 \(p\mu\) 的标量适配已失败，不建议重新原样实现。PDF 原题为 *D-OAMP: A Denoising-Based Signal Recovery Algorithm for Compressed Sensing*。 |
| [15 On OAMP](../../../literature/liu2023_orthogonal_principle.pdf) | pp.7–8，§III-G、§IV-A/C/D，式(27)–(34) | 用信号增益与误差功率描述消息，强调二者之比；可通过积分/Monte Carlo 或导数获得正交化系数。离线表是一种条件校准工具，不自动修复真实查询失配。其可分、iid、Haar 与大系统条件不能省略。零增益时不能作单位增益归一化。 |
| [21 LDAMP](../../../literature/metzler2017_ldamp.pdf) | pp.5–7，§3、§4.1/4.2，Fig.4，Footnote 5，Corollaries 1–2 | 已有三种训练方式：端到端、逐层、独立去噪器。原文每个展开层含多层 CNN，“10 层展开”不是总共 10 个卷积层。独立训练有跨测量率泛化收益；同测量率未必最好。其训练最优性依赖经验 SE 与单调性，Footnote 5 明说该文 D-AMP/LDAMP 的 SE 当时无严格证明。下载实际为 arXiv **1704.06625v4，2017-11-06**。 |
| [23 Cai STMP](../../../literature/cai2026_stmp_v2.pdf) | §III-B，式(20)、(26)–(27)、(35)–(42)；pp.9–10，§V-B，式(57)–(65)、Algorithm 2 | 应分别审查条件信道均值、活动混合矩、Gaussian 外信息。双向参数阻尼已有出处；原文逐信道功率归一化与本项目冻结全局 RMS 不同，不能只抄式(60)用于弱用户而认为先验不变。 |
| [24 L-STMP](../../../literature/wei_yuan_2026_lstmp_v1.pdf) | pp.2–3，§II、§III，式(5)–(13) | 训练层内 \(\gamma,\alpha,\beta\) 及各层 score；逐步加层时联合微调已加入层。式(6)要求 \(BB^H=I\)，式(12)的残差方差不是对任意有偏估计都成立的真实 MSE 恒等式。目标是单用户信道 NMSE，没有 JADCE 活动损失，不能直接复制为检测目标。该版本训练损失在 §III-D 正文，**式(13)是最终输出而非损失**。 |
| [25 非可分 AMP 普适性](../../../literature/lovig2026_universality.pdf) | pp.1–3，Introduction、Example 1.1、§1.1 | 新补原文，用于限定结论：即便非可分映射满足通常的二范数/Lipschitz 条件，也不能无条件把 iid Gaussian 结论推广至独立非 Gaussian；文中提出额外可逼近性条件。更不能据此宣称固定 AFDM 可用。未审阅该 82 页稿件的全部证明，不作为我们的直接构造依据。 |

## 与当前实现的具体关系

- [linear.py](../../../../src/algorithm/STMP/linear.py) 的线性后验与外信息已有迹归一化；不能把“增加 OAMP 去相关”当作全新方案。
- [denoiser.py](../../../../src/algorithm/STMP/denoiser.py) 的输出依赖活动概率；修正完整映射时需要包含概率导数。这个公式本身也已经在历史 full-matrix AMP 中实现。
- [gaussian.py](../../../../src/algorithm/STMP/gaussian.py) 使用后验矩构造 Gaussian 外信息。对精确、匹配的 Bayesian AWGN 去噪，协方差和 Jacobian 有关联；独立训练网络在真实失配输入上的两个输出不自动满足该关系。
- [iterations.py](../../../../src/algorithm/STMP/iterations.py) 的参数阻尼不是错误本身。要借鉴 Memory AMP，必须明确真实跨轮协方差如何估计，不能只换权重公式。

## 阅读中的两个不能照抄的说法

1. L-STMP §IV-A 将均匀选择 DFT 行称为“approximately right-rotationally invariant”。这里不把该描述当作严格分布性质：选择固定 DFT 基的若干行，其行空间分布并非 Haar 子空间。可引用其经验设计，不能据此套用一般右酉不变定理。
2. 非可分 VAMP 的 Gaussian 误差结论涉及旋转后的反馈坐标；不能要求所有原坐标去噪输出误差都独立于信号。我们真正需要匹配的对象首先是送入冻结 AWGN 网络的查询。

本笔记由 AI 辅助核读与整理；公式位置依据本地原文，项目判断是对代码及既有记录的分析。本轮没有新增训练或接收机实验。
