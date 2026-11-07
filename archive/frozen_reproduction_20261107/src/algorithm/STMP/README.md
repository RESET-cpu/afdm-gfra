# STMP 三网络

`receiver.py` 执行三网络接收流程，`noise.py` 提供观测噪声估计的输入入口。
`iterations.py` 是迭代主体，`linear.py` 处理线性模块，`moments.py` 与 `posterior.py` 处理后验矩，
`activity.py` 是活动证据网络。共用的一阶、二阶网络结构在 `networks`。

默认配置为 `src/configs/final/STMP.json`；实验模型清单为 `src/configs/final/models.json`。
此算法与 `proposed` 的十层深度展开分开，当前按用户要求保留但暂不执行实验。
