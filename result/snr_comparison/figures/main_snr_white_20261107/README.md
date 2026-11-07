# 白噪声主 SNR 图源

本目录采用已通过完整核验的白噪声已知相位 GP-MP 与白噪声估计相位 GP-MP-EP，每档 1000 场景、六档 SNR。其他七条曲线与 `../main_snr_sbl_budgets_20261105/PLOT_DATA.json` 逐项相同，原快照保持。

图源内部历史方法 ID 沿用于既有样式，当前网络和相位归属由 `metadata.method_bindings`、`source_sha256` 与实验完成收据确定。通过 `src/evaluation/plots/render_paper.py --figures snr_comparison` 生成现行论文图。

详见[采用与核验](../../../../paper/C-STMP/checks/white_snr_adopted_20261107/README.md)及[完整比较](../../data/white_phase_frontend_marginal_1000_20261106/closing_20261107/COMPARISON.md)。
