# 第二章全部具名对象与技术表达的出处核查

**当前修订状态：作者随后要求“能替换的全部替换”，本清单特别列出的 13 项已全部处理。** 有明确原词的采用原词，其余改为直接公式或公式回指，未把 pilot energy 改成 power。wrap 已用等价取整式展开，附录 A 同步引用该式。完整替换、出处与验证见[实际修改记录](../checks/ch2_named_expressions_revision_20261101/REVISION_NOTES.md)。

以下 96 项及其数字统计是**修改前审计记录**，对应下面保存的源稿哈希，不代表修改后的剩余问题。原证据和边界保留，以便回溯；不要将旧表中的“待核”“适配”等状态继续当作当前表达仍在正文。

## 修改前审计记录

日期：2026-11-01。核查对象：当前 `sections/02_system_model.tex` 的全部正文、小节标题与公式中的具名算子。第二章 SHA-256：`ee2a176d5eda597807fbb028171a82b62cbc24d1dc111f134539c59f70b49f16`。本轮只写核查文档，未修改正文、书目或阅读 PDF。

## 结论与口径

**不能确认所有名称都已经来自现有参考文献。** 完整清单合并重复用法及单复数，共 96 项：83 项原词；4 项待核；7 项适配；1 项外部用例；1 项书目库原词。这些数量是下面逐项清单的分类统计，不是对全体英文单词的统计。

- **原词**：当前 PDF 已列出的参考论文实际使用该名称，语义适用。允许单复数、大小写、排版连字符及已定义缩写的展开，不允许换词序或拼接近义词后当成原词。名称适用不等于其公式、域、维度和假设全部相同。
- **书目库原词**：原词有参考论文依据，该论文已在 `references.bib`，但尚未列入当前 `main.bbl`／PDF 参考文献。
- **适配**：核心术语有来源，完整标题、修饰语或操作描述是本文适配；按作者“完整名称也要已有出处”的标准，不能并入原词通过项。
- **外部用例**：此前找到的外部论文有用例，但不属于本稿现有书目，不能拿来宣称现有参考文献已覆盖。
- **待核**：本轮没有核到同义完整用例，不表示学界从未用过。

本轮查询了本地已有的 27 份逐页参考文本及 Ke 原 PDF；出处判定还逐一阅读了命中处上下文。未持有全文的 Xu 等条目不纳入“全文没出现”的断言；具体检索边界见 `checks/ch2_all_names_20261101/SEARCH_SCOPE.json`。其中 3GPP 是标准而非论文，没有将其不同语义的词形匹配作为论文术语依据。

变量字母、索引、取值集合和纯公式定义不因存在符号就自动获得一个英文名称。`q_tr` 的 for training 是用途说明；没有据此补造 training prior。CN、E、Pr、转置、范数等只有数学记号的项沿用 [变量审计](VARIABLE_NAMES_AUDIT.md) 的覆盖，不把核查者翻译出的名称混入本清单。正文未另取名字的 B_d、D、g_q 等也不重复制造名称。

## 当前未能作为“现有参考文献原词”通过的项目

| 编号 | 当前名称或完整表达 | 分类 | 原因／已经核实的替代依据 |
|---|---|---|---|
| 12 | pilot resources | 待核 | 未在本轮检索的现有参考语料中核得完整名称；Cai p.1 的原词为 resources for pilot transmission，可直接采用。 |
| 20 | receiver compensation for the common delay | 适配 | common delay 见 Shen p.3；接收端补偿的完整表述尚未核得同文用例，是本文操作说明，不能当成已有命名。 |
| 36 | arrival angles | 待核 | 未核得原词；Li §II-B/p.4 用 paired angles-of-arrival，Cai §VI-A/p.11 用 angle of arrival。可改为 angles of arrival，不能将词序不同登记为原词。 |
| 37 | Multi-Frame AFDM Transmission | 适配 | Shen p.4 有 multi-frame OTFS transmission；Huang p.2 有 AFDM frame。当前标题是技术对象替换后的标题，不能宣称为同一论文已有的完整名称。 |
| 43 | known pilot matrix | 适配 | pilot matrix 见 Cai p.4；Arvinte p.3 有 having knowledge of the transmitted pilot matrix。known pilot matrix 这个完整搭配未核得，已知性条件不等于新方法名。 |
| 46 | pilot energy | 外部用例 | 上轮仅核得 Tang 等 arXiv:2610.23420 §III-A/p.3 的 total useful-sample pilot energy per frame；Tang 未在本稿书目库或 PDF 参考文献中。Cai p.4 用 transmit power budget，不能作该名称的直接出处，也不能不核对量纲就替换 energy 为 power。 |
| 56 | time duration of an AFDM frame with CPP | 适配 | Shen §II-B/p.4 的原文为 time duration of a OFDM symbol with CP；本文换成 AFDM frame/CPP，不能说完整释义原样出现过。 |
| 58 | CPP relation | 适配 | CPP 有 Bemani 原词，relation 是本文对式(5)的回指；未核得 CPP relation 完整名称，不作为既有专门关系名称通过。 |
| 60 | transmitted symbol position | 待核 | 正文合写 transmitted and received symbol positions。Shen p.4 的 received symbol position 不能反向证明 transmitted symbol position；未核得当前发送符号索引含义的原词。 |
| 62 | antenna index | 书目库原词 | Appendix A；Ke 已在 references.bib，当前 main.bbl 没有该条。词源成立，不能宣称读者已能从当前 PDF 参考文献找到它。 |
| 69 | wrap | 待核 | 未在已核参考论文中找到将角度映射到 [-pi,pi) 的同名函数。3GPP 的计数器 wrap around 与 O'Leary 的 wrapper 不同义，不能用来通过。 |
| 71 | phase evolution across frames | 适配 | 当前引言贡献段有此表述，但本轮要求参考论文出处，不能以自己的引言证明已有论文用过。Shen p.5 的原词为 phase rotation，并说明 accumulates across multiple frames。 |
| 79 | inter-frame phase rotation | 适配 | phase rotation 及其跨帧累积见 Shen p.5，但 inter-frame phase rotation 完整命名未核得。inter-frame interference 不能证明这个不同的名称。 |

## 全部逐项清单

页码均为各来源 PDF 的文件页码；正文行号指本轮未修改的 TeX。相邻同源条目分开列出，便于逐项核对。

### 场景与物理信道

| 编号 | 第二章实际名称 | 正文行 | 判定与出处 |
|---|---|---|---|
| 01 | System Model | [L1](../sections/02_system_model.tex:1) | **原词**：`cai2026`，PDF p.3，原词 `system model`。章标题已有用例。 |
| 02 | LEO satellite-enabled grant-free random access system | [L4](../sections/02_system_model.tex:4) | **原词**：`shen2025`，PDF p.3，原词 `LEO satellite-enabled grant-free random access system`。§II，系统场景原词；不表示本文采用其 OTFS 系统。 |
| 03 | LEO satellite | [L4](../sections/02_system_model.tex:4) | **原词**：`shen2025`，PDF p.3，原词 `LEO satellite`。沿用已有卫星名称。 |
| 04 | AFDM | [L5](../sections/02_system_model.tex:5) | **原词**：`bemani2022`，PDF p.1，原词 `affine frequency division multiplexing`。该文题名及摘要给出 AFDM 全称。 |
| 05 | doubly dispersive effect | [L5](../sections/02_system_model.tex:5) | **原词**：`shen2025`，PDF p.3，原词 `doubly dispersive effect`。§II。 |
| 06 | terrestrial-satellite links (TSLs) | [L6](../sections/02_system_model.tex:6) | **原词**：`shen2025`，PDF p.2，原词 `terrestrial-satellite links`。§I，含 TSLs 缩写。 |
| 07 | single-antenna terrestrial devices | [L7](../sections/02_system_model.tex:7) | **原词**：`shen2025`，PDF p.3，原词 `single-antenna terrestrial devices`。§II。 |
| 08 | uniform planar array (UPA) | [L8](../sections/02_system_model.tex:8) | **原词**：`shen2025`，PDF p.3，原词 `uniform planar array`。§II，含 UPA 缩写。 |
| 09 | antennas | [L9](../sections/02_system_model.tex:9) | **原词**：`shen2025`，PDF p.3，原词 `antennas`。§II，天线数量的名称。 |
| 10 | transmission block | [L10](../sections/02_system_model.tex:10) | **原词**：`cai2026`，PDF p.4，原词 `transmission block`。§II-A。 |
| 11 | active devices | [L10](../sections/02_system_model.tex:10) | **原词**：`cai2026`，PDF p.4，原词 `active devices`。§II-B；active/inactive 条件也见同页式(1)及式(4)后的说明。 |
| 12 | pilot resources | [L10](../sections/02_system_model.tex:10) | **待核**：未在本轮检索的现有参考语料中核得完整名称；Cai p.1 的原词为 resources for pilot transmission，可直接采用。 |
| 13 | GNSS capabilities | [L13](../sections/02_system_model.tex:13) | **原词**：`shen2025`，PDF p.3，原词 `GNSS capabilities`。§II，整组表达和缩写均来自原文。 |
| 14 | Terrestrial-Satellite Link Model | [L16](../sections/02_system_model.tex:16) | **原词**：`shen2025`，PDF p.3，原词 `Terrestrial-Satellite Link Model`。§II-A 原小节标题。 |
| 15 | high mobility | [L18](../sections/02_system_model.tex:18) | **原词**：`shen2025`，PDF p.3，原词 `high mobility`。§II-A，描述卫星运动。 |
| 16 | time variation | [L19](../sections/02_system_model.tex:19) | **原词**：`shen2025`，PDF p.3，原词 `time variation`。§II-A，描述信道随时间变化。 |
| 17 | multipath propagation | [L19](../sections/02_system_model.tex:19) | **原词**：`shen2025`，PDF p.3，原词 `multipath propagation`。§II-A。 |
| 18 | doubly dispersive channel model | [L20](../sections/02_system_model.tex:20) | **原词**：`shen2025`，PDF p.3，原词 `doubly dispersive channel model`。§II-A。 |
| 19 | common Doppler shift | [L22](../sections/02_system_model.tex:22) | **原词**：`huang2026`，PDF p.4，原词 `common Doppler shift`。§IV，描述各路径共享 Doppler；不是只匹配独立单词。 |
| 20 | receiver compensation for the common delay | [L24](../sections/02_system_model.tex:24) | **适配**：common delay 见 Shen p.3；接收端补偿的完整表述尚未核得同文用例，是本文操作说明，不能当成已有命名。 |
| 21 | channel impulse response | [L25](../sections/02_system_model.tex:25) | **原词**：`li2023`，PDF p.3，原词 `channel impulse response`。§II-B，式(1)–(2)附近。 |
| 22 | time instant | [L26](../sections/02_system_model.tex:26) | **原词**：`li2023`，PDF p.3，原词 `time instant`。§II-B；本文另行规定时间原点。 |
| 23 | number of physical paths | [L34](../sections/02_system_model.tex:34) | **原词**：`shen2025`，PDF p.3，原词 `number of physical paths`。§II-A，式(1)后。 |
| 24 | path gain / path gains | [L35](../sections/02_system_model.tex:35) | **原词**：`shen2025`，PDF p.3，原词 `path gain`。§II-A，式(1)后；增益为 1 的路径没有另取 unit-gain path 等名称。 |
| 25 | Dirac delta function | [L36](../sections/02_system_model.tex:36) | **原词**：`shen2025`，PDF p.3，原词 `Dirac delta function`。Notations；不采用其他稿件误写的 Dirichlet function。 |
| 26 | differential delay | [L39](../sections/02_system_model.tex:39) | **原词**：`shen2025`，PDF p.3，原词 `differential delay`。§II-A，式(1)后。 |
| 27 | propagation delay | [L41](../sections/02_system_model.tex:41) | **原词**：`shen2025`，PDF p.3，原词 `propagation delay`。§II-A，式(1)后。 |
| 28 | common delay | [L24](../sections/02_system_model.tex:24) | **原词**：`shen2025`，PDF p.3，原词 `common delay`。§II-A，图1及式(1)后的定义。 |
| 29 | propagation time | [L43](../sections/02_system_model.tex:43) | **原词**：`shen2025`，PDF p.3，原词 `propagation time`。§II-A，公共时延的说明。 |
| 30 | beam coverage | [L44](../sections/02_system_model.tex:44) | **原词**：`shen2025`，PDF p.3，原词 `beam coverage`。§II-A。 |
| 31 | array response vector | [L46](../sections/02_system_model.tex:46) | **原词**：`li2023`，PDF p.3，原词 `array response vector`。§II-B；p.4 给出阵列式。当前稿已不使用 UPA response。 |
| 32 | wavelength | [L54](../sections/02_system_model.tex:54) | **原词**：`li2023`，PDF p.4，原词 `wavelength`。§II-B，阵列响应定义后。 |
| 33 | spacing between adjacent antennas along the v-axis | [L54](../sections/02_system_model.tex:54) | **原词**：`li2023`，PDF p.4，原词 `spacing between adjacent antennas`。§II-B，原文随后为 along the v-axis；本文只将坐标集合 x/y 换为 y/z。 |
| 34 | directional cosines | [L56](../sections/02_system_model.tex:56) | **原词**：`shen2025`，PDF p.3，原词 `directional cosines`。§II-A。 |
| 35 | z-axis / y-axis | [L57](../sections/02_system_model.tex:57) | **原词**：`shen2025`，PDF p.3，原词 `z-axis and y-axis`。§II-A，方向余弦说明。 |
| 36 | arrival angles | [L58](../sections/02_system_model.tex:58) | **待核**：未核得原词；Li §II-B/p.4 用 paired angles-of-arrival，Cai §VI-A/p.11 用 angle of arrival。可改为 angles of arrival，不能将词序不同登记为原词。 |

### AFDM与导频

| 编号 | 第二章实际名称 | 正文行 | 判定与出处 |
|---|---|---|---|
| 37 | Multi-Frame AFDM Transmission | [L61](../sections/02_system_model.tex:61) | **适配**：Shen p.4 有 multi-frame OTFS transmission；Huang p.2 有 AFDM frame。当前标题是技术对象替换后的标题，不能宣称为同一论文已有的完整名称。 |
| 38 | chirp subcarriers / chirp subcarrier | [L63](../sections/02_system_model.tex:63) | **原词**：`huang2026`，PDF p.2，原词 `chirp subcarriers`。§II 的 AFDM chirp subcarriers。 |
| 39 | pilot transmission | [L64](../sections/02_system_model.tex:64) | **原词**：`cai2026`，PDF p.4，原词 `pilot transmission`。§II-A；分配 Q 个 AFDM 帧是本文设定。 |
| 40 | AFDM frame / AFDM frames | [L65](../sections/02_system_model.tex:65) | **原词**：`huang2026`，PDF p.2，原词 `AFDM frame`。§II；允许单复数变化。 |
| 41 | pilot symbol / pilot symbols | [L66](../sections/02_system_model.tex:66) | **原词**：`cai2026`，PDF p.4，原词 `pilot symbol`。§II-A，式(2)后。 |
| 42 | pilot vector | [L68](../sections/02_system_model.tex:68) | **原词**：`arvinte2023`，PDF p.3，原词 `pilot vectors`。§II-A，式(1)后；原文向量是空间导频，本文为子载波导频；名称适用，但不照搬其维度或构造。此来源已列入当前 PDF，无需依赖 Quayum。 |
| 43 | known pilot matrix | [L71](../sections/02_system_model.tex:71) | **适配**：pilot matrix 见 Cai p.4；Arvinte p.3 有 having knowledge of the transmitted pilot matrix。known pilot matrix 这个完整搭配未核得，已知性条件不等于新方法名。 |
| 44 | satellite receiver | [L72](../sections/02_system_model.tex:72) | **原词**：`shen2025`，PDF p.1，原词 `satellite receiver`。摘要，名称原词。 |
| 45 | entries | [L72](../sections/02_system_model.tex:72) | **原词**：`cai2026`，PDF p.14，原词 `pilot matrix whose entries`。Fig.12 附近；为矩阵元素的通用名称。 |
| 46 | pilot energy | [L77](../sections/02_system_model.tex:77) | **外部用例**：上轮仅核得 Tang 等 arXiv:2610.23420 §III-A/p.3 的 total useful-sample pilot energy per frame；Tang 未在本稿书目库或 PDF 参考文献中。Cai p.4 用 transmit power budget，不能作该名称的直接出处，也不能不核对量纲就替换 energy 为 power。 |
| 47 | time-domain transmitted signal | [L82](../sections/02_system_model.tex:82) | **原词**：`ding2026`，PDF p.2，原词 `time-domain transmitted signal`。§II，式(1)前。 |
| 48 | inverse discrete affine Fourier transform (IDAFT) | [L82](../sections/02_system_model.tex:82) | **原词**：`ding2026`，PDF p.2，原词 `inverse discrete affine Fourier transform`。§II，式(1)前，原文同时给出 IDAFT。 |
| 49 | AFDM modulation parameters | [L91](../sections/02_system_model.tex:91) | **原词**：`ding2026`，PDF p.2，原词 `AFDM modulation parameters`。§II，式(1)后。 |
| 50 | sampling interval | [L93](../sections/02_system_model.tex:93) | **原词**：`ding2026`，PDF p.2，原词 `sampling interval`。§II，式(3)后。 |
| 51 | subcarrier spacing | [L94](../sections/02_system_model.tex:94) | **原词**：`huang2026`，PDF p.2，原词 `subcarrier spacing`。§II；Ding p.2 另有 sub-carrier spacing 的拼写。 |
| 52 | discrete affine Fourier transform (DAFT) matrix | [L109](../sections/02_system_model.tex:109) | **原词**：`ding2026`，PDF p.2，原词 `DAFT matrix`。名称 DAFT matrix 见 Ding；本轮另外重读 Xu §II-B/印刷p.3（带封面 PDF p.4）式(6)后，核得完整展开名称。在线证据见 REMOTE_EVIDENCE.json，不依靠不同单词拼接通过。 |
| 53 | chirp-periodic prefix (CPP) | [L111](../sections/02_system_model.tex:111) | **原词**：`bemani2022`，PDF p.8，原词 `chirp-periodic prefix`。§III-A，式(19)前；含 CPP 缩写。 |
| 54 | CPP length | [L111](../sections/02_system_model.tex:111) | **原词**：`bemani2022`，PDF p.9，原词 `CPP length`。§III-B，式(22)前；正文以括号展开 CPP。 |
| 55 | maximum differential delay | [L112](../sections/02_system_model.tex:112) | **原词**：`shen2025`，PDF p.12，原词 `maximum differential delay`。小段 3) Feasibility of integration with existing satellite infrastructure；名称直接出现，本文 CPP 条件仍是本文适配。 |
| 56 | time duration of an AFDM frame with CPP | [L125](../sections/02_system_model.tex:125) | **适配**：Shen §II-B/p.4 的原文为 time duration of a OFDM symbol with CP；本文换成 AFDM frame/CPP，不能说完整释义原样出现过。 |
| 57 | transmit waveform | [L128](../sections/02_system_model.tex:128) | **原词**：`shen2025`，PDF p.4，原词 `transmit waveform`。§II-B，式(3)前。名称源于 Shen；本文连续波形公式另有 Bemani 的技术依据，二者不要混同。 |
| 58 | CPP relation | [L138](../sections/02_system_model.tex:138) | **适配**：CPP 有 Bemani 原词，relation 是本文对式(5)的回指；未核得 CPP relation 完整名称，不作为既有专门关系名称通过。 |
| 59 | effective channel | [L141](../sections/02_system_model.tex:141) | **原词**：`huang2026`，PDF p.2，原词 `effective channel`。§II，式(4)–(5)后；本文三阶维度不是来源相同公式的保证。 |
| 60 | transmitted symbol position | [L151](../sections/02_system_model.tex:151) | **待核**：正文合写 transmitted and received symbol positions。Shen p.4 的 received symbol position 不能反向证明 transmitted symbol position；未核得当前发送符号索引含义的原词。 |
| 61 | received symbol position | [L151](../sections/02_system_model.tex:151) | **原词**：`shen2025`，PDF p.4，原词 `received symbol position`。§II-B，式(9)后的解释；Shen 为 delay 维，本文为 DAFT 输出位置，保留其通用索引含义，不声称域相同。 |
| 62 | antenna index | [L152](../sections/02_system_model.tex:152) | **书目库原词**：`ke2020`，PDF p.13，原词 `antenna index`。Appendix A；Ke 已在 references.bib，当前 main.bbl 没有该条。词源成立，不能宣称读者已能从当前 PDF 参考文献找到它。 |
| 63 | channel response | [L154](../sections/02_system_model.tex:154) | **原词**：`ding2026`，PDF p.2，原词 `channel response`。§III-A，式(6)前；使用名称，不照搬导频提取模型。 |
| 64 | power leakage | [L168](../sections/02_system_model.tex:168) | **原词**：`huang2026`，PDF p.2，原词 `power leakage`。§II，式(5)后。 |
| 65 | fractional delays | [L168](../sections/02_system_model.tex:168) | **原词**：`huang2026`，PDF p.2，原词 `fractional delay`。§II，式(5)前；单复数变化，不要求全文恰好有复数拼写。 |
| 66 | delay / delays | [L58](../sections/02_system_model.tex:58) | **原词**：`shen2025`，PDF p.3，原词 `delay`。物理路径时延名称；本文不另外命名 d、g 等辅助变量。 |
| 67 | Doppler shift / Doppler shifts | [L13](../sections/02_system_model.tex:13) | **原词**：`shen2025`，PDF p.3，原词 `Doppler shift`。§II-A；单复数变化。 |
| 68 | sparsity | [L169](../sections/02_system_model.tex:169) | **原词**：`huang2026`，PDF p.2，原词 `sparsity`。§II，式(5)后，信道稀疏性语境。 |
| 69 | wrap | [L177](../sections/02_system_model.tex:177) | **待核**：未在已核参考论文中找到将角度映射到 [-pi,pi) 的同名函数。3GPP 的计数器 wrap around 与 O'Leary 的 wrapper 不同义，不能用来通过。 |
| 70 | angle | [L181](../sections/02_system_model.tex:181) | **原词**：`shen2025`，PDF p.3，原词 `angle`。§II-A，角的基本名称；不能用该词的出处替代 wrap 算子的出处。 |
| 71 | phase evolution across frames | [L182](../sections/02_system_model.tex:182) | **适配**：当前引言贡献段有此表述，但本轮要求参考论文出处，不能以自己的引言证明已有论文用过。Shen p.5 的原词为 phase rotation，并说明 accumulates across multiple frames。 |

### 问题与概率模型

| 编号 | 第二章实际名称 | 正文行 | 判定与出处 |
|---|---|---|---|
| 72 | Problem Formulation | [L185](../sections/02_system_model.tex:185) | **原词**：`shen2025`，PDF p.5，原词 `Problem Formulation`。§II-C 原标题；Wei §II-B/p.2 也使用。 |
| 73 | independent and identically distributed (i.i.d.) | [L187](../sections/02_system_model.tex:187) | **原词**：`cai2026`，PDF p.4，原词 `independent and identically distributed`。§II-A，同时给出 i.i.d. 缩写。 |
| 74 | indicator function | [L191](../sections/02_system_model.tex:191) | **原词**：`cai2026`，PDF p.4，原词 `indicator function`。§II-A，式(1)前，与 0/1 活动指示用途一致。 |
| 75 | device activity | [L191](../sections/02_system_model.tex:191) | **原词**：`cai2026`，PDF p.4，原词 `device activity`。§II-A，式(1)前。 |
| 76 | probability of a device being active | [L199](../sections/02_system_model.tex:199) | **原词**：`cai2026`，PDF p.4，原词 `probability of a device being active`。§II-A，式(1)后；本文改概率变量字母不影响名称。 |
| 77 | activity states | [L200](../sections/02_system_model.tex:200) | **原词**：`ding2026`，PDF p.2，原词 `activity state`。§II，式(4)后。单数原词已核得，因此复数可以通过；但不能据此证明本文整块不变假设。 |
| 78 | block transmission | [L201](../sections/02_system_model.tex:201) | **原词**：`shen2025`，PDF p.1，原词 `block transmission`。§I；原文恒定的是 fading channels，本文活动不变仍是自己的假设。 |
| 79 | inter-frame phase rotation | [L203](../sections/02_system_model.tex:203) | **适配**：phase rotation 及其跨帧累积见 Shen p.5，但 inter-frame phase rotation 完整命名未核得。inter-frame interference 不能证明这个不同的名称。 |
| 80 | received signal | [L209](../sections/02_system_model.tex:209) | **原词**：`cai2026`，PDF p.4，原词 `received signal`。§II-A，式(3)前。 |
| 81 | AWGN matrix | [L218](../sections/02_system_model.tex:218) | **原词**：`cai2026`，PDF p.4，原词 `AWGN matrix`。§II-A，式(3)后；同为 i.i.d. 复高斯噪声矩阵。 |
| 82 | block-sparsity structure | [L241](../sections/02_system_model.tex:241) | **原词**：`cai2026`，PDF p.4，原词 `block-sparsity structure`。§II-A，式(4)后；对应设备不活动时整个块为零。 |
| 83 | sporadic access | [L240](../sections/02_system_model.tex:240) | **原词**：`cai2026`，PDF p.4，原词 `sporadic access`。§II-A，式(4)后。 |
| 84 | inverse problem | [L244](../sections/02_system_model.tex:244) | **原词**：`wei2026`，PDF p.2，原词 `inverse problem`。§II-B；当前观测的行列数条件仍按本文公式判断。 |
| 85 | underdetermined | [L244](../sections/02_system_model.tex:244) | **原词**：`wei2026`，PDF p.2，原词 `underdetermined`。§II-B；原词为 severely underdetermined，本文未沿用程度词。 |
| 86 | observation | [L215](../sections/02_system_model.tex:215) | **原词**：`cai2026`，PDF p.4，原词 `observation`。§II-B，目标段中的 observation Y。 |
| 87 | Bayesian inference framework | [L248](../sections/02_system_model.tex:248) | **原词**：`cai2026`，PDF p.4，原词 `Bayesian inference framework`。§II-B，目标段。 |
| 88 | channel sparsity | [L249](../sections/02_system_model.tex:249) | **原词**：`cai2026`，PDF p.1，原词 `channel sparsity`。§I；名称出处不意味着 Cai 使用本文相同的非稀疏信道模型。 |
| 89 | channel prior | [L251](../sections/02_system_model.tex:251) | **原词**：`cai2026`，PDF p.5，原词 `channel prior`。§II-B；本文 for training 只是 q_tr 的用途说明，不登记为独立名称 training prior 或 channel prior for training。 |
| 90 | joint posterior distribution | [L256](../sections/02_system_model.tex:256) | **原词**：`cai2026`，PDF p.4，原词 `joint posterior distribution`。§II-B，式(5)前；不自动证明本文固定前端后的后验等同于全联合后验。 |
| 91 | Bayes' theorem | [L257](../sections/02_system_model.tex:257) | **原词**：`cai2026`，PDF p.2，原词 `Bayes' theorem`。§I 的正确拼写；Cai p.4 的 Baye’s theorem 是误拼，不照抄。 |
| 92 | conditional independence relationships | [L258](../sections/02_system_model.tex:258) | **原词**：`cai2026`，PDF p.4，原词 `conditional independence relationships`。§II-B，式(5)前；具体独立对象是本文建模假设。 |
| 93 | column | [L271](../sections/02_system_model.tex:271) | **原词**：`cai2026`，PDF p.5，原词 `column`。式(5)后；第 j 列是本文索引。 |
| 94 | MMSE estimate | [L277](../sections/02_system_model.tex:277) | **原词**：`li2023`，PDF p.8，原词 `MMSE estimate`。§IV-A，原文使用 estimate；Cai p.4 使用 MMSE estimator，不能混报词形。 |
| 95 | posterior probability of activity | [L277](../sections/02_system_model.tex:277) | **原词**：`cai2026`，PDF p.7，原词 `posterior probability of activity`。§III-B2，式(30)后。 |

### 具名算子

| 编号 | 第二章实际名称 | 正文行 | 判定与出处 |
|---|---|---|---|
| 96 | diag | [L159](../sections/02_system_model.tex:159) | **原词**：`shen2025`，PDF p.3，原词 `diag`。Notations 给出从元素组成对角矩阵的同义算子。wrap 已单独列出。 |

## 对上轮记录的补充与纠正

1. **pilot vector**：现已在当前参考文献 Arvinte §II-A/p.3 核到 pilot vectors，不再只依赖书目外的 Quayum。原文为向量导频；这里仅据此认定名称适用，不照搬空间维度和导频码本。
2. **activity states**：Ding §II/p.2 的 activity state 是同一活动指示含义。允许单复数后可以通过。不能因为只搜索复数未命中就判定无出处。
3. **antenna index**：Ke Appendix A/p.13 的词源成立，而且 Ke 本来就在 references.bib；但当前 PDF 没有引用到 Ke。应区分“书目库已有”和“阅读稿列出”。
4. **pilot energy**：Tang 的用例不能算作本稿已有参考文献。此前“补查有出处”不能简写成“当前参考文献已有出处”。
5. **arrival angles**：不能由 angle of arrival / angles-of-arrival 推出词序已被原文使用。此前变量核查未单列这处描述，本轮补上。
6. 通过的是名称与语义，不是全部句子、全部模型条件和全部推导都来自同一参考论文。此前若作过“第二章所有内容都从已有论文来”的笼统保证，应以本清单为准撤回该保证。

## 来源与复核入口

| 书目键 | 本地原论文 | 本轮主要定位 |
|---|---|---|
| shen2025 | [Shen PDF](../../reference/literature/shen2025.pdf) | pp.1–5、12 |
| cai2026 | [Cai PDF](../../reference/literature/cai2026.pdf) | pp.1–5、7、11、14 |
| ding2026 | [Ding PDF](../../reference/literature/ding2026.pdf) | p.2；不是 ding2026_iccdm |
| huang2026 | [Huang PDF](../../reference/literature/huang2026.pdf) | pp.2、4 |
| li2023 | [Li PDF](../../archive/figure_cleanup_20261104/retired_files/paper/checks/strict_sentence_audit_20261029/sources/li2023.pdf) | pp.3–4、8 |
| bemani2022 | [Bemani PDF](../../archive/figure_cleanup_20261104/retired_files/paper/checks/strict_sentence_audit_20261029/sources/bemani2022.pdf) | pp.1、8–9 |
| wei2026 | [Wei PDF](../../reference/literature/wei_yuan_2026_lstmp_v1.pdf) | p.2 |
| arvinte2023 | [Arvinte PDF](../../archive/figure_cleanup_20261104/retired_files/paper/checks/full_terminology_audit_20261030/downloaded_sources/arvinte2023.pdf) | §II-A，p.3，式(1)后 |
| ke2020 | [Ke PDF](../../reference/literature/ke2020_gmmv_amp.pdf) | Appendix A，p.13；当前 PDF 未列该参考文献 |

Xu 的 DAFT 矩阵完整名称另经 [Surrey 作者稿](https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/AFDM-aided-Grant-Free-Random-Access-for-LEO/991050765702346)在线 PDF 文本复核，定位为 §II-B、印刷 p.3／PDF p.4、式(6)后；见 [在线证据](../checks/ch2_all_names_20261101/REMOTE_EVIDENCE.json)。未将部分在线核验计入本地全篇检索覆盖。

每项原文上下文见 [INVENTORY.json](../checks/ch2_all_names_20261101/INVENTORY.json)。检索命中只是取证辅助；wrap 的不同义命中明确未通过。第二章全部行均已人工通读，机器检查只验证登记名称确实出现在正文、登记的原词确实出现在指定来源页，以及正文未被更改，不能自动证明语言清单没有遗漏。

本轮不改正文、不改公式、不新增引用。书目覆盖和完整表述未通过的项目保留待处理，不能为了通过审计而把本文适配伪称为引用原词。
