# 白噪声主 SNR 结果采用与工作稿同步

2026-11-07：按既有授权完成白噪声网络主 SNR 估计相位的 6000 份推断、完整重评分、配对比较及论文采用。结果于北京时间 03:09 完成最终重评分，后续核对协调器和全部工作进程已经退出。

## 数据与结论

- [完整比较表](../../../result/snr_comparison/data/white_phase_frontend_marginal_1000_20261106/closing_20261107/COMPARISON.md)：三种配置的每档能量汇总 NMSE、全部设备 AER、漏检、虚警和迭代上限数。
- [实验完成收据](../../../result/snr_comparison/data/white_phase_frontend_marginal_1000_20261106/COMPLETION.json)为 PASS；[汇总](../../../result/snr_comparison/data/white_phase_frontend_marginal_1000_20261106/SUMMARY.json)为 VERIFIED。白噪声估计相位、原有色估计相位、白噪声已知相位共 18000 份保存预测已重评分并核验输入与输出哈希，每种配置每档 1000 个场景。
- [补充核验](../../../result/snr_comparison/data/white_phase_frontend_marginal_1000_20261106/closing_20261107/COMPLETION_VERIFICATION.json)检查完成收据、汇总和逐场景表哈希、全部新结果元数据、历史保留结果、运行时适配绑定及实际进程退出。两次历史 Windows 状态文件冲突及修复记录完整保留；本批新结果无迭代上限输出，参照配置的有限上限输出全部计入。
- 白/有色网络估计相位的最大绝对 NMSE 差为 0.104245 dB，最大 AER 差为 0.03 个百分点；低 SNR 白噪声结果略差，高 SNR NMSE 略好。这里描述本批配对场景的观察，不宣称统计等价。相对白噪声已知相位，估计相位损失为 0.279507–0.604199 dB。

## 本次修改

新图源为 [main_snr_white_20261107/PLOT_DATA.json](../../../result/snr_comparison/figures/main_snr_white_20261107/PLOT_DATA.json)。仅替换 GP-MP 与 GP-MP-EP 的 12 个汇总行（24 个 NMSE/AER 点）；另外七种配置的 42 行（84 点）逐项一致。原图源、改前图及配置均保留。内部历史方法 ID 仅用于沿用既有图形样式，实际权重归属由新图源的 method_bindings 和实验收据确定。

通过 `src/evaluation/plots/render_paper.py --figures snr_comparison` 重绘图 6，颜色、图例、网格、坐标范围保持。其他九幅图的文件哈希不变。第六章仅修改工作稿数据状态和两处结果数字：0 dB 下已知相位 GP-MP 对 STMP 的 NMSE 优势由约 1.6 dB 更新为约 1.5 dB；估计相位损失由 0.30–0.61 dB 更新为 0.28–0.60 dB。摘要、引言、结论、其余章节、公式、参考文献及 100 场景消融表保持。

## 核验与复现

[DATA_ADOPTION.json](DATA_ADOPTION.json)记录来源；[RENDER.json](RENDER.json)记录 108 个绘图点、绘图代码与来源哈希；[VALIDATION.json](VALIDATION.json)记录保护资产、编译及版面检查。两版均使用 Tectonic 编译成功，仍为 13/14 页、42 条参考文献；未改公式和引用。保留原有 PDF 1.7 输入对输出 1.5 的兼容性提示，无新增越栏、缺字或未定义引用错误。

目视检查了主 SNR 图与两版第 8、11、12 页，文字、图例、图注和曲线没有裁剪或重叠。[preview/](preview)保存渲染预览；`before/`保存改前图源配置、图文件及相关说明。`validate.py` 可在项目 Python 和 `PYTHONPATH=src` 下复核。

图形审核采用实验结果双面板折线图：左 NMSE、右对数 AER；3.5 × 2.65 英寸，主要文字至少 8 pt，矢量 PDF 无嵌入位图。沿用作者已采纳的颜色、标记与线型组合、浅网格及说明性图注，不扩张为图形风格重设。

核心叙述按作者既定阶段作为工作稿固定。图 4 与图 7–10 的其他白噪声替换、导频/用户数/活动概率估计相位曲线及额外 Off-grid SBL 13/25 仍待后续授权推进。本次没有启动后续扫描，也不代表最终投稿定稿。
