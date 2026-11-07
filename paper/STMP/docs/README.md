# STMP 研究文档

本目录保存本稿的方法说明、系统模型、实验协议与术语依据。共用文档为实际文件副本；后续按各稿独立维护，共用定义有变化时同步相关稿件。

文档中的日期、实验状态和性能描述保留原文，仅调整文件链接；当前状态仍以对应实验记录为准。

[返回稿件](../README.md) · [原始文档与历史记录](../../../archive/paper_layout_20261026/README.md)

| 文档 | 内容 |
|---|---|
| [ACTIVITY_DETECTOR_REVIEW_20261024.md](ACTIVITY_DETECTOR_REVIEW_20261024.md) | 当前 GFRA 实验的活动检测判据核查 |
| [ATTRIBUTION.md](ATTRIBUTION.md) | 方法来源与许可 |
| [BASELINE_ACTIVITY_READOUT.md](BASELINE_ACTIVITY_READOUT.md) | 活动判决的原文与实现 |
| [BASELINE_BUDGET_REVIEW_20261024.md](BASELINE_BUDGET_REVIEW_20261024.md) | 四个 baseline 的 AER 曲线：预算、信道重构与活动判据复核 |
| [BASELINE_GFRA_AUDIT_20261023.md](BASELINE_GFRA_AUDIT_20261023.md) | 四个 baseline 的 GFRA 文献、实现与判决核验 |
| [BASELINE_GRID.md](BASELINE_GRID.md) | 当前整数时延/Doppler 字典 |
| [BASELINE_NOISE.md](BASELINE_NOISE.md) | 五个 baseline 的噪声估计 |
| [BASELINE_PHASE.md](BASELINE_PHASE.md) | 两个 SBL 基线的后验相位更新 |
| [BASELINES.md](BASELINES.md) | 五个主线基线的实现与来源 |
| [CODE_GUIDE.md](CODE_GUIDE.md) | 当前代码导读 |
| [CURRENT_STAGE.md](CURRENT_STAGE.md) | 当前阶段 |
| [DIFFUSION_AMP.md](DIFFUSION_AMP.md) | 独立训练的 score 去噪器与矩阵 D-AMP |
| [EXPERIMENT_PROTOCOL.md](EXPERIMENT_PROTOCOL.md) | 当前实验协议 |
| [JOINT_AMP.md](JOINT_AMP.md) | 完整用户联合去噪的矩阵 D-AMP |
| [LDAMP.md](LDAMP.md) | L-DAMP 实现与验证 |
| [LDAMP_JOINT.md](LDAMP_JOINT.md) | 联合去噪 L-DAMP 候选：模型、数值核验与复现 |
| [LDAMP_SCORE.md](LDAMP_SCORE.md) | 在固定 L-DAMP 递推中替换冻结 score 去噪器 |
| [MESSAGE_AWGN_CONDITIONS_20261022.md](MESSAGE_AWGN_CONDITIONS_20261022.md) | 不同工况下的消息误差与 AWGN 假设 |
| [OFFGRID_BASELINES.md](OFFGRID_BASELINES.md) | Off-grid SBL |
| [PHASE_ESTIMATION_PROGRESS_20261022.md](PHASE_ESTIMATION_PROGRESS_20261022.md) | 相位估计候选：失败分支、训练样本匹配与独立验证 |
| [PHASE_ESTIMATION_REVIEW_20261021.md](PHASE_ESTIMATION_REVIEW_20261021.md) | AFDM 相位估计的改进方向 |
| [PHASE_MESSAGE_GEM.md](PHASE_MESSAGE_GEM.md) | 各向同性高斯消息下的一次广义EM参数更新 |
| [PROPOSED_AMP.md](PROPOSED_AMP.md) | 使用冻结 score 与活动分类器的复数矩阵 AMP |
| [PROPOSED_AMP_DAMPING.md](PROPOSED_AMP_DAMPING.md) | 冻结联合去噪器的 AMP 阻尼递推 |
| [PROPOSED_AMP_QUERY_DAMPING.md](PROPOSED_AMP_QUERY_DAMPING.md) | AMP 中的查询阻尼与完整历史校正 |
| [PROPOSED_APPROXIMATIONS.md](PROPOSED_APPROXIMATIONS.md) | Proposed 中的近似与逐项验证 |
| [PROPOSED_MAINLINE.md](PROPOSED_MAINLINE.md) | Proposed 主线与保存规则 |
| [PROPOSED_UNKNOWN_PHASE.md](PROPOSED_UNKNOWN_PHASE.md) | Proposed：估计跨帧相位后进行信道与活动推断 |
| [RESEARCH.md](RESEARCH.md) | 独立研究入口 |
| [SHEN_PHASE_IMPLEMENTATION_20261021.md](SHEN_PHASE_IMPLEMENTATION_20261021.md) | Shen 相位更新的 AFDM 候选实现与验证协议 |
| [STMP_COVARIANCE_GROUPING_20261024.md](STMP_COVARIANCE_GROUPING_20261024.md) | 更粗的 GEC 分组：首轮误差、模式响应与天线相关 |
| [STMP_COVARIANCE_REPRESENTATION_20261024.md](STMP_COVARIANCE_REPRESENTATION_20261024.md) | D-GEC 候选中的 C：维度、公开坐标基与精度递推 |
| [STMP_COVARIANCE_VALIDATION_20261024.md](STMP_COVARIANCE_VALIDATION_20261024.md) | C 候选验证：输入列基的解释能力与逐模式外信息代价 |
| [STMP_LINEAR_COVARIANCE_INTERFACE_20261024.md](STMP_LINEAR_COVARIANCE_INTERFACE_20261024.md) | 当前线性观测模块能否给出去噪协方差 |
| [STMP_MESSAGE_AWGN_REVIEW_20261024.md](STMP_MESSAGE_AWGN_REVIEW_20261024.md) | STMP 迭代消息失配的已有研究与改进方向 |
| [STMP_PAPER_READING_NOTES_20261024.md](STMP_PAPER_READING_NOTES_20261024.md) | STMP 论文下载后的阅读与可借鉴环节 |
| [STMP_PHASE.md](STMP_PHASE.md) | STMP 相位更新：实现、验证和边界 |
| [SYSTEM_MODEL.md](SYSTEM_MODEL.md) | 观测模型、空间结构与实验信息 |
| [TERMINOLOGY.md](TERMINOLOGY.md) | 当前术语与来源 |
| [THEORY.md](THEORY.md) | 完整信道 score 与消息传递 |
| [TRAINING.md](TRAINING.md) | 当前算法训练 |
| [WORKSPACE_INDEX.md](WORKSPACE_INDEX.md) | 工作区索引 |
