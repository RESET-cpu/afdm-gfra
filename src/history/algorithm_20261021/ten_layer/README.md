# 最终十层推断实现

从已完成训练的实际冻结源码提取，保持选中权重和数值运算。外部实验通过 `evaluation/receivers.py` 加载。
固定选用深度10、epoch 1；推断阈值0.5，由训练验证集选模，本次代码整理不重新选择。
配置在 `src/configs/final/receiver.json`，资产位置和哈希在 `src/configs/final/models.json`。

`Receiver` 内部每层保留独立一阶网络、活动头及三个标量参数。`inputs.py` 处理公共观测与算子，
标签只在外部评分使用。当前正式实验在外部先估计相位，适配器再从观测估计噪声。
原源码中 `prepare_public(..., known)` 在该适配器内接收的是这两个估计值，不是模拟真值。

推断需要原D盘选中权重，但无需导入训练目录的Python模块。
训练调度、优化器和CUDA图捕获仍保留在原冻结训练副本，最终推断包不提供自动续训功能。
来源及逐工况等价记录见仓库 `result/final_version_20261021/`。
