# GP-MP：当前算法稿（正文修订中）

2026-11-07：主 SNR 图 6 的 GP-MP／GP-MP-EP 已采用完整核验的白噪声网络结果，每档 1000 场景。白／有色估计相位最大 NMSE 差约 0.104 dB、AER 差 0.03 个百分点。两版仍为 13／14 页，数据状态和对应数值已同步；图 4、7–10 的替换仍待后续完成，当前为工作稿。[采用与核验](checks/white_snr_adopted_20261107/README.md)。以下带日期记录保留各自历史状态。

2026-11-06：已采用作者手动修订的最新摘要，首句明确设备不进行时间与频率预补偿；中英文摘要同步。英文 219 词，两版已编译检查，仍为 13／14 页。[采用与核验](checks/abstract_author_revision_20261106/README.md)。

2026-11-06：已按作者要求整理全文公式分组，核心独立更新分别编号，辅助定义移入邻近正文；编号由 45 个调整为 59 个。正文、算法和图 3 引用同步，主稿 13 页、完整稿 14 页，数学内容与实验表数据保持。[修订与编号对应](checks/equation_numbering_revision_20261106/README.md)。

2026-11-06：按作者要求精简全文，删除重复辩解、核验过程叙述和变量维度的反复说明，约减少 410 个英文词项。主稿 13 页、完整稿 14 页，42 条参考文献；公式、算法和图表数据保持。[精简与核验](checks/conciseness_revision_20261106/README.md)。以下日期记录保留各轮页数快照。

2026-11-06：按作者要求，将第六章与完整稿附录统一为白高斯噪声训练、协方差 $vI$ 和标量预条件，删除相关协方差采样与矩阵推广的旧描述。两版当时为 13/15 页；不再引用矩阵推广文献后，实际参考文献为 42 篇。图 5 与表 III 已使用白噪声网络；图 4、6–10 的 GP-MP 曲线仍待替换，第六章开头集中标明工作稿数据状态。[修订与核验](checks/white_noise_wording_20261106/README.md)。

2026-11-05：已采用作者确认的第二点表述，按“学习先验 → Tweedie 公式构造去噪器 → 条件均值导数估计方差 → 训练依赖与开销”组织，中英文摘要与引言同步。两版已编译检查，当前为 13/15 页。[采用与核验记录](checks/second_contribution_adopted_20261105/README.md)。

2026-11-05：按作者反馈恢复摘要与引言第二点的贡献逻辑，突出学习信道先验、同一去噪器的信道估计与不确定性量化，以及其为消息传递提供统计量的作用；第一、第三点保持，两版仍为 13/14 页。[本轮修改与依据](checks/second_contribution_restore_20261105/README.md)。

2026-11-05：相位估计并入第五章 V-B，搜索参数归入第六章，主稿取消独立相位附录；完整稿的评估协议附录顺延为 A。[实施记录](checks/phase_into_ch5_20261105/README.md)。

2026-11-05：图例及正文方法名称统一为 **GP-MP**，估计相位版为 **GP-MP-EP**；两版 PDF 同步。最新名称覆盖以下历史状态说明。

2026-11-05：同精度、同场景白/有色训练比较显示各档 NMSE 相差不超过 0.081 dB，支持先调整论文论述。已移除摘要、引言和方法章节中对有色训练收益的依赖，补充条件均值导数与不确定性估计的来源；预条件仅保留为实现设置。[配对结果与本轮修订](checks/white_mainline_revision_20261105/README.md)。以下带日期记录保留各自历史含义。

2026-11-04：EP 的含义已集中到第 9 页比较算法中的 CGP-MP 条目，删除图注中的重复相位说明；两版 PDF 保持 13/15 页。[实施记录](checks/ep_definition_placement_20261104/README.md)。

2026-11-04 已将完整相位估计实验加入主 SNR 图（图 6，第 11 页）：**CGP-MP-EP** 用红色虚线三角，六档 SNR 各 1000 个配对场景；其余六条曲线不变。第五章、相位附录及评估说明同步为一次估计后固定相位，两版 PDF 已更新，保持 13/15 页、44 篇参考文献。[结果与核验](checks/snr_estimated_phase_1000_20261104/README.md)。

2026-11-04 作者确认将 GP-MP-C 简化为 **CGP-MP**；正文、图例和两版 PDF 已同步，C 仍表示有色高斯噪声训练。[本轮核验](checks/algorithm_name_cgp_mp_20261104/README.md)。

2026-11-04：[十幅论文图统一生成与清理](checks/figure_consolidation_20261104/README.md)已完成；现行入口及图号见[图目录](figures/README.md)。正式图和两版论文 PDF 保持，数据与版面复现通过。

[论文源码](main.tex) · [main：不含评估协议附录](main.pdf) · [main_full：含评估协议附录](main_full.pdf) · [中文摘要](sections/00_abstract_zh.md) · [研究文档](docs/README.md) · [术语出处](docs/TERMINOLOGY.md)

再次预审或讨论已有问题，先读[预审问题与讨论决定](docs/REVIEW_DECISIONS.md)。其中记录 C1、M1–M5 的最新状态、作者已回答的事项及结果证据；先查记录，不重复要求作者解释已核实内容。

后续章节的写作与修订参照[用词出处与段落修订规范](docs/WRITING_GUIDE.md)，其中记录了第二章的修改经验、出处核验方法和七项后续修正实例。

当前正文以 **GP-MP** 表示生成式先验辅助消息传递接收机，方法推导、训练设置与附录均采用白高斯噪声形式。**STMP** 仍为含学习密度比活动更新的三网络适配基线。图 5 与表 III 使用白噪声去噪器及配套分类器；图 4、6–10 的 GP-MP 曲线暂保留历史权重结果，不能据此声称全部白噪声实验已入稿。统一关闭 TF32 的已知相位 SNR 批次已保存 6000/6000 份结果并通过其完成核验，但本轮只修改表述，未替换该图或切换 FINAL.json、冻结资产。以下带日期的旧状态按记录时点理解。

## 内容与位置

| 内容 | 位置 |
|---|---|
| 不含评估协议附录的编译入口与阅读稿 | `main.tex`、`main.pdf`（当前 13 页，42 篇参考文献） |
| 包含评估协议附录 A 的完整版本 | `main_full.tex`、`main_full.pdf`（当前 14 页） |
| 正文、中英文材料与附录 | `sections/` |
| 七幅实验图与三幅方法示意图 | [图文件及各格式](figures/README.md) |
| 参考文献 | [references.bib](references.bib) |
| 推导、训练、诊断与术语 | [docs/](docs/README.md) |
| 修订依据、核验与历史源文件 | `checks/` |

`main.tex` 编入第 I–VII 章和参考文献，不含附录；相位估计已并入第五章 V-B，搜索参数位于第六章 VI-A4。`main_full.tex` 复用同一正文并启用评估协议附录 A。原相位附录及详细推导保存在[内部文档](docs/derivations/phase_estimation.md)，原信道推导保存在[内部推导记录](docs/derivations/afdm_channel_model.tex)。七幅实验图为去噪、收敛、SNR、导频帧数、用户数、活动概率及跨信道；其中 SNR 和导频图展示 NMSE 与 AER，其余接收机比较图展示 NMSE。原始数据及未展示指标仍保留在[结果目录](../../result/README.md)。

## 最近修订依据

- [STMP 基线与 GP-MP 白噪声消融命名](checks/stmp_baseline_white_ablation_20261104/README.md)（2026-11-04）：旧三网络对照改称 STMP，GP-MP 专指当前方法的同结构白噪声消融。七幅实验图的 547 个点保持；引言补 Wei–Yuan 动机引用，两版为 13/15 页、44 篇参考文献。新白噪声消融尚未形成正式评估曲线。

- [第六章图序、图例及代表性结果](checks/ch6_results_order_style_20261104/README.md)（2026-11-04）：导频实验直接接主 SNR，图 7/8/9 依次为导频、设备数、活动概率；跨信道按 A/B/C/D 排列，去噪图例采用统一样式。主 SNR 补充 0 dB 下 1.6 dB 的代表性 NMSE 收益，两幅图的 198 点保持，两版仍为 13/15 页。原单场景收敛图保持，多场景方案见同目录后续建议。

- [第六章按 Cai 重组并精简结果分析](checks/ch6_cai_revision_20261104/README.md)（2026-11-04）：设置归为四组，基线分点加粗，新增网络表；结果以连续图引导段落组织，按作者意见删除过细的错误类别拆解及重复说明。原公式、原图表数据保持，22 项数据核对通过；两版为 13/15 页，图 10 已排在结论之前。以下旧记录中的页数和状态为当时快照。

- [第六、七章九项修订完成](checks/chapters_vi_vii_language_selected_20261104/README.md)（2026-11-04）：落实获批的语言修改、结论比较对象澄清和矩阵预条件直接补引；两版仍为 13/14 页，参考文献增至 43 篇，公式与图表保持。

- [恢复六算法主 SNR 图并继续第六章分析](checks/snr_six_methods_20261104/README.md)（2026-11-04）：原每档 1000 场景六方法数据恢复，旧估计相位曲线暂时撤出，样本数、结果说明及完整稿评估协议同步；新实验完成后再补入。两版仍为 13/14 页。[第六章分析与候选表](docs/CHAPTER_VI_SIX_METHOD_REVIEW_20261104.md)供作者选择，普通语言候选未实施。

- [名称简化为 GP-MP-C](checks/algorithm_name_c_20261104/REVISION_NOTES.md)（2026-11-04）：按作者确认将 CCD 后缀改为 C；引言补 GP-MP 的含义，第五章说明 C 表示有色高斯噪声训练。正文、算法标题、六幅实验图例和两版 PDF 同步，实验数据、数学表达式和算法步骤保持；两版仍为 13/14 页。

- [长 CPP、导数方差及预条件的呈现精简](docs/DERIVATION_PRESENTATION_20261104.md)（2026-11-04）：按作者确认移出单独的 CPP 延拓式及信道展开附录，压缩导数恒等式引出过程；矩阵预条件保留在网络实现设置。编号公式由 57 个减为 53 个，其余编号公式运算及全部图文件保持；两版编译与目视检查通过，当前为 13/14 页。

- [变量形式修正与 57 个公式出处复核](docs/FORMULA_PROVENANCE_20261104.md)（2026-11-04）：按作者授权统一设备矩阵、条件均值和 site 方差记号，删除重复索引及辅助后验层，修复 Y_0 重名；Fig.2/3 同步。32 项代数检查通过，两版仍为 13/15 页；七幅实验图、实验数值及引言保持。

- [预审讨论记录与分 SNR 消融报告](docs/REVIEW_DECISIONS.md)（2026-11-03）：记录已撤回、待处理和进行中事项，保留 C1 单场景影响复算及 M2/M3 历史证据入口。M5 已更新表 II，分 SNR 展示 AER 与迭代上限比例；两版 PDF 保持 13/15 页，[核验记录](checks/review_followup_20261103/VALIDATION.json)。本次建立讨论记录未继续修改论文正文或运行实验。

- [分段修订后重新编译](checks/recompile_20261103/README.md)（2026-11-03）：作者恢复编译后，已更新 main（13页）和 main_full（15页），两版均包含最新第3–5章修订、保留42篇参考文献。引用及版面检查通过；源码未改动。下列“暂不编译”说明均为此前历史状态。

- [第3–5章分段与措辞修订](checks/paragraph_revision_20261103/REVISION_NOTES.md)（2026-11-03）：按作者确认的分段判断，将47个正文段整理为33段，保留新增技术任务，合并式后解释及尾句，重新组织归一化、阻尼与复杂度说明。[逐段来源](checks/paragraph_revision_20261103/PARAGRAPH_MAP.md)记录保留差异。公式与算法运算保持；Algorithm 1 仅删去 SVD 前的 thin 修饰。摘要未重新生成。本轮不编译，当前 PDF 不包含这些源码修订。

- [第3–5章与 Cai 的逐段对应核查](checks/cai_paragraph_alignment_20261103/PARAGRAPH_AUDIT.md)（2026-11-03）：记录修订前47个正文段与 Cai 的28个母段，列出拆段、合并、跨章搬移及本文新增内容。当时只完成核查；随后按上条确认的分段判断实施，未采用全部机械合并建议。PDF 保留停止编译指令前的版本。

- [进一步逐词与操作对象修订](checks/wording_pass_20261103/REVISION_NOTES.md)（2026-11-03）：修正 mean function、complex mean map、Gaussian covariance、noise estimate 等搭配和对象；修订记录区分已编译版本与随后停止编译时的源码状态。此轮措辞修订不代表已满足后一项段落骨架要求。

- [完整搭配核查与正文压缩](checks/prose_terminology_20261103/REVISION_NOTES.md)（2026-11-03）：按完整表达及使用位置改写 moments、activity evidence、new-message weight 等；完整停止设置移至附录 C-G，接收机图同步具体统计量名称。当前 main 13 页、main_full 15 页；来源与本文命名分别登记。

- [正式出版版本核对与预印本条目清理](checks/published_references_20261103/REVISION_NOTES.md)（2026-11-03）：4 篇更新为正式期刊或会议版本；删除 Wei 预印本条目，按作者要求保留引言对应论述，仅去掉引用标号及悬空介词。当前 42 篇参考文献，main 13 页、main_full 15 页。
- [参考文献补至 43 篇并压缩到 13 页](checks/references_compression_20261103/REVISION_NOTES.md)（2026-11-03）：原有 35 篇保留，补充 8 篇有明确支撑位置的文献，规范期刊缩写与在线链接，补全出版信息；第五、六章精简约 315 个源码英文词。摘要、引言原文、第二章、结论、附录及全部编号数学环境保持。`main` 为 13 页，`main_full` 为 15 页。

- [结论编入两版阅读稿](checks/conclusion_integration_20261103/REVISION_NOTES.md)（2026-11-03）：按作者要求启用第 VII 章结论，保持既有结论文字；引言末尾仅补章节导航句。两版已编译及检查，结论均位于第 12 页，总页数仍为 14／15 页。

- [补充网络结构与结论构思](checks/network_structure_conclusion_20261103/REVISION_NOTES.md)（2026-11-03）：VI-A2 按已绑定权重与实现补充去噪器、分类器的阶段、通道、卷积、条件输入与输出层；网络尺寸经 CPU 合成输入核对。结论对照 Cai、Shen、Wei、Huang，并按作者要求与摘要、引言的三点贡献对应，先保存草稿。摘要、引言、公式、实验结果和附录未改；网络补充后 main 为 14 页，main_full 为 15 页。

- [第三至六章与附录 A/B 压缩、双版本命名](checks/initial_submission_compression_20261103/REVISION_NOTES.md)（2026-11-03）：噪声估计移至 V-B，AFDM/OTFS 比较精简为 II-B 和 V-C 的短段，A/B 分别保留相位估计和信道矩阵推导；第三至六章说明文字约减少 19%。摘要、引言、实验数值、图文件和附录 C 保持。含 C 完整稿从 16 页降至 15 页；不含 C 的 `main` 为 13 页，包含 C 的 `main_full` 为 15 页。

- [第六章改为总体趋势分析](checks/ch6_trend_summary_20261103/REVISION_NOTES.md)（2026-11-03）：对照 Cai、Shen 后，按作者要求将八处结果解释收紧为总体趋势和主要对比，删除逐点报数及回落、交叉的专门讨论；所有图表、设置和其他章节保持，完整稿由 17 页降为 16 页。

- [正文保守删减与第六章分析精简](checks/content_trim_cai_20261103/REVISION_NOTES.md)（2026-11-03）：摘要、引言、第二章和附录保持；第三至五章只删重复说明，第六章 B–E 参照 Cai 的分析粒度减少约四分之一文字。公式、图表、实验设置及不利结果保留，完整阅读稿由 18 页降为 17 页，附录 C 暂未删除。

- [撤回符号表，仅保留重名修复与正文定义](checks/notation_inline_only_20261103/REVISION_NOTES.md)（2026-11-03）：按作者要求删除新增符号表，恢复之前的简短 Notation 段，必要说明在首次使用处补充；公式、算法、图和实验内容保持。

- [参照 Cai、Shen 统一符号](checks/notation_cai_shen_20261103/REVISION_NOTES.md)（2026-11-03）：增加常用符号表和字体约定，区分跨章重名，补首次定义、索引及展开顺序；正文、Algorithm 1、Fig. 3 同步。71 个公式块经记号映射核对一致，七幅实验图和结果数字保持，完整阅读稿为 18 页。

- [OTFS 对比段落与第二章风格统一](checks/otfs_prose_alignment_20261103/README.md)（2026-11-03）：II-B 末尾改为围绕信道矩阵与帧时长的一段简短说明；对照表、各轴解释和数值例子集中到附录 B，保持原模型与比较条件。

- [OTFS 对比并入传输方案](checks/otfs_into_transmission_20261103/README.md)（2026-11-03）：取消第二章独立的 OTFS 对比小节，将说明及对照表接在 II-B 的跨帧相位与有效导频之后；问题表述恢复为 II-C，附录引用同步。

- [红、蓝、绿提高饱和度](checks/saturated_rgb_palette_20261103/README.md)（2026-11-03）：采用参考图的纯红、鲜蓝与饱和深青，并为其他基线配以相近深绿；六幅接收机比较图与阅读稿同步，505 个绘图点及线型、标记保持。

- [AFDM–OTFS 对照与实验说明完善](checks/afdm_otfs_comparison_20261103/REVISION_NOTES.md)（2026-11-03）：第二章新增同带宽、同时长的信道表示对照；附录 B 补充资源匹配、共同多普勒下的 OTFS 分解与调制运算推导。引言同步收紧普遍复杂度优势的表述，第五章接入调制成本分析。正文按白噪声／有色噪声训练区分接收机，其他配置差异集中至附录 C；保留 AER 消融表，并在附录补充原始错误计数与未收敛统计。未运行训练或新增接收机实验。

- [基线配色改为相近暗色系](checks/baseline_muted_palette_20261103/README.md)（2026-11-03）：依据作者提供的参考图，保留 GP 系列红色与 Off-grid SBL 蓝色，另外三个基线统一为低饱和度的暗青灰、灰绿和深绿色；替代上一轮高饱和配色，曲线数据与线型保持。

- [基线曲线配色调整](checks/baseline_colors_20261103/README.md)（2026-11-03）：Off-grid SBL 使用原 STMP 的蓝色；GNN-ASPL、GAMP-SBL、SOMP 分别改为更高饱和度的紫色、橙色和绿色。五幅包含这些基线的比较图及阅读稿同步，三条 GP 系列曲线的红色、线型与标记保持。

- [算法名称与三条曲线样式统一](checks/algorithm_name_simplify_20261103/REVISION_NOTES.md)（2026-11-03）：主算法去掉 DRE 后缀并统一为 GP-MP-CCD；基线及估计相位版本分别为 GP-MP、GP-MP-CCD-EP。三者均为红色，依次使用虚线圆点、实线方块、虚线三角。正文、Algorithm 1、附录及六幅比较图同步；密度比估计仍是接收机组成部分。

- [因子图增加彩色分区框](checks/factor_graph_region_frames_20261103/README.md)（2026-11-03）：参照 Shen Fig. 2，用蓝色和铜色虚线框分别标出 Linear estimation 与 Joint denoising，标题同步加粗着色；更新矢量图、PNG 和第 4 页正文。

- [因子图改为设备块变量表示](checks/factor_graph_device_blocks_20261103/README.md)（2026-11-03）：删除矩阵展开与逐元素索引，直接连接观测因子、设备块及信道和活动先验；同步更新图注、三种图格式和第 4 页正文。后验分解、公式及算法保持。

- [方法图线宽、直线与平行关系修正](checks/method_figures_line_geometry_20261103/README.md)（2026-11-03）：多帧边框和分隔线统一描边，卫星到 UPA 改为直线，因子图两组斜线分别平行。两张单栏图及阅读稿已更新；本轮未改正文源码。

- [第六章精简重复限定与防御性说明](checks/ch6_prose_streamline_20261103/REVISION_NOTES.md)（2026-11-03）：删除运行时间免责声明、实验范围与附录提示的重复说明；保留相位条件、样本范围、能量约定和不利结果，公式、表格数值及图文件保持。

- [系统图对齐与因子图交叉排列](checks/method_figures_alignment_crossing_20261103/README.md)（2026-11-03）：修正终端圆点与圆盘边界、卫星到 UPA 的连线；因子图恢复 Cai Fig. 2 的上方信道、下方活动变量排列。两图保持单栏，更新图文件及第 3、4 页正文；变量依赖、公式与算法保持。

- [第六章实验组织与分析修订](checks/ch6_revision_20261103/REVISION_NOTES.md)（2026-11-03）：按去噪、密度比估计、整机性能、跨信道展开；新增仅报告 AER 的活动证据表，将估计相位曲线并入 SNR 主图，统一每档 500 场景的图文数值，并同步第五章与附录的相位更新说明。保留工作区同时更新的方法图布局；未启动实验或训练。

- [系统图、因子图改为单栏，接收机图进一步收紧](checks/method_figures_column_layout_20261103/README.md)（2026-11-03）：前两图按 88.9 mm 原生宽度重排，分别位于第 3、4 页；接收机图保留双栏并压缩支路与反馈线，位于第 8 页。PDF、SVG、600 dpi PNG 及阅读稿均已更新；本次编译包含工作区同时更新的实验章节与附录，完整稿为 17 页。

- [三张方法图编入正文](checks/method_figures_integration_20261103/README.md)（2026-11-03）：系统图、因子图和学习接收机图依次为 Fig. 1–3，位于阅读稿第 3、5、8 页；因子图替换第三章原框图。当前阅读稿已更新为 15 页，公式、Algorithm 1 及图文件保持。

- [系统图精简文字与公式](checks/method_system_minimal_20261103/README.md)（2026-11-03）：对照 Cai、Shen 的系统图，删除推导等式、解释性长句和重复标签，收紧场景间距；只保留识别对象、状态和帧结构所需标注。

- [系统图改为统一接入场景](checks/method_system_scene_20261103/README.md)（2026-11-03）：以地面设备到卫星的上行链路为主，多帧导频作为设备局部展开，UPA 作为卫星局部展开；更新系统图 PDF、SVG、PNG。因子图、接收机图和阅读稿沿用上一轮。

- [三张方法图压缩布局并明确主次](checks/method_figures_compact_20261103/README.md)（2026-11-03）：去掉接收机上下重复总览，缩短支路，集中联合矩的汇合；压缩系统图与因子图，调整相邻标签间距。当前图文件以本轮为准，提供 PDF、SVG 和 600 dpi PNG；正文及阅读稿未改动。

- [三张方法图进一步调整构图](checks/method_figures_distinct_layout_20261103/README.md)（2026-11-03）：在原图改绘基础上重新组织连续 AFDM 帧、按设备成对的因子分支，以及上下两层的接收机图；保留简洁论文图风格和改绘出处。当前图文件以本轮为准，提供 PDF、SVG、600 dpi PNG 及改前改后对照。

- [三张方法图按原图改绘](checks/method_figures_source_adaptation_20261103/README.md)（2026-11-03）：按作者反馈，替换上一版大色块流程图。直接采用 Shen 的卫星与阵列、Cai 的资源格子和因子图、Cai 的网络矢量元素及局部放大构图，再替换当前模型的符号和计算支路。当前 [PDF / SVG / PNG](figures/README.md) 与[图注片段](checks/method_figures_source_adaptation_20261103/figure_inserts.tex)以本轮为准，旧图已归档；正文及阅读稿未改动。

- [三张方法图与矢量导出](checks/method_figures_20261103/README.md)（2026-11-03）：按当前模型绘制系统与多帧 AFDM 传输、后验因子图与消息交换、学习接收机总图，统一配色并提供 PDF、SVG、600 dpi PNG。[图文件](figures/README.md)及[插入片段](checks/method_figures_20261103/figure_inserts.tex)已备好，正文和阅读稿尚未插图。

- [第五章逐句表达修订与补图建议](checks/ch5_sentence_revision_figures_20261102/REVISION_NOTES.md)：逐句核对 51 个原句单元，调整 20 个、保留 31 个，改善学习矩与消息传递、方差更新及复杂度各项之间的衔接。10 个编号公式、Algorithm 1、引文及第三、四章源码保持；[逐句对照](checks/ch5_sentence_revision_figures_20261102/SENTENCE_REVIEW.md)对应当前第五章。[补图方案](checks/ch5_sentence_revision_figures_20261102/FIGURE_PLAN.md)依据 Cai、Shen、Ding、Huang 原图，优先建议系统与多帧传输图、学习接收机总图；尚未插入新图或启动实验。

- [第五章按第三、四章标准精简表达](checks/ch5_prose_revision_20261102/REVISION_NOTES.md)：删除 site 一致性、方差裁剪正值性和计算开销的重复说明，将算法汇总前的泛化描述改为估计量与外信息之间的直接衔接。10 个编号公式、伪代码及更新条件保持；第五章位于阅读稿第 7–8 页。

- [第三、四章删除防御性与重复说明](checks/ch3_ch4_remove_defensive_20261102/REVISION_NOTES.md)：删除四处、五句话，包括与 Cai 简化条件的对照、重复最优性及有限差分说明、分类器关系仍成立的补充辩解。25 个编号公式和必要数学条件保持；当前阅读稿已重新编译。

- [第三、四章逐句表达修订](checks/ch3_ch4_sentence_revision_20261102/REVISION_NOTES.md)：保留现有 Cai 论证结构，结合 Shen、Xu、Huang、Ding、Wei 的适用表达逐句审读；119 个句子单元中调整 67 个、保留 52 个。25 个编号公式、章节标题与原有技术引用保持。[逐句前后对照及出处](checks/ch3_ch4_sentence_revision_20261102/SENTENCE_REVIEW.md)为随后删句前的历史快照；当前正文同时参照上条删除记录。

- [第四章的论述顺序与段落衔接](checks/ch4_cai_continuity_20261102/REVISION_NOTES.md)：按后验矩与 score 的联系、一阶 score 学习、条件均值导数求方差、密度比估计活动概率展开。有色训练接在多噪声水平训练之后；方差由本章已有恒等式自然推出。第四章的当前结构以本条为准。

- [第三章通用框架与第四、第五章分工](checks/ch3_general_framework_20261102/REVISION_NOTES.md)：第三章及框图改用线性估计、联合去噪的通用表述；第四章推导后验量的学习方法，第五章定义 MFLE、GPJD 并集中说明共用方差和反馈裁剪。下列第三章对照稿保留为历史版本，当前正文以本条为准。

- [第三章原文对照与独立润色稿](checks/ch3_cai_comparison_polish_20261102/01_comparison_notes.md)：直接提取项目内 Cai v2 第三章，记录 18 处段落、公式对应关系；保存带出处批注的论述稿及独立润色稿。润色稿已用于正文，密度比学习仍留在第四章。

- [第三章按 Cai 的推导顺序重排](checks/ch3_cai_logic_20261102/REVISION_NOTES.md)：先线性估计，再依次推导信道估计、活动后验概率和联合估计与外信息反馈。第三章仅给出贝叶斯推断关系，密度比估计器仍在第四章；本条替代上一轮关于第三章组织的说明。

- [第三至第五章论证结构重写](checks/ch3_ch5_argument_revision_20261102/REVISION_NOTES.md)：按后验推断、后验量学习、完整算法展开；网络与停止设置归入 VI-A，噪声估计细节归入附录 A。原公式与算法行为保留，当前阅读稿为 14 页。

- [附录 A、B、D 内容归位](checks/appendices_restructure_20261031/REVISION_NOTES.md)：噪声估计、波形定义、实现与参数说明并入相应正文；A、B 保留相位估计和信道推导，独立附录 D 取消。C、摘要和引言保持原文，阅读稿仍为 13 页。
- [恢复原引言](checks/restore_introduction_20261031/REVISION_NOTES.md)：按作者要求恢复本轮压缩前、已完成术语统一的引言，其余章节保留压缩版；当前阅读稿为 13 页。
- [全文篇幅压缩](checks/compress_20261030/REVISION_NOTES.md)：从 15 页压缩至 12 页，保留全部公式、图表和四个附录，字号与图幅不变。
- [全篇术语统一](checks/full_terminology_revision_20261030/REVISION_NOTES.md)：正文、表格与三幅图的用词修订，补充 proper complex Gaussian 出处；按作者要求保留常见及已有算法缩写。
- [评估过程说明集中至附录 C](checks/protocol_appendix_only_20261030/REVISION_NOTES.md)：当前正文与图注的评估披露安排。
- [第二至第六章精简](checks/prose_streamline_20261030/REVISION_NOTES.md)：实现细节集中至附录 D。
- [实验分析修订](checks/experiment_analysis_20261030/REVISION_NOTES.md)：曲线、数值及论证核查。
- [指标展示与图源核对](checks/aer_selection_20261030/SOURCE_AUDIT.md)、[算法名称与六图更新](checks/algorithm_name_20261030/REVISION_NOTES.md)。

此前所有修订说明完整保存在[历史说明](../../archive/project_cleanup_20261030/C_STMP_HISTORY.md)，其中页码、图源、阶段状态及“暂不编译”等表述属于对应历史时点。

## 编译与文件约定

本目录保存本稿的正文、图片和参考文献；可在包含 IEEEtran 的 LaTeX 环境中运行 `latexmk -pdf main.tex`。完整阅读稿始终更新 `main.pdf`，不新增带日期或版本号的完整 PDF 副本。

论文采用图统一保存在 `figures/`。重绘及数据核验入口随 `checks/` 中对应记录维护，不能用历史结果目录内已退役的导出图替代。临时预览和旧编译日志已登记于[本次整理映射](../../archive/project_cleanup_20261030/MAPPING.json)，正文、七幅图和阅读 PDF 均未由此次整理改动。

旧论文布局见[2026-10-26 映射](../../archive/paper_layout_20261026/MAPPING.json)，共享文献见[参考资料](../../reference/README.md)。
