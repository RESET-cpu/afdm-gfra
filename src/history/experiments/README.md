> 2026-10-21 最终代码整理已完成。当前维护入口见[最终版本](../src/afdm_jadcedd/evaluation/README.md)；下文保留整理前的说明及历史路径。

# 评价、训练实现与历史来源

面向使用者的命令在 [experiment/](../experiment/README.md)（单数）。本目录 `experiments/`（复数）存放评价实现、训练版本和按日期保存的研究来源。

## 当前评价

| 目录 | 状态与职责 |
|---|---|
| [lstmp_evaluation_2000_20261021](lstmp_evaluation_2000_20261021/README.md) | 当前执行包：共享 2000 场景、十层/基线接入、计时、评分、报告；旧三网络暂缓 |

当前只有最终十层与旧三网络作为新旧学习接收机保留在模型绑定中；五层、七层和 v2 不在当前实验的方法列表里。四个既有基线继续保留。

## 最终十层的训练及基础模块来源

| 工作区目录 | 用途 |
|---|---|
| `lstmp_execution_v3_20261020/` | 第三版训练的执行加速、接收机与数据实现 |
| [lstmp_training_v3_20261020](lstmp_training_v3_20261020/README.md) | 19 个条件、十层训练的协议、计划、数据生成和原训练循环 |
| [lstmp_training_v2_20261020](lstmp_training_v2_20261020/README.md) | 后续版本复用的接收机结构、目标、优化和验证代码；名称不代表加载 v2 权重 |
| [lstmp_candidate_20261019](lstmp_candidate_20261019/README.md) | 基础网络、线性查询、校准参数、公共配置和数据等来源 |
| [lstmp_message_damping_candidate_20261019](lstmp_message_damping_candidate_20261019/README.md) | 消息阻尼实现来源；实际运行冻结副本把相关模块合入基础包 |

实际推断由 `lstmp_evaluation_2000_20261021/receivers.py` 从 `models.json` 指定的 D 盘最终训练目录加载冻结源码和权重。以上工作区文件用于开发与审阅，不自动替换训练时保存的实现。完整路径与依赖链见 [代码导读](../docs/CODE_GUIDE.md)。

## 历史候选与专项诊断

| 目录 | 范围 |
|---|---|
| `lstmp_cai_activity_candidate_20261019/` | 早期活动处理候选 |
| `lstmp_stability_candidate_20261019/` | 早期稳定性研究候选 |
| `lstmp_depth_extension_20261020/` | 历史层数扩展方案 |

这些目录不作为当前正式评价入口。对应历史权重的保留/删除状态应查看运行目录与清理清单；不能仅凭源码仍在就假定可重跑。

## 既有基线及结果来源

| 目录 | 保留原因 |
|---|---|
| `baseline_comparison_600_20261017/` | 历史 500 场景结果绑定的批次代码与协议；目录名沿用最初计划 |
| `comparison_log_aer_20261018/`、`comparison_stop500_20261018/` | 原比较绘图和最终范围记录 |
| `proposed_original_snr8_10_20261016/` | 原批次使用的评分来源 |
| `ldamp_repair_20261014/`、`ldamp_complete_20261015/` | 保留的 L-DAMP 训练辅助文件和推导 |
| `joint_amp_20261015/training/` | 保留实现引用的训练和方法来源 |

日常实验不需要遍历这些历史目录。此次整理保持源码路径不变，避免破坏冻结计划、训练来源和历史引用。
