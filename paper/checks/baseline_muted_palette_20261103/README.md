# 基线配色改为相近暗色系

2026-11-03，作者提供参考图并要求突出红色 GP 方法族和蓝色 Off-grid SBL，另外三个基线使用相近、较暗的颜色。本轮替代此前的高饱和紫、橙、绿方案。

| 方法 | 颜色 | 色值 |
|---|---|---|
| GP-MP、GP-MP-CCD、GP-MP-CCD-EP | 原红色 | `#b83253` |
| Off-grid SBL | 原蓝色 | `#2878b5` |
| GNN-ASPL | 暗青灰 | `#356d73` |
| GAMP-SBL | 灰绿 | `#54776a` |
| SOMP | 深绿 | `#2c5645` |

三个次要基线依靠原有标记及线型继续区分。GP-MP、GP-MP-CCD、GP-MP-CCD-EP 的虚线圆点、实线方块、虚线三角保持；Off-grid SBL 的蓝色虚线方块保持。

更新用户数、活动概率、跨信道、导频帧数和 SNR 五幅图。收敛图、独立去噪图和三幅方法图保持。505 个绘图点以及除上述三个颜色外的全部曲线设置与上一轮逐项一致，见 `COLOR_VALIDATION.json`。未启动推断或训练。

`render_five_figures.py` 与 `render_snr.py` 为当前绘图入口，仍读取相同的已保存实验数据。修改前稿件和图文件位于 `before/`；当前配色记录在 `PALETTE.json`。最终编译与排版检查见 `VALIDATION.json`，预览位于 `previews/`。
