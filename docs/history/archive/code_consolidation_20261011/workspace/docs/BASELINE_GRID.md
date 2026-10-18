# 整数时延/Doppler网格与当前基线

## 2026-10-10：恢复 Ding 的归一化网格粒度

当前入口为 [baselines_paper_reference_20261010.json](../configs/baselines_paper_reference_20261010.json)。依据 [Ding 接受稿](../paper/literature/ding2026.pdf) p.2 式(8)及 p.5 §IV-A，原文为
\(\tau_i=i\tau_{\max}/N_\iota\)、\(\nu_j=(2j-N_\kappa)\nu_{\max}/N_\kappa\)，
\(\tau_{\max}=2,N_\iota=2,\nu_{\max}=30\,\mathrm{kHz},N_\kappa=4,\Delta f=15\,\mathrm{kHz}\)。
因此原文时延步长为一个采样点，Doppler 步长为 15 kHz，即一个归一化子载波间隔；原模型每用户 3×5=15 个原子。

| 项目 | Ding 原模型 | 本项目对应设置 |
|---|---|---|
| 时延步长 | 1 个采样点 | 1 个采样点 |
| Doppler 步长 / Δf | 1 | 1 |
| Δf / Doppler 物理步长 | 15 / 15 kHz | 30 / 30 kHz |
| 时延格点 | 0,1,2 | 0,1,…,15 |
| Doppler 格点 | −30,−15,0,15,30 kHz | −60,−30,0,30,60 kHz |
| 每用户原子数 | 15 | 80 |

这是按归一化坐标恢复原文粒度，并对新场景扩展覆盖范围；不称为原物理 Hz 数值的逐项复现。时延覆盖一个 N=16 折叠周期，Doppler 两端格点覆盖真实 ±41 kHz 支持。不能直接截取原文的 0–2 时延范围；也不再使用自行加密的 0.25 采样点 / 15 kHz（每用户 448 原子）配置。SOMP、Zhang GAMP-SBL 的一般稀疏恢复论文没有给出 AFDM 时延/Doppler粒度，因此该共同字典以 Ding 的比较模型为依据。

真实信道继续使用原 off-grid 输入。GNN 换回与 80 原子训练网格和源码指纹匹配的已有 10001/256 样本权重，未新增训练；活动规则同时恢复 Ding 式(27)物理系数块能量。GAMP 恢复 Zhang 单次无阻尼更新与学习噪声，独立天线列并行计算仍属于 SMV 的场景适配。Zhao EM 全文及其活动规则尚待取得，现有 Vila 方法不作为它的替代复现。配置、独立校准和公开输入检查记录位于 [paper_reference_20261010](../results/paper_reference_20261010/PLAN.json)。

以下保留 2026-10-08 的历史配置、门限和验证记录，不能作为这次恢复后的实验结果。

2026-10-08整数网格资格阶段，SOMP、OAMP-MMV和GAMP-SBL统一使用较小的整数网格。本次基线选择调整后，默认入口 [current_baseline_suite.json](../configs/current_baseline_suite.json) 保留SOMP和GAMP-SBL；OAMP三方法原配方保存在[归档](../archive/oamp_mmv_20261008/configs/current_baseline_suite.json)。原门限证书与102份结果保留，新增方法状态见[BASELINE_REVISION.md](BASELINE_REVISION.md)。

## 网格与真实信道

| 设置 | 当前取值 | 原细网格 |
|---|---|---|
| 折叠时延样本 d | 0,1,…,15，步长1 | 0,0.25,…,15.75 |
| 归一化Doppler ν/Δf | −2,−1,0,1,2 | ±41 kHz之间的9个等距点 |
| Δf | 30 kHz | 30 kHz |
| 每用户物理原子数 | 16×5=80 | 64×9=576 |

时延网格覆盖一个N=16的折叠周期，周期跨越的确定相位可收入未知复增益，依据见 [BASELINES.md](BASELINES.md)。不能直接套用Ding较小的时延索引范围而漏掉本项目的时延支持。真实Doppler最大绝对值为41 kHz，因此保留±2两端整数点；物理频率为−60、−30、0、30、60 kHz。

真实信道仍由原分数时延和分数Doppler生成，已知跨帧相位及共同噪声条件保持原定义。三方法的网格都相同，每用户字典列数减少7.2倍。当前实现是on-grid稀疏估计，没有加入off-grid细化。原细网格也是有限字典，并非gridless估计。

## 求解与判决

SOMP及OAMP-MMV保留原核心求解器与停止设置。GAMP采用Ding §IV-B所引Zhang p.15059 Algorithm 1的单次GAMP/全步精度更新、每列均值向量变化的平方和停止（\(\|m^{t+1}-m^t\|_2^2\le10^{-6}\)，不除以系数维数），上限2000轮；0.2消息/均值阻尼及给定噪声为项目设置，复数推导见 [DING_GAMP_ALIGNMENT.md](DING_GAMP_ALIGNMENT.md)。

三方法共同以完整重构H的用户平均能量严格 `>` 判决。分别在20个校准场景上重新拟合门限后冻结，另14个种子不同的检查场景不参与拟合。两组输入来自既有开发面板；本轮不增加独立场景，不作为正式独立性能确认。

采用前独立复核实际输入、原生输出、轨迹、重构H能量、活动判决、误差能量、门限拟合和配置指纹。102条输出均有效、失败0；GAMP全部544个天线列达到论文均值停止条件。详细数值和所有警告保留于结果目录。

## 文献与适用范围

小整数网格适合当前三个有限字典基线，理由是控制字典规模和迭代成本。连续参数估计并非不可行，也不是现有研究的空白。

| 已核对来源 | 原文定位 | 与本项目的关系 |
|---|---|---|
| Wei et al., *Off-grid Channel Estimation with Sparse Bayesian Learning for OTFS Systems*, arXiv:2101.05629v1 | [PDF](https://arxiv.org/pdf/2101.05629v1)，§III-B pp.11–12，式(17)–(24)；§VI-B pp.26–27 | 使用virtual sampling grid和一阶局部近似学习off-grid偏移，支持“有限粗网格加偏移细化”的路线；具体AFDM适配尚未实现。 |
| Chen et al., *A Low-Complexity Joint Fractional Delay and Doppler Frequency Estimator for AFDM-Enabled Vehicular LEO-ICAN Systems*, arXiv:2602.04316v2 | [原文](https://arxiv.org/html/2602.04316v2)，§II式(6)及其后参数定义；§III-B1–B2 | AFDM场景分别估计分数Doppler与分数时延，说明分数参数可以估计；其LOS估计问题不是本项目的多用户JADCE。 |
| Zhang, Yuan and Greco, *Zak-OTFS ISAC with Bistatic Sensing via Semi-Blind Atomic Norm Denoising Scheme*, arXiv:2601.03639v1，预印本 | [原文](https://arxiv.org/html/2601.03639v1)，§III-A式(28)–(31) | 原子集合在连续时延/Doppler区域Ω上定义，存在真正连续字典的原子范数建模；其SDP计算和ISAC模型不能直接当作本项目接收机。 |

本轮整数网格的34场景完整H最佳子空间投影误差为−11.239 dB。这是用真H计算的oracle离线诊断，接收机未读取该投影或真路径。它给出这些固定场景在80原子子空间内的表示误差下限，不能当作接收机性能。新网格的SOMP/OAMP检查full NMSE比旧细网格约退化3 dB，具体配对数据见报告。若后续需要更强的传统基线，可在相同粗网格上增加文献已有的off-grid偏移学习，并另行校准及评估。

## 保存及重放

冻结计划、代码副本、34个配对输入和102条输出在 [baseline_integer_grid_20261008](../results/baseline_integer_grid_20261008)。原细网格配置及门限按原字节保留为 [PREVIOUS_SUITE.json](../results/baseline_integer_grid_20261008/PREVIOUS_SUITE.json)和 [PREVIOUS_THRESHOLDS.json](../results/baseline_integer_grid_20261008/PREVIOUS_THRESHOLDS.json)，原结果目录保持原状。

执行脚本为 `scripts/qualify_integer_grid_baselines.py`，依次执行calibration、freeze、confirmation和report；历史采用脚本为 `scripts/adopt_integer_grid_baselines.py`。已存在的prepare计划不能被覆盖。原三方法独立核查使用 `scripts/audit_baseline_qualification.py --output results/baseline_integer_grid_20261008 --stage confirmation --adopted archive/oamp_mmv_20261008/configs/current_baseline_suite.json`；本次两方法的保留核验见 `results/baseline_revision_20261008/RETAINED_METHODS.json`。再次执行历史采用脚本会恢复三方法配置，应仅用于重放历史采用。

用户暂停的主线开发队列仍使用其启动时的独立运行副本，保持暂停。新的默认配置不会改写旧队列结果；完整主线比较应另建输出目录。
