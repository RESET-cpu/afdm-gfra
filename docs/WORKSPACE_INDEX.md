# 工作区索引

当前主线和七项实验不依赖 `archive/`。算法版本以 [MAINLINE.json](../MAINLINE.json) 为准。

| 内容 | 位置 |
|---|---|
| 七项正式实验 | [experiment](../experiment/README.md) |
| 系统与算法实现 | [代码导读](CODE_GUIDE.md) · `src/` |
| 配置、模型、训练数据 | `configs/`、`models/`、`data/` |
| 训练工具 | [scripts](../scripts/README.md) |
| 必要的批次和训练辅助代码 | [experiments](../experiments/README.md) |
| 500 场景结果及校准记录 | [results](../results/README.md) |
| 7 个正确性检查文件 | [tests](../tests/README.md) |
| 论文与参考文献 | `paper/`、`references/` |
| 主要历史报告与引用依据 | [history](history/README.md) |
| 独立运行与清理记录 | [REPORT](../results/cleanup_20261018/REPORT.md) |

阅读顺序：[系统模型](SYSTEM_MODEL.md)、[理论](THEORY.md)、[术语依据](TERMINOLOGY.md)、[主线说明](PROPOSED_MAINLINE.md)、[500 场景结果](../results/baseline_comparison_500_20261018/REPORT.md)。

旧实验的大数组、重复快照和中间检查点已清理。保留的历史记录不足以直接恢复每个旧实验的完整运行；当前 500 场景数据和按约定冻结的 Proposed 副本完整保留。
