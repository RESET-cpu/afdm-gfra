# 引言结构修订依据（2026-10-27，待作者审阅）

本轮保留背景三段与稀疏模型综述段，修改多帧传输、生成式先验、训练误差和活动推断的衔接，并重分配三点贡献。英文为针对本稿方法的改写，不是参考论文逐句摘录；未执行或宣称通过旧摘要的四篇逐词词形检查。摘要、关键词、模型、算法、实验及 main.pdf 不变；按作者要求不编译。

## 文献与方法对应

| 内容/术语 | 原文位置 | 本轮使用范围 |
|---|---|---|
| spreading-based multi-frame OTFS transmission scheme；quasi-static properties；large differential delay and Doppler shift | Shen2025 §I 贡献，PDF p.2；§II-B，PDF p.4；摘要，PDF p.1 | 描述已有OTFS多帧方案；不再将“shared channel”当作Shen原词。AFDM扩展及其输入输出关系是本稿工作。 |
| AFDM effective channel；restrictive sparse or grid-aligned channel assumptions；likelihood-annealed Langevin dynamics | Huang2026 摘要与§I，PDF p.1 | 说明直接学习有效信道的依据与Huang采用的推断方法；本稿没有采用其在线朗之万采样流程。 |
| Gaussian denoising；posterior mean and variance；activity uncertainty；linear estimation module；extrinsic message | Cai2026 §III，PDF pp.5–8，特别是§III-B式(15)后及式(22)–(30)；§IV，PDF pp.8–9 | 说明继承的MP推断结构、条件信道矩与活动不确定性的分工；不声称新创MP框架，也不暗示Cai没有活动推断。 |
| generalized expectation-consistent approximation；colored Gaussian noise；denoiser input error | Shastri2022/D-GEC §III-A，PDF p.11；§III-B式(38)与训练说明，PDF pp.15–16 | 支持结构化算子下输入误差未必白化、有色噪声去噪的动机。本稿AFDM误差可能相关是模型层面的推断，不是该文对AFDM的实验证明。本稿不采用其完整D-GEC算法或corr+corr网络。 |
| density ratio estimator；binary classification | Menon–Ong2016 §3式(6)–(8)、§4.2式(16)–(17)，PDF p.3/印刷p.306；既有术语记录已核对官方原文 | 支持分类学习密度比；引言新增既有文献键menon2016。该术语不归于四篇核心论文。 |

本轮前四篇原文核对使用 `../abstract_sources_20261026/` 中带PDF页码的文本缓存。Menon来源沿用 `../../docs/TERMINOLOGY.md` 中已核对的原文记录及现有正文引用。

## 与本稿公式的对应

- 多帧观测、前缀相位、帧间相位分离及MMV表述依据第II节。信道维度不随帧数增加的结论保留块内信道模型条件。
- 有色扰动与协方差条件输入依据第IV-A/D节。在线仍使用标量查询协方差；本轮只把实现细节移出引言，没有声称在线跟踪完整有色误差协方差或训练分布等于实际迭代误差分布。
- 活跃密度的边缘化及密度比到概率的关系依据第III节 `eq:query-densities`、`eq:local-activity`，分类训练与先验修正依据第IV-C节 `eq:ideal-logit`。
- 估计器使用信道去噪特征的概括涵盖输入、噪声水平和条件均值等；不表示其输入包含后验方差，也不表示原始网络输出直接是活动概率。
- 条件后验矩与软活动概率的组合依据 `eq:exact-local-moments` 及后续近似实现。方差仍来自均值导数，没有引入额外二阶网络。

## 编辑范围

1. 压缩AFDM通用实现细节，把Shen多帧方案放到传输建模的动机中。
2. 第二点贡献集中描述有效信道先验与有色高斯扰动训练。
3. 第三点贡献概括后验矩、密度比估计和MP迭代的配合；删除均值导数及标量方差更新的实现细节。
4. 保留正文原有技术定义及引用。中文编号按引言引用顺序同步；未编译，不更新现有PDF的引用编号。
