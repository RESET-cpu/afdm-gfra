# 代码导读

主入口先在 `algorithm/phase_estimation_optimized.py` 估计跨帧相位，保留原两轮完整搜索。阅读条件 Proposed 时，先读 `proposed/iterations.py` 的 `run_spatial_score`，再顺着调用进入 `linear.py` 和 `denoiser.py`。
默认算法、配置与结果由 [MAINLINE.json](../MAINLINE.json) 记录。

日常批量实验从 [experiment/](../experiment/README.md) 的七个单文件入口运行，专用参数写在各文件顶部；共享默认值、权重与求解器创建在 `_support/settings.py`，文件与身份检查在 `_support/storage.py`，已有结果复用在 `_support/reuse.py`；`_common.py` 负责配对运行和汇总。算法实现仍在 `src/`。默认只执行 [7 个核心检查文件](../tests/README.md)。

## 一次运行

```text
run.py → experiment/run.py → algorithm/baselines/unknown_phase_baselines.py
  proposed → proposed_frontend_candidate.py → 相位估计 → proposed_noise_candidate.py → proposed/receiver.py
  baseline → 相位估计 → algorithm/baselines/baseline_noise.py → 噪声估计与条件推断
```

Proposed 与基线默认只需要 observation、pilot、activity_prior 三项，估计噪声模式忽略旧输入中的 noise_variance。`noise_estimation.load_unknown_noise_input` 将估计值装入内部四字段 `UnknownPhaseInput`；Proposed 的默认前端及条件噪声包装器同样只使用观测估噪，再调用原接收机。
相位估计后构造条件求解器使用的 `ReceiverInput`，将 pilot 替换为含估计相位的 operator。SOMP/GNN-ASPL 的协方差噪声前端在 `noise_estimation.py`，GAMP 的输出后验更新调用原核函数，SBL 的噪声更新在 `offgrid_noise.py`，L-DAMP 沿用原残差协方差。
显式 `--phase-mode known` 使用含已知相位的 operator；`--noise-mode known` 使用准确噪声。两项分别控制信息条件。
系统生成与事后评分放在算法目录之外；两种输入条件见 [实验协议](EXPERIMENT_PROTOCOL.md)。

## Proposed 的一轮迭代

| 顺序 | 实现 | 对应公式 |
|---|---|---|
| 初始化零均值和先验方差 | `iterations.run_spatial_score` | THEORY 第 6 节 |
| A：线性后验、外信息查询与阻尼 | `linear.SpatialLinear.update`、`iterations.moment_damp` | T3–T5 |
| B：一、二阶网络产生完整信道条件矩 | `moments.FullChannelMoments.infer` | T8–T12 |
| 更新活跃 Gaussian site | `denoiser.Denoiser.__call__` | T13 |
| 分类器产生当前查询的活动概率 | `activity.FrozenEvidence.infer`、`denoiser.py` | T15 |
| 合成信道均值与协方差 | `denoiser.py` | T16 |
| 外信息反馈与第二次阻尼 | `gaussian.gaussian_extrinsic`、`iterations.moment_damp` | T17 |
| 检查停止窗口、记录、进入下一轮 | `iterations._stopping_step` | THEORY 第 6 节 |

公式见 [THEORY.md](THEORY.md)。查询超出网络支持范围时，`posterior.full_posterior` 使用保留的 Gaussian site 计算 T14 和 T16。
`receiver.py` 负责权重加载、文件输入输出和运行记录；`iterations.py` 下方的辅助函数负责变化量、停止窗口和消息诊断。
`network.py` 与 `cai_models/` 保存 score 网络结构与许可证。

阅读顺序参照本地固定版本 [Cai 作者主程序](../references/known_phase_iteration_review_20260928/cai_official_main_stmp_jadce.py.txt) 的 module A / module B 顺序。
本项目有自己的活动分类器、协方差和停止规则，具体公式以上表为准。`run_spatial_score`、`SpatialConfig`、`full_score` 等名称保留为已有软件接口和记录字段。

## Baseline

Baseline 实体代码统一放在 [`algorithm/baselines/`](../src/afdm_jadcedd/algorithm/baselines/README.md)。
Off-grid SBL、L-DAMP 及基线相位／噪声接入统一使用 `afdm_jadcedd.algorithm.baselines` 包路径。
下表列的是当前源码位置。

当前正式比较为 500 个物理场景、七档 SNR，Proposed 与以下四方法均估计相位和噪声。完整报告见[结果索引](../docs/history/results/README.md)。

| 命令 | 核心文件 | 当前用途 |
|---|---|---|
| `somp` | `baselines/somp.py` | 500 场景比较 |
| `gamp` | `baselines/gamp_sbl_mmv.py` | 500 场景比较 |
| `gnn` | `baselines/gnn_aspl.py` | 500 场景比较；同一网络的 CPU/MPS 后端 |
| `offgrid_sbl` | `baselines/offgrid/sbl.py` | 500 场景比较及当前实验均最多 120 轮 |
| `ldamp` | `baselines/ldamp/` | 保留实现与权重，可选基线 |

`baselines/receiver.py` 统一接入和保存；`ding.py` 计算系数能量；`readout.py` 使用一份冻结规则。
求解器、参数和权重身份由 [baselines.json](../configs/baselines.json) 绑定。
GNN 源文件保持 checkpoint 所绑定的原始内容。
`baselines/offgrid/atoms.py` 定义连续原子、区间内导数和重建；SBL 主线由
`baselines/offgrid/receiver.py` 保存分量和信道输出。配置和独立活动规则在 `configs/offgrid_*.json`；
当前实验与通用 `run.py` 单次入口统一使用 [120 轮配置](../configs/offgrid_baselines.json)，容差 1e-4，满足原条件提前停止；活动阈值使用同一配置绑定的冻结校准结果。来源和公式见 [OFFGRID_BASELINES.md](OFFGRID_BASELINES.md)。其他方法经 `run.py research` 与 `algorithm/research.py` 访问，见 [研究入口](RESEARCH.md)。

## 运行

```sh
.venv/bin/python -B run.py info
.venv/bin/python -B run.py verify
.venv/bin/python -B run.py simulate --seed 202610090100001 --snr -4 --users 40 --output NEW_CASE
.venv/bin/python -B run.py run --method proposed --input NEW_CASE/input.npz --output NEW_PROPOSED.npz --device mps
.venv/bin/python -B run.py run --method gamp --input NEW_CASE/input.npz --output NEW_GAMP.npz
.venv/bin/python -B run.py evaluate --estimate NEW_GAMP.npz --truth NEW_CASE/truth.npz
.venv/bin/python -B run.py test
```

使用新输出路径；`verify` 检查已就绪方法的冻结资产清单，并显式报告 L-DAMP 训练状态、配置与 checkpoint 身份，性能范围由已有评价记录说明。
训练工具见 [scripts/README.md](../scripts/README.md)，实际冻结权重的训练历史见 [TRAINING.md](TRAINING.md)。

## 训练实现

```text
scripts/train_gnn.py → experiment/training/gnn/cli.py
  mixed   → mixed.py       混合条件、epoch 续训与模型选择
  per-snr → per_snr.py     固定 SNR、阶段续训
  共用      common.py      物理标签、阶段顺序、源码身份
scripts/train_proposed.py → experiment/training/proposed/cli.py
  data.py                  完整几何信道库生成
  first.py                 一阶 score 训练与断点
  auxiliary.py             二阶 score / 活动分类器训练与断点
  common.py                数据路径、教师身份和源码记录
experiment/training/scores/
  trainer.py               共用验证、batch 和设备随机状态
  score_matching.py        查询噪声与训练 batch
  direct_objectives.py     两个 score 损失
  checkpoints.py           权重保存
```

训练模块通过包导入公共函数；推断网络仍在 `algorithm/` 中。
三阶段训练默认使用 `configs/training/proposed.json`，数据、初始化权重和教师记录均在主线内。
当前三网络权重的训练来源按 [TRAINING.md](TRAINING.md) 追溯。
迁移测试所需的独立参考文件位于 `tests/fixtures/`；运行时无需读取 `archive/`。

## 结果与历史复现

2026-10-16：当前实验及其训练、测试、冻结来源依赖继续放在 `experiments/`。
77 个历史实验目录集中到[本次归档](../docs/history/archive/workspace_cleanup_20261016/README.md)，
其中保留原文件内容、路径映射和恢复工具。旧脚本按原项目目录深度计算根路径，需要恢复后执行。
该轮整理保留 `src/`、配置、训练脚本、测试、权重和所有结果目录原位。
随后进行的 [baseline 目录整理](../results/baseline_package_20261016/REPORT.md)
将 baseline 实现和导入路径统一到 `algorithm/baselines/`。

[结果索引](../docs/history/results/README.md) 区分当前比较、运行依赖、回归材料和历史研究。
历史结果的实体位于归档，原 `results/<日期目录>` 路径通过符号链接继续可读；原数组、配置和证书保持内容。
旧实验脚本和旧文档集中于 [整理前快照](../docs/history/archive/workspace_organization_20261011/README.md)。
依赖旧 API 的日期实验使用其匹配源码：

```sh
.venv/bin/python -B docs/history/archive/code_consolidation_20261011/run_legacy.py run.py info
```

该入口采用快照工作目录、源码和配置；具体数据路径与原脚本参数按其协议执行。
快照共享原数据资产，其保存范围见 [归档说明](../docs/history/archive/code_consolidation_20261011/README.md)。

2026-10-18 整理以冻结结果的身份为约束：数值实现与 JSON 配置未改动；14 个历史研究启动脚本及两个独立候选实验已归档，原路径保留兼容链接。归档工作区以链接提供公共依赖，不是新的冻结版本。见[本次清单](../docs/history/archive/workspace_cleanup_20261018/README.md)。
