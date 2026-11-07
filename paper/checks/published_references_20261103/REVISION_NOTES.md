# 正式出版版本核对与预印本条目清理

2026-11-03。范围仅为当前 C-STMP 稿的引用与出版信息，不改变算法、公式、实验、图件、摘要或结论。

## 已完成的替换

| 原引用 | 正式引用与 DOI | 必要更正 |
|---|---|---|
| Xu 2019, arXiv:1911.08133 | Zou et al., ICC Workshops 2021, pp.1–6；10.1109/ICCWorkshops50388.2021.9473771 | 正式版第一作者为 Tingting Zou，第二作者为 Wenjun Xu；键改为 zou2021otfs |
| Dytso 2021, arXiv:2104.01883 | Dytso, Poor, Shamai (Shitz), IEEE TIT 69(3):1883–1898, 2023；10.1109/TIT.2022.3216012 | 正式标题为 Conditional Mean Estimation in Gaussian Noise: A Meta Derivative Identity With Applications；键改为 dytso2023 |
| Shastri 2022, arXiv:2206.05049v2 | IEEE JSAIT 3(3):528–542, 2022；10.1109/JSAIT.2022.3207109 | 补齐卷、期、页码，保留 shastri2022 |
| Metzler 2014, arXiv:1406.4175 | IEEE TIT 62(9):5117–5144, 2016；10.1109/TIT.2016.2556683 | 键改为 metzler2016 |

出版信息分别核对 DOI 的 Crossref 记录（metadata/）与出版方、作者机构记录：[Zou](https://khazna.ku.ac.ae/en/publications/low-complexity-linear-equalization-for-otfs-systems-with-rectangu/)、[Dytso](https://collaborate.princeton.edu/en/publications/conditional-mean-estimation-in-gaussian-noise-a-meta-derivative-i/)、[Shastri 正式 PDF](https://phil-schniter.web.app/pdf/jsait22_dgec.pdf)、[Metzler](https://scholars.houstonmethodist.org/en/publications/from-denoising-to-compressed-sensing/)。

## 正文处理与来源定位

- 作者最新指示是保留 Wei 对应论述，只去掉引用标号。因此保留 “A similar limitation has been highlighted for structured compression matrices.”，仅删除原句的 `in` 和引用命令；不再从正文或参考文献列出 Wei2026。原有阅读记录保留其来源，不把这句话登记为本次新增或独立验证的结论。
- Dytso 正式 PDF 第1页（1883）式(3)给出条件均值；第3页（1885）III 节 Proposition 1、式(17)给出导数与条件方差恒等式。正文 Prop.1 定位仍有效。原文 Jacobian 排列与本稿定义相差转置，当前右乘协方差的公式沿用既有定义，不改变数学。
- Shastri 正式 PDF 第8页（535）III-B “DNN Denoiser for Correlated Noise”、式(38)直接描述已知协方差的有色高斯噪声输入；正文 III-B 定位仍有效。本文协方差结构和网络设计仍属于自己的适配。
- Metzler 作者公开稿第15页 V-B “Monte Carlo method”支持散度的有限差分估计；本轮未取得排版后的出版社全文核对同节编号，因此正文保留正式文献引用并去掉原作者稿的节号。随机符号探针和协方差加权仍是本稿既有适配。
- Zou 会议版已核实标题、作者顺序、年份、页码和 DOI；本轮无法读取出版社 PDF，未声称核实其公式编号。因此移除旧作者稿式(1)/(4)/(5)的精确编号，保留正式文献引用。变换消去的数学依据仍见此前 SOURCES.md 对作者稿 II-A/B 的核对，不改变本稿公式或复杂度结论。

已有正式发表条目的作者稿链接属于内部来源字段，不作为预印本条目输出。已发表论文、正式 Early Access、标准与学位论文继续保留；文献库中的历史 PDF 不删除。其他稿件未改动。

## 编译与检查

- 两版均重新编译：main **13 页**，main_full **15 页**，均为 **42 篇**参考文献。
- 输出参考文献无 arXiv/preprint 条目，无未解析引用、错误引用键或越界排版警告。
- 62 个陈列数学环境逐一对照不变；图件引用和标签不变。引言除指定引用与介词外逐字保持，其余正文仅改变引用键或定位。
- 所有最终页面已重新渲染；检查两版概览、引言和参考文献页，未见裁切、覆盖或引用排版异常。原有两条 underfull 段落提示和图件 PDF 版本提示不影响输出。
- 机器核验见 VALIDATION.json，实际源码差异见 CHANGES.diff，修改前源码及 PDF 在 before/；新正式 PDF 来源与哈希见 SOURCES.json。
