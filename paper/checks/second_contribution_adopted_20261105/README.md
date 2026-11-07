# 采用作者确认的第二点表述

2026-11-05，作者确认采用“利用 Tweedie 公式……并省去独立二阶模型对应的训练与存储开销”三句话。本轮逐字写入中文摘要，并将对应英文同步用于英文摘要与引言第二项贡献。

英文采用已讨论的版本：

> Using Tweedie's formula to relate the score function to the posterior mean, we construct a channel denoiser based on the learned prior. We then exploit the relation between conditional-mean derivatives and posterior covariance to estimate the average posterior variance required for message passing. This avoids the dependence of second-order score learning on first-order score estimates and the additional training and storage required by a separate second-order model.

原先学习 AFDM 有效信道先验的引导句保留。摘要的其他部分、引言第一和第三项贡献及背景段保持。出处沿用已核对的 Cai v2 §IV-A 式 (44)、§IV-C 式 (52)–(54)，Dytso 正式版 §III Proposition 1 式 (17)，Manor–Michaeli §3.2 式 (11)；完整含义与范围见 `docs/TERMINOLOGY.md` 和修订建议顶部。

英文摘要共 227 词。两版编译成功，无未定义引用、越栏或缺字；主稿 13 页，完整稿 15 页，均含 43 篇参考文献。因新增文字造成浮动体重排，将第六章七幅图的源码块提前到去噪性能小节之前，使两版最后一幅图均位于第 12 页结论之前；图块内容、顺序、图文件、正文实验分析及表格保持。完整稿的评估附录自第 13 页开始，参考文献占第 14–15 页。相关页面与全稿缩略图已检查。

`before/` 和 `BEFORE_HASHES.json` 保存改前稿；`SOURCE_DIFF.txt`、`VALIDATION.json` 保存改动和核验。数学公式、实验数据、算法、权重与 FINAL/MAINLINE 保持，未运行训练或实验。
