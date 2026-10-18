# 2026-10-16 工作区归档

本次归档包含 77 个历史实验目录、旧 `outputs 2` 记录，以及原临时材料链接。当前主线源码、配置、权重、结果和训练数据保持原位。

迁移记录：[MIGRATION.json](MIGRATION.json)；核验和说明：[整理报告](../../results/workspace_cleanup_20261016/REPORT.md)。每个常规文件在移动前后的设备、inode、大小和修改时间一致；符号链接的目标单独记录。

另保留 32 个原位置的兼容链接，供冻结术语文档访问推导和协议，清单见 [COMPATIBILITY_LINKS.json](COMPATIBILITY_LINKS.json)。链接不代表实验仍在运行；执行旧脚本仍需先恢复。

## 查询与恢复

原路径 `experiments/<名称>` 对应本目录下的 `workspace/experiments/<名称>`。历史脚本通常按原项目深度定位根目录，需要恢复原路径后运行，不能直接把归档路径当作新的运行入口。

从项目根目录查看恢复范围：

```sh
.venv/bin/python -B archive/workspace_cleanup_20261016/restore.py --list
```

恢复本批全部原路径：

```sh
.venv/bin/python -B archive/workspace_cleanup_20261016/restore.py --all
```

恢复时如有同名文件或目录会停止，不覆盖新工作。当前导航文档不回滚，归档位置会保留指向恢复路径的链接。整理前导航另存于 [before](../../results/workspace_cleanup_20261016/before/)。

## 实验目录

| 原目录 | 归档位置 | 现有结果 |
|---|---|---|
| activity_posterior_20261015 | [源码](workspace/experiments/activity_posterior_20261015/) | [结果](../../results/activity_posterior_20261015/) |
| activity_posterior_refinement_20261015 | [源码](workspace/experiments/activity_posterior_refinement_20261015/) | [结果](../../results/activity_posterior_refinement_20261015/) |
| amp_foundation_20261015 | [源码](workspace/experiments/amp_foundation_20261015/) | [结果](../../results/amp_foundation_20261015/) |
| awgn_reference_ladder_20261015 | [源码](workspace/experiments/awgn_reference_ladder_20261015/) | [结果](../../results/awgn_reference_ladder_20261015/) |
| baseline_optimization_20261012 | [源码](workspace/experiments/baseline_optimization_20261012/) | [结果](../../results/baseline_optimization_20261012/) |
| baseline_phase_learning_20261015 | [源码](workspace/experiments/baseline_phase_learning_20261015/) | [结果](../../results/baseline_phase_learning_20261015/) |
| baseline_resolution_20261009 | [源码](workspace/experiments/baseline_resolution_20261009/) | [结果](../../results/baseline_resolution_20261009/) |
| channel512_continuation_20261014 | [源码](workspace/experiments/channel512_continuation_20261014/) | [结果](../../results/channel512_continuation_20261014/) |
| channel_capacity_20261013 | [源码](workspace/experiments/channel_capacity_20261013/) | [结果](../../results/channel_capacity_20261013/) |
| diffusion_amp_20261015 | [源码](workspace/experiments/diffusion_amp_20261015/) | [结果](../../results/diffusion_amp_20261015/) |
| full_power_channels_w128_20261013 | [源码](workspace/experiments/full_power_channels_w128_20261013/) | [结果](../../results/full_power_channels_w128_20261013/) |
| historical_snr8_extension_20261016 | [源码](workspace/experiments/historical_snr8_extension_20261016/) | 见该目录内的来源记录 |
| implementation_audit_20261014 | [源码](workspace/experiments/implementation_audit_20261014/) | [结果](../../results/implementation_audit_20261014/) |
| joint_amp_checkpoint_20261015 | [源码](workspace/experiments/joint_amp_checkpoint_20261015/) | [结果](../../results/joint_amp_checkpoint_20261015/) |
| ldamp_score_swap_20261015 | [源码](workspace/experiments/ldamp_score_swap_20261015/) | [结果](../../results/ldamp_score_swap_20261015/) |
| low_snr_parameterization_20261014 | [源码](workspace/experiments/low_snr_parameterization_20261014/) | [结果](../../results/low_snr_parameterization_20261014/) |
| offgrid_baselines_20261012 | [源码](workspace/experiments/offgrid_baselines_20261012/) | [结果](../../results/offgrid_baselines_20261012/) |
| offgrid_sbl_audit_20261012 | [源码](workspace/experiments/offgrid_sbl_audit_20261012/) | [结果](../../results/offgrid_sbl_audit_20261012/) |
| offgrid_sbl_reference_20261013 | [源码](workspace/experiments/offgrid_sbl_reference_20261013/) | [结果](../../results/offgrid_sbl_reference_20261013/) |
| oracle_direction_small_20261013 | [源码](workspace/experiments/oracle_direction_small_20261013/) | [结果](../../results/oracle_direction_small_20261013/) |
| phase_feasibility_20261015 | [源码](workspace/experiments/phase_feasibility_20261015/) | [结果](../../results/phase_feasibility_20261015/) |
| physical_message_20261015 | [源码](workspace/experiments/physical_message_20261015/) | [结果](../../results/physical_message_20261015/) |
| proposed_activity_repair_20261016 | [源码](workspace/experiments/proposed_activity_repair_20261016/) | [结果](../../results/proposed_activity_repair_20261016/) |
| proposed_adaptive_geometry_20261016 | [源码](workspace/experiments/proposed_adaptive_geometry_20261016/) | [结果](../../results/proposed_adaptive_geometry_20261016/) |
| proposed_amp_20261015 | [源码](workspace/experiments/proposed_amp_20261015/) | [结果](../../results/proposed_amp_20261015/) |
| proposed_amp_damping_20261015 | [源码](workspace/experiments/proposed_amp_damping_20261015/) | [结果](../../results/proposed_amp_damping_20261015/) |
| proposed_amp_revision_20261015 | [源码](workspace/experiments/proposed_amp_revision_20261015/) | [结果](../../results/proposed_amp_revision_20261015/) |
| proposed_awgn_20261014 | [源码](workspace/experiments/proposed_awgn_20261014/) | [结果](../../results/proposed_awgn_20261014/) |
| proposed_awgn_mean_scale_20261016 | [源码](workspace/experiments/proposed_awgn_mean_scale_20261016/) | [结果](../../results/proposed_awgn_mean_scale_20261016/) |
| proposed_awgn_weighting_20261016 | [源码](workspace/experiments/proposed_awgn_weighting_20261016/) | [结果](../../results/proposed_awgn_weighting_20261016/) |
| proposed_axis_control_20261015 | [源码](workspace/experiments/proposed_axis_control_20261015/) | [结果](../../results/proposed_axis_control_20261015/) |
| proposed_cai_relaxation_20261015 | [源码](workspace/experiments/proposed_cai_relaxation_20261015/) | [结果](../../results/proposed_cai_relaxation_20261015/) |
| proposed_colored_20261015 | [源码](workspace/experiments/proposed_colored_20261015/) | [结果](../../results/proposed_colored_20261015/) |
| proposed_covariance_constraints_20261015 | [源码](workspace/experiments/proposed_covariance_constraints_20261015/) | [结果](../../results/proposed_covariance_constraints_20261015/) |
| proposed_ddrm_20261015 | [源码](workspace/experiments/proposed_ddrm_20261015/) | [结果](../../results/proposed_ddrm_20261015/) |
| proposed_delay_coordinates_20261016 | [源码](workspace/experiments/proposed_delay_coordinates_20261016/) | [结果](../../results/proposed_delay_coordinates_20261016/) |
| proposed_feedback_uncertainty_20261016 | [源码](workspace/experiments/proposed_feedback_uncertainty_20261016/) | [结果](../../results/proposed_feedback_uncertainty_20261016/) |
| proposed_geometry_integral_20261016 | [源码](workspace/experiments/proposed_geometry_integral_20261016/) | [结果](../../results/proposed_geometry_integral_20261016/) |
| proposed_integral_budget_20261016 | [源码](workspace/experiments/proposed_integral_budget_20261016/) | [结果](../../results/proposed_integral_budget_20261016/) |
| proposed_joint_score_factor_20261016 | [源码](workspace/experiments/proposed_joint_score_factor_20261016/) | [结果](../../results/proposed_joint_score_factor_20261016/) |
| proposed_known_activity_score_20261012 | [源码](workspace/experiments/proposed_known_activity_score_20261012/) | [结果](../../results/proposed_known_activity_score_20261012/) |
| proposed_matrix_geometry_20261016 | [源码](workspace/experiments/proposed_matrix_geometry_20261016/) | [结果](../../results/proposed_matrix_geometry_20261016/) |
| proposed_measurement_response_20261015 | [源码](workspace/experiments/proposed_measurement_response_20261015/) | [结果](../../results/proposed_measurement_response_20261015/) |
| proposed_measurement_root_20261015 | [源码](workspace/experiments/proposed_measurement_root_20261015/) | [结果](../../results/proposed_measurement_root_20261015/) |
| proposed_memory_requirements_20261015 | [源码](workspace/experiments/proposed_memory_requirements_20261015/) | [结果](../../results/proposed_memory_requirements_20261015/) |
| proposed_mixture_message_20261016 | [源码](workspace/experiments/proposed_mixture_message_20261016/) | [结果](../../results/proposed_mixture_message_20261016/) |
| proposed_moment_importance_20261016 | [源码](workspace/experiments/proposed_moment_importance_20261016/) | [结果](../../results/proposed_moment_importance_20261016/) |
| proposed_optimization_20261014 | [源码](workspace/experiments/proposed_optimization_20261014/) | [结果](../../results/proposed_optimization_20261014/) |
| proposed_physical_linear_factor_20261016 | [源码](workspace/experiments/proposed_physical_linear_factor_20261016/) | [结果](../../results/proposed_physical_linear_factor_20261016/) |
| proposed_polar_20261015 | [源码](workspace/experiments/proposed_polar_20261015/) | [结果](../../results/proposed_polar_20261015/) |
| proposed_polar_diagnosis_20261016 | [源码](workspace/experiments/proposed_polar_diagnosis_20261016/) | [结果](../../results/proposed_polar_diagnosis_20261016/) |
| proposed_probability_consistency_20261016 | [源码](workspace/experiments/proposed_probability_consistency_20261016/) | [结果](../../results/proposed_probability_consistency_20261016/) |
| proposed_query_distribution_20261015 | [源码](workspace/experiments/proposed_query_distribution_20261015/) | [结果](../../results/proposed_query_distribution_20261015/) |
| proposed_query_terms_20261015 | [源码](workspace/experiments/proposed_query_terms_20261015/) | [结果](../../results/proposed_query_terms_20261015/) |
| proposed_repair_literature_20261016 | [源码](workspace/experiments/proposed_repair_literature_20261016/) | [结果](../../results/proposed_repair_literature_20261016/) |
| proposed_score_factor_split_20261016 | [源码](workspace/experiments/proposed_score_factor_split_20261016/) | [结果](../../results/proposed_score_factor_split_20261016/) |
| proposed_spatial_feedback_20261014 | [源码](workspace/experiments/proposed_spatial_feedback_20261014/) | [结果](../../results/proposed_spatial_feedback_20261014/) |
| proposed_spatial_messages_20261016 | [源码](workspace/experiments/proposed_spatial_messages_20261016/) | [结果](../../results/proposed_spatial_messages_20261016/) |
| proposed_speed_20261014 | [源码](workspace/experiments/proposed_speed_20261014/) | [结果](../../results/proposed_speed_20261014/) |
| proposed_stopping_validation_20261014 | [源码](workspace/experiments/proposed_stopping_validation_20261014/) | [结果](../../results/proposed_stopping_validation_20261014/) |
| proposed_structured_iteration_20261016 | [源码](workspace/experiments/proposed_structured_iteration_20261016/) | [结果](../../results/proposed_structured_iteration_20261016/) |
| proposed_subspace_20261015 | [源码](workspace/experiments/proposed_subspace_20261015/) | [结果](../../results/proposed_subspace_20261015/) |
| proposed_temporal_20261015 | [源码](workspace/experiments/proposed_temporal_20261015/) | [结果](../../results/proposed_temporal_20261015/) |
| proposed_training_200_100_100_20261012 | [源码](workspace/experiments/proposed_training_200_100_100_20261012/) | 见该目录内的来源记录 |
| proposed_uniform_inference_20261014 | [源码](workspace/experiments/proposed_uniform_inference_20261014/) | [结果](../../results/proposed_uniform_inference_20261014/) |
| proposed_uniform_spatial_20261015 | [源码](workspace/experiments/proposed_uniform_spatial_20261015/) | [结果](../../results/proposed_uniform_spatial_20261015/) |
| proposed_unitary_joint_ep_20261016 | [源码](workspace/experiments/proposed_unitary_joint_ep_20261016/) | [结果](../../results/proposed_unitary_joint_ep_20261016/) |
| proposed_unitary_mixture_20261016 | [源码](workspace/experiments/proposed_unitary_mixture_20261016/) | [结果](../../results/proposed_unitary_mixture_20261016/) |
| proposed_weak_user_diagnosis_20261016 | [源码](workspace/experiments/proposed_weak_user_diagnosis_20261016/) | [结果](../../results/proposed_weak_user_diagnosis_20261016/) |
| query_matched_20261015 | [源码](workspace/experiments/query_matched_20261015/) | [结果](../../results/query_matched_20261015/) |
| route_rank_one_20261006 | [源码](workspace/experiments/route_rank_one_20261006/) | [结果](../../results/route_rank_one_20261006/) |
| route_score_evidence_20261006 | [源码](workspace/experiments/route_score_evidence_20261006/) | [结果](../../results/route_score_evidence_20261006/) |
| shen_phase_update_20261015 | [源码](workspace/experiments/shen_phase_update_20261015/) | [结果](../../results/shen_phase_update_20261015/) |
| small_direction_marginal_20261013 | [源码](workspace/experiments/small_direction_marginal_20261013/) | [结果](../../results/small_direction_marginal_20261013/) |
| small_estimated_direction_20261013 | [源码](workspace/experiments/small_estimated_direction_20261013/) | [结果](../../results/small_estimated_direction_20261013/) |
| two_candidate_comparison_20261006 | [源码](workspace/experiments/two_candidate_comparison_20261006/) | [结果](../../results/two_candidate_comparison_20261006/) |
| two_route_development_20261006 | [源码](workspace/experiments/two_route_development_20261006/) | [结果](../../results/two_route_development_20261006/) |

## 其他材料

- [旧 outputs 2 记录](<workspace/outputs 2/>)。
- [原临时文献材料](workspace/tmp/)，链接仍解析到原有归档中的材料。

`historical_snr8_extension_20261016` 仅准备了补跑代码，未启动推断；用户随后优先进行本次整理。该目录的归档不代表 8 dB 实验已经完成。
