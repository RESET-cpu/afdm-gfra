# reference 目录整理（2026-10-26）

当前入口：[参考资料](../../reference/README.md)、[论文库](../../reference/literature/README.md)、[专题索引](../../reference/reviews/README.md)。

- 顶层保留 `literature/`、`reviews/`、`writing_profile/` 与导航 README。
- 9 个旧调研目录及 `literature/section_structure_20261009/` 归入 `reviews/`。
- 57 份 PDF 按 SHA-256 合并为 50 份；7 个冗余副本的内容均能从保留文件恢复。同题不同版本不合并。
- Markdown 导航和当前研究说明中的路径同步更新；历史 JSON、原代码、文本、截图及诊断数据保持原字节。修改过的说明原件保存在 [before_documents.zip](before_documents.zip)。
- 原下载/诊断脚本为历史记录，依赖当时布局及模型环境；此次不执行或改写。复现时可按映射在独立目录恢复旧结构，不能把原核验记录当作对整理后 Markdown 字节的核验。

## 记录

- [BEFORE.json](BEFORE.json)：整理前 277 份文件的大小与哈希、保护文件及已有失效链接。
- [MAPPING.json](MAPPING.json)：每个旧文件到现文件的精确映射，另附目录映射。文件映射优先于目录映射。
- [FILE_ACTIONS.json](FILE_ACTIONS.json)：移动及完全相同 PDF 的去重清单。
- [DOCUMENT_EDITS.json](DOCUMENT_EDITS.json)：本次文档变更及原件哈希。
- [VERIFY.json](VERIFY.json)：原文件去向、内容保持、保护文件与链接核验结果。

旧记录中的 `D:\afdm-gfra\reference\...` 或其他机器绝对路径，应先取 `reference/` 开始的仓库相对路径，再查 `MAPPING.json`；`paper/literature/` 和 `paper/writing_profile/` 先使用 `legacy_aliases` 转换。原文档字节如已因路径更新变化，可从备份 ZIP 按旧路径提取。

只读复核（在项目根目录运行）：

```powershell
& .\.venv\Scripts\python.exe -B archive/reference_layout_20261026/organize.py verify
```

复核不启动下载、训练或推断。已有失效链接单独记录；本次迁移要求所有原本有效的链接继续有效，并检查新增导航。
