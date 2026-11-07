# 有色噪声网络结构调研

2026-10-24，定向文献核读与当前实现诊断。主报告：[网络结构是否需要更换](../../../paper/C-STMP/docs/COLORED_SCORE_ARCHITECTURE_REVIEW_20261024.md)。

- `dgec_interfaces.md`：D-GEC、D-VDAMP、FFDNet、DRUNet 的条件接口、训练目标与官方代码。
- `preconditioning.md`：EDM、矩阵预条件先例与本项目公式。
- `architecture_audit.md`：当前条件编码、归一化、幅度表示和证据边界。
- `CONDITION_PROBE.json/.npz`、`condition_probe.py`：第20轮冻结权重在64个不同开发场景上的条件诊断，仅CPU推断，没有训练。
- `LINEAR_REFERENCE_CHECK.json`：分解形式与密集求解的一次代数核对。
- [论文库](../../literature/README.md)、`text/`、`code/`：新下载论文、分页文本和未执行的作者代码。D-GEC与D-VDAMP复用前一批已下载原文。
- `backbone_downloads.json`：本代理下载的DnCNN、Restormer、NAFNet原文及哈希。其代码固定版本在`code/backbone_sources.json`。

检索于2026-10-24执行，关键词包括colored Gaussian noise / known covariance denoising、D-GEC corr+corr、covariance preconditioning、EDM、matrix-form EDM、FFDNet、DRUNet、Restormer及NAFNet。证据只采用论文原文及作者仓库；未进行PRISMA穷尽检索、跨论文性能合并或AFDM新结构训练。论文选择性细读范围由各笔记记录。

研究问题是“当前单一C族下，先改输入输出和条件模块，还是换整个主干”。搜索结果中的新扩散框架并不自动比已有方法更适用；仅筛查的论文不得算作已验证方案。
