# AER 范围调整：跨章节只读终审

日期：2026-10-30。此次仅审查，不修改正式正文。

## 审查范围

读取 `main.tex` 的实际输入列表、内嵌英文摘要、引言与未启用的结论文件；搜索全部 `sections/*.tex` 中的 AER、活动错误、四幅被调整图的标签与文件名、实验性能概括、上下排/面板描述及相关小节引用。进一步核对正式启用的第二至第五章和两个附录的仿真配置引用。

`main.tex` 启用的正文为第一至第六章，附录为参数估计与 AFDM 信道模型；结论输入被注释。第二阶训练附录未启用。当前没有独立 `00_abstract.tex`，英文摘要直接在 `main.tex` 中。

## 发现并已同步：一处关联总述

位置：`sections/01_introduction.tex` 第 117–119 行，贡献 3 的结尾：

> Simulation results demonstrate that the proposed receiver improves activity detection and channel estimation performance compared with STMP across different signal-to-noise ratios and device activity levels.

原因：这句把活动检测和信道估计的双指标改善同时关联到 SNR 与活动程度；当前决定将活动概率组改为仅展示 NMSE，因而应把双指标总述对应到保留 AER 的 SNR 和导频组。

最小建议：只将 `device activity levels` 替换为 `pilot-frame counts`，其他文字不变。此处是由本轮展示范围改变直接引出的同步，并非额外重写引言。根代理已按该最小建议完成同步；本代理再次读取正式引言并核实已改为 `signal-to-noise ratios and pilot-frame counts.`，旧说法已不存在。原文备份由根代理保存在 `before/01_introduction.tex`。

## 无需修改的范围

- `main.tex` 摘要的一般性检测与估计性能总述仍由 SNR/导频双指标实验支持；不依赖被撤下的四组 AER，不需改动。
- 四幅图的引用均在第六章对应小节内；其他正式章节未发现对其 AER、联合改善或上下排位置的描述。
- 第六章修订稿已经保留原图文件名和全部标签，因此没有删去图对象或悬空引用；跨信道只改为单排图注。
- 第二至第五章与附录中的活动概率、活动阈值、活动稳定性停止条件是算法定义，不能因 AER 展示精简而删除；它们不构成遗漏。
- 第二章、第四章和第五章指向仿真设置的引用对应的配置段落未修改，无需同步。
- 未启用的结论仅有待写占位文字，无实验性能依赖。

上述引言一处已完成同步，除此之外无需扩大文字修改范围。未再检索文献，未改任何正式文件。
