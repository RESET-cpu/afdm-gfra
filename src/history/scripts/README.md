> 2026-10-21 最终代码整理已完成。当前维护入口见[最终版本](../src/afdm_jadcedd/evaluation/README.md)；下文保留整理前的说明及历史路径。

# 脚本导航

日常性能实验从 [experiment/](../experiment/README.md) 运行。本目录存放训练准备、专项检查、历史比较和报告脚本；当前不会自动恢复训练或执行旧三网络。

| 类别 | 代表脚本 | 当前用途 |
|---|---|---|
| 最终十层训练来源 | `prepare_lstmp_training_v3_20261020.py`、`prepare_lstmp_v3_gpu_continuation_20261020.py` | 已完成运行的准备来源，不是当前实验启动入口 |
| 十层已完成 20 场景比较 | `evaluate_lstmp_v3_depth10_previous20_20261020.py`、`compare_lstmp_depth10_standard20_gpu_20261021.py` | 历史比较来源；当前正式测试走共享 2000 场景入口 |
| 模型/训练核验 | `check_lstmp_training_v3_implementation_20261020.py`、`check_lstmp_v3_gpu_continuation_20261020.py` | 特定实现和协议的核验 |
| 三网络及基线训练工具 | `train_proposed.py`、`train_proposed_sizes.py`、`train_proposed_50000.py`、`train_auxiliary_200.py`、`train_gnn.py`、`train_ldamp.py` | 原训练协议工具；保留，当前未启动 |
| 专项诊断、计时和报告 | `diagnose_*`、`benchmark_*`、`profile_*`、`report_*`、`analyze_*` | 各自日期/候选的记录；名称不是运行状态，先查其输入和对应协议 |
| 旧五层/七层/v2及修复候选 | `prepare_lstmp_depth7_*`、`evaluate_lstmp_epoch6_*`、`compare_*v2*`、稳定性/消息校准相关脚本 | 历史来源；部分权重已删除，不能假定可完整重跑 |

最终十层的实际训练模块在冻结运行的 `source_code/experiments/`，当前实验调度在工作区 `experiments/lstmp_evaluation_2000_20261021/`。详细依赖见 [代码导读](../docs/CODE_GUIDE.md)。

以下保留原训练命令和历史协议作为来源说明；它们不表示待自动执行的工作。相对路径按项目根目录解释。

## 保留的三网络训练与研究说明

## Windows NVIDIA：50,000 样本独立训练

`train_proposed_50000.py` 沿用样本量实验的随机初始化与网络结构，只训练 50,000 样本版本。
顺序为一阶完整 200 轮 → 独立信道去噪 → 二阶（最多 80 轮）→ 分类器（最多 100 轮）→ 绑定接收机。
后两阶段保留原验证平台停止规则；全部使用 5,000 个独立验证信道选权重。
去噪为原协议的 500 场景、每场景 4 个信道、六档复噪声方差，不是接收机性能实验。
现有冻结配置、权重和结果保持不变。

Windows 使用项目独立环境 `.venv/Scripts/python.exe`，安装支持显卡的 CUDA 版 PyTorch。
RTX 5080 已采用 PyTorch 2.7.1 + CUDA 12.8。`-X utf8` 用于正确读取原 UTF-8 元数据。

```powershell
& ./.venv/Scripts/python.exe -X utf8 scripts/train_proposed_50000.py prepare --output runs/proposed_50000_cuda_20261018
& ./.venv/Scripts/python.exe -X utf8 -u scripts/train_proposed_50000.py run --output runs/proposed_50000_cuda_20261018
& ./.venv/Scripts/python.exe -X utf8 scripts/train_proposed_50000.py status --output runs/proposed_50000_cuda_20261018
```

在去噪计划生成之前，可登记另一台机器传来的已完成 5,000 样本一阶模型配置：

```powershell
& ./.venv/Scripts/python.exe -X utf8 scripts/train_proposed_50000.py attach-small --output runs/proposed_50000_cuda_20261018 --small-config PATH_TO_FIRST_RECEIVER_JSON
```

该配置须连同权重、先验、完成记录与 specification 一起传入，并保持身份可验证。
未登记时先执行大样本单模型去噪，结果明确标记小样本对照待补齐。
训练每约 120 秒及每轮完成保存断点；在 `model/<当前阶段>/pause.request` 创建文件可安全暂停。
移走暂停请求后重复原 `run` 命令恢复，CUDA 随机状态与优化器状态随断点恢复。
运行时阻止 Windows 自动休眠，退出后释放；不改变系统电源方案。
`prepare --smoke` 仅用于新目录中的 16 样本流程检查，不能产生论文性能结论。

CUDA 吞吐优化使用独立续训目录：原每 16 个样本的随机查询生成顺序保持，合并 64 个样本做一次
GPU 前向／反向；有效优化批量仍是 64，精度仍是 float32，验证过程不变。EMA 使用等价批量运算。
先用 `model/first/pause.request` 暂停原运行，再准备新目录：

```powershell
& ./.venv/Scripts/python.exe -X utf8 scripts/train_proposed_50000.py prepare-cuda-continuation --from-run runs/proposed_50000_cuda_20261018 --output runs/proposed_50000_cuda_optimized_20261018
& ./.venv/Scripts/python.exe -X utf8 -u scripts/train_proposed_50000.py run --output runs/proposed_50000_cuda_optimized_20261018
```

续训恢复模型、EMA、Adam、样本顺序、全部随机状态和进度，保留原学习率日程及累计 200 轮预算。
旧运行保留；GPU 批量变化允许浮点舍入差异，不宣称后续权重逐位一致。
去噪及后续训练顺序不变，`attach-small` 须指向新的运行目录。

推断、生成、评分和常规测试使用根目录 `run.py`。主线训练包含以下启动入口：

| 工具 | 实现与配方 |
|---|---|
| `train_proposed.py` | `training/proposed/`；一阶 score → 二阶 score → 活动分类器，配方为 `configs/training/proposed.json` |
| `train_proposed_sizes.py` | 5,000／50,000 干净信道配对训练；同一随机初始化，先各训练一阶 200 轮，再去噪，随后训练二阶与分类器 |
| `train_ldamp.py` | DnCNN 噪声区间训练；使用 `--resume-from 原训练目录 --output 新目录` 续训，原目录保留 |
| `train_gnn.py` | `training/gnn/`；显式选择 `mixed` 或 `per-snr`，共用唯一 GNN 网络 |

只读检查已有训练资产：

```sh
.venv/bin/python -B scripts/train_proposed.py --inspect --check-assets
.venv/bin/python -B scripts/train_gnn.py --help
.venv/bin/python -B scripts/train_gnn.py mixed --help
.venv/bin/python -B scripts/train_gnn.py per-snr --help
```

开始新的三阶段训练时，输出写入独立运行目录：

```sh
.venv/bin/python -B scripts/train_proposed.py --stage all --output runs/proposed_new --device mps
```

`all` 顺序训练三份网络，使用本次运行的教师，最后生成 `runs/proposed_new/receiver.json`。
单独运行 `second` 或 `activity` 时，默认使用当前选定的教师；传 `--teachers run` 可改用该输出目录里已完成的一、二阶训练。
`bind` 检查训练记录与教师配对，生成新的接收机配置。完整用法见 [TRAINING.md](../docs/TRAINING.md)。

Proposed 中断后重复同一命令即可续训；GNN 使用原配方加 `--resume NEW_RUN/training_state.pt`。
`mixed` 在 epoch 边界续训，`per-snr` 在阶段边界续训。旧断点保留其原始源码身份，新实现不会重写旧证书以接续历史轨迹。

L-DAMP 通过 `train_ldamp.py` 按 `configs/training/ldamp.json` 训练五段网络，再用 `validate_ldamp.py --config 新训练目录/receiver.json --output 新验证目录` 校准活动门限并检验独立场景。`--smoke` 只检查流程，不具备性能验证资格。`--resume-from` 复用相同配方与源码下已完成阶段，未完成阶段从头运行。当前默认版已通过独立 16 场景及配对 10 场景 × 六 SNR 验证，训练与验证范围见 [L-DAMP 文档](../docs/LDAMP.md)。

## 历史文件整理记录

上表记录三网络和基线训练入口。后续新增的十层准备、诊断和核验脚本也保留在本目录，当前分类见页首；旧说明中的目录范围不再代表本目录全部文件。

### Auxiliary CUDA execution (Windows, 200 epochs)

`scripts/train_auxiliary_200.py run --output <run>` executes the two auxiliary stages for both banks from completed, immutable first-score checkpoints. The execution-only continuation is prepared by `scripts/prepare_auxiliary_cuda_graph.py` in a new output directory after pausing the parent and passing `scripts/benchmark_auxiliary_cuda.py`.

The optional `cuda_execution.second` and `cuda_execution.activity` settings enable CUDA graphs and batched EMA updates. Each graph retains the original 16-sample query draws, microbatch reductions, gradient accumulation, optimizer batch, float32 networks, and float64 activity-mean readout. Partial batches use the same eager operations. Fixed validation, epoch budgets, learning-rate schedules, checkpoint selection, and model definitions are unchanged. The benchmark compares losses, gradients, Adam updates, EMA and RNG states, including partial batches; original and new timing measurements and continuation provenance are saved alongside the run.

### 独立消息校准候选（2026-10-19）

`validate_message_calibration.py` 按 `prepare` → `cache` → `train` → `banks` → `physical` → `report` 顺序执行首轮小规模验证。该入口保留既有50k三网络，只拟合三个小型校准头；原理、来源、损失、数据划分及限制见 `docs/TERMINOLOGY.md` 的对应条目。模型与统计分别写入 `runs/message_calibration_candidates_20261019` 和 `results/message_calibration_candidates_20261019`，原实验不恢复。协议记录全部来源哈希，要求新目录；不要覆盖既有运行以反复调参。物理比较使用相同固定输入、阻尼0.1和300次更新。复现前先运行 `python -m pytest tests/test_message_calibration_candidate.py -q`。本候选不是完整L-STMP复现。
