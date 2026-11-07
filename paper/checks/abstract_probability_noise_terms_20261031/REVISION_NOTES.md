# 摘要活动概率与训练噪声用词（2026-10-31）

作者要求修改 soft activity probabilities 和 white Gaussian training noise 两处表述。

- 前者改为 posterior probabilities of activity，依据 Cai v2 §III-B2、式 (30) 后的 posterior probability of activity，仅作复数变化；中文同步为“活动后验概率”。
- 后者改为 white Gaussian noise used for training，沿用 Shastri 等摘要及 §V 的 white Gaussian noise，用后置修饰说明训练用途；不把整个新搭配冒称为文献逐字原句。中文同步为“用于训练的白高斯噪声”。
- 原文链接、术语含义及适用边界见 `../../docs/TERMINOLOGY.md` 本轮条目。

## 核验

- 中英文源稿与 `before/` 快照相比均严格只有对应两处替换；英文差异见 `MANUSCRIPT.diff`。
- Tectonic 0.17.0 使用 `--only-cached --keep-logs main.tex` 编译成功，唯一阅读稿 main.pdf 为 13 页。
- PDF 文本确认已包含两个新表述；首页渲染并目视检查，无裁切、重叠或异常衔接。
- 日志无 overfull、未定义引用、重复标签或缺失字符；有 10 处 underfull 提示。
- 缩写检查为 partial、无报告错误；脚本未识别 MP/MFLE/GPJD/MMSE 的连字符全称，已人工核对其定义，缩写及全称与本轮前一致。详见 `ACRONYMS.json`。
- 核验记录见 `VERIFICATION.json`，本轮未运行训练或实验。
