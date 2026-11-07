# 单一有色 Gaussian 噪声的一阶 score 候选

2026-10-24修订：移除四类等比例训练采样，两个方向的协方差因子都独立连续抽样。当前实现和CPU检查完成，正式训练及性能比较尚未启动。

已有查询的[相对近似检查](../../../../paper/docs/COLORED_COVARIANCE_RELATIVE_CHECK_20261024.md)支持保留当前受限C族作初步去噪候选。它优于同样拟合功率的白噪声描述，但不是训练后性能验证；本轮没有继续调rank或强度范围。

- [方案与命令](../../../../paper/docs/COLORED_SCORE_TRAINING_20261024.md)
- [PLAN.json](PLAN.json)：单一噪声族及1000个开发验证场景的配对对照。
- [CHECKS.json](CHECKS.json)：7项定向检查及当前源码哈希。
- [SMOKE.json](SMOKE.json)：真实冻结权重的AWGN一致性及一次CPU优化检查，无权重保存。

AWGN只用于独立的退化检查和控制模型，没有固定占比加入有色候选的训练样本。采样强度上限0.5与rank=4仍是未选优的设计参数。检查通过不代表低SNR检测性能已有改善。

前版原始记录与源码快照保留于[旧目录](../colored_score_20261024/README.md)。
