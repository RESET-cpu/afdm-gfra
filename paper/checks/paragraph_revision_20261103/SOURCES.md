# 本轮句子与术语依据

以完整技术对象、原段的操作顺序与适用条件核查。下列“本文写法”是忠实适配，不表示整句逐字摘自原文。具体每段来源见 [PARAGRAPH_MAP.md](PARAGRAPH_MAP.md)。

| 表述或操作 | 已读原文定位 | 本文写法与适配 |
|---|---|---|
| linear estimation、Gaussian posterior、extrinsic message | Cai 正式版 III、III-A，PDF p.5／印刷 p.3579，式(6)–(11)；原文用 Gaussian 乘积得后验，再以商求外信息。 | 同样按后验、标量协方差近似、外信息相除与传送叙述。完整矩阵估计来自本文模型，不复制 Cai 的部分正交简式。 |
| conditional mean、conditional covariance、first-order score function、Hessian | Cai IV-A，PDF p.8／3582，式(43)–(45)；Dytso 正式版 p.1／1883 式(3)、p.3／1885 III 节 Proposition 1 式(17)。 | 把定义、特例接回公式；复数实数表示、一般协方差与 Jacobian 转置约定按本文定义保留。 |
| 条件 Gaussian 密度的 score；去噪器参数化 | Cai IV-B，PDF p.8／3582，式(46)–(48)，明确比较边缘对数密度梯度与条件对数密度梯度；Vincent §4.2 是既有原始方法来源。 | score 的对象改写为 conditional Gaussian density；加权 DSM 与去噪器损失之间的代入为本文推导，保留固定协方差条件。 |
| correlated noise、colored Gaussian noise | Shastri 正式版 III-B，PDF p.8／535，式(38)–(40)，段末继续说明如何从干净样本和噪声分布生成训练输入。 | 采用有色 Gaussian 噪声训练的描述；Kronecker 协方差和显式 C 条件输入来自本文实现。原文 corr+corr 网络结构没有移植到本文。 |
| Monte Carlo method、有限差分求散度 | [Metzler 作者稿](https://arxiv.org/pdf/1406.4175)，V-B，PDF p.15。原文用随机扰动的去噪差分估计散度，再对样本平均。 | 保留导数近似和随机迹估计两项操作；本文采用中心差分、随机符号和协方差权重。参数指引接在这一段末尾。 |
| density ratio estimation、分类训练、logistic loss | [Menon–Ong](https://proceedings.mlr.press/v48/menon16.pdf)，§2.1–2.2 PDF p.2，§4.2 PDF p.3 式(16)–(17)。原文以 logistic link 连接分类输出、类概率和密度比。 | 二元交叉熵与理想函数最优解集中说明。输出段直接写减去 logit(pi_tr)，再代入本文的活动先验。`training prior log odds` 不再作为紧缩名词组合。 |
| 神经网络参数与交叉熵训练的说明顺序 | Shen IV-A2，PDF p.11，式(60)–(61)。先定义参数化网络与输出，再给交叉熵目标。 | 采用这一描述顺序；本文的标签是设备活动状态，未使用原文的多类符号标签和 Softmax 输出。 |
| site approximation | [Vehtari et al.](https://www.jmlr.org/papers/volume21/18-817/18-817.pdf)，§2.1，pp.5–6。局部因子近似与 cavity 的乘积用于近似局部更新。 | 保留原术语，明确近似的是信道先验，形式由 Gaussian 公式直接给出；相除与相乘恢复条件均值、方差放在同段。 |
| Gaussian 方差的期望目标；damping factor | Vila–Schniter 正式版 III-A，PDF p.4／4661，式(22)–(27)；Cai V-B1，PDF pp.9–10／3583–3584，式(57)–(58)。 | 方差更新对象为本文 Gaussian 输入；kappa 的缩放和阻尼为实际更新。双向消息阻尼按 Cai 原段集中说明，保留本文首次迭代及截断设置。 |
| singular value decomposition (SVD) | Rangan–Schniter–Fletcher 作者稿 III，PDF pp.3–4，式(11)、Algorithm 2；原文说明先做分解、迭代中复用分解因子。 | 使用已核到的完整名称，删除 thin 修饰。Q 个奇异值、更新式与运算次数来自本文矩阵尺寸和算法，不套用 VAMP 的渐近结论。 |

Cai 段落定位沿用[原段索引](../cai_paragraph_alignment_20261103/SOURCE_INDEX.json)；本轮再次阅读的 Cai、Shen、Dytso、Shastri、Vila 页面文本及原 PDF 哈希保存于 [LOCAL_SOURCE_PAGES.json](LOCAL_SOURCE_PAGES.json)。Rangan 原文与哈希见此前 [CORPUS.json](../prose_terminology_20261103/CORPUS.json) 的 `rangan2019_vamp.pdf`。没有新增参考文献或作者命名；MFLE、GPJD、GP-MP-CCD 等仍按既有作者命名记录处理。
