# 论文

日常阅读打开 [main.pdf](main.pdf)，修改正文进入 [sections](sections)。摘要、作者和全局排版在 [main.tex](main.tex)。当前研究方法为 GP-MP，估计相位版本为 GP-MP-EP。

| 文件 | 用途 |
|---|---|
| [main.pdf](main.pdf) / [main.tex](main.tex) | 主稿 |
| [sections](sections) / [references.bib](references.bib) | 正文分节与参考文献 |
| [figures](figures/README.md) | 三幅方法图、七幅实验图 |
| [docs](docs/README.md) | 复现说明、术语依据、审稿决定和写作规范 |
| [历史检查与备份](../archive/paper_cleanup_20261114/README.md) | 历次修改、检查截图、旧图和整理映射 |

当前论文统一使用 `main.tex`，编译输出 `main.pdf`。`figures/` 保留正文实际引用的十张 PDF 图；`docs/` 用于研究核查。

`sections/` 中保留两份附录源文件；默认主稿不编入附录。中文摘要草稿为 [00_abstract_zh.md](sections/00_abstract_zh.md)。

## 编译

在安装 IEEEtran 的 LaTeX 环境中，进入本目录运行：

```text
latexmk -pdf main.tex
```

本机也可使用 `tectonic --keep-logs --keep-intermediates main.tex`。编译会重新生成日志和辅助文件。

图 3 的公式引用由 `main.aux` 提供。若修改公式编号，应先编译主稿，再按[绘图说明](../src/plotting/README.md)更新相关图并重新编译。

`main.aux` 保留为图 3 的公式编号依赖，`main.bbl` 保留为生成的参考文献列表。

当前图源和采用状态集中在[逐图复现说明](docs/REPRODUCTION.md)维护。历次研究决定见[审稿记录](docs/REVIEW_DECISIONS.md)，实验进度见[实验索引](../result/README.md)。
