# 有色噪声一阶网络：矩阵预条件训练

2026-10-24，用户在结构调研后授权“修改并重新训练”。本候选独立于冻结主线及先前有色 score 候选。实现依据见[结构调研](COLORED_SCORE_ARCHITECTURE_REVIEW_20261024.md)与[公式推导及文献页码](../../../reference/reviews/colored_architecture_review_20261024/preconditioning.md)。

## 参数化与目标

实数打包坐标为 `[2,antenna,output,input]`。复协方差为
`C = v Ra ⊗ I_output ⊗ Rc`，实协方差为 `Σ = real_embedding(C)/2`。
固定实参考方差 `τ² = 0.5`，它对应归一化复数参考协方差 I，并非实测完整信道先验。

```
B = (τ²I + Σ)^(-1/2)
K = τ²(τ²I + Σ)^(-1)
O = τ Σ^(1/2)(τ²I + Σ)^(-1/2)
Dθ(r,C) = K r + O Fθ(B r, condition(v,Ra,Rc))
sθ(r,C) = Σ^(-1)(Dθ-r)
```

`Fθ` 是原 RefineNet 主干的原始输出，取消旧包装层的 `1/sqrt(v/2)`；其内部 `legacy_image` 输入变换仍保留。条件支路仍接收完整 Ra、Rc，经原 64 维条件向量调制。输入预处理和线性分支直接使用 C，因此这些已知矩阵运算无需通过条件支路学习。B 通常不将噪声白化；所有算子运算后都回到物理坐标，CNN 不在随机特征基中训练。

**目标仍是原 DSM，不改为无权 residual MSE：**

```
L = mean(||Σ^(-1/2)(Dθ-h)||²)
  = mean(||sqrt(K) Fθ - Σ^(1/2)(τ²I+Σ)^(-1) h + K ε||²)
r = h + Σ^(1/2) ε
```

第二式用于实际训练，直接保留抽样时的 ε，避免由 noisy-clean 反算噪声或通过大数相消求 mean。验证 NMSE 直接使用 D。公式在精确算术下相同，浮点实现的误差由独立稠密矩阵、目标与梯度测试核对。

Ra、Rc 的 eigendecomposition 在 CPU 预先完成，联合谱为 `λ_ij = (v/2) ea_i ec_j`。B、K、O 的非可分离标量函数作用于这个 16×16 联合谱，不构造 4096×4096 或 8192×8192 矩阵，也不把加法逆误拆为两个独立轴的逆。CUDA 图中仅包含张量运算。`score()` 与 `mean()` 都保留对输入 r 的完整可微路径。

## 配对条件

- 复用原 50000 个训练信道、5000 个内部验证信道、固定尺度及其哈希。
- 与上一有色候选使用同一单一协方差族、强度范围 [0,0.5]、rank 4、SNR [-20,30] dB，以及相同两组训练/验证随机数。每次仍抽 16 条，拼接为 batch 64；新增特征分解不消耗随机数。
- 从原随机初始化文件重新开始，逐项复制主干参数；条件支路新增列仍为零。**不从已训练的有色 checkpoint 接续，也不将原输出层清零。** 参数初值相同，但输入/输出函数有意改变，因此初始网络不等于 F=0 的线性参考估计。
- Adam、梯度裁剪 1、学习率 1e-4 到 1e-6 的原余弦调度、EMA 0.999、float32、200 个完整 epoch 保持不变。每轮 782 次更新，共 156400 次。
- 每轮固定全部 5000 个内部验证信道与噪声，按最低验证 DSM 选 EMA 权重，包含 epoch 0；同时记录各 5 dB 区间 NMSE。接收机正式性能评估另遵循 1000 MC 场景协议。

## 实现与执行记录

- [配置](../../../src/configs/training/colored_preconditioned_matched_20261024.json)
- [模型](../../../src/training/colored_preconditioned_20261024/model.py)、[矩阵算子](../../../src/training/colored_preconditioned_20261024/operators.py)、[训练入口](../../../src/training/colored_preconditioned_20261024/formal.py)
- [独立运行目录](../../../result/channel_denoising/data/colored_preconditioned_50000_matched_20261024)

新权重 schema 为 `colored-preconditioned-first-v1`，forward 明确返回 conditional mean；需通过该模块的专用 loader 读取，不能当作旧 direct score 权重。训练恢复文件独立保存模型、EMA、Adam、数据游标、两个 NumPy RNG 和 Torch RNG，并绑定源码/配置哈希。

运行目录的 `PREFLIGHT.json`、`VERIFICATION.json`、`TRANSITION.json` 与 `status.json` 分别记录实际 GPU 检查、测试、旧候选暂停和当前状态；`complete.json` 仅在 200 轮结束后生成。启动检查与正式训练彼此独立，检查使用的优化步骤不会进入正式模型。

这项改动检验的是参数化是否改善优化。显式矩阵运算、输出尺度有界等代数性质不构成低 SNR 活跃检测性能或接收机收敛保证；仍须依据后续固定噪声验证及接收机实验判断。
