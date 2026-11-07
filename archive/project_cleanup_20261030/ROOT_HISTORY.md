> 整理前说明的历史阅读版：正文内容保留，仅调整相对链接；原字节副本见 `before/README.md`。旧状态及已退役图源不代表当前版本。

# AFDM-GFRA

**2026-10-30 新选定相位版本的SNR每档500场景已启动。** 六档 −4/−2/0/2/4/6 dB 各用场景0–499，共3000份；复用25份经重评分核验的同版本结果，新增2975次推断，首份通过后4路GPU并发。沿用已选定的物理初始化、20/20检查和5%完整周期停止，独立E盘输出；与既有旧相位和已知相位各3000份配对，结束后自动重评分、汇总及独立出图。13个开发重叠场景全部保留并另报剔除后的487场景统计。无训练，不恢复旧暂停队列，不改冻结主线。见[本批说明](../../result/snr_comparison/data/c_stmp_phase_selected_500_20261030/README.md)、[实时状态](../../result/snr_comparison/data/c_stmp_phase_selected_500_20261030/STATUS.json)。

**2026-10-30 相位版本选择及预留验证完成。** 推荐物理初始化、20/20检查、5%完整周期停止、取消局部分类器相位替换的独立版本。60对预留输入的检测错误6→5、上限数2→0、平均迭代133.33→111.67，NMSE −12.065527→−12.080371 dB，满足全部预定条件；逐例退化与统计局限完整保留。新增254次推断、执行错误0，旧资产8431份哈希不变，无训练，旧批次未恢复、冻结主线未改。见[推荐配置记录](../../result/candidates/c_stmp_phase_selection_20261030/RECOMMENDED.json)、[完整说明](../../paper/C-STMP/docs/C_STMP_PHASE_SELECTION_20261030.md)和[完成核验](../../result/candidates/c_stmp_phase_selection_20261030/COMPLETION.json)。

**2026-10-30 用户暂停相位实验以讨论调度。** 已停止派发并保存全部6份在途结果，最终4169/6000，57份达到迭代上限，执行失败0；父进程及6个工作进程已退出。剩余1831份暂不运行，未经用户后续指示不恢复，不改初始化、算法参数或权重。见[暂停核验](../../result/snr_comparison/data/c_stmp_ablation_1000_20261028/phase_only_20261029/pause_20261030_002556/VALIDATION.json)。下方接续说明为此前运行安排。

**2026-10-29 用户调整消融范围：高斯活动证据停止，两项高斯消融不单独出图。** 已安全保存2128份活动证据结果；纯高斯先验6000份保留。估计相位从3783份结果核验接续，仅补剩余2217份。旧三项完成后统一出图的安排由本次范围更新替代，见[仅相位接续](../../result/snr_comparison/data/c_stmp_ablation_1000_20261028/phase_only_20261029/README.md)。

**2026-10-28 23:36 消融按用户要求充分使用5080。** 已保存并重新核验73份结果，改为纯高斯先验两个CPU进程与两个学习版本的GPU并发同时执行；GPU从两路逐步增加、最多六路，以实测利用率及显存/内存余量控制。算法、权重、输入和全部既有输出不变。当前日志见[GPU接续](../../result/snr_comparison/data/c_stmp_ablation_1000_20261028/acceleration_20261028/README.md)；下方最初两进程顺序安排已由本次资源授权替代。

**2026-10-28 主 SNR 三项 C-STMP 消融已获授权并启动。** 沿用正式 SNR 的 −4/−2/0/2/4/6 dB、每档1000个相同场景，新增高斯信道先验、高斯活动证据、迭代内估计相位三个版本，共18000次推断；完整C-STMP的6000份结果作为配对参照。独立输出在E盘，最多两进程，主线和旧结果保持不变；结束后自动汇总核验，暂不改论文。15项测试通过；首次输入字段读取失败发生在算法推断前，记录已保留并修正。当前状态及执行顺序见[消融批次](../../result/snr_comparison/data/c_stmp_ablation_1000_20261028/README.md)和[实时状态](../../result/snr_comparison/data/c_stmp_ablation_1000_20261028/STATUS.json)。下方“本次授权全部完成”指此前跨信道批次。

**2026-10-28 完整跨信道比较已完成并同步论文。** STMP/C-STMP各12000份、24条件各500，全部满足原收敛判据；六方法共72000条比较结果，318186份审计资产哈希及144组配对覆盖复核PASS。完整图替换STMP临时图，现为13页阅读稿第12页图7；零AER仅显示在对数轴底边，不加零值栏，原统计保持零。正文如实保留A/B高SNR下STMP更优的点。9份重复导出、预览及旧STMP单独PDF已退役，数据、配置和冻结报告保留；论文实际引用的7个独立PDF为现行图。见[完整跨信道核验](../../paper/C-STMP/checks/cross_full_500_20261028/VALIDATION.json)和[论文阅读稿](../../paper/C-STMP/main.pdf)。本次授权实验及图文清理全部完成，不启动其他实验。下方运行中说明为历史记录。

**2026-10-28 用户数重绘与 STMP 跨信道单独图已同步论文。** 用户数重绘与原图逐像素一致，保持现行五档阻尼和全部有限结果；仍为第10页图5。STMP跨信道24条件各500，共12000份已逐份重新评分，123177份绑定资产哈希与实际配置核验通过，全部收敛；D/A/B/C四信道单独图现为第11页图7。论文阅读稿现13页，C-STMP仍4并发运行，完整比较结束后替换临时单独图。仅保留论文独立PDF，16份重绘/临时图已退役，数据与配置保留。见[本轮核验](../../paper/C-STMP/checks/redraw_user_count_cross_stmp_20261028/VALIDATION.json)。

**2026-10-28 用户数β0.1批次完成并更新论文。** 五档各500场景；20/40用户保留β0.2，60/80/100用户β0.1。STMP未收敛数分别为0/0/0/3/14，全部保留。67792份审计绑定资产及完整覆盖核验通过，论文第10页图5已更新并视觉核验；唯一用户数图位于 `paper/C-STMP/figures/user_count.pdf`。回顾性选择及12例诊断计入评估的说明、既有C-STMP例外说明保留。3份暂留旧图与新图多余导出已清理。见 [核验](../../paper/C-STMP/checks/user_count_beta01_500_20261028/VALIDATION.json)。跨信道已有6724份结果已重新核验配置、哈希并重评分，独立接续入口为 `result/receiver_sweeps_500_20261026/resume_after_user_count_20261027/resume.py`；只补剩余17276份，STMP/C-STMP各最多4并发。

**2026-10-27 用户更新接续顺序：用户数完成后继续跨信道。** 当前先运行6并发STMP用户数阻尼0.1，跨信道暂不启动；用户数完成并退出后核验复用已有6724份跨信道结果，接续剩余17276份，STMP/C-STMP各最多4并发、算法参数不变。此授权取代此前“用户数完成后也不自动恢复跨信道”的安排。见[等待与接续计划](../../result/receiver_sweeps_500_20261026/resume_after_user_count_20261027/README.md)。

**2026-10-27 用户数实验已提高到6并发。** 按用户要求独占5080推进STMP用户数阻尼0.1批次；原2进程排空后1399份结果及6097份绑定资产核验通过，从剩余1101份接续，2→4→6逐步增加，现实际6个工作进程已运行并保存新结果，算法、权重与停止判据不变。现行身份和日志见`result/user_count/data/stmp_500_k60_k80_k100_beta01_20261027/resource6_20261027/`，旧host_stdout不再更新。跨信道保持用户暂停，不自动恢复。前一resource4仅启动前路径格式检查失败、未执行推断，证据保留。见[6并发接续](../../result/user_count/data/stmp_500_k60_k80_k100_beta01_20261027/resource6_20261027/README.md)和[实际进程核验](../../result/user_count/data/stmp_500_k60_k80_k100_beta01_20261027/resource6_20261027/STARTUP_VALIDATION.json)。

**2026-10-27 18:03（北京时间）用户暂停跨信道，优先用户数实验。** 跨信道已停止派发、排空在途任务并正常退出，保留6724/24000份结果（6000复用、724新增），无新增失败；未经用户后续指示不恢复。独立STMP用户数阻尼0.1批次继续2并发运行，原算法参数不变。本轮自动跟进只推进用户数出图、论文更新和已授权图片清理，完成后暂停；不自动接续跨信道。见[暂停核验](../../result/receiver_sweeps_500_20261026/monitoring/user_pause_cross_prioritize_beta01_20261027.json)。

**2026-10-27 六项实验只保留论文用图。** 已删除95个旧图、重复导出和预览文件，唯一六图统一在[论文图片目录](../../paper/C-STMP/figures)；原始数据、统计、配置和阅读稿不变。3份旧用户数图为在跑批次的冻结校验依赖，完成后自动删除。旧记录中的源图链接已退役，详见[清理与保留清单](../../result/figure_cleanup_six_20261027/README.md)。

**2026-10-27 活跃概率完整比较已完成。** STMP/C-STMP各2500份推断结果齐全，与四基线组成六方法、每档500场景的完整比较；覆盖、完成文件哈希及审计通过。C-STMP全部收敛，STMP两份迭代上限结果保留。完整图已替换论文图6，原STMP单独图保留为历史。见[完整图](../../result/activity_probability/figures/stmp_c_stmp_500_20261026/activity_probability.pdf)、[论文阅读稿](../../paper/C-STMP/main.pdf)及[核验记录](../../paper/C-STMP/checks/activity_full_500_20261027/VALIDATION.json)。后续跨信道和独立用户数批次按既有授权继续。

**2026-10-27 16:37（北京时间）：按用户授权以最多4个C-STMP进程接续。** 活跃概率已有4864份结果全部保留，绑定文件哈希重新核验通过；补跑剩余136份，包含上次显存不足的场景465、条件0。先单独补该失败例，成功后逐步增加至4并发。原算法参数、权重及停止判据不变；原7并发失败记录保留。随后跨信道的C-STMP也最多4进程，STMP维持4进程。独立STMP用户数阻尼0.1批次继续。见[四进程接续说明](../../result/receiver_sweeps_500_20261026/resume_4workers_20261027/README.md)及[当前状态](../../result/receiver_sweeps_500_20261026/STATUS.json)。

**历史记录：2026-10-27 活跃概率STMP单独结果图已生成并同步论文（现已由上述完整比较替换）。** 五档活动概率0.05/0.10/0.15/0.20/0.25，每档500场景、阻尼0.2；2500份结果已逐份核验并重新评分，2份达到600轮上限的输出均保留。[独立图](../../result/activity_probability/figures/stmp_only_500_20261027/activity_probability.pdf)仅包含STMP，不能视为C-STMP比较已完成；已作为图6加入[C-STMP阅读稿](../../paper/C-STMP/main.pdf)，实际第10页已视觉核验，见[核验记录](../../paper/C-STMP/checks/activity_stmp_only_500_20261027/VALIDATION.json)。用户已澄清暂停活跃概率C-STMP是误会并要求继续，原暂停记录保留，接续以最新队列状态为准。

**2026-10-27 11:24（北京时间）：按用户授权启动 STMP 用户数 β=0.1 独立批次。** 60、80、100用户档各取前500个场景，20、40用户档沿用原β=0.2结果。1012份复用结果已通过哈希、实际配置及重评分核验，新增1488次推断；仅改变指定三档的阻尼，原β=0.2的2500份结果、报告和图完整保留。该调整发生在观察原500场景及12例配对诊断之后，属于回顾性参数开发，12例诊断计入本批次。新批次完成后核验并更新图和论文；当前论文仍展示原β=0.2结果。原活跃概率及跨信道队列继续按原参数运行。见[新批次说明](../../result/user_count/data/stmp_500_k60_k80_k100_beta01_20261027/README.md)、[冻结计划](../../result/user_count/data/stmp_500_k60_k80_k100_beta01_20261027/PLAN.json)和[当前状态](../../result/user_count/data/stmp_500_k60_k80_k100_beta01_20261027/STATUS.json)。

**2026-10-27 用户数 STMP 每条件500场景已完成。** 2500份 STMP 输出与既有比较结果通过覆盖、哈希和审计，1477份达到迭代上限的输出全部保留。活跃概率已自动接续运行；跨信道仍排队。本次完成版图及论文同步记录见 [用户数核验](../../paper/C-STMP/checks/user_count_stmp500_20261027/VALIDATION.json)。另按用户要求完成阻尼0.1的12输入独立配对诊断：60/80/100用户各4个既定场景全部收敛，原0.2为1/12；仅阻尼不同，输入、权重、噪声估计及停止条件一致。此为回顾性小样本诊断，未修改本批参数或替换正式结果，见 [配对核验](../../result/candidates/stmp_beta01_user_count_probe_20261027/VERIFICATION.json)。

**2026-10-27 运行时间实验已按用户要求取消，后续不再开展。** 四 baseline 计时批次从未启动，snr 已暂停，批次已写 STOP。29份运行时间准备文件已按清单删除并核验，其他已完成结果保留；下方历史运行时间安排不再执行。SNR、导频数、用户数、活动概率、跨信道五项四 baseline 数据已完成并保留，共192000条、每条件1000 MC；其他线程不受影响。见[最新范围与取消记录](../../result/baseline_completion_20261025/README.md)。

## 论文目录

`paper/` 只保留三个文件夹，各自包含 `main.tex`、`main.pdf`、`sections/`、`figures/`、`references.bib`、`docs/` 和本稿说明。

- [STMP](../../paper/STMP/README.md)：原三网络稿。
- [C-STMP](../../paper/C-STMP/README.md)：当前 C-STMP 稿。
- [DU](../../paper/DU/README.md)：十层深度展开稿。

2026-10-26 完成目录整理。三稿正文、参考文献、阅读 PDF 和论文图片保持原字节；旧顶层原稿、集中研究文档原件及失效图片链接移入[历史归档](../paper_layout_20261026/README.md)。共用依据已在各稿 `docs/` 内保留副本，术语按各稿维护。旧路径见[映射](../paper_layout_20261026/MAPPING.json)。


**2026-10-26 根目录 `output/` 已整理移除。** 旧四图拼版PDF、PNG及六份检查记录，共8个文件、0.71 MiB，已移入[历史预览归档](../output_previews_20261026)。正式实验图继续保存在 `result/<实验>/figures/`，当前排版预览统一查看 [C-STMP阅读稿](../../paper/C-STMP/main.pdf)。旧预览链接已改指归档；本次为移动归档，未释放这些文件占用的空间，详见[整理说明](../../result/figure_cleanup_four_20261026/README.md)。

**2026-10-26 五项实验旧图片和中间数据已清理。** 去噪、收敛、SNR、导频及用户数的现行图、原始结果和复用依赖保留，共享输入按各实验独立保留。删除33份旧图导出和9份缓存，将1851份旧中间输出及绘图元数据压缩归档，移除100个空目录；204份保护文件清理前后哈希一致。当前五图入口、可恢复归档和执行记录见[五项实验清理记录](../../result/cleanup_five_experiments_20261026/README.md)。下方历史链接如已归档，请通过该记录定位。

**2026-10-26 19:56（北京时间）：按用户授权接续三项500场景实验。** 已启动STMP用户数，随后依次运行STMP/C-STMP活跃概率及跨信道；用户明确跨信道也为每条件500场景。固定前500个配对场景，预计复用7500份同输入、同配置的SNR结果，新增24000次推断；STMP沿用已完成SNR配置，C-STMP活跃概率及跨信道沿用当前β=0.4配置。新原生输出保存在E盘独立目录，各项核验汇总出图后自动接续，三项结束后停止。用户数比较保留既有C-STMP的K100整档β=0.2与K80场景372单例替换及其回顾性说明；不据此调整新实验参数。见[三项接续说明](../../result/receiver_sweeps_500_20261026/README.md)、[冻结队列](../../result/receiver_sweeps_500_20261026/QUEUE.json)与[当前状态](../../result/receiver_sweeps_500_20261026/STATUS.json)。此前用户数单项结束后暂停的安排由本次三项接续授权取代，既有结果仍保留。

**2026-10-26 用户数绘图脚本已按用户要求固定。** [用户数正式入口](../../src/evaluation/plots/user_count.py)现调用[独立固定版本](../../src/evaluation/plots/frozen_user_count_20261026/README.md)，代码、配置及依赖共10份文件已绑定SHA256；只允许指定输入与新输出目录。重画前100场景的高清PNG和预览与刚确认的论文图完全一致，统计亦完全一致，见[复绘核验](../../result/user_count/figures/frozen_paper_interim100_20261026/FREEZE_QA.json)。后续500场景图采用此入口，不受公共绘图配置变化影响；原实验继续运行，完成出图后暂停。

**2026-10-26 后续直接在C-STMP论文中预览实验图。** 结果目录只保存各实验独立图及复现记录；论文排版统一使用 [C-STMP稿件](../../paper/C-STMP/main.tex) 的编译预览和 [阅读稿](../../paper/C-STMP/main.pdf)，不再更新独立的三图/四图模拟论文预览。C-STMP 阅读稿固定为 `paper/C-STMP/main.pdf`，后续编译直接更新该文件，不另存日期或版本 PDF，也不再新增完整论文 PDF 备份。当前四幅论文引用与结果目录采用版已逐字节核对一致，去噪80.01 mm、其余三图88.9 mm；后续图按既定实验顺序同步到论文并检查，见[绘图流程](../../src/configs/plots/README.md)。下方旧拼版预览链接仅为历史记录。

**2026-10-26 用户数临时图统一到论文样式。** 每档前100场景、100用户 β=0.2 的[用户数图](../../result/user_count/figures/paper_interim100_20261026/user_count.pdf)现采用双栏论文中的单栏88.9×55.88 mm、轴8.5 pt/图例6 pt及既定颜色线型。按用户新要求，零AER仅在显示时贴对数轴底边，不另设零值栏或标注；25个统计点和5个精确零值均未改动，见[核验](../../result/user_count/figures/paper_interim100_20261026/QA.json)。原冻结快照及四幅已确认图保留，500场景主实验继续，最终交付沿用此论文样式。

**2026-10-26 论文目录改名并新增 C-STMP。** 原 `paper/TWC-1/` 改为 `paper/STMP/`，原 `paper/TWC-2/` 改为 `paper/DU/`；原稿正文和 PDF 保持不变。新增 [C-STMP 稿件](../../paper/C-STMP/README.md)：按作者要求直接复制 DU 的摘要、引言与系统模型，仅替换深度展开相关段落；算法章节直接复制 STMP，实验加入当前去噪、收敛、SNR及导频四图。见[三稿入口](#论文目录)。

**2026-10-26 去噪论文图横向缩窄。** 按用户要求，宽度由88.9 mm减为80.01 mm，高度66.04 mm、轴8.5 pt、图例6 pt及全部曲线数据不变；[当前去噪图](../../result/channel_denoising/figures/narrow_paper_20261026/channel_denoising.pdf)在[历史四图论文预览](../output_previews_20261026/pdf/four_figures_single_column_actual_size.pdf)中按原生尺寸居中。其余三幅图保持不变，去噪配置已同步；原宽版保留对照。

**2026-10-26 论文实验顺序已确认。** 去噪 → 收敛 → SNR → 导频数 → 用户数 → 活跃概率 → 消融 → 跨信道 → 运行时间。[历史四图实际尺寸双栏预览](../output_previews_20261026/pdf/four_figures_single_column_actual_size.pdf)按左栏去噪/收敛、右栏SNR/导频重排，图注编号同步更新，四幅源图及尺寸不变。后续图按此顺序编排并沿用既定样式，详见[绘图标准](../../src/configs/plots/README.md)。此更新仅涉及论文呈现，不改变正在执行或暂停的实验安排。

**2026-10-26 用户数实验按授权仅将100用户档改为β=0.2。** 其他20/40/60/80用户档仍为β=0.4，权重、门限、600轮上限及全部停止条件不变。旧批保存全部1244份结果后退出；独立接续批逐份核验复用其他档1058份结果及已完成的15份β=0.2诊断，7进程继续其余1427次推断。原100用户β=0.4结果保留为对照，不混入新面板。调整发生在观察前100场景与部分失败诊断之后，属于回顾性参数开发。每档500场景完成、核验出图后暂停。历史图清理导致的旧退出校验错误已绑定证据修复，接收机及数据未变。见[新批次说明](../../result/user_count/data/c_stmp_variance_em_500_k100beta02_20261026/README.md)、[冻结计划](../../result/user_count/data/c_stmp_variance_em_500_k100beta02_20261026/PLAN.json)与[状态](../../result/user_count/data/c_stmp_variance_em_500_k100beta02_20261026/STATUS.json)。全局默认算法及既有SNR/导频实验不变。

**2026-10-26 四幅论文图最终确认。** 当时保留SNR、导频、去噪和当前C-STMP收敛图，以及[四图实际尺寸双栏预览（现已归档）](../output_previews_20261026/pdf/four_figures_single_column_actual_size.pdf)。旧收敛图、旧三图论文预览及临时检查图共8个文件已删除；18个定稿导出/预览文件与59个数据、配置和核验文件哈希均未改变。后续绘图继续按单栏88.9 mm、轴8.5 pt、图例6 pt、统一线型颜色及完整网格执行，图例依实际空白布置。见[四图索引及清理记录](../../result/figure_cleanup_four_20261026/README.md)。下方三图定稿和历史版本记录仅为过程记录，旧图链接可能已退役。

**2026-10-26 当前C-STMP收敛实验已重跑。** 场景200、0 dB、同一观测，从当前登记入口新增1次C-STMP推断，60轮收敛、NMSE −13.853659 dB、AER为0；概率、NMSE及停止轮数与已完成SNR实验同输入结果完全一致。STMP复用原85轮轨迹与原停止规则。87项保护资产哈希不变，未训练。收敛绘图配置已切到[当前图](../../result/snr_comparison/figures/convergence_current_paper_20261026/convergence.pdf)，见[运行核验](../../result/snr_comparison/data/c_stmp_current_convergence_20261026_scene0200_snr0/RESULT.json)。下方旧分类器版本保留为历史。

**2026-10-26 历史收敛图按当前论文样式重绘。** 场景200、0 dB，STMP 85轮、C-STMP 60轮，145个迭代点均与保存的误差及活动判决核对，未重新推断。该C-STMP为导数方差配旧活动分类器的历史版本，不是SNR定稿采用的当前查询方差更新版。见[收敛图](../../result/snr_comparison/figures/convergence_paper_20261026/convergence.pdf)；可通过补充入口 `src/evaluation/plots/convergence.py` 和对应JSON配置重绘。

**2026-10-26 三幅论文图已定稿。** 保留 SNR、导频的 `full_grid_final_20261026` 和去噪的 `full_grid_final_v2_20261026`；均保留完整上下网格。八个绘图配置已统一到当前字号、线型、网格和紧凑布局，默认只输出合并图。旧图清理已完成，共删除950个文件（123.92 MiB），三幅定稿及保护资产的哈希均未改变；详见[保留清单及清理状态](../../result/figure_cleanup_20261026/README.md)。

**八个正式绘图入口已统一默认样式。** 不带 `--config` 也会读取对应配置：C-STMP 红色圆圈实线、STMP 蓝色方块实线，主网格加深、对数次网格浅灰虚线。图例按实际空白安排，接收机合并图只在 AD 子图显示；优先图内分组，不为图例扩大坐标范围，自动布局发生图外回退时须人工检查后再定稿；旧图的冻结复现样式保持原文。见[绘图配置说明](../../src/configs/plots/README.md)。

**2026-10-26 用户数500场景评估加速至7个GPU进程。** 按用户要求，在保存全部在途结果后由6进程平稳接续；595份已有结果全部核验保留，只继续剩余1905个输入。算法、权重、门限和研究计划不变，资源配置独立记录于[并行执行计划](../../result/user_count/data/c_stmp_variance_em_500_resumed_20261026/parallel7/PLAN.json)。实际新主进程见`parallel7/START.json`，自动跟进已更新，完成每档500场景图后暂停。

**2026-10-26：八个绘图入口支持统一 JSON 配置。** 通过 `--config src/configs/plots/<实验名>.json` 修改算法与顺序、条件和物理场景选择、图例、线型、坐标轴、分面、尺寸与导出格式。当前完整 SNR、导频500场景及历史去噪等保存数据可直接读取；选择场景时重新配对汇总，不启动推断。见[配置与使用说明](../../src/configs/plots/README.md)。原始图及其固定复现代码保留。

**2026-10-26 用户恢复用户数500场景实验。** 按“继续跑500场景的用户数实验”，使用当前默认C-STMP，20/40/60/80/100用户每档前500场景；40用户500份复用，只新增2000次，四baseline仅复用。新执行记录保留原暂停批次及已退役资产凭据，算法、权重和最新图门限不变；完成本项核验出图后停止，不接续其他实验。见[本批次说明](../../result/user_count/data/c_stmp_variance_em_500_resumed_20261026/README.md)与[实际状态](../../result/user_count/data/c_stmp_variance_em_500_resumed_20261026/STATUS.json)。

**2026-10-26 用户授权切换默认 C-STMP 并完成三算法清理。** 默认算法目录 `src/configs/algorithms.json` 的 `C_STMP` 已绑定 `C_STMP_variance_em_20261025`，与六档 SNR、1000 场景的已完成版本一致：一阶 epoch 200 EMA、分类器 epoch 90 EMA、导数方差及查询方差更新。STMP、C-STMP、DU 分别保留 3、2、1 份权重，另保留图中 GNN 基线的 1 份权重；没有剩余的中间网络。清理共 54,994 个文件、约 95.42 GiB，含 138 个旧网络/断点文件。当前实验输入、种子、原始结果、图表统计、源码和正负结果报告保留。见[保留清单](../../result/storage_cleanup_20261026/RETENTION.json)、[默认入口切换记录](../../result/storage_cleanup_20261026/DEFAULT_SWITCH.json)和[清理后检查](../../result/storage_cleanup_20261026/FINAL_CLEANUP_REPORT.json)。

SNR 的 6000 份保存结果已在清理后重新核验；SNR 图及导频前 500 场景图均已从保存统计重绘，PNG 与原图完全一致。可用 `.\.venv\Scripts\python.exe result\storage_cleanup_20261026\replay_figures.py` 重绘到清理记录下的独立目录，不启动推断或训练。旧 SNR/导频冻结计划仍保留已退役的有色二阶网络哈希，因此其原始完整依赖校验不再适用；原记录不改写。新推断使用当前默认入口创建新计划，保存数据重绘使用上述入口，退役详情见[记录](../../result/storage_cleanup_20261026/RETIRED_NETWORK_RECEIPT.json)。

**2026-10-26 用户最新更新：导频500场景完成后先暂停，不运行后续实验。** 前500场景六档结果已齐，导频保存全部在途结果后停止；只读500场景汇总与绘图继续完成。用户数批次及其队列已写STOP，尚未启动用户数推断，准备好的计划和500份复用结果保留。自动跟进已暂停，不恢复用户数、后500场景、门限校准或其他实验。下方“自动接续用户数”安排已被本条替代。

**2026-10-26 用户更新：导频和下一项用户数实验各先完成500场景并出图，剩余以后再补。** 导频固定前500场景六档齐全后，由独立监控请求停止派发并保存在途结果，原1000场景计划与既有结果保留。随后核验并生成500场景导频图，再接续20/40/60/80/100用户、每档前500场景的C-STMP；40用户500份已核验复用，只新增2000次，四baseline直接配对历史结果。接收机及最新图门限不变，追加门限校准已按用户要求停止。接续队列已启动等待，不能把等待状态当作用户数推断已运行。见[500场景接续说明](../../result/user_count/data/c_stmp_variance_em_500_20261026/README.md)、[导频停止监控](../../result/pilot_frames/data/c_stmp_variance_em_1000_20261026/control500/STATUS.json)和[接续状态](../../result/user_count/data/c_stmp_variance_em_500_20261026/queue/STATUS.json)。下方1000场景安排保留为历史。

**2026-10-26 05:55（北京时间）：六档SNR的1000场景已完成并核验，按用户授权接续C-STMP导频。** SNR共6000份C-STMP结果（740复用、5260新增）与30000份历史比较结果；C-STMP在各档的NMSE/AER均优于原STMP，整体平均迭代63.872轮对98.977轮，保留3份达到上限的有限输出。baseline仍使用原冻结读出，门限开发与评估有重叠，属于回顾性比较；独立追加门限验证另行运行，不用于改动本批次。见[SNR汇总](../../result/snr_comparison/data/c_stmp_variance_em_1000_snr_m4_p6_20261025/SUMMARY.json)及[完整图](../../result/snr_comparison/figures/c_stmp_variance_em_1000_snr_m4_p6_20261025/comparison.png)。导频沿用相同接收机、权重和参数，16帧1000份已核验复用，其余五档新增5000次，6个GPU进程；首个物理场景六档保存结果核验通过。新增原生输出存E盘，并通过原结果目录的 `inference` 联接访问，以解决启动前D盘空间不足；未删减任何结果。见[导频状态与存储说明](../../result/pilot_frames/data/c_stmp_variance_em_1000_20261026/README.md)。

**2026-10-25 22:26（北京时间）：用户授权当前六档 SNR 结束后接续 C-STMP 导频实验。** 已安排每30分钟检查一次的本对话自动跟进，等待当前 SNR 推断、核验与汇总全部完成并退出后，在独立目录准备冻结执行计划并启动。导频沿用0 dB、40用户、8/16/24/32/40/48帧、每档1000场景；保持当前修复版接收机及权重。输入清单已核对，16帧的1000个输入与SNR 0 dB完全对应，届时核验输出后复用，只新增其余5000次C-STMP推断；历史STMP及四baseline推断只读复用。当前导频尚未启动，SNR继续运行。见[接续说明](../../result/pilot_frames/data/c_stmp_variance_em_1000_20261026/README.md)、[接续协议](../../result/pilot_frames/data/c_stmp_variance_em_1000_20261026/QUEUE_PROTOCOL.json)和[准备核查](../../result/pilot_frames/data/c_stmp_variance_em_1000_20261026/QUEUE_PREFLIGHT.json)。

**2026-10-25 22:14（北京时间）：按用户要求，后续SNR推断及绘图范围收窄为−4、−2、0、2、4、6 dB。** 原八档批次通过STOP.json保存全部在途结果后退出，共986份，其中保留范围内740份已验证并全部复用，既有8/10 dB的246份结果保留。新的独立冻结计划仍为1000场景、同接收机/权重/门限/阻尼和同输入，总量6000，只补跑5260份，6个GPU工作进程继续执行。完成汇总和绘图均只使用六档，保持既定六方法图例及AER对数坐标；100场景临时图也已从核验数据中筛出六档重绘。范围调整发生在查看100场景结果之后，已记录在计划中，原八档图与结果不覆盖。见[当前状态](../../result/snr_comparison/data/c_stmp_variance_em_1000_snr_m4_p6_20261025/STATUS.json)、[新计划](../../result/snr_comparison/data/c_stmp_variance_em_1000_snr_m4_p6_20261025/PLAN.json)、[复用清单](../../result/snr_comparison/data/c_stmp_variance_em_1000_snr_m4_p6_20261025/REUSED.json)和[六档100场景图](../../result/snr_comparison/figures/c_stmp_variance_em_1000_snr_m4_p6_20261025/interim100/comparison.png)。以下八档启动记录为历史状态。

**2026-10-25 21:22（北京时间）：用户授权启动当前查询方差修正版 C-STMP 的完整1000场景 SNR 评估。** 配置与已完成的50场景完全一致，一阶epoch 200 EMA、新分类器epoch 90 EMA、导数方差、门限0.5、新消息权重0.4，以及标量查询方差更新均冻结。直接复用场景0–49的400份已核验输出，只补跑场景50–999的7600个输入；不混入旧版C-STMP结果，不重训。已知相位、估计噪声、8档SNR与历史STMP及四个baseline共用输入；6个GPU工作进程、每进程2个CPU线程。完成后自动重评分、汇总NMSE/AER/漏检/虚警/迭代/收敛率，并保持既定六方法图例、AER对数坐标和零值单列。包含既往开发场景且baseline门限开发与评估重叠，仍披露为回顾性比较。当前候选独立保存，默认主线和旧暂停批次不变。见[运行状态](../../result/snr_comparison/data/c_stmp_variance_em_1000_20261025/STATUS.json)、[冻结计划](../../result/snr_comparison/data/c_stmp_variance_em_1000_20261025/PLAN.json)、[复用清单](../../result/snr_comparison/data/c_stmp_variance_em_1000_20261025/REUSED.json)及[数学核查](../../paper/C-STMP/docs/C_STMP_DERIVATION_20261024.md#13-当前标量查询方差修正的数学核查2026-10-25)。以下“完整1000场景暂停”记录为旧批次历史状态。

**2026-10-25：查询方差更新候选完成原50场景×8档SNR的400次完整复评。** 全部重新推断并收敛，原有虚警5→0，但漏检7→9；新增漏检为场景2/−2 dB的用户32与场景30/0 dB的用户5（零起始编号），均为该场景最弱活跃用户。2/4 dB本批次均零误判，总错误12→9、AER 0.00075→0.0005625；总能量NMSE−13.59588→−13.62551 dB，平均迭代62.3125→69.0125轮，不能宣称普遍加速或全面改善。未重训或调整冻结候选，10个已知问题输入的重新推断结果与前次完全一致；400份新结果和2400份历史结果核对通过，816项保护资产未变。4个高SNR输入共8个早期迭代触发原有超范围复用机制，最终均回到支持范围并收敛；汇总脚本按逐轮记录精确核对调用数，保留最初过强检查及修正说明，未修改推断结果。对比图保持既定图例与AER对数坐标，零值单列；包含开发样本和历史baseline门限重叠，属于回顾性复评。默认主线未切换，完整1000场景继续暂停。见[结果与逐SNR比较](../../result/snr_comparison/data/c_stmp_variance_em_50_20261025/SUMMARY.json)、[对比图](../../result/snr_comparison/figures/c_stmp_variance_em_50_20261025/comparison.png)和[冻结计划](../../result/snr_comparison/data/c_stmp_variance_em_50_20261025/PLAN.json)。

**2026-10-25：完成当前 C-STMP 查询方差更新候选的有限配对验证，未重训。** 独立候选保留现有标量消息接口、一阶 epoch 200 EMA、新分类器 epoch 90 EMA、门限0.5与新消息权重0.4；每轮由后验预期残差能量更新查询方差修正系数，同一方差用于一阶、导数方差、分类器及外信息计算。原10个问题输入的虚警5→0、漏检仍7、总能量NMSE−9.037→−9.198 dB，2/4 dB的三个目标虚警均消失。另6个物理场景（300–305）×4档SNR的24个配对输入两版均零误判，NMSE−14.605→−14.663 dB，但平均迭代60.25→67.42轮，不能宣称普遍加速或总体AER改善。场景200/0 dB保持60轮、零误判、NMSE−13.854 dB。全部候选运行收敛；2项数学检查、关闭适配后的原版复现、60份完整接收输出重评分及406项保护资产核对通过。该更新采用近似神经后验，不宣称精确EM单调性。候选独立保存，默认主线未切换，完整SNR和训练继续暂停。见[结果及局限](../../result/snr_comparison/data/c_stmp_variance_em_20261025/SUMMARY.json)、[公式与依据](../../result/snr_comparison/data/c_stmp_variance_em_20261025/METHOD.json)、[实现](../../src/algorithm/C_STMP_variance_em_20261025/iterations.py)和[候选配置](../../src/configs/candidates/C_STMP_variance_em_20261025.json)。

**2026-10-25 19:36：用户决定回到当前 C-STMP 的漏检/虚警问题，暂停更换矩阵消息接口的方向。** 已停止独立矩阵评估进程，保留8/14项完整结果、3项在途进度，另3项尚未开始；在途输出不作为完成结果评分。照片中的场景200、0dB旧C-STMP精确复现为60轮、NMSE−13.85988dB、零误判；复用相同一阶和两套已有分类器的完整矩阵候选均600轮未收敛、NMSE+19.65702dB、35次虚警。该失败不等于旧C-STMP失败，也不能单独证明必须重训。已训练权重、冻结原算法及433项保护资产未变；新重训与原1000场景均继续暂停。见[暂停记录](../../result/snr_comparison/data/c_stmp_reuse_20261025/STOP_RECEIPT.json)和[场景200配对图](../../result/snr_comparison/figures/c_stmp_reuse_20261025/scene200_original_classifier.png)。以下运行启动记录为历史状态。

**2026-10-25 19:18：按用户要求暂停重训，改为复用已有有色权重评估矩阵消息接口。** 新一阶训练在第30轮38592样本处保存完整断点并退出，分类器阶段未启动。独立适配器保留已训练一阶及分类器全部权重，统一列协方差下的预处理、二阶读出和反馈；分类器使用原特征的矩阵推广，在C=vI时还原旧接口，但不宣称其已学会一般有色噪声的活动证据。5项接口/数学检查通过。现评估场景200、0dB的两套已有分类器配对，以及原10个错误输入；不恢复1000场景、不训练。见[运行状态](../../result/snr_comparison/data/c_stmp_reuse_20261025/STATUS.json)、[冻结计划](../../result/snr_comparison/data/c_stmp_reuse_20261025/PLAN.json)和[适配器](../../src/algorithm/C_STMP_reuse_20261025/receiver.py)。以下训练启动记录为历史状态。

**2026-10-25 18:45：统一消息的 C-STMP 已实现并启动配套训练。** 新独立接收循环在每轮使用同一精度矩阵消息：线性积分、一阶条件均值、活动分类、复数导数列协方差、活动混合及外信息反馈；不使用末端校准。沿用50000/5000干净信道，一阶从原随机主干训练200轮，分类器随机初始化训练100轮，完成后自动评估原10个问题输入及4个独立物理场景×3档SNR。10项数学检查、GPU图梯度和权重读写检查通过，3轮随机权重闭环检查通过；正式性能尚待训练后评估。5080已进入正式一阶训练，保留原STMP/DU/C-STMP和暂停的1000场景批次。见[当前运行状态](../../result/snr_comparison/data/c_stmp_column_50000_20261025/STATUS.json)、[启动检查](../../result/snr_comparison/data/c_stmp_column_50000_20261025/PREFLIGHT.json)和[实现说明](../../paper/C-STMP/docs/C_STMP_COLUMN_MESSAGES_20261025.md#8-完整实现与正式训练)。

**2026-10-25：完成每用户输入列协方差消息的独立推导与接口验证，尚未接入正式接收机。** 在独立 Gaussian 消息近似下，显式保留每用户 16×16 列协方差，单位响应和协方差传播核对误差≤3.2e−12；7项数学/复数/活动混合检查通过。10个已知问题输入的首轮共400个用户中，新C全部超出现有列相关噪声训练族，382个超出平均功率范围，不能直接复用现有权重；已实现等价精度输入以避免显式放大查询数值。真实首轮残差归一化二次型仍有0.985–1.485的用户中位范围，统计近似并未自动准确。尚无新AER或完整收敛结论，未训练，正式1000场景继续暂停。见[推导、实现和限制](../../paper/C-STMP/docs/C_STMP_COLUMN_MESSAGES_20261025.md)与[数值记录](../../result/snr_comparison/data/c_stmp_column_messages_20261025/SUMMARY.json)。

**2026-10-25：末端噪声功率修正仅保留为诊断对照，不作为 C-STMP 的正式修复。** 用户指出末端重算缺少循环内部的一致性。该对照说明活动检测对查询噪声条件敏感，但原循环的停止条件仍对应原消息，最终重算没有得到新条件下的固定点，也没有解决弱用户漏检。保留全部正负结果、代码和配置；不采用该末端处理恢复完整 SNR。后续修复回到线性模块的用户内响应与查询协方差、同条件均值与活动概率、匹配的方差及外信息更新。相关协方差仍须在明确的 Gaussian 消息近似下推导，不能直接把导频 Gram 当作全部误差协方差。

**2026-10-25：查询噪声功率修正完成两项候选验证，原完整SNR仍暂停。** 持续把中位数查询功率反馈给迭代，虽然已知问题输入的误判12→6，但NMSE变差0.377 dB，因此未采用。独立的最终输出修正保留原迭代，只在结束后用同一可观测噪声条件重算均值、导数方差和分类器：10个问题输入中虚警5→0、漏检仍7、NMSE−9.037→−9.123 dB；没有引入新误判。另20个新物理场景×4档SNR（80输入、3200判决），两版均零误判，NMSE−13.452→−13.431 dB，不能据此宣称总体AER优势；迭代次数完全不变，每次接收额外3次一阶前向和1次分类器。6项针对性检查及全部输入/结果/保护资产核对通过。未训练、未切换默认模型，旧STMP/DU/C-STMP保留。见[结果及局限](../../result/snr_comparison/data/c_stmp_query_repair_20261025/readout_validation/REPORT.md)、[候选配置](../../src/configs/candidates/C_STMP_query_readout_20261025.json)、[独立算法目录](../../src/configs/candidates/algorithms_C_STMP_query_readout_20261025.json)和[推导](../../paper/C-STMP/docs/C_STMP_QUERY_POWER_REPAIR_20261025.md)。剩余弱用户漏检与完整有色消息模型尚未解决。

**2026-10-25：完成剩余误判的逐模块诊断，未训练或修改接收机。** 固定 10 个问题输入，完成原结果复现、真实注入噪声对照、同查询均值/方差/分类器检查、配对白/列相关 Gaussian 控制，以及三个代表输入的 8 方向方差和真实活跃反馈诊断。LMMSE 数值核对通过；所抽查导数方向与自动微分最大相对差 0.412%，8 方向未改善代表误判。主要缺口是实际查询含明显输入列相关性和轻微功率失配，但一阶运行条件仍为 vI、分类器仍按白噪声训练。真值辅助修正同查询噪声条件时虚警 5→0、漏检仍为 7，仅为离线诊断。新一阶同查询活跃均值 NMSE 比旧一阶改善 1.81 dB，但漏检用户的条件均值仍接近 0 dB。直接给出列 Gram 会减少部分虚警却恶化均值 NMSE，不能直接采用。见[完整报告与所有限制](../../result/snr_comparison/data/c_stmp_component_diagnostic_20261025/REPORT.md)及[统计模型推导](../../paper/C-STMP/docs/C_STMP_COMPONENT_DIAGNOSTIC_20261025.md)。完整 SNR 实验保持暂停，原权重、代码、配置与结果均保留。

**2026-10-25：新分类器增大阻尼的诊断完成。** 使用同一阶 epoch 200、同新分类器 epoch 90 EMA、同导数方差和停止规则，只将新消息权重 β 从 0.4 降到 0.2。此前出错的 10 个场景–SNR 组合中，全部 400 次活动判决相同，仍为 7 漏检、5 虚警；两版均全部收敛。平均迭代 73.8→120.0，总能量 NMSE −9.036816→−9.036213 dB。本次更强阻尼没有改善这些误判；这是错误样本诊断，不外推总体性能。首轮概率和导数方差完全相同，配置核对确认仅阻尼改变，保存输出重评分与受保护资产哈希检查通过。见[报告](../../result/snr_comparison/data/c_stmp_retrained_damping02_errors_20261025/REPORT.md)及[独立配置](../../src/configs/candidates/C_STMP_retrained_damping02_20261025.json)。未重新训练，原 β=0.4 配置与完整 SNR 实验继续保持暂停。

**2026-10-25：按用户要求完成已有误判场景的解析活动概率诊断，未训练网络。** 独立 C-STMP 候选保留新一阶 epoch 200、导数方差、0.4 新消息权重与原停止规则，只将分类器换为 Cai Gaussian 消息积分的标量方差特例。固定 8 个物理场景的 10 个场景–SNR 输入、全部 400 次用户判决：漏检 7→1，但虚警 5→169，总错误 12→170；平均迭代 73.8→281.8，解析版 3/10 未收敛仍纳入统计；总能量 NMSE −9.037→−8.256 dB。原 12 次误判修复 8 次、引入 166 次新虚警，不支持直接移除分类器。此为按错误选择的回顾性诊断，不代表总体 AER，也不证明分类器理论上必需。公式数值核对、首次同查询导数输出、输入/保护资产哈希及落盘后重评分通过。见[完整报告](../../result/snr_comparison/data/c_stmp_analytic_errors_20261025/REPORT.md)、[独立计划](../../result/snr_comparison/data/c_stmp_analytic_errors_20261025/PLAN.json)和[公式与边界](../../paper/C-STMP/docs/C_STMP_ANALYTIC_ACTIVITY_20261025.md)。完整 SNR 实验仍保持暂停，旧算法、分类器与冻结绑定未改。

**2026-10-25 14:46（北京时间）：用户要求暂停新分类器 C-STMP 的完整 SNR 评估并检查分类器。** 已通过本批次 `STOP.json` 保存在途结果后停止，状态为 `STOPPED_BY_USER`，共保存 487/8000 个场景–SNR 组合、待处理数 0；主进程及工作进程退出，不自动恢复。固定前 50 场景八档 SNR 的只读配对检查显示：仅替换分类器的 C-STMP 总误判由 21 降为 12（漏检 8→7、虚警 13→5），但 −4 dB 为 7→8；剩余漏检全部是各场景最弱活跃用户，且存在概率较高的虚警。训练仍为白噪声合成查询，实际查询失配是待验证原因，不能据此直接认定网络容量不足。见[暂停状态](../../result/snr_comparison/data/c_stmp_retrained_1000_20261025/STATUS.json)、[50场景图](../../result/snr_comparison/figures/c_stmp_retrained_1000_20261025/interim50/comparison.png)及[诊断记录](../../result/snr_comparison/data/c_stmp_retrained_1000_20261025/classifier_diagnostic_20261025/SUMMARY.json)。冻结计划、接收机、权重、门限和原算法保留，未追加训练或推断。

**2026-10-25 14:09（北京时间）：新分类器完成 100 轮后，已启动完整 JADCE SNR 评估。** 共 156300 次更新，按固定验证 BCE 选中 epoch 90 EMA（BCE 0.0410023）；使用独立 C-STMP 配置，冻结一阶 epoch 200、导数方差、0.4 新消息权重及原停止规则。场景 0 和 200 的全部 8 档预检共 16 次，均 60–64 轮收敛、AER=0；预检只验证运行，不代表总体性能提升。现以 6 个 GPU 工作进程、每进程 2 个 CPU 线程执行同输入的 1000 场景×8档 SNR（8000 次完整接收，含预检），保持已知相位、估计噪声口径。见[运行状态](../../result/snr_comparison/data/c_stmp_retrained_1000_20261025/STATUS.json)、[冻结计划](../../result/snr_comparison/data/c_stmp_retrained_1000_20261025/inference/PLAN.json)、[预检](../../result/snr_comparison/data/c_stmp_retrained_1000_20261025/PREFLIGHT.json)及[新分类器配置](../../src/configs/candidates/C_STMP_retrained_20261025.json)。旧分类器的 1170 个结果及旧 STMP/DU 保留，旧运行仍暂停；完成后自动核验 AER、漏检/虚警、NMSE、迭代和收敛率，附原 100 场景的新旧分类器配对比较。baseline 沿用用户采纳的历史规则，明确开发/评估场景重叠；并行耗时不用于算法独立延迟比较。

**2026-10-25 13:00（北京时间）：分类器训练已按用户要求加速并续跑。** 从第 25 轮第 41696 个样本、38815 次更新的完整断点继续，加入单线程后台批次预取和固定内存异步搬运；原实现、断点、最优权重与历史已保存。配对检查确认查询/噪声/RNG 恢复完全一致，8 次更新后参数最大差异 2.98e-8，冻结一阶未变；150 步交错计时吞吐量提高 28%。首个完整加速轮（epoch 26，包含验证）44.38 秒，此前约 53 秒；GPU 利用率采样为 85%–91%。训练目标、batch=32、微批=16、Adam/EMA、float32 和累计 100 轮预算保持一致；SNR 实验仍暂停。见[执行记录](../../result/snr_comparison/data/c_stmp_classifier_50000_100epochs_20261025/acceleration_20261025/EXECUTION.json)、[配对验证](../../result/snr_comparison/data/c_stmp_classifier_50000_100epochs_20261025/acceleration_20261025/BENCHMARK.json)和[当前状态](../../result/snr_comparison/data/c_stmp_classifier_50000_100epochs_20261025/status.json)。epoch 25 耗时只记录续跑部分，不作为整轮加速依据。

**2026-10-25 12:36（北京时间）：用户要求暂停完整 SNR 实验，把 GPU 留给分类器训练。** 已通过 `STOP.json` 让在途接收完成并保存，状态为 `STOPPED_BY_USER`，保存 1170/8000 个场景–SNR 组合、待处理数为 0；6 个 GPU 工作进程均已退出。冻结计划、权重和已有结果保持原样，等待用户要求后再续跑。100 轮分类器训练已进入第 1 轮，当前是唯一占用 GPU 的 Python 研究进程。以下 12:34 的共用 GPU 安排已被本条替代。

**2026-10-25 12:34（北京时间）：按用户要求从随机初始化重训 C-STMP 活动分类器 100 轮。** 固定新一阶 epoch 200 EMA，正负查询均使用其 `C=vI` 条件均值；沿用原分类器结构、50000/5000 信道、平衡类别、噪声范围、Adam、EMA 和批量设置，不加载已训练分类器。接口、梯度、GPU graph、固定验证随机数和权重读写预检通过；独立后台进程已启动，先准备磁盘验证缓存，再完成全部 100 轮，不早停。见[状态](../../result/snr_comparison/data/c_stmp_classifier_50000_100epochs_20261025/status.json)、[训练配置](../../src/configs/training/colored_activity_20261025.json)及[预检](../../result/snr_comparison/data/c_stmp_classifier_50000_100epochs_20261025/PREFLIGHT.json)。保留验证最优和第 100 轮权重，完整接收机 AER 尚待配对验证；不使用正式 SNR 场景训练或选权重。正在运行的 SNR 实验继续使用原冻结分类器，新训练与其共用 GPU。

**2026-10-25 用户确认后续 baseline 判决口径：采用所附历史 AER 图的原规则。** Off-grid SBL 与 SOMP 按接收机估计 SNR 最近节点分档，GNN-ASPL 与 GAMP-SBL 使用历史固定门限；端点/中点处理原样保留，不重新拟合。后续 baseline 汇总与绘图先读取 [默认策略入口](../../result/BASELINE_READOUT.json) 和 [采纳说明](../../result/snr_comparison/data/adopted_baseline_readout_20261025/README.md)。当前用户数原始推断继续；完成后通过独立新应用写入 `selected_readout_20261025/`，不调用旧全固定门限后处理。历史冻结资产与结果保留；原门限开发和当前评估场景重叠，披露为回顾性迁移评估。以下较早的门限安排作为历史保留。

**2026-10-25 11:07（北京时间）：用户授权启动导数版 C-STMP 完整 SNR 实验。** 独立冻结计划采用一阶 epoch 200 EMA、导数方差、旧分类器、门限0.5、新消息权重0.4；1000个配对场景×8档SNR，共8000次完整接收。场景200八档预检均60轮收敛、AER为0，预检结果计入正式集合。6个常驻GPU工作进程、每进程2个CPU线程；原CPU用户数实验继续。见[运行状态](../../result/snr_comparison/data/c_stmp_derivative_1000_20261025/STATUS.json)、[冻结计划](../../result/snr_comparison/data/c_stmp_derivative_1000_20261025/inference/PLAN.json)和[预检](../../result/snr_comparison/data/c_stmp_derivative_1000_20261025/PREFLIGHT.json)。输入与8000份旧STMP结果已逐项配对，77项受保护资产未变；原二阶失稳计划保留。所有有限但未收敛结果继续纳入统计，异常保存并停止且不自动重试；完成后自动核验、汇总和绘图。并行耗时只用于吞吐量评估。

**2026-10-25 补充完整接收计时：导数版较少迭代抵消了单轮额外计算。** 场景200、8/10 dB，各方法完整预热后交错计时3次，保留原停止规则。导数C-STMP（新消息权重0.4）均60轮，耗时中位数7.39/7.45秒；旧STMP为129/144轮、11.03/12.16秒；学习二阶C-STMP（0.2）为103/118轮、10.32/12.14秒。导数版相对旧STMP减少33.0%/38.8%时间，相对学习二阶减少28.4%/38.7%；AER均0，导数版NMSE略低。仅一个物理场景，CPU后台实验仍运行；[计时协议、全部重复与局限](../../result/runtime_comparison/data/c_stmp_variance_scene0200_20261025/REPORT.md)。原算法与绑定未改，正式1000场景未启动。

**2026-10-25 新二阶C-STMP高SNR排查完成，完整1000场景尚未启动：** 场景200使用0.4新消息权重时，8/10dB均600轮振荡未收敛、AER87.5%；仅改为0.2后分别103/118轮收敛、AER为0。另4个独立随机场景×8档SNR全部收敛，60–194轮，仅−4dB共3次漏检、无虚警。已保存[独立0.2候选](../../src/configs/candidates/C_STMP_second_damping02_20261025.json)，详见[报告与局限](../../result/snr_comparison/data/c_stmp_stability_20261025/REPORT.md)及[对照曲线](../../result/snr_comparison/figures/c_stmp_stability_20261025/controlled_comparison.png)。导数版高SNR参考仍更少迭代、NMSE略低；本次不宣称学习二阶总体优越。原0.4的[冻结计划与失败记录](../../result/snr_comparison/data/c_stmp_second_1000_20261025/README.md)保留，不能混入0.2结果。77项原算法、权重及绑定资产未变。

**2026-10-25 新二阶网络已完成并对比场景200：** 完成100轮，选中epoch96 EMA。0 dB场景200中，新二阶C-STMP的NMSE为−13.910 dB、AER为0，与导数版−13.860 dB基本持平；均60轮停止，三次完整推断耗时中位数由7.98秒降至6.22秒。新版本本场景未出现非正方差，原导数版67/2400次；旧STMP参考为−11.788 dB、85轮、7.33秒。见[结果与限制](../../paper/C-STMP/docs/C_STMP_DERIVATION_20261024.md#9-2026年10月25日二阶网络完成与场景200配对比较)、[收敛与时间图](../../result/snr_comparison/figures/c_stmp_second_20261025_scene0200_snr0/comparison.png)和[原始结果](../../result/snr_comparison/data/c_stmp_second_20261025_scene0200_snr0/RESULT.json)。仅此一个场景，旧算法、权重和全局绑定保留。

**2026-10-25 有色噪声去噪正式实验已完成：** 1000 场景、6 档 SNR、3 档相关强度，以及 48 组保存接收机条件全部完成并核验，约 46 分钟。合成实验中新网络使用 C 在低 SNR 改善，在 0–30 dB 比使用 vI 退化；均匀接收机诊断组中，新网络用 vI 优于旧网络，但加入估计 C 比同网络用 vI 差 0.32–1.94 dB。见[完整报告](../../result/channel_denoising/data/colored_noise_1000_20261025/REPORT.md)、[合成有色图](../../result/channel_denoising/figures/colored_noise_1000_20261025/colored_denoising.png)、[接收机输入图](../../result/channel_denoising/figures/colored_noise_1000_20261025/receiver_queries.png)和[实验协议](../../paper/C-STMP/docs/COLORED_DENOISING_EXPERIMENT_20261025.md)。原 AWGN 图保留，新旧一阶权重及接收机绑定未改变。

**2026-10-25 去噪新曲线已追加：** 新有色训练的一阶 epoch 200 EMA 已完成原 500 场景、六档 AWGN 的补算；3000 组输入与旧一阶网络实验的真值、观测和噪声哈希完全一致。原九条曲线保留，新增蓝色三角线，见[十曲线图](../../result/channel_denoising/figures/colored_first_500_20261025_v2/channel_denoising.png)和[结果报告](../../result/channel_denoising/data/colored_first_500_20261025_v2/REPORT.md)。旧 50k 网络在 10–30 dB 的 NMSE 仍更低；新网络在 −20、−10 dB 更低。接收机绑定不变，统一入口也已登记 `pretrained_colored_first`；[此前接入记录](../../result/channel_denoising/data/colored_first_integration_20261025/README.md)保留。

**2026-10-25 用户授权：开始训练配套二阶 score 网络。** 新一阶 epoch 200 EMA 固定；新增独立的协方差条件二阶 score 迹网络，沿用原 50000/5000 信道、有色噪声族及当前旧二阶的 100 轮预算。数学、恢复和 GPU 检查通过后已启动；进度见[状态](../../result/channel_denoising/data/colored_second_50000_20261025/status.json)，设置见[配置](../../src/configs/training/colored_second_20261025.json)，公式及有限一阶误差边界见[推导第8节](../../paper/C-STMP/docs/C_STMP_DERIVATION_20261024.md#8-2026年10月25日独立二阶-score-训练候选)。当前 STMP、DU、C-STMP 导数版本及分类器绑定保持原样；未启动批量接收机实验。

**2026-10-24 三种接收算法已区分：STMP、C-STMP、DU。** 原 STMP 代码、三网络权重及冻结配置保留；十层展开展示名为 DU，旧 `proposed` 标识仍可读取历史计划。新增独立候选 `C_STMP` 使用有色训练的一阶 epoch 200、运行时 `C=vI`、数值导数方差和旧活动分类器。单场景完整 JADCE 配对验证见[报告](../../result/channel_denoising/data/c_stmp_integration_20261024/REPORT.md)，接口与限制见[推导](../../paper/C-STMP/docs/C_STMP_DERIVATION_20261024.md)。本次不恢复已暂停的批量实验。

**2026-10-24 19:00（北京时间）：导频已完成并核验。** 每条件 1000 MC、6 档导频、5 种方法，共 30000 条（5000 复用、25000 新算）；[最终报告](../../result/pilot_frames/data/known_phase_1000_20261023/fixed_readout/REPORT.md)。队列已按用户要求在导频结束后停止，用户数新推断暂未启动。下方此前运行安排保留为历史。

**2026-10-24 用户授权更新：修改结构并重新训练。** 保留 RefineNet 主干与原随机初始化，加入由 C 显式计算的矩阵输入预条件、线性分支和输出缩放；保持原 DSM 目标及 50000/5000 数据、噪声与 200 轮设置。新运行见[训练记录](../../result/channel_denoising/data/colored_preconditioned_50000_matched_20261024/README.md)，公式与配对条件见[实现说明](../../paper/C-STMP/docs/COLORED_PRECONDITIONED_TRAINING_20261024.md)。上一有色候选已保存完整断点并暂停在第 27 轮第 6528 个样本（完成 26 轮）；旧权重保留，新候选从原始随机权重重新训练，不切换冻结模型绑定。

**2026-10-24 用户授权：训练新的有色噪声一阶网络。** 使用原 50000 个训练信道及 5000 个内部验证信道，复用原随机初始化和 200 轮训练设置；仅增加有色噪声及其必要的条件、损失配套。独立配置与运行状态见[训练记录](../../result/channel_denoising/data/colored_score_50000_matched_20261024/README.md)，不切换冻结模型绑定。

**2026-10-24 用户更新：导频完成后暂停。** 当前导频继续运行并完成结果核验与固定门限汇总；用户数实验暂缓，已通过其批次 `STOP.json` 阻止自动启动。此前的接续授权作为历史保留，以此条为当前执行范围。

实验结果统一从 [result/](../../result/README.md) 进入：八项实验各有 `data/` 和 `figures/`。
新实验批次使用 `result/<实验名>/data/<批次>/`，新图使用 `result/<实验名>/figures/<版本>/`。
既有冻结实验和正在运行的主实验保留原始文件身份及旧路径兼容入口；历史工作记录归入 `archive/result_legacy_20261023/`。
本次整理未修改冻结执行入口的默认路径，后续创建计划和绘图时显式指定上述 `--output`。

2026-10-23 用户更新协议：**除已结束的一阶去噪和收敛性实验保留原结果外，其余后续实验均为 1000 MC 场景**，使用固定编号 0–999。
当前 SNR 比较为已知相位、估计噪声，SNR 为 **−4、−2、0、2、4、6、8、10 dB**，
包含 STMP 和四个 baseline；十层展开暂缓。baseline 另补齐编号 1000–1999，
仅用于各方法跨八档 SNR 的单一固定门限校准，不混入比较集。STMP 保持 0.5 门限，
最少60轮、相对变化阈值0.0005；超过前1000场景的旧 STMP 推断输出按用户要求删除。
当前计划、启动命令及进度见[本轮说明](../../result/snr_comparison/data/known_phase_1000_calibration1000_snr10_20261023/README.md)。
用户已授权接续[导频](../../result/pilot_frames/data/known_phase_1000_20261023/README.md)和[用户数](../../result/user_count/data/known_phase_1000_20261023/README.md)：后台队列等待 SNR 完成后依次补跑，各已复用 5000 份结果，分别还需 25000、20000 次推断。
共享场景库仍保留 2000 个种子用于分离校准和后续复用。运行时间实验也改为 1000 场景，
单场景计时重复次数保持 3。旧 2000 场景 SNR 和导频接续计划已停用，原计划及源码快照保留。
下面保留原有默认入口与历史计划说明；本轮采用独立配置，不覆盖旧计划或全局模型绑定。

日常实验统一运行根目录的 **`run_experiments.py`**，也可以直接运行每项实验的独立文件。
Proposed 固定执行十层，使用验证集选中的 epoch 1 权重。未知相位采用已接受的
`message_gem` 实现：先初始化相位，再在第1至9层之后更新相位，每层网络只执行一次。
旧默认计划不包含STMP，本轮独立主实验已显式启用。未知相位已接入经过28个开发输入及20个独立场景验证的修正流程：
从第20轮起每20轮检查，当前输出稳定后才更新相位；相位变化后重新计算匹配的线性查询，
并检查全部用户的观测相位候选。最少80轮、最多600轮，新消息权重仍为0.2；
依据完整相位更新周期的信道、预测信号和活动决策停止。已知相位保留原条件流程及最少150轮。
三网络权重未改变。相位算法的独立验证平均132轮；先前运行优化保留于
[历史运行报告](../../result/candidates/stmp_runtime_20261023/REPORT.md)。当前相位初始化在GPU上以双精度
计算相同目标与梯度，保留3轮坐标扫描、40/500次迭代上限和全部容差。18个保留输入中初始化
平均9.53→3.87秒，活动判决全部相同，最大NMSE退化0.0021 dB；这些是实现回归结果，不是总体性能保证。
浮点运算顺序改变，局部求解轨迹并非逐位一致；一个输入从260轮变为240轮，原600轮未收敛输入仍保留。
本轮100轮输入完整推断约12–14秒，具体计时与局限见[初始化加速报告](../../result/candidates/stmp_initialization_runtime_20261023/REPORT.md)。
当前入口与原相位验证见[相位说明](../../paper/STMP/docs/STMP_PHASE.md)、
[独立相位验证](../../result/candidates/stmp_phase_supported_hypotheses_holdout_20261023/REPORT.md)；
原实现和配置备份见[采用记录](../../result/candidates/stmp_initialization_runtime_20261023/ADOPTION.json)。

当前版本位于 `D:\afdm-gfra`。代码、运行所需权重、共享缓存和 Python 基础环境均在项目内，
使用下方 `.venv\Scripts\python.exe` 启动，无需桌面的旧项目链接或 `D:\afdm-gfra-cpu`。
Windows、NVIDIA 驱动等系统组件仍由操作系统提供。

## 项目目录

```text
src/                       代码、配置与检查
  algorithm/               proposed、STMP、baseline
  evaluation/              每项实验的入口与共用评分、报告
  system/                  物理模型、场景与相位/噪声估计
  networks/                共用网络结构
  training/                训练代码
  configs/experiments/     每项实验一个配置，选择方法和扫描范围
  configs/algorithms.json  算法登记：实现、参数、资源与计算后端
  configs/final/           当前推断配置与模型位置
  tests/                   当前版本检查
  history/                 历史脚本、候选实现与旧测试原件
result/                    八项论文实验的统一入口
  snr_comparison/          SNR 对比；data/、figures/
  pilot_frames/            导频帧数；data/、figures/
  user_count/              用户数量；data/、figures/
  activity_probability/    活动概率；data/、figures/
  cross_channel/           跨信道；data/、figures/
  channel_denoising/       独立去噪；data/、figures/
  runtime_comparison/      运行时间与精度；data/、figures/
  density_ratio_ablation/  密度比消融（暂缓）；data/、figures/
archive/                   历史记录原件；旧路径保留兼容入口
paper/                     论文与研究文档
  STMP/                    STMP 正文、阅读稿、图片、参考文献、研究文档
  C-STMP/                  C-STMP 正文、阅读稿、图片、参考文献、研究文档
  DU/                      DU 正文、阅读稿、图片、参考文献、研究文档
reference/                 参考文献原文、阅读材料与写作资料
```

根目录其他文件是启动入口、项目配置和版本记录；`.venv`、`.git` 等点号目录是运行环境及版本管理文件。

Python 包直接位于 `src`，按职责分为 `algorithm`（算法）、`evaluation`（实验与评分）、
`system`（物理模型与场景）、`networks`（网络结构）、`training`（保留的训练代码）。
文件读写与哈希统一在 `utils.py`，算法构造统一在 `algorithm/registry.py`。
`models.json` 引用唯一的 `final/STMP.json`，生成实验计划时将完整配置保存到计划中。

## 使用

在项目根目录运行：

```powershell
# 实验清单；不进行推断
& .\.venv\Scripts\python.exe -B run_experiments.py list

# 核验全部计划和依赖；不进行推断
& .\.venv\Scripts\python.exe -B run_experiments.py inspect

# 当前版本测试
& .\.venv\Scripts\python.exe -B -m pytest -q

# 查看某项说明
& .\.venv\Scripts\python.exe -B run_experiments.py snr_comparison --help

# 明确启动指定正式实验
& .\.venv\Scripts\python.exe -B run_experiments.py snr_comparison run
```

七项启用实验为 SNR、导频数、用户数、活动概率、跨信道、一阶预训练网络去噪、运行时间与精度。
前六项每工况使用 2000 个共享场景；运行时间使用固定前 20 个场景，每输入重复三次。
标准接收工况为 40 用户、16 导频、0 dB、活动概率 0.1，估计相位和噪声。
创建计划时可用 `--phase-mode known|estimated`、`--noise-mode known|estimated` 独立切换，
用 `--scenes 500` 选择正式清单前 500 个配对场景；默认配置仍保持 2000 场景和双估计。
独立 AWGN 去噪使用给定噪声方差，只检查预训练的一阶网络。旧三网络及其密度比消融暂缓。

每项实验的实现位于 `src/evaluation/experiments/<实验名>.py`，
对应配置为 `src/configs/experiments/<实验名>.json`；修改 `methods` 即可选择参加该实验的算法。
新增算法实现后，在 `src/configs/algorithms.json` 登记一次，再在需要的实验配置里加入其名称。
接入约定和配置示例见 [实验说明](../../src/evaluation/README.md)。

每项实验的论文绘图入口独立放在 `src/evaluation/plots/<实验名>.py`，
共用 `style.py` 保持字体、配色、线型与导出标准一致；仅读取保存的结果，不重跑推断。
输出矢量 PDF/SVG、600 dpi PNG、LaTeX 插图片段和数据来源记录。
八个入口及使用方法见 [论文绘图说明](../../src/evaluation/plots/README.md)。
当前三网络 STMP 图归属 TWC-1，统一存于 `result/<实验名>/figures/`；
`paper/STMP/figures/` 保存本稿图片的实际文件；旧失效链接已归档。DU 对应十层展开稿件。
冻结实验原有报告代码保持不变，新版论文图通过这些入口单独生成。

修改配置后，用 `plan --output <新目录>` 保存新计划，再对该目录执行 `run`；已有计划按其保存的配置执行。
正式计划的扫描条件、方法选择与共享2000场景保持不变。本次只接入新相位流程并准备计划，
不自动启动批量实验。旧 `result/final2000` 保留，不能与新版本混合续跑。
十层选中权重、初始化所用训练二阶矩及完成凭据在 `result/models/proposed_10`，
当前新计划的共享缓存位于 `result/main2000_initialization_runtime_20261023/shared`；上一版缓存保留。
准确路径和 SHA-256 见 [模型配置](../../src/configs/final/models.json)。
Python 基础环境保存在 `.venv/base`；依赖包仍在 `.venv/Lib/site-packages`。

## 导航与复现

- [实验说明](../../src/evaluation/README.md) · [代码导读](../../paper/STMP/docs/CODE_GUIDE.md)
- [相位更新推导](../../paper/STMP/docs/PHASE_MESSAGE_GEM.md) · [本次接入核验](../../result/mainline_message_gem_20261022/AUDIT.json)
- [三份论文](#论文目录) · [术语出处](../../paper/STMP/docs/TERMINOLOGY.md) · [参考资料](../../reference/README.md)
- [当前版本记录](../../FINAL.json) · [目录迁移记录](../../result/layout_20261021/REPORT.md)
- [独立运行迁移核验](../../result/independent_20261021/AUDIT.json) · [迁移前原件](../../result/independent_20261021/before)

历史结果、预测及冻结记录保留原文，嵌入的旧路径按 [迁移映射](../../result/layout_20261021/MAPPING.json) 查找。
原 `MAINLINE.json` 是保留的旧主线身份，当前执行入口以 `FINAL.json` 为准。
`src/history/` 保存历史原件，不作为当前运行入口；旧脚本依赖旧目录结构，复现时需在独立目录恢复原布局。
