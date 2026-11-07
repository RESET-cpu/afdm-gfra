# STMP：三网络论文稿

[论文源码](main.tex) · [阅读稿](main.pdf) · [中文引言](sections/01_introduction_zh.md) · [研究文档](docs/README.md)

本目录包含本稿的全部现有正文、图片、参考文献与研究依据，可直接从本目录编译 `main.tex`，无需其他稿件目录。

| 内容 | 位置 |
|---|---|
| 编译入口与阅读稿 | `main.tex`、`main.pdf` |
| 各章、中文引言与附录 | `sections/` |
| 论文图片 | [figures/](figures/README.md) |
| 本稿参考文献 | [references.bib](references.bib) |
| 系统模型、推导、训练和术语 | [docs/](docs/README.md) |
| 图片及实验章节接收记录 | `imports/` |
| 原始复制凭据 | `COPY_MANIFEST.json`、`SOURCE_README.md` |

本稿对应一阶、二阶及活动分类器三网络。当前 `main.tex` 编入第 I–V 章及二阶训练附录；第 VI 章已接收去噪实验内容，但尚未启用，第 VII 章仍为占位。此次只整理目录，正文和阅读 PDF 没有改动。

`figures/denoising.pdf` 是本稿已接收的实际图片文件；8 个指向已清理旧图的失效目录链接已归档。图像来源和历史实验范围见 [imports/mac_experiments_20261023/IMPORT.json](imports/mac_experiments_20261023/IMPORT.json)。实验数据和后续图仍由 [result/](../../result/README.md) 管理。

在本目录使用包含 IEEEtran 的 LaTeX 环境编译，例如 `latexmk -pdf main.tex`。阅读稿固定为 `main.pdf`。

原名 `TWC-1`，更早为 `DCN`。旧顶层来源稿、历次改名记录和本次整理前说明均保存在[历史归档](../../archive/paper_layout_20261026/README.md)，原有内容未删除。共享文献原文仍在 [reference/](../../reference/README.md)。
