# 当前算法训练

当前训练入口、数据与权重以 [scripts/README.md](../../../src/history/scripts/README.md) 和 `configs/training/` 为准。2026-10-18 已完成脱离归档的资产检查；本页以下按日期描述的旧试验状态属于历史记录，旧训练中间断点已清理，不能直接恢复这些旧运行。

原比较图五种方法的权重保持冻结。L-DAMP 旧训练已完成但去噪和接收机验证失败，当前进行有记录的训练对照，状态见 [CURRENT_STAGE.md](CURRENT_STAGE.md)。

2026-10-14：proposed 仅保留当前旧完整三网络及其消息传递接收机。其他 proposed 权重、训练断点和历史副本已按用户要求清理；实验源码、报告、指标与共享数据保留。原三网络训练初始化、GNN-ASPL 主线权重与 L-DAMP 研究资产保留。 详见[当前说明](CURRENT_STAGE.md)。

相位增强与关系约束的一阶小规模对照，最后保存状态为 FAILED，原因为 `TimeoutError: [Errno 60] Operation timed out`，原进程已退出；不能把启动记录当作已完成性能结果。协议与断点见[试验记录](../../../archive/paper_layout_20261026/original_paper/docs/history/runs/proposed_phase_training_20261012/README.md)，实际状态见 [STATUS.json](../../../archive/paper_layout_20261026/original_paper/docs/history/runs/proposed_phase_training_20261012/STATUS.json)。

2026-10-12 最新状态：用户要求停止 200/100/100 续训，任务已保存完整断点并退出。一阶已完成 96 轮，第 97 轮处理了 46,976 / 50,000 个样本，二阶与分类器尚未启动；未经重新授权不恢复。见[训练记录](../../../archive/paper_layout_20261026/original_paper/docs/history/runs/proposed_200_100_100_20261012/README.md)和[暂停核验](../../../archive/paper_layout_20261026/original_paper/docs/history/runs/proposed_200_100_100_20261012/PAUSE_VERIFICATION.json)。默认推断仍使用下表原权重。有色噪声条件三模块路线已[归档](../../../archive/paper_layout_20261026/original_paper/docs/history/archive/covariance_training_20261012/README.md)；已检出用户均值与反馈研究（历史文件已清理，原路径：`experiments/proposed_mean_feedback_20261012/PLAN.md`）的已有结果保留。

训练代码、数据、初始化权重和教师记录均在主线内。统一入口为
[scripts/train_proposed.py](../../../src/history/scripts/train_proposed.py)，默认配方为
[configs/training/proposed.json](../../../src/configs/training/proposed.json)。

## 数据与当前权重

当前先验使用 50,000 个训练活跃信道和 5,000 个验证信道，实际文件在
[data/proposed/](../../../result/data/proposed)。候选用户在活动掩码之前均匀选取，场景不跨训练/验证集合。
固定坐标尺度为 0.2647966452702405，归一化坐标平均功率为 1.0004404181394917；
固定尺度并非新分布的精确 RMS。

| 网络 | 原训练状态 | 当前权重 |
|---|---|---|
| 一阶 score | 完成 81 轮，并保留第 82 轮部分更新；按用户预算停止 | [first.pt](../../../result/models/proposed/first.pt) |
| 二阶 score | 完成 39 轮；按用户预算停止 | [second.pt](../../../result/models/proposed/second.pt) |
| 活动分类器 | 完成 84 轮，验证平台停止，选第 82 轮 | [activity.pt](../../../result/models/proposed/activity.pt) |

完整的原配方、完成记录、初始验证和训练历史保存在
[models/proposed/training_records/](../../../result/models/proposed/training_records)。
一、二阶因预算停止不等于已经证明优化收敛。当前推断继续使用这些冻结权重。

一阶采用完整实复坐标 DSM。二阶冻结选定的一阶网络，以整个样本平均后的平方损失回归该有限完整均值的条件 MSE；目标关系见 [THEORY.md T8–T11](THEORY.md)。
分类器在同一先验和查询噪声分布下使用完整 R 及同查询 F0，平衡两类 BCE 训练，部署时加入公开活动先验一次。

[先验定义](../../../result/data/proposed/prior_definition.json)保持原字节内容，以维持 SHA 和分类器内嵌先验的相等关系。
其中的历史绝对路径只作来源记录；实际读取路径由当前训练配置提供，并校验数据 SHA。
三份原初始化权重位于 [models/initialization/](../../../result/models/initialization)。

## 运行方式

只读检查全部依赖：

```sh
.venv/bin/python -B scripts/train_proposed.py --inspect --check-assets
```

需要重新训练时，一条命令顺序执行三阶段并绑定本次运行的教师：

```sh
.venv/bin/python -B scripts/train_proposed.py --stage all --output runs/proposed_new --device mps
```

该命令使用原初始化权重、原数据和原损失配方，创建新的优化轨迹。结果写入 `runs/proposed_new/`，
最后生成 `receiver.json`。重复同一命令可接续本次运行的断点，源码、配置、教师与数据身份必须一致。
输出目录中的 `first/pause.request`、`second/pause.request` 或 `activity/pause.request` 可暂停对应阶段，移除后继续。

只训练活动分类器并使用当前选定的一、二阶教师：

```sh
.venv/bin/python -B scripts/train_proposed.py --stage activity --output runs/activity_new --device mps
.venv/bin/python -B scripts/train_proposed.py --stage bind --output runs/activity_new
```

单阶段 `second`、`activity` 默认使用选定教师。手动顺序运行同一输出目录中的新阶段时，加 `--teachers run`。
新的接收机使用 `run.py run --config runs/proposed_new/receiver.json ...`，是否采用新权重需要另行评价。
数据生成用 `--stage data` 和新的输出目录，见 [data/README.md](../../../result/data/README.md)。

历史来源证书保留；除当前训练初始化外，历史断点已按本次清理删除。它们记录的是当时的源码，不能改写 SHA 后冒充在新实现中逐位续训。
当前实现中的新运行具有独立的断点和来源记录。

本次 200/100/100 运行显式导入经过核验的一阶完整断点，并以 `CONTINUATION.json` 记录旧、新规格和继承进度。
原轨迹已完成 81 轮，第 82 轮已处理 20,928 个样本；其参数、EMA、Adam、随机流和样本顺序均保留。
学习率从断点的 8.857950124856526e-6 平滑下降至第 200 轮的 1e-6。
二阶和分类器使用当前选定权重初始化、新优化器与新的训练噪声随机流；验证噪声流保持原定义。
各阶段的最小轮数设为目标轮数，保证累计 200 / 新增 100 / 新增 100 轮；按完整验证集选最优权重，同时保留最后一轮 EMA。
本次代码、数据、原权重与断点均已复制到运行目录，后台任务不依赖后续工作区源码改动。

## 实现位置

| 文件 | 职责 |
|---|---|
| `training/proposed/data.py` | 完整几何信道库生成 |
| `training/proposed/first.py` | 一阶 score 训练、EMA、模型选择和断点 |
| `training/proposed/auxiliary.py` | 二阶 score 与活动分类器训练、冻结教师和断点 |
| `training/proposed/common.py` | 可搬动路径、先验/教师校验和源码 SHA |
| `training/proposed/cli.py` | 三阶段顺序及接收机配置绑定 |
| `training/scores/` | 共用损失、batch、验证和 checkpoint 序列化 |

所有网络仍只定义在 `algorithm/` 中。原有两个 score 的历史启动器已由当前三阶段入口替代。

## GNN-ASPL

当前 GNN 使用 10001/256 训练/验证样本的冻结权重，29 阶段、39 个 epoch；
原历史训练混合 on/off-grid 场景，权重见 [baselines.json](../../../src/configs/baselines.json)。
未来重新训练时，按已有协议使用 on-grid 训练与训练验证，并独立评价 off-grid 性能。

| 配方 | 数据与方差拟合 | 续训与模型选择 |
|---|---|---|
| `train_gnn.py mixed` → `gnn/mixed.py` | 按显式 SNR/grid 分布采样；从 on-grid 训练真值的占用行拟合固定 slab 方差 | epoch 边界恢复 Adam；按第 10 层 joint 阶段验证 NMSE 选权重 |
| `train_gnn.py per-snr` → `gnn/per_snr.py` | 固定 SNR；网格由参数选择；从训练活跃用户的全部网格坐标拟合固定 slab 方差 | 阶段边界恢复；每阶段重新建立 Adam；保存最终阶段权重 |

两种配方共用 `gnn/common.py` 的场景生成、物理系数标签、29 阶段顺序和源码记录。
网络只有 `algorithm/baselines/gnn_aspl.py` 一份实现。用各自的 `--help` 查看参数。

## 本次核验范围

以下为工作区整理时的历史核验，当时研究训练处于停止状态（最新训练授权见文首）：
CPU 上使用完整输入形状、较窄的真实网络和明确标记的合成数据跑通三阶段，并检查逐阶段中断续训一致性；
GNN 沿用已有训练和续训测试。另使用当前冻结权重进行了五个算法的小场景推断。
全部 180 项测试在禁止读取 `archive/` 的条件下通过，详见
[独立运行核验](../../../archive/paper_layout_20261026/original_paper/docs/history/results/standalone_mainline_20261012/VERIFICATION.json)。
这些检查证明运行依赖已取出，不是新的完整训练或性能评价。

## 2026-10-13：16×16 小网络续训与真实方向对照

用户确认续训历史 16×16 一阶网络，累计最多 400 轮（历史40轮＋最多新增360轮）。
使用当前完整信道库的 G=H[0]，覆盖方向合并后的复噪声方差 v/16；固定验证集重新评测，
不将新旧数据/噪声范围的 loss 直接拼接。达到最低学习率后的验证平台与预算耗尽分开记录。
一阶完成后冻结其最佳权重，重新训练配套二阶和采用当前 BCE 方法的证据网络，随后自动
比较真实方向下的 NMSE/AER。正式完整网络权重不被覆盖。

协议：[PLAN.md](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/oracle_direction_small_20261013/PLAN.md)。
实际执行的是结果目录中的源码快照，运行入口与状态见
[STARTED.md](../../../archive/paper_layout_20261026/original_paper/docs/history/results/oracle_direction_small_20261013/STARTED.md)。
本次训练及预定对照已完成。一阶累计400轮、二阶新增100轮，均因达到预算停止，
未满足验证平台判据；分别选择累计第400轮和二阶新增第99轮。证据网络训练57轮，
按验证平台规则停止，选择第42轮。权重配套和全部144条闭环指标复算通过。
真实方向小网络相对冻结完整网络的NMSE在 −4/0/4 dB 下改善约1.97/1.71/1.28 dB；
相对完整网络最终输出方向投影的额外改善区间均跨0，不能归因于小网络先验学习更充分。
完整结果、停止状态及限制见 [REPORT.md](../../../archive/paper_layout_20261026/original_paper/docs/history/results/oracle_direction_small_20261013/REPORT.md)，
核验见 [COMPLETION_AUDIT.json](../../../archive/paper_layout_20261026/original_paper/docs/history/results/oracle_direction_small_20261013/COMPLETION_AUDIT.json)。


## 2026-10-13：波束通道网络容量实验

用户授权仅将宽度64改为128，6块及其他训练配置不变，参数1,994,528。旧宽度64第59轮完整断点已保存并保持暂停，此前第60轮写状态异常证据未删除。新运行完成7项检查和MPS中断恢复预检，此前受磁盘不足阻塞，清理约2 GiB下载缓存后已正式从头启动。方案见[容量实验](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/full_power_channels_w128_20261013/PLAN.md)，最新状态见[STATUS](../../../archive/paper_layout_20261026/original_paper/docs/history/results/full_power_channels_w128_20261013/STATUS.json)。后续仍需原独立测试门槛通过才训练二阶和证据。
