# 配置

当前模型绑定见 [final/models.json](final/models.json)，十层推断参数见 [final/receiver.json](final/receiver.json)。
正式计划见 [result/final2000](../../result/final2000/READINESS.json)，日常入口为根目录 `run_experiments.py`。

| 配置 | 用途 |
|---|---|
| algorithms.json | 算法名称、实现入口、构造参数、资源和计算后端 |
| experiments/*.json | 每项实验的 methods、场景数、扫描范围、重复计时次数及执行状态 |
| final/models.json | Proposed 权重与相位配置位置；通过 STMP_configuration 引用三网络配置 |
| final/receiver.json | 十层推断的数值设置 |
| final/STMP.json | 三网络 STMP 推断配置和权重位置的唯一来源 |
| final/phase.json | 共用相位估计设置 |
| final/baselines.json / final/offgrid_sbl.json | 四个基准的控制参数 |
| final/baseline_noise.json | 观测驱动的噪声估计设置 |
| final/readout_policy.json / final/offgrid_readout_policy.json | 活动判决规则 |
| final/baseline_sources.json | 当前基准源码的校验值 |
| training/STMP.json | STMP 训练配方；不会自动启动训练 |

这里仅保留当前配置。历史配置位于 `src/history/algorithm_20261021/configs/`，不参与当前推断。
配置接入没有改变各算法的参数、权重或活动门限。方法接入示例见 [实验说明](../evaluation/README.md)。
`algorithm.registry.load_models()` 解析 STMP 配置引用。实验计划内保存完整配置，供后续核验与复现。
