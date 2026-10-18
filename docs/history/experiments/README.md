# 历史实验实现与复现依赖

日常实验入口现统一在 [experiment/](../experiment/README.md)，每个核心实验一个文件。本目录保留已经完成实验的原实现和冻结清单引用的辅助代码；现有 500 场景结果仍可追溯到原脚本。根目录 [run.py](../run.py) 继续用于单次生成、推断和评分。

## 当前实验

| 入口 | 用途 |
|---|---|
| [500 场景汇总与核验](../results/baseline_comparison_500_20261018/) | 当前最终报告、统计与独立核验入口 |
| [baseline_comparison_600_20261017](baseline_comparison_600_20261017/) | 正式批次原冻结代码；最终按 500 场景结束 |
| [baseline_comparison_200_20261017](baseline_comparison_200_20261017/) | 前 200 场景来源与原协议 |
| [phase_optimization_20261017](phase_optimization_20261017/) | 已采用相位实现与噪声估计验收 |
| [comparison_log_aer_20261018](comparison_log_aer_20261018/) | 当前 AER 对数轴绘图 |

## 历史比较与复现

| 目录 | 用途 |
|---|---|
| [proposed_original_snr8_10_20261016](proposed_original_snr8_10_20261016/) | 当前原导频八档五方法实验；运行、汇总与绘图 |
| [historical_figure_verification_20261016](historical_figure_verification_20261016/) | 历史已知相位图及冻结接收机复核 |
| [proposed_unknown_phase_20261015](proposed_unknown_phase_20261015/) | 已冻结的估计相位 Proposed 面板 |
| [unknown_phase_20261015](unknown_phase_20261015/) | 估计相位场景与回归对照 |

## 保留的依赖

以下目录保留是为了现有测试、训练和复现路径完整，不表示重新启动这些研究路线。

| 目录 | 依赖范围 |
|---|---|
| [full_power_channels_20261013](full_power_channels_20261013/) | 现有回归测试引用 |
| [joint_amp_20261015](joint_amp_20261015/) | 已保留的实现或训练入口引用 |
| [ldamp_20261014](ldamp_20261014/) | 上述保留目录的辅助依赖 |
| [ldamp_complete_20261015](ldamp_complete_20261015/) | 现有回归测试引用 |
| [ldamp_repair_20261014](ldamp_repair_20261014/) | 已保留的实现或训练入口引用 |
| [ldamp_structure_20261015](ldamp_structure_20261015/) | 已保留的实现或训练入口引用 |
| [proposed_ablation_20261012](proposed_ablation_20261012/) | 上述保留目录的辅助依赖 |
| [proposed_activity_diagnosis_20261009](proposed_activity_diagnosis_20261009/) | 上述保留目录的辅助依赖 |
| [proposed_low_snr_20261015](proposed_low_snr_20261015/) | 现有回归测试引用 |
| [proposed_mean_feedback_20261012](proposed_mean_feedback_20261012/) | 上述保留目录的辅助依赖 |
| [proposed_phase_training_20261012](proposed_phase_training_20261012/) | 现有回归测试引用 |
| [proposed_pilot_polar_20261016](proposed_pilot_polar_20261016/) | 八档实验冻结源码与复现依赖 |
| [proposed_polar_baselines_20261016](proposed_polar_baselines_20261016/) | 八档实验冻结源码与复现依赖 |
| [proposed_polar_baselines_30_20261016](proposed_polar_baselines_30_20261016/) | 八档实验冻结源码与复现依赖 |
| [proposed_polar_snr6_10_20261016](proposed_polar_snr6_10_20261016/) | 八档实验冻结源码与复现依赖 |
| [proposed_rank_one_20261012](proposed_rank_one_20261012/) | 现有回归测试引用 |

依赖逐项记录见 [迁移清单](../results/workspace_cleanup_20261016/MIGRATION.json)。`covariance_training_20261012` 是此前已有的归档链接；另有 32 个旧路径链接用于保持冻结术语文档的出处可访问。这些链接指向归档源码，不计入 20 个实体目录。

## 历史实验

77 个历史实验目录已移至 [归档](../archive/workspace_cleanup_20261016/README.md)。结果、失败样本和冻结资产继续保留在原结果目录；历史脚本依赖原项目相对路径，恢复后再执行。

2026-10-18：`proposed_joint_phase_20261017`、`proposed_phase_iteration_20261017` 两个独立候选目录已加入[本次归档](../archive/workspace_cleanup_20261018/README.md)，原路径通过链接保留。当前实验和既有测试所需依赖继续可访问；上述历史表格不表示实验仍在运行。
