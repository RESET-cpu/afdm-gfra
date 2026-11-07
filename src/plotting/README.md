# 绘图

绘图只读已保存的汇总和素材，不运行接收机、生成正式场景或训练网络。全部导入采用包路径，可直接作为模块运行，不再依赖把绘图目录加入搜索路径。

```text
python run_experiments.py plot --list
python run_experiments.py plot --check
python run_experiments.py plot --figures snr_comparison --output result/tmp/figure_preview
```

- `render_paper.py`：当前十幅论文图的统一入口、来源核验和比较。
- `manuscript/`：三幅方法图与七幅实验图的绘制。
- `configurable.py`、`data.py`、`plot_selection.py`：配置、汇总读取与选择。
- `style.py`、`legend_layout.py`：样式和图例。
- `summary.py`：通用实验的诊断图，从实验报告代码中拆出。

配置仍是 `src/configs/plots/manuscript.json`。`--check` 在临时目录重绘；不带 `--check` 且不指定 `--output` 会替换论文图，应只在明确采用新结果时使用。

需要 Matplotlib、NumPy、PyMuPDF 和现有 Times New Roman 字体。通过根目录 `requirements.txt` 安装这些依赖。方法图还依赖配置中登记的文献素材、编译标签及本地信道示例；仅下载排除原始数据的 GitHub 快照不能完整重绘该示例。
