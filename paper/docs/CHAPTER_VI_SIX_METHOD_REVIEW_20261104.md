# 第六章六算法版本的分析

**2026-11-04 后续状态：作者已确认修改，VI01–VI07、VII01–VII02 全部完成。** 两版 PDF 已更新，13/14 页，43 篇参考文献；以下候选和“未修改”描述保留为本轮审阅时的历史记录，不再视为待处理。见[实施与核验](../checks/chapters_vi_vii_language_selected_20261104/README.md)。

日期：2026-11-04。当前六种配置为 GP-MP、GP-MP-C、Off-grid SBL、GNN-ASPL、GAMP-SBL、SOMP，整机比较均使用已知相位。本轮沿用 pre-submission-reviewer 与 humanizer 检查原则，按作者既有决定区分真实问题与可选措辞。

## 本轮范围与判断

已通读第六章 A–E 全部正文、表 I–II、图 4–10 的说明，并核对保存曲线和更新后 PDF。现有结果足以先分析去噪、活动概率、收敛示例、SNR、设备数、活动概率、导频帧数及跨信道剖面的主要表现。第六章一般语言审读现在可以继续，不再以新相位实验和新增 SBL 预算尚未结束为由暂停整章。

新相位前端的有效性及扩大 Off-grid SBL 搜索预算后的性能，需要后续各自的结果支撑。当前不预设其结果，也不把后续补充称为已完成。本轮仅实施恢复图 6 所必需的图文同步；下述一般语言候选未实施。

## 已实施的图 6 恢复

- 恢复原每档 1000 个场景、六档 SNR、六种接收配置的保存结果，使用原数据全体有限输出；不是在原七曲线的 500 场景子集上简单隐藏一条线。
- 当前名称、配色、标记、线型和字号沿用已批准版本；图例六项排成两行，宽 3.5 英寸，高 2.5 英寸。
- 第六章设置、图注和 SNR 结果段移除旧 GP-MP-C-EP 描述。SNR 为每点 1000 场景，其余相关整机扫描仍为每点 500 场景。
- 完整稿附录 B 同步样本范围及收敛统计：GP-MP 与 GP-MP-C 分别有 1 和 3 次达到迭代上限，均在 −4 dB，全部计入指标。原“500 场景子集各 3000 次均满足停止条件”不再用于新图。
- 原附录 B 的旧估计相位评估小节存档移出，并删除附录 A 指向该小节的一句引用。第五章和相位附录的算法描述保留，待最终新方案确定后统一更新。
- 未改图 7 的数据或选择 C1 的处理方案；未启动、停止或干预实验。

来源：[原六算法数据](../../result/snr_comparison/figures/full_grid_final_20261026/PLOT_DATA.json)；[本轮曲线与统计核验](../checks/snr_six_methods_20261104/RENDER_VALIDATION.json)；[修改差异](../checks/snr_six_methods_20261104/SOURCE_DIFF.txt)。

## 各部分的分析重点与结论范围

| 部分 | 现有证据支持的分析 | 当前处理建议 |
|---|---|---|
| VI-A 仿真设置 | 系统、训练、网络、基线、停止条件与指标均已有定义。主 SNR 恢复 1000 场景，其余扫描 500 场景，独立去噪每档 2000 信道样本，活动概率消融每档 354 配对场景。 | 已同步因本轮恢复发生变化的相位条件和样本数；其余参数不动。 |
| VI-B 独立去噪，图 4 | 两个学习去噪器随 SNR 改善；有色训练版本在低 SNR 更好。−20/−10 dB 的 NMSE 改善约 1.74/2.11 dB；高 SNR 并非处处优于白噪声版本。 | 现稿只写低 SNR 增益，范围正确，保留总体趋势。无需添加逐点报数或另设交叉分析段。 |
| VI-C 密度比估计，表 II | 固定其余接收配置，学习密度比在六档 SNR 下均降低 AER；汇总 AER 约 0.134% 对 36.952%，迭代上限比例 0 对 34.09%。 | 现稿“every evaluated SNR”有数据依据，保留；不把达到迭代上限解释成已有明确单一失效机理。 |
| VI-D1 收敛，图 5 | 一个含五个活动设备的配对场景中，GP-MP-C 更快接近最终 NMSE，停止于 60 次，GP-MP 为 85 次。 | 保留“In this example”，不扩成所有场景的平均速度结论。 |
| VI-D2 SNR，图 6 | GP-MP-C 在六个点的 NMSE 都最低，比 GP-MP 低约 0.41–1.87 dB；AER 在六个点均低于 GP-MP。 | 现有主要对比成立，只需去掉重复 achieves。−4 dB 下 Off-grid SBL 的 AER 为 0.435%，GP-MP-C 为 0.455%；不能写“所有 SNR 下 AER 都最低”。正文仍可只保留总体比较，不必单独讨论该点。 |
| VI-D3 设备数，图 7 | 当前显示数据支持设备数增多时 NMSE 变差。 | C1 按既有安排留待图 7 定稿。当前“maintains the lowest NMSE”和相对优势增长不能视为已最终核定；不重复开启方案选择，也不影响其余段落分析。 |
| VI-D4 活动概率，图 8 | 六种方法的 NMSE 随名义活动概率升高而变差；GP-MP-C 在当前各点最低，相对 GP-MP 的差距从约 1.07 dB 增至 2.25 dB。 | 现有总体趋势表述可保留。 |
| VI-D5 导频帧数，图 9 | 固定每帧能量，增加帧数总体改善估计与检测。GP-MP-C 首个达到 −14 dB 的已评估档位为 Q=24，GP-MP 为 Q=32，因而“25% fewer frames”成立。 | 保留“Among the evaluated pilot-frame counts”和固定每帧能量条件；不是插值得到的连续最小需求。 |
| VI-E 跨信道剖面，图 10 | 在已评估 D/A/B/C 剖面和 SNR 上，GP-MP-C 的 NMSE 均低于四个稀疏恢复基线，且未重新训练。 | 当前“four sparse-recovery baselines”范围准确。A/B 的部分高 SNR 点中 GP-MP 更低，所以不扩大为所有方法、所有点均最优。可澄清比较对象为不同剖面下的性能。 |

图 4 来源：[保存曲线](../../result/channel_denoising/figures/narrow_paper_20261026/PLOT_DATA.json)。图 5、7–10 来源及精确坐标见[现行图形核验记录](../checks/algorithm_name_c_20261104/RENDER_VALIDATION.json)。表 II 数值与上一轮已完成消融报告保持一致，没有重新筛选样本。

## 待作者选择的一般语言修改

以下是原有候选对应当前稿件后的整理，不计作新发现的重大问题。

| 编号 | 当前文字 | 建议 | 性质 |
|---|---|---|---|
| VI01 | “Training and validation use … channels from disjoint scenes, four per scene before multiplication by …” | 将训练/验证样本数量与每场景四个样本拆成两句。 | 可读性小修 |
| VI02 | “train the classifier from random initialization by” 后接损失公式引用 | 将 by 改为 using the loss in，保留原公式引用命令。 | 搭配小修 |
| VI03 | “Their default damping factors are 0.2 and 0.4.” | 明确 GP-MP 与 GP-MP-C 的数值对应，并用 respectively。 | 指代澄清 |
| VI04 | “GP-MP-C achieves the lowest NMSE and achieves lower AER than GP-MP.” | 删除第二个 achieves：“… achieves the lowest NMSE and a lower AER than GP-MP.” | 重复小修 |
| VI05 | “compares the training profile D with profiles A, B, and C without retraining” | 明确为比较这些剖面下的 channel-estimation performance。 | 对象澄清 |
| VI06 | “For Q≤KN, select distinct DFT rows” | 可用 we select 与实验说明语气统一；原祈使句也成立。 | 可选 |
| VI07 | “a matrix extension of the scalar preconditioning in …” | 可补入已核实的矩阵预条件直接来源；不据此修改当前公式。 | 可选补引 |

VI02 保持原引用键 eq:classifier-loss，不按旧文档的印刷式号改写。矩阵预条件来源见[既有出处记录](DAMPING_AND_FORMULA_PROTOTYPES_20261104.md)。本轮没有引入新专业术语，没有改动上述候选句。

## 后续补入范围

新相位结果完成后补充最终前端定义、设置、图中曲线和对应分析；新增 Off-grid SBL 预算完成后补充预算定义及比较。若这些结果改变方法排序或差距，则相应调整 SNR 分析和结论。现阶段按六种配置推进第六章，不预留虚构数值或结论。

本轮校验：两版仍为 13/14 页、42 篇参考文献；编号公式保持。图 6 为矢量图，72 个绘图数值与原保存数据完全一致。除本轮同步涉及的三份章节文件、图 6 及编译产物外，其余保护稿件资产保持。已查看图 6 与变动页面；无未定义引用或越栏，保留已有类别的 Underfull 及插入 PDF 版本提示。

