# 第一项贡献修订（2026-11-01）

作者确认保留“连续帧共同对应一组有效信道，因此可增加针对这些信道的观测”的关系，要求再次修改。此次仅修改引言第一项贡献。最初按 Shen 的两句结构适配；作者随后确认三句表述，要求保留原意调整措辞并删除 symbol-level，当前采用该最终版本。

## 改后正文

> We propose a multi-frame AFDM transmission scheme that accommodates large differential delays and Doppler shifts at the satellite receiver. The scheme exploits the quasi-static properties of the effective channel over consecutive frames to obtain additional observations for JADCE. We further analyze the input--output relationship of the proposed scheme in detail.

## 原句与技术对应

- 母本：`reference/literature/shen2025.pdf`，PDF p.2，引言第一项贡献两句。第一句依次提出传输方案、目标、所利用的信道性质；第二句分析符号级输入输出关系。
- 初次改写的必要适配（后续措辞见本记录末尾）：`spreading-based multi-frame OTFS` 改为本文多帧 AFDM；大差分时延、多普勒由卫星端处理沿用本文原引言；时延–多普勒域准静态性质改写为本文每个设备的有效信道在连续帧内近似不变。
- Shen 的辅助依据：§II-B pp.4–5 在有效信道近似跨帧不变后解释增加观测，§II-C p.5 式(15)后给出欠采样比 Q/(UM)。
- 本文对应：第二章式(9)中 H_k^(q)=exp(jq beta_k)H_k，相位单独计入 A，近似不变对象为 H_k；Y=A X+W 中 A 为 Q×KN，因此欠采样比为 Q/(KN)。保持 K、N 和既有跨帧假设时，增加 Q 增加观测行数，不增加 X 的维度。
- 不将本文模型当作 Shen 原式，不把任意帧数下的近似不变或性能单调改善写成结论。分数时延、多普勒、CPP 和 MMV 的详细建模从第一项贡献删去，在既有正文中保留。

## 核验

- 引言第一项贡献之外的文字逐字一致，包括第二、第三项贡献；未落实此前未最终确认的其他讨论稿。
- 基线所登记的其余 20 份源码、参考文献或图片保持 SHA-256 一致；公式、模型与算法未变。
- Tectonic 缓存编译成功，阅读稿仍为 13 页，无未定义引用或溢出版面。其他章节和参考文献已有的 underfull 警告保留。
- 渲染检查第2、3页：贡献段及系统模型衔接无重叠或裁切。
- 前后差异见 `CHANGES.diff`，核验见 `VALIDATION.json`，原稿见 `before/`。术语及适配依据同步写入 `docs/TERMINOLOGY.md`。

## 同日措辞修正

作者指出 `exploiting the fact that` 生硬。已删去这一绕行从句，直接沿用 Shen 引言 `by exploiting the quasi-static properties of the channel` 的表达框架，将技术对象适配为本文跨连续帧的有效信道。准静态对象仍为 H_k，未改变相位关系或模型假设。

## 最终确认的三句版本

作者确认使用 `that accommodates ...`、`The scheme exploits ... to obtain additional observations for JADCE` 和 `We further analyze ... in detail`，删除 `symbol-level`。已将整项贡献同步为这三句，而非仅从旧稿删除一个限定词。`increase the undersampling ratio` 和 `Subsequently, we conduct ...` 同步退出当前贡献表述。修改前版本保存在 `before_final/`，本次差异另见 `FINAL_CHANGES.diff`。

术语账本已同步当前措辞及具体出处；本文原有跨帧相位和有效信道定义保持。最终编译和版面检查结果见 `VALIDATION.json`、`VISUAL_REVIEW.json`。
