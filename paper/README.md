# 论文

当前稿件直接放在本目录，研究方法为 GP-MP，估计相位版本为 GP-MP-EP。

| 文件 | 用途 |
|---|---|
| [main.pdf](main.pdf) / [main.tex](main.tex) | 主稿 |
| [main_full.pdf](main_full.pdf) / [main_full.tex](main_full.tex) | 含评估协议附录的完整稿，与主稿共享正文 |
| [sections](sections) / [references.bib](references.bib) | 正文分节与参考文献 |
| [figures](figures/README.md) | 三幅方法图、七幅实验图 |
| [docs](docs/README.md) | 复现说明、术语依据、审稿决定和写作规范 |

## 编译

在安装 IEEEtran 的 LaTeX 环境中，进入本目录运行：

```text
latexmk -pdf main.tex
latexmk -pdf main_full.tex
```

图 3 的公式引用由 `main.aux` 提供。若修改公式编号，应先编译主稿，再按[绘图说明](../src/plotting/README.md)更新相关图并重新编译。

当前图源及尚未完成的替换集中在[逐图复现说明](docs/REPRODUCTION.md)维护。工作稿中的历史曲线按其实际来源保留；完成一项实验并通过核验后再采用。历次研究决定见[审稿记录](docs/REVIEW_DECISIONS.md)，日常进度见[实验索引](../result/README.md)。
