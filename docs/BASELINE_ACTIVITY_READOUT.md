# 活动判决的原文与实现

2026-10-09按用户“尽量参照原论文”的要求核对。当前修订解决活动读出；不把该修订表述为所有基线的作者代码复现。

| 方法 | 原文定位与输出 | 本次设备判决的来源 |
|---|---|---|
| SOMP | [Tropp Algorithm 3.1、§3.2，PDF pp.6–7](https://tropp.caltech.edu/papers/TGS05-Algorithms-Simultaneous-I-preprint.pdf)：共同支撑、正交投影与残差；原文停止门限用于终止恢复 | 原文不规定我们的设备块检测；比较接入采用Ding式(27) |
| GAMP-SBL | [Zhang，p.15059 Algorithm 1](../references/zhang2023_gamp_sbl_grant_free_noma.pdf)：输出估计信号b，Stage 4的1e−6用于停止均值更新 | 该算法未规定AFDM设备块归一化能量门限；比较接入采用Ding式(27) |
| EM-BG-AMP | [Vila–Schniter，p.3 Eqs.(10)、(15)，Tables I/II](https://arxiv.org/pdf/1207.3107v3)：信号均值、方差及系数支撑后验概率π | 原文不规定本项目设备块检测；比较接入采用Ding式(27)。不是Ding引用的Zhao版本 |
| AMP-NNSPL | [Meng，§III Algorithm 1、Eqs.(9)–(20)](https://arxiv.org/html/1601.00543v1)：SMV系数估计、最近邻稀疏率及EM更新 | 原文不规定设备块η；当前已登记MMV适配的比较接入采用Ding式(27) |
| GNN-ASPL | [Ding，p.4 Eq.(27)](../Learning_Sparsity_Pattern_An_Adaptive_Joint_Detection_for_AFDM_Grant-Free_System_in_LEO_Satellites_Communication.pdf)：物理系数块平均能量/最大块能量，`>= η` | 直接采用原式 |

Ding全文只把η定义为decision threshold，未给数值、拟合步骤或逐SNR门限规则。p.5 §IV-A明确的“for each SNR”指十层网络训练。可见[式(27)渲染](../docs/history/results/baseline_pilot_20261008/paper_reaudit/ding_eq27_detail.png)。

运行所需的η直接从[已完成原模型验证](history/results/ding_reproduction_20261009/independent_snr8/VERIFICATION.json)的128场景独立校准证书转用，所有SNR/网格保持同值；原文未公开的数值仍明确标为实施设置。没有新增混合SNR拟合，也没有用当前评价标签选门限。GNN原模型证书对应另一套原场景权重；现在只转用固定数值，不声称它是当前统一权重的校准证书。

实现见`scripts/run_project_baselines_paper_readout.py`，判决直接调用已核对的`coefficient_activity`和`activity_decisions`。恢复核心先输出系数，活动读出在外部执行；索引指向此入口。现有求解设置、适配来源、权重和旧结果保持，新的固定门限读出与旧读出分开保存。
