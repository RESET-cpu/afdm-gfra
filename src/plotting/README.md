# 绘图

绘图读取保存的汇总和素材。入口、来源与状态见[逐图复现说明](../../paper/docs/REPRODUCTION.md)。

```text
python run_experiments.py plot --list
python run_experiments.py plot --figures snr_comparison --output result/snr_figure_preview
python run_experiments.py plot --check
```

指定 `--output` 可预览；`--check` 在临时目录重绘并比较。未指定这两个选项时会写入正式论文图目录，仅在采用新结果时使用。

- `render_paper.py`：十幅论文图的入口与来源校验。
- `manuscript/`：方法图和实验图。
- `configurable.py`、`data.py`、`plot_selection.py`：配置和数据选择。
- `style.py`、`legend_layout.py`：样式、图例。
- `summary.py`：通用实验的诊断图。

[manuscript.json](../configs/plots/manuscript.json) 保存当前图源。依赖为 NumPy、Matplotlib、PyMuPDF 和 Times New Roman 字体。系统图和接收机图分别核验各自的文献素材、编译标签或本地信道示例；这些素材并未全部发布。因子图可独立绘制，不依赖上述额外素材。

正式论文图只保留 PDF；需要其他格式时加上 `--formats pdf png svg --output result/figure_preview`。图 3 的公式标签读取 `paper/build/main.aux`，编译步骤见[论文说明](../../paper/README.md)。
