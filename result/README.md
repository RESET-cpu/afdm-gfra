# 实验结果

按实验类型查数据，按稿件查正式图片。各批次的样本范围、方法和状态以其保存的计划及核验为准；默认配置不代表所有历史批次。

## 数据与论文用图

当前论文七幅独立 PDF 均在 [paper/C-STMP/figures/](../paper/C-STMP/figures/)，部分旧结果目录的图片导出已退役。下表直接链接论文采用图。

| 实验入口 | 论文采用图 | 数据与核验入口 |
|---|---|---|
| [SNR](snr_comparison/) | [SNR 图](../paper/C-STMP/figures/snr_comparison.pdf) | [数据批次](snr_comparison/data/)；已知相位六档 1000 场景比较与新相位候选分别保存 |
| [导频帧数](pilot_frames/) | [导频图](../paper/C-STMP/figures/pilot_frames.pdf) | [数据批次](pilot_frames/data/)；论文采用前 500 场景，原计划和未采用输出保留 |
| [用户数](user_count/) | [用户数图](../paper/C-STMP/figures/user_count.pdf) | [数据批次](user_count/data/)；[500 场景核验](../paper/C-STMP/checks/user_count_beta01_500_20261028/VALIDATION.json) |
| [活动概率](activity_probability/) | [活动概率图](../paper/C-STMP/figures/activity_probability.pdf) | [数据批次](activity_probability/data/)；[完整比较核验](../paper/C-STMP/checks/activity_full_500_20261027/VALIDATION.json) |
| [跨信道](cross_channel/) | [跨信道图](../paper/C-STMP/figures/cross_channel.pdf) | [数据批次](cross_channel/data/)；[完整比较核验](../paper/C-STMP/checks/cross_full_500_20261028/VALIDATION.json) |
| [独立去噪](channel_denoising/) | [去噪图](../paper/C-STMP/figures/channel_denoising.pdf) | [数据批次](channel_denoising/data/)；保留原始结果、训练和诊断记录 |
| 收敛（随 SNR 存放） | [收敛图](../paper/C-STMP/figures/convergence.pdf) | [当前轨迹记录](snr_comparison/data/c_stmp_current_convergence_20261026_scene0200_snr0/RESULT.json) |
| [运行时间](runtime_comparison/) | 未列入当前七幅图 | [数据索引](runtime_comparison/data/README.md)；并发实验耗时不能替代独立算法时延 |
| [密度比消融](density_ratio_ablation/) | 未列入当前七幅图 | [数据索引](density_ratio_ablation/data/README.md)；保留旧定义与记录 |

图例名称和展示指标的最近调整见[命名核验](../paper/C-STMP/checks/algorithm_name_20261030/REVISION_NOTES.md)与[图源核对](../paper/C-STMP/checks/aer_selection_20261030/SOURCE_AUDIT.md)。参数开发、评估重叠和未收敛结果的详细说明随原批次及稿件附录保留。

## 新相位批次

2026-10-30 整理时，[新相位 500 场景批次](snr_comparison/data/c_stmp_phase_selected_500_20261030/README.md)的 [STATUS.json](snr_comparison/data/c_stmp_phase_selected_500_20261030/STATUS.json) 为 `FAILED`：完成 654/3000，记录两项执行失败，涉及内存分配失败及工作进程退出。本次未重试或继续派发，也未将部分结果替换正式论文图。未来状态须重新读取该文件，完成还须核对完成凭据。

## 存放约定

- 新批次写入 `result/<实验名>/data/<批次名>/`；明确指定独立输出，保留输入身份和配置。
- 绘图来源、汇总及核验放入相应 `figures/<版本名>/`；论文采用 PDF 统一在稿件的 `figures/`，预览只作临时检查。
- `current/`、`history/` 和部分旧索引是早期布局入口，可能对应旧协议，不能仅凭目录名判断是否为论文当前版本。
- `models/`、`data/`、`runs/`、共享场景和旧路径链接保留原位置。部分结果实际位于 E 盘，不沿目录链接重复复制或清理。

## 历史与辅助记录

八类实验目录供日常浏览；已完成的整理、绘图检查和调度记录沿用既有隐藏属性约定收起，原路径仍可访问，可在资源管理器开启“隐藏的项目”查看。本次涉及的十个目录及原属性见[整理映射](../archive/project_cleanup_20261030/MAPPING.json)，入口汇总见[归档索引](../archive/README.md)。

旧结果归档位于 [archive/result_legacy_20261023/](../archive/result_legacy_20261023/)。旧路径按[结果迁移映射](layout_20261021/MAPPING.json)及[2026-10-23 布局记录](../archive/paper_layout_20261026/original_paper/docs/result_layout_20261023/MAPPING.json)查找。

整理前的索引原文保存在[历史副本](../archive/project_cleanup_20261030/before/result/README.md)，其中“等待执行”“尚无结果”等表述为历史状态。
