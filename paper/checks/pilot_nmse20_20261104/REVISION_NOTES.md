# 图 9 NMSE 下限调整

> 本轮历史图和绘图脚本已移入归档；当前生图入口见 [统一说明](../../../src/evaluation/plots/manuscript/README.md)。以下记录描述当时版本。

日期：2026-11-04。

作者查看上一版后要求将左图下限从 −15 dB 改为 −20 dB。当前 NMSE 纵轴为 −20～0 dB，主刻度为 −20、−15、−10、−5、0；右图 AER 仍为 10⁻⁴～10⁻¹。

图例 8 pt、坐标轴 8.5 pt、3.5 × 2.5 英寸画布、颜色、线型和标记沿用上一版。72 个曲线点完整保留，此前位于 −15 dB 下方的五个 NMSE 点现已显示。GP-MP 在 8 个导频帧处的 NMSE 和 AER 仍高于显示上限，按原值连线并由坐标边界裁切。没有修改实验数据、统计或正文，未开展训练或推断。

- 当前重绘入口：[render_pilot.py](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/pilot_nmse20_20261104/render_pilot.py)。
- 重绘与逐点核验：[RENDER_VALIDATION.json](RENDER_VALIDATION.json)。
- 修改前文件及哈希：`before/`、[BEFORE.json](BEFORE.json)。
- 成稿核验：[VALIDATION.json](VALIDATION.json)。
- 上一版 −15 dB 显示范围及 Ding 示例：[首次范围调整记录](../pilot_axis_limits_20261104/REVISION_NOTES.md)。

`main.pdf` 和 `main_full.pdf` 已同步编译；页数保持 13/15，图 9 所在页完成目视检查。
