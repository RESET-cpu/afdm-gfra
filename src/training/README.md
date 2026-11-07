# 训练

训练目标、批次采样和优化只放在本目录。接收机推断不导入训练代码。

- `gp_mp/`：白高斯噪声条件均值与活动分类器训练；不含有色噪声生成分支。
- `stmp/`：STMP 三网络训练与信道库构建。
- `scores/`：共用得分网络训练操作。
- `gnn/`：GNN-ASPL 训练。
- `cli.py`：根入口的显式分发。

直接在仓库根目录运行，无需安装本项目为软件包：

```text
python run_experiments.py train gp-mp-first --help
python run_experiments.py train gp-mp-activity --help
python run_experiments.py train stmp --help
python run_experiments.py train gnn --help
```

当前白噪声训练配方为 `src/configs/training/gp_mp_first.json` 与 `gp_mp_activity.json`。
默认输出使用独立的 `_reproduction` 路径，不覆盖采用的模型。训练需要原始信道库、初始化和溯源记录；这些并未随推断权重全部发布。
`training.stmp.data.build_bank` 可生成新库，但新生成器身份必须独立记录并验证，不能冒充原冻结库。

原训练入口及原配方保存在 `archive/frozen_reproduction_20261107`。白噪声提取已验证相同随机数抽样、张量、网络输出、损失及梯度，见 `archive/retired_code_20261107/NUMERICAL_PARITY.json`；本次未重新训练模型。
