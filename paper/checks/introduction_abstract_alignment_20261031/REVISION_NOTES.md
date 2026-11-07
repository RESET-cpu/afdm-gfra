# 引言与摘要对齐（2026-10-31）

作者要求落实对照意见的前四点及第六点，明确保留第五点涉及的 AFDM/OTFS 优势论述。

## 修改

1. 贡献第 3 点将 soft activity probabilities 改为 posterior probabilities of activity。
2. 贡献第 2 点补明不施加 sparse or grid-aligned channel assumptions。
3. 贡献第 2 点将训练噪声具体写为 colored Gaussian noise with different covariance matrices。
4. 贡献第 3 点先介绍 MFLE 与 GPJD 及其功能，再说明学习密度比、活动后验概率、信道后验矩和活动不确定性之间的关系，最后说明两模块交换 Gaussian extrinsic messages。
5. 失配动机从 can exacerbate the mismatch 改为 may cause a mismatch，denoiser-input errors 和 white Gaussian noise used for training 与摘要用词统一。

术语与适用边界追加于 `../../docs/TERMINOLOGY.md`。AFDM/OTFS 优势段、摘要、贡献第 1 点、仿真结论与章节安排均保持原文。

## 核验

- 与 `before/` 快照对照，引言仅三个段落改变：失配动机、贡献第 2 点、贡献第 3 点。其余段落逐字一致；详细差异见 `INTRODUCTION.diff`。
- `main.tex` 与快照逐字节一致，确认已定稿摘要没有改动。
- Tectonic 0.17.0 以 `--only-cached --keep-logs main.tex` 编译成功，唯一阅读稿 `main.pdf` 仍为 13 页。
- PDF 文本确认失配用词、有色训练细节及两个模块的介绍已更新。
- 第 1、2、3、13 页渲染并目视检查通过，未发现裁切、重叠或异常分页；引言及系统模型衔接正常。
- 日志无 overfull、未定义引用或缺失字符；存在 10 处 underfull 提示。
- MFLE、GPJD 的英文全称与摘要及正文已有定义一致；MMSE 在引言此前已展开。
- 未运行训练或实验，未修改算法或技术定义。
