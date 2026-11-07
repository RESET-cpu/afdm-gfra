# 第六章段落任务、来源和证据边界

本轮采用 academic-research-suite 的 academic-paper 修订流程，按已由作者确认的结构直接编辑。此记录是逐段的来源与论据说明，不是独立外部同行评审，也不将本文实验结果归属于参考论文。

实际读取：`reference/literature/cai2026_stmp_v2.pdf` 的 PDF pp.11–15（VI-A/B/C）；`reference/literature/shen2025.pdf` 的 PDF pp.12–13（V）及 p.9（III-C）。文件均为本地完整论文，未使用搜索摘要代替原段。

| 正文位置 / 段落任务 | 母本位置与实际支持层次 | 本文数据 / 改写与边界 |
|---|---|---|
| VI 开头与 A：介绍评价顺序、控制条件和数据 | Cai VI-A，p.11–12：数据、网络、评价设置；Shen V，p.12：系统参数、指标和信息条件。借鉴段落任务与顺序。 | 保持本稿 AFDM 模型、训练条件、归一化及指标公式。新增本地 STMP 分类器说明、500 场景图口径和估计相位例外；不移植参考论文的数值。 |
| B 第一段：在活动检测和迭代之外评价信道均值 | Cai VI-B，p.12：先评价 AWGN 去噪、解释 LS / Gaussian / genie 参照。借鉴评价组织；当前公式与测试分布为本文已有定义。 | `channel_denoising/figures/narrow_paper_20261026/PLOT_DATA.json`。正确区分有色训练与白噪声测试，genie 的附加路径信息仍写清楚。 |
| B 结果两段：先说明完整信道先验，再说明训练取舍 | Cai Fig.4 / VI-B，p.12：不同先验、结构及误差之间的解释。本文结果独立措辞。 | 有色 vs Gaussian 在 0 dB 的差距；有色 vs 白训练在低 SNR 改善、高 SNR 变差。训练参数化及预条件也改变，不宣称单因素消融；稀疏表示误差属于与结果一致的解释，不声称已分离每项原因。 |
| C：固定接收机其余模块，替换活动概率 | density ratio estimation 沿用 Menon–Ong §3、§4.2、式(6)–(8)/(16)–(17) 的既有术语登记；活动后验与联合矩沿用本文 III/IV。Cai VI-C、Fig.7，p.13 展示检测与信道估计间的消息联系，但没有本文此项消融。 | `c_stmp_ablation_1000_20261028/phase_only_20261029/GAUSSIAN_RETAINED_SUMMARY.json`。仅报告共同 354 场景 × 六档 SNR 的 AER。activity evidence 是对本文似然比输入的描述，不是另创的算法名。结果仅支持当前高斯近似、接收机和分布。 |
| D-1：解释单场景迭代轨迹 | Cai VI-C / Fig.5，p.12–13；Shen V / Fig.5，p.12–13。借鉴初始变化、下降和最终精度的分析顺序。 | `convergence_current_paper_20261026/PLOT_DATA.json`。保留单场景身份、不同阻尼设置和实际终止点，不移植 Cai 的初始路径损耗误差猜想或平均速度结论。 |
| D-2 前两段：SNR 下的估计与检测 | Cai VI-C / Fig.6–7，p.13；Shen V / Fig.7，p.13。借鉴分别比较 NMSE / 检测及讨论差异的组织。 | `phase_selected_main_500_20261102/PLOT_DATA.json`。500 场景重新汇总，正文 43% 与新图一致。比较两类基线的增益趋势；不同指标权重来自本稿定义。 |
| D-2 第三段：同一图中的估计相位曲线 | Shen V，p.12：清楚区分算法的相位条件；III-C 式(47)–(54)，p.9：后验量辅助相位更新。仅借鉴问题和方法思路。 | 完成的选定相位批次 3000 份输入，NMSE 损失约 0.26–0.31 dB；高 SNR 的 AER 仍有损失。其他基线已知相位，停止规则和选择场景重用写入附录。 |
| D-3：候选规模与固定精度阈值 | Cai VI-C / Fig.8，p.13–14：以目标 NMSE 对照支持的候选数量。借鉴分析关系，不移植容量数值。 | `user_count/figures/redraw_beta01_500_20261028/PLOT_DATA.json`。候选维度和活动人数均变化；STMP 与 off-grid 的增益趋势不同。保留回顾性阻尼说明，不称独立固定配置验证。 |
| D-4：固定候选规模下的活动密度 | Cai VI-C / Fig.9，p.13–14：改变活动概率。本文区分其与 K 扫描的控制条件。 | `activity_probability/figures/stmp_c_stmp_500_20261026/PLOT_DATA.json`。活动维度增加，候选空间及导频维度固定，阻尼不变。 |
| D-5：导频资源与稳定性 | Cai VI-C / Fig.10，p.14：导频有限时的收益；Shen V / Fig.6，p.13：帧数影响及条件分析。借鉴解释顺序。 | `pilot_frames/figures/full_grid_final_20261026/PLOT_DATA.json`。24 vs 32 是测试网格上首次达到 −14 dB；总能量 QE_p 随帧数增加。Q=8 与正常收敛区间区分，未删除不利结果。 |
| E：不重新训练时的跨分布表现 | Cai VI-C / Fig.11，p.14：cross-CDL / channel model mismatch 的测试组织。 | `cross_channel/figures/full_500_paper_20261028/PLOT_DATA.json` 与 `src/evaluation/profiles.py`。D/C 含 LOS、A/B 为 diffuse，保留 A/B 高 SNR 反转。对训练分布差异的解释明确用 suggests，不继承 Cai 的全范围优势。 |
| V / 附录 A、C：使相位曲线与算法说明一致 | Shen III-C 式(47)–(54)，p.9 提供条件期望平方残差的相位更新思路；本文已有 `PHASE_MESSAGE_GEM.md` 给出带共同斜率和固定 Gaussian 消息的适配。 | 对照 `src/algorithm/C_STMP_phase_selection_20261030/iterations.py`、`src/algorithm/proposed/phase_update.py`、`src/algorithm/STMP/phase_output_cycle_stopping.py` 及选定配置。附录新增的是本文实际算法描述，不冒称 Shen 原算法；其余编号公式保持。 |

本文没有复制参考论文的结果句来替代证据，也没有为各句勉强指定完整原句来源。上表的“借鉴组织”只表示段落所回答的问题与展开顺序相近；新写的结果分析由绑定数据支持。数值逐项机器核对结果见 `VALIDATION.json`，语义与逻辑由本次内联审读完成。
