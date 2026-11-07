# 五个主线基线的实现与来源

> **2026-10-23 阅读入口：** 以下保留早期五基线及未知相位历史。当前2000场景主实验仅含STMP与SOMP、GAMP、GNN、off-grid SBL，采用已知相位、估计噪声。四基线的最新原文核验、GFRA适配边界及尚未完成的正式资格检查见[专项报告](BASELINE_GFRA_AUDIT_20261023.md)。尤其不能将当前分档门限、混合SNR GNN训练或Wei-SBL的GFRA读出称为原论文原样设置。

五个基线为 **SOMP、GAMP-SBL MMV、GNN-ASPL、off-grid SBL、L-DAMP**。2026-10-15 起五者默认由观测估计噪声；字典、网络权重和既有活动门限保留。
主线采用未知跨帧相位：五个方法均先从观测和原始导频估计相位，再执行下述条件求解器。统一入口为 `algorithm/unknown_phase_baselines.py`；准确已知相位作为 `--phase-mode known` 的理想参考。
噪声处理入口为 [`algorithm/baseline_noise.py`](../../../src/afdm_jadcedd/algorithm/baselines/baseline_noise.py)，配置为 [baseline_noise.json](../../../src/configs/baseline_noise.json)。原条件内核由 `algorithm/registry.py` 分派，显式 `--noise-mode known` 可复现供给准确噪声的参考条件。各方法的原论文依据、公式及补充适配见 [噪声估计说明](BASELINE_NOISE.md)。

| 方法 | 核心与数值设置 | 论文定位 |
|---|---|---|
| SOMP | 单位列范数字典；正交残差更新；最多 64 原子；残差能量达到估计噪声能量时停止 | Tropp–Gilbert–Strauss, *Algorithms for simultaneous sparse approximation. Part I: Greedy pursuit*, 2006；Algorithm 3.1，预印本 pp.6–7。原文将停止准则作为输入；协方差噪声估计为补充适配。 |
| GAMP-SBL MMV | 物理字典；复高斯矩；跨天线共享行精度，学习一个噪声精度；无阻尼；最多 1000 轮；所有列的均值变化平方和 ≤1e−6 时停止 | [Zhang 2023](../../../reference/zhang2023_gamp_sbl_grant_free_noma.pdf)，pp.15058–15059，式(3)–(19)、Algorithm 1。共享 MMV 精度为明确的项目适配。 |
| GNN-ASPL | 十层网络；同一已完成训练的整数网格权重；以观测协方差估计值代入噪声参数 | [Ding](../../../reference/literature/ding2026.pdf)，pp.3–5，式(12)–(28)、§III-C。原文无独立噪声方差更新；该前端是补充适配。本轮未重新训练。 |

L-DAMP 使用十次 AMP 迭代、复数矩阵校正和五个噪声区间 DnCNN；使用精确网络方向导数和 Monte Carlo 部分迹估计，完整信道去噪器作用于复数 AFDM 矩阵。论文定位为 He 等 IEEE WCL 2018 §III-A 式(4)–(8)、Fig.3；多天线与复数处理是项目适配，详细说明见 [LDAMP.md](LDAMP.md)。该条件求解器已完成已知相位下独立 16 场景及配对 10 场景 × 六 SNR 验证，配置状态为 `VALIDATED_PAIRED_10_SCENES`；未知相位六方法面板使用显式的输出 TSVD 配置，见主 README。

原图 off-grid SBL 使用 120 次迭代、每用户 12 个筛选原子、48 个偏移候选、偏移子问题每次进行 5 轮坐标更新，前 5 次迭代不更新偏移、Doppler 步长 0.5；连续原子与导数由 `offgrid/atoms.py` 提供。论文来源、公式定位与 AFDM/MMV 适配范围见 [OFFGRID_BASELINES.md](OFFGRID_BASELINES.md)。原图 120 个 SBL 输出均达到迭代上限，结果完整保留。

当前 off-grid SBL 噪声学习保留 Wei 式(45)–(46)的后验期望残差，采用 c=1+LM、d=LMσ̂²_spatial 的数据依赖 Gamma 先验。
这是针对弱先验持续低估的项目适配；原论文 §VI-A 使用 c=d=1e−4。
原噪声初值和 120 轮预算不变，方差学习与原算法来源的边界见[四基线噪声核验](../../../archive/paper_layout_20261026/original_paper/docs/history/results/baseline_noise_audit_20261015/REPORT.md)。

GAMP 中设观测为 L×M，行索引为 g，Gamma 先验用 shape/rate 参数化：

\[
\alpha_g=\frac{M+a-1}{\sum_m(|\mu_{gm}|^2+v_{gm})+b},\qquad
\gamma=\frac{LM+c-1}{\sum_{lm}(|y_{lm}-\widehat u_{lm}|^2+v^u_{lm})+d}.
\]

当前 a=1、b=1e−12，c=1+LM、d=LMσ̂²_spatial，其中 σ̂²_spatial 由空间协方差估计。Gamma 先验强度沿用既有条件基线，尺度改由观测提供；数值强度属于项目设置，原论文未公布这组值。同一观测参与先验尺度估计和似然，不能把该尺度当作独立额外信息。初始化保持观测能量的 0.1 噪声比例，活动门限节点使用最终噪声估计。显式已知噪声参考将 rate 的尺度换为准确噪声。两者调用同一 `gamp_sbl_mmv.solve_mmv` 核函数。修正依据与验证见 [GAMP 噪声报告](../../../archive/paper_layout_20261026/original_paper/docs/history/results/gamp_noise_20261015/REPORT.md)。

共同网格为每用户 16×5=80 原子，时延步长 1 个采样点、Doppler 步长 30 kHz，见[网格说明](BASELINE_GRID.md)。性能评价输入保持连续 off-grid 物理信道。

前三个方法使用 Ding 式(27)物理系数块能量及已冻结的公共 SNR 判决规则，详见[活动判决](BASELINE_ACTIVITY_READOUT.md)。噪声估计版本以估计噪声计算节点，不重拟合门限。原校准身份保留，新噪声适配另有推断身份；门限复用不代表已在新信息条件下重新校准。

其他方法与参数版本见 [RESEARCH.md](RESEARCH.md)，已有不利结果继续保留。

整理前的完整推导、候选设置和核验历史见[原 BASELINES.md](../../../archive/paper_layout_20261026/original_paper/docs/history/archive/code_consolidation_20261011/workspace/docs/BASELINES.md)。术语和论文原文定位汇总在 [TERMINOLOGY.md](TERMINOLOGY.md)。

2026-10-15 GAMP-SBL 与 off-grid SBL 的[后验相位更新入口](BASELINE_PHASE.md)已完成实现，比较估计初相位后固定使用、一次全步和一次半步更新。三组均由观测估计相位。10 个新场景、六个 SNR、360 个输出全部保存，具体 NMSE、活动判决、配对区间及单列的真实相位诊断见[实验报告](../../../archive/paper_layout_20261026/original_paper/docs/history/results/baseline_phase_learning_20261015/REPORT.md)。这组实验用于比较未知相位条件下的更新方式。
