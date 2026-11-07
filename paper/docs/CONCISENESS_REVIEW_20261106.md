# 全文防御性语言与冗余表达复查

2026-11-06。作者随后要求“能删就删”，并要求进一步压缩变量与维度说明。**以下建议已实施，两版 PDF 已更新。** 下文保留修改前的原句和行号；具体差异及核验见[实施记录](../checks/conciseness_revision_20261106/README.md)。

**有可删的防御性评论，也有明显的重复说明。前者主要在完整稿附录，后者集中在方法衔接和实验设置。** 上轮“没有需要强制重写的新段落”的判断偏重技术正确性与常规语言错误，没有充分评估这些句子是否值得占据篇幅。

11 月 4 日已完成的六处精简没有重新计入。本轮由作者主动要求检查全文，包含当时未处理的附录评论和后来新增的版本说明。

## 最值得先删的四类表述

### 1. 实验没有讨论失效原因，却主动声明不能解释失效原因

位置：[附录 A-C，第 60 行起](../sections/appendix_evaluation_protocol.tex#L60)。

> These results describe the effect of replacing the activity-probability calculation within each receiver; they do not identify the internal cause of failure to satisfy the stopping criterion.

**建议整句删除。** 前半句已在正文 VI-C 和附录 A-A 交代；后半句回应了文中没有提出的机制主张。该段到迭代上限比例的定义结束即可。

### 2. 已说明关闭提前停止，又说明没有填补提前停止后的曲线

位置：[附录 A-E，第 94 行起](../sections/appendix_evaluation_protocol.tex#L94)。

> No curve is padded after an early stop.

**建议删除。** 同段已明确各方法执行 300 轮且关闭提前停止，这一句没有增加信息。

### 3. 参数选择的事实后面，又加一条“这不证明什么”

位置：[附录 A-D，第 82 行起](../sections/appendix_evaluation_protocol.tex#L82)。

> These damping factors were selected retrospectively and do not constitute independent validation of a fixed rule across all candidate device counts.

建议压为：

> These damping factors were selected retrospectively.

保留实际选择方式，删去没有对应主张的否定尾句。前面各设备数采用的阻尼及特殊场景处理已有具体说明，无须再抽象辩解一遍。

### 4. 反复保证“达到上限的输出也保留”

位置：附录[第 42 行](../sections/appendix_evaluation_protocol.tex#L42)、58、75、101、106、112 行附近。

> All finite outputs are included in the reported metrics, including those that reach the iteration limit.

后文又分别写了 `These 17 outputs are retained in the NMSE`、`All outputs are retained in the reported metrics`、`both outputs are retained` 等。

**建议统一在 A-B 保留一次纳入规则，删除后文重复的保留声明。** 各实验达到上限的具体数量仍可直接报告。正文 VI-C 的 `All such runs are included in AER` 可保留，因为主稿不含附录；这里需要清理的是同一附录内反复自证。

## 正文中可以明显压缩的地方

### 5. 第六章开头的工作稿状态说明

位置：[VI 开头，第 4–11 行](../sections/06_simulation_results.tex#L4)。

原段先列已更新图表，再列历史曲线，最后又补：

> The numerical comparisons for these figures refer to those earlier checkpoints.

最后一句只是重复前一句。整个状态说明可以压为：

> GP-MP uses the white-noise-trained networks in Fig. 5 and Table III. Its results in Figs. 4 and 6–10 use earlier checkpoints with different training perturbations and await replacement.

这里只用当前显示编号展示候选句，实际修订时沿用现有交叉引用。曲线替换完成后，这段工作状态说明整体移出论文。

### 6. 第四章已经定义的白噪声模型，第六章重新讲了一遍

位置：[VI-A2，第 167–172 行](../sections/06_simulation_results.tex#L167)。

原段除给出方差采样范围外，又说明复噪声协方差、与信道独立、实噪声协方差、损失与预条件。前三项已由 IV-A 式 (23) 及相邻文字给出。

建议只保留本节新增设置，并引用训练定义：

> We sample $v$ uniformly on a logarithmic scale over $[10^{-3},10^2]$ and train the denoiser using (27) with the preconditioning in (44).

这样保留了采样范围、目标函数与实际预条件，不重复推导实复噪声的换算。

### 7. SVD 只计算一次被说了三遍

位置：[V-C，第 232–259 行](../sections/05_overall_algorithm.tex#L232)，以及 Algorithm 1 的循环前步骤。

本节先说 SVD `is reused across iterations`，随后把其代价列为 `per block`，末尾又说：

> Here $C_{\rm phase}=0$ for known phases, and the SVD is computed once.

**建议删除末尾的 `and the SVD is computed once`。** 已知相位时相位估计代价为零这一新信息保留。

### 8. Bernoulli–Gaussian 混合分布前后解释两次

位置：[III-B3，第 124–129 行](../sections/03_bayesian_receiver_design.tex#L124)。

先写活动时等于信道、非活动时为零，再写 Gaussian 近似，随后又说明零分量和 Gaussian 分量各占什么概率。可以直接给出混合近似及权重：

> Approximating the active-channel posterior by a Gaussian with mean $\mathbf H_k^{\rm post}$ and covariance $t_k\mathbf I_D$ gives a Bernoulli–Gaussian approximation with active probability $p_k$. Its mean is

随后接原式 (19)，沿用原有 Liu、Cai 引用。这是局部合句，不需要改整段推导。

### 9. 分类器的密度比含义在相邻位置重复

位置：[IV-D，第 151–178 行](../sections/04_generative_priors.tex#L151)。

前面定义平衡类别，式 (32) 已给出最优 logit 等于 log density ratio，后面又写：

> With balanced training classes, the classifier output directly estimates the log density ratio …

可以把它和接下来代入活动赔率的句子合并：

> Using the classifier output as the log density-ratio estimate and setting $\mathbf F_k=\mathbf F_\theta(\mathbf R_k,v)$, (30) gives

随后接原式 (33)，原 Menon 引用保留。读者从训练结论直接进入使用方式，不再重新启动一次解释。

## 附录里过细的工作记录

### 10. 方法介绍在附录重复，但没有增加附录所需设置

位置：[A-A，第 20–27 行](../sections/appendix_evaluation_protocol.tex#L20)。

> The receiver comparisons evaluate the complete configurations.

这是笼统说明，建议删除；保留紧随其后的“消融仅改变概率计算”即可。

> Only the estimated phases are passed to the receiver; the front-end gain and power estimates are not used to initialize channel or activity messages.

V-B 已明确只有相位传入接收机并保持固定。建议删掉这一重复句，保留 GP-MP-EP 与对应 GP-MP 使用相同权重和接收机的说明。

### 11. 结果如何保存和复用的细节过多

以下内容更适合已有实验记录，论文直接说明采用的数据和设置即可：

| 位置 | 现有表达 | 建议 |
|---|---|---|
| [A-B，第 35 行](../sections/appendix_evaluation_protocol.tex#L35) | `the first 500 of the planned 1,000 scenes` | 改为 `500 paired scenes`；原计划规模不影响当前实验定义。 |
| [A-C，第 51–54 行](../sections/appendix_evaluation_protocol.tex#L51) | 两组重新计算，另外两组复用，并列出输入、配置、精度核验 | 前一句已说明共同观测、已知相位和估计噪声；后面直接接 `All four use single-precision inference with TF32 disabled.`，复用核验过程留在实验记录。 |
| [A-E，第 118–120 行](../sections/appendix_evaluation_protocol.tex#L118) | `The profile-D outputs are reused from the saved SNR experiment after matching inputs and configurations.` | 删除；正文已说明各信道配置的设置和场景数，此处不必叙述数据整理过程。 |

这是压缩工作流程说明。关于子集在中途查看结果后选定、参数事后选择等会改变实验解释的事实，保持简短的一次性陈述。

## 较小的可选精简

- [II-C，第 240–243 行](../sections/02_system_model.tex#L240)：块稀疏与非活动块为零可以合为一句：`The matrix $\mathbf X$ is block-sparse, with $\mathbf X_k=\mathbf0$ for inactive devices.`，保留原 Cai 引用。
- [IV-A，第 39–40 行](../sections/04_generative_priors.tex#L39)：式 (24) 前已说 conditional mean，式后再解释“这给出了实表示下的精确条件均值”可删；保留 score 的定义即可。
- [图 3 图注，第 16 行](../sections/05_overall_algorithm.tex#L16)：`saved input--output pair` 中的 `saved` 可以删掉。这是此前 R02 的已有可选项，此次按作者的精简要求一起列出。
- [VII，第 22–24 行](../sections/07_conclusion.tex#L22)：`These results support the use of learned effective-channel priors ...` 是泛化收尾，没有新增结果。若追求紧凑，可让结论结束于前一句具体实验发现。此前认为该句可保留；本轮因作者主动要求查冗余，将删去它列为风格选择，不把它说成错误。

## 整体判断

摘要和引言中的数学衔接主要承担贡献解释，不是本轮最值得删的部分。第六章的结果分析也已经比较克制。最有收益的处理是：删掉附录的无对象辩解，合并重复的纳入规则，移走核验流水账，再压缩正文里已经由相邻公式或前章说清的重复解释。

本报告中的候选句由现有表述删减、合并而来，没有新增技术术语、文献或实验结论。初次审阅未改正式稿；作者授权后的实施如下。

## 授权后的实施

上述 11 组建议及四处可选精简均已落实。另按作者要求删除重复的列向量和消息矩阵尺寸、向量化时逐层索引顺序、网络输入维度的再次展开、设备更新索引的泛泛说明；合并导频定义、空间协方差和指标解释。vec 与单位阵在 Notation 中各定义一次，重要矩阵首次出现的尺寸及行列含义保留。

附录 SNR 配置数量同步修正为九种、其余八种已知相位。按去除公式和命令后的英文词项粗计，净减少约 410 词。公式、算法步骤、三张表和十幅图保持；主稿 13 页，完整稿由 15 页减至 14 页。编译、交叉引用和版面检查通过。
