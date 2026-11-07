# 最终十层推断实现

`inference.py` 是公开推断入口，`receiver.py` 保留给定相位算子的十层迭代，`components.py` 实现每层计算。
`backbone.py` 使用 `networks` 中的网络结构；本算法独立加载十层权重。
固定选用深度10、epoch 1；推断阈值0.5，由训练验证集选模，本次代码整理不重新选择。
配置在 `src/configs/final/receiver.json`，资产位置和哈希在 `src/configs/final/models.json`。

`Receiver` 内部每层保留独立一阶网络、活动头及三个标量参数。`inputs.py` 处理公共观测与算子，
信道和活动标签只在外部评分使用。实验入口的 `--phase-mode` 与 `--noise-mode` 独立选择
`known` 或 `estimated`，默认均为 `estimated`。已知模式显式提供模拟相位或噪声方差真值，
未知噪声模式忽略输入中的噪声字段，从观测估计噪声。所有模式共用原有十层方程与权重。
`prepare_public(..., known)` 在适配器内接收已经选定的算子和噪声方差；它不决定实验的信息条件。

默认未知相位路径接收 `UnknownPhaseInput` 中的原始导频，直接执行用户接受的 `message_gem`：

- `phase_initialization.py`：用训练二阶矩构造协方差，通过方向导数初始化及连续边缘似然求解得到相位初值。
- `phase_layers.py`：十层各执行一次，仅第1至9层之后进行一次相位参数更新，将估计的标量旋转吸收入信道消息。
- `phase_update.py`：在当前各向同性高斯消息下计算完整投影条件矩，再做广义M步。
- `phase_math.py`：投影协方差、三角多项式及驻点计算。

这些文件直接位于当前 `src`，运行时不导入候选结果目录。固定数值预算记录在
`src/configs/final/proposed_phase.json`；训练二阶矩为 `result/models/proposed_10/phase_moments.npz`。
接受的是 `directional_coordinate` 初始化，未切换到后续 Bernoulli 初始化对照。
给定相位算子的 `ReceiverInput` 继续走条件十层路径；主实验的 known 相位模式使用此路径。
初始化和9次更新的时间均计入 proposed 的端到端时间，不再叠加公共相位估计耗时。

推导见 [PHASE_MESSAGE_GEM.md](../../../paper/DU/docs/PHASE_MESSAGE_GEM.md)。固定高斯消息下的目标下降，
不等于整套神经网络的全局收敛保证。原5个物理场景×两种导频数的回放仅验证接入一致性。

推断需要原D盘选中权重，但无需导入训练目录的Python模块。
训练调度、优化器和CUDA图捕获仍保留在原冻结训练副本，最终推断包不提供自动续训功能。
来源记录在 `result/final_version_20261021/`，此次结构核验在 `result/algorithm_layout_20261021/`。
