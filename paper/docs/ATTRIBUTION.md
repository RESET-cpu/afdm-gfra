# 方法来源与许可

Score 网络骨干保存在 [proposed/cai_models/](../../src/afdm_jadcedd/algorithm/proposed/cai_models)，
代码来源为 Cai 作者项目；许可证见该目录的 [LICENSE](../../src/afdm_jadcedd/algorithm/proposed/cai_models/LICENSE)
及项目保留的 [LICENSE.cai](../../src/afdm_jadcedd/LICENSE.cai)。
作者主程序的固定提交、下载地址和 SHA 见 [来源记录](../../reference/reviews/known_phase_iteration_review_20260928/cai_code_provenance.json)。
该程序快照用于源码对照，记录中未声明执行过作者完整实验。

消息传递、Tweedie 条件矩和一、二阶得分匹配的文献定位见 [TERMINOLOGY.md](TERMINOLOGY.md)。
本项目的观测模型、活动分类器接法、共享方差和停止规则分别定义于
[SYSTEM_MODEL.md](SYSTEM_MODEL.md) 与 [THEORY.md](THEORY.md)。
Baseline 来源及 AFDM/MMV 适配见 [BASELINES.md](BASELINES.md)。
`offgrid/sbl.py` 根据 Wei 的论文公式独立编写；Zhu 方法的实现保存在 [MNOMP 归档](../../archive/paper_layout_20261026/original_paper/docs/history/archive/mnomp_20261014/README.md)。
物理原子、MMV 推导和数值设置见 [OFFGRID_BASELINES.md](OFFGRID_BASELINES.md)。

选定网络的原始 checkpoint 及配对元数据由 [权重索引](../../result/models/README.md) 定位。
