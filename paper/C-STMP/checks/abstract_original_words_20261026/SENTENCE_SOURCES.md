> 本文件为此前版本的历史逐句记录。2026-10-27作者确认定稿已编译，当前依据见 [定稿记录](../abstract_final_20261027/SENTENCE_SOURCES.md)。

# C-STMP 摘要逐句依据

当前摘要175词、八句。第2–4句保留传输与先验学习重点，共72词。第5–7句共64词，依次交代去噪器提供信道后验矩、密度比估计器提供活动概率，以及由两类估计形成软信息，与线性估计模块迭代交换。第8句为既有基准比较。

词汇范围为 Shen2025、Huang2026、Cai2026 和 D-GEC。各句均为本项目适配或改写，不声称完整照录。原词核验不替代技术含义核对，也不意味着参考论文已经提出本项目全部组合。

## 第 1 句：研究对象与应用条件

This paper investigates grant-free random access in low Earth orbit satellite Internet-of-Things systems without global navigation satellite system (GNSS) assistance.

- 原文位置：Shen2025 摘要（PDF p.1）；Cai2026 摘要（PDF p.1）。
- 含义与边界：开头聚焦无 GNSS 辅助的卫星免授权接入，以对应标题；JADCE 的定义位于第7句。不是任何一篇的完整原句。

## 第 2 句：第一点——处理大差分时延和多普勒

We firstly propose a multi-frame transmission scheme with affine frequency division multiplexing (AFDM) to handle the large differential delay and Doppler shift at the satellite receiver, and derive the input-output relationship.

- 原文位置：Shen2025 摘要与 §II-B（PDF pp.1、4–5，式(8)–(10)）；Huang2026 §II（PDF p.2）。
- 含义与边界：保留多帧 AFDM 方案和输入输出关系，明确在卫星接收端处理大差分时延和多普勒。卫星端处理的直接依据还包括本稿系统模型开头（sections/02_system_model.tex 第8–10行），保留公共定时及参考时延补偿条件。Shen 的原方案采用 OTFS，本稿的 AFDM 输入输出关系由正文推导；不将本稿组合归为 Shen 原算法。多帧准静态及观测数量的机制说明仍在正文，摘要不再单独展开。

## 第 3 句：第二点——直接学习 AFDM 有效信道先验

Subsequently, we learn a score-based generative channel prior directly on the AFDM effective channel with fractional delay and Doppler, without restrictive sparse or grid-aligned channel assumptions.

- 原文位置：Huang2026 摘要与 §III-A（PDF pp.1、3，式(6)–(7)）；Cai2026 §I-A（PDF p.2）；Subsequently 见 Shen PDF p.2。
- 含义与边界：沿用直接在 AFDM effective channel 上学习及避免 restrictive sparse or grid-aligned channel assumptions 的表述。fractional delay and Doppler 说明所学信道的物理效应，不声称新增鲁棒性实验或完全没有任何训练分布假设。本稿使用去噪训练与 TMP 推断，不采用 Huang 的 Langevin 后验采样。

## 第 4 句：第二点的训练方法——有色高斯噪声

The training uses colored Gaussian noise to account for correlations in the denoiser input error.

- 原文位置：D-GEC 摘要与 §I（PDF pp.1–2）、§III-A（PDF p.11，式(28)）、§III-B（PDF pp.15–16，式(38)–(41)）；本稿第 IV-A 节。
- 含义与边界：The training 回指上一句同一次先验学习；colored Gaussian noise 与 denoiser input error 采用原词。这里是去噪器输入误差的相关性，不是信道自身相关性；训练目的不等于在线误差已被精确匹配，也不单独宣称已证明有色训练的因果收益。

## 第 5–7 句：条件信道统计量与活动不确定性的承接

The learned prior is then incorporated into a message passing (MP) receiver as a minimum mean-squared error (MMSE) denoiser, providing posterior mean and variance estimates without calculating high-dimensional integrals. To incorporate activity uncertainty into channel estimation, a learned density ratio estimator provides activity probabilities. The resulting soft information is iteratively exchanged with the linear estimation module for joint activity detection and channel estimation (JADCE).

- 原文依据：Cai2026 §III-B（PDF p.6，式(15)之后）说明信道去噪条件于活跃假设，并明确 activity uncertainty 通过活动更新处理；PDF pp.7–8讨论后验矩高维积分。density ratio estimator 的原术语见 Menon–Ong §4.2式(17)，其方法应用于本稿的活动分支。
- 本稿依据：第III节 exact-local-moments、mixture与joint-spatial-covariance中，活动概率对条件均值加权，并贡献p(1-p)项的活动不确定性；第IV-B节以条件均值及其导数得到信道统计量，第IV-C节训练密度比网络。第二句动机是将活动不确定性纳入信道估计，不再重复声称避免某种密度计算。
- 实现边界：分类器读取观测R、输入噪声方差v和去噪均值F及派生特征，不读取后验方差tau。原始输出是logit，经活动先验校正和sigmoid才得到概率。本句概括整个活动概率估计过程，不声称原始网络输出直接是概率，也不保证精确后验。
- 贡献边界：Cai也处理activity uncertainty；本稿与其不同的是学习密度比估计器，而非首次考虑活动不确定性。未新增性能、速度或消融结论，保留MP中的Gaussian近似。所有词形仍经四篇核验，密度比估计器连续术语另依Menon–Ong记录。

## 第 8 句：相同基准接收机的性能比较

Numerical simulations demonstrate that the proposed receiver outperforms the baseline receiver in terms of activity detection and channel estimation.

- 原文位置：结句句式参照 Shen/Cai 摘要，outperforms 同见 Huang 摘要，baseline 词形见 Cai2026 正文。性能依据仍为本项目保存结果。
- 含义与边界：the baseline receiver 仅指正文定义的项目原始 STMP 接收机；改为上位称呼不改变比较对象，也不扩展为全部基准或全部MP方法。既有六档SNR、每档1000场景采用已知跨帧相位及估计噪声方差；具体条件保留在正文。

## 当前核验与编译状态

- [以学习先验为主的 MP 接收段记录](RECEIVER_SOFT_INFORMATION_CLOSING.json)
- [当前源文件差异](RECEIVER_SOFT_INFORMATION_CLOSING.diff)
- [四篇来源逐词核验](WORD_AUDIT.json)
- [连续技术短语核验](TERM_AUDIT.json)
- [检查汇总](SOURCE_WORD_CHECK.md)
- [中英文摘要](phase5_abstract/abstract.md)

结果依据：result/snr_comparison/data/c_stmp_variance_em_1000_snr_m4_p6_20261025/SUMMARY.json。此次仅调整叙述，不运行训练或实验。

遵循作者要求，当前只更新源稿，确认措辞后再编译；现有 main.pdf 保留上一编译版本。此前 COHESION_CHECK.json、RECEIVER_PARAPHRASE_CHECK.json、RECEIVER_FRAMEWORK_TRANSITION.json 和 RECEIVER_JOINT_DENOISING.json 均为历史措辞。当前来源与句号编号以本文件为准。

本轮命名核对：density ratio estimator 是 Menon–Ong §4.2式(17)之前的连续原词（PDF p.3 / 印刷p.306），本轮直接核对官方PDF。learned 修饰本稿通过分类训练获得的估计器，不自造缩写或宣称新的通用密度比算法。

本轮仅删去摘要中的特征枚举。provides activity probabilities指密度比估计器结合活动先验后的概率读出；不把网络原始logit等同于概率。实际输入R、v、F及派生特征保留正文，F仅是去噪均值，不包含后验方差。

本轮收尾依据：本稿第III节mixture、joint-spatial-covariance和joint-average-variance将活动概率与条件信道矩组合，随后形成外信息反馈与迭代。Cai2026 §III-B/C及算法1（PDF pp.7–8）提供相应消息传递背景。本句不声称两个网络直接彼此交换消息或单独决定全部线性更新；网络输出的概率与统计量均指正文规定的读出过程。

本轮收尾句来源：Shen2025摘要（PDF p.1）以soft information在模块间交换描述接收机；§III前后（PDF pp.5–6）说明iteratively exchanged。Cai2026 §I-A（PDF p.2）、§III（PDF p.5）说明linear estimation与denoising模块间迭代。本稿第III节开头及消息更新与上述结构一致。resulting soft information指由条件信道矩、活动概率形成的外信息；不把两个网络说成独立彼此交换消息，也不声称把原始概率直接送入线性估计器。该句为适配本稿的改写，不是任何单篇完整原句。
