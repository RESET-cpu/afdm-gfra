# 论文

日常阅读打开 [main.pdf](main.pdf)，修改正文进入 [sections](sections)。摘要、作者和全局排版在 [main.tex](main.tex)。当前研究方法为 GP-MP，估计相位版本为 GP-MP-EP。

| 文件 | 用途 |
|---|---|
| [main.pdf](main.pdf) / [main.tex](main.tex) | 主稿 |
| [sections](sections) / [references.bib](references.bib) | 正文分节与参考文献 |
| [figures](figures/README.md) | 三幅方法图、七幅实验图 |
| [docs](docs/README.md) | 复现说明、术语依据、审稿决定和写作规范 |

当前论文统一使用 `main.tex`，编译输出 `main.pdf`。`figures/` 保留正文实际引用的十张 PDF 图；`docs/` 用于研究核查。

## 编译

在安装 IEEEtran 的 LaTeX 环境中，进入本目录运行：

```text
latexmk -pdf main.tex
```

图 3 的公式引用由 `main.aux` 提供。若修改公式编号，应先编译主稿，再按[绘图说明](../src/plotting/README.md)更新相关图并重新编译。

当前图源及尚未完成的替换集中在[逐图复现说明](docs/REPRODUCTION.md)维护。工作稿中的历史曲线按其实际来源保留；完成一项实验并通过核验后再采用。历次研究决定见[审稿记录](docs/REVIEW_DECISIONS.md)，日常进度见[实验索引](../result/README.md)。
