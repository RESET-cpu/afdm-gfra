# Cai：章节结构卡

2026-10-09。本卡仅核对章节层级、内容归属和论述顺序；不作语言风格全集、科学结论或新颖性评价。

来源：项目所存 JSAC 正式排版 PDF，16页，印刷页3575–3590；DOI 10.1109/JSAC.2026.3663274。标题层级与 https://arxiv.org/html/2506.00581v2 交叉核对。页码以下优先使用印刷页。

| 原文节标题 | 小节 | 起始页 |
|---|---|---:|
| I. Introduction | A. Contributions；B. Related Works；C. Organization and Notations | 3575 |
| II. System Model and Problem Statement | A. System Model；B. Problem Statement | 3577 |
| III. Turbo Message Passing Framework | A. Module A: Linear Estimator；B. Module B: Channel and Device Activity Denoisers | 3579 |
| IV. Learning Score-Based Generative Priors for MMSE Denoising | A. Bridging Score Function and MMSE Denoising；B. First-Order Score Matching；C. Second-Order Score Matching | 3582 |
| V. STMP-JADCE Algorithm | A. Overall Algorithm；B. Engineering Tricks；C. Pilot Design and Complexity Analysis | 3583 |
| VI. Simulation Results | A. Simulation Settings；B. Score-Based MMSE Denoising Performance；C. JADCE Performance | 3585 |
| VII. Conclusion and Discussion | 无字母小节 | 3588 |

III-B细分为信道H、活动变量α、活动加权信道X三个去噪器。IV在此基础上解释所需信道均值及方差如何通过一阶、二阶score学习获得。V再将框架与学习模块组合成完整算法，而非另起一节泛讲软件实现。

V-B包括阻尼与信道功率归一化；V-C连接作者的导频选择和相应计算复杂度。这里的导频设计与FFT复杂度属于该文具体方法，不能仅因章节仿照而移入本项目。

VI-A进一步分为信道数据集、网络结构与超参数、评价设置。在印刷页3585（PDF第11页），网络层表Table III、学习率、batch size、训练轮数、计算平台均在仿真设置中。该页已图像核对。

结构观察（paper-specific）：先说明推断框架需要哪些统计量，再推导学习这些统计量的方法，最后组装完整算法。Related Works位于引言内部；没有独立的一级Related Work、Network Training或Complexity Analysis章节。

对本项目的启示：可将已有Receiver Algorithm初稿拆成框架、条件矩与活动密度比学习、完整迭代三个层次。第三层不重复前两层推导，只负责调度、数值处理和成本。本文的分类器密度比推导需明确加入学习部分，不可误称Cai原有内容。
