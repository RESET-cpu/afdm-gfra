# 全篇术语出处与一致性清查

日期：2026-10-30。稿件：D:/afdm-gfra/paper/C-STMP。结论：仍有术语出处需要澄清及前后称呼不一致之处；主要问题集中在第 VI 章、表 I 和附录 B。不是所有未检索到完整词组的写法都属于自造术语。

本轮为清查记录，未修改论文正文、公式、参考文献或图件。下列替换均为待落实建议。

## 范围与证据边界

- 通读当前 `main.tex` 实际编入的摘要、第 I–VI 章、附录 A–D、图注、表格和算法；补查中文摘要。未编入的结论占位文件、其他旧附录以及历史草稿不混入当前结论。
- 检查当前 15 页阅读稿，以及七个外置实验图中的图例、标题和坐标轴；接收机框图另随第三章源码核对。
- 正文共引用 32 个文献键，均存在于 `references.bib`。另有 5 个未被当前正文引用的备用 BibTeX 条目，没有进入编译后的参考文献表，不判为论文中的“孤立引用”。
- 本轮取得并检索其中 27 篇全文：11 份本地原文、16 份在线原文。26 份 PDF 的页树完整性检查通过；Vila 本地文件有解析修复告警，其文字只作辅助，不用本轮抽取页码建立新依据。
- 另外 5 项（Hadani 2017、Xu 2026、Zhang–Fan–Hao–Quan 2023、Zhu 1997、3GPP TR 22.865）只有文献记录或在线可见片段核对，没有将其标为完整全文检索。因此，本文的“未核到原词”是明确检索范围内的结论，不是宣称整个文献世界不存在该术语。
- 对 65 个候选术语及词组建立词面检索记录，再结合原文语境复核。自动检索结果可能命中参考文献标题或受断词影响，不能单独作为语义证据。
- `INVENTORY.json` 保存被查稿件、图片和参考原文的哈希；`REMOTE_SOURCES.json` 保存在线出处；`LEXICAL_SOURCE_MATCHES.json` 为辅助检索记录。所有下列源码行号以本轮快照为准。

## 七组优先处理的问题

| 编号 | 当前表述及位置 | 判定与依据 | 建议统一写法 |
|---|---|---|---|
| F01 | II-B，`02_system_model.tex:100–102`：maximum channel delay spread；VI 表 I，`06_simulation_results.tex:72`：Residual-delay support；同表第 75 行：Delay spread | **不同物理量混称，优先修正。** II-A 已定义 τ 为传播时延减去公共时延的 differential delay。CPP 不等式右端是所有设备与路径的最大差分时延，不能与 VI 中用于缩放多径功率时延谱的 30–50 ns delay spread 混称。表 I 的 [0,699] μs 也应与 II-A 对齐。Shen §II-A 式(1)后、PDF p.3；§V 表 I、p.12，原表该范围明确称 differential delay。 | CPP 句改为 maximum differential delay；表 I 改为 Differential-delay range。保留 30–50 ns 项的 Delay spread，不改任何值或不等式。 |
| F02 | VI-A1，`06_simulation_results.tex:88`：first-order network | **沿用旧称，和当前网络输出定义不一致。** IV-A 的 fθ 直接输出条件均值；V-B 称 mean network，附录 D 称 channel network。Cai §IV-B、PDF p.9 的 first-order score network 输出一阶得分，不能省略 score 后拿来作为当前均值网络的统一名称。 | 统一为 channel denoiser 或 channel-mean network；本稿优先使用 channel denoiser，并保留 IV-A 的 fθ 定义。谈论 Cai 原方法时继续保留 first-order score network。 |
| F03 | VI-A1，`06_simulation_results.tex:111–112`：training queries；scalar query covariance | **上一轮第二类表述的跨章残留。** III–V 已改成 denoiser input 与直接写明的协方差；VI 仍用 query。Shastri §III-B、式(38)–(41)、PDF pp.15–16 使用去噪器输入及其噪声统计的表述。 | 直接写 classifier training inputs are generated with noise covariance C=vI，下一句说明接收机调用时同样使用 C=vI；不把矩阵 vI 简称为标量协方差。 |
| F04 | VI-A1，`06_simulation_results.tex:107`：covariance-weighted loss | **上一轮第二类表述残留。** IV-A 已明确是信道平方误差由 Σ⁻¹ 加权，等价得分误差由 Σ 加权；该短语省略权重方向，且本轮参考全文未核到对应命名。Vincent §4.2 的 denoising score matching 支撑基本目标，不直接命名本文矩阵加权形式。 | 引用 `eq:first-loss`，写 the loss in …，或说明 squared error weighted by Σ⁻¹。 |
| F05 | VI-A1，`06_simulation_results.tex:109`：balanced binary cross-entropy | **把类别采样条件和损失名称挤在一起，容易误读为另一种损失。** IV-C 使用普通 binary cross-entropy，同时规定两类先验均为 1/2。Menon §II.1–2、§III–IV.2 将类比例和 logistic loss 分开；Ying §III-D、PDF p.6 使用 binary cross-entropy。 | 写 binary cross-entropy with equally likely active and inactive training labels；保持已有损失和采样方式。不能写成本文采用了文献外的特殊 balanced loss。 |
| F06 | 附录 B，`appendix_afdm_channel_model.tex:7`：frequency wrapping，紧接 Huang 引用 | **当前引文的词面出处未落实。** 本轮核读 Huang 全文，其 §II 式(5)支持分数时延下的信道表达，但未出现 frequency wrapping；在已检索的参考全文中也未核到这一完整名称。历史术语表的同词另指向 Cao–Shao，该文没有列入当前参考文献。不能据此声称全领域不存在该说法。 | 直接描述本稿用 wξ、ζn 和式 `eq:continuous-waveform` 定义波形；如确要保留这一术语，则需补入实际采用该词且含义相同的原论文。Huang 的引用继续只承担其实际支持的内容。 |
| F07 | VI 表 I，`06_simulation_results.tex:68`：AFDM block length N | **时间层级的称呼不够一致。** II 将一个 transmission block 定义为包含 Q 个 AFDM frames 的观测时段，N 是每帧 chirp subcarriers 数，也对应有用部分的采样点数。这里的 block length 容易与整块长度混淆。 | 改为 Number of chirp subcarriers N，或 Useful samples per AFDM frame N；保留 transmission block 表示 Q 帧组成的传输块。 |

## 进一步统一或补来源的项目

| 编号 | 项目与位置 | 处理建议及边界 |
|---|---|---|
| U01 | proper complex Gaussian：`main.tex:75`、IV-A 和 VI-A | 这是**已有标准数学术语，并非本文自造**；但在本轮已取得的参考全文中未核到该完整原词。Cai 符号说明、Liu §I 符号说明、Huang §II 使用 circularly symmetric complex Gaussian。若严格要求每个原词在当前书目中有据，可补 proper 的直接出处，或说明“中心化后的复高斯变量具有圆对称性”。对于带非零均值 μ 的 CN(μ,Σ)，不宜不加说明就把整个变量替换为 zero-mean/circularly symmetric，造成数学含义变化。可补充来源为 Neeser–Massey, *Proper Complex Random Processes with Applications to Information Theory*, IEEE TIT 1993；此文当前不在书目内，本轮不擅自添加。 |
| U02 | 图 6 的 Number of users；图 7 的 Activity probability | 图 6 实际扫描候选设备数 K，不是活动设备数；建议 Number of candidate devices。图 7 扫描名义概率 p，接收机使用条件抽样后的边缘概率 ρ；建议 Nominal activity probability。图注已有相应说明，因此这是图内自足性和用词精度问题，不是数据错误。 |
| U03 | device、terminal、user 混用 | 原文确实都使用这些词，**不属于无出处术语**。当前模型主要用 device，训练和实验多用 terminal，小节/坐标轴又用 user。建议以 device 为当前稿主称呼；描述引用论文的正式名称、方法名时保留原词。涉及 K 时写 candidate devices，涉及活动集合时写 active devices。 |
| U04 | VI-D 的 Comparison Across Channel Models、图 8 的 Channel A/B/C/D；附录 C 的 cross-profile | 正文和附录已说明改变功率时延谱/衰落 profile，几何固定。建议统一为 Comparison Across Channel Profiles，图内按 NTN-TDL-A/B/C/D 标识。不是说 channel model 一词错误，而是用同一层级描述本次变量，避免误读为完整卫星几何与时变模型均改变。 |
| U05 | 缩写展开 | MIMO 仅见题名，正文没有完整展开；GNN-ASPL 没有整体展开；NTN-TDL-D 未解释 NTN、TDL；MSE 在 VI-B 首次独立使用时未展开。建议分别补 multiple-input multiple-output、graph neural network-based adaptive sparsity pattern learning、non-terrestrial network / tapped delay line、mean-squared error。GNN-ASPL 的完整名称见 Ding PDF p.1 贡献 1；NTN 见 Huang p.1，tapped delay line 见 Arvinte §IV、PDF p.6。D 是模型标记，无须编造展开。 |
| U06 | 拼写风格：sub-carriers/subcarriers；pre-compensation/precompensation | 统一为 subcarriers、precompensation 即可，属于编辑一致性。density-ratio estimator 与 density ratio estimation、effective-channel prior 与 effective channel 中的连字符随语法功能变化是正常的，不列为概念冲突。 |

附录 D 的 variance-update residual 与 activity-history residual 未在上述参考全文中核到同名术语，但正文已紧接公式定义，属于本稿停止条件的直接描述，并未宣称新的既有算法名称。若追求最简洁，可直接写 relative difference … 或 maximum difference …；不将其与真正缺乏定义的术语等同处理。

## 已核实可保留的用词

| 术语组 | 原文依据与使用边界 |
|---|---|
| AFDM、DAFT、IDAFT、chirp-periodic prefix | Bemani §III-A，特别是 CPP 式(19)前后；Ding §II 式(1)–(3)；Huang §II。第二章及附录 B 的延迟范围和波形扩展是本稿自己的公式约定，不把扩展部分冒称文献原式。 |
| differential delay、common delay、directional cosines、quasi-static property | Shen §II-A、式(1)及 §II-B；Li §II-B。术语本身有依据；F01 指当前稿的跨位置混称。 |
| fractional delay / Doppler、effective channel、power leakage | Huang §II 式(5)后的说明；第二章术语沿用正确。 |
| MMV、Gaussian likelihood、Bernoulli prior、block sparsity | Cai §II-B 与 §III；Liu §II–III。当前 X=αH 的块活动与 H 内部非稀疏先验已明确区分。 |
| score-based generative prior、score function、posterior sampling | Cai §IV；Song §§2–3；Arvinte §III。摘要、引言和 IV 的有色扰动离线训练表述与线上 C=vI 的公式没有直接矛盾。 |
| first-order / second-order score networks | Cai §IV-B/C；用于介绍 Cai 既有方法可以保留。F02 是当前均值网络被简称为 first-order network 的问题。 |
| device activity denoiser | **Cai §III-B 标题、PDF p.6 即有该词。** III-B2 推导活动概率。第四章标题中的 activity denoiser 是输出活动后验均值/概率的功能称呼，activity classifier 是实现方式，二者不必判为概念矛盾。可为清楚统一采用 classifier，但不应宣称原文没有 activity denoiser。 |
| expectation propagation、Gaussian approximation、extrinsic messages、site approximation | Minka §§2–3；Vehtari §2.1、PDF pp.5–6；Cai §III-A/B。Gaussian site approximation 是以高斯族近似 site 的直接描述，不是自造方法名。 |
| natural parameters、precision | Vehtari §2.2、§5.3 及 Appendix A.1，PDF pp.6、18、32。附录 D 中 c⁻¹、E/c 的写法有依据。 |
| conditional mean/covariance、Jacobian、Tweedie's formula | Dytso v1 §IV Proposition 1 式(22)、PDF p.5；Efron §2 式(2.7)–(2.8)、p.4。实/复归一化、Jacobian 转置约定已说明，不能因坐标约定不同就判为不同方法。 |
| denoising score matching、colored Gaussian noise、denoiser input | Vincent §4.2、PDF pp.6–7；Shastri §III-B、式(38)–(41)、pp.15–16。本文矩阵权重与显式协方差条件输入属于说明过的适配，不是这些原文的完整同名架构。 |
| preconditioning、RefineNet | Karras §5、式(7)–(8)、PDF p.8；Song Appendix A.3、p.14；Huang §III-A、p.3。当前 RefineNet backbone 加条件输入的写法保留了适配边界。 |
| Monte Carlo divergence、finite differences、random sign vectors | Metzler §V-B、式(21)和 PDF p.18 起的 Monte Carlo method 支撑随机方向近似；原文方向和差分形式与本文不同。本文随机符号、协方差缩放及中央差分由公式直接定义，不需要把这一组合虚构成原文方法名。 |
| density ratio estimation、logistic loss、log odds、binary cross-entropy | Menon §§II–IV、式(6)–(8)、(16)–(17)；Ying §III-D。完整的 log density ratio 是对比值取对数的直接数学描述，不要求每个带修饰语的词组都另设名称。 |
| damping、new-message weight | Cai §V-B1；Vehtari §5.2。η 的意义一直是新消息权重，未出现把旧消息权重混作 η 的反转。 |
| singular value decomposition / SVD | Ying §IV-B、式(23b)后；Arvinte 接收机处理；Metzler §V-A。thin 是所取分解尺寸的常规限定，不把未检索到 thin SVD 这一缩写词组误报为新算法。 |
| variable projection、separable nonlinear least squares、MDL | O'Leary–Rust §§1–2；Nadakuditi–Edelman §II 的 WK/AIC/MDL 回顾。附录 A 的局部路径拟合是本文应用，不能宣称原文提供了完整 AFDM 相位算法。 |
| SOMP、GNN-ASPL、off-grid SBL | Tropp Algorithm 3.1；Ding p.1 及 §§III–IV；Wei §§III–IV、Algorithm 1。沿用名称与本稿 AFDM/MMV 适配说明并不冲突。GAMP-SBL 对应原始书目已列，但本轮未取得所引 Zhang 等全文，不单凭其他 GAMP-SBL 文献替它完成实现同一性核验。 |
| NTN-TDL-D、NMSE、AER、genie-aided、oracle | Shen §V 表 I 与指标定义、PDF p.12；Ding §IV 式(28)；Cai §VI-B、p.12。genie 与 oracle 均有原文先例，当前稿已经明确给 genie 的额外信息，不属于无来源方法名。 |
| Adam、exponential moving average | Cai §VI-A、PDF p.11。当前训练超参数为本项目设置，不因采用同名优化器而声称复用了 Cai 全部训练配方。 |

## 作者已批准的名称

GP-CCD-MP-DRE、MFLE、GPJD，以及组成部分 CCD 的完整组合名称，不是上述参考论文的既有原名。`docs/TERMINOLOGY.md` 的 2026-10-30 命名记录已明确它们是作者批准的本文描述性名称，并分别说明技术来源和适配边界。

这类名称仍应作为“本文命名”管理，不能在审稿答复中说它们原封不动来自参考文献；本轮也不将它们混入应删除的未核实术语。正文、框图、Algorithm 1 和六幅接收机比较图中的算法名一致；未发现当前可见图例仍使用旧名 C-STMP。

## 核心含义的一致性

| 对象 | 核对结论 |
|---|---|
| 物理噪声 σ² / 估计值 σ̂² 与去噪输入方差 v | 区分清楚。前者是观测模型噪声，后者是局部去噪近似的不确定性；κ 更新 v，不改物理噪声模型。 |
| p、ρ、πtr、pk | VI 中 p 是非空条件抽样前的名义概率，ρ=p/[1−(1−p)^K] 用作独立先验近似；πtr=1/2 是训练类先验；pk 是估计的活动概率。不能为“统一符号”把这些合并。 |
| H 与 X=αH；Fθ、μ、X̂ | 未活动信道与活动掩码后的信道、网络条件均值与 site 组合后的条件均值、活动加权估计相互有定义；NMSE 的 H/X 使用场景分别说明。 |
| C 与 Σ；实维度 2D 与复维度 D | IV 的复协方差到实协方差含 1/2；条件方差迹按复坐标归一化。未发现本次术语层面的混用。 |
| 条件后验方差与活动不确定性 | III 的联合矩同时包含两项；方差目标没有把活动不确定性漏称为物理噪声。 |
| 参数保持、训练与在线调用 | 有色扰动训练与线上 C=vI 分开写明；没有据名称 CCD 就宣称在线追踪完整有色协方差。 |
| 已知跨帧相位与可选相位估计 | V/附录 A 描述可选估计，VI 声明当前比较使用已知相位。属于不同实验条件，不能仅因两种表述同时出现判为术语矛盾。 |

## 自动检查的人工复核

缩写检查结果为 partial，原始报告保存于 `acronym_report.md`。实际确认需要补充的为 U05；该工具对 GP-CCD-MP-DRE 的连字符组成、MFLE/GPJD 长名称、GAMP-SBL 复合缩写和 L-BFGS-B 固定算法名的拆分提示不能全部当作真实错误。MIMO 在标题中由人工另行发现，未依赖该工具发现。

正文和 PDF 中的原词均交叉核对；图 6、7、8 的坐标轴/标题从真实图件读取，未凭绘图脚本猜测。重新渲染并查看阅读稿 pp.8–9、12–13，确认表格、训练段、附录 B 和跨 profile 图的实际显示；本次不修改排版，未重新编译或运行训练、推断和批量实验。

## 主要在线原文

- [Menon–Ong：密度比、类别概率与损失](https://proceedings.mlr.press/v48/menon16.pdf)。
- [Vehtari 等：site approximation 与自然参数](https://jmlr.org/papers/volume21/18-817/18-817.pdf)。
- [Song–Ermon：RefineNet，Appendix A.3](https://arxiv.org/pdf/1907.05600)。
- [Dytso 等：条件均值导数恒等式](https://arxiv.org/pdf/2104.01883)。
- [Vincent：denoising score matching，原刊论文镜像](https://gwern.net/doc/ai/nn/diffusion/2011-vincent.pdf)。
- [Bemani 等：AFDM 与 CPP](https://arxiv.org/html/2204.12798v2)。
- [Neeser–Massey：proper 的可补充原始出处，当前未列入书目](https://www.isiweb.ee.ethz.ch/archive/massey_pub/pdf/BI437.pdf)。

全部本地来源、网络抓取地址、文件摘要和覆盖限制见本目录的 JSON 记录。
