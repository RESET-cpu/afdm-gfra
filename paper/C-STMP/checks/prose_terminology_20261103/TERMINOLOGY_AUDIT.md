# 当前稿件完整搭配、操作用语与正文压缩核查

2026-11-03。对象为 `main.tex` 实际编入的 I–VII、附录 A–B、三张方法图，以及 `main_full.tex` 增加的附录 C。未编入的历史章节不作为当前论文内容。

## 判断标准

本轮以“**同一对象、同一操作下的完整表达是否自然**”为准。分别找到两个单词，不能证明其组合是文献用语；找到一个组合在其他研究中出现，也不能证明它适合本文的位置。Cai、Shen 是主要行文参照，其他文献用于本文确实增加的密度比、导数方差、相关噪声去噪和数值优化操作。

下表区分完整用语、公式支持的操作描述、本文命名和应替换的组合。普通连接词、矩阵下标和自定义变量符号不逐个包装成专业术语。“未检出”只针对所核对版本，不表示所有文献都不存在。

本地 PDF 建立了 55 份文本索引，重点原文的整词搭配与页码保存在 [PHRASE_EVIDENCE.json](PHRASE_EVIDENCE.json)。索引保留 PDF 页序；扫描对 Unicode 连字做规范化，并结合原段落判断，参考文献表中的匹配不作为方法用语证据。

## 实际改动的搭配

| 原表达／原位置 | 判断 | 当前处理 |
|---|---|---|
| channel moments、conditional channel moments；III/V | 范围过宽，实际只用均值与平均方差 | channel mean and variance；接上定义后用 these estimates |
| conditional channel moments；附录 A 相位更新 | 此处用完整协方差，不能机械改成 variance | conditional channel mean and covariance |
| Channel moments、Joint moments；Fig. 3 | 图中各节点对应的统计量不同，笼统标签不利于阅读 | Mean and variance；Mean and covariance，与节点公式逐一对应 |
| activity evidence、Gaussian evidence；VI 表格/C | evidence 是已有贝叶斯概念，但本稿混用它指密度比、概率和整套计算 | 分别写 activity probability、learned density ratio、Gaussian approximation；表头用 Probability calculation |
| Gaussian-site probability；VI | 不是此处有必要建立的名称 | probability from the Gaussian approximation |
| covariance-weighted score matching；IV | 可理解的描述性组合，未作为本稿所引文献的固定名称确认 | score matching weighted by Σ，直接说明权重 |
| output-by-input Jacobian；IV | 把矩阵约定写成复合修饰语，不必要 | Jacobian；保留导数定义与乘法次序 |
| training posterior log odds；IV | 多层名词堆叠，修饰关系不清 | posterior log odds under the training distribution |
| receiver activity probability；IV | receiver 修饰语多余 | activity probability |
| block-fixed random sign vector；V/VI | 项目实现缩写，未在 Cai/Shen 中确认这一完整搭配 | random sign vector … reused across iterations |
| new-message weight；V/VI/C | 给 damping factor 又起了一个称呼 | damping factor；公式保留新消息的权重约定 |
| first-order atom approximation；VI 基线 | 已有文献采用更明确的操作名称 | first-order linear approximation of the dictionary；Wei IV-B |
| activity readout、readout rules；VI/C | 软件式说法；这里描述二元判决 | activity decision rules |
| sparse-recovery kernels；VI | kernel 容易被理解为核函数，实际指四种算法 | sparse-recovery methods |
| gain-refitting cost、refit the gains；V/A | 工程式简写 | gain-estimation cost、re-estimate the gains |
| Doppler aliases；A | aliasing 本身有文献，但此处没有必要新增该组合名 | 直接给出“产生相同帧间相位的 Doppler shifts”及其公式 |
| differentiable waveform branch；A | branch 的对象不明确 | an interval where the waveform is differentiable |
| phase slopes、constant device rotations；A | 本文特定参数化，被写成似乎已有的操作名称 | 直接写优化 β_k 和每设备的 constant phase |
| phase-policy selection；C | 未定义 policy，容易让读者联想到另一种策略学习 | phase-update settings |
| query variance；C | query 是代码内部习惯，不是接收机推导需要的对象名 | input variance |
| valid-moment iterations；C | 生硬的复合标签，掩盖具体条件 | iterations with stable decisions and valid mean and covariance estimates |
| native convergence criterion；C | native 不描述数学收敛性质 | receiver stopping criterion |
| clean-channel bank、epoch budget；C | 具有内部实验记录口吻 | clean training channels、number of denoiser training epochs |
| fixed-noise validation loss、checkpoint selection；VI | 信息需要保留，但压缩搭配不够自然 | validation loss under fixed noise realizations、model selection |
| indicator function α_k；II | α_k 在这里是随机二元变量；判决才使用指示函数 | binary activity variable |

### posterior moments 的具体结论

本轮开始时，可编译正文中的相关原句主要是 `channel moments`、`conditional channel moments`，图中还有 `Joint moments`。用户提出的 `posterior moments` 是同类问题的代表。

- Cai 正式版 PDF p.6，III-B1，式(16)–(18)附近确有 **matched first- and second-order moments**；这不能当作其使用 **posterior moments** 这一完整搭配的证据。Cai 对待计算量主要直接说 posterior mean 和 variance。
- Shen 本地版本未检出 moment/moments；IV-A（PDF p.11）使用 **posterior means and variances**。
- **posterior moments** 这个完整搭配确实见于 [Manor–Michaeli](https://arxiv.org/abs/2309.13598) §3.2、Theorem 2（本地 PDF p.4）。该文讨论后验高阶统计量；它只能证明完整搭配存在，不能决定本文应采用它。
- 因而本稿仍将这些概括词全部改成实际计算的 mean、variance 或 covariance。替换依据是对象与上下文，不是声称 moments 在数学上错误。

## 保留用语与操作的来源、位置

以下按当前稿件顺序核查。相同概念跨章重复使用时合并登记，避免把每次出现都算作一个新术语。

| 当前用语／操作 | 原文定位或数学依据 | 使用判断 |
|---|---|---|
| grant-free random access；joint activity detection and channel estimation | Cai 摘要、I–II；Shen I–II | 整体任务一致，保留 |
| GNSS-independent；large differential delays and Doppler shifts | Shen 摘要、I–II，PDF pp.1–4 | 对应免设备预补偿的系统条件；保留 |
| AFDM；DAFT；IDAFT；chirp-periodic prefix | Bemani II–III；Ding II；既有来源账本与当前波形公式 | 原有波形名称；分数延迟波形和长 CPP 的具体表达是本文模型，不将整个公式冒充原文 |
| doubly dispersive channel；fractional delays/Doppler shifts | Bemani III；Huang II，PDF p.2 | 时变与多径对象对应，保留 |
| effective channel matrix | Huang II；Ding II | DAFT 后的矩阵；保留 |
| channel tensor | Shen 式(9)给出三索引有效信道；本文明确给定数组尺寸 | 作为数学数组描述，不声称 Shen 使用了这个连续短语，也不是新方法名 |
| uniform planar array；array response；common delay | Shen II-A，PDF p.3；Li II | 阵列及传播几何对象对应，保留 |
| common Doppler shift | Huang 模型及 p.4；本文 II-A 假设 | 保留假设，跨帧分解是基于该假设的本文推导 |
| multi-frame transmission；phase rotation | Shen II-B，PDF pp.4–5 | 操作同类；本文 AFDM 的单参数相位约束单独由公式定义 |
| power leakage；sparse or grid-aligned channel assumptions | Huang 摘要、II，PDF pp.1–2 | 整体表达有据；不把活动块稀疏与信道内部稀疏混为一谈 |
| block sparsity | Cai II 的活动块结构；Liu III 的共享活动变量 | 本文明确为不活动设备整块为零；不是每个活动信道都稀疏 |
| Bayesian inference；posterior distribution；MMSE estimate | Cai II–III，PDF pp.4–6 | 目标定义与后验分解一致 |
| proper complex Gaussian distribution | Neeser–Massey 摘要、II；既有账本 | 保留 proper，不能仅因 Cai/Shen 未采用同一限定就删去复数统计约定 |
| turbo message passing；Gaussian extrinsic message | Cai III-A/B，PDF pp.5–8 | 整体用语和消息相除操作对应 |
| expectation propagation；Gaussian approximation/projection | Minka §2–3；Cai III-B1/B2，PDF pp.6–7 | 支持均值方差匹配及因子相除；不把本文所有控制规则都归为原算法 |
| posterior mean and variance | Cai III-A/B1，PDF pp.5–6；Shen IV-A，PDF p.11 | 适合本文实际所需的两个量，优先采用 |
| conditional mean and covariance | Dytso 摘要及 Proposition 1，正式版 PDF pp.1–3 | 用于完整协方差对象；标量 t_k 则称 variance |
| active/inactive hypothesis；posterior probability of activity | Cai III-B2，PDF p.7；Ding III-B | 二元假设和贝叶斯概率的语境一致 |
| Bernoulli–Gaussian approximation | Liu Appendix A Lemma 1，本地 PDF p.11 | 本文先将活动条件后验近似为 Gaussian，再形成零点质量与 Gaussian 的混合；不是声称真实信道先验为 Gaussian |
| spatial covariance；average variance | 本文 III-C 的明确求和及迹公式；Cai III 的标量方差近似 | 常规统计量名称；具体天线维平均是本文计算，不附会为文献同一算法 |
| score-based generative prior；score function | Cai 标题/I/IV；Hyvärinen §2 | 对数密度梯度与学习先验语境一致 |
| first-order/second-order score | Cai IV-A，PDF p.8 | 本文明确分别为 log density 的梯度/Hessian，保留 |
| Tweedie's formula | Efron；Cai IV-A；Dytso | 用于 Gaussian 观测下的条件均值；矩阵协方差版本由所列恒等式支持 |
| denoising score matching | Vincent；Cai IV-B，PDF pp.8–9 | 目标及条件 Gaussian score 对应；Σ 加权和均值参数化是本文推导 |
| denoiser input error；colored Gaussian noise | Shastri 摘要及 III-B，正式版 PDF pp.1、8 | 这两个完整搭配有原文；它们不自动支持本文全部 Kronecker 设计 |
| denoiser conditioned on the noise covariance | Shastri III-B 的相关噪声去噪操作；本文 IV-B | 普通操作描述；不宣称它是 Shastri 的算法名称 |
| Jacobian of the conditional mean；conditional covariance | Dytso Proposition 1，正式版 PDF p.3 | 与本文输出行、输入列约定相配；P=JΣ 的次序保留 |
| Monte Carlo finite differences；divergence | Metzler 原公开稿 V-B，PDF p.15；既有账本 | 借鉴随机散度估计；随机符号、中心差分、复坐标缩放及跨迭代复用是本文实现设置 |
| density ratio estimation；density-ratio estimator | Menon–Ong §3 式(6)–(8)、§4.2 式(16)–(17)，PDF pp.2–3 | 完整表达与分类估计比值的操作一致 |
| log odds；logit；sigmoid；binary cross-entropy | Menon–Ong §2–4 的 logistic loss/链接函数；本文给出三个函数的明确表达；Ying III-D 用 binary cross-entropy | logit 是所定义的 log odds，不另创类别输出含义；BCE 的实际公式保留 |
| training-prior correction／Bayes correction | Menon–Ong §3–4.2；本文 IV-D 直接给出 Bayes 恒等式 | 作为先减训练先验、再加接收端先验的操作说明，不包装成命名方法 |
| site approximation；Gaussian site | Vehtari §2.1 pp.5–6；§5.3 pp.18–19 | site approximation 是完整原词；本文首次出现明确它近似信道先验因子，并给 E_k,c_k；保留 |
| precision；natural parameter | Vehtari §5.3 p.18、Appendix A p.32 | c_k 的倒数及 E_k/c_k 对应 Gaussian 自然参数；只在完整停止规则保留 |
| numerical floor；clipping；retain the sites | 本文显式 max/clip/条件分支 | 普通数值操作，不声称是有文献专名的算法；阈值与逻辑保留 |
| damping factor | Cai V-B1，PDF pp.9–10，式(57)–(58) | 替代 new-message weight；本文公式明确其乘新消息 |
| root mean square；channel power normalization | Cai V-B2，PDF p.10；本文 s 定义 | 保留归一化方式，十位小数常数移至附录 C |
| sample covariance；MDL；noise-variance estimation | Wax–Kailath；Nadakuditi–Edelman II-A 式(5)–(7)，既有账本 | 低秩空间信号加白噪声条件保留；尾部特征值均值不误称 oracle |
| expected Gaussian negative log likelihood；variance update | Vila–Schniter III-A，正式版 PDF p.4；本文 V-B | 本文将残差平方加后验方差用于局部输入 v，不能将它称为完全复现原文物理噪声估计 |
| thin SVD；singular values；computational complexity | Ma OAMP；本文 V-C 的分解及维度 | 直接线性代数描述；成本及每次更新需重算 SVD 的条件保留 |
| RefineNet；residual/refinement blocks；conditional instance normalization；dilated convolutions；ELU | Song Appendix A.1–A.3；Lin RefineNet；Cai VI-A2/Table III | 均为既有网络构件；通道数、条件输入、卷积安排是本文配置，不能把整套配置归为 Cai 的结构 |
| sigmoid-weighted linear unit (SiLU) | Elfwing–Uchibe–Doya 摘要及 §2 | 完整名称、函数含义有原文；本稿用法正确 |
| preconditioning | Karras §5/Table 1；本文 VI-A2 | 术语有据；BΣ/KΣ/OΣ 的矩阵推广属于本文，保留明确的 extend 表述 |
| Adam；exponential moving average；validation/model selection | Song Appendix B；Karras Appendix F.3；Cai VI-A2 | 常规训练操作；学习率、批量、训练轮数及选模条件属于实验设置 |
| SOMP；GAMP-SBL；GNN-ASPL；off-grid SBL | Tropp §4；Zhang 等原论文标题/算法；Ding III；Wei III–IV | 保留原方法名；AFDM/多天线适配及活动判决规则单独交代 |
| first-order linear approximation | Wei IV-B，PDF p.11 的小节标题 | 直接对应字典对连续偏移的一阶展开，替代 atom approximation |
| least squares；Gaussian-prior estimate；genie-aided conditional MMSE | Cai VI-B 及本文 VI-B 的明确辅助信息和解析 MSE 定义 | 三种参照必须按实际可用信息区分；genie 的真值条件保留 |
| NMSE；AER；missed detections；false alarms | Shen V-A，PDF p.12；Cai VI-A | 完整指标名称有据；分母、场景汇总与本稿定义一致 |
| convergence behavior；stopping criterion | Cai Algorithm 2；Shen Algorithm 1（PDF p.10） | 结果中的“满足停止条件”不扩大为数学收敛定理；复杂停止规则移至附录 |
| variable projection；least-squares gain | O'Leary–Rust §1 式(2)–(3)，PDF p.2；§2 | 固定非线性参数后消去线性增益，操作位置正确 |
| L-BFGS-B | Zhu 等作者技术稿摘要、§1，PDF pp.1–2 | 带边界的局部优化；不加全局最优描述 |
| phase refinement；expected squared residual | Shen III-C，PDF p.9，式(47)–(54) | 固定 Gaussian 反馈下更新相位；共同 β_k 约束、常相位吸收及调度是本文适配 |
| cyclic shift；CPP phase；integer/fractional delay | Bemani III；Huang II；本文附录 B 的波形展开 | 操作与矩阵定义一致；长时延推广不以自造名称代替公式 |

## 明确保留为本文命名的内容

| 名称 | 身份与处理 |
|---|---|
| multi-frame linear estimation (MFLE) | 作者已确认的模块名；线性估计是既有操作，整个名字与缩写不是 Cai/Shen 原名。保留定义。 |
| generative-prior-aided joint denoising (GPJD) | 作者已确认的模块名；整套组合属于本文，保留定义，不以拆词出处证明整名已有。 |
| GP-MP、GP-MP-CCD | 作者已确认的比较接收机标签。CCD 展开 covariance-conditioned denoising 属于本文描述性命名；Shastri 使用相关噪声去噪，不代表使用 CCD 原名。 |
| GP-MP-CCD-EP | EP 后缀在此表示 estimated phases；与推导中的 expectation propagation 区分。正文比较设置已明确。 |
| Kronecker 训练协方差、矩阵预条件、随机方向复用、方差缩放、停止窗口 | 本文具体设计或实现设置；用公式和普通动词描述，不另起技术名称，不声称这些完整操作组合都来自某一篇参考论文。 |

这些名称属于可识别的本文贡献和实验标签。用户本轮提出的是清理不必要的组合词，没有要求撤销之前确认的算法命名，因此保留名称并纠正来源归属。

## 压缩范围与保留的信息

删除了图注中泛泛的 schematic 免责声明、重复的张量/索引解释、已在公式中明确的当前方差提醒、重复的训练与推断区分。停止逻辑在正文保留简短说明，完整检查、窗口和容差与高精度归一化常数集中到完整版附录 C；另见 [IMPLEMENTATION_DETAILS.md](IMPLEMENTATION_DETAILS.md)。

网络架构没有因“Cai/Shen 没有”而删空：Cai VI-A2/Table III、Shen IV-B/Table II 都详细说明网络结构。本文不同的条件输入、预条件公式和分类器特征属于理解、复现当前方法所需的信息。

保留影响读者判断的事实：共同 Doppler 假设、dense 表示比较条件、已知/估计相位区别、真实信息的 genie 条件、训练/在线噪声协方差区别、参数选择与评估场景重叠、选择性重跑、未收敛输出和回溯性消融。这些是实验有效性的具体条件，不能以删“防御性语言”为由抹去。

## 来源入口

- [Cai 正式版（本地）](../../../../reference/literature/cai2026.pdf)，本轮页码以此为主；并核对本地 v2。
- [Shen 本地版本](../../../../reference/literature/shen2025.pdf)，页码为 PDF 页序，与正式出版页码可能不同。
- [Manor–Michaeli](https://arxiv.org/abs/2309.13598)、[Dytso 正式版](https://par.nsf.gov/servlets/purl/10444847)。
- [Shastri 正式版](https://phil-schniter.web.app/pdf/jsait22_dgec.pdf)、[Menon–Ong](https://proceedings.mlr.press/v48/menon16.pdf)、[Vehtari](https://www.jmlr.org/papers/volume21/18-817/18-817.pdf)、[Minka](https://tminka.github.io/papers/ep/minka-ep-uai.pdf)。
- [Song Appendix A](https://arxiv.org/html/1907.05600v3#A1)、[SiLU 原文](https://arxiv.org/abs/1702.03118v3)、[Karras](https://arxiv.org/abs/2206.00364)。
- [O'Leary–Rust](https://www.cs.umd.edu/users/oleary/software/varpro.pdf)、[Zhu L-BFGS-B](https://users.iems.northwestern.edu/~nocedal/PDFfiles/lbfgsb.pdf)。

原有完整书目信息及沿用的来源核查见 [TERMINOLOGY.md](../../docs/TERMINOLOGY.md)。本次结论不把“公式来源存在”误记为“完整搭配逐字出现”。
