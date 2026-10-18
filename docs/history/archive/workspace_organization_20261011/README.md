# 工作区整理与保存范围

本轮整理保留已有研究文件和结果，统一当前阅读入口。

- [before/](before/) 保存修改前 379 个文本、源码与配置文件；逐文件 SHA 见 [SNAPSHOT.json](SNAPSHOT.json)。
- 顶层 23 个日期实验目录和专题旧文档已从当前工作入口移出，原文在 [before/experiments/](before/experiments/) 与 [before/docs/](before/docs/)。
- [assets/results/](assets/results/) 保存 105 个历史结果目录；旧权重、输出与临时研究材料分别位于 `assets/models/`、`assets/outputs/` 和 `assets/tmp/`。
- 结果与权重采用同一文件系统内的目录重命名，原路径保留符号链接。内部 2413 个既有链接在迁移后仍指向原文件对象。
- [MIGRATION.json](MIGRATION.json) 记录逐文件归档位置、目录移动和原路径；[organize.py](organize.py) 为已执行的一次性迁移脚本，不用于重复运行。

当前结果入口见 [results/README.md](../../results/README.md)，当前代码见 [CODE_GUIDE.md](../../docs/CODE_GUIDE.md)。
本轮数值、路径和保留范围核验见 [workspace_organization_20261011/](../../results/workspace_organization_20261011/)。

日期脚本与上一轮快照逐文件一致，依赖旧 API 的脚本通过 [匹配源码入口](../code_consolidation_20261011/README.md) 使用。
`before/` 中的大型共享资产通过链接访问原路径；它是可追溯的源码快照，而非独立的数据备份。
原冻结结果中的绝对路径继续通过项目原路径解析；完整项目迁到另一台机器仍需按原协议处理路径与外部数据依赖。
