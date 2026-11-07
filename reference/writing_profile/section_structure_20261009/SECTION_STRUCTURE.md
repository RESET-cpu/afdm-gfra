# 原文章节命名与本稿结构建议

日期：2026-10-09（Asia/Shanghai）。性质：章节结构与命名核对。Cai、Ding沿用已完成的本地PDF核对；新增核对Han、Arvinte、Ying、Shen、Mei五篇作者原稿中的相关标题及正文归属，详见[语料记录](corpus_manifest.md)。本轮只更新写作提纲与术语依据。

## 1. 原文结构

### Cai

来源：[本地正式版](../../literature/cai2026.pdf)，JSAC 2026，16页；[作者在线版本](https://arxiv.org/html/2506.00581v2)。完整标题和页码见 [Cai结构卡](style_cards/cai.md)。

| 节 | 原文标题 | 内容组织 |
|---|---|---|
| I | Introduction | 贡献、相关工作、组织与符号；相关工作不是独立一级章节 |
| II | System Model and Problem Statement | 系统模型，随后定义联合估计问题 |
| III | Turbo Message Passing Framework | 线性估计模块；信道、活动变量、活动加权信道三个去噪环节 |
| IV | Learning Score-Based Generative Priors for MMSE Denoising | score与MMSE条件矩的关系、一阶学习、二阶学习 |
| V | STMP-JADCE Algorithm | 完整算法、阻尼与功率归一化、导频设计及复杂度 |
| VI | Simulation Results | 设置、独立去噪评价、整体JADCE评价 |
| VII | Conclusion and Discussion | 结论与讨论 |

其论述顺序是：先明确推断框架需要哪些条件统计量，再说明如何学习这些量，最后组装完整迭代。IV是学习原理与目标推导，不是训练日志或配置说明。网络结构、层表、学习率、batch size、epochs和硬件放在VI-A2（印刷页3585）。

### Ding

来源：[本地接受稿](../../literature/ding2026.pdf)，TVT 2026，6页；[作者机构记录](https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/Learning-Sparsity-Pattern-An-Adaptive-Joint/991155194002346?institution=44SUR_INST)。完整定位见 [Ding结构卡](style_cards/ding.md)。

| 节 | 原文标题 | 内容组织 |
|---|---|---|
| I | Introduction | 背景、相关工作、贡献 |
| II | AFDM-GF-RA SYSTEM | 卫星AFDM系统与信道输入输出 |
| III | Proposed Joint Detection for AFDM-GF-RA | A.导频安排与双重稀疏模型；B.GNN-ASPL算法；C.离线训练；D.复杂度 |
| IV | Simulation Results | A.Simulation Setup；B.性能比较 |
| V | Conclusion | 结论 |

III-C（PDF第4–5页）介绍分层训练的先后顺序和式(28)的NMSE损失；IV-A（第5页）另给实际训练样本数、层数、学习率、batch size和计算平台。训练方法属于方法章，具体训练配置属于仿真设置。

## 2. 扩展文献中的命名依据

| 原文与定位 | 可复用的原文标题 | 本稿使用方式 |
|---|---|---|
| [Han，§III](style_cards/han.md) | Bayesian Receiver Design | III直接复用；在章首交代迭代结构 |
| [Cai，§III-B及§IV](style_cards/cai.md) | Channel and Device Activity Denoisers；Score-Based Generative Priors | IV以信道与活动去噪器为共同学习对象，并明确所采用的生成式信道先验 |
| [Arvinte，§II-D](style_cards/arvinte.md) | Score-Based Generative Modeling | IV内部生成式信道先验部分的术语依据 |
| [Ying，§V-D/E](style_cards/ying.md) | Overall Algorithm；Computational Complexity Analysis | 分别用于V及V-C；调整层级属于本文安排 |
| [Shen，§III-B、§IV](style_cards/shen.md) | Message Scheduling；CNN-Enhanced Detector | 前者用于V-A；后者仅说明可按学习模块的具体功能命名 |
| [Mei，§III、§IV-B](style_cards/mei.md) | Proposed Scheme；Computational Complexity Analysis | 参照简洁标题和复杂度小节的写法 |

上述单篇标题均属于paper-specific依据。相同复杂度小节标题在Ying与Mei中出现，属于limited证据；将已有短标题用于本稿不表示采用其算法。Cai、Ding、Ying在方法部分保留复杂度小节，属于recurrent的内容组织观察，但不规定其父章节的名称。Arvinte则把复杂度与消融放在结果讨论内，说明仍应按本稿论述需要安排。

本稿III、V采用原文标题；IV以Cai定义的信道与活动去噪器为共同对象，用Learning明确学习目标与方法，并用with Score-Based Generative Priors交代信道先验的表征方式。IV标题属于基于原有术语的描述性改写。信道条件矩学习与活动密度比学习分别推导，公式、近似与算法来源在正文就近说明。官方边界见[核对记录](twc_official_requirements.md)。

## 3. 推荐本稿采用的目录

按用户意见，方法部分采用三个技术章节，全文共七节。第三节给出总体迭代更新及所需统计量，第四节介绍生成式信道先验和活动证据的学习，第五节给出整体算法执行及复杂度。标题描述内容，不另命名算法。

### I. Introduction

交代卫星AFDM免授权接入问题、现有JADCE与学习方法、本文与已有工作的区别及贡献。相关工作放在本节；贡献按可证实的模型、方法和结果分别写。

### II. System Model

- A. Terrestrial-Satellite Link Model
- B. Transmission Scheme
- C. Problem Formulation

章首先说明接入场景、阵列、接入块和活动状态；A给出物理链路，B把AFDM波形、信道算子、导频和接收关系连续推到矩阵观测，C定义待估量、工作后验与估计目标。小节结构与标题依据Shen §II-A–C；AFDM信号链参考Ding §II，贝叶斯表述参考Cai §II-B。已知有效相位、已知噪声及工作先验近似在首次使用时说明。该结构已获用户确认并落实到当前分章节源稿。

### III. Bayesian Receiver Design

- A. Linear Estimation
- B. Channel and Activity Denoising
- C. Extrinsic Message Update

在第二节已定义的工作后验下，先概述一轮迭代中线性估计、联合去噪及反馈的关系，再推导各模块的更新方程，以及非线性模块需要的条件均值、条件误差和活动概率。局部后验、联合矩与Gaussian外信息在这里连接成近似贝叶斯推断过程；学习模块先作为已定义的函数接口，具体目标留待IV解释。采用来自Cai等已有方法的步骤应就近归因，不把全部框架写成本文原创。

### IV. Learning Channel and Activity Denoisers with Score-Based Generative Priors

- A. First-Order Score Matching
- B. Conditional Error Estimation
- C. Density Ratio Estimation
- D. Offline Training

本节围绕第三节的信道与活动去噪器，说明其所需统计量的学习方法。先从Gaussian扰动信道分布及其score表示引入生成式先验，随后由IV-A–C说明Tweedie关系及一阶目标、冻结有限一阶均值后的二阶条件MSE目标，以及活动分类器BCE最优解、密度比与活动先验修正。IV-A/B为信道去噪提供均值和条件误差，IV-C通过密度比学习构造活动概率。IV-B按实际学习目标命名，正文再说明它与理想二阶score关系的联系。IV-D说明训练数据的构造原则、网络输入输出、训练先后关系、一阶教师冻结及两类查询的共同噪声律。实际网络层数、宽度和优化器数值留在VI-A。

保留有限网络目标与理想条件矩的区别。不能把当前二阶平均迹读数扩大表述为逐坐标精确Hessian。活动分类器作为密度比学习环节单独说明，不将其归称为生成模型；其性能收益留待配对实验验证。

### V. Overall Algorithm

- A. Message Scheduling
- B. Damping and Stopping Criteria
- C. Computational Complexity Analysis

V-A将已训练模块嵌入第三节的更新式，给出完整伪代码及初始化、支持范围、方差处理、site接受/复用、消息调度和输出。V-B定义阻尼、停止统计量及计数逻辑，具体实验取值集中在VI-A。V-C使用本项目有效算子、SVD和三个网络的实际成本分析复杂度，不能照搬Cai基于特定导频的FFT表达式。

第三节负责推导每轮更新，第五节通过引用这些公式说明接收机的执行顺序及数值处理；第四节的离线训练与第五节的在线推断分别交代。数值停止条件不写成全局收敛定理。

### VI. Simulation Results

A. Simulation Setup集中呈现系统与数据集参数、网络配置、训练超参数、接收机取值、指标和对比条件。其余小节沿用已确定实验矩阵，本轮不重新改动实验方案。

### VII. Conclusion

待完整实验后写结论及定量总结。

## 4. 现有初稿如何迁移

| 现有初稿部分 | 推荐位置 |
|---|---|
| 系统模型及问题表述 | II，章首概述与三个小节；公式保持不变 |
| Linear Estimation and Extrinsic Queries | III-A |
| Conditional Gaussian Messages and Joint Moments | III-B/C；实现接受/回退细节交给V-A |
| Learning the Channel Mean and Conditional Error | IV-A/B |
| Activity Detection by Density Ratio Estimation | IV-C；III-B先定义所需活动概率及密度比 |
| 训练先后顺序、教师冻结与查询构造原则 | IV-D |
| Iteration Schedule and Implementation中的算法、阻尼和停止 | V-A/B |
| 该小节的复杂度段落 | V-C |
| 数据集大小、网络宽度、学习率等实际配置 | VI-A |

当前源稿：[main.tex](../../../paper/main.tex)，正文位于 [sections/](../../../paper/sections)。章节拆分与第二章三小节重排已完成；迁移前的 [draft.md](../../../paper/history/phase4_sections_20261008/draft.md)保存在历史目录。此次整理保留III–V正文与全部公式，不调整实验配置。

## 5. 术语与范围

本稿沿用[项目术语依据](../../../paper/STMP/docs/TERMINOLOGY.md)中的既有推断与学习术语，并补充本次标题的原文定位。小节中的条件误差估计、外信息更新以及阻尼与停止条件是对现有公式的简短描述，不宣称整句均为某篇论文的原始小节标题。目录不作为新方法名或新缩写。
