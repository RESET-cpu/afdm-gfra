# 必要的复现与训练辅助文件

日常八项实验从 [experiment/](../experiment/README.md) 运行。本目录仅保留当前代码仍需读取的实际文件：

- `baseline_comparison_600_20261017/`：500 场景结果绑定的原批次代码及协议。
- `proposed_original_snr8_10_20261016/analyze.py`：原批次使用的独立评分函数。
- `comparison_log_aer_20261018/`、`comparison_stop500_20261018/`：最终图和 500 场景范围记录的辅助代码。
- `ldamp_repair_20261014/`：保留的 L-DAMP 训练入口所需五个辅助文件。
- `ldamp_complete_20261015/`、`joint_amp_20261015/training/`：配置或保留实现引用的推导和辅助文件。

这些文件不通过归档链接读取。其他旧实验目录已清理；被引用的推导、主要报告和日志集中到 [docs/history](../docs/history/README.md)。
