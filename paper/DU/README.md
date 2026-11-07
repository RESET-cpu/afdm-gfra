# DU：十层深度展开论文稿

[论文源码](main.tex) · [阅读稿](main.pdf) · [中文摘要](sections/00_abstract_zh.md) · [中文引言](sections/01_introduction_zh.md) · [研究文档](docs/README.md)

本目录包含本稿的全部现有正文、图片、参考文献与研究依据，可直接从本目录编译 `main.tex`，无需其他稿件目录。

| 内容 | 位置 |
|---|---|
| 编译入口与唯一阅读稿 | `main.tex`、`main.pdf` |
| 各章、中英文材料与附录 | `sections/` |
| 后验因子图源文件 | `figures/posterior_factor_graph.tex` |
| 本稿参考文献 | [references.bib](references.bib) |
| 十层推导、训练协议和术语 | [docs/](docs/README.md) |
| 修改依据、校验和历史候选 | `checks/`、`history/`、`revisions/` |

本稿对应十层展开接收机。当前阅读稿编入摘要、第 I–V 章、相位与噪声估计附录及参考文献；第 VI、VII 章尚未完成且未启用。本次未补写实验结论，正文和阅读 PDF 保持原样。

训练依据见 [第三版训练协议](docs/LSTMP_TRAINING_PROTOCOL_20261020_V3.md)、[第二版目标与梯度定义](docs/LSTMP_TRAINING_PROTOCOL_20261020_V2.md)及[完整推导](docs/LSTMP_DERIVATION_AND_TRAINING_20261020.md)。模型绑定仍以根目录 [FINAL.json](../../FINAL.json) 和实验保存的配置为准。

在本目录使用包含 IEEEtran 的 LaTeX 环境编译，例如 `latexmk -pdf main.tex`。阅读稿固定为 `main.pdf`；不另存日期或版本 PDF，也不保留检查目录中的完整论文 PDF 副本。

原名 `TWC-2`，更早为 `TWC`。`checks/` 中的历史程序和凭据保留当时内容；其旧论文路径可通过[本次迁移映射](../../archive/paper_layout_20261026/MAPPING.json)查找。整理前完整说明见[历史归档](../../archive/paper_layout_20261026/README.md)，共享文献原文仍在 [reference/](../../reference/README.md)。
