# 矩阵预条件一阶网络训练

2026-10-24 用户授权修改结构并重新训练。训练已于北京时间 17:06 启动，正式完成情况以 `status.json` / `complete.json` 为准。

17:11 启动核验：已完成第 1 轮并进入第 2/200 轮，训练进程正常、stderr 为空。固定 5000 个验证信道上的 DSM 从初始化 `0.8623786` 降至 `0.6160914`，整体 NMSE 从 `−2.7929 dB` 至 `−4.2474 dB`；这是同一新结构训练前后的验证值，不是接收机活跃检测结果。首轮最佳权重与轮末完整恢复断点均已核验，见 `STARTUP_VERIFICATION.json`。24 项 CPU 检查和 GPU batch 64 检查通过。

## 本次变化

保留 RefineNet 与原条件支路，显式加入 `B=(0.5I+Σ)^(-1/2)`、`K=0.5(0.5I+Σ)^(-1)`、`O=sqrt(0.5)Σ^(1/2)(0.5I+Σ)^(-1/2)`，输出 `D=Kr+OF(Br,C)`。实协方差 `Σ=real_embedding(C)/2`。原始网络输出 F 不再除以标量噪声标准差；`forward` 明确返回均值，通过 `.score()` 得到实坐标 score。

原 DSM 目标保持 `mean(||Σ^(-1/2)(D-h)||²)`，采用数学等价的稳定表达式计算。各矩阵函数在两个轴的联合特征谱上计算，再回到原物理轴，未将其误拆为两个独立逆矩阵。

详细公式、文献依据及实现限制见[说明](../../../../paper/docs/COLORED_PRECONDITIONED_TRAINING_20261024.md)。

## 保持一致

- 同一 50000 个训练信道、5000 个内部验证信道、固定归一化尺度和文件哈希。
- 与上一有色候选相同的 C 分布、[-20,30] dB 噪声范围、数据顺序及基础噪声/相关形状随机数。
- 同一原始随机权重；主干逐项复制，条件支路新增列为零，输出层保留原参数。没有继承上一候选已训练的权重，也没有将输出层清零；改变参数化后初始网络函数有意不同。
- batch 64，每次按原顺序抽 16 条，末批 16；Adam、梯度裁剪 1、余弦学习率 1e-4 至 1e-6、EMA 0.999、float32。
- 完整 200 轮，共 156400 次更新；每轮固定验证全部 5000 个信道，按最低验证 DSM 选择 EMA，包含 epoch 0。接收机性能评估另遵循 1000 MC 场景协议。

## 执行与审计

配置：`src/configs/training/colored_preconditioned_matched_20261024.json`。
项目目录设置 `PYTHONPATH=src` 后，使用项目虚拟环境执行：

```
python -B -u -m training.colored_preconditioned_20261024.formal train
```

- `specification.json`、`recipe.json`、`source/`：固定配置、数据与源码哈希及精确源码快照。
- `PREFLIGHT.json`：GPU batch 64 检查，图捕获/普通执行梯度相对差 `9.792167586412902e-6`。临时优化步骤未写入正式训练；单次检查不用于判断收敛。
- `VERIFICATION.json`：实际测试命令、结果和检查范围。
- `TRANSITION.json`：旧候选完成 26 轮，保存完整断点后暂停在 epoch 27、样本 6528、20434 次更新；原源码哈希核对未变，保存其 `last.pt` 与 `first_best.pt` 哈希。可恢复，不代表完成 200 轮。
- `LAUNCH.json` / `status.json` / `training.stdout.log` / `training.stderr.log`：启动、实时状态及日志。
- `baseline.json` / `history.json`：初始化和每轮固定验证，包括分 SNR NMSE。
- `last.pt`：每 120 秒及每轮结束保存模型、EMA、Adam、游标与随机数；原命令可显式恢复。`pause.request` 会在批次边界保存并退出。
- `first_best.pt`：最低验证 DSM 的 EMA。`first_final.pt` 和 `complete.json` 在 200 轮完成后生成。

新权重使用 `colored-preconditioned-first-v1` schema，由 `training.colored_preconditioned_20261024.model.load_checkpoint` 读取。不会改写旧候选或冻结接收机模型。导频实验继续运行，用户数实验仍暂停；GPU 资源共享会影响每轮时间。

这是训练启动记录，不是低 SNR 活跃检测改善的结果。需在后续验证与接收机实验中检验性能。
