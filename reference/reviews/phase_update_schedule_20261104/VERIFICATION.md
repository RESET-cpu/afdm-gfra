# 相位更新间隔的文献依据核对

日期：2026-11-04。问题：现有周期检查并等待消息稳定的相位更新是否有研究支持？本次为事实核查，不运行实验，不修改算法、配置或稿件正文。

结论：在两次同步参数更新之间进行多轮检测／译码，有直接文献讨论和接收机实验先例。现有每20轮检查、稳定门、状态重置与停止规则的具体组合，仍是本项目的实现选择；以下论文不提供其最优性或收敛保证。

| 来源与原文位置 | 核实内容 | 适用范围 |
|---|---|---|
| Noels et al., *A Theoretical Framework for Soft-Information-Based Synchronization in Iterative (Turbo) Receivers*, 2005, DOI 10.1155/WCN.2005.117；§3.2，印刷p.121，PDF第5页 | 严格实现固定同步参数，让译码软信息达到稳定，再做EM更新；合并为每次仅一轮检测／译码是近似实现，尤其早期APP可能较差。多参数联合估计时，两次同步更新之间可能需要更多检测／译码轮数。 | 直接支持区分两类迭代、权衡APP准确度与复杂度。原文也报告合并更新在其引用的例子中性能损失很小，不能解读为低频更新总是更好。并不规定20轮或本项目门限。 |
| Krishnan, Colavolpe, Graell i Amat, Eriksson, *Algorithms for Joint Phase Estimation and Decoding for MIMO Systems in the Presence of Phase Noise and Quasi-Static Fading Channels*, IEEE TSP 63(13):3360–3375, 2015, DOI 10.1109/TSP.2015.2420533；§VII–VIII，作者稿PDF第10–13页，重点第12–13页、Table I及Fig.7 | 区分检测器与译码器之间的全局迭代LDet和LDPC内部迭代LDec。比较(2,30)、(15,1)、(10,1)：前两者在该实验中性能相近，后者成本更低但有小幅性能损失。 | 相位估计接收机中的直接调度实例。30是内部译码轮数，不是本项目相位周期；全局检测过程内部还有相位估计步骤，不能简写为该文每30轮仅更新一次相位。 |
| Shen et al., *LEO Satellite-Enabled Random Access with Large Differential Delay and Doppler Shift*, arXiv:2412.20806v1；Algorithm 1，第2、12–14、19–22行 | 每个未终止外层迭代执行第20行的相位更新。12–14行内循环是MRF消息更新。 | 不能用Shen为每20个完整接收机迭代检查一次的策略背书；也不能把MRF内部循环解释成本项目的20轮条件推断。 |

## 当前实现的对应关系

`src/configs/candidates/c_stmp_phase_shen_frames_20261103/shen_frames_physical.json`绑定`c_stmp_phase_selection_20261030/physical_no_hypotheses_legacy_stop.json`。配置的检查起点为20、间隔20；`C_STMP_phase_shen_frames_20261103/iterations.py`同时要求`due`与`ready`。因此实际更新间隔可长于20，论文依据应对应“固定参数期间进行多轮推断”的思想，而非替这组门限作证明。

本项目从神经模块取得信道／活动近似统计量，上述两篇同步论文主要使用检测／译码软信息。统计模型和参数更新均需独立核对，不能直接继承原文EM或MAP性质。11月4日失败样本对照同时改变调度、重置和停止，不能据其断言20轮最优。

## 可追溯来源

- Noels：[作者PDF](https://telin.ugent.be/~hs/full/j17.pdf)、[出版方](https://link.springer.com/article/10.1155/WCN.2005.117)。项目此前已有`phase_update_20261103/SOURCES.json`和C-STMP术语记录，本次重新核对原文，结论一致。
- Krishnan：[机构PDF](https://publications.lib.chalmers.se/records/fulltext/217287/local_217287.pdf)、[机构书目](https://research.chalmers.se/publication/217287)。
- Shen：[arXiv原文](https://arxiv.org/html/2412.20806v1#alg1)、既有本地`baseline_gfra_audit_20261023/shen2025_local.txt`。
- 两篇DOI均成功解析。Semantic Scholar API三次均返回429，采用作者／机构全文与出版元数据交叉核对，详见`METADATA_VERIFICATION.json`。没有将API失败标记为文献不存在。

## Material Passport

- Origin Skill: academic-research-suite / deep-research
- Mode: fact-check
- Status: completed, bounded claim verification
- Human read status: not asserted
- No experiment, training, mainline change or manuscript rewrite
