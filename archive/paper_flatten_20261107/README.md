# 论文目录上移

按作者要求，仅保留原 C-STMP 稿件，内容直接放到 `paper/`。现在的入口为 `paper/main.tex`、`paper/main.pdf`，完整版本为 `paper/main_full.tex`、`paper/main_full.pdf`。

原 `paper/STMP` 的 71 个文件移入 `delete/paper_flatten_20261107/paper/STMP/`；原 C-STMP 的 4871 个文件完整搬移。空外层目录也在同一待删区，未永久删除文件。STMP 接收机代码和实验结果不受这次论文目录调整影响。

当前绘图路径、资产清单及文档导航同步更新；历史检查脚本与 JSON 记录保留原文，其旧路径通过 `MAPPING.json` 查找。`EDITS.json` 记录导航变更，原文件副本留在本地 `before/`。

验证：4942 个搬移文件逐项核对，正文与参考文献保持；两个主稿只更新编译目录注释，PDF 原字节保持。20 项 LaTeX 文件引用均可解析，10 幅论文图重绘逐像素一致，39 项发布检查通过。没有启动实验或训练，也未重新编译覆盖论文 PDF。
