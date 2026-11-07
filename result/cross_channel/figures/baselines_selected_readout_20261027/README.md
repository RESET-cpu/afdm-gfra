# 跨信道四 baseline 结果图（2026-10-27）

四类信道 D/A/B/C 各一张 NMSE/AER 双面板图，沿用当前统一论文样式。每个信道包含 SNR −4/−2/0/2/4/6 dB，每条件 1000 MC（场景 0–999），方法为 Off-grid SBL、GNN-ASPL、GAMP-SBL、SOMP。共 96 组、96000 条：D 复用 24000，A/B/C 新算 72000。

- [D 信道](D/cross_channel.png) · [PDF](D/cross_channel.pdf)
- [A 信道](A/cross_channel.png) · [PDF](A/cross_channel.pdf)
- [B 信道](B/cross_channel.png) · [PDF](B/cross_channel.pdf)
- [C 信道](C/cross_channel.png) · [PDF](C/cross_channel.pdf)
- [正式报告](../../data/known_phase_1000_baselines_20261025/selected_readout_20261025/REPORT.md)

全部图使用正式 selected_readout 汇总，未筛选场景、未平滑曲线、未调整门限。Off-grid SBL/SOMP 按接收机估计 SNR 查既有最近节点门限，GNN/GAMP 用既有固定门限；不按真实 SNR 查表。NMSE 沿用原始推断结果。四图的数据逐项等于正式汇总，图例布局已逐图查看；部分图例由现有自动布局拆成两组以避开曲线。

门限在场景 0–499 拟合、500–999 选择，本次评估复用 0–999，属于回顾性迁移评估，不能宣称独立测试。40 用户、16 帧、p=0.1，已知相位使用仿真真值、噪声由接收机估计；活动抽样条件为至少一人活跃，边际先验为 p/(1-(1-p)^40)。跨信道沿用固定几何下表列功率、时延和衰落剖面，不代表完整时变多普勒谱。并发耗时仅用于诊断。

原准备阶段绘图脚本保留不改。本次独立配置位于相邻 baselines_selected_readout_20261027_configs，调用 src/evaluation/plots/cross_channel.py；只读取已完成数据，生成 PNG/PDF/SVG 及配置、图例和来源记录，不运行推断、训练或校准。
