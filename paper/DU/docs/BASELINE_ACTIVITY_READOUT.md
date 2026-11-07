# 活动判决的原文与实现

> **当前用户决定（2026-10-25）：** 用户以历史 AER 图确认，后续四个 baseline 采用 `baseline_calibration_reuse1000_20261023/FROZEN_READOUT.json` 的完整既有规则：Off-grid SBL、SOMP 按估计 SNR 分档；GNN-ASPL、GAMP-SBL 固定门限。见 [默认入口](../../../result/BASELINE_READOUT.json) 与 [精确门限、边界规则、验证及用户数接续](../../../result/snr_comparison/data/adopted_baseline_readout_20261025/README.md)。原研究 0–499 拟合、500–999 选择；当前同编号场景存在重叠，仍须披露，不能改称独立测试。此次是明确授权后的独立后处理切换，不覆盖旧冻结计划和已完成结果。下面各日期的执行决定与研究建议保留为历史；具体数值不表述成原论文公开参数。

> **最新执行决定（2026-10-23 23:14 CST）：** 主实验达到 1500 个 baseline 场景后安全暂停，
> 额外种子校准同时停止。改用主实验固定编号 1000–1499 的 500 场景校准四个 baseline 的固定门限，
> 然后对编号 0–999 的 1000 场景重新判决和绘图；STMP 保持 0.5。
> 记录见 [baseline_fixed_last500_20261023](../../../result/snr_comparison/data/baseline_fixed_last500_20261023/README.md)。
> 本轮拟合与绘图样本互不重叠，既往查看记录仍保留；不将回顾性结果描述成完全盲态测试。

> **最新执行决定（2026-10-23 23:08 CST）：** 用户要求额外场景校准，所有方法使用跨 SNR 固定门限。
> 当前执行 [baseline_fixed_independent_20261023](../../../result/snr_comparison/data/baseline_fixed_independent_20261023/README.md)：
> 四个 baseline 在额外 500 场景拟合各自一个标量，在另 500 场景验证，不再用验证集选择分档策略；STMP 保持 0.5。
> 旧的主实验前 1000 场景拟合及混合门限选择已被替代，保存为历史诊断。
> 运行中的主实验原始输出与配置仍冻结，完成校准后通过保存的分数重新判决；以下研究与历史记录保留。

> **2026-10-23 当前状态更正：** 下文是10月9日的历史记录，其中“所有SNR/网格保持同值”不描述当前主实验。现行四个 baseline 均采用估计 SNR 最近节点门限；前三者见 `src/configs/final/readout_policy.json`，off-grid SBL 见 `src/configs/final/offgrid_readout_policy.json`。Ding 式(27)只给出了统计量及门限符号，没有公开本项目的分档规则。当前来源、训练差异、固定门限候选和800场景离线核验见[四基线GFRA核验](BASELINE_GFRA_AUDIT_20261023.md)。保留以下原始记录，不据此覆盖冻结实验。

2026-10-23按用户要求另存了[GNN恢复历史固定门限的对照](../../../result/snr_comparison/data/candidates/gnn_ding_eq27_fixed_20261023/REPORT.md)：保持式(27)，使用早期独立校准记录的η=0.0878782570362091，移除SNR分档。800场景六档总错误517→866；这只是旧门限跨权重/场景转用的结果，不能称为Ding公开门限，也未替换运行中主实验。

## 2026年10月23日 固定门限与随噪声变化的门限

**核查结论：文献不支持“所有方法必须跨 SNR 固定数值”，也不支持“分档一定更合理”。应固定的是完整判决规则和校准程序；数值是否随噪声、有效误差或其他可观测量变化，取决于统计量及模型。** 对本项目目前的四个 baseline，在独立校准集上为每种方法确定一个跨 SNR 固定值，适合作为透明且参数少的主比较方案；这是项目方法学建议，不是所有 GFRA 论文共同规定。现行最近 SNR 节点查表有可能成为有效的自适应实现，但其性能和来源尚需独立验证。

本次针对门限的核查覆盖九篇原始论文，结合作者存档、出版社全文、arXiv、Semantic Scholar 元数据及项目现有 PDF。证据与本地文件哈希见 [EVIDENCE.json](../../../reference/reviews/activity_threshold_review_20261023/EVIDENCE.json)；新增来源见 [FETCH_MANIFEST.json](../../../reference/reviews/activity_threshold_review_20261023/FETCH_MANIFEST.json)。这是有范围的文献核查，不以检索结果数量判断主流，也不宣称穷尽全部研究。

### 原文到底固定了什么

页码和公式号以所链接 PDF 版本为准；自动生成 HTML 的公式编号有时不同。

| 文献 | 判决与原文位置 | 能支持的判断 |
|---|---|---|
| Zhou 等，TWC 2023，GF NOMA-OTFS/SOMP | [PDF p.10，§IV-C 式(27)、脚注3](https://arxiv.org/pdf/2201.02084v2#page=10)：用户能量与最大用户能量乘以 β 比较，给出 β=0.1。 | 固定的是相对门限系数，绝对能量门限仍随接收结果变化。0.1 是该系统的经验设置，不保证移植到 AFDM 后最优。SOMP 残差停止门限另依赖噪声，不能混为活动门限。 |
| Zhaoji Zhang 等，TVT 2019，DNN-MP-BSBL | [§II-B、§III-D，PDF p.10 Table IV](https://arxiv.org/pdf/1910.02953v1#page=10)：用户块精度的倒数与 0.1 比较，同时估计噪声精度。 | 直接 GFRA 中存在固定的用户方差门限；它不是归一化能量的 0.1。 |
| Ke 等，TSP 2020，GMMV-AMP | [PDF p.7，§III-B 式(39)–(41)、脚注3](https://arxiv.org/pdf/1906.09867v4#page=7)：空间域 BI-AD 先以 0.5 二值化后验指标，再以 0.9 判断跨观测占比。 | 固定后验判决参数有直接先例；需保留其用户共同稀疏模型和投票过程，不可只摘取 0.5。 |
| Liu、Yu，TSP 2018，vector AMP | [PDF p.6，§III-E Definition 1、式(30)后的门限](https://arxiv.org/pdf/1706.06438v2#page=6)：门限由有效方差、用户大尺度系数、天线数确定。 | 随有效噪声和用户变化的解析门限有直接理论依据；不是按绘图横坐标拟合数表。 |
| Quayum 等，ICC 2018，GF 导频检测 | [PDF p.4，§IV-A 式(9)、Fig.5](https://personal.utdallas.edu/~hxm025000/GrantFreePilots_ICC2018.pdf#page=4)：从正确检测概率推导最优门限，明确比较固定目标 SNR 与瞬时 SNR 估计驱动的动态门限。 | 动态门限在该模型中优于固定值；不能推广为任意 SNR 分档表均有效。其任务是导频非零位置/碰撞检测，不是当前四种 AFDM 恢复器。 |
| Shen 等，TWC 2025，MRF-MP-GAMP | [PDF p.7，§III-A 式(21)](https://arxiv.org/pdf/2412.20806v1#page=7)：用户聚合能量与预设经验门限比较。 | 已核实能量判决，但未找到支持本项目六档表的数值或校准说明。一个门限符号不足以断言跨全部 SNR 数值不变。 |
| Ding 等，TVT 2026，GNN-ASPL | [本地 PDF p.4 式(27)、p.5 §IV-A](../../../reference/literature/ding2026.pdf)，[作者机构记录](https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/Learning-Sparsity-Pattern-An-Adaptive-Joint/991155194002346?institution=44SUR_INST)：归一化系数块能量与 η 比较。 | 原文未给 η 数值、SNR 表和校准流程；逐 SNR 训练网络的说明不能转述成逐 SNR 门限规定。 |
| Chang Cai 等，JSAC 2026，STMP | [§III-B2 式(29)–(31)](https://arxiv.org/html/2506.00581v2#S3.SS2)，[正式稿 PDF p.7](../../../reference/literature/cai2026.pdf)：对用户活动后验概率设门限，后验包含先验和消息方差。 | 概率门限与归一化能量门限应分开；固定概率门限不表示判决忽略噪声。此处不把未明确的数值补写成论文规定。 |
| Ohshita、Miyajima，IEICE Trans. Commun. 2026 | [出版社 §4、Fig.4 附近](https://globals.ieice.org/en_transactions/communications/10.23919/transcom.2025CEP0005/_f)：对一个归一化幅度门限基准逐 SNR 搜索最佳参数，作者明确说明实际使用有困难。 | 文献确实存在逐 SNR 优化的性能对照，但该对照与接收机可执行、独立校准的门限规则有区别。 |

### 固定概率门限与固定能量门限不是同一个限制

设用户活动后验为 q=P(a=1|Y)。以下为对判决代价的直接推导，不额外声称某篇论文的具体实现：误判活动的条件风险为 C_FA(1−q)，误判不活动的条件风险为 C_MD q。因此判活动等价于

\[
q\geq\frac{C_{\mathrm{FA}}}{C_{\mathrm{FA}}+C_{\mathrm{MD}}}.
\]

在后验模型正确、两类单次错误代价相等时，该门限为 0.5。活动先验和噪声水平已经通过后验进入判决；这不意味着条件漏检率和条件虚警率必然相等。学习得到的近似概率也不能仅凭输出在 [0,1] 内就当作校准良好的后验。Cai 式(29)–(31)提供用户后验判决的直接论文背景；该推导不证明当前 STMP 分类器在所有条件下已正确校准。

当前能量分数 r_k=E_k/max_j E_j 则没有后验概率含义。固定 r_k≥η 等价于 E_k≥η max_j E_j，已经随场景中最大恢复能量变化。这个归一化去掉了共同尺度，但不能保证主动/非主动用户分数的条件分布不随 SNR、用户数、活动率、近远效应或恢复偏差变化。因此，既不能把 η=0.5 当作 Bayes 判决，也不能因分数已归一化就证明固定 η 对所有工况最优。

Liu–Yu 的解析门限具体为

\[
\theta_{t,n}=\frac{M\log(1+\beta_n/\tau_t^2)}{1/\tau_t^2-1/(\tau_t^2+\beta_n)}.
\]

其中 τ_t² 是 AMP 有效误差方差，按原文状态演化更新，不能直接替换成接收机物理噪声方差。它展示的是“同一公式、变化数值”。论文的独立 Gaussian 信道、AMP 状态演化等假设不自动适用于本项目 AFDM、off-grid 字典和神经估计器。

### 分档是否合理，要看它怎样产生

按可获得的估计 SNR 使用一个预先固定的函数 η=g(SNR_hat)，可以是合法的接收机设计；分段常数表只是实现形式之一。若固定值是函数类的特例，则在同一总体分布、同一风险目标下，该函数类的最小总体风险不会高于仅允许一个常数的最小风险。这是模型类包含关系，不是有限样本拟合后的性能保证。增加分档会增加需要估计的参数，可能引入校准方差、SNR 估计误差和场景迁移问题；断点也可能影响曲线形状，但曲线起伏本身不证明程序错误。

应区分三种评估条件：

1. 用接收机估计的 SNR/噪声查预先校准的表：可以部署，但校准和测试必须使用一致的估计流程，并验证其泛化。
2. 用仿真的真实 SNR 查表：额外获得了条件信息；允许作为明确标记的已知 SNR 对照，但不能冒充估计条件。
3. 在每个测试 SNR 上扫描门限并用同批真值选最优：可报告该组输出在事后最佳门限下的性能参考，不能当作独立测试下可部署接收机的结果。Ohshita–Miyajima 的对照说明，文献中的逐 SNR 最优曲线也需要按作者声明的角色理解。

### 对当前四个 baseline 的判断

目前 SOMP、GAMP、GNN 的策略来自 `readout_policy.json`，原校准用户数为 80，每个节点约 20 个条件；off-grid 表每个 SNR 仅 16 个场景，原校准采用已知噪声，现用于 40 用户、估计噪声主实验。它们不是现用测试标签现场拟合的门限，不能仅凭分档形式称为使用真值或作弊；但这些校准条件差异使其可靠性需要验证。

原文忠实性也需单独判断：SOMP 有直接 GFRA 相对能量门限先例；GNN 统计量可遵循 Ding，但数值必须声明为项目校准；现有 GAMP 的逐路径 Gaussian SBL 与 MP-BSBL 的用户共享方差并非同一模型；Wei 的 off-grid SBL 原本是信道估计方法，GFRA 活动读出属于本项目适配。不能为了形式统一，把不匹配的原生用户后验或方差规则机械移植过来。

对当前版本的建议是：

- 主比较优先采用每个方法各自一个跨 −4～6 dB 的固定门限，从独立、匹配当前模型/权重/已知相位/估计噪声条件的校准集确定。不要直接采用旧模型门限，也不要把 0 dB 单点值视为已完成全区间校准。
- 校准目标预先固定为六档等权的 AER，并同时报告漏检率、虚警率。AER=(1−p_a)P_FA+p_a P_MD，不能把 P_FA+P_MD 与其混同。
- 同一校准预算下保留估计 SNR 条件门限作为对照。若独立验证显示其稳定改善，可以把它作为充分披露的主接收机设置；没有原则要求为了统一而压低 baseline 性能。
- 所有算法使用相同的校准/验证场景划分、接收机信息条件和评估范围；不要求所有算法采用同一个数值，也不要求把原生后验方法全部改成能量门限。
- ROC 或漏检—虚警曲线可作为补充，检查结论是否只是单一工作点导致；它不能代替主图中事先冻结的判决规则。

已有 [800 场景固定门限诊断](../../../result/snr_comparison/data/candidates/baseline_fixed_eta_20261023/REPORT.md)仅说明现行分档并不必然优于固定值，不能据此选择最终门限。这 800 场景已被查看，应作为开发诊断数据；可继续保留完整 2000 场景描述性报告，但若根据前 800 场景选择了方案，最终确认应另外报告未参与选择的保留部分，并清楚标记边界。本次只作研究核查，不改动运行中的冻结主实验，不启动新校准、推断或训练。

## 2026-10-23 用户授权后的独立校准

用户随后明确要求“可以，那请你开始校准”。已建立独立批次
[baseline_calibration_20261023](../../../result/snr_comparison/data/baseline_calibration_20261023/README.md)：
500 个校准物理场景、另 500 个验证物理场景，均覆盖 −4、−2、0、2、4、6 dB，
保持 40 用户、16 帧、已知相位、估计噪声，与现行主实验相同的四个冻结 baseline。
新种子范围与主实验 2000 场景、功能检查及预热场景明确分离。

每个方法分别拟合跨 SNR 固定门限与估计 SNR 分档门限；两策略共用同一校准集。
分档拟合和执行都用接收机观测估计 SNR，不能按真实 SNR 拟合后偷偷用真实 SNR 分档。
程序先冻结门限及哈希，再执行验证。总体六档等权 AER 是预先固定的选择目标，
同错误数优先减少虚警，再选更小门限。默认建议固定门限，仅在分档减固定的总体 AER
配对 bootstrap 98.75% 区间上界小于零时建议分档，四个方法比较采用 Bonferroni 调整。
六档 SNR 随物理场景一起重采样；逐 SNR 区间仅作描述，完整报告漏检、虚警与 AER。

这属于当前实现的项目校准，不补足原论文未披露的数值，也不声称所有 baseline 都是作者代码复现。
所选策略的验证性能受策略选择影响，不称为未使用过的最终测试。
独立推断已授权；没有训练、STMP 推断、十层展开或自动改写主实验门限。
状态以批次 STATUS.json 为准，完成以 COMPLETE.json 和校验后的 RESULT.json 为准。

## 2026-10-23 改为复用主实验输出校准

用户随后确认：0–499 场景校准，500–999 场景验证并选择，1000–1999 场景用于最终比较。
执行批次为 [baseline_calibration_reuse1000_20261023](../../../result/snr_comparison/data/baseline_calibration_reuse1000_20261023/README.md)。
只重放保存的分数，不新增推断。原新种子校准在 880 份结果后暂停并保留，本次不混用。
拟合目标、估计 SNR 分档方式、精确断点扫描、物理场景配对 bootstrap 与策略选择规则沿用已确定协议。

前 800 场景已经做过诊断，所以本次是回顾性的开发划分，不把验证区间包装成全盲确认性检验。
核查 PRIOR_EXPOSURE.json 后发现，后 1000 中的 1040–1057 共 18 个场景也曾用于早期停止条件/GNN诊断。
它们不参与本次门限拟合和选择，但不是完全未查看的数据；保留全部固定场景并披露历史，不按表现删样本。
该暴露清单是既有记录的下界。最终比较统一在同一后 1000 场景上进行，不能标为 2000 场景独立测试。

FROZEN_READOUT.json 记录验证后选择的门限与来源哈希；它供保存输出后处理使用，
不改写正在运行的主实验全局配置。STMP 的原判决保持不变；信道恢复无需重跑。

## 2026年10月9日历史记录

2026-10-09按用户“尽量参照原论文”的要求核对。当前修订解决活动读出；不把该修订表述为所有基线的作者代码复现。

| 方法 | 原文定位与输出 | 本次设备判决的来源 |
|---|---|---|
| SOMP | [Tropp Algorithm 3.1、§3.2，PDF pp.6–7](https://tropp.caltech.edu/papers/TGS05-Algorithms-Simultaneous-I-preprint.pdf)：共同支撑、正交投影与残差；原文停止门限用于终止恢复 | 原文不规定我们的设备块检测；比较接入采用Ding式(27) |
| GAMP-SBL | [Zhang，p.15059 Algorithm 1](../../../reference/zhang2023_gamp_sbl_grant_free_noma.pdf)：输出估计信号b，Stage 4的1e−6用于停止均值更新 | 该算法未规定AFDM设备块归一化能量门限；比较接入采用Ding式(27) |
| EM-BG-AMP | [Vila–Schniter，p.3 Eqs.(10)、(15)，Tables I/II](https://arxiv.org/pdf/1207.3107v3)：信号均值、方差及系数支撑后验概率π | 原文不规定本项目设备块检测；比较接入采用Ding式(27)。不是Ding引用的Zhao版本 |
| AMP-NNSPL | [Meng，§III Algorithm 1、Eqs.(9)–(20)](https://arxiv.org/html/1601.00543v1)：SMV系数估计、最近邻稀疏率及EM更新 | 原文不规定设备块η；当前已登记MMV适配的比较接入采用Ding式(27) |
| GNN-ASPL | [Ding，p.4 Eq.(27)](../../../Learning_Sparsity_Pattern_An_Adaptive_Joint_Detection_for_AFDM_Grant-Free_System_in_LEO_Satellites_Communication.pdf)：物理系数块平均能量/最大块能量，`>= η` | 直接采用原式 |

Ding全文只把η定义为decision threshold，未给数值、拟合步骤或逐SNR门限规则。p.5 §IV-A明确的“for each SNR”指十层网络训练。可见[式(27)渲染](../../../archive/paper_layout_20261026/original_paper/docs/history/results/baseline_pilot_20261008/paper_reaudit/ding_eq27_detail.png)。

运行所需的η直接从[已完成原模型验证](../../../archive/paper_layout_20261026/original_paper/docs/history/results/ding_reproduction_20261009/independent_snr8/VERIFICATION.json)的128场景独立校准证书转用，所有SNR/网格保持同值；原文未公开的数值仍明确标为实施设置。没有新增混合SNR拟合，也没有用当前评价标签选门限。GNN原模型证书对应另一套原场景权重；现在只转用固定数值，不声称它是当前统一权重的校准证书。

实现见`scripts/run_project_baselines_paper_readout.py`，判决直接调用已核对的`coefficient_activity`和`activity_decisions`。恢复核心先输出系数，活动读出在外部执行；索引指向此入口。现有求解设置、适配来源、权重和旧结果保持，新的固定门限读出与旧读出分开保存。
