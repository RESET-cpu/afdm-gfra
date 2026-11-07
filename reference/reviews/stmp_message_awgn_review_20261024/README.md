# STMP 消息模型相关论文库

更新：2026-10-24。围绕固定 AFDM、低 SNR 活动检测和 AWGN 预训练网络的实际查询失配，汇总此前讨论的 24 篇论文，并补充 1 篇非可分 AMP 普适性论文。

**已取得 24 篇全文：19 篇新下载、5 篇复用已有文件，共 459 页。唯一未取得全文的是 Cheng 等 2021 年 JSAC 论文。** 原文以公开预印本/作者稿为主，不能把各版本页码混为期刊页码。

先看 [哪些地方可参考及与旧实验的区别](../../../paper/STMP/docs/STMP_PAPER_READING_NOTES_20261024.md)。建议阅读顺序：**18 D-GEC → 08 相关信道 AMP → 14 OAMP-MMV → 20 FIRE**。

全部可用 PDF 已核对首页身份、页数并提取分页文本；下载记录含来源、字节数和 SHA-256。本次重点阅读有关方法、假设与实验段落，不宣称逐页审完全部证明。

## 全文清单

| 编号与原文 | 固定版本 / PDF 页数 | 本项目可参考内容 |
|---|---|---|
| [01 · Orthogonal AMP](../../literature/ma2017_oamp_v3.pdf) | 2017; arXiv v3 / 13 页 | 迹去相关与无散度反馈的来源 |
| [02 · Vector Approximate Message Passing](../../literature/rangan2019_vamp.pdf) | 2019; arXiv v2 / 21 页 | 两模块后验、散度、外信息的对称接口 |
| [03 · Plug-in Estimation in High-Dimensional Linear Inverse Problems: A Rigorous Analysis](../../literature/fletcher2019_nonseparable_vamp.pdf) | JSTAT 2019 / 15 页 | 非可分网络的理论条件；旋转后的反馈误差 |
| [04 · D-OAMP: A Denoising-Based Signal Recovery Algorithm for Compressed Sensing](../../literature/xue2016_doamp.pdf) | 2016; arXiv v1 / 5 页 | 通用去噪器散度与 SURE；旧适配已试 |
| [05 · Denoising-based Turbo Compressed Sensing](../../literature/xue2017_dturbo.pdf) | 2017; arXiv v1 / 11 页 | 通用外信息；相关信号与真实测量随机化 |
| [06 · Massive Connectivity with Massive MIMO—Part I: Device Activity Detection and Channel Estimation](../../literature/liu2018_massive_mimo.pdf) | 2018; arXiv v2 / 14 页 | 矩阵状态何时可化为标量；活动检测 |
| [07 · Performance Analysis of Approximate Message Passing for Distributed Compressed Sensing](../../literature/hannak2018_mmv.pdf) | 2018; arXiv v2 / 13 页 | 完整 MMV Jacobian；先验与估计器同步变换 |
| [08 · User Activity Detection and Channel Estimation of Spatially Correlated Channels via AMP in Massive MTC](../../literature/djelouat2021_correlated_amp.pdf) | 2021; arXiv v1 / 5 页 | 有色 Gaussian 活动似然；R 与 Σ 分开 |
| [09 · Complex Approximate Message Passing with Non-separable Denoising](../../literature/kunde2026_complex_amp.pdf) | 2026; arXiv v1 / 28 页 | 复数非可分 Jacobian 部分迹；结构矩阵边界 |
| [10 · Hierarchical MTC User Activity Detection and Channel Estimation with Unknown Spatial Covariance](../../literature/djelouat2024_hierarchical_ep.pdf) | TWC 2024; arXiv 2023 v1 / 31 页 | 矩阵 cavity/site 与先验协方差学习；预印本公式需核对 |
| [11 · Memory AMP](../../literature/liu2022_memory_amp.pdf) | 2022; arXiv v7 / 24 页 | 完整记忆递推与历史正交条件 |
| [12 · Sufficient-Statistic Memory AMP](../../literature/liu2023_ssmamp.pdf) | 2023; arXiv v4 / 21 页 | 跨轮协方差加权的条件；不等于残差融合 |
| [13 · On the Convergence of Orthogonal/Vector AMP: Long-Memory Message-Passing Strategy](../../literature/takeuchi2022_long_memory.pdf) | 2022; arXiv v2 / 18 页 | 阻尼交叉项；有限维负结果 |
| [14 · Orthogonal AMP for Problems with Multiple Measurement Vectors and/or Multiple Transforms](../../literature/cheng2023_oamp_mmv.pdf) | TSP 2023; arXiv v1 / 14 页 | 矩阵信号增益与误差协方差一起传递 |
| [15 · On Orthogonal Approximate Message Passing](../../literature/liu2023_orthogonal_principle.pdf) | TCOM 2023, published as On OAMP: Impact of the Orthogonal Principle; arXiv v2 / 15 页 | 积分/Monte Carlo 与导数正交化；增益归一化 |
| [16 · Approximate Message Passing with a Colored Aliasing Model for Variable Density Fourier Sampled Images](../../literature/millard2020_vdamp.pdf) | 2020; arXiv v3 / 13 页 | 分组精度、密度补偿与噪声代价 |
| [17 · D-VDAMP: Denoising-based Approximate Message Passing for Compressive MRI](../../literature/metzler2020_dvdamp.pdf) | 2020; arXiv v1 / 5 页 | 有色噪声条件网络；低 SNR 性能反例 |
| [18 · Denoising Generalized Expectation-Consistent Approximation for MR Image Recovery](../../literature/shastri2022_dgec.pdf) | 2022; arXiv v2 / 40 页 | 重点：分组消息接口与 corr+corr |
| [19 · MRI Image Recovery using Damped Denoising Vector AMP](../../literature/sarkar2020_ddvamp.pdf) | ICASSP 2021; arXiv 2020 v1 / 5 页 | 初始化与阻尼一致性；旧适配已试 |
| [20 · Solving Inverse Problems using Diffusion with Iterative Colored Renoising](../../literature/bendel2025_fire.pdf) | TMLR 2025; arXiv v4 / 31 页 | posterior 补噪对象、独立性和功率代价 |
| [21 · Learned D-AMP: Principled Neural Network based Compressive Image Recovery](../../literature/metzler2017_ldamp.pdf) | NeurIPS 2017; arXiv 1704.06625v4, 2017-11-06; verified on PDF first page / 14 页 | 端到端/逐层/独立去噪训练的比较 |
| [22 · Orthogonal AMP for Massive Access in Channels With Spatial and Temporal Correlations](https://doi.org/10.1109/JSAC.2020.3018799) | JSAC 2021 / **未取得全文** | 仅书目与摘要，不能据此引用正文公式 |
| [23 · Joint Activity Detection and Channel Estimation for Massive Connectivity: Where Message Passing Meets Score-Based Generative Priors](../../literature/cai2026_stmp_v2.pdf) | 2026; arXiv v2 / 16 页 | 现有 STMP 基础；联合活动矩与工程阻尼 |
| [24 · Learned Score-Based Turbo Message Passing for Channel Recovery From Spatially Compressed Measurements](../../literature/wei_yuan_2026_lstmp_v1.pdf) | 2026; arXiv v1 / 5 页 | 展开校准与 score 联合微调；单用户边界 |
| [25 · On Universality of Non-Separable Approximate Message Passing Algorithms](../../literature/lovig2026_universality.pdf) | 2026; arXiv v2; supplementary scope check / 82 页 | 补充：非可分普适性的反例与额外条件 |

## 阅读记录

- [基础、STMP 与展开](notes/download_followup_foundations.md)：01–04、15、21、23–25。
- [有色噪声与补噪](notes/download_followup_colored.md)：05、16–20。
- [MMV 与活动检测](notes/download_followup_mmv.md)：06–10。
- [记忆与正交化](notes/download_followup_memory.md)：11–14，以及 22 的全文获取尝试。
- [修订后的整体调研](../../../paper/STMP/docs/STMP_MESSAGE_AWGN_REVIEW_20261024.md)：已补入完整矩阵 AMP、FIRE/DD-VAMP、历史融合的既有负结果。
- [术语与公式定位](../../../paper/STMP/docs/TERMINOLOGY.md)。

## 版本与缺失说明

- 22 的作者主页与 CityU 页面仅提供摘要/出版链接；IEEE PDF 入口本次未返回可用全文，完整尝试见记忆笔记。没有用其他论文替代或生成空 PDF。
- 10 已保存 2023 arXiv v1 全文；补取 Oulu 2024 期刊最终版返回 403，因此本地公式定位只对应预印本。
- 21 从未指定版本的 arXiv 地址下载，首页核实为 1704.06625v4（2017-11-06）。
- 25 为补充条件核查，已读 pp.1–3 的问题、反例和结论概要，没有审阅全部 82 页证明。
- [当前获取记录](DOWNLOAD_MANIFEST.json) 是本轮状态；[上一阶段记录](main_sources/MANIFEST.json) 保留当时的失败，不代表这次仍失败。

## 文件组织与验证

- [论文库](../../literature/README.md)：完整原文；text/：以 PDF 页码分隔的提取文本。
- notes/：原文位置、可借鉴操作、代码对应和不能直接迁移的条件。
- page_checks/：部分关键公式/结果页的核对图；其余核对图路径见各笔记。
- [本轮验证记录](DOWNLOAD_VALIDATION.json)：PDF 哈希、解析、文档链接和阅读覆盖。

本轮未改算法、模型绑定或权重，未启动训练或接收机实验。文献评价与项目推断由 AI 辅助完成，所有实际实验数值均引用既有落盘记录。
