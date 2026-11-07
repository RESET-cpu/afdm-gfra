# 代码导读

在仓库根目录运行 `python run_experiments.py ...`。环境准备和最小示例见[运行指南](../REPRODUCING.md)。

| 目录 | 职责 | 主要入口 |
|---|---|---|
| [scenario](scenario/README.md) | 几何、设备活动、路径和配对场景 | `generate.py`、`profiles.py` |
| [waveform](waveform/README.md) | AFDM 波形、路径算子和导频 | `afdm/continuous.py`、`pilot.py` |
| [channel](channel/README.md) | 阵列、有效信道和观测结构 | `config.py`、`observation.py` |
| [receiver](receiver/README.md) | GP-MP、STMP、基线及相位前端 | `registry.py`、`gp_mp/receiver.py` |
| [experiment](experiment/README.md) | 计划、接收机调用、保存、评分、汇总 | `suite.py`、`experiments/` |
| [plotting](plotting/README.md) | 从保存结果生成图表 | `render_paper.py`、`manuscript/` |
| [networks](networks/README.md) | 共用网络定义和加载 | `score.py` |
| [training](training/README.md) | 采样、训练目标和优化 | `cli.py`、`gp_mp/`、`stmp/` |
| [configs](configs/README.md) | 方法登记、参数、权重和绘图来源 | `organized/algorithms.json` |
| [tests](tests/README.md) | 数学、接口、资产和回归检查 | `public/` |

场景、波形和信道模块产生观测；接收机完成推断；实验层持有真值并独立评分；绘图层读取保存的汇总。`workspace.py` 和 `fileio.py` 负责路径、文件读写与哈希。

## 模型和执行版本

- [FINAL.json](../FINAL.json)：冻结的 GP-MP 模型身份；其中旧源码路径用于核验历史记录。当前实现为 `receiver/gp_mp/`，当前方法登记为 `configs/organized/algorithms.json`。
- [算法登记](configs/organized/algorithms.json)：方法名称、工厂、数值配置和资源。
- [STMP 模型登记](configs/organized/models.json)：STMP 配置和共享相位配置。
- [实验配置](configs/experiments)：新实验的方法、场景数和扫描条件。

`experiment/studies/` 保存特定研究批次的执行流程。正在进行的导频批次使用清理前的独立执行副本，原计划、权重和源码身份保持不变；说明见[本轮修改与验证](../archive/code_fixes_20261107/README.md)。其他冻结批次按[冻结归档说明](../archive/frozen_reproduction_20261107/README.md)执行。
