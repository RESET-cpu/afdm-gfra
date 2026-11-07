# 条件信道与活动监督第二版

执行依据是 [第二版协议](../../docs/LSTMP_TRAINING_PROTOCOL_20261020_V2.md)。
本目录是独立候选；准备脚本将七层历史运行的接收机基础模块、数据接口和
物理模型复制到新运行目录，与本目录的训练实现一并冻结并校验。

- 主候选 A：真实活跃用户的条件信道平方误差 + 全用户自然比例 BCE。
  两项采用固定训练集分母，系数均为 1；每个前层权重 0.2，末层权重 1。
- 每层独立加载同一个 50,000 信道 AWGN 一阶 score；新活动头输出为公开先验。
- 深度 1–7 均为一轮新增层适配、两轮全层联合训练。联合学习率统一乘 0.1。
  三个校准量具有独立 Adam 状态；末层之后的反馈校准不更新。
- 各深度从 epoch 0–3 中选择末层条件信道损失与 BCE 之和最低者，
  同值优先较早轮。全部检查点、全部条件及逐用户统计均保留。
- 最大 100,800 次场景更新，不继承历史训练的时间预算，不自动启动对照或测试。

从仓库根目录使用既有 CUDA 环境执行：

```powershell
.\.venv\Scripts\python.exe scripts/prepare_lstmp_training_v2_20261020.py --fresh
.\.venv\Scripts\python.exe scripts/check_lstmp_training_v2_implementation_20261020.py
& D:\afdm-gfra-cpu\runs\lstmp_conditional_bce_v2_20261020\start_training.ps1
```

运行目录内 `MANIFEST.json` 绑定代码、配置、先验、统计量和数据清单；
`protocol/PREFLIGHT.json` 必须对应同一版本才能启动。训练断点包含模型、
Adam 状态、各随机数状态、场景顺序和游标。停止后查看原因和进程，
使用同一启动脚本的 `-Resume` 恢复。运行期间创建空的 `pause.request`
文件会在下一场景开始前保存断点并暂停；恢复前移除该请求文件。

`STATUS.json` 给出进度，`checkpoints/depth_*/history.json` 给出逐轮指标，
`validation_epoch_*.json` 保存完整验证结果，`best.pt` 为按固定规则选中的权重。
真实信道与活动标签只供损失和评价使用；接收机仅接收公开观测、算子、
已知噪声和活动先验。本轮仍是已知相位/噪声设置。

`objectives.assign_gradients(..., bce_updates_score=False)` 精确定义协议中的
梯度对照 B，供核验和后续独立运行使用；当前正式入口始终训练主候选 A。
