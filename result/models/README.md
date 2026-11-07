# 模型资产

当前推断权重、训练初始化和教师记录均为主线内的实际文件。

| 用途 | 位置 |
|---|---|
| Proposed 一阶、二阶、活动分类器 | [proposed/](proposed/)：`first.pt`、`second.pt`、`activity.pt` |
| GNN-ASPL（原图主线） | [gnn/checkpoint.pt](gnn/checkpoint.pt) |
| 三阶段训练初始化 | [initialization/](initialization/)：`first.pt`、`second.pt`、`activity.pt` |
| 当前三网络的原始训练记录 | [proposed/training_records/](proposed/training_records/)：各阶段的完成记录、配方、历史与初始验证 |

推断权重的 SHA 和教师身份由 [proposed.json](../configs/proposed.json) 与 [baselines.json](../configs/baselines.json) 绑定。
初始化权重和可搬动的数据路径由 [训练配置](../configs/training/proposed.json) 绑定；训练状态见 [TRAINING.md](../docs/TRAINING.md)。

```sh
.venv/bin/python -B run.py verify
.venv/bin/python -B scripts/train_proposed.py --inspect --check-assets
```

当前模型与训练初始化均为本目录中的实际文件。旧模型链接与重复检查点已清理；主要来源记录见 [docs/history](../docs/history/README.md)。
