# 有色噪声条件三模块路线归档

2026-10-12，按用户决定归档。项目研究主线恢复为原有一阶 score、二阶标量读出与活动分类器，下一步研究已检出用户的均值估计及其反馈对弱用户查询的影响。

当前状态以本文件和 [CURRENT_STATUS.json](CURRENT_STATUS.json) 为准。资产中的 README、REPAIR_PLAN、训练状态和日志是保留原字节的历史记录，其中“正在运行”“后续继续”等文字不代表当前安排。

## 保存范围与结果边界

- [源代码、配置、推导和检查](assets/experiments/covariance_training_20261012/)：70 个文件。
- [权重、优化器断点、训练历史、预测、诊断和图表](assets/results/covariance_training_20261012/)：1,045 个文件。
- 一阶选定第22轮 EMA，原训练暂停于第23轮，未完成完整训练；二阶与活动模块各完成20轮，均选第20轮，绑定同一一阶快照。
- 原闭环评价停止状态记录为102/189条、3次数值失败；完整面板未完成。−4 dB的20场景子面板已完成，其余子集按原覆盖率读取。
- 阻尼比较完成2/6条，已完成的两条均数值失败；后续一条中断，其余未执行。
- 二阶替代损失训练与完整矩阵/aC/标量反馈对照仅完成准备，未执行正式比较。
- [一阶实际查询对照](assets/results/covariance_training_20261012/real_first_queries_002/REPORT.md)、[三网络loss曲线](assets/results/covariance_training_20261012/loss_curves_001/loss_curves.png)、[二阶方向诊断](assets/results/covariance_training_20261012/diagnostics/pilot_second_selected_epoch020.json)均保留。

上述结果属于开发验证，不能把未完成面板称为完整性能比较，也不能把归档决定解释为已经证明有色建模无效。

## 原有主线

当前配置仍为 [configs/proposed.json](../../configs/proposed.json)，权重仍为 `models/proposed/{first,second,activity}.pt`，分别对应第81、39、82轮。归档没有更改主算法代码、配置或权重。

主线身份见 [MAINLINE_BASELINE.json](MAINLINE_BASELINE.json)，后续研究见 [均值与反馈研究计划](../../experiments/proposed_mean_feedback_20261012/PLAN.md)。本次只归档、核验资产与整理方案，训练和接收机性能实验保持停止。

## 保存与恢复

两棵目录整体移入本归档，原来的 `experiments/covariance_training_20261012` 和 `results/covariance_training_20261012` 保留相对符号链接，用于读取既有记录中的路径。没有删除权重或预测数据。

[PRESERVATION.json](PRESERVATION.json)保存迁移前逐文件长度和SHA-256；[MIGRATION.json](MIGRATION.json)记录迁移后全部1,115个文件的逐字节身份核验及目录inode保持结果。项目入口文档修改前的副本保存在 `before/`。

主线算法身份、原训练资产和文档链接的检查见 [VERIFICATION.json](VERIFICATION.json)；检查没有执行网络推断或优化器更新。

旧路径链接仅用于历史读取。部分实验脚本通过解析自身路径定位项目根目录；将来如明确恢复执行，应先把两棵实体目录恢复到原位置，再使用对应冻结源码、配置、数据和教师身份检查恢复条件，不能直接把归档路径当作续训入口。本次没有改写任何历史源码哈希或实验完成状态。
