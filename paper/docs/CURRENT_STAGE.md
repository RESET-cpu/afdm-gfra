2026-10-21 四目录整理已完成：代码与配置在 `src`，实验和数据在 `result`，研究文档在 `paper/docs`，文献在 `reference`。
当前正式计划见 [计划索引](../../archive/result_legacy_20261023/final2000/READINESS.json)，文件迁移和回放核验见 [目录整理记录](../../archive/result_legacy_20261023/layout_20261021/REPORT.md)。
以下按先后保留整理前的阶段记录。

# 当前阶段

2026-10-21 最终代码整理：日常入口统一为 `run_experiments.py`，十层实现位于 `src/afdm_jadcedd/algorithm/ten_layer/`，
实验调度位于 `src/afdm_jadcedd/evaluation/`。已完成配对输出核验，正式2000场景计划迁移后仍未启动全量推断。
旧三网络及其消融继续暂缓。当前身份见 [FINAL.json](../../FINAL.json)，核验见 [整理记录](../../archive/result_legacy_20261023/final_version_20261021/REPORT.md)。

## 整理前的接入与研究历史

2026-10-21：最终十层训练已完成，固定选用 depth 10 / epoch 1。已接入共享 2000 场景实验，七项入口的小规模检查共 184 条记录通过；正式计划已冻结，尚未开始全量推断。旧三网络及其密度比消融按用户要求暂缓。

运行时间与精度比较替代收敛实验，沿用固定前 20 个共享场景；去噪只检查预训练一阶网络。旧五层、七层等候选的 78 份权重已清理，最终十层和旧三网络保留，历史源码和已保存预测保留。

当前事实及范围见 [接入核验报告](../../archive/result_legacy_20261023/experiment_integration_20261021/REPORT.md)、[正式计划索引](../../result/lstmp_v3_formal2000_20261021/READINESS.json)及[代码导读](CODE_GUIDE.md)。原 `MAINLINE.json` 仍记录原三网络主线，不被替换为新十层记录。

下面保留逐日期研究历史；其中“正在运行”“尚待训练”和旧路径只描述当时状态。

## 2026-10-18 及以前的历史状态

2026-10-18 清理：当前主线及七项实验已通过不含归档的独立运行检查。500 场景完整结果、当前权重/训练数据与冻结主线保留；旧大数组、重复输出及中间训练断点清理。现状见[工作区索引](WORKSPACE_INDEX.md)，证据见[清理报告](../../result/cleanup_20261018/REPORT.md)。下文为各日期的历史状态，不能据其旧路径描述推断文件仍在原位。

2026-10-18：按用户最新指示在500个完整场景结束，17500次推断全部完成并通过指标与记录核验，计算进程已停止。Proposed 全部SNR的NMSE最低，−2～8 dB AER最低；−4 dB AER略高于GNN-ASPL和Off-grid SBL。图例n=500，AER概率值对数轴。见[最终报告](../../archive/result_legacy_20261023/baseline_comparison_500_20261018/REPORT.md)。以下均为各日期历史记录，原600场景安排由本次要求替代。

2026-10-17：用户将当前比较扩大为 600 个场景，SNR 仍为 −4～8 dB，五方法共 21000 次推断。
已冻结独立扩展计划，7 项续跑／复用检查通过。原 200 场景继续运行，完成并通过核验后，
逐文件核对并实际复制其结果到 600 场景目录，再自动运行新增 400 个不同种子的场景。
原生算法、权重、信息条件和门限不变；原 200 场景目录及结果继续保留。
见[600 场景协议](../../src/history/experiments/baseline_comparison_600_20261017/PROTOCOL.md)、
[检查记录](../../result/baseline_comparison_600_20261017/POST_FREEZE_TESTS.txt)和
[续跑状态](../../result/baseline_comparison_600_20261017/CONTINUATION_STATUS.json)。

2026-10-17：Proposed 默认已接入观测驱动的空间协方差 MDL 噪声估计。
20 个场景、160 个配对条件的全部活动判决保持不变，逐 SNR 汇总 NMSE 最大恶化 0.0623 dB，
全部通过事先设定的 0.15 dB / 0.1 个百分点容差，因此按用户要求采用估计噪声。
相位前端保留原两轮完整搜索，优化实现后在 30 个场景、240 个条件中输出逐元素一致；
8 条件的独立计时由平均 6.035 秒降至 4.309 秒。原导频、三网络、条件迭代和门限保持。
曾尝试的局部搜索方案在新场景产生额外漏检，已撤回并保留证据；当前不采用该方案。
默认入口及旧配置重放核验通过，旧入口独立保存于 `docs/history/archive/phase_frontend_public_20261017`。
200 个新物理场景 × 七档 SNR（−4～8 dB）× 五方法的比较正在运行，统一估计相位与噪声，
不包含 L-DAMP。采用证据见[入口核验](../../result/phase_optimization_20261017/PUBLIC_INTEGRATION.json)、
[噪声验收](../../result/phase_optimization_20261017/NOISE_DECISION.json)，
实验进度见[运行状态](../../archive/paper_layout_20261026/original_paper/docs/history/results/baseline_comparison_200_20261017/RUN.json)。下方为历史阶段记录。

2026-10-16：按用户要求先整理代码与归档，77 个历史实验目录及旧记录入口移至独立归档，
20 个当前实验、训练或测试依赖目录保留原位。生产源码、配置、权重与已有结果保持内容，
首页、实验索引和结果索引已按当前估计相位主线更新；本次未启动历史已知相位的 8 dB 补跑。
原路径、文件身份、恢复入口及核验见[整理报告](../../archive/paper_layout_20261026/original_paper/docs/history/results/workspace_cleanup_20261016/REPORT.md)和
[归档说明](../../archive/paper_layout_20261026/original_paper/docs/history/archive/workspace_cleanup_20261016/README.md)。下方研究安排为各自日期的历史记录。

2026-10-16：原导频八档 SNR 的十场景配对实验完成，五方法共 400 次推断，0 失败、0 缺失。
各档按原导频下接收功率精确标定，所有方法使用相同观测、估计相位并获得准确物理噪声方差；
GAMP-SBL 保留其原有噪声精度更新。Proposed 的完整信道 NMSE 在八档均最低，
漏检数按 −4、−2、0、2、4、6、8、10 dB 为 1、1、1、0、0、0、0、1，虚警全部为零。
10 dB 的漏检经完整入口重放逐元素复现；此前相同热噪声导频核查的对应样本实际为 10.30855 dB，
两次观测及重新计算的相位估计不同，旧参考点的零漏检不能转用于本批精确 10 dB。
全部输出与输入／冻结源码核验通过，主线算法和权重未改动，详见
[八点结果](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_original_snr8_10_20261016/FINDINGS.md)及
[完成核验](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_original_snr8_10_20261016/COMPLETION_CHECK.json)。

2026-10-16：用户正式确定 Proposed 主线为原 `PartialDFTPilot` 导频、原三网络、原迭代及 0.5 门限，
本轮算法探索结束。相位仍由观测估计，Proposed 使用给定热噪声方差，阻尼保持 0.2；
后续正式实验 SNR 扩展为 −4、−2、0、2、4、6、8、10 dB，按原导频下无噪接收功率标定。
后续范围为该版本的复现、baseline 配对对照和结果／论文整理。
进一步算法探索须经用户重新明确提出；下方候选的续训和继续探索安排保留为历史记录。
确认时，本会话两个子任务均已完成，未发现运行中的实验进程。
见[主线说明](../../delete/paper_flatten_20261107/paper/STMP/docs/PROPOSED_MAINLINE.md)与[本次决定](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_mainline_confirmation_20261016/DECISION.json)。

2026-10-16：原导频补充核查完成，同十场景的 8、10 dB 参考点均为 0 次漏检、0 次虚警，
二十次推断全部收敛，酉导频对应为 0/3、0/1。保持相同热噪声后的实际 SNR 偏移不超过 0.309 dB。
原导频完整 NMSE 分别为 −16.440、−16.865 dB；相对酉导频，8 dB 改善 0.214 dB，10 dB 退化 0.063 dB。
这批原导频 4、6、8、10 dB 参考点均无活动检测错误；目前结果为 Proposed 的导频配对核查。
见[补充结果](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_polar_snr6_10_20261016/original_pilot_8_10/SUMMARY.json)与
[输入及指标复核](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_polar_snr6_10_20261016/original_pilot_8_10/VERIFICATION.json)。

2026-10-16：按用户选择，Proposed 后续采用原 `PartialDFTPilot` 导频、原三网络、原迭代和原门限，
SNR 点保持 0、2、4、6、8、10 dB。默认物理生成入口及冻结主线已与该选择一致。
最新十场景在 4、6 dB 参考点的二十个原导频配对条件全部完成并收敛，两档均为 0 次漏检、0 次虚警，
酉导频对应为 0/1、0/4。保持相同热噪声后的原导频实际接收 SNR 偏移为 −0.240 至 +0.309 dB。
旧面板和新虚警样例共四次重放逐元素一致，未发现网络、核心迭代或调用入口用错；
酉导频结果保留为对照。本轮核查没有重跑原导频六方法的全部六档 SNR。
见[主线说明](../../delete/paper_flatten_20261107/paper/STMP/docs/PROPOSED_MAINLINE.md)、[核查结果](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_polar_snr6_10_20261016/version_audit/SUMMARY.json)。

2026-10-16：四个 baseline 的 1000 场景正式实验已完成，SOMP、GAMP-SBL、GNN-ASPL、off-grid SBL 覆盖六档 SNR。
24,000 次推断全部保存，0 运行失败、0 缺失，1000 个场景完整配对；相位与噪声均由观测估计。
运行耗时约 3 小时 55 分钟，冻结资产核验通过。Off-grid SBL 的完整信道 NMSE 在各档最低，
GNN-ASPL 在 −2～6 dB 的 AER 最低；这是本批经验结果。预算停止的输出均计入，未宣称全部算法收敛。
详见[完整报告](../../archive/paper_layout_20261026/original_paper/docs/history/results/baselines_1000_20261015/REPORT.md)及[完成核验](../../archive/paper_layout_20261026/original_paper/docs/history/results/baselines_1000_20261015/COMPLETION_CHECK.json)。

2026-10-16：同先验密度比值与导数联合监督的首个800步候选已完成，5个检查点均未满足原资格标准。
最终选择集BCE为0.06706，原版为0.05097；导数均值MSE为0.24944，原版为1.80992，
说明均值指标改善没有同时带来合格的分类表现。未生成选中模型，未使用确认集，未进入完整接收机。
全部统计独立重算及10输入CPU双精度重放通过，原失败和加法项拟合诊断保存。
后续候选在独立目录按1/(s+v)归一化均值损失，从固定800步权重开始新优化，验收仍用原未加权指标。
主线979个冻结文件及56个当前核心文件再次校验一致。
见[800步报告](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_probability_consistency_20261016/candidate_training/REPORT.md)、
[后续协议](../../archive/paper_layout_20261026/original_paper/docs/history/archive/workspace_cleanup_20261016/workspace/experiments/proposed_probability_consistency_20261016/WEIGHTED_CANDIDATE_PROTOCOL.md)及
[后续进度](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_probability_consistency_20261016/weighted_candidate_training/STATUS.json)。

2026-10-16：三网络概率一致性完整面板已完成，10240条记录全部独立重算，原判决没有改变。
匹配Gaussian末态控制中，原first的活动条件均值NMSE为−9.22至−16.95 dB，
活动分类器总梯度导出的均值为+3.68至+0.31 dB；局部网络不一致不能全归于实际查询非Gaussian。
64个CPU双精度参考中，均值、第一导数和原second均通过既定精度门槛；
Hessian有7/64组超出1e−3，最大1.17%，所有被查方向符号一致。总复核保留FAIL，未放宽门槛。
既有双精度差分确认的负曲率结论仍成立，但全量曲率不能宣称同等精度。
新候选的联合监督目标与参数梯度预检已通过，按独立协议开展训练、选择和确认；原主线不变。
见[完整报告](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_probability_consistency_20261016/REPORT.md)、
[分项复核](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_probability_consistency_20261016/VERIFICATION_BREAKDOWN.json)及
[候选协议](../../archive/paper_layout_20261026/original_paper/docs/history/archive/workspace_cleanup_20261016/workspace/experiments/proposed_probability_consistency_20261016/CANDIDATE_PROTOCOL.md)。

2026-10-16：三网络概率一致性的完整诊断面板已启动，复用128个查询快照的全部40用户，
并增加匹配方差的离线Gaussian控制，共10240条记录；当前进度见[状态](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_probability_consistency_20261016/STATUS.json)。
两个预选查询的双精度独立检查已经确认：一个活动用户在实际及Gaussian控制下均有负证据曲率，
原first在四个被查输入上的交叉导数也不对称；不能将全部不一致归于实际查询的非Gaussian误差。
这些是局部函数证据，不是完整接收机因果结论或修复成绩；所有失败和正向对照均保留。
同先验下的分类值与导数联合监督目标已完成公式核验，尚未训练或接入循环。
见[已验证的局部结果](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_probability_consistency_20261016/LOCAL_CHECKS.md)。

2026-10-16：主线冻结包重新校验通过，979个冻结文件及56个当前Proposed核心文件身份均一致。
三网络概率一致性诊断的数值预检已通过：排除内部默认float32累加器对双精度差分的影响，
并记录ELU零点跨越导致的粗步长二阶差分误差；两次失败及步长扫描完整保留。
两个固定查询的局部导数差分误差低于1e−4，MPS与双精度参考的最大相对差约5.46e−5。
本阶段尚未运行10240条记录的完整诊断面板，也未选择或接入任何接收机修正。
见[数值预检](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_probability_consistency_20261016/PREFLIGHT.json)、
[范围与状态](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_probability_consistency_20261016/STATUS.json)和
[主线复核](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_mainline_freeze_20261015/REVERIFICATION_20261016.json)。

2026-10-16：活动混合消息的连续小系统核验及原末态联合诊断完成。
432条件、1152用户的混合局部后验与全枚举吻合；1151个正标量site拟合通过，1例正精度约束不相容已独立确认。
随后固定原两个困难末态的全部40用户拟合混合因子，四链联合采样仍为3 MD、0 FA，80个判决逐位不变。
12项确定性测试、全量后验/保留状态独立复核及主线身份检查通过；数值参考警告及显式收缩复核均保留。
尚未得到完整接收机修正；下一步核查原三网络的均值、方差与活动密度比是否对应同一局部概率对象。
见[本轮报告](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_mixture_message_20261016/REPORT.md)与[下一步](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_mixture_message_20261016/NEXT_ACTION.md)。

2026-10-16：原Proposed的实际查询及其他用户反馈误差分布核验完成一轮。
8个历史场景×4 SNR×4阶段的128快照包含全部用户：平均误差功率和四阶矩可接近Gaussian，
但信号方向偏差、输入轴相关和用户间交叉项仍明显；保持干扰二阶矩的oracle重抽反而产生大量虚警。
实际查询条件修正的均值/活动训练未通过验证，风险校准单独进入闭环后，两个困难条件的错误由3增至39，候选淘汰。
数学复审进一步区分Gaussian局部因子的矩与实际轨迹监督条件矩，后者不能直接沿用原因子相除。
原主线与冻结副本保持不变；尚无通过完整闭环及独立确认的修正，整体目标继续。
见[本轮完整报告](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_query_distribution_20261015/REPORT.md)及
[数学接口复审](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_query_distribution_20261015/MATHEMATICAL_INTERFACE_REVIEW.md)。

2026-10-15：按用户要求，将已有结果对应的原版 Proposed 固定为后续研究主线。
独立副本保存源码、配置、三份权重及 10 场景 × 六档 SNR 的全部输入、输出、迭代记录和警告。
56 个当前 Proposed 源码/配置/资产身份一致；冻结副本在 MPS 上重放 scene000/0 dB，
所有输出数组与原结果逐元素完全一致，活动判决、88 次迭代及停止原因一致。
后续候选使用独立路径，切换时保留旧版；Git 自动快照保持停用。
版本与验证入口见 [Proposed 主线说明](../../delete/paper_flatten_20261107/paper/STMP/docs/PROPOSED_MAINLINE.md) 和
[冻结副本](../../archive/proposed_mainline_20261015/README.md)。

2026-10-15：原TMP内保留A→B用户块矩阵信息的闭环初筛完成，原Proposed保持默认。
匹配均值网络适配1200步、活动与方差输出各600步后，固定独立验证选出的模型，
仅新增scene003/007、−4 dB的两次完整运行：原版MD=3、FA=0、AER=3.75%，候选MD=4、FA=0、AER=5.00%。
候选110/234轮收敛，无越界、正精度失败或方差下限触发；完整NMSE为−3.904 dB，原版−5.758 dB。
15项测试、终点Gaussian代数/停止/指标独立复核及20个原核心文件身份检查通过。
真值辅助的固定J Gaussian局部输入对照中，8次噪声抽样均检出所有用户；实际四个漏检的方向系数仅0.573–0.675，
尽管白化误差平均能量接近1。这支持实际消息分布失配的诊断，尚未定位具体来源，也不构成实际AER改善。
不扩大本候选或延长训练；代码、独立权重、全部结果与失败记录均保留，见[完整初筛报告](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_cai_relaxation_20261015/matrix_receiver/REPORT.md)。

2026-10-15：按用户反馈，Proposed研究回到原TMP迭代内逐项放宽近似，以AER为主。
原消息核查完成：两个保存末态的完整分解表明，三个漏检不能统一归因为反馈过度抵消；
其中一人的其他用户反馈沿目标方向略有帮助。直接自身反馈贡献仅约+0.0005，
完整用户块求逆所得平均工作方差至少167，原查询约20，不能直接交给旧标量AWGN网络。
已推导并实现保留A→B用户块(J,B)、B→A仍共同标量的消息内核，7项测试及80个真实块核对通过。
该前置核查阶段仅完成消息内核；后续匹配非线性、矩阵阻尼及完整接收机初筛见本页首条。
第三至第五项末端候选保留为历史对照，当前不据其扩展积分路径训练。
见[消息核查报告](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_cai_relaxation_20261015/native_message_audit/REPORT.md)及
[单项矩阵消息设计](../../archive/paper_layout_20261026/original_paper/docs/history/archive/workspace_cleanup_20261016/workspace/experiments/proposed_cai_relaxation_20261015/MATRIX_MESSAGE_DESIGN.md)。

2026-10-15：SOMP、GAMP-SBL、GNN-ASPL、off-grid SBL 的 1000 场景实验已启动。
同一批物理场景覆盖 −4、−2、0、2、4、6 dB，共 24,000 次推断；相位和噪声均由观测估计。
配置、权重和门限固定，四个 CPU 进程运行，保留输入、逐例统计和失败记录，支持续跑。
冻结副本复现与保存/续跑/统计核验均通过；完成后汇总场景配对 bootstrap 区间。
当前状态见[运行进度](../../archive/paper_layout_20261026/original_paper/docs/history/results/baselines_1000_20261015/STATUS.json)，结果见[四基线 1000 场景实验](../../archive/paper_layout_20261026/original_paper/docs/history/results/baselines_1000_20261015/REPORT.md)。

2026-10-15：第五项近似检验完成。复用两个原末态，以幂后验条件矩积分替代末端活动证据，
未新增完整接收机运行。旧网络在积分路径上出现负条件方差，起点先验积分和16/32点求积检查也未通过；
原始候选MD由3增至15、FA仍0、AER由3.75%升至18.75%，不采用。
12项确定性检查、直接网络矩换算及独立积分复核通过；8个合成查询的匹配噪声控制支持积分查询分布失配解释。
原Proposed及分类器保持默认，候选和全部失败数据保存；见[第五项报告](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_cai_relaxation_20261015/step5/REPORT.md)。

2026-10-15：第四项近似检验完成。原Proposed末端为每个目标按公开消息选一名伙伴，
保留两用户的四种离散活动组合，更新活动概率及条件/混合矩。
同两个预选困难条件、4次完整运行仍为MD=3、FA=0、AER=3.75%，与原版及第三项一致。
19项确定性检查和312个状态的独立积分核验通过；无额外网络调用，末端总开销约0.651秒。
本项不接入每轮反馈，保留候选与失败结果；局部求和仍依赖Gaussian工作因子，不能据此否定所有联合推断。
见[第四项报告](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_cai_relaxation_20261015/step4/REPORT.md)。

2026-10-15：其余四个 baseline 的噪声核验完成。Off-grid SBL 弱先验下的持续低估已通过观测估计的 Gamma 先验修正，保留 Wei 后验更新、原噪声初值及 120 轮预算；该先验与原文设置不同，属于项目适配。
原六条件的噪声估计/真值由 72.4%–83.8% 改为 91.5%–96.9%，完整信道 NMSE −6.060→−6.877 dB，活动错误均为零。
两个新场景×三 SNR 中比值为 88.4%–96.7%，估计/准确噪声参考均为 3 次漏检、0 虚警；仍有偏差和预算停止。
SOMP/GNN-ASPL 未发现同类迭代低估；L-DAMP 保留残差等效噪声估计，检查其单位与输入物理噪声独立性。
75 项测试、37 次固定验证推断完成，原生内核、权重与门限保持；详见[四基线核验报告](../../archive/paper_layout_20261026/original_paper/docs/history/results/baseline_noise_audit_20261015/REPORT.md)。

2026-10-15：第三项近似检验完成。原Proposed结束后追加一次保留单用户矩阵似然的
活动/信道矩更新，同两个预选低SNR条件的4次运行仍为MD=3、FA=0、AER=3.75%。
三个原漏检用户的活动概率进一步降低；该局部候选不进入每轮反馈，不扩大实验。
9项确定性检查、四次原循环复现、80项证据的独立积分复核通过，原版与候选均保存。
这只是局部观测因子的替换，其他用户Gaussian反馈和条件Gaussian密度近似仍在；
见[第三项报告](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_cai_relaxation_20261015/step3/REPORT.md)。

2026-10-15：GAMP 的噪声低估修正已接入默认入口。Gamma 先验保留既有 c=1+LM，
rate 改为 LM 乘空间协方差噪声估计；初始化、字典、门限及原核函数保持。
原两个场景×三档 SNR 中，虚警 48→0，AER 20%→0.417%，完整信道 NMSE −0.644→−3.917 dB。
两个新场景×三档 SNR 的估计噪声分支无活动错误，噪声估计为真值的约84%–90%；这是有限验证，仍有向下偏差。
69 项测试、三次噪声字段独立性全流程核验通过；详见 [GAMP 修正报告](../../archive/paper_layout_20261026/original_paper/docs/history/results/gamp_noise_20261015/REPORT.md)。

2026-10-15：按AER目标完成第二项近似放宽的4次初筛。将共同反馈方差改为逐用户标量，
在预先选定的两个估计相位困难条件（scene003、scene007，−4 dB）中，原版及候选均
漏检3个、虚警0个，AER均3.75%；原版迭代75/229轮，候选76/230轮。
8项确定性测试和两次原版历史结果核对通过，运行期间代码/权重身份未变。
本项未降低AER，停止扩大方差候选，保存原版与候选用于比较；该小面板仅为开发证据。
见[第二项结果](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_cai_relaxation_20261015/step2/REPORT.md)及
[近似清单](../../delete/paper_flatten_20261107/paper/STMP/docs/PROPOSED_APPROXIMATIONS.md)。

2026-10-15：五个 baseline 默认已改为观测噪声估计；Proposed 本轮仍使用准确噪声。
GAMP 按原文后验更新、off-grid SBL 恢复噪声学习，SOMP/GNN-ASPL 补充空间协方差估计，L-DAMP 沿用原残差等效噪声。
67 项相关测试、15 次噪声字段独立性全流程检查及 60 个小规模配对输出完成。
首版中 GAMP 噪声估计仅为真值的 0.62%–1.83%，AER 为 20%；该历史失败完整保留，当前默认已按本页 GAMP 修正条目更新。
Off-grid SBL 的方差约为真值的 72%–84%，仍达到原迭代预算。
原十场景图属于供给准确噪声的历史条件；公式、适配范围和完整结果见 [噪声说明](BASELINE_NOISE.md)及[核验报告](../../archive/paper_layout_20261026/original_paper/docs/history/results/baseline_noise_20261015/REPORT.md)。

2026-10-15：按用户最新方向，在 Cai 的 TMP 结构内逐项放宽 Proposed 的近似，
对应关系见 [PROPOSED_APPROXIMATIONS](../../delete/paper_flatten_20261107/paper/STMP/docs/PROPOSED_APPROXIMATIONS.md)。
第一项延后跨用户二阶方差平均，复用原网络和原外信息循环。
用户认为72次设计过大后，批次已停止：35次完成、17个完整配对，双方AER均为0。
用户随后明确以降低AER为目标，NMSE只作辅助记录；本批零错误条件不能检验检测改善。
已有未知相位困难面板该候选仍为5次漏检、0虚警，尚未显示AER收益；候选保留，默认版暂不替换。
后续每项先2个原版已有检测错误的条件×2版本、最多4次运行，优先复用已有输入与结果；本次原计划未完成，
详见[阶段记录](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_cai_relaxation_20261015/step1/REPORT.md)。默认接收机与权重保持原样。

2026-10-15：主线信息条件为未知跨帧相位。默认 `simulate` 提供原始导频，`run/baseline` 从公开观测估计相位；Proposed 使用既有 `proposed_unknown_phase.json`，五个 baseline 经共用物理相位前端调用各自条件接收机。准确已知相位由 `--phase-mode known` 显式指定，作为理想参考。主要比较实际估计条件下的 NMSE、AER，以及相同场景中相对理想信息条件的差距。入口核验见 `docs/history/results/estimated_phase_mainline_20261015/`。

2026-10-15：未知相位 Proposed 保留“估计跨帧相位，再执行原推断过程与原活动分类器”的两阶段流程，
入口为 [proposed_unknown_phase.json](../../src/configs/proposed_unknown_phase.json)。各 SNR 共用原三网络、
0.5 活动概率门限、0.2 阻尼及原停止规则。配置、权重和核心实现的核对记录见
[MAINLINE_SELECTION.json](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_low_snr_20261015/MAINLINE_SELECTION.json)。
本轮低 SNR 诊断及候选比较作为实验记录保留，结果与适用范围见
[PROPOSED_UNKNOWN_PHASE](../../delete/paper_flatten_20261107/paper/STMP/docs/PROPOSED_UNKNOWN_PHASE.md)。

2026-10-15：参考 Shen §III-C 的相位更新思路已完成可选实现，入口为 [proposed_iterative_phase.json](../../src/configs/proposed_iterative_phase.json)。保留每用户 exp(jq beta_k) 约束，使用有效信道软后验均值更新相位并重新运行原 Proposed，最多两次相位更新。原三网络、门限和条件推断规则保持不变。
同十场景、六档 SNR 的 60 条结果全部保存；0～6 dB NMSE 改善 0.155～0.436 dB，AER 不变；−4、−2 dB 的 NMSE 分别退化 0.424、0.595 dB，AER 分别由 1.25%、0.50% 升至 1.50%、1.25%。这里比较的是两种估计相位流程，原两阶段估计配置用于当前六方法面板。
用户提出停止条件问题后，单独重放一个困难条件：最终相位固定时，仅放宽活动权重残差门限至 1e-3，可在第 286 轮停止，比第 600 轮 NMSE 低 1.036 dB，漏检由 2 次降为 1 次。该诊断说明未满足旧停止门限不能直接视为性能失败；它尚不等于采用新停止规则完整重跑外迭代。详见 [相位迭代报告](../../archive/paper_layout_20261026/original_paper/docs/history/results/shen_phase_update_20261015/evaluation/REPORT.md)。

2026-10-15：Proposed 已接入观测驱动的跨帧相位估计，入口为 [proposed_unknown_phase.json](../../src/configs/proposed_unknown_phase.json)。与五 baseline 使用同一批十个物理场景、六档 SNR，新增 60 次 Proposed 推断均达到原停止条件，输入与全部相位结果一致性检查、指标复核及固定条件复跑通过。
本批未知相位结果中，Proposed 的完整信道 NMSE 比各档最强 baseline（Off-grid SBL）低 2.837–5.344 dB；0 dB 为 −10.806 dB、AER 0.25%。−4、−2 dB 的 AER 分别为 1.25%、0.50%，仍高于 Off-grid SBL 的 0.50%、0.25%；0 dB 及以上 AER 为 0.25%，与本批最优值持平。
接收机先估计相位再执行原三网络与消息传递，配置和权重在本轮固定。主要评价 NMSE 与 AER；具体输入、公式范围与完整结果见 [实现说明](../../delete/paper_flatten_20261107/paper/STMP/docs/PROPOSED_UNKNOWN_PHASE.md)、[十场景报告](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_unknown_phase_20261015/evaluation/REPORT.md)和[比较图](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_unknown_phase_20261015/evaluation/comparison.png)。

L-DAMP 实现与训练复审已完成，当前保留经有限规模验证的逐波束五段版本。联合波束候选失败及原因、公共 NMSE 评分修正见 `results/ldamp_implementation_20261014/REVIEW_20261014.md`。

2026-10-14：主线为 Proposed 加五个 baseline，共六种方法：**Proposed、SOMP、GAMP-SBL MMV、GNN-ASPL、off-grid SBL、L-DAMP**。

Proposed 为旧三网络和 LMMSE/外信息消息传递接收机，当前默认新值权重为0.2，沿用原初始化和停止规则。原图的0.1配置保存在 [proposed_figure_20261009.json](../../src/configs/proposed_figure_20261009.json)，历史图表继续对应其原始配置。其他原图方法保留已核验的实现、权重与配置；SBL 为原图120次迭代版本。

Proposed 的[各轮一致推断规则试验](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_uniform_inference_20261014/REPORT.md)已完成：4个开发条件筛查后，固定参数比较2个新物理场景×3个SNR。原接收机新值权重0.2的汇总NMSE为−13.507 dB（0.1为−13.469 dB），均无活动错误，score调用减少42.2%。依据该小规模配对结果，默认配置现采用0.2；选择与核验记录见 [DEFAULT_SELECTION.json](../../result/proposed_default_20261014/DEFAULT_SELECTION.json)。旧网络和接收机实现不变，历史结果不改写为0.2的结果。

L-DAMP 已替换为经原稿、作者代码和权重数值核对后的复数 AFDM 适配：固定可逆信道表示、逐波束共享两通道 DnCNN、五个噪声区间、十轮迭代及复数矩阵 Onsager 校正。训练和推断入口均已接入，配置状态为 `VALIDATED_PAIRED_10_SCENES`。原失败实现、权重和结果完整保留，详见[实现报告](../../result/ldamp_implementation_20261014/REFERENCE_REPORT.md)。

修正活动能量判决后，冻结接收机在另 16 个全新物理场景 × 六 SNR 上验证通过；0 dB 全信道 NMSE 为 −4.592 dB、活动错误率为 0.625%。按用户要求，统一比较使用原面板固定前 10 个场景 × 六 SNR，L-DAMP 的 0 dB 指标为 −4.216 dB、0.5%；高 SNR 接近 GNN-ASPL，仍明显弱于 off-grid SBL 和原冻结 Proposed。见[比较图](../../result/ldamp_implementation_20261014/paired_comparison_10/comparison.png)。扩大运行已停止，191 条完成记录保留。

六个 SNR 复用同一批物理场景，统计区间按场景重采样；10 场景用于本轮有限规模比较。真实查询的相关误差、结构化 AFDM 感知矩阵及噪声范围外调用仍是适用性限制，不能宣称独立高斯 AMP 的收敛保证。最低效用检查、数学核对及相对性能比较分别报告。

- [本轮诊断与训练对照](../../archive/paper_layout_20261026/original_paper/docs/history/results/ldamp_diagnosis_20261014/REPORT.md) · [原结果复核](../../archive/paper_layout_20261026/original_paper/docs/history/results/ldamp_diagnosis_20261014/EXISTING_BASELINE_AUDIT.json)
- [原论文、作者代码与设计适配对照](../../archive/paper_layout_20261026/original_paper/docs/history/results/ldamp_paper_audit_20261014/REPORT.md) · [He 原文 PDF](../../reference/ldamp_review_20261014/he2018_ldamp.pdf)
- [历史续训记录](../../archive/paper_layout_20261026/original_paper/docs/history/results/ldamp_20261014/continuation/STATUS.json) · [历史逐轮记录](../../archive/paper_layout_20261026/original_paper/docs/history/results/ldamp_20261014/continuation/training/STATUS.json)
- [L-DAMP 实现与来源](../../delete/paper_flatten_20261107/paper/STMP/docs/LDAMP.md)
- [原比较图及汇总](../../result/baseline_comparison_20261012/summary.json) · [原图复现核验](../../archive/paper_layout_20261026/original_paper/docs/history/results/figure_reproduction_20261014/REPORT.md)
- [原五方法代码整理核验](../../archive/paper_layout_20261026/original_paper/docs/history/results/final_mainline_20261014/VERIFICATION.json)

当前比较规模、配置版本与验证证据均记录于 MAINLINE.json。
随后完成的 L-DAMP 联合波束有效误差方差匹配对照，没有改变物理接收噪声模型；五段继续训练改善了合成去噪，但最高区间及完整递推仍失败，未替换默认逐波束版本，见[后续对照](../../archive/paper_layout_20261026/original_paper/docs/history/results/ldamp_noise_matching_20261014/STATUS.json)。
其他方法与参数版本见 [研究入口](RESEARCH.md)。历史实验和清理记录继续保留。

2026-10-15：针对近似AWGN查询的顺序实施已完成当前一轮开发筛查：一般去噪器D-OAMP、两种导频对照、每轮空间协方差处理及酉导频组合，共4个物理条件、32次接收机运行。空间处理改善早期误差统计，但增加噪声并损失完整性能，没有候选通过质量要求，未替换主线。见[结果、图和失败记录](../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_awgn_20261014/REPORT.md)。有色噪声条件去噪与矩阵反馈的后续设计已记录，尚未训练或验证。
