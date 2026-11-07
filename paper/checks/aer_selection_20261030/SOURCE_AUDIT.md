# AER 展示精简：现行图源核对

2026-10-30。范围仅为四图的来源、汇总数值和样式核验；未运行实验、推断或训练，未修改 canonical 图、正文、代码或结果。下列路径均相对于 `D:/afdm-gfra`。

## 现行图哈希

四图当前 SHA256 与 `paper/C-STMP/checks/cross_full_500_20261028/VALIDATION.json` 中最终论文图记录完全一致，也与本轮 baseline 一致：

| 图 | SHA256 |
|---|---|
| convergence.pdf | `8195cd6fd7489e8d5e4d257071bd8e9655216945b8857c5ddfdc669027c45d93` |
| user_count.pdf | `d60fbfa5208f2c15e182c96dbf78017c7d4a0acbdacb8c8d5ff10caf042a6286` |
| activity_probability.pdf | `4046be132307e4d6ee10dec7bbb6afd597d3551e00f9b5af9de8e75f48139f85` |
| cross_channel.pdf | `b7e2c7720260600acbbfe95cada2cfae0971b5dc06cd27a848ce71b77bc90dd0` |

## 最小可靠绘图来源

### 收敛

- `result/snr_comparison/figures/convergence_current_paper_20261026/PLOT_DATA.json`
- 同目录 `CONFIG.json`、`FIGURES.json`、`CHECKS.json`。
- 绘图数据 SHA256：`5e0585ffc6f49ed9035e643f5b9a3f0d8f9157143f3b5445ed8ac404c52b0131`，与 FIGURES 清单一致。
- 145 行：C_STMP 60 行、STMP 85 行；每行有 `method`、`parameters.iteration`、`nmse_db`、`aer`。
- 单场景 200、0 dB、40 用户、5 活跃；不外推曲线，两条曲线在各自原始停止轮数 60、85 截止。
- `metadata.sources` 内 PLAN、两份 JSON 和两份 NPZ 的五个哈希均重新核验通过。
- 实际入口 `src/evaluation/plots/convergence.py`，最终调用 `configurable.render`。本轮可直接复用 PLOT_DATA，不必重新读取/评分 NPZ。
- 历史 FIGURES 所记 configurable.py 哈希为 `656179...`；当前文件为 `b0d4a2...`，因此不能声称重用完整历史渲染器字节。数据、CONFIG 和原 PDF 均匹配，重绘只使用现有样式函数并显式固定样式即可。
- 原标记位置：C_STMP `[0,9,19,29,39,49,59]`；STMP 另有 `[69,79,84]`。横轴标签 Receiver iteration，刻度 `[1,20,40,60,85]`。

### 用户数

- `result/user_count/figures/redraw_beta01_500_20261028/PLOT_DATA.json`
- 同目录 `CONFIG.json`；重绘入口 `result/user_count/figures/redraw_beta01_500_20261028_render.py`。
- 图源数据 SHA256：`63ad4bcb9ac14bbc09a5d558cedb81fc6c154fa8836d15bed5e4dae14e69b3cf`。
- 汇总 `result/user_count/data/stmp_500_k60_k80_k100_beta01_20261027/SUMMARY.json`，SHA256 `04a4eba9bad57294c3650bc77bc6374a5181c8f8f2cd3c880d961c4b1145ed5b`。
- 30 行 = 六方法 × `[20,40,60,80,100]`；各行 500 场景；PLOT_DATA.rows 与 SUMMARY.rows 完全相等。
- SUMMARY 哈希与 COMPLETE.files 一致。每行 `nmse_db=10 log10(full_error/signal_energy)` 核验通过。
- STMP 阻尼：20/40 用户为 0.2，60/80/100 为 0.1；C-STMP：20/40/60 为 0.4，80 仅场景 372 为 0.2、其余 499 为 0.4，100 全部为 0.2。这些条件在 metadata、SUMMARY、REPORT 中一致，重绘不可替换。
- 实际渲染引擎 `src/evaluation/plots/frozen_user_count_20261026/engine/`；FROZEN.json 中 10 个文件哈希已全部核验通过。
- 20261028 重绘曾通过像素一致性检查：`paper/C-STMP/checks/redraw_user_count_cross_stmp_20261028/VALIDATION.json`。该目录没有 FIGURES.json，不应假设有。

### 活动概率

- `result/activity_probability/figures/stmp_c_stmp_500_20261026/PLOT_DATA.json`
- 同目录 CONFIG、FIGURES；数据 SHA256 `f5a931bf2f8e80332c786a308b2dbda05e1e5f6541f54b95a9e52169752f6373`。
- 汇总 `result/activity_probability/data/stmp_c_stmp_500_20261026/SUMMARY.json`，SHA256 `e498a00a4b3043b43f42050d0bac2c7ab127b4798889c877822dfd9fdc4abb76`。
- 30 行 = 六方法 × `[0.05,0.10,0.15,0.20,0.25]`；每行 500 场景，40 用户、16 帧、0 dB、D 信道。
- PLOT_DATA.rows 与 SUMMARY.rows 相等；SUMMARY 哈希与 COMPLETE.files 一致；每行 NMSE 能量比恒等式核验通过。
- 实际入口为 `result/receiver_sweeps_500_20261026/report.py::render_saved`，使用 `src/evaluation/plots/configurable.py`，而非另一个旧的 standalone baseline 脚本。
- 历史完整审计见 `paper/C-STMP/checks/activity_full_500_20261027/VALIDATION.json`；STMP 两份有限未收敛输出继续包含在汇总中。

### 跨信道

- `result/cross_channel/figures/full_500_paper_20261028/PLOT_DATA.json`
- 同目录 CONFIG；图源数据 SHA256 `3ae6c6ac2f66b48b2f8a9d58e42ff8f962610de9772828b117641b4f328b431a`。
- 汇总 `result/cross_channel/data/stmp_c_stmp_500_20261026/SUMMARY.json`，SHA256 `c53f62a7bd793dc7b3e632849d6377c2a2fd9d1275eedc52a46dfe4cb71a86e0`。
- 144 行 = 六方法 × D/A/B/C 四信道 × 六档 `[-4,-2,0,2,4,6]` dB；各行 500 场景，24 条件、72000 方法结果。
- 本图 PLOT_DATA 是整个 SUMMARY 对象的重新序列化，**不是 PlotData dataclass 字段结构**；应直接取 rows 或显式构建新的 PlotData。
- PLOT_DATA.rows 与 SUMMARY.rows 相等；SUMMARY 哈希与 COMPLETE.files 一致；每行 NMSE 能量比恒等式核验通过。
- 现行 PDF 的真正绘图入口为 `paper/C-STMP/checks/cross_full_500_20261028/render.py`；后续完整版覆盖了早期 stmp_only 及其 v2/v3 图，不能用后者重绘。
- 现行图原为 2×4（NMSE/AER）；信道顺序 D、A、B、C。删去 AER 后可保留同序 1×4 NMSE；原 NMSE 轴范围 `[-20,0]`、每 5 dB 刻度，横轴 -4 至6、每2 dB 刻度。
- STMP 在 A 信道 6 dB、B 信道 4/6 dB 的 NMSE 优于 C-STMP，需原样保留并继续如实描述。

## 行结构、方法顺序与实际样式

用户数/活动概率/跨信道的每行均保留 `method`、`parameters`、扁平条件字段（如 users、snr_db、channel_model）、`scenes`、`full_error`、`signal_energy`、`nmse_db`、活动计数及收敛统计。仅展示字段变化，不应重算/筛选样本。

三幅六方法图方法顺序一致：`C_STMP, STMP, offgrid_sbl, gnn, gamp, somp`，显示名依次 C-STMP、STMP、Off-grid SBL、GNN-ASPL、GAMP-SBL、SOMP。

应使用 `configurable.method_style` 的最终覆盖样式，而非只抄 `style.STYLES`，后者对 C_STMP/STMP 的旧颜色不同：

| 方法 | 颜色 | 标记 | 线型 | 线宽 |
|---|---|---|---|---:|
| C-STMP | `#b83253` | o | 实线 | 0.9 |
| STMP | `#2878b5` | s | 实线 | 0.9 |
| Off-grid SBL | `#20847c` | s | 虚线 | 0.65 |
| GNN-ASPL | `#745c9f` | ^ | 点划线 | 0.65 |
| GAMP-SBL | `#b7802a` | D | 点线 | 0.65 |
| SOMP | `#6d7b8e` | x | 虚线 | 0.65 |

所有标记大小 3.5、边宽 0.7、白色填充。字体 Times New Roman，正文/刻度 8.5 pt，图例 6 pt。主要网格颜色 #909090、alpha 0.8、线宽 0.65。现行三个单栏双面板图总宽 3.5 英寸；改为单面板时建议仍保持 3.5 英寸宽（而不是原半幅 1.75 英寸），并把 `legend.combined_metrics` 从 `['aer']` 改为 `['nmse_db']`，避免图例消失。

当前及冻结 `configurable.py` 哈希均为 `b0d4a2f6d484d4f970a4f4c2219c2f66d78e2b8c8beef61ce58f515307f73555`；当前及冻结 `style.py` 均为 `594af1149c3fd3cdb9f80ea9bbbb97a2819199b28f9dd61a161ff72c71619273`。

## 本次核验边界

本次重新检查现行 PDF、图源数据、SUMMARY 完成封印和汇总恒等式；没有重复扫描全部原始结果文件。原始结果逐份评分、配对覆盖及大规模资产哈希以已完成审计记录为依据。保留所有旧统计及全部有限未收敛结果；这次修改仅移除四图 AER 展示。
