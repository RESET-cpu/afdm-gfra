# 实验

`experiments/` 定义八类通用实验，`suite.py` 负责计划、校验、调用与汇总。`metrics.py` 独立评分，`observations.py` 管理观测，`storage.py` 保存数组，`runtime.py` 管理设备与计时，`reporting.py` 生成报告。

## 创建新实验

```text
python run_experiments.py list
python run_experiments.py pilot_frames --help
python run_experiments.py pilot_frames plan --config src/configs/experiments/pilot_frames.json --device cuda --output result/my_pilot_frames
python run_experiments.py pilot_frames inspect --output result/my_pilot_frames
python run_experiments.py pilot_frames run --output result/my_pilot_frames
```

先核对配置中的方法、场景数和扫描范围，再执行 `run`。`plan` 保存配置及源码/资产校验值，`inspect` 检查计划，`run` 执行并生成评分、汇总和诊断图。需要重新汇总时使用 `summarize --output ...`。

配置修改只在创建计划时生效；改变参数应使用新的输出目录。`--smoke` 使用独立诊断种子。首次运行建议先完成[单场景 GP-MP 示例](../../REPRODUCING.md)，再增加预算。

## 已保存的研究批次

`studies/white_followup` 和 `studies/convergence` 对应既定研究协议。它们与通用新实验的默认配置分开管理；历史图的采用状态见[实验索引](../../result/README.md)。

```text
python run_experiments.py white_followup inspect
```

导频数批次已完成任务读取修复并从原断点恢复，见[恢复记录](../../archive/pilot_resume_20261107/README.md)。它需要完整本地输入和原计划，不能仅凭 GitHub 中的汇总文件续跑。运行进度以本地批次状态为准。
