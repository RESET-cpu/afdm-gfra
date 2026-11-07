# 第一项贡献修订记录（2026-11-02）

作者确认采用本轮最后给出的版本。本次只替换第一项贡献，未扩大修改到引言其他段落。

## 改后文本

We propose a multi-frame AFDM transmission scheme that accommodates large differential delays and Doppler shifts at the satellite receiver. The scheme reduces modulation complexity through one-dimensional chirp modulation and uses a lower-dimensional effective-channel representation. By exploiting the quasi-static properties of the effective channel over consecutive frames, the scheme provides additional observations for JADCE.

## 相对改前的变化

- 保留第一句方案目标。
- 第二句明确一维 chirp 调制降低调制复杂度，以及较低维度的有效信道表示。
- 原有跨帧准静态性质与增加观测的作用调整至第三句，采用作者确认的完整表述。
- 删除贡献中的详细分析输入输出关系一句；正文相应推导保持。

术语、比较对象和适用范围见 TERMINOLOGY.md 的 2026-11-02 条目。维度比较是本文与 Shen 既有模型的比较，不是新增数值实验结论，也不表示完整接收机运行时间降低。

## 验证

编译及版面检查结果另记于 VALIDATION.json。源文件差异见 CHANGES.diff；改前引言与用词记录保存在 before/。
