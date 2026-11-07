# 配置

日常入口使用 [organized/algorithms.json](organized/algorithms.json)，工厂和直接源码路径指向 `src` 下对应功能目录。原登记与下列配置保留为冻结记录，数值参数和模型绑定未因代码整理改变。[代码导读](../README.md)。

当前 GP-MP 绑定见根目录 [FINAL.json](../../FINAL.json)，STMP 配置引用见
[organized/models.json](organized/models.json)。日常入口为根目录 `run_experiments.py`。

| 配置 | 用途 |
|---|---|
| algorithms.json | 算法名称、实现入口、构造参数、资源和计算后端 |
| experiments/*.json | 每项实验的 methods、场景数、扫描范围、重复计时次数及执行状态 |
| organized/models.json | 当前 STMP 配置与共用相位配置的引用 |
| final/models.json | 冻结历史混合记录，含已退役 DU 的原始身份；不作为当前模型加载入口 |
| final/STMP.json | 三网络 STMP 推断配置和权重位置的唯一来源 |
| final/phase.json | 共用相位估计设置 |
| final/baselines.json / final/offgrid_sbl.json | 四个基准的控制参数 |
| final/baseline_noise.json | 观测驱动的噪声估计设置 |
| final/readout_policy.json / final/offgrid_readout_policy.json | 活动判决规则 |
| final/baseline_sources.json | 当前基准源码的校验值 |
| training/STMP.json | STMP 训练配方；不会自动启动训练 |

已退役 DU 的独立配置移入根目录 `delete/`。历史配置及混合绑定保留原文，不参与当前方法选择。
配置接入没有改变各算法的参数、权重或活动门限。方法接入示例见 [实验说明](../evaluation/README.md)。
`receiver.registry.load_models()` 解析当前 STMP 配置引用。实验计划内保存完整配置，供后续核验与复现。
