# 复现与两个算法的独立入口

所有命令在项目根目录执行。现有结果禁止覆盖；下面的 `NEW_*` 路径应取尚不存在的目录/文件。
依赖为项目已有 `.venv`，训练与本轮计时采用 PyTorch MPS。硬件后端可能造成小量浮点差异，
数学测试使用相应容差，不把文件逐字节重现作为随机学习训练成功的必要条件。

## 用同一输入比较两个算法

```sh
.venv/bin/python run.py simulate --seed 2026101519000000 --snr 0 --output NEW_CASE
.venv/bin/python run.py run --method proposed --input NEW_CASE/input.npz --output NEW_PROPOSED.npz --device mps
.venv/bin/python scripts/run_diffusion_amp.py --input NEW_CASE/input.npz --output NEW_SCORE_AMP.npz --device mps
.venv/bin/python run.py evaluate --estimate NEW_PROPOSED.npz --truth NEW_CASE/truth.npz
.venv/bin/python run.py evaluate --estimate NEW_SCORE_AMP.npz --truth NEW_CASE/truth.npz
```

`configs/proposed.json` 配原三网络，`configs/diffusion_amp.json` 配本轮独立训练模型。
新方法每次输出同名 `.json`，记录模型/推断签名、方差序列、导数成本及完成/失败状态。
失败输出为 `last_valid_estimate`，不当作完成结果评分。

## 精确训练流程

本轮使用原始物理样本银行，完整哈希见训练 `PLAN.json`；它们是训练数据，不是旧网络权重。
训练和验证物理场景交集为零。第一次正式训练命令为：

```sh
.venv/bin/python scripts/train_diffusion_amp.py \
  --output NEW_TRAIN_STAGE1 --device mps --steps 15000 --minimum-steps 8000 \
  --patience 8 --validation-interval 500 --validation-users 96 \
  --final-validation-users 512 --batch-size 64 --width 48 --blocks 4 \
  --learning-rate 0.0003 --seed 202610157001 --validation-seed 202610157002
.venv/bin/python experiments/diffusion_amp_20261015/training/continue_training.py \
  --from-run NEW_TRAIN_STAGE1 --output NEW_TRAIN_STAGE2 \
  --device mps --steps 30000 --minimum-steps 20000
```

续训恢复本次随机初始化模型的优化器、学习率调度和随机状态，不重新加载已有 Proposed/L-DAMP。
Adam、梯度范数裁剪10、验证驱动学习率减半及固定多噪声加权损失的实现与源码哈希均存于训练目录。
本轮最后选中27,000步的 `best.pt`，30,000步 `last.pt` 仅供继续训练和追溯。

网络权重改变后须重新运行阻尼验证和活动门限校准。不可将旧门限绑定到新模型，也不能据
现有独立测试真值来选新模型。重复科学比较应预先登记新的测试场景和独立结果目录。

## 检查既有实验与资产

```sh
.venv/bin/python -m pytest -q tests/test_diffusion_amp.py tests/test_ldamp_matrix.py tests/test_ldamp.py tests/test_ldamp_score.py
.venv/bin/python run.py verify
.venv/bin/python experiments/diffusion_amp_20261015/report.py
```

最后一条只从已有冻结测试输出重建表格和图，不重选接收机。所有候选和失败记录保留于
`results/diffusion_amp_20261015/`；实验脚本按 `validate`、`calibrate`、`evaluate` 顺序实施
[预定协议](PROTOCOL.md)。未标定阶段的占位活动决策不用于活动性能结论。

当前推断签名覆盖网络、主要求解器源码和表示文件，但不穷尽传递依赖。改变系统 C1/C2、
阵列形状、活动负载或物理分布后需重新训练/验证并重新绑定门限；当前受保护资产哈希核验
确保此次比较没有悄然改变这些设置。
