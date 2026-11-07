# 2026-11-06 Supervisor 与 Humanizer 复审核验

作者要求再次审阅现稿。本轮为审阅，不修改正式 TeX、书目、PDF、图表或实验数据，也不启动实验。

结果见[复审报告](../../docs/SUPERVISOR_HUMANIZER_REVIEW_20261106.md)。

- `BEFORE_HASHES.json`：审阅前保存的稿件、两版 PDF、十幅图、绘图配置与 FINAL/MAINLINE 的 SHA-256。
- `CHECKS.json`：活动源码引用与标签、现有编译日志、PDF 页数和参考文献数、词项候选、表 III 与保存汇总的 48 个数值单元匹配、SNR 配置数量与 0 dB 数值，以及审阅后哈希核验。
- `main_text.txt`、`main_full_text.txt`：从现有 PDF 提取的检查文本。
- `preview/`：两版全部页面的渲染和缩略图。检查了两版缩略图，并放大复核模型图、算法、表 III、SNR 图、其他实验图及完整稿附录；未见遮挡、裁切或缺图。

表 III 的依据为 `../activity_evidence_four_variants_50_20261106/SUMMARY.json`，本轮未重新评分原始活动数组。SNR 的依据为 `result/snr_comparison/figures/main_snr_sbl_budgets_20261105/PLOT_DATA.json`。源码检查按 `main.tex` 实际输入范围执行；未编入的二阶训练附录不参与缺失引用判定。

本轮没有重新编译；所述日志结论来自现有两版编译日志。检查通过表示所列一致性检查通过，不表示所有投稿待办均已完成。
