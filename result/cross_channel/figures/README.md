# 跨信道四 baseline 图片已完成

[当前四类信道 NMSE/AER 图](baselines_selected_readout_20261027/README.md)：每条件1000MC，96000条结果，24000复用/72000新算；数据与正式汇总逐项一致。门限开发场景重叠，属于回顾性迁移评估。

## 历史说明（原文保留）

# 跨信道图片

独立绘图入口：`src/evaluation/plots/cross_channel.py`。
新图保存到本目录的独立版本文件夹，读取相邻 data/ 内的已审核结果。

尚未生成本轮正式论文图；本次只建立目录，未计算实验或生成模拟曲线。


`history/` 与 `mac_original/` 仅收录原有图片的逐字节副本，不代表采用新版式。
图片应与对应 PLAN.json、SUMMARY.json 及来源记录一起引用。
