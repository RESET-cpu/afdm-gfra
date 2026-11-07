# 训练与训练来源

整理后的共用训练代码位于 `scores/`，STMP 训练位于 `stmp/`，GNN-ASPL 训练位于 `gnn/`。数据、损失、优化、续训与检查点保存保留各自模块。

当前 GP-MP 白噪声权重已经训练完成。本次没有重训，也没有更换用于产生它们的冻结入口：

| 已冻结训练 | 原始入口 | 配置 |
|---|---|---|
| 白噪声条件均值网络 | `training.colored_preconditioned_20261024.formal` | `src/configs/training/white_preconditioned_matched_20261104.json` |
| 匹配的活动分类器 | `training.colored_activity_20261025.run` | `src/configs/training/white_activity_matched_20261104.json` |

入口名是历史实现名称，实际白噪声训练设置以配置与训练记录为准。它们的原源码及训练时保存的副本均保留。当前权重身份以 `FINAL.json` 为准。

新的训练工作应使用独立配置和输出目录，另做科学验证，不能把目录整理当作已重现全部训练。这里只验证了新包的网络加载及一次已训练去噪器的对照输出。
