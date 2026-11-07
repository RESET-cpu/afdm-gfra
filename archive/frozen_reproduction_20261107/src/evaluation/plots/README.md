# 绘图入口

当前 GP-MP-C 稿件的十幅图统一由 [render_paper.py](render_paper.py) 生成，配置为 [manuscript.json](../../configs/plots/manuscript.json)。[完整使用说明](manuscript/README.md)。

在仓库根目录运行：

```powershell
& .\.venv\Scripts\python.exe -B src/evaluation/plots/render_paper.py --list
& .\.venv\Scripts\python.exe -B src/evaluation/plots/render_paper.py
& .\.venv\Scripts\python.exe -B src/evaluation/plots/render_paper.py --check
```

默认生成 `paper/C-STMP/figures/` 内十个 PDF，重复运行可覆盖同名生成文件。`--figures` 选择单图，`--output` 指定输出目录，`--formats pdf svg png` 可按需导出其他格式。`--check` 临时重绘并与现稿逐像素比较，自动清除临时图，不改正文或正式图。

绘图只读取保存数据，不运行实验或训练。代码不再依赖 `paper/C-STMP/checks/` 内的修订脚本；旧图、旧绘图脚本及预览已[归档](../../../archive/figure_cleanup_20261104/README.md)。

## 仍保留的通用和冻结工具

`snr_comparison.py`、`pilot_frames.py` 等通用工具用于显式指定输入的自定义绘图和其他稿件；其默认配置保留原有实验协议，不代表当前 GP-MP-C 稿件。`style.py`、`configurable.py` 等是仍在使用的共享绘图基础代码，保留以支持新入口和既有实验。`user_count.py` 指向的 `frozen_user_count_20261026` 保持冻结，不随此次整理修改。

通用参数说明见[归档说明](../../../archive/figure_cleanup_20261104/LEGACY_CONFIGURATION.md)，旧入口说明见[历史工具说明](../../../archive/figure_cleanup_20261104/LEGACY_PLOTTING.md)。当前稿件请始终从上面的统一入口生成。
