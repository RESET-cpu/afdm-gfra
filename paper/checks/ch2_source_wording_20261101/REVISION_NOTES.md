# 第二章：按已有出处修正表达（2026-11-01）

本轮授权：“有明确替代依据的都给我换成有出处的表达，不通过的请你修正”。修改对象为 `sections/02_system_model.tex`，以本目录 `before/02_system_model.tex` 中已恢复的原稿为基线。此前被撤回的修改仍保持撤回状态，本次是新授权的措辞修改。

## 修改对照与具体依据

下列页码均为本地 PDF 从 1 开始的页码。来源范围为稿件已有参考文献及当前摘要、引言，没有为迁就用词另添文献。表中区分原词、句式借用和本文公式说明，不把符号或对象替换后的句子登记成文献完整原句。

| 原表达 | 修改后 | 出处与说明 |
|---|---|---|
| `path count`；`Dirac delta` | `number of physical paths`；`Dirac delta function` | Shen p.3，§II-A 式(1)后及 Notations，有完整原词。 |
| differential delay `subtracts`…；`beam footprint` | `represents the differential delay`；`propagation delay and common delay`；`corresponds to the propagation time`；`within the beam coverage` | Shen p.3，§II-A 式(1)后。保留原差分时延等式，改用原文定义方式。`closest` 已目视核实，文本提取误拆为 `closes t`。 |
| `element spacings`；`two array axes` | `the spacing between adjacent antennas along the y-axis and z-axis` | Li p.4，§II-B：`the spacing between adjacent antennas along the v-axis`；Shen p.3，§II-A：`directional cosines`、`z-axis`、`y-axis`。代入本文坐标。 |
| `We allocate`…`to pilot transmission` | `Assume that a total of`…`are allocated for pilot transmission` | Cai p.4，§II-A，原对象为 T 个 OFDM 符号，此处为 Q 个 AFDM 帧；仅借用分配导频的句式。 |
| `By the chirp periodicity, the prefix samples satisfy` | `The prefix is`，接原式(5) | Bemani p.8，§III-A 式(19)前有 `the prefix is`；保留既有名称 `chirp-periodic prefix (CPP)`。 |
| `To specify the waveform between sample times`；`normalized time`；`AFDM basis waveform` | `For time` ξT_s，`let`…`Define`，接原 φ_n 定义 | 删除没有完整名称依据的描述，直接定义。`time`、`Let`、`Define` 均为来源中的已有用词；ξT_s 是原归一化时间的物理时间。该 φ_n 属于本文原公式，不声称文献已有同名模型。 |
| `For integer useful samples` | `For` t=0,…,N−1 | Bemani p.8，§III-A 式(18)给出 IDAFT 样本范围；本文原等式的适用范围不变。 |
| `After CPP removal and DAFT demodulation`；`after CPP removal` | `After removing the CPP and applying the DAFT`；`After removing the CPP` | Cai p.4，§II-A 式(3)前为 `After removing the CP and applying the DFT`；CPP、DAFT 是 Bemani p.8，§III 的既有名称。按本文操作替换对象。 |
| `unit-gain path`；`normalized delay`；`path matrix` | `For path gain` 1，`delay` dT_s，`and Doppler shift` ν，`the channel matrix is` | Shen p.3，§II-A：`path gain`、`Doppler shift`；Huang p.2，§II：`channel matrix`。用原物理量及取值限定 G，不另命名。 |
| `whose useful interval starts at sample g`；`Frame 0 starts at`… | t_c=(g+t)T_s，t=0,…,N−1；`For frame` 0，g=N_CPP | 直接展开原 G 中 νT_s(g+t) 与原时间定义的关系，g 的起点含义不变。这是本文模型的等价说明，不声称文献采用同一 g。 |
| `integer-delay form` | `the expression for integer` d | `expression`、`integer` 均见 Bemani；以本文变量 d 直接指明特殊情形。 |
| `the N samples after CPP removal start at` g_q | `After removing the CPP in frame q, let` g_q=… | `After removing` 依据同上；g_q 原公式保持，与前述样本时间关系配合。 |
| `observe the same H_k up to phase rotation` | `Separating the phase evolution across frames yields the same H_k for all q` | 当前引言贡献第1点已有 `Separating the phase evolution across frames yields`；含义对应本文式(9)。 |
| `maintains its activity state throughout a transmission block` | `The activity states are assumed to remain constant during one block transmission` | Shen p.1，§I 有 `are assumed to remain constant during one block transmission`；此处仅借用不变性句式，保持本文原活动假设，不称 Shen 对活动作了相同假设。 |
| `device inactivity gives block sparsity through`… | `Due to the sporadic access of the devices`…`exhibits a block-sparsity structure`，接 inactive 时的原零块条件 | Cai p.4，§II-A 式(4)后，完整短语及零块条件均有明确依据。 |
| `training prior`；`retains dependence within` | `For training, we use the channel prior q_tr(H_k), rather than factorizing it element-wise` | `channel prior` 沿用当前摘要／引言及 Cai；Cai p.1 摘要有 `rather than factorizing it element-wise`。q_tr 仍为训练信道分布，没有改称另一已学习分布。 |
| `devices and their activity/channel variables are otherwise independent` | 明确写 H_k 与 α_k 对不同 k 独立，且同一 k 的 H_k 与 α_k 独立 | Li p.5，§II-C 有 `we assume that`…`are independent for different`…；Cai p.4，§II-B 式(5)有同类分解。展开本文原假设和原后验式，不移植 Li 的路径独立模型。 |
| `With Bernoulli activity priors, the posterior factorizes as` | `We factorize the joint posterior distribution as` | Cai p.4，§II-B 式(5)前有完整用词。后文原 p(α_k)=ρ^{α_k}(1−ρ)^{1−α_k} 保持，Bernoulli 分布没有变。 |
| `The desired MMSE estimate` | `The MMSE estimate` | 删除未在所核语料匹配到、也无必要的 `desired`；`MMSE estimate` 沿用既有文献，目标定义不变。 |

## 核验结果

- 15 个编号公式、2 个无编号陈列公式及全部标签保持原样（忽略排版空白比较）。正文内新增／改写了等价表示：ξT_s、路径增益 1、时延 dT_s、t_c=(g+t)T_s、样本范围，以及 q_tr 的参数和独立性变量。因此不将本轮描述为“所有数学文字逐字未变”。
- 摘要、引言、书目、其他章节及插图共 20 个受保护文件与修改前 SHA-256 一致。模型假设、算法和实验设置未改。
- 去除 LaTeX 命令、引用键及公式后，正文共有 254 种英文词形，全部在六份既有参考文献或当前摘要、引言找到；唯一自动匹配失败的 `closest` 已通过 Shen p.3 原图确认。逐词来源见 [WORD_SOURCES.json](WORD_SOURCES.json)。词形检查不代替技术搭配核验，上表另列了短语出处及适用范围。
- 检索的 16 个旧问题搭配已全部从第二章移除。完整逐行差异见 [CHANGES.diff](CHANGES.diff)。
- `main.pdf` 编译成功，仍为 13 页；无未定义引用，无 overfull box。已查看第 2–4 页，第二章文字、公式及跨页衔接正常。编译仍有 underfull box 提示，未发现影响阅读的溢出或重叠。

源 PDF 路径及哈希见 `../ch2_sentence_source_check_20261030/SOURCES.json`；本轮六份源文件哈希均一致。页文本见 `SOURCE_PAGES.json`，检查结果见 [VALIDATION.json](VALIDATION.json)。
