# 用户数实验固定绘图版本

按用户2026-10-26要求冻结，只允许更换已核验结果路径和新输出目录。
主实验执行脚本、参数、权重及旧结果不变；此脚本只读已完成的统计。

- 五方法及顺序：C-STMP、Off-grid SBL、GNN-ASPL、GAMP-SBL、SOMP。
- 用户数20/40/60/80的阻尼为0.4，100用户为0.2；每档使用固定前N场景。
- 双栏论文内单栏宽88.9 mm、高55.88 mm；Times New Roman，轴8.5 pt、图例6 pt。
- C-STMP红色空心圆实线；其余颜色、线型、标记与已确认图一致。
- NMSE/AER左右双子图，图例仅在AER中，按冻结的避让规则放置；100场景为左上角。
- 横轴20–100；纵轴按完整5 dB及十倍区间自动覆盖全部数据，不为图例扩轴。
- AER对数坐标；精确零值只在显示时贴最终纵轴下界，不另设零值栏或标注。
- PNG 600 dpi、PDF、SVG及180 dpi预览；原统计及PLOT_DATA中的零值保持为零。

`engine/`是独立源码副本，不导入公共绘图代码或配置；`FROZEN.json`绑定代码与配置的SHA256。
公共绘图代码后续修改不会改变本实验。更改本冻结版本须有新的用户指示，并另存版本。
数学统计与数据核验沿用原逻辑，不筛选有限未收敛结果。

默认读取当前500场景主批次的完成汇总；未完成时不会提前生成500场景图：

```powershell
.\.venv\Scripts\python.exe -B -X utf8 src/evaluation/plots/user_count.py
```

复绘前100场景到新目录：

```powershell
.\.venv\Scripts\python.exe -B -X utf8 src/evaluation/plots/user_count.py --input result/user_count/data/c_stmp_variance_em_500_k100beta02_20261026/interim100 --output result/user_count/figures/frozen_paper_interim100_20261026
```

不得覆盖旧图。`src/configs/plots/user_count.json`是历史公共配置参考，不再控制此入口；
实际固定配置为本目录的`CONFIG.json`。原运行结束时生成的旧样式图仍保留作为完成凭据；
对外展示使用本固定版本。
