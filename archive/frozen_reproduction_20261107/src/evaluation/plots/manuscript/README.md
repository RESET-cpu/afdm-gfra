# 当前论文图的统一生成入口

2026-11-07 后续：图 4 绑定 `result/channel_denoising/figures/white_mainline_500_20261107/PLOT_DATA.json`，图 3 绑定同目录 `scene000_example.npz`。500 场景去噪已重评分核验，原图源保持；白噪声后续扫描已获作者授权，当前阶段见 `result/white_followup_20261107/REQUEST.json`。

2026-11-07：主 SNR 的 GP-MP／GP-MP-EP 已绑定 `result/snr_comparison/figures/main_snr_white_20261107/PLOT_DATA.json`，每档 1000 场景、共 108 个曲线点；原图源保留，其他七条曲线及颜色、图例、浅网格保持。[采用与核验](../../../../paper/C-STMP/checks/white_snr_adopted_20261107/README.md)。

2026-11-06：图 3 的公式引用改为读取 `paper/C-STMP/main.aux` 中的标签。公式重新编号后，先编译主稿，再以 `--figures learned_receiver` 单独重绘图 3，最后编译两版论文。无需重绘实验图。[本轮核验](../../../../paper/C-STMP/checks/equation_numbering_revision_20261106/README.md)。

2026-11-06：七幅实验图统一使用浅灰主网格（#b9b9b9，alpha 0.65，线宽 0.45）；对数坐标辅助网格为 #d4d4d4、alpha 0.45、线宽 0.35。双面板配置与通用绘图入口同步，共 888 个曲线点。

2026-11-06：收敛图采用 30 个配对场景、三种算法、前 150 次迭代的 NMSE，共 450 点；Off-grid SBL 使用原基础配置，图例不标 7。数据源为 `result/snr_comparison/figures/convergence_first30_300_20261105/PAPER_PLOT_DATA.json`，统一入口的 `convergence` 已绑定并核验。以下旧单场景及等待多场景实验的说明为历史记录。

2026-11-05：主 SNR 图新增完成核验的两档 Off-grid SBL，当前共九种配置、每档 1000 场景，主图 108 点，七幅实验图合计 583 点。当前合并快照为 `result/snr_comparison/figures/main_snr_sbl_budgets_20261105/PLOT_DATA.json`；此前快照保留。三档图例中的 7／13／25 表示多普勒网格点数，保留候选及偏移候选预算也随档位改变，不能解释为仅改变网格密度。数据来源和视觉核验见 [本轮记录](../../../../paper/C-STMP/checks/snr_sbl_budgets_20261105/README.md)。下文七种配置及新 SBL 待完成的说明为历史状态。

从仓库根目录运行 `src/evaluation/plots/render_paper.py`。这是当前 CGP-MP 稿件十幅图的唯一维护入口；只读取保存数据，不执行推断、训练或新场景生成。

```powershell
# 查看图名、顺序及数据来源，不生成文件
& .\.venv\Scripts\python.exe -B src/evaluation/plots/render_paper.py --list

# 重新生成当前十幅 PDF 到 paper/C-STMP/figures/
& .\.venv\Scripts\python.exe -B src/evaluation/plots/render_paper.py

# 单独重绘；可指定新的输出目录
& .\.venv\Scripts\python.exe -B src/evaluation/plots/render_paper.py --figures cross_channel --output result/tmp/paper_figures

# 临时重绘、对照当前论文图，结束后自动删除临时图，不改论文
& .\.venv\Scripts\python.exe -B src/evaluation/plots/render_paper.py --check --report result/tmp/paper_figure_check.json
```

可使用 `--formats pdf svg png` 按需导出 SVG 和 600 dpi PNG。默认仅保存论文实际使用的 PDF，不额外生成预览副本。重复执行会替换所选输出目录中的同名生成文件，不改正文或编译论文。

## 配置和来源

- [当前配置](../../../configs/plots/manuscript.json)：图号、输入路径和 SHA-256、图例、样式、坐标设置，以及当前已确认的数据范围。
- `system.py`、`factor.py`、`receiver.py`：三幅方法图；共用 `vector.py` 的矢量绘图工具。
- `experiments.py`：七幅实验图；复用上一级 `style.py` 和 `configurable.py` 的绘图基础功能。没有对历史 `paper/C-STMP/checks/` 脚本的依赖。
- [当前成图目录](../../../../paper/C-STMP/figures/README.md)；[归并核验](../../../../paper/C-STMP/checks/figure_consolidation_20261104/README.md)。

源文件哈希变化时停止绘图，先核对新的实验结果及场景范围，再更新配置。原始实验记录和当前图的数据绑定保留，不能只修改哈希来绕过核验。SNR 当前为六种已知相位配置与 CGP-MP-EP 共七种配置、每档 1000 场景；收敛图仍为场景 200 的单场景示例。新相位前端的 6000 份结果已完成核验并入图；多场景收敛与新 SBL 预算需完成各自实验后单独更新。设备数图沿用当前稿件数据，C1 的最终处置状态不因代码归并而改变。

### 算法配色约定（2026-11-04 作者确认）

- 2026-11-05 作者要求在青绿色系内增大区分：GNN-ASPL 使用亮青绿 `#00a0a0`，GAMP-SBL 使用海绿 `#2e8b57`，SOMP 使用深墨绿 `#123d2a`。六幅相关图及双面板内外配置共 24 处同步；原线型和标记保持。

- Off-grid SBL 使用 Shen 图 6–7 的亮蓝色 `#0000ff`（2026-11-05 作者要求），保留方块标记和虚线。

- STMP 基线统一使用 Shen 图 6–9 所用的亮粉色 `#ff00ff`（2026-11-05 作者最新要求），保留圆圈标记和虚线；独立去噪图中的历史数据键 `proposed` 亦按其当前 STMP 标签处理。
- CGP-MP 保持红色 `#ff0000`、方块标记和实线。
- CGP-MP-EP 已加入主 SNR 图，使用红色 `#ff0000`、三角标记和虚线。SNR 图例采用三列三行，画布为 3.5 × 2.65 英寸，保持 8 pt 图例。
- 后续 GP-MP 白高斯噪声训练版本继续使用红色，以另一种线型和标记区分；其评估尚未完成，不增加曲线或空图例。
- 双面板图的 `panel_config.styles` 与外层 `styles` 必须同步。当前七幅实验图及两版论文已更新，见[本轮核验](../../../../paper/C-STMP/checks/stmp_xu_pink_20261104/README.md)。

方法图保留既有改绘出处：Shen Fig. 1（PDF 第 3 页）的系统图矢量元素、Cai Fig. 3（PDF 第 10 页）的网络元素；因子图依据本文设备块关系。接收机图中输入/输出切片来自已保存的去噪实验场景 0、设备索引 0、方差索引 3、天线索引 0–2，使用共同幅度色标。绘图不调用去噪网络。

## 环境与核验

使用项目 Python，依赖 Matplotlib、NumPy、PyMuPDF 和 Times New Roman。当前环境的 PyMuPDF 位于已有用户缓存；其他环境应安装 PyMuPDF。版本写入 `--report` 指定的报告。字体或渲染库变化可能影响精确像素比较，应重新进行版面检查。

`--check` 验证输入哈希、559 个曲线点的直接绘制、图例遮挡和画布边界，并将十幅图与现稿按 200 dpi 逐像素比较。它不把已有数据的科学审核状态升级为已完成，也不检查尚未完成的实验。

上一级的通用工具和 `frozen_user_count_20261026` 仍服务于自定义实验、其他稿件或冻结复现，不再作为当前稿件的默认出图入口。冻结代码、配置和记录保持原文。

主 SNR 合并快照为 `result/snr_comparison/figures/main_snr_estimated_phase_20261104/PLOT_DATA.json`，原六算法快照保持。原数据行逐项一致；新曲线读取完整 `main_1000.frontend_phase`，并从逐场景记录复核。见[新增相位曲线核验](../../../../paper/C-STMP/checks/snr_estimated_phase_1000_20261104/README.md)。
