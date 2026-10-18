# 核心正确性检查

性能实验从 [experiment/](../experiment/README.md) 运行。本目录仅保留直接影响结果可信度的 7 个检查文件：

| 文件 | 检查内容 |
|---|---|
| `test_array_transforms.py` | 数组变换与直接矩阵计算一致 |
| `test_activity_classifier.py` | 当前分类器输入、概率与导数 |
| `test_baseline_noise.py` | 估噪公式、噪声接入及真值隔离 |
| `test_evaluation_metrics.py` | 完整信道误差包含非活跃用户 |
| `test_phase_estimation_candidate.py` | 当前优化相位实现的物理原子、导数与搜索 |
| `test_proposed_noise_candidate.py` | Proposed 估噪不使用供给的真实方差 |
| `test_experiment.py` | 观测配对、下界计算、120 轮配置与校准绑定、历史结果/相位复用、失败保留及固定场景汇总 |

```sh
.venv/bin/python -B -m pytest -q tests
```

改到对应公式或实验流程时运行相关检查。这 7 个文件已在不含归档的独立工作区中全部通过；它们覆盖当前关键性质，不代表所有历史候选算法的完整测试覆盖。
