# 第 II–VI 章叙述修订

日期：2026-11-06。作者要求进一步修改正文中的说明书式表达，并追加要求：不作防御性说明，不反复强调优势，让叙述自然推进。

## 本轮处理

| 位置 | 原有问题 | 实际修改 |
|---|---|---|
| II-B/C | 导频定义、跨帧关系和观测堆叠连续以操作指令起句。 | 合并导频定义及其条件；用共同多普勒与标量相位关系承接共享信道表示；将堆叠操作写成观测模型的构成。 |
| III | 部分段落只是预告先推导什么、再计算什么。 | 从两个模块分别利用的似然与先验进入推断；用活动假设下的去噪问题引出信道矩；说明联合协方差中已有的信道与活动不确定性，再接外信息。 |
| IV | 训练、输出重排和章节指引分散，分类器的作用被操作细节隔开。 | 连起得分与信道矩、训练与实际输入、均值导数与平均方差、分类输出与活动先验。保留必要的条件概率术语；单去噪器的收益在方差关系处说明一次。 |
| V | 输出值、Gaussian site、回传消息以及参数估计逐项罗列。 | 按学习量如何构成 GPJD 更新来组织；相位估计按观测模型、目标和所得相位推进；合并阻尼说明；按预处理和迭代组织复杂度。 |
| VI | 训练噪声、损失、优化和模型选择分散；部分设置像执行说明。 | 将同一网络的训练条件合并；先说明分类器的估计对象，再描述输入与结构；统一配对场景和活动更新比较的表述。原有结果趋势、代表性收益及不利比较均保留。 |

摘要、引言、结论、附录、所有数学表达、图表与算法框不变。未新增实验、性能结论或机制假设。工作稿数据状态说明保持。

## 代表性修改

**III-B：从操作预告转为估计关系。**

原文：Following ... we first derive the channel estimate under the active hypothesis and the posterior activity probability, and then combine them to estimate ...

改后：Joint denoising combines the channel estimate under the active hypothesis with the posterior activity probability to estimate ...

后句直接接每个设备的 Gaussian 输入与局部观测模型，不再重复列推导顺序。

**IV-C：在关系成立处交代收益。**

改后在条件均值导数与协方差恒等式之后说明：Thus, the average variance can be estimated from the derivatives of the trained denoiser without training a separate variance model.

该含义已在确认后的引言与结论中存在，此处将它落到已有公式；随后仍保留随机方向有限差分估计，不改成精确的网络输出保证。

**IV-D：明确分类输出的统计含义。**

原文以 Taking the log odds 起句，继而分别列积分、分类和输出操作。

改后先说明活动概率通过似然比依赖两种观测分布，再给出 log-odds 形式；平衡训练下的最优 logit 接到密度比估计，最后与接收机活动先验结合。训练类先验与接收机先验仍有明确区别。

**V-B：正面描述相位估计的用途。**

原文：Only the phases are passed to GP-MP ... The single-path approximation is confined to phase estimation ...

改后：The estimated Doppler determines ... GP-MP uses the resulting phases throughout its iterations, with channel denoising based on the learned prior ...

单主径近似仍在相位观测模型处明示；相位在 MP 前估计一次、后续固定的执行方式不变。

**VI-A2：将训练设置合为完整段落。**

去噪器段依次交代损失与预条件、噪声方差采样、优化参数、验证选择及 STMP 对照条件。分类器段接固定去噪器后的训练与验证。全部样本量、轮数、学习率、批量大小及噪声条件保持。

## 文献与本稿内容的对应

本轮重新读取 Cai 期刊版 PDF pp.5–9、11（印刷 pp.3579–3583、3585）和 Shen 本地版 PDF p.3 的完整相关段落及上下文。下表区分原段组织、已有技术出处及本稿表述，不将改后句称为原文逐字引用或逐段一一对应。

| 本稿位置 | 原文位置及借鉴内容 | 本文适配 |
|---|---|---|
| II-B/C | Shen §II/II-A，PDF p.3：先界定传输场景和物理量，再给模型。Cai §II/III 的观测与推断对象沿用既有核对。 | AFDM 独立调制、共同多普勒、参考信道与有效导频的关系来自本稿既有式 (6)–(10)，不是 Shen 的 AFDM 结论。 |
| III 开头、III-A | Cai §III 首段及 III-A，PDF p.5，式 (6)–(9)：似然/先验分工、Gaussian 乘积与外信息。 | 改为本稿多帧似然与既有共享方差，没有引入原文的系统极限保证。 |
| III-B1 | Cai §III-B，PDF pp.6–7，式 (20)–(23) 及相邻段：Gaussian 输入对应信道去噪与均值/方差。 | 活动假设及近似符号保留；算法计算仍引用本稿 V-A。 |
| III-B2 | 本稿既有式 (19)–(21)。 | 保留真实学习先验下的活动边缘似然，未改成 Cai 式 (30) 的 Gaussian 活动公式。 |
| III-B3 | Cai §III-B3，PDF pp.7–8，式 (32)–(42)：混合后验的矩与回传外信息。 | 本稿空间协方差与公共平均方差公式不变；两类不确定性的说明是对现有公式及已确认贡献的文字解释。 |
| IV 开头、IV-A/B | Cai §IV 开头、IV-A/B，PDF pp.8–9，式 (43)–(49)：得分与去噪的联系、DSM 目标、跨噪声水平训练。 | 实坐标表示、直接去噪参数化及连续噪声采样均沿用本稿。 |
| IV-C | 沿用已核对的 Dytso 正式版 §III Proposition 1、式 (17)，印刷 p.1885；Manor–Michaeli §3.2 式 (11)、§4.1 式 (15)。 | 本稿平均方差的随机方向有限差分计算不变；不将其声称为原文完全相同的数值算法。 |
| IV-D | 沿用 Menon–Ong §3 式 (6)–(8)、§4.2 式 (16)–(17)，印刷 pp.305–306。 | 平衡分类训练与接收机先验校正按本稿已有推导叙述，不归于 Cai。 |
| V-A | Cai §V-A，PDF p.9：学习输出与 TMP 框架的衔接；Gaussian site 沿用 Vehtari §2.1 的既有出处。 | 使用本稿单去噪器方差与分类活动更新，保留 site 更新及联合估计的实际顺序。 |
| V-B | 噪声与相位沿用既有 Wax–Kailath、Tipping–Faul §2.1、Zhu 等出处；阻尼对照 Cai §V-B1，PDF p.9。 | 只修改叙述。单次相位估计、固定相位、方差尺度更新、归一化和阻尼参数不变。 |
| V-C | Cai 复杂度段，PDF p.11：矩阵运算与网络前向计算分别计入。 | 本稿 SVD、相位估计和有限差分的计算次数及阶数保持。 |
| VI-A/B | Cai §VI-A2/3、VI-B 开头，PDF p.11：结构说明、训练条件、评估条件、单独去噪比较。 | 仅借鉴段落任务和组织，不搬用其网络层数、噪声集合或实验设置。 |
| VI-C/E | 本稿已有活动更新比较与跨 profile 协议。 | 合并重复范围说明；Gaussian 更新下 STMP 优于 GP-MP 的比较和跨 profile 相对 STMP 的限制保持。 |

完整改前改后见 [CHANGES.diff](CHANGES.diff) 与 [EDIT_LOG.json](EDIT_LOG.json)。修订前源码和 PDF 保存在 `before/`。

## 核验

- 两版编译成功，正文版 13 页、含附录版 14 页；42 条参考文献、59 个公式标签。
- 五章的行内数学内容集合、陈列公式、标签顺序、引文集合、图表和算法框均保持。
- 摘要、引言、结论、附录、书目及图文件与本轮开始时的副本一致。
- 完整稿第 2–14 页与正文版第 10–13 页已目视检查；两版前 9 页逐像素相同。
- 无越栏、缺字、未定义引用或 Underfull 警告；原有三幅图 PDF 版本高于输出版本的提示仍在。
- 未启动训练或实验。

核验数据见 [VALIDATION.json](VALIDATION.json)。
