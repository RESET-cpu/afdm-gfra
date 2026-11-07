# 阻尼合理性及非 Cai 公式的文献原型

后续呈现更新：κ 更新、训练协方差采样及后续五项普通操作/指标已改为正文，当前共 46 个编号公式；本文档保留修改前式号作为核查快照。见[第一次精简](IMPLEMENTATION_SETTINGS_PROSE_20261104.md)及[最新逐式复查与编号映射](FORMULA_PRESENTATION_AUDIT_20261104.md)。

日期：2026-11-04。作者本轮询问：当前阻尼是否合理；不能归给 Cai 的公式是否能在其他论文找到接近的原型，以避免没有依据的拼接。

## 结论与范围

当前递归阻尼有明确的消息传递文献原型，正文和实际迭代实现相符，没有发现需要因“与 Cai 印刷式不完全相同”而修改算法的理由。主要非 Cai 公式也能追溯到已有恒等式、估计方法或物理模型；但不能把所有具体组合、训练采样和尺度更新都归成某篇论文的原式。

本次新增最直接的证据是 **de Albuquerque–Pearson, NeurIPS 2024, Inflationary Flows** 的矩阵预条件：附录 B.1 明确给出矩阵形式，按本文的名义信号协方差取值可得到当前式 (47)。此前只追溯到 Karras 标量式，依据不够完整，现补充这一更接近的已发表原型。

本轮只补充研究记录与出处；不改正文、PDF、算法、模型或实验参数，不启动实验，不恢复已删的辅助推导，也不重开既有 C/M 讨论。

## 1. 阻尼：是什么，为什么可保留

### 当前实际形式

正文 (40)–(41) 的共同形式为

\[
z^{(i)}=(1-\eta)z^{(i-1)}+\eta z_{\mathrm{new}}^{(i)},\qquad 0<\eta\leq1.
\]

旧量是**上一轮已经阻尼的状态**。输入端对均值和原始线性方差分别这样更新；之后才用 \(v^{(i)}=\kappa^{(i)}\bar v^{(i)}\) 缩放去噪器输入方差。反馈端对外信息均值和方差也递归更新。首次没有历史消息，直接使用新值。

已读实现：

- [共用 moment_damp](../../src/algorithm/STMP/iterations.py:18)：均值、协方差分别作线性插值；首次直接返回新值。
- [默认 C-STMP 迭代](../../src/algorithm/C_STMP_variance_em_20261025/iterations.py:46)：第 47 行输入阻尼，第 51 行再乘尺度，第 60 行反馈阻尼，第 82–85 行保存已阻尼状态。原始方差历史不混入已校准的方差。
- [选定相位版本](../../src/algorithm/C_STMP_phase_selection_20261030/iterations.py:64)：同一阻尼函数；相位更新时另有历史重置，此处不把它混同于固定映射的迭代。
- [默认候选配置](../../src/configs/candidates/C_STMP_variance_em_20261025.json) 的 \(\eta=0.4\)。它是项目设置，不是文献规定的最优值。

### 接近的文献形式及边界

| 文献 | 精确位置 | 支持什么 | 不可声称什么 |
|---|---|---|---|
| Rangan et al., *On the Convergence of Approximate Message Passing With Arbitrary Matrices*, IEEE TIT 2019 | [作者提供的期刊 PDF](https://phil-schniter.web.app/pdf/tit19_gamplin.pdf)，PDF p.2/印刷 p.5340，Algorithm 1 第 9、13 行；§II-B 在 PDF p.3 | \(s^t=(1-\theta_s)s^{t-1}+\theta_s g_s(\cdot)\)、\(x^{t+1}=(1-\theta_x)x^t+\theta_xg_x(\cdot)\)，就是递归旧状态加新候选的形式 | 该算法没有逐项复制本文全部均值/方差阻尼；其特定 Gaussian/凸性条件下的收敛结论不能移植给本学习接收机 |
| Rangan–Schniter–Fletcher, *Vector Approximate Message Passing*, 2019 | [本地作者稿](../../reference/literature/rangan2019_vamp.pdf)，§III-C，PDF pp.5–6，式 (26)–(27) | 估计值和精度参数均使用递归阻尼，旧值为已更新状态 | 原式 (27) 阻尼的是 precision；本文阻尼 variance。二者不是同一数值操作 |
| Sarkar–Ahmad–Schniter, *MRI Image Recovery Using Damped Denoising Vector AMP*, ICASSP 2021 | [正式论文](https://par.nsf.gov/servlets/purl/10338587)，§3/Algorithm 1；[本地作者稿](../../reference/literature/sarkar2020_ddvamp.pdf) PDF p.3 | 学习去噪器 VAMP 中也采用阻尼，并明确讨论对参数作不同变换后再阻尼 | 该文采用幅度域的部分阻尼，不能说与我们线性方差插值逐式相同 |
| Cai 期刊版 | [本地 PDF](../../reference/literature/cai2026.pdf)，§V-B1，式 (57)–(58) 与 Algorithm 2 | Gaussian 消息均值、方差均加权的近邻原型 | 按印刷公式，旧项是上轮原始外信息；不能据此把本文递归形式标成完全相同。此处未审计 Cai 的代码 |

数学上，它是对消息参数的松弛更新。在固定映射 \(F\) 下，\(z\leftarrow(1-\eta)z+\eta F(z)\) 与 \(z=F(z)\) 有相同的不动点；正方差/正定协方差的凸组合仍为正。这说明形式本身有一致的解释，不是任意改写。它可减弱某些振荡，并不保证任意非线性耦合算法收敛，也不能仅凭公式断言 0.4 最优。

这里插值的是 Gaussian **参数**。它不是两份随机估计误差线性组合的真实协方差，也不是两个 Gaussian 分布混合后的矩匹配；因此不能要求附加一个“均值差的平方”项。自然参数阻尼、方差阻尼和幅度阻尼是不同策略，本文采用其中一种即可，不应混称。

**建议：保留现有运算。后续修订正文时，校准 (40) 前只引用 Cai 的表述，补充递归阻尼来源；无需为此新增推导或改成精度阻尼。**

## 2. 非 Cai 内容的原型对照

按当前 53 式编号。已在前两轮核过的内容沿用其原文页码和代数检查，下面不把沿用记录伪称为本轮重新验证所有论文全文。

| 本文位置 | 最接近的已有原型与定位 | 对应程度、仍属于本文的部分 |
|---|---|---|
| (1)–(9)：物理模型、AFDM、跨帧相位 | Shen §II-B 式 (3)、(8)–(10) 与附录 A；Huang §II 式 (4)–(5)，PDF p.2；Bemani 学位论文 §3.1.1 式 (3.7)、(3.9)，PDF pp.52–53/印刷 pp.26–27，§3.2 式 (3.14)，PDF p.55/印刷 p.29 | 连续 AFDM 波形、CPP、时延和 Doppler 有原型；本文的长前缀延拓、完整分数时延采样、共同 Doppler 的帧相位及排列是模型适配。没有找到与整组模型完全相同的一篇原式，不声称 Shen 的 OTFS 模型就是本文 AFDM 模型 |
| (12)–(13)、(42)：一般矩阵 LMMSE 与 SVD 计算 | Ma–Ping OAMP 的一般 LMMSE；亦可由 Cai 特例前的一般 Gaussian 条件均值公式得到。具体原文位置沿用 [公式来源记录](FORMULA_PROVENANCE_20261104.md) | 保留一般逆矩阵以及将其谱分解，是标准等价计算；本文有效导频不一定行正交，不能为外观一致套 Cai 的标量分母 |
| (20)–(21)：混合空间协方差 | Cai (35)–(38) 的 Bernoulli–Gaussian 混合矩；Dytso §I-B 式 (4)–(6) 的协方差定义 | 从标量二阶矩扩为全协方差，并按本文矩阵位置平均；是直接的矩关系，不是新的概率模型 |
| (23)–(28)：有色 Gaussian 条件矩与导数 | [Dytso 正式版](../../reference/literature/dytso2023_conditional_mean_published.pdf)，§I-B 式 (9) 与 §III Proposition 1 式 (17)，PDF p.3/印刷 p.1885；DSM 来源沿用 Vincent/Cai | 导数—条件协方差是已有精确恒等式；本文 Jacobian 约定转置，所以 \(P_{\mathbb R}=J_m\Sigma\)。实/复转换、每复坐标归一化和训练参数化需适配；用有限网络代替精确条件均值后为近似 |
| (29)、(34)：导数迹的数值估计与汇总 | [Metzler 作者稿](https://arxiv.org/pdf/1406.4175)，§V-B/PDF p.15，Monte Carlo 散度估计；[Avron–Toledo 2011](https://www.cs.tau.ac.il/~stoledo/Bib/Pubs/randomized-trace.pdf)，§2 Lemma 2.1/PDF p.2、§3 Definition 3.3/PDF p.3，随机符号向量迹估计 | 原型明确；本文采用 \(w=\Sigma^{1/2}z\)、正负扰动的中央差分和有限方向数。没有找到同时包含这些全部设置的逐字原式。方差下限和跨设备汇总为实现设置；有限差分及有限网络的输出不能称为精确后验方差 |
| (30)–(33)：分类器估计密度比及活动概率 | [Menon–Ong, ICML 2016](https://proceedings.mlr.press/v48/menon16.html)，§3 式 (6)–(9)，§4.2 式 (16)–(17)；本地原文在既有术语核验目录 | 均衡类别下最优 logistic 输出为 log density ratio，再加接收端 log prior odds，属于直接对应。本文的网络输入和训练分布为具体选择，有限网络不自动达到理想最优 |
| (37)：空间谱噪声估计 | Wax–Kailath 的 MDL 信号维数选择、噪声子空间特征值平均；Nadakuditi–Edelman 相关谱估计。沿用 [噪声估计文献记录](BASELINE_NOISE.md) | 是已有估计框架；低秩信号和空间白噪声是前提，不能归给 Cai，也不是本文发明 |
| (38)–(39)：输入方差目标与 κ 更新 | [Vila–Schniter 2013](../../reference/literature/vila_schniter_2013.pdf)，§III-A 式 (22)–(27)，PDF p.4/印刷 p.4661 | (38) 的“残差平方＋后验不确定度”有直接 Gaussian EM 原型；原文估计观测噪声，本文用于局部伪观测方差。(39) 选用尺度 κ 并递归阻尼是本文设计，不能声称文献证明了整套外循环的 EM 单调性 |
| (40)–(41)：递归消息阻尼 | 本文档第 1 节的 Rangan/GAMP、VAMP 和蔡文 | 有近邻原型，可保留；完整阻尼位置和 variance 参数选择是本文实现 |
| (46)：训练协方差随机采样 | Shastri DGEC §III-B 支持相关噪声条件化训练；构造本身为 \((1-\xi)I+\xi nZZ^H/\operatorname{tr}(ZZ^H)\) | **这是本文训练分布设置，不是已查得的某篇论文原式。** 它由正半定项构成，\(\xi\leq0.5\) 保证正定，迹固定为 n；无需伪装成已有算法或理论贡献 |
| (47)：矩阵预条件 | [de Albuquerque–Pearson, NeurIPS 2024](https://proceedings.nips.cc/paper_files/paper/2024/hash/af85ade5e70a6e1eb07a9541fb529baf-Abstract-Conference.html)，附录 B.1，PDF pp.23–24，式 (67)–(68)、(73)、(77)–(78)；基础为 Karras EDM | **此次补查到非常直接的矩阵原型**，见下节。网络、噪声条件输入及 loss weighting 不与其整套方法等同 |
| (A.1)–(A.3)：相位原子、最小二乘和消去增益 | AFDM 原子沿用物理模型；[O’Leary–Rust 原文](../../archive/figure_cleanup_20261104/retired_files/paper/checks/full_terminology_audit_20261030/downloaded_sources/oleary2013.pdf)，§1 式 (2)–(3)/PDF p.2，variable projection | 对非线性参数搜索、解析消去线性增益是标准方法；特定相位原子、单主径近似、候选搜索和更新日程为本文设计。该出处不替代相位算法的实验验收 |
| (43)、(45)、(49)–(50) | 运算计数、SNR、NMSE、AER 的定义 | 属于本文实现成本与评估约定，不是都要另找一篇同式论文的推断定理；统计对象和归一化必须按本文写清 |

### 矩阵预条件的直接对应

新来源 [Inflationary Flows 原文](../../archive/figure_cleanup_20261104/retired_files/paper/checks/formula_prototypes_20261104/inflationary_flows_2024.pdf) 附录 B.1 将输入、skip 和输出系数都写成矩阵。令其信号协方差 \(\Sigma_0=\sigma_d^2I\)、加噪协方差 \(C(t)=\Sigma\)，则：

| 原文 | 本文 (47) |
|---|---|
| (67) \(C_{\rm in}=(\Sigma_0+C(t))^{-1/2}\) | \(B_\Sigma=(\sigma_d^2I+\Sigma)^{-1/2}\) |
| (73) \(C_{\rm skip}=\Sigma_0(\Sigma_0+C(t))^{-1}\) | \(K_\Sigma=\sigma_d^2(\sigma_d^2I+\Sigma)^{-1}\) |
| (77)–(78) \(C_{\rm out}=(\Sigma_0^{-1}+C(t)^{-1})^{-1/2}\)，取对称正定平方根 | \(O_\Sigma=\sigma_d[\Sigma(\sigma_d^2I+\Sigma)^{-1}]^{1/2}\) |

原文使用共同特征基；本文的 \(\Sigma_0=\sigma_d^2I\) 与任意正定 \(\Sigma\) 对易，因而上述化简适用。这里 \(\sigma_d^2I\) 是预条件所用的**名义**信号协方差，不是声称实际 AFDM 信道空间协方差为单位阵。

只说明三个矩阵系数同类且能直接化简对应，不能把本文损失 \(\|\Sigma^{-1/2}(f-h)\|^2\) 说成该文式 (79) 的完整 loss weighting。该文也没有提出本文的接收机、网络结构或训练协方差采样。

### 中央差分为何是有来源的适配

对固定输入、固定网络和固定协方差，\(E[zz^T]=I\) 给出 \(E[w^TJ_fw]=\operatorname{tr}(J_f\Sigma)\)。用
\([f(u+\delta w)-f(u-\delta w)]/(2\delta)\) 近似 \(J_fw\)，即得到本文 (29)。因此它是已有随机迹估计和数值方向导数的组合；中央差分不是另造一套统计恒等式。

这不意味着单方向、有限步长的结果无误差，也不把固定方向在自适应迭代中复用说成每轮条件无偏；当前稿件把它称为估计而非精确后验量是合适的。相关技术路线已经讨论过，本轮只校准依据，不重复提出更换路线或增加正文证明。

## 3. 后续呈现建议与证据

可以保留现有公式。优先校准两处来源说明：递归阻尼补充 Rangan 的原型，矩阵预条件补充 NeurIPS 2024 的直接矩阵来源。局部方差尺度、协方差采样和相位搜索日程继续明确为本文方法设置。此次查到来源，并不要求为每个式子增加一个引用或把内部推导搬回正文。

既有 [32 项代数核验](../checks/notation_formula_revision_20261104/MATH_VALIDATION.json) 和 [7 项蔡文特例核验](../checks/cai_formula_correspondence_20261104/CAI_LIMIT_CHECKS.json) 保持有效；本轮不重复运行，不将其夸大为整机性能/收敛证明。

新来源 PDF、页图和提取文字保存在 [本轮证据目录](../checks/formula_prototypes_20261104)。其中矩阵预条件第 23–24 页已按原页目视复核；随机符号迹估计通过作者网站原文核对。原论文源码与 PDF 未改，见 [核验记录](../checks/formula_prototypes_20261104/VALIDATION.json)。
