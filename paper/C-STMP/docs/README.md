# C-STMP 研究文档

2026-11-05：[相位估计完整推导](derivations/phase_estimation.md)保留原附录及坐标功率更新细节；论文核心说明已并入 V-B，搜索参数位于 VI-A4。

2026-11-04 最新[算法名称简化](../checks/algorithm_name_cgp_mp_20261104/README.md)：当前方法统一称 **CGP-MP**，估计相位版为 **CGP-MP-EP**；GP-MP 白噪声消融及 STMP 基线名称保持。下面的旧名称保留为历史记录。

2026-11-04 [有色训练未显示优势时的条件性论述方案](REVIEW_DECISIONS.md#colored-training-null-gain-20261104)已获作者确认：若后续匹配消融未显示有色训练优势，围绕“由同一均值网络构造方差反馈、无需独立二阶训练”和“密度比活动证据”论述算法设计。记录包含触发条件、已有证据及归因边界；当前仅保存讨论，正文和训练安排保持。

2026-11-04 最新[STMP 基线与 GP-MP 白噪声消融命名](../checks/stmp_baseline_white_ablation_20261104/README.md)：旧 GP-MP 三网络对照改称 STMP；GP-MP 留给与 GP-MP-C 同结构、同接收机设置的白噪声训练消融。当前图不含尚未完成的新消融。以下记录按历史时点理解。

2026-11-04：[绘图代码归并和历史图清理](../checks/figure_consolidation_20261104/README.md)完成。当前十幅图统一由一个入口生成，原始实验及既有研究决定保持。

本目录保存本稿的方法说明、系统模型、实验协议与术语依据。共用文档为实际文件副本；后续按各稿独立维护，共用定义有变化时同步相关稿件。

文档中的日期、实验状态和性能描述保留原文，仅调整文件链接；当前状态仍以对应实验记录为准。

[返回稿件](../README.md) · [原始文档与历史记录](../../../archive/paper_layout_20261026/README.md)

再次预审先读[预审问题、讨论决定与剩余事项](REVIEW_DECISIONS.md)，复用作者已经回答的内容及已核实证据。该记录区分未解决问题、进行中工作、撤回判断和已完成改动，避免重复询问。

2026-11-04 最新[第六章图序、图例与代表性结果修订](../checks/ch6_results_order_style_20261104/README.md)：图 7/8/9 现在为导频、设备数、活动概率；跨信道按 A/B/C/D 排列，去噪图例与其他实验统一。主 SNR 增加一项 1.6 dB 代表性比较，活动概率段保留必要资源解释；两版仍 13/15 页。多场景收敛目前是已核对可行性的建议，尚未运行或替换图 5。

2026-11-04 [第六章与 Cai 的呈现方式逐节对照](CHAPTER_VI_CAI_PRESENTATION_REVIEW_20261104.md)已获作者授权并[完成实施](../checks/ch6_cai_revision_20261104/README.md)：重组设置、基线分点加粗、增加网络表格，以连续段落分析结果；按作者追加意见删除漏检/误警拆解、具体错误计数及重复条件。主稿/完整稿目前为 13/15 页，图 10 在第 12 页结论之前；43 篇参考文献、46 个编号公式保持。下文历次页数为历史快照。

2026-11-04 当前安排：按作者最新决定，已恢复六算法、已知相位、每档 1000 场景的主 SNR 图，并继续第六章分析；[分节分析及语言候选](CHAPTER_VI_SIX_METHOD_REVIEW_20261104.md)已整理。旧估计相位曲线暂时撤出，新相位及两档新增 Off-grid SBL 预算完成后再补入。该轮语言候选随后已获批准并完成；后续新建议仍先列出供作者选择。[恢复与核验](../checks/snr_six_methods_20261104/README.md)。此前整章等待补充实验的安排已由本条取代。

2026-11-04 [第六、七章复审与实施](CHAPTERS_VI_VII_REVIEW_20261104.md)：作者已确认九项建议，VI01–VI07、VII01–VII02 全部完成。语言、比较对象及矩阵预条件引用已同步；两版仍为 13/14 页，43 篇参考文献。[实施核验](../checks/chapters_vi_vii_language_selected_20261104/README.md)。

2026-11-04 最新：[名称简化为 GP-MP-C](../checks/algorithm_name_c_20261104/REVISION_NOTES.md)。作者确认 C，表示有色高斯噪声训练；正文、六幅实验图例及两版 PDF 已同步。[摘要至第五章连续通读](ABSTRACT_TO_V_REREAD_20261104.md)中的 R01 名称说明已解决，R02 图注精简仍为可选、未实施项。连续通读本身未发现新增的主线、变量关系或公式衔接问题。

论文写作与修订先读[用词出处与段落修订规范](WRITING_GUIDE.md)，再查[术语出处](TERMINOLOGY.md)。前者包含第二章正反例、七项后续修正实例及可供后续章节复用的检查方法。

最新[语言润色前全文复核](POLISH_READINESS_20261104.md)确认当前可以进入语言润色：未发现新增的前置研究阻塞，核对了两版引用、主要结果及已完成的 3000 份相位结果。旧语言表中已被后续修订取代的条目已标记；图 7 仍按既有决定留待定稿。本轮只检查并更新记录，未改稿或 PDF。

摘要与引言的[逐项语言建议及作者决定](ABSTRACT_INTRO_LANGUAGE_REVIEW_20261104.md)已按作者选择执行：摘要原文、CS 及引用作主语写法保留；引言简化 OTFS 信道表示、展开变换名称、精简 JADCE 引出句、删除泛指衔接句并统一表示名称。第五章补 DFT 首次缩写定义，两版 PDF 已更新，仍为 13/14 页；原 11 项分析作为历史快照保留。

随后[摘要、引言复查与第二章语言建议](CHAPTER_II_LANGUAGE_REVIEW_20261104.md)未发现摘要或引言新的必要改动。第二章 S02–S04 已按作者选择实施；再次连读后列出的 S01 及相邻三处也已获授权完成，减少 matrix/indices 类型说明，并用 Define 直接引出跨天线定义。两版 PDF 已更新，仍为 13/14 页；原分析与讨论保留为历史快照。

第三至第五章的[11 项语言修改](CHAPTERS_III_V_LANGUAGE_REVIEW_20261104.md)已全部获作者授权并完成：损失关系正面说明具有相同最优解，存储开销直接列明对象，其余指代、名称、缩写及后验交叉引用按表修改；同步第六章两处排列名称。章节、段落、公式和伪代码保持，两版 PDF 已更新并检查。另有[三章详细逻辑导读](CHAPTERS_III_V_LOGIC_GUIDE_20261104.md)，解释推断目标、学习估计与完整算法的衔接。

随后完成[图 2/3 调整与章节讲解澄清](../checks/method_figures_simplified_20261104/README.md)：因子图使用绿/红分区，第五章示意图参考 Cai/Huang 精简长标签；图 2/3 PDF、SVG、PNG 及两版稿件均已更新。第三章仍使用通用模块名称，第五章使用 MFLE/GPJD；V-B 统一交代参数估计和数值实现，不单设两种方差区别的小节。正文源文件保持。

图 3 后续按作者新要求改为[左侧两模块迭代、右侧 GPJD 展开](../checks/receiver_overview_expansion_20261104/README.md)：内部框线黑色，仅 MFLE/GPJD 外框加粗着色；图注同步，主稿/完整稿仍为 13/14 页。图 2 及其他图保持。

图 3 最新纠正见[平行箭头与局部配色](../checks/receiver_parallel_arrows_color_20261104/README.md)：左侧采用两条平行反向直箭头及浅绿/浅红填充；展开框加粗黑色并去掉重复名称，内部文本框黑色，网络和数组保留彩色。替代上一轮全灰度图示与红色展开框的理解；三格式和两版 PDF 已更新，正文源文件保持。

图 3 随后按作者要求[补全去噪前后对照](../checks/receiver_denoising_pair_20261104/README.md)：重新核对 Cai Fig. 3，以同一已保存实验样本展示含噪 R_k 经 F_theta 得到 F_k，前后使用相同幅度色标；网络改为蓝／浅绿／橙色。既定总览与黑色文本框保持。三格式、图注与两版 PDF 已更新，未运行新实验。

作者随后要求核对流程是否准确；[图 3 流程语义核对](FIGURE3_FLOW_AUDIT_20261104.md)确认主干依赖与正文/实现一致，但列出分类器接线、方差支路、site 框含义、共同方差输出及反馈阻尼五处表达问题。本轮只分析记录，尚未重绘，不将版面核验视为语义核验。

上述五项随后已获作者授权并[全部修正](../checks/receiver_flow_corrected_20261104/README.md)：三格式和两版 PDF 已更新，接线端点及变量/公式对应复核通过。全部 TeX、其他图及既有去噪样本保持；主稿/完整稿仍为 13/14 页，仅第 7 页变化。前一段“尚未重绘”为当时的分析状态。

作者随后指出实现细节与文字过多，图 3 已进一步[精简](../checks/receiver_concise_flow_20261104/README.md)：删除差分文字、扰动表达式、平均操作说明及单独阻尼框，展开图止于原始外信息。保留五项语义修正的核心关系；不再将数值细节逐一入图作为要求。三格式与两版 PDF 已同步，正文及算法保持。

最新[伪代码形式对照与修订](PSEUDOCODE_STYLE_20261104.md)核对 Cai、Shen、Huang 的原算法框，改为逐行编号、缩进和短公式引用。依作者纠正，算法框不突出训练范围外的 Gaussian evidence 兜底；实现未改。

[正文防御性与辩护性说明检查及修订](DEFENSIVE_LANGUAGE_REVIEW_20261104.md)的六处建议已按作者授权完成：精简兜底、自证与重复限定，式 (43) 移至消融对照定义处，停止条件保留正文原则和既有实现细节。两版 PDF 已更新，仍为 13/14 页、46 个编号公式与 42 篇参考文献。

最新[公式与正文呈现的逐式复查](FORMULA_PRESENTATION_AUDIT_20261104.md)覆盖精简前 51 式，进一步将方差平均/下限、每轮复杂度、SNR、NMSE、AER 改为正文。当前共 46 个编号公式（正文 43＋附录 3），两版仍为 13/14 页。

此前[两项实现设置的文字化修订](IMPLEMENTATION_SETTINGS_PROSE_20261104.md)将 κ 更新和训练协方差采样改为文字，保留全部操作与参数，当时编号公式共 51 个（正文 48＋附录 3）；两版仍为 13/14 页。

作者关于公式是否能与 Cai 一一对应的疑问，见 [精简前 53 式逐项对照](CAI_FORMULA_CORRESPONDENCE_20261104.md)：按期刊版式号区分同类式、必要适配及其他来源，附 7 项针对对应关系的代数核验。此表不要求把已删推导补回论文，也不改算法。

进一步的[阻尼合理性与非 Cai 公式原型核查](DAMPING_AND_FORMULA_PROTOTYPES_20261104.md)确认递归阻尼的文献依据和代码一致性，并补查到 NeurIPS 2024 的直接矩阵预条件原型；明确区分已有关系与本文的局部方差尺度、训练采样及相位搜索设置。

最新[推导呈现精简记录](DERIVATION_PRESENTATION_20261104.md)将单独的 CPP 延拓式及信道展开移至[内部推导](derivations/afdm_channel_model.tex)，正文保留波形、有效信道与跨帧关系；导数方差保留恒等式和最终估计式，预条件保留实现定义。`main.tex` / `main.pdf` 为不含评估协议附录的 13 页版本；`main_full.tex` / `main_full.pdf` 为包含评估协议附录 B 的 14 页版本，二者共享正文并已包含结论。原评估协议附录 C 仅因信道附录移出而顺延为 B，内容保持。此前[第三至六章压缩记录](../checks/initial_submission_compression_20261103/REVISION_NOTES.md)、[第六章总体趋势分析修订](../checks/ch6_trend_summary_20261103/REVISION_NOTES.md)和[更早删减记录](../checks/content_trim_cai_20261103/REVISION_NOTES.md)保留为历史依据。

第 I–VI 章、附录 A–C 和方法图的符号来源、重名及定义检查见 [2026-11-03 全文符号核查](NOTATION_AUDIT_20261103.md)。该报告保留修改前证据；当前按作者要求只保留重名修复与正文中的必要定义，已撤回上一轮新增符号表和扩写的 Notation 段，详见[当前实施及核验记录](../checks/notation_inline_only_20261103/REVISION_NOTES.md)。

第二章变量的英文名称、完整搭配与尚未核得的项目，见[逐项核查清单](VARIABLE_NAMES_AUDIT.md)。字母是否相同不作为英文名称的通过条件。

第二章全部具名对象、技术表达、小节标题及具名算子的扩大核查，见[全部名称出处清单](CHAPTER_II_NAMES_AUDIT.md)。该表区分当前 PDF 已引用、仅书目库已有、本文适配和书目外补查，并补充修正上一轮的 pilot vector、activity states、antenna index 等出处状态。

上述清单特别列出的 13 项已按作者要求处理，当前替换与数学一致性说明见[第二章具名表达替换记录](../checks/ch2_named_expressions_revision_20261101/REVISION_NOTES.md)；旧清单保留为修改前证据，不继续作为待处理列表。

| 文档 | 内容 |
|---|---|
| [ACTIVITY_DETECTOR_REVIEW_20261024.md](ACTIVITY_DETECTOR_REVIEW_20261024.md) | 当前 GFRA 实验的活动检测判据核查 |
| [ATTRIBUTION.md](ATTRIBUTION.md) | 方法来源与许可 |
| [BASELINE_ACTIVITY_READOUT.md](BASELINE_ACTIVITY_READOUT.md) | 活动判决的原文与实现 |
| [BASELINE_BUDGET_REVIEW_20261024.md](BASELINE_BUDGET_REVIEW_20261024.md) | 四个 baseline 的 AER 曲线：预算、信道重构与活动判据复核 |
| [BASELINE_GFRA_AUDIT_20261023.md](BASELINE_GFRA_AUDIT_20261023.md) | 四个 baseline 的 GFRA 文献、实现与判决核验 |
| [BASELINE_GRID.md](BASELINE_GRID.md) | 当前整数时延/Doppler 字典 |
| [BASELINE_NOISE.md](BASELINE_NOISE.md) | 五个 baseline 的噪声估计 |
| [BASELINE_PHASE.md](BASELINE_PHASE.md) | 两个 SBL 基线的后验相位更新 |
| [BASELINES.md](BASELINES.md) | 五个主线基线的实现与来源 |
| [C_STMP_ANALYTIC_ACTIVITY_20261025.md](C_STMP_ANALYTIC_ACTIVITY_20261025.md) | C-STMP 的解析活动概率：独立诊断候选 |
| [C_STMP_COLUMN_MESSAGES_20261025.md](C_STMP_COLUMN_MESSAGES_20261025.md) | C-STMP：保留每用户输入列协方差的 Gaussian 消息推导与验证 |
| [C_STMP_COMPONENT_DIAGNOSTIC_20261025.md](C_STMP_COMPONENT_DIAGNOSTIC_20261025.md) | C-STMP 查询统计与网络条件：逐模块诊断 |
| [C_STMP_DERIVATION_20261024.md](C_STMP_DERIVATION_20261024.md) | C-STMP：条件均值、方差与活动检测接口 |
| [C_STMP_QUERY_POWER_REPAIR_20261025.md](C_STMP_QUERY_POWER_REPAIR_20261025.md) | C-STMP 查询噪声功率修正：独立候选 |
| [CODE_GUIDE.md](CODE_GUIDE.md) | 当前代码导读 |
| [COLORED_COVARIANCE_RELATIVE_CHECK_20261024.md](COLORED_COVARIANCE_RELATIVE_CHECK_20261024.md) | 有色协方差是否比标量白噪声更合理 |
| [COLORED_DENOISING_EXPERIMENT_20261025.md](COLORED_DENOISING_EXPERIMENT_20261025.md) | 2026-10-25 有色噪声独立去噪与接收机输入比较 |
| [COLORED_PRECONDITIONED_TRAINING_20261024.md](COLORED_PRECONDITIONED_TRAINING_20261024.md) | 有色噪声一阶网络：矩阵预条件训练 |
| [COLORED_SCORE_ARCHITECTURE_REVIEW_20261024.md](COLORED_SCORE_ARCHITECTURE_REVIEW_20261024.md) | 有色噪声一阶网络：结构是否需要更换 |
| [COLORED_SCORE_TRAINING_20261024.md](COLORED_SCORE_TRAINING_20261024.md) | 单一有色 Gaussian 噪声的 score 训练候选 |
| [CURRENT_STAGE.md](CURRENT_STAGE.md) | 当前阶段 |
| [EXPERIMENT_PROTOCOL.md](EXPERIMENT_PROTOCOL.md) | 当前实验协议 |
| [MESSAGE_AWGN_CONDITIONS_20261022.md](MESSAGE_AWGN_CONDITIONS_20261022.md) | 不同工况下的消息误差与 AWGN 假设 |
| [OFFGRID_BASELINES.md](OFFGRID_BASELINES.md) | Off-grid SBL |
| [PHASE_ESTIMATION_PROGRESS_20261022.md](PHASE_ESTIMATION_PROGRESS_20261022.md) | 相位估计候选：失败分支、训练样本匹配与独立验证 |
| [PHASE_ESTIMATION_REVIEW_20261021.md](PHASE_ESTIMATION_REVIEW_20261021.md) | AFDM 相位估计的改进方向 |
| [PHASE_MESSAGE_GEM.md](PHASE_MESSAGE_GEM.md) | 各向同性高斯消息下的一次广义EM参数更新 |
| [RESEARCH.md](RESEARCH.md) | 独立研究入口 |
| [SHEN_PHASE_IMPLEMENTATION_20261021.md](SHEN_PHASE_IMPLEMENTATION_20261021.md) | Shen 相位更新的 AFDM 候选实现与验证协议 |
| [STMP_COVARIANCE_GROUPING_20261024.md](STMP_COVARIANCE_GROUPING_20261024.md) | 更粗的 GEC 分组：首轮误差、模式响应与天线相关 |
| [STMP_COVARIANCE_REPRESENTATION_20261024.md](STMP_COVARIANCE_REPRESENTATION_20261024.md) | D-GEC 候选中的 C：维度、公开坐标基与精度递推 |
| [STMP_COVARIANCE_VALIDATION_20261024.md](STMP_COVARIANCE_VALIDATION_20261024.md) | C 候选验证：输入列基的解释能力与逐模式外信息代价 |
| [STMP_LINEAR_COVARIANCE_INTERFACE_20261024.md](STMP_LINEAR_COVARIANCE_INTERFACE_20261024.md) | 当前线性观测模块能否给出去噪协方差 |
| [STMP_MESSAGE_AWGN_REVIEW_20261024.md](STMP_MESSAGE_AWGN_REVIEW_20261024.md) | STMP 迭代消息失配的已有研究与改进方向 |
| [STMP_PAPER_READING_NOTES_20261024.md](STMP_PAPER_READING_NOTES_20261024.md) | STMP 论文下载后的阅读与可借鉴环节 |
| [STMP_PHASE.md](STMP_PHASE.md) | STMP 相位更新：实现、验证和边界 |
| [SYSTEM_MODEL.md](SYSTEM_MODEL.md) | 观测模型、空间结构与实验信息 |
| [TERMINOLOGY.md](TERMINOLOGY.md) | 当前术语与来源 |
| [THEORY.md](THEORY.md) | 完整信道 score 与消息传递 |
| [TRAINING.md](TRAINING.md) | 当前算法训练 |
| [WORKSPACE_INDEX.md](WORKSPACE_INDEX.md) | 工作区索引 |
| [WRITING_GUIDE.md](WRITING_GUIDE.md) | 用词出处、原段原句适配、自然表达与后续章节修订检查 |
