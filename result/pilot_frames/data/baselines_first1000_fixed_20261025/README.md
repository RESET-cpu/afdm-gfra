# 历史固定门限的导频重放

用户于 2026-10-25 要求用前 1000 场景研究得到的旧门限重画 SNR 和导频 baseline 图。本目录仅保存现有导频输出的活动判决重放，不是新增推断或正式结果替换。

| 方法 | 固定门限 |
|---|---:|
| Off-grid SBL | 0.07174861272505266 |
| GNN-ASPL | 0.027625354006886486 |
| GAMP-SBL | 0.06753045555230983 |
| SOMP | 0.12201713102013244 |

门限取自 `result/snr_comparison/data/old_first1000_all_fixed_snr10_20261024/FIXED_READOUT.json`，与 `baseline_calibration_reuse1000_20261023/POLICIES.json` 的固定候选一致。场景 0–499、SNR −4/−2/0/2/4/6 dB 用于拟合，500–999 用于验证。本次未重新拟合或按 SNR 分档。SNR 曲线沿用已保存的八档历史重放；导频在 SNR 0 dB、8/16/24/32/40/48 帧应用同一组门限。

两图均包含场景 0–999，每条件 1000 MC。物理场景与门限开发重叠，因此是回顾性诊断，不是独立测试。仅改变活动判决，保留全部信道估计及 NMSE，不运行或汇总 STMP。

已逐项核验导频 24,000 条指针、原始 JSON、compact 数组，以及 6,000 份输入收据和真值文件的哈希；复现原始活动判决计数并核对信道能量汇总。SNR 旧固定门限在拟合与验证集上的错误数已复现；SNR 0 dB 与导频 16 帧的四个 baseline 汇总完全一致。具体证据见 `RESULT_AUDIT.json`，逐场景判决见 `DECISIONS.npz`，汇总见 `SUMMARY.json`。

绘图与重放脚本：`result/snr_comparison/figures/plot_baselines_first1000_fixed_20261025.py`。脚本拒绝覆盖既有派生目录；原正式 `fixed_readout`、冻结 PLAN、门限文件和推断结果均保持原样。

[导频图](../../figures/baselines_first1000_fixed_20261025/pilot_frames_baselines_preview.png) · [PDF](../../figures/baselines_first1000_fixed_20261025/pilot_frames_baselines.pdf)
