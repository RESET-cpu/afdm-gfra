# 当前代码导读

根目录仅保留四个主要目录：代码 `src`、实验与数据 `result`、论文 `paper`、文献资料 `reference`。
运行入口是 [run_experiments.py](../../../run_experiments.py)，实验设置见 [实验说明](../../../src/evaluation/README.md)。

| 位置 | 内容 |
|---|---|
| `src/algorithm/proposed` | 固定十层深度展开；epoch 1 权重；内部相位初始化及9次层间更新 |
| `src/algorithm/STMP` | 三网络 STMP，暂不实验 |
| `src/algorithm/baseline` | SOMP、GAMP-SBL、GNN-ASPL、Off-grid SBL，每个算法一个文件 |
| `src/networks` | 共用网络结构；模型权重分别指定 |
| `src/evaluation` | 场景共享、接收机调用、评分、汇总与作图 |
| `src/evaluation/experiments` | 每个实验一个文件，方法列表由各自配置选择 |
| `src/evaluation/metrics.py` | 信道误差和活动检测的统一评分 |
| `src/system` | 物理场景、信道、导频和观测 |
| `src/system/scenario` | 物理场景和已知/未知相位观测生成 |
| `src/training` | STMP、GNN 的训练代码与共用训练工具 |
| `src/utils.py` | JSON 读写、文件哈希与记录 |
| `src/configs/algorithms.json` | 算法实现、构造参数与资源登记 |
| `src/configs/experiments` | 每个实验一个配置 |
| `src/configs/final` | 当前模型绑定和推断设置 |
| `src/tests` | 当前检查 |
| `result/main2000_message_gem_20261022` | 当前正式实验计划及后续结果 |
| `result/final2000` | 保留的旧计划、结果和暂停状态 |
| `src/history` | 保留原文的历史脚本和候选实验 |

执行流程：统一入口 → 实验计划 → 共享物理输入 → 按登记选择内部或公共相位估计 → 指定接收机 → 独立评分 → 汇总。
接收机只取得公开观测、导频与活动先验，真实信道用于评分。
路径整理后重新冻结当前执行计划；旧计划、预测和原 `MAINLINE.json` 不改写。
算法入口统一使用 `proposed`、`STMP`、`somp`、`gamp`、`gnn`、`offgrid_sbl`。
公共相位和噪声估计在 `system/receiver/`；proposed 接收原始导频时，使用自身的
`phase_initialization.py`、`phase_layers.py` 和 `phase_update.py`。
数值基准共用的读出和输入检查位于 `baseline/_common.py`。
算法由 `algorithm/registry.py` 构造；`evaluation/receivers.py` 只处理设备、计时与参数统计。
STMP 的推断设置只保存在 `src/configs/final/STMP.json`；`models.json` 引用该文件，
实验计划保存解析后的完整配置。训练配方 `src/configs/training/STMP.json` 职责不同，单独保留。
训练、评分、生成器已归位，不保留原 `experiment` 包的转发入口。
STMP 与高斯证据消融共用文件保存和停止判定，各自的证据计算保留在相应实现中。
结构与回放核验见 [本次整理记录](../../../result/source_cleanup_20261021/REPORT.md)。
