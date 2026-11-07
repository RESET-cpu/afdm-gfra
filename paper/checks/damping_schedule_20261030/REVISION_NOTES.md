# 阻尼与方差系数更新集中至第五章

日期：2026-10-30。范围：作者在本轮对话中确认的第三至第五章职责划分调整。

## 改动

- 第 III 章删除 MFLE 末尾的阻尼及尺度系数说明，将 GPJD 外信息后的句子改为局部输出消息定义；保留后验残差能量目标 `eq:query-variance-target` 及其推导依据。
- 将尺度系数递推 `eq:query-variance-update` 移到 V-A。初始化与 `v = kappa * bar_v` 仍在 V-A，明确本轮保持输入方差不变、更新系数用于下一轮、两种更新沿用同一权重。
- V-A 补明线性消息按终端重排的含义。Algorithm 1 将不再连续的公式范围引用改为分别引用；当前 PDF 对应式 (30) 和 (41)。
- 第 IV 章逐字节保持不变。未调整算法数值规则、网络、参数、复杂度或实验结果，未重新生成摘要。

## 来源与范围

沿用现有正文的 Cai Sec. V-B1 阻尼依据，以及 Vila Sec. III-A 高斯方差更新依据；原文定位和适配边界已记录于 `../../docs/TERMINOLOGY.md` 及 `../chapters_3_5_revision_20261030/ch3/SOURCES.md`、`../chapters_3_5_revision_20261030/ch5/SOURCES.md`。本次未新增专业术语、公式假设或性能主张，也未改变共用物理定义。

## 核验

- 修改前源文件保存在 `before/`，文件摘要见 `BEFORE_HASHES.json`；本轮源文件差异见 `REVISION.diff`。
- 第 III、IV 章不含 damping、kappa 或 eta；三章原有公式与章节标签集合完整保留。
- Tectonic 编译成功，唯一阅读稿仍为 `../../main.pdf`，共 15 页。无未定义引用、重复标签、缺失字形或 overfull；有少量 underfull 排版提示。
- 已实际检查新 PDF 第 4–8 页，包括第 III 章末尾、第四章、第五章递推式与 Algorithm 1；未发现内容重叠、裁切或错误公式引用。
- 缩写脚本已执行，报告覆盖为 partial，并包含既有复合缩写的识别提示；见 `acronym_report.md`。不将此报告表述为全文缩写检查通过；本次改动没有新增缩写。
- 未运行训练、推断或批量实验。
