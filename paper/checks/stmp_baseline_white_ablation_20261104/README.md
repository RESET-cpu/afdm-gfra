# STMP 基线与 GP-MP 白噪声消融

2026-11-04，作者确认重新区分既有方法基线与训练噪声消融。本文主算法仍为 GP-MP-C。

| 展示名 | 实际版本 | 当前证据用途 |
|---|---|---|
| STMP | 原来展示为 GP-MP 的三网络 AFDM 适配版本；白噪声一阶、二阶得分网络，配套学习密度比活动估计器 | 与 GP-MP-C 比较整套已采用配置的效果 |
| GP-MP | 与当前 GP-MP-C 保持相同网络架构、预条件、导数方差计算规则、分类器训练流程和接收机设置，仅将一阶训练噪声改为 AWGN | 新的训练噪声消融；尚无正式评估曲线 |
| GP-MP-C | 当前有色高斯噪声训练版本及其配套分类器 | 本文方法 |

GP-MP 与 GP-MP-C 均使用各自一阶网络计算导数方差，并使用各自冻结的一阶网络重新训练分类器。数值方差与分类器权重随一阶网络变化，是训练干预的后续影响；“其余保持不变”指架构、规则、训练流程及接收机超参数一致，不是强行复用另一去噪器的分类器权重。内部 STMP/C_STMP 标识、运行路径、冻结配置和原始结果未重命名。

## 来源与解释边界

- Cai 等的 STMP：原文 §III-B, PDF p.7, 式(22)–(31)，AWGN 去噪均值/方差接口与基于高斯外信息的活动概率更新；§IV–V 的一、二阶得分网络。[原文](../../../reference/literature/cai2026.pdf)。当前 STMP 基线保留相关计算路线，但将活动更新替换为学习密度比估计，正文已明确说明，不称为未经修改的原版复现。
- Wei、Yuan，*Learned Score-Based Turbo Message Passing for Channel Recovery From Spatially Compressed Measurements*, arXiv:2610.17785v1, §I, PDF p.1：讨论有限维、结构化空间压缩与理想 STMP AWGN 条件之间的差异。[原文](../../../reference/literature/wei_yuan_2026_lstmp_v1.pdf)与[已保存来源元数据](../../../reference/literature/wei_yuan_2026_lstmp_v1.source.json)。本文据此补充失配动机，未将其称为 AFDM 有色训练收益的直接证据，也未将右旋转不变性表述成所有 AWGN 近似的必要条件。
- 本文有限维多帧 AFDM 结构化观测与上述理论条件之间的差异，提供引入相关训练扰动的研究动机；效果由配对消融检验。本文选取的随机 Kronecker 协方差不是从接收机残差拟合的经验分布。
- GP-MP/GP-MP-C 是作者指定的算法标签，非 Cai 或 Wei 原文已有名称；术语记录在 C-STMP、STMP、DU 三稿的术语文件顶部同步。

## 本轮修改

1. 正文、结果分析、评估附录中的旧 GP-MP 对照改称 STMP。基线介绍明确 AFDM 适配及学习密度比活动更新。
2. 第五章定义 GP-MP 为当前方法的 AWGN 训练变体；不添加尚未完成的结果，不声称已经验证了有色训练增益。
3. 引言补充 Wei–Yuan 对有限维结构化空间压缩下 AWGN 近似局限的引用。参考文献由 43 篇增至 44 篇。
4. 七幅实验图使用准确方法名称，包括独立去噪图中的 STMP 与 GP-MP-C；不把旧 STMP 一阶网络冒充新 GP-MP 消融。
5. 更新训练计划中的展示名与解释范围。所有启动前置条件、200/100 轮训练预算、配置路径、优化参数和执行顺序保持。仍待相位批次完成核验且退出后依次训练，不因本次命名启动实验。

## 核验

- [绘图核验](PLOT_VALIDATION.json)：七幅实验图、547 个绘图点与保存输入完全对应，原始输入 SHA-256 全部通过；绘图配置仅标签字符串发生变化。
- [稿件核验](VALIDATION.json)：main 为 13 页、main_full 为 15 页，均为 44 篇参考文献；无未定义引用、缺字、重复标签或 Overfull 越界报告。保留一般 Underfull 与 PDF 版本提示。
- 变动源文件中的编号数学环境逐块相同。未修改算法、统计量、训练科学设置或实验数值。
- 已查看两版变动页面的全部缩略图，并放大检查基线介绍、名称定义与实验图例；没有文字或图例遮挡、裁切。变动页因新增引用编号、局部换行及图例同步较多，未改动相应数学内容。
- 改前源码与 PDF 保存在 `before/`，哈希见 [before_hashes.json](before_hashes.json)；编译日志位于 `build_main/` 与 `build_full/`，预览位于 `render/`。

白噪声计划：[TRAINING_PLAN.json](../../../result/channel_denoising/data/white_preconditioned_matched_20261104/TRAINING_PLAN.json)。本记录不把准备完成等同于训练或配对评估完成。
