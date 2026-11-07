# C-STMP 摘要逐词核验

范围为本轮英文摘要及关键词；中文是同义翻译。全部英文词形均在指定四篇论文的摘要或正文中检出，排除参考文献列表。只统一大小写及 Unicode 排版字符，不采用词干归并、近义词替代、停用词或方法名豁免。连字符词按完整词形匹配。

本核验不表示整句来自文献，也不表示这些论文已经提出本项目的全部操作或证明本项目的结果。句子仍描述当前 AFDM 系统与接收机。技术含义、原文位置和适配边界另见 paper/C-STMP/docs/TERMINOLOGY.md；结果来自本项目已保存实验。

- 英文摘要：175 词，120 个不同词形。
- 摘要与关键词合计：121 个不同词形；未检出词形：0。
- 技术短语：31 项；未检出项：0。
- 中文摘要：295 个汉字（不计标题）。
- 逐词证据：[WORD_AUDIT.json](WORD_AUDIT.json)。
- 短语证据：[TERM_AUDIT.json](TERM_AUDIT.json)。
- 重查程序：[verify_source_words.py](verify_source_words.py)。

| 摘要中的短语 | 原文首次匹配位置（PDF 页码） |
|---|---|
| joint activity detection and channel estimation | cai2026，p.1 |
| grant-free random access | shen2025，p.1 |
| global navigation satellite system | shen2025，p.1 |
| multi-frame transmission scheme | shen2025，p.13 |
| affine frequency division multiplexing | huang2026，p.1 |
| large differential delay and Doppler shift | shen2025，p.1 |
| input-output relationship | shen2025，p.2 |
| score-based generative channel prior | cai2026，p.2 |
| AFDM effective channel | huang2026，p.1 |
| grid-aligned channel assumptions | huang2026，p.1 |
| fractional delay | shen2025，p.4 |
| Doppler | shen2025，p.1 |
| colored Gaussian noise | dgec，p.15 |
| Internet-of-Things | shen2025，p.1 |
| score-based generative models | huang2026，p.1 |
| We firstly propose | shen2025，p.1 |
| Subsequently | shen2025，p.2 |
| denoiser input error | dgec，p.1 |
| correlations | cai2026，p.2 |
| Numerical simulations | cai2026，p.1 |
| the proposed receiver | shen2025，p.10 |
| in terms of | shen2025，p.1 |
| message passing | shen2025，p.1 |
| channel prior | cai2026，p.1 |
| satellite receiver | shen2025，p.1 |
| minimum mean-squared error | cai2026，p.1 |
| posterior mean and variance | cai2026，p.5 |
| high-dimensional integrals | cai2026，p.4 |
| activity uncertainty | cai2026，p.6 |
| soft information | shen2025，p.1 |
| linear estimation module | cai2026，p.2 |

“共享信道观测 / shared effective channel”已从摘要删除；改用 Shen 的 quasi-static property 与 consecutive frames。C-STMP 是作者的方法名，不在这四篇原文中，本轮摘要不使用该名称。旧版摘要源文件保存在 before/；不保存历史 PDF。逐句来源与本项目适配边界见 SENTENCE_SOURCES.md。

补充术语 density ratio estimator 见 Menon–Ong §4.2式(17)，PDF p.3；独立于四篇连续短语核验，见 ACTIVITY_DENSITY_RATIO_SOURCE.json。
