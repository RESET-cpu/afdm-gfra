# 2026-10-18 代码与结果归档

以 500 场景正式结果为当前入口。主线数值源码、配置、权重与当前实验记录保持原位及原内容。

115 个历史结果目录、14 个研究启动脚本、2 个候选实验目录集中在 `workspace/`；19 份根目录日志中 15 份通过最终核验，4 份在迁移后的检查中缺失。原因尚未确定，未能恢复，见[异常清单](../../results/workspace_cleanup_20261018/ARCHIVE_ISSUE.json)。原有正式路径保留符号链接，但缺失日志的链接不可用。另保存重复目录中 5 个独有文件及原有链接。

- [本次报告](../../results/workspace_cleanup_20261018/REPORT.md)与[执行清单](../../results/workspace_cleanup_20261018/EXECUTION.json)。
- [历史结果](workspace/results/) · [研究脚本](workspace/scripts/) · [候选实验](workspace/experiments/)。
- `workspace/` 中未迁移的依赖通过链接指向原工作区；本归档不是独立冻结副本。
- 删除的 1,928 个文件均有逐字节相同的保留副本，路径和 SHA-256 见执行清单。最终归档检查有上述 4 份日志缺失，不能据此声称所有历史材料完整。

**当前整体恢复预检失败，`--all` 会在移动文件前停止。可针对单个完整归档路径执行恢复。**

## 查询与恢复

从项目根目录执行：

```sh
.venv/bin/python -B archive/workspace_cleanup_20261018/restore.py --list
.venv/bin/python -B archive/workspace_cleanup_20261018/restore.py --check
.venv/bin/python -B archive/workspace_cleanup_20261018/restore.py --path results/cai_alignment_20261014
.venv/bin/python -B archive/workspace_cleanup_20261018/restore.py --all
```

恢复前检查整个选定范围的路径冲突与常规文件身份，不覆盖后续工作。恢复归档实体后保留反向导航链接；不重建缓存或已去除的重复副本。

## 本批实体

| 原路径 | 归档位置 |
|---|---|
| `results/activity_posterior_20261015` | [查看](<workspace/results/activity_posterior_20261015>) |
| `results/activity_posterior_refinement_20261015` | [查看](<workspace/results/activity_posterior_refinement_20261015>) |
| `results/amp_foundation_20261015` | [查看](<workspace/results/amp_foundation_20261015>) |
| `results/archive_cleanup_20261012` | [查看](<workspace/results/archive_cleanup_20261012>) |
| `results/archive_cleanup_review_20261012` | [查看](<workspace/results/archive_cleanup_review_20261012>) |
| `results/awgn_reference_ladder_20261015` | [查看](<workspace/results/awgn_reference_ladder_20261015>) |
| `results/baseline_comparison_200_20261017_interim_58` | [查看](<workspace/results/baseline_comparison_200_20261017_interim_58>) |
| `results/baseline_comparison_first100_20261017` | [查看](<workspace/results/baseline_comparison_first100_20261017>) |
| `results/baseline_comparison_partial_20261018` | [查看](<workspace/results/baseline_comparison_partial_20261018>) |
| `results/baseline_layout_20261016` | [查看](<workspace/results/baseline_layout_20261016>) |
| `results/baseline_optimization_20261012` | [查看](<workspace/results/baseline_optimization_20261012>) |
| `results/baseline_phase_learning_20261015` | [查看](<workspace/results/baseline_phase_learning_20261015>) |
| `results/baseline_review_20261013` | [查看](<workspace/results/baseline_review_20261013>) |
| `results/baseline_selection_20261014` | [查看](<workspace/results/baseline_selection_20261014>) |
| `results/cai_alignment_20261014` | [查看](<workspace/results/cai_alignment_20261014>) |
| `results/channel512_continuation_20261014` | [查看](<workspace/results/channel512_continuation_20261014>) |
| `results/channel_capacity_20261013` | [查看](<workspace/results/channel_capacity_20261013>) |
| `results/figure_reproduction_20261014` | [查看](<workspace/results/figure_reproduction_20261014>) |
| `results/full_power_channels_w128_20261013` | [查看](<workspace/results/full_power_channels_w128_20261013>) |
| `results/high_snr_receiver_20261014` | [查看](<workspace/results/high_snr_receiver_20261014>) |
| `results/huang_alignment_20261014` | [查看](<workspace/results/huang_alignment_20261014>) |
| `results/huang_comparison_audit_20261014` | [查看](<workspace/results/huang_comparison_audit_20261014>) |
| `results/implementation_audit_20261014` | [查看](<workspace/results/implementation_audit_20261014>) |
| `results/joint_amp_checkpoint_20261015` | [查看](<workspace/results/joint_amp_checkpoint_20261015>) |
| `results/ldamp_noise_matching_20261014` | [查看](<workspace/results/ldamp_noise_matching_20261014>) |
| `results/ldamp_output_integration_20261015` | [查看](<workspace/results/ldamp_output_integration_20261015>) |
| `results/ldamp_paper_audit_20261014` | [查看](<workspace/results/ldamp_paper_audit_20261014>) |
| `results/ldamp_resume_20261014` | [查看](<workspace/results/ldamp_resume_20261014>) |
| `results/ldamp_score_swap_20261015` | [查看](<workspace/results/ldamp_score_swap_20261015>) |
| `results/low_snr_parameterization_20261014` | [查看](<workspace/results/low_snr_parameterization_20261014>) |
| `results/network_cleanup_20261014` | [查看](<workspace/results/network_cleanup_20261014>) |
| `results/offgrid_budget_20261014` | [查看](<workspace/results/offgrid_budget_20261014>) |
| `results/offgrid_original_grid_20261014` | [查看](<workspace/results/offgrid_original_grid_20261014>) |
| `results/offgrid_sbl_audit_20261012` | [查看](<workspace/results/offgrid_sbl_audit_20261012>) |
| `results/offgrid_sbl_reference_20261013` | [查看](<workspace/results/offgrid_sbl_reference_20261013>) |
| `results/offgrid_selection_20261014` | [查看](<workspace/results/offgrid_selection_20261014>) |
| `results/oracle_direction_small_20261013` | [查看](<workspace/results/oracle_direction_small_20261013>) |
| `results/phase_feasibility_20261015` | [查看](<workspace/results/phase_feasibility_20261015>) |
| `results/phase_frontend_research_20261017` | [查看](<workspace/results/phase_frontend_research_20261017>) |
| `results/physical_message_20261015` | [查看](<workspace/results/physical_message_20261015>) |
| `results/proposed_1000_20261016` | [查看](<workspace/results/proposed_1000_20261016>) |
| `results/proposed_ablation_20261012` | [查看](<workspace/results/proposed_ablation_20261012>) |
| `results/proposed_activity_repair_20261016` | [查看](<workspace/results/proposed_activity_repair_20261016>) |
| `results/proposed_adaptive_geometry_20261016` | [查看](<workspace/results/proposed_adaptive_geometry_20261016>) |
| `results/proposed_adaptive_geometry_20261016_PREFLIGHT.log` | [查看](<workspace/results/proposed_adaptive_geometry_20261016_PREFLIGHT.log>) |
| `results/proposed_amp_20261015` | [查看](<workspace/results/proposed_amp_20261015>) |
| `results/proposed_amp_damping_20261015` | [查看](<workspace/results/proposed_amp_damping_20261015>) |
| `results/proposed_amp_revision_20261015` | [查看](<workspace/results/proposed_amp_revision_20261015>) |
| `results/proposed_awgn_20261014` | [查看](<workspace/results/proposed_awgn_20261014>) |
| `results/proposed_awgn_mean_scale_20261016` | [查看](<workspace/results/proposed_awgn_mean_scale_20261016>) |
| `results/proposed_awgn_mean_scale_20261016_initial_precision_failure` | [查看](<workspace/results/proposed_awgn_mean_scale_20261016_initial_precision_failure>) |
| `results/proposed_awgn_weighting_20261016` | [查看](<workspace/results/proposed_awgn_weighting_20261016>) |
| `results/proposed_axis_control_20261015` | [查看](<workspace/results/proposed_axis_control_20261015>) |
| `results/proposed_axis_control_20261015.log` | [查看](<workspace/results/proposed_axis_control_20261015.log>) |
| `results/proposed_cai_equation_audit_20261015` | [查看](<workspace/results/proposed_cai_equation_audit_20261015>) |
| `results/proposed_cai_relaxation_20261015` | [查看](<workspace/results/proposed_cai_relaxation_20261015>) |
| `results/proposed_colored_20261015` | [查看](<workspace/results/proposed_colored_20261015>) |
| `results/proposed_covariance_constraints_20261015` | [查看](<workspace/results/proposed_covariance_constraints_20261015>) |
| `results/proposed_ddrm_20261015` | [查看](<workspace/results/proposed_ddrm_20261015>) |
| `results/proposed_delay_coordinates_20261016` | [查看](<workspace/results/proposed_delay_coordinates_20261016>) |
| `results/proposed_delay_coordinates_20261016_CHECK.log` | [查看](<workspace/results/proposed_delay_coordinates_20261016_CHECK.log>) |
| `results/proposed_feedback_uncertainty_20261016` | [查看](<workspace/results/proposed_feedback_uncertainty_20261016>) |
| `results/proposed_geometry_integral_20261016` | [查看](<workspace/results/proposed_geometry_integral_20261016>) |
| `results/proposed_integral_budget_20261016` | [查看](<workspace/results/proposed_integral_budget_20261016>) |
| `results/proposed_joint_phase_20261017` | [查看](<workspace/results/proposed_joint_phase_20261017>) |
| `results/proposed_joint_score_factor_20261016` | [查看](<workspace/results/proposed_joint_score_factor_20261016>) |
| `results/proposed_known_activity_score_20261012` | [查看](<workspace/results/proposed_known_activity_score_20261012>) |
| `results/proposed_matrix_geometry_20261016` | [查看](<workspace/results/proposed_matrix_geometry_20261016>) |
| `results/proposed_mean_feedback_20261012` | [查看](<workspace/results/proposed_mean_feedback_20261012>) |
| `results/proposed_measurement_response_20261015` | [查看](<workspace/results/proposed_measurement_response_20261015>) |
| `results/proposed_measurement_response_20261015.log` | [查看](<workspace/results/proposed_measurement_response_20261015.log>) |
| `results/proposed_measurement_root_20261015` | [查看](<workspace/results/proposed_measurement_root_20261015>) |
| `results/proposed_measurement_root_20261015.log` | 缺失，见异常清单（`workspace/results/proposed_measurement_root_20261015.log`） |
| `results/proposed_memory_requirements_20261015` | [查看](<workspace/results/proposed_memory_requirements_20261015>) |
| `results/proposed_memory_requirements_20261015.log` | [查看](<workspace/results/proposed_memory_requirements_20261015.log>) |
| `results/proposed_mixture_message_20261016` | [查看](<workspace/results/proposed_mixture_message_20261016>) |
| `results/proposed_moment_importance_20261016` | [查看](<workspace/results/proposed_moment_importance_20261016>) |
| `results/proposed_optimization_20261014` | [查看](<workspace/results/proposed_optimization_20261014>) |
| `results/proposed_phase_iteration_20261017` | [查看](<workspace/results/proposed_phase_iteration_20261017>) |
| `results/proposed_physical_linear_factor_20261016` | [查看](<workspace/results/proposed_physical_linear_factor_20261016>) |
| `results/proposed_pilot_polar_20261016` | [查看](<workspace/results/proposed_pilot_polar_20261016>) |
| `results/proposed_polar_20261015` | [查看](<workspace/results/proposed_polar_20261015>) |
| `results/proposed_polar_baselines_20261016` | [查看](<workspace/results/proposed_polar_baselines_20261016>) |
| `results/proposed_polar_baselines_30_20261016` | [查看](<workspace/results/proposed_polar_baselines_30_20261016>) |
| `results/proposed_polar_diagnosis_20261016` | [查看](<workspace/results/proposed_polar_diagnosis_20261016>) |
| `results/proposed_probability_consistency_20261016` | [查看](<workspace/results/proposed_probability_consistency_20261016>) |
| `results/proposed_query_distribution_20261015` | [查看](<workspace/results/proposed_query_distribution_20261015>) |
| `results/proposed_query_terms_20261015` | [查看](<workspace/results/proposed_query_terms_20261015>) |
| `results/proposed_repair_literature_20261016` | [查看](<workspace/results/proposed_repair_literature_20261016>) |
| `results/proposed_score_factor_split_20261016` | [查看](<workspace/results/proposed_score_factor_split_20261016>) |
| `results/proposed_snr_20261009_preflight` | [查看](<workspace/results/proposed_snr_20261009_preflight>) |
| `results/proposed_spatial_feedback_20261014` | [查看](<workspace/results/proposed_spatial_feedback_20261014>) |
| `results/proposed_spatial_messages_20261016` | [查看](<workspace/results/proposed_spatial_messages_20261016>) |
| `results/proposed_speed_20261014` | [查看](<workspace/results/proposed_speed_20261014>) |
| `results/proposed_stopping_validation_20261014` | [查看](<workspace/results/proposed_stopping_validation_20261014>) |
| `results/proposed_structured_iteration_20261016` | [查看](<workspace/results/proposed_structured_iteration_20261016>) |
| `results/proposed_subspace_20261015` | [查看](<workspace/results/proposed_subspace_20261015>) |
| `results/proposed_temporal_20261015` | [查看](<workspace/results/proposed_temporal_20261015>) |
| `results/proposed_uniform_spatial_20261015` | [查看](<workspace/results/proposed_uniform_spatial_20261015>) |
| `results/proposed_uniform_spatial_20261015.log` | [查看](<workspace/results/proposed_uniform_spatial_20261015.log>) |
| `results/proposed_uniform_spatial_20261015_confirmation.log` | 缺失，见异常清单（`workspace/results/proposed_uniform_spatial_20261015_confirmation.log`） |
| `results/proposed_uniform_spatial_20261015_derivative_check.log` | [查看](<workspace/results/proposed_uniform_spatial_20261015_derivative_check.log>) |
| `results/proposed_uniform_spatial_20261015_feedback_postcheck.log` | 缺失，见异常清单（`workspace/results/proposed_uniform_spatial_20261015_feedback_postcheck.log`） |
| `results/proposed_uniform_spatial_20261015_feedback_probe_control.log` | [查看](<workspace/results/proposed_uniform_spatial_20261015_feedback_probe_control.log>) |
| `results/proposed_uniform_spatial_20261015_feedback_probe_replay.log` | [查看](<workspace/results/proposed_uniform_spatial_20261015_feedback_probe_replay.log>) |
| `results/proposed_uniform_spatial_20261015_feedback_receiver.log` | 缺失，见异常清单（`workspace/results/proposed_uniform_spatial_20261015_feedback_receiver.log`） |
| `results/proposed_uniform_spatial_20261015_feedback_weighted_check.log` | [查看](<workspace/results/proposed_uniform_spatial_20261015_feedback_weighted_check.log>) |
| `results/proposed_uniform_spatial_20261015_input_filter.log` | [查看](<workspace/results/proposed_uniform_spatial_20261015_input_filter.log>) |
| `results/proposed_uniform_spatial_20261015_input_filter_confirmation.log` | [查看](<workspace/results/proposed_uniform_spatial_20261015_input_filter_confirmation.log>) |
| `results/proposed_uniform_spatial_20261015_noise_reference.log` | [查看](<workspace/results/proposed_uniform_spatial_20261015_noise_reference.log>) |
| `results/proposed_uniform_spatial_20261015_ordered.log` | [查看](<workspace/results/proposed_uniform_spatial_20261015_ordered.log>) |
| `results/proposed_uniform_spatial_20261015_stopping_check.log` | [查看](<workspace/results/proposed_uniform_spatial_20261015_stopping_check.log>) |
| `results/proposed_unitary_joint_ep_20261016` | [查看](<workspace/results/proposed_unitary_joint_ep_20261016>) |
| `results/proposed_unitary_mixture_20261016` | [查看](<workspace/results/proposed_unitary_mixture_20261016>) |
| `results/proposed_weak_user_diagnosis_20261016` | [查看](<workspace/results/proposed_weak_user_diagnosis_20261016>) |
| `results/query_matched_20261015` | [查看](<workspace/results/query_matched_20261015>) |
| `results/scenario_assumptions_audit_20261013` | [查看](<workspace/results/scenario_assumptions_audit_20261013>) |
| `results/shen_phase_update_20261015` | [查看](<workspace/results/shen_phase_update_20261015>) |
| `results/small_data_physics_audit_20261013` | [查看](<workspace/results/small_data_physics_audit_20261013>) |
| `results/small_direction_marginal_20261013` | [查看](<workspace/results/small_direction_marginal_20261013>) |
| `results/small_estimated_direction_20261013` | [查看](<workspace/results/small_estimated_direction_20261013>) |
| `results/small_training_audit_20261013` | [查看](<workspace/results/small_training_audit_20261013>) |
| `results/standalone_mainline_20261012` | [查看](<workspace/results/standalone_mainline_20261012>) |
| `results/storage_cleanup_20261013` | [查看](<workspace/results/storage_cleanup_20261013>) |
| `results/storage_cleanup_20261015` | [查看](<workspace/results/storage_cleanup_20261015>) |
| `results/storage_cleanup_20261017` | [查看](<workspace/results/storage_cleanup_20261017>) |
| `results/storage_prevention_20261014` | [查看](<workspace/results/storage_prevention_20261014>) |
| `results/storage_review_20261013` | [查看](<workspace/results/storage_review_20261013>) |
| `results/storage_review_20261014` | [查看](<workspace/results/storage_review_20261014>) |
| `results/storage_review_20261017` | [查看](<workspace/results/storage_review_20261017>) |
| `results/training_structure_20261011` | [查看](<workspace/results/training_structure_20261011>) |
| `results/unknown_phase_baselines_20261015` | [查看](<workspace/results/unknown_phase_baselines_20261015>) |
| `results/workspace_organization_20261011` | [查看](<workspace/results/workspace_organization_20261011>) |
| `results/workspace_organization_20261013` | [查看](<workspace/results/workspace_organization_20261013>) |
| `experiments/proposed_joint_phase_20261017` | [查看](<workspace/experiments/proposed_joint_phase_20261017>) |
| `experiments/proposed_phase_iteration_20261017` | [查看](<workspace/experiments/proposed_phase_iteration_20261017>) |
| `scripts/evaluate_ldamp_joint.py` | [查看](<workspace/scripts/evaluate_ldamp_joint.py>) |
| `scripts/export_ldamp_joint.py` | [查看](<workspace/scripts/export_ldamp_joint.py>) |
| `scripts/report_ldamp_joint.py` | [查看](<workspace/scripts/report_ldamp_joint.py>) |
| `scripts/run_baseline_phase.py` | [查看](<workspace/scripts/run_baseline_phase.py>) |
| `scripts/run_diffusion_amp.py` | [查看](<workspace/scripts/run_diffusion_amp.py>) |
| `scripts/run_joint_amp.py` | [查看](<workspace/scripts/run_joint_amp.py>) |
| `scripts/run_ldamp_score.py` | [查看](<workspace/scripts/run_ldamp_score.py>) |
| `scripts/run_ldamp_structure.py` | [查看](<workspace/scripts/run_ldamp_structure.py>) |
| `scripts/run_proposed_amp.py` | [查看](<workspace/scripts/run_proposed_amp.py>) |
| `scripts/run_proposed_amp_damped.py` | [查看](<workspace/scripts/run_proposed_amp_damped.py>) |
| `scripts/run_proposed_amp_query_damped.py` | [查看](<workspace/scripts/run_proposed_amp_query_damped.py>) |
| `scripts/train_diffusion_amp.py` | [查看](<workspace/scripts/train_diffusion_amp.py>) |
| `scripts/train_joint_amp.py` | [查看](<workspace/scripts/train_joint_amp.py>) |
| `scripts/train_ldamp_joint.py` | [查看](<workspace/scripts/train_ldamp_joint.py>) |
| `results/baseline_resolution_20261009 2` | [查看](<workspace/results/baseline_resolution_20261009 2>) |
| `results/full_score_nonempty_20261008_100345 2` | [查看](<workspace/results/full_score_nonempty_20261008_100345 2>) |
| `results/proposed_activity_diagnosis_20261009 2` | [查看](<workspace/results/proposed_activity_diagnosis_20261009 2>) |
