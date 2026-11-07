# 四个 baseline 的 GFRA 文献、实现与判决核验

日期：2026-10-23。范围：SOMP、GAMP-SBL、GNN-ASPL、off-grid SBL；40 用户、16 帧、16 天线，SNR 为 −4、−2、0、2、4、6 dB，已知相位、估计噪声。十层 Proposed 不在本次范围。

## 结论和证据边界

GFRA 的联合活动检测与信道估计已有长期文献基础，不能把活动判决当成没有出处的附属步骤。2013 年已有稀疏随机接入的联合估计，2018 年已有 MP-BSBL，2020 年已有自适应 GMMV-AMP；SOMP 也有直接用于 LEO grant-free NOMA-OTFS 的论文。当前四个方法的求解器都有算法来源，但**当前完整接收机不是四篇原论文的逐项原样复现**。

最需纠正的是来源表述和活动判决协议：四者当前均按**估计 SNR 的最近节点**选择门限，不是跨 SNR 固定门限；这不是 Ding 式(27)给定的规则。分档规则不因其形式就必然无效，也不能从曲线不平滑断言求解器错误。但当前校准场景、噪声条件和评估条件不完全一致，样本很少，不能借“原论文 baseline”掩盖这些适配。

本次不改动运行中的求解器、权重、配置和主实验。候选固定门限代码、离线重判和数学检查均独立保存。没有启动新接收机 MC 或训练。**数学检查通过 ≠ 对原论文完全复现 ≠ 性能校准完成。**

## 文献检索与原文定位

检索覆盖作者主页、机构知识库、arXiv、IEEE DOI/Crossref、出版社全文及关键论文参考文献，日期截至 2026-10-23。关键词组合包括 grant-free/GFRA/random access、activity detection/channel estimation、SOMP、GAMP/SBL、block sparse Bayesian learning、off-grid、AFDM/OTFS。沿 Ding、Shen、Ke 的引用向前追溯，并检索近期后续工作。这是有范围的工程研究审计，不宣称穷尽全部文献或系统综述。

下列 PDF 页码均指此次存档文件的页序。HTML、预印本和期刊排版的公式编号可能不同；不得混用。PDF、文本、下载地址和 SHA256 在 `reference/reviews/baseline_gfra_audit_20261023/FETCH_MANIFEST.json`；下载成功不等于全文全部逐式核对。

| 文献及原始来源 | 已核对的内容与用途 | 边界 |
|---|---|---|
| Schepker–Bockelmann–Dekorsy, 2013, *Exploiting Sparsity in Channel and Data Estimation for Sporadic Multi-User Communication*，[作者机构 PDF](https://www.ant.uni-bremen.de/sixcms/media.php/102/11853/ISWCS_2013_schepker.pdf) | p.1–2、§II-B 式(3)、§III-A：已知导频下同时估计活动和信道，区别于已知 CSI 的数据检测。 | 早期随机接入依据，不是当前 SOMP 的逐项来源。 |
| Wunder–Jung–Ramadan, 2015, *Compressive Random Access Using A Common Overloaded Control Channel*，[原文](https://arxiv.org/html/1504.05318v1) | §II、§III-B：共同控制信道上利用用户和信道稀疏性进行接入检测。 | 背景及检测分析；不能替四个实现背书。 |
| Tropp–Gilbert–Strauss, 2006, *Algorithms for simultaneous sparse approximation. Part I: Greedy pursuit*，[2005 作者预印本](https://tropp.caltech.edu/papers/TGS05-Algorithms-Simultaneous-I-preprint.pdf) | Algorithm 3.1，PDF pp.6–7：跨观测绝对相关和、支持集合、最小二乘与残差；停止条件为算法输入。 | 通用 SOMP，不是 GFRA 协议；噪声停止不是该算法唯一规定。 |
| Yuanyuan Zhang et al., TVT 2018, *Block Sparse Bayesian Learning Based Joint User Activity Detection and Channel Estimation for Grant-Free NOMA Systems*，[作者机构记录](https://pure.bit.edu.cn/en/publications/block-sparse-bayesian-learning-based-joint-user-activity-detectio)，DOI 10.1109/TVT.2018.2859806 | 原始 MP-BSBL，联合活动/信道/噪声估计的直接 GFRA 来源。 | 本次仅核实元数据与摘要；原始全文未取得。其算法说明另核对下列 2019 原文，不伪称已读 2018 全文。 |
| Al-Shoukairi–Schniter–Rao, TSP 2018, *A GAMP-Based Low Complexity Sparse Bayesian Learning Algorithm*，[作者 PDF](https://phil-schniter.web.app/pdf/tsp18_sbl.pdf) | §III、Table I、PDF pp.4–5 式(19)–(22)：GGAMP 内层完成 E 步，外层更新 SBL，阻尼用于改善稳定性。 | 非 GFRA；当前单循环无阻尼 GAMP 不能引用其保证宣称收敛。 |
| Zhaoji Zhang et al., TVT 2019, *DNN-Aided Block Sparse Bayesian Learning for User Activity Detection and Channel Estimation in Grant-Free Non-Orthogonal Random Access*，[原文](https://arxiv.org/html/1910.02953v1) | PDF p.4 §II-B 用户块共享精度；p.5 式(14)估计噪声；p.10 Table IV 设用户方差门限 0.1。§II-C 复述 MP-BSBL。 | 这里的 0.1 是用户块方差门限，不是归一化能量门限；不能直接移植给当前逐路径 SBL。 |
| Ke et al., TSP 2020, *Compressive Sensing Based Adaptive Active User Detection and Channel Estimation: Massive Access Meets Massive MIMO*，[原文](https://arxiv.org/html/1906.09867v4) | §III-B，PDF p.7 式(39)–(41)：CG-AD 与 BI-AD；后者先对后验指标作 0.5 判决，再按跨观测比例 0.9 判用户活动。噪声用 EM 学习。 | 这是具有相应用户共同稀疏模型的 GMMV-AMP；不是任意路径概率求均值后与 0.5 比较。 |
| Wei et al., TWC 2022, *Off-grid Channel Estimation with Sparse Bayesian Learning for OTFS Systems*，[原文](https://arxiv.org/html/2101.05629v1) | §III–IV、Algorithm 1、§VI-A：二维一阶 off-grid 模型、SBL 后验和偏移更新；原始噪声先验及停止设置可查。 | 单用户信道估计来源，未定义当前 GFRA 活动读出；AFDM、MMV、字典筛选与噪声前端须另行声明。 |
| Shen et al., 2022, *LEO Satellite-Enabled Grant-Free Random Access with MIMO-OTFS*，[原文](https://arxiv.org/html/2208.01828v1) | 本次 PDF p.3 式(14)按用户信道能量判活动；§III 的 Gaussian 精度结构、GAMP/EM/学习用于联合估计。 | DL-GAMP/ConvGAMP 有专门的相关结构及学习条件；不是当前行共享精度 GAMP 的同名替身。 |
| Zhou et al., TWC 2023, *Active Terminal Identification, Channel Estimation, and Signal Detection for Grant-Free NOMA-OTFS in LEO Satellite Internet-of-Things*，[原文](https://arxiv.org/html/2201.02084v2)，DOI 10.1109/TWC.2022.3214862 | PDF p.10 §IV-C 式(27)、脚注3：SOMP 后用户能量相对最大能量，β=0.1 为经验设置；Algorithm 1；p.13 §VI-A：最多30次，残差停止用 1.05σ²。 | 原文假设已知噪声；本项目用估计噪声且字典不同，30次不能机械照搬。其后续参数精化不是当前 SOMP 的一部分。 |
| Xiaoxu Zhang et al., TVT 2023, *Generalized Approximate Message Passing Based Bayesian Learning Detectors for Uplink Grant-Free NOMA*，[DOI](https://doi.org/10.1109/TVT.2023.3280919) | 当前 GAMP 历史实现引用。核实作者、标题及 pp.15057–15061；摘要讨论多用户信号检测。 | 本次未取得可读全文，旧本地 PDF 引用已失效；不新宣称已验证式(3)–(19)。是否及如何与本项目导频 JADCE 对应仍需原文核对。 |
| Shuo Chen et al., Drones 2023, *Block Sparse Bayesian Learning Based Joint User Activity Detection and Channel Estimation in Grant-Free MIMO-NOMA*，[出版社](https://www.mdpi.com/2504-446X/7/1/27) | 直接 GFRA MIMO，研究空间相关 BSBL；证明存在比通用 CE 更贴题的 SBL 文献。 | 此次核读摘要/引言及部分正文；不据此指定当前实现的更新式和门限。 |
| Shen et al., TWC 2025, *LEO Satellite-Enabled Random Access with Large Differential Delay and Doppler Shift*，[原文](https://arxiv.org/html/2412.20806v1) | PDF p.7 式(21)：用户能量与预设经验门限比较；MRF-MP-GAMP 联合估计，相位与噪声有相应学习步骤。 | 不能将跨帧相位处理与 Wei 二维网格偏移视为同一 off-grid 算法。 |
| Marata–Ollila–Alves, TVT 2025, *Activity Detection for Massive Random Access Using Covariance-Based Matching Pursuit*，[机构 PDF](https://aaltodoc.aalto.fi/bitstreams/53a36764-729e-41cc-ba08-0c5dbef21bc9/download) | 原文比较活动检测方法并讨论停止与能量检测；作为匹配追踪接入检测的补充检索。 | 协方差活动检测不自动提供本任务需要的完整信道 NMSE；本地下载因 TLS 失败，浏览器可读。 |
| Ding et al., TVT 2026, *Learning Sparsity Pattern: An Adaptive Joint Detection for AFDM Grant-Free System in LEO Satellites Communication*，[作者机构](https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/Learning-Sparsity-Pattern-An-Adaptive-Joint/991155194002346?institution=44SUR_INST)，DOI 10.1109/TVT.2026.3729877 | 本地六页稿 p.4 式(27)是系数块归一化能量；p.5 §IV-A 明确每个 SNR 训练十层网络。 | 未找到 η 的数值、分档表或门限校准过程。不能把本文方法误写成直接采用图网络输出的用户概率判决。 |
| Huang et al., TCOM 2026, *Joint Terminal Identification and Channel Estimation of Asynchronous Grant-Free Access for LEO Satellite-IoT Network*，[DOI](https://doi.org/10.1109/TCOMM.2026.3693170) | 直接针对 LEO 异步 GFRA，摘要说明 Rician 参数学习 GAMP 与 Taylor off-grid 扩展。 | 仅元数据/摘要核实；不是已核实可替换的 Wei-SBL 作者实现。 |
| Ge et al., 2026, *Structured-Sparsity-Aware Joint User Activity Detection and Channel Estimation for OTFS-Based Grant-Free Random Access*，[预印本](https://arxiv.org/abs/2608.03896) | PDF p.5 式(26)按用户活动指标判断，BEM 与双层结构稀疏 EP。 | 新近预印本；用于对照用户层先验，不属于当前四个 baseline，也不替它们命名。 |

额外检索到 Liu–Yu TSP 2018 的 *Massive Connectivity With Massive MIMO—Part I: Device Activity Detection and Channel Estimation*（[作者列出的论文与代码入口](https://www.eie.polyu.edu.hk/~liangliu/mMTC_publication.html)、[预印本](https://arxiv.org/abs/1706.06438)），是用户级 AMP 的重要来源；此次仅核实摘要及作者目录，不引用未经检查的代码实现。Xiaoxu Zhang TWC 2022 的 Bayesian Learning-Based Multiuser Detection 与 2024 Drones 的 Message Passing Detectors for UAV-Based Uplink Grant-Free NOMA 属于相邻数据检测路线，不能仅凭 grant-free 标题就视作未知信道 JADCE。

同一论文的会议/期刊或 arXiv 版本不累计为独立性能证据。此次没有核实到当前四个特定实现各自的官方代码，第三方 FastSBL 等仓库不能写成 Zhang 2023 或 Ding 的作者代码。

## 四个实现应怎样定位

### SOMP

保留 Tropp 的同时稀疏恢复核心，并引用 Zhou 的 GFRA 使用与能量活动判决。当前 `src/algorithm/baseline/somp.py` 采用单位范数字典、跨天线绝对相关和、正交残差、LS 输出，不输入真实活动数。最多64原子，残差能量不高于观测维数乘估计噪声时停止；64是预算，不是已知活跃数。

候选优先保持核心，独立比较两项：固定跨 SNR 能量门限；噪声停止因子。Zhou 的 β=0.1、噪声因子1.05可作有出处的参考控制，但不是本场景最优参数。不能为了“复现”把当前最多64改为30后就宣称严格对齐，因为两者未知量、路径数与观测维度不同。

### GAMP-SBL

当前 `gamp.py` 是复数、跨天线共享行精度的 Gaussian SBL，交替更新 Gaussian 消息、行精度和噪声精度。它没有显式二元用户活动后验。MMV 扩展、空间协方差噪声锚定、能量活动判决均须独立声明；不能直接改用“概率≥0.5”。

当前噪声精度 MAP 采用 shape/rate：c=1+LM、d=LM·σ̂²_spatial。相当于给当前观测提供一个较强的噪声尺度约束；与似然使用同一观测，不能声称获得独立额外信息。代数成立不等于原文就采用这组超参数。

需要补全 Zhang 2023 原文到代码的对应，尤其数据检测模型与本任务导频信道估计的区别。2018 MP-BSBL、2019 的公开完整叙述及 Shen 2022 是更直接的 JADCE 对照。若改成用户块共享精度，就是新的 BSBL 候选，不能仍称当前逐路径先验完全未变。若采用 Al-Shoukairi 的 GGAMP-SBL，应真的实现内外两层与阻尼，不能只给当前单循环加一个系数便引用其收敛论证。

当前绝对停止量是每列均值变化的**平方和** ≤1e−6，非相对变化；它受幅度、维数影响。需要在独立小规模配对验证中检查预算和稳定性，不能以调出光滑 AER 为目标。

### GNN-ASPL

当前 `gnn.py` 保留十层 AMP、同用户图注意力和 GRU、Ding 式(21)四个节点特征；式(27)能量判决与图网络里的路径稀疏概率是两回事。此次独立检查了复 Gaussian 混合后验，以及完整用户/原子重排时输出的等变性。

`result/models/gnn/checkpoint.pt` 实际记录：10001训练样本、256验证样本、SNR 连续均匀[-10,10]、on/off-grid 各约一半、一套混合 SNR 权重；`separate_model_per_snr=False`，状态为 `TRAINED_UNQUALIFIED`，接收机记录 `formal_qualification=False`。这些字段表示已完成训练但未声明正式资格，不能改写为“未训练”，也不能遗漏它们而称严格复现。

Ding 原文每 SNR 分别训练，故当前最准确表述为**按 Ding 结构重实现、采用混合 SNR 训练的适配版本**。若论文需要严格比较其原训练协议，应另建六个 SNR 模型和独立权重目录，再进行配对验证；本次未训练。原文没有公开门限数值时，使用独立校准并披露，比自行声称“论文门限”更可靠。

### Off-grid SBL

当前 `offgrid_sbl.py` 源自 Wei 的二维一阶 off-grid SBL，并扩展到 AFDM/MMV。逐原子方差、后验协方差、期望残差、偏移二次目标与连续原子导数已通过局部数值检查。

研究风险在整体适配：每用户初始筛至12个原子、每轮只更新48个偏移候选、中心固定、噪声强先验、120轮预算和用户活动读出。Wei 在偏移子问题中限制重要分量，不等于本实现一开始永久排除其余字典原子。此前800场景的4800份输出全部到120轮，一阶模型与最终精确连续重构的预测有明显差异。原文允许精确重构，因此差异本身不证明代码错误，但应验证其性能影响。

不能把用户所有路径的独立方差相加后，冒称 2018 MP-BSBL 的用户共享超参数；也不能把该文方差门限0.1直接用于我们的归一化能量。推荐保留可追溯的 Wei-SBL 适配版，同时在独立候选中分开检查字典筛选、迭代预算、噪声先验和读出。若引入用户块先验，应明确新候选的模型变化。

## 判决规则与实验复用

当前 SOMP/GAMP/GNN 的分数是物理系数块平均能量除以最大用户能量；off-grid SBL 用重构信道 Frobenius 能量的相对值。二者不在所有非正交字典下等价。

推荐的默认候选是**每个算法独立校准一个跨六档 SNR 固定的门限**。算法间不强行同值；校准目标预先定为总体用户错误数，并同时报告漏检和虚警。门限只在独立校准物理场景上选；单独验证集检验，2000主场景禁止参与拟合。仅同一物理场景改变 SNR 不构成新的独立校准/验证场景。

这一候选不是声称所有论文必须固定门限；若某原文有明确的噪声相关解析检测式，按其模型使用更合理。现阶段也不把插值平滑分档门限当成有理论依据的修复。

独立代码在 `result/snr_comparison/data/candidates/baseline_readout_20261023/readout.py`：判决接口不接收 SNR 或真值；校准函数按所有分数变化点精确搜索，固定同错时优先少虚警的规则，拒绝与明确列出的测试物理场景重叠。已检查与穷举结果一致、门限相等时的≥语义、全零输出和数据重叠拒绝。**当前未拟合正式门限，未接入冻结接收机。**

只有读出变动时，可用已保存的分数和能量重新计算活动指标；原始信道估计与当前未按活动判决截断的 NMSE 不变。若改变 GAMP 先验、SOMP 停止、off-grid 字典/偏移或 GNN 权重，必须重新推断对应候选，不能只改结果文件。若新增按检测集合截断信道的后处理，NMSE也须重算并另标版本。

## 此次可复现检查

检查目录：`result/snr_comparison/data/audits/baseline_gfra_20261023/`。

- `check_math.py` / `MATH_CHECKS.json`：SOMP 确定性稀疏恢复；GAMP 独立标量 Gaussian 条件矩及噪声 MAP 驻点；GNN 显式密度乘积的 BG 后验及图重排；固定门限候选的校准和隔离检查。复用并核对 off-grid 数值检查时的源文件哈希。
- `replay_readouts.py` / `READOUT_REPLAY.json`：固定 scene0000–0799、六档SNR、四方法19200份已保存输出；校验结果与压缩文件哈希，逐项复现原判决和漏检/虚警，再计算事先指定的0.1数值控制。**不拟合测试集门限、不选择平滑曲线。**
- `READOUT_INPUTS.npz`、`REPLAY_REFERENCES.json`：保存完整分数、能量、原判决、真值和原始文件身份，供后续重判审计；这些仍是测试集，不能转充校准集。
- `SOURCE_EVIDENCE.json`：当前核心/配置/权重来源及文献证据状态。

主实验计划 SHA256：`254c0f8f72c779dd9253bdbbb787eae2b986c1d6f5fac5bcba83619e401d92a7`。800场景快照 SUMMARY SHA256：`436c4ab11bef0e851de4a6abfd50cacd54c88d2c12df0a69daf201330d3d23c5`。此次没有修改这两个文件。

已知相位是明确的 oracle 条件。原生结果里的 `truth_used_in_inference=True` 由 `suite.py` 统一写入，包含这一已授权的真实相位；不是使用活动真值。核查时应分别检查 `oracle_phase_supplied=True`、`oracle_noise_supplied=False`、`activity_count_or_truth_used=False`，不能机械要求所有 truth 字段均为 false。

## 正式采用前的剩余工作

此次19200份输出均已通过重判核验。当前停止情况：SOMP有4762份按噪声残差停止、38份到64原子预算；GAMP全部按均值变化停止，中位242轮、最大480轮；GNN固定10层；off-grid SBL全部到120轮。这些是停止状态，不是正确率证明。

事先指定固定0.1控制的错误数如下，每格分母为32000个用户判决。前一行保留原分档规则，后一行为同一恢复输出的固定门限读出。**这是测试集敏感性诊断，不是正式改进结果，也不据此选择最终门限。**

| 方法/读出 | −4 dB | −2 dB | 0 dB | 2 dB | 4 dB | 6 dB |
|---|---:|---:|---:|---:|---:|---:|
| SOMP 原规则 | 337 | 265 | 184 | 161 | 172 | 151 |
| SOMP 固定0.1 | 398 | 221 | 207 | 193 | 185 | 187 |
| GAMP 原规则 | 423 | 165 | 111 | 84 | 81 | 72 |
| GAMP 固定0.1 | 270 | 215 | 186 | 160 | 137 | 131 |
| GNN 原规则 | 171 | 108 | 74 | 60 | 54 | 50 |
| GNN 固定0.1 | 266 | 197 | 156 | 136 | 122 | 106 |
| off-grid SBL 原规则 | 202 | 183 | 146 | 126 | 94 | 92 |
| off-grid SBL 固定0.1 | 156 | 139 | 125 | 111 | 106 | 103 |

固定0.1并不普遍改善结果，GNN各点反而更差；off-grid低SNR减少错误、高SNR增加错误。仅凭“有论文用0.1”就统一覆盖四个算法，会改变虚警/漏检权衡，不能视作公平性的证明。完整漏检、虚警和发生变化的判决数保留于JSON。

1. 用已知相位、估计噪声的当前40用户条件建立独立校准与验证集合。沿用−4至6 dB；记录输入哈希，事前固定场景，不按性能选样。校准样本数应由目标错误率及区间精度决定，不再次用每档十几场景宣称充分。
2. 优先验证活动读出，因为无需更改求解核心。报告 AER、Pmd、Pfa 和按物理场景成组的配对置信区间；稀少错误下不以点估计或光滑度裁决。
3. 对 off-grid 做同输入的字典筛选/预算/噪声消融，区分永久筛选造成的可表示性限制、未充分迭代和读出漏检。每次只改变一个因素，保留不利结果。
4. 完成 GAMP 原文模型核对与稳定性验证。只有证据显示当前适配不足，才引入命名清楚的 MP-BSBL/GGAMP-SBL 候选；不把不同算法拼接后继续冒用旧名称。
5. GNN 当前可作为声明训练差异的适配对照；若要求 Ding 原训练协议，另行训练并验证。不能通过改 metadata 把现有权重升级为严格复现。

这些工作完成前，现有2000场景运行应保留为当前冻结协议的结果。后续若只改门限可以重判，若改求解器则保留旧版本并另跑候选；不能悄悄覆盖后将两种协议混成一条正式曲线。
