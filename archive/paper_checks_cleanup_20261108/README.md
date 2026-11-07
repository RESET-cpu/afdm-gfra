# 论文检查目录清理

2026-11-08，作者要求检查并清理 `paper/checks`。当前版本实际含 1,260 个已发布文件；本地连同未发布的备份、预览和编译产物共 4,733 个文件，468,066,530 字节。它们不是当前编译、绘图、训练或接收机入口的依赖。

整个目录已移至 `delete/paper_checks_cleanup_20261108/paper/checks/`，由作者手动删除。逐文件原哈希保存在同一待删目录的 `INVENTORY.json`。GitHub 当前版本移除该目录；已发布历史内容仍可在[清理前的固定版本](https://github.com/RESET-cpu/afdm-gfra/tree/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks)查阅。

245 处当前文档引用改为该固定版本链接。历史 JSON 身份和被冻结的写作快照不改写；其中旧路径按记录日期理解。术语说明中一条早已缺失的 `terminology_20261018_125231/TERM_AUDIT.md` 仅为原有历史路径，不计为本轮可用证据。

以下三份仍被审稿记录直接引用的数值证据单独保留，字节不变：

- [场景 372 敏感性汇总](evidence/scene372_sensitivity.json)：保留替换前后差异及未解决事项的依据。
- [分 SNR 活动检测汇总](evidence/activity_by_snr.csv)：保留既有审稿回应的汇总依据。
- `evidence/PAIRED_CASES.csv`：本地历史逐场景配对记录；继续按原发布范围排除，不随仓库发布。

其余未发布修订差异与摘录仍在待删副本内，相关文字明确指向本地路径。作者决定、术语结论、论文正文、PDF、正式图表、模型权重、冻结实现和正在运行的导频实验均保持。验证见 [VALIDATION.json](VALIDATION.json)，移动范围见 [REMOVAL.json](REMOVAL.json)。
