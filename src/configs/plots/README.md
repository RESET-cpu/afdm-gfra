# 绘图配置

当前 GP-MP-C 稿件的十幅图统一使用 [manuscript.json](manuscript.json)，由 [render_paper.py](../../evaluation/plots/render_paper.py) 读取。[命令与维护说明](../../evaluation/plots/manuscript/README.md)。

配置保存图号、当前数据来源及哈希、算法展示名、曲线样式、图例和面板参数。数据路径以仓库根目录为基准；更新实验结果时需要核对场景范围、配对条件和数据来源，再更新绑定。默认只输出论文使用的 PDF。

本目录其他 JSON 是通用工具及历史实验使用的配置，保留原协议，不应作为当前稿件的默认样式。冻结配置及运行中实验依赖不作覆盖。旧配置格式和用法见[历史说明](../../../archive/figure_cleanup_20261104/LEGACY_CONFIGURATION.md)。

当前图 6 为六算法已知相位、每档 1000 场景；图 5 为单场景收敛；图 7/8/9 分别为导频、设备数、活动概率；图 10 顺序为 A/B/C/D。多场景收敛、新相位及新 SBL 预算结果完成后，另行更新对应数据绑定。
