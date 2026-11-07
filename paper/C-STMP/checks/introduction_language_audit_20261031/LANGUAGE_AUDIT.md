# 引言语言与出处核查（2026-10-31）

对象：`paper/C-STMP/sections/01_introduction.tex`。本轮仅核查并记录，不修改 TeX、PDF、公式、实验或书目。语言出处核查不等于重新验证整篇论文的技术结论或所有参考文献。

## 核查方法及范围

- 直接核对 Shen 作者稿、Cai arXiv v2、Ding 接受稿、Huang 正式版、Wei–Yuan v1、Shastri v2 的相关原文。六份本地 PDF 均通过结构预检，旁文件见本目录 `*_preflight.json`。
- `phrase_matches.json` 保存六篇 PDF 的定向词面检索，`source_pages.json` 保存逐页提取结果。匹配前进行 Unicode NFKC、跨行断词与空白规范化；未统一单复数、时态、连字符与普通空格。提取中的异常词内空格可能造成漏检。因此命中只是定位工具，未命中不证明整个学界没有使用过；下表结论经过上下文复核。
- 另查 Menon–Ong §4.2 式(17)、Bemani §IV Theorem 1、Friel–Hurn–Wyse §1 式(3) 及 Gu 等摘要。在线原文链接见下表。
- 旧术语账本的“依据某文献”有时指概念/公式依据，不应追认为该文献的连续原词。本轮明确区分词面、概念、组合描述和本文命名。

## 核心术语与短语

| 引言中的表达 | 原文位置 | 词面与含义判断 |
|---|---|---|
| grant-free random access；large differential delays and Doppler shifts | Shen 摘要、§I，PDF pp.1–2 | 既有术语；后者有单复数调整，本文采用 AFDM，不称 Shen 已提出本文方案。 |
| quasi-static；input–output relationship；remains approximately constant | Shen §II-B，PDF p.4 | 原词/搭配有依据；最后一个搭配原文用于连续帧的等效信道，本文是否满足仍以自己的第二章假设为准。 |
| Doppler robustness；doubly dispersive channels；sparse or grid-aligned channel assumptions | Huang 摘要、§I，PDF p.1，印刷 p.2949 | 原词有依据；不将免除信道稀疏假设扩大成免除设备活动稀疏性。 |
| full diversity | [Bemani §IV Theorem 1、式(51)](https://arxiv.org/html/2204.12798v2#S4) | 标准技术性质，具有参数与支持范围条件；不是一般褒义形容词。当前引言保留参数设计限定，本轮不修改作者指定保留的 AFDM/OTFS 段。 |
| score-based generative priors；Tweedie's formulas；single-step denoising | Cai 标题、§I-A、§IV-A，PDF pp.1–2、8 | 原词及正规语法组合；Tweedie's formulas 概括一阶和二阶关系。 |
| posterior probabilities of activity | Cai §III-B2、式(30)后，PDF p.7 | 原文为 posterior probability of activity，本文仅改为复数。 |
| activity uncertainty | Cai §III-B1、式(16)前，PDF p.6 | 连续原词；本文的处理方式仍由本稿的概率加权后验矩定义。 |
| denoiser-input errors | Shastri 摘要，PDF p.1 | 原文为 denoiser input error；本文增加连字符并改复数，含义相同。 |
| white Gaussian noise；colored Gaussian noise | Shastri 摘要、§III-B，PDF pp.1、15–16 | 原词有依据；used for training 和 with different covariance matrices 是本文说明用途/训练设置的组合，不是已核实的完整原句。 |
| finite-dimensional；structured compression matrices | Wei–Yuan §I，PDF p.1 | 前者为原词；原文讨论有限维压缩矩阵及结构化波束选择，本文多帧 AFDM 的联系属于本文设计动机，保留 may。 |
| density-ratio estimator | [Menon–Ong §4.2、式(17)前，PDF p.3](https://proceedings.mlr.press/v48/menon16.pdf) | 原文为 density ratio estimator；连字符为写法调整，learned 为训练获得的普通限定。 |
| marginal likelihood | [Friel–Hurn–Wyse §1、式(3)](https://arxiv.org/html/1209.3198v2#S1) | 既有术语。当前关于后验矩匹配不能一般性保留边际似然的分析，不归为 Cai 原文宣称的缺陷。 |
| Gaussian extrinsic messages | Cai §III-A 式(9)–(11)、§III-B 式(24)–(30)，PDF pp.5–7 | 已核对 extrinsic message 原词和 Gaussian 概率密度形式；未在本次六篇主语料中核得完整连续搭配。可作忠实数学描述，不标成 Cai 的逐字原词。 |
| activity-weighted channel estimates | Cai §III-B3、式(35)，PDF p.7；本稿 III-C | 对活动概率乘条件均值的描述；本轮未核得完整连续用例，不作为已有方法名称。 |
| structured multi-frame AFDM observation model | 本稿第二章 | 既有词汇组合成对本文模型的限定，非某篇参考文献的完整名称。 |
| MFLE；GPJD | 本稿 III-A；既有作者批准记录 | 本文模块名称及缩写，不声称文献已有同名算法。 |

## 动词、程度与连接

- Shen 摘要使用 propose、analyze、mitigate，§I 使用 complement，§II-A 使用 comprises；Cai 摘要使用 incorporate、develop，§II/III 采用 formulate、account for，仿真段使用 demonstrate。这支持一般词汇及论述习惯，不证明本文每个完整动宾搭配都原样出自这些论文。
- 丁文 §I（PDF p.1）的 `To unleash the full potential` 和 `critical prerequisite` 均为连续原词。本文第四段首句与该文几乎逐字一致，仅有 AFDM-GFRA 的拼写及引文差异；建议独立重述句子，而不是为了追求“原词”保留整句结构。
- Huang §II 式(5)后（PDF p.2，印刷 p.2950）关于分数时延/多普勒造成泄漏、削弱稀疏性的整句，与本文第四段相应句高度接近。术语和事实有依据，句法仍建议重新组织。
- power-limited、severe 可见 Shen §I（PDF p.2）；relatively high、strong Doppler robustness 可见 Huang §I（PDF p.1）；significant power leakage 可见 Huang §II（PDF p.2）。这些修饰有先例，但强度是否适合仍取决于对象和条件。当前未以这些词宣称本文性能全面领先。
- substantial computational cost 是计算负担的概括，不登记为两篇扩散论文的已核实逐字短语。[Ying §V-D/E](https://arxiv.org/html/2505.12382v3#S5.SS5) 确有反复后验 score 计算及复杂度分析；这支持计算负担动机，不是本文与其运行时的实测比较。
- Accordingly：Ding §I，PDF p.1；This motivates：Cai §I，PDF p.2；However、Moreover、Consequently、thereby、therefore：Shen/Cai 原文有用例；To avoid：Ding §III，PDF p.4；In general：Cai §IV-C，PDF p.9。它们在本稿分别承担因果、限制、并列缺口和推论，未发现明显逻辑误配。
- Against this background 未在六篇主语料核得，但可在 [Gu 等信道估计论文摘要](https://arxiv.org/abs/2409.17707) 核得；它是通用过渡，不必为该连接词向本稿增加引用。
- With such precompensation 是普通回指结构；没有必要将整段回指包装成专业术语。However 重复较多是同一种“已有方法—局限”组织方式，并非语法问题，不建议仅为换词而换词。

## 结构判断与建议边界

当前论证链为：业务场景/GFRA → 无 GNSS 需求和差分偏移 → OTFS/AFDM 波形选择 → 稀疏表示局限 → 生成式先验与采样代价 → STMP 的输入噪声及活动似然近似 → 本文三项贡献。结构连贯，贡献与已确认摘要一致。第六段较密集，但两类问题有 Moreover 分开，不构成必须重排的缺陷。

本次建议集中于第四段的两处句法重述；没有理由大改技术术语或为追求多样性替换连接词。本文模块命名、操作描述和潜在失配推论均应与“文献逐字原词”区别说明。尚未将任何建议写回正文。

## 稿件快照

- `sections/01_introduction.tex` SHA-256: `887bc9ec98de98aae3a44fc138934345476b5bff57451f8f402165a1be20e739`
- `main.tex` SHA-256: `4a2e7adc693b874b7caf193509cb8b43c9094d95c283778b7ca5ff066c0ef3a7`
- `main.pdf` SHA-256: `e746b84f7d1f3bf0f832cdee7135dccb26b748491315e653fc9a3976d882e3be`
