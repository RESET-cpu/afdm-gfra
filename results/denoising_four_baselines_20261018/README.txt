独立一阶信道去噪

状态：已完成（2026-10-19）。实验、数据核验及用户确认的论文图已齐备，见 COMPLETION.json。

图：denoising.png / denoising.pdf（同一张图的两种格式）。
绘图数据：SNR_NMSE.csv，每行一个 SNR，列为九条曲线的 NMSE（dB）。
完整统计：STATISTICS.csv、SUMMARY.json，包含误差与信道能量。
图注：CAPTION.txt。
实验说明与核验：REPORT.txt、VERIFICATION.json、ADAPTER_VERIFICATION.json。
图表及数据一致性核验：PRESENTATION.json。

500 个物理场景，每场景 4 个候选信道，六档标称 SNR：−20、−10、0、10、20、30 dB。
曲线：Proposed 5k/50k、SOMP、GAMP-SBL、GNN-ASPL、Off-grid SBL、LS、Gaussian prior、Genie conditional MMSE。
Proposed 采用红色圆圈、实线；训练样本量以文字和红色深浅区分。

逐场景数据：scenes/、ALL_SCENES.npz、BASELINE_RECORDS.csv。
首场景完整预测：scene000_predictions.npz。
Proposed 云端结果、训练权重及配对核验：../denoising_merged_20261018/。
输入观测和真值：../local_baselines_20261018/formal/channel_denoising/。

适用范围：一阶均值去噪。四基线使用原接收机配置迁移到独立去噪任务；字典表示与 Off-grid 重建局限见 ../denoising_baseline_diagnosis_20261019/REPORT.md。
统计采用汇总误差能量与信道能量之比；图中为点估计。5k/50k 为训练信道数，两组更新次数不同。

重绘：在项目根目录运行 .venv/bin/python results/denoising_presentation_20261019/render.py。
