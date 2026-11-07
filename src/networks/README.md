# 共用网络结构

`score.py` 定义并加载一阶、二阶 score 网络，`cai_models/` 保存其网络组件，
`channel_score.py` 和 `array_transforms.py` 提供已有信道网络与阵列变换。
Proposed、STMP 和预训练代码共用结构定义，各自使用明确指定的权重。
这里只包含结构和加载代码，不执行任何接收算法或训练任务。
