# 主 SNR 图加入两档完成的 Off-grid SBL

2026-11-05，按作者要求将新增 13／25 点配置加入主 SNR 的 NMSE、AER 双面板图。

- 数据来源：`result/snr_comparison/data/offgrid_search_budgets_1000_cpu_20261105/SUMMARY.json`，其完成记录及独立核验均为 PASS；12000 次新增推断覆盖两档、1000 个共同物理场景、六档 SNR。
- 新绘图快照：`result/snr_comparison/figures/main_snr_sbl_budgets_20261105/PLOT_DATA.json`。旧快照保留；原七种配置的 42 行、84 个点逐项保持，新增 12 行、24 点，共 108 点。
- 原 7 点配置与完成汇总复核一致。三档都达到 120 轮上限，有限输出全部保留；已完成运行不表示达到收敛阈值。新档位沿用原活动阈值，未重新拟合。
- 图例 `Off-grid SBL (7/13/25)` 的数字表示多普勒网格点数。三档均为 112 个时延点，保留候选分别为 12／24／48，每轮偏移候选分别为 48／96／192。网格与候选预算同时变化。
- 亮蓝色 `#0000ff` 保持，三档分别使用方块虚线、圆圈点划线、倒三角点线。STMP 亮粉色、GP-MP 与 GP-MP-EP 红色保持；8 pt、三列三行图例，原 3.5×2.65 英寸画布。25 点配置低 SNR 的 AER 为 0.0111，因此纵轴上限改为 0.02，所有点均位于显示范围内。
- 论文同步使用矢量 PDF；PNG 同步更新，防止继续展示过期预览。图注解释数字，VI-A3 列明三档设置；未新增性能优越或收敛结论。
- `main.pdf`／`main_full.pdf` 已用本地 Tectonic 缓存编译，仍为 13／15 页、43 篇参考文献，图 6 均位于第 11 页。无未定义引用、缺字或越栏。独立图、第 11 页及所有受影响页面缩略图已目视检查，无图例越界或遮挡。

记录：`BEFORE_HASHES.json` 与 `before/` 保存改前文件；`DATA_VALIDATION.json` 核对数据来源；`PLOT_VALIDATION.json` 核对实际绘图值与图例边界；`VALIDATION.json` 核对原数据、其他九幅图、冻结绑定及编译稿。`prepare_plot.py` 为本次一次性合并记录；以后从统一入口 `src/evaluation/plots/render_paper.py --figures snr_comparison` 重绘。没有运行实验或训练。
