# 旧绘图代码和重复图清理记录（2026-11-04）

作者授权统一当前论文的绘图代码，并清理多余代码和图片。现行入口为 [render_paper.py](../../src/evaluation/plots/render_paper.py)，用法见[统一绘图说明](../../src/evaluation/plots/manuscript/README.md)。

清理对象为当前稿件修订目录中的历史图、页面预览、旧图压缩包、被替代的绘图脚本和缓存，以及成图目录中可按需重建的 PNG/SVG 副本。当前十幅论文 PDF、两版论文、原始数据、统计、研究决定和核验记录保留。`result/`、冻结代码与后台运行实验的依赖不在此次清理范围内。

归档移动前已完成十图独立重绘及逐像素比较。历史文件保存在 [superseded_figures.zip](superseded_figures.zip)，路径、文件哈希和对应压缩包成员见 [MANIFEST.json](MANIFEST.json)。相同内容仅存一份，`archive_member` 指向实际成员；恢复时按 `path` 放回原位置，文件内容应匹配 `sha256`。压缩包已做 CRC 和逐内容哈希验证。

部分历史文档中指向已清理图片或脚本的链接转到本页。原始相对路径可通过清单查找；历史轮次的“当前入口”“最新版”等说法仅描述当时状态，不能覆盖上面的统一入口。修订前导航说明保存在压缩包的 `navigation_before/` 中。

[归并和核验结果](../../paper/C-STMP/checks/figure_consolidation_20261104/README.md)。

实际采用可恢复移动，2055 个旧文件保存在 `retired_files/` 下，维持原相对目录；压缩副本也保留。工作目录已清理，此次没有释放磁盘空间。批量删除曾被自动审批以 `blocked by policy` 拦截，未继续尝试删除。
