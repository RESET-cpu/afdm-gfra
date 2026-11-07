# 实验

`experiments/` 只定义八类实验的条件和入口；`suite.py` 负责创建计划、验证资产、逐项调用与汇总调度。

- `observations.py`：观测缓存与相位前端结果的保存。
- `runtime.py`：设备准备、同步、模型切换与参数统计；从原 `evaluation/receivers.py` 归入执行模块。
- `storage.py`：数组保存和读取。
- `metrics.py`：预测与真值的评分。
- `reporting.py`：结果聚合、区间与报告；图形生成已拆到 `plotting/summary.py`。

新通用计划默认使用 `result/organized_default_20261107/`，使用 `src/configs/organized/algorithms.json`。`plan`、`inspect`、`run` 各司其职，`run` 才执行推断。不要让新代码直接续跑冻结批次；现有白噪声后续队列由总入口 `white_followup` 转交原执行模块。

```text
python run_experiments.py list
python run_experiments.py pilot_frames --help
python run_experiments.py white_followup inspect
```

本次整理未修复或重启导频数阶段的任务文件读取失败。续跑时仍需检查原失败记录、进程和部分结果。
