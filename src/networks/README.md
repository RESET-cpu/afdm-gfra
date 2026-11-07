# 共用网络

`score.py` 定义和加载得分网络，`cai_models/` 保存网络组件；`channel_score.py` 和 `array_transforms.py` 提供信道网络与阵列变换。

GP-MP、STMP 与训练模块共用结构定义，各自使用登记的权重。推断在 `receiver/`，训练在 `training/`。第三方来源和许可见 [RIGHTS.md](../../RIGHTS.md)。
