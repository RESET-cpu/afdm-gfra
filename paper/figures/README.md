# 当前论文图

2026-11-07 后续：图 4 的 GP-MP 六个点及图 3 的同场景示例已采用白噪声输出，其他曲线和样式保持；现仅图 7–10 待逐项替换。[采用核验](../checks/white_denoising_adopted_20261107/README.md)。

2026-11-07：图 6 的 GP-MP／GP-MP-EP 已替换为完成核验的白噪声网络数据，各 1000 场景 × 六档 SNR；其余七条曲线和原样式保持。图 5、6 与表 III 已使用白噪声网络；图 4、7–10 仍待替换。[采用与核验](../checks/white_snr_adopted_20261107/README.md)。下列旧数据状态为历史记录。

2026-11-06：全文公式重新分组后，图 3 的五处公式引用已同步。绘图代码从 `main.aux` 读取编号；修改公式编号时，先编译主稿，再单独重绘 `learned_receiver`，最后重新编译两版。图的其他区域保持，见[核验](../checks/equation_numbering_revision_20261106/README.md)。

2026-11-06 数据版本说明：当前图 5 使用白噪声网络；图 4、6–10 中 GP-MP/GP-MP-EP 的数据仍来自历史训练权重，不能随正文白噪声表述改动而重新归属。本轮保留所有图文件、绘图配置及来源哈希，第六章集中注明待替换状态。见[本轮记录](../checks/white_noise_wording_20261106/README.md)。

2026-11-06：七幅实验图的主网格已统一为更淡的灰色，对数坐标辅助网格同步淡化；两版论文已更新。见[统一网格与核验](../checks/all_plot_grids_20261106/README.md)。

2026-11-06：去噪图纵轴网格间隔改为 10 dB，并采用更淡的灰色。两版论文同步，54 个数据点保持。见[网格调整核验](../checks/denoising_grid_20261106/README.md)。

2026-11-06：图 5 已替换为 30 个配对场景、前 150 次迭代的 NMSE，三条曲线为 GP-MP、STMP、Off-grid SBL（图例不显示预算编号）。原始 90 份结果均含实际 300 次迭代；两版论文及统一绘图入口同步。见[本轮记录](../checks/convergence_30_adopted_20261106/README.md)。

2026-11-05：按作者要求拉开三条青绿色系基线的差异：GNN-ASPL 亮青绿 `#00a0a0`、GAMP-SBL 海绿 `#2e8b57`、SOMP 深墨绿 `#123d2a`。六幅相关图和两版论文已同步。见[配色与核验](../checks/sparse_baseline_green_separation_20261105/README.md)。

2026-11-05：主 SNR 图已加入两档完成的 Off-grid SBL 结果，现有 7 点配置及新增 13／25 点配置均为每档 1000 个配对场景。三条曲线保持亮蓝色，以方块虚线、圆圈点划线、倒三角点线区分；共九种配置、108 个曲线点。AER 上限调整为 0.02，两版论文同步。见[数据与版面核验](../checks/snr_sbl_budgets_20261105/README.md)。

2026-11-05 最新蓝色：Off-grid SBL 改用 Shen 图 6–7 的亮蓝色 **#0000ff**，六幅相关图和两版 PDF 同步。STMP 亮粉色与其他样式保持。出处见[取色记录](../checks/offgrid_shen_blue_20261105/SHEN_SOURCE.json)。

2026-11-05 最新配色：按作者要求，STMP 改用 Shen 图 6–9 的亮粉色 **#ff00ff**，GP-MP/GP-MP-EP 保持红色；七幅实验图和两版 PDF 同步。出处见[取色记录](../checks/stmp_shen_pink_20261105/SHEN_SOURCE.json)。

2026-11-05：七幅实验图统一使用 **GP-MP**，估计相位版使用 **GP-MP-EP**。现有数据与样式保持，见[核验记录](../checks/gp_mp_legends_20261105/VALIDATION.json)。以下带日期名称属于历史记录。

2026-11-04 最新更新：图 6 已加入完整 **CGP-MP-EP** 估计相位曲线，红色虚线三角；当前共七种配置、每档 1000 个配对场景。原 72 点保持，新增 12 点；七幅实验图合计 **559** 点。两版论文同步为 13/15 页。下文“547 点／相位待完成”是此前快照。见[结果与核验](../checks/snr_estimated_phase_1000_20261104/README.md)。

2026-11-04 最新名称：七幅实验图中的 **GP-MP-C** 已统一改为 **CGP-MP**，两版论文已同步。Xu 粉色、其他样式和全部 547 个数据点保持，见[名称核验](../checks/algorithm_name_cgp_mp_20261104/README.md)。

2026-11-04 最新配色：STMP 已统一改为Xu 图 9–11 所用的粉色 `#ff6699`，CGP-MP 保持红色 `#ff0000`；后续白高斯噪声版 GP-MP 和估计相位版 CGP-MP-EP 也使用红色，以不同线型和标记区分。七幅实验图及两版论文已同步，数据和其他样式保持，见[配色核验](../checks/stmp_xu_pink_20261104/README.md)。尚未完成的新版本曲线未提前加入。

2026-11-04 后续：[STMP 基线与 GP-MP 白噪声消融命名同步](../checks/stmp_baseline_white_ablation_20261104/README.md)已完成。七幅实验图的旧 GP-MP 对照统一为 STMP，独立去噪图亦标明 STMP/GP-MP-C，547 个点保持。下文关于图归并及“正式 PDF 保持”的描述是前一轮快照；当前两版论文 PDF 已同步最新名称。

2026-11-04 已统一绘图入口并核对全部十幅图。论文实际使用本目录的十个 PDF；默认出图只保留 PDF，需要 SVG/PNG 时按需导出。

**唯一维护入口：** [render_paper.py](../../src/plotting/render_paper.py)。[使用说明](../../src/plotting/manuscript/README.md) · [当前配置](../../src/configs/plots/manuscript.json) · [复现核验](../checks/figure_consolidation_20261104/README.md)。

| 图号 | 内容 | 当前 PDF | 代码 |
|---|---|---|---|
| 1 | 系统与多帧 AFDM 传输 | [system_multiframe.pdf](system_multiframe.pdf) | [system.py](../../src/plotting/manuscript/system.py) |
| 2 | 设备块因子图 | [factor_graph.pdf](factor_graph.pdf) | [factor.py](../../src/plotting/manuscript/factor.py) |
| 3 | 迭代接收机与 GPJD | [learned_receiver.pdf](learned_receiver.pdf) | [receiver.py](../../src/plotting/manuscript/receiver.py) |
| 4 | 独立信道去噪 | [channel_denoising.pdf](channel_denoising.pdf) | [experiments.py](../../src/plotting/manuscript/experiments.py) |
| 5 | 30 场景收敛 | [convergence.pdf](convergence.pdf) | 同上 |
| 6 | 六种已知相位配置及 CGP-MP-EP 的 SNR | [snr_comparison.pdf](snr_comparison.pdf) | 同上 |
| 7 | 导频帧数 | [pilot_frames.pdf](pilot_frames.pdf) | 同上 |
| 8 | 候选设备数 | [user_count.pdf](user_count.pdf) | 同上 |
| 9 | 活动概率 | [activity_probability.pdf](activity_probability.pdf) | 同上 |
| 10 | 跨信道 A/B/C/D | [cross_channel.pdf](cross_channel.pdf) | 同上 |

实验图沿用已确认的配色、线型、标记、8 pt 图例和 8.5 pt 坐标字。图 4 为下方三列图例；图 6/7 为双面板共享图例；图 10 按 A/B/C/D 排列。本文方法与现有三网络基线分别展示为 CGP-MP、STMP。GP-MP 留给同结构白噪声训练消融，尚未加入曲线。SNR 使用每档 1000 场景；图 5 仍是原单场景，后续多场景方案尚未运行。图 8 的 C1 最终核定状态见[预审决定](../docs/REVIEW_DECISIONS.md)，此次整理未改变统计或结论。

此次没有改动曲线数据、方法图几何、正文、图注或两版论文 PDF。七幅实验图的重绘 PDF 逐字节一致，三幅方法图的 PDF 元数据标识可能不同，但全部十幅图按 200 dpi 渲染逐像素一致。当前正式 PDF 保持原文件。

历史绘图脚本、重复图及预览已[移入归档](../../archive/figure_cleanup_20261104/README.md)。各轮研究记录仍保留，历史记录中“当前入口”等说法不再代表现行入口。原始实验数据、冻结代码与运行中批次未清理。
