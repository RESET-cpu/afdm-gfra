# 恢复六算法主 SNR 图

> 本轮历史图和绘图脚本已移入归档；当前生图入口见 [统一说明](../../../../src/evaluation/plots/manuscript/README.md)。以下记录描述当时版本。

2026-11-04，按作者最新安排，图 6 暂时撤出旧估计相位曲线，恢复六种已知相位配置。后续新相位与额外两档 Off-grid SBL 预算完成后再补入；第六章分析现在继续。

- 数据：原 `full_grid_final_20261026/PLOT_DATA.json`，每档 1000 配对场景，六档 SNR，六方法；两面板共 72 个数据点。原保存数据未改，未删除不利输出。
- 图例：GP-MP、GP-MP-C、Off-grid SBL、GNN-ASPL、GAMP-SBL、SOMP。保留批准的颜色、标记、线型和字号；图例两行，图宽 3.5 英寸、高 2.5 英寸。
- 同步：第六章相位条件、样本数、图注和旧相位结果句；完整稿附录 B 样本范围及上限统计；旧估计相位评估小节存档移出，附录 A 删除指向该小节的一句引用。
- 1000 场景的 GP-MP/GP-MP-C 分别有 1/3 次达到迭代上限，均在 −4 dB，全部计入指标。其余整机扫描的 500 场景设置保持。
- 两版编译成功，13/14 页、42 篇参考文献；公式、算法、其余图保持。没有未定义引用或 Overfull；已查看变动页面和图 6。Underfull 与 PDF 版本提示仍存在。
- 一般语言候选仅分析，尚未实施。图 7 的 C1 仍按原安排待最终定稿。实验进程和全部结果目录未改动。

[第六章分析](../../docs/CHAPTER_VI_SIX_METHOD_REVIEW_20261104.md) · [主稿](../../main.pdf) · [完整稿](../../main_full.pdf) · [图 6](../../figures/snr_comparison.pdf)

[曲线核验](RENDER_VALIDATION.json) · [稿件核验](VALIDATION.json) · [完整差异](SOURCE_DIFF.txt) · [修改前备份](before/) · [旧相位评估说明](archived_estimated_phase_evaluation.tex) · [图预览](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/snr_six_methods_20261104/previews/snr_comparison.png) · [变动页预览](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/snr_six_methods_20261104/previews/changed_pages.png)

`restore_snr.py` 是本轮首次恢复入口，使用 Python 3.12 及已有绘图依赖。已有备份时会拒绝重复覆盖；当前图副本及 SVG 位于 `staged_figures/`。`verify_revision.py` 可单独重复核查。后续重绘图 6 不应使用历史七曲线入口覆盖此版本。
