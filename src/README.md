# 日常研究代码

外部读者先看 [使用与复现](../REPRODUCING.md)，可运行 `demo` 和 `assets` 命令。
`experiment/demo.py` 是无需权重的单场景数值示例；`experiment/assets.py` 只检查资产，
不下载文件或启动推断。`configs/` 与源码一同提供。

从根目录运行 `python run_experiments.py ...`。场景、波形、信道、接收机、实验和绘图直接放在 `src` 下。已有冻结批次继续使用原始源码与原始配置。

## 按研究任务找代码

| 分区 | 负责什么 | 首先阅读 |
|---|---|---|
| [scenario](scenario/README.md) | 卫星几何、设备活动、物理路径、配对场景与 NTN-TDL 条件 | `scenario/generate.py`、`scenario/profiles.py` |
| [waveform](waveform/README.md) | AFDM 变换、连续时延多普勒路径算子、导频 | `waveform/afdm/continuous.py`、`waveform/pilot.py` |
| [channel](channel/README.md) | 物理参数、阵列、有效信道、观测噪声及输入结构 | `channel/config.py`、`channel/observation.py` |
| [receiver](receiver/README.md) | GP-MP、STMP、传统基准、相位与噪声估计 | `receiver/registry.py`、`receiver/gp_mp/receiver.py` |
| [experiment](experiment/README.md) | 条件扫描、计划、调用、保存、评分与汇总 | `experiment/suite.py`、`experiment/experiments/` |
| [plotting](plotting/README.md) | 从已保存结果生成论文图和检查图 | `plotting/render_paper.py`、`plotting/manuscript/` |
| `networks/` | 接收机和训练共用的网络定义、权重加载 | `networks/score.py` |
| [training](training/README.md) | 训练目标、优化、保存和训练入口导航 | `training/scores/`、`training/stmp/` |
| `workspace.py`、`fileio.py` | 路径、文件读写与哈希 | 不放算法或实验参数 |

场景与波形组成观测，接收机只接收公开输入；实验层调用各模块并单独持有真值进行评分，绘图层读取已保存汇总。场景、波形和信道模块不导入接收机推断、实验或绘图。`genie_bound` 等使用真值的研究对照继续明确标记。

## 配置与资产

- 当前工作代码登记：[`src/configs/organized/algorithms.json`](configs/organized/algorithms.json)。工厂和源码路径指向上述功能目录，数值配置与权重绑定保持原值。
- 科学参数：[`src/configs/experiments`](configs/experiments)、[`src/configs/final`](configs/final)、[`src/configs/candidates`](configs/candidates)。不在模块导读中另抄一套参数。
- 冻结模型身份：[`FINAL.json`](../FINAL.json)。本次整理不改它或 `MAINLINE.json`，原始绑定仍可核对。
- 新通用计划默认保存到 `result/organized_default_20261107/`；实验输出、论文、模型和原始数据各在已有目录中。

## 常用命令

```text
python run_experiments.py list
python run_experiments.py snr_comparison --help
python run_experiments.py plot --list
python run_experiments.py plot --check
python run_experiments.py white_followup inspect
```

`plot --check` 在临时目录重绘、比较，不覆盖正式图；图形依赖和字体见绘图说明。推断和训练需要另外显式执行，查询命令不会启动。

## 冻结实验与待删内容

旧 `algorithm`、`system`、`evaluation` 和原训练入口已移出 `src`。
保留实验需要的原始源码和配置在 [冻结归档](../archive/frozen_reproduction_20261107/README.md)，
原逻辑路径与哈希不变。独立 DU 及重复旧快照在 `delete/`，不参与运行和发布。

当前 `white_followup` 和 `convergence` 位于 `experiment/studies/`。
冻结计划的原始来源与当前实际执行源码分别核验和记录；原导频数失败现场未改动，也未续跑。
整理与数值对照记录见 [本次核验](../archive/code_cleanup_20261107/README.md)。
