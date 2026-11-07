# 2026-10-26 论文目录整理

按用户要求，`paper/` 顶层只保留 `STMP/`、`C-STMP/`、`DU/`。各稿件分别保存现有正文、唯一阅读 PDF、章节、图片、参考文献和研究文档。

- [STMP](../../paper/STMP/README.md)
- [C-STMP](../../paper/C-STMP/README.md)
- [DU](../../paper/DU/README.md)

本次是文件组织调整，未补写未完成章节，未改变算法、模型配置、权重或实验结果，也未启动训练或推断。各稿件已有的修订记录、来源核验和历史候选继续保留在原稿件目录中。

## 原件和映射

| 内容 | 归档位置 |
|---|---|
| 原 `paper/main.tex`、`main.pdf`、`sections/`、`references.bib`、`figures/` | [original_paper/](original_paper/) |
| 原集中研究文档及其历史记录 | [original_paper/docs/](original_paper/docs/) |
| 旧三稿总入口及改名记录 | `original_paper/README.md`、[RENAME_20261026.json](original_paper/RENAME_20261026.json) |
| 本次修改前的导航说明 | [before_navigation/](before_navigation/) |
| 8 个已失效的历史图片目录链接 | `obsolete_figure_links/`，目标地址记录在 [BEFORE.json](BEFORE.json) |
| 旧路径、保留原件和当前文档副本的对应关系 | [MAPPING.json](MAPPING.json) |

原件保持原字节，包括旧描述、旧路径、正负结果和冻结凭据。归档中的相对链接仍是原布局下的历史写法；查找当前位置时使用映射。8 个目录链接在整理前均已失效，本次仅移动链接本身，不沿链接操作结果目录。

`paper/<方法>/docs/` 按方法分配研究文档，共用定义、基线说明和术语依据各保留实际文件副本；只更新其中的导航链接，不改写研究内容。后续方法专属内容在对应稿件维护，共用定义变化时同步相关稿件。现有论文编译只依赖各稿件自身的文件，以及 LaTeX 环境提供的标准类、宏包和字体。

## 核验范围

[BEFORE.json](BEFORE.json) 保存整理前全部论文文件及源码、配置和模型绑定的 SHA-256；[VERIFY.json](VERIFY.json) 逐项检查保留文件和受保护资产；[MANUSCRIPT_CHECK.json](MANUSCRIPT_CHECK.json) 检查三稿的编译输入、图片、引用和编译结果。

原冻结代码与元数据保留旧文档路径，不批量改写历史脚本。原 `docs/...` 路径可先按 [2026-10-21 映射](../../result/layout_20261021/MAPPING.json) 转为原 `paper/docs/...`，再使用本次 [MAPPING.json](MAPPING.json) 查找。历史 `paper/DU/checks/validate_manuscript.py` 的旧复制一致性检查仍针对当时来源版本，不作为当前稿件编译检查入口。

本次没有新增完整论文 PDF 备份；`original_paper/main.pdf` 是从原顶层移动的既有旧稿，三份现行阅读稿仍分别为各目录下唯一的 `main.pdf`。
