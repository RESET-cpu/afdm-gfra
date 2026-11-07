# Ding：章节结构卡

2026-10-09。本卡仅核对章节层级、内容归属和论述顺序；不按六页篇幅推断稿件类别。

来源：项目所存TVT作者接受稿，共6页；DOI 10.1109/TVT.2026.3729877。作者机构记录：https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/Learning-Sparsity-Pattern-An-Adaptive-Joint/991155194002346?institution=44SUR_INST 。以下为PDF页码，不是最终期刊页码。

| 原文节标题 | 小节 | 起始页 |
|---|---|---:|
| I. Introduction | 相关工作及三项贡献位于引言内，没有字母小节 | 1 |
| II. AFDM-GF-RA SYSTEM | 无字母小节 | 2 |
| III. Proposed Joint Detection for AFDM-GF-RA | A. Pilot Arrangement and Dual Sparsity Model；B. Proposed GNN-ASPL Algorithm；C. Offline Training of GNN-ASPL；D. Complexity Analysis | 2 |
| IV. Simulation Results | A. Simulation Setup；B. Performance Comparsion（原文拼写） | 5 |
| V. Conclusion | 无字母小节 | 6 |

III-A在第2–3页把导频组织与稀疏观测建模接到系统模型；III-B在第3–4页依次介绍AMP估计与GNN稀疏先验更新；III-C从第4页右栏延续到第5页左栏，给出分层训练顺序及NMSE损失式(28)；III-D给出按模块计算的FLOPs式(29)。第4、5页已图像核对。

IV-A在第5页左栏给出系统参数及具体训练配方，包括十层网络、训练样本数量、学习率、batch size和设备。IV-B从同页右栏开始；文本提取时两栏可能交错，不能把其读取顺序误当章节顺序。

结构观察（paper-specific）：系统模型之后，算法、离线训练与复杂度集中于一个方法章节。离线训练是方法小节，具体训练数值属于仿真设置。没有单独的一级Related Work、Network Training、Implementation或Complexity章节。

对本项目的启示：可以学习其系统到观测、再到推断的紧凑衔接；不宜照六页稿件的压缩程度，把本项目的矩推导、密度比证明及完整迭代全塞入一个过长章节。是否合并章节由实际内容长度决定，并非由期刊名决定。
