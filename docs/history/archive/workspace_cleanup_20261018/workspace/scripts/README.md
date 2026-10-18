# 主线训练与研究入口

推断、生成、评分和常规测试使用根目录 `run.py`。主线训练包含以下启动入口：

| 工具 | 实现与配方 |
|---|---|
| `train_proposed.py` | `training/proposed/`；一阶 score → 二阶 score → 活动分类器，配方为 `configs/training/proposed.json` |
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

## 历史研究工具

日常使用本页的 `train_proposed.py`、`train_gnn.py`、`train_ldamp.py`、`validate_ldamp.py`。其余 14 个研究启动脚本已归档至 [研究脚本目录](../archive/workspace_cleanup_20261018/workspace/scripts/)，本目录保留原路径链接以兼容测试、训练来源与历史命令。脚本内容没有改动。

AMP、D-AMP、联合 L-DAMP 和后验相位更新等独立入口均属于历史研究工具；当前五方法运行使用 `run.py`。逐项路径与恢复入口见[归档说明](../archive/workspace_cleanup_20261018/README.md)。
