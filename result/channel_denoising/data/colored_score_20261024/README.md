# 有色噪声一阶 score 候选

此目录保留已撤回的四类等比例采样版本，不是当前训练方案。其源码和说明见 [four_class_snapshot](four_class_snapshot/MANIFEST.json)；当前统一噪声族版本见[新目录](../colored_score_single_family_20261024/README.md)。下列 PLAN/CHECKS/SMOKE 均保留原始内容。

2026-10-24：实现及检查完成，正式训练和性能比较尚未启动；没有候选训练权重。

- [当时的方案、公式和命令](four_class_snapshot/paper/docs/COLORED_SCORE_TRAINING_20261024.md)
- [PLAN.json](PLAN.json)：现有50000训练信道、1000独立开发验证场景及配对配置。
- [CHECKS.json](CHECKS.json)：7项定向测试通过及源码哈希。
- [SMOKE.json](SMOKE.json)：真实冻结权重的AWGN一致性及一次CPU优化检查，无权重保存。

本目录中的噪声模型是可分的proper复Gaussian训练候选。检查通过只支持公式与实现一致、流程可运行，不支持去噪或低SNR活动检测已改善的结论。冻结主线不变。
