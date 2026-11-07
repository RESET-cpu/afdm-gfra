> 2026-10-21 最终代码整理已完成。当前维护入口见[最终版本](test_final_evaluation.py)；下文保留整理前的说明及历史路径。

# 检查分组

这里同时保留公共物理/评价检查、旧三网络检查、十层训练实现检查和历史候选检查；不再只有 7 个测试文件。当前七项实验的实际接入检查记录在 [experiment_integration_20261021](../results/experiment_integration_20261021/REPORT.md)。

| 范围 | 文件举例 | 用途 |
|---|---|---|
| 公共数组、评分与信息边界 | `test_array_transforms.py`、`test_evaluation_metrics.py`、`test_baseline_noise.py`、`test_phase_estimation_candidate.py` | 物理和指标计算、相位/噪声估计 |
| 原三网络及实验辅助流程 | `test_activity_classifier.py`、`test_proposed_noise_candidate.py`、`test_experiment.py`、`test_density_ratio_ablation.py` | 保留原接口、统计和旧消融检查 |
| 十层的基础/训练实现 | `test_lstmp_candidate_interfaces.py`、`test_lstmp_message_damping.py`、`test_lstmp_training_v2.py`、`test_lstmp_training_v3.py`、`test_lstmp_execution.py` | 分层实现、目标、训练和执行依赖 |
| 训练设备与执行 | `test_training_device.py`、`test_cuda_execution.py`、`test_cuda_auxiliary.py` | 设备和训练执行机制 |
| 历史候选与旧面板 | 其余带 `lstmp`、`stability`、`calibration` 等名称的文件 | 对应各自协议和数据，部分旧权重现已删除 |

修改相关公式时选择对应检查。下面只运行公共数组和指标检查，不启动接收机性能实验：

```powershell
& .\.venv\Scripts\python.exe -B -m pytest -q tests/test_array_transforms.py tests/test_evaluation_metrics.py
```

直接运行 `pytest tests` 或 `run.py test` 会发现整个目录中的测试，包括历史候选；不能把它解释成仅执行当前七项实验的检查。依赖已删除旧权重的历史测试需要其原资产，不能静默替换为新十层权重。

最近的当前入口检查为七项、184 条入口结果记录，并核对了清理后十层输出与已保存预测一致；这是独立诊断场景的流程检查，不是正式 2000 场景性能结论。此次目录说明整理只做文件身份、链接和入口帮助检查，没有再次运行训练或接收机推断。
